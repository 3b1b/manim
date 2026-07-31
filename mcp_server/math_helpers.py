"""
Reusable mathematical helper functions organized by domain.

These are code snippets an LLM can incorporate into scene code.
Distilled from patterns in the 3b1b/videos repository.
"""
from __future__ import annotations

HELPERS: dict[str, dict[str, str]] = {
    "calculus": {
        "description": "Derivatives, integrals, limits, Taylor series visualization helpers.",
        "code": r'''
# --- Calculus Helpers ---

def get_tangent_line(axes, graph, x, length=4, color=YELLOW):
    """Draw a tangent line to a graph at point x."""
    dx = 0.001
    x0 = x
    y0 = axes.p2c(graph.pfp(axes.x_axis.p2n(axes.c2p(x0, 0))))[1]
    # Numerical derivative
    y1 = axes.p2c(graph.pfp(axes.x_axis.p2n(axes.c2p(x0 + dx, 0))))[1]
    slope = (y1 - y0) / dx
    line = Line(
        axes.c2p(x0 - length/2, y0 - slope * length/2),
        axes.c2p(x0 + length/2, y0 + slope * length/2),
        color=color,
    )
    return line

def get_riemann_rects(axes, graph, x_range, dx=0.25, color=BLUE, opacity=0.5):
    """Create Riemann sum rectangles under a curve."""
    rects = VGroup()
    x = x_range[0]
    while x < x_range[1]:
        y = axes.p2c(graph.pfp(axes.x_axis.p2n(axes.c2p(x, 0))))[1]
        rect = Rectangle(
            width=axes.x_axis.get_unit_size() * dx,
            height=abs(y) * axes.y_axis.get_unit_size(),
            fill_color=color,
            fill_opacity=opacity,
            stroke_color=WHITE,
            stroke_width=1,
        )
        rect.move_to(axes.c2p(x + dx/2, y/2))
        rects.add(rect)
        x += dx
    return rects

def get_area_under_curve(axes, graph, x_range, color=BLUE, opacity=0.3):
    """Shade the area under a curve between x_range[0] and x_range[1]."""
    area = axes.get_area_under_graph(graph, x_range, color=color)
    area.set_fill(opacity=opacity)
    return area

def get_secant_line(axes, graph, x1, x2, length=6, color=RED):
    """Draw a secant line between two points on a graph."""
    p1 = graph.pfp(axes.x_axis.p2n(axes.c2p(x1, 0)))
    p2 = graph.pfp(axes.x_axis.p2n(axes.c2p(x2, 0)))
    direction = normalize(p2 - p1)
    line = Line(
        p1 - direction * length/2,
        p1 + direction * length/2,
        color=color,
    )
    return line
''',
    },
    "linear_algebra": {
        "description": "Matrix transformations, eigenvectors, basis vectors, grid deformations.",
        "code": r'''
# --- Linear Algebra Helpers ---

def get_basis_vectors(axes, colors=(GREEN, RED)):
    """Create labeled basis vectors i-hat and j-hat."""
    i_hat = Arrow(axes.c2p(0, 0), axes.c2p(1, 0), buff=0, color=colors[0])
    j_hat = Arrow(axes.c2p(0, 0), axes.c2p(0, 1), buff=0, color=colors[1])
    i_label = Text("î", font_size=30, color=colors[0])
    j_label = Text("ĵ", font_size=30, color=colors[1])
    i_label.next_to(i_hat, DOWN, buff=0.1)
    j_label.next_to(j_hat, LEFT, buff=0.1)
    return VGroup(i_hat, j_hat), VGroup(i_label, j_label)

def apply_matrix_to_points(matrix, points):
    """Apply a 2x2 matrix to an array of 2D points."""
    mat = np.array(matrix)
    result = np.zeros_like(points)
    result[:, :2] = (mat @ points[:, :2].T).T
    return result

def get_column_vectors(matrix, axes, colors=(GREEN, RED)):
    """Show where the basis vectors land after a matrix transformation."""
    col1 = Arrow(
        axes.c2p(0, 0),
        axes.c2p(matrix[0][0], matrix[1][0]),
        buff=0, color=colors[0],
    )
    col2 = Arrow(
        axes.c2p(0, 0),
        axes.c2p(matrix[0][1], matrix[1][1]),
        buff=0, color=colors[1],
    )
    return VGroup(col1, col2)

def get_eigen_line(axes, eigenvector, length=8, color=PURPLE):
    """Draw a line through the origin in the direction of an eigenvector."""
    direction = np.array([*eigenvector, 0])
    direction = direction / np.linalg.norm(direction)
    return DashedLine(
        axes.c2p(*(direction[:2] * -length/2)),
        axes.c2p(*(direction[:2] * length/2)),
        color=color,
    )
''',
    },
    "complex_analysis": {
        "description": "Complex plane, conformal maps, Euler's formula, Möbius transforms.",
        "code": r'''
# --- Complex Analysis Helpers ---

def complex_to_point(z):
    """Convert a complex number to a manim 3D point."""
    return np.array([z.real, z.imag, 0])

def point_to_complex(point):
    """Convert a manim point to a complex number."""
    return complex(point[0], point[1])

def get_complex_dot(z, color=YELLOW, radius=0.08):
    """Place a dot at a complex number on the plane."""
    return Dot(complex_to_point(z), color=color, radius=radius)

def get_unit_circle(plane, color=YELLOW, stroke_width=2):
    """Draw the unit circle on a complex plane."""
    return Circle(
        radius=plane.x_axis.get_unit_size(),
        color=color,
        stroke_width=stroke_width,
    ).move_to(plane.n2p(0))

def mobius_transform(z, a=0, b=1, c=1, d=0):
    """Apply a Möbius transformation (az + b) / (cz + d)."""
    denom = c * z + d
    if abs(denom) < 1e-10:
        return complex(1e10, 0)
    return (a * z + b) / denom

def stereographic_proj(points3d, epsilon=1e-10):
    """Project 3D sphere points to 2D plane via stereographic projection."""
    x, y, z = points3d.T
    denom = 1 - z
    denom[np.abs(denom) < epsilon] = np.inf
    return np.array([x / denom, y / denom, 0 * z]).T

def inv_stereographic_proj(points2d):
    """Inverse stereographic projection: 2D plane to 3D sphere."""
    u, v = points2d[:, 0], points2d[:, 1]
    norm_sq = u * u + v * v
    denom = 1 + norm_sq
    return np.array([
        2 * u / denom,
        2 * v / denom,
        (norm_sq - 1) / denom,
    ]).T
''',
    },
    "vector_calculus": {
        "description": "Vector fields, divergence, curl, line integrals, surface integrals.",
        "code": r'''
# --- Vector Calculus Helpers ---

def numerical_gradient(scalar_func, point, dt=1e-7):
    """Compute the gradient of a scalar function at a point."""
    p = np.array(point, dtype=float)
    grad = np.zeros(3)
    f0 = scalar_func(p)
    for i in range(3):
        dp = np.zeros(3)
        dp[i] = dt
        grad[i] = (scalar_func(p + dp) - f0) / dt
    return grad

def numerical_divergence(vector_func, point, dt=1e-7):
    """Compute divergence of a vector field at a point."""
    p = np.array(point, dtype=float)
    div = 0
    v0 = vector_func(p)
    for i in range(3):
        dp = np.zeros(3)
        dp[i] = dt
        div += (vector_func(p + dp)[i] - v0[i]) / dt
    return div

def numerical_curl_2d(vector_func, point, dt=1e-7):
    """Compute the z-component of curl for a 2D vector field."""
    p = np.array(point, dtype=float)
    v0 = vector_func(p)
    dvx_dy = (vector_func(p + dt * UP)[0] - v0[0]) / dt
    dvy_dx = (vector_func(p + dt * RIGHT)[1] - v0[1]) / dt
    return dvy_dx - dvx_dy

def get_flow_field(func, axes, x_range=(-5, 5), y_range=(-5, 5),
                   density=1.0, color=BLUE, stroke_width=1):
    """Create a vector field visualization."""
    return VectorField(
        func, axes,
        x_range=x_range,
        y_range=y_range,
        density=density,
        stroke_color=color,
        stroke_width=stroke_width,
    )
''',
    },
    "differential_geometry": {
        "description": "Surfaces, curvature, tangent planes, geodesics, Gauss map.",
        "code": r'''
# --- Differential Geometry Helpers ---

def parametric_sphere(radius=1):
    """Create a parametric sphere surface."""
    return ParametricSurface(
        lambda u, v: radius * np.array([
            np.sin(u) * np.cos(v),
            np.sin(u) * np.sin(v),
            np.cos(u),
        ]),
        u_range=[0, PI],
        v_range=[0, TAU],
        resolution=(48, 48),
    )

def parametric_torus(R=2, r=0.7):
    """Create a parametric torus surface."""
    return ParametricSurface(
        lambda u, v: np.array([
            (R + r * np.cos(v)) * np.cos(u),
            (R + r * np.cos(v)) * np.sin(u),
            r * np.sin(v),
        ]),
        u_range=[0, TAU],
        v_range=[0, TAU],
        resolution=(48, 48),
    )

def parametric_mobius(width=1):
    """Create a Möbius strip surface."""
    return ParametricSurface(
        lambda u, v: np.array([
            (1 + v/2 * np.cos(u/2)) * np.cos(u),
            (1 + v/2 * np.cos(u/2)) * np.sin(u),
            v/2 * np.sin(u/2),
        ]),
        u_range=[0, TAU],
        v_range=[-width, width],
        resolution=(64, 16),
    )

def get_tangent_vectors(surface_func, u, v, scale=0.5, du=0.001, dv=0.001):
    """Compute tangent vectors to a parametric surface at (u, v)."""
    p = surface_func(u, v)
    tu = (surface_func(u + du, v) - p) / du * scale
    tv = (surface_func(u, v + dv) - p) / dv * scale
    return tu, tv

def get_normal_vector(surface_func, u, v, scale=0.5, du=0.001, dv=0.001):
    """Compute the unit normal to a parametric surface at (u, v)."""
    tu, tv = get_tangent_vectors(surface_func, u, v, 1.0, du, dv)
    normal = np.cross(tu, tv)
    norm = np.linalg.norm(normal)
    if norm < 1e-10:
        return np.array([0, 0, 1.0])
    return normal / norm * scale

def fibonacci_sphere_points(n=1000):
    """Generate approximately uniform points on a unit sphere."""
    phi = np.pi * (np.sqrt(5) - 1)  # golden angle
    indices = np.arange(n)
    y = 1 - (indices / (n - 1)) * 2
    radius = np.sqrt(1 - y * y)
    theta = phi * indices
    x = np.cos(theta) * radius
    z = np.sin(theta) * radius
    return np.column_stack([x, y, z])
''',
    },
    "probability": {
        "description": "Distributions, Bayes' theorem, random walks, central limit theorem.",
        "code": r'''
# --- Probability Helpers ---

def get_bar_chart(axes, values, width=0.6, colors=None, opacity=0.8):
    """Create a bar chart from a list of values."""
    if colors is None:
        colors = color_gradient([BLUE, GREEN], len(values))
    bars = VGroup()
    for i, (val, col) in enumerate(zip(values, colors)):
        bar = Rectangle(
            width=width * axes.x_axis.get_unit_size(),
            height=val * axes.y_axis.get_unit_size(),
            fill_color=col,
            fill_opacity=opacity,
            stroke_color=WHITE,
            stroke_width=1,
        )
        bar.move_to(axes.c2p(i + 0.5, val / 2))
        bars.add(bar)
    return bars

def gaussian(x, mu=0, sigma=1):
    """Standard Gaussian/normal distribution PDF."""
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))

def binomial_pmf(n, k, p=0.5):
    """Binomial distribution PMF."""
    from math import comb
    return comb(n, k) * p**k * (1 - p)**(n - k)

def random_walk_points(n_steps=100, step_size=0.3):
    """Generate a 2D random walk as a list of points."""
    angles = np.random.uniform(0, TAU, n_steps)
    steps = step_size * np.column_stack([np.cos(angles), np.sin(angles), np.zeros(n_steps)])
    return np.cumsum(steps, axis=0)
''',
    },
}


def get_math_helpers(domain: str) -> dict:
    """
    Get reusable math helper functions for a domain.

    Args:
        domain: One of the available domains.

    Returns:
        Dict with "description" and "code", or error with available domains.
    """
    if domain in HELPERS:
        return HELPERS[domain]
    return {
        "error": f"Unknown domain '{domain}'.",
        "available_domains": list(HELPERS.keys()),
    }
