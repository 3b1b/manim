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
    def __init__(
        self,
        *animations,
        lag_ratio: float = DEFAULT_LAGGED_START_LAG_RATIO,
        **kwargs
    ):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)


class LaggedStartMap(LaggedStart):
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
