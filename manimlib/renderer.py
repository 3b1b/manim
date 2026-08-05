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
    from typing import Any, Callable, Optional


# A depth buffer with stencil bits alongside it, which is what a fill counting windings
# needs. WebGPU guarantees this format, so unlike GL there is nothing to arrange by hand.
DEPTH_STENCIL_FORMAT = wgpu.TextureFormat.depth24plus_stencil8
# What a frame is drawn into and read back from
COLOR_FORMAT = wgpu.TextureFormat.rgba8unorm
# The shader which puts a finished frame on screen, see Renderer.present
PRESENT_SHADER = "present.wgsl"

KEEP = ("keep", "keep", "keep")


@dataclass(frozen=True)
class DrawState:
    """
    How a draw behaves, beyond which program runs and what it reads: whether depth decides
    what is hidden and whether it is written, whether the stencil buffer is tested and what
    it is left holding, and whether color is written at all.

    All of it is settled when a pipeline is built rather than said around each draw, which
    is what wgpu asks for, and there are only the handful of combinations named below.

    depth_test is None wherever the mobject being drawn decides, which is most of them. A
    fill counting windings is the exception: it has to see every triangle of the path,
    whatever stands in front of it.

    Nothing here drops a triangle for the way it faces. Both sides of a surface are drawn,
    the depth test settling an opaque one and the order of its triangles a see through one,
    see SurfaceShaderWrapper.
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
        """What this settles about depth and stencil, as a pipeline wants to hear it"""
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
            # Where depth is not being tested, everything passes whatever its depth
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
# The three passes a fill takes, see VShaderWrapper.render_fill for what each is for
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
    What a shader may bind: the values for the whole frame, the values for the mobject being
    drawn, and the records of its kind along with a texture for each image it names.

    None of that varies between two mobjects of a kind, so it is made once for each number of
    textures a kind might have. Which matters: a pipeline is built against these, so making
    them per mobject would have every mobject compiling pipelines of its own.
    """
    resource_entries = [{
        "binding": DATA_BINDING,
        "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
        # Which stretch of the arena is the mobject's own is said around the draw, so that
        # nothing about where its records are has to live among its values, see DataArena
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
    One buffer holding what many mobjects read, a stretch of it each, gathered a frame at a
    time and sent in one write.

    A stretch is claimed for the length of a frame rather than owned: a frame writes everything
    before it draws anything, see Camera.capture, so the stretches can be handed out in the
    order the writing goes and given back all at once. Nothing is allocated and nothing is
    freed, so there is no free list to keep, nothing to fragment, and no way for a mobject to
    be left holding a stretch it has no use for.

    The point of it is that sending a buffer costs about the same whatever it holds: 4.7us for
    one mobject's uniforms and 178us for two megabytes of every mobject's points. So a frame of
    six thousand mobjects, which sent six thousand times, gathers here at a memory copy each
    and sends the stretch which changed.

    Two things keep it from costing anything where there is nothing to gain. A scene which is
    not changing hands its stretches out in the same order every frame, so a mobject whose
    values have not moved finds them already in place and copies nothing; and only what was
    written into is sent, which for such a frame is nothing at all.
    """

    def __init__(self, renderer: Renderer, capacity: int):
        self.renderer = renderer
        self.device = renderer.device
        self.used = 0
        self.make_room(capacity)

    def make_room(self, capacity: int) -> None:
        """
        A buffer of that many bytes, and whatever reads it. Growing means making both afresh,
        which only happens while a frame is being written, so nothing is drawing through the
        old ones. What the stretches held is carried over, so one which was already right
        stays right, but the new buffer holds none of it yet.
        """
        held = getattr(self, "blocks", None)
        self.capacity = capacity
        self.blocks = np.zeros(capacity, dtype=np.uint8)
        if held is not None:
            self.blocks[:len(held)] = held
        # Copied into a stretch at a time through this rather than through the array, a
        # memoryview slice being half the cost of a numpy one at these sizes
        self.bytes = memoryview(self.blocks)
        self.buffer = self.device.create_buffer(size=capacity, usage=self.usage)
        self.make_bindings()
        self.dirty: tuple[int, int] | None = (0, self.used)

    def reset(self) -> None:
        self.used = 0

    def claim(self, nbytes: int) -> int:
        """Where the next stretch of that many bytes begins, making room if there is none"""
        offset = self.used
        self.used += nbytes
        while self.used > self.capacity:
            self.make_room(2 * self.capacity)
        return offset

    def put(self, offset: int, source: np.ndarray) -> None:
        end = offset + len(source)
        self.bytes[offset:end] = source
        if self.dirty is None:
            self.dirty = (offset, end)
        else:
            self.dirty = (min(self.dirty[0], offset), max(self.dirty[1], end))

    def upload(self) -> None:
        """Whatever was written into since the last frame sent, in one write"""
        if self.dirty is None:
            return
        start, end = self.dirty
        self.renderer.queue.write_buffer(
            self.buffer, start, self.blocks, start, end - start,
        )
        self.dirty = None


class UniformArena(Arena):
    """
    An arena of mobject uniform blocks, a row each. Which row a draw reads comes from the
    dynamic offset its bind group takes, so a row has to begin where the device allows one to,
    see ShaderWrapper.render.
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
        return self.claim(self.stride)


class DataArena(Arena):
    """
    An arena of mobject records, every mobject whose records are the same size sharing one.

    A draw is given the stretch belonging to the mobject being drawn, as the dynamic offset of
    its bind group, so the shader counts a record from the front of what it was given and
    nothing about where a mobject's records are has to live among the mobject's own values.
    Which matters: a mobject's values get copied, interpolated and handed to other mobjects,
    and an offset put among them would be blended halfway through a transform.

    A stretch therefore begins where the device allows a binding to, and the window bound is
    wide enough for the longest mobject there has been, since one bind group serves them all.
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
        if stretch > self.window or self.used + self.window > self.capacity:
            self.window = max(self.window, stretch)
            capacity = self.capacity
            while self.used + self.window > capacity:
                capacity *= 2
            self.make_room(capacity)
        return offset


class Renderer(object):
    """
    What a mobject needs of the gpu in order to draw itself, in one thing rather than
    several: the device its buffers and programs are made from, the pipelines it is drawn
    by, the pass it is drawn into, and the values which hold for every mobject of a frame.

    Those last travel in one block, written once a frame by the camera which owns this and
    read by every program from group 0, see inserts/frame_uniforms.wgsl. A mobject wanting
    one of them, as a surface sorting its triangles wants the camera position, reads it from
    frame_uniforms rather than being told.

    A frame is one render pass from beginning to end. Beginning a pass loads the frame's
    attachments into fast memory on the sort of gpu this port is for, and ending one writes
    them back out, so a pass for every mobject would cost more than all the drawing. So
    everything a frame sends to the gpu happens before the pass opens, see Camera.capture.
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
        # What a mobject's uniforms are read through, one row of an arena at a time, see
        # UniformArena. Shared by every mobject, so that a pipeline built against it is too.
        self.mobject_layout = self.device.create_bind_group_layout(entries=[{
            "binding": 0,
            "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
            "buffer": {
                "type": wgpu.BufferBindingType.uniform,
                "has_dynamic_offset": True,
            },
        }])
        # What a mobject reads its own records through, which is the same for every mobject
        # of a size that has no images of its own, see DataArena
        self.data_layout, _ = get_bind_layouts(
            self.device, self.frame_layout, self.mobject_layout, 0,
        )
        # Every arena there is, for the two moments a frame speaks to all of them, along with
        # the two ways of finding the one a mobject belongs in
        self.arenas: list[Arena] = []
        self.uniform_arenas: dict[int, UniformArena] = dict()
        self.data_arenas: dict[int, DataArena] = dict()
        self.frame_bind_group = self.device.create_bind_group(
            layout=self.frame_layout,
            entries=[{"binding": 0, "resource": {
                "buffer": self.frame_buffer, "offset": 0, "size": self.frame_buffer.size,
            }}],
        )

        # How many samples a frame's attachments take, which every pipeline has to match.
        # The camera says, when it makes what it draws into.
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
        The pipeline for a key, built the first time it is asked for. Everything a draw
        settles sits in one of these, so there is one for each combination of program, draw
        state, whether the mobject is depth tested, and how many samples are taken: a key
        has to name all of that.
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
        Points the pass at what a draw is to read, unless that is where it points already.
        A pass holds onto what it was told until it is told otherwise, and a mobject drawn in
        several passes reads the same things in each, so most of what a frame has to say
        about this it has said already, see ShaderWrapper.render.
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
        shaders/present.wgsl. This is a pass of its own rather than part of the
        frame's, the two drawing into textures of different sizes and formats.
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
