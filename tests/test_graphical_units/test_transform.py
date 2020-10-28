import pytest

from manim import *
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester


class TransformTest(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(Transform(square, circle))


class TransformFromCopyTest(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(TransformFromCopy(square, circle))


class ClockwiseTransformTest(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(ClockwiseTransform(square, circle))


class CounterclockwiseTransformTest(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(CounterclockwiseTransform(square, circle))


class MoveToTargetTest(Scene):
    def construct(self):
        square = Square()
        square.generate_target()
        square.target.shift(3 * UP)
        self.play(MoveToTarget(square))


class ApplyPointwiseFunctionTest(Scene):
    def construct(self):
        square = Square()

        def func(p):
            return np.array([1.0, 1.0, 0.0])

        self.play(ApplyPointwiseFunction(func, square))


class FadeToColortTest(Scene):
    def construct(self):
        square = Square()
        self.play(FadeToColor(square, RED))


class ScaleInPlaceTest(Scene):
    def construct(self):
        square = Square()
        self.play(ScaleInPlace(square, scale_factor=0.1))


class ShrinkToCenterTest(Scene):
    def construct(self):
        square = Square()
        self.play(ShrinkToCenter(square))


class RestoreTest(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(Transform(square, circle))
        square.save_state()
        self.play(square.shift, UP)
        self.play(Restore(square))


class ApplyFunctionTest(Scene):
    def construct(self):
        square = Square()
        self.add(square)

        def apply_function(mob):
            mob.scale(2)
            mob.to_corner(UR)
            mob.rotate(PI / 4)
            mob.set_color(RED)
            return mob

        self.play(ApplyFunction(apply_function, square))


class ApplyComplexFunctionTest(Scene):
    def construct(self):
        square = Square()
        self.play(
            ApplyComplexFunction(
                lambda complex_num: complex_num + 2 * np.complex(0, 1), square
            )
        )


class ApplyMatrixTest(Scene):
    def construct(self):
        square = Square()
        matrice = [[1.0, 0.5], [1.0, 0.0]]
        self.play(ApplyMatrix(matrice, square))


class CyclicReplaceTest(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        circle.shift(3 * UP)
        self.play(CyclicReplace(square, circle))


class FadeInAndOutTest(Scene):
    def construct(self):
        square = Square(color=BLUE).shift(2 * UP)
        annotation = Square(color=BLUE)
        self.add(annotation)
        self.play(FadeIn(square))

        annotation.become(Square(color=RED).rotate(PI / 4))
        self.add(annotation)
        self.play(FadeOut(square))


MODULE_NAME = "transform"


@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
