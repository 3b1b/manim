"""Fast, static validation of submitted ManimGL scene code.

Pure ``ast``/``symtable`` analysis -- no GPU, no manimlib runtime
dependencies, and critically, submitted code is never executed or even
imported. This is what makes ``validate_scene`` cheap enough to run on
every draft before anyone reaches for :mod:`manimlib.mcp.render`.

The single highest-value check this performs is catching
ManimCommunity-flavored code: since almost all Manim training data is
ManimCommunity rather than ManimGL, an LLM asked for "manim code" will
confidently reach for names like ``Create`` or ``MathTex`` that simply
do not exist here.
"""
from __future__ import annotations

import ast
import symtable
from dataclasses import dataclass, field

# ManimCommunity names commonly confused for ManimGL equivalents. Kept
# small and specific (rather than an exhaustive CE/GL diff) since a
# stale or over-broad map produces false suggestions; the name-resolution
# pass below (using the real, live `known_names`) already catches
# anything not on this list, just without a suggested replacement.
#
# Deliberately absent: `ThreeDScene` and `Mobject.animate`, both of
# which exist in ManimGL too and would be wrong entries here.
_CE_TO_GL_HINTS: dict[str, str] = {
    "Create": "ShowCreation",
    "Uncreate": "Uncreate exists in both; check the import source",
    "MathTex": "Tex",
    "MovingCameraScene": "use self.frame (Scene.frame) directly",
    "Circumscribe": "no direct equivalent; try FlashAround",
    "Wiggle": "no direct equivalent; try WiggleOutThenIn",
    "config": "manim_config (from manimlib.config import manim_config)",
}

# Constructs that are valid ManimGL but hang or no-op when driven
# headlessly by an agent, as opposed to being outright wrong.
_HEADLESS_HAZARDS: dict[str, str] = {
    "embed": "Scene.embed() opens an interactive IPython shell; it is a no-op "
    "without a window and will not advance the scene headlessly.",
    "interact": "Scene.interact() blocks waiting for window events; it is a "
    "no-op without a window.",
}


@dataclass
class ValidationResult:
    syntax_ok: bool
    scenes_found: list[str] = field(default_factory=list)
    unknown_names: list[dict[str, object]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "syntax_ok": self.syntax_ok,
            "scenes_found": self.scenes_found,
            "unknown_names": self.unknown_names,
            "warnings": self.warnings,
            "error": self.error,
        }


def _scene_class_names(tree: ast.Module) -> list[str]:
    names = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = {b.id for b in node.bases if isinstance(b, ast.Name)}
            bases |= {b.attr for b in node.bases if isinstance(b, ast.Attribute)}
            if any("Scene" in base for base in bases):
                names.append(node.name)
    return names


def _is_unresolved_global_reference(sym: symtable.Symbol) -> bool:
    """True if ``sym`` is looked up via global/builtin scope at runtime, not bound anywhere visible.

    Verified empirically against CPython 3.13's ``symtable``: a name is
    only ``is_global()`` when Python would actually emit a global (as
    opposed to local or closure-cell) lookup for it, so this correctly
    treats loop variables, comprehension targets, ``with ... as``,
    ``except ... as``, the walrus operator, and closures over an
    enclosing function's locals as *not* global -- exactly the cases a
    plain ``ast.Name`` walk gets wrong. ``is_assigned()``/``is_imported()``
    exclude names the code itself defines or imports (e.g. a module-level
    helper function, or ``import numpy as np``), and ``is_parameter()``
    excludes function parameters.
    """
    return (
        sym.is_global()
        and sym.is_referenced()
        and not sym.is_assigned()
        and not sym.is_imported()
        and not sym.is_parameter()
    )


def _global_references(table: symtable.SymbolTable) -> list[symtable.Symbol]:
    """Recursively collect every unresolved global/builtin reference in ``table`` and its children."""
    symbols = [sym for sym in table.get_symbols() if _is_unresolved_global_reference(sym)]
    for child in table.get_children():
        symbols.extend(_global_references(child))
    return symbols


def _module_level_bound_names(table: symtable.SymbolTable) -> set[str]:
    """Names the submitted code itself defines at module level.

    A name referenced deep inside e.g. ``construct()`` that resolves to
    a module-level helper function or constant the *scene itself*
    defines is a real, working reference -- ``_is_unresolved_global_reference``
    correctly reports it as a global lookup (which it is, at runtime),
    but it must not be flagged as "unknown" just because it isn't part
    of manimlib's own namespace.
    """
    return {
        sym.get_name()
        for sym in table.get_symbols()
        if sym.is_assigned() or sym.is_imported() or sym.is_namespace()
    }


def _find_unknown_names(code: str, known_names: set[str]) -> list[dict[str, object]]:
    try:
        table = symtable.symtable(code, "<scene>", "exec")
    except SyntaxError:
        return []

    all_known = known_names | _module_level_bound_names(table)

    unknown: dict[str, dict[str, object]] = {}
    for sym in _global_references(table):
        name = sym.get_name()
        if name in all_known or name.startswith("_") or name in unknown:
            continue
        entry: dict[str, object] = {"name": name}
        if name in _CE_TO_GL_HINTS:
            entry["hint"] = f"Not in ManimGL. Did you mean: {_CE_TO_GL_HINTS[name]}?"
        unknown[name] = entry
    return sorted(unknown.values(), key=lambda e: str(e["name"]))


def _headless_warnings(code: str) -> list[str]:
    warnings = []
    for call, message in _HEADLESS_HAZARDS.items():
        if f".{call}(" in code or f"self.{call}()" in code:
            warnings.append(message)
    if "while True" in code:
        warnings.append(
            "`while True` inside construct() will hang a headless render "
            "until the render tool's timeout kills the process."
        )
    if "input(" in code:
        warnings.append(
            "input() will block forever in a headless render (stdin is "
            "closed for sandboxed renders)."
        )
    if "import manim " in code or "from manim import" in code or "from manim " in code:
        warnings.append(
            "This looks like it imports the `manim` package (ManimCommunity). "
            "This repository is ManimGL: `from manimlib import *`."
        )
    return warnings


def validate_scene(code: str, known_names: set[str] | None = None) -> dict[str, object]:
    """Statically validate submitted ManimGL scene code.

    Args:
        code: The Python source to validate.
        known_names: The set of names available unqualified in a scene
            file (see :func:`manimlib.mcp.introspect.public_names`).
            Passed as a parameter, never imported live, so this function
            -- and its tests -- work without manimlib installed. If
            ``None``, name resolution is skipped and only syntax,
            scene discovery, and the headless-hazard/CE-import checks
            run (reported with ``"unknown_names": []`` and a note in
            ``warnings``).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return ValidationResult(syntax_ok=False, error=str(exc)).to_dict()

    result = ValidationResult(syntax_ok=True)
    result.scenes_found = _scene_class_names(tree)
    result.warnings = _headless_warnings(code)

    if known_names is None:
        result.warnings.append(
            "manimlib is unavailable; name resolution was skipped. Only "
            "syntax and pattern-based checks ran (confidence: static)."
        )
    else:
        result.unknown_names = _find_unknown_names(code, known_names)

    if not result.scenes_found:
        result.warnings.append("No Scene subclass found in this code.")

    return result.to_dict()
