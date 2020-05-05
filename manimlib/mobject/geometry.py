import warnings
import numpy as np

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import DashedVMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import adjacent_n_tuples
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import angle_between_vectors
from manimlib.utils.space_ops import compass_directions
from manimlib.utils.space_ops import line_intersection
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import normalize
from manimlib.utils.space_ops import rotate_vector


DEFAULT_DOT_RADIUS = 0.08
DEFAULT_SMALL_DOT_RADIUS = 0.04
DEFAULT_DASH_LENGTH = 0.05
DEFAULT_ARROW_TIP_LENGTH = 0.35


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
    CONFIG = {
        "tip_length": DEFAULT_ARROW_TIP_LENGTH,
        # TODO
        "normal_vector": OUT,
        "tip_style": {
            "fill_opacity": 1,
            "stroke_width": 0,
        }
    }
    
    # Adding, Creating, Modifying tips

    def add_tip(self, tip_length=None, at_start=False):
        """
        Adds a tip to the TipableVMobject instance, recognising
        that the endpoints might need to be switched if it's
        a 'starting tip' or not.
        """
        tip = self.create_tip(tip_length, at_start)
        self.reset_endpoints_based_on_tip(tip, at_start)
        self.asign_tip_attr(tip, at_start)
        self.add(tip)
        return self

    def create_tip(self, tip_length=None, at_start=False):
        """
        Stylises the tip, positions it spacially, and returns
        the newly instantiated tip to the caller.
        """
        tip = self.get_unpositioned_tip(tip_length)
        self.position_tip(tip, at_start)
        return tip

    def get_unpositioned_tip(self, tip_length=None):
        """
        Returns a tip that has been stylistically configured,
        but has not yet been given a position in space.
        """
        if tip_length is None:
            tip_length = self.get_default_tip_length()
        color = self.get_color()
        style = {
            "fill_color": color,
            "stroke_color": color
        }
        style.update(self.tip_style)
        tip = ArrowTip(length=tip_length, **style)
        return tip

    def position_tip(self, tip, at_start=False):
        # Last two control points, defining both
        # the end, and the tangency direction
        if at_start:
            anchor = self.get_start()
            handle = self.get_first_handle()
        else:
            handle = self.get_last_handle()
            anchor = self.get_end()
        tip.rotate(
            angle_of_vector(handle - anchor) -
            PI - tip.get_angle()
        )
        tip.shift(anchor - tip.get_tip_point())
        return tip

    def reset_endpoints_based_on_tip(self, tip, at_start):
        if self.get_length() == 0:
            # Zero length, put_start_and_end_on wouldn't
            # work
            return self

        if at_start:
            self.put_start_and_end_on(
                tip.get_base(), self.get_end()
            )
        else:
            self.put_start_and_end_on(
                self.get_start(), tip.get_base(),
            )
        return self

    def asign_tip_attr(self, tip, at_start):
        if at_start:
            self.start_tip = tip
        else:
            self.tip = tip
        return self

    # Checking for tips

    def has_tip(self):
        return hasattr(self, "tip") and self.tip in self

    def has_start_tip(self):
        return hasattr(self, "start_tip") and self.start_tip in self


    # Getters

    def pop_tips(self):
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

    def get_tips(self):
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

    def get_tip(self):
        """Returns the TipableVMobject instance's (first) tip,
        otherwise throws an exception."""
        tips = self.get_tips()
        if len(tips) == 0:
            raise Exception("tip not found")
        else:
            return tips[0]

    def get_default_tip_length(self):
        return self.tip_length

    def get_first_handle(self):
        return self.points[1]

    def get_last_handle(self):
        return self.points[-2]

    def get_end(self):
        if self.has_tip():
            return self.tip.get_start()
        else:
            return VMobject.get_end(self)

    def get_start(self):
        if self.has_start_tip():
            return self.start_tip.get_start()
        else:
            return VMobject.get_start(self)

    def get_length(self):
        start, end = self.get_start_and_end()
        return get_norm(start - end)


class Arc(TipableVMobject):
    '''
    Creates an arc.

    Parameters
    -----
    radius : float
        Radius of the arc
    start_angle : float
        Starting angle of the arc in radians. (Angles are measured counter-clockwise)
    angle : float
        Angle subtended by the arc at its center in radians. (Angles are measured counter-clockwise)
    arc_center : array_like
        Center of the arc
    Examples :
            arc = Arc(radius = 3, start_angle = TAU/4, angle = TAU/2, arc_center = ORIGIN)

            arc = Arc(radius = 4.5, angle = TAU/4, arc_center = (1,2,0), color = BLUE)

    Returns
    -----
    out : Arc object
        An Arc object satisfying the specified parameters
    '''
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
    '''
    Creates an arc passing through the specified points with "angle" as the
    angle subtended at its center.

    Parameters
    -----
    start : array_like
        Starting point of the arc
    end : array_like
        Ending point of the arc
    angle : float
        Angle subtended by the arc at its center in radians. (Angles are measured counter-clockwise)
    Examples :
            arc = ArcBetweenPoints(start = (0, 0, 0), end = (1, 2, 0), angle = TAU/2)

            arc = ArcBetweenPoints(start = (-2, 3, 0), end = (1, 2, 0), angle = -TAU/12, color = BLUE)

    Returns
    -----
    out : ArcBetweenPoints object
        An ArcBetweenPoints object satisfying the specified parameters
    '''
    def __init__(self, start, end, angle=TAU / 4, **kwargs):
        Arc.__init__(
            self,
            angle=angle,
            **kwargs,
        )
        if angle == 0:
            self.set_points_as_corners([LEFT, RIGHT])
        self.put_start_and_end_on(np.array(start), np.array(end))


class CurvedArrow(ArcBetweenPoints):
    '''
    Creates a curved arrow passing through the specified points with "angle" as the
    angle subtended at its center.

    Parameters
    -----
    start_point : array_like
        Starting point of the curved arrow
    end_point : array_like
        Ending point of the curved arrow
    angle : float
        Angle subtended by the curved arrow at its center in radians. (Angles are measured counter-clockwise)
    Examples :
            curvedArrow = CurvedArrow(start_point = (0, 0, 0), end_point = (1, 2, 0), angle = TAU/2)

            curvedArrow = CurvedArrow(start_point = (-2, 3, 0), end_point = (1, 2, 0), angle = -TAU/12, color = BLUE)

    Returns
    -----
    out : CurvedArrow object
        A CurvedArrow object satisfying the specified parameters
    '''
    def __init__(self, start_point, end_point, **kwargs):
        ArcBetweenPoints.__init__(self, start_point, end_point, **kwargs)
        self.add_tip()


class CurvedDoubleArrow(CurvedArrow):
    '''
    Creates a curved double arrow passing through the specified points with "angle" as the
    angle subtended at its center.

    Parameters
    -----
    start_point : array_like
        Starting point of the curved double arrow
    end_point : array_like
        Ending point of the curved double arrow
    angle : float
        Angle subtended by the curved double arrow at its center in radians. (Angles are measured counter-clockwise)
    Examples :
            curvedDoubleArrow = CurvedDoubleArrow(start_point = (0, 0, 0), end_point = (1, 2, 0), angle = TAU/2)

            curvedDoubleArrow = CurvedDoubleArrow(start_point = (-2, 3, 0), end_point = (1, 2, 0), angle = -TAU/12, color = BLUE)

    Returns
    -----
    out : CurvedDoubleArrow object
        A CurvedDoubleArrow object satisfying the specified parameters
    '''
    def __init__(self, start_point, end_point, **kwargs):
        CurvedArrow.__init__(
            self, start_point, end_point, **kwargs
        )
        self.add_tip(at_start=True)


class Circle(Arc):
    '''
    Creates a circle.

    Parameters
    -----
    radius : float
        Radius of the circle
    arc_center : array_like
        Center of the circle
    Examples :
            circle = Circle(radius = 2, arc_center = (1,2,0))

            circle = Circle(radius = 3.14, arc_center = 2 * LEFT + UP, color = DARK_BLUE)

    Returns
    -----
    out : Circle object
        A Circle object satisfying the specified parameters
    '''
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
    '''
    Creates a dot. Dot is a filled white circle with no bounary and DEFAULT_DOT_RADIUS.

    Parameters
    -----
    point : array_like
        Coordinates of center of the dot.
    Examples :
            dot = Dot(point = (1, 2, 0))
    
    Returns
    -----
    out : Dot object
        A Dot object satisfying the specified parameters
    '''
    CONFIG = {
        "radius": DEFAULT_DOT_RADIUS,
        "stroke_width": 0,
        "fill_opacity": 1.0,
        "color": WHITE
    }

    def __init__(self, point=ORIGIN, **kwargs):
        Circle.__init__(self, arc_center=point, **kwargs)


class SmallDot(Dot):
    '''
    Creates a small dot. Small dot is a filled white circle with no bounary and DEFAULT_SMALL_DOT_RADIUS.

    Parameters
    -----
    point : array_like
        Coordinates of center of the small dot.
    Examples :
            smallDot = SmallDot(point = (1, 2, 0))
    
    Returns
    -----
    out : SmallDot object
        A SmallDot object satisfying the specified parameters
    '''
    CONFIG = {
        "radius": DEFAULT_SMALL_DOT_RADIUS,
    }


class Ellipse(Circle):
    '''
    Creates an ellipse.

    Parameters
    -----
    width : float
        Width of the ellipse
    height : float
        Height of the ellipse
    arc_center : array_like
        Coordinates of center of the ellipse
    Examples :
            ellipse = Ellipse(width = 4, height = 1, arc_center = (3, 3, 0))

            ellipse = Ellipse(width = 2, height = 5, arc_center = ORIGIN, color = BLUE)

    Returns
    -----
    out : Ellipse object
        An Ellipse object satisfying the specified parameters
    '''
    CONFIG = {
        "width": 2,
        "height": 1
    }

    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)
        self.set_width(self.width, stretch=True)
        self.set_height(self.height, stretch=True)


class AnnularSector(Arc):
    '''
    Creates an annular sector.

    Parameters
    -----
    inner_radius : float
        Inner radius of the annular sector
    outer_radius : float
        Outer radius of the annular sector
    start_angle : float
        Starting angle of the annular sector (Angles are measured counter-clockwise)
    angle : float
        Angle subtended at the center of the annular sector (Angles are measured counter-clockwise)
    arc_center : array_like
        Coordinates of center of the annular sector
    Examples :
            annularSector = AnnularSector(inner_radius = 1, outer_radius = 2, angle = TAU/2, start_angle = TAU*3/4, arc_center = (1,-2,0))

    Returns
    -----
    out : AnnularSector object
        An AnnularSector object satisfying the specified parameters
    '''
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
    '''
    Creates a sector.

    Parameters
    -----
    outer_radius : float
        Radius of the sector
    start_angle : float
        Starting angle of the sector in radians. (Angles are measured counter-clockwise)
    angle : float
        Angle subtended by the sector at its center in radians. (Angles are measured counter-clockwise)
    arc_center : array_like
        Coordinates of center of the sector
    Examples :
            sector = Sector(outer_radius = 1, start_angle = TAU/3, angle = TAU/2, arc_center = [0,3,0])

            sector = Sector(outer_radius = 3, start_angle = TAU/4, angle = TAU/4, arc_center = ORIGIN, color = PINK)

    Returns
    -----
    out : Sector object
        An Sector object satisfying the specified parameters
    '''
    CONFIG = {
        "outer_radius": 1,
        "inner_radius": 0
    }


class Annulus(Circle):
    '''
    Creates an annulus.

    Parameters
    -----
    inner_radius : float
        Inner radius of the annulus
    outer_radius : float
        Outer radius of the annulus
    arc_center : array_like
        Coordinates of center of the annulus
    Examples :
            annulus = Annulus(inner_radius = 2, outer_radius = 3, arc_center = (1, -1, 0))

            annulus = Annulus(inner_radius = 2, outer_radius = 3, stroke_width = 20, stroke_color = RED, fill_color = BLUE, arc_center = ORIGIN)

    Returns
    -----
    out : Annulus object
        An Annulus object satisfying the specified parameters
    '''
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


class Line(TipableVMobject):
    '''
    Creates a line joining the points "start" and "end".

    Parameters
    -----
    start : array_like
        Starting point of the line
    end : array_like
        Ending point of the line 
    Examples :
            line = Line((0, 0, 0), (3, 0, 0))

            line = Line((1, 2, 0), (-2, -3, 0), color = BLUE)

    Returns
    -----
    out : Line object
        A Line object satisfying the specified parameters
    '''
    CONFIG = {
        "buff": 0,
        "path_arc": None,  # angle of arc specified here
    }

    def __init__(self, start=LEFT, end=RIGHT, **kwargs):
        digest_config(self, kwargs)
        self.set_start_and_end_attrs(start, end)
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
        #
        if self.path_arc == 0:
            length = self.get_length()
        else:
            length = self.get_arc_length()
        #
        if length < 2 * self.buff:
            return
        buff_proportion = self.buff / length
        self.pointwise_become_partial(
            self, buff_proportion, 1 - buff_proportion
        )
        return self

    def set_start_and_end_attrs(self, start, end):
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

    def put_start_and_end_on(self, start, end):
        curr_start, curr_end = self.get_start_and_end()
        if np.all(curr_start == curr_end):
            # TODO, any problems with resetting
            # these attrs?
            self.start = start
            self.end = end
            self.generate_points()
        return super().put_start_and_end_on(start, end)

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

    def set_length(self, length):
        self.scale(length / self.get_length())

    def set_opacity(self, opacity, family=True):
        # Overwrite default, which would set
        # the fill opacity
        self.set_stroke(opacity=opacity)
        if family:
            for sm in self.submobjects:
                sm.set_opacity(opacity, family)
        return self


class DashedLine(Line):
    '''
    Creates a dashed line joining the points "start" and "end".

    Parameters
    -----
    start : array_like
        Starting point of the dashed line
    end : array_like
        Ending point of the dashed line 
    Examples :
            line = DashedLine((0, 0, 0), (3, 0, 0))

            line = DashedLine((1, 2, 3), (4, 5, 6), color = BLUE)

    Returns
    -----
    out : DashedLine object
        A DashedLine object satisfying the specified parameters
    '''
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

    def get_first_handle(self):
        return self.submobjects[0].points[1]

    def get_last_handle(self):
        return self.submobjects[-1].points[-2]


class TangentLine(Line):
    '''
    Creates a tangent line to the specified vectorized math object.

    Parameters
    -----
    vmob : VMobject object
        Vectorized math object which the line will be tangent to 
    alpha : float
        Point on the perimeter of the vectorized math object. It takes value between 0 and 1
        both inclusive.
    length : float
        Length of the tangent line
    Examples :
            circle = Circle(arc_center = ORIGIN, radius = 3, color = GREEN)
            tangentLine = TangentLine(vmob = circle, alpha = 1/3, length = 6, color = BLUE)

    Returns
    -----
    out : TangentLine object
        A TangentLine object satisfying the specified parameters
    '''
    CONFIG = {
        "length": 1,
        "d_alpha": 1e-6
    }

    def __init__(self, vmob, alpha, **kwargs):
        digest_config(self, kwargs)
        da = self.d_alpha
        a1 = np.clip(alpha - da, 0, 1)
        a2 = np.clip(alpha + da, 0, 1)
        super().__init__(
            vmob.point_from_proportion(a1),
            vmob.point_from_proportion(a2),
            **kwargs
        )
        self.scale(self.length / self.get_length())


class Elbow(VMobject):
    '''
    Creates an elbow. Elbow is an L-shaped shaped object.

    Parameters
    -----
    width : float
        Width of the elbow
    angle : float
        Angle of the elbow in radians with the horizontal. (Angles are measured counter-clockwise)
    Examples :
            line = Elbow(width = 2, angle = TAU/16)

    Returns
    -----
    out : Elbow object
        A Elbow object satisfying the specified parameters
    '''
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
    '''
    Creates an arrow.

    Parameters
    -----
    start : array_like
        Starting point of the arrow
    end : array_like
        Ending point of the arrow 
    Examples :
            arrow = Arrow((0, 0, 0), (3, 0, 0))

            arrow = Arrow((1, 2, 0), (-2, -3, 0), color = BLUE)

    Returns
    -----
    out : Arrow object
        A Arrow object satisfying the specified parameters
    '''
    CONFIG = {
        "stroke_width": 6,
        "buff": MED_SMALL_BUFF,
        "max_tip_length_to_length_ratio": 0.25,
        "max_stroke_width_to_length_ratio": 5,
        "preserve_tip_size_when_scaling": True,
    }

    def __init__(self, *args, **kwargs):
        Line.__init__(self, *args, **kwargs)
        # TODO, should this be affected when
        # Arrow.set_stroke is called?
        self.initial_stroke_width = self.stroke_width
        self.add_tip()
        self.set_stroke_width_from_length()

    def scale(self, factor, **kwargs):
        if self.get_length() == 0:
            return self

        has_tip = self.has_tip()
        has_start_tip = self.has_start_tip()
        if has_tip or has_start_tip:
            old_tips = self.pop_tips()

        VMobject.scale(self, factor, **kwargs)
        self.set_stroke_width_from_length()

        # So horribly confusing, must redo
        if has_tip:
            self.add_tip()
            old_tips[0].points[:, :] = self.tip.points
            self.remove(self.tip)
            self.tip = old_tips[0]
            self.add(self.tip)
        if has_start_tip:
            self.add_tip(at_start=True)
            old_tips[1].points[:, :] = self.start_tip.points
            self.remove(self.start_tip)
            self.start_tip = old_tips[1]
            self.add(self.start_tip)
        return self

    def get_normal_vector(self):
        p0, p1, p2 = self.tip.get_start_anchors()[:3]
        return normalize(np.cross(p2 - p1, p1 - p0))

    def reset_normal_vector(self):
        self.normal_vector = self.get_normal_vector()
        return self

    def get_default_tip_length(self):
        max_ratio = self.max_tip_length_to_length_ratio
        return min(
            self.tip_length,
            max_ratio * self.get_length(),
        )

    def set_stroke_width_from_length(self):
        max_ratio = self.max_stroke_width_to_length_ratio
        self.set_stroke(
            width=min(
                self.initial_stroke_width,
                max_ratio * self.get_length(),
            ),
            family=False,
        )
        return self

    # TODO, should this be the default for everything?
    def copy(self):
        return self.deepcopy()


class Vector(Arrow):
    '''
    Creates a vector. Vector is an arrow with start point as ORIGIN

    Parameters
    -----
    direction : array_like
        Coordinates of direction of the arrow
    Examples :
            arrow = Vector(direction = LEFT)

            arrow = Vector(direction = (4,3,0), color = BLUE)

    Returns
    -----
    out : Vector object
        A Vector object satisfying the specified parameters
    '''
    CONFIG = {
        "buff": 0,
    }

    def __init__(self, direction=RIGHT, **kwargs):
        if len(direction) == 2:
            direction = np.append(np.array(direction), 0)
        Arrow.__init__(self, ORIGIN, direction, **kwargs)


class DoubleArrow(Arrow):
    '''
    Creates a double arrow.

    Parameters
    -----
    start : array_like
        Starting point of the double arrow
    end : array_like
        Ending point of the double arrow 
    Examples :
            doubleArrow = DoubleArrow((0, 0, 0), (3, 0, 0))

            doubleArrow = DoubleArrow((1, 2, 0), (-2, -3, 0), color = BLUE)

    Returns
    -----
    out : DoubleArrow object
        A DoubleArrow object satisfying the specified parameters
    '''
    def __init__(self, *args, **kwargs):
        Arrow.__init__(self, *args, **kwargs)
        self.add_tip(at_start=True)


class CubicBezier(VMobject):
    def __init__(self, points, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points(points)


class Polygon(VMobject):
    '''
    Creates a polygon by joining the specified vertices.

    Parameters
    -----
    *vertices : array_like
        Vertex of the polygon
    Examples :
            triangle = Polygon((-3,0,0), (3,0,0), (0,3,0))

    Returns
    -----
    out : Polygon object
        A Polygon object satisfying the specified parameters
    '''
    CONFIG = {
        "color": BLUE,
    }

    def __init__(self, *vertices, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points_as_corners(
            [*vertices, vertices[0]]
        )

    def get_vertices(self):
        return self.get_start_anchors()

    def round_corners(self, radius=0.5):
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
                angle=sign * angle
            )
            arcs.append(arc)

        self.clear_points()
        # To ensure that we loop through starting with last
        arcs = [arcs[-1], *arcs[:-1]]
        for arc1, arc2 in adjacent_pairs(arcs):
            self.append_points(arc1.points)
            line = Line(arc1.get_end(), arc2.get_start())
            # Make sure anchors are evenly distributed
            len_ratio = line.get_length() / arc1.get_arc_length()
            line.insert_n_curves(
                int(arc1.get_num_curves() * len_ratio)
            )
            self.append_points(line.get_points())
        return self


class RegularPolygon(Polygon):
    '''
    Creates a regular polygon of edge length 1 at the center of the screen.

    Parameters
    -----
    n : int
        Number of vertices of the regular polygon
    start_angle : float
        Starting angle of the regular polygon in radians. (Angles are measured counter-clockwise)
    Examples :
            pentagon = RegularPolygon(n = 5, start_angle = 30 * DEGREES)

    Returns
    -----
    out : RegularPolygon object
        A RegularPolygon object satisfying the specified parameters
    '''
    CONFIG = {
        "start_angle": None,
    }

    def __init__(self, n=6, **kwargs):
        digest_config(self, kwargs, locals())
        if self.start_angle is None:
            if n % 2 == 0:
                self.start_angle = 0
            else:
                self.start_angle = 90 * DEGREES
        start_vect = rotate_vector(RIGHT, self.start_angle)
        vertices = compass_directions(n, start_vect)
        Polygon.__init__(self, *vertices, **kwargs)


class Triangle(RegularPolygon):
    '''
    Creates a triangle of edge length 1 at the center of the screen.

    Parameters
    -----
    start_angle : float
        Starting angle of the triangle in radians. (Angles are measured counter-clockwise)
    Examples :
            triangle = Triangle(start_angle = 45 * DEGREES)

    Returns
    -----
    out : Triangle object
        A Triangle object satisfying the specified parameters
    '''
    def __init__(self, **kwargs):
        RegularPolygon.__init__(self, n=3, **kwargs)


class ArrowTip(Triangle):
    '''
    Creates an arrow tip.

    Returns
    -----
    out : ArrowTip object
        A ArrowTip object satisfying the specified parameters
    '''
    CONFIG = {
        "fill_opacity": 1,
        "stroke_width": 0,
        "length": DEFAULT_ARROW_TIP_LENGTH,
        "start_angle": PI,
    }

    def __init__(self, **kwargs):
        Triangle.__init__(self, **kwargs)
        self.set_width(self.length)
        self.set_height(self.length, stretch=True)

    def get_base(self):
        return self.point_from_proportion(0.5)

    def get_tip_point(self):
        return self.points[0]

    def get_vector(self):
        return self.get_tip_point() - self.get_base()

    def get_angle(self):
        return angle_of_vector(self.get_vector())

    def get_length(self):
        return get_norm(self.get_vector())


class Rectangle(Polygon):
    '''
    Creates a rectangle at the center of the screen.

    Parameters
    -----
    width : float
        Width of the rectangle
    height : float
        Height of the rectangle
    Examples :
            rectangle = Rectangle(width = 3, height = 4, color = BLUE)

    Returns
    -----
    out : Rectangle object
        A Rectangle object satisfying the specified parameters
    '''
    CONFIG = {
        "color": WHITE,
        "height": 2.0,
        "width": 4.0,
        "mark_paths_closed": True,
        "close_new_points": True,
    }

    def __init__(self, **kwargs):
        Polygon.__init__(self, UL, UR, DR, DL, **kwargs)
        self.set_width(self.width, stretch=True)
        self.set_height(self.height, stretch=True)


class Square(Rectangle):
    '''
    Creates a square at the center of the screen.

    Parameters
    -----
    side_length : float
        Edge length of the square
    Examples :
            square = Square(side_length = 5, color = PINK)

    Returns
    -----
    out : Square object
        A Square object satisfying the specified parameters
    '''
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
    '''
    Creates a rectangle with round edges at the center of the screen.

    Parameters
    -----
    width : float
        Width of the rounded rectangle
    height : float
        Height of the rounded rectangle
    corner_radius : float
        Corner radius of the rectangle
    Examples :
            rRectangle = RoundedRectangle(width = 3, height = 4, corner_radius = 1, color = BLUE)

    Returns
    -----
    out : RoundedRectangle object
        A RoundedRectangle object satisfying the specified parameters
    '''
    CONFIG = {
        "corner_radius": 0.5,
    }

    def __init__(self, **kwargs):
        Rectangle.__init__(self, **kwargs)
        self.round_corners(self.corner_radius)
