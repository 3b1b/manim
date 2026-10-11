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
    """
    TransformFromCopy
    =================

    Animate a copy of one Mobject into a target Mobject while preserving the
    original Mobject in the scene.

    TransformFromCopy is a specialized Transform animation that creates a copy
    of the source Mobject and animates that copy toward the target Mobject's
    appearance and geometry. Unlike a standard Transform, the original source
    Mobject is not directly transformed because the constructor passes
    mobject.copy() to the parent Transform constructor.

    This animation is useful when an object should appear to produce another
    object without losing or changing its original appearance. For example, a
    mathematical symbol can visually move toward a new expression while the
    original symbol remains visible.

    Parameters
    ----------
    mobject : Mobject
        The original source Mobject. Its copy is used as the starting object
        for the animation, leaving the original object itself unchanged by the
        transformation.

    target_mobject : Mobject
        The destination Mobject whose appearance and geometry the copied source
        approaches during the animation.

    **kwargs
        Additional keyword arguments forwarded to Transform through the parent
        constructor. These can include supported animation settings such as
        run_time, rate_func, and other Transform options.

    Attributes
    ----------
    replace_mobject_with_target_in_scene : bool
        Class-level setting inherited or defined for scene replacement behavior.
        It is set to True. At the end of the animation, the target Mobject
        replaces the animated copy in the scene. The original source Mobject
        remains separate from this replacement.

    Implementation Details
    ----------------------
    The constructor calls:

        super().__init__(mobject.copy(), target_mobject, **kwargs)

    The call to mobject.copy() is the key distinction from a regular Transform.
    The parent Transform receives a copy of the source object rather than the
    original source object.

    Consequently:
    - The original source Mobject is not the object being transformed.
    - The copied source is animated toward the target Mobject.
    - The target replaces the animated copy in the scene when the animation
      finishes, according to the replacement setting.
    - The original source can remain visible alongside the target.

    The source object should normally be present in the scene before the
    animation starts. The target is used as the destination and is typically
    added to the scene through the animation's replacement behavior.

    Examples
    --------
    Example 1: Transform a copy of a circle into a square.

        from manimlib import *

        class CopyTransformExample(Scene):
            def construct(self):
                circle = Circle(color=BLUE)
                square = Square(color=YELLOW).shift(RIGHT * 2)

                self.add(circle)
                self.play(TransformFromCopy(circle, square))
                self.wait()

    After the animation, the original circle remains on the left and the
    square appears on the right.

    Example 2: Copy a mathematical symbol into an expression.

        from manimlib import *

        class SymbolCopyExample(Scene):
            def construct(self):
                x = Tex("x").scale(1.5)
                expression = Tex("x^2").scale(1.5).shift(RIGHT * 3)

                self.add(x)
                self.play(TransformFromCopy(x, expression))
                self.wait()

    The animation uses a copy of x to form the destination expression while
    the original x remains in the scene.

    Example 3: Specify animation timing.

        self.play(
            TransformFromCopy(
                source,
                target,
                run_time=2,
                rate_func=smooth,
            )
        )

    The copied source animates for two seconds using the smooth rate function.

    Notes
    -----
    - TransformFromCopy does not mean that the target is copied. The source
      Mobject is copied, and that copy is animated toward the supplied target.
    - The original source is not directly modified by this animation's
      transformation because the parent receives a separate copy.
    - The copy operation follows the source Mobject's own copy behavior.
    - If the source contains submobjects, its copy generally includes the
      corresponding submobject structure.
    - The target should be configured with the intended final position,
      geometry, and appearance before the animation begins.
    - The class-level replacement setting is True, so the animated copy is
      replaced by the target in the scene at the end. This does not imply that
      the original source is removed.
    - If the original source should disappear or transform directly, consider
      using Transform or ReplacementTransform instead.
    - Exact visual interpolation depends on Transform's implementation and
      the structure of the source and target Mobjects.

    See Also
    --------
    Transform
        Animates a Mobject into another Mobject.
    ReplacementTransform
        Transforms a source Mobject and replaces it with the target.
    FadeTransform
        Uses a fading transformation between Mobjects.
    TransformMatchingParts
        Matches corresponding parts of two Mobjects during transformation.
    """

    replace_mobject_with_target_in_scene: bool = True

    def __init__(self, mobject: Mobject, target_mobject: Mobject, **kwargs):
        super().__init__(mobject.copy(), target_mobject, **kwargs)


class MoveToTarget(Transform):
    """
    MoveToTarget
    ============

    Animate a Mobject from its current state to a previously defined target
    state stored in its ``target`` attribute.

    MoveToTarget is a specialized Transform animation that uses the target
    Mobject associated with the source Mobject. Instead of passing the target
    as a separate argument, the animation retrieves it from ``mobject.target``.

    This class is useful when a Mobject's desired final state has already been
    prepared using a target-generation method such as ``generate_target()``.
    You can modify the generated target's position, scale, rotation, or other
    properties and then animate the original Mobject toward that prepared state.

    Parameters
    ----------
    mobject : Mobject
        The Mobject to animate. It must have a ``target`` attribute, typically
        created by calling ``mobject.generate_target()`` before constructing
        the animation.

    **kwargs
        Additional keyword arguments forwarded to the parent Transform
        constructor. These can include supported animation options such as
        ``run_time``, ``rate_func``, and other Transform configuration
        parameters.

    Attributes
    ----------
    target : Mobject
        This is not explicitly assigned by MoveToTarget itself. The class
        expects the supplied Mobject to already have a ``target`` attribute.
        The attribute is accessed and passed to Transform as the destination.

    Implementation Details
    ----------------------
    The constructor performs two operations:

    1. Calls ``check_validity_of_input(mobject)`` to verify that the source
       Mobject has a ``target`` attribute.
    2. Calls the parent constructor with ``mobject`` as the source and
       ``mobject.target`` as the destination.

    Conceptually, the implementation is equivalent to:

        Transform(mobject, mobject.target, **kwargs)

    The validation method checks only whether the ``target`` attribute exists.
    It does not verify that the attribute contains a valid Mobject or that
    the target has the intended geometry or appearance.

    If the attribute is missing, the method raises an Exception with the
    message:

        MoveToTarget called on mobject without attribute 'target'

    Example
    -------
    Move a circle to a new position using a generated target.

        from manimlib import *

        class MoveToTargetExample(Scene):
            def construct(self):
                circle = Circle(color=BLUE)
                self.add(circle)

                circle.generate_target()
                circle.target.shift(RIGHT * 3)
                circle.target.scale(1.5)

                self.play(MoveToTarget(circle))
                self.wait()

    In this example, ``generate_target()`` creates the target state. The target
    is then shifted to the right and enlarged. MoveToTarget animates the
    original circle toward that state.

    Example: Change Position and Rotation
    -------------------------------------
        from manimlib import *

        class MoveAndRotateExample(Scene):
            def construct(self):
                square = Square(color=YELLOW)
                self.add(square)

                square.generate_target()
                square.target.shift(UP * 2 + RIGHT)
                square.target.rotate(PI / 4)

                self.play(
                    MoveToTarget(
                        square,
                        run_time=2,
                        rate_func=smooth,
                    )
                )
                self.wait()

    The square moves toward the target's position and orientation over two
    seconds using the smooth rate function.

    Example: Scale a Mobject
    ------------------------
        circle = Circle()
        circle.generate_target()
        circle.target.scale(2)

        self.add(circle)
        self.play(MoveToTarget(circle))

    The circle animates toward the enlarged target state.

    Notes
    -----
    - Call ``generate_target()`` before using MoveToTarget unless another
      operation has already created a suitable ``target`` attribute.
    - Modify ``mobject.target`` rather than the original Mobject when preparing
      the destination state.
    - The validation checks only for the presence of the ``target`` attribute.
      An existing but unsuitable target may still cause problems later.
    - MoveToTarget uses the existing target object; it does not generate a new
      target automatically.
    - The original Mobject is the source of the Transform animation, so this
      class differs from TransformFromCopy, which transforms a copy.
    - Animation timing and interpolation behavior are provided by Transform.
    - The exact result depends on the properties configured on the target
      Mobject and the behavior of the parent Transform implementation.

    See Also
    --------
    Transform
        Animates one Mobject into another.
    MoveAlongPath
        Animates a Mobject along a specified path.
    TransformFromCopy
        Animates a copy of a source Mobject toward a target.
    ReplacementTransform
        Transforms a Mobject and replaces it with the target.
    """

    def __init__(self, mobject: Mobject, **kwargs):
        self.check_validity_of_input(mobject)
        super().__init__(mobject, mobject.target, **kwargs)

    def check_validity_of_input(self, mobject: Mobject) -> None:
        if not hasattr(mobject, "target"):
            raise Exception(
                "MoveToTarget called on mobject without attribute 'target'"
            )


class _MethodAnimation(MoveToTarget):
    """
    _MethodAnimation
    ================

    Internal animation class that applies a sequence of callable methods to a
    Mobject's prepared target state and animates the original Mobject toward
    that state.

    _MethodAnimation is a subclass of MoveToTarget. It stores a list of
    callable methods and delegates target validation and transformation setup
    to MoveToTarget.

    The class is intended as an internal building block for method-based
    animations. It relies on the source Mobject having a valid ``target``
    attribute, typically created using ``generate_target()``. The supplied
    methods are stored for use by the surrounding animation implementation;
    the constructor shown here does not execute them directly.

    Parameters
    ----------
    mobject : Mobject
        The Mobject to animate. It must have a ``target`` attribute because
        MoveToTarget validates this attribute during initialization.

    methods : list[Callable]
        A list of callable objects representing methods associated with the
        animation. The constructor stores this list in ``self.methods``.
        The exact arguments, execution order, and effects of these callables
        depend on the code that uses this class and are not defined by this
        constructor alone.

    **kwargs
        Additional keyword arguments forwarded to MoveToTarget and ultimately
        to the parent Transform constructor. These may include animation
        settings such as ``run_time`` and ``rate_func``.

    Attributes
    ----------
    methods : list[Callable]
        The list of callable methods passed to the constructor. The original
        list is assigned directly; this constructor does not copy it.

    Inherited Behavior
    ------------------
    _MethodAnimation inherits from MoveToTarget, which in turn inherits from
    Transform. Consequently, it uses the Mobject's ``target`` attribute as
    the destination of the transformation.

    During initialization, the following operations occur:

    1. The supplied methods list is assigned to ``self.methods``.
    2. The constructor calls ``MoveToTarget.__init__`` with the Mobject and
       any additional keyword arguments.
    3. MoveToTarget checks that the Mobject has a ``target`` attribute.
    4. If the check succeeds, MoveToTarget initializes Transform using the
       original Mobject and its target.

    The constructor does not explicitly invoke any callable in ``methods``.
    Any method application must occur elsewhere in the surrounding framework
    or in code that consumes this class.

    Example
    -------
    The following example demonstrates the constructor's required inputs.
    The methods are stored, while the target state is prepared separately.

        from manimlib import *

        class MethodAnimationExample(Scene):
            def construct(self):
                square = Square(color=BLUE)
                square.generate_target()
                square.target.shift(RIGHT * 2)

                methods = [
                    lambda mob: mob.shift(RIGHT),
                    lambda mob: mob.scale(1.5),
                ]

                animation = _MethodAnimation(square, methods)
                self.play(animation)
                self.wait()

    In this example, the target is shifted to the right before the animation
    is constructed. The callables are passed to the constructor and stored.
    However, this constructor alone does not execute those callables, so their
    presence does not automatically apply the listed operations.

    Notes
    -----
    - The leading underscore in ``_MethodAnimation`` indicates that the class
      is intended for internal use rather than as a primary public API.
    - The ``methods`` parameter is stored directly without being copied,
      validated, or executed by the shown constructor.
    - The constructor assumes that MoveToTarget's requirements are satisfied,
      including the existence of the Mobject's ``target`` attribute.
    - The target state must be prepared before initialization; this class does
      not call ``generate_target()`` itself.
    - The exact role of the stored methods cannot be determined from this
      constructor alone. Consult the surrounding implementation to establish
      where and how the callables are applied.
    - Transformation behavior, interpolation, and animation configuration
      are inherited from MoveToTarget and Transform.

    See Also
    --------
    MoveToTarget
        Animates a Mobject toward its prepared target state.
    Transform
        Animates a Mobject into another Mobject.
    TransformFromCopy
        Animates a copy of a Mobject toward a target.
    """

    def __init__(self, mobject: Mobject, methods: list[Callable], **kwargs):
        self.methods = methods
        super().__init__(mobject, **kwargs)


class ApplyMethod(Transform):
    """
    ApplyMethod
    ===========

    Animate the application of a Mobject method by transforming the original
    Mobject into a copy modified by that method.

    ApplyMethod is a subclass of Transform designed to animate method calls
    on Mobjects. Instead of manually creating a target Mobject, the caller
    provides a bound method and the arguments that should be passed to it.
    ApplyMethod creates a copy of the original Mobject, applies the method
    to that copy, and uses the modified copy as the transformation target.

    This allows operations such as shifting, scaling, rotating, and changing
    other Mobject properties to be animated through a method-call interface.

    Parameters
    ----------
    method : Callable
        A bound method belonging to a Mobject instance. The instance is
        available through ``method.__self__``, and the underlying function
        is available through ``method.__func__``.

        Pass the method itself without calling it. For example, use
        ``square.shift`` rather than ``square.shift(RIGHT)``.

    *args
        Positional arguments to pass to the method when it is applied to the
        copied target Mobject. If the final positional argument is a dictionary,
        that dictionary is removed from the positional arguments and expanded
        into keyword arguments for the method call.

    **kwargs
        Keyword arguments forwarded to the parent Transform constructor.
        These configure the animation itself, rather than the method being
        animated. Examples include ``run_time`` and ``rate_func``.

    Attributes
    ----------
    method : Callable
        The bound method supplied by the caller.

    method_args : tuple
        The positional arguments supplied to the constructor. These are stored
        as a tuple and converted to a list when the target is created.

    Inherited Attributes
    --------------------
    ApplyMethod inherits animation configuration and transformation behavior
    from Transform. The original Mobject is obtained from ``method.__self__``
    and passed to the parent constructor.

    Input Validation
    ----------------
    The constructor calls ``check_validity_of_input(method)`` before
    initializing Transform.

    The validation performs two checks:

    1. ``inspect.ismethod(method)`` must return True. Otherwise, an Exception
       is raised with the message:

           Whoops, looks like you accidentally invoked the method you want to animate

       This commonly catches cases where a method was called immediately
       instead of being passed as a bound method.

    2. The assertion verifies that ``method.__self__`` is an instance of
       Mobject. This ensures that the bound method belongs to a Mobject.

    These checks do not guarantee that the method arguments are valid or that
    the method will successfully execute on the copied Mobject.

    Target Creation
    ---------------
    The ``create_target()`` method constructs the destination Mobject.

    Its procedure is:

    1. Retrieve the stored bound method.
    2. Convert the stored arguments into a mutable list.
    3. If the last argument is a dictionary, remove it and use its entries as
       keyword arguments for the method call.
    4. Copy the original Mobject using ``method.__self__.copy()``.
    5. Call the underlying method function on the copy, passing the remaining
       positional arguments and any extracted keyword arguments.
    6. Return the modified copy as the target Mobject.

    The underlying function is invoked as:

        method.__func__(target, *args, **method_kwargs)

    Using ``method.__func__`` allows the method to operate on the copied
    Mobject rather than on the original instance.

    The implementation therefore depends on the method modifying the supplied
    Mobject appropriately. Although the class's original documentation notes
    that Mobject methods return the Mobject, the shown ``create_target()``
    implementation does not use the method's return value; it returns the
    modified copy directly.

    Examples
    --------
    Example 1: Animate a shift.

        from manimlib import *

        class ApplyMethodShiftExample(Scene):
            def construct(self):
                square = Square(color=BLUE)
                self.add(square)

                self.play(ApplyMethod(square.shift, RIGHT * 2))
                self.wait()

    The square is copied, the shift method is applied to the copy, and the
    original square is transformed toward the resulting target position.

    Example 2: Animate scaling.

        from manimlib import *

        class ApplyMethodScaleExample(Scene):
            def construct(self):
                circle = Circle(color=GREEN)
                self.add(circle)

                self.play(ApplyMethod(circle.scale, 2))
                self.wait()

    The target is created by scaling a copy of the circle by a factor of two.

    Example 3: Animate rotation with timing options.

        from manimlib import *

        class ApplyMethodRotateExample(Scene):
            def construct(self):
                square = Square(color=YELLOW)
                self.add(square)

                self.play(
                    ApplyMethod(
                        square.rotate,
                        PI / 4,
                        run_time=2,
                        rate_func=smooth,
                    )
                )
                self.wait()

    Here, ``PI / 4`` is passed to the rotation method, while ``run_time`` and
    ``rate_func`` configure the animation.

    Example 4: Pass keyword arguments to the Mobject method.

        from manimlib import *

        class ApplyMethodKeywordExample(Scene):
            def construct(self):
                square = Square(color=BLUE)
                self.add(square)

                self.play(
                    ApplyMethod(
                        square.set_color,
                        {"color": RED},
                        run_time=2,
                    )
                )
                self.wait()

    The final positional dictionary is interpreted as keyword arguments for
    ``set_color``. The ``run_time`` keyword is passed to Transform instead.

    Argument Handling
    -----------------
    ApplyMethod distinguishes between method arguments and animation options.

    Positional arguments following the method are stored in ``method_args``.
    If the final positional argument is a dictionary, its contents are
    expanded into keyword arguments when the method is applied to the target.

    For example:

        ApplyMethod(
            square.shift,
            RIGHT,
            {"something": value},
            run_time=2,
        )

    The dictionary is treated as method keyword arguments, whereas
    ``run_time=2`` is treated as an animation configuration option.

    A dictionary intended as the final positional argument cannot be passed
    through unchanged as an ordinary positional argument using this interface:
    the implementation specifically interprets it as keyword arguments.

    Notes
    -----
    - Pass a bound Mobject method without invoking it.
    - ``square.shift`` is appropriate; ``square.shift(RIGHT)`` invokes the
      method immediately and usually does not provide the required bound
      method object.
    - The method is applied to a copy of the original Mobject when the target
      is created, helping preserve the original state while preparing the
      transformation destination.
    - The method must be compatible with the copied Mobject and the supplied
      arguments.
    - The final dictionary in ``*args``, if present, is unpacked as keyword
      arguments for the method.
    - Animation configuration keywords must be passed directly to
      ApplyMethod, not placed in the method-argument dictionary.
    - The implementation shown uses ``inspect.ismethod`` and assumes that
      ``inspect`` is available in the module.
    - The precise animation interpolation and final scene behavior depend on
      the inherited Transform implementation.
    - ApplyMethod is useful for animating one method call. For more complex
      sequences of method operations, inspect the related method-animation
      classes available in the codebase.

    See Also
    --------
    Transform
        Animates a Mobject into a target Mobject.
    _MethodAnimation
        Internal method-related animation class.
    MoveToTarget
        Animates a Mobject toward its prepared target state.
    ApplyFunction
        Related animation interface for applying a function to a Mobject,
        if available in the codebase.
    """

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
    """
    ApplyPointwiseFunction
    ======================

    Animate a Mobject by applying a pointwise function to its points and
    transforming its geometry toward the resulting shape.

    ApplyPointwiseFunction is a subclass of ApplyMethod. It provides a
    convenient interface for animating geometric transformations defined by
    a function that maps one NumPy coordinate array to another.

    Instead of manually constructing a target Mobject, the caller supplies
    a pointwise function and the Mobject to transform. The class delegates
    the transformation to the Mobject's ``apply_function`` method through
    ApplyMethod, which prepares a transformed copy and animates the original
    Mobject toward it.

    This class is useful for visualizing geometric mappings, coordinate
    transformations, deformations, and other operations in which each point
    of a Mobject is mapped to a new position.

    Parameters
    ----------
    function : Callable[[np.ndarray], np.ndarray]
        A callable that accepts a NumPy coordinate array representing a point
        and returns a NumPy coordinate array representing its transformed
        position.

        For a typical three-dimensional Mobject, the input and output arrays
        contain x, y, and z coordinates. The function should return a
        coordinate array compatible with the Mobject's point representation.

    mobject : Mobject
        The Mobject whose geometry will be transformed by the pointwise
        function. Its ``apply_function`` method is used to construct the
        transformed target.

    run_time : float, default=3.0
        Duration of the animation in seconds. The default duration is
        3 seconds.

    **kwargs
        Additional keyword arguments forwarded to ApplyMethod and ultimately
        to Transform. These can configure the animation, for example through
        ``rate_func`` or other supported Transform options.

    Inheritance
    -----------
    ApplyPointwiseFunction inherits from ApplyMethod, which inherits from
    Transform. The constructor delegates the work using:

        super().__init__(
            mobject.apply_function,
            function,
            run_time=run_time,
            **kwargs,
        )

    Here, ``mobject.apply_function`` is the bound method being animated, and
    ``function`` is passed as its argument.

    ApplyMethod creates a copy of the source Mobject and applies the method
    to that copy to produce the target. The original Mobject is then animated
    toward the target using Transform's behavior.

    How the Pointwise Mapping Works
    -------------------------------
    A pointwise function describes how individual coordinates change.

    For example, a function might map each point

        (x, y, z)

    to

        (x, y + 0.5 * sin(x), z)

    This leaves the x and z coordinates unchanged while shifting the y
    coordinate according to the point's x-coordinate. Applying this mapping
    to a Mobject can produce a wave-like deformation.

    The function is supplied to ``mobject.apply_function``. The exact
    sampling, point handling, and interpolation behavior are determined by
    the Mobject implementation and the inherited animation classes.

    Examples
    --------
    Example 1: Apply a simple coordinate transformation.

        from manimlib import *
        import numpy as np

        class PointwiseShiftExample(Scene):
            def construct(self):
                grid = NumberPlane()
                self.add(grid)

                def shift_points(point):
                    return point + np.array([1, 0, 0])

                self.play(
                    ApplyPointwiseFunction(
                        shift_points,
                        grid,
                        run_time=2,
                    )
                )
                self.wait()

    This maps every point one unit to the right. The transformation is
    applied to a copy of the grid to prepare the target, and the original
    grid animates toward that target.

    Example 2: Create a wave-like deformation.

        from manimlib import *
        import numpy as np

        class PointwiseWaveExample(Scene):
            def construct(self):
                grid = NumberPlane()
                self.add(grid)

                def wave(point):
                    x, y, z = point
                    return np.array([
                        x,
                        y + 0.5 * np.sin(x),
                        z,
                    ])

                self.play(
                    ApplyPointwiseFunction(
                        wave,
                        grid,
                        run_time=3,
                    )
                )
                self.wait()

    Each point's y-coordinate is adjusted according to its x-coordinate,
    producing a wave-like geometric deformation.

    Example 3: Apply a rotation in the xy-plane.

        from manimlib import *
        import numpy as np

        class PointwiseRotationExample(Scene):
            def construct(self):
                square = Square()
                self.add(square)

                angle = PI / 4

                def rotate_point(point):
                    x, y, z = point
                    return np.array([
                        x * np.cos(angle) - y * np.sin(angle),
                        x * np.sin(angle) + y * np.cos(angle),
                        z,
                    ])

                self.play(
                    ApplyPointwiseFunction(
                        rotate_point,
                        square,
                        run_time=2,
                    )
                )
                self.wait()

    This rotates each point around the origin in the xy-plane while leaving
    its z-coordinate unchanged.

    Notes
    -----
    - The function should return a valid NumPy coordinate array compatible
      with the input point.
    - The mapping is applied through ``mobject.apply_function`` rather than
      by directly modifying the source Mobject in the constructor.
    - The function defines the destination geometry; Transform controls the
      animation from the original geometry to that destination.
    - The default animation duration is 3 seconds, unless overridden.
    - Pointwise transformations can distort shapes significantly. For a
      continuous-looking deformation, the Mobject may need enough points or
      sufficiently dense geometry.
    - The function may be called many times, once for different points of
      the Mobject. Avoid relying on it being called only once.
    - The examples assume that NumPy is available as ``np`` and that the
      relevant ManimGL classes are imported.
    - The constructor shown does not validate the mathematical properties of
      the supplied function, such as continuity, invertibility, or whether
      it preserves distances.
    - Exact rendering and interpolation details depend on the implementations
      of ``apply_function``, ApplyMethod, and Transform.

    See Also
    --------
    ApplyMethod
        Animates the application of a method to a Mobject.
    Transform
        Animates a Mobject toward a target Mobject.
    MoveToTarget
        Animates a Mobject toward a previously prepared target state.
    ComplexHomotopy
        Related animation for point transformations expressed through complex
        coordinates, if available in the codebase.
    """

    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        run_time: float = 3.0,
        **kwargs
    ):
        super().__init__(mobject.apply_function, function, run_time=run_time, **kwargs)


class ApplyPointwiseFunctionToCenter(Transform):
    """
    ApplyPointwiseFunctionToCenter
    ==============================

    Animate a Mobject by moving its center to the position returned by a
    function applied to its current center.

    ApplyPointwiseFunctionToCenter is a subclass of Transform. It accepts a
    function that maps a NumPy coordinate array to another coordinate array,
    evaluates that function at the center of the supplied Mobject, and uses
    the resulting position to create a target Mobject.

    Unlike ApplyPointwiseFunction, which applies a function to the points
    defining a Mobject's geometry, this class applies the function only to
    the Mobject's center. It then moves a copy of the entire Mobject so that
    its center reaches the computed destination.

    Consequently, the Mobject's overall shape and internal geometry are
    preserved by the target-creation step; the function determines the
    destination of the Mobject rather than deforming its individual points.

    Parameters
    ----------
    function : Callable[[np.ndarray], np.ndarray]
        A callable that accepts a NumPy coordinate array representing the
        Mobject's center and returns a NumPy coordinate array representing
        the desired destination center.

        For a typical three-dimensional Mobject, the input and output arrays
        contain x, y, and z coordinates. The returned coordinates should be
        compatible with the coordinate system used by the Mobject.

    mobject : Mobject
        The Mobject to animate. Its current center is obtained through
        ``mobject.get_center()``.

    **kwargs
        Additional keyword arguments forwarded to the parent Transform
        constructor. These can include supported animation settings such as
        ``run_time`` and ``rate_func``.

    Attributes
    ----------
    function : Callable[[np.ndarray], np.ndarray]
        The function supplied to the constructor. It is stored as
        ``self.function`` and used when the target is created.

    Inherited Attributes
    --------------------
    The class inherits animation behavior and configuration from Transform.
    The source Mobject is passed to the parent constructor, while the target
    is generated by the overridden ``create_target()`` method.

    Implementation Details
    ----------------------
    The constructor performs two operations:

    1. Stores the supplied function in ``self.function``.
    2. Initializes Transform with the source Mobject and any additional
       animation configuration options.

    The target is created by:

        return self.mobject.copy().move_to(
            self.function(self.mobject.get_center())
        )

    This operation follows three steps:

    1. Obtain the source Mobject's current center using ``get_center()``.
    2. Pass that center to the supplied function to calculate a destination
       coordinate.
    3. Copy the source Mobject and move the copy so that its center is at
       the returned coordinate.

    The function is therefore evaluated on the original Mobject's center,
    and the returned position is used as the destination for the copied
    Mobject.

    Examples
    --------
    Example 1: Move a circle according to a center-based function.

        from manimlib import *
        import numpy as np

        class CenterFunctionExample(Scene):
            def construct(self):
                circle = Circle(color=BLUE)
                self.add(circle)

                def move_center(center):
                    return center + np.array([2, 1, 0])

                self.play(
                    ApplyPointwiseFunctionToCenter(
                        move_center,
                        circle,
                        run_time=2,
                    )
                )
                self.wait()

    The function adds two units to the x-coordinate and one unit to the
    y-coordinate of the circle's center. The circle's shape is preserved
    while its center moves to the computed destination.

    Example 2: Map the center to a fixed point.

        from manimlib import *

        class CenterToPointExample(Scene):
            def construct(self):
                square = Square(color=YELLOW)
                self.add(square)

                def destination(center):
                    return RIGHT * 3 + UP

                self.play(
                    ApplyPointwiseFunctionToCenter(
                        destination,
                        square,
                        run_time=2,
                    )
                )
                self.wait()

    Regardless of the square's starting center, the function returns the
    fixed coordinate represented by ``RIGHT * 3 + UP``. The square moves so
    that its center reaches that point.

    Example 3: Reflect the center across the y-axis.

        from manimlib import *
        import numpy as np

        class CenterReflectionExample(Scene):
            def construct(self):
                dot = Dot(point=[2, 1, 0])
                self.add(dot)

                def reflect_center(center):
                    x, y, z = center
                    return np.array([-x, y, z])

                self.play(
                    ApplyPointwiseFunctionToCenter(
                        reflect_center,
                        dot,
                        run_time=2,
                    )
                )
                self.wait()

    The function negates the x-coordinate of the center while preserving
    the y- and z-coordinates. The dot moves to the reflected center position.

    Notes
    -----
    - The supplied function is applied only to the result of
      ``mobject.get_center()``. It is not applied independently to every
      point of the Mobject.
    - The target is a copy of the source Mobject, moved to the computed
      destination center.
    - Since the target is moved as a whole, the function does not directly
      define a rotation, scaling, or deformation of the Mobject's geometry.
    - The function should return a valid coordinate accepted by the
      Mobject's ``move_to()`` method.
    - The implementation does not explicitly validate the function's input
      or output, so incompatible return values may cause errors.
    - The function is evaluated when the target is created, not continuously
      during every animation frame by this class's own implementation.
    - The animation's duration, interpolation, and final scene behavior are
      controlled by Transform and the supplied keyword arguments.
    - The resulting motion depends on the difference between the original
      center and the computed destination center.

    See Also
    --------
    ApplyPointwiseFunction
        Applies a coordinate mapping to the points of a Mobject's geometry.
    ApplyMethod
        Animates the application of a method to a Mobject.
    Transform
        Animates a Mobject toward a target Mobject.
    MoveToTarget
        Animates a Mobject toward its prepared target state.
    """

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
    """
    FadeToColor
    ===========

    Animate a Mobject's color from its current appearance to a specified
    target color.

    FadeToColor is a subclass of ApplyMethod that uses the Mobject's
    ``set_color()`` method to prepare a target copy with the requested color.
    The inherited ApplyMethod behavior then animates the original Mobject
    toward that target using Transform.

    Despite its name, FadeToColor does not simply fade a Mobject's opacity
    to transparent or make it disappear. It animates a color change, allowing
    the object to transition from its existing color toward the specified
    color.

    Parameters
    ----------
    mobject : Mobject
        The Mobject whose color should be changed. Its ``set_color()`` method
        is used to prepare the target appearance.

    color : ManimColor
        The destination color for the Mobject. This should be a color value
        accepted by the Mobject's ``set_color()`` method, such as ``RED``,
        ``BLUE``, or a supported ManimColor instance.

    **kwargs
        Additional keyword arguments forwarded to ApplyMethod and ultimately
        to Transform. These can include animation configuration options such
        as ``run_time`` and ``rate_func``.

    Inheritance
    -----------
    FadeToColor inherits from ApplyMethod, which inherits from Transform.

    Its constructor delegates to the parent using:

        super().__init__(mobject.set_color, color, **kwargs)

    Here, ``mobject.set_color`` is passed as a bound method, and ``color`` is
    passed as the method argument. ApplyMethod creates a copy of the original
    Mobject, applies ``set_color(color)`` to that copy, and uses the modified
    copy as the transformation target.

    The original Mobject is then animated toward the target appearance.

    Examples
    --------
    Example 1: Change a circle from blue to red.

        from manimlib import *

        class FadeToColorExample(Scene):
            def construct(self):
                circle = Circle(color=BLUE)
                self.add(circle)

                self.play(FadeToColor(circle, RED))
                self.wait()

    The circle animates toward the red target appearance.

    Example 2: Animate a color change with custom timing.

        from manimlib import *

        class TimedColorChangeExample(Scene):
            def construct(self):
                square = Square(color=YELLOW)
                self.add(square)

                self.play(
                    FadeToColor(
                        square,
                        PURPLE,
                        run_time=2,
                        rate_func=smooth,
                    )
                )
                self.wait()

    The square transitions toward purple over two seconds using the smooth
    rate function.

    Example 3: Change the color of text.

        from manimlib import *

        class TextColorChangeExample(Scene):
            def construct(self):
                text = Text("Hello, ManimGL!", color=WHITE)
                self.add(text)

                self.play(FadeToColor(text, GREEN))
                self.wait()

    The text animates toward the target color.

    Notes
    -----
    - FadeToColor changes color rather than directly animating opacity.
    - The destination appearance is prepared by calling ``set_color()`` on
      a copy of the original Mobject through ApplyMethod.
    - The color transition is performed through Transform's interpolation
      behavior; it is not implemented as a direct per-frame call to
      ``set_color()`` by FadeToColor itself.
    - The actual visual result depends on the Mobject's structure and how
      its ``set_color()`` method applies color to its points and submobjects.
    - For Mobjects with multiple submobjects or independently styled parts,
      the resulting appearance depends on the behavior of ``set_color()``.
    - The supplied color must be compatible with the color system used by
      the installed ManimGL version.
    - Use ``FadeIn`` or ``FadeOut`` when the intended effect is to make an
      object appear or disappear rather than change its color.
    - Animation duration and interpolation can be customized through the
      inherited Transform options.

    See Also
    --------
    ApplyMethod
        Animates the application of a Mobject method.
    Transform
        Animates a Mobject toward a target Mobject.
    FadeIn
        Animates a Mobject into view.
    FadeOut
        Animates a Mobject out of view.
    """

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
