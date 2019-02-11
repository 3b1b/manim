import copy

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config


class ContinualAnimation(object):
    CONFIG = {
        "start_up_time": 1,
        "wind_down_time": 1,
        "end_time": np.inf,
    }

    def __init__(self, mobject, **kwargs):
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs, locals())
        self.internal_time = 0
        self.external_time = 0
        self.setup()
        self.update(0)

    def setup(self):
        # To implement in subclass
        pass

    def begin_wind_down(self, wind_down_time=None):
        if wind_down_time is not None:
            self.wind_down_time = wind_down_time
        self.end_time = self.external_time + self.wind_down_time

    def update(self, dt):
        # TODO, currenty time moves slower for a
        # continual animation during its start up
        # to help smooth things out.  Does this have
        # unwanted consequences?
        self.external_time += dt
        if self.external_time < self.start_up_time:
            dt *= float(self.external_time) / self.start_up_time
        elif self.external_time > self.end_time - self.wind_down_time:
            dt *= np.clip(
                float(self.end_time - self.external_time) / self.wind_down_time,
                0, 1
            )
        self.internal_time += dt
        self.update_mobject(dt)

    def update_mobject(self, dt):
        # To implement in subclass
        pass

    def copy(self):
        return copy.deepcopy(self)
