from __future__ import annotations

from typing import Callable

from manimlib.animation.animation import Animation
from manimlib.mobject.numbers import DecimalNumber
from manimlib.utils.bezier import interpolate


class ChangingDecimal(Animation):
    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def __init__(
        self,
        decimal_mob: DecimalNumber,
        number_update_func: Callable[[float], float],
        **kwargs
    ):
        assert(isinstance(decimal_mob, DecimalNumber))
        self.number_update_func = number_update_func
        super().__init__(decimal_mob, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        self.mobject.set_value(
            self.number_update_func(alpha)
        )


class ChangeDecimalToValue(ChangingDecimal):
    def __init__(
        self,
        decimal_mob: DecimalNumber,
        target_number: float | complex,
        **kwargs
    ):
        start_number = decimal_mob.number
        super().__init__(
            decimal_mob,
            lambda a: interpolate(start_number, target_number, a),
            **kwargs
        )


class CountInFrom(ChangingDecimal):
    def __init__(
        self,
        decimal_mob: DecimalNumber,
        source_number: float | complex = 0,
        **kwargs
    ):
        start_number = decimal_mob.number
        super().__init__(
            decimal_mob,
            lambda a: interpolate(source_number, start_number, a),
            **kwargs
        )
