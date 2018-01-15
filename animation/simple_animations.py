import numpy as np
import itertools as it

from helpers import *

from mobject import Mobject, Group
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TextMobject
from animation import Animation
from animation import sync_animation_run_times_and_rate_funcs
from transform import Transform

class Rotating(Animation):
    CONFIG = {
        "axes"       : [],
        "axis"       : OUT,
        "radians"    : 2*np.pi,
        "run_time"   : 5,
        "rate_func"  : None,
        "in_place"   : True,
        "about_point" : None,
    }
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        axes = self.axes if self.axes else [self.axis]
        about_point = None
        if self.about_point is not None:
            about_point = self.about_point
        elif self.in_place: #This is superseeded
            self.about_point = self.mobject.get_center()
        self.mobject.rotate(
            alpha*self.radians, 
            axes = axes,
            about_point = self.about_point
        )

class ShowPartial(Animation):
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.pointwise_become_partial(
            starting_submobject, *self.get_bounds(alpha)
        )

    def get_bounds(self, alpha):
        raise Exception("Not Implemented")

class ShowCreation(ShowPartial):
    CONFIG = {
        "submobject_mode" : "one_at_a_time",
    }
    def get_bounds(self, alpha):
        return (0, alpha)

class Uncreate(ShowCreation):
    CONFIG = {
        "rate_func" : lambda t : smooth(1-t),
        "remover"   : True
    }

class Write(ShowCreation):
    CONFIG = {
        "rate_func" : None,
        "submobject_mode" : "lagged_start",
    }
    def __init__(self, mob_or_text, **kwargs):
        digest_config(self, kwargs)        
        if isinstance(mob_or_text, str):
            mobject = TextMobject(mob_or_text)
        else:
            mobject = mob_or_text
        if "run_time" not in kwargs:
            self.establish_run_time(mobject)
        if "lag_factor" not in kwargs:
            if len(mobject.family_members_with_points()) < 4:
                min_lag_factor = 1
            else:
                min_lag_factor = 2
            self.lag_factor = max(self.run_time - 1, min_lag_factor)
        ShowCreation.__init__(self, mobject, **kwargs)

    def establish_run_time(self, mobject):
        num_subs = len(mobject.family_members_with_points())
        if num_subs < 15:
            self.run_time = 1
        else:
            self.run_time = 2

class DrawBorderThenFill(Animation):
    CONFIG = {
        "run_time" : 2,
        "stroke_width" : 2,
        "stroke_color" : None,
        "rate_func" : double_smooth,
    }
    def __init__(self, vmobject, **kwargs):
        if not isinstance(vmobject, VMobject):
            raise Exception("DrawBorderThenFill only works for VMobjects")
        self.reached_halfway_point_before = False
        Animation.__init__(self, vmobject, **kwargs)

    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.pointwise_become_partial(
            starting_submobject, 0, min(2*alpha, 1)
        )
        if alpha < 0.5:
            if self.stroke_color:
                color = self.stroke_color 
            elif starting_submobject.stroke_width > 0:
                color = starting_submobject.get_stroke_color()
            else:
                color = starting_submobject.get_color()
            submobject.set_stroke(color, width = self.stroke_width)
            submobject.set_fill(opacity = 0)
        else:
            if not self.reached_halfway_point_before:
                self.reached_halfway_point_before = True
                submobject.points = np.array(starting_submobject.points)
            width, opacity = [
                interpolate(start, end, 2*alpha - 1)
                for start, end in [
                    (self.stroke_width, starting_submobject.get_stroke_width()),
                    (0, starting_submobject.get_fill_opacity())
                ]
            ]
            submobject.set_stroke(width = width)
            submobject.set_fill(opacity = opacity)

class ShowPassingFlash(ShowPartial):
    CONFIG = {
        "time_width" : 0.1,
        "remover" : True,
    }
    def get_bounds(self, alpha):
        alpha *= (1+self.time_width)
        alpha -= self.time_width/2.0
        lower = max(0, alpha - self.time_width/2.0)
        upper = min(1, alpha + self.time_width/2.0)
        return (lower, upper)

    def clean_up(self, *args, **kwargs):
        ShowPartial.clean_up(self, *args, **kwargs)
        for submob, start_submob in self.get_all_families_zipped():
            submob.pointwise_become_partial(start_submob, 0, 1)

class ShowCreationThenDestruction(ShowPassingFlash):
    CONFIG = {
        "time_width" : 2.0,
        "run_time" : 1,
    }

class Homotopy(Animation):
    CONFIG = {
        "run_time" : 3,
        "apply_function_kwargs" : {},
    }
    def __init__(self, homotopy, mobject, **kwargs):
        """
        Homotopy a function from (x, y, z, t) to (x', y', z')
        """
        def function_at_time_t(t):
            return lambda p : homotopy(p[0], p[1], p[2], t)
        self.function_at_time_t = function_at_time_t
        digest_config(self, kwargs)
        Animation.__init__(self, mobject, **kwargs)

    def update_submobject(self, submob, start, alpha):
        submob.points = start.points
        submob.apply_function(
            self.function_at_time_t(alpha),
            **self.apply_function_kwargs
        )

class SmoothedVectorizedHomotopy(Homotopy):
    def update_submobject(self, submob, start, alpha):
        Homotopy.update_submobject(self, submob, start, alpha)
        submob.make_smooth()

class ApplyWave(Homotopy):
    CONFIG = {
        "direction" : DOWN,
        "amplitude" : 0.2,
        "run_time" : 1,
        "apply_function_kwargs" : {
            "maintain_smoothness" : False,
        },
    }
    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs, locals())
        left_x = mobject.get_left()[0]
        right_x = mobject.get_right()[0]
        vect = self.amplitude*self.direction
        def homotopy(x, y, z, t):
            start_point = np.array([x, y, z])
            alpha = (x-left_x)/(right_x-left_x)
            power = np.exp(2*(alpha-0.5))
            nudge = there_and_back(t**power)
            return np.array([x, y, z]) + nudge*vect
        Homotopy.__init__(self, homotopy, mobject, **kwargs)

class PhaseFlow(Animation):
    CONFIG = {
        "virtual_time" : 1,
        "rate_func" : None,
    }
    def __init__(self, function, mobject, **kwargs):
        digest_config(self, kwargs, locals())        
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        if hasattr(self, "last_alpha"):
            dt = self.virtual_time*(alpha-self.last_alpha)
            self.mobject.apply_function(
                lambda p : p + dt*self.function(p)
            )
        self.last_alpha = alpha

class MoveAlongPath(Animation):
    def __init__(self, mobject, path, **kwargs):
        digest_config(self, kwargs, locals())
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)

class UpdateFromFunc(Animation):
    """
    update_function of the form func(mobject), presumably
    to be used when the state of one mobject is dependent
    on another simultaneously animated mobject
    """
    def __init__(self, mobject, update_function, **kwargs):
        digest_config(self, kwargs, locals())
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        self.update_function(self.mobject)

class UpdateFromAlphaFunc(UpdateFromFunc):
    def update_mobject(self, alpha):
        self.update_function(self.mobject, alpha)

class MaintainPositionRelativeTo(Animation):
    CONFIG = {
        "tracked_critical_point" : ORIGIN
    }
    def __init__(self, mobject, tracked_mobject, **kwargs):
        digest_config(self, kwargs, locals())
        tcp = self.tracked_critical_point
        self.diff = mobject.get_critical_point(tcp) - \
                    tracked_mobject.get_critical_point(tcp)
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        self.mobject.shift(
            self.tracked_mobject.get_critical_point(self.tracked_critical_point) - \
            self.mobject.get_critical_point(self.tracked_critical_point) + \
            self.diff
        )

### Animation modifiers ###

class ApplyToCenters(Animation):
    def __init__(self, AnimationClass, mobjects, **kwargs):
        full_kwargs = AnimationClass.CONFIG
        full_kwargs.update(kwargs)
        full_kwargs["mobject"] = Mobject(*[
            mob.get_point_mobject()
            for mob in mobjects
        ])
        self.centers_container = AnimationClass(**full_kwargs)
        full_kwargs.pop("mobject")
        Animation.__init__(self, Mobject(*mobjects), **full_kwargs)
        self.name = str(self) + AnimationClass.__name__

    def update_mobject(self, alpha):
        self.centers_container.update_mobject(alpha)
        center_mobs = self.centers_container.mobject.split()
        mobjects = self.mobject.split()        
        for center_mob, mobject in zip(center_mobs, mobjects):
            mobject.shift(
                center_mob.get_center()-mobject.get_center()
            )

class LaggedStart(Animation):
    CONFIG = {
        "run_time" : 2,
        "lag_ratio" : 0.5,
    }
    def __init__(self, AnimationClass, mobject, arg_creator = None, **kwargs):
        digest_config(self, kwargs)
        for key in "rate_func", "run_time", "lag_ratio":
            if key in kwargs:
                kwargs.pop(key)
        if arg_creator is None:
            arg_creator = lambda mobject : (mobject,)
        self.subanimations = [
            AnimationClass(
                *arg_creator(submob),
                run_time = self.run_time,
                rate_func = squish_rate_func(
                    self.rate_func, beta, beta + self.lag_ratio
                ),
                **kwargs
            )
            for submob, beta in zip(
                mobject, 
                np.linspace(0, 1-self.lag_ratio, len(mobject))
            )
        ]
        Animation.__init__(self, mobject, **kwargs)

    def update(self, alpha):
        for anim in self.subanimations:
            anim.update(alpha)
        return self

    def clean_up(self, *args, **kwargs):
        for anim in self.subanimations:
            anim.clean_up(*args, **kwargs)

class Succession(Animation):
    CONFIG = {
        "rate_func" : None,
    }
    def __init__(self, *args, **kwargs):
        """
        Each arg will either be an animation, or an animation class 
        followed by its arguments (and potentially a dict for 
        configuraiton).

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
            "animations" : animations,
            "curr_class" : None,
            "curr_class_args" : [],
            "curr_class_config" : {},
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
            if isinstance(arg, Animation):
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

        self.run_times = [anim.run_time for anim in animations]
        if "run_time" in kwargs:
            run_time = kwargs.pop("run_time")
        else:
            run_time = sum(self.run_times)
        self.num_anims = len(animations)
        self.animations = animations
        self.last_index = 0
        #Have to keep track of this run_time, because Scene.play
        #might very well mess with it.
        self.original_run_time = run_time

        mobject = Group(*[anim.mobject for anim in self.animations])
        Animation.__init__(self, mobject, run_time = run_time, **kwargs)

    def update_mobject(self, alpha):
        if alpha >= 1.0:
            self.animations[-1].update(1)
            return
        run_times = self.run_times
        index = 0
        time = alpha*self.original_run_time
        while sum(run_times[:index+1]) < time:
            index += 1
        if index > self.last_index:
            self.animations[self.last_index].update(1)
            self.animations[self.last_index].clean_up()
            self.last_index = index
        curr_anim = self.animations[index]
        sub_alpha = np.clip(
            (time - sum(run_times[:index]))/run_times[index], 0, 1
        )
        curr_anim.update(sub_alpha)

class AnimationGroup(Animation):
    CONFIG = {
        "rate_func" : None
    }
    def __init__(self, *sub_anims, **kwargs):
        digest_config(self, kwargs, locals())
        sync_animation_run_times_and_rate_funcs(*sub_anims, **kwargs)
        self.run_time = max([a.run_time for a in sub_anims])
        everything = Mobject(*[a.mobject for a in sub_anims])
        Animation.__init__(self, everything, **kwargs)

    def update_mobject(self, alpha):
        for anim in self.sub_anims:
            anim.update(alpha)





















