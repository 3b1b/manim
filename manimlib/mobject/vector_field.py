from __future__ import annotations

import itertools as it

import numpy as np
from scipy.integrate import solve_ivp

from manimlib.constants import FRAME_HEIGHT, FRAME_WIDTH
from manimlib.constants import DEFAULT_MOBJECT_COLOR
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
    """
    Return a vectorized function that maps values to RGB colors.

    Values are normalized to the given range, clipped to [0, 1], and
    mapped to the colormap using linear interpolation between adjacent
    RGB entries.

    Parameters
    ----------
    min_value, max_value
        Input value range.
    color_map
        Name of the colormap to use.

    Returns
    -------
    Callable[[VectN], Vect3Array]
        Function mapping an array of values to an (N, 3) RGB array.
    """

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
    """
    Return a scalar RGB gradient function using a colormap.

    Wraps the vectorized gradient function to accept a single value
    and return its corresponding RGB color.

    Parameters
    ----------
    min_value, max_value
    Input value range.
    color_map
    Name of the colormap.

    Returns
    -------
    Callable[[float], Vect3]
    Function mapping a scalar value to an RGB color.
    """

    vectorized_func = get_vectorized_rgb_gradient_function(min_value, max_value, color_map)
    return lambda value: vectorized_func(np.array([value]))[0]
####


def ode_solution_points(function, state0, time, dt=0.01):
    """
    Compute points along the solution of an ordinary differential equation.

    Parameters
    ----------
    function
        Function that returns the derivative of the current state.
    state0
        Initial state of the system.
    time
        End time of integration.
    dt
        Time interval between evaluation points. Defaults to 0.01.

    Returns
    -------
    np.ndarray
        Array containing the solution states, with one state per row.
    """

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
    """
    Move a mobject along a vector field using an updater.

    At each frame, evaluates the vector field at the mobject's center
    and shifts it by the resulting vector multiplied by dt.

    Parameters
    ----------
    mobject
        The mobject to move.
    func
        Function mapping a 3D position to a movement vector.

    Returns
    -------
    Mobject
        The same mobject with the updater attached.
    """

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
    """
    Move each submobject along a vector field using an updater.

    Only moves submobjects whose centers lie within the frame bounds.

    Parameters
    ----------
    mobject
        The mobject containing the submobjects to move.
    func
        Function mapping a 3D position to a movement vector.

    Returns
    -------
    Mobject
        The same mobject with the updater attached.
    """

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
    """
    Move the points of a mobject along a vector field.

    Uses the coordinate system to convert points to coordinates,
    evaluate the vector field, and convert the resulting vectors
    back to scene-space displacements.

    Parameters
    ----------
    mobject
        The mobject whose points will be moved.
    func
        Function mapping coordinates to a vector.
    coordinate_system
        Coordinate system used to convert between coordinates
        and scene-space points.

    Returns
    -------
    Mobject
        The same mobject with the updater attached.
    """

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
    """
    Generate sample coordinates across a coordinate system's ranges.

    Divides each range's step size by the given density and returns
    the Cartesian product of the resulting coordinate values.

    Parameters
    ----------
    coordinate_system
        Coordinate system providing the coordinate ranges.
    density
        Sampling density multiplier. Defaults to 1.0.

    Returns
    -------
    np.ndarray
        Array containing all combinations of sampled coordinates.
    """

    ranges = []
    for range_args in coordinate_system.get_all_ranges():
        _min, _max, step = range_args
        step /= density
        ranges.append(np.arange(_min, _max + step, step))
    return np.array(list(it.product(*ranges)))


def vectorize(pointwise_function: Callable[[Tuple], Tuple]):
    """
    Convert a pointwise function into a vectorized function.

    Applies the given function to each coordinate tuple in an array
    and returns the results as a NumPy array.

    Parameters
    ----------
    pointwise_function
        Function that accepts individual coordinates as arguments.

    Returns
    -------
    Callable[[VectArray], VectArray]
        Function that applies pointwise_function to an array of coordinates.
    """

    def v_func(coords_array: VectArray) -> VectArray:
        return np.array([pointwise_function(*coords) for coords in coords_array])

    return v_func


# Mobjects


class VectorField(VMobject):
    """
    Visualize a vector field as a collection of arrows on a coordinate system.

    Each arrow represents the output of a vectorized function evaluated at
    a sampled coordinate. Arrow direction indicates the vector's direction,
    while its displayed length is scaled to keep the visualization readable.
    Colors and opacities can optionally represent vector magnitudes.

    Parameters
    ----------
    func
        A vectorized function that accepts an array of coordinates with shape
        (N, dimension) and returns an array of vectors with corresponding shape.

    coordinate_system
        Coordinate system used to convert sampled coordinates and vector
        outputs into scene-space positions.

    sample_coords
        Optional array of coordinates at which to evaluate the vector field.
        If None, coordinates are generated using get_sample_coords().

    density
        Sampling density used when sample_coords is None. Defaults to 2.0.
        Higher values produce more sample points.

    magnitude_range
        Optional (minimum, maximum) magnitude range for color mapping.
        If None, the range is inferred from the maximum norm of the function's
        outputs at the sampled coordinates.

    color
        Optional uniform stroke color. When provided, color mapping is disabled.

    color_map_name
        Name of the colormap to use when color_map is not provided.
        Defaults to "3b1b_colormap".

    color_map
        Optional callable that maps normalized magnitudes to RGBA colors.
        Takes precedence over color_map_name when color is None.

    stroke_opacity
        Base opacity of the vector-field strokes. Defaults to 1.0.

    stroke_width
        Base stroke width. Defaults to 3.

    tip_width_ratio
        Arrowhead width relative to the base stroke width. Defaults to 4.

    tip_len_to_width
        Arrowhead length relative to its width. Defaults to 0.01.

    max_vect_len
        Optional maximum displayed vector length, scaled by the coordinate
        system's x-axis unit size. If None, the limit is derived from sample
        spacing and max_vect_len_to_step_size.

    max_vect_len_to_step_size
        Maximum displayed vector length as a multiple of sample spacing when
        max_vect_len is None. Defaults to 0.8.

    flat_stroke
        Whether to use flat strokes. Defaults to False.

    norm_to_opacity_func
        Optional function mapping vector magnitudes to stroke opacities.
        Receives an array of magnitudes corresponding to the rendered stroke
        points, with values repeated for each arrow segment.

    **kwargs
        Additional keyword arguments passed to VMobject.

    Attributes
    ----------
    func
        Vectorized function defining the vector field.
    coordinate_system
        Coordinate system used for sampling and rendering.
    sample_coords
        Coordinates where the vector field is evaluated.
    sample_points
        Corresponding positions in scene coordinates.
    magnitude_range
        Magnitude range used for color mapping.
    color_map
        Callable used to map magnitudes to colors, or None.
    max_displayed_vect_len
        Maximum displayed arrow length in scene units.
    stroke_width
        Current base stroke width.
    base_stroke_width_array
        Per-point multipliers used to shape the arrow strokes.

    Examples
    --------
    Example 1: Create a simple rotational vector field.

        axes = Axes(
            x_range=(-4, 4, 1),
            y_range=(-4, 4, 1),
        )

        def rotational_field(coords):
            x, y = coords.T
            return np.column_stack((-y, x))

        field = VectorField(
            rotational_field,
            axes,
            density=1.5,
            color=BLUE,
        )

        self.add(axes, field)

    The field produces vectors (-y, x), which are perpendicular to the
    position vector (x, y). The arrows therefore circulate around the origin.

    Example 2: Visualize a radial vector field.

        def radial_field(coords):
            return coords

        field = VectorField(
            radial_field,
            axes,
            density=2,
            color=YELLOW,
            max_vect_len=1.0,
        )

        self.add(field)

    Each vector points away from the origin. The finite max_vect_len limits
    the displayed arrow lengths using the coordinate system's x-axis scale.

    Example 3: Color vectors according to their magnitudes.

        def scaling_field(coords):
            return 0.5 * coords

        field = VectorField(
            scaling_field,
            axes,
            density=2,
            magnitude_range=(0, 3),
            color_map_name="3b1b_colormap",
        )

        self.add(field)

    The output magnitude increases with distance from the origin. When no
    uniform color is specified, the colormap maps these magnitudes to colors.
    Values outside magnitude_range are passed through inverse_interpolate
    to the colormap function, whose behavior determines their final colors.

    Example 4: Supply custom sample coordinates.

        sample_coords = np.array([
            [-2, 0, 0],
            [ 0, 0, 0],
            [ 2, 0, 0],
            [ 0, 2, 0],
        ])

        field = VectorField(
            rotational_field,
            axes,
            sample_coords=sample_coords,
            color=GREEN,
        )

        self.add(field)

    Only the specified coordinates are sampled. When sample_coords is
    provided, density is not used to generate a replacement sample grid.

    Notes
    -----
    The vectorized function must accept the coordinate array in the format
    expected by the coordinate system and return one vector per sample.

    The output vectors are converted to scene-space displacements by
    subtracting the coordinate system's scene-space origin from the
    converted vector coordinates.

    When max_vect_len is None, the initial sample spacing is estimated from
    the first two sample points. Therefore, the generated sample points
    must contain at least two entries for this calculation.

    If color is provided, color_map is set to None. Otherwise, the supplied
    color_map is used, or a colormap is obtained from color_map_name.

    Returns
    -------
    VectorField
        The initialized vector-field visualization as a VMobject.
    """

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
            self.data['stroke_width'] = width * self.base_stroke_width_array[:, np.newaxis]
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

        # Everything below writes through views onto the data rather than replacing fields
        with self.data.being_written():
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
        return self


class TimeVaryingVectorField(VectorField):
    """
    Visualize a time-dependent vector field.

    Extends VectorField by evaluating the vector function using the current
    simulation time. An updater advances time and refreshes the displayed
    vectors as the animation progresses.

    Parameters
    ----------
    time_func
        Function accepting an array of coordinates and a time value, returning
        an array of vectors with corresponding shape.
    coordinate_system
        Coordinate system used to position and scale the vectors.
    **kwargs
        Additional keyword arguments forwarded to VectorField.

    Attributes
    ----------
    time
        Current elapsed simulation time, initialized to 0.

    Examples
    --------
    Example 1: Create a rotating vector field.

        axes = Axes(
            x_range=(-4, 4, 1),
            y_range=(-4, 4, 1),
        )

        def rotating_field(coords, time):
            x, y = coords.T
            angle = time
            c, s = np.cos(angle), np.sin(angle)
            return np.column_stack((
                c * (-y) - s * x,
                s * (-y) + c * x,
            ))

        field = TimeVaryingVectorField(
            rotating_field,
            axes,
            density=1.5,
            color=BLUE,
        )

        self.add(axes, field)
        self.wait(5)

    The function receives the sampled coordinates and the current time.
    As time advances, the vectors are recalculated to show the evolving field.

    Example 2: Create a field whose strength oscillates over time.

        def oscillating_field(coords, time):
            return np.sin(time) * coords

        field = TimeVaryingVectorField(
            oscillating_field,
            axes,
            density=2,
            color=YELLOW,
        )

        self.add(field)
        self.wait(2 * PI)

    The vector magnitudes vary with sin(time), periodically changing direction
    when the multiplier changes sign and becoming zero when sin(time) is zero.

    Notes
    -----
    The field's time is advanced by the attached updater using the frame
    delta time. The time_func must accept the coordinate array and current
    time as separate arguments.

    Returns
    -------
    TimeVaryingVectorField
        The initialized time-dependent vector-field visualization.
    """

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
    """
    Generate and style streamlines for a vector field.

    Each streamline is obtained by numerically integrating the vector field
    from a sampled starting coordinate and drawing the resulting trajectory
    as a smooth VMobject. Lines can be repeated with random offsets and
    colored according to the vector field's magnitude.

    Parameters
    ----------
    func
        Vectorized function mapping an array of coordinates to an array
        of corresponding vectors.
    coordinate_system
        Coordinate system used to convert between coordinate-space values
        and scene-space points.
    density
        Sampling density used to generate starting coordinates. Defaults to 1.0.
    n_repeats
        Number of times to repeat the sampled starting coordinates.
        Defaults to 1.
    noise_factor
        Magnitude of random offsets applied to starting coordinates.
        If None, it is derived from the x-axis unit size and density.
    solution_time
        Integration duration for each streamline. Defaults to 3.
    dt
        Time interval between numerical solution samples. Defaults to 0.05.
    arc_len
        Stored configuration value for streamline arc length; it is not
        currently used in the implementation.
    max_time_steps
        Stored configuration value for the maximum number of time steps;
        it is not currently used in the implementation.
    n_samples_per_line
        Stored configuration value for samples per line; it is not
        currently used in the implementation.
    cutoff_norm
        Stored configuration value for a vector-norm cutoff; it is not
        currently used in the implementation.
    stroke_width
        Stroke width used when styling the streamlines. Defaults to 1.0.
    stroke_color
        Uniform stroke color when color_by_magnitude is False.
    stroke_opacity
        Stroke opacity. Defaults to 1.
    color_by_magnitude
        Whether to color each streamline according to vector magnitudes.
        Defaults to True.
    magnitude_range
        Minimum and maximum magnitudes used for color mapping.
        Defaults to (0, 2.0).
    taper_stroke_width
        Whether to taper each streamline's stroke width at both ends.
        Defaults to False.
    color_map
        Name of the colormap used when coloring by magnitude.
        Defaults to "3b1b_colormap".
    **kwargs
        Additional keyword arguments passed to VGroup.

    Attributes
    ----------
    func
        Vectorized function defining the vector field.
    coordinate_system
        Coordinate system used to generate and display streamlines.
    submobjects
        Generated streamline VMobjects. Each line stores solution_time
        in its virtual_time attribute.

    Examples
    --------
    Example 1: Draw streamlines for a rotational vector field.

        axes = Axes(
            x_range=(-4, 4, 1),
            y_range=(-4, 4, 1),
        )

        def rotational_field(coords):
            x, y = coords.T
            return np.column_stack((-y, x))

        streamlines = StreamLines(
            rotational_field,
            axes,
            density=1,
            solution_time=4,
            dt=0.05,
            color_by_magnitude=False,
            stroke_color=BLUE,
        )

        self.add(axes, streamlines)

    The vectors circulate around the origin, producing curved streamlines.

    Example 2: Color streamlines by vector magnitude.

        def radial_field(coords):
            return coords

        streamlines = StreamLines(
            radial_field,
            axes,
            density=1.5,
            solution_time=2,
            color_by_magnitude=True,
            magnitude_range=(0, 4),
            color_map="3b1b_colormap",
            stroke_width=1.5,
        )

        self.add(streamlines)

    Colors are determined by the magnitude of the vector field evaluated
    along each streamline.

    Example 3: Add repeated, slightly offset streamlines.

        streamlines = StreamLines(
            rotational_field,
            axes,
            density=1,
            n_repeats=3,
            noise_factor=0.05,
            solution_time=3,
            taper_stroke_width=True,
        )

        self.add(streamlines)

    Each repetition samples the same coordinate grid with random offsets.
    With taper_stroke_width enabled, the stroke narrows toward both ends.

    Notes
    -----
    Starting coordinates are generated using get_sample_coords().
    Random offsets are applied independently to each sampled coordinate
    for every repetition.

    The function is integrated using ode_solution_points(). The resulting
    coordinate trajectories are converted to scene-space points and drawn
    with set_points_smoothly().

    The arc_len, max_time_steps, n_samples_per_line, and cutoff_norm
    arguments are stored as attributes but do not currently affect the
    line-generation process in this implementation.

    Returns
    -------
    StreamLines
        A VGroup containing the generated and styled streamline objects.
    """

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
        stroke_color: ManimColor = DEFAULT_MOBJECT_COLOR,
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
                    get_norm(self.func(cs.p2c(point)))
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
    """
    Animate streamlines by repeatedly showing moving flashes along them.

    Each streamline receives a VShowPassingFlash animation that loops
    continuously. The animations start at randomized time offsets to create
    a staggered flow effect.

    Parameters
    ----------
    stream_lines
        StreamLines object containing the paths to animate. Each line must
        have a virtual_time attribute specifying its animation duration.
    lag_range
        Maximum initial delay applied randomly to each line. Defaults to 4.
    rate_multiple
        Multiplier controlling animation speed. Each animation's runtime is
        line.virtual_time / rate_multiple. Defaults to 1.0.
    line_anim_config
        Additional configuration passed to VShowPassingFlash.
        Defaults to linear rate_func and time_width=1.0.
    **kwargs
        Additional keyword arguments passed to VGroup.

    Attributes
    ----------
    stream_lines
        The original StreamLines object being animated.

    Examples
    --------
    Example 1: Animate a rotational vector field.

        axes = Axes(
            x_range=(-4, 4, 1),
            y_range=(-4, 4, 1),
        )

        def rotational_field(coords):
            x, y = coords.T
            return np.column_stack((-y, x))

        stream_lines = StreamLines(
            rotational_field,
            axes,
            density=1,
            solution_time=4,
            color_by_magnitude=False,
            stroke_color=BLUE,
        )

        animated_lines = AnimatedStreamLines(
            stream_lines,
            lag_range=3,
            rate_multiple=1,
        )

        self.add(axes, animated_lines)
        self.wait(5)

    Flashes travel along the streamlines, producing the appearance of
    continuous motion around the origin.

    Example 2: Increase the animation speed.

        animated_lines = AnimatedStreamLines(
            stream_lines,
            rate_multiple=2,
        )

        self.add(animated_lines)

    A larger rate_multiple reduces each animation's runtime, making the
    flashes cycle more quickly.

    Example 3: Customize the passing-flash appearance.

        animated_lines = AnimatedStreamLines(
            stream_lines,
            line_anim_config={
                "rate_func": linear,
                "time_width": 0.3,
            },
        )

        self.add(animated_lines)

    The smaller time_width narrows the visible portion of each passing
    flash, creating shorter moving highlights.

    Notes
    -----
    Each line's animation is initialized and begun during construction.
    Its time offset is randomized between -lag_range and 0.

    During updates, line.time increases by dt. Negative times delay the
    start of the corresponding flash. Once active, the animation progress
    wraps around its runtime, causing the flash to repeat.

    The class adds an updater that calls update(dt) each frame.

    Returns
    -------
    AnimatedStreamLines
        A VGroup containing the animated flash mobjects.
    """

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

    def update(self, dt: float = 0) -> None:
        stream_lines = self.stream_lines
        for line in stream_lines:
            line.time += dt
            adjusted_time = max(line.time, 0) % line.anim.run_time
            line.anim.update(adjusted_time / line.anim.run_time)
