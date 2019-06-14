from manimlib.imports import *


class WriteHeatEquationTemplate(Scene):
    CONFIG = {
        "tex_mobject_config": {
            "tex_to_color_map": {
                "{T}": WHITE,
                "{t}": YELLOW,
                "{x}": GREEN,
                "{y}": RED,
                "{z}": BLUE,
                "\\partial": WHITE,
                "2": WHITE,
            },
        },
    }

    def get_d1_equation(self):
        return TexMobject(
            "{\\partial {T} \\over \\partial {t}}({x}, {t})", "=",
            "\\alpha \\cdot",
            "{\\partial^2 {T} \\over \\partial {x}^2} ({x}, {t})",
            **self.tex_mobject_config
        )

    def get_d1_equation_without_inputs(self):
        return TexMobject(
            "{\\partial {T} \\over \\partial {t}}", "=",
            "\\alpha \\cdot",
            "{\\partial^2 {T} \\over \\partial {x}^2}",
            **self.tex_mobject_config
        )

    def get_d3_equation(self):
        return TexMobject(
            "{\\partial {T} \\over \\partial {t}}", "=",
            "\\alpha \\left(",
            "{\\partial^2 {T} \\over \\partial {x}^2} + ",
            "{\\partial^2 {T} \\over \\partial {y}^2} + ",
            "{\\partial^2 {T} \\over \\partial {z}^2}",
            "\\right)",
            **self.tex_mobject_config
        )

    def get_general_equation(self):
        return TexMobject(
            "{\\partial {T} \\over \\partial {t}}", "=",
            "\\alpha", "\\nabla^2 {T}",
            **self.tex_mobject_config,
        )

    def get_d3_equation_with_inputs(self):
        return TexMobject(
            "{\\partial {T} \\over \\partial {t}}",
            "({x}, {y}, {z}, {t})", "=",
            "\\alpha \\left(",
            "{\\partial^2 {T} \\over \\partial {x}^2}",
            "({x}, {y}, {z}, {t}) + ",
            "{\\partial^2 {T} \\over \\partial {y}^2}",
            "({x}, {y}, {z}, {t}) + ",
            "{\\partial^2 {T} \\over \\partial {z}^2}",
            "({x}, {y}, {z}, {t})",
            "\\right)",
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


class HeatEquationIntroTitle(WriteHeatEquationTemplate):
    def construct(self):
        scale_factor = 1.25
        title = TextMobject("The Heat Equation")
        title.scale(scale_factor)
        title.to_edge(UP)

        equation = self.get_general_equation()
        equation.scale(scale_factor)
        equation.next_to(title, DOWN, MED_LARGE_BUFF)
        equation.set_color_by_tex("{T}", RED)

        self.play(
            FadeInFrom(title, DOWN),
            FadeInFrom(equation, UP),
        )
        self.wait()


class BringTogether(Scene):
    def construct(self):
        arrows = VGroup(Vector(2 * RIGHT), Vector(2 * LEFT))
        arrows.arrange(RIGHT, buff=2)
        words = TextMobject("Bring together")[0]
        words.next_to(arrows, DOWN)
        words.save_state()
        words.space_out_submobjects(1.2)

        self.play(
            VFadeIn(words),
            Restore(words),
            arrows.arrange, RIGHT, {"buff": SMALL_BUFF},
            VFadeIn(arrows),
        )
        self.play(FadeOut(words), FadeOut(arrows))


class FourierSeriesIntro(WriteHeatEquationTemplate):
    def construct(self):
        title_scale_value = 1.5

        title = TextMobject(
            "Fourier ", "Series",
        )
        title.scale(title_scale_value)
        title.to_edge(UP)
        title.generate_target()

        details_coming = TextMobject("Details coming...")
        details_coming.next_to(title.get_corner(DR), DOWN)
        details_coming.set_color(LIGHT_GREY)

        # physics = TextMobject("Physics")
        heat = TextMobject("Heat")
        heat.scale(title_scale_value)
        physics = self.get_general_equation()
        physics.set_color_by_tex("{T}", RED)
        arrow1 = Arrow(LEFT, RIGHT)
        arrow2 = Arrow(LEFT, RIGHT)
        group = VGroup(
            heat, arrow1, physics, arrow2, title.target
        )
        group.arrange(RIGHT)
        # physics.align_to(title.target, UP)
        group.to_edge(UP)

        rot_square = Square()
        rot_square.fade(1)
        rot_square.add_updater(lambda m, dt: m.rotate(dt))

        def update_heat_colors(heat):
            colors = [YELLOW, RED]
            vertices = rot_square.get_vertices()
            letters = heat.family_members_with_points()
            for letter, vertex in zip(letters, vertices):
                alpha = (normalize(vertex)[0] + 1) / 2
                i, sa = integer_interpolate(0, len(colors) - 1, alpha)
                letter.set_color(interpolate_color(
                    colors[i], colors[i + 1], alpha,
                ))
        heat.add_updater(update_heat_colors)

        image = ImageMobject("Joseph Fourier")
        image.set_height(5)
        image.next_to(title, DOWN, LARGE_BUFF)
        image.to_edge(LEFT)
        name = TextMobject("Joseph", "Fourier")
        name.next_to(image, DOWN)

        bubble = ThoughtBubble(
            height=2,
            width=2.5,
            direction=RIGHT,
        )
        bubble.set_fill(opacity=0)
        bubble.set_stroke(WHITE)
        bubble.set_stroke(BLACK, 5, background=True)
        bubble.shift(heat.get_center() - bubble.get_bubble_center())
        bubble[:-1].shift(LEFT + 0.2 * DOWN)
        bubble[:-1].rotate(-20 * DEGREES)
        for mob in bubble[:-1]:
            mob.rotate(20 * DEGREES)

        # self.play(FadeInFromDown(title))
        self.add(title)
        self.play(
            FadeInFromDown(image),
            TransformFromCopy(
                title.get_part_by_tex("Fourier"),
                name.get_part_by_tex("Fourier"),
                path_arc=90 * DEGREES,
            ),
            FadeIn(name.get_part_by_tex("Joseph")),
        )
        self.play(Write(details_coming, run_time=1))
        self.play(LaggedStartMap(FadeOut, details_coming[0], run_time=1))
        self.wait()
        self.add(rot_square)
        self.play(
            FadeInFrom(physics, RIGHT),
            GrowArrow(arrow2),
            FadeInFrom(heat, RIGHT),
            GrowArrow(arrow1),
            MoveToTarget(title),
        )
        self.play(ShowCreation(bubble))
        self.wait(10)


class CompareODEToPDE(Scene):
    def construct(self):
        pass


class TodaysTargetWrapper(Scene):
    def construct(self):
        pass


class TwoGraphTypeTitles(Scene):
    def construct(self):
        left_title = TextMobject(
            "Represent time\\\\with actual time"
        )
        left_title.shift(FRAME_WIDTH * LEFT / 4)
        right_title = TextMobject(
            "Represent time\\\\with an axis"
        )
        right_title.shift(FRAME_WIDTH * RIGHT / 4)

        titles = VGroup(left_title, right_title)
        for title in titles:
            title.scale(1.25)
            title.to_edge(UP)

        self.play(FadeInFromDown(right_title))
        self.wait()
        self.play(FadeInFromDown(left_title))
        self.wait()


class ShowPartialDerivativeSymbols(Scene):
    def construct(self):
        t2c = {
            "{x}": GREEN,
            "{t}": YELLOW,
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
                color=word[-1].get_color(),
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


class WriteHeatEquation(WriteHeatEquationTemplate):
    def construct(self):
        title = TextMobject("The Heat Equation")
        title.to_edge(UP)

        equation = self.get_d1_equation()
        equation.next_to(title, DOWN)

        eq_i = equation.index_of_part_by_tex("=")
        dt_part = equation[:eq_i]
        dx_part = equation[eq_i + 3:]
        dt_rect = SurroundingRectangle(dt_part)
        dt_rect.set_stroke(YELLOW, 2)
        dx_rect = SurroundingRectangle(dx_part)
        dx_rect.set_stroke(GREEN, 2)

        two_outlines = equation.get_parts_by_tex("2").copy()
        two_outlines.set_stroke(YELLOW, 2)
        two_outlines.set_fill(opacity=0)

        to_be_explained = TextMobject(
            "To be explained shortly..."
        )
        to_be_explained.scale(0.7)
        to_be_explained.next_to(equation, RIGHT, MED_LARGE_BUFF)
        to_be_explained.fade(1)

        pde = TextMobject("Partial Differential Equation")
        pde.move_to(title)

        del_outlines = equation.get_parts_by_tex("\\partial").copy()
        del_outlines.set_stroke(YELLOW, 2)
        del_outlines.set_fill(opacity=0)

        self.play(
            FadeInFrom(title, 0.5 * DOWN),
            FadeInFrom(equation, 0.5 * UP),
        )
        self.wait()
        self.play(ShowCreation(dt_rect))
        self.wait()
        self.play(TransformFromCopy(dt_rect, dx_rect))
        self.play(ShowCreationThenDestruction(two_outlines))
        self.wait()
        self.play(Write(to_be_explained, run_time=1))
        self.wait(2)
        self.play(
            ShowCreationThenDestruction(
                del_outlines,
                lag_ratio=0.1,
            )
        )
        self.play(
            FadeOutAndShift(title, UP),
            FadeInFrom(pde, DOWN),
            FadeOut(dt_rect),
            FadeOut(dx_rect),
        )
        self.wait()


class Show3DEquation(WriteHeatEquationTemplate):
    def construct(self):
        equation = self.get_d3_equation_with_inputs()
        equation.set_width(FRAME_WIDTH - 1)
        inputs = VGroup(*it.chain(*[
            equation.get_parts_by_tex(s)
            for s in ["{x}", "{y}", "{z}", "{t}"]
        ]))
        inputs.sort()
        equation.to_edge(UP)

        self.add(equation)
        self.play(LaggedStartMap(
            ShowCreationThenFadeAround, inputs,
            surrounding_rectangle_config={
                "buff": 0.05,
                "stroke_width": 2,
            }
        ))
        self.wait()


class Show1DAnd3DEquations(WriteHeatEquationTemplate):
    def construct(self):
        d1_group = self.get_d1_group()
        d3_group = self.get_d3_group()
        d1_words, d1_equation = d1_group
        d3_words, d3_equation = d3_group

        groups = VGroup(d1_group, d3_group)
        for group in groups:
            group.arrange(DOWN, buff=MED_LARGE_BUFF)
        groups.arrange(RIGHT, buff=1.5)
        groups.to_edge(UP)

        d3_rhs = d3_equation[9:-2]
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


class D1EquationNoInputs(WriteHeatEquationTemplate):
    def construct(self):
        equation = self.get_d1_equation_without_inputs()
        equation.to_edge(UP)
        # i1 = equation.index_of_part_by_tex("\\partial")
        # i2 = equation.index_of_part_by_tex("\\cdot")
        # equation[i1:i1 + 2].set_color(RED)
        # equation[i2 + 1:i2 + 6].set_color(RED)
        equation.set_color_by_tex("{T}", RED)
        self.add(equation)


class AltHeatRHS(Scene):
    def construct(self):
        formula = TexMobject(
            "{\\alpha \\over 2}", "\\Big(",
            "T({x} - 1, {t}) + T({x} + 1, {t})"
            "\\Big)",
            tex_to_color_map={
                "{x}": GREEN,
                "{t}": YELLOW,
            }
        )
        self.add(formula)


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


class ShowLaplacian(WriteHeatEquation):
    def construct(self):
        equation = self.get_d3_equation()
        equation.to_edge(UP, buff=MED_SMALL_BUFF)

        parts = VGroup()
        plusses = VGroup()
        for char in "xyz":
            index = equation.index_of_part_by_tex(
                "{" + char + "}"
            )
            part = equation[index - 6:index + 3]
            rect = SurroundingRectangle(part)
            rect.match_color(equation[index])
            parts.add(part)
            part.rect = rect
            if char in "yz":
                plus = equation[index - 8]
                part.plus = plus
                plusses.add(plus)

        lp = equation.get_part_by_tex("(")
        rp = equation.get_part_by_tex(")")

        for part in parts:
            part.rp = rp.copy()
            part.rp.next_to(part, RIGHT, SMALL_BUFF)
            part.rp.align_to(lp, UP)
        rp.become(parts[0].rp)

        # Show new second derivatives
        self.add(*equation)
        self.remove(*plusses, *parts[1], *parts[2])
        for part in parts[1:]:
            self.play(
                rp.become, part.rp,
                FadeInFrom(part, LEFT),
                Write(part.plus),
                ShowCreation(part.rect),
            )
            self.play(
                FadeOut(part.rect),
            )
            self.wait()

        # Show laplacian
        brace = Brace(parts, DOWN)
        laplacian = TexMobject("\\nabla^2", "T")
        laplacian.next_to(brace, DOWN)
        laplacian_name = TextMobject(
            "``Laplacian''"
        )
        laplacian_name.next_to(laplacian, DOWN)

        T_parts = VGroup(*[part[3] for part in parts])
        non_T_parts = VGroup(*[
            VGroup(*part[:3], *part[4:])
            for part in parts
        ])

        self.play(GrowFromCenter(brace))
        self.play(Write(laplacian_name))
        self.play(
            TransformFromCopy(non_T_parts, laplacian[0])
        )
        self.play(
            TransformFromCopy(T_parts, laplacian[1])
        )
        self.wait(3)


class AskAboutActuallySolving(WriteHeatEquationTemplate):
    def construct(self):
        equation = self.get_d1_equation()
        equation.center()

        q1 = TextMobject("Solve for T?")
        q1.next_to(equation, UP, LARGE_BUFF)
        q2 = TextMobject("What does it \\emph{mean} to solve this?")
        q2.next_to(equation, UP, LARGE_BUFF)
        formula = TexMobject(
            "T({x}, {t}) = \\sin\\big(a{x}\\big) e^{-\\alpha \\cdot a^2 {t}}",
            tex_to_color_map={
                "{x}": GREEN,
                "{t}": YELLOW,
            }
        )
        formula.next_to(equation, DOWN, LARGE_BUFF)
        q3 = TextMobject("Is this it?")
        arrow = Vector(LEFT, color=WHITE)
        arrow.next_to(formula, RIGHT)
        q3.next_to(arrow, RIGHT)

        self.add(equation)
        self.play(FadeInFromDown(q1))
        self.wait()
        self.play(
            FadeInFromDown(q2),
            q1.shift, 1.5 * UP,
        )
        self.play(FadeInFrom(formula, UP))
        self.play(
            GrowArrow(arrow),
            FadeInFrom(q3, LEFT)
        )
        self.wait()


class PDEPatreonEndscreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Vassili Philippov",
            "Burt Humburg",
            "Matt Russell",
            "Scott Gray",
            "soekul",
            "Tihan Seale",
            "Richard Barthel",
            "Ali Yahya",
            "dave nicponski",
            "Evan Phillips",
            "Graham",
            "Joseph Kelly",
            "Kaustuv DeBiswas",
            "LambdaLabs",
            "Lukas Biewald",
            "Mike Coleman",
            "Peter Mcinerney",
            "Quantopian",
            "Roy Larson",
            "Scott Walter, Ph.D.",
            "Yana Chernobilsky",
            "Yu Jun",
            "Jordan Scales",
            "D. Sivakumar",
            "Lukas -krtek.net- Novy",
            "John Shaughnessy",
            "Britt Selvitelle",
            "David Gow",
            "J",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Magnus Dahlström",
            "Randy C. Will",
            "Ryan Atallah",
            "Luc Ritchie",
            "1stViewMaths",
            "Adrian Robinson",
            "Alexis Olson",
            "Andreas Benjamin Brössel",
            "Andrew Busey",
            "Ankalagon",
            "Antoine Bruguier",
            "Antonio Juarez",
            "Arjun Chakroborty",
            "Art Ianuzzi",
            "Awoo",
            "Bernd Sing",
            "Boris Veselinovich",
            "Brian Staroselsky",
            "Chad Hurst",
            "Charles Southerland",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Cooper Jones",
            "Danger Dai",
            "Dave B",
            "Dave Kester",
            "David B. Hill",
            "David Clark",
            "DeathByShrimp",
            "Delton Ding",
            "eaglle",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Hitoshi Yamauchi",
            "Isaac Jeffrey Lee",
            "j eduardo perez",
            "Jacob Magnuson",
            "Jameel Syed",
            "Jason Hise",
            "Jeff Linse",
            "Jeff Straathof",
            "John Griffith",
            "John Haley",
            "John V Wertheim",
            "Jonathan Eppele",
            "Kai-Siang Ang",
            "Kanan Gill",
            "L0j1k",
            "Lee Beck",
            "Lee Redden",
            "Linh Tran",
            "Ludwig Schubert",
            "Magister Mugit",
            "Mark B Bahu",
            "Mark Heising",
            "Martin Price",
            "Mathias Jansson",
            "Matt Langford",
            "Matt Roveto",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Michael Faust",
            "Michael Hardel",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nero Li",
            "Nikita Lesnikov",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Peter Ehrnstrom",
            "RedAgent14",
            "rehmi post",
            "Richard Burgmann",
            "Richard Comish",
            "Ripta Pasay",
            "Rish Kundalia",
            "Robert Teed",
            "Roobie",
            "Ryan Williams",
            "Sachit Nagpal",
            "Solara570",
            "Stevie Metke",
            "Tal Einav",
            "Ted Suzman",
            "Thomas Tarler",
            "Tom Fleming",
            "Valeriy Skobelev",
            "Xavier Bernard",
            "Yavor Ivanov",
            "Yaw Etse",
            "YinYangBalance.Asia",
            "Zach Cardwell",
        ],
    }
