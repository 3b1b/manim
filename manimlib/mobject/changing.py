from manimlib.constants import *
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

        if self.back_and_forth and int(time) % 1 == 0:
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
    }

    def __init__(self, traced_point_func, **kwargs):
        super().__init__(**kwargs)
        self.traced_point_func = traced_point_func
        self.add_updater(lambda m: m.update_path())

    def update_path(self):
        new_point = self.traced_point_func()
        if self.has_no_points():
            self.start_new_path(new_point)
            self.add_line_to(new_point)
        else:
            # Set the end to be the new point
            self.points[-1] = new_point

            # Second to last point
            nppcc = self.n_points_per_cubic_curve
            dist = get_norm(new_point - self.points[-nppcc])
            if dist >= self.min_distance_to_new_point:
                self.add_line_to(new_point)
