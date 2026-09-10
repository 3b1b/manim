"""Reflection over the installed ManimGL version.

There are two distinct surfaces here and they must not be conflated:

- :func:`public_names` -- the *availability* oracle used by
  :mod:`manimlib.mcp.validate`. Since ``manimlib/__init__.py`` re-exports
  via roughly eighty unqualified ``from ... import *`` statements and
  defines no ``__all__``, ``from manimlib import *`` in a scene file
  binds more than manimlib's own classes and functions -- it also binds
  names like ``np`` and ``math`` that individual modules import without
  scoping. Those names are genuinely available in a scene file, so this
  set must include them.
- :func:`list_classes` / :func:`describe_class` -- the *discovery*
  surface, restricted to actual classes defined somewhere under
  ``manimlib``.
"""
from __future__ import annotations

import builtins
import difflib
import inspect
import io
import tokenize
from typing import Any

from manimlib.mcp._bootstrap import import_manimlib

_KIND_PREFIXES: dict[str, str] = {
    "animation": "manimlib.animation",
    "mobject": "manimlib.mobject",
    "scene": "manimlib.scene",
}


def _kind_of(cls: type) -> str:
    module = cls.__module__
    for kind, prefix in _KIND_PREFIXES.items():
        if module.startswith(prefix):
            return kind
    return "other"


def _suggest_names(name: str, candidates: list[str], limit: int = 10) -> list[str]:
    """"Did you mean" suggestions for a class/method name that wasn't found.

    Combines ``difflib``'s fuzzy ratio matching (catches typos like an
    extra or missing letter -- e.g. ``"Circlee"`` -> ``"Circle"``, which
    a plain substring check misses since "circlee" is not a substring of
    "circle") with a substring check (catches a truncated or partial
    name a pure ratio match can undervalue).
    """
    close = list(difflib.get_close_matches(name, candidates, n=limit, cutoff=0.6))
    name_lower = name.lower()
    for candidate in sorted(candidates):
        if len(close) >= limit:
            break
        if candidate not in close and name_lower in candidate.lower():
            close.append(candidate)
    return close[:limit]


def public_names() -> set[str]:
    """Every name available, unqualified, inside a ManimGL scene file.

    This is ``{n for n in vars(manimlib) if not n.startswith("_")}``
    (what ``from manimlib import *`` actually binds, since there is no
    ``__all__``) unioned with Python's builtins. It deliberately
    includes leaked names such as ``np`` and ``math`` -- they are
    genuinely bound in a real scene file, so a validator that flagged
    them as "unknown" would be wrong about working code.
    """
    manimlib = import_manimlib()
    names = {name for name in vars(manimlib) if not name.startswith("_")}
    names |= {name for name in vars(builtins) if not name.startswith("_")}
    return names


def _manim_classes() -> dict[str, type]:
    """Classes genuinely defined under ``manimlib``, keyed by their public name.

    Sourced from ``vars(manimlib)`` rather than walking submodules
    directly: because ``manimlib/__init__.py``'s star-imports skip names
    that individual modules didn't intend to export (no ``__all__``
    means Python's ``import *`` already excludes leading-underscore
    names), private helper classes like ``_MethodAnimation`` and modules
    that are never star-imported (e.g.
    ``manimlib.mobject.svg.old_tex_mobject``) are already absent here --
    no separate exclusion list is needed.
    """
    manimlib = import_manimlib()
    classes: dict[str, type] = {}
    for name, obj in vars(manimlib).items():
        if name.startswith("_"):
            continue
        if not isinstance(obj, type):
            continue
        if not obj.__module__.startswith("manimlib"):
            continue
        classes[name] = obj
    return classes


def list_classes(kind: str = "all", query: str = "") -> list[dict[str, Any]]:
    """List ManimGL classes, optionally filtered by kind and a name substring.

    Args:
        kind: One of ``"all"``, ``"mobject"``, ``"animation"``, ``"scene"``.
        query: Case-insensitive substring matched against class names.
    """
    query_lower = query.lower()
    results: list[dict[str, Any]] = []
    for name, cls in sorted(_manim_classes().items()):
        cls_kind = _kind_of(cls)
        if kind != "all" and cls_kind != kind:
            continue
        if query_lower and query_lower not in name.lower():
            continue
        results.append(
            {
                "name": name,
                "kind": cls_kind,
                "module": cls.__module__,
                "bases": [b.__name__ for b in cls.__bases__ if b is not object],
            }
        )
    return results


def _flatten_init_params(cls: type) -> list[inspect.Parameter]:
    """Collect ``__init__`` parameters across the MRO.

    Most ManimGL constructors forward unrecognized keyword arguments to
    their superclass's ``__init__`` via ``**kwargs`` -- many ``Mobject``
    subclasses take almost all of their real configuration this way, so
    the class's own local signature alone is close to useless. This
    walks the MRO, collecting parameters from each ``__init__`` in turn,
    and keeps going past a class only while that class's own
    ``__init__`` still declares ``**kwargs`` -- once a level's
    constructor stops forwarding, parameters further up the MRO are no
    longer reachable through this particular constructor, so collection
    stops there.
    """
    seen: dict[str, inspect.Parameter] = {}
    for klass in cls.__mro__:
        if klass is object:
            continue
        init = klass.__dict__.get("__init__")
        if init is None:
            continue
        try:
            signature = inspect.signature(init, eval_str=False)
        except (TypeError, ValueError):
            continue

        has_var_keyword = False
        for pname, param in signature.parameters.items():
            if pname == "self":
                continue
            if param.kind is inspect.Parameter.VAR_KEYWORD:
                has_var_keyword = True
                continue
            if param.kind is inspect.Parameter.VAR_POSITIONAL:
                continue
            seen.setdefault(pname, param)

        if not has_var_keyword:
            break
    return list(seen.values())


def _harvest_param_comments(init: Any) -> dict[str, str]:
    """Best-effort extraction of inline ``#`` comments documenting parameters.

    ManimGL's docstrings are sparse (roughly a fifth of classes have
    one), but many ``__init__`` signatures carry per-parameter
    explanations as comments next to each keyword argument::

        def __init__(
            self,
            stroke_width: float = 4.0,  # Width of the stroke, in pixels
            ...
        ):

    This is where most of ManimGL's real parameter documentation
    actually lives. Extraction is heuristic -- it associates each
    comment with the nearest parameter name token at the signature's
    top parenthesis depth -- and deliberately best-effort: any failure
    here is swallowed, since this is a documentation aid, not load-
    bearing behavior.
    """
    try:
        source = inspect.getsource(init)
    except (OSError, TypeError):
        return {}

    comments: dict[str, str] = {}
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return {}

    paren_depth = 0
    current_param: str | None = None
    pending_comment: str | None = None

    for tok in tokens:
        if tok.type == tokenize.OP and tok.string in "([{":
            paren_depth += 1
        elif tok.type == tokenize.OP and tok.string in ")]}":
            paren_depth -= 1
        elif tok.type == tokenize.NAME and paren_depth == 1:
            current_param = tok.string
        elif tok.type == tokenize.COMMENT:
            text = tok.string.lstrip("#").strip()
            if current_param is not None and current_param not in comments:
                comments[current_param] = text
            elif pending_comment is None:
                pending_comment = text
        elif tok.type in (tokenize.NEWLINE, tokenize.NL):
            if (
                pending_comment is not None
                and current_param is not None
                and current_param not in comments
            ):
                comments[current_param] = pending_comment
            pending_comment = None

    return comments


def describe_class(name: str) -> dict[str, Any]:
    """Describe a ManimGL class: MRO-flattened signature, docstring, inline param docs.

    Annotations are returned as their raw source strings, never
    evaluated. Most of manimlib uses
    ``from __future__ import annotations``, and the type aliases in
    ``manimlib/typing.py`` (``ManimColor``, ``Vect3``, ``Selector``, ...)
    only exist inside ``if TYPE_CHECKING:`` blocks, so evaluating an
    annotation at runtime (``eval_str=True`` / ``typing.get_type_hints``)
    raises ``NameError``.
    """
    classes = _manim_classes()
    if name not in classes:
        return {
            "error": f"No ManimGL class named {name!r}.",
            "did_you_mean": _suggest_names(name, list(classes)),
        }

    cls = classes[name]
    params = _flatten_init_params(cls)
    own_init = cls.__dict__.get("__init__", cls.__init__)
    comments = _harvest_param_comments(own_init)

    return {
        "name": cls.__name__,
        "module": cls.__module__,
        "kind": _kind_of(cls),
        "mro": [base.__name__ for base in cls.__mro__ if base is not object],
        "docstring": inspect.getdoc(cls),
        "parameters": [
            {
                "name": p.name,
                "kind": p.kind.name,
                "annotation": (
                    None if p.annotation is inspect.Parameter.empty else str(p.annotation)
                ),
                "default": (
                    None if p.default is inspect.Parameter.empty else repr(p.default)
                ),
                "comment": comments.get(p.name),
            }
            for p in params
        ],
    }


def get_constants(category: str = "all") -> dict[str, dict[str, Any]]:
    """Reflect ``manimlib.constants``, grouped by inferred category.

    Values are read from the live module rather than hardcoded, so this
    returns the user's *actual configured* values -- every constant in
    ``manimlib/constants.py`` is an annotated assignment pulled from
    ``manim_config`` at import time (e.g. ``BLUE_E: ManimColor =
    manim_config.colors.blue_e``), so a user's ``custom_config.yml``
    changes what this reports, which a static list never could.

    Args:
        category: One of ``"all"``, ``"colors"``, ``"vectors"``,
            ``"angles"``, ``"sizes"``. Categorization is inferred from
            each value's type and name (hex-string colors, numpy-array
            vectors, named angle constants, other numeric sizes/buffs)
            rather than hardcoded against the file's current contents,
            so it doesn't need updating if constants are added.
    """
    manimlib = import_manimlib()
    from manimlib import constants as manim_constants

    import numpy as np

    angle_names = {"PI", "TAU", "DEGREES", "DEG"}

    def infer_category(name: str, value: Any) -> str:
        if isinstance(value, str) and value.startswith("#"):
            return "colors"
        if isinstance(value, np.ndarray):
            return "vectors"
        if name in angle_names:
            return "angles"
        if isinstance(value, (int, float)):
            return "sizes"
        return "other"

    grouped: dict[str, dict[str, Any]] = {}
    for name, value in vars(manim_constants).items():
        if name.startswith("_") or not name.isupper():
            continue
        cat = infer_category(name, value)
        if category != "all" and cat != category:
            continue
        serialized = value.tolist() if isinstance(value, np.ndarray) else value
        grouped.setdefault(cat, {})[name] = serialized
    return grouped


def list_methods(name: str) -> dict[str, Any]:
    """List public callables on a class -- the verbs on e.g. ``Scene``/``Mobject``."""
    classes = _manim_classes()
    if name not in classes:
        return {
            "error": f"No ManimGL class named {name!r}.",
            "did_you_mean": _suggest_names(name, list(classes)),
        }

    cls = classes[name]
    methods: list[dict[str, Any]] = []
    for attr_name in sorted(dir(cls)):
        if attr_name.startswith("_"):
            continue
        attr = getattr(cls, attr_name, None)
        if not callable(attr):
            continue
        try:
            signature: inspect.Signature | None = inspect.signature(attr, eval_str=False)
        except (TypeError, ValueError):
            signature = None
        methods.append(
            {
                "name": attr_name,
                "signature": str(signature) if signature is not None else None,
                "docstring": inspect.getdoc(attr),
            }
        )
    return {"name": cls.__name__, "methods": methods}
