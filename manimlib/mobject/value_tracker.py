import numpy as np

from manimlib.mobject.mobject import Mobject


class ValueTracker(Mobject):
    """
    Note meant to be displayed.  Instead the position encodes some
    number, often one which another animation or continual_animation
    uses for its update function, and by treating it as a mobject it can
    still be animated and manipulated just like anything else.
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
