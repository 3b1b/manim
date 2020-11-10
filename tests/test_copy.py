from pathlib import Path
from manim import Mobject, BraceLabel, config


def test_mobject_copy():
    """Test that a copy is a deepcopy."""
    orig = Mobject()
    orig.add(*[Mobject() for _ in range(10)])
    copy = orig.copy()

    assert orig is orig
    assert orig is not copy
    assert orig.submobjects is not copy.submobjects
    for i in range(10):
        assert orig.submobjects[i] is not copy.submobjects[i]


def test_bracelabel_copy(tmp_path):
    """Test that a copy is a deepcopy."""
    # For this test to work, we need to tweak some folders temporarily
    original_text_dir = config["text_dir"]
    original_tex_dir = config["tex_dir"]
    mediadir = Path(tmp_path) / "deepcopy"
    config["text_dir"] = str(mediadir.joinpath("Text"))
    config["tex_dir"] = str(mediadir.joinpath("Tex"))
    for el in ["text_dir", "tex_dir"]:
        Path(config[el]).mkdir(parents=True)

    # Before the refactoring of Mobject.copy(), the class BraceLabel was the
    # only one to have a non-trivial definition of copy.  Here we test that it
    # still works after the refactoring.
    orig = BraceLabel(Mobject(), "label")
    copy = orig.copy()

    assert orig is orig
    assert orig is not copy
    assert orig.brace is not copy.brace
    assert orig.label is not copy.label
    assert orig.submobjects is not copy.submobjects
    assert orig.submobjects[0] is orig.brace
    assert copy.submobjects[0] is copy.brace
    assert orig.submobjects[0] is not copy.brace
    assert copy.submobjects[0] is not orig.brace

    # Restore the original folders
    config["text_dir"] = original_text_dir
    config["tex_dir"] = original_tex_dir
