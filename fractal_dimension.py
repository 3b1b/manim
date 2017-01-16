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
        "num_zooms" : 4,
        "fractal_class" : Sierpinski,
        "index_to_replace" : 0,
    }
    def construct(self):
        morty = self.pi_creature
        fractal = self.get_zoomable_fractal()

        fractal.show()
        
        self.play(
            ShowCreation(
                fractal, 
                run_time = 4, 
                rate_func = rush_from
            ),
            morty.change_mode, "hooray",
        )
        self.dither()
        self.play(
            ApplyMethod(
                fractal.scale, 2**self.num_zooms, 
                self.zoom_in_about_point,
                run_time = 8
            ),
            morty.change_mode, "thinking",
            morty.look_at, fractal.get_corner(self.zoom_in_about_point),
        )
        self.play(Blink(morty))
        self.dither()

    def get_zoomable_fractal(self):
        fractal = self.fractal_class(order = self.fractal_order)

        to_be_tweaked = fractal
        for x in range(self.num_zooms):
            new_corner = self.fractal_class(order = self.fractal_order)
            new_corner.replace(to_be_tweaked[self.index_to_replace])
            self.tweak_subpart(new_corner)
            to_be_tweaked.submobjects[self.index_to_replace] = new_corner
            to_be_tweaked = new_corner
        self.zoom_in_about_point = to_be_tweaked.get_center()

        return fractal

    def tweak_subpart(self, subpart):
        pass


class ZoomInOnDiamondFractal(ZoomInOnFractal):
    CONFIG = {
        "fractal_order" : 5,
        "fractal_class" : DiamondFractal,
    }
    def construct(self):
        high_res_fractal = self.fractal_class(order = self.fractal_order)
        low_res_fractal = self.fractal_class(order = self.fractal_order-1)

        high_res_fractal.scale(3, high_res_fractal.get_top())

        self.add(low_res_fractal)
        self.dither()
        self.play(Transform(low_res_fractal, high_res_fractal))
        self.dither(3)



















