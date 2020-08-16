import pytest
from manim import Mobject, VMobject, VGroup


def test_vgroup_init():
    """Test the VGroup instantiation."""
    VGroup()
    VGroup(VMobject())
    VGroup(VMobject(), VMobject())
    with pytest.raises(TypeError):
        VGroup(Mobject())
    with pytest.raises(TypeError):
        VGroup(Mobject(), Mobject())


def test_vgroup_add():
    """Test the VGroup add method."""
    obj = VGroup()
    assert len(obj.submobjects) == 0
    obj.add(VMobject())
    assert len(obj.submobjects) == 1
    with pytest.raises(TypeError):
        obj.add(Mobject())
    assert len(obj.submobjects) == 1
    with pytest.raises(TypeError):
        # If only one of the added object is not an instance of VMobject, none of them should be added
        obj.add(VMobject(), Mobject())
    assert len(obj.submobjects) == 1
    with pytest.raises(Exception):  # TODO change this to ValueError once #307 is merged
        # a Mobject cannot contain itself
        obj.add(obj)
