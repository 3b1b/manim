from __future__ import annotations

from manimlib.animation.animation import Animation
from manimlib.mobject.numbers import DecimalNumber
from manimlib.utils.bezier import interpolate
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable


class ChangingDecimal(Animation):
    """
    Animate a DecimalNumber by updating its displayed numerical value.

    ChangingDecimal is an Animation subclass designed to change the value
    shown by a DecimalNumber over the course of an animation. Instead of
    directly transforming the digits or interpolating between two fixed
    numbers, it uses a user-provided function to calculate the value at
    each animation progress step.

    The update function receives the animation's time-adjusted progress
    and returns the numerical value that should be displayed.

    Parameters
    ----------
    decimal_mob : DecimalNumber
        The DecimalNumber object whose displayed value will change.

        The constructor verifies that this argument is an instance of
        DecimalNumber using an assert statement.

    number_update_func : Callable[[float], float]
        A callable that accepts a time-adjusted animation progress value
        and returns the numerical value to display.

        Conceptually:

            progress -> displayed_number

    suspend_mobject_updating : bool, optional
        Whether to suspend the DecimalNumber's regular updating during
        the animation. Defaults to False.

    **kwargs
        Additional keyword arguments passed to the parent Animation
        constructor, such as run_time, rate_func, and other supported
        animation options.

    Attributes
    ----------
    number_update_func : Callable[[float], float]
        The function used to calculate the displayed value at each
        interpolation step.

    mobject : DecimalNumber
        The DecimalNumber being animated. The constructor explicitly
        assigns decimal_mob to this attribute after initializing the
        parent Animation.

    How It Works
    ------------
    1. The constructor checks whether decimal_mob is a DecimalNumber.
    2. It stores number_update_func for use during interpolation.
    3. The parent Animation constructor initializes the animation.
    4. The constructor explicitly assigns decimal_mob to self.mobject.
    5. During interpolation, time_spanned_alpha(alpha) converts the
       animation's alpha into the time-adjusted progress value.
    6. number_update_func(true_alpha) calculates the new numerical value.
    7. self.mobject.set_value(new_value) updates the displayed number.

    The key distinction is that the displayed value is calculated from
    the progress value on every interpolation step. It is not necessarily
    a linear interpolation between two predefined endpoints.

    Examples
    --------
    Example 1: Count from Zero to Ten
    ---------------------------------
    A DecimalNumber can display a value that increases with animation
    progress.

        from manimlib import *

        number = DecimalNumber(0)

        self.add(number)
        self.play(
            ChangingDecimal(
                number,
                lambda t: 10 * t,
                run_time=3
            )
        )

    The displayed value progresses from approximately 0 to 10 when the
    rate function spans the usual interval from 0 to 1.

    Example 2: Count Backward
    -------------------------
    The update function can decrease the displayed value.

        number = DecimalNumber(100)

        self.add(number)
        self.play(
            ChangingDecimal(
                number,
                lambda t: 100 * (1 - t),
                run_time=4
            )
        )

    The number decreases from 100 toward 0 as the animation progresses.

    Example 3: Nonlinear Change
    ---------------------------
    A nonlinear update function can make the displayed value change
    nonlinearly with animation progress.

        number = DecimalNumber(0)

        self.add(number)
        self.play(
            ChangingDecimal(
                number,
                lambda t: 20 * t**2,
                run_time=3
            )
        )

    Because the update function uses t squared, the displayed value
    changes slowly at first and more rapidly later when progress increases
    from 0 to 1.

    Example 4: Display a Sine Function
    ----------------------------------
    The update function can calculate values from mathematical functions.

        import numpy as np
        from manimlib import *

        number = DecimalNumber(0, num_decimal_places=2)

        self.add(number)
        self.play(
            ChangingDecimal(
                number,
                lambda t: np.sin(2 * PI * t),
                run_time=4
            )
        )

    The displayed value follows one sine-wave cycle as the animation
    progresses from 0 to 1.

    Example 5: Update a Mathematical Expression
    -------------------------------------------
    A changing DecimalNumber can be placed beside explanatory text.

        from manimlib import *

        label = Text("Value:")
        number = DecimalNumber(1)

        group = VGroup(label, number).arrange(RIGHT)
        self.add(group)

        self.play(
            ChangingDecimal(
                number,
                lambda t: 1 + 9 * t,
                run_time=3
            )
        )

    Notes
    -----
    - time_spanned_alpha(alpha) is used instead of alpha directly, so the
      value passed to number_update_func follows the animation's configured
      time progression.
    - The update function should return a value accepted by
      DecimalNumber.set_value().
    - The number of decimal places and other formatting options are
      controlled by the DecimalNumber object itself.
    - The animation does not impose a particular mathematical relationship
      between progress and value. Linear, nonlinear, periodic, or
      piecewise functions can be supplied.
    - The assert statement validates the argument during initialization
      when Python assertions are enabled.
    - The displayed result depends on the configured rate function,
      animation runtime, and implementation of time_spanned_alpha().
    - If the update function returns values outside the intended range,
      the DecimalNumber will attempt to display those values according
      to its own formatting configuration.

    See Also
    --------
    Animation
    DecimalNumber
    DecimalNumber.set_value
    Animation.time_spanned_alpha
    """

    def __init__(
        self,
        decimal_mob: DecimalNumber,
        number_update_func: Callable[[float], float],
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        assert isinstance(decimal_mob, DecimalNumber)
        self.number_update_func = number_update_func
        super().__init__(
            decimal_mob,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )
        self.mobject = decimal_mob

    def interpolate_mobject(self, alpha: float) -> None:
        true_alpha = self.time_spanned_alpha(alpha)
        new_value = self.number_update_func(true_alpha)
        self.mobject.set_value(new_value)


class ChangeDecimalToValue(ChangingDecimal):
    def __init__(
        self,
        decimal_mob: DecimalNumber,
        target_number: float | complex,
        **kwargs
    ):
        start_number = decimal_mob.number
        super().__init__(
            decimal_mob,
            lambda a: interpolate(start_number, target_number, a),
            **kwargs
        )


class CountInFrom(ChangingDecimal):
    def __init__(
        self,
        decimal_mob: DecimalNumber,
        source_number: float | complex = 0,
        **kwargs
    ):
        start_number = decimal_mob.get_value()
        super().__init__(
            decimal_mob,
            lambda a: interpolate(source_number, start_number, clip(a, 0, 1)),
            **kwargs
        )
