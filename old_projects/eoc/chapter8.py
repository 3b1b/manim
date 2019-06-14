import scipy
from manimlib.imports import *
from old_projects.eoc.chapter1 import Thumbnail as Chapter1Thumbnail
from old_projects.eoc.chapter2 import Car, MoveCar, ShowSpeedometer, \
    IncrementNumber, GraphCarTrajectory, SecantLineToTangentLine, \
    VELOCITY_COLOR, TIME_COLOR, DISTANCE_COLOR

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
        self.wait(3)
        self.play(
            author.restore,
            self.pi_creature.change_mode, "plain"
        )
        self.play(
            words_copy.next_to, self.pi_creature, 
                LEFT, MED_SMALL_BUFF, UP,
            self.pi_creature.change_mode, "thinking"
        )
        self.wait(2)
        self.play(
            Write(formula),
            self.pi_creature.change_mode, "confused"
        )
        self.wait()

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
        result.set_color_by_tex("h", GREEN, substring = False)
        result.set_color_by_tex("d\\theta", GREEN)

        result.set_width(FRAME_WIDTH - 2*MED_SMALL_BUFF)
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
        formula.set_color_by_tex("v", VELOCITY_COLOR)
        formula.next_to(self.teacher.get_corner(UP+LEFT), UP, MED_LARGE_BUFF)

        self.play(FadeIn(series, lag_ratio = 0.5))
        self.play(
            this_video.shift, this_video.get_height()*DOWN/2,
            this_video.set_color, YELLOW,
            self.teacher.change_mode, "raise_right_hand",
        )
        self.play(Write(VGroup(integral, v_t, dt)))
        self.change_student_modes(*["erm"]*3)
        self.wait()
        self.play(Write(VGroup(deriv, equals, v_T)), )
        self.change_student_modes(*["confused"]*3)
        self.wait(3)
        self.play(
            this_video.restore,
            next_video.shift, next_video.get_height()*DOWN/2,
            next_video.set_color, YELLOW,
            integral[0].copy().next_to, next_video, DOWN, MED_LARGE_BUFF,
            FadeOut(formula),
            *it.chain(*[
                [pi.change_mode, "plain", pi.look_at, next_video]
                for pi in self.pi_creatures
            ])
        )
        self.wait(2)

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

        dots = VGroup(*list(map(Dot, [self.point_A, self.point_B])))
        line = Line(*dots, buff = 0)
        line.set_color(DISTANCE_COLOR)
        brace = Brace(line, DOWN)
        brace_text = brace.get_text("Distance traveled?")


        #Sit in car
        self.add(car)
        self.play(Blink(car.randy))
        self.play(car.randy.restore, Animation(car))
        self.play(ShowCreation(window, run_time = 2))
        self.wait()

        #Show speedometer
        self.introduce_added_mobjects()
        self.play(ShowCreation(square))
        self.wait()

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
        self.wait()

        #Ask about distance
        self.play(*list(map(ShowCreation, dots)))
        self.play(ShowCreation(line))
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait(2)

class GraphDistanceVsTime(GraphCarTrajectory):
    CONFIG = {
        "y_min" : 0,
        "y_max" : 100,
        "y_axis_height" : 6,
        "y_tick_frequency" : 10,
        "y_labeled_nums" : list(range(10, 100, 10)),
        "y_axis_label" : "Distance (in meters)",
        "x_min" : -1,
        "x_max" : 9,
        "x_axis_width" : 9,
        "x_tick_frequency" : 1,
        "x_leftmost_tick" : None, #Change if different from x_min
        "x_labeled_nums" : list(range(1, 9)),
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
        "x_labeled_nums" : list(range(1, 9)),
        "x_axis_label" : "$t$",
        "y_min" : 0,
        "y_max" : 25,
        "y_axis_height" : 6,
        "y_tick_frequency" : 5,
        "y_labeled_nums" : list(range(5, 30, 5)),
        "y_axis_label" : "Velocity in $\\frac{\\text{meters}}{\\text{second}}$",
        "num_graph_anchor_points" : 50,
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
            lag_ratio = 0.5,
            rate_func=linear,
        ))

        self.speedometer = speedometer

    def plot_points(self):
        times = list(range(0, 9))
        points = [
            self.coords_to_point(t, v_func(t))
            for t in times
        ]
        dots = VGroup(*[Dot(p, radius = 0.07) for p in points])
        dots.set_color(VELOCITY_COLOR)

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
                *dot_intro_anims, rate_func=linear
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
        self.wait()

    def draw_curve(self):
        graph, label = self.get_v_graph_and_label()

        self.revert_to_original_skipping_status()
        self.play(ShowCreation(graph, run_time = 3))
        self.play(Write(graph_label))
        self.wait()

    ##

    def get_v_graph_and_label(self):
        graph = self.get_graph(
            v_func, 
            x_min = 0,
            x_max = 8,
            color = VELOCITY_COLOR
        )
        graph_label = TexMobject("v(t)", "=t(8-t)")
        graph_label.set_color_by_tex("v(t)", VELOCITY_COLOR)
        graph_label.next_to(
            graph.point_from_proportion(7./8.),
            UP+RIGHT
        )
        self.v_graph = graph
        self.v_graph_label = graph_label
        return graph, graph_label

class Chapter2Wrapper(Scene):
    CONFIG = {
        "title" : "Chapter 2: The paradox of the derivative",
    }
    def construct(self):
        title = TextMobject(self.title)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = WHITE)
        rect.set_height(1.5*FRAME_Y_RADIUS)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait(3)

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
        ds_dt.set_color_by_tex("ds", DISTANCE_COLOR)
        ds_dt.set_color_by_tex("dt", TIME_COLOR)
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
        self.wait()

    def write_antiderivative(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        randy.shift(2*RIGHT)
        words = TexMobject(
            "{d(", "???", ") \\over \\,", "dt}", "=", "t(8-t)"
        )
        words.set_color_by_tex("t(8-t)", VELOCITY_COLOR)
        words.set_color_by_tex("???", DISTANCE_COLOR)
        words.set_color_by_tex("dt", TIME_COLOR)
        words.scale(0.7)

        self.play(FadeIn(randy))
        self.play(PiCreatureSays(
            randy, words, 
            target_mode = "confused",
            bubble_kwargs = {"height" : 3, "width" : 4},
        ))
        self.play(Blink(randy))
        self.wait()

class Antiderivative(PiCreatureScene):
    def construct(self):
        functions = self.get_functions("t^2", "2t")
        alt_functions = self.get_functions("???", "t(8-t)")
        top_arc, bottom_arc = arcs = self.get_arcs(functions)
        derivative, antiderivative = self.get_arc_labels(arcs)
        group = VGroup(functions, arcs, derivative, antiderivative)

        self.add(functions, top_arc, derivative)
        self.wait()
        self.play(
            ShowCreation(bottom_arc),
            Write(antiderivative),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.wait(2)
        for pair in reversed(list(zip(functions, alt_functions))):
            self.play(
                Transform(*pair),
                self.pi_creature.change_mode, "pondering"
            )
        self.wait(2)

        self.pi_creature_says(
            "But first!", 
            target_mode = "surprised",
            look_at_arg = 50*OUT,
            added_anims = [group.to_edge, LEFT],
            run_time = 1,
        )
        self.wait()

    def get_functions(self, left_tex, right_tex):
        left = TexMobject(left_tex)
        left.shift(2*LEFT)
        left.set_color(DISTANCE_COLOR)
        right = TexMobject(right_tex)
        right.shift(2*RIGHT)
        right.set_color(VELOCITY_COLOR)
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
        arcs.set_width(top_line.get_width())
        for arc in arcs:
            arc.add_tip()
        top_arc.next_to(top_line, UP)
        bottom_arc.next_to(bottom_line, DOWN)
        bottom_arc.set_color(MAROON_B)

        return arcs

    def get_arc_labels(self, arcs):
        top_arc, bottom_arc = arcs
        derivative = TextMobject("Derivative")
        derivative.next_to(top_arc, UP)
        antiderivative = TextMobject("``Antiderivative''")
        antiderivative.next_to(bottom_arc, DOWN)
        antiderivative.set_color(bottom_arc.get_color())

        return VGroup(derivative, antiderivative)

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
                lag_ratio = 0.5
            ))
        self.wait()

class ConstantVelocityCar(Scene):
    def construct(self):
        car = Car()
        car.move_to(5*LEFT + 3*DOWN)

        self.add(car)
        self.wait()
        self.play(MoveCar(
            car, 7*RIGHT+3*DOWN,
            run_time = 5,
            rate_func=linear,
        ))
        self.wait()

class ConstantVelocityPlot(PlotVelocity):
    CONFIG = {
        "x_axis_label" : "Time",
        "units_of_area_color" : BLUE_E,
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

        self.play(ShowCreation(graph, rate_func=linear, run_time = 3))
        self.wait()

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
        v_label.set_color(VELOCITY_COLOR)
        t_label = top_brace.get_text(
            "8 seconds"
        )
        t_label.set_color(TIME_COLOR)

        s_label = TexMobject("10", "\\times",  "8", "\\text{ meters}")
        s_label.set_color_by_tex("10", VELOCITY_COLOR)
        s_label.set_color_by_tex("8", TIME_COLOR)
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
        self.wait(2)

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
            self.area_rect.set_color, YELLOW,
            *list(map(Animation, self.get_mobjects())),
            rate_func = there_and_back
        )
        self.play(Blink(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, randy.bubble,
            ShowCreation(bubble), 
            Write(bubble.content),
        )
        self.wait()
        self.play(Blink(randy))
        self.wait()
        self.play(
            randy.change_mode, "pondering",
            FadeOut(bubble),
            FadeOut(bubble.content),
        )

        self.randy = randy

    def note_units(self):
        x_line, y_line  = lines = VGroup(*[
            axis.copy()
            for axis in (self.x_axis, self.y_axis)
        ])
        lines.set_color(TIME_COLOR)
        square = Square(
            stroke_color = BLACK,
            stroke_width = 1,
            fill_color = self.units_of_area_color,
            fill_opacity = 1,
        )
        square.replace(
            VGroup(*[
                VectorizedPoint(self.coords_to_point(i, i))
                for i in (0, 1)
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
                    lag_ratio = 0.5,
                    run_time = 3
                ),
                Animation(self.s_label),
                self.randy.look_at, self.area_rect
            )
        self.play(Blink(self.randy))
        self.wait()

class PiecewiseConstantCar(Scene):
    def construct(self):
        car = Car()
        start_point = 5*LEFT
        car.move_to(start_point)

        self.add(car)
        self.wait()
        for shift in 2, 6, 12:
            car.randy.rotate_in_place(np.pi/8)
            anim = MoveCar(
                car, start_point+shift*RIGHT,
                rate_func=linear
            )

            anim.target_mobject[0].rotate_in_place(-np.pi/8)
            # for mob in anim.starting_mobject, anim.mobject:
            #     mob.randy.rotate_in_place(np.pi/6)
            self.play(anim)
        self.wait()

class PiecewiseConstantPlot(PlotVelocity):
    CONFIG = {
        "y_axis_label" : "",
        "min_graph_proportion" : 0.1,
        "max_graph_proportion" : 0.8,
        "num_riemann_approximations" : 7,
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
        self.label_integral()

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
        self.wait()
        self.play(FadeOut(group))

    def show_piecewise_constant_graph(self):
        pw_constant_graph = self.get_pw_constant_graph()
        alt_lines = [
            line.copy().set_color(YELLOW)
            for line in pw_constant_graph[:4]
        ]
        for line in alt_lines:
            line.start_dot = Dot(line.get_start())
            line.end_dot = Dot(line.get_end())
            VGroup(line.start_dot, line.end_dot).set_color(line.get_color())
        line = alt_lines[0]

        faders = [self.v_graph, self.v_graph_label]
        for mob in faders:
            mob.save_state()
            mob.generate_target()
            mob.target.fade(0.7)

        self.play(*list(map(MoveToTarget, faders)))
        self.play(ShowCreation(pw_constant_graph, run_time = 2))
        self.wait()
        self.play(ShowCreation(line))
        self.wait()
        for new_line in alt_lines[1:]:
            for mob in line.end_dot, new_line.start_dot, new_line:
                self.play(Transform(
                    line, mob,
                    run_time = 1./3
                ))
            self.remove(line)
            self.add(new_line)
            self.wait(2)
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
            self.wait()
        self.play(
            ReplacementTransform(
                flat_rects, rects,
                run_time = 2,
                lag_ratio = 0.5,
            ),
            Animation(right_brace)
        )
        self.play(*list(map(FadeOut, [top_brace, right_brace])))
        self.wait()

        self.rects = rects
        self.rect_list = rect_list

    def approximate_original_curve(self):
        rects = self.rects
        self.play(
            FadeOut(self.pw_constant_graph),
            *[
                m.restore 
                for m in (self.v_graph, self.v_graph_label)
            ]+[Animation(self.rects)]
        )
        for new_rects in self.rect_list[1:]:
            self.transform_between_riemann_rects(rects, new_rects)
            self.wait()

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
        example_text.set_color_by_tex("dt", YELLOW)

        self.play(ReplacementTransform(
            rects, target_rects,
            run_time = 2,
            lag_ratio = 0.5
        ))
        rects.restore()
        self.wait()
        self.play(
            ShowCreation(ticks),
            FadeOut(self.x_axis.numbers)
        )
        self.play(
            GrowFromCenter(brace),
            Write(dt_label)
        )
        self.wait()
        self.play(
            FadeIn(
                example_text, 
                run_time = 2,
                lag_ratio = 0.5,
            ),
            ReplacementTransform(
                dt_label.copy(),
                example_text.get_part_by_tex("dt")
            )
        )
        self.wait()

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
        self.wait()
        for label in t_labels:
            self.play(FadeIn(label))
        self.wait()
        for v_line, h_line, label in zip(v_lines, h_lines, height_labels):
            self.play(ShowCreation(v_line))
            self.play(ShowCreation(h_line))
            self.play(Write(label, run_time = 1))
            self.wait()
        self.wait()
        t_label_copy = t_labels[0].copy()
        self.play(
            t_label_copy.scale, 1./0.7,
            t_label_copy.next_to, self.v_graph_label, DOWN+LEFT, 0
        )
        self.wait()
        self.play(FadeOut(t_label_copy))
        self.wait()

        self.play(ShowCreation(circle))
        self.play(ShowCreation(rect_top))
        self.play(FadeOut(circle))
        rect.add(rect_top)
        self.wait()
        for x in range(2):
            self.play(
                rect.stretch_to_fit_height, v_lines[1].get_height(),
                rect.move_to, rect.get_bottom(), DOWN,
                Animation(v_lines),
                run_time = 4,
                rate_func = there_and_back
            )

        self.play(*list(map(FadeOut, [
            group[1]
            for group in (v_lines, h_lines, height_labels)
        ])))
        self.play(
            v_lines[0].set_color, RED,
            rate_func = there_and_back,
        )
        self.wait()

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
        self.wait(2)
        self.play(*list(map(FadeOut, [
            area, arrow, 
            v_lines[0], h_lines[0], height_labels[0],
            rect, t_labels
        ])))

    def show_v_dt_for_all_rectangles(self):
        dt_brace_group = VGroup(self.dt_brace, self.dt_label)
        rects_subset = self.rects[10:20]

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
            self.wait()

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
        bounds = list(map(integral.get_part_by_tex, ["0", "8"]))

        sum_word = TextMobject("``Sum''")
        sum_word.next_to(integral, DOWN, MED_LARGE_BUFF, LEFT)
        alt_sum_word = sum_word.copy()
        int_symbol = TexMobject("\\int")
        int_symbol.replace(alt_sum_word[1], dim_to_match = 1)
        alt_sum_word.submobjects[1] = int_symbol

        self.play(FadeOut(self.dt_example_text))
        self.play(Write(integral.get_part_by_tex("int")))
        self.wait()
        self.play(Transform(int_copy, int_symbol))
        self.play(Write(alt_sum_word), Animation(int_copy))
        self.remove(int_copy)
        self.play(ReplacementTransform(alt_sum_word, sum_word))
        self.wait()

        for bound in bounds:
            self.play(Write(bound))
        self.wait()
        for bound, num in zip(bounds, [0, 8]):
            bound_copy = bound.copy()
            point = self.coords_to_point(num, 0)
            self.play(
                bound_copy.scale, 1.5,
                bound_copy.next_to, point, DOWN, MED_LARGE_BUFF
            )
        self.play(ApplyWave(self.ticks, direction = UP))
        self.wait()

        for mob, tex in (self.v_t, "v(t)"), (self.dt_label, "dt"):
            self.play(ReplacementTransform(
                mob.copy().set_color(YELLOW), 
                integral.get_part_by_tex(tex),
                run_time = 2
            ))
        self.wait()

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
            dt_copy.set_color, YELLOW
        )
        self.play(Blink(morty))
        self.play(
            ReplacementTransform(
                dt_copy.copy(), int_dt,
                run_time = 2
            ),
            morty.look_at, int_dt
        )
        self.wait(2)
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
        self.wait()

        #Shrink dt just a bit
        self.play(
            morty.change_mode, "pondering",
            rects.set_fill, None, 0.75,
            *list(map(FadeOut, [
                dt_copy, self.v_t, self.v_t_brace
            ]))
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
                lag_ratio = 0.5
            ),
            Transform(
                self.ticks, self.get_ticks(next_rects),
                run_time = 2,
                lag_ratio = 0.5,
            ),
        )
        self.rects = rects = next_rects
        self.wait()
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
        self.wait()

        self.morty = morty

    def what_does_sum_approach(self):
        morty = self.morty
        rects = self.rects

        cross = TexMobject("\\times")
        cross.replace(self.sum_word, stretch = True)
        cross.set_color(RED)
        brace = Brace(self.integral, DOWN)
        dt_to_0 = brace.get_text("$dt \\to 0$")

        distance_words = TextMobject(
            "Area", "= Distance traveled"
        )
        distance_words.next_to(rects, UP)
        arrow = Arrow(
            distance_words[0].get_bottom(),
            rects.get_center(),
            color = WHITE
        )

        self.play(PiCreatureSays(
            morty, "Why not $\\Sigma$?",
            target_mode = "sassy"
        ))
        self.play(Blink(morty))
        self.wait()
        self.play(Write(cross))
        self.wait()
        self.play(
            RemovePiCreatureBubble(morty, target_mode = "plain"),
            *list(map(FadeOut, [
                cross, self.sum_word, self.ticks,
                self.dt_brace, self.dt_label,
            ]))
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
                    lag_ratio = 0.5
                ),
                morty.look_at, rects,
            )
            self.wait()

        self.play(
            Write(distance_words),
            ShowCreation(arrow),
            morty.change_mode, "pondering",
            morty.look_at, distance_words,
        )
        self.wait()
        self.play(Blink(morty))
        self.wait()

        self.area_arrow = arrow

    def label_integral(self):
        words = TextMobject("``Integral of $v(t)$''")
        words.to_edge(UP)
        arrow = Arrow(
            words.get_right(),
            self.integral.get_left()
        )

        self.play(Indicate(self.integral))
        self.play(Write(words, run_time = 2))
        self.play(ShowCreation(arrow))
        self.wait()
        self.play(*[
            ApplyFunction(
                lambda r : r.shift(0.2*UP).set_fill(None, 1),
                rect,
                run_time = 3,
                rate_func = squish_rate_func(
                    there_and_back,
                    alpha, alpha+0.2,
                )
            )
            for rect, alpha in zip(
                self.rects, 
                np.linspace(0, 0.8, len(self.rects))
            )
        ]+[
            Animation(self.area_arrow),
            self.morty.change_mode, "happy",
            self.morty.look_at, self.rects,
        ])
        self.wait()

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
            line.set_color(self.v_graph.get_color())
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
        ticks.set_color(YELLOW)
        return ticks

class DontKnowHowToHandleNonConstant(TeacherStudentsScene):
    def construct(self):
        self.play(*[
            ApplyMethod(pi.change, "maybe", UP)
            for pi in self.get_pi_creatures()
        ])
        self.wait(3)

class CarJourneyApproximation(Scene):
    CONFIG = {
        "n_jumps" : 5,
        "bottom_words" : "Approximated motion (5 jumps)",
    }
    def construct(self):
        points = [5*LEFT + v for v in (UP, 2*DOWN)]
        cars = [Car().move_to(point) for point in points]
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        words = [
            TextMobject("Real motion (smooth)").shift(3*UP),
            TextMobject(self.bottom_words).shift(0.5*DOWN),
        ]
        words[1].set_color(GREEN)


        self.add(h_line, *cars + words)
        self.wait()
        self.play(*[
            MoveCar(
                car, point+10*RIGHT,
                run_time = 5,
                rate_func = rf
            )
            for car, point, rf in zip(cars, points, [
                s_rate_func,
                self.get_approximated_rate_func(self.n_jumps)
            ])
        ])
        self.wait()

    def get_approximated_rate_func(self, n):
        new_v_rate_func = lambda t : v_rate_func(np.floor(t*n)/n)
        max_integral, err = scipy.integrate.quad(
            v_rate_func, 0, 1
        )
        def result(t):
            integral, err = scipy.integrate.quad(new_v_rate_func, 0, t)
            return integral/max_integral
        return result

class LessWrongCarJourneyApproximation(CarJourneyApproximation):
    CONFIG = {
        "n_jumps" : 20,
        "bottom_words" : "Better approximation (20 jumps)",
    }

class TellMeThatsNotSurprising(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Tell me that's \\\\ not surprising!",
            target_mode = "hooray",
            run_time = 1
        )
        self.wait(3)

class HowDoesThisHelp(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "How does this help\\textinterrobang",
            target_mode = "angry",
            run_time = 1
        )
        self.change_student_modes(
            "confused", "angry", "confused",
        )
        self.wait(2)
        self.teacher_says(
            "You're right.",
            target_mode = "shruggie",
            run_time = 1
        )
        self.change_student_modes(*["sassy"]*3)
        self.wait(2)

class AreaUnderACurve(GraphScene):
    CONFIG = {
        "y_max" : 4,
        "y_min" : 0,
        "num_iterations" : 7
    }
    def construct(self):
        self.setup_axes()
        graph = self.get_graph(self.func)
        rect_list = self.get_riemann_rectangles_list(
            graph, self.num_iterations
        )
        VGroup(*rect_list).set_fill(opacity = 0.8)
        rects = rect_list[0]

        self.play(ShowCreation(graph))
        self.play(Write(rects))
        for new_rects in rect_list[1:]:
            rects.align_submobjects(new_rects)
            for every_other_rect in rects[::2]:
                every_other_rect.set_fill(opacity = 0)
            self.play(Transform(
                rects, new_rects,
                run_time = 2,
                lag_ratio = 0.5
            ))
        self.wait()


    def func(self, x):
        return np.sin(x) + 1

class AltAreaUnderCurve(AreaUnderACurve):
    CONFIG = {
        "graph_origin" : 2*DOWN,
        "x_min" : -3,
        "x_max" : 3,
        "x_axis_width" : 12,
        "y_max" : 2,
        "y_axis_height" : 4,
    }
    def func(self, x):
        return np.exp(-x**2)

class Chapter1Wrapper(Chapter2Wrapper):
    CONFIG = {
        "title" : "Essence of calculus, chapter 1",
    }

class AreaIsDerivative(PlotVelocity, ReconfigurableScene):
    CONFIG = {
        "y_axis_label" : "",
        "num_rects" : 400,
        "dT" : 0.25,
        "variable_point_label" : "T",
        "area_opacity" : 0.8,
    }
    def setup(self):
        PlotVelocity.setup(self)
        ReconfigurableScene.setup(self)
        self.setup_axes()
        self.add(*self.get_v_graph_and_label())
        self.x_axis_label_mob.shift(MED_LARGE_BUFF*DOWN)
        self.v_graph_label.shift(MED_LARGE_BUFF*DOWN)
        self.foreground_mobjects = []

    def construct(self):
        self.introduce_variable_area()
        self.write_integral()
        self.nudge_input()
        self.show_rectangle_approximation()

    def introduce_variable_area(self):
        area = self.area = self.get_area(0, 6)
        x_nums = self.x_axis.numbers

        self.play(Write(area, run_time = 2))
        self.play(FadeOut(self.x_axis.numbers))
        self.add_T_label(6)
        self.change_area_bounds(
            new_t_max = 4,
            rate_func = there_and_back,
            run_time = 2
        )
        self.wait()

    def write_integral(self):
        integral = TexMobject("\\int", "^T", "_0", "v(t)", "\\,dt")
        integral.to_corner(UP+RIGHT)
        integral.shift(2*LEFT)
        top_T = integral.get_part_by_tex("T")
        moving_T = self.T_label_group[0]

        s_T = TexMobject("s(T)", "= ")
        s_T.set_color_by_tex("s", DISTANCE_COLOR)
        s_T.next_to(integral, LEFT)

        int_arrow, s_arrow = [
            Arrow(
                mob.get_left(), self.area.get_center(),
                color = WHITE
            )
            for mob in (integral, s_T)
        ]

        distance_word = TextMobject("Distance")
        distance_word.move_to(self.area)

        self.play(Write(integral))
        self.play(ShowCreation(int_arrow))
        self.foreground_mobjects.append(int_arrow)
        self.wait()
        self.change_area_bounds(
            new_t_max = 8,
            rate_func = there_and_back,
            run_time = 3,
        )
        self.play(Indicate(top_T))
        self.play(ReplacementTransform(
            top_T.copy(), moving_T
        ))
        self.change_area_bounds(
            new_t_max = 3,
            rate_func = there_and_back,
            run_time = 3
        )
        self.wait()
        self.play(Write(distance_word, run_time = 2))
        self.play(
            ReplacementTransform(int_arrow, s_arrow),
            FadeIn(s_T)
        )
        self.wait()
        self.play(FadeOut(distance_word))
        self.change_area_bounds(new_t_max = 0, run_time = 2)
        self.change_area_bounds(
            new_t_max = 8, 
            rate_func=linear,
            run_time = 7.9,
        )
        self.wait()
        self.change_area_bounds(new_t_max = 5)
        self.wait()

    def nudge_input(self):
        dark_area = self.area.copy()
        dark_area.set_fill(BLACK, opacity = 0.5)
        curr_T = self.x_axis.point_to_number(self.area.get_right())
        new_T = curr_T + self.dT

        rect = Rectangle(
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = 0.75
        )
        rect.replace(
            VGroup(
                VectorizedPoint(self.coords_to_point(new_T, 0)),
                self.right_v_line,
            ),
            stretch = True
        )

        dT_brace = Brace(rect, DOWN, buff = 0)
        dT_label = dT_brace.get_text("$dT$", buff = SMALL_BUFF)
        dT_label_group = VGroup(dT_label, dT_brace)

        ds_label = TexMobject("ds")
        ds_label.next_to(rect, RIGHT, LARGE_BUFF, UP)
        ds_label.set_color(DISTANCE_COLOR)
        ds_arrow = Arrow(ds_label.get_left(), rect.get_left())
        ds_arrow.set_color(WHITE)

        v_brace = Brace(rect, LEFT, buff = SMALL_BUFF)
        v_T_label = v_brace.get_text("$v(T)$", buff = SMALL_BUFF)

        self.change_area_bounds(new_t_max = new_T)
        self.play(
            FadeIn(dark_area),
            *list(map(Animation, self.foreground_mobjects))
        )
        self.play(
            FadeOut(self.T_label_group),
            FadeIn(dT_label_group)
        )
        self.wait()
        self.play(Write(ds_label))
        self.play(ShowCreation(ds_arrow))
        self.wait(2)
        self.play(GrowFromCenter(v_brace))
        self.play(ReplacementTransform(
            self.v_graph_label.get_part_by_tex("v").copy(),
            v_T_label,
            run_time = 2
        ))
        self.wait()
        self.play(Indicate(dT_label))
        self.wait()

        self.rect = rect
        self.dT_label_group = dT_label_group
        self.v_T_label_group = VGroup(v_T_label, v_brace)
        self.dark_area = dark_area
        self.ds_label = ds_label
        self.ds_arrow = ds_arrow

    def show_rectangle_approximation(self):
        formula1 = TexMobject("ds", "=", "v(T)", "dT")
        formula2 = TexMobject("{ds", "\\over\\,", "dT}", "=", "v(T)")
        for formula in formula1, formula2:
            formula.next_to(self.v_graph_label, UP, LARGE_BUFF)
            formula.set_color_by_tex("ds", DISTANCE_COLOR)

        self.play(
            DrawBorderThenFill(self.rect),
            Animation(self.ds_arrow)
        )
        self.wait()
        self.play(*[
            ReplacementTransform(
                mob, formula1.get_part_by_tex(tex),
                run_time = 2
            )
            for mob, tex in [
                (self.ds_label, "ds"),
                (self.ds_arrow, "="),
                (self.v_T_label_group[0].copy(), "v(T)"),
                (self.dT_label_group[0].copy(), "dT"),
            ]
        ])
        self.wait()
        self.transition_to_alt_config(
            dT = self.dT/5.0,
            transformation_kwargs = {"run_time" : 2},
        )
        self.wait()
        self.play(*[
            ReplacementTransform(
                formula1.get_part_by_tex(tex),
                formula2.get_part_by_tex(tex),
            )
            for tex in ("ds", "=", "v(T)", "dT")
        ] + [
            Write(formula2.get_part_by_tex("over"))
        ])
        self.wait()


    ####

    def add_T_label(self, x_val, **kwargs):
        triangle = RegularPolygon(n=3, start_angle = np.pi/2)
        triangle.set_height(MED_SMALL_BUFF)
        triangle.move_to(self.coords_to_point(x_val, 0), UP)
        triangle.set_fill(WHITE, 1)
        triangle.set_stroke(width = 0)
        T_label = TexMobject(self.variable_point_label)
        T_label.next_to(triangle, DOWN)
        v_line = self.get_vertical_line_to_graph(
            x_val, self.v_graph,
            color = YELLOW
        )

        self.play(
            DrawBorderThenFill(triangle),
            ShowCreation(v_line),
            Write(T_label, run_time = 1),
            **kwargs
        )

        self.T_label_group = VGroup(T_label, triangle)
        self.right_v_line = v_line

    def get_area(self, t_min, t_max):
        numerator = max(t_max - t_min, 0.01)
        dx = float(numerator) / self.num_rects
        return self.get_riemann_rectangles(
            self.v_graph,
            x_min = t_min,
            x_max = t_max,
            dx = dx,
            stroke_width = 0,
        ).set_fill(opacity = self.area_opacity)

    def change_area_bounds(self, new_t_min = None, new_t_max = None, **kwargs):
        curr_t_min = self.x_axis.point_to_number(self.area.get_left())
        curr_t_max = self.x_axis.point_to_number(self.area.get_right())
        if new_t_min is None:
            new_t_min = curr_t_min
        if new_t_max is None:
            new_t_max = curr_t_max

        group = VGroup(self.area, self.right_v_line, self.T_label_group)
        def update_group(group, alpha):
            area, v_line, T_label = group
            t_min = interpolate(curr_t_min, new_t_min, alpha)
            t_max = interpolate(curr_t_max, new_t_max, alpha)
            new_area = self.get_area(t_min, t_max)
            new_v_line = self.get_vertical_line_to_graph(
                t_max, self.v_graph
            )
            new_v_line.set_color(v_line.get_color())
            T_label.move_to(new_v_line.get_bottom(), UP)

            #Fade close to 0
            T_label[0].set_fill(opacity = min(1, t_max)) 

            Transform(area, new_area).update(1)
            Transform(v_line, new_v_line).update(1)
            return group

        self.play(
            UpdateFromAlphaFunc(group, update_group),
            *list(map(Animation, self.foreground_mobjects)),
            **kwargs
        )

class DirectInterpretationOfDsDt(TeacherStudentsScene):
    def construct(self):
        equation = TexMobject("{ds", "\\over\\,", "dT}", "(T)", "=", "v(T)")
        ds, over, dt, of_T, equals, v = equation
        equation.next_to(self.get_pi_creatures(), UP, LARGE_BUFF)
        equation.shift(RIGHT)
        v.set_color(VELOCITY_COLOR)

        s_words = TextMobject("Tiny change in", "distance")
        s_words.next_to(ds, UP+LEFT, LARGE_BUFF)
        s_words.shift_onto_screen()
        s_arrow = Arrow(s_words[1].get_bottom(), ds.get_left())
        s_words.add(s_arrow)
        s_words.set_color(DISTANCE_COLOR)

        t_words = TextMobject("Tiny change in", "time")
        t_words.next_to(dt, DOWN+LEFT)
        t_words.to_edge(LEFT)
        t_arrow = Arrow(t_words[1].get_top(), dt.get_left())
        t_words.add(t_arrow)
        t_words.set_color(TIME_COLOR)

        self.add(ds, over, dt, of_T)
        for words, part in (s_words, ds), (t_words, dt):
            self.play(
                FadeIn(
                    words, 
                    run_time = 2,
                    lag_ratio = 0.5,
                ),
                self.students[1].change_mode, "raise_right_hand"
            )
            self.play(part.set_color, words.get_color())
        self.wait()
        self.play(Write(VGroup(equals, v)))
        self.change_student_modes(*["pondering"]*3)
        self.wait(3)

class FindAntiderivative(Antiderivative):
    def construct(self):
        self.introduce()
        self.first_part()
        self.second_part()
        self.combine()
        self.add_plus_C()

    def introduce(self):
        q_marks, rhs = functions = self.get_functions("???", "t(8-t)")
        expanded_rhs = TexMobject("8t - t^2")
        expanded_rhs.move_to(rhs, LEFT)
        expanded_rhs.set_color(rhs.get_color())
        self.v_part1 = VGroup(*expanded_rhs[:2])
        self.v_part2 = VGroup(*expanded_rhs[2:])
        for part in self.v_part1, self.v_part2:
            part.save_state()

        top_arc, bottom_arc = arcs = self.get_arcs(functions)
        derivative, antiderivative = words = self.get_arc_labels(arcs)

        self.add(functions)
        self.play(*list(map(ShowCreation, arcs)))
        for word in words:
            self.play(FadeIn(word, lag_ratio = 0.5))
        self.wait()
        self.change_mode("confused")
        self.wait(2)
        self.play(*[
            ReplacementTransform(
                rhs[i], expanded_rhs[j],
                run_time = 2,
                path_arc = np.pi
            )
            for i, j in enumerate([1, 4, 0, 2, 3, 4])
        ]+[
            self.pi_creature.change_mode, "hesitant"
        ])
        self.wait()

        self.q_marks = q_marks
        self.arcs = arcs
        self.words = words

    def first_part(self):
        four_t_squared, two_t = self.get_functions("4t^2", "2t")
        four = four_t_squared[0]
        four.shift(UP)
        four.set_fill(opacity = 0)
        t_squared = VGroup(*four_t_squared[1:])
        two_t.move_to(self.v_part1, LEFT)

        self.play(self.v_part2.to_corner, UP+RIGHT)
        self.play(
            self.pi_creature.change, "plain", self.v_part1
        )
        self.play(ApplyWave(
            self.q_marks, 
            direction = UP, 
            amplitude = SMALL_BUFF
        ))
        self.wait(2)
        self.play(
            FadeOut(self.q_marks),
            FadeIn(t_squared),
            self.v_part1.shift, DOWN+RIGHT,
        )
        self.play(*[
            ReplacementTransform(
                t_squared[i].copy(), two_t[1-i],
                run_time = 2,
                path_arc = -np.pi/6.
            )
            for i in (0, 1)
        ])
        self.change_mode("thinking")
        self.wait()
        self.play(four.set_fill, YELLOW, 1)
        self.play(four.shift, DOWN)
        self.play(FadeOut(two_t))
        self.play(self.v_part1.restore)
        self.play(four.set_color, DISTANCE_COLOR)
        self.wait(2)

        self.s_part1 = four_t_squared

    def second_part(self):
        self.arcs_copy = self.arcs.copy()
        self.words_copy = self.words.copy()
        part1_group = VGroup(
            self.s_part1, self.v_part1, 
            self.arcs_copy, self.words_copy
        )

        neg_third_t_cubed, three_t_squared = self.get_functions(
            "- \\frac{1}{3} t^3", "3t^2"
        )
        three_t_squared.move_to(self.v_part1, LEFT)
        neg = neg_third_t_cubed[0]
        third = VGroup(*neg_third_t_cubed[1:4])
        t_cubed = VGroup(*neg_third_t_cubed[4:])
        three = three_t_squared[0]
        t_squared = VGroup(*three_t_squared[1:])

        self.play(
            part1_group.scale, 0.5,
            part1_group.to_corner, UP+LEFT,
            self.pi_creature.change_mode, "plain"
        )
        self.play(
            self.v_part2.restore,
            self.v_part2.shift, LEFT
        )
        self.play(FadeIn(self.q_marks))
        self.wait()

        self.play(
            FadeOut(self.q_marks),
            FadeIn(t_cubed),
            self.v_part2.shift, DOWN+RIGHT
        )
        self.play(*[
            ReplacementTransform(
                t_cubed[i].copy(), three_t_squared[j],
                path_arc = -np.pi/6,
                run_time = 2,
            )
            for i, j in [(0, 1), (1, 0), (1, 2)]
        ])
        self.wait()
        self.play(FadeIn(third))
        self.play(FadeOut(three))
        self.wait(2)
        self.play(Write(neg))
        self.play(
            FadeOut(t_squared),
            self.v_part2.shift, UP+LEFT
        )
        self.wait(2)

        self.s_part2 = neg_third_t_cubed

    def combine(self):
        self.play(
            self.v_part1.restore,
            self.v_part2.restore,
            self.s_part1.scale, 2,
            self.s_part1.next_to, self.s_part2, LEFT,
            FadeOut(self.arcs_copy),
            FadeOut(self.words_copy),
            run_time = 2,
        )
        self.change_mode("happy")
        self.wait(2)

    def add_plus_C(self):
        s_group = VGroup(self.s_part1, self.s_part2)
        plus_Cs = [
            TexMobject("+%d"%d)
            for d in range(1, 8)
        ]
        for plus_C in plus_Cs:
            plus_C.set_color(YELLOW)
            plus_C.move_to(s_group, RIGHT)
        plus_C = plus_Cs[0]

        self.change_mode("sassy")
        self.wait()
        self.play(
            s_group.next_to, plus_C.copy(), LEFT,
            GrowFromCenter(plus_C),
        )
        self.wait()
        for new_plus_C in plus_Cs[1:]:
            self.play(Transform(plus_C, new_plus_C))
            self.wait()

class GraphSPlusC(GraphDistanceVsTime):
    CONFIG = {
        "y_axis_label" : "Distance"
    }
    def construct(self):
        self.setup_axes()
        graph = self.get_graph(
            s_func, 
            color = DISTANCE_COLOR,
            x_min = 0,
            x_max = 8,
        )
        tangent = self.get_secant_slope_group(
            6, graph, dx = 0.01
        ).secant_line
        v_line = self.get_vertical_line_to_graph(
            6, graph, line_class = DashedLine
        )
        v_line.scale_in_place(2)
        v_line.set_color(WHITE)
        graph_label, plus_C = full_label = TexMobject(
            "s(t) = 4t^2 - \\frac{1}{3}t^3", "+C"
        )
        plus_C.set_color(YELLOW)
        full_label.next_to(graph.points[-1], DOWN)
        full_label.to_edge(RIGHT)

        self.play(ShowCreation(graph))
        self.play(FadeIn(graph_label))
        self.wait()
        self.play(
            graph.shift, UP,
            run_time = 2,
            rate_func = there_and_back
        )
        self.play(ShowCreation(tangent))
        graph.add(tangent)
        self.play(ShowCreation(v_line))
        self.play(
            graph.shift, 2*DOWN, 
            run_time = 4,
            rate_func = there_and_back,
        )
        self.play(Write(plus_C))
        self.play(
            graph.shift, 2*UP,
            rate_func = there_and_back,
            run_time = 4,
        )
        self.wait()

class LowerBound(AreaIsDerivative):
    CONFIG = {
        "graph_origin" : 2.5*DOWN + 6*LEFT
    }

    def construct(self):
        self.add_integral_and_area()
        self.mention_lower_bound()
        self.drag_right_endpoint_to_zero()
        self.write_antiderivative_difference()
        self.show_alternate_antiderivative_difference()
        self.add_constant_to_antiderivative()

    def add_integral_and_area(self):
        self.area = self.get_area(0, 6)
        self.integral = self.get_integral("0", "T")
        self.remove(self.x_axis.numbers)
        self.add(self.area, self.integral)
        self.add_T_label(6, run_time = 0)

    def mention_lower_bound(self):
        lower_bound = self.integral.get_part_by_tex("0")
        circle = Circle(color = YELLOW)
        circle.replace(lower_bound)
        circle.scale_in_place(3)
        zero_label = lower_bound.copy()

        self.play(ShowCreation(circle))
        self.play(Indicate(lower_bound))
        self.play(
            zero_label.scale, 1.5,
            zero_label.next_to, self.graph_origin, DOWN, MED_LARGE_BUFF,
            FadeOut(circle)
        )
        self.wait()

        self.zero_label = zero_label

    def drag_right_endpoint_to_zero(self):
        zero_integral = self.get_integral("0", "0")
        zero_integral[1].set_color(YELLOW)
        zero_int_bounds = list(reversed(
            zero_integral.get_parts_by_tex("0")
        ))
        for bound in zero_int_bounds:
            circle = Circle(color = YELLOW)
            circle.replace(bound)
            circle.scale_in_place(3)
            bound.circle = circle
        self.integral.save_state()
        equals_zero = TexMobject("=0")
        equals_zero.next_to(zero_integral, RIGHT)
        equals_zero.set_color(GREEN)

        self.change_area_bounds(0, 0, run_time = 3)
        self.play(ReplacementTransform(
            self.zero_label.copy(), equals_zero
        ))
        self.play(Transform(self.integral, zero_integral))
        self.wait(2)
        for bound in zero_int_bounds:
            self.play(ShowCreation(bound.circle))
            self.play(FadeOut(bound.circle))
        self.play(*[
            ReplacementTransform(
                bound.copy(), VGroup(equals_zero[1])
            )
            for bound in zero_int_bounds
        ])
        self.wait(2)
        self.change_area_bounds(0, 5)
        self.play(
            self.integral.restore,
            FadeOut(equals_zero)
        )

        self.zero_integral = zero_integral

    def write_antiderivative_difference(self):
        antideriv_diff = self.get_antiderivative_difference("0", "T")
        equals, at_T, minus, at_zero = antideriv_diff
        antideriv_diff_at_eight = self.get_antiderivative_difference("0", "8")
        at_eight = antideriv_diff_at_eight.left_part
        integral_at_eight = self.get_integral("0", "8")

        for part in at_T, at_zero, at_eight:
            part.brace = Brace(part, DOWN, buff = SMALL_BUFF)
            part.brace.save_state()

        antideriv_text = at_T.brace.get_text("Antiderivative", buff = SMALL_BUFF)
        antideriv_text.set_color(MAROON_B)
        value_at_eight = at_eight.brace.get_text(
            "%.2f"%s_func(8)
        )
        happens_to_be_zero = at_zero.brace.get_text("""
            Happens to
            equal 0
        """)

        big_brace = Brace(VGroup(at_T, at_zero))
        cancel_text = big_brace.get_text("Cancels when $T=0$")

        self.play(*list(map(Write, [equals, at_T])))
        self.play(
            GrowFromCenter(at_T.brace),
            Write(antideriv_text, run_time = 2)
        )
        self.change_area_bounds(0, 5.5, rate_func = there_and_back)
        self.wait()
        self.play(
            ReplacementTransform(at_T.copy(), at_zero),
            Write(minus)
        )
        self.wait()
        self.play(
            ReplacementTransform(at_T.brace, big_brace),
            ReplacementTransform(antideriv_text, cancel_text)
        )
        self.change_area_bounds(0, 0, run_time = 4)
        self.wait()
        self.play(
            ReplacementTransform(big_brace, at_zero.brace),
            ReplacementTransform(cancel_text, happens_to_be_zero),
        )
        self.wait(2)
        self.change_area_bounds(0, 8, run_time = 2)
        self.play(
            Transform(self.integral, integral_at_eight),
            Transform(antideriv_diff, antideriv_diff_at_eight),
            MaintainPositionRelativeTo(at_zero.brace, at_zero),
            MaintainPositionRelativeTo(happens_to_be_zero, at_zero.brace),
        )
        self.play(
            GrowFromCenter(at_eight.brace),
            Write(value_at_eight)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [
            at_eight.brace, value_at_eight,
            at_zero.brace, happens_to_be_zero,
        ])))

        self.antideriv_diff = antideriv_diff

    def show_alternate_antiderivative_difference(self):
        new_integral = self.get_integral("1", "7")
        new_antideriv_diff = self.get_antiderivative_difference("1", "7")
        numbers = [
            TexMobject("%d"%d).next_to(
                self.coords_to_point(d, 0), 
                DOWN, MED_LARGE_BUFF
            )
            for d in (1, 7)
        ]
        tex_mobs = [new_integral]+new_antideriv_diff[1::2]+numbers
        for tex_mob in tex_mobs:
            tex_mob.set_color_by_tex("1", RED)
            tex_mob.set_color_by_tex("7", GREEN)
            tex_mob.set_color_by_tex("\\frac{1}{3}", WHITE)

        self.change_area_bounds(1, 7, run_time = 2)
        self.play(
            self.T_label_group[0].set_fill, None, 0,
            *list(map(FadeIn, numbers))
        )
        self.play(
            Transform(self.integral, new_integral),
            Transform(self.antideriv_diff, new_antideriv_diff),
        )
        self.wait(3)
        for part in self.antideriv_diff[1::2]:
            self.play(Indicate(part, scale_factor = 1.1))
            self.wait()

    def add_constant_to_antiderivative(self):
        antideriv_diff = self.antideriv_diff
        plus_fives = VGroup(*[TexMobject("+5") for i in range(2)])
        plus_fives.set_color(YELLOW)
        for five, part in zip(plus_fives, antideriv_diff[1::2]):
            five.next_to(part, DOWN)
        group = VGroup(
            plus_fives[0],
            antideriv_diff[2].copy(),
            plus_fives[1]
        )

        self.play(Write(plus_fives, run_time = 2))
        self.wait(2)
        self.play(
            group.arrange,
            group.next_to, antideriv_diff, DOWN, MED_LARGE_BUFF
        )
        self.wait()
        self.play(FadeOut(group, run_time = 2))
        self.wait()

    #####

    def get_integral(self, lower_bound, upper_bound):
        result = TexMobject(
            "\\int", "^"+upper_bound, "_"+lower_bound, 
            "t(8-t)", "\\,dt"
        )
        result.next_to(self.graph_origin, RIGHT, MED_LARGE_BUFF)
        result.to_edge(UP)
        return result

    def get_antiderivative_difference(self, lower_bound, upper_bound):
        strings = []
        for bound in upper_bound, lower_bound:
            try:
                d = int(bound)
                strings.append("(%d)"%d)
            except:
                strings.append(bound)
        parts = []
        for s in strings:
            part = TexMobject(
                "\\left(",
                "4", s, "^2", "-", "\\frac{1}{3}", s, "^3"
                "\\right))"
            )
            part.set_color_by_tex(s, YELLOW, substring = False)
            parts.append(part)
        result = VGroup(
            TexMobject("="), parts[0], 
            TexMobject("-"), parts[1],
        )
        result.left_part, result.right_part = parts
        result.arrange(RIGHT)
        result.scale(0.9)
        result.next_to(self.integral, RIGHT)
        return result

class FundamentalTheorem(GraphScene):
    CONFIG = {
        "lower_bound" : 1,
        "upper_bound" : 7,
        "lower_bound_color" : RED,
        "upper_bound_color" : GREEN,
        "n_riemann_iterations" : 6,
    }

    def construct(self):
        self.add_graph_and_integral()
        self.show_f_dx_sum()
        self.show_rects_approaching_area()
        self.write_antiderivative()
        self.write_fundamental_theorem_of_calculus()
        self.show_integral_considering_continuum()
        self.show_antiderivative_considering_bounds()

    def add_graph_and_integral(self):
        self.setup_axes()
        integral = TexMobject("\\int", "^b", "_a", "f(x)", "\\,dx")
        integral.next_to(ORIGIN, LEFT)
        integral.to_edge(UP)
        integral.set_color_by_tex("a", self.lower_bound_color)
        integral.set_color_by_tex("b", self.upper_bound_color)
        graph = self.get_graph(
            lambda x : -0.01*x*(x-3)*(x-6)*(x-12) + 3,
        )
        self.add(integral, graph)
        self.graph = graph
        self.integral = integral

        self.bound_labels = VGroup()
        self.v_lines = VGroup()
        for bound, tex in (self.lower_bound, "a"), (self.upper_bound, "b"):
            label = integral.get_part_by_tex(tex).copy()
            label.scale(1.5)
            label.next_to(self.coords_to_point(bound, 0), DOWN)
            v_line = self.get_vertical_line_to_graph(
                bound, graph, color = label.get_color()
            )

            self.bound_labels.add(label)
            self.v_lines.add(v_line)
            self.add(label, v_line)

    def show_f_dx_sum(self):
        kwargs = {
            "x_min" : self.lower_bound,
            "x_max" : self.upper_bound,
            "fill_opacity" : 0.75,
            "stroke_width" : 0.25,
        }
        low_opacity = 0.25
        start_rect_index = 3
        num_shown_sum_steps = 5
        last_rect_index = start_rect_index + num_shown_sum_steps + 1

        self.rect_list = self.get_riemann_rectangles_list(
            self.graph, self.n_riemann_iterations, **kwargs
        )
        rects = self.rects = self.rect_list[0]
        rects.save_state()

        start_rect = rects[start_rect_index]
        f_brace = Brace(start_rect, LEFT, buff = 0)
        dx_brace = Brace(start_rect, DOWN, buff = 0)
        f_brace.label = f_brace.get_text("$f(x)$")
        dx_brace.label = dx_brace.get_text("$dx$")

        flat_rects = self.get_riemann_rectangles(
            self.get_graph(lambda x : 0), dx = 0.5, **kwargs
        )

        self.transform_between_riemann_rects(
            flat_rects, rects, 
            replace_mobject_with_target_in_scene = True,
        )
        self.play(*[
            ApplyMethod(
                rect.set_fill, None, 
                1 if rect is start_rect else low_opacity
            )
            for rect in rects
        ])
        self.play(*it.chain(
            list(map(GrowFromCenter, [f_brace, dx_brace])),
            list(map(Write, [f_brace.label, dx_brace.label])),
        ))
        self.wait()
        for i in range(start_rect_index+1, last_rect_index):
            self.play(
                rects[i-1].set_fill, None, low_opacity,
                rects[i].set_fill, None, 1,
                f_brace.set_height, rects[i].get_height(),
                f_brace.next_to, rects[i], LEFT, 0,
                dx_brace.next_to, rects[i], DOWN, 0,
                *[
                    MaintainPositionRelativeTo(brace.label, brace)
                    for brace in (f_brace, dx_brace)
                ]
            )
        self.wait()
        self.play(*it.chain(
            list(map(FadeOut, [
                f_brace, dx_brace, 
                f_brace.label, dx_brace.label
            ])),
            [rects.set_fill, None, kwargs["fill_opacity"]]
        ))

    def show_rects_approaching_area(self):
        for new_rects in self.rect_list:
            self.transform_between_riemann_rects(
                self.rects, new_rects
            )

    def write_antiderivative(self):
        deriv = TexMobject(
            "{d", "F", "\\over\\,", "dx}", "(x)", "=", "f(x)"
        )
        deriv_F = deriv.get_part_by_tex("F")
        deriv.next_to(self.integral, DOWN, MED_LARGE_BUFF)
        rhs = TexMobject(*"=F(b)-F(a)")
        rhs.set_color_by_tex("a", self.lower_bound_color)
        rhs.set_color_by_tex("b", self.upper_bound_color)
        rhs.next_to(self.integral, RIGHT)

        self.play(Write(deriv))
        self.wait(2)
        self.play(*it.chain(
            [
                ReplacementTransform(deriv_F.copy(), part)
                for part in rhs.get_parts_by_tex("F")
            ],
            [
                Write(VGroup(*rhs.get_parts_by_tex(tex)))
                for tex in "=()-"
            ]
        ))
        for tex in "b", "a":
            self.play(ReplacementTransform(
                self.integral.get_part_by_tex(tex).copy(),
                rhs.get_part_by_tex(tex)
            ))
            self.wait()
        self.wait(2)

        self.deriv = deriv
        self.rhs = rhs

    def write_fundamental_theorem_of_calculus(self):
        words = TextMobject("""
            Fundamental 
            theorem of 
            calculus
        """)
        words.to_edge(RIGHT)

        self.play(Write(words))
        self.wait()

    def show_integral_considering_continuum(self):
        self.play(*[
            ApplyMethod(mob.set_fill, None, 0.2)
            for mob in (self.deriv, self.rhs)
        ])
        self.play(
            self.rects.restore,
            run_time = 3,
            rate_func = there_and_back
        )
        self.wait()
        for x in range(2):
            self.play(*[
                ApplyFunction(
                    lambda m : m.shift(MED_SMALL_BUFF*UP).set_fill(opacity = 1),
                    rect,
                    run_time = 3,
                    rate_func = squish_rate_func(
                        there_and_back,
                        alpha, alpha+0.2
                    )
                )
                for rect, alpha in zip(
                    self.rects, 
                    np.linspace(0, 0.8, len(self.rects))
                )
            ])
        self.wait()

    def show_antiderivative_considering_bounds(self):
        self.play(
            self.integral.set_fill, None, 0.5,
            self.deriv.set_fill, None, 1,
            self.rhs.set_fill, None, 1,
        )
        for label, line in reversed(list(zip(self.bound_labels, self.v_lines))):
            new_line = line.copy().set_color(YELLOW)
            label.save_state()
            self.play(label.set_color, YELLOW)
            self.play(ShowCreation(new_line))
            self.play(ShowCreation(line))
            self.remove(new_line)
            self.play(label.restore)
        self.wait()
        self.play(self.integral.set_fill, None, 1)
        self.wait(3)

class LetsRecap(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Let's recap",
            target_mode = "hesitant",
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(3)

class NegativeArea(GraphScene):
    CONFIG = {
        "x_axis_label" : "Time",
        "y_axis_label" : "Velocity",
        "graph_origin" : 1.5*DOWN + 5*LEFT,
        "y_min" : -3,
        "y_max" : 7,
        "small_dx" : 0.01,
        "sample_input" : 5,
    }
    def construct(self):
        self.setup_axes()
        self.add_graph_and_area()
        self.write_negative_area()
        self.show_negative_point()
        self.show_car_going_backwards()
        self.write_v_dt()
        self.show_rectangle()
        self.write_signed_area()

    def add_graph_and_area(self):
        graph = self.get_graph(
            lambda x : -0.02*(x+1)*(x-3)*(x-7)*(x-10),
            x_min = 0,
            x_max = 8,
            color = VELOCITY_COLOR
        )
        area = self.get_riemann_rectangles(
            graph, 
            x_min = 0,
            x_max = 8,
            dx = self.small_dx,
            start_color = BLUE_D,
            end_color = BLUE_D,
            fill_opacity = 0.75,
            stroke_width = 0,
        )

        self .play(
            ShowCreation(graph),
            FadeIn(
                area, 
                run_time = 2,
                lag_ratio = 0.5,
            )
        )

        self.graph = graph
        self.area = area

    def write_negative_area(self):
        words = TextMobject("Negative area")
        words.set_color(RED)
        words.next_to(
            self.coords_to_point(7, -2),
            RIGHT,
        )
        arrow = Arrow(words, self.coords_to_point(
            self.sample_input, -1,
        ))

        self.play(
            Write(words, run_time = 2),
            ShowCreation(arrow)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [self.area, arrow])))

        self.negative_area_words = words

    def show_negative_point(self):
        v_line = self.get_vertical_line_to_graph(
            self.sample_input, self.graph,
            color = RED
        )
        self.play(ShowCreation(v_line))
        self.wait()
        self.v_line = v_line

    def show_car_going_backwards(self):
        car = Car()
        start_point = 3*RIGHT + 2*UP
        end_point = start_point + LEFT
        nudged_end_point = end_point + MED_SMALL_BUFF*LEFT
        car.move_to(start_point)
        arrow = Arrow(RIGHT, LEFT, color = RED)
        arrow.next_to(car, UP+LEFT)
        arrow.shift(MED_LARGE_BUFF*RIGHT)

        self.play(FadeIn(car))
        self.play(ShowCreation(arrow))
        self.play(MoveCar(
            car, end_point, 
            moving_forward = False,
            run_time = 3
        ))
        self.wait()
        ghost_car = car.copy().fade()
        right_nose_line = self.get_car_nose_line(car)
        self.play(ShowCreation(right_nose_line))
        self.add(ghost_car)
        self.play(MoveCar(
            car, nudged_end_point,
            moving_forward = False
        ))
        left_nose_line = self.get_car_nose_line(car)
        self.play(ShowCreation(left_nose_line))

        self.nose_lines = VGroup(left_nose_line, right_nose_line)
        self.car = car
        self.ghost_car = ghost_car

    def write_v_dt(self):
        brace = Brace(self.nose_lines, DOWN, buff = 0)
        equation = TexMobject("ds", "=", "v(t)", "dt")
        equation.next_to(brace, DOWN, SMALL_BUFF, LEFT)
        equation.set_color_by_tex("ds", DISTANCE_COLOR)
        equation.set_color_by_tex("dt", TIME_COLOR)

        negative = TextMobject("Negative")
        negative.set_color(RED)
        negative.next_to(equation.get_corner(UP+RIGHT), UP, LARGE_BUFF)
        ds_arrow, v_arrow = arrows = VGroup(*[
            Arrow(
                negative.get_bottom(),
                equation.get_part_by_tex(tex).get_top(),
                color = RED,
            )
            for tex in ("ds", "v(t)")
        ])

        self.play(
            GrowFromCenter(brace),
            Write(equation)
        )
        self.wait()
        self.play(FadeIn(negative))
        self.play(ShowCreation(v_arrow))
        self.wait(2)
        self.play(ReplacementTransform(
            v_arrow.copy(),
            ds_arrow
        ))
        self.wait(2)

        self.ds_equation = equation
        self.negative_word = negative
        self.negative_word_arrows = arrows

    def show_rectangle(self):
        rect_list = self.get_riemann_rectangles_list(
            self.graph, x_min = 0, x_max = 8,
            n_iterations = 6,
            start_color = BLUE_D,
            end_color = BLUE_D,
            fill_opacity = 0.75,
        )
        rects = rect_list[0]
        rect = rects[len(rects)*self.sample_input//8]

        dt_brace = Brace(rect, UP, buff = 0)
        v_brace = Brace(rect, LEFT, buff = 0)
        dt_label = dt_brace.get_text("$dt$", buff = SMALL_BUFF)
        dt_label.set_color(YELLOW)
        v_label = v_brace.get_text("$v(t)$", buff = SMALL_BUFF)
        v_label.add_background_rectangle()

        self.play(FadeOut(self.v_line), FadeIn(rect))
        self.play(
            GrowFromCenter(dt_brace), 
            GrowFromCenter(v_brace), 
            Write(dt_label),
            Write(v_label),
        )
        self.wait(2)
        self.play(*it.chain(
            [FadeIn(r) for r in rects if r is not rect],
            list(map(FadeOut, [
                dt_brace, v_brace, dt_label, v_label
            ]))
        ))
        self.wait()
        for new_rects in rect_list[1:]:
            self.transform_between_riemann_rects(rects, new_rects)
        self.wait()

    def write_signed_area(self):
        words = TextMobject("``Signed area''")
        words.next_to(self.coords_to_point(self.sample_input, 0), UP)
        symbols = VGroup(*[
            TexMobject(sym).move_to(self.coords_to_point(*coords))
            for sym, coords in [
                ("+", (1, 2)),
                ("-", (5, -1)),
                ("+", (7.6, 0.5)),
            ]
        ])
        self.play(Write(words))
        self.play(Write(symbols))
        self.wait()

    ####

    def get_car_nose_line(self, car):
        line = DashedLine(car.get_top(), car.get_bottom())
        line.move_to(car.get_right())
        return line

class NextVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        next_video = series[8]
        integral = TexMobject("\\int")
        integral.next_to(next_video, DOWN, LARGE_BUFF)

        self.play(FadeIn(series, lag_ratio = 0.5))
        self.play(
            next_video.set_color, YELLOW,
            next_video.shift, next_video.get_height()*DOWN/2,
            self.teacher.change_mode, "raise_right_hand"
        )
        self.play(Write(integral))
        self.wait(5)

class Chapter8PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "CrypticSwarm",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Karan Bhargava",
            "Ankit Agarwal",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Juan Benet",
            "Othman Alikhan",
            "Markus Persson",
            "Dan Buchoff",
            "Derek Dai",
            "Joseph John Cox",
            "Luc Ritchie",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Nils Schneider",
            "James Thornton",
            "Mustafa Mahdi",
            "Jonathan Eppele",
            "Mathew Bramson",
            "Jerry Ling",
            "Mark Govea",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }

class Thumbnail(Chapter1Thumbnail):
    CONFIG = {
        "x_axis_label" : "",
        "y_axis_label" : "",
        "graph_origin" : 1.5*DOWN + 4*LEFT,
        "y_axis_height" : 5,
        "x_max" : 5,
        "x_axis_width" : 11,
    }
    def construct(self):
        self.setup_axes()
        self.remove(*self.x_axis.numbers)
        self.remove(*self.y_axis.numbers)
        graph = self.get_graph(self.func)
        rects = self.get_riemann_rectangles(
            graph,
            x_min = 0,
            x_max = 4,
            dx = 0.25,
        )
        words = TextMobject("Integrals")
        words.set_width(8)
        words.to_edge(UP)

        self.add(graph, rects, words)












