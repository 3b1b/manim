"""Animations for changing numbers."""

__all__ = ["ChangingDecimal", "ChangeDecimalToValue"]


import typing
import warnings

from ..animation.animation import Animation
from ..mobject.numbers import DecimalNumber
from ..utils.bezier import interpolate


class ChangingDecimal(Animation):
    def __init__(
        self,
        decimal_mob: DecimalNumber,
        number_update_func: typing.Callable[[float], float],
        suspend_mobject_updating: typing.Optional[bool] = False,
        **kwargs,
    ) -> None:
        self.check_validity_of_input(decimal_mob)
        self.yell_about_depricated_configuration(**kwargs)
        self.number_update_func = number_update_func
        super().__init__(
            decimal_mob, suspend_mobject_updating=suspend_mobject_updating, **kwargs
        )

    def check_validity_of_input(self, decimal_mob: DecimalNumber) -> None:
        if not isinstance(decimal_mob, DecimalNumber):
            raise TypeError("ChangingDecimal can only take in a DecimalNumber")

    def yell_about_depricated_configuration(self, **kwargs) -> None:
        # Obviously this would optimally be removed at
        # some point.
        for attr in ["tracked_mobject", "position_update_func"]:
            if attr in kwargs:
                warnings.warn(
                    f"""
                    Don't use {attr} for ChangingDecimal,
                    that functionality has been depricated
                    and you should use a mobject updater
                    instead
                """
                )

    def interpolate_mobject(self, alpha: float) -> None:
        self.mobject.set_value(self.number_update_func(alpha))


class ChangeDecimalToValue(ChangingDecimal):
    def __init__(
        self, decimal_mob: DecimalNumber, target_number: int, **kwargs
    ) -> None:
        start_number = decimal_mob.number
        super().__init__(
            decimal_mob, lambda a: interpolate(start_number, target_number, a), **kwargs
        )
