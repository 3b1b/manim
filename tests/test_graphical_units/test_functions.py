import pytest
import numpy as np

from manim import *
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester


class FunctionGraphTest(Scene):
    def construct(self):
        graph = FunctionGraph(
            lambda x: 2 * np.cos(0.5 * x), x_min=-PI, x_max=PI, color=BLUE
        )
        self.add(graph)
        self.wait()


MODULE_NAME = "functions"


@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
