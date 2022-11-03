from __future__ import annotations

import numpy as np

from manimlib.constants import DOWN, LEFT, RIGHT, UP
from manimlib.constants import GREY_B
from manimlib.constants import MED_SMALL_BUFF
from manimlib.mobject.geometry import Line
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import outer_interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.config_ops import merge_dicts_recursively
from manimlib.utils.simple_functions import fdiv

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Sequence


class NumberLine(Line):
    CONFIG = {
        "color": GREY_B,
        "stroke_width": 2,
        # List of 2 or 3 elements, x_min, x_max, step_size
        "x_range": [-8, 8, 1],
        # How big is one one unit of this number line in terms of absolute spacial distance
        "unit_size": 1,
        "width": None,
        "include_ticks": True,
        "tick_size": 0.1,
        "longer_tick_multiple": 1.5,
        "tick_offset": 0,
        # Change name
        "numbers_with_elongated_ticks": [],
        "include_numbers": False,
        "line_to_number_direction": DOWN,
        "line_to_number_buff": MED_SMALL_BUFF,
        "include_tip": False,
        "tip_config": {
            "width": 0.25,
            "length": 0.25,
        },
        "decimal_number_config": {
            "num_decimal_places": 0,
            "font_size": 36,
        },
        "numbers_to_exclude": None
    }

    def __init__(self, x_range: Sequence[float] | None = None, **kwargs):
        digest_config(self, kwargs)
        if x_range is None:
            x_range = self.x_range
        if len(x_range) == 2:
            x_range = [*x_range, 1]

        x_min, x_max, x_step = x_range
        # A lot of old scenes pass in x_min or x_max explicitly,
        # so this is just here to keep those workin
        self.x_min: float = kwargs.get("x_min", x_min)
        self.x_max: float = kwargs.get("x_max", x_max)
        self.x_step: float = kwargs.get("x_step", x_step)

        super().__init__(self.x_min * RIGHT, self.x_max * RIGHT, **kwargs)
        if self.width:
            self.set_width(self.width)
            self.unit_size = self.get_unit_size()
        else:
            self.scale(self.unit_size)
        self.center()

        if self.include_tip:
            self.add_tip()
            self.tip.set_stroke(
                self.stroke_color,
                self.stroke_width,
            )
        if self.include_ticks:
            self.add_ticks()
        if self.include_numbers:
            self.add_numbers(excluding=self.numbers_to_exclude)

    def get_tick_range(self) -> np.ndarray:
        if self.include_tip:
            x_max = self.x_max
        else:
            x_max = self.x_max + self.x_step
        return np.arange(self.x_min, x_max, self.x_step)

    def add_ticks(self) -> None:
        ticks = VGroup()
        for x in self.get_tick_range():
            size = self.tick_size
            if np.isclose(self.numbers_with_elongated_ticks, x).any():
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

    def number_to_point(self, number: float | np.ndarray) -> np.ndarray:
        alpha = (number - self.x_min) / (self.x_max - self.x_min)
        return outer_interpolate(self.get_start(), self.get_end(), alpha)

    def point_to_number(self, point: np.ndarray) -> float:
        points = self.get_points()
        start = points[0]
        end = points[-1]
        vect = end - start
        proportion = fdiv(
            np.dot(point - start, vect),
            np.dot(end - start, vect),
        )
        return interpolate(self.x_min, self.x_max, proportion)

    def n2p(self, number: float) -> np.ndarray:
        """Abbreviation for number_to_point"""
        return self.number_to_point(number)

    def p2n(self, point: np.ndarray) -> float:
        """Abbreviation for point_to_number"""
        return self.point_to_number(point)

    def get_unit_size(self) -> float:
        return self.get_length() / (self.x_max - self.x_min)

    def get_number_mobject(
        self,
        x: float,
        direction: np.ndarray | None = None,
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
        if x == unit and unit_tex:
            center = num_mob.get_center()
            num_mob.remove(num_mob[0])
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
        self.add(numbers)
        self.numbers = numbers
        return numbers


class UnitInterval(NumberLine):
    CONFIG = {
        "x_range": [0, 1, 0.1],
        "unit_size": 10,
        "numbers_with_elongated_ticks": [0, 1],
        "decimal_number_config": {
            "num_decimal_places": 1,
        }
    }
