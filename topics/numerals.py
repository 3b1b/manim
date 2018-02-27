
from mobject.vectorized_mobject import VMobject, VGroup, VectorizedPoint
from mobject.tex_mobject import TexMobject
from animation import Animation
from animation.continual_animation import ContinualAnimation
from topics.geometry import BackgroundRectangle
from scene import Scene
from helpers import *

class DecimalNumber(VMobject):
    CONFIG = {
        "num_decimal_points" : 2,
        "digit_to_digit_buff" : 0.05,
        "show_ellipsis" : False,
        "unit" : None, #Aligned to bottom unless it starts with "^"
        "include_background_rectangle" : False,
    }
    def __init__(self, number, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.number = number
        ndp = self.num_decimal_points

        #Build number string
        if isinstance(number, complex):
            num_string = '%.*f%s%.*fi'%(
                ndp, number.real, 
                "-" if number.imag < 0 else "+",
                ndp, abs(number.imag)
            )
        else:
            num_string = '%.*f'%(ndp, number)
            negative_zero_string = "-%.*f"%(ndp, 0.)
            if num_string == negative_zero_string:
                num_string = num_string[1:]
        self.add(*[
            TexMobject(char, **kwargs)
            for char in num_string
        ])

        #Add non-numerical bits
        if self.show_ellipsis:
            self.add(TexMobject("\\dots"))


        if num_string.startswith("-"):
            minus = self.submobjects[0]
            minus.next_to(
                self.submobjects[1], LEFT,
                buff = self.digit_to_digit_buff
            )

        if self.unit != None:
            self.unit_sign = TexMobject(self.unit)
            self.add(self.unit_sign)

        self.arrange_submobjects(
            buff = self.digit_to_digit_buff,
            aligned_edge = DOWN
        )

        #Handle alignment of parts that should be aligned
        #to the bottom
        for i, c in enumerate(num_string):
            if c == "-" and len(num_string) > i+1:
                self[i].align_to(self[i+1], alignment_vect = UP)
        if self.unit and self.unit.startswith("^"):
            self.unit_sign.align_to(self, UP)
        #
        if self.include_background_rectangle:
            self.add_background_rectangle()

    def add_background_rectangle(self):
        #TODO, is this the best way to handle
        #background rectangles?
        self.background_rectangle = BackgroundRectangle(self)
        self.submobjects = [
            self.background_rectangle,
            VGroup(*self.submobjects)
        ]
        return self

class Integer(DecimalNumber):
    CONFIG = {
        "num_decimal_points" : 0,
    }

class ChangingDecimal(Animation):
    CONFIG = {
        "num_decimal_points" : None,
        "show_ellipsis" : None,
        "position_update_func" : None,
        "tracked_mobject" : None,
    }
    def __init__(self, decimal_number_mobject, number_update_func, **kwargs):
        digest_config(self, kwargs, locals())
        self.decimal_number_config = dict(
            decimal_number_mobject.initial_config
        )
        for attr in "num_decimal_points", "show_ellipsis":
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
            self.decimal_number_mobject.move_to(self.tracked_mobject.get_center() + self.diff_from_tracked_mobject)

class ChangeDecimalToValue(ChangingDecimal):
    def __init__(self, decimal_number_mobject, target_number, **kwargs):
        start_number = decimal_number_mobject.number
        func = lambda alpha : interpolate(start_number, target_number, alpha)
        ChangingDecimal.__init__(self, decimal_number_mobject, func, **kwargs)

class ContinualChangingDecimal(ContinualAnimation):
    def __init__(self, decimal_number_mobject, number_update_func, **kwargs):
        self.anim = ChangingDecimal(decimal_number_mobject, number_update_func, **kwargs)
        ContinualAnimation.__init__(self, decimal_number_mobject, **kwargs)

    def update_mobject(self, dt):
        self.anim.update(self.internal_time)


        
















