from __future__ import annotations

from functools import wraps

import moderngl
import numpy as np

from manimlib.constants import GREY_A, GREY_C, GREY_E
from manimlib.constants import BLACK, WHITE
from manimlib.constants import DEFAULT_STROKE_WIDTH
from manimlib.constants import DEGREES
from manimlib.constants import JOINT_TYPE_MAP
from manimlib.constants import ORIGIN, OUT, UP
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.utils.bezier import bezier
from manimlib.utils.bezier import get_quadratic_approximation_of_cubic
from manimlib.utils.bezier import get_smooth_cubic_bezier_handle_points
from manimlib.utils.bezier import get_smooth_quadratic_bezier_handle_points
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.bezier import find_intersection
from manimlib.utils.bezier import partial_quadratic_bezier_points
from manimlib.utils.bezier import outer_interpolate
from manimlib.utils.color import color_gradient
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.iterables import listify
from manimlib.utils.iterables import make_even
from manimlib.utils.iterables import resize_array
from manimlib.utils.iterables import resize_with_interpolation
from manimlib.utils.iterables import resize_preserving_order
from manimlib.utils.iterables import arrays_match
from manimlib.utils.space_ops import angle_between_vectors
from manimlib.utils.space_ops import cross2d
from manimlib.utils.space_ops import earclip_triangulation
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import get_unit_normal
from manimlib.utils.space_ops import line_intersects_path
from manimlib.utils.space_ops import midpoint
from manimlib.utils.space_ops import normalize_along_axis
from manimlib.utils.space_ops import z_to_vector
from manimlib.utils.simple_functions import arr_clip
from manimlib.shader_wrapper import ShaderWrapper

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Iterable, Sequence, Tuple
    from manimlib.typing import ManimColor, Vect3, Vect4, Vect3Array, Vect4Array

DEFAULT_STROKE_COLOR = GREY_A
DEFAULT_FILL_COLOR = GREY_C

class VMobject(Mobject):
    fill_shader_folder: str = "quadratic_bezier_fill"
    stroke_shader_folder: str = "quadratic_bezier_stroke"
    shader_dtype: np.dtype = np.dtype([
        ('point', np.float32, (3,)),
        ('stroke_rgba', np.float32, (4,)),
        ('stroke_width', np.float32, (1,)),
        ('joint_angle', np.float32, (1,)),
        ('fill_rgba', np.float32, (4,)),
        ('orientation', np.float32, (1,)),
        ('vert_index', np.float32, (1,)),
    ])
    fill_data_names = ['point', 'fill_rgba', 'orientation', 'vert_index']
    stroke_data_names = ['point', 'stroke_rgba', 'stroke_width', 'joint_angle']

    fill_render_primitive: int = moderngl.TRIANGLES
    stroke_render_primitive: int = moderngl.TRIANGLE_STRIP

    pre_function_handle_to_anchor_scale_factor: float = 0.01
    make_smooth_after_applying_functions: bool = False
    # TODO, do we care about accounting for varying zoom levels?
    tolerance_for_point_equality: float = 1e-8

    def __init__(
        self,
        color: ManimColor = None,  # If set, this will override stroke_color and fill_color
        fill_color: ManimColor = None,
        fill_opacity: float | Iterable[float] | None = 0.0,
        stroke_color: ManimColor = None,
        stroke_opacity: float | Iterable[float] | None = 1.0,
        stroke_width: float | Iterable[float] | None = DEFAULT_STROKE_WIDTH,
        stroke_behind: bool = False,
        background_image_file: str | None = None,
        long_lines: bool = False,
        # Could also be "no_joint", "bevel", "miter"
        joint_type: str = "auto",
        flat_stroke: bool = False,
        use_simple_quadratic_approx: bool = False,
        # Measured in pixel widths
        anti_alias_width: float = 1.0,
        **kwargs
    ):
        self.fill_color = fill_color or color or DEFAULT_FILL_COLOR
        self.fill_opacity = fill_opacity
        self.stroke_color = stroke_color or color or DEFAULT_STROKE_COLOR
        self.stroke_opacity = stroke_opacity
        self.stroke_width = stroke_width
        self.stroke_behind = stroke_behind
        self.background_image_file = background_image_file
        self.long_lines = long_lines
        self.joint_type = joint_type
        self.flat_stroke = flat_stroke
        self.use_simple_quadratic_approx = use_simple_quadratic_approx
        self.anti_alias_width = anti_alias_width

        self.needs_new_triangulation = True
        self.triangulation = np.zeros(0, dtype='i4')
        self.needs_new_joint_angles = True
        self.outer_vert_indices = np.zeros(0, dtype='i4')

        super().__init__(**kwargs)

    def get_group_class(self):
        return VGroup

    def init_uniforms(self):
        super().init_uniforms()
        self.uniforms["anti_alias_width"] = self.anti_alias_width
        self.uniforms["joint_type"] = JOINT_TYPE_MAP[self.joint_type]
        self.uniforms["flat_stroke"] = float(self.flat_stroke)

    # These are here just to make type checkers happy
    def get_family(self, recurse: bool = True) -> list[VMobject]:
        return super().get_family(recurse)

    def family_members_with_points(self) -> list[VMobject]:
        return super().family_members_with_points()

    def replicate(self, n: int) -> VGroup:
        if self.has_fill():
            self.get_triangulation()
        return super().replicate(n)

    def get_grid(self, *args, **kwargs) -> VGroup:
        return super().get_grid(*args, **kwargs)

    def __getitem__(self, value: int | slice) -> VMobject:
        return super().__getitem__(value)

    def add(self, *vmobjects: VMobject):
        if not all((isinstance(m, VMobject) for m in vmobjects)):
            raise Exception("All submobjects must be of type VMobject")
        super().add(*vmobjects)

    # Colors
    def init_colors(self):
        self.set_fill(
            color=self.fill_color,
            opacity=self.fill_opacity,
        )
        self.set_stroke(
            color=self.stroke_color,
            width=self.stroke_width,
            opacity=self.stroke_opacity,
            background=self.stroke_behind,
        )
        self.set_gloss(self.gloss)
        self.set_flat_stroke(self.flat_stroke)
        self.color = self.get_color()
        return self

    def set_rgba_array(
        self,
        rgba_array: Vect4Array,
        name: str | None = None,
        recurse: bool = False
    ):
        if name is None:
            names = ["fill_rgba", "stroke_rgba"]
        else:
            names = [name]

        for name in names:
            super().set_rgba_array(rgba_array, name, recurse)
        return self

    def set_fill(
        self,
        color: ManimColor | Iterable[ManimColor] = None,
        opacity: float | Iterable[float] | None = None,
        recurse: bool = True
    ):
        self.set_rgba_array_by_color(color, opacity, 'fill_rgba', recurse)
        return self

    def set_stroke(
        self,
        color: ManimColor | Iterable[ManimColor] = None,
        width: float | Iterable[float] | None = None,
        opacity: float | Iterable[float] | None = None,
        background: bool | None = None,
        recurse: bool = True
    ):
        self.set_rgba_array_by_color(color, opacity, 'stroke_rgba', recurse)

        if width is not None:
            for mob in self.get_family(recurse):
                data = mob.data if mob.get_num_points() > 0 else mob._data_defaults
                width_arr = np.array(listify(width)).flatten()
                if len(width_arr) == 0:
                    continue
                data['stroke_width'][:, 0] = resize_with_interpolation(width_arr, len(data))

        if background is not None:
            for mob in self.get_family(recurse):
                mob.stroke_behind = background
        return self

    def set_backstroke(
        self,
        color: ManimColor | Iterable[ManimColor] = BLACK,
        width: float | Iterable[float] = 3,
        background: bool = True
    ):
        self.set_stroke(color, width, background=background)
        return self

    def set_style(
        self,
        fill_color: ManimColor | Iterable[ManimColor] | None = None,
        fill_opacity: float | Iterable[float] | None = None,
        fill_rgba: Vect4 | None = None,
        stroke_color: ManimColor | Iterable[ManimColor] | None = None,
        stroke_opacity: float | Iterable[float] | None = None,
        stroke_rgba: Vect4 | None = None,
        stroke_width: float | Iterable[float] | None = None,
        stroke_background: bool = True,
        reflectiveness: float | None = None,
        gloss: float | None = None,
        shadow: float | None = None,
        recurse: bool = True
    ):
        for mob in self.get_family(recurse):
            if fill_rgba is not None:
                mob.data['fill_rgba'][:] = resize_with_interpolation(fill_rgba, len(mob.data['fill_rgba']))
            else:
                mob.set_fill(
                    color=fill_color,
                    opacity=fill_opacity,
                    recurse=False
                )

            if stroke_rgba is not None:
                mob.data['stroke_rgba'][:] = resize_with_interpolation(stroke_rgba, len(mob.data['stroke_rgba']))
                mob.set_stroke(
                    width=stroke_width,
                    background=stroke_background,
                    recurse=False,
                )
            else:
                mob.set_stroke(
                    color=stroke_color,
                    width=stroke_width,
                    opacity=stroke_opacity,
                    recurse=False,
                    background=stroke_background,
                )

            if reflectiveness is not None:
                mob.set_reflectiveness(reflectiveness, recurse=False)
            if gloss is not None:
                mob.set_gloss(gloss, recurse=False)
            if shadow is not None:
                mob.set_shadow(shadow, recurse=False)
        return self

    def get_style(self):
        data = self.data if self.get_num_points() > 0 else self._data_defaults
        return {
            "fill_rgba": data['fill_rgba'].copy(),
            "stroke_rgba": data['stroke_rgba'].copy(),
            "stroke_width": data['stroke_width'].copy(),
            "stroke_background": self.stroke_behind,
            "reflectiveness": self.get_reflectiveness(),
            "gloss": self.get_gloss(),
            "shadow": self.get_shadow(),
        }

    def match_style(self, vmobject: VMobject, recurse: bool = True):
        self.set_style(**vmobject.get_style(), recurse=False)
        if recurse:
            # Does its best to match up submobject lists, and
            # match styles accordingly
            submobs1, submobs2 = self.submobjects, vmobject.submobjects
            if len(submobs1) == 0:
                return self
            elif len(submobs2) == 0:
                submobs2 = [vmobject]
            for sm1, sm2 in zip(*make_even(submobs1, submobs2)):
                sm1.match_style(sm2)
        return self

    def set_color(
        self,
        color: ManimColor | Iterable[ManimColor] | None,
        opacity: float | Iterable[float] | None = None,
        recurse: bool = True
    ):
        self.set_fill(color, opacity=opacity, recurse=recurse)
        self.set_stroke(color, opacity=opacity, recurse=recurse)
        return self

    def set_opacity(
        self,
        opacity: float | Iterable[float] | None,
        recurse: bool = True
    ):
        self.set_fill(opacity=opacity, recurse=recurse)
        self.set_stroke(opacity=opacity, recurse=recurse)
        return self

    def fade(self, darkness: float = 0.5, recurse: bool = True):
        mobs = self.get_family() if recurse else [self]
        for mob in mobs:
            factor = 1.0 - darkness
            mob.set_fill(
                opacity=factor * mob.get_fill_opacity(),
                recurse=False,
            )
            mob.set_stroke(
                opacity=factor * mob.get_stroke_opacity(),
                recurse=False,
            )
        return self

    def get_fill_colors(self) -> list[str]:
        return [
            rgb_to_hex(rgba[:3])
            for rgba in self.data['fill_rgba']
        ]

    def get_fill_opacities(self) -> np.ndarray:
        return self.data['fill_rgba'][:, 3]

    def get_stroke_colors(self) -> list[str]:
        return [
            rgb_to_hex(rgba[:3])
            for rgba in self.data['stroke_rgba']
        ]

    def get_stroke_opacities(self) -> np.ndarray:
        return self.data['stroke_rgba'][:, 3]

    def get_stroke_widths(self) -> np.ndarray:
        return self.data['stroke_width'][:, 0]

    # TODO, it's weird for these to return the first of various lists
    # rather than the full information
    def get_fill_color(self) -> str:
        """
        If there are multiple colors (for gradient)
        this returns the first one
        """
        data = self.data if self.has_points() else self._data_defaults
        return rgb_to_hex(data["fill_rgba"][0, :3])

    def get_fill_opacity(self) -> float:
        """
        If there are multiple opacities, this returns the
        first
        """
        data = self.data if self.has_points() else self._data_defaults
        return data["fill_rgba"][0, 3]

    def get_stroke_color(self) -> str:
        data = self.data if self.has_points() else self._data_defaults
        return rgb_to_hex(data["stroke_rgba"][0, :3])

    def get_stroke_width(self) -> float | np.ndarray:
        data = self.data if self.has_points() else self._data_defaults
        return data["stroke_width"][0, 0]

    def get_stroke_opacity(self) -> float:
        data = self.data if self.has_points() else self._data_defaults
        return data["stroke_rgba"][0, 3]

    def get_color(self) -> str:
        if self.has_fill():
            return self.get_fill_color()
        return self.get_stroke_color()

    def has_stroke(self) -> bool:
        return any(self.data['stroke_width']) and any(self.data['stroke_rgba'][:, 3])

    def has_fill(self) -> bool:
        return any(self.data['fill_rgba'][:, 3])

    def get_opacity(self) -> float:
        if self.has_fill():
            return self.get_fill_opacity()
        return self.get_stroke_opacity()

    def set_flat_stroke(self, flat_stroke: bool = True, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.uniforms["flat_stroke"] = float(flat_stroke)
        return self

    def get_flat_stroke(self) -> bool:
        return self.uniforms["flat_stroke"] == 1.0

    def set_joint_type(self, joint_type: str, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.uniforms["joint_type"] = JOINT_TYPE_MAP[joint_type]
        return self

    def get_joint_type(self) -> float:
        return self.uniforms["joint_type"]

    # Points
    def set_anchors_and_handles(
        self,
        anchors: Vect3Array,
        handles: Vect3Array,
    ):
        assert(len(anchors) == len(handles) + 1)
        points = resize_array(self.get_points(), 2 * len(anchors) - 1)
        points[0::2] = anchors
        points[1::2] = handles
        self.set_points(points)
        return self

    def start_new_path(self, point: Vect3):
        # Path ends are signaled by a handle point sitting directly
        # on top of the previous anchor
        if self.has_points():
            self.append_points([self.get_last_point(), point])
        else:
            self.set_points([point])
        return self

    def add_cubic_bezier_curve(
        self,
        anchor1: Vect3,
        handle1: Vect3,
        handle2: Vect3,
        anchor2: Vect3
    ):
        self.add_subpath(get_quadratic_approximation_of_cubic(
            anchor1, handle1, handle2, anchor2
        ))
        return self

    def add_cubic_bezier_curve_to(
        self,
        handle1: Vect3,
        handle2: Vect3,
        anchor: Vect3,
    ):
        """
        Add cubic bezier curve to the path.
        """
        self.throw_error_if_no_points()
        last = self.get_last_point()
        # If the two relevant tangents are close in angle to each other,
        # then just approximate with a single quadratic bezier curve.
        # Otherwise, approximate with two
        v1 = handle1 - last
        v2 = anchor - handle2
        angle = angle_between_vectors(v1, v2)
        if self.use_simple_quadratic_approx and angle < 45 * DEGREES:
            quadratic_approx = [last, find_intersection(last, v1, anchor, -v2), anchor]
        else:
            quadratic_approx = get_quadratic_approximation_of_cubic(
                last, handle1, handle2, anchor
            )
        if self.consider_points_equal(quadratic_approx[1], last):
            # This is to prevent subpaths from accidentally being marked closed
            quadratic_approx[1] = midpoint(*quadratic_approx[1:3])
        self.append_points(quadratic_approx[1:])
        return self

    def add_quadratic_bezier_curve_to(self, handle: Vect3, anchor: Vect3):
        self.throw_error_if_no_points()
        last_point = self.get_last_point()
        if self.consider_points_equal(handle, last_point):
            # This is to prevent subpaths from accidentally being marked closed
            handle = midpoint(handle, anchor)
        self.append_points([handle, anchor])
        return self

    def add_line_to(self, point: Vect3):
        self.throw_error_if_no_points()
        last_point = self.get_last_point()
        alphas = np.linspace(0, 1, 5 if self.long_lines else 3)
        self.append_points(outer_interpolate(last_point, point, alphas[1:]))
        return self

    def add_smooth_curve_to(self, point: Vect3):
        if self.has_new_path_started():
            self.add_line_to(point)
        else:
            self.throw_error_if_no_points()
            new_handle = self.get_reflection_of_last_handle()
            self.add_quadratic_bezier_curve_to(new_handle, point)
        return self

    def add_smooth_cubic_curve_to(self, handle: Vect3, point: Vect3):
        self.throw_error_if_no_points()
        if self.get_num_points() == 1:
            new_handle = handle
        else:
            new_handle = self.get_reflection_of_last_handle()
        self.add_cubic_bezier_curve_to(new_handle, handle, point)

    def has_new_path_started(self) -> bool:
        points = self.get_points()
        if len(points) == 1:
            return True
        return self.consider_points_equal(points[-3], points[-2])

    def get_last_point(self) -> Vect3:
        return self.get_points()[-1]

    def get_reflection_of_last_handle(self) -> Vect3:
        points = self.get_points()
        return 2 * points[-1] - points[-2]

    def close_path(self, smooth: bool = False):
        if self.is_closed():
            return self
        last_path_start = self.get_subpaths()[-1][0]
        if smooth:
            self.add_smooth_curve_to(last_path_start)
        else:
            self.add_line_to(last_path_start)
        return self

    def is_closed(self) -> bool:
        points = self.get_points()
        return self.consider_points_equal(points[0], points[-1])

    def subdivide_curves_by_condition(
        self,
        tuple_to_subdivisions: Callable,
        recurse: bool = True
    ):
        for vmob in self.get_family(recurse):
            if not vmob.has_points():
                continue
            new_points = [vmob.get_points()[0]]
            for tup in vmob.get_bezier_tuples():
                n_divisions = tuple_to_subdivisions(*tup)
                if n_divisions > 0:
                    alphas = np.linspace(0, 1, n_divisions + 2)
                    new_points.extend([
                        partial_quadratic_bezier_points(tup, a1, a2)[1:]
                        for a1, a2 in zip(alphas, alphas[1:])
                    ])
                else:
                    new_points.append(tup[1:])
            vmob.set_points(np.vstack(new_points))
        return self

    def subdivide_sharp_curves(
        self,
        angle_threshold: float = 30 * DEGREES,
        recurse: bool = True
    ):
        def tuple_to_subdivisions(b0, b1, b2):
            angle = angle_between_vectors(b1 - b0, b2 - b1)
            return int(angle / angle_threshold)

        self.subdivide_curves_by_condition(tuple_to_subdivisions, recurse)
        return self

    def subdivide_intersections(self, recurse: bool = True, n_subdivisions: int = 1):
        path = self.get_anchors()
        def tuple_to_subdivisions(b0, b1, b2):
            if line_intersects_path(b0, b1, path):
                return n_subdivisions
            return 0

        self.subdivide_curves_by_condition(tuple_to_subdivisions, recurse)
        return self

    def add_points_as_corners(self, points: Iterable[Vect3]):
        for point in points:
            self.add_line_to(point)
        return points

    def set_points_as_corners(self, points: Iterable[Vect3]):
        anchors = np.array(points)
        handles = 0.5 * (anchors[:-1] + anchors[1:])
        self.set_anchors_and_handles(anchors, handles)
        return self

    def set_points_smoothly(
        self,
        points: Iterable[Vect3],
        true_smooth: bool = False
    ):
        self.set_points_as_corners(points)
        if true_smooth:
            self.make_smooth()
        else:
            self.make_approximately_smooth()
        return self

    def change_anchor_mode(self, mode: str):
        assert(mode in ("jagged", "approx_smooth", "true_smooth"))
        for submob in self.family_members_with_points():
            subpaths = submob.get_subpaths()
            new_points = []
            for subpath in subpaths:
                anchors = subpath[::2]
                new_subpath = np.array(subpath)
                if mode == "approx_smooth":
                    new_subpath[1::2] = get_smooth_quadratic_bezier_handle_points(anchors)
                elif mode == "true_smooth":
                    h1, h2 = get_smooth_cubic_bezier_handle_points(anchors)
                    # The format here is that each successive group of 5 points
                    # represents two quadratic bezier curves. We assume the end
                    # of one is the start of the next, so eliminate elements 5, 10, 15, etc.
                    quads = get_quadratic_approximation_of_cubic(anchors[:-1], h1, h2, anchors[1:])
                    is_start = (np.arange(len(quads)) % 5 == 0)
                    new_subpath = np.array([quads[0], *quads[~is_start]])
                elif mode == "jagged":
                    new_subpath[1::2] = 0.5 * (anchors[:-1] + anchors[1:])
                if new_points:
                    # Close previous path
                    new_points.append(new_points[-1][-1])
                new_points.append(new_subpath)
            submob.set_points(np.vstack(new_points))
            submob.refresh_triangulation()
        return self

    def make_smooth(self):
        """
        This will double the number of points in the mobject,
        so should not be called repeatedly.  It also means
        transforming between states before and after calling
        this might have strange artifacts
        """
        self.change_anchor_mode("true_smooth")
        return self

    def make_approximately_smooth(self):
        """
        Unlike make_smooth, this will not change the number of
        points, but it also does not result in a perfectly smooth
        curve.  It's most useful when the points have been
        sampled at a not-too-low rate from a continuous function,
        as in the case of ParametricCurve
        """
        self.change_anchor_mode("approx_smooth")
        return self

    def make_jagged(self):
        self.change_anchor_mode("jagged")
        return self

    def add_subpath(self, points: Vect3Array):
        assert(len(points) % 2 == 1)
        if not self.has_points():
            self.set_points(points)
            return self
        if not self.consider_points_equal(points[0], self.get_points()[-1]):
            self.start_new_path(points[0])
        self.append_points(points[1:])
        return self

    def append_vectorized_mobject(self, vmobject: VMobject):
        self.add_subpath(vmobject.get_points())
        return self

    #
    def consider_points_equal(self, p0: Vect3, p1: Vect3) -> bool:
        return get_norm(p1 - p0) < self.tolerance_for_point_equality

    # Information about the curve
    def get_bezier_tuples_from_points(self, points: Vect3Array) -> Iterable[Vect3Array]:
        n_curves = (len(points) - 1) // 2
        return (points[2 * i : 2 * i + 3] for i in range(n_curves))

    def get_bezier_tuples(self) -> Iterable[Vect3Array]:
        return self.get_bezier_tuples_from_points(self.get_points())

    def get_subpath_end_indices_from_points(self, points: Vect3Array):
        atol = self.tolerance_for_point_equality
        a0, h, a1 = points[0:-1:2], points[1::2], points[2::2]
        # An anchor point is considered the end of a path
        # if its following handle is sitting on top of it.
        # To disambiguate this from cases with many null
        # curves in a row, we also check that the following
        # anchor is genuinely distinct
        is_end = np.empty(len(points) // 2 + 1, dtype=bool)
        is_end[:-1] = (a0 == h).all(1) & (abs(h - a1) > atol).any(1)
        is_end[-1] = True
        # If the curve immediately after an end marker is also an
        # end marker, don't mark the second one
        is_end[:-1] = is_end[:-1] & ~is_end[1:]
        return np.array([2 * n for n, end in enumerate(is_end) if end])

    def get_subpath_end_indices(self):
        return self.get_subpath_end_indices_from_points(self.get_points())

    def get_subpaths_from_points(self, points: Vect3Array) -> list[Vect3Array]:
        end_indices = self.get_subpath_end_indices_from_points(points)
        start_indices = [0, *(end_indices[:-1] + 2)]
        return [points[i1:i2 + 1] for i1, i2 in zip(start_indices, end_indices)]

    def get_subpaths(self) -> list[Vect3Array]:
        return self.get_subpaths_from_points(self.get_points())

    def get_nth_curve_points(self, n: int) -> Vect3Array:
        assert(n < self.get_num_curves())
        return self.get_points()[2 * n : 2 * n + 3]

    def get_nth_curve_function(self, n: int) -> Callable[[float], Vect3]:
        return bezier(self.get_nth_curve_points(n))

    def get_num_curves(self) -> int:
        return self.get_num_points() // 2

    def quick_point_from_proportion(self, alpha: float) -> Vect3:
        # Assumes all curves have the same length, so is inaccurate
        num_curves = self.get_num_curves()
        n, residue = integer_interpolate(0, num_curves, alpha)
        curve_func = self.get_nth_curve_function(n)
        return curve_func(residue)

    def point_from_proportion(self, alpha: float) -> Vect3:
        if alpha <= 0:
            return self.get_start()
        elif alpha >= 1:
            return self.get_end()

        partials: list[float] = [0]
        for tup in self.get_bezier_tuples():
            if self.consider_points_equal(tup[0], tup[1]):
                # Don't consider null curves
                arclen = 0
            else:
                # Approximate length with straight line from start to end
                arclen = get_norm(tup[2] - tup[0])
            partials.append(partials[-1] + arclen)
        full = partials[-1]
        if full == 0:
            return self.get_start()
        # First index where the partial length is more than alpha times the full length
        i = next(
            (i for i, x in enumerate(partials) if x >= full * alpha),
            len(partials)  # Default
        )
        residue = float(inverse_interpolate(partials[i - 1] / full, partials[i] / full, alpha))
        return self.get_nth_curve_function(i - 1)(residue)

    def get_anchors_and_handles(self) -> list[Vect3]:
        """
        returns anchors1, handles, anchors2,
        where (anchors1[i], handles[i], anchors2[i])
        will be three points defining a quadratic bezier curve
        for any i in range(0, len(anchors1))
        """
        points = self.get_points()
        return [points[0:-1:2], points[1::2], points[2::2]]

    def get_start_anchors(self) -> Vect3Array:
        return self.get_points()[0:-1:2]

    def get_end_anchors(self) -> Vect3:
        return self.get_points()[2::2]

    def get_anchors(self) -> Vect3Array:
        return self.get_points()[::2]

    def get_points_without_null_curves(self, atol: float = 1e-9) -> Vect3Array:
        new_points = [self.get_points()[0]]
        for tup in self.get_bezier_tuples():
            if get_norm(tup[1] - tup[0]) > atol or get_norm(tup[2] - tup[0]) > atol:
                new_points.append(tup[1:])
        return np.vstack(new_points)

    def get_arc_length(self, n_sample_points: int | None = None) -> float:
        if n_sample_points is None:
            n_sample_points = 4 * self.get_num_curves() + 1
        points = np.array([
            self.point_from_proportion(a)
            for a in np.linspace(0, 1, n_sample_points)
        ])
        diffs = points[1:] - points[:-1]
        return sum(map(get_norm, diffs))

    def get_area_vector(self) -> Vect3:
        # Returns a vector whose length is the area bound by
        # the polygon formed by the anchor points, pointing
        # in a direction perpendicular to the polygon according
        # to the right hand rule.
        if not self.has_points():
            return np.zeros(3)

        p0 = self.get_anchors()
        p1 = np.vstack([p0[1:], p0[0]])

        # Each term goes through all edges [(x0, y0, z0), (x1, y1, z1)]
        sums = p0 + p1
        diffs = p1 - p0
        return 0.5 * np.array([
            (sums[:, 1] * diffs[:, 2]).sum(),  # Add up (y0 + y1)*(z1 - z0)
            (sums[:, 2] * diffs[:, 0]).sum(),  # Add up (z0 + z1)*(x1 - x0)
            (sums[:, 0] * diffs[:, 1]).sum(),  # Add up (x0 + x1)*(y1 - y0)
        ])

    def get_unit_normal(self) -> Vect3:
        if self.get_num_points() < 3:
            return OUT

        area_vect = self.get_area_vector()
        area = get_norm(area_vect)
        if area > 0:
            normal = area_vect / area
        else:
            points = self.get_points()
            normal = get_unit_normal(
                points[1] - points[0],
                points[2] - points[1],
            )
        return normal

    # Alignment
    def align_points(self, vmobject: VMobject):
        if self.get_num_points() == len(vmobject.get_points()):
            # If both have fill, and they have the same shape, just
            # give them the same triangulation so that it's not recalculated
            # needlessly throughout an animation
            if self.has_fill() and vmobject.has_fill() and self.has_same_shape_as(vmobject):
                vmobject.triangulation = self.triangulation
            return self

        for mob in self, vmobject:
            # If there are no points, add one to
            # where the "center" is
            if not mob.has_points():
                mob.start_new_path(mob.get_center())

        # Figure out what the subpaths are, and align
        subpaths1 = self.get_subpaths()
        subpaths2 = vmobject.get_subpaths()
        n_subpaths = max(len(subpaths1), len(subpaths2))

        # Start building new ones
        new_subpaths1 = []
        new_subpaths2 = []

        def get_nth_subpath(path_list, n):
            if n >= len(path_list):
                # Create a null path at the very end
                return [path_list[-1][-1]] * 3
            return path_list[n]

        for n in range(n_subpaths):
            sp1 = get_nth_subpath(subpaths1, n)
            sp2 = get_nth_subpath(subpaths2, n)
            diff1 = max(0, (len(sp2) - len(sp1)) // 2)
            diff2 = max(0, (len(sp1) - len(sp2)) // 2)
            sp1 = self.insert_n_curves_to_point_list(diff1, sp1)
            sp2 = self.insert_n_curves_to_point_list(diff2, sp2)
            if n > 0:
                # Add intermediate anchor to mark path end
                new_subpaths1.append(new_subpaths1[0][-1])
                new_subpaths2.append(new_subpaths2[0][-1])
            new_subpaths1.append(sp1)
            new_subpaths2.append(sp2)

        for mob, paths in [(self, new_subpaths1), (vmobject, new_subpaths2)]:
            new_points = np.vstack(paths)
            mob.resize_points(len(new_points), resize_func=resize_preserving_order)
            mob.set_points(new_points)
        return self

    def insert_n_curves(self, n: int, recurse: bool = True):
        for mob in self.get_family(recurse):
            if mob.get_num_curves() > 0:
                new_points = mob.insert_n_curves_to_point_list(n, mob.get_points())
                mob.set_points(new_points)
        return self

    def insert_n_curves_to_point_list(self, n: int, points: Vect3Array):
        if len(points) == 1:
            return np.repeat(points, 2 * n + 1, 0)

        bezier_tuples = list(self.get_bezier_tuples_from_points(points))
        atol = self.tolerance_for_point_equality
        norms = np.array([
            0 if get_norm(tup[1] - tup[0]) < atol else get_norm(tup[2] - tup[0])
            for tup in bezier_tuples
        ])
        total_norm = sum(norms)
        # Calculate insertions per curve (ipc)
        if total_norm < 1e-6:
            ipc = [n] + [0] * (len(bezier_tuples) - 1)
        else:
            ipc = np.round(n * norms / sum(norms)).astype(int)

        diff = n - sum(ipc)
        for x in range(diff):
            ipc[np.argmin(ipc)] += 1
        for x in range(-diff):
            ipc[np.argmax(ipc)] -= 1

        new_points = [points[0]]
        for tup, n_inserts in zip(bezier_tuples, ipc):
            # What was once a single quadratic curve defined
            # by "tup" will now be broken into n_inserts + 1
            # smaller quadratic curves
            alphas = np.linspace(0, 1, n_inserts + 2)
            for a1, a2 in zip(alphas, alphas[1:]):
                new_points.extend(partial_quadratic_bezier_points(tup, a1, a2)[1:])
        return np.vstack(new_points)

    def interpolate(
        self,
        mobject1: VMobject,
        mobject2: VMobject,
        alpha: float,
        *args, **kwargs
    ):
        super().interpolate(mobject1, mobject2, alpha, *args, **kwargs)
        if self.has_fill():
            tri1 = mobject1.get_triangulation()
            tri2 = mobject2.get_triangulation()
            if not arrays_match(tri1, tri2):
                self.refresh_triangulation()
        return self

    def pointwise_become_partial(self, vmobject: VMobject, a: float, b: float):
        assert(isinstance(vmobject, VMobject))
        vm_points = vmobject.get_points()
        if a <= 0 and b >= 1:
            self.set_points(vm_points, refresh=False)
            return self
        num_curves = vmobject.get_num_curves()

        # Partial curve includes three portions:
        # - A start, which is some ending portion of an inner quadratic
        # - A middle section, which matches the curve exactly
        # - An end, which is the starting portion of a later inner quadratic

        lower_index, lower_residue = integer_interpolate(0, num_curves, a)
        upper_index, upper_residue = integer_interpolate(0, num_curves, b)
        i1 = 2 * lower_index
        i2 = 2 * lower_index + 3
        i3 = 2 * upper_index
        i4 = 2 * upper_index + 3

        new_points = vm_points.copy()
        if num_curves == 0:
            new_points[:] = 0
            return self
        if lower_index == upper_index:
            tup = partial_quadratic_bezier_points(vm_points[i1:i2], lower_residue, upper_residue)
            new_points[:i1] = tup[0]
            new_points[i1:i4] = tup
            new_points[i4:] = tup[2]
        else:
            low_tup = partial_quadratic_bezier_points(vm_points[i1:i2], lower_residue, 1)
            high_tup = partial_quadratic_bezier_points(vm_points[i3:i4], 0, upper_residue)
            new_points[0:i1] = low_tup[0]
            new_points[i1:i2] = low_tup
            # Keep new_points i2:i3 as they are
            new_points[i3:i4] = high_tup
            new_points[i4:] = high_tup[2]
        self.set_points(new_points, refresh=False)
        if self.has_fill():
            self.refresh_triangulation()
        return self

    def get_subcurve(self, a: float, b: float) -> VMobject:
        vmob = self.copy()
        vmob.pointwise_become_partial(self, a, b)
        return vmob

    def get_outer_vert_indices(self):
        """
        Returns the pattern (0, 1, 2, 2, 3, 4, 4, 5, 6, ...)
        """
        n_curves = self.get_num_curves()
        if len(self.outer_vert_indices) != 3 * n_curves:
            self.outer_vert_indices = (np.arange(1, 3 * n_curves + 1) * 2) // 3
        return self.outer_vert_indices

    # Data for shaders that may need refreshing

    def refresh_triangulation(self):
        for mob in self.get_family():
            mob.needs_new_triangulation = True
        return self

    def get_triangulation(self):
        # Figure out how to triangulate the interior to know
        # how to send the points as to the vertex shader.
        # First triangles come directly from the points
        if not self.needs_new_triangulation:
            return self.triangulation

        points = self.get_points()

        if len(points) <= 1:
            self.triangulation = np.zeros(0, dtype='i4')
            self.needs_new_triangulation = False
            return self.triangulation

        normal_vector = self.get_unit_normal()

        # Rotate points such that unit normal vector is OUT
        if not np.isclose(normal_vector, OUT).all():
            points = np.dot(points, z_to_vector(normal_vector))


        v01s = points[1::2] - points[0:-1:2]
        v12s = points[2::2] - points[1::2]
        curve_orientations = np.sign(cross2d(v01s, v12s))

        # Reset orientation data
        self.data["orientation"][1::2, 0] = curve_orientations
        if "orientation" in self.locked_data_keys:
            self.locked_data_keys.remove("orientation")

        concave_parts = curve_orientations < 0

        # These are the vertices to which we'll apply a polygon triangulation
        indices = np.arange(len(points), dtype=int)
        inner_vert_indices = np.hstack([
            indices[0::2],
            indices[1::2][concave_parts],
        ])
        inner_vert_indices.sort()
        # Even indices correspond to anchors, and `end_indices // 2`
        # shows which anchors are considered end points
        end_indices = self.get_subpath_end_indices()
        counts = np.arange(1, len(inner_vert_indices) + 1)
        rings = counts[inner_vert_indices % 2 == 0][end_indices // 2]

        # Triangulate
        inner_verts = points[inner_vert_indices]
        inner_tri_indices = inner_vert_indices[
            earclip_triangulation(inner_verts, rings)
        ]
        # Remove null triangles, coming from adjascent points
        iti = inner_tri_indices
        null1 = (iti[0::3] + 1 == iti[1::3]) & (iti[0::3] + 2 == iti[2::3])
        null2 = (iti[0::3] - 1 == iti[1::3]) & (iti[0::3] - 2 == iti[2::3])
        inner_tri_indices = iti[~(null1 | null2).repeat(3)]

        outer_tri_indices = self.get_outer_vert_indices()
        tri_indices = np.hstack([outer_tri_indices, inner_tri_indices])
        self.triangulation = tri_indices
        self.needs_new_triangulation = False
        return tri_indices

    def refresh_joint_angles(self):
        for mob in self.get_family():
            mob.needs_new_joint_angles = True
        return self

    def get_joint_angles(self, refresh: bool = False):
        if not self.needs_new_joint_angles and not refresh:
            return self.data["joint_angle"]
        if "joint_angle" in self.locked_data_keys:
            return self.data["joint_angle"]

        self.needs_new_joint_angles = False

        points = self.get_points()

        if(len(points) < 3):
            return self.data["joint_angle"]

        # Unit tangent vectors
        a0, h, a1 = points[0:-1:2], points[1::2], points[2::2]
        a0_to_h = normalize_along_axis(h - a0, 1)
        h_to_a1 = normalize_along_axis(a1 - h, 1)

        vect_to_vert = np.zeros(points.shape)
        vect_from_vert = np.zeros(points.shape)

        vect_to_vert[1::2] = a0_to_h
        vect_to_vert[2::2] = h_to_a1
        vect_from_vert[0:-1:2] = a0_to_h
        vect_from_vert[1::2] = h_to_a1

        ends = self.get_subpath_end_indices()
        starts = [0, *(e + 2 for e in ends[:-1])]
        for start, end in zip(starts, ends):
            if start > len(a0_to_h):
                continue
            if self.consider_points_equal(points[start], points[end]):
                vect_to_vert[start] = h_to_a1[end // 2 - 1]
                vect_from_vert[end] = a0_to_h[start // 2]

        # Compute angles, and read them into
        # the joint_angles array
        result = self.data["joint_angle"][:, 0]
        dots = (vect_to_vert * vect_from_vert).sum(1)
        np.arccos(dots, out=result, where=((dots <= 1) & (dots >= -1)))
        # Assumes unit normal in the positive z direction
        result *= np.sign(cross2d(vect_to_vert, vect_from_vert))
        return result

    def triggers_refreshed_triangulation(func: Callable):
        @wraps(func)
        def wrapper(self, *args, refresh=True, **kwargs):
            func(self, *args, **kwargs)
            if refresh:
                self.refresh_triangulation()
                self.refresh_joint_angles()
        return wrapper

    @triggers_refreshed_triangulation
    def set_points(self, points: Vect3Array):
        assert(len(points) == 0 or len(points) % 2 == 1)
        super().set_points(points)
        return self

    @triggers_refreshed_triangulation
    def append_points(self, points: Vect3Array):
        assert(len(points) % 2 == 0)
        super().append_points(points)
        return self

    @triggers_refreshed_triangulation
    def reverse_points(self):
        # This will reset which anchors are
        # considered path ends
        if not self.has_points():
            return self
        inner_ends = self.get_subpath_end_indices()[:-1]
        self.data["point"][inner_ends + 1] = self.data["point"][inner_ends + 2]
        super().reverse_points()
        return self

    @triggers_refreshed_triangulation
    def set_data(self, data: np.ndarray):
        super().set_data(data)
        return self

    def resize_points(
        self,
        new_length: int,
        resize_func: Callable[[np.ndarray, int], np.ndarray] = resize_array
    ):
        super().resize_points(new_length, resize_func)
        self.data["vert_index"][:, 0] = np.arange(new_length)

    # TODO, how to be smart about tangents here?
    @triggers_refreshed_triangulation
    def apply_function(
        self,
        function: Callable[[Vect3], Vect3],
        make_smooth: bool = False,
        **kwargs
    ):
        super().apply_function(function, **kwargs)
        if self.make_smooth_after_applying_functions or make_smooth:
            self.make_approximately_smooth()
        return self

    def apply_points_function(self, *args, **kwargs,):
        super().apply_points_function(*args, **kwargs)
        self.refresh_joint_angles()

    # For shaders
    def init_shader_data(self):
        dtype = self.shader_dtype
        fill_dtype, stroke_dtype = (
            np.dtype([
                (name, dtype[name].base, dtype[name].shape)
                for name in names
            ])
            for names in [self.fill_data_names, self.stroke_data_names]
        )
        fill_data = np.zeros(0, dtype=fill_dtype)
        stroke_data = np.zeros(0, dtype=stroke_dtype)
        self.fill_shader_wrapper = ShaderWrapper(
            vert_data=fill_data,
            vert_indices=np.zeros(0, dtype='i4'),
            uniforms=self.uniforms,
            shader_folder=self.fill_shader_folder,
            render_primitive=self.fill_render_primitive,
        )
        self.stroke_shader_wrapper = ShaderWrapper(
            vert_data=stroke_data,
            uniforms=self.uniforms,
            shader_folder=self.stroke_shader_folder,
            render_primitive=self.stroke_render_primitive,
        )
        self.back_stroke_shader_wrapper = self.stroke_shader_wrapper.copy()

    def refresh_shader_wrapper_id(self):
        for wrapper in self.get_shader_wrapper_list():
            wrapper.refresh_id()
        return self

    def get_shader_wrapper_list(self) -> list[ShaderWrapper]:
        family = self.family_members_with_points()
        if not family:
            return []
        fill_names = self.fill_data_names
        stroke_names = self.stroke_data_names

        # Build up data lists
        fill_datas = []
        fill_indices = []
        stroke_datas = []
        back_stroke_data = []
        for submob in family:
            if submob.has_fill():
                fill_datas.append(submob.data[fill_names])
                fill_indices.append(submob.get_triangulation())
            if submob.has_stroke():
                if submob.stroke_behind:
                    lst = back_stroke_data
                else:
                    lst = stroke_datas
                lst.append(submob.data[stroke_names])
                # Set data array to be one longer than number of points,
                # with a dummy vertex added at the end. This is to ensure
                # it can be safely stacked onto other stroke data arrays.
                lst.append(submob.data[stroke_names][-1:])

        shader_wrappers = [
            self.back_stroke_shader_wrapper.read_in(back_stroke_data),
            self.fill_shader_wrapper.read_in(fill_datas, fill_indices),
            self.stroke_shader_wrapper.read_in(stroke_datas),
        ]

        for sw in shader_wrappers:
            # Assume uniforms of the first family member
            sw.uniforms = family[0].get_uniforms()
            sw.depth_test = family[0].depth_test
        return [sw for sw in shader_wrappers if len(sw.vert_data) > 0]

    def refresh_shader_data(self):
        for submob in self.get_family():
            submob.get_joint_angles()
        self.get_shader_wrapper_list()


class VGroup(VMobject):
    def __init__(self, *vmobjects: VMobject, **kwargs):
        super().__init__(**kwargs)
        self.add(*vmobjects)

    def __add__(self, other: VMobject | VGroup):
        assert(isinstance(other, VMobject))
        return self.add(other)


class VectorizedPoint(Point, VMobject):
    def __init__(
        self,
        location: np.ndarray = ORIGIN,
        color: ManimColor = BLACK,
        fill_opacity: float = 0.0,
        stroke_width: float = 0.0,
        **kwargs
    ):
        Point.__init__(self, location, **kwargs)
        VMobject.__init__(
            self,
            color=color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs
        )
        self.set_points(np.array([location]))


class CurvesAsSubmobjects(VGroup):
    def __init__(self, vmobject: VMobject, **kwargs):
        super().__init__(**kwargs)
        for tup in vmobject.get_bezier_tuples():
            part = VMobject()
            part.set_points(tup)
            part.match_style(vmobject)
            self.add(part)


class DashedVMobject(VMobject):
    def __init__(
        self,
        vmobject: VMobject,
        num_dashes: int = 15,
        positive_space_ratio: float = 0.5,
        **kwargs
    ):
        super().__init__(**kwargs)

        if num_dashes > 0:
            # End points of the unit interval for division
            alphas = np.linspace(0, 1, num_dashes + 1)

            # This determines the length of each "dash"
            full_d_alpha = (1.0 / num_dashes)
            partial_d_alpha = full_d_alpha * positive_space_ratio

            # Rescale so that the last point of vmobject will
            # be the end of the last dash
            alphas /= (1 - full_d_alpha + partial_d_alpha)

            self.add(*[
                vmobject.get_subcurve(alpha, alpha + partial_d_alpha)
                for alpha in alphas[:-1]
            ])
        # Family is already taken care of by get_subcurve
        # implementation
        self.match_style(vmobject, recurse=False)


class VHighlight(VGroup):
    def __init__(
        self,
        vmobject: VMobject,
        n_layers: int = 5,
        color_bounds: Tuple[ManimColor] = (GREY_C, GREY_E),
        max_stroke_addition: float = 5.0,
    ):
        outline = vmobject.replicate(n_layers)
        outline.set_fill(opacity=0)
        added_widths = np.linspace(0, max_stroke_addition, n_layers + 1)[1:]
        colors = color_gradient(color_bounds, n_layers)
        for part, added_width, color in zip(reversed(outline), added_widths, colors):
            for sm in part.family_members_with_points():
                sm.set_stroke(
                    width=sm.get_stroke_width() + added_width,
                    color=color,
                )
        super().__init__(*outline)
