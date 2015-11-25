

from mobject import Mobject, Mobject1D
from scene import Scene
from animation.transform import Transform
from animation.simple_animations import ShowCreation
from topics.geometry import Line, Point

from helpers import *

def flip(points, axis, angle = np.pi):
    if axis is None:
        return points
    if isinstance(axis, tuple):
        axes = axis
    else:
        axes = [axis]
    for ax in axes:
        matrix = rotation_matrix(angle, ax)
        points = np.dot(points, np.transpose(matrix))
    return points


class SpaceFillingCurve(Mobject1D):
    DEFAULT_CONFIG = {
        "radius"      : 3,
        "order"       : 5,
        "start_color" : RED,
        "end_color"   : GREEN,
    }

    def generate_points(self):
        points = self.get_anchor_points()
        for pair in zip(points, points[1:]):
            self.add_line(*pair)
        self.gradient_highlight(self.start_color, self.end_color)

    def get_anchor_points(self):
        raise Exception("Not implemented")

class SelfSimilarSpaceFillingCurve(SpaceFillingCurve):
    DEFAULT_CONFIG = {
        "axis_offset_pairs" : [],
        "scale_factor" : 2,
        "radius_scale_factor" : 0.5,
    }
    def refine_into_subparts(self, points):
        transformed_copies = [
            flip(points/self.scale_factor, axis) + \
            offset*self.radius*self.radius_scale_factor
            for axis, offset in self.axis_offset_pairs
        ]
        return reduce(
            lambda a, b : np.append(a, b, axis = 0), 
            transformed_copies
        )

    def get_anchor_points(self):
        points = np.zeros((1, 3))
        for count in range(self.order):
            points = self.refine_into_subparts(
                points
            )
        return points



class HilbertCurve(SelfSimilarSpaceFillingCurve):
    DEFAULT_CONFIG = {
        "axis_offset_pairs" : [
            (RIGHT+UP,   LEFT+DOWN ),
            (None,       LEFT+UP   ),
            (None,       RIGHT+UP  ),
            (RIGHT+DOWN, RIGHT+DOWN),
        ],
    }

class HilbertCurve3D(SelfSimilarSpaceFillingCurve):
    DEFAULT_CONFIG = {
        "axis_offset_pairs" : [ #TODO
           (None, LEFT+DOWN+OUT),
           (None, LEFT+UP+OUT),
           (None, LEFT+UP+IN),
           (None, LEFT+DOWN+IN),
           (None, RIGHT+DOWN+IN),                                                
           (None, RIGHT+UP+IN),
           (None, RIGHT+UP+OUT),
           (None, RIGHT+DOWN+OUT),
        ],
    }

class PeanoCurve(SelfSimilarSpaceFillingCurve):
    DEFAULT_CONFIG = {
        "start_color" : PURPLE,
        "end_color"   : TEAL,
        "axis_offset_pairs" : [
            (None,     LEFT+DOWN ),
            (UP,       LEFT      ),
            (None,     LEFT+UP   ),
            (RIGHT,    UP        ),
            (LEFT+UP,  ORIGIN    ),
            (RIGHT,    DOWN      ),
            (None,     RIGHT+DOWN),
            (UP,       RIGHT     ),
            (None,     RIGHT+UP  ),
        ],
        "scale_factor" : 3,
        "radius_scale_factor" : 2.0/3,
    }

class TriangleFillingCurve(SelfSimilarSpaceFillingCurve):
    DEFAULT_CONFIG = {
        "start_color" : MAROON,
        "end_color"   : YELLOW,
        "axis_offset_pairs" : [
            (None,  LEFT/4.+DOWN/6.),
            (RIGHT, ORIGIN),
            (None,  RIGHT/4.+DOWN/6.),            
            (UP,    UP/3.),
        ],
        "scale_factor" : 2,
        "radius_scale_factor" : 1.5,
    }

class HexagonFillingCurve(SelfSimilarSpaceFillingCurve):
    DEFAULT_CONFIG = {
        "start_color" : WHITE,
        "end_color"   : BLUE_D,
        "axis_offset_pairs" : [
            (None,                1.5*DOWN + 0.5*np.sqrt(3)*LEFT),
            (UP+np.sqrt(3)*RIGHT, 1.5*DOWN + 0.5*np.sqrt(3)*RIGHT),
            (np.sqrt(3)*UP+RIGHT, ORIGIN),            
            ((UP, RIGHT),         np.sqrt(3)*LEFT),
            (None,                1.5*UP + 0.5*np.sqrt(3)*LEFT),
            (None,                1.5*UP + 0.5*np.sqrt(3)*RIGHT),
            (RIGHT,               np.sqrt(3)*RIGHT),
        ],
        "scale_factor" : 3,
        "radius_scale_factor" : 2/(3*np.sqrt(3)),
    }

    def refine_into_subparts(self, points):
        return SelfSimilarSpaceFillingCurve.refine_into_subparts(
            self,
            flip(points, IN, np.pi/6)
        )

class UtahFillingCurve(SelfSimilarSpaceFillingCurve):
    DEFAULT_CONFIG = {
        "start_color" : WHITE,
        "end_color"   : BLUE_D,
        "axis_offset_pairs" : [
            (None,                1.5*DOWN + 0.5*np.sqrt(3)*LEFT),
            (UP+np.sqrt(3)*RIGHT, 1.5*DOWN + 0.5*np.sqrt(3)*RIGHT),
            (np.sqrt(3)*UP+RIGHT, ORIGIN),            
            ((UP, RIGHT),         np.sqrt(3)*LEFT),
            (None,                1.5*UP + 0.5*np.sqrt(3)*LEFT),
            (None,                1.5*UP + 0.5*np.sqrt(3)*RIGHT),
            (RIGHT,               np.sqrt(3)*RIGHT),
        ],
        "scale_factor" : 3,
        "radius_scale_factor" : 2/(3*np.sqrt(3)),
    }


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
    @staticmethod
    def args_to_string(CurveClass, order):
        return CurveClass.__name__ + "Order" + str(order)

    @staticmethod
    def string_to_args(arg_str):
        curve_class_name, order_str = arg_str.split()
        space_filling_curves = dict([
            (Class.__name__, Class)
            for Class in get_all_descendent_classes(SpaceFillingCurve)
        ])
        if curve_class_name not in space_filling_curves:
            raise Exception(
                "%s is not a space filling curve"%curve_class_name
            )
        CurveClass = space_filling_curves[curve_class_name]
        return CurveClass, int(order_str)

class TransformOverIncreasingOrders(SpaceFillingCurveScene):
    def construct(self, CurveClass, max_order):
        sample = CurveClass(order = 1)
        curve = Line(sample.radius*LEFT, sample.radius*RIGHT)
        curve.gradient_highlight(
            sample.start_color, 
            sample.end_color
        )
        for order in range(1, max_order):
            new_curve = CurveClass(order = order)
            self.play(
                Transform(curve, new_curve),
                run_time = 3/np.sqrt(order),
            )
        self.dither()


class DrawSpaceFillingCurve(SpaceFillingCurveScene):
    def construct(self, CurveClass, order):
        curve = CurveClass(order = order)
        self.play(ShowCreation(curve), run_time = 10)
        self.dither()














