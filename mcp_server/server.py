"""
ManimGL MCP Server — exposes ManimGL functionality to LLMs via FastMCP.

Run with:  uv run --extra mcp manimgl-mcp
"""
from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP

from mcp_server.renderer import render_scene as _render_scene
from mcp_server.renderer import render_frame as _render_frame
from mcp_server.validation import validate_scene_code
from mcp_server.introspection import (
    list_mobjects as _list_mobjects,
    list_animations as _list_animations,
    MOBJECT_CATEGORIES,
    ANIMATION_CATEGORIES,
)
from mcp_server.examples import get_example as _get_example, EXAMPLES
from mcp_server.topics import (
    list_topics as _list_topics,
    get_topic_template as _get_topic_template,
    LEVELS as TOPIC_LEVELS,
    CATEGORIES as TOPIC_CATEGORIES,
)
from mcp_server.math_helpers import get_math_helpers as _get_math_helpers, HELPERS
from mcp_server.style_guide import STYLE_GUIDE, PEDAGOGY_GUIDE
from mcp_server.video_planner import create_video_plan as _create_video_plan

mcp = FastMCP("manimgl")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool
def render(
    code: str,
    scene_name: str | None = None,
    quality: str = "medium",
    format: str = "mp4",
) -> str:
    """Render a ManimGL scene from Python code.

    The code should define one or more Scene subclasses with a
    construct() method. You do NOT need to include
    'from manimlib import *' — it is added automatically.

    Args:
        code: Python source defining Scene subclass(es).
        scene_name: Class name to render. If omitted, renders the
                    first Scene found.
        quality: One of "low" (480p), "medium" (720p), "high"
                 (1080p), "4k".
        format: Output format — "mp4", "gif", or "png".
                "png" captures the final frame only.
    """
    result = _render_scene(code, scene_name, quality, format)
    return json.dumps(result, indent=2)


@mcp.tool
def preview(
    code: str,
    scene_name: str | None = None,
    quality: str = "low",
) -> str:
    """Render a single frame (final frame) of a scene for quick preview.

    Much faster than a full render. Returns a base64-encoded PNG image.

    Args:
        code: Python source defining Scene subclass(es).
        scene_name: Class name to render. Defaults to first found.
        quality: One of "low", "medium", "high", "4k".
    """
    result = _render_frame(code, scene_name, quality)
    return json.dumps(result, indent=2)


@mcp.tool
def validate(code: str) -> str:
    """Validate ManimGL scene code without rendering.

    Checks for syntax errors, undefined names, and import problems.
    Does NOT invoke the GPU or run animations.

    Args:
        code: Python source defining Scene subclass(es).
    """
    result = validate_scene_code(code)
    return json.dumps(result, indent=2)


@mcp.tool
def list_mobjects(category: str = "all") -> str:
    """List available ManimGL Mobject (mathematical object) classes.

    Returns class names, constructor signatures, and docstrings.

    Args:
        category: Filter by category. Options: "all", "geometry",
                  "text", "svg", "three_d", "coordinate_systems",
                  "functions", "number_line", "numbers", "matrix",
                  "probability", "boolean_ops", "vector_field",
                  "value_tracker", "dot_cloud", "image", "surface".
    """
    results = _list_mobjects(category)
    return json.dumps(results, indent=2)


@mcp.tool
def list_animations(category: str = "all") -> str:
    """List available ManimGL Animation classes.

    Returns class names, constructor signatures, and docstrings.

    Args:
        category: Filter by category. Options: "all", "creation",
                  "fading", "growing", "indication", "movement",
                  "numbers", "rotation", "transform",
                  "transform_matching_parts", "composition",
                  "update", "specialized".
    """
    results = _list_animations(category)
    return json.dumps(results, indent=2)


@mcp.tool
def get_example(topic: str) -> str:
    """Get a working example scene for a given topic.

    Returns complete, runnable code you can pass directly to
    the render or preview tools.

    Args:
        topic: Example topic. Options include "basic_shapes",
               "transform", "tex", "graph", "3d", "number_line",
               "complex_plane", "text_animation",
               "value_tracker_graph", "grid_transformation",
               "vector_field_2d", "color_gradient_surface",
               "progressive_equation", "parametric_curve",
               "side_by_side", "camera_orbit_3d",
               "staggered_animation", "updater_chain".
    """
    result = _get_example(topic)
    return json.dumps(result, indent=2)


@mcp.tool
def list_topics(
    category: str | None = None,
    level: str | None = None,
) -> str:
    """Browse available math video topic templates.

    Each topic is a structured video plan with concept arc,
    scene code, and pedagogical notes following 3Blue1Brown's
    visual-first teaching approach.

    Args:
        category: Filter by math category. Options: "geometry",
                  "linear_algebra", "complex_analysis", "calculus",
                  "differential_geometry". Omit for all.
        level: Filter by difficulty. Options: "basic",
               "intermediate", "calculus", "advanced". Omit for all.
    """
    results = _list_topics(category, level)
    return json.dumps(results, indent=2)


@mcp.tool
def get_topic_template(topic_id: str) -> str:
    """Get the full video template for a math topic.

    Returns the concept arc (pedagogical outline), complete
    renderable scene code, and visual design notes.

    The scene code can be passed directly to the render tool.

    Args:
        topic_id: Topic identifier from list_topics.
    """
    result = _get_topic_template(topic_id)
    return json.dumps(result, indent=2, default=str)


@mcp.tool
def get_math_helpers(domain: str) -> str:
    """Get reusable math helper functions for a domain.

    Returns Python code with documented helper functions you can
    incorporate into scene code. Covers common mathematical
    operations for visualization.

    Args:
        domain: One of "calculus", "linear_algebra",
                "complex_analysis", "vector_calculus",
                "differential_geometry", "probability".
    """
    result = _get_math_helpers(domain)
    return json.dumps(result, indent=2)


@mcp.tool
def create_math_video(
    topic: str,
    level: str = "intermediate",
    duration_hint: str = "medium",
) -> str:
    """Create a structured plan for a math explainer video.

    Takes a natural language description of a math concept and
    returns a complete video plan with:
    - Matched topic templates with renderable scene code
    - Relevant math helper functions
    - Technique examples to draw from
    - Pedagogical guidance (3Blue1Brown style)
    - Duration and pacing notes

    The scene code in matched templates can be passed directly
    to the render tool. For topics without an exact template
    match, use the returned examples and helpers as building
    blocks to write new scene code.

    Args:
        topic: Natural language description, e.g. "how the
               derivative relates to the slope of a tangent line"
               or "visualize Gaussian curvature on different surfaces".
        level: Target difficulty. One of "basic", "intermediate",
               "calculus", "advanced".
        duration_hint: Target length. One of "short" (~10s),
                       "medium" (~30s), "long" (~60s+).
    """
    result = _create_video_plan(topic, level, duration_hint)
    return json.dumps(result, indent=2, default=str)


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("manim://constants")
def get_constants() -> str:
    """Key ManimGL constants for positioning and colors.

    Includes direction vectors (UP, DOWN, LEFT, RIGHT, ORIGIN),
    frame dimensions, buffer sizes, and the full color palette.
    """
    constants = {
        "directions": {
            "ORIGIN": [0, 0, 0],
            "UP": [0, 1, 0],
            "DOWN": [0, -1, 0],
            "RIGHT": [1, 0, 0],
            "LEFT": [-1, 0, 0],
            "IN": [0, 0, -1],
            "OUT": [0, 0, 1],
            "UL": [-1, 1, 0],
            "UR": [1, 1, 0],
            "DL": [-1, -1, 0],
            "DR": [1, -1, 0],
        },
        "frame": {
            "FRAME_HEIGHT": 8.0,
            "FRAME_WIDTH": "8.0 * aspect_ratio (default ~14.22 at 1920x1080)",
        },
        "buffers": {
            "SMALL_BUFF": 0.1,
            "MED_SMALL_BUFF": 0.25,
            "MED_LARGE_BUFF": 0.5,
            "LARGE_BUFF": 1.0,
            "DEFAULT_MOBJECT_TO_EDGE_BUFF": 0.5,
        },
        "colors": {
            "primary": [
                "WHITE", "BLACK", "GREY_A", "GREY_B", "GREY_C",
                "GREY_D", "GREY_E",
            ],
            "spectrum": [
                "BLUE_A", "BLUE_B", "BLUE_C", "BLUE_D", "BLUE_E",
                "TEAL_A", "TEAL_B", "TEAL_C", "TEAL_D", "TEAL_E",
                "GREEN_A", "GREEN_B", "GREEN_C", "GREEN_D", "GREEN_E",
                "YELLOW_A", "YELLOW_B", "YELLOW_C", "YELLOW_D", "YELLOW_E",
                "GOLD_A", "GOLD_B", "GOLD_C", "GOLD_D", "GOLD_E",
                "RED_A", "RED_B", "RED_C", "RED_D", "RED_E",
                "MAROON_A", "MAROON_B", "MAROON_C", "MAROON_D", "MAROON_E",
                "PURPLE_A", "PURPLE_B", "PURPLE_C", "PURPLE_D", "PURPLE_E",
            ],
            "aliases": {
                "BLUE": "BLUE_C",
                "TEAL": "TEAL_C",
                "GREEN": "GREEN_C",
                "YELLOW": "YELLOW_C",
                "GOLD": "GOLD_C",
                "RED": "RED_C",
                "MAROON": "MAROON_C",
                "PURPLE": "PURPLE_C",
                "ORANGE": "#FF862F",
                "PINK": "#D147BD",
            },
        },
        "example_topics": list(EXAMPLES.keys()),
        "mobject_categories": list(MOBJECT_CATEGORIES.keys()),
        "animation_categories": list(ANIMATION_CATEGORIES.keys()),
    }
    return json.dumps(constants, indent=2)


@mcp.resource("manim://config")
def get_default_config() -> str:
    """Default ManimGL configuration.

    Shows camera resolution, FPS, background color, file writer
    settings, and other defaults that affect rendering.
    """
    config_path = Path(__file__).resolve().parent.parent / "manimlib" / "default_config.yml"
    if config_path.exists():
        return config_path.read_text()
    return "default_config.yml not found"


@mcp.resource("manim://style-guide")
def get_style_guide() -> str:
    """Visual style guide for creating ManimGL animations.

    Covers animation timing, color conventions, camera work,
    text/equation presentation, updaters, staggered animations,
    and common pitfalls. Distilled from 3Blue1Brown production code.
    """
    return STYLE_GUIDE


@mcp.resource("manim://pedagogy")
def get_pedagogy_guide() -> str:
    """Visual mathematics pedagogy principles.

    The 3Blue1Brown approach to teaching math through animation:
    concrete before abstract, geometry before algebra, animation
    shows process, one concept per scene, let the eye follow.

    Includes video structure patterns and color conventions
    for different math domains.
    """
    return PEDAGOGY_GUIDE


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
