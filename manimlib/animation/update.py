from __future__ import annotations

from manimlib.animation.animation import Animation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from manimlib.mobject.mobject import Mobject


class UpdateFromFunc(Animation):
    """
    UpdateFromFunc
    ==============

    An animation that calls a user-provided function on a Mobject every time
    the animation interpolates. Unlike animations that interpolate between a
    starting state and a target state, UpdateFromFunc delegates the actual
    changes to a custom function.

    This is particularly useful when one Mobject depends on another Mobject
    that is being animated simultaneously. For example, a label can follow
    a moving dot, a line can continuously connect two moving points, or a
    geometric construction can update dynamically as its components change.

    The supplied function receives the animated Mobject as its only argument.
    It can modify that Mobject in place. Although the function's return type
    allows Mobject or None, the return value is ignored by UpdateFromFunc;
    the function should therefore perform its changes directly on the
    provided Mobject.

    Parameters
    ----------
    mobject : Mobject
        The Mobject that will be passed to update_function on each
        interpolation step. This is the object managed by the animation.

    update_function : Callable[[Mobject], Mobject | None]
        A function that accepts the animated Mobject and performs the desired
        update. It is called by interpolate_mobject(alpha) whenever the
        animation is interpolated.

        The function can modify the Mobject's position, dimensions, color,
        points, or other properties. The alpha argument is not passed to this
        function, so progress-dependent behavior must be calculated separately
        or obtained from the current state of other objects.

    suspend_mobject_updating : bool, default=False
        Controls whether the animated Mobject's ordinary updaters are
        suspended while the animation runs. The default is False, meaning
        the Mobject's updaters are not suspended by this animation.

    **kwargs
        Additional keyword arguments forwarded to Animation.__init__.
        These may include standard animation options such as run_time,
        rate_func, and remover, depending on the Animation implementation.

    Attributes
    ----------
    update_function : Callable
        The custom function invoked on the animated Mobject.

    mobject : Mobject
        Inherited from Animation. The object passed to update_function.

    Implementation
    --------------
    1. The constructor stores update_function on the animation instance.
    2. It initializes the parent Animation with the supplied Mobject and
       suspend_mobject_updating option.
    3. During interpolation, interpolate_mobject(alpha) calls
       update_function(self.mobject).
    4. The alpha value is accepted by interpolate_mobject to satisfy the
       Animation interface, but it is not used directly in this class.

    The class does not automatically create a target state, interpolate
    between two saved states, or use the return value of update_function.
    All visual changes are determined by the custom function.

    Examples
    --------
    1. Make a label follow a moving dot
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class FollowDotExample(Scene):
        def construct(self):
            dot = Dot(LEFT * 3)
            label = Text("Moving point").scale(0.5)

            label.next_to(dot, UP)

            self.add(dot, label)

            self.play(
                dot.animate.shift(RIGHT * 6),
                UpdateFromFunc(
                    label,
                    lambda mob: mob.next_to(dot, UP),
                ),
                run_time=3,
            )

            self.wait()

    The dot moves across the scene while UpdateFromFunc repeatedly
    repositions the label relative to the dot's current position.

    2. Keep a line connected to two moving dots
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class DynamicLineExample(Scene):
        def construct(self):
            dot_a = Dot(LEFT * 2)
            dot_b = Dot(RIGHT * 2)
            line = Line(dot_a.get_center(), dot_b.get_center())

            self.add(dot_a, dot_b, line)

            self.play(
                dot_a.animate.shift(UP * 2),
                dot_b.animate.shift(DOWN * 2),
                UpdateFromFunc(
                    line,
                    lambda mob: mob.put_start_and_end_on(
                        dot_a.get_center(),
                        dot_b.get_center(),
                    ),
                ),
                run_time=3,
            )

            self.wait()

    The line is reconstructed from the current centers of both dots on
    each interpolation step, keeping its endpoints connected to them.

    3. Update a circle's radius from another object's position
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class DynamicRadiusExample(Scene):
        def construct(self):
            center = Dot(ORIGIN)
            moving_dot = Dot(RIGHT * 2)
            circle = Circle(radius=2)

            self.add(center, moving_dot, circle)

            self.play(
                moving_dot.animate.move_to(UP * 3),
                UpdateFromFunc(
                    circle,
                    lambda mob: mob.set_width(
                        2 * np.linalg.norm(
                            moving_dot.get_center() - center.get_center()
                        )
                    ),
                ),
                run_time=3,
            )

            self.wait()

    The circle's width is recalculated using the distance between the two
    dots. This example assumes a circle centered at the origin and uses
    set_width, so the displayed result is a circle whose diameter matches
    that distance.

    4. Update a value label while a point moves
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class DynamicValueExample(Scene):
        def construct(self):
            dot = Dot(LEFT * 2)
            label = DecimalNumber(0, num_decimal_places=2)
            label.to_corner(UR)

            self.add(dot, label)

            self.play(
                dot.animate.move_to(RIGHT * 2 + UP),
                UpdateFromFunc(
                    label,
                    lambda mob: mob.set_value(
                        np.linalg.norm(dot.get_center())
                    ),
                ),
                run_time=3,
            )

            self.wait()

    The displayed number is recalculated from the dot's distance from the
    origin as the dot moves.

    Notes
    -----
    - update_function is called during animation interpolation, not merely
      once at the beginning or end of the animation.
    - The function receives only the animated Mobject. Other objects needed
      for the update can be referenced through a closure or another callable.
    - The function should generally mutate the supplied Mobject directly.
      Returning a different Mobject does not replace self.mobject.
    - The alpha argument is not forwarded to update_function. If the update
      needs animation progress, use a different animation class or explicitly
      maintain and access the required progress state.
    - When multiple animations run together, their execution and update order
      can affect the result. Ensure that dependent objects are updated after
      the objects they depend on have reached the relevant frame state.
    - Ordinary Mobject updaters remain active by default because
      suspend_mobject_updating defaults to False. If those updaters conflict
      with the custom function, consider suspending them for the duration
      of the animation.
    - UpdateFromFunc is appropriate for procedural, frame-by-frame changes.
      For a straightforward transformation to a known target state,
      Mobject.animate or Transform may be more suitable.
    - The function's return annotation permits Mobject or None, but this
      implementation ignores the returned value.

    See Also
    --------
    Animation
        Base class defining the animation lifecycle and interpolation API.

    UpdateFromAlphaFunc
        A related animation pattern that passes interpolation progress to a
        custom update function, when available in the installed ManimGL version.

    Mobject.add_updater
        Attaches a persistent updater directly to a Mobject.

    Transform
        Animates a Mobject toward another Mobject's state.

    MoveAlongPath
        Animates a Mobject along a specified path.
    """

    def __init__(
        self,
        mobject: Mobject,
        update_function: Callable[[Mobject], Mobject | None],
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        self.update_function = update_function
        super().__init__(
            mobject,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        self.update_function(self.mobject)


class UpdateFromAlphaFunc(Animation):
    """
    UpdateFromAlphaFunc
    ===================

    An animation that updates a Mobject by repeatedly calling a custom
    function with both the Mobject and its normalized animation progress.

    UpdateFromAlphaFunc is useful when the appearance or geometry of an
    object must be calculated procedurally throughout an animation. Unlike
    UpdateFromFunc, which passes only the Mobject to its callback, this
    class also supplies an alpha value representing the animation's progress
    after applying the animation's timing configuration.

    The callback can use this progress value to calculate positions, sizes,
    colors, rotations, or other properties. This allows the animation to
    follow a custom mathematical rule rather than simply interpolating
    between a starting state and a target state.

    Parameters
    ----------
    mobject : Mobject
        The Mobject that will be modified by update_function throughout
        the animation.

    update_function : Callable[[Mobject, float], Mobject | None]
        A callable receiving two arguments:

        - mobject: the object being animated.
        - alpha: the adjusted animation progress, generally ranging from
          0 to 1 when the rate function and timing configuration follow
          their usual conventions.

        The function should modify the supplied Mobject directly. Although
        the type annotation permits returning a Mobject or None, the return
        value is ignored by this implementation.

    suspend_mobject_updating : bool, default=False
        Determines whether the animated Mobject's ordinary updaters are
        suspended while the animation runs. By default, they are not
        suspended.

    **kwargs
        Additional keyword arguments forwarded to Animation.__init__.
        Depending on the installed ManimGL version, these can include
        options such as run_time, rate_func, and remover.

    Attributes
    ----------
    update_function : Callable
        The custom callback invoked on every interpolation step.

    mobject : Mobject
        Inherited from Animation. The object passed to update_function.

    Implementation
    --------------
    1. The constructor stores update_function on the instance.
    2. The parent Animation constructor initializes the animation and
       its timing-related configuration.
    3. When interpolation occurs, interpolate_mobject(alpha) transforms
       the incoming interpolation value using time_spanned_alpha and
       rate_func.
    4. The resulting true_alpha is passed to update_function alongside
       self.mobject.

    The callback receives the adjusted progress value, not necessarily
    the raw alpha supplied to interpolate_mobject. Consequently, the
    animation's rate function can influence how quickly the callback's
    calculated changes progress.

    Examples
    --------
    1. Move a dot along a straight path
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class MoveDotExample(Scene):
        def construct(self):
            dot = Dot(LEFT * 3)
            start = LEFT * 3
            end = RIGHT * 3

            self.add(dot)

            self.play(
                UpdateFromAlphaFunc(
                    dot,
                    lambda mob, alpha: mob.move_to(
                        interpolate(start, end, alpha)
                    ),
                    run_time=3,
                )
            )

            self.wait()

    The callback calculates the dot's position from the supplied progress
    value. The interpolation function blends the starting and ending
    coordinates.

    2. Animate a circle's radius
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class RadiusExample(Scene):
        def construct(self):
            circle = Circle(radius=0.5)
            self.add(circle)

            self.play(
                UpdateFromAlphaFunc(
                    circle,
                    lambda mob, alpha: mob.become(
                        Circle(
                            radius=0.5 + 1.5 * alpha,
                            color=BLUE,
                        )
                    ),
                    run_time=3,
                )
            )

            self.wait()

    The circle is repeatedly replaced with a circle whose radius depends
    on alpha. Because become copies the target object's appearance and
    geometry, properties not explicitly preserved by the replacement may
    change as well.

    3. Animate a dot along a semicircle
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class SemicirclePathExample(Scene):
        def construct(self):
            dot = Dot()
            radius = 2

            self.add(dot)

            self.play(
                UpdateFromAlphaFunc(
                    dot,
                    lambda mob, alpha: mob.move_to(
                        radius * np.array([
                            np.cos(PI * alpha),
                            np.sin(PI * alpha),
                            0,
                        ])
                    ),
                    run_time=3,
                )
            )

            self.wait()

    The dot follows the upper semicircle from the rightmost point to the
    leftmost point. The path is calculated directly from the angle PI *
    alpha.

    4. Change color progressively
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class ColorProgressExample(Scene):
        def construct(self):
            square = Square(color=BLUE)
            self.add(square)

            self.play(
                UpdateFromAlphaFunc(
                    square,
                    lambda mob, alpha: mob.set_color(
                        interpolate_color(BLUE, RED, alpha)
                    ),
                    run_time=3,
                )
            )

            self.wait()

    The square's color is recalculated on each interpolation step using
    the current adjusted alpha.

    5. Animate a point with a nonlinear trajectory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class NonlinearPathExample(Scene):
        def construct(self):
            dot = Dot()
            self.add(dot)

            self.play(
                UpdateFromAlphaFunc(
                    dot,
                    lambda mob, alpha: mob.move_to(
                        np.array([
                            4 * (alpha - 0.5),
                            2 * np.sin(2 * PI * alpha),
                            0,
                        ])
                    ),
                    run_time=4,
                    rate_func=smooth,
                )
            )

            self.wait()

    The horizontal and vertical coordinates are calculated from alpha.
    The smooth rate function changes the relationship between elapsed
    animation time and the progress value supplied to the callback.

    Notes
    -----
    - The callback is invoked during interpolation, so it should be
      efficient enough to execute repeatedly.
    - The callback receives the adjusted progress value produced by
      rate_func(time_spanned_alpha(alpha)).
    - A rate function may produce values outside the interval [0, 1].
      Callbacks should account for this if they require strictly bounded
      progress.
    - The callback's return value is ignored. Modify the supplied Mobject
      directly rather than expecting a returned object to replace it.
    - When using become() or reconstructing an object, ensure that the
      replacement preserves any styling or structure that should remain.
    - suspend_mobject_updating defaults to False. Existing updaters may
      therefore interact with changes made by update_function.
    - This class is useful for custom procedural animations. For simple
      transformations between known states, Mobject.animate or Transform
      may be more convenient.
    - If the callback needs only the Mobject and not animation progress,
      UpdateFromFunc is a simpler alternative.

    See Also
    --------
    Animation
        Base class providing animation timing and interpolation behavior.

    UpdateFromFunc
        Calls a custom function with the animated Mobject only.

    Transform
        Animates a Mobject toward a target Mobject.

    MoveAlongPath
        Animates a Mobject along a path.

    Mobject.add_updater
        Adds a persistent updater to a Mobject.
    """

    def __init__(
        self,
        mobject: Mobject,
        update_function: Callable[[Mobject, float], Mobject | None],
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        self.update_function = update_function
        super().__init__(mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        true_alpha = self.rate_func(self.time_spanned_alpha(alpha))
        self.update_function(self.mobject, true_alpha)


class MaintainPositionRelativeTo(Animation):
    def __init__(
        self,
        mobject: Mobject,
        tracked_mobject: Mobject,
        **kwargs
    ):
        self.tracked_mobject = tracked_mobject
        self.diff = mobject.get_center() - tracked_mobject.get_center()
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        target = self.tracked_mobject.get_center()
        location = self.mobject.get_center()
        self.mobject.shift(target - location + self.diff)
