from __future__ import annotations

import itertools as it

import numpy as np
from scipy.integrate import solve_ivp

from manimlib.constants import FRAME_HEIGHT, FRAME_WIDTH
from manimlib.constants import WHITE
from manimlib.animation.indication import VShowPassingFlash
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.color import get_colormap_list
from manimlib.utils.color import get_color_map
from manimlib.utils.iterables import cartesian_product
from manimlib.utils.rate_functions import linear
from manimlib.utils.space_ops import get_norm

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Iterable, Sequence, TypeVar, Tuple, Optional
    from manimlib.typing import ManimColor, Vect3, VectN, VectArray, Vect3Array, Vect4Array

    from manimlib.mobject.coordinate_systems import CoordinateSystem
    from manimlib.mobject.mobject import Mobject

    T = TypeVar("T")


#### Delete these two ###
def get_vectorized_rgb_gradient_function(
    min_value: T,
    max_value: T,
    color_map: str
) -> Callable[[VectN], Vect3Array]:
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
) -> Callable[[float], Vect3]:
    vectorized_func = get_vectorized_rgb_gradient_function(min_value, max_value, color_map)
    return lambda value: vectorized_func(np.array([value]))[0]
####


def ode_solution_points(function, state0, time, dt=0.01):
    solution = solve_ivp(
        lambda t, state: function(state),
        t_span=(0, time),
        y0=state0,
        t_eval=np.arange(0, time, dt)
    )
    return solution.y.T


def move_along_vector_field(
    mobject: Mobject,
    func: Callable[[Vect3], Vect3]
) -> Mobject:
    mobject.add_updater(
        lambda m, dt: m.shift(
            func(m.get_center()) * dt
        )
    )
    return mobject


def move_submobjects_along_vector_field(
    mobject: Mobject,
    func: Callable[[Vect3], Vect3]
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

    def apply_nudge(mob, dt):
        mob.apply_function(
            lambda p: p + (cs.c2p(*func(*cs.p2c(p))) - origin) * dt
        )
    mobject.add_updater(apply_nudge)
    return mobject


def get_sample_coords(
    coordinate_system: CoordinateSystem,
    density: float = 1.0
) -> it.product[tuple[Vect3, ...]]:
    ranges = []
    for range_args in coordinate_system.get_all_ranges():
        _min, _max, step = range_args
        step /= density
        ranges.append(np.arange(_min, _max + step, step))
    return np.array(list(it.product(*ranges)))


def vectorize(pointwise_function: Callable[[Tuple], Tuple]):
    def v_func(coords_array: VectArray) -> VectArray:
        return np.array([pointwise_function(*coords) for coords in coords_array])

    return v_func


# Mobjects


class VectorField(VMobject):
    def __init__(
        self,
        # Vectorized function: Takes in an array of coordinates, returns an array of outputs.
        func: Callable[[VectArray], VectArray],
        # Typically a set of Axes or NumberPlane
        coordinate_system: CoordinateSystem,
        sample_coords: Optional[VectArray] = None,
        density: float = 2.0,
        magnitude_range: Optional[Tuple[float, float]] = None,
        color: Optional[ManimColor] = None,
        color_map_name: Optional[str] = "3b1b_colormap",
        color_map: Optional[Callable[[Sequence[float]], Vect4Array]] = None,
        stroke_opacity: float = 1.0,
        stroke_width: float = 3,
        tip_width_ratio: float = 4,
        tip_len_to_width: float = 0.01,
        max_vect_len: float | None = None,
        max_vect_len_to_step_size: float = 0.8,
        flat_stroke: bool = False,
        norm_to_opacity_func=None,  # TODO, check on this
        **kwargs
    ):
        self.func = func
        self.coordinate_system = coordinate_system
        self.stroke_width = stroke_width
        self.tip_width_ratio = tip_width_ratio
        self.tip_len_to_width = tip_len_to_width
        self.norm_to_opacity_func = norm_to_opacity_func

        # Search for sample_points
        if sample_coords is not None:
            self.sample_coords = sample_coords
        else:
            self.sample_coords = get_sample_coords(coordinate_system, density)
        self.update_sample_points()

        if max_vect_len is None:
            step_size = get_norm(self.sample_points[1] - self.sample_points[0])
            self.max_displayed_vect_len = max_vect_len_to_step_size * step_size
        else:
            self.max_displayed_vect_len = max_vect_len * coordinate_system.x_axis.get_unit_size()

        # Prepare the color map
        if magnitude_range is None:
            max_value = max(map(get_norm, func(self.sample_coords)))
            magnitude_range = (0, max_value)

        self.magnitude_range = magnitude_range

        if color is not None:
            self.color_map = None
        else:
            self.color_map = color_map or get_color_map(color_map_name)

        self.init_base_stroke_width_array(len(self.sample_coords))

        super().__init__(
            stroke_opacity=stroke_opacity,
            flat_stroke=flat_stroke,
            **kwargs
        )
        self.set_stroke(color, stroke_width)
        self.update_vectors()

    def init_points(self):
        n_samples = len(self.sample_coords)
        self.set_points(np.zeros((8 * n_samples - 1, 3)))
        self.set_joint_type('no_joint')

    def get_sample_points(
        self,
        center: np.ndarray,
        width: float,
        height: float,
        depth: float,
        x_density: float,
        y_density: float,
        z_density: float
    ) -> np.ndarray:
        to_corner = np.array([width / 2, height / 2, depth / 2])
        spacings = 1.0 / np.array([x_density, y_density, z_density])
        to_corner = spacings * (to_corner / spacings).astype(int)
        lower_corner = center - to_corner
        upper_corner = center + to_corner + spacings
        return cartesian_product(*(
            np.arange(low, high, space)
            for low, high, space in zip(lower_corner, upper_corner, spacings)
        ))

    def init_base_stroke_width_array(self, n_sample_points):
        arr = np.ones(8 * n_sample_points - 1)
        arr[4::8] = self.tip_width_ratio
        arr[5::8] = self.tip_width_ratio * 0.5
        arr[6::8] = 0
        arr[7::8] = 0
        self.base_stroke_width_array = arr

    def set_sample_coords(self, sample_coords: VectArray):
        self.sample_coords = sample_coords
        return self

    def set_stroke(self, color=None, width=None, opacity=None, behind=None, flat=None, recurse=True):
        super().set_stroke(color, None, opacity, behind, flat, recurse)
        if width is not None:
            self.set_stroke_width(float(width))
        return self

    def set_stroke_width(self, width: float):
        if self.get_num_points() > 0:
            self.get_stroke_widths()[:] = width * self.base_stroke_width_array
            self.stroke_width = width
        return self

    def update_sample_points(self):
        self.sample_points = self.coordinate_system.c2p(*self.sample_coords.T)

    def update_vectors(self):
        tip_width = self.tip_width_ratio * self.stroke_width
        tip_len = self.tip_len_to_width * tip_width

        # Outputs in the coordinate system
        outputs = self.func(self.sample_coords)
        output_norms = np.linalg.norm(outputs, axis=1)[:, np.newaxis]

        # Corresponding vector values in global coordinates
        out_vects = self.coordinate_system.c2p(*outputs.T) - self.coordinate_system.get_origin()
        out_vect_norms = np.linalg.norm(out_vects, axis=1)[:, np.newaxis]
        unit_outputs = np.zeros_like(out_vects)
        np.true_divide(out_vects, out_vect_norms, out=unit_outputs, where=(out_vect_norms > 0))

        # How long should the arrows be drawn, in global coordinates
        max_len = self.max_displayed_vect_len
        if max_len < np.inf:
            drawn_norms = max_len * np.tanh(out_vect_norms / max_len)
        else:
            drawn_norms = out_vect_norms

        # What's the distance from the base of an arrow to
        # the base of its head?
        dist_to_head_base = np.clip(drawn_norms - tip_len, 0, np.inf)  # Mixing units!

        # Set all points
        points = self.get_points()
        points[0::8] = self.sample_points
        points[2::8] = self.sample_points + dist_to_head_base * unit_outputs
        points[4::8] = points[2::8]
        points[6::8] = self.sample_points + drawn_norms * unit_outputs
        for i in (1, 3, 5):
            points[i::8] = 0.5 * (points[i - 1::8] + points[i + 1::8])
        points[7::8] = points[6:-1:8]

        # Adjust stroke widths
        width_arr = self.stroke_width * self.base_stroke_width_array
        width_scalars = np.clip(drawn_norms / tip_len, 0, 1)
        width_scalars = np.repeat(width_scalars, 8)[:-1]
        self.get_stroke_widths()[:] = width_scalars * width_arr

        # Potentially adjust opacity and color
        if self.color_map is not None:
            self.get_stroke_colors()  # Ensures the array is updated to appropriate length
            low, high = self.magnitude_range
            self.data['stroke_rgba'][:, :3] = self.color_map(
                inverse_interpolate(low, high, np.repeat(output_norms, 8)[:-1])
            )[:, :3]

        if self.norm_to_opacity_func is not None:
            self.get_stroke_opacities()[:] = self.norm_to_opacity_func(
                np.repeat(output_norms, 8)[:-1]
            )

        self.note_changed_data()
        return self


class TimeVaryingVectorField(VectorField):
    def __init__(
        self,
        # Takes in an array of points and a float for time
        time_func: Callable[[VectArray, float], VectArray],
        coordinate_system: CoordinateSystem,
        **kwargs
    ):
        self.time = 0

        def func(coords):
            return time_func(coords, self.time)

        super().__init__(func, coordinate_system, **kwargs)
        self.add_updater(lambda m, dt: m.increment_time(dt))
        self.always.update_vectors()

    def increment_time(self, dt):
        self.time += dt


class StreamLines(VGroup):
    def __init__(
        self,
        func: Callable[[VectArray], VectArray],
        coordinate_system: CoordinateSystem,
        density: float = 1.0,
        n_repeats: int = 1,
        noise_factor: float | None = None,
        # Config for drawing lines
        solution_time: float = 3,
        dt: float = 0.05,
        arc_len: float = 3,
        max_time_steps: int = 200,
        n_samples_per_line: int = 10,
        cutoff_norm: float = 15,
        # Style info
        stroke_width: float = 1.0,
        stroke_color: ManimColor = WHITE,
        stroke_opacity: float = 1,
        color_by_magnitude: bool = True,
        magnitude_range: Tuple[float, float] = (0, 2.0),
        taper_stroke_width: bool = False,
        color_map: str = "3b1b_colormap",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.func = func
        self.coordinate_system = coordinate_system
        self.density = density
        self.n_repeats = n_repeats
        self.noise_factor = noise_factor
        self.solution_time = solution_time
        self.dt = dt
        self.arc_len = arc_len
        self.max_time_steps = max_time_steps
        self.n_samples_per_line = n_samples_per_line
        self.cutoff_norm = cutoff_norm
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self.stroke_opacity = stroke_opacity
        self.color_by_magnitude = color_by_magnitude
        self.magnitude_range = magnitude_range
        self.taper_stroke_width = taper_stroke_width
        self.color_map = color_map

        self.draw_lines()
        self.init_style()

    def point_func(self, points: Vect3Array) -> Vect3:
        in_coords = np.array(self.coordinate_system.p2c(points)).T
        out_coords = self.func(in_coords)
        origin = self.coordinate_system.get_origin()
        return self.coordinate_system.c2p(*out_coords.T) - origin

    def draw_lines(self) -> None:
        lines = []
        origin = self.coordinate_system.get_origin()

        # Todo, it feels like coordinate system should just have
        # the ODE solver built into it, no?
        lines = []
        for coords in self.get_sample_coords():
            solution_coords = ode_solution_points(self.func, coords, self.solution_time, self.dt)
            line = VMobject()
            line.set_points_smoothly(self.coordinate_system.c2p(*solution_coords.T))
            # TODO, account for arc length somehow?
            line.virtual_time = self.solution_time
            lines.append(line)
        self.set_submobjects(lines)

    def get_sample_coords(self):
        cs = self.coordinate_system
        sample_coords = get_sample_coords(cs, self.density)

        noise_factor = self.noise_factor
        if noise_factor is None:
            noise_factor = (cs.x_axis.get_unit_size() / self.density) * 0.5

        return np.array([
            coords + noise_factor * np.random.random(coords.shape)
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
    def __init__(
        self,
        stream_lines: StreamLines,
        lag_range: float = 4,
        rate_multiple: float = 1.0,
        line_anim_config: dict = dict(
            rate_func=linear,
            time_width=1.0,
        ),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.stream_lines = stream_lines

        for line in stream_lines:
            line.anim = VShowPassingFlash(
                line,
                run_time=line.virtual_time / rate_multiple,
                **line_anim_config,
            )
            line.anim.begin()
            line.time = -lag_range * np.random.random()
            self.add(line.anim.mobject)

        self.add_updater(lambda m, dt: m.update(dt))

    def update(self, dt: float) -> None:
        stream_lines = self.stream_lines
        for line in stream_lines:
            line.time += dt
            adjusted_time = max(line.time, 0) % line.anim.run_time
            line.anim.update(adjusted_time / line.anim.run_time)
