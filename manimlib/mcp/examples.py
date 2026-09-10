"""Search ManimGL's example scenes for known-good usage patterns.

The corpus is small -- a few thousand lines across a handful of files --
so it is parsed lazily on first use and memoized in memory
(:func:`load_corpus`). A disk cache would only save single-digit
milliseconds per process start, against real added complexity (cache
invalidation, cross-process staleness, temp-directory permission
failures on Windows), so this deliberately does not add one.

Two corpora are combined:

1. A small, curated set of scenes **vendored** under
   ``manimlib/mcp/vendored_scenes/*.py`` (named distinctly from this
   module -- ``manimlib.mcp.examples`` -- since a same-named package
   directory would shadow it: Python resolves a package over a
   same-named module in the same parent, so ``examples/`` and
   ``examples.py`` side by side is a real, silent collision, not just a
   style nit). This subpackage ships inside the installed ``manimlib``
   package like any other, so it is present even when installed from a
   wheel -- where the repository's own ``docs/``, ``tests/``, and root
   ``example_scenes.py`` are not, since ``MANIFEST.in`` only grafts
   ``manimlib`` itself.
2. When running from a source checkout (detected via the presence of
   the repository's root ``example_scenes.py`` next to the installed
   ``manimlib`` package), the checkout's own ``example_scenes.py``,
   ``docs/example.py``, ``tests/scenes.py``, and the
   ``.. manim-example::`` blocks inside
   ``docs/source/getting_started/example_scenes.rst``.

Vendored entries take priority over same-named checkout entries, so a
curated, headless-safe version always wins.
"""
from __future__ import annotations

import ast
import functools
import re
from dataclasses import dataclass
from pathlib import Path

_VENDORED_DIR = Path(__file__).parent / "vendored_scenes"

_MANIM_EXAMPLE_RE = re.compile(r"^\.\. manim-example:: (?P<name>\S+)\s*$")

# Scenes that are correct ManimGL usage but require an interactive
# window (``self.embed()``/``self.interact()``) to do anything -- these
# are actively misleading as "known-good" examples in a headless,
# agent-driven context, so they are excluded from search results.
_INTERACTIVE_ONLY = {"InteractiveDevelopment", "ControlsExample", "SquareToCircleEmbed"}


@dataclass(frozen=True)
class Example:
    name: str
    source: str
    origin: str  # e.g. "vendored:basic_shapes.py" or "checkout:example_scenes.py"


def _get_manim_dir() -> Path | None:
    """Locate the repository root, if running from a source checkout.

    Mirrors ``manimlib.config.get_manim_dir``: the parent directory of
    the installed ``manimlib`` package. Returns ``None`` -- rather than
    raising -- if manimlib cannot be imported, since example search does
    not itself need manimlib's runtime dependencies (glfw, wgpu, ...) and
    should keep working without them; it just won't find checkout-only
    examples.
    """
    try:
        import manimlib
    except ImportError:
        return None
    return Path(manimlib.__file__).resolve().parent.parent


def _scenes_from_python_source(source: str, origin: str) -> list[Example]:
    """Extract top-level ``*Scene`` classes from a .py file via ``ast``.

    Never imports or executes the file -- this must work without
    manimlib installed, and must never execute untrusted or
    still-unverified example code.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    examples = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        base_names = {b.id for b in node.bases if isinstance(b, ast.Name)}
        base_names |= {b.attr for b in node.bases if isinstance(b, ast.Attribute)}
        if not any("Scene" in base for base in base_names):
            continue
        segment = ast.get_source_segment(source, node)
        if segment is None:
            continue
        examples.append(Example(name=node.name, source=segment, origin=origin))
    return examples


def _scenes_from_rst(text: str, origin: str) -> list[Example]:
    """Extract ``.. manim-example:: Name`` code blocks from an rst file.

    The directive (``docs/source/manim_example_ext.py``) only ever
    re-renders the wrapped code as a literal block -- it never executes
    it -- so these snippets have no independent guarantee they still
    run; this module's test suite asserts each extracted snippet at
    least still compiles.
    """
    lines = text.splitlines()
    examples = []
    i = 0
    while i < len(lines):
        match = _MANIM_EXAMPLE_RE.match(lines[i])
        if not match:
            i += 1
            continue
        name = match.group("name")
        i += 1
        while i < len(lines) and lines[i].strip().startswith(":"):
            i += 1  # skip :option: lines
        while i < len(lines) and not lines[i].strip():
            i += 1  # skip the blank line before the code block
        block_lines = []
        while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
            block_lines.append(lines[i][4:] if lines[i].startswith("    ") else "")
            i += 1
        source = "\n".join(block_lines).rstrip("\n") + "\n"
        examples.append(Example(name=name, source=source, origin=origin))
    return examples


def _load_vendored() -> list[Example]:
    if not _VENDORED_DIR.is_dir():
        return []
    examples = []
    for path in sorted(_VENDORED_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        source = path.read_text(encoding="utf-8")
        examples.extend(_scenes_from_python_source(source, origin=f"vendored:{path.name}"))
    return examples


def _load_checkout() -> list[Example]:
    root = _get_manim_dir()
    if root is None or not (root / "example_scenes.py").is_file():
        return []

    examples: list[Example] = []
    for relative in ("example_scenes.py", "docs/example.py", "tests/scenes.py"):
        path = root / relative
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        examples.extend(_scenes_from_python_source(source, origin=f"checkout:{relative}"))

    rst_path = root / "docs" / "source" / "getting_started" / "example_scenes.rst"
    if rst_path.is_file():
        text = rst_path.read_text(encoding="utf-8")
        examples.extend(_scenes_from_rst(text, origin=f"checkout:{rst_path.name}"))

    return examples


@functools.lru_cache(maxsize=1)
def load_corpus() -> tuple[Example, ...]:
    """Load and memoize the full example corpus (vendored, then checkout if present).

    Lazy (nothing is parsed until the first call) and memoized for the
    life of the process. On a name collision the earlier source wins, so
    a curated vendored scene always takes priority over a same-named
    scene found in a checkout.
    """
    seen: dict[str, Example] = {}
    for example in (*_load_vendored(), *_load_checkout()):
        if example.name in _INTERACTIVE_ONLY:
            continue
        seen.setdefault(example.name, example)
    return tuple(seen.values())


def search_examples(query: str = "", limit: int = 10) -> list[dict[str, str]]:
    """Search the example corpus by scene name and source substring.

    An empty query returns the whole corpus (up to ``limit``), with
    exact-ish name matches sorted first.
    """
    query_lower = query.lower()
    scored = []
    for example in load_corpus():
        haystack = f"{example.name}\n{example.source}".lower()
        if query_lower and query_lower not in haystack:
            continue
        rank = 0 if query_lower and query_lower in example.name.lower() else 1
        scored.append((rank, example.name, example))

    scored.sort(key=lambda item: (item[0], item[1]))
    return [
        {"name": ex.name, "source": ex.source, "origin": ex.origin}
        for _, _, ex in scored[:limit]
    ]
