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
from ..utils.config_ops import digest_config
from ..utils.color import BLACK


class ScreenRectangle(Rectangle):
    CONFIG = {"aspect_ratio": 16.0 / 9.0, "height": 4}

    def __init__(self, **kwargs):
        Rectangle.__init__(self, **kwargs)
        self.set_width(self.aspect_ratio * self.get_height(), stretch=True)


class FullScreenRectangle(ScreenRectangle):
    def __init__(self, **kwargs):
        ScreenRectangle.__init__(self, **kwargs)
        self.set_height(config["frame_height"])


class FullScreenFadeRectangle(FullScreenRectangle):
    CONFIG = {
        "stroke_width": 0,
        "fill_color": BLACK,
        "fill_opacity": 0.7,
    }


class PictureInPictureFrame(Rectangle):
    CONFIG = {"height": 3, "aspect_ratio": 16.0 / 9.0}

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Rectangle.__init__(
            self, width=self.aspect_ratio * self.height, height=self.height, **kwargs
        )
