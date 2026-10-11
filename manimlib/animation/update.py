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
