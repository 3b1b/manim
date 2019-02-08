from copy import deepcopy

import numpy as np

from manimlib.constants import *
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
        "submobject_mode": "all_at_once",
        "lag_factor": 2,
        # Used by EmptyAnimation to announce itself ignorable
        # in Successions and AnimationGroups
        "empty": False
    }

    def __init__(self, mobject, **kwargs):
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs)
        self.mobject = mobject

    def begin(self):
        mobject = self.mobject
        # Keep track of where it started
        self.starting_mobject = mobject.copy()
        # All calls to mobject's internal updaters
        # during the animation, either from this Animation
        # or from the surrounding scene, should do nothing.
        # It is, however, okay and desirable to call
        # self.starting_mobject's internal updaters
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
        if self.submobject_mode in ["lagged_start", "smoothed_lagged_start"]:
            prop = float(index) / num_submobjects
            if self.submobject_mode is "smoothed_lagged_start":
                prop = smooth(prop)
            lf = self.lag_factor
            return np.clip(lf * alpha - (lf - 1) * prop, 0, 1)
        elif self.submobject_mode == "one_at_a_time":
            lower = float(index) / num_submobjects
            upper = float(index + 1) / num_submobjects
            return np.clip((alpha - lower) / (upper - lower), 0, 1)
        elif self.submobject_mode == "all_at_once":
            return alpha
        raise Exception("Invalid submobject mode")

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
