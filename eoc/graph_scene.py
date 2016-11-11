from helpers import *

from scene import Scene
# from topics.geometry import 
from mobject.tex_mobject import TexMobject
from mobject.vectorized_mobject import VGroup
from animation.simple_animations import Write, ShowCreation
from topics.number_line import NumberLine
from topics.functions import ParametricFunction

class GraphScene(Scene):
    CONFIG = {
        "x_min" : -1,
        "x_max" : 10,
        "x_axis_width" : 9,
        "x_tick_frequency" : 1,
        "x_leftmost_tick" : -1,
        "x_labeled_nums" : range(1, 10),
        "x_axis_label" : "x",
        "y_min" : -1,
        "y_max" : 10,
        "y_axis_height" : 6,
        "y_tick_frequency" : 1,
        "y_bottom_tick" : -1,
        "y_labeled_nums" : range(1, 10),
        "y_axis_label" : "y",
        "axes_color" : GREY,
        "graph_origin" : 2.5*DOWN + 4*LEFT,
        "y_axis_numbers_nudge" : 0.4*UP+0.5*LEFT,
    }
    def setup_axes(self, animate = True):
        x_num_range = float(self.x_max - self.x_min)
        x_axis = NumberLine(
            x_min = self.x_min,
            x_max = self.x_max,
            space_unit_to_num = self.x_axis_width/x_num_range,
            tick_frequency = self.x_tick_frequency,
            leftmost_tick = self.x_leftmost_tick,
            numbers_with_elongated_ticks = self.x_labeled_nums,
            color = self.axes_color
        )
        x_axis.shift(self.graph_origin - x_axis.number_to_point(0))
        x_axis.add_numbers(*self.x_labeled_nums)
        x_label = TexMobject(self.x_axis_label)
        x_label.next_to(x_axis, RIGHT+UP, buff = SMALL_BUFF)

        y_num_range = float(self.y_max - self.y_min)
        y_axis = NumberLine(
            x_min = self.y_min,
            x_max = self.y_max,
            space_unit_to_num = self.y_axis_height/y_num_range,
            tick_frequency = self.y_tick_frequency,
            leftmost_tick = self.y_bottom_tick,
            numbers_with_elongated_ticks = self.y_labeled_nums,
            color = self.axes_color
        )
        y_axis.shift(self.graph_origin-y_axis.number_to_point(0))
        y_axis.rotate(np.pi/2, about_point = y_axis.number_to_point(0))
        y_axis.add_numbers(*self.y_labeled_nums)
        y_axis.numbers.shift(self.y_axis_numbers_nudge)
        y_label = TexMobject(self.y_axis_label)
        y_label.next_to(y_axis.get_top(), RIGHT, buff = 2*MED_BUFF)

        if animate:
            self.play(Write(VGroup(x_axis, y_axis)))
        else:
            selfe.add(x_axis, y_axis_label)
        self.x_axis, self.y_axis = x_axis, y_axis

    def coords_to_point(self, x, y):
        assert(hasattr(self, "x_axis") and hasattr(self, "y_axis"))
        result = self.x_axis.number_to_point(x)[0]*RIGHT
        result += self.y_axis.number_to_point(y)[1]*UP
        return result

    def graph_function(self, func, 
                       color = BLUE,
                       animate = True,
                       is_main_graph = True, 
                       ):

        def parameterized_graph(alpha):
            x = interpolate(self.x_min, self.x_max, alpha)
            return self.coords_to_point(x, func(x))

        graph = ParametricFunction(parameterized_graph, color = color)

        if is_main_graph:
            self.graph = graph
        if animate:
            self.play(ShowCreation(graph))
        self.add(graph)
        return graph

    def input_to_graph_point(self, x):
        assert(hasattr(self, "graph"))
        alpha = (x - self.x_min)/(self.x_max - self.x_min)
        return self.graph.point_from_proportion(alpha)

    def angle_of_tangent(self, x, dx = 0.01):
        assert(hasattr(self, "graph"))
        vect = self.graph_point(x + dx) - self.graph_point(x)
        return angle_of_vector(vect)

    def label_graph(self, graph, label = "f(x)", 
                    proportion = 0.7, 
                    direction = LEFT,
                    buff = 2*MED_BUFF,
                    animate = True
                    ):
        label = TexMobject(label)
        label.highlight(graph.get_color())
        label.next_to(
            graph.point_from_proportion(proportion), 
            direction,
            buff = buff
        )
        if animate:
            self.play(Write(label))
        self.add(label)
        return label















