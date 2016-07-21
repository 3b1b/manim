

from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TexMobject
from animation import Animation
from helpers import *



class DecimalNumber(VMobject):
    CONFIG = {
        "num_decimal_points" : 2,
        "digit_to_digit_buff" : 0.05
    }
    def __init__(self, float_num, **kwargs):
        digest_config(self, kwargs)
        num_string = '%.*f' % (self.num_decimal_points, float_num)
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



class RangingValues(Animation):
    CONFIG = {
        "num_decimal_points" : 2,
        "rate_func" : None,
        "tracking_function" : None,
        "value_function" : None,
        "tracked_mobject" : None,
        "tracked_mobject_next_to_kwargs" : {},
        "scale_val" : None
    }
    def __init__(self, start_val = 0, end_val = 1, **kwargs):
        digest_config(self, kwargs, locals())
        Animation.__init__(self, self.get_mobject_at_alpha(0), **kwargs)

    def update_mobject(self, alpha):
        target = self.get_mobject_at_alpha(alpha)
        self.mobject.submobjects = target.submobjects

    def get_number(self, alpha):
        if self.value_function:
            return self.value_function(alpha)
        return interpolate(self.start_val, self.end_val, alpha)

    def get_mobject_at_alpha(self, alpha):
        mob = DecimalNumber(
            self.get_number(alpha), 
            num_decimal_points=self.num_decimal_points
        )
        if self.scale_val:
            mob.scale(self.scale_val)
        if self.tracking_function:
            self.tracking_function(alpha, mob)
        elif self.tracked_mobject:
            mob.next_to(
                self.tracked_mobject,
                **self.tracked_mobject_next_to_kwargs
            )
        return mob

    def set_tracking_function(self, func):
        """
        func shoudl be of the form func(alpha, mobject), and
        should dictate where to place running number during an 
        animation
        """
        self.tracking_function = func

    def set_value_function(self, func):
        """
        func must be of the form alpha->number
        """
        self.value_function = func
