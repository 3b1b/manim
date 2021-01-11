import numpy as np
import moderngl
import numbers

from manimlib.constants import GREY_C
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.mobject.geometry import DEFAULT_DOT_RADIUS
from manimlib.utils.iterables import resize_preserving_order


class DotCloud(PMobject):
    CONFIG = {
        "color": GREY_C,
        "opacity": 1,
        "radii": DEFAULT_DOT_RADIUS,
        "shader_folder": "true_dot",
        "render_primitive": moderngl.POINTS,
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('radius', np.float32, (1,)),
            ('color', np.float32, (4,)),
        ],
    }

    def __init__(self, points=None, **kwargs):
        super().__init__(**kwargs)
        if points:
            self.set_points(points)

    def init_data(self):
        self.data = {
            "points": np.zeros((1, 3)),
            "rgbas": np.zeros((1, 4)),
            "radii": np.zeros((1, 1))
        }
        self.set_radii(self.radii)

    def set_points_by_grid(self, n_rows, n_cols, height=None, width=None):
        # TODO, add buff/hbuff/vbuff args...
        new_points = np.zeros((n_rows * n_cols, 3))
        new_points[:, 0] = np.tile(range(n_cols), n_rows)
        new_points[:, 1] = np.repeat(range(n_rows), n_cols)
        new_points[:, 2] = 0
        self.set_points(new_points)

        radius = self.data["radii"].max()
        if height is None:
            height = n_rows * 3 * radius
        if width is None:
            width = n_cols * 3 * radius

        self.set_height(height, stretch=True)
        self.set_width(width, stretch=True)
        self.center()

        return self

    def set_radii(self, radii):
        if not isinstance(radii, numbers.Number):
            radii = resize_preserving_order(radii, self.get_num_points())
        self.data["radii"][:, 0] = radii
        return self

    def scale(self, scale_factor, scale_radii=True, **kwargs):
        super().scale(scale_factor, **kwargs)
        if scale_radii:
            self.data["radii"] *= scale_factor
        return self

    def get_shader_data(self):
        data = super().get_shader_data()
        data["radius"] = self.data["radii"]
        data["color"] = self.data["rgbas"]
        return data
