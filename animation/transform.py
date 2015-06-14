import numpy as np
import itertools as it
import inspect
import copy
import warnings

from animation import Animation
from mobject import Mobject
from constants import *
from helpers import *

class Transform(Animation):
    def __init__(self, mobject1, mobject2, 
                 run_time = DEFAULT_TRANSFORM_RUN_TIME,
                 black_out_extra_points = True,
                 *args, **kwargs):
        count1, count2 = mobject1.get_num_points(), mobject2.get_num_points()
        if count2 == 0:
            mobject2 = Point((SPACE_WIDTH, SPACE_HEIGHT, 0))
            count2 = mobject2.get_num_points()
        Mobject.align_data(mobject1, mobject2)
        Animation.__init__(self, mobject1, run_time = run_time, *args, **kwargs)
        self.ending_mobject = mobject2
        self.mobject.SHOULD_BUFF_POINTS = \
            mobject1.SHOULD_BUFF_POINTS and mobject2.SHOULD_BUFF_POINTS
        self.reference_mobjects.append(mobject2)
        self.name += "To" + str(mobject2)

        if black_out_extra_points and count2 < count1:
            #Ensure redundant pixels fade to black
            indices = np.arange(
                0, count1-1, float(count1) / count2
            ).astype('int')
            temp = np.zeros(mobject2.points.shape)
            temp[indices] = mobject2.rgbs[indices]
            mobject2.rgbs = temp
            self.non_redundant_m2_indices = indices

    def update_mobject(self, alpha):
        Mobject.interpolate(
            self.starting_mobject, 
            self.ending_mobject,
            self.mobject,
            alpha
        )

    def clean_up(self):
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

class SemiCircleTransform(Transform):
    def __init__(self, mobject1, mobject2, counterclockwise = True,
                 *args, **kwargs):
        Transform.__init__(self, mobject1, mobject2, *args, **kwargs)
        self.axis = (0, 0, 1) if counterclockwise else (0, 0, -1)

    def update_mobject(self, alpha):
        sm, em = self.starting_mobject, self.ending_mobject
        midpoints = (sm.points + em.points) / 2
        angle = alpha * np.pi
        rot_matrix = rotation_matrix(angle, self.axis)[:2, :2]
        self.mobject.points[:,:2] = np.dot(
            (sm.points - midpoints)[:,:2], 
            np.transpose(rot_matrix)
        ) + midpoints[:,:2]
        self.mobject.points[:,2] = (1-alpha)*sm.points[:,2] + alpha*em.points[:,2]
        self.mobject.rgbs = (1-alpha)*sm.rgbs + alpha*em.rgbs

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
    def __init__(self, function, mobject, run_time = DEFAULT_ANIMATION_RUN_TIME,
                 *args, **kwargs):
        map_image = copy.deepcopy(mobject)
        map_image.points = np.array(map(function, map_image.points))
        Transform.__init__(self, mobject, map_image, run_time = run_time, 
                           *args, **kwargs)
        self.name = "".join([
            "Apply",
            "".join([s.capitalize() for s in function.__name__.split("_")]),
            "To" + str(mobject)
        ])

class ComplexFunction(ApplyFunction):
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
        ApplyFunction.__init__(self, point_map, mobject, *args, **kwargs)
        self.name = "ComplexFunction" + to_cammel_case(function.__name__)
        #Todo, abstract away function naming'








