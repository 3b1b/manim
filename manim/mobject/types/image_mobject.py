__all__ = ["AbstractImageMobject", "ImageMobject", "ImageMobjectFromCamera"]


import numpy as np

from PIL import Image

from ...constants import *
from ...mobject.mobject import Mobject
from ...mobject.shape_matchers import SurroundingRectangle
from ...utils.bezier import interpolate
from ...utils.color import color_to_int_rgb
from ...utils.config_ops import digest_config
from ...utils.images import get_full_raster_image_path


class AbstractImageMobject(Mobject):
    """
    Automatically filters out black pixels
    """

    CONFIG = {
        "height": 2.0,
        "pixel_array_dtype": "uint8",
    }

    def get_pixel_array(self):
        raise Exception("Not implemented")

    def set_color(self):
        # Likely to be implemented in subclasses, but no obgligation
        pass

    def reset_points(self):
        # Corresponding corners of image are fixed to these 3 points
        self.points = np.array(
            [
                UP + LEFT,
                UP + RIGHT,
                DOWN + LEFT,
            ]
        )
        self.center()
        h, w = self.get_pixel_array().shape[:2]
        self.stretch_to_fit_height(self.height)
        self.stretch_to_fit_width(self.height * w / h)


class ImageMobject(AbstractImageMobject):
    CONFIG = {
        "invert": False,
        "image_mode": "RGBA",
    }

    def __init__(self, filename_or_array, **kwargs):
        digest_config(self, kwargs)
        if isinstance(filename_or_array, str):
            path = get_full_raster_image_path(filename_or_array)
            image = Image.open(path).convert(self.image_mode)
            self.pixel_array = np.array(image)
        else:
            self.pixel_array = np.array(filename_or_array)
        self.change_to_rgba_array()
        if self.invert:
            self.pixel_array[:, :, :3] = 255 - self.pixel_array[:, :, :3]
        AbstractImageMobject.__init__(self, **kwargs)

    def change_to_rgba_array(self):
        pa = self.pixel_array
        if len(pa.shape) == 2:
            pa = pa.reshape(list(pa.shape) + [1])
        if pa.shape[2] == 1:
            pa = pa.repeat(3, axis=2)
        if pa.shape[2] == 3:
            alphas = 255 * np.ones(
                list(pa.shape[:2]) + [1], dtype=self.pixel_array_dtype
            )
            pa = np.append(pa, alphas, axis=2)
        self.pixel_array = pa

    def get_pixel_array(self):
        return self.pixel_array

    def set_color(self, color, alpha=None, family=True):
        rgb = color_to_int_rgb(color)
        self.pixel_array[:, :, :3] = rgb
        if alpha is not None:
            self.pixel_array[:, :, 3] = int(255 * alpha)
        for submob in self.submobjects:
            submob.set_color(color, alpha, family)
        self.color = color
        return self

    def set_opacity(self, alpha):
        self.pixel_array[:, :, 3] = int(255 * alpha)
        return self

    def fade(self, darkness=0.5, family=True):
        self.set_opacity(1 - darkness)
        super().fade(darkness, family)
        return self

    def interpolate_color(self, mobject1, mobject2, alpha):
        assert mobject1.pixel_array.shape == mobject2.pixel_array.shape
        self.pixel_array = interpolate(
            mobject1.pixel_array, mobject2.pixel_array, alpha
        ).astype(self.pixel_array_dtype)


# TODO, add the ability to have the dimensions/orientation of this
# mobject more strongly tied to the frame of the camera it contains,
# in the case where that's a MovingCamera


class ImageMobjectFromCamera(AbstractImageMobject):
    CONFIG = {
        "default_display_frame_config": {
            "stroke_width": 3,
            "stroke_color": WHITE,
            "buff": 0,
        }
    }

    def __init__(self, camera, **kwargs):
        self.camera = camera
        AbstractImageMobject.__init__(self, **kwargs)

    def get_pixel_array(self):
        return self.camera.get_pixel_array()

    def add_display_frame(self, **kwargs):
        config = dict(self.default_display_frame_config)
        config.update(kwargs)
        self.display_frame = SurroundingRectangle(self, **config)
        self.add(self.display_frame)
        return self
