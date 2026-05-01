"""
Video planning engine.

Takes a math topic description and assembles relevant context
from templates, helpers, and style guides to help an LLM
create a multi-scene math video.
"""
from __future__ import annotations

from mcp_server.topics import TOPICS
from mcp_server.math_helpers import HELPERS
from mcp_server.style_guide import STYLE_GUIDE, PEDAGOGY_GUIDE
from mcp_server.examples import EXAMPLES


# Map keywords to topic IDs for matching
_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "area_of_circle": [
        "circle", "area", "pi r squared", "πr²", "concentric",
        "rings", "circumference",
    ],
    "pythagorean_theorem": [
        "pythagorean", "pythagoras", "a² + b²", "right triangle",
        "hypotenuse",
    ],
    "linear_transformations": [
        "linear transformation", "matrix", "basis vector",
        "shear", "rotation matrix", "grid", "i-hat", "j-hat",
        "determinant", "eigenvalue", "eigenvector", "eigen",
    ],
    "complex_multiplication": [
        "complex number", "complex multiplication", "rotation",
        "euler", "polar form", "argand", "imaginary",
    ],
    "derivative_as_slope": [
        "derivative", "slope", "tangent", "secant", "limit",
        "differentiation", "rate of change", "dx",
    ],
    "fourier_series": [
        "fourier", "sine wave", "harmonic", "frequency",
        "square wave", "periodic", "spectrum",
    ],
    "curvature_of_surfaces": [
        "curvature", "gaussian curvature", "sphere", "saddle",
        "cylinder", "surface", "bend", "principal curvature",
    ],
    "stereographic_projection": [
        "stereographic", "projection", "sphere to plane",
        "conformal", "map", "riemann sphere",
    ],
}

# Map keywords to helper domains
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "calculus": [
        "derivative", "integral", "limit", "tangent", "area under",
        "riemann", "taylor", "series", "convergence", "dx", "dy",
        "rate of change", "fundamental theorem", "antiderivative",
        "calculus",
    ],
    "linear_algebra": [
        "matrix", "vector", "eigenvalue", "eigenvector", "eigen", "basis",
        "linear transformation", "determinant", "span", "null space",
        "rank", "linear algebra", "dot product", "cross product",
    ],
    "complex_analysis": [
        "complex", "imaginary", "euler", "conformal", "analytic",
        "holomorphic", "residue", "contour", "möbius", "mobius",
        "complex plane", "argand",
    ],
    "vector_calculus": [
        "vector field", "divergence", "curl", "gradient", "flux",
        "line integral", "surface integral", "stokes", "green",
        "gauss", "conservative",
    ],
    "differential_geometry": [
        "curvature", "geodesic", "manifold", "surface", "tangent plane",
        "normal", "gauss map", "first fundamental form", "torus",
        "möbius strip", "klein bottle", "differential geometry",
        "stereographic", "topology",
    ],
    "probability": [
        "probability", "distribution", "gaussian", "normal",
        "binomial", "random walk", "expected value", "variance",
        "bayes", "central limit", "histogram", "dice", "coin",
    ],
}

# Map keywords to example IDs
_EXAMPLE_KEYWORDS: dict[str, list[str]] = {
    "value_tracker_graph": [
        "tracker", "sliding", "dynamic label", "moving dot",
        "derivative", "slope", "tangent", "curve", "function plot",
    ],
    "grid_transformation": [
        "grid", "linear transformation", "deform", "matrix",
        "basis", "shear", "rotation", "eigen", "stretch",
    ],
    "vector_field_2d": [
        "vector field", "arrows", "flow", "divergence", "curl",
        "gradient", "force field",
    ],
    "color_gradient_surface": [
        "3d surface", "height color", "gradient", "bell curve",
        "gaussian", "scalar field", "heat map",
    ],
    "progressive_equation": [
        "equation", "step by step", "highlight", "formula",
        "build up", "derivation",
    ],
    "parametric_curve": [
        "parametric", "lissajous", "curve drawing", "polar",
        "cycloid", "spiral",
    ],
    "side_by_side": [
        "dual view", "side by side", "frequency", "time domain",
        "fourier", "comparison", "two representations",
    ],
    "camera_orbit_3d": [
        "orbit", "camera rotation", "3d", "torus", "sphere",
        "surface", "möbius", "mobius", "manifold", "topology",
    ],
    "staggered_animation": [
        "staggered", "lagged", "sequential", "grid", "many objects",
        "array", "collection",
    ],
    "updater_chain": [
        "updater", "tracking", "connected", "orbit", "circle",
        "angle", "dynamic", "linked",
    ],
    "basic_shapes": ["circle", "square", "triangle", "shapes", "geometry"],
    "transform": ["transform", "morph", "interpolate", "transition"],
    "graph": ["graph", "plot", "function", "axes", "sine", "cosine"],
    "3d": ["3d surface", "parametric surface", "3d plot"],
    "number_line": ["number line", "real line", "interval"],
    "complex_plane": ["complex plane", "z squared", "complex function"],
    "text_animation": ["text", "write", "fade", "title", "label"],
}


def _score_match(query: str, keywords: list[str]) -> int:
    """Count how many keywords appear in the query."""
    query_lower = query.lower()
    return sum(1 for kw in keywords if kw in query_lower)


def _find_best_matches(query: str, keyword_map: dict[str, list[str]], top_n: int = 3) -> list[str]:
    """Return the top_n best-matching keys from a keyword map."""
    scored = [
        (key, _score_match(query, keywords))
        for key, keywords in keyword_map.items()
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [key for key, score in scored[:top_n] if score > 0]


def create_video_plan(
    topic: str,
    level: str = "intermediate",
    duration_hint: str = "medium",
) -> dict:
    """
    Create a structured video plan for a math topic.

    Assembles relevant templates, helpers, examples, and style
    guidance based on the topic description.

    Args:
        topic: Natural language description of the math concept.
        level: Target difficulty — basic, intermediate, calculus, advanced.
        duration_hint: short (~10s), medium (~30s), long (~60s+).

    Returns:
        A structured plan with matched templates, helpers, examples,
        and pedagogical guidance.
    """
    plan: dict = {
        "topic": topic,
        "level": level,
        "duration_hint": duration_hint,
    }

    # 1. Match topic templates
    matched_topics = _find_best_matches(topic, _TOPIC_KEYWORDS, top_n=2)
    if matched_topics:
        plan["matched_templates"] = []
        for tid in matched_topics:
            t = TOPICS[tid]
            plan["matched_templates"].append({
                "id": tid,
                "title": t["title"],
                "concept_arc": t["concept_arc"],
                "scenes": t["scenes"],
            })
    else:
        plan["matched_templates"] = []
        plan["template_note"] = (
            "No exact template match. Use the concept_arc pattern from "
            "similar topics and adapt. The style guide and pedagogy "
            "resources describe how to structure a scene."
        )

    # 2. Match helper domains
    matched_domains = _find_best_matches(topic, _DOMAIN_KEYWORDS, top_n=2)
    if matched_domains:
        plan["math_helpers"] = {
            domain: HELPERS[domain]
            for domain in matched_domains
        }

    # 3. Match relevant examples (by technique)
    matched_examples = _find_best_matches(topic, _EXAMPLE_KEYWORDS, top_n=3)
    if matched_examples:
        plan["relevant_examples"] = {
            eid: {
                "description": EXAMPLES[eid]["description"],
                "code": EXAMPLES[eid]["code"],
            }
            for eid in matched_examples
        }

    # 4. Duration guidance
    duration_map = {
        "short": {
            "target_seconds": 10,
            "n_scenes": 1,
            "guidance": "Single scene, 2-3 play() calls. Show one key idea.",
        },
        "medium": {
            "target_seconds": 30,
            "n_scenes": "1-2",
            "guidance": "One or two scenes. Introduce, demonstrate, conclude.",
        },
        "long": {
            "target_seconds": 60,
            "n_scenes": "2-4",
            "guidance": "Multiple scenes building on each other. Follow the concept arc pattern.",
        },
    }
    plan["duration_guidance"] = duration_map.get(duration_hint, duration_map["medium"])

    # 5. Level-specific notes
    level_notes = {
        "basic": "Use simple shapes and concrete numbers. Avoid abstract notation. Animate slowly with generous wait() calls.",
        "intermediate": "Can use coordinate systems, functions, and basic notation. Show the visual first, then the formula.",
        "calculus": "Use graphs, tangent lines, areas. Show limiting processes with ValueTracker animations.",
        "advanced": "Use 3D surfaces, vector fields, parametric objects. Camera orbits help reveal 3D structure. Fix equations in frame.",
    }
    plan["level_notes"] = level_notes.get(level, level_notes["intermediate"])

    # 6. Always include pedagogy reminder
    plan["pedagogy_principles"] = [
        "Concrete before abstract — start with a specific example",
        "Geometry before algebra — show the shape, then the equation",
        "Animation shows process — don't just display, transform",
        "One concept per scene — split complex ideas",
        "Progressive revelation — build complexity one layer at a time",
    ]

    return plan
