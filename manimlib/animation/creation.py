from manimlib.animation.animation import Animation
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import double_smooth
from manimlib.utils.rate_functions import smooth

#Old packages
from manimlib.mobject.types.vectorized_mobject import VectorizedPoint
from manimlib.utils.bezier import interpolate
from manimlib.utils.paths import counterclockwise_path
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.utils.rate_functions import there_and_back

from manimlib.constants import *
from manimlib.animation.animation import OldAnimation

class ShowPartial(Animation):
    """
    Abstract class for ShowCreation and ShowPassingFlash
    """

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
        "remover": True
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
        self.check_validity_of_input(vmobject)
        super().__init__(vmobject, **kwargs)

    def check_validity_of_input(self, vmobject):
        if not isinstance(vmobject, VMobject):
            raise Exception(
                "DrawBorderThenFill only works for VMobjects"
            )

    def begin(self):
        self.outline = self.get_outline()
        super().begin()

    def get_outline(self):
        outline = self.mobject.copy()
        outline.set_fill(opacity=0)
        for sm in outline.family_members_with_points():
            sm.set_stroke(
                color=self.get_stroke_color(sm),
                width=self.stroke_width
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
        if index == 0:
            submob.pointwise_become_partial(
                outline, 0, subalpha
            )
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
    }

    def __init__(self, group, **kwargs):
        self.all_submobs = list(group.submobjects)
        super().__init__(group, **kwargs)

    def interpolate_mobject(self, alpha):
        n_submobs = len(self.all_submobs)
        index = int(alpha * n_submobs)
        self.mobject.submobjects = self.all_submobs[:index]


#Old classes

class OldDrawBorderThenFill(OldAnimation):
    CONFIG = {
        "run_time": 2,
        "stroke_width": 2,
        "stroke_color": None,
        "rate_func": double_smooth,
    }

    def __init__(self, vmobject, **kwargs):
        if not isinstance(vmobject, VMobject):
            raise Exception("DrawBorderThenFill only works for VMobjects")
        self.reached_halfway_point_before = False
        OldAnimation.__init__(self, vmobject, **kwargs)

    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.pointwise_become_partial(
            starting_submobject, 0, min(2 * alpha, 1)
        )
        if alpha < 0.5:
            if self.stroke_color:
                color = self.stroke_color
            elif starting_submobject.stroke_width > 0:
                color = starting_submobject.get_stroke_color()
            else:
                color = starting_submobject.get_color()
            submobject.set_stroke(color, width=self.stroke_width)
            submobject.set_fill(opacity=0)
        else:
            if not self.reached_halfway_point_before:
                self.reached_halfway_point_before = True
                submobject.points = np.array(starting_submobject.points)
            width, opacity = [
                interpolate(start, end, 2 * alpha - 1)
                for start, end in [
                    (self.stroke_width, starting_submobject.get_stroke_width()),
                    (0, starting_submobject.get_fill_opacity())
                ]
            ]
            submobject.set_stroke(width=width)
            submobject.set_fill(opacity=opacity)


class OldWrite(OldDrawBorderThenFill):
    CONFIG = {
        "rate_func": None,
        "submobject_mode": "lagged_start",
    }

    def __init__(self, mob_or_text, **kwargs):
        digest_config(self, kwargs)
        if isinstance(mob_or_text, str):
            mobject = TextMobject(mob_or_text)
        else:
            mobject = mob_or_text

        if "run_time" not in kwargs:
            self.establish_run_time(mobject)
        if "lag_factor" not in kwargs:
            if len(mobject.family_members_with_points()) < 4:
                min_lag_factor = 1
            else:
                min_lag_factor = 2
            self.lag_factor = max(self.run_time - 1, min_lag_factor)
        OldDrawBorderThenFill.__init__(self, mobject, **kwargs)

    def establish_run_time(self, mobject):
        num_subs = len(mobject.family_members_with_points())
        if num_subs < 15:
            self.run_time = 1
        else:
            self.run_time = 2


class Escribe(OldAnimation):
    CONFIG = {
        "run_time": 2,
        "stroke_width": 2,
        "stroke_color": None,
        "rate_func": linear,
        "submobject_mode": "lagged_start",
        "color_orilla" : WHITE,
        "usar_otra_orilla":False,
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
        if self.usar_otra_orilla==True:
            color_orilla=self.color_orilla
        else:
            color_orilla=submobject.get_color()
        if alpha < 0.5:
            if self.stroke_color:
                color = self.stroke_color
            elif starting_submobject.stroke_width > 0:
                color = starting_submobject.get_stroke_color()
            else:
                color = starting_submobject.get_color()
            submobject.set_stroke(color_orilla, width=self.stroke_width)
            submobject.set_fill(opacity=0)
        else:
            if not self.reached_halfway_point_before:
                self.reached_halfway_point_before = True
                submobject.points = np.array(starting_submobject.points)
            width, opacity = [
                interpolate(start, end, 2 * alpha - 1)
                for start, end in [
                    (self.stroke_width, starting_submobject.get_stroke_width()),
                    (0, starting_submobject.get_fill_opacity())
                ]
            ]
            submobject.set_stroke(width=width)
            submobject.set_fill(opacity=opacity)

