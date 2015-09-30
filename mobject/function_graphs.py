import numpy as np
import itertools as it

from mobject import Mobject, Mobject1D, Mobject2D, CompoundMobject
from image_mobject import tex_mobject
from constants import *
from helpers import *

class FunctionGraph(Mobject1D):
    DEFAULT_CONFIG = {
        "color" : "lightblue",
        "x_min" : -10,
        "x_max" : 10,
        "spacial_radius" : SPACE_WIDTH,
    }
    def __init__(self, function, **kwargs):
        digest_config(self, FunctionGraph, kwargs, locals())
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        numerical_radius = (self.x_max - self.x_min)/2
        numerical_center = (self.x_max + self.x_min)/2
        ratio = numerical_radius / self.spacial_radius
        epsilon = self.epsilon * ratio
        self.add_points([
            np.array([(x-numerical_center)/ratio, self.function(x), 0])
            for x in np.arange(self.x_min, self.x_max, self.epsilon)
        ])


class ParametricFunction(Mobject):
    DEFAULT_CONFIG = {
        "color" : "white",
        "dim" : 1,
        "expected_measure" : 10.0,
        "density" : None
    }
    def __init__(self, function, **kwargs):
        digest_config(self, ParametricFunction, kwargs, locals())
        if self.density:
            self.epsilon = 1.0 / self.density
        elif self.dim == 1:
            self.epsilon = 1.0 / self.expected_measure / DEFAULT_POINT_DENSITY_1D
        else:
            self.epsilon = 1.0 / np.sqrt(self.expected_measure) / DEFAULT_POINT_DENSITY_2D
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
    DEFAULT_CONFIG = {
        "color" : "green",
        "radius" : max(SPACE_HEIGHT, SPACE_WIDTH), 
        "interval_size" : 1.0,
        "subinterval_size" : 0.5,
    }
    def __init__(self, **kwargs):
        digest_config(self, Grid, kwargs)
        Mobject1D.__init__(self, **kwargs)

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
    DEFAULT_CONFIG = {
        "color" : "skyblue",
        "numerical_radius" : SPACE_WIDTH,
        "unit_length_to_spacial_width" : 1,
        "tick_size" : 0.1,
        "tick_frequency" : 0.5,
        "leftmost_tick" : -int(SPACE_WIDTH),
        "number_at_center" : 0,                 
        "numbers_with_elongated_ticks" : [0],
        "longer_tick_multiple" : 2,
    }
    def __init__(self, **kwargs):
        digest_config(self, NumberLine, kwargs)
        self.left_num  = self.number_at_center - self.numerical_radius
        self.right_num = self.number_at_center + self.numerical_radius
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        spacial_radius = self.numerical_radius*self.unit_length_to_spacial_width
        self.add_points([
            (b*x, 0, 0)
            for x in np.arange(0, spacial_radius, self.epsilon)
            for b in [-1, 1]
        ])
        self.index_of_left  = np.argmin(self.points[:,0])
        self.index_of_right = np.argmax(self.points[:,0])
        spacial_tick_frequency = self.tick_frequency*self.unit_length_to_spacial_width
        self.add_points([
            (x, y, 0)
            for num in self.get_tick_numbers()
            for y in np.arange(-self.tick_size, self.tick_size, self.epsilon)
            for x in [self.number_to_point(num)[0]]
        ])
        for number in self.numbers_with_elongated_ticks:
            self.elongate_tick_at(number, self.longer_tick_multiple)
        self.number_of_points_without_numbers = self.get_num_points()

    def get_tick_numbers(self):
        return np.arange(self.leftmost_tick, self.right_num, self.tick_frequency)

    def elongate_tick_at(self, number, multiple = 2):
        x = self.number_to_point(number)[0]
        self.add_points([
            [x, y, 0]
            for y in np.arange(
                -multiple*self.tick_size, 
                multiple*self.tick_size,
                self.epsilon
            )
        ])
        return self

    def number_to_point(self, number):
        return interpolate(
            self.points[self.index_of_left],
            self.points[self.index_of_right],
            float(number-self.left_num)/(self.right_num - self.left_num)
        )

    def point_to_number(self, point):
        return self.number_at_center + point[0]/self.unit_length_to_spacial_width

    def default_numbers_to_display(self):
        return self.get_tick_numbers()[::2]

    def get_vertical_number_offset(self):
        return 4*DOWN*self.tick_size

    def get_number_mobjects(self, *numbers):
        if len(numbers) == 0:
            numbers = self.default_numbers_to_display()
        log_spacing = int(np.log10(self.tick_frequency))
        if log_spacing < 0:
            num_decimal_places = 2-log_spacing
        else:
            num_decimal_places = 1+log_spacing
        result = []
        for number in numbers:
            if number < 0:
                num_string = str(number)[:num_decimal_places+1]
            else:
                num_string = str(number)[:num_decimal_places]
            mob = tex_mobject(num_string)
            vert_scale = 2*self.tick_size/mob.get_height()
            hori_scale = self.tick_frequency*self.unit_length_to_spacial_width/mob.get_width()
            mob.scale(min(vert_scale, hori_scale))
            mob.shift(self.number_to_point(number))
            mob.shift(self.get_vertical_number_offset())
            result.append(mob)
        return result

    def add_numbers(self, *numbers):
        self.add(*self.get_number_mobjects(*numbers))

    def remove_numbers(self):
        self.points = self.points[:self.number_of_points_without_numbers]
        self.rgbs = self.rgbs[:self.number_of_points_without_numbers]

class UnitInterval(NumberLine):
    DEFAULT_CONFIG = {
        "numerical_radius" : 0.5,
        "unit_length_to_spacial_width" : 2*(SPACE_WIDTH-1),
        "tick_frequency" : 0.1,
        "leftmost_tick" : 0,
        "number_at_center" : 0.5,                 
        "numbers_with_elongated_ticks" : [0, 1],
    }
    def __init__(self, **kwargs):
        digest_config(self, UnitInterval, kwargs)
        NumberLine.__init__(self, **kwargs)


class Axes(CompoundMobject):
    def __init__(self, **kwargs):
        x_axis = NumberLine(**kwargs)
        y_axis = NumberLine(**kwargs).rotate(np.pi/2, OUT)
        CompoundMobject.__init__(self, x_axis, y_axis)










