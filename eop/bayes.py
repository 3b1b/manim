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

class IntroducePokerHand(PiCreatureScene, SampleSpaceScene):
    CONFIG = {
        "community_cards_center" : 1.5*DOWN,
        "community_card_values" : ["10S", "QH", "AH", "2C", "5H"],
        "your_hand_values" : ["JS", "KC"],
    }
    def construct(self):
        self.add_cards()
        self.indicate_straight()
        self.show_flush_potential()
        self.compute_flush_probability()
        self.show_flush_sample_space()
        self.talk_through_sample_space()
        self.place_high_bet()
        self.change_belief()
        self.move_community_cards_out_of_the_way()
        self.name_bayes_rule()

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
        self.deck = deck

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
        you.hand.target.shift(MED_SMALL_BUFF*UP)

        self.play(LaggedStart(
            MoveToTarget,
            selected_community_cards,
            run_time = 1.5
        ))
        self.play(MoveToTarget(you.hand))
        self.play(LaggedStart(
            ApplyMethod,
            straight_cards,
            lambda m : (m.highlight, YELLOW),
            rate_func = there_and_back,
            run_time = 1.5,
            lag_ratio = 0.5,
            remover = True,
        ))
        self.play(you.change, "hooray", straight_cards)
        self.dither(2)
        self.play(
            selected_community_cards.restore,
            you.hand.restore,
            you.change_mode, "happy"
        )
        self.dither()

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

        her.glasses.save_state()
        her.glasses.move_to(her.hand.target)
        her.glasses.set_fill(opacity = 0)

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
            her.glasses.restore,
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

        sample_space = self.get_sample_space()
        sample_space.add_title("Your belief")
        sample_space.move_to(VGroup(you.hand, her.hand))
        sample_space.to_edge(UP, buff = MED_SMALL_BUFF)
        p = 1./22
        sample_space.divide_horizontally(
            p, colors = [SuitSymbol.CONFIG["red"], BLUE_E]
        )
        braces, labels = sample_space.get_side_braces_and_labels([
            percentage.get_tex_string(), "95.5\\%"
        ])
        top_label, bottom_label = labels

        self.play(
            FadeIn(sample_space),
            ReplacementTransform(percentage, top_label)
        )
        self.play(*map(GrowFromCenter, [
            brace for brace in braces
        ]))
        self.dither(2)
        self.play(Write(bottom_label))
        self.dither(2)

        self.sample_space = sample_space

    def talk_through_sample_space(self):
        her = self.her
        sample_space = self.sample_space
        top_part, bottom_part = self.sample_space.horizontal_parts

        flush_hands, non_flush_hands = hand_lists = [
            [self.get_hand(her, keys) for keys in key_list]
            for key_list in [
                [("3H", "8H"), ("4H", "5H"), ("JH", "KH")],
                [("AC", "6D"), ("3D", "6S"), ("JH", "4C")],
            ]
        ]   
        for hand_list, part in zip(hand_lists, [top_part, bottom_part]):
            self.play(Indicate(part, scale_factor = 1))
            for hand in hand_list:
                hand.save_state()
                hand.scale(0.01)
                hand.move_to(part.get_right())
                self.play(hand.restore)
            self.dither()
        self.dither()
        self.play(*map(FadeOut, it.chain(*hand_lists)))

    def place_high_bet(self):
        you, her = self.you, self.her
        pre_money = VGroup(*[
            VGroup(*[
                TexMobject("\\$")
                for x in range(10)
            ]).arrange_submobjects(RIGHT, buff = SMALL_BUFF)
            for y in range(4)
        ]).arrange_submobjects(UP, buff = SMALL_BUFF)
        money = VGroup(*it.chain(*pre_money))
        money.highlight(GREEN)
        money.scale(0.8)
        money.next_to(her.hand, DOWN)
        for dollar in money:
            dollar.save_state()
            dollar.scale(0.01)
            dollar.move_to(her.get_boundary_point(RIGHT))
            dollar.set_fill(opacity = 0)

        self.play(LaggedStart(
            ApplyMethod,
            money,
            lambda m : (m.restore,),
            run_time = 5,
        ))
        self.play(you.change_mode, "confused")
        self.dither()

        self.money = money

    def change_belief(self):
        numbers = self.sample_space.horizontal_parts.labels
        rect = Rectangle(stroke_width = 0)
        rect.set_fill(BLACK, 1)
        rect.stretch_to_fit_width(numbers.get_width())
        rect.stretch_to_fit_height(self.sample_space.get_height())
        rect.move_to(numbers, UP)

        self.play(FadeIn(rect))
        anims = self.get_horizontal_division_change_animations(0.2)
        anims.append(Animation(rect))
        self.play(
            *anims,
            run_time = 3,
            rate_func = there_and_back
        )
        self.play(FadeOut(rect))

    def move_community_cards_out_of_the_way(self):
        cards = self.community_cards
        cards.generate_target()
        cards.target.arrange_submobjects(
            RIGHT, buff = -cards[0].get_width() + MED_SMALL_BUFF,
        )
        cards.target.move_to(self.deck)
        cards.target.to_edge(LEFT)

        self.sample_space.add_braces_and_labels()

        self.play(
            self.deck.scale, 0.7,
            self.deck.next_to, cards.target, UP,
            self.deck.to_edge, LEFT,
            self.sample_space.shift, 3*DOWN,
            MoveToTarget(cards)
        )

    def name_bayes_rule(self):
        title = TextMobject("Bayes' rule")
        title.highlight(BLUE)
        title.to_edge(UP)
        subtitle = TextMobject("Update ", "prior ", "beliefs")
        subtitle.scale(0.8)
        subtitle.next_to(title, DOWN)
        prior_word = subtitle.get_part_by_tex("prior")
        numbers = self.sample_space.horizontal_parts.labels
        rect = SurroundingRectangle(numbers, color = GREEN)
        arrow = Arrow(prior_word.get_bottom(), rect.get_top())
        arrow.highlight(GREEN)

        words = TextMobject(
            "Maybe she really \\\\ does have a flush $\\dots$",
            alignment = ""
        )
        words.scale(0.7)
        words.next_to(self.money, DOWN, aligned_edge = LEFT)

        self.play(
            Write(title, run_time = 2),
            self.you.change_mode, "pondering"
        )
        self.dither()
        self.play(FadeIn(subtitle))
        self.play(prior_word.highlight, GREEN)
        self.play(
            ShowCreation(rect),
            ShowCreation(arrow)
        )
        self.dither(3)
        self.play(Write(words))
        self.dither(3)


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

        glasses = SunGlasses(her)
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

class YourGutKnowsBayesRule(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Your gut knows \\\\ Bayes' rule.",
            run_time = 1
        )
        self.change_student_modes("confused", "gracious", "guilty")
        self.dither(3)

class UpdatePokerPrior(SampleSpaceScene):
    CONFIG = {
        "double_heart_template" : "HH",
        "cash_string" : "\\$\\$\\$",
    }
    def construct(self):
        self.force_skipping()

        self.add_sample_space()
        self.add_top_conditionals()
        self.react_to_top_conditionals()
        self.add_bottom_conditionals()
        # self.ask_where_conditionals_come_from()
        # self.vary_conditionals()
        self.show_restricted_space()
        self.write_P_flush_given_bet()
        self.reshape_rectangles()
        self.compare_prior_to_posterior()
        self.tweak_estimates()
        self.compute_posterior()

    def add_sample_space(self):
        p = 1./22
        sample_space = SampleSpace(fill_opacity = 0)
        sample_space.shift(LEFT)
        sample_space.divide_horizontally(p, colors = [
            SuitSymbol.CONFIG["red"], BLUE_E
        ])
        labels = self.get_prior_labels(p)
        braces_and_labels = sample_space.get_side_braces_and_labels(labels)

        self.play(
            DrawBorderThenFill(sample_space),
            Write(braces_and_labels)
        )
        self.dither()

        sample_space.add(braces_and_labels)
        self.sample_space = sample_space

    def add_top_conditionals(self):
        top_part = self.sample_space.horizontal_parts[0]
        color = average_color(YELLOW, GREEN, GREEN)
        p = 0.97
        top_part.divide_vertically(p, colors = [color, BLUE])
        label = self.get_conditional_label(p, True)
        brace, _ignore = top_part.get_top_braces_and_labels([label])

        explanation = TextMobject(
            "Probability of", "high bet", "given", "flush"
        )
        explanation.highlight_by_tex("high bet", GREEN)
        explanation.highlight_by_tex("flush", RED)
        explanation.scale(0.6)
        explanation.next_to(label, UP)

        self.play(
            FadeIn(top_part.vertical_parts),
            Write(explanation, run_time = 3),
            GrowFromCenter(brace),
        )
        self.play(LaggedStart(FadeIn, label, run_time = 2, lag_ratio = 0.7))
        self.dither(2)

        self.sample_space.add(brace, label)

        self.top_explanation = explanation
        self.top_conditional_rhs = label[-1]

    def react_to_top_conditionals(self):
        her = PiCreature(color = BLUE_B).flip()
        her.next_to(self.sample_space, RIGHT)
        her.to_edge(RIGHT)
        glasses = SunGlasses(her)
        glasses.save_state()
        glasses.shift(UP)
        glasses.set_fill(opacity = 0)
        her.glasses = glasses

        self.play(FadeIn(her))
        self.play(glasses.restore)
        self.play(
            her.change_mode, "happy", 
            Animation(glasses)
        )
        self.dither(2)

        self.her = her
        
    def add_bottom_conditionals(self):
        her = self.her
        bottom_part = self.sample_space.horizontal_parts[1]
        p = 0.3
        bottom_part.divide_vertically(p, colors = [GREEN_E, BLUE_E])
        label = self.get_conditional_label(p, False)
        brace, _ignore = bottom_part.get_bottom_braces_and_labels([label])

        explanation = TextMobject(
            "Probability of", "high bet", "given", "no flush"
        )
        explanation.highlight_by_tex("high bet", GREEN)
        explanation.highlight_by_tex("no flush", RED)
        explanation.scale(0.6)
        explanation.next_to(label, DOWN)

        self.play(DrawBorderThenFill(bottom_part.vertical_parts))
        self.play(GrowFromCenter(brace))
        self.play(
            her.change_mode, "shruggie",
            MaintainPositionRelativeTo(her.glasses, her.eyes)
        )
        self.play(Write(explanation))
        self.dither()
        self.play(*[
            ReplacementTransform(
                VGroup(explanation[j].copy()),
                VGroup(*label[i1:i2]),
                run_time = 2,
                rate_func = squish_rate_func(smooth, a, a+0.5)
            )
            for a, (i1, i2, j) in zip(np.linspace(0, 0.5, 4), [
                (0, 1, 0),
                (1, 2, 1),
                (2, 3, 2),
                (3, 6, 3),
            ])
        ])
        self.play(Write(VGroup(*label[-2:])))
        self.dither(2)
        self.play(*map(FadeOut, [her, her.glasses]))

        self.sample_space.add(brace, label)
        self.bottom_explanation = explanation
        self.bottom_conditional_rhs = label[-1]

    def ask_where_conditionals_come_from(self):
        randy = Randolph().flip()
        randy.scale(0.75)
        randy.to_edge(RIGHT)
        randy.shift(2*DOWN)
        words = TextMobject("Where do these \\\\", "numbers", "come from?")
        numbers_word = words.get_part_by_tex("numbers")
        numbers_word.highlight(YELLOW)
        words.scale(0.7)
        bubble = ThoughtBubble(height = 3, width = 4)
        bubble.pin_to(randy)
        bubble.shift(MED_LARGE_BUFF*RIGHT)
        bubble.add_content(words)

        numbers = VGroup(
            self.top_conditional_rhs, 
            self.bottom_conditional_rhs
        )
        numbers.save_state()
        arrows = VGroup(*[
            Arrow(
                numbers_word.get_left(), 
                num.get_right(), 
                buff = 2*SMALL_BUFF
            )
            for num in numbers
        ])

        questions = VGroup(*map(TextMobject, [
            "Does she bluff?",
            "How much does she have?",
            "Does she take risks?",
            "What's her model of me?",
            "\\vdots"
        ]))
        questions.arrange_submobjects(DOWN, aligned_edge = LEFT)
        questions[-1].next_to(questions[-2], DOWN)
        questions.scale(0.7)
        questions.next_to(randy, UP)
        questions.shift_onto_screen()

        self.play(
            randy.change_mode, "confused",
            ShowCreation(bubble),
            Write(words, run_time = 2)
        )
        self.play(*map(ShowCreation, arrows))
        self.play(numbers.highlight, YELLOW)
        self.play(Blink(randy))
        self.play(randy.change_mode, "maybe")
        self.play(*map(FadeOut, [
            bubble, words, arrows
        ]))
        for question in questions:
            self.play(
                FadeIn(question),
                randy.look_at, question
            )
        self.dither()
        self.play(Blink(randy))
        self.dither()
        self.play(
            randy.change_mode, "pondering",
            FadeOut(questions)
        )

        self.randy = randy

    def vary_conditionals(self):
        randy = self.randy
        rects = VGroup(*[
            SurroundingRectangle(
                VGroup(explanation),
                buff = SMALL_BUFF,
            )
            for explanation, rhs in zip(
                [self.top_explanation, self.bottom_explanation],
                [self.top_conditional_rhs, self.bottom_conditional_rhs],
            )
        ])

        new_conditionals = [
            (0.91, 0.4),
            (0.83, 0.1),
            (0.99, 0.2),
            (0.97, 0.3),
        ]

        self.play(*map(ShowCreation, rects))
        self.play(FadeOut(rects))
        for i, value in enumerate(it.chain(*new_conditionals)):
            self.play(
                randy.look_at, rects[i%2],
                *self.get_conditional_change_anims(i%2, value)
            )
            if i%2 == 1:
                self.dither()
        self.play(FadeOut(randy))

    def show_restricted_space(self):
        high_bet_space, low_bet_space = [
            VGroup(*[
                self.sample_space.horizontal_parts[i].vertical_parts[j]
                for i in range(2)
            ])
            for j in range(2)
        ]
        words = TexMobject("P(", self.cash_string, ")")
        words.highlight_by_tex(self.cash_string, GREEN)
        words.next_to(self.sample_space, RIGHT)
        low_bet_space.generate_target()
        for submob in low_bet_space.target:
            submob.highlight(average_color(
                submob.get_color(), *[BLACK]*4
            ))
        arrows = VGroup(*[
            Arrow(
                words.get_left(),
                submob.get_edge_center(vect),
                color = submob.get_color()
            )
            for submob, vect in zip(high_bet_space, [DOWN, RIGHT])
        ])

        self.play(MoveToTarget(low_bet_space))
        self.play(
            Write(words),
            *map(ShowCreation, arrows)
        )
        self.dither()
        for rect in high_bet_space:
            self.play(Indicate(rect, scale_factor = 1))
        self.play(*map(FadeOut, [words, arrows]))

        self.high_bet_space = high_bet_space

    def write_P_flush_given_bet(self):
        posterior_tex = TexMobject(
            "P(", self.double_heart_template, 
            "|", self.cash_string, ")"
        )
        posterior_tex.scale(0.7)
        posterior_tex.highlight_by_tex(self.cash_string, GREEN)
        self.insert_double_heart(posterior_tex)
        rects = self.high_bet_space.copy()
        rects = [rects[0].copy()] + list(rects)
        for rect in rects:
            rect.generate_target()
        numerator = rects[0].target
        plus = TexMobject("+")
        denominator = VGroup(rects[1].target, plus, rects[2].target)
        denominator.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        frac_line = TexMobject("\\over")
        frac_line.stretch_to_fit_width(denominator.get_width())
        fraction = VGroup(numerator, frac_line, denominator)
        fraction.arrange_submobjects(DOWN)

        arrow = TexMobject("\\downarrow")
        group = VGroup(posterior_tex, arrow, fraction)
        group.arrange_submobjects(DOWN)
        group.to_corner(UP+RIGHT)

        self.play(Write(posterior_tex))
        self.play(Write(arrow))
        self.play(MoveToTarget(rects[0]))
        self.dither()
        self.play(*it.chain(
            map(Write, [frac_line, plus]),
            map(MoveToTarget, rects[1:])
        ))
        self.dither(3)

        self.posterior_tex = posterior_tex
        self.to_fade = VGroup(arrow, frac_line, plus)
        self.to_post_rects = VGroup(VGroup(*rects[:2]),rects[2])

    def reshape_rectangles(self):
        post_rects = self.get_posterior_rectangles()
        braces, labels = self.get_posterior_rectangle_braces_and_labels(
            post_rects, [self.posterior_tex.copy()]
        )
        height_rect = SurroundingRectangle(braces)

        self.play(
            FadeOut(self.to_fade),
            ReplacementTransform(
                self.to_post_rects, post_rects,
                run_time = 2,
            ),
        )
        self.dither(2)
        self.play(ReplacementTransform(self.posterior_tex, labels[0]))
        self.posterior_tex = labels[0]
        self.play(GrowFromCenter(braces))
        self.dither()
        self.play(ShowCreation(height_rect))
        self.play(FadeOut(height_rect))
        self.dither()

        self.post_rects = post_rects

    def compare_prior_to_posterior(self):
        prior_tex = self.sample_space.horizontal_parts.labels[0]
        post_tex = self.posterior_tex
        prior_rect, post_rect = [
            SurroundingRectangle(tex, stroke_width = 2)
            for tex in [prior_tex, post_tex]
        ]

        post_words = TextMobject("Posterior", "probability")
        post_words.scale(0.8)
        post_words.to_corner(UP+RIGHT)
        post_arrow = Arrow(
            post_words[0].get_bottom(), post_tex.get_top(),
            color = WHITE
        )

        self.play(ShowCreation(prior_rect))
        self.dither()
        self.play(ReplacementTransform(prior_rect, post_rect))
        self.dither()
        self.play(FadeOut(post_rect))
        self.play(Indicate(post_tex.get_part_by_tex(self.cash_string)))
        self.dither()
        self.play(
            Write(post_words),
            ShowCreation(post_arrow)
        )
        self.dither()
        self.play(post_words[1].fade, 0.8)
        self.dither(2)
        self.play(*map(FadeOut, [post_words, post_arrow]))

    def tweak_estimates(self):
        post_rects = self.post_rects
        self.revert_to_original_skipping_status()
        self.preview_tweaks(post_rects)

    def preview_tweaks(self, post_rects):
        new_value_lists = [
            (0.85, 0.1, 0.11),
            (0.97, 0.3, 1./22),
        ]
        for new_values in new_value_lists:
            for i, value in zip(range(2), new_values):
                self.play(*self.get_conditional_change_anims(
                    i, value, post_rects
                ))
            self.play(*self.get_prior_change_anims(
                new_values[-1], post_rects
            ))
            self.dither()

    def compute_posterior(self):
        pass

    ######

    def get_prior_labels(self, value):
        p_str = "%0.3f"%value
        q_str = "%0.3f"%(1-value)
        labels = [
            TexMobject(
                "P(", s, self.double_heart_template, ")",
                "= ", num
            )
            for s, num in ("", p_str), ("\\text{not }", q_str)
        ]
        for label in labels:
            label.scale(0.7)
            self.insert_double_heart(label)
        return labels

    def get_conditional_label(self, value, given_flush = True):
        label = TexMobject(
            "P(", self.cash_string, "|", 
            "" if given_flush else "\\text{not }",
            self.double_heart_template, ")",
            "=", str(value)
        )
        self.insert_double_heart(label)
        label.highlight_by_tex(self.cash_string, GREEN)
        label.scale(0.7)
        return label

    def insert_double_heart(self, tex_mob):
        double_heart = SuitSymbol("hearts")
        double_heart.add(SuitSymbol("hearts"))
        double_heart.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        double_heart.get_tex_string = lambda : self.double_heart_template
        template = tex_mob.get_part_by_tex(self.double_heart_template)
        double_heart.replace(template)
        tex_mob.submobjects[tex_mob.index_of_part(template)] = double_heart
        return tex_mob

    def get_prior_change_anims(self, value, post_rects = None):
        space = self.sample_space
        parts = space.horizontal_parts
        anims = self.get_horizontal_division_change_animations(
            value, new_label_kwargs = {
                "labels" : self.get_prior_labels(value)
            }
        )
        if post_rects is not None:
            anims += self.get_posterior_rectangle_change_anims(post_rects)
        return anims

    def get_conditional_change_anims(
        self, sub_sample_space_index, value,
        post_rects = None
        ):
        parts = self.sample_space.horizontal_parts
        sub_sample_space = parts[sub_sample_space_index]
        given_flush = (sub_sample_space_index == 0)
        label = self.get_conditional_label(value, given_flush)

        anims = self.get_division_change_animations(
            sub_sample_space, sub_sample_space.vertical_parts, value,
            dimension = 0,
            new_label_kwargs = {"labels" : [label]},
        )

        if post_rects is not None:
            anims += self.get_posterior_rectangle_change_anims(post_rects)

        return anims

    def get_top_conditional_change_anims(self, *args, **kwargs):
        return self.get_conditional_change_anims(0, *args, **kwargs)

    def get_bottom_conditional_change_anims(self, *args, **kwargs):
        return self.get_conditional_change_anims(1, *args, **kwargs)

    def get_prior_rectangles(self):
        return VGroup(*[
            self.sample_space.horizontal_parts[i].vertical_parts[0]
            for i in range(2)
        ])

    def get_posterior_rectangles(self):
        prior_rects = self.get_prior_rectangles()
        areas = [
            rect.get_width()*rect.get_height()
            for rect in prior_rects
        ]
        total_area = sum(areas)
        total_height = prior_rects.get_height()

        post_rects = prior_rects.copy()
        for rect, area in zip(post_rects, areas):
            rect.stretch_to_fit_height(total_height * area/total_area)
            rect.stretch_to_fit_width(
                area/rect.get_height()
            )
        post_rects.arrange_submobjects(DOWN, buff = 0)
        post_rects.next_to(
            self.sample_space.full_space, RIGHT, MED_LARGE_BUFF
        )
        return post_rects

    def get_posterior_rectangle_braces_and_labels(self, post_rects, labels):
        braces = VGroup()
        label_mobs = VGroup()
        for label, rect in zip(labels, post_rects):
            if not isinstance(label, Mobject):
                label_mob = TexMobject(label)
                label_mob.scale(0.7)
            else:
                label_mob = label
            brace = Brace(
                rect, RIGHT, 
                buff = SMALL_BUFF, 
                min_num_quads = 2
            )
            label_mob.next_to(brace, RIGHT, SMALL_BUFF)

            label_mobs.add(label_mob)
            braces.add(brace)
        post_rects.braces = braces
        post_rects.labels = label_mobs
        return VGroup(braces, label_mobs)

    def update_posterior_braces(self, post_rects):
        braces = post_rects.braces
        labels = post_rects.labels
        for rect, brace, label in zip(post_rects, braces, labels):
            brace.stretch_to_fit_height(rect.get_height())
            brace.next_to(rect, RIGHT, SMALL_BUFF)
            label.next_to(brace, RIGHT, SMALL_BUFF)

    def get_posterior_rectangle_change_anims(self, post_rects):
        def update_rects(rects):
            new_rects = self.get_posterior_rectangles() 
            Transform(rects, new_rects).update(1)
            if hasattr(rects, "braces"):
                self.update_posterior_braces(rects)
            return rects

        anims = [UpdateFromFunc(post_rects, update_rects)]
        if hasattr(post_rects, "braces"):
            anims += map(Animation, [
                post_rects.labels, post_rects.braces
            ])
        return anims


class NextVideoWrapper(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Next video: Bayesian networks")
        title.scale(0.8)
        title.to_edge(UP, buff = SMALL_BUFF)
        screen = ScreenRectangle(height = 4)
        screen.next_to(title, DOWN)
        title.save_state()
        title.shift(DOWN)
        title.set_fill(opacity = 0)

        self.play(
            title.restore,
            self.teacher.change, "raise_right_hand"
        )
        self.play(ShowCreation(screen))
        self.change_student_modes(*["pondering"]*3)
        self.play(Animation(screen))
        self.dither(5)

























