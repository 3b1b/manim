from __future__ import annotations

import numpy as np

from manimlib.constants import DOWN, LEFT, RIGHT, UP
from manimlib.constants import DEFAULT_LIGHT_COLOR
from manimlib.constants import MED_SMALL_BUFF, SMALL_BUFF
from manimlib.constants import YELLOW, DEG
from manimlib.mobject.geometry import Line, ArrowTip
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.value_tracker import ValueTracker
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import outer_interpolate
from manimlib.utils.dict_ops import merge_dicts_recursively
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.space_ops import rotate_vector, angle_of_vector

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Optional, Tuple, Dict, Any
    from manimlib.typing import ManimColor, Vect3, Vect3Array, VectN, RangeSpecifier


class NumberLine(Line):
    """
    A one-dimensional number line with configurable ticks, labels,
    and an optional tip.

    NumberLine represents a numerical interval as a geometric line.
    It provides conversions between numerical values and points in
    space, making it useful for plotting values, positioning objects,
    and creating number-line visualizations.

    Parameters
    ----------
    x_range
        Numerical range specified as (x_min, x_max) or
        (x_min, x_max, step). Defaults to (-8, 8, 1).
        The first two values define the numerical interval, while
        the optional third value determines tick spacing and the
        default spacing of number labels.

    color
        Color of the number line and its tick marks.
        Defaults to DEFAULT_LIGHT_COLOR.

    stroke_width
        Stroke width of the line. Tick marks inherit the line's
        style when created.

    unit_size
        Geometric distance corresponding to one numerical unit.
        Applied by scaling the line when width is not provided.

    width
        Optional total geometric width of the line. When provided
        and truthy, it takes precedence over unit_size.

    include_ticks
        Whether to create and add tick marks during initialization.

    tick_size
        Half-length parameter used to construct each tick.
        A tick extends by this amount in both directions before
        being rotated to match the line's angle.

    longer_tick_multiple
        Multiplier applied to tick_size for values listed in
        big_tick_numbers.

    tick_offset
        Stored as an attribute but not used by the shown
        implementation to position tick marks.

    big_tick_spacing
        Optional spacing used to generate big_tick_numbers
        across the numerical range. When provided, it takes
        precedence over the explicit big_tick_numbers list.

    big_tick_numbers
        Numerical values whose ticks should be longer.
        Defaults to an empty list.

    include_numbers
        Whether to add numerical labels during initialization.

    line_to_number_direction
        Direction in which number labels are placed relative
        to their corresponding points. Defaults to DOWN.

    line_to_number_buff
        Distance between the line and its number labels.
        Defaults to MED_SMALL_BUFF.

    include_tip
        Whether to add a tip to the line. When enabled, the tip
        inherits the line's stroke color and stroke width.

    tip_config
        Configuration dictionary copied and stored for the tip.
        Defaults to a width and length of 0.25 each.

    decimal_number_config
        Default configuration for DecimalNumber labels.
        Defaults to zero decimal places and font size 36.

    numbers_to_exclude
        Optional list of values to omit when automatically
        generating number labels.

    **kwargs
        Additional keyword arguments forwarded to Line.

    Attributes
    ----------
    x_range
        Original numerical range specification.
    x_min, x_max
        Lower and upper numerical bounds.
    x_step
        Tick spacing, taken from x_range or defaulting to 1.
    tick_size
        Base tick size.
    longer_tick_multiple
        Scale factor for longer ticks.
    tick_offset
        Stored tick offset value; unused by the shown methods.
    big_tick_numbers
        Values whose tick marks are longer.
    line_to_number_direction
        Default label direction.
    line_to_number_buff
        Default label spacing.
    include_tip
        Whether a tip was requested.
    tip_config
        Copy of the supplied tip configuration.
    decimal_number_config
        Copy of the default decimal-label configuration.
    numbers_to_exclude
        Values excluded from automatically generated labels.
    ticks
        VGroup of tick marks, created when add_ticks is called.
    numbers
        VGroup of numerical labels, created when add_numbers
        is called.

    Methods
    -------
    get_tick_range()
        Return numerical values at which ticks should be placed.
    add_ticks()
        Create and add tick marks to the line.
    get_tick(x, size=None)
        Create a single tick at a numerical value.
    get_tick_marks()
        Return the stored tick-mark group.
    number_to_point(number)
        Convert numerical values into points on the line.
    point_to_number(point)
        Project points onto the line and convert their positions
        into numerical values.
    n2p(number)
        Abbreviation for number_to_point.
    p2n(point)
        Abbreviation for point_to_number.
    get_unit_size()
        Return geometric length per numerical unit.
    get_number_mobject(x, ...)
        Create a DecimalNumber label for a value.
    add_numbers(x_values=None, ...)
        Create and add numerical labels.

    Notes
    -----
    - The line is initially constructed from x_min * RIGHT to
      x_max * RIGHT, then scaled or resized and centered.
    - If width is truthy, set_width(width) is used; otherwise,
      the line is scaled by unit_size.
    - Tick marks are positioned using number_to_point, so they
      follow the line's current geometric position and direction.
    - Values in big_tick_numbers receive longer ticks according
      to longer_tick_multiple.
    - When big_tick_spacing is supplied, big tick values are
      generated with numpy.arange, starting at x_min.
    - get_tick_range excludes x_max when include_tip is True,
      and can include x_max when include_tip is False, provided
      the step lands on that endpoint.
    - number_to_point maps values linearly across the numerical
      interval. Values outside the interval extrapolate beyond
      the endpoints rather than being clamped.
    - point_to_number uses projection onto the line's direction.
      A point need not lie exactly on the line to produce a value.
    - get_unit_size measures the current geometric line length
      divided by the numerical interval. It can differ from the
      original unit_size after subsequent transformations.
    - add_numbers defaults to get_tick_range. Its excluding
      argument uses ordinary value membership, not approximate
      floating-point comparison.
    - decimal_number_config supplies default label settings.
      Additional keyword arguments passed to get_number_mobject
      are recursively merged with those defaults.
    - tick_offset is stored but does not affect tick placement
      in the implementation shown here.

    Examples
    --------
    Create a basic number line::

        number_line = NumberLine()

    Create a number line with custom bounds and tick spacing::

        number_line = NumberLine(
            x_range=(-5, 5, 0.5),
            unit_size=0.8,
            include_ticks=True,
        )

    Highlight selected tick values::

        number_line = NumberLine(
            x_range=(-4, 4, 1),
            big_tick_numbers=[-4, 0, 4],
            longer_tick_multiple=2,
        )

    Add number labels while excluding zero::

        number_line = NumberLine(
            x_range=(-5, 5, 1),
            include_numbers=True,
            numbers_to_exclude=[0],
        )

    Convert a number into a point in space::

        number_line = NumberLine()
        point = number_line.number_to_point(3)
        dot = Dot(point)

    Use the shorthand conversion methods::

        point = number_line.n2p(2)
        value = number_line.p2n(point)

    Add labels later with custom formatting::

        number_line = NumberLine(include_numbers=False)
        labels = number_line.add_numbers(
            x_values=[-2, 0, 2],
            font_size=30,
        )

    See Also
    --------
    Axes
        Coordinate axes for two-dimensional plots.
    NumberPlane
        A plane with coordinate grid lines.
    DecimalNumber
        Numerical labels used by the number line.
    Line
        The geometric line class from which NumberLine inherits.
    """

    def __init__(
        self,
        x_range: RangeSpecifier = (-8, 8, 1),
        color: ManimColor = DEFAULT_LIGHT_COLOR,
        stroke_width: float = 2.0,
        # How big is one one unit of this number line in terms of absolute spacial distance
        unit_size: float = 1.0,
        width: Optional[float] = None,
        include_ticks: bool = True,
        tick_size: float = 0.1,
        longer_tick_multiple: float = 1.5,
        tick_offset: float = 0.0,
        # Change name
        big_tick_spacing: Optional[float] = None,
        big_tick_numbers: list[float] = [],
        include_numbers: bool = False,
        line_to_number_direction: Vect3 = DOWN,
        line_to_number_buff: float = MED_SMALL_BUFF,
        include_tip: bool = False,
        tip_config: dict = dict(
            width=0.25,
            length=0.25,
        ),
        decimal_number_config: dict = dict(
            num_decimal_places=0,
            font_size=36,
        ),
        numbers_to_exclude: list | None = None,
        **kwargs,
    ):
        self.x_range = x_range
        self.tick_size = tick_size
        self.longer_tick_multiple = longer_tick_multiple
        self.tick_offset = tick_offset
        if big_tick_spacing is not None:
            self.big_tick_numbers = np.arange(
                x_range[0],
                x_range[1] + big_tick_spacing,
                big_tick_spacing,
            )
        else:
            self.big_tick_numbers = list(big_tick_numbers)
        self.line_to_number_direction = line_to_number_direction
        self.line_to_number_buff = line_to_number_buff
        self.include_tip = include_tip
        self.tip_config = dict(tip_config)
        self.decimal_number_config = dict(decimal_number_config)
        self.numbers_to_exclude = numbers_to_exclude

        self.x_min, self.x_max = x_range[:2]
        self.x_step = 1 if len(x_range) == 2 else x_range[2]

        super().__init__(
            self.x_min * RIGHT, self.x_max * RIGHT,
            color=color,
            stroke_width=stroke_width,
            **kwargs
        )

        if width:
            self.set_width(width)
        else:
            self.scale(unit_size)
        self.center()

        if include_tip:
            self.add_tip()
            self.tip.set_stroke(
                self.stroke_color,
                self.stroke_width,
            )
        if include_ticks:
            self.add_ticks()
        if include_numbers:
            self.add_numbers(excluding=self.numbers_to_exclude)

    def get_tick_range(self) -> np.ndarray:
        if self.include_tip:
            x_max = self.x_max
        else:
            x_max = self.x_max + self.x_step
        result = np.arange(self.x_min, x_max, self.x_step)
        return result[result <= self.x_max]

    def add_ticks(self) -> None:
        ticks = VGroup()
        for x in self.get_tick_range():
            size = self.tick_size
            if np.isclose(self.big_tick_numbers, x).any():
                size *= self.longer_tick_multiple
            ticks.add(self.get_tick(x, size))
        self.add(ticks)
        self.ticks = ticks

    def get_tick(self, x: float, size: float | None = None) -> Line:
        if size is None:
            size = self.tick_size
        result = Line(size * DOWN, size * UP)
        result.rotate(self.get_angle())
        result.move_to(self.number_to_point(x))
        result.match_style(self)
        return result

    def get_tick_marks(self) -> VGroup:
        return self.ticks

    def number_to_point(self, number: float | VectN) -> Vect3 | Vect3Array:
        start = self.get_points()[0]
        end = self.get_points()[-1]
        alpha = (number - self.x_min) / (self.x_max - self.x_min)
        return outer_interpolate(start, end, alpha)

    def point_to_number(self, point: Vect3 | Vect3Array) -> float | VectN:
        start = self.get_points()[0]
        end = self.get_points()[-1]
        vect = end - start
        proportion = fdiv(
            np.dot(point - start, vect),
            np.dot(end - start, vect),
        )
        return interpolate(self.x_min, self.x_max, proportion)

    def n2p(self, number: float | VectN) -> Vect3 | Vect3Array:
        """Abbreviation for number_to_point"""
        return self.number_to_point(number)

    def p2n(self, point: Vect3 | Vect3Array) -> float | VectN:
        """Abbreviation for point_to_number"""
        return self.point_to_number(point)

    def get_unit_size(self) -> float:
        return self.get_length() / (self.x_max - self.x_min)

    def get_number_mobject(
        self,
        x: float,
        direction: Vect3 | None = None,
        buff: float | None = None,
        unit: float = 1.0,
        unit_tex: str = "",
        **number_config
    ) -> DecimalNumber:
        number_config = merge_dicts_recursively(
            self.decimal_number_config, number_config,
        )
        if direction is None:
            direction = self.line_to_number_direction
        if buff is None:
            buff = self.line_to_number_buff
        if unit_tex:
            number_config["unit"] = unit_tex

        num_mob = DecimalNumber(x / unit, **number_config)
        num_mob.next_to(
            self.number_to_point(x),
            direction=direction,
            buff=buff
        )
        if x < 0 and direction[0] == 0:
            # Align without the minus sign
            num_mob.shift(num_mob[0].get_width() * LEFT / 2)
        if abs(x) == unit and unit_tex:
            center = num_mob.get_center()
            if x > 0:
                num_mob.remove(num_mob[0])
            else:
                num_mob.remove(num_mob[1])
                num_mob[0].next_to(num_mob[1], LEFT, buff=num_mob[0].get_width() / 4)
            num_mob.move_to(center)
        return num_mob

    def add_numbers(
        self,
        x_values: Iterable[float] | None = None,
        excluding: Iterable[float] | None = None,
        font_size: int = 24,
        **kwargs
    ) -> VGroup:
        if x_values is None:
            x_values = self.get_tick_range()

        kwargs["font_size"] = font_size

        if excluding is None:
            excluding = self.numbers_to_exclude

        numbers = VGroup()
        for x in x_values:
            if excluding is not None and x in excluding:
                continue
            numbers.add(self.get_number_mobject(x, **kwargs))
        # Labels typically don't overlap, and hence can be drawn together
        numbers.draw_fills_together_if_disjoint()
        self.add(numbers)
        self.numbers = numbers
        return numbers


class UnitInterval(NumberLine):
    """
    A specialized NumberLine for representing the unit interval.

    UnitInterval inherits from NumberLine and provides defaults
    for the interval [0, 1], with closely spaced ticks and longer
    ticks at the endpoints. It is useful for visualizing normalized
    values, proportions, and parameters between zero and one.

    Parameters
    ----------
    x_range
        Numerical range specified as (x_min, x_max) or
        (x_min, x_max, step). Defaults to (0, 1, 0.1).
    unit_size
        Geometric distance corresponding to one numerical unit.
        Defaults to 10, making the default interval relatively wide.
    big_tick_numbers
        Values whose tick marks should be longer.
        Defaults to [0, 1].
    decimal_number_config
        Configuration dictionary for DecimalNumber labels.
        Defaults to one decimal place.
    **kwargs
        Additional keyword arguments forwarded to NumberLine.

    Notes
    -----
    - All supplied parameters are forwarded to NumberLine.
    - The default interval has tick spacing of 0.1 and longer
      ticks at both endpoints.
    - The default unit_size is 10, but the final geometric size
      may be affected by other inherited options such as width.
    - Features such as tick marks, number labels, and line tips
      follow the behavior and defaults of NumberLine.

    Examples
    --------
    Create a default unit interval::

        interval = UnitInterval()

    Customize the tick spacing::

        interval = UnitInterval(
            x_range=(0, 1, 0.2),
            big_tick_numbers=[0, 0.5, 1],
        )

    Display numerical labels::

        interval = UnitInterval(
            include_numbers=True,
            numbers_to_exclude=[0.5],
        )

    Convert a normalized value to a point::

        interval = UnitInterval()
        point = interval.number_to_point(0.75)

    See Also
    --------
    NumberLine
        Parent class providing tick, label, and coordinate methods.
    Axes
        Coordinate axes for plotting functions.
    """

    def __init__(
        self,
        x_range: RangeSpecifier = (0, 1, 0.1),
        unit_size: float = 10,
        big_tick_numbers: list[float] = [0, 1],
        decimal_number_config: dict = dict(
            num_decimal_places=1,
        ),
        **kwargs
    ):
        super().__init__(
            x_range=x_range,
            unit_size=unit_size,
            big_tick_numbers=big_tick_numbers,
            decimal_number_config=decimal_number_config,
            **kwargs
        )


class Slider(VGroup):
    """
    A labeled slider controlled by a ValueTracker.

    Slider combines a NumberLine, a movable ArrowTip, and a
    numeric label that updates automatically as the associated
    ValueTracker changes. It can be used to visualize a changing
    parameter in an animation or interactive mathematical scene.

    Parameters
    ----------
    value_tracker
        ValueTracker supplying the slider's current numerical value.
        Its value determines the arrow tip's position and the
        displayed numeric label.
    x_range
        Minimum and maximum values of the number line.
        Defaults to (-5, 5).
    var_name
        Optional variable name displayed before the value,
        such as ``x = 2.50``. If None, only the value is shown.
    width
        Geometric width of the number line. Defaults to 3.
    unit_size
        Accepted by the signature but not directly used in this
        implementation. The number line is configured using width.
    arrow_width
        Width passed to ArrowTip. Defaults to 0.15.
    arrow_length
        Length passed to ArrowTip. Defaults to 0.15.
    arrow_color
        Color of the arrow tip and the variable-name portion
        of the label. Defaults to YELLOW.
    font_size
        Font size of the main label. Defaults to 24.
    label_buff
        Spacing between the arrow tip and the label.
        Defaults to SMALL_BUFF.
    num_decimal_places
        Number of decimal places shown in the changing value.
        Defaults to 2.
    tick_size
        Tick size passed to NumberLine. Defaults to 0.05.
    number_line_config
        Additional configuration for NumberLine. These values
        override the default x_range, width, and tick_size
        settings when keys overlap.
    arrow_tip_config
        Additional ArrowTip configuration. These values override
        the default arrow-tip settings when keys overlap.
    decimal_config
        Accepted by the signature but not used in this
        implementation.
    angle
        Rotation angle of the number line, in radians.
        Defaults to 0.
    label_direction
        Direction vector used to position the main label and
        orient the arrow tip. If None, it is computed by rotating
        UP by angle and rounding the resulting vector to two
        decimal places.
    add_tick_labels
        Whether to add numerical labels to the number line.
        Defaults to True.
    tick_label_font_size
        Font size of the number-line tick labels. Defaults to 16.

    Attributes
    ----------
    number_line
        NumberLine created as the slider's first submobject.
    tip
        ArrowTip that tracks the ValueTracker's value.
    label
        Tex label containing the optional variable name and value.

    Notes
    -----
    - The slider consists of three submobjects: the number line,
      the arrow tip, and the main label.
    - The arrow tip moves to the point corresponding to the
      current ValueTracker value whenever its updater runs.
    - The displayed numeric value is updated through a
      changeable Tex number and an updater.
    - The main label is repositioned relative to the arrow tip
      on every update.
    - Values outside x_range are not explicitly clamped by
      Slider; NumberLine's coordinate conversion determines
      the resulting position.
    - number_line_config can override the initial range, width,
      and tick size because it is merged after their defaults.
    - arrow_tip_config can override the initial tip configuration.
    - unit_size and decimal_config are present in the signature
      but are not used by the shown implementation.
    - The variable name is passed to label[var_name].set_fill.
      Therefore, var_name should correspond to a valid subobject
      selector in the generated Tex expression.

    Examples
    --------
    Create a slider controlled by a ValueTracker::

        tracker = ValueTracker(0)
        slider = Slider(tracker)

    Display a named parameter::

        tracker = ValueTracker(2.5)
        slider = Slider(tracker, var_name="x")

    Rotate the slider and position its label accordingly::

        tracker = ValueTracker(1)
        slider = Slider(
            tracker,
            angle=PI / 4,
            var_name="t",
        )

    Customize the number line and tick labels::

        tracker = ValueTracker(0)
        slider = Slider(
            tracker,
            x_range=(-2, 2),
            width=5,
            add_tick_labels=True,
            tick_label_font_size=20,
        )

    Animate the tracked value in a scene::

        tracker = ValueTracker(-3)
        slider = Slider(tracker, var_name="x")
        self.add(slider)
        self.play(tracker.animate.set_value(4), run_time=3)

    See Also
    --------
    ValueTracker
        Stores a numerical value that can be animated.
    NumberLine
        Provides the geometric scale and tick labels.
    ArrowTip
        Supplies the slider's movable indicator.
    """

    def __init__(
        self,
        value_tracker: ValueTracker,
        x_range: Tuple[float, float] = (-5, 5),
        var_name: Optional[str] = None,
        width: float = 3,
        unit_size: float = 1,
        arrow_width: float = 0.15,
        arrow_length: float = 0.15,
        arrow_color: ManimColor = YELLOW,
        font_size: int = 24,
        label_buff: float = SMALL_BUFF,
        num_decimal_places: int = 2,
        tick_size: float = 0.05,
        number_line_config: Dict[str, Any] = dict(),
        arrow_tip_config: Dict[str, Any] = dict(),
        decimal_config: Dict[str, Any] = dict(),
        angle: float = 0,
        label_direction: Optional[np.ndarray] = None,
        add_tick_labels: bool = True,
        tick_label_font_size: int = 16,
    ):
        get_value = value_tracker.get_value
        if label_direction is None:
            label_direction = np.round(rotate_vector(UP, angle), 2)

        # Initialize number line
        number_line_kw = dict(x_range=x_range, width=width, tick_size=tick_size)
        number_line_kw.update(number_line_config)
        number_line = NumberLine(**number_line_kw)
        number_line.rotate(angle)
        if add_tick_labels:
            number_line.add_numbers(
                font_size=tick_label_font_size,
                buff=2 * tick_size,
                direction=-label_direction
            )

        # Initialize arrow tip
        arrow_tip_kw = dict(
            width=arrow_width,
            length=arrow_length,
            fill_color=arrow_color,
            angle=-180 * DEG + angle_of_vector(label_direction),
        )
        arrow_tip_kw.update(arrow_tip_config)
        tip = ArrowTip(**arrow_tip_kw)
        tip.add_updater(lambda m: m.move_to(number_line.n2p(get_value()), -label_direction))

        # Initialize label
        dec_string = f"{{:.{num_decimal_places}f}}".format(0)
        lhs = f"{var_name} = " if var_name is not None else ""
        label = Tex(lhs + dec_string, font_size=font_size)
        label[var_name].set_fill(arrow_color)
        decimal = label.make_number_changeable(dec_string)
        decimal.add_updater(lambda m: m.set_value(get_value()))
        label.add_updater(lambda m: m.next_to(tip, label_direction, label_buff))

        # Assemble group
        super().__init__(number_line, tip, label)
        self.set_stroke(behind=True)
