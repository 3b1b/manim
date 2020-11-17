"""Mobjects representing numbers."""

__all__ = ["DecimalNumber", "Integer", "Variable"]


from ..constants import *
from ..mobject.svg.tex_mobject import MathTex, SingleStringMathTex
from ..mobject.types.vectorized_mobject import VMobject
from ..mobject.value_tracker import ValueTracker


class DecimalNumber(VMobject):
    """An mobject representing a decimal number.

    Examples
    --------

    .. manim:: MovingSquareWithUpdaters

        class MovingSquareWithUpdaters(Scene):
            def construct(self):
                decimal = DecimalNumber(
                    0,
                    show_ellipsis=True,
                    num_decimal_places=3,
                    include_sign=True,
                )
                square = Square().to_edge(UP)

                decimal.add_updater(lambda d: d.next_to(square, RIGHT))
                decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
                self.add(square, decimal)
                self.play(
                    square.to_edge,
                    DOWN,
                    rate_func=there_and_back,
                    run_time=5,
                )
                self.wait()

    """

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

    def __init__(self, number=0, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.initial_config = kwargs

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

        self.add(*[SingleStringMathTex(char, **kwargs) for char in num_string])

        # Add non-numerical bits
        if self.show_ellipsis:
            self.add(SingleStringMathTex("\\dots"))

        if num_string.startswith("-"):
            minus = self.submobjects[0]
            minus.next_to(self.submobjects[1], LEFT, buff=self.digit_to_digit_buff)

        if self.unit is not None:
            self.unit_sign = SingleStringMathTex(self.unit, color=self.color)
            self.add(self.unit_sign)

        self.arrange(buff=self.digit_to_digit_buff, aligned_edge=DOWN)

        # Handle alignment of parts that should be aligned
        # to the bottom
        for i, c in enumerate(num_string):
            if c == "-" and len(num_string) > i + 1:
                self[i].align_to(self[i + 1], UP)
                self[i].shift(self[i + 1].get_height() * DOWN / 2)
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
        config = dict(
            [
                (attr, getattr(self, attr))
                for attr in [
                    "include_sign",
                    "group_with_commas",
                    "num_decimal_places",
                ]
            ]
        )
        config.update(kwargs)
        return "".join(
            [
                "{",
                config.get("field_name", ""),
                ":",
                "+" if config["include_sign"] else "",
                "," if config["group_with_commas"] else "",
                ".",
                str(config["num_decimal_places"]),
                "f",
                "}",
            ]
        )

    def get_complex_formatter(self, **kwargs):
        return "".join(
            [
                self.get_formatter(field_name="0.real"),
                self.get_formatter(field_name="0.imag", include_sign=True),
                "i",
            ]
        )

    def set_value(self, number, **config):
        full_config = dict(self.CONFIG)
        full_config.update(self.initial_config)
        full_config.update(config)
        new_decimal = DecimalNumber(number, **full_config)
        # Make sure last digit has constant height
        new_decimal.scale(self[-1].get_height() / new_decimal[-1].get_height())
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

    def increment_value(self, delta_t=1):
        self.set_value(self.get_value() + delta_t)


class Integer(DecimalNumber):
    CONFIG = {
        "num_decimal_places": 0,
    }

    def get_value(self):
        return int(np.round(super().get_value()))


class Variable(VMobject):
    """A class for displaying text that continuously updates to reflect the value of a python variable.

    Automatically adds the text for the label and the value when instantiated and added to the screen.

    Parameters
    ----------
    var : Union[:class:`int`, :class:`float`]
        The python variable you need to keep track of and display.
    label : Union[:class:`str`, :class:`~.Tex`, :class:`~.MathTex`, :class:`~.Text`, :class:`~.TexSymbol`, :class:`~.SingleStringMathTex`, :class:`~.MathTexFromPresetString`]
        The label for your variable, for example ``x = ...``. To use math mode, for e.g.
        subscripts, superscripts, etc. simply pass in a raw string.
    var_type : Union[:class:`DecimalNumber`, :class:`Integer`], optional
        The class used for displaying the number. Defaults to :class:`DecimalNumber`.
    num_decimal_places : :class:`int`, optional
        The number of decimal places to display in your variable. Defaults to 2.
        If `var_type` is an :class:`Integer`, this parameter is ignored.
    kwargs : Any
            Other arguments to be passed to `~.Mobject`.

    Attributes
    ----------
    label : Union[:class:`str`, :class:`~.Tex`, :class:`~.MathTex`, :class:`~.Text`, :class:`~.TexSymbol`, :class:`~.SingleStringMathTex`, :class:`~.MathTexFromPresetString`]
        The label for your variable, for example ``x = ...``.
    tracker : :class:`~.ValueTracker`
        Useful in updating the value of your variable on-screen.
    value : Union[:class:`DecimalNumber`, :class:`Integer`]
        The tex for the value of your variable.

    Examples
    --------
    Normal usage::

        # DecimalNumber type
        var = 0.5
        on_screen_var = Variable(var, Text("var"), num_decimal_places=3)
        # Integer type
        int_var = 0
        on_screen_int_var = Variable(int_var, Text("int_var"), var_type=Integer)
        # Using math mode for the label
        on_screen_int_var = Variable(int_var, "{a}_{i}", var_type=Integer)

    .. manim:: VariablesWithValueTracker

        class VariablesWithValueTracker(Scene):
            def construct(self):
                var = 0.5
                on_screen_var = Variable(var, Text("var"), num_decimal_places=3)

                # You can also change the colours for the label and value
                on_screen_var.label.set_color(RED)
                on_screen_var.value.set_color(GREEN)

                self.play(Write(on_screen_var))
                # The above line will just display the variable with
                # its initial value on the screen. If you also wish to
                # update it, you can do so by accessing the `tracker` attribute
                self.wait()
                var_tracker = on_screen_var.tracker
                var = 10.5
                self.play(var_tracker.set_value, var)
                self.wait()

                int_var = 0
                on_screen_int_var = Variable(
                    int_var, Text("int_var"), var_type=Integer
                ).next_to(on_screen_var, DOWN)
                on_screen_int_var.label.set_color(RED)
                on_screen_int_var.value.set_color(GREEN)

                self.play(Write(on_screen_int_var))
                self.wait()
                var_tracker = on_screen_int_var.tracker
                var = 10.5
                self.play(var_tracker.set_value, var)
                self.wait()

                # If you wish to have a somewhat more complicated label for your
                # variable with subscripts, superscripts, etc. the default class
                # for the label is MathTex
                subscript_label_var = 10
                on_screen_subscript_var = Variable(subscript_label_var, "{a}_{i}").next_to(
                    on_screen_int_var, DOWN
                )
                self.play(Write(on_screen_subscript_var))
                self.wait()

    """

    def __init__(
        self, var, label, var_type=DecimalNumber, num_decimal_places=2, **kwargs
    ):

        self.label = MathTex(label) if isinstance(label, str) else label
        equals = MathTex("=").next_to(self.label, RIGHT)
        self.label.add(equals)

        self.tracker = ValueTracker(var)

        if var_type == DecimalNumber:
            self.value = DecimalNumber(
                self.tracker.get_value(), num_decimal_places=num_decimal_places
            )
        elif var_type == Integer:
            self.value = Integer(self.tracker.get_value())

        self.value.add_updater(lambda v: v.set_value(self.tracker.get_value())).next_to(
            self.label, RIGHT
        )

        VMobject.__init__(self, **kwargs)
        self.add(self.label, self.value)
