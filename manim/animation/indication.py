"""Animations drawing attention to particular mobjects."""

__all__ = [
    "FocusOn",
    "Indicate",
    "Flash",
    "CircleIndicate",
    "ShowPassingFlash",
    "ShowCreationThenDestruction",
    "ShowCreationThenFadeOut",
    "AnimationOnSurroundingRectangle",
    "ShowPassingFlashAround",
    "ShowCreationThenDestructionAround",
    "ShowCreationThenFadeAround",
    "ApplyWave",
    "WiggleOutThenIn",
    "TurnInsideOut",
]


import numpy as np

from .. import config
from ..constants import *
from ..animation.animation import Animation
from ..animation.movement import Homotopy
from ..animation.composition import AnimationGroup
from ..animation.composition import Succession
from ..animation.creation import ShowCreation
from ..animation.creation import ShowPartial
from ..animation.fading import FadeOut
from ..animation.transform import Transform
from ..mobject.types.vectorized_mobject import VMobject
from ..mobject.geometry import Circle
from ..mobject.geometry import Dot
from ..mobject.shape_matchers import SurroundingRectangle
from ..mobject.types.vectorized_mobject import VGroup
from ..mobject.geometry import Line
from ..utils.bezier import interpolate
from ..utils.rate_functions import there_and_back
from ..utils.rate_functions import wiggle
from ..utils.color import GREY, YELLOW


class FocusOn(Transform):
    def __init__(
        self, focus_point, opacity=0.2, color=GREY, run_time=2, remover=True, **kwargs
    ):
        self.focus_point = focus_point
        self.color = color
        self.opacity = opacity
        # Initialize with blank mobject, while create_target
        # and create_starting_mobject handle the meat
        super().__init__(VMobject(), run_time=run_time, remover=remover, **kwargs)

    def create_target(self):
        little_dot = Dot(radius=0)
        little_dot.set_fill(self.color, opacity=self.opacity)
        little_dot.add_updater(lambda d: d.move_to(self.focus_point))
        return little_dot

    def create_starting_mobject(self):
        return Dot(
            radius=config["frame_x_radius"] + config["frame_y_radius"],
            stroke_width=0,
            fill_color=self.color,
            fill_opacity=0,
        )


class Indicate(Transform):
    def __init__(
        self,
        mobject,
        scale_factor=1.2,
        color=YELLOW,
        rate_func=there_and_back,
        **kwargs
    ):
        self.color = color
        self.scale_factor = scale_factor
        super().__init__(mobject, rate_func=rate_func, **kwargs)

    def create_target(self):
        target = self.mobject.copy()
        target.scale_in_place(self.scale_factor)
        target.set_color(self.color)
        return target


class Flash(AnimationGroup):
    def __init__(
        self,
        point,
        line_length=0.2,
        num_lines=12,
        flash_radius=0.3,
        line_stroke_width=3,
        color=YELLOW,
        run_time=1,
        **kwargs
    ):
        self.point = point
        self.color = color
        self.line_length = line_length
        self.num_lines = num_lines
        self.flash_radius = flash_radius
        self.line_stroke_width = line_stroke_width

        self.lines = self.create_lines()
        animations = self.create_line_anims()
        super().__init__(
            *animations,
            group=self.lines,
            run_time=run_time,
            **kwargs,
        )

    def create_lines(self):
        lines = VGroup()
        for angle in np.arange(0, TAU, TAU / self.num_lines):
            line = Line(ORIGIN, self.line_length * RIGHT)
            line.shift((self.flash_radius - self.line_length) * RIGHT)
            line.rotate(angle, about_point=ORIGIN)
            lines.add(line)
        lines.set_color(self.color)
        lines.set_stroke(width=3)
        lines.add_updater(lambda l: l.move_to(self.point))
        return lines

    def create_line_anims(self):
        return [ShowCreationThenDestruction(line) for line in self.lines]


class CircleIndicate(Indicate):
    def __init__(
        self,
        mobject,
        circle_config={"color": YELLOW},
        rate_func=there_and_back,
        remover=True,
        **kwargs
    ):
        self.circle_config = circle_config
        circle = self.get_circle(mobject)
        super().__init__(circle, rate_func=rate_func, remover=remover, **kwargs)

    def get_circle(self, mobject):
        circle = Circle(**self.circle_config)
        circle.add_updater(lambda c: c.surround(mobject))
        return circle

    def interpolate_mobject(self, alpha):
        super().interpolate_mobject(alpha)
        self.mobject.set_stroke(opacity=alpha)


class ShowPassingFlash(ShowPartial):
    """Show only a sliver of the VMobject each frame.

    Examples
    --------
    .. manim:: ShowPassingFlashScene

        class ShowPassingFlashScene(Scene):
            def construct(self):
                self.play(ShowPassingFlash(Square()))


    See Also
    --------
    :class:`~.ShowCreation`

    """

    def __init__(self, mobject, time_width=0.1, remover=True, **kwargs):
        self.time_width = time_width
        super().__init__(mobject, remover=remover, **kwargs)

    def _get_bounds(self, alpha):
        tw = self.time_width
        upper = interpolate(0, 1 + tw, alpha)
        lower = upper - tw
        upper = min(upper, 1)
        lower = max(lower, 0)
        return (lower, upper)

    def finish(self):
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.pointwise_become_partial(start, 0, 1)


class ShowCreationThenDestruction(ShowPassingFlash):
    def __init__(self, mobject, time_width=2.0, run_time=1, **kwargs):
        super().__init__(mobject, time_width=time_width, run_time=run_time, **kwargs)


class ShowCreationThenFadeOut(Succession):
    def __init__(self, mobject, remover=True, **kwargs):
        super().__init__(
            ShowCreation(mobject), FadeOut(mobject), remover=remover, **kwargs
        )


class AnimationOnSurroundingRectangle(AnimationGroup):
    def __init__(
        self,
        mobject,
        rect_animation=Animation,
        surrounding_rectangle_config={},
        **kwargs
    ):
        # Callable which takes in a rectangle, and spits out some animation.  Could be
        # some animation class, could be something more
        self.rect_animation = rect_animation
        self.surrounding_rectangle_config = surrounding_rectangle_config
        self.mobject_to_surround = mobject

        rect = self.get_rect()
        rect.add_updater(lambda r: r.move_to(mobject))

        super().__init__(
            self.rect_animation(rect, **kwargs),
        )

    def get_rect(self):
        return SurroundingRectangle(
            self.mobject_to_surround, **self.surrounding_rectangle_config
        )


class ShowPassingFlashAround(AnimationOnSurroundingRectangle):
    def __init__(self, mobject, rect_animation=ShowPassingFlash, **kwargs):
        super().__init__(mobject, rect_animation=rect_animation, **kwargs)


class ShowCreationThenDestructionAround(AnimationOnSurroundingRectangle):
    def __init__(self, mobject, rect_animation=ShowCreationThenDestruction, **kwargs):
        super().__init__(mobject, rect_animation=rect_animation, **kwargs)


class ShowCreationThenFadeAround(AnimationOnSurroundingRectangle):
    def __init__(self, mobject, rect_animation=ShowCreationThenFadeOut, **kwargs):
        super().__init__(mobject, rect_animation=rect_animation, **kwargs)


class ApplyWave(Homotopy):
    def __init__(self, mobject, direction=UP, amplitude=0.2, run_time=1, **kwargs):
        self.direction = direction
        self.amplitude = amplitude
        left_x = mobject.get_left()[0]
        right_x = mobject.get_right()[0]
        vect = self.amplitude * self.direction

        def homotopy(x, y, z, t):
            alpha = (x - left_x) / (right_x - left_x)
            power = np.exp(2.0 * (alpha - 0.5))
            nudge = there_and_back(t ** power)
            return np.array([x, y, z]) + nudge * vect

        super().__init__(homotopy, mobject, run_time=run_time, **kwargs)


class WiggleOutThenIn(Animation):
    def __init__(
        self,
        mobject,
        scale_value=1.1,
        rotation_angle=0.01 * TAU,
        n_wiggles=6,
        scale_about_point=None,
        rotate_about_point=None,
        run_time=2,
        **kwargs
    ):
        self.scale_value = scale_value
        self.rotation_angle = rotation_angle
        self.n_wiggles = n_wiggles
        self.scale_about_point = scale_about_point
        self.rotate_about_point = rotate_about_point
        super().__init__(mobject, run_time=run_time, **kwargs)

    def get_scale_about_point(self):
        if self.scale_about_point is None:
            return self.mobject.get_center()

    def get_rotate_about_point(self):
        if self.rotate_about_point is None:
            return self.mobject.get_center()

    def interpolate_submobject(self, submobject, starting_sumobject, alpha):
        submobject.points[:, :] = starting_sumobject.points
        submobject.scale(
            interpolate(1, self.scale_value, there_and_back(alpha)),
            about_point=self.get_scale_about_point(),
        )
        submobject.rotate(
            wiggle(alpha, self.n_wiggles) * self.rotation_angle,
            about_point=self.get_rotate_about_point(),
        )


class TurnInsideOut(Transform):
    def __init__(self, mobject, path_arc=TAU / 4, **kwargs):
        super().__init__(mobject, path_arc=path_arc, **kwargs)

    def create_target(self):
        return self.mobject.copy().reverse_points()
