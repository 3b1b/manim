from __future__ import annotations

from manimlib.animation.animation import Animation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from manimlib.mobject.mobject import Mobject


class UpdateFromFunc(Animation):
    """
    update_function of the form func(mobject), presumably
    to be used when the state of one mobject is dependent
    on another simultaneously animated mobject
    """
    def __init__(
        self,
        mobject: Mobject,
        update_function: Callable[[Mobject], Mobject | None],
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        self.update_function = update_function
        super().__init__(
            mobject,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        self.update_function(self.mobject)


class UpdateFromAlphaFunc(Animation):
    def __init__(
        self,
        mobject: Mobject,
        update_function: Callable[[Mobject, float], Mobject | None],
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        self.update_function = update_function
        super().__init__(mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        self.update_function(self.mobject, alpha)


class MaintainPositionRelativeTo(Animation):
    def __init__(
        self,
        mobject: Mobject,
        tracked_mobject: Mobject,
        **kwargs
    ):
        self.tracked_mobject = tracked_mobject
        self.diff = mobject.get_center() - tracked_mobject.get_center()
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        target = self.tracked_mobject.get_center()
        location = self.mobject.get_center()
        self.mobject.shift(target - location + self.diff)
