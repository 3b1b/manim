from helpers import *

from mobject import Mobject1D
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TexMobject
from topics.geometry import Line, Arrow
from scene import Scene

class NumberLine(VMobject):
    CONFIG = {
        "color" : BLUE,
        "x_min" : -SPACE_WIDTH,
        "x_max" : SPACE_WIDTH,
        "space_unit_to_num" : 1,
        "tick_size" : 0.1,
        "tick_frequency" : 0.5,
        "leftmost_tick" : None, #Defaults to ceil(x_min)
        "numbers_with_elongated_ticks" : [0],
        "longer_tick_multiple" : 2,
        "number_at_center" : 0,
        "propogate_style_to_family" : True
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.leftmost_tick is None:
            self.leftmost_tick = np.ceil(self.x_min)
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        self.main_line = Line(self.x_min*RIGHT, self.x_max*RIGHT)
        self.tick_marks = VMobject()
        self.add(self.main_line, self.tick_marks)
        for x in self.get_tick_numbers():
            self.add_tick(x, self.tick_size)
        for x in self.numbers_with_elongated_ticks:
            self.add_tick(x, self.longer_tick_multiple*self.tick_size)
        self.stretch(self.space_unit_to_num, 0)
        self.shift(-self.number_to_point(self.number_at_center))

    def add_tick(self, x, size):
        self.tick_marks.add(Line(
            x*RIGHT+size*DOWN,
            x*RIGHT+size*UP,
        ))
        return self

    def get_tick_marks(self):
        return self.tick_marks

    def get_tick_numbers(self):
        return np.arange(self.leftmost_tick, self.x_max, self.tick_frequency)

    def number_to_point(self, number):
        return interpolate(
            self.main_line.get_left(),
            self.main_line.get_right(),
            float(number-self.x_min)/(self.x_max - self.x_min)
        )

    def point_to_number(self, point):
        dist_from_left = (point[0]-self.main_line.get_left()[0])
        num_dist_from_left = num_dist_from_left/self.space_unit_to_num
        return self.x_min + dist_from_left

    def default_numbers_to_display(self):
        return self.get_tick_numbers()[::2]

    def get_vertical_number_offset(self, direction = DOWN):
        return 4*direction*self.tick_size

    def get_number_mobjects(self, *numbers, **kwargs):
        #TODO, handle decimals
        if len(numbers) == 0:
            numbers = self.default_numbers_to_display()
        result = []
        for number in numbers:
            mob = TexMobject(str(int(number)))
            mob.scale_to_fit_height(2*self.tick_size)
            mob.shift(
                self.number_to_point(number),
                self.get_vertical_number_offset(**kwargs)
            )
            result.append(mob)
        return result

    def add_numbers(self, *numbers, **kwargs):
        self.numbers = self.get_number_mobjects(
            *numbers, **kwargs
        )
        self.add(*self.numbers)
        return self

class UnitInterval(NumberLine):
    CONFIG = {
        "x_min" : 0,
        "x_max" : 1,
        "space_unit_to_num" : 6,
        "tick_frequency" : 0.1,
        "numbers_with_elongated_ticks" : [0, 1],
        "number_at_center" : 0.5,
    }


class Axes(VMobject):
    CONFIG = {
        "propogate_style_to_family" : True
    }
    def generate_points(self, **kwargs):
        self.x_axis = NumberLine(**kwargs)
        self.y_axis = NumberLine(**kwargs).rotate(np.pi/2)
        self.add(self.x_axis, self.y_axis)


class NumberPlane(VMobject):
    CONFIG = {
        "color" : BLUE_D,
        "secondary_color" : BLUE_E,
        "axes_color" : WHITE,
        "x_radius": SPACE_WIDTH,
        "y_radius": SPACE_HEIGHT,
        "space_unit_to_x_unit" : 1,
        "space_unit_to_y_unit" : 1,
        "x_line_frequency" : 1,
        "y_line_frequency" : 1,
        "secondary_line_ratio" : 1,
        "written_coordinate_height" : 0.2,
        "written_coordinate_nudge" : 0.1*(DOWN+RIGHT),
        "num_pair_at_center" : (0, 0),
        "propogate_style_to_family" : False,
    }
    
    def generate_points(self):
        self.axes = VMobject()
        self.main_lines = VMobject()
        self.secondary_lines = VMobject()
        tuples = [
            (
                self.x_radius, 
                self.x_line_frequency, 
                self.y_radius*DOWN, 
                self.y_radius*UP,
                RIGHT
            ),
            (
                self.y_radius, 
                self.y_line_frequency, 
                self.x_radius*LEFT, 
                self.x_radius*RIGHT,
                UP,
            ),
        ]
        for radius, freq, start, end, unit in tuples:
            main_range = np.arange(0, radius, freq)
            step = freq/float(freq + self.secondary_line_ratio)
            for v in np.arange(0, radius, step):
                line1 = Line(start+v*unit, end+v*unit)
                line2 = Line(start-v*unit, end-v*unit)                
                if v == 0:
                    self.axes.add(line1)
                elif v in main_range:
                    self.main_lines.add(line1, line2)
                else:
                    self.secondary_lines.add(line1, line2)
        self.add(self.axes, self.main_lines, self.secondary_lines)
        self.stretch(self.space_unit_to_x_unit, 0)
        self.stretch(self.space_unit_to_y_unit, 1)
        #Put x_axis before y_axis
        y_axis, x_axis = self.axes.split()
        self.axes = VMobject(x_axis, y_axis)

    def init_colors(self):
        VMobject.init_colors(self)
        self.axes.set_stroke(self.axes_color)
        self.main_lines.set_stroke(self.color)
        self.secondary_lines.set_stroke(self.secondary_color, 1)
        return self

    def get_center_point(self):
        return self.num_pair_to_point(self.num_pair_at_center)

    def num_pair_to_point(self, pair):
        pair = np.array(pair) + self.num_pair_at_center
        result = self.get_center()
        result[0] += pair[0]*self.space_unit_to_x_unit
        result[1] += pair[1]*self.space_unit_to_y_unit
        return result

    def point_to_num_pair(self, point):
        new_point = point-self.get_center()
        center_x, center_y = self.num_pair_at_center
        x = center_x + point[0]/self.space_unit_to_x_unit
        y = center_y + point[1]/self.space_unit_to_y_unit
        return x, y

    def get_coordinate_labels(self, x_vals = None, y_vals = None):
        result = []
        if x_vals == None and y_vals == None:
            x_vals = range(-int(self.x_radius), int(self.x_radius))
            y_vals = range(-int(self.y_radius), int(self.y_radius))
        for index, vals in enumerate([x_vals, y_vals]):
            num_pair = [0, 0]
            for val in vals:
                num_pair[index] = val
                point = self.num_pair_to_point(num_pair)
                num = TexMobject(str(val))
                num.scale_to_fit_height(
                    self.written_coordinate_height
                )
                num.shift(
                    point-num.get_corner(UP+LEFT),
                    self.written_coordinate_nudge
                )
                result.append(num)
        return result

    def get_axes(self):
        return self.axes

    def get_axis_labels(self, x_label = "x", y_label = "y"):
        x_axis, y_axis = self.get_axes().split()
        x_label_mob = TexMobject(x_label)
        y_label_mob = TexMobject(y_label)
        x_label_mob.next_to(x_axis, DOWN)
        x_label_mob.to_edge(RIGHT)
        y_label_mob.next_to(y_axis, RIGHT)
        y_label_mob.to_edge(UP)
        return VMobject(x_label_mob, y_label_mob)


    def add_coordinates(self, x_vals = None, y_vals = None):
        self.add(*self.get_coordinate_labels(x_vals, y_vals))
        return self

    def get_vector(self, coords, **kwargs):
        point = coords[0]*RIGHT + coords[1]*UP
        arrow = Arrow(ORIGIN, coords, **kwargs)
        return arrow

    def prepare_for_nonlinear_transform(self):
        for mob in self.submobject_family():
            if mob.get_num_points() > 0:
                mob.insert_n_anchor_points(20)
                mob.change_anchor_mode("smooth")












