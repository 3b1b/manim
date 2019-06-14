import numpy as np

from manimlib.animation.animation import Animation
from manimlib.mobject.mobject import Group
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.rate_functions import linear


DEFAULT_LAGGED_START_LAG_RATIO = 0.05


class AnimationGroup(Animation):
    CONFIG = {
        # If None, this defaults to the sum of all
        # internal animations
        "run_time": None,
        "rate_func": linear,
        # If 0, all animations are played at once.
        # If 1, all are played successively.
        # If >0 and <1, they start at lagged times
        # from one and other.
        "lag_ratio": 0,
        "group": None,
    }

    def __init__(self, *animations, **kwargs):
        digest_config(self, kwargs)
        self.animations = animations
        if self.group is None:
            self.group = Group(*remove_list_redundancies(
                [anim.mobject for anim in animations]
            ))
        Animation.__init__(self, self.group, **kwargs)

    def get_all_mobjects(self):
        return self.group

    def begin(self):
        for anim in self.animations:
            anim.begin()
        self.init_run_time()

    def finish(self):
        for anim in self.animations:
            anim.finish()

    def clean_up_from_scene(self, scene):
        for anim in self.animations:
            anim.clean_up_from_scene(scene)

    def update_mobjects(self, dt):
        for anim in self.animations:
            anim.update_mobjects(dt)

    def init_run_time(self):
        self.build_animations_with_timings()
        if self.anims_with_timings:
            self.max_end_time = np.max([
                awt[2] for awt in self.anims_with_timings
            ])
        else:
            self.max_end_time = 0
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

    def begin(self):
        assert(len(self.animations) > 0)
        self.init_run_time()
        self.active_animation = self.animations[0]
        self.active_animation.begin()

    def finish(self):
        self.active_animation.finish()

    def update_mobjects(self, dt):
        self.active_animation.update_mobjects(dt)

    def interpolate(self, alpha):
        index, subalpha = integer_interpolate(
            0, len(self.animations), alpha
        )
        animation = self.animations[index]
        if animation is not self.active_animation:
            self.active_animation.finish()
            animation.begin()
            self.active_animation = animation
        animation.interpolate(subalpha)


class LaggedStart(AnimationGroup):
    CONFIG = {
        "lag_ratio": DEFAULT_LAGGED_START_LAG_RATIO,
    }


class LaggedStartMap(LaggedStart):
    CONFIG = {
        "run_time": 2,
    }

    def __init__(self, AnimationClass, mobject, arg_creator=None, **kwargs):
        args_list = []
        for submob in mobject:
            if arg_creator:
                args_list.append(arg_creator(submob))
            else:
                args_list.append((submob,))
        anim_kwargs = dict(kwargs)
        if "lag_ratio" in anim_kwargs:
            anim_kwargs.pop("lag_ratio")
        animations = [
            AnimationClass(*args, **anim_kwargs)
            for args in args_list
        ]
        super().__init__(*animations, **kwargs)
