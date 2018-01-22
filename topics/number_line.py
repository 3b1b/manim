from helpers import *

from mobject import Mobject1D
from mobject.vectorized_mobject import VMobject, VGroup
from mobject.tex_mobject import TexMobject
from topics.geometry import Line, Arrow
from topics.functions import ParametricFunction
from scene import Scene

class NumberLine(VMobject):
    CONFIG = {
        "color" : BLUE,
        "x_min" : -SPACE_WIDTH,
        "x_max" : SPACE_WIDTH,
        "unit_size" : 1,
        "tick_size" : 0.1,
        "tick_frequency" : 1,
        "leftmost_tick" : None, #Defaults to value near x_min s.t. 0 is a tick
        "numbers_with_elongated_ticks" : [0],
        "numbers_to_show" : None,
        "longer_tick_multiple" : 2,
        "number_at_center" : 0,
        "number_scale_val" : 0.75,
        "label_direction" : DOWN,
        "line_to_number_buff" : MED_SMALL_BUFF,
        "include_tip" : False,
        "propagate_style_to_family" : True,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.leftmost_tick is None:
            tf = self.tick_frequency
            self.leftmost_tick = tf*np.ceil(self.x_min/tf)
        VMobject.__init__(self, **kwargs)
        if self.include_tip:
            self.add_tip()

    def generate_points(self):
        self.main_line = Line(self.x_min*RIGHT, self.x_max*RIGHT)
        self.tick_marks = VGroup()
        self.add(self.main_line, self.tick_marks)
        rounding_value = int(-np.log10(0.1*self.tick_frequency))
        rounded_numbers_with_elongated_ticks = np.round(
            self.numbers_with_elongated_ticks, 
            rounding_value
        )

        for x in self.get_tick_numbers():
            rounded_x = np.round(x, rounding_value)
            if rounded_x in rounded_numbers_with_elongated_ticks:
                tick_size_used = self.longer_tick_multiple*self.tick_size
            else:
                tick_size_used = self.tick_size
            self.add_tick(x, tick_size_used)

        self.stretch(self.unit_size, 0)
        self.shift(-self.number_to_point(self.number_at_center))

    def add_tick(self, x, size = None):
        self.tick_marks.add(self.get_tick(x, size))
        return self

    def get_tick(self, x, size = None):
        if size is None: size = self.tick_size
        result = Line(size*DOWN, size*UP)
        result.rotate(self.main_line.get_angle())
        result.move_to(self.number_to_point(x))
        return result

    def get_tick_marks(self):
        return self.tick_marks

    def get_tick_numbers(self):
        epsilon = 0.001
        return np.arange(
            self.leftmost_tick, self.x_max+epsilon,
            self.tick_frequency
        )

    def number_to_point(self, number):
        alpha = float(number-self.x_min)/(self.x_max - self.x_min)
        return interpolate(
            self.main_line.get_start(),
            self.main_line.get_end(),
            alpha
        )

    def point_to_number(self, point):
        left_point, right_point = self.main_line.get_start_and_end()
        full_vect = right_point-left_point
        def distance_from_left(p):
            return np.dot(p-left_point, full_vect)/np.linalg.norm(full_vect)

        return interpolate(
            self.x_min, self.x_max, 
            distance_from_left(point)/distance_from_left(right_point)
        )

    def default_numbers_to_display(self):
        if self.numbers_to_show is not None:
            return self.numbers_to_show
        return np.arange(int(self.leftmost_tick), int(self.x_max)+1)

    def get_number_mobjects(self, *numbers, **kwargs):
        #TODO, handle decimals
        if len(numbers) == 0:
            numbers = self.default_numbers_to_display()
        if "force_integers" in kwargs and kwargs["force_integers"]:
            numbers = map(int, numbers)
        result = VGroup()
        for number in numbers:
            mob = TexMobject(str(number))
            mob.scale(self.number_scale_val)
            mob.next_to(
                self.number_to_point(number),
                self.label_direction,
                self.line_to_number_buff,
            )
            result.add(mob)
        return result

    def add_numbers(self, *numbers, **kwargs):
        self.numbers = self.get_number_mobjects(
            *numbers, **kwargs
        )
        self.add(*self.numbers)
        return self

    def add_tip(self):
        start, end = self.main_line.get_start_and_end()
        vect = (end - start)/np.linalg.norm(end-start)
        arrow = Arrow(start, end + MED_SMALL_BUFF*vect, buff = 0)
        tip = arrow.tip
        tip.highlight(self.color)
        self.tip = tip
        self.add(tip)



class UnitInterval(NumberLine):
    CONFIG = {
        "x_min" : 0,
        "x_max" : 1,
        "unit_size" : 6,
        "tick_frequency" : 0.1,
        "numbers_with_elongated_ticks" : [0, 1],
        "number_at_center" : 0.5,
    }

class Axes(VGroup):
    CONFIG = {
        "propagate_style_to_family" : True,
        "three_d" : False,
        "number_line_config" : {
            "color" : LIGHT_GREY,
            "include_tip" : True,
        },
        "x_axis_config" : {},
        "y_axis_config" : {},
        "z_axis_config" : {},
        "x_min" : -SPACE_WIDTH,
        "x_max" : SPACE_WIDTH,
        "y_min" : -SPACE_HEIGHT,
        "y_max" : SPACE_HEIGHT,
        "z_min" : -3.5,
        "z_max" : 3.5,
        "z_normal" : DOWN,
        "default_num_graph_points" : 100,
    }
    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.x_axis = self.get_axis(self.x_min, self.x_max, self.x_axis_config)
        self.y_axis = self.get_axis(self.y_min, self.y_max, self.y_axis_config)
        self.y_axis.rotate(np.pi/2, about_point = ORIGIN)
        self.add(self.x_axis, self.y_axis)
        if self.three_d:
            self.z_axis = self.get_axis(self.z_min, self.z_max, self.z_axis_config)
            self.z_axis.rotate(-np.pi/2, UP, about_point = ORIGIN)
            self.z_axis.rotate(
                angle_of_vector(self.z_normal), OUT,
                about_point = ORIGIN
            )
            self.add(self.z_axis)

    def get_axis(self, min_val, max_val, extra_config):
        config = dict(self.number_line_config)
        config.update(extra_config)
        return NumberLine(x_min = min_val, x_max = max_val, **config)

    def coords_to_point(self, x, y):
        origin = self.x_axis.number_to_point(0)
        x_axis_projection = self.x_axis.number_to_point(x)
        y_axis_projection = self.y_axis.number_to_point(y)
        return x_axis_projection + y_axis_projection - origin

    def point_to_coords(self, point):
        return (
            self.x_axis.point_to_number(point), 
            self.y_axis.point_to_number(point),
        )

    def get_graph(self, function, num_graph_points = None, **kwargs):
        kwargs["fill_opacity"] = kwargs.get("fill_opacity", 0)
        kwargs["num_anchor_points"] = \
            num_graph_points or self.default_num_graph_points
        graph = ParametricFunction(
            lambda t : self.coords_to_point(t, function(t)),
            t_min = self.x_min,
            t_max = self.x_max,
            **kwargs
        )
        graph.underlying_function = function
        return graph

    def input_to_graph_point(self, x, graph):
        return self.coords_to_point(x, graph.underlying_function(x))

class ThreeDAxes(Axes):
    CONFIG = {
        "x_min" : -5.5,
        "x_max" : 5.5,
        "y_min" : -4.5,
        "y_max" : 4.5,
        "three_d" : True,
    }

class NumberPlane(VMobject):
    CONFIG = {
        "color" : BLUE_D,
        "secondary_color" : BLUE_E,
        "axes_color" : WHITE,
        "secondary_stroke_width" : 1,
        "x_radius": None,
        "y_radius": None,
        "x_unit_size" : 1,
        "y_unit_size" : 1,
        "center_point" : ORIGIN,
        "x_line_frequency" : 1,
        "y_line_frequency" : 1,
        "secondary_line_ratio" : 1,
        "written_coordinate_height" : 0.2,
        "propagate_style_to_family" : False,
        "make_smooth_after_applying_functions" : True,
    }
    def generate_points(self):
        if self.x_radius is None:
            center_to_edge = (SPACE_WIDTH + abs(self.center_point[0])) 
            self.x_radius = center_to_edge / self.x_unit_size
        if self.y_radius is None:
            center_to_edge = (SPACE_HEIGHT + abs(self.center_point[1])) 
            self.y_radius = center_to_edge / self.y_unit_size
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
        self.add(self.secondary_lines, self.main_lines, self.axes)
        self.stretch(self.x_unit_size, 0)
        self.stretch(self.y_unit_size, 1)
        self.shift(self.center_point)
        #Put x_axis before y_axis
        y_axis, x_axis = self.axes.split()
        self.axes = VMobject(x_axis, y_axis)

    def init_colors(self):
        VMobject.init_colors(self)
        self.axes.set_stroke(self.axes_color, self.stroke_width)
        self.main_lines.set_stroke(self.color, self.stroke_width)
        self.secondary_lines.set_stroke(
            self.secondary_color, self.secondary_stroke_width
        )
        return self

    def get_center_point(self):
        return self.coords_to_point(0, 0)

    def coords_to_point(self, x, y):
        x, y = np.array([x, y])
        result = self.axes.get_center()
        result += x*self.get_x_unit_size()*RIGHT
        result += y*self.get_y_unit_size()*UP
        return result

    def point_to_coords(self, point):
        new_point = point - self.axes.get_center()
        x = new_point[0]/self.get_x_unit_size()
        y = new_point[1]/self.get_y_unit_size()
        return x, y

    def get_x_unit_size(self):
        return self.axes.get_width() / (2.0*self.x_radius)

    def get_y_unit_size(self):
        return self.axes.get_height() / (2.0*self.y_radius)

    def get_coordinate_labels(self, x_vals = None, y_vals = None):
        coordinate_labels = VGroup()
        if x_vals == None:
            x_vals = range(-int(self.x_radius), int(self.x_radius)+1)
        if y_vals == None:
            y_vals = range(-int(self.y_radius), int(self.y_radius)+1)
        for index, vals in enumerate([x_vals, y_vals]):
            num_pair = [0, 0]
            for val in vals:
                if val == 0:
                    continue
                num_pair[index] = val
                point = self.coords_to_point(*num_pair)
                num = TexMobject(str(val))
                num.add_background_rectangle()
                num.scale_to_fit_height(
                    self.written_coordinate_height
                )
                num.next_to(point, DOWN+LEFT, buff = SMALL_BUFF)
                coordinate_labels.add(num)
        self.coordinate_labels = coordinate_labels
        return coordinate_labels

    def get_axes(self):
        return self.axes

    def get_axis_labels(self, x_label = "x", y_label = "y"):
        x_axis, y_axis = self.get_axes().split()
        quads = [
            (x_axis, x_label, UP, RIGHT),
            (y_axis, y_label, RIGHT, UP),
        ]
        labels = VGroup()
        for axis, tex, vect, edge in quads:
            label = TexMobject(tex)
            label.add_background_rectangle()
            label.next_to(axis, vect)
            label.to_edge(edge)
            labels.add(label)
        self.axis_labels = labels
        return labels

    def add_coordinates(self, x_vals = None, y_vals = None):
        self.add(*self.get_coordinate_labels(x_vals, y_vals))
        return self

    def get_vector(self, coords, **kwargs):
        point = coords[0]*RIGHT + coords[1]*UP
        arrow = Arrow(ORIGIN, coords, **kwargs)
        return arrow

    def prepare_for_nonlinear_transform(self, num_inserted_anchor_points = 50):
        for mob in self.family_members_with_points():
            num_anchors = mob.get_num_anchor_points()
            if num_inserted_anchor_points > num_anchors:
                mob.insert_n_anchor_points(num_inserted_anchor_points-num_anchors)
                mob.make_smooth()
        return self











