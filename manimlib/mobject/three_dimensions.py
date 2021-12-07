import math

from manimlib.constants import *
from manimlib.mobject.types.surface import Surface
from manimlib.mobject.types.surface import SGroup
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import Square
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import z_to_vector
from manimlib.utils.space_ops import compass_directions


class SurfaceMesh(VGroup):
    CONFIG = {
        "resolution": (21, 11),
        "stroke_width": 1,
        "normal_nudge": 1e-2,
        "depth_test": True,
        "flat_stroke": False,
    }

    def __init__(self, uv_surface, **kwargs):
        if not isinstance(uv_surface, Surface):
            raise Exception("uv_surface must be of type Surface")
        self.uv_surface = uv_surface
        super().__init__(**kwargs)

    def init_points(self):
        uv_surface = self.uv_surface

        full_nu, full_nv = uv_surface.resolution
        part_nu, part_nv = self.resolution
        # 'indices' are treated as floats. Later, there will be
        # an interpolation between the floor and ceiling of these
        # indices
        u_indices = np.linspace(0, full_nu - 1, part_nu)
        v_indices = np.linspace(0, full_nv - 1, part_nv)

        points, du_points, dv_points = uv_surface.get_surface_points_and_nudged_points()
        normals = uv_surface.get_unit_normals()
        nudge = self.normal_nudge
        nudged_points = points + nudge * normals

        for ui in u_indices:
            path = VMobject()
            low_ui = full_nv * int(math.floor(ui))
            high_ui = full_nv * int(math.ceil(ui))
            path.set_points_smoothly(interpolate(
                nudged_points[low_ui:low_ui + full_nv],
                nudged_points[high_ui:high_ui + full_nv],
                ui % 1
            ))
            self.add(path)
        for vi in v_indices:
            path = VMobject()
            path.set_points_smoothly(interpolate(
                nudged_points[int(math.floor(vi))::full_nv],
                nudged_points[int(math.ceil(vi))::full_nv],
                vi % 1
            ))
            self.add(path)


# 3D shapes

class Sphere(Surface):
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


class Torus(Surface):
    CONFIG = {
        "u_range": (0, TAU),
        "v_range": (0, TAU),
        "r1": 3,
        "r2": 1,
    }

    def uv_func(self, u, v):
        P = np.array([math.cos(u), math.sin(u), 0])
        return (self.r1 - self.r2 * math.cos(v)) * P - math.sin(v) * OUT


class Cylinder(Surface):
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


class Disk3D(Surface):
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


class Square3D(Surface):
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
        "color": BLUE,
        "opacity": 1,
        "gloss": 0.5,
        "square_resolution": (2, 2),
        "side_length": 2,
        "square_class": Square3D,
    }

    def init_points(self):
        face = Square3D(
            resolution=self.square_resolution,
            side_length=self.side_length,
        )
        self.add(*self.square_to_cube_faces(face))

    @staticmethod
    def square_to_cube_faces(square):
        radius = square.get_height() / 2
        square.move_to(radius * OUT)
        result = [square]
        result.extend([
            square.copy().rotate(PI / 2, axis=vect, about_point=ORIGIN)
            for vect in compass_directions(4)
        ])
        result.append(square.copy().rotate(PI, RIGHT, about_point=ORIGIN))
        return result

    def _get_face(self):
        return Square3D(resolution=self.square_resolution)


class VCube(VGroup):
    CONFIG = {
        "fill_color": BLUE_D,
        "fill_opacity": 1,
        "stroke_width": 0,
        "gloss": 0.5,
        "shadow": 0.5,
    }

    def __init__(self, side_length=2, **kwargs):
        super().__init__(**kwargs)
        face = Square(side_length=side_length)
        face.get_triangulation()
        self.add(*Cube.square_to_cube_faces(face))
        self.init_colors()
        self.apply_depth_test()
        self.refresh_unit_normal()


class Prism(Cube):
    CONFIG = {
        "dimensions": [3, 2, 1]
    }

    def init_points(self):
        Cube.init_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)
