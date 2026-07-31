"""
Structured topic templates for mathematical video creation.

Each template follows 3b1b pedagogy: concrete before abstract,
geometry before algebra, progressive revelation.
"""
from __future__ import annotations

TOPICS: dict[str, dict] = {
    # ===== BASIC =====
    "area_of_circle": {
        "title": "Why is the area of a circle πr²?",
        "level": "basic",
        "category": "geometry",
        "description": "Derive the area formula by unwrapping concentric rings into a triangle. Inspired by 3b1b Essence of Calculus chapter 1.",
        "concept_arc": [
            "Show a filled circle with radius R",
            "Peel off concentric rings and unroll them",
            "Each ring becomes a thin rectangle: width = 2πr, height = dr",
            "Stack the rectangles — they form a triangle",
            "Triangle area = ½ × base × height = ½ × 2πR × R = πR²",
        ],
        "scenes": [
            {
                "name": "CircleAreaDerivation",
                "description": "Unwrap concentric rings to derive πr².",
                "code": r'''class CircleAreaDerivation(Scene):
    def construct(self):
        # Show circle
        radius = 2.0
        circle = Circle(radius=radius, color=BLUE, fill_opacity=0.5)
        r_line = Line(ORIGIN, radius * RIGHT, color=YELLOW)
        r_label = Text("R", font_size=36, color=YELLOW)
        r_label.next_to(r_line, DOWN, buff=0.1)

        self.play(ShowCreation(circle))
        self.play(ShowCreation(r_line), Write(r_label))
        self.wait()

        # Show concentric rings
        n_rings = 15
        rings = VGroup()
        colors = color_gradient([BLUE_E, GREEN_C], n_rings)
        for i in range(n_rings):
            r_inner = radius * i / n_rings
            r_outer = radius * (i + 1) / n_rings
            ring = Annulus(
                inner_radius=r_inner,
                outer_radius=r_outer,
                fill_color=colors[i],
                fill_opacity=0.8,
                stroke_color=WHITE,
                stroke_width=0.5,
            )
            rings.add(ring)

        self.play(
            FadeOut(circle),
            FadeIn(rings),
            run_time=1.5,
        )
        self.wait()

        # Unroll rings into rectangles on the right
        axes = Axes(
            x_range=[0, 2.5 * PI, PI],
            y_range=[0, 2.5, 0.5],
            width=6, height=3,
        )
        axes.to_edge(RIGHT)

        rects = VGroup()
        for i in range(n_rings):
            r_mid = radius * (i + 0.5) / n_rings
            dr = radius / n_rings
            width = 2 * PI * r_mid
            rect = Rectangle(
                width=width * axes.x_axis.get_unit_size(),
                height=dr * axes.y_axis.get_unit_size(),
                fill_color=colors[i],
                fill_opacity=0.8,
                stroke_width=0.5,
            )
            rect.move_to(axes.c2p(width / 2, dr * i + dr / 2))
            rects.add(rect)

        self.play(
            rings.animate.scale(0.4).to_edge(LEFT),
            ShowCreation(axes),
            run_time=1.5,
        )
        self.play(
            LaggedStartMap(FadeIn, rects, lag_ratio=0.05),
            run_time=2,
        )
        self.wait()

        # Show triangle outline and formula
        triangle = Polygon(
            axes.c2p(0, 0),
            axes.c2p(2 * PI * radius, 0),
            axes.c2p(0, radius),
            stroke_color=YELLOW,
            stroke_width=3,
            fill_opacity=0,
        )
        formula = Text("Area = ½ × 2πR × R = πR²", font_size=32)
        formula.next_to(axes, DOWN, buff=0.5)

        self.play(ShowCreation(triangle))
        self.play(Write(formula))
        self.wait(2)
''',
            },
        ],
    },
    "pythagorean_theorem": {
        "title": "A Visual Proof of the Pythagorean Theorem",
        "level": "basic",
        "category": "geometry",
        "description": "Prove a² + b² = c² by rearranging squares built on the sides of a right triangle.",
        "concept_arc": [
            "Show a right triangle with sides a, b, c",
            "Build squares on each side",
            "Animate the rearrangement proof",
            "Show the algebraic identity emerging from the geometry",
        ],
        "scenes": [
            {
                "name": "PythagoreanProof",
                "description": "Visual rearrangement proof of the Pythagorean theorem.",
                "code": r'''class PythagoreanProof(Scene):
    def construct(self):
        # Right triangle
        a, b = 1.5, 2.0
        c = np.sqrt(a**2 + b**2)
        triangle = Polygon(
            ORIGIN, a * RIGHT, a * RIGHT + b * UP,
            stroke_color=WHITE, stroke_width=3,
            fill_color=BLUE_E, fill_opacity=0.3,
        )
        triangle.move_to(ORIGIN)

        # Labels
        a_label = Text("a", font_size=36, color=GREEN)
        b_label = Text("b", font_size=36, color=RED)
        c_label = Text("c", font_size=36, color=YELLOW)

        verts = triangle.get_vertices()
        a_label.next_to(Line(verts[0], verts[1]), DOWN, buff=0.2)
        b_label.next_to(Line(verts[1], verts[2]), RIGHT, buff=0.2)
        c_label.next_to(Line(verts[0], verts[2]), LEFT, buff=0.2)

        self.play(ShowCreation(triangle))
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait()

        # Squares on each side
        sq_a = Square(side_length=a, color=GREEN, fill_opacity=0.4)
        sq_b = Square(side_length=b, color=RED, fill_opacity=0.4)
        sq_c = Square(side_length=c, color=YELLOW, fill_opacity=0.4)

        sq_a.next_to(Line(verts[0], verts[1]), DOWN, buff=0)
        sq_b.next_to(Line(verts[1], verts[2]), RIGHT, buff=0)
        sq_c.next_to(Line(verts[0], verts[2]), LEFT, buff=0)

        for sq in [sq_a, sq_b, sq_c]:
            self.play(GrowFromCenter(sq), run_time=0.8)
        self.wait()

        # Show equation
        equation = Text("a² + b² = c²", font_size=48)
        equation.to_edge(UP)
        self.play(Write(equation))
        self.wait(2)
''',
            },
        ],
    },
    # ===== INTERMEDIATE =====
    "linear_transformations": {
        "title": "Linear Transformations as Matrix Multiplication",
        "level": "intermediate",
        "category": "linear_algebra",
        "description": "Show how a 2x2 matrix transforms the plane by tracking where basis vectors land. Inspired by 3b1b Essence of Linear Algebra chapter 3.",
        "concept_arc": [
            "Show the standard grid with basis vectors i-hat and j-hat",
            "Apply a matrix transformation — watch the grid deform",
            "Highlight that i-hat and j-hat land on the columns of the matrix",
            "Show that every vector's destination is determined by the basis",
        ],
        "scenes": [
            {
                "name": "MatrixTransformation",
                "description": "Visualize a 2x2 matrix as a grid transformation.",
                "code": r'''class MatrixTransformation(Scene):
    def construct(self):
        # Setup grid
        plane = NumberPlane(
            x_range=[-4, 4], y_range=[-3, 3],
            background_line_style={"stroke_opacity": 0.4},
        )
        plane.add_coordinate_labels(font_size=20)

        # Basis vectors
        i_hat = Arrow(ORIGIN, RIGHT, buff=0, color=GREEN, stroke_width=6)
        j_hat = Arrow(ORIGIN, UP, buff=0, color=RED, stroke_width=6)
        i_label = Text("î", font_size=30, color=GREEN).next_to(i_hat, DOWN, 0.1)
        j_label = Text("ĵ", font_size=30, color=RED).next_to(j_hat, LEFT, 0.1)

        self.play(ShowCreation(plane), run_time=1.5)
        self.play(
            GrowArrow(i_hat), GrowArrow(j_hat),
            Write(i_label), Write(j_label),
        )
        self.wait()

        # The matrix [[1, 1], [0, 1]] — a shear
        matrix = [[1, 1], [0, 1]]

        # Show matrix
        matrix_label = Text("[[1, 1], [0, 1]]", font_size=32)
        matrix_label.to_corner(UL)
        matrix_label.set_backstroke(width=4)
        self.play(Write(matrix_label))

        # Apply transformation
        self.play(
            plane.animate.apply_matrix(matrix),
            i_hat.animate.put_start_and_end_on(ORIGIN, np.array([1, 0, 0])),
            j_hat.animate.put_start_and_end_on(ORIGIN, np.array([1, 1, 0])),
            i_label.animate.next_to(np.array([1, 0, 0]), DOWN, 0.1),
            j_label.animate.next_to(np.array([1, 1, 0]), LEFT, 0.1),
            run_time=3,
        )
        self.wait()

        # Highlight columns
        col_note = Text(
            "Columns = where î and ĵ land",
            font_size=28, color=YELLOW,
        )
        col_note.to_edge(DOWN)
        col_note.set_backstroke(width=4)
        self.play(Write(col_note))
        self.wait(2)
''',
            },
        ],
    },
    "complex_multiplication": {
        "title": "Complex Multiplication is Rotation and Scaling",
        "level": "intermediate",
        "category": "complex_analysis",
        "description": "Show that multiplying complex numbers rotates and scales. Visualize on the complex plane.",
        "concept_arc": [
            "Show the complex plane with a point z",
            "Multiply by a complex number w — watch z rotate and scale",
            "Show the polar form: |w| scales, arg(w) rotates",
            "Euler's formula connects this to e^(iθ)",
        ],
        "scenes": [
            {
                "name": "ComplexMultiplication",
                "description": "Visualize complex multiplication as rotation + scaling.",
                "code": r'''class ComplexMultiplication(Scene):
    def construct(self):
        # Complex plane
        plane = ComplexPlane(
            x_range=[-3, 3], y_range=[-3, 3],
            width=6, height=6,
        )
        plane.add_coordinate_labels(font_size=20)
        self.play(ShowCreation(plane), run_time=1.5)

        # Point z = 1 + 0.5i
        z = complex(2, 0.5)
        z_dot = Dot(plane.n2p(z), color=YELLOW, radius=0.1)
        z_label = Text("z", font_size=30, color=YELLOW)
        z_label.next_to(z_dot, UR, buff=0.1)
        z_line = Line(plane.n2p(0), plane.n2p(z), color=YELLOW, stroke_width=2)

        self.play(ShowCreation(z_line), FadeIn(z_dot), Write(z_label))
        self.wait()

        # Multiplier w = e^(iπ/4) ≈ rotation by 45°
        w = np.exp(1j * PI / 4)
        result = z * w

        # Show the rotation
        arc = Arc(
            start_angle=np.angle(z),
            angle=np.angle(w),
            radius=0.8,
            color=GREEN,
            stroke_width=3,
        ).move_arc_center_to(plane.n2p(0))
        angle_label = Text("45°", font_size=24, color=GREEN)
        angle_label.next_to(arc, RIGHT, buff=0.1)

        result_dot = Dot(plane.n2p(result), color=RED, radius=0.1)
        result_line = Line(plane.n2p(0), plane.n2p(result), color=RED, stroke_width=2)
        result_label = Text("z·w", font_size=30, color=RED)
        result_label.next_to(result_dot, UR, buff=0.1)

        self.play(ShowCreation(arc), Write(angle_label))
        self.play(
            ShowCreation(result_line),
            FadeIn(result_dot),
            Write(result_label),
            run_time=1.5,
        )
        self.wait()

        # Caption
        caption = Text(
            "Multiplying by w rotates by arg(w) and scales by |w|",
            font_size=28,
        )
        caption.to_edge(DOWN)
        caption.set_backstroke(width=4)
        self.play(Write(caption))
        self.wait(2)
''',
            },
        ],
    },
    # ===== CALCULUS =====
    "derivative_as_slope": {
        "title": "The Derivative as the Slope of a Tangent Line",
        "level": "calculus",
        "category": "calculus",
        "description": "Show the derivative visually: zoom into a curve until it looks like a straight line, and measure its slope.",
        "concept_arc": [
            "Plot f(x) = x² and pick a point",
            "Draw a secant line between two nearby points",
            "Animate the second point approaching the first",
            "The secant becomes the tangent — its slope is the derivative",
            "Show the slope value changing as we move along the curve",
        ],
        "scenes": [
            {
                "name": "DerivativeAsSlope",
                "description": "Animate secant lines converging to the tangent.",
                "code": r'''class DerivativeAsSlope(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-1, 4, 1], y_range=[-1, 10, 2],
            width=8, height=5,
            axis_config={"include_numbers": True},
        )
        axes.to_edge(DOWN, buff=0.5)
        graph = axes.get_graph(lambda x: x**2, color=BLUE)
        graph_label = Text("f(x) = x²", font_size=30, color=BLUE)
        graph_label.to_corner(UR)

        self.play(ShowCreation(axes), ShowCreation(graph), Write(graph_label))
        self.wait()

        # Fixed point
        x0 = 1.5
        dot0 = Dot(axes.c2p(x0, x0**2), color=YELLOW, radius=0.08)
        self.play(FadeIn(dot0))

        # Animate secant lines approaching tangent
        dx_tracker = ValueTracker(2.0)
        secant = always_redraw(lambda: Line(
            axes.c2p(x0, x0**2),
            axes.c2p(
                x0 + dx_tracker.get_value(),
                (x0 + dx_tracker.get_value())**2,
            ),
            color=RED,
            stroke_width=3,
        ).scale(3, about_point=axes.c2p(x0, x0**2)))

        dot1 = always_redraw(lambda: Dot(
            axes.c2p(
                x0 + dx_tracker.get_value(),
                (x0 + dx_tracker.get_value())**2,
            ),
            color=RED, radius=0.06,
        ))

        slope_label = always_redraw(lambda: Text(
            f"slope = {((x0 + dx_tracker.get_value())**2 - x0**2) / dx_tracker.get_value():.2f}",
            font_size=28,
        ).to_corner(UL))

        self.play(ShowCreation(secant), FadeIn(dot1), Write(slope_label))
        self.wait(0.5)

        # Shrink dx
        self.play(dx_tracker.animate.set_value(0.01), run_time=4)
        self.wait()

        # Final label
        result = Text("f'(1.5) = 2 × 1.5 = 3.0", font_size=32, color=YELLOW)
        result.to_edge(DOWN)
        self.play(Write(result))
        self.wait(2)
''',
            },
        ],
    },
    "fourier_series": {
        "title": "Fourier Series: Building Any Function from Sine Waves",
        "level": "calculus",
        "category": "calculus",
        "description": "Show how adding sine waves of different frequencies can approximate any periodic function.",
        "concept_arc": [
            "Show a square wave — a function that seems impossible to build from smooth curves",
            "Add the first sine harmonic — a rough approximation",
            "Add the 3rd, 5th, 7th harmonics one by one",
            "Watch the approximation converge to the square wave",
        ],
        "scenes": [
            {
                "name": "FourierApproximation",
                "description": "Progressively add harmonics to approximate a square wave.",
                "code": r'''class FourierApproximation(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-PI, PI, PI/2],
            y_range=[-1.5, 1.5, 0.5],
            width=10, height=4,
        )
        axes.to_edge(DOWN, buff=1)

        # Target: square wave
        square_wave = axes.get_graph(
            lambda x: 1 if x > 0 else (-1 if x < 0 else 0),
            discontinuities=[0],
            color=WHITE,
            stroke_width=2,
        )

        title = Text("Fourier Series Approximation", font_size=36)
        title.to_edge(UP)

        self.play(ShowCreation(axes), Write(title))
        self.play(ShowCreation(square_wave), run_time=1.5)
        self.wait()

        # Build up Fourier approximation
        def fourier_partial_sum(n_terms):
            def func(x):
                result = 0
                for k in range(n_terms):
                    n = 2 * k + 1  # odd harmonics only
                    result += (4 / (n * PI)) * np.sin(n * x)
                return result
            return func

        colors = color_gradient([BLUE, GREEN, YELLOW], 8)
        current_graph = None

        for i in range(1, 9):
            new_graph = axes.get_graph(
                fourier_partial_sum(i),
                color=colors[i - 1],
                stroke_width=3,
            )
            n_label = Text(
                f"{i} term{'s' if i > 1 else ''}",
                font_size=28, color=colors[i - 1],
            )
            n_label.next_to(axes, RIGHT, buff=0.3)

            if current_graph is None:
                self.play(ShowCreation(new_graph), Write(n_label), run_time=1.5)
            else:
                self.play(
                    Transform(current_graph, new_graph),
                    Transform(prev_label, n_label),
                    run_time=1,
                )

            if current_graph is None:
                current_graph = new_graph
                prev_label = n_label
            self.wait(0.3)

        self.wait(2)
''',
            },
        ],
    },
    # ===== ADVANCED =====
    "curvature_of_surfaces": {
        "title": "Gaussian Curvature: How Surfaces Bend",
        "level": "advanced",
        "category": "differential_geometry",
        "description": "Visualize Gaussian curvature by showing how surfaces with positive, zero, and negative curvature differ. Sphere vs cylinder vs saddle.",
        "concept_arc": [
            "Show a sphere — positive curvature everywhere",
            "Show a cylinder — zero Gaussian curvature (flat in one direction)",
            "Show a saddle surface — negative curvature",
            "Color-code curvature on a general surface",
        ],
        "scenes": [
            {
                "name": "GaussianCurvature",
                "description": "Compare surfaces with positive, zero, and negative Gaussian curvature.",
                "code": r'''class GaussianCurvature(ThreeDScene):
    def construct(self):
        frame = self.frame
        frame.reorient(20, 70)

        # Sphere (positive curvature)
        sphere = ParametricSurface(
            lambda u, v: np.array([
                np.sin(u) * np.cos(v),
                np.sin(u) * np.sin(v),
                np.cos(u),
            ]),
            u_range=[0, PI], v_range=[0, TAU],
            resolution=(32, 32),
        )
        sphere.set_color(BLUE)
        sphere.set_opacity(0.7)
        sphere.shift(3 * LEFT)

        # Cylinder (zero curvature)
        cylinder = ParametricSurface(
            lambda u, v: np.array([
                np.cos(v),
                np.sin(v),
                u,
            ]),
            u_range=[-1.2, 1.2], v_range=[0, TAU],
            resolution=(16, 32),
        )
        cylinder.set_color(GREEN)
        cylinder.set_opacity(0.7)

        # Saddle (negative curvature)
        saddle = ParametricSurface(
            lambda u, v: np.array([u, v, u**2 - v**2]),
            u_range=[-1, 1], v_range=[-1, 1],
            resolution=(32, 32),
        )
        saddle.set_color(RED)
        saddle.set_opacity(0.7)
        saddle.shift(3 * RIGHT)

        # Labels (fixed in frame)
        labels = VGroup(
            Text("K > 0", font_size=28, color=BLUE),
            Text("K = 0", font_size=28, color=GREEN),
            Text("K < 0", font_size=28, color=RED),
        )
        labels.arrange(RIGHT, buff=2.5)
        labels.to_edge(UP)
        for label in labels:
            label.fix_in_frame()

        # Animate
        self.play(
            ShowCreation(sphere),
            Write(labels[0]),
            run_time=2,
        )
        self.play(
            ShowCreation(cylinder),
            Write(labels[1]),
            run_time=2,
        )
        self.play(
            ShowCreation(saddle),
            Write(labels[2]),
            run_time=2,
        )
        self.wait()

        # Rotate camera
        self.play(
            frame.animate.reorient(160, 60),
            run_time=6,
            rate_func=smooth,
        )
        self.wait(2)
''',
            },
        ],
    },
    "stereographic_projection": {
        "title": "Stereographic Projection: Mapping a Sphere to a Plane",
        "level": "advanced",
        "category": "differential_geometry",
        "description": "Visualize how stereographic projection maps circles on a sphere to circles on a plane, preserving angles. Inspired by 3b1b's hairy ball and holomorphic dynamics videos.",
        "concept_arc": [
            "Show a sphere sitting on a plane",
            "Draw a point on the sphere and project it from the north pole to the plane",
            "Show circles on the sphere mapping to circles on the plane",
            "Demonstrate angle preservation (conformality)",
        ],
        "scenes": [
            {
                "name": "StereographicProjection",
                "description": "Animate stereographic projection from sphere to plane.",
                "code": r'''class StereographicProjection(ThreeDScene):
    def construct(self):
        frame = self.frame
        frame.reorient(30, 65)

        # Sphere
        sphere = ParametricSurface(
            lambda u, v: np.array([
                np.sin(u) * np.cos(v),
                np.sin(u) * np.sin(v),
                np.cos(u),
            ]),
            u_range=[0.05, PI], v_range=[0, TAU],
            resolution=(32, 48),
        )
        sphere.set_color(BLUE_D)
        sphere.set_opacity(0.4)

        # North pole
        north_pole = Dot3D(np.array([0, 0, 1]), color=RED, radius=0.06)

        # Plane at z = 0
        plane = ParametricSurface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-3, 3], v_range=[-3, 3],
            resolution=(1, 1),
        )
        plane.set_color(GREY)
        plane.set_opacity(0.15)

        self.play(ShowCreation(sphere), FadeIn(north_pole), FadeIn(plane))
        self.wait()

        # Project latitude circles
        for phi in [PI/6, PI/3, PI/2, 2*PI/3]:
            # Circle on sphere
            theta_range = np.linspace(0, TAU, 100)
            sphere_points = np.array([
                [np.sin(phi)*np.cos(t), np.sin(phi)*np.sin(t), np.cos(phi)]
                for t in theta_range
            ])
            sphere_circle = VMobject()
            sphere_circle.set_points_smoothly([*sphere_points, sphere_points[0]])
            sphere_circle.set_stroke(YELLOW, 3)

            # Projected circle on plane
            z_vals = sphere_points[:, 2]
            denom = 1 - z_vals
            denom[denom == 0] = 1e-10
            proj_points = np.column_stack([
                sphere_points[:, 0] / denom,
                sphere_points[:, 1] / denom,
                np.zeros(len(denom)),
            ])
            plane_circle = VMobject()
            plane_circle.set_points_smoothly([*proj_points, proj_points[0]])
            plane_circle.set_stroke(GREEN, 3)

            # Projection lines (a few sample lines)
            lines = VGroup()
            for i in range(0, len(sphere_points), 25):
                line = Line(
                    np.array([0, 0, 1]),
                    proj_points[i],
                    stroke_color=WHITE,
                    stroke_width=1,
                    stroke_opacity=0.3,
                )
                lines.add(line)

            self.play(
                ShowCreation(sphere_circle),
                ShowCreation(lines),
                run_time=1,
            )
            self.play(ShowCreation(plane_circle), run_time=1)
            self.wait(0.3)

        # Rotate to appreciate
        self.play(frame.animate.reorient(180, 50), run_time=5)
        self.wait(2)
''',
            },
        ],
    },
}


# --- Lookup functions ---

LEVELS = ["basic", "intermediate", "calculus", "advanced"]
CATEGORIES = sorted(set(t["category"] for t in TOPICS.values()))


def list_topics(category: str | None = None, level: str | None = None) -> list[dict]:
    """List available topic templates, optionally filtered."""
    results = []
    for key, topic in TOPICS.items():
        if category and topic["category"] != category:
            continue
        if level and topic["level"] != level:
            continue
        results.append({
            "id": key,
            "title": topic["title"],
            "level": topic["level"],
            "category": topic["category"],
            "description": topic["description"],
            "n_scenes": len(topic["scenes"]),
        })
    return results


def get_topic_template(topic_id: str) -> dict:
    """Get the full template for a topic, including all scene code."""
    if topic_id in TOPICS:
        return TOPICS[topic_id]
    return {
        "error": f"Unknown topic '{topic_id}'.",
        "available_topics": [
            {"id": k, "title": v["title"]} for k, v in TOPICS.items()
        ],
    }
