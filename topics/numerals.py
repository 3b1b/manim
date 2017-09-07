
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
    def __init__(self, float_num, **kwargs):
        digest_config(self, kwargs)
        num_string = '%.*f'%(self.num_decimal_points, float_num)
        VMobject.__init__(self, *[
            TexMobject(char)
            for char in num_string
        ], **kwargs)
        self.arrange_submobjects(
            buff = self.digit_to_digit_buff,
            aligned_edge = DOWN
        )
        if float_num < 0:
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
        num_str = str(integer)
        VGroup.__init__(self, *map(TexMobject, num_str), **kwargs)
        self.arrange_submobjects(
            RIGHT, buff = self.digit_buff, aligned_edge = DOWN
        )
        if num_str[0] == "-":
            self[0].next_to(self[1], LEFT, buff = SMALL_BUFF)

#Todo, this class is now broken

class ChangingDecimal(Animation):
    CONFIG = {
        "num_decimal_points" : 2,
        "spare_parts" : 2,
        "position_update_func" : None,
        "tracked_mobject" : None,
    }
    def __init__(self, decimal_number, number_update_func, **kwargs):
        digest_config(self, kwargs, locals())
        decimal_number.add(*[
            VectorizedPoint(decimal_number.get_corner(DOWN+LEFT))
            for x in range(self.spare_parts)]
        )
        Animation.__init__(self, decimal_number, **kwargs)

    def update_mobject(self, alpha):
        self.update_number(alpha)
        self.update_position()

    def update_number(self, alpha):
        decimal = self.decimal_number
        new_decimal = DecimalNumber(
            self.number_update_func(alpha),
            num_decimal_points = self.num_decimal_points
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

    def update_position(self):
        if self.position_update_func is not None:
            self.position_update_func(self.decimal_number)
        elif self.tracked_mobject is not None:
            self.decimal_number.move_to(self.tracked_mobject)

class ContinualChangingDecimal(ContinualAnimation):
    def __init__(self, decimal_number, number_update_func, **kwargs):
        self.anim = ChangingDecimal(decimal_number, number_update_func, **kwargs)
        ContinualAnimation.__init__(self, decimal_number, **kwargs)

    def update_mobject(self, dt):
        self.anim.update(self.internal_time)
        


        
















