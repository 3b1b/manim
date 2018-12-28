from manimlib.animation.composition import LaggedStart
from manimlib.animation.transform import ApplyMethod
from manimlib.constants import *
from manimlib.mobject.geometry import Circle
from manimlib.mobject.svg.drawings import Car
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import get_norm


class MoveCar(ApplyMethod):
    CONFIG = {
        "moving_forward": True,
    }

    def __init__(self, car, target_point, **kwargs):
        assert isinstance(car, Car)
        ApplyMethod.__init__(self, car.move_to, target_point, **kwargs)
        displacement = self.target_mobject.get_right() - self.starting_mobject.get_right()
        distance = get_norm(displacement)
        if not self.moving_forward:
            distance *= -1
        tire_radius = car.get_tires()[0].get_width() / 2
        self.total_tire_radians = -distance / tire_radius

    def update_mobject(self, alpha):
        ApplyMethod.update_mobject(self, alpha)
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
        "lag_ratio": 0.7,
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
            circle.move_to(focal_point)
            circle.save_state()
            circle.set_width(self.small_radius * 2)
            circle.set_stroke(self.color, self.start_stroke_width)
            circles.add(circle)
        LaggedStart.__init__(
            self, ApplyMethod, circles,
            lambda c: (c.restore,),
            **kwargs
        )
