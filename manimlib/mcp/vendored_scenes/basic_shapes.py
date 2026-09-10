"""Adapted from docs/example.py's SquareToCircle -- the project's own quickstart scene."""
from manimlib import *


class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        square = Square()

        self.play(ShowCreation(square))
        self.wait()
        self.play(ReplacementTransform(square, circle))
        self.wait()
        self.play(circle.animate.stretch(4, dim=0))
        self.play(Rotate(circle, TAU / 4))
        self.play(circle.animate.shift(2 * RIGHT), circle.animate.scale(0.25))
