from __future__ import annotations

from manimlib.animation.composition import LaggedStart
from manimlib.animation.transform import Restore
from manimlib.constants import BLACK, WHITE
from manimlib.mobject.geometry import Circle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.config_ops import digest_config

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


class Broadcast(LaggedStart):
    CONFIG = {
        "small_radius": 0.0,
        "big_radius": 5,
        "n_circles": 5,
        "start_stroke_width": 8,
        "color": WHITE,
        "remover": True,
        "lag_ratio": 0.2,
        "run_time": 3,
    }

    def __init__(self, focal_point: np.ndarray, **kwargs):
        digest_config(self, kwargs)
        circles = VGroup()
        for x in range(self.n_circles):
            circle = Circle(
                radius=self.big_radius,
                stroke_color=BLACK,
                stroke_width=0,
            )
            circle.add_updater(
                lambda c: c.move_to(focal_point)
            )
            circle.save_state()
            circle.set_width(self.small_radius * 2)
            circle.set_stroke(self.color, self.start_stroke_width)
            circles.add(circle)
        animations = [
            Restore(circle)
            for circle in circles
        ]
        super().__init__(*animations, **kwargs)
