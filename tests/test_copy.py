import os
from manim import Mobject, BraceLabel, file_writer_config


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
    original_text_dir = file_writer_config["text_dir"]
    original_tex_dir = file_writer_config["tex_dir"]
    mediadir = os.path.join(tmp_path, "deepcopy")
    file_writer_config["text_dir"] = os.path.join(mediadir, "Text")
    file_writer_config["tex_dir"] = os.path.join(mediadir, "Tex")
    for el in ["text_dir", "tex_dir"]:
        os.makedirs(file_writer_config[el])

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
    file_writer_config["text_dir"] = original_text_dir
    file_writer_config["tex_dir"] = original_tex_dir
