import numpy as np
import itertools as it
import inspect
import copy
import warnings

from helpers import *

from animation import Animation
from simple_animations import DelayByOrder
from mobject import Mobject, Point

class Transform(Animation):
    DEFAULT_CONFIG = {
        "path_func" : straight_path,
        "should_black_out_extra_points" : False
    }
    def __init__(self, mobject, ending_mobject, **kwargs):
        mobject = instantiate(mobject)
        #Copy ending_mobject so as to not mess with caller
        ending_mobject = instantiate(ending_mobject).copy()
        digest_config(self, kwargs, locals())
        count1, count2 = mobject.get_num_points(), ending_mobject.get_num_points()
        if count2 == 0:
            ending_mobject.add_points(
                [mobject.get_center()],
                color = BLACK
            )
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
        families = map(
            Mobject.submobject_family,
            [self.mobject, self.starting_mobject, self.ending_mobject]
        )
        for m, start, end in zip(*families):
            # print m, start, end
            m.points = self.path_func(
                start.points, end.points, alpha
            )
            m.rgbs = straight_path(start.rgbs, end.rgbs, alpha)


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
        "path_func" : clockwise_path()
    }

class CounterclockwiseTransform(Transform):
    DEFAULT_CONFIG = {
        "path_func" : counterclockwise_path()
    }

class GrowFromCenter(Transform):
    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        point = Point(mobject.get_center())
        mobject.replace(point)
        mobject.highlight(point.get_color())
        Transform.__init__(self, mobject, target, **kwargs)

class SpinInFromNothing(GrowFromCenter):
    DEFAULT_CONFIG = {
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

class FadeOut(ApplyMethod):
    def __init__(self, mobject, **kwargs):
        ApplyMethod.__init__(self, mobject.fade, 1, **kwargs)

class FadeIn(Transform):
    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        mobject.fade(1)
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
    DEFAULT_CONFIG = {
        "in_place" : False,
    }
    def __init__(self, mobject, angle = np.pi, axis = OUT, **kwargs):
        kwargs["path_func"] = path_along_arc(angle)
        digest_config(self, kwargs, locals())
        if self.in_place:
            method = mobject.rotate_in_place
        else:
            method = mobject.rotate
        ApplyMethod.__init__(self, method, angle, axis, **kwargs)


class ApplyPointwiseFunction(ApplyMethod):
    DEFAULT_CONFIG = {
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



