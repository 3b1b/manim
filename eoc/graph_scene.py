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
        "x_labeled_nums" : None,
        "x_axis_label" : "$x$",
        "y_min" : -1,
        "y_max" : 10,
        "y_axis_height" : 6,
        "y_tick_frequency" : 1,
        "y_bottom_tick" : None, #Change if different from y_min
        "y_labeled_nums" : None,
        "y_axis_label" : "$y$",
        "axes_color" : GREY,
        "graph_origin" : 2.5*DOWN + 4*LEFT,
        "y_axis_numbers_nudge" : 0.4*UP,
        "num_graph_anchor_points" : 25,
        "default_graph_colors" : [BLUE, GREEN, YELLOW],
        "default_derivative_color" : GREEN,
        "default_input_color" : YELLOW,
    }
    def setup_axes(self, animate = False):
        x_num_range = float(self.x_max - self.x_min)
        self.space_unit_to_x = self.x_axis_width/x_num_range
        self.x_labeled_nums = self.x_labeled_nums or []
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
        if len(self.x_labeled_nums) > 0:
            x_axis.add_numbers(*filter(
                lambda x : x != 0,
                self.x_labeled_nums
            ))
        x_label = TextMobject(self.x_axis_label)
        x_label.next_to(
            x_axis.get_tick_marks(), UP+RIGHT, 
            buff = SMALL_BUFF
        )
        x_label.shift_onto_screen()
        x_axis.add(x_label)
        self.x_axis_label_mob = x_label

        y_num_range = float(self.y_max - self.y_min)
        self.space_unit_to_y = self.y_axis_height/y_num_range
        self.y_labeled_nums = self.y_labeled_nums or []
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
        if len(self.y_labeled_nums) > 0:
            y_axis.add_numbers(*filter(
                lambda y : y != 0,
                self.y_labeled_nums
            ))
            for mob in y_axis.numbers:
                mob.next_to(mob.get_center(), LEFT, MED_SMALL_BUFF)
                mob.shift(self.y_axis_numbers_nudge)
        y_label = TextMobject(self.y_axis_label)
        y_label.next_to(
            y_axis.get_tick_marks(), UP+RIGHT, 
            buff = SMALL_BUFF
        )
        y_label.shift_onto_screen()
        y_axis.add(y_label)
        self.y_axis_label_mob = y_label

        if animate:
            self.play(Write(VGroup(x_axis, y_axis)))
        else:
            self.add(x_axis, y_axis)
        self.x_axis, self.y_axis = self.axes = VGroup(x_axis, y_axis)
        self.default_graph_colors = it.cycle(self.default_graph_colors)

    def coords_to_point(self, x, y):
        assert(hasattr(self, "x_axis") and hasattr(self, "y_axis"))
        result = self.x_axis.number_to_point(x)[0]*RIGHT
        result += self.y_axis.number_to_point(y)[1]*UP
        return result

    def get_graph(
        self, func, 
        color = None,
        x_min = None,
        x_max = None,
        ):
        if color is None:
            color = self.default_graph_colors.next()
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

    def get_derivative_graph(self, graph, dx = 0.01, **kwargs):
        if "color" not in kwargs:
            kwargs["color"] = self.default_derivative_color
        def deriv(x):
            return self.slope_of_tangent(x, graph, dx) / self.space_unit_to_y
        return self.get_graph(deriv, **kwargs)

    def get_graph_label(
        self, 
        graph, 
        label = "f(x)", 
        x_val = None,
        direction = RIGHT,
        buff = MED_SMALL_BUFF,
        color = None,
        ):
        label = TexMobject(label)
        color = color or graph.get_color()
        label.highlight(color)
        if x_val is None:
            #Search from right to left
            for x in np.linspace(self.x_max, self.x_min, 100):
                point = self.input_to_graph_point(x, graph)
                if point[1] < SPACE_HEIGHT:
                    break
            x_val = x
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
        **line_kwargs
        ):
        if "color" not in line_kwargs:
            line_kwargs["color"] = graph.get_color()
        return line_class(
            self.coords_to_point(x, 0),
            self.input_to_graph_point(x, graph),
            **line_kwargs
        )  

    def get_vertical_lines_to_graph(
        self, graph,
        x_min = None,
        x_max = None,
        num_lines = 20,
        **kwargs
        ):
        x_min = x_min or self.x_min
        x_max = x_max or self.x_max
        return VGroup(*[
            self.get_vertical_line_to_graph(x, graph, **kwargs)
            for x in np.linspace(x_min, x_max, num_lines)
        ])

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
        """
        Resulting group is of the form VGroup(
            dx_line, 
            df_line,
            dx_label, (if applicable)
            df_label, (if applicable)
            secant_line, (if applicable)
        )
        """
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
        group.add(group.dx_line, group.df_line)

        labels = VGroup()
        if dx_label is not None:
            group.dx_label = TexMobject(dx_label)
            labels.add(group.dx_label)
            group.add(group.dx_label)
        if df_label is not None:
            group.df_label = TexMobject(df_label)
            labels.add(group.df_label)
            group.add(group.df_label)

        if len(labels) > 0:
            max_width = 0.8*group.dx_line.get_width()
            max_height = 0.8*group.df_line.get_height()            
            if labels.get_width() > max_width:
                labels.scale_to_fit_width(max_width)
            if labels.get_height() > max_height:
                labels.scale_to_fit_height(max_height)

        if dx_label is not None:
            group.dx_label.next_to(
                group.dx_line, DOWN, buff = group.dx_label.get_height()/2
            )
            group.dx_label.highlight(group.dx_line.get_color())

        if df_label is not None:
            group.df_label.next_to(
                group.df_line, RIGHT, buff = group.df_label.get_height()/2
            )
            group.df_label.highlight(group.df_line.get_color())

        if include_secant_line:
            secant_line_color = secant_line_color or self.default_derivative_color
            group.secant_line = Line(p1, p2, color = secant_line_color)
            group.secant_line.scale_in_place(
                secant_line_length/group.secant_line.get_length()
            )
            group.add(group.secant_line)

        return group

    def animate_secant_slope_group_change(
        self, secant_slope_group, 
        target_dx = None,
        target_x = None,
        run_time = 3,
        added_anims = None,
        **anim_kwargs
        ):
        if target_dx is None and target_x is None:
            raise Exception("At least one of target_x and target_dx must not be None")
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
            Transform(group, new_group).update(1)
            return group

        self.play(
            UpdateFromAlphaFunc(
                secant_slope_group, update_func,
                run_time = run_time,
                **anim_kwargs
            ),
            *added_anims
        )
        secant_slope_group.kwargs["x"] = target_x
        secant_slope_group.kwargs["dx"] = target_dx





















