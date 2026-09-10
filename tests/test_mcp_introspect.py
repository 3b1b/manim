"""Tests for manimlib.mcp.introspect -- requires manimlib importable, no GPU."""
from __future__ import annotations

import pytest

pytest.importorskip("manimlib")

from manimlib.mcp.introspect import (  # noqa: E402
    describe_class,
    get_constants,
    list_classes,
    list_methods,
    public_names,
)


def test_public_names_includes_leaked_module_level_imports():
    """manimlib/__init__.py has no __all__, so `np` and `math` are genuinely
    bound by `from manimlib import *` -- a validator must not flag them."""
    names = public_names()
    assert "np" in names
    assert "math" in names
    assert "Scene" in names
    assert "Circle" in names


def test_manim_classes_excludes_private_and_dead_module_names():
    classes = {c["name"] for c in list_classes(kind="all")}
    assert "np" not in classes
    assert "math" not in classes
    assert "_MethodAnimation" not in classes
    # old_tex_mobject.py is never star-imported by manimlib/__init__.py.
    assert "OldTex" not in classes


def test_list_classes_kind_filters_are_disjoint_and_populated():
    mobjects = list_classes(kind="mobject")
    animations = list_classes(kind="animation")
    scenes = list_classes(kind="scene")
    # Counts as ranges, not exact values, so adding a class upstream
    # doesn't red this build.
    assert len(mobjects) >= 100
    assert len(animations) >= 50
    assert len(scenes) >= 1

    mobject_names = {c["name"] for c in mobjects}
    animation_names = {c["name"] for c in animations}
    assert mobject_names.isdisjoint(animation_names)
    assert "Circle" in mobject_names
    assert "ShowCreation" in animation_names
    assert "Scene" in {c["name"] for c in scenes}


def test_list_classes_query_filters_by_substring():
    results = list_classes(kind="all", query="fade")
    assert results
    assert all("fade" in c["name"].lower() for c in results)


def test_describe_class_circle_has_a_signature():
    result = describe_class("Circle")
    assert result["name"] == "Circle"
    assert result["module"] == "manimlib.mobject.geometry"
    assert "Arc" in result["mro"]
    param_names = {p["name"] for p in result["parameters"]}
    assert "radius" in param_names or "arc_center" in param_names


def test_describe_class_unknown_name_suggests_alternatives():
    result = describe_class("Circlee")
    assert "error" in result
    assert "Circle" in result["did_you_mean"]


def test_describe_class_annotations_are_strings_not_evaluated():
    """Most manimlib modules use `from __future__ import annotations`, and
    manimlib/typing.py's aliases only exist under TYPE_CHECKING -- evaluating
    an annotation at runtime would raise NameError, so this must never happen."""
    result = describe_class("VMobject")
    for param in result["parameters"]:
        if param["annotation"] is not None:
            assert isinstance(param["annotation"], str)


def test_describe_class_never_raises_for_any_discovered_class():
    """The single highest-value regression test for this module: loop over
    every real ManimGL class and confirm signature extraction is robust."""
    for entry in list_classes(kind="all"):
        result = describe_class(entry["name"])
        assert "error" not in result, f"describe_class raised/errored on {entry['name']}"
        assert isinstance(result["parameters"], list)


def test_list_methods_scene_includes_known_verbs():
    result = list_methods("Scene")
    names = {m["name"] for m in result["methods"]}
    assert "play" in names
    assert "add" in names
    assert "wait" in names


def test_get_constants_colors_returns_hex_strings():
    result = get_constants(category="colors")
    colors = result["colors"]
    assert "BLUE_C" in colors
    assert colors["BLUE_C"].startswith("#")
    # Matches default_config.yml's colors section (57 named colors).
    assert len(colors) >= 50


def test_get_constants_reflects_actual_configured_values():
    """BLUE_E's value comes from manim_config.colors.blue_e at import time --
    this must be the live configured value, not a hardcoded copy."""
    import manimlib

    result = get_constants(category="colors")
    assert result["colors"]["BLUE_E"] == manimlib.manim_config.colors.blue_e


def test_get_constants_vectors_are_lists_not_ndarrays():
    result = get_constants(category="vectors")
    assert list(result["vectors"]["UP"]) == [0.0, 1.0, 0.0]


def test_get_constants_all_covers_every_category():
    result = get_constants(category="all")
    assert set(result.keys()) >= {"colors", "vectors", "sizes"}
