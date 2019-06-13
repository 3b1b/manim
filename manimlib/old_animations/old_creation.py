import numpy as np

from manimlib.animation.animation import OldAnimation
from manimlib.animation.transform import OldTransform
from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VectorizedPoint
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.paths import counterclockwise_path
from manimlib.utils.rate_functions import double_smooth
from manimlib.utils.rate_functions import smooth
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import there_and_back

# Drawing


class OldShowPartial(OldAnimation):
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.pointwise_become_partial(
            starting_submobject, *self.get_bounds(alpha)
        )

    def get_bounds(self, alpha):
        raise Exception("Not Implemented")


class OldShowCreation(OldShowPartial):
    CONFIG = {
        "submobject_mode": "one_at_a_time",
    }

    def get_bounds(self, alpha):
        return (0, alpha)


class OldUncreate(OldShowCreation):
    CONFIG = {
        "rate_func": lambda t: smooth(1 - t),
        "remover": True
    }



class OldShowIncreasingSubsets(OldAnimation):
    def __init__(self, group, **kwargs):
        self.all_submobs = group.submobjects
        Animation.__init__(self, group, **kwargs)

    def update_mobject(self, alpha):
        n_submobs = len(self.all_submobs)
        index = int(alpha * n_submobs)
        self.mobject.submobjects = self.all_submobs[:index]

# Fading


class OldFadeOut(OldTransform):
    CONFIG = {
        "remover": True,
    }

    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        target.fade(1)
        OldTransform.__init__(self, mobject, target, **kwargs)

    def clean_up(self, surrounding_scene=None):
        OldTransform.clean_up(self, surrounding_scene)
        self.update(0)


class OldFadeIn(OldTransform):
    def __init__(self, mobject, **kwargs):
        target = mobject.copy()
        OldTransform.__init__(self, mobject, target, **kwargs)
        self.starting_mobject.fade(1)
        if isinstance(self.starting_mobject, VMobject):
            self.starting_mobject.set_stroke(width=0)
            self.starting_mobject.set_fill(opacity=0)


class OldFadeInAndShiftFromDirection(OldTransform):
    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        digest_config(self, kwargs)
        target = mobject.copy()
        if direction is None:
            direction = self.direction
        mobject.shift(direction)
        mobject.fade(1)
        OldTransform.__init__(self, mobject, target, **kwargs)


class OldFadeInFrom(OldFadeInAndShiftFromDirection):
    """
    Alternate name for FadeInAndShiftFromDirection
    """


class OldFadeInFromDown(OldFadeInAndShiftFromDirection):
    """
    Essential a more convenient form of FadeInAndShiftFromDirection
    """
    CONFIG = {
        "direction": DOWN,
    }


class OldFadeOutAndShift(OldFadeOut):
    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        OldFadeOut.__init__(self, mobject, **kwargs)
        if direction is None:
            direction = self.direction
        self.target_mobject.shift(direction)


class OldFadeOutAndShiftDown(OldFadeOutAndShift):
    CONFIG = {
        "direction": DOWN,
    }


class OldFadeInFromLarge(OldTransform):
    def __init__(self, mobject, scale_factor=2, **kwargs):
        target = mobject.copy()
        mobject.scale(scale_factor)
        mobject.fade(1)
        OldTransform.__init__(self, mobject, target, **kwargs)


class OldVFadeIn(OldAnimation):
    """
    VFadeIn and VFadeOut only work for VMobjects, but they can be applied
    to mobjects while they are being animated in some other way (e.g. shifting
    then) in a way that does not work with FadeIn and FadeOut
    """

    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.set_stroke(
            opacity=interpolate(0, starting_submobject.get_stroke_opacity(), alpha)
        )
        submobject.set_fill(
            opacity=interpolate(0, starting_submobject.get_fill_opacity(), alpha)
        )


class OldVFadeOut(OldVFadeIn):
    CONFIG = {
        "remover": True
    }

    def update_submobject(self, submobject, starting_submobject, alpha):
        OldVFadeIn.update_submobject(
            self, submobject, starting_submobject, 1 - alpha
        )


# Growing


class OldGrowFromPoint(OldTransform):
    CONFIG = {
        "point_color": None,
    }

    def __init__(self, mobject, point, **kwargs):
        digest_config(self, kwargs)
        target = mobject.copy()
        point_mob = VectorizedPoint(point)
        if self.point_color:
            point_mob.set_color(self.point_color)
        mobject.replace(point_mob)
        mobject.set_color(point_mob.get_color())
        OldTransform.__init__(self, mobject, target, **kwargs)


class OldGrowFromCenter(OldGrowFromPoint):
    def __init__(self, mobject, **kwargs):
        OldGrowFromPoint.__init__(self, mobject, mobject.get_center(), **kwargs)


class OldGrowFromEdge(OldGrowFromPoint):
    def __init__(self, mobject, edge, **kwargs):
        OldGrowFromPoint.__init__(
            self, mobject, mobject.get_critical_point(edge), **kwargs
        )


class OldGrowArrow(OldGrowFromPoint):
    def __init__(self, arrow, **kwargs):
        OldGrowFromPoint.__init__(self, arrow, arrow.get_start(), **kwargs)


class OldSpinInFromNothing(OldGrowFromCenter):
    CONFIG = {
        "path_func": counterclockwise_path()
    }


class OldShrinkToCenter(OldTransform):
    def __init__(self, mobject, **kwargs):
        OldTransform.__init__(
            self, mobject, mobject.get_point_mobject(), **kwargs
        )


class Escribe_y_desvanece(OldAnimation):
    CONFIG = {
        "run_time": 2,
        "stroke_width": 2,
        "stroke_color": None,
        "rate_func": there_and_back,
        "submobject_mode": "lagged_start",
        "color_orilla" : WHITE,
        "factor_desvanecimiento": 6
    }

    def __init__(self, vmobject, **kwargs):
        if not isinstance(vmobject, VMobject):
            raise Exception("DrawBorderThenFill only works for VMobjects")
        self.reached_halfway_point_before = False
        OldAnimation.__init__(self, vmobject, **kwargs)

    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.pointwise_become_partial(
            starting_submobject, 0, min(self.factor_desvanecimiento * alpha, 1)
        )
        if alpha < 0.5:
            if self.stroke_color:
                color = self.stroke_color
            elif starting_submobject.stroke_width > 0:
                color = starting_submobject.get_stroke_color()
            else:
                color = starting_submobject.get_color()
            submobject.set_stroke(self.color_orilla, width=self.stroke_width)
            submobject.set_fill(opacity=0)
        else:
            if not self.reached_halfway_point_before:
                self.reached_halfway_point_before = True
                submobject.points = np.array(starting_submobject.points)
            width, opacity = [
                interpolate(start, end, 2 * alpha - 1)
                for start, end in [
                    (self.stroke_width, starting_submobject.get_stroke_width()),
                    (0, 1)
                ]
            ]
            submobject.set_stroke(width=width)
            submobject.set_fill(opacity=opacity)
