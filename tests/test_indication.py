from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


class FocusOnTest(Scene):
    def construct(self):
        square = Square()
        self.add(square)

        self.play(FocusOn(square))


class IndicateTest(Scene):
    def construct(self):
        square = Square()

        self.play(Indicate(square))


class FlashTest(Scene):
    def construct(self):
        square = Square()
        self.add(square)

        self.play(Flash(square))


class CircleIndicateTest(Scene):
    def construct(self):
        square = Square()
        self.add(square)

        self.play(CircleIndicate(square))


class ShowPassingFlashTest(Scene):
    def construct(self):
        square = Square()
        self.add(square)

        self.play(ShowPassingFlash(square))


class ShowCreationThenDestructionTest(Scene):
    def construct(self):
        square = Square()

        self.play(ShowCreationThenDestruction(square))


class ShowCreationThenFadeOutTest(Scene):
    def construct(self):
        square = Square()

        self.play(ShowCreationThenFadeOut(square))


class ShowPassingFlashAroundTest(Scene):
    def construct(self):
        circle = Circle()

        self.play(ShowPassingFlashAround(circle))


class ApplyWaveTest(Scene):
    def construct(self):
        square = Square()

        self.play(ApplyWave(square))


class WiggleOutThenInTest(Scene):
    def construct(self):
        square = Square()
        self.add(square)

        self.play(WiggleOutThenIn(square))


class TurnInsideOutTest(Scene):
    def construct(self):
        square = Square()
        self.add(square)

        self.play(TurnInsideOut(square))

def test_scenes(get_config_test):
    utils_test_scenes(get_scenes_to_test(__name__), get_config_test, "indication")


