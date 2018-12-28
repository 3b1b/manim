import copy

from manimlib.constants import *
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.config_ops import instantiate


class ContinualAnimation(object):
    CONFIG = {
        "start_up_time": 1,
        "wind_down_time": 1,
        "end_time": np.inf,
    }

    def __init__(self, mobject, **kwargs):
        mobject = instantiate(mobject)
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


class ContinualAnimationGroup(ContinualAnimation):
    CONFIG = {
        "start_up_time": 0,
        "wind_down_time": 0,
    }

    def __init__(self, *continual_animations, **kwargs):
        digest_config(self, kwargs, locals())
        self.group = Group(*[ca.mobject for ca in continual_animations])
        ContinualAnimation.__init__(self, self.group, **kwargs)

    def update_mobject(self, dt):
        for continual_animation in self.continual_animations:
            continual_animation.update(dt)


class ContinualRotation(ContinualAnimation):
    CONFIG = {
        "axis": OUT,
        "rate": np.pi / 12,  # Radians per second
        "in_place": True,
        "about_point": None,
    }

    def update_mobject(self, dt):
        if self.about_point:
            about_point = self.about_point
        elif self.in_place:
            about_point = self.mobject.get_center()
        else:
            about_point = ORIGIN
        self.mobject.rotate(
            dt * self.rate, axis=self.axis,
            about_point=about_point
        )


class ContinualMovement(ContinualAnimation):
    CONFIG = {
        "direction": RIGHT,
        "rate": 0.05,  # Units per second
    }

    def update_mobject(self, dt):
        self.mobject.shift(dt * self.rate * self.direction)
