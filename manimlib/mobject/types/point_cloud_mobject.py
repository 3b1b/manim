from __future__ import annotations

import numpy as np

from manimlib.mobject.mobject import Mobject
from manimlib.utils.color import color_gradient
from manimlib.utils.color import color_to_rgba
from manimlib.utils.iterables import resize_array
from manimlib.utils.iterables import resize_with_interpolation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import ManimColor, Vect3, Vect3Array, Vect4Array


class PMobject(Mobject):
    def set_points(self, points: Vect3Array):
        if len(points) == 0:
            points = np.zeros((0, 3))
        super().set_points(points)
        self.resize_points(len(points))
        return self

    def add_points(
        self,
        points: Vect3Array,
        rgbas: Vect4Array | None = None,
        color: ManimColor | None = None,
        opacity: float | None = None
    ):
        """
        points must be a Nx3 numpy array, as must rgbas if it is not None
        """
        self.append_points(points)
        # rgbas array will have been resized with points
        if color is not None:
            if opacity is None:
                opacity = self.data["rgbas"][-1, 3]
            rgbas = np.repeat(
                [color_to_rgba(color, opacity)],
                len(points),
                axis=0
            )
        if rgbas is not None:
            self.data["rgbas"][-len(rgbas):] = rgbas
        return self

    def add_point(self, point: Vect3, rgba=None, color=None, opacity=None):
        rgbas = None if rgba is None else [rgba]
        self.add_points([point], rgbas, color, opacity)
        return self

    def set_color_by_gradient(self, *colors: ManimColor):
        self.data["rgbas"][:] = np.array(list(map(
            color_to_rgba,
            color_gradient(colors, self.get_num_points())
        )))
        return self

    def match_colors(self, pmobject: PMobject):
        self.data["rgbas"][:] = resize_with_interpolation(
            pmobject.data["rgbas"], self.get_num_points()
        )
        return self

    def filter_out(self, condition: Callable[[np.ndarray], bool]):
        for mob in self.family_members_with_points():
            to_keep = ~np.apply_along_axis(condition, 1, mob.get_points())
            for key in mob.data:
                mob.data[key] = mob.data[key][to_keep]
        return self

    def sort_points(self, function: Callable[[Vect3], None] = lambda p: p[0]):
        """
        function is any map from R^3 to R
        """
        for mob in self.family_members_with_points():
            indices = np.argsort(
                np.apply_along_axis(function, 1, mob.get_points())
            )
            for key in mob.data:
                mob.data[key][:] = mob.data[key][indices]
        return self

    def ingest_submobjects(self):
        for key in self.data:
            self.data[key] = np.vstack([
                sm.data[key]
                for sm in self.get_family()
            ])
        return self

    def point_from_proportion(self, alpha: float) -> np.ndarray:
        index = alpha * (self.get_num_points() - 1)
        return self.get_points()[int(index)]

    def pointwise_become_partial(self, pmobject: PMobject, a: float, b: float):
        lower_index = int(a * pmobject.get_num_points())
        upper_index = int(b * pmobject.get_num_points())
        for key in self.data:
            self.data[key] = pmobject.data[key][lower_index:upper_index].copy()
        return self


class PGroup(PMobject):
    def __init__(self, *pmobs: PMobject, **kwargs):
        if not all([isinstance(m, PMobject) for m in pmobs]):
            raise Exception("All submobjects must be of type PMobject")
        super().__init__(**kwargs)
        self.add(*pmobs)
