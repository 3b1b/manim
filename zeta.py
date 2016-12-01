from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

import mpmath
mpmath.mp.dps = 7


def zeta(z):
    try:
        return np.complex(mpmath.zeta(z))
    except:
        return np.complex(10*SPACE_WIDTH, 0)

class ComplexTransformationScene(Scene):
    CONFIG = {
        "plane_config" : {
            "x_line_frequency" : 1,
            "y_line_frequency" : 1,
            "secondary_line_ratio" : 1,
        },
        "x_min" : -int(SPACE_WIDTH),
        "x_max" : int(SPACE_WIDTH),
        "y_min" : -SPACE_HEIGHT,
        "y_max" : SPACE_HEIGHT,
        "vert_start_color" : MAROON_B,
        "vert_end_color" : RED,
        "horiz_start_color" : GREEN_B,
        "horiz_end_color" : YELLOW,
        "num_anchors_to_add_per_line" : 50,
        "thincken_lines_after_transformation" : False,
        "default_apply_complex_function_kwargs" : {
            "run_time" : 5,
        }
    }
    def setup(self):
        self.foreground_mobjects = []
        self.transformable_mobjects = []
        self.add_background_plane()

    def add_foreground_mobject(self, mobject):
        self.add_foreground_mobjects(mobject)

    def add_transformable_mobjects(self, *mobjects):
        self.transformable_mobjects += list(mobjects)
        self.add(*mobjects)

    def add_foreground_mobjects(self, *mobjects):
        self.foreground_mobjects += list(mobjects)
        Scene.add(self, *mobjects)

    def add(self, *mobjects):
        Scene.add(self, *list(mobjects)+self.foreground_mobjects)

    def play(self, *animations, **kwargs):
        Scene.play(
            self,
            *list(animations)+map(Animation, self.foreground_mobjects),
            **kwargs
        )

    def add_background_plane(self):
        background = NumberPlane().fade()
        real_labels = VGroup(*[
            TexMobject(str(x)).shift(x*RIGHT)
            for x in range(int(self.x_min), int(self.x_max)+1)
        ])
        imag_labels = VGroup(*[
            TexMobject("%di"%y).shift(y*UP)
            for y in range(int(self.y_min), int(self.y_max)+1)
            if y != 0
        ])
        for labels in real_labels, imag_labels:
            for label in labels:
                label.scale_in_place(0.5)
                label.next_to(label.get_center(), DOWN+LEFT, buff = SMALL_BUFF)
                label.add_background_rectangle()
            background.add(labels)
        self.real_labels = real_labels
        self.imag_labels = imag_labels
        self.add(background)

    def add_transformable_plane(self, animate = False):
        self.plane_config.update({
            "x_radius" : (self.x_max - self.x_min)/2,
            "y_radius" : (self.y_max - self.y_min)/2,
        })
        plane = NumberPlane(**self.plane_config)
        plane.shift(
            (self.x_max+self.x_min)*RIGHT/2,
            (self.y_max+self.y_min)*UP/2,
        )
        self.paint_plane(plane)
        if animate:
            self.play(ShowCreation(plane, run_time = 2))
        else:
            self.add(plane)
        self.plane = plane            

    def add_points_to_plane(self, plane):
        #TODO
        plane.prepare_for_nonlinear_transform(
            self.num_anchors_to_add_per_line
        )

    def paint_plane(self, plane):
        for lines in plane.main_lines, plane.secondary_lines:
            lines.gradient_highlight(
                self.vert_start_color,
                self.vert_end_color,
                self.horiz_start_color,
                self.horiz_end_color,
            )
        plane.axes.gradient_highlight(
            self.horiz_start_color,
            self.vert_start_color
        )
        
    def apply_complex_function(self, func, **kwargs):
        transform_kwargs = dict(self.default_apply_complex_function_kwargs)
        transform_kwargs.update(kwargs)

        plane = self.plane
        self.add_points_to_plane(plane)
        transformer = VGroup(
            plane, *self.transformable_mobjects
        )
        transformer.generate_target()
        transformer.target.apply_complex_function(func)
        for mob in transformer.target[0].family_members_with_points():
            mob.make_smooth()
            if mob.get_stroke_width() == 1 and self.thincken_lines_after_transformation:
                mob.set_stroke(width = 2)
        self.play(
            MoveToTarget(transformer),
            **transform_kwargs
        )

class ZetaTransformationScene(ComplexTransformationScene):
    CONFIG = {
        "num_anchors_to_add_per_line" : 300,
        "thincken_lines_after_transformation" : True,
        "default_apply_complex_function_kwargs" : {
            "submobject_mode" : "lagged_start",
            "run_time" : 8,
        }
    }
    def add_extra_plane_lines_for_zeta(self, step_size = 1./16, animate = False):
        epsilon = 0.1
        vert_lines = VGroup(*[
            Line(
                self.y_min*UP,
                self.y_max*UP,
            ).shift(x*RIGHT)
            for x in np.arange(max(0, self.x_min), 2, step_size)
            if abs(x) > epsilon
        ])
        vert_lines.gradient_highlight(
            self.vert_start_color, self.vert_end_color
        )
        horiz_lines = VGroup(*[
            Line(
                self.x_min*RIGHT,
                self.x_max*RIGHT,
            ).shift(y*UP)
            for y in np.arange(-1, 1, step_size)
            if abs(y) > epsilon
        ])
        horiz_lines.gradient_highlight(
            self.horiz_start_color, self.horiz_end_color
        )
        for lines in horiz_lines, vert_lines:
            lines.set_stroke(width = 1)
        if animate:
            self.play(*[
                ShowCreation(lines)
                for lines in vert_lines, horiz_lines
            ])
        self.plane.add(vert_lines, horiz_lines)
        self.add(self.plane)

    def apply_zeta_function(self, **kwargs):
        transform_kwargs = dict(self.default_apply_complex_function_kwargs)
        transform_kwargs.update(kwargs)
        self.apply_complex_function(zeta, **kwargs)

class TestZetaOnFullPlane(ZetaTransformationScene):
    CONFIG = {
        "num_anchors_to_add_per_line" : 300,
    }
    def construct(self):
        self.add_transformable_plane(animate = True)
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.dither()
        self.apply_zeta_function()
        self.dither(3)

class TestZetaOnHalfPlane(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
    }
    def construct(self):
        self.add_transformable_plane(animate = True)
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.apply_zeta_function()
        self.dither(3)

######################

class IntroduceZeta(ZetaTransformationScene):
    CONFIG = {
        "num_anchors_to_add_per_line" : 300,
        "default_apply_complex_function_kwargs" : {
            "submobject_mode" : "lagged_start",
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
        func_mob.arrange_submobjects(RIGHT, buff = 0)
        for submob in func_mob:
            submob.add_background_rectangle()
        func_mob.next_to(title, DOWN)

        randy = Randolph().flip()
        randy.to_corner(DOWN+RIGHT)

        self.add_foreground_mobjects(title, func_mob)
        self.add_transformable_plane(animate = True)
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.dither()
        self.apply_zeta_function()
        self.dither(2)
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, func_mob,
        )
        self.play(Blink(randy))
        self.dither()

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
            TexMobject("\\$1{,}000{,}000").gradient_highlight(GREEN_B, GREEN_D),
            TexMobject("\\zeta(s) = 0")
        )
        mercenary_thought.arrange_submobjects(DOWN)
        divergent_sum = VGroup(
            TexMobject("1+2+3+4+\\cdots = -\\frac{1}{12}"),
            TexMobject("\\zeta(-1) = -\\frac{1}{12}")
        )
        divergent_sum.arrange_submobjects(DOWN)
        divergent_sum[0].gradient_highlight(YELLOW, MAROON_B)

        #Thoughts
        self.play(*it.chain(*[
            [pi.change_mode, "pondering", pi.look_at, func_mob]
            for pi in self.get_everyone()
        ]))
        self.random_blink()
        self.student_thinks(
            mercenary_thought, student_index = 2,
            target_mode = "surprised",
        )
        student = self.get_students()[2]
        self.random_blink()
        self.dither(2)
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
            for pi in self.get_everyone()
        ]))
        self.dither()
        self.random_blink()

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
        self.dither(2)
        self.random_blink()
        self.dither()

class PreviewZetaAndContinuation(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
        "num_anchors_to_add_per_line" : 300,
        "default_apply_complex_function_kwargs" : {
            "run_time" : 4,
        }
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        reflected_plane = self.plane.copy()
        reflected_plane.rotate(np.pi, UP, about_point = RIGHT)
        reflected_plane.prepare_for_nonlinear_transform(self.num_anchors_to_add_per_line)
        for mob in reflected_plane.family_members_with_points():
            mob.highlight(
                Color(rgb = 1-0.5*color_to_rgb(mob.get_color()))
            )
            mob.set_stroke(width = 2)

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
            mob[1].highlight(YELLOW)
            mob.to_corner(UP+LEFT, buff = 0.7)
            mob.add_background_rectangle()

        self.remove(self.plane)
        self.play(Write(titles[0], run_time = 2))
        self.add_foreground_mobjects(titles[0])
        self.play(FadeIn(self.plane))
        self.apply_zeta_function()
        reflected_plane.apply_complex_function(zeta)
        reflected_plane.make_smooth()
        self.dither()
        self.play(Transform(*titles))
        self.dither()
        self.play(ShowCreation(
            reflected_plane,
            submobject_mode = "all_at_once",
            run_time = 2
        ))
        self.dither()

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
        complex_number_label[0].highlight(x_line.get_color())
        complex_number_label[2].highlight(y_line.get_color())
        complex_number_label.next_to(dot, UP)

        text = VGroup(
            TextMobject("Assumed knowledge:"),
            TextMobject("1) What complex numbers are."),
            TextMobject("2) How to work with them."),
            TextMobject("3) Maybe derivatives?"),
        )
        text.arrange_submobjects(DOWN, aligned_edge = LEFT)
        for words in text:
            words.add_background_rectangle()
        text[0].shift(LEFT)
        text[-1].highlight(PINK)
        text.to_corner(UP+LEFT)

        self.play(Write(text[0]))
        self.dither()
        self.play(FadeIn(text[1]))
        self.play(
            ShowCreation(x_line),
            ShowCreation(y_line),
            ShowCreation(VGroup(line, dot)),
            Write(complex_number_label),        
        )
        self.play(Write(text[2]))
        self.dither(2)
        self.play(Write(text[3]))
        self.dither()
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
        self.dither()

        for count, term in enumerate(sum_terms):
            self.play(FadeIn(term), run_time = 0.5)
            if count%2 == 0:
                self.dither()
        self.play(
            GrowFromCenter(brace),
            Write(sigma),
            self.pi_creature.change_mode, "pondering"
        )
        self.dither()

    def plug_in_two(self, zeta_def):
        two_def = self.get_definition("2")[0]
        number_line = NumberLine(
            x_min = 0, 
            x_max = 3,
            tick_frequency = 0.25,
            numbers_with_elongated_ticks = range(4),
            space_unit_to_num = 3,
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
            frac.highlight(line.get_color())
            frac.next_to(brace, UP, buff = SMALL_BUFF)
            if frac is fracs[-1]:
                frac.shift(0.5*RIGHT + 0.2*UP)
                arrow = Arrow(
                    frac.get_bottom(), brace.get_top(),
                    tip_length = 0.1, 
                    buff = 0.1
                )
                arrow.highlight(line.get_color())
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
        self.dither()
        self.play(ShowCreation(number_line))

        for frac, brace, line in zip(fracs, braces, lines):
            self.play(
                Write(frac),
                GrowFromCenter(brace),
                ShowCreation(line),
                run_time = 0.7
            )
            self.dither(0.7)
        self.dither()
        self.play(
            ShowCreation(VGroup(*lines[4:])),
            Write(dots)
        )
        self.dither()
        self.play(
            Write(pi_term),
            ShowCreation(VGroup(pi_arrow, pi_dot)),
            self.pi_creature.change_mode, "hooray"
        )
        self.dither()
        self.play(
            Write(approx),
            self.pi_creature.change_mode, "happy"
        )
        self.dither(3)
        self.play(*map(FadeOut, [
            fracs, pi_arrow, pi_dot, approx,
        ]))
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
            self.dither()

        arrow = Arrow(sum_terms.get_left(), sum_terms.get_right())
        arrow.next_to(sum_terms, DOWN)
        smaller_words = TextMobject("Getting smaller")
        smaller_words.next_to(arrow, DOWN)
        self.arrow, self.smaller_words = arrow, smaller_words

        self.dither()
        self.play(
            ShowCreation(arrow),
            Write(smaller_words)
        )
        self.change_mode("happy")
        self.dither(2)

    def plug_in_negative_values(self, zeta_def):
        zeta_s, sum_terms, brace, sigma = zeta_def
        arrow = self.arrow
        smaller_words = self.smaller_words
        bigger_words = TextMobject("Getting \\emph{bigger}?")

        #plug in -1
        self.transition_to_new_input(zeta_def, -1, "-\\frac{1}{12}")
        self.change_mode("confused")
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
            sigma.next_to, new_brace, UP
        )
        self.play(
            MoveToTarget(arrow),
            Transform(smaller_words, bigger_words),
            self.final_sum.next_to, sum_terms, RIGHT
        )
        self.dither(3)

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
        self.dither()
        self.change_mode("pleading")
        self.dither(2)

    def get_definition(self, input_string, input_color = YELLOW):
        inputs = VGroup()
        num_shown_terms = 4
        n_input_chars = len(input_string)

        zeta_s_eq = TexMobject("\\zeta(%s) = "%input_string)
        zeta_s_eq.to_edge(LEFT, buff = LARGE_BUFF)
        zeta_s_eq.shift(0.5*UP)
        inputs.add(*zeta_s_eq[2:2+n_input_chars])

        sum_terms = TexMobject(*it.chain(*zip(
            [
                "\\frac{1}{%d^{%s}}"%(d, input_string)
                for d in range(1, 1+num_shown_terms)
            ],
            it.cycle(["+"])
        )))
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

        inputs.highlight(input_color)
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
        VGroup(*lines[:4]).gradient_highlight(RED, GREEN_B)
        VGroup(*lines[4:]).gradient_highlight(GREEN_B, MAROON_B)

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
            color = MAROON_B
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























