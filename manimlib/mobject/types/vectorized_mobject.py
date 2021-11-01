import itertools as it
import operator as op
import moderngl

from functools import reduce, wraps

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.utils.bezier import bezier
from manimlib.utils.bezier import get_smooth_quadratic_bezier_handle_points
from manimlib.utils.bezier import get_smooth_cubic_bezier_handle_points
from manimlib.utils.bezier import get_quadratic_approximation_of_cubic
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import partial_quadratic_bezier_points
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.iterables import make_even
from manimlib.utils.iterables import resize_array
from manimlib.utils.iterables import resize_with_interpolation
from manimlib.utils.iterables import listify
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
        "fill_shader_folder": "quadratic_bezier_fill",
        # Could also be "bevel", "miter", "round"
        "joint_type": "auto",
        "flat_stroke": False,
        "render_primitive": moderngl.TRIANGLES,
        "fill_dtype": [
            ('point', np.float32, (3,)),
            ('unit_normal', np.float32, (3,)),
            ('color', np.float32, (4,)),
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
        self.needs_new_triangulation = True
        self.triangulation = np.zeros(0, dtype='i4')
        super().__init__(**kwargs)

    def get_group_class(self):
        return VGroup

    def init_data(self):
        super().init_data()
        self.data.pop("rgbas")
        self.data.update({
            "fill_rgba": np.zeros((1, 4)),
            "stroke_rgba": np.zeros((1, 4)),
            "stroke_width": np.zeros((1, 1)),
            "unit_normal": np.zeros((1, 3))
        })

    # Colors
    def init_colors(self):
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

    def set_rgba_array(self, rgba_array, name=None, recurse=False):
        if name is None:
            names = ["fill_rgba", "stroke_rgba"]
        else:
            names = [name]

        for name in names:
            super().set_rgba_array(rgba_array, name, recurse)
        return self

    def set_fill(self, color=None, opacity=None, recurse=True):
        self.set_rgba_array_by_color(color, opacity, 'fill_rgba', recurse)
        return self

    def set_stroke(self, color=None, width=None, opacity=None, background=None, recurse=True):
        self.set_rgba_array_by_color(color, opacity, 'stroke_rgba', recurse)

        if width is not None:
            for mob in self.get_family(recurse):
                if isinstance(width, np.ndarray):
                    arr = width.reshape((len(width), 1))
                else:
                    arr = np.array([[w] for w in listify(width)], dtype=float)
                mob.data['stroke_width'] = arr

        if background is not None:
            for mob in self.get_family(recurse):
                mob.draw_stroke_behind_fill = background
        return self

    def align_stroke_width_data_to_points(self, recurse=True):
        for mob in self.get_family(recurse):
            mob.data["stroke_width"] = resize_with_interpolation(
                mob.data["stroke_width"], len(mob.get_points())
            )

    def set_style(self,
                  fill_color=None,
                  fill_opacity=None,
                  fill_rgba=None,
                  stroke_color=None,
                  stroke_opacity=None,
                  stroke_rgba=None,
                  stroke_width=None,
                  stroke_background=True,
                  gloss=None,
                  shadow=None,
                  recurse=True):
        if fill_rgba is not None:
            self.data['fill_rgba'] = resize_with_interpolation(fill_rgba, len(fill_rgba))
        else:
            self.set_fill(
                color=fill_color,
                opacity=fill_opacity,
                recurse=recurse
            )

        if stroke_rgba is not None:
            self.data['stroke_rgba'] = resize_with_interpolation(stroke_rgba, len(fill_rgba))
            self.set_stroke(
                width=stroke_width,
                background=stroke_background,
            )
        else:
            self.set_stroke(
                color=stroke_color,
                width=stroke_width,
                opacity=stroke_opacity,
                recurse=recurse,
                background=stroke_background,
            )

        if gloss is not None:
            self.set_gloss(gloss, recurse=recurse)
        if shadow is not None:
            self.set_shadow(shadow, recurse=recurse)
        return self

    def get_style(self):
        return {
            "fill_rgba": self.data['fill_rgba'],
            "stroke_rgba": self.data['stroke_rgba'],
            "stroke_width": self.data['stroke_width'],
            "stroke_background": self.draw_stroke_behind_fill,
            "gloss": self.get_gloss(),
            "shadow": self.get_shadow(),
        }

    def match_style(self, vmobject, recurse=True):
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

    def set_color(self, color, recurse=True):
        self.set_fill(color, recurse=recurse)
        self.set_stroke(color, recurse=recurse)
        return self

    def set_opacity(self, opacity, recurse=True):
        self.set_fill(opacity=opacity, recurse=recurse)
        self.set_stroke(opacity=opacity, recurse=recurse)
        return self

    def fade(self, darkness=0.5, recurse=True):
        factor = 1.0 - darkness
        self.set_fill(
            opacity=factor * self.get_fill_opacity(),
            recurse=False,
        )
        self.set_stroke(
            opacity=factor * self.get_stroke_opacity(),
            recurse=False,
        )
        super().fade(darkness, recurse)
        return self

    def get_fill_colors(self):
        return [
            rgb_to_hex(rgba[:3])
            for rgba in self.data['fill_rgba']
        ]

    def get_fill_opacities(self):
        return self.data['fill_rgba'][:, 3]

    def get_stroke_colors(self):
        return [
            rgb_to_hex(rgba[:3])
            for rgba in self.data['stroke_rgba']
        ]

    def get_stroke_opacities(self):
        return self.data['stroke_rgba'][:, 3]

    def get_stroke_widths(self):
        return self.data['stroke_width'][:, 0]

    # TODO, it's weird for these to return the first of various lists
    # rather than the full information
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

    def get_stroke_color(self):
        return self.get_stroke_colors()[0]

    def get_stroke_width(self):
        return self.get_stroke_widths()[0]

    def get_stroke_opacity(self):
        return self.get_stroke_opacities()[0]

    def get_color(self):
        if self.has_stroke():
            return self.get_stroke_color()
        return self.get_fill_color()

    def has_stroke(self):
        return self.get_stroke_widths().any() and self.get_stroke_opacities().any()

    def has_fill(self):
        return any(self.get_fill_opacities())

    def get_opacity(self):
        if self.has_fill():
            return self.get_fill_opacity()
        return self.get_stroke_opacity()

    def set_flat_stroke(self, flat_stroke=True, recurse=True):
        for mob in self.get_family(recurse):
            mob.flat_stroke = flat_stroke
        return self

    def get_flat_stroke(self):
        return self.flat_stroke

    # Points
    def set_anchors_and_handles(self, anchors1, handles, anchors2):
        assert(len(anchors1) == len(handles) == len(anchors2))
        nppc = self.n_points_per_curve
        new_points = np.zeros((nppc * len(anchors1), self.dim))
        arrays = [anchors1, handles, anchors2]
        for index, array in enumerate(arrays):
            new_points[index::nppc] = array
        self.set_points(new_points)
        return self

    def start_new_path(self, point):
        assert(self.get_num_points() % self.n_points_per_curve == 0)
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
            self.get_last_point(), handle1, handle2, anchor
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
            self.append_points([self.get_last_point(), handle, anchor])

    def add_line_to(self, point):
        end = self.get_points()[-1]
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
        return self.get_num_points() % self.n_points_per_curve == 1

    def get_last_point(self):
        return self.get_points()[-1]

    def get_reflection_of_last_handle(self):
        points = self.get_points()
        return 2 * points[-1] - points[-2]

    def close_path(self):
        if not self.is_closed():
            self.add_line_to(self.get_subpaths()[-1][0])

    def is_closed(self):
        return self.consider_points_equals(
            self.get_points()[0], self.get_points()[-1]
        )

    def subdivide_sharp_curves(self, angle_threshold=30 * DEGREES, recurse=True):
        vmobs = [vm for vm in self.get_family(recurse) if vm.has_points()]
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
            vmob.set_points(np.vstack(new_points))
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

    def set_points_smoothly(self, points, true_smooth=False):
        self.set_points_as_corners(points)
        if true_smooth:
            self.make_smooth()
        else:
            self.make_approximately_smooth()
        return self

    def change_anchor_mode(self, mode):
        assert(mode in ("jagged", "approx_smooth", "true_smooth"))
        nppc = self.n_points_per_curve
        for submob in self.family_members_with_points():
            subpaths = submob.get_subpaths()
            submob.clear_points()
            for subpath in subpaths:
                anchors = np.vstack([subpath[::nppc], subpath[-1:]])
                new_subpath = np.array(subpath)
                if mode == "approx_smooth":
                    new_subpath[1::nppc] = get_smooth_quadratic_bezier_handle_points(anchors)
                elif mode == "true_smooth":
                    h1, h2 = get_smooth_cubic_bezier_handle_points(anchors)
                    new_subpath = get_quadratic_approximation_of_cubic(anchors[:-1], h1, h2, anchors[1:])
                elif mode == "jagged":
                    new_subpath[1::nppc] = 0.5 * (anchors[:-1] + anchors[1:])
                submob.append_points(new_subpath)
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

    def add_subpath(self, points):
        assert(len(points) % self.n_points_per_curve == 0)
        self.append_points(points)
        return self

    def append_vectorized_mobject(self, vectorized_mobject):
        new_points = list(vectorized_mobject.get_points())

        if self.has_new_path_started():
            # Remove last point, which is starting
            # a new path
            self.resize_data(len(self.get_points() - 1))
        self.append_points(new_points)
        return self

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
        return self.get_points()[nppc * n:nppc * (n + 1)]

    def get_nth_curve_function(self, n):
        return bezier(self.get_nth_curve_points(n))

    def get_num_curves(self):
        return self.get_num_points() // self.n_points_per_curve

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
        points = self.get_points()
        return [
            points[i::nppc]
            for i in range(nppc)
        ]

    def get_start_anchors(self):
        return self.get_points()[0::self.n_points_per_curve]

    def get_end_anchors(self):
        nppc = self.n_points_per_curve
        return self.get_points()[nppc - 1::nppc]

    def get_anchors(self):
        points = self.get_points()
        if len(points) == 1:
            return points
        return np.array(list(it.chain(*zip(
            self.get_start_anchors(),
            self.get_end_anchors(),
        ))))

    def get_points_without_null_curves(self, atol=1e-9):
        nppc = self.n_points_per_curve
        points = self.get_points()
        distinct_curves = reduce(op.or_, [
            (abs(points[i::nppc] - points[0::nppc]) > atol).any(1)
            for i in range(1, nppc)
        ])
        return points[distinct_curves.repeat(nppc)]

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
        if not self.has_points():
            return np.zeros(3)

        nppc = self.n_points_per_curve
        points = self.get_points()
        p0 = points[0::nppc]
        p1 = points[nppc - 1::nppc]

        # Each term goes through all edges [(x1, y1, z1), (x2, y2, z2)]
        return 0.5 * np.array([
            sum((p0[:, 1] + p1[:, 1]) * (p1[:, 2] - p0[:, 2])),  # Add up (y1 + y2)*(z2 - z1)
            sum((p0[:, 2] + p1[:, 2]) * (p1[:, 0] - p0[:, 0])),  # Add up (z1 + z2)*(x2 - x1)
            sum((p0[:, 0] + p1[:, 0]) * (p1[:, 1] - p0[:, 1])),  # Add up (x1 + x2)*(y2 - y1)
        ])

    def get_unit_normal(self, recompute=False):
        if not recompute:
            return self.data["unit_normal"][0]

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
        self.data["unit_normal"][:] = normal
        return normal

    def refresh_unit_normal(self):
        for mob in self.get_family():
            mob.get_unit_normal(recompute=True)
        return self

    # Alignment
    def align_points(self, vmobject):
        if self.get_num_points() == len(vmobject.get_points()):
            return

        for mob in self, vmobject:
            # If there are no points, add one to
            # where the "center" is
            if not mob.has_points():
                mob.start_new_path(mob.get_center())
            # If there's only one point, turn it into
            # a null curve
            if mob.has_new_path_started():
                mob.add_line_to(mob.get_points()[0])

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

    def insert_n_curves(self, n, recurse=True):
        for mob in self.get_family(recurse):
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

    def interpolate(self, mobject1, mobject2, alpha, *args, **kwargs):
        super().interpolate(mobject1, mobject2, alpha, *args, **kwargs)
        if self.has_fill():
            tri1 = mobject1.get_triangulation()
            tri2 = mobject2.get_triangulation()
            if len(tri1) != len(tri1) or not np.all(tri1 == tri2):
                self.refresh_triangulation()
        return self

    def pointwise_become_partial(self, vmobject, a, b):
        assert(isinstance(vmobject, VMobject))
        if a <= 0 and b >= 1:
            self.become(vmobject)
            return self
        num_curves = vmobject.get_num_curves()
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

        vm_points = vmobject.get_points()
        new_points = vm_points.copy()
        if num_curves == 0:
            new_points[:] = 0
            return self
        if lower_index == upper_index:
            tup = partial_quadratic_bezier_points(vm_points[i1:i2], lower_residue, upper_residue)
            new_points[:i1] = tup[0]
            new_points[i1:i4] = tup
            new_points[i4:] = tup[2]
            new_points[nppc:] = new_points[nppc - 1]
        else:
            low_tup = partial_quadratic_bezier_points(vm_points[i1:i2], lower_residue, 1)
            high_tup = partial_quadratic_bezier_points(vm_points[i3:i4], 0, upper_residue)
            new_points[0:i1] = low_tup[0]
            new_points[i1:i2] = low_tup
            # Keep new_points i2:i3 as they are
            new_points[i3:i4] = high_tup
            new_points[i4:] = high_tup[2]
        self.set_points(new_points)
        return self

    def get_subcurve(self, a, b):
        vmob = self.copy()
        vmob.pointwise_become_partial(self, a, b)
        return vmob

    # Related to triangulation

    def refresh_triangulation(self):
        for mob in self.get_family():
            mob.needs_new_triangulation = True
        return self

    def get_triangulation(self, normal_vector=None):
        # Figure out how to triangulate the interior to know
        # how to send the points as to the vertex shader.
        # First triangles come directly from the points
        if normal_vector is None:
            normal_vector = self.get_unit_normal(recompute=True)

        if not self.needs_new_triangulation:
            return self.triangulation

        points = self.get_points()

        if len(points) <= 1:
            self.triangulation = np.zeros(0, dtype='i4')
            self.needs_new_triangulation = False
            return self.triangulation

        if not np.isclose(normal_vector, OUT).all():
            # Rotate points such that unit normal vector is OUT
            points = np.dot(points, z_to_vector(normal_vector))
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
        inner_tri_indices = inner_vert_indices[
            earclip_triangulation(inner_verts, rings)
        ]

        tri_indices = np.hstack([indices, inner_tri_indices])
        self.triangulation = tri_indices
        self.needs_new_triangulation = False
        return tri_indices

    def triggers_refreshed_triangulation(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            old_points = self.get_points()
            func(self, *args, **kwargs)
            if not np.all(self.get_points() == old_points):
                self.refresh_unit_normal()
                self.refresh_triangulation()
        return wrapper

    @triggers_refreshed_triangulation
    def set_points(self, points):
        super().set_points(points)
        return self

    @triggers_refreshed_triangulation
    def set_data(self, data):
        super().set_data(data)
        return self

    # TODO, how to be smart about tangents here?
    @triggers_refreshed_triangulation
    def apply_function(self, function, make_smooth=False, **kwargs):
        super().apply_function(function, **kwargs)
        if self.make_smooth_after_applying_functions or make_smooth:
            self.make_approximately_smooth()
        return self

    def flip(self, *args, **kwargs):
        super().flip(*args, **kwargs)
        self.refresh_unit_normal()
        self.refresh_triangulation()
        return self

    # For shaders
    def init_shader_data(self):
        self.fill_data = np.zeros(0, dtype=self.fill_dtype)
        self.stroke_data = np.zeros(0, dtype=self.stroke_dtype)
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
        result = dict(super().get_shader_uniforms())
        result["joint_type"] = JOINT_TYPE_MAP[self.joint_type]
        result["flat_stroke"] = float(self.flat_stroke)
        return result

    def get_stroke_shader_data(self):
        points = self.get_points()
        if len(self.stroke_data) != len(points):
            self.stroke_data = resize_array(self.stroke_data, len(points))

        if "points" not in self.locked_data_keys:
            nppc = self.n_points_per_curve
            self.stroke_data["point"] = points
            self.stroke_data["prev_point"][:nppc] = points[-nppc:]
            self.stroke_data["prev_point"][nppc:] = points[:-nppc]
            self.stroke_data["next_point"][:-nppc] = points[nppc:]
            self.stroke_data["next_point"][-nppc:] = points[:nppc]

        self.read_data_to_shader(self.stroke_data, "color", "stroke_rgba")
        self.read_data_to_shader(self.stroke_data, "stroke_width", "stroke_width")
        self.read_data_to_shader(self.stroke_data, "unit_normal", "unit_normal")

        return self.stroke_data

    def get_fill_shader_data(self):
        points = self.get_points()
        if len(self.fill_data) != len(points):
            self.fill_data = resize_array(self.fill_data, len(points))
            self.fill_data["vert_index"][:, 0] = range(len(points))

        self.read_data_to_shader(self.fill_data, "point", "points")
        self.read_data_to_shader(self.fill_data, "color", "fill_rgba")
        self.read_data_to_shader(self.fill_data, "unit_normal", "unit_normal")

        return self.fill_data

    def refresh_shader_data(self):
        self.get_fill_shader_data()
        self.get_stroke_shader_data()

    def get_fill_shader_vert_indices(self):
        return self.get_triangulation()


class VGroup(VMobject):
    def __init__(self, *vmobjects, **kwargs):
        if not all([isinstance(m, VMobject) for m in vmobjects]):
            raise Exception("All submobjects must be of type VMobject")
        super().__init__(**kwargs)
        self.add(*vmobjects)
    
    def __add__(self:'VGroup', other : 'VMobject' or 'VGroup'):
        assert(isinstance(other, VMobject))
        return self.add(other)


class VectorizedPoint(Point, VMobject):
    CONFIG = {
        "color": BLACK,
        "fill_opacity": 0,
        "stroke_width": 0,
        "artificial_width": 0.01,
        "artificial_height": 0.01,
    }

    def __init__(self, location=ORIGIN, **kwargs):
        super().__init__(**kwargs)
        self.set_points(np.array([location]))


class CurvesAsSubmobjects(VGroup):
    def __init__(self, vmobject, **kwargs):
        super().__init__(**kwargs)
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
        super().__init__(**kwargs)
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
        self.match_style(vmobject, recurse=False)
