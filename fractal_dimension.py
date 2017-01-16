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
            "But what \\emph{is} a fractal",
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
































