from __future__ import absolute_import

from constants import *

from animation.animation import Animation
from mobject.numbers import DecimalNumber
from utils.bezier import interpolate
from utils.config_ops import digest_config


class ChangingDecimal(Animation):
    CONFIG = {
        "num_decimal_places": None,
        "show_ellipsis": None,
        "position_update_func": None,
        "include_sign": None,
        "tracked_mobject": None,
    }

    def __init__(self, decimal_number_mobject, number_update_func, **kwargs):
        digest_config(self, kwargs, locals())
        self.decimal_number_config = dict(
            decimal_number_mobject.initial_config
        )
        for attr in "num_decimal_places", "show_ellipsis", "include_sign":
            value = getattr(self, attr)
            if value is not None:
                self.decimal_number_config[attr] = value
        if hasattr(self.decimal_number_mobject, "background_rectangle"):
            self.decimal_number_config["include_background_rectangle"] = True
        if self.tracked_mobject:
            dmc = decimal_number_mobject.get_center()
            tmc = self.tracked_mobject.get_center()
            self.diff_from_tracked_mobject = dmc - tmc
        Animation.__init__(self, decimal_number_mobject, **kwargs)

    def update_mobject(self, alpha):
        self.update_number(alpha)
        self.update_position()

    def update_number(self, alpha):
        decimal = self.decimal_number_mobject
        new_number = self.number_update_func(alpha)
        new_decimal = DecimalNumber(
            new_number, **self.decimal_number_config
        )
        new_decimal.match_height(decimal)
        new_decimal.move_to(decimal)
        new_decimal.match_style(decimal)

        decimal.submobjects = new_decimal.submobjects
        decimal.number = new_number

    def update_position(self):
        if self.position_update_func is not None:
            self.position_update_func(self.decimal_number_mobject)
        elif self.tracked_mobject is not None:
            self.decimal_number_mobject.move_to(
                self.tracked_mobject.get_center() + self.diff_from_tracked_mobject)


class ChangeDecimalToValue(ChangingDecimal):
    def __init__(self, decimal_number_mobject, target_number, **kwargs):
        start_number = decimal_number_mobject.number

        def func(alpha):
            return interpolate(start_number, target_number, alpha)
        ChangingDecimal.__init__(self, decimal_number_mobject, func, **kwargs)
