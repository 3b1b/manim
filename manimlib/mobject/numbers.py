from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VMobject


string_to_mob_map = {}


class DecimalNumber(VMobject):
    CONFIG = {
        "stroke_width": 0,
        "fill_opacity": 1.0,
        "num_decimal_places": 2,
        "include_sign": False,
        "group_with_commas": True,
        "digit_buff_per_font_unit": 0.001,
        "show_ellipsis": False,
        "unit": None,  # Aligned to bottom unless it starts with "^"
        "include_background_rectangle": False,
        "edge_to_fix": LEFT,
        "font_size": 48,
    }

    def __init__(self, number=0, **kwargs):
        super().__init__(**kwargs)
        self.set_submobjects_from_number(number)
        self.init_colors()

    def set_submobjects_from_number(self, number):
        self.number = number
        self.set_submobjects([])

        num_string = self.get_num_string(number)
        self.add(*map(self.string_to_mob, num_string))

        # Add non-numerical bits
        if self.show_ellipsis:
            dots = self.string_to_mob("...")
            dots.arrange(RIGHT, buff=2 * dots[0].get_width())
            self.add(dots)
        if self.unit is not None:
            self.unit_sign = self.string_to_mob(self.unit, Tex)
            self.add(self.unit_sign)

        self.arrange(
            buff=self.digit_buff_per_font_unit * self.get_font_size(),
            aligned_edge=DOWN
        )

        # Handle alignment of parts that should be aligned
        # to the bottom
        for i, c in enumerate(num_string):
            if c == "–" and len(num_string) > i + 1:
                self[i].align_to(self[i + 1], UP)
                self[i].shift(self[i + 1].get_height() * DOWN / 2)
            elif c == ",":
                self[i].shift(self[i].get_height() * DOWN / 2)
        if self.unit and self.unit.startswith("^"):
            self.unit_sign.align_to(self, UP)

        if self.include_background_rectangle:
            self.add_background_rectangle()

    def get_num_string(self, number):
        if isinstance(number, complex):
            formatter = self.get_complex_formatter()
        else:
            formatter = self.get_formatter()
        num_string = formatter.format(number)

        rounded_num = np.round(number, self.num_decimal_places)
        if num_string.startswith("-") and rounded_num == 0:
            if self.include_sign:
                num_string = "+" + num_string[1:]
            else:
                num_string = num_string[1:]
        num_string = num_string.replace("-", "–")
        return num_string

    def init_data(self):
        super().init_data()
        self.data["font_size"] = np.array([self.font_size], dtype=float)

    def get_font_size(self):
        return self.data["font_size"][0]

    def string_to_mob(self, string, mob_class=Text):
        if string not in string_to_mob_map:
            string_to_mob_map[string] = mob_class(string, font_size=1)
        mob = string_to_mob_map[string].copy()
        mob.scale(self.get_font_size())
        return mob

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
        config = dict([
            (attr, getattr(self, attr))
            for attr in [
                "include_sign",
                "group_with_commas",
                "num_decimal_places",
            ]
        ])
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

    def set_value(self, number):
        move_to_point = self.get_edge_center(self.edge_to_fix)
        old_submobjects = list(self.submobjects)
        self.set_submobjects_from_number(number)
        self.move_to(move_to_point, self.edge_to_fix)
        for sm1, sm2 in zip(self.submobjects, old_submobjects):
            sm1.match_style(sm2)
        return self

    def _handle_scale_side_effects(self, scale_factor):
        self.data["font_size"] *= scale_factor

    def get_value(self):
        return self.number

    def increment_value(self, delta_t=1):
        self.set_value(self.get_value() + delta_t)


class Integer(DecimalNumber):
    CONFIG = {
        "num_decimal_places": 0,
    }

    def get_value(self):
        return int(np.round(super().get_value()))
