__all__ = ["MoveCar", "Broadcast"]


import operator as op

from ..animation.composition import LaggedStart
from ..animation.transform import ApplyMethod
from ..animation.transform import Restore
from ..constants import WHITE
from ..constants import BLACK
from ..mobject.geometry import Circle
from ..mobject.svg.drawings import Car
from ..mobject.types.vectorized_mobject import VGroup
from ..utils.config_ops import digest_config
from ..utils.space_ops import get_norm


class MoveCar(ApplyMethod):
    CONFIG = {
        "moving_forward": True,
        "run_time": 5,
    }

    def __init__(self, car, target_point, **kwargs):
        self.check_if_input_is_car(car)
        self.target_point = target_point
        super().__init__(car.move_to, target_point, **kwargs)

    def check_if_input_is_car(self, car):
        if not isinstance(car, Car):
            raise Exception("MoveCar must take in Car object")

    def begin(self):
        super().begin()
        car = self.mobject
        distance = get_norm(
            op.sub(
                self.target_mobject.get_right(),
                self.starting_mobject.get_right(),
            )
        )
        if not self.moving_forward:
            distance *= -1
        tire_radius = car.get_tires()[0].get_width() / 2
        self.total_tire_radians = -distance / tire_radius

    def interpolate_mobject(self, alpha):
        ApplyMethod.interpolate_mobject(self, alpha)
        if alpha == 0:
            return
        radians = alpha * self.total_tire_radians
        for tire in self.mobject.get_tires():
            tire.rotate_in_place(radians)


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
        "remover": True,
    }

    def __init__(self, focal_point, **kwargs):
        digest_config(self, kwargs)
        circles = VGroup()
        for x in range(self.n_circles):
            circle = Circle(
                radius=self.big_radius,
                stroke_color=BLACK,
                stroke_width=0,
            )
            circle.add_updater(lambda c: c.move_to(focal_point))
            circle.save_state()
            circle.set_width(self.small_radius * 2)
            circle.set_stroke(self.color, self.start_stroke_width)
            circles.add(circle)
        animations = [Restore(circle) for circle in circles]
        super().__init__(*animations, **kwargs)
