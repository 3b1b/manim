import pytest
from manim import Mobject, VMobject, VGroup, VDict


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


def test_vdict_init():
    """Test the VDict instantiation."""
    # Test empty VDict
    VDict()
    # Test VDict made from list of pairs
    VDict([("a", VMobject()), ("b", VMobject()), ("c", VMobject())])
    # Test VDict made from a python dict
    VDict({"a": VMobject(), "b": VMobject(), "c": VMobject()})
    # Test VDict made using zip
    VDict(zip(["a", "b", "c"], [VMobject(), VMobject(), VMobject()]))
    # If the value is of type Mobject, must raise a TypeError
    with pytest.raises(TypeError):
        VDict({"a": Mobject()})


def test_vdict_add():
    """Test the VDict add method."""
    obj = VDict()
    assert len(obj.submob_dict) == 0
    obj.add([("a", VMobject())])
    assert len(obj.submob_dict) == 1
    with pytest.raises(TypeError):
        obj.add([("b", Mobject())])


def test_vdict_remove():
    """Test the VDict remove method."""
    obj = VDict([("a", VMobject())])
    assert len(obj.submob_dict) == 1
    obj.remove("a")
    assert len(obj.submob_dict) == 0
    with pytest.raises(KeyError):
        obj.remove("a")
