from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.shared_constructs import *


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


class SetAsideSeekingSolution(Scene):
    def construct(self):
        ode = get_ode()
        ode.to_edge(UP)
        q1 = TextMobject("Find an exact solution")
        q1.set_color(YELLOW)
        q2 = TexMobject(
            "\\text{What is }", "\\theta", "(t)",
            "\\text{'s personality?}",
            tex_to_color_map={"\\theta": BLUE},
            arg_separator="",
        )
        theta = q2.get_part_by_tex("\\theta")

        for q in q1, q2:
            q.scale(1.5)
            q.next_to(ode, DOWN, MED_LARGE_BUFF)
        eyes = Eyes(theta, height=0.1)

        self.add(ode)
        self.add(q1)
        self.wait()
        self.play(
            q1.scale, 0.3,
            q1.to_corner, UR, MED_SMALL_BUFF,
        )
        self.play(FadeInFrom(q2, DOWN))
        self.play(
            eyes.blink,
            rate_func=lambda t: smooth(1 - t),
        )
        self.play(eyes.look_at, q2.get_left())
        self.play(eyes.look_at, q2.get_right())
        self.play(
            eyes.blink,
            rate_func=squish_rate_func(there_and_back)
        )
        self.wait()
        self.play(
            eyes.change_mode, "confused",
            eyes.look_at, ode.get_left(),
        )
        self.play(
            eyes.blink,
            rate_func=squish_rate_func(there_and_back)
        )


class ThreeBodySymbols(Scene):
    def construct(self):
        self.init_coord_groups()
        self.introduce_coord_groups()
        self.count_coords()

    def init_coord_groups(self):
        kwargs = {
            "bracket_v_buff": 2 * SMALL_BUFF
        }
        positions = VGroup(*[
            get_vector_symbol(*[
                "{}_{}".format(s, i)
                for s in "xyz"
            ], **kwargs)
            for i in range(1, 4)
        ])
        velocities = VGroup(*[
            get_vector_symbol(*[
                "p^{}_{}".format(s, i)
                for s in "xyz"
            ], **kwargs)
            for i in range(1, 4)
        ])
        groups = VGroup(positions, velocities)
        colors = [GREEN, RED, BLUE]
        for group in groups:
            for matrix in group:
                matrix.coords = matrix.get_entries()
                for coord, color in zip(matrix.coords, colors):
                    coord.set_color(color)
            group.arrange(RIGHT)
        groups.arrange(DOWN, buff=LARGE_BUFF)
        groups.to_edge(LEFT)

        self.coord_groups = groups

    def introduce_coord_groups(self):
        groups = self.coord_groups
        x_group, p_group = groups
        x_word = TextMobject("Positions")
        p_word = TextMobject("Momenta")
        words = VGroup(x_word, p_word)
        for word, group in zip(words, groups):
            word.next_to(group, UP)

        rect_groups = VGroup()
        for group in groups:
            rect_group = VGroup(*[
                SurroundingRectangle(
                    VGroup(*[
                        tm.coords[i]
                        for tm in group
                    ]),
                    color=WHITE,
                    stroke_width=2,
                )
                for i in range(3)
            ])
            rect_groups.add(rect_group)

        self.play(
            *[
                LaggedStartMap(
                    FadeInFrom, group,
                    lambda m: (m, UP),
                    run_time=1,
                )
                for group in groups
            ],
            *map(FadeInFromDown, words),
        )
        for rect_group in rect_groups:
            self.play(
                ShowCreationThenFadeOut(
                    rect_group,
                    lag_ratio=0.5,
                )
            )
        self.wait()

    def count_coords(self):
        coord_copies = VGroup()
        for group in self.coord_groups:
            for tex_mob in group:
                for coord in tex_mob.coords:
                    coord_copy = coord.copy()
                    coord_copy.set_stroke(
                        WHITE, 2, background=True
                    )
                    coord_copies.add(coord_copy)

        count = Integer()
        count_word = TextMobject("18", "degrees \\\\ of freedom")[1]
        count_group = VGroup(count, count_word)
        count_group.arrange(
            RIGHT,
            aligned_edge=DOWN,
        )
        count_group.scale(1.5)
        count_group.next_to(
            self.coord_groups, RIGHT,
            aligned_edge=DOWN,
        )
        count.add_updater(
            lambda m: m.set_value(len(coord_copies))
        )
        count.add_updater(
            lambda m: m.next_to(count_word[0][0], LEFT, aligned_edge=DOWN)
        )

        self.add(count_group)
        self.play(
            # ChangeDecimalToValue(count, len(coord_copies)),
            ShowIncreasingSubsets(coord_copies),
            run_time=1.5,
            rate_func=linear,
        )
        self.play(FadeOut(coord_copies))
