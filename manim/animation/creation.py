"""Animate the display or removal of a mobject from a scene."""


__all__ = [
    "ShowPartial",
    "ShowCreation",
    "Uncreate",
    "DrawBorderThenFill",
    "Write",
    "ShowIncreasingSubsets",
    "AddTextLetterByLetter",
    "ShowSubmobjectsOneByOne",
    "AddTextWordByWord",
]


from ..animation.animation import Animation
from ..animation.composition import Succession
from ..mobject.types.vectorized_mobject import VMobject
from ..mobject.mobject import Group
from ..utils.bezier import integer_interpolate
from ..utils.config_ops import digest_config
from ..utils.rate_functions import linear
from ..utils.rate_functions import double_smooth
from ..utils.rate_functions import smooth

import numpy as np
import itertools as it


class ShowPartial(Animation):
    """Abstract class for Animations that show the VMobject partially.

    Raises
    ------
    :class:`TypeError`
        If ``mobject`` is not an instance of :class:`~.VMobject`.

    See Also
    --------
    :class:`ShowCreation`, :class:`~.ShowPassingFlash`

    """

    def __init__(self, mobject, **kwargs):
        if not isinstance(mobject, VMobject):
            raise TypeError("This Animation only works on vectorized mobjects")
        super().__init__(mobject, **kwargs)

    def interpolate_submobject(self, submob, start_submob, alpha):
        submob.pointwise_become_partial(start_submob, *self.get_bounds(alpha))

    def get_bounds(self, alpha):
        raise NotImplementedError("Please use ShowCreation or ShowPassingFlash")


class ShowCreation(ShowPartial):
    """Incrementally shows the VMobject.

    Examples
    --------
    .. manim:: ShowCreationScene

        class ShowCreationScene(Scene):
            def construct(self):
                self.play(ShowCreation(Square()))


    See Also
    --------
    :class:`~.ShowPassingFlash`

    """

    CONFIG = {
        "lag_ratio": 1,
    }

    def get_bounds(self, alpha):
        return (0, alpha)


class Uncreate(ShowCreation):
    CONFIG = {"rate_func": lambda t: smooth(1 - t), "remover": True}


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
        self.check_validity_of_input(vmobject)
        super().__init__(vmobject, **kwargs)

    def check_validity_of_input(self, vmobject):
        if not isinstance(vmobject, VMobject):
            raise TypeError("DrawBorderThenFill only works for VMobjects")

    def begin(self):
        self.outline = self.get_outline()
        super().begin()

    def get_outline(self):
        outline = self.mobject.copy()
        outline.set_fill(opacity=0)
        for sm in outline.family_members_with_points():
            sm.set_stroke(color=self.get_stroke_color(sm), width=self.stroke_width)
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
        if index == 0:
            submob.pointwise_become_partial(outline, 0, subalpha)
            submob.match_style(outline)
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
        "int_func": np.floor,
    }

    def __init__(self, group, **kwargs):
        self.all_submobs = list(group.submobjects)
        super().__init__(group, **kwargs)

    def interpolate_mobject(self, alpha):
        n_submobs = len(self.all_submobs)
        index = int(self.int_func(alpha * n_submobs))
        self.update_submobject_list(index)

    def update_submobject_list(self, index):
        self.mobject.submobjects = self.all_submobs[:index]


class AddTextLetterByLetter(ShowIncreasingSubsets):
    """
    Add a Text Object letter by letter on the scene. Use time_per_char to change frequency of appearance of the letters.
    """

    CONFIG = {
        "suspend_mobject_updating": False,
        "int_func": np.ceil,
        "rate_func": linear,
        "time_per_char": 0.1,
    }

    def __init__(self, text, **kwargs):
        digest_config(self, kwargs)

        self.run_time = np.max((0.06, self.time_per_char)) * len(
            text
        )  # Time_per_char must be above 0.06. Otherwise the animation doesn't finish.
        super().__init__(text, **kwargs)


class ShowSubmobjectsOneByOne(ShowIncreasingSubsets):
    CONFIG = {
        "int_func": np.ceil,
    }

    def __init__(self, group, **kwargs):
        new_group = Group(*group)
        super().__init__(new_group, **kwargs)

    def update_submobject_list(self, index):
        # N = len(self.all_submobs)
        if index == 0:
            self.mobject.submobjects = []
        else:
            self.mobject.submobjects = self.all_submobs[index - 1]


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
        anims = it.chain(
            *[
                [
                    ShowIncreasingSubsets(word, run_time=tpc * len(word)),
                    Animation(word, run_time=0.005 * len(word) ** 1.5),
                ]
                for word in text_mobject
            ]
        )
        super().__init__(*anims, **kwargs)
