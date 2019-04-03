import inspect
import numpy as np

from manimlib.constants import DEGREES
from manimlib.constants import RIGHT
from manimlib.mobject.mobject import Mobject


def assert_is_mobject_method(method):
    assert(inspect.ismethod(method))
    mobject = method.__self__
    assert(isinstance(mobject, Mobject))


def always(method, *args, **kwargs):
    assert_is_mobject_method(method)
    mobject = method.__self__
    func = method.__func__
    mobject.add_updater(lambda m: func(m, *args, **kwargs))
    return mobject


def f_always(method, *arg_generators, **kwargs):
    """
    More functional version of always, where instead
    of taking in args, it takes in functions which ouput
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


def always_redraw(func):
    mob = func()
    mob.add_updater(lambda m: mob.become(func()))
    return mob


def always_shift(mobject, direction=RIGHT, rate=0.1):
    mobject.add_updater(
        lambda m, dt: m.shift(dt * rate * direction)
    )
    return mobject


def always_rotate(mobject, rate=20 * DEGREES, **kwargs):
    mobject.add_updater(
        lambda m, dt: m.rotate(dt * rate, **kwargs)
    )
    return mobject


def turn_animation_into_updater(animation, cycle=False, **kwargs):
    """
    Add an updater to the animation's mobject which applies
    the interpolation and update functions of the animation

    If cycle is True, this repeats over and over.  Otherwise,
    the updater will be popped uplon completion
    """
    mobject = animation.mobject
    animation.update_config(**kwargs)
    animation.suspend_mobject_updating = False
    animation.begin()
    animation.total_time = 0

    def update(m, dt):
        run_time = animation.get_run_time()
        time_ratio = animation.total_time / run_time
        if cycle:
            alpha = time_ratio % 1
        else:
            alpha = np.clip(time_ratio, 0, 1)
            if alpha >= 1:
                animation.finish()
                m.remove_updater(update)
                return
        animation.interpolate(alpha)
        animation.update_mobjects(dt)
        animation.total_time += dt

    mobject.add_updater(update)
    return mobject


def cycle_animation(animation, **kwargs):
    return turn_animation_into_updater(
        animation, cycle=True, **kwargs
    )
