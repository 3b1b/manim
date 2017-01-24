from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

class FractalCreation(Scene):
    CONFIG = {
        "fractal_class" : PentagonalFractal,
        "max_order" : 5,
        "transform_kwargs" : {
            "path_arc" : np.pi/6,
            "submobject_mode" : "lagged_start",
            "run_time" : 2,
        },
        "fractal_kwargs" : {},
        "modify_stroke_width" : True,
    }
    def construct(self):
        fractal = self.fractal_class(order = 0, **self.fractal_kwargs)
        self.play(FadeIn(fractal))
        for order in range(1, self.max_order+1):
            new_fractal = self.fractal_class(
                order = order,
                **self.fractal_kwargs
            )
            if self.modify_stroke_width:
                smallest = new_fractal.family_members_with_points()[0]
                if smallest.get_width() < 0.25:
                    new_fractal.set_stroke(width = 2)
                if smallest.get_width() < 0.1:
                    new_fractal.set_stroke(width = 1)
            self.play(Transform(
                fractal, new_fractal,
                **self.transform_kwargs
            ))
            self.dither()
        self.dither()
        self.fractal = fractal

class PentagonalFractalCreation(FractalCreation):
    pass

class DiamondFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : DiamondFractal,
        "max_order" : 6,
        "fractal_kwargs" : {"height" : 6}
    }


class PiCreatureFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : PiCreatureFractal,
        "max_order" : 5,
        "fractal_kwargs" : {"height" : 6},
        "transform_kwargs" : {
            "submobject_mode" : "all_at_once",
            "run_time" : 2,
        },
    }
    def construct(self):
        FractalCreation.construct(self)
        fractal = self.fractal
        smallest_pi = fractal[0][0]
        zoom_factor = 0.1/smallest_pi.get_height()
        fractal.generate_target()
        fractal.target.shift(-smallest_pi.get_corner(UP+LEFT))
        fractal.target.scale(zoom_factor)
        self.play(MoveToTarget(fractal, run_time = 10))
        self.dither()

class QuadraticKochFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : QuadraticKoch,
        "max_order" : 5,
        "fractal_kwargs" : {"radius" : 10},
        # "transform_kwargs" : {
        #     "submobject_mode" : "all_at_once",
        #     "run_time" : 2,
        # },
    }

class KochSnowFlakeFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : KochSnowFlake,
        "max_order" : 5,
        "fractal_kwargs" : {"radius" : 6},
        "transform_kwargs" : {
            "submobject_mode" : "lagged_start",
            "path_arc" : np.pi/6,
            "run_time" : 2,
        },
    }


class WonkyHexagonFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : WonkyHexagonFractal,
        "max_order" : 5,
        "fractal_kwargs" : {"height" : 6},
        "transform_kwargs" : {
            "submobject_mode" : "lagged_start",
            "path_arc" : np.pi/6,
            "run_time" : 2,
        },
    }










































