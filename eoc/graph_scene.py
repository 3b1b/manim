from helpers import *

from scene import Scene
# from topics.geometry import 
from mobject.tex_mobject import TexMobject, TextMobject
from mobject.vectorized_mobject import VGroup, VectorizedPoint
from animation.simple_animations import Write, ShowCreation, UpdateFromAlphaFunc
from animation.transform import Transform
from topics.number_line import NumberLine
from topics.functions import ParametricFunction
from topics.geometry import Rectangle, DashedLine, Line

class GraphScene(Scene):
    CONFIG = {
        "x_min" : -1,
        "x_max" : 10,
        "x_axis_width" : 9,
        "x_tick_frequency" : 1,
        "x_leftmost_tick" : None, #Change if different from x_min
        "x_labeled_nums" : range(1, 10),
        "x_axis_label" : "$x$",
        "y_min" : -1,
        "y_max" : 10,
        "y_axis_height" : 6,
        "y_tick_frequency" : 1,
        "y_bottom_tick" : None, #Change if different from y_min
        "y_labeled_nums" : range(1, 10),
        "y_axis_label" : "$y$",
        "axes_color" : GREY,
        "graph_origin" : 2.5*DOWN + 4*LEFT,
        "y_axis_numbers_nudge" : 0.4*UP+0.5*LEFT,
        "num_graph_anchor_points" : 25,
        "default_graph_colors" : [BLUE, GREEN, YELLOW],
        "default_derivative_color" : GREEN,
        "default_input_color" : YELLOW,
    }
    def setup_axes(self, animate = False):
        x_num_range = float(self.x_max - self.x_min)
        self.space_unit_to_x = self.x_axis_width/x_num_range
        x_axis = NumberLine(
            x_min = self.x_min,
            x_max = self.x_max,
            space_unit_to_num = self.space_unit_to_x,
            tick_frequency = self.x_tick_frequency,
            leftmost_tick = self.x_leftmost_tick or self.x_min,
            numbers_with_elongated_ticks = self.x_labeled_nums,
            color = self.axes_color
        )
        x_axis.shift(self.graph_origin - x_axis.number_to_point(0))
        if self.x_labeled_nums:
            x_axis.add_numbers(*self.x_labeled_nums)
        x_label = TextMobject(self.x_axis_label)
        x_label.next_to(x_axis, RIGHT+UP, buff = SMALL_BUFF)
        x_label.shift_onto_screen()
        x_axis.add(x_label)
        self.x_axis_label_mob = x_label

        y_num_range = float(self.y_max - self.y_min)
        self.space_unit_to_y = self.y_axis_height/y_num_range
        y_axis = NumberLine(
            x_min = self.y_min,
            x_max = self.y_max,
            space_unit_to_num = self.space_unit_to_y,
            tick_frequency = self.y_tick_frequency,
            leftmost_tick = self.y_bottom_tick or self.y_min,
            numbers_with_elongated_ticks = self.y_labeled_nums,
            color = self.axes_color
        )
        y_axis.shift(self.graph_origin-y_axis.number_to_point(0))
        y_axis.rotate(np.pi/2, about_point = y_axis.number_to_point(0))
        if self.y_labeled_nums:
            y_axis.add_numbers(*self.y_labeled_nums)
            y_axis.numbers.shift(self.y_axis_numbers_nudge)
        y_label = TextMobject(self.y_axis_label)
        y_label.next_to(y_axis.get_top(), RIGHT, buff = 2*MED_BUFF)
        y_label.shift_onto_screen()
        y_axis.add(y_label)
        self.y_axis_label_mob = y_label

        if animate:
            self.play(Write(VGroup(x_axis, y_axis)))
        else:
            self.add(x_axis, y_axis)
        self.x_axis, self.y_axis = x_axis, y_axis
        self.default_graph_colors = it.cycle(self.default_graph_colors)

    def coords_to_point(self, x, y):
        assert(hasattr(self, "x_axis") and hasattr(self, "y_axis"))
        result = self.x_axis.number_to_point(x)[0]*RIGHT
        result += self.y_axis.number_to_point(y)[1]*UP
        return result

    def get_graph(self, func, color = None):
        if color is None:
            color = self.default_graph_colors.next()

        def parameterized_function(alpha):
            x = interpolate(self.x_min, self.x_max, alpha)
            return self.coords_to_point(x, func(x))

        graph = ParametricFunction(
            parameterized_function, 
            color = color,
            num_anchor_points = self.num_graph_anchor_points,
        )
        graph.underlying_function = func
        return graph

    def input_to_graph_point(self, x, graph):
        return self.coords_to_point(x, graph.underlying_function(x))

    def angle_of_tangent(self, x, graph, dx = 0.01):
        vect = self.input_to_graph_point(x + dx, graph) - self.input_to_graph_point(x, graph)
        return angle_of_vector(vect)

    def slope_of_tangent(self, *args, **kwargs):
        return np.tan(self.angle_of_tangent(*args, **kwargs))

    def get_derivative_graph(self, graph, dx = 0.01, color = None):
        if color is None:
            color = self.default_derivative_color
        return self.get_graph(
            lambda x : self.slope_of_tangent(x, graph, dx) / self.space_unit_to_y,
            color = color,
        )

    def get_graph_label(
        self, 
        graph, 
        label = "f(x)", 
        x_val = None,
        direction = RIGHT,
        buff = MED_BUFF,
        color = None,
        ):
        label = TexMobject(label)
        color = color or graph.get_color()
        label.highlight(color)
        if x_val is None:
            x_range = np.linspace(self.x_min, self.x_max, 20)
            for left_x, right_x in zip(x_range, x_range[1:]):
                right_point = self.input_to_graph_point(right_x, graph)
                if right_point[1] > SPACE_HEIGHT:
                    break
            x_val = left_x
        label.next_to(
            self.input_to_graph_point(x_val, graph),
            direction,
            buff = buff
        )
        label.shift_onto_screen()
        return label

    def get_riemann_rectangles(
        self, 
        graph,
        x_min = None, 
        x_max = None, 
        dx = 0.1, 
        stroke_width = 1,
        start_color = BLUE,
        end_color = GREEN):
        x_min = x_min if x_min is not None else self.x_min
        x_max = x_max if x_max is not None else self.x_max
        rectangles = VGroup()
        for x in np.arange(x_min, x_max, dx):
            points = VGroup(*map(VectorizedPoint, [
                self.coords_to_point(x, 0),
                self.input_to_graph_point(x+dx, graph)
            ]))
            rect = Rectangle()
            rect.replace(points, stretch = True)
            rect.set_fill(opacity = 1)
            rectangles.add(rect)
        rectangles.gradient_highlight(start_color, end_color)
        rectangles.set_stroke(BLACK, width = stroke_width)
        return rectangles

    def get_vertical_line_to_graph(
        self,
        x, graph,
        line_class = Line,
        line_kwargs = None,
        ):
        if line_kwargs is None:
            line_kwargs = {}
        if "color" not in line_kwargs:
            line_kwargs["color"] = graph.get_color()
        return line_class(
            self.coords_to_point(x, 0),
            self.input_to_graph_point(x, graph),
            **line_kwargs
        )   

    def get_secant_slope_group(
        self, 
        x, graph, 
        dx = None,
        dx_line_color = None,
        df_line_color = None,
        slope_line_color = None,
        dx_label = None,
        df_label = None,
        include_secant_line = True,
        secant_line_color = None,
        secant_line_length = 10,
        ):
        kwargs = locals()
        kwargs.pop("self")
        group = VGroup()
        group.kwargs = kwargs

        dx = dx or float(self.x_max - self.x_min)/10
        dx_line_color = dx_line_color or self.default_input_color
        df_line_color = df_line_color or graph.get_color()

        p1 = self.input_to_graph_point(x, graph)
        p2 = self.input_to_graph_point(x+dx, graph)
        interim_point = p2[0]*RIGHT + p1[1]*UP

        group.dx_line = Line(
            p1, interim_point,
            color = dx_line_color
        )
        group.df_line = Line(
            interim_point, p2,
            color = df_line_color
        )
        if dx_label is not None:
            group.dx_label = TexMobject(dx_label)
            if group.dx_label.get_width() > group.dx_line.get_width():
                group.dx_label.scale_to_fit_width(group.dx_line.get_width())
            group.dx_label.next_to(group.dx_line, DOWN, SMALL_BUFF)
            group.dx_label.highlight(group.dx_line.get_color())

        if df_label is not None:
            group.df_label = TexMobject(df_label)
            if group.df_label.get_height() > group.df_line.get_height():
                group.df_label.scale_to_fit_height(group.df_line.get_height())
            group.df_label.next_to(group.df_line, RIGHT, SMALL_BUFF)
            group.df_label.highlight(group.df_line.get_color())

        if include_secant_line:
            secant_line_color = secant_line_color or self.default_derivative_color
            group.secant_line = Line(p1, p2, color = secant_line_color)
            group.secant_line.scale_in_place(
                secant_line_length/group.secant_line.get_length()
            )

        group.digest_mobject_attrs()
        return group

    def animate_secant_slope_group_dx_change(
        self, secant_slope_group, target_dx,
        run_time = 3,
        **anim_kwargs
        ):
        start_dx = secant_slope_group.kwargs["dx"]
        def update_func(group, alpha):
            dx = interpolate(start_dx, target_dx, alpha)
            kwargs = dict(secant_slope_group.kwargs)
            kwargs["dx"] = dx
            new_group = self.get_secant_slope_group(**kwargs)
            Transform(group, new_group).update(1)
            return group

        self.play(UpdateFromAlphaFunc(
            secant_slope_group, update_func,
            run_time = run_time,
            **anim_kwargs
        ))





















