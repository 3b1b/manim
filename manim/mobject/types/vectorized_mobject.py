"""Mobjects that use vector graphics."""


__all__ = [
    "VMobject",
    "VGroup",
    "VDict",
    "VectorizedPoint",
    "CurvesAsSubmobjects",
    "DashedVMobject",
]


import itertools as it
import sys
import colour

from ...constants import *
from ...mobject.mobject import Mobject
from ...mobject.three_d_utils import get_3d_vmob_gradient_start_and_end_points
from ...utils.bezier import bezier
from ...utils.bezier import get_smooth_handle_points
from ...utils.bezier import interpolate
from ...utils.bezier import integer_interpolate
from ...utils.bezier import partial_bezier_points
from ...utils.color import color_to_rgba, BLACK, WHITE
from ...utils.iterables import make_even
from ...utils.iterables import stretch_array_to_length
from ...utils.iterables import tuplify
from ...utils.simple_functions import clip_in_place
from ...utils.space_ops import rotate_vector
from ...utils.space_ops import get_norm
from ...utils.space_ops import shoelace_direction

# TODO
# - Change cubic curve groups to have 4 points instead of 3
# - Change sub_path idea accordingly
# - No more mark_paths_closed, instead have the camera test
#   if last point in close to first point
# - Think about length of self.points.  Always 0 or 1 mod 4?
#   That's kind of weird.


class VMobject(Mobject):
    CONFIG = {
        "fill_color": None,
        "fill_opacity": 0.0,
        "stroke_color": None,
        "stroke_opacity": 1.0,
        "stroke_width": DEFAULT_STROKE_WIDTH,
        # The purpose of background stroke is to have
        # something that won't overlap the fill, e.g.
        # For text against some textured background
        "background_stroke_color": BLACK,
        "background_stroke_opacity": 1.0,
        "background_stroke_width": 0,
        # When a color c is set, there will be a second color
        # computed based on interpolating c to WHITE by with
        # sheen_factor, and the display will gradient to this
        # secondary color in the direction of sheen_direction.
        "sheen_factor": 0.0,
        "sheen_direction": UL,
        # Indicates that it will not be displayed, but
        # that it should count in parent mobject's path
        "close_new_points": False,
        "pre_function_handle_to_anchor_scale_factor": 0.01,
        "make_smooth_after_applying_functions": False,
        "background_image_file": None,
        "shade_in_3d": False,
        # This is within a pixel
        # TODO, do we care about accounting for
        # varying zoom levels?
        "tolerance_for_point_equality": 1e-6,
        "n_points_per_cubic_curve": 4,
    }

    def get_group_class(self):
        return VGroup

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
        )
        self.set_background_stroke(
            color=self.background_stroke_color,
            width=self.background_stroke_width,
            opacity=self.background_stroke_opacity,
        )
        self.set_sheen(
            factor=self.sheen_factor,
            direction=self.sheen_direction,
        )
        return self

    def generate_rgbas_array(self, color, opacity):
        """
        First arg can be either a color, or a tuple/list of colors.
        Likewise, opacity can either be a float, or a tuple of floats.
        If self.sheen_factor is not zero, and only
        one color was passed in, a second slightly light color
        will automatically be added for the gradient
        """
        colors = list(tuplify(color))
        opacities = list(tuplify(opacity))
        rgbas = np.array(
            [color_to_rgba(c, o) for c, o in zip(*make_even(colors, opacities))]
        )

        sheen_factor = self.get_sheen_factor()
        if sheen_factor != 0 and len(rgbas) == 1:
            light_rgbas = np.array(rgbas)
            light_rgbas[:, :3] += sheen_factor
            clip_in_place(light_rgbas, 0, 1)
            rgbas = np.append(rgbas, light_rgbas, axis=0)
        return rgbas

    def update_rgbas_array(self, array_name, color=None, opacity=None):
        passed_color = color if (color is not None) else BLACK
        passed_opacity = opacity if (opacity is not None) else 0
        rgbas = self.generate_rgbas_array(passed_color, passed_opacity)
        if not hasattr(self, array_name):
            setattr(self, array_name, rgbas)
            return self
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
            for submobject in self.submobjects:
                submobject.set_fill(color, opacity, family)
        self.update_rgbas_array("fill_rgbas", color, opacity)
        return self

    def set_stroke(
        self, color=None, width=None, opacity=None, background=False, family=True
    ):
        if family:
            for submobject in self.submobjects:
                submobject.set_stroke(color, width, opacity, background, family)
        if background:
            array_name = "background_stroke_rgbas"
            width_name = "background_stroke_width"
        else:
            array_name = "stroke_rgbas"
            width_name = "stroke_width"
        self.update_rgbas_array(array_name, color, opacity)
        if width is not None:
            setattr(self, width_name, width)
        return self

    def set_background_stroke(self, **kwargs):
        kwargs["background"] = True
        self.set_stroke(**kwargs)
        return self

    def set_style(
        self,
        fill_color=None,
        fill_opacity=None,
        stroke_color=None,
        stroke_width=None,
        stroke_opacity=None,
        background_stroke_color=None,
        background_stroke_width=None,
        background_stroke_opacity=None,
        sheen_factor=None,
        sheen_direction=None,
        background_image_file=None,
        family=True,
    ):
        self.set_fill(color=fill_color, opacity=fill_opacity, family=family)
        self.set_stroke(
            color=stroke_color,
            width=stroke_width,
            opacity=stroke_opacity,
            family=family,
        )
        self.set_background_stroke(
            color=background_stroke_color,
            width=background_stroke_width,
            opacity=background_stroke_opacity,
            family=family,
        )
        if sheen_factor:
            self.set_sheen(
                factor=sheen_factor,
                direction=sheen_direction,
                family=family,
            )
        if background_image_file:
            self.color_using_background_image(background_image_file)
        return self

    def get_style(self, simple=False):
        ret = {
            "stroke_opacity": self.get_stroke_opacity(),
            "stroke_width": self.get_stroke_width(),
        }

        if simple:
            ret["fill_color"] = colour.rgb2hex(self.get_fill_color().get_rgb())
            ret["fill_opacity"] = self.get_fill_opacity()
            ret["stroke_color"] = colour.rgb2hex(self.get_stroke_color().get_rgb())
        else:
            ret["fill_color"] = self.get_fill_colors()
            ret["fill_opacity"] = self.get_fill_opacities()
            ret["stroke_color"] = self.get_stroke_colors()
            ret["background_stroke_color"] = self.get_stroke_colors(background=True)
            ret["background_stroke_width"] = self.get_stroke_width(background=True)
            ret["background_stroke_opacity"] = self.get_stroke_opacity(background=True)
            ret["sheen_factor"] = self.get_sheen_factor()
            ret["sheen_direction"] = self.get_sheen_direction()
            ret["background_image_file"] = self.get_background_image_file()

        return ret

    def match_style(self, vmobject, family=True):
        self.set_style(**vmobject.get_style(), family=False)

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
        self.color = colour.Color(color)
        return self

    def set_opacity(self, opacity, family=True):
        self.set_fill(opacity=opacity, family=family)
        self.set_stroke(opacity=opacity, family=family)
        self.set_stroke(opacity=opacity, family=family, background=True)
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
        self.set_background_stroke(
            opacity=factor * self.get_stroke_opacity(background=True),
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
        return [colour.Color(rgb=rgba[:3]) for rgba in self.get_fill_rgbas()]

    def get_fill_opacities(self):
        return self.get_fill_rgbas()[:, 3]

    def get_stroke_rgbas(self, background=False):
        try:
            if background:
                rgbas = self.background_stroke_rgbas
            else:
                rgbas = self.stroke_rgbas
            return rgbas
        except AttributeError:
            return np.zeros((1, 4))

    def get_stroke_color(self, background=False):
        return self.get_stroke_colors(background)[0]

    def get_stroke_width(self, background=False):
        if background:
            width = self.background_stroke_width
        else:
            width = self.stroke_width
        return max(0, width)

    def get_stroke_opacity(self, background=False):
        return self.get_stroke_opacities(background)[0]

    def get_stroke_colors(self, background=False):
        return [
            colour.Color(rgb=rgba[:3]) for rgba in self.get_stroke_rgbas(background)
        ]

    def get_stroke_opacities(self, background=False):
        return self.get_stroke_rgbas(background)[:, 3]

    def get_color(self):
        if np.all(self.get_fill_opacities() == 0):
            return self.get_stroke_color()
        return self.get_fill_color()

    def set_sheen_direction(self, direction, family=True):
        direction = np.array(direction)
        if family:
            for submob in self.get_family():
                submob.sheen_direction = direction
        else:
            self.sheen_direction = direction
        return self

    def set_sheen(self, factor, direction=None, family=True):
        if family:
            for submob in self.submobjects:
                submob.set_sheen(factor, direction, family)
        self.sheen_factor = factor
        if direction is not None:
            # family set to false because recursion will
            # already be handled above
            self.set_sheen_direction(direction, family=False)
        # Reset color to put sheen_factor into effect
        if factor != 0:
            self.set_stroke(self.get_stroke_color(), family=family)
            self.set_fill(self.get_fill_color(), family=family)
        return self

    def get_sheen_direction(self):
        return np.array(self.sheen_direction)

    def get_sheen_factor(self):
        return self.sheen_factor

    def get_gradient_start_and_end_points(self):
        if self.shade_in_3d:
            return get_3d_vmob_gradient_start_and_end_points(self)
        else:
            direction = self.get_sheen_direction()
            c = self.get_center()
            bases = np.array(
                [self.get_edge_center(vect) - c for vect in [RIGHT, UP, OUT]]
            ).transpose()
            offset = np.dot(bases, direction)
            return (c - offset, c + offset)

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

    def set_shade_in_3d(self, value=True, z_index_as_group=False):
        for submob in self.get_family():
            submob.shade_in_3d = value
            if z_index_as_group:
                submob.z_index_group = self
        return self

    # Points
    def set_points(self, points):
        self.points = np.array(points)
        return self

    def get_points(self):
        return np.array(self.points)

    def set_anchors_and_handles(self, anchors1, handles1, handles2, anchors2):
        assert len(anchors1) == len(handles1) == len(handles2) == len(anchors2)
        nppcc = self.n_points_per_cubic_curve  # 4
        total_len = nppcc * len(anchors1)
        self.points = np.zeros((total_len, self.dim))
        arrays = [anchors1, handles1, handles2, anchors2]
        for index, array in enumerate(arrays):
            self.points[index::nppcc] = array
        return self

    def clear_points(self):
        self.points = np.zeros((0, self.dim))

    def append_points(self, new_points):
        # TODO, check that number new points is a multiple of 4?
        # or else that if len(self.points) % 4 == 1, then
        # len(new_points) % 4 == 3?
        self.points = np.append(self.points, new_points, axis=0)
        return self

    def start_new_path(self, point):
        # TODO, make sure that len(self.points) % 4 == 0?
        self.append_points([point])
        return self

    def add_cubic_bezier_curve(self, anchor1, handle1, handle2, anchor2):
        # TODO, check the len(self.points) % 4 == 0?
        self.append_points([anchor1, handle1, handle2, anchor2])

    def add_cubic_bezier_curve_to(self, handle1, handle2, anchor):
        """
        Add cubic bezier curve to the path.
        """
        self.throw_error_if_no_points()
        new_points = [handle1, handle2, anchor]
        if self.has_new_path_started():
            self.append_points(new_points)
        else:
            self.append_points([self.get_last_point()] + new_points)

    def add_line_to(self, point):
        nppcc = self.n_points_per_cubic_curve
        self.add_cubic_bezier_curve_to(
            *[
                interpolate(self.get_last_point(), point, a)
                for a in np.linspace(0, 1, nppcc)[1:]
            ]
        )
        return self

    def add_smooth_curve_to(self, *points):
        """
        If two points are passed in, the first is intepretted
        as a handle, the second as an anchor
        """
        if len(points) == 1:
            handle2 = None
            new_anchor = points[0]
        elif len(points) == 2:
            handle2, new_anchor = points
        else:
            name = sys._getframe(0).f_code.co_name
            raise ValueError("Only call {} with 1 or 2 points".format(name))

        if self.has_new_path_started():
            self.add_line_to(new_anchor)
        else:
            self.throw_error_if_no_points()
            last_h2, last_a2 = self.points[-2:]
            last_tangent = last_a2 - last_h2
            handle1 = last_a2 + last_tangent
            if handle2 is None:
                to_anchor_vect = new_anchor - last_a2
                new_tangent = rotate_vector(last_tangent, PI, axis=to_anchor_vect)
                handle2 = new_anchor - new_tangent
            self.append_points([last_a2, handle1, handle2, new_anchor])
        return self

    def has_new_path_started(self):
        nppcc = self.n_points_per_cubic_curve  # 4
        return len(self.points) % nppcc == 1

    def get_last_point(self):
        return self.points[-1]

    def is_closed(self):
        return self.consider_points_equals(self.points[0], self.points[-1])

    def add_points_as_corners(self, points):
        for point in points:
            self.add_line_to(point)
        return points

    def set_points_as_corners(self, points):
        nppcc = self.n_points_per_cubic_curve
        points = np.array(points)
        self.set_anchors_and_handles(
            *[interpolate(points[:-1], points[1:], a) for a in np.linspace(0, 1, nppcc)]
        )
        return self

    def set_points_smoothly(self, points):
        self.set_points_as_corners(points)
        self.make_smooth()
        return self

    def change_anchor_mode(self, mode):
        assert mode in ["jagged", "smooth"]
        nppcc = self.n_points_per_cubic_curve
        for submob in self.family_members_with_points():
            subpaths = submob.get_subpaths()
            submob.clear_points()
            for subpath in subpaths:
                anchors = np.append(subpath[::nppcc], subpath[-1:], 0)
                if mode == "smooth":
                    h1, h2 = get_smooth_handle_points(anchors)
                elif mode == "jagged":
                    a1 = anchors[:-1]
                    a2 = anchors[1:]
                    h1 = interpolate(a1, a2, 1.0 / 3)
                    h2 = interpolate(a1, a2, 2.0 / 3)
                new_subpath = np.array(subpath)
                new_subpath[1::nppcc] = h1
                new_subpath[2::nppcc] = h2
                submob.append_points(new_subpath)
        return self

    def make_smooth(self):
        return self.change_anchor_mode("smooth")

    def make_jagged(self):
        return self.change_anchor_mode("jagged")

    def add_subpath(self, points):
        assert len(points) % 4 == 0
        self.points = np.append(self.points, points, axis=0)
        return self

    def append_vectorized_mobject(self, vectorized_mobject):
        new_points = list(vectorized_mobject.points)

        if self.has_new_path_started():
            # Remove last point, which is starting
            # a new path
            self.points = self.points[:-1]
        self.append_points(new_points)

    def apply_function(self, function):
        factor = self.pre_function_handle_to_anchor_scale_factor
        self.scale_handle_to_anchor_distances(factor)
        Mobject.apply_function(self, function)
        self.scale_handle_to_anchor_distances(1.0 / factor)
        if self.make_smooth_after_applying_functions:
            self.make_smooth()
        return self

    def scale_handle_to_anchor_distances(self, factor):
        """
        If the distance between a given handle point H and its associated
        anchor point A is d, then it changes H to be a distances factor*d
        away from A, but so that the line from A to H doesn't change.
        This is mostly useful in the context of applying a (differentiable)
        function, to preserve tangency properties.  One would pull all the
        handles closer to their anchors, apply the function then push them out
        again.
        """
        for submob in self.family_members_with_points():
            if len(submob.points) < self.n_points_per_cubic_curve:
                continue
            a1, h1, h2, a2 = submob.get_anchors_and_handles()
            a1_to_h1 = h1 - a1
            a2_to_h2 = h2 - a2
            new_h1 = a1 + factor * a1_to_h1
            new_h2 = a2 + factor * a2_to_h2
            submob.set_anchors_and_handles(a1, new_h1, new_h2, a2)
        return self

    #
    def consider_points_equals(self, p0, p1):
        return np.allclose(p0, p1, atol=self.tolerance_for_point_equality)

    def consider_points_equals_2d(self, p0, p1):
        """
        Determine if two points are close enough to be considered equal.

        This uses the algorithm from np.isclose(), but expanded here for the
        2D point case. NumPy is overkill for such a small question.
        """
        rtol = 1.0e-5  # default from np.isclose()
        atol = self.tolerance_for_point_equality
        if abs(p0[0] - p1[0]) > atol + rtol * abs(p1[0]):
            return False
        if abs(p0[1] - p1[1]) > atol + rtol * abs(p1[1]):
            return False
        return True

    # Information about line
    def get_cubic_bezier_tuples_from_points(self, points):
        return np.array(list(self.gen_cubic_bezier_tuples_from_points(points)))

    def gen_cubic_bezier_tuples_from_points(self, points):
        """
        Get a generator for the cubic bezier tuples of this object.

        Generator to not materialize a list or np.array needlessly.
        """
        nppcc = VMobject.CONFIG["n_points_per_cubic_curve"]
        remainder = len(points) % nppcc
        points = points[: len(points) - remainder]
        return (points[i : i + nppcc] for i in range(0, len(points), nppcc))

    def get_cubic_bezier_tuples(self):
        return self.get_cubic_bezier_tuples_from_points(self.get_points())

    def _gen_subpaths_from_points(self, points, filter_func):
        nppcc = self.n_points_per_cubic_curve
        split_indices = filter(filter_func, range(nppcc, len(points), nppcc))
        split_indices = [0] + list(split_indices) + [len(points)]
        return (
            points[i1:i2]
            for i1, i2 in zip(split_indices, split_indices[1:])
            if (i2 - i1) >= nppcc
        )

    def get_subpaths_from_points(self, points):
        return list(
            self._gen_subpaths_from_points(
                points,
                lambda n: not self.consider_points_equals(points[n - 1], points[n]),
            )
        )

    def gen_subpaths_from_points_2d(self, points):
        return self._gen_subpaths_from_points(
            points,
            lambda n: not self.consider_points_equals_2d(points[n - 1], points[n]),
        )

    def get_subpaths(self):
        return self.get_subpaths_from_points(self.get_points())

    def get_nth_curve_points(self, n):
        assert n < self.get_num_curves()
        nppcc = self.n_points_per_cubic_curve
        return self.points[nppcc * n : nppcc * (n + 1)]

    def get_nth_curve_function(self, n):
        return bezier(self.get_nth_curve_points(n))

    def get_num_curves(self):
        nppcc = self.n_points_per_cubic_curve
        return len(self.points) // nppcc

    def point_from_proportion(self, alpha):
        num_cubics = self.get_num_curves()
        n, residue = integer_interpolate(0, num_cubics, alpha)
        curve = self.get_nth_curve_function(n)
        return curve(residue)

    def get_anchors_and_handles(self):
        """
        returns anchors1, handles1, handles2, anchors2,
        where (anchors1[i], handles1[i], handles2[i], anchors2[i])
        will be four points defining a cubic bezier curve
        for any i in range(0, len(anchors1))
        """
        nppcc = self.n_points_per_cubic_curve
        return [self.points[i::nppcc] for i in range(nppcc)]

    def get_start_anchors(self):
        return self.points[0 :: self.n_points_per_cubic_curve]

    def get_end_anchors(self):
        nppcc = self.n_points_per_cubic_curve
        return self.points[nppcc - 1 :: nppcc]

    def get_anchors(self):
        if self.points.shape[0] == 1:
            return self.points
        return np.array(
            list(
                it.chain(
                    *zip(
                        self.get_start_anchors(),
                        self.get_end_anchors(),
                    )
                )
            )
        )

    def get_points_defining_boundary(self):
        return np.array(list(it.chain(*[sm.get_anchors() for sm in self.get_family()])))

    def get_arc_length(self, n_sample_points=None):
        if n_sample_points is None:
            n_sample_points = 4 * self.get_num_curves() + 1
        points = np.array(
            [self.point_from_proportion(a) for a in np.linspace(0, 1, n_sample_points)]
        )
        diffs = points[1:] - points[:-1]
        norms = np.apply_along_axis(get_norm, 1, diffs)
        return np.sum(norms)

    # Alignment
    def align_points(self, vmobject):
        self.align_rgbas(vmobject)
        if self.get_num_points() == vmobject.get_num_points():
            return

        for mob in self, vmobject:
            # If there are no points, add one to
            # whereever the "center" is
            if mob.has_no_points():
                mob.start_new_path(mob.get_center())
            # If there's only one point, turn it into
            # a null curve
            if mob.has_new_path_started():
                mob.add_line_to(mob.get_last_point())

        # Figure out what the subpaths are, and align
        subpaths1 = self.get_subpaths()
        subpaths2 = vmobject.get_subpaths()
        n_subpaths = max(len(subpaths1), len(subpaths2))
        # Start building new ones
        new_path1 = np.zeros((0, self.dim))
        new_path2 = np.zeros((0, self.dim))

        nppcc = self.n_points_per_cubic_curve

        def get_nth_subpath(path_list, n):
            if n >= len(path_list):
                # Create a null path at the very end
                return [path_list[-1][-1]] * nppcc
            return path_list[n]

        for n in range(n_subpaths):
            sp1 = get_nth_subpath(subpaths1, n)
            sp2 = get_nth_subpath(subpaths2, n)
            diff1 = max(0, (len(sp2) - len(sp1)) // nppcc)
            diff2 = max(0, (len(sp1) - len(sp2)) // nppcc)
            sp1 = self.insert_n_curves_to_point_list(diff1, sp1)
            sp2 = self.insert_n_curves_to_point_list(diff2, sp2)
            new_path1 = np.append(new_path1, sp1, axis=0)
            new_path2 = np.append(new_path2, sp2, axis=0)
        self.set_points(new_path1)
        vmobject.set_points(new_path2)
        return self

    def insert_n_curves(self, n):
        new_path_point = None
        if self.has_new_path_started():
            new_path_point = self.get_last_point()

        new_points = self.insert_n_curves_to_point_list(n, self.get_points())
        self.set_points(new_points)

        if new_path_point is not None:
            self.append_points([new_path_point])
        return self

    def insert_n_curves_to_point_list(self, n, points):
        if len(points) == 1:
            nppcc = self.n_points_per_cubic_curve
            return np.repeat(points, nppcc * n, 0)
        bezier_quads = self.get_cubic_bezier_tuples_from_points(points)
        curr_num = len(bezier_quads)
        target_num = curr_num + n
        # This is an array with values ranging from 0
        # up to curr_num,  with repeats such that
        # it's total length is target_num.  For example,
        # with curr_num = 10, target_num = 15, this would
        # be [0, 0, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 8, 9]
        repeat_indices = (np.arange(target_num) * curr_num) // target_num

        # If the nth term of this list is k, it means
        # that the nth curve of our path should be split
        # into k pieces.  In the above example, this would
        # be [2, 1, 2, 1, 2, 1, 2, 1, 2, 1]
        split_factors = [sum(repeat_indices == i) for i in range(curr_num)]
        new_points = np.zeros((0, self.dim))
        for quad, sf in zip(bezier_quads, split_factors):
            # What was once a single cubic curve defined
            # by "quad" will now be broken into sf
            # smaller cubic curves
            alphas = np.linspace(0, 1, sf + 1)
            for a1, a2 in zip(alphas, alphas[1:]):
                new_points = np.append(
                    new_points, partial_bezier_points(quad, a1, a2), axis=0
                )
        return new_points

    def align_rgbas(self, vmobject):
        attrs = ["fill_rgbas", "stroke_rgbas", "background_stroke_rgbas"]
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

    def get_point_mobject(self, center=None):
        if center is None:
            center = self.get_center()
        point = VectorizedPoint(center)
        point.match_style(self)
        return point

    def interpolate_color(self, mobject1, mobject2, alpha):
        attrs = [
            "fill_rgbas",
            "stroke_rgbas",
            "background_stroke_rgbas",
            "stroke_width",
            "background_stroke_width",
            "sheen_direction",
            "sheen_factor",
        ]
        for attr in attrs:
            setattr(
                self,
                attr,
                interpolate(getattr(mobject1, attr), getattr(mobject2, attr), alpha),
            )
            if alpha == 1.0:
                setattr(self, attr, getattr(mobject2, attr))

    def pointwise_become_partial(self, vmobject, a, b):
        assert isinstance(vmobject, VMobject)
        # Partial curve includes three portions:
        # - A middle section, which matches the curve exactly
        # - A start, which is some ending portion of an inner cubic
        # - An end, which is the starting portion of a later inner cubic
        if a <= 0 and b >= 1:
            self.set_points(vmobject.points)
            return self
        bezier_quads = vmobject.get_cubic_bezier_tuples()
        num_cubics = len(bezier_quads)

        lower_index, lower_residue = integer_interpolate(0, num_cubics, a)
        upper_index, upper_residue = integer_interpolate(0, num_cubics, b)

        self.clear_points()
        if num_cubics == 0:
            return self
        if lower_index == upper_index:
            self.append_points(
                partial_bezier_points(
                    bezier_quads[lower_index], lower_residue, upper_residue
                )
            )
        else:
            self.append_points(
                partial_bezier_points(bezier_quads[lower_index], lower_residue, 1)
            )
            for quad in bezier_quads[lower_index + 1 : upper_index]:
                self.append_points(quad)
            self.append_points(
                partial_bezier_points(bezier_quads[upper_index], 0, upper_residue)
            )
        return self

    def get_subcurve(self, a, b):
        vmob = self.copy()
        vmob.pointwise_become_partial(self, a, b)
        return vmob

    def get_direction(self):
        """Uses :func:`~.space_ops.shoelace_direction` to calculate the direction.
        The direction of points determines in which direction the
        object is drawn, clockwise or counterclockwise.

        Examples
        --------
        The default direction of a :class:`~.Circle` is counterclockwise::

            >>> from manim import Circle
            >>> Circle().get_direction()
            'CCW'

        Returns
        -------
        :class:`str`
            Either ``"CW"`` or ``"CCW"``.
        """
        return shoelace_direction(self.get_start_anchors())

    def reverse_direction(self):
        """Reverts the point direction by inverting the point order.

        Returns
        -------
        :class:`VMobject`
            Returns self.

        Examples
        --------
        .. manim:: ChangeOfDirection

            class ChangeOfDirection(Scene):
                def construct(self):
                    ccw = RegularPolygon(5)
                    ccw.shift(LEFT).rotate
                    cw = RegularPolygon(5)
                    cw.shift(RIGHT).reverse_direction()

                    self.play(ShowCreation(ccw), ShowCreation(cw),
                    run_time=4)
        """
        self.points = self.points[::-1]
        return self

    def force_direction(self, target_direction):
        """Makes sure that points are either directed clockwise or
        counterclockwise.

        Parameters
        ----------
        target_direction : :class:`str`
            Either ``"CW"`` or ``"CCW"``.
        """
        if target_direction not in ("CW", "CCW"):
            raise ValueError('Invalid input for force_direction. Use "CW" or "CCW"')
        if self.get_direction() != target_direction:
            # Since we already assured the input is CW or CCW,
            # and the directions don't match, we just reverse
            self.reverse_direction()
        return self


class VGroup(VMobject):
    """A group of vectorized mobjects.

    This can be used to group multiple :class:`~.VMobject` instances together
    in order to scale, move, ... them together.

    Examples
    --------

    .. manim:: ArcShapeIris
        :save_last_frame:

        class ArcShapeIris(Scene):
            def construct(self):
                colors = [DARK_BLUE, DARK_BROWN, BLUE_E, BLUE_D, BLUE_A, TEAL_B, GREEN_B, YELLOW_E]
                radius = [1 + rad * 0.1 for rad in range(len(colors))]

                circles_group = VGroup()

                # zip(radius, color) makes the iterator [(radius[i], color[i]) for i in range(radius)]
                circles_group.add(*[Circle(radius=rad, stroke_width=10, color=col)
                                    for rad, col in zip(radius, colors)])
                self.add(circles_group)

    """

    def __init__(self, *vmobjects, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.add(*vmobjects)

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + ", ".join(str(mob) for mob in self.submobjects)
            + ")"
        )

    def add(self, *vmobjects):
        """Checks if all passed elements are an instance of VMobject and then add them to submobjects

        Parameters
        ----------
        vmobjects : :class:`~.VMobject`
            List of VMobject to add

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If one element of the list is not an instance of VMobject
        """
        if not all(isinstance(m, VMobject) for m in vmobjects):
            raise TypeError("All submobjects must be of type VMobject")
        super().add(*vmobjects)


class VDict(VMobject):
    """A VGroup-like class, also offering submobject access by
    key, like a python dict

    Parameters
    ----------
    mapping_or_iterable : Union[:class:`Mapping`, Iterable[Tuple[Hashable, :class:`~.VMobject`]]], optional
            The parameter specifying the key-value mapping of keys and mobjects.
    show_keys : :class:`bool`, optional
            Whether to also display the key associated with
            the mobject. This might be useful when debugging,
            especially when there are a lot of mobjects in the
            :class:`VDict`. Defaults to False.
    kwargs : Any
            Other arguments to be passed to `Mobject` or the CONFIG.

    Attributes
    ----------
    show_keys : :class:`bool`
            Whether to also display the key associated with
            the mobject. This might be useful when debugging,
            especially when there are a lot of mobjects in the
            :class:`VDict`. When displayed, the key is towards
            the left of the mobject.
            Defaults to False.
    submob_dict : :class:`dict`
            Is the actual python dictionary that is used to bind
            the keys to the mobjects.

    Examples
    --------

    .. manim:: ShapesWithVDict

        class ShapesWithVDict(Scene):
            def construct(self):
                square = Square().set_color(RED)
                circle = Circle().set_color(YELLOW).next_to(square, UP)

                # create dict from list of tuples each having key-mobject pair
                pairs = [("s", square), ("c", circle)]
                my_dict = VDict(pairs, show_keys=True)

                # display it just like a VGroup
                self.play(ShowCreation(my_dict))
                self.wait()

                text = Tex("Some text").set_color(GREEN).next_to(square, DOWN)

                # add a key-value pair by wrapping it in a single-element list of tuple
                # after attrs branch is merged, it will be easier like `.add(t=text)`
                my_dict.add([("t", text)])
                self.wait()

                rect = Rectangle().next_to(text, DOWN)
                # can also do key assignment like a python dict
                my_dict["r"] = rect

                # access submobjects like a python dict
                my_dict["t"].set_color(PURPLE)
                self.play(my_dict["t"].scale, 3)
                self.wait()

                # also supports python dict styled reassignment
                my_dict["t"] = Tex("Some other text").set_color(BLUE)
                self.wait()

                # remove submoject by key
                my_dict.remove("t")
                self.wait()

                self.play(Uncreate(my_dict["s"]))
                self.wait()

                self.play(FadeOut(my_dict["c"]))
                self.wait()

                self.play(FadeOutAndShift(my_dict["r"], DOWN))
                self.wait()

                # you can also make a VDict from an existing dict of mobjects
                plain_dict = {
                    1: Integer(1).shift(DOWN),
                    2: Integer(2).shift(2 * DOWN),
                    3: Integer(3).shift(3 * DOWN),
                }

                vdict_from_plain_dict = VDict(plain_dict)
                vdict_from_plain_dict.shift(1.5 * (UP + LEFT))
                self.play(ShowCreation(vdict_from_plain_dict))

                # you can even use zip
                vdict_using_zip = VDict(zip(["s", "c", "r"], [Square(), Circle(), Rectangle()]))
                vdict_using_zip.shift(1.5 * RIGHT)
                self.play(ShowCreation(vdict_using_zip))
                self.wait()
    """

    def __init__(self, mapping_or_iterable={}, show_keys=False, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.show_keys = show_keys
        self.submob_dict = {}
        self.add(mapping_or_iterable)

    def __repr__(self):
        return __class__.__name__ + "(" + repr(self.submob_dict) + ")"

    def add(self, mapping_or_iterable):
        """Adds the key-value pairs to the :class:`VDict` object.

        Also, it internally adds the value to the `submobjects` :class:`list`
        of :class:`~.Mobject`, which is responsible for actual on-screen display.

        Parameters
        ---------
        mapping_or_iterable : Union[:class:`Mapping`, Iterable[Tuple[Hashable, :class:`~.VMobject`]]], optional
            The parameter specifying the key-value mapping of keys and mobjects.

        Returns
        -------
        :class:`VDict`
            Returns the :class:`VDict` object on which this method was called.

        Examples
        --------
        Normal usage::

            square_obj = Square()
            my_dict.add([('s', square_obj)])
        """
        for key, value in dict(mapping_or_iterable).items():
            self.add_key_value_pair(key, value)

        return self

    def remove(self, key):
        """Removes the mobject from the :class:`VDict` object having the key `key`

        Also, it internally removes the mobject from the `submobjects` :class:`list`
        of :class:`~.Mobject`, (which is responsible for removing it from the screen)

        Parameters
        ----------
        key : :class:`typing.Hashable`
            The key of the submoject to be removed.

        Returns
        -------
        :class:`VDict`
            Returns the :class:`VDict` object on which this method was called.

        Examples
        --------
        Normal usage::

            my_dict.remove('square')
        """
        if key not in self.submob_dict:
            raise KeyError("The given key '%s' is not present in the VDict" % str(key))
        super().remove(self.submob_dict[key])
        del self.submob_dict[key]
        return self

    def __getitem__(self, key):
        """Override the [] operator for item retrieval.

        Parameters
        ----------
        key : :class:`typing.Hashable`
           The key of the submoject to be accessed

        Returns
        -------
        :class:`VMobject`
           The submobject corresponding to the key `key`

        Examples
        --------
        Normal usage::

           self.play(ShowCreation(my_dict['s']))
        """
        submob = self.submob_dict[key]
        return submob

    def __setitem__(self, key, value):
        """Override the [] operator for item assignment.

        Parameters
        ----------
        key : :class:`typing.Hashable`
            The key of the submoject to be assigned
        value : :class:`VMobject`
            The submobject to bind the key to

        Returns
        -------
        None

        Examples
        --------
        Normal usage::

            square_obj = Square()
            my_dict['sq'] = square_obj
        """
        if key in self.submob_dict:
            self.remove(key)
        self.add([(key, value)])

    def __delitem__(self, key):
        """Override the del operator for deleting an item.

        Parameters
        ----------
        key : :class:`typing.Hashable`
            The key of the submoject to be deleted

        Returns
        -------
        None

        Examples
        --------
        ::

            >>> from manim import *
            >>> my_dict = VDict({'sq': Square()})
            >>> 'sq' in my_dict
            True
            >>> del my_dict['sq']
            >>> 'sq' in my_dict
            False

        Notes
        -----
        Removing an item from a VDict does not remove that item from any Scene
        that the VDict is part of.

        """
        del self.submob_dict[key]

    def __contains__(self, key):
        """Override the in operator.

        Parameters
        ----------
        key : :class:`typing.Hashable`
            The key to check membership of.

        Returns
        -------
        :class:`bool`

        Examples
        --------
        ::

            >>> from manim import *
            >>> my_dict = VDict({'sq': Square()})
            >>> 'sq' in my_dict
            True

        """
        return key in self.submob_dict

    def get_all_submobjects(self):
        """To get all the submobjects associated with a particular :class:`VDict` object

        Returns
        -------
        :class:`dict_values`
            All the submobjects associated with the :class:`VDict` object

        Examples
        --------
        Normal usage::

            for submob in my_dict.get_all_submobjects():
                self.play(ShowCreation(submob))
        """
        submobjects = self.submob_dict.values()
        return submobjects

    def add_key_value_pair(self, key, value):
        """A utility function used by :meth:`add` to add the key-value pair
        to :attr:`submob_dict`. Not really meant to be used externally.

        Parameters
        ----------
        key : :class:`typing.Hashable`
            The key of the submobject to be added.
        value : :class:`~.VMobject`
            The mobject associated with the key

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the value is not an instance of VMobject

        Examples
        --------
        Normal usage::

            square_obj = Square()
            self.add_key_value_pair('s', square_obj)

        """
        if not isinstance(value, VMobject):
            raise TypeError("All submobjects must be of type VMobject")
        mob = value
        if self.show_keys:
            # This import is here and not at the top to avoid circular import
            from ...mobject.svg.tex_mobject import Tex

            key_text = Tex(str(key)).next_to(value, LEFT)
            mob.add(key_text)

        self.submob_dict[key] = mob
        super().add(value)


class VectorizedPoint(VMobject):
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

    def get_width(self):
        return self.artificial_width

    def get_height(self):
        return self.artificial_height

    def get_location(self):
        return np.array(self.points[0])

    def set_location(self, new_loc):
        self.set_points(np.array([new_loc]))


class CurvesAsSubmobjects(VGroup):
    def __init__(self, vmobject, **kwargs):
        VGroup.__init__(self, **kwargs)
        tuples = vmobject.get_cubic_bezier_tuples()
        for tup in tuples:
            part = VMobject()
            part.set_points(tup)
            part.match_style(vmobject)
            self.add(part)


class DashedVMobject(VMobject):
    CONFIG = {"num_dashes": 15, "positive_space_ratio": 0.5, "color": WHITE}

    def __init__(self, vmobject, **kwargs):
        VMobject.__init__(self, **kwargs)
        num_dashes = self.num_dashes
        ps_ratio = self.positive_space_ratio
        if num_dashes > 0:
            # End points of the unit interval for division
            alphas = np.linspace(0, 1, num_dashes + 1)

            # This determines the length of each "dash"
            full_d_alpha = 1.0 / num_dashes
            partial_d_alpha = full_d_alpha * ps_ratio

            # Rescale so that the last point of vmobject will
            # be the end of the last dash
            alphas /= 1 - full_d_alpha + partial_d_alpha

            self.add(
                *[
                    vmobject.get_subcurve(alpha, alpha + partial_d_alpha)
                    for alpha in alphas[:-1]
                ]
            )
        # Family is already taken care of by get_subcurve
        # implementation
        self.match_style(vmobject, family=False)
