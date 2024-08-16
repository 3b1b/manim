from __future__ import annotations

from manimlib.animation.animation import Animation
from manimlib.mobject.numbers import DecimalNumber
from manimlib.utils.bezier import interpolate
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable


class ChangingDecimal(Animation):
    def __init__(
        self,
        decimal_mob: DecimalNumber,
        number_update_func: Callable[[float], float],
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        assert isinstance(decimal_mob, DecimalNumber)
        self.number_update_func = number_update_func
        super().__init__(
            decimal_mob,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )
        self.mobject = decimal_mob

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
        start_number = decimal_mob.get_value()
        super().__init__(
            decimal_mob,
            lambda a: interpolate(source_number, start_number, clip(a, 0, 1)),
            **kwargs
        )
