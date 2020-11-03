import pytest

from manim import *
from ..utils.testing_utils import get_scenes_to_test
from ..utils.GraphicalUnitTester import GraphicalUnitTester


class AxesTest(GraphScene):
    CONFIG = {
        "x_min": -5,
        "x_max": 5,
        "y_min": -3,
        "y_max": 3,
        "x_axis_config": {
            "add_start": 0.5,
            "add_end": 0.5,
            "include_tip": True,
        },
        "y_axis_config": {
            "add_start": 0.25,
            "add_end": 0.5,
            "include_tip": True,
        },
        "x_axis_visibility": True,
        "y_axis_visibility": True,
        "y_label_position": UP,
        "x_label_position": RIGHT,
        "graph_origin": ORIGIN,
        "axes_color": WHITE,
    }

    def construct(self):
        self.setup_axes(animate=True)


MODULE_NAME = "graph"


@pytest.mark.slow
@pytest.mark.parametrize("scene_to_test", get_scenes_to_test(__name__), indirect=False)
def test_scene(scene_to_test, tmpdir, show_diff):
    GraphicalUnitTester(scene_to_test[1], MODULE_NAME, tmpdir).test(show_diff=show_diff)
