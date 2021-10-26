import numpy as np

from manimlib.utils.bezier import bezier


def linear(t):
    return t


def smooth(t):
    # Zero first and second derivatives at t=0 and t=1.
    # Equivalent to bezier([0, 0, 0, 1, 1, 1])
    s = 1 - t
    return (t**3) * (10 * s * s + 5 * s * t + t * t)


def rush_into(t):
    return 2 * smooth(0.5 * t)


def rush_from(t):
    return 2 * smooth(0.5 * (t + 1)) - 1


def slow_into(t):
    return np.sqrt(1 - (1 - t) * (1 - t))


def double_smooth(t):
    if t < 0.5:
        return 0.5 * smooth(2 * t)
    else:
        return 0.5 * (1 + smooth(2 * t - 1))


def there_and_back(t):
    new_t = 2 * t if t < 0.5 else 2 * (1 - t)
    return smooth(new_t)


def there_and_back_with_pause(t, pause_ratio=1. / 3):
    a = 1. / pause_ratio
    if t < 0.5 - pause_ratio / 2:
        return smooth(a * t)
    elif t < 0.5 + pause_ratio / 2:
        return 1
    else:
        return smooth(a - a * t)


def running_start(t, pull_factor=-0.5):
    return bezier([0, 0, pull_factor, pull_factor, 1, 1, 1])(t)


def not_quite_there(func=smooth, proportion=0.7):
    def result(t):
        return proportion * func(t)
    return result


def wiggle(t, wiggles=2):
    return there_and_back(t) * np.sin(wiggles * np.pi * t)


def squish_rate_func(func, a=0.4, b=0.6):
    def result(t):
        if a == b:
            return a
        elif t < a:
            return func(0)
        elif t > b:
            return func(1)
        else:
            return func((t - a) / (b - a))

    return result

# Stylistically, should this take parameters (with default values)?
# Ultimately, the functionality is entirely subsumed by squish_rate_func,
# but it may be useful to have a nice name for with nice default params for
# "lingering", different from squish_rate_func's default params


def lingering(t):
    return squish_rate_func(lambda t: t, 0, 0.8)(t)


def exponential_decay(t, half_life=0.1):
    # The half-life should be rather small to minimize
    # the cut-off error at the end
    return 1 - np.exp(-t / half_life)
