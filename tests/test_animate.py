import numpy as np
import pytest

from manim.mobject.mobject import override_animate
from manim.mobject.types.vectorized_mobject import VGroup
from manim.mobject.geometry import Dot, Line, Square
from manim.animation.creation import Uncreate


def test_simple_animate():
    s = Square()
    scale_factor = 2
    anim = s.animate.scale(scale_factor).build()
    assert anim.mobject.target.width == scale_factor * s.width


def test_chained_animate():
    s = Square()
    scale_factor = 2
    direction = np.array((1, 1, 0))
    anim = s.animate.scale(scale_factor).shift(direction).build()
    assert (
        anim.mobject.target.width == scale_factor * s.width
        and (anim.mobject.target.get_center() == direction).all()
    )


def test_overridden_animate():
    class DotsWithLine(VGroup):
        def __init__(self):
            super().__init__()
            self.left_dot = Dot().shift((-1, 0, 0))
            self.right_dot = Dot().shift((1, 0, 0))
            self.line = Line(self.left_dot, self.right_dot)
            self.add(self.left_dot, self.right_dot, self.line)

        def remove_line(self):
            self.remove(self.line)

        @override_animate(remove_line)
        def _remove_line_animation(self):
            self.remove_line()
            return Uncreate(self.line)

    dots_with_line = DotsWithLine()
    anim = dots_with_line.animate.remove_line().build()
    assert len(dots_with_line.submobjects) == 2
    assert type(anim) is Uncreate


def test_chaining_overridden_animate():
    class DotsWithLine(VGroup):
        def __init__(self):
            super().__init__()
            self.left_dot = Dot().shift((-1, 0, 0))
            self.right_dot = Dot().shift((1, 0, 0))
            self.line = Line(self.left_dot, self.right_dot)
            self.add(self.left_dot, self.right_dot, self.line)

        def remove_line(self):
            self.remove(self.line)

        @override_animate(remove_line)
        def _remove_line_animation(self):
            self.remove_line()
            return Uncreate(self.line)

    with pytest.raises(
        NotImplementedError, match="not supported for overridden animations"
    ):
        DotsWithLine().animate.shift((1, 0, 0)).remove_line()

    with pytest.raises(
        NotImplementedError, match="not supported for overridden animations"
    ):
        DotsWithLine().animate.remove_line().shift((1, 0, 0))
