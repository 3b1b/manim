
from manimlib.imports import *
from old_projects.eoc.chapter8 import *

import scipy.special

class IllustrateAreaModelErf(GraphScene):
    CONFIG = {
        "x_min" : -3.0,
        "x_max" : 3.0,
        "y_min" : 0,
        "y_max" : 1.0,
        "num_rects": 400,
        "y_axis_label" : "",
        "x_axis_label" : "",
        "variable_point_label" : "a",
        "graph_origin": 2.5 * DOWN + 4 * RIGHT,
        "x_axis_width": 5,
        "y_axis_height": 5
    }

    def construct(self):

        # integral bounds
        x_min_1 = -0.0001
        x_max_1 = 0.0001

        x_min_2 = self.x_min
        x_max_2 = self.x_max

        self.setup_axes()
        self.remove(self.x_axis, self.y_axis)
        graph = self.get_graph(lambda x: np.exp(-x**2) * 2.0 / TAU ** 0.5)
        area = self.area = self.get_area(graph, x_min_1, x_max_1)


        pdf_formula = TexMobject("p(x) = {1\over \sigma\sqrt{2\pi}}e^{-{1\over 2}({x\over\sigma})^2}")
        pdf_formula.set_color(graph.color)

        cdf_formula = TexMobject("P(|X| < ", "a", ") = \int", "_{-a}", "^a", "p(x) dx")
        cdf_formula.set_color_by_tex("a", YELLOW)
        cdf_formula.next_to(graph, LEFT, buff = 2)
        pdf_formula.next_to(cdf_formula, UP)

        formulas = VGroup(pdf_formula, cdf_formula)
        self.play(Write(pdf_formula))
        self.play(Write(cdf_formula))
        
        self.wait()


        self.play(ShowCreation(self.x_axis))
        self.play(ShowCreation(graph))
        self.play(FadeIn(area))

        self.v_graph = graph
        self.add_T_label(
            x_min_1,
            label = "-a",
            side = LEFT,
            color = YELLOW,
            animated = False
        )
        self.add_T_label(
            x_max_1,
            label = "a",
            side = RIGHT,
            color = YELLOW,
            animated = False
        )
        # don't show the labels just yet
        self.remove(
            self.left_T_label_group[0],
            self.right_T_label_group[0],
        )

        def integral_update_func(t):
            return scipy.special.erf(
                self.point_to_coords(self.right_v_line.get_center())[0]
            )

        def integral_update_func_percent(t):
            return 100 * integral_update_func(t)
            
        equals_sign = TexMobject("=").next_to(cdf_formula, buff = MED_LARGE_BUFF)

        cdf_value = DecimalNumber(0, color = graph.color, num_decimal_places = 3)
        cdf_value.next_to(equals_sign)
        self.play(
            FadeIn(equals_sign),
            FadeIn(cdf_value)
        )
        self.add_foreground_mobject(cdf_value)

        cdf_percentage = DecimalNumber(0, unit = "\\%")
        cdf_percentage.move_to(self.coords_to_point(0,0.2))
        self.add_foreground_mobject(cdf_percentage)

        cdf_value.add_updater(
            lambda m: m.set_value(integral_update_func())
        )

        anim = self.get_animation_integral_bounds_change(
            graph, x_min_2, x_max_2,
            run_time = 3)


        self.play(
            anim
        )

        rect = SurroundingRectangle(formulas, buff = 0.5 * MED_LARGE_BUFF)
        self.play(ShowCreation(rect))
