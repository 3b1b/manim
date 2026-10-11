from __future__ import annotations
from functools import lru_cache

import numpy as np

from manimlib.constants import DOWN, LEFT, RIGHT, UP
from manimlib.constants import DEFAULT_MOBJECT_COLOR
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.paths import straight_path
from manimlib.utils.bezier import interpolate

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar, Callable
    from manimlib.mobject.mobject import Mobject
    from manimlib.typing import ManimColor, Vect3, Self

    T = TypeVar("T", bound=VMobject)


@lru_cache()
def char_to_cahced_mob(char: str, **text_config):
    if "\\" in char or char == "i":
        # This is for when the "character" is a LaTeX command
        # like ^\circ or \dots
        return Tex(char, **text_config)
    else:
        return Text(char, **text_config)


class DecimalNumber(VMobject):
    """
    Display a numerical value as individually rendered characters.

    DecimalNumber is a VMobject that represents a real or complex
    number using Text-based character mobjects. It supports decimal
    precision, sign formatting, thousands separators, minimum
    field width, optional ellipses, units, and automatic value
    updates while preserving a chosen alignment edge.

    Parameters
    ----------
    number
        Initial real or complex number to display. Defaults to 0.
    color
        Color applied to the number. Defaults to DEFAULT_MOBJECT_COLOR.
    stroke_width
        Stroke width of the VMobject. Defaults to 0.
    fill_opacity
        Fill opacity of the rendered characters. Defaults to 1.0.
    fill_border_width
        Fill-border width passed to VMobject. Defaults to 0.5.
    num_decimal_places
        Number of decimal places for real-number formatting.
        If zero, floating-point values are converted to integers
        before formatting.
    min_total_width
        Optional minimum numeric field width. When truthy, it is
        included in the format specification to pad the number.
    include_sign
        Whether to include an explicit plus sign for non-negative
        values. Defaults to False.
    group_with_commas
        Whether to insert thousands separators. Defaults to True.
    digit_buff_per_font_unit
        Horizontal spacing factor between character mobjects,
        multiplied by the effective font size.
    show_ellipsis
        Whether to append a separate ellipsis mobject after the
        formatted number. Defaults to False.
    unit
        Optional text appended after the number. Units beginning
        with "^" are aligned to the top; other units are arranged
        with the characters and aligned to the bottom.
    include_background_rectangle
        Whether to add a background rectangle. Defaults to False.
    hide_zero_components_on_complex
        If True, suppress the zero real or imaginary component
        when the corresponding component is exactly zero.
    edge_to_fix
        Edge direction used to preserve the number's position
        when its value changes. Defaults to LEFT.
    font_size
        Effective font size used to scale the character mobjects.
        Defaults to 48.
    text_config
        Configuration passed to the Text mobjects created for
        characters. Do not pass font_size here; font size is
        managed separately by this class.
    **kwargs
        Additional keyword arguments forwarded to VMobject.

    Attributes
    ----------
    number
        Current real or complex numerical value.
    num_string
        Formatted string representation of the current value.
    num_decimal_places
        Configured decimal precision.
    include_sign
        Whether explicit positive signs are enabled.
    group_with_commas
        Whether thousands separators are enabled.
    min_total_width
        Minimum numeric field width, if configured.
    digit_buff_per_font_unit
        Character spacing factor.
    show_ellipsis
        Whether an ellipsis is appended.
    unit
        Optional unit string.
    include_background_rectangle
        Whether a background rectangle is requested.
    hide_zero_components_on_complex
        Whether zero components are suppressed in complex values.
    edge_to_fix
        Alignment edge preserved by set_value.
    font_size
        Effective font size used for character scaling.
    text_config
        Copy of the character Text configuration.

    Methods
    -------
    set_submobjects_from_number(number)
        Build or update character mobjects from a numerical value.
    get_num_string(number)
        Format a real or complex number as a string.
    char_to_mob(char)
        Create a Text mobject for a character or text fragment.
    get_font_size()
        Return the effective font size.
    get_formatter(**kwargs)
        Build a Python-style numeric format specification.
    get_complex_formatter(**kwargs)
        Build a format specification for complex numbers.
    get_tex()
        Return the formatted numeric string.
    set_value(number)
        Replace the displayed value while preserving the chosen edge.
    get_value()
        Return the current numerical value.
    increment_value(delta_t=1)
        Add a value to the current number.
    interpolate(mobject1, mobject2, alpha, path_func=straight_path)
        Interpolate between mobjects and update font-size metadata.
    _handle_scale_side_effects(scale_factor)
        Update font-size metadata when scaling.

    Notes
    -----
    - Each formatted character is represented by a Text mobject.
      Character mobjects are obtained through char_to_cahced_mob,
      allowing the implementation to reuse cached text objects.
    - When the number changes, existing submobjects are reused
      with become() if the character count stays the same.
      Otherwise, a new submobject list is constructed.
    - Character spacing is calculated as
      digit_buff_per_font_unit * effective_font_size.
    - A Unicode en dash replaces the ordinary minus sign in the
      displayed string.
    - Negative values that round to zero have their minus sign
      removed by default. If include_sign is True, that sign is
      replaced with a plus sign instead.
    - Complex-number components are hidden only when they are
      exactly zero, not merely close to zero.
    - Complex values are formatted using separate real and
      imaginary fields. The imaginary component always receives
      a sign when both components are displayed.
    - With num_decimal_places=0, the formatter uses integer
      formatting. This is intended for integer-like values.
    - set_value preserves the selected edge position and restores
      the style taken from the first family member with points.
    - increment_value updates the displayed value and returns
      the same DecimalNumber instance.
    - get_tex returns num_string; it does not generate a separate
      TeX expression.
    - text_config controls character rendering, while font_size
      controls the scaling applied to those character mobjects.

    Examples
    --------
    Display a basic decimal number::

        number = DecimalNumber(3.14159)

    Control decimal precision::

        number = DecimalNumber(
            3.14159,
            num_decimal_places=3,
        )

    Include a positive sign and thousands separators::

        number = DecimalNumber(
            12345.6,
            include_sign=True,
            group_with_commas=True,
        )

    Display a complex number::

        number = DecimalNumber(2 + 3j)

    Append a unit::

        number = DecimalNumber(9.81, unit="m/s")

    Update the displayed value::

        number = DecimalNumber(0)
        number.set_value(2.5)
        number.increment_value(1)

    Animate a ValueTracker's value::

        tracker = ValueTracker(0)
        number = DecimalNumber(tracker.get_value())
        number.add_updater(
            lambda mob: mob.set_value(tracker.get_value())
        )
        self.add(number)
        self.play(tracker.animate.set_value(10), run_time=2)

    See Also
    --------
    IntegerMatrix
        Matrix variant using DecimalNumber elements with zero
        decimal places by default.
    ValueTracker
        Stores a numerical value that can be animated.
    Tex
        Renders mathematical text using TeX.
    """

    def __init__(
        self,
        number: float | complex = 0,
        color: ManimColor = DEFAULT_MOBJECT_COLOR,
        stroke_width: float = 0,
        fill_opacity: float = 1.0,
        fill_border_width: float = 0.5,
        num_decimal_places: int = 2,
        min_total_width: Optional[int] = 0,
        include_sign: bool = False,
        group_with_commas: bool = True,
        digit_buff_per_font_unit: float = 0.001,
        show_ellipsis: bool = False,
        unit: str | None = None,  # Aligned to bottom unless it starts with "^"
        include_background_rectangle: bool = False,
        hide_zero_components_on_complex: bool = True,
        edge_to_fix: Vect3 = LEFT,
        font_size: float = 48,
        text_config: dict = dict(),  # Do not pass in font_size here
        **kwargs
    ):
        self.num_decimal_places = num_decimal_places
        self.include_sign = include_sign
        self.group_with_commas = group_with_commas
        self.min_total_width = min_total_width
        self.digit_buff_per_font_unit = digit_buff_per_font_unit
        self.show_ellipsis = show_ellipsis
        self.unit = unit
        self.include_background_rectangle = include_background_rectangle
        self.hide_zero_components_on_complex = hide_zero_components_on_complex
        self.edge_to_fix = edge_to_fix
        self.font_size = font_size
        self.text_config = dict(text_config)

        super().__init__(
            color=color,
            stroke_width=stroke_width,
            fill_opacity=fill_opacity,
            fill_border_width=fill_border_width,
            **kwargs
        )

        self.set_submobjects_from_number(number)
        self.init_colors()
        self.draw_fills_together_if_disjoint()

    def set_submobjects_from_number(self, number: float | complex) -> None:
        # Create the submobject list
        self.number = number
        self.num_string = self.get_num_string(number)

        # Submob_templates will be a list of cached Tex and Text mobjects,
        # with the intent of calling .copy or .become on them
        submob_templates = list(map(self.char_to_mob, self.num_string))
        if self.show_ellipsis:
            dots = self.char_to_mob("...")
            dots.arrange(RIGHT, buff=2 * dots[0].get_width())
            submob_templates.append(dots)
        if self.unit is not None:
            submob_templates.append(self.char_to_mob(self.unit))

        # Set internals
        font_size = self.get_font_size()
        if len(submob_templates) == len(self.submobjects):
            for sm, smt in zip(self.submobjects, submob_templates):
                sm.become(smt)
                sm.scale(font_size / smt.font_size)
        else:
            self.set_submobjects([
                smt.copy().scale(font_size / smt.font_size)
                for smt in submob_templates
            ])

        digit_buff = self.digit_buff_per_font_unit * font_size
        self.arrange(RIGHT, buff=digit_buff, aligned_edge=DOWN)

        # Handle alignment of special characters
        for i, c in enumerate(self.num_string):
            if c == "–" and len(self.num_string) > i + 1:
                self[i].align_to(self[i + 1], UP)
                self[i].shift(self[i + 1].get_height() * DOWN / 2)
            elif c == ",":
                self[i].shift(self[i].get_height() * DOWN / 2)
        if self.unit and self.unit.startswith("^"):
            self[-1].align_to(self, UP)

        if self.include_background_rectangle:
            self.add_background_rectangle()

    def get_num_string(self, number: float | complex) -> str:
        if isinstance(number, complex):
            if self.hide_zero_components_on_complex and number.imag == 0:
                number = number.real
                formatter = self.get_formatter()
            elif self.hide_zero_components_on_complex and number.real == 0:
                number = number.imag
                formatter = self.get_formatter() + "i"
            else:
                formatter = self.get_complex_formatter()
        else:
            formatter = self.get_formatter()
        if self.num_decimal_places == 0 and isinstance(number, float):
            number = int(number)
        num_string = formatter.format(number)

        rounded_num = np.round(number, self.num_decimal_places)
        if num_string.startswith("-") and rounded_num == 0:
            if self.include_sign:
                num_string = "+" + num_string[1:]
            else:
                num_string = num_string[1:]
        num_string = num_string.replace("-", "–")
        return num_string

    def char_to_mob(self, char: str) -> Text:
        return char_to_cahced_mob(char, **self.text_config)

    def interpolate(
        self,
        mobject1: Mobject,
        mobject2: Mobject,
        alpha: float,
        path_func: Callable[[np.ndarray, np.ndarray, float], np.ndarray] = straight_path
    ) -> Self:
        super().interpolate(mobject1, mobject2, alpha, path_func)
        if hasattr(mobject1, "font_size") and hasattr(mobject2, "font_size"):
            self.font_size = interpolate(mobject1.font_size, mobject2.font_size, alpha)

    def get_font_size(self) -> float:
        return self.font_size

    def get_formatter(self, **kwargs) -> str:
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
                "min_total_width",
            ]
        ])
        config.update(kwargs)
        ndp = config["num_decimal_places"]
        return "".join([
            "{",
            config.get("field_name", ""),
            ":",
            "+" if config["include_sign"] else "",
            "0" + str(config.get("min_total_width", "")) if config.get("min_total_width") else "",
            "," if config["group_with_commas"] else "",
            f".{ndp}f" if ndp > 0 else "d",
            "}",
        ])

    def get_complex_formatter(self, **kwargs) -> str:
        return "".join([
            self.get_formatter(field_name="0.real"),
            self.get_formatter(field_name="0.imag", include_sign=True),
            "i"
        ])

    def get_tex(self):
        return self.num_string

    def set_value(self, number: float | complex) -> Self:
        move_to_point = self.get_edge_center(self.edge_to_fix)
        style = self.family_members_with_points()[0].get_style()
        self.set_submobjects_from_number(number)
        self.move_to(move_to_point, self.edge_to_fix)
        self.set_style(**style)
        for submob in self.get_family():
            submob.uniforms.update(self.uniforms)
        # Digits are laid out in a row a buff apart, so they usually share a draw
        self.draw_fills_together_if_disjoint()
        return self

    def _handle_scale_side_effects(self, scale_factor: float) -> Self:
        self.font_size *= scale_factor
        return self

    def get_value(self) -> float | complex:
        return self.number

    def increment_value(self, delta_t: float | complex = 1) -> Self:
        self.set_value(self.get_value() + delta_t)
        return self


class Integer(DecimalNumber):
    """
    Display a numerical value as an integer.

    Integer subclasses DecimalNumber, defaulting to zero decimal
    places. Its get_value() method rounds the stored value to the
    nearest integer and returns it as a Python int.

    Parameters
    ----------
    number
        Initial numerical value. Defaults to 0.
    num_decimal_places
        Number of decimal places used for display. Defaults to 0,
        but can be overridden to display decimal places.
    **kwargs
        Additional keyword arguments forwarded to DecimalNumber.

    Methods
    -------
    get_value()
        Return the stored value rounded to the nearest integer,
        converted to a Python int.

    Notes
    -----
    - Integer does not enforce integer-only values internally.
      The inherited set_value() method can still store floats.
    - get_value() rounds the stored value using np.round before
      converting it to int. NumPy's rounding behavior applies,
      including ties-to-even for halfway values.
    - The displayed value is controlled by num_decimal_places;
      changing it does not change the rounding performed by
      get_value().
    - Methods inherited from DecimalNumber, including set_value()
      and increment_value(), remain available.

    Examples
    --------
    Create an integer display::

        number = Integer(5)

    Update the stored value::

        number.set_value(3.7)
        value = number.get_value()  # 4

    Display decimal places while retrieving an integer::

        number = Integer(2.8, num_decimal_places=2)
        value = number.get_value()  # 3

    See Also
    --------
    DecimalNumber
        Base class for formatting and displaying numerical values.
    """

    def __init__(
        self,
        number: int = 0,
        num_decimal_places: int = 0,
        **kwargs,
    ):
        super().__init__(number, num_decimal_places=num_decimal_places, **kwargs)

    def get_value(self) -> int:
        return int(np.round(super().get_value()))
