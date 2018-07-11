from __future__ import absolute_import

from colour import Color

from mobject.mobject import Mobject
from constants import *
from utils.bezier import bezier
from utils.bezier import get_smooth_handle_points
from utils.bezier import interpolate
from utils.bezier import is_closed
from utils.bezier import partial_bezier_points
from utils.color import color_to_rgb
from utils.iterables import make_even


class VMobject(Mobject):
    CONFIG = {
        "fill_color": None,
        "fill_opacity": 0.0,
        "stroke_color": None,
        "stroke_width": DEFAULT_POINT_THICKNESS,
        # Indicates that it will not be displayed, but
        # that it should count in parent mobject's path
        "is_subpath": False,
        "close_new_points": False,
        "mark_paths_closed": False,
        "propagate_style_to_family": False,
        "pre_function_handle_to_anchor_scale_factor": 0.01,
        "make_smooth_after_applying_functions": False,
        "background_image_file": None,
    }

    def get_group_class(self):
        return VGroup

    # Colors
    def init_colors(self):
        self.set_style_data(
            stroke_color=self.stroke_color or self.color,
            stroke_width=self.stroke_width,
            fill_color=self.fill_color or self.color,
            fill_opacity=self.fill_opacity,
            family=self.propagate_style_to_family
        )
        return self

    def set_family_attr(self, attr, value):
        for mob in self.submobject_family():
            setattr(mob, attr, value)

    def set_style_data(self,
                       stroke_color=None,
                       stroke_width=None,
                       fill_color=None,
                       fill_opacity=None,
                       family=True
                       ):
        if stroke_color is not None:
            self.stroke_rgb = color_to_rgb(stroke_color)
        if fill_color is not None:
            self.fill_rgb = color_to_rgb(fill_color)
        if stroke_width is not None:
            self.stroke_width = stroke_width
        if fill_opacity is not None:
            self.fill_opacity = fill_opacity
        if family:
            for mob in self.submobjects:
                mob.set_style_data(
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    fill_color=fill_color,
                    fill_opacity=fill_opacity,
                    family=family
                )
        return self

    def set_fill(self, color=None, opacity=None, family=True):
        return self.set_style_data(
            fill_color=color,
            fill_opacity=opacity,
            family=family
        )

    def set_stroke(self, color=None, width=None, family=True):
        return self.set_style_data(
            stroke_color=color,
            stroke_width=width,
            family=family
        )

    def set_color(self, color, family=True):
        self.set_style_data(
            stroke_color=color,
            fill_color=color,
            family=family
        )
        self.color = color
        return self

    def match_style(self, vmobject):
        self.set_style_data(
            stroke_color=vmobject.get_stroke_color(),
            stroke_width=vmobject.get_stroke_width(),
            fill_color=vmobject.get_fill_color(),
            fill_opacity=vmobject.get_fill_opacity(),
            family=False
        )

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

    def fade_no_recurse(self, darkness):
        self.set_stroke(
            width=(1 - darkness) * self.get_stroke_width(),
            family=False
        )
        self.set_fill(
            opacity=(1 - darkness) * self.get_fill_opacity(),
            family=False
        )
        return self

    def get_fill_rgb(self):
        return np.clip(self.fill_rgb, 0, 1)

    def get_fill_color(self):
        try:
            self.fill_rgb = np.clip(self.fill_rgb, 0.0, 1.0)
            return Color(rgb=self.fill_rgb)
        except:
            return Color(WHITE)

    def get_fill_opacity(self):
        return np.clip(self.fill_opacity, 0, 1)

    def get_stroke_rgb(self):
        return np.clip(self.stroke_rgb, 0, 1)

    def get_stroke_color(self):
        try:
            self.stroke_rgb = np.clip(self.stroke_rgb, 0, 1)
            return Color(rgb=self.stroke_rgb)
        except:
            return Color(WHITE)

    def get_stroke_width(self):
        return max(0, self.stroke_width)

    def get_color(self):
        if self.fill_opacity == 0:
            return self.get_stroke_color()
        return self.get_fill_color()

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

    # Drawing
    def start_at(self, point):
        if len(self.points) == 0:
            self.points = np.zeros((1, 3))
        self.points[0] = point
        return self

    def add_control_points(self, control_points):
        assert(len(control_points) % 3 == 0)
        self.points = np.append(
            self.points,
            control_points,
            axis=0
        )
        return self

    def is_closed(self):
        return is_closed(self.points)

    def set_anchors_and_handles(self, anchors, handles1, handles2):
        assert(len(anchors) == len(handles1) + 1)
        assert(len(anchors) == len(handles2) + 1)
        total_len = 3 * (len(anchors) - 1) + 1
        self.points = np.zeros((total_len, self.dim))
        self.points[0] = anchors[0]
        arrays = [handles1, handles2, anchors[1:]]
        for index, array in enumerate(arrays):
            self.points[index + 1::3] = array
        return self.points

    def set_points_as_corners(self, points):
        if len(points) <= 1:
            return self
        points = np.array(points)
        self.set_anchors_and_handles(points, *[
            interpolate(points[:-1], points[1:], alpha)
            for alpha in (1. / 3, 2. / 3)
        ])
        return self

    def set_points_smoothly(self, points):
        if len(points) <= 1:
            return self
        h1, h2 = get_smooth_handle_points(points)
        self.set_anchors_and_handles(points, h1, h2)
        return self

    def set_points(self, points):
        self.points = np.array(points)
        return self

    def set_anchor_points(self, points, mode="smooth"):
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        if self.close_new_points and not is_closed(points):
            points = np.append(points, [points[0]], axis=0)
        if mode == "smooth":
            self.set_points_smoothly(points)
        elif mode == "corners":
            self.set_points_as_corners(points)
        else:
            raise Exception("Unknown mode")
        return self

    def change_anchor_mode(self, mode):
        for submob in self.family_members_with_points():
            anchors, h1, h2 = submob.get_anchors_and_handles()
            submob.set_anchor_points(anchors, mode=mode)
        return self

    def make_smooth(self):
        return self.change_anchor_mode("smooth")

    def make_jagged(self):
        return self.change_anchor_mode("corners")

    def add_subpath(self, points):
        """
        A VMobject is meant to represent
        a single "path", in the svg sense of the word.
        However, one such path may really consist of separate
        continuous components if there is a move_to command.
        These other portions of the path will be treated as submobjects,
        but will be tracked in a separate special list for when
        it comes time to display.
        """
        subpath_mobject = self.copy()  # Really helps to be of the same class
        subpath_mobject.submobjects = []
        subpath_mobject.is_subpath = True
        subpath_mobject.set_points(points)
        self.add(subpath_mobject)
        return subpath_mobject

    def append_vectorized_mobject(self, vectorized_mobject):
        new_points = list(vectorized_mobject.points)
        if len(new_points) == 0:
            return
        if self.get_num_points() == 0:
            self.start_at(new_points[0])
            self.add_control_points(new_points[1:])
        else:
            self.add_control_points(2 * [new_points[0]] + new_points)
        return self

    def get_subpath_mobjects(self):
        return filter(
            lambda m: hasattr(m, 'is_subpath') and m.is_subpath,
            self.submobjects
        )

    def apply_function(self, function):
        factor = self.pre_function_handle_to_anchor_scale_factor
        self.scale_handle_to_anchor_distances(factor)
        Mobject.apply_function(self, function)
        self.scale_handle_to_anchor_distances(1. / factor)
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
        if self.get_num_points() == 0:
            return
        anchors, handles1, handles2 = self.get_anchors_and_handles()
        # print len(anchors), len(handles1), len(handles2)
        a_to_h1 = handles1 - anchors[:-1]
        a_to_h2 = handles2 - anchors[1:]
        handles1 = anchors[:-1] + factor * a_to_h1
        handles2 = anchors[1:] + factor * a_to_h2
        self.set_anchors_and_handles(anchors, handles1, handles2)

    # Information about line

    def component_curves(self):
        for n in range(self.get_num_anchor_points() - 1):
            yield self.get_nth_curve(n)

    def get_nth_curve(self, n):
        return bezier(self.points[3 * n:3 * n + 4])

    def get_num_anchor_points(self):
        return (len(self.points) - 1) / 3 + 1

    def point_from_proportion(self, alpha):
        num_cubics = self.get_num_anchor_points() - 1
        interpoint_alpha = num_cubics * (alpha % (1. / num_cubics))
        index = min(3 * int(alpha * num_cubics), 3 * num_cubics)
        cubic = bezier(self.points[index:index + 4])
        return cubic(interpoint_alpha)

    def get_anchors_and_handles(self):
        return [
            self.points[i::3]
            for i in range(3)
        ]

    def get_anchors(self):
        return self.points[::3]

    def get_points_defining_boundary(self):
        return self.get_anchors()

    # Alignment
    def align_points(self, mobject):
        Mobject.align_points(self, mobject)
        is_subpath = self.is_subpath or mobject.is_subpath
        self.is_subpath = mobject.is_subpath = is_subpath
        mark_closed = self.mark_paths_closed and mobject.mark_paths_closed
        self.mark_paths_closed = mobject.mark_paths_closed = mark_closed
        return self

    def align_points_with_larger(self, larger_mobject):
        assert(isinstance(larger_mobject, VMobject))
        self.insert_n_anchor_points(
            larger_mobject.get_num_anchor_points() -
            self.get_num_anchor_points()
        )
        return self

    def insert_n_anchor_points(self, n):
        curr = self.get_num_anchor_points()
        if curr == 0:
            self.points = np.zeros((1, 3))
            n = n - 1
        if curr == 1:
            self.points = np.repeat(self.points, 3 * n + 1, axis=0)
            return self
        points = np.array([self.points[0]])
        num_curves = curr - 1
        # Curves in self are buckets, and we need to know
        # how many new anchor points to put into each one.
        # Each element of index_allocation is like a bucket,
        # and its value tells you the appropriate index of
        # the smaller curve.
        index_allocation = (np.arange(curr + n - 1) *
                            num_curves) / (curr + n - 1)
        for index in range(num_curves):
            curr_bezier_points = self.points[3 * index:3 * index + 4]
            num_inter_curves = sum(index_allocation == index)
            alphas = np.linspace(0, 1, num_inter_curves + 1)
            # alphas = np.arange(0, num_inter_curves+1)/float(num_inter_curves)
            for a, b in zip(alphas, alphas[1:]):
                new_points = partial_bezier_points(
                    curr_bezier_points, a, b
                )
                points = np.append(
                    points, new_points[1:], axis=0
                )
        self.set_points(points)
        return self

    def get_point_mobject(self, center=None):
        if center is None:
            center = self.get_center()
        return VectorizedPoint(center)

    def repeat_submobject(self, submobject):
        if submobject.is_subpath:
            return VectorizedPoint(submobject.points[0])
        return submobject.copy()

    def interpolate_color(self, mobject1, mobject2, alpha):
        attrs = [
            "stroke_rgb",
            "stroke_width",
            "fill_rgb",
            "fill_opacity",
        ]
        for attr in attrs:
            setattr(self, attr, interpolate(
                getattr(mobject1, attr),
                getattr(mobject2, attr),
                alpha
            ))
            if alpha == 1.0:
                # print getattr(mobject2, attr)
                setattr(self, attr, getattr(mobject2, attr))

    def pointwise_become_partial(self, mobject, a, b):
        assert(isinstance(mobject, VMobject))
        # Partial curve includes three portions:
        # - A middle section, which matches the curve exactly
        # - A start, which is some ending portion of an inner cubic
        # - An end, which is the starting portion of a later inner cubic
        if a <= 0 and b >= 1:
            self.set_points(mobject.points)
            self.mark_paths_closed = mobject.mark_paths_closed
            return self
        self.mark_paths_closed = False
        num_cubics = mobject.get_num_anchor_points() - 1
        lower_index = int(a * num_cubics)
        upper_index = int(b * num_cubics)
        points = np.array(
            mobject.points[3 * lower_index:3 * upper_index + 4]
        )
        if len(points) > 1:
            a_residue = (num_cubics * a) % 1
            b_residue = (num_cubics * b) % 1
            if b == 1:
                b_residue = 1
            elif lower_index == upper_index:
                b_residue = (b_residue - a_residue) / (1 - a_residue)

            points[:4] = partial_bezier_points(
                points[:4], a_residue, 1
            )
            points[-4:] = partial_bezier_points(
                points[-4:], 0, b_residue
            )
        self.set_points(points)
        return self


class VGroup(VMobject):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            args = args[0]

        packed_args = []
        for arg in args:
            if isinstance(arg, (tuple, list)):
                packed_args.append(VGroup(arg))
            else:
                packed_args.append(arg)

        VMobject.__init__(self, *packed_args, **kwargs)


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
        return self.get_anchors()[0]

    def set_location(self, new_loc):
        self.set_points(np.array([new_loc]))


class DashedMobject(VMobject):
    CONFIG = {
        "dashes_num": 15,
        "spacing": 0.5,
        "color": WHITE
    }

    def __init__(self, mobject, **kwargs):
        VMobject.__init__(self, **kwargs)

        buff = float(self.spacing) / self.dashes_num

        for i in range(self.dashes_num):
            a = ((1 + buff) * i) / self.dashes_num
            b = 1 - ((1 + buff) * (self.dashes_num - 1 - i)) / self.dashes_num
            dash = VMobject(color=self.color)
            dash.pointwise_become_partial(mobject, a, b)
            self.submobjects.append(dash)
