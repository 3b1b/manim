from __future__ import absolute_import

from constants import *

from mobject.types.vectorized_mobject import VMobject
from mobject.geometry import Square

from utils.space_ops import z_to_vector

##############


def should_shade_in_3d(mobject):
    return hasattr(mobject, "shade_in_3d") and mobject.shade_in_3d


def shade_in_3d(mobject):
    for submob in mobject.submobject_family():
        submob.shade_in_3d = True


def turn_off_3d_shading(mobject):
    for submob in mobject.submobject_family():
        submob.shade_in_3d = False


class ThreeDMobject(VMobject):
    def __init__(self, *args, **kwargs):
        VMobject.__init__(self, *args, **kwargs)
        shade_in_3d(self)


class Cube(ThreeDMobject):
    CONFIG = {
        "fill_opacity": 0.75,
        "fill_color": BLUE,
        "stroke_width": 0,
        "propagate_style_to_family": True,
        "side_length": 2,
    }

    def generate_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = Square(side_length=self.side_length)
            face.shift(self.side_length * OUT / 2.0)
            face.apply_function(lambda p: np.dot(p, z_to_vector(vect).T))

            self.add(face)


class Prism(Cube):
    CONFIG = {
        "dimensions": [3, 2, 1]
    }

    def generate_points(self):
        Cube.generate_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)
