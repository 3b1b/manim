from __future__ import absolute_import

from continual_animation.continual_animation import ContinualAnimation
from animation.update import MaintainPositionRelativeTo


class ContinualUpdateFromFunc(ContinualAnimation):
    CONFIG = {
        "function_depends_on_dt": False
    }

    def __init__(self, mobject, func, **kwargs):
        self.func = func
        ContinualAnimation.__init__(self, mobject, **kwargs)

    def update_mobject(self, dt):
        if self.function_depends_on_dt:
            self.func(self.mobject, dt)
        else:
            self.func(self.mobject)


class ContinualUpdateFromTimeFunc(ContinualUpdateFromFunc):
    CONFIG = {
        "function_depends_on_dt": True
    }


class ContinualMaintainPositionRelativeTo(ContinualAnimation):
    # TODO: Possibly reimplement using CycleAnimation?
    def __init__(self, mobject, tracked_mobject, **kwargs):
        self.anim = MaintainPositionRelativeTo(
            mobject, tracked_mobject, **kwargs)
        ContinualAnimation.__init__(self, mobject, **kwargs)

    def update_mobject(self, dt):
        self.anim.update(0)  # 0 is arbitrary
