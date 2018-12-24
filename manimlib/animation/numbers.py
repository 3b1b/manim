from manimlib.animation.animation import Animation
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config


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
        if self.tracked_mobject:
            dmc = decimal_number_mobject.get_center()
            tmc = self.tracked_mobject.get_center()
            self.diff_from_tracked_mobject = dmc - tmc
            self.diff_from_tracked_mobject = dmc - tmc
        Animation.__init__(self, decimal_number_mobject, **kwargs)

    def update_mobject(self, alpha):
        self.update_number(alpha)
        self.update_position()

    def update_number(self, alpha):
        self.decimal_number_mobject.set_value(
            self.number_update_func(alpha)
        )

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
