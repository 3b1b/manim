from manim import *


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

def test_scenes(get_config_test, Tester):
    CONFIG = get_config_test
    module_name = os.path.splitext(os.path.basename(__file__))[0].replace('test_', '')
    for _, scene_tested in inspect.getmembers(sys.modules[__name__], lambda m: inspect.isclass(m) and m.__module__ == __name__):
        Tester(scene_tested, CONFIG, module_name).test()


