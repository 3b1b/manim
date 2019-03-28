from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.shared_constructs import *
from active_projects.ode.part1.pendulum import Pendulum
from active_projects.ode.part1.pendulum import ThetaVsTAxes
from active_projects.ode.part1.phase_space import IntroduceVectorField
from old_projects.div_curl import PhaseSpaceOfPopulationModel
from old_projects.div_curl import ShowTwoPopulations


# Scenes


class VectorFieldTest(Scene):
    def construct(self):
        plane = NumberPlane(
            # axis_config={"unit_size": 2}
        )
        mu_tracker = ValueTracker(1)
        field = VectorField(
            lambda p: pendulum_vector_field_func(
                plane.point_to_coords(p),
                mu=mu_tracker.get_value()
            ),
            delta_x=0.5,
            delta_y=0.5,
            max_magnitude=6,
            opacity=0.5,
            # length_func=lambda norm: norm,
        )
        field.set_opacity(1)

        self.add(plane, field)
        return

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


class ShowRect(Scene):
    def construct(self):
        rect = Rectangle()
        rect.set_stroke(YELLOW)
        rect.set_height(1)
        rect.set_width(3, stretch=True)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))


class PeriodFormula(Scene):
    def construct(self):
        formula = get_period_formula()
        formula.scale(2)
        q_mark = TexMobject("?")
        q_mark.scale(3)
        q_mark.next_to(formula, RIGHT)
        self.add(formula, q_mark)


class TourOfDifferentialEquations(MovingCameraScene):
    CONFIG = {
        "screen_rect_style": {
            "stroke_width": 2,
            "stroke_color": WHITE,
            "fill_opacity": 1,
            "fill_color": BLACK,
        },
        "camera_config": {"background_color": DARKER_GREY},
    }

    def construct(self):
        self.add_title()
        self.show_thumbnails()
        # self.show_words()

    def add_title(self):
        title = TextMobject(
            "A Tourist's Guide \\\\to Differential\\\\Equations"
        )
        title.scale(1.5)
        title.to_corner(UR)
        self.add(title)

    def show_thumbnails(self):
        thumbnails = self.thumbnails = Group(
            Group(ScreenRectangle(**self.screen_rect_style)),
            Group(ScreenRectangle(**self.screen_rect_style)),
            Group(ScreenRectangle(**self.screen_rect_style)),
            Group(ScreenRectangle(**self.screen_rect_style)),
            Group(ScreenRectangle(**self.screen_rect_style)),
        )
        n = len(thumbnails)
        thumbnails.set_height(1.5)

        line = self.line = CubicBezier([
            [-5, 3, 0],
            [3, 3, 0],
            [-3, -3, 0],
            [5, -3, 0],
        ])
        line.shift(MED_SMALL_BUFF * LEFT)
        for thumbnail, a in zip(thumbnails, np.linspace(0, 1, n)):
            thumbnail.move_to(line.point_from_proportion(a))
        dots = TexMobject("\\dots")
        dots.next_to(thumbnails[-1], RIGHT)

        self.add_heat_preview(thumbnails[1])
        self.add_fourier_series(thumbnails[2])
        self.add_matrix_exponent(thumbnails[3])
        self.add_laplace_symbol(thumbnails[4])

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
        self.play(Write(dots))
        self.wait()
        self.play(
            self.camera_frame.replace,
            thumbnails[0],
            run_time=3,
        )
        self.wait()

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

    #
    def add_heat_preview(self, thumbnail):
        image = ImageMobject("HeatSurfaceExample")
        image.replace(thumbnail)
        thumbnail.add(image)

    def add_matrix_exponent(self, thumbnail):
        matrix = IntegerMatrix(
            [[3, 1], [4, 1]],
            v_buff=MED_LARGE_BUFF,
            h_buff=MED_LARGE_BUFF,
            bracket_h_buff=SMALL_BUFF,
            bracket_v_buff=SMALL_BUFF,
        )
        e = TexMobject("e")
        t = TexMobject("t")
        t.scale(1.5)
        t.next_to(matrix, RIGHT, SMALL_BUFF)
        e.scale(2)
        e.move_to(matrix.get_corner(DL), UR)
        group = VGroup(e, matrix, t)
        group.set_height(0.7 * thumbnail.get_height())
        randy = Randolph(mode="confused", height=0.75)
        randy.next_to(group, LEFT, aligned_edge=DOWN)
        randy.look_at(matrix)
        group.add(randy)
        group.move_to(thumbnail)
        thumbnail.add(group)

    def add_fourier_series(self, thumbnail):
        colors = [BLUE, GREEN, YELLOW, RED, RED_E, PINK]

        waves = VGroup(*[
            self.get_square_wave_approx(N, color)
            for N, color in enumerate(colors)
        ])
        waves.set_stroke(width=1.5)
        waves.replace(thumbnail, stretch=True)
        waves.scale(0.8)
        waves.move_to(thumbnail)
        thumbnail.add(waves)

    def get_square_wave_approx(self, N, color):
        return FunctionGraph(
            lambda x: sum([
                (1 / n) * np.sin(n * PI * x)
                for n in range(1, 2 * N + 3, 2)
            ]),
            x_min=0,
            x_max=2,
            color=color
        )

    def add_laplace_symbol(self, thumbnail):
        mob = TexMobject(
            "\\mathcal{L}\\left\\{f(t)\\right\\}"
        )
        mob.set_width(0.8 * thumbnail.get_width())
        mob.move_to(thumbnail)
        thumbnail.add(mob)


class HeatEquationPreview(ExternallyAnimatedScene):
    pass


class ShowHorizontalDashedLine(Scene):
    def construct(self):
        line = DashedLine(LEFT_SIDE, RIGHT_SIDE)
        self.play(ShowCreation(line))
        self.wait()


class RabbitFoxPopulations(ShowTwoPopulations):
    pass


class RabbitFoxEquation(PhaseSpaceOfPopulationModel):
    def construct(self):
        equations = self.get_equations()
        self.add(equations)


class ShowGravityAcceleration(Scene):
    def construct(self):
        self.add_gravity_field()
        self.add_title()
        self.pulse_gravity_down()
        self.show_g_value()
        self.show_trajectory()
        self.combine_v_vects()
        self.show_g_symbol()

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
        title.add_background_rectangle(
            buff=0.05,
            opacity=1,
        )
        self.play(FadeInFromDown(title))

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
        self.add(self.title)

    def show_g_value(self):
        title = self.title
        g_eq = self.g_eq = TexMobject(
            "-9.8", "{\\text{m/s}", "\\over", "\\text{s}}",
            **Lg_formula_config
        )
        g_eq.add_background_rectangle_to_submobjects()
        g_eq.scale(2)
        g_eq.center()
        num, ms, per, s = g_eq

        self.add(num)
        self.wait(0.75)
        self.play(
            FadeInFrom(ms, 0.25 * DOWN, run_time=0.5)
        )
        self.wait(0.25)
        self.play(LaggedStart(
            GrowFromPoint(per, per.get_left()),
            FadeInFrom(s, 0.5 * UP),
            lag_ratio=0.7,
            run_time=0.75
        ))
        self.wait()
        self.play(
            g_eq.scale, 0.5,
            g_eq.next_to, title, DOWN,
        )

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

        time_label = TextMobject("Time = ")
        time_label.shift(MED_SMALL_BUFF * LEFT)
        time_tracker = ValueTracker(0)
        time = DecimalNumber(0)
        time.next_to(time_label, RIGHT)
        time.add_updater(lambda d, dt: d.set_value(
            time_tracker.get_value()
        ))
        time_group = VGroup(time_label, time)
        time_group.center().to_edge(DOWN)
        self.add(time_group)

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
                ApplyMethod(
                    time_tracker.increment_value, 1,
                    rate_func=linear
                ),
                flash,
                run_time=1,
            )
            dashed_graph.restore()
        randy.clear_updaters()
        self.play(FadeOut(time_group))
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

    def show_g_symbol(self):
        g = TexMobject("g")
        brace = Brace(self.g_eq[0][2:], UP, buff=SMALL_BUFF)
        g.scale(1.5)
        g.next_to(brace, UP)
        g.set_color(YELLOW)
        self.play(
            FadeOut(self.title),
            GrowFromCenter(brace),
            FadeInFrom(g, UP),
        )
        self.wait()


class ShowDerivativeVideo(Scene):
    def construct(self):
        title = TextMobject("Essence of", "Calculus")
        title.scale(1.5)
        title.to_edge(UP)

        title2 = TextMobject("Essence of", "Linear Algebra")
        title2.scale(1.5)
        title2.move_to(title, DOWN)

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
        self.wait(5)
        self.play(ReplacementTransform(title, title2))
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
        de_word.to_edge(UP, buff=MED_SMALL_BUFF)

        equation = get_ode()
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
            "tex_to_color_map": {
                "{\\theta}": BLUE,
                "{\\dot\\theta}": YELLOW,
                "{\\ddot\\theta}": RED,
            },
            "height": 0.5,
        }
        theta, d_theta, dd_theta = [
            TexMobject(
                "{" + s + "\\theta}(t)",
                **tex_config
            )
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
                stroke_color=BLUE,
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
            TextMobject("= Height").set_color(BLUE),
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
        main_example = self.get_main_example()
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

    def get_main_example(self):
        return VGroup(
            self.second_order_word,
            self.ode_initials,
            self.equation
        )

    def show_changing_curvature_group(self):
        t_tracker = self.t_tracker
        curvature_group = self.curvature_group
        labels = self.curvature_group_labels
        graph = VMobject()
        graph.pointwise_become_partial(
            self.fake_graph,
            t_tracker.get_value() / self.axes.x_max,
            1,
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


# Largely a copy of DefineODE, which is not great.
# But what can you do?
class SecondOrderEquationExample(DefineODE):
    def construct(self):
        self.add_graph()
        self.write_differential_equation()
        self.show_value_slope_curvature()
        self.show_higher_order_examples()
        self.show_changing_curvature_group()

    def add_graph(self):
        axes = self.axes = Axes(
            x_min=0,
            x_max=10.5,
            y_min=-2.5,
            y_max=2.5,
        )
        axes.center()
        axes.to_edge(DOWN)
        x_t = TexMobject("x", "(t)")
        x_t.set_color_by_tex("x", BLUE)
        t = TexMobject("t")
        t.next_to(axes.x_axis.get_right(), UP)
        x_t.next_to(axes.y_axis.get_top(), UP)

        axes.add(t, x_t)
        axes.add_coordinates()

        self.add(axes)

    def write_differential_equation(self):
        de_word = TextMobject("Differential", "Equation")
        de_word.scale(1.25)
        de_word.to_edge(UP, buff=MED_SMALL_BUFF)
        so_word = TextMobject("Second Order")
        so_word.scale(1.25)
        de_word.generate_target()
        group = VGroup(so_word, de_word.target)
        group.arrange(RIGHT)
        group.to_edge(UP, buff=MED_SMALL_BUFF)
        so_word.align_to(de_word.target[0], DOWN)
        so_line = Line(LEFT, RIGHT, color=YELLOW)
        so_line.match_width(so_word)
        so_line.next_to(so_word, DOWN, buff=SMALL_BUFF)

        equation = TexMobject(
            "{\\ddot x}(t)", "=",
            "-\\mu", "{\\dot x}(t)",
            "-", "\\omega", "{x}(t)",
            tex_to_color_map={
                "{x}": BLUE,
                "{\\dot x}": YELLOW,
                "{\\ddot x}": RED,
            }
        )
        equation.next_to(de_word, DOWN)

        dd_x_part = equation[:2]
        dd_x_rect = SurroundingRectangle(dd_x_part)

        self.add(de_word, equation)
        self.play(
            MoveToTarget(de_word),
            FadeInFrom(so_word, RIGHT),
            GrowFromCenter(so_line),
        )
        self.play(ReplacementTransform(so_line, dd_x_rect))
        self.play(FadeOut(dd_x_rect))

        self.equation = equation
        self.title = VGroup(*so_word, *de_word)

    def show_value_slope_curvature(self):
        axes = self.axes
        graph = axes.get_graph(
            lambda t: -2.5 * np.cos(2 * t) * np.exp(-0.2 * t)
        )

        tex_config = {
            "tex_to_color_map": {
                "{x}": BLUE,
                "{\\dot x}": YELLOW,
                "{\\ddot x}": RED,
            },
            "height": 0.5,
        }
        x, d_x, dd_x = [
            TexMobject(
                "{" + s + "x}(t)",
                **tex_config
            )
            for s in ("", "\\dot ", "\\ddot ")
        ]

        t_tracker = ValueTracker(1.25)
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
                stroke_color=BLUE,
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

        x.next_to(v_line, RIGHT, SMALL_BUFF)
        d_x.next_to(slope_line.get_end(), UP, SMALL_BUFF)
        dd_x.next_to(curve.get_end(), RIGHT, SMALL_BUFF)
        xs = VGroup(x, d_x, dd_x)

        words = VGroup(
            TextMobject("= Height").set_color(BLUE),
            TextMobject("= Slope").set_color(YELLOW),
            TextMobject("= ``Curvature''").set_color(RED),
        )
        words.scale(0.75)
        for word, sym in zip(words, xs):
            word.next_to(sym, RIGHT, buff=2 * SMALL_BUFF)
            sym.word = word

        self.play(
            ShowCreation(v_line),
            FadeInFromPoint(dot, v_line.get_start()),
            FadeInFrom(x, DOWN),
            FadeInFrom(x.word, DOWN),
        )
        self.add(slope_line, dot)
        self.play(
            ShowCreation(slope_line),
            FadeInFrom(d_x, LEFT),
            FadeInFrom(d_x.word, LEFT),
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
            FadeInFrom(dd_x, LEFT),
            FadeInFrom(dd_x.word, LEFT),
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
        self.curvature_group_labels = VGroup(xs, words)
        self.fake_graph = graph

    def get_main_example(self):
        return VGroup(
            self.equation,
            self.title,
        )

# class VisualizeHeightSlopeCurvature(DefineODE):
#     CONFIG = {
#         "pendulum_config": {
#             "length": 2,
#             "top_point": 5 * RIGHT + 2 * UP,
#             "initial_theta": 175 * DEGREES,
#             "mu": 0.3,
#         },
#     }

#     def construct(self):
#         self.add_graph()
#         self.show_value_slope_curvature()
#         self.show_changing_curvature_group()


class ODEvsPDEinFrames(Scene):
    CONFIG = {
        "camera_config": {"background_color": DARKER_GREY}
    }

    def construct(self):
        frames = VGroup(*[
            ScreenRectangle(
                height=3.5,
                fill_opacity=1,
                fill_color=BLACK,
                stroke_width=0,
            )
            for x in range(2)
        ])
        frames.arrange(RIGHT, buff=LARGE_BUFF)
        frames.shift(0.5 * DOWN)

        animated_frames = VGroup(*[
            AnimatedBoundary(
                frame,
                cycle_rate=0.2,
                max_stroke_width=1,
            )
            for frame in frames
        ])

        titles = VGroup(
            # TextMobject("ODEs"),
            # TextMobject("PDEs"),
            TextMobject("Ordinary", "Differential", "Equations"),
            TextMobject("Partial", "Differential", "Equations"),
        )
        for title, frame in zip(titles, frames):
            title.arrange(
                DOWN,
                buff=MED_SMALL_BUFF,
                aligned_edge=LEFT
            )
            title.next_to(frame, UP, MED_LARGE_BUFF)
            title.initials = VGroup(*[
                part[0] for part in title
            ])
        titles[0][1].shift(0.05 * UP)

        # ODE content
        ode = get_ode()
        ode.set_width(frames[0].get_width() - MED_LARGE_BUFF)
        ode.next_to(frames[0].get_top(), DOWN)
        ts = ode.get_parts_by_tex("{t}")
        one_input = TextMobject("One input")
        one_input.next_to(frames[0].get_bottom(), UP)
        o_arrows = VGroup(*[
            Arrow(
                one_input.get_top(),
                t.get_bottom(),
                buff=0.2,
                color=WHITE,
                max_tip_length_to_length_ratio=0.075,
                path_arc=pa
            )
            for t, pa in zip(ts, [-0.7, 0, 0.7])
        ])
        o_arrows.set_stroke(width=3)
        frames[0].add(ode, one_input, o_arrows)

        # PDE content
        pde = TexMobject(
            """
            \\frac{\\partial T}{\\partial t}
            {(x, y, t)} =
            \\frac{\\partial^2 T}{\\partial x^2}
            {(x, y, t)} +
            \\frac{\\partial^2 T}{\\partial y^2}
            {(x, y, t)}
            """,
            tex_to_color_map={"{(x, y, t)}": WHITE}
        )
        pde.set_width(frames[1].get_width() - MED_LARGE_BUFF)
        pde.next_to(frames[1].get_top(), DOWN)
        inputs = pde.get_parts_by_tex("{(x, y, t)}")
        multi_input = TextMobject("Multiple inputs")
        multi_input.next_to(frames[1].get_bottom(), UP)
        p_arrows = VGroup(*[
            Arrow(
                multi_input.get_top(),
                mob.get_bottom(),
                buff=0.2,
                color=WHITE,
                max_tip_length_to_length_ratio=0.075,
                path_arc=pa
            )
            for mob, pa in zip(inputs, [-0.7, 0, 0.7])
        ])
        p_arrows.set_stroke(width=3)
        frames[1].add(pde, multi_input, p_arrows)

        self.add(
            frames[0],
            animated_frames[0],
            titles[0]
        )
        self.play(
            Write(one_input),
            ShowCreation(o_arrows, lag_ratio=0.5)
        )
        self.wait(2)
        self.play(titles[0].initials.set_color, BLUE)
        self.wait(7)

        # Transition
        self.play(
            TransformFromCopy(*titles),
            TransformFromCopy(*frames),
        )
        self.play(VFadeIn(animated_frames[1]))
        self.wait()
        self.play(titles[1].initials.set_color, YELLOW)
        self.wait(30)


class ReferencePiCollisionStateSpaces(Scene):
    CONFIG = {
        "camera_config": {"background_color": DARKER_GREY}
    }

    def construct(self):
        title = TextMobject("The block collision puzzle")
        title.scale(1.5)
        title.to_edge(UP)
        self.add(title)

        frames = VGroup(*[
            ScreenRectangle(
                height=3.5,
                fill_opacity=1,
                fill_color=BLACK,
                stroke_width=0,
            )
            for x in range(2)
        ])
        frames.arrange(RIGHT, buff=LARGE_BUFF)
        boundary = AnimatedBoundary(frames)
        self.add(frames, boundary)
        self.wait(15)


class XComponentArrows(Scene):
    def construct(self):
        field = VectorField(
            lambda p: np.array([p[1], 0, 0])
        )
        field.set_opacity(0.75)
        for u in (1, -1):
            field.sort(lambda p: u * p[0])
            self.play(LaggedStartMap(
                GrowArrow, field,
                lag_ratio=0.1,
                run_time=1
            ))
            self.play(FadeOut(field))


class BreakingSecondOrderIntoTwoFirstOrder(IntroduceVectorField):
    def construct(self):
        ode = TexMobject(
            "{\\ddot\\theta}", "(t)", "=",
            "-\\mu", "{\\dot\\theta}", "(t)"
            "-(g / L)\\sin\\big(", "{\\theta}", "(t)\\big)",
            tex_to_color_map={
                "{\\ddot\\theta}": RED,
                "{\\dot\\theta}": YELLOW,
                "{\\theta}": BLUE,
                # "{t}": WHITE,
            }
        )
        so_word = TextMobject("Second order ODE")
        sys_word = TextMobject("System of two first order ODEs")

        system1 = self.get_system("{\\theta}", "{\\dot\\theta}")
        system2 = self.get_system("{\\theta}", "{\\omega}")

        so_word.to_edge(UP)
        ode.next_to(so_word, DOWN)
        sys_word.move_to(ORIGIN)
        system1.next_to(sys_word, DOWN)
        system2.move_to(system1)

        theta_dots = VGroup(*filter(
            lambda m: (
                isinstance(m, SingleStringTexMobject) and
                "{\\dot\\theta}" == m.get_tex_string()
            ),
            system1.get_family(),
        ))

        self.add(ode)
        self.play(FadeInFrom(so_word, 0.5 * DOWN))
        self.wait()

        self.play(
            TransformFromCopy(
                ode[3:], system1[3].get_entries()[1],
            ),
            TransformFromCopy(ode[2], system1[2]),
            TransformFromCopy(
                ode[:2], VGroup(
                    system1[0],
                    system1[1].get_entries()[1],
                )
            ),
        )
        self.play(
            FadeIn(system1[1].get_brackets()),
            FadeIn(system1[1].get_entries()[0]),
            FadeIn(system1[3].get_brackets()),
            FadeIn(system1[3].get_entries()[0]),
        )
        self.play(
            FadeInFromDown(sys_word)
        )
        self.wait()
        self.play(LaggedStartMap(
            ShowCreationThenFadeAround,
            theta_dots,
            surrounding_rectangle_config={
                "color": PINK,
            }
        ))

        self.play(ReplacementTransform(system1, system2))
        self.wait()

    def get_system(self, tex1, tex2):
        system = VGroup(
            TexMobject("d \\over dt"),
            self.get_vector_symbol(
                tex1 + "(t)",
                tex2 + "(t)",
            ),
            TexMobject("="),
            self.get_vector_symbol(
                tex2 + "(t)",
                "".join([
                    "-\\mu", tex2, "(t)",
                    "-(g / L) \\sin\\big(",
                    tex1, "(t)", "\\big)",
                ])
            )
        )
        system.arrange(RIGHT)
        return system


class FromODEToVectorField(Scene):
    def construct(self):
        matrix_config = {
            "bracket_v_buff": 2 * SMALL_BUFF,
            "element_to_mobject_config": {
                "tex_to_color_map": {
                    "x": GREEN,
                    "y": RED,
                    "z": BLUE,
                },
            }
        }
        vect = get_vector_symbol(
            "x(t)", "y(t)", "z(t)",
            **matrix_config,
        )
        d_vect = get_vector_symbol(
            "\\sigma\\big(y(t) - x(t)\\big)",
            "x(t)\\big(\\rho - z(t)\\big) - y(t)",
            "x(t)y(t) - \\beta z(t)",
            **matrix_config
        )
        equation = VGroup(
            TexMobject("d \\over dt").scale(1.5),
            vect,
            TexMobject("="),
            d_vect
        )
        equation.scale(0.8)
        equation.arrange(RIGHT)
        equation.to_edge(UP)

        arrow = Vector(DOWN, color=YELLOW)
        arrow.next_to(equation, DOWN)

        self.add(equation)
        self.play(ShowCreation(arrow))
        self.wait()


class LorenzVectorField(ExternallyAnimatedScene):
    pass


class ThreeBodiesInSpace(SpecialThreeDScene):
    CONFIG = {
        "masses": [1, 6, 3],
        "colors": [RED_E, GREEN_E, BLUE_E],
        "G": 0.5,
        "play_time": 60,
    }

    def construct(self):
        self.add_axes()
        self.add_bodies()
        self.add_trajectories()
        self.let_play()

    def add_axes(self):
        axes = self.axes = self.get_axes()
        axes.set_stroke(width=0.5)
        self.add(axes)

        # Orient
        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-110 * DEGREES,
        )
        self.begin_ambient_camera_rotation()

    def add_bodies(self):
        masses = self.masses
        colors = self.colors

        bodies = self.bodies = VGroup()
        velocity_vectors = VGroup()

        centers = [
            np.dot(
                4 * (np.random.random(3) - 0.5),
                [RIGHT, UP, OUT]
            )
            for x in range(len(masses))
        ]

        for mass, color, center in zip(masses, colors, centers):
            body = self.get_sphere(
                checkerboard_colors=[
                    color, color
                ],
                color=color,
                stroke_width=0.1,
            )
            body.set_opacity(0.75)
            body.mass = mass
            body.set_width(0.15 * np.sqrt(mass))

            body.point = center
            body.move_to(center)

            to_others = [
                center - center2
                for center2 in centers
            ]
            velocity = 0.2 * mass * normalize(np.cross(*filter(
                lambda diff: get_norm(diff) > 0,
                to_others
            )))

            body.velocity = velocity
            body.add_updater(self.update_body)

            vect = self.get_velocity_vector_mob(body)

            bodies.add(body)
            velocity_vectors.add(vect)

            self.add(body)
            # self.add(vect)

        total_mass = np.sum([body.mass for body in bodies])
        center_of_mass = reduce(op.add, [
            body.mass * body.get_center() / total_mass
            for body in bodies
        ])
        average_momentum = reduce(op.add, [
            body.mass * body.velocity / total_mass
            for body in bodies
        ])
        for body in bodies:
            body.shift(-center_of_mass)
            body.velocity -= average_momentum

    def add_trajectories(self):
        def update_trajectory(traj, dt):
            new_point = traj.body.point
            if get_norm(new_point - traj.points[-1]) > 0.01:
                traj.add_smooth_curve_to(new_point)

        for body in self.bodies:
            traj = VMobject()
            traj.body = body
            traj.start_new_path(body.point)
            traj.set_stroke(body.color, 1, opacity=0.75)
            traj.add_updater(update_trajectory)
            self.add(traj, body)

    def let_play(self):
        # Break it up to see partial files as
        # it's rendered
        for x in range(int(self.play_time)):
            self.wait()

    #
    def get_velocity_vector_mob(self, body):
        def draw_vector():
            center = body.get_center()
            vect = Arrow(
                center,
                center + body.velocity,
                buff=0,
                color=RED,
            )
            vect.set_shade_in_3d(True)
            return vect
            # length = vect.get_length()
            # if length > 2:
            #     vect.scale(
            #         2 / length,
            #         about_point=vect.get_start(),
            #     )
        return always_redraw(draw_vector)

    def update_body(self, body, dt):
        G = self.G
        acceleration = np.zeros(3)
        for body2 in self.bodies:
            if body2 is body:
                continue
            diff = body2.point - body.point
            m2 = body2.mass
            R = get_norm(diff)
            acceleration += G * m2 * diff / (R**3)

        num_mid_steps = 100
        for x in range(num_mid_steps):
            body.point += body.velocity * dt / num_mid_steps
            body.velocity += acceleration * dt / num_mid_steps
        body.move_to(body.point)
        return body


class AltThreeBodiesInSpace(ThreeBodiesInSpace):
    CONFIG = {
        "random_seed": 6,
        "masses": [1, 2, 6],
    }


class TwoBodiesInSpace(ThreeBodiesInSpace):
    CONFIG = {
        "colors": [GREY, BLUE],
        "masses": [1, 6],
        "play_time": 5,
    }

    def construct(self):
        self.add_axes()
        self.add_bodies()
        self.add_trajectories()
        self.let_play()


class DefineODECopy(DefineODE):
    pass


class WriteODESolvingCode(ExternallyAnimatedScene):
    pass


class InaccurateComputation(Scene):
    def construct(self):
        h_line = DashedLine(LEFT_SIDE, RIGHT_SIDE)
        h_line.to_edge(UP, buff=1.5)
        words = VGroup(
            TextMobject("Real number"),
            TextMobject("IEEE 754\\\\representation"),
            TextMobject("Error"),
        )
        for i, word in zip([-1, 0, 1], words):
            word.next_to(h_line, UP)
            word.shift(i * FRAME_WIDTH * RIGHT / 3)

        lines = VGroup(*[
            DashedLine(TOP, BOTTOM)
            for x in range(4)
        ])
        lines.arrange(RIGHT)
        lines.stretch_to_fit_width(FRAME_WIDTH)

        self.add(h_line, lines[1:-1], words)

        numbers = VGroup(
            TexMobject("\\pi").scale(2),
            TexMobject("e^{\\sqrt{163}\\pi}").scale(1.5),
        )
        numbers.set_color(YELLOW)
        numbers.set_stroke(width=0, background=True)

        bit_strings = VGroup(
            TexMobject(
                "01000000",
                "01001001",
                "00001111",
                "11011011",
            ),
            TexMobject(
                "01011100",
                "01101001",
                "00101110",
                "00011001",
            )
        )
        for mob in bit_strings:
            mob.arrange(DOWN, buff=SMALL_BUFF)
            for word in mob:
                for submob, bit in zip(word, word.get_tex_string()):
                    if bit == "0":
                        submob.set_color(LIGHT_GREY)
        errors = VGroup(
            TexMobject(
                "\\approx 8.7422 \\times 10^{-8}"
            ),
            TexMobject(
                "\\approx 5{,}289{,}803{,}032.00",
            ),
        )
        errors.set_color(RED)

        content = VGroup(numbers, bit_strings, errors)

        for group, word in zip(content, words):
            group[1].shift(3 * DOWN)
            group.move_to(DOWN)
            group.match_x(word)

        self.play(*map(Write, numbers))
        self.wait()
        self.play(
            TransformFromCopy(numbers, bit_strings),
            lag_ratio=0.01,
            run_time=2,
        )
        self.wait()
        self.play(FadeInFrom(errors, 3 * LEFT))
        self.wait()


class NewSceneName(Scene):
    def construct(self):
        pass
