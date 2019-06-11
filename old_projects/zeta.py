
from manimlib.imports import *

import mpmath
mpmath.mp.dps = 7


def zeta(z):
    max_norm = FRAME_X_RADIUS
    try:
        return np.complex(mpmath.zeta(z))
    except:
        return np.complex(max_norm, 0)

def d_zeta(z):
    epsilon = 0.01
    return (zeta(z + epsilon) - zeta(z))/epsilon

class ZetaTransformationScene(ComplexTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
        "min_added_anchors" : 10,
        "max_added_anchors" : 300,
        "num_anchors_to_add_per_line" : 75,
        "post_transformation_stroke_width" : 2,
        "default_apply_complex_function_kwargs" : {
            "run_time" : 5,
        },
        "x_min" : 1,
        "x_max" : int(FRAME_X_RADIUS+2),
        "extra_lines_x_min" : -2,
        "extra_lines_x_max" : 4,
        "extra_lines_y_min" : -2,
        "extra_lines_y_max" : 2,
    }
    def prepare_for_transformation(self, mob):
        for line in mob.family_members_with_points():
            #Find point of line cloest to 1 on C
            if not isinstance(line, Line):
                line.insert_n_curves(self.min_added_anchors)
                continue
            p1 = line.get_start()+LEFT
            p2 = line.get_end()+LEFT
            t = (-np.dot(p1, p2-p1))/(get_norm(p2-p1)**2)
            closest_to_one = interpolate(
                line.get_start(), line.get_end(), t
            )
            #See how big this line will become
            diameter = abs(zeta(complex(*closest_to_one[:2])))
            target_num_curves = np.clip(
                int(self.anchor_density*np.pi*diameter),
                self.min_added_anchors,
                self.max_added_anchors,
            )
            num_curves = line.get_num_curves()
            if num_curves < target_num_curves:
                line.insert_n_curves(target_num_curves-num_curves)
            line.make_smooth()

    def add_extra_plane_lines_for_zeta(self, animate = False, **kwargs):
        dense_grid = self.get_dense_grid(**kwargs)
        if animate:
            self.play(ShowCreation(dense_grid))
        self.plane.add(dense_grid)
        self.add(self.plane)

    def get_dense_grid(self, step_size = 1./16):
        epsilon = 0.1
        x_range = np.arange(
            max(self.x_min, self.extra_lines_x_min),
            min(self.x_max, self.extra_lines_x_max),
            step_size
        )
        y_range = np.arange(
            max(self.y_min, self.extra_lines_y_min),
            min(self.y_max, self.extra_lines_y_max),
            step_size
        )
        vert_lines = VGroup(*[
            Line(
                self.y_min*UP,
                self.y_max*UP,
            ).shift(x*RIGHT)
            for x in x_range
            if abs(x-1) > epsilon
        ])
        vert_lines.set_color_by_gradient(
            self.vert_start_color, self.vert_end_color
        )
        horiz_lines = VGroup(*[
            Line(
                self.x_min*RIGHT,
                self.x_max*RIGHT,
            ).shift(y*UP)
            for y in y_range
            if abs(y) > epsilon
        ])
        horiz_lines.set_color_by_gradient(
            self.horiz_start_color, self.horiz_end_color
        )
        dense_grid = VGroup(horiz_lines, vert_lines)
        dense_grid.set_stroke(width = 1)
        return dense_grid

    def add_reflected_plane(self, animate = False):
        reflected_plane = self.get_reflected_plane()
        if animate:
            self.play(ShowCreation(reflected_plane, run_time = 5))
        self.plane.add(reflected_plane)
        self.add(self.plane)

    def get_reflected_plane(self):
        reflected_plane = self.plane.copy()
        reflected_plane.rotate(np.pi, UP, about_point = RIGHT)
        for mob in reflected_plane.family_members_with_points():
            mob.set_color(
                Color(rgb = 1-0.5*color_to_rgb(mob.get_color()))
            )
        self.prepare_for_transformation(reflected_plane)
        reflected_plane.submobjects = list(reversed(
            reflected_plane.family_members_with_points()
        ))
        return reflected_plane

    def apply_zeta_function(self, **kwargs):
        transform_kwargs = dict(self.default_apply_complex_function_kwargs)
        transform_kwargs.update(kwargs)
        self.apply_complex_function(zeta, **kwargs)

class TestZetaOnHalfPlane(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 15,
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.prepare_for_transformation(self.plane)
        print(sum([
            mob.get_num_points()
            for mob in self.plane.family_members_with_points()
        ]))
        print(len(self.plane.family_members_with_points()))
        self.apply_zeta_function()
        self.wait()

class TestZetaOnFullPlane(ZetaTransformationScene):
    def construct(self):
        self.add_transformable_plane(animate = True)
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.add_reflected_plane(animate = True)
        self.apply_zeta_function()


class TestZetaOnLine(ZetaTransformationScene):
    def construct(self):
        line = Line(UP+20*LEFT, UP+20*RIGHT)
        self.add_transformable_plane()
        self.plane.submobjects = [line]
        self.apply_zeta_function()
        self.wait(2)
        self.play(ShowCreation(line, run_time = 10))
        self.wait(3)

######################

class IntroduceZeta(ZetaTransformationScene):
    CONFIG = {
        "default_apply_complex_function_kwargs" : {
            "run_time" : 8,
        }
    }
    def construct(self):
        title = TextMobject("Riemann zeta function")
        title.add_background_rectangle()
        title.to_corner(UP+LEFT)
        func_mob = VGroup(
            TexMobject("\\zeta(s) = "),
            TexMobject("\\sum_{n=1}^\\infty \\frac{1}{n^s}")
        )
        func_mob.arrange(RIGHT, buff = 0)
        for submob in func_mob:
            submob.add_background_rectangle()
        func_mob.next_to(title, DOWN)

        randy = Randolph().flip()
        randy.to_corner(DOWN+RIGHT)

        self.add_foreground_mobjects(title, func_mob)
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.play(ShowCreation(self.plane, run_time = 2))
        reflected_plane = self.get_reflected_plane()
        self.play(ShowCreation(reflected_plane, run_time = 2))
        self.plane.add(reflected_plane)
        self.wait()
        self.apply_zeta_function()
        self.wait(2)
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, func_mob,
        )
        self.play(Blink(randy))
        self.wait()

class WhyPeopleMayKnowIt(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Riemann zeta function")
        title.to_corner(UP+LEFT)
        func_mob = TexMobject(
            "\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}"
        )
        func_mob.next_to(title, DOWN, aligned_edge = LEFT)
        self.add(title, func_mob)

        mercenary_thought = VGroup(
            TexMobject("\\$1{,}000{,}000").set_color_by_gradient(GREEN_B, GREEN_D),
            TexMobject("\\zeta(s) = 0")
        )
        mercenary_thought.arrange(DOWN)
        divergent_sum = VGroup(
            TexMobject("1+2+3+4+\\cdots = -\\frac{1}{12}"),
            TexMobject("\\zeta(-1) = -\\frac{1}{12}")
        )
        divergent_sum.arrange(DOWN)
        divergent_sum[0].set_color_by_gradient(YELLOW, MAROON_B)
        divergent_sum[1].set_color(BLACK)

        #Thoughts
        self.play(*it.chain(*[
            [pi.change_mode, "pondering", pi.look_at, func_mob]
            for pi in self.get_pi_creatures()
        ]))
        self.random_blink()
        self.student_thinks(
            mercenary_thought, student_index = 2,
            target_mode = "surprised",
        )
        student = self.get_students()[2]
        self.random_blink()
        self.wait(2)
        self.student_thinks(
            divergent_sum, student_index = 1,
            added_anims = [student.change_mode, "plain"]
        )
        student = self.get_students()[1]
        self.play(
            student.change_mode, "confused",
            student.look_at, divergent_sum,
        )
        self.random_blink()
        self.play(*it.chain(*[
            [pi.change_mode, "confused", pi.look_at, divergent_sum]
            for pi in self.get_pi_creatures()
        ]))
        self.wait()
        self.random_blink()
        divergent_sum[1].set_color(WHITE)
        self.play(Write(divergent_sum[1]))
        self.random_blink()
        self.wait()

        #Ask about continuation
        self.student_says(
            TextMobject("Can you explain \\\\" , "``analytic continuation''?"),
            student_index = 1,
            target_mode = "raise_right_hand"
        )
        self.change_student_modes(
            "raise_left_hand",
            "raise_right_hand",
            "raise_left_hand",
        )
        self.play(
            self.get_teacher().change_mode, "happy",
            self.get_teacher().look_at, student.eyes,
        )
        self.random_blink()
        self.wait(2)
        self.random_blink()
        self.wait()

class ComplexValuedFunctions(ComplexTransformationScene):
    def construct(self):
        title = TextMobject("Complex-valued function")
        title.scale(1.5)
        title.add_background_rectangle()
        title.to_edge(UP)
        self.add(title)

        z_in = Dot(UP+RIGHT, color = YELLOW)
        z_out = Dot(4*RIGHT + 2*UP, color = MAROON_B)
        arrow = Arrow(z_in, z_out, buff = 0.1)
        arrow.set_color(WHITE)
        z = TexMobject("z").next_to(z_in, DOWN+LEFT, buff = SMALL_BUFF)
        z.set_color(z_in.get_color())
        f_z = TexMobject("f(z)").next_to(z_out, UP+RIGHT, buff = SMALL_BUFF)
        f_z.set_color(z_out.get_color())

        self.add(z_in, z)
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(
            ShowCreation(z_out),
            Write(f_z)
        )
        self.wait(2)

class PreviewZetaAndContinuation(ZetaTransformationScene):
    CONFIG = {
        "default_apply_complex_function_kwargs" : {
            "run_time" : 4,
        }
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        reflected_plane = self.get_reflected_plane()

        titles = [
            TextMobject(
                "What does", "%s"%s,
                "look like?",
                alignment = "",
            )
            for s in [
                "$\\displaystyle \\sum_{n=1}^\\infty \\frac{1}{n^s}$",
                "analytic continuation"
            ]
        ]
        for mob in titles:
            mob[1].set_color(YELLOW)
            mob.to_corner(UP+LEFT, buff = 0.7)
            mob.add_background_rectangle()

        self.remove(self.plane)
        self.play(Write(titles[0], run_time = 2))
        self.add_foreground_mobjects(titles[0])
        self.play(FadeIn(self.plane))
        self.apply_zeta_function()
        reflected_plane.apply_complex_function(zeta)
        reflected_plane.make_smooth()
        reflected_plane.set_stroke(width = 2)
        self.wait()
        self.play(Transform(*titles))
        self.wait()
        self.play(ShowCreation(
            reflected_plane,
            lag_ratio = 0,
            run_time = 2
        ))
        self.wait()

class AssumeKnowledgeOfComplexNumbers(ComplexTransformationScene):
    def construct(self):
        z = complex(5, 2)
        dot = Dot(z.real*RIGHT + z.imag*UP, color = YELLOW)
        line = Line(ORIGIN, dot.get_center(), color = dot.get_color())
        x_line = Line(ORIGIN, z.real*RIGHT, color = GREEN_B)
        y_line = Line(ORIGIN, z.imag*UP, color = RED)
        y_line.shift(z.real*RIGHT)
        complex_number_label = TexMobject(
            "%d+%di"%(int(z.real), int(z.imag))
        )
        complex_number_label[0].set_color(x_line.get_color())
        complex_number_label[2].set_color(y_line.get_color())
        complex_number_label.next_to(dot, UP)

        text = VGroup(
            TextMobject("Assumed knowledge:"),
            TextMobject("1) What complex numbers are."),
            TextMobject("2) How to work with them."),
            TextMobject("3) Maybe derivatives?"),
        )
        text.arrange(DOWN, aligned_edge = LEFT)
        for words in text:
            words.add_background_rectangle()
        text[0].shift(LEFT)
        text[-1].set_color(PINK)
        text.to_corner(UP+LEFT)

        self.play(Write(text[0]))
        self.wait()
        self.play(FadeIn(text[1]))
        self.play(
            ShowCreation(x_line),
            ShowCreation(y_line),
            ShowCreation(VGroup(line, dot)),
            Write(complex_number_label),
        )
        self.play(Write(text[2]))
        self.wait(2)
        self.play(Write(text[3]))
        self.wait()
        self.play(text[3].fade)

class DefineForRealS(PiCreatureScene):
    def construct(self):
        zeta_def, s_group = self.get_definition("s")

        self.initial_definition(zeta_def)
        self.plug_in_two(zeta_def)
        self.plug_in_three_and_four(zeta_def)
        self.plug_in_negative_values(zeta_def)

    def initial_definition(self, zeta_def):
        zeta_s, sum_terms, brace, sigma = zeta_def

        self.say("Let's define $\\zeta(s)$")
        self.blink()
        pre_zeta_s = VGroup(
            *self.pi_creature.bubble.content.copy()[-4:]
        )
        pre_zeta_s.add(VectorizedPoint(pre_zeta_s.get_right()))
        self.play(
            Transform(pre_zeta_s, zeta_s),
            *self.get_bubble_fade_anims()
        )
        self.remove(pre_zeta_s)
        self.add(zeta_s)
        self.wait()

        for count, term in enumerate(sum_terms):
            self.play(FadeIn(term), run_time = 0.5)
            if count%2 == 0:
                self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(sigma),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait()

    def plug_in_two(self, zeta_def):
        two_def = self.get_definition("2")[0]
        number_line = NumberLine(
            x_min = 0,
            x_max = 3,
            tick_frequency = 0.25,
            numbers_with_elongated_ticks = list(range(4)),
            unit_size = 3,
        )
        number_line.add_numbers()
        number_line.next_to(self.pi_creature, LEFT)
        number_line.to_edge(LEFT)
        self.number_line = number_line

        lines, braces, dots, pi_dot = self.get_sum_lines(2)
        fracs = VGroup(*[
            TexMobject("\\frac{1}{%d}"%((d+1)**2)).scale(0.7)
            for d, brace in enumerate(braces)
        ])
        for frac, brace, line in zip(fracs, braces, lines):
            frac.set_color(line.get_color())
            frac.next_to(brace, UP, buff = SMALL_BUFF)
            if frac is fracs[-1]:
                frac.shift(0.5*RIGHT + 0.2*UP)
                arrow = Arrow(
                    frac.get_bottom(), brace.get_top(),
                    tip_length = 0.1,
                    buff = 0.1
                )
                arrow.set_color(line.get_color())
                frac.add(arrow)

        pi_term = TexMobject("= \\frac{\\pi^2}{6}")
        pi_term.next_to(zeta_def[1], RIGHT)
        pi_arrow = Arrow(
            pi_term[-1].get_bottom(), pi_dot,
            color = pi_dot.get_color()
        )
        approx = TexMobject("\\approx 1.645")
        approx.next_to(pi_term)

        self.play(Transform(zeta_def, two_def))
        self.wait()
        self.play(ShowCreation(number_line))

        for frac, brace, line in zip(fracs, braces, lines):
            self.play(
                Write(frac),
                GrowFromCenter(brace),
                ShowCreation(line),
                run_time = 0.7
            )
            self.wait(0.7)
        self.wait()
        self.play(
            ShowCreation(VGroup(*lines[4:])),
            Write(dots)
        )
        self.wait()
        self.play(
            Write(pi_term),
            ShowCreation(VGroup(pi_arrow, pi_dot)),
            self.pi_creature.change_mode, "hooray"
        )
        self.wait()
        self.play(
            Write(approx),
            self.pi_creature.change_mode, "happy"
        )
        self.wait(3)
        self.play(*list(map(FadeOut, [
            fracs, pi_arrow, pi_dot, approx,
        ])))
        self.lines = lines
        self.braces = braces
        self.dots = dots
        self.final_dot = pi_dot
        self.final_sum = pi_term

    def plug_in_three_and_four(self, zeta_def):
        final_sums = ["1.202\\dots", "\\frac{\\pi^4}{90}"]
        sum_terms, brace, sigma = zeta_def[1:]
        for exponent, final_sum in zip([3, 4], final_sums):
            self.transition_to_new_input(zeta_def, exponent, final_sum)
            self.wait()

        arrow = Arrow(sum_terms.get_left(), sum_terms.get_right())
        arrow.next_to(sum_terms, DOWN)
        smaller_words = TextMobject("Getting smaller")
        smaller_words.next_to(arrow, DOWN)
        self.arrow, self.smaller_words = arrow, smaller_words

        self.wait()
        self.play(
            ShowCreation(arrow),
            Write(smaller_words)
        )
        self.change_mode("happy")
        self.wait(2)

    def plug_in_negative_values(self, zeta_def):
        zeta_s, sum_terms, brace, sigma = zeta_def
        arrow = self.arrow
        smaller_words = self.smaller_words
        bigger_words = TextMobject("Getting \\emph{bigger}?")
        bigger_words.move_to(self.smaller_words)

        #plug in -1
        self.transition_to_new_input(zeta_def, -1, "-\\frac{1}{12}")
        self.play(
            Transform(self.smaller_words, bigger_words),
            self.pi_creature.change_mode, "confused"
        )
        new_sum_terms = TexMobject(
            list("1+2+3+4+") + ["\\cdots"]
        )
        new_sum_terms.move_to(sum_terms, LEFT)
        arrow.target = arrow.copy().next_to(new_sum_terms, DOWN)
        arrow.target.stretch_to_fit_width(new_sum_terms.get_width())
        bigger_words.next_to(arrow.target, DOWN)
        new_brace = Brace(new_sum_terms, UP)
        self.play(
            Transform(sum_terms, new_sum_terms),
            Transform(brace, new_brace),
            sigma.next_to, new_brace, UP,
            MoveToTarget(arrow),
            Transform(smaller_words, bigger_words),
            self.final_sum.next_to, new_sum_terms, RIGHT
        )
        self.wait(3)

        #plug in -2
        new_sum_terms = TexMobject(
            list("1+4+9+16+") + ["\\cdots"]
        )
        new_sum_terms.move_to(sum_terms, LEFT)
        new_zeta_def, ignore = self.get_definition("-2")
        zeta_minus_two, ignore, ignore, new_sigma = new_zeta_def
        new_sigma.next_to(brace, UP)
        new_final_sum = TexMobject("=0")
        new_final_sum.next_to(new_sum_terms)
        lines, braces, dots, final_dot = self.get_sum_lines(-2)

        self.play(
            Transform(zeta_s, zeta_minus_two),
            Transform(sum_terms, new_sum_terms),
            Transform(sigma, new_sigma),
            Transform(self.final_sum, new_final_sum),
            Transform(self.lines, lines),
            Transform(self.braces, braces),
        )
        self.wait()
        self.change_mode("pleading")
        self.wait(2)

    def get_definition(self, input_string, input_color = YELLOW):
        inputs = VGroup()
        num_shown_terms = 4
        n_input_chars = len(input_string)

        zeta_s_eq = TexMobject("\\zeta(%s) = "%input_string)
        zeta_s_eq.to_edge(LEFT, buff = LARGE_BUFF)
        zeta_s_eq.shift(0.5*UP)
        inputs.add(*zeta_s_eq[2:2+n_input_chars])

        sum_terms = TexMobject(*it.chain(*list(zip(
            [
                "\\frac{1}{%d^{%s}}"%(d, input_string)
                for d in range(1, 1+num_shown_terms)
            ],
            it.cycle(["+"])
        ))))
        sum_terms.add(TexMobject("\\cdots").next_to(sum_terms))
        sum_terms.next_to(zeta_s_eq, RIGHT)
        for x in range(num_shown_terms):
            inputs.add(*sum_terms[2*x][-n_input_chars:])


        brace = Brace(sum_terms, UP)
        sigma = TexMobject(
            "\\sum_{n=1}^\\infty \\frac{1}{n^{%s}}"%input_string
        )
        sigma.next_to(brace, UP)
        inputs.add(*sigma[-n_input_chars:])

        inputs.set_color(input_color)
        group = VGroup(zeta_s_eq, sum_terms, brace, sigma)
        return group, inputs

    def get_sum_lines(self, exponent, line_thickness = 6):
        num_lines = 100 if exponent > 0 else 6
        powers = [0] + [x**(-exponent) for x in range(1, num_lines)]
        power_sums = np.cumsum(powers)
        lines = VGroup(*[
            Line(
                self.number_line.number_to_point(s1),
                self.number_line.number_to_point(s2),
            )
            for s1, s2 in zip(power_sums, power_sums[1:])
        ])
        lines.set_stroke(width = line_thickness)
        # VGroup(*lines[:4]).set_color_by_gradient(RED, GREEN_B)
        # VGroup(*lines[4:]).set_color_by_gradient(GREEN_B, MAROON_B)
        VGroup(*lines[::2]).set_color(MAROON_B)
        VGroup(*lines[1::2]).set_color(RED)

        braces = VGroup(*[
            Brace(line, UP)
            for line in lines[:4]
        ])
        dots = TexMobject("...")
        dots.stretch_to_fit_width(
            0.8 * VGroup(*lines[4:]).get_width()
        )
        dots.next_to(braces, RIGHT, buff = SMALL_BUFF)

        final_dot = Dot(
            self.number_line.number_to_point(power_sums[-1]),
            color = GREEN_B
        )

        return lines, braces, dots, final_dot

    def transition_to_new_input(self, zeta_def, exponent, final_sum):
        new_zeta_def = self.get_definition(str(exponent))[0]
        lines, braces, dots, final_dot = self.get_sum_lines(exponent)
        final_sum = TexMobject("=" + final_sum)
        final_sum.next_to(new_zeta_def[1][-1])
        final_sum.shift(SMALL_BUFF*UP)
        self.play(
            Transform(zeta_def, new_zeta_def),
            Transform(self.lines, lines),
            Transform(self.braces, braces),
            Transform(self.dots, dots),
            Transform(self.final_dot, final_dot),
            Transform(self.final_sum, final_sum),
            self.pi_creature.change_mode, "pondering"
        )

class ReadIntoZetaFunction(Scene):
    CONFIG = {
        "statement" : "$\\zeta(-1) = -\\frac{1}{12}$",
        "target_mode" : "frustrated",
    }
    def construct(self):
        randy = Randolph(mode = "pondering")
        randy.shift(3*LEFT+DOWN)
        paper = Rectangle(width = 4, height = 5)
        paper.next_to(randy, RIGHT, aligned_edge = DOWN)
        paper.set_color(WHITE)
        max_width = 0.8*paper.get_width()

        title = TextMobject("$\\zeta(s)$ manual")
        title.next_to(paper.get_top(), DOWN)
        title.set_color(YELLOW)
        paper.add(title)
        paragraph_lines = VGroup(
            Line(LEFT, RIGHT),
            Line(LEFT, RIGHT).shift(0.2*DOWN),
            Line(LEFT, ORIGIN).shift(0.4*DOWN)
        )
        paragraph_lines.set_width(max_width)
        paragraph_lines.next_to(title, DOWN, MED_LARGE_BUFF)
        paper.add(paragraph_lines)
        max_height = 1.5*paragraph_lines.get_height()

        statement = TextMobject(self.statement)
        if statement.get_width() > max_width:
            statement.set_width(max_width)
        if statement.get_height() > max_height:
            statement.set_height(max_height)

        statement.next_to(paragraph_lines, DOWN)
        statement.set_color(GREEN_B)
        paper.add(paragraph_lines.copy().next_to(statement, DOWN, MED_LARGE_BUFF))

        randy.look_at(statement)
        self.add(randy, paper)
        self.play(Write(statement))
        self.play(
            randy.change_mode, self.target_mode,
            randy.look_at, title
        )
        self.play(Blink(randy))
        self.play(randy.look_at, statement)
        self.wait()

class ReadIntoZetaFunctionTrivialZero(ReadIntoZetaFunction):
    CONFIG = {
        "statement" : "$\\zeta(-2n) = 0$"
    }

class ReadIntoZetaFunctionAnalyticContinuation(ReadIntoZetaFunction):
    CONFIG = {
        "statement" : "...analytic \\\\ continuation...",
        "target_mode" : "confused",
    }

class IgnoreNegatives(TeacherStudentsScene):
    def construct(self):
        definition = TexMobject("""
            \\zeta(s) = \\sum_{n=1}^{\\infty} \\frac{1}{n^s}
        """)
        VGroup(definition[2], definition[-1]).set_color(YELLOW)
        definition.to_corner(UP+LEFT)
        self.add(definition)
        brace = Brace(definition, DOWN)
        only_s_gt_1 = brace.get_text("""
            Only defined
            for $s > 1$
        """)
        only_s_gt_1[-3].set_color(YELLOW)


        self.change_student_modes(*["confused"]*3)
        words = TextMobject(
            "Ignore $s \\le 1$ \\dots \\\\",
            "For now."
        )
        words[0][6].set_color(YELLOW)
        words[1].set_color(BLACK)
        self.teacher_says(words)
        self.play(words[1].set_color, WHITE)
        self.change_student_modes(*["happy"]*3)
        self.play(
            GrowFromCenter(brace),
            Write(only_s_gt_1),
            *it.chain(*[
                [pi.look_at, definition]
                for pi in self.get_pi_creatures()
            ])
        )
        self.random_blink(3)

class RiemannFatherOfComplex(ComplexTransformationScene):
    def construct(self):
        name = TextMobject(
            "Bernhard Riemann $\\rightarrow$ Complex analysis"
        )
        name.to_corner(UP+LEFT)
        name.shift(0.25*DOWN)
        name.add_background_rectangle()
        # photo = Square()
        photo = ImageMobject("Riemann", invert = False)
        photo.set_width(5)
        photo.next_to(name, DOWN, aligned_edge = LEFT)


        self.add(photo)
        self.play(Write(name))
        self.wait()

        input_dot = Dot(2*RIGHT+UP, color = YELLOW)
        arc = Arc(-2*np.pi/3)
        arc.rotate(-np.pi)
        arc.add_tip()
        arc.shift(input_dot.get_top()-arc.points[0]+SMALL_BUFF*UP)
        output_dot = Dot(
            arc.points[-1] + SMALL_BUFF*(2*RIGHT+DOWN),
            color = MAROON_B
        )
        for dot, tex in (input_dot, "z"), (output_dot, "f(z)"):
            dot.label = TexMobject(tex)
            dot.label.add_background_rectangle()
            dot.label.next_to(dot, DOWN+RIGHT, buff = SMALL_BUFF)
            dot.label.set_color(dot.get_color())

        self.play(
            ShowCreation(input_dot),
            Write(input_dot.label)
        )
        self.play(ShowCreation(arc))
        self.play(
            ShowCreation(output_dot),
            Write(output_dot.label)
        )
        self.wait()

class FromRealToComplex(ComplexTransformationScene):
    CONFIG = {
        "plane_config" : {
            "space_unit_to_x_unit" : 2,
            "space_unit_to_y_unit" : 2,
        },
        "background_label_scale_val" : 0.7,
        "output_color" : GREEN_B,
        "num_lines_in_spiril_sum" : 1000,
    }
    def construct(self):
        self.handle_background()
        self.show_real_to_real()
        self.transition_to_complex()
        self.single_out_complex_exponent()
        ##Fade to several scenes defined below
        self.show_s_equals_two_lines()
        self.transition_to_spiril_sum()
        self.vary_complex_input()
        self.show_domain_of_convergence()
        self.ask_about_visualizing_all()

    def handle_background(self):
        self.remove(self.background)
        #Oh yeah, this is great practice...
        self.background[-1].remove(*self.background[-1][-3:])

    def show_real_to_real(self):
        zeta = self.get_zeta_definition("2",  "\\frac{\\pi^2}{6}")
        number_line = NumberLine(
            unit_size = 2,
            tick_frequency = 0.5,
            numbers_with_elongated_ticks = list(range(-2, 3))
        )
        number_line.add_numbers()
        input_dot = Dot(number_line.number_to_point(2))
        input_dot.set_color(YELLOW)

        output_dot = Dot(number_line.number_to_point(np.pi**2/6))
        output_dot.set_color(self.output_color)

        arc = Arc(
            2*np.pi/3, start_angle = np.pi/6,
        )
        arc.stretch_to_fit_width(
            (input_dot.get_center()-output_dot.get_center())[0]
        )
        arc.stretch_to_fit_height(0.5)
        arc.next_to(input_dot.get_center(), UP, aligned_edge = RIGHT)
        arc.add_tip()

        two = zeta[1][2].copy()
        sum_term = zeta[-1]
        self.add(number_line, *zeta[:-1])
        self.wait()
        self.play(Transform(two, input_dot))
        self.remove(two)
        self.add(input_dot)
        self.play(ShowCreation(arc))
        self.play(ShowCreation(output_dot))
        self.play(Transform(output_dot.copy(), sum_term))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(sum_term)
        self.wait(2)
        self.play(
            ShowCreation(
                self.background,
                run_time = 2
            ),
            FadeOut(VGroup(arc, output_dot, number_line)),
            Animation(zeta),
            Animation(input_dot)
        )
        self.wait(2)

        self.zeta = zeta
        self.input_dot = input_dot

    def transition_to_complex(self):
        complex_zeta = self.get_zeta_definition("2+i", "???")
        input_dot = self.input_dot
        input_dot.generate_target()
        input_dot.target.move_to(
            self.background.num_pair_to_point((2, 1))
        )
        input_label = TexMobject("2+i")
        input_label.set_color(YELLOW)
        input_label.next_to(input_dot.target, DOWN+RIGHT, buff = SMALL_BUFF)
        input_label.add_background_rectangle()
        input_label.save_state()
        input_label.replace(VGroup(*complex_zeta[1][2:5]))
        input_label.background_rectangle.scale_in_place(0.01)
        self.input_label = input_label

        self.play(Transform(self.zeta, complex_zeta))
        self.wait()
        self.play(
            input_label.restore,
            MoveToTarget(input_dot)
        )
        self.wait(2)

    def single_out_complex_exponent(self):
        frac_scale_factor = 1.2

        randy = Randolph()
        randy.to_corner()
        bubble = randy.get_bubble(height = 4)
        bubble.set_fill(BLACK, opacity = 1)

        frac = VGroup(
            VectorizedPoint(self.zeta[2][3].get_left()),
            self.zeta[2][3],
            VectorizedPoint(self.zeta[2][3].get_right()),
            self.zeta[2][4],
        ).copy()
        frac.generate_target()
        frac.target.scale(frac_scale_factor)
        bubble.add_content(frac.target)
        new_frac = TexMobject(
            "\\Big(", "\\frac{1}{2}", "\\Big)", "^{2+i}"
        )
        new_frac[-1].set_color(YELLOW)
        new_frac.scale(frac_scale_factor)
        new_frac.move_to(frac.target)
        new_frac.shift(LEFT+0.2*UP)

        words = TextMobject("Not repeated \\\\", " multiplication")
        words.scale(0.8)
        words.set_color(RED)
        words.next_to(new_frac, RIGHT)

        new_words = TextMobject("Not \\emph{super} \\\\", "crucial to know...")
        new_words.replace(words)
        new_words.scale_in_place(1.3)

        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, bubble,
            ShowCreation(bubble),
            MoveToTarget(frac)
        )
        self.play(Blink(randy))
        self.play(Transform(frac, new_frac))
        self.play(Write(words))
        for x in range(2):
            self.wait(2)
            self.play(Blink(randy))
        self.play(
            Transform(words, new_words),
            randy.change_mode, "maybe"
        )
        self.wait()
        self.play(Blink(randy))
        self.play(randy.change_mode, "happy")
        self.wait()
        self.play(*list(map(FadeOut, [randy, bubble, frac, words])))

    def show_s_equals_two_lines(self):
        self.input_label.save_state()
        zeta = self.get_zeta_definition("2", "\\frac{\\pi^2}{6}")
        lines, output_dot = self.get_sum_lines(2)
        sum_terms = self.zeta[2][:-1:3]
        dots_copy = zeta[2][-1].copy()
        pi_copy = zeta[3].copy()
        def transform_and_replace(m1, m2):
            self.play(Transform(m1, m2))
            self.remove(m1)
            self.add(m2)

        self.play(
            self.input_dot.shift, 2*DOWN,
            self.input_label.fade, 0.7,
        )
        self.play(Transform(self.zeta, zeta))

        for term, line in zip(sum_terms, lines):
            line.save_state()
            line.next_to(term, DOWN)
            term_copy = term.copy()
            transform_and_replace(term_copy, line)
            self.play(line.restore)
        later_lines = VGroup(*lines[4:])
        transform_and_replace(dots_copy, later_lines)
        self.wait()
        transform_and_replace(pi_copy, output_dot)
        self.wait()

        self.lines = lines
        self.output_dot = output_dot

    def transition_to_spiril_sum(self):
        zeta = self.get_zeta_definition("2+i", "1.15 - 0.44i")
        zeta.set_width(FRAME_WIDTH-1)
        zeta.to_corner(UP+LEFT)
        lines, output_dot = self.get_sum_lines(complex(2, 1))

        self.play(
            self.input_dot.shift, 2*UP,
            self.input_label.restore,
        )
        self.wait()
        self.play(Transform(self.zeta, zeta))
        self.wait()
        self.play(
            Transform(self.lines, lines),
            Transform(self.output_dot, output_dot),
            run_time = 2,
            path_arc = -np.pi/6,
        )
        self.wait()

    def vary_complex_input(self):
        zeta = self.get_zeta_definition("s", "")
        zeta[3].set_color(BLACK)
        self.play(Transform(self.zeta, zeta))
        self.play(FadeOut(self.input_label))
        self.wait(2)
        inputs = [
            complex(1.5, 1.8),
            complex(1.5, -1),
            complex(3, -1),
            complex(1.5, 1.8),
            complex(1.5, -1.8),
            complex(1.4, -1.8),
            complex(1.5, 0),
            complex(2, 1),
        ]
        for s in inputs:
            input_point = self.z_to_point(s)
            lines, output_dot = self.get_sum_lines(s)
            self.play(
                self.input_dot.move_to, input_point,
                Transform(self.lines, lines),
                Transform(self.output_dot, output_dot),
                run_time = 2
            )
            self.wait()
        self.wait()

    def show_domain_of_convergence(self, opacity = 0.2):
        domain = Rectangle(
            width = FRAME_X_RADIUS-2,
            height = FRAME_HEIGHT,
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = opacity,
        )
        domain.to_edge(RIGHT, buff = 0)
        anti_domain = Rectangle(
            width = FRAME_X_RADIUS+2,
            height = FRAME_HEIGHT,
            stroke_width = 0,
            fill_color = RED,
            fill_opacity = opacity,
        )
        anti_domain.to_edge(LEFT, buff = 0)

        domain_words = TextMobject("""
            $\\zeta(s)$ happily
            converges and
            makes sense
        """)
        domain_words.to_corner(UP+RIGHT, buff = MED_LARGE_BUFF)

        anti_domain_words = TextMobject("""
            Not so much...
        """)
        anti_domain_words.next_to(ORIGIN, LEFT, buff = LARGE_BUFF)
        anti_domain_words.shift(1.5*DOWN)

        self.play(FadeIn(domain))
        self.play(Write(domain_words))
        self.wait()
        self.play(FadeIn(anti_domain))
        self.play(Write(anti_domain_words))
        self.wait(2)
        self.play(*list(map(FadeOut, [
            anti_domain, anti_domain_words,
        ])))
        self.domain_words = domain_words

    def ask_about_visualizing_all(self):
        morty = Mortimer().flip()
        morty.scale(0.7)
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble(SpeechBubble, height = 4)
        bubble.set_fill(BLACK, opacity = 0.5)
        bubble.write("""
            How can we visualize
            this for all inputs?
        """)

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait(3)
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, self.input_dot,
            *list(map(FadeOut, [
                bubble, bubble.content, self.domain_words
            ]))
        )
        arrow = Arrow(self.input_dot, self.output_dot, buff = SMALL_BUFF)
        arrow.set_color(WHITE)
        self.play(ShowCreation(arrow))
        self.play(Blink(morty))
        self.wait()

    def get_zeta_definition(self, input_string, output_string, input_color = YELLOW):
        inputs = VGroup()
        num_shown_terms = 4
        n_input_chars = len(input_string)

        zeta_s_eq = TexMobject("\\zeta(%s) = "%input_string)
        zeta_s_eq.to_edge(LEFT, buff = LARGE_BUFF)
        zeta_s_eq.shift(0.5*UP)
        inputs.add(*zeta_s_eq[2:2+n_input_chars])


        raw_sum_terms = TexMobject(*[
            "\\frac{1}{%d^{%s}} + "%(d, input_string)
            for d in range(1, 1+num_shown_terms)
        ])
        sum_terms = VGroup(*it.chain(*[
            [
                VGroup(*term[:3]),
                VGroup(*term[3:-1]),
                term[-1],
            ]
            for term in raw_sum_terms
        ]))
        sum_terms.add(TexMobject("\\cdots").next_to(sum_terms[-1]))
        sum_terms.next_to(zeta_s_eq, RIGHT)
        for x in range(num_shown_terms):
            inputs.add(*sum_terms[3*x+1])

        output = TexMobject("= \\," + output_string)
        output.next_to(sum_terms, RIGHT)
        output.set_color(self.output_color)

        inputs.set_color(input_color)
        group = VGroup(zeta_s_eq, sum_terms, output)
        group.to_edge(UP)
        group.add_to_back(BackgroundRectangle(group))
        return group

    def get_sum_lines(self, exponent, line_thickness = 6):
        powers = [0] + [
            x**(-exponent)
            for x in range(1, self.num_lines_in_spiril_sum)
        ]
        power_sums = np.cumsum(powers)
        lines = VGroup(*[
            Line(*list(map(self.z_to_point, z_pair)))
            for z_pair in zip(power_sums, power_sums[1:])
        ])
        widths = np.linspace(line_thickness, 0, len(list(lines)))
        for line, width in zip(lines, widths):
            line.set_stroke(width = width)
        VGroup(*lines[::2]).set_color(MAROON_B)
        VGroup(*lines[1::2]).set_color(RED)

        final_dot = Dot(
            # self.z_to_point(power_sums[-1]),
            self.z_to_point(zeta(exponent)),
            color = self.output_color
        )

        return lines, final_dot

class TerritoryOfExponents(ComplexTransformationScene):
    def construct(self):
        self.add_title()
        familiar_territory = TextMobject("Familiar territory")
        familiar_territory.set_color(YELLOW)
        familiar_territory.next_to(ORIGIN, UP+RIGHT)
        familiar_territory.shift(2*UP)
        real_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        real_line.set_color(YELLOW)
        arrow1 = Arrow(familiar_territory.get_bottom(), real_line.get_left())
        arrow2 = Arrow(familiar_territory.get_bottom(), real_line.get_right())
        VGroup(arrow1, arrow2).set_color(WHITE)

        extended_realm = TextMobject("Extended realm")
        extended_realm.move_to(familiar_territory)
        full_plane = Rectangle(
            width = FRAME_WIDTH,
            height = FRAME_HEIGHT,
            fill_color = YELLOW,
            fill_opacity = 0.3
        )

        self.add(familiar_territory)
        self.play(ShowCreation(arrow1))
        self.play(
            Transform(arrow1, arrow2),
            ShowCreation(real_line)
        )
        self.play(FadeOut(arrow1))
        self.play(
            FadeIn(full_plane),
            Transform(familiar_territory, extended_realm),
            Animation(real_line)
        )

    def add_title(self):
        exponent = TexMobject(
            "\\left(\\frac{1}{2}\\right)^s"
        )
        exponent[-1].set_color(YELLOW)
        exponent.next_to(ORIGIN, LEFT, MED_LARGE_BUFF).to_edge(UP)
        self.add_foreground_mobjects(exponent)

class ComplexExponentiation(Scene):
    def construct(self):
        self.extract_pure_imaginary_part()
        self.add_on_planes()
        self.show_imaginary_powers()

    def extract_pure_imaginary_part(self):
        original = TexMobject(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        split = TexMobject(
             "\\left(\\frac{1}{2}\\right)", "^{2}",
             "\\left(\\frac{1}{2}\\right)", "^{i}",
        )
        VGroup(original[-1], split[1], split[3]).set_color(YELLOW)
        VGroup(original, split).shift(UP)
        real_part = VGroup(*split[:2])
        imag_part = VGroup(*split[2:])

        brace = Brace(real_part)
        we_understand = brace.get_text(
            "We understand this"
        )
        VGroup(brace, we_understand).set_color(GREEN_B)

        self.add(original)
        self.wait()
        self.play(*[
            Transform(*pair)
            for pair in [
                (original[0], split[0]),
                (original[1][0], split[1]),
                (original[0].copy(), split[2]),
                (VGroup(*original[1][1:]), split[3]),
            ]
        ])
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(real_part, imag_part)
        self.wait()
        self.play(
            GrowFromCenter(brace),
            FadeIn(we_understand),
            real_part.set_color, GREEN_B
        )
        self.wait()
        self.play(
            imag_part.move_to, imag_part.get_left(),
            *list(map(FadeOut, [brace, we_understand, real_part]))
        )
        self.wait()
        self.imag_exponent = imag_part

    def add_on_planes(self):
        left_plane = NumberPlane(x_radius = (FRAME_X_RADIUS-1)/2)
        left_plane.to_edge(LEFT, buff = 0)
        imag_line = Line(DOWN, UP).scale(FRAME_Y_RADIUS)
        imag_line.set_color(YELLOW).fade(0.3)
        imag_line.move_to(left_plane.get_center())
        left_plane.add(imag_line)
        left_title = TextMobject("Input space")
        left_title.add_background_rectangle()
        left_title.set_color(YELLOW)
        left_title.next_to(left_plane.get_top(), DOWN)

        right_plane = NumberPlane(x_radius = (FRAME_X_RADIUS-1)/2)
        right_plane.to_edge(RIGHT, buff = 0)
        unit_circle = Circle()
        unit_circle.set_color(MAROON_B).fade(0.3)
        unit_circle.shift(right_plane.get_center())
        right_plane.add(unit_circle)
        right_title = TextMobject("Output space")
        right_title.add_background_rectangle()
        right_title.set_color(MAROON_B)
        right_title.next_to(right_plane.get_top(), DOWN)

        for plane in left_plane, right_plane:
            labels = VGroup()
            for x in range(-2, 3):
                label = TexMobject(str(x))
                label.move_to(plane.num_pair_to_point((x, 0)))
                labels.add(label)
            for y in range(-3, 4):
                if y == 0:
                    continue
                label = TexMobject(str(y) + "i")
                label.move_to(plane.num_pair_to_point((0, y)))
                labels.add(label)
            for label in labels:
                label.scale_in_place(0.5)
                label.next_to(
                    label.get_center(), DOWN+RIGHT,
                    buff = SMALL_BUFF
                )
            plane.add(labels)

        arrow = Arrow(LEFT, RIGHT)

        self.play(
            ShowCreation(left_plane),
            Write(left_title),
            run_time = 3
        )
        self.play(
            ShowCreation(right_plane),
            Write(right_title),
            run_time = 3
        )
        self.play(ShowCreation(arrow))
        self.wait()
        self.left_plane = left_plane
        self.right_plane = right_plane

    def show_imaginary_powers(self):
        i = complex(0, 1)
        input_dot = Dot(self.z_to_point(i))
        input_dot.set_color(YELLOW)
        output_dot = Dot(self.z_to_point(0.5**(i), is_input = False))
        output_dot.set_color(MAROON_B)

        output_dot.save_state()
        output_dot.move_to(input_dot)
        output_dot.set_color(input_dot.get_color())

        curr_base = 0.5
        def output_dot_update(ouput_dot):
            y = input_dot.get_center()[1]
            output_dot.move_to(self.z_to_point(
                curr_base**complex(0, y), is_input = False
            ))
            return output_dot

        def walk_up_and_down():
            for vect in 3*DOWN, 5*UP, 5*DOWN, 2*UP:
                self.play(
                    input_dot.shift, vect,
                    UpdateFromFunc(output_dot, output_dot_update),
                    run_time = 3
                )

        exp = self.imag_exponent[-1]
        new_exp = TexMobject("ti")
        new_exp.set_color(exp.get_color())
        new_exp.set_height(exp.get_height())
        new_exp.move_to(exp, LEFT)

        nine = TexMobject("9")
        nine.set_color(BLUE)
        denom = self.imag_exponent[0][3]
        denom.save_state()
        nine.replace(denom)

        self.play(Transform(exp, new_exp))
        self.play(input_dot.shift, 2*UP)
        self.play(input_dot.shift, 2*DOWN)
        self.wait()
        self.play(output_dot.restore)
        self.wait()
        walk_up_and_down()
        self.wait()
        curr_base = 1./9
        self.play(Transform(denom, nine))
        walk_up_and_down()
        self.wait()

    def z_to_point(self, z, is_input = True):
        if is_input:
            plane = self.left_plane
        else:
            plane = self.right_plane
        return plane.num_pair_to_point((z.real, z.imag))

class SizeAndRotationBreakdown(Scene):
    def construct(self):
        original = TexMobject(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        split = TexMobject(
             "\\left(\\frac{1}{2}\\right)", "^{2}",
             "\\left(\\frac{1}{2}\\right)", "^{i}",
        )
        VGroup(original[-1], split[1], split[3]).set_color(YELLOW)
        VGroup(original, split).shift(UP)
        real_part = VGroup(*split[:2])
        imag_part = VGroup(*split[2:])

        size_brace = Brace(real_part)
        size = size_brace.get_text("Size")
        rotation_brace = Brace(imag_part, UP)
        rotation = rotation_brace.get_text("Rotation")

        self.add(original)
        self.wait()
        self.play(*[
            Transform(*pair)
            for pair in [
                (original[0], split[0]),
                (original[1][0], split[1]),
                (original[0].copy(), split[2]),
                (VGroup(*original[1][1:]), split[3]),
            ]
        ])
        self.play(
            GrowFromCenter(size_brace),
            Write(size)
        )
        self.play(
            GrowFromCenter(rotation_brace),
            Write(rotation)
        )
        self.wait()

class SeeLinksInDescription(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            See links in the
            description for more.
        """)
        self.play(*it.chain(*[
            [pi.change_mode, "hooray", pi.look, DOWN]
            for pi in self.get_students()
        ]))
        self.random_blink(3)

class ShowMultiplicationOfRealAndImaginaryExponentialParts(FromRealToComplex):
    def construct(self):
        self.break_up_exponent()
        self.show_multiplication()

    def break_up_exponent(self):
        original = TexMobject(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        split = TexMobject(
             "\\left(\\frac{1}{2}\\right)", "^{2}",
             "\\left(\\frac{1}{2}\\right)", "^{i}",
        )
        VGroup(original[-1], split[1], split[3]).set_color(YELLOW)
        VGroup(original, split).to_corner(UP+LEFT)
        rect = BackgroundRectangle(split)
        real_part = VGroup(*split[:2])
        imag_part = VGroup(*split[2:])

        self.add(rect, original)
        self.wait()
        self.play(*[
            Transform(*pair)
            for pair in [
                (original[0], split[0]),
                (original[1][0], split[1]),
                (original[0].copy(), split[2]),
                (VGroup(*original[1][1:]), split[3]),
            ]
        ])
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(real_part, imag_part)
        self.wait()
        self.real_part = real_part
        self.imag_part = imag_part

    def show_multiplication(self):
        real_part = self.real_part.copy()
        imag_part = self.imag_part.copy()
        for part in real_part, imag_part:
            part.add_to_back(BackgroundRectangle(part))

        fourth_point = self.z_to_point(0.25)
        fourth_line = Line(ORIGIN, fourth_point)
        brace = Brace(fourth_line, UP, buff = SMALL_BUFF)
        fourth_dot = Dot(fourth_point)
        fourth_group = VGroup(fourth_line, brace, fourth_dot)
        fourth_group.set_color(RED)

        circle = Circle(radius = 2, color = MAROON_B)
        circle.fade(0.3)
        imag_power_point = self.z_to_point(0.5**complex(0, 1))
        imag_power_dot = Dot(imag_power_point)
        imag_power_line = Line(ORIGIN, imag_power_point)
        VGroup(imag_power_dot, imag_power_line).set_color(MAROON_B)

        full_power_tex = TexMobject(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        full_power_tex[-1].set_color(YELLOW)
        full_power_tex.add_background_rectangle()
        full_power_tex.scale(0.7)
        full_power_tex.next_to(
            0.5*self.z_to_point(0.5**complex(2, 1)),
            UP+RIGHT
        )

        self.play(
            real_part.scale, 0.7,
            real_part.next_to, brace, UP, SMALL_BUFF, LEFT,
            ShowCreation(fourth_dot)
        )
        self.play(
            GrowFromCenter(brace),
            ShowCreation(fourth_line),
        )
        self.wait()
        self.play(
            imag_part.scale, 0.7,
            imag_part.next_to, imag_power_dot, DOWN+RIGHT, SMALL_BUFF,
            ShowCreation(imag_power_dot)
        )
        self.play(ShowCreation(circle), Animation(imag_power_dot))
        self.play(ShowCreation(imag_power_line))
        self.wait(2)
        self.play(
            fourth_group.rotate, imag_power_line.get_angle()
        )
        real_part.generate_target()
        imag_part.generate_target()
        real_part.target.next_to(brace, UP+RIGHT, buff = 0)
        imag_part.target.next_to(real_part.target, buff = 0)
        self.play(*list(map(MoveToTarget, [real_part, imag_part])))
        self.wait()

class ComplexFunctionsAsTransformations(ComplexTransformationScene):
    def construct(self):
        self.add_title()
        input_dots, output_dots, arrows = self.get_dots()

        self.play(FadeIn(
            input_dots,
            run_time = 2,
            lag_ratio = 0.5
        ))
        for in_dot, out_dot, arrow in zip(input_dots, output_dots, arrows):
            self.play(
                Transform(in_dot.copy(), out_dot),
                ShowCreation(arrow)
            )
            self.wait()
        self.wait()


    def add_title(self):
        title = TextMobject("Complex functions as transformations")
        title.add_background_rectangle()
        title.to_edge(UP)
        self.add(title)

    def get_dots(self):
        input_points = [
            RIGHT+2*UP,
            4*RIGHT+DOWN,
            2*LEFT+2*UP,
            LEFT+DOWN,
            6*LEFT+DOWN,
        ]
        output_nudges = [
            DOWN+RIGHT,
            2*UP+RIGHT,
            2*RIGHT+2*DOWN,
            2*RIGHT+DOWN,
            RIGHT+2*UP,
        ]
        input_dots = VGroup(*list(map(Dot, input_points)))
        input_dots.set_color(YELLOW)
        output_dots = VGroup(*[
            Dot(ip + on)
            for ip, on in zip(input_points, output_nudges)
        ])
        output_dots.set_color(MAROON_B)
        arrows = VGroup(*[
            Arrow(in_dot, out_dot, buff = 0.1, color = WHITE)
            for in_dot, out_dot, in zip(input_dots, output_dots)
        ])
        for i, dot in enumerate(input_dots):
            label = TexMobject("s_%d"%i)
            label.set_color(dot.get_color())
            label.next_to(dot, DOWN+LEFT, buff = SMALL_BUFF)
            dot.add(label)
        for i, dot in enumerate(output_dots):
            label = TexMobject("f(s_%d)"%i)
            label.set_color(dot.get_color())
            label.next_to(dot, UP+RIGHT, buff = SMALL_BUFF)
            dot.add(label)
        return input_dots, output_dots, arrows

class VisualizingSSquared(ComplexTransformationScene):
    CONFIG = {
        "num_anchors_to_add_per_line" : 100,
        "horiz_end_color" : GOLD,
        "y_min" : 0,
    }
    def construct(self):
        self.add_title()
        self.plug_in_specific_values()
        self.show_transformation()
        self.comment_on_two_dimensions()

    def add_title(self):
        title = TexMobject("f(", "s", ") = ", "s", "^2")
        title.set_color_by_tex("s", YELLOW)
        title.add_background_rectangle()
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        self.play(Write(title))
        self.add_foreground_mobject(title)
        self.wait()
        self.title = title

    def plug_in_specific_values(self):
        inputs = list(map(complex, [2, -1, complex(0, 1)]))
        input_dots  = VGroup(*[
            Dot(self.z_to_point(z), color = YELLOW)
            for z in inputs
        ])
        output_dots = VGroup(*[
            Dot(self.z_to_point(z**2), color = BLUE)
            for z in inputs
        ])
        arrows = VGroup()
        VGroup(*[
            ParametricFunction(
                lambda t : self.z_to_point(z**(1.1+0.8*t))
            )
            for z in inputs
        ])
        for z, dot in zip(inputs, input_dots):
            path = ParametricFunction(
                lambda t : self.z_to_point(z**(1+t))
            )
            dot.path = path
            arrow = ParametricFunction(
                lambda t : self.z_to_point(z**(1.1+0.8*t))
            )
            stand_in_arrow = Arrow(
                arrow.points[-2], arrow.points[-1],
                tip_length = 0.2
            )
            arrow.add(stand_in_arrow.tip)
            arrows.add(arrow)
        arrows.set_color(WHITE)

        for input_dot, output_dot, arrow in zip(input_dots, output_dots, arrows):
            input_dot.save_state()
            input_dot.move_to(self.title[1][1])
            input_dot.set_fill(opacity = 0)

            self.play(input_dot.restore)
            self.wait()
            self.play(ShowCreation(arrow))
            self.play(ShowCreation(output_dot))
            self.wait()
        self.add_foreground_mobjects(arrows, output_dots, input_dots)
        self.input_dots = input_dots
        self.output_dots = output_dots

    def add_transformable_plane(self, **kwargs):
        ComplexTransformationScene.add_transformable_plane(self, **kwargs)
        self.plane.next_to(ORIGIN, UP, buff = 0.01)
        self.plane.add(self.plane.copy().rotate(np.pi, RIGHT))
        self.plane.add(
            Line(ORIGIN, FRAME_X_RADIUS*RIGHT, color = self.horiz_end_color),
            Line(ORIGIN, FRAME_X_RADIUS*LEFT, color = self.horiz_end_color),
        )
        self.add(self.plane)

    def show_transformation(self):
        self.add_transformable_plane()
        self.play(ShowCreation(self.plane, run_time = 3))

        self.wait()
        self.apply_complex_homotopy(
            lambda z, t : z**(1+t),
            added_anims = [
                MoveAlongPath(dot, dot.path, run_time = 5)
                for dot in self.input_dots
            ],
            run_time = 5
        )
        self.wait(2)


    def comment_on_two_dimensions(self):
        morty = Mortimer().flip()
        morty.scale(0.7)
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble(SpeechBubble, height = 2, width = 4)
        bubble.set_fill(BLACK, opacity = 0.9)
        bubble.write("""
            It all happens
            in two dimensions!
        """)
        self.foreground_mobjects = []

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "hooray",
            ShowCreation(bubble),
            Write(bubble.content),
        )
        self.play(Blink(morty))
        self.wait(2)

class ShowZetaOnHalfPlane(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
        "x_max" : int(FRAME_X_RADIUS+2),
    }
    def construct(self):
        self.add_title()
        self.initial_transformation()
        self.react_to_transformation()
        self.show_cutoff()
        self.set_color_i_line()
        self.show_continuation()
        self.emphsize_sum_doesnt_make_sense()


    def add_title(self):
        zeta = TexMobject(
            "\\zeta(", "s", ")=",
            *[
                "\\frac{1}{%d^s} + "%d
                for d in range(1, 5)
            ] + ["\\cdots"]
        )
        zeta[1].set_color(YELLOW)
        for mob in zeta[3:3+4]:
            mob[-2].set_color(YELLOW)
        zeta.add_background_rectangle()
        zeta.scale(0.8)
        zeta.to_corner(UP+LEFT)
        self.add_foreground_mobjects(zeta)
        self.zeta = zeta

    def initial_transformation(self):
        self.add_transformable_plane()
        self.wait()
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.wait(2)
        self.plane.save_state()
        self.apply_zeta_function()
        self.wait(2)

    def react_to_transformation(self):
        morty = Mortimer().flip()
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble(SpeechBubble)
        bubble.set_fill(BLACK, 0.5)
        bubble.write("\\emph{Damn}!")
        bubble.resize_to_content()
        bubble.pin_to(morty)

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "surprised",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.play(morty.look_at, self.plane.get_top())
        self.wait()
        self.play(
            morty.look_at, self.plane.get_bottom(),
            *list(map(FadeOut, [bubble, bubble.content]))
        )
        self.play(Blink(morty))
        self.play(FadeOut(morty))

    def show_cutoff(self):
        words = TextMobject("Such an abrupt stop...")
        words.add_background_rectangle()
        words.next_to(ORIGIN, UP+LEFT)
        words.shift(LEFT+UP)

        line = Line(*list(map(self.z_to_point, [
            complex(np.euler_gamma, u*FRAME_Y_RADIUS)
            for u in (1, -1)
        ])))
        line.set_color(YELLOW)
        arrows = [
            Arrow(words.get_right(), point)
            for point in line.get_start_and_end()
        ]

        self.play(Write(words, run_time = 2))
        self.play(ShowCreation(arrows[0]))
        self.play(
            Transform(*arrows),
            ShowCreation(line),
            run_time = 2
        )
        self.play(FadeOut(arrows[0]))
        self.wait(2)
        self.play(*list(map(FadeOut, [words, line])))

    def set_color_i_line(self):
        right_i_lines, left_i_lines = [
            VGroup(*[
                Line(
                    vert_vect+RIGHT,
                    vert_vect+(FRAME_X_RADIUS+1)*horiz_vect
                )
                for vert_vect in (UP, DOWN)
            ])
            for horiz_vect in (RIGHT, LEFT)
        ]
        right_i_lines.set_color(YELLOW)
        left_i_lines.set_color(BLUE)
        for lines in right_i_lines, left_i_lines:
            self.prepare_for_transformation(lines)

        self.restore_mobjects(self.plane)
        self.plane.add(*right_i_lines)
        colored_plane = self.plane.copy()
        right_i_lines.set_stroke(width = 0)
        self.play(
            self.plane.set_stroke, GREY, 1,
        )
        right_i_lines.set_stroke(YELLOW, width = 3)
        self.play(ShowCreation(right_i_lines))
        self.plane.save_state()
        self.wait(2)
        self.apply_zeta_function()
        self.wait(2)

        left_i_lines.save_state()
        left_i_lines.apply_complex_function(zeta)
        self.play(ShowCreation(left_i_lines, run_time = 5))
        self.wait()
        self.restore_mobjects(self.plane, left_i_lines)
        self.play(Transform(self.plane, colored_plane))
        self.wait()
        self.left_i_lines = left_i_lines

    def show_continuation(self):
        reflected_plane = self.get_reflected_plane()
        self.play(ShowCreation(reflected_plane, run_time = 2))
        self.plane.add(reflected_plane)
        self.remove(self.left_i_lines)
        self.wait()
        self.apply_zeta_function()
        self.wait(2)
        self.play(ShowCreation(
            reflected_plane,
            run_time = 6,
            rate_func = lambda t : 1-there_and_back(t)
        ))
        self.wait(2)

    def emphsize_sum_doesnt_make_sense(self):
        brace = Brace(VGroup(*self.zeta[1][3:]))
        words = brace.get_text("""
            Still fails to converge
            when Re$(s) < 1$
        """, buff = SMALL_BUFF)
        words.add_background_rectangle()
        words.scale_in_place(0.8)
        divergent_sum = TexMobject("1+2+3+4+\\cdots")
        divergent_sum.next_to(ORIGIN, UP)
        divergent_sum.to_edge(LEFT)
        divergent_sum.add_background_rectangle()

        self.play(
            GrowFromCenter(brace),
            Write(words)
        )
        self.wait(2)
        self.play(Write(divergent_sum))
        self.wait(2)

    def restore_mobjects(self, *mobjects):
        self.play(*it.chain(*[
            [m.restore, m.make_smooth]
            for m in  mobjects
        ]), run_time = 2)
        for m in mobjects:
            self.remove(m)
            m.restore()
            self.add(m)

class ShowConditionalDefinition(Scene):
    def construct(self):
        zeta = TexMobject("\\zeta(s)=")
        zeta[2].set_color(YELLOW)
        sigma = TexMobject("\\sum_{n=1}^\\infty \\frac{1}{n^s}")
        sigma[-1].set_color(YELLOW)
        something_else = TextMobject("Something else...")
        conditions = VGroup(*[
            TextMobject("if Re$(s) %s 1$"%s)
            for s in (">", "\\le")
        ])
        definitions = VGroup(sigma, something_else)
        definitions.arrange(DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT)
        conditions.arrange(DOWN, buff = LARGE_BUFF)
        definitions.shift(2*LEFT+2*UP)
        conditions.next_to(definitions, RIGHT, buff = LARGE_BUFF, aligned_edge = DOWN)
        brace = Brace(definitions, LEFT)
        zeta.next_to(brace, LEFT)

        sigma.save_state()
        sigma.next_to(zeta)
        self.add(zeta, sigma)
        self.wait()
        self.play(
            sigma.restore,
            GrowFromCenter(brace),
            FadeIn(something_else)
        )
        self.play(Write(conditions))
        self.wait()

        underbrace = Brace(something_else)
        question = underbrace.get_text("""
            What to put here?
        """)
        VGroup(underbrace, question).set_color(GREEN_B)

        self.play(
            GrowFromCenter(underbrace),
            Write(question),
            something_else.set_color, GREEN_B
        )
        self.wait(2)

class SquiggleOnExtensions(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
        "x_max" : int(FRAME_X_RADIUS+2),
    }
    def construct(self):
        self.show_negative_one()
        self.cycle_through_options()
        self.lock_into_place()

    def show_negative_one(self):
        self.add_transformable_plane()
        thin_plane = self.plane.copy()
        thin_plane.add(self.get_reflected_plane())
        self.remove(self.plane)
        self.add_extra_plane_lines_for_zeta()
        reflected_plane = self.get_reflected_plane()
        self.plane.add(reflected_plane)
        self.remove(self.plane)
        self.add(thin_plane)

        dot = self.note_point(-1, "-1")
        self.play(
            ShowCreation(self.plane, run_time = 2),
            Animation(dot),
            run_time = 2
        )
        self.remove(thin_plane)
        self.apply_zeta_function(added_anims = [
            ApplyMethod(
                dot.move_to, self.z_to_point(-1./12),
                run_time = 5
            )
        ])
        dot_to_remove = self.note_point(-1./12, "-\\frac{1}{12}")
        self.remove(dot_to_remove)
        self.left_plane = reflected_plane
        self.dot = dot

    def note_point(self, z, label_tex):
        dot = Dot(self.z_to_point(z))
        dot.set_color(YELLOW)
        label = TexMobject(label_tex)
        label.add_background_rectangle()
        label.next_to(dot, UP+LEFT, buff = SMALL_BUFF)
        label.shift(LEFT)
        arrow = Arrow(label.get_right(), dot, buff = SMALL_BUFF)

        self.play(Write(label, run_time = 1))
        self.play(*list(map(ShowCreation, [arrow, dot])))
        self.wait()
        self.play(*list(map(FadeOut, [arrow, label])))
        return dot

    def cycle_through_options(self):
        gamma = np.euler_gamma
        def shear(point):
            x, y, z = point
            return np.array([
                x,
                y+0.25*(1-x)**2,
                0
            ])
        def mixed_scalar_func(point):
            x, y, z = point
            scalar = 1 + (gamma-x)/(gamma+FRAME_X_RADIUS)
            return np.array([
                (scalar**2)*x,
                (scalar**3)*y,
                0
            ])
        def alt_mixed_scalar_func(point):
            x, y, z = point
            scalar = 1 + (gamma-x)/(gamma+FRAME_X_RADIUS)
            return np.array([
                (scalar**5)*x,
                (scalar**2)*y,
                0
            ])
        def sinusoidal_func(point):
            x, y, z = point
            freq = np.pi/gamma
            return np.array([
                x-0.2*np.sin(x*freq)*np.sin(y),
                y-0.2*np.sin(x*freq)*np.sin(y),
                0
            ])
        funcs = [
            shear,
            mixed_scalar_func,
            alt_mixed_scalar_func,
            sinusoidal_func,
        ]
        for mob in self.left_plane.family_members_with_points():
            if np.all(np.abs(mob.points[:,1]) < 0.1):
                self.left_plane.remove(mob)

        new_left_planes = [
            self.left_plane.copy().apply_function(func)
            for func in funcs
        ]
        new_dots = [
            self.dot.copy().move_to(func(self.dot.get_center()))
            for func in funcs
        ]
        self.left_plane.save_state()
        for plane, dot in zip(new_left_planes, new_dots):
            self.play(
                Transform(self.left_plane, plane),
                Transform(self.dot, dot),
                run_time = 3
            )
            self.wait()
        self.play(FadeOut(self.dot))

        #Squiggle on example
        self.wait()
        self.play(FadeOut(self.left_plane))
        self.play(ShowCreation(
            self.left_plane,
            run_time = 5,
            rate_func=linear
        ))
        self.wait()

    def lock_into_place(self):
        words = TextMobject(
            """Only one extension
            has a """,
            "\\emph{derivative}",
            "everywhere",
            alignment = ""
        )
        words.to_corner(UP+LEFT)
        words.set_color_by_tex("\\emph{derivative}", YELLOW)
        words.add_background_rectangle()

        self.play(Write(words))
        self.add_foreground_mobjects(words)
        self.play(self.left_plane.restore)
        self.wait()

class DontKnowDerivatives(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            """
            You said we don't
            need derivatives!
            """,
            target_mode = "pleading"
        )
        self.random_blink(2)
        self.student_says(
            """
            I get $\\frac{df}{dx}$, just not
            for complex functions
            """,
            target_mode = "confused",
            student_index = 2
        )
        self.random_blink(2)
        self.teacher_says(
            """
            Luckily, there's a purely
            geometric intuition here.
            """,
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.random_blink(3)

class IntroduceAnglePreservation(VisualizingSSquared):
    CONFIG = {
        "num_anchors_to_add_per_line" : 50,
        "use_homotopy" : True,
    }
    def construct(self):
        self.add_title()
        self.show_initial_transformation()
        self.talk_about_derivative()
        self.cycle_through_line_pairs()
        self.note_grid_lines()
        self.name_analytic()

    def add_title(self):
        title = TexMobject("f(", "s", ")=", "s", "^2")
        title.set_color_by_tex("s", YELLOW)
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        title.add_background_rectangle()
        self.title = title

        self.add_transformable_plane()
        self.play(Write(title))
        self.add_foreground_mobjects(title)
        self.wait()

    def show_initial_transformation(self):
        self.apply_function()
        self.wait(2)
        self.reset()

    def talk_about_derivative(self):
        randy = Randolph().scale(0.8)
        randy.to_corner(DOWN+LEFT)
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        randy.make_eye_contact(morty)
        for pi, words in (randy, "$f'(s) = 2s$"), (morty, "Here's some \\\\ related geometry..."):
            pi.bubble = pi.get_bubble(SpeechBubble)
            pi.bubble.set_fill(BLACK, opacity = 0.7)
            pi.bubble.write(words)
            pi.bubble.resize_to_content()
            pi.bubble.pin_to(pi)
        for index in 3, 7:
            randy.bubble.content[index].set_color(YELLOW)

        self.play(*list(map(FadeIn, [randy, morty])))
        self.play(
            randy.change_mode, "speaking",
            ShowCreation(randy.bubble),
            Write(randy.bubble.content)
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change_mode, "speaking",
            randy.change_mode, "pondering",
            ShowCreation(morty.bubble),
            Write(morty.bubble.content),
        )
        self.play(Blink(randy))
        self.wait()
        self.play(*list(map(FadeOut, [
            randy, morty,
            randy.bubble, randy.bubble.content,
            morty.bubble, morty.bubble.content,
        ])))


    def cycle_through_line_pairs(self):
        line_pairs = [
            (
                Line(3*DOWN+3*RIGHT, 2*UP),
                Line(DOWN+RIGHT, 3*UP+4*RIGHT)
            ),
            (
                Line(RIGHT+3.5*DOWN, RIGHT+2.5*UP),
                Line(3*LEFT+0.5*UP, 3*RIGHT+0.5*UP),
            ),
            (
                Line(4*RIGHT+4*DOWN, RIGHT+2*UP),
                Line(4*DOWN+RIGHT, 2*UP+2*RIGHT)
            ),
        ]
        for lines in line_pairs:
            self.show_angle_preservation_between_lines(*lines)
            self.reset()

    def note_grid_lines(self):
        intersection_inputs = [
            complex(x, y)
            for x in np.arange(-5, 5, 0.5)
            for y in np.arange(0, 3, 0.5)
            if not (x <= 0 and y == 0)
        ]
        brackets = VGroup(*list(map(
            self.get_right_angle_bracket,
            intersection_inputs
        )))
        self.apply_function()
        self.wait()
        self.play(
            ShowCreation(brackets, run_time = 5),
            Animation(self.plane)
        )
        self.wait()

    def name_analytic(self):
        equiv = TextMobject("``Analytic'' $\\Leftrightarrow$ Angle-preserving")
        kind_of = TextMobject("...kind of")
        for text in equiv, kind_of:
            text.scale(1.2)
            text.add_background_rectangle()
        equiv.set_color(YELLOW)
        kind_of.set_color(RED)
        kind_of.next_to(equiv, RIGHT)
        VGroup(equiv, kind_of).next_to(ORIGIN, UP, buff = 1)

        self.play(Write(equiv))
        self.wait(2)
        self.play(Write(kind_of, run_time = 1))
        self.wait(2)

    def reset(self, faded = True):
        self.play(FadeOut(self.plane))
        self.add_transformable_plane()
        if faded:
            self.plane.fade()
        self.play(FadeIn(self.plane))

    def apply_function(self, **kwargs):
        if self.use_homotopy:
            self.apply_complex_homotopy(
                lambda z, t : z**(1+t),
                run_time = 5,
                **kwargs
            )
        else:
            self.apply_complex_function(
                lambda z : z**2,
                **kwargs
            )

    def show_angle_preservation_between_lines(self, *lines):
        R2_endpoints = [
            [l.get_start()[:2], l.get_end()[:2]]
            for l in lines
        ]
        R2_intersection_point = intersection(*R2_endpoints)
        intersection_point = np.array(list(R2_intersection_point) + [0])

        angle1, angle2 = [l.get_angle() for l in lines]
        arc = Arc(
            start_angle = angle1,
            angle = angle2-angle1,
            radius = 0.4,
            color = YELLOW
        )
        arc.shift(intersection_point)
        arc.insert_n_curves(10)
        arc.generate_target()
        input_z = complex(*arc.get_center()[:2])
        scale_factor = abs(2*input_z)
        arc.target.scale_about_point(1./scale_factor, intersection_point)
        arc.target.apply_complex_function(lambda z : z**2)

        angle_tex = TexMobject(
            "%d^\\circ"%abs(int((angle2-angle1)*180/np.pi))
        )
        angle_tex.set_color(arc.get_color())
        angle_tex.add_background_rectangle()
        self.put_angle_tex_next_to_arc(angle_tex, arc)
        angle_arrow = Arrow(
            angle_tex, arc,
            color = arc.get_color(),
            buff = 0.1,
        )
        angle_group = VGroup(angle_tex, angle_arrow)


        self.play(*list(map(ShowCreation, lines)))
        self.play(
            Write(angle_tex),
            ShowCreation(angle_arrow),
            ShowCreation(arc)
        )
        self.wait()

        self.play(FadeOut(angle_group))
        self.plane.add(*lines)
        self.apply_function(added_anims = [
            MoveToTarget(arc, run_time = 5)
        ])
        self.put_angle_tex_next_to_arc(angle_tex, arc)
        arrow = Arrow(angle_tex, arc, buff = 0.1)
        arrow.set_color(arc.get_color())
        self.play(
            Write(angle_tex),
            ShowCreation(arrow)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [arc, angle_tex, arrow])))

    def put_angle_tex_next_to_arc(self, angle_tex, arc):
        vect = arc.point_from_proportion(0.5)-interpolate(
            arc.points[0], arc.points[-1], 0.5
        )
        unit_vect = vect/get_norm(vect)
        angle_tex.move_to(arc.get_center() + 1.7*unit_vect)

    def get_right_angle_bracket(self, input_z):
        output_z = input_z**2
        derivative = 2*input_z
        rotation = np.log(derivative).imag

        brackets = VGroup(
            Line(RIGHT, RIGHT+UP),
            Line(RIGHT+UP, UP)
        )
        brackets.scale(0.15)
        brackets.set_stroke(width = 2)
        brackets.set_color(YELLOW)
        brackets.shift(0.02*UP) ##Why???
        brackets.rotate(rotation, about_point = ORIGIN)
        brackets.shift(self.z_to_point(output_z))
        return brackets

class AngleAtZeroDerivativePoints(IntroduceAnglePreservation):
    CONFIG = {
        "use_homotopy" : True
    }
    def construct(self):
        self.add_title()
        self.is_before_transformation = True
        self.add_transformable_plane()
        self.plane.fade()
        line = Line(3*LEFT+0.5*UP, 3*RIGHT+0.5*DOWN)
        self.show_angle_preservation_between_lines(
            line, line.copy().rotate(np.pi/5)
        )
        self.wait()

    def add_title(self):
        title = TexMobject("f(", "s", ")=", "s", "^2")
        title.set_color_by_tex("s", YELLOW)
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        title.add_background_rectangle()
        derivative = TexMobject("f'(0) = 0")
        derivative.set_color(RED)
        derivative.scale(1.2)
        derivative.add_background_rectangle()
        derivative.next_to(title, DOWN)

        self.add_foreground_mobjects(title, derivative)


    def put_angle_tex_next_to_arc(self, angle_tex, arc):
        IntroduceAnglePreservation.put_angle_tex_next_to_arc(
            self, angle_tex, arc
        )
        if not self.is_before_transformation:
            two_dot = TexMobject("2 \\times ")
            two_dot.set_color(angle_tex.get_color())
            two_dot.next_to(angle_tex, LEFT, buff = SMALL_BUFF)
            two_dot.add_background_rectangle()
            center = angle_tex.get_center()
            angle_tex.add_to_back(two_dot)
            angle_tex.move_to(center)
        else:
            self.is_before_transformation = False

class AnglePreservationAtAnyPairOfPoints(IntroduceAnglePreservation):
    def construct(self):
        self.add_transformable_plane()
        self.plane.fade()
        line_pairs = self.get_line_pairs()
        line_pair = line_pairs[0]
        for target_pair in line_pairs[1:]:
            self.play(Transform(
                line_pair, target_pair,
                run_time = 2,
                path_arc = np.pi
            ))
            self.wait()
        self.show_angle_preservation_between_lines(*line_pair)
        self.show_example_analytic_functions()

    def get_line_pairs(self):
        return list(it.starmap(VGroup, [
            (
                Line(3*DOWN, 3*LEFT+2*UP),
                Line(2*LEFT+DOWN, 3*UP+RIGHT)
            ),
            (
                Line(2*RIGHT+DOWN, 3*LEFT+2*UP),
                Line(LEFT+3*DOWN, 4*RIGHT+3*UP),
            ),
            (
                Line(LEFT+3*DOWN, LEFT+3*UP),
                Line(5*LEFT+UP, 3*RIGHT+UP)
            ),
            (
                Line(4*RIGHT+3*DOWN, RIGHT+2*UP),
                Line(3*DOWN+RIGHT, 2*UP+2*RIGHT)
            ),
        ]))

    def show_example_analytic_functions(self):
        words = TextMobject("Examples of analytic functions:")
        words.shift(2*UP)
        words.set_color(YELLOW)
        words.add_background_rectangle()
        words.next_to(UP, UP).to_edge(LEFT)
        functions = TextMobject(
            "$e^x$, ",
            "$\\sin(x)$, ",
            "any polynomial, "
            "$\\log(x)$, ",
            "\\dots",
        )
        functions.next_to(ORIGIN, UP).to_edge(LEFT)
        for function in functions:
            function.add_to_back(BackgroundRectangle(function))

        self.play(Write(words))
        for function in functions:
            self.play(FadeIn(function))
        self.wait()

class NoteZetaFunctionAnalyticOnRightHalf(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
    }
    def construct(self):
        self.add_title()
        self.add_transformable_plane(animate = False)
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.apply_zeta_function()
        self.note_right_angles()

    def add_title(self):
        title = TexMobject(
            "\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}"
        )
        title[2].set_color(YELLOW)
        title[-1].set_color(YELLOW)
        title.add_background_rectangle()
        title.to_corner(UP+LEFT)
        self.add_foreground_mobjects(title)

    def note_right_angles(self):
        intersection_inputs = [
            complex(x, y)
            for x in np.arange(1+2./16, 1.4, 1./16)
            for y in np.arange(-0.5, 0.5, 1./16)
            if abs(y) > 1./16
        ]
        brackets = VGroup(*list(map(
            self.get_right_angle_bracket,
            intersection_inputs
        )))
        self.play(ShowCreation(brackets, run_time = 3))
        self.wait()

    def get_right_angle_bracket(self, input_z):
        output_z = zeta(input_z)
        derivative = d_zeta(input_z)
        rotation = np.log(derivative).imag

        brackets = VGroup(
            Line(RIGHT, RIGHT+UP),
            Line(RIGHT+UP, UP)
        )
        brackets.scale(0.1)
        brackets.set_stroke(width = 2)
        brackets.set_color(YELLOW)
        brackets.rotate(rotation, about_point = ORIGIN)
        brackets.shift(self.z_to_point(output_z))
        return brackets

class InfiniteContinuousJigsawPuzzle(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
    }
    def construct(self):
        self.set_stage()
        self.add_title()
        self.show_jigsaw()
        self.name_analytic_continuation()

    def set_stage(self):
        self.plane = self.get_dense_grid()
        left_plane = self.get_reflected_plane()
        self.plane.add(left_plane)
        self.apply_zeta_function(run_time = 0)
        self.remove(left_plane)
        lines_per_piece = 5
        pieces = [
            VGroup(*left_plane[lines_per_piece*i:lines_per_piece*(i+1)])
            for i in range(len(list(left_plane))/lines_per_piece)
        ]
        random.shuffle(pieces)
        self.pieces = pieces

    def add_title(self):
        title = TextMobject("Infinite ", "continuous ", "jigsaw puzzle")
        title.scale(1.5)
        title.to_edge(UP)
        for word in title:
            word.add_to_back(BackgroundRectangle(word))
            self.play(FadeIn(word))
        self.wait()
        self.add_foreground_mobjects(title)
        self.title = title

    def show_jigsaw(self):
        for piece in self.pieces:
            self.play(FadeIn(piece, run_time = 0.5))
        self.wait()

    def name_analytic_continuation(self):
        words = TextMobject("``Analytic continuation''")
        words.set_color(YELLOW)
        words.scale(1.5)
        words.next_to(self.title, DOWN, buff = LARGE_BUFF)
        words.add_background_rectangle()
        self.play(Write(words))
        self.wait()

class ThatsHowZetaIsDefined(TeacherStudentsScene):
    def construct(self):
        self.add_zeta_definition()
        self.teacher_says("""
            So that's how
            $\\zeta(s)$ is defined
        """)
        self.change_student_modes(*["hooray"]*3)
        self.random_blink(2)

    def add_zeta_definition(self):
        zeta = TexMobject(
            "\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}"
        )
        VGroup(zeta[2], zeta[-1]).set_color(YELLOW)
        zeta.to_corner(UP+LEFT)
        self.add(zeta)

class ManyIntersectingLinesPreZeta(ZetaTransformationScene):
    CONFIG = {
        "apply_zeta" : False,
        "lines_center" : RIGHT,
        "nudge_size" : 0.9,
        "function" : zeta,
        "angle" : np.pi/5,
        "arc_scale_factor" : 0.3,
        "shift_directions" : [LEFT, RIGHT],
    }
    def construct(self):
        self.establish_plane()
        self.add_title()

        line = Line(DOWN+2*LEFT, UP+2*RIGHT)
        lines = VGroup(line, line.copy().rotate(self.angle))
        arc = Arc(start_angle = line.get_angle(), angle = self.angle)
        arc.scale(self.arc_scale_factor)
        arc.set_color(YELLOW)
        lines.add(arc)
        # lines.set_stroke(WHITE, width = 5)
        lines.shift(self.lines_center + self.nudge_size*RIGHT)

        if self.apply_zeta:
            self.apply_zeta_function(run_time = 0)
            lines.set_stroke(width = 0)

        added_anims = self.get_modified_line_anims(lines)
        for vect in self.shift_directions:
            self.play(
                ApplyMethod(lines.shift, 2*self.nudge_size*vect, path_arc = np.pi),
                *added_anims,
                run_time = 3
            )

    def establish_plane(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.add_reflected_plane()
        self.plane.fade()


    def add_title(self):
        if self.apply_zeta:
            title = TextMobject("After \\\\ transformation")
        else:
            title = TextMobject("Before \\\\ transformation")
        title.add_background_rectangle()
        title.to_edge(UP)
        self.add_foreground_mobjects(title)

    def get_modified_line_anims(self, lines):
        return []

class ManyIntersectingLinesPostZeta(ManyIntersectingLinesPreZeta):
    CONFIG = {
        "apply_zeta" : True,
        # "anchor_density" : 5
    }
    def get_modified_line_anims(self, lines):
        n_inserted_points = 30
        new_lines = lines.copy()
        new_lines.set_stroke(width = 5)
        def update_new_lines(lines_to_update):
            transformed = lines.copy()
            self.prepare_for_transformation(transformed)
            transformed.apply_complex_function(self.function)
            transformed.make_smooth()
            transformed.set_stroke(width = 5)
            for start, end in zip(lines_to_update, transformed):
                if start.get_num_points() > 0:
                    start.points = np.array(end.points)
        return [UpdateFromFunc(new_lines, update_new_lines)]

class ManyIntersectingLinesPreSSquared(ManyIntersectingLinesPreZeta):
    CONFIG = {
        "x_min" : -int(FRAME_X_RADIUS),
        "apply_zeta" : False,
        "lines_center" : ORIGIN,
        "nudge_size" : 0.9,
        "function" : lambda z : z**2,
        "shift_directions" : [LEFT, RIGHT, UP, DOWN, DOWN+LEFT, UP+RIGHT],
    }
    def establish_plane(self):
        self.add_transformable_plane()
        self.plane.fade()

    def apply_zeta_function(self, **kwargs):
        self.apply_complex_function(self.function, **kwargs)

class ManyIntersectingLinesPostSSquared(ManyIntersectingLinesPreSSquared):
    CONFIG = {
        "apply_zeta" : True,
    }
    def get_modified_line_anims(self, lines):
        n_inserted_points = 30
        new_lines = lines.copy()
        new_lines.set_stroke(width = 5)
        def update_new_lines(lines_to_update):
            transformed = lines.copy()
            self.prepare_for_transformation(transformed)
            transformed.apply_complex_function(self.function)
            transformed.make_smooth()
            transformed.set_stroke(width = 5)
            for start, end in zip(lines_to_update, transformed):
                if start.get_num_points() > 0:
                    start.points = np.array(end.points)
        return [UpdateFromFunc(new_lines, update_new_lines)]

class ButWhatIsTheExensions(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            """
            But what exactly \\emph{is}
            that continuation?
            """,
            target_mode = "sassy"
        )
        self.change_student_modes("confused", "sassy", "confused")
        self.random_blink(2)
        self.teacher_says("""
            You're $\\$1{,}000{,}000$ richer
            if you can answer
            that fully
        """, target_mode = "shruggie")
        self.change_student_modes(*["pondering"]*3)
        self.random_blink(3)

class MathematiciansLookingAtFunctionEquation(Scene):
    def construct(self):
        equation = TexMobject(
            "\\zeta(s)",
            "= 2^s \\pi ^{s-1}",
            "\\sin\\left(\\frac{\\pi s}{2}\\right)",
            "\\Gamma(1-s)",
            "\\zeta(1-s)",
        )
        equation.shift(UP)

        mathy = Mathematician().to_corner(DOWN+LEFT)
        mathys = VGroup(mathy)
        for x in range(2):
            mathys.add(Mathematician().next_to(mathys))
        for mathy in mathys:
            mathy.change_mode("pondering")
            mathy.look_at(equation)

        self.add(mathys)
        self.play(Write(VGroup(*equation[:-1])))
        self.play(Transform(
            equation[0].copy(),
            equation[-1],
            path_arc = -np.pi/3,
            run_time = 2
        ))
        for mathy in mathys:
            self.play(Blink(mathy))
        self.wait()

class DiscussZeros(ZetaTransformationScene):
    def construct(self):
        self.establish_plane()
        self.ask_about_zeros()
        self.show_trivial_zeros()
        self.show_critical_strip()
        self.transform_bit_of_critical_line()
        self.extend_transformed_critical_line()

    def establish_plane(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.add_reflected_plane()
        self.plane.fade()

    def ask_about_zeros(self):
        dots = VGroup(*[
            Dot(
                (2+np.sin(12*alpha))*\
                rotate_vector(RIGHT, alpha+nudge)
            )
            for alpha in np.arange(3*np.pi/20, 2*np.pi, 2*np.pi/5)
            for nudge in [random.random()*np.pi/6]
        ])
        dots.set_color(YELLOW)
        q_marks = VGroup(*[
            TexMobject("?").next_to(dot, UP)
            for dot in dots
        ])
        arrows = VGroup(*[
            Arrow(dot, ORIGIN, buff = 0.2, tip_length = 0.1)
            for dot in dots
        ])
        question = TextMobject("Which numbers go to $0$?")
        question.add_background_rectangle()
        question.to_edge(UP)

        for mob in dots, arrows, q_marks:
            self.play(ShowCreation(mob))
        self.play(Write(question))
        self.wait(2)
        dots.generate_target()
        for i, dot in enumerate(dots.target):
            dot.move_to(2*(i+1)*LEFT)
        self.play(
            FadeOut(arrows),
            FadeOut(q_marks),
            FadeOut(question),
            MoveToTarget(dots),
        )
        self.wait()
        self.dots = dots

    def show_trivial_zeros(self):
        trivial_zero_words = TextMobject("``Trivial'' zeros")
        trivial_zero_words.next_to(ORIGIN, UP)
        trivial_zero_words.to_edge(LEFT)

        randy = Randolph().flip()
        randy.to_corner(DOWN+RIGHT)
        bubble = randy.get_bubble()
        bubble.set_fill(BLACK, opacity = 0.8)
        bubble.write("$1^1 + 2^2 + 3^2 + \\cdots = 0$")
        bubble.resize_to_content()
        bubble.pin_to(randy)

        self.plane.save_state()
        self.dots.save_state()
        for dot in self.dots.target:
            dot.move_to(ORIGIN)
        self.apply_zeta_function(
            added_anims = [MoveToTarget(self.dots, run_time = 3)],
            run_time = 3
        )
        self.wait(3)
        self.play(
            self.plane.restore,
            self.plane.make_smooth,
            self.dots.restore,
            run_time = 2
        )
        self.remove(*self.get_mobjects_from_last_animation())
        self.plane.restore()
        self.dots.restore()
        self.add(self.plane, self.dots)

        self.play(Write(trivial_zero_words))
        self.wait()
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(randy))
        self.wait()
        self.play(Blink(randy))
        self.play(*list(map(FadeOut, [
            randy, bubble, bubble.content, trivial_zero_words
        ])))

    def show_critical_strip(self):
        strip = Rectangle(
            height = FRAME_HEIGHT,
            width = 1
        )
        strip.next_to(ORIGIN, RIGHT, buff = 0)
        strip.set_stroke(width = 0)
        strip.set_fill(YELLOW, opacity = 0.3)
        name = TextMobject("Critical strip")
        name.add_background_rectangle()
        name.next_to(ORIGIN, LEFT)
        name.to_edge(UP)
        arrow = Arrow(name.get_bottom(), 0.5*RIGHT+UP)
        primes = TexMobject("2, 3, 5, 7, 11, 13, 17, \\dots")
        primes.to_corner(UP+RIGHT)
        # photo = Square()
        photo = ImageMobject("Riemann", invert = False)
        photo.set_width(5)
        photo.to_corner(UP+LEFT)
        new_dots = VGroup(*[
            Dot(0.5*RIGHT + y*UP)
            for y in np.linspace(-2.5, 3.2, 5)
        ])
        new_dots.set_color(YELLOW)
        critical_line = Line(
            0.5*RIGHT+FRAME_Y_RADIUS*DOWN,
            0.5*RIGHT+FRAME_Y_RADIUS*UP,
            color = YELLOW
        )

        self.give_dots_wandering_anims()

        self.play(FadeIn(strip), *self.get_dot_wandering_anims())
        self.play(
            Write(name, run_time = 1),
            ShowCreation(arrow),
            *self.get_dot_wandering_anims()
        )
        self.play(*self.get_dot_wandering_anims())
        self.play(
            FadeIn(primes),
            *self.get_dot_wandering_anims()
        )
        for x in range(7):
            self.play(*self.get_dot_wandering_anims())
        self.play(
            GrowFromCenter(photo),
            FadeOut(name),
            FadeOut(arrow),
            *self.get_dot_wandering_anims()
        )
        self.play(Transform(self.dots, new_dots))
        self.play(ShowCreation(critical_line))
        self.wait(3)
        self.play(
            photo.shift, 7*LEFT,
            *list(map(FadeOut, [
            primes, self.dots, strip
            ]))
        )
        self.remove(photo)
        self.critical_line = critical_line

    def give_dots_wandering_anims(self):
        def func(t):
            result = (np.sin(6*2*np.pi*t) + 1)*RIGHT/2
            result += 3*np.cos(2*2*np.pi*t)*UP
            return result

        self.wandering_path = ParametricFunction(func)
        for i, dot in enumerate(self.dots):
            dot.target = dot.copy()
            q_mark = TexMobject("?")
            q_mark.next_to(dot.target, UP)
            dot.target.add(q_mark)
            dot.target.move_to(self.wandering_path.point_from_proportion(
                (float(2+2*i)/(4*len(list(self.dots))))%1
            ))
        self.dot_anim_count = 0

    def get_dot_wandering_anims(self):
        self.dot_anim_count += 1
        if self.dot_anim_count == 1:
            return list(map(MoveToTarget, self.dots))
        denom = 4*(len(list(self.dots)))
        def get_rate_func(index):
            return lambda t : (float(self.dot_anim_count + 2*index + t)/denom)%1
        return [
            MoveAlongPath(
                dot, self.wandering_path,
                rate_func = get_rate_func(i)
            )
            for i, dot in enumerate(self.dots)
        ]

    def transform_bit_of_critical_line(self):
        self.play(
            self.plane.scale, 0.8,
            self.critical_line.scale, 0.8,
            rate_func = there_and_back,
            run_time = 2
        )
        self.wait()
        self.play(
            self.plane.set_stroke, GREY, 1,
            Animation(self.critical_line)
        )
        self.plane.add(self.critical_line)
        self.apply_zeta_function()
        self.wait(2)
        self.play(
            self.plane.fade,
            Animation(self.critical_line)
        )

    def extend_transformed_critical_line(self):
        def func(t):
            z = zeta(complex(0.5, t))
            return z.real*RIGHT + z.imag*UP
        full_line = VGroup(*[
            ParametricFunction(func, t_min = t0, t_max = t0+1)
            for t0 in range(100)
        ])
        full_line.set_color_by_gradient(
            YELLOW, BLUE, GREEN, RED, YELLOW, BLUE, GREEN, RED,
        )
        self.play(ShowCreation(full_line, run_time = 20, rate_func=linear))
        self.wait()

class AskAboutRelationToPrimes(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            Whoa!  Where the heck
            do primes come in here?
        """, target_mode = "confused")
        self.random_blink(3)
        self.teacher_says("""
            Perhaps in a
            different video.
        """, target_mode = "hesitant")
        self.random_blink(3)

class HighlightCriticalLineAgain(DiscussZeros):
    def construct(self):
        self.establish_plane()
        title = TexMobject("\\zeta(", "s", ") = 0")
        title.set_color_by_tex("s", YELLOW)
        title.add_background_rectangle()
        title.to_corner(UP+LEFT)
        self.add(title)

        strip = Rectangle(
            height = FRAME_HEIGHT,
            width = 1
        )
        strip.next_to(ORIGIN, RIGHT, buff = 0)
        strip.set_stroke(width = 0)
        strip.set_fill(YELLOW, opacity = 0.3)
        line = Line(
            0.5*RIGHT+FRAME_Y_RADIUS*UP,
            0.5*RIGHT+FRAME_Y_RADIUS*DOWN,
            color = YELLOW
        )
        randy = Randolph().to_corner(DOWN+LEFT)
        million = TexMobject("\\$1{,}000{,}000")
        million.set_color(GREEN_B)
        million.next_to(ORIGIN, UP+LEFT)
        million.shift(2*LEFT)
        arrow1 = Arrow(million.get_right(), line.get_top())
        arrow2 = Arrow(million.get_right(), line.get_bottom())

        self.add(randy, strip)
        self.play(Write(million))
        self.play(
            randy.change_mode, "pondering",
            randy.look_at, line.get_top(),
            ShowCreation(arrow1),
            run_time = 3
        )
        self.play(
            randy.look_at, line.get_bottom(),
            ShowCreation(line),
            Transform(arrow1, arrow2)
        )
        self.play(FadeOut(arrow1))
        self.play(Blink(randy))
        self.wait()
        self.play(randy.look_at, line.get_center())
        self.play(randy.change_mode, "confused")
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change_mode, "pondering")
        self.wait()

class DiscussSumOfNaturals(Scene):
    def construct(self):
        title = TexMobject(
            "\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}"
        )
        VGroup(title[2], title[-1]).set_color(YELLOW)
        title.to_corner(UP+LEFT)

        neg_twelfth, eq, zeta_neg_1, sum_naturals = equation = TexMobject(
            "-\\frac{1}{12}",
            "=",
            "\\zeta(-1)",
            "= 1 + 2 + 3 + 4 + \\cdots"
        )
        neg_twelfth.set_color(GREEN_B)
        VGroup(*zeta_neg_1[2:4]).set_color(YELLOW)
        q_mark = TexMobject("?").next_to(sum_naturals[0], UP)
        q_mark.set_color(RED)
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        analytic_continuation = TextMobject("Analytic continuation")
        analytic_continuation.next_to(title, RIGHT, 3*LARGE_BUFF)

        sum_to_zeta = Arrow(title.get_corner(DOWN+RIGHT), zeta_neg_1)
        sum_to_ac = Arrow(title.get_right(), analytic_continuation)
        ac_to_zeta = Arrow(analytic_continuation.get_bottom(), zeta_neg_1.get_top())
        cross = TexMobject("\\times")
        cross.scale(2)
        cross.set_color(RED)
        cross.rotate(np.pi/6)
        cross.move_to(sum_to_zeta.get_center())

        brace = Brace(VGroup(zeta_neg_1, sum_naturals))
        words = TextMobject(
            "If not equal, at least connected",
            "\\\\(see links in description)"
        )
        words.next_to(brace, DOWN)

        self.add(neg_twelfth, eq, zeta_neg_1, randy, title)
        self.wait()
        self.play(
            Write(sum_naturals),
            Write(q_mark),
            randy.change_mode, "confused"
        )
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change_mode, "angry")
        self.play(
            ShowCreation(sum_to_zeta),
            Write(cross)
        )
        self.play(Blink(randy))
        self.wait()
        self.play(
            Transform(sum_to_zeta, sum_to_ac),
            FadeOut(cross),
            Write(analytic_continuation),
            randy.change_mode, "pondering",
            randy.look_at, analytic_continuation,
        )
        self.play(ShowCreation(ac_to_zeta))
        self.play(Blink(randy))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(words[0]),
            randy.look_at, words[0],
        )
        self.wait()
        self.play(FadeIn(words[1]))
        self.play(Blink(randy))
        self.wait()

class InventingMathPreview(Scene):
    def construct(self):
        rect = Rectangle(height = 9, width = 16)
        rect.set_height(4)
        title = TextMobject("What does it feel like to invent math?")
        title.next_to(rect, UP)
        sum_tex = TexMobject("1+2+4+8+\\cdots = -1")
        sum_tex.set_width(rect.get_width()-1)

        self.play(
            ShowCreation(rect),
            Write(title)
        )
        self.play(Write(sum_tex))
        self.wait()

class FinalAnimationTease(Scene):
    def construct(self):
        morty = Mortimer().shift(2*(DOWN+RIGHT))
        bubble = morty.get_bubble(SpeechBubble)
        bubble.write("""
            Want to know what
            $\\zeta'(s)$ looks like?
        """)

        self.add(morty)
        self.play(
            morty.change_mode, "hooray",
            morty.look_at, bubble.content,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait()

class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons" : [
            "CrypticSwarm",
            "Ali Yahya",
            "Damion Kistler",
            "Juan Batiz-Benet",
            "Yu Jun",
            "Othman Alikhan",
            "Markus Persson",
            "Joseph John Cox",
            "Luc Ritchie",
            "Shimin Kuang",
            "Einar Johansen",
            "Rish Kundalia",
            "Achille Brighton",
            "Kirk Werklund",
            "Ripta Pasay",
            "Felipe Diniz",
        ]
    }
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        n_patrons = len(self.specific_patrons)
        special_thanks = TextMobject("Special thanks to:")
        special_thanks.set_color(YELLOW)
        special_thanks.shift(3*UP)
        patreon_logo = ImageMobject("patreon", invert = False)
        patreon_logo.set_height(1.5)
        patreon_logo.next_to(special_thanks, DOWN)

        left_patrons = VGroup(*list(map(TextMobject,
            self.specific_patrons[:n_patrons/2]
        )))
        right_patrons = VGroup(*list(map(TextMobject,
            self.specific_patrons[n_patrons/2:]
        )))
        for patrons, vect in (left_patrons, LEFT), (right_patrons, RIGHT):
            patrons.arrange(DOWN, aligned_edge = LEFT)
            patrons.next_to(special_thanks, DOWN)
            patrons.to_edge(vect, buff = LARGE_BUFF)

        self.add(patreon_logo)
        self.play(morty.change_mode, "gracious")
        self.play(Write(special_thanks, run_time = 1))
        self.play(
            Write(left_patrons),
            morty.look_at, left_patrons
        )
        self.play(
            Write(right_patrons),
            morty.look_at, right_patrons
        )
        self.play(Blink(morty))
        for patrons in left_patrons, right_patrons:
            for index in 0, -1:
                self.play(morty.look_at, patrons[index])
                self.wait()

class CreditTwo(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        morty.to_edge(RIGHT)

        brother = PiCreature(color = GOLD_E)
        brother.next_to(morty, LEFT)
        brother.look_at(morty.eyes)

        headphones = Headphones(height = 1)
        headphones.move_to(morty.eyes, aligned_edge = DOWN)
        headphones.shift(0.1*DOWN)

        url = TextMobject("www.audible.com/3blue1brown")
        url.to_corner(UP+RIGHT, buff = LARGE_BUFF)

        self.add(morty)
        self.play(Blink(morty))
        self.play(
            FadeIn(headphones),
            Write(url),
            Animation(morty)
        )
        self.play(morty.change_mode, "happy")
        for x in range(4):
            self.wait()
            self.play(Blink(morty))
        self.wait()
        self.play(
            FadeIn(brother),
            morty.look_at, brother.eyes
        )
        self.play(brother.change_mode, "surprised")
        self.play(Blink(brother))
        self.wait()
        self.play(
            morty.look, LEFT,
            brother.change_mode, "happy",
            brother.look, LEFT
        )
        for x in range(10):
            self.play(Blink(morty))
            self.wait()
            self.play(Blink(brother))
            self.wait()

class FinalAnimation(ZetaTransformationScene):
    CONFIG = {
        "min_added_anchors" : 100,
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.add_reflected_plane()
        title = TexMobject("s", "\\to \\frac{d\\zeta}{ds}(", "s", ")")
        title.set_color_by_tex("s", YELLOW)
        title.add_background_rectangle()
        title.scale(1.5)
        title.to_corner(UP+LEFT)

        self.play(Write(title))
        self.add_foreground_mobjects(title)
        self.wait()
        self.apply_complex_function(d_zeta, run_time = 8)
        self.wait()

class Thumbnail(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 35
    }
    def construct(self):
        self.y_min = -4
        self.y_max = 4
        self.x_min = 1
        self.x_max = int(FRAME_X_RADIUS+2)
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.add_reflected_plane()
        # self.apply_zeta_function()
        self.plane.set_stroke(width = 4)

        div_sum = TexMobject("-\\frac{1}{12} = ", "1+2+3+4+\\cdots")
        div_sum.set_width(FRAME_WIDTH-1)
        div_sum.to_edge(DOWN)
        div_sum.set_color(YELLOW)
        div_sum.set_background_stroke(width=8)
        # for mob in div_sum.submobjects:
        #     mob.add_to_back(BackgroundRectangle(mob))

        zeta = TexMobject("\\zeta(s)")
        zeta.set_height(FRAME_Y_RADIUS-1)
        zeta.to_corner(UP+LEFT)

        million = TexMobject("\\$1{,}000{,}000")
        million.set_width(FRAME_X_RADIUS+1)
        million.to_edge(UP+RIGHT)
        million.set_color(GREEN_B)
        million.set_background_stroke(width=8)

        self.add(div_sum, million, zeta)


class ZetaPartialSums(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
        "num_partial_sums" : 12,
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.prepare_for_transformation(self.plane)

        N_list = [2**k for k in range(self.num_partial_sums)]
        sigma = TexMobject(
            "\\sum_{n = 1}^N \\frac{1}{n^s}"
        )
        sigmas = []
        for N in N_list + ["\\infty"]:
            tex = TexMobject(str(N))
            tex.set_color(YELLOW)
            new_sigma = sigma.copy()
            top = new_sigma[0]
            tex.move_to(top, DOWN)
            new_sigma.remove(top)
            new_sigma.add(tex)
            new_sigma.to_corner(UP+LEFT)
            sigmas.append(new_sigma)

        def get_partial_sum_func(n_terms):
            return lambda s : sum([1./(n**s) for n in range(1, n_terms+1)])
        interim_planes = [
            self.plane.copy().apply_complex_function(
                get_partial_sum_func(N)
            )
            for N in N_list
        ]
        interim_planes.append(self.plane.copy().apply_complex_function(zeta))
        symbol = VGroup(TexMobject("s"))
        symbol.scale(2)
        symbol.set_color(YELLOW)
        symbol.to_corner(UP+LEFT)
        for plane, sigma in zip(interim_planes, sigmas):
            self.play(
                Transform(self.plane, plane),
                Transform(symbol, sigma)
            )
            self.wait()
