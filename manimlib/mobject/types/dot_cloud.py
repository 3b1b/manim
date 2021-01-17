import numpy as np
import moderngl
import numbers

from manimlib.constants import GREY_C
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.utils.iterables import resize_preserving_order


DEFAULT_DOT_CLOUD_RADIUS = 0.05
DEFAULT_GRID_HEIGHT = 6
DEFAULT_BUFF_RATIO = 0.5


class DotCloud(PMobject):
    CONFIG = {
        "color": GREY_C,
        "opacity": 1,
        "radii": DEFAULT_DOT_CLOUD_RADIUS,
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
        if points is not None:
            self.set_points(points)

    def init_data(self):
        super().init_data()
        self.data["radii"] = np.zeros((1, 1))
        self.set_radii(self.radii)

    def to_grid(self, n_rows, n_cols, n_layers=1,
                buff_ratio=None,
                h_buff_ratio=1.0,
                v_buff_ratio=1.0,
                d_buff_ratio=1.0,
                height=DEFAULT_GRID_HEIGHT,
                ):
        n_points = n_rows * n_cols * n_layers
        points = np.repeat(range(n_points), 3, axis=0).reshape((n_points, 3))
        points[:, 0] = points[:, 0] % n_cols
        points[:, 1] = (points[:, 1] // n_cols) % n_rows
        points[:, 2] = points[:, 2] // (n_rows * n_cols)
        self.set_points(points.astype(float))

        if buff_ratio is not None:
            v_buff_ratio = buff_ratio
            h_buff_ratio = buff_ratio
            d_buff_ratio = buff_ratio

        radius = self.get_radius()
        ns = [n_cols, n_rows, n_layers]
        brs = [h_buff_ratio, v_buff_ratio, d_buff_ratio]
        for n, br, dim in zip(ns, brs, range(3)):
            self.rescale_to_fit(2 * radius * (1 + br) * (n - 1), dim, stretch=True)
        if height is not None:
            self.set_height(height)
        self.center()
        return self

    def set_radii(self, radii):
        if not isinstance(radii, numbers.Number):
            radii = resize_preserving_order(radii, len(self.data["radii"]))
        self.data["radii"][:] = radii
        return self

    def get_radii(self):
        return self.data["radii"]

    def get_radius(self):
        return self.get_radii().max()

    def scale(self, scale_factor, scale_radii=True, **kwargs):
        super().scale(scale_factor, **kwargs)
        if scale_radii:
            self.set_radii(scale_factor * self.get_radii())
        return self

    def style_for_3d(self, gloss=0.5, shadow=0.2):
        self.set_gloss(gloss)
        self.set_shadow(shadow)
        self.apply_depth_test()
        return self

    def get_shader_data(self):
        shader_data = super().get_shader_data()
        self.read_data_to_shader(shader_data, "radius", "radii")
        self.read_data_to_shader(shader_data, "color", "rgbas")
        return shader_data
