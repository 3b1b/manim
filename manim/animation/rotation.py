"""Animations related to rotation."""

__all__ = ["Rotating", "Rotate"]


from ..animation.animation import Animation
from ..animation.transform import Transform
from ..constants import OUT
from ..constants import PI
from ..constants import TAU
from ..utils.rate_functions import linear


class Rotating(Animation):
    def __init__(
        self,
        mobject,
        axis=OUT,
        radians=TAU,
        about_point=None,
        about_edge=None,
        run_time=5,
        rate_func=linear,
        **kwargs
    ):
        self.axis = axis
        self.radians = radians
        self.about_point = about_point
        self.about_edge = about_edge
        super().__init__(mobject, run_time=run_time, rate_func=rate_func, **kwargs)

    def interpolate_mobject(self, alpha):
        self.mobject.become(self.starting_mobject)
        self.mobject.rotate(
            alpha * self.radians,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )


class Rotate(Transform):
    def __init__(
        self, mobject, angle=PI, axis=OUT, about_point=None, about_edge=None, **kwargs
    ):
        if "path_arc" not in kwargs:
            kwargs["path_arc"] = angle
        if "path_arc_axis" not in kwargs:
            kwargs["path_arc_axis"] = axis
        self.angle = angle
        self.axis = axis
        self.about_edge = about_edge
        self.about_point = about_point
        super().__init__(mobject, **kwargs)

    def create_target(self):
        target = self.mobject.copy()
        target.rotate(
            self.angle,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )
        return target
