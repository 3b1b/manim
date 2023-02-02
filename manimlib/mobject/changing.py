from __future__ import annotations

import numpy as np

from manimlib.constants import BLUE_B, BLUE_D, BLUE_E, GREY_BROWN, WHITE
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.rate_functions import smooth

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, List, Iterable, Self
    from manimlib.typing import ManimColor, Vect3


class AnimatedBoundary(VGroup):
    def __init__(
        self,
        vmobject: VMobject,
        colors: List[ManimColor] = [BLUE_D, BLUE_B, BLUE_E, GREY_BROWN],
        max_stroke_width: float = 3.0,
        cycle_rate: float = 0.5,
        back_and_forth: bool = True,
        draw_rate_func: Callable[[float], float] = smooth,
        fade_rate_func: Callable[[float], float] = smooth,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vmobject: VMobject = vmobject
        self.colors = colors
        self.max_stroke_width = max_stroke_width
        self.cycle_rate = cycle_rate
        self.back_and_forth = back_and_forth
        self.draw_rate_func = draw_rate_func
        self.fade_rate_func = fade_rate_func

        self.boundary_copies: list[VMobject] = [
            vmobject.copy().set_style(
                stroke_width=0,
                fill_opacity=0
            )
            for x in range(2)
        ]
        self.add(*self.boundary_copies)
        self.total_time: float = 0
        self.add_updater(
            lambda m, dt: self.update_boundary_copies(dt)
        )

    def update_boundary_copies(self, dt: float) -> Self:
        # Not actual time, but something which passes at
        # an altered rate to make the implementation below
        # cleaner
        time = self.total_time * self.cycle_rate
        growing, fading = self.boundary_copies
        colors = self.colors
        msw = self.max_stroke_width
        vmobject = self.vmobject

        index = int(time % len(colors))
        alpha = time % 1
        draw_alpha = self.draw_rate_func(alpha)
        fade_alpha = self.fade_rate_func(alpha)

        if self.back_and_forth and int(time) % 2 == 1:
            bounds = (1 - draw_alpha, 1)
        else:
            bounds = (0, draw_alpha)
        self.full_family_become_partial(growing, vmobject, *bounds)
        growing.set_stroke(colors[index], width=msw)

        if time >= 1:
            self.full_family_become_partial(fading, vmobject, 0, 1)
            fading.set_stroke(
                color=colors[index - 1],
                width=(1 - fade_alpha) * msw
            )

        self.total_time += dt
        return self

    def full_family_become_partial(
        self,
        mob1: VMobject,
        mob2: VMobject,
        a: float,
        b: float
    ) -> Self:
        family1 = mob1.family_members_with_points()
        family2 = mob2.family_members_with_points()
        for sm1, sm2 in zip(family1, family2):
            sm1.pointwise_become_partial(sm2, a, b)
        return self


class TracedPath(VMobject):
    def __init__(
        self,
        traced_point_func: Callable[[], Vect3],
        time_traced: float = np.inf,
        time_per_anchor: float = 1.0 / 15,
        stroke_width: float | Iterable[float] = 2.0,
        stroke_color: ManimColor = WHITE,
        fill_opacity: float = 0.0,
        **kwargs
    ):
        super().__init__(
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            fill_opacity=fill_opacity,
            **kwargs
        )
        self.traced_point_func = traced_point_func
        self.time_traced = time_traced
        self.time_per_anchor = time_per_anchor
        self.time: float = 0
        self.traced_points: list[np.ndarray] = []
        self.add_updater(lambda m, dt: m.update_path(dt))

    def update_path(self, dt: float) -> Self:
        if dt == 0:
            return self
        point = self.traced_point_func().copy()
        self.traced_points.append(point)

        if self.time_traced < np.inf:
            n_relevant_points = int(self.time_traced / dt + 0.5)
            n_tps = len(self.traced_points)
            if n_tps < n_relevant_points:
                points = self.traced_points + [point] * (n_relevant_points - n_tps)
            else:
                points = self.traced_points[n_tps - n_relevant_points:]
            # Every now and then refresh the list
            if n_tps > 10 * n_relevant_points:
                self.traced_points = self.traced_points[-n_relevant_points:]
        else:
            points = self.traced_points

        if points:
            self.set_points_smoothly(points)

        self.time += dt
        return self


class TracingTail(TracedPath):
    def __init__(
        self,
        mobject_or_func: Mobject | Callable[[], np.ndarray],
        time_traced: float = 1.0,
        stroke_width: float | Iterable[float] = (0, 3),
        stroke_opacity: float | Iterable[float] = (0, 1),
        stroke_color: ManimColor = WHITE,
        **kwargs
    ):
        if isinstance(mobject_or_func, Mobject):
            func = mobject_or_func.get_center
        else:
            func = mobject_or_func
        super().__init__(
            func,
            time_traced=time_traced,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
            stroke_color=stroke_color,
            **kwargs
        )
