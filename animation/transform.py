import numpy as np
import itertools as it
import inspect
import copy
import warnings

from helpers import *

from animation import Animation
from mobject import Mobject, Point, VMobject, Group
from topics.geometry import Dot, Circle

class Transform(Animation):
    CONFIG = {
        "path_arc" : 0,
        "path_arc_axis" : OUT,
        "path_func" : None,
        "submobject_mode" : "all_at_once",
        "replace_mobject_with_target_in_scene" : False,
    }
    def __init__(self, mobject, target_mobject, **kwargs):
        #Copy target_mobject so as to not mess with caller
        self.original_target_mobject = target_mobject
        target_mobject = target_mobject.copy()
        mobject.align_data(target_mobject)
        self.target_mobject = target_mobject
        digest_config(self, kwargs)
        self.init_path_func()

        Animation.__init__(self, mobject, **kwargs)
        self.name += "To" + str(target_mobject)  

    def update_config(self, **kwargs):
        Animation.update_config(self, **kwargs)
        if "path_arc" in kwargs:
            self.path_func = path_along_arc(
                kwargs["path_arc"],
                kwargs.get("path_arc_axis", OUT)
            )

    def init_path_func(self):
        if self.path_func is not None:
            return
        elif self.path_arc == 0:
            self.path_func = straight_path
        else:
            self.path_func = path_along_arc(
                self.path_arc,
                self.path_arc_axis,
            )

    def get_all_mobjects(self):
        return self.mobject, self.starting_mobject, self.target_mobject

    def update_submobject(self, submob, start, end, alpha):
        submob.interpolate(start, end, alpha, self.path_func)
        return self

    def clean_up(self, surrounding_scene = None):
        Animation.clean_up(self, surrounding_scene)
        if self.replace_mobject_with_target_in_scene and surrounding_scene is not None:
            surrounding_scene.remove(self.mobject)
            if not self.remover:
                surrounding_scene.add(self.original_target_mobject)

class ReplacementTransform(Transform):
    CONFIG = {
        "replace_mobject_with_target_in_scene" : True,
    }


class ClockwiseTransform(Transform):
    CONFIG = {
        "path_arc" : -np.pi
    }

class CounterclockwiseTransform(Transform):
    CONFIG = {
        "path_arc" : np.pi
    }

class MoveToTarget(Transform):
    def __init__(self, mobject, **kwargs):
        if not hasattr(mobject, "target"):
            raise Exception("MoveToTarget called on mobject without attribute 'target' ")
        Transform.__init__(self, mobject, mobject.target, **kwargs)

class CyclicReplace(Transform):
    CONFIG = {
        "path_arc" : np.pi/2
    }
    def __init__(self, *mobjects, **kwargs):
        start = Group(*mobjects)
        target = Group(*[
            m1.copy().move_to(m2)
            for m1, m2 in adjacent_pairs(start)
        ])
        Transform.__init__(self, start, target, **kwargs)

class Swap(CyclicReplace):
    pass #Renaming, more understandable for two entries

class GrowFromPoint(Transform):
    def __init__(self, mobject, point, **kwargs):
        target = mobject.copy()
        point_mob = Point(point)
        mobject.replace(point_mob)
        mobject.highlight(point_mob.get_color())
        Transform.__init__(self, mobject, target, **kwargs)

class GrowFromCenter(GrowFromPoint):
    def __init__(self, mobject, **kwargs):
        GrowFromPoint.__init__(self, mobject, mobject.get_center(), **kwargs)

class GrowArrow(GrowFromPoint):
    def __init__(self, arrow, **kwargs):
        GrowFromPoint.__init__(self, arrow, arrow.get_start(), **kwargs)

class SpinInFromNothing(GrowFromCenter):
    CONFIG = {
        "path_func" : counterclockwise_path()
    }

class ShrinkToCenter(Transform):
    def __init__(self, mobject, **kwargs):
        Transform.__init__(
            self, mobject, mobject.get_point_mobject(), **kwargs
        )

class ApplyMethod(Transform):
    CONFIG = {
        "submobject_mode" : "all_at_once"
    }
    def __init__(self, method, *args, **kwargs):
        """
        Method is a method of Mobject.  *args is for the method,
        **kwargs is for the transform itself.

        Relies on the fact that mobject methods return the mobject
        """
        if not inspect.ismethod(method):
            raise Exception(
            "Whoops, looks like you accidentally invoked " + \
            "the method you want to animate"
        )
        assert(isinstance(method.im_self, Mobject))
        args = list(args) #So that args.pop() works
        if "method_kwargs" in kwargs:
            method_kwargs = kwargs["method_kwargs"]
        elif len(args) > 0 and isinstance(args[-1], dict):
            method_kwargs = args.pop()
        else:
            method_kwargs = {}
        target = method.im_self.copy()
        method.im_func(target, *args, **method_kwargs)
        Transform.__init__(self, method.im_self, target, **kwargs)

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

    def clean_up(self, surrounding_scene = None):
        Transform.clean_up(self, surrounding_scene)
        self.update(0)

class FadeIn(Transform):
    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        Transform.__init__(self, mobject, target, **kwargs)
        self.starting_mobject.fade(1)
        if isinstance(self.starting_mobject, VMobject):
            self.starting_mobject.set_stroke(width = 0)
            self.starting_mobject.set_fill(opacity = 0)

class FocusOn(Transform):
    CONFIG = {
        "opacity" : 0.2,
        "color" : GREY,
        "run_time" : 2,
        "remover" : True,
    }
    def __init__(self, mobject_or_point, **kwargs):
        digest_config(self, kwargs)
        big_dot = Dot(
            radius = SPACE_WIDTH+SPACE_HEIGHT,
            stroke_width = 0,
            fill_color = self.color,
            fill_opacity = 0,
        )
        little_dot = Dot(radius = 0)
        little_dot.set_fill(self.color, opacity = self.opacity)
        little_dot.move_to(mobject_or_point)

        Transform.__init__(self, big_dot, little_dot, **kwargs)

class Indicate(Transform):
    CONFIG = {
        "rate_func" : there_and_back,
        "scale_factor" : 1.2,
        "color" : YELLOW,
    }
    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        target = mobject.copy()
        target.scale_in_place(self.scale_factor)
        target.highlight(self.color)
        Transform.__init__(self, mobject, target, **kwargs)

class CircleIndicate(Indicate):
    CONFIG = {
        "rate_func" : squish_rate_func(there_and_back, 0, 0.8),
        "remover" : True
    }
    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        circle = Circle(color = self.color, **kwargs)
        circle.surround(mobject)
        Indicate.__init__(self, circle, **kwargs)

class Rotate(ApplyMethod):
    CONFIG = {
        "in_place" : False,
        "about_point" : None,
    }
    def __init__(self, mobject, angle = np.pi, axis = OUT, **kwargs):
        if "path_arc" not in kwargs:
            kwargs["path_arc"] = angle
        if "path_arc_axis" not in kwargs:
            kwargs["path_arc_axis"] = axis
        digest_config(self, kwargs, locals())
        target = mobject.copy()
        if self.in_place:
            self.about_point = mobject.get_center()
        target.rotate(
            angle, 
            axis = axis,
            about_point = self.about_point,
        )
        Transform.__init__(self, mobject, target, **kwargs)

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
    CONFIG = {
        "submobject_mode" : "all_at_once",
    }
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
                if hasattr(anim, "target_mobject"):
                    anim.starting_mobject.align_data(anim.target_mobject)

        Transform.__init__(self, start_anim.mobject, end_anim.mobject, **kwargs)
        #Rewire starting and ending mobjects
        start_anim.mobject = self.starting_mobject
        end_anim.mobject = self.target_mobject

    def update(self, alpha):
        self.start_anim.update(alpha)
        self.end_anim.update(alpha)
        Transform.update(self, alpha)



