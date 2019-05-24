from manimlib.imports import *
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
    CONFIG = {
        "height": 1,
        "width": 3,
    }

    def construct(self):
        rect = Rectangle(
            height=self.height,
            width=self.width,
        )
        rect.set_stroke(YELLOW)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))


class ShowSquare(ShowRect):
    CONFIG = {
        "height": 3,
        "width": 3,
    }


class WhenChangeIsEasier(Scene):
    def construct(self):
        pass


class AirResistanceBrace(Scene):
    def construct(self):
        brace = Brace(Line(ORIGIN, RIGHT), DOWN)
        word = TextMobject("Air resistance")
        word.next_to(brace, DOWN)
        self.play(GrowFromCenter(brace), FadeInFrom(word, UP))
        self.wait()


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
        "zoomed_thumbnail_index": 0,
    }

    def construct(self):
        self.add_title()
        self.show_thumbnails()
        self.zoom_in_to_one_thumbnail()
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

        self.add_phase_space_preview(thumbnails[0])
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

        self.thumbnails = thumbnails

    def zoom_in_to_one_thumbnail(self):
        self.play(
            self.camera_frame.replace,
            self.thumbnails[self.zoomed_thumbnail_index],
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
    def add_phase_space_preview(self, thumbnail):
        image = ImageMobject("LovePhaseSpace")
        image.replace(thumbnail)
        thumbnail.add(image)

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
    CONFIG = {
        "flash": True,
        "add_ball_copies": True,
    }

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
        total_time = 6

        ball = self.get_ball()

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
            ball_copy = ball.copy()
            ball_copy.clear_updaters()
            ball_copies.add(ball_copy)

            if self.add_ball_copies:
                self.add(v_vect_copy)
                self.add(ball_copy, ball)

            dashed_graph.save_state()
            kw = {
                "rate_func": lambda alpha: interpolate(
                    t1 / total_time,
                    t2 / total_time,
                    alpha
                )
            }
            anims = [
                ShowCreation(dashed_graph, **kw),
                MoveAlongPath(ball, graph, **kw),
                MoveAlongPath(v_point, velocity_graph, **kw),
                ApplyMethod(
                    time_tracker.increment_value, 1,
                    rate_func=linear
                ),
            ]
            if self.flash:
                anims.append(flash)
            self.play(*anims, run_time=1)
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

    #
    def get_ball(self):
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
        return ball


class ShowSimpleTrajectory(ShowGravityAcceleration):
    CONFIG = {
        "flash": False,
    }

    def construct(self):
        self.show_trajectory()


class SimpleProjectileEquation(ShowGravityAcceleration):
    CONFIG = {
        "y0": 0,
        "g": 9.8,
        "axes_config": {
            "x_min": 0,
            "x_max": 6,
            "x_axis_config": {
                "unit_size": 1.5,
                "tip_width": 0.15,
            },
            "y_min": -30,
            "y_max": 35,
            "y_axis_config": {
                "unit_size": 0.1,
                "numbers_with_elongated_ticks": range(
                    -30, 35, 10
                ),
                "tick_size": 0.05,
                "numbers_to_show": range(-30, 31, 10),
                "tip_width": 0.15,
            },
            "center_point": 2 * LEFT,
        }
    }

    def construct(self):
        self.add_axes()
        self.setup_trajectory()

        self.show_trajectory()
        self.show_equation()
        self.solve_for_velocity()
        self.solve_for_position()

    def add_axes(self):
        axes = self.axes = Axes(**self.axes_config)
        axes.set_stroke(width=2)
        axes.add_coordinates()

        t_label = TexMobject("t")
        t_label.next_to(axes.x_axis.get_right(), UL)
        axes.add(t_label)

        self.add(axes)

    def setup_trajectory(self):
        axes = self.axes
        total_time = self.total_time = 5

        ball = self.get_ball()
        offset_vector = 3 * LEFT

        g = self.g
        y0 = self.y0
        v0 = 0.5 * g * total_time

        t_tracker = ValueTracker(0)
        get_t = t_tracker.get_value

        # Position
        def y_func(t):
            return -0.5 * g * t**2 + v0 * t + y0

        graph_template = axes.get_graph(y_func, x_max=total_time)
        graph_template.set_stroke(width=2)
        traj_template = graph_template.copy()
        traj_template.stretch(0, 0)
        traj_template.move_to(
            axes.coords_to_point(0, 0), DOWN
        )
        traj_template.shift(offset_vector)
        traj_template.set_stroke(width=0.5)

        graph = VMobject()
        graph.set_stroke(BLUE, 2)
        traj = VMobject()
        traj.set_stroke(WHITE, 0.5)
        graph.add_updater(lambda g: g.pointwise_become_partial(
            graph_template, 0, get_t() / total_time
        ))
        traj.add_updater(lambda t: t.pointwise_become_partial(
            traj_template, 0, get_t() / total_time
        ))

        def get_ball_point():
            return axes.coords_to_point(
                0, y_func(get_t())
            ) + offset_vector

        f_always(ball.move_to, get_ball_point)

        h_line = always_redraw(lambda: DashedLine(
            get_ball_point(),
            axes.input_to_graph_point(get_t(), graph_template),
            stroke_width=1,
        ))

        y_label = TexMobject("y", "(t)")
        y_label.set_color_by_tex("y", BLUE)
        y_label.add_updater(
            lambda m: m.next_to(
                graph.get_last_point(),
                UR, SMALL_BUFF,
            )
        )

        # Velocity
        def v_func(t):
            return -g * t + v0

        def get_v_vect():
            return Vector(
                axes.y_axis.unit_size * v_func(get_t()) * UP,
                color=RED,
            )
        v_vect = always_redraw(
            lambda: get_v_vect().shift(get_ball_point())
        )
        v_brace = always_redraw(lambda: Brace(v_vect, LEFT))
        dy_dt_label = TexMobject(
            "{d", "y", "\\over dt}", "(t)",
        )
        dy_dt_label.scale(0.8)
        dy_dt_label.set_color_by_tex("y", BLUE)
        y_dot_label = TexMobject("\\dot y", "(t)")
        y_dot_label.set_color_by_tex("\\dot y", RED)
        for label in dy_dt_label, y_dot_label:
            label.add_updater(lambda m: m.next_to(
                v_brace, LEFT, SMALL_BUFF,
            ))

        graphed_v_vect = always_redraw(
            lambda: get_v_vect().shift(
                axes.coords_to_point(get_t(), 0)
            )
        )
        v_graph_template = axes.get_graph(
            v_func, x_max=total_time,
        )
        v_graph = VMobject()
        v_graph.set_stroke(RED, 2)
        v_graph.add_updater(lambda m: m.pointwise_become_partial(
            v_graph_template,
            0, get_t() / total_time,
        ))

        # Acceleration
        def get_a_vect():
            return Vector(
                axes.y_axis.unit_size * g * DOWN
            )

        a_vect = get_a_vect()
        a_vect.add_updater(lambda a: a.move_to(
            get_ball_point(), UP,
        ))
        a_brace = Brace(a_vect, RIGHT)
        always(a_brace.next_to, a_vect, RIGHT, SMALL_BUFF)
        d2y_dt2_label = TexMobject(
            "d^2", "{y}", "\\over dt}", "(t)"
        )
        d2y_dt2_label.scale(0.8)
        d2y_dt2_label.set_color_by_tex(
            "y", BLUE,
        )
        y_ddot_label = TexMobject("\\ddot y", "(t)")
        y_ddot_label.set_color_by_tex("\\ddot y", YELLOW)
        for label in d2y_dt2_label, y_ddot_label:
            label.add_updater(lambda m: m.next_to(
                a_brace, RIGHT, SMALL_BUFF
            ))
        a_graph = axes.get_graph(
            lambda t: -g, x_max=total_time,
        )
        a_graph.set_stroke(YELLOW, 2)

        graphed_a_vect = get_a_vect()
        graphed_a_vect.add_updater(lambda a: a.move_to(
            axes.coords_to_point(get_t(), 0), UP,
        ))

        self.set_variables_as_attrs(
            t_tracker,
            graph,
            y_label,
            traj,
            h_line,
            v_vect,
            v_brace,
            dy_dt_label,
            y_dot_label,
            ball,
            graphed_v_vect,
            v_graph,
            a_vect,
            a_brace,
            d2y_dt2_label,
            y_ddot_label,
            a_graph,
            graphed_a_vect,
        )

    def show_trajectory(self):
        self.add(
            self.h_line,
            self.traj,
            self.ball,
            self.graph,
            self.y_label,
        )
        self.play_trajectory()
        self.wait()

        self.add(
            self.v_vect,
            self.v_brace,
            self.dy_dt_label,
            self.ball,
            self.graphed_v_vect,
            self.v_graph,
        )
        self.play_trajectory()
        self.wait()

        self.add(
            self.a_vect,
            self.ball,
            self.a_brace,
            self.d2y_dt2_label,
            self.a_graph,
            self.graphed_a_vect,
        )
        self.play_trajectory()
        self.wait()

        self.play(
            ReplacementTransform(
                self.dy_dt_label,
                self.y_dot_label,
            ),
            ShowCreationThenFadeAround(
                self.y_dot_label,
            ),
        )
        self.play(
            ReplacementTransform(
                self.d2y_dt2_label,
                self.y_ddot_label,
            ),
            ShowCreationThenFadeAround(
                self.y_ddot_label,
            ),
        )

    def show_equation(self):
        y_ddot = self.y_ddot_label
        new_y_ddot = y_ddot.deepcopy()
        new_y_ddot.clear_updaters()

        equation = VGroup(
            new_y_ddot,
            *TexMobject(
                "=", "-g",
                tex_to_color_map={"-g": YELLOW},
            ),
        )
        new_y_ddot.next_to(equation[1], LEFT, SMALL_BUFF)
        equation.move_to(self.axes)
        equation.to_edge(UP)

        self.play(
            TransformFromCopy(y_ddot, new_y_ddot),
            Write(equation[1:]),
            FadeOut(self.graph),
            FadeOut(self.y_label),
            FadeOut(self.h_line),
            FadeOut(self.v_graph),
            FadeOut(self.graphed_v_vect),
            FadeOut(self.graphed_a_vect),
        )

        self.equation = equation

    def solve_for_velocity(self):
        axes = self.axes
        equation = self.equation
        v_graph = self.v_graph.deepcopy()
        v_graph.clear_updaters()
        v_start_point = v_graph.get_start()
        origin = axes.coords_to_point(0, 0)
        offset = v_start_point - origin
        v_graph.shift(-offset)

        tex_question, answer1, answer2 = derivs = [
            TexMobject(
                "{d", "(", *term, ")", "\\over", "dt}", "(t)",
                "=", "-g",
                tex_to_color_map={
                    "-g": YELLOW,
                    "v_0": RED,
                    "?": RED,
                }
            )
            for term in [
                ("?", "?", "?", "?"),
                ("-g", "t"),
                ("-g", "t", "+", "v_0",),
            ]
        ]
        for x in range(2):
            answer1.submobjects.insert(
                4, VectorizedPoint(answer1[4].get_left())
            )
        for deriv in derivs:
            deriv.next_to(equation, DOWN, MED_LARGE_BUFF)

        question = TextMobject(
            "What function has slope $-g$?",
            tex_to_color_map={"$-g$": YELLOW},
        )
        question.next_to(tex_question, DOWN)
        question.set_stroke(BLACK, 5, background=True)
        question.add_background_rectangle()

        v0_dot = Dot(v_start_point, color=PINK)
        v0_label = TexMobject("v_0")
        v0_label.set_color(RED)
        v0_label.next_to(v0_dot, UR, buff=0)

        y_dot_equation = TexMobject(
            "{\\dot y}", "(t)", "=",
            "-g", "t", "+", "v_0",
            tex_to_color_map={
                "{\\dot y}": RED,
                "-g": YELLOW,
                "v_0": RED,
            }
        )
        y_dot_equation.to_corner(UR)

        self.play(
            FadeInFrom(tex_question, DOWN),
            FadeInFrom(question, UP)
        )
        self.wait()
        self.add(v_graph, question)
        self.play(
            ReplacementTransform(tex_question, answer1),
            ShowCreation(v_graph),
        )
        self.wait()
        self.play(
            ReplacementTransform(answer1, answer2),
            v_graph.shift, offset,
        )
        self.play(
            FadeInFromLarge(v0_dot),
            FadeInFromDown(v0_label),
        )
        self.wait()
        self.play(
            TransformFromCopy(
                answer2[2:6], y_dot_equation[3:],
            ),
            Write(y_dot_equation[:3]),
            equation.shift, LEFT,
        )
        self.play(
            FadeOut(question),
            FadeOut(answer2),
        )

        self.remove(v_graph)
        self.add(self.v_graph)
        self.y_dot_equation = y_dot_equation

    def solve_for_position(self):
        # Largely copied from above...not great
        equation = self.equation
        y_dot_equation = self.y_dot_equation
        graph = self.graph

        all_terms = [
            ("?", "?", "?", "?"),
            ("-", "(1/2)", "g", "t^2", "+", "v_0", "t"),
            ("-", "(1/2)", "g", "t^2", "+", "v_0", "t", "+", "y_0"),
        ]
        tex_question, answer1, answer2 = derivs = [
            TexMobject(
                "{d", "(", *term, ")", "\\over", "dt}", "(t)",
                "=",
                "-g", "t", "+", "v_0",
                tex_to_color_map={
                    "g": YELLOW,
                    "v_0": RED,
                    "?": BLUE,
                    "y_0": BLUE,
                }
            )
            for term in all_terms
        ]
        answer1.scale(0.8)
        answer2.scale(0.8)
        for deriv, terms in zip(derivs, all_terms):
            for x in range(len(all_terms[-1]) - len(terms)):
                n = 2 + len(terms)
                deriv.submobjects.insert(
                    n, VectorizedPoint(deriv[n].get_left())
                )
            deriv.next_to(
                VGroup(equation, y_dot_equation),
                DOWN, MED_LARGE_BUFF + SMALL_BUFF
            )
            deriv.shift_onto_screen()
            deriv.add_background_rectangle_to_submobjects()

        y_equation = TexMobject(
            "y", "(t)", "=",
            "-", "(1/2)", "g", "t^2",
            "+", "v_0", "t",
            "+", "y_0",
            tex_to_color_map={
                "y": BLUE,
                "g": YELLOW,
                "v_0": RED,
            }
        )
        y_equation.next_to(
            VGroup(equation, y_dot_equation),
            DOWN, MED_LARGE_BUFF,
        )

        self.play(
            FadeInFrom(tex_question, DOWN),
        )
        self.wait()
        self.add(graph, tex_question)
        self.play(
            ReplacementTransform(tex_question, answer1),
            ShowCreation(graph),
        )
        self.add(graph, answer1)
        self.wait()
        self.play(ReplacementTransform(answer1, answer2))
        self.add(graph, answer2)
        g_updaters = graph.updaters
        graph.clear_updaters()
        self.play(
            graph.shift, 2 * DOWN,
            rate_func=there_and_back,
            run_time=2,
        )
        graph.add_updater(g_updaters[0])
        self.wait()
        br = BackgroundRectangle(y_equation)
        self.play(
            FadeIn(br),
            ReplacementTransform(
                answer2[2:11],
                y_equation[3:]
            ),
            FadeIn(y_equation[:3]),
            FadeOut(answer2[:2]),
            FadeOut(answer2[11:]),
        )
        self.play(ShowCreationThenFadeAround(y_equation))
        self.play_trajectory()

    #
    def play_trajectory(self, *added_anims, **kwargs):
        self.t_tracker.set_value(0)
        self.play(
            ApplyMethod(
                self.t_tracker.set_value, 5,
                rate_func=linear,
                run_time=self.total_time,
            ),
            *added_anims,
        )
        self.wait()


class SimpleProjectileEquationVGraphFreedom(SimpleProjectileEquation):
    def construct(self):
        self.add_axes()
        self.setup_trajectory()
        self.clear()
        v_graph = self.v_graph
        self.t_tracker.set_value(5)
        v_graph.update()
        v_graph.clear_updaters()
        self.add(v_graph)
        self.play(v_graph.shift, 5 * DOWN, run_time=2)
        self.play(v_graph.shift, 5 * UP, run_time=2)


class UniversalGravityLawSymbols(Scene):
    def construct(self):
        x1_tex = "\\vec{\\textbf{x}}_1"
        x2_tex = "\\vec{\\textbf{x}}_2"
        a1_tex = "\\vec{\\textbf{a}}_1"
        new_brown = interpolate_color(LIGHT_GREY, LIGHT_BROWN, 0.5)
        law = TexMobject(
            "F_1", "=", "m_1", a1_tex, "=",
            "G", "m_1", "m_2",
            "\\left({", x2_tex, "-", x1_tex, "\\over",
            "||", x2_tex, "-", x1_tex, "||", "}\\right)",
            "\\left({", "1", "\\over",
            "||", x2_tex, "-", x1_tex, "||^2", "}\\right)",
            tex_to_color_map={
                x1_tex: BLUE_C,
                "m_1": BLUE_C,
                x2_tex: new_brown,
                "m_2": new_brown,
                a1_tex: YELLOW,
            }
        )
        law.to_edge(UP)

        force = law[:4]
        constants = law[4:8]
        unit_vect = law[8:19]
        inverse_square = law[19:]
        parts = VGroup(
            force, unit_vect, inverse_square
        )

        words = VGroup(
            TextMobject("Force on\\\\mass 1"),
            TextMobject("Unit vector\\\\towards mass 2"),
            TextMobject("Inverse square\\\\law"),
        )

        self.add(law)

        braces = VGroup()
        rects = VGroup()
        for part, word in zip(parts, words):
            brace = Brace(part, DOWN)
            word.scale(0.8)
            word.next_to(brace, DOWN)
            rect = SurroundingRectangle(part)
            rect.set_stroke(YELLOW, 1)
            braces.add(brace)
            rects.add(rect)

        self.play(
            ShowCreationThenFadeOut(rects[0]),
            GrowFromCenter(braces[0]),
            FadeInFrom(words[0], UP)
        )
        self.wait()
        self.play(
            ShowCreationThenFadeOut(rects[1]),
            GrowFromCenter(braces[1]),
            FadeInFrom(words[1], UP)
        )
        self.wait()
        self.play(
            ShowCreationThenFadeOut(rects[2]),
            TransformFromCopy(*braces[1:3]),
            FadeInFrom(words[2], UP),
        )
        self.wait()

        # Position derivative
        v1_tex = "\\vec{\\textbf{v}}_1"
        kw = {
            "tex_to_color_map": {
                x1_tex: BLUE_C,
                v1_tex: RED,
            }
        }
        x_deriv = TexMobject(
            "{d", x1_tex, "\\over", "dt}", "=", v1_tex, **kw
        )
        x_deriv.to_corner(UL)
        v_deriv = TexMobject(
            "{d", v1_tex, "\\over", "dt}", "=", **kw
        )

        # Make way
        law.generate_target()
        lt = law.target
        lt.to_edge(RIGHT)
        lt[6].fade(1)
        lt[:6].align_to(lt[6], RIGHT)
        lt[:3].fade(1)
        v_deriv.next_to(lt[3], LEFT)

        self.play(
            FadeInFromDown(x_deriv),
            MoveToTarget(law),
            braces[1:].align_to, lt, RIGHT,
            MaintainPositionRelativeTo(words[1:], braces[1:]),
            FadeOut(words[0]),
            FadeOut(braces[0]),
        )
        self.play(ShowCreationThenFadeAround(x_deriv))

        self.play(
            TransformFromCopy(
                x_deriv.get_part_by_tex(v1_tex),
                v_deriv.get_part_by_tex(v1_tex),
            ),
            Write(VGroup(*filter(
                lambda m: m is not v_deriv.get_part_by_tex(v1_tex),
                v_deriv,
            )))
        )

        x_parts = law.get_parts_by_tex(x1_tex)
        self.play(
            TransformFromCopy(
                x_deriv.get_parts_by_tex(x1_tex),
                x_parts.copy(),
                remover=True,
                path_arc=30 * DEGREES,
            )
        )
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeAround,
                x_parts
            )
        )
        self.wait()


class ExampleTypicalODE(TeacherStudentsScene):
    def construct(self):
        examples = VGroup(
            TexMobject(
                "{\\dot x}(t) = k{x}(t)",
                tex_to_color_map={
                    "{\\dot x}": BLUE,
                    "{x}": BLUE,
                },
            ),
            get_ode(),
            TexMobject(
                "{\\partial T", "\\over", "\\partial t} = ",
                "{\\partial^2 T", "\\over", "\\partial x^2}", "+",
                "{\\partial^2 T", "\\over", "\\partial y^2}", "+",
                "{\\partial^2 T", "\\over", "\\partial z^2}",
                tex_to_color_map={
                    "T": RED,
                }
            ),
        )
        examples[1].get_parts_by_tex("theta").set_color(GREEN)
        examples.arrange(DOWN, buff=MED_LARGE_BUFF)
        examples.to_edge(UP)

        self.play(
            FadeInFrom(examples[0], UP),
            self.teacher.change, "raise_right_hand",
        )
        self.play(
            FadeInFrom(examples[1], UP),
            self.get_student_changes(
                *3 * ["pondering"],
                look_at_arg=examples,
            ),
        )
        self.play(
            FadeInFrom(examples[2], UP)
        )
        self.wait(5)


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
                "{\\dot\\theta}": RED,
                "{\\ddot\\theta}": YELLOW,
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
                color=RED,
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
            curve.set_stroke(YELLOW, 1)
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
            TextMobject("= Slope").set_color(RED),
            TextMobject("= ``Curvature''").set_color(YELLOW),
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
            Indicate(second_deriv, color=YELLOW),
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
                "{\\dot x}": RED,
                "{\\ddot x}": YELLOW,
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
                "{\\dot x}": RED,
                "{\\ddot x}": YELLOW,
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
                color=RED,
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
            curve.set_stroke(YELLOW, 1)
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
            TextMobject("= Slope").set_color(RED),
            TextMobject("= ``Curvature''").set_color(YELLOW),
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

        centers = self.get_initial_positions()

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
            body.radius = 0.08 * np.sqrt(mass)
            body.set_width(2 * body.radius)

            body.point = center
            body.move_to(center)

            body.velocity = self.get_initial_velocity(
                center, centers, mass
            )

            vect = self.get_velocity_vector_mob(body)

            bodies.add(body)
            velocity_vectors.add(vect)

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

    def get_initial_positions(self):
        return [
            np.dot(
                4 * (np.random.random(3) - 0.5),
                [RIGHT, UP, OUT]
            )
            for x in range(len(self.masses))
        ]

    def get_initial_velocity(self, center, centers, mass):
        to_others = [
            center - center2
            for center2 in centers
        ]
        velocity = 0.2 * mass * normalize(np.cross(*filter(
            lambda diff: get_norm(diff) > 0,
            to_others
        )))
        return velocity

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
        bodies = self.bodies
        bodies.add_updater(self.update_bodies)
        # Break it up to see partial files as
        # it's rendered
        self.add(bodies)
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

    def update_bodies(self, bodies, dt):
        G = self.G

        num_mid_steps = 1000
        for x in range(num_mid_steps):
            for body in bodies:
                acceleration = np.zeros(3)
                for body2 in bodies:
                    if body2 is body:
                        continue
                    diff = body2.point - body.point
                    m2 = body2.mass
                    R = get_norm(diff)
                    acceleration += G * m2 * diff / (R**3)
                body.point += body.velocity * dt / num_mid_steps
                body.velocity += acceleration * dt / num_mid_steps
        for body in bodies:
            body.move_to(body.point)
        return bodies


class AltThreeBodiesInSpace(ThreeBodiesInSpace):
    CONFIG = {
        "random_seed": 6,
        "masses": [1, 2, 6],
    }


class TwoBodiesInSpace(ThreeBodiesInSpace):
    CONFIG = {
        "colors": [GREY, BLUE],
        "masses": [6, 36],
        "play_time": 60,
    }

    def construct(self):
        self.add_axes()
        self.add_bodies()
        self.add_trajectories()
        self.add_velocity_vectors()
        self.add_force_vectors()
        self.let_play()

    def add_bodies(self):
        super().add_bodies()
        for body in self.bodies:
            body.point = 3 * normalize(body.get_center())
            # body.point += 2 * IN
            # body.velocity += (4 / 60) * OUT
            body.move_to(body.point)

    def get_initial_positions(self):
        return [
            np.dot(
                6 * (np.random.random(3) - 0.5),
                [RIGHT, UP, ORIGIN]
            )
            for x in range(len(self.masses))
        ]

    def get_initial_velocity(self, center, centers, mass):
        return 0.75 * normalize(np.cross(center, OUT))

    def add_velocity_vectors(self):
        vectors = VGroup(*[
            self.get_velocity_vector(body)
            for body in self.bodies
        ])
        self.velocity_vectors = vectors
        self.add(vectors)

    def get_velocity_vector(self, body):
        def create_vector(b):
            v = Vector(
                b.velocity,
                color=RED,
                max_stroke_width_to_length_ratio=3,
            )
            v.set_stroke(width=3)
            v.shift(
                b.point + b.radius * normalize(b.velocity) -
                v.get_start(),
            )
            v.set_shade_in_3d(True)
            return v
        return always_redraw(lambda: create_vector(body))

    def add_force_vectors(self):
        vectors = VGroup(*[
            self.get_force_vector(b1, b2)
            for (b1, b2) in (self.bodies, self.bodies[::-1])
        ])
        self.force_vectors = vectors
        self.add(vectors)

    def get_force_vector(self, body1, body2):
        def create_vector(b1, b2):
            r = b2.point - b1.point
            F = r / (get_norm(r)**3)
            v = Vector(
                4 * F,
                color=YELLOW,
                max_stroke_width_to_length_ratio=3,
            )
            v.set_stroke(width=3)
            v.shift(
                b1.point + b1.radius * normalize(F) -
                v.get_start(),
            )
            v.set_shade_in_3d(True)
            return v
        return always_redraw(lambda: create_vector(body1, body2))


class TwoBodiesWithZPart(TwoBodiesInSpace):
    def add_bodies(self):
        super().add_bodies()
        for body in self.bodies:
            body.point += 3 * IN
            body.velocity += (6 / 60) * OUT


class LoveExample(PiCreatureScene):
    def construct(self):
        self.show_hearts()
        self.add_love_trackers()
        self.break_down_your_rule()
        self.break_down_their_rule()

    def create_pi_creatures(self):
        you = You()
        you.shift(FRAME_WIDTH * LEFT / 4)
        you.to_edge(DOWN)

        tau = TauCreature(color=GREEN)
        tau.flip()
        tau.shift(FRAME_WIDTH * RIGHT / 4)
        tau.to_edge(DOWN)

        self.you = you
        self.tau = tau
        return (you, tau)

    def show_hearts(self):
        you, tau = self.you, self.tau
        hearts = VGroup()
        n_hearts = 20
        for x in range(n_hearts):
            heart = SuitSymbol("hearts")
            heart.scale(0.5 + 2 * np.random.random())
            heart.shift(np.random.random() * 4 * RIGHT)
            heart.shift(np.random.random() * 4 * UP)
            hearts.add(heart)
        hearts.move_to(2 * DOWN)
        hearts.add_updater(lambda m, dt: m.shift(2 * dt * UP))

        self.add(hearts)
        self.play(
            LaggedStartMap(
                UpdateFromAlphaFunc, hearts,
                lambda heart: (
                    heart,
                    lambda h, a: h.set_opacity(
                        there_and_back(a)
                    ).shift(0.02 * UP)
                ),
                lag_ratio=0.01,
                run_time=3,
                suspend_mobject_updating=False,
            ),
            ApplyMethod(
                you.change, 'hooray', tau.eyes,
                run_time=2,
                rate_func=squish_rate_func(smooth, 0.5, 1)
            ),
            ApplyMethod(
                tau.change, 'hooray', you.eyes,
                run_time=2,
                rate_func=squish_rate_func(smooth, 0.5, 1)
            ),
        )
        self.remove(hearts)
        self.wait()

    def add_love_trackers(self):
        self.init_ps_point()
        self.add_love_decimals()
        self.add_love_number_lines()
        self.tie_creature_state_to_ps_point()

        self.play(Rotating(
            self.ps_point,
            radians=-7 * TAU / 8,
            about_point=ORIGIN,
            run_time=10,
            rate_func=linear,
        ))
        self.wait()

    def break_down_your_rule(self):
        label1 = self.love_1_label
        label2 = self.love_2_label
        ps_point = self.ps_point

        up_arrow = Vector(UP, color=GREEN)
        down_arrow = Vector(DOWN, color=RED)
        for arrow in (up_arrow, down_arrow):
            arrow.next_to(label1, RIGHT)

        self.play(GrowArrow(up_arrow))
        self.play(
            self.tau.love_eyes.scale, 1.25,
            self.tau.love_eyes.set_color, BLUE_C,
            rate_func=there_and_back,
        )
        self.play(
            ps_point.shift, 6 * RIGHT,
            run_time=2,
        )
        self.wait()
        ps_point.shift(13 * DOWN)
        self.play(
            FadeOut(up_arrow),
            GrowArrow(down_arrow),
        )
        self.play(
            ps_point.shift, 11 * LEFT,
            run_time=3,
        )
        self.wait()

        # Derivative
        equation = get_love_equation1()
        equation.shift(0.5 * UP)
        deriv, equals, a, h2 = equation

        self.play(
            Write(deriv[:-1]),
            Write(equals),
            Write(a),
            TransformFromCopy(label1[0], deriv.heart),
            TransformFromCopy(label2[0], h2),
        )
        self.wait()
        self.play(
            equation.scale, 0.5,
            equation.to_corner, UL,
            FadeOut(down_arrow)
        )

    def break_down_their_rule(self):
        label1 = self.love_1_label
        label2 = self.love_2_label
        ps_point = self.ps_point

        up_arrow = Vector(UP, color=GREEN)
        down_arrow = Vector(DOWN, color=RED)
        for arrow in (up_arrow, down_arrow):
            arrow.next_to(label2, RIGHT)

        # Derivative
        equation = get_love_equation2()
        equation.shift(0.5 * UP)
        deriv, equals, mb, h1 = equation

        self.play(
            Write(deriv[:-1]),
            Write(equals),
            Write(mb),
            TransformFromCopy(label1[0], h1),
            TransformFromCopy(label2[0], deriv.heart),
        )

        self.play(GrowArrow(up_arrow))
        self.play(
            ps_point.shift, 13 * UP,
            run_time=3,
        )
        self.wait()
        self.play(
            ps_point.shift, 11 * RIGHT,
        )
        self.play(
            FadeOut(up_arrow),
            GrowArrow(down_arrow),
        )
        self.play(
            ps_point.shift, 13 * DOWN,
            run_time=3,
        )
        self.wait()

    #
    def init_ps_point(self):
        self.ps_point = VectorizedPoint(np.array([5.0, 5.0, 0]))

    def get_love1(self):
        return self.ps_point.get_location()[0]

    def get_love2(self):
        return self.ps_point.get_location()[1]

    def set_loves(self, love1=None, love2=None):
        if love1 is not None:
            self.ps_point.set_x(love1)
        if love2 is not None:
            self.ps_point.set_x(love2)

    def add_love_decimals(self):
        self.love_1_label = self.add_love_decimal(
            1, self.get_love1, self.you.get_color(), -3,
        )
        self.love_2_label = self.add_love_decimal(
            2, self.get_love2, self.tau.get_color(), 3,
        )

    def add_love_decimal(self, index, value_func, color, x_coord):
        d = DecimalNumber(include_sign=True)
        d.add_updater(lambda d: d.set_value(value_func()))

        label = get_heart_var(index)
        label.move_to(x_coord * RIGHT)
        label.to_edge(UP)
        eq = TexMobject("=")
        eq.next_to(label, RIGHT, SMALL_BUFF)
        eq.shift(SMALL_BUFF * UP)
        d.next_to(eq, RIGHT, SMALL_BUFF)

        self.add(label, eq, d)
        return VGroup(label, eq, d)

    def add_love_number_lines(self):
        nl1 = NumberLine(
            x_min=-8,
            x_max=8,
            unit_size=0.25,
            tick_frequency=2,
            number_scale_val=0.25,
        )
        nl1.set_stroke(width=1)
        nl1.next_to(self.love_1_label, DOWN)
        nl1.add_numbers(*range(-6, 8, 2))

        nl2 = nl1.copy()
        nl2.next_to(self.love_2_label, DOWN)

        dot1 = Dot(color=self.you.get_color())
        dot1.add_updater(lambda d: d.move_to(
            nl1.number_to_point(self.get_love1())
        ))
        dot2 = Dot(color=self.tau.get_color())
        dot2.add_updater(lambda d: d.move_to(
            nl2.number_to_point(self.get_love2())
        ))

        self.add(nl1, nl2, dot1, dot2)

    def get_love_eyes(self, eyes):
        hearts = VGroup()
        for eye in eyes:
            heart = SuitSymbol("hearts")
            heart.match_width(eye)
            heart.move_to(eye)
            heart.scale(1.25)
            heart.set_stroke(BLACK, 1)
            hearts.add(heart)
        hearts.add_updater(
            lambda m: m.move_to(eyes)
        )
        return hearts

    def tie_creature_state_to_ps_point(self):
        # Quite a mess, but I'm coding in a rush here...
        you = self.you
        you_copy = you.copy()
        tau = self.tau
        tau_copy = tau.copy()

        you.love_eyes = self.get_love_eyes(you.eyes)
        tau.love_eyes = self.get_love_eyes(tau.eyes)

        self.add(you.love_eyes)
        self.add(tau.love_eyes)

        you_height = you.get_height()
        tau_height = tau.get_height()

        you_bottom = you.get_bottom()
        tau_bottom = tau.get_bottom()

        def update_you(y):
            love = self.get_love1()

            cutoff_values = [
                -5, -3, -1, 1, 3, 5
            ]
            modes = [
                "angry", "sassy", "hesitant",
                "plain",
                "happy", "hooray", "surprised",
            ]

            if love < cutoff_values[0]:
                y.change(modes[0])
            elif love >= cutoff_values[-1]:
                y.change(modes[-1])
            else:
                i = 0
                while cutoff_values[i] < love:
                    i += 1
                m1 = modes[i - 1]
                m2 = modes[i]
                y.change(m1)
                you_copy.change(m2)
                for mob in y, you_copy:
                    mob.set_height(you_height)
                    mob.move_to(you_bottom, DOWN)

                alpha = inverse_interpolate(
                    cutoff_values[i - 1],
                    cutoff_values[i],
                    love,
                )
                s_alpha = squish_rate_func(smooth, 0.25, 1)(alpha)
                if s_alpha > 0:
                    y.align_data(you_copy)
                    f1 = y.family_members_with_points()
                    f2 = you_copy.family_members_with_points()
                    for sm1, sm2 in zip(f1, f2):
                        sm1.interpolate(sm1, sm2, s_alpha)
            y.look_at(tau.eyes)
            if love < -4:
                y.look_at(LEFT_SIDE)
            # y.move_to(
            #     you_bottom + 0.025 * love * RIGHT, DOWN,
            # )

            l_alpha = np.clip(
                inverse_interpolate(5, 5.5, love),
                0, 1
            )
            y.eyes.set_opacity(1 - l_alpha)
            y.love_eyes.set_opacity(l_alpha)

            return y

        def update_tau(t):
            love = self.get_love2()

            cutoff_values = [
                -5, -1.7, 1.7, 5
            ]
            modes = [
                "angry", "confused", "plain",
                "hooray", "hooray"
            ]

            if love < cutoff_values[0]:
                t.change(modes[0])
            elif love >= cutoff_values[-1]:
                t.change(modes[-1])
            else:
                i = 0
                while cutoff_values[i] < love:
                    i += 1
                m1 = modes[i - 1]
                m2 = modes[i]
                t.change(m1)
                tau_copy.change(m2)
                for mob in t, tau_copy:
                    mob.set_height(tau_height)
                    mob.move_to(tau_bottom, DOWN)

                alpha = inverse_interpolate(
                    cutoff_values[i - 1],
                    cutoff_values[i],
                    love,
                )
                s_alpha = squish_rate_func(smooth, 0.25, 1)(alpha)
                if s_alpha > 0:
                    t.align_data(tau_copy)
                    f1 = t.family_members_with_points()
                    f2 = tau_copy.family_members_with_points()
                    for sm1, sm2 in zip(f1, f2):
                        sm1.interpolate(sm1, sm2, s_alpha)
            # t.move_to(
            #     tau_bottom + 0.025 * love * LEFT, DOWN,
            # )
            t.look_at(you.eyes)
            if love < -4:
                t.look_at(RIGHT_SIDE)

            l_alpha = np.clip(
                inverse_interpolate(5, 5.5, love),
                0, 1
            )
            t.eyes.set_opacity(1 - l_alpha)
            t.love_eyes.set_opacity(l_alpha)

        you.add_updater(update_you)
        tau.add_updater(update_tau)

        self.pi_creatures = VGroup()


class ComparePhysicsToLove(Scene):
    def construct(self):
        ode = get_ode()
        ode.to_edge(UP)
        thetas = ode.get_parts_by_tex("theta")

        love = VGroup(
            get_love_equation1(),
            get_love_equation2(),
        )
        love.scale(0.5)
        love.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        love.move_to(DOWN)
        hearts = VGroup(*filter(
            lambda sm: isinstance(sm, SuitSymbol),
            love.get_family()
        ))

        arrow = DoubleArrow(love.get_top(), ode.get_bottom())

        self.play(FadeInFrom(ode, DOWN))
        self.play(FadeInFrom(love, UP))
        self.wait()
        self.play(LaggedStartMap(
            ShowCreationThenFadeAround,
            thetas,
        ))
        self.play(LaggedStartMap(
            ShowCreationThenFadeAround,
            hearts,
        ))
        self.wait()
        self.play(ShowCreation(arrow))
        self.wait()


class FramesComparingPhysicsToLove(Scene):
    CONFIG = {
        "camera_config": {"background_color": DARKER_GREY}
    }

    def construct(self):
        ode = get_ode()
        ode.to_edge(UP)

        love = VGroup(
            get_love_equation1(),
            get_love_equation2(),
        )
        love.scale(0.5)
        love.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)

        frames = VGroup(*[
            ScreenRectangle(
                height=3.5,
                fill_color=BLACK,
                fill_opacity=1,
                stroke_width=0,
            )
            for x in range(2)
        ])
        frames.arrange(RIGHT, buff=LARGE_BUFF)
        frames.shift(DOWN)

        animated_frames = AnimatedBoundary(frames)

        ode.next_to(frames[0], UP)
        love.next_to(frames[1], UP)

        self.add(frames, animated_frames)
        self.add(ode, love)

        self.wait(15)


class PassageOfTime(Scene):
    def construct(self):
        clock = Clock()
        clock[0].set_color(BLUE)
        clock.set_stroke(width=1)
        clock.scale(0.8)
        clock.to_corner(UL)
        passage = ClockPassesTime(
            clock,
            hours_passed=48,
        )
        self.play(passage, run_time=10)


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
