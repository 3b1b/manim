import numpy as np
import itertools as it
import inspect
import copy
import warnings

from animation import Animation
from mobject import Mobject, Point
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
    def __init__(self, mobject1, mobject2, 
                 run_time = DEFAULT_TRANSFORM_RUN_TIME,
                 interpolation_function = straight_path,
                 black_out_extra_points = False,
                 *args, **kwargs):
        self.interpolation_function = interpolation_function
        count1, count2 = mobject1.get_num_points(), mobject2.get_num_points()
        if count2 == 0:
            mobject2.add_points([SPACE_WIDTH*RIGHT+SPACE_HEIGHT*UP])
            count2 = mobject2.get_num_points()
        Mobject.align_data(mobject1, mobject2)
        self.ending_mobject = mobject2
        if black_out_extra_points and count2 < count1:
            self.black_out_extra_points(count1, count2)

        Animation.__init__(self, mobject1, run_time = run_time, *args, **kwargs)                
        self.name += "To" + str(mobject2)  
        self.mobject.SHOULD_BUFF_POINTS = \
            mobject1.SHOULD_BUFF_POINTS and mobject2.SHOULD_BUFF_POINTS

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
    def __init__(self, mobject1, mobject2, **kwargs):
        Transform.__init__(
            self, mobject1, mobject2, 
            interpolation_function = clockwise_path, **kwargs
        )

class CounterclockwiseTransform(Transform):
    def __init__(self, mobject1, mobject2, **kwargs):
        Transform.__init__(
            self, mobject1, mobject2, 
            interpolation_function = counterclockwise_path, **kwargs
        )

class SpinInFromNothing(Transform):
    def __init__(self, mob, **kwargs):
        name = "interpolation_function"
        interp_func = kwargs[name] if name in kwargs else counterclockwise_path
        dot = Point(mob.get_center(), color = "black")
        Transform.__init__(
            self, dot, mob, 
            interpolation_function = interp_func, 
            **kwargs
        )
        

class FadeToColor(Transform):
    def __init__(self, mobject, color, *args, **kwargs):
        target = copy.deepcopy(mobject).highlight(color)
        Transform.__init__(self, mobject, target, *args, **kwargs)

class Highlight(FadeToColor):
    def __init__(self, mobject, color = "red",
                 run_time = DEFAULT_ANIMATION_RUN_TIME, 
                 alpha_func = there_and_back, *args, **kwargs):
        FadeToColor.__init__(
            self, mobject, color, 
            run_time = run_time, 
            alpha_func = alpha_func, 
            *args, **kwargs
        )

class ScaleInPlace(Transform):
    def __init__(self, mobject, scale_factor, *args, **kwargs):
        target = copy.deepcopy(mobject)
        center = mobject.get_center()
        target.shift(-center).scale(scale_factor).shift(center)
        Transform.__init__(self, mobject, target, *args, **kwargs)

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

class ApplyFunction(Transform):
    def __init__(self, function, mobject, **kwargs):
        Transform.__init__(
            self, 
            mobject, 
            function(copy.deepcopy(mobject)),
            **kwargs
        )
        self.name = "ApplyFunctionTo"+str(mobject)


class ApplyPointwiseFunction(Transform):
    def __init__(self, function, mobject, 
                 run_time = DEFAULT_ANIMATION_RUN_TIME, **kwargs):
        map_image = copy.deepcopy(mobject)
        map_image.points = np.array(map(function, map_image.points))
        Transform.__init__(
            self, mobject, map_image, 
            run_time = run_time, **kwargs
        )
        self.name = "".join([
            "Apply",
            "".join([s.capitalize() for s in function.__name__.split("_")]),
            "To" + str(mobject)
        ])

class ComplexFunction(ApplyPointwiseFunction):
    def __init__(self, function, *args, **kwargs):
        def point_map(point):
            x, y, z = point
            c = np.complex(x, y)
            c = function(c)
            return c.real, c.imag, z
        if len(args) > 0:
            args = list(args)
            mobject = args.pop(0)
        elif "mobject" in kwargs:
            mobject = kwargs.pop("mobject")
        else:
            mobject = Grid()
        ApplyPointwiseFunction.__init__(self, point_map, mobject, *args, **kwargs)
        self.name = "ComplexFunction" + to_cammel_case(function.__name__)
        #Todo, abstract away function naming'


class TransformAnimations(Transform):
    def __init__(self, start_anim, end_anim, 
                 alpha_func = squish_alpha_func(smooth),
                 **kwargs):
        if "run_time" in kwargs:
            run_time = kwargs.pop("run_time")
            for anim in start_anim, end_anim:
                anim.set_run_time(run_time)
        self.start_anim, self.end_anim = start_anim, end_anim
        Transform.__init__(
            self,
            start_anim.mobject,
            end_anim.mobject,
            run_time = max(start_anim.run_time, end_anim.run_time),
            alpha_func = alpha_func,
            **kwargs
        )
        #Rewire starting and ending mobjects
        start_anim.mobject = self.starting_mobject
        end_anim.mobject = self.ending_mobject

    def update(self, alpha):
        self.start_anim.update(alpha)
        self.end_anim.update(alpha)
        Transform.update(self, alpha)





