import numpy as np
import itertools as it
import inspect
import copy
import warnings

from animation import Animation
from mobject import Mobject, Point, ComplexPlane
from constants import *
from helpers import *

def straight_path(start_points, end_points, alpha):
    return (1-alpha)*start_points + alpha*end_points

def path_along_arc(arc_angle):
    """
    If vect is vector from start to end, [vect[:,1], -vect[:,0]] is 
    perpendicualr to vect in the left direction.
    """
    if arc_angle == 0:
        return straight_path
    def path(start_points, end_points, alpha):
        vects = end_points - start_points
        centers = start_points + 0.5*vects
        if arc_angle != np.pi:
            for i, b in [(0, -1), (1, 1)]:
                centers[:,i] += 0.5*b*vects[:,1-i]/np.tan(arc_angle/2)
        return centers + np.dot(
            start_points-centers, 
            np.transpose(rotation_about_z(alpha*arc_angle))
        )
    return path

def clockwise_path():
    return path_along_arc(np.pi)

def counterclockwise_path():
    return path_along_arc(-np.pi)


class Transform(Animation):
    DEFAULT_CONFIG = {
        "interpolation_function" : straight_path,
        "should_black_out_extra_points" : False
    }
    def __init__(self, mobject, ending_mobject, **kwargs):
        mobject, ending_mobject = map(instantiate, [mobject, ending_mobject])
        digest_config(self, Transform, kwargs, locals())
        count1, count2 = mobject.get_num_points(), ending_mobject.get_num_points()
        if count2 == 0:
            ending_mobject.add_points([SPACE_WIDTH*RIGHT+SPACE_HEIGHT*UP])
            count2 = ending_mobject.get_num_points()
        Mobject.align_data(mobject, ending_mobject)
        if self.should_black_out_extra_points and count2 < count1:
            self.black_out_extra_points(count1, count2)

        Animation.__init__(self, mobject, **kwargs)
        self.name += "To" + str(ending_mobject)  
        self.mobject.point_thickness = ending_mobject.point_thickness


    def black_out_extra_points(self, count1, count2):
        #Ensure redundant pixels fade to black
        indices = np.arange(
            0, count1-1, float(count1) / count2
        ).astype('int')
        temp = np.zeros(self.ending_mobject.points.shape)
        temp[indices] = self.ending_mobject.rgbs[indices]
        self.ending_mobject.rgbs = temp
        self.non_redundant_m2_indices = indices

    def update_mobject(self, alpha):
        self.mobject.points = self.interpolation_function(
            self.starting_mobject.points,
            self.ending_mobject.points,
            alpha
        )
        self.mobject.rgbs = straight_path(
            self.starting_mobject.rgbs,
            self.ending_mobject.rgbs,
            alpha
        )

    def clean_up(self):
        Animation.clean_up(self)
        if hasattr(self, "non_redundant_m2_indices"):
            #Reduce mobject (which has become identical to mobject2), as
            #well as mobject2 itself
            for mobject in [self.mobject, self.ending_mobject]:
                for attr in ['points', 'rgbs']:
                    setattr(
                        mobject, attr, 
                        getattr(
                            self.ending_mobject, 
                            attr
                        )[self.non_redundant_m2_indices]
                    )

class ClockwiseTransform(Transform):
    DEFAULT_CONFIG = {
        "interpolation_function" : clockwise_path()
    }
    def __init__(self, *args, **kwargs):
        digest_config(self, ClockwiseTransform, kwargs)
        Transform.__init__(self, *args, **kwargs)

class CounterclockwiseTransform(Transform):
    DEFAULT_CONFIG = {
        "interpolation_function" : counterclockwise_path()
    }
    def __init__(self, *args, **kwargs):
        digest_config(self, ClockwiseTransform, kwargs)
        Transform.__init__(self, *args, **kwargs)

class SpinInFromNothing(Transform):
    DEFAULT_CONFIG = {
        "interpolation_function" : counterclockwise_path()
    }
    def __init__(self, mob, **kwargs):
        digest_config(self, SpinInFromNothing, kwargs)
        Transform.__init__(self, Point(mob.get_center()), mob, **kwargs)

class ApplyMethod(Transform):
    def __init__(self, method, *args, **kwargs):
        """
        Method is a method of Mobject.  *args is for the method,
        **kwargs is for the transform itself.

        Relies on the fact that mobject methods return the mobject
        """
        assert(inspect.ismethod(method))
        assert(isinstance(method.im_self, Mobject))
        Transform.__init__(
            self,
            method.im_self,
            copy.deepcopy(method)(*args),
            **kwargs
        )

class ApplyPointwiseFunction(ApplyMethod):
    DEFAULT_CONFIG = {
        "run_time" : DEFAULT_POINTWISE_FUNCTION_RUN_TIME
    }
    def __init__(self, function, mobject, **kwargs):
        digest_config(self, ApplyPointwiseFunction, kwargs)
        ApplyMethod.__init__(
            self, mobject.apply_function, function, **kwargs
        )


class ComplexFunction(ApplyPointwiseFunction):
    def __init__(self, function, mobject = ComplexPlane, **kwargs):
        if "interpolation_function" not in kwargs:
            self.interpolation_function = path_along_arc(
                np.log(function(complex(1))).imag
            )
        ApplyPointwiseFunction.__init__(
            self,
            lambda (x, y, z) : complex_to_R3(function(complex(x, y))),
            instantiate(mobject),
            **kwargs
        )

class FadeToColor(ApplyMethod):
    def __init__(self, mobject, color, **kwargs):
        ApplyMethod.__init__(self, mobject.highlight, color, **kwargs)

class ScaleInPlace(ApplyMethod):
    def __init__(self, mobject, scale_factor, **kwargs):
        ApplyMethod.__init__(self, mobject.scale_in_place, scale_factor, **kwargs)

class ApplyFunction(Transform):
    def __init__(self, function, mobject, **kwargs):
        Transform.__init__(
            self, 
            mobject, 
            function(copy.deepcopy(mobject)),
            **kwargs
        )
        self.name = "ApplyFunctionTo"+str(mobject)

class ApplyMatrix(Animation):
    #Truth be told, I'm not sure if this is useful.
    def __init__(self, matrix, mobject, **kwargs):
        matrix = np.array(matrix)
        if matrix.shape == (2, 2):
            self.matrix = np.identity(3)
            self.matrix[:2, :2] = matrix
        elif matrix.shape == (3, 3):
            self.matrix = matrix
        else:
            raise "Matrix has bad dimensions"
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        matrix = interpolate(np.identity(3), self.matrix, alpha)
        self.mobject.points = np.dot(
            self.starting_mobject.points, 
            np.transpose(matrix)
        )


class TransformAnimations(Transform):
    DEFAULT_CONFIG = {
        "alpha_func" : squish_alpha_func(smooth)
    }
    def __init__(self, start_anim, end_anim, **kwargs):
        digest_config(self, TransformAnimations, kwargs, locals())
        if "run_time" in kwargs:
            self.run_time = kwargs.pop("run_time")
        else:
            self.run_time = max(start_anim.run_time, end_anim.run_time)
        for anim in start_anim, end_anim:
            anim.set_run_time(self.run_time)

        if start_anim.starting_mobject.get_num_points() != end_anim.starting_mobject.get_num_points():
            Mobject.align_data(start_anim.starting_mobject, end_anim.starting_mobject)
            for anim in start_anim, end_anim:
                if hasattr(anim, "ending_mobject"):
                    Mobject.align_data(anim.starting_mobject, anim.ending_mobject)

        Transform.__init__(self, start_anim.mobject, end_anim.mobject, **kwargs)
        #Rewire starting and ending mobjects
        start_anim.mobject = self.starting_mobject
        end_anim.mobject = self.ending_mobject

    def update(self, alpha):
        self.start_anim.update(alpha)
        self.end_anim.update(alpha)
        Transform.update(self, alpha)





