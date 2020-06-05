import numpy as np
import moderngl

# from PIL import Image

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.color import color_to_rgba


class SurfaceMobject(Mobject):
    CONFIG = {
        "color": GREY,
        "opacity": 1,
        "gloss": 1.0,
        "render_primative": moderngl.TRIANGLES,
        # "render_primative": moderngl.TRIANGLE_STRIP,
        "vert_shader_file": "surface_vert.glsl",
        "frag_shader_file": "surface_frag.glsl",
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('normal', np.float32, (3,)),
            ('color', np.float32, (4,)),
            ('gloss', np.float32, (1,)),
            # ('im_coords', np.float32, (2,)),
        ]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def init_points(self):
        self.points = np.zeros((0, self.dim))
        self.normals = np.zeros((0, self.dim))

    def init_colors(self):
        self.set_color(self.color, self.opacity)

    def set_points(self, points, normals=None):
        self.points = np.array(points)
        if normals is None:
            v01 = points[1:-1] - points[:-2]
            v02 = points[2:] - points[:-2]
            crosses = np.cross(v01, v02)
            crosses[1::2] *= -1  # Because of reversed orientation of every other triangle in the strip
            self.normals = np.vstack([
                crosses,
                crosses[-1:].repeat(2, 0)  # Repeat last entry twice
            ])
        else:
            self.normals = np.array(normals)

    def set_color(self, color, opacity):
        # TODO, allow for multiple colors
        rgba = color_to_rgba(color, opacity)
        self.rgbas = np.array([rgba])

    def apply_function(self, function, **kwargs):
        # Apply it to infinitesimal neighbors to preserve normals
        pass

    def rotate(self, axis, angle, **kwargs):
        # Account for normals
        pass

    def stretch(self, factor, dim, **kwargs):
        # Account for normals
        pass

    def get_shader_data(self):
        data = self.get_blank_shader_data_array(len(self.points))
        data["point"] = self.points
        data["normal"] = self.normals
        data["color"] = self.rgbas
        data["gloss"] = self.gloss
        return data
