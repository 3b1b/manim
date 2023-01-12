from __future__ import annotations

import math
import numbers

import numpy as np

from manimlib.constants import DL, DOWN, DR, LEFT, ORIGIN, OUT, RIGHT, UL, UP, UR
from manimlib.constants import GREY_A, RED, WHITE, BLACK
from manimlib.constants import MED_SMALL_BUFF
from manimlib.constants import DEGREES, PI, TAU
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import DashedVMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.iterables import adjacent_n_tuples
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.simple_functions import clip
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.space_ops import angle_between_vectors
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import compass_directions
from manimlib.utils.space_ops import find_intersection
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import normalize
from manimlib.utils.space_ops import rotate_vector
from manimlib.utils.space_ops import rotation_matrix_transpose

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable
    from manimlib.typing import ManimColor, Vect3, Vect3Array


DEFAULT_DOT_RADIUS = 0.08
DEFAULT_SMALL_DOT_RADIUS = 0.04
DEFAULT_DASH_LENGTH = 0.05
DEFAULT_ARROW_TIP_LENGTH = 0.35
DEFAULT_ARROW_TIP_WIDTH = 0.35


# Deprecate?
class TipableVMobject(VMobject):
    """
    Meant for shared functionality between Arc and Line.
    Functionality can be classified broadly into these groups:

        * Adding, Creating, Modifying tips
            - add_tip calls create_tip, before pushing the new tip
                into the TipableVMobject's list of submobjects
            - stylistic and positional configuration

        * Checking for tips
            - Boolean checks for whether the TipableVMobject has a tip
                and a starting tip

        * Getters
            - Straightforward accessors, returning information pertaining
                to the TipableVMobject instance's tip(s), its length etc
    """
    tip_config: dict = dict(
        fill_opacity=1.0,
        stroke_width=0.0,
        tip_style=0.0,  # triangle=0, inner_smooth=1, dot=2
    )

    # Adding, Creating, Modifying tips
    def add_tip(self, at_start: bool = False, **kwargs):
        """
        Adds a tip to the TipableVMobject instance, recognising
        that the endpoints might need to be switched if it's
        a 'starting tip' or not.
        """
        tip = self.create_tip(at_start, **kwargs)
        self.reset_endpoints_based_on_tip(tip, at_start)
        self.asign_tip_attr(tip, at_start)
        tip.set_color(self.get_stroke_color())
        self.add(tip)
        return self

    def create_tip(self, at_start: bool = False, **kwargs) -> ArrowTip:
        """
        Stylises the tip, positions it spacially, and returns
        the newly instantiated tip to the caller.
        """
        tip = self.get_unpositioned_tip(**kwargs)
        self.position_tip(tip, at_start)
        return tip

    def get_unpositioned_tip(self, **kwargs) -> ArrowTip:
        """
        Returns a tip that has been stylistically configured,
        but has not yet been given a position in space.
        """
        config = dict()
        config.update(self.tip_config)
        config.update(kwargs)
        return ArrowTip(**config)

    def position_tip(self, tip: ArrowTip, at_start: bool = False) -> ArrowTip:
        # Last two control points, defining both
        # the end, and the tangency direction
        if at_start:
            anchor = self.get_start()
            handle = self.get_first_handle()
        else:
            handle = self.get_last_handle()
            anchor = self.get_end()
        tip.rotate(angle_of_vector(handle - anchor) - PI - tip.get_angle())
        tip.shift(anchor - tip.get_tip_point())
        return tip

    def reset_endpoints_based_on_tip(self, tip: ArrowTip, at_start: bool):
        if self.get_length() == 0:
            # Zero length, put_start_and_end_on wouldn't
            # work
            return self

        if at_start:
            start = tip.get_base()
            end = self.get_end()
        else:
            start = self.get_start()
            end = tip.get_base()
        self.put_start_and_end_on(start, end)
        return self

    def asign_tip_attr(self, tip: ArrowTip, at_start: bool):
        if at_start:
            self.start_tip = tip
        else:
            self.tip = tip
        return self

    # Checking for tips
    def has_tip(self) -> bool:
        return hasattr(self, "tip") and self.tip in self

    def has_start_tip(self) -> bool:
        return hasattr(self, "start_tip") and self.start_tip in self

    # Getters
    def pop_tips(self) -> VGroup:
        start, end = self.get_start_and_end()
        result = VGroup()
        if self.has_tip():
            result.add(self.tip)
            self.remove(self.tip)
        if self.has_start_tip():
            result.add(self.start_tip)
            self.remove(self.start_tip)
        self.put_start_and_end_on(start, end)
        return result

    def get_tips(self) -> VGroup:
        """
        Returns a VGroup (collection of VMobjects) containing
        the TipableVMObject instance's tips.
        """
        result = VGroup()
        if hasattr(self, "tip"):
            result.add(self.tip)
        if hasattr(self, "start_tip"):
            result.add(self.start_tip)
        return result

    def get_tip(self) -> ArrowTip:
        """Returns the TipableVMobject instance's (first) tip,
        otherwise throws an exception."""
        tips = self.get_tips()
        if len(tips) == 0:
            raise Exception("tip not found")
        else:
            return tips[0]

    def get_default_tip_length(self) -> float:
        return self.tip_length

    def get_first_handle(self) -> Vect3:
        return self.get_points()[1]

    def get_last_handle(self) -> Vect3:
        return self.get_points()[-2]

    def get_end(self) -> Vect3:
        if self.has_tip():
            return self.tip.get_start()
        else:
            return VMobject.get_end(self)

    def get_start(self) -> Vect3:
        if self.has_start_tip():
            return self.start_tip.get_start()
        else:
            return VMobject.get_start(self)

    def get_length(self) -> float:
        start, end = self.get_start_and_end()
        return get_norm(start - end)


class Arc(TipableVMobject):
    def __init__(
        self,
        start_angle: float = 0,
        angle: float = TAU / 4,
        radius: float = 1.0,
        n_components: int = 8,
        arc_center: Vect3 = ORIGIN,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.set_points(Arc.create_quadratic_bezier_points(
            angle=angle,
            start_angle=start_angle,
            n_components=n_components
        ))
        self.scale(radius, about_point=ORIGIN)
        self.shift(arc_center)

    @staticmethod
    def create_quadratic_bezier_points(
        angle: float,
        start_angle: float = 0,
        n_components: int = 8
    ) -> Vect3Array:
        n_points = 2 * n_components + 1
        angles = np.linspace(start_angle, start_angle + angle, n_points)
        points = np.array([np.cos(angles), np.sin(angles), np.zeros(n_points)]).T
        # Adjust handles
        theta = angle / n_components
        points[1::2] /= np.cos(theta / 2)
        return points

    def get_arc_center(self) -> Vect3:
        """
        Looks at the normals to the first two
        anchors, and finds their intersection points
        """
        # First two anchors and handles
        a1, h, a2 = self.get_points()[:3]
        # Tangent vectors
        t1 = h - a1
        t2 = h - a2
        # Normals
        n1 = rotate_vector(t1, TAU / 4)
        n2 = rotate_vector(t2, TAU / 4)
        return find_intersection(a1, n1, a2, n2)

    def get_start_angle(self) -> float:
        angle = angle_of_vector(self.get_start() - self.get_arc_center())
        return angle % TAU

    def get_stop_angle(self) -> float:
        angle = angle_of_vector(self.get_end() - self.get_arc_center())
        return angle % TAU

    def move_arc_center_to(self, point: Vect3):
        self.shift(point - self.get_arc_center())
        return self


class ArcBetweenPoints(Arc):
    def __init__(
        self,
        start: Vect3,
        end: Vect3,
        angle: float = TAU / 4,
        **kwargs
    ):
        super().__init__(angle=angle, **kwargs)
        if angle == 0:
            self.set_points_as_corners([LEFT, RIGHT])
        self.put_start_and_end_on(start, end)


class CurvedArrow(ArcBetweenPoints):
    def __init__(
        self,
        start_point: Vect3,
        end_point: Vect3,
        **kwargs
    ):
        super().__init__(start_point, end_point, **kwargs)
        self.add_tip()


class CurvedDoubleArrow(CurvedArrow):
    def __init__(
        self,
        start_point: Vect3,
        end_point: Vect3,
        **kwargs
    ):
        super().__init__(start_point, end_point, **kwargs)
        self.add_tip(at_start=True)


class Circle(Arc):
    def __init__(
        self,
        start_angle: float = 0,
        stroke_color: ManimColor = RED,
        **kwargs
    ):
        super().__init__(
            start_angle, TAU,
            stroke_color=stroke_color,
            **kwargs
        )

    def surround(
        self,
        mobject: Mobject,
        dim_to_match: int = 0,
        stretch: bool = False,
        buff: float = MED_SMALL_BUFF
    ):
        self.replace(mobject, dim_to_match, stretch)
        self.stretch((self.get_width() + 2 * buff) / self.get_width(), 0)
        self.stretch((self.get_height() + 2 * buff) / self.get_height(), 1)
        return self

    def point_at_angle(self, angle: float) -> Vect3:
        start_angle = self.get_start_angle()
        return self.point_from_proportion(
            ((angle - start_angle) % TAU) / TAU
        )

    def get_radius(self) -> float:
        return get_norm(self.get_start() - self.get_center())


class Dot(Circle):
    def __init__(
        self,
        point: Vect3 = ORIGIN,
        radius: float = DEFAULT_DOT_RADIUS,
        stroke_color: ManimColor = BLACK,
        stroke_width: float = 0.0,
        fill_opacity: float = 1.0,
        fill_color: ManimColor = WHITE,
        **kwargs
    ):
        super().__init__(
            arc_center=point,
            radius=radius,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            fill_opacity=fill_opacity,
            fill_color=fill_color,
            **kwargs
        )


class SmallDot(Dot):
    def __init__(
        self,
        point: Vect3 = ORIGIN,
        radius: float = DEFAULT_SMALL_DOT_RADIUS,
        **kwargs
    ):
        super().__init__(point, radius=radius, **kwargs)


class Ellipse(Circle):
    def __init__(
        self,
        width: float = 2.0,
        height: float = 1.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.set_width(width, stretch=True)
        self.set_height(height, stretch=True)


class AnnularSector(VMobject):
    def __init__(
        self,
        angle: float = TAU / 4,
        start_angle: float = 0.0,
        inner_radius: float = 1.0,
        outer_radius: float = 2.0,
        arc_center: Vect3 = ORIGIN,
        fill_color: ManimColor = GREY_A,
        fill_opacity: float = 1.0,
        stroke_width: float = 0.0,
        **kwargs,
    ):
        super().__init__(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs,
        )

        # Initialize points
        inner_arc, outer_arc = [
            Arc(
                start_angle=start_angle,
                angle=angle,
                radius=radius,
                arc_center=arc_center,
            )
            for radius in (inner_radius, outer_radius)
        ]
        self.append_points(inner_arc.get_points()[::-1])  # Reverse
        self.add_line_to(outer_arc.get_points()[0])
        self.append_points(outer_arc.get_points())
        self.add_line_to(inner_arc.get_points()[-1])


class Sector(AnnularSector):
    def __init__(
        self,
        angle: float = TAU / 4,
        radius: float = 1.0,
        **kwargs
    ):
        super().__init__(
            angle,
            inner_radius=0,
            outer_radius=radius,
            **kwargs
        )


class Annulus(VMobject):
    def __init__(
        self,
        inner_radius: float = 1.0,
        outer_radius: float = 2.0,
        fill_opacity: float = 1.0,
        stroke_width: float = 0.0,
        fill_color: ManimColor = GREY_A,
        center: Vect3 = ORIGIN,
        **kwargs,
    ):
        super().__init__(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs,
        )

        self.radius = outer_radius
        outer_circle = Circle(radius=outer_radius)
        inner_circle = Circle(radius=inner_radius)
        inner_circle.reverse_points()
        self.append_points(outer_circle.get_points())
        self.append_points(inner_circle.get_points())
        self.shift(center)


class Line(TipableVMobject):
    def __init__(
        self,
        start: Vect3 | Mobject = LEFT,
        end: Vect3 | Mobject = RIGHT,
        buff: float = 0.0,
        path_arc: float = 0.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.path_arc = path_arc
        self.set_start_and_end_attrs(start, end)
        self.set_points_by_ends(self.start, self.end, buff, path_arc)

    def set_points_by_ends(
        self,
        start: Vect3,
        end: Vect3,
        buff: float = 0,
        path_arc: float = 0
    ):
        vect = end - start
        dist = get_norm(vect)
        if np.isclose(dist, 0):
            self.set_points_as_corners([start, end])
            return self
        if path_arc:
            neg = path_arc < 0
            if neg:
                path_arc = -path_arc
                start, end = end, start
            radius = (dist / 2) / math.sin(path_arc / 2)
            alpha = (PI - path_arc) / 2
            center = start + radius * normalize(rotate_vector(end - start, alpha))

            raw_arc_points = Arc.create_quadratic_bezier_points(
                angle=path_arc - 2 * buff / radius,
                start_angle=angle_of_vector(start - center) + buff / radius,
            )
            if neg:
                raw_arc_points = raw_arc_points[::-1]
            self.set_points(center + radius * raw_arc_points)
        else:
            if buff > 0 and dist > 0:
                start = start + vect * (buff / dist)
                end = end - vect * (buff / dist)
            self.set_points_as_corners([start, end])
        return self

    def set_path_arc(self, new_value: float) -> None:
        self.path_arc = new_value
        self.init_points()

    def set_start_and_end_attrs(self, start: Vect3 | Mobject, end: Vect3 | Mobject):
        # If either start or end are Mobjects, this
        # gives their centers
        rough_start = self.pointify(start)
        rough_end = self.pointify(end)
        vect = normalize(rough_end - rough_start)
        # Now that we know the direction between them,
        # we can find the appropriate boundary point from
        # start and end, if they're mobjects
        self.start = self.pointify(start, vect)
        self.end = self.pointify(end, -vect)

    def pointify(
        self,
        mob_or_point: Mobject | Vect3,
        direction: Vect3 | None = None
    ) -> Vect3:
        """
        Take an argument passed into Line (or subclass) and turn
        it into a 3d point.
        """
        if isinstance(mob_or_point, Mobject):
            mob = mob_or_point
            if direction is None:
                return mob.get_center()
            else:
                return mob.get_continuous_bounding_box_point(direction)
        else:
            point = mob_or_point
            result = np.zeros(self.dim)
            result[:len(point)] = point
            return result

    def put_start_and_end_on(self, start: Vect3, end: Vect3):
        curr_start, curr_end = self.get_start_and_end()
        if np.isclose(curr_start, curr_end).all():
            # Handle null lines more gracefully
            self.set_points_by_ends(start, end, buff=0, path_arc=self.path_arc)
            return self
        return super().put_start_and_end_on(start, end)

    def get_vector(self) -> Vect3:
        return self.get_end() - self.get_start()

    def get_unit_vector(self) -> Vect3:
        return normalize(self.get_vector())

    def get_angle(self) -> float:
        return angle_of_vector(self.get_vector())

    def get_projection(self, point: Vect3) -> Vect3:
        """
        Return projection of a point onto the line
        """
        unit_vect = self.get_unit_vector()
        start = self.get_start()
        return start + np.dot(point - start, unit_vect) * unit_vect

    def get_slope(self) -> float:
        return np.tan(self.get_angle())

    def set_angle(self, angle: float, about_point: Vect3 | None = None):
        if about_point is None:
            about_point = self.get_start()
        self.rotate(
            angle - self.get_angle(),
            about_point=about_point,
        )
        return self

    def set_length(self, length: float, **kwargs):
        self.scale(length / self.get_length(), **kwargs)
        return self

    def get_arc_length(self) -> float:
        arc_len = get_norm(self.get_vector())
        if self.path_arc > 0:
            arc_len *= self.path_arc / (2 * math.sin(self.path_arc / 2))
        return arc_len


class DashedLine(Line):
    def __init__(
        self,
        start: Vect3 = LEFT,
        end: Vect3 = RIGHT,
        dash_length: float = DEFAULT_DASH_LENGTH,
        positive_space_ratio: float = 0.5,
        **kwargs
    ):
        super().__init__(start, end, **kwargs)

        num_dashes = self.calculate_num_dashes(dash_length, positive_space_ratio)
        dashes = DashedVMobject(
            self,
            num_dashes=num_dashes,
            positive_space_ratio=positive_space_ratio
        )
        self.clear_points()
        self.add(*dashes)

    def calculate_num_dashes(self, dash_length: float, positive_space_ratio: float) -> int:
        try:
            full_length = dash_length / positive_space_ratio
            return int(np.ceil(self.get_length() / full_length))
        except ZeroDivisionError:
            return 1

    def get_start(self) -> Vect3:
        if len(self.submobjects) > 0:
            return self.submobjects[0].get_start()
        else:
            return Line.get_start(self)

    def get_end(self) -> Vect3:
        if len(self.submobjects) > 0:
            return self.submobjects[-1].get_end()
        else:
            return Line.get_end(self)

    def get_first_handle(self) -> Vect3:
        return self.submobjects[0].get_points()[1]

    def get_last_handle(self) -> Vect3:
        return self.submobjects[-1].get_points()[-2]


class TangentLine(Line):
    def __init__(
        self,
        vmob: VMobject,
        alpha: float,
        length: float = 2,
        d_alpha: float = 1e-6,
        **kwargs
    ):
        a1 = clip(alpha - d_alpha, 0, 1)
        a2 = clip(alpha + d_alpha, 0, 1)
        super().__init__(vmob.pfp(a1), vmob.pfp(a2), **kwargs)
        self.scale(length / self.get_length())


class Elbow(VMobject):
    def __init__(
        self,
        width: float = 0.2,
        angle: float = 0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.set_points_as_corners([UP, UR, RIGHT])
        self.set_width(width, about_point=ORIGIN)
        self.rotate(angle, about_point=ORIGIN)


class Arrow(Line):
    def __init__(
        self,
        start: Vect3 | Mobject,
        end: Vect3 | Mobject,
        stroke_color: ManimColor = GREY_A,
        stroke_width: float = 5,
        buff: float = 0.25,
        tip_width_ratio: float = 5,
        width_to_tip_len: float = 0.0075,
        max_tip_length_to_length_ratio: float = 0.3,
        max_width_to_length_ratio: float = 8.0,
        **kwargs,
    ):
        self.tip_width_ratio = tip_width_ratio
        self.width_to_tip_len = width_to_tip_len
        self.max_tip_length_to_length_ratio = max_tip_length_to_length_ratio
        self.max_width_to_length_ratio = max_width_to_length_ratio
        self.max_stroke_width = stroke_width
        super().__init__(
            start, end,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            buff=buff,
            **kwargs
        )

    def set_points_by_ends(
        self,
        start: Vect3,
        end: Vect3,
        buff: float = 0,
        path_arc: float = 0
    ):
        super().set_points_by_ends(start, end, buff, path_arc)
        self.insert_tip_anchor()
        self.create_tip_with_stroke_width()
        return self

    def insert_tip_anchor(self):
        prev_end = self.get_end()
        arc_len = self.get_arc_length()
        tip_len = self.get_stroke_width() * self.width_to_tip_len * self.tip_width_ratio
        if tip_len >= self.max_tip_length_to_length_ratio * arc_len:
            alpha = self.max_tip_length_to_length_ratio
        else:
            alpha = tip_len / arc_len
        self.pointwise_become_partial(self, 0, 1 - alpha)
        self.start_new_path(self.get_points()[-1])
        self.add_line_to(prev_end)
        return self

    def create_tip_with_stroke_width(self):
        if not self.has_points():
            return self
        width = min(
            self.max_stroke_width,
            self.max_width_to_length_ratio * self.get_length(),
        )
        widths_array = np.full(self.get_num_points(), width)
        if len(widths_array) > 3:
            tip_width = self.tip_width_ratio * width
            widths_array[-3:] = tip_width * np.linspace(1, 0, 3)
            self.set_stroke(width=widths_array)
        return self

    def reset_tip(self):
        self.set_points_by_ends(
            self.get_start(), self.get_end(),
            path_arc=self.path_arc
        )
        return self

    def set_stroke(
        self,
        color: ManimColor | Iterable[ManimColor] | None = None,
        width: float | Iterable[float] | None = None,
        *args, **kwargs
    ):
        super().set_stroke(color=color, width=width, *args, **kwargs)
        if isinstance(width, numbers.Number):
            self.max_stroke_width = width
            self.create_tip_with_stroke_width()
        return self

    def _handle_scale_side_effects(self, scale_factor: float):
        return self.reset_tip()


class FillArrow(Line):
    def __init__(
        self,
        start: Vect3 | Mobject = LEFT,
        end: Vect3 | Mobject = LEFT,
        fill_color: ManimColor = GREY_A,
        fill_opacity: float = 1.0,
        stroke_width: float = 0.0,
        buff: float = MED_SMALL_BUFF,
        thickness: float = 0.05,
        tip_width_ratio: float = 5,
        tip_angle: float = PI / 3,
        max_tip_length_to_length_ratio: float = 0.5,
        max_width_to_length_ratio: float = 0.1,
        **kwargs,
    ):
        self.thickness = thickness
        self.tip_width_ratio = tip_width_ratio
        self.tip_angle = tip_angle
        self.max_tip_length_to_length_ratio = max_tip_length_to_length_ratio
        self.max_width_to_length_ratio = max_width_to_length_ratio
        super().__init__(
            start, end,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            buff=buff,
            **kwargs
        )

    def set_points_by_ends(
        self,
        start: Vect3,
        end: Vect3,
        buff: float = 0,
        path_arc: float = 0
    ) -> None:
        # Find the right tip length and thickness
        vect = end - start
        length = max(get_norm(vect), 1e-8)
        thickness = self.thickness
        w_ratio = fdiv(self.max_width_to_length_ratio, fdiv(thickness, length))
        if w_ratio < 1:
            thickness *= w_ratio

        tip_width = self.tip_width_ratio * thickness
        tip_length = tip_width / (2 * np.tan(self.tip_angle / 2))
        t_ratio = fdiv(self.max_tip_length_to_length_ratio, fdiv(tip_length, length))
        if t_ratio < 1:
            tip_length *= t_ratio
            tip_width *= t_ratio

        # Find points for the stem
        if path_arc == 0:
            points1 = (length - tip_length) * np.array([RIGHT, 0.5 * RIGHT, ORIGIN])
            points1 += thickness * UP / 2
            points2 = points1[::-1] + thickness * DOWN
        else:
            # Solve for radius so that the tip-to-tail length matches |end - start|
            a = 2 * (1 - np.cos(path_arc))
            b = -2 * tip_length * np.sin(path_arc)
            c = tip_length**2 - length**2
            R = (-b + np.sqrt(b**2 - 4 * a * c)) / (2 * a)

            # Find arc points
            points1 = Arc.create_quadratic_bezier_points(path_arc)
            points2 = np.array(points1[::-1])
            points1 *= (R + thickness / 2)
            points2 *= (R - thickness / 2)
            if path_arc < 0:
                tip_length *= -1
            rot_T = rotation_matrix_transpose(PI / 2 - path_arc, OUT)
            for points in points1, points2:
                points[:] = np.dot(points, rot_T)
                points += R * DOWN

        self.set_points(points1)
        # Tip
        self.add_line_to(tip_width * UP / 2)
        self.add_line_to(tip_length * LEFT)
        self.tip_index = len(self.get_points()) - 1
        self.add_line_to(tip_width * DOWN / 2)
        self.add_line_to(points2[0])
        # Close it out
        self.append_points(points2)
        self.add_line_to(points1[0])

        if length > 0 and self.get_length() > 0:
            # Final correction
            super().scale(length / self.get_length())

        self.rotate(angle_of_vector(vect) - self.get_angle())
        self.rotate(
            PI / 2 - np.arccos(normalize(vect)[2]),
            axis=rotate_vector(self.get_unit_vector(), -PI / 2),
        )
        self.shift(start - self.get_start())
        self.refresh_triangulation()

    def reset_points_around_ends(self):
        self.set_points_by_ends(
            self.get_start().copy(), self.get_end().copy(), path_arc=self.path_arc
        )
        return self

    def get_start(self) -> Vect3:
        nppc = self.n_points_per_curve
        points = self.get_points()
        return (points[0] + points[-nppc]) / 2

    def get_end(self) -> Vect3:
        return self.get_points()[self.tip_index]

    def put_start_and_end_on(self, start: Vect3, end: Vect3):
        self.set_points_by_ends(start, end, buff=0, path_arc=self.path_arc)
        return self

    def scale(self, *args, **kwargs):
        super().scale(*args, **kwargs)
        self.reset_points_around_ends()
        return self

    def set_thickness(self, thickness: float):
        self.thickness = thickness
        self.reset_points_around_ends()
        return self

    def set_path_arc(self, path_arc: float):
        self.path_arc = path_arc
        self.reset_points_around_ends()
        return self


class Vector(Arrow):
    def __init__(
        self,
        direction: Vect3 = RIGHT,
        buff: float = 0.0,
        **kwargs
    ):
        if len(direction) == 2:
            direction = np.hstack([direction, 0])
        super().__init__(ORIGIN, direction, buff=buff, **kwargs)


class CubicBezier(VMobject):
    def __init__(
        self,
        a0: Vect3,
        h0: Vect3,
        h1: Vect3,
        a1: Vect3,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.add_cubic_bezier_curve(a0, h0, h1, a1)


class Polygon(VMobject):
    def __init__(self, *vertices: Vect3, **kwargs):
        super().__init__(**kwargs)
        self.set_points_as_corners([*vertices, vertices[0]])

    def get_vertices(self) -> Vect3Array:
        return self.get_start_anchors()

    def round_corners(self, radius: float | None = None):
        if radius is None:
            verts = self.get_vertices()
            min_edge_length = min(
                get_norm(v1 - v2)
                for v1, v2 in zip(verts, verts[1:])
                if not np.isclose(v1, v2).all()
            )
            radius = 0.25 * min_edge_length
        vertices = self.get_vertices()
        arcs = []
        for v1, v2, v3 in adjacent_n_tuples(vertices, 3):
            vect1 = v2 - v1
            vect2 = v3 - v2
            unit_vect1 = normalize(vect1)
            unit_vect2 = normalize(vect2)
            angle = angle_between_vectors(vect1, vect2)
            # Negative radius gives concave curves
            angle *= np.sign(radius)
            # Distance between vertex and start of the arc
            cut_off_length = radius * np.tan(angle / 2)
            # Determines counterclockwise vs. clockwise
            sign = np.sign(np.cross(vect1, vect2)[2])
            arc = ArcBetweenPoints(
                v2 - unit_vect1 * cut_off_length,
                v2 + unit_vect2 * cut_off_length,
                angle=sign * angle,
                n_components=2,
            )
            arcs.append(arc)

        self.clear_points()
        # To ensure that we loop through starting with last
        arcs = [arcs[-1], *arcs[:-1]]
        for arc1, arc2 in adjacent_pairs(arcs):
            self.append_points(arc1.get_points())
            line = Line(arc1.get_end(), arc2.get_start())
            # Make sure anchors are evenly distributed
            len_ratio = line.get_length() / arc1.get_arc_length()
            line.insert_n_curves(
                int(arc1.get_num_curves() * len_ratio)
            )
            self.append_points(line.get_points())
        return self


class Polyline(VMobject):
    def __init__(self, *vertices: Vect3, **kwargs):
        super().__init__(**kwargs)
        self.set_points_as_corners(vertices)


class RegularPolygon(Polygon):
    def __init__(
        self,
        n: int = 6,
        radius: float = 1.0,
        start_angle: float | None = None,
        **kwargs
    ):
        # Defaults to 0 for odd, 90 for even
        start_angle = start_angle or (n % 2) * 90 * DEGREES
        start_vect = rotate_vector(radius * RIGHT, start_angle)
        vertices = compass_directions(n, start_vect)
        super().__init__(*vertices, **kwargs)


class Triangle(RegularPolygon):
    def __init__(self, **kwargs):
        super().__init__(n=3, **kwargs)


class ArrowTip(Triangle):
    def __init__(
        self,
        angle: float = 0,
        width: float = DEFAULT_ARROW_TIP_WIDTH,
        length: float = DEFAULT_ARROW_TIP_LENGTH,
        fill_opacity: float = 1.0,
        fill_color: ManimColor = WHITE,
        stroke_width: float = 0.0,
        tip_style: int = 0,  # triangle=0, inner_smooth=1, dot=2
        **kwargs
    ):
        super().__init__(
            start_angle=0,
            fill_opacity=fill_opacity,
            fill_color=fill_color,
            stroke_width=stroke_width,
            **kwargs
        )
        self.set_height(width)
        self.set_width(length, stretch=True)
        if tip_style == 1:
            self.set_height(length * 0.9, stretch=True)
            self.data["points"][4] += np.array([0.6 * length, 0, 0])
        elif tip_style == 2:
            h = length / 2
            self.set_points(Dot().set_width(h).get_points())
        self.rotate(angle)

    def get_base(self) -> Vect3:
        return self.point_from_proportion(0.5)

    def get_tip_point(self) -> Vect3:
        return self.get_points()[0]

    def get_vector(self) -> Vect3:
        return self.get_tip_point() - self.get_base()

    def get_angle(self) -> float:
        return angle_of_vector(self.get_vector())

    def get_length(self) -> float:
        return get_norm(self.get_vector())


class Rectangle(Polygon):
    def __init__(
        self,
        width: float = 4.0,
        height: float = 2.0,
        **kwargs
    ):
        super().__init__(UR, UL, DL, DR, **kwargs)
        self.set_width(width, stretch=True)
        self.set_height(height, stretch=True)


class Square(Rectangle):
    def __init__(self, side_length: float = 2.0, **kwargs):
        super().__init__(side_length, side_length, **kwargs)


class RoundedRectangle(Rectangle):
    def __init__(
        self,
        width: float = 4.0,
        height: float = 2.0,
        corner_radius: float = 0.5,
        **kwargs
    ):
        super().__init__(width, height, **kwargs)
        self.round_corners(corner_radius)
