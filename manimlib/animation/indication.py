from functools import reduce

import numpy as np

from manimlib.constants import *
from manimlib.animation.animation import Animation
from manimlib.animation.movement import Homotopy
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.composition import Succession
from manimlib.animation.creation import ShowCreation
from manimlib.animation.creation import ShowPartial
from manimlib.animation.creation import FadeOut
from manimlib.animation.transform import Transform
from manimlib.animation.update import UpdateFromAlphaFunc
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Dot
from manimlib.mobject.shape_matchers import SurroundingRectangle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.geometry import Line
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import smooth
from manimlib.utils.rate_functions import squish_rate_func
from manimlib.utils.rate_functions import there_and_back
from manimlib.utils.rate_functions import wiggle


class FocusOn(Transform):
    CONFIG = {
        "opacity": 0.2,
        "color": GREY,
        "run_time": 2,
        "remover": True,
    }

    def __init__(self, mobject_or_point, **kwargs):
        digest_config(self, kwargs)
        big_dot = Dot(
            radius=FRAME_X_RADIUS + FRAME_Y_RADIUS,
            stroke_width=0,
            fill_color=self.color,
            fill_opacity=0,
        )
        little_dot = Dot(radius=0)
        little_dot.set_fill(self.color, opacity=self.opacity)
        little_dot.move_to(mobject_or_point)

        Transform.__init__(self, big_dot, little_dot, **kwargs)


class Indicate(Transform):
    CONFIG = {
        "rate_func": there_and_back,
        "scale_factor": 1.2,
        "color": YELLOW,
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        target = mobject.copy()
        target.scale_in_place(self.scale_factor)
        target.set_color(self.color)
        Transform.__init__(self, mobject, target, **kwargs)


class Flash(AnimationGroup):
    CONFIG = {
        "line_length": 0.2,
        "num_lines": 12,
        "flash_radius": 0.3,
        "line_stroke_width": 3,
    }

    def __init__(self, point, color=YELLOW, **kwargs):
        digest_config(self, kwargs)
        lines = VGroup()
        for angle in np.arange(0, TAU, TAU / self.num_lines):
            line = Line(ORIGIN, self.line_length * RIGHT)
            line.shift((self.flash_radius - self.line_length) * RIGHT)
            line.rotate(angle, about_point=ORIGIN)
            lines.add(line)
        lines.move_to(point)
        lines.set_color(color)
        lines.set_stroke(width=3)
        line_anims = [
            ShowCreationThenDestruction(
                line, rate_func=squish_rate_func(smooth, 0, 0.5)
            )
            for line in lines
        ]
        fade_anims = [
            UpdateFromAlphaFunc(
                line, lambda m, a: m.set_stroke(
                    width=self.line_stroke_width * (1 - a)
                ),
                rate_func=squish_rate_func(smooth, 0, 0.75)
            )
            for line in lines
        ]

        AnimationGroup.__init__(
            self, *line_anims + fade_anims, **kwargs
        )


class CircleIndicate(Indicate):
    CONFIG = {
        "rate_func": squish_rate_func(there_and_back, 0, 0.8),
        "remover": True
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        circle = Circle(color=self.color, **kwargs)
        circle.surround(mobject)
        Indicate.__init__(self, circle, **kwargs)


class ShowPassingFlash(ShowPartial):
    CONFIG = {
        "time_width": 0.1,
        "remover": True,
    }

    def get_bounds(self, alpha):
        alpha *= (1 + self.time_width)
        alpha -= self.time_width / 2.0
        lower = max(0, alpha - self.time_width / 2.0)
        upper = min(1, alpha + self.time_width / 2.0)
        return (lower, upper)

    def clean_up(self, *args, **kwargs):
        ShowPartial.clean_up(self, *args, **kwargs)
        for submob, start_submob in self.get_all_families_zipped():
            submob.pointwise_become_partial(start_submob, 0, 1)


class ShowCreationThenDestruction(ShowPassingFlash):
    CONFIG = {
        "time_width": 2.0,
        "run_time": 1,
    }


class AnimationOnSurroundingRectangle(AnimationGroup):
    CONFIG = {
        "surrounding_rectangle_config": {},
        # Function which takes in a rectangle, and spits
        # out some animation.  Could be some animation class,
        # could be something more
        "rect_to_animation": Animation
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        rect = SurroundingRectangle(
            mobject, **self.surrounding_rectangle_config
        )
        if "surrounding_rectangle_config" in kwargs:
            kwargs.pop("surrounding_rectangle_config")
        AnimationGroup.__init__(self, self.rect_to_animation(rect, **kwargs))


class ShowPassingFlashAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_to_animation": ShowPassingFlash
    }


class ShowCreationThenDestructionAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_to_animation": ShowCreationThenDestruction
    }


class CircleThenFadeAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_to_animation": lambda rect: Succession(
            ShowCreation, rect,
            FadeOut, rect,
        )
    }


class ApplyWave(Homotopy):
    CONFIG = {
        "direction": UP,
        "amplitude": 0.2,
        "run_time": 1,
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs, locals())
        left_x = mobject.get_left()[0]
        right_x = mobject.get_right()[0]
        vect = self.amplitude * self.direction

        def homotopy(x, y, z, t):
            alpha = (x - left_x) / (right_x - left_x)
            # lf = self.lag_factor
            power = np.exp(2.0 * (alpha - 0.5))
            nudge = there_and_back(t**power)
            return np.array([x, y, z]) + nudge * vect
        Homotopy.__init__(self, homotopy, mobject, **kwargs)


class WiggleOutThenIn(Animation):
    CONFIG = {
        "scale_value": 1.1,
        "rotation_angle": 0.01 * TAU,
        "n_wiggles": 6,
        "run_time": 2,
        "scale_about_point": None,
        "rotate_about_point": None,
    }

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        if self.scale_about_point is None:
            self.scale_about_point = mobject.get_center()
        if self.rotate_about_point is None:
            self.rotate_about_point = mobject.get_center()
        Animation.__init__(self, mobject, **kwargs)

    def update_submobject(self, submobject, starting_sumobject, alpha):
        submobject.points[:, :] = starting_sumobject.points
        submobject.scale(
            interpolate(1, self.scale_value, there_and_back(alpha)),
            about_point=self.scale_about_point
        )
        submobject.rotate(
            wiggle(alpha, self.n_wiggles) * self.rotation_angle,
            about_point=self.rotate_about_point
        )


class Vibrate(Animation):
    CONFIG = {
        "spatial_period": 6,
        "temporal_period": 1,
        "overtones": 4,
        "amplitude": 0.5,
        "radius": FRAME_X_RADIUS / 2,
        "run_time": 3.0,
        "rate_func": None
    }

    def __init__(self, mobject=None, **kwargs):
        if mobject is None:
            mobject = Line(3 * LEFT, 3 * RIGHT)
        Animation.__init__(self, mobject, **kwargs)

    def wave_function(self, x, t):
        return sum([
            reduce(op.mul, [
                self.amplitude / (k**2),  # Amplitude
                np.sin(2 * np.pi * (k**1.5) * t / \
                       self.temporal_period),  # Frequency
                # Number of waves
                np.sin(2 * np.pi * k * x / self.spatial_period)
            ])
            for k in range(1, self.overtones + 1)
        ])

    def update_mobject(self, alpha):
        time = alpha * self.run_time
        families = list(map(
            Mobject.get_family,
            [self.mobject, self.starting_mobject]
        ))
        for mob, start in zip(*families):
            mob.points = np.apply_along_axis(
                lambda x_y_z: (
                    x_y_z[0], x_y_z[1] + self.wave_function(x_y_z[0], time), x_y_z[2]),
                1, start.points
            )


class TurnInsideOut(Transform):
    CONFIG = {
        "path_arc": TAU / 4,
    }

    def __init__(self, mobject, **kwargs):
        mob_copy = mobject.copy()
        mob_copy.reverse_points()
        Transform.__init__(self, mobject, mob_copy, **kwargs)
