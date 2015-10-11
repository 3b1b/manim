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
        "spatial_radius" : SPACE_WIDTH,
    }
    def __init__(self, function, **kwargs):
        digest_config(self, FunctionGraph, kwargs, locals())
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

class NumberLine(Mobject1D):
    DEFAULT_CONFIG = {
        "color" : "skyblue",
        "numerical_radius" : SPACE_WIDTH,
        "unit_length_to_spatial_width" : 1,
        "tick_size" : 0.1,
        "tick_frequency" : 0.5,
        "leftmost_tick" : None,
        "number_at_center" : 0,                 
        "numbers_with_elongated_ticks" : [0],
        "longer_tick_multiple" : 2,
    }
    def __init__(self, **kwargs):
        digest_config(self, NumberLine, kwargs)
        if self.leftmost_tick is None:
            self.leftmost_tick = -int(self.numerical_radius)
        self.left_num  = self.number_at_center - self.numerical_radius
        self.right_num = self.number_at_center + self.numerical_radius
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        spatial_radius = self.numerical_radius*self.unit_length_to_spatial_width
        self.add_points([
            (b*x, 0, 0)
            for x in np.arange(0, spatial_radius, self.epsilon)
            for b in [-1, 1]
        ])
        self.index_of_left  = np.argmin(self.points[:,0])
        self.index_of_right = np.argmax(self.points[:,0])
        spatial_tick_frequency = self.tick_frequency*self.unit_length_to_spatial_width
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
        return self.number_at_center + point[0]/self.unit_length_to_spatial_width

    def default_numbers_to_display(self):
        return self.get_tick_numbers()[::2]

    def get_vertical_number_offset(self):
        return 4*DOWN*self.tick_size

    def get_number_mobjects(self, *numbers):
        #TODO, handle decimals
        if len(numbers) == 0:
            numbers = self.default_numbers_to_display()
        result = []
        for number in numbers:
            mob = tex_mobject(str(int(number)))
            vert_scale = 2*self.tick_size/mob.get_height()
            hori_scale = self.tick_frequency*self.unit_length_to_spatial_width/mob.get_width()
            mob.scale(min(vert_scale, hori_scale))
            mob.shift(self.number_to_point(number))
            mob.shift(self.get_vertical_number_offset())
            result.append(mob)
        return result

    def add_numbers(self, *numbers):
        self.add(*self.get_number_mobjects(*numbers))
        return self

    def remove_numbers(self):
        self.points = self.points[:self.number_of_points_without_numbers]
        self.rgbs = self.rgbs[:self.number_of_points_without_numbers]
        return self

class UnitInterval(NumberLine):
    DEFAULT_CONFIG = {
        "numerical_radius" : 0.5,
        "unit_length_to_spatial_width" : 2*(SPACE_WIDTH-1),
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


class NumberPlane(Mobject1D):
    DEFAULT_CONFIG = {
        "color" : "skyblue",
        "x_radius" : SPACE_WIDTH,
        "y_radius" : SPACE_HEIGHT,
        "x_unit_to_spatial_width" : 1,
        "y_uint_to_spatial_height" : 1,
        "x_line_frequency" : 1,
        "x_faded_line_frequency" : 0.5,
        "y_line_frequency" : 1,
        "y_faded_line_frequency" : 0.5,
        "fade_factor" : 0.3,
        "number_scale_factor" : 0.25,
        "num_pair_at_center" : np.array((0, 0)),
    }
    def __init__(self, **kwargs):
        digest_config(self, NumberPlane, kwargs)
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        color = self.color
        faded = Color(rgb = self.fade_factor*np.array(color.get_rgb()))
        #Vertical Lines
        freq_color_pairs = [
            (self.x_faded_line_frequency, faded),
            (self.x_line_frequency, color)
        ]
        for freq, color in freq_color_pairs:
            if not freq:
                continue
            self.add_points([
                (sgns[0]*self.x_unit_to_spatial_width*x, sgns[1]*y, 0)
                for x in np.arange(0, self.x_radius, freq)
                for y in np.arange(0, self.y_radius, self.epsilon)
                for sgns in it.product([-1, 1], [-1, 1])
            ], color = color)
        #Horizontal lines
        freq_color_pairs = [
            (self.y_faded_line_frequency, faded),
            (self.y_line_frequency, color)
        ]
        for freq, color in freq_color_pairs:
            if not freq:
                continue
            self.add_points([
                (sgns[0]*x, sgns[1]*self.y_uint_to_spatial_height*y, 0)
                for x in np.arange(0, self.x_radius, self.epsilon)
                for y in np.arange(0, self.y_radius, freq)
                for sgns in it.product([-1, 1], [-1, 1])
            ], color = color)
        self.shift(self.get_center_point())

    def get_center_point(self):
        return self.num_pair_to_point(self.num_pair_at_center)

    def num_pair_to_point(self, pair):
        pair = pair + self.num_pair_at_center
        return pair[0]*self.x_unit_to_spatial_width*RIGHT + \
               pair[1]*self.y_uint_to_spatial_height*UP

    def get_coordinate_labels(self, x_vals = None, y_vals = None):
        result = []
        nudge = 0.1*(DOWN+RIGHT)
        if x_vals == None and y_vals == None:
            x_vals = range(-int(self.x_radius), int(self.x_radius))
            y_vals = range(-int(self.y_radius), int(self.y_radius))
        for index, vals in zip([0, 1], [x_vals, y_vals]):
            num_pair = [0, 0]
            for val in vals:
                num_pair[index] = val
                point = self.num_pair_to_point(num_pair)
                num = tex_mobject(str(val))
                num.scale(self.number_scale_factor)
                num.shift(point-num.get_corner(UP+LEFT)+nudge)
                result.append(num)
        return result

    def add_coordinates(self, x_vals = None, y_vals = None):
        self.add(*self.get_coordinate_labels(x_vals, y_vals))
        return self

class ComplexPlane(NumberPlane):
    #TODO
    pass







