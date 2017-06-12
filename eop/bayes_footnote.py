from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.complex_numbers import *
from topics.common_scenes import *
from topics.probability import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eop.bayes import IntroducePokerHand

SICKLY_GREEN = "#9BBD37"

class Introduction(TeacherStudentsScene):
    def construct(self):
        self.hold_up_example()
        self.write_counter_intuitive()
        self.put_it_first()
        self.swap_example_order()
        self.other_culprit()

    def hold_up_example(self):
        everyone = self.get_pi_creatures()
        self.teacher.change_mode("raise_right_hand")
        rect = ScreenRectangle()
        rect.set_stroke(YELLOW, 2)
        rect.to_edge(UP)
        randy = Randolph()
        randy.scale(0.7)
        name = TextMobject(r"""
            Bayes' theorem \\
            disease example
        """)
        name.next_to(rect.get_top(), DOWN, SMALL_BUFF)
        randy.next_to(name, DOWN)
        example = VGroup(rect, name, randy)

        self.remove(everyone)
        self.add(name, randy)
        self.play(
            randy.change_mode, "sick",
            randy.highlight, SICKLY_GREEN
        )
        self.play(ShowCreation(rect))
        self.play(
            FadeIn(everyone),
            example.scale, 0.5,
            example.next_to, self.teacher.get_corner(UP+LEFT), UP,
        )
        self.dither(2)

        self.example = example

    def write_counter_intuitive(self):
        bayes = TextMobject("Bayes")
        arrow = TexMobject("\\leftrightarrow")
        intuition = TextMobject("Intuition")

        group = VGroup(bayes, arrow, intuition)
        group.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        group.scale(0.8)
        group.next_to(self.example, UP, buff = SMALL_BUFF)
        group.shift_onto_screen()
        cross = VGroup(
            Line(UP+LEFT, DOWN+RIGHT),
            Line(UP+RIGHT, DOWN+LEFT),
        )
        cross.replace(arrow, stretch = True)
        cross.set_stroke(RED, 6)
        group.add(cross)

        self.play(*map(FadeIn, [bayes, intuition]))
        self.play(Write(arrow))
        self.play(ShowCreation(cross))
        self.change_student_modes(*["confused"]*3)
        self.dither(2)

        self.bayes_to_intuition = group

    def put_it_first(self):
        poker_example = self.get_poker_example()
        music_example = self.get_music_example()
        disease_group = VGroup(
            self.example, self.bayes_to_intuition
        )

        self.play(disease_group.to_edge, LEFT)
        self.change_student_modes(
            *["pondering"]*3, 
            look_at_arg = disease_group
        )

        poker_example.next_to(self.example, RIGHT)
        music_example.next_to(poker_example, RIGHT)
        examples = VGroup(poker_example, music_example)
        brace = Brace(examples, UP)
        bayes_to_intuition = VGroup(*map(TextMobject, [
            "Bayes", "$\\leftrightarrow$", "Intuition"
        ]))
        bayes_to_intuition.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        bayes_to_intuition.next_to(brace, UP, SMALL_BUFF)
        check = TexMobject("\\checkmark")
        check.highlight(GREEN)
        check.next_to(bayes_to_intuition[1], UP, SMALL_BUFF)

        for example in examples:
            self.play(FadeIn(example))
            self.dither()
        self.play(GrowFromCenter(brace))
        self.play(FadeIn(bayes_to_intuition))
        self.play(Write(check))
        self.dither(2)

        self.intuitive_examples = VGroup(
            examples, brace, bayes_to_intuition, check
        )

    def swap_example_order(self):
        intuitive_examples = self.intuitive_examples
        disease_group = VGroup(
            self.example, self.bayes_to_intuition
        )

        self.play(
            disease_group.next_to, 
                self.teacher.get_corner(UP+LEFT), UP,
            disease_group.shift, LEFT,
            intuitive_examples.scale, 0.7,
            intuitive_examples.to_corner, UP+LEFT,
            self.teacher.change_mode, "sassy"
        )

    def other_culprit(self):
        bayes = self.bayes_to_intuition[0]
        something_else = TextMobject("Something else")
        something_else.highlight(YELLOW)
        something_else.scale_to_fit_height(bayes.get_height())
        something_else.move_to(bayes, RIGHT)
        new_group = VGroup(
            something_else, 
            *self.bayes_to_intuition[1:]
        )

        self.play(bayes.to_edge, UP)
        self.play(Write(something_else))
        self.play(new_group.next_to, self.example, UP, SMALL_BUFF)
        self.change_student_modes(
            "erm", "confused", "hesitant",
            added_anims = [self.teacher.change_mode, "happy"]
        )
        self.dither(3)


    #####

    def get_poker_example(self):
        rect = self.get_example_rect()
        values = IntroducePokerHand.CONFIG["community_card_values"]
        community_cards = VGroup(*map(PlayingCard, values))
        community_cards.arrange_submobjects(RIGHT)
        deck = VGroup(*[
            PlayingCard(turned_over = True)
            for x in range(5)
        ])
        for i, card in enumerate(deck):
            card.shift(i*(0.03*RIGHT + 0.015*DOWN))
        deck.next_to(community_cards, LEFT)
        cards = VGroup(deck, community_cards)
        cards.scale_to_fit_width(rect.get_width() - 2*SMALL_BUFF)
        cards.next_to(rect.get_bottom(), UP, MED_SMALL_BUFF)

        probability = TexMobject(
            "P(", "\\text{Flush}", "|", "\\text{High bet}", ")"
        )
        probability.highlight_by_tex("Flush", RED)
        probability.highlight_by_tex("High bet", GREEN)
        probability.scale(0.5)
        probability.next_to(rect.get_top(), DOWN)

        return VGroup(rect, probability, cards)

    def get_music_example(self):
        rect = self.get_example_rect()

        musician = Randolph(mode = "soulful_musician")
        musician.left_arm_range = [.36, .45]
        musician.arms = musician.get_arm_copies()
        guitar = musician.guitar = Guitar()
        guitar.move_to(musician)
        guitar.shift(0.31*RIGHT + 0.6*UP)
        musician.add(guitar, musician.arms)
        musician.scale_to_fit_height(0.7*rect.get_height())
        musician.next_to(rect.get_bottom(), UP, SMALL_BUFF)

        probability = TexMobject(
            "P(", "\\text{Suck }", "|", "\\text{ Good review}", ")"
        )
        probability.highlight_by_tex("Suck", RED)
        probability.highlight_by_tex("Good", GREEN)
        probability.scale(0.5)
        probability.next_to(rect.get_top(), DOWN)

        return VGroup(rect, musician, probability)

    def get_example_rect(self):
        rect = self.example[0].copy()
        rect.highlight(WHITE)
        return rect

class OneInOneThousandHaveDisease(Scene):
    def construct(self):
        title = TextMobject("1 in 1{,}000")
        title.to_edge(UP)
        creature = PiCreature()
        all_creatures = VGroup(*[
            VGroup(*[
                creature.copy()
                for y in range(25)
            ]).arrange_submobjects(DOWN, SMALL_BUFF)
            for x in range(40)
        ]).arrange_submobjects(RIGHT, SMALL_BUFF)
        all_creatures.scale_to_fit_width(2*SPACE_WIDTH - 4)
        all_creatures.next_to(title, DOWN)
        randy = all_creatures[0][0]
        all_creatures[0].remove(randy)
        randy.change_mode("sick")
        randy.highlight(SICKLY_GREEN)
        randy.save_state()
        randy.scale_to_fit_height(3)
        randy.center()
        randy.change_mode("plain")
        randy.highlight(BLUE)

        self.add(randy)
        self.play(
            randy.change_mode, "sick",
            randy.highlight, SICKLY_GREEN
        )
        self.play(Blink(randy))
        self.play(randy.restore)
        self.play(
            Write(title),
            LaggedStart(FadeIn, all_creatures, run_time = 3)
        )
        self.dither()

class TestScene(Scene):
    def get_result(self, creature, word, color):
        arrow = self.get_test_arrow()
        test_result = TextMobject(word)
        test_result.highlight(color)
        test_result.next_to(arrow.get_end(), RIGHT)
        group = VGroup(arrow, test_result)
        group.next_to(creature, RIGHT, aligned_edge = UP)
        return group

    def get_positive_result(self, creature):
        return self.get_result(creature, "Diseased", SICKLY_GREEN)

    def get_negative_result(self, creature):
        return self.get_result(creature, "Healthy", GREEN)

    def get_test_arrow(self):
        arrow = Arrow(
            LEFT, RIGHT, 
            color = WHITE,
        )
        word = TextMobject("Test")
        word.scale(0.8)
        word.next_to(arrow, UP, buff = 0)
        arrow.add(word)
        return arrow

class TestDiseaseCase(TestScene):
    def construct(self):
        randy = Randolph(
            mode = "sick",
            color = SICKLY_GREEN
        )
        randy.next_to(ORIGIN, LEFT)
        result = self.get_positive_result(randy)
        accuracy = TextMobject("100\\% Accuracy")
        accuracy.next_to(VGroup(randy, result), UP, LARGE_BUFF)

        self.add(randy)
        self.play(FadeIn(result[0]))
        self.play(Write(result[1]))
        self.play(FadeIn(accuracy))
        self.dither()

class TestNonDiseaseCase(TestScene):
    def construct(self):
        pass

class ReceivePositiveResults(TestScene):
    def construct(self):
        pass

class RephraseQuestion(Scene):
    def construct(self):
        pass




















