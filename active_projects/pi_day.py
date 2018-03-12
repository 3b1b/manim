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

class PiTauDebate(PiCreatureScene):
    def construct(self):
        pi, tau = self.pi, self.tau

        self.add(pi, tau)

        self.play(PiCreatureSays(
            pi, "3.1415...!",
            target_mode = "angry",
            look_at_arg = tau.eyes,
            # bubble_kwargs = {"width" : 3}
        ))
        self.play(PiCreatureSays(
            tau, "6.2831...!",
            target_mode = "angry",
            look_at_arg = pi.eyes,
            bubble_kwargs = {"width" : 3, "height" : 2},
        ))
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(pi),
            RemovePiCreatureBubble(tau),
        )

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

        self.play(ShowCreation(radius), Write(one))
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




































