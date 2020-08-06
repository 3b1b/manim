from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


class PlotFunctions(GraphScene):
    CONFIG = {
        "x_min": -10,
        "x_max": 10.3,
        "y_min": -1.5,
        "y_max": 1.5,
        "graph_origin": ORIGIN,
        "function_color": RED,
        "axes_color": GREEN,
        "x_labeled_nums": range(-10, 12, 2),
    }

    def construct(self):
        constants.TEX_TEMPLATE = TexTemplate()
        self.setup_axes()
        f = self.get_graph(lambda x: x ** 2)

        self.play(Animation(f))


class NumberLineTest(GraphScene):
    CONFIG = {
        "x_min": -10,
        "x_max": 10.3,
        "y_min": -1.5,
        "y_max": 1.5,
        "graph_origin": ORIGIN,
        "axes_color": YELLOW,
        "x_labeled_nums": range(-10, 12, 2),
        "y_labeled_nums": range(-1, 2),
        "x_axis_config": {
            "x_min": -5,
            "decimal_number_config": {"num_decimal_places": 1,},
        },
        "y_axis_config": {
            "color": RED,
            "decimal_number_config": {"num_decimal_places": 2,},
        },
    }

    def construct(self):
        constants.TEX_TEMPLATE = TexTemplate()
        self.setup_axes()
        f = self.get_graph(lambda x: x ** 2)

        self.play(Animation(f))


def test_scenes():
    utils_test_scenes(get_scenes_to_test(__name__), "graph", caching_needed=True)
