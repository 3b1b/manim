"""Animate mobjects."""


__all__ = ["Animation", "Wait"]


import typing
from copy import deepcopy

import numpy as np
if typing.TYPE_CHECKING:
    from manim.scene.scene import Scene

from .. import logger
from ..mobject.mobject import Mobject
from ..utils.rate_functions import smooth

DEFAULT_ANIMATION_RUN_TIME: float = 1.0
DEFAULT_ANIMATION_LAG_RATIO: int = 0


class Animation:
    def __init__(
        self,
        mobject: Mobject,
        # If lag_ratio is 0, the animation is applied to all submobjects
        # at the same time
        # If 1, it is applied to each successively.
        # If 0 < lag_ratio < 1, its applied to each
        # with lagged start times
        lag_ratio: float = DEFAULT_ANIMATION_LAG_RATIO,
        run_time: int = DEFAULT_ANIMATION_RUN_TIME,
        rate_func: typing.Callable[[float, float], np.ndarray] = smooth,
        name: str = None,
        remover: bool = False,  # remove a mobject from the screen?
        suspend_mobject_updating: bool = True,
        **kwargs
    ) -> None:
        self._typecheck_input(mobject)
        self.run_time = run_time
        self.rate_func = rate_func
        self.name = name
        self.remover = remover
        self.suspend_mobject_updating = suspend_mobject_updating
        self.lag_ratio = lag_ratio
        self.starting_mobject = None
        self.mobject = mobject
        if kwargs:
            logger.debug("Animation received extra kwargs: %s", kwargs)

        if hasattr(self, "CONFIG"):
            logger.error(
                ("CONFIG has been removed from ManimCommunity.",
                "Please use keyword arguments instead.")
            )

    def _typecheck_input(self, mobject: Mobject) -> None:
        if mobject is None:
            logger.warning("creating dummy animation")
        elif not isinstance(mobject, Mobject):
            raise TypeError("Animation only works on Mobjects")

    def __str__(self) -> str:
        if self.name:
            return self.name
        return self.__class__.__name__ + str(self.mobject)

    def begin(self) -> None:
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

    def finish(self) -> None:
        self.interpolate(1)
        if self.suspend_mobject_updating:
            self.mobject.resume_updating()

    def clean_up_from_scene(self, scene: 'Scene') -> None:
        if self.is_remover():
            scene.remove(self.mobject)

    def create_starting_mobject(self) -> Mobject:
        # Keep track of where the mobject starts
        return self.mobject.copy()

    def get_all_mobjects(self) -> typing.Tuple[Mobject, typing.Union[Mobject, None]]:
        """
        Ordering must match the ording of arguments to interpolate_submobject
        """
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self) -> typing.Iterator[typing.Tuple]:
        return zip(
            *[mob.family_members_with_points() for mob in self.get_all_mobjects()]
        )

    def update_mobjects(self, dt: int) -> None:
        """
        Updates things like starting_mobject, and (for
        Transforms) target_mobject.  Note, since typically
        (always?) self.mobject will have its updating
        suspended during the animation, this will do
        nothing to self.mobject.
        """
        for mob in self.get_all_mobjects_to_update():
            mob.update(dt)

    def get_all_mobjects_to_update(self) -> list:
        # The surrounding scene typically handles
        # updating of self.mobject.  Besides, in
        # most cases its updating is suspended anyway
        return list(filter(lambda m: m is not self.mobject, self.get_all_mobjects()))

    def copy(self) -> "Animation":
        return deepcopy(self)

    def update_config(self, **kwargs: typing.Dict[str, typing.Any]) -> "Animation":
        self.__dict__.update(kwargs)
        return self

    # Methods for interpolation, the mean of an Animation
    def interpolate(self, alpha: float) -> None:
        alpha = np.clip(alpha, 0, 1)
        self.interpolate_mobject(self.rate_func(alpha))

    def update(self, alpha: float) -> None:
        """
        This method shouldn't exist, but it's here to
        keep many old scenes from breaking
        """
        logger.warning(
            "animation.update() has been deprecated. "
            "Please use animation.interpolate() instead."
        )
        self.interpolate(alpha)

    def interpolate_mobject(self, alpha: float) -> None:
        families = list(self.get_all_families_zipped())
        for i, mobs in enumerate(families):
            sub_alpha = self.get_sub_alpha(alpha, i, len(families))
            self.interpolate_submobject(*mobs, sub_alpha)

    def interpolate_submobject(
        self, submobject: Mobject, starting_sumobject: Mobject, alpha: float
    ) -> None:
        # Typically implemented by subclass
        pass

    def get_sub_alpha(self, alpha: float, index: int, num_submobjects: int):
        # TODO, make this more understanable, and/or combine
        # its functionality with AnimationGroup's method
        # build_animations_with_timings
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        return np.clip((value - lower), 0, 1)

    # Getters and setters
    def set_run_time(self, run_time: float) -> "Animation":
        self.run_time = run_time
        return self

    def get_run_time(self) -> float:
        return self.run_time

    def set_rate_func(
        self, rate_func: typing.Callable[[float, float], np.ndarray]
    ) -> "Animation":
        self.rate_func = rate_func
        return self

    def get_rate_func(self) -> typing.Callable[[float, float], np.ndarray]:
        return self.rate_func

    def set_name(self, name: str) -> "Animation":
        self.name = name
        return self

    def is_remover(self) -> bool:
        return self.remover


class Wait(Animation):
    def __init__(
        self, duration: float = 1, stop_condition=None, **kwargs
    ):  # what is stop_condition?
        self.duration = duration
        self.mobject = None
        self.stop_condition = stop_condition
        super().__init__(None, **kwargs)

    def begin(self) -> None:
        pass

    def finish(self) -> None:
        pass

    def clean_up_from_scene(self, scene: 'Scene') -> None:
        pass

    def update_mobjects(self, dt: int) -> None:
        pass

    def interpolate(self, alpha: float) -> None:
        pass
