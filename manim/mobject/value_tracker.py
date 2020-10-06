"""Mobjects that dynamically show the change of a variable."""

__all__ = ["ValueTracker", "ExponentialValueTracker", "ComplexValueTracker"]


import numpy as np

from ..utils.paths import straight_path
from ..mobject.mobject import Mobject


class ValueTracker(Mobject):
    """A mobject that can be used for tracking (real-valued) parameters.
    Useful for animating parameter changes.

    Not meant to be displayed.  Instead the position encodes some
    number, often one which another animation or continual_animation
    uses for its update function, and by treating it as a mobject it can
    still be animated and manipulated just like anything else.

    Examples
    --------
    .. manim:: ValueTrackerExample

        class ValueTrackerExample(Scene):
            def construct(self):
                number_line = NumberLine()
                pointer = Vector(DOWN)
                label = MathTex("x").add_updater(lambda m: m.next_to(pointer, UP))

                pointer_value = ValueTracker(0)
                pointer.add_updater(
                    lambda m: m.next_to(
                                number_line.n2p(pointer_value.get_value()),
                                UP
                            )
                )
                self.add(number_line, pointer,label)
                self.play(pointer_value.set_value, 5)
                self.wait()
                self.play(pointer_value.set_value, 3)

    """

    def __init__(self, value=0, **kwargs):
        Mobject.__init__(self, **kwargs)
        self.points = np.zeros((1, 3))
        self.set_value(value)

    def get_value(self):
        return self.points[0, 0]

    def set_value(self, value):
        self.points[0, 0] = value
        return self

    def increment_value(self, d_value):
        self.set_value(self.get_value() + d_value)

    def __iadd__(self, d_value):
        self.increment_value(d_value)
        return self

    def interpolate(self, mobject1, mobject2, alpha, path_func=straight_path):
        """
        Turns self into an interpolation between mobject1
        and mobject2.
        """
        self.points = path_func(mobject1.points, mobject2.points, alpha)
        return self


class ExponentialValueTracker(ValueTracker):
    """
    Operates just like ValueTracker, except it encodes the value as the
    exponential of a position coordinate, which changes how interpolation
    behaves
    """

    def get_value(self):
        return np.exp(ValueTracker.get_value(self))

    def set_value(self, value):
        return ValueTracker.set_value(self, np.log(value))


class ComplexValueTracker(ValueTracker):
    def get_value(self):
        return complex(*self.points[0, :2])

    def set_value(self, z):
        z = complex(z)
        self.points[0, :2] = (z.real, z.imag)
        return self
