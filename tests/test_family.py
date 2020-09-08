import numpy as np
from manim import Mobject, Circle, RIGHT


def test_family():
    """Check that the family is gathered correctly."""
    # Check that an empty mobject's family only contains itself
    mob = Mobject()
    assert mob.get_family() == [mob]

    # Check that all children are in the family
    mob = Mobject()
    children = [Mobject() for _ in range(10)]
    mob.add(*children)
    family = mob.get_family()
    assert len(family) == 1 + 10
    assert mob in family
    for c in children:
        assert c in family

    # Nested children should be in the family
    mob = Mobject()
    grandchildren = {}
    for _ in range(10):
        child = Mobject()
        grandchildren[child] = [Mobject() for _ in range(10)]
        child.add(*grandchildren[child])
    mob.add(*list(grandchildren.keys()))
    family = mob.get_family()
    assert len(family) == 1 + 10 + 10 * 10
    assert mob in family
    for c in grandchildren:
        assert c in family
        for gc in grandchildren[c]:
            assert gc in family


def test_overlapping_family():
    """Check that each member of the family is only gathered once."""
    mob, child1, child2, = (
        Mobject(),
        Mobject(),
        Mobject(),
    )
    gchild1, gchild2, gchild_common = Mobject(), Mobject(), Mobject()
    child1.add(gchild1, gchild_common)
    child2.add(gchild2, gchild_common)
    mob.add(child1, child2)
    family = mob.get_family()
    assert mob in family
    assert len(family) == 6
    assert family.count(gchild_common) == 1


def test_shift_family():
    """Check that each member of the family is shifted along with the parent.

    Importantly, here we add a common grandchild to each of the children.  So
    this test will fail if the grandchild moves twice as much as it should.

    """
    # Note shift() needs the mobject to have a non-empty `points` attribute, so
    # we cannot use a plain Mobject or VMobject.  We use Circle instead.
    mob, child1, child2, = (
        Circle(),
        Circle(),
        Circle(),
    )
    gchild1, gchild2, gchild_common = Circle(), Circle(), Circle()

    child1.add(gchild1, gchild_common)
    child2.add(gchild2, gchild_common)
    mob.add(child1, child2)
    family = mob.get_family()

    positions_before = {m: m.get_center() for m in family}
    mob.shift(RIGHT)
    positions_after = {m: m.get_center() for m in family}

    for m in family:
        assert np.allclose(positions_before[m] + RIGHT, positions_after[m])
