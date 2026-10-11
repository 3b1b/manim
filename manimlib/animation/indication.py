from __future__ import annotations

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.composition import Succession
from manimlib.animation.creation import ShowCreation
from manimlib.animation.creation import ShowPartial
from manimlib.animation.fading import FadeOut
from manimlib.animation.fading import FadeIn
from manimlib.animation.movement import Homotopy
from manimlib.animation.transform import Transform
from manimlib.constants import FRAME_X_RADIUS, FRAME_Y_RADIUS
from manimlib.constants import ORIGIN, RIGHT, UP
from manimlib.constants import SMALL_BUFF
from manimlib.constants import DEG
from manimlib.constants import TAU
from manimlib.constants import GREY, YELLOW
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Dot
from manimlib.mobject.geometry import Line
from manimlib.mobject.shape_matchers import SurroundingRectangle
from manimlib.mobject.shape_matchers import Underline
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.bezier import interpolate
from manimlib.utils.rate_functions import smooth
from manimlib.utils.rate_functions import squish_rate_func
from manimlib.utils.rate_functions import there_and_back
from manimlib.utils.rate_functions import wiggle

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import ManimColor
    from manimlib.mobject.mobject import Mobject


class FocusOn(Transform):
    """
    Create a focus effect that visually draws attention to a specific point.

    FocusOn is a subclass of Transform that animates a large, transparent Dot
    into a small Dot with a configurable fill opacity. The starting Dot covers
    a large area, while the target Dot has a radius of zero and follows the
    specified focus point through an updater.

    The animation creates a visual focus effect by transforming the large,
    transparent starting Dot into the small target Dot. The target Dot's fill
    color and opacity control the appearance of the focus point.

    Parameters
    ----------
    focus_point : np.ndarray | Mobject
        The location to focus on. This can be a coordinate array or a Mobject.
        The target Dot receives an updater that calls ``move_to(focus_point)``,
        allowing it to follow the specified point or object's position.

    opacity : float, optional
        The fill opacity assigned to the target Dot. Defaults to 0.2.

    color : ManimColor, optional
        The fill color used for both the starting and target Dots.
        Defaults to GREY.

    run_time : float, optional
        The duration of the animation. Defaults to 2 seconds.

    remover : bool, optional
        Whether the animated mobject should be removed during animation
        cleanup. Defaults to True.

    **kwargs
        Additional keyword arguments forwarded to Transform, apart from
        ``run_time`` and ``remover``, which are passed explicitly.

    Methods
    -------
    create_target() -> Dot
        Create a zero-radius Dot with the configured fill color and opacity.
        Attach an updater that moves the Dot to ``self.focus_point``.

    create_starting_mobject() -> Dot
        Create a large Dot whose radius is the sum of FRAME_X_RADIUS and
        FRAME_Y_RADIUS. Its stroke width is zero, and its fill uses the
        configured color with zero opacity.

    Notes
    -----
    - The constructor initializes Transform with an empty VMobject. The
      overridden ``create_target()`` and ``create_starting_mobject()``
      methods provide the actual target and starting mobjects.
    - The starting Dot has a radius of
      ``FRAME_X_RADIUS + FRAME_Y_RADIUS``. Its fill is initially transparent.
    - The target Dot has radius zero, so the target itself does not represent
      a large visible disk.
    - The target Dot's updater continuously calls ``move_to(self.focus_point)``.
      If ``focus_point`` is a Mobject, this allows the target to follow that
      object's position as its center changes.
    - The animation's exact visual appearance depends on Transform's
      interpolation behavior and the configured color and opacity.
    - The ``remover`` argument controls the inherited animation's cleanup
      behavior.
    - The implementation does not explicitly remove the updater in this
      class; updater cleanup depends on the surrounding animation lifecycle.

    Examples
    --------
    Example 1: Focus on the origin.

    >>> scene.play(FocusOn(ORIGIN))

    A focus effect is animated toward the origin using the default grey
    color, opacity 0.2, and two-second duration.

    Example 2: Focus on a specific coordinate.

    >>> point = np.array([2.0, 1.0, 0.0])
    >>> scene.play(
    ...     FocusOn(
    ...         point,
    ...         color=YELLOW,
    ...         opacity=0.4,
    ...     )
    ... )

    The focus target is placed at the specified coordinate, with yellow
    fill and opacity 0.4.

    Example 3: Focus on a Mobject.

    >>> circle = Circle().shift(RIGHT * 2)
    >>> scene.add(circle)
    >>> scene.play(FocusOn(circle, color=BLUE))

    The target Dot's updater moves it to the circle's current position.
    If the circle moves while the updater is active, the target follows it.

    Example 4: Change the animation duration.

    >>> square = Square()
    >>> scene.add(square)
    >>> scene.play(
    ...     FocusOn(
    ...         square,
    ...         run_time=3,
    ...         remover=False,
    ...     )
    ... )

    The focus animation runs for three seconds and is configured not to
    remove the animated mobject during cleanup.

    See Also
    --------
    Transform
    Dot
    Mobject.move_to
    Mobject.add_updater
    """

    def __init__(
        self,
        focus_point: np.ndarray | Mobject,
        opacity: float = 0.2,
        color: ManimColor = GREY,
        run_time: float = 2,
        remover: bool = True,
        **kwargs
    ):
        self.focus_point = focus_point
        self.opacity = opacity
        self.color = color
        # Initialize with blank mobject, while create_target
        # and create_starting_mobject handle the meat
        super().__init__(VMobject(), run_time=run_time, remover=remover, **kwargs)

    def create_target(self) -> Dot:
        little_dot = Dot(radius=0)
        little_dot.set_fill(self.color, opacity=self.opacity)
        little_dot.add_updater(lambda d: d.move_to(self.focus_point))
        return little_dot

    def create_starting_mobject(self) -> Dot:
        return Dot(
            radius=FRAME_X_RADIUS + FRAME_Y_RADIUS,
            stroke_width=0,
            fill_color=self.color,
            fill_opacity=0,
        )


class Indicate(Transform):
    """
    Temporarily emphasize a mobject by enlarging it and changing its color.

    Indicate is a subclass of Transform that creates a modified copy of the
    input mobject as its transformation target. The target is scaled by a
    specified factor and assigned a highlight color.

    By default, the animation uses ``there_and_back`` as its rate function.
    This makes the transformation progress toward the enlarged, highlighted
    target and then return toward the starting state, producing a temporary
    visual emphasis effect.

    Parameters
    ----------
    mobject : Mobject
        The object to emphasize. The animation transforms it toward a
        modified copy and, with the default rate function, back toward its
        original appearance.

    scale_factor : float, optional
        The factor by which the target copy is scaled. A value greater than
        1 enlarges the target, while a value between 0 and 1 makes it smaller.
        Defaults to 1.2.

    color : ManimColor, optional
        The color assigned to the target copy. Defaults to YELLOW.

    rate_func : Callable[[float], float], optional
        The rate function controlling the animation's interpolation progress.
        Defaults to ``there_and_back``, which typically progresses from the
        starting state toward the target and then returns.

    **kwargs
        Additional keyword arguments forwarded to Transform, such as
        ``run_time`` and other supported transformation settings.

    Methods
    -------
    create_target() -> Mobject
        Create a copy of the original mobject, scale it by ``self.scale_factor``,
        set its color to ``self.color``, and return it as the transformation
        target.

    Notes
    -----
    - The original mobject is copied before scaling and recoloring, so these
      target modifications are applied to the copy.
    - ``scale_factor`` controls the target's size relative to the original.
    - ``color`` is applied to the target using ``set_color()``.
    - The default ``there_and_back`` rate function makes the emphasis
      temporary. A different rate function can produce different behavior.
    - The class does not explicitly restore the mobject in its own methods;
      the resulting animation behavior depends on Transform and the selected
      rate function.
    - The exact visual effect depends on the input mobject and its geometry.

    Examples
    --------
    Example 1: Highlight a circle.

    >>> circle = Circle()
    >>> scene.play(Indicate(circle))

    The circle briefly grows to 1.2 times its original scale and changes
    toward yellow before returning through the default rate function.

    Example 2: Emphasize a specific object with a custom color.

    >>> square = Square()
    >>> scene.play(
    ...     Indicate(
    ...         square,
    ...         color=BLUE,
    ...     )
    ... )

    The target copy is enlarged and assigned blue, producing a temporary
    blue emphasis effect.

    Example 3: Use a stronger scale change.

    >>> triangle = Triangle()
    >>> scene.play(
    ...     Indicate(
    ...         triangle,
    ...         scale_factor=1.5,
    ...     )
    ... )

    The target copy is scaled to 1.5 times its original size, creating a
    more pronounced size change during the transformation.

    Example 4: Customize the duration.

    >>> dot = Dot()
    >>> scene.play(
    ...     Indicate(
    ...         dot,
    ...         run_time=2,
    ...     )
    ... )

    The emphasis animation runs over two seconds. The default rate function
    still controls the progression toward and back from the target.

    See Also
    --------
    Transform
    Flash
    Circumscribe
    FocusOn
    Mobject.scale
    Mobject.set_color
    there_and_back
    """

    def __init__(
        self,
        mobject: Mobject,
        scale_factor: float = 1.2,
        color: ManimColor = YELLOW,
        rate_func: Callable[[float], float] = there_and_back,
        **kwargs
    ):
        self.scale_factor = scale_factor
        self.color = color
        super().__init__(mobject, rate_func=rate_func, **kwargs)

    def create_target(self) -> Mobject:
        target = self.mobject.copy()
        target.scale(self.scale_factor)
        target.set_color(self.color)
        return target


class Flash(AnimationGroup):
    """
    Create a brief radial flash effect around a specified point.

    Flash is a subclass of AnimationGroup that creates multiple short lines
    arranged radially around a center point. Each line is animated using
    ShowCreationThenDestruction, making it appear briefly and then disappear.

    The lines are initially constructed along the positive x-axis, shifted
    outward by the difference between the flash radius and the line length,
    and rotated around the origin at evenly spaced angles. The resulting
    VGroup receives the configured stroke color and width.

    An updater moves the entire line group to the specified point, allowing
    the flash to follow a Mobject when that object's position changes while
    the updater is active.

    Parameters
    ----------
    point : np.ndarray | Mobject
        The location around which the flash appears. This can be a coordinate
        array or a Mobject whose position is used by the line group's updater.

    color : ManimColor, optional
        The stroke color of all flash lines. Defaults to YELLOW.

    line_length : float, optional
        The length of each radial line. Defaults to 0.2.

    num_lines : int, optional
        The number of radial lines used to construct the flash. Defaults to 12.
        The lines are distributed at evenly spaced angles around a full circle.

    flash_radius : float, optional
        The radial distance used when positioning the lines before animation.
        Each line is shifted outward by ``flash_radius - line_length``.
        Defaults to 0.3.

    line_stroke_width : float, optional
        The stroke width applied to all lines. Defaults to 3.0.

    run_time : float, optional
        The total duration of the animation group. Defaults to 1.0 second.

    **kwargs
        Additional keyword arguments forwarded to AnimationGroup, such as
        other supported animation-group configuration options.

    Attributes
    ----------
    point
        The location or Mobject around which the flash is positioned.

    color
        The configured stroke color of the flash lines.

    line_length
        The length of each line.

    num_lines
        The number of radial lines.

    flash_radius
        The radial positioning parameter used when constructing the lines.

    line_stroke_width
        The stroke width applied to the lines.

    lines : VGroup
        The group containing all radial flash lines. It is also supplied as
        the AnimationGroup's ``group``.

    Methods
    -------
    create_lines() -> VGroup
        Construct and return the radial line group. The method creates lines
        at evenly spaced angles, applies the configured stroke style, and
        adds an updater that moves the group to ``self.point``.

    create_line_anims() -> list[Animation]
        Return one ShowCreationThenDestruction animation for each line in
        ``self.lines``.

    Notes
    -----
    - The angular positions are generated with
      ``np.arange(0, TAU, TAU / self.num_lines)``.
    - Each line starts as a segment from ORIGIN to
      ``self.line_length * RIGHT``.
    - The line is shifted by
      ``(self.flash_radius - self.line_length) * RIGHT`` before rotation.
    - The stroke color and width are applied to the complete VGroup.
    - Each line has its own ShowCreationThenDestruction animation.
    - The animation group runs all of these line animations together.
    - The line group has an updater that calls ``move_to(self.point)``.
      If ``point`` is a Mobject, the flash can follow its position while
      the updater is active.
    - ``num_lines`` should be a positive, nonzero value because it is used
      to calculate the angular step. A value of zero would make the angular
      step undefined.
    - The exact appearance depends on the chosen radius, line length, stroke
      width, animation duration, and inherited animation behavior.

    Examples
    --------
    Example 1: Create a default yellow flash at the origin.

    >>> scene.play(Flash(ORIGIN))

    A ring-like arrangement of 12 short yellow lines appears around the
    origin. Each line is drawn and then removed during the animation.

    Example 2: Flash at a specific coordinate.

    >>> point = np.array([2.0, 1.0, 0.0])
    >>> scene.play(Flash(point, color=BLUE))

    The radial flash is positioned at the specified coordinate and uses
    blue strokes instead of the default yellow.

    Example 3: Create a larger flash with more lines.

    >>> scene.play(
    ...     Flash(
    ...         ORIGIN,
    ...         num_lines=20,
    ...         flash_radius=0.5,
    ...         line_length=0.25,
    ...     )
    ... )

    The flash contains 20 evenly distributed lines, with a larger radial
    positioning parameter and longer line segments.

    Example 4: Emphasize a moving Mobject.

    >>> dot = Dot()
    >>> scene.add(dot)
    >>> scene.play(
    ...     dot.animate.shift(RIGHT * 2),
    ...     Flash(dot, color=YELLOW),
    ... )

    The line group uses an updater that moves it to the Dot's position.
    The visible result depends on the updater and animation lifecycle while
    the Dot moves.

    Example 5: Customize stroke width and duration.

    >>> scene.play(
    ...     Flash(
    ...         ORIGIN,
    ...         line_stroke_width=6,
    ...         run_time=0.5,
    ...     )
    ... )

    The flash uses thicker lines and a half-second animation duration.

    See Also
    --------
    AnimationGroup
    ShowCreationThenDestruction
    Line
    VGroup
    Indicate
    FocusOn
    """

    def __init__(
        self,
        point: np.ndarray | Mobject,
        color: ManimColor = YELLOW,
        line_length: float = 0.2,
        num_lines: int = 12,
        flash_radius: float = 0.3,
        line_stroke_width: float = 3.0,
        run_time: float = 1.0,
        **kwargs
    ):
        self.point = point
        self.color = color
        self.line_length = line_length
        self.num_lines = num_lines
        self.flash_radius = flash_radius
        self.line_stroke_width = line_stroke_width

        self.lines = self.create_lines()
        animations = self.create_line_anims()
        super().__init__(
            *animations,
            group=self.lines,
            run_time=run_time,
            **kwargs,
        )

    def create_lines(self) -> VGroup:
        lines = VGroup()
        for angle in np.arange(0, TAU, TAU / self.num_lines):
            line = Line(ORIGIN, self.line_length * RIGHT)
            line.shift((self.flash_radius - self.line_length) * RIGHT)
            line.rotate(angle, about_point=ORIGIN)
            lines.add(line)
        lines.set_stroke(
            color=self.color,
            width=self.line_stroke_width
        )
        lines.add_updater(lambda l: l.move_to(self.point))
        return lines

    def create_line_anims(self) -> list[Animation]:
        return [
            ShowCreationThenDestruction(line)
            for line in self.lines
        ]


class CircleIndicate(Transform):
    """
    Temporarily highlight a mobject by animating a circle around it.

    CircleIndicate is a subclass of Transform that creates a circle surrounding
    the specified mobject and animates that circle from a smaller, initially
    invisible-stroke version to the full surrounding circle.

    The target circle is created with a configurable stroke color and width.
    It is positioned around the mobject using ``circle.surround(mobject)``.
    A copy of this circle is then made, its stroke width is set to zero, and
    it is scaled down by the reciprocal of ``scale_factor``. Transform
    animates from this smaller circle to the full circle.

    By default, the ``there_and_back`` rate function makes the circle expand
    around the object and then return to its starting state, creating a
    temporary highlighting effect.

    Parameters
    ----------
    mobject : Mobject
        The object to highlight. The circle is positioned to surround this
        object when the animation is initialized.

    scale_factor : float, optional
        The factor used to determine the initial circle size. The starting
        circle is scaled by ``1 / scale_factor`` relative to the surrounding
        circle. Defaults to 1.2.

    rate_func : Callable[[float], float], optional
        The rate function controlling the transformation progress.
        Defaults to ``there_and_back``, which typically moves toward the
        target state and then returns to the starting state.

    stroke_color : ManimColor, optional
        The stroke color of the surrounding circle. Defaults to YELLOW.

    stroke_width : float, optional
        The stroke width of the surrounding circle. Defaults to 3.0.

    remover : bool, optional
        Whether the animated mobject should be removed during animation
        cleanup. Defaults to True.

    **kwargs
        Additional keyword arguments forwarded to Transform.

    Notes
    -----
    - The circle is created independently of the highlighted mobject.
    - ``circle.surround(mobject)`` positions the target circle around the
      supplied object.
    - The starting circle is a copy of the target circle with stroke width
      set to zero, then scaled by ``1 / scale_factor``.
    - The target circle retains the configured stroke color and stroke width.
    - The animation uses Transform with the starting circle and target circle.
    - The default ``there_and_back`` rate function creates a temporary
      indication effect. A different rate function changes how the
      transformation progresses.
    - ``scale_factor`` should be nonzero because the constructor calculates
      its reciprocal. A value greater than 1 makes the starting circle
      smaller than the target circle.
    - The ``remover`` setting is forwarded to Transform and controls inherited
      cleanup behavior.
    - This implementation creates and transforms the circle; it does not
      explicitly animate the highlighted mobject itself.

    Examples
    --------
    Example 1: Indicate a circle with a surrounding outline.

    >>> dot = Dot()
    >>> scene.add(dot)
    >>> scene.play(CircleIndicate(dot))

    A circle expands from its smaller starting version to surround the Dot,
    then returns toward the starting state using the default rate function.

    Example 2: Highlight a square in blue.

    >>> square = Square()
    >>> scene.add(square)
    >>> scene.play(
    ...     CircleIndicate(
    ...         square,
    ...         stroke_color=BLUE,
    ...     )
    ... )

    A blue circle is animated around the square.

    Example 3: Make the surrounding circle larger.

    >>> triangle = Triangle()
    >>> scene.add(triangle)
    >>> scene.play(
    ...     CircleIndicate(
    ...         triangle,
    ...         scale_factor=1.5,
    ...     )
    ... )

    The starting circle is scaled by 1 / 1.5 relative to the surrounding
    circle, so the transformation begins with a smaller circle.

    Example 4: Customize stroke width and duration.

    >>> square = Square()
    >>> scene.add(square)
    >>> scene.play(
    ...     CircleIndicate(
    ...         square,
    ...         stroke_width=6,
    ...         run_time=2,
    ...     )
    ... )

    The surrounding circle uses a thicker stroke and the transformation
    runs over two seconds.

    Example 5: Use a different rate function.

    >>> dot = Dot()
    >>> scene.add(dot)
    >>> scene.play(
    ...     CircleIndicate(
    ...         dot,
    ...         rate_func=there_and_back,
    ...     )
    ... )

    The explicitly supplied rate function produces the usual expand-and-return
    progression.

    See Also
    --------
    Transform
    Circle
    Indicate
    Circumscribe
    FocusOn
    Mobject.surround
    """

    def __init__(
        self,
        mobject: Mobject,
        scale_factor: float = 1.2,
        rate_func: Callable[[float], float] = there_and_back,
        stroke_color: ManimColor = YELLOW,
        stroke_width: float = 3.0,
        remover: bool = True,
        **kwargs
    ):
        circle = Circle(stroke_color=stroke_color, stroke_width=stroke_width)
        circle.surround(mobject)
        pre_circle = circle.copy().set_stroke(width=0)
        pre_circle.scale(1 / scale_factor)
        super().__init__(
            pre_circle, circle,
            rate_func=rate_func,
            remover=remover,
            **kwargs
        )


class ShowPassingFlash(ShowPartial):
    """
    Animate a short segment of a mobject passing along its geometry.

    ShowPassingFlash is a subclass of ShowPartial that displays only a moving
    portion of a mobject during the animation. Instead of revealing the entire
    object at once, it computes a lower and upper bound for the visible
    portion based on the current animation progress and ``time_width``.

    As the animation progresses, the visible segment travels from the beginning
    of the mobject's geometry toward its end. When the animation finishes,
    the ``finish()`` method restores every submobject to its complete starting
    geometry using ``pointwise_become_partial(start, 0, 1)``.

    Parameters
    ----------
    mobject : Mobject
        The object whose geometry is used for the passing flash. The visible
        portion is determined by the partial-geometry behavior supported by
        the mobject and its submobjects.

    time_width : float, optional
        The width of the moving visible segment, expressed in normalized
        animation-progress units. Defaults to 0.1. A smaller value produces
        a shorter visible segment, while a larger value produces a wider one.

    remover : bool, optional
        Whether the animated mobject should be removed during animation
        cleanup. Defaults to True.

    **kwargs
        Additional keyword arguments forwarded to ShowPartial, including
        other supported animation settings such as ``run_time``.

    Methods
    -------
    get_bounds(alpha: float) -> tuple[float, float]
        Calculate the lower and upper normalized bounds of the visible
        portion at the given animation progress.

        The method first computes the upper bound as
        ``interpolate(0, 1 + time_width, alpha)`` and the lower bound as
        ``upper - time_width``. It then clamps the upper bound to at most 1
        and the lower bound to at least 0.

    finish() -> None
        Complete the parent animation and restore each submobject to its full
        starting geometry by calling
        ``pointwise_become_partial(start, 0, 1)``.

    Notes
    -----
    - ``alpha`` represents normalized animation progress, typically from 0
      to 1.
    - The bounds returned by ``get_bounds()`` determine which portion of the
      object's geometry is displayed by the inherited ShowPartial behavior.
    - At the beginning, the visible interval starts at the beginning of the
      geometry. As progress increases, the interval moves toward the end.
    - Near the end of the animation, the upper bound is clamped to 1, allowing
      the visible segment to leave the geometry's endpoint.
    - ``time_width`` is a normalized width, not a duration in seconds.
    - ``finish()`` explicitly restores the full geometry of the starting
      submobjects. Whether the object remains in the scene also depends on
      the inherited animation cleanup behavior and the ``remover`` setting.
    - The visual result depends on the geometry and partial-rendering support
      of the mobject being animated.

    Examples
    --------
    Example 1: Create a passing flash along a line.

    >>> line = Line(LEFT * 3, RIGHT * 3)
    >>> scene.add(line)
    >>> scene.play(ShowPassingFlash(line))

    A short portion of the line moves from one end to the other. At the end,
    the animation's finish method restores the full starting geometry.

    Example 2: Make the visible segment wider.

    >>> line = Line(LEFT * 3, RIGHT * 3)
    >>> scene.add(line)
    >>> scene.play(
    ...     ShowPassingFlash(
    ...         line,
    ...         time_width=0.3,
    ...     )
    ... )

    The visible segment spans a larger portion of the normalized geometry
    than it does with the default width of 0.1.

    Example 3: Use a shorter animation duration.

    >>> circle = Circle()
    >>> scene.add(circle)
    >>> scene.play(
    ...     ShowPassingFlash(
    ...         circle,
    ...         time_width=0.1,
    ...         run_time=0.5,
    ...     )
    ... )

    The flash travels along the circle's geometry over half a second.
    The time width remains a normalized progress interval rather than
    changing into a duration in seconds.

    Example 4: Inspect the bounds at an intermediate progress value.

    >>> flash = ShowPassingFlash(
    ...     Line(LEFT, RIGHT),
    ...     time_width=0.1,
    ... )
    >>> print(flash.get_bounds(0.5))
    (0.45, 0.55)

    At alpha = 0.5, the visible interval spans from 0.45 to 0.55 of the
    normalized geometry. This example assumes the default time width of 0.1.

    See Also
    --------
    ShowPartial
    ShowCreation
    ShowCreationThenDestruction
    Uncreate
    Animation
    Mobject.pointwise_become_partial
    """

    def __init__(
        self,
        mobject: Mobject,
        time_width: float = 0.1,
        remover: bool = True,
        **kwargs
    ):
        self.time_width = time_width
        super().__init__(
            mobject,
            remover=remover,
            **kwargs
        )

    def get_bounds(self, alpha: float) -> tuple[float, float]:
        tw = self.time_width
        upper = interpolate(0, 1 + tw, alpha)
        lower = upper - tw
        upper = min(upper, 1)
        lower = max(lower, 0)
        return (lower, upper)

    def finish(self) -> None:
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.pointwise_become_partial(start, 0, 1)


class VShowPassingFlash(Animation):

    """
    Animate a moving stroke flash along a VMobject using a Gaussian profile.

    VShowPassingFlash is an Animation subclass that creates a short, bright
    segment of a VMobject's stroke and moves it along the object's geometry.
    The visible segment is shaped by a Gaussian function, while the stroke
    widths are tapered near the beginning and end of the geometry.

    At the beginning of the animation, the original stroke widths of every
    mobject in the family are recorded. A tapering kernel reduces widths near
    the two ends. During interpolation, a Gaussian profile determines the
    stroke width at each sampled position, producing a passing flash effect.

    Parameters
    ----------
    vmobject : VMobject
        The vector mobject whose stroke will display the moving flash.

    time_width : float, optional
        Controls the width of the Gaussian flash in normalized geometry
        coordinates. Defaults to 0.3. Larger values produce a wider flash.

    taper_width : float, optional
        Controls the width of the tapering regions near both ends of the
        stroke. Defaults to 0.05.

    remover : bool, optional
        Whether the animated mobject should be removed during animation
        cleanup. Defaults to True.

    **kwargs
        Additional keyword arguments forwarded to Animation.

    Attributes
    ----------
    submob_to_widths : dict
        Maps the hash of each family member to its precomputed tapered stroke
        widths. This data is created in begin() and used during interpolation.

    Methods
    -------
    taper_kernel(x)
        Return a taper multiplier for a normalized position x. The multiplier
        increases from the start, remains 1 in the middle, and decreases
        toward the end.

    begin() -> None
        Record the stroke widths for each family member and apply the taper
        kernel to each sampled width before initializing the parent animation.

    interpolate_submobject(
        submobject: VMobject,
        starting_sumobject: None,
        alpha: float
    ) -> None
        Calculate a Gaussian profile centered at the current animation
        position and multiply it by the precomputed tapered stroke widths.

    finish() -> None
        Finish the parent animation and restore the starting style to each
        submobject using match_style().

    Notes
    -----
    - The Gaussian center moves from approximately -time_width / 2 to
      1 + time_width / 2 as alpha progresses from 0 to 1.
    - The Gaussian standard deviation is calculated as time_width / 6, so
      the region three standard deviations from the center spans time_width.
    - Values farther than three standard deviations from the center are
      explicitly set to zero.
    - Stroke widths are sampled from 0 to 1 using np.linspace().
    - The taper kernel reduces widths near both ends of the sampled stroke.
    - The animation changes stroke width rather than explicitly changing
      the object's geometry.
    - finish() restores the starting style after the parent finish method.
    - The exact visual appearance depends on the VMobject's stroke data and
      the values of time_width and taper_width.

    Examples
    --------
    Example 1: Create a passing flash along a line.

    >>> line = Line(LEFT * 3, RIGHT * 3)
    >>> scene.add(line)
    >>> scene.play(VShowPassingFlash(line))

    A bright stroke segment travels along the line using the default Gaussian
    width and taper settings.

    Example 2: Create a wider flash.

    >>> line = Line(LEFT * 3, RIGHT * 3)
    >>> scene.add(line)
    >>> scene.play(
    ...     VShowPassingFlash(
    ...         line,
    ...         time_width=0.5,
    ...     )
    ... )

    The larger time_width produces a wider Gaussian flash.

    Example 3: Increase the tapering region.

    >>> circle = Circle()
    >>> scene.add(circle)
    >>> scene.play(
    ...     VShowPassingFlash(
    ...         circle,
    ...         taper_width=0.15,
    ...     )
    ... )

    The stroke widths are reduced across a wider region near the beginning
    and end of the sampled geometry.

    Example 4: Customize the animation duration.

    >>> square = Square()
    >>> scene.add(square)
    >>> scene.play(
    ...     VShowPassingFlash(
    ...         square,
    ...         time_width=0.2,
    ...         run_time=2,
    ...     )
    ... )

    The flash travels around the square's geometry over two seconds.

    See Also
    --------
    ShowPassingFlash
    ShowPartial
    Animation
    VMobject
    VMobject.get_stroke_widths
    VMobject.set_stroke
    """
    def __init__(
        self,
        vmobject: VMobject,
        time_width: float = 0.3,
        taper_width: float = 0.05,
        remover: bool = True,
        **kwargs
    ):
        self.time_width = time_width
        self.taper_width = taper_width
        super().__init__(vmobject, remover=remover, **kwargs)
        self.mobject = vmobject

    def taper_kernel(self, x):
        if x < self.taper_width:
            return x
        elif x > 1 - self.taper_width:
            return 1.0 - x
        return 1.0

    def begin(self) -> None:
        # Compute an array of stroke widths for each submobject
        # which tapers out at either end
        self.submob_to_widths = dict()
        for sm in self.mobject.get_family():
            widths = sm.get_stroke_widths()
            self.submob_to_widths[hash(sm)] = np.array([
                width * self.taper_kernel(x)
                for width, x in zip(widths, np.linspace(0, 1, len(widths)))
            ])
        super().begin()

    def interpolate_submobject(
        self,
        submobject: VMobject,
        starting_sumobject: None,
        alpha: float
    ) -> None:
        widths = self.submob_to_widths[hash(submobject)]

        # Create a gaussian such that 3 sigmas out on either side
        # will equals time_width
        tw = self.time_width
        sigma = tw / 6
        mu = interpolate(-tw / 2, 1 + tw / 2, alpha)
        xs = np.linspace(0, 1, len(widths))
        zs = (xs - mu) / sigma
        gaussian = np.exp(-0.5 * zs * zs)
        gaussian[abs(xs - mu) > 3 * sigma] = 0

        if len(widths * gaussian) !=0:
            submobject.set_stroke(width=widths * gaussian)


    def finish(self) -> None:
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.match_style(start)


class FlashAround(VShowPassingFlash):
    """
    Animate a bright flash traveling around the boundary of a Mobject.

    FlashAround is a subclass of VShowPassingFlash that creates a temporary
    highlight around an object by animating a moving stroke along a path that
    surrounds it. By default, the path is a SurroundingRectangle, so the flash
    travels around the object's outer boundary.

    This animation is useful for drawing attention to equations, text, shapes,
    diagrams, or other visual elements without permanently changing their
    appearance.

    Parameters
    ----------
    mobject : Mobject
        The object to highlight. A surrounding path is created around this
        object, and the flash travels along that path.

    time_width : float, default=1.0
        Controls the width of the moving flash along the path, relative to the
        path's normalized parameter range. Larger values create a broader flash;
        smaller values create a narrower flash.

    taper_width : float, default=0.0
        Controls the tapering near the ends of the flash. The default value of
        0.0 disables additional endpoint tapering in the inherited animation.

    stroke_width : float, default=4.0
        Thickness of the stroke used to draw the flash around the object.

    color : ManimColor, default=YELLOW
        Color of the animated highlight.

    buff : float, default=SMALL_BUFF
        Distance between the target object and its surrounding rectangular path.
        Increase this value to move the flash farther away from the object.

    n_inserted_curves : int, default=100
        Number of additional curves inserted into the surrounding path to
        provide a smoother and more finely sampled animation path.

    **kwargs
        Additional keyword arguments forwarded to VShowPassingFlash and its
        parent Animation class. These can include supported animation settings
        such as run_time, rate_func, and remover.

    Methods
    -------
    get_path(mobject, buff)
        Creates and returns a SurroundingRectangle around the supplied object
        using the specified buffer distance.

    Implementation Details
    ----------------------
    1. The constructor creates a surrounding rectangle using get_path().
    2. If the target object is fixed in the camera frame, the path is also
       fixed in the frame.
    3. The path receives additional curves using insert_n_curves() to improve
       the smoothness of the traveling flash.
    4. Null curves are removed using get_points_without_null_curves().
    5. The path's stroke color and width are set using color and stroke_width.
    6. The resulting path is passed to VShowPassingFlash, which animates the
       visible stroke along the path.
    7. The inherited animation controls the moving highlight and its timing.

    Examples
    --------
    Example 1: Highlight a circle.

        circle = Circle()
        self.add(circle)

        self.play(FlashAround(circle))

    A yellow flash travels around the circle's surrounding rectangle.

    Example 2: Highlight a mathematical equation.

        equation = Tex(r"E = mc^2")
        self.play(Write(equation))
        self.play(
            FlashAround(
                equation,
                color=YELLOW,
                stroke_width=5,
                run_time=1.5
            )
        )

    The flash draws attention to the equation after it appears.

    Example 3: Use a different color and spacing.

        square = Square()
        self.add(square)

        self.play(
            FlashAround(
                square,
                color=BLUE,
                stroke_width=6,
                buff=0.3,
                run_time=2
            )
        )

    The flash uses a blue stroke, a thicker line, and a larger gap around
    the square.

    Example 4: Highlight a group of objects.

        dot = Dot(LEFT)
        circle = Circle().shift(RIGHT)
        group = VGroup(dot, circle)

        self.add(group)
        self.play(
            FlashAround(
                group,
                color=GREEN,
                buff=0.2,
                run_time=1.5
            )
        )

    The surrounding rectangle is created around the group as a whole.

    Example 5: Make the flash broader.

        triangle = Triangle()
        self.add(triangle)

        self.play(
            FlashAround(
                triangle,
                time_width=1.5,
                stroke_width=8,
                n_inserted_curves=150
            )
        )

    A larger time_width produces a broader moving highlight. The exact visual
    result also depends on the path and animation duration.

    Notes
    -----
    - Despite the name, FlashAround does not necessarily trace the exact
      outline of the target object. Its default path is a SurroundingRectangle.
    - The animation highlights the object's surrounding area rather than
      filling the object itself.
    - The default color is YELLOW, making it suitable for emphasis.
    - A larger buff creates more space between the object and the path.
    - Increasing n_inserted_curves can provide denser path sampling, though
      it may add processing overhead.
    - The path is the object animated by VShowPassingFlash; the target object
      itself is not directly transformed by this class.
    - The fixed-in-frame check helps keep the path consistent with objects
      anchored to the camera frame.
    - The animation's final behavior also depends on inherited settings,
      including remover and run_time.

    See Also
    --------
    VShowPassingFlash
        Animates a moving stroke along a VMobject path.
    ShowPassingFlash
        Displays a passing highlight along an object's path.
    SurroundingRectangle
        Creates a rectangular boundary around an object.
    Indicate
        Briefly emphasizes an object through a visual change.
    Circumscribe
        Draws a surrounding outline around an object.
    """

    def __init__(
        self,
        mobject: Mobject,
        time_width: float = 1.0,
        taper_width: float = 0.0,
        stroke_width: float = 4.0,
        color: ManimColor = YELLOW,
        buff: float = SMALL_BUFF,
        n_inserted_curves: int = 100,
        **kwargs
    ):
        path = self.get_path(mobject, buff)
        if mobject.is_fixed_in_frame():
            path.fix_in_frame()
        path.insert_n_curves(n_inserted_curves)
        path.set_points(path.get_points_without_null_curves())
        path.set_stroke(color, stroke_width)
        super().__init__(path, time_width=time_width, taper_width=taper_width, **kwargs)

    def get_path(self, mobject: Mobject, buff: float) -> SurroundingRectangle:
        return SurroundingRectangle(mobject, buff=buff)


class FlashUnder(FlashAround):
    """
    Animate a moving flash beneath an object.

    FlashUnder is a subclass of FlashAround that highlights an object by
    animating a colored stroke along an underline beneath it. Instead of
    creating a surrounding rectangle, it overrides get_path() to return an
    Underline object.

    This animation is useful for emphasizing words, mathematical equations,
    headings, or specific labels without drawing attention to the entire
    boundary of the object.

    Parameters
    ----------
    mobject : Mobject
        The object to emphasize. An underline is created beneath this object,
        and the animated flash travels along that underline.

    time_width : float, default=1.0
        Controls the width of the moving flash along the underline path.

    taper_width : float, default=0.0
        Controls the tapering near the ends of the flash.

    stroke_width : float, default=4.0
        Thickness of the animated underline stroke.

    color : ManimColor, default=YELLOW
        Color of the moving highlight.

    buff : float, default=SMALL_BUFF
        Distance between the target object and its underline.

    n_inserted_curves : int, default=100
        Number of additional curves inserted into the underline path to
        improve the smoothness of the animation.

    **kwargs
        Additional animation arguments forwarded through FlashAround to
        VShowPassingFlash and its parent Animation class.

    Methods
    -------
    get_path(mobject, buff)
        Returns an Underline beneath the target object, using the specified
        buffer distance and a stretch_factor of 1.0.

    Implementation Details
    ----------------------
    1. FlashUnder inherits the animation setup from FlashAround.
    2. When the inherited constructor calls get_path(), this class's
       overridden method creates an Underline instead of a SurroundingRectangle.
    3. The underline is created with stretch_factor=1.0.
    4. FlashAround's constructor processes the resulting path, including
       handling fixed-in-frame objects, inserting additional curves,
       removing null curves, and setting the stroke appearance.
    5. VShowPassingFlash animates the visible stroke along the underline.

    Examples
    --------
    Example 1: Underline a word with a moving flash.

        word = Text("Important")
        self.add(word)
        self.play(FlashUnder(word))

    A yellow flash travels beneath the word.

    Example 2: Highlight a mathematical equation.

        equation = Tex(r"E = mc^2")
        self.add(equation)
        self.play(
            FlashUnder(
                equation,
                color=BLUE,
                stroke_width=5
            )
        )

    A blue flash travels beneath the equation.

    Example 3: Increase the distance below the object.

        title = Text("Pythagorean Theorem")
        self.add(title)
        self.play(
            FlashUnder(
                title,
                buff=0.2,
                color=GREEN,
                run_time=2
            )
        )

    The underline is placed farther from the title, and the flash uses
    a green stroke.

    Example 4: Emphasize a particular mathematical expression.

        expression = MathTex(r"a^2 + b^2 = c^2")
        self.add(expression)
        self.play(
            FlashUnder(
                expression,
                color=YELLOW,
                stroke_width=6,
                time_width=0.5
            )
        )

    The expression is emphasized by a relatively narrow moving flash.

    Notes
    -----
    - Unlike FlashAround, which normally uses a SurroundingRectangle,
      FlashUnder uses an Underline.
    - The target object itself is not directly transformed by the animation.
    - The underline's position and geometry depend on the target object and
      the buff parameter.
    - Animation timing and other supported settings are inherited from
      FlashAround and its parent classes.

    See Also
    --------
    FlashAround
        Animates a flash around an object's surrounding rectangle.
    VShowPassingFlash
        Animates a moving stroke along a VMobject path.
    Underline
        Creates an underline beneath a Mobject.
    Indicate
        Briefly emphasizes an object through a visual change.
    """

    def get_path(self, mobject: Mobject, buff: float) -> Underline:
        return Underline(mobject, buff=buff, stretch_factor=1.0)


class ShowCreationThenDestruction(ShowPassingFlash):
    """
    Animate a VMobject with a passing stroke that creates and then destroys
    the visible highlight along its path.

    ShowCreationThenDestruction is a subclass of ShowPassingFlash. It uses
    the parent animation's moving stroke effect to make a portion of a
    VMobject appear progressively and then disappear as the highlight moves
    along the object's path.

    This animation is useful for tracing curves, highlighting mathematical
    graphs, emphasizing geometric boundaries, and creating temporary
    visual effects without permanently drawing the entire path.

    Parameters
    ----------
    vmobject : VMobject
        The vector object whose path will be highlighted by the passing flash.

    time_width : float, default=2.0
        Controls the width of the moving visible portion along the path.
        Larger values produce a wider highlight, while smaller values produce
        a narrower highlight.

    **kwargs
        Additional keyword arguments forwarded to ShowPassingFlash, such as
        run_time, rate_func, and other supported animation settings.

    Implementation Details
    ----------------------
    1. The constructor receives a VMobject and the desired time_width.
    2. It forwards both arguments to ShowPassingFlash.
    3. ShowPassingFlash handles the animation of the moving stroke along
       the VMobject's path.
    4. As the stroke progresses, the highlighted portion appears temporarily
       and then disappears, creating a creation-and-destruction effect.

    Examples
    --------
    Example 1: Trace a circle temporarily.

        circle = Circle()
        self.add(circle)
        self.play(
            ShowCreationThenDestruction(circle)
        )

    A moving highlight travels around the circle and disappears as it moves.

    Example 2: Highlight a mathematical curve.

        curve = FunctionGraph(
            lambda x: np.sin(x),
            x_range=[-PI, PI]
        )
        self.add(curve)
        self.play(
            ShowCreationThenDestruction(
                curve,
                time_width=1.0,
                run_time=2
            )
        )

    A temporary highlight travels along the sine curve.

    Example 3: Use a broader passing highlight.

        square = Square()
        self.add(square)
        self.play(
            ShowCreationThenDestruction(
                square,
                time_width=3.0,
                run_time=2
            )
        )

    The larger time_width produces a broader moving highlight.

    Example 4: Emphasize a portion of a parametric curve.

        curve = ParametricCurve(
            lambda t: np.array([
                np.cos(t),
                np.sin(2 * t),
                0
            ]),
            t_range=[0, TAU]
        )
        self.add(curve)
        self.play(
            ShowCreationThenDestruction(
                curve,
                time_width=1.5
            )
        )

    The animation temporarily highlights the curve as the stroke moves along it.

    Notes
    -----
    - This class inherits its animation behavior from ShowPassingFlash.
    - It does not permanently create a complete new path; it produces a
      moving, temporary highlight along an existing VMobject.
    - The target must be a VMobject or a compatible vector object.
    - The actual visual effect depends on the object's path, stroke style,
      time_width, and inherited animation settings.
    - time_width controls the moving highlight's width; run_time controls
      how long the animation takes to play.

    See Also
    --------
    ShowPassingFlash
        Animates a temporary stroke moving along a VMobject.
    VShowPassingFlash
        Animates a passing flash using variable stroke widths.
    ShowCreation
        Progressively reveals an object's path.
    Uncreate
        Animates the disappearance of an object's path.
    """

    def __init__(self, vmobject: VMobject, time_width: float = 2.0, **kwargs):
        super().__init__(vmobject, time_width=time_width, **kwargs)


class ShowCreationThenFadeOut(Succession):
    """
    Animate the creation of a Mobject followed immediately by its fade-out.

    ShowCreationThenFadeOut is a subclass of Succession. It combines two
    animations in sequence: first, ShowCreation progressively reveals the
    object; then, FadeOut gradually makes the object disappear.

    This animation is useful when an object needs to appear temporarily,
    such as when tracing a mathematical construction, presenting an equation,
    or demonstrating a geometric shape before moving to the next step.

    Parameters
    ----------
    mobject : Mobject
        The object to animate. It is first progressively revealed and then
        faded out.

    remover : bool, default=True
        Determines whether the object is removed from the scene after the
        animation sequence finishes. When True, the object is removed
        according to the inherited Succession animation behavior.

    **kwargs
        Additional keyword arguments passed to Succession, such as run_time
        and rate_func, when supported by the parent animation.

    Animation Sequence
    ------------------
    1. ShowCreation(mobject)
       Progressively reveals the object, making it appear as though it is
       being drawn.

    2. FadeOut(mobject)
       Fades the object out after the creation animation finishes.

    3. Succession
       Runs the two animations one after another rather than simultaneously.

    Methods
    -------
    __init__(mobject, remover=True, **kwargs)
        Initializes the sequential animation using ShowCreation followed
        by FadeOut.

    Examples
    --------
    Example 1: Draw and remove a circle.

        circle = Circle()
        self.play(ShowCreationThenFadeOut(circle))

    The circle is drawn progressively and then fades away.

    Example 2: Animate a mathematical equation.

        equation = MathTex(r"a^2 + b^2 = c^2")
        self.play(ShowCreationThenFadeOut(equation))

    The equation appears progressively and then disappears.

    Example 3: Draw and fade out a square with a custom duration.

        square = Square()
        self.play(
            ShowCreationThenFadeOut(
                square,
                run_time=3
            )
        )

    The complete sequence runs within the specified overall duration,
    subject to Succession's timing behavior.

    Example 4: Use the animation in a geometric construction.

        triangle = Triangle()
        self.play(ShowCreationThenFadeOut(triangle))

    The triangle is drawn and then faded out, leaving the scene ready
    for the next construction.

    Notes
    -----
    - The animations run sequentially: ShowCreation completes before
      FadeOut begins.
    - This class does not define a custom interpolation method; it relies
      on Succession, ShowCreation, and FadeOut.
    - remover defaults to True, so the object is removed after the sequence
      according to the inherited animation behavior.
    - The visual result depends on the object type and the implementations
      of ShowCreation and FadeOut.
    - For an animation that leaves the object visible after being drawn,
      use ShowCreation directly instead.

    See Also
    --------
    Succession
        Runs multiple animations one after another.
    ShowCreation
        Progressively reveals a Mobject.
    FadeOut
        Fades a Mobject out of the scene.
    ShowCreationThenDestruction
        Creates a temporary moving highlight along a vector path.
    """

    def __init__(self, mobject: Mobject, remover: bool = True, **kwargs):
        super().__init__(
            ShowCreation(mobject),
            FadeOut(mobject),
            remover=remover,
            **kwargs
        )


class AnimationOnSurroundingRectangle(AnimationGroup):
    """
    Apply an animation to a rectangle that surrounds a Mobject.

    AnimationOnSurroundingRectangle is a subclass of AnimationGroup. It creates
    a SurroundingRectangle around a target object, attaches an updater that
    keeps the rectangle centered on the target, and applies a specified
    animation to that rectangle.

    The animation type is controlled by the class attribute RectAnimationType,
    which defaults to Animation. Subclasses can override this attribute to
    choose a particular animation, such as ShowCreation or FadeIn.

    Parameters
    ----------
    mobject : Mobject
        The object around which the surrounding rectangle is created.
        The rectangle follows the object's position through an updater.

    stroke_width : float, default=2.0
        Thickness of the rectangle's outline.

    stroke_color : ManimColor, default=YELLOW
        Color of the rectangle's outline.

    buff : float, default=SMALL_BUFF
        Spacing between the target object and the surrounding rectangle.

    **kwargs
        Additional keyword arguments forwarded to the animation constructed
        through RectAnimationType. Supported arguments depend on the selected
        animation class.

    Attributes
    ----------
    RectAnimationType : type, default=Animation
        Class-level attribute specifying which animation is applied to the
        surrounding rectangle. Subclasses can override it to customize the
        animation behavior.

    Implementation Details
    ----------------------
    1. Creates a SurroundingRectangle around the target Mobject.
    2. Sets the rectangle's stroke width, stroke color, and buffer distance.
    3. Adds an updater that moves the rectangle to the target object's position.
    4. Constructs an animation using RectAnimationType(rect, **kwargs).
    5. Passes that animation to AnimationGroup.

    Examples
    --------
    Example 1: Animate a surrounding rectangle.

        circle = Circle()
        self.add(circle)

        self.play(
            AnimationOnSurroundingRectangle(circle)
        )

    The rectangle receives the default Animation type. Since Animation itself
    does not define a specific visual effect, a subclass or a more specific
    RectAnimationType is generally needed for a visible result.

    Example 2: Use ShowCreation for the rectangle.

        class DrawAround(AnimationOnSurroundingRectangle):
            RectAnimationType = ShowCreation

        equation = MathTex(r"E = mc^2")
        self.add(equation)

        self.play(
            DrawAround(
                equation,
                stroke_color=YELLOW,
                stroke_width=3,
                buff=0.2
            )
        )

    The rectangle is drawn around the equation.

    Example 3: Fade in a surrounding rectangle.

        class FadeAround(AnimationOnSurroundingRectangle):
            RectAnimationType = FadeIn

        square = Square()
        self.add(square)

        self.play(
            FadeAround(
                square,
                stroke_color=BLUE,
                buff=0.3
            )
        )

    The surrounding rectangle fades in around the square.

    Example 4: Follow a moving object.

        class DrawAround(AnimationOnSurroundingRectangle):
            RectAnimationType = ShowCreation

        dot = Dot(LEFT)
        self.add(dot)

        self.play(
            dot.animate.shift(RIGHT * 2),
            DrawAround(dot)
        )

    The rectangle's updater moves it toward the target object's current
    position as the object moves. Exact behavior depends on the timing of
    the updater and the animation being played.

    Notes
    -----
    - The rectangle is a separate Mobject; it does not replace or transform
      the target object.
    - The updater calls move_to(mobject), keeping the rectangle centered
      on the target's current position.
    - The updater centers the rectangle but does not explicitly resize it
      when the target object's dimensions change.
    - RectAnimationType is a class attribute, making it possible to define
      specialized subclasses without rewriting the constructor.
    - The default Animation class may not create a visible effect by itself.
      Choose an appropriate animation type for the intended result.
    - The rectangle's appearance depends on the target object's geometry,
      buff, stroke_width, and stroke_color.

    See Also
    --------
    AnimationGroup
        Runs multiple animations as a group.
    SurroundingRectangle
        Creates a rectangle around a Mobject.
    ShowCreation
        Progressively reveals a Mobject.
    FadeIn
        Fades a Mobject into the scene.
    """

    RectAnimationType: type = Animation

    def __init__(
        self,
        mobject: Mobject,
        stroke_width: float = 2.0,
        stroke_color: ManimColor = YELLOW,
        buff: float = SMALL_BUFF,
        **kwargs
    ):
        rect = SurroundingRectangle(
            mobject,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            buff=buff,
        )
        rect.add_updater(lambda r: r.move_to(mobject))
        super().__init__(self.RectAnimationType(rect, **kwargs))


class ShowPassingFlashAround(AnimationOnSurroundingRectangle):
    """
    Animate a passing flash around a rectangle surrounding a Mobject.

    ShowPassingFlashAround is a subclass of AnimationOnSurroundingRectangle.
    It creates a SurroundingRectangle around the target object and applies
    ShowPassingFlash to that rectangle, producing a temporary highlight that
    travels along its outline.

    This animation is useful for drawing attention to equations, geometric
    shapes, diagrams, or important text without permanently highlighting
    the entire surrounding boundary.

    Parameters
    ----------
    mobject : Mobject
        The object around which the surrounding rectangle is created.

    stroke_width : float, default=2.0
        Thickness of the surrounding rectangle's stroke.

    stroke_color : ManimColor, default=YELLOW
        Color of the surrounding rectangle's stroke.

    buff : float, default=SMALL_BUFF
        Distance between the target object and the surrounding rectangle.

    **kwargs
        Additional keyword arguments forwarded to ShowPassingFlash, such
        as time_width, run_time, and other supported animation settings.

    Class Attributes
    ----------------
    RectAnimationType : type
        Set to ShowPassingFlash. This determines the animation applied
        to the surrounding rectangle.

    Implementation Details
    ----------------------
    1. Inherits the constructor from AnimationOnSurroundingRectangle.
    2. Creates a SurroundingRectangle around the supplied Mobject.
    3. Adds an updater that keeps the rectangle centered on the target.
    4. Applies ShowPassingFlash to the rectangle.
    5. Animates a temporary stroke along the rectangle's outline.

    Examples
    --------
    Example 1: Highlight a circle with a passing flash.

        circle = Circle()
        self.add(circle)

        self.play(
            ShowPassingFlashAround(circle)
        )

    A temporary flash travels around the rectangle surrounding the circle.

    Example 2: Highlight a mathematical equation.

        equation = MathTex(r"E = mc^2")
        self.add(equation)

        self.play(
            ShowPassingFlashAround(
                equation,
                stroke_color=BLUE,
                stroke_width=4,
                buff=0.2
            )
        )

    A blue flash travels around the equation's surrounding rectangle.

    Example 3: Use a larger buffer.

        square = Square()
        self.add(square)

        self.play(
            ShowPassingFlashAround(
                square,
                buff=0.4,
                stroke_color=GREEN,
                run_time=2
            )
        )

    The flash travels around a rectangle with more space around the square.

    Example 4: Control the flash width.

        triangle = Triangle()
        self.add(triangle)

        self.play(
            ShowPassingFlashAround(
                triangle,
                time_width=0.5,
                stroke_width=5
            )
        )

    The time_width argument is forwarded to ShowPassingFlash and controls
    the width of the moving highlight.

    Notes
    -----
    - The animation highlights the surrounding rectangle, not the exact
      outline of the target object.
    - The target object itself is not directly transformed by this class.
    - The rectangle follows the target's position through an updater.
    - The updater centers the rectangle but does not explicitly resize it
      if the target's dimensions change.
    - The actual visual effect depends on ShowPassingFlash and its
      supported animation parameters.

    See Also
    --------
    AnimationOnSurroundingRectangle
        Base class for animating a surrounding rectangle.
    ShowPassingFlash
        Animates a temporary stroke traveling along a VMobject.
    SurroundingRectangle
        Creates a rectangle around a Mobject.
    FlashAround
        Animates a flash around an object's surrounding boundary.
    """

    RectAnimationType = ShowPassingFlash


class ShowCreationThenDestructionAround(AnimationOnSurroundingRectangle):
    """
    Draw a rectangle around a Mobject and then animate its disappearance.

    ShowCreationThenDestructionAround is a subclass of
    AnimationOnSurroundingRectangle. It creates a SurroundingRectangle around
    a target object and applies ShowCreationThenDestruction to the rectangle.

    The rectangle is progressively drawn along its path and then the visible
    stroke disappears, creating a temporary outline effect around the target.

    This animation is useful for emphasizing equations, geometric shapes,
    diagrams, and important text without leaving a permanent rectangle
    on the screen.

    Parameters
    ----------
    mobject : Mobject
        The object around which the surrounding rectangle is created.

    stroke_width : float, default=2.0
        Thickness of the surrounding rectangle's outline.

    stroke_color : ManimColor, default=YELLOW
        Color of the rectangle's outline.

    buff : float, default=SMALL_BUFF
        Distance between the target object and its surrounding rectangle.

    **kwargs
        Additional keyword arguments forwarded to ShowCreationThenDestruction,
        such as time_width, run_time, and other supported animation settings.

    Class Attributes
    ----------------
    RectAnimationType : type
        Set to ShowCreationThenDestruction. This determines the animation
        applied to the surrounding rectangle.

    Implementation Details
    ----------------------
    1. Inherits the rectangle creation and updater logic from
       AnimationOnSurroundingRectangle.
    2. Creates a SurroundingRectangle around the target Mobject.
    3. Keeps the rectangle centered on the target using an updater.
    4. Applies ShowCreationThenDestruction to the rectangle.
    5. Animates a temporary stroke that travels along the rectangle's path.

    Examples
    --------
    Example 1: Temporarily outline a circle.

        circle = Circle()
        self.add(circle)

        self.play(
            ShowCreationThenDestructionAround(circle)
        )

    The surrounding rectangle is drawn progressively, and its visible
    stroke then disappears.

    Example 2: Highlight an equation.

        equation = MathTex(r"a^2 + b^2 = c^2")
        self.add(equation)

        self.play(
            ShowCreationThenDestructionAround(
                equation,
                stroke_color=YELLOW,
                stroke_width=3,
                buff=0.2
            )
        )

    A temporary yellow outline effect emphasizes the equation.

    Example 3: Use a blue outline with a larger buffer.

        square = Square()
        self.add(square)

        self.play(
            ShowCreationThenDestructionAround(
                square,
                stroke_color=BLUE,
                stroke_width=4,
                buff=0.35,
                run_time=2
            )
        )

    The animation creates a temporary blue highlight around the square.

    Example 4: Emphasize a geometric construction.

        triangle = Triangle()
        self.add(triangle)

        self.play(
            ShowCreationThenDestructionAround(
                triangle,
                stroke_color=GREEN,
                time_width=1.5
            )
        )

    The passing stroke temporarily draws attention to the triangle's
    surrounding rectangular boundary.

    Notes
    -----
    - The animation follows the surrounding rectangle, not the exact
      outline of the target object.
    - The target object itself is not directly transformed by this class.
    - The inherited updater keeps the rectangle centered on the target,
      but does not explicitly resize it when the target's dimensions change.
    - The visible effect depends on ShowCreationThenDestruction and its
      supported animation settings.
    - RectAnimationType is a class attribute, allowing subclasses to choose
      a different animation without rewriting the constructor.

    See Also
    --------
    AnimationOnSurroundingRectangle
        Base class for animating a surrounding rectangle.
    ShowCreationThenDestruction
        Animates a moving stroke that appears and disappears along a path.
    ShowPassingFlashAround
        Animates a passing flash around a surrounding rectangle.
    SurroundingRectangle
        Creates a rectangle around a Mobject.
    """

    RectAnimationType = ShowCreationThenDestruction


class ShowCreationThenFadeAround(AnimationOnSurroundingRectangle):
    """
    Draw a surrounding rectangle around a Mobject and then fade it out.

    ShowCreationThenFadeAround is a subclass of AnimationOnSurroundingRectangle.
    It creates a SurroundingRectangle around the target object and applies
    ShowCreationThenFadeOut to that rectangle.

    The animation first progressively draws the rectangle and then fades it
    out. This provides a temporary highlighting effect that draws attention
    to an object without leaving a permanent outline on the screen.

    Parameters
    ----------
    mobject : Mobject
        The object around which the surrounding rectangle is created.

    stroke_width : float, default=2.0
        Thickness of the surrounding rectangle's outline.

    stroke_color : ManimColor, default=YELLOW
        Color of the rectangle's outline.

    buff : float, default=SMALL_BUFF
        Distance between the target object and its surrounding rectangle.

    **kwargs
        Additional keyword arguments forwarded to ShowCreationThenFadeOut,
        such as run_time and other supported animation settings.

    Class Attributes
    ----------------
    RectAnimationType : type
        Set to ShowCreationThenFadeOut. This specifies the animation applied
        to the surrounding rectangle.

    Implementation Details
    ----------------------
    1. Inherits the rectangle creation logic from
       AnimationOnSurroundingRectangle.
    2. Creates a SurroundingRectangle around the target Mobject.
    3. Adds an updater that keeps the rectangle centered on the target.
    4. Applies ShowCreationThenFadeOut to the rectangle.
    5. ShowCreation progressively draws the rectangle.
    6. FadeOut then fades the rectangle away.

    Examples
    --------
    Example 1: Draw and fade a rectangle around a circle.

        circle = Circle()
        self.add(circle)

        self.play(
            ShowCreationThenFadeAround(circle)
        )

    The rectangle is drawn around the circle and then fades away.

    Example 2: Highlight a mathematical equation.

        equation = MathTex(r"E = mc^2")
        self.add(equation)

        self.play(
            ShowCreationThenFadeAround(
                equation,
                stroke_color=YELLOW,
                stroke_width=3,
                buff=0.2
            )
        )

    A yellow rectangle is drawn around the equation and then fades out.

    Example 3: Use a blue outline with extra spacing.

        square = Square()
        self.add(square)

        self.play(
            ShowCreationThenFadeAround(
                square,
                stroke_color=BLUE,
                stroke_width=4,
                buff=0.3,
                run_time=2
            )
        )

    The blue outline appears around the square before fading away.

    Example 4: Emphasize a geometric shape.

        triangle = Triangle()
        self.add(triangle)

        self.play(
            ShowCreationThenFadeAround(
                triangle,
                stroke_color=GREEN,
                buff=0.25
            )
        )

    The surrounding rectangle temporarily emphasizes the triangle.

    Notes
    -----
    - The animation uses a SurroundingRectangle rather than tracing the
      target object's exact outline.
    - The target object itself is not directly faded out by this class;
      the rectangle is the object passed to ShowCreationThenFadeOut.
    - The updater keeps the rectangle centered on the target but does not
      explicitly resize it if the target's dimensions change.
    - The rectangle is drawn first and faded out second because
      ShowCreationThenFadeOut uses Succession.
    - The overall visual result depends on the inherited animation settings.

    See Also
    --------
    AnimationOnSurroundingRectangle
        Base class for animating a rectangle around a Mobject.
    ShowCreationThenFadeOut
        Draws a Mobject and then fades it out.
    ShowPassingFlashAround
        Animates a passing flash around a surrounding rectangle.
    SurroundingRectangle
        Creates a rectangle around a Mobject.
    """

    RectAnimationType = ShowCreationThenFadeOut


class ApplyWave(Homotopy):
    """
    Apply a traveling wave-like deformation to a Mobject.

    ApplyWave is a subclass of Homotopy. It temporarily displaces points of
    a Mobject along a specified direction, creating a wave-like motion that
    travels across the object from left to right.

    The deformation is controlled by each point's horizontal position.
    Points on the left respond earlier, while points farther to the right
    respond later. The displacement grows and then returns to zero, so the
    object returns toward its original shape as the animation progresses.

    Parameters
    ----------
    mobject : Mobject
        The object to deform with the wave effect.

    direction : np.ndarray, default=UP
        Direction vector in which points are displaced. The default moves
        points upward. Other vectors can produce horizontal, downward, or
        diagonal deformations.

    amplitude : float, default=0.2
        Magnitude of the displacement. Larger values create a more pronounced
        wave, while smaller values produce a subtle deformation.

    run_time : float, default=1.0
        Intended duration of the animation. In this implementation, run_time
        appears in the signature but is not explicitly passed to Homotopy;
        it may therefore be unused unless handled elsewhere.

    **kwargs
        Additional keyword arguments forwarded to Homotopy.

    Implementation Details
    ----------------------
    1. Retrieves the leftmost and rightmost x-coordinates of the Mobject.
    2. Multiplies the direction vector by amplitude to obtain the displacement
       vector.
    3. Defines a homotopy function that is evaluated for points (x, y, z)
       at animation time t.
    4. Calculates each point's normalized horizontal position:

           alpha = (x - left_x) / (right_x - left_x)

    5. Uses an exponential function of alpha to vary the response timing
       across the object's width.
    6. Applies there_and_back(t**power) to make each point move away from
       its original position and then return.
    7. Adds the resulting displacement to the original point coordinates.
    8. Passes the homotopy function and target Mobject to Homotopy.

    Examples
    --------
    Example 1: Apply a basic upward wave to a square.

        square = Square()
        self.add(square)

        self.play(
            ApplyWave(square)
        )

    The square deforms upward in a wave-like motion and returns toward
    its original shape.

    Example 2: Increase the wave amplitude.

        circle = Circle()
        self.add(circle)

        self.play(
            ApplyWave(
                circle,
                amplitude=0.5
            )
        )

    The larger amplitude produces a stronger displacement.

    Example 3: Apply a downward wave.

        text = Text("Hello")
        self.add(text)

        self.play(
            ApplyWave(
                text,
                direction=DOWN,
                amplitude=0.3
            )
        )

    The text undergoes a wave-like deformation in the downward direction.

    Example 4: Apply a diagonal wave.

        square = Square()
        self.add(square)

        self.play(
            ApplyWave(
                square,
                direction=UP + RIGHT,
                amplitude=0.2
            )
        )

    The displacement follows the supplied diagonal direction vector.

    Example 5: Emphasize an equation.

        equation = MathTex(r"E = mc^2")
        self.add(equation)

        self.play(
            ApplyWave(
                equation,
                direction=UP,
                amplitude=0.15
            )
        )

    The equation temporarily deforms as the wave travels across it.

    Notes
    -----
    - The horizontal coordinate x determines the relative timing of the
      deformation.
    - The direction vector controls where points move, while amplitude
      controls the displacement magnitude.
    - there_and_back makes the displacement return toward zero during
      the animation.
    - The implementation divides by right_x - left_x. Objects with zero
      horizontal width can cause division-by-zero or invalid numerical
      results.
    - The exponential power changes the timing across the object's width;
      it is not a simple constant-speed wave.
    - The default direction is UP, so the deformation is vertical.
    - The run_time parameter is present in the signature but is not
      explicitly forwarded to Homotopy in the supplied implementation.
      Use the animation system's supported timing controls when needed.

    See Also
    --------
    Homotopy
        Deforms a Mobject using a time-dependent coordinate transformation.
    there_and_back
        Rate function that progresses forward and then returns.
    ApplyMethod
        Animates a method applied to a Mobject.
    """

    def __init__(
        self,
        mobject: Mobject,
        direction: np.ndarray = UP,
        amplitude: float = 0.2,
        run_time: float = 1.0,
        **kwargs
    ):

        left_x = mobject.get_left()[0]
        right_x = mobject.get_right()[0]
        vect = amplitude * direction

        def homotopy(x, y, z, t):
            alpha = (x - left_x) / (right_x - left_x)
            power = np.exp(2.0 * (alpha - 0.5))
            nudge = there_and_back(t**power)
            return np.array([x, y, z]) + nudge * vect

        super().__init__(homotopy, mobject, **kwargs)


class WiggleOutThenIn(Animation):
    """
    Animate a Mobject by repeatedly scaling and rotating it, then returning
    it toward its original size and orientation.

    WiggleOutThenIn is a subclass of Animation. It combines a temporary
    scaling effect with an oscillating rotation to create a playful wiggle.
    The object grows and shrinks while rotating back and forth, producing
    a motion useful for emphasizing text, equations, icons, and geometric
    objects.

    Parameters
    ----------
    mobject : Mobject
        The object to animate.

    scale_value : float, default=1.1
        Maximum scale factor reached during the animation. A value of 1.1
        means the object can grow to 110% of its original size before
        returning toward its original size.

    rotation_angle : float, default=0.01 * TAU
        Maximum angular multiplier for the oscillating rotation, expressed
        in radians. The actual angle at each moment is determined by the
        wiggle rate function.

    n_wiggles : int, default=6
        Number of oscillations used by the wiggle function. Higher values
        produce more rapid back-and-forth rotation during the animation.

    scale_about_point : np.ndarray | None, default=None
        Point around which the object scales. If None, the object's center
        is used.

    rotate_about_point : np.ndarray | None, default=None
        Point around which the object rotates. If None, the object's center
        is used.

    run_time : float, default=2
        Duration of the animation in seconds.

    **kwargs
        Additional keyword arguments forwarded to the Animation constructor,
        such as rate_func and other supported animation settings.

    Methods
    -------
    get_scale_about_point()
        Returns the point used as the scaling origin. If scale_about_point
        is None, returns the current center of the animated Mobject.

    get_rotate_about_point()
        Returns the point used as the rotation origin. If rotate_about_point
        is None, returns the current center of the animated Mobject.

    interpolate_submobject(submobject, starting_sumobject, alpha)
        Restores the submobject's points from the starting state, applies
        temporary scaling using there_and_back(alpha), and applies the
        oscillating rotation produced by wiggle().

    Implementation Details
    ----------------------
    1. The constructor stores the scale factor, rotation angle, wiggle count,
       and optional transformation origins.
    2. The Animation constructor initializes the animation with the target
       Mobject and run_time.
    3. During interpolation, match_points() resets the animated submobject
       to its starting geometry before each frame's transformations.
    4. The scale factor is calculated by interpolating between 1 and
       scale_value using there_and_back(alpha).
    5. The rotation angle is calculated using wiggle(alpha, n_wiggles)
       multiplied by rotation_angle.
    6. Scaling and rotation are applied around their respective pivot points.

    Examples
    --------
    Example 1: Wiggle a circle.

        circle = Circle()
        self.add(circle)

        self.play(
            WiggleOutThenIn(circle)
        )

    The circle grows slightly and rotates back and forth before returning
    toward its original appearance.

    Example 2: Emphasize a mathematical equation.

        equation = MathTex(r"E = mc^2")
        self.add(equation)

        self.play(
            WiggleOutThenIn(
                equation,
                scale_value=1.2,
                rotation_angle=0.05,
                n_wiggles=8
            )
        )

    The equation becomes slightly larger while performing several small
    rotations.

    Example 3: Use a custom scaling origin.

        square = Square()
        self.add(square)

        self.play(
            WiggleOutThenIn(
                square,
                scale_value=1.3,
                scale_about_point=ORIGIN
            )
        )

    The square scales around the origin rather than its center.

    Example 4: Rotate around a different point.

        triangle = Triangle()
        self.add(triangle)

        self.play(
            WiggleOutThenIn(
                triangle,
                rotate_about_point=LEFT,
                rotation_angle=0.08
            )
        )

    The triangle's oscillating rotation uses LEFT as its pivot point.

    Example 5: Change the animation duration.

        dot = Dot()
        self.add(dot)

        self.play(
            WiggleOutThenIn(
                dot,
                run_time=3,
                n_wiggles=10
            )
        )

    The wiggle lasts three seconds and uses more oscillations.

    Notes
    -----
    - The default scale_value of 1.1 produces a modest size change.
    - rotation_angle is multiplied by the output of wiggle(); it is not
      necessarily the maximum angle reached in every configuration.
    - The default pivot points are obtained from the Mobject's center.
    - match_points() restores the starting geometry before each interpolation
      step, preventing transformations from accumulating frame after frame.
    - The final appearance depends on the interpolation functions and the
      animation's rate_func.
    - The optional pivot points should be NumPy-compatible coordinate arrays
      when supplied explicitly.

    See Also
    --------
    Animation
        Base class for time-dependent Mobject animations.
    ApplyWave
        Applies a traveling wave-like deformation to a Mobject.
    there_and_back
        Rate function that moves forward and then returns.
    wiggle
        Produces an oscillating interpolation value.
    interpolate
        Interpolates between two values.
    """

    def __init__(
        self,
        mobject: Mobject,
        scale_value: float = 1.1,
        rotation_angle: float = 0.01 * TAU,
        n_wiggles: int = 6,
        scale_about_point: np.ndarray | None = None,
        rotate_about_point: np.ndarray | None = None,
        run_time: float = 2,
        **kwargs
    ):
        self.scale_value = scale_value
        self.rotation_angle = rotation_angle
        self.n_wiggles = n_wiggles
        self.scale_about_point = scale_about_point
        self.rotate_about_point = rotate_about_point
        super().__init__(mobject, run_time=run_time, **kwargs)

    def get_scale_about_point(self) -> np.ndarray:
        return self.scale_about_point or self.mobject.get_center()

    def get_rotate_about_point(self) -> np.ndarray:
        return self.rotate_about_point or self.mobject.get_center()

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_sumobject: Mobject,
        alpha: float
    ) -> None:
        submobject.match_points(starting_sumobject)
        submobject.scale(
            interpolate(1, self.scale_value, there_and_back(alpha)),
            about_point=self.get_scale_about_point()
        )
        submobject.rotate(
            wiggle(alpha, self.n_wiggles) * self.rotation_angle,
            about_point=self.get_rotate_about_point()
        )


class TurnInsideOut(Transform):
    def __init__(self, mobject: Mobject, path_arc: float = 90 * DEG, **kwargs):
        super().__init__(mobject, path_arc=path_arc, **kwargs)

    def create_target(self) -> Mobject:
        return self.mobject.copy().reverse_points()


class FlashyFadeIn(AnimationGroup):
    def __init__(self,
        vmobject: VMobject,
        stroke_width: float = 2.0,
        fade_lag: float = 0.0,
        time_width: float = 1.0,
        **kwargs
    ):
        outline = vmobject.copy()
        outline.set_fill(opacity=0)
        outline.set_stroke(width=stroke_width, opacity=1)

        rate_func = kwargs.get("rate_func", smooth)
        super().__init__(
            FadeIn(vmobject, rate_func=squish_rate_func(rate_func, fade_lag, 1)),
            VShowPassingFlash(outline, time_width=time_width),
            **kwargs
        )
