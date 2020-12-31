"""Mobjects representing raster images."""

__all__ = ["AbstractImageMobject", "ImageMobject", "ImageMobjectFromCamera"]

import pathlib
import colour

import numpy as np

from PIL import Image

from ... import config
from ...constants import *
from ...mobject.mobject import Mobject
from ...mobject.shape_matchers import SurroundingRectangle
from ...utils.bezier import interpolate
from ...utils.color import color_to_int_rgb, WHITE
from ...utils.images import get_full_raster_image_path
from manim.constants import QUALITIES, DEFAULT_QUALITY


class AbstractImageMobject(Mobject):
    """
    Automatically filters out black pixels

    Parameters
    ----------
    scale_to_resolution : :class:`int`
        At this resolution the image is placed pixel by pixel onto the screen, so it will look the sharpest and best.
        This is a custom parameter of ImageMobject so that rendering a scene with e.g. the ``--quality low`` or ``--quality medium`` flag for faster rendering won't effect the position of the image on the screen.
    """

    def __init__(self, scale_to_resolution, pixel_array_dtype="uint8", **kwargs):
        self.pixel_array_dtype = pixel_array_dtype
        self.scale_to_resolution = scale_to_resolution
        Mobject.__init__(self, **kwargs)

    def get_pixel_array(self):
        raise NotImplementedError()

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
        if self.scale_to_resolution:
            self.height = h / self.scale_to_resolution * config["frame_height"]
        else:
            self.height = 3  ## this is the case for ImageMobjectFromCamera
        self.stretch_to_fit_height(self.height)
        self.stretch_to_fit_width(self.height * w / h)


class ImageMobject(AbstractImageMobject):
    """Displays an Image from a numpy array or a file.

    Parameters
    ----------
    scale_to_resolution : :class:`int`
        At this resolution the image is placed pixel by pixel onto the screen, so it will look the sharpest and best.
        This is a custom parameter of ImageMobject so that rendering a scene with e.g. the ``--quality low`` or ``--quality medium`` flag for faster rendering won't effect the position of the image on the screen.


    Example
    -------
    .. manim:: ImageFromArray
        :save_last_frame:

        class ImageFromArray(Scene):
            def construct(self):
                image = ImageMobject(np.uint8([[0, 100, 30, 200],
                                               [255, 0, 5, 33]]))
                image.set_height(7)
                self.add(image)

    """

    def __init__(
        self,
        filename_or_array,
        scale_to_resolution=QUALITIES[DEFAULT_QUALITY]["pixel_height"],
        invert=False,
        image_mode="RGBA",
        **kwargs,
    ):
        self.fill_opacity = 1
        self.stroke_opacity = 1
        self.invert = invert
        self.image_mode = image_mode
        if isinstance(filename_or_array, (str, pathlib.PurePath)):
            path = get_full_raster_image_path(filename_or_array)
            image = Image.open(path).convert(self.image_mode)
            self.pixel_array = np.array(image)
            self.path = path
        else:
            self.pixel_array = np.array(filename_or_array)
        self.pixel_array_dtype = kwargs.get("pixel_array_dtype", "uint8")
        self.change_to_rgba_array()
        if self.invert:
            self.pixel_array[:, :, :3] = 255 - self.pixel_array[:, :, :3]
        AbstractImageMobject.__init__(self, scale_to_resolution, **kwargs)

    def change_to_rgba_array(self):
        """Converts an RGB array into RGBA with the alpha value opacity maxed."""
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
        """A simple getter method."""
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
        """Sets the image's opacity.

        Parameters
        ----------
        alpha : float
            The alpha value of the object, 1 being opaque and 0 being
            transparent.
        """
        self.pixel_array[:, :, 3] = int(255 * alpha)
        self.fill_opacity = alpha
        self.stroke_opacity = alpha
        return self

    def fade(self, darkness=0.5, family=True):
        """Sets the image's opacity using a 1 - alpha relationship.

        Parameters
        ----------
        darkness : float
            The alpha value of the object, 1 being transparent and 0 being
            opaque.
        family : Boolean
            Whether the submobjects of the ImageMobject should be affected.
        """
        self.set_opacity(1 - darkness)
        super().fade(darkness, family)
        return self

    def interpolate_color(self, mobject1, mobject2, alpha):
        """Interpolates an array of pixel color values into another array of
        equal size.

        Parameters
        ----------
        mobject1 : ImageMobject
            The ImageMobject to tranform from.

        mobject1 : ImageMobject

            The ImageMobject to tranform into.
        alpha : float
            Used to track the lerp relationship. Not opacity related.
        """
        assert mobject1.pixel_array.shape == mobject2.pixel_array.shape, (
            f"Mobject pixel array shapes incompatible for interpolation.\n"
            f"Mobject 1 ({mobject1}) : {mobject1.pixel_array.shape}\n"
            f"Mobject 2 ({mobject2}) : {mobject2.pixel_array.shape}"
        )
        self.fill_opacity = interpolate(
            mobject1.fill_opacity, mobject2.fill_opacity, alpha
        )
        self.stroke_opacity = interpolate(
            mobject1.stroke_opacity, mobject2.stroke_opacity, alpha
        )
        self.pixel_array = interpolate(
            mobject1.pixel_array, mobject2.pixel_array, alpha
        ).astype(self.pixel_array_dtype)

    def get_style(self):
        return {
            "fill_color": colour.rgb2hex(self.color.get_rgb()),
            "fill_opacity": self.fill_opacity,
        }


# TODO, add the ability to have the dimensions/orientation of this
# mobject more strongly tied to the frame of the camera it contains,
# in the case where that's a MovingCamera


class ImageMobjectFromCamera(AbstractImageMobject):
    def __init__(self, camera, default_display_frame_config=None, **kwargs):
        self.camera = camera
        if default_display_frame_config is None:
            default_display_frame_config = {
                "stroke_width": 3,
                "stroke_color": WHITE,
                "buff": 0,
            }
        self.default_display_frame_config = default_display_frame_config
        self.pixel_array = self.camera.pixel_array
        AbstractImageMobject.__init__(self, scale_to_resolution=False, **kwargs)

    # TODO: Get rid of this.
    def get_pixel_array(self):
        self.pixel_array = self.camera.pixel_array
        return self.pixel_array

    def add_display_frame(self, **kwargs):
        config = dict(self.default_display_frame_config)
        config.update(kwargs)
        self.display_frame = SurroundingRectangle(self, **config)
        self.add(self.display_frame)
        return self

    def interpolate_color(self, mobject1, mobject2, alpha):
        assert mobject1.pixel_array.shape == mobject2.pixel_array.shape, (
            f"Mobject pixel array shapes incompatible for interpolation.\n"
            f"Mobject 1 ({mobject1}) : {mobject1.pixel_array.shape}\n"
            f"Mobject 2 ({mobject2}) : {mobject2.pixel_array.shape}"
        )
        self.pixel_array = interpolate(
            mobject1.pixel_array, mobject2.pixel_array, alpha
        ).astype(self.pixel_array_dtype)
