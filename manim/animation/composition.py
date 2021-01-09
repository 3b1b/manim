"""Tools for displaying multiple animations at once."""
import typing

import numpy as np

from ..animation.animation import Animation, prepare_animation
from ..mobject.mobject import Group, Mobject
from ..scene.scene import Scene
from ..utils.bezier import interpolate
from ..utils.iterables import remove_list_redundancies
from ..utils.rate_functions import linear

if typing.TYPE_CHECKING:
    from ..mobject.types.vectorized_mobject import VGroup

__all__ = ["AnimationGroup", "Succession", "LaggedStart", "LaggedStartMap"]


DEFAULT_LAGGED_START_LAG_RATIO: float = 0.05


class AnimationGroup(Animation):
    def __init__(
        self,
        *animations: Animation,
        group: typing.Union[Group, "VGroup"] = None,
        run_time: float = None,
        rate_func: typing.Callable[[float], float] = linear,
        lag_ratio: float = 0,
        **kwargs
    ) -> None:
        self.animations = [prepare_animation(anim) for anim in animations]
        self.group = group
        if self.group is None:
            self.group = Group(
                *remove_list_redundancies([anim.mobject for anim in animations])
            )
        super().__init__(self.group, rate_func=rate_func, lag_ratio=lag_ratio, **kwargs)
        self.run_time = run_time
        self.init_run_time()

    def get_all_mobjects(self) -> Group:
        return self.group

    def get_run_time(self) -> float:
        if super().get_run_time() is None:
            self.init_run_time()
        return super().get_run_time()

    def begin(self) -> None:
        for anim in self.animations:
            anim.begin()

    def finish(self) -> None:
        for anim in self.animations:
            anim.finish()

    def clean_up_from_scene(self, scene: Scene) -> None:
        for anim in self.animations:
            anim.clean_up_from_scene(scene)

    def update_mobjects(self, dt: int) -> None:
        for anim in self.animations:
            anim.update_mobjects(dt)

    def init_run_time(self) -> None:
        self.build_animations_with_timings()
        if self.anims_with_timings:
            self.max_end_time = np.max([awt[2] for awt in self.anims_with_timings])
        else:
            self.max_end_time = 0
        self.run_time = self.max_end_time if self.run_time is None else self.run_time

    def build_animations_with_timings(self) -> None:
        """
        Creates a list of triplets of the form
        (anim, start_time, end_time)
        """
        self.anims_with_timings = []
        curr_time = 0
        for anim in self.animations:
            start_time = curr_time
            end_time = start_time + anim.get_run_time()
            self.anims_with_timings.append((anim, start_time, end_time))
            # Start time of next animation is based on
            # the lag_ratio
            curr_time = interpolate(start_time, end_time, self.lag_ratio)

    def interpolate(self, alpha: float) -> None:
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
                sub_alpha = np.clip((time - start_time) / anim_time, 0, 1)
            anim.interpolate(sub_alpha)


class Succession(AnimationGroup):
    def __init__(self, *animations: Animation, lag_ratio: float = 1, **kwargs) -> None:
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)

    def begin(self) -> None:
        assert len(self.animations) > 0
        self.init_run_time()
        self.update_active_animation(0)

    def finish(self) -> None:
        while self.active_animation is not None:
            self.next_animation()

    def update_mobjects(self, dt: int) -> None:
        if self.active_animation:
            self.active_animation.update_mobjects(dt)

    def update_active_animation(self, index: int) -> None:
        self.active_index = index
        if index >= len(self.animations):
            self.active_animation = None
            self.active_start_time = None
            self.active_end_time = None
        else:
            self.active_animation = self.animations[index]
            self.active_animation.begin()
            self.active_start_time = self.anims_with_timings[index][1]
            self.active_end_time = self.anims_with_timings[index][2]

    def next_animation(self) -> None:
        self.active_animation.finish()
        self.update_active_animation(self.active_index + 1)

    def interpolate(self, alpha: float) -> None:
        current_time = interpolate(0, self.run_time, alpha)
        while self.active_end_time is not None and current_time >= self.active_end_time:
            self.next_animation()
        if self.active_animation:
            elapsed = current_time - self.active_start_time
            active_run_time = self.active_animation.get_run_time()
            subalpha = elapsed / active_run_time if active_run_time != 0.0 else 1.0
            self.active_animation.interpolate(subalpha)


class LaggedStart(AnimationGroup):
    def __init__(
        self,
        *animations: Animation,
        lag_ratio: float = DEFAULT_LAGGED_START_LAG_RATIO,
        **kwargs
    ):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)


class LaggedStartMap(LaggedStart):
    def __init__(
        self,
        AnimationClass: Animation,
        mobject: Mobject,
        arg_creator: typing.Callable[[Mobject], str] = None,
        run_time: float = 2,
        **kwargs
    ) -> None:
        args_list = []
        for submob in mobject:
            if arg_creator:
                args_list.append(arg_creator(submob))
            else:
                args_list.append((submob,))
        anim_kwargs = dict(kwargs)
        if "lag_ratio" in anim_kwargs:
            anim_kwargs.pop("lag_ratio")
        animations = [AnimationClass(*args, **anim_kwargs) for args in args_list]
        super().__init__(*animations, run_time=run_time, **kwargs)
