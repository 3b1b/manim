from helpers import *

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
from eoc.chapter2 import Car, MoveCar, ShowSpeedometer, \
    IncrementNumber, GraphCarTrajectory, SecantLineToTangentLine, \
    VELOCITY_COLOR, TIME_COLOR, DISTANCE_COLOR
from topics.common_scenes import OpeningQuote, PatreonThanks

def v_rate_func(t):
    return 4*t - 4*(t**2)

def s_rate_func(t):
    return 3*(t**2) - 2*(t**3)

def v_func(t):
    return t*(8-t)

def s_func(t):
    return 4*t**2 - (t**3)/3.


class Chapter8OpeningQuote(OpeningQuote, PiCreatureScene):
    CONFIG = {
        "quote" : [
            " One should never try to prove anything that \\\\ is not ",
            "almost obvious", ". "
        ],
        "quote_arg_separator" : "",
        "highlighted_quote_terms" : {
            "almost obvious" : BLUE,
        },
        "author" : "Alexander Grothendieck"
    }
    def construct(self):
        self.remove(self.pi_creature)
        OpeningQuote.construct(self)

        words_copy = self.quote.get_part_by_tex("obvious").copy()
        author = self.author
        author.save_state()
        formula = self.get_formula()
        formula.next_to(author, DOWN, MED_LARGE_BUFF)
        formula.to_edge(LEFT)

        self.revert_to_original_skipping_status()
        self.play(FadeIn(self.pi_creature))
        self.play(
            author.next_to, self.pi_creature.get_corner(UP+LEFT), UP,
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.dither(3)
        self.play(
            author.restore,
            self.pi_creature.change_mode, "plain"
        )
        self.play(
            words_copy.next_to, self.pi_creature, 
                LEFT, MED_SMALL_BUFF, UP,
            self.pi_creature.change_mode, "thinking"
        )
        self.dither(2)
        self.play(
            Write(formula),
            self.pi_creature.change_mode, "confused"
        )
        self.dither()

    def get_formula(self):
        result = TexMobject(
            "{d(\\sin(\\theta)) \\over \\,", "d\\theta}", "=",
            "\\lim_{", "h", " \\to 0}", 
            "{\\sin(\\theta+", "h", ") - \\sin(\\theta) \\over", " h}", "=",
            "\\lim_{", "h", " \\to 0}", 
            "{\\big[ \\sin(\\theta)\\cos(", "h", ") + ",
            "\\sin(", "h", ")\\cos(\\theta)\\big] - \\sin(\\theta) \\over", "h}",
            "= \\dots"
        )
        result.highlight_by_tex("h", GREEN, substring = False)
        result.highlight_by_tex("d\\theta", GREEN)

        result.scale_to_fit_width(2*SPACE_WIDTH - 2*MED_SMALL_BUFF)
        return result

class ThisVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        this_video = series[7]
        this_video.save_state()
        next_video = series[8]

        deriv, integral, v_t, dt, equals, v_T = formula = TexMobject(
            "\\frac{d}{dT}", 
            "\\int_0^T", "v(t)", "\\,dt", 
            "=", "v(T)"
        )
        formula.highlight_by_tex("v", VELOCITY_COLOR)
        formula.next_to(self.teacher.get_corner(UP+LEFT), UP, MED_LARGE_BUFF)

        self.play(FadeIn(series, submobject_mode = "lagged_start"))
        self.play(
            this_video.shift, this_video.get_height()*DOWN/2,
            this_video.highlight, YELLOW,
            self.teacher.change_mode, "raise_right_hand",
        )
        self.play(Write(VGroup(integral, v_t, dt)))
        self.change_student_modes(*["erm"]*3)
        self.dither()
        self.play(Write(VGroup(deriv, equals, v_T)), )
        self.change_student_modes(*["confused"]*3)
        self.dither(3)
        self.play(
            this_video.restore,
            next_video.shift, next_video.get_height()*DOWN/2,
            next_video.highlight, YELLOW,
            integral[0].copy().next_to, next_video, DOWN, MED_LARGE_BUFF,
            FadeOut(formula),
            *it.chain(*[
                [pi.change_mode, "plain", pi.look_at, next_video]
                for pi in self.pi_creatures
            ])
        )
        self.dither(2)

class InCarRestrictedView(ShowSpeedometer):
    CONFIG = {
        "speedometer_title_text" : "Your view",
    }
    def construct(self):
        car = Car()
        car.move_to(self.point_A)
        self.car = car
        car.randy.save_state()
        Transform(car.randy, Randolph()).update(1)
        car.randy.next_to(car, RIGHT, MED_LARGE_BUFF)
        car.randy.look_at(car)

        window = car[1][6].copy()
        window.is_subpath = False
        window.set_fill(BLACK, opacity = 0.75)
        window.set_stroke(width = 0)

        square = Square(stroke_color = WHITE)
        square.replace(VGroup(self.speedometer, self.speedometer_title))
        square.scale_in_place(1.5)
        square.pointwise_become_partial(square, 0.25, 0.75)

        time_label = TextMobject("Time (in seconds):", "0")
        time_label.shift(2*UP)

        dots = VGroup(*map(Dot, [self.point_A, self.point_B]))
        line = Line(*dots, buff = 0)
        line.highlight(DISTANCE_COLOR)
        brace = Brace(line, DOWN)
        brace_text = brace.get_text("Distance traveled?")


        #Sit in car
        self.add(car)
        self.play(Blink(car.randy))
        self.play(car.randy.restore, Animation(car))
        self.play(ShowCreation(window, run_time = 2))
        self.dither()

        #Show speedometer
        self.introduce_added_mobjects()
        self.play(ShowCreation(square))
        self.dither()

        #Travel
        self.play(FadeIn(time_label))
        self.play(
            MoveCar(car, self.point_B, rate_func = s_rate_func),
            IncrementNumber(time_label[1], run_time = 8),
            MaintainPositionRelativeTo(window, car),
            *self.get_added_movement_anims(
                rate_func = v_rate_func,
                radians = -(16.0/70)*4*np.pi/3
            ),
            run_time = 8
        )
        eight = TexMobject("8").move_to(time_label[1])
        self.play(Transform(
            time_label[1], eight,
            rate_func = squish_rate_func(smooth, 0, 0.5)
        ))
        self.dither()

        #Ask about distance
        self.play(*map(ShowCreation, dots))
        self.play(ShowCreation(line))
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.dither(2)

class GraphDistanceVsTime(GraphCarTrajectory):
    CONFIG = {
        "y_min" : 0,
        "y_max" : 100,
        "y_axis_height" : 6,
        "y_tick_frequency" : 10,
        "y_labeled_nums" : range(10, 100, 10),
        "y_axis_label" : "Distance (in meters)",
        "x_min" : -1,
        "x_max" : 9,
        "x_axis_width" : 9,
        "x_tick_frequency" : 1,
        "x_leftmost_tick" : None, #Change if different from x_min
        "x_labeled_nums" : range(1, 9),
        "x_axis_label" : "$t$",
        "time_of_journey" : 8,
        "care_movement_rate_func" : s_rate_func,
        "num_graph_anchor_points" : 100
    }
    def construct(self):
        self.setup_axes()
        graph = self.get_graph(
            s_func, 
            color = DISTANCE_COLOR,
            x_min = 0,
            x_max = 8,
        )
        origin = self.coords_to_point(0, 0)
        graph_label = self.get_graph_label(
            graph, "s(t)", color = DISTANCE_COLOR
        )
        self.introduce_graph(graph, origin)

class PlotVelocity(GraphScene):
    CONFIG = {
        "x_min" : -1,
        "x_max" : 9,
        "x_axis_width" : 9,
        "x_tick_frequency" : 1,
        "x_labeled_nums" : range(1, 9),
        "x_axis_label" : "$t$",
        "y_min" : 0,
        "y_max" : 25,
        "y_axis_height" : 6,
        "y_tick_frequency" : 5,
        "y_labeled_nums" : range(5, 30, 5),
        "y_axis_label" : "Velocity in $\\frac{\\text{meters}}{\\text{second}}$",
    }
    def construct(self):
        self.setup_axes()
        self.add_speedometer()
        self.plot_points()
        self.draw_curve()

    def add_speedometer(self):
        speedometer = Speedometer()
        speedometer.next_to(self.y_axis_label_mob, RIGHT, LARGE_BUFF)
        speedometer.to_edge(UP)

        self.play(DrawBorderThenFill(
            speedometer, 
            submobject_mode = "lagged_start",
            rate_func = None,
        ))

        self.speedometer = speedometer

    def plot_points(self):
        times = range(0, 9)
        points = [
            self.coords_to_point(t, v_func(t))
            for t in times
        ]
        dots = VGroup(*[Dot(p, radius = 0.07) for p in points])
        dots.highlight(VELOCITY_COLOR)

        pre_dots = VGroup()
        dot_intro_anims = []

        for time, dot in zip(times, dots):
            pre_dot = dot.copy()
            self.speedometer.move_needle_to_velocity(v_func(time))
            pre_dot.move_to(self.speedometer.get_needle_tip())
            pre_dot.set_fill(opacity = 0)
            pre_dots.add(pre_dot)
            dot_intro_anims += [
                ApplyMethod(
                    pre_dot.set_fill, YELLOW, 1,
                    run_time = 0.1,
                ),
                ReplacementTransform(
                    pre_dot, dot,
                    run_time = 0.9,
                )
            ]
        self.speedometer.move_needle_to_velocity(0)

        self.play(
            Succession(
                *dot_intro_anims, rate_func = None
            ),
            ApplyMethod(
                self.speedometer.move_needle_to_velocity,
                v_func(4),
                rate_func = squish_rate_func(
                    lambda t : 1-v_rate_func(t),
                    0, 0.95,
                )
            ),
            run_time = 5
        )
        self.dither()

    def draw_curve(self):
        graph, label = self.get_v_graph_and_label()

        self.revert_to_original_skipping_status()
        self.play(ShowCreation(graph, run_time = 3))
        self.play(Write(graph_label))
        self.dither()

    ##

    def get_v_graph_and_label(self):
        graph = self.get_graph(
            v_func, 
            x_min = 0,
            x_max = 8,
            color = VELOCITY_COLOR
        )
        graph_label = TexMobject("v(t)", "=t(8-t)")
        graph_label.highlight_by_tex("v(t)", VELOCITY_COLOR)
        graph_label.next_to(
            graph.point_from_proportion(7./8.),
            UP+RIGHT
        )
        self.v_graph = graph
        self.v_graph_label = graph_label
        return graph, graph_label

class Chapter2Wrapper(Scene):
    def construct(self):
        title = TextMobject("Chapter 2: The paradox of the derivative")
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = WHITE)
        rect.scale_to_fit_height(1.5*SPACE_HEIGHT)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.dither(3)

class GivenDistanceWhatIsVelocity(GraphCarTrajectory):
    def construct(self):
        self.force_skipping()
        self.setup_axes()
        graph = self.graph_sigmoid_trajectory_function()
        origin = self.coords_to_point(0, 0)

        self.introduce_graph(graph, origin)
        self.comment_on_slope(graph, origin)
        self.revert_to_original_skipping_status()
        self.show_velocity_graph()

class DerivativeOfDistance(SecantLineToTangentLine):
    def construct(self):
        self.setup_axes()
        self.remove(self.y_axis_label_mob, self.x_axis_label_mob)
        self.add_derivative_definition(self.y_axis_label_mob)
        self.add_graph()
        self.draw_axes()
        self.show_tangent_line()

class AskAboutAntiderivative(PlotVelocity):
    def construct(self):
        self.setup_axes()
        self.add_v_graph()
        self.write_s_formula()
        self.write_antiderivative()


    def add_v_graph(self):
        graph, label = self.get_v_graph_and_label()
        self.play(ShowCreation(graph))
        self.play(Write(label))

        self.graph = graph
        self.graph_label = label

    def write_s_formula(self):
        ds_dt = TexMobject("ds", "\\over\\,", "dt")
        ds_dt.highlight_by_tex("ds", DISTANCE_COLOR)
        ds_dt.highlight_by_tex("dt", TIME_COLOR)
        ds_dt.next_to(self.graph_label, UP, LARGE_BUFF)

        v_t = self.graph_label.get_part_by_tex("v(t)")
        arrow = Arrow(
            ds_dt.get_bottom(), v_t.get_top(),
            color = WHITE,
        )

        self.play(
            Write(ds_dt, run_time = 2),
            ShowCreation(arrow)
        )
        self.dither()

    def write_antiderivative(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        randy.shift(2*RIGHT)
        words = TexMobject(
            "{d(", "???", ") \\over \\,", "dt}", "=", "t(8-t)"
        )
        words.highlight_by_tex("t(8-t)", VELOCITY_COLOR)
        words.highlight_by_tex("???", DISTANCE_COLOR)
        words.highlight_by_tex("dt", TIME_COLOR)
        words.scale(0.7)

        self.play(FadeIn(randy))
        self.play(PiCreatureSays(
            randy, words, 
            target_mode = "confused",
            bubble_kwargs = {"height" : 3, "width" : 4},
        ))
        self.play(Blink(randy))
        self.dither()

class Antiderivative(PiCreatureScene):
    def construct(self):
        functions = self.get_functions("t^2", "2t")
        alt_functions = self.get_functions("???", "t(8-t)")
        top_arc, bottom_arc = arcs = self.get_arcs(functions)
        derivative = TextMobject("Derivative")
        derivative.next_to(top_arc, UP)
        antiderivative = TextMobject("``Antiderivative''")
        antiderivative.next_to(bottom_arc, DOWN)
        antiderivative.highlight(bottom_arc.get_color())
        group = VGroup(functions, arcs, derivative, antiderivative)

        self.add(functions, top_arc, derivative)
        self.dither()
        self.play(
            ShowCreation(bottom_arc),
            Write(antiderivative),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.dither(2)
        for pair in reversed(zip(functions, alt_functions)):
            self.play(
                Transform(*pair),
                self.pi_creature.change_mode, "pondering"
            )
        self.dither(2)

        self.pi_creature_says(
            "But first!", 
            target_mode = "surprised",
            look_at_arg = 50*OUT,
            added_anims = [group.to_edge, LEFT],
            run_time = 1,
        )
        self.dither()


    def get_functions(self, left_tex, right_tex):
        left = TexMobject(left_tex)
        left.shift(2*LEFT)
        left.highlight(DISTANCE_COLOR)
        right = TexMobject(right_tex)
        right.shift(2*RIGHT)
        right.highlight(VELOCITY_COLOR)
        result = VGroup(left, right)
        result.shift(UP)
        return result

    def get_arcs(self, functions):
        f1, f2 = functions
        top_line = Line(f1.get_corner(UP+RIGHT), f2.get_corner(UP+LEFT))
        bottom_line = Line(f1.get_corner(DOWN+RIGHT), f2.get_corner(DOWN+LEFT))
        top_arc = Arc(start_angle = 5*np.pi/6, angle = -2*np.pi/3)
        bottom_arc = top_arc.copy()
        bottom_arc.rotate(np.pi)
        arcs = VGroup(top_arc, bottom_arc)
        arcs.scale_to_fit_width(top_line.get_width())
        for arc in arcs:
            arc.add_tip()
        top_arc.next_to(top_line, UP)
        bottom_arc.next_to(bottom_line, DOWN)
        bottom_arc.highlight(MAROON_B)

        return arcs

class AreaUnderVGraph(PlotVelocity):
    def construct(self):
        self.setup_axes()
        self.add(*self.get_v_graph_and_label())
        self.show_rects()

    def show_rects(self):
        rect_list = self.get_riemann_rectangles_list(
            self.v_graph, 7, 
            max_dx = 1.0,
            x_min = 0,
            x_max = 8,
        )
        flat_graph = self.get_graph(lambda t : 0)
        rects = self.get_riemann_rectangles(
            flat_graph, x_min = 0, x_max = 8, dx = 1.0
        )

        for new_rects in rect_list:
            new_rects.set_fill(opacity = 0.8)
            rects.align_submobjects(new_rects)
            for alt_rect in rects[::2]:
                alt_rect.set_fill(opacity = 0)
            self.play(Transform(
                rects, new_rects,
                run_time = 2,
                submobject_mode = "lagged_start"
            ))
        self.dither()

class ConstantVelocityCar(Scene):
    def construct(self):
        car = Car()
        car.scale(2)
        car.move_to(3*LEFT + 3*DOWN)

        self.add(car)
        self.dither()
        self.play(MoveCar(
            car, 6*RIGHT+3*DOWN,
            run_time = 5,
            rate_func = None,
        ))
        self.dither()

class ConstantVelocityPlot(PlotVelocity):
    CONFIG = {
        "x_axis_label" : "Time"
    }
    def construct(self):
        self.setup_axes()
        self.x_axis_label_mob.shift(DOWN)
        self.draw_graph()
        self.show_product()
        self.comment_on_area_wierdness()
        self.note_units()

    def draw_graph(self):
        graph = self.get_graph(
            lambda t : 10,
            x_min = 0, 
            x_max = 8,
            color = VELOCITY_COLOR
        )

        self.play(ShowCreation(graph, rate_func = None, run_time = 3))
        self.dither()

        self.graph = graph

    def show_product(self):
        rect = Rectangle(
            stroke_width = 0,
            fill_color = DISTANCE_COLOR,
            fill_opacity = 0.5
        )
        rect.replace(
            VGroup(self.graph, VectorizedPoint(self.graph_origin)),
            stretch = True
        )

        right_brace = Brace(rect, RIGHT)
        top_brace = Brace(rect, UP)
        v_label = right_brace.get_text(
            "$10 \\frac{\\text{meters}}{\\text{second}}$",
        )
        v_label.highlight(VELOCITY_COLOR)
        t_label = top_brace.get_text(
            "8 seconds"
        )
        t_label.highlight(TIME_COLOR)

        s_label = TexMobject("10", "\\times",  "8", "\\text{ meters}")
        s_label.highlight_by_tex("10", VELOCITY_COLOR)
        s_label.highlight_by_tex("8", TIME_COLOR)
        s_label.move_to(rect)

        self.play(
            GrowFromCenter(right_brace),
            Write(v_label),
        )
        self.play(
            GrowFromCenter(top_brace),
            Write(t_label),
        )
        self.play(
            FadeIn(rect),
            Write(s_label),
            Animation(self.graph)
        )
        self.dither(2)

        self.area_rect = rect
        self.s_label = s_label

    def comment_on_area_wierdness(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        bubble = randy.get_bubble(
            "Distance \\\\ is area?",
            bubble_class = ThoughtBubble,
            height = 3,
            width = 4,
            fill_opacity = 1,
        )
        bubble.content.scale_in_place(0.8)
        bubble.content.shift(SMALL_BUFF*UP)
        VGroup(bubble[-1], bubble.content).shift(1.5*LEFT)

        self.play(FadeIn(randy))
        self.play(randy.change_mode, "pondering")
        self.play(
            self.area_rect.highlight, YELLOW,
            *map(Animation, self.get_mobjects()),
            rate_func = there_and_back
        )
        self.play(Blink(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, randy.bubble,
            ShowCreation(bubble), 
            Write(bubble.content),
        )
        self.dither()
        self.play(Blink(randy))
        self.dither()
        self.play(
            randy.change_mode, "pondering",
            FadeOut(bubble),
            FadeOut(bubble.content),
        )

        self.randy = randy

    def note_units(self):
        x_line, y_line  = lines = VGroup(*[
            axis.main_line.copy()
            for axis in self.x_axis, self.y_axis
        ])
        lines.highlight(TIME_COLOR)
        square = Square(
            stroke_color = BLACK,
            stroke_width = 1,
            fill_color = PINK,
            fill_opacity = 1,
        )
        square.replace(
            VGroup(*[
                VectorizedPoint(self.coords_to_point(i, i))
                for i in 0, 1
            ]),
            stretch = True
        )
        units_of_area = VGroup(*[
            square.copy().move_to(
                self.coords_to_point(x, y),
                DOWN+LEFT
            )
            for x in range(8)
            for y in range(10)
        ])

        self.play(ShowCreation(x_line))
        self.play(Indicate(self.x_axis_label_mob))
        self.play(FadeOut(x_line))
        self.play(
            ShowCreation(y_line),
            self.randy.look_at, self.y_axis_label_mob
        )
        self.play(Indicate(self.y_axis_label_mob))
        self.play(FadeOut(y_line))
        for FadeClass in FadeIn, FadeOut:
            self.play(
                FadeClass(
                    units_of_area, 
                    submobject_mode = "lagged_start",
                    run_time = 3
                ),
                Animation(self.s_label),
                self.randy.look_at, self.area_rect
            )
        self.play(Blink(self.randy))
        self.dither()

class PiecewiseConstantCar(Scene):
    def construct(self):
        car = Car()
        start_point = 5*LEFT
        car.move_to(start_point)

        self.add(car)
        self.dither()
        for shift in 2, 6, 12:
            car.randy.rotate_in_place(np.pi/8)
            anim = MoveCar(
                car, start_point+shift*RIGHT,
                rate_func = None
            )

            anim.target_mobject[0].rotate_in_place(-np.pi/8)
            # for mob in anim.starting_mobject, anim.mobject:
            #     mob.randy.rotate_in_place(np.pi/6)
            self.play(anim)
        self.dither()

class PiecewiseConstantPlot(PlotVelocity):
    CONFIG = {
        "y_axis_label" : "",
        "min_graph_proportion" : 0.1,
        "max_graph_proportion" : 0.8,
        "num_riemann_approximations" : 7, ##TODO
        "riemann_rect_fill_opacity" : 0.75,
        "tick_size" : 0.2,
    }
    def construct(self):
        self.setup_graph()
        self.always_changing()
        self.show_piecewise_constant_graph()
        self.compute_distance_on_each_interval()
        self.approximate_original_curve()
        self.revert_to_specific_approximation()
        self.show_specific_rectangle()
        self.show_v_dt_for_all_rectangles()
        self.write_integral_symbol()
        self.roles_of_dt()
        self.what_does_sum_approach()

    def setup_graph(self):
        self.setup_axes()
        self.add(*self.get_v_graph_and_label())

    def always_changing(self):
        dot = Dot()
        arrow = Arrow(LEFT, RIGHT)
        words = TextMobject("Always changing")
        group = VGroup(dot, arrow, words)
        def update_group(group, alpha):
            dot, arrow, words = group
            prop = interpolate(
                self.min_graph_proportion,
                self.max_graph_proportion,
                alpha
            )
            graph_point = self.v_graph.point_from_proportion(prop)
            dot.move_to(graph_point)
            x_val = self.x_axis.point_to_number(graph_point)
            angle = self.angle_of_tangent(x_val, self.v_graph)
            angle += np.pi/2
            vect = rotate_vector(RIGHT, angle)
            arrow.rotate(angle - arrow.get_angle() + np.pi)
            arrow.shift(
                graph_point + MED_SMALL_BUFF*vect - arrow.get_end()
            )
            words.next_to(arrow.get_start(), UP)
            return group
        update_group(group, 0)

        self.play(
            Write(words),
            ShowCreation(arrow),
            DrawBorderThenFill(dot),
            run_time = 1
        )
        self.play(UpdateFromAlphaFunc(
            group, update_group,
            rate_func = there_and_back,
            run_time = 5
        ))
        self.dither()
        self.play(FadeOut(group))

    def show_piecewise_constant_graph(self):
        pw_constant_graph = self.get_pw_constant_graph()
        alt_lines = [
            line.copy().highlight(YELLOW)
            for line in pw_constant_graph[:4]
        ]
        for line in alt_lines:
            line.start_dot = Dot(line.get_start())
            line.end_dot = Dot(line.get_end())
            VGroup(line.start_dot, line.end_dot).highlight(line.get_color())
        line = alt_lines[0]

        faders = [self.v_graph, self.v_graph_label]
        for mob in faders:
            mob.save_state()
            mob.generate_target()
            mob.target.fade(0.7)

        self.play(*map(MoveToTarget, faders))
        self.play(ShowCreation(pw_constant_graph, run_time = 2))
        self.dither()
        self.play(ShowCreation(line))
        self.dither()
        for new_line in alt_lines[1:]:
            for mob in line.end_dot, new_line.start_dot, new_line:
                self.play(Transform(
                    line, mob,
                    run_time = 1./3
                ))
            self.remove(line)
            self.add(new_line)
            self.dither(2)
            line = new_line
        self.play(FadeOut(line))

        self.pw_constant_graph = pw_constant_graph

    def compute_distance_on_each_interval(self):
        rect_list = self.get_riemann_rectangles_list(
            self.v_graph, self.num_riemann_approximations, 
            max_dx = 1,
            x_min = 0,
            x_max = 8,
        )
        for rects in rect_list:
            rects.set_fill(opacity = self.riemann_rect_fill_opacity)
        flat_rects = self.get_riemann_rectangles(
            self.get_graph(lambda t : 0),
            x_min = 0, x_max = 8, dx = 1
        )
        rects = rect_list[0]
        rect = rects[1]
        flat_rects.submobjects[1] = rect.copy()

        right_brace = Brace(rect, RIGHT)
        top_brace = Brace(rect, UP)
        right_brace.label = right_brace.get_text("$7\\frac{\\text{m}}{\\text{s}}$")
        top_brace.label = top_brace.get_text("$1$s")

        self.play(FadeIn(rect))
        for brace in right_brace, top_brace:
            self.play(
                GrowFromCenter(brace),
                Write(brace.label, run_time = 1),
            )
            brace.add(brace.label)
            self.dither()
        self.play(
            ReplacementTransform(
                flat_rects, rects,
                run_time = 2,
                submobject_mode = "lagged_start",
            ),
            Animation(right_brace)
        )
        self.play(*map(FadeOut, [top_brace, right_brace]))
        self.dither()

        self.rects = rects
        self.rect_list = rect_list

    def approximate_original_curve(self):
        rects = self.rects
        self.play(
            FadeOut(self.pw_constant_graph),
            *[
                m.restore 
                for m in self.v_graph, self.v_graph_label
            ]+[Animation(self.rects)]
        )
        for new_rects in self.rect_list[1:]:
            rects.align_submobjects(new_rects)
            for every_other_rect in rects[::2]:
                every_other_rect.set_fill(opacity = 0)
            self.play(Transform(
                rects, new_rects, 
                run_time = 2,
                submobject_mode = "lagged_start"
            ))
            self.dither()

    def revert_to_specific_approximation(self):
        rects = self.rects
        rects.save_state()
        target_rects = self.rect_list[2]
        target_rects.set_fill(opacity = 1)

        ticks = self.get_ticks(target_rects)
        tick_pair = VGroup(*ticks[4:6])
        brace = Brace(tick_pair, DOWN, buff = 0)
        dt_label = brace.get_text("$dt$", buff = SMALL_BUFF)

        example_text = TextMobject(
            "For example, \\\\",
            "$dt$", "$=0.25$"
        )
        example_text.to_corner(UP+RIGHT)
        example_text.highlight_by_tex("dt", YELLOW)

        self.play(ReplacementTransform(
            rects, target_rects,
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        rects.restore()
        self.dither()
        self.play(
            ShowCreation(ticks),
            FadeOut(self.x_axis.numbers)
        )
        self.play(
            GrowFromCenter(brace),
            Write(dt_label)
        )
        self.dither()
        self.play(
            FadeIn(
                example_text, 
                run_time = 2,
                submobject_mode = "lagged_start",
            ),
            ReplacementTransform(
                dt_label.copy(),
                example_text.get_part_by_tex("dt")
            )
        )
        self.dither()

        self.rects = rects = target_rects
        self.ticks = ticks
        self.dt_brace = brace
        self.dt_label = dt_label
        self.dt_example_text = example_text

    def show_specific_rectangle(self):
        rects = self.rects
        rect = rects[4].copy()
        rect_top = Line(
            rect.get_corner(UP+LEFT),
            rect.get_corner(UP+RIGHT),
            color = self.v_graph.get_color()
        )

        t_vals = [1, 1.25]
        t_labels = VGroup(*[
            TexMobject("t=%s"%str(t))
            for t in t_vals
        ])
        t_labels.scale(0.7)
        t_labels.next_to(rect, DOWN)
        for vect, label in zip([LEFT, RIGHT], t_labels):
            label.shift(1.5*vect)
            label.add(Arrow(
                label.get_edge_center(-vect),
                rect.get_corner(DOWN+vect),
                buff = SMALL_BUFF,
                tip_length = 0.15,
                color = WHITE
            ))

        v_lines = VGroup()
        h_lines = VGroup()
        height_labels = VGroup()
        for t in t_vals:
            v_line = self.get_vertical_line_to_graph(
                t, self.v_graph,
                color = YELLOW
            )
            y_axis_point = self.graph_origin[0]*RIGHT
            y_axis_point += v_line.get_end()[1]*UP
            h_line = DashedLine(v_line.get_end(), y_axis_point)
            label = TexMobject("%.1f"%v_func(t))
            label.scale(0.5)
            label.next_to(h_line, LEFT, SMALL_BUFF)
            v_lines.add(v_line)
            h_lines.add(h_line)
            height_labels.add(label)

        circle = Circle(radius = 0.25, color = WHITE)
        circle.move_to(rect.get_top())

        self.play(
            rects.set_fill, None, 0.25,
            Animation(rect)
        )
        self.dither()
        for label in t_labels:
            self.play(FadeIn(label))
        self.dither()
        for v_line, h_line, label in zip(v_lines, h_lines, height_labels):
            self.play(ShowCreation(v_line))
            self.play(ShowCreation(h_line))
            self.play(Write(label, run_time = 1))
            self.dither()
        self.dither()
        t_label_copy = t_labels[0].copy()
        self.play(
            t_label_copy.scale, 1./0.7,
            t_label_copy.next_to, self.v_graph_label, DOWN+LEFT, 0
        )
        self.dither()
        self.play(FadeOut(t_label_copy))
        self.dither()

        self.play(ShowCreation(circle))
        self.play(ShowCreation(rect_top))
        self.play(FadeOut(circle))
        rect.add(rect_top)
        self.dither()
        for x in range(2):
            self.play(
                rect.scale_to_fit_height, v_lines[1].get_height(),
                rect.move_to, rect.get_bottom(), DOWN,
                run_time = 4,
                rate_func = there_and_back
            )

        self.play(*map(FadeOut, [
            group[1]
            for group in v_lines, h_lines, height_labels
        ]))
        self.play(
            v_lines[0].highlight, RED,
            rate_func = there_and_back,
        )
        self.dither()

        area = TextMobject(
            "7$\\frac{\\text{m}}{\\text{s}}$",
            "$\\times$",
            "0.25s",
            "=",
            "1.75m"
        )
        area.next_to(rect, RIGHT, LARGE_BUFF)
        arrow = Arrow(
            area.get_left(), rect.get_center(), 
            buff = 0,
            color = WHITE
        )
        area.shift(SMALL_BUFF*RIGHT)

        self.play(
            Write(area),
            ShowCreation(arrow)
        )
        self.dither(2)
        self.play(*map(FadeOut, [
            area, arrow, 
            v_lines[0], h_lines[0], height_labels[0],
            rect, t_labels
        ]))

    def show_v_dt_for_all_rectangles(self):
        dt_brace_group = VGroup(self.dt_brace, self.dt_label)
        rects_subset = self.rects[10:15]

        last_rect = None
        for rect in rects_subset:
            brace = Brace(rect, LEFT, buff = 0)
            v_t = TexMobject("v(t)")
            v_t.next_to(brace, LEFT, SMALL_BUFF)
            anims = [
                rect.set_fill, None, 1,
                dt_brace_group.next_to, rect, DOWN, SMALL_BUFF
            ]
            if last_rect is not None:
                anims += [
                    last_rect.set_fill, None, 0.25,
                    ReplacementTransform(last_brace, brace),
                    ReplacementTransform(last_v_t, v_t),
                ]
            else:
                anims += [
                    GrowFromCenter(brace),
                    Write(v_t)
                ]
            self.play(*anims)
            self.dither()

            last_rect = rect
            last_brace = brace
            last_v_t = v_t

        self.v_t = last_v_t
        self.v_t_brace = last_brace

    def write_integral_symbol(self):
        integral = TexMobject(
            "\\int", "^8", "_0", "v(t)", "\\,dt"
        )
        integral.to_corner(UP+RIGHT)
        int_copy = integral.get_part_by_tex("int").copy()
        bounds = map(integral.get_part_by_tex, ["0", "8"])

        sum_word = TextMobject("``Sum''")
        sum_word.next_to(integral, DOWN, MED_LARGE_BUFF, LEFT)
        alt_sum_word = sum_word.copy()
        int_symbol = TexMobject("\\int")
        int_symbol.replace(alt_sum_word[1], dim_to_match = 1)
        alt_sum_word.submobjects[1] = int_symbol

        self.play(FadeOut(self.dt_example_text))
        self.play(Write(integral.get_part_by_tex("int")))
        self.dither()
        self.play(Transform(int_copy, int_symbol))
        self.play(Write(alt_sum_word), Animation(int_copy))
        self.remove(int_copy)
        self.play(ReplacementTransform(alt_sum_word, sum_word))
        self.dither()

        for bound in bounds:
            self.play(Write(bound))
        self.dither()
        for bound, num in zip(bounds, [0, 8]):
            bound_copy = bound.copy()
            point = self.coords_to_point(num, 0)
            self.play(
                bound_copy.scale, 1.5,
                bound_copy.next_to, point, DOWN, MED_LARGE_BUFF
            )
        self.play(ApplyWave(self.ticks, direction = UP))
        self.dither()

        for mob, tex in (self.v_t, "v(t)"), (self.dt_label, "dt"):
            self.play(ReplacementTransform(
                mob.copy().highlight(YELLOW), 
                integral.get_part_by_tex(tex),
                run_time = 2
            ))
        self.dither()

        self.integral = integral
        self.sum_word = sum_word

    def roles_of_dt(self):
        rects = self.rects
        next_rects = self.rect_list[3]

        morty = Mortimer().flip()
        morty.to_corner(DOWN+LEFT)
        int_dt = self.integral.get_part_by_tex("dt")
        dt_copy = int_dt.copy()

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look, UP+RIGHT,
            dt_copy.next_to, morty.get_corner(UP+RIGHT), UP,
            dt_copy.highlight, YELLOW
        )
        self.play(Blink(morty))
        self.play(
            ReplacementTransform(
                dt_copy.copy(), int_dt,
                run_time = 2
            ),
            morty.look_at, int_dt
        )
        self.dither(2)
        self.play(
            ReplacementTransform(dt_copy.copy(), self.dt_label),
            morty.look_at, self.dt_label
        )
        self.play(*[
            ApplyMethod(
                tick.shift, tick.get_height()*UP/2,
                run_time = 2,
                rate_func = squish_rate_func(
                    there_and_back,
                    alpha, alpha+0.2,
                )
            )
            for tick, alpha in zip(
                self.ticks, 
                np.linspace(0, 0.8, len(self.ticks))
            )
        ])
        self.dither()

        #Shrink dt just a bit
        self.play(
            morty.change_mode, "pondering",
            rects.set_fill, None, 0.75,
            *map(FadeOut, [
                dt_copy, self.v_t, self.v_t_brace
            ])
        )
        rects.align_submobjects(next_rects)
        for every_other_rect in rects[::2]:
            every_other_rect.set_fill(opacity = 0)
        self.play(
            self.dt_brace.stretch, 0.5, 0,
            self.dt_brace.move_to, self.dt_brace, LEFT,
            ReplacementTransform(
                rects, next_rects,
                run_time = 2,
                submobject_mode = "lagged_start"
            ),
            Transform(
                self.ticks, self.get_ticks(next_rects),
                run_time = 2,
                submobject_mode = "lagged_start",
            ),
        )
        self.rects = rects = next_rects
        self.dither()
        self.play(Blink(morty))
        self.play(*[
            ApplyFunction(
                lambda r : r.shift(0.2*UP).set_fill(None, 1),
                rect,
                run_time = 2,
                rate_func = squish_rate_func(
                    there_and_back,
                    alpha, alpha+0.2,
                )
            )
            for rect, alpha in zip(
                rects, 
                np.linspace(0, 0.8, len(rects))
            )
        ]+[
            morty.change_mode, "thinking",
        ])
        self.dither()

        self.morty = morty

    def what_does_sum_approach(self):
        morty = self.morty
        rects = self.rects

        cross = TexMobject("\\times")
        cross.replace(self.sum_word, stretch = True)
        cross.highlight(RED)
        brace = Brace(self.integral, DOWN)
        dt_to_0 = brace.get_text("$dt \\to 0$")

        self.play(PiCreatureSays(
            morty, "Why not $\\Sigma$?",
            target_mode = "sassy"
        ))
        self.play(Blink(morty))
        self.dither()
        self.play(Write(cross))
        self.dither()
        self.play(
            RemovePiCreatureBubble(morty, target_mode = "plain"),
            *map(FadeOut, [
                cross, self.sum_word, self.ticks,
                self.dt_brace, self.dt_label,
            ])
        )
        self.play(FadeIn(brace), FadeIn(dt_to_0))
        for new_rects in self.rect_list[4:]:
            rects.align_submobjects(new_rects)
            for every_other_rect in rects[::2]:
                every_other_rect.set_fill(opacity = 0)
            self.play(
                Transform(
                    rects, new_rects, 
                    run_time = 2,
                    submobject_mode = "lagged_start"
                ),
                morty.look_at, rects,
            )
            self.dither()

    #####

    def get_pw_constant_graph(self):
        result = VGroup()
        for left_x in range(8):
            xs = [left_x, left_x+1]
            y = self.v_graph.underlying_function(left_x)
            line = Line(*[
                self.coords_to_point(x, y)
                for x in xs
            ])
            line.highlight(self.v_graph.get_color())
            result.add(line)
        return result

    def get_ticks(self, rects):
        ticks = VGroup(*[
            Line(
                point+self.tick_size*UP/2, 
                point+self.tick_size*DOWN/2
            )
            for t in np.linspace(0, 8, len(rects)+1)
            for point in [self.coords_to_point(t, 0)]
        ])
        ticks.highlight(YELLOW)
        return ticks

class CarJourneyApproximations(Scene):
    def construct(self):
        pass































