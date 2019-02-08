from copy import deepcopy

import numpy as np

from manimlib.constants import DEFAULT_ANIMATION_RUN_TIME
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import smooth


class Animation(object):
    CONFIG = {
        "run_time": DEFAULT_ANIMATION_RUN_TIME,
        "rate_func": smooth,
        "name": None,
        # Does this animation add or remove a mobject form the screen
        "remover": False,
        # TODO, replace this with a single lag parameter

        # If 0, the animation is applied to all submobjects
        # at the same time
        # If 1, it is applied to each successively.
        # If 0 < lag_ratio < 1, its applied to each
        # with lagged start times
        "lag_ratio": 0,
        # TODO, remove anything with lag_factor
        "lag_factor": 2,
    }

    def __init__(self, mobject, **kwargs):
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs)
        self.mobject = mobject

    def begin(self):
        mobject = self.mobject
        # Keep track of where it started
        self.starting_mobject = mobject.copy()
        # All calls to self.mobject's internal updaters
        # during the animation, either from this Animation
        # or from the surrounding scene, should do nothing.
        # It is, however, okay and desirable to call
        # the internal updaters of self.starting_mobject,
        # or any others among self.get_all_mobjects()
        mobject.suspend_updating()
        self.interpolate(0)

    def finish(self):
        self.interpolate(1)
        self.mobject.resume_updating()

    def clean_up_from_scene(self, scene):
        if self.is_remover():
            scene.remove(self.mobject)

    def __str__(self):
        if self.name:
            return self.name
        return self.__class__.__name__ + str(self.mobject)

    def copy(self):
        return deepcopy(self)

    def update_config(self, **kwargs):
        digest_config(self, kwargs)
        return self

    def update_mobjects(self, dt):
        """
        Updates things like starting_mobject, and (for
        Transforms) target_mobject.  Note, since typically
        (always?) self.mobject will have its updating
        suspended during the animation, this will do
        nothing to self.mobject.
        """
        for mob in self.get_all_mobjects():
            mob.update(dt)

    def interpolate(self, alpha):
        alpha = np.clip(alpha, 0, 1)
        self.interpolate_mobject(self.rate_func(alpha))

    def update(self, alpha):
        """
        This method shouldn't exist, but it's here to
        keep many old scenes from breaking
        """
        self.interpolate(alpha)

    def interpolate_mobject(self, alpha):
        families = self.get_all_families_zipped()
        for i, mobs in enumerate(families):
            sub_alpha = self.get_sub_alpha(alpha, i, len(families))
            self.interpolate_submobject(*mobs, sub_alpha)

    def interpolate_submobject(self, submobject, starting_sumobject, alpha):
        # Typically ipmlemented by subclass
        pass

    def get_sub_alpha(self, alpha, index, num_submobjects):
        # TODO, make this more understanable, and/or combine
        # its functionality with AnimationGroup's method
        # build_animations_with_timings
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        return np.clip(
            (value - lower),
            0, 1,
        )

    def get_all_mobjects(self):
        """
        Ordering must match the ording of arguments to interpolate_submobject
        """
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self):
        return list(zip(*map(
            Mobject.family_members_with_points,
            self.get_all_mobjects()
        )))

    def set_run_time(self, run_time):
        self.run_time = run_time
        return self

    def get_run_time(self):
        return self.run_time

    def set_rate_func(self, rate_func):
        self.rate_func = rate_func
        return self

    def get_rate_func(self):
        return self.rate_func

    def set_name(self, name):
        self.name = name
        return self

    def is_remover(self):
        return self.remover
