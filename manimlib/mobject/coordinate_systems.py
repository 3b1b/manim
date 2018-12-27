import numpy as np

from manimlib.constants import *
from manimlib.mobject.functions import ParametricFunction
from manimlib.mobject.geometry import Arrow
from manimlib.mobject.geometry import Line
from manimlib.mobject.number_line import NumberLine
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import angle_of_vector

# TODO: There should be much more code reuse between Axes, NumberPlane and GraphScene


class Axes(VGroup):
    CONFIG = {
        "propagate_style_to_family": True,
        "three_d": False,
        "number_line_config": {
            "color": LIGHT_GREY,
            "include_tip": True,
        },
        "x_axis_config": {},
        "y_axis_config": {
            "label_direction": LEFT,
        },
        "x_min": -FRAME_X_RADIUS,
        "x_max": FRAME_X_RADIUS,
        "y_min": -FRAME_Y_RADIUS,
        "y_max": FRAME_Y_RADIUS,
        "default_num_graph_points": 100,
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.x_axis = self.get_axis(self.x_min, self.x_max, self.x_axis_config)
        self.y_axis = self.get_axis(self.y_min, self.y_max, self.y_axis_config)
        self.y_axis.rotate(np.pi / 2, about_point=ORIGIN)
        self.add(self.x_axis, self.y_axis)

    def get_axis(self, min_val, max_val, extra_config):
        config = dict(self.number_line_config)
        config.update(extra_config)
        return NumberLine(x_min=min_val, x_max=max_val, **config)

    def coords_to_point(self, *coords):
        origin = self.x_axis.number_to_point(0)
        result = np.array(origin)
        for axis, coord in zip(self, coords):
            result += (axis.number_to_point(coord) - origin)
        return result

    def point_to_coords(self, point):
        return tuple([
            axis.point_to_number(point)
            for axis in self
            if isinstance(axis, NumberLine)
        ])

    def get_graph(
        self, function, num_graph_points=None,
        x_min=None,
        x_max=None,
        **kwargs
    ):
        kwargs["fill_opacity"] = kwargs.get("fill_opacity", 0)
        kwargs["num_anchor_points"] = \
            num_graph_points or self.default_num_graph_points
        x_min = x_min or self.x_min
        x_max = x_max or self.x_max
        graph = ParametricFunction(
            lambda t: self.coords_to_point(t, function(t)),
            t_min=x_min,
            t_max=x_max,
            **kwargs
        )
        graph.underlying_function = function
        return graph

    def input_to_graph_point(self, x, graph):
        if hasattr(graph, "underlying_function"):
            return self.coords_to_point(x, graph.underlying_function(x))
        else:
            # binary search
            lh, rh = 0, 1
            while abs(lh - rh) > 0.001:
                mh = np.mean([lh, rh])
                hands = [lh, mh, rh]
                points = list(map(graph.point_from_proportion, hands))
                lx, mx, rx = list(map(self.x_axis.point_to_number, points))
                if lx <= x and rx >= x:
                    if mx > x:
                        rh = mh
                    else:
                        lh = mh
                elif lx <= x and rx <= x:
                    return points[2]
                elif lx >= x and rx >= x:
                    return points[0]
                elif lx > x and rx < x:
                    lh, rh = rh, lh
            return points[1]
        return self.coords_to_point(x, graph.underlying_function(x))


class ThreeDAxes(Axes):
    CONFIG = {
        "x_min": -5.5,
        "x_max": 5.5,
        "y_min": -5.5,
        "y_max": 5.5,
        "z_axis_config": {},
        "z_min": -3.5,
        "z_max": 3.5,
        "z_normal": DOWN,
        "num_axis_pieces": 20,
        "light_source": 9 * DOWN + 7 * LEFT + 10 * OUT,
    }

    def __init__(self, **kwargs):
        Axes.__init__(self, **kwargs)
        z_axis = self.z_axis = self.get_axis(
            self.z_min, self.z_max, self.z_axis_config
        )
        z_axis.rotate(-np.pi / 2, UP, about_point=ORIGIN)
        z_axis.rotate(
            angle_of_vector(self.z_normal), OUT,
            about_point=ORIGIN
        )
        self.add(z_axis)

        self.add_3d_pieces()
        self.set_axis_shading()

    def add_3d_pieces(self):
        for axis in self:
            axis.pieces = VGroup(
                *axis.main_line.get_pieces(self.num_axis_pieces)
            )
            axis.add(axis.pieces)
            axis.main_line.set_stroke(width=0, family=False)
            axis.set_shade_in_3d(True)

    def set_axis_shading(self):
        def make_func(axis):
            vect = self.light_source
            return lambda: (
                axis.get_edge_center(-vect),
                axis.get_edge_center(vect),
            )
        for axis in self:
            for submob in axis.family_members_with_points():
                submob.get_gradient_start_and_end_points = make_func(axis)
                submob.get_unit_normal = lambda a: np.ones(3)
                submob.set_sheen(0.2)


class NumberPlane(VMobject):
    CONFIG = {
        "color": BLUE_D,
        "secondary_color": BLUE_E,
        "axes_color": WHITE,
        "secondary_stroke_width": 1,
        # TODO: Allow coordinate center of NumberPlane to not be at (0, 0)
        "x_radius": None,
        "y_radius": None,
        "x_unit_size": 1,
        "y_unit_size": 1,
        "center_point": ORIGIN,
        "x_line_frequency": 1,
        "y_line_frequency": 1,
        "secondary_line_ratio": 1,
        "written_coordinate_height": 0.2,
        "propagate_style_to_family": False,
        "make_smooth_after_applying_functions": True,
    }

    def generate_points(self):
        if self.x_radius is None:
            center_to_edge = (FRAME_X_RADIUS + abs(self.center_point[0]))
            self.x_radius = center_to_edge / self.x_unit_size
        if self.y_radius is None:
            center_to_edge = (FRAME_Y_RADIUS + abs(self.center_point[1]))
            self.y_radius = center_to_edge / self.y_unit_size
        self.axes = VMobject()
        self.main_lines = VMobject()
        self.secondary_lines = VMobject()
        tuples = [
            (
                self.x_radius,
                self.x_line_frequency,
                self.y_radius * DOWN,
                self.y_radius * UP,
                RIGHT
            ),
            (
                self.y_radius,
                self.y_line_frequency,
                self.x_radius * LEFT,
                self.x_radius * RIGHT,
                UP,
            ),
        ]
        for radius, freq, start, end, unit in tuples:
            main_range = np.arange(0, radius, freq)
            step = freq / float(freq + self.secondary_line_ratio)
            for v in np.arange(0, radius, step):
                line1 = Line(start + v * unit, end + v * unit)
                line2 = Line(start - v * unit, end - v * unit)
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
        # Put x_axis before y_axis
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
        result += x * self.get_x_unit_size() * RIGHT
        result += y * self.get_y_unit_size() * UP
        return result

    def point_to_coords(self, point):
        new_point = point - self.axes.get_center()
        x = new_point[0] / self.get_x_unit_size()
        y = new_point[1] / self.get_y_unit_size()
        return x, y

    # Does not recompute center, unit_sizes for each call; useful for
    # iterating over large lists of points, but does assume these
    # attributes are kept accurate. (Could alternatively have a method
    # which returns a function dynamically created after a single
    # call to each of get_center(), get_x_unit_size(), etc.)
    def point_to_coords_cheap(self, point):
        new_point = point - self.center_point
        x = new_point[0] / self.x_unit_size
        y = new_point[1] / self.y_unit_size
        return x, y

    def get_x_unit_size(self):
        return self.axes.get_width() / (2.0 * self.x_radius)

    def get_y_unit_size(self):
        return self.axes.get_height() / (2.0 * self.y_radius)

    def get_coordinate_labels(self, x_vals=None, y_vals=None):
        coordinate_labels = VGroup()
        if x_vals is None:
            x_vals = list(range(-int(self.x_radius), int(self.x_radius) + 1))
        if y_vals is None:
            y_vals = list(range(-int(self.y_radius), int(self.y_radius) + 1))
        for index, vals in enumerate([x_vals, y_vals]):
            num_pair = [0, 0]
            for val in vals:
                if val == 0:
                    continue
                num_pair[index] = val
                point = self.coords_to_point(*num_pair)
                num = TexMobject(str(val))
                num.add_background_rectangle()
                num.set_height(
                    self.written_coordinate_height
                )
                num.next_to(point, DOWN + LEFT, buff=SMALL_BUFF)
                coordinate_labels.add(num)
        self.coordinate_labels = coordinate_labels
        return coordinate_labels

    def get_axes(self):
        return self.axes

    def get_axis_labels(self, x_label="x", y_label="y"):
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

    def add_coordinates(self, x_vals=None, y_vals=None):
        self.add(*self.get_coordinate_labels(x_vals, y_vals))
        return self

    def get_vector(self, coords, **kwargs):
        point = coords[0] * RIGHT + coords[1] * UP
        arrow = Arrow(ORIGIN, point, **kwargs)
        return arrow

    def prepare_for_nonlinear_transform(self, num_inserted_anchor_points=50):
        for mob in self.family_members_with_points():
            num_anchors = mob.get_num_anchor_points()
            if num_inserted_anchor_points > num_anchors:
                mob.insert_n_anchor_points(
                    num_inserted_anchor_points - num_anchors)
                mob.make_smooth()
        return self


class ComplexPlane(NumberPlane):
    CONFIG = {
        "color": BLUE,
        "unit_size": 1,
        "line_frequency": 1,
        "faded_line_frequency": 0.5,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        kwargs.update({
            "x_unit_size": self.unit_size,
            "y_unit_size": self.unit_size,
            "x_line_frequency": self.line_frequency,
            "x_faded_line_frequency": self.faded_line_frequency,
            "y_line_frequency": self.line_frequency,
            "y_faded_line_frequency": self.faded_line_frequency,
        })
        NumberPlane.__init__(self, **kwargs)

    def number_to_point(self, number):
        number = complex(number)
        return self.coords_to_point(number.real, number.imag)

    def point_to_number(self, point):
        x, y = self.point_to_coords(point)
        return complex(x, y)

    def get_coordinate_labels(self, *numbers):
        # TODO: Should merge this with the code from NumberPlane.get_coordinate_labels

        result = VGroup()
        if len(numbers) == 0:
            numbers = list(range(-int(self.x_radius), int(self.x_radius) + 1))
            numbers += [
                complex(0, y)
                for y in range(-int(self.y_radius), int(self.y_radius) + 1)
                if y != 0
            ]
        for number in numbers:
            # if number == complex(0, 0):
            #     continue
            point = self.number_to_point(number)
            num_str = str(number).replace("j", "i")
            if num_str.startswith("0"):
                num_str = "0"
            elif num_str in ["1i", "-1i"]:
                num_str = num_str.replace("1", "")
            num_mob = TexMobject(num_str)
            num_mob.add_background_rectangle()
            num_mob.set_height(self.written_coordinate_height)
            num_mob.next_to(point, DOWN + LEFT, SMALL_BUFF)
            result.add(num_mob)
        self.coordinate_labels = result
        return result

    def add_coordinates(self, *numbers):
        self.coordinate_labels = self.get_coordinate_labels(*numbers)
        self.add(self.coordinate_labels)
        return self
