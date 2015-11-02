from helpers import *

from helpers import *

from mobject import Mobject, Mobject1D, Mobject


class FunctionGraph(Mobject1D):
    DEFAULT_CONFIG = {
        "color" : BLUE,
        "x_min" : -10,
        "x_max" : 10,
        "spatial_radius" : SPACE_WIDTH,
    }
    def __init__(self, function, **kwargs):
        self.function = function
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        numerical_radius = (self.x_max - self.x_min)/2
        numerical_center = (self.x_max + self.x_min)/2
        ratio = numerical_radius / self.spatial_radius
        epsilon = self.epsilon * ratio
        self.add_points([
            np.array([(x-numerical_center)/ratio, self.function(x), 0])
            for x in np.arange(self.x_min, self.x_max, self.epsilon)
        ])


class ParametricFunction(Mobject):
    DEFAULT_CONFIG = {
        "color"            : WHITE,
        "dim"              : 1,
        "expected_measure" : 10.0,
        "density"          : None
    }
    def __init__(self, function, **kwargs):
        self.function = function
        if self.density:
            self.epsilon = 1.0 / self.density
        elif self.dim == 1:
            self.epsilon = 1.0 / self.expected_measure / DEFAULT_POINT_DENSITY_1D
        else:
            self.epsilon = 1.0 / np.sqrt(self.expected_measure) / DEFAULT_POINT_DENSITY_2D
        Mobject.__init__(self, **kwargs)

    def generate_points(self):
        if self.dim == 1:
            self.add_points([
                self.function(t)
                for t in np.arange(-1, 1, self.epsilon)
            ])
        if self.dim == 2:
            self.add_points([
                self.function(s, t)
                for t in np.arange(-1, 1, self.epsilon)
                for s in np.arange(-1, 1, self.epsilon)
            ])


class Axes(Mobject):
    def __init__(self, **kwargs):
        x_axis = NumberLine(**kwargs)
        y_axis = NumberLine(**kwargs).rotate(np.pi/2, OUT)
        Mobject.__init__(self, x_axis, y_axis)


        