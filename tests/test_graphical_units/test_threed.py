import pytest

from manim import *
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester


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
        self.move_camera(phi=PI / 4, theta=PI / 4, frame_center=[0, 0, -1])


class AmbientCameraMoveTest(ThreeDScene):
    def construct(self):
        cube = Cube()
        self.begin_ambient_camera_rotation(rate=0.5)
        self.play(Animation(cube))


MODULE_NAME = "threed"


@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
