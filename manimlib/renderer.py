from __future__ import annotations

import os
from dataclasses import dataclass

import wgpu

from manimlib.utils.shaders import FRAME_DTYPE
from manimlib.utils.shaders import FRAME_GROUP
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
PRESENT_SHADER = os.path.join("present", "shader.wgsl")

KEEP = ("keep", "keep", "keep")


@dataclass(frozen=True)
class DrawState:
    """
    How a draw behaves, beyond which program runs and what it reads: whether depth decides
    what is hidden and whether it is written, whether the stencil buffer is tested and what
    it is left holding, whether color is written at all, and which facing is dropped.

    All of it is settled when a pipeline is built rather than said around each draw, which
    is what wgpu asks for, and there are only the handful of combinations named below.

    depth_test is None wherever the mobject being drawn decides, which is most of them. A
    fill counting windings is the exception: it has to see every triangle of the path,
    whatever stands in front of it.
    """
    depth_test: bool | None = None
    depth_write: bool = True
    color_write: bool = True
    cull: str | None = None
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
# A surface draws the side of itself facing away from the camera before the side facing
# towards it, each pass dropping the other, see SurfaceShaderWrapper
CULL_FRONT = DrawState(cull="front")
CULL_BACK = DrawState(cull="back")
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
        self.frame_bind_group = self.device.create_bind_group(
            layout=self.frame_layout,
            entries=[{"binding": 0, "resource": {
                "buffer": self.frame_buffer, "offset": 0, "size": self.frame_buffer.size,
            }}],
        )
        self.sent_version = 0

        # How many samples a frame's attachments take, which every pipeline has to match.
        # The camera says, when it makes what it draws into.
        self.samples = 1
        self.pipelines: dict[Any, Any] = dict()
        self.encoder = None
        self.pass_ = None
        self.init_present_resources()

    def send_frame_uniforms(self) -> None:
        """The frame's uniforms, if they have been written to since they were last sent"""
        if self.frame_uniforms.version != self.sent_version:
            self.queue.write_buffer(self.frame_buffer, 0, self.frame_uniforms.array)
            self.sent_version = self.frame_uniforms.version

    def get_pipeline(self, key: Any, build: Callable[[], Any]):
        """
        The pipeline for a key, built the first time it is asked for. Everything a draw
        settles sits in one of these, so there is one for each combination of program, draw
        state, whether the mobject is depth tested, and how many samples are taken: a key
        has to name all of that.
        """
        if key not in self.pipelines:
            self.pipelines[key] = build()
        return self.pipelines[key]

    def begin_frame(self, attachments: dict) -> None:
        """Opens the one render pass a frame is drawn in"""
        self.encoder = self.device.create_command_encoder()
        self.pass_ = self.encoder.begin_render_pass(**attachments)
        self.pass_.set_bind_group(FRAME_GROUP, self.frame_bind_group)

    def end_frame(self) -> None:
        self.pass_.end()
        self.queue.submit([self.encoder.finish()])
        self.pass_ = None
        self.encoder = None

    def present(self, frame_view, target_view, format: str) -> None:
        """
        Draws a finished frame onto what a window will show, stretched to fill it, see
        shaders/present/shader.wgsl. This is a pass of its own rather than part of the
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
