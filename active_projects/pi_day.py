# -*- coding: utf-8 -*-

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.compositions import *
from animation.playground import *
from animation.continual_animation import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from scene.moving_camera_scene import *
from camera import *
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *

RESOURCE_DIR = os.path.join(MEDIA_DIR, "3b1b_videos", "π Day 2018", "images")
def get_image(name):
    return ImageMobject(os.path.join(RESOURCE_DIR, name))

def get_circle_drawing_terms(radius = 1, positioning_func = lambda m : m.center()):
    circle = Circle(color = YELLOW, radius = 1.25)
    positioning_func(circle)
    radius = Line(circle.get_center(), circle.points[0])
    radius.highlight(WHITE)
    one = TexMobject("1")
    one.scale(0.75)
    one_update = UpdateFromFunc(
        one, lambda m : m.move_to(
            radius.get_center() + \
            0.25*rotate_vector(radius.get_vector(), TAU/4)
        ),
    )
    decimal = DecimalNumber(0, num_decimal_points = 4, show_ellipsis = True)
    decimal.scale(0.75)
    def reposition_decimal(decimal):
        vect = radius.get_vector()
        unit_vect = vect/np.linalg.norm(vect)
        angle = radius.get_angle()
        alpha = (-np.cos(2*angle) + 1)/2
        interp_length = interpolate(decimal.get_width(), decimal.get_height(), alpha)
        buff = interp_length/2 + MED_SMALL_BUFF
        decimal.move_to(radius.get_end() + buff*unit_vect)
        decimal.shift(UP*decimal.get_height()/2)
        return decimal

    kwargs = {"run_time" : 3, "rate_func" : bezier([0, 0, 1, 1])} 
    changing_decimal = ChangingDecimal(
        decimal, lambda a : a*TAU,
        position_update_func = reposition_decimal,
        **kwargs
    )

    terms = VGroup(circle, radius, one, decimal)
    generate_anims1 = lambda : [ShowCreation(radius), Write(one)]
    generate_anims2 = lambda : [
        ShowCreation(circle, **kwargs),
        Rotating(radius, about_point = radius.get_start(), **kwargs),
        changing_decimal,
        one_update,
    ]

    return terms, generate_anims1, generate_anims2

##

class PiTauDebate(PiCreatureScene):
    def construct(self):
        pi, tau = self.pi, self.tau
        self.add(pi, tau)

        pi_value = TextMobject("3.1415...!")
        pi_value.highlight(BLUE)
        tau_value = TextMobject("6.2831...!")
        tau_value.highlight(GREEN)

        self.play(PiCreatureSays(
            pi, pi_value,
            target_mode = "angry",
            look_at_arg = tau.eyes,
            # bubble_kwargs = {"width" : 3}
        ))
        self.play(PiCreatureSays(
            tau, tau_value,
            target_mode = "angry",
            look_at_arg = pi.eyes,
            bubble_kwargs = {"width" : 3, "height" : 2},
        ))
        self.wait()

        # Show tau
        terms, generate_anims1, generate_anims2 = get_circle_drawing_terms(
            radius = 1.25,
            positioning_func = lambda m : m.to_edge(RIGHT, buff = 2).to_edge(UP, buff = 1)
        )
        circle, radius, one, decimal = terms

        self.play(
            RemovePiCreatureBubble(pi),
            RemovePiCreatureBubble(tau),
            *generate_anims1()
        )
        self.play(
            tau.change, "hooray",
            pi.change, "sassy",
            *generate_anims2()
        )
        self.wait()


        # Show pi
        circle = Circle(color = RED, radius = 1.25/2)
        circle.rotate(TAU/4)
        circle.move_to(pi)
        circle.to_edge(UP, buff = MED_LARGE_BUFF)
        diameter = Line(circle.get_left(), circle.get_right())
        one = TexMobject("1")
        one.scale(0.75)
        one.next_to(diameter, UP, SMALL_BUFF)

        circum_line = diameter.copy().scale(np.pi)
        circum_line.match_style(circle)
        circum_line.next_to(circle, DOWN, buff = MED_LARGE_BUFF)
        # circum_line.to_edge(LEFT)
        brace = Brace(circum_line, DOWN, buff = SMALL_BUFF)
        decimal = DecimalNumber(np.pi, num_decimal_points = 4, show_ellipsis = True)
        decimal.scale(0.75)
        decimal.next_to(brace, DOWN, SMALL_BUFF)

        self.play(
            FadeIn(VGroup(circle, diameter, one)),
            tau.change, "confused",
            pi.change, "hooray"
        )
        self.add(circle.copy().fade(0.5))
        self.play(
            ReplacementTransform(circle, circum_line, run_time = 2)
        )
        self.play(GrowFromCenter(brace), Write(decimal))
        self.wait(3)
        # self.play()


    def create_pi_creatures(self):
        pi = self.pi = Randolph()
        pi.to_edge(DOWN).shift(4*LEFT)
        tau = self.tau = TauCreature(
            # mode = "angry",
            file_name_prefix = "TauCreatures",
            color = GREEN_E
        ).flip()
        tau.to_edge(DOWN).shift(4*RIGHT)
        return VGroup(pi, tau)

class HartlAndPalais(Scene):
    def construct(self):
        hartl_rect = ScreenRectangle(
            color = WHITE,
            stroke_width = 1,
        )
        hartl_rect.scale_to_fit_width(SPACE_WIDTH - 1)
        hartl_rect.to_edge(LEFT)
        palais_rect = hartl_rect.copy()
        palais_rect.to_edge(RIGHT)

        tau_words = TextMobject("$\\tau$ ``tau''")
        tau_words.next_to(hartl_rect, UP)

        hartl_words = TextMobject("Michael Hartl's \\\\ ``Tau manifesto''")
        hartl_words.next_to(hartl_rect, DOWN)

        palais_words = TextMobject("Robert Palais' \\\\ ``Pi is Wrong!''")
        palais_words.next_to(palais_rect, DOWN)

        for words in hartl_words, palais_words:
            words.scale(0.7, about_edge = UP)

        three_legged_creature = ThreeLeggedPiCreature(height = 1.5)
        three_legged_creature.next_to(palais_rect, UP)

        # self.add(hartl_rect, palais_rect)
        self.add(hartl_words)
        self.play(Write(tau_words))
        self.wait()
        self.play(FadeIn(palais_words))
        self.play(FadeIn(three_legged_creature))
        self.play(three_legged_creature.change_mode, "wave")
        self.play(Blink(three_legged_creature))
        self.play(Homotopy(
            lambda x, y, z, t : (x + 0.1*np.sin(2*TAU*t)*np.exp(-10*(t-0.5 - 0.5*(y-1.85))**2), y, z),
            three_legged_creature,
            run_time = 2,
        ))
        self.wait()

class ManyFormulas(Scene):
    def construct(self):
        formulas = VGroup(
            TexMobject("\\sin(x + \\tau) = \\sin(x)"),
            TexMobject("e^{\\tau i} = 1"),
            TexMobject("n! \\approx \\sqrt{\\tau n} \\left(\\frac{n}{e} \\right)^n"),
            TexMobject("c_n = \\frac{1}{\\tau} \\int_0^\\tau f(x) e^{inx}dx"),
        )
        formulas.arrange_submobjects(DOWN, buff = MED_LARGE_BUFF)
        formulas.to_edge(LEFT)

        self.play(LaggedStart(FadeIn, formulas, run_time = 3))

        circle = Circle(color = YELLOW, radius = 2)
        circle.to_edge(RIGHT)
        radius = Line(circle.get_center(), circle.get_right())
        radius.highlight(WHITE)

        angle_groups = VGroup()
        for denom in 5, 4, 3, 2:
            radius_copy = radius.copy()
            radius_copy.rotate(TAU/denom, about_point = circle.get_center())
            arc = Arc(
                angle = TAU/denom,
                stroke_color = RED,
                stroke_width = 4,
                radius = circle.radius,
            )
            arc.shift(circle.get_center())
            mini_arc = arc.copy()
            mini_arc.set_stroke(WHITE, 2)
            mini_arc.scale(0.15, about_point = circle.get_center())
            tau_tex = TexMobject("\\tau/%d"%denom)
            point = mini_arc.point_from_proportion(0.5)
            tau_tex.next_to(point, direction = point - circle.get_center())
            angle_group = VGroup(radius_copy, mini_arc, tau_tex, arc)
            angle_groups.add(angle_group)


        angle_group = angle_groups[0]
        self.play(*map(FadeIn, [circle, radius]))
        self.play(
            circle.set_stroke, {"width" : 1,},
            FadeIn(angle_group),
        )
        self.wait()
        for group in angle_groups[1:]:
            self.play(Transform(angle_group, group, path_arc = TAU/8))
            self.wait()

class HistoryOfOurPeople(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Today: The history \\\\ of our people.",
            bubble_kwargs = {"width" : 4, "height" : 3}
        )
        self.change_all_student_modes("hooray")
        self.wait()
        self.play(*[
            ApplyMethod(pi.change, "happy", self.screen)
            for pi in self.pi_creatures
        ])
        self.wait(4)

class TauFalls(Scene):
    def construct(self):
        tau = TauCreature()
        bottom = np.min(tau.body.points[:,1])*UP
        angle = -0.15*TAU
        tau.generate_target()
        tau.target.change("angry")
        tau.target.rotate(angle, about_point = bottom)
        self.play(Rotate(tau, angle, rate_func = rush_into, path_arc = angle, about_point = bottom))
        # self.play(MoveToTarget(tau, rate_func = rush_into, path_arc = angle))
        self.play(MoveToTarget(tau))
        self.wait()

class EulerWrites628(Scene):
    CONFIG = {
        "camera_config" : {
            "background_alpha" : 255,
        }
    }
    def construct(self):
        image = ImageMobject(os.path.join(RESOURCE_DIR, "dalembert_zoom"))
        image.scale_to_fit_width(2*SPACE_WIDTH - 1)
        image.to_edge(UP, buff = MED_SMALL_BUFF)
        image.fade(0.15)
        rect = Rectangle(
            width = 12, 
            height = 0.5,
            stroke_width = 0,
            fill_opacity = 0.3,
            fill_color = GREEN,
        )
        rect.insert_n_anchor_points(20)
        rect.apply_function(lambda p : np.array([p[0], p[1] - 0.005*p[0]**2, p[2]]))
        rect.rotate(0.012*TAU)
        rect.move_to(image)
        rect.shift(0.15*DOWN)

        words = TextMobject(
            "``Let", "$\\pi$", "be the", "circumference", 
            "of a circle whose", "radius = 1''",
        )
        words.highlight_by_tex_to_color_map({
            "circumference" : YELLOW,
            "radius" : GREEN,
        })
        words.next_to(image, DOWN)
        pi = words.get_part_by_tex("\\pi").copy()

        terms, generate_anims1, generate_anims2 = get_circle_drawing_terms(
            radius = 1, 
            positioning_func = lambda circ : circ.next_to(words, DOWN, buff = 1.25)
        )
        circle, radius, one, decimal = terms

        unwrapped_perimeter = Line(ORIGIN, TAU*RIGHT)
        unwrapped_perimeter.match_style(circle)
        unwrapped_perimeter.next_to(circle, DOWN)
        brace = Brace(unwrapped_perimeter, UP, buff = SMALL_BUFF)

        perimeter = TexMobject(
            "\\pi\\epsilon\\rho\\iota\\mu\\epsilon\\tau\\rho\\text{o}\\varsigma",
            "\\text{ (perimeter)}",
            "="
        )
        perimeter.next_to(brace, UP, submobject_to_align = perimeter[1], buff = SMALL_BUFF)
        perimeter[0][0].highlight(GREEN)

        self.play(FadeInFromDown(image))
        self.play(
            Write(words), 
            GrowFromPoint(rect, rect.point_from_proportion(0.9))
        )
        self.wait()
        self.play(*generate_anims1())
        self.play(*generate_anims2())
        self.play(terms.shift, UP)
        self.play(
            pi.scale, 2,
            pi.shift, DOWN, 
            pi.highlight, GREEN
        )
        self.wait()
        self.play(
            GrowFromCenter(brace),
            circle.set_stroke, YELLOW, 1,
            ReplacementTransform(circle.copy(), unwrapped_perimeter),
            decimal.scale, 1.25,
            decimal.next_to, perimeter[-1].get_right(), RIGHT,
            ReplacementTransform(pi, perimeter[0][0]),
            Write(perimeter),
        )
        self.wait()

class HeroAndVillain(Scene):
    CONFIG = {
        "camera_config" : {
            "background_alpha" : 255,
        } 
    }
    def construct(self):
        good_euler = get_image("Leonhard_Euler_by_Handmann")
        bad_euler_pixelated = get_image("Leonard_Euler_pixelated")
        bad_euler = get_image("Leonard_Euler_revealed")
        pictures = good_euler, bad_euler_pixelated, bad_euler
        for mob in pictures:
            mob.scale_to_fit_height(5)

        good_euler.move_to(SPACE_WIDTH*LEFT/2)
        bad_euler.move_to(SPACE_WIDTH*RIGHT/2)
        bad_euler_pixelated.move_to(bad_euler)

        good_euler_label = TextMobject("Leonhard Euler")
        good_euler_label.next_to(good_euler, DOWN)
        tau_words = TextMobject("Used 6.2831...")
        tau_words.next_to(good_euler, UP)
        tau_words.highlight(GREEN)

        bad_euler_label = TextMobject("Also Euler...")
        bad_euler_label.next_to(bad_euler, DOWN)
        pi_words = TextMobject("Used 3.1415...")
        pi_words.highlight(RED)
        pi_words.next_to(bad_euler, UP)

        self.play(
            FadeInFromDown(good_euler),
            Write(good_euler_label)
        )
        self.play(LaggedStart(FadeIn, tau_words))
        self.wait()
        self.play(FadeInFromDown(bad_euler_pixelated))
        self.play(LaggedStart(FadeIn, pi_words))
        self.wait(2)
        self.play(
            FadeIn(bad_euler),
            Write(bad_euler_label),
        )
        self.remove(bad_euler_pixelated)
        self.wait(2)























