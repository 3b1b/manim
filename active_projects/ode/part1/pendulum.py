from big_ol_pile_of_manim_imports import *


class Pendulum(VGroup):
    CONFIG = {
        "length": 3,
        "gravity": 9.8,
        "weight_diameter": 0.5,
        "rod_style": {
            "stroke_width": 2,
            "stroke_color": LIGHT_GREY,
        },
        "weight_style": {
            "stroke_width": 0,
            "fill_opacity": 1,
            "fill_color": LIGHT_GREY,
            "sheen_direction": UL,
            "sheen_factor": 0.5,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_rod()

    def create_rod(self):
        pass

    def create_weight(self):
        pass

    def get_theta(self):
        pass

    def set_theta(self):
        pass

    def get_angular_velocity(self):
        pass

    def set_angular_velocity(self):
        pass

    def get_fixed_point(self):
        pass


class PendulumTest(Scene):
    def construct(self):
        pass
