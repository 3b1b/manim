from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


class UpdaterTest(Scene):
    def construct(self):
        dot = Dot()
        square = Square()
        self.add(dot, square)
        square.add_updater(lambda m: m.next_to(dot, RIGHT, buff=SMALL_BUFF))
        self.add(square)
        self.play(dot.shift, UP*2)
        square.clear_updaters()


class ValueTrackerTest(Scene):
    def construct(self):
        theta = ValueTracker(PI/2)
        line_1 = Line(ORIGIN, RIGHT*3, color=RED)
        line_2 = Line(ORIGIN, RIGHT*3, color=GREEN)
        line_2.rotate(theta.get_value(), about_point=ORIGIN)


def test_scenes():
    utils_test_scenes(get_scenes_to_test(__name__), "updaters")
