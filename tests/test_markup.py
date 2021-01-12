import pytest
from manim import MarkupText


def test_good_markup():
    """Test creation of valid :class:`MarkupText` object"""
    try:
        text1 = MarkupText("<b>foo</b>")
        text2 = MarkupText("foo")
        success = True
    except ValueError:
        success = False
    assert success, "'<b>foo</b>' and 'foo' should not fail validation"


def test_special_tags_markup():
    """Test creation of valid :class:`MarkupText` object with unofficial tags"""
    try:
        text1 = MarkupText('<color col="RED">foo</color>')
        text1 = MarkupText('<gradient from="RED" to="YELLOW">foo</gradient>')
        success = True
    except ValueError:
        success = False
    assert (
        success
    ), '\'<color col="RED">foo</color>\' and \'<gradient from="RED" to="YELLOW">foo</gradient>\' should not fail validation'


def test_unbalanced_tag_markup():
    """Test creation of invalid :class:`MarkupText` object (unbalanced tag)"""
    try:
        text = MarkupText("<b>foo")
        success = False
    except ValueError:
        success = True
    assert success, "'<b>foo' should fail validation"


def test_invalid_tag_markup():
    """Test creation of invalid :class:`MarkupText` object (invalid tag)"""
    try:
        text = MarkupText("<invalidtag>foo</invalidtag>")
        success = False
    except ValueError:
        success = True

    assert success, "'<invalidtag>foo</invalidtag>' should fail validation"
