from manimlib.imports import *

from active_projects.ode.part2.fourier_series import FourierOfTrebleClef


class FourierNameIntro(Scene):
    def construct(self):
        self.show_two_titles()
        self.transition_to_image()
        self.show_paper()

    def show_two_titles(self):
        lt = TextMobject("Fourier", "Series")
        rt = TextMobject("Fourier", "Transform")
        lt_variants = VGroup(
            TextMobject("Complex", "Fourier Series"),
            TextMobject("Discrete", "Fourier Series"),
        )
        rt_variants = VGroup(
            TextMobject("Discrete", "Fourier Transform"),
            TextMobject("Fast", "Fourier Transform"),
            TextMobject("Quantum", "Fourier Transform"),
        )

        titles = VGroup(lt, rt)
        titles.scale(1.5)
        for title, vect in (lt, LEFT), (rt, RIGHT):
            title.move_to(vect * FRAME_WIDTH / 4)
            title.to_edge(UP)

        for title, variants in (lt, lt_variants), (rt, rt_variants):
            title.save_state()
            title.target = title.copy()
            title.target.scale(1 / 1.5, about_edge=RIGHT)
            for variant in variants:
                variant.move_to(title.target, UR)
                variant[0].set_color(YELLOW)

        v_line = Line(UP, DOWN)
        v_line.set_height(FRAME_HEIGHT)
        v_line.set_stroke(WHITE, 2)

        self.play(
            FadeInFrom(lt, RIGHT),
            ShowCreation(v_line)
        )
        self.play(
            FadeInFrom(rt, LEFT),
        )
        # Edit in images of circle animations
        # and clips from FT video

        # for title, variants in (rt, rt_variants), (lt, lt_variants):
        for title, variants in [(rt, rt_variants)]:
            # Maybe do it for left variant, maybe not...
            self.play(
                MoveToTarget(title),
                FadeInFrom(variants[0][0], LEFT)
            )
            for v1, v2 in zip(variants, variants[1:]):
                self.play(
                    FadeOutAndShift(v1[0], UP),
                    FadeInFrom(v2[0], DOWN),
                    run_time=0.5,
                )
                self.wait(0.5)
            self.play(
                Restore(title),
                FadeOut(variants[-1][0])
            )
        self.wait()

        self.titles = titles
        self.v_line = v_line

    def transition_to_image(self):
        titles = self.titles
        v_line = self.v_line

        image = ImageMobject("Joseph Fourier")
        image.set_height(5)
        image.to_edge(LEFT)

        frame = Rectangle()
        frame.replace(image, stretch=True)

        name = TextMobject("Joseph", "Fourier")
        fourier_part = name.get_part_by_tex("Fourier")
        fourier_part.set_color(YELLOW)
        F_sym = fourier_part[0]
        name.match_width(image)
        name.next_to(image, DOWN)

        self.play(
            ReplacementTransform(v_line, frame),
            FadeIn(image),
            FadeIn(name[0]),
            *[
                ReplacementTransform(
                    title[0].deepcopy(),
                    name[1]
                )
                for title in titles
            ],
            titles.scale, 0.65,
            titles.arrange, DOWN,
            titles.next_to, image, UP,
        )
        self.wait()

        big_F = F_sym.copy()
        big_F.set_fill(opacity=0)
        big_F.set_stroke(WHITE, 2)
        big_F.set_height(3)
        big_F.move_to(midpoint(
            image.get_right(),
            RIGHT_SIDE,
        ))
        big_F.shift(DOWN)
        equivalence = VGroup(
            fourier_part.copy().scale(1.25),
            TexMobject("\\Leftrightarrow").scale(1.5),
            TextMobject("Break down into\\\\pure frequencies"),
        )
        equivalence.arrange(RIGHT)
        equivalence.move_to(big_F)
        equivalence.to_edge(UP)

        self.play(
            FadeIn(big_F),
            TransformFromCopy(fourier_part, equivalence[0]),
            Write(equivalence[1:]),
        )
        self.wait(3)
        self.play(FadeOut(VGroup(big_F, equivalence)))

        self.image = image
        self.name = name

    def show_paper(self):
        image = self.image
        paper = ImageMobject("Fourier paper")
        paper.match_height(image)
        paper.next_to(image, RIGHT, MED_LARGE_BUFF)

        date = TexMobject("1822")
        date.next_to(paper, DOWN)
        date_rect = SurroundingRectangle(date)
        date_rect.scale(0.3)
        date_rect.set_color(RED)
        date_rect.shift(1.37 * UP + 0.08 * LEFT)
        date_arrow = Arrow(
            date_rect.get_bottom(),
            date.get_top(),
            buff=SMALL_BUFF,
            color=date_rect.get_color(),
        )

        heat_rect = SurroundingRectangle(
            TextMobject("CHALEUR")
        )
        heat_rect.set_color(RED)
        heat_rect.scale(0.6)
        heat_rect.move_to(
            paper.get_top() +
            1.22 * DOWN + 0.37 * RIGHT
        )
        heat_word = TextMobject("Heat")
        heat_word.scale(1.5)
        heat_word.next_to(paper, UP)
        heat_word.shift(paper.get_width() * RIGHT)
        heat_arrow = Arrow(
            heat_rect.get_top(),
            heat_word.get_left(),
            buff=0.1,
            path_arc=-60 * DEGREES,
            color=heat_rect.get_color(),
        )

        self.play(FadeInFrom(paper, LEFT))
        self.play(
            ShowCreation(date_rect),
        )
        self.play(
            GrowFromPoint(date, date_arrow.get_start()),
            ShowCreation(date_arrow),
        )
        self.wait(3)

        # Insert animation of circles/sine waves
        # approximating a square wave

        self.play(
            ShowCreation(heat_rect),
        )
        self.play(
            GrowFromPoint(heat_word, heat_arrow.get_start()),
            ShowCreation(heat_arrow),
        )
        self.wait(3)


class FourierSeriesIllustraiton(Scene):
    CONFIG = {
        "n_range": range(1, 31, 2),
    }

    def construct(self):
        n_range = self.n_range

        axes1 = Axes(
            number_line_config={
                "include_tip": False,
            },
            x_axis_config={
                "tick_frequency": 1 / 4,
                "unit_size": 4,
            },
            x_min=0,
            x_max=1,
            y_min=-1,
            y_max=1,
        )
        axes2 = axes1.copy()
        step_func = axes2.get_graph(
            lambda x: (1 if x < 0.5 else -1),
            discontinuities=[0.5],
            color=YELLOW,
            stroke_width=3,
        )
        dot = Dot(axes2.c2p(0.5, 0), color=step_func.get_color())
        dot.scale(0.5)
        step_func.add(dot)
        axes2.add(step_func)

        arrow = Arrow(LEFT, RIGHT, color=WHITE)
        VGroup(axes1, arrow, axes2).arrange(RIGHT).shift(UP)

        def generate_nth_func(n):
            return lambda x: (4 / n / PI) * np.sin(TAU * n * x)

        def generate_kth_partial_sum_func(k):
            return lambda x: np.sum([
                generate_nth_func(n)(x)
                for n in n_range[:k]
            ])

        sine_graphs = VGroup(*[
            axes1.get_graph(generate_nth_func(n))
            for n in n_range
        ])
        sine_graphs.set_stroke(width=3)
        sine_graphs.set_color_by_gradient(
            BLUE, GREEN, RED, YELLOW, PINK,
            BLUE, GREEN, RED, YELLOW, PINK,
        )

        partial_sums = VGroup(*[
            axes1.get_graph(generate_kth_partial_sum_func(k + 1))
            for k in range(len(n_range))
        ])
        partial_sums.match_style(sine_graphs)

        sum_tex = TexMobject(
            "\\frac{4}{\\pi}"
            "\\sum_{1, 3, 5, \\dots}"
            "\\frac{1}{n} \\sin(2\\pi \\cdot n \\cdot x)"
        )
        sum_tex.next_to(partial_sums, DOWN, buff=0.7)
        eq = TexMobject("=")
        step_tex = TexMobject(
            """
            1 \\quad \\text{if $x < 0.5$} \\\\
            0 \\quad \\text{if $x = 0.5$} \\\\
            -1 \\quad \\text{if $x > 0.5$} \\\\
            """
        )
        lb = Brace(step_tex, LEFT, buff=SMALL_BUFF)
        step_tex.add(lb)
        step_tex.next_to(axes2, DOWN, buff=MED_LARGE_BUFF)
        eq.move_to(midpoint(
            step_tex.get_left(),
            sum_tex.get_right()
        ))

        rects = it.chain(
            [
                SurroundingRectangle(sum_tex[0][i])
                for i in [4, 6, 8]
            ],
            it.cycle([None])
        )

        self.add(axes1, arrow, axes2)
        self.add(step_func)
        self.add(sum_tex, eq, step_tex)

        curr_partial_sum = axes1.get_graph(lambda x: 0)
        curr_partial_sum.set_stroke(width=1)
        for sine_graph, partial_sum, rect in zip(sine_graphs, partial_sums, rects):
            anims1 = [
                ShowCreation(sine_graph)
            ]
            partial_sum.set_stroke(BLACK, 4, background=True)
            anims2 = [
                curr_partial_sum.set_stroke,
                {"width": 1, "opacity": 0.5},
                curr_partial_sum.set_stroke,
                {"width": 0, "background": True},
                ReplacementTransform(
                    sine_graph, partial_sum,
                    remover=True
                ),
            ]
            if rect:
                rect.match_style(sine_graph)
                anims1.append(ShowCreation(rect))
                anims2.append(FadeOut(rect))
            self.play(*anims1)
            self.play(*anims2)
            curr_partial_sum = partial_sum


class CircleAnimationOfF(FourierOfTrebleClef):
    CONFIG = {
        "height": 3,
        "n_circles": 200,
        "run_time": 10,
        "arrow_config": {
            "tip_length": 0.1,
            "stroke_width": 2,
        }
    }

    def get_shape(self):
        path = VMobject()
        shape = TexMobject("F")
        for sp in shape.family_members_with_points():
            path.append_points(sp.points)
        return path


class LastChapterWrapper(Scene):
    def construct(self):
        full_rect = FullScreenFadeRectangle(
            fill_color=DARK_GREY,
            fill_opacity=1,
        )
        rect = ScreenRectangle(height=6)
        rect.set_stroke(WHITE, 2)
        rect.set_fill(BLACK, 1)
        title = TextMobject("Last chapter")
        title.scale(2)
        title.to_edge(UP)
        rect.next_to(title, DOWN)

        self.add(full_rect)
        self.play(
            FadeIn(rect),
            Write(title, run_time=2),
        )
        self.wait()


class ThreeMainObservations(Scene):
    def construct(self):
        fourier = ImageMobject("Joseph Fourier")
        fourier.set_height(5)
        fourier.to_corner(DR)
        fourier.shift(LEFT)
        bubble = ThoughtBubble(
            direction=RIGHT,
            height=3,
            width=4,
        )
        bubble.move_tip_to(fourier.get_corner(UL) + 0.5 * DR)

        observations = VGroup(
            TextMobject(
                "1)",
                # "Sine waves",
                # "H",
                # "Heat equation",
            ),
            TextMobject(
                "2)",
                # "Linearity"
            ),
            TextMobject(
                "3)",
                # "Any$^{*}$ function is\\\\",
                # "a sum of sine waves",
            ),
        )
        # heart = SuitSymbol("hearts")
        # heart.replace(observations[0][2])
        # observations[0][2].become(heart)
        # observations[0][1].add(happiness)
        # observations[2][2].align_to(
        #     observations[2][1], LEFT,
        # )

        observations.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=LARGE_BUFF,
        )
        observations.set_height(FRAME_HEIGHT - 2)
        observations.to_corner(UL, buff=LARGE_BUFF)

        self.add(fourier)
        self.play(ShowCreation(bubble))
        self.wait()
        self.play(LaggedStart(*[
            TransformFromCopy(bubble, observation)
            for observation in observations
        ], lag_ratio=0.2))
        self.play(
            FadeOut(fourier),
            FadeOut(bubble),
        )
        self.wait()


class NewSceneName(Scene):
    def construct(self):
        pass
