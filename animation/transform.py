import numpy as np
import itertools as it
import inspect
import copy
import warnings

from helpers import *

from animation import Animation
from mobject import Mobject, Point

class Transform(Animation):
    DEFAULT_CONFIG = {
        "interpolation_function" : straight_path,
        "should_black_out_extra_points" : False
    }
    def __init__(self, mobject, ending_mobject, **kwargs):
        mobject, ending_mobject = map(instantiate, [mobject, ending_mobject])
        digest_config(self, kwargs, locals())
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
        families = map(
            Mobject.get_full_submobject_family,
            [self.mobject, self.starting_mobject, self.ending_mobject]
        )
        for m, start, end in zip(*families):
            # print m, start, end
            m.points = self.interpolation_function(
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
        "interpolation_function" : clockwise_path()
    }

class CounterclockwiseTransform(Transform):
    DEFAULT_CONFIG = {
        "interpolation_function" : counterclockwise_path()
    }

class SpinInFromNothing(Transform):
    DEFAULT_CONFIG = {
        "interpolation_function" : counterclockwise_path()
    }
    def __init__(self, mob, **kwargs):
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

class Rotate(ApplyMethod):
    def __init__(self, mobject, angle = np.pi, **kwargs):
        kwargs["interpolation_function"] = path_along_arc(angle)
        ApplyMethod.__init__(self, mobject.rotate, angle, **kwargs)


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






