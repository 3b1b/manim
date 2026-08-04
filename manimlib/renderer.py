from __future__ import annotations

import moderngl

from manimlib.utils.shaders import FRAME_BLOCK_BINDING
from manimlib.utils.shaders import FRAME_DTYPE
from manimlib.utils.shaders import Uniforms


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

    def send_frame_uniforms(self) -> None:
        """The frame's uniforms to the gpu, if they have been written to since last sent"""
        if self.frame_uniforms.version != self.sent_version:
            self.frame_uniform_buffer.write(self.frame_uniforms.array)
            self.sent_version = self.frame_uniforms.version
