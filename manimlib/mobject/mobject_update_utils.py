from __future__ import annotations

import inspect

from manimlib.constants import DEGREES
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
    mob = func(*args, **kwargs)
    mob.add_updater(lambda m: mob.become(func(*args, **kwargs)))
    return mob


def always_shift(
    mobject: Mobject,
    direction: np.ndarray = RIGHT,
    rate: float = 0.1
) -> Mobject:
    mobject.add_updater(
        lambda m, dt: m.shift(dt * rate * direction)
    )
    return mobject


def always_rotate(
    mobject: Mobject,
    rate: float = 20 * DEGREES,
    **kwargs
) -> Mobject:
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
    Add an updater to the animation's mobject which applies
    the interpolation and update functions of the animation

    If cycle is True, this repeats over and over.  Otherwise,
    the updater will be popped uplon completion
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
        animation.update_mobjects(dt)
        animation.total_time += dt

    mobject.add_updater(update)
    return mobject


def cycle_animation(animation: Animation, **kwargs) -> Mobject:
    return turn_animation_into_updater(
        animation, cycle=True, **kwargs
    )
