"""
Curated example scenes for common ManimGL patterns.
"""
from __future__ import annotations

EXAMPLES: dict[str, dict[str, str]] = {
    "basic_shapes": {
        "description": "Create and animate basic geometric shapes.",
        "code": '''class BasicShapes(Scene):
    def construct(self):
        circle = Circle(radius=1.5, color=BLUE)
        square = Square(side_length=2, color=GREEN)
        triangle = Triangle(color=RED)

        shapes = VGroup(circle, square, triangle)
        shapes.arrange(RIGHT, buff=1)

        self.play(ShowCreation(circle))
        self.play(FadeIn(square))
        self.play(GrowFromCenter(triangle))
        self.wait()
''',
    },
    "transform": {
        "description": "Transform one shape into another.",
        "code": '''class TransformExample(Scene):
    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)

        self.play(ShowCreation(circle))
        self.wait(0.5)
        self.play(Transform(circle, square), run_time=2)
        self.wait()
''',
    },
    "tex": {
        "description": "Render LaTeX mathematical expressions.",
        "code": '''class TexExample(Scene):
    def construct(self):
        equation = Tex(
            r"e^{i\\pi} + 1 = 0",
            font_size=72,
        )
        label = Text("Euler's Identity", font_size=36)
        label.next_to(equation, DOWN, buff=0.5)

        self.play(Write(equation))
        self.play(FadeIn(label, shift=UP * 0.3))
        self.wait()
''',
    },
    "graph": {
        "description": "Plot a function on coordinate axes.",
        "code": '''class GraphExample(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            axis_config={"include_numbers": True},
        )
        graph = axes.get_graph(lambda x: np.sin(x), color=BLUE)
        label = axes.get_graph_label(graph, "\\\\sin(x)")

        self.play(ShowCreation(axes))
        self.play(ShowCreation(graph), Write(label))
        self.wait()
''',
    },
    "3d": {
        "description": "Create a 3D surface with camera rotation.",
        "code": '''class ThreeDExample(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        surface = ParametricSurface(
            lambda u, v: np.array([u, v, np.sin(u) * np.cos(v)]),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(32, 32),
        )
        surface.set_color_by_gradient(BLUE, GREEN)

        self.set_floor_plane("xz")
        self.play(ShowCreation(axes))
        self.play(ShowCreation(surface), run_time=3)
        self.wait()
''',
    },
    "number_line": {
        "description": "Animate a value tracker on a number line.",
        "code": '''class NumberLineExample(Scene):
    def construct(self):
        number_line = NumberLine(
            x_range=[-5, 5, 1],
            include_numbers=True,
        )
        tracker = ValueTracker(0)
        dot = Dot(color=RED)
        dot.add_updater(
            lambda d: d.move_to(number_line.n2p(tracker.get_value()))
        )

        self.play(ShowCreation(number_line))
        self.add(dot)
        self.play(tracker.animate.set_value(3), run_time=2)
        self.play(tracker.animate.set_value(-2), run_time=2)
        self.wait()
''',
    },
    "complex_plane": {
        "description": "Visualize a complex function transformation.",
        "code": '''class ComplexPlaneExample(Scene):
    def construct(self):
        plane = ComplexPlane()
        plane.add_coordinate_labels(font_size=24)

        moving_plane = plane.copy()
        moving_plane.prepare_for_nonlinear_transform()

        self.play(ShowCreation(plane))
        self.wait(0.5)
        self.play(
            moving_plane.animate.apply_complex_function(lambda z: z**2),
            run_time=3,
        )
        self.wait()
''',
    },
    "text_animation": {
        "description": "Animate text with Write and FadeTransform.",
        "code": '''class TextAnimation(Scene):
    def construct(self):
        text1 = Text("Hello, Manim!", font_size=60)
        text2 = Text("Animations are fun", font_size=60, color=YELLOW)

        self.play(Write(text1))
        self.wait()
        self.play(FadeTransform(text1, text2))
        self.wait()
''',
    },
}


def get_example(topic: str) -> dict:
    """
    Get example code for a given topic.

    Args:
        topic: One of the available example topics.

    Returns:
        Dict with "code" and "description", or an error with available topics.
    """
    if topic in EXAMPLES:
        return EXAMPLES[topic]

    return {
        "error": f"Unknown topic '{topic}'.",
        "available_topics": list(EXAMPLES.keys()),
    }
