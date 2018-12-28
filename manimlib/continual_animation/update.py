from manimlib.animation.update import MaintainPositionRelativeTo
from manimlib.continual_animation.continual_animation import ContinualAnimation
from manimlib.mobject.value_tracker import ValueTracker


class ContinualUpdate(ContinualAnimation):
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


class ContinualUpdateFromTimeFunc(ContinualUpdate):
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


# TODO, maybe factor into a different file
class ContinualGrowValue(ContinualAnimation):
    CONFIG = {
        "rate": 1,
    }

    def __init__(self, value_tracker, **kwargs):
        if not isinstance(value_tracker, ValueTracker):
            raise Exception("ContinualGrowValue must take a ValueTracker as its mobject")
        self.value_tracker = value_tracker
        ContinualAnimation.__init__(self, value_tracker, **kwargs)

    def update_mobject(self, dt):
        self.value_tracker.set_value(
            self.value_tracker.get_value() + self.rate * dt
        )
