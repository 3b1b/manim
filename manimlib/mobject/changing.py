import warnings

from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.rate_functions import smooth

POINTLESS_VMOBJECT_WARNING = """

Calling AnimatedBoundary on a VMobject with no points.
"""


class AnimatedBoundary(VGroup):
    CONFIG = {
        "colors": [BLUE_D, BLUE_B, BLUE_E, GREY_BROWN],
        "max_stroke_width": 3,
        "cycle_rate": 0.5,
    }

    def __init__(self, vmobject, **kwargs):
        super().__init__(**kwargs)
        if len(vmobject.points) == 0:
            warnings.warn(POINTLESS_VMOBJECT_WARNING)
        self.vmobject = vmobject
        self.boundary_copies = [
            VMobject(stroke_width=0, fill_opacity=0)
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

        index = int(time % len(colors))
        alpha = smooth(time % 1)

        if int(time) % 2 == 0:
            bounds = (0, alpha)
        else:
            bounds = (1 - alpha, 1)
        growing.pointwise_become_partial(self.vmobject, *bounds)
        growing.set_stroke(colors[index], width=msw)

        if time > 1:
            fading.pointwise_become_partial(self.vmobject, 0, 1)
            fading.set_stroke(
                color=colors[index - 1],
                width=(1 - alpha) * msw
            )

        self.total_time += dt
