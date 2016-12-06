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
    max_norm = SPACE_WIDTH
    try:
        return np.complex(mpmath.zeta(z))
    except:
        return np.complex(max_norm, 0)

def d_zeta(z):
    epsilon = 0.01
    return (zeta(z + epsilon) - zeta(z))/epsilon

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
        "post_transformation_storke_width" : None,
        "default_apply_complex_function_kwargs" : {
            "run_time" : 5,
        },
        "background_label_scale_val" : 0.5,
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
        background = NumberPlane(**self.plane_config).fade()
        real_labels = VGroup(*[
            TexMobject(str(x)).shift(
                background.num_pair_to_point((x, 0))
            )
            for x in range(-int(self.x_max), int(self.x_max))
        ])
        imag_labels = VGroup(*[
            TexMobject("%di"%y).shift(
                background.num_pair_to_point((0, y))
            )
            for y in range(-int(self.y_max), int(self.y_max))
            if y != 0
        ])
        for labels in real_labels, imag_labels:
            for label in labels:
                label.scale_in_place(self.background_label_scale_val)
                label.next_to(label.get_center(), DOWN+LEFT, buff = SMALL_BUFF)
                label.add_background_rectangle()
            background.add(labels)
        self.real_labels = real_labels
        self.imag_labels = imag_labels
        self.add(background)
        self.background = background

    def add_transformable_plane(self, animate = False):
        self.plane_config.update({
            "x_radius" : (self.x_max - self.x_min)/2.,
            "y_radius" : (self.y_max - self.y_min)/2.,
        })
        plane = NumberPlane(**self.plane_config)
        plane.shift(
            (self.x_max+self.x_min)*RIGHT/2.,
            (self.y_max+self.y_min)*UP/2.,
        )
        self.paint_plane(plane)
        if animate:
            self.play(ShowCreation(plane, run_time = 2))
        else:
            self.add(plane)
        self.plane = plane            

    def prepare_for_transformation(self, mob):
        if hasattr(mob, "prepare_for_nonlinear_transform"):
            mob.prepare_for_nonlinear_transform(
                self.num_anchors_to_add_per_line
            )
        #TODO...

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

    def z_to_point(self, z):
        return self.background.num_pair_to_point((z.real, z.imag))
        
    def get_transformer(self, **kwargs):
        transform_kwargs = dict(self.default_apply_complex_function_kwargs)
        transform_kwargs.update(kwargs)
        plane = self.plane
        self.prepare_for_transformation(plane)
        transformer = VGroup(
            plane, *self.transformable_mobjects
        )        
        return transformer, transform_kwargs


    def apply_complex_function(self, func, added_anims = [], **kwargs):
        transformer, transform_kwargs = self.get_transformer(**kwargs)
        transformer.generate_target()
        transformer.target.apply_complex_function(func)
        for mob in transformer.target[0].family_members_with_points():
            mob.make_smooth()
        if self.post_transformation_storke_width is not None:
            transformer.target.set_stroke(width = self.post_transformation_storke_width)
        self.play(
            MoveToTarget(transformer, **transform_kwargs),
            *added_anims
        )

    def apply_complex_homotopy(self, complex_homotopy, added_anims = [], **kwargs):
        transformer, transform_kwargs = self.get_transformer(**kwargs)
        def homotopy(x, y, z, t):
            output = complex_homotopy(complex(x, y), t)
            return (output.real, output.imag, z)

        self.play(
            SmoothedVectorizedHomotopy(
                homotopy, transformer,
                **transform_kwargs
            ),
            *added_anims
        )

class ZetaTransformationScene(ComplexTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
        "min_added_anchors" : 10,
        "max_added_anchors" : 300,
        "num_anchors_to_add_per_line" : 75,
        "post_transformation_storke_width" : 2,
        "default_apply_complex_function_kwargs" : {
            "run_time" : 5,
        },
        "x_min" : 1,
        "x_max" : int(SPACE_WIDTH+2),
        "extra_lines_x_min" : -2,
        "extra_lines_x_max" : 4,
        "extra_lines_y_min" : -2,
        "extra_lines_y_max" : 2,
    }
    def prepare_for_transformation(self, mob):
        for line in mob.family_members_with_points():
            #Find point of line cloest to 1 on C
            p1 = line.get_start()+LEFT
            p2 = line.get_end()+LEFT
            t = (-np.dot(p1, p2-p1))/(np.linalg.norm(p2-p1)**2)
            closest_to_one = interpolate(
                line.get_start(), line.get_end(), t
            )
            #See how big this line will become
            diameter = abs(zeta(complex(*closest_to_one[:2])))
            target_num_anchors = np.clip(
                int(self.anchor_density*np.pi*diameter),                
                self.min_added_anchors,
                self.max_added_anchors,
            )
            num_anchors = line.get_num_anchor_points()
            if num_anchors < target_num_anchors:
                line.insert_n_anchor_points(target_num_anchors-num_anchors)
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
        vert_lines.gradient_highlight(
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
        horiz_lines.gradient_highlight(
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
            mob.highlight(
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

class TestZetaOnFullPlane(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 15,
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.prepare_for_transformation(self.plane)
        print sum([
            mob.get_num_points()
            for mob in self.plane.family_members_with_points()
        ])
        print len(self.plane.family_members_with_points())
        self.show_frame()
        self.apply_zeta_function()
        self.dither()

class TestZetaOnHalfPlane(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
        "x_max" : int(SPACE_WIDTH+2)
    }
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
        self.dither(2)
        self.play(ShowCreation(line, run_time = 10))
        self.dither(3)

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
        func_mob.arrange_submobjects(RIGHT, buff = 0)
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
        reflected_plane.set_stroke(width = 2)
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
        # VGroup(*lines[:4]).gradient_highlight(RED, GREEN_B)
        # VGroup(*lines[4:]).gradient_highlight(GREEN_B, MAROON_B)
        VGroup(*lines[::2]).highlight(MAROON_B)
        VGroup(*lines[1::2]).highlight(RED)

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

class IgnoreNegatives(TeacherStudentsScene):
    def construct(self):
        definition = TexMobject("""
            \\zeta(s) = \\sum_{n=1}^{\\infty} \\frac{1}{n^s}
        """)
        VGroup(definition[2], definition[-1]).highlight(YELLOW)
        definition.to_corner(UP+LEFT)
        self.add(definition)
        brace = Brace(definition, DOWN)
        only_s_gt_1 = brace.get_text("""
            Only defined 
            for $s > 1$
        """)
        only_s_gt_1[-3].highlight(YELLOW)


        self.change_student_modes(*["confused"]*3)
        words = TextMobject(
            "Ignore $s \\le 1$ \\dots \\\\",
            "For now."
        )
        words[0][6].highlight(YELLOW)
        words[1].highlight(BLACK)
        self.teacher_says(words)
        self.play(words[1].highlight, WHITE)
        self.change_student_modes(*["happy"]*3)
        self.play(
            GrowFromCenter(brace),
            Write(only_s_gt_1),
            *it.chain(*[
                [pi.look_at, definition]
                for pi in self.get_everyone()
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
        photo.scale_to_fit_width(5)
        photo.next_to(name, DOWN, aligned_edge = LEFT)


        self.add(photo)
        self.play(Write(name))
        self.dither()

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
            dot.label.highlight(dot.get_color())

        self.play(
            ShowCreation(input_dot),
            Write(input_dot.label)
        )
        self.play(ShowCreation(arc))
        self.play(
            ShowCreation(output_dot),
            Write(output_dot.label)
        )
        self.dither()

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
            space_unit_to_num = 2, 
            tick_frequency = 0.5,
            numbers_with_elongated_ticks = range(-2, 3)
        )
        number_line.add_numbers()
        input_dot = Dot(number_line.number_to_point(2))
        input_dot.highlight(YELLOW)

        output_dot = Dot(number_line.number_to_point(np.pi**2/6))
        output_dot.highlight(self.output_color)

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
        self.dither()
        self.play(Transform(two, input_dot))
        self.remove(two)
        self.add(input_dot)
        self.play(ShowCreation(arc))
        self.play(ShowCreation(output_dot))
        self.play(Transform(output_dot.copy(), sum_term))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(sum_term)
        self.dither(2)
        self.play(
            ShowCreation(
                self.background,
                run_time = 2
            ),
            FadeOut(VGroup(arc, output_dot, number_line)),
            Animation(zeta),
            Animation(input_dot)
        )
        self.dither(2)

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
        input_label.highlight(YELLOW)
        input_label.next_to(input_dot.target, DOWN+RIGHT, buff = SMALL_BUFF)
        input_label.add_background_rectangle()
        input_label.save_state()
        input_label.replace(VGroup(*complex_zeta[1][2:5]))
        input_label.background_rectangle.scale_in_place(0.01)
        self.input_label = input_label

        self.play(Transform(self.zeta, complex_zeta))
        self.dither()
        self.play(
            input_label.restore,
            MoveToTarget(input_dot)
        )
        self.dither(2)

    def single_out_complex_exponent(self):
        frac_scale_factor = 1.2

        randy = Randolph()
        randy.to_corner()
        bubble = randy.get_bubble(height = 4)
        bubble.set_fill(BLACK, opacity = 1)

        pre_frac = self.zeta[2][2].copy()
        frac = VGroup(
            VectorizedPoint(pre_frac.get_left()),
            VGroup(*pre_frac[:3]),
            VectorizedPoint(pre_frac.get_right()),
            VGroup(*pre_frac[3:])
        )
        frac.generate_target()
        frac.target.scale(frac_scale_factor)
        bubble.add_content(frac.target)
        new_frac = TexMobject(
            "\\Big(", "\\frac{1}{2}", "\\Big)", "^{2+i}"
        )
        new_frac[-1].highlight(YELLOW)
        new_frac.scale(frac_scale_factor)
        new_frac.move_to(frac.target)
        new_frac.shift(LEFT+0.2*UP)

        words = TextMobject("Not repeated \\\\", " multiplication")
        words.scale(0.8)
        words.highlight(RED)
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
            self.dither(2)
            self.play(Blink(randy))
        self.play(
            Transform(words, new_words),
            randy.change_mode, "maybe"
        )
        self.dither()
        self.play(Blink(randy))
        self.play(randy.change_mode, "happy")
        self.dither()
        self.play(*map(FadeOut, [randy, bubble, frac, words]))

    def show_s_equals_two_lines(self):
        self.input_label.save_state()
        zeta = self.get_zeta_definition("2", "\\frac{\\pi^2}{6}")
        lines, output_dot = self.get_sum_lines(2)
        sum_terms = self.zeta[2][:-1:2]
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
        self.dither()
        transform_and_replace(pi_copy, output_dot)
        self.dither()

        self.lines = lines
        self.output_dot = output_dot

    def transition_to_spiril_sum(self):
        zeta = self.get_zeta_definition("2+i", "1.15 - 0.44i")
        zeta.scale_to_fit_width(2*SPACE_WIDTH-1)
        zeta.to_corner(UP+LEFT)
        lines, output_dot = self.get_sum_lines(complex(2, 1))

        self.play(
            self.input_dot.shift, 2*UP,
            self.input_label.restore,
        )
        self.dither()
        self.play(Transform(self.zeta, zeta))
        self.dither()
        self.play(
            Transform(self.lines, lines),
            Transform(self.output_dot, output_dot),
            run_time = 2,
            path_arc = -np.pi/6,
        )
        self.dither()

    def vary_complex_input(self):
        zeta = self.get_zeta_definition("s", "")
        zeta[3].highlight(BLACK)
        self.play(Transform(self.zeta, zeta))
        self.play(FadeOut(self.input_label))
        self.dither(2)
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
            self.dither()
        self.dither()

    def show_domain_of_convergence(self, opacity = 0.2):
        domain = Rectangle(
            width = SPACE_WIDTH-2,
            height = 2*SPACE_HEIGHT,
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = opacity,
        )
        domain.to_edge(RIGHT, buff = 0)
        anti_domain = Rectangle(
            width = SPACE_WIDTH+2,
            height = 2*SPACE_HEIGHT,
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
        domain_words.to_corner(UP+RIGHT, buff = 2*MED_BUFF)

        anti_domain_words = TextMobject("""
            Not so much...
        """)
        anti_domain_words.next_to(ORIGIN, LEFT, buff = LARGE_BUFF)
        anti_domain_words.shift(1.5*DOWN)

        self.play(FadeIn(domain))
        self.play(Write(domain_words))
        self.dither()
        self.play(FadeIn(anti_domain))
        self.play(Write(anti_domain_words))
        self.dither(2)
        self.play(*map(FadeOut, [
            anti_domain, anti_domain_words,
        ]))
        self.domain_words = domain_words

    def ask_about_visualizing_all(self):
        morty = Mortimer().flip()
        morty.scale(0.7)
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble("speech", height = 4)
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
        self.dither(3)
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, self.input_dot,
            *map(FadeOut, [
                bubble, bubble.content, self.domain_words
            ])
        )
        arrow = Arrow(self.input_dot, self.output_dot, buff = SMALL_BUFF)
        arrow.highlight(WHITE)
        self.play(ShowCreation(arrow))
        self.play(Blink(morty))
        self.dither()

    def get_zeta_definition(self, input_string, output_string, input_color = YELLOW):
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
        sum_terms.add(TexMobject("\\cdots").next_to(sum_terms[-1]))
        sum_terms.next_to(zeta_s_eq, RIGHT)
        for x in range(num_shown_terms):
            inputs.add(*sum_terms[2*x][-n_input_chars:])

        output = TexMobject("= \\," + output_string)
        output.next_to(sum_terms, RIGHT)
        output.highlight(self.output_color)

        inputs.highlight(input_color)
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
            Line(*map(self.z_to_point, z_pair))
            for z_pair in zip(power_sums, power_sums[1:])
        ])
        widths = np.linspace(line_thickness, 0, len(list(lines)))
        for line, width in zip(lines, widths):
            line.set_stroke(width = width)
        VGroup(*lines[::2]).highlight(MAROON_B)
        VGroup(*lines[1::2]).highlight(RED)

        final_dot = Dot(
            self.z_to_point(power_sums[-1]),
            color = self.output_color
        )

        return lines, final_dot

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
        VGroup(original[-1], split[1], split[3]).highlight(YELLOW)
        VGroup(original, split).shift(UP)
        real_part = VGroup(*split[:2])
        imag_part = VGroup(*split[2:])

        brace = Brace(real_part)
        we_understand = brace.get_text(
            "We understand this"
        )
        VGroup(brace, we_understand).highlight(GREEN_B)

        self.add(original)
        self.dither()
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
        self.dither()
        self.play(
            GrowFromCenter(brace),
            FadeIn(we_understand),
            real_part.highlight, GREEN_B
        )
        self.dither()
        self.play(
            imag_part.move_to, imag_part.get_left(),
            *map(FadeOut, [brace, we_understand, real_part])
        )
        self.dither()
        self.imag_exponent = imag_part

    def add_on_planes(self):
        left_plane = NumberPlane(x_radius = (SPACE_WIDTH-1)/2)
        left_plane.to_edge(LEFT, buff = 0)
        imag_line = Line(DOWN, UP).scale(SPACE_HEIGHT)
        imag_line.highlight(YELLOW).fade(0.3)
        imag_line.move_to(left_plane.get_center())
        left_plane.add(imag_line)
        left_title = TextMobject("Input space")
        left_title.add_background_rectangle()
        left_title.highlight(YELLOW)
        left_title.next_to(left_plane.get_top(), DOWN)

        right_plane = NumberPlane(x_radius = (SPACE_WIDTH-1)/2)
        right_plane.to_edge(RIGHT, buff = 0)
        unit_circle = Circle()
        unit_circle.highlight(MAROON_B).fade(0.3)
        unit_circle.shift(right_plane.get_center())
        right_plane.add(unit_circle)
        right_title = TextMobject("Output space")
        right_title.add_background_rectangle()
        right_title.highlight(MAROON_B)
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
        self.dither()
        self.left_plane = left_plane
        self.right_plane = right_plane

    def show_imaginary_powers(self):
        i = complex(0, 1)
        input_dot = Dot(self.z_to_point(i))
        input_dot.highlight(YELLOW)
        output_dot = Dot(self.z_to_point(0.5**(i), is_input = False))
        output_dot.highlight(MAROON_B)

        output_dot.save_state()
        output_dot.move_to(input_dot)
        output_dot.highlight(input_dot.get_color())

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
        new_exp.highlight(exp.get_color())
        new_exp.scale_to_fit_height(exp.get_height())
        new_exp.move_to(exp, LEFT)

        nine = TexMobject("9")
        nine.highlight(BLUE)
        denom = self.imag_exponent[0][3]
        denom.save_state()
        nine.replace(denom)

        self.play(Transform(exp, new_exp))
        self.play(input_dot.shift, 2*UP)
        self.play(input_dot.shift, 2*DOWN)
        self.dither()
        self.play(output_dot.restore)
        self.dither()
        walk_up_and_down()
        self.dither()
        curr_base = 1./9        
        self.play(Transform(denom, nine))
        walk_up_and_down()
        self.dither()

    def z_to_point(self, z, is_input = True):
        if is_input:
            plane = self.left_plane
        else:
            plane = self.right_plane
        return plane.num_pair_to_point((z.real, z.imag))

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
        VGroup(original[-1], split[1], split[3]).highlight(YELLOW)
        VGroup(original, split).to_corner(UP+LEFT)
        rect = BackgroundRectangle(split)
        real_part = VGroup(*split[:2])
        imag_part = VGroup(*split[2:])

        self.add(rect, original)
        self.dither()
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
        self.dither()
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
        fourth_group.highlight(RED)

        circle = Circle(radius = 2, color = MAROON_B)
        circle.fade(0.3)
        imag_power_point = self.z_to_point(0.5**complex(0, 1))
        imag_power_dot = Dot(imag_power_point)
        imag_power_line = Line(ORIGIN, imag_power_point)
        VGroup(imag_power_dot, imag_power_line).highlight(MAROON_B)

        full_power_tex = TexMobject(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        full_power_tex[-1].highlight(YELLOW)
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
        self.dither()
        self.play(
            imag_part.scale, 0.7,
            imag_part.next_to, imag_power_dot, DOWN+RIGHT, SMALL_BUFF,
            ShowCreation(imag_power_dot)
        )
        self.play(ShowCreation(circle), Animation(imag_power_dot))
        self.play(ShowCreation(imag_power_line))
        self.dither(2)
        self.play(
            fourth_group.rotate, imag_power_line.get_angle()
        )
        real_part.generate_target()
        imag_part.generate_target()
        real_part.target.next_to(brace, UP+RIGHT, buff = 0)
        imag_part.target.next_to(real_part.target, buff = 0)
        self.play(*map(MoveToTarget, [real_part, imag_part]))
        self.dither()

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
        title.highlight_by_tex("s", YELLOW)
        title.add_background_rectangle()
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        self.play(Write(title))
        self.add_foreground_mobject(title)
        self.dither()
        self.title = title

    def plug_in_specific_values(self):
        inputs = map(complex, [2, -1, complex(0, 1)])
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
        arrows.highlight(WHITE)

        for input_dot, output_dot, arrow in zip(input_dots, output_dots, arrows):
            input_dot.save_state()
            input_dot.move_to(self.title[1][1])
            input_dot.set_fill(opacity = 0)

            self.play(input_dot.restore)
            self.dither()
            self.play(ShowCreation(arrow))
            self.play(ShowCreation(output_dot))
            self.dither()
        self.add_foreground_mobjects(arrows, output_dots, input_dots)
        self.input_dots = input_dots
        self.output_dots = output_dots

    def add_transformable_plane(self, **kwargs):
        ComplexTransformationScene.add_transformable_plane(self, **kwargs)
        self.plane.next_to(ORIGIN, UP, buff = 0.01)
        self.plane.add(self.plane.copy().rotate(np.pi, RIGHT))
        self.plane.add(
            Line(ORIGIN, SPACE_WIDTH*RIGHT, color = self.horiz_end_color),
            Line(ORIGIN, SPACE_WIDTH*LEFT, color = self.horiz_end_color),
        )
        self.add(self.plane)

    def show_transformation(self):
        self.add_transformable_plane()
        self.play(ShowCreation(self.plane, run_time = 3))

        self.dither()
        self.apply_complex_homotopy(
            lambda z, t : z**(1+t),
            added_anims = [
                MoveAlongPath(dot, dot.path, run_time = 5)
                for dot in self.input_dots
            ],
            run_time = 5
        )
        self.dither(2)


    def comment_on_two_dimensions(self):
        morty = Mortimer().flip()
        morty.scale(0.7)
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble("speech", height = 2, width = 4)
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
        self.dither(2)

class ShowZetaOnHalfPlane(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
        "x_max" : int(SPACE_WIDTH+2),
    }
    def construct(self):
        self.add_title()
        self.initial_transformation()
        self.react_to_transformation()
        self.show_cutoff()
        self.highlight_i_line()
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
        zeta[1].highlight(YELLOW)
        for mob in zeta[3:3+4]:
            mob[-2].highlight(YELLOW)
        zeta.add_background_rectangle()
        zeta.scale(0.8)
        zeta.to_corner(UP+LEFT)
        self.add_foreground_mobjects(zeta)
        self.zeta = zeta

    def initial_transformation(self):
        self.add_transformable_plane()
        self.dither()
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.dither(2)
        self.plane.save_state()
        self.apply_zeta_function()
        self.dither(2)

    def react_to_transformation(self):
        morty = Mortimer().flip()
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble("speech")
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
        self.dither()
        self.play(
            morty.look_at, self.plane.get_bottom(),
            *map(FadeOut, [bubble, bubble.content])
        )
        self.play(Blink(morty))
        self.play(FadeOut(morty))

    def show_cutoff(self):
        words = TextMobject("Such an abrupt stop...")
        words.add_background_rectangle()
        words.next_to(ORIGIN, UP+LEFT)
        words.shift(LEFT+UP)

        line = Line(*map(self.z_to_point, [
            complex(np.euler_gamma, u*SPACE_HEIGHT)
            for u in 1, -1
        ]))
        line.highlight(YELLOW)
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
        self.dither(2)
        self.play(*map(FadeOut, [words, line]))

    def highlight_i_line(self):
        right_i_lines, left_i_lines = [
            VGroup(*[
                Line(
                    vert_vect+RIGHT, 
                    vert_vect+(SPACE_WIDTH+1)*horiz_vect
                )
                for vert_vect in UP, DOWN
            ])
            for horiz_vect in RIGHT, LEFT
        ]
        right_i_lines.highlight(YELLOW)
        left_i_lines.highlight(BLUE)
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
        self.dither(2)
        self.apply_zeta_function()
        self.dither(2)

        left_i_lines.save_state()
        left_i_lines.apply_complex_function(zeta)
        self.play(ShowCreation(left_i_lines, run_time = 5))
        self.dither()
        self.restore_mobjects(self.plane, left_i_lines)
        self.play(Transform(self.plane, colored_plane))
        self.dither()
        self.left_i_lines = left_i_lines

    def show_continuation(self):
        reflected_plane = self.get_reflected_plane()
        self.play(ShowCreation(reflected_plane, run_time = 2))
        self.plane.add(reflected_plane)
        self.remove(self.left_i_lines)
        self.dither()
        self.apply_zeta_function()
        self.dither(2)
        self.play(ShowCreation(
            reflected_plane,
            run_time = 6,
            rate_func = lambda t : 1-there_and_back(t)
        ))
        self.dither(2)

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
        self.dither(2)
        self.play(Write(divergent_sum))
        self.dither(2)

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
        zeta[2].highlight(YELLOW)
        sigma = TexMobject("\\sum_{n=1}^\\infty \\frac{1}{n^s}")
        sigma[-1].highlight(YELLOW)
        something_else = TextMobject("Something else...")
        conditions = VGroup(*[
            TextMobject("if Re$(s) %s 1$"%s)
            for s in ">", "\\le"
        ])
        definitions = VGroup(sigma, something_else)
        definitions.arrange_submobjects(DOWN, buff = 2*MED_BUFF, aligned_edge = LEFT)
        conditions.arrange_submobjects(DOWN, buff = LARGE_BUFF)
        definitions.shift(2*LEFT+2*UP)
        conditions.next_to(definitions, RIGHT, buff = LARGE_BUFF, aligned_edge = DOWN)
        brace = Brace(definitions, LEFT)
        zeta.next_to(brace, LEFT)

        sigma.save_state()
        sigma.next_to(zeta)
        self.add(zeta, sigma)
        self.dither()
        self.play(
            sigma.restore,
            GrowFromCenter(brace),
            FadeIn(something_else)
        )
        self.play(Write(conditions))
        self.dither()

        underbrace = Brace(something_else)
        question = underbrace.get_text("""
            What to put here?
        """)
        VGroup(underbrace, question).highlight(GREEN_B)

        self.play(
            GrowFromCenter(underbrace),
            Write(question),
            something_else.highlight, GREEN_B
        )
        self.dither(2)

class SquiggleOnExtensions(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
        "x_max" : int(SPACE_WIDTH+2),
    }
    def construct(self):
        self.show_negative_one()
        self.cycle_through_options()
        self.lock_into_place()

    def show_negative_one(self):
        self.add_transformable_plane()
        self.add_reflected_plane()
        thin_plane = self.plane.copy()
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
        dot.highlight(YELLOW)
        label = TexMobject(label_tex)
        label.add_background_rectangle()
        label.next_to(dot, UP+LEFT, buff = SMALL_BUFF)
        label.shift(LEFT)
        arrow = Arrow(label.get_right(), dot, buff = SMALL_BUFF)

        self.play(Write(label, run_time = 1))
        self.play(*map(ShowCreation, [arrow, dot]))
        self.dither()
        self.play(*map(FadeOut, [arrow, label]))
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
            scalar = 1 + (gamma-x)/(gamma+SPACE_WIDTH)
            return np.array([
                (scalar**2)*x,
                (scalar**3)*y,
                0
            ])
        def alt_mixed_scalar_func(point):
            x, y, z = point
            scalar = 1 + (gamma-x)/(gamma+SPACE_WIDTH)
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
            self.dither()
        self.play(FadeOut(self.dot))

        #Squiggle on example
        self.dither()
        self.play(FadeOut(self.left_plane))
        self.play(ShowCreation(
            self.left_plane,
            run_time = 5,
            rate_func = None
        ))
        self.dither()

    def lock_into_place(self):
        words = TextMobject(
            """Only one extension
            has a """, 
            "\\emph{derivative}",
            "everywhere", 
            alignment = ""
        )
        words.to_corner(UP+LEFT)
        words.highlight_by_tex("\\emph{derivative}", YELLOW)
        words.add_background_rectangle()
        words.show()

        self.play(Write(words))
        self.add_foreground_mobjects(words)
        self.play(self.left_plane.restore)
        self.dither()

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
        self.cycle_through_line_pairs()
        self.note_grid_lines()
        self.name_analytic()

    def add_title(self):
        title = TexMobject("f(", "s", ")=", "s", "^2")
        title.highlight_by_tex("s", YELLOW)
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        title.add_background_rectangle()
        self.title = title

        self.add_transformable_plane()
        self.play(Write(title))
        self.add_foreground_mobjects(title)
        self.dither()

    def show_initial_transformation(self):
        self.apply_function()
        self.dither(2)
        self.reset()

    def cycle_through_line_pairs(self):
        line_pairs = [
            (
                Line(3*DOWN+2*RIGHT, LEFT+2*UP),
                Line(DOWN, 3*UP+3*RIGHT)
            ),
            (
                Line(RIGHT+3*DOWN, RIGHT+3*UP),
                Line(3*LEFT+UP, 3*RIGHT+UP)
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
        brackets = VGroup(*map(
            self.get_right_angle_bracket,
            intersection_inputs
        ))
        self.apply_function()
        self.dither()
        self.play(
            ShowCreation(brackets, run_time = 5),
            Animation(self.plane)
        )
        self.dither()

    def name_analytic(self):
        equiv = TextMobject("``Analytic'' $\\Leftrightarrow$ Angle-preserving")
        kind_of = TextMobject("...kind of")
        for text in equiv, kind_of:       
            text.scale(1.2)
            text.add_background_rectangle()
        equiv.highlight(YELLOW)
        kind_of.highlight(RED)
        kind_of.next_to(equiv, RIGHT)
        VGroup(equiv, kind_of).next_to(ORIGIN, UP, buff = 1)

        self.play(Write(equiv))
        self.dither(2)
        self.play(Write(kind_of, run_time = 1))
        self.dither(2)

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
        arc.insert_n_anchor_points(10)
        arc.generate_target()
        input_z = complex(*arc.get_center()[:2])
        scale_factor = abs(2*input_z)
        arc.target.scale_about_point(1./scale_factor, intersection_point)
        arc.target.apply_complex_function(lambda z : z**2)

        angle_tex = TexMobject(
            "%d^\\circ"%abs(int((angle2-angle1)*180/np.pi))
        )
        angle_tex.highlight(arc.get_color())
        angle_tex.add_background_rectangle()
        self.put_angle_tex_next_to_arc(angle_tex, arc)
        angle_arrow = Arrow(
            angle_tex, arc, 
            color = arc.get_color(),
            buff = 0.1,
        )
        angle_group = VGroup(angle_tex, angle_arrow)


        self.play(*map(ShowCreation, lines))
        self.play(
            Write(angle_tex),
            ShowCreation(angle_arrow),
            ShowCreation(arc)
        )
        self.dither()

        self.play(FadeOut(angle_group))
        self.plane.add(*lines)
        self.apply_function(added_anims = [
            MoveToTarget(arc, run_time = 5)
        ])
        self.put_angle_tex_next_to_arc(angle_tex, arc)
        arrow = Arrow(angle_tex, arc, buff = 0.1)
        arrow.highlight(arc.get_color())
        self.play(
            Write(angle_tex),
            ShowCreation(arrow)
        )
        self.dither(2)
        self.play(*map(FadeOut, [arc, angle_tex, arrow]))

    def put_angle_tex_next_to_arc(self, angle_tex, arc):
        vect = arc.point_from_proportion(0.5)-interpolate(
            arc.points[0], arc.points[-1], 0.5
        )
        unit_vect = vect/np.linalg.norm(vect)
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
        brackets.highlight(YELLOW)
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
        self.dither()

    def add_title(self):
        title = TexMobject("f(", "s", ")=", "s", "^2")
        title.highlight_by_tex("s", YELLOW)
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        title.add_background_rectangle()
        derivative = TexMobject("f'(0) = 0")
        derivative.highlight(RED)
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
            two_dot.highlight(angle_tex.get_color())
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
            self.dither()
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
        words.highlight(YELLOW)
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
        self.dither()

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
        title[2].highlight(YELLOW)
        title[-1].highlight(YELLOW)
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
        brackets = VGroup(*map(
            self.get_right_angle_bracket,
            intersection_inputs
        ))
        self.play(ShowCreation(brackets, run_time = 3))
        self.dither()

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
        brackets.highlight(YELLOW)
        brackets.rotate(rotation, about_point = ORIGIN)
        brackets.shift(self.z_to_point(output_z))
        return brackets















