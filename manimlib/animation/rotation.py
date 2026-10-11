from __future__ import annotations

from manimlib.animation.animation import Animation
from manimlib.constants import ORIGIN, OUT
from manimlib.constants import PI, TAU
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import smooth

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from typing import Callable
    from manimlib.mobject.mobject import Mobject


class Rotating(Animation):
    """
    Animate a Mobject by rotating it through a specified angle.

    Rotating is an Animation subclass that rotates a Mobject around a
    specified axis and pivot location over the duration of an animation.
    By default, it performs one complete revolution around the OUT axis
    over five seconds.

    Unlike a simple one-time rotation, this animation restores pointlike
    data from the starting Mobject before applying the current rotation.
    This helps the rotation be evaluated relative to the original animated
    state rather than accumulating repeated rotations at every frame.

    Parameters
    ----------
    mobject : Mobject
        The object to rotate.

    angle : float, optional
        The total rotation angle, expressed in radians. Defaults to TAU,
        corresponding to one complete revolution.

    axis : np.ndarray, optional
        The axis of rotation, represented by a vector. Defaults to OUT,
        which points along the positive z-axis and produces rotation in
        the xy-plane for standard 3D coordinates.

    about_point : np.ndarray or None, optional
        The point around which the Mobject rotates. If None, the behavior
        is determined by Mobject.rotate's default pivot handling.

    about_edge : np.ndarray or None, optional
        An edge-direction vector used by Mobject.rotate to determine the
        rotation pivot when applicable. Its exact effect depends on the
        parent Mobject.rotate implementation.

    run_time : float, optional
        The animation duration in seconds. Defaults to 5.0.

    rate_func : Callable[[float], float], optional
        A function mapping animation progress to rotation progress.
        Defaults to linear.

    suspend_mobject_updating : bool, optional
        Whether to suspend the Mobject's regular updating during the
        animation. Defaults to False.

    **kwargs
        Additional keyword arguments forwarded to the parent Animation
        constructor.

    Attributes
    ----------
    angle : float
        The total rotation angle in radians.

    axis : np.ndarray
        The axis around which the Mobject rotates.

    about_point : np.ndarray or None
        The explicitly supplied rotation pivot point, if any.

    about_edge : np.ndarray or None
        The edge-direction setting passed to Mobject.rotate.

    How It Works
    ------------
    1. The constructor stores the rotation parameters.
    2. The parent Animation constructor initializes the animation and
       its starting state.
    3. During interpolation, the animation pairs family members containing
       points with their corresponding starting family members.
    4. For each pair, it restores the values of the pointlike data keys
       from the starting member.
    5. It calculates the current rotation angle using the rate function
       and time-adjusted alpha.
    6. It calls Mobject.rotate() with the resulting angle, axis, and
       pivot configuration.

    The angle applied at a given interpolation step is conceptually:

        current_angle = rate_func(time_spanned_alpha(alpha)) * angle

    For a linear rate function and the usual progress interval from 0 to 1,
    the rotation progresses proportionally from zero to the requested angle.

    Examples
    --------
    Example 1: One Complete Revolution
    ----------------------------------
    Rotate a square through one full revolution.

        from manimlib import *

        square = Square()
        self.add(square)

        self.play(
            Rotating(
                square,
                run_time=4
            )
        )

    The default angle is TAU, representing 2*pi radians.

    Example 2: Rotate Through 90 Degrees
    ------------------------------------
    Specify the angle explicitly in radians.

        square = Square()
        self.add(square)

        self.play(
            Rotating(
                square,
                angle=PI / 2,
                run_time=2
            )
        )

    The square rotates through a quarter turn.

    Example 3: Rotate Around a Specific Point
    -----------------------------------------
    The about_point parameter specifies the pivot point.

        square = Square().shift(RIGHT * 2)
        self.add(square)

        self.play(
            Rotating(
                square,
                angle=PI,
                about_point=ORIGIN,
                run_time=3
            )
        )

    The square rotates around the origin rather than around its own center.

    Example 4: Rotate Around the X-Axis
    -----------------------------------
    The axis parameter controls the direction of the rotation axis.

        cube = Cube()
        self.add(cube)

        self.play(
            Rotating(
                cube,
                angle=PI,
                axis=RIGHT,
                run_time=3
            )
        )

    The cube rotates around the positive x-axis.

    Example 5: Use a Nonlinear Rate Function
    ----------------------------------------
    A nonlinear rate function changes the timing of the rotation.

        square = Square()
        self.add(square)

        self.play(
            Rotating(
                square,
                angle=TAU,
                rate_func=smooth,
                run_time=4
            )
        )

    The smooth rate function changes the angular progression so that
    rotation is slower near the beginning and end than around the middle.

    Notes
    -----
    - Rotation angles are specified in radians, not degrees.
    - TAU is equivalent to 2*pi radians and represents a full revolution.
    - OUT is the default rotation axis and normally corresponds to the
      positive z-axis.
    - The rate function is applied to time_spanned_alpha(alpha), rather
      than directly to alpha.
    - Pointlike data is restored for the paired family members before
      the current rotation is applied.
    - The animation delegates the actual geometric rotation and pivot
      behavior to Mobject.rotate().
    - The result depends on the Mobject's geometry, its family structure,
      and the pivot arguments supplied.
    - The about_point and about_edge parameters are forwarded to rotate();
      their precise interaction is determined by that method's
      implementation.
    - The axis should be a valid vector for the underlying rotation method.

    See Also
    --------
    Animation
    Mobject.rotate
    Rotate
    MoveAlongPath
    """

    def __init__(
        self,
        mobject: Mobject,
        angle: float = TAU,
        axis: np.ndarray = OUT,
        about_point: np.ndarray | None = None,
        about_edge: np.ndarray | None = None,
        run_time: float = 5.0,
        rate_func: Callable[[float], float] = linear,
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        self.angle = angle
        self.axis = axis
        self.about_point = about_point
        self.about_edge = about_edge
        super().__init__(
            mobject,
            run_time=run_time,
            rate_func=rate_func,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        pairs = zip(
            self.mobject.family_members_with_points(),
            self.starting_mobject.family_members_with_points(),
        )
        for sm1, sm2 in pairs:
            for key in sm1.pointlike_data_keys:
                sm1.data[key] = sm2.data[key]
        self.mobject.rotate(
            self.rate_func(self.time_spanned_alpha(alpha)) * self.angle,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )


class Rotate(Rotating):
    """
    Animate a Mobject through a specified rotation using convenient defaults.

    Rotate is a subclass of Rotating that provides a simplified interface
    for performing a rotation animation. It inherits the interpolation
    behavior from Rotating while changing the default angle, duration,
    rate function, and pivot configuration.

    By default, Rotate turns the Mobject through PI radians (180 degrees)
    over one second, using the smooth rate function and the ORIGIN value
    for about_edge.

    Parameters
    ----------
    mobject : Mobject
        The object to rotate.

    angle : float, optional
        The total rotation angle in radians. Defaults to PI, corresponding
        to a half-turn or 180-degree rotation.

    axis : np.ndarray, optional
        The axis of rotation. Defaults to OUT, which typically represents
        the positive z-axis.

    run_time : float, optional
        The duration of the animation in seconds. Defaults to 1.

    rate_func : Callable[[float], float], optional
        The function controlling the timing of the rotation. Defaults to
        smooth, which eases the animation near its beginning and end.

    about_edge : np.ndarray, optional
        The edge-direction vector passed to Rotating and ultimately to
        Mobject.rotate(). Defaults to ORIGIN. Its precise effect depends
        on the implementation of Mobject.rotate().

    **kwargs
        Additional keyword arguments forwarded to the Rotating constructor,
        including other supported Animation options.

    Inheritance
    -----------
    Rotate inherits from Rotating, which inherits from Animation.

    The constructor forwards the Mobject, angle, and axis positionally
    to Rotating, and passes run_time, rate_func, and about_edge by keyword.
    Other supported keyword arguments are forwarded through **kwargs.

    How It Works
    ------------
    1. The constructor receives the Mobject and rotation settings.
    2. It delegates initialization to Rotating.
    3. Rotating stores the rotation parameters and initializes Animation.
    4. During interpolation, Rotating restores pointlike data from the
       starting Mobject's family members.
    5. It computes the current rotation angle using the configured rate
       function and time-adjusted animation progress.
    6. It calls Mobject.rotate() with the calculated angle, axis, and
       pivot configuration.

    The applied angle is conceptually:

        current_angle = rate_func(time_spanned_alpha(alpha)) * angle

    For the default smooth rate function, the angular progression is
    nonlinear in time even though the total angle remains PI radians.

    Examples
    --------
    Example 1: Rotate a Square by 180 Degrees
    -----------------------------------------
        from manimlib import *

        square = Square()
        self.add(square)

        self.play(
            Rotate(square)
        )

    The square rotates through PI radians using the default one-second
    duration and smooth rate function.

    Example 2: Rotate by 90 Degrees
    -------------------------------
        square = Square()
        self.add(square)

        self.play(
            Rotate(
                square,
                angle=PI / 2,
                run_time=2
            )
        )

    The square rotates through a quarter-turn over two seconds.

    Example 3: Rotate a Cube Around the X-Axis
    ------------------------------------------
        cube = Cube()
        self.add(cube)

        self.play(
            Rotate(
                cube,
                angle=PI,
                axis=RIGHT,
                run_time=3
            )
        )

    The cube rotates around the x-axis.

    Example 4: Use Linear Timing
    ----------------------------
        square = Square()
        self.add(square)

        self.play(
            Rotate(
                square,
                angle=TAU,
                rate_func=linear,
                run_time=4
            )
        )

    The square completes one full revolution with a linear rate function,
    giving a constant angular progression with respect to animation time.

    Example 5: Rotate a Mobject Around a Chosen Point
    -------------------------------------------------
        square = Square().shift(RIGHT * 2)
        self.add(square)

        self.play(
            Rotate(
                square,
                angle=PI,
                about_point=ORIGIN,
                run_time=2
            )
        )

    The about_point argument is inherited through **kwargs and is passed
    to Rotating, allowing the rotation pivot to be specified explicitly.

    Notes
    -----
    - Rotate does not implement its own interpolation method; it uses the
      behavior inherited from Rotating.
    - Angles are expressed in radians. PI represents 180 degrees, while
      TAU represents a full 360-degree revolution.
    - The default rate function is smooth, unlike Rotating's linear
      default.
    - The default duration is one second, unlike Rotating's five-second
      default.
    - The about_edge parameter is forwarded to Rotating. The parent class
      also supports about_point, which can be supplied through **kwargs.
    - The actual pivot behavior is determined by Mobject.rotate().
    - The animation changes the Mobject's geometric orientation and
      position according to the selected axis and pivot.

    See Also
    --------
    Rotating
    Animation
    Mobject.rotate
    MoveAlongPath
    """

    def __init__(
        self,
        mobject: Mobject,
        angle: float = PI,
        axis: np.ndarray = OUT,
        run_time: float = 1,
        rate_func: Callable[[float], float] = smooth,
        about_edge: np.ndarray = ORIGIN,
        **kwargs
    ):
        super().__init__(
            mobject, angle, axis,
            run_time=run_time,
            rate_func=rate_func,
            about_edge=about_edge,
            **kwargs
        )
