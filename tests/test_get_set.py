import types
import pytest

from manim.mobject.mobject import Mobject


def test_generic_set():
    m = Mobject()
    m.set(test=0)

    assert m.test == 0


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_get_compat_layer():
    m = Mobject()

    assert isinstance(m.get_test, types.MethodType)
    with pytest.raises(AttributeError):
        m.get_test()

    m.test = 0
    assert m.get_test() == 0


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_set_compat_layer():
    m = Mobject()

    assert isinstance(m.set_test, types.MethodType)
    m.set_test(0)

    assert m.test == 0


def test_nonexistent_attr():
    m = Mobject()

    with pytest.raises(AttributeError):
        m.test
