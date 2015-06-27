import numpy as np
import itertools as it

from mobject import Mobject, Mobject1D, Mobject2D, CompoundMobject
from constants import *
from helpers import *

class FunctionGraph(Mobject1D):
    DEFAULT_COLOR = "lightblue"
    def __init__(self, function, x_range = [-10, 10], *args, **kwargs):
        self.function = function
        self.x_min = x_range[0] / SPACE_WIDTH
        self.x_max = x_range[1] / SPACE_WIDTH
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        scale_factor = 2.0 * SPACE_WIDTH / (self.x_max - self.x_min)
        self.epsilon /= scale_factor
        self.add_points([
            np.array([x, self.function(x), 0])
            for x in np.arange(self.x_min, self.x_max, self.epsilon)
        ])
        self.scale(scale_factor)


class ParametricFunction(Mobject):
    DEFAULT_COLOR = "white"
    def __init__(self, 
                 function, 
                 dim = 1, 
                 expected_measure = 10.0, 
                 density = None,
                 *args, 
                 **kwargs):
        self.function = function
        self.dim = dim
        self.expected_measure = expected_measure
        if density:
            self.epsilon = 1.0 / density
        elif self.dim == 1:
            self.epsilon = 1.0 / expected_measure / DEFAULT_POINT_DENSITY_1D
        else:
            self.epsilon = 1.0 / np.sqrt(expected_measure) / DEFAULT_POINT_DENSITY_2D
        Mobject.__init__(self, *args, **kwargs)

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

class Grid(Mobject1D):
    DEFAULT_COLOR = "green"
    def __init__(self, 
                 radius = max(SPACE_HEIGHT, SPACE_WIDTH), 
                 interval_size = 1.0,
                 subinterval_size = 0.5,
                 *args, **kwargs):
        self.radius = radius
        self.interval_size = interval_size
        self.subinterval_size = subinterval_size
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            (sgns[0] * x, sgns[1] * y, 0)
            for beta in np.arange(0, self.radius, self.interval_size)
            for alpha in np.arange(0, self.radius, self.epsilon)
            for sgns in it.product((-1, 1), (-1, 1))
            for x, y in [(alpha, beta), (beta, alpha)]
        ])
        if self.subinterval_size:
            si = self.subinterval_size
            color = Color(self.color)
            color.set_rgb([x/2 for x in color.get_rgb()])
            self.add_points([
                (sgns[0] * x, sgns[1] * y, 0)
                for beta in np.arange(0, self.radius, si)
                if abs(beta % self.interval_size) > self.epsilon
                for alpha in np.arange(0, self.radius, self.epsilon)
                for sgns in it.product((-1, 1), (-1, 1))
                for x, y in [(alpha, beta), (beta, alpha)]
            ], color = color)

class NumberLine(Mobject1D):
    def __init__(self, 
                 radius = SPACE_WIDTH,
                 interval_size = 0.5, tick_size = 0.1, 
                 *args, **kwargs):
        self.radius = int(radius) + 1
        self.interval_size = interval_size
        self.tick_size = tick_size
        Mobject1D.__init__(self, *args, **kwargs)

    def generate_points(self):
        self.add_points([
            (x, 0, 0)
            for x in np.arange(-self.radius, self.radius, self.epsilon)
        ])
        self.add_points([
            (0, y, 0)
            for y in np.arange(-2*self.tick_size, 2*self.tick_size, self.epsilon)
        ])
        self.add_points([
            (x, y, 0)
            for x in np.arange(-self.radius, self.radius, self.interval_size)
            for y in np.arange(-self.tick_size, self.tick_size, self.epsilon)
        ])

class Axes(CompoundMobject):
    def __init__(self, *args, **kwargs):
        x_axis = NumberLine(*args, **kwargs)
        y_axis = NumberLine(*args, **kwargs).rotate(np.pi/2, OUT)
        CompoundMobject.__init__(self, x_axis, y_axis)










