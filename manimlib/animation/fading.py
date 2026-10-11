from __future__ import annotations

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.animation.transform import Transform
from manimlib.constants import ORIGIN
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.mobject import Group
from manimlib.utils.bezier import interpolate
from manimlib.utils.rate_functions import there_and_back

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.mobject.mobject import Mobject
    from manimlib.scene.scene import Scene
    from manimlib.typing import Vect3


class Fade(Transform):
    """
    Animates a Mobject by transforming it while applying a positional shift and
    a scale factor.

    Fade extends Transform and stores a shift vector and scale factor before
    forwarding the Mobject and additional arguments to Transform. The exact
    transformation behavior depends on how the parent Transform class uses these
    attributes.

    Parameters
    ----------
    mobject : Mobject
        The object to animate.

    shift : np.ndarray, optional
        Vector describing the positional shift associated with the animation.
        Defaults to ORIGIN, meaning a zero displacement.

    scale : float, optional
        Scale factor associated with the animation. Defaults to 1, meaning the
        original scale.

    **kwargs
        Additional keyword arguments forwarded to Transform.

    Attributes
    ----------
    shift_vect : np.ndarray
        Stores the supplied shift vector.

    scale_factor : float
        Stores the supplied scale factor.

    Notes
    -----
    - Fade inherits its transformation lifecycle and interpolation behavior from
      Transform.
    - The constructor stores shift in self.shift_vect and scale in
      self.scale_factor.
    - This class does not directly modify the Mobject's position or scale in the
      supplied implementation; it passes the Mobject to Transform after storing
      these values.
    - The actual visual result depends on the parent Transform implementation.

    Examples
    --------
    Example 1: Create a Fade animation with default values.

        >>> fade = Fade(circle)

    Here, circle is the Mobject being animated. Since shift defaults to ORIGIN
    and scale defaults to 1, no additional displacement or scaling is requested
    through these parameters.

    Example 2: Configure a shift to the right.

        >>> fade = Fade(circle, shift=RIGHT)

    The shift vector is stored in fade.shift_vect. How it affects the animation
    depends on the Transform implementation.

    Example 3: Configure a scale factor of 0.5.

        >>> fade = Fade(circle, scale=0.5)

    The scale factor is stored in fade.scale_factor. A value of 0.5 represents
    half the original scale if the parent transformation uses this attribute
    as a scale factor.

    Example 4: Combine a shift and a scale factor.

        >>> fade = Fade(
        ...     circle,
        ...     shift=UP,
        ...     scale=0.5,
        ...     run_time=2,
        ... )

    This constructs the animation with both parameters and requests a two-second
    runtime from the parent class.

    In these examples, circle must be a defined Mobject, and RIGHT and UP must
    be available direction vectors.

    See Also
    --------
    Transform
    Mobject
    """

    def __init__(
        self,
        mobject: Mobject,
        shift: np.ndarray = ORIGIN,
        scale: float = 1,
        **kwargs
    ):
        self.shift_vect = shift
        self.scale_factor = scale
        super().__init__(mobject, **kwargs)


class FadeIn(Fade):
    """
    Animates a Mobject into view by transitioning it from a modified starting
    state to its original appearance.

    FadeIn extends Fade. It creates a copy of the original Mobject as the target,
    then constructs a starting Mobject that is fully transparent, inversely
    scaled by the configured scale factor, and shifted in the opposite direction
    to the configured shift vector.

    The animation interpolates from this starting state toward the target using
    the transformation behavior inherited from Transform.

    Parameters
    ----------
    mobject : Mobject
        The object to animate into view.

    shift : np.ndarray, optional
        Vector describing the direction and distance from which the object
        starts moving toward its target. Defaults to ORIGIN, so no positional
        shift is applied.

    scale : float, optional
        Scale factor used to determine the starting object's size. Defaults to 1.
        The starting Mobject is scaled by 1.0 / scale.

    **kwargs
        Additional keyword arguments forwarded through Fade to Transform.

    Attributes
    ----------
    shift_vect : np.ndarray
        Inherited from Fade. Stores the requested shift vector.

    scale_factor : float
        Inherited from Fade. Stores the scale factor used to construct the
        starting Mobject.

    Methods
    -------
    create_target()
        Returns a copy of the original Mobject. This copy represents the target
        appearance of the animation.

    create_starting_mobject()
        Creates the starting state by calling the parent implementation,
        setting its opacity to zero, scaling it by the reciprocal of
        scale_factor, and shifting it by the negative of shift_vect.

    Notes
    -----
    - The target is a copy of the original Mobject.
    - The starting Mobject has zero opacity.
    - The starting scale is determined by 1.0 / scale_factor.
    - The starting position is offset by -shift_vect.
    - The actual transition between the starting state and target is handled by
      the inherited Transform implementation.
    - A scale_factor of zero causes division by zero when the starting Mobject
      is constructed, so it should not be used.

    Examples
    --------
    Example 1: Fade in a circle with default settings.

        >>> animation = FadeIn(circle)

    The circle starts transparent and transitions toward its original appearance.
    Because the default shift is ORIGIN and scale is 1, no additional starting
    offset or size change is applied.

    Example 2: Fade in while moving upward.

        >>> animation = FadeIn(circle, shift=UP)

    The starting Mobject is shifted by -UP, so it begins below its target and
    moves toward the original position during the transformation.

    Example 3: Fade in while scaling up.

        >>> animation = FadeIn(circle, scale=0.5)

    The starting Mobject is scaled by 1 / 0.5 = 2, so it starts at twice the
    target's scale and transitions toward the target.

    Example 4: Combine shifting and scaling.

        >>> animation = FadeIn(
        ...     circle,
        ...     shift=RIGHT,
        ...     scale=0.5,
        ...     run_time=2,
        ... )

    The starting Mobject is transparent, shifted left by the RIGHT vector, and
    scaled to twice its target size. It then transitions toward the target over
    the requested runtime.

    These examples illustrate construction only; circle must be a defined
    Mobject, and direction vectors such as UP and RIGHT must be available.

    See Also
    --------
    Fade
    FadeOut
    Transform
    Mobject
    """

    def create_target(self) -> Mobject:
        return self.mobject.copy()

    def create_starting_mobject(self) -> Mobject:
        start = super().create_starting_mobject()
        start.set_opacity(0)
        start.scale(1.0 / self.scale_factor)
        start.shift(-self.shift_vect)
        return start


class FadeOut(Fade):
    """
    Animates a Mobject out of view by transitioning it toward a transparent,
    shifted, and scaled target state.

    FadeOut extends Fade. It creates a copy of the original Mobject, makes the
    copy fully transparent, shifts it by the configured shift vector, and scales
    it by the configured scale factor. The inherited Transform behavior then
    interpolates the original Mobject toward this target state.

    Parameters
    ----------
    mobject : Mobject
        The object to animate out of view.

    shift : Vect3, optional
        Vector describing the displacement applied to the target Mobject.
        Defaults to ORIGIN, meaning no positional shift.

    remover : bool, optional
        Whether the animation should remove the Mobject from the scene when it
        finishes. Defaults to True.

    final_alpha_value : float, optional
        Final alpha value used by the parent animation implementation.
        Defaults to 0.0. The supplied code forwards this value to Fade/Transform.

    **kwargs
        Additional keyword arguments forwarded through Fade to Transform.

    Attributes
    ----------
    shift_vect : np.ndarray
        Inherited from Fade. Stores the shift vector applied to the target.

    scale_factor : float
        Inherited from Fade. Stores the scale factor applied to the target.

    Methods
    -------
    create_target()
        Creates a copy of the original Mobject, sets its opacity to zero, shifts
        it by shift_vect, scales it by scale_factor, and returns the resulting
        target Mobject.

    Notes
    -----
    - The original Mobject is copied before its target state is modified.
    - The target's opacity is set to zero, making it fully transparent.
    - The target is shifted by shift_vect.
    - The target is scaled by scale_factor.
    - The actual transition from the original state to the target is handled by
      the inherited Transform implementation.
    - With the default remover=True, the animation is configured to remove the
      Mobject from the scene when it finishes.
    - Setting remover=False disables that automatic removal behavior.
    - The scale parameter defaults to 1 in Fade, so FadeOut does not change the
      target's scale unless a different value is supplied.
    - final_alpha_value is passed to the parent implementation; its precise
      effect depends on the implementation of Fade and Transform.

    Examples
    --------
    Example 1: Fade out a circle without moving or scaling it.

        >>> animation = FadeOut(circle)

    The target is a transparent copy at the same position and scale. By default,
    the original Mobject is removed from the scene when the animation finishes.

    Example 2: Fade out while moving to the right.

        >>> animation = FadeOut(circle, shift=RIGHT)

    The target copy is shifted by RIGHT while becoming transparent.

    Example 3: Fade out while shrinking.

        >>> animation = FadeOut(circle, scale=0.5)

    The target copy is scaled to half its original size and made transparent.

    Example 4: Keep the Mobject in the scene after the animation.

        >>> animation = FadeOut(circle, remover=False)

    The animation is configured not to remove the Mobject automatically when it
    finishes.

    Example 5: Combine displacement and scaling.

        >>> animation = FadeOut(
        ...     circle,
        ...     shift=UP,
        ...     scale=0.5,
        ...     run_time=2,
        ... )

    The target is transparent, shifted upward, and scaled to half its original
    size.

    These examples illustrate construction only; circle must be a defined
    Mobject, and direction vectors such as RIGHT and UP must be available.

    See Also
    --------
    Fade
    FadeIn
    Transform
    Mobject
    """

    def __init__(
        self,
        mobject: Mobject,
        shift: Vect3 = ORIGIN,
        remover: bool = True,
        final_alpha_value: float = 0.0,  # Put it back in original state when done,
        **kwargs
    ):
        super().__init__(
            mobject, shift,
            remover=remover,
            final_alpha_value=final_alpha_value,
            **kwargs
        )

    def create_target(self) -> Mobject:
        result = self.mobject.copy()
        result.set_opacity(0)
        result.shift(self.shift_vect)
        result.scale(self.scale_factor)
        return result


class FadeInFromPoint(FadeIn):
    """
    Animates a Mobject into view from a specified point.

    FadeInFromPoint extends FadeIn and configures the starting state so that
    the Mobject begins at the supplied point and transitions toward its original
    position. It calculates the shift vector as the difference between the
    Mobject's center and the specified point, then passes an infinite scale
    factor to FadeIn.

    Parameters
    ----------
    mobject : Mobject
        The object to animate into view.

    point : Vect3
        The point from which the object should appear. The shift vector is
        calculated as mobject.get_center() - point.

    **kwargs
        Additional keyword arguments forwarded to FadeIn, such as run_time
        or rate_func.

    Notes
    -----
    - The class inherits its animation behavior from FadeIn and Fade.
    - The shift is calculated automatically; callers do not supply shift
      directly to this constructor.
    - FadeIn's starting Mobject is shifted by the negative of the calculated
      shift vector. This places its starting center at the specified point.
    - The scale factor is set to np.inf. In FadeIn.create_starting_mobject(),
      the starting Mobject is scaled by 1.0 / scale_factor, which evaluates to
      zero for an infinite scale factor.
    - A zero scale factor can be problematic for some Mobject implementations.
      The exact visual result depends on how the underlying scaling operation
      handles a scale of zero.
    - This class does not define its own target or interpolation methods.

    Examples
    --------
    Example 1: Make a circle appear from the origin.

        >>> animation = FadeInFromPoint(circle, ORIGIN)

    The animation calculates the displacement from the origin to the circle's
    center and uses that to configure the starting state.

    Example 2: Make a square appear from a point above it.

        >>> animation = FadeInFromPoint(square, 2 * UP)

    The square's starting position is configured around the point 2 * UP, then
    the inherited FadeIn animation transitions toward the original square.

    Example 3: Set a custom runtime.

        >>> animation = FadeInFromPoint(
        ...     circle,
        ...     point=LEFT,
        ...     run_time=2,
        ... )

    The animation is configured to begin from LEFT and use a two-second runtime.

    These examples illustrate construction only; circle, square, and direction
    vectors must be defined in the surrounding scene.

    See Also
    --------
    FadeIn
    FadeOut
    Fade
    Transform
    Mobject
    """

    def __init__(self, mobject: Mobject, point: Vect3, **kwargs):
        super().__init__(
            mobject,
            shift=mobject.get_center() - point,
            scale=np.inf,
            **kwargs,
        )

class FadeOutToPoint(FadeOut):
    """
    Animates a Mobject out of view toward a specified point.

    FadeOutToPoint extends FadeOut and calculates a shift vector that moves the
    Mobject's center toward the given point. It also sets the scale factor to
    zero, so the target copy collapses to zero scale while becoming transparent.

    Parameters
    ----------
    mobject : Mobject
        The object to animate out of view.

    point : Vect3
        The destination point toward which the Mobject moves. The shift vector
        is calculated as point - mobject.get_center().

    **kwargs
        Additional keyword arguments forwarded to FadeOut, such as run_time,
        rate_func, or remover.

    Notes
    -----
    - The class inherits its target creation and interpolation behavior from
      FadeOut, Fade, and Transform.
    - The shift vector is calculated automatically from the Mobject's current
      center and the specified destination point.
    - FadeOut.create_target() applies this shift to the copied Mobject.
    - The scale factor is set to zero, so the target copy is scaled to zero.
    - The target copy is also assigned zero opacity by FadeOut.create_target().
    - With FadeOut's default remover=True, the original Mobject is configured
      to be removed from the scene when the animation finishes.
    - Because scaling to zero can collapse the target geometry, the exact visual
      result depends on the Mobject and the parent Transform implementation.

    Examples
    --------
    Example 1: Make a circle disappear toward the origin.

        >>> animation = FadeOutToPoint(circle, ORIGIN)

    The target is shifted so that its center moves toward the origin, while
    the target copy becomes transparent and collapses to zero scale.

    Example 2: Make a square disappear toward a point above it.

        >>> animation = FadeOutToPoint(square, 2 * UP)

    The destination is 2 * UP. The class calculates the necessary shift from
    the square's current center.

    Example 3: Keep the Mobject in the scene after the animation.

        >>> animation = FadeOutToPoint(
        ...     circle,
        ...     point=LEFT,
        ...     remover=False,
        ...     run_time=2,
        ... )

    The animation is configured to move the circle toward LEFT over two seconds
    without automatically removing it from the scene at completion.

    These examples illustrate construction only; circle, square, and direction
    vectors must be defined in the surrounding scene.

    See Also
    --------
    FadeOut
    FadeInToPoint
    Fade
    Transform
    Mobject
    """

    def __init__(self, mobject: Mobject, point: Vect3, **kwargs):
        super().__init__(
            mobject,
            shift=point - mobject.get_center(),
            scale=0,
            **kwargs,
        )


class FadeTransform(Transform):
    """
    Transforms one Mobject into another by crossfading between their appearances.

    FadeTransform extends Transform but prepares a grouped object containing the
    source Mobject and a copy of the target Mobject. It aligns transparent
    "ghost" copies at the beginning and ending states so the source appears to
    fade into the target.

    Parameters
    ----------
    mobject : Mobject
        The original object being transformed. Its state is saved before the
        animation begins so that it can be restored during cleanup.

    target_mobject : Mobject
        The object that should appear as the result of the transformation.
        The supplied object is stored for completion handling, while a copy is
        placed inside the animation's group.

    stretch : bool, optional
        Whether source.replace() may stretch the source geometry to match the
        target geometry. Defaults to True.

    dim_to_match : int, optional
        Dimension used by source.replace() when matching the target. Defaults
        to 1. Its exact interpretation depends on Mobject.replace().

    **kwargs
        Additional keyword arguments forwarded to Transform.

    Attributes
    ----------
    to_add_on_completion : Mobject
        Reference to the original target_mobject supplied to the constructor.

    stretch : bool
        Controls whether ghost objects are stretched when matched to their
        corresponding targets.

    dim_to_match : int
        Dimension setting forwarded to Mobject.replace().

    Methods
    -------
    begin()
        Creates the ending Mobject, initializes the animation, prepares the
        transparent ghost objects at both endpoints, and refreshes interpolation
        preparation after modifying those endpoints.

    ghost_to(source, target)
        Makes source match the target's geometry according to stretch and
        dim_to_match, copies the target's uniforms to source, and sets source's
        opacity to zero.

    get_all_mobjects()
        Returns the grouped animated Mobject, starting Mobject, and ending
        Mobject.

    get_all_families_zipped()
        Uses Animation.get_all_families_zipped() to obtain the zipped family
        members used during animation processing.

    get_interpolation_ends()
        Returns starting_mobject and ending_mobject as the interpolation
        endpoints, rather than using Transform's usual target-copy endpoint.

    clean_up_from_scene(scene)
        Runs the base Animation cleanup, removes the temporary grouped Mobject
        from the scene, restores the original source Mobject's saved state, and
        re-adds the original target Mobject if remover is False.

    Notes
    -----
    - The animated Mobject passed to Transform is Group(mobject,
      target_mobject.copy()). The original target object is not directly placed
      in this group.
    - The source Mobject's state is saved before the parent constructor runs.
    - At the beginning of the animation, the starting endpoint's target copy is
      made into a transparent ghost matching the source.
    - At the ending endpoint, the source copy is made into a transparent ghost
      matching the target.
    - ghost_to() aligns geometry using replace(), copies the target's uniforms,
      and sets the source opacity to zero.
    - prepare_interpolation() is called again after the endpoints are modified
      so interpolation uses their updated states.
    - During cleanup, the grouped animation object is removed and the original
      source Mobject is restored.
    - The target_mobject is added to the scene during cleanup only when
      self.remover is False, according to the supplied implementation.
    - The precise visual result depends on Transform and Mobject's interpolation,
      replacement, and uniform-handling behavior.

    Examples
    --------
    Example 1: Transform a circle into a square.

        >>> animation = FadeTransform(circle, square)

    The animation uses a group containing the circle and a copy of the square,
    then prepares transparent ghost objects to create the transition.

    Example 2: Allow the source geometry to stretch to match the target.

        >>> animation = FadeTransform(
        ...     circle,
        ...     square,
        ...     stretch=True,
        ... )

    Example 3: Keep the target in the scene after cleanup.

        >>> animation = FadeTransform(
        ...     circle,
        ...     square,
        ...     remover=False,
        ... )

    When cleanup runs, the temporary group is removed, the original circle's
    saved state is restored, and the original square is added to the scene.

    Example 4: Set a custom runtime.

        >>> animation = FadeTransform(
        ...     circle,
        ...     square,
        ...     run_time=2,
        ... )

    These examples illustrate construction only; circle and square must be
    defined Mobjects in the surrounding scene.

    See Also
    --------
    Transform
    Fade
    FadeIn
    FadeOut
    Mobject
    Group
    """

    def __init__(
        self,
        mobject: Mobject,
        target_mobject: Mobject,
        stretch: bool = True,
        dim_to_match: int = 1,
        **kwargs
    ):
        self.to_add_on_completion = target_mobject
        self.stretch = stretch
        self.dim_to_match = dim_to_match

        mobject.save_state()
        super().__init__(Group(mobject, target_mobject.copy()), **kwargs)

    def begin(self) -> None:
        self.ending_mobject = self.mobject.copy()
        Animation.begin(self)
        # Both 'start' and 'end' consists of the source and target mobjects.
        # At the start, the traget should be faded replacing the source,
        # and at the end it should be the other way around.
        start, end = self.starting_mobject, self.ending_mobject
        for m0, m1 in ((start[1], start[0]), (end[0], end[1])):
            self.ghost_to(m0, m1)
        # The two ends only became what they are here, so what a blend between them comes to
        # has to be settled again, having been settled over what they held a moment ago
        self.prepare_interpolation()

    def ghost_to(self, source: Mobject, target: Mobject) -> None:
        source.replace(target, stretch=self.stretch, dim_to_match=self.dim_to_match)
        source.set_uniform(**target.get_uniforms())
        source.set_opacity(0)

    def get_all_mobjects(self) -> list[Mobject]:
        return [
            self.mobject,
            self.starting_mobject,
            self.ending_mobject,
        ]

    def get_all_families_zipped(self) -> zip[tuple[Mobject]]:
        return Animation.get_all_families_zipped(self)

    def get_interpolation_ends(self) -> tuple[Mobject, Mobject]:
        # Its own pair rather than Transform's, this one never having made a target_copy
        return self.starting_mobject, self.ending_mobject

    def clean_up_from_scene(self, scene: Scene) -> None:
        Animation.clean_up_from_scene(self, scene)
        scene.remove(self.mobject)
        self.mobject[0].restore()
        if not self.remover:
            scene.add(self.to_add_on_completion)


class FadeTransformPieces(FadeTransform):
    """
    Animate a transformation by fading individual pieces of the source and target
    mobjects into one another.

    FadeTransformPieces is a subclass of FadeTransform that performs the
    transformation at the level of individual mobjects within each object's
    family, rather than treating the source and target as single objects.

    Before the animation begins, the source mobject's family is aligned with
    the target mobject's family using ``align_family()``. During the setup of
    the fade transformation, corresponding members of the two families are
    processed individually by ``ghost_to()``.

    This is useful when transforming objects made up of multiple components,
    such as groups of letters, mathematical expressions, or collections of
    shapes, and you want their individual pieces to participate in the
    transformation.

    Parameters
    ----------
    mobject : Mobject
        The source mobject that will be transformed. Its family members are
        aligned with those of the target before the animation begins.

    target_mobject : Mobject
        The target mobject that the source transforms into. The individual
        members of its family are paired with the source family's members
        during the fade setup.

    stretch : bool, optional
        Whether replacement operations may stretch the source pieces to match
        the corresponding target pieces. Inherited from FadeTransform.
        Defaults to True.

    dim_to_match : int, optional
        The dimension used when matching source and target pieces during
        replacement. Inherited from FadeTransform. Defaults to 1.

    **kwargs
        Additional keyword arguments forwarded through FadeTransform to
        Transform. Available options depend on the parent animation classes.

    Methods
    -------
    begin() -> None
        Align the families of the source and target mobjects, then initialize
        the FadeTransform animation.

    ghost_to(source: Mobject, target: Mobject) -> None
        Process corresponding family members individually. For each pair,
        delegate to FadeTransform.ghost_to(), which replaces the source
        member's geometry with the target member's geometry, copies the
        target's uniforms, and sets the source member's opacity to zero.

    Inherited Behavior
    ------------------
    FadeTransformPieces inherits the main animation setup and cleanup behavior
    from FadeTransform, including its handling of the source and target
    mobjects and the addition of the target to the scene when appropriate.

    Notes
    -----
    - ``align_family()`` is called before the parent ``begin()`` method.
      This prepares the two families for piece-by-piece processing.
    - ``ghost_to()`` uses ``zip(source.get_family(), target.get_family())``.
      Consequently, members are paired according to their order in the
      family lists. The method itself does not explicitly match pieces by
      semantic meaning, such as matching identical letters.
    - The number and ordering of family members can affect which pieces are
      paired. Family alignment is performed first to help make the structures
      compatible.
    - The exact visual result depends on the structure of the source and target
      mobjects, their family members, and the interpolation behavior inherited
      from the parent animation classes.
    - This class overrides ``begin()`` and ``ghost_to()``; the remaining
      animation lifecycle is inherited.

    Examples
    --------
    Example 1: Transform one group of shapes into another.

    >>> source = VGroup(
    ...     Square(),
    ...     Circle(),
    ... )
    >>> target = VGroup(
    ...     Circle(),
    ...     Square(),
    ... )
    >>> scene.add(source)
    >>> scene.play(FadeTransformPieces(source, target))

    The source and target families are aligned before the animation begins.
    Their family members are then processed individually during the fade
    transformation. The code does not guarantee that the pieces will be
    matched by shape or meaning; pairing follows their family order.

    Example 2: Transform groups containing multiple components.

    >>> source = VGroup(
    ...     Dot(LEFT),
    ...     Dot(ORIGIN),
    ...     Dot(RIGHT),
    ... )
    >>> target = VGroup(
    ...     Dot(UP),
    ...     Dot(ORIGIN),
    ...     Dot(DOWN),
    ... )
    >>> scene.add(source)
    >>> scene.play(FadeTransformPieces(source, target))

    Each corresponding family-member pair is processed through the parent's
    ``ghost_to()`` implementation. This example illustrates the setup for
    piece-by-piece transformation; the final visual behavior depends on the
    objects' family structures and the parent animation's interpolation.

    Example 3: Compare with FadeTransform.

    >>> scene.play(FadeTransform(source, target))
    >>> scene.play(FadeTransformPieces(source, target))

    FadeTransform performs its ghosting operation on the mobjects passed to
    its ``ghost_to()`` method. FadeTransformPieces overrides that operation
    to iterate through the members returned by ``get_family()``, applying the
    parent implementation to each pair individually.

    See Also
    --------
    FadeTransform
    Transform
    Animation
    Mobject.align_family
    Mobject.get_family
    """

    def begin(self) -> None:
        self.mobject[0].align_family(self.mobject[1])
        super().begin()

    def ghost_to(self, source: Mobject, target: Mobject) -> None:
        for sm0, sm1 in zip(source.get_family(), target.get_family()):
            super().ghost_to(sm0, sm1)


class VFadeIn(Animation):
    """
    Fade a VMobject into view by gradually increasing its stroke and fill opacity.

    VFadeIn is an Animation subclass that reveals a VMobject by interpolating
    its stroke opacity and fill opacity from zero to their original values.
    Unlike a general-purpose fade animation, it specifically modifies the
    visual opacity of vector-object strokes and fills.

    The animation processes the object's submobjects individually. For each
    submobject, it uses the corresponding starting object's stroke and fill
    opacity as the final values and interpolates from zero according to the
    current animation progress.

    Parameters
    ----------
    vmobject : VMobject
        The vector mobject to reveal. Its stroke and fill opacity are
        interpolated from zero to their starting values.

    suspend_mobject_updating : bool, optional
        Whether to suspend updating of the animated mobject while the
        animation runs. Defaults to False.

    **kwargs
        Additional keyword arguments forwarded to Animation, such as
        ``run_time`` and other supported animation configuration options.

    Methods
    -------
    interpolate_submobject(
        submob: VMobject,
        start: VMobject,
        alpha: float
    ) -> None
        Interpolate the stroke and fill opacity of a submobject.

        Parameters
        ----------
        submob : VMobject
            The submobject whose opacity is being updated.
        start : VMobject
            The corresponding starting submobject. Its original stroke and
            fill opacity values determine the final opacity.
        alpha : float
            Animation progress, typically ranging from 0 to 1. At 0, the
            stroke and fill opacity are zero; at 1, they reach their
            respective starting opacity values.

    Notes
    -----
    - VFadeIn is intended for VMobjects. It is not a general-purpose fade
      animation for every type of Mobject.
    - Stroke and fill opacity are interpolated independently. For example,
      a VMobject can have a visible stroke but a transparent fill.
    - The method uses ``start.get_stroke_opacity()`` and
      ``start.get_fill_opacity()`` as the respective final values.
    - The opacity of each submobject is updated using the interpolation
      function and the current animation progress.
    - This class changes stroke and fill opacity; it does not explicitly
      interpolate the object's position, scale, or color.
    - If a VMobject has no visible stroke or fill initially, the
      corresponding component will remain transparent throughout the
      animation.

    Examples
    --------
    Example 1: Fade in a circle.

    >>> circle = Circle()
    >>> scene.play(VFadeIn(circle))

    The circle's stroke and fill become visible gradually, reaching their
    original opacity values when the animation completes.

    Example 2: Control the animation duration.

    >>> square = Square()
    >>> scene.play(VFadeIn(square, run_time=2))

    The square takes two seconds to reveal, assuming the scene's animation
    timing is measured in seconds.

    Example 3: Fade in a group of vector objects.

    >>> shapes = VGroup(
    ...     Circle(),
    ...     Square().shift(RIGHT * 2),
    ... )
    >>> scene.play(VFadeIn(shapes))

    The animation processes the VMobject submobjects individually. Each
    submobject's stroke and fill opacity are interpolated toward the values
    stored in its corresponding starting state.

    Example 4: Inspect opacity interpolation.

    >>> shape = Circle()
    >>> animation = VFadeIn(shape)
    >>> animation.begin()
    >>> animation.interpolate(0)
    >>> animation.interpolate(1)

    At the beginning of the interpolation, stroke and fill opacity are set
    to zero. At the end, they are restored to the corresponding starting
    opacity values through the interpolation logic.

    See Also
    --------
    Animation
    VMobject
    VFadeOut
    FadeIn
    FadeOut
    """

    def __init__(self, vmobject: VMobject, suspend_mobject_updating: bool = False, **kwargs):
        super().__init__(
            vmobject,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )

    def interpolate_submobject(
        self,
        submob: VMobject,
        start: VMobject,
        alpha: float
    ) -> None:
        submob.set_stroke(
            opacity=interpolate(0, start.get_stroke_opacity(), alpha)
        )
        submob.set_fill(
            opacity=interpolate(0, start.get_fill_opacity(), alpha)
        )


class VFadeOut(VFadeIn):
    """
    Fade a VMobject out by gradually decreasing its stroke and fill opacity.

    VFadeOut is a subclass of VFadeIn that reverses the opacity interpolation
    used by its parent. Instead of revealing a vector object from transparent
    to its original opacity, it transitions the object's stroke and fill
    opacity from their starting values toward zero.

    The animation reuses VFadeIn's ``interpolate_submobject()`` method by
    passing ``1 - alpha`` as the interpolation parameter. As the animation
    progresses, this reversed parameter decreases from 1 to 0, causing the
    stroke and fill to fade out.

    Parameters
    ----------
    vmobject : VMobject
        The vector mobject to fade out. Its stroke and fill opacity are
        interpolated toward zero.

    remover : bool, optional
        Whether the animated mobject should be removed from the scene when
        the animation finishes. Defaults to True.

    final_alpha_value : float, optional
        The final alpha value used by the parent Animation configuration.
        Defaults to 0.0. Its precise effect depends on the implementation
        of the inherited animation lifecycle.

    **kwargs
        Additional keyword arguments forwarded through VFadeIn to Animation.

    Methods
    -------
    interpolate_submobject(
        submob: VMobject,
        start: VMobject,
        alpha: float
    ) -> None
        Fade out an individual VMobject submobject by delegating to
        VFadeIn.interpolate_submobject() with the reversed progress value
        ``1 - alpha``.

        Parameters
        ----------
        submob : VMobject
            The submobject whose stroke and fill opacity are being updated.
        start : VMobject
            The corresponding starting submobject, which supplies the
            original stroke and fill opacity values.
        alpha : float
            The animation progress. The method passes ``1 - alpha`` to
            the parent interpolation method.

    Notes
    -----
    - VFadeOut is designed for VMobjects, not arbitrary Mobject instances.
    - At alpha = 0, the parent receives 1, so the stroke and fill opacity
      reach their original starting values.
    - At alpha = 1, the parent receives 0, so the stroke and fill opacity
      become zero.
    - Intermediate alpha values reverse the opacity progression of VFadeIn.
    - Stroke and fill opacity are handled independently.
    - With the default ``remover=True``, the animation is configured to
      remove the animated mobject during cleanup. Set ``remover=False`` if
      the object should remain in the scene after the animation.
    - The constructor forwards ``remover`` and ``final_alpha_value`` to
      the parent class. Their behavior is determined by the inherited
      animation implementation.

    Examples
    --------
    Example 1: Fade out a circle.

    >>> circle = Circle()
    >>> scene.add(circle)
    >>> scene.play(VFadeOut(circle))

    The circle's stroke and fill gradually become transparent. With the
    default remover setting, the circle is removed from the scene when
    the animation finishes.

    Example 2: Keep the mobject in the scene.

    >>> square = Square()
    >>> scene.add(square)
    >>> scene.play(VFadeOut(square, remover=False))

    The square fades out, but the animation is configured not to remove
    it from the scene during cleanup. The square remains transparent
    unless another operation changes its appearance.

    Example 3: Control the duration.

    >>> triangle = Triangle()
    >>> scene.add(triangle)
    >>> scene.play(VFadeOut(triangle, run_time=2))

    The triangle fades out over two seconds, assuming the scene's animation
    timing is measured in seconds.

    Example 4: Understand the reversed alpha.

    >>> alpha = 0.25
    >>> reversed_alpha = 1 - alpha
    >>> print(reversed_alpha)
    0.75

    At 25% animation progress, VFadeOut passes 0.75 to the parent method.
    At 100% progress, it passes 0, producing zero stroke and fill opacity.

    See Also
    --------
    VFadeIn
    Animation
    VMobject
    FadeOut
    FadeIn
    """

    def __init__(
        self,
        vmobject: VMobject,
        remover: bool = True,
        final_alpha_value: float = 0.0,
        **kwargs
    ):
        super().__init__(
            vmobject,
            remover=remover,
            final_alpha_value=final_alpha_value,
            **kwargs
        )

    def interpolate_submobject(
        self,
        submob: VMobject,
        start: VMobject,
        alpha: float
    ) -> None:
        super().interpolate_submobject(submob, start, 1 - alpha)


class VFadeInThenOut(VFadeIn):
    """
    Fade a VMobject in and then fade it out within a single animation.

    VFadeInThenOut is a subclass of VFadeIn that uses a rate function to
    control the progression of the opacity animation. By default, it uses
    ``there_and_back``, which moves the animation's alpha value from 0 to 1
    and then back to 0.

    Because VFadeIn interpolates stroke and fill opacity from zero toward
    their original values, the default rate function makes the VMobject
    gradually appear and then disappear again.

    Parameters
    ----------
    vmobject : VMobject
        The vector mobject whose stroke and fill opacity will be animated.
        It fades in and then fades out according to the configured rate
        function.

    rate_func : Callable[[float], float], optional
        The rate function that maps the animation's normalized progress to
        an interpolation value. Defaults to ``there_and_back``, which
        typically rises from 0 to 1 and returns to 0.

    remover : bool, optional
        Whether the animated mobject should be removed from the scene during
        animation cleanup. Defaults to True.

    final_alpha_value : float, optional
        The final alpha value configured by the inherited Animation class.
        Defaults to 0.5. Its exact effect depends on the parent animation
        implementation.

    **kwargs
        Additional keyword arguments forwarded through VFadeIn to Animation.

    Inherited Behavior
    ------------------
    VFadeInThenOut does not override ``interpolate_submobject()``. It inherits
    VFadeIn's implementation, which interpolates each submobject's stroke and
    fill opacity from zero toward the opacity values stored in its starting
    state.

    The rate function supplied to the parent animation determines how that
    interpolation progresses over time.

    Notes
    -----
    - The default ``there_and_back`` rate function produces an appearance
      followed by a disappearance during one animation.
    - The actual opacity progression depends on the chosen ``rate_func``.
      A different rate function may produce a different visual result.
    - The animation modifies stroke and fill opacity. It does not explicitly
      animate position, scale, or color.
    - This class is intended for VMobjects.
    - With the default ``remover=True``, the object is configured to be
      removed from the scene during cleanup.
    - ``final_alpha_value`` is passed to the inherited animation setup; its
      specific behavior is determined by the parent implementation.

    Examples
    --------
    Example 1: Briefly reveal a circle.

    >>> circle = Circle()
    >>> scene.add(circle)
    >>> scene.play(VFadeInThenOut(circle))

    The circle gradually appears and then fades away using the default
    ``there_and_back`` rate function.

    Example 2: Control the duration.

    >>> square = Square()
    >>> scene.add(square)
    >>> scene.play(VFadeInThenOut(square, run_time=2))

    The square appears and disappears over a two-second animation.

    Example 3: Keep the object in the scene after the animation.

    >>> triangle = Triangle()
    >>> scene.add(triangle)
    >>> scene.play(VFadeInThenOut(triangle, remover=False))

    The triangle fades in and out, but the animation is configured not to
    remove it during cleanup. Its final visual state depends on the
    interpolation and cleanup behavior of the inherited animation classes.

    Example 4: Supply a custom rate function.

    >>> circle = Circle()
    >>> scene.add(circle)
    >>> scene.play(
    ...     VFadeInThenOut(
    ...         circle,
    ...         rate_func=there_and_back,
    ...         run_time=3,
    ...     )
    ... )

    The supplied rate function controls how the opacity interpolation
    progresses. Here, ``there_and_back`` is specified explicitly, and the
    animation lasts three seconds.

    See Also
    --------
    VFadeIn
    VFadeOut
    Animation
    there_and_back
    VMobject
    """

    def __init__(
        self,
        vmobject: VMobject,
        rate_func: Callable[[float], float] = there_and_back,
        remover: bool = True,
        final_alpha_value: float = 0.5,
        **kwargs
    ):
        super().__init__(
            vmobject,
            rate_func=rate_func,
            remover=remover,
            final_alpha_value=final_alpha_value,
            **kwargs
        )
