from __future__ import annotations

from manimlib.animation.animation import Animation
from manimlib.animation.animation import prepare_animation
from manimlib.mobject.mobject import _AnimationBuilder
from manimlib.mobject.mobject import Group
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING, Union, Iterable
AnimationType = Union[Animation, _AnimationBuilder]

if TYPE_CHECKING:
    from typing import Callable, Optional

    from manimlib.mobject.mobject import Mobject
    from manimlib.scene.scene import Scene


DEFAULT_LAGGED_START_LAG_RATIO = 0.05


class AnimationGroup(Animation):
    """
    Groups multiple animations into a single coordinated animation.

    `AnimationGroup` is a subclass of `Animation` that combines several animations
    and controls their relative start times and playback durations. Each child
    animation retains its own interpolation behavior, while the group determines
    when that animation begins and ends within the overall timeline.

    The group can automatically construct a suitable `Group` or `VGroup` from the
    animated mobjects, or use a caller-supplied group. It also coordinates the
    beginning, interpolation, finishing, reference updates, and scene cleanup of
    its child animations.

    Parameters
    ----------
    *args : AnimationType or Iterable[AnimationType]
        Animations to combine. If the first positional argument is an iterable,
        that iterable is used as the animation collection. Otherwise, all
        positional arguments are treated as individual animations.

        Each item is passed through `prepare_animation` before being stored.

    run_time : float or None, default=None
        Duration of the group in seconds. If None, the duration is set to the
        maximum end time calculated from the child animations and their lag.
        If `time_span` is provided, the duration is extended when necessary to
        reach the span's ending time.

    lag_ratio : float, default=0.0
        Controls the relative start times of consecutive child animations.

        - `0.0` starts every child animation at the same time.
        - `1.0` starts each animation when the preceding animation ends.
        - Values between 0 and 1 cause overlapping animations with staggered
          starting times.
        - Values greater than 1 introduce gaps between consecutive animations.

    group : Mobject or None, default=None
        An existing mobject to use as the group's main mobject. When supplied,
        this takes precedence over `group_type` and automatic group selection.

    group_type : type or None, default=None
        Mobject group class used to construct the group when `group` is None.
        It is instantiated with the distinct animated mobjects as positional
        arguments.

    time_span : tuple[float, float] or None, default=None
        Optional interval `(start, end)` over which the group's timeline is
        mapped. The group duration is extended as needed to reach the span's
        ending time.

    **kwargs
        Additional keyword arguments forwarded to the parent `Animation`
        constructor, including options such as `rate_func`, `name`, `remover`,
        `final_alpha_value`, and `suspend_mobject_updating`.

    Attributes
    ----------
    animations : list[AnimationType]
        Prepared child animations controlled by the group.

    anims_with_timings : list[tuple]
        Triplets of the form `(animation, start_time, end_time)` describing each
        child's position on the group's internal timeline.

    max_end_time : float
        Maximum ending time among the child animations after their staggered
        timings have been calculated. Defaults to 0 when there are no animations.

    run_time : float
        Duration used by the group. Initially determined from `max_end_time`
        unless an explicit duration is provided, then adjusted for `time_span`
        if necessary.

    lag_ratio : float
        Lag ratio used to calculate the relative start times of child animations.

    group : Mobject
        Main mobject representing the animation group. It is supplied explicitly,
        constructed using `group_type`, or automatically created as a `VGroup`
        or `Group`.

    Methods
    -------
    get_all_mobjects()
        Returns the group's main mobject. This overrides the base implementation
        of `Animation.get_all_mobjects`.

    begin()
        Marks the group as animating and calls `begin` on every child animation.
        Unlike the base implementation, this method does not create the usual
        group-level starting mobject or prepare interpolation through the parent
        implementation.

    finish()
        Clears the group's animating status and calls `finish` on every child
        animation, allowing each child to apply its own final interpolation state
        and cleanup of animation-specific state.

    clean_up_from_scene(scene)
        Calls `clean_up_from_scene` on every child animation, allowing each child
        to perform its own scene cleanup.

    update_reference_mobjects(dt, frame_rate=None)
        Updates reference mobjects for every child animation using the supplied
        time delta and optional frame rate.

    build_animations_with_timings(lag_ratio)
        Builds `anims_with_timings` by assigning each animation a start and end
        time. Each animation's duration comes from `get_run_time`. The next
        animation's start time is calculated by interpolating between the current
        animation's start and end times using `lag_ratio`.

    interpolate(alpha)
        Converts the group's normalized interpolation value into an internal
        time using `time_spanned_alpha(alpha) * max_end_time`. For each child
        animation, calculates local progress from its start and end times, clips
        that progress to the interval from 0 to 1, and passes it to the child's
        `interpolate` method. A child with zero duration receives alpha 0.

    Notes
    -----
    - `prepare_animation` is called for every item in the selected animation
      collection. This allows supported animation inputs to be converted into
      animation objects before scheduling.
    - The constructor uses the first argument as the animation collection when
      that argument is an `Iterable`. Otherwise, it uses all positional arguments.
      Consequently, an empty positional argument list is not handled by the
      current implementation because it accesses `args[0]`.
    - `max_end_time` is calculated from the scheduled end times, not necessarily
      from the sum of all child durations. With overlapping animations, the
      group's natural duration can be shorter than that sum.
    - For each animation, the next start time is calculated as
      `interpolate(start_time, end_time, lag_ratio)`. This means a lag ratio of
      0 starts every animation at time 0, while a ratio of 1 schedules each
      animation immediately after the preceding animation's end.
    - The constructor creates a list of distinct animated mobjects using
      `remove_list_redundancies`. Repeated references to the same mobject are
      therefore included only once in the automatically constructed group.
    - Group selection follows this precedence:
      1. Use `group` when explicitly supplied.
      2. Otherwise, construct `group_type(*mobs)` when `group_type` is supplied.
      3. Otherwise, use `VGroup(*mobs)` if all animated mobjects are `VMobject`
         instances.
      4. Otherwise, use `Group(*mobs)`.
    - The implementation checks `all(isinstance(anim.mobject, VMobject) for anim
      in animations)` when selecting the default group. This check uses the local
      variable `animations` from initialization rather than `self.animations`.
    - The group-level `begin` and `finish` methods explicitly delegate to the
      child animations. They do not call the corresponding parent methods.
    - `interpolate` uses the group's internal timeline based on `max_end_time`.
      If the group's `run_time` is overridden, this timeline may be rescaled
      relative to the duration used by the surrounding scene.
    - Child animations are interpolated independently using their scheduled
      intervals. A child's local alpha is clipped to 0 before its scheduled start
      and to 1 after its scheduled end.
    - The child animations' own `rate_func` settings are applied when each child
      handles its interpolation. The group's `interpolate` method itself does
      not apply the group's `rate_func` directly.
    - A zero-duration child receives `sub_alpha = 0` in `interpolate`, regardless
      of its scheduled position on the timeline.
    - `get_all_mobjects` is annotated as returning `Mobject`, and returns the
      group's main mobject directly rather than a tuple. This differs from the
      base `Animation.get_all_mobjects` return structure and should be considered
      when extending this class.

    Examples
    --------
    Play several animations simultaneously:

    >>> circle = Circle()
    >>> square = Square()
    >>> group = AnimationGroup(
    ...     Create(circle),
    ...     Create(square),
    ... )
    >>> self.play(group)

    Stagger child animations with a lag ratio:

    >>> group = AnimationGroup(
    ...     FadeIn(Circle()),
    ...     FadeIn(Square()),
    ...     FadeIn(Triangle()),
    ...     lag_ratio=0.5,
    ... )
    >>> self.play(group)

    Schedule animations sequentially:

    >>> group = AnimationGroup(
    ...     Create(Circle()),
    ...     Create(Square()),
    ...     Create(Triangle()),
    ...     lag_ratio=1.0,
    ... )
    >>> self.play(group)

    Specify the total playback duration:

    >>> group = AnimationGroup(
    ...     Create(Circle()),
    ...     Create(Square()),
    ...     run_time=3,
    ... )
    >>> self.play(group)

    Provide an explicit group mobject:

    >>> circle = Circle()
    >>> square = Square()
    >>> container = VGroup(circle, square)
    >>> group = AnimationGroup(
    ...     Create(circle),
    ...     Create(square),
    ...     group=container,
    ... )
    >>> self.play(group)

    Use a custom group type:

    >>> group = AnimationGroup(
    ...     Create(Circle()),
    ...     Create(Square()),
    ...     group_type=VGroup,
    ... )
    >>> self.play(group)

    See Also
    --------
    Animation
    Succession
    LaggedStart
    Group
    VGroup
    prepare_animation
    """

    def __init__(
        self,
        *args: AnimationType | Iterable[AnimationType],
        run_time: Optional[float] = None,  # If None, default to sum of inputed animation runtimes
        lag_ratio: float = 0.0,
        group: Optional[Mobject] = None,
        group_type: Optional[type] = None,
        time_span: tuple[float, float] | None = None,
        **kwargs
    ):
        animations = args[0] if isinstance(args[0], Iterable) else args
        self.animations = [prepare_animation(anim) for anim in animations]
        self.build_animations_with_timings(lag_ratio)
        self.max_end_time = max((awt[2] for awt in self.anims_with_timings), default=0)
        self.run_time = self.max_end_time if run_time is None else run_time
        if time_span is not None:
            # The contents are laid out over their own natural stretch of time, and it is
            # time_spanned_alpha which fits that stretch into the span, see interpolate. So
            # the run_time here is what the scene plays for, which has to reach the span's end.
            self.run_time = max(self.run_time, time_span[1])
        self.lag_ratio = lag_ratio
        mobs = remove_list_redundancies([a.mobject for a in self.animations])
        if group is not None:
            self.group = group
        elif group_type is not None:
            self.group = group_type(*mobs)
        elif all(isinstance(anim.mobject, VMobject) for anim in animations):
            self.group = VGroup(*mobs)
        else:
            self.group = Group(*mobs)

        super().__init__(
            self.group,
            run_time=self.run_time,
            lag_ratio=lag_ratio,
            time_span=time_span,
            **kwargs
        )

    def get_all_mobjects(self) -> Mobject:
        return self.group

    def begin(self) -> None:
        self.group.set_animating_status(True)
        for anim in self.animations:
            anim.begin()
        # self.init_run_time()

    def finish(self) -> None:
        self.group.set_animating_status(False)
        for anim in self.animations:
            anim.finish()

    def clean_up_from_scene(self, scene: Scene) -> None:
        for anim in self.animations:
            anim.clean_up_from_scene(scene)

    def update_reference_mobjects(self, dt: float, frame_rate: float | None = None) -> None:
        for anim in self.animations:
            anim.update_reference_mobjects(dt, frame_rate)

    def build_animations_with_timings(self, lag_ratio: float) -> None:
        """
        Creates a list of triplets of the form
        (anim, start_time, end_time)
        """
        self.anims_with_timings = []
        curr_time = 0
        for anim in self.animations:
            start_time = curr_time
            end_time = start_time + anim.get_run_time()
            self.anims_with_timings.append(
                (anim, start_time, end_time)
            )
            # Start time of next animation is based on the lag_ratio
            curr_time = interpolate(
                start_time, end_time, lag_ratio
            )

    def interpolate(self, alpha: float) -> None:
        # Note, if the run_time of AnimationGroup has been
        # set to something other than its default, these
        # times might not correspond to actual times,
        # e.g. of the surrounding scene.  Instead they'd
        # be a rescaled version.  But that's okay!
        time = self.time_spanned_alpha(alpha) * self.max_end_time
        for anim, start_time, end_time in self.anims_with_timings:
            anim_time = end_time - start_time
            if anim_time == 0:
                sub_alpha = 0
            else:
                sub_alpha = clip((time - start_time) / anim_time, 0, 1)
            anim.interpolate(sub_alpha)


class Succession(AnimationGroup):
    """
    Plays a sequence of animations one after another.

    `Succession` is a subclass of `AnimationGroup` designed for sequential
    animation playback. Instead of progressing all child animations according
    to overlapping time intervals, it activates one animation at a time and
    advances to the next as the overall interpolation progresses.

    By default, `Succession` uses a `lag_ratio` of 1.0, which schedules each
    animation to begin when the previous animation ends. It overrides the
    animation lifecycle and interpolation methods to initialize, update, finish,
    and switch between the active child animation as needed.

    Parameters
    ----------
    *animations : Animation
        Animation objects to execute in sequence. These are passed to
        `AnimationGroup`, which prepares the animations and calculates their
        scheduled timing information.

    lag_ratio : float, default=1.0
        Timing ratio forwarded to `AnimationGroup`. A value of 1.0 schedules
        animations sequentially without overlap. Other values alter the scheduled
        start times calculated by the parent class, although `Succession` still
        activates only one child animation at a time.

    **kwargs
        Additional keyword arguments forwarded to `AnimationGroup`, such as
        `run_time`, `group`, `group_type`, `time_span`, and other animation
        configuration options.

    Attributes
    ----------
    animations : list[Animation]
        Prepared child animations inherited from `AnimationGroup`, in the order
        they will be considered during sequential playback.

    active_animation : Animation
        The child animation currently active. It is assigned in `begin` and
        updated whenever interpolation advances to a different child animation.

    Methods
    -------
    begin()
        Asserts that at least one child animation exists, selects the first
        animation as `active_animation`, and calls its `begin` method.

    finish()
        Calls `finish` on the currently active child animation.

    update_reference_mobjects(dt, frame_rate=None)
        Updates reference mobjects belonging to the active child animation only.
        Other animations are not updated because they have not necessarily begun
        and may not yet have initialized their starting or target mobjects.

    interpolate(alpha)
        Converts the group's normalized interpolation value to a time-spanned
        alpha, then uses `integer_interpolate` to determine the active animation
        index and its local interpolation value.

        If the selected animation differs from `active_animation`, the previous
        animation is finished, the newly selected animation is begun, and
        `active_animation` is updated. The selected animation is then interpolated
        using its local alpha.

    Notes
    -----
    - `Succession` inherits animation preparation, timing construction, group
      creation, and other configuration behavior from `AnimationGroup`.
    - Its default `lag_ratio=1.0` produces sequential timing in the parent
      class's timing schedule.
    - Only one child animation is treated as active at a time. When the selected
      animation changes, the previous active animation is finished before the
      next one begins.
    - Reference mobject updates are delegated only to the active animation.
      This avoids updating animations whose starting or target mobjects may not
      yet have been initialized.
    - `begin` uses an assertion to require at least one child animation. Creating
      an empty `Succession` may therefore succeed during construction but fail
      when `begin` is called.
    - `interpolate` relies on `integer_interpolate` to map the overall progress
      across the number of child animations. Exact boundary behavior depends on
      that helper's implementation.
    - Although `lag_ratio` is forwarded to `AnimationGroup`, the active animation
      is selected using an evenly divided index interval through
      `integer_interpolate`, rather than by directly consulting
      `anims_with_timings`.
    - `finish` finishes only the current active animation; it does not explicitly
      call `finish` on every child animation.
    - The parent `AnimationGroup` constructor determines the group's overall
      duration. An explicit `run_time` or `time_span` can therefore affect how
      the overall alpha maps onto the succession's child animations.

    Examples
    --------
    Play animations one after another:

    >>> succession = Succession(
    ...     Create(Circle()),
    ...     Create(Square()),
    ...     Create(Triangle()),
    ... )
    >>> self.play(succession)

    Specify the total duration:

    >>> succession = Succession(
    ...     FadeIn(Circle()),
    ...     FadeOut(Circle()),
    ...     run_time=4,
    ... )
    >>> self.play(succession)

    Pass a custom lag ratio:

    >>> succession = Succession(
    ...     Create(Circle()),
    ...     Create(Square()),
    ...     lag_ratio=1.0,
    ... )
    >>> self.play(succession)

    Use a succession inside a scene:

    >>> circle = Circle()
    >>> square = Square()
    >>> self.play(
    ...     Succession(
    ...         FadeIn(circle),
    ...         circle.animate.shift(RIGHT),
    ...         FadeOut(circle),
    ...         FadeIn(square),
    ...     )
    ... )

    See Also
    --------
    Animation
    AnimationGroup
    LaggedStart
    integer_interpolate
    """

    def __init__(
        self,
        *animations: Animation,
        lag_ratio: float = 1.0,
        **kwargs
    ):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)

    def begin(self) -> None:
        assert len(self.animations) > 0
        self.active_animation = self.animations[0]
        self.active_animation.begin()

    def finish(self) -> None:
        self.active_animation.finish()

    def update_reference_mobjects(self, dt: float, frame_rate: float | None = None) -> None:
        # Only the active animation, since the rest are yet to begin, and so
        # have no starting_mobject or target to speak of
        self.active_animation.update_reference_mobjects(dt, frame_rate)

    def interpolate(self, alpha: float) -> None:
        index, subalpha = integer_interpolate(
            0, len(self.animations), self.time_spanned_alpha(alpha)
        )
        animation = self.animations[index]
        if animation is not self.active_animation:
            self.active_animation.finish()
            animation.begin()
            self.active_animation = animation
        animation.interpolate(subalpha)


class LaggedStart(AnimationGroup):
    """
    An animation group that starts its child animations with a configurable delay
    between consecutive animations.

    LaggedStart extends AnimationGroup and forwards the supplied animations to
    the parent class with a default lag ratio of DEFAULT_LAGGED_START_LAG_RATIO.
    The lag ratio controls the relative timing offset between the starts of
    consecutive animations.

    Parameters
    ----------
    *animations
        Variable number of Animation instances to include in the group. Their
        start times are staggered according to the configured lag ratio.

    lag_ratio : float, optional
        Relative delay between the start times of consecutive animations.
        Defaults to DEFAULT_LAGGED_START_LAG_RATIO. A larger value generally
        produces more separation between animation start times, while a smaller
        value produces more overlap. The exact timing behavior is determined by
        AnimationGroup.

    **kwargs
        Additional keyword arguments forwarded to AnimationGroup.

    Notes
    -----
    - LaggedStart does not define its own animation lifecycle or interpolation
      methods. It relies on AnimationGroup for those behaviors.
    - The child animations are passed to AnimationGroup together with the
      selected lag_ratio.
    - The actual animation schedule depends on the timing logic implemented by
      AnimationGroup.
    - Unlike a succession-style sequence, a lagged start allows animations to
      overlap when their durations and start-time offsets permit it.

    Examples
    --------
    Create several animations that begin one after another with some overlap:

        >>> animations = [
        ...     FadeIn(circle),
        ...     FadeIn(square),
        ...     FadeIn(triangle),
        ... ]
        >>> lagged = LaggedStart(*animations, lag_ratio=0.2)

    The example illustrates construction only; the objects and animation classes
    must be defined in the surrounding scene.

    See Also
    --------
    AnimationGroup
    Succession
    Animation
    """

    def __init__(
        self,
        *animations,
        lag_ratio: float = DEFAULT_LAGGED_START_LAG_RATIO,
        **kwargs
    ):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)


class LaggedStartMap(LaggedStart):
    """
    Creates a lagged-start animation for each submobject in a group.

    LaggedStartMap extends LaggedStart and automatically constructs one animation
    for every submobject in the supplied Mobject. The provided anim_func is
    called once per submobject, and the resulting animations are passed to
    LaggedStart to create a staggered animation sequence.

    Parameters
    ----------
    anim_func : Callable[[Mobject], Animation]
        A callable that creates an Animation for a given submobject. Additional
        keyword arguments supplied to LaggedStartMap are forwarded to this
        callable when it is invoked for each submobject.

    group : Mobject
        The Mobject whose submobjects will each receive an animation. The group
        is also passed to the parent animation group through the group keyword
        argument.

    run_time : float, optional
        Total runtime requested for the resulting animation group. Defaults to
        2.0.

    lag_ratio : float, optional
        Relative delay between the start times of consecutive animations.
        Defaults to DEFAULT_LAGGED_START_LAG_RATIO. The timing behavior is
        inherited from LaggedStart.

    time_span : tuple[float, float] or None, optional
        Optional time span associated with the animation group. Defaults to None.
        This argument belongs to the group itself, so it is handled explicitly
        rather than being forwarded to each animation constructor.

    **kwargs
        Additional keyword arguments passed to anim_func for every submobject.
        The lag_ratio entry is removed from the copied keyword arguments before
        constructing the child animations, preventing it from being passed to
        anim_func.

    Notes
    -----
    - One animation is created for each submobject yielded by iterating over
      group.
    - Each child animation is constructed by calling anim_func(submob,
      **anim_kwargs).
    - The supplied group, run_time, lag_ratio, and time_span are passed to the
      LaggedStart constructor.
    - The original kwargs dictionary is not modified. A shallow copy is made
      before lag_ratio is removed from that copy.
    - The time_span parameter is reserved for the parent animation group rather
      than being forwarded to individual child animations.
    - The class does not implement its own interpolation logic; it inherits
      the staggered animation behavior from LaggedStart and AnimationGroup.

    Examples
    --------
    Apply FadeIn to each submobject with a staggered start:

        >>> animation = LaggedStartMap(
        ...     FadeIn,
        ...     group,
        ...     run_time=2.0,
        ...     lag_ratio=0.1,
        ... )

    Pass additional keyword arguments to every child animation:

        >>> animation = LaggedStartMap(
        ...     FadeIn,
        ...     group,
        ...     shift=UP,
        ...     lag_ratio=0.15,
        ... )

    These examples illustrate construction only; the group, animation
    constructors, and any required objects must be defined in the surrounding
    scene.

    See Also
    --------
    LaggedStart
    AnimationGroup
    Succession
    Animation
    """

    def __init__(
        self,
        anim_func: Callable[[Mobject], Animation],
        group: Mobject,
        run_time: float = 2.0,
        lag_ratio: float = DEFAULT_LAGGED_START_LAG_RATIO,
        time_span: tuple[float, float] | None = None,
        **kwargs
    ):
        # Named rather than left in kwargs, which are handed to each member rather than
        # to the group, and a span belongs to the group
        anim_kwargs = dict(kwargs)
        anim_kwargs.pop("lag_ratio", None)
        super().__init__(
            *(anim_func(submob, **anim_kwargs) for submob in group),
            run_time=run_time,
            lag_ratio=lag_ratio,
            group=group,
            time_span=time_span,
        )
