from big_ol_pile_of_manim_imports import *


class CompareODEToPDE(Scene):
    def construct(self):
        pass


class TodaysTargetWrapper(Scene):
    def construct(self):
        pass


class ShowPartialDerivativeSymbols(Scene):
    def construct(self):
        t2c = {
            "{x}": GREEN,
            "{t}": PINK,
        }
        d_derivs, del_derivs = VGroup(*[
            VGroup(*[
                TexMobject(
                    "{" + sym, "T", "\\over", sym, var + "}",
                    "(", "{x}", ",", "{t}", ")",
                ).set_color_by_tex_to_color_map(t2c)
                for var in ("{x}", "{t}")
            ])
            for sym in ("d", "\\partial")
        ])
        dTdx, dTdt = d_derivs
        delTdelx, delTdelx = del_derivs
        dels = VGroup(*it.chain(*[
            del_deriv.get_parts_by_tex("\\partial")
            for del_deriv in del_derivs
        ]))

        dTdx.to_edge(UP)
        self.play(FadeInFrom(dTdx, DOWN))
        self.wait()
        self.play(ShowCreationThenFadeAround(dTdx[3:5]))
        self.play(ShowCreationThenFadeAround(dTdx[:2]))
        self.wait()

        dTdt.move_to(dTdx)
        self.play(
            dTdx.next_to, dTdt, RIGHT, {"buff": 1.5},
            dTdx.set_opacity, 0.5,
            FadeInFromDown(dTdt)
        )
        self.wait()

        for m1, m2 in zip(d_derivs, del_derivs):
            m2.move_to(m1)

        pd_words = TextMobject("Partial derivatives")
        pd_words.next_to(del_derivs, DOWN, MED_LARGE_BUFF)

        self.play(
            Write(pd_words),
            dTdx.set_opacity, 1,
            run_time=1,
        )
        self.wait()
        self.play(
            ReplacementTransform(d_derivs, del_derivs)
        )
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeAround,
                dels,
                surrounding_rectangle_config={
                    "color": BLUE,
                    "buff": 0.5 * SMALL_BUFF,
                    "stroke_width": 2,
                }
            )
        )
        self.wait()

        num_words = VGroup(*[
            TextMobject(
                "Change in $T$\\\\caused by {}",
                "$\\partial$", "${}$".format(var),
                arg_separator="",
            ).set_color_by_tex_to_color_map(t2c)
            for var in ("{x}", "{t}")
        ])
        num_words.scale(0.8)
        for word, deriv in zip(num_words, del_derivs):
            num = deriv[:2]
            word.move_to(num, UP)
            word.to_edge(UP, buff=MED_SMALL_BUFF)
            deriv.rect = SurroundingRectangle(
                num,
                buff=SMALL_BUFF,
                stroke_width=2,
            )
            deriv.rect.mob = num
            deriv.rect.add_updater(lambda r: r.move_to(r.mob))

        self.play(
            Write(num_words[1]),
            VGroup(del_derivs, pd_words).shift, DOWN,
            ShowCreation(del_derivs[1].rect),
        )
        self.play(
            Write(num_words[0]),
            ShowCreation(del_derivs[0].rect),
        )
        self.wait()


class WriteHeatEquation(Scene):
    CONFIG = {
        "tex_mobject_config": {
            "tex_to_color_map": {
                "{T}": YELLOW,
                "{t}": WHITE,
                "{x}": GREEN,
                "{y}": RED,
                "{z}": BLUE,
            },
        },
    }

    def construct(self):
        d1_group = self.get_d1_group()
        d3_group = self.get_d3_group()
        d1_words, d1_equation = d1_group
        d3_words, d3_equation = d3_group

        groups = VGroup(d1_group, d3_group)
        for group in groups:
            group.arrange(DOWN, buff=MED_LARGE_BUFF)
        groups.arrange(RIGHT, buff=2)
        groups.to_edge(UP)

        d3_rhs = d3_equation[6:]
        d3_brace = Brace(d3_rhs, DOWN)
        nabla_words = TextMobject("Sometimes written as")
        nabla_words.match_width(d3_brace)
        nabla_words.next_to(d3_brace, DOWN)
        nabla_exp = TexMobject(
            "\\nabla^2 {T}",
            **self.tex_mobject_config,
        )
        nabla_exp.next_to(nabla_words, DOWN)
        # nabla_group = VGroup(nabla_words, nabla_exp)

        d1_group.save_state()
        d1_group.center().to_edge(UP)

        self.play(
            Write(d1_words),
            FadeInFrom(d1_equation, UP),
            run_time=1,
        )
        self.wait(2)
        self.play(
            Restore(d1_group),
            FadeInFrom(d3_group, LEFT)
        )
        self.wait()
        self.play(
            GrowFromCenter(d3_brace),
            Write(nabla_words),
            TransformFromCopy(d3_rhs, nabla_exp),
            run_time=1,
        )
        self.wait()

    def get_d1_equation(self):
        return TexMobject(
            "{\\partial {T} \\over \\partial {t}}({x}, {t})="
            "{\\partial^2 {T} \\over \\partial {x}^2} ({x}, {t})",
            **self.tex_mobject_config
        )

    def get_d3_equation(self):
        return TexMobject(
            "{\\partial {T} \\over \\partial {t}} = ",
            "{\\partial^2 {T} \\over \\partial {x}^2} + ",
            "{\\partial^2 {T} \\over \\partial {y}^2} + ",
            "{\\partial^2 {T} \\over \\partial {z}^2}",
            **self.tex_mobject_config
        )

    def get_d3_equation_with_inputs(self):
        return TexMobject(
            "{\\partial {T} \\over \\partial {t}} = ",
            "{\\partial^2 {T} \\over \\partial {x}^2}",
            "(x, y, z, t) + ",
            "{\\partial^2 {T} \\over \\partial {y}^2}",
            "(x, y, z, t) + ",
            "{\\partial^2 {T} \\over \\partial {z}^2}",
            "(x, y, z, t)",
            **self.tex_mobject_config
        )

    def get_d1_words(self):
        return TextMobject("Heat equation\\\\", "(1 dimension)")

    def get_d3_words(self):
        return TextMobject("Heat equation\\\\", "(3 dimensions)")

    def get_d1_group(self):
        group = VGroup(
            self.get_d1_words(),
            self.get_d1_equation(),
        )
        group.arrange(DOWN, buff=MED_LARGE_BUFF)
        return group

    def get_d3_group(self):
        group = VGroup(
            self.get_d3_words(),
            self.get_d3_equation(),
        )
        group.arrange(DOWN, buff=MED_LARGE_BUFF)
        return group


class CompareInputsOfGeneralCaseTo1D(WriteHeatEquation):
    def construct(self):
        three_d_expr, one_d_expr = [
            TexMobject(
                "{T}(" + inputs + ", {t})",
                **self.tex_mobject_config,
            )
            for inputs in ["{x}, {y}, {z}", "{x}"]
        ]
        for expr in three_d_expr, one_d_expr:
            expr.scale(2)
            expr.to_edge(UP)

        x, y, z = [
            three_d_expr.get_part_by_tex(letter)
            for letter in ["x", "y", "z"]
        ]

        self.play(FadeInFromDown(three_d_expr))
        self.play(LaggedStartMap(
            ShowCreationThenFadeAround,
            VGroup(x, y, z)
        ))
        self.wait()
        low = 3
        high = -3
        self.play(
            ReplacementTransform(three_d_expr[:low], one_d_expr[:low]),
            ReplacementTransform(three_d_expr[high:], one_d_expr[high:]),
            three_d_expr[low:high].scale, 0,
        )
        self.wait()
