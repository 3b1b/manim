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

RESOURCE_DIR = os.path.join(MEDIA_DIR, "3b1b_videos", "π Day 2018")

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
        circle = Circle(color = YELLOW, radius = 1.25)
        circle.next_to(tau, UP, MED_LARGE_BUFF)
        circle.to_edge(RIGHT, buff = 2)
        circle.to_edge(UP)
        radius = Line(circle.get_center(), circle.get_right())
        radius.highlight(WHITE)
        one = TexMobject("1")
        kwargs = {"run_time" : 3, "rate_func" : bezier([0, 0, 1, 1])} 
        one_update = UpdateFromFunc(
            one, lambda m : m.move_to(
                radius.get_center() + \
                0.25*rotate_vector(radius.get_vector(), TAU/4)
            ),
            **kwargs
        )
        decimal = DecimalNumber(0, num_decimal_points = 4, show_ellipsis = True)
        decimal.scale(0.75)
        changing_decimal = ChangingDecimal(
            decimal, lambda a : a*TAU,
            position_update_func = lambda m : m.next_to(
                radius.get_end(), RIGHT,
                aligned_edge = DOWN,
            ),
            **kwargs
        )

        self.play(
            ShowCreation(radius), Write(one),
            RemovePiCreatureBubble(pi),
            RemovePiCreatureBubble(tau),
        )
        self.play(
            tau.change, "hooray",
            pi.change, "sassy",
            Rotating(radius, about_point = radius.get_start(), **kwargs),
            ShowCreation(circle, **kwargs),
            changing_decimal,
            one_update,
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
        for denom in 8, 4, 3:
            radius_copy = radius.copy()
            radius_copy.rotate(TAU/denom, about_point = circle.get_center())
            arc = circle.copy()
            arc.set_stroke(RED, width = 4)
            arc.pointwise_become_partial(circle, 0, 1./denom)
            mini_arc = arc.copy()
            mini_arc.set_stroke(WHITE, 2)
            mini_arc.scale(0.2, about_point = circle.get_center())
            tau_tex = TexMobject("\\tau/%d"%denom)
            tau_tex.next_to(
                mini_arc, 
                mini_arc.point_from_proportion(0.5) - circle.get_center()
            )
            angle_group = VGroup(radius_copy, mini_arc, tau_tex, arc)
            angle_groups.add(angle_group)


        angle_group = angle_groups[0]
        self.play(*map(FadeIn, [circle, radius]))
        self.play(
            FadeIn(angle_group),
            circle.fade, 0.25,
        )
        self.wait()
        for group in angle_groups[1:]:
            self.play(Transform(angle_group, group, path_arc = TAU/8))
            self.wait()
































