
from mobject.vectorized_mobject import VMobject, VGroup, VectorizedPoint
from mobject.tex_mobject import TexMobject
from animation import Animation
from animation.continual_animation import ContinualAnimation
from scene import Scene
from helpers import *

class DecimalNumber(VMobject):
    CONFIG = {
        "num_decimal_points" : 2,
        "digit_to_digit_buff" : 0.05
    }
    def __init__(self, number, **kwargs):
        digest_config(self, kwargs, locals())
        num_string = '%.*f'%(self.num_decimal_points, number)
        VMobject.__init__(self, *[
            TexMobject(char)
            for char in num_string
        ], **kwargs)
        self.arrange_submobjects(
            buff = self.digit_to_digit_buff,
            aligned_edge = DOWN
        )
        if number < 0:
            minus = self.submobjects[0]
            minus.next_to(
                self.submobjects[1], LEFT,
                buff = self.digit_to_digit_buff
            )

class Integer(VGroup):
    CONFIG = {
        "digit_buff" : 0.8*SMALL_BUFF
    }
    def __init__(self, integer, **kwargs):
        self.number = integer
        num_str = str(integer)
        VGroup.__init__(self, *map(TexMobject, num_str), **kwargs)
        self.arrange_submobjects(
            RIGHT, buff = self.digit_buff, aligned_edge = DOWN
        )
        if num_str[0] == "-":
            self[0].next_to(self[1], LEFT, buff = SMALL_BUFF)

class ChangingDecimal(Animation):
    CONFIG = {
        "num_decimal_points" : None,
        "spare_parts" : 2,
        "position_update_func" : None,
        "tracked_mobject" : None
    }
    def __init__(self, decimal_number_mobject, number_update_func, **kwargs):
        digest_config(self, kwargs, locals())
        if self.num_decimal_points is None:
            self.num_decimal_points = decimal_number_mobject.num_decimal_points
        decimal_number_mobject.add(*[
            VectorizedPoint(decimal_number_mobject.get_corner(DOWN+LEFT))
            for x in range(self.spare_parts)]
        )
        if self.tracked_mobject:
            self.diff_from_tracked_mobject = \
                decimal_number_mobject.get_center() - self.tracked_mobject.get_center()
        Animation.__init__(self, decimal_number_mobject, **kwargs)

    def update_mobject(self, alpha):
        self.update_number(alpha)
        self.update_position()

    def update_number(self, alpha):
        decimal = self.decimal_number_mobject
        new_number = self.number_update_func(alpha)
        new_decimal = DecimalNumber(
            new_number, num_decimal_points = self.num_decimal_points
        )
        new_decimal.replace(decimal, dim_to_match = 1)
        new_decimal.highlight(decimal.get_color())
        decimal.align_data(new_decimal)
        families = [
            mob.family_members_with_points()
            for mob in decimal, new_decimal
        ]
        for sm1, sm2 in zip(*families):
            sm1.interpolate(sm1, sm2, 1)
        self.mobject.number = new_number

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
        


        
















