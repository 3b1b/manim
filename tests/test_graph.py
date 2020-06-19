from manim import *

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

def test_scenes(get_config_test, Tester):
    CONFIG = get_config_test
    module_name = os.path.splitext(os.path.basename(__file__))[
        0].replace('test_', '')
    for name, scene_tested in inspect.getmembers(sys.modules[__name__], lambda m: inspect.isclass(m) and m.__module__ == __name__):
        Tester(scene_tested, CONFIG, module_name, caching_needed=True).test()