from __future__ import annotations

import inspect

from manimlib.constants import DEG
from manimlib.constants import RIGHT
from manimlib.mobject.mobject import Mobject
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    import numpy as np

    from manimlib.animation.animation import Animation


def assert_is_mobject_method(method):
    assert inspect.ismethod(method)
    mobject = method.__self__
    assert isinstance(mobject, Mobject)


def always(method, *args, **kwargs):
    """
    Apply a method to a mobject on every update.

    Parameters
    ----------
    method
        Bound method of a Mobject to call on each update.
    *args
        Positional arguments passed to the method on every update.
    **kwargs
        Keyword arguments passed to the method on every update.

    Returns
    -------
    Mobject
        The mobject with the updater added.

    Notes
    -----
    The method must be bound to a Mobject. The updater calls the
    underlying function with the mobject as its first argument.

    Examples
    --------
    >>> always(square.shift, RIGHT)
    """

    assert_is_mobject_method(method)
    mobject = method.__self__
    func = method.__func__
    mobject.add_updater(lambda m: func(m, *args, **kwargs))
    return mobject


def f_always(method, *arg_generators, **kwargs):
    """
    More functional version of always, where instead
    of taking in args, it takes in functions which output
    the relevant arguments.

    Apply a method to a mobject using dynamically generated arguments.

    Parameters
    ----------
    method
        Bound method of a Mobject to call on each update.
    *arg_generators
        Zero-argument callables that generate positional arguments
        whenever the updater runs.
    **kwargs
        Keyword arguments passed unchanged to the method.

    Returns
    -------
    Mobject
        The mobject with the updater added.

    Notes
    -----
    Each argument generator is evaluated on every update, while
    keyword arguments remain fixed.

    Examples
    --------
    >>> f_always(dot.move_to, lambda: tracker.get_value() * RIGHT)
    """

    assert_is_mobject_method(method)
    mobject = method.__self__
    func = method.__func__

    def updater(mob):
        args = [
            arg_generator()
            for arg_generator in arg_generators
        ]
        func(mob, *args, **kwargs)

    mobject.add_updater(updater)
    return mobject


def always_redraw(func: Callable[..., Mobject], *args, **kwargs) -> Mobject:
    """
    Redraw a mobject on every update by recreating it with a function.

    Parameters
    ----------
    func
        Callable that returns a Mobject.
    *args
        Positional arguments passed to func on each redraw.
    **kwargs
        Keyword arguments passed to func on each redraw.

    Returns
    -------
    Mobject
        The initially created mobject, updated to match the
        newly generated mobject on every update.

    Examples
    --------
    >>> always_redraw(lambda: Circle().scale(tracker.get_value()))
    """

    mob = func(*args, **kwargs)
    mob.add_updater(lambda m: mob.become(func(*args, **kwargs)))
    return mob


def always_shift(
    mobject: Mobject,
    direction: np.ndarray = RIGHT,
    rate: float = 0.1
) -> Mobject:
    """
    Continuously shift a mobject in a given direction.

    Parameters
    ----------
    mobject
        The mobject to shift.
    direction
        Direction vector of motion. Defaults to RIGHT.
    rate
        Shift distance per unit of time. Defaults to 0.1.

    Returns
    -------
    Mobject
        The mobject with the updater added.

    Notes
    -----
    Movement depends on the frame time delta (dt), making the
    motion rate independent of frame rate.

    Examples
    --------
    >>> always_shift(square, direction=UP, rate=0.5)
    """

    mobject.add_updater(
        lambda m, dt: m.shift(dt * rate * direction)
    )
    return mobject


def always_rotate(
    mobject: Mobject,
    rate: float = 20 * DEG,
    **kwargs
) -> Mobject:
    """
    Continuously rotate a mobject at a constant angular rate.

    Parameters
    ----------
    mobject
        The mobject to rotate.
    rate
        Angular rotation per unit of time, in radians. Defaults
        to 20 * DEG.
    **kwargs
        Additional keyword arguments passed to ``mobject.rotate``.

    Returns
    -------
    Mobject
        The mobject with the updater added.

    Examples
    --------
    >>> always_rotate(square, rate=45 * DEG)
    """

    mobject.add_updater(
        lambda m, dt: m.rotate(dt * rate, **kwargs)
    )
    return mobject


def turn_animation_into_updater(
    animation: Animation,
    cycle: bool = False,
    **kwargs
) -> Mobject:
    """
    Convert an Animation into a continuously updated mobject.

    The animation's interpolation and update functions are applied
    by an updater attached to its mobject, allowing the animation
    to progress alongside other scene updates.

    Parameters
    ----------
    animation
        The Animation whose behavior will be driven by an updater.
    cycle
        If True, repeat the animation by wrapping its progress back
        to the beginning. If False, stop and remove the updater
        when the animation completes. Defaults to False.
    **kwargs
        Additional keyword arguments passed to
        ``animation.update_rate_info``.

    Returns
    -------
    Mobject
        The animation's mobject, with the updater attached.

    Notes
    -----
    - The animation is initialized with ``begin()``, and its
      ``total_time`` is reset to zero.
    - Each update computes progress from ``total_time / run_time``
      and interpolates the animation accordingly.
    - When ``cycle=False``, progress is clamped to the interval
      [0, 1]. On completion, ``finish()`` is called and the updater
      removes itself.
    - When ``cycle=True``, progress wraps using the modulo
      operation, creating a repeating animation.
    - The updater advances ``total_time`` using the frame's
      time delta (dt).
    - This function returns the original animation mobject rather
      than a separate Animation object.

    Examples
    --------
    Convert an animation into an updater that runs once::

        square = Square()
        anim = square.animate.shift(RIGHT * 2)
        turn_animation_into_updater(anim)

    Make an animation repeat continuously::

        dot = Dot()
        anim = dot.animate.shift(RIGHT * 2)
        turn_animation_into_updater(anim, cycle=True)

    Run the animation alongside other scene activity::

        square = Square()
        turn_animation_into_updater(
            square.animate.rotate(PI),
            cycle=True,
        )
        self.add(square)
        self.wait(5)

    See Also
    --------
    always
        Apply a method to a mobject on every update.
    always_redraw
        Recreate a mobject on every update.
    """

    mobject = animation.mobject
    animation.update_rate_info(**kwargs)
    animation.suspend_mobject_updating = False
    animation.begin()
    animation.total_time = 0

    def update(m, dt):
        run_time = animation.get_run_time()
        time_ratio = animation.total_time / run_time
        if cycle:
            alpha = time_ratio % 1
        else:
            alpha = clip(time_ratio, 0, 1)
            if alpha >= 1:
                animation.finish()
                m.remove_updater(update)
                return
        animation.interpolate(alpha)
        animation.update_reference_mobjects(dt)
        animation.total_time += dt

    mobject.add_updater(update)
    return mobject


def cycle_animation(animation: Animation, **kwargs) -> Mobject:
    """
    Convert an animation into a continuously repeating updater.

    This is a convenience wrapper around
    ``turn_animation_into_updater`` with ``cycle=True``.

    Parameters
    ----------
    animation
        The animation to repeat continuously.
    **kwargs
        Additional keyword arguments passed to
        ``turn_animation_into_updater``.

    Returns
    -------
    Mobject
        The animation's mobject with a repeating updater attached.

    Notes
    -----
    The animation progress wraps back to the beginning after
    reaching its end. The updater remains attached until removed
    or otherwise modified.

    Examples
    --------
    Repeat a rotation animation::

        square = Square()
        cycle_animation(square.animate.rotate(TAU))

    Repeat a shift animation::

        dot = Dot()
        cycle_animation(dot.animate.shift(RIGHT * 2))

    See Also
    --------
    turn_animation_into_updater
        Convert an animation into an updater, optionally cycling.
    """

    return turn_animation_into_updater(
        animation, cycle=True, **kwargs
    )
