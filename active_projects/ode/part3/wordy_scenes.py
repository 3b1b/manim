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


class EquationAboveSineAnalysis(WriteHeatEquationTemplate):
    def construct(self):
        equation = self.get_d1_equation()
        equation.to_edge(UP)
        equation.shift(2 * LEFT)
        eq_index = equation.index_of_part_by_tex("=")
        lhs = equation[:eq_index]
        eq = equation[eq_index]
        rhs = equation[eq_index + 1:]
        t_terms = equation.get_parts_by_tex("{t}")[1:]
        t_terms.save_state()
        zeros = VGroup(*[
            TexMobject("0").replace(t, dim_to_match=1)
            for t in t_terms
        ])
        zeros.align_to(t_terms, DOWN)
        new_rhs = TexMobject(
            "=", "-\\alpha \\cdot {T}", "({x}, 0)",
            **self.tex_mobject_config
        )
        # new_rhs.move_to(equation.get_right())
        # new_rhs.next_to(equation, DOWN, MED_LARGE_BUFF)
        # new_rhs.align_to(eq, LEFT)
        new_rhs.next_to(equation, RIGHT)
        new_rhs.shift(SMALL_BUFF * DOWN)

        self.add(equation)
        self.play(ShowCreationThenFadeAround(rhs))
        self.wait()
        self.play(
            FadeOutAndShift(t_terms, UP),
            FadeInFrom(zeros, DOWN),
        )
        t_terms.fade(1)
        self.wait()
        self.play(
            # VGroup(equation, zeros).next_to,
            # new_rhs, LEFT,
            FadeIn(new_rhs),
        )
        self.wait()
        self.play(
            VGroup(
                lhs[6:],
                eq,
                rhs,
                new_rhs[0],
                new_rhs[-3:],
                zeros,
            ).fade, 0.5,
        )
        self.play(ShowCreationThenFadeAround(lhs[:6]))
        self.play(ShowCreationThenFadeAround(new_rhs[1:-3]))
        self.wait()


class ShowSinExpDerivatives(WriteHeatEquationTemplate):
    CONFIG = {
        "tex_mobject_config": {
            "tex_to_color_map": {
                "{0}": WHITE,
                "\\partial": WHITE,
                "=": WHITE,
            }
        }
    }

    def construct(self):
        pde = self.get_d1_equation_without_inputs()
        pde.to_edge(UP)
        pde.generate_target()

        new_rhs = TexMobject(
            "=- \\alpha \\cdot T",
            **self.tex_mobject_config,
        )
        new_rhs.next_to(pde, RIGHT)
        new_rhs.align_to(pde.get_part_by_tex("alpha"), DOWN)

        equation1 = TexMobject(
            "T({x}, {0}) = \\sin\\left({x}\\right)",
            **self.tex_mobject_config
        )
        equation2 = TexMobject(
            "T({x}, {t}) = \\sin\\left({x}\\right)",
            "e^{-\\alpha{t}}",
            **self.tex_mobject_config
        )
        for eq in equation1, equation2:
            eq.next_to(pde, DOWN, MED_LARGE_BUFF)

        eq2_part1 = equation2[:len(equation1)]
        eq2_part2 = equation2[len(equation1):]

        # Rectangles
        exp_rect = SurroundingRectangle(eq2_part2)
        exp_rect.set_stroke(RED, 3)
        sin_rect = SurroundingRectangle(
            eq2_part1[-3:]
        )
        sin_rect.set_color(BLUE)

        VGroup(pde.target, new_rhs).center().to_edge(UP)

        # Show proposed solution
        self.add(pde)
        self.add(equation1)
        self.wait()
        self.play(
            MoveToTarget(pde),
            FadeInFrom(new_rhs, LEFT)
        )
        self.wait()
        self.play(
            ReplacementTransform(equation1, eq2_part1),
            FadeIn(eq2_part2),
        )
        self.play(ShowCreation(exp_rect))
        self.wait()
        self.play(FadeOut(exp_rect))

        # Take partial derivatives wrt x
        q_mark = TexMobject("?")
        q_mark.next_to(pde.get_part_by_tex("="), UP)
        q_mark.set_color(RED)

        arrow1 = Vector(3 * DOWN + 1 * RIGHT, color=WHITE)
        arrow1.scale(1.2 / arrow1.get_length())
        arrow1.next_to(
            eq2_part2.get_corner(DL),
            DOWN, MED_LARGE_BUFF
        )
        ddx_label1 = TexMobject(
            "\\partial \\over \\partial {x}",
            **self.tex_mobject_config,
        )
        ddx_label1.scale(0.7)
        ddx_label1.next_to(
            arrow1.point_from_proportion(0.8),
            UR, SMALL_BUFF
        )

        pde_ddx = VGroup(
            *pde.get_parts_by_tex("\\partial")[2:],
            pde.get_parts_by_tex("\\over")[1],
            pde.get_part_by_tex("{x}"),
        )
        pde_ddx_rect = SurroundingRectangle(pde_ddx)
        pde_ddx_rect.set_color(GREEN)

        eq2_part2_rect = SurroundingRectangle(eq2_part2)

        dx = TexMobject(
            "\\cos\\left({x}\\right)", "e^{-\\alpha {t}}",
            **self.tex_mobject_config
        )
        ddx = TexMobject(
            "-\\sin\\left({x}\\right)", "e^{-\\alpha {t}}",
            **self.tex_mobject_config
        )
        dx.next_to(arrow1, DOWN)
        dx.align_to(eq2_part2, RIGHT)
        x_shift = arrow1.get_end()[0] - arrow1.get_start()[0]
        x_shift *= 2
        dx.shift(x_shift * RIGHT)
        arrow2 = arrow1.copy()
        arrow2.next_to(dx, DOWN)
        arrow2.shift(MED_SMALL_BUFF * RIGHT)
        dx_arrows = VGroup(arrow1, arrow2)

        ddx_label2 = ddx_label1.copy()
        ddx_label2.shift(
            arrow2.get_center() - arrow1.get_center()
        )
        ddx.next_to(arrow2, DOWN)
        ddx.align_to(eq2_part2, RIGHT)
        ddx.shift(2 * x_shift * RIGHT)

        rhs = equation2[-6:]

        self.play(
            FadeInFromDown(q_mark)
        )
        self.play(
            ShowCreation(pde_ddx_rect)
        )
        self.wait()
        self.play(
            LaggedStart(
                GrowArrow(arrow1),
                GrowArrow(arrow2),
            ),
            TransformFromCopy(
                pde_ddx[0], ddx_label1
            ),
            TransformFromCopy(
                pde_ddx[0], ddx_label2
            ),
        )
        self.wait()
        self.play(
            TransformFromCopy(rhs, dx)
        )
        self.wait()
        self.play(
            FadeIn(eq2_part2_rect)
        )
        self.play(
            Transform(
                eq2_part2_rect,
                SurroundingRectangle(dx[-3:])
            )
        )
        self.play(
            FadeOut(eq2_part2_rect)
        )
        self.wait()
        self.play(
            TransformFromCopy(dx, ddx)
        )
        self.play(
            FadeIn(
                SurroundingRectangle(ddx).match_style(
                    pde_ddx_rect
                )
            )
        )
        self.wait()

        # Take partial derivative wrt t
        pde_ddt = pde[:pde.index_of_part_by_tex("=") - 1]
        pde_ddt_rect = SurroundingRectangle(pde_ddt)

        dt_arrow = Arrow(
            arrow1.get_start(),
            arrow2.get_end() + RIGHT,
            buff=0
        )
        dt_arrow.flip(UP)
        dt_arrow.next_to(dx_arrows, LEFT, MED_LARGE_BUFF)

        dt_label = TexMobject(
            "\\partial \\over \\partial {t}",
            **self.tex_mobject_config,
        )
        dt_label.scale(1)
        dt_label.next_to(
            dt_arrow.get_center(), UL,
            SMALL_BUFF,
        )

        rhs_copy = rhs.copy()
        rhs_copy.next_to(dt_arrow.get_end(), DOWN)
        rhs_copy.shift(MED_LARGE_BUFF * LEFT)
        rhs_copy.match_y(ddx)

        minus_alpha_in_exp = rhs_copy[-3][1:].copy()
        minus_alpha_in_exp.set_color(RED)
        minus_alpha = TexMobject("-\\alpha")
        minus_alpha.next_to(rhs_copy, LEFT)
        minus_alpha.align_to(rhs_copy[0][0], DOWN)
        dot = TexMobject("\\cdot")
        dot.move_to(midpoint(
            minus_alpha.get_right(),
            rhs_copy.get_left(),
        ))

        self.play(
            TransformFromCopy(
                pde_ddx_rect,
                pde_ddt_rect,
            )
        )
        self.play(
            GrowArrow(dt_arrow),
            TransformFromCopy(
                pde_ddt,
                dt_label,
            )
        )
        self.wait()
        self.play(TransformFromCopy(rhs, rhs_copy))
        self.play(FadeIn(minus_alpha_in_exp))
        self.play(
            ApplyMethod(
                minus_alpha_in_exp.replace, minus_alpha,
                path_arc=TAU / 4
            ),
            FadeIn(dot),
        )
        self.play(
            FadeIn(minus_alpha),
            FadeOut(minus_alpha_in_exp),
        )
        self.wait()
        rhs_copy.add(minus_alpha, dot)
        self.play(
            FadeIn(SurroundingRectangle(rhs_copy))
        )
        self.wait()

        #
        checkmark = TexMobject("\\checkmark")
        checkmark.set_color(GREEN)
        checkmark.move_to(q_mark, DOWN)
        self.play(
            FadeInFromDown(checkmark),
            FadeOutAndShift(q_mark, UP)
        )
        self.wait()
