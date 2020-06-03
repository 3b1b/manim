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
        self.setup_axes()
        f = self.get_graph(lambda x : x**2)

        self.play(Animation(f))