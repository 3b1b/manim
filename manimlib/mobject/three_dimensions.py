from manimlib.constants import *
from manimlib.mobject.types.surface import ParametricSurface
from manimlib.mobject.types.surface import SGroup
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import z_to_vector


# Sphere, cylinder, cube, prism

class Sphere(ParametricSurface):
    CONFIG = {
        "resolution": (100, 50),
        "radius": 1,
        "u_range": (0, TAU),
        "v_range": (0, PI),
    }

    def uv_func(self, u, v):
        return self.radius * np.array([
            np.cos(u) * np.sin(v),
            np.sin(u) * np.sin(v),
            -np.cos(v)
        ])


class Cylinder(ParametricSurface):
    CONFIG = {
        "height": 2,
        "radius": 1,
        "axis": OUT,
        "u_range": (0, TAU),
        "v_range": (-1, 1),
        "resolution": (100, 10),
    }

    def init_points(self):
        super().init_points()
        self.scale(self.radius)
        self.set_depth(self.height, stretch=True)
        self.apply_matrix(z_to_vector(self.axis))
        return self

    def uv_func(self, u, v):
        return [np.cos(u), np.sin(u), v]


class Line3D(Cylinder):
    CONFIG = {
        "width": 0.05,
    }

    def __init__(self, start, end, **kwargs):
        digest_config(self, kwargs)
        axis = end - start
        super().__init__(
            height=get_norm(axis),
            radius=self.width / 2,
            axis=axis
        )


class Disk3D(ParametricSurface):
    CONFIG = {
        "radius": 1,
        "u_range": (0, 1),
        "v_range": (0, TAU),
        "resolution": (1, 24),
    }

    def init_points(self):
        super().init_points()
        self.scale(self.radius)

    def uv_func(self, u, v):
        return [
            u * np.cos(v),
            u * np.sin(v),
            0
        ]


class Square3D(ParametricSurface):
    CONFIG = {
        "side_length": 2,
        "u_range": (-1, 1),
        "v_range": (-1, 1),
        "resolution": (1, 1),
    }

    def init_points(self):
        super().init_points()
        self.scale(self.side_length / 2)

    def uv_func(self, u, v):
        return [u, v, 0]


class Cube(SGroup):
    CONFIG = {
        # "fill_color": BLUE,
        # "fill_opacity": 1,
        # "stroke_width": 1,
        # "stroke_color": BLACK,
        "color": BLUE,
        "opacity": 1,
        "gloss": 0.5,
        "square_resolution": (1, 1),
        "side_length": 2,
    }

    def init_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = Square3D(resolution=self.square_resolution)
            face.shift(OUT)
            face.apply_matrix(z_to_vector(vect))
            self.add(face)
        self.set_height(self.side_length)
        # self.set_color(self.color, self.opacity, self.gloss)


class Prism(Cube):
    CONFIG = {
        "dimensions": [3, 2, 1]
    }

    def init_points(self):
        Cube.init_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)
