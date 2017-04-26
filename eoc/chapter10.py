from helpers import *
import scipy
import math

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from scene.reconfigurable_scene import ReconfigurableScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.graph_scene import GraphScene
from topics.common_scenes import OpeningQuote, PatreonThanks

def derivative(func, x, n = 1, dx = 0.01):
    samples = [func(x + (k - n/2)*dx) for k in range(n+1)]
    while len(samples) > 1:
        samples = [
            (s_plus_dx - s)/dx
            for s, s_plus_dx in zip(samples, samples[1:])
        ]
    return samples[0]

def taylor_approximation(func, highest_term, center_point = 0):
    derivatives = [
        derivative(func, center_point, n = n)
        for n in range(highest_term + 1)
    ]
    coefficients = [
        d/math.factorial(n) 
        for n, d in enumerate(derivatives)
    ]
    return lambda x : sum([
        c*(x**n) 
        for n, c in enumerate(coefficients)
    ])

class Chapter10OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "For me, mathematics is a collection of ", 
            "examples", "; a ",
            "theorem", " is a statement about a collection of ",
            "examples", " and the purpose of proving ",
            "theorems", " is to classify and explain the ",
            "examples", "."
        ],
        "quote_arg_separator" : "",
        "highlighted_quote_terms" : {
            "examples" : BLUE,
        },
        "author" : "John B. Conway",
        "fade_in_kwargs" : {
            "run_time" : 7,
        }
    }

class ExampleApproximation(GraphScene):
    CONFIG = {
        "function" : lambda x : np.exp(-x**2),
        "function_tex" : "e^{-x^2}", 
        "function_color" : BLUE,
        "order_sequence" : [0, 2, 4],
        "center_point" : 0,
        "approximation_terms" : ["1 ", "-x^2", "+\\frac{1}{2}x^4"],
        "approximation_color" : GREEN,
        "x_min" : -3,
        "x_max" : 3,
        "y_min" : -1,
        "y_max" : 2,
        "graph_origin" : DOWN + 2*LEFT,
    }
    def construct(self):
        self.setup_axes()
        func_graph = self.get_graph(
            self.function,
            self.function_color,
        )
        approx_graphs = [
            self.get_graph(
                taylor_approximation(self.function, n),
                self.approximation_color
            )
            for n in self.order_sequence
        ]

        near_text = TextMobject(
            "Near %s $= %d$"%(
                self.x_axis_label, self.center_point
            )
        )
        near_text.to_corner(UP + RIGHT)
        near_text.add_background_rectangle()
        equation = TexMobject(
            self.function_tex, 
            "\\approx",
            *self.approximation_terms
        )
        equation.next_to(near_text, DOWN, MED_LARGE_BUFF)
        equation.to_edge(RIGHT)
        near_text.next_to(equation, UP, MED_LARGE_BUFF)
        equation.highlight_by_tex(
            self.function_tex, self.function_color,
            substring = False
        )
        approx_terms = VGroup(*[
            equation.get_part_by_tex(tex, substring = False)
            for tex in self.approximation_terms
        ])
        approx_terms.set_fill(
            self.approximation_color,
            opacity = 0,
        )
        equation.add_background_rectangle()

        approx_graph = VectorizedPoint(
            self.input_to_graph_point(self.center_point, func_graph)
        )

        self.play(
            ShowCreation(func_graph, run_time = 2),
            Animation(equation),
            Animation(near_text),
        )
        for graph, term in zip(approx_graphs, approx_terms):
            self.play(
                Transform(approx_graph, graph, run_time = 2),
                Animation(equation),
                Animation(near_text),
                term.set_fill, None, 1,
            )
            self.dither()
        self.dither(2)

class ExampleApproximationWithSine(ExampleApproximation):
    CONFIG = {
        "function" : np.sin,
        "function_tex" : "\\sin(x)", 
        "order_sequence" : [1, 3, 5],
        "center_point" : 0,
        "approximation_terms" : [
            "x", 
            "-\\frac{1}{6}x^3", 
            "+\\frac{1}{120}x^5",
        ],
        "approximation_color" : GREEN,
        "x_min" : -2*np.pi,
        "x_max" : 2*np.pi,
        "x_tick_frequency" : np.pi/2,
        "y_min" : -2,
        "y_max" : 2,
        "graph_origin" : DOWN + 2*LEFT,
    }

class ExampleApproximationWithExp(ExampleApproximation):
    CONFIG = {
        "function" : np.exp,
        "function_tex" : "e^x", 
        "order_sequence" : [1, 2, 3, 4],
        "center_point" : 0,
        "approximation_terms" : [
            "1 + x", 
            "+\\frac{1}{2}x^2", 
            "+\\frac{1}{6}x^3",
            "+\\frac{1}{24}x^4",
        ],
        "approximation_color" : GREEN,
        "x_min" : -3,
        "x_max" : 4,
        "y_min" : -1,
        "y_max" : 10,
        "graph_origin" : 2*DOWN + 3*LEFT,
    }

class Pendulum(ReconfigurableScene):
    CONFIG = {
        "anchor_point" : 3*UP + 4*LEFT,
        "radius" : 4,
        "weight_radius" : 0.2,
        "angle" : np.pi/6,
    }
    def construct(self):
        self.draw_pendulum()
        self.show_oscillation()
        self.show_height()
        self.get_angry_at_cosine()
        self.substitute_approximation()
        self.show_confusion()


    def draw_pendulum(self):
        pendulum = self.get_pendulum()
        ceiling = self.get_ceiling()

        self.add(ceiling)
        self.play(ShowCreation(pendulum.line))
        self.play(DrawBorderThenFill(pendulum.weight, run_time = 1))

        self.pendulum = pendulum

    def show_oscillation(self):
        trajectory_dots = self.get_trajectory_dots()
        kwargs = self.get_swing_kwargs()

        self.play(
            ShowCreation(
                trajectory_dots,
                rate_func = None,
                run_time = kwargs["run_time"]
            ),
            Rotate(self.pendulum, -2*self.angle, **kwargs),
        )
        for m in 2, -2, 2:
            self.play(Rotate(self.pendulum, m*self.angle, **kwargs))
        self.dither()

    def show_height(self):
        v_line = self.get_v_line()
        h_line = self.get_h_line()
        radius_brace = self.get_radius_brace()
        height_brace = self.get_height_brace()
        height_tex = self.get_height_brace_tex(height_brace)
        arc, theta = self.get_arc_and_theta()

        height_tex_R = height_tex.get_part_by_tex("R")
        height_tex_theta = height_tex.get_part_by_tex("\\theta")
        to_write = VGroup(*[
            part
            for part in height_tex
            if part not in [height_tex_R, height_tex_theta]
        ])

        self.play(
            ShowCreation(h_line),
            GrowFromCenter(height_brace)
        )
        self.play(
            ShowCreation(v_line),
            ShowCreation(arc),
            Write(theta),
        )
        self.play(
            GrowFromCenter(radius_brace)
        )
        self.dither(2)
        self.play(
            Write(to_write),
            ReplacementTransform(
                radius_brace[-1].copy(),
                height_tex_R
            ),
            ReplacementTransform(
                theta.copy(),
                height_tex_theta
            ),
            run_time = 2
        )
        self.dither(2)

        self.arc = arc
        self.theta = theta
        self.height_tex_R = height_tex_R
        self.cosine = VGroup(*[
            height_tex.get_part_by_tex(tex)
            for tex in "cos", "theta", ")"
        ])
        self.one_minus = VGroup(*[
            height_tex.get_part_by_tex(tex)
            for tex in "\\big(1-", "\\big)"
        ])

    def get_angry_at_cosine(self):
        cosine = self.cosine
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        cosine.generate_target()
        cosine.save_state()
        cosine.target.next_to(morty, UP)

        self.play(FadeIn(morty))
        self.play(
            MoveToTarget(cosine),
            morty.change, "angry", cosine.target,
        )
        self.dither()
        self.play(Blink(morty))
        self.dither()

        self.morty = morty

    def substitute_approximation(self):
        morty = self.morty
        cosine = self.cosine
        cosine.generate_target()
        cosine_approx = self.get_cosine_approx()
        cosine_approx.next_to(cosine, UP+RIGHT)
        cosine_approx.to_edge(RIGHT)
        cosine.target.next_to(
            cosine_approx, LEFT,
            align_using_submobjects = True
        )
        kwargs = self.get_swing_kwargs()

        self.play(
            FadeIn(
                cosine_approx,
                run_time = 2,
                submobject_mode = "lagged_start"
            ),
            MoveToTarget(cosine),
            morty.change, "pondering", cosine_approx
        )
        self.dither()
        self.play(
            ApplyMethod(
                cosine_approx.theta_squared_over_two.copy().next_to,
                self.height_tex_R,
                run_time = 2,
            ),
            FadeOut(self.one_minus),
            morty.look_at, self.height_tex_R,
        )
        self.play(morty.change, "thinking", self.height_tex_R)
        self.transition_to_alt_config(
            angle = np.pi/12,
            transformation_kwargs = {"run_time" : 2},
        )

    def show_confusion(self):
        randy = Randolph(color = BLUE_C)
        randy.scale(0.8)
        randy.next_to(self.cosine, DOWN+LEFT)
        randy.to_edge(DOWN)

        self.play(FadeIn(randy))
        self.play(
            randy.change, "confused", self.cosine
        )
        self.play(randy.look_at, self.height_tex_R)
        self.dither()
        self.play(randy.look_at, self.cosine)
        self.play(Blink(randy))
        self.dither()

    #######

    def get_pendulum(self):
        line = Line(
            self.anchor_point,
            self.anchor_point + self.radius*DOWN,
            color = WHITE
        )
        weight = Circle(
            radius = self.weight_radius,
            fill_color = GREY,
            fill_opacity = 1,
            stroke_width = 0,
        )
        weight.move_to(line.get_end())
        result = VGroup(line, weight)
        result.rotate(
            self.angle, 
            about_point = self.anchor_point
        )
        result.line = line
        result.weight = weight

        return result

    def get_ceiling(self):
        line = Line(LEFT, RIGHT, color = GREY)
        line.scale(SPACE_WIDTH)
        line.move_to(self.anchor_point[1]*UP)
        return line

    def get_trajectory_dots(self, n_dots = 40, color = YELLOW):
        arc_angle = np.pi/6
        proportions = self.swing_rate_func(
            np.linspace(0, 1, n_dots)
        )
        angles = -2*arc_angle*proportions
        angle_to_point = lambda a : np.cos(a)*RIGHT + np.sin(a)*UP
        dots = VGroup(*[
            # Line(*map(angle_to_point, pair))
            Dot(angle_to_point(angle), radius = 0.005)
            for angle in angles
        ])
            
        dots.highlight(color)
        dots.scale(self.radius)
        dots.rotate(-np.pi/2 + arc_angle)
        dots.shift(self.anchor_point)
        return dots

    def get_v_line(self):
        return DashedLine(
            self.anchor_point, 
            self.anchor_point + self.radius*DOWN,
            color = WHITE
        )

    def get_h_line(self, color = BLUE):
        start = self.anchor_point + self.radius*DOWN
        end = start + self.radius*np.sin(self.angle)*RIGHT

        return Line(start, end, color = color)

    def get_radius_brace(self):
        v_line = self.get_v_line()
        brace = Brace(v_line, RIGHT)
        brace.rotate(self.angle, about_point = self.anchor_point)
        brace.add(brace.get_text("$R$", buff = SMALL_BUFF))
        return brace

    def get_height_brace(self):
        h_line = self.get_h_line()
        height = (1 - np.cos(self.angle))*self.radius
        line = Line(
            h_line.get_end(),
            h_line.get_end() + height*UP,
        )
        brace = Brace(line, RIGHT)
        return brace

    def get_height_brace_tex(self, brace):
        tex_mob = TexMobject(
            "R", "\\big(1-", "\\cos(", "\\theta", ")", "\\big)"
        )
        tex_mob.highlight_by_tex("theta", YELLOW)
        tex_mob.next_to(brace, RIGHT)
        return tex_mob

    def get_arc_and_theta(self):
        arc = Arc(
            start_angle = -np.pi/2,
            angle = self.angle,
            color = YELLOW
        )
        theta = TexMobject("\\theta")
        theta.highlight(YELLOW)
        theta.next_to(
            arc.point_from_proportion(0.5), 
            DOWN, SMALL_BUFF
        )
        for mob in arc, theta:
            mob.shift(self.anchor_point)
        return arc, theta

    def get_cosine_approx(self):
        approx = TexMobject(
            "\\approx 1 - ", "{\\theta", "^2", "\\over", "2}"
        )
        approx.highlight_by_tex("theta", YELLOW)
        approx.theta_squared_over_two = VGroup(*approx[-4:])

        return approx

    def get_swing_kwargs(self):
        return {
            "about_point" : self.anchor_point,
            "run_time" : 1.7,
            "rate_func" : self.swing_rate_func,
        }

    def swing_rate_func(self, t):
        return (1-np.cos(np.pi*t))/2.0

class ExampleApproximationWithCos(ExampleApproximationWithSine):
    CONFIG = {
        "function" : np.cos,
        "function_tex" : "\\cos(\\theta)", 
        "order_sequence" : [0, 2],
        "approximation_terms" : [
            "1", 
            "-\\frac{1}{2} \\theta ^2", 
        ],
        "x_axis_label" : "$\\theta$",
        "y_axis_label" : "",
        "x_axis_width" : 13,
        "graph_origin" : DOWN,
    }

    def construct(self):
        ExampleApproximationWithSine.construct(self)
        randy = Randolph(color = BLUE_C)
        randy.to_corner(DOWN+LEFT)
        high_graph = self.get_graph(lambda x : 4)
        v_lines, alt_v_lines = [
            VGroup(*[
                self.get_vertical_line_to_graph(
                    u*dx, high_graph,
                    line_class = DashedLine,
                    color = YELLOW
                )
                for u in -1, 1
            ])
            for dx in 0.01, 0.7
        ]

        self.play(*map(ShowCreation, v_lines), run_time = 2)
        self.play(Transform(
            v_lines, alt_v_lines,
            run_time = 2,
        ))
        self.play(FadeIn(randy))
        self.play(PiCreatureBubbleIntroduction(
            randy, "How...?",
            bubble_class = ThoughtBubble,
            look_at_arg = self.graph_origin,
            target_mode = "confused"
        ))
        self.dither(2)
        self.play(Blink(randy))
        self.dither()

    def setup_axes(self):
        GraphScene.setup_axes(self)
        x_val_label_pairs = [
            (-np.pi, "-\\pi"),
            (np.pi, "\\pi"),
            (2*np.pi, "2\\pi"),
        ]
        for x_val, label in x_val_label_pairs:
            tex = TexMobject(label)
            tex.next_to(self.coords_to_point(x_val, 0), DOWN)
            self.add(tex)

class ConstructQuadraticApproximation(ExampleApproximationWithCos, ZoomedScene):
    CONFIG = {
        "x_axis_label" : "$x$",
        "colors" : [BLUE, YELLOW, GREEN],
        "zoomed_canvas_corner" : DOWN+LEFT,
        "zoom_factor" : 2,
    }
    def construct(self):
        self.force_skipping()

        self.setup_axes()
        self.add_cosine_graph()
        self.add_quadratic_graph()
        self.introduce_quadratic_constants()
        self.show_value_at_zero()
        self.set_c0_to_one()
        self.let_c1_and_c2_vary()
        self.show_tangent_slope()
        self.compute_cosine_derivative()
        self.compute_polynomial_derivative()
        self.let_c2_vary()
        self.point_out_negative_concavity()
        self.compute_cosine_second_derivative()
        self.show_matching_curvature()
        self.compute_polynomial_second_derivative()
        self.point_out_underestimate()
        self.second_derivative_of_cosine_increases()
        self.second_derivative_of_quadratic_is_constant()


    def add_cosine_graph(self):
        cosine_label = TexMobject("\\cos(x)")
        cosine_label.to_corner(UP+LEFT)
        cosine_graph = self.get_graph(np.cos)
        dot = Dot(color = WHITE)
        dot.move_to(cosine_label)
        for mob in cosine_label, cosine_graph:
            mob.highlight(self.colors[0])

        def update_dot(dot):
            dot.move_to(cosine_graph.points[-1])
            return dot

        self.play(Write(cosine_label, run_time = 1))
        self.play(dot.move_to, cosine_graph.points[0])
        self.play(
            ShowCreation(cosine_graph),
            UpdateFromFunc(dot, update_dot),
            run_time = 4
        )
        self.play(FadeOut(dot))

        self.cosine_label = cosine_label
        self.cosine_graph = cosine_graph

    def add_quadratic_graph(self):
        quadratic_graph = self.get_quadratic_graph()

        self.play(ReplacementTransform(
            self.cosine_graph.copy(),
            quadratic_graph
        ))
        self.dither()

        self.quadratic_graph = quadratic_graph

    def introduce_quadratic_constants(self):
        quadratic_tex = self.get_quadratic_tex("c_0", "c_1", "c_2")
        const_terms = quadratic_tex.get_parts_by_tex("c")
        free_to_change = TextMobject("Free to change")
        free_to_change.next_to(const_terms, DOWN, LARGE_BUFF)
        arrows = VGroup(*[
            Arrow(
                free_to_change.get_top(),
                const.get_bottom(),
                tip_length = 0.75*Arrow.CONFIG["tip_length"],
                color = const.get_color()
            )
            for const in const_terms
        ])
        alt_consts_list = [
            (0, -1, -0.25),
            (1, -1, -0.25),
            (1, 0, -0.25),
            (),
        ]

        self.play(FadeIn(
            quadratic_tex, 
            run_time = 3,
            submobject_mode = "lagged_start"
        ))
        self.play(
            FadeIn(free_to_change),
            *map(ShowCreation, arrows)
        )
        self.play(*[
            ApplyMethod(
                const.scale_in_place, 0.8,
                run_time = 2,
                rate_func = squish_rate_func(there_and_back, a, a + 0.75)
            )
            for const, a in zip(const_terms, np.linspace(0, 0.25, len(const_terms)))
        ])
        for alt_consts in alt_consts_list:
            self.change_quadratic_graph(
                self.quadratic_graph, *alt_consts
            )
            self.dither()

        self.quadratic_tex = quadratic_tex
        self.free_to_change_group = VGroup(free_to_change, *arrows)
        self.free_to_change_group.arrows = arrows

    def show_value_at_zero(self):
        arrow, x_equals_0 = ax0_group = self.get_arrow_x_equals_0_group()
        ax0_group.next_to(
            self.cosine_label, RIGHT,
            align_using_submobjects = True
        )
        one = TexMobject("1")
        one.next_to(arrow, RIGHT)
        one.save_state()
        one.move_to(self.cosine_label)
        one.set_fill(opacity = 0)

        v_line = self.get_vertical_line_to_graph(
            0, self.cosine_graph,
            line_class = DashedLine, 
            color = YELLOW
        )

        self.play(ShowCreation(v_line))
        self.play(
            ShowCreation(arrow),
            Write(x_equals_0, run_time = 2)
        )
        self.play(one.restore)
        self.dither()

        self.v_line = v_line
        self.equals_one_group = VGroup(arrow, x_equals_0, one)

    def set_c0_to_one(self):
        poly_at_zero = self.get_quadratic_tex(
            "c_0", "c_1", "c_2", arg = "0"
        )
        poly_at_zero.next_to(self.quadratic_tex, DOWN)
        equals_c0 = TexMobject("=", "c_0", "+0")
        equals_c0.highlight_by_tex("c_0", self.colors[0])
        equals_c0.next_to(
            poly_at_zero.get_part_by_tex("="), DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        poly_group = VGroup(
            equals_c0,
            poly_at_zero,
            self.quadratic_tex,
        )
        poly_group_target = VGroup(
            TexMobject("=", "1", "+0").highlight_by_tex("1", self.colors[0]),
            self.get_quadratic_tex("1", "c_1", "c_2", arg = "0"),
            self.get_quadratic_tex("1", "c_1", "c_2"),
        )
        for start, target in zip(poly_group, poly_group_target):
            target.move_to(start)

        self.play(FadeOut(self.free_to_change_group))
        self.play(ReplacementTransform(
            self.quadratic_tex.copy(),
            poly_at_zero
        ))
        self.dither(2)
        self.play(FadeIn(equals_c0))
        self.dither(2)
        self.play(Transform(
            poly_group, poly_group_target,
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        self.dither(2)
        self.play(*map(FadeOut, [poly_at_zero, equals_c0]))

        self.free_to_change_group.remove(
            self.free_to_change_group.arrows[0]
        )
        self.play(FadeIn(self.free_to_change_group))

    def let_c1_and_c2_vary(self):
        alt_consts_list = [
            (1, 1, -0.25),
            (1, -1, -0.25),
            (1, -1, 0.25),
            (1, 1, -0.1),
        ]

        for alt_consts in alt_consts_list:
            self.change_quadratic_graph(
                self.quadratic_graph,
                *alt_consts
            )
            self.dither()

    def show_tangent_slope(self):
        tangent_line = Line(LEFT, RIGHT, color = self.colors[1])
        tangent_line.scale(2)
        graph_point_at_zero = self.input_to_graph_point(
            0, self.cosine_graph
        ) 
        tangent_line.move_to(graph_point_at_zero)

        self.play(ShowCreation(tangent_line))
        self.change_quadratic_graph(
            self.quadratic_graph, 1, 0, -0.1
        )
        self.dither()
        self.change_quadratic_graph(
            self.quadratic_graph, 1, 1, -0.1
        )
        self.dither()
        self.activate_zooming()
        self.little_rectangle.move_to(graph_point_at_zero)
        self.play(
            self.little_rectangle.scale_in_place, 0.1,
        )
        self.dither()
        self.change_quadratic_graph(
            self.quadratic_graph, 1, 0, -0.1
        )
        self.dither()
        self.disactivate_zooming()
        self.dither()

        self.tangent_line = tangent_line

    def compute_cosine_derivative(self):
        derivative = TexMobject(
            "{d(", "\\cos", ")", "\\over", "dx}", "(0)",
        )
        derivative.highlight_by_tex("\\cos", self.colors[0])
        derivative.scale(0.75)
        derivative.next_to(
            self.cosine_label, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        rhs = TexMobject("=", "-\\sin(0)", "=", "0")
        rhs.highlight_by_tex("\\sin", self.colors[1])
        rhs.scale(0.8)
        rhs.next_to(
            derivative, RIGHT,
            align_using_submobjects = True
        )

        self.play(FadeIn(
            VGroup(derivative, *rhs[:2]),
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        self.dither(2)
        self.play(Write(VGroup(*rhs[2:])), run_time = 2)
        self.dither()
        self.play(Rotate(
            self.tangent_line, np.pi/12,
            in_place = True,
            run_time = 3,
            rate_func = wiggle
        ))
        self.dither()

        self.derivative_equation = VGroup(derivative, rhs)

    def compute_polynomial_derivative(self):
        derivative = self.get_quadratic_derivative("c_1", "c_2")
        derivative_at_zero = self.get_quadratic_derivative(
            "c_1", "c_2", arg = "0"
        )
        equals_c1 = TexMobject("=", "c_1", "+0")
        equals_c1.next_to(
            derivative_at_zero.get_part_by_tex("="), DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        equals_c1.highlight_by_tex("c_1", self.colors[1])
        poly_group = VGroup(
            equals_c1,
            derivative,
            self.quadratic_tex
        )
        poly_group_target = VGroup(
            TexMobject("=", "0", "+0").highlight_by_tex(
                "0", self.colors[1], substring = False
            ),
            self.get_quadratic_derivative("0", "c_2", arg = "0"),
            self.get_quadratic_tex("1", "0", "c_2")
        )
        for start, target in zip(poly_group, poly_group_target):
            target.move_to(start)

        self.revert_to_original_skipping_status()
        self.play(FadeOut(self.free_to_change_group))
        self.play(FadeIn(
            derivative, 
            run_time = 3,
            submobject_mode = "lagged_start"
        ))
        self.dither()
        self.play(Transform(
            derivative, derivative_at_zero,
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        self.dither()
        self.play(Write(equals_c1))
        self.dither(2)
        self.play(Transform(
            poly_group, poly_group_target,
            run_time = 3,
            submobject_mode = "lagged_start"
        ))
        self.dither(2)

        self.play(*map(FadeOut, poly_group[:-1]))
        self.free_to_change_group.remove(
            self.free_to_change_group.arrows[1]
        )
        self.play(FadeIn(self.free_to_change_group))

    def let_c2_vary(self):
        pass

    def point_out_negative_concavity(self):
        pass

    def compute_cosine_second_derivative(self):
        pass

    def show_matching_curvature(self):
        pass

    def compute_polynomial_second_derivative(self):
        pass

    def point_out_underestimate(self):
        pass

    def second_derivative_of_cosine_increases(self):
        pass

    def second_derivative_of_quadratic_is_constant(self):
        pass


    ######

    def change_quadratic_graph(self, graph, *args, **kwargs):
        transformation_kwargs = {}
        transformation_kwargs["run_time"] = kwargs.pop("run_time", 2)
        transformation_kwargs["rate_func"] = kwargs.pop("rate_func", smooth)
        new_graph = self.get_quadratic_graph(*args, **kwargs)
        self.play(Transform(graph, new_graph, **transformation_kwargs))
        graph.underlying_function = new_graph.underlying_function

    def get_quadratic_graph(self, c0 = 1, c1 = 0, c2 = -0.5):
        return self.get_graph(
            lambda x : c0 + c1*x + c2*x**2,
            color = self.colors[-1]
        )

    def get_quadratic_tex(self, c0, c1, c2, arg = "x"):
        tex_mob = TexMobject(
            "P(", arg, ")", "=", 
            c0, "+", c1, arg, "+", c2, arg, "^2"
        )
        for tex, color in zip([c0, c1, c2], self.colors):
            tex_mob.highlight_by_tex(tex, color)
        tex_mob.to_corner(UP+RIGHT)
        return tex_mob

    def get_quadratic_derivative(self, c1, c2, arg = "x"):
        result = TexMobject(
            "{dP \\over dx}", "(", arg, ")", "=",
            c1, "+", "2", c2, arg
        )
        for tex, color in zip([c1, c2], self.colors[1:]):
            result.highlight_by_tex(tex, color)
        if hasattr(self, "quadratic_tex"):
            result.next_to(
                self.quadratic_tex, DOWN,
                buff = MED_LARGE_BUFF,
                aligned_edge = LEFT
            )
        return result

    def get_arrow_x_equals_0_group(self):
        arrow = Arrow(LEFT, RIGHT)
        x_equals_0 = TexMobject("x = 0")
        x_equals_0.scale(0.75)
        x_equals_0.next_to(arrow.get_center(), DOWN, SMALL_BUFF)
        x_equals_0.shift(SMALL_BUFF*LEFT)
        return VGroup(arrow, x_equals_0)































