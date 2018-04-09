from __future__ import absolute_import

import numpy as np

from constants import *

from mobject.types.vectorized_mobject import VectorizedPoint

# TODO: Rather than using VectorizedPoint, there should be some UndisplayedPointSet type


class ValueTracker(VectorizedPoint):
    """
    Note meant to be displayed.  Instead the position encodes some
    number, often one which another animation or continual_animation
    uses for its update function, and by treating it as a mobject it can
    still be animated and manipulated just like anything else.
    """

    def __init__(self, value=0, **kwargs):
        VectorizedPoint.__init__(self, **kwargs)
        self.set_value(value)

    def get_value(self):
        return self.get_center()[0]

    def set_value(self, value):
        self.move_to(value * RIGHT)
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
        return np.exp(self.get_center()[0])

    def set_value(self, value):
        self.move_to(np.log(value) * RIGHT)
        return self
