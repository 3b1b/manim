from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.shared_constructs import *


def pendulum_vector_field(point, mu=0.1, g=9.8, L=3):
    theta, omega = point[:2]
    return np.array([
        omega,
        -np.sqrt(g / L) * np.sin(theta) - mu * omega,
        0,
    ])


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


class SmallAngleApproximationTex(Scene):
    def construct(self):
        approx = TexMobject(
            "\\sin", "(", "\\theta", ") \\approx \\theta",
            tex_to_color_map={"\\theta": RED},
            arg_separator="",
        )

        implies = TexMobject("\\Downarrow")
        period = TexMobject(
            "\\text{Period}", "\\approx",
            "2\\pi \\sqrt{\\,{L} / {g}}",
            **Lg_formula_config,
        )
        group = VGroup(approx, implies, period)
        group.arrange(DOWN)

        approx_brace = Brace(approx, UP, buff=SMALL_BUFF)
        approx_words = TextMobject(
            "For small $\\theta$",
            tex_to_color_map={"$\\theta$": RED},
        )
        approx_words.scale(0.75)
        approx_words.next_to(approx_brace, UP, SMALL_BUFF)

        self.add(approx, approx_brace, approx_words)
        self.play(
            Write(implies),
            FadeInFrom(period, LEFT)
        )
        self.wait()


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


class StrogatzQuote(Scene):
    def construct(self):
        law_words = "laws of physics"
        language_words = "language of differential equations"
        author = "-Steven Strogatz"
        quote = TextMobject(
            """
            \\Large
            ``Since Newton, mankind has come to realize
            that the laws of physics are always expressed
            in the language of differential equations.''\\\\
            """ + author,
            alignment="",
            arg_separator=" ",
            substrings_to_isolate=[law_words, language_words, author]
        )
        law_part = quote.get_part_by_tex(law_words)
        language_part = quote.get_part_by_tex(language_words)
        author_part = quote.get_part_by_tex(author)
        quote.set_width(12)
        quote.to_edge(UP)
        quote[-2].shift(SMALL_BUFF * LEFT)
        author_part.shift(RIGHT + 0.5 * DOWN)
        author_part.scale(1.2, about_edge=UL)

        movers = VGroup(*quote[:-1].family_members_with_points())
        for mover in movers:
            mover.save_state()
            disc = Circle(radius=0.05)
            disc.set_stroke(width=0)
            disc.set_fill(BLACK, 0)
            disc.move_to(mover)
            mover.become(disc)
        self.play(
            FadeInFrom(author_part, LEFT),
            LaggedStartMap(
                # FadeInFromLarge,
                # quote[:-1].family_members_with_points(),
                Restore, movers,
                lag_ratio=0.005,
                run_time=2,
            )
            # FadeInFromDown(quote[:-1]),
            # lag_ratio=0.01,
        )
        self.wait()
        self.play(
            Write(law_part.copy().set_color(YELLOW)),
            run_time=1,
        )
        self.wait()
        self.play(
            Write(language_part.copy().set_color(BLUE)),
            run_time=1.5,
        )
        self.wait(2)


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
