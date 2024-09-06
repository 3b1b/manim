from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.constants import WHITE
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
        submob: VMobject,
        start_submob: VMobject,
        alpha: float
    ) -> None:
        submob.pointwise_become_partial(
            start_submob, *self.get_bounds(alpha)
        )

    @abstractmethod
    def get_bounds(self, alpha: float) -> tuple[float, float]:
        raise Exception("Not Implemented")


class ShowCreation(ShowPartial):
    def __init__(self, mobject: Mobject, lag_ratio: float = 1.0, **kwargs):
        super().__init__(mobject, lag_ratio=lag_ratio, **kwargs)

    def get_bounds(self, alpha: float) -> tuple[float, float]:
        return (0, alpha)


class Uncreate(ShowCreation):
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

    def finish(self) -> None:
        super().finish()
        self.mobject.refresh_joint_angles()

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
