from big_ol_pile_of_manim_imports import *

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
    }
    def construct(self):
        fractal = self.fractal_class(order = 0, **self.fractal_kwargs)
        self.play(FadeIn(fractal))
        for order in range(1, self.max_order+1):
            new_fractal = self.fractal_class(
                order = order,
                **self.fractal_kwargs
            )
            fractal.align_data(new_fractal)
            self.play(Transform(
                fractal, new_fractal,
                **self.transform_kwargs
            ))
            self.wait()
        self.wait()
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
        "max_order" : 6,
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
        self.wait()

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
        "max_order" : 6,
        "fractal_kwargs" : {
            "radius" : 6,
            "num_submobjects" : 100,
        },
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
    }

class SierpinskiFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : Sierpinski,
        "max_order" : 6,
        "fractal_kwargs" : {"height" : 6},
        "transform_kwargs" : {
            "path_arc" : 0,
        },
    }

class CircularFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : CircularFractal,
        "max_order" : 5,
        "fractal_kwargs" : {"height" : 6},
    }
    
