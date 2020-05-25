from manim import *

# This file is intended to test any new feature added.
# Feel free to add a test or to modify one when adding a new/changing a feature.
class BasicScene(Scene):
    def construct(self):
        square = Square()
        self.play(ShowCreation(square))


class GeometryScene(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)
        self.play(ShowCreation(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))

        text = Text("Testing !")
        self.play(DrawBorderThenFill(text))

        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square().to_edge(UP)

        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            rate_func=there_and_back,
            run_time=1,
        )
        self.wait()


class PlottingScene(GraphScene):
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
        self.setup_axes(animate=False)
        func_graph = self.get_graph(lambda x : x**2, self.function_color)
        self.play(ShowCreation(func_graph))


def test_scenes():
    BasicScene()
