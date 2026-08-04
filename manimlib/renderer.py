from __future__ import annotations

from dataclasses import dataclass

import moderngl
import OpenGL.GL as gl

from manimlib.utils.shaders import FRAME_BLOCK_BINDING
from manimlib.utils.shaders import FRAME_DTYPE
from manimlib.utils.shaders import Uniforms


@dataclass(frozen=True)
class DrawState:
    """
    How a draw behaves, beyond which program runs and what it reads: whether depth decides
    what is hidden and whether it is written, whether the stencil buffer is tested and what
    it is left holding, whether color is written at all, and which facing is dropped.

    Said as a value rather than poked into place around each draw, both because manim only
    ever asks for the handful of combinations named below, and because wgpu takes exactly
    this and bakes it into a pipeline object built once.

    depth_test is None wherever the mobject being drawn decides, which is most of them. A
    fill counting windings is the exception: it has to see every triangle of the path,
    whatever stands in front of it.
    """
    depth_test: bool | None = None
    depth_write: bool = True
    color_write: bool = True
    cull: int | None = None
    # (function, reference, mask), or None to leave the stencil buffer out of it
    stencil_func: tuple[int, int, int] | None = None
    # What to leave in the stencil buffer when the test fails, when depth fails, and when
    # the fragment is drawn: once for front facing triangles, once for back facing ones
    stencil_ops: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None


KEEP = (gl.GL_KEEP, gl.GL_KEEP, gl.GL_KEEP)

DEFAULT = DrawState()
# A surface draws the side of itself facing away from the camera before the side facing
# towards it, each pass dropping the other, see SurfaceShaderWrapper
CULL_FRONT = DrawState(cull=gl.GL_FRONT)
CULL_BACK = DrawState(cull=gl.GL_BACK)
# The three passes a fill takes, see VShaderWrapper.render_fill for what each is for
WINDING_COUNT = DrawState(
    depth_test=False,
    depth_write=False,
    color_write=False,
    stencil_func=(gl.GL_ALWAYS, 0, 0xFF),
    stencil_ops=(
        (gl.GL_KEEP, gl.GL_INCR_WRAP, gl.GL_INCR_WRAP),
        (gl.GL_KEEP, gl.GL_DECR_WRAP, gl.GL_DECR_WRAP),
    ),
)
FILL_BORDER = DrawState(stencil_func=(gl.GL_EQUAL, 0, 0xFF), stencil_ops=(KEEP, KEEP))
WINDING_COVER = DrawState(
    stencil_func=(gl.GL_NOTEQUAL, 0, 0xFF),
    stencil_ops=2 * ((gl.GL_KEEP, gl.GL_ZERO, gl.GL_ZERO),),
)


class Renderer(object):
    """
    What a mobject needs of the gpu in order to draw itself, in one thing rather than
    several.

    That is the context it belongs to, which is where its buffers are made and its
    programs compiled, and the values which hold for every mobject of a frame: where the
    camera is, what it is looking along, and where the light is.

    Those travel in one block, written once a frame by the camera which owns this and read
    by every program from the one buffer it is bound to, see inserts/frame_uniforms.glsl.
    A mobject wanting one of them, as a surface sorting its triangles wants the camera
    position, reads it from frame_uniforms rather than being told.
    """

    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
        self.frame_uniforms = Uniforms(FRAME_DTYPE)
        self.frame_uniform_buffer = ctx.buffer(self.frame_uniforms.array)
        self.sent_version = 0
        # Nothing else binds here, so the buffer stays bound for the life of the renderer
        # and only its contents are written afresh
        self.frame_uniform_buffer.bind_to_uniform_block(FRAME_BLOCK_BINDING)
        # What state the context is in, so that a draw asking for the state it is already
        # in says nothing to the driver, see use
        self.state = DEFAULT
        self.depth_test = False

    def send_frame_uniforms(self) -> None:
        """The frame's uniforms to the gpu, if they have been written to since last sent"""
        if self.frame_uniforms.version != self.sent_version:
            self.frame_uniform_buffer.write(self.frame_uniforms.array)
            self.sent_version = self.frame_uniforms.version

    def use(self, state: DrawState, depth_test: bool = False) -> None:
        """
        Puts the context into the state a draw asks for, saying only what differs from the
        state it is already in, which is usually nothing at all: consecutive draws mostly
        want the same state, and the states differ from one another in a field or two.

        Whether depth is tested is kept apart from the rest, since it is the one thing the
        mobject being drawn has a say in, see DrawState.
        """
        if state.depth_test is not None:
            depth_test = state.depth_test
        if depth_test != self.depth_test:
            if depth_test:
                self.ctx.enable(moderngl.DEPTH_TEST)
            else:
                self.ctx.disable(moderngl.DEPTH_TEST)
            self.depth_test = depth_test
        current = self.state
        if state is current:
            return
        if state.depth_write != current.depth_write:
            gl.glDepthMask(state.depth_write)
        if state.color_write != current.color_write:
            gl.glColorMask(*4 * [state.color_write])
        if state.cull != current.cull:
            if state.cull is None:
                gl.glDisable(gl.GL_CULL_FACE)
            else:
                gl.glEnable(gl.GL_CULL_FACE)
                gl.glCullFace(state.cull)
        if (state.stencil_func is None) != (current.stencil_func is None):
            if state.stencil_func is None:
                gl.glDisable(gl.GL_STENCIL_TEST)
            else:
                gl.glEnable(gl.GL_STENCIL_TEST)
        if state.stencil_func is not None and state.stencil_func != current.stencil_func:
            gl.glStencilFunc(*state.stencil_func)
        if state.stencil_ops is not None and state.stencil_ops != current.stencil_ops:
            front, back = state.stencil_ops
            gl.glStencilOpSeparate(gl.GL_FRONT, *front)
            gl.glStencilOpSeparate(gl.GL_BACK, *back)
        self.state = state

    def reset_state(self) -> None:
        """
        Says every part of the default state whether the context is in it or not, since
        using a framebuffer or clearing one goes behind this class's back where the masks
        are concerned. Called once a frame, before anything is drawn.
        """
        self.ctx.disable(moderngl.DEPTH_TEST)
        gl.glDepthMask(True)
        gl.glColorMask(True, True, True, True)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_STENCIL_TEST)
        self.depth_test = False
        self.state = DEFAULT
