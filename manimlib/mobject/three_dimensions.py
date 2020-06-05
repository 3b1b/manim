from manimlib.constants import *
from manimlib.mobject.geometry import Square
from manimlib.mobject.types.surface_mobject import ParametricSurface
from manimlib.mobject.types.vectorized_mobject import VGroup


# Sphere, cylinder, cube, prism

class Sphere(ParametricSurface):
    CONFIG = {
        "resolution": (96, 48),
        "radius": 1,
        "u_range": (0, TAU),
        "v_range": (0, PI),
    }

    def func(self, u, v):
        return self.radius * np.array([
            np.cos(u) * np.sin(v),
            np.sin(u) * np.sin(v),
            np.cos(v)
        ])


class Cube(VGroup):
    CONFIG = {
        "fill_opacity": 0.75,
        "fill_color": BLUE,
        "stroke_width": 0,
        "side_length": 2,
    }

    def init_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = Square(
                side_length=self.side_length,
                shade_in_3d=True,
            )
            face.flip()
            face.shift(self.side_length * OUT / 2.0)
            face.apply_matrix(z_to_vector(vect))

            self.add(face)


class Prism(Cube):
    CONFIG = {
        "dimensions": [3, 2, 1]
    }

    def init_points(self):
        Cube.init_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)
