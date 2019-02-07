import warnings
import numpy as np

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import DashedVMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import center_of_mass
from manimlib.utils.space_ops import compass_directions
from manimlib.utils.space_ops import line_intersection
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import normalize
from manimlib.utils.space_ops import rotate_vector


DEFAULT_DOT_RADIUS = 0.08
DEFAULT_DASH_LENGTH = 0.05


class Arc(VMobject):
    CONFIG = {
        "radius": 1.0,
        "num_components": 9,
        "anchors_span_full_range": True,
        "arc_center": ORIGIN,
    }

    def __init__(self, start_angle=0, angle=TAU / 4, **kwargs):
        self.start_angle = start_angle
        self.angle = angle
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        self.set_pre_positioned_points()
        self.scale(self.radius, about_point=ORIGIN)
        self.shift(self.arc_center)

    def set_pre_positioned_points(self):
        anchors = np.array([
            np.cos(a) * RIGHT + np.sin(a) * UP
            for a in np.linspace(
                self.start_angle,
                self.start_angle + self.angle,
                self.num_components,
            )
        ])
        # Figure out which control points will give the
        # Appropriate tangent lines to the circle
        d_theta = self.angle / (self.num_components - 1.0)
        tangent_vectors = np.zeros(anchors.shape)
        # Rotate all 90 degress, via (x, y) -> (-y, x)
        tangent_vectors[:, 1] = anchors[:, 0]
        tangent_vectors[:, 0] = -anchors[:, 1]
        # Use tangent vectors to deduce anchors
        handles1 = anchors[:-1] + (d_theta / 3) * tangent_vectors[:-1]
        handles2 = anchors[1:] - (d_theta / 3) * tangent_vectors[1:]
        self.set_anchors_and_handles(
            anchors[:-1],
            handles1, handles2,
            anchors[1:],
        )

    def add_tip(self, tip_length=0.25, at_start=False):
        tip = self.tip = Triangle(start_angle=PI)
        tip.match_style(self)
        tip.set_fill(self.get_stroke_color(), opacity=1)
        tip.set_height(tip_length)
        tip.set_width(tip_length, stretch=True)
        tip.move_to(ORIGIN, LEFT)
        # Last two control points, defining both
        # the end, and the tangency direction
        if at_start:
            end, handle = self.points[:2]
        else:
            handle, end = self.points[-2:]
        tip.rotate(
            angle_of_vector(handle - end),
            about_point=ORIGIN
        )
        tip.shift(end)
        self.add(tip)
        return self

    def get_arc_center(self):
        """
        Looks at the normals to the first two
        anchors, and finds their intersection points
        """
        # First two anchors and handles
        a1, h1, h2, a2 = self.points[:4]
        # Tangent vectors
        t1 = h1 - a1
        t2 = h2 - a2
        # Normals
        n1 = rotate_vector(t1, TAU / 4)
        n2 = rotate_vector(t2, TAU / 4)
        try:
            return line_intersection(
                line1=(a1, a1 + n1),
                line2=(a2, a2 + n2),
            )
        except Exception:
            warnings.warn("Can't find Arc center, using ORIGIN instead")
            return np.array(ORIGIN)

    def move_arc_center_to(self, point):
        self.shift(point - self.get_arc_center())
        return self

    def stop_angle(self):
        return angle_of_vector(
            self.points[-1] - self.get_arc_center()
        ) % TAU


class ArcBetweenPoints(Arc):
    def __init__(self, start_point, end_point, angle=TAU / 4, **kwargs):
        Arc.__init__(
            self,
            angle=angle,
            **kwargs,
        )
        if angle == 0:
            self.set_points_as_corners([LEFT, RIGHT])
        self.put_start_and_end_on(start_point, end_point)


class CurvedArrow(ArcBetweenPoints):
    def __init__(self, start_point, end_point, **kwargs):
        ArcBetweenPoints.__init__(self, start_point, end_point, **kwargs)
        self.add_tip()


class CurvedDoubleArrow(CurvedArrow):
    def __init__(self, start_point, end_point, **kwargs):
        CurvedArrow.__init__(
            self, start_point, end_point, **kwargs
        )
        self.add_tip(at_start=True)


class Circle(Arc):
    CONFIG = {
        "color": RED,
        "close_new_points": True,
        "anchors_span_full_range": False
    }

    def __init__(self, **kwargs):
        Arc.__init__(self, 0, TAU, **kwargs)

    def surround(self, mobject, dim_to_match=0, stretch=False, buffer_factor=1.2):
        # Ignores dim_to_match and stretch; result will always be a circle
        # TODO: Perhaps create an ellipse class to handle singele-dimension stretching

        # Something goes wrong here when surrounding lines?
        # TODO: Figure out and fix
        self.replace(mobject, dim_to_match, stretch)

        self.set_width(
            np.sqrt(mobject.get_width()**2 + mobject.get_height()**2)
        )
        self.scale(buffer_factor)

    def point_at_angle(self, angle):
        start_angle = angle_of_vector(
            self.points[0] - self.get_center()
        )
        return self.point_from_proportion(
            (angle - start_angle) / TAU
        )


class Dot(Circle):
    CONFIG = {
        "radius": DEFAULT_DOT_RADIUS,
        "stroke_width": 0,
        "fill_opacity": 1.0,
        "color": WHITE
    }

    def __init__(self, point=ORIGIN, **kwargs):
        Circle.__init__(self, arc_center=point, **kwargs)


class Ellipse(Circle):
    CONFIG = {
        "width": 2,
        "height": 1
    }

    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)
        self.set_width(width, stretch=True)
        self.set_height(width, stretch=True)


class AnnularSector(Arc):
    CONFIG = {
        "inner_radius": 1,
        "outer_radius": 2,
        "angle": TAU / 4,
        "start_angle": 0,
        "fill_opacity": 1,
        "stroke_width": 0,
        "color": WHITE,
    }

    def generate_points(self):
        inner_arc, outer_arc = [
            Arc(
                start_angle=self.start_angle,
                angle=self.angle,
                radius=radius,
                arc_center=self.arc_center,
            )
            for radius in (self.inner_radius, self.outer_radius)
        ]
        outer_arc.reverse_points()
        self.append_points(inner_arc.points)
        self.add_line_to(outer_arc.points[0])
        self.append_points(outer_arc.points)
        self.add_line_to(inner_arc.points[0])


class Sector(AnnularSector):
    CONFIG = {
        "outer_radius": 1,
        "inner_radius": 0
    }


class Annulus(Circle):
    CONFIG = {
        "inner_radius": 1,
        "outer_radius": 2,
        "fill_opacity": 1,
        "stroke_width": 0,
        "color": WHITE,
        "mark_paths_closed": False,
    }

    def generate_points(self):
        self.radius = self.outer_radius
        outer_circle = Circle(radius=self.outer_radius)
        inner_circle = Circle(radius=self.inner_radius)
        inner_circle.reverse_points()
        self.append_points(outer_circle.points)
        self.append_points(inner_circle.points)
        self.shift(self.arc_center)


class Line(VMobject):
    CONFIG = {
        "buff": 0,
        "path_arc": None,  # angle of arc specified here
    }

    def __init__(self, start, end, **kwargs):
        digest_config(self, kwargs)
        self.set_start_and_end(start, end)
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        if self.path_arc:
            arc = ArcBetweenPoints(
                self.start, self.end,
                angle=self.path_arc
            )
            self.set_points(arc.points)
        else:
            self.set_points_as_corners([self.start, self.end])
        self.account_for_buff()

    def set_path_arc(self, new_value):
        self.path_arc = new_value
        self.generate_points()

    def account_for_buff(self):
        if self.buff == 0:
            return
        length = self.get_arc_length()
        if length < 2 * self.buff:
            return
        buff_proportion = self.buff / length
        self.pointwise_become_partial(
            self, buff_proportion, 1 - buff_proportion
        )

    def set_start_and_end(self, start, end):
        # If either start or end are Mobjects, this
        # gives their centers
        rough_start = self.pointify(start)
        rough_end = self.pointify(end)
        vect = normalize(rough_end - rough_start)
        # Now that we know the direction between them,
        # we can the appropriate boundary point from
        # start and end, if they're mobjects
        self.start = self.pointify(start, vect)
        self.end = self.pointify(end, -vect)

    def pointify(self, mob_or_point, direction=None):
        if isinstance(mob_or_point, Mobject):
            mob = mob_or_point
            if direction is None:
                return mob.get_center()
            else:
                return mob.get_boundary_point(direction)
        return np.array(mob_or_point)

    def get_length(self):
        start, end = self.get_start_and_end()
        return get_norm(start - end)

    def get_arc_length(self):
        if self.path_arc:
            points = np.array([
                self.point_from_proportion(a)
                for a in np.linspace(0, 1, 100)
            ])
            diffs = points[1:] - points[:-1]
            norms = np.apply_along_axis(get_norm, 1, diffs)
            return np.sum(norms)
        else:
            return self.get_length()

    def get_vector(self):
        return self.get_end() - self.get_start()

    def get_unit_vector(self):
        return normalize(self.get_vector())

    def get_angle(self):
        return angle_of_vector(self.get_vector())

    def get_slope(self):
        return np.tan(self.get_angle())

    def set_angle(self, angle):
        self.rotate(
            angle - self.get_angle(),
            about_point=self.get_start(),
        )


class DashedLine(Line):
    CONFIG = {
        "dash_length": DEFAULT_DASH_LENGTH,
        "dash_spacing": None,
        "positive_space_ratio": 0.5,
    }

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        ps_ratio = self.positive_space_ratio
        num_dashes = self.calculate_num_dashes(ps_ratio)
        dashes = DashedVMobject(
            self,
            num_dashes=num_dashes,
            positive_space_ratio=ps_ratio
        )
        self.clear_points()
        self.add(*dashes)

    def calculate_num_dashes(self, positive_space_ratio):
        try:
            full_length = self.dash_length / positive_space_ratio
            return int(np.ceil(
                self.get_length() / full_length
            ))
        except ZeroDivisionError:
            return 1

    def calculate_positive_space_ratio(self):
        return fdiv(
            self.dash_length,
            self.dash_length + self.dash_spacing,
        )

    def get_start(self):
        if len(self.submobjects) > 0:
            return self.submobjects[0].get_start()
        else:
            return Line.get_start(self)

    def get_end(self):
        if len(self.submobjects) > 0:
            return self.submobjects[-1].get_end()
        else:
            return Line.get_end(self)


class Elbow(VMobject):
    CONFIG = {
        "width": 0.2,
        "angle": 0,
    }

    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points_as_corners([UP, UP + RIGHT, RIGHT])
        self.set_width(self.width, about_point=ORIGIN)
        self.rotate(self.angle, about_point=ORIGIN)


class Arrow(Line):
    CONFIG = {
        "tip_length": 0.25,
        "tip_width_to_length_ratio": 1,
        "max_tip_length_to_length_ratio": 0.35,
        "max_stem_width_to_tip_width_ratio": 0.3,
        "buff": MED_SMALL_BUFF,
        "preserve_tip_size_when_scaling": True,
        "normal_vector": OUT,
        "use_rectangular_stem": True,
        "rectangular_stem_width": 0.05,
    }

    def __init__(self, *args, **kwargs):
        points = list(map(self.pointify, args))
        if len(args) == 1:
            args = (points[0] + UP + LEFT, points[0])
        Line.__init__(self, *args, **kwargs)
        self.init_tip()
        if self.use_rectangular_stem and not hasattr(self, "rect"):
            self.add_rectangular_stem()
        self.init_colors()

    def init_tip(self):
        self.add_tip()

    def add_tip(self, add_at_end=True):
        tip = VMobject(
            close_new_points=True,
            mark_paths_closed=True,
            fill_color=self.color,
            fill_opacity=1,
            stroke_color=self.color,
            stroke_width=0,
        )
        tip.add_at_end = add_at_end
        self.set_tip_points(tip, add_at_end, preserve_normal=False)
        self.add(tip)
        if not hasattr(self, 'tip'):
            self.tip = VGroup()
            self.tip.match_style(tip)
        self.tip.add(tip)
        return tip

    def add_rectangular_stem(self):
        self.rect = Rectangle(
            stroke_width=0,
            fill_color=self.tip.get_fill_color(),
            fill_opacity=self.tip.get_fill_opacity()
        )
        self.add_to_back(self.rect)
        self.set_stroke(width=0)
        self.set_rectangular_stem_points()

    def set_rectangular_stem_points(self):
        start, end = self.get_start_and_end()
        tip_base_points = self.tip[0].get_anchors()[1:3]
        tip_base = center_of_mass(tip_base_points)
        tbp1, tbp2 = tip_base_points
        perp_vect = tbp2 - tbp1
        tip_base_width = get_norm(perp_vect)
        if tip_base_width > 0:
            perp_vect /= tip_base_width
        width = min(
            self.rectangular_stem_width,
            self.max_stem_width_to_tip_width_ratio * tip_base_width,
        )
        if hasattr(self, "second_tip"):
            start = center_of_mass(
                self.second_tip.get_anchors()[1:]
            )
        self.rect.set_points_as_corners([
            tip_base - perp_vect * width / 2,
            start - perp_vect * width / 2,
            start + perp_vect * width / 2,
            tip_base + perp_vect * width / 2,
        ])
        self.stem = self.rect  # Alternate name
        return self

    def set_tip_points(
        self, tip,
        add_at_end=True,
        tip_length=None,
        preserve_normal=True,
    ):
        if tip_length is None:
            tip_length = self.tip_length
        if preserve_normal:
            normal_vector = self.get_normal_vector()
        else:
            normal_vector = self.normal_vector
        line_length = get_norm(self.points[-1] - self.points[0])
        tip_length = min(
            tip_length, self.max_tip_length_to_length_ratio * line_length
        )

        indices = (-2, -1) if add_at_end else (1, 0)
        pre_end_point, end_point = [
            self.get_anchors()[index]
            for index in indices
        ]
        vect = end_point - pre_end_point
        perp_vect = np.cross(vect, normal_vector)
        for v in vect, perp_vect:
            if get_norm(v) == 0:
                v[0] = 1
            v *= tip_length / get_norm(v)
        ratio = self.tip_width_to_length_ratio
        tip.set_points_as_corners([
            end_point,
            end_point - vect + perp_vect * ratio / 2,
            end_point - vect - perp_vect * ratio / 2,
        ])

        return self

    def get_normal_vector(self):
        p0, p1, p2 = self.tip[0].get_anchors()[:3]
        result = np.cross(p2 - p1, p1 - p0)
        norm = get_norm(result)
        if norm == 0:
            return self.normal_vector
        else:
            return result / norm

    def reset_normal_vector(self):
        self.normal_vector = self.get_normal_vector()
        return self

    def get_end(self):
        if hasattr(self, "tip"):
            return self.tip[0].get_anchors()[0]
        else:
            return Line.get_end(self)

    def get_tip(self):
        return self.tip

    def put_start_and_end_on(self, *args, **kwargs):
        Line.put_start_and_end_on(self, *args, **kwargs)
        self.set_tip_points(self.tip[0], preserve_normal=False)
        self.set_rectangular_stem_points()
        return self

    def scale(self, scale_factor, **kwargs):
        Line.scale(self, scale_factor, **kwargs)
        if self.preserve_tip_size_when_scaling:
            for t in self.tip:
                self.set_tip_points(t, add_at_end=t.add_at_end)
        if self.use_rectangular_stem:
            self.set_rectangular_stem_points()
        return self

    def copy(self):
        return self.deepcopy()


class Vector(Arrow):
    CONFIG = {
        "color": YELLOW,
        "buff": 0,
    }

    def __init__(self, direction, **kwargs):
        if len(direction) == 2:
            direction = np.append(np.array(direction), 0)
        Arrow.__init__(self, ORIGIN, direction, **kwargs)


class DoubleArrow(Arrow):
    def init_tip(self):
        self.tip = VGroup()
        for b in True, False:
            t = self.add_tip(add_at_end=b)
            t.add_at_end = b
            self.tip.add(t)
        self.tip.match_style(self.tip[0])


class CubicBezier(VMobject):
    def __init__(self, points, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points(points)


class Polygon(VMobject):
    CONFIG = {
        "color": GREEN_D,
        "mark_paths_closed": True,
        "close_new_points": True,
    }

    def __init__(self, *vertices, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points_as_corners(
            [*vertices, vertices[0]]
        )

    def get_vertices(self):
        return self.get_start_anchors()


class RegularPolygon(Polygon):
    CONFIG = {
        "start_angle": 0
    }

    def __init__(self, n=6, **kwargs):
        digest_config(self, kwargs, locals())
        start_vect = rotate_vector(RIGHT, self.start_angle)
        vertices = compass_directions(n, start_vect)
        Polygon.__init__(self, *vertices, **kwargs)


class Triangle(RegularPolygon):
    def __init__(self, **kwargs):
        RegularPolygon.__init__(self, n=3, **kwargs)


class Rectangle(Polygon):
    CONFIG = {
        "color": WHITE,
        "height": 2.0,
        "width": 4.0,
        "mark_paths_closed": True,
        "close_new_points": True,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        x, y = self.width / 2., self.height / 2.
        vertices = [
            x * LEFT + y * UP,
            x * RIGHT + y * UP,
            x * RIGHT + y * DOWN,
            x * LEFT + y * DOWN
        ]
        Polygon.__init__(self, *vertices, **kwargs)


class Square(Rectangle):
    CONFIG = {
        "side_length": 2.0,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Rectangle.__init__(
            self,
            height=self.side_length,
            width=self.side_length,
            **kwargs
        )


class RoundedRectangle(Rectangle):
    CONFIG = {
        "corner_radius": 0.5,
        "close_new_points": True
    }

    def generate_points(self):
        y, x = self.height / 2., self.width / 2.
        r = self.corner_radius

        arc_ul = ArcBetweenPoints(x * LEFT + (y - r) * UP, (x - r) * LEFT + y * UP, angle = -TAU/4)
        arc_ur = ArcBetweenPoints((x - r) * RIGHT + y * UP, x * RIGHT + (y - r) * UP, angle = -TAU/4)
        arc_lr = ArcBetweenPoints(x * RIGHT + (y - r) * DOWN, (x - r) * RIGHT + y * DOWN, angle = -TAU/4)
        arc_ll = ArcBetweenPoints(x * LEFT + (y - r) * DOWN, (x - r) * LEFT + y * DOWN, angle = TAU/4) # sic! bug in ArcBetweenPoints?
        
        points = arc_ul.points
        points = np.append(points,np.array([y * UP]), axis = 0)
        points = np.append(points,np.array([y * UP]), axis = 0)
        points = np.append(points,arc_ur.points, axis = 0)
        points = np.append(points,np.array([x * RIGHT]), axis = 0)
        points = np.append(points,np.array([x * RIGHT]), axis = 0)
        points = np.append(points,arc_lr.points, axis = 0)
        points = np.append(points,np.array([y * DOWN]), axis = 0)
        points = np.append(points,np.array([y * DOWN]), axis = 0)
        points = np.append(points,arc_ll.points[::-1], axis = 0) # sic! see comment above
        points = np.append(points,np.array([x * LEFT]), axis = 0)
        points = np.append(points,np.array([x * LEFT]), axis = 0)
        points = np.append(points,np.array([x * LEFT + (y - r) * UP]), axis = 0)

        points = points[::-1]

        self.set_points(points)


class Grid(VMobject):
    CONFIG = {
        "height": 6.0,
        "width": 6.0,
    }

    def __init__(self, rows, columns, **kwargs):
        digest_config(self, kwargs, locals())
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        x_step = self.width / self.columns
        y_step = self.height / self.rows

        for x in np.arange(0, self.width + x_step, x_step):
            self.add(Line(
                [x - self.width / 2., -self.height / 2., 0],
                [x - self.width / 2., self.height / 2., 0],
            ))
        for y in np.arange(0, self.height + y_step, y_step):
            self.add(Line(
                [-self.width / 2., y - self.height / 2., 0],
                [self.width / 2., y - self.height / 2., 0]
            ))
