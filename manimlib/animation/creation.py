from __future__ import annotations

import itertools as it
from abc import abstractmethod

import numpy as np

from manimlib.animation.animation import Animation
from manimlib.mobject.svg.labelled_string import LabelledString
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import double_smooth
from manimlib.utils.rate_functions import smooth

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.mobject import Group


class ShowPartial(Animation):
    """
    Abstract class for ShowCreation and ShowPassingFlash
    """
    CONFIG = {
        "should_match_start": False,
    }

    def begin(self) -> None:
        super().begin()
        if not self.should_match_start:
            self.mobject.lock_matching_data(self.mobject, self.starting_mobject)

    def finish(self) -> None:
        super().finish()
        self.mobject.unlock_data()

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
    CONFIG = {
        "lag_ratio": 1,
    }

    def get_bounds(self, alpha: float) -> tuple[float, float]:
        return (0, alpha)


class Uncreate(ShowCreation):
    CONFIG = {
        "rate_func": lambda t: smooth(1 - t),
        "remover": True,
        "should_match_start": True,
    }


class DrawBorderThenFill(Animation):
    CONFIG = {
        "run_time": 2,
        "rate_func": double_smooth,
        "stroke_width": 2,
        "stroke_color": None,
        "draw_border_animation_config": {},
        "fill_animation_config": {},
    }

    def __init__(self, vmobject: VMobject, **kwargs):
        assert(isinstance(vmobject, VMobject))
        self.sm_to_index = dict([
            (hash(sm), 0)
            for sm in vmobject.get_family()
        ])
        super().__init__(vmobject, **kwargs)

    def begin(self) -> None:
        # Trigger triangulation calculation
        for submob in self.mobject.get_family():
            submob.get_triangulation()

        self.outline = self.get_outline()
        super().begin()
        self.mobject.match_style(self.outline)
        self.mobject.lock_matching_data(self.mobject, self.outline)

    def finish(self) -> None:
        super().finish()
        self.mobject.unlock_data()

    def get_outline(self) -> VMobject:
        outline = self.mobject.copy()
        outline.set_fill(opacity=0)
        for sm in outline.get_family():
            sm.set_stroke(
                color=self.get_stroke_color(sm),
                width=float(self.stroke_width)
            )
        return outline

    def get_stroke_color(self, vmobject: VMobject) -> str:
        if self.stroke_color:
            return self.stroke_color
        elif vmobject.get_stroke_width() > 0:
            return vmobject.get_stroke_color()
        return vmobject.get_color()

    def get_all_mobjects(self) -> list[VMobject]:
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
            submob.unlock_data()
            if not self.mobject.has_updaters:
                submob.lock_matching_data(submob, start)
            submob.needs_new_triangulation = False
            self.sm_to_index[hash(submob)] = 1

        if index == 0:
            submob.pointwise_become_partial(outline, 0, subalpha)
        else:
            submob.interpolate(outline, start, subalpha)


class Write(DrawBorderThenFill):
    CONFIG = {
        # To be figured out in
        # set_default_config_from_lengths
        "run_time": None,
        "lag_ratio": None,
        "rate_func": linear,
    }

    def __init__(self, vmobject: VMobject, **kwargs):
        digest_config(self, kwargs)
        self.set_default_config_from_length(vmobject)
        super().__init__(vmobject, **kwargs)

    def set_default_config_from_length(self, vmobject: VMobject) -> None:
        length = len(vmobject.family_members_with_points())
        if self.run_time is None:
            if length < 15:
                self.run_time = 1
            else:
                self.run_time = 2
        if self.lag_ratio is None:
            self.lag_ratio = min(4.0 / (length + 1.0), 0.2)


class ShowIncreasingSubsets(Animation):
    CONFIG = {
        "suspend_mobject_updating": False,
        "int_func": np.round,
    }

    def __init__(self, group: Group, **kwargs):
        self.all_submobs = list(group.submobjects)
        super().__init__(group, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        n_submobs = len(self.all_submobs)
        index = int(self.int_func(alpha * n_submobs))
        self.update_submobject_list(index)

    def update_submobject_list(self, index: int) -> None:
        self.mobject.set_submobjects(self.all_submobs[:index])


class ShowSubmobjectsOneByOne(ShowIncreasingSubsets):
    CONFIG = {
        "int_func": np.ceil,
    }

    def update_submobject_list(self, index: int) -> None:
        # N = len(self.all_submobs)
        if index == 0:
            self.mobject.set_submobjects([])
        else:
            self.mobject.set_submobjects([self.all_submobs[index - 1]])


class AddTextWordByWord(ShowIncreasingSubsets):
    CONFIG = {
        # If given a value for run_time, it will
        # override the time_per_word
        "run_time": None,
        "time_per_word": 0.2,
        "rate_func": linear,
    }

    def __init__(self, string_mobject, **kwargs):
        assert isinstance(string_mobject, LabelledString)
        grouped_mobject = string_mobject.get_submob_groups()
        digest_config(self, kwargs)
        if self.run_time is None:
            self.run_time = self.time_per_word * len(grouped_mobject)
        super().__init__(grouped_mobject, **kwargs)
