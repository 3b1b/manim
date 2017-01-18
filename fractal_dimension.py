#!/usr/bin/env python

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


class Britain(SVGMobject):
    CONFIG = {
        "file_name" : "Britain.svg",
        "stroke_width" : 1,
        "stroke_color" : WHITE,
        "fill_opacity" : 0,
        "height" : 5,
        "mark_paths_closed" : True,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.scale_to_fit_height(self.height)
        self.center()


class KochTest(Scene):
    def construct(self):
        koch = KochCurve(order = 5, stroke_width = 2)

        self.play(ShowCreation(koch, run_time = 3))
        self.play(
            koch.scale, 3, koch.get_left(),
            koch.set_stroke, None, 4
        )
        self.dither()

class SierpinskiTest(Scene):
    def construct(self):
        sierp = Sierpinski(
            order = 5,
        )

        self.play(FadeIn(
            sierp, 
            run_time = 5,
            submobject_mode = "lagged_start",
        ))
        self.dither()
        # self.play(sierp.scale, 2, sierp.get_top())
        # self.dither(3)

class FractalCreation(Scene):
    CONFIG = {
        "fractal_class" : PentagonalFractal,
        "max_order" : 6,
        "path_arc" : np.pi/6,
        "submobject_mode" : "lagged_start"
    }
    def construct(self):
        fractal = self.fractal_class(order = 0)
        self.play(FadeIn(fractal))
        for order in range(1, self.max_order+1):
            new_fractal = self.fractal_class(order = order)
            self.play(Transform(
                fractal, new_fractal,
                path_arc = self.path_arc,
                submobject_mode = self.submobject_mode,
                run_time = 2
            ))
            self.dither()
        self.dither()

###################################


class ZoomInOnFractal(PiCreatureScene):
    CONFIG = {
        "fractal_order" : 6,
        "num_zooms" : 5,
        "fractal_class" : DiamondFractal,
        "index_to_replace" : 0,
    }
    def construct(self):
        morty = self.pi_creature

        fractal = self.fractal_class(order = self.fractal_order)
        fractal.show()

        fractal = self.introduce_fractal()
        self.change_mode("thinking")
        self.blink()
        self.zoom_in(fractal)


    def introduce_fractal(self):
        fractal = self.fractal_class(order = 0)
        self.play(FadeIn(fractal))
        for order in range(1, self.fractal_order+1):
            new_fractal = self.fractal_class(order = order)
            self.play(
                Transform(fractal, new_fractal, run_time = 2),
                self.pi_creature.change_mode, "hooray"
            )
        return fractal

    def zoom_in(self, fractal):
        grower = fractal[self.index_to_replace]
        grower_target = fractal.copy()

        for x in range(self.num_zooms):
            self.tweak_fractal_subpart(grower_target)
            grower_family = grower.family_members_with_points()
            everything = VGroup(*[
                submob
                for submob in fractal.family_members_with_points()
                if not submob.is_off_screen()
                if submob not in grower_family
            ])
            everything.generate_target()
            everything.target.shift(
                grower_target.get_center()-grower.get_center()
            )
            everything.target.scale(
                grower_target.get_height()/grower.get_height()
            )

            self.play(
                Transform(grower, grower_target),
                MoveToTarget(everything),
                self.pi_creature.change_mode, "thinking",
                run_time = 2
            )
            self.dither()
            grower_target = grower.copy()            
            grower = grower[self.index_to_replace]


    def tweak_fractal_subpart(self, subpart):
        subpart.rotate_in_place(np.pi/4)

class WhatAreFractals(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "But what \\emph{is} a fractal?",
            student_index = 2,
            width = 6
        )
        self.change_student_modes("thinking", "pondering", None)
        self.dither()

        name = TextMobject("Benoit Mandelbrot")
        name.to_corner(UP+LEFT)
        # picture = Rectangle(height = 4, width = 3)
        picture = ImageMobject("Mandelbrot")
        picture.scale_to_fit_height(4)
        picture.next_to(name, DOWN)
        self.play(
            Write(name, run_time = 2),
            FadeIn(picture),
            *[
                ApplyMethod(pi.look_at, name)
                for pi in self.get_everyone()
            ]
        )
        self.dither(2)
        question = TextMobject("Aren't they", "self-similar", "shapes?")
        question.highlight_by_tex("self-similar", YELLOW)
        self.student_says(question)
        self.play(self.get_teacher().change_mode, "happy")
        self.dither(2)

class IntroduceVonKochCurve(Scene):
    CONFIG = {
        "order" : 5,
        "stroke_width" : 3,
    }
    def construct(self):
        snowflake = self.get_snowflake()
        name = TextMobject("Von Koch Snowflake")
        name.to_edge(UP)

        self.play(ShowCreation(snowflake, run_time = 3))
        self.play(Write(name, run_time = 2))
        curve = self.isolate_one_curve(snowflake)
        self.dither()
        self.zoom_in_on(curve)

    def get_snowflake(self):
        triangle = RegularPolygon(n = 3, start_angle = np.pi/2)
        triangle.scale_to_fit_height(4)
        curves = VGroup(*[
            KochCurve(
                order = self.order,
                stroke_width = self.stroke_width
            )
            for x in range(3)
        ])
        for index, curve in enumerate(curves):
            width = curve.get_width()
            curve.move_to(
                (np.sqrt(3)/6)*width*UP, DOWN
            )
            curve.rotate(-index*2*np.pi/3)
        curves.gradient_highlight(BLUE, WHITE, BLUE)

        return curves

    def isolate_one_curve(self, snowflake):
        self.play(*[
            ApplyMethod(curve.shift, curve.get_center()/2)
            for curve in snowflake
        ])
        self.dither()
        self.play(
            snowflake.scale, 2.1,
            snowflake.next_to, UP, DOWN
        )
        self.remove(*snowflake[1:])
        return snowflake[0]

    def zoom_in_on(self, curve):
        larger_curve = KochCurve(order = self.order+1)
        larger_curve.replace(curve)
        larger_curve.scale(3, about_point = curve.get_corner(DOWN+LEFT))
        larger_curve.gradient_highlight(
            curve[0].get_color(),
            curve[-1].get_color(),
        )

        self.play(Transform(curve, larger_curve, run_time = 2))
        n_parts = len(curve.split())
        sub_portion = VGroup(*curve[:n_parts/4])
        self.play(
            sub_portion.highlight, YELLOW,
            rate_func = there_and_back
        )
        self.dither()

class IntroduceSierpinskiTriangle(PiCreatureScene):
    CONFIG = {
        "order" : 7,
    }
    def construct(self):
        sierp = Sierpinski(order = self.order)
        sierp.save_state()

        self.play(FadeIn(
            sierp, 
            run_time = 2,
            submobject_mode = "lagged_start" 
        ))
        self.dither()
        self.play(
            self.pi_creature.change_mode, "pondering",
            *[
                ApplyMethod(submob.shift, submob.get_center())
                for submob in sierp
            ]
        )
        self.dither()
        for submob in sierp:
            self.play(sierp.shift, -submob.get_center())
            self.dither()
        self.play(sierp.restore)
        self.change_mode("happy")
        self.dither()
        
class SelfSimilarFractalsAsSubset(Scene):
    CONFIG = {
        "fractal_width" : 1.5
    }
    def construct(self):
        self.add_self_similar_fractals()
        self.add_general_fractals()

    def add_self_similar_fractals(self):
        fractals = VGroup(
            DiamondFractal(order = 5),
            KochSnowFlake(order = 3),
            Sierpinski(order = 5),
        )
        for submob in fractals:
            submob.scale_to_fit_width(self.fractal_width)
        fractals.arrange_submobjects(RIGHT)
        fractals[-1].next_to(VGroup(*fractals[:-1]), DOWN)

        title = TextMobject("Self-similar fractals")
        title.next_to(fractals, UP)

        small_rect = Rectangle()
        small_rect.replace(VGroup(fractals, title), stretch = True)
        small_rect.scale_in_place(1.2)
        self.small_rect = small_rect

        group = VGroup(fractals, title, small_rect)
        group.to_corner(UP+LEFT, buff = 2*MED_BUFF)

        self.play(
            Write(title),
            ShowCreation(fractals),
            run_time = 3
        )
        self.play(ShowCreation(small_rect))
        self.dither()

    def add_general_fractals(self):
        big_rectangle = Rectangle(
            width = 2*SPACE_WIDTH - 2*MED_BUFF,
            height = 2*SPACE_HEIGHT - 2*MED_BUFF,
        )
        title = TextMobject("Fractals")
        title.scale(1.5)
        title.next_to(ORIGIN, RIGHT, buff = LARGE_BUFF)
        title.to_edge(UP, buff = 2*MED_BUFF)

        britain = Britain()
        britain.next_to(self.small_rect, RIGHT)
        britain.shift(2*DOWN)

        randy = Randolph().flip().scale(1.4)
        randy.next_to(britain, buff = SMALL_BUFF)
        randy.generate_target()
        randy.target.change_mode("pleading")
        fractalify(randy.target, order = 2)

        self.play(
            ShowCreation(big_rectangle), 
            Write(title),
        )
        self.play(ShowCreation(britain), run_time = 5)
        self.play(
            britain.set_stroke, BLACK, 0,
            britain.set_fill, BLUE, 1,
        )
        self.play(FadeIn(randy))
        self.play(MoveToTarget(randy, run_time = 2))
        self.dither(2)

class ConstrastSmoothAndFractal(Scene):
    def construct(self):
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        smooth = TextMobject("Smooth")
        smooth.shift(SPACE_WIDTH*LEFT/2)
        fractal = TextMobject("Fractal")
        fractal.shift(SPACE_WIDTH*RIGHT/2)
        VGroup(smooth, fractal).to_edge(UP)
        self.add(v_line, smooth, fractal)

        britain = Britain()
        anchors = britain.get_anchors()
        smooth_britain = 
























