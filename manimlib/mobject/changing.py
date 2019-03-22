from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.rate_functions import smooth


class AnimatedBoundary(VGroup):
    CONFIG = {
        "colors": [BLUE_D, BLUE_B, BLUE_E, GREY_BROWN],
        "max_stroke_width": 3,
        "cycle_rate": 0.5,
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
        self.add_updater(lambda m, dt: self.update(dt))

    def update(self, dt):
        # Not actual time, but something which passes at
        # an altered rate to make the implementation below
        # cleaner
        time = self.total_time * self.cycle_rate
        growing, fading = self.boundary_copies
        colors = self.colors
        msw = self.max_stroke_width
        vmobject = self.vmobject

        index = int(time % len(colors))
        alpha = smooth(time % 1)

        if int(time) % 2 == 0:
            bounds = (0, alpha)
        else:
            bounds = (1 - alpha, 1)
        self.full_family_become_partial(growing, vmobject, *bounds)
        growing.set_stroke(colors[index], width=msw)

        if time >= 1:
            self.full_family_become_partial(fading, vmobject, 0, 1)
            fading.set_stroke(
                color=colors[index - 1],
                width=(1 - alpha) * msw
            )

        self.total_time += dt

    def full_family_become_partial(self, mob1, mob2, a, b):
        family1 = mob1.family_members_with_points()
        family2 = mob2.family_members_with_points()
        for sm1, sm2 in zip(family1, family2):
            sm1.pointwise_become_partial(sm2, a, b)
        return self
