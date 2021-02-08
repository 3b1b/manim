"""Animations that grow mobjects."""

__all__ = [
    "GrowFromPoint",
    "GrowFromCenter",
    "GrowFromEdge",
    "GrowArrow",
    "SpinInFromNothing",
]

import typing

import numpy as np

from ..animation.transform import Transform
from ..constants import PI

if typing.TYPE_CHECKING:
    from ..mobject.geometry import Arrow
    from ..mobject.mobject import Mobject


class GrowFromPoint(Transform):
    def __init__(
        self, mobject: "Mobject", point: np.ndarray, point_color: str = None, **kwargs
    ) -> None:
        self.point = point
        self.point_color = point_color
        super().__init__(mobject, **kwargs)

    def create_target(self) -> "Mobject":
        return self.mobject

    def create_starting_mobject(self) -> "Mobject":
        start = super().create_starting_mobject()
        start.scale(0)
        start.move_to(self.point)
        if self.point_color:
            start.set_color(self.point_color)
        return start


class GrowFromCenter(GrowFromPoint):
    def __init__(self, mobject: "Mobject", point_color: str = None, **kwargs) -> None:
        point = mobject.get_center()
        super().__init__(mobject, point, point_color=point_color, **kwargs)


class GrowFromEdge(GrowFromPoint):
    def __init__(self, mobject: "Mobject", edge: np.ndarray, **kwargs) -> None:
        point = mobject.get_critical_point(edge)
        super().__init__(mobject, point, **kwargs)


class GrowArrow(GrowFromPoint):
    def __init__(self, arrow: "Arrow", **kwargs) -> None:
        point = arrow.get_start()
        super().__init__(arrow, point, **kwargs)

    def create_starting_mobject(self) -> "Mobject":
        start_arrow = self.mobject.copy()
        start_arrow.scale(0, scale_tips=True, about_point=self.point)
        if self.point_color:
            start_arrow.set_color(self.point_color)
        return start_arrow


class SpinInFromNothing(GrowFromCenter):
    def __init__(self, mobject: "Mobject", path_arc: float = PI, **kwargs) -> None:
        super().__init__(mobject, path_arc=path_arc, **kwargs)
