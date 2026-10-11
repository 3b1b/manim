from __future__ import annotations

import inspect

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.constants import DEG
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
    """
    Transform
    =========

    An animation that transforms a Mobject from its starting state into the
    state of a target Mobject. Transform interpolates the geometry and visual
    properties of the source object toward those of the target over the
    animation's duration.

    It is one of the fundamental animation classes in ManimGL and serves as
    the basis for many specialized transformations. It can be used to morph
    geometric shapes, modify mathematical expressions, change object colors,
    and animate objects along straight or curved interpolation paths.

    By default, the original Mobject remains the object managed by the scene.
    At cleanup, the target replaces the original in the scene only when
    replace_mobject_with_target_in_scene is enabled by a subclass or
    otherwise configured appropriately.

    Parameters
    ----------
    mobject : Mobject
        The original object to animate. Its starting state is captured by
        the parent Animation lifecycle, and its family members are
        interpolated toward the corresponding members of the target copy.

    target_mobject : Mobject or None, default=None
        The destination object describing the desired final state.

        If None is supplied, create_target() must provide a valid target.
        The base implementation simply returns self.target_mobject, so the
        base Transform class requires a target_mobject to be supplied.

    path_arc : float or tuple[float, float], default=0.0
        Controls the angular curvature of the interpolation path when the
        default path function is selected.

        A floating-point value of 0.0 selects straight_path. Other supported
        values are passed to path_along_arc() to construct a curved path.
        A tuple can represent the angular parameters supported by that
        helper in the installed ManimGL version.

    path_arc_axis : np.ndarray, default=OUT
        The axis used by path_along_arc() when constructing the default
        curved interpolation path. OUT is the default direction, typically
        corresponding to the positive z-axis in the standard 3D coordinate
        system.

    path_func : Callable or None, default=None
        An optional custom interpolation-path function.

        When supplied, this function is used directly and the default path
        selection is skipped. When omitted, init_path_func() chooses either
        straight_path or path_along_arc(), depending on path_arc.

    **kwargs
        Additional keyword arguments forwarded to Animation.__init__.
        Depending on the installed ManimGL version, these can include
        run_time, rate_func, remover, and other standard animation options.

    Class Attributes
    ----------------
    replace_mobject_with_target_in_scene : bool, default=False
        Controls whether cleanup removes the original Mobject from the scene
        and adds target_mobject in its place.

        The base Transform class sets this to False. Subclasses can override
        it to change the replacement behavior.

    Instance Attributes
    -------------------
    target_mobject : Mobject or None
        The destination object supplied to the constructor or returned by
        create_target().

    path_arc : float or tuple[float, float]
        Angular configuration used to construct the default curved path.

    path_arc_axis : np.ndarray
        Axis passed to path_along_arc() when the default curved path is used.

    path_func : Callable
        Function used to interpolate the points of corresponding Mobject
        components along the chosen path.

    target_copy : Mobject
        A target representation used for interpolation. If the source is
        already aligned with the target, this may refer directly to the
        target object. Otherwise, it is created as a copy so that alignment
        does not modify the actual target.

    starting_mobject : Mobject
        Inherited from Animation. Represents the captured starting state
        used during interpolation.

    Implementation
    --------------
    1. The constructor stores the target and path configuration.
    2. init_path_func() selects the interpolation path unless a custom
       path_func has already been supplied.
    3. At begin(), create_target() obtains the target and
       check_target_mobject_validity() ensures that it is not None.
    4. If the source and target are already aligned, target_copy refers to
       the target directly. Otherwise, the target is copied and
       align_data_and_family() is used to make the source and target copy
       structurally compatible for interpolation.
    5. The parent Animation begin() process captures the starting state.
    6. During interpolation, get_all_families_zipped() supplies corresponding
       family members of the source, starting state, and target copy.
    7. interpolate_submobject() calls the source component's interpolate()
       method with the starting component, target component, alpha, and
       path_func.
    8. During cleanup, the parent cleanup runs. If
       replace_mobject_with_target_in_scene is True, the original object is
       removed and target_mobject is added to the scene.

    The alignment process is important because two Mobjects can contain
    different numbers or arrangements of points and submobjects. The class
    uses aligned family structures so corresponding components can be
    interpolated consistently.

    Methods
    -------
    init_path_func()
        Selects straight_path or path_along_arc() when no custom path_func
        has been supplied.

    begin()
        Creates and validates the target, prepares an aligned target copy
        when necessary, and begins the parent animation lifecycle.

    create_target()
        Returns target_mobject in this base implementation. Subclasses can
        override this method to construct a target automatically.

    check_target_mobject_validity()
        Raises an exception if create_target() has not supplied a target.

    clean_up_from_scene(scene)
        Performs parent cleanup and optionally replaces the original object
        with target_mobject in the scene.

    update_config(**kwargs)
        Updates animation configuration and recalculates the path function
        when path_arc is included in the supplied configuration.

    get_all_mobjects()
        Returns the source, starting state, target, and target copy.

    get_all_families_zipped()
        Returns an iterator that groups corresponding family members from
        the source, starting state, and target copy.

    get_interpolation_ends()
        Returns the starting Mobject and target copy.

    interpolate_submobject(submob, start, target_copy, alpha)
        Interpolates an individual subobject between its starting and target
        states using path_func.

    Examples
    --------
    1. Transform a circle into a square
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class CircleToSquareExample(Scene):
        def construct(self):
            circle = Circle(color=BLUE)
            square = Square(color=YELLOW)

            self.add(circle)
            self.play(Transform(circle, square), run_time=3)
            self.wait()

    The circle gradually changes its geometry and visual properties toward
    those of the square. The original circle remains the animated object;
    the target is not automatically substituted into the scene by the base
    Transform cleanup behavior.

    2. Transform one mathematical expression into another
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class ExpressionTransformExample(Scene):
        def construct(self):
            source = Tex("x^2 + 2x + 1")
            target = Tex("(x + 1)^2")

            self.add(source)
            self.play(
                Transform(source, target),
                run_time=3,
            )
            self.wait()

    The source expression is transformed toward the target expression.
    For transformations that explicitly match corresponding text pieces,
    consider TransformMatchingStrings instead.

    3. Move a square along a curved path
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class CurvedTransformExample(Scene):
        def construct(self):
            square = Square(color=BLUE)
            target = square.copy().shift(RIGHT * 3 + UP)

            self.add(square)
            self.play(
                Transform(
                    square,
                    target,
                    path_arc=PI / 2,
                    run_time=3,
                )
            )
            self.wait()

    The nonzero path_arc selects a curved interpolation path. The exact
    trajectory depends on path_along_arc() and the selected path axis.

    4. Use a custom interpolation path
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class CustomPathExample(Scene):
        def construct(self):
            dot = Dot(LEFT * 2)
            target = Dot(RIGHT * 2 + UP)

            def custom_path(start, end, alpha):
                return interpolate(start, end, alpha) + (
                    0.5 * np.sin(PI * alpha) * UP
                )

            self.add(dot)
            self.play(
                Transform(
                    dot,
                    target,
                    path_func=custom_path,
                    run_time=3,
                )
            )
            self.wait()

    The supplied path function takes precedence over the default path
    selection. Its arguments and expected output must match the path
    function interface used by the installed ManimGL implementation.

    5. Replace the original object with the target
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class ReplaceTargetExample(Scene):
        def construct(self):
            source = Circle(color=BLUE)
            target = Square(color=GREEN)

            self.add(source)

            transform = Transform(source, target)
            transform.replace_mobject_with_target_in_scene = True

            self.play(transform, run_time=2)
            self.wait()

    Setting the replacement flag makes cleanup remove the original source
    and add the target object to the scene. This behavior is not enabled
    by default in the base Transform class.

    Notes
    -----
    - The target describes the desired final state; it is not necessarily
      the same Python object as the animated source.
    - When the source and target are not aligned, the implementation copies
      the target before aligning it. This protects the original target from
      structural changes caused by alignment.
    - The interpolation path affects how corresponding points move between
      their starting and target states. It does not necessarily imply that
      the entire Mobject follows one rigid-body trajectory.
    - The path_arc == 0.0 check specifically uses isinstance(path_arc,
      float). Other numeric types, such as some integer or NumPy scalar
      values, may follow the curved-path branch depending on their type.
    - A custom path_func bypasses the default path initialization.
    - update_config() recalculates the path function when path_arc is
      supplied. In this implementation, that branch constructs
      path_along_arc() directly, even when the supplied path_arc is zero.
    - get_all_families_zipped() aligns family members from the source,
      starting state, and target copy. The begin() alignment step helps
      ensure that these families can be interpolated consistently.
    - replace_mobject_with_target_in_scene defaults to False. Transform
      therefore does not automatically replace the original object with
      target_mobject during cleanup unless the flag is enabled.
    - If a subclass overrides create_target(), it should ensure that the
      returned target is valid before interpolation begins.
    - Use Transform for general state-to-state interpolation. Use specialized
      subclasses when you need a particular behavior, such as fading,
      matching text components, or moving along a predefined path.

    See Also
    --------
    Animation
        Base class providing timing, interpolation, and cleanup behavior.

    ReplacementTransform
        A specialized transformation that replaces the source with the
        target in the scene, when available in the installed version.

    TransformMatchingParts
        Matches and transforms individual components of compound Mobjects.

    TransformMatchingStrings
        Matches text substrings between StringMobject instances.

    MoveAlongPath
        Animates an object along a path.

    Mobject.interpolate
        Interpolates a Mobject between two states.
    """

    replace_mobject_with_target_in_scene: bool = False

    def __init__(
        self,
        mobject: Mobject,
        target_mobject: Mobject | None = None,
        path_arc: float | Tuple[float, float] = 0.0,
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
        elif isinstance(self.path_arc, float) and self.path_arc == 0:
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
            # Nothing to align, so nothing is done to the target and it can stand as it is
            self.target_copy = self.target_mobject
        else:
            # Use a copy of target_mobject for the align_data_and_family
            # call so that the actual target_mobject stays
            # preserved, since calling align_data will potentially
            # change the structure of both arguments
            self.target_copy = self.target_mobject.copy()
            self.mobject.align_data_and_family(self.target_copy)
        super().begin()

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

    def get_interpolation_ends(self) -> tuple[Mobject, Mobject]:
        return self.starting_mobject, self.target_copy

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
    """
    ReplacementTransform
    ====================

    A specialized subclass of Transform that replaces the original Mobject
    with the target Mobject in the scene when the animation finishes.

    ReplacementTransform performs the same state-to-state interpolation as
    Transform. Its defining difference is that the class-level attribute
    replace_mobject_with_target_in_scene is set to True. During cleanup, the
    original animated Mobject is removed from the scene and target_mobject
    is added in its place.

    This behavior is useful when an object should become a distinct target
    object rather than simply adopt the target's appearance while retaining
    its original scene identity.

    For example, a circle can transform into a square, one mathematical
    expression can be replaced by another, or one geometric construction
    can be replaced by a different construction.

    Parameters
    ----------
    mobject : Mobject
        The original object that will be animated toward the target's state.
        It is removed from the scene during cleanup when the replacement
        behavior is applied.

    target_mobject : Mobject or None, default=None
        The destination object whose state is used for interpolation and
        which is added to the scene during cleanup.

        The base Transform implementation requires a valid target. If None
        is supplied, a subclass must provide one through create_target().

    path_arc : float or tuple[float, float], default=0.0
        Controls the curvature of the interpolation path when the default
        path function is used. A floating-point value of 0.0 selects a
        straight path; other supported values are passed to
        path_along_arc().

    path_arc_axis : np.ndarray, default=OUT
        Axis used to construct the default curved interpolation path.

    path_func : Callable or None, default=None
        Optional custom interpolation-path function. When supplied, it
        takes precedence over the default path selection.

    **kwargs
        Additional keyword arguments forwarded to Transform and ultimately
        to Animation.__init__. These may include run_time, rate_func,
        remover, and other supported animation settings.

    Class Attributes
    ----------------
    replace_mobject_with_target_in_scene : bool, default=True
        Enables scene replacement during cleanup. After the animation's
        parent cleanup runs, the original Mobject is removed from the scene
        and target_mobject is added.

    Inherited Attributes
    --------------------
    target_mobject : Mobject or None
        The target state and the object added to the scene during cleanup.

    path_arc : float or tuple[float, float]
        Angular configuration for the default curved interpolation path.

    path_arc_axis : np.ndarray
        Axis used by the default curved path helper.

    path_func : Callable
        Function used to interpolate corresponding points during the
        transformation.

    target_copy : Mobject
        Target representation used during interpolation. Depending on
        whether the source and target are already aligned, this can refer
        directly to the target or to an aligned copy.

    starting_mobject : Mobject
        Captured starting state inherited from Animation.

    Implementation
    --------------
    ReplacementTransform does not define its own constructor or interpolation
    methods. It inherits these behaviors from Transform and changes the
    class-level replacement flag.

    The inherited lifecycle works as follows:

    1. Transform initializes the target and interpolation-path configuration.
    2. At begin(), it obtains and validates target_mobject.
    3. If necessary, it copies and aligns the target's family structure with
       the source so corresponding components can be interpolated.
    4. During the animation, the source is interpolated toward the target
       using Transform's interpolation machinery.
    5. During cleanup, Transform.clean_up_from_scene() invokes the parent
       cleanup and checks replace_mobject_with_target_in_scene.
    6. Because the flag is True for ReplacementTransform, the source
       Mobject is removed from the scene and target_mobject is added.

    Examples
    --------
    1. Replace a circle with a square
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class CircleToSquareReplacement(Scene):
        def construct(self):
            circle = Circle(color=BLUE)
            square = Square(color=YELLOW)

            self.add(circle)

            self.play(
                ReplacementTransform(circle, square),
                run_time=3,
            )

            self.wait()

    The circle transforms into the square, and the target square becomes
    the object present in the scene after cleanup.

    2. Replace one mathematical expression with another
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class ExpressionReplacement(Scene):
        def construct(self):
            expression = Tex("x^2 + 2x + 1")
            simplified = Tex("(x + 1)^2")

            self.add(expression)

            self.play(
                ReplacementTransform(
                    expression,
                    simplified,
                    run_time=3,
                )
            )

            self.wait()

    The original expression transforms toward the factored expression.
    After cleanup, the target expression is added to the scene.

    3. Replace a geometric construction
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class GeometryReplacement(Scene):
        def construct(self):
            triangle = Triangle(color=BLUE)
            square = Square(color=GREEN)

            self.add(triangle)

            self.play(
                ReplacementTransform(
                    triangle,
                    square,
                    path_arc=PI / 3,
                    run_time=2,
                )
            )

            self.wait()

    The transformation uses a curved interpolation path. Once it finishes,
    the target square replaces the original triangle in the scene.

    4. Replace a dot with a labeled point
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class DotToLabelReplacement(Scene):
        def construct(self):
            dot = Dot(ORIGIN, color=BLUE)
            labeled_point = VGroup(
                Dot(ORIGIN, color=RED),
                Text("A").scale(0.5).next_to(ORIGIN, UP),
            )

            self.add(dot)

            self.play(
                ReplacementTransform(
                    dot,
                    labeled_point,
                    run_time=2,
                )
            )

            self.wait()

    The dot transforms toward the grouped target. The target VGroup is added
    to the scene during cleanup.

    Notes
    -----
    - ReplacementTransform inherits the interpolation behavior of Transform.
      Its distinguishing feature is the replacement behavior during cleanup.
    - The target object is added to the scene after the original object is
      removed. The target is not necessarily the same Python object as the
      animated source.
    - If the target is already present in the scene, adding it again may
      produce scene-management behavior that depends on the Scene
      implementation. Avoid unnecessary duplicate additions.
    - The replacement flag is a class attribute, so instances inherit True
      unless it is overridden on the instance or by a subclass.
    - Setting replace_mobject_with_target_in_scene to False on an instance
      disables the replacement branch inherited from Transform.
    - The remover option inherited from Animation is separate from the
      replacement flag. The actual cleanup sequence depends on the parent
      Animation implementation.
    - Use Transform when you want to animate one object toward another
      without explicitly replacing the source with the target during
      cleanup.
    - Use ReplacementTransform when the target should become the scene's
      final object.

    See Also
    --------
    Transform
        Base class that implements target alignment and interpolation.

    TransformMatchingParts
        Transforms matched components of compound Mobjects.

    TransformMatchingStrings
        Matches substrings when transforming StringMobject instances.

    FadeTransform
        Combines fading behavior with a transformation.

    Animation
        Base class defining the animation lifecycle.
    """

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
    def __init__(self, *mobjects: Mobject, path_arc=90 * DEG, **kwargs):
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
