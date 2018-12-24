from manimlib.constants import *
from manimlib.mobject.geometry import Rectangle
from manimlib.utils.config_ops import digest_config


class ScreenRectangle(Rectangle):
    CONFIG = {
        "width_to_height_ratio": 16.0 / 9.0,
        "height": 4,
    }

    def generate_points(self):
        self.width = self.width_to_height_ratio * self.height
        Rectangle.generate_points(self)


class FullScreenRectangle(ScreenRectangle):
    CONFIG = {
        "height": FRAME_HEIGHT,
    }


class FullScreenFadeRectangle(FullScreenRectangle):
    CONFIG = {
        "stroke_width": 0,
        "fill_color": BLACK,
        "fill_opacity": 0.7,
    }


class PictureInPictureFrame(Rectangle):
    CONFIG = {
        "height": 3,
        "aspect_ratio": (16, 9)
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        height = self.height
        if "height" in kwargs:
            kwargs.pop("height")
        Rectangle.__init__(
            self,
            width=self.aspect_ratio[0],
            height=self.aspect_ratio[1],
            **kwargs
        )
        self.set_height(height)
