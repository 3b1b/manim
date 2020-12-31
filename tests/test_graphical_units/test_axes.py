import pytest

from manim import *
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester


class AxesTest(GraphScene):
    def construct(self):
        self.x_min = -5
        self.x_max = 5
        self.y_min = -3
        self.y_max = 3
        self.x_axis_config = {
            "add_start": 0.5,
            "add_end": 0.5,
            "include_tip": True,
        }
        self.y_axis_config = {
            "add_start": 0.25,
            "add_end": 0.5,
            "include_tip": True,
        }
        self.x_axis_visibility = True
        self.y_axis_visibility = True
        self.y_label_position = UP
        self.x_label_position = RIGHT
        self.graph_origin = ORIGIN
        self.axes_color = WHITE
        self.setup_axes(animate=True)


MODULE_NAME = "graph"


@pytest.mark.slow
@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
