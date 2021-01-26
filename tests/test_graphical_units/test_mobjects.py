import pytest

from manim import *
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester


class PointCloudDotTest(ThreeDScene):
    def construct(self):
        p = PointCloudDot()
        self.play(Animation(p))


MODULE_NAME = "mobjects"


@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
