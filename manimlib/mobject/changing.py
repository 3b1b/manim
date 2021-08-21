import numpy as np
from manimlib.constants import BLUE_D
from manimlib.constants import BLUE_B
from manimlib.constants import BLUE_E
from manimlib.constants import GREY_BROWN
from manimlib.constants import WHITE
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.rate_functions import smooth
from manimlib.utils.space_ops import get_norm


class AnimatedBoundary(VGroup):
    CONFIG = {
        "colors": [BLUE_D, BLUE_B, BLUE_E, GREY_BROWN],
        "max_stroke_width": 3,
        "cycle_rate": 0.5,
        "back_and_forth": True,
        "draw_rate_func": smooth,
        "fade_rate_func": smooth,
    }

    def __init__(self, vmobject, **kwargs):
        super().__init__(**kwargs)
        self.vmobject = vmobject
        self.boundary_copies = [
            vmobject.copy().set_style(
                stroke_width=0,
                fill_opacity=0
            )
            for x in range(2)
        ]
        self.add(*self.boundary_copies)
        self.total_time = 0
        self.add_updater(
            lambda m, dt: self.update_boundary_copies(dt)
        )

    def update_boundary_copies(self, dt):
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

    def full_family_become_partial(self, mob1, mob2, a, b):
        family1 = mob1.family_members_with_points()
        family2 = mob2.family_members_with_points()
        for sm1, sm2 in zip(family1, family2):
            sm1.pointwise_become_partial(sm2, a, b)
        return self


class TracedPath(VMobject):
    CONFIG = {
        "stroke_width": 2,
        "stroke_color": WHITE,
        "min_distance_to_new_point": 0.1,
        "time_traced": np.inf,
        "fill_opacity": 0,
        "sparseness": 1,
    }

    def __init__(self, traced_point_func, **kwargs):
        super().__init__(**kwargs)
        self.traced_point_func = traced_point_func
        self.time = 0
        self.times = []
        self.traced_points = []
        self.add_updater(lambda m, dt: m.update_path(dt))

    def update_path(self, dt):
        point = np.array(self.traced_point_func())
        tps = self.traced_points
        times = self.times

        if len(tps) == 0:
            tps.append(point)
            times.append(self.time)
        if get_norm(point - tps[-1]) >= self.min_distance_to_new_point:
            times.append(self.time)
            tps.append(point)
        # Cut off tail
        while times and times[0] < self.time - self.time_traced:
            times = times[1:]
            tps = tps[1:]
        if tps:
            self.set_points_as_corners(tps[::self.sparseness])
        self.time += dt


class TracingTail(TracedPath):
    CONFIG = {
        "stroke_width": (0, 3),
        "stroke_opacity": (0, 1),
        "stroke_color": WHITE,
        "time_traced": 1.0,
        "min_distance_to_new_point": 0,
        "sparseness": 3,
    }

    def __init__(self, mobject_or_func, **kwargs):
        if isinstance(mobject_or_func, Mobject):
            func = mobject_or_func.get_center
        else:
            func = mobject_or_func
        super().__init__(func, **kwargs)
