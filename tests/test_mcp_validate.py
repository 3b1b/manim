"""Tests for manimlib.mcp.validate -- pure ast/symtable analysis, no manimlib needed.

known_names is always passed explicitly (never imported live) so these
run without manimgl installed, per the module's own design.
"""
from __future__ import annotations

from manimlib.mcp.validate import validate_scene

KNOWN_NAMES = {
    "Scene", "ThreeDScene", "Square", "Circle", "ShowCreation",
    "ReplacementTransform", "Tex", "TexText", "VGroup", "Mobject",
    "self", "np", "math", "range", "print", "open", "Exception",
    "RIGHT", "LEFT", "UP", "DOWN", "BLUE", "TAU", "PI", "Rotate",
}


def test_valid_code_has_no_unknown_names():
    code = """
from manimlib import *

class Demo(Scene):
    def construct(self):
        square = Square()
        self.play(ShowCreation(square))
        for i in range(3):
            square.shift(RIGHT)
        items = [x for x in range(5)]
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert result["syntax_ok"] is True
    assert result["scenes_found"] == ["Demo"]
    assert result["unknown_names"] == []


def test_manim_community_create_is_flagged_with_hint():
    code = """
from manimlib import *

class Demo(Scene):
    def construct(self):
        self.play(Create(Square()))
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    names = {entry["name"] for entry in result["unknown_names"]}
    assert "Create" in names
    hint = next(e["hint"] for e in result["unknown_names"] if e["name"] == "Create")
    assert "ShowCreation" in hint


def test_manim_community_mathtex_is_flagged_with_hint():
    code = """
from manimlib import *

class Demo(Scene):
    def construct(self):
        self.add(MathTex("x^2"))
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    names = {entry["name"] for entry in result["unknown_names"]}
    assert "MathTex" in names


def test_three_d_scene_and_animate_are_not_flagged():
    """ThreeDScene and Mobject.animate exist in ManimGL -- must not be treated as CE-only."""
    code = """
from manimlib import *

class Demo(ThreeDScene):
    def construct(self):
        square = Square()
        self.play(square.animate.shift(RIGHT))
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert result["unknown_names"] == []


def test_numpy_and_math_leaked_names_are_not_flagged():
    """manimlib/__init__.py has no __all__, so `np` and `math` are genuinely bound."""
    code = """
from manimlib import *

class Demo(Scene):
    def construct(self):
        square = Square()
        square.apply_function(lambda p: [p[0] + math.sin(p[1]), p[1], p[2]])
        self.play(square.animate.apply_complex_function(np.exp))
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert result["unknown_names"] == []


def test_loop_and_comprehension_variables_are_not_flagged():
    """A plain ast.Name walk would misreport these; symtable must not."""
    code = """
from manimlib import *

class Demo(Scene):
    def construct(self):
        for i in range(3):
            pass
        items = [x for x in range(5)]
        with open("f") as fh:
            pass
        try:
            pass
        except Exception as e:
            pass
        if (n := 5) > 0:
            pass
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert result["unknown_names"] == []


def test_closures_over_enclosing_locals_are_not_flagged():
    code = """
from manimlib import *

class Demo(Scene):
    def construct(self):
        width = 5

        def inner():
            return width + 1

        self.play(inner())
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert result["unknown_names"] == []


def test_module_level_helper_functions_are_not_flagged():
    code = """
from manimlib import *


def helper(x):
    return x + 1


class Demo(Scene):
    def construct(self):
        self.play(Square().animate.shift(helper(1) * RIGHT))
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert result["unknown_names"] == []


def test_syntax_error_is_reported_without_raising():
    result = validate_scene("def f(:", known_names=KNOWN_NAMES)
    assert result["syntax_ok"] is False
    assert result["error"]
    assert result["scenes_found"] == []


def test_no_scene_found_warns():
    result = validate_scene("x = 1\n", known_names=KNOWN_NAMES)
    assert result["syntax_ok"] is True
    assert any("No Scene subclass" in w for w in result["warnings"])


def test_none_known_names_skips_resolution_and_warns():
    code = "from manimlib import *\nclass Demo(Scene):\n    def construct(self):\n        self.play(Create(Square()))\n"
    result = validate_scene(code, known_names=None)
    assert result["syntax_ok"] is True
    assert result["unknown_names"] == []
    assert any("manimlib is unavailable" in w for w in result["warnings"])


def test_embed_and_interact_are_flagged_as_headless_hazards():
    code = """
from manimlib import *

class Demo(Scene):
    def construct(self):
        self.add(Square())
        self.embed()
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert any("embed" in w for w in result["warnings"])


def test_while_true_is_flagged():
    code = """
from manimlib import *

class Demo(Scene):
    def construct(self):
        while True:
            pass
"""
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert any("while True" in w for w in result["warnings"])


def test_manim_community_import_is_flagged():
    code = "from manim import *\n\nclass Demo(Scene):\n    def construct(self):\n        pass\n"
    result = validate_scene(code, known_names=KNOWN_NAMES)
    assert any("ManimGL" in w for w in result["warnings"])
