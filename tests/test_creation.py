from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


class ShowCreationTest(Scene):
    def construct(self):
        square = Square()

        self.play(ShowCreation(square))


class UncreateTest(Scene):
    def construct(self):
        square = Square()

        self.add(square)
        self.play(Uncreate(square))


class DrawBorderThenFillTest(Scene):
    def construct(self):
        square = Square(fill_opacity=1)

        self.play(DrawBorderThenFill(square))


# NOTE : Here should be the Write Test. But for some reasons it appears that this function is untestable (see issue #157)

class FadeOutTest(Scene):
    def construct(self):
        square = Square()
        self.add(square)

        self.play(FadeOut(square))


class FadeInTest(Scene):
    def construct(self):
        square = Square()

        self.play(FadeIn(square))


class FadeInFromTest(Scene):
    def construct(self):
        square = Square()

        self.play(FadeInFrom(square, direction=UP))


class FadeInFromDownTest(Scene):
    def construct(self):
        square = Square()

        self.play(FadeInFromDown(square))


class FadeOutAndShiftTest(Scene):
    def construct(self):
        square = Square()

        self.play(FadeOutAndShift(square, direction=UP))


class FadeInFromLargeTest(Scene):
    def construct(self):
        square = Square()

        self.play(FadeInFromLarge(square))


class GrowFromPointTest(Scene):
    def construct(self):
        square = Square()

        self.play(GrowFromPoint(square, np.array((1, 1, 0))))


class GrowFromCenterTest(Scene):
    def construct(self):
        square = Square()

        self.play(GrowFromCenter(square))


class GrowFromEdgeTest(Scene):
    def construct(self):
        square = Square()

        self.play(GrowFromEdge(square, DOWN))


class SpinInFromNothingTest(Scene):
    def construct(self):
        square = Square()

        self.play(SpinInFromNothing(square))


class ShrinkToCenterTest(Scene):
    def construct(self):
        square = Square()

        self.play(ShrinkToCenter(square))

def test_scenes(get_config_test):
    utils_test_scenes(get_scenes_to_test(__name__), get_config_test, "creation")
