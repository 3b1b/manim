from helpers import *
from mobject import Mobject

class ContinualAnimation(object):
    CONFIG = {
        "start_up_time" : 1,
        "wind_down_time" : 1,
    }
    def __init__(self, mobject, **kwargs):
        mobject = instantiate(mobject)
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs, locals())
        self.total_time = 0
        self.setup()

    def setup(self):
        #To implement in subclass
        pass

    def update(self, dt):
        if self.total_time < self.start_up_time:
             dt *= float(self.total_time+dt)/self.start_time
        self.total_time += dt
        self.update_mobject(dt)

    def update_mobject(self, dt):
        #To implement in subclass
        pass






















