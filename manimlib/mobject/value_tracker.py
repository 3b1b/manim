from __future__ import annotations

import numpy as np
from manimlib.mobject.mobject import Mobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import listify
from manimlib.utils.paths import straight_path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import Self


class ValueTracker(Mobject):
    """
    Not meant to be displayed.  Instead the position encodes some
    number, often one which another animation or continual_animation
    uses for its update function, and by treating it as a mobject it can
    still be animated and manipulated just like anything else.

    The value is held here rather than among the uniforms, which are floats laid out
    to match what a shader expects, since a tracker's value may be complex, or an
    array of any length, and never reaches a shader in any case.
    """
    value_type: type = np.float64

    def __init__(
        self,
        value: float | complex | np.ndarray = 0,
        **kwargs
    ):
        self.value = np.array(listify(value), dtype=self.value_type)
        super().__init__(**kwargs)

    def get_value(self) -> float | complex | np.ndarray:
        result = self.value
        if len(result) == 1:
            return result[0]
        return result

    def set_value(self, value: float | complex | np.ndarray) -> Self:
        # Written in place to keep the broadcasting behavior
        self.value[:] = value
        return self

    def increment_value(self, d_value: float | complex) -> None:
        self.set_value(self.get_value() + d_value)

    def interpolate(
        self,
        mobject1: ValueTracker,
        mobject2: ValueTracker,
        alpha: float,
        path_func: Callable[[np.ndarray, np.ndarray, float], np.ndarray] = straight_path
    ) -> Self:
        super().interpolate(mobject1, mobject2, alpha, path_func)
        # What gets interpolated is the value as held, not as get_value returns it,
        # which is what lets a subclass change how animating it behaves by encoding
        # it differently
        self.value[:] = interpolate(mobject1.value, mobject2.value, alpha)
        return self

    def become(self, mobject: ValueTracker, match_updaters: bool = False) -> Self:
        super().become(mobject, match_updaters)
        self.value = mobject.value.copy()
        return self


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
