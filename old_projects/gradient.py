from manimlib.imports import *


# Warning, this file uses ContinualChangingDecimal,
# which has since been been deprecated.  Use a mobject
# updater instead


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
        many_inputs.set_width(FRAME_WIDTH)
        many_inputs.to_edge(UL)

        inputs_brace = Brace(inputs, UP)
        inputs_brace_text = inputs_brace.get_text("Multiple inputs")

        decimal = DecimalNumber(0)
        decimal.scale(scale_val)
        decimal.next_to(tex, RIGHT)
        value_tracker = ValueTracker(0)
        always_shift(value_tracker, rate=0.5)
        self.add(value_tracker)
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
            LaggedStartMap(
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
            LaggedStartMap(FadeOutAndShiftDown, many_inputs)
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
        gradient.arrange(RIGHT, buff=SMALL_BUFF)
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
            LaggedStartMap(FadeIn, gradient),
            LaggedStartMap(
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


class ExampleGraphHoldXConstant(ExternallyAnimatedScene):
    pass


class ExampleGraphHoldYConstant(ExternallyAnimatedScene):
    pass


class TakePartialDerivatives(Scene):
    def construct(self):
        tex_to_color_map = {
            "x": BLUE,
            "y": RED,
        }
        func_tex = TexMobject(
            "f", "(", "x", ",", "y", ")", "=",
            "e^{", "-x^2", "+ \\cos(2y)}",
            tex_to_color_map=tex_to_color_map
        )
        partial_x = TexMobject(
            "{\\partial", "f", "\\over", "\\partial", "x}", "=",
            "\\left(", "e^", "{-x^2", "+ \\cos(2y)}", "\\right)",
            "(", "-2", "x", ")",
            tex_to_color_map=tex_to_color_map,
        )
        partial_y = TexMobject(
            "{\\partial", "f", "\\over", "\\partial", "y}", "=",
            "\\left(", "e^", "{-x^2", "+ \\cos(", "2", "y)}", "\\right)",
            "(", "-\\sin(", "2", "y)", "\\cdot 2", ")",
            tex_to_color_map=tex_to_color_map,
        )
        partials = VGroup(partial_x, partial_y)
        for mob in func_tex, partials:
            mob.scale(1.5)

        func_tex.move_to(2 * UP + 3 * LEFT)
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
        treat_as_constant = TextMobject("Treat as a constant")
        treat_as_constant.next_to(ys.arrows[1], UP)

        # Start to show partial_x
        self.play(FadeInFromDown(func_tex))
        self.wait()
        self.play(
            ReplacementTransform(func_tex[0].copy(), partial_x[1]),
            Write(partial_x[0]),
            Write(partial_x[2:4]),
            Write(partial_x[6]),
        )
        self.play(
            ReplacementTransform(func_tex[2].copy(), partial_x[4])
        )
        self.wait()

        # Label y as constant
        self.play(LaggedStartMap(ShowCreation, ys.rects))
        self.play(
            LaggedStartMap(GrowArrow, ys.arrows, lag_ratio=0.8),
            Write(treat_as_constant)
        )
        self.wait(2)

        # Perform partial_x derivative
        self.play(FadeIn(exp_rect), Animation(func_tex))
        self.wait()
        pxi1 = 8
        pxi2 = 15
        self.play(
            ReplacementTransform(
                func_tex[7:].copy(),
                partial_x[pxi1:pxi2],
            ),
            FadeIn(partial_x[pxi1 - 1:pxi1]),
            FadeIn(partial_x[pxi2]),
        )
        self.wait(2)
        self.play(
            ReplacementTransform(
                partial_x[10:12].copy(),
                partial_x[pxi2 + 2:pxi2 + 4],
                path_arc=-(TAU / 4)
            ),
            FadeIn(partial_x[pxi2 + 1]),
            FadeIn(partial_x[-1]),
        )
        self.wait(2)

        # Swap out partial_x for partial_y
        self.play(
            FadeOutAndShiftDown(partial_x),
            FadeOut(ys.rects),
            FadeOut(ys.arrows),
            FadeOut(treat_as_constant),
            FadeOut(exp_rect),
            Animation(func_tex)
        )
        self.play(FadeInFromDown(partial_y[:7]))
        self.wait()

        treat_as_constant.next_to(xs.arrows[1], UP, SMALL_BUFF)
        self.play(
            LaggedStartMap(ShowCreation, xs.rects),
            LaggedStartMap(GrowArrow, xs.arrows),
            Write(treat_as_constant),
            lag_ratio=0.8
        )
        self.wait()

        # Show same outer derivative
        self.play(
            ReplacementTransform(
                func_tex[7:].copy(),
                partial_x[pxi1:pxi2],
            ),
            FadeIn(partial_x[pxi1 - 2:pxi1]),
            FadeIn(partial_x[pxi2]),
        )
        self.wait()
        self.play(
            ReplacementTransform(
                partial_y[12:16].copy(),
                partial_y[pxi2 + 3:pxi2 + 7],
                path_arc=-(TAU / 4)
            ),
            FadeIn(partial_y[pxi2 + 2]),
            FadeIn(partial_y[-1]),
        )
        self.wait()
        self.play(ReplacementTransform(
            partial_y[-5].copy(),
            partial_y[-2],
            path_arc=-PI
        ))
        self.wait()


class ShowDerivativeAtExamplePoint(Scene):
    def construct(self):
        tex_to_color_map = {
            "x": BLUE,
            "y": RED,
        }
        func_tex = TexMobject(
            "f", "(", "x", ",", "y", ")", "=",
            "e^{", "-x^2", "+ \\cos(2y)}",
            tex_to_color_map=tex_to_color_map
        )
        gradient_tex = TexMobject(
            "\\nabla", "f", "(", "x", ",", "y", ")", "=",
            tex_to_color_map=tex_to_color_map
        )

        partial_vect = Matrix([
            ["{\\partial f / \\partial x}"],
            ["{\\partial f / \\partial y}"],
        ])
        partial_vect.get_mob_matrix()[0, 0][-1].set_color(BLUE)
        partial_vect.get_mob_matrix()[1, 0][-1].set_color(RED)
        result_vector = self.get_result_vector("x", "y")

        gradient = VGroup(
            gradient_tex,
            partial_vect,
            TexMobject("="),
            result_vector
        )
        gradient.arrange(RIGHT, buff=SMALL_BUFF)

        func_tex.to_edge(UP)
        gradient.next_to(func_tex, DOWN, buff=LARGE_BUFF)

        example_lhs = TexMobject(
            "\\nabla", "f", "(", "1", ",", "3", ")", "=",
            tex_to_color_map={"1": BLUE, "3": RED},
        )
        example_result_vector = self.get_result_vector("1", "3")
        example_rhs = DecimalMatrix([[-1.92], [0.54]])
        example = VGroup(
            example_lhs,
            example_result_vector,
            TexMobject("="),
            example_rhs,
        )
        example.arrange(RIGHT, buff=SMALL_BUFF)
        example.next_to(gradient, DOWN, LARGE_BUFF)

        self.add(func_tex, gradient)
        self.wait()
        self.play(
            ReplacementTransform(gradient_tex.copy(), example_lhs),
            ReplacementTransform(result_vector.copy(), example_result_vector),
        )
        self.wait()
        self.play(Write(example[2:]))
        self.wait()

    def get_result_vector(self, x, y):
        result_vector = Matrix([
            ["e^{-%s^2 + \\cos(2\\cdot %s)} (-2\\cdot %s)" % (x, y, x)],
            ["e^{-%s^2 + \\cos(2\\cdot %s)} \\big(-\\sin(2\\cdot %s) \\cdot 2\\big)" % (x, y, y)],
        ], v_buff=1.2, element_alignment_corner=ORIGIN)

        x_terms = VGroup(
            result_vector.get_mob_matrix()[0, 0][2],
            result_vector.get_mob_matrix()[1, 0][2],
            result_vector.get_mob_matrix()[0, 0][-2],
        )
        y_terms = VGroup(
            result_vector.get_mob_matrix()[0, 0][11],
            result_vector.get_mob_matrix()[1, 0][11],
            result_vector.get_mob_matrix()[1, 0][-5],
        )
        x_terms.set_color(BLUE)
        y_terms.set_color(RED)
        return result_vector
