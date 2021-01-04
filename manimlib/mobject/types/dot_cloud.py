import numpy as np
import moderngl
import numbers

from manimlib.constants import GREY_C
from manimlib.constants import ORIGIN
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.mobject.geometry import DEFAULT_DOT_RADIUS
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import stretch_array_to_length


class DotCloud(PMobject):
    CONFIG = {
        "color": GREY_C,
        "opacity": 1,
        "vert_shader_file": "true_dot_vert.glsl",
        "geom_shader_file": "true_dot_geom.glsl",
        "frag_shader_file": "true_dot_frag.glsl",
        "render_primitive": moderngl.POINTS,
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('radius', np.float32, (1,)),
            ('color', np.float32, (4,)),
        ],
    }

    def __init__(self, points=[[ORIGIN]], radii=DEFAULT_DOT_RADIUS, **kwargs):
        super().__init__(**kwargs)
        self.rgbas = np.zeros((len(points), 4))
        self.radii = np.full((len(points), 1), radii)
        self.points = np.array(points)
        self.set_color(self.color)

    def set_points(self, points):
        super().set_points(points)
        self.radii = stretch_array_to_length(self.radii, len(points))
        return self

    def set_points_by_grid(self, n_rows, n_cols, height=None, width=None):
        new_points = np.zeros((n_rows * n_cols, 3))
        new_points[:, 0] = np.tile(range(n_cols), n_rows)
        new_points[:, 1] = np.repeat(range(n_rows), n_cols)
        new_points[:, 2] = 0
        self.set_points(new_points)

        radius = self.radii[0]
        if height is None:
            height = n_rows * 3 * radius
        if width is None:
            width = n_cols * 3 * radius

        self.set_height(height, stretch=True)
        self.set_width(width, stretch=True)
        self.center()

        return self

    def set_radii(self, radii):
        if isinstance(radii, numbers.Number):
            self.radii[:] = radii
        else:
            self.radii = stretch_array_to_length(radii, len(self.points))
        return self

    def scale(self, scale_factor, scale_radii=True, **kwargs):
        super().scale(scale_factor, **kwargs)
        if scale_radii:
            self.radii *= scale_factor
        return self

    def interpolate(self, mobject1, mobject2, alpha, *args, **kwargs):
        super().interpolate(mobject1, mobject2, alpha, *args, **kwargs)
        self.radii = interpolate(mobject1.radii, mobject2.radii, alpha)
        return self

    def get_shader_data(self):
        data = self.get_blank_shader_data_array(len(self.points))
        data["point"] = self.points
        data["radius"] = self.radii.reshape((len(self.radii), 1))
        data["color"] = self.rgbas
        return data
