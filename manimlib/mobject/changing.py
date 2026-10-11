from __future__ import annotations

import numpy as np

from manimlib.constants import BLUE_B, BLUE_D, BLUE_E, GREY_BROWN, DEFAULT_MOBJECT_COLOR
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.rate_functions import smooth

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, List, Iterable
    from manimlib.typing import ManimColor, Vect3, Self


class AnimatedBoundary(VGroup):
    """
    Animate a moving, multicolored outline along a VMobject's boundary.

    The animation uses copies of the supplied VMobject to create a
    growing boundary segment and a fading boundary segment. The stroke
    color cycles through the specified colors, while the stroke width
    of the fading segment decreases over time.

    The animation is updated automatically using an updater. The
    ``cycle_rate`` controls how quickly the animation progresses, and
    ``back_and_forth`` determines whether the growing segment alternates
    between drawing from the beginning and drawing from the end.

    Parameters
    ----------
    vmobject : VMobject
        The VMobject whose boundary is animated. Copies of this object
        are used to display the growing and fading boundary segments.
    colors : List[ManimColor]
        Sequence of colors used by the animation. The colors are cycled
        through as the animation progresses.
    max_stroke_width : float
        Maximum stroke width used for the animated boundary.
    cycle_rate : float
        Rate at which the animation progresses through its cycles.
        Larger values make the animation progress more quickly.
    back_and_forth : bool
        Whether the growing boundary alternates its drawing direction
        between the beginning and the end of the VMobject. If ``True``,
        alternate cycles draw from opposite ends; otherwise, drawing
        starts from the beginning each cycle.
    draw_rate_func : Callable[[float], float]
        Rate function used to control the progress of the growing
        boundary segment. Receives a value between 0 and 1 and returns
        the transformed progress value.
    fade_rate_func : Callable[[float], float]
        Rate function used to control the fading of the previous
        boundary segment. Receives a value between 0 and 1 and returns
        the transformed progress value.
    **kwargs
        Additional keyword arguments passed to the parent ``VGroup``
        constructor.

    Examples
    --------
    Create an animated boundary around a circle::

        circle = Circle()
        boundary = AnimatedBoundary(circle)

    Customize the boundary colors and stroke width::

        boundary = AnimatedBoundary(
            Square(),
            colors=[BLUE, GREEN, YELLOW],
            max_stroke_width=5,
        )

    Make the animation progress more quickly::

        boundary = AnimatedBoundary(
            Circle(),
            cycle_rate=1.0,
        )

    Disable the alternating drawing direction::

        boundary = AnimatedBoundary(
            Square(),
            back_and_forth=False,
        )

    Notes
    -----
    The animation is driven by an updater that advances the internal
    time accumulator and updates the partial boundary copies on each
    frame. Add the ``AnimatedBoundary`` instance to a scene to display
    the animation.

    The input VMobject is stored as ``vmobject`` and is not replaced
    by the animated copies. The copies are stored in
    ``boundary_copies``.

    See Also
    --------
    VGroup
        Base class used to group the animated boundary objects.
    VMobject
        Vectorized object whose boundary is animated.
    """

    def __init__(
        self,
        vmobject: VMobject,
        colors: List[ManimColor] = [BLUE_D, BLUE_B, BLUE_E, GREY_BROWN],
        max_stroke_width: float = 3.0,
        cycle_rate: float = 0.5,
        back_and_forth: bool = True,
        draw_rate_func: Callable[[float], float] = smooth,
        fade_rate_func: Callable[[float], float] = smooth,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vmobject: VMobject = vmobject
        self.colors = colors
        self.max_stroke_width = max_stroke_width
        self.cycle_rate = cycle_rate
        self.back_and_forth = back_and_forth
        self.draw_rate_func = draw_rate_func
        self.fade_rate_func = fade_rate_func

        self.boundary_copies: list[VMobject] = [
            vmobject.copy().set_style(
                stroke_width=0,
                fill_opacity=0
            )
            for x in range(2)
        ]
        self.add(*self.boundary_copies)
        self.total_time: float = 0
        self.add_updater(
            lambda m, dt: self.update_boundary_copies(dt)
        )

    def update_boundary_copies(self, dt: float) -> Self:
        # Not actual time, but something which passes at
        # an altered rate to make the implementation below
        # cleaner
        time = self.total_time * self.cycle_rate
        growing, fading = self.boundary_copies
        colors = self.colors
        msw = self.max_stroke_width
        vmobject = self.vmobject

        index = int(time % len(colors))
        alpha = time % 1
        draw_alpha = self.draw_rate_func(alpha)
        fade_alpha = self.fade_rate_func(alpha)

        if self.back_and_forth and int(time) % 2 == 1:
            bounds = (1 - draw_alpha, 1)
        else:
            bounds = (0, draw_alpha)
        self.full_family_become_partial(growing, vmobject, *bounds)
        growing.set_stroke(colors[index], width=msw)

        if time >= 1:
            self.full_family_become_partial(fading, vmobject, 0, 1)
            fading.set_stroke(
                color=colors[index - 1],
                width=(1 - fade_alpha) * msw
            )

        self.total_time += dt
        return self

    def full_family_become_partial(
        self,
        mob1: VMobject,
        mob2: VMobject,
        a: float,
        b: float
    ) -> Self:
        family1 = mob1.family_members_with_points()
        family2 = mob2.family_members_with_points()
        for sm1, sm2 in zip(family1, family2):
            sm1.pointwise_become_partial(sm2, a, b)
        return self


class TracedPath(VMobject):
    """
    Trace the path followed by a point over time.

    A TracedPath creates a VMobject that records the successive positions
    returned by a point-producing function. As the scene updates, the
    recorded points are connected with a smooth curve, creating a visual
    trail behind the moving object.

    The path can retain all recorded points or only a limited portion
    of the trajectory, depending on ``time_traced``. Its appearance
    is controlled by the stroke configuration supplied at initialization.

    Parameters
    ----------
    traced_point_func : Callable[[], Vect3]
        A callable that returns the current 3D position of the point
        to trace. It is evaluated during each update, and the returned
        point is copied before being stored.
    time_traced : float
        Duration of the trajectory to retain. By default, ``np.inf``
        keeps the entire recorded trajectory. A finite value limits
        the trail to a recent portion of the motion.
    time_per_anchor : float
        Time interval between path anchors, expressed in seconds.
        This parameter is stored by the object but is not directly
        used by the current ``update_path`` implementation.
    stroke_color : ManimColor
        Color of the traced path.
    stroke_width : float or Iterable[float]
        Width of the path stroke. A single float applies a uniform
        width, while an iterable can specify varying stroke widths.
    stroke_opacity : float
        Opacity of the path stroke, where 0 is fully transparent
        and 1 is fully opaque.
    **kwargs
        Additional keyword arguments passed to the parent ``VMobject``
        constructor.

    Examples
    --------
    Trace a moving dot::

        dot = Dot()
        trace = TracedPath(dot.get_center)

        self.add(trace, dot)
        dot.add_updater(
            lambda m, dt: m.shift(RIGHT * dt)
        )

    Trace circular motion::

        dot = Dot(radius=0.08)
        dot.move_to(RIGHT)

        trace = TracedPath(
            dot.get_center,
            stroke_color=BLUE,
            stroke_width=3,
        )

        self.add(trace, dot)
        dot.add_updater(
            lambda m, dt: m.rotate(
                dt,
                about_point=ORIGIN,
            )
        )

    Keep a finite trail::

        dot = Dot().move_to(RIGHT)
        trace = TracedPath(
            dot.get_center,
            time_traced=2.0,
            stroke_color=YELLOW,
            stroke_width=4,
        )

        self.add(trace, dot)
        dot.add_updater(
            lambda m, dt: m.rotate(
                dt,
                about_point=ORIGIN,
            )
        )

    Trace a point defined by a custom function::

        tracker = ValueTracker(0)

        def moving_point():
            t = tracker.get_value()
            return np.array([
                np.cos(t),
                np.sin(2 * t),
                0,
            ])

        trace = TracedPath(
            moving_point,
            stroke_color=GREEN,
            stroke_width=2,
        )

        self.add(trace)
        self.play(
            tracker.animate.set_value(TAU),
            run_time=4,
        )

    Customize the stroke appearance::

        trace = TracedPath(
            dot.get_center,
            stroke_color=RED,
            stroke_width=5,
            stroke_opacity=0.7,
        )

    Notes
    -----
    The path is updated automatically using an updater. Each update
    samples the current point position and reconstructs the visible
    path from the recorded positions.

    When ``time_traced`` is finite, the implementation estimates the
    number of relevant samples using the current frame's ``dt``.
    Consequently, the retained trail duration is approximate and can
    depend on the update interval.

    The ``time_per_anchor`` parameter is stored but is not currently
    used by ``update_path`` to control sampling frequency.

    See Also
    --------
    VMobject
        Base class providing vector geometry and stroke styling.
    ShowPassingFlash
        An animation that displays a moving segment of a VMobject.
    ValueTracker
        A helper for animating a numerical value over time.
    """

    def __init__(
        self,
        traced_point_func: Callable[[], Vect3],
        time_traced: float = np.inf,
        time_per_anchor: float = 1.0 / 15,
        stroke_color: ManimColor = DEFAULT_MOBJECT_COLOR,
        stroke_width: float | Iterable[float] = 2.0,
        stroke_opacity: float = 1.0,
        **kwargs
    ):
        self.stroke_config = dict(
            color=stroke_color,
            width=stroke_width,
            opacity=stroke_opacity,
        )

        super().__init__(**kwargs)
        self.traced_point_func = traced_point_func
        self.time_traced = time_traced
        self.time_per_anchor = time_per_anchor
        self.time: float = 0
        self.traced_points: list[np.ndarray] = []
        self.add_updater(lambda m, dt: m.update_path(dt))

    def update_path(self, dt: float) -> Self:
        if dt == 0:
            return self
        point = self.traced_point_func().copy()
        self.traced_points.append(point)

        if self.time_traced < np.inf:
            n_relevant_points = int(self.time_traced / dt + 0.5)
            n_tps = len(self.traced_points)
            if n_tps < n_relevant_points:
                points = self.traced_points + [point] * (n_relevant_points - n_tps)
            else:
                points = self.traced_points[n_tps - n_relevant_points:]
            # Every now and then refresh the list
            if n_tps > 10 * n_relevant_points:
                self.traced_points = self.traced_points[-n_relevant_points:]
        else:
            points = self.traced_points

        if points:
            self.set_points_smoothly(points)

        self.set_stroke(**self.stroke_config)

        self.time += dt
        return self


class TracingTail(TracedPath):
    """
    Create a trailing path that follows a moving Mobject or point.

    TracingTail is a specialized subclass of ``TracedPath`` that
    creates a trail behind a moving object or a point returned by
    a callable. Unlike a basic traced path, it initializes its
    recorded points with repeated copies of the current position,
    allowing the trail to exist immediately instead of starting
    as an empty path.

    The stroke width and opacity can vary along the trail, making
    it possible to create effects such as a thick, opaque head
    that gradually narrows and fades toward the tail.

    Parameters
    ----------
    mobject_or_func : Mobject or Callable[[], np.ndarray]
        The object or callable whose position should be traced.
        If a ``Mobject`` is supplied, its ``get_center`` method is
        used to obtain its current position. Otherwise, the argument
        is treated as a callable that returns a point as a NumPy array.
    time_traced : float
        Duration of the trail to retain, in seconds. The trail follows
        the most recent portion of the object's trajectory over this
        time interval.
    stroke_color : ManimColor
        Color of the trail's stroke.
    stroke_width : float or Iterable[float]
        Stroke width configuration passed to ``TracedPath``.
        A scalar specifies a uniform width, while an iterable can
        specify varying widths along the path. The default ``(0, 3)``
        is intended to create a width gradient from one end of the
        trail to the other.
    stroke_opacity : float or Iterable[float]
        Stroke opacity configuration passed to ``TracedPath``.
        A scalar specifies uniform opacity, while an iterable can
        specify varying opacity along the trail. The default ``(0, 1)``
        is intended to create a fade between transparent and opaque.
    **kwargs
        Additional keyword arguments passed through ``TracedPath``
        to the parent ``VMobject`` constructor.

    Examples
    --------
    Create a tail following a moving Dot::

        dot = Dot(RIGHT)
        tail = TracingTail(dot)

        self.add(tail, dot)
        dot.add_updater(
            lambda m, dt: m.shift(RIGHT * dt)
        )

    Trace circular motion::

        dot = Dot(RIGHT)
        tail = TracingTail(
            dot,
            time_traced=2,
            stroke_color=BLUE,
        )

        self.add(tail, dot)
        dot.add_updater(
            lambda m, dt: m.rotate(
                dt,
                about_point=ORIGIN,
            )
        )

    Customize the width and opacity of the tail::

        dot = Dot()
        tail = TracingTail(
            dot,
            time_traced=1.5,
            stroke_color=YELLOW,
            stroke_width=(0, 5),
            stroke_opacity=(0, 1),
        )

        self.add(tail, dot)
        dot.add_updater(
            lambda m, dt: m.shift(
                RIGHT * dt + UP * dt
            )
        )

    Trace a point supplied by a callable::

        tracker = ValueTracker(0)

        def get_moving_point():
            t = tracker.get_value()
            return np.array([
                np.cos(t),
                np.sin(t),
                0,
            ])

        tail = TracingTail(
            get_moving_point,
            time_traced=3,
            stroke_color=GREEN,
        )

        self.add(tail)
        self.play(
            tracker.animate.set_value(TAU),
            run_time=4,
        )

    Create a short, fast-moving tail::

        dot = Dot()
        tail = TracingTail(
            dot,
            time_traced=0.4,
            stroke_color=RED,
            stroke_width=(0, 4),
            stroke_opacity=(0, 1),
        )

        self.add(tail, dot)
        dot.add_updater(
            lambda m, dt: m.shift(RIGHT * 3 * dt)
        )

    Notes
    -----
    This class inherits the path-updating behavior and stroke styling
    from ``TracedPath``. The supplied callable is sampled as the scene
    updates, and the resulting positions are used to construct the
    visible trail.

    When a Mobject is provided, its center is traced rather than its
    entire outline or boundary.

    The initial point history is populated using the current position
    of the traced point. The number of initial samples is calculated
    as::

        int(time_traced / self.time_per_anchor)

    The ``time_per_anchor`` value is inherited from ``TracedPath``.
    If it is not supplied through ``kwargs``, the inherited default
    is used.

    The actual retained trail duration can be approximate because
    the parent class updates its point history using frame time.

    See Also
    --------
    TracedPath
        Base class that records and displays a point's trajectory.
    Mobject
        Base class for objects that can be positioned and animated.
    ValueTracker
        Utility for animating a numerical value over time.
    """

    def __init__(
        self,
        mobject_or_func: Mobject | Callable[[], np.ndarray],
        time_traced: float = 1.0,
        stroke_color: ManimColor = DEFAULT_MOBJECT_COLOR,
        stroke_width: float | Iterable[float] = (0, 3),
        stroke_opacity: float | Iterable[float] = (0, 1),
        **kwargs
    ):
        if isinstance(mobject_or_func, Mobject):
            func = mobject_or_func.get_center
        else:
            func = mobject_or_func

        super().__init__(
            func,
            time_traced=time_traced,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
            **kwargs
        )
        curr_point = self.traced_point_func()
        n_points = int(self.time_traced / self.time_per_anchor)
        self.traced_points: list[np.ndarray] = [curr_point.copy() for _ in range(n_points)]
