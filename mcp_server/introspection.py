"""
Introspect manimlib to discover available Mobjects and Animations.
"""
from __future__ import annotations

import inspect
from typing import Any


# Mapping of category names to module paths
MOBJECT_CATEGORIES = {
    "geometry": "manimlib.mobject.geometry",
    "text": "manimlib.mobject.svg.tex_mobject",
    "svg": "manimlib.mobject.svg.svg_mobject",
    "three_d": "manimlib.mobject.three_dimensions",
    "coordinate_systems": "manimlib.mobject.coordinate_systems",
    "functions": "manimlib.mobject.functions",
    "number_line": "manimlib.mobject.number_line",
    "numbers": "manimlib.mobject.numbers",
    "matrix": "manimlib.mobject.matrix",
    "probability": "manimlib.mobject.probability",
    "boolean_ops": "manimlib.mobject.boolean_ops",
    "vector_field": "manimlib.mobject.vector_field",
    "value_tracker": "manimlib.mobject.value_tracker",
    "dot_cloud": "manimlib.mobject.types.dot_cloud",
    "image": "manimlib.mobject.types.image_mobject",
    "surface": "manimlib.mobject.types.surface",
}

ANIMATION_CATEGORIES = {
    "creation": "manimlib.animation.creation",
    "fading": "manimlib.animation.fading",
    "growing": "manimlib.animation.growing",
    "indication": "manimlib.animation.indication",
    "movement": "manimlib.animation.movement",
    "numbers": "manimlib.animation.numbers",
    "rotation": "manimlib.animation.rotation",
    "transform": "manimlib.animation.transform",
    "transform_matching_parts": "manimlib.animation.transform_matching_parts",
    "composition": "manimlib.animation.composition",
    "update": "manimlib.animation.update",
    "specialized": "manimlib.animation.specialized",
}


def _get_classes_from_module(module_path: str, base_class: type | None = None) -> list[dict]:
    """Import a module and extract public classes with their signatures."""
    import importlib

    try:
        mod = importlib.import_module(module_path)
    except ImportError:
        return []

    results = []
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        # Skip private classes and imports from other modules
        if name.startswith("_"):
            continue
        if not hasattr(obj, "__module__") or not obj.__module__.startswith(module_path.rsplit(".", 1)[0]):
            continue
        if base_class and not issubclass(obj, base_class):
            continue

        try:
            sig = str(inspect.signature(obj.__init__))
            # Remove 'self' parameter for cleaner display
            sig = sig.replace("(self, ", "(", 1).replace("(self)", "()")
        except (ValueError, TypeError):
            sig = "(...)"

        doc = inspect.getdoc(obj) or ""
        # Truncate long docstrings
        if len(doc) > 200:
            doc = doc[:200] + "..."

        results.append({
            "name": name,
            "module": module_path,
            "signature": sig,
            "doc": doc,
        })

    return results


def list_mobjects(category: str = "all") -> list[dict]:
    """
    List available Mobject classes.

    Args:
        category: Filter by category name, or "all" for everything.
    """
    from manimlib.mobject.mobject import Mobject

    if category != "all" and category in MOBJECT_CATEGORIES:
        return _get_classes_from_module(MOBJECT_CATEGORIES[category], Mobject)

    results = []
    for cat_module in MOBJECT_CATEGORIES.values():
        results.extend(_get_classes_from_module(cat_module, Mobject))
    return results


def list_animations(category: str = "all") -> list[dict]:
    """
    List available Animation classes.

    Args:
        category: Filter by category name, or "all" for everything.
    """
    from manimlib.animation.animation import Animation

    if category != "all" and category in ANIMATION_CATEGORIES:
        return _get_classes_from_module(ANIMATION_CATEGORIES[category], Animation)

    results = []
    for cat_module in ANIMATION_CATEGORIES.values():
        results.extend(_get_classes_from_module(cat_module, Animation))
    return results
