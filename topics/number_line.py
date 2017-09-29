from helpers import *

from mobject import Mobject1D
from mobject.vectorized_mobject import VMobject, VGroup
from mobject.tex_mobject import TexMobject
from topics.geometry import Line, Arrow
from scene import Scene

class NumberLine(VMobject):
    CONFIG = {
        "color" : BLUE,
        "x_min" : -SPACE_WIDTH,
        "x_max" : SPACE_WIDTH,
        "unit_size" : 1,
        "tick_size" : 0.1,
        "tick_frequency" : 1,
        "leftmost_tick" : None, #Defaults to ceil(x_min)
        "numbers_with_elongated_ticks" : [0],
        "numbers_to_show" : None,
        "longer_tick_multiple" : 2,
        "number_at_center" : 0,
        "number_scale_val" : 0.75,
        "line_to_number_vect" : DOWN,
        "line_to_number_buff" : MED_SMALL_BUFF,
        "include_tip" : False,
        "propogate_style_to_family" : True,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.leftmost_tick is None:
            self.leftmost_tick = np.ceil(self.x_min)
        VMobject.__init__(self, **kwargs)
        if self.include_tip:
            self.add_tip()

    def generate_points(self):
        self.main_line = Line(self.x_min*RIGHT, self.x_max*RIGHT)
        self.tick_marks = VGroup()
        self.add(self.main_line, self.tick_marks)
        for x in self.get_tick_numbers():
            self.add_tick(x, self.tick_size)
        for x in self.numbers_with_elongated_ticks:
            self.add_tick(x, self.longer_tick_multiple*self.tick_size)
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
                self.line_to_number_vect,
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
        "propogate_style_to_family" : True,
        "three_d" : False,
        "number_line_config" : {
            "color" : LIGHT_GREY,
            "include_tip" : True,
        },
        "x_min" : -SPACE_WIDTH,
        "x_max" : SPACE_WIDTH,
        "y_min" : -SPACE_HEIGHT,
        "y_max" : SPACE_HEIGHT,
        "z_min" : -3.5,
        "z_max" : 3.5,
        "z_normal" : DOWN,
    }
    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.x_axis = NumberLine(
            x_min = self.x_min,
            x_max = self.x_max,
            **self.number_line_config
        )
        self.y_axis = NumberLine(
            x_min = self.y_min,
            x_max = self.y_max,
            **self.number_line_config
        )
        self.y_axis.rotate(np.pi/2)
        self.add(self.x_axis, self.y_axis)
        if self.three_d:
            self.z_axis = NumberLine(
                x_min = self.z_min,
                x_max = self.z_max,
                **self.number_line_config
            )
            self.z_axis.rotate(-np.pi/2, UP)
            self.z_axis.rotate(angle_of_vector(self.z_normal), OUT)
            self.add(self.z_axis)

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
        "propogate_style_to_family" : False,
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

    def apply_function(self, function, maintain_smoothness = True):
        SVGMobject.apply_function(self, function, maintain_smoothness = maintain_smoothness)












