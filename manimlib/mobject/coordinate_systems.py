from __future__ import annotations

import numbers
from abc import abstractmethod
from typing import Type, TypeVar, Union, Callable, Iterable, Sequence

import numpy as np

from manimlib.constants import *
from manimlib.mobject.functions import ParametricCurve
from manimlib.mobject.geometry import Arrow
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import DashedLine
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.number_line import NumberLine
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.config_ops import digest_config
from manimlib.utils.config_ops import merge_dicts_recursively
from manimlib.utils.simple_functions import binary_search
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import rotate_vector

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import colour
    from manimlib.mobject.mobject import Mobject
    T = TypeVar("T", bound=Mobject)
    ManimColor = Union[str, colour.Color, Sequence[float]]


EPSILON = 1e-8


class CoordinateSystem():
    """
    Abstract class for Axes and NumberPlane
    """
    CONFIG = {
        "dimension": 2,
        "default_x_range": [-8.0, 8.0, 1.0],
        "default_y_range": [-4.0, 4.0, 1.0],
        "width": FRAME_WIDTH,
        "height": FRAME_HEIGHT,
        "num_sampled_graph_points_per_tick": 20,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.x_range = np.array(self.default_x_range)
        self.y_range = np.array(self.default_y_range)

    @abstractmethod
    def coords_to_point(self, *coords: float) -> np.ndarray:
        raise Exception("Not implemented")

    @abstractmethod
    def point_to_coords(self, point: np.ndarray) -> tuple[float, ...]:
        raise Exception("Not implemented")

    def c2p(self, *coords: float):
        """Abbreviation for coords_to_point"""
        return self.coords_to_point(*coords)

    def p2c(self, point: np.ndarray):
        """Abbreviation for point_to_coords"""
        return self.point_to_coords(point)

    def get_origin(self) -> np.ndarray:
        return self.c2p(*[0] * self.dimension)

    @abstractmethod
    def get_axes(self) -> VGroup:
        raise Exception("Not implemented")

    @abstractmethod
    def get_all_ranges(self) -> list[np.ndarray]:
        raise Exception("Not implemented")

    def get_axis(self, index: int) -> NumberLine:
        return self.get_axes()[index]

    def get_x_axis(self) -> NumberLine:
        return self.get_axis(0)

    def get_y_axis(self) -> NumberLine:
        return self.get_axis(1)

    def get_z_axis(self) -> NumberLine:
        return self.get_axis(2)

    def get_x_axis_label(
        self,
        label_tex: str,
        edge: np.ndarray = RIGHT,
        direction: np.ndarray = DL,
        **kwargs
    ) -> Tex:
        return self.get_axis_label(
            label_tex, self.get_x_axis(),
            edge, direction, **kwargs
        )

    def get_y_axis_label(
        self,
        label_tex: str,
        edge: np.ndarray = UP,
        direction: np.ndarray = DR,
        **kwargs
    ) -> Tex:
        return self.get_axis_label(
            label_tex, self.get_y_axis(),
            edge, direction, **kwargs
        )

    def get_axis_label(
        self,
        label_tex: str,
        axis: np.ndarray,
        edge: np.ndarray,
        direction: np.ndarray,
        buff: float = MED_SMALL_BUFF
    ) -> Tex:
        label = Tex(label_tex)
        label.next_to(
            axis.get_edge_center(edge), direction,
            buff=buff
        )
        label.shift_onto_screen(buff=MED_SMALL_BUFF)
        return label

    def get_axis_labels(
        self,
        x_label_tex: str = "x",
        y_label_tex: str = "y"
    ) -> VGroup:
        self.axis_labels = VGroup(
            self.get_x_axis_label(x_label_tex),
            self.get_y_axis_label(y_label_tex),
        )
        return self.axis_labels

    def get_line_from_axis_to_point(
        self, 
        index: int,
        point: np.ndarray,
        line_func: Type[T] = DashedLine,
        color: ManimColor = GREY_A,
        stroke_width: float = 2
    ) -> T:
        axis = self.get_axis(index)
        line = line_func(axis.get_projection(point), point)
        line.set_stroke(color, stroke_width)
        return line

    def get_v_line(self, point: np.ndarray, **kwargs):
        return self.get_line_from_axis_to_point(0, point, **kwargs)

    def get_h_line(self, point: np.ndarray, **kwargs):
        return self.get_line_from_axis_to_point(1, point, **kwargs)

    # Useful for graphing
    def get_graph(
        self,
        function: Callable[[float], float],
        x_range: Sequence[float] | None = None,
        **kwargs
    ) -> ParametricCurve:
        t_range = np.array(self.x_range, dtype=float)
        if x_range is not None:
            t_range[:len(x_range)] = x_range
        # For axes, the third coordinate of x_range indicates
        # tick frequency.  But for functions, it indicates a
        # sample frequency
        if x_range is None or len(x_range) < 3:
            t_range[2] /= self.num_sampled_graph_points_per_tick

        graph = ParametricCurve(
            lambda t: self.c2p(t, function(t)),
            t_range=t_range,
            **kwargs
        )
        graph.underlying_function = function
        graph.x_range = x_range
        return graph

    def get_parametric_curve(
        self,
        function: Callable[[float], np.ndarray],
        **kwargs
    ) -> ParametricCurve:
        dim = self.dimension
        graph = ParametricCurve(
            lambda t: self.coords_to_point(*function(t)[:dim]),
            **kwargs
        )
        graph.underlying_function = function
        return graph

    def input_to_graph_point(
        self,
        x: float,
        graph: ParametricCurve
    ) -> np.ndarray | None:
        if hasattr(graph, "underlying_function"):
            return self.coords_to_point(x, graph.underlying_function(x))
        else:
            alpha = binary_search(
                function=lambda a: self.point_to_coords(
                    graph.quick_point_from_proportion(a)
                )[0],
                target=x,
                lower_bound=self.x_range[0],
                upper_bound=self.x_range[1],
            )
            if alpha is not None:
                return graph.quick_point_from_proportion(alpha)
            else:
                return None

    def i2gp(self, x: float, graph: ParametricCurve) -> np.ndarray | None:
        """
        Alias for input_to_graph_point
        """
        return self.input_to_graph_point(x, graph)

    def get_graph_label(
        self,
        graph: ParametricCurve,
        label: str | Mobject = "f(x)",
        x: float | None = None,
        direction: np.ndarray = RIGHT,
        buff: float = MED_SMALL_BUFF,
        color: ManimColor | None = None
    ) -> Tex | Mobject:
        if isinstance(label, str):
            label = Tex(label)
        if color is None:
            label.match_color(graph)
        if x is None:
            # Searching from the right, find a point
            # whose y value is in bounds
            max_y = FRAME_Y_RADIUS - label.get_height()
            max_x = FRAME_X_RADIUS - label.get_width()
            for x0 in np.arange(*self.x_range)[::-1]:
                pt = self.i2gp(x0, graph)
                if abs(pt[0]) < max_x and abs(pt[1]) < max_y:
                    x = x0
                    break
            if x is None:
                x = self.x_range[1]

        point = self.input_to_graph_point(x, graph)
        angle = self.angle_of_tangent(x, graph)
        normal = rotate_vector(RIGHT, angle + 90 * DEGREES)
        if normal[1] < 0:
            normal *= -1
        label.next_to(point, normal, buff=buff)
        label.shift_onto_screen()
        return label

    def get_v_line_to_graph(self, x: float, graph: ParametricCurve, **kwargs):
        return self.get_v_line(self.i2gp(x, graph), **kwargs)

    def get_h_line_to_graph(self, x: float, graph: ParametricCurve, **kwargs):
        return self.get_h_line(self.i2gp(x, graph), **kwargs)

    # For calculus
    def angle_of_tangent(
        self,
        x: float,
        graph: ParametricCurve,
        dx: float = EPSILON
    ) -> float:
        p0 = self.input_to_graph_point(x, graph)
        p1 = self.input_to_graph_point(x + dx, graph)
        return angle_of_vector(p1 - p0)

    def slope_of_tangent(
        self,
        x: float,
        graph: ParametricCurve,
        **kwargs
    ) -> float:
        return np.tan(self.angle_of_tangent(x, graph, **kwargs))

    def get_tangent_line(
        self,
        x: float,
        graph: ParametricCurve,
        length: float = 5,
        line_func: Type[T] = Line
    ) -> T:
        line = line_func(LEFT, RIGHT)
        line.set_width(length)
        line.rotate(self.angle_of_tangent(x, graph))
        line.move_to(self.input_to_graph_point(x, graph))
        return line

    def get_riemann_rectangles(
        self,
        graph: ParametricCurve,
        x_range: Sequence[float] = None,
        dx: float | None = None,
        input_sample_type: str = "left",
        stroke_width: float = 1,
        stroke_color: ManimColor = BLACK,
        fill_opacity: float = 1,
        colors: Iterable[ManimColor] = (BLUE, GREEN),
        show_signed_area: bool = True
    ) -> VGroup:
        if x_range is None:
            x_range = self.x_range[:2]
        if dx is None:
            dx = self.x_range[2]
        if len(x_range) < 3:
            x_range = [*x_range, dx]

        rects = []
        xs = np.arange(*x_range)
        for x0, x1 in zip(xs, xs[1:]):
            if input_sample_type == "left":
                sample = x0
            elif input_sample_type == "right":
                sample = x1
            elif input_sample_type == "center":
                sample = 0.5 * x0 + 0.5 * x1
            else:
                raise Exception("Invalid input sample type")
            height = get_norm(
                self.i2gp(sample, graph) - self.c2p(sample, 0)
            )
            rect = Rectangle(width=x1 - x0, height=height)
            rect.move_to(self.c2p(x0, 0), DL)
            rects.append(rect)
        result = VGroup(*rects)
        result.set_submobject_colors_by_gradient(*colors)
        result.set_style(
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            fill_opacity=fill_opacity,
        )
        return result

    def get_area_under_graph(self, graph, x_range, fill_color=BLUE, fill_opacity=1):
        # TODO
        pass


class Axes(VGroup, CoordinateSystem):
    CONFIG = {
        "axis_config": {
            "include_tip": False,
            "numbers_to_exclude": [0],
        },
        "x_axis_config": {},
        "y_axis_config": {
            "line_to_number_direction": LEFT,
        },
        "height": FRAME_HEIGHT - 2,
        "width": FRAME_WIDTH - 2,
    }

    def __init__(
        self,
        x_range: Sequence[float] | None = None,
        y_range: Sequence[float] | None = None,
        **kwargs
    ):
        CoordinateSystem.__init__(self, **kwargs)
        VGroup.__init__(self, **kwargs)

        if x_range is not None:
            self.x_range[:len(x_range)] = x_range
        if y_range is not None:
            self.y_range[:len(y_range)] = y_range

        self.x_axis = self.create_axis(
            self.x_range, self.x_axis_config, self.width,
        )
        self.y_axis = self.create_axis(
            self.y_range, self.y_axis_config, self.height
        )
        self.y_axis.rotate(90 * DEGREES, about_point=ORIGIN)
        # Add as a separate group in case various other
        # mobjects are added to self, as for example in
        # NumberPlane below
        self.axes = VGroup(self.x_axis, self.y_axis)
        self.add(*self.axes)
        self.center()

    def create_axis(
        self,
        range_terms: Sequence[float],
        axis_config: dict[str],
        length: float
    ) -> NumberLine:
        new_config = merge_dicts_recursively(self.axis_config, axis_config)
        new_config["width"] = length
        axis = NumberLine(range_terms, **new_config)
        axis.shift(-axis.n2p(0))
        return axis

    def coords_to_point(self, *coords: float) -> np.ndarray:
        origin = self.x_axis.number_to_point(0)
        result = origin.copy()
        for axis, coord in zip(self.get_axes(), coords):
            result += (axis.number_to_point(coord) - origin)
        return result

    def point_to_coords(self, point: np.ndarray) -> tuple[float, ...]:
        return tuple([
            axis.point_to_number(point)
            for axis in self.get_axes()
        ])

    def get_axes(self) -> VGroup:
        return self.axes

    def get_all_ranges(self) -> list[Sequence[float]]:
        return [self.x_range, self.y_range]

    def add_coordinate_labels(
        self,
        x_values: Iterable[float] | None = None,
        y_values: Iterable[float] | None = None,
        **kwargs
    ) -> VGroup:
        axes = self.get_axes()
        self.coordinate_labels = VGroup()
        for axis, values in zip(axes, [x_values, y_values]):
            labels = axis.add_numbers(values, **kwargs)
            self.coordinate_labels.add(labels)
        return self.coordinate_labels


class ThreeDAxes(Axes):
    CONFIG = {
        "dimension": 3,
        "x_range": np.array([-6.0, 6.0, 1.0]),
        "y_range": np.array([-5.0, 5.0, 1.0]),
        "z_range": np.array([-4.0, 4.0, 1.0]),
        "z_axis_config": {},
        "z_normal": DOWN,
        "height": None,
        "width": None,
        "depth": None,
        "num_axis_pieces": 20,
        "gloss": 0.5,
    }

    def __init__(
        self,
        x_range: Sequence[float] | None = None,
        y_range: Sequence[float] | None = None,
        z_range: Sequence[float] | None = None,
        **kwargs
    ):
        Axes.__init__(self, x_range, y_range, **kwargs)
        if z_range is not None:
            self.z_range[:len(z_range)] = z_range

        z_axis = self.create_axis(
            self.z_range,
            self.z_axis_config,
            self.depth,
        )
        z_axis.rotate(-PI / 2, UP, about_point=ORIGIN)
        z_axis.rotate(
            angle_of_vector(self.z_normal), OUT,
            about_point=ORIGIN
        )
        z_axis.shift(self.x_axis.n2p(0))
        self.axes.add(z_axis)
        self.add(z_axis)
        self.z_axis = z_axis

        for axis in self.axes:
            axis.insert_n_curves(self.num_axis_pieces - 1)

    def get_all_ranges(self) -> list[Sequence[float]]:
        return [self.x_range, self.y_range, self.z_range]


class NumberPlane(Axes):
    CONFIG = {
        "axis_config": {
            "stroke_color": WHITE,
            "stroke_width": 2,
            "include_ticks": False,
            "include_tip": False,
            "line_to_number_buff": SMALL_BUFF,
            "line_to_number_direction": DL,
        },
        "y_axis_config": {
            "line_to_number_direction": DL,
        },
        "background_line_style": {
            "stroke_color": BLUE_D,
            "stroke_width": 2,
            "stroke_opacity": 1,
        },
        "height": None,
        "width": None,
        # Defaults to a faded version of line_config
        "faded_line_style": None,
        "faded_line_ratio": 4,
        "make_smooth_after_applying_functions": True,
    }

    def __init__(
        self,
        x_range: Sequence[float] | None = None,
        y_range: Sequence[float] | None = None,
        **kwargs
    ):
        super().__init__(x_range, y_range, **kwargs)
        self.init_background_lines()

    def init_background_lines(self) -> None:
        if self.faded_line_style is None:
            style = dict(self.background_line_style)
            # For anything numerical, like stroke_width
            # and stroke_opacity, chop it in half
            for key in style:
                if isinstance(style[key], numbers.Number):
                    style[key] *= 0.5
            self.faded_line_style = style

        self.background_lines, self.faded_lines = self.get_lines()
        self.background_lines.set_style(**self.background_line_style)
        self.faded_lines.set_style(**self.faded_line_style)
        self.add_to_back(
            self.faded_lines,
            self.background_lines,
        )

    def get_lines(self) -> tuple[VGroup, VGroup]:
        x_axis = self.get_x_axis()
        y_axis = self.get_y_axis()

        x_lines1, x_lines2 = self.get_lines_parallel_to_axis(x_axis, y_axis)
        y_lines1, y_lines2 = self.get_lines_parallel_to_axis(y_axis, x_axis)
        lines1 = VGroup(*x_lines1, *y_lines1)
        lines2 = VGroup(*x_lines2, *y_lines2)
        return lines1, lines2

    def get_lines_parallel_to_axis(
        self,
        axis1: NumberLine,
        axis2: NumberLine
    ) -> tuple[VGroup, VGroup]:
        freq = axis2.x_step
        ratio = self.faded_line_ratio
        line = Line(axis1.get_start(), axis1.get_end())
        dense_freq = (1 + ratio)
        step = (1 / dense_freq) * freq

        lines1 = VGroup()
        lines2 = VGroup()
        inputs = np.arange(axis2.x_min, axis2.x_max + step, step)
        for i, x in enumerate(inputs):
            new_line = line.copy()
            new_line.shift(axis2.n2p(x) - axis2.n2p(0))
            if i % (1 + ratio) == 0:
                lines1.add(new_line)
            else:
                lines2.add(new_line)
        return lines1, lines2

    def get_x_unit_size(self) -> float:
        return self.get_x_axis().get_unit_size()

    def get_y_unit_size(self) -> list:
        return self.get_x_axis().get_unit_size()

    def get_axes(self) -> VGroup:
        return self.axes

    def get_vector(self, coords: Iterable[float], **kwargs) -> Arrow:
        kwargs["buff"] = 0
        return Arrow(self.c2p(0, 0), self.c2p(*coords), **kwargs)

    def prepare_for_nonlinear_transform(self, num_inserted_curves: int = 50):
        for mob in self.family_members_with_points():
            num_curves = mob.get_num_curves()
            if num_inserted_curves > num_curves:
                mob.insert_n_curves(num_inserted_curves - num_curves)
            mob.make_smooth_after_applying_functions = True
        return self


class ComplexPlane(NumberPlane):
    CONFIG = {
        "color": BLUE,
        "line_frequency": 1,
    }

    def number_to_point(self, number: complex | float) -> np.ndarray:
        number = complex(number)
        return self.coords_to_point(number.real, number.imag)

    def n2p(self, number: complex | float) -> np.ndarray:
        return self.number_to_point(number)

    def point_to_number(self, point: np.ndarray) -> complex:
        x, y = self.point_to_coords(point)
        return complex(x, y)

    def p2n(self, point: np.ndarray) -> complex:
        return self.point_to_number(point)

    def get_default_coordinate_values(
        self,
        skip_first: bool = True
    ) -> list[complex]:
        x_numbers = self.get_x_axis().get_tick_range()[1:]
        y_numbers = self.get_y_axis().get_tick_range()[1:]
        y_numbers = [complex(0, y) for y in y_numbers if y != 0]
        return [*x_numbers, *y_numbers]

    def add_coordinate_labels(
        self,
        numbers: list[complex] | None = None,
        skip_first: bool = True,
        **kwargs
    ):
        if numbers is None:
            numbers = self.get_default_coordinate_values(skip_first)

        self.coordinate_labels = VGroup()
        for number in numbers:
            z = complex(number)
            if abs(z.imag) > abs(z.real):
                axis = self.get_y_axis()
                value = z.imag
                kwargs["unit"] = "i"
            else:
                axis = self.get_x_axis()
                value = z.real
            number_mob = axis.get_number_mobject(value, **kwargs)
            # For i and -i, remove the "1"
            if z.imag == 1:
                number_mob.remove(number_mob[0])
            if z.imag == -1:
                number_mob.remove(number_mob[1])
                number_mob[0].next_to(
                    number_mob[1], LEFT,
                    buff=number_mob[0].get_width() / 4
                )
            self.coordinate_labels.add(number_mob)
        self.add(self.coordinate_labels)
        return self
