import inspect

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.constants import *
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.paths import path_along_arc
from manimlib.utils.paths import straight_path
from manimlib.utils.rate_functions import smooth
from manimlib.utils.rate_functions import squish_rate_func
from manimlib.utils.space_ops import complex_to_R3


class Transform(Animation):
    CONFIG = {
        "path_arc": 0,
        "path_arc_axis": OUT,
        "path_func": None,
        "replace_mobject_with_target_in_scene": False,
    }

    def __init__(self, mobject, target_mobject, **kwargs):
        Animation.__init__(self, mobject, **kwargs)
        self.target_mobject = target_mobject
        self.init_path_func()

    def __str__(self):
        return "{}To{}".format(
            super().__str__(),
            str(self.target_mobject)
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

    def begin(self):
        # Use a copy of target_mobject for the align_data
        # call so that the actual target_mobject stays
        # preserved.
        self.target_copy = self.target_mobject.copy()
        # Note, this potentially changes the structure
        # of both mobject and target_mobject
        self.mobject.align_data(self.target_copy)
        super().begin()

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        if self.replace_mobject_with_target_in_scene:
            scene.remove(self.mobject)
            scene.add(self.target_mobject)

    def update_config(self, **kwargs):
        Animation.update_config(self, **kwargs)
        if "path_arc" in kwargs:
            self.path_func = path_along_arc(
                kwargs["path_arc"],
                kwargs.get("path_arc_axis", OUT)
            )

    def get_all_mobjects(self):
        return [
            self.mobject,
            self.starting_mobject,
            self.target_mobject,
            self.target_copy,
        ]

    def interpolate_submobject(self, submob, start, target, target_copy, alpha):
        submob.interpolate(
            start, target_copy,
            alpha, self.path_func
        )
        return self


class ReplacementTransform(Transform):
    CONFIG = {
        "replace_mobject_with_target_in_scene": True,
    }


class TransformFromCopy(Transform):
    """
    Performs a reversed Transform
    """

    def __init__(self, mobject, target_mobject, **kwargs):
        Transform.__init__(
            self, target_mobject, mobject, **kwargs
        )

    def interpolate(self, alpha):
        super().interpolate(1 - alpha)


class ClockwiseTransform(Transform):
    CONFIG = {
        "path_arc": -np.pi
    }


class CounterclockwiseTransform(Transform):
    CONFIG = {
        "path_arc": np.pi
    }


class MoveToTarget(Transform):
    def __init__(self, mobject, **kwargs):
        self.check_validity_of_input(mobject)
        Transform.__init__(self, mobject, mobject.target, **kwargs)

    def check_validity_of_input(self, mobject):
        if not hasattr(mobject, "target"):
            raise Exception(
                "MoveToTarget called on mobject"
                "without attribute 'target'"
            )


class ApplyMethod(Transform):
    def __init__(self, method, *args, **kwargs):
        """
        method is a method of Mobject, *args are arguments for
        that method.  Key word arguments should be passed in
        as the last arg, as a dict, since **kwargs is for
        configuration of the transform itslef

        Relies on the fact that mobject methods return the mobject
        """
        self.check_validity_of_input(method)
        self.method = method
        self.method_args = args
        # This will be replaced
        temp_target = method.__self__
        Transform.__init__(self, method.__self__, temp_target, **kwargs)

    def check_validity_of_input(self, method):
        if not inspect.ismethod(method):
            raise Exception(
                "Whoops, looks like you accidentally invoked "
                "the method you want to animate"
            )
        assert(isinstance(method.__self__, Mobject))

    def begin(self):
        self.target_mobject = self.create_target()
        super().begin()

    def create_target(self):
        method = self.method
        # Make sure it's a list so that args.pop() works
        args = list(self.method_args)

        if len(args) > 0 and isinstance(args[-1], dict):
            method_kwargs = args.pop()
        else:
            method_kwargs = {}
        target = method.__self__.copy()
        method.__func__(target, *args, **method_kwargs)
        return target


class ApplyPointwiseFunction(ApplyMethod):
    CONFIG = {
        "run_time": DEFAULT_POINTWISE_FUNCTION_RUN_TIME
    }

    def __init__(self, function, mobject, **kwargs):
        ApplyMethod.__init__(
            self, mobject.apply_function, function, **kwargs
        )


class ApplyPointwiseFunctionToCenter(ApplyPointwiseFunction):
    def __init__(self, function, mobject, **kwargs):
        self.function = function
        ApplyMethod.__init__(
            self, mobject.move_to, **kwargs
        )

    def begin(self):
        self.method_args = [
            self.function(self.mobject.get_center())
        ]
        super().begin()


class FadeToColor(ApplyMethod):
    def __init__(self, mobject, color, **kwargs):
        ApplyMethod.__init__(self, mobject.set_color, color, **kwargs)


class ScaleInPlace(ApplyMethod):
    def __init__(self, mobject, scale_factor, **kwargs):
        ApplyMethod.__init__(
            self, mobject.scale, scale_factor, **kwargs
        )


class Restore(ApplyMethod):
    def __init__(self, mobject, **kwargs):
        ApplyMethod.__init__(self, mobject.restore, **kwargs)


class ApplyFunction(Transform):
    def __init__(self, function, mobject, **kwargs):
        self.function = function
        temp_target = mobject
        Transform.__init__(
            self, mobject, temp_target, **kwargs
        )

    def begin(self):
        self.target_mobject = self.function(
            self.mobject.copy()
        )
        super().begin()


class ApplyMatrix(ApplyPointwiseFunction):
    # Truth be told, I'm not sure if this is useful.
    def __init__(self, matrix, mobject, **kwargs):
        matrix = np.array(matrix)
        if matrix.shape == (2, 2):
            new_matrix = np.identity(3)
            new_matrix[:2, :2] = matrix
            matrix = new_matrix
        elif matrix.shape != (3, 3):
            raise Exception("Matrix has bad dimensions")
        transpose = np.transpose(matrix)

        def func(p):
            return np.dot(p, transpose)
        ApplyPointwiseFunction.__init__(self, func, mobject, **kwargs)


class ComplexFunction(ApplyPointwiseFunction):
    def __init__(self, function, mobject, **kwargs):
        if "path_func" not in kwargs:
            self.path_func = path_along_arc(
                np.log(function(complex(1))).imag
            )
        ApplyPointwiseFunction.__init__(
            self,
            lambda p: complex_to_R3(function(
                complex(p[0], p[1])
            )),
            mobject,
            **kwargs
        )

###


class CyclicReplace(Transform):
    CONFIG = {
        "path_arc": np.pi / 2
    }

    def __init__(self, *mobjects, **kwargs):
        start = Group(*mobjects)
        target = Group(*[
            m1.copy().move_to(m2)
            for m1, m2 in adjacent_pairs(start)
        ])
        Transform.__init__(self, start, target, **kwargs)


class Swap(CyclicReplace):
    pass  # Renaming, more understandable for two entries

# TODO: Um...does this work


class TransformAnimations(Transform):
    CONFIG = {
        "rate_func": squish_rate_func(smooth)
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

        Transform.__init__(self, start_anim.mobject,
                           end_anim.mobject, **kwargs)
        # Rewire starting and ending mobjects
        start_anim.mobject = self.starting_mobject
        end_anim.mobject = self.target_mobject

    def interpolate(self, alpha):
        self.start_anim.interpolate(alpha)
        self.end_anim.interpolate(alpha)
        Transform.interpolate(self, alpha)
