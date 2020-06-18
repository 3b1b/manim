import math

from manimlib.constants import *
from manimlib.mobject.types.surface import ParametricSurface
from manimlib.mobject.types.surface import SGroup
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import z_to_vector


class SurfaceMesh(VGroup):
    CONFIG = {
        "resolution": (21, 21),
        "stroke_width": 1,
        "normal_nudge": 1e-2,
        "depth_test": True,
    }

    def __init__(self, uv_surface, **kwargs):
        if not isinstance(uv_surface, ParametricSurface):
            raise Exception("uv_surface must be of type ParametricSurface")
        self.uv_surface = uv_surface
        super().__init__(**kwargs)

    def init_points(self):
        uv_surface = self.uv_surface

        full_nu, full_nv = uv_surface.resolution
        part_nu, part_nv = self.resolution
        u_indices = np.linspace(0, full_nu, part_nu).astype(int)
        v_indices = np.linspace(0, full_nv, part_nv).astype(int)

        points, du_points, dv_points = uv_surface.get_surface_points_and_nudged_points()
        normals = uv_surface.get_unit_normals()
        nudge = 1e-2
        nudged_points = points + nudge * normals

        for ui in u_indices:
            path = VMobject()
            full_ui = full_nv * ui
            path.set_points_smoothly(nudged_points[full_ui:full_ui + full_nv])
            self.add(path)
        for vi in v_indices:
            path = VMobject()
            path.set_points_smoothly(nudged_points[vi::full_nv])
            self.add(path)


# Sphere, cylinder, cube, prism

class ArglessSurface(ParametricSurface):
    def __init__(self, **kwargs):
        super().__init__(self.uv_func, **kwargs)

    def uv_func(self, u, v):
        # To be implemented by a subclass
        return [u, v, 0]


class Sphere(ArglessSurface):
    CONFIG = {
        "resolution": (101, 51),
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


class Torus(ArglessSurface):
    CONFIG = {
        "u_range": (0, TAU),
        "v_range": (0, TAU),
        "r1": 3,
        "r2": 1,
    }

    def uv_func(self, u, v):
        P = np.array([math.cos(u), math.sin(u), 0])
        return (self.r1 - self.r2 * math.cos(v)) * P - math.sin(v) * OUT


class Cylinder(ArglessSurface):
    CONFIG = {
        "height": 2,
        "radius": 1,
        "axis": OUT,
        "u_range": (0, TAU),
        "v_range": (-1, 1),
        "resolution": (101, 11),
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
        "resolution": (21, 25)
    }

    def __init__(self, start, end, **kwargs):
        digest_config(self, kwargs)
        axis = end - start
        super().__init__(
            height=get_norm(axis),
            radius=self.width / 2,
            axis=axis
        )
        self.shift((start + end) / 2)


class Disk3D(ArglessSurface):
    CONFIG = {
        "radius": 1,
        "u_range": (0, 1),
        "v_range": (0, TAU),
        "resolution": (2, 25),
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


class Square3D(ArglessSurface):
    CONFIG = {
        "side_length": 2,
        "u_range": (-1, 1),
        "v_range": (-1, 1),
        "resolution": (2, 2),
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
        "square_resolution": (2, 2),
        "side_length": 2,
    }

    def init_points(self):
        for vect in [OUT, RIGHT, UP, LEFT, DOWN, IN]:
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
