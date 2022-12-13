from __future__ import annotations

from manimlib.animation.transform import Transform
from manimlib.constants import PI

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

    from manimlib.mobject.geometry import Arrow
    from manimlib.mobject.mobject import Mobject


class GrowFromPoint(Transform):
    CONFIG = {
        "point_color": None,
    }

    def __init__(self, mobject: Mobject, point: np.ndarray, **kwargs):
        self.point = point
        super().__init__(mobject, **kwargs)

    def create_target(self) -> Mobject:
        return self.mobject

    def create_starting_mobject(self) -> Mobject:
        start = super().create_starting_mobject()
        start.scale(0)
        start.move_to(self.point)
        if self.point_color:
            start.set_color(self.point_color)
        return start


class GrowFromCenter(GrowFromPoint):
    def __init__(self, mobject: Mobject, **kwargs):
        point = mobject.get_center()
        super().__init__(mobject, point, **kwargs)


class GrowFromEdge(GrowFromPoint):
    def __init__(self, mobject: Mobject, edge: np.ndarray, **kwargs):
        point = mobject.get_bounding_box_point(edge)
        super().__init__(mobject, point, **kwargs)


class GrowArrow(GrowFromPoint):
    def __init__(self, arrow: Arrow, **kwargs):
        point = arrow.get_start()
        super().__init__(arrow, point, **kwargs)


class SpinInFromNothing(GrowFromCenter):
    CONFIG = {
        "path_arc": PI,
    }
