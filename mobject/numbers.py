from __future__ import absolute_import

from constants import *

from mobject.svg.tex_mobject import TexMobject
from mobject.types.vectorized_mobject import VMobject


class DecimalNumber(VMobject):
    CONFIG = {
        "num_decimal_places": 2,
        "digit_to_digit_buff": 0.05,
        "show_ellipsis": False,
        "unit": None,  # Aligned to bottom unless it starts with "^"
        "include_background_rectangle": False,
    }

    def __init__(self, number, **kwargs):
        VMobject.__init__(self, **kwargs)
        # TODO, make this more ediable with a getter and setter
        self.number = number
        ndp = self.num_decimal_places

        # Build number string
        if isinstance(number, complex):
            num_string = '%.*f%s%.*fi' % (
                ndp, number.real,
                "-" if number.imag < 0 else "+",
                ndp, abs(number.imag)
            )
        else:
            num_string = '%.*f' % (ndp, number)
            negative_zero_string = "-%.*f" % (ndp, 0.)
            if num_string == negative_zero_string:
                num_string = num_string[1:]
        self.add(*[
            TexMobject(char, **kwargs)
            for char in num_string
        ])

        # Add non-numerical bits
        if self.show_ellipsis:
            self.add(TexMobject("\\dots"))

        if num_string.startswith("-"):
            minus = self.submobjects[0]
            minus.next_to(
                self.submobjects[1], LEFT,
                buff=self.digit_to_digit_buff
            )

        if self.unit is not None:
            self.unit_sign = TexMobject(self.unit, color=self.color)
            self.add(self.unit_sign)

        self.arrange_submobjects(
            buff=self.digit_to_digit_buff,
            aligned_edge=DOWN
        )

        # Handle alignment of parts that should be aligned
        # to the bottom
        for i, c in enumerate(num_string):
            if c == "-" and len(num_string) > i + 1:
                self[i].align_to(self[i + 1], alignment_vect=UP)
        if self.unit and self.unit.startswith("^"):
            self.unit_sign.align_to(self, UP)
        #
        if self.include_background_rectangle:
            self.add_background_rectangle()


class Integer(DecimalNumber):
    CONFIG = {
        "num_decimal_places": 0,
    }
