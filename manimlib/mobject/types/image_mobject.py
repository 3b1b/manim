import numpy as np

from PIL import Image

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.images import get_full_raster_image_path
from manimlib.utils.iterables import listify


class ImageMobject(Mobject):
    CONFIG = {
        "height": 4,
        "opacity": 1,
        "vert_shader_file": "image_vert.glsl",
        "frag_shader_file": "image_frag.glsl",
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('im_coords', np.float32, (2,)),
            ('opacity', np.float32, (1,)),
        ]
    }

    def __init__(self, filename, **kwargs):
        path = get_full_raster_image_path(filename)
        self.image = Image.open(path)
        self.texture_paths = {"Texture": path}
        Mobject.__init__(self, **kwargs)

    def init_points(self):
        self.points = np.array([UL, DL, UR, DR])
        self.im_coords = np.array([(0, 0), (0, 1), (1, 0), (1, 1)])
        size = self.image.size
        self.set_width(2 * size[0] / size[1], stretch=True)
        self.set_height(self.height)

    def init_colors(self):
        self.set_opacity(self.opacity)

    def set_opacity(self, alpha, family=True):
        opacity = listify(alpha)
        diff = 4 - len(opacity)
        opacity += [opacity[-1]] * diff
        self.opacity = np.array(opacity).reshape((4, 1))

        if family:
            for sm in self.submobjects:
                sm.set_opacity(alpha)

    def fade(self, darkness=0.5, family=True):
        self.set_opacity(1 - darkness, family)
        return self

    def interpolate_color(self, mobject1, mobject2, alpha):
        # TODO, transition between actual images?
        self.opacity = interpolate(
            mobject1.opacity, mobject2.opacity, alpha
        )

    def point_to_rgb(self, point):
        x0, y0 = self.get_corner(UL)[:2]
        x1, y1 = self.get_corner(DR)[:2]
        x_alpha = inverse_interpolate(x0, x1, point[0])
        y_alpha = inverse_interpolate(y0, y1, point[1])
        if not (0 <= x_alpha <= 1) and (0 <= y_alpha <= 1):
            # TODO, raise smarter exception
            raise Exception("Cannot sample color from outside an image")

        pw, ph = self.image.size
        rgb = self.image.getpixel((
            int((pw - 1) * x_alpha),
            int((ph - 1) * y_alpha),
        ))
        return np.array(rgb) / 255

    def get_shader_data(self):
        data = self.get_blank_shader_data_array(len(self.points))
        data["point"] = self.points
        data["im_coords"] = self.im_coords
        data["opacity"] = self.opacity
        return data
