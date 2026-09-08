"""Adapted from example_scenes.py's CoordinateSystemExample and GraphExample."""
from manimlib import *


class CoordinateSystemExample(Scene):
    def construct(self):
        axes = Axes(
            x_range=(-1, 10),
            y_range=(-2, 2, 0.5),
            height=6,
            width=10,
            axis_config=dict(stroke_color=GREY_A, stroke_width=2),
        )
        axes.add_coordinate_labels(font_size=20, num_decimal_places=1)
        self.add(axes)

        # Axes descends from CoordinateSystem, so axes.c2p (short for
        # coords_to_point) maps a coordinate pair to a point on screen.
        dot = Dot(fill_color=RED)
        dot.move_to(axes.c2p(0, 0))
        self.play(FadeIn(dot, scale=0.5))
        self.play(dot.animate.move_to(axes.c2p(3, 2)))
        self.wait()

        # Axes.get_graph returns the graph of a function over the axes.
        sin_graph = axes.get_graph(lambda x: 2 * math.sin(x), color=BLUE)
        sin_label = axes.get_graph_label(sin_graph, "\\sin(x)")
        self.play(ShowCreation(sin_graph), FadeIn(sin_label, RIGHT))
        self.wait()
