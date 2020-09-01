import pytest

from manim import *
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester


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


MODULE_NAME = "indication"


@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
