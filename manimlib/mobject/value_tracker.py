from __future__ import annotations

import numpy as np

from manimlib.mobject.mobject import Mobject
from manimlib.utils.iterables import listify


class ValueTracker(Mobject):
    """
    Not meant to be displayed.  Instead the position encodes some
    number, often one which another animation or continual_animation
    uses for its update function, and by treating it as a mobject it can
    still be animated and manipulated just like anything else.
    """
    value_type: type = np.float64

    def __init__(
        self,
        value: float | complex | np.ndarray = 0,
        **kwargs
    ):
        self.value = value
        super().__init__(**kwargs)

    def init_data(self) -> None:
        super().init_data()
        self.data["value"] = np.array(
            listify(self.value),
            ndmin=2,
            dtype=self.value_type,
        )

    def get_value(self) -> float | complex:
        result = self.data["value"][0, :]
        if len(result) == 1:
            return result[0]
        return result

    def set_value(self, value: float | complex):
        self.data["value"][0, :] = value
        return self

    def increment_value(self, d_value: float | complex) -> None:
        self.set_value(self.get_value() + d_value)


class ExponentialValueTracker(ValueTracker):
    """
    Operates just like ValueTracker, except it encodes the value as the
    exponential of a position coordinate, which changes how interpolation
    behaves
    """

    def get_value(self) -> float | complex:
        return np.exp(ValueTracker.get_value(self))

    def set_value(self, value: float | complex):
        return ValueTracker.set_value(self, np.log(value))


class ComplexValueTracker(ValueTracker):
    value_type: type = np.complex128
