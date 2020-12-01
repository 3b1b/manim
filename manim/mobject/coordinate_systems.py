"""Mobjects that represent coordinate systems."""

__all__ = ["CoordinateSystem", "Axes", "ThreeDAxes", "NumberPlane", "ComplexPlane"]


import numpy as np
import numbers

from .. import config
from ..constants import *
from ..mobject.functions import ParametricFunction
from ..mobject.geometry import Arrow
from ..mobject.geometry import Line
from ..mobject.number_line import NumberLine
from ..mobject.svg.tex_mobject import MathTex
from ..mobject.types.vectorized_mobject import VGroup
from ..utils.config_ops import merge_dicts_recursively
from ..utils.simple_functions import binary_search
from ..utils.space_ops import angle_of_vector
from ..utils.color import LIGHT_GREY, WHITE, BLUE_D, BLUE


# TODO: There should be much more code reuse between Axes, NumberPlane and GraphScene


class CoordinateSystem:
    """
    Abstract class for Axes and NumberPlane
    """

    def __init__(self, dim=2):
        self.dimension = dim
        if not hasattr(self, "x_min"):
            self.x_min = -config["frame_x_radius"]
        if not hasattr(self, "x_max"):
            self.x_max = config["frame_x_radius"]
        if not hasattr(self, "y_min"):
            self.y_min = -config["frame_y_radius"]
        if not hasattr(self, "y_max"):
            self.y_max = config["frame_y_radius"]

    def coords_to_point(self, *coords):
        raise NotImplementedError()

    def point_to_coords(self, point):
        raise NotImplementedError()

    def c2p(self, *coords):
        """Abbreviation for coords_to_point"""
        return self.coords_to_point(*coords)

    def p2c(self, point):
        """Abbreviation for point_to_coords"""
        return self.point_to_coords(point)

    def get_axes(self):
        raise NotImplementedError()

    def get_axis(self, index):
        return self.get_axes()[index]

    def get_x_axis(self):
        return self.get_axis(0)

    def get_y_axis(self):
        return self.get_axis(1)

    def get_z_axis(self):
        return self.get_axis(2)

    def get_x_axis_label(self, label_tex, edge=RIGHT, direction=DL, **kwargs):
        return self.get_axis_label(
            label_tex, self.get_x_axis(), edge, direction, **kwargs
        )

    def get_y_axis_label(self, label_tex, edge=UP, direction=DR, **kwargs):
        return self.get_axis_label(
            label_tex, self.get_y_axis(), edge, direction, **kwargs
        )

    def get_axis_label(self, label_tex, axis, edge, direction, buff=MED_SMALL_BUFF):
        label = MathTex(label_tex)
        label.next_to(axis.get_edge_center(edge), direction, buff=buff)
        label.shift_onto_screen(buff=MED_SMALL_BUFF)
        return label

    def get_axis_labels(self, x_label_tex="x", y_label_tex="y"):
        self.axis_labels = VGroup(
            self.get_x_axis_label(x_label_tex),
            self.get_y_axis_label(y_label_tex),
        )
        return self.axis_labels

    def get_graph(self, function, **kwargs):
        x_min = kwargs.pop("x_min", self.x_min)
        x_max = kwargs.pop("x_max", self.x_max)
        graph = ParametricFunction(
            lambda t: self.coords_to_point(t, function(t)),
            t_min=x_min,
            t_max=x_max,
            **kwargs,
        )
        graph.underlying_function = function
        return graph

    def get_parametric_curve(self, function, **kwargs):
        dim = self.dimension
        graph = ParametricFunction(
            lambda t: self.coords_to_point(*function(t)[:dim]), **kwargs
        )
        graph.underlying_function = function
        return graph

    def input_to_graph_point(self, x, graph):
        if hasattr(graph, "underlying_function"):
            return self.coords_to_point(x, graph.underlying_function(x))
        else:
            alpha = binary_search(
                function=lambda a: self.point_to_coords(graph.point_from_proportion(a))[
                    0
                ],
                target=x,
                lower_bound=self.x_min,
                upper_bound=self.x_max,
            )
            if alpha is not None:
                return graph.point_from_proportion(alpha)
            else:
                return None


class Axes(VGroup, CoordinateSystem):
    CONFIG = {
        "axis_config": {
            "color": LIGHT_GREY,
            "include_tip": True,
            "exclude_zero_from_default_numbers": True,
        },
        "x_axis_config": {},
        "y_axis_config": {"label_direction": LEFT},
        "center_point": ORIGIN,
    }

    def __init__(self, **kwargs):
        CoordinateSystem.__init__(self)
        VGroup.__init__(self, **kwargs)
        self.x_axis = self.create_axis(self.x_min, self.x_max, self.x_axis_config)
        self.y_axis = self.create_axis(self.y_min, self.y_max, self.y_axis_config)
        self.y_axis.rotate(90 * DEGREES, about_point=ORIGIN)
        # Add as a separate group in case various other
        # mobjects are added to self, as for example in
        # NumberPlane below
        self.axes = VGroup(self.x_axis, self.y_axis)
        self.add(*self.axes)
        self.shift(self.center_point)

    def create_axis(self, min_val, max_val, axis_config):
        new_config = merge_dicts_recursively(
            self.axis_config,
            {"x_min": min_val, "x_max": max_val},
            axis_config,
        )
        return NumberLine(**new_config)

    def coords_to_point(self, *coords):
        origin = self.x_axis.number_to_point(0)
        result = np.array(origin)
        for axis, coord in zip(self.get_axes(), coords):
            result += axis.number_to_point(coord) - origin
        return result

    def c2p(self, *coords):
        return self.coords_to_point(*coords)

    def point_to_coords(self, point):
        return tuple([axis.point_to_number(point) for axis in self.get_axes()])

    def p2c(self, point):
        return self.point_to_coords(point)

    def get_axes(self):
        return self.axes

    def get_coordinate_labels(self, x_vals=None, y_vals=None):
        if x_vals is None:
            x_vals = []
        if y_vals is None:
            y_vals = []
        x_mobs = self.get_x_axis().get_number_mobjects(*x_vals)
        y_mobs = self.get_y_axis().get_number_mobjects(*y_vals)

        self.coordinate_labels = VGroup(x_mobs, y_mobs)
        return self.coordinate_labels

    def add_coordinates(self, x_vals=None, y_vals=None):
        self.add(self.get_coordinate_labels(x_vals, y_vals))
        return self


class ThreeDAxes(Axes):
    CONFIG = {
        "z_axis_config": {},
        "z_min": -3.5,
        "z_max": 3.5,
        "z_normal": DOWN,
        "num_axis_pieces": 20,
        "light_source": 9 * DOWN + 7 * LEFT + 10 * OUT,
    }

    def __init__(self, **kwargs):
        self.x_min = -5.5
        self.x_max = 5.5
        self.y_min = -5.5
        self.y_max = 5.5
        Axes.__init__(self, **kwargs)
        self.dimension = 3
        z_axis = self.z_axis = self.create_axis(
            self.z_min, self.z_max, self.z_axis_config
        )
        z_axis.rotate(-np.pi / 2, UP, about_point=ORIGIN)
        z_axis.rotate(angle_of_vector(self.z_normal), OUT, about_point=ORIGIN)
        self.axes.add(z_axis)
        self.add(z_axis)

        self.add_3d_pieces()
        self.set_axis_shading()

    def add_3d_pieces(self):
        for axis in self.axes:
            axis.pieces = VGroup(*axis.get_pieces(self.num_axis_pieces))
            axis.add(axis.pieces)
            axis.set_stroke(width=0, family=False)
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


class NumberPlane(Axes):
    CONFIG = {
        "axis_config": {
            "stroke_color": WHITE,
            "stroke_width": 2,
            "include_ticks": False,
            "include_tip": False,
            "line_to_number_buff": SMALL_BUFF,
            "label_direction": DR,
            "number_scale_val": 0.5,
        },
        "y_axis_config": {"label_direction": DR},
        "background_line_style": {
            "stroke_color": BLUE_D,
            "stroke_width": 2,
            "stroke_opacity": 1,
        },
        # Defaults to a faded version of line_config
        "faded_line_style": None,
        "x_line_frequency": 1,
        "y_line_frequency": 1,
        "faded_line_ratio": 1,
        "make_smooth_after_applying_functions": True,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_background_lines()

    def init_background_lines(self):
        """Will init all the lines of NumberPlanes (faded or not)"""
        if self.faded_line_style is None:
            style = dict(self.background_line_style)
            # For anything numerical, like stroke_width
            # and stroke_opacity, chop it in half
            for key in style:
                if isinstance(style[key], numbers.Number):
                    style[key] *= 0.5
            self.faded_line_style = style

        self.background_lines, self.faded_lines = self.get_lines()
        self.background_lines.set_style(
            **self.background_line_style,
        )
        self.faded_lines.set_style(
            **self.faded_line_style,
        )
        self.add_to_back(
            self.faded_lines,
            self.background_lines,
        )

    def get_lines(self):
        """Generate all the lines, faded and not faded. Two sets of lines are generated: one parallel to the X-axis, and parallel to the Y-axis.

        Returns
        -------
        Tuple[:class:`~.VGroup`, :class:`~.VGroup`]
            The first (i.e the non faded lines) and second (i.e the faded lines) sets of lines, respectively.
        """
        x_axis = self.get_x_axis()
        y_axis = self.get_y_axis()
        x_freq = self.x_line_frequency
        y_freq = self.y_line_frequency

        x_lines1, x_lines2 = self.get_lines_parallel_to_axis(
            x_axis,
            y_axis,
            x_freq,
            self.faded_line_ratio,
        )
        y_lines1, y_lines2 = self.get_lines_parallel_to_axis(
            y_axis,
            x_axis,
            y_freq,
            self.faded_line_ratio,
        )
        lines1 = VGroup(*x_lines1, *y_lines1)
        lines2 = VGroup(*x_lines2, *y_lines2)
        return lines1, lines2

    def get_lines_parallel_to_axis(
        self, axis_parallel_to, axis_perpendicular_to, freq, ratio_faded_lines
    ):
        """Generate a set of lines parallel to an axis.

        Parameters
        ----------
        axis_parallel_to : :class:`~.Line`
            The axis with which the lines will be parallel.

        axis_perpendicular_to : :class:`~.Line`
            The axis with which the lines will be perpendicular.

        ratio_faded_lines : :class:`float`
            The ratio between the space between faded lines and the space between non-faded lines.

        freq : :class:`float`
            Frequency of non-faded lines (number of non-faded lines per graph unit).

        Returns
        -------
        Tuple[:class:`~.VGroup`, :class:`~.VGroup`]
            The first (i.e the non-faded lines parallel to `axis_parallel_to`) and second (i.e the faded lines parallel to `axis_parallel_to`) sets of lines, respectively.
        """
        line = Line(axis_parallel_to.get_start(), axis_parallel_to.get_end())
        if ratio_faded_lines == 0:  # don't show faded lines
            ratio_faded_lines = 1  # i.e. set ratio to 1
        step = (1 / ratio_faded_lines) * freq
        lines1 = VGroup()
        lines2 = VGroup()
        unit_vector_axis_perp_to = axis_perpendicular_to.get_unit_vector()
        ranges = (
            np.arange(0, axis_perpendicular_to.x_max, step),
            np.arange(0, axis_perpendicular_to.x_min, -step),
        )
        for inputs in ranges:
            for k, x in enumerate(inputs):
                new_line = line.copy()
                new_line.shift(unit_vector_axis_perp_to * x)
                if k % ratio_faded_lines == 0:
                    lines1.add(new_line)
                else:
                    lines2.add(new_line)
        return lines1, lines2

    def get_center_point(self):
        return self.coords_to_point(0, 0)

    def get_x_unit_size(self):
        return self.get_x_axis().get_unit_size()

    def get_y_unit_size(self):
        return self.get_x_axis().get_unit_size()

    def get_axes(self):
        return self.axes

    def get_vector(self, coords, **kwargs):
        kwargs["buff"] = 0
        return Arrow(
            self.coords_to_point(0, 0), self.coords_to_point(*coords), **kwargs
        )

    def prepare_for_nonlinear_transform(self, num_inserted_curves=50):
        for mob in self.family_members_with_points():
            num_curves = mob.get_num_curves()
            if num_inserted_curves > num_curves:
                mob.insert_n_curves(num_inserted_curves - num_curves)
        return self


class ComplexPlane(NumberPlane):
    CONFIG = {
        "color": BLUE,
        "line_frequency": 1,
    }

    def number_to_point(self, number):
        number = complex(number)
        return self.coords_to_point(number.real, number.imag)

    def n2p(self, number):
        return self.number_to_point(number)

    def point_to_number(self, point):
        x, y = self.point_to_coords(point)
        return complex(x, y)

    def p2n(self, point):
        return self.point_to_number(point)

    def get_default_coordinate_values(self):
        x_numbers = self.get_x_axis().default_numbers_to_display()
        y_numbers = self.get_y_axis().default_numbers_to_display()
        y_numbers = [complex(0, y) for y in y_numbers if y != 0]
        return [*x_numbers, *y_numbers]

    def get_coordinate_labels(self, *numbers, **kwargs):
        if len(numbers) == 0:
            numbers = self.get_default_coordinate_values()

        self.coordinate_labels = VGroup()
        for number in numbers:
            z = complex(number)
            if abs(z.imag) > abs(z.real):
                axis = self.get_y_axis()
                value = z.imag
                kwargs = merge_dicts_recursively(
                    kwargs,
                    {"number_config": {"unit": "i"}},
                )
            else:
                axis = self.get_x_axis()
                value = z.real
            number_mob = axis.get_number_mobject(value, **kwargs)
            self.coordinate_labels.add(number_mob)
        return self.coordinate_labels

    def add_coordinates(self, *numbers):
        self.add(self.get_coordinate_labels(*numbers))
        return self
