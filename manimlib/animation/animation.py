from __future__ import annotations

from copy import deepcopy

from manimlib.mobject.mobject import _AnimationBuilder
from manimlib.mobject.mobject import Mobject
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.rate_functions import smooth
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from manimlib.scene.scene import Scene


DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0


class Animation(object):
    """
    Base class for animations that interpolate a Mobject over time.

    `Animation` defines the common lifecycle and interpolation interface used by
    ManimGL animations. It manages the animated mobject, animation duration,
    rate function, timing span, lag between submobjects, updater suspension,
    starting-state snapshots, and optional removal of the mobject after playback.

    This class provides the general animation framework rather than a specific
    visual effect. Subclasses typically implement `interpolate_submobject` to
    define how individual mobjects transition between states.

    Parameters
    ----------
    mobject : Mobject
        The mobject controlled by the animation. Must be an instance of `Mobject`
        or a subclass; otherwise, initialization raises `TypeError`.

    run_time : float, default=DEFAULT_ANIMATION_RUN_TIME
        Nominal duration of the animation in seconds. If `time_span` is supplied,
        the effective duration may be extended to accommodate its ending time.

    time_span : tuple[float, float] or None, default=None
        Optional pair `(start, end)` specifying the interval, in animation-time
        units, during which interpolation occurs. Outside this interval, the
        normalized interpolation value is clipped to the corresponding boundary.

    lag_ratio : float, default=DEFAULT_ANIMATION_LAG_RATIO
        Controls how interpolation is staggered across the animation's submobjects.
        A value of 0 applies the same normalized timing to all submobjects. A
        positive value introduces progressively delayed starts. A value of 1
        produces successive timing intervals for adjacent submobjects.

    rate_func : Callable[[float], float], default=smooth
        Function that transforms each submobject's normalized interpolation value.
        For example, `linear` produces a linear progression, while `smooth`
        produces eased progression. The result of this function determines the
        value passed to `interpolate_submobject`.

    name : str, default=""
        Optional name identifying the animation. If empty, a name is generated
        from the class name and string representation of the animated mobject.

    remover : bool, default=False
        Whether the animation should remove its animated mobject from the scene
        during `clean_up_from_scene`.

    final_alpha_value : float, default=1.0
        Interpolation value passed to `interpolate` when `finish` is called.
        Normally 1.0 represents the end of the animation, but subclasses may
        support other meaningful values.

    suspend_mobject_updating : bool, default=False
        Whether to suspend the animated mobject's updaters when the animation
        begins. If updating was active before suspension, it is resumed when the
        animation finishes. This option does not suspend the starting mobject
        or other reference mobjects.

    Attributes
    ----------
    mobject : Mobject
        The mobject being animated.

    run_time : float
        Configured animation duration. May be adjusted in `begin` when a time
        span is supplied.

    time_span : tuple[float, float] or None
        Optional interval restricting when interpolation progresses.

    rate_func : Callable[[float], float]
        Function applied to each submobject's normalized interpolation value.

    name : str
        Human-readable animation name.

    remover : bool
        Indicates whether the animated mobject should be removed during cleanup.

    final_alpha_value : float
        Interpolation value used when finishing the animation.

    lag_ratio : float
        Staggering factor used to calculate submobject timing.

    suspend_mobject_updating : bool
        Whether the animated mobject's updaters should be suspended during playback.

    starting_mobject : Mobject
        Copy of the animated mobject captured by `create_starting_mobject` when
        `begin` is called.

    families : list
        Cached zipped families of the mobjects returned by `get_all_mobjects`.
        These are used to interpolate corresponding submobjects.

    mobject_was_updating : bool
        Set during `begin` when updater suspension is enabled. Records whether
        the mobject was not already suspended, so `finish` can decide whether to
        resume updating.

    Methods
    -------
    _validate_input_type(mobject)
        Validates that the input is a `Mobject`, raising `TypeError` otherwise.

    __str__()
        Returns the animation's name.

    begin()
        Initializes the animation at playback start. Adjusts `run_time` when a
        time span is supplied, marks the mobject as animating, creates the
        starting-state copy, optionally suspends updating, caches the mobject
        families, prepares interpolation, and evaluates the animation at alpha 0.

    prepare_interpolation()
        Retrieves the interpolation endpoints and, if provided, prepares the
        animated mobject for interpolation between them. Subclasses can override
        `get_interpolation_ends` to specify these endpoints.

    get_interpolation_ends()
        Returns the pair of mobjects representing the interpolation endpoints,
        or None when the animation has no such pair to prepare. The base
        implementation returns None.

    finish()
        Applies `final_alpha_value`, turns off interpolation skipping, clears the
        mobject's animating status, and resumes its updaters if they were suspended
        by this animation and were active before suspension.

    clean_up_from_scene(scene)
        Removes the animated mobject from the supplied scene when `is_remover`
        returns True. Otherwise, it leaves the scene unchanged.

    create_starting_mobject()
        Creates and returns a copy of the animated mobject to preserve its initial
        state for interpolation.

    get_all_mobjects()
        Returns the tuple `(mobject, starting_mobject)`. Subclasses may override
        this to include additional mobjects needed for interpolation.

    get_all_families_zipped()
        Retrieves the family of each mobject returned by `get_all_mobjects` and
        zips the families together. Each resulting tuple contains corresponding
        family members at the same structural position.

    update_reference_mobjects(dt, frame_rate=None)
        Updates the reference mobjects returned by `get_reference_mobjects`,
        passing along the time delta and optional frame rate.

    get_reference_mobjects()
        Returns the mobjects tracked by the animation other than its primary
        animated mobject. The base implementation removes redundant references
        from the mobjects returned by `get_all_mobjects`.

    copy()
        Returns a deep copy of the animation.

    update_rate_info(run_time=None, rate_func=None, lag_ratio=None)
        Updates the animation's duration, rate function, and lag ratio when
        corresponding arguments are truthy, then returns the animation.
        Because the implementation uses `or`, values such as 0 do not replace
        existing settings.

    interpolate(alpha)
        Delegates to `interpolate_mobject(alpha)`. The input is generally a
        normalized animation value, commonly between 0 and 1.

    update(alpha)
        Compatibility method for older scenes. Delegates to `interpolate(alpha)`.

    time_spanned_alpha(alpha)
        Converts the global normalized animation value into a value restricted
        to `time_span` when one is supplied. Otherwise, returns `alpha` unchanged.

    interpolate_mobject(alpha)
        Iterates over cached family tuples, calculates a separate interpolation
        value for each tuple using `get_sub_alpha`, and delegates the actual
        interpolation to `interpolate_submobject`.

    interpolate_submobject(submobject, starting_submobject, alpha)
        Subclass extension point for interpolating an individual submobject from
        its starting state. The base implementation does nothing.

    get_sub_alpha(alpha, index, num_submobjects)
        Computes the normalized interpolation value for one submobject, taking
        the animation's lag ratio and rate function into account.

    set_run_time(run_time)
        Sets the animation duration and returns the animation.

    get_run_time()
        Returns the effective duration. When `time_span` is truthy, returns the
        larger of `run_time` and the span's ending time; otherwise, returns
        `run_time`.

    set_rate_func(rate_func)
        Sets the rate function and returns the animation.

    get_rate_func()
        Returns the current rate function.

    set_name(name)
        Sets the animation's name and returns the animation.

    is_remover()
        Returns the value of the `remover` attribute.

    Notes
    -----
    - The interpolation value, commonly called `alpha`, is generally normalized
      from 0 to 1. The animation lifecycle calls `interpolate(0)` during
      initialization and `interpolate(final_alpha_value)` during finishing.
    - `begin` creates the starting mobject before interpolation starts. Changes
      to the original mobject after this point may not be reflected in the saved
      starting state.
    - `time_span` changes how alpha is mapped to interpolation progress. In
      `begin`, `run_time` is adjusted using the span's ending value, while
      `get_run_time` also considers that ending value.
    - When a time span is used, `time_spanned_alpha` clips the elapsed animation
      time to the span's interval. The formula divides by `end - start`, so
      callers should provide a span with a nonzero duration.
    - Submobject staggering is calculated using
      `(num_submobjects - 1) * lag_ratio + 1`. The rate function is applied to
      each submobject's clipped local progress, not directly to the original
      global alpha.
    - `families` is computed during `begin`. If the relevant mobject hierarchy
      changes afterward, the cached family tuples may no longer represent the
      current structure.
    - `get_all_mobjects` and `get_interpolation_ends` serve different purposes.
      The former identifies mobjects whose families participate in animation
      interpolation; the latter identifies endpoint states for interpolation
      preparation.
    - If `suspend_mobject_updating` is True, `begin` records whether the mobject
      was previously updating. `finish` resumes it only if this animation
      suspended an updater state that was active beforehand.
    - `clean_up_from_scene` does not automatically add the animated mobject to
      the scene. Scene membership is managed by the surrounding playback logic.
    - The base `interpolate_submobject` method intentionally does nothing.
      A concrete animation subclass generally needs to override it to produce
      a visible change.
    - `update_rate_info` uses truth-value checks rather than explicit None checks.
      Consequently, values such as `run_time=0` or `lag_ratio=0` will not be
      applied through this method.
    - `get_all_families_zipped` assumes the returned mobjects have compatible
      family structures for the subclass's interpolation logic.

    Examples
    --------
    Create a concrete animation using a subclass:

    >>> circle = Circle()
    >>> animation = FadeIn(circle, run_time=2)
    >>> self.play(animation)

    Configure an animation's duration and rate function:

    >>> animation = FadeIn(Circle())
    >>> animation.set_run_time(3)
    >>> animation.set_rate_func(linear)

    Set a custom animation name:

    >>> animation = FadeIn(Circle()).set_name("Circle entrance")
    >>> print(str(animation))
    Circle entrance

    Configure timing and lag information:

    >>> animation = FadeIn(Circle())
    >>> animation.update_rate_info(
    ...     run_time=2,
    ...     rate_func=smooth,
    ...     lag_ratio=0.2,
    ... )

    Inspect the effective duration:

    >>> animation = FadeIn(Circle(), run_time=2)
    >>> print(animation.get_run_time())

    Implement a custom animation by overriding the interpolation hook:

    >>> class ShiftRight(Animation):
    ...     def interpolate_submobject(self, submobject, starting_submobject, alpha):
    ...         submobject.move_to(
    ...             starting_submobject.get_center() + alpha * RIGHT
    ...         )

    See Also
    --------
    Mobject
    Scene
    FadeIn
    Transform
    AnimationGroup
    """

    def __init__(
        self,
        mobject: Mobject,
        run_time: float = DEFAULT_ANIMATION_RUN_TIME,
        # Tuple of times, between which the animation will run
        time_span: tuple[float, float] | None = None,
        # If 0, the animation is applied to all submobjects at the same time
        # If 1, it is applied to each successively.
        # If 0 < lag_ratio < 1, its applied to each with lagged start times
        lag_ratio: float = DEFAULT_ANIMATION_LAG_RATIO,
        rate_func: Callable[[float], float] = smooth,
        name: str = "",
        # Does this animation add or remove a mobject from the screen
        remover: bool = False,
        # What to enter into the update function upon completion
        final_alpha_value: float = 1.0,
        # If set to True, the mobject itself will have its internal updaters called,
        # but the start or target mobjects would not be suspended. To completely suspend
        # updating, call mobject.suspend_updating() before the animation
        suspend_mobject_updating: bool = False,
    ):
        self._validate_input_type(mobject)
        self.mobject = mobject
        self.run_time = run_time
        self.time_span = time_span
        self.rate_func = rate_func
        self.name = name or self.__class__.__name__ + str(self.mobject)
        self.remover = remover
        self.final_alpha_value = final_alpha_value
        self.lag_ratio = lag_ratio
        self.suspend_mobject_updating = suspend_mobject_updating

    def _validate_input_type(self, mobject: Mobject) -> None:
        if not isinstance(mobject, Mobject):
            raise TypeError("Animation only works for Mobjects.")

    def __str__(self) -> str:
        return self.name

    def begin(self) -> None:
        # This is called right as an animation is being
        # played.  As much initialization as possible,
        # especially any mobject copying, should live in
        # this method
        if self.time_span is not None:
            start, end = self.time_span
            self.run_time = max(end, self.run_time)
        self.mobject.set_animating_status(True)
        self.starting_mobject = self.create_starting_mobject()
        if self.suspend_mobject_updating:
            self.mobject_was_updating = not self.mobject.updating_suspended
            self.mobject.suspend_updating()
        self.families = list(self.get_all_families_zipped())
        self.prepare_interpolation()
        self.interpolate(0)

    def prepare_interpolation(self) -> None:
        """
        Whatever holds of the two ends for the whole of the animation, settled here rather
        than found again in every blend, see Mobject.prepare_interpolation.

        One which changes its ends after they have been made says so by calling this again,
        see FadeTransform.
        """
        ends = self.get_interpolation_ends()
        if ends is not None:
            self.mobject.prepare_interpolation(*ends)

    def get_interpolation_ends(self) -> tuple[Mobject, Mobject] | None:
        """
        The two states every blend this animation makes runs between, in the order it blends
        them, or none where it makes no such blend and so has nothing to settle in advance.

        Saying so is the animation's to do rather than something read off the mobjects it
        gathers: those same three may be two ends with the mobject between them, or a mobject
        and two others put to some other use entirely.
        """
        return None

    def finish(self) -> None:
        self.interpolate(self.final_alpha_value)
        self.mobject.turn_off_interpolation_skip()
        self.mobject.set_animating_status(False)
        if self.suspend_mobject_updating and self.mobject_was_updating:
            self.mobject.resume_updating()

    def clean_up_from_scene(self, scene: Scene) -> None:
        if self.is_remover():
            scene.remove(self.mobject)

    def create_starting_mobject(self) -> Mobject:
        # Keep track of where the mobject starts
        return self.mobject.copy()

    def get_all_mobjects(self) -> tuple[Mobject, Mobject]:
        """
        Ordering must match the ording of arguments to interpolate_submobject
        """
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self) -> zip[tuple[Mobject]]:
        return zip(*[
            mob.get_family()
            for mob in self.get_all_mobjects()
        ])

    def update_reference_mobjects(self, dt: float, frame_rate: float | None = None) -> None:
        """
        Updates things like starting_mobject, and (for
        Transforms) target_mobject.
        """
        for mob in self.get_reference_mobjects():
            mob.update(dt, frame_rate=frame_rate)

    def get_reference_mobjects(self) -> list[Mobject]:
        """
        Returns mobjects the Animation tracks other than
        self.mobject, e.g. the start and end points of
        interpolation.
        """
        # Remove redundancies for cases like Transform where target and target_copy
        # are the same, which happens when the already align.
        return remove_list_redundancies([
            mob for mob in self.get_all_mobjects()
            if mob is not self.mobject
        ])

    def copy(self):
        return deepcopy(self)

    def update_rate_info(
        self,
        run_time: float | None = None,
        rate_func: Callable[[float], float] | None = None,
        lag_ratio: float | None = None,
    ):
        self.run_time = run_time or self.run_time
        self.rate_func = rate_func or self.rate_func
        self.lag_ratio = lag_ratio or self.lag_ratio
        return self

    # Methods for interpolation, the mean of an Animation
    def interpolate(self, alpha: float) -> None:
        self.interpolate_mobject(alpha)

    def update(self, alpha: float) -> None:
        """
        This method shouldn't exist, but it's here to
        keep many old scenes from breaking
        """
        self.interpolate(alpha)

    def time_spanned_alpha(self, alpha: float) -> float:
        if self.time_span is not None:
            start, end = self.time_span
            return clip(alpha * self.run_time - start, 0, end - start) / (end - start)
        return alpha

    def interpolate_mobject(self, alpha: float) -> None:
        for i, mobs in enumerate(self.families):
            sub_alpha = self.get_sub_alpha(self.time_spanned_alpha(alpha), i, len(self.families))
            self.interpolate_submobject(*mobs, sub_alpha)

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_submobject: Mobject,
        alpha: float
    ):
        # Typically ipmlemented by subclass
        pass

    def get_sub_alpha(
        self,
        alpha: float,
        index: int,
        num_submobjects: int
    ) -> float:
        # TODO, make this more understanable, and/or combine
        # its functionality with AnimationGroup's method
        # build_animations_with_timings
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        raw_sub_alpha = clip((value - lower), 0, 1)
        return self.rate_func(raw_sub_alpha)

    # Getters and setters
    def set_run_time(self, run_time: float):
        self.run_time = run_time
        return self

    def get_run_time(self) -> float:
        if self.time_span:
            return max(self.run_time, self.time_span[1])
        return self.run_time

    def set_rate_func(self, rate_func: Callable[[float], float]):
        self.rate_func = rate_func
        return self

    def get_rate_func(self) -> Callable[[float], float]:
        return self.rate_func

    def set_name(self, name: str):
        self.name = name
        return self

    def is_remover(self) -> bool:
        return self.remover


def prepare_animation(anim: Animation | _AnimationBuilder):
    if isinstance(anim, _AnimationBuilder):
        return anim.build()

    if isinstance(anim, Animation):
        return anim

    raise TypeError(f"Object {anim} cannot be converted to an animation")
