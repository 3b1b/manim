import itertools as it
import operator as op
import moderngl

from colour import Color
from functools import reduce

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.utils.bezier import bezier
from manimlib.utils.bezier import get_smooth_quadratic_bezier_handle_points
from manimlib.utils.bezier import get_smooth_cubic_bezier_handle_points
from manimlib.utils.bezier import get_quadratic_approximation_of_cubic
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import set_array_by_interpolation
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import partial_quadratic_bezier_points
from manimlib.utils.color import color_to_rgba
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.iterables import make_even
from manimlib.utils.iterables import stretch_array_to_length
from manimlib.utils.iterables import stretch_array_to_length_with_interpolation
from manimlib.utils.iterables import listify
from manimlib.utils.paths import straight_path
from manimlib.utils.space_ops import angle_between_vectors
from manimlib.utils.space_ops import cross2d
from manimlib.utils.space_ops import earclip_triangulation
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import get_unit_normal
from manimlib.utils.space_ops import z_to_vector
from manimlib.shader_wrapper import ShaderWrapper


class VMobject(Mobject):
    CONFIG = {
        "fill_color": None,
        "fill_opacity": 0.0,
        "stroke_color": None,
        "stroke_opacity": 1.0,
        "stroke_width": DEFAULT_STROKE_WIDTH,
        "draw_stroke_behind_fill": False,
        # Indicates that it will not be displayed, but
        # that it should count in parent mobject's path
        "pre_function_handle_to_anchor_scale_factor": 0.01,
        "make_smooth_after_applying_functions": False,
        "background_image_file": None,
        # This is within a pixel
        # TODO, do we care about accounting for
        # varying zoom levels?
        "tolerance_for_point_equality": 1e-8,
        "n_points_per_curve": 3,
        "long_lines": False,
        # For shaders
        "stroke_shader_folder": "quadratic_bezier_stroke",
        # "stroke_vert_shader_file": "quadratic_bezier_stroke_vert.glsl",
        # "stroke_geom_shader_file": "quadratic_bezier_stroke_geom.glsl",
        # "stroke_frag_shader_file": "quadratic_bezier_stroke_frag.glsl",
        "fill_shader_folder": "quadratic_bezier_fill",
        # "fill_vert_shader_file": "quadratic_bezier_fill_vert.glsl",
        # "fill_geom_shader_file": "quadratic_bezier_fill_geom.glsl",
        # "fill_frag_shader_file": "quadratic_bezier_fill_frag.glsl",
        # Could also be Bevel, Miter, Round
        "joint_type": "auto",
        "flat_stroke": True,
        "render_primitive": moderngl.TRIANGLES,
        "triangulation_locked": False,
        "fill_dtype": [
            ('point', np.float32, (3,)),
            ('unit_normal', np.float32, (3,)),
            ('color', np.float32, (4,)),
            # ('fill_all', np.float32, (1,)),
            ('vert_index', np.float32, (1,)),
        ],
        "stroke_dtype": [
            ("point", np.float32, (3,)),
            ("prev_point", np.float32, (3,)),
            ("next_point", np.float32, (3,)),
            ('unit_normal', np.float32, (3,)),
            ("stroke_width", np.float32, (1,)),
            ("color", np.float32, (4,)),
        ]
    }

    def __init__(self, **kwargs):
        self.unit_normal_locked = False
        self.triangulation_locked = False
        super().__init__(**kwargs)
        self.lock_unit_normal(family=False)
        self.lock_triangulation(family=False)

    def get_group_class(self):
        return VGroup

    # Colors
    def init_colors(self):
        self.fill_rgbas = np.zeros((1, 4))
        self.stroke_rgbas = np.zeros((1, 4))
        self.set_fill(
            color=self.fill_color or self.color,
            opacity=self.fill_opacity,
        )
        self.set_stroke(
            color=self.stroke_color or self.color,
            width=self.stroke_width,
            opacity=self.stroke_opacity,
            background=self.draw_stroke_behind_fill,
        )
        self.set_gloss(self.gloss)
        self.set_flat_stroke(self.flat_stroke)
        return self

    def generate_rgba_array(self, color, opacity):
        """
        First arg can be either a color, or a tuple/list of colors.
        Likewise, opacity can either be a float, or a tuple of floats.
        """
        colors = listify(color)
        opacities = listify(opacity)
        return np.array([
            color_to_rgba(c, o)
            for c, o in zip(*make_even(colors, opacities))
        ])

    def update_rgbas_array(self, array_name, color, opacity):
        rgbas = self.generate_rgba_array(color or BLACK, opacity or 0)
        # Match up current rgbas array with the newly calculated
        # one. 99% of the time they'll be the same.
        curr_rgbas = getattr(self, array_name)
        if len(curr_rgbas) < len(rgbas):
            curr_rgbas = stretch_array_to_length(curr_rgbas, len(rgbas))
            setattr(self, array_name, curr_rgbas)
        elif len(rgbas) < len(curr_rgbas):
            rgbas = stretch_array_to_length(rgbas, len(curr_rgbas))
        # Only update rgb if color was not None, and only
        # update alpha channel if opacity was passed in
        if color is not None:
            curr_rgbas[:, :3] = rgbas[:, :3]
        if opacity is not None:
            curr_rgbas[:, 3] = rgbas[:, 3]
        return self

    def set_fill(self, color=None, opacity=None, family=True):
        if family:
            for sm in self.submobjects:
                sm.set_fill(color, opacity, family)
        self.update_rgbas_array("fill_rgbas", color, opacity)
        return self

    def set_stroke(self, color=None, width=None, opacity=None,
                   background=None, family=True):
        if family:
            for sm in self.submobjects:
                sm.set_stroke(color, width, opacity, background, family)
        self.update_rgbas_array("stroke_rgbas", color, opacity)
        if width is not None:
            self.stroke_width = np.array(listify(width), dtype=float)
        if background is not None:
            self.draw_stroke_behind_fill = background
        return self

    def set_style(self,
                  fill_color=None,
                  fill_opacity=None,
                  fill_rgbas=None,
                  stroke_color=None,
                  stroke_opacity=None,
                  stroke_rgbas=None,
                  stroke_width=None,
                  gloss=None,
                  shadow=None,
                  background_image_file=None,
                  family=True):
        if fill_rgbas is not None:
            self.fill_rgbas = np.array(fill_rgbas)
        else:
            self.set_fill(
                color=fill_color,
                opacity=fill_opacity,
                family=family
            )

        if stroke_rgbas is not None:
            self.stroke_rgbas = np.array(stroke_rgbas)
            if stroke_width is not None:
                self.stroke_width = np.array(listify(stroke_width))
        else:
            self.set_stroke(
                color=stroke_color,
                width=stroke_width,
                opacity=stroke_opacity,
                family=family,
            )

        if gloss is not None:
            self.set_gloss(gloss, family=family)
        if shadow is not None:
            self.set_shadow(shadow, family=family)
        if background_image_file:
            self.color_using_background_image(background_image_file)
        return self

    def get_style(self):
        return {
            "fill_rgbas": self.get_fill_rgbas(),
            "stroke_rgbas": self.get_stroke_rgbas(),
            "stroke_width": self.stroke_width,
            "gloss": self.get_gloss(),
            "shadow": self.get_shadow(),
            "background_image_file": self.get_background_image_file(),
        }

    def match_style(self, vmobject, family=True):
        for name, value in vmobject.get_style().items():
            if isinstance(value, np.ndarray):
                curr = getattr(self, name)
                if curr.size == value.size:
                    curr[:] = value[:]
                else:
                    setattr(self, name, np.array(value))
            else:
                setattr(self, name, value)

        if family:
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

    def set_color(self, color, family=True):
        self.set_fill(color, family=family)
        self.set_stroke(color, family=family)
        return self

    def set_opacity(self, opacity, family=True):
        self.set_fill(opacity=opacity, family=family)
        self.set_stroke(opacity=opacity, family=family)
        return self

    def fade(self, darkness=0.5, family=True):
        factor = 1.0 - darkness
        self.set_fill(
            opacity=factor * self.get_fill_opacity(),
            family=False,
        )
        self.set_stroke(
            opacity=factor * self.get_stroke_opacity(),
            family=False,
        )
        super().fade(darkness, family)
        return self

    def get_fill_rgbas(self):
        try:
            return self.fill_rgbas
        except AttributeError:
            return np.zeros((1, 4))

    def get_fill_color(self):
        """
        If there are multiple colors (for gradient)
        this returns the first one
        """
        return self.get_fill_colors()[0]

    def get_fill_opacity(self):
        """
        If there are multiple opacities, this returns the
        first
        """
        return self.get_fill_opacities()[0]

    def get_fill_colors(self):
        return [
            Color(rgb=rgba[:3])
            for rgba in self.get_fill_rgbas()
        ]

    def get_fill_opacities(self):
        return self.get_fill_rgbas()[:, 3]

    def get_stroke_rgbas(self):
        try:
            return self.stroke_rgbas
        except AttributeError:
            return np.zeros((1, 4))

    # TODO, it's weird for these to return the first of various lists
    # rather than the full information
    def get_stroke_color(self):
        return self.get_stroke_colors()[0]

    def get_stroke_width(self):
        return self.stroke_width[0]

    def get_stroke_opacity(self):
        return self.get_stroke_opacities()[0]

    def get_stroke_colors(self):
        return [
            rgb_to_hex(rgba[:3])
            for rgba in self.get_stroke_rgbas()
        ]

    def get_stroke_opacities(self):
        return self.get_stroke_rgbas()[:, 3]

    def get_color(self):
        if np.all(self.get_fill_opacities() == 0):
            return self.get_stroke_color()
        return self.get_fill_color()

    def has_stroke(self):
        if len(self.stroke_width) == 1:
            if self.stroke_width == 0:
                return False
        elif not self.stroke_width.any():
            return False
        alphas = self.stroke_rgbas[:, 3]
        if len(alphas) == 1:
            return alphas[0] > 0
        return alphas.any()

    def has_fill(self):
        alphas = self.fill_rgbas[:, 3]
        if len(alphas) == 1:
            return alphas[0] > 0
        return alphas.any()

    def get_opacity(self):
        if self.has_fill():
            return self.get_fill_opacity()
        return self.get_stroke_opacity()

    def set_flat_stroke(self, flat_stroke=True, family=True):
        self.flat_stroke = flat_stroke
        if family:
            for submob in self.submobjects:
                submob.set_flat_stroke(flat_stroke, family)
        return self

    def get_flat_stroke(self):
        return self.flat_stroke

    # TODO, this currently does nothing
    def color_using_background_image(self, background_image_file):
        self.background_image_file = background_image_file
        self.set_color(WHITE)
        for submob in self.submobjects:
            submob.color_using_background_image(background_image_file)
        return self

    def get_background_image_file(self):
        return self.background_image_file

    def match_background_image_file(self, vmobject):
        self.color_using_background_image(vmobject.get_background_image_file())
        return self

    def stretched_style_array_matching_points(self, array):
        new_len = self.get_num_points()
        long_arr = stretch_array_to_length_with_interpolation(
            array, 1 + 2 * (new_len // 3)
        )
        shape = array.shape
        if len(shape) > 1:
            result = np.zeros((new_len, shape[1]))
        else:
            result = np.zeros(new_len)
        result[0::3] = long_arr[0:-1:2]
        result[1::3] = long_arr[1::2]
        result[2::3] = long_arr[2::2]
        return result

    # Points
    def set_points(self, points):
        super().set_points(points)
        self.refresh_triangulation()
        return self

    def get_points(self):
        # TODO, shouldn't points always be a numpy array anyway?
        return np.array(self.points)

    def set_anchors_and_handles(self, anchors1, handles, anchors2):
        assert(len(anchors1) == len(handles) == len(anchors2))
        nppc = self.n_points_per_curve
        self.points = np.zeros((nppc * len(anchors1), self.dim))
        arrays = [anchors1, handles, anchors2]
        for index, array in enumerate(arrays):
            self.points[index::nppc] = array
        return self

    def clear_points(self):
        self.points = np.zeros((0, self.dim))

    def append_points(self, new_points):
        # TODO, check that number new points is a multiple of 4?
        # or else that if len(self.points) % 4 == 1, then
        # len(new_points) % 4 == 3?
        self.points = np.vstack([self.points, new_points])
        return self

    def start_new_path(self, point):
        assert(len(self.points) % self.n_points_per_curve == 0)
        self.append_points([point])
        return self

    def add_cubic_bezier_curve(self, anchor1, handle1, handle2, anchor2):
        new_points = get_quadratic_approximation_of_cubic(anchor1, handle1, handle2, anchor2)
        self.append_points(new_points)

    def add_cubic_bezier_curve_to(self, handle1, handle2, anchor):
        """
        Add cubic bezier curve to the path.
        """
        self.throw_error_if_no_points()
        quadratic_approx = get_quadratic_approximation_of_cubic(
            self.points[-1], handle1, handle2, anchor
        )
        if self.has_new_path_started():
            self.append_points(quadratic_approx[1:])
        else:
            self.append_points(quadratic_approx)

    def add_quadratic_bezier_curve_to(self, handle, anchor):
        self.throw_error_if_no_points()
        if self.has_new_path_started():
            self.append_points([handle, anchor])
        else:
            self.append_points([self.points[-1], handle, anchor])

    def add_line_to(self, point):
        end = self.points[-1]
        alphas = np.linspace(0, 1, self.n_points_per_curve)
        if self.long_lines:
            halfway = interpolate(end, point, 0.5)
            points = [
                interpolate(end, halfway, a)
                for a in alphas
            ] + [
                interpolate(halfway, point, a)
                for a in alphas
            ]
        else:
            points = [
                interpolate(end, point, a)
                for a in alphas
            ]
        if self.has_new_path_started():
            points = points[1:]
        self.append_points(points)
        return self

    def add_smooth_curve_to(self, point):
        if self.has_new_path_started():
            self.add_line_to(point)
        else:
            self.throw_error_if_no_points()
            new_handle = self.get_reflection_of_last_handle()
            self.add_quadratic_bezier_curve_to(new_handle, point)
        return self

    def add_smooth_cubic_curve_to(self, handle, point):
        self.throw_error_if_no_points()
        new_handle = self.get_reflection_of_last_handle()
        self.add_cubic_bezier_curve_to(new_handle, handle, point)

    def has_new_path_started(self):
        return len(self.points) % self.n_points_per_curve == 1

    def get_last_point(self):
        return self.points[-1]

    def get_reflection_of_last_handle(self):
        return 2 * self.points[-1] - self.points[-2]

    def close_path(self):
        if not self.is_closed():
            self.add_line_to(self.get_subpaths()[-1][0])

    def is_closed(self):
        return self.consider_points_equals(
            self.points[0], self.points[-1]
        )

    def subdivide_sharp_curves(self, angle_threshold=30 * DEGREES, family=True):
        if family:
            vmobs = self.family_members_with_points()
        else:
            vmobs = [self] if self.has_points() else []

        for vmob in vmobs:
            new_points = []
            for tup in vmob.get_bezier_tuples():
                angle = angle_between_vectors(tup[1] - tup[0], tup[2] - tup[1])
                if angle > angle_threshold:
                    n = int(np.ceil(angle / angle_threshold))
                    alphas = np.linspace(0, 1, n + 1)
                    new_points.extend([
                        partial_quadratic_bezier_points(tup, a1, a2)
                        for a1, a2 in zip(alphas, alphas[1:])
                    ])
                else:
                    new_points.append(tup)
            vmob.points = np.vstack(new_points)
        return self

    def add_points_as_corners(self, points):
        for point in points:
            self.add_line_to(point)
        return points

    def set_points_as_corners(self, points):
        nppc = self.n_points_per_curve
        points = np.array(points)
        self.set_anchors_and_handles(*[
            interpolate(points[:-1], points[1:], a)
            for a in np.linspace(0, 1, nppc)
        ])
        return self

    def set_points_smoothly(self, points):
        self.set_points_as_corners(points)
        self.make_smooth()
        return self

    def change_anchor_mode(self, mode):
        assert(mode in ["jagged", "smooth"])
        nppc = self.n_points_per_curve
        for submob in self.family_members_with_points():
            subpaths = submob.get_subpaths()
            submob.clear_points()
            for subpath in subpaths:
                anchors = np.vstack([subpath[::nppc], subpath[-1:]])
                new_subpath = np.array(subpath)
                if mode == "smooth":
                    # TOOD, it's not clear which of the two options below should be the default,
                    # leaving option 1 here commented out as a temporary note.
                    # Option 1:
                    # new_subpath[1::nppc] = get_smooth_quadratic_bezier_handle_points(anchors)
                    # Option 2:
                    h1, h2 = get_smooth_cubic_bezier_handle_points(anchors)
                    new_subpath = get_quadratic_approximation_of_cubic(anchors[:-1], h1, h2, anchors[1:])
                elif mode == "jagged":
                    new_subpath[1::nppc] = 0.5 * (anchors[:-1] + anchors[1:])
                submob.append_points(new_subpath)
            submob.refresh_triangulation()
        return self

    def make_smooth(self):
        # TODO, Change this to not rely on a cubic-to-quadratic conversion
        return self.change_anchor_mode("smooth")

    def make_jagged(self):
        return self.change_anchor_mode("jagged")

    def add_subpath(self, points):
        assert(len(points) % self.n_points_per_curve == 0)
        self.append_points(points)

    def append_vectorized_mobject(self, vectorized_mobject):
        new_points = list(vectorized_mobject.points)

        if self.has_new_path_started():
            # Remove last point, which is starting
            # a new path
            self.points = self.points[:-1]
        self.append_points(new_points)

    # TODO, how to be smart about tangents here?
    def apply_function(self, function):
        Mobject.apply_function(self, function)
        if self.make_smooth_after_applying_functions:
            self.make_smooth()
        self.refresh_triangulation()
        return self

    def flip(self, *args, **kwargs):
        super().flip(*args, **kwargs)
        self.refresh_unit_normal()
        self.refresh_triangulation()

    #
    def consider_points_equals(self, p0, p1):
        return get_norm(p1 - p0) < self.tolerance_for_point_equality

    # Information about the curve
    def get_bezier_tuples_from_points(self, points):
        nppc = self.n_points_per_curve
        remainder = len(points) % nppc
        points = points[:len(points) - remainder]
        return [
            points[i:i + nppc]
            for i in range(0, len(points), nppc)
        ]

    def get_bezier_tuples(self):
        return self.get_bezier_tuples_from_points(self.get_points())

    def get_subpaths_from_points(self, points):
        nppc = self.n_points_per_curve
        diffs = points[nppc - 1:-1:nppc] - points[nppc::nppc]
        splits = (diffs * diffs).sum(1) > self.tolerance_for_point_equality
        split_indices = np.arange(nppc, len(points), nppc, dtype=int)[splits]

        # split_indices = filter(
        #     lambda n: not self.consider_points_equals(points[n - 1], points[n]),
        #     range(nppc, len(points), nppc)
        # )
        split_indices = [0, *split_indices, len(points)]
        return [
            points[i1:i2]
            for i1, i2 in zip(split_indices, split_indices[1:])
            if (i2 - i1) >= nppc
        ]

    def get_subpaths(self):
        return self.get_subpaths_from_points(self.get_points())

    def get_nth_curve_points(self, n):
        assert(n < self.get_num_curves())
        nppc = self.n_points_per_curve
        return self.points[nppc * n:nppc * (n + 1)]

    def get_nth_curve_function(self, n):
        return bezier(self.get_nth_curve_points(n))

    def get_num_curves(self):
        return len(self.points) // self.n_points_per_curve

    def point_from_proportion(self, alpha):
        num_curves = self.get_num_curves()
        n, residue = integer_interpolate(0, num_curves, alpha)
        curve_func = self.get_nth_curve_function(n)
        return curve_func(residue)

    def get_anchors_and_handles(self):
        """
        returns anchors1, handles, anchors2,
        where (anchors1[i], handles[i], anchors2[i])
        will be three points defining a quadratic bezier curve
        for any i in range(0, len(anchors1))
        """
        nppc = self.n_points_per_curve
        return [
            self.points[i::nppc]
            for i in range(nppc)
        ]

    def get_start_anchors(self):
        return self.points[0::self.n_points_per_curve]

    def get_end_anchors(self):
        nppc = self.n_points_per_curve
        return self.points[nppc - 1::nppc]

    def get_anchors(self):
        if len(self.points) == 1:
            return self.points
        return np.array(list(it.chain(*zip(
            self.get_start_anchors(),
            self.get_end_anchors(),
        ))))

    def get_points_without_null_curves(self, atol=1e-9):
        nppc = self.n_points_per_curve
        distinct_curves = reduce(op.or_, [
            (abs(self.points[i::nppc] - self.points[0::nppc]) > atol).any(1)
            for i in range(1, nppc)
        ])
        return self.points[distinct_curves.repeat(nppc)]

    def get_arc_length(self, n_sample_points=None):
        if n_sample_points is None:
            n_sample_points = 4 * self.get_num_curves() + 1
        points = np.array([
            self.point_from_proportion(a)
            for a in np.linspace(0, 1, n_sample_points)
        ])
        diffs = points[1:] - points[:-1]
        norms = np.array([get_norm(d) for d in diffs])
        return norms.sum()

    def get_area_vector(self):
        # Returns a vector whose length is the area bound by
        # the polygon formed by the anchor points, pointing
        # in a direction perpendicular to the polygon according
        # to the right hand rule.
        if self.has_no_points():
            return np.zeros(3)

        nppc = self.n_points_per_curve
        p0 = self.points[0::nppc]
        p1 = self.points[nppc - 1::nppc]

        # Each term goes through all edges [(x1, y1, z1), (x2, y2, z2)]
        return 0.5 * np.array([
            sum((p0[:, 1] + p1[:, 1]) * (p1[:, 2] - p0[:, 2])),  # Add up (y1 + y2)*(z2 - z1)
            sum((p0[:, 2] + p1[:, 2]) * (p1[:, 0] - p0[:, 0])),  # Add up (z1 + z2)*(x2 - x1)
            sum((p0[:, 0] + p1[:, 0]) * (p1[:, 1] - p0[:, 1])),  # Add up (x1 + x2)*(y2 - y1)
        ])

    def get_unit_normal(self):
        if self.unit_normal_locked:
            return self.saved_unit_normal

        if len(self.points) < 3:
            return OUT

        area_vect = self.get_area_vector()
        area = get_norm(area_vect)
        if area > 0:
            return area_vect / area
        else:
            return get_unit_normal(
                self.points[1] - self.points[0],
                self.points[2] - self.points[1],
            )

    def lock_unit_normal(self, family=True):
        mobs = self.get_family() if family else [self]
        for mob in mobs:
            mob.unit_normal_locked = False
            mob.saved_unit_normal = mob.get_unit_normal()
            mob.unit_normal_locked = True
        return self

    def unlock_unit_normal(self):
        for mob in self.get_family():
            self.unit_normal_locked = False
        return self

    def refresh_unit_normal(self):
        for mob in self.get_family():
            mob.unit_normal_locked = False
            mob.saved_unit_normal = mob.get_unit_normal()
            mob.unit_normal_locked = True
        return self

    # Alignment
    def align_points(self, vmobject):
        self.align_rgbas(vmobject)
        if len(self.points) == len(vmobject.points):
            return

        for mob in self, vmobject:
            # If there are no points, add one to
            # where the "center" is
            if mob.has_no_points():
                mob.start_new_path(mob.get_center())
            # If there's only one point, turn it into
            # a null curve
            if mob.has_new_path_started():
                mob.add_line_to(mob.points[0])

        # Figure out what the subpaths are, and align
        subpaths1 = self.get_subpaths()
        subpaths2 = vmobject.get_subpaths()
        n_subpaths = max(len(subpaths1), len(subpaths2))
        # Start building new ones
        new_subpaths1 = []
        new_subpaths2 = []

        nppc = self.n_points_per_curve

        def get_nth_subpath(path_list, n):
            if n >= len(path_list):
                # Create a null path at the very end
                return [path_list[-1][-1]] * nppc
            return path_list[n]

        for n in range(n_subpaths):
            sp1 = get_nth_subpath(subpaths1, n)
            sp2 = get_nth_subpath(subpaths2, n)
            diff1 = max(0, (len(sp2) - len(sp1)) // nppc)
            diff2 = max(0, (len(sp1) - len(sp2)) // nppc)
            sp1 = self.insert_n_curves_to_point_list(diff1, sp1)
            sp2 = self.insert_n_curves_to_point_list(diff2, sp2)
            new_subpaths1.append(sp1)
            new_subpaths2.append(sp2)
        self.set_points(np.vstack(new_subpaths1))
        vmobject.set_points(np.vstack(new_subpaths2))
        return self

    def insert_n_curves(self, n, family=True):
        mobs = self.get_family() if family else [self]
        for mob in mobs:
            if mob.get_num_curves() > 0:
                new_points = mob.insert_n_curves_to_point_list(n, mob.get_points())
                # TODO, this should happen in insert_n_curves_to_point_list
                if mob.has_new_path_started():
                    new_points = np.vstack([new_points, mob.get_last_point()])
                mob.set_points(new_points)
        return self

    def insert_n_curves_to_point_list(self, n, points):
        nppc = self.n_points_per_curve
        if len(points) == 1:
            return np.repeat(points, nppc * n, 0)

        bezier_groups = self.get_bezier_tuples_from_points(points)
        norms = np.array([
            get_norm(bg[nppc - 1] - bg[0])
            for bg in bezier_groups
        ])
        total_norm = sum(norms)
        # Calculate insertions per curve (ipc)
        if total_norm < 1e-6:
            ipc = [n] + [0] * (len(bezier_groups) - 1)
        else:
            ipc = np.round(n * norms / sum(norms)).astype(int)

        diff = n - sum(ipc)
        for x in range(diff):
            ipc[np.argmin(ipc)] += 1
        for x in range(-diff):
            ipc[np.argmax(ipc)] -= 1

        new_points = []
        for group, n_inserts in zip(bezier_groups, ipc):
            # What was once a single quadratic curve defined
            # by "group" will now be broken into n_inserts + 1
            # smaller quadratic curves
            alphas = np.linspace(0, 1, n_inserts + 2)
            for a1, a2 in zip(alphas, alphas[1:]):
                new_points += partial_quadratic_bezier_points(group, a1, a2)
        return np.vstack(new_points)

    def align_rgbas(self, vmobject):
        attrs = ["fill_rgbas", "stroke_rgbas"]
        for attr in attrs:
            a1 = getattr(self, attr)
            a2 = getattr(vmobject, attr)
            if len(a1) > len(a2):
                new_a2 = stretch_array_to_length(a2, len(a1))
                setattr(vmobject, attr, new_a2)
            elif len(a2) > len(a1):
                new_a1 = stretch_array_to_length(a1, len(a2))
                setattr(self, attr, new_a1)
        return self

    def interpolate_color(self, mobject1, mobject2, alpha):
        attrs = [
            "fill_rgbas",
            "stroke_rgbas",
            "stroke_width",
        ]
        for attr in attrs:
            set_array_by_interpolation(
                getattr(self, attr),
                getattr(mobject1, attr),
                getattr(mobject2, attr),
                alpha
            )

    def pointwise_become_partial(self, vmobject, a, b):
        assert(isinstance(vmobject, VMobject))
        self.points[:] = vmobject.points[:]
        if a <= 0 and b >= 1:
            return self
        num_curves = self.get_num_curves()
        nppc = self.n_points_per_curve

        # Partial curve includes three portions:
        # - A middle section, which matches the curve exactly
        # - A start, which is some ending portion of an inner quadratic
        # - An end, which is the starting portion of a later inner quadratic

        lower_index, lower_residue = integer_interpolate(0, num_curves, a)
        upper_index, upper_residue = integer_interpolate(0, num_curves, b)
        i1 = nppc * lower_index
        i2 = nppc * (lower_index + 1)
        i3 = nppc * upper_index
        i4 = nppc * (upper_index + 1)

        if num_curves == 0:
            self.points[:] = 0
            return self
        if lower_index == upper_index:
            tup = partial_quadratic_bezier_points(vmobject.points[i1:i2], lower_residue, upper_residue)
            self.points[:i1] = tup[0]
            self.points[i1:i4] = tup
            self.points[i4:] = tup[2]
            self.points[nppc:] = self.points[nppc - 1]
        else:
            low_tup = partial_quadratic_bezier_points(vmobject.points[i1:i2], lower_residue, 1)
            high_tup = partial_quadratic_bezier_points(vmobject.points[i3:i4], 0, upper_residue)
            self.points[0:i1] = low_tup[0]
            self.points[i1:i2] = low_tup
            # Keep points i2:i3 as they are
            self.points[i3:i4] = high_tup
            self.points[i4:] = high_tup[2]
        return self

    def get_subcurve(self, a, b):
        vmob = self.copy()
        vmob.pointwise_become_partial(self, a, b)
        return vmob

    def interpolate(self, mobject1, mobject2, alpha, path_func=straight_path):
        super().interpolate(mobject1, mobject2, alpha, path_func)
        if not np.all(mobject1.get_triangulation() == mobject2.get_triangulation()):
            self.refresh_triangulation()
        return self

    # For shaders
    def init_shader_data(self):
        self.fill_data = np.zeros(len(self.points), dtype=self.fill_dtype)
        self.stroke_data = np.zeros(len(self.points), dtype=self.stroke_dtype)
        self.fill_shader_wrapper = ShaderWrapper(
            vert_data=self.fill_data,
            vert_indices=np.zeros(0, dtype='i4'),
            shader_folder=self.fill_shader_folder,
            render_primitive=self.render_primitive,
        )
        self.stroke_shader_wrapper = ShaderWrapper(
            vert_data=self.stroke_data,
            shader_folder=self.stroke_shader_folder,
            render_primitive=self.render_primitive,
        )

    def refresh_shader_wrapper_id(self):
        for wrapper in [self.fill_shader_wrapper, self.stroke_shader_wrapper]:
            wrapper.refresh_id()
        return self

    def get_fill_shader_wrapper(self):
        self.fill_shader_wrapper.vert_data = self.get_fill_shader_data()
        self.fill_shader_wrapper.vert_indices = self.get_fill_shader_vert_indices()
        self.fill_shader_wrapper.uniforms = self.get_shader_uniforms()
        self.fill_shader_wrapper.depth_test = self.depth_test
        return self.fill_shader_wrapper

    def get_stroke_shader_wrapper(self):
        self.stroke_shader_wrapper.vert_data = self.get_stroke_shader_data()
        self.stroke_shader_wrapper.uniforms = self.get_stroke_uniforms()
        self.stroke_shader_wrapper.depth_test = self.depth_test
        return self.stroke_shader_wrapper

    def get_shader_wrapper_list(self):
        # Build up data lists
        fill_shader_wrappers = []
        stroke_shader_wrappers = []
        back_stroke_shader_wrappers = []
        for submob in self.family_members_with_points():
            if submob.has_fill():
                fill_shader_wrappers.append(submob.get_fill_shader_wrapper())
            if submob.has_stroke():
                ssw = submob.get_stroke_shader_wrapper()
                if submob.draw_stroke_behind_fill:
                    back_stroke_shader_wrappers.append(ssw)
                else:
                    stroke_shader_wrappers.append(ssw)

        # Combine data lists
        wrapper_lists = [
            back_stroke_shader_wrappers,
            fill_shader_wrappers,
            stroke_shader_wrappers
        ]
        result = []
        for wlist in wrapper_lists:
            if wlist:
                wrapper = wlist[0]
                wrapper.combine_with(*wlist[1:])
                result.append(wrapper)
        return result

    def get_stroke_uniforms(self):
        result = super().get_shader_uniforms()
        result["joint_type"] = JOINT_TYPE_MAP[self.joint_type]
        result["flat_stroke"] = float(self.flat_stroke)
        return result

    def get_stroke_shader_data(self):
        rgbas = self.get_stroke_rgbas()
        if len(rgbas) > 1:
            rgbas = self.stretched_style_array_matching_points(rgbas)

        stroke_width = self.stroke_width
        if len(stroke_width) > 1:
            stroke_width = self.stretched_style_array_matching_points(stroke_width)

        points = self.points
        nppc = self.n_points_per_curve

        data = self.get_blank_shader_data_array(len(points), "stroke_data")
        data["point"] = points
        data["prev_point"][:nppc] = points[-nppc:]
        data["prev_point"][nppc:] = points[:-nppc]
        data["next_point"][:-nppc] = points[nppc:]
        data["next_point"][-nppc:] = points[:nppc]
        data["unit_normal"] = self.get_unit_normal()
        data["stroke_width"][:, 0] = stroke_width
        data["color"] = rgbas
        return data

    def lock_triangulation(self, family=True):
        mobs = self.get_family() if family else [self]
        for mob in mobs:
            mob.triangulation_locked = False
            mob.saved_triangulation = mob.get_triangulation()
            mob.triangulation_locked = True
        return self

    def unlock_triangulation(self):
        for sm in self.get_family():
            sm.triangulation_locked = False
        return self

    def refresh_triangulation(self):
        for mob in self.get_family():
            if mob.triangulation_locked:
                mob.triangulation_locked = False
                mob.saved_triangulation = mob.get_triangulation()
                mob.triangulation_locked = True
        return self

    def get_triangulation(self, normal_vector=None):
        # Figure out how to triangulate the interior to know
        # how to send the points as to the vertex shader.
        # First triangles come directly from the points
        if normal_vector is None:
            normal_vector = self.get_unit_normal()

        if self.triangulation_locked:
            return self.saved_triangulation

        if len(self.points) <= 1:
            return np.zeros(0, dtype='i4')

        # Rotate points such that unit normal vector is OUT
        # TODO, 99% of the time this does nothing.  Do a check for that?
        points = np.dot(self.points, z_to_vector(normal_vector))
        indices = np.arange(len(points), dtype=int)

        b0s = points[0::3]
        b1s = points[1::3]
        b2s = points[2::3]
        v01s = b1s - b0s
        v12s = b2s - b1s

        crosses = cross2d(v01s, v12s)
        convexities = np.sign(crosses)

        atol = self.tolerance_for_point_equality
        end_of_loop = np.zeros(len(b0s), dtype=bool)
        end_of_loop[:-1] = (np.abs(b2s[:-1] - b0s[1:]) > atol).any(1)
        end_of_loop[-1] = True

        concave_parts = convexities < 0

        # These are the vertices to which we'll apply a polygon triangulation
        inner_vert_indices = np.hstack([
            indices[0::3],
            indices[1::3][concave_parts],
            indices[2::3][end_of_loop],
        ])
        inner_vert_indices.sort()
        rings = np.arange(1, len(inner_vert_indices) + 1)[inner_vert_indices % 3 == 2]

        # Triangulate
        inner_verts = points[inner_vert_indices]
        inner_tri_indices = inner_vert_indices[earclip_triangulation(inner_verts, rings)]

        tri_indices = np.hstack([indices, inner_tri_indices])
        return tri_indices

    def get_fill_shader_data(self):
        points = self.points
        n_points = len(points)
        unit_normal = self.get_unit_normal()

        # TODO, best way to enable multiple colors?
        rgbas = self.get_fill_rgbas()[:1]

        data = self.get_blank_shader_data_array(n_points, "fill_data")
        data["point"] = points
        data["unit_normal"] = unit_normal
        data["color"] = rgbas
        data["vert_index"][:, 0] = range(n_points)
        return data

    def get_fill_shader_vert_indices(self):
        return self.get_triangulation()


class VGroup(VMobject):
    def __init__(self, *vmobjects, **kwargs):
        if not all([isinstance(m, VMobject) for m in vmobjects]):
            raise Exception("All submobjects must be of type VMobject")
        VMobject.__init__(self, **kwargs)
        self.add(*vmobjects)


class VectorizedPoint(VMobject, Point):
    CONFIG = {
        "color": BLACK,
        "fill_opacity": 0,
        "stroke_width": 0,
        "artificial_width": 0.01,
        "artificial_height": 0.01,
    }

    def __init__(self, location=ORIGIN, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points(np.array([location]))


class CurvesAsSubmobjects(VGroup):
    def __init__(self, vmobject, **kwargs):
        VGroup.__init__(self, **kwargs)
        for tup in vmobject.get_bezier_tuples():
            part = VMobject()
            part.set_points(tup)
            part.match_style(vmobject)
            self.add(part)


class DashedVMobject(VMobject):
    CONFIG = {
        "num_dashes": 15,
        "positive_space_ratio": 0.5,
        "color": WHITE
    }

    def __init__(self, vmobject, **kwargs):
        VMobject.__init__(self, **kwargs)
        num_dashes = self.num_dashes
        ps_ratio = self.positive_space_ratio
        if num_dashes > 0:
            # End points of the unit interval for division
            alphas = np.linspace(0, 1, num_dashes + 1)

            # This determines the length of each "dash"
            full_d_alpha = (1.0 / num_dashes)
            partial_d_alpha = full_d_alpha * ps_ratio

            # Rescale so that the last point of vmobject will
            # be the end of the last dash
            alphas /= (1 - full_d_alpha + partial_d_alpha)

            self.add(*[
                vmobject.get_subcurve(alpha, alpha + partial_d_alpha)
                for alpha in alphas[:-1]
            ])
        # Family is already taken care of by get_subcurve
        # implementation
        self.match_style(vmobject, family=False)
