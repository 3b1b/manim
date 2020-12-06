"""Animations that update mobjects."""

__all__ = ["UpdateFromFunc", "UpdateFromAlphaFunc", "MaintainPositionRelativeTo"]


import operator as op
import typing

from ..animation.animation import Animation

if typing.TYPE_CHECKING:
    from ..mobject.mobject import Mobject


class UpdateFromFunc(Animation):
    """
    update_function of the form func(mobject), presumably
    to be used when the state of one mobject is dependent
    on another simultaneously animated mobject
    """

    def __init__(
        self,
        mobject: "Mobject",
        update_function: typing.Callable[["Mobject"], typing.Any],
        suspend_mobject_updating: bool = False,
        **kwargs
    ) -> None:
        self.update_function = update_function
        super().__init__(
            mobject, suspend_mobject_updating=suspend_mobject_updating, **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        self.update_function(self.mobject)


class UpdateFromAlphaFunc(UpdateFromFunc):
    def interpolate_mobject(self, alpha: float) -> None:
        self.update_function(self.mobject, alpha)


class MaintainPositionRelativeTo(Animation):
    def __init__(
        self, mobject: "Mobject", tracked_mobject: "Mobject", **kwargs
    ) -> None:
        self.tracked_mobject = tracked_mobject
        self.diff = op.sub(
            mobject.get_center(),
            tracked_mobject.get_center(),
        )
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        target = self.tracked_mobject.get_center()
        location = self.mobject.get_center()
        self.mobject.shift(target - location + self.diff)
