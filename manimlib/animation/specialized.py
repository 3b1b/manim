from __future__ import annotations

from manimlib.animation.composition import LaggedStart
from manimlib.animation.transform import Restore
from manimlib.constants import BLACK, WHITE
from manimlib.mobject.geometry import Circle
from manimlib.mobject.types.vectorized_mobject import VGroup

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from manimlib.typing import ManimColor


class Broadcast(LaggedStart):
    """
    Create a broadcast or ripple effect using expanding concentric circles.

    Broadcast is a subclass of LaggedStart that animates multiple circles
    from a common focal point. Each circle begins with a small radius and
    expands toward the size of its saved original state. The circles start
    at slightly different times, creating a wave-like broadcast effect.

    The animation is built by creating a VGroup of circles and passing a
    Restore animation for each circle to LaggedStart. The lag_ratio
    controls the delay between the start times of consecutive circle
    animations.

    Parameters
    ----------
    focal_point : np.ndarray
        The point around which all circles are positioned. Each circle has
        an updater that moves it to this point.

    small_radius : float, optional
        The initial radius of each circle. Defaults to 0.0, so each circle
        begins with zero width before being restored toward its saved size.

    big_radius : float, optional
        The radius used when initially creating each circle and saving its
        state. Defaults to 5.0. This determines the target circle size
        restored by the animation.

    n_circles : int, optional
        The number of circles created for the broadcast effect. Defaults
        to 5.

    start_stroke_width : float, optional
        The stroke width applied to each circle before the Restore
        animations begin. Defaults to 8.0.

    color : ManimColor, optional
        The stroke color applied to the circles. Defaults to WHITE.

    run_time : float, optional
        The total duration of the LaggedStart animation. Defaults to 3.0.

    lag_ratio : float, optional
        Controls the timing overlap or delay between consecutive circle
        animations. Defaults to 0.2.

    remover : bool, optional
        Passed to LaggedStart to determine whether the animated group is
        removed when the animation finishes. Defaults to True.

    **kwargs
        Additional keyword arguments forwarded to the LaggedStart
        constructor.

    Attributes
    ----------
    focal_point : np.ndarray
        The common center point for all circles.

    small_radius : float
        The initial radius used to set each circle's width.

    big_radius : float
        The radius used when creating the circles and saving their states.

    n_circles : int
        The number of circles in the broadcast.

    start_stroke_width : float
        The stroke width initially assigned to the circles.

    color : ManimColor
        The stroke color initially assigned to the circles.

    Implementation Details
    ----------------------
    1. The constructor stores the supplied configuration values.
    2. It creates an empty VGroup to hold the circles.
    3. For each requested circle, it creates a Circle with radius big_radius,
       black stroke color, and zero stroke width.
    4. An updater is attached to move the circle to focal_point.
    5. The circle's current state is saved using save_state().
    6. Its width is changed to twice small_radius.
    7. Its stroke is set to the requested color and start_stroke_width.
    8. Each circle is added to the VGroup.
    9. Restore animations are created for all circles.
    10. LaggedStart coordinates these Restore animations using run_time
        and lag_ratio, with remover passed through to the parent class.

    The saved state contains the circle's geometry from before its width
    and stroke are changed. Restore uses that saved state as the target
    for each circle's animation.

    Examples
    --------
    Example 1: Basic Broadcast
    --------------------------
    Create a broadcast effect centered at the origin.

        from manimlib import *

        self.play(
            Broadcast(ORIGIN)
        )

    The circles expand from the focal point with staggered timing.

    Example 2: Broadcast from a Dot
    -------------------------------
    Use the position of a Dot as the focal point.

        dot = Dot(LEFT * 2)
        self.add(dot)

        self.play(
            Broadcast(
                dot.get_center(),
                color=BLUE
            )
        )

    The broadcast is centered at the Dot's position.

    Example 3: Customize the Circle Count and Size
    ----------------------------------------------
    Create a larger broadcast with more circles.

        self.play(
            Broadcast(
                focal_point=ORIGIN,
                small_radius=0.1,
                big_radius=3.0,
                n_circles=8,
                color=YELLOW,
                run_time=4
            )
        )

    Example 4: Adjust the Timing Overlap
    ------------------------------------
    Change lag_ratio to control how the individual circle animations
    are staggered.

        self.play(
            Broadcast(
                focal_point=UP,
                n_circles=6,
                lag_ratio=0.1,
                run_time=3
            )
        )

    A smaller lag_ratio generally causes more overlap between the
    individual animations.

    Notes
    -----
    - Each circle's saved state is created before set_width() and
      set_stroke() are called. Restore therefore targets the saved state.
    - The circle updater continually moves the circle to focal_point.
    - The initial circle width is set to 2 * small_radius.
    - The target size is based on the circle's saved state, created with
      radius=big_radius.
    - remover is passed to LaggedStart rather than handled directly by
      this class.
    - The final visual behavior depends on Restore, LaggedStart, updater
      execution, and the parent Animation implementation.
    - Since the updater is attached to each circle, its behavior during
      and after animation depends on how the surrounding scene handles
      Mobject updaters and animation cleanup.

    See Also
    --------
    LaggedStart
    Restore
    Circle
    VGroup
    Animation
    """

    def __init__(
        self,
        focal_point: np.ndarray,
        small_radius: float = 0.0,
        big_radius: float = 5.0,
        n_circles: int = 5,
        start_stroke_width: float = 8.0,
        color: ManimColor = WHITE,
        run_time: float = 3.0,
        lag_ratio: float = 0.2,
        remover: bool = True,
        **kwargs
    ):
        self.focal_point = focal_point
        self.small_radius = small_radius
        self.big_radius = big_radius
        self.n_circles = n_circles
        self.start_stroke_width = start_stroke_width
        self.color = color

        circles = VGroup()
        for x in range(n_circles):
            circle = Circle(
                radius=big_radius,
                stroke_color=BLACK,
                stroke_width=0,
            )
            circle.add_updater(lambda c: c.move_to(focal_point))
            circle.save_state()
            circle.set_width(small_radius * 2)
            circle.set_stroke(color, start_stroke_width)
            circles.add(circle)
        super().__init__(
            *map(Restore, circles),
            run_time=run_time,
            lag_ratio=lag_ratio,
            remover=remover,
            **kwargs
        )
