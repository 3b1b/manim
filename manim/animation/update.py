__all__ = ["UpdateFromFunc", "UpdateFromAlphaFunc", "MaintainPositionRelativeTo"]


import operator as op

from ..animation.animation import Animation


class UpdateFromFunc(Animation):
    """
    update_function of the form func(mobject), presumably
    to be used when the state of one mobject is dependent
    on another simultaneously animated mobject
    """

    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def __init__(self, mobject, update_function, **kwargs):
        self.update_function = update_function
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        self.update_function(self.mobject)


class UpdateFromAlphaFunc(UpdateFromFunc):
    def interpolate_mobject(self, alpha):
        self.update_function(self.mobject, alpha)


class MaintainPositionRelativeTo(Animation):
    def __init__(self, mobject, tracked_mobject, **kwargs):
        self.tracked_mobject = tracked_mobject
        self.diff = op.sub(
            mobject.get_center(),
            tracked_mobject.get_center(),
        )
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        target = self.tracked_mobject.get_center()
        location = self.mobject.get_center()
        self.mobject.shift(target - location + self.diff)
