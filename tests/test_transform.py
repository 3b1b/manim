from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


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


def test_scenes():
    utils_test_scenes(get_scenes_to_test(__name__), "transform")
