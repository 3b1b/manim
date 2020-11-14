import pytest
from manim.animation.composition import Succession
from manim.animation.fading import FadeInFrom, FadeOutAndShift
from manim.constants import DOWN
from manim.mobject.geometry import Line


def test_succession_timing():
    """Test timing of animations in a succession."""
    line = Line()
    animation_1s = FadeInFrom(line, direction=DOWN, run_time=1.0)
    animation_4s = FadeOutAndShift(line, direction=DOWN, run_time=4.0)
    succession = Succession(animation_1s, animation_4s)
    assert succession.get_run_time() == 5.0
    succession.begin()
    assert succession.active_index == 0
    # The first animation takes 20% of the total run time.
    succession.interpolate(0.199)
    assert succession.active_index == 0
    succession.interpolate(0.2)
    assert succession.active_index == 1
    succession.interpolate(0.8)
    assert succession.active_index == 1
    # At 100% and more, no animation must be active anymore.
    succession.interpolate(1.0)
    assert succession.active_index == 2
    assert succession.active_animation is None
    succession.interpolate(1.2)
    assert succession.active_index == 2
    assert succession.active_animation is None


def test_succession_in_succession_timing():
    """Test timing of nested successions."""
    line = Line()
    animation_1s = FadeInFrom(line, direction=DOWN, run_time=1.0)
    animation_4s = FadeOutAndShift(line, direction=DOWN, run_time=4.0)
    nested_succession = Succession(animation_1s, animation_4s)
    succession = Succession(
        FadeInFrom(line, direction=DOWN, run_time=4.0),
        nested_succession,
        FadeInFrom(line, direction=DOWN, run_time=1.0),
    )
    assert nested_succession.get_run_time() == 5.0
    assert succession.get_run_time() == 10.0
    succession.begin()
    succession.interpolate(0.1)
    assert succession.active_index == 0
    # The nested succession must not be active yet, and as a result hasn't set active_animation yet.
    assert not hasattr(nested_succession, "active_animation")
    succession.interpolate(0.39)
    assert succession.active_index == 0
    assert not hasattr(nested_succession, "active_animation")
    # The nested succession starts at 40% of total run time
    succession.interpolate(0.4)
    assert succession.active_index == 1
    assert nested_succession.active_index == 0
    # The nested succession second animation starts at 50% of total run time.
    succession.interpolate(0.49)
    assert succession.active_index == 1
    assert nested_succession.active_index == 0
    succession.interpolate(0.5)
    assert succession.active_index == 1
    assert nested_succession.active_index == 1
    # The last animation starts at 90% of total run time. The nested succession must be finished at that time.
    succession.interpolate(0.89)
    assert succession.active_index == 1
    assert nested_succession.active_index == 1
    succession.interpolate(0.9)
    assert succession.active_index == 2
    assert nested_succession.active_index == 2
    assert nested_succession.active_animation is None
    # After 100%, nothing must be playing anymore.
    succession.interpolate(1.0)
    assert succession.active_index == 3
    assert succession.active_animation is None
    assert nested_succession.active_index == 2
    assert nested_succession.active_animation is None
