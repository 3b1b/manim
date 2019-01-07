import itertools as it

from colour import Color

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.three_d_utils import get_3d_vmob_gradient_start_and_end_points
from manimlib.utils.bezier import bezier
from manimlib.utils.bezier import get_smooth_handle_points
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import is_closed
from manimlib.utils.bezier import partial_bezier_points
from manimlib.utils.color import color_to_rgba
from manimlib.utils.iterables import make_even
from manimlib.utils.iterables import stretch_array_to_length
from manimlib.utils.iterables import tuplify
from manimlib.utils.simple_functions import clip_in_place


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
        # sheen, and the display will gradient to this
        # secondary color in the direction of sheen_direction.
        "sheen": 0.0,
        "sheen_direction": UL,
        # Indicates that it will not be displayed, but
        # that it should count in parent mobject's path
        "is_subpath": False,
        "close_new_points": False,
        "mark_paths_closed": False,
        "propagate_style_to_family": False,
        "pre_function_handle_to_anchor_scale_factor": 0.01,
        "make_smooth_after_applying_functions": False,
        "background_image_file": None,
        "shade_in_3d": False,
    }

    def get_group_class(self):
        return VGroup

    # Colors
    def init_colors(self):
        self.set_fill(
            color=self.fill_color or self.color,
            opacity=self.fill_opacity,
            family=self.propagate_style_to_family
        )
        self.set_stroke(
            color=self.stroke_color or self.color,
            width=self.stroke_width,
            opacity=self.stroke_opacity,
            family=self.propagate_style_to_family
        )
        self.set_background_stroke(
            color=self.background_stroke_color,
            width=self.background_stroke_width,
            opacity=self.background_stroke_opacity,
            family=self.propagate_style_to_family,
        )
        self.set_sheen(
            factor=self.sheen,
            direction=self.sheen_direction,
            family=self.propagate_style_to_family
        )
        return self

    def generate_rgbas_array(self, color, opacity):
        """
        First arg can be either a color, or a tuple/list of colors.
        Likewise, opacity can either be a float, or a tuple of floats.
        If self.sheen is not zero, and only
        one color was passed in, a second slightly light color
        will automatically be added for the gradient
        """
        colors = list(tuplify(color))
        opacities = list(tuplify(opacity))
        rgbas = np.array([
            color_to_rgba(c, o)
            for c, o in zip(*make_even(colors, opacities))
        ])

        sheen = self.get_sheen()
        if sheen != 0 and len(rgbas) == 1:
            light_rgbas = np.array(rgbas)
            light_rgbas[:, :3] += sheen
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
            curr_rgbas = stretch_array_to_length(
                curr_rgbas, len(rgbas)
            )
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

    def set_stroke(self, color=None, width=None, opacity=None,
                   background=False, family=True):
        if family:
            for submobject in self.submobjects:
                submobject.set_stroke(
                    color, width, opacity, background, family
                )
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

    def set_style(self,
                  fill_color=None,
                  fill_opacity=None,
                  stroke_color=None,
                  stroke_width=None,
                  background_stroke_color=None,
                  background_stroke_width=None,
                  sheen_factor=None,
                  sheen_direction=None,
                  background_image_file=None,
                  family=True):
        self.set_fill(
            color=fill_color,
            opacity=fill_opacity,
            family=family
        )
        self.set_stroke(
            color=stroke_color,
            width=stroke_width,
            family=family,
        )
        self.set_background_stroke(
            color=background_stroke_color,
            width=background_stroke_width,
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

    def get_style(self):
        return {
            "fill_color": self.get_fill_colors(),
            "fill_opacity": self.get_fill_opacities(),
            "stroke_color": self.get_stroke_colors(),
            "stroke_width": self.get_stroke_width(),
            "background_stroke_color": self.get_stroke_colors(background=True),
            "background_stroke_width": self.get_stroke_width(background=True),
            "sheen_factor": self.get_sheen(),
            "sheen_direction": self.get_sheen_direction(),
            "background_image_file": self.get_background_image_file(),
        }

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
        return self

    def fade_no_recurse(self, darkness):
        opacity = 1.0 - darkness
        self.set_fill(opacity=opacity)
        self.set_stroke(opacity=opacity)
        self.set_background_stroke(opacity=opacity)
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
            Color(rgb=rgba[:3])
            for rgba in self.get_stroke_rgbas(background)
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
        self.sheen = factor
        if direction is not None:
            # family set to false because recursion will
            # already be handled above
            self.set_sheen_direction(direction, family=False)
        # Reset color to put sheen into effect
        if factor != 0:
            self.set_stroke(self.get_stroke_color(), family=family)
            self.set_fill(self.get_fill_color(), family=family)
        return self

    def get_sheen_direction(self):
        return np.array(self.sheen_direction)

    def get_sheen(self):
        return self.sheen

    def get_gradient_start_and_end_points(self):
        if self.shade_in_3d:
            return get_3d_vmob_gradient_start_and_end_points(self)
        else:
            direction = self.get_sheen_direction()
            c = self.get_center()
            bases = np.array([
                self.get_edge_center(vect) - c
                for vect in [RIGHT, UP, OUT]
            ]).transpose()
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
        points = self.prepare_new_anchor_points(points)
        self.set_anchors_and_handles(points, *[
            interpolate(points[:-1], points[1:], alpha)
            for alpha in (1. / 3, 2. / 3)
        ])
        return self

    def set_points_smoothly(self, points):
        if len(points) <= 1:
            return self
        points = self.prepare_new_anchor_points(points)
        h1, h2 = get_smooth_handle_points(points)
        self.set_anchors_and_handles(points, h1, h2)
        return self

    def prepare_new_anchor_points(self, points):
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        if self.close_new_points and not is_closed(points):
            points = np.append(points, [points[0]], axis=0)
        return points

    def set_points(self, points):
        self.points = np.array(points)
        return self

    def set_anchor_points(self, points, mode="smooth"):
        if mode == "smooth":
            self.set_points_smoothly(points)
        elif mode == "corners":
            self.set_points_as_corners(points)
        else:
            raise Exception("Unknown mode")
        return self

    def change_anchor_mode(self, mode):
        for submob in self.family_members_with_points():
            anchors = submob.get_anchors()
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
        return [m for m in self.submobjects if hasattr(m, 'is_subpath') and m.is_subpath]

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
        for submob in self.family_members_with_points():
            anchors, handles1, handles2 = submob.get_anchors_and_handles()
            # print len(anchors), len(handles1), len(handles2)
            a_to_h1 = handles1 - anchors[:-1]
            a_to_h2 = handles2 - anchors[1:]
            handles1 = anchors[:-1] + factor * a_to_h1
            handles2 = anchors[1:] + factor * a_to_h2
            submob.set_anchors_and_handles(anchors, handles1, handles2)

    # Information about line

    def component_curves(self):
        for n in range(self.get_num_anchor_points() - 1):
            yield self.get_nth_curve(n)

    def get_nth_curve(self, n):
        return bezier(self.points[3 * n:3 * n + 4])

    def get_num_anchor_points(self):
        return (len(self.points) - 1) // 3 + 1

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
        return np.array(list(it.chain(*[
            sm.get_anchors() for sm in self.get_family()
        ])))

    # Alignment
    def align_points(self, vmobject):
        Mobject.align_points(self, vmobject)
        self.align_rgbas(vmobject)
        is_subpath = self.is_subpath or vmobject.is_subpath
        self.is_subpath = vmobject.is_subpath = is_subpath
        mark_closed = self.mark_paths_closed and vmobject.mark_paths_closed
        self.mark_paths_closed = vmobject.mark_paths_closed = mark_closed
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
        index_allocation = (
            np.arange(curr + n - 1) * num_curves) // (curr + n - 1)
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
        return VectorizedPoint(center)

    def repeat_submobject(self, submobject):
        if submobject.is_subpath:
            return VectorizedPoint(submobject.points[0])
        return submobject.copy()

    def interpolate_color(self, mobject1, mobject2, alpha):
        attrs = [
            "fill_rgbas",
            "stroke_rgbas",
            "background_stroke_rgbas",
            "stroke_width",
            "background_stroke_width",
            "sheen_direction",
            "sheen",
        ]
        for attr in attrs:
            setattr(self, attr, interpolate(
                getattr(mobject1, attr),
                getattr(mobject2, attr),
                alpha
            ))
            if alpha == 1.0:
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
        return self.points[0]

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
            dash = VMobject(color=self.get_color())
            dash.pointwise_become_partial(mobject, a, b)
            self.submobjects.append(dash)
