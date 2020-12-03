"""Special rectangles."""

__all__ = [
    "ScreenRectangle",
    "FullScreenRectangle",
    "FullScreenFadeRectangle",
    "PictureInPictureFrame",
]


from .. import config
from ..constants import *
from ..mobject.geometry import Rectangle
from ..utils.color import BLACK


class ScreenRectangle(Rectangle):
    def __init__(self, aspect_ratio=16.0 / 9.0, height=4, **kwargs):
        self.aspect_ratio = aspect_ratio
        self.height = height
        Rectangle.__init__(self, **kwargs)
        self.set_width(self.aspect_ratio * self.get_height(), stretch=True)


class FullScreenRectangle(ScreenRectangle):
    def __init__(self, **kwargs):
        ScreenRectangle.__init__(self, **kwargs)
        self.set_height(config["frame_height"])


class FullScreenFadeRectangle(FullScreenRectangle):
    def __init__(self, stroke_width=0, fill_color=BLACK, fill_opacity=0.7, **kwargs):
        FullScreenRectangle.__init__(
            self,
            stroke_width=stroke_width,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            **kwargs
        )


class PictureInPictureFrame(Rectangle):
    def __init__(self, height=3, aspect_ratio=16.0 / 9.0, **kwargs):
        self.height = height
        self.aspect_ratio = aspect_ratio
        Rectangle.__init__(
            self, width=self.aspect_ratio * self.height, height=self.height, **kwargs
        )
