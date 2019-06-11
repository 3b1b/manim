import inspect

import numpy as np

from manimlib.animation.animation import OldAnimation
from manimlib.animation.transform import OldTransform,OldMoveToTarget,OldApplyMethod
from manimlib.animation.transform import instantiate
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


class OldReplacementTransform(OldTransform):
    CONFIG = {
        "replace_mobject_with_target_in_scene": True,
    }


class OldTransformFromCopy(OldReplacementTransform):
    def __init__(self, mobject, target_mobject, **kwargs):
        OldReplacementTransform.__init__(
            self, mobject.deepcopy(), target_mobject, **kwargs
        )


class OldClockwiseTransform(OldTransform):
    CONFIG = {
        "path_arc": -np.pi
    }


class OldCounterclockwiseTransform(OldTransform):
    CONFIG = {
        "path_arc": np.pi
    }


class OldMoveToTarget(OldTransform):
    def __init__(self, mobject, **kwargs):
        if not hasattr(mobject, "target"):
            raise Exception(
                "MoveToTarget called on mobject without attribute 'target' ")
        OldTransform.__init__(self, mobject, mobject.target, **kwargs)


class OldApplyMethod(OldTransform):
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
        OldTransform.__init__(self, method.__self__, target, **kwargs)


class OldApplyPointwiseFunction(OldApplyMethod):
    CONFIG = {
        "run_time": DEFAULT_POINTWISE_FUNCTION_RUN_TIME
    }

    def __init__(self, function, mobject, **kwargs):
        OldApplyMethod.__init__(
            self, mobject.apply_function, function, **kwargs
        )


class OldApplyPointwiseFunctionToCenter(OldApplyPointwiseFunction):
    def __init__(self, function, mobject, **kwargs):
        OldApplyMethod.__init__(
            self, mobject.move_to, function(mobject.get_center()), **kwargs
        )


class OldFadeToColor(OldApplyMethod):
    def __init__(self, mobject, color, **kwargs):
        OldApplyMethod.__init__(self, mobject.set_color, color, **kwargs)


class OldScaleInPlace(OldApplyMethod):
    def __init__(self, mobject, scale_factor, **kwargs):
        OldApplyMethod.__init__(self, mobject.scale_in_place,
                             scale_factor, **kwargs)


class OldRestore(OldApplyMethod):
    def __init__(self, mobject, **kwargs):
        OldApplyMethod.__init__(self, mobject.restore, **kwargs)


class OldApplyFunction(OldTransform):
    CONFIG = {
        "submobject_mode": "all_at_once",
    }

    def __init__(self, function, mobject, **kwargs):
        OldTransform.__init__(
            self,
            mobject,
            function(mobject.copy()),
            **kwargs
        )
        self.name = "ApplyFunctionTo" + str(mobject)


class OldApplyMatrix(OldApplyPointwiseFunction):
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
        OldApplyPointwiseFunction.__init__(self, func, mobject, **kwargs)


class OldComplexFunction(OldApplyPointwiseFunction):
    def __init__(self, function, mobject, **kwargs):
        if "path_func" not in kwargs:
            self.path_func = path_along_arc(
                np.log(function(complex(1))).imag
            )
        OldApplyPointwiseFunction.__init__(
            self,
            lambda x_y_z: complex_to_R3(function(complex(x_y_z[0], x_y_z[1]))),
            instantiate(mobject),
            **kwargs
        )

###


class OldCyclicReplace(OldTransform):
    CONFIG = {
        "path_arc": np.pi / 2
    }

    def __init__(self, *mobjects, **kwargs):
        start = Group(*mobjects)
        target = Group(*[
            m1.copy().move_to(m2)
            for m1, m2 in adjacent_pairs(start)
        ])
        OldTransform.__init__(self, start, target, **kwargs)


class OldSwap(OldCyclicReplace):
    pass  # Renaming, more understandable for two entries

# TODO: Um...does this work


class OldTransformAnimations(OldTransform):
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

        OldTransform.__init__(self, start_anim.mobject,
                           end_anim.mobject, **kwargs)
        # Rewire starting and ending mobjects
        start_anim.mobject = self.starting_mobject
        end_anim.mobject = self.target_mobject

    def update(self, alpha):
        self.start_anim.update(alpha)
        self.end_anim.update(alpha)
        OldTransform.update(self, alpha)
