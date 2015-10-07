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

def semi_circular_path(start_points, end_points, alpha, axis):
    midpoints = (start_points + end_points) / 2
    angle = alpha * np.pi
    rot_matrix = rotation_matrix(angle, axis)[:2, :2]
    result = np.zeros(start_points.shape)
    result[:,:2] = np.dot(
        (start_points - midpoints)[:,:2], 
        np.transpose(rot_matrix)
    ) + midpoints[:,:2]
    result[:,2] = (1-alpha)*start_points[:,2] + alpha*end_points[:,2]
    return result

def clockwise_path(start_points, end_points, alpha):
    return semi_circular_path(start_points, end_points, alpha, IN)

def counterclockwise_path(start_points, end_points, alpha):
    return semi_circular_path(start_points, end_points, alpha, OUT)

class Transform(Animation):
    DEFAULT_CONFIG = {
        "run_time" : DEFAULT_TRANSFORM_RUN_TIME,
        "interpolation_function" : straight_path,
        "should_black_out_extra_points" : False
    }
    def __init__(self, mobject, ending_mobject, **kwargs):
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
        self.mobject.should_buffer_points = \
            mobject.should_buffer_points and ending_mobject.should_buffer_points

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
        "interpolation_function" : clockwise_path
    }
    def __init__(self, *args, **kwargs):
        digest_config(self, ClockwiseTransform, kwargs)
        Transform.__init__(self, *args, **kwargs)

class CounterclockwiseTransform(Transform):
    DEFAULT_CONFIG = {
        "interpolation_function" : counterclockwise_path
    }
    def __init__(self, *args, **kwargs):
        digest_config(self, ClockwiseTransform, kwargs)
        Transform.__init__(self, *args, **kwargs)

class SpinInFromNothing(Transform):
    DEFAULT_CONFIG = {
        "interpolation_function" : counterclockwise_path
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
        if not inspect.ismethod(method) or \
           not isinstance(method.im_self, Mobject):
            raise "Not a valid Mobject method"
        Transform.__init__(
            self,
            method.im_self,
            copy.deepcopy(method)(*args),
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

class ApplyPointwiseFunction(Transform):
    DEFAULT_CONFIG = {
        "run_time" : DEFAULT_ANIMATION_RUN_TIME
    }
    def __init__(self, function, mobject, **kwargs):
        digest_config(self, ApplyPointwiseFunction, kwargs)
        map_image = copy.deepcopy(mobject)
        map_image.points = np.array(map(function, map_image.points))
        Transform.__init__(self, mobject, map_image, **kwargs)
        self.name = "".join([
            "Apply",
            "".join([s.capitalize() for s in function.__name__.split("_")]),
            "To" + str(mobject)
        ])

class ComplexFunction(ApplyPointwiseFunction):
    def __init__(self, function, mobject = ComplexPlane, **kwargs):
        def point_map(point):
            x, y, z = point
            c = np.complex(x, y)
            c = function(c)
            return c.real, c.imag, z
        ApplyPointwiseFunction.__init__(self, mobject, point_map, *args, **kwargs)
        self.name = "ComplexFunction" + to_cammel_case(function.__name__)
        #Todo, abstract away function naming'


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





