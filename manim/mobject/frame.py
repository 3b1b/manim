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
        Rectangle.__init__(self, width=aspect_ratio * height, height=height, **kwargs)

    @property
    def aspect_ratio(self):
        """The aspect ratio.

        When set, the width is stretched to accommodate
        the new aspect ratio.
        """

        return self.width / self.height

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        self.stretch_to_fit_width(value * self.height)


class FullScreenRectangle(ScreenRectangle):
    def __init__(self, **kwargs):
        ScreenRectangle.__init__(self, **kwargs)
        self.height = config["frame_height"]


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
        Rectangle.__init__(self, width=aspect_ratio * height, height=height, **kwargs)

    @property
    def aspect_ratio(self):
        """The aspect ratio.

        When set, the width is stretched to accommodate
        the new aspect ratio.
        """

        return self.width / self.height

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        self.stretch_to_fit_width(value * self.height)
