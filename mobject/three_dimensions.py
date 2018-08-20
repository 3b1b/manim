

from constants import *

from mobject.types.vectorized_mobject import VMobject
from mobject.types.vectorized_mobject import VGroup
from mobject.geometry import Square

from utils.config_ops import digest_config
from utils.iterables import tuplify
from utils.space_ops import z_to_vector
from utils.space_ops import get_unit_normal

##############


class ThreeDVMobject(VMobject):
    CONFIG = {}

    def __init__(self, vmobject=None, **kwargs):
        VMobject.__init__(self, **kwargs)
        if vmobject is not None:
            self.points = np.array(vmobject.points)
            self.match_style(vmobject, family=False)
            self.submobjects = [
                ThreeDVMobject(submob, **kwargs)
                for submob in vmobject.submobjects
            ]

    def get_gradient_start_and_end_points(self):
        return self.get_start_corner(), self.get_end_corner()

    def get_start_corner_index(self):
        return 0

    def get_end_corner_index(self):
        return ((len(self.points) - 1) // 6) * 3
        # return ((len(self.points) - 1) // 12) * 3

    def get_start_corner(self):
        if self.get_num_points() == 0:
            return np.array(ORIGIN)
        return self.points[self.get_start_corner_index()]

    def get_end_corner(self):
        if self.get_num_points() == 0:
            return np.array(ORIGIN)
        return self.points[self.get_end_corner_index()]

    def get_unit_normal(self, point_index):
        n_points = self.get_num_points()
        if self.get_num_points() == 0:
            return np.array(ORIGIN)
        i = point_index
        im1 = i - 1 if i > 0 else (n_points - 2)
        ip1 = i + 1 if i < (n_points - 1) else 1
        return get_unit_normal(
            self.points[ip1] - self.points[i],
            self.points[im1] - self.points[i],
        )

    def get_start_corner_unit_normal(self):
        return self.get_unit_normal(
            self.get_start_corner_index()
        )

    def get_end_corner_unit_normal(self):
        return self.get_unit_normal(
            self.get_end_corner_index()
        )


class ParametricSurface(VGroup):
    CONFIG = {
        "u_min": 0,
        "u_max": 1,
        "v_min": 0,
        "v_max": 1,
        "resolution": 32,
        "surface_piece_config": {},
        "fill_color": BLUE_D,
        "fill_opacity": 1.0,
        "checkerboard_colors": [BLUE_D, BLUE_E],
        "stroke_color": LIGHT_GREY,
        "stroke_width": 0.5,
        "should_make_jagged": False,
    }

    def __init__(self, func, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.setup_in_uv_space()
        self.apply_function(lambda p: func(p[0], p[1]))
        if self.should_make_jagged:
            self.make_jagged()

    def setup_in_uv_space(self):
        res = tuplify(self.resolution)
        if len(res) == 1:
            u_res = v_res = res
        else:
            u_res, v_res = res
        u_min = self.u_min
        u_max = self.u_max
        v_min = self.v_min
        v_max = self.v_max

        u_values = np.linspace(u_min, u_max, u_res + 1)
        v_values = np.linspace(v_min, v_max, v_res + 1)
        faces = VGroup()
        for i in range(u_res):
            for j in range(v_res):
                u1, u2 = u_values[i:i + 2]
                v1, v2 = v_values[j:j + 2]
                face = ThreeDVMobject()
                face.set_points_as_corners([
                    [u1, v1, 0],
                    [u2, v1, 0],
                    [u2, v2, 0],
                    [u1, v2, 0],
                    [u1, v1, 0],
                ])
                faces.add(face)
                face.u_index = i
                face.v_index = j
        faces.set_fill(
            color=self.fill_color,
            opacity=self.fill_opacity
        )
        faces.set_stroke(
            color=self.stroke_color,
            width=self.stroke_width,
            opacity=self.stroke_opacity,
        )
        self.add(*faces)
        if self.checkerboard_colors:
            self.set_fill_by_checkerboard(*self.checkerboard_colors)

    def set_fill_by_checkerboard(self, *colors, opacity=None):
        n_colors = len(colors)
        for face in self:
            c_index = (face.u_index + face.v_index) % n_colors
            face.set_fill(colors[c_index], opacity=opacity)


# Specific shapes


class Sphere(ParametricSurface):
    CONFIG = {
        "resolution": (12, 24),
        "radius": 3,
        "u_min": 0.001,
        "u_max": PI - 0.001,
        "v_min": 0,
        "v_max": TAU,
    }

    def __init__(self, **kwargs):
        ParametricSurface.__init__(
            self, self.func, **kwargs
        )
        self.scale(self.radius)

    def func(self, u, v):
        return np.array([
            np.cos(v) * np.sin(u),
            np.sin(v) * np.sin(u),
            np.cos(u)
        ])


class Cube(VGroup):
    CONFIG = {
        "fill_opacity": 0.75,
        "fill_color": BLUE,
        "stroke_width": 0,
        "propagate_style_to_family": True,
        "side_length": 2,
    }

    def generate_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = ThreeDVMobject(
                Square(side_length=self.side_length)
            )
            face.make_jagged()
            face.flip()
            face.shift(self.side_length * OUT / 2.0)
            face.apply_matrix(z_to_vector(vect))

            self.add(face)


class Prism(Cube):
    CONFIG = {
        "dimensions": [3, 2, 1]
    }

    def generate_points(self):
        Cube.generate_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)
