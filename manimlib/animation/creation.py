from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.mobject.svg.string_mobject import StringMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import double_smooth
from manimlib.utils.rate_functions import smooth
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.mobject.mobject import Mobject
    from manimlib.scene.scene import Scene
    from manimlib.typing import ManimColor


class ShowPartial(Animation, ABC):
    """
    Abstract class for ShowCreation and ShowPassingFlash
    """
    def __init__(self, mobject: Mobject, should_match_start: bool = False, **kwargs):
        self.should_match_start = should_match_start
        super().__init__(mobject, **kwargs)

    def interpolate_submobject(
        self,
        submob: Mobject,
        start_submob: Mobject,
        alpha: float
    ) -> None:
        submob.pointwise_become_partial(
            start_submob, *self.get_bounds(alpha)
        )

    @abstractmethod
    def get_bounds(self, alpha: float) -> tuple[float, float]:
        raise Exception("Not Implemented")


class ShowCreation(ShowPartial):
    """
    Animates the creation of a Mobject by progressively revealing it from its
    beginning to its end.

    ShowCreation extends ShowPartial and defines the visible portion of the
    Mobject at each animation progress value. At alpha = 0, the revealed interval
    has zero length. As alpha increases, the visible portion grows from the
    beginning of the Mobject. At alpha = 1, the entire Mobject is revealed.

    Parameters
    ----------
    mobject : Mobject
        The object whose creation is to be animated.

    lag_ratio : float, optional
        Relative timing parameter forwarded to ShowPartial. Defaults to 1.0.
        Its effect depends on the implementation of ShowPartial.

    **kwargs
        Additional keyword arguments forwarded to ShowPartial.

    Methods
    -------
    get_bounds(alpha)
        Returns the start and end bounds of the visible portion for the given
        animation progress. The start bound remains 0, while the end bound
        increases linearly with alpha.

    Notes
    -----
    - ShowCreation inherits its animation behavior from ShowPartial.
    - The get_bounds method returns (0, alpha), representing a growing interval
      from the beginning of the Mobject.
    - At alpha = 0, the bounds are (0, 0).
    - At alpha = 0.5, the bounds are (0, 0.5).
    - At alpha = 1, the bounds are (0, 1).
    - The method does not clamp alpha; any clamping or progress management is
      handled elsewhere in the animation system.
    - The precise visual result depends on how ShowPartial interprets these
      bounds for the supplied Mobject.

    Examples
    --------
    Reveal a curve progressively:

        >>> animation = ShowCreation(curve, run_time=2)

    The example illustrates construction only; curve must be a defined Mobject.

    See Also
    --------
    ShowPartial
    Animation
    Mobject
    """

    def __init__(self, mobject: Mobject, lag_ratio: float = 1.0, **kwargs):
        super().__init__(mobject, lag_ratio=lag_ratio, **kwargs)

    def get_bounds(self, alpha: float) -> tuple[float, float]:
        return (0, alpha)


class Uncreate(ShowCreation):
    """
    Animates the disappearance of a Mobject by progressively reversing its
    creation animation.

    Uncreate extends ShowCreation and forwards its configuration to the parent
    class. Its default rate function is smooth(1 - t), which reverses the input
    progress before applying the smooth rate function. This makes the object
    appear to be drawn backward, gradually disappearing from its end toward
    its beginning.

    Parameters
    ----------
    mobject : Mobject
        The object whose visible portion is to be progressively removed.

    rate_func : Callable[[float], float], optional
        Rate function controlling the animation's progress. Defaults to
        lambda t: smooth(1 - t), which reverses the input before applying
        smooth interpolation.

    remover : bool, optional
        Whether the animation should remove the Mobject from the scene when
        it finishes. Defaults to True. The behavior is inherited from the
        parent animation implementation.

    should_match_start : bool, optional
        Whether the animation should match the starting state according to the
        behavior implemented by the parent animation classes. Defaults to True.

    **kwargs
        Additional keyword arguments forwarded to ShowCreation.

    Notes
    -----
    - Uncreate inherits its partial-revelation behavior from ShowCreation and
      ShowPartial.
    - Unlike ShowCreation's default forward progression, Uncreate uses a
      reversed smooth rate function by default.
    - The rate function transforms the animation's input progress; the actual
      visible interval is determined by the inherited get_bounds method.
    - With the default remover=True, the animation is configured to remove the
      Mobject when the animation finishes.
    - Setting remover=False disables that removal behavior.
    - The class does not define its own begin, finish, or interpolate methods;
      these behaviors are inherited.

    Examples
    --------
    Animate a curve disappearing as though it were being drawn backward:

        >>> animation = Uncreate(curve, run_time=2)

    Keep the Mobject from being removed automatically after the animation:

        >>> animation = Uncreate(curve, remover=False)

    These examples illustrate construction only; curve must be a defined Mobject.

    See Also
    --------
    ShowCreation
    ShowPartial
    Animation
    Mobject
    """

    def __init__(
        self,
        mobject: Mobject,
        rate_func: Callable[[float], float] = lambda t: smooth(1 - t),
        remover: bool = True,
        should_match_start: bool = True,
        **kwargs,
    ):
        super().__init__(
            mobject,
            rate_func=rate_func,
            remover=remover,
            should_match_start=should_match_start,
            **kwargs,
        )


class DrawBorderThenFill(Animation):
    """
    Animates a VMobject by first tracing its outline and then transitioning it
    to its original style and appearance.

    DrawBorderThenFill extends Animation. During the first half of the animation,
    each submobject progressively traces the outline of a copied version of the
    original VMobject. During the second half, the traced outline transitions
    toward the original starting mobject, restoring its original style and fill.

    Parameters
    ----------
    vmobject : VMobject
        The vector object to animate. The constructor asserts that this argument
        is an instance of VMobject.

    run_time : float, optional
        Total duration of the animation in seconds. Defaults to 2.0.

    rate_func : Callable[[float], float], optional
        Function that transforms animation progress over time. Defaults to
        double_smooth.

    stroke_width : float, optional
        Stroke width used when constructing the outline. Defaults to 2.0.

    stroke_color : ManimColor or None, optional
        Color used for the outline stroke. If None, each family member's existing
        stroke color is used. Defaults to None.

    draw_border_animation_config : dict, optional
        Configuration dictionary stored on the animation for drawing the border.
        Defaults to an empty dictionary. This class does not directly read its
        contents in the supplied implementation.

    fill_animation_config : dict, optional
        Configuration dictionary stored on the animation for the fill phase.
        Defaults to an empty dictionary. This class does not directly read its
        contents in the supplied implementation.

    **kwargs
        Additional keyword arguments forwarded to Animation.

    Attributes
    ----------
    sm_to_index : dict
        Maps the hash of each submobject in the original object's family to an
        integer state. Each entry initially has the value 0 and is changed to 1
        when that submobject first crosses into the second interpolation phase.

    stroke_width : float
        Width assigned to the outline strokes.

    stroke_color : ManimColor or None
        Explicit outline color, or None to preserve each submobject's existing
        stroke color.

    draw_border_animation_config : dict
        Stored border-animation configuration.

    fill_animation_config : dict
        Stored fill-animation configuration.

    outline : VMobject
        Copy of the animated object with fill opacity set to zero and outline
        strokes configured. Created when begin() is called.

    Methods
    -------
    begin()
        Marks the Mobject as animating, creates the outline, initializes the
        parent animation, and matches the animated Mobject's style to the outline.

    get_outline()
        Creates and returns a copy of the Mobject with transparent fill and
        configured stroke styling for tracing its border.

    get_all_mobjects()
        Returns the Mobjects collected by the parent implementation, with the
        outline appended to the returned list.

    get_interpolation_ends()
        Returns the outline and starting Mobject as the endpoints used for the
        style-transition phase.

    interpolate_submobject(submob, start, outline, alpha)
        Divides normalized progress into two phases. The first phase progressively
        traces the outline using pointwise_become_partial(). The second phase
        interpolates from the outline toward the starting Mobject.

    Notes
    -----
    - The constructor requires a VMobject, not an arbitrary Mobject.
    - get_outline() copies the original object, sets its fill opacity to zero,
      and configures the stroke for each family member that has points.
    - The outline stroke uses stroke_color when provided; otherwise it uses
      each corresponding submobject's existing stroke color.
    - The outline stroke is placed according to the original Mobject's
      stroke_behind setting.
    - integer_interpolate(0, 2, alpha) selects the drawing phase or the
      transition phase and calculates the local progress within that phase.
    - During the first phase, pointwise_become_partial() progressively reveals
      the outline.
    - On the first frame of the second phase for each submobject, its data is
      initialized from the outline before interpolation proceeds.
    - The second phase interpolates from the outline toward the starting
      Mobject, restoring the original appearance.
    - get_interpolation_ends() returns (outline, starting_mobject), matching
      the endpoint order expected by interpolate_submobject().
    - The two configuration dictionaries are stored but are not used elsewhere
      in the supplied class implementation.
    - The default dictionary arguments are shared mutable objects in Python.
      Callers should avoid mutating them unless that shared behavior is intended.

    Examples
    --------
    Animate the outline tracing and fill transition of a vector object:

        >>> animation = DrawBorderThenFill(
        ...     square,
        ...     run_time=2.0,
        ...     stroke_width=3.0,
        ... )

    Specify a custom outline color:

        >>> animation = DrawBorderThenFill(
        ...     square,
        ...     stroke_color=RED,
        ...     stroke_width=2.5,
        ... )

    These examples illustrate construction only; square and any color constants
    must be defined in the surrounding scene.

    See Also
    --------
    Animation
    VMobject
    ShowCreation
    Uncreate
    """

    def __init__(
        self,
        vmobject: VMobject,
        run_time: float = 2.0,
        rate_func: Callable[[float], float] = double_smooth,
        stroke_width: float = 2.0,
        stroke_color: ManimColor = None,
        draw_border_animation_config: dict = {},
        fill_animation_config: dict = {},
        **kwargs
    ):
        assert isinstance(vmobject, VMobject)
        self.sm_to_index = {hash(sm): 0 for sm in vmobject.get_family()}
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self.draw_border_animation_config = draw_border_animation_config
        self.fill_animation_config = fill_animation_config
        super().__init__(
            vmobject,
            run_time=run_time,
            rate_func=rate_func,
            **kwargs
        )
        self.mobject = vmobject

    def begin(self) -> None:
        self.mobject.set_animating_status(True)
        self.outline = self.get_outline()
        super().begin()
        self.mobject.match_style(self.outline)

    def get_outline(self) -> VMobject:
        outline = self.mobject.copy()
        outline.set_fill(opacity=0)
        for sm in outline.family_members_with_points():
            sm.set_stroke(
                color=self.stroke_color or sm.get_stroke_color(),
                width=self.stroke_width,
                behind=self.mobject.stroke_behind,
            )
        return outline

    def get_all_mobjects(self) -> list[Mobject]:
        return [*super().get_all_mobjects(), self.outline]

    def get_interpolation_ends(self) -> tuple[VMobject, VMobject]:
        """
        The second half blends between these two, and the first half never blends at all: it
        traces the outline with pointwise_become_partial, which writes the points itself and
        refreshes the box from them, so what is settled here is read only where it holds.

        The outline being a copy of the mobject in another style, the two agree about every
        point and about the box, and only the style has anywhere to go.
        """
        return self.outline, self.starting_mobject

    def interpolate_submobject(
        self,
        submob: VMobject,
        start: VMobject,
        outline: VMobject,
        alpha: float
    ) -> None:
        index, subalpha = integer_interpolate(0, 2, alpha)

        if index == 1 and self.sm_to_index[hash(submob)] == 0:
            # First time crossing over
            submob.set_data(outline.data)
            self.sm_to_index[hash(submob)] = 1

        if index == 0:
            submob.pointwise_become_partial(outline, 0, subalpha)
        else:
            submob.interpolate(outline, start, subalpha)


class Write(DrawBorderThenFill):
    """
    Animates a VMobject as though it is being written or drawn, using a
    border-tracing effect followed by a transition to its original appearance.

    Write extends DrawBorderThenFill and automatically determines default values
    for the total runtime and the lag ratio based on the number of family members
    that contain points. It also defaults the outline stroke color to the
    Mobject's color when no stroke color is explicitly provided.

    Parameters
    ----------
    vmobject : VMobject
        The vector object to animate. Its family members with points determine
        the default runtime and lag ratio.

    run_time : float, optional
        Total duration of the animation in seconds. Defaults to -1, which signals
        that the runtime should be computed automatically. Negative values trigger
        automatic selection; non-negative values are used as provided.

    lag_ratio : float, optional
        Relative delay between the starts of consecutive submobject animations.
        Defaults to -1, which signals automatic calculation. Negative values
        trigger automatic selection; non-negative values are used as provided.

    rate_func : Callable[[float], float], optional
        Function that transforms animation progress over time. Defaults to linear.

    stroke_color : ManimColor or None, optional
        Color used to trace the object's outline. If None, the color returned by
        vmobject.get_color() is used. Defaults to None.

    **kwargs
        Additional keyword arguments forwarded to DrawBorderThenFill, including
        any supported animation configuration options.

    Methods
    -------
    compute_run_time(family_size, run_time)
        Returns the requested runtime when run_time is non-negative. Otherwise,
        returns 1 second if family_size is less than 15, or 2 seconds if it is
        15 or greater.

    compute_lag_ratio(family_size, lag_ratio)
        Returns the requested lag ratio when lag_ratio is non-negative.
        Otherwise, computes a default using the family size, capped at 0.2.

    Notes
    -----
    - family_size is calculated using len(vmobject.family_members_with_points()).
      It counts family members that contain points, not necessarily every
      object in the full family.
    - The default runtime is 1 second for fewer than 15 such members and
      2 seconds for 15 or more.
    - The default lag ratio is min(4.0 / (family_size + 1.0), 0.2).
    - For small family sizes, the computed lag ratio is capped at 0.2.
      As family_size increases, the computed ratio can become smaller.
    - The computed runtime and lag ratio are passed to DrawBorderThenFill.
    - Write does not implement a separate interpolation method; it inherits the
      border-tracing and style-transition behavior from DrawBorderThenFill.
    - The default rate function is linear, unlike the double_smooth default
      specified by DrawBorderThenFill.
    - The stroke color defaults to vmobject.get_color() only when stroke_color
      is None. An explicitly supplied color is passed through unchanged.

    Examples
    --------
    Write a vector object using automatically selected timing:

        >>> animation = Write(text_mobject)

    Specify a custom runtime and lag ratio:

        >>> animation = Write(
        ...     text_mobject,
        ...     run_time=3.0,
        ...     lag_ratio=0.1,
        ...     stroke_color=BLUE,
        ... )

    These examples illustrate construction only; text_mobject and any color
    constants must be defined in the surrounding scene.

    See Also
    --------
    DrawBorderThenFill
    ShowCreation
    Uncreate
    Animation
    VMobject
    """

    def __init__(
        self,
        vmobject: VMobject,
        run_time: float = -1,  # If negative, this will be reassigned
        lag_ratio: float = -1,  # If negative, this will be reassigned
        rate_func: Callable[[float], float] = linear,
        stroke_color: ManimColor = None,
        **kwargs
    ):
        if stroke_color is None:
            stroke_color = vmobject.get_color()
        family_size = len(vmobject.family_members_with_points())
        super().__init__(
            vmobject,
            run_time=self.compute_run_time(family_size, run_time),
            lag_ratio=self.compute_lag_ratio(family_size, lag_ratio),
            rate_func=rate_func,
            stroke_color=stroke_color,
            **kwargs
        )

    def compute_run_time(self, family_size: int, run_time: float):
        if run_time < 0:
            return 1 if family_size < 15 else 2
        return run_time

    def compute_lag_ratio(self, family_size: int, lag_ratio: float):
        if lag_ratio < 0:
            return min(4.0 / (family_size + 1.0), 0.2)
        return lag_ratio


class ShowIncreasingSubsets(Animation):
    """
    Reveals the submobjects of a group progressively by increasing the number
    of visible submobjects as the animation advances.

    ShowIncreasingSubsets extends Animation. It stores the group's original
    submobject list and, during interpolation, calculates how many submobjects
    should currently be visible. It then replaces the group's current submobject
    list with a prefix of the stored list.

    Parameters
    ----------
    group : Mobject
        The Mobject whose submobjects will be revealed progressively. The
        animation operates on its direct submobjects, rather than automatically
        flattening the entire family hierarchy.

    int_func : Callable[[float], float], optional
        Function used to convert the scaled animation progress into a submobject
        index. Defaults to np.round. The result is converted to int before being
        passed to update_submobject_list().

    suspend_mobject_updating : bool, optional
        Whether to suspend updating of the animated Mobject during the animation.
        Defaults to False. The setting is forwarded to Animation.

    **kwargs
        Additional keyword arguments forwarded to Animation.

    Attributes
    ----------
    all_submobs : list
        Snapshot of the group's direct submobjects captured when the animation
        is initialized. This stored list is used to determine which submobjects
        should be present at each animation progress.

    int_func : Callable[[float], float]
        Function used to calculate the current submobject index from normalized
        animation progress.

    Methods
    -------
    interpolate_mobject(alpha)
        Applies the animation's rate function to alpha, scales the result by the
        number of stored submobjects, converts it to an integer index using
        int_func, and updates the group's submobject list.

    update_submobject_list(index)
        Sets the animated Mobject's direct submobjects to the first index
        elements of all_submobs.

    Notes
    -----
    - The original direct submobject list is captured during initialization.
      Changes made to the group's submobject list afterward do not automatically
      update all_submobs.
    - The animation reveals submobjects by list membership, not by progressively
      changing each submobject's geometry or opacity.
    - The visible list is always assigned from the prefix all_submobs[:index].
    - With the default np.round function, the index is calculated by rounding
      alpha * n_submobs to the nearest integer before converting it to int.
    - The rate function is applied inside interpolate_mobject() before the
      index is calculated.
    - The computed index is not explicitly clamped in this class. Python slicing
      determines the result if the index is outside the usual range.
    - At alpha = 0, the default index is 0, so the group has no direct
      submobjects assigned by this method.
    - At alpha = 1, the default index is the rounded number of submobjects,
      so the full stored list is assigned.
    - Because set_submobjects() replaces the current direct submobject list,
      any submobjects added to the animated group after initialization but not
      present in all_submobs will not be retained by this update method.

    Examples
    --------
    Reveal a group of objects progressively:

        >>> animation = ShowIncreasingSubsets(group, run_time=2)

    Use floor-based indexing instead of rounding:

        >>> animation = ShowIncreasingSubsets(
        ...     group,
        ...     int_func=np.floor,
        ...     run_time=2,
        ... )

    These examples illustrate construction only; group and any referenced
    functions must be defined in the surrounding scene.

    See Also
    --------
    Animation
    ShowSubmobjectsOneByOne
    Mobject
    """

    def __init__(
        self,
        group: Mobject,
        int_func: Callable[[float], float] = np.round,
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        self.all_submobs = list(group.submobjects)
        self.int_func = int_func
        super().__init__(
            group,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        n_submobs = len(self.all_submobs)
        alpha = self.rate_func(alpha)
        index = int(self.int_func(alpha * n_submobs))
        self.update_submobject_list(index)

    def update_submobject_list(self, index: int) -> None:
        self.mobject.set_submobjects(self.all_submobs[:index])


class ShowSubmobjectsOneByOne(ShowIncreasingSubsets):
    """
    Displays the submobjects of a group one at a time as the animation progresses.

    ShowSubmobjectsOneByOne extends ShowIncreasingSubsets but overrides the
    submobject-list update behavior. Instead of progressively displaying an
    increasing prefix of the original submobject list, it displays only the
    single submobject corresponding to the current index.

    Parameters
    ----------
    group : Mobject
        The Mobject containing the submobjects to display sequentially.

    int_func : Callable[[float], float], optional
        Function used to convert scaled animation progress into a submobject
        index. Defaults to np.ceil. The function is forwarded to
        ShowIncreasingSubsets.

    **kwargs
        Additional keyword arguments forwarded to ShowIncreasingSubsets and
        subsequently to Animation.

    Attributes
    ----------
    all_submobs : list
        Inherited from ShowIncreasingSubsets. Stores the group's direct
        submobjects as they existed during initialization.

    int_func : Callable[[float], float]
        Inherited function used to calculate the current submobject index.

    Methods
    -------
    update_submobject_list(index)
        Clamps the supplied index between zero and len(all_submobs) - 1,
        converts it to an integer, and updates the animated Mobject's direct
        submobject list. An index of zero produces an empty list; otherwise,
        only the submobject at index - 1 is displayed.

    Notes
    -----
    - The animation inherits interpolate_mobject() from ShowIncreasingSubsets.
      It applies the rate function, calculates an index using int_func, and
      passes that index to update_submobject_list().
    - Unlike ShowIncreasingSubsets, this class displays at most one direct
      submobject at a time.
    - The index is clamped using clip(index, 0, len(all_submobs) - 1) before
      being converted to int.
    - When the clamped index is zero, the group is assigned an empty submobject
      list.
    - For a positive index, the displayed submobject is all_submobs[index - 1].
    - With the default np.ceil function, the index generally advances to the
      next integer as soon as scaled progress becomes positive enough to cross
      an integer boundary.
    - The class does not animate the geometry or opacity of individual
      submobjects; it changes which submobject is present in the group's
      direct submobject list.
    - For a group containing no submobjects, the upper clipping bound is -1.
      The resulting behavior depends on the implementation of clip and should
      not be assumed to match the non-empty case.

    Examples
    --------
    Display the objects in a group one by one:

        >>> animation = ShowSubmobjectsOneByOne(group, run_time=3)

    Use a custom index function:

        >>> animation = ShowSubmobjectsOneByOne(
        ...     group,
        ...     int_func=np.floor,
        ...     run_time=3,
        ... )

    These examples illustrate construction only; group and any referenced
    functions must be defined in the surrounding scene.

    See Also
    --------
    ShowIncreasingSubsets
    Animation
    Mobject
    """

    def __init__(
        self,
        group: Mobject,
        int_func: Callable[[float], float] = np.ceil,
        **kwargs
    ):
        super().__init__(group, int_func=int_func, **kwargs)

    def update_submobject_list(self, index: int) -> None:
        index = int(clip(index, 0, len(self.all_submobs) - 1))
        if index == 0:
            self.mobject.set_submobjects([])
        else:
            self.mobject.set_submobjects([self.all_submobs[index - 1]])


class AddTextWordByWord(ShowIncreasingSubsets):
    """
    Reveals a StringMobject progressively, adding its word groups one by one.

    AddTextWordByWord extends ShowIncreasingSubsets. It converts the supplied
    StringMobject into a grouped Mobject using build_groups(), then animates that
    group so its submobjects appear progressively. If no non-negative runtime is
    specified, the duration is calculated from the number of word groups and the
    requested time per word.

    Parameters
    ----------
    string_mobject : StringMobject
        The text object to reveal. The constructor asserts that the supplied
        object is an instance of StringMobject.

    time_per_word : float, optional
        Amount of animation time allocated per group when run_time is negative.
        Defaults to 0.2 seconds. The total runtime is calculated by multiplying
        this value by the number of groups returned by build_groups().

    run_time : float, optional
        Total duration of the animation in seconds. Defaults to -1.0, which
        indicates that the runtime should be calculated automatically. Any
        negative value triggers automatic calculation.

    rate_func : Callable[[float], float], optional
        Function controlling the animation's progress over time. Defaults to
        linear.

    **kwargs
        Additional keyword arguments forwarded to ShowIncreasingSubsets and
        subsequently to Animation.

    Attributes
    ----------
    string_mobject : StringMobject
        Reference to the original text object. It is retained separately from
        the grouped Mobject used for the animation.

    Methods
    -------
    clean_up_from_scene(scene)
        Removes the grouped animation Mobject from the scene. If the animation
        is not configured as a remover, it adds the original StringMobject back
        to the scene.

    Notes
    -----
    - The constructor uses string_mobject.build_groups() to obtain the Mobject
      that is animated.
    - The resulting grouped Mobject is passed to ShowIncreasingSubsets, so the
      inherited interpolation logic progressively reveals prefixes of its
      submobject list.
    - Automatic runtime is computed as time_per_word multiplied by the number
      of groups returned by build_groups().
    - The runtime is automatically recomputed only when run_time is negative.
    - The name suggests word-by-word animation, but the actual grouping behavior
      depends on how StringMobject.build_groups() divides the text.
    - The original StringMobject is stored in self.string_mobject, while the
      grouped Mobject is the inherited self.mobject.
    - During cleanup, the grouped Mobject is removed. The original text object
      is re-added only when is_remover() returns False.
    - The class does not define its own interpolation logic; it inherits that
      behavior from ShowIncreasingSubsets.

    Examples
    --------
    Reveal a text object progressively using the default timing:

        >>> animation = AddTextWordByWord(text)

    Set a custom time per group:

        >>> animation = AddTextWordByWord(
        ...     text,
        ...     time_per_word=0.3,
        ... )

    Specify the total runtime directly:

        >>> animation = AddTextWordByWord(
        ...     text,
        ...     run_time=4,
        ... )

    These examples illustrate construction only; text must be a defined
    StringMobject.

    See Also
    --------
    ShowIncreasingSubsets
    ShowSubmobjectsOneByOne
    StringMobject
    Animation
    """

    def __init__(
        self,
        string_mobject: StringMobject,
        time_per_word: float = 0.2,
        run_time: float = -1.0, # If negative, it will be recomputed with time_per_word
        rate_func: Callable[[float], float] = linear,
        **kwargs
    ):
        assert isinstance(string_mobject, StringMobject)
        grouped_mobject = string_mobject.build_groups()
        if run_time < 0:
            run_time = time_per_word * len(grouped_mobject)
        super().__init__(
            grouped_mobject,
            run_time=run_time,
            rate_func=rate_func,
            **kwargs
        )
        self.string_mobject = string_mobject

    def clean_up_from_scene(self, scene: Scene) -> None:
        scene.remove(self.mobject)
        if not self.is_remover():
            scene.add(self.string_mobject)
