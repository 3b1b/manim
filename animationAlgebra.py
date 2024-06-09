'''
Created by: Pranay Rishi Nalem
Date: June 8th, 2024 Time: 10:50 PM PST
Program Name: MathQuest Animations
Purpose: KTHack 2024
'''
from manim import *


class quadraticQuarticFunction(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-5, 5],
            y_range=[-5, 5],
            axis_config={"color": ORANGE},
        )

        quadraticGraph = axes.plot(lambda x: x**2, color=DARK_BLUE)
        quadraticLabel = axes.get_graph_label(quadraticGraph, label='x^{2}')

        quarticGraph = axes.plot(lambda x: x**3, color=DARK_BLUE)
        quarticLabel = axes.get_graph_label(quarticGraph, label='x^{4}')

        self.play(Create(axes), Create(quadraticGraph), Write(quadraticLabel))
        self.wait(1)
        self.play(Transform(quadraticGraph, quarticGraph), Transform(quadraticLabel, quarticLabel))
        self.wait(1)
