from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


class HomotopyTest(Scene):
    def construct(self):
        def func(x, y, z, t):
            norm = get_norm([x, y])
            tau = interpolate(5, -5, t) + norm/FRAME_X_RADIUS
            alpha = sigmoid(tau)
            return [x, y + 0.5*np.sin(2*np.pi*alpha)-t*SMALL_BUFF/2, z]

        square = Square()

        self.play(Homotopy(func, square))


class PhaseFlowTest(Scene):
    def construct(self):
        square = Square()

        def func(t):
            return t*0.5*UP

        self.play(PhaseFlow(func, square))


class MoveAlongPathTest(Scene):
    def construct(self):
        square = Square()
        dot = Dot()

        self.play(MoveAlongPath(dot, square))


class RotateTest(Scene):
    def construct(self):
        square = Square()

        self.play(Rotate(square, PI))


class MoveToTest(Scene):
    def construct(self):
        square = Square()

        self.play(square.move_to, np.array([1.0, 1.0, 0.0]))


class ShiftTest(Scene):
    def construct(self):
        square = Square()
        self.play(square.shift, UP)


def test_scenes(get_config_test):
    utils_test_scenes(get_scenes_to_test(__name__), get_config_test, "movements")
