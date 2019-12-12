#!/usr/bin/env python
# -*- coding: utf-8 -*-

from manimlib.imports import *
from old_projects.efvgt import get_confetti_animations


class Test(Scene):
    def construct(self):
        pass

class Announcements(PiCreatureScene):
    def construct(self):
        title = TextMobject("Announcements!")
        title.scale(1.5)
        title.to_edge(UP)
        title.shift(LEFT)
        underline = Line(LEFT, RIGHT)
        underline.set_width(1.2*title.get_width())
        underline.next_to(title, DOWN)

        announcements = VGroup(*[
            TextMobject("$\\cdot$ %s"%s)
            for s in [
                "Q\\&A Round 2",
                "The case against Net Neutrality?",
            ]
        ])
        announcements.arrange(
            DOWN, 
            buff = LARGE_BUFF,
            aligned_edge = LEFT,
        )
        announcements.next_to(underline, DOWN, LARGE_BUFF, aligned_edge = LEFT)
        announcements.set_color_by_gradient(GREEN, YELLOW)

        self.play(
            Write(title),
            LaggedStartMap(FadeIn, announcements),
            ShowCreation(underline),
            self.pi_creature.change, "hooray", underline,
        )
        self.play(self.pi_creature.change, "confused", announcements)
        self.wait(2)


class PowersOfTwo(Scene):
    def construct(self):
        powers_of_2 = VGroup(*[
            TexMobject("2^{%d}"%n, "=", "{:,}".format(2**n))
            for n in range(20)
        ])
        powers_of_2.to_edge(UP)
        max_height = 6
        center = MED_LARGE_BUFF*DOWN

        mob = Dot(color = BLUE)
        mob.move_to(center)
        vects = it.cycle(5*[UP] + 5*[RIGHT])
        curr_po2 = powers_of_2[0]

        for i, vect, po2 in zip(it.count(), vects, powers_of_2[1:]):
            if i == 10:
                rect = SurroundingRectangle(mob, color = GREEN)
                group = VGroup(mob, rect)
                two_to_ten = group.copy()
                group.generate_target()
                group.target.set_height(0.2)
                group.target[1].set_fill(BLUE, 1)

                self.play(ShowCreation(rect))
                self.play(MoveToTarget(group))
                self.remove(group)
                mob = rect
                self.add(mob)
            m1, m2 = mob.copy(), mob.copy()
            group = VGroup(m1, m2)
            group.arrange(
                vect, buff = SMALL_BUFF
            )
            if group.get_height() > max_height:
                group.set_height(max_height)
            group.move_to(center)
            pa = np.pi/3
            self.play(
                Transform(curr_po2, po2),
                ReplacementTransform(mob, m1, path_arc = pa),
                ReplacementTransform(mob.copy(), m2, path_arc = pa),
            )
            mob = VGroup(*it.chain(m1, m2))

        #Show two_to_ten for comparrison
        self.play(
            mob.space_out_submobjects, 1.1,
            mob.to_edge, RIGHT
        )
        two_to_ten.to_edge(LEFT)
        lines = VGroup(*[
            Line(
                two_to_ten.get_corner(vect+RIGHT),
                mob[0].get_corner(vect+LEFT),
            )
            for vect in (UP, DOWN)
        ])
        two_to_ten.save_state()
        two_to_ten.replace(mob[0])
        self.play(
            two_to_ten.restore,
            *list(map(ShowCreation, lines))
        )

        curr_po2_outline = curr_po2[-1].copy()
        curr_po2_outline.set_fill(opacity = 0)
        curr_po2_outline.set_stroke(width = 2)
        curr_po2_outline.set_color_by_gradient(
            YELLOW, RED, PINK, PURPLE, BLUE, GREEN
        )

        self.play(
            LaggedStartMap(
                FadeIn, curr_po2_outline,
                rate_func = lambda t : wiggle(t, 8),
                run_time = 2,
                lag_ratio = 0.75,
            ),
            *get_confetti_animations(50)
        )

class PiHoldingScreen(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        screen = ScreenRectangle()
        screen.set_height(5.5)
        screen.to_edge(UP, buff = LARGE_BUFF)
        screen.to_edge(LEFT)

        words = VGroup(
            TextMobject("Ben Eater"),
            TextMobject("The Case Against Net Neutrality?"),
        )
        words.next_to(screen, UP, SMALL_BUFF)

        self.play(
            ShowCreation(screen),
            morty.change, "raise_right_hand", screen
        )
        self.wait(10)
        self.play(
            morty.change, "hooray", words[0],
            Write(words[0])
        )
        self.wait(10)
        self.play(
            morty.change, "pondering", words[1],
            Transform(words[0], words[1])
        )
        self.wait(10)

class QuestionsLink(Scene):
    def construct(self):
        link = TextMobject("https://3b1b.co/questions")
        link.set_width(FRAME_WIDTH)
        link.to_edge(DOWN)
        self.play(Write(link))
        self.wait()

class Thumbnail(Scene):
    def construct(self):
        equation = TexMobject("2^{19} = " + "{:,}".format(2**19))
        equation.set_width(FRAME_X_RADIUS)
        equation.to_edge(DOWN, buff = LARGE_BUFF)

        q_and_a = TextMobject("Q\\&A \\\\ Round 2")
        q_and_a.set_color_by_gradient(BLUE, YELLOW)
        q_and_a.set_width(FRAME_X_RADIUS)
        q_and_a.to_edge(UP, buff = LARGE_BUFF)

        eater = ImageMobject("eater", height = 3)
        eater.to_corner(UP+RIGHT, buff = 0)

        confetti_anims = get_confetti_animations(100)
        for anim in confetti_anims:
            anim.update(0.5)
        confetti = VGroup(*[a.mobject for a in confetti_anims])

        self.add(equation, q_and_a, eater)
















