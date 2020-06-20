from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


class CubeTest(ThreeDScene):
    def construct(self):
        self.play(Animation(Cube()))


class SphereTest(ThreeDScene):
    def construct(self):
        self.play(Animation(Sphere()))


class AxesTest(ThreeDScene):
    def construct(self):
        self.play(Animation(ThreeDAxes()))


class CameraMoveTest(ThreeDScene):
    def construct(self):
        cube = Cube()
        self.play(Animation(cube))
        self.move_camera(phi=PI/4, theta=PI/4)


class AmbientCameraMoveTest(ThreeDScene):
    def construct(self):
        cube = Cube()
        self.begin_ambient_camera_rotation(rate=0.5)
        self.play(Animation(cube))


def test_scenes(get_config_test):
    utils_test_scenes(get_scenes_to_test(__name__), get_config_test, "threed")
