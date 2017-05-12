

from mobject.vectorized_mobject import VMobject, VGroup
from mobject.tex_mobject import TexMobject
from animation import Animation
from scene import Scene
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

class Integer(VGroup):
    def __init__(self, integer, **kwargs):
        num_str = str(integer)
        VGroup.__init__(self, *map(TexMobject, num_str), **kwargs)
        self.arrange_submobjects(
            RIGHT, buff = SMALL_BUFF, aligned_edge = DOWN
        )
        if num_str[0] == "-":
            self[0].next_to(self[1], LEFT, buff = SMALL_BUFF)

#Todo, this class is now broken

class RangingValue(Animation):
    CONFIG = {
        "num_decimal_points" : 2,
        "rate_func" : None,
        "tracked_mobject" : None,
        "tracked_mobject_next_to_kwargs" : {},
        "scale_factor" : None,
        "color" : WHITE,
    }
    def __init__(self, value_function, **kwargs):
        """
        Value function should return a real value 
        depending on the state of the surrounding scene    
        """
        digest_config(self, kwargs, locals())
        self.update_mobject()
        Animation.__init__(self, self.mobject, **kwargs)

    def update_mobject(self, alpha = 0):
        mobject = DecimalNumber(
            self.value_function(alpha),
            num_decimal_points = self.num_decimal_points,
            color = self.color,
        )
        if not hasattr(self, "mobject"):
            self.mobject = mobject
        else:
            self.mobject.points = mobject.points
            self.mobject.submobjects = mobject.submobjects
        if self.scale_factor:
            self.mobject.scale(self.scale_factor)
        elif self.tracked_mobject:
            self.mobject.next_to(
                self.tracked_mobject,
                **self.tracked_mobject_next_to_kwargs
            )
        return self


class RangingValueScene(Scene):
    CONFIG = {
        "ranging_values" : []
    }

    def add_ranging_value(self, value_function, **kwargs):
        self.ranging_values.append(
            RangingValue(value_function, **kwargs)
        )

    def update_frame(self, *args, **kwargs):
        for val in self.ranging_values:
            self.remove(val.mobject)
            val.update_mobject()
            self.add(val.mobject)
        return Scene.update_frame(self, *args, **kwargs)






