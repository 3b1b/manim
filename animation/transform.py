import numpy as np
import itertools as it
import inspect
import copy
import warnings

from helpers import *

from animation import Animation
from simple_animations import DelayByOrder
from mobject import Mobject, Point, VMobject

class Transform(Animation):
    CONFIG = {
        "path_arc" : 0,
        "path_func" : None,
    }
    def __init__(self, mobject, ending_mobject, **kwargs):
        #Copy ending_mobject so as to not mess with caller
        ending_mobject = ending_mobject.copy()
        digest_config(self, kwargs, locals())
        mobject.align_data(ending_mobject)
        self.init_path_func()

        Animation.__init__(self, mobject, **kwargs)
        self.name += "To" + str(ending_mobject)  
        self.mobject.stroke_width = ending_mobject.stroke_width

    def init_path_func(self):
        if self.path_func is not None:
            return
        if self.path_arc == 0:
            self.path_func = straight_path
        else:
            self.path_func = path_along_arc(self.path_arc)


    def update_mobject(self, alpha):
        families = map(
            Mobject.submobject_family,
            [self.mobject, self.starting_mobject, self.ending_mobject]
        )
        for m, start, end in zip(*families):
            m.interpolate(start, end, alpha, self.path_func)


class ClockwiseTransform(Transform):
    CONFIG = {
        "path_arc" : -np.pi
    }

class CounterclockwiseTransform(Transform):
    CONFIG = {
        "path_arc" : np.pi
    }

class GrowFromCenter(Transform):
    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        point = Point(mobject.get_center())
        mobject.replace(point)
        mobject.highlight(point.get_color())
        Transform.__init__(self, mobject, target, **kwargs)

class SpinInFromNothing(GrowFromCenter):
    CONFIG = {
        "path_func" : counterclockwise_path()
    }

class ShrinkToCenter(Transform):
    def __init__(self, mobject, **kwargs):
        Transform.__init__(
            self, mobject,
            Point(mobject.get_center()), 
            **kwargs
        )

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

class FadeOut(Transform):
    CONFIG = {
        "remover" : True, 
    }
    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        target.fade(1)
        if isinstance(mobject, VMobject):
            target.set_stroke(width = 0)
            target.set_fill(opacity = 0)
        Transform.__init__(self, mobject, target, **kwargs)

    def clean_up(self):
        self.update(0)

class FadeIn(Transform):
    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        mobject.fade(1)
        if isinstance(mobject, VMobject):
            mobject.set_stroke(width = 0)
        Transform.__init__(self, mobject, target, **kwargs)
        # self.mobject.rgbs = self.starting_mobject.rgbs * alpha
        # if self.mobject.points.shape != self.starting_mobject.points.shape:
        #     self.mobject.points = self.starting_mobject.points
        #     #TODO, Why do you need to do this? Shouldn't points always align?

class ShimmerIn(DelayByOrder):
    def __init__(self, mobject, **kwargs):
        mobject.sort_points(lambda p : np.dot(p, DOWN+RIGHT))
        DelayByOrder.__init__(self, FadeIn(mobject, **kwargs))


class Rotate(ApplyMethod):
    CONFIG = {
        "in_place" : False,
    }
    def __init__(self, mobject, angle = np.pi, axis = OUT, **kwargs):
        kwargs["path_arc"] = angle
        digest_config(self, kwargs, locals())
        if self.in_place:
            method = mobject.rotate_in_place
        else:
            method = mobject.rotate
        ApplyMethod.__init__(self, method, angle, axis, **kwargs)


class ApplyPointwiseFunction(ApplyMethod):
    CONFIG = {
        "run_time" : DEFAULT_POINTWISE_FUNCTION_RUN_TIME
    }
    def __init__(self, function, mobject, **kwargs):
        ApplyMethod.__init__(
            self, mobject.apply_function, function, **kwargs
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
            function(mobject.copy()),
            **kwargs
        )
        self.name = "ApplyFunctionTo"+str(mobject)

class ApplyMatrix(ApplyPointwiseFunction):
    #Truth be told, I'm not sure if this is useful.
    def __init__(self, matrix, mobject, **kwargs):
        matrix = np.array(matrix)
        if matrix.shape == (2, 2):
            new_matrix = np.identity(3)
            new_matrix[:2, :2] = matrix
            matrix = new_matrix
        elif matrix.shape != (3, 3):
            raise "Matrix has bad dimensions"
        transpose = np.transpose(matrix)
        def func(p):
            return np.dot(p, transpose)
        ApplyPointwiseFunction.__init__(self, func, mobject, **kwargs)


class TransformAnimations(Transform):
    CONFIG = {
        "rate_func" : squish_rate_func(smooth)
    }
    def __init__(self, start_anim, end_anim, **kwargs):
        digest_config(self, kwargs, locals())
        if "run_time" in kwargs:
            self.run_time = kwargs.pop("run_time")
        else:
            self.run_time = max(start_anim.run_time, end_anim.run_time)
        for anim in start_anim, end_anim:
            anim.set_run_time(self.run_time)
            
        if start_anim.starting_mobject.get_num_points() != end_anim.starting_mobject.get_num_points():
            start_anim.starting_mobject.align_data(end_anim.starting_mobject)
            for anim in start_anim, end_anim:
                if hasattr(anim, "ending_mobject"):
                    anim.starting_mobject.align_data(anim.ending_mobject)

        Transform.__init__(self, start_anim.mobject, end_anim.mobject, **kwargs)
        #Rewire starting and ending mobjects
        start_anim.mobject = self.starting_mobject
        end_anim.mobject = self.ending_mobject

    def update(self, alpha):
        self.start_anim.update(alpha)
        self.end_anim.update(alpha)
        Transform.update(self, alpha)



