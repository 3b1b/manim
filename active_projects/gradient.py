from big_ol_pile_of_manim_imports import *


class GradientDescentWrapper(Scene):
    def construct(self):
        title = TextMobject("Gradient descent")
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()


class ShowSimpleMultivariableFunction(Scene):
    def construct(self):
        scale_val = 1.5

        func_tex = TexMobject(
            "C(", "x_1,", "x_2,", "\\dots,", "x_n", ")", "=",
        )
        func_tex.scale(scale_val)
        func_tex.shift(2 * LEFT)
        alt_func_tex = TexMobject(
            "C(", "x,", "y", ")", "="
        )
        alt_func_tex.scale(scale_val)
        for tex in func_tex, alt_func_tex:
            tex.set_color_by_tex_to_color_map({
                "C(": RED,
                ")": RED,
            })
        alt_func_tex.move_to(func_tex, RIGHT)
        inputs = func_tex[1:-2]
        self.add(func_tex)

        many_inputs = TexMobject(*[
            "x_{%d}, " % d for d in range(1, 25)
        ])
        many_inputs.scale_to_fit_width(FRAME_WIDTH)
        many_inputs.to_edge(UL)

        inputs_brace = Brace(inputs, UP)
        inputs_brace_text = inputs_brace.get_text("Multiple inputs")

        decimal = DecimalNumber(0)
        decimal.scale(scale_val)
        decimal.next_to(tex, RIGHT)
        value_tracker = ValueTracker(0)
        self.add(ContinualMovement(value_tracker, rate=0.5))
        decimal_change = ContinualChangingDecimal(
            decimal,
            lambda a: 1 + np.sin(value_tracker.get_value())
        )
        self.add(decimal_change)

        output_brace = Brace(decimal, DOWN)
        output_brace_text = output_brace.get_text("Single output")

        self.wait(2)
        self.play(GrowFromCenter(inputs_brace))
        self.play(Write(inputs_brace_text))
        self.play(GrowFromCenter(output_brace))
        self.play(Write(output_brace_text))
        self.wait(3)
        self.play(
            ReplacementTransform(
                inputs,
                many_inputs[:len(inputs)]
            ),
            LaggedStart(
                FadeIn,
                many_inputs[len(inputs):]
            ),
            FadeOut(inputs_brace),
            FadeOut(inputs_brace_text),
        )
        self.wait()
        self.play(
            ReplacementTransform(
                func_tex[0], alt_func_tex[0]
            ),
            Write(alt_func_tex[1:3]),
            LaggedStart(FadeOutAndShiftDown, many_inputs)
        )
        self.wait(3)


class ShowGraphWithVectors(ExternallyAnimatedScene):
    pass


class ShowFunction(Scene):
    def construct(self):
        func = TexMobject(
            "f(x, y) = e^{-x^2 + \\cos(2y)}",
            tex_to_color_map={
                "x": BLUE,
                "y": RED,
            }
        )
        func.scale(1.5)
        self.play(FadeInFromDown(func))
        self.wait()


class ShowExampleFunctionGraph(ExternallyAnimatedScene):
    pass


class ShowGradient(Scene):
    def construct(self):
        lhs = TexMobject(
            "\\nabla f(x, y)=",
            tex_to_color_map={"x": BLUE, "y": RED}
        )
        vector = Matrix([
            ["\\partial f / \\partial x"],
            ["\\partial f / \\partial y"],
        ], v_buff=1)
        gradient = VGroup(lhs, vector)
        gradient.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        gradient.scale(1.5)

        del_x, del_y = partials = vector.get_entries()
        background_rects = VGroup()
        for partial, color in zip(partials, [BLUE, RED]):
            partial[-1].set_color(color)
            partial.rect = SurroundingRectangle(
                partial, buff=MED_SMALL_BUFF
            )
            partial.rect.set_stroke(width=0)
            partial.rect.set_fill(color=color, opacity=0.5)
            background_rects.add(partial.rect.copy())
        background_rects.set_fill(opacity=0.1)

        partials.set_fill(opacity=0)

        self.play(
            LaggedStart(FadeIn, gradient),
            LaggedStart(
                FadeIn, background_rects,
                rate_func=squish_rate_func(smooth, 0.5, 1)
            )
        )
        self.wait()
        for partial in partials:
            self.play(DrawBorderThenFill(partial.rect))
            self.wait()
            self.play(FadeOut(partial.rect))
        self.wait()
        for partial in partials:
            self.play(Write(partial))
            self.wait()


class SliceGraphTwoWays(ExternallyAnimatedScene):
    pass


class TakePartialDerivatives(Scene):
    def construct(self):
        tex_to_color_map = {
            "x": BLUE,
            "y": RED,
        }
        func_tex = TexMobject(
            "f(x, y)", "=", "e^{", "-x^2 + \\cos(2y)}",
            tex_to_color_map=tex_to_color_map
        )
        partial_x = TexMobject(
            "{\\partial f \\over \\partial x}", "=",
            "\\left( e^{-x^2 + \\cos(2y)} \\right)",
            "(-2x)",
            tex_to_color_map=tex_to_color_map
        )
        partial_y = TexMobject(
            "{\\partial f \\over \\partial y}", "=",
            "\\left( e^{-x^2 + \\cos(2y)} \\right)",
            "(-\\sin(2y) \\cdot 2)",
            tex_to_color_map=tex_to_color_map
        )
        partials = VGroup(partial_x, partial_y)
        for mob in func_tex, partials:
            mob.scale(1.5)

        func_tex.move_to(2 * UP + LEFT)
        for partial in partials:
            partial.next_to(func_tex, DOWN, buff=LARGE_BUFF)
            top_eq_x = func_tex.get_part_by_tex("=").get_center()[0]
            low_eq_x = partial.get_part_by_tex("=").get_center()[0]
            partial.shift((top_eq_x - low_eq_x) * RIGHT)

        index = func_tex.index_of_part_by_tex("e^")
        exp_rect = SurroundingRectangle(func_tex[index + 1:], buff=0)
        exp_rect.set_stroke(width=0)
        exp_rect.set_fill(GREEN, opacity=0.5)

        xs = func_tex.get_parts_by_tex("x", substring=False)
        ys = func_tex.get_parts_by_tex("y", substring=False)
        for terms in xs, ys:
            terms.rects = VGroup(*[
                SurroundingRectangle(term, buff=0.5 * SMALL_BUFF)
                for term in terms
            ])
            terms.arrows = VGroup(*[
                Vector(0.5 * DOWN).next_to(rect, UP, SMALL_BUFF)
                for rect in terms.rects
            ])
        treat_as_constant

        self.add(func_tex, partial_x)
        self.add(exp_rect)
        self.add(xs.rects)
        self.add(ys.rects)
        self.add(xs.arrows)
        self.add(ys.arrows)

        # Start to show partial_x
        # Label y as constant
        # Perform partial_x derivative
        # Swap out partial_x for partial_y
        # Show same outer derivative
        # Finish y derivative


class ShowDerivativeAtExamplePoint(Scene):
    def construct(self):
        pass
