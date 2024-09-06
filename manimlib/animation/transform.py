from __future__ import annotations

import inspect

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.constants import DEGREES
from manimlib.constants import OUT
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.utils.paths import path_along_arc
from manimlib.utils.paths import straight_path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    import numpy.typing as npt
    from manimlib.scene.scene import Scene
    from manimlib.typing import ManimColor


class Transform(Animation):
    replace_mobject_with_target_in_scene: bool = False

    def __init__(
        self,
        mobject: Mobject,
        target_mobject: Mobject | None = None,
        path_arc: float = 0.0,
        path_arc_axis: np.ndarray = OUT,
        path_func: Callable | None = None,
        **kwargs
    ):
        self.target_mobject = target_mobject
        self.path_arc = path_arc
        self.path_arc_axis = path_arc_axis
        self.path_func = path_func
        super().__init__(mobject, **kwargs)
        self.init_path_func()

    def init_path_func(self) -> None:
        if self.path_func is not None:
            return
        elif self.path_arc == 0:
            self.path_func = straight_path
        else:
            self.path_func = path_along_arc(
                self.path_arc,
                self.path_arc_axis,
            )

    def begin(self) -> None:
        self.target_mobject = self.create_target()
        self.check_target_mobject_validity()

        if self.mobject.is_aligned_with(self.target_mobject):
            self.target_copy = self.target_mobject
        else:
            # Use a copy of target_mobject for the align_data_and_family
            # call so that the actual target_mobject stays
            # preserved, since calling align_data will potentially
            # change the structure of both arguments
            self.target_copy = self.target_mobject.copy()
        self.mobject.align_data_and_family(self.target_copy)
        super().begin()
        if not self.mobject.has_updaters():
            self.mobject.lock_matching_data(
                self.starting_mobject,
                self.target_copy,
            )

    def finish(self) -> None:
        super().finish()
        self.mobject.unlock_data()

    def create_target(self) -> Mobject:
        # Has no meaningful effect here, but may be useful
        # in subclasses
        return self.target_mobject

    def check_target_mobject_validity(self) -> None:
        if self.target_mobject is None:
            raise Exception(
                f"{self.__class__.__name__}.create_target not properly implemented"
            )

    def clean_up_from_scene(self, scene: Scene) -> None:
        super().clean_up_from_scene(scene)
        if self.replace_mobject_with_target_in_scene:
            scene.remove(self.mobject)
            scene.add(self.target_mobject)

    def update_config(self, **kwargs) -> None:
        Animation.update_config(self, **kwargs)
        if "path_arc" in kwargs:
            self.path_func = path_along_arc(
                kwargs["path_arc"],
                kwargs.get("path_arc_axis", OUT)
            )

    def get_all_mobjects(self) -> list[Mobject]:
        return [
            self.mobject,
            self.starting_mobject,
            self.target_mobject,
            self.target_copy,
        ]

    def get_all_families_zipped(self) -> zip[tuple[Mobject]]:
        return zip(*[
            mob.get_family()
            for mob in [
                self.mobject,
                self.starting_mobject,
                self.target_copy,
            ]
        ])

    def interpolate_submobject(
        self,
        submob: Mobject,
        start: Mobject,
        target_copy: Mobject,
        alpha: float
    ):
        submob.interpolate(start, target_copy, alpha, self.path_func)
        return self


class ReplacementTransform(Transform):
    replace_mobject_with_target_in_scene: bool = True


class TransformFromCopy(Transform):
    replace_mobject_with_target_in_scene: bool = True

    def __init__(self, mobject: Mobject, target_mobject: Mobject, **kwargs):
        super().__init__(mobject.copy(), target_mobject, **kwargs)


class MoveToTarget(Transform):
    def __init__(self, mobject: Mobject, **kwargs):
        self.check_validity_of_input(mobject)
        super().__init__(mobject, mobject.target, **kwargs)

    def check_validity_of_input(self, mobject: Mobject) -> None:
        if not hasattr(mobject, "target"):
            raise Exception(
                "MoveToTarget called on mobject without attribute 'target'"
            )


class _MethodAnimation(MoveToTarget):
    def __init__(self, mobject: Mobject, methods: list[Callable], **kwargs):
        self.methods = methods
        super().__init__(mobject, **kwargs)


class ApplyMethod(Transform):
    def __init__(self, method: Callable, *args, **kwargs):
        """
        method is a method of Mobject, *args are arguments for
        that method.  Key word arguments should be passed in
        as the last arg, as a dict, since **kwargs is for
        configuration of the transform itself

        Relies on the fact that mobject methods return the mobject
        """
        self.check_validity_of_input(method)
        self.method = method
        self.method_args = args
        super().__init__(method.__self__, **kwargs)

    def check_validity_of_input(self, method: Callable) -> None:
        if not inspect.ismethod(method):
            raise Exception(
                "Whoops, looks like you accidentally invoked "
                "the method you want to animate"
            )
        assert isinstance(method.__self__, Mobject)

    def create_target(self) -> Mobject:
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
    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        run_time: float = 3.0,
        **kwargs
    ):
        super().__init__(mobject.apply_function, function, run_time=run_time, **kwargs)


class ApplyPointwiseFunctionToCenter(Transform):
    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        super().__init__(mobject, **kwargs)

    def create_target(self) -> Mobject:
        return self.mobject.copy().move_to(self.function(self.mobject.get_center()))


class FadeToColor(ApplyMethod):
    def __init__(
        self,
        mobject: Mobject,
        color: ManimColor,
        **kwargs
    ):
        super().__init__(mobject.set_color, color, **kwargs)


class ScaleInPlace(ApplyMethod):
    def __init__(
        self,
        mobject: Mobject,
        scale_factor: npt.ArrayLike,
        **kwargs
    ):
        super().__init__(mobject.scale, scale_factor, **kwargs)


class ShrinkToCenter(ScaleInPlace):
    def __init__(self, mobject: Mobject, **kwargs):
        super().__init__(mobject, 0, **kwargs)


class Restore(Transform):
    def __init__(self, mobject: Mobject, **kwargs):
        if not hasattr(mobject, "saved_state") or mobject.saved_state is None:
            raise Exception("Trying to restore without having saved")
        super().__init__(mobject, mobject.saved_state, **kwargs)


class ApplyFunction(Transform):
    def __init__(
        self,
        function: Callable[[Mobject], Mobject],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        super().__init__(mobject, **kwargs)

    def create_target(self) -> Mobject:
        target = self.function(self.mobject.copy())
        if not isinstance(target, Mobject):
            raise Exception("Functions passed to ApplyFunction must return object of type Mobject")
        return target


class ApplyMatrix(ApplyPointwiseFunction):
    def __init__(
        self,
        matrix: npt.ArrayLike,
        mobject: Mobject,
        **kwargs
    ):
        matrix = self.initialize_matrix(matrix)

        def func(p):
            return np.dot(p, matrix.T)

        super().__init__(func, mobject, **kwargs)

    def initialize_matrix(self, matrix: npt.ArrayLike) -> np.ndarray:
        matrix = np.array(matrix)
        if matrix.shape == (2, 2):
            new_matrix = np.identity(3)
            new_matrix[:2, :2] = matrix
            matrix = new_matrix
        elif matrix.shape != (3, 3):
            raise Exception("Matrix has bad dimensions")
        return matrix


class ApplyComplexFunction(ApplyMethod):
    def __init__(
        self,
        function: Callable[[complex], complex],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        method = mobject.apply_complex_function
        super().__init__(method, function, **kwargs)

    def init_path_func(self) -> None:
        func1 = self.function(complex(1))
        self.path_arc = np.log(func1).imag
        super().init_path_func()

###


class CyclicReplace(Transform):
    def __init__(self, *mobjects: Mobject, path_arc=90 * DEGREES, **kwargs):
        super().__init__(Group(*mobjects), path_arc=path_arc, **kwargs)

    def create_target(self) -> Mobject:
        group = self.mobject
        target = group.copy()
        cycled_targets = [target[-1], *target[:-1]]
        for m1, m2 in zip(cycled_targets, group):
            m1.move_to(m2)
        return target


class Swap(CyclicReplace):
    """Alternate name for CyclicReplace"""
    pass
