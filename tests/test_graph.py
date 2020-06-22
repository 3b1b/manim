from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


class PlotFunctions(GraphScene):
    CONFIG = {
        "x_min" : -10,
        "x_max" : 10.3,
        "y_min" : -1.5,
        "y_max" : 1.5,
        "graph_origin" : ORIGIN ,
        "function_color" : RED ,
        "axes_color" : GREEN,
        "x_labeled_nums" :range(-10,12,2), 
    }

    def construct(self): 
        constants.TEX_TEMPLATE = TexTemplate()
        self.setup_axes()
        f = self.get_graph(lambda x : x**2)
        self.play(Animation(f))

def test_scenes(get_config_test):
    utils_test_scenes(get_scenes_to_test(__name__), get_config_test, "graph", caching_needed=True)