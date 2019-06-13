import numpy as np

from manimlib.animation.animation import Animation
from manimlib.mobject.mobject import Group
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.rate_functions import linear


DEFAULT_LAGGED_START_LAG_RATIO = 0.05

#Old packages:
from manimlib.constants import *
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.rate_functions import squish_rate_func
from manimlib.animation.animation import OldAnimation
import warnings


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

#Old classes --------------------------------------------

class OldEmptyAnimation(OldAnimation):
    CONFIG = {
        "run_time": 0,
        "empty": True
    }

    def __init__(self, *args, **kwargs):
        return OldAnimation.__init__(self, Group(), *args, **kwargs)


class OldSuccession(OldAnimation):
    CONFIG = {
        "rate_func": None,
    }

    def __init__(self, *args, **kwargs):
        """
        Each arg will either be an animation, or an animation class
        followed by its arguments (and potentially a dict for
        configuration).
        For example,
        Succession(
            ShowCreation(circle),
            Transform, circle, square,
            Transform, circle, triangle,
            ApplyMethod, circle.shift, 2*UP, {"run_time" : 2},
        )
        """
        animations = []
        state = {
            "animations": animations,
            "curr_class": None,
            "curr_class_args": [],
            "curr_class_config": {},
        }

        def invoke_curr_class(state):
            if state["curr_class"] is None:
                return
            anim = state["curr_class"](
                *state["curr_class_args"],
                **state["curr_class_config"]
            )
            state["animations"].append(anim)
            anim.update(1)
            state["curr_class"] = None
            state["curr_class_args"] = []
            state["curr_class_config"] = {}

        for arg in args:
            if isinstance(arg, OldAnimation):
                animations.append(arg)
                arg.update(1)
                invoke_curr_class(state)
            elif isinstance(arg, type) and issubclass(arg, Animation):
                invoke_curr_class(state)
                state["curr_class"] = arg
            elif isinstance(arg, dict):
                state["curr_class_config"] = arg
            else:
                state["curr_class_args"].append(arg)
        invoke_curr_class(state)
        for anim in animations:
            anim.update(0)

        animations = [x for x in animations if not(x.empty)]

        self.run_times = [anim.run_time for anim in animations]
        if "run_time" in kwargs:
            run_time = kwargs.pop("run_time")
            warnings.warn(
                "Succession doesn't currently support explicit run_time.")
        run_time = sum(self.run_times)
        self.num_anims = len(animations)
        if self.num_anims == 0:
            self.empty = True
        self.animations = animations
        # Have to keep track of this run_time, because Scene.play
        # might very well mess with it.
        self.original_run_time = run_time

        # critical_alphas[i] is the start alpha of self.animations[i]
        # critical_alphas[i + 1] is the end alpha of self.animations[i]
        critical_times = np.concatenate(([0], np.cumsum(self.run_times)))
        self.critical_alphas = [np.true_divide(
            x, run_time) for x in critical_times] if self.num_anims > 0 else [0.0]

        # self.scene_mobjects_at_time[i] is the scene's mobjects at start of self.animations[i]
        # self.scene_mobjects_at_time[i + 1] is the scene mobjects at end of self.animations[i]
        self.scene_mobjects_at_time = [None for i in range(self.num_anims + 1)]
        self.scene_mobjects_at_time[0] = Group()
        for i in range(self.num_anims):
            self.scene_mobjects_at_time[i + 1] = self.scene_mobjects_at_time[i].copy()
            self.animations[i].clean_up(self.scene_mobjects_at_time[i + 1])

        self.current_alpha = 0
        # If self.num_anims == 0, this is an invalid index, but so it goes
        self.current_anim_index = 0
        if self.num_anims > 0:
            self.mobject = self.scene_mobjects_at_time[0]
            self.mobject.add(self.animations[0].mobject)
        else:
            self.mobject = Group()

        OldAnimation.__init__(self, self.mobject, run_time=run_time, **kwargs)

    # Beware: This does NOT take care of calling update(0) on the subanimation.
    # This was important to avoid a pernicious possibility in which subanimations were called
    # with update twice, which could in turn call a sub-Succession with update four times,
    # continuing exponentially.
    def jump_to_start_of_anim(self, index):
        if index != self.current_anim_index:
            # Should probably have a cleaner "remove_all" method...
            self.mobject.remove(*self.mobject.submobjects)
            self.mobject.add(*self.scene_mobjects_at_time[index].submobjects)
            self.mobject.add(self.animations[index].mobject)

        for i in range(index):
            self.animations[i].update(1)

        self.current_anim_index = index
        self.current_alpha = self.critical_alphas[index]

    def update_mobject(self, alpha):
        if self.num_anims == 0:
            # This probably doesn't matter for anything, but just in case,
            # we want it in the future, we set current_alpha even in this case
            self.current_alpha = alpha
            return

        gt_alpha_iter = iter(filter(
            lambda i: self.critical_alphas[i + 1] >= alpha,
            range(self.num_anims)
        ))
        i = next(gt_alpha_iter, None)
        if i is None:
            # In this case, we assume what is happening is that alpha is 1.0,
            # but that rounding error is causing us to overshoot the end of
            # self.critical_alphas (which is also 1.0)
            if not abs(alpha - 1) < 0.001:
                warnings.warn(
                    "Rounding error not near alpha=1 in Succession.update_mobject,"
                    "instead alpha = %f" % alpha
                )
                print(self.critical_alphas, alpha)
            i = self.num_anims - 1

        # At this point, we should have self.critical_alphas[i] <= alpha <= self.critical_alphas[i +1]

        self.jump_to_start_of_anim(i)
        sub_alpha = inverse_interpolate(
            self.critical_alphas[i],
            self.critical_alphas[i + 1],
            alpha
        )
        self.animations[i].update(sub_alpha)
        self.current_alpha = alpha

    def clean_up(self, *args, **kwargs):
        # We clean up as though we've played ALL animations, even if
        # clean_up is called in middle of things
        for anim in self.animations:
            anim.clean_up(*args, **kwargs)


class OldAnimationGroup(OldAnimation):
    CONFIG = {
        "rate_func": None
    }

    def __init__(self, *sub_anims, **kwargs):
        sub_anims = [x for x in sub_anims if not(x.empty)]
        digest_config(self, locals())
        self.update_config(**kwargs)  # Handles propagation to self.sub_anims

        if len(sub_anims) == 0:
            self.empty = True
            self.run_time = 0
        else:
            self.run_time = max([a.run_time for a in sub_anims])
        everything = Mobject(*[a.mobject for a in sub_anims])
        OldAnimation.__init__(self, everything, **kwargs)

    def update(self, alpha):
        for anim in self.sub_anims:
            anim.update(alpha * self.run_time / anim.run_time)

    def clean_up(self, *args, **kwargs):
        for anim in self.sub_anims:
            anim.clean_up(*args, **kwargs)

    def update_config(self, **kwargs):
        OldAnimation.update_config(self, **kwargs)

        # If AnimationGroup is called with any configuration,
        # it is propagated to the sub_animations
        for anim in self.sub_anims:
            anim.update_config(**kwargs)

# Variants on mappin an animation over submobjectsg


class OldLaggedStart(OldAnimation):
    CONFIG = {
        "run_time": 2,
        "lag_ratio": 0.5,
    }

    def __init__(self, AnimationClass, mobject, arg_creator=None, **kwargs):
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
        OldAnimation.__init__(self, mobject, **kwargs)

    def update(self, alpha):
        for anim in self.subanimations:
            anim.update(alpha)
        return self

    def clean_up(self, *args, **kwargs):
        for anim in self.subanimations:
            anim.clean_up(*args, **kwargs)


class OldApplyToCenters(OldAnimation):
    def __init__(self, AnimationClass, mobjects, **kwargs):
        full_kwargs = AnimationClass.CONFIG
        full_kwargs.update(kwargs)
        full_kwargs["mobject"] = Mobject(*[
            mob.get_point_mobject()
            for mob in mobjects
        ])
        self.centers_container = AnimationClass(**full_kwargs)
        full_kwargs.pop("mobject")
        OldAnimation.__init__(self, Mobject(*mobjects), **full_kwargs)
        self.name = str(self) + AnimationClass.__name__

    def update_mobject(self, alpha):
        self.centers_container.update_mobject(alpha)
        center_mobs = self.centers_container.mobject.split()
        mobjects = self.mobject.split()
        for center_mob, mobject in zip(center_mobs, mobjects):
            mobject.shift(
                center_mob.get_center() - mobject.get_center()
            )
