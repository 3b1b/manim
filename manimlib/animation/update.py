from manimlib.animation.animation import Animation
from manimlib.constants import *
from manimlib.utils.config_ops import digest_config


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
        "tracked_critical_point": ORIGIN
    }

    def __init__(self, mobject, tracked_mobject, **kwargs):
        digest_config(self, kwargs, locals())
        tcp = self.tracked_critical_point
        self.diff = mobject.get_critical_point(tcp) - \
            tracked_mobject.get_critical_point(tcp)
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        target = self.tracked_mobject.get_critical_point(self.tracked_critical_point)
        location = self.mobject.get_critical_point(self.tracked_critical_point)
        self.mobject.shift(target - location + self.diff)
