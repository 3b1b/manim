from copy import deepcopy

import numpy as np

from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import smooth

#Old packages
from manimlib.constants import *


DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0


class Animation(object):
    CONFIG = {
        "run_time": DEFAULT_ANIMATION_RUN_TIME,
        "rate_func": smooth,
        "name": None,
        # Does this animation add or remove a mobject form the screen
        "remover": False,
        # If 0, the animation is applied to all submobjects
        # at the same time
        # If 1, it is applied to each successively.
        # If 0 < lag_ratio < 1, its applied to each
        # with lagged start times
        "lag_ratio": DEFAULT_ANIMATION_LAG_RATIO,
        "suspend_mobject_updating": True,
        "submobject_mode": "None",
        "lag_factor": 2,
    }

    def __init__(self, mobject, **kwargs):
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs)
        self.mobject = mobject

    def __str__(self):
        if self.name:
            return self.name
        return self.__class__.__name__ + str(self.mobject)

    def begin(self):
        # This is called right as an animation is being
        # played.  As much initialization as possible,
        # especially any mobject copying, should live in
        # this method
        self.starting_mobject = self.create_starting_mobject()
        if self.suspend_mobject_updating:
            # All calls to self.mobject's internal updaters
            # during the animation, either from this Animation
            # or from the surrounding scene, should do nothing.
            # It is, however, okay and desirable to call
            # the internal updaters of self.starting_mobject,
            # or any others among self.get_all_mobjects()
            self.mobject.suspend_updating()
        self.interpolate(0)

    def finish(self):
        self.interpolate(1)
        if self.suspend_mobject_updating:
            self.mobject.resume_updating()

    def clean_up_from_scene(self, scene):
        if self.is_remover():
            scene.remove(self.mobject)

    def create_starting_mobject(self):
        # Keep track of where the mobject starts
        return self.mobject.copy()

    def get_all_mobjects(self):
        """
        Ordering must match the ording of arguments to interpolate_submobject
        """
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self):
        return zip(*[
            mob.family_members_with_points()
            for mob in self.get_all_mobjects()
        ])

    def update_mobjects(self, dt):
        """
        Updates things like starting_mobject, and (for
        Transforms) target_mobject.  Note, since typically
        (always?) self.mobject will have its updating
        suspended during the animation, this will do
        nothing to self.mobject.
        """
        for mob in self.get_all_mobjects_to_update():
            mob.update(dt)

    def get_all_mobjects_to_update(self):
        # The surrounding scene typically handles
        # updating of self.mobject.  Besides, in
        # most cases its updating is suspended anyway
        return list(filter(
            lambda m: m is not self.mobject,
            self.get_all_mobjects()
        ))

    def copy(self):
        return deepcopy(self)

    def update_config(self, **kwargs):
        digest_config(self, kwargs)
        return self

    # Methods for interpolation, the mean of an Animation
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
        families = list(self.get_all_families_zipped())
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
        return np.clip((value - lower), 0, 1)

    # Getters and setters
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

#Old classes:
def instantiate(obj):
    """
    Useful so that classes or instance of those classes can be
    included in configuration, which can prevent defaults from
    getting created during compilation/importing
    """
    return obj() if isinstance(obj, type) else obj

class OldAnimation(object):
    CONFIG = {
        "run_time": DEFAULT_ANIMATION_RUN_TIME,
        "rate_func": smooth,
        "name": None,
        # Does this animation add or remove a mobject form the screen
        "remover": False,
        # Options are lagged_start, smoothed_lagged_start,
        # one_at_a_time, all_at_once
        "submobject_mode": "all_at_once",
        "lag_factor": 2,
        # Used by EmptyAnimation to announce itself ignorable
        # in Successions and AnimationGroups
        "empty": False
    }

    def __init__(self, mobject, **kwargs):
        mobject = instantiate(mobject)
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs, locals())
        # Make sure it's all up to date
        mobject.update()
        # Keep track of where it started
        self.starting_mobject = self.mobject.copy()
        if self.rate_func is None:
            self.rate_func = (lambda x: x)
        if self.name is None:
            self.name = self.__class__.__name__ + str(self.mobject)
        self.all_families_zipped = self.get_all_families_zipped()
        self.update(0)

    def update_config(self, **kwargs):
        digest_config(self, kwargs)
        if "rate_func" in kwargs and kwargs["rate_func"] is None:
            self.rate_func = (lambda x: x)
        return self

    def __str__(self):
        return self.name

    def copy(self):
        return deepcopy(self)

    def update(self, alpha):
        alpha = np.clip(alpha, 0, 1)
        self.update_mobject(self.rate_func(alpha))

    def update_mobject(self, alpha):
        families = self.all_families_zipped
        for i, mobs in enumerate(families):
            sub_alpha = self.get_sub_alpha(alpha, i, len(families))
            self.update_submobject(*list(mobs) + [sub_alpha])
        return self

    def update_submobject(self, submobject, starting_sumobject, alpha):
        # Typically ipmlemented by subclass
        pass

    def get_all_mobjects(self):
        """
        Ordering must match the ording of arguments to update_submobject
        """
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self):
        return list(zip(*list(map(
            Mobject.family_members_with_points,
            self.get_all_mobjects()
        ))))

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

    def filter_out(self, *filter_functions):
        self.filter_functions += filter_functions
        return self

    def set_run_time(self, time):
        self.run_time = time
        return self

    def get_run_time(self):
        return self.run_time

    def set_rate_func(self, rate_func):
        if rate_func is None:
            def rate_func(x):
                return x
        self.rate_func = rate_func
        return self

    def get_rate_func(self):
        return self.rate_func

    def set_name(self, name):
        self.name = name
        return self

    def is_remover(self):
        return self.remover

    def clean_up(self, surrounding_scene=None):
        self.update(1)
        if surrounding_scene is not None:
            if self.is_remover():
                surrounding_scene.remove(self.mobject)
        return self

#New Classes
