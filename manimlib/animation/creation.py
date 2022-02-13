from manimlib.animation.animation import Animation
from manimlib.animation.composition import Succession
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import double_smooth
from manimlib.utils.rate_functions import smooth

import numpy as np
import itertools as it


class ShowPartial(Animation):
    """
    Abstract class for ShowCreation and ShowPassingFlash
    """
    CONFIG = {
        "should_match_start": False,
    }

    def begin(self):
        super().begin()
        if not self.should_match_start:
            self.mobject.lock_matching_data(self.mobject, self.starting_mobject)

    def finish(self):
        super().finish()
        self.mobject.unlock_data()

    def interpolate_submobject(self, submob, start_submob, alpha):
        submob.pointwise_become_partial(
            start_submob, *self.get_bounds(alpha)
        )

    def get_bounds(self, alpha):
        raise Exception("Not Implemented")


class ShowCreation(ShowPartial):
    CONFIG = {
        "lag_ratio": 1,
    }

    def get_bounds(self, alpha):
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

    def __init__(self, vmobject, **kwargs):
        assert(isinstance(vmobject, VMobject))
        self.sm_to_index = dict([
            (hash(sm), 0)
            for sm in vmobject.get_family()
        ])
        super().__init__(vmobject, **kwargs)

    def begin(self):
        # Trigger triangulation calculation
        for submob in self.mobject.get_family():
            submob.get_triangulation()

        self.outline = self.get_outline()
        super().begin()
        self.mobject.match_style(self.outline)
        self.mobject.lock_matching_data(self.mobject, self.outline)

    def finish(self):
        super().finish()
        self.mobject.unlock_data()

    def get_outline(self):
        outline = self.mobject.copy()
        outline.set_fill(opacity=0)
        for sm in outline.get_family():
            sm.set_stroke(
                color=self.get_stroke_color(sm),
                width=float(self.stroke_width)
            )
        return outline

    def get_stroke_color(self, vmobject):
        if self.stroke_color:
            return self.stroke_color
        elif vmobject.get_stroke_width() > 0:
            return vmobject.get_stroke_color()
        return vmobject.get_color()

    def get_all_mobjects(self):
        return [*super().get_all_mobjects(), self.outline]

    def interpolate_submobject(self, submob, start, outline, alpha):
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

    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        self.set_default_config_from_length(mobject)
        super().__init__(mobject, **kwargs)

    def set_default_config_from_length(self, mobject):
        length = len(mobject.family_members_with_points())
        if self.run_time is None:
            if length < 15:
                self.run_time = 1
            else:
                self.run_time = 2
        if self.lag_ratio is None:
            self.lag_ratio = min(4.0 / length, 0.2)


class ShowIncreasingSubsets(Animation):
    CONFIG = {
        "suspend_mobject_updating": False,
        "int_func": np.round,
    }

    def __init__(self, group, **kwargs):
        self.all_submobs = list(group.submobjects)
        super().__init__(group, **kwargs)

    def interpolate_mobject(self, alpha):
        n_submobs = len(self.all_submobs)
        index = int(self.int_func(alpha * n_submobs))
        self.update_submobject_list(index)

    def update_submobject_list(self, index):
        self.mobject.set_submobjects(self.all_submobs[:index])


class ShowSubmobjectsOneByOne(ShowIncreasingSubsets):
    CONFIG = {
        "int_func": np.ceil,
    }

    def update_submobject_list(self, index):
        # N = len(self.all_submobs)
        if index == 0:
            self.mobject.set_submobjects([])
        else:
            self.mobject.set_submobjects([self.all_submobs[index - 1]])


# TODO, this is broken...
class AddTextWordByWord(Succession):
    CONFIG = {
        # If given a value for run_time, it will
        # override the time_per_char
        "run_time": None,
        "time_per_char": 0.06,
    }

    def __init__(self, text_mobject, **kwargs):
        digest_config(self, kwargs)
        tpc = self.time_per_char
        anims = it.chain(*[
            [
                ShowIncreasingSubsets(word, run_time=tpc * len(word)),
                Animation(word, run_time=0.005 * len(word)**1.5),
            ]
            for word in text_mobject
        ])
        super().__init__(*anims, **kwargs)
