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
    def get_path(self, mobject: Mobject, buff: float) -> Underline:
        return Underline(mobject, buff=buff, stretch_factor=1.0)


class ShowCreationThenDestruction(ShowPassingFlash):
    def __init__(self, vmobject: VMobject, time_width: float = 2.0, **kwargs):
        super().__init__(vmobject, time_width=time_width, **kwargs)


class ShowCreationThenFadeOut(Succession):
    def __init__(self, mobject: Mobject, remover: bool = True, **kwargs):
        super().__init__(
            ShowCreation(mobject),
            FadeOut(mobject),
            remover=remover,
            **kwargs
        )


class AnimationOnSurroundingRectangle(AnimationGroup):
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
    RectAnimationType = ShowPassingFlash


class ShowCreationThenDestructionAround(AnimationOnSurroundingRectangle):
    RectAnimationType = ShowCreationThenDestruction


class ShowCreationThenFadeAround(AnimationOnSurroundingRectangle):
    RectAnimationType = ShowCreationThenFadeOut


class ApplyWave(Homotopy):
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
