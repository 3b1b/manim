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
        "axis"       : OUT,
        "radians"    : 2*np.pi,
        "run_time"   : 5,
        "rate_func"  : None,
        "in_place"   : True,
        "about_point" : None,
        "about_edge" : None,
    }
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        about_point = None
        if self.about_point is not None:
            about_point = self.about_point
        elif self.in_place: #This is superseeded
            self.about_point = self.mobject.get_center()
        self.mobject.rotate(
            alpha*self.radians, 
            axis = self.axis,
            about_point = self.about_point,
            about_edge = self.about_edge,
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

class WiggleOutThenIn(Animation):
    CONFIG = {
        "scale_value" : 1.1,
        "rotation_angle" : 0.01*TAU,
        "n_wiggles" : 6,
        "run_time" : 2,
        "scale_about_point" : None,
        "rotate_about_point" : None,
    }
    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        if self.scale_about_point is None:
            self.scale_about_point = mobject.get_center()
        if self.rotate_about_point is None:
            self.rotate_about_point = mobject.get_center()
        Animation.__init__(self, mobject, **kwargs)

    def update_submobject(self, submobject, starting_sumobject, alpha):
        submobject.points[:,:] = starting_sumobject.points
        submobject.scale(
            interpolate(1, self.scale_value, there_and_back(alpha)),
            about_point = self.scale_about_point
        )
        submobject.rotate(
            wiggle(alpha, self.n_wiggles)*self.rotation_angle,
            about_point = self.rotate_about_point
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

        animations = filter (lambda x : not(x.empty), animations)

        self.run_times = [anim.run_time for anim in animations]
        if "run_time" in kwargs:
            run_time = kwargs.pop("run_time")
        else:
            run_time = sum(self.run_times)
        self.num_anims = len(animations)
        if self.num_anims == 0:
            self.empty = True
        self.animations = animations
        #Have to keep track of this run_time, because Scene.play
        #might very well mess with it.
        self.original_run_time = run_time

        # critical_alphas[i] is the start alpha of self.animations[i]
        # critical_alphas[i + 1] is the end alpha of self.animations[i]
        critical_times = np.concatenate(([0], np.cumsum(self.run_times)))
        self.critical_alphas = map (lambda x : np.true_divide(x, run_time), critical_times) if self.num_anims > 0 else [0.0]

        # self.scene_mobjects_at_time[i] is the scene's mobjects at start of self.animations[i]
        # self.scene_mobjects_at_time[i + 1] is the scene mobjects at end of self.animations[i]
        self.scene_mobjects_at_time = [None for i in range(self.num_anims + 1)]
        self.scene_mobjects_at_time[0] = Group()
        for i in range(self.num_anims):
            self.scene_mobjects_at_time[i + 1] = self.scene_mobjects_at_time[i].copy()
            self.animations[i].clean_up(self.scene_mobjects_at_time[i + 1])

        self.current_alpha = 0
        self.current_anim_index = 0 # If self.num_anims == 0, this is an invalid index, but so it goes
        if self.num_anims > 0:
            self.mobject = self.scene_mobjects_at_time[0]
            self.mobject.add(self.animations[0].mobject)
        else:
            self.mobject = Group()

        Animation.__init__(self, self.mobject, run_time = run_time, **kwargs)

    # Beware: This does NOT take care of calling update(0) on the subanimation.
    # This was important to avoid a pernicious possibility in which subanimations were called
    # with update(0) twice, which could in turn call a sub-Succession with update(0) four times,
    # continuing exponentially.
    def jump_to_start_of_anim(self, index):
        if index != self.current_anim_index:
            self.mobject.remove(*self.mobject.submobjects) # Should probably have a cleaner "remove_all" method...
            for m in self.scene_mobjects_at_time[index].submobjects:
                self.mobject.add(m)
            self.mobject.add(self.animations[index].mobject)

        self.current_anim_index = index
        self.current_alpha = self.critical_alphas[index]

    def update_mobject(self, alpha):
        if self.num_anims == 0:
            return

        i = 0
        while self.critical_alphas[i + 1] < alpha:
            i = i + 1
            # TODO: Special handling if alpha < 0 or alpha > 1, to use
            # first or last sub-animation

        # At this point, we should have self.critical_alphas[i] <= alpha <= self.critical_alphas[i +1]

        self.jump_to_start_of_anim(i)
        sub_alpha = inverse_interpolate(
            self.critical_alphas[i], 
            self.critical_alphas[i + 1], 
            alpha
        )
        self.animations[i].update(sub_alpha)

    def clean_up(self, *args, **kwargs):
        # We clean up as though we've played ALL animations, even if
        # clean_up is called in middle of things
        for anim in self.animations:
            anim.clean_up(*args, **kwargs)

class AnimationGroup(Animation):
    CONFIG = {
        "rate_func" : None
    }
    def __init__(self, *sub_anims, **kwargs):
        digest_config(self, kwargs, locals())
        sub_anims = filter (lambda x : not(x.empty), sub_anims)
        if len(sub_anims) == 0:
            self.empty = True
            self.run_time = 0
        else:
            # Should really make copies of animations, instead of messing with originals...
            sync_animation_run_times_and_rate_funcs(*sub_anims, **kwargs)
            self.run_time = max([a.run_time for a in sub_anims])
        everything = Mobject(*[a.mobject for a in sub_anims])
        Animation.__init__(self, everything, **kwargs)

    def update_mobject(self, alpha):
        for anim in self.sub_anims:
            anim.update(alpha)

    def clean_up(self, *args, **kwargs):
        for anim in self.sub_anims:
            anim.clean_up(*args, **kwargs)

class EmptyAnimation(Animation):
    CONFIG = {
        "run_time" : 0,
        "empty" : True
    }

    def __init__(self, *args, **kwargs):
        return Animation.__init__(self, Group(), *args, **kwargs)
