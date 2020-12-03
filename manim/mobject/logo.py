"""Utilities for Manim's logo and banner."""

__all__ = ["ManimBanner"]

import numpy as np

from ..constants import LEFT, UP, RIGHT, DOWN, ORIGIN, TAU
from ..animation.composition import AnimationGroup, Succession
from ..animation.fading import FadeIn
from ..animation.transform import ApplyMethod
from ..mobject.geometry import Circle, Square, Triangle
from ..mobject.value_tracker import ValueTracker
from ..mobject.svg.tex_mobject import Tex, MathTex
from ..mobject.types.vectorized_mobject import VGroup
from ..utils.space_ops import normalize
from ..utils.tex_templates import TexFontTemplates


class ManimBanner(VGroup):
    r"""Convenience class representing Manim's banner.

    Can be animated using custom methods.

    Parameters
    ----------
    dark_theme
        If ``True`` (the default), the dark theme version of the logo
        (with light text font) will be rendered. Otherwise, if ``False``,
        the light theme version (with dark text font) is used.

    Examples
    --------

    .. manim:: BannerDarkBackground

        class BannerDarkBackground(Scene):
            def construct(self):
                banner = ManimBanner().scale(0.5).to_corner(DR)
                self.play(FadeIn(banner))
                self.play(banner.expand())
                self.play(FadeOut(banner))

    .. manim:: BannerLightBackground

        class BannerLightBackground(Scene):
            def construct(self):
                self.camera.background_color = "#ece6e2"
                banner_large = ManimBanner(dark_theme=False).scale(0.7)
                banner_small = ManimBanner(dark_theme=False).scale(0.35)
                banner_small.next_to(banner_large, DOWN)
                self.play(banner_large.create(), banner_small.create())
                self.play(banner_large.expand(), banner_small.expand())
                self.play(FadeOut(banner_large), FadeOut(banner_small))

    """

    def __init__(self, dark_theme: bool = True):
        VGroup.__init__(self)

        logo_green = "#81b29a"
        logo_blue = "#454866"
        logo_red = "#e07a5f"
        m_height_over_anim_height = 0.75748

        self.font_color = "#ece6e2" if dark_theme else "#343434"
        self.scale_factor = 1

        self.M = MathTex(r"\mathbb{M}").scale(7).set_color(self.font_color)
        self.M.shift(2.25 * LEFT + 1.5 * UP)

        self.circle = Circle(color=logo_green, fill_opacity=1).shift(LEFT)
        self.square = Square(color=logo_blue, fill_opacity=1).shift(UP)
        self.triangle = Triangle(color=logo_red, fill_opacity=1).shift(RIGHT)
        self.add(self.triangle, self.square, self.circle, self.M)
        self.move_to(ORIGIN)

        anim = VGroup()
        for i, ch in enumerate("anim"):
            tex = Tex(
                "\\textbf{" + ch + "}",
                tex_template=TexFontTemplates.gnu_freeserif_freesans,
            )
            if i != 0:
                tex.next_to(anim, buff=0.01)
            tex.align_to(self.M, DOWN)
            anim.add(tex)
        anim.set_color(self.font_color).set_height(
            m_height_over_anim_height * self.M.get_height()
        )

        # Note: "anim" is only shown in the expanded state
        # and thus not yet added to the submobjects of self.
        self.anim = anim
        self.anim.set_opacity(0)

    def scale(self, scale_factor: float, **kwargs) -> "ManimBanner":
        """Scale the banner by the specified scale factor.

        Parameters
        ----------
        scale_factor
            The factor used for scaling the banner.

        Returns
        -------
        :class:`~.ManimBanner`
            The scaled banner.
        """
        self.scale_factor *= scale_factor
        # Note: self.anim is only added to self after expand()
        if self.anim not in self.submobjects:
            self.anim.scale(scale_factor, **kwargs)
        return super().scale(scale_factor, **kwargs)

    def create(self):
        """The creation animation for Manim's logo.

        Returns
        -------
        :class:`~.AnimationGroup`
            An animation to be used in a :meth:`.Scene.play` call.
        """
        shape_center = VGroup(self.circle, self.square, self.triangle).get_center()

        spiral_run_time = 2.1
        expansion_factor = 8 * self.scale_factor

        tracker = ValueTracker(0)

        for mob in [self.circle, self.square, self.triangle]:
            mob.final_position = mob.get_center()
            mob.initial_position = (
                mob.final_position
                + (mob.final_position - shape_center) * expansion_factor
            )
            mob.initial_to_final_distance = np.linalg.norm(
                mob.final_position - mob.initial_position
            )
            mob.move_to(mob.initial_position)
            mob.current_time = 0
            mob.starting_mobject = mob.copy()

            def updater(mob, dt):
                mob.become(mob.starting_mobject)
                direction = shape_center - mob.get_center()
                mob.shift(
                    normalize(direction, fall_back=direction)
                    * mob.initial_to_final_distance
                    * tracker.get_value()
                )
                mob.rotate(TAU * tracker.get_value(), about_point=shape_center)
                mob.rotate(-TAU * tracker.get_value())

            mob.add_updater(updater)

        spin_animation = ApplyMethod(tracker.set_value, 1, run_time=spiral_run_time)

        return AnimationGroup(
            FadeIn(self, run_time=spiral_run_time / 2), spin_animation
        )

    def expand(self) -> Succession:
        """An animation that expands Manim's logo into its banner.

        The returned animation transforms the banner from its initial
        state (representing Manim's logo with just the icons) to its
        expanded state (showing the full name together with the icons).

        See the class documentation for how to use this.

        .. note::

            Before calling this method, the text "anim" is not a
            submobject of the banner object. After the expansion,
            it is added as a submobject so subsequent animations
            to the banner object apply to the text "anim" as well.

        Returns
        -------
        :class:`~.Succession`
            An animation to be used in a :meth:`.Scene.play` call.

        """
        m_shape_offset = 6.25 * self.scale_factor
        m_anim_buff = 0.06
        self.add(self.anim)
        self.anim.next_to(self.M, buff=m_anim_buff).shift(
            m_shape_offset * LEFT
        ).align_to(self.M, DOWN)
        move_left = AnimationGroup(
            ApplyMethod(self.triangle.shift, m_shape_offset * LEFT),
            ApplyMethod(self.square.shift, m_shape_offset * LEFT),
            ApplyMethod(self.circle.shift, m_shape_offset * LEFT),
            ApplyMethod(self.M.shift, m_shape_offset * LEFT),
        )
        move_right = AnimationGroup(
            ApplyMethod(self.triangle.shift, m_shape_offset * RIGHT),
            ApplyMethod(self.square.shift, m_shape_offset * RIGHT),
            ApplyMethod(self.circle.shift, m_shape_offset * RIGHT),
            ApplyMethod(self.M.shift, 0 * LEFT),
            AnimationGroup(
                *[ApplyMethod(obj.set_opacity, 1) for obj in self.anim], lag_ratio=0.15
            ),
            # It would be nice to have the last AnimationGroup replaced by
            # FadeIn(self.anim, lag_ratio=1)
            # Currently not working though.
        )
        return Succession(move_left, move_right)
