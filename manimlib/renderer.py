from __future__ import annotations

import moderngl


class Renderer(object):
    """
    What a mobject needs of the gpu in order to draw itself, in one thing rather than
    several.

    For now that is the context it belongs to, which is where its buffers are made and
    its programs compiled. It is also where whatever holds for a whole frame will sit,
    the camera's own uniforms among it, rather than being pushed into every program
    separately: a mobject asks the renderer for what it shares with all the others, and
    the renderer is handed to it once a frame by the camera which owns it.
    """

    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
