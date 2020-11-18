"""A scene for plotting / graphing functions.

Examples
--------

.. manim:: FunctionPlotWithLabbeledYAxis
    :save_last_frame:

    class FunctionPlotWithLabbeledYAxis(GraphScene):
        CONFIG = {
            "y_min": 0,
            "y_max": 100,
            "y_axis_config": {"tick_frequency": 10},
            "y_labeled_nums": np.arange(0, 100, 10)
        }

        def construct(self):
            self.setup_axes()
            dot = Dot().move_to(self.coords_to_point(PI / 2, 20))
            func_graph = self.get_graph(lambda x: 20 * np.sin(x))
            self.add(dot,func_graph)


.. manim:: GaussianFunctionPlot
    :save_last_frame:

    amp = 5
    mu = 3
    sig = 1

    def gaussian(x):
        return amp * np.exp((-1 / 2 * ((x - mu) / sig) ** 2))

    class GaussianFunctionPlot(GraphScene):
        def construct(self):
            self.setup_axes()
            graph = self.get_graph(gaussian, x_min=-1, x_max=10)
            graph.set_stroke(width=5)
            self.add(graph)

"""

__all__ = ["GraphScene"]


import itertools as it

from .. import config
from ..animation.creation import Write, DrawBorderThenFill, ShowCreation
from ..animation.transform import Transform
from ..animation.update import UpdateFromAlphaFunc
from ..constants import *
from ..mobject.functions import ParametricFunction
from ..mobject.geometry import Line
from ..mobject.geometry import Rectangle
from ..mobject.geometry import RegularPolygon
from ..mobject.number_line import NumberLine
from ..mobject.svg.tex_mobject import MathTex
from ..mobject.svg.tex_mobject import Tex
from ..mobject.types.vectorized_mobject import VGroup
from ..mobject.types.vectorized_mobject import VectorizedPoint
from ..scene.scene import Scene
from ..utils.bezier import interpolate
from ..utils.color import color_gradient, GREY, BLUE, GREEN, YELLOW, BLACK, WHITE
from ..utils.color import invert_color
from ..utils.space_ops import angle_of_vector

# TODO, this should probably reimplemented entirely, especially so as to
# better reuse code from mobject/coordinate_systems.
# Also, I really dislike how the configuration is set up, this
# is way too messy to work with.


class GraphScene(Scene):
    CONFIG = {
        "x_min": -1,
        "x_max": 10,
        "x_axis_width": 9,
        "x_leftmost_tick": None,  # Change if different from x_min
        "x_labeled_nums": None,
        "x_axis_label": "$x$",
        "y_min": -1,
        "y_max": 10,
        "y_axis_height": 6,
        "y_bottom_tick": None,  # Change if different from y_min
        "y_labeled_nums": None,
        "y_axis_label": "$y$",
        "axes_color": GREY,
        "graph_origin": 2.5 * DOWN + 4 * LEFT,
        "exclude_zero_label": True,
        "default_graph_colors": [BLUE, GREEN, YELLOW],
        "default_derivative_color": GREEN,
        "default_input_color": YELLOW,
        "default_riemann_start_color": BLUE,
        "default_riemann_end_color": GREEN,
        "area_opacity": 0.8,
        "num_rects": 50,
        "include_tip": False,  # add tip at the end of the axes
        "x_axis_visibility": True,  # show or hide the x axis
        "y_axis_visibility": True,  # show or hide the y axis
        "x_label_position": UP + RIGHT,  # where to place the label of the x axis
        "y_label_position": UP + RIGHT,  # where to place the label of the y axis
        "x_axis_config": {},
        "y_axis_config": {},
    }

    def setup(self):
        """
        This method is used internally by Manim
        to set up the scene for proper use.
        """
        self.default_graph_colors_cycle = it.cycle(self.default_graph_colors)

        self.left_T_label = VGroup()
        self.left_v_line = VGroup()
        self.right_T_label = VGroup()
        self.right_v_line = VGroup()

    def setup_axes(self, animate=False):
        """
        This method sets up the axes of the graph.

        Parameters
        ----------
        animate : bool, optional
            Whether or not to animate the setting up of the Axes.
        """
        # TODO, once eoc is done, refactor this to be less redundant.
        x_num_range = float(self.x_max - self.x_min)
        self.space_unit_to_x = self.x_axis_width / x_num_range
        if self.x_labeled_nums is None:
            self.x_labeled_nums = []
        if self.x_leftmost_tick is None:
            self.x_leftmost_tick = self.x_min

        # The dictionary we update here are sensible defaults
        # that can be overridden through x_axis_config
        self.x_axis_config = dict(
            {
                "x_min": self.x_min,
                "x_max": self.x_max,
                "unit_size": self.space_unit_to_x,
                "leftmost_tick": self.x_leftmost_tick,
                "numbers_with_elongated_ticks": self.x_labeled_nums,
                "color": self.axes_color,
                "include_tip": self.include_tip,
            },
            **self.x_axis_config,
        )

        x_axis = NumberLine(**self.x_axis_config)
        x_shift = x_axis.number_to_point(
            0 if self.x_min <= 0 <= self.x_max else self.x_min
        )
        x_axis.shift(self.graph_origin - x_shift)
        if len(self.x_labeled_nums) > 0:
            if self.exclude_zero_label:
                self.x_labeled_nums = [x for x in self.x_labeled_nums if x != 0]
            x_axis.add_numbers(*self.x_labeled_nums)
        if self.x_axis_label:
            x_label = Tex(self.x_axis_label)
            x_label.next_to(
                x_axis.get_corner(self.x_label_position),
                self.x_label_position,
                buff=SMALL_BUFF,
            )
            x_axis.add(x_label)
            self.x_axis_label_mob = x_label

        y_num_range = float(self.y_max - self.y_min)
        self.space_unit_to_y = self.y_axis_height / y_num_range

        if self.y_labeled_nums is None:
            self.y_labeled_nums = []
        if self.y_bottom_tick is None:
            self.y_bottom_tick = self.y_min

        # The dictionary we update here are sensible defaults
        # that can be overridden through y_axis_config
        self.y_axis_config = dict(
            {
                "x_min": self.y_min,
                "x_max": self.y_max,
                "unit_size": self.space_unit_to_y,
                "leftmost_tick": self.y_bottom_tick,
                "numbers_with_elongated_ticks": self.y_labeled_nums,
                "color": self.axes_color,
                "line_to_number_vect": LEFT,
                "label_direction": LEFT,
                "include_tip": self.include_tip,
            },
            **self.y_axis_config,
        )

        y_axis = NumberLine(**self.y_axis_config)
        y_shift = y_axis.number_to_point(
            0 if self.y_min <= 0 <= self.y_max else self.y_min
        )
        y_axis.shift(self.graph_origin - y_shift)
        y_axis.rotate(np.pi / 2, about_point=self.graph_origin)
        if len(self.y_labeled_nums) > 0:
            if self.exclude_zero_label:
                self.y_labeled_nums = [y for y in self.y_labeled_nums if y != 0]
            y_axis.add_numbers(*self.y_labeled_nums)
        if self.y_axis_label:
            y_label = Tex(self.y_axis_label)
            y_label.next_to(
                y_axis.get_corner(self.y_label_position),
                self.y_label_position,
                buff=SMALL_BUFF,
            )
            y_axis.add(y_label)
            self.y_axis_label_mob = y_label

        axes = []
        if self.x_axis_visibility:
            axes.append(x_axis)
        if self.y_axis_visibility:
            axes.append(y_axis)

        if animate:
            self.play(Write(VGroup(*axes)))
        else:
            self.add(*axes)
        self.x_axis, self.y_axis = self.axes = VGroup(x_axis, y_axis)
        self.default_graph_colors = it.cycle(self.default_graph_colors)

    def coords_to_point(self, x, y):
        """
        The graph is smaller than the scene.
        Because of this, coordinates in the scene don't map
        to coordinates on the graph.
        This method returns a scaled coordinate for the graph,
        given cartesian coordinates that correspond to the scene..

        Parameters
        ----------
        x : int, float
            The x value

        y : int, float
            The y value

        Returns
        -------
        np.ndarray
            The array of the coordinates.

        Examples
        --------

        .. manim:: SequencePlot
            :save_last_frame:

            class SequencePlot(GraphScene):
                CONFIG = {
                    "y_axis_label": r"Concentration [\%]",
                    "x_axis_label": "Time [s]",
                    }

                def construct(self):
                    data = [1, 2, 2, 4, 4, 1, 3]
                    self.setup_axes()
                    for time, dat in enumerate(data):
                        dot = Dot().move_to(self.coords_to_point(time, dat))
                        self.add(dot)

        """
        assert hasattr(self, "x_axis") and hasattr(self, "y_axis")
        result = self.x_axis.number_to_point(x)[0] * RIGHT
        result += self.y_axis.number_to_point(y)[1] * UP
        return result

    def point_to_coords(self, point):
        """
        The scene is smaller than the graph.

        Because of this, coordinates in the graph don't map
        to coordinates on the scene.

        This method returns a scaled coordinate for the scene,
        given coordinates that correspond to the graph.

        Parameters
        ----------
        point : np.ndarray
            The point on the graph.

        Returns
        -------
        tuple
            The coordinates on the scene.
        """
        return (self.x_axis.point_to_number(point), self.y_axis.point_to_number(point))

    def get_graph(self, func, color=None, x_min=None, x_max=None, **kwargs):
        """
        This method gets a curve to plot on the graph.

        Parameters
        ----------
        func : function
            The function to plot. It's return value should be
            the y-coordinate for a given x-coordinate

        color : str, optional
            The string of the RGB color of the curve. in Hexadecimal representation.

        x_min : int, float, optional
            The lower x_value from which to plot the curve.

        x_max : int, float, optional
            The higher x_value until which to plot the curve.

        **kwargs :
            Any valid keyword arguments of ParametricFunction.

        Return
        ------
        ParametricFunction
            The Parametric Curve for the function passed.

        """
        if color is None:
            color = next(self.default_graph_colors_cycle)
        if x_min is None:
            x_min = self.x_min
        if x_max is None:
            x_max = self.x_max

        def parameterized_function(alpha):
            x = interpolate(x_min, x_max, alpha)
            y = func(x)
            if not np.isfinite(y):
                y = self.y_max
            return self.coords_to_point(x, y)

        graph = ParametricFunction(parameterized_function, color=color, **kwargs)
        graph.underlying_function = func
        return graph

    def input_to_graph_point(self, x, graph):
        """
        This method returns a coordinate on the curve
        given an x_value and a the graoh-curve for which
        the corresponding y value should be found.

        Parameters
        ----------
        x : int, float
            The x value for which to find the y value.

        graph : ParametricFunction
            The ParametricFunction object on which
            the x and y value lie.

        Returns
        -------
        numpy.nparray
            The array of the coordinates on the graph.
        """
        return self.coords_to_point(x, graph.underlying_function(x))

    def angle_of_tangent(self, x, graph, dx=0.01):
        """
        Returns the angle to the x axis of the tangent
        to the plotted curve at a particular x-value.

        Parameters
        ----------
        x : int, float
            The x value at which the tangent must touch the curve.

        graph : ParametricFunction
            The ParametricFunction for which to calculate the tangent.

        dx : int, float, optional
            The small change in x with which a small change in y
            will be compared in order to obtain the tangent.

        Returns
        -------
        float
            The angle of the tangent with the x axis.
        """
        vect = self.input_to_graph_point(x + dx, graph) - self.input_to_graph_point(
            x, graph
        )
        return angle_of_vector(vect)

    def slope_of_tangent(self, *args, **kwargs):
        """
        Returns the slople of the tangent to the plotted curve
        at a particular x-value.

        Parameters
        ----------
        x : int, float
            The x value at which the tangent must touch the curve.

        graph : ParametricFunction
            The ParametricFunction for which to calculate the tangent.

        dx : int, float, optional
            The small change in x with which a small change in y
            will be compared in order to obtain the tangent.

        Returns
        -------
        float
            The slope of the tangent with the x axis.
        """
        return np.tan(self.angle_of_tangent(*args, **kwargs))

    def get_derivative_graph(self, graph, dx=0.01, **kwargs):
        """
        Returns the curve of the derivative of the passed
        graph.

        Parameters
        ----------
        graph : ParametricFunction
            The graph for which the derivative must be found.

        dx : float, int, optional
            The small change in x with which a small change in y
            will be compared in order to obtain the derivative.

        **kwargs
            Any valid keyword argument of ParametricFunction

        Returns
        -------
        ParametricFunction
            The curve of the derivative.
        """
        if "color" not in kwargs:
            kwargs["color"] = self.default_derivative_color

        def deriv(x):
            return self.slope_of_tangent(x, graph, dx) / self.space_unit_to_y

        return self.get_graph(deriv, **kwargs)

    def get_graph_label(
        self,
        graph,
        label="f(x)",
        x_val=None,
        direction=RIGHT,
        buff=MED_SMALL_BUFF,
        color=None,
    ):
        """
        This method returns a properly positioned label for the passed graph,
        styled with the passed parameters.

        Parameters
        ----------
        graph : ParametricFunction
            The curve of the function plotted.

        label : str, optional
            The label for the function's curve.

        x_val : int, float, optional
            The x_value with which the label should be aligned.

        direction : np.ndarray, list, tuple
            The cartesian position, relative to the curve that the label will be at.
            e.g LEFT, RIGHT

        buff : float, int, option
            The buffer space between the curve and the label

        color : str, optional
            The color of the label.

        Returns
        -------
        :class:`~.MathTex`
            The LaTeX of the passed 'label' parameter

        """
        label = MathTex(label)
        color = color or graph.get_color()
        label.set_color(color)
        if x_val is None:
            # Search from right to left
            for x in np.linspace(self.x_max, self.x_min, 100):
                point = self.input_to_graph_point(x, graph)
                if point[1] < config["frame_y_radius"]:
                    break
            x_val = x
        label.next_to(self.input_to_graph_point(x_val, graph), direction, buff=buff)
        label.shift_onto_screen()
        return label

    def get_riemann_rectangles(
        self,
        graph,
        x_min=None,
        x_max=None,
        dx=0.1,
        input_sample_type="left",
        bounded_graph=None,
        stroke_width=1,
        stroke_color=BLACK,
        fill_opacity=1,
        start_color=None,
        end_color=None,
        show_signed_area=True,
        width_scale_factor=1.001,
    ):
        """
        This method returns the VGroup() of the Riemann Rectangles for
        a particular curve.

        Parameters
        ----------
        graph : ParametricFunction
            The graph whose area needs to be approximated
            by the Riemann Rectangles.

        x_min : int, float, optional
            The lower bound from which to start adding rectangles

        x_max : int, float, optional
            The upper bound where the rectangles stop.

        dx : int, float, optional
            The smallest change in x-values that is
            considered significant.

        input_sample_type : {"left", "right", "center"}
            Can be any of "left", "right" or "center

        stroke_width : int, float, optional
            The stroke_width of the border of the rectangles.

        stroke_color : str, optional
            The string of hex colour of the rectangle's border.

        fill_opacity : int, float
            The opacity of the rectangles. Takes values from 0 to 1.

        start_color : str, optional
            The hex starting colour for the rectangles,
            this will, if end_color is a different colour,
            make a nice gradient.

        end_color : str, optional
            The hex ending colour for the rectangles,
            this will, if start_color is a different colour,
            make a nice gradient.

        show_signed_area : bool, optional
            Whether or not to indicate -ve area if curve dips below
            x-axis.

        width_scale_factor : int, float, optional
            How much the width of the rectangles are scaled by when transforming.

        Returns
        -------
        VGroup
            A VGroup containing the Riemann Rectangles.

        """
        x_min = x_min if x_min is not None else self.x_min
        x_max = x_max if x_max is not None else self.x_max
        if start_color is None:
            start_color = self.default_riemann_start_color
        if end_color is None:
            end_color = self.default_riemann_end_color
        rectangles = VGroup()
        x_range = np.arange(x_min, x_max, dx)
        colors = color_gradient([start_color, end_color], len(x_range))
        for x, color in zip(x_range, colors):
            if input_sample_type == "left":
                sample_input = x
            elif input_sample_type == "right":
                sample_input = x + dx
            elif input_sample_type == "center":
                sample_input = x + 0.5 * dx
            else:
                raise ValueError("Invalid input sample type")
            graph_point = self.input_to_graph_point(sample_input, graph)
            if bounded_graph == None:
                y_point = 0
            else:
                y_point = bounded_graph.underlying_function(x)
            points = VGroup(
                *list(
                    map(
                        VectorizedPoint,
                        [
                            self.coords_to_point(x, y_point),
                            self.coords_to_point(x + width_scale_factor * dx, y_point),
                            graph_point,
                        ],
                    )
                )
            )

            rect = Rectangle()
            rect.replace(points, stretch=True)
            if graph_point[1] < self.graph_origin[1] and show_signed_area:
                fill_color = invert_color(color)
            else:
                fill_color = color
            rect.set_fill(fill_color, opacity=fill_opacity)
            rect.set_stroke(stroke_color, width=stroke_width)
            rectangles.add(rect)
        return rectangles

    def get_riemann_rectangles_list(
        self, graph, n_iterations, max_dx=0.5, power_base=2, stroke_width=1, **kwargs
    ):
        """
        This method returns a list of multiple VGroups of Riemann
        Rectangles. The inital VGroups are relatively inaccurate,
        but the closer you get to the end the more accurate the Riemann
        rectangles become

        Parameters
        ----------
        graph : ParametricFunction
            The graph whose area needs to be approximated
            by the Riemann Rectangles.

        n_iterations : int,
            The number of VGroups of successive accuracy that are needed.

        max_dx : int, float, optional
            The maximum change in x between two VGroups of Riemann Rectangles

        power_base : int, float, optional
            Defaults to 2

        stroke_width : int, float, optional
            The stroke_width of the border of the rectangles.

        **kwargs
            Any valid keyword arguments of get_riemann_rectangles.

        Returns
        -------
        list
            The list of Riemann Rectangles of increasing accuracy.
        """
        return [
            self.get_riemann_rectangles(
                graph=graph,
                dx=float(max_dx) / (power_base ** n),
                stroke_width=float(stroke_width) / (power_base ** n),
                **kwargs,
            )
            for n in range(n_iterations)
        ]

    def get_area(
        self, graph, t_min, t_max, bounded=None, dx_scaling=1, area_color=WHITE
    ):
        """
        Returns a VGroup of Riemann rectangles
        sufficiently small enough to visually
        approximate the area under the graph passed.

        Parameters
        ----------
        graph : ParametricFunction
            The graph/curve for which the area needs to be gotten.

        t_min : int, float
            The lower bound of x from which to approximate the area.

        t_max : int, float
            The upper bound of x until which the area must be approximated.

        Returns
        -------
        VGroup
            The VGroup containing the Riemann Rectangles.
        """
        numerator = max(t_max - t_min, 0.0001)
        dx = float(numerator) / self.num_rects
        return (
            self.get_riemann_rectangles(
                graph,
                x_min=t_min,
                x_max=t_max,
                dx=dx * dx_scaling,
                stroke_width=0,
                bounded_graph=bounded,
            )
            .set_fill(opacity=0.3)
            .set_color(area_color)
        )

    def transform_between_riemann_rects(self, curr_rects, new_rects, **kwargs):
        """
        This method is used to transform between two VGroups of Riemann Rectangles,
        if they were obtained by get_riemann_rectangles or get_riemann_rectangles_list.
        No animation is returned, and the animation is directly played.

        Parameters
        ----------
        curr_rects : VGroup
            The current Riemann Rectangles

        new_rects : VGroup
            The Riemann Rectangles to transform to.

        **kwargs
            added_anims
                Any other animations to play simultaneously.
        """
        transform_kwargs = {"run_time": 2, "lag_ratio": 0.5}
        added_anims = kwargs.get("added_anims", [])
        transform_kwargs.update(kwargs)
        curr_rects.align_submobjects(new_rects)
        x_coords = set()  # Keep track of new repetitions
        for rect in curr_rects:
            x = rect.get_center()[0]
            if x in x_coords:
                rect.set_fill(opacity=0)
            else:
                x_coords.add(x)
        self.play(Transform(curr_rects, new_rects, **transform_kwargs), *added_anims)

    def get_vertical_line_to_graph(self, x, graph, line_class=Line, **line_kwargs):
        """
        This method returns a Vertical line from the x-axis to
        the corresponding point on the graph/curve.

        Parameters
        ----------
        x : int, float
            The x-value at which the line should be placed/calculated.

        graph : ParametricFunction
            The graph on which the line should extend to.

        line_class : Line and similar
            The type of line that should be used.
            Defaults to Line.

        **line_kwargs
            Any valid keyword arguments of the object passed in "line_class"
            If line_class is Line, any valid keyword arguments of Line are allowed.

        Return
        ------
        An object of type passed in "line_class"
            Defaults to Line
        """
        if "color" not in line_kwargs:
            line_kwargs["color"] = graph.get_color()
        return line_class(
            self.coords_to_point(x, 0),
            self.input_to_graph_point(x, graph),
            **line_kwargs,
        )

    def get_vertical_lines_to_graph(
        self, graph, x_min=None, x_max=None, num_lines=20, **kwargs
    ):
        """
        Obtains multiple lines from the x axis to the Graph/curve.

        Parameters
        ----------
        graph : ParametricFunction
            The graph on which the line should extend to.

        x_min : int, float, optional
            The lower bound from which lines can appear.

        x_max : int, float, optional
            The upper bound until which the lines can appear.

        num_lines : int, optional
            The number of lines (evenly spaced)
            that are needed.

        Returns
        -------
        VGroup
            The VGroup of the evenly spaced lines.

        """
        x_min = x_min or self.x_min
        x_max = x_max or self.x_max
        return VGroup(
            *[
                self.get_vertical_line_to_graph(x, graph, **kwargs)
                for x in np.linspace(x_min, x_max, num_lines)
            ]
        )

    def get_secant_slope_group(
        self,
        x,
        graph,
        dx=None,
        dx_line_color=None,
        df_line_color=None,
        dx_label=None,
        df_label=None,
        include_secant_line=True,
        secant_line_color=None,
        secant_line_length=10,
    ):
        """
        This method returns a VGroup of (two lines
        representing dx and df, the labels for dx and
        df, and the Secant to the Graph/curve at a
        particular x value.

        Parameters
        ----------
        x : int, float
            The x value at which the secant enters, and intersects
            the graph for the first time.

        graph : ParametricFunction
            The curve/graph for which the secant must
            be found.

        dx : int, float, optional
            The change in x after which the secant exits.

        dx_line_color : str, optional
            The line color for the line that indicates the change in x.

        df_line_color : str, optional
            The line color for the line that indicates the change in y.

        dx_label : str, optional
            The label to be provided for the change in x.

        df_label : str, optional
            The label to be provided for the change in y.

        include_secant_line : bool, optional
            Whether or not to include the secant line in the graph,
            or just have the df and dx lines and labels.

        secant_line_color : str, optional
            The color of the secant line.

        secant_line_length : int, float, optional
            How long the secant line should be.


        Returns
        -------
        :class:`.VGroup`
            A group containing the elements ``dx_line``, ``df_line``, and
            if applicable also ``dx_label``, ``df_label``, ``secant_line``.

        """
        kwargs = locals()
        kwargs.pop("self")
        group = VGroup()
        group.kwargs = kwargs

        dx = dx or float(self.x_max - self.x_min) / 10
        dx_line_color = dx_line_color or self.default_input_color
        df_line_color = df_line_color or graph.get_color()

        p1 = self.input_to_graph_point(x, graph)
        p2 = self.input_to_graph_point(x + dx, graph)
        interim_point = p2[0] * RIGHT + p1[1] * UP

        group.dx_line = Line(p1, interim_point, color=dx_line_color)
        group.df_line = Line(interim_point, p2, color=df_line_color)
        group.add(group.dx_line, group.df_line)

        labels = VGroup()
        if dx_label is not None:
            group.dx_label = MathTex(dx_label)
            labels.add(group.dx_label)
            group.add(group.dx_label)
        if df_label is not None:
            group.df_label = MathTex(df_label)
            labels.add(group.df_label)
            group.add(group.df_label)

        if len(labels) > 0:
            max_width = 0.8 * group.dx_line.get_width()
            max_height = 0.8 * group.df_line.get_height()
            if labels.get_width() > max_width:
                labels.set_width(max_width)
            if labels.get_height() > max_height:
                labels.set_height(max_height)

        if dx_label is not None:
            group.dx_label.next_to(
                group.dx_line, np.sign(dx) * DOWN, buff=group.dx_label.get_height() / 2
            )
            group.dx_label.set_color(group.dx_line.get_color())

        if df_label is not None:
            group.df_label.next_to(
                group.df_line, np.sign(dx) * RIGHT, buff=group.df_label.get_height() / 2
            )
            group.df_label.set_color(group.df_line.get_color())

        if include_secant_line:
            secant_line_color = secant_line_color or self.default_derivative_color
            group.secant_line = Line(p1, p2, color=secant_line_color)
            group.secant_line.scale_in_place(
                secant_line_length / group.secant_line.get_length()
            )
            group.add(group.secant_line)

        return group

    def add_T_label(
        self, x_val, side=RIGHT, label=None, color=WHITE, animated=False, **kwargs
    ):
        """Create a triangle marker with a vertical line from the x-axis
        to ``self.v_graph`` at the given x coordinate ``x_val``.

        This method adds to the Scene:

        - a Vertical line from the x-axis to the corresponding point on the graph/curve.
        - a small vertical Triangle whose top point lies on the base of the vertical line
        - a MathTex to be a label for the Line and Triangle, at the bottom of
          the Triangle.

        The scene needs to have the graph have the identifier/variable
        name ``self.v_graph``.

        Parameters
        ----------
        x_val : float, int
            The x value at which the secant enters, and intersects
            the graph for the first time.

        side : np.array(), optional

        label : str, optional
            The label to give the vertline and triangle

        color : str, optional
            The hex color of the label.

        animated : bool, optional
            Whether or not to animate the addition of the T_label

        **kwargs
            Any valid keyword argument of a self.play call.
        """
        triangle = RegularPolygon(n=3, start_angle=np.pi / 2)
        triangle.set_height(MED_SMALL_BUFF)
        triangle.move_to(self.coords_to_point(x_val, 0), UP)
        triangle.set_fill(color, 1)
        triangle.set_stroke(width=0)
        if label is None:
            T_label = MathTex(self.variable_point_label, fill_color=color)
        else:
            T_label = MathTex(label, fill_color=color)

        T_label.next_to(triangle, DOWN)
        v_line = self.get_vertical_line_to_graph(x_val, self.v_graph, color=YELLOW)

        if animated:
            self.play(
                DrawBorderThenFill(triangle),
                ShowCreation(v_line),
                Write(T_label, run_time=1),
                **kwargs,
            )

        if np.all(side == LEFT):
            self.left_T_label_group = VGroup(T_label, triangle)
            self.left_v_line = v_line
            self.add(self.left_T_label_group, self.left_v_line)
        elif np.all(side == RIGHT):
            self.right_T_label_group = VGroup(T_label, triangle)
            self.right_v_line = v_line
            self.add(self.right_T_label_group, self.right_v_line)

    def get_animation_integral_bounds_change(
        self, graph, new_t_min, new_t_max, fade_close_to_origin=True, run_time=1.0
    ):
        """
        This method requires a lot of prerequisites:
        self.area must be defined from self.get_area()
        self.left_v_line and self.right_v_line must be defined from self.get_v_line
        self.left_T_label_group and self.right_T_label_group must be defined from self.add_T_label

        This method will return a VGroup of new mobjects for each of those, when provided the graph/curve,
        the new t_min and t_max, the run_time and a bool stating whether or not to fade when close to
        the origin.

        Parameters
        ----------
        graph : ParametricFunction
            The graph for which this must be done.

        new_t_min : int, float
            The new lower bound.

        new_t_max : int, float
            The new upper bound.

        fade_close_to_origin : bool, optional
            Whether or not to fade when close to the origin.

        run_time : int, float, optional
            The run_time of the animation of this change.
        """
        curr_t_min = self.x_axis.point_to_number(self.area.get_left())
        curr_t_max = self.x_axis.point_to_number(self.area.get_right())
        if new_t_min is None:
            new_t_min = curr_t_min
        if new_t_max is None:
            new_t_max = curr_t_max

        group = VGroup(self.area)
        group.add(self.left_v_line)
        group.add(self.left_T_label_group)
        group.add(self.right_v_line)
        group.add(self.right_T_label_group)

        def update_group(group, alpha):
            area, left_v_line, left_T_label, right_v_line, right_T_label = group
            t_min = interpolate(curr_t_min, new_t_min, alpha)
            t_max = interpolate(curr_t_max, new_t_max, alpha)
            new_area = self.get_area(graph, t_min, t_max)

            new_left_v_line = self.get_vertical_line_to_graph(t_min, graph)
            new_left_v_line.set_color(left_v_line.get_color())
            left_T_label.move_to(new_left_v_line.get_bottom(), UP)

            new_right_v_line = self.get_vertical_line_to_graph(t_max, graph)
            new_right_v_line.set_color(right_v_line.get_color())
            right_T_label.move_to(new_right_v_line.get_bottom(), UP)

            # Fade close to 0
            if fade_close_to_origin:
                if len(left_T_label) > 0:
                    left_T_label[0].set_fill(opacity=min(1, np.abs(t_min)))
                if len(right_T_label) > 0:
                    right_T_label[0].set_fill(opacity=min(1, np.abs(t_max)))

            Transform(area, new_area).update(1)
            Transform(left_v_line, new_left_v_line).update(1)
            Transform(right_v_line, new_right_v_line).update(1)
            return group

        return UpdateFromAlphaFunc(group, update_group, run_time=run_time)

    def animate_secant_slope_group_change(
        self,
        secant_slope_group,
        target_dx=None,
        target_x=None,
        run_time=3,
        added_anims=None,
        **anim_kwargs,
    ):
        """
        This method animates the change of the secant slope group  from
        the old secant slope group, into a new secant slope group.

        Parameters
        ----------
        secant_slope_group : VGroup
            The old secant_slope_group

        target_dx : int, float, optional
            The new dx value.

        target_x : int, float, optional
            The new x value at which the secant should be.

        run_time : int, float, optional
            The run time for this change when animated.

        added_anims : list, optional
            Any exta animations that should be played alongside.

        **anim_kwargs
            Any valid kwargs of a self.play call.

        NOTE: At least one of target_dx and target_x should be not None.
        """
        if target_dx is None and target_x is None:
            raise ValueError("At least one of target_x and target_dx must not be None")
        if added_anims is None:
            added_anims = []

        start_dx = secant_slope_group.kwargs["dx"]
        start_x = secant_slope_group.kwargs["x"]
        if target_dx is None:
            target_dx = start_dx
        if target_x is None:
            target_x = start_x

        def update_func(group, alpha):
            dx = interpolate(start_dx, target_dx, alpha)
            x = interpolate(start_x, target_x, alpha)
            kwargs = dict(secant_slope_group.kwargs)
            kwargs["dx"] = dx
            kwargs["x"] = x
            new_group = self.get_secant_slope_group(**kwargs)
            group.become(new_group)
            return group

        self.play(
            UpdateFromAlphaFunc(
                secant_slope_group, update_func, run_time=run_time, **anim_kwargs
            ),
            *added_anims,
        )
        secant_slope_group.kwargs["x"] = target_x
        secant_slope_group.kwargs["dx"] = target_dx
