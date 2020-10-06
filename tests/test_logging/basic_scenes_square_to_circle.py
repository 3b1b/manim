from manim import *

# This module is used in the CLI tests in tests_CLi.py.


class SquareToCircle(Scene):
    def construct(self):
        self.play(Transform(Square(), Circle()))
