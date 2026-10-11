from __future__ import annotations

import numpy as np

from manimlib.constants import BLUE, BLUE_E, GREEN_E, GREY_B, GREY_D, MAROON_B, YELLOW
from manimlib.constants import DOWN, LEFT, RIGHT, UP
from manimlib.constants import MED_LARGE_BUFF, MED_SMALL_BUFF, SMALL_BUFF
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.svg.brace import Brace
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.tex_mobject import TexText
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.color import color_gradient
from manimlib.utils.iterables import listify

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable
    from manimlib.typing import ManimColor


EPSILON = 0.0001


class SampleSpace(Rectangle):
    """
    Represent a sample space as a rectangle that can be divided
    into probability regions with optional braces and labels.

    SampleSpace extends Rectangle with helpers for dividing its
    area according to a list of proportions. It is useful for
    visualizing sample spaces, probability distributions, and
    conditional probability diagrams.

    Parameters
    ----------
    width
        Width of the sample-space rectangle. Defaults to 3.
    height
        Height of the rectangle. Defaults to 3.
    fill_color
        Initial fill color. Defaults to GREY_D.
    fill_opacity
        Initial fill opacity. Defaults to 1.
    stroke_width
        Width of the rectangle's outline. Defaults to 0.5.
    stroke_color
        Color of the outline. Defaults to GREY_B.
    default_label_scale_val
        Scale factor applied to labels created from strings.
        Defaults to 1.
    **kwargs
        Additional keyword arguments forwarded to Rectangle.

    Attributes
    ----------
    default_label_scale_val
        Default scale factor for generated labels.
    title
        Title mobject created by add_title(), if called.
    label
        Value assigned by add_label(), if called.
    horizontal_parts
        Regions created by divide_horizontally(), if called.
    vertical_parts
        Regions created by divide_vertically(), if called.

    Methods
    -------
    add_title(title="Sample space", buff=MED_SMALL_BUFF)
        Create and add a title above the rectangle.
    add_label(label)
        Store a label value on the instance.
    complete_p_list(p_list)
        Convert proportions to a list and append the remainder
        needed to make their sum equal to one, when significant.
    get_division_along_dimension(p_list, dim, colors, vect)
        Create colored subdivisions along a chosen dimension.
    get_horizontal_division(p_list, colors, vect)
        Create horizontal strips representing proportions.
    get_vertical_division(p_list, colors, vect)
        Create vertical strips representing proportions.
    divide_horizontally(*args, **kwargs)
        Create, store, and add horizontal subdivisions.
    divide_vertically(*args, **kwargs)
        Create, store, and add vertical subdivisions.
    get_subdivision_braces_and_labels(parts, labels, direction, buff)
        Create braces and labels for a group of subdivisions.
    get_side_braces_and_labels(labels, direction=LEFT, **kwargs)
        Create braces and labels beside horizontal subdivisions.
    get_top_braces_and_labels(labels, **kwargs)
        Create braces and labels above vertical subdivisions.
    get_bottom_braces_and_labels(labels, **kwargs)
        Create braces and labels below vertical subdivisions.
    add_braces_and_labels()
        Add stored braces and labels for existing subdivisions.
    __getitem__(index)
        Index the preferred subdivision group, or the result of
        split() if no subdivisions have been created.

    Notes
    -----
    - complete_p_list() appends the remaining probability mass
      only when its absolute value exceeds EPSILON. It does not
      normalize the supplied probabilities.
    - If the supplied proportions sum to more than one, the
      remainder can be negative. Proportions are not validated.
    - get_division_along_dimension() creates fresh SampleSpace
      objects, stretches them to match the original rectangle,
      and then scales each region along the selected dimension.
    - The colors are interpolated with color_gradient() to match
      the number of proportions.
    - The direction vector determines the side from which the
      subdivision begins and the direction in which it proceeds.
    - Labels passed as strings are iterated character by character.
      To use multi-character labels, pass a suitable sequence or
      prebuilt Mobject labels as appropriate.
    - Prebuilt Mobject labels are used directly and are not scaled
      by default_label_scale_val.
    - Subdivision braces and labels are stored as attributes on
      the parts VGroup. add_braces_and_labels() adds them to the
      SampleSpace only if those attributes exist.
    - __getitem__ prefers horizontal_parts whenever available;
      otherwise it uses vertical_parts, and falls back to split()
      when neither subdivision group exists.
    - Calling divide_horizontally() or divide_vertically() again
      replaces the corresponding stored group, but does not
      explicitly remove the previous group from the rectangle.

    Examples
    --------
    Create a sample space::

        sample_space = SampleSpace()

    Divide it into horizontal regions::

        sample_space.divide_horizontally(
            [0.3, 0.7],
            colors=[GREEN_E, BLUE_E],
        )

    Divide it into vertical regions::

        sample_space.divide_vertically(
            [0.4, 0.6],
            colors=[MAROON_B, YELLOW],
        )

    Add a title and subdivision labels::

        sample_space = SampleSpace()
        sample_space.add_title("Possible outcomes")
        sample_space.divide_horizontally([0.25, 0.75])
        braces_labels = sample_space.get_side_braces_and_labels(
            ["A", "B"]
        )
        sample_space.add_braces_and_labels()

    Access a subdivision::

        first_region = sample_space[0]

    See Also
    --------
    Rectangle
        Base rectangular geometry.
    Brace
        Adds a brace alongside a region.
    VGroup
        Groups subdivision regions, braces, and labels.
    """

    def __init__(
        self,
        width: float = 3,
        height: float = 3,
        fill_color: ManimColor = GREY_D,
        fill_opacity: float = 1,
        stroke_width: float = 0.5,
        stroke_color: ManimColor = GREY_B,
        default_label_scale_val: float = 1,
        **kwargs,
    ):
        super().__init__(
            width, height,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            **kwargs
        )
        self.default_label_scale_val = default_label_scale_val

    def add_title(
        self,
        title: str = "Sample space",
        buff: float = MED_SMALL_BUFF
    ) -> None:
        # TODO, should this really exist in SampleSpaceScene
        title_mob = TexText(title)
        if title_mob.get_width() > self.get_width():
            title_mob.set_width(self.get_width())
        title_mob.next_to(self, UP, buff=buff)
        self.title = title_mob
        self.add(title_mob)

    def add_label(self, label: str) -> None:
        self.label = label

    def complete_p_list(self, p_list: list[float]) -> list[float]:
        new_p_list = listify(p_list)
        remainder = 1.0 - sum(new_p_list)
        if abs(remainder) > EPSILON:
            new_p_list.append(remainder)
        return new_p_list

    def get_division_along_dimension(
        self,
        p_list: list[float],
        dim: int,
        colors: Iterable[ManimColor],
        vect: np.ndarray
    ) -> VGroup:
        p_list = self.complete_p_list(p_list)
        colors = color_gradient(colors, len(p_list))

        last_point = self.get_edge_center(-vect)
        parts = VGroup()
        for factor, color in zip(p_list, colors):
            part = SampleSpace()
            part.set_fill(color, 1)
            part.replace(self, stretch=True)
            part.stretch(factor, dim)
            part.move_to(last_point, -vect)
            last_point = part.get_edge_center(vect)
            parts.add(part)
        return parts

    def get_horizontal_division(
        self,
        p_list: list[float],
        colors: Iterable[ManimColor] = [GREEN_E, BLUE_E],
        vect: np.ndarray = DOWN
    ) -> VGroup:
        return self.get_division_along_dimension(p_list, 1, colors, vect)

    def get_vertical_division(
        self,
        p_list: list[float],
        colors: Iterable[ManimColor] = [MAROON_B, YELLOW],
        vect: np.ndarray = RIGHT
    ) -> VGroup:
        return self.get_division_along_dimension(p_list, 0, colors, vect)

    def divide_horizontally(self, *args, **kwargs) -> None:
        self.horizontal_parts = self.get_horizontal_division(*args, **kwargs)
        self.add(self.horizontal_parts)

    def divide_vertically(self, *args, **kwargs) -> None:
        self.vertical_parts = self.get_vertical_division(*args, **kwargs)
        self.add(self.vertical_parts)

    def get_subdivision_braces_and_labels(
        self,
        parts: VGroup,
        labels: str,
        direction: np.ndarray,
        buff: float = SMALL_BUFF,
    ) -> VGroup:
        label_mobs = VGroup()
        braces = VGroup()
        for label, part in zip(labels, parts):
            brace = Brace(
                part, direction,
                buff=buff
            )
            if isinstance(label, Mobject):
                label_mob = label
            else:
                label_mob = Tex(label)
                label_mob.scale(self.default_label_scale_val)
            label_mob.next_to(brace, direction, buff)

            braces.add(brace)
            label_mobs.add(label_mob)
        parts.braces = braces
        parts.labels = label_mobs
        parts.label_kwargs = {
            "labels": label_mobs.copy(),
            "direction": direction,
            "buff": buff,
        }
        return VGroup(parts.braces, parts.labels)

    def get_side_braces_and_labels(
        self,
        labels: str,
        direction: np.ndarray = LEFT,
        **kwargs
    ) -> VGroup:
        assert hasattr(self, "horizontal_parts")
        parts = self.horizontal_parts
        return self.get_subdivision_braces_and_labels(parts, labels, direction, **kwargs)

    def get_top_braces_and_labels(
        self,
        labels: str,
        **kwargs
    ) -> VGroup:
        assert hasattr(self, "vertical_parts")
        parts = self.vertical_parts
        return self.get_subdivision_braces_and_labels(parts, labels, UP, **kwargs)

    def get_bottom_braces_and_labels(
        self,
        labels: str,
        **kwargs
    ) -> VGroup:
        assert hasattr(self, "vertical_parts")
        parts = self.vertical_parts
        return self.get_subdivision_braces_and_labels(parts, labels, DOWN, **kwargs)

    def add_braces_and_labels(self) -> None:
        for attr in "horizontal_parts", "vertical_parts":
            if not hasattr(self, attr):
                continue
            parts = getattr(self, attr)
            for subattr in "braces", "labels":
                if hasattr(parts, subattr):
                    self.add(getattr(parts, subattr))

    def __getitem__(self, index: int | slice) -> VGroup:
        if hasattr(self, "horizontal_parts"):
            return self.horizontal_parts[index]
        elif hasattr(self, "vertical_parts"):
            return self.vertical_parts[index]
        return self.split()[index]


class BarChart(VGroup):
    """
    Create a bar chart with configurable axes, tick marks, bars,
    and optional category labels.

    BarChart arranges rectangular bars to represent numerical
    values. Bar heights are scaled relative to max_value, while
    the axes and optional y-axis labels provide a visual reference
    for comparing the values.

    Parameters
    ----------
    values
        Iterable of numerical values represented by the bars.
    height
        Geometric height of the y-axis and maximum bar height.
        Defaults to 4.
    width
        Geometric width of the x-axis. Defaults to 6.
    n_ticks
        Number of y-axis intervals. The implementation creates
        n_ticks + 1 tick marks, including both endpoints.
    include_x_ticks
        Whether to add tick marks along the x-axis.
    tick_width
        Width of each y-axis tick and half the initial x-axis
        extension to the left of the origin.
    tick_height
        Height of each x-axis tick.
    label_y_axis
        Whether to display numerical labels beside y-axis ticks.
    y_axis_label_height
        Geometric height of each y-axis label.
    max_value
        Numerical value corresponding to the full chart height.
        If None, the maximum of values is used.
    bar_colors
        Colors interpolated across the bars using
        set_color_by_gradient. Defaults to [BLUE, YELLOW].
    bar_fill_opacity
        Fill opacity of each bar. Defaults to 0.8.
    bar_stroke_width
        Stroke width of each bar. Defaults to 3.
    bar_names
        Names displayed below bars. Defaults to an empty list.
    bar_label_scale_val
        Scale factor applied to category labels. Defaults to 0.75.
    **kwargs
        Additional keyword arguments forwarded to VGroup.

    Attributes
    ----------
    height
        Configured chart height.
    width
        Configured chart width.
    n_ticks
        Number of y-axis intervals.
    n_ticks_x
        Number of input values, used to determine x-axis tick count.
    max_value
        Value mapped to the full chart height.
    x_axis
        Horizontal axis, including x-axis ticks when enabled.
    y_axis
        Vertical axis, including y-axis ticks.
    y_axis_labels
        Group of y-axis labels, created when label_y_axis is True.
    bars
        Group of bar rectangles.
    bar_labels
        Group of category labels created from bar_names.

    Methods
    -------
    add_axes()
        Create and add the axes, tick marks, and optional y labels.
    add_bars(values)
        Create and add bars and their category labels.
    change_bar_values(values)
        Resize existing bars to represent new values.

    Notes
    -----
    - The constructor creates the axes and bars, then centers
      the complete VGroup.
    - The chart height corresponds to max_value. Each bar's
      height is calculated as value / max_value * height.
    - Bar width is calculated as width / (2 * len(values)).
      Bars are placed at regular intervals using this width.
    - The bars receive colors through set_color_by_gradient.
      Colors are interpolated across the group, rather than
      assigned by category name.
    - Y-axis tick positions and labels are generated using
      evenly spaced values from zero to max_value.
    - The implementation creates n_ticks + 1 y-axis ticks.
    - When include_x_ticks is True, n_ticks_x + 1 x-axis ticks
      are created, regardless of the number of bar_names.
    - The x-axis tick-label values are calculated but are not
      used to create labels.
    - Category labels are created by pairing bars and bar_names
      with zip. Extra bars or names are ignored by that pairing.
    - The implementation places bars using a fixed offset
      involving DOWN + LEFT * 5 before the final group is centered.
    - change_bar_values updates only the existing bars paired
      with the supplied values. Extra values or bars are ignored.
      It does not update the y-axis labels or max_value.
    - Values exceeding max_value produce bars taller than the
      configured chart height. Negative values are not specially
      handled.
    - max_value must be a usable nonzero number when calculating
      bar heights. An empty values iterable also makes automatic
      max_value calculation or bar-width calculation invalid.
    - Although max_value is annotated as float, None is explicitly
      checked to enable automatic maximum selection.

    Examples
    --------
    Create a basic bar chart::

        chart = BarChart([2, 5, 3, 7], max_value=10)

    Customize bar colors and category labels::

        chart = BarChart(
            [4, 8, 6],
            max_value=10,
            bar_colors=[BLUE, GREEN, YELLOW],
            bar_names=["A", "B", "C"],
        )

    Include x-axis ticks::

        chart = BarChart(
            [3, 6, 9],
            include_x_ticks=True,
            bar_names=["First", "Second", "Third"],
        )

    Automatically determine the maximum from the data::

        chart = BarChart(
            [2, 5, 8],
            max_value=None,
        )

    Change the bar heights after creation::

        chart = BarChart([2, 4, 6], max_value=10)
        chart.change_bar_values([5, 3, 9])

    See Also
    --------
    Axes
        Coordinate axes for mathematical plots.
    Rectangle
        Geometry used to represent each bar.
    VGroup
        Base group class for the chart components.
    """

    def __init__(
        self,
        values: Iterable[float],
        height: float = 4,
        width: float = 6,
        n_ticks: int = 4,
        include_x_ticks: bool = False,
        tick_width: float = 0.2,
        tick_height: float = 0.15,
        label_y_axis: bool = True,
        y_axis_label_height: float = 0.25,
        max_value: float = 1,
        bar_colors: list[ManimColor] = [BLUE, YELLOW],
        bar_fill_opacity: float = 0.8,
        bar_stroke_width: float = 3,
        bar_names: list[str] = [],
        bar_label_scale_val: float = 0.75,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.height = height
        self.width = width
        self.n_ticks = n_ticks
        self.include_x_ticks = include_x_ticks
        self.tick_width = tick_width
        self.tick_height = tick_height
        self.label_y_axis = label_y_axis
        self.y_axis_label_height = y_axis_label_height
        self.max_value = max_value
        self.bar_colors = bar_colors
        self.bar_fill_opacity = bar_fill_opacity
        self.bar_stroke_width = bar_stroke_width
        self.bar_names = bar_names
        self.bar_label_scale_val = bar_label_scale_val

        if self.max_value is None:
            self.max_value = max(values)

        self.n_ticks_x = len(values)
        self.add_axes()
        self.add_bars(values)
        self.center()

    def add_axes(self) -> None:
        x_axis = Line(self.tick_width * LEFT / 2, self.width * RIGHT)
        y_axis = Line(MED_LARGE_BUFF * DOWN, self.height * UP)
        y_ticks = VGroup()
        heights = np.linspace(0, self.height, self.n_ticks + 1)
        values = np.linspace(0, self.max_value, self.n_ticks + 1)
        for y, value in zip(heights, values):
            y_tick = Line(LEFT, RIGHT)
            y_tick.set_width(self.tick_width)
            y_tick.move_to(y * UP)
            y_ticks.add(y_tick)
        y_axis.add(y_ticks)

        if self.include_x_ticks == True:
            x_ticks = VGroup()
            widths = np.linspace(0, self.width, self.n_ticks_x + 1)
            label_values = np.linspace(0, len(self.bar_names), self.n_ticks_x + 1)
            for x, value in zip(widths, label_values):
                x_tick = Line(UP, DOWN)
                x_tick.set_height(self.tick_height)
                x_tick.move_to(x * RIGHT)
                x_ticks.add(x_tick)
            x_axis.add(x_ticks)

        self.add(x_axis, y_axis)
        self.x_axis, self.y_axis = x_axis, y_axis

        if self.label_y_axis:
            labels = VGroup()
            for y_tick, value in zip(y_ticks, values):
                label = Tex(str(np.round(value, 2)))
                label.set_height(self.y_axis_label_height)
                label.next_to(y_tick, LEFT, SMALL_BUFF)
                labels.add(label)
            self.y_axis_labels = labels
            self.add(labels)

    def add_bars(self, values: Iterable[float]) -> None:
        buff = float(self.width) / (2 * len(values))
        bars = VGroup()
        for i, value in enumerate(values):
            bar = Rectangle(
                height=(value / self.max_value) * self.height,
                width=buff,
                stroke_width=self.bar_stroke_width,
                fill_opacity=self.bar_fill_opacity,
            )
            bar.move_to((2 * i + 0.5) * buff * RIGHT, DOWN + LEFT * 5)
            bars.add(bar)
        bars.set_color_by_gradient(*self.bar_colors)

        bar_labels = VGroup()
        for bar, name in zip(bars, self.bar_names):
            label = Tex(str(name))
            label.scale(self.bar_label_scale_val)
            label.next_to(bar, DOWN, SMALL_BUFF)
            bar_labels.add(label)

        self.add(bars, bar_labels)
        self.bars = bars
        self.bar_labels = bar_labels

    def change_bar_values(self, values: Iterable[float]) -> None:
        for bar, value in zip(self.bars, values):
            bar_bottom = bar.get_bottom()
            bar.stretch_to_fit_height(
                (value / self.max_value) * self.height
            )
            bar.move_to(bar_bottom, DOWN)
