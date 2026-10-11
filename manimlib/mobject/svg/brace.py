from __future__ import annotations

import math
import copy

import numpy as np

from manimlib.constants import DEFAULT_MOBJECT_TO_MOBJECT_BUFF, SMALL_BUFF
from manimlib.constants import DOWN, LEFT, ORIGIN, RIGHT, DL, DR, UL, UP
from manimlib.constants import PI
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeIn
from manimlib.animation.growing import GrowFromCenter
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.tex_mobject import TexText
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.iterables import listify
from manimlib.utils.space_ops import get_norm

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable

    from manimlib.animation.animation import Animation
    from manimlib.mobject.mobject import Mobject
    from manimlib.typing import Vect3


class Brace(Tex):
    """
    A LaTeX-rendered brace used to annotate a mobject and optionally position
    text or mathematical expressions at the brace's tip.

    Brace inherits from Tex and uses a LaTeX underbrace representation by default.
    It adjusts the brace's width to match the width of a target mobject, positions
    the brace relative to that mobject, and rotates both objects as needed to
    support different brace orientations.

    The class is useful for grouping parts of a mathematical expression, labeling
    a region of a diagram, or indicating which portion of a visual construction
    corresponds to a particular quantity or concept.

    Parameters
    ----------
    mobject : Mobject
        The target mobject whose width determines the initial width of the brace.
        Its lower-left and lower-right corners are used to calculate the target
        width after temporarily rotating it into the brace's reference orientation.

    direction : Vect3, optional
        The direction in which the brace is oriented relative to the target
        mobject. Defaults to DOWN. The direction's first two components determine
        the rotation angle used during positioning.

    buff : float, optional
        The vertical offset applied while positioning the brace relative to the
        target mobject in the brace's temporary reference orientation. Defaults
        to 0.2.

    tex_string : str, optional
        The LaTeX string used to render the brace. Defaults to
        R"\underbrace{\qquad}". The implementation assumes a particular point
        arrangement in this LaTeX representation when identifying the brace's tip
        and adjusting its width.

    **kwargs
        Additional keyword arguments forwarded to Tex during initialization.

    Attributes
    ----------
    tip_point_index : int
        Index of the point in the brace's complete point array that represents
        its tip. It is determined by locating the point with the minimum y
        coordinate in the initially rendered brace geometry. This index is
        subsequently used by get_tip() to retrieve the tip's position.

    Width Adjustment
    ----------------
    The constructor calculates the horizontal distance between the target
    mobject's lower-left and lower-right corners after rotating the target into
    a reference orientation. It then calls set_initial_width() to resize the
    brace to that width before positioning and rotating both objects back.

    set_initial_width() handles widening differently from narrowing. When the
    requested width exceeds the brace's current width, it expands the two
    outer rectangular portions while moving the corresponding tips outward.
    When the requested width is smaller, it stretches the entire brace to the
    requested width.

    Brace Orientation and Placement
    -------------------------------
    The constructor computes a rotation angle from the supplied direction's
    first two components. It temporarily rotates the target mobject, determines
    the target width, positions the brace relative to the target, and finally
    rotates both objects back to their intended orientation.

    This approach allows the brace to be placed along different orientations
    without implementing a separate brace geometry for every direction.

    Methods
    -------
    set_initial_width(width)
        Adjusts the brace to the specified width and returns the brace itself.

    put_at_tip(mob, use_next_to=True, **kwargs)
        Positions another mobject relative to the brace's tip. When use_next_to
        is True, it uses Mobject.next_to() with the rounded brace direction.
        Otherwise, it moves the supplied mobject to the tip and shifts it along
        the brace direction by half its width plus a buffer.

    get_text(text, **kwargs)
        Creates a Text mobject and positions it relative to the brace's tip.
        The optional buff argument controls the spacing and defaults to
        SMALL_BUFF. Other keyword arguments are passed to Text.

    get_tex(*tex, **kwargs)
        Creates a Tex mobject and positions it relative to the brace's tip.
        The optional buff argument controls the spacing and defaults to
        SMALL_BUFF. Other keyword arguments are passed to Tex.

    get_tip()
        Returns the point at tip_point_index from the brace's complete point
        array. The implementation relies on the geometry of the chosen LaTeX
        brace representation.

    get_direction()
        Computes a normalized vector from the brace's center to its tip.
        This vector is used to determine the direction in which labels should
        be positioned relative to the brace.

    Examples
    --------
    Create a brace beneath a mathematical expression:

        expression = Tex("a", "+", "b", "+", "c")
        brace = Brace(expression, direction=DOWN)
        label = brace.get_tex("x")
        self.add(expression, brace, label)

    Create a brace with a custom buffer:

        brace = Brace(expression, direction=DOWN, buff=0.3)
        label = brace.get_text("sum", buff=0.15)
        self.add(expression, brace, label)

    Position an existing mobject at the brace's tip:

        brace.put_at_tip(label)

    Notes
    -----
    - The default LaTeX representation is an underbrace. Other tex_string values
      may not have the same point arrangement or a reliably identifiable tip.
    - tip_point_index is computed from the minimum y coordinate of the initially
      rendered geometry. Its correctness depends on the chosen LaTeX representation.
    - The width adjustment logic assumes a particular internal organization of
      the rendered brace, including specific submobject indices.
    - set_initial_width() stretches existing geometry rather than regenerating
      the LaTeX expression at a new size.
    - get_direction() returns a unit vector from the brace's center toward its
      tip; it is not simply the original direction argument.
    - When use_next_to is False, put_at_tip() calculates its offset using half
      the supplied mobject's width, even when the brace direction is not
      horizontal. This behavior follows the implementation and may affect
      placement for differently oriented braces.
    - The constructor rotates the supplied target mobject during positioning and
      then rotates it back. It therefore modifies the target's geometry as part
      of the placement procedure.

    See Also
    --------
    Tex
        The LaTeX-rendered mobject class from which Brace inherits.
    Text
        The text mobject used by get_text().
    Mobject.next_to
        The relative-positioning method used by put_at_tip().
    """

    def __init__(
        self,
        mobject: Mobject,
        direction: Vect3 = DOWN,
        buff: float = 0.2,
        tex_string: str = R"\underbrace{\qquad}",
        **kwargs
    ):
        super().__init__(tex_string, **kwargs)

        angle = -math.atan2(*direction[:2]) + PI
        mobject.rotate(-angle, about_point=ORIGIN)
        left = mobject.get_corner(DL)
        right = mobject.get_corner(DR)
        target_width = right[0] - left[0]

        self.tip_point_index = np.argmin(self.get_all_points()[:, 1])
        self.set_initial_width(target_width)
        self.shift(left - self.get_corner(UL) + buff * DOWN)
        for mob in mobject, self:
            mob.rotate(angle, about_point=ORIGIN)

    def set_initial_width(self, width: float):
        width_diff = width - self.get_width()
        if width_diff > 0:
            for tip, rect, vect in [(self[0], self[1], RIGHT), (self[5], self[4], LEFT)]:
                rect.set_width(
                    width_diff / 2 + rect.get_width(),
                    about_edge=vect, stretch=True
                )
                tip.shift(-width_diff / 2 * vect)
        else:
            self.set_width(width, stretch=True)
        return self

    def put_at_tip(
        self,
        mob: Mobject,
        use_next_to: bool = True,
        **kwargs
    ):
        if use_next_to:
            mob.next_to(
                self.get_tip(),
                np.round(self.get_direction()),
                **kwargs
            )
        else:
            mob.move_to(self.get_tip())
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_MOBJECT_BUFF)
            shift_distance = mob.get_width() / 2.0 + buff
            mob.shift(self.get_direction() * shift_distance)
        return self

    def get_text(self, text: str, **kwargs) -> Text:
        buff = kwargs.pop("buff", SMALL_BUFF)
        text_mob = Text(text, **kwargs)
        self.put_at_tip(text_mob, buff=buff)
        return text_mob

    def get_tex(self, *tex: str, **kwargs) -> Tex:
        buff = kwargs.pop("buff", SMALL_BUFF)
        tex_mob = Tex(*tex, **kwargs)
        self.put_at_tip(tex_mob, buff=buff)
        return tex_mob

    def get_tip(self) -> np.ndarray:
        # Very specific to the LaTeX representation
        # of a brace, but it's the only way I can think
        # of to get the tip regardless of orientation.
        return self.get_all_points()[self.tip_point_index]

    def get_direction(self) -> np.ndarray:
        vect = self.get_tip() - self.get_center()
        return vect / get_norm(vect)


class BraceLabel(VMobject):
    """
    A mobject that combines a Brace with a text or mathematical label.

    BraceLabel provides a convenient way to annotate a visual object or a group
    of objects with a brace and a corresponding label. It combines the brace
    geometry and the label into a single VMobject, allowing both components to
    be positioned, displayed, and animated together.

    The brace is created around the supplied target object, using the requested
    brace direction. The label is constructed using the class-level
    label_constructor, scaled according to label_scale, and positioned relative
    to the brace's tip using label_buff.

    By default, label_constructor is Tex, so labels are rendered as LaTeX
    expressions. Subclasses can override label_constructor to use a different
    label representation, provided that the resulting object supports the
    operations expected by this class.

    Parameters
    ----------
    obj : VMobject | list[VMobject]
        The object or collection of objects to annotate. If a list is supplied,
        its elements are grouped into a VGroup before the brace is constructed.
        The brace uses this object to determine its dimensions and placement.

    text : str | Iterable[str]
        The text or mathematical expression used for the label. The value is
        passed through listify() and expanded into positional arguments for
        label_constructor. This allows a single string or an iterable of strings
        to be supplied, depending on the behavior of listify().

    brace_direction : np.ndarray, optional
        The direction in which the brace is oriented relative to the target
        object. Defaults to DOWN.

    label_scale : float, optional
        The scale factor applied to the newly constructed label. Defaults to 1.0,
        which leaves the label at its constructor-provided size.

    label_buff : float, optional
        The spacing passed to Brace.put_at_tip() when positioning the initial
        label. Defaults to DEFAULT_MOBJECT_TO_MOBJECT_BUFF.

    **kwargs
        Additional keyword arguments forwarded to VMobject initialization,
        Brace construction, and label construction. These objects may interpret
        the same keyword arguments differently.

    Attributes
    ----------
    label_constructor : type
        Class-level constructor used to create the label. Defaults to Tex.

    brace_direction : np.ndarray
        Direction used when constructing or replacing the brace.

    label_scale : float
        Scale factor applied when the initial label is created and when a label
        is replaced through change_label().

    label_buff : float
        Buffer used to position the initial label relative to the brace's tip.
        The initial constructor passes this value explicitly to put_at_tip();
        later label replacements use put_at_tip() with its default buffer unless
        another method or implementation changes that behavior.

    brace : Brace
        The brace associated with the annotated object.

    label : VMobject
        The label object associated with the brace. Its concrete type depends
        on label_constructor.

    Structure
    ---------
    BraceLabel stores the brace and label as its two submobjects, in that order.
    The brace is available as self.brace and the label as self.label.

    This organization allows the combined object to be manipulated as a single
    mobject while still providing methods to animate, replace, or reposition
    the individual components.

    Methods
    -------
    creation_anim(label_anim=FadeIn, brace_anim=GrowFromCenter)
        Returns an AnimationGroup that animates the brace and label separately.
        The brace uses brace_anim, while the label uses label_anim. The method
        returns the animation group rather than playing it automatically.

    shift_brace(obj, **kwargs)
        Constructs a new brace for the supplied object, positions it relative
        to the existing label, replaces the stored brace, and returns self.
        If obj is a list, the method attempts to create a VMobject from its
        elements before constructing the brace. Unlike __init__(), it does not
        explicitly reuse the stored label_buff when positioning the label.

    change_label(*text, **kwargs)
        Constructs a replacement label using label_constructor, scales it when
        label_scale differs from 1, positions it at the current brace's tip,
        replaces the stored label, and returns self. The replacement label is
        positioned using put_at_tip()'s default buffer because no explicit buff
        is passed here.

    change_brace_label(obj, *text)
        Replaces the brace using shift_brace() and then replaces the label using
        change_label(). Returns the result of change_label(), which is self.
        This provides a convenient way to update both the annotated object and
        its label in sequence.

    copy()
        Creates a shallow copy of the BraceLabel instance, then independently
        copies its brace and label and assigns those copies as the new
        submobjects. The copied object is returned.

    Examples
    --------
    Create a brace and a LaTeX label beneath an expression:

        expression = Tex("a", "+", "b", "+", "c")
        annotation = BraceLabel(expression, "x")
        self.add(expression, annotation)

    Annotate a group of objects:

        parts = [Tex("a"), Tex("b"), Tex("c")]
        annotation = BraceLabel(parts, "three terms")
        self.add(*parts, annotation)

    Animate the brace and label separately:

        annotation = BraceLabel(expression, "x")
        self.play(annotation.creation_anim())

    Change the label:

        annotation.change_label("y")

    Change both the annotated object and the label:

        annotation.change_brace_label(new_expression, "z")

    Notes
    -----
    - The default label constructor is Tex. A subclass can customize the
      representation by overriding label_constructor.
    - The initial constructor uses listify(text), while change_label() accepts
      positional strings directly. Their accepted input forms may therefore
      differ.
    - label_scale is applied when labels are initially constructed and when
      change_label() creates a replacement. It is not automatically applied by
      shift_brace(), which preserves the existing label.
    - label_buff is explicitly used during initial construction. The replacement
      and repositioning methods call put_at_tip() without passing label_buff,
      so they use that method's default buffer.
    - shift_brace() handles list inputs differently from __init__(): it attempts
      VMobject(*obj) instead of grouping the elements in a VGroup. Whether this
      is appropriate depends on the VMobject constructor and the supplied list.
    - **kwargs is forwarded to multiple constructors in __init__(). A keyword
      accepted by one constructor may not necessarily be accepted by another.
    - copy() explicitly duplicates the brace and label so that these components
      are not shared with the original object. Other attributes are initially
      carried over through copy.copy().

    See Also
    --------
    Brace
        Constructs the brace and provides label-positioning helpers.
    Tex
        The default constructor used for mathematical labels.
    VMobject
        The base class for this combined annotation object.
    AnimationGroup
        Groups the brace and label animations into one animation.
    """

    label_constructor: type = Tex

    def __init__(
        self,
        obj: VMobject | list[VMobject],
        text: str | Iterable[str],
        brace_direction: np.ndarray = DOWN,
        label_scale: float = 1.0,
        label_buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFF,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.brace_direction = brace_direction
        self.label_scale = label_scale
        self.label_buff = label_buff

        if isinstance(obj, list):
            obj = VGroup(*obj)
        self.brace = Brace(obj, brace_direction, **kwargs)

        self.label = self.label_constructor(*listify(text), **kwargs)
        self.label.scale(self.label_scale)

        self.brace.put_at_tip(self.label, buff=self.label_buff)
        self.set_submobjects([self.brace, self.label])

    def creation_anim(
        self,
        label_anim: Animation = FadeIn,
        brace_anim: Animation = GrowFromCenter
    ) -> AnimationGroup:
        return AnimationGroup(brace_anim(self.brace), label_anim(self.label))

    def shift_brace(self, obj: VMobject | list[VMobject], **kwargs):
        if isinstance(obj, list):
            obj = VMobject(*obj)
        self.brace = Brace(obj, self.brace_direction, **kwargs)
        self.brace.put_at_tip(self.label)
        self.submobjects[0] = self.brace
        return self

    def change_label(self, *text: str, **kwargs):
        self.label = self.label_constructor(*text, **kwargs)
        if self.label_scale != 1:
            self.label.scale(self.label_scale)

        self.brace.put_at_tip(self.label)
        self.submobjects[1] = self.label
        return self

    def change_brace_label(self, obj: VMobject | list[VMobject], *text: str):
        self.shift_brace(obj)
        self.change_label(*text)
        return self

    def copy(self):
        copy_mobject = copy.copy(self)
        copy_mobject.brace = self.brace.copy()
        copy_mobject.label = self.label.copy()
        copy_mobject.set_submobjects([copy_mobject.brace, copy_mobject.label])

        return copy_mobject


class BraceText(BraceLabel):
    """
    A BraceLabel specialization that uses TexText to create text labels.

    BraceText combines a brace around a target mobject with a text label positioned
    at the brace's tip. It inherits the brace construction, label positioning,
    animation, and replacement functionality from BraceLabel, while setting
    label_constructor to TexText instead of the default Tex.

    This class is useful for annotating diagrams, geometric constructions, and
    mathematical expressions with ordinary text rather than labels intended
    primarily for mathematical LaTeX notation.

    The target object and brace direction determine where the brace is placed.
    The supplied text is passed to TexText through the inherited BraceLabel
    implementation, and the resulting label is scaled and positioned according
    to the inherited label_scale and label_buff settings.

    Class Attributes
    ----------------
    label_constructor : type
        Set to TexText, which is used to construct labels. This overrides the
        Tex constructor inherited from BraceLabel.

    Parameters
    ----------
    obj : VMobject | list[VMobject]
        The object or list of objects to annotate. Lists are handled by the
        inherited BraceLabel constructor.

    text : str | Iterable[str]
        The text content used to create the label through TexText.

    brace_direction : np.ndarray, optional
        Direction in which the brace is oriented relative to the target object.
        Defaults to DOWN, as defined by BraceLabel.

    label_scale : float, optional
        Scale factor applied to the label. Defaults to 1.0.

    label_buff : float, optional
        Spacing between the brace's tip and the initial label. Defaults to
        DEFAULT_MOBJECT_TO_MOBJECT_BUFF.

    **kwargs
        Additional keyword arguments forwarded according to the inherited
        BraceLabel implementation. They are passed to the base VMobject
        initialization, Brace construction, and label construction, so they
        must be compatible with the relevant constructors.

    Inherited Functionality
    -----------------------
    BraceText inherits the following methods from BraceLabel:

    creation_anim(label_anim=FadeIn, brace_anim=GrowFromCenter)
        Returns an AnimationGroup for animating the brace and label.

    shift_brace(obj, **kwargs)
        Replaces the brace to annotate a different target object and repositions
        the existing label at the new brace's tip.

    change_label(*text, **kwargs)
        Replaces the current label using TexText as the label constructor.

    change_brace_label(obj, *text)
        Updates both the target brace and its label.

    copy()
        Creates a copy of the combined object, including copies of its brace
        and label.

    Example
    -------
        expression = Tex("a", "+", "b")
        annotation = BraceText(expression, "Two terms")
        self.add(expression, annotation)

    The example creates a brace around the expression and places the text
    "Two terms" at the brace's tip.

    Notes
    -----
    - BraceText changes the label constructor; it does not introduce a separate
      brace geometry or video-independent animation system.
    - Label construction and placement behavior are inherited from BraceLabel.
    - The inherited change_label() method also uses TexText because it refers
      to self.label_constructor.
    - The inherited label_buff value is explicitly used during initial label
      placement. Replacement labels use the default buffer of put_at_tip()
      unless the implementation is changed.
    - The exact text syntax and rendering behavior depend on TexText.

    See Also
    --------
    BraceLabel
        Base class that combines a brace and a label.
    Brace
        Creates and positions the brace.
    TexText
        Text-rendering class used to construct labels.
    """

    label_constructor: type = TexText


class LineBrace(Brace):
    """
    A Brace specialization designed to place a brace relative to a Line while
    accounting for the line's orientation.

    LineBrace inherits from Brace and adapts its construction process for line
    mobjects that may be rotated relative to the coordinate axes. It temporarily
    rotates the supplied line to align it with the horizontal reference
    orientation, constructs the brace using the inherited Brace implementation,
    and then restores the line's original rotation. Finally, it rotates the
    brace around the line's center so that the brace follows the line's
    orientation.

    This approach allows the brace to be positioned relative to an inclined
    line without requiring the caller to manually rotate the line into a
    horizontal orientation before constructing the brace.

    Parameters
    ----------
    line : Line
        The line mobject to annotate. Its angle is obtained using get_angle().
        The line is temporarily rotated during brace construction and then
        rotated back before the resulting brace is adjusted to match its
        orientation.

    direction : optional
        Direction passed to Brace after the line has been temporarily rotated.
        Defaults to UP. The direction is interpreted by the inherited Brace
        implementation during its construction.

    **kwargs
        Additional keyword arguments forwarded to Brace, such as its buffer
        or LaTeX representation options.

    Construction Process
    --------------------
    1. Obtain the line's current angle using line.get_angle().
    2. Rotate the line by the negative of that angle, temporarily aligning it
       with the horizontal reference orientation.
    3. Construct the brace by calling Brace.__init__ through super(), passing
       the temporarily rotated line, the requested direction, and any additional
       keyword arguments.
    4. Rotate the line back by its original angle.
    5. Rotate the newly constructed brace around the line's center by the
       original angle.

    The final rotation makes the brace follow the orientation of the line,
    while the inherited Brace implementation handles its width and relative
    placement.

    Example
    -------
        line = Line(LEFT, RIGHT).rotate(PI / 4)
        brace = LineBrace(line, direction=UP)
        self.add(line, brace)

    In this example, the brace is constructed relative to a line rotated by
    45 degrees. LineBrace handles the temporary alignment and final rotation
    internally.

    Notes
    -----
    - LineBrace relies on the geometry and positioning behavior implemented by
      Brace.
    - The line is modified in place during construction, although the method
      rotates it back to its original angle before completing.
    - The final brace rotation uses line.get_center() as its rotation center.
    - The implementation assumes that temporarily rotating the line is an
      appropriate way to establish the reference orientation for brace
      construction.
    - The default direction is UP, unlike Brace's default direction of DOWN.
    - The resulting placement depends on the line's geometry, the supplied
      direction, and any additional arguments passed to Brace.

    See Also
    --------
    Brace
        Base class that renders and positions a LaTeX brace.
    Line
        Line mobject accepted as the target of the brace.
    """

    def __init__(self, line: Line, direction=UP, **kwargs):
        angle = line.get_angle()
        line.rotate(-angle)
        super().__init__(line, direction, **kwargs)
        line.rotate(angle)
        self.rotate(angle, about_point=line.get_center())
