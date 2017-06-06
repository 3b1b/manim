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

#revert_to_original_skipping_status

#########

class BayesOpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "Inside every non-Bayesian there \\\\ is a Bayesian struggling to get out."
        ],
        "author" : "Dennis V. Lindley",
    }

class IntroducePokerHand(PiCreatureScene):
    CONFIG = {
        "community_cards_center" : 1.5*DOWN,
        "community_card_values" : ["AS", "QH", "10H", "2C", "5H"],
        "your_hand_values" : ["JS", "KC"],
    }
    def construct(self):
        self.force_skipping()

        self.add_cards()
        # self.indicate_straight()
        self.show_flush_potential()
        self.compute_flush_probability()
        self.show_flush_sample_space()
        self.place_high_bet()

    def add_cards(self):
        you, her = self.you, self.her
        community_cards = VGroup(*map(
            PlayingCard, self.community_card_values
        ))
        community_cards.arrange_submobjects(RIGHT)
        community_cards.move_to(self.community_cards_center)
        deck = VGroup(*[
            PlayingCard(turned_over = True)
            for x in range(5)
        ])
        for i, card in enumerate(deck):
            card.shift(i*(0.03*RIGHT + 0.015*DOWN))
        deck.next_to(community_cards, LEFT)

        you.hand = self.get_hand(you, self.your_hand_values)
        her.hand = self.get_hand(her, None)
        hand_cards = VGroup(*it.chain(*zip(you.hand, her.hand)))

        self.add(deck)
        for group in hand_cards, community_cards:
            for card in group:
                card.generate_target()
                card.scale(0.01)
                card.move_to(deck[-1], UP+RIGHT)
            self.play(LaggedStart(MoveToTarget, group, lag_ratio = 0.8))
            self.dither()
        self.dither()

        self.community_cards = community_cards

    def indicate_straight(self):
        you = self.you
        community_cards = self.community_cards
        you.hand.save_state()
        you.hand.generate_target()
        for card in you.hand.target:
            card.scale_to_fit_height(community_cards.get_height())

        selected_community_cards = VGroup(*filter(
            lambda card : card.numerical_value >= 10,
            community_cards
        ))
        card_cmp = lambda c1, c2 : cmp(
            c1.numerical_value, c2.numerical_value
        )
        selected_community_cards.submobjects.sort(card_cmp)

        selected_community_cards.save_state()
        for card in selected_community_cards:
            card.generate_target()

        straight_cards = VGroup(*it.chain(
            you.hand.target, 
            [c.target for c in selected_community_cards]
        ))
        straight_cards.submobjects.sort(card_cmp)
        straight_cards.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        straight_cards.next_to(community_cards, UP, aligned_edge = LEFT)

        self.play(LaggedStart(
            MoveToTarget,
            selected_community_cards,
            run_time = 1.5
        ))
        self.play(MoveToTarget(you.hand))
        self.play(you.change, "hooray", straight_cards)
        self.play(LaggedStart(
            ApplyMethod,
            straight_cards,
            lambda m : (m.highlight, YELLOW),
            rate_func = there_and_back,
            run_time = 1.5,
            lag_ratio = 0.5,
            remover = True,
        ))
        self.dither(2)
        self.play(
            selected_community_cards.restore,
            you.hand.restore,
            you.change_mode, "happy"
        )

    def show_flush_potential(self):
        you, her = self.you, self.her
        heart_cards = VGroup(*filter(
            lambda c : c.suit == "hearts",
            self.community_cards
        ))
        heart_cards.save_state()

        her.hand.save_state()
        her.hand.generate_target()
        her.hand.target.arrange_submobjects(RIGHT)
        her.hand.target.next_to(heart_cards, UP)
        her.hand.target.to_edge(UP)

        heart_qs = VGroup()
        hearts = VGroup()
        q_marks = VGroup()
        for target in her.hand.target:
            heart = SuitSymbol("hearts")
            q_mark = TexMobject("?")
            heart_q = VGroup(heart, q_mark)
            for mob in heart_q:
                mob.scale_to_fit_height(0.5)
            heart_q.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
            heart_q.move_to(target)
            heart_qs.add(heart, q_mark)
            hearts.add(heart)
            q_marks.add(q_mark)

        self.play(heart_cards.shift, heart_cards.get_height()*UP)
        self.play(you.change_mode, "hesitant")
        self.play(MoveToTarget(her.hand))
        self.play(LaggedStart(DrawBorderThenFill, heart_qs))
        self.play(
            her.change, "happy",
            DrawBorderThenFill(her.glasses)
        )
        self.pi_creatures.remove(her)
        new_suit_pairs = [
            ("clubs", "diamonds"),
            ("diamonds", "spades"),
            ("spades", "clubs"),
            ("hearts", "hearts"),
        ]
        for new_suit_pair in new_suit_pairs:
            new_symbols = VGroup(*map(SuitSymbol, new_suit_pair))
            for new_symbol, heart in zip(new_symbols, hearts):
                new_symbol.replace(heart, dim_to_match = 1)
            self.play(Transform(
                hearts, new_symbols,
                submobject_mode = "lagged_start"
            ))
            self.dither()
        self.play(FadeOut(heart_qs))
        self.play(
            heart_cards.restore,
            her.hand.restore,
            you.change_mode, "pondering",
        )

        self.q_marks = q_marks

    def compute_flush_probability(self):
        you, her = self.you, self.her
        equation = TexMobject(
            "{ {10 \\choose 2}", "\\over", "{45 \\choose 2} }", 
            "=", "{1 \\over 22}", "\\approx", "4.5\\%"
        )
        equation.next_to(self.community_cards, UP, buff = LARGE_BUFF)
        percentage = equation.get_part_by_tex("4.5")

        ten = VGroup(*equation[0][1:3])
        num_hearts = TextMobject("\\# Remaining hearts")
        num_hearts.scale(0.75)
        num_hearts.next_to(
            ten, UP, aligned_edge = LEFT
        )
        num_hearts.to_edge(UP)
        num_hearts.highlight(RED)
        num_hearts_arrow = Arrow(
            num_hearts.get_bottom(), ten.get_right(),
            color = RED, buff = SMALL_BUFF
        )

        fourty_five = VGroup(*equation[2][1:3])
        num_cards = TextMobject("\\# Remaining cards")
        num_cards.scale(0.75)
        num_cards.next_to(fourty_five, LEFT)
        num_cards.to_edge(LEFT)
        num_cards.highlight(BLUE)
        num_cards_arrow = Arrow(
            num_cards, fourty_five,
            color = BLUE, buff = SMALL_BUFF
        )

        self.revert_to_original_skipping_status()
        self.play(LaggedStart(FadeIn, equation))
        self.dither(2)
        self.play(
            FadeIn(num_hearts), 
            ShowCreation(num_hearts_arrow),
            ten.highlight, RED,
        )
        self.play(
            FadeIn(num_cards), 
            ShowCreation(num_cards_arrow),
            fourty_five.highlight, BLUE
        )
        self.dither(3)
        equation.remove(percentage)
        self.play(*map(FadeOut, [
            equation, 
            num_hearts, num_hearts_arrow,
            num_cards, num_cards_arrow,
        ]))


        self.percentage = percentage

    def show_flush_sample_space(self):
        you, her = self.you, self.her
        percentage = self.percentage

        sample_space = SampleSpace()
        sample_space.add_title()
        sample_space.move_to(VGroup(you.hand, her.hand))
        sample_space.to_edge(UP, buff = MED_SMALL_BUFF)
        sample_space.shift(RIGHT)
        p = 1./22
        top_part, bottom_part = sample_space.divide_horizontally(
            p, colors = [SuitSymbol.CONFIG["red"], BLUE_E]
        )

        self.revert_to_original_skipping_status()
        self.play(FadeIn(sample_space))
        self.dither()
        self.add(top_part, bottom_part)

    def place_high_bet(self):
        pass


    ######

    def create_pi_creatures(self):
        shift_val = 3
        you = PiCreature(color = BLUE_D)
        her = PiCreature(color = BLUE_B).flip()
        for pi in you, her:
            pi.scale(0.5)
        you.to_corner(UP+LEFT)
        her.to_corner(UP+RIGHT)
        you.make_eye_contact(her)

        glasses = SVGMobject(file_name = "sunglasses")
        glasses.set_stroke(WHITE, width = 0)
        glasses.set_fill(GREY, 1)
        glasses.scale_to_fit_width(
            1.1*her.eyes.get_width()
        )
        glasses.move_to(her.eyes, UP)

        her.glasses = glasses
        self.you = you
        self.her = her
        return VGroup(you, her)

    def get_hand(self, pi_creature, keys = None):
        if keys is not None:
            hand = VGroup(*map(PlayingCard, keys))
        else:
            hand = VGroup(*[
                PlayingCard(turned_over = True)
                for x in range(2)
            ])
        hand.scale(0.7)
        card1, card2 = hand
        vect = np.sign(pi_creature.get_center()[0])*LEFT
        card2.move_to(card1)
        card2.shift(MED_SMALL_BUFF*RIGHT + SMALL_BUFF*DOWN)
        hand.next_to(
            pi_creature, vect, 
            buff = MED_LARGE_BUFF,
            aligned_edge = UP
        )
        return hand
    

class HowDoesPokerWork(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Wait, how does \\\\ poker work again?",
            target_mode = "confused",
            run_time = 1
        )
        self.change_student_modes(*["confused"]*3)
        self.dither(2)

class ShowCountingArgument(IntroducePokerHand):
    def construct(self):
        pass



























