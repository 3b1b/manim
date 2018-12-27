import inspect

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.constants import *
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.config_ops import instantiate
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
        "submobject_mode": "all_at_once",
        "replace_mobject_with_target_in_scene": False,
    }

    def __init__(self, mobject, target_mobject, **kwargs):
        # Copy target_mobject so as to not mess with caller
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

    def clean_up(self, surrounding_scene=None):
        Animation.clean_up(self, surrounding_scene)
        if self.replace_mobject_with_target_in_scene and surrounding_scene is not None:
            surrounding_scene.remove(self.mobject)
            if not self.remover:
                surrounding_scene.add(self.original_target_mobject)


class ReplacementTransform(Transform):
    CONFIG = {
        "replace_mobject_with_target_in_scene": True,
    }


class TransformFromCopy(ReplacementTransform):
    def __init__(self, mobject, target_mobject, **kwargs):
        ReplacementTransform.__init__(
            self, mobject.deepcopy(), target_mobject, **kwargs
        )


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
        if not hasattr(mobject, "target"):
            raise Exception(
                "MoveToTarget called on mobject without attribute 'target' ")
        Transform.__init__(self, mobject, mobject.target, **kwargs)


class ApplyMethod(Transform):
    CONFIG = {
        "submobject_mode": "all_at_once"
    }

    def __init__(self, method, *args, **kwargs):
        """
        Method is a method of Mobject.  *args is for the method,
        **kwargs is for the transform itself.

        Relies on the fact that mobject methods return the mobject
        """
        if not inspect.ismethod(method):
            raise Exception(
                "Whoops, looks like you accidentally invoked "
                "the method you want to animate"
            )
        assert(isinstance(method.__self__, Mobject))
        args = list(args)  # So that args.pop() works
        if "method_kwargs" in kwargs:
            method_kwargs = kwargs["method_kwargs"]
        elif len(args) > 0 and isinstance(args[-1], dict):
            method_kwargs = args.pop()
        else:
            method_kwargs = {}
        target = method.__self__.copy()
        method.__func__(target, *args, **method_kwargs)
        Transform.__init__(self, method.__self__, target, **kwargs)


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
        ApplyMethod.__init__(
            self, mobject.move_to, function(mobject.get_center()), **kwargs
        )


class FadeToColor(ApplyMethod):
    def __init__(self, mobject, color, **kwargs):
        ApplyMethod.__init__(self, mobject.set_color, color, **kwargs)


class ScaleInPlace(ApplyMethod):
    def __init__(self, mobject, scale_factor, **kwargs):
        ApplyMethod.__init__(self, mobject.scale_in_place,
                             scale_factor, **kwargs)


class Restore(ApplyMethod):
    def __init__(self, mobject, **kwargs):
        ApplyMethod.__init__(self, mobject.restore, **kwargs)


class ApplyFunction(Transform):
    CONFIG = {
        "submobject_mode": "all_at_once",
    }

    def __init__(self, function, mobject, **kwargs):
        Transform.__init__(
            self,
            mobject,
            function(mobject.copy()),
            **kwargs
        )
        self.name = "ApplyFunctionTo" + str(mobject)


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
            lambda x_y_z: complex_to_R3(function(complex(x_y_z[0], x_y_z[1]))),
            instantiate(mobject),
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

    def update(self, alpha):
        self.start_anim.update(alpha)
        self.end_anim.update(alpha)
        Transform.update(self, alpha)
