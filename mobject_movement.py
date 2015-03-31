from PIL import Image
from colour import Color
import numpy as np
import warnings
import time
import os
import copy
import progressbar
import inspect
from images2gif import writeGif

from helpers import *
from mobject import *
import displayer as disp

class MobjectMovement(object):
    def __init__(self, 
                 mobject,
                 run_time = DEFAULT_ANIMATION_RUN_TIME,
                 alpha_func = high_inflection_0_to_1,
                 name = None):
        if isinstance(mobject, type) and issubclass(mobject, Mobject):
            self.mobject = mobject()
        elif isinstance(mobject, Mobject):
            self.mobject = mobject
        else:
            raise Exception("Invalid mobject parameter, must be \
                             subclass or instance of Mobject")
        self.starting_mobject = copy.deepcopy(self.mobject)
        self.reference_mobjects = [self.starting_mobject]
        self.alpha_func = alpha_func or (lambda x : x)
        self.run_time = run_time
        #TODO, Adress the idea of filtering the mobmov
        self.filter_functions = []
        self.restricted_height = SPACE_HEIGHT
        self.restricted_width  = SPACE_WIDTH
        self.spacial_center = np.zeros(3)
        self.name = name or self.__class__.__name__ + str(self.mobject)

    def __str__(self):
        return self.name

    def get_points_and_rgbs(self):
        """
        It is the responsibility of this class to only emit points within
        the space.  Returns np array of points and corresponding np array 
        of rgbs
        """
        #TODO, I don't think this should be necessary.  This should happen 
        #under the individual mobjects.  
        points = self.mobject.points
        rgbs   = self.mobject.rgbs
        #Filters out what is out of bounds.
        admissibles = (abs(points[:,0]) < self.restricted_width) * \
                      (abs(points[:,1]) < self.restricted_height)
        for filter_function in self.filter_functions:
            admissibles *= ~filter_function(points)
        if any(self.spacial_center):
            points += self.spacial_center
            #Filter out points pushed off the edge
            admissibles *= (abs(points[:,0]) < SPACE_WIDTH) * \
                           (abs(points[:,1]) < SPACE_HEIGHT)
        if rgbs.shape[0] < points.shape[0]:
            #TODO, this shouldn't be necessary, find what's happening.
            points = points[:rgbs.shape[0], :]
            admissibles = admissibles[:rgbs.shape[0]]
        return points[admissibles, :], rgbs[admissibles, :]

    def update(self, alpha):
        if alpha < 0:
            alpha = 0
        if alpha > 1:
            alpha = 1
        self.update_mobject(self.alpha_func(alpha))

    def filter_out(self, *filter_functions):
        self.filter_functions += filter_functions
        return self

    def restrict_height(self, height):
        self.restricted_height = min(height, SPACE_HEIGHT)
        return self

    def restrict_width(self, width):
        self.restricted_width = min(width, SPACE_WIDTH)   
        return self

    def shift(self, vector):
        self.spacial_center += vector
        return self

    def set_run_time(self, time):
        self.run_time = time
        return self.reload()

    def set_alpha_func(self, alpha_func):
        if alpha_func is None:
            alpha_func = lambda x : x
        self.alpha_func = alpha_func
        return self

    def set_name(self, name):
        self.name = name
        return self

    # def drag_pixels(self):
    #     self.frames = drag_pixels(self.get_frames())
    #     return self

    # def reverse(self):
    #     self.get_frames().reverse()
    #     self.name = 'Reversed' + str(self)
    #     return self

    def update_mobject(self, alpha):
        #Typically ipmlemented by subclass
        pass

    def clean_up(self):
        pass
        

###### Concrete MobjectMovement ########

class Rotating(MobjectMovement):
    def __init__(self,
                 mobject,
                 axis = None,
                 axes = [[0, 0, 1], [0, 1, 0]], 
                 radians = 2 * np.pi,
                 run_time = 20.0,
                 alpha_func = None,
                 *args, **kwargs):
        MobjectMovement.__init__(
            self, mobject,
            run_time = run_time,
            alpha_func = alpha_func,
            *args, **kwargs
        )
        self.axes = [axis] if axis else axes
        self.radians = radians

    def update_mobject(self, alpha):
        self.mobject.points = self.starting_mobject.points
        for axis in self.axes:
            self.mobject.rotate(
                self.radians * alpha,
                axis
            )

class RotationAsTransform(Rotating):
    def __init__(self, mobject, radians, axis = (0, 0, 1), axes = None,
                 run_time = DEFAULT_ANIMATION_RUN_TIME,
                 alpha_func = high_inflection_0_to_1,
                 *args, **kwargs):
        Rotating.__init__(
            self,
            mobject,
            axis = axis,
            axes = axes,
            run_time = run_time,
            radians = radians,
            alpha_func = alpha_func,
        )

class FadeOut(MobjectMovement):
    def update_mobject(self, alpha):
        self.mobject.rgbs = self.starting_mobject.rgbs * (1 - alpha)

class Reveal(MobjectMovement):
    def update_mobject(self, alpha):
        self.mobject.rgbs = self.starting_mobject.rgbs * alpha
        if self.mobject.points.shape != self.starting_mobject.points.shape:
            self.mobject.points = self.starting_mobject.points
            #TODO, Why do you need to do this? Shouldn't points always align?

class Transform(MobjectMovement):
    def __init__(self, mobject1, mobject2, 
                 run_time = DEFAULT_TRANSFORM_RUN_TIME,
                 *args, **kwargs):
        count1, count2 = mobject1.get_num_points(), mobject2.get_num_points()
        Mobject.align_data(mobject1, mobject2)
        MobjectMovement.__init__(self, mobject1, run_time = run_time, *args, **kwargs)
        self.ending_mobject = mobject2
        self.mobject.SHOULD_BUFF_POINTS = \
            mobject1.SHOULD_BUFF_POINTS and mobject2.SHOULD_BUFF_POINTS
        self.reference_mobjects.append(mobject2)
        self.name += "To" + str(mobject2)

        if count2 < count1:
            #Ensure redundant pixels fade to black
            indices = self.non_redundant_m2_indices = \
                np.arange(0, count1-1, float(count1) / count2).astype('int')
            temp = np.zeros(mobject2.points.shape)
            temp[indices] = mobject2.rgbs[indices]
            mobject2.rgbs = temp

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

class ApplyMethod(Transform):
    def __init__(self, method, mobject, *args, **kwargs):
        """
        Method is a method of Mobject
        """
        method_args = ()
        if isinstance(method, tuple):
            method, method_args = method[0], method[1:]
        if not inspect.ismethod(method):
            raise "Not a valid Mobject method"
        Transform.__init__(
            self,
            mobject, 
            method(copy.deepcopy(mobject), *method_args),
            *args, **kwargs
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

class Homotopy(MobjectMovement):
    def __init__(self, homotopy, *args, **kwargs):
        """
        Homotopy a function from (x, y, z, t) to (x', y', z')
        """
        self.homotopy = homotopy
        MobjectMovement.__init__(self, *args, **kwargs)

    def update_mobject(self, alpha):
        self.mobject.points = np.array([
            self.homotopy((x, y, z, alpha))
            for x, y, z in self.starting_mobject.points
        ])

class ComplexHomotopy(Homotopy):
    def __init__(self, complex_homotopy, *args, **kwargs):
        """
        Complex Hootopy a function (z, t) to z'
        """
        def homotopy((x, y, z, t)):
            c = complex_homotopy((complex(x, y), t))
            return (c.real, c.imag, z)
        if len(args) > 0:
            args = list(args)
            mobject = args.pop(0)
        elif "mobject" in kwargs:
            mobject = kwargs["mobject"]
        else:
            mobject = Grid()
        Homotopy.__init__(self, homotopy, mobject, *args, **kwargs)
        self.name = "ComplexHomotopy" + \
            to_cammel_case(complex_homotopy.__name__)


class ShowCreation(MobjectMovement):
    def update_mobject(self, alpha):
        #TODO, shoudl I make this more efficient?
        new_num_points = int(alpha * self.starting_mobject.points.shape[0])
        for attr in ["points", "rgbs"]:
            setattr(
                self.mobject, 
                attr, 
                getattr(self.starting_mobject, attr)[:new_num_points, :]
            )

class Flash(MobjectMovement):
    def __init__(self, mobject, color = "white", slow_factor = 0.01,
                 run_time = 0.1, alpha_func = None,
                 *args, **kwargs):
        MobjectMovement.__init__(self, mobject, run_time = run_time, 
                           alpha_func = alpha_func,
                           *args, **kwargs)
        self.intermediate = Mobject(color = color)
        self.intermediate.add_points([
            point + (x, y, 0)
            for point in self.mobject.points
            for x in [-1, 1]
            for y in [-1, 1]
        ])
        self.reference_mobjects.append(self.intermediate)
        self.slow_factor = slow_factor

    def update_mobject(self, alpha):
        #Makes alpha go from 0 to slow_factor to 0 instead of 0 to 1
        alpha = self.slow_factor * (1.0 - 4 * (alpha - 0.5)**2)
        Mobject.interpolate(
            self.starting_mobject, 
            self.intermediate, 
            self.mobject, 
            alpha
        )







