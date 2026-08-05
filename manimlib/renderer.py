from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import wgpu

from manimlib.utils.shaders import DATA_BINDING
from manimlib.utils.shaders import FIRST_TEXTURE_BINDING
from manimlib.utils.shaders import FRAME_DTYPE
from manimlib.utils.shaders import FRAME_GROUP
from manimlib.utils.shaders import SAMPLER_BINDING
from manimlib.utils.shaders import Uniforms
from manimlib.utils.shaders import get_shader_code_from_file
from manimlib.utils.shaders import get_shader_module

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable


# Stencil bits alongside the depth, which a fill counting windings needs
DEPTH_STENCIL_FORMAT = wgpu.TextureFormat.depth24plus_stencil8
COLOR_FORMAT = wgpu.TextureFormat.rgba8unorm
PRESENT_SHADER = "present.wgsl"

KEEP = ("keep", "keep", "keep")


@dataclass(frozen=True)
class DrawState:
    """
    How a draw behaves, beyond which program runs and what it reads. All of it is baked into
    a pipeline, and there are only the few combinations named below.

    depth_test is None wherever the mobject decides, which is most of them. A fill counting
    windings is the exception: it must see every triangle of the path, whatever is in front.
    """
    depth_test: bool | None = None
    depth_write: bool = True
    color_write: bool = True
    # What the stencil buffer is compared against, "always" leaving it out of the decision
    stencil_compare: str = "always"
    # What to leave in the stencil buffer when the test fails, when depth fails, and when
    # the fragment is drawn: once for front facing triangles, once for back facing ones
    stencil_ops: tuple[tuple[str, str, str], tuple[str, str, str]] = (KEEP, KEEP)

    def tests_depth(self, depth_test: bool) -> bool:
        return depth_test if self.depth_test is None else self.depth_test

    def depth_stencil_descriptor(self, depth_test: bool) -> dict:
        """This state as a pipeline descriptor wants it"""
        def face(ops):
            fail, depth_fail, passed = ops
            return {
                "compare": self.stencil_compare,
                "fail_op": fail,
                "depth_fail_op": depth_fail,
                "pass_op": passed,
            }

        front, back = self.stencil_ops
        return {
            "format": DEPTH_STENCIL_FORMAT,
            "depth_write_enabled": self.depth_write,
            "depth_compare": "less" if self.tests_depth(depth_test) else "always",
            "stencil_front": face(front),
            "stencil_back": face(back),
            "stencil_read_mask": 0xFF,
            "stencil_write_mask": 0xFF,
        }

    @property
    def color_write_mask(self) -> int:
        return 0xF if self.color_write else 0


DEFAULT = DrawState()
# The three passes a fill takes, see VProgram.draw_fill
WINDING_COUNT = DrawState(
    depth_test=False,
    depth_write=False,
    color_write=False,
    stencil_ops=(
        ("keep", "increment-wrap", "increment-wrap"),
        ("keep", "decrement-wrap", "decrement-wrap"),
    ),
)
FILL_BORDER = DrawState(stencil_compare="equal", stencil_ops=(KEEP, KEEP))
WINDING_COVER = DrawState(
    stencil_compare="not-equal",
    stencil_ops=2 * (("keep", "zero", "zero"),),
)


@lru_cache()
def get_bind_layouts(device, frame_layout, mobject_layout, texture_count: int):
    """
    What a shader may bind: the frame's values, the mobject's values, and its records along
    with a texture for each image it names.

    Made once for each number of textures rather than once per mobject: a pipeline is built
    against these, so per mobject layouts would mean per mobject pipelines.
    """
    resource_entries = [{
        "binding": DATA_BINDING,
        "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
        # The stretch a draw reads is given as a dynamic offset, see DataArena
        "buffer": {
            "type": wgpu.BufferBindingType.read_only_storage,
            "has_dynamic_offset": True,
        },
    }]
    if texture_count:
        resource_entries.append({
            "binding": SAMPLER_BINDING,
            "visibility": wgpu.ShaderStage.FRAGMENT,
            "sampler": {"type": wgpu.SamplerBindingType.filtering},
        })
        resource_entries += [{
            "binding": FIRST_TEXTURE_BINDING + index,
            "visibility": wgpu.ShaderStage.FRAGMENT,
            "texture": {"sample_type": wgpu.TextureSampleType.float},
        } for index in range(texture_count)]

    resource_layout = device.create_bind_group_layout(entries=resource_entries)
    pipeline_layout = device.create_pipeline_layout(bind_group_layouts=[
        frame_layout, mobject_layout, resource_layout,
    ])
    return resource_layout, pipeline_layout


class Arena(object):
    """
    One buffer holding what many mobjects read, a stretch of it each, sent in one write.
    Sending a buffer costs about the same whatever it holds, so gathering beats sending one
    mobject at a time.

    A stretch is claimed for the length of a frame rather than owned. A frame writes everything
    before it draws anything, see Camera.capture, so stretches are handed out in the order the
    writing goes and given back all at once: no free list, nothing to fragment, nothing to free.

    A scene which is not changing hands them out in the same order every frame, so a mobject
    whose values have not moved finds them in place and copies nothing, and an arena nothing
    wrote into is not sent.
    """

    def __init__(self, renderer: Renderer, first_capacity: int):
        self.renderer = renderer
        self.device = renderer.device
        self.first_capacity = first_capacity
        self.used = 0
        self.capacity = 0
        # Nothing is set aside until a stretch is asked for, a scene having kinds of mobject
        # it never draws
        self.blocks = np.zeros(0, dtype=np.uint8)
        self.bytes = memoryview(self.blocks)
        self.buffer = None
        self.bind_group = None
        self.dirty: tuple[int, int] | None = None

    def grow_to(self, needed: int) -> bool:
        """
        Room for that many bytes, and whether that meant a new buffer, in which case the
        caller makes its bindings afresh.
        """
        capacity = max(self.capacity, self.first_capacity)
        while capacity < needed:
            capacity *= 2
        if capacity == self.capacity:
            return False

        # Carried over so that a stretch which was already right stays right, though the new
        # buffer holds none of it yet
        held = self.blocks
        self.capacity = capacity
        self.blocks = np.zeros(capacity, dtype=np.uint8)
        self.blocks[:len(held)] = held
        # A memoryview slice being half the cost of a numpy one at these sizes
        self.bytes = memoryview(self.blocks)
        self.buffer = self.device.create_buffer(size=capacity, usage=self.usage)
        self.dirty = (0, self.used)
        return True

    def reset(self) -> None:
        self.used = 0

    def put(self, offset: int, source: np.ndarray) -> None:
        end = offset + len(source)
        self.bytes[offset:end] = source
        if self.dirty is None:
            self.dirty = (offset, end)
        else:
            self.dirty = (min(self.dirty[0], offset), max(self.dirty[1], end))

    def upload(self) -> None:
        """Whatever was written into since the last send, in one write"""
        if self.dirty is None:
            return
        start, end = self.dirty
        self.renderer.queue.write_buffer(
            self.buffer, start, self.blocks, start, end - start,
        )
        self.dirty = None


class UniformArena(Arena):
    """
    An arena of mobject uniform blocks, a row each. A draw is given its row as a dynamic
    offset, so rows begin where the device allows a binding to.
    """
    usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST

    def __init__(self, renderer: Renderer, block_size: int, rows: int = 256):
        self.block_size = block_size
        alignment = renderer.device.limits["min-uniform-buffer-offset-alignment"]
        self.stride = block_size + (-block_size % alignment)
        super().__init__(renderer, rows * self.stride)

    def make_bindings(self) -> None:
        self.bind_group = self.device.create_bind_group(
            layout=self.renderer.mobject_layout,
            entries=[{"binding": 0, "resource": {
                "buffer": self.buffer, "offset": 0, "size": self.block_size,
            }}],
        )

    def next_row(self) -> int:
        """Where the next block goes, as the offset its draw is to be given"""
        offset = self.used
        self.used += self.stride
        if self.grow_to(self.used):
            self.make_bindings()
        return offset


class DataArena(Arena):
    """
    An arena of mobject records, every mobject whose records are the same size sharing one.

    A draw is given its stretch as a dynamic offset, so the shader counts records from the
    front of what it was given. Keeping the offset out of the mobject's own values matters:
    those get interpolated, and a blended offset points nowhere.

    Stretches therefore begin where the device allows a binding to, and the window bound is
    wide enough for the longest mobject there has been, one bind group serving them all.
    """
    usage = wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST

    def __init__(self, renderer: Renderer, record_size: int, records: int = 4096):
        self.record_size = record_size
        self.alignment = renderer.device.limits["min-storage-buffer-offset-alignment"]
        self.window = self.alignment
        super().__init__(renderer, records * record_size)

    def make_bindings(self) -> None:
        self.bind_group = self.device.create_bind_group(
            layout=self.renderer.data_layout,
            entries=[{"binding": DATA_BINDING, "resource": {
                "buffer": self.buffer, "offset": 0, "size": self.window,
            }}],
        )

    def claim_stretch(self, nbytes: int) -> int:
        """
        Where this mobject's records go, as the offset its draw is to be given.

        One bind group serves every mobject of the arena, so the window it binds has to be
        wide enough for the longest of them, and there has to be a whole window of buffer past
        the last stretch for the shortest one's binding not to run off the end.
        """
        stretch = nbytes + -nbytes % self.alignment
        offset = self.used
        self.used += stretch
        wider = stretch > self.window
        if wider:
            self.window = stretch
        if self.grow_to(self.used + self.window) or wider:
            self.make_bindings()
        return offset


class Renderer(object):
    """
    What a mobject needs of the gpu in order to draw itself: the device its buffers and
    programs are made from, the arenas its values are gathered in, the pipelines it is drawn
    by, the pass it is drawn into, and the values which hold for a whole frame.

    Those last are written once a frame by the camera and read by every program from group 0,
    see inserts/frame_uniforms.wgsl.

    A frame is one render pass from beginning to end, since opening a pass loads its
    attachments into fast memory and ending one writes them back out. So everything a frame
    sends to the gpu happens before the pass opens, see Camera.capture.
    """

    def __init__(self):
        self.adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
        self.device = self.adapter.request_device_sync()
        self.queue = self.device.queue

        self.frame_uniforms = Uniforms(FRAME_DTYPE)
        self.frame_buffer = self.device.create_buffer(
            size=self.frame_uniforms.array.nbytes,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )
        self.frame_layout = self.device.create_bind_group_layout(entries=[{
            "binding": 0,
            "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
            "buffer": {"type": wgpu.BufferBindingType.uniform},
        }])
        # One row of an arena at a time, see UniformArena. Shared by every mobject, so that a
        # pipeline built against it is too.
        self.mobject_layout = self.device.create_bind_group_layout(entries=[{
            "binding": 0,
            "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
            "buffer": {
                "type": wgpu.BufferBindingType.uniform,
                "has_dynamic_offset": True,
            },
        }])
        # What a mobject with no images of its own reads its records through, see DataArena
        self.data_layout, _ = get_bind_layouts(
            self.device, self.frame_layout, self.mobject_layout, 0,
        )
        # Every arena, for the two moments a frame speaks to all of them, and the two ways of
        # finding the one a mobject belongs in
        self.arenas: list[Arena] = []
        self.uniform_arenas: dict[int, UniformArena] = dict()
        self.data_arenas: dict[int, DataArena] = dict()
        self.frame_bind_group = self.device.create_bind_group(
            layout=self.frame_layout,
            entries=[{"binding": 0, "resource": {
                "buffer": self.frame_buffer, "offset": 0, "size": self.frame_buffer.size,
            }}],
        )

        # Every pipeline has to match this, which the camera sets when it makes its
        # attachments
        self.samples = 1
        self.pipelines: dict[Any, Any] = dict()
        self.encoder = None
        self.pass_ = None
        # What the pass has been told already, see bind and use_pipeline
        self.bound: list[Any] = 3 * [None]
        self.pipeline_in_use: Any = None
        self.init_present_resources()

    def send_frame_uniforms(self) -> None:
        """The frame's uniforms, if they have been written to since they were last sent"""
        if self.frame_uniforms.has_changed(observer=self):
            self.queue.write_buffer(self.frame_buffer, 0, self.frame_uniforms.array)

    def get_pipeline(self, key: Any, build: Callable[[], Any]):
        """
        The pipeline for a key, built the first time it is asked for. A pipeline settles
        everything about a draw but its bindings, so a key has to name all of that.
        """
        pipeline = self.pipelines.get(key)
        if pipeline is None:
            pipeline = self.pipelines[key] = build()
        return pipeline

    def uniform_arena_for(self, block_size: int) -> UniformArena:
        """Where the uniforms of a mobject whose block is this size are gathered"""
        if block_size not in self.uniform_arenas:
            self.uniform_arenas[block_size] = UniformArena(self, block_size)
            self.arenas.append(self.uniform_arenas[block_size])
        return self.uniform_arenas[block_size]

    def data_arena_for(self, record_size: int) -> DataArena:
        """Where the records of a mobject whose records are this size are gathered"""
        if record_size not in self.data_arenas:
            self.data_arenas[record_size] = DataArena(self, record_size)
            self.arenas.append(self.data_arenas[record_size])
        return self.data_arenas[record_size]

    def begin_writes(self) -> None:
        """Gives back every stretch of every arena, a frame's stretches being a frame's own"""
        for arena in self.arenas:
            arena.reset()

    def end_writes(self) -> None:
        for arena in self.arenas:
            arena.upload()

    def bind(self, group: int, bind_group: Any, offsets: tuple = ()) -> None:
        """
        Points the pass at what a draw is to read, unless that is where it points already. A
        pass holds onto what it was told, and a mobject drawn in several passes reads the same
        things in each.
        """
        if self.bound[group] != (bind_group, offsets):
            self.pass_.set_bind_group(group, bind_group, offsets)
            self.bound[group] = (bind_group, offsets)

    def use_pipeline(self, pipeline: Any) -> None:
        if self.pipeline_in_use is not pipeline:
            self.pass_.set_pipeline(pipeline)
            self.pipeline_in_use = pipeline

    def begin_frame(self, attachments: dict) -> None:
        """Opens the one render pass a frame is drawn in"""
        self.encoder = self.device.create_command_encoder()
        self.pass_ = self.encoder.begin_render_pass(**attachments)
        # A new pass has been told nothing, whatever the last one knew
        self.bound = 3 * [None]
        self.pipeline_in_use = None
        self.bind(FRAME_GROUP, self.frame_bind_group)

    def end_frame(self) -> None:
        self.pass_.end()
        self.queue.submit([self.encoder.finish()])
        self.pass_ = None
        self.encoder = None

    def present(self, frame_view, target_view, format: str) -> None:
        """
        Draws a finished frame onto what a window will show, stretched to fill it, see
        shaders/present.wgsl. A pass of its own, the two textures differing in size and format.
        """
        module = get_shader_module(self.device, get_shader_code_from_file(PRESENT_SHADER))
        layout = self.present_layout
        pipeline = self.get_pipeline(
            (module, format),
            lambda: self.device.create_render_pipeline(
                layout=self.device.create_pipeline_layout(bind_group_layouts=[layout]),
                vertex={"module": module, "entry_point": "vs_main"},
                fragment={
                    "module": module,
                    "entry_point": "fs_main",
                    "targets": [{"format": format}],
                },
                primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
            ),
        )
        bind_group = self.device.create_bind_group(layout=layout, entries=[
            {"binding": 0, "resource": frame_view},
            {"binding": 1, "resource": self.present_sampler},
        ])

        encoder = self.device.create_command_encoder()
        render_pass = encoder.begin_render_pass(color_attachments=[{
            "view": target_view,
            "load_op": wgpu.LoadOp.clear,
            "store_op": wgpu.StoreOp.store,
            "clear_value": (0.0, 0.0, 0.0, 1.0),
        }])
        render_pass.set_pipeline(pipeline)
        render_pass.set_bind_group(0, bind_group)
        render_pass.draw(3)
        render_pass.end()
        self.queue.submit([encoder.finish()])

    def init_present_resources(self) -> None:
        """What Renderer.present reads a finished frame through, made once"""
        self.present_layout = self.device.create_bind_group_layout(entries=[
            {
                "binding": 0,
                "visibility": wgpu.ShaderStage.FRAGMENT,
                "texture": {"sample_type": wgpu.TextureSampleType.float},
            },
            {
                "binding": 1,
                "visibility": wgpu.ShaderStage.FRAGMENT,
                "sampler": {"type": wgpu.SamplerBindingType.filtering},
            },
        ])
        # Smoothly, since a window is rarely exactly the size of the frame drawn for it
        self.present_sampler = self.device.create_sampler(
            mag_filter=wgpu.FilterMode.linear, min_filter=wgpu.FilterMode.linear,
        )
