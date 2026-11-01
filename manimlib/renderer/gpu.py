from __future__ import annotations

from contextlib import contextmanager

import numpy as np
import wgpu
from PIL import Image

from manimlib.renderer.pipeline import COLOR_FORMAT
from manimlib.renderer.pipeline import DEPTH_STENCIL_FORMAT
from manimlib.renderer.pipeline import build_pipeline
from manimlib.renderer.shader_source import DATA_BINDING
from manimlib.renderer.shader_source import FIRST_TEXTURE_BINDING
from manimlib.renderer.shader_source import FRAME_GROUP
from manimlib.renderer.shader_source import SAMPLER_BINDING
from manimlib.renderer.shader_source import TEXTURE_KINDS
from manimlib.renderer.shared_buffer import SharedBuffer
from manimlib.renderer.texture import FILTER_MODES
from manimlib.renderer.texture import check_texture_filter
from manimlib.renderer.texture import stack_view
from manimlib.renderer.uniform_block import Uniforms
from manimlib.renderer.uniform_block import uniform_block_dtype

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Iterator
    from manimlib.renderer.pipeline import PipelineState


"""
The camera's uniforms travel as one block for the whole frame, read by every shader from the
same buffer and bound once a frame, see Gpu.render_pass.
"""
# Mirrors inserts/frame_uniforms.wgsl. Ordered so that each vec3 is followed by the float
# which fits beside it, leaving nothing padded but the last three floats.
FRAME_UNIFORMS = (
    ("view", 16),
    ("frame_rescale_factors", 3),
    ("frame_scale", 1),
    ("camera_position", 3),
    ("pixel_size", 1),
    ("light_position", 3),
)
FRAME_DTYPE = uniform_block_dtype(*FRAME_UNIFORMS)

# How many mobjects' worth of room a shared buffer starts with, doubling from there
UNIFORM_BLOCKS = 256
RECORDS = 4096


class RenderPass(object):
    """
    Where draw commands go. A live pass and a bundle being recorded take the same commands, so
    one wrapper covers both, see Gpu.render_pass and Gpu.bundle.

    Its own job is to say nothing twice: a pass holds onto what it was told, and a mobject
    drawn in several passes reads the same things in each.
    """

    def __init__(self, encoder: Any, frame_bind_group: Any):
        self.encoder = encoder
        self.frame_bind_group = frame_bind_group
        self.forget()

    def forget(self) -> None:
        """
        Whatever was told to the pass is forgotten, and the one thing every draw reads said
        again. Called at the start, and after a bundle, which leaves the pass knowing nothing.
        """
        self.bound: list[Any] = 3 * [None]
        self.pipeline_in_use: Any = None
        self.bind(FRAME_GROUP, self.frame_bind_group)

    def bind(self, group: int, bind_group: Any, offsets: tuple = ()) -> None:
        if self.bound[group] != (bind_group, offsets):
            self.encoder.set_bind_group(group, bind_group, offsets)
            self.bound[group] = (bind_group, offsets)

    def draw(self, pipeline: Any, vertices: int, indices: Any = None) -> None:
        """
        One pass over a mobject's records, taking them in the order a buffer of indices gives
        where it is handed one, each index being the vertex the shader is to work out.
        """
        if self.pipeline_in_use is not pipeline:
            self.encoder.set_pipeline(pipeline)
            self.pipeline_in_use = pipeline
        if indices is None:
            self.encoder.draw(vertices)
        else:
            self.encoder.set_index_buffer(indices, wgpu.IndexFormat.uint32)
            self.encoder.draw_indexed(vertices)

    def replay(self, bundle: Any) -> None:
        self.encoder.execute_bundles([bundle])
        self.forget()


class Gpu(object):
    """
    The device everything is made from, and every cache built on it: the modules shaders are
    compiled to, the layouts and pipelines they are drawn through, the images they sample, and
    the buffers mobjects' values are gathered in.

    Also the values which hold for a whole frame, written once a frame by the camera and read
    by every shader from group 0, see inserts/frame_uniforms.wgsl.

    Everything here lasts as long as the device, so the caches are its own rather than global:
    a scene reloaded into a new device leaves the old one's behind with it.
    """

    def __init__(self):
        self.adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
        self.device = self.adapter.request_device_sync()
        self.queue = self.device.queue

        self.frame_uniforms = Uniforms(FRAME_DTYPE)
        # Which version of them was last sent, none having been, see StructuredArray.version
        self.frame_version = 0
        self.frame_buffer = self.device.create_buffer(
            size=self.frame_uniforms.array.nbytes,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )
        self.frame_layout = self.device.create_bind_group_layout(entries=[{
            "binding": 0,
            "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
            "buffer": {"type": wgpu.BufferBindingType.uniform},
        }])
        self.frame_bind_group = self.device.create_bind_group(
            layout=self.frame_layout,
            entries=[{"binding": 0, "resource": {
                "buffer": self.frame_buffer, "offset": 0, "size": self.frame_buffer.size,
            }}],
        )
        # One stretch of a shared buffer at a time, see SharedBuffer. Shared by every
        # mobject, so that a pipeline built against it is too.
        self.mobject_layout = self.device.create_bind_group_layout(entries=[{
            "binding": 0,
            "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
            "buffer": {
                "type": wgpu.BufferBindingType.uniform,
                "has_dynamic_offset": True,
            },
        }])

        # Every pipeline has to match this, which the camera sets when it makes its
        # attachments
        self.samples = 1
        # How many times a shared buffer has made a new bind group, which a bundle holds
        # references to, see Renderer.draw
        self.rebinds = 0
        self.modules: dict[str, Any] = dict()
        self.textures: dict[Any, Any] = dict()
        # Views onto stacks of images, one per key, see texture_stack
        self.stacks: dict[Any, Any] = dict()
        self.layouts: dict[tuple[str, ...], tuple[Any, Any]] = dict()
        self.resource_layouts: dict[tuple[str, ...], Any] = dict()
        self.pipelines: dict[tuple, Any] = dict()
        self.shared_buffers: dict[tuple, SharedBuffer] = dict()
        self.samplers: dict[str, Any] = dict()

    # What a shader is compiled to, and what it may read

    def module(self, code: str) -> Any:
        """One module holds both stages of a shader, sharing a struct rather than a varying"""
        if code not in self.modules:
            self.modules[code] = self.device.create_shader_module(code=code)
        return self.modules[code]

    def texture(self, path: str) -> Any:
        """An image on the gpu, for whatever samples it. Uploaded once per path."""
        if path not in self.textures:
            image = Image.open(path).convert("RGBA")
            pixels = np.asarray(image, dtype=np.uint8)
            texture = self.device.create_texture(
                size=(image.width, image.height, 1),
                format=wgpu.TextureFormat.rgba8unorm,
                usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST,
            )
            self.queue.write_texture(
                {"texture": texture, "mip_level": 0, "origin": (0, 0, 0)},
                pixels,
                {"offset": 0, "bytes_per_row": 4 * image.width,
                 "rows_per_image": image.height},
                (image.width, image.height, 1),
            )
            self.textures[path] = texture
        return self.textures[path]

    def layer_texture(self, layers: np.ndarray) -> Any:
        """A texture holding a stack of images the shape of these, with nothing in it yet"""
        count, height, width = layers.shape[:3]
        return self.device.create_texture(
            size=(width, height, count),
            dimension=wgpu.TextureDimension.d2,
            format=wgpu.TextureFormat.rgba8unorm,
            usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST,
        )

    def write_layers(self, texture: Any, layers: np.ndarray) -> None:
        """Every layer of a stack into the texture it was made for"""
        count, height, width = layers.shape[:3]
        self.queue.write_texture(
            {"texture": texture, "mip_level": 0, "origin": (0, 0, 0)},
            np.ascontiguousarray(layers),
            {"offset": 0, "bytes_per_row": 4 * width, "rows_per_image": height},
            (width, height, count),
        )

    def texture_stack(self, key: Any, layers: np.ndarray) -> Any:
        """
        A 2d-array view of the layers uploaded under this key. Built once, so mobjects
        reading the same frames share one copy, see texture.LayeredPixels.
        """
        if key not in self.stacks:
            texture = self.layer_texture(layers)
            self.write_layers(texture, layers)
            # The view is cached too, so every reader shares one
            self.stacks[key] = stack_view(texture)
        return self.stacks[key]

    def sampler(self, texture_filter: str = "linear") -> Any:
        """
        How an image is read between its pixels: "linear" blends, "nearest" takes the nearest
        pixel, keeping pixel art crisp when scaled up. One sampler per mode.
        """
        if texture_filter not in self.samplers:
            mode = FILTER_MODES[check_texture_filter(texture_filter)]
            self.samplers[texture_filter] = self.device.create_sampler(
                mag_filter=mode, min_filter=mode,
            )
        return self.samplers[texture_filter]

    def bind_layouts(self, texture_kinds: tuple[str, ...] = ()) -> tuple[Any, Any]:
        """
        What a shader may bind: the frame's values, the mobject's values, and its records along
        with a texture for each image it names, each held as whatever its kind says.

        Made once for each run of kinds rather than once per mobject: a pipeline is built
        against these, so per mobject layouts would mean per mobject pipelines.
        """
        if texture_kinds in self.layouts:
            return self.layouts[texture_kinds]

        resource_layout = self.resource_layout(texture_kinds)
        pipeline_layout = self.device.create_pipeline_layout(bind_group_layouts=[
            self.frame_layout, self.mobject_layout, resource_layout,
        ])
        self.layouts[texture_kinds] = (resource_layout, pipeline_layout)
        return self.layouts[texture_kinds]

    def resource_layout(self, texture_kinds: tuple[str, ...] = ()) -> Any:
        """How a mobject's records are bound, along with a texture for each image it names"""
        if texture_kinds in self.resource_layouts:
            return self.resource_layouts[texture_kinds]

        entries = [{
            "binding": DATA_BINDING,
            "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
            # The stretch a draw reads is given as a dynamic offset, see SharedBuffer
            "buffer": {
                "type": wgpu.BufferBindingType.read_only_storage,
                "has_dynamic_offset": True,
            },
        }]
        if texture_kinds:
            entries.append({
                "binding": SAMPLER_BINDING,
                "visibility": wgpu.ShaderStage.FRAGMENT,
                "sampler": {"type": wgpu.SamplerBindingType.filtering},
            })
            entries += [{
                "binding": FIRST_TEXTURE_BINDING + index,
                "visibility": wgpu.ShaderStage.FRAGMENT,
                "texture": {
                    "sample_type": wgpu.TextureSampleType.float,
                    "view_dimension": TEXTURE_KINDS[kind][1],
                },
            } for index, kind in enumerate(texture_kinds)]

        self.resource_layouts[texture_kinds] = self.device.create_bind_group_layout(
            entries=entries,
        )
        return self.resource_layouts[texture_kinds]

    def pipeline(self, layout: Any, module: Any, state: PipelineState) -> Any:
        """
        The pipeline for one pass over one kind of mobject, kept here so that every mobject of
        a kind draws through the same ones rather than building its own.
        """
        key = (layout, module, state, self.samples)
        if key not in self.pipelines:
            self.pipelines[key] = build_pipeline(
                self.device, layout, module, state, self.samples,
            )
        return self.pipelines[key]

    # Where mobjects' values are gathered

    def uniform_buffer(self, block_size: int) -> SharedBuffer:
        """Where the uniforms of a mobject whose block is this size are gathered"""
        return self.shared_buffer(
            ("uniforms", block_size), self.mobject_layout, wgpu.BufferUsage.UNIFORM,
            "min-uniform-buffer-offset-alignment", UNIFORM_BLOCKS * block_size,
        )

    def data_buffer(self, record_size: int) -> SharedBuffer:
        """Where the records of a mobject whose records are this size are gathered"""
        # A mobject with no images of its own reads through the layout with none
        layout = self.resource_layout()
        return self.shared_buffer(
            ("records", record_size), layout, wgpu.BufferUsage.STORAGE,
            "min-storage-buffer-offset-alignment", RECORDS * record_size,
        )

    def shared_buffer(
        self, key: tuple, layout: Any, usage: int, limit: str, first_capacity: int,
    ) -> SharedBuffer:
        if key not in self.shared_buffers:
            self.shared_buffers[key] = SharedBuffer(
                self, layout, usage, self.device.limits[limit], first_capacity,
            )
        return self.shared_buffers[key]

    def begin_writes(self) -> None:
        """Gives back every stretch of every buffer, a frame's stretches being a frame's own"""
        for shared in self.shared_buffers.values():
            shared.reset()

    def end_writes(self) -> None:
        for shared in self.shared_buffers.values():
            shared.upload()

    def send_frame_uniforms(self) -> None:
        """The frame's uniforms, if they have been written to since they were last sent"""
        version = self.frame_uniforms.version
        if version != self.frame_version:
            self.frame_version = version
            self.queue.write_buffer(self.frame_buffer, 0, self.frame_uniforms.array)

    # Drawing

    @contextmanager
    def render_pass(self, attachments: dict) -> Iterator[RenderPass]:
        """
        The one render pass a frame is drawn in. Opening a pass loads its attachments into fast
        memory and ending one writes them back out, so a frame is a single pass from beginning
        to end, and everything it sends to the gpu happens before this opens.
        """
        encoder = self.device.create_command_encoder()
        render_pass = RenderPass(
            encoder.begin_render_pass(**attachments), self.frame_bind_group,
        )
        try:
            yield render_pass
        finally:
            render_pass.encoder.end()
            self.queue.submit([encoder.finish()])

    def bundle(self, draw: Callable[[RenderPass], None]) -> Any:
        """
        The draws a callable makes, gathered into a bundle to be replayed with one call rather
        than made again. Recorded without a pass open, a bundle being a thing of its own.
        """
        encoder = self.device.create_render_bundle_encoder(
            color_formats=[COLOR_FORMAT],
            depth_stencil_format=DEPTH_STENCIL_FORMAT,
            sample_count=self.samples,
        )
        draw(RenderPass(encoder, self.frame_bind_group))
        return encoder.finish()
