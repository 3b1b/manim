from __future__ import annotations

import itertools as it

import numpy as np

from manimlib.constants import FRAME_HEIGHT, FRAME_WIDTH
from manimlib.constants import WHITE
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.indication import VShowPassingFlash
from manimlib.mobject.geometry import Arrow
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.color import get_colormap_list
from manimlib.utils.config_ops import digest_config
from manimlib.utils.config_ops import merge_dicts_recursively
from manimlib.utils.rate_functions import linear
from manimlib.utils.simple_functions import sigmoid
from manimlib.utils.space_ops import get_norm

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Iterable, Sequence, TypeVar

    import numpy.typing as npt

    from manimlib.mobject.coordinate_systems import CoordinateSystem
    from manimlib.mobject.mobject import Mobject

    T = TypeVar("T")


def get_vectorized_rgb_gradient_function(
    min_value: T,
    max_value: T,
    color_map: str
) -> Callable[[npt.ArrayLike], np.ndarray]:
    rgbs = np.array(get_colormap_list(color_map))

    def func(values):
        alphas = inverse_interpolate(
            min_value, max_value, np.array(values)
        )
        alphas = np.clip(alphas, 0, 1)
        scaled_alphas = alphas * (len(rgbs) - 1)
        indices = scaled_alphas.astype(int)
        next_indices = np.clip(indices + 1, 0, len(rgbs) - 1)
        inter_alphas = scaled_alphas % 1
        inter_alphas = inter_alphas.repeat(3).reshape((len(indices), 3))
        result = interpolate(rgbs[indices], rgbs[next_indices], inter_alphas)
        return result
    return func


def get_rgb_gradient_function(
    min_value: T,
    max_value: T,
    color_map: str
) -> Callable[[T], np.ndarray]:
    vectorized_func = get_vectorized_rgb_gradient_function(min_value, max_value, color_map)
    return lambda value: vectorized_func([value])[0]


def move_along_vector_field(
    mobject: Mobject,
    func: Callable[[np.ndarray], np.ndarray]
) -> Mobject:
    mobject.add_updater(
        lambda m, dt: m.shift(
            func(m.get_center()) * dt
        )
    )
    return mobject


def move_submobjects_along_vector_field(
    mobject: Mobject,
    func: Callable[[np.ndarray], np.ndarray]
) -> Mobject:
    def apply_nudge(mob, dt):
        for submob in mob:
            x, y = submob.get_center()[:2]
            if abs(x) < FRAME_WIDTH and abs(y) < FRAME_HEIGHT:
                submob.shift(func(submob.get_center()) * dt)

    mobject.add_updater(apply_nudge)
    return mobject


def move_points_along_vector_field(
    mobject: Mobject,
    func: Callable[[float, float], Iterable[float]],
    coordinate_system: CoordinateSystem
) -> Mobject:
    cs = coordinate_system
    origin = cs.get_origin()

    def apply_nudge(self, dt):
        mobject.apply_function(
            lambda p: p + (cs.c2p(*func(*cs.p2c(p))) - origin) * dt
        )
    mobject.add_updater(apply_nudge)
    return mobject


def get_sample_points_from_coordinate_system(
    coordinate_system: CoordinateSystem,
    step_multiple: float
) -> it.product[tuple[np.ndarray, ...]]:
    ranges = []
    for range_args in coordinate_system.get_all_ranges():
        _min, _max, step = range_args
        step *= step_multiple
        ranges.append(np.arange(_min, _max + step, step))
    return it.product(*ranges)


# Mobjects

class VectorField(VGroup):
    CONFIG = {
        "step_multiple": 0.5,
        "magnitude_range": (0, 2),
        "color_map": "3b1b_colormap",
        # Takes in actual norm, spits out displayed norm
        "length_func": lambda norm: 0.45 * sigmoid(norm),
        "opacity": 1.0,
        "vector_config": {},
    }

    def __init__(
        self,
        func: Callable[[float, float], Sequence[float]],
        coordinate_system: CoordinateSystem,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.func = func
        self.coordinate_system = coordinate_system
        self.value_to_rgb = get_rgb_gradient_function(
            *self.magnitude_range, self.color_map,
        )

        samples = get_sample_points_from_coordinate_system(
            coordinate_system, self.step_multiple
        )
        self.add(*(
            self.get_vector(coords)
            for coords in samples
        ))

    def get_vector(self, coords: Iterable[float], **kwargs) -> Arrow:
        vector_config = merge_dicts_recursively(
            self.vector_config,
            kwargs
        )

        output = np.array(self.func(*coords))
        norm = get_norm(output)
        if norm > 0:
            output *= self.length_func(norm) / norm

        origin = self.coordinate_system.get_origin()
        _input = self.coordinate_system.c2p(*coords)
        _output = self.coordinate_system.c2p(*output)

        vect = Arrow(
            origin, _output, buff=0,
            **vector_config
        )
        vect.shift(_input - origin)
        vect.set_rgba_array([[*self.value_to_rgb(norm), self.opacity]])
        return vect


class StreamLines(VGroup):
    CONFIG = {
        "step_multiple": 0.5,
        "n_repeats": 1,
        "noise_factor": None,
        # Config for drawing lines
        "dt": 0.05,
        "arc_len": 3,
        "max_time_steps": 200,
        "n_samples_per_line": 10,
        "cutoff_norm": 15,
        # Style info
        "stroke_width": 1,
        "stroke_color": WHITE,
        "stroke_opacity": 1,
        "color_by_magnitude": True,
        "magnitude_range": (0, 2.0),
        "taper_stroke_width": False,
        "color_map": "3b1b_colormap",
    }

    def __init__(
        self,
        func: Callable[[float, float], Sequence[float]],
        coordinate_system: CoordinateSystem,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.func = func
        self.coordinate_system = coordinate_system
        self.draw_lines()
        self.init_style()

    def point_func(self, point: np.ndarray) -> np.ndarray:
        in_coords = self.coordinate_system.p2c(point)
        out_coords = self.func(*in_coords)
        return self.coordinate_system.c2p(*out_coords)

    def draw_lines(self) -> None:
        lines = []
        origin = self.coordinate_system.get_origin()
        for point in self.get_start_points():
            points = [point]
            total_arc_len = 0
            time = 0
            for x in range(self.max_time_steps):
                time += self.dt
                last_point = points[-1]
                new_point = last_point + self.dt * (self.point_func(last_point) - origin)
                points.append(new_point)
                total_arc_len += get_norm(new_point - last_point)
                if get_norm(last_point) > self.cutoff_norm:
                    break
                if total_arc_len > self.arc_len:
                    break
            line = VMobject()
            line.virtual_time = time
            step = max(1, int(len(points) / self.n_samples_per_line))
            line.set_points_as_corners(points[::step])
            line.make_approximately_smooth()
            lines.append(line)
        self.set_submobjects(lines)

    def get_start_points(self) -> np.ndarray:
        cs = self.coordinate_system
        sample_coords = get_sample_points_from_coordinate_system(
            cs, self.step_multiple,
        )

        noise_factor = self.noise_factor
        if noise_factor is None:
            noise_factor = cs.x_range[2] * self.step_multiple * 0.5

        return np.array([
            cs.c2p(*coords) + noise_factor * np.random.random(3)
            for n in range(self.n_repeats)
            for coords in sample_coords
        ])

    def init_style(self) -> None:
        if self.color_by_magnitude:
            values_to_rgbs = get_vectorized_rgb_gradient_function(
                *self.magnitude_range, self.color_map,
            )
            cs = self.coordinate_system
            for line in self.submobjects:
                norms = [
                    get_norm(self.func(*cs.p2c(point)))
                    for point in line.get_points()
                ]
                rgbs = values_to_rgbs(norms)
                rgbas = np.zeros((len(rgbs), 4))
                rgbas[:, :3] = rgbs
                rgbas[:, 3] = self.stroke_opacity
                line.set_rgba_array(rgbas, "stroke_rgba")
        else:
            self.set_stroke(self.stroke_color, opacity=self.stroke_opacity)

        if self.taper_stroke_width:
            width = [0, self.stroke_width, 0]
        else:
            width = self.stroke_width
        self.set_stroke(width=width)


class AnimatedStreamLines(VGroup):
    CONFIG = {
        "lag_range": 4,
        "line_anim_class": VShowPassingFlash,
        "line_anim_config": {
            # "run_time": 4,
            "rate_func": linear,
            "time_width": 0.5,
        },
    }

    def __init__(self, stream_lines: StreamLines, **kwargs):
        super().__init__(**kwargs)
        self.stream_lines = stream_lines
        for line in stream_lines:
            line.anim = self.line_anim_class(
                line,
                run_time=line.virtual_time,
                **self.line_anim_config,
            )
            line.anim.begin()
            line.time = -self.lag_range * np.random.random()
            self.add(line.anim.mobject)

        self.add_updater(lambda m, dt: m.update(dt))

    def update(self, dt: float) -> None:
        stream_lines = self.stream_lines
        for line in stream_lines:
            line.time += dt
            adjusted_time = max(line.time, 0) % line.anim.run_time
            line.anim.update(adjusted_time / line.anim.run_time)


# TODO: This class should be deleted
class ShowPassingFlashWithThinningStrokeWidth(AnimationGroup):
    CONFIG = {
        "n_segments": 10,
        "time_width": 0.1,
        "remover": True
    }

    def __init__(self, vmobject: VMobject, **kwargs):
        digest_config(self, kwargs)
        max_stroke_width = vmobject.get_stroke_width()
        max_time_width = kwargs.pop("time_width", self.time_width)
        AnimationGroup.__init__(self, *[
            VShowPassingFlash(
                vmobject.copy().set_stroke(width=stroke_width),
                time_width=time_width,
                **kwargs
            )
            for stroke_width, time_width in zip(
                np.linspace(0, max_stroke_width, self.n_segments),
                np.linspace(max_time_width, 0, self.n_segments)
            )
        ])
