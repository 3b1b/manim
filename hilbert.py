from mobject import Mobject, Mobject1D
from scene import Scene
from animation.transform import Transform
from animation.simple_animations import ShowCreation
from topics.geometry import Line, Point

from helpers import *

def flip_over_slope_1(points):
    return points[:,[1, 0 , 2]]

def flip_over_slope_neg_1(points):
    return -points[:,[1, 0, 2]]

def hilbertification(points, radius=3):
    transformed_copies = [
        flip(points/2) + offset*radius/2.0
        for flip, offset in [
            (flip_over_slope_1,     (LEFT+DOWN)),
            (lambda x : x,          (LEFT+UP)),
            (lambda x : x,          (RIGHT+UP)),
            (flip_over_slope_neg_1, (RIGHT+DOWN)),
        ]
    ]
    return reduce(
        lambda a, b : np.append(a, b, axis = 0), 
        transformed_copies
    )



class SpaceFillingCurve(Mobject1D):
    DEFAULT_CONFIG = {
        "radius"      : 3,
        "order"       : 5,
        "start_color" : RED,
        "end_color"   : GREEN,
    }

    def generate_points(self):
        points = self.get_anchor_points(self.order)
        for pair in zip(points, points[1:]):
            self.add_line(*pair, min_density = 0.01)
        self.gradient_highlight(self.start_color, self.end_color)

    def get_anchor_points(self, order):
        """
        To be filled out in subclasses
        """
        return []


class HilbertCurve(SpaceFillingCurve):
    def get_anchor_points(self, order):
        points = np.zeros((1, 3))
        for count in range(order):
            points = hilbertification(points)
        return points

class HilbertCurve3D(SpaceFillingCurve):
    def get_anchor_points(self, order):
        pass

class SnakeCurve(SpaceFillingCurve):
    DEFAULT_CONFIG = {
        "start_color" : BLUE,
        "end_color"   : YELLOW,
    }
    def get_anchor_points(self, order):
        result = []
        lower_left = ORIGIN + \
                     LEFT*self.radius + \
                     DOWN*self.radius
        step = 2.0*self.radius / (order)
        for y in range(order+1):
            x_range = range(order+1)
            if y%2 == 0:
                x_range.reverse()
            for x in x_range:
                result.append(
                    lower_left + x*step*RIGHT + y*step*UP
                )
        return result


class SpaceFillingCurveScene(Scene):
    DEFAULT_CONFIG = {
        "curve_class" : None #Must be filled in in subclasses
    }        
    @staticmethod
    def args_to_string(max_order):
        return str(max_order)

    @staticmethod
    def string_to_args(num_str):
        return int(num_str)

class SpaceFillingCurveGrowingOrder(SpaceFillingCurveScene):
    def construct(self, max_order):
        sample = self.curve_class(order = 1)
        curve = Line(sample.radius*LEFT, sample.radius*RIGHT)
        curve.gradient_highlight(
            sample.start_color, 
            sample.end_color
        )
        for order in range(1, max_order):
            new_curve = self.curve_class(order = order)
            self.play(
                Transform(curve, new_curve),
                run_time = 3/np.sqrt(order),
            )
        self.dither()


class HilbertCurveGrowingOrder(SpaceFillingCurveGrowingOrder):
    DEFAULT_CONFIG = {
        "curve_class" : HilbertCurve,
    }   

class SnakeCurveGrowingOrder(SpaceFillingCurveGrowingOrder):
    DEFAULT_CONFIG = {
        "curve_class" : SnakeCurve,
    }      


class DrawSpaceFillingCurve(SpaceFillingCurveScene):
    def construct(self, order):
        curve = self.curve_class(order = order)
        self.play(ShowCreation(curve), run_time = 10)
        self.dither()

class DrawHilbertCurve(DrawSpaceFillingCurve):
    DEFAULT_CONFIG = {
        "curve_class" : HilbertCurve,
    }   

class DrawSnakeCurve(DrawSpaceFillingCurve):
    DEFAULT_CONFIG = {
        "curve_class" : SnakeCurve,
    }















