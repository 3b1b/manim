import pytest

from manim import *
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester


class GradientTest(Scene):
    def construct(self):
        c = Circle(fill_opacity=1).set_color(color=[YELLOW, GREEN])
        self.play(Animation(c))


MODULE_NAME = "modifier_methods"


@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
