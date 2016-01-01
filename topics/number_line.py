from helpers import *

from mobject import Mobject1D
from mobject.tex_mobject import TexMobject
from scene import Scene

class NumberLine(Mobject1D):
    DEFAULT_CONFIG = {
        "color"                        : BLUE,
        "numerical_radius"             : SPACE_WIDTH,
        "unit_length_to_spatial_width" : 1,
        "tick_size"                    : 0.1,
        "tick_frequency"               : 0.5,
        "leftmost_tick"                : None,
        "number_at_center"             : 0,         
        "numbers_with_elongated_ticks" : [0],
        "longer_tick_multiple"         : 2,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.leftmost_tick is None:
            self.leftmost_tick = -int(self.numerical_radius-self.number_at_center)
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
            self.get_left(),
            self.get_right(),
            float(number-self.left_num)/(self.right_num - self.left_num)
        )

    def point_to_number(self, point):
        new_point = point-self.get_center()
        return self.number_at_center + new_point[0]/self.unit_length_to_spatial_width

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
            mob = TexMobject(str(int(number)))
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
        "numerical_radius"             : 0.5,
        "unit_length_to_spatial_width" : 2*(SPACE_WIDTH-1),
        "tick_frequency"               : 0.1,
        "leftmost_tick"                : 0,
        "number_at_center"             : 0.5,                 
        "numbers_with_elongated_ticks" : [0, 1],
    }


class NumberPlane(Mobject1D):
    DEFAULT_CONFIG = {
        "color"                    : BLUE,
        "x_radius"                 : SPACE_WIDTH,
        "y_radius"                 : SPACE_HEIGHT,
        "x_unit_to_spatial_width"  : 1,
        "y_unit_to_spatial_height" : 1,
        "x_line_frequency"         : 1,
        "x_faded_line_frequency"   : 0.5,
        "y_line_frequency"         : 1,
        "y_faded_line_frequency"   : 0.5,
        "fade_factor"              : 0.3,
        "number_scale_factor"      : 0.25,
        "num_pair_at_center"       : np.array((0, 0)),
    }
    
    def generate_points(self):
        #TODO, clean this
        color = self.color
        faded = Color(rgb = self.fade_factor*np.array(color.get_rgb()))

        freq_color_tuples = [
            (self.x_line_frequency, self.y_line_frequency, color),
            (self.x_faded_line_frequency, self.y_faded_line_frequency, faded),
        ]
        x_vals = []
        y_vals = []
        for x_freq, y_freq, color in freq_color_tuples:
            if not x_freq or not y_freq:
                continue
            x_vals = np.array(filter(lambda x : x not in x_vals, np.arange(
                0, self.x_radius,
                self.x_unit_to_spatial_width*x_freq
            )))
            y_vals = np.array(filter(lambda y : y not in y_vals, np.arange(
                0, self.y_radius,
                self.y_unit_to_spatial_height*y_freq
            )))
            x_cont_vals = np.arange(
                0, self.x_radius,
                self.epsilon/self.x_unit_to_spatial_width
            )
            y_cont_vals = np.arange(
                0, self.y_radius,
                self.epsilon/self.y_unit_to_spatial_height
            )
            for x_sgn, y_sgn in it.product([-1, 1], [-1, 1]):
                self.add_points(
                    list(it.product(x_sgn*x_vals, y_sgn*y_cont_vals, [0])) + \
                    list(it.product(x_sgn*x_cont_vals, y_sgn*y_vals, [0])),
                    color = color
                )
        self.shift(self.get_center_point())



    def get_center_point(self):
        return self.num_pair_to_point(self.num_pair_at_center)

    def num_pair_to_point(self, pair):
        pair = pair + self.num_pair_at_center
        result = self.get_center()
        result[0] += pair[0]*self.x_unit_to_spatial_width
        result[1] += pair[1]*self.y_unit_to_spatial_height
        return result

    def point_to_num_pair(self, point):
        new_point = point-self.get_center()
        center_x, center_y = self.num_pair_at_center
        x = center_x + point[0]/self.x_unit_to_spatial_width
        y = center_y + point[1]/self.y_unit_to_spatial_height
        return x, y

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
                num = TexMobject(str(val))
                num.scale(self.number_scale_factor)
                num.shift(point-num.get_corner(UP+LEFT)+nudge)
                result.append(num)
        return result

    def add_coordinates(self, x_vals = None, y_vals = None):
        self.add(*self.get_coordinate_labels(x_vals, y_vals))
        return self

    def get_vector(self, coords, **kwargs):
        if len(coords) == 2:
            coords = tuple(list(coords) + [0])
        arrow = Arrow(ORIGIN, coords, **kwargs)
        arrow.remove_tip()
        arrow.align_data(Line(ORIGIN, SPACE_WIDTH*LEFT))
        arrow.add_tip()
        return arrow


class XYZAxes(Mobject1D):
    DEFAULT_CONFIG = {
        "color"          : TEAL,
        "radius"         : SPACE_HEIGHT,
        "tick_frequency" : 1,
    }
    def generate_points(self):
        self.x_axis = NumberLine(
            numerical_radius = self.radius,
            tick_frequency = self.tick_frequency
        )
        self.y_axis = self.x_axis.copy().rotate(np.pi/2, OUT)
        self.z_axis = self.x_axis.copy().rotate(np.pi/2, DOWN)

        self.digest_mobject_attrs()
        self.pose_at_angle()


class SpaceGrid(Mobject1D):
    DEFAULT_CONFIG = {
        "color"                  : GREEN,
        "radius"                 : SPACE_HEIGHT,
        "unit_to_spatial_length" : 1,
        "line_frequency"         : 2,
    }
    def generate_points(self):
        line_range = range(-int(self.radius), int(self.radius)+1, self.line_frequency)
        for i in range(3):
            perm = np.arange(i, i+3) % 3
            for a, b in it.product(line_range, line_range):
                start = np.array([a, b, -self.radius])[perm]
                end   = np.array([a, b, self.radius])[perm]
                self.add_line(start, end)
        self.pose_at_angle()



class NumberLineScene(Scene):
    def construct(self, **number_line_config):
        self.number_line = NumberLine(**number_line_config)
        self.displayed_numbers = self.number_line.default_numbers_to_display()
        self.number_mobs = self.number_line.get_number_mobjects(*self.displayed_numbers)
        self.add(self.number_line, *self.number_mobs)

    def zoom_in_on(self, number, zoom_factor, run_time = 2.0):
        unit_length_to_spatial_width = self.number_line.unit_length_to_spatial_width*zoom_factor
        radius = SPACE_WIDTH/unit_length_to_spatial_width
        tick_frequency = 10**(np.floor(np.log10(radius)))
        left_tick = tick_frequency*(np.ceil((number-radius)/tick_frequency))
        new_number_line = NumberLine(
            numerical_radius = radius,
            unit_length_to_spatial_width = unit_length_to_spatial_width,
            tick_frequency = tick_frequency,
            leftmost_tick = left_tick,
            number_at_center = number
        )
        new_displayed_numbers = new_number_line.default_numbers_to_display()
        new_number_mobs = new_number_line.get_number_mobjects(*new_displayed_numbers)        

        transforms = []
        additional_mobjects = []
        squished_new_line = new_number_line.copy()
        squished_new_line.scale(1.0/zoom_factor)
        squished_new_line.shift(self.number_line.number_to_point(number))
        squished_new_line.points[:,1] = self.number_line.number_to_point(0)[1]
        transforms.append(Transform(squished_new_line, new_number_line))
        for mob, num in zip(new_number_mobs, new_displayed_numbers):
            point = Point(self.number_line.number_to_point(num))
            point.shift(new_number_line.get_vertical_number_offset())
            transforms.append(Transform(point, mob))
        for mob in self.mobjects:
            if mob == self.number_line:
                new_mob = mob.copy()
                new_mob.shift(-self.number_line.number_to_point(number))
                new_mob.stretch(zoom_factor, 0)
                transforms.append(Transform(mob, new_mob))
                continue
            mob_center = mob.get_center()
            number_under_center = self.number_line.point_to_number(mob_center)
            new_point = new_number_line.number_to_point(number_under_center)
            new_point += mob_center[1]*UP
            if mob in self.number_mobs:
                transforms.append(Transform(mob, Point(new_point)))
            else:
                transforms.append(ApplyMethod(mob.shift, new_point - mob_center))
                additional_mobjects.append(mob)
        line_to_hide_pixelation = Line(
            self.number_line.get_left(),
            self.number_line.get_right(),
            color = self.number_line.get_color()
        )
        self.add(line_to_hide_pixelation)
        self.play(*transforms, run_time = run_time)
        self.clear()
        self.number_line = new_number_line
        self.displayed_numbers = new_displayed_numbers
        self.number_mobs = new_number_mobs
        self.add(self.number_line, *self.number_mobs)
        self.add(*additional_mobjects)

    def show_multiplication(self, num, **kwargs):
        if "path_func" not in kwargs:
            if num > 0:
                kwargs["path_func"] = straight_path
            else:
                kwargs["path_func"] = counterclockwise_path()
        self.play(*[
            ApplyMethod(self.number_line.stretch, num, 0, **kwargs)
        ]+[
            ApplyMethod(mob.shift, (num-1)*mob.get_center()[0]*RIGHT, **kwargs)
            for mob in self.number_mobs
        ])




















