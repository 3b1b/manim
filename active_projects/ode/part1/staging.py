from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.shared_constructs import *
from active_projects.ode.part1.pendulum import Pendulum
from active_projects.ode.part1.pendulum import ThetaVsTAxes


# Scenes


class VectorFieldTest(Scene):
    def construct(self):
        plane = NumberPlane(
            # axis_config={"unit_size": 2}
        )
        mu_tracker = ValueTracker(1)
        field = VectorField(
            lambda p: pendulum_vector_field(
                plane.point_to_coords(p),
                mu=mu_tracker.get_value()
            ),
            delta_x=0.5,
            delta_y=0.5,
            max_magnitude=4,
            opacity=0.5,
            # length_func=lambda norm: norm,
        )
        stream_lines = StreamLines(
            field.func,
            delta_x=0.5,
            delta_y=0.5,
        )
        animated_stream_lines = AnimatedStreamLines(
            stream_lines,
            line_anim_class=ShowPassingFlashWithThinningStrokeWidth,
        )

        self.add(plane, field, animated_stream_lines)
        self.wait(10)


class FollowThisThread(Scene):
    CONFIG = {
        "screen_rect_style": {
            "stroke_width": 2,
            "stroke_color": WHITE,
            "fill_opacity": 1,
            "fill_color": DARKER_GREY,
        }
    }

    def construct(self):
        self.show_thumbnails()
        self.show_words()

    def show_thumbnails(self):
        # TODO, replace each of these with a picture?
        thumbnails = self.thumbnails = VGroup(
            ScreenRectangle(**self.screen_rect_style),
            ScreenRectangle(**self.screen_rect_style),
            ScreenRectangle(**self.screen_rect_style),
            ScreenRectangle(**self.screen_rect_style),
            ScreenRectangle(**self.screen_rect_style),
        )
        n = len(thumbnails)
        thumbnails.set_height(1.5)

        line = self.line = CubicBezier([
            [-5, 3, 0],
            [3, 3, 0],
            [-3, -3, 0],
            [5, -3, 0],
        ])
        for thumbnail, a in zip(thumbnails, np.linspace(0, 1, n)):
            thumbnail.move_to(line.point_from_proportion(a))

        self.play(
            ShowCreation(
                line,
                rate_func=lambda t: np.clip(t * (n + 1) / n, 0, 1)
            ),
            LaggedStart(*[
                GrowFromCenter(
                    thumbnail,
                    rate_func=squish_rate_func(
                        smooth,
                        0, 0.7,
                    )
                )
                for thumbnail in thumbnails
            ], lag_ratio=1),
            run_time=5
        )

    def show_words(self):
        words = VGroup(
            TextMobject("Generalize"),
            TextMobject("Put in context"),
            TextMobject("Modify"),
        )
        # words.arrange(DOWN, aligned_edge=LEFT, buff=LARGE_BUFF)
        words.scale(1.5)
        words.to_corner(UR)
        words.add_to_back(VectorizedPoint(words.get_center()))
        words.add(VectorizedPoint(words.get_center()))

        diffEq = TextMobject("Differential\\\\equations")
        diffEq.scale(1.5)
        diffEq.to_corner(DL, buff=LARGE_BUFF)

        for word1, word2 in zip(words, words[1:]):
            self.play(
                FadeInFromDown(word2),
                FadeOutAndShift(word1, UP),
            )
            self.wait()
        self.play(
            ReplacementTransform(
                VGroup(self.thumbnails).copy().fade(1),
                diffEq,
                lag_ratio=0.01,
            )
        )
        self.wait()


class ShowGravityAcceleration(Scene):
    def construct(self):
        self.add_gravity_field()
        self.add_title()
        self.pulse_gravity_down()
        self.show_trajectory()
        self.combine_v_vects()

    def add_gravity_field(self):
        gravity_field = self.gravity_field = VectorField(
            lambda p: DOWN,
            # delta_x=2,
            # delta_y=2,
        )
        gravity_field.set_opacity(0.5)
        gravity_field.sort_submobjects(
            lambda p: -p[1],
        )
        self.add(gravity_field)

    def add_title(self):
        title = self.title = TextMobject("Gravitational acceleration")
        title.scale(1.5)
        title.to_edge(UP)
        g_eq = self.g_eq = TexMobject(
            "{g}", "=", "-9.8", "\\frac{\\text{m/s}}{\\text{s}}",
            **Lg_formula_config
        )
        g_eq.next_to(title, DOWN)
        for mob in title, g_eq:
            mob.add_background_rectangle_to_submobjects(
                buff=0.05,
                opacity=1,
            )
        self.add(title, g_eq)

    def pulse_gravity_down(self):
        field = self.gravity_field
        self.play(LaggedStart(*[
            ApplyFunction(
                lambda v: v.set_opacity(1).scale(1.2),
                vector,
                rate_func=there_and_back,
            )
            for vector in field
        ]), run_time=2, lag_ratio=0.001)
        self.add(self.title, self.g_eq)

    def show_trajectory(self):
        ball = Circle(
            stroke_width=1,
            stroke_color=WHITE,
            fill_color=GREY,
            fill_opacity=1,
            sheen_factor=1,
            sheen_direction=UL,
            radius=0.25,
        )
        randy = Randolph(mode="pondering")
        randy.eyes.set_stroke(BLACK, 0.5)
        randy.match_height(ball)
        randy.scale(0.75)
        randy.move_to(ball)
        ball.add(randy)

        total_time = 6

        p0 = 3 * DOWN + 5 * LEFT
        v0 = 2.8 * UP + 1.5 * RIGHT
        g = 0.9 * DOWN
        graph = ParametricFunction(
            lambda t: p0 + v0 * t + 0.5 * g * t**2,
            t_min=0,
            t_max=total_time,
        )
        # graph.center().to_edge(DOWN)
        dashed_graph = DashedVMobject(graph, num_dashes=60)
        dashed_graph.set_stroke(WHITE, 1)

        ball.move_to(graph.get_start())
        randy.add_updater(
            lambda m, dt: m.rotate(dt).move_to(ball)
        )
        times = np.arange(0, total_time + 1)

        velocity_graph = ParametricFunction(
            lambda t: v0 + g * t,
            t_min=0, t_max=total_time,
        )
        v_point = VectorizedPoint()
        v_point.move_to(velocity_graph.get_start())

        def get_v_vect():
            result = Vector(
                v_point.get_location(),
                color=RED,
                tip_length=0.2,
            )
            result.scale(0.5, about_point=result.get_start())
            result.shift(ball.get_center())
            result.set_stroke(width=2, family=False)
            return result
        v_vect = always_redraw(get_v_vect)
        self.add(v_vect)

        flash_rect = FullScreenRectangle(
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=0.2,
        )
        flash = FadeOut(
            flash_rect,
            rate_func=squish_rate_func(smooth, 0, 0.1)
        )

        ball_copies = VGroup()
        v_vect_copies = VGroup()
        self.add(dashed_graph, ball)
        for t1, t2 in zip(times, times[1:]):
            v_vect_copy = v_vect.copy()
            v_vect_copies.add(v_vect_copy)
            self.add(v_vect_copy)
            ball_copy = ball.copy()
            ball_copy.clear_updaters()
            ball_copies.add(ball_copy)
            self.add(ball_copy)

            dashed_graph.save_state()
            kw = {
                "rate_func": lambda alpha: interpolate(
                    t1 / total_time,
                    t2 / total_time,
                    alpha
                )
            }
            self.play(
                ShowCreation(dashed_graph, **kw),
                MoveAlongPath(ball, graph, **kw),
                MoveAlongPath(v_point, velocity_graph, **kw),
                flash,
                run_time=1,
            )
            dashed_graph.restore()
        randy.clear_updaters()
        self.wait()

        self.v_vects = v_vect_copies

    def combine_v_vects(self):
        v_vects = self.v_vects.copy()
        v_vects.generate_target()
        new_center = 2 * DOWN + 2 * LEFT
        for vect in v_vects.target:
            vect.scale(1.5)
            vect.set_stroke(width=2)
            vect.shift(new_center - vect.get_start())

        self.play(MoveToTarget(v_vects))

        delta_vects = VGroup(*[
            Arrow(
                v1.get_end(),
                v2.get_end(),
                buff=0.01,
                color=YELLOW,
            ).set_opacity(0.5)
            for v1, v2 in zip(v_vects, v_vects[1:])
        ])
        brace = Brace(Line(ORIGIN, UP), RIGHT)
        braces = VGroup(*[
            brace.copy().match_height(arrow).next_to(
                arrow, RIGHT, buff=0.2 * SMALL_BUFF
            )
            for arrow in delta_vects
        ])
        amounts = VGroup(*[
            TextMobject("9.8 m/s").scale(0.5).next_to(
                brace, RIGHT, SMALL_BUFF
            )
            for brace in braces
        ])

        self.play(
            FadeOut(self.gravity_field),
            FadeIn(delta_vects, lag_ratio=0.1),
        )
        self.play(
            LaggedStartMap(GrowFromCenter, braces),
            LaggedStartMap(FadeInFrom, amounts, lambda m: (m, LEFT)),
        )
        self.wait()


class ShowDerivativeVideo(Scene):
    CONFIG = {
        "camera_config": {"background_color": DARKER_GREY}
    }

    def construct(self):
        title = TextMobject("Essence of Calculus")
        title.scale(1.25)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect = rect.copy()
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.next_to(title, DOWN)
        animated_rect = AnimatedBoundary(rect)

        self.add(title, rect)
        self.add(animated_rect)
        self.wait(10)


class SubtleAirCurrents(Scene):
    def construct(self):
        pass


class DefineODE(Scene):
    CONFIG = {
        "pendulum_config": {
            "length": 2,
            "top_point": 5 * RIGHT + 2 * UP,
            "initial_theta": 150 * DEGREES,
            "mu": 0.3,
        },
        "axes_config": {
            "y_axis_config": {"unit_size": 0.75},
            "y_max": PI,
            "y_min": -PI,
            "x_max": 10,
            "x_axis_config": {
                "numbers_to_show": range(2, 10, 2),
                "unit_size": 1,
            }
        },
    }

    def construct(self):
        self.add_graph()
        self.write_differential_equation()
        self.dont_know_the_value()
        self.show_value_slope_curvature()
        self.write_ode()
        self.show_second_order()
        self.show_higher_order_examples()
        self.show_changing_curvature_group()

    def add_graph(self):
        pendulum = Pendulum(**self.pendulum_config)
        axes = ThetaVsTAxes(**self.axes_config)

        axes.center()
        axes.to_corner(DL)
        graph = axes.get_live_drawn_graph(pendulum)

        pendulum.start_swinging()
        self.add(axes, pendulum, graph)

        self.pendulum = pendulum
        self.axes = axes
        self.graph = graph

    def write_differential_equation(self):
        de_word = TextMobject("Differential", "Equation")
        de_word.to_edge(UP)

        equation = TexMobject(
            "\\ddot \\theta({t})", "=",
            "-\\mu \\dot \\theta({t})",
            "-{g \\over L} \\sin\\big(\\theta({t})\\big)",
            tex_to_color_map={
                "\\theta": BLUE,
                "{t}": WHITE
            }
        )
        equation.next_to(de_word, DOWN)
        thetas = equation.get_parts_by_tex("\\theta")

        lines = VGroup(*[
            Line(v, 1.2 * v)
            for v in compass_directions(25)
        ])
        lines.replace(equation, stretch=True)
        lines.scale(1.5)
        lines.set_stroke(YELLOW)
        lines.shuffle()

        self.add(equation)
        self.wait(5)
        self.play(
            ShowPassingFlashWithThinningStrokeWidth(
                lines,
                lag_ratio=0.002,
                run_time=1.5,
                time_width=0.9,
                n_segments=5,
            )
        )
        self.play(FadeInFromDown(de_word))
        self.wait(2)
        self.play(
            LaggedStartMap(
                ApplyMethod, thetas,
                lambda m: (m.shift, 0.25 * DOWN),
                rate_func=there_and_back,
            )
        )
        self.wait()

        self.de_word = de_word
        self.equation = equation

    def dont_know_the_value(self):
        graph = self.graph
        pendulum = self.pendulum

        q_marks = VGroup(*[
            TexMobject("?").move_to(graph.point_from_proportion(a))
            for a in np.linspace(0, 1, 20)
        ])
        q_marks.set_stroke(width=0, background=True)
        self.play(
            VFadeOut(graph),
            FadeOut(pendulum),
            LaggedStart(*[
                UpdateFromAlphaFunc(
                    q_mark,
                    lambda m, a: m.set_height(0.5 * (1 + a)).set_fill(
                        opacity=there_and_back(a)
                    ),
                )
                for q_mark in q_marks
            ], lag_ratio=0.01, run_time=2)
        )
        self.remove(q_marks)

    def show_value_slope_curvature(self):
        axes = self.axes
        p = self.pendulum
        graph = axes.get_graph(
            lambda t: p.initial_theta * np.cos(
                np.sqrt(p.gravity / p.length) * t
            ) * np.exp(-p.mu * t / 2)
        )

        tex_config = {
            "tex_to_color_map": {"\\theta": BLUE},
            "height": 0.5,
        }
        theta, d_theta, dd_theta = [
            TexMobject(s + "\\theta(t)", **tex_config)
            for s in ("", "\\dot", "\\ddot")
        ]

        t_tracker = ValueTracker(2.5)
        get_t = t_tracker.get_value

        def get_point(t):
            return graph.point_from_proportion(t / axes.x_max)

        def get_dot():
            return Dot(get_point(get_t())).scale(0.5)

        def get_v_line():
            point = get_point(get_t())
            x_point = axes.x_axis.number_to_point(
                axes.x_axis.point_to_number(point)
            )
            return DashedLine(
                x_point, point,
                dash_length=0.025,
                stroke_color=WHITE,
                stroke_width=2,
            )

        def get_tangent_line(curve, alpha):
            line = Line(
                ORIGIN, 1.5 * RIGHT,
                color=YELLOW,
                stroke_width=1.5,
            )
            da = 0.0001
            p0 = curve.point_from_proportion(alpha)
            p1 = curve.point_from_proportion(alpha - da)
            p2 = curve.point_from_proportion(alpha + da)
            angle = angle_of_vector(p2 - p1)
            line.rotate(angle)
            line.move_to(p0)
            return line

        def get_slope_line():
            return get_tangent_line(
                graph, get_t() / axes.x_max
            )

        def get_curve():
            curve = VMobject()
            t = get_t()
            curve.set_points_smoothly([
                get_point(t + a)
                for a in np.linspace(-0.5, 0.5, 11)
            ])
            curve.set_stroke(RED, 1)
            return curve

        v_line = always_redraw(get_v_line)
        dot = always_redraw(get_dot)
        slope_line = always_redraw(get_slope_line)
        curve = always_redraw(get_curve)

        theta.next_to(v_line, RIGHT, SMALL_BUFF)
        d_theta.next_to(slope_line.get_end(), UP, SMALL_BUFF)
        dd_theta.next_to(curve.get_end(), RIGHT, SMALL_BUFF)
        thetas = VGroup(theta, d_theta, dd_theta)

        words = VGroup(
            TextMobject("= Height"),
            TextMobject("= Slope").set_color(YELLOW),
            TextMobject("= ``Curvature''").set_color(RED),
        )
        words.scale(0.75)
        for word, sym in zip(words, thetas):
            word.next_to(sym, RIGHT, buff=2 * SMALL_BUFF)
            sym.word = word

        self.play(
            ShowCreation(v_line),
            FadeInFromPoint(dot, v_line.get_start()),
            FadeInFrom(theta, DOWN),
            FadeInFrom(theta.word, DOWN),
        )
        self.add(slope_line, dot)
        self.play(
            ShowCreation(slope_line),
            FadeInFrom(d_theta, LEFT),
            FadeInFrom(d_theta.word, LEFT),
        )

        a_tracker = ValueTracker(0)
        curve_copy = curve.copy()
        changing_slope = always_redraw(
            lambda: get_tangent_line(
                curve_copy,
                a_tracker.get_value(),
            ).set_stroke(
                opacity=there_and_back(a_tracker.get_value())
            )
        )
        self.add(curve, dot)
        self.play(
            ShowCreation(curve),
            FadeInFrom(dd_theta, LEFT),
            FadeInFrom(dd_theta.word, LEFT),
        )
        self.add(changing_slope)
        self.play(
            a_tracker.set_value, 1,
            run_time=3,
        )
        self.remove(changing_slope, a_tracker)

        self.t_tracker = t_tracker
        self.curvature_group = VGroup(
            v_line, slope_line, curve, dot
        )
        self.curvature_group_labels = VGroup(thetas, words)
        self.fake_graph = graph

    def write_ode(self):
        equation = self.equation
        axes = self.axes
        de_word = self.de_word

        ts = equation.get_parts_by_tex("{t}")
        t_rects = VGroup(*map(SurroundingRectangle, ts))  # Rawr
        x_axis = axes.x_axis
        x_axis_line = Line(
            x_axis.get_start(), x_axis.get_end(),
            stroke_color=YELLOW,
            stroke_width=5,
        )

        ordinary = TextMobject("Ordinary")
        de_word.generate_target()
        group = VGroup(ordinary, de_word.target)
        group.arrange(RIGHT)
        group.to_edge(UP)
        ordinary_underline = Line(LEFT, RIGHT)
        ordinary_underline.replace(ordinary, dim_to_match=0)
        ordinary_underline.next_to(ordinary, DOWN, SMALL_BUFF)
        ordinary_underline.set_color(YELLOW)

        self.play(
            ShowCreationThenFadeOut(
                t_rects,
                lag_ratio=0.8
            ),
            ShowCreationThenFadeOut(x_axis_line)
        )
        self.play(
            MoveToTarget(de_word),
            FadeInFrom(ordinary, RIGHT),
            GrowFromCenter(ordinary_underline)
        )
        self.play(FadeOut(ordinary_underline))
        self.wait()

        self.remove(ordinary, de_word)
        ode_word = self.ode_word = VGroup(*ordinary, *de_word)
        ode_initials = VGroup(*[word[0] for word in ode_word])
        ode_initials.generate_target()
        ode_initials.target.scale(1.2)
        ode_initials.target.set_color(PINK)
        ode_initials.target.arrange(
            RIGHT, buff=0.5 * SMALL_BUFF, aligned_edge=DOWN
        )
        ode_initials.target.to_edge(UP, buff=MED_SMALL_BUFF)

        ode_remaining_letters = VGroup(*it.chain(*[
            word[1:] for word in ode_word
        ]))
        ode_remaining_letters.generate_target()
        for mob in ode_remaining_letters.target:
            mob.shift(0.2 * UP)
            mob.fade(1)

        self.play(
            MoveToTarget(ode_initials),
            MoveToTarget(ode_remaining_letters, lag_ratio=0.05),
        )
        self.wait()

        self.ode_initials = ode_initials

    def show_second_order(self):
        so = TextMobject("Second order")
        so.scale(1.4)
        ode = self.ode_initials
        ode.generate_target()
        group = VGroup(so, ode.target)
        group.arrange(RIGHT, aligned_edge=DOWN)
        group.to_edge(UP, buff=MED_SMALL_BUFF)

        second_deriv = self.equation[:5]

        self.play(
            Write(so),
            MoveToTarget(ode),
        )
        self.wait()
        self.play(FocusOn(second_deriv))
        self.play(
            Indicate(second_deriv, color=RED),
        )
        self.wait()

        self.second_order_word = so

    def show_higher_order_examples(self):
        main_example = VGroup(
            self.second_order_word,
            self.ode_initials,
            self.equation
        )
        tex_config = {"tex_to_color_map": {"{x}": BLUE}}
        example3 = VGroup(
            TextMobject("Third order ODE"),
            TexMobject(
                "\\dddot {x}(t) + \\dot {x}(t)^2 = 0",
                **tex_config,
            )
        )
        example4 = VGroup(
            TextMobject("Fourth order ODE"),
            TexMobject(
                "\\ddddot {x}(t) +",
                "a\\dddot {x}(t) \\dot {x}(t) + ",
                "b \\ddot {x}(t) {x}(t)",
                "= 1",
                **tex_config,
            )
        )
        for example in [example3, example4]:
            example[0].scale(1.2)
            example.arrange(DOWN, buff=MED_LARGE_BUFF)
            example.to_edge(UP, buff=MED_SMALL_BUFF)

        self.play(
            FadeOut(main_example),
            FadeIn(example3),
        )
        self.wait(2)
        self.play(
            FadeOut(example3),
            FadeIn(example4),
        )
        self.wait(2)
        self.play(
            FadeOut(example4),
            FadeIn(main_example),
        )
        self.wait(2)

    def show_changing_curvature_group(self):
        t_tracker = self.t_tracker
        curvature_group = self.curvature_group
        labels = self.curvature_group_labels
        graph = VMobject()
        graph.pointwise_become_partial(
            self.fake_graph,
            0.25, 1,
        )
        dashed_graph = DashedVMobject(graph, num_dashes=100)
        dashed_graph.set_stroke(GREEN, 1)

        self.play(FadeOut(labels))
        self.add(dashed_graph, curvature_group)
        self.play(
            t_tracker.set_value, 10,
            ShowCreation(dashed_graph),
            run_time=15,
            rate_func=linear,
        )
        self.wait()


class ODEvsPDEinFrames(Scene):
    def construct(self):
        pass


class ReferencePiCollisionStateSpaces(Scene):
    def construct(self):
        pass


class BreakingSecondOrderIntoTwoFirstOrder(Scene):
    def construct(self):
        pass


class NewSceneName(Scene):
    def construct(self):
        pass
