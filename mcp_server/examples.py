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
    # --- Technique examples inspired by 3b1b/videos ---
    "value_tracker_graph": {
        "description": "Use a ValueTracker to animate a dot sliding along a curve with a dynamic label.",
        "code": '''class ValueTrackerGraph(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-1, 5, 1], y_range=[-1, 8, 2],
            width=8, height=5,
            axis_config={"include_numbers": True},
        )
        axes.to_edge(DOWN, buff=0.5)
        graph = axes.get_graph(lambda x: 0.5 * x**2, color=BLUE)

        self.play(ShowCreation(axes), ShowCreation(graph))

        # Tracker controls the x position
        tracker = ValueTracker(0.5)

        dot = always_redraw(lambda: Dot(
            axes.c2p(tracker.get_value(), 0.5 * tracker.get_value()**2),
            color=YELLOW, radius=0.08,
        ))
        v_line = always_redraw(lambda: DashedLine(
            axes.c2p(tracker.get_value(), 0),
            axes.c2p(tracker.get_value(), 0.5 * tracker.get_value()**2),
            color=GREY, stroke_width=2,
        ))
        label = always_redraw(lambda: Text(
            f"({tracker.get_value():.1f}, {0.5 * tracker.get_value()**2:.1f})",
            font_size=24,
        ).next_to(dot, UR, buff=0.15))

        self.play(FadeIn(dot), ShowCreation(v_line), Write(label))
        self.play(tracker.animate.set_value(4), run_time=4, rate_func=smooth)
        self.play(tracker.animate.set_value(1.5), run_time=2)
        self.wait()
''',
    },
    "grid_transformation": {
        "description": "Apply a linear transformation to a grid, showing how the plane deforms. Core 3b1b linear algebra technique.",
        "code": '''class GridTransformation(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range=[-5, 5], y_range=[-4, 4],
            background_line_style={"stroke_opacity": 0.5},
        )
        # Basis vectors
        i_hat = Arrow(ORIGIN, RIGHT, buff=0, color=GREEN, stroke_width=5)
        j_hat = Arrow(ORIGIN, UP, buff=0, color=RED, stroke_width=5)

        self.play(ShowCreation(plane), run_time=1)
        self.play(GrowArrow(i_hat), GrowArrow(j_hat))
        self.wait()

        # Apply a rotation + scale matrix
        matrix = [[0, -1], [1, 0]]  # 90 degree rotation
        label = Text("90° rotation", font_size=32, color=YELLOW)
        label.to_corner(UL).set_backstroke(width=4)

        self.play(
            plane.animate.apply_matrix(matrix),
            i_hat.animate.put_start_and_end_on(ORIGIN, UP),
            j_hat.animate.put_start_and_end_on(ORIGIN, LEFT),
            Write(label),
            run_time=3,
        )
        self.wait(2)
''',
    },
    "vector_field_2d": {
        "description": "Visualize a 2D vector field with arrows. Inspired by 3b1b divergence/curl video.",
        "code": '''class VectorField2D(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range=[-5, 5], y_range=[-4, 4],
            background_line_style={"stroke_opacity": 0.3},
        )

        def func(point):
            x, y = point[:2]
            return np.array([-y, x, 0]) * 0.3

        field = VectorField(
            func, plane,
            x_range=[-4, 4],
            y_range=[-3, 3],
            density=2.0,
            stroke_color=BLUE,
            stroke_width=2,
        )

        title = Text("Rotational vector field", font_size=32)
        title.to_edge(UP).set_backstroke(width=4)

        self.play(ShowCreation(plane), run_time=1)
        self.play(ShowCreation(field), run_time=2)
        self.play(Write(title))
        self.wait(2)
''',
    },
    "color_gradient_surface": {
        "description": "Create a 3D surface colored by height. Common pattern for visualizing scalar fields.",
        "code": '''class ColorGradientSurface(ThreeDScene):
    def construct(self):
        frame = self.frame
        frame.reorient(30, 70)

        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-1, 2, 1],
        )

        surface = ParametricSurface(
            lambda u, v: np.array([
                u, v,
                np.exp(-(u**2 + v**2) / 2),
            ]),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(48, 48),
        )
        surface.set_color_by_gradient(BLUE, GREEN, YELLOW, RED)
        surface.set_opacity(0.8)

        title = Text("Gaussian bell curve in 2D", font_size=32)
        title.fix_in_frame()
        title.to_edge(UP)

        self.play(ShowCreation(axes), run_time=1)
        self.play(Write(title))
        self.play(ShowCreation(surface), run_time=3)
        self.play(frame.animate.reorient(150, 60), run_time=5)
        self.wait()
''',
    },
    "progressive_equation": {
        "description": "Build an equation step by step, highlighting each part. Key 3b1b presentation technique.",
        "code": '''class ProgressiveEquation(Scene):
    def construct(self):
        # Build up: distance = rate x time
        step1 = Text("distance", font_size=48, color=BLUE)
        step2 = Text("distance = rate", font_size=48)
        step2[0:8].set_color(BLUE)
        step2[10:14].set_color(GREEN)
        step3 = Text("distance = rate × time", font_size=48)
        step3[0:8].set_color(BLUE)
        step3[10:14].set_color(GREEN)
        step3[16:].set_color(RED)

        self.play(Write(step1))
        self.wait()
        self.play(FadeTransform(step1, step2))
        self.wait()
        self.play(FadeTransform(step2, step3))
        self.wait()

        # Box the final result
        box = SurroundingRectangle(step3, color=YELLOW, buff=0.2)
        self.play(ShowCreation(box))
        self.wait(2)
''',
    },
    "parametric_curve": {
        "description": "Animate drawing a parametric curve (Lissajous figure).",
        "code": '''class ParametricCurveExample(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-2, 2, 1], y_range=[-2, 2, 1],
            width=6, height=6,
        )

        curve = ParametricCurve(
            lambda t: axes.c2p(np.sin(3 * t), np.sin(2 * t)),
            t_range=[0, TAU],
            color=YELLOW,
            stroke_width=3,
        )

        title = Text("Lissajous curve (3:2)", font_size=32)
        title.to_edge(UP)

        self.play(ShowCreation(axes), Write(title))
        self.play(ShowCreation(curve), run_time=4, rate_func=linear)
        self.wait(2)
''',
    },
    "side_by_side": {
        "description": "Show two related views side by side — the 'dual view' pattern from 3b1b videos.",
        "code": '''class SideBySide(Scene):
    def construct(self):
        # Left: time domain
        left_axes = Axes(
            x_range=[0, 4*PI, PI], y_range=[-1.5, 1.5, 1],
            width=5.5, height=3,
        )
        left_axes.to_edge(LEFT, buff=0.5)
        left_title = Text("Time domain", font_size=28)
        left_title.next_to(left_axes, UP, buff=0.3)

        wave = left_axes.get_graph(lambda x: np.sin(x), color=BLUE)

        # Right: frequency domain (single spike)
        right_axes = Axes(
            x_range=[0, 5, 1], y_range=[0, 1.5, 0.5],
            width=5.5, height=3,
        )
        right_axes.to_edge(RIGHT, buff=0.5)
        right_title = Text("Frequency domain", font_size=28)
        right_title.next_to(right_axes, UP, buff=0.3)

        spike = Line(
            right_axes.c2p(1, 0), right_axes.c2p(1, 1),
            color=YELLOW, stroke_width=4,
        )
        spike_dot = Dot(right_axes.c2p(1, 1), color=YELLOW, radius=0.08)

        # Divider
        divider = DashedLine(3 * UP, 3 * DOWN, color=GREY, stroke_width=1)

        self.play(
            ShowCreation(left_axes), ShowCreation(right_axes),
            ShowCreation(divider),
            Write(left_title), Write(right_title),
            run_time=1.5,
        )
        self.play(ShowCreation(wave), run_time=2)
        self.play(ShowCreation(spike), FadeIn(spike_dot))
        self.wait(2)
''',
    },
    "camera_orbit_3d": {
        "description": "Orbit the camera around a 3D object to reveal its structure.",
        "code": '''class CameraOrbit3D(ThreeDScene):
    def construct(self):
        frame = self.frame
        frame.reorient(0, 75)

        # Torus
        torus = ParametricSurface(
            lambda u, v: np.array([
                (2 + 0.7 * np.cos(v)) * np.cos(u),
                (2 + 0.7 * np.cos(v)) * np.sin(u),
                0.7 * np.sin(v),
            ]),
            u_range=[0, TAU], v_range=[0, TAU],
            resolution=(48, 24),
        )
        torus.set_color_by_gradient(BLUE, TEAL, GREEN)
        torus.set_opacity(0.8)

        title = Text("Torus", font_size=36)
        title.fix_in_frame()
        title.to_corner(UL)

        self.play(ShowCreation(torus), Write(title), run_time=2)
        self.wait()

        # Full orbit
        self.play(frame.animate.reorient(360, 70), run_time=8, rate_func=linear)
        self.wait()
''',
    },
    "staggered_animation": {
        "description": "Use LaggedStartMap for staggered entrance animations. Common 3b1b pattern.",
        "code": '''class StaggeredAnimation(Scene):
    def construct(self):
        # Grid of colored squares
        squares = VGroup(
            Square(side_length=0.6, fill_opacity=0.8, fill_color=color)
            for color in color_gradient([BLUE, GREEN, YELLOW, RED], 25)
        )
        squares.arrange_in_grid(5, 5, buff=0.15)

        title = Text("LaggedStartMap demo", font_size=32)
        title.to_edge(UP)

        self.play(Write(title))
        self.play(LaggedStartMap(FadeIn, squares, lag_ratio=0.05), run_time=2)
        self.wait()
        self.play(LaggedStartMap(
            lambda m: m.animate.scale(0.5).set_opacity(0.3),
            squares,
            lag_ratio=0.03,
        ), run_time=2)
        self.wait()
''',
    },
    "updater_chain": {
        "description": "Chain multiple updaters so objects stay connected as one moves.",
        "code": '''class UpdaterChain(Scene):
    def construct(self):
        # A dot orbiting a circle, with a line and label tracking it
        circle = Circle(radius=2, color=BLUE_D, stroke_width=2)
        center_dot = Dot(ORIGIN, color=WHITE, radius=0.05)

        tracker = ValueTracker(0)

        moving_dot = always_redraw(lambda: Dot(
            2 * np.array([
                np.cos(tracker.get_value()),
                np.sin(tracker.get_value()),
                0,
            ]),
            color=YELLOW, radius=0.1,
        ))
        radius_line = always_redraw(lambda: Line(
            ORIGIN, moving_dot.get_center(),
            color=YELLOW, stroke_width=2,
        ))
        angle_arc = always_redraw(lambda: Arc(
            start_angle=0,
            angle=tracker.get_value() % TAU,
            radius=0.5,
            color=GREEN,
        ))
        angle_label = always_redraw(lambda: Text(
            f"{np.degrees(tracker.get_value() % TAU):.0f}°",
            font_size=24, color=GREEN,
        ).next_to(angle_arc, RIGHT, buff=0.1))

        self.add(circle, center_dot)
        self.add(moving_dot, radius_line, angle_arc, angle_label)
        self.play(tracker.animate.set_value(TAU), run_time=4, rate_func=linear)
        self.play(tracker.animate.set_value(3 * TAU), run_time=6, rate_func=linear)
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
