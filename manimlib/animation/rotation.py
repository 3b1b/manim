import numpy as np

from manimlib.animation.animation import Animation
from manimlib.animation.transform import Transform
from manimlib.constants import *
from manimlib.utils.config_ops import digest_config


class Rotating(Animation):
    CONFIG = {
        "axis": OUT,
        "radians": TAU,
        "run_time": 5,
        "rate_func": None,
        "in_place": True,
        "about_point": None,
        "about_edge": None,
    }

    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        if self.in_place and self.about_point is None:
            self.about_point = self.mobject.get_center()
        self.mobject.rotate(
            alpha * self.radians,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )


class Rotate(Transform):
    CONFIG = {
        "in_place": False,
        "about_point": None,
    }

    def __init__(self, mobject, angle=np.pi, axis=OUT, **kwargs):
        if "path_arc" not in kwargs:
            kwargs["path_arc"] = angle
        if "path_arc_axis" not in kwargs:
            kwargs["path_arc_axis"] = axis
        digest_config(self, kwargs, locals())
        target = mobject.copy()
        if self.in_place:
            self.about_point = mobject.get_center()
        target.rotate(
            angle,
            axis=axis,
            about_point=self.about_point,
        )
        Transform.__init__(self, mobject, target, **kwargs)
