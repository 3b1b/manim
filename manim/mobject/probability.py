"""Mobjects representing objects from probability theory and statistics."""

__all__ = ["SampleSpace", "BarChart"]


from ..constants import *
from ..mobject.geometry import Line
from ..mobject.geometry import Rectangle
from ..mobject.mobject import Mobject
from ..mobject.svg.brace import Brace
from ..mobject.svg.tex_mobject import MathTex
from ..mobject.svg.tex_mobject import Tex
from ..mobject.types.vectorized_mobject import VGroup
from ..utils.color import (
    color_gradient,
    DARK_GREY,
    LIGHT_GREY,
    GREEN_E,
    BLUE_E,
    MAROON_B,
    YELLOW,
    BLUE,
)
from ..utils.iterables import tuplify

EPSILON = 0.0001


class SampleSpace(Rectangle):
    CONFIG = {
        "height": 3,
        "width": 3,
        "fill_color": DARK_GREY,
        "fill_opacity": 1,
        "stroke_width": 0.5,
        "stroke_color": LIGHT_GREY,
        ##
        "default_label_scale_val": 1,
    }

    def add_title(self, title="Sample space", buff=MED_SMALL_BUFF):
        # TODO, should this really exist in SampleSpaceScene
        title_mob = Tex(title)
        if title_mob.get_width() > self.get_width():
            title_mob.set_width(self.get_width())
        title_mob.next_to(self, UP, buff=buff)
        self.title = title_mob
        self.add(title_mob)

    def add_label(self, label):
        self.label = label

    def complete_p_list(self, p_list):
        new_p_list = list(tuplify(p_list))
        remainder = 1.0 - sum(new_p_list)
        if abs(remainder) > EPSILON:
            new_p_list.append(remainder)
        return new_p_list

    def get_division_along_dimension(self, p_list, dim, colors, vect):
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

    def get_horizontal_division(self, p_list, colors=[GREEN_E, BLUE_E], vect=DOWN):
        return self.get_division_along_dimension(p_list, 1, colors, vect)

    def get_vertical_division(self, p_list, colors=[MAROON_B, YELLOW], vect=RIGHT):
        return self.get_division_along_dimension(p_list, 0, colors, vect)

    def divide_horizontally(self, *args, **kwargs):
        self.horizontal_parts = self.get_horizontal_division(*args, **kwargs)
        self.add(self.horizontal_parts)

    def divide_vertically(self, *args, **kwargs):
        self.vertical_parts = self.get_vertical_division(*args, **kwargs)
        self.add(self.vertical_parts)

    def get_subdivision_braces_and_labels(
        self, parts, labels, direction, buff=SMALL_BUFF, min_num_quads=1
    ):
        label_mobs = VGroup()
        braces = VGroup()
        for label, part in zip(labels, parts):
            brace = Brace(part, direction, min_num_quads=min_num_quads, buff=buff)
            if isinstance(label, Mobject):
                label_mob = label
            else:
                label_mob = MathTex(label)
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

    def get_side_braces_and_labels(self, labels, direction=LEFT, **kwargs):
        assert hasattr(self, "horizontal_parts")
        parts = self.horizontal_parts
        return self.get_subdivision_braces_and_labels(
            parts, labels, direction, **kwargs
        )

    def get_top_braces_and_labels(self, labels, **kwargs):
        assert hasattr(self, "vertical_parts")
        parts = self.vertical_parts
        return self.get_subdivision_braces_and_labels(parts, labels, UP, **kwargs)

    def get_bottom_braces_and_labels(self, labels, **kwargs):
        assert hasattr(self, "vertical_parts")
        parts = self.vertical_parts
        return self.get_subdivision_braces_and_labels(parts, labels, DOWN, **kwargs)

    def add_braces_and_labels(self):
        for attr in "horizontal_parts", "vertical_parts":
            if not hasattr(self, attr):
                continue
            parts = getattr(self, attr)
            for subattr in "braces", "labels":
                if hasattr(parts, subattr):
                    self.add(getattr(parts, subattr))

    def __getitem__(self, index):
        if hasattr(self, "horizontal_parts"):
            return self.horizontal_parts[index]
        elif hasattr(self, "vertical_parts"):
            return self.vertical_parts[index]
        return self.split()[index]


class BarChart(VGroup):
    CONFIG = {
        "height": 4,
        "width": 6,
        "n_ticks": 4,
        "tick_width": 0.2,
        "label_y_axis": True,
        "y_axis_label_height": 0.25,
        "max_value": 1,
        "bar_colors": [BLUE, YELLOW],
        "bar_fill_opacity": 0.8,
        "bar_stroke_width": 3,
        "bar_names": [],
        "bar_label_scale_val": 0.75,
    }

    def __init__(self, values, **kwargs):
        VGroup.__init__(self, **kwargs)
        if self.max_value is None:
            self.max_value = max(values)

        self.add_axes()
        self.add_bars(values)
        self.center()

    def add_axes(self):
        x_axis = Line(self.tick_width * LEFT / 2, self.width * RIGHT)
        y_axis = Line(MED_LARGE_BUFF * DOWN, self.height * UP)
        ticks = VGroup()
        heights = np.linspace(0, self.height, self.n_ticks + 1)
        values = np.linspace(0, self.max_value, self.n_ticks + 1)
        for y, value in zip(heights, values):
            tick = Line(LEFT, RIGHT)
            tick.set_width(self.tick_width)
            tick.move_to(y * UP)
            ticks.add(tick)
        y_axis.add(ticks)

        self.add(x_axis, y_axis)
        self.x_axis, self.y_axis = x_axis, y_axis

        if self.label_y_axis:
            labels = VGroup()
            for tick, value in zip(ticks, values):
                label = MathTex(str(np.round(value, 2)))
                label.set_height(self.y_axis_label_height)
                label.next_to(tick, LEFT, SMALL_BUFF)
                labels.add(label)
            self.y_axis_labels = labels
            self.add(labels)

    def add_bars(self, values):
        buff = float(self.width) / (2 * len(values) + 1)
        bars = VGroup()
        for i, value in enumerate(values):
            bar = Rectangle(
                height=(value / self.max_value) * self.height,
                width=buff,
                stroke_width=self.bar_stroke_width,
                fill_opacity=self.bar_fill_opacity,
            )
            bar.move_to((2 * i + 1) * buff * RIGHT, DOWN + LEFT)
            bars.add(bar)
        bars.set_color_by_gradient(*self.bar_colors)

        bar_labels = VGroup()
        for bar, name in zip(bars, self.bar_names):
            label = MathTex(str(name))
            label.scale(self.bar_label_scale_val)
            label.next_to(bar, DOWN, SMALL_BUFF)
            bar_labels.add(label)

        self.add(bars, bar_labels)
        self.bars = bars
        self.bar_labels = bar_labels

    def change_bar_values(self, values):
        for bar, value in zip(self.bars, values):
            bar_bottom = bar.get_bottom()
            bar.stretch_to_fit_height((value / self.max_value) * self.height)
            bar.move_to(bar_bottom, DOWN)
