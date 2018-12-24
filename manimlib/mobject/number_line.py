from manimlib.constants import *
from manimlib.mobject.geometry import Arrow
from manimlib.mobject.geometry import Line
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import normalize


class NumberLine(VMobject):
    CONFIG = {
        "color": LIGHT_GREY,
        "x_min": -FRAME_X_RADIUS,
        "x_max": FRAME_X_RADIUS,
        "unit_size": 1,
        "tick_size": 0.1,
        "tick_frequency": 1,
        "leftmost_tick": None,  # Defaults to value near x_min s.t. 0 is a tick
        "numbers_with_elongated_ticks": [0],
        "include_numbers": False,
        "numbers_to_show": None,
        "longer_tick_multiple": 2,
        "number_at_center": 0,
        "number_scale_val": 0.75,
        "label_direction": DOWN,
        "line_to_number_buff": MED_SMALL_BUFF,
        "include_tip": False,
        "propagate_style_to_family": True,
        "decimal_number_config": {
            "num_decimal_places": 0,
        }
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.leftmost_tick is None:
            tf = self.tick_frequency
            self.leftmost_tick = tf * np.ceil(self.x_min / tf)
        VMobject.__init__(self, **kwargs)
        if self.include_tip:
            self.add_tip()
        if self.include_numbers:
            self.add_numbers()

    def generate_points(self):
        self.main_line = Line(self.x_min * RIGHT, self.x_max * RIGHT)
        self.tick_marks = VGroup()
        self.add(self.main_line, self.tick_marks)
        rounding_value = int(-np.log10(0.1 * self.tick_frequency))
        rounded_numbers_with_elongated_ticks = np.round(
            self.numbers_with_elongated_ticks,
            rounding_value
        )

        for x in self.get_tick_numbers():
            rounded_x = np.round(x, rounding_value)
            if rounded_x in rounded_numbers_with_elongated_ticks:
                tick_size_used = self.longer_tick_multiple * self.tick_size
            else:
                tick_size_used = self.tick_size
            self.add_tick(x, tick_size_used)

        self.stretch(self.unit_size, 0)
        self.shift(-self.number_to_point(self.number_at_center))

    def add_tick(self, x, size=None):
        self.tick_marks.add(self.get_tick(x, size))
        return self

    def get_tick(self, x, size=None):
        if size is None:
            size = self.tick_size
        result = Line(size * DOWN, size * UP)
        result.rotate(self.main_line.get_angle())
        result.move_to(self.number_to_point(x))
        return result

    def get_tick_marks(self):
        return self.tick_marks

    def get_tick_numbers(self):
        epsilon = 0.001
        return np.arange(
            self.leftmost_tick, self.x_max + epsilon,
            self.tick_frequency
        )

    def number_to_point(self, number):
        alpha = float(number - self.x_min) / (self.x_max - self.x_min)
        return interpolate(
            self.main_line.get_start(),
            self.main_line.get_end(),
            alpha
        )

    def point_to_number(self, point):
        start_point, end_point = self.main_line.get_start_and_end()
        full_vect = end_point - start_point
        unit_vect = normalize(full_vect)

        def distance_from_start(p):
            return np.dot(p - start_point, unit_vect)

        proportion = fdiv(
            distance_from_start(point),
            distance_from_start(end_point)
        )
        return interpolate(self.x_min, self.x_max, proportion)

    def default_numbers_to_display(self):
        if self.numbers_to_show is not None:
            return self.numbers_to_show
        return np.arange(int(self.leftmost_tick), int(self.x_max) + 1)

    def get_number_mobjects(self, *numbers, **kwargs):
        # TODO, handle decimals
        if len(numbers) == 0:
            numbers = self.default_numbers_to_display()
        result = VGroup()
        for number in numbers:
            mob = DecimalNumber(
                number, **self.decimal_number_config
            )
            mob.scale(self.number_scale_val)
            mob.next_to(
                self.number_to_point(number),
                self.label_direction,
                self.line_to_number_buff,
            )
            result.add(mob)
        return result

    def get_labels(self):
        return self.get_number_mobjects()

    def add_numbers(self, *numbers, **kwargs):
        self.numbers = self.get_number_mobjects(
            *numbers, **kwargs
        )
        self.add(self.numbers)
        return self

    def add_tip(self):
        start, end = self.main_line.get_start_and_end()
        vect = (end - start) / get_norm(end - start)
        arrow = Arrow(start, end + MED_SMALL_BUFF * vect, buff=0)
        tip = arrow.tip
        tip.set_stroke(width=self.get_stroke_width())
        tip.set_color(self.color)
        self.tip = tip
        self.add(tip)


class UnitInterval(NumberLine):
    CONFIG = {
        "x_min": 0,
        "x_max": 1,
        "unit_size": 6,
        "tick_frequency": 0.1,
        "numbers_with_elongated_ticks": [0, 1],
        "number_at_center": 0.5,
    }
