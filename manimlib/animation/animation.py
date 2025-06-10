from __future__ import annotations

from copy import deepcopy

from manimlib.mobject.mobject import _AnimationBuilder
from manimlib.mobject.mobject import Mobject
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.rate_functions import smooth
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from manimlib.scene.scene import Scene


DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0


class Animation(object):
    def __init__(
        self,
        mobject: Mobject,
        run_time: float = DEFAULT_ANIMATION_RUN_TIME,
        # Tuple of times, between which the animation will run
        time_span: tuple[float, float] | None = None,
        # If 0, the animation is applied to all submobjects at the same time
        # If 1, it is applied to each successively.
        # If 0 < lag_ratio < 1, its applied to each with lagged start times
        lag_ratio: float = DEFAULT_ANIMATION_LAG_RATIO,
        rate_func: Callable[[float], float] = smooth,
        name: str = "",
        # Does this animation add or remove a mobject from the screen
        remover: bool = False,
        # What to enter into the update function upon completion
        final_alpha_value: float = 1.0,
        # If set to True, the mobject itself will have its internal updaters called,
        # but the start or target mobjects would not be suspended. To completely suspend
        # updating, call mobject.suspend_updating() before the animation
        suspend_mobject_updating: bool = False,
    ):
        self._validate_input_type(mobject)
        self.mobject = mobject
        self.run_time = run_time
        self.time_span = time_span
        self.rate_func = rate_func
        self.name = name or self.__class__.__name__ + str(self.mobject)
        self.remover = remover
        self.final_alpha_value = final_alpha_value
        self.lag_ratio = lag_ratio
        self.suspend_mobject_updating = suspend_mobject_updating

    def _validate_input_type(self, mobject: Mobject) -> None:
        if not isinstance(mobject, Mobject):
            raise TypeError("Animation only works for Mobjects.")

    def __str__(self) -> str:
        return self.name

    def begin(self) -> None:
        # This is called right as an animation is being
        # played.  As much initialization as possible,
        # especially any mobject copying, should live in
        # this method
        if self.time_span is not None:
            start, end = self.time_span
            self.run_time = max(end, self.run_time)
        self.mobject.set_animating_status(True)
        self.starting_mobject = self.create_starting_mobject()
        if self.suspend_mobject_updating:
            self.mobject_was_updating = not self.mobject.updating_suspended
            self.mobject.suspend_updating()
        self.families = list(self.get_all_families_zipped())
        self.interpolate(0)

    def finish(self) -> None:
        self.interpolate(self.final_alpha_value)
        self.mobject.set_animating_status(False)
        if self.suspend_mobject_updating and self.mobject_was_updating:
            self.mobject.resume_updating()

    def clean_up_from_scene(self, scene: Scene) -> None:
        if self.is_remover():
            scene.remove(self.mobject)

    def create_starting_mobject(self) -> Mobject:
        # Keep track of where the mobject starts
        return self.mobject.copy()

    def get_all_mobjects(self) -> tuple[Mobject, Mobject]:
        """
        Ordering must match the ording of arguments to interpolate_submobject
        """
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self) -> zip[tuple[Mobject]]:
        return zip(*[
            mob.get_family()
            for mob in self.get_all_mobjects()
        ])

    def update_mobjects(self, dt: float) -> None:
        """
        Updates things like starting_mobject, and (for
        Transforms) target_mobject.
        """
        for mob in self.get_all_mobjects_to_update():
            mob.update(dt)

    def get_all_mobjects_to_update(self) -> list[Mobject]:
        # The surrounding scene typically handles
        # updating of self.mobject.
        items = list(filter(
            lambda m: m is not self.mobject,
            self.get_all_mobjects()
        ))
        items = remove_list_redundancies(items)
        return items

    def copy(self):
        return deepcopy(self)

    def update_rate_info(
        self,
        run_time: float | None = None,
        rate_func: Callable[[float], float] | None = None,
        lag_ratio: float | None = None,
    ):
        self.run_time = run_time or self.run_time
        self.rate_func = rate_func or self.rate_func
        self.lag_ratio = lag_ratio or self.lag_ratio
        return self

    # Methods for interpolation, the mean of an Animation
    def interpolate(self, alpha: float) -> None:
        self.interpolate_mobject(alpha)

    def update(self, alpha: float) -> None:
        """
        This method shouldn't exist, but it's here to
        keep many old scenes from breaking
        """
        self.interpolate(alpha)

    def time_spanned_alpha(self, alpha: float) -> float:
        if self.time_span is not None:
            start, end = self.time_span
            return clip(alpha * self.run_time - start, 0, end - start) / (end - start)
        return alpha

    def interpolate_mobject(self, alpha: float) -> None:
        for i, mobs in enumerate(self.families):
            sub_alpha = self.get_sub_alpha(self.time_spanned_alpha(alpha), i, len(self.families))
            self.interpolate_submobject(*mobs, sub_alpha)

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_submobject: Mobject,
        alpha: float
    ):
        # Typically ipmlemented by subclass
        pass

    def get_sub_alpha(
        self,
        alpha: float,
        index: int,
        num_submobjects: int
    ) -> float:
        # TODO, make this more understanable, and/or combine
        # its functionality with AnimationGroup's method
        # build_animations_with_timings
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        raw_sub_alpha = clip((value - lower), 0, 1)
        return self.rate_func(raw_sub_alpha)

    # Getters and setters
    def set_run_time(self, run_time: float):
        self.run_time = run_time
        return self

    def get_run_time(self) -> float:
        if self.time_span:
            return max(self.run_time, self.time_span[1])
        return self.run_time

    def set_rate_func(self, rate_func: Callable[[float], float]):
        self.rate_func = rate_func
        return self

    def get_rate_func(self) -> Callable[[float], float]:
        return self.rate_func

    def set_name(self, name: str):
        self.name = name
        return self

    def is_remover(self) -> bool:
        return self.remover


def prepare_animation(anim: Animation | _AnimationBuilder):
    if isinstance(anim, _AnimationBuilder):
        return anim.build()

    if isinstance(anim, Animation):
        return anim

    raise TypeError(f"Object {anim} cannot be converted to an animation")
