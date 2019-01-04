from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import SingleStringTexMobject
from manimlib.mobject.types.vectorized_mobject import VMobject


class DecimalNumber(VMobject):
    CONFIG = {
        "num_decimal_places": 2,
        "include_sign": False,
        "group_with_commas": True,
        "digit_to_digit_buff": 0.05,
        "show_ellipsis": False,
        "unit": None,  # Aligned to bottom unless it starts with "^"
        "include_background_rectangle": False,
        "edge_to_fix": LEFT,
    }

    def __init__(self, number, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.number = number
        self.initial_config = kwargs

        if isinstance(number, complex):
            formatter = self.get_complex_formatter()
        else:
            formatter = self.get_formatter()
        num_string = formatter.format(number)

        shows_zero = np.round(number, self.num_decimal_places) == 0
        if num_string.startswith("-") and shows_zero:
            if self.include_sign:
                num_string = "+" + num_string[1:]
            else:
                num_string = num_string[1:]

        self.add(*[
            SingleStringTexMobject(char, **kwargs)
            for char in num_string
        ])

        # Add non-numerical bits
        if self.show_ellipsis:
            self.add(SingleStringTexMobject("\\dots"))

        if num_string.startswith("-"):
            minus = self.submobjects[0]
            minus.next_to(
                self.submobjects[1], LEFT,
                buff=self.digit_to_digit_buff
            )

        if self.unit is not None:
            self.unit_sign = SingleStringTexMobject(self.unit, color=self.color)
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
            elif c == ",":
                self[i].shift(self[i].get_height() * DOWN / 2)
        if self.unit and self.unit.startswith("^"):
            self.unit_sign.align_to(self, UP)
        #
        if self.include_background_rectangle:
            self.add_background_rectangle()

    def get_formatter(self, **kwargs):
        """
        Configuration is based first off instance attributes,
        but overwritten by any kew word argument.  Relevant
        key words:
        - include_sign
        - group_with_commas
        - num_decimal_places
        - field_name (e.g. 0 or 0.real)
        """
        config = dict(self.__dict__)
        config.update(kwargs)
        return "".join([
            "{",
            config.get("field_name", ""),
            ":",
            "+" if config["include_sign"] else "",
            "," if config["group_with_commas"] else "",
            ".", str(config["num_decimal_places"]), "f",
            "}",
        ])

    def get_complex_formatter(self, **kwargs):
        return "".join([
            self.get_formatter(field_name="0.real"),
            self.get_formatter(field_name="0.imag", include_sign=True),
            "i"
        ])

    def set_value(self, number, **config):
        full_config = dict(self.CONFIG)
        full_config.update(self.initial_config)
        full_config.update(config)
        new_decimal = DecimalNumber(number, **full_config)
        new_decimal.match_height(self)
        new_decimal.move_to(self, self.edge_to_fix)
        new_decimal.match_style(self)

        old_family = self.get_family()
        self.submobjects = new_decimal.submobjects
        for mob in old_family:
            # Dumb hack...due to how scene handles families
            # of animated mobjects
            mob.points[:] = 0
        self.number = number
        return self

    def get_value(self):
        return self.number


class Integer(DecimalNumber):
    CONFIG = {
        "num_decimal_places": 0,
    }

    def increment_value(self):
        self.set_value(self.get_value() + 1)
