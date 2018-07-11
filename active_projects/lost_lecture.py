from __future__ import absolute_import
from big_ol_pile_of_manim_imports import *


class ShowEmergingEllipse(Scene):
    def construct(self):
        circle = Circle(num_anchors=50, radius=3, color=BLUE)
        e_point = 2 * RIGHT
        e_dot = Dot(e_point, color=YELLOW)
        lines = VGroup(*[
            Line(e_point, circle.point_from_proportion(a))
            for a in np.linspace(0, 1, 4 * 49)
        ])
        lines.set_stroke(width=1)
        for line in lines:
            line.generate_target()
            line.target.rotate(90 * DEGREES)

        fade_rect = FullScreenFadeRectangle()
        line = lines[20]
        line_dot = Dot(line.get_center(), color=YELLOW)

        words = TextMobject("Rotate $90^\\circ$ \\\\ about center")
        words.add_to_back(words.copy().set_stroke(BLACK, 2))
        words.next_to(line_dot, RIGHT)

        self.play(
            LaggedStart(ShowCreation, lines),
            Animation(VGroup(e_dot, circle))
        )
        self.add(lines.copy().set_stroke(LIGHT_GREY, 0.5))
        self.add(e_dot, circle)
        self.wait()
        self.play(FadeIn(fade_rect), Animation(line))
        self.play(
            GrowFromCenter(line_dot),
            FadeInFromDown(words)
        )
        self.add_foreground_mobjects(line.copy().set_stroke(LIGHT_GREY, 0.5))
        self.play(MoveToTarget(line, path_arc=90 * DEGREES))
        self.wait()
        self.play(
            FadeOut(fade_rect),
            FadeOut(line_dot),
            FadeOut(words),
            Animation(line)
        )
        self.play(
            LaggedStart(MoveToTarget, lines, run_time=4),
            Animation(VGroup(e_dot, circle))
        )
        self.wait()