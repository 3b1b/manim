#!/usr/bin/env python

from manimlib.imports import *

# To watch one of these scenes, run the following:
# python -m manim example_scenes.py SquareToCircle -pl
#
# Use the flat -l for a faster rendering at a lower
# quality.
# Use -s to skip to the end and just save the final frame
# Use the -p to have the animation (or image, if -s was
# used) pop up once done.
# Use -n <number> to skip ahead to the n'th animation of a scene.
# Use -r <number> to specify a resolution (for example, -r 1080
# for a 1920x1080 video)
from manimlib.imports import *

class WhatIsTransform(Scene):
    def construct(self):
        M1 = TextMobject("A")
        M2 = TextMobject("B")
        M3 = TextMobject("C")
        M4 = TextMobject("D")
        self.add(M1)
        self.wait()

class WhatIsReplacementTransform(Scene):
    def construct(self):
        M1 = TextMobject("A")
        M2 = TextMobject("B")
        M3 = TextMobject("C")
        M4 = TextMobject("D")
        self.add(M1)
        self.wait()
 
        self.play(ReplacementTransform(M1,M2))
        self.wait()
 
        self.play(ReplacementTransform(M2,M3))
        self.wait()
 
        self.play(ReplacementTransform(M3,M4))
        self.wait()
 
        self.play(FadeOut(M4))

class ChangeTextColorAnimation(Scene):
    def construct(self):
        text = TextMobject("hahi")
        text.scale(3)
        self.play(Write(text))
        self.wait()
        self.play(
            ApplyMethod(text.set_color, YELLOW),
                run_time=2
            )
        self.wait()

class Floors(Scene):
    def construct(self):
        line = Line((0,0,0),(3,0,0))
        rectangle = Rectangle(width=2, height=6)
        # OR: square = Square()
        rectangle.move_to([-3,-3,0])
        self.play(ShowCreation(rectangle))
        self.wait()        