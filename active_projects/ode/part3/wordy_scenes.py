from manimlib.imports import *
from active_projects.ode.part2.wordy_scenes import *


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


class ThreeConstraints(WriteHeatEquationTemplate):
    def construct(self):
        self.cross_out_solving()
        self.show_three_conditions()

    def cross_out_solving(self):
        equation = self.get_d1_equation()
        words = TextMobject("Solve this equation")
        words.to_edge(UP)
        equation.next_to(words, DOWN)
        cross = Cross(words)

        self.add(words, equation)
        self.wait()
        self.play(ShowCreation(cross))
        self.wait()

        self.equation = equation
        self.to_remove = VGroup(words, cross)

    def show_three_conditions(self):
        equation = self.equation
        to_remove = self.to_remove

        title = TexMobject(
            "\\text{Constraints }"
            "T({x}, {t})"
            "\\text{ must satisfy:}",
            **self.tex_mobject_config
        )
        title.to_edge(UP)

        items = VGroup(
            TextMobject("1)", "The PDE"),
            TextMobject("2)", "Boundary condition"),
            TextMobject("3)", "Initial condition"),
        )
        items.scale(0.7)
        items.arrange(RIGHT, buff=LARGE_BUFF)
        items.set_width(FRAME_WIDTH - 2)
        items.next_to(title, DOWN, LARGE_BUFF)
        items[1].set_color(MAROON_B)
        items[2].set_color(RED)

        bc_paren = TextMobject("(Explained soon)")
        bc_paren.scale(0.7)
        bc_paren.next_to(items[1], DOWN)

        self.play(
            FadeInFromDown(title),
            FadeOutAndShift(to_remove, UP),
            equation.scale, 0.6,
            equation.next_to, items[0], DOWN,
            equation.shift_onto_screen,
            LaggedStartMap(FadeIn, [
                items[0],
                items[1][0],
                items[2][0],
            ])
        )
        self.wait()
        self.play(Write(items[1][1]))
        bc_paren.match_y(equation)
        self.play(FadeInFrom(bc_paren, UP))
        self.wait(2)
        self.play(Write(items[2][1]))
        self.wait(2)
