import numpy as np

from manimlib.animation.animation import Animation
from manimlib.mobject.mobject import Group
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import squish_rate_func


class AnimationGroup(Animation):
    CONFIG = {
        # If None, this defaults to the sum of all
        # internal animations
        "run_time": None,
        "rate_functions": linear,
        # If 0, all animations are played at once.
        # If 1, all are played successively.
        # If >0 and <1, they start at lagged times
        # from one and other.
        "lag_ratio": 0,
    }

    def __init__(self, *animations, **kwargs):
        self.animations = animations
        self.group = Group(*[anim.mobject for anim in animations])
        Animation.__init__(self, self.group, **kwargs)
        self.init_run_time()

    def get_all_mobjects(self):
        return self.group

    def init_run_time(self):
        self.build_animations_with_timings()
        self.max_end_time = np.max([
            awt[2] for awt in self.anims_with_timings
        ])
        if self.run_time is None:
            self.run_time = self.max_end_time

    def build_animations_with_timings(self):
        """
        Creates a list of triplets of the form
        (anim, start_time, end_time)
        """
        self.anims_with_timings = []
        curr_time = 0
        for anim in self.animations:
            start_time = curr_time
            end_time = start_time + anim.get_run_time()
            self.anims_with_timings.append(
                (anim, start_time, end_time)
            )
            # Start time of next animation is based on
            # the lag_ratio
            curr_time = interpolate(
                start_time, end_time, self.lag_ratio
            )

    def begin(self):
        for anim in self.animations:
            anim.begin()

    def finish(self):
        for anim in self.animations:
            anim.finish()

    def clean_up_from_scene(self, scene):
        for anim in self.animations:
            anim.clean_up_from_scene(scene)

    def update_mobjects(self, dt):
        for anim in self.animations:
            anim.update_mobjects(dt)

    def interpolate(self, alpha):
        # Note, if the run_time of AnimationGroup has been
        # set to something other than its default, these
        # times might not correspond to actual times,
        # e.g. of the surrounding scene.  Instead they'd
        # be a rescaled version.  But that's okay!
        time = alpha * self.max_end_time
        for anim, start_time, end_time in self.anims_with_timings:
            anim_time = end_time - start_time
            if anim_time == 0:
                sub_alpha = 0
            else:
                sub_alpha = np.clip(
                    (time - start_time) / anim_time,
                    0, 1
                )
            anim.interpolate(sub_alpha)


class Succession(AnimationGroup):
    CONFIG = {
        "lag_ratio": 1,
    }


class LaggedStart(AnimationGroup):
    CONFIG = {
        "lag_ratio": 0.2,
    }


# Variants on mapping an animation over submobjects


# This class is depricated.  One should use OldLaggedStart
# instead, which has different syntax, but more generality
class OldLaggedStart(Animation):
    CONFIG = {
        "run_time": 2,
        "lag_ratio": 0.5,
    }

    def __init__(self, AnimationClass, mobject, arg_creator=None, **kwargs):
        for key in ["rate_func", "run_time"]:
            if key in AnimationClass.CONFIG:
                setattr(self, key, AnimationClass.CONFIG[key])
        digest_config(self, kwargs)
        for key in "rate_func", "run_time", "lag_ratio":
            if key in kwargs:
                kwargs.pop(key)

        if arg_creator is None:
            def arg_creator(mobject):
                return (mobject,)
        self.subanimations = [
            AnimationClass(
                *arg_creator(submob),
                run_time=self.run_time,
                rate_func=squish_rate_func(
                    self.rate_func, beta, beta + self.lag_ratio
                ),
                **kwargs
            )
            for submob, beta in zip(
                mobject,
                np.linspace(0, 1 - self.lag_ratio, len(mobject))
            )
        ]
        Animation.__init__(self, mobject, **kwargs)

    def update(self, alpha):
        for anim in self.subanimations:
            anim.update(alpha)
        return self

    def clean_up_from_scene(self, *args, **kwargs):
        for anim in self.subanimations:
            anim.clean_up_from_scene(*args, **kwargs)


class ApplyToCenters(Animation):
    def __init__(self, AnimationClass, mobjects, **kwargs):
        full_kwargs = AnimationClass.CONFIG
        full_kwargs.update(kwargs)
        full_kwargs["mobject"] = Group(*[
            mob.get_point_mobject()
            for mob in mobjects
        ])
        self.centers_container = AnimationClass(**full_kwargs)
        full_kwargs.pop("mobject")
        Animation.__init__(self, Group(*mobjects), **full_kwargs)
        self.name = str(self) + AnimationClass.__name__

    def interpolate_mobject(self, alpha):
        self.centers_container.interpolate_mobject(alpha)
        center_mobs = self.centers_container.mobject.split()
        mobjects = self.mobject.split()
        for center_mob, mobject in zip(center_mobs, mobjects):
            mobject.shift(
                center_mob.get_center() - mobject.get_center()
            )
