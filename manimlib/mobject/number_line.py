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
from manimlib.utils.dict_ops import merge_dicts_recursively
from manimlib.utils.simple_functions import fdiv

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Optional
    from manimlib.typing import ManimColor, Vect3, Vect3Array, VectN, RangeSpecifier


class NumberLine(Line):
    def __init__(
        self,
        x_range: RangeSpecifier = (-8, 8, 1),
        color: ManimColor = GREY_B,
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
        self.add(numbers)
        self.numbers = numbers
        return numbers


class UnitInterval(NumberLine):
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
