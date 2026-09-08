"""Tests for manimlib.mcp.examples -- pure ast/text parsing, no manimlib needed."""
from __future__ import annotations

import ast

from manimlib.mcp.examples import (
    _load_vendored,
    _scenes_from_python_source,
    _scenes_from_rst,
    load_corpus,
    search_examples,
)


def test_every_vendored_scene_compiles():
    """The vendored corpus is meant to be run; it must at least be syntactically valid."""
    examples = _load_vendored()
    assert examples, "expected at least one vendored example"
    for example in examples:
        compile(example.source, f"<vendored:{example.name}>", "exec")


def test_vendored_scenes_all_define_a_scene_subclass():
    for example in _load_vendored():
        assert "Scene" in example.source


def test_scenes_from_python_source_extracts_scene_classes_only():
    source = """
def helper():
    pass


class Demo(Scene):
    def construct(self):
        pass


class NotAScene:
    pass
"""
    examples = _scenes_from_python_source(source, origin="test")
    names = {e.name for e in examples}
    assert names == {"Demo"}


def test_scenes_from_python_source_handles_syntax_error_gracefully():
    assert _scenes_from_python_source("def f(:", origin="test") == []


def test_scenes_from_python_source_extracted_segment_is_valid_python():
    source = """
class Demo(Scene):
    def construct(self):
        self.add(Circle())
"""
    examples = _scenes_from_python_source(source, origin="test")
    assert len(examples) == 1
    compile(examples[0].source, "<test>", "exec")


def test_scenes_from_rst_parses_manim_example_directive():
    text = """Example Scenes
==============

.. manim-example:: InteractiveDevelopment
    :media: https://example.com/video.mp4

    from manimlib import *

    class InteractiveDevelopment(Scene):
        def construct(self):
            circle = Circle()
            self.play(ShowCreation(circle))

This scene is similar to what we wrote earlier.

AnimatingMethods
----------------

.. manim-example:: AnimatingMethods
    :media: https://example.com/other.mp4

    from manimlib import *

    class AnimatingMethods(Scene):
        def construct(self):
            self.add(Square())
"""
    examples = _scenes_from_rst(text, origin="test.rst")
    assert [e.name for e in examples] == ["InteractiveDevelopment", "AnimatingMethods"]
    # The extracted block should compile as Python, since it starts with
    # `from manimlib import *` followed by the class -- exactly the shape
    # the real docs/source/getting_started/example_scenes.rst uses.
    for example in examples:
        compile(example.source, f"<rst:{example.name}>", "exec")
    assert "circle = Circle()" in examples[0].source
    assert "self.add(Square())" in examples[1].source


def test_scenes_from_rst_handles_blank_lines_inside_the_code_block():
    text = """.. manim-example:: Demo
    :media: x.mp4

    from manimlib import *

    class Demo(Scene):
        def construct(self):
            self.add(Circle())

            self.wait()

Not part of the code block.
"""
    examples = _scenes_from_rst(text, origin="test.rst")
    assert len(examples) == 1
    assert "Not part of the code block" not in examples[0].source
    compile(examples[0].source, "<test>", "exec")


def test_real_repository_example_scenes_rst_yields_nine_examples():
    """Cross-check against the actual repository file, when running from a checkout."""
    import pytest

    from pathlib import Path

    manimlib = pytest.importorskip("manimlib")

    root = Path(manimlib.__file__).resolve().parent.parent
    rst_path = root / "docs" / "source" / "getting_started" / "example_scenes.rst"
    if not rst_path.is_file():
        pytest.skip("not running from a source checkout")

    text = rst_path.read_text(encoding="utf-8")
    examples = _scenes_from_rst(text, origin="checkout")
    assert len(examples) == 9
    for example in examples:
        ast.parse(example.source)  # every real example must at least parse


def test_search_examples_empty_query_returns_whole_corpus():
    results = search_examples(query="", limit=1000)
    assert len(results) == len(load_corpus())


def test_search_examples_name_match_ranks_first():
    results = search_examples(query="updater", limit=5)
    names = [r["name"] for r in results]
    assert names, "expected at least one match for 'updater'"
    assert "updater" in names[0].lower()


def test_search_examples_respects_limit():
    results = search_examples(query="", limit=2)
    assert len(results) <= 2


def test_interactive_only_scenes_are_excluded():
    names = {e.name for e in load_corpus()}
    assert "InteractiveDevelopment" not in names
    assert "ControlsExample" not in names
