from manimlib.imports import *
from old_projects.efvgt import get_confetti_animations


class CrossingOneMillion(TeacherStudentsScene):
    def construct(self):
        self.increment_count()
        self.comment_on_real_milestone()
        self.reflect()

    def increment_count(self):
        number = self.number = Integer(0)
        number.move_to(UP, LEFT)
        number.scale(3)
        self.look_at(number, run_time=0)

        confetti_spirils = self.confetti_spirils = list(map(
            turn_animation_into_updater,
            get_confetti_animations(50)
        ))
        self.add(*confetti_spirils)
        self.play(
            ChangeDecimalToValue(
                number, 10**6,
                position_update_func=lambda m: m.move_to(
                    UP, LEFT
                ),
                rate_func=bezier([0, 0, 0, 1, 1, 1]),
                run_time=5,
            ),
            LaggedStartMap(
                ApplyMethod, self.get_pi_creatures(),
                lambda m: (m.change, "hooray", number),
                rate_func=squish_rate_func(smooth, 0, 0.5),
                run_time=4,
            ),
        )
        self.wait()

    def comment_on_real_milestone(self):
        number = self.number
        remainder = Integer(2**20 - 10**6)
        words = TextMobject(
            "Just",
            "{:,}".format(remainder.number),
            "to go \\\\ before the real milestone",
        )
        self.student_says(
            words,
            added_anims=[
                ApplyMethod(self.teacher.change, "hesitant"),
                self.get_student_changes(
                    "sassy", "speaking", "happy"
                ),
                number.scale, 0.5,
                number.center,
                number.to_edge, UP,
            ]
        )
        self.wait()
        self.remove(*self.confetti_spirils)
        remainder.replace(words[1])
        words.submobjects[1] = remainder
        self.play(
            ChangeDecimalToValue(number, 2**20, run_time=3),
            ChangeDecimalToValue(remainder, 0.1, run_time=3),
            self.teacher.change, "pondering", number,
            self.get_student_changes(
                *["pondering"] * 3,
                look_at_arg=number
            ),
        )
        self.play(
            FadeOut(self.students[1].bubble),
            FadeOut(self.students[1].bubble.content),
        )
        self.wait(2)

    def reflect(self):
        bubble = ThoughtBubble(
            direction=RIGHT,
            height=4,
            width=7,
        )
        bubble.pin_to(self.teacher)
        q_marks = TexMobject("???")
        q_marks.scale(2)
        q_marks.set_color_by_gradient(BLUE_D, BLUE_B)
        q_marks.next_to(bubble[-1].get_top(), DOWN)
        arrow = Vector(0.5 * DOWN, color=WHITE)
        arrow.next_to(q_marks, DOWN)
        number = self.number
        number.generate_target()
        number.target.next_to(arrow, DOWN)

        self.play(
            ShowCreation(
                bubble,
                rate_func=squish_rate_func(smooth, 0, 0.3)
            ),
            Write(q_marks),
            GrowArrow(arrow),
            MoveToTarget(number),
            run_time=3
        )
        self.wait()


class ShareWithFriends(PiCreatureScene):
    def construct(self):
        randy, morty = self.pi_creatures

        self.pi_creature_says(
            randy,
            "Wanna see why \\\\" +
            "$1 - \\frac{1}{3} + \\frac{1}{5}" +
            "- \\frac{1}{7} + \\cdots = \\frac{\\pi}{4}$?",
            target_mode="tease",
            added_anims=[morty.look, UP]
        )
        self.play(morty.change, "maybe", UP)
        self.wait()

    def create_pi_creatures(self):
        randy = Randolph(color=GREEN)
        morty = Mortimer(color=RED_E)
        randy.to_edge(DOWN).shift(4 * LEFT)
        morty.to_edge(DOWN)
        return randy, morty


class AllFeaturedCreators(MortyPiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        title = Title("Featured creators")

        dots = VGroup(*[Dot(color=WHITE) for x in range(4)])
        dots.arrange(DOWN, buff=LARGE_BUFF)
        dots.to_edge(LEFT, buff=2)

        creators = VGroup(*list(map(TextMobject, [
            "Think Twice",
            "LeiosOS",
            "Welch Labs",
            "Infinity plus one",
        ])))

        for creator, dot in zip(creators, dots):
            creator.next_to(dot, RIGHT)
            dot.save_state()
            dot.scale(4)
            dot.set_fill(opacity=0)

        rects = VGroup(*list(map(SurroundingRectangle, creators)))
        rects.set_stroke(WHITE, 2)
        rects.set_fill(BLUE_E, 1)

        think_words = VGroup(*list(map(TextMobject, [
            "(thinks visually)",
            "(thinks in terms of communities)",
            "(thinks in terms of series)",
            "(thinks playfully)",
        ])))
        for word, creator in zip(think_words, creators):
            # word.move_to(creator, RIGHT)
            # word.align_to(RIGHT, LEFT)
            word.next_to(creator, RIGHT)
            word.set_color(YELLOW)

        self.play(
            morty.change, "raise_right_hand",
            Write(title)
        )
        self.wait()
        self.play(LaggedStartMap(
            ApplyMethod, dots,
            lambda m: (m.restore,)
        ))
        self.play(
            LaggedStartMap(FadeIn, rects, lag_ratio=0.7),
            morty.change, "happy"
        )
        self.add(creators, rects)
        self.wait()

        modes = ["hooray", "tease", "raise_right_hand", "hooray"]
        for rect, word, mode in zip(rects, think_words, modes):
            self.play(
                self.get_rect_removal(rect),
                morty.change, mode,
            )
            self.wait()
            self.play(Write(word))
            self.wait()

        self.add(think_words)

    def get_rect_removal(self, rect):
        rect.generate_target()
        rect.target.stretch(0, 0, about_edge=LEFT)
        rect.target.set_stroke(width=0)
        return MoveToTarget(rect)


class GeneralWrapper(Scene):
    CONFIG = {
        "title_text": ""
    }

    def construct(self):
        title = TextMobject(self.title_text)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6.5)
        rect.next_to(title, DOWN)
        self.play(Write(title), ShowCreation(rect))
        self.wait()


class ThinkTwiceWrapper(GeneralWrapper):
    CONFIG = {"title_text": "Think Twice"}


class LeiosOSWrapper(GeneralWrapper):
    CONFIG = {"title_text": "LeiosOS"}


class WelchLabsWrapper(GeneralWrapper):
    CONFIG = {"title_text": "Welch Labs"}


class InfinityPlusOneWrapper(GeneralWrapper):
    CONFIG = {"title_text": "Infinity Plus One"}


class EndScreen(PiCreatureScene):
    CONFIG = {
        "seconds_to_blink": 3,
    }

    def construct(self):
        words = TextMobject("Clicky stuffs")
        words.scale(1.5)
        words.next_to(self.pi_creature, UP)
        words.to_edge(UP)

        self.play(
            FadeIn(
                words,
                run_time=2,
                lag_ratio=0.5
            ),
            self.pi_creature.change_mode, "hooray"
        )
        self.wait()
        mode_point_pairs = [
            ("raise_left_hand", 5 * LEFT + 3 * UP),
            ("raise_right_hand", 5 * RIGHT + 3 * UP),
            ("thinking", 5 * LEFT + 2 * DOWN),
            ("thinking", 5 * RIGHT + 2 * DOWN),
            ("thinking", 5 * RIGHT + 2 * DOWN),
            ("happy", 5 * LEFT + 3 * UP),
            ("raise_right_hand", 5 * RIGHT + 3 * UP),
        ]
        for mode, point in mode_point_pairs:
            self.play(self.pi_creature.change, mode, point)
            self.wait()
        self.wait(3)

    def create_pi_creature(self):
        self.pi_creature = Randolph()
        self.pi_creature.shift(2 * DOWN + 1.5 * LEFT)
        return self.pi_creature
