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
    """
    Animate a DecimalNumber from its current value to a target value.

    ChangeDecimalToValue is a subclass of ChangingDecimal that provides a
    convenient way to animate a DecimalNumber between two numerical values.
    Instead of requiring the user to define a custom update function, it
    uses the interpolate function to calculate intermediate values between
    the number displayed initially and the specified target.

    The starting value is read from decimal_mob.number when the animation
    is constructed. The target value and the animation's progress determine
    the intermediate values displayed throughout the animation.

    Parameters
    ----------
    decimal_mob : DecimalNumber
        The DecimalNumber object whose displayed value will be animated.
        Its current numerical value is obtained from decimal_mob.number.

    target_number : float or complex
        The target numerical value toward which the displayed number
        interpolates. The annotation permits either a real floating-point
        value or a complex number.

    **kwargs
        Additional keyword arguments forwarded to ChangingDecimal. These
        may include run_time, rate_func, suspend_mobject_updating, and
        other supported animation configuration options.

    Attributes
    ----------
    start_number
        A local variable captured by the interpolation lambda. It stores
        the DecimalNumber's value at construction time.

    target_number
        The target value used by the interpolation lambda.

    Inherited Attributes
    --------------------
    number_update_func
        The function created by this class to interpolate between the
        starting value and target value.

    mobject
        The DecimalNumber being animated, inherited from ChangingDecimal.

    How It Works
    ------------
    1. The constructor reads decimal_mob.number and stores it in
       start_number.
    2. It creates a lambda function that calls interpolate() with
       start_number, target_number, and the current progress value.
    3. This function is passed to the ChangingDecimal constructor.
    4. During animation, ChangingDecimal calculates time-adjusted progress
       and evaluates the interpolation function.
    5. The resulting value is passed to DecimalNumber.set_value() by the
       inherited interpolation implementation.

    Conceptually, the numerical value is calculated as:

        value = interpolate(start_number, target_number, alpha)

    For ordinary real-valued endpoints, linear interpolation typically
    produces the starting value at alpha = 0 and the target value at
    alpha = 1.

    Examples
    --------
    Example 1: Increase a Number
    ----------------------------
    Animate a DecimalNumber from 0 to 100.

        from manimlib import *

        number = DecimalNumber(0)

        self.add(number)
        self.play(
            ChangeDecimalToValue(
                number,
                100,
                run_time=3
            )
        )

    Example 2: Decrease a Number
    ----------------------------
    Animate a DecimalNumber from 50 to 10.

        number = DecimalNumber(50)

        self.add(number)
        self.play(
            ChangeDecimalToValue(
                number,
                10,
                run_time=2
            )
        )

    Example 3: Animate a DecimalNumber Beside a Label
    -------------------------------------------------
    A label can identify the quantity being displayed.

        from manimlib import *

        label = Text("Distance:")
        distance = DecimalNumber(0, num_decimal_places=2)

        display = VGroup(label, distance).arrange(RIGHT)
        self.add(display)

        self.play(
            ChangeDecimalToValue(
                distance,
                25.5,
                run_time=4
            )
        )

    Example 4: Use a Nonlinear Rate Function
    ----------------------------------------
    A rate function can alter how quickly the animation progresses
    between the starting and target values.

        number = DecimalNumber(0)

        self.add(number)
        self.play(
            ChangeDecimalToValue(
                number,
                1,
                rate_func=smooth,
                run_time=3
            )
        )

    The rate function changes the progress supplied to the interpolation
    process, producing a nonlinear progression over time.

    Notes
    -----
    - The starting value is captured when the constructor runs. It is not
      dynamically re-read from decimal_mob.number during each frame.
    - The interpolation function is inherited through ChangingDecimal's
      number_update_func mechanism.
    - The actual progression depends on the implementation of interpolate()
      and the animation's time-adjusted alpha.
    - DecimalNumber controls formatting, including decimal places and
      other display options.
    - Although target_number is annotated as float or complex, whether a
      complex value can be displayed meaningfully depends on the behavior
      of interpolate() and DecimalNumber.set_value() in the specific
      ManimGL version.
    - This class does not independently implement interpolate_mobject();
      it uses the implementation inherited from ChangingDecimal.

    See Also
    --------
    ChangingDecimal
    DecimalNumber
    interpolate
    Animation
    """

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
    """
    Animate a DecimalNumber from a specified source value to its current value.

    CountInFrom is a subclass of ChangingDecimal that animates a DecimalNumber
    from a given source_number to the value the DecimalNumber holds when the
    animation is constructed.

    Unlike ChangeDecimalToValue, which captures the current value as the
    starting point and animates toward a target, CountInFrom captures the
    current value as the destination and interpolates from the supplied
    source value.

    The interpolation progress is clipped to the interval [0, 1], ensuring
    that the value passed to interpolate() remains within the intended
    progress range.

    Parameters
    ----------
    decimal_mob : DecimalNumber
        The DecimalNumber object whose displayed value will be animated.
        Its current value is obtained using decimal_mob.get_value() and
        becomes the destination value.

    source_number : float or complex, optional
        The numerical value from which the animation begins. Defaults to 0.

    **kwargs
        Additional keyword arguments forwarded to ChangingDecimal, such as
        run_time, rate_func, suspend_mobject_updating, and other supported
        animation configuration options.

    Attributes
    ----------
    source_number
        The source value captured by the interpolation lambda.

    start_number
        A local variable storing the DecimalNumber's value at construction
        time. Despite its name, this value is the destination of the
        interpolation, not the source.

    Inherited Attributes
    --------------------
    number_update_func
        The function used by ChangingDecimal to calculate the displayed
        value at each interpolation step.

    mobject
        The DecimalNumber being animated.

    How It Works
    ------------
    1. The constructor reads the current value using decimal_mob.get_value().
    2. This value is stored in start_number and serves as the destination.
    3. A lambda function clips the incoming progress a to the interval
       from 0 to 1.
    4. The clipped progress is passed to interpolate(), together with
       source_number and start_number.
    5. The resulting value is passed through ChangingDecimal's animation
       logic and displayed using DecimalNumber.set_value().

    Conceptually, the displayed value is:

        value = interpolate(
            source_number,
            start_number,
            clip(alpha, 0, 1)
        )

    At progress 0, the value corresponds to source_number. At progress 1,
    it corresponds to the DecimalNumber's captured value.

    Examples
    --------
    Example 1: Count Up from Zero
    -----------------------------
    Animate a DecimalNumber from zero to its current value.

        from manimlib import *

        number = DecimalNumber(100)

        self.add(number)
        self.play(
            CountInFrom(
                number,
                source_number=0,
                run_time=3
            )
        )

    The displayed value progresses from 0 toward 100. Note that the
    DecimalNumber initially contains 100 before the animation begins.

    Example 2: Count Up from a Custom Starting Value
    ------------------------------------------------
    The source value does not have to be zero.

        number = DecimalNumber(80)

        self.add(number)
        self.play(
            CountInFrom(
                number,
                source_number=20,
                run_time=2
            )
        )

    The value interpolates from 20 to the captured value of 80.

    Example 3: Count Down to the Existing Value
    -------------------------------------------
    The source value can also be greater than the destination.

        number = DecimalNumber(25)

        self.add(number)
        self.play(
            CountInFrom(
                number,
                source_number=100,
                run_time=3
            )
        )

    The displayed value progresses from 100 down to 25.

    Example 4: Use a Nonlinear Rate Function
    ----------------------------------------
    The animation can use a nonlinear rate function inherited from
    ChangingDecimal and Animation.

        number = DecimalNumber(10)

        self.add(number)
        self.play(
            CountInFrom(
                number,
                source_number=0,
                rate_func=smooth,
                run_time=3
            )
        )

    The smooth rate function changes the timing of the interpolation.

    Notes
    -----
    - The destination value is captured once during initialization.
    - The source value defaults to zero.
    - clip(a, 0, 1) restricts the progress supplied to interpolate() to
      the interval from 0 to 1.
    - The animation uses the interpolation and display-update behavior
      inherited from ChangingDecimal.
    - DecimalNumber formatting settings determine how the interpolated
      values are displayed.
    - Although source_number is annotated as float or complex, successful
      complex-number animation depends on the behavior of interpolate()
      and DecimalNumber.set_value() in the installed ManimGL version.
    - The original DecimalNumber may display its destination value before
      the animation starts; the first interpolation update establishes the
      value calculated from the source and clipped progress.

    See Also
    --------
    ChangingDecimal
    ChangeDecimalToValue
    DecimalNumber
    interpolate
    clip
    """

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
