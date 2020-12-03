"""Animations that grow mobjects."""

__all__ = [
    "GrowFromPoint",
    "GrowFromCenter",
    "GrowFromEdge",
    "GrowArrow",
    "SpinInFromNothing",
]


from ..animation.transform import Transform
from ..constants import PI


class GrowFromPoint(Transform):
    def __init__(self, mobject, point, point_color=None, **kwargs):
        self.point = point
        self.point_color = point_color
        super().__init__(mobject, **kwargs)

    def create_target(self):
        return self.mobject

    def create_starting_mobject(self):
        start = super().create_starting_mobject()
        start.scale(0)
        start.move_to(self.point)
        if self.point_color:
            start.set_color(self.point_color)
        return start


class GrowFromCenter(GrowFromPoint):
    def __init__(self, mobject, point_color=None, **kwargs):
        point = mobject.get_center()
        super().__init__(mobject, point, point_color=point_color, **kwargs)


class GrowFromEdge(GrowFromPoint):
    def __init__(self, mobject, edge, **kwargs):
        point = mobject.get_critical_point(edge)
        super().__init__(mobject, point, **kwargs)


class GrowArrow(GrowFromPoint):
    def __init__(self, arrow, **kwargs):
        point = arrow.get_start()
        super().__init__(arrow, point, **kwargs)


class SpinInFromNothing(GrowFromCenter):
    def __init__(self, mobject, path_arc=PI, **kwargs):
        super().__init__(mobject, path_arc=path_arc, **kwargs)
