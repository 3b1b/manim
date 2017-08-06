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
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from topics.common_scenes import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

##########
#revert_to_original_skipping_status

class MathIsATease(Scene):
    def construct(self):
        randy = Randolph()
        lashes = VGroup()
        for eye in randy.eyes:
            for angle in np.linspace(-np.pi/3, np.pi/3, 12):
                lash = Line(ORIGIN, RIGHT)
                lash.set_stroke(DARK_GREY, 2)
                lash.scale_to_fit_width(0.27)
                lash.next_to(ORIGIN, RIGHT, buff = 0)
                lash.rotate(angle + np.pi/2)
                lash.shift(eye.get_center())
                lashes.add(lash)
        lashes.do_in_place(lashes.stretch, 0.8, 1)
        lashes.shift(0.04*DOWN)


        fan = SVGMobject(
            file_name = "fan",
            fill_opacity = 1,
            fill_color = YELLOW,
            stroke_width = 2,
            stroke_color = YELLOW,
            height = 0.7,
        )
        VGroup(*fan[-12:]).set_fill(YELLOW_E)
        fan.rotate(-np.pi/4)
        fan.move_to(randy)
        fan.shift(0.85*UP+0.25*LEFT)

        self.add(randy)
        self.play(
            ShowCreation(lashes, submobject_mode = "all_at_once"),
            randy.change, "tease",
            randy.look, OUT,
        )
        self.add_foreground_mobjects(fan)
        eye_bottom_y = randy.eyes.get_bottom()[1]
        self.play(
            ApplyMethod(
                lashes.apply_function, 
                lambda p : [p[0], eye_bottom_y, p[2]],
                rate_func = Blink.CONFIG["rate_func"],
            ),
            Blink(randy),
            DrawBorderThenFill(fan),
        )
        self.play(
            ApplyMethod(
                lashes.apply_function, 
                lambda p : [p[0], eye_bottom_y, p[2]],
                rate_func = Blink.CONFIG["rate_func"],
            ),
            Blink(randy),
        )
        self.dither()

class TODODeterminants(TODOStub):
    CONFIG = {
        "message" : "Determinants clip"
    }

class CircleToPairsOfPoints(Scene):
    def construct(self):
        plane = NumberPlane(written_coordinate_height = 0.3)
        plane.scale(2)
        plane.add_coordinates(y_vals = [-1, 1])
        background_plane = plane.copy()
        background_plane.highlight(GREY)
        background_plane.fade()
        circle = Circle(radius = 2, color = YELLOW)
        dot = Dot(circle.get_right(), color = LIGHT_GREY)

        equation = TexMobject("x", "^2", "+", "y", "^2", "=", "1")
        equation.highlight_by_tex("x", GREEN)
        equation.highlight_by_tex("y", RED)
        equation.to_corner(UP+LEFT)
        equation.add_background_rectangle()

        x, y = 1, 0
        coord_pair = TexMobject("(", "-%.02f"%x, ",", "-%.02f"%y, ")") 
        fixed_numbers = coord_pair.get_parts_by_tex(".00")
        fixed_numbers.set_fill(opacity = 0)
        coord_pair.add_background_rectangle()
        coord_pair.next_to(dot, UP+RIGHT, SMALL_BUFF)
        numbers = VGroup(*[
            DecimalNumber(val).replace(num, dim_to_match = 1)
            for val, num in zip([x, y], fixed_numbers)
        ])
        numbers[0].highlight(GREEN)
        numbers[1].highlight(RED)

        def get_update_func(i):
            return lambda t : dot.get_center()[i]/2.0


        self.add(background_plane, plane)
        self.play(ShowCreation(circle))
        self.play(Write(equation))
        self.play(
            LaggedStart(FadeIn, coord_pair),
            ShowCreation(dot),
            *[
                ReplacementTransform(
                    equation.get_parts_by_tex(tex).copy(),
                    number
                )
                for tex, number in zip("xy", numbers)
            ]
        )
        self.play(
            Rotating(
                dot, run_time = 7, in_place = False,
                rate_func = smooth,
            ),
            MaintainPositionRelativeTo(coord_pair, dot),
            *[
                ChangingDecimal(
                    num, get_update_func(i),
                    tracked_mobject = fixed_num
                )
                for num, i, fixed_num in zip(
                    numbers, (0, 1), fixed_numbers
                )
            ]
        )
        self.dither()

        ######### Rotation equations ##########

        rot_equation = TexMobject(
            "\\Rightarrow"
            "\\big(\\cos(\\theta)x - \\sin(\\theta)y\\big)^2 + ",
            "\\big(\\sin(\\theta)x + \\cos(\\theta)y\\big)^2 = 1",
        )
        rot_equation.scale(0.9)
        rot_equation.next_to(equation, RIGHT)
        rot_equation.add_background_rectangle()

        words = TextMobject("Rotational \\\\ symmetry")
        words.next_to(ORIGIN, UP)
        words.to_edge(RIGHT)
        words.add_background_rectangle()

        arrow = Arrow(
            words.get_left(), rot_equation.get_bottom(),
            path_arc = -np.pi/6
        )
        randy = Randolph().to_corner(DOWN+LEFT)

        self.play(
            Write(rot_equation, run_time = 2),
            FadeOut(coord_pair),
            FadeOut(numbers),
            FadeOut(dot),
            FadeIn(randy)
        )
        self.play(randy.change, "confused", rot_equation)
        self.play(Blink(randy))
        self.play(
            Write(words, run_time = 1),
            ShowCreation(arrow),
            randy.look_at, words
        )
        plane.remove(*plane.coordinate_labels)
        self.play(
            Rotate(
                plane, np.pi/3, 
                run_time = 4,
                rate_func = there_and_back
            ),
            Animation(equation),
            Animation(rot_equation),
            Animation(words),
            Animation(arrow),
            Animation(circle),
            randy.change, "hooray"
        )
        self.dither()

























