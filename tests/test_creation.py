from manim import *


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


class WriteTest(Scene):
    def construct(self):
        t = Text('helloworld')

        self.play(Write(t))


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

def test_scenes(get_config_test, Tester):
    CONFIG = get_config_test
    module_name = os.path.splitext(os.path.basename(__file__))[0].replace('test_', '')
    for _, scene_tested in inspect.getmembers(sys.modules[__name__], lambda m: inspect.isclass(m) and m.__module__ == __name__):
        Tester(scene_tested, CONFIG, module_name).test()
