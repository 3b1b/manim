from manimlib.imports import *

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
        community_cards = VGroup(*list(map(
            PlayingCard, self.community_card_values
        )))
        community_cards.arrange(RIGHT)
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
        hand_cards = VGroup(*it.chain(*list(zip(you.hand, her.hand))))

        self.add(deck)
        for group in hand_cards, community_cards:
            for card in group:
                card.generate_target()
                card.scale(0.01)
                card.move_to(deck[-1], UP+RIGHT)
            self.play(LaggedStartMap(MoveToTarget, group, lag_ratio = 0.8))
            self.wait()
        self.wait()

        self.community_cards = community_cards
        self.deck = deck

    def indicate_straight(self):
        you = self.you
        community_cards = self.community_cards
        you.hand.save_state()
        you.hand.generate_target()
        for card in you.hand.target:
            card.set_height(community_cards.get_height())

        selected_community_cards = VGroup(*[card for card in community_cards if card.numerical_value >= 10])
        selected_community_cards.submobjects.sort(
            key=lambda c: c.numerical_value
        )

        selected_community_cards.save_state()
        for card in selected_community_cards:
            card.generate_target()

        straight_cards = VGroup(*it.chain(
            you.hand.target, 
            [c.target for c in selected_community_cards]
        ))
        straight_cards.submobjects.sort(
            key=lambda c: c.numerical_value
        )
        straight_cards.arrange(RIGHT, buff = SMALL_BUFF)
        straight_cards.next_to(community_cards, UP, aligned_edge = LEFT)
        you.hand.target.shift(MED_SMALL_BUFF*UP)

        self.play(LaggedStartMap(
            MoveToTarget,
            selected_community_cards,
            run_time = 1.5
        ))
        self.play(MoveToTarget(you.hand))
        self.play(LaggedStartMap(
            ApplyMethod,
            straight_cards,
            lambda m : (m.set_color, YELLOW),
            rate_func = there_and_back,
            run_time = 1.5,
            lag_ratio = 0.5,
            remover = True,
        ))
        self.play(you.change, "hooray", straight_cards)
        self.wait(2)
        self.play(
            selected_community_cards.restore,
            you.hand.restore,
            you.change_mode, "happy"
        )
        self.wait()

    def show_flush_potential(self):
        you, her = self.you, self.her
        heart_cards = VGroup(*[c for c in self.community_cards if c.suit == "hearts"])
        heart_cards.save_state()

        her.hand.save_state()
        her.hand.generate_target()
        her.hand.target.arrange(RIGHT)
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
                mob.set_height(0.5)
            heart_q.arrange(RIGHT, buff = SMALL_BUFF)
            heart_q.move_to(target)
            heart_qs.add(heart, q_mark)
            hearts.add(heart)
            q_marks.add(q_mark)

        self.play(heart_cards.shift, heart_cards.get_height()*UP)
        self.play(you.change_mode, "hesitant")
        self.play(MoveToTarget(her.hand))
        self.play(LaggedStartMap(DrawBorderThenFill, heart_qs))
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
            new_symbols = VGroup(*list(map(SuitSymbol, new_suit_pair)))
            for new_symbol, heart in zip(new_symbols, hearts):
                new_symbol.replace(heart, dim_to_match = 1)
            self.play(Transform(
                hearts, new_symbols,
                lag_ratio = 0.5
            ))
            self.wait()
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
            "=", "{45 \\over 990}", "\\approx", "4.5\\%"
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
        num_hearts.set_color(RED)
        num_hearts_arrow = Arrow(
            num_hearts.get_bottom(), ten.get_right(),
            color = RED, buff = SMALL_BUFF
        )

        fourty_five = VGroup(*equation[2][1:3])
        num_cards = TextMobject("\\# Remaining cards")
        num_cards.scale(0.75)
        num_cards.next_to(fourty_five, LEFT)
        num_cards.to_edge(LEFT)
        num_cards.set_color(BLUE)
        num_cards_arrow = Arrow(
            num_cards, fourty_five,
            color = BLUE, buff = SMALL_BUFF
        )

        self.play(LaggedStartMap(FadeIn, equation))
        self.wait(2)
        self.play(
            FadeIn(num_hearts), 
            ShowCreation(num_hearts_arrow),
            ten.set_color, RED,
        )
        self.play(
            FadeIn(num_cards), 
            ShowCreation(num_cards_arrow),
            fourty_five.set_color, BLUE
        )
        self.wait(3)
        equation.remove(percentage)
        self.play(*list(map(FadeOut, [
            equation, 
            num_hearts, num_hearts_arrow,
            num_cards, num_cards_arrow,
        ])))


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
        self.play(*list(map(GrowFromCenter, [
            brace for brace in braces
        ])))
        self.wait(2)
        self.play(Write(bottom_label))
        self.wait(2)

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
            self.wait()
        self.wait()
        self.play(*list(map(FadeOut, it.chain(*hand_lists))))

    def place_high_bet(self):
        you, her = self.you, self.her
        pre_money = VGroup(*[
            VGroup(*[
                TexMobject("\\$")
                for x in range(10)
            ]).arrange(RIGHT, buff = SMALL_BUFF)
            for y in range(4)
        ]).arrange(UP, buff = SMALL_BUFF)
        money = VGroup(*it.chain(*pre_money))
        money.set_color(GREEN)
        money.scale(0.8)
        money.next_to(her.hand, DOWN)
        for dollar in money:
            dollar.save_state()
            dollar.scale(0.01)
            dollar.move_to(her.get_boundary_point(RIGHT))
            dollar.set_fill(opacity = 0)

        self.play(LaggedStartMap(
            ApplyMethod,
            money,
            lambda m : (m.restore,),
            run_time = 5,
        ))
        self.play(you.change_mode, "confused")
        self.wait()

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
        cards.target.arrange(
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
        title.set_color(BLUE)
        title.to_edge(UP)
        subtitle = TextMobject("Update ", "prior ", "beliefs")
        subtitle.scale(0.8)
        subtitle.next_to(title, DOWN)
        prior_word = subtitle.get_part_by_tex("prior")
        numbers = self.sample_space.horizontal_parts.labels
        rect = SurroundingRectangle(numbers, color = GREEN)
        arrow = Arrow(prior_word.get_bottom(), rect.get_top())
        arrow.set_color(GREEN)

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
        self.wait()
        self.play(FadeIn(subtitle))
        self.play(prior_word.set_color, GREEN)
        self.play(
            ShowCreation(rect),
            ShowCreation(arrow)
        )
        self.wait(3)
        self.play(Write(words))
        self.wait(3)


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
            hand = VGroup(*list(map(PlayingCard, keys)))
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
        self.wait(2)

class YourGutKnowsBayesRule(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Your gut knows \\\\ Bayes' rule.",
            run_time = 1
        )
        self.change_student_modes("confused", "gracious", "guilty")
        self.wait(3)

class UpdatePokerPrior(SampleSpaceScene):
    CONFIG = {
        "double_heart_template" : "HH",
        "cash_string" : "\\$\\$\\$",
    }
    def construct(self):
        self.add_sample_space()
        self.add_top_conditionals()
        self.react_to_top_conditionals()
        self.add_bottom_conditionals()
        self.ask_where_conditionals_come_from()
        self.vary_conditionals()
        self.show_restricted_space()
        self.write_P_flush_given_bet()
        self.reshape_rectangles()
        self.compare_prior_to_posterior()
        self.preview_tweaks()
        self.tweak_non_flush_case()
        self.tweak_flush_case()
        self.tweak_prior()
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
            LaggedStartMap(FadeIn, sample_space),
            Write(braces_and_labels)
        )
        self.wait()

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
        explanation.set_color_by_tex("high bet", GREEN)
        explanation.set_color_by_tex("flush", RED)
        explanation.scale(0.6)
        explanation.next_to(label, UP)

        self.play(
            FadeIn(top_part.vertical_parts),
            FadeIn(label),
            GrowFromCenter(brace),
        )
        self.play(Write(explanation, run_time = 3))
        self.wait(2)

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
        self.wait(2)

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
        explanation.set_color_by_tex("high bet", GREEN)
        explanation.set_color_by_tex("no flush", RED)
        explanation.scale(0.6)
        explanation.next_to(label, DOWN)

        self.play(DrawBorderThenFill(bottom_part.vertical_parts))
        self.play(
            GrowFromCenter(brace),
            FadeIn(label)
        )
        self.play(
            her.change_mode, "shruggie",
            MaintainPositionRelativeTo(her.glasses, her.eyes)
        )
        self.wait()
        self.play(*[
            ReplacementTransform(
                VGroup(*label[i1:i2]).copy(),
                VGroup(explanation[j]),
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
        self.wait()
        self.play(Write(VGroup(*label[-2:])))
        self.wait(2)
        self.play(*list(map(FadeOut, [her, her.glasses])))

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
        numbers_word.set_color(YELLOW)
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

        questions = VGroup(*list(map(TextMobject, [
            "Does she bluff?",
            "How much does she have?",
            "Does she take risks?",
            "What's her model of me?",
            "\\vdots"
        ])))
        questions.arrange(DOWN, aligned_edge = LEFT)
        questions[-1].next_to(questions[-2], DOWN)
        questions.scale(0.7)
        questions.next_to(randy, UP)
        questions.shift_onto_screen()

        self.play(
            randy.change_mode, "confused",
            ShowCreation(bubble),
            Write(words, run_time = 2)
        )
        self.play(*list(map(ShowCreation, arrows)))
        self.play(numbers.set_color, YELLOW)
        self.play(Blink(randy))
        self.play(randy.change_mode, "maybe")
        self.play(*list(map(FadeOut, [
            bubble, words, arrows
        ])))
        for question in questions:
            self.play(
                FadeIn(question),
                randy.look_at, question
            )
        self.wait()
        self.play(Blink(randy))
        self.wait()
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

        self.play(*list(map(ShowCreation, rects)))
        self.play(FadeOut(rects))
        for i, value in enumerate(it.chain(*new_conditionals)):
            self.play(
                randy.look_at, rects[i%2],
                *self.get_conditional_change_anims(i%2, value)
            )
            if i%2 == 1:
                self.wait()
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
        words.set_color_by_tex(self.cash_string, GREEN)
        words.next_to(self.sample_space, RIGHT)
        low_bet_space.generate_target()
        for submob in low_bet_space.target:
            submob.set_color(average_color(
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
            *list(map(ShowCreation, arrows))
        )
        self.wait()
        for rect in high_bet_space:
            self.play(Indicate(rect, scale_factor = 1))
        self.play(*list(map(FadeOut, [words, arrows])))

        self.high_bet_space = high_bet_space

    def write_P_flush_given_bet(self):
        posterior_tex = TexMobject(
            "P(", self.double_heart_template, 
            "|", self.cash_string, ")"
        )
        posterior_tex.scale(0.7)
        posterior_tex.set_color_by_tex(self.cash_string, GREEN)
        self.insert_double_heart(posterior_tex)
        rects = self.high_bet_space.copy()
        rects = [rects[0].copy()] + list(rects)
        for rect in rects:
            rect.generate_target()
        numerator = rects[0].target
        plus = TexMobject("+")
        denominator = VGroup(rects[1].target, plus, rects[2].target)
        denominator.arrange(RIGHT, buff = SMALL_BUFF)
        frac_line = TexMobject("\\over")
        frac_line.stretch_to_fit_width(denominator.get_width())
        fraction = VGroup(numerator, frac_line, denominator)
        fraction.arrange(DOWN)

        arrow = TexMobject("\\downarrow")
        group = VGroup(posterior_tex, arrow, fraction)
        group.arrange(DOWN)
        group.to_corner(UP+RIGHT)

        self.play(LaggedStartMap(FadeIn, posterior_tex))
        self.play(Write(arrow))
        self.play(MoveToTarget(rects[0]))
        self.wait()
        self.play(*it.chain(
            list(map(Write, [frac_line, plus])),
            list(map(MoveToTarget, rects[1:]))
        ))
        self.wait(3)
        self.play(*list(map(FadeOut, [arrow, fraction] + rects)))

        self.posterior_tex = posterior_tex

    def reshape_rectangles(self):
        post_rects = self.get_posterior_rectangles()
        prior_rects = self.get_prior_rectangles()
        braces, labels = self.get_posterior_rectangle_braces_and_labels(
            post_rects, [self.posterior_tex.copy()]
        )
        height_rect = SurroundingRectangle(braces)

        self.play(
            ReplacementTransform(
                prior_rects.copy(), post_rects,
                run_time = 2,
            ),
        )
        self.wait(2)
        self.play(ReplacementTransform(self.posterior_tex, labels[0]))
        self.posterior_tex = labels[0]
        self.play(GrowFromCenter(braces))
        self.wait()
        self.play(ShowCreation(height_rect))
        self.play(FadeOut(height_rect))
        self.wait()

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
        self.wait()
        self.play(ReplacementTransform(prior_rect, post_rect))
        self.wait()
        self.play(FadeOut(post_rect))
        self.play(Indicate(post_tex.get_part_by_tex(self.cash_string)))
        self.wait()
        self.play(
            Write(post_words),
            ShowCreation(post_arrow)
        )
        self.wait()
        self.play(post_words[1].fade, 0.8)
        self.wait(2)
        self.play(*list(map(FadeOut, [post_words, post_arrow])))

    def preview_tweaks(self):
        post_rects = self.post_rects
        new_value_lists = [
            (0.85, 0.1, 0.11),
            (0.97, 0.3, 1./22),
        ]
        for new_values in new_value_lists:
            for i, value in zip(list(range(2)), new_values):
                self.play(*self.get_conditional_change_anims(
                    i, value, post_rects
                ))
            self.play(*self.get_prior_change_anims(
                new_values[-1], post_rects
            ))
        self.wait(2)

    def tweak_non_flush_case(self):
        her = self.her
        her.scale_in_place(0.7)
        her.change_mode("plain")
        her.shift(DOWN)
        her.glasses = SunGlasses(her)
        post_rects = self.post_rects
        posterior = VGroup(post_rects.braces, post_rects.labels)
        prior_rects = self.get_prior_rectangles()
        risk_averse_words = TextMobject(
            "Suppose risk \\\\ averse \\dots"
        )
        risk_averse_words.scale(0.7)
        risk_averse_words.next_to(her, DOWN)
        risk_averse_words.shift_onto_screen()

        arrows = VGroup(*[
            Arrow(ORIGIN, LEFT, tip_length = SMALL_BUFF)
            for x in range(3)
        ])
        arrows.arrange(DOWN)
        arrows.next_to(prior_rects[1], RIGHT, SMALL_BUFF)

        self.wait(2)
        self.play(*list(map(FadeIn, [her, her.glasses])))
        self.play(LaggedStartMap(FadeIn, risk_averse_words))
        self.play(her.change_mode, "sad", Animation(her.glasses))
        self.wait()
        self.play(ShowCreation(arrows))
        self.play(
            *it.chain(
                self.get_conditional_change_anims(1, 0.1, post_rects),
                [Animation(arrows)]
            ),
            run_time = 3
        )
        self.play(FadeOut(arrows))
        self.wait(2)
        post_surrounding_rect = SurroundingRectangle(posterior)
        self.play(ShowCreation(post_surrounding_rect))
        self.play(FadeOut(post_surrounding_rect))
        self.wait()
        self.play(
            FadeOut(risk_averse_words),
            *self.get_conditional_change_anims(1, 0.3, post_rects),
            run_time = 2
        )

    def tweak_flush_case(self):
        her = self.her
        post_rects = self.post_rects

        self.play(
            her.change_mode, "erm", Animation(her.glasses)
        )
        self.play(
            *self.get_conditional_change_anims(0, 0.47, post_rects),
            run_time = 3
        )
        self.wait(3)
        self.play(*self.get_conditional_change_anims(
            0, 0.97, post_rects
        ))
        self.wait()

    def tweak_prior(self):
        her = self.her
        post_rects = self.post_rects

        self.play(
            her.change_mode, "happy", Animation(her.glasses)
        )
        self.play(
            *self.get_prior_change_anims(0.3, post_rects),
            run_time = 2
        )
        self.wait(3)
        self.play(
            *self.get_prior_change_anims(1./22, post_rects),
            run_time = 2
        )
        self.play(*list(map(FadeOut, [her, her.glasses])))

    def compute_posterior(self):
        prior_rects = self.get_prior_rectangles()
        post_tex = self.posterior_tex
        prior_rhs_group = self.get_prior_rhs_group()

        fraction = TexMobject(
            "{(0.045)", "(0.97)", "\\over", 
            "(0.995)", "(0.3)", "+", "(0.045)", "(0.97)}"
        )
        products = [
            VGroup(*[
                fraction.get_parts_by_tex(tex)[i]
                for tex in tex_list
            ])
            for i, tex_list in [
                (0, ["0.045", "0.97"]),
                (0, ["0.995", "0.3"]),
                (1, ["0.045", "0.97"]),
            ]
        ]
        for i in 0, 2:
            products[i].set_color(prior_rects[0].get_color())
        products[1].set_color(prior_rects[1].get_color())
        fraction.scale(0.65)
        fraction.to_corner(UP+RIGHT, buff = MED_SMALL_BUFF)
        arrow_kwargs = {
            "color" : WHITE,
            "tip_length" : 0.15,
        }
        rhs = TexMobject("\\approx", "0.13")
        rhs.scale(0.8)
        rhs.next_to(post_tex, RIGHT)
        to_rhs_arrow = Arrow(
            fraction.get_bottom(), rhs.get_top(),
            **arrow_kwargs
        )

        pre_top_rect_products = VGroup(
            prior_rhs_group[0], self.top_conditional_rhs
        )
        pre_bottom_rect_products = VGroup(
            prior_rhs_group[1], self.bottom_conditional_rhs
        )

        self.play(Indicate(prior_rects[0], scale_factor = 1))
        self.play(*[
            ReplacementTransform(
                mob.copy(), term,
                run_time = 2,
            )
            for mob, term in zip(
                pre_top_rect_products, products[0]
            )
        ])
        self.play(Write(fraction.get_part_by_tex("over")))
        for pair in zip(pre_top_rect_products, products[0]):
            self.play(*list(map(Indicate, pair)))
            self.wait()
        self.wait()
        self.play(Indicate(prior_rects[1], scale_factor = 1))
        self.play(*[
            ReplacementTransform(
                mob.copy(), term,
                run_time = 2,
            )
            for mob, term in zip(
                pre_bottom_rect_products, products[1]
            )
        ])
        self.wait()
        for pair in zip(pre_bottom_rect_products, products[1]):
            self.play(*list(map(Indicate, pair)))
            self.wait()
        self.play(
            Write(fraction.get_part_by_tex("+")),
            ReplacementTransform(products[0].copy(), products[2])
        )
        self.wait()
        self.play(ShowCreation(to_rhs_arrow))
        self.play(Write(rhs))
        self.wait(3)


    ######

    def get_prior_labels(self, value):
        p_str = "%0.3f"%value
        q_str = "%0.3f"%(1-value)
        labels = [
            TexMobject(
                "P(", s, self.double_heart_template, ")",
                "= ", num
            )
            for s, num in (("", p_str), ("\\text{not }", q_str))
        ]
        for label in labels:
            label.scale(0.7)
            self.insert_double_heart(label)

        return labels

    def get_prior_rhs_group(self):
        labels = self.sample_space.horizontal_parts.labels
        return VGroup(*[label[-1] for label in labels])

    def get_conditional_label(self, value, given_flush = True):
        label = TexMobject(
            "P(", self.cash_string, "|", 
            "" if given_flush else "\\text{not }",
            self.double_heart_template, ")",
            "=", str(value)
        )
        self.insert_double_heart(label)
        label.set_color_by_tex(self.cash_string, GREEN)
        label.scale(0.7)
        return label

    def insert_double_heart(self, tex_mob):
        double_heart = SuitSymbol("hearts")
        double_heart.add(SuitSymbol("hearts"))
        double_heart.arrange(RIGHT, buff = SMALL_BUFF)
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
        given_flush = (sub_sample_space_index == 0)
        label = self.get_conditional_label(value, given_flush)
        return SampleSpaceScene.get_conditional_change_anims(
            self, sub_sample_space_index, value, post_rects,
            new_label_kwargs = {"labels" : [label]},
        )

class BayesRuleInMemory(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        bubble = ThoughtBubble(height = 4)
        bubble.pin_to(randy)
        B = "\\text{Belief}"
        D = "\\text{Data}"
        rule = TexMobject(
            "P(", B, "|", D, ")", "=", 
            "P(", "B", ")", 
            "{P(", D, "|", B, ")", "\\over", "P(", D, ")}"
        )
        rule.set_color_by_tex(B, RED)
        rule.set_color_by_tex(D, GREEN)
        rule.next_to(randy, RIGHT, LARGE_BUFF, UP)
        rule.generate_target()
        bubble.add_content(rule.target)
        screen_rect = ScreenRectangle()
        screen_rect.next_to(randy, UP+RIGHT)

        self.add(randy)
        self.play(
            LaggedStartMap(FadeIn, rule),
            randy.change, "erm", rule
        )
        self.play(Blink(randy))
        self.play(
            ShowCreation(bubble),
            MoveToTarget(rule),
            randy.change, "pondering",
        )
        self.wait()
        self.play(rule.fade, 0.7, run_time = 2)
        self.play(randy.change, "confused", rule)
        self.play(Blink(randy))
        self.wait(2)
        self.play(
            FadeOut(VGroup(bubble, rule)),
            randy.change, "pondering", screen_rect,
        )
        self.play(
            randy.look_at, screen_rect.get_right(),
            ShowCreation(screen_rect),
        )
        self.wait(4)

class NextVideoWrapper(TeacherStudentsScene):
    CONFIG = {
        "title" : "Upcoming chapter: Bayesian networks"
    }
    def construct(self):
        title = TextMobject(self.title)
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
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = screen
        )
        self.play(Animation(screen))
        self.wait(5)

class BayesianNetworkPreview(Scene):
    def construct(self):
        self.add_network()
        self.show_propogation(self.network.nodes[0])
        self.show_propogation(self.network.nodes[-1])

    def add_network(self):
        radius = MED_SMALL_BUFF
        node = Circle(color = WHITE, radius = radius)
        node.shift(2*DOWN)
        nodes = VGroup(*[
            node.copy().shift(x*RIGHT + y*UP)
            for x, y in [
                (-1, 0),  
                (1, 0),
                (-2, 2),
                (0, 2),
                (2, 2),
                (-2, 4),
                (0, 4),
            ]
        ])
        for node in nodes:
            node.children = VGroup()
            node.parents = VGroup()
            node.outgoing_edges = VGroup()
        edge_index_pairs = [
            (2, 0),
            (3, 0),
            (3, 1),
            (4, 1),
            (5, 2),
            (6, 3),
        ]
        edges = VGroup()
        for i1, i2 in edge_index_pairs:
            n1, n2 = nodes[i1], nodes[i2]
            edge = Arrow(
                n1.get_center(), 
                n2.get_center(),
                buff = radius,
                color = WHITE,
            )
            n1.outgoing_edges.add(edge)
            edges.add(edge)
            n1.children.add(n2)
            n2.parents.add(n1)

        network = VGroup(nodes, edges)
        network.nodes = nodes
        network.edges = edges
        self.add(network)
        self.network = network

    def show_propogation(self, node):
        self.set_network_fills()
        all_ghosts = VGroup()
        curr_nodes = [node]
        covered_nodes = set()
        self.play(GrowFromCenter(node.fill))
        self.remove(node.fill)
        while curr_nodes:
            next_nodes = set([])
            anims = []
            for node in curr_nodes:
                node.ghost = node.fill.copy().fade()
                self.add(node.ghost)
                all_ghosts.add(node.ghost)
                connected_nodes = [n for n in it.chain(node.children, node.parents) if n not in covered_nodes]
                for next_node in connected_nodes:
                    if next_node in covered_nodes:
                        continue
                    next_nodes.add(next_node)
                    anims.append(Transform(
                        node.fill.copy(), next_node.fill,
                        remover = True
                    ))
                if len(connected_nodes) == 0:
                    anims.append(FadeOut(node.fill))
            if anims:
                self.play(*anims)
            covered_nodes.update(curr_nodes)
            curr_nodes = list(next_nodes)
        self.wait()
        self.play(FadeOut(all_ghosts))


    def set_network_fills(self):
        for node in self.network.nodes:
            node.fill = self.get_fill(node)


    def get_fill(self, node):
        fill = node.copy()
        fill.set_fill(YELLOW, 1)
        fill.set_stroke(width = 0)
        return fill

class GeneralizeBayesRule(SampleSpaceScene):
    def construct(self):
        self.add_sample_space()
        self.add_title()
        self.add_posterior_rectangles()
        self.add_bayes_rule()
        self.talk_through_terms()
        self.name_likelihood()
        self.dont_memorize()
        self.show_space_restriction()

    def add_sample_space(self):
        sample_space = SampleSpace(
            full_space_config = {
                "height" : 3,
                "width" : 3,
                "fill_opacity" : 0
            }
        )
        sample_space.divide_horizontally(0.4)
        sample_space.horizontal_parts.set_fill(opacity = 0)
        labels = [
            TexMobject("P(", "B", ")"),
            TexMobject("P(\\text{not }", "B", ")"),
        ]
        for label in labels:
            label.scale(0.7)
            self.color_label(label)
        sample_space.get_side_braces_and_labels(labels)
        sample_space.add_braces_and_labels()

        parts = sample_space.horizontal_parts
        values = [0.8, 0.4]
        given_strs = ["", "\\text{not }"]
        color_pairs = [(GREEN, BLUE), (GREEN_E, BLUE_E)]
        vects = [UP, DOWN]
        for tup in zip(parts, values, given_strs, color_pairs, vects):
            part, value, given_str, colors, vect = tup
            part.divide_vertically(value, colors = colors)
            part.vertical_parts.set_fill(opacity = 0.8)
            label = TexMobject(
                "P(", "I", "|", given_str, "B", ")"
            )
            label.scale(0.7)
            self.color_label(label)
            part.get_subdivision_braces_and_labels(
                part.vertical_parts, [label], vect
            )
            sample_space.add(
                part.vertical_parts.braces,
                part.vertical_parts.labels,
            )
        sample_space.to_edge(LEFT)

        self.add(sample_space)
        self.sample_space = sample_space

    def add_title(self):
        title = TextMobject(
            "Updating", "Beliefs", "from new", "Information"
        )
        self.color_label(title)
        title.scale(0.8)
        title.to_corner(UP+LEFT)

        self.add(title)

    def add_posterior_rectangles(self):
        prior_rects = self.get_prior_rectangles()
        post_rects = self.get_posterior_rectangles()

        label = TexMobject("P(", "B", "|", "I", ")")
        label.scale(0.7)
        self.color_label(label)
        braces, labels = self.get_posterior_rectangle_braces_and_labels(
            post_rects, [label]
        )

        self.play(ReplacementTransform(
            prior_rects.copy(), post_rects,
            run_time = 2
        ))
        self.play(
            GrowFromCenter(braces),
            Write(label)
        )

        self.post_rects = post_rects
        self.posterior_tex = label

    def add_bayes_rule(self):
        rule = TexMobject(
             "=", "{P(", "B", ")", "P(", "I", "|", "B", ")",
            "\\over", "P(", "I", ")}",
        )
        self.color_label(rule)
        rule.scale(0.7)
        rule.next_to(self.posterior_tex, RIGHT)

        bayes_rule_words = TextMobject("Bayes' rule")
        bayes_rule_words.next_to(VGroup(*rule[1:]), UP, LARGE_BUFF)
        bayes_rule_words.shift_onto_screen()

        self.play(FadeIn(rule))
        self.play(Write(bayes_rule_words))
        self.wait(2)

        self.bayes_rule_words = bayes_rule_words
        self.bayes_rule = rule

    def talk_through_terms(self):
        prior = self.sample_space.horizontal_parts.labels[0]
        posterior = self.posterior_tex
        prior_target = VGroup(*self.bayes_rule[1:4])
        likelihood = VGroup(*self.bayes_rule[4:9])
        P_I = VGroup(*self.bayes_rule[-3:])

        prior_word = TextMobject("Prior")
        posterior_word = TextMobject("Posterior")
        words = [prior_word, posterior_word]
        for word in words:
            word.set_color(YELLOW)
            word.scale(0.7)
        prior_rect = SurroundingRectangle(prior)
        posterior_rect = SurroundingRectangle(posterior)
        for rect in prior_rect, posterior_rect:
            rect.set_stroke(YELLOW, 2)

        prior_word.next_to(prior, UP, LARGE_BUFF)
        posterior_word.next_to(posterior, DOWN, LARGE_BUFF)
        for word in words:
            word.shift_onto_screen()
        prior_arrow = Arrow(
            prior_word.get_bottom(), prior.get_top(),
            tip_length = 0.15
        )
        posterior_arrow = Arrow(
            posterior_word.get_top(), posterior.get_bottom(),
            tip_length = 0.15
        )

        self.play(
            Write(prior_word), 
            ShowCreation(prior_arrow), 
            ShowCreation(prior_rect),
        ) 
        self.wait()
        self.play(Transform(
            prior.copy(), prior_target,
            run_time = 2,
            path_arc = -np.pi/3,
            remover = True,
        ))
        self.wait()
        parts = self.sample_space[0].vertical_parts
        self.play(
            Indicate(likelihood),
            Indicate(parts.labels),
            Indicate(parts.braces),
        )
        self.wait()
        self.play(Indicate(P_I))
        self.play(FocusOn(self.sample_space[0][0]))
        for i in range(2):
            self.play(Indicate(
                self.sample_space[i][0], 
                scale_factor = 1
            ))
        self.wait()
        self.play(
            Write(posterior_word), 
            ShowCreation(posterior_arrow), 
            ShowCreation(posterior_rect),
        )

        self.prior_label = VGroup(prior_word, prior_arrow, prior_rect)
        self.posterior_label = VGroup(posterior_word, posterior_arrow, posterior_rect)
        self.likelihood = likelihood

    def name_likelihood(self):
        likelihoods = [
            self.sample_space[0].vertical_parts.labels[0],
            self.likelihood
        ]
        rects = [
            SurroundingRectangle(mob, buff = SMALL_BUFF)
            for mob in likelihoods
        ]
        name = TextMobject("Likelihood")
        name.scale(0.7)
        name.next_to(self.posterior_tex, UP, 1.5*LARGE_BUFF)
        arrows = [
            Arrow(
                name, rect.get_edge_center(vect), 
                tip_length = 0.15
            )
            for rect, vect in zip(rects, [RIGHT, UP])
        ]
        VGroup(name, *arrows+rects).set_color(YELLOW)

        morty = Mortimer()
        morty.scale(0.5)
        morty.next_to(rects[1], UP, buff = 0)
        morty.shift(SMALL_BUFF*RIGHT)

        self.play(
            self.bayes_rule_words.to_edge, UP,
            Write(name),
            *list(map(ShowCreation, arrows+rects))
        )
        self.wait()

        self.play(FadeIn(morty))
        self.play(morty.change, "confused", name)
        self.play(Blink(morty))
        self.play(morty.look, DOWN)
        self.wait()
        self.play(morty.look_at, name)
        self.play(Blink(morty))
        self.play(morty.change, "shruggie")

        self.play(FadeOut(VGroup(name, *arrows+rects)))
        self.play(FadeOut(morty))
        self.play(FadeOut(self.posterior_label))
        self.play(FadeOut(self.prior_label))

    def dont_memorize(self):
        rule = VGroup(*self.bayes_rule[1:])
        word = TextMobject("Memorize")
        word.scale(0.7)
        word.next_to(rule, DOWN)
        cross = VGroup(
            Line(UP+LEFT, DOWN+RIGHT),
            Line(UP+RIGHT, DOWN+LEFT),
        )
        cross.set_stroke(RED, 6)
        cross.replace(word, stretch = True)

        self.play(Write(word))
        self.wait()
        self.play(ShowCreation(cross))
        self.wait()
        self.play(FadeOut(VGroup(cross, word)))
        self.play(FadeOut(self.bayes_rule))
        self.play(
            FadeOut(self.post_rects),
            FadeOut(self.post_rects.braces),
            FadeOut(self.post_rects.labels),
        )

    def show_space_restriction(self):
        prior_rects = self.get_prior_rectangles()
        non_I_rects = VGroup(*[
            self.sample_space[i][1]
            for i in range(2)
        ])
        post_rects = self.post_rects

        self.play(non_I_rects.fade, 0.8)
        self.play(LaggedStartMap(
            ApplyMethod,
            prior_rects,
            lambda m : (m.set_color, YELLOW),
            rate_func = there_and_back,
            lag_ratio = 0.7
        ))
        self.wait(2)
        self.play(ReplacementTransform(
            prior_rects.copy(), post_rects,
            run_time = 2
        ))
        self.play(*list(map(FadeIn, [
            post_rects.braces, post_rects.labels
        ])))
        self.wait()
        self.play(*self.get_conditional_change_anims(1, 0.2, post_rects))
        self.play(*self.get_conditional_change_anims(0, 0.6, post_rects))
        self.wait()
        self.play(*it.chain(
            self.get_division_change_animations(
                self.sample_space, 
                self.sample_space.horizontal_parts,
                0.1
            ),
            self.get_posterior_rectangle_change_anims(post_rects)
        ))
        self.wait(3)


    ####

    def color_label(self, label):
        label.set_color_by_tex("B", RED)
        label.set_color_by_tex("I", GREEN)

class MoreExamples(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("More examples!", target_mode = "hooray")
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)

class MusicExample(SampleSpaceScene, PiCreatureScene):
    def construct(self):
        self.introduce_musician()
        self.add_prior()
        self.record_track()
        self.add_bottom_conditionl()
        self.friend_gives_compliment()
        self.friends_dont_like()
        self.false_compliment()
        self.add_top_conditionl()
        self.get_positive_review()
        self.restrict_space()
        self.show_posterior_rectangles()
        self.show_prior_rectangle_areas()
        self.show_posterior_probability()
        self.intuition_of_positive_feedback()
        self.make_friends_honest()
        self.fade_out_post_rect()
        self.get_negative_feedback()
        self.compare_prior_to_post_given_negative()
        self.intuition_of_negative_feedback()

    def introduce_musician(self):
        randy = self.pi_creature
        randy.change_mode("soulful_musician")
        randy.arms = randy.get_arm_copies()
        guitar = randy.guitar = Guitar()
        guitar.move_to(randy)
        guitar.shift(0.31*RIGHT + 0.6*UP)

        randy.change_mode("plain")
        self.play(
            randy.change_mode, "soulful_musician",
            path_arc = np.pi/6,
        )
        self.play(
            Animation(randy),
            DrawBorderThenFill(guitar),
            Animation(randy.arms)
        )
        randy.add(guitar, randy.arms)
        self.wait()
        self.play_notes(guitar)
        self.change_pi_creature_with_guitar("concerned_musician")
        self.wait(2)
        self.play(
            randy.scale, 0.7,
            randy.to_corner, UP+LEFT,
        )
        self.play_notes(guitar)

    def add_prior(self):
        sample_space = SampleSpace()
        sample_space.shift(DOWN)
        sample_space.divide_horizontally(0.8, colors = [MAROON_D, BLUE_E])
        labels = VGroup(
            TexMobject("P(S) = ", "0.8"),
            TexMobject("P(\\text{not } S) = ", "0.2"),
        )
        labels.scale(0.7)
        braces, labels = sample_space.get_side_braces_and_labels(labels)
        VGroup(sample_space, braces, labels).to_edge(LEFT)
        words = list(map(TextMobject, [
            "Blunt honesty", "Some confidence"
        ]))
        for word, part in zip(words, sample_space.horizontal_parts):
            word.scale(0.6)
            word.move_to(part)

        self.play(LaggedStartMap(FadeIn, sample_space, run_time = 1))
        self.play(*list(map(GrowFromCenter, braces)))
        for label in labels:
            self.play(Write(label, run_time = 2))
            self.wait()
        for word, mode in zip(words, ["maybe", "soulful_musician"]):
            self.play(LaggedStartMap(FadeIn, word, run_time = 1))
            self.change_pi_creature_with_guitar(mode)
            self.wait()
        self.wait()
        self.play(*list(map(FadeOut, words)))

        self.sample_space = sample_space

    def record_track(self):
        randy = self.pi_creature
        friends = VGroup(*[
            PiCreature(mode = "happy", color = color).flip()
            for color in (BLUE_B, GREY_BROWN, MAROON_E)
        ])
        friends.scale(0.6)
        friends.arrange(RIGHT)
        friends.next_to(randy, RIGHT, LARGE_BUFF, DOWN)
        friends.to_edge(RIGHT)
        for friend in friends:
            friend.look_at(randy.eyes)

        headphones = VGroup(*list(map(Headphones, friends)))

        self.play(FadeIn(friends))
        self.pi_creatures.add(*friends)
        self.play(
            FadeIn(headphones), 
            Animation(friends)
        )
        self.play_notes(randy.guitar)
        self.play(LaggedStartMap(
            ApplyMethod, friends,
            lambda pi : (pi.change, "hooray"),
            run_time = 2,
        ))

        self.friends = friends
        self.headphones = headphones

    def add_bottom_conditionl(self):
        p = 0.99
        bottom_part = self.sample_space[1]
        bottom_part.divide_vertically(p, colors = [GREEN_E, YELLOW])
        label = self.get_conditional_label(p, False)
        braces, labels = bottom_part.get_bottom_braces_and_labels([label])
        brace = braces[0]

        self.play(FadeIn(bottom_part.vertical_parts))
        self.play(GrowFromCenter(brace))
        self.play(Write(label))
        self.wait()

    def friend_gives_compliment(self):
        friends = self.friends
        bubble = SpeechBubble(
            height = 1.25, width = 3, direction = RIGHT,
            fill_opacity = 0,
        )
        content = TextMobject("Phenomenal!")
        content.scale(0.75)
        bubble.add_content(content)
        VGroup(bubble, content).next_to(friends, LEFT, SMALL_BUFF)
        VGroup(bubble, content).to_edge(UP, SMALL_BUFF)
    
        self.play(LaggedStartMap(
            ApplyMethod, friends,
            lambda pi : (pi.change_mode, "conniving")
        ))
        self.wait()
        self.play(
            ShowCreation(bubble),
            Write(bubble.content, run_time = 1),
            ApplyMethod(friends[0].change_mode, "hooray"),
            LaggedStartMap(
                ApplyMethod, VGroup(*friends[1:]),
                lambda pi : (pi.change_mode, "happy")
            ),
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [bubble, content])))

    def friends_dont_like(self):
        friends = self.friends
        pi1, pi2, pi3 = friends
        for friend in friends:
            friend.generate_target()
        pi1.target.change("guilty", pi2.eyes)
        pi2.target.change("hesitant", pi1.eyes)
        pi3.target.change("pondering", pi2.eyes)

        self.play(LaggedStartMap(
            MoveToTarget, friends
        ))
        self.change_pi_creature_with_guitar("concerned_musician")
        self.wait()

    def false_compliment(self):
        friend = self.friends[0]
        bubble = SpeechBubble(
            height = 1.25, width = 4.5, direction = RIGHT,
            fill_opacity = 0,
        )
        content = TextMobject("The beat was consistent.")
        content.scale(0.75)
        bubble.add_content(content)
        VGroup(bubble, content).next_to(friend, LEFT, SMALL_BUFF)
        VGroup(bubble, content).to_edge(UP, SMALL_BUFF)

        self.play(
            friend.change_mode, "maybe",
            ShowCreation(bubble),
            Write(content)
        )
        self.change_pi_creature_with_guitar("happy")
        self.wait()
        self.play(*list(map(FadeOut, [bubble, content])))

        self.bubble = bubble

    def add_top_conditionl(self):
        p = 0.9
        top_part = self.sample_space[0]
        top_part.divide_vertically(p, colors = [TEAL_E, RED_E])
        label = self.get_conditional_label(p, True)
        braces, labels = top_part.get_top_braces_and_labels([label])
        brace = braces[0]

        self.play(FadeIn(top_part.vertical_parts))
        self.play(GrowFromCenter(brace))
        self.play(Write(label, run_time = 2))
        self.wait()

    def get_positive_review(self):
        friends = self.friends

        self.change_pi_creature_with_guitar(
            "soulful_musician",
            LaggedStartMap(
                ApplyMethod, friends, 
                lambda pi : (pi.change, "happy"),
                run_time = 1,
            )
        )
        self.play_notes(self.pi_creature.guitar)

    def restrict_space(self):
        positive_space, negative_space = [
            VGroup(*[
                self.sample_space[i][j]
                for i in range(2)
            ])
            for j in range(2)
        ]
        negative_space.save_state()

        self.play(negative_space.fade, 0.8)
        self.play(LaggedStartMap(
            ApplyMethod, positive_space,
            lambda m : (m.set_color, YELLOW),
            rate_func = there_and_back,
            run_time = 2,
            lag_ratio = 0.7,
        ))
        self.wait()

        self.negative_space = negative_space

    def show_posterior_rectangles(self):
        prior_rects = self.get_prior_rectangles()
        post_rects = self.get_posterior_rectangles()
        label = TexMobject("P(S | ", "\\checkmark", ")")
        label.scale(0.7)
        label.set_color_by_tex("\\checkmark", GREEN)
        braces, labels = self.get_posterior_rectangle_braces_and_labels(
            post_rects, [label]
        )
        brace = braces[0]

        self.play(ReplacementTransform(
            prior_rects.copy(), post_rects,
            run_time = 2
        ))
        self.play(GrowFromCenter(brace))
        self.play(Write(label))
        self.wait()

        self.post_rects = post_rects
        self.post_tex = label

    def show_prior_rectangle_areas(self):
        prior_rects = self.get_prior_rectangles()
        products = VGroup(
            TexMobject("(", "0.8", ")(", "0.9", ")"),
            TexMobject("(", "0.2", ")(", "0.99", ")"),
        )
        top_product, bottom_product = products
        for product, rect in zip(products, prior_rects):
            product.scale(0.7)
            product.move_to(rect)
        side_labels = self.sample_space.horizontal_parts.labels
        top_labels = self.sample_space[0].vertical_parts.labels
        bottom_labels = self.sample_space[1].vertical_parts.labels

        self.play(
            ReplacementTransform(
                side_labels[0][-1].copy(),
                top_product[1],
            ),
            ReplacementTransform(
                top_labels[0][-1].copy(),
                top_product[3],
            ),
            Write(VGroup(*top_product[::2]))
        )
        self.wait(2)
        self.play(
            ReplacementTransform(
                side_labels[1][-1].copy(),
                bottom_product[1],
            ),
            ReplacementTransform(
                bottom_labels[0][-1].copy(),
                bottom_product[3],
            ),
            Write(VGroup(*bottom_product[::2]))
        )
        self.wait(2)

        self.products = products

    def show_posterior_probability(self):
        post_tex = self.post_tex
        rhs = TexMobject("\\approx", "0.78")
        rhs.scale(0.7)
        rhs.next_to(post_tex, RIGHT)
        ratio = TexMobject(
            "{(0.8)(0.9)", "\\over", 
            "(0.8)(0.9)", "+", "(0.2)(0.99)}"
        )
        ratio.scale(0.6)
        ratio.next_to(VGroup(post_tex, rhs), DOWN, LARGE_BUFF)
        ratio.to_edge(RIGHT)
        arrow_kwargs = {
            "tip_length" : 0.15, 
            "color" : WHITE,
            "buff" : 2*SMALL_BUFF,
        }
        to_ratio_arrow = Arrow(
            post_tex.get_bottom(), ratio.get_top(), **arrow_kwargs
        )
        to_rhs_arrow = Arrow(
            ratio.get_top(), rhs[1].get_bottom(), **arrow_kwargs
        )

        prior_rects = self.get_prior_rectangles()

        self.play(
            ShowCreation(to_ratio_arrow),
            FadeIn(ratio)
        )
        self.wait(2)
        for mob in prior_rects, prior_rects[0]:
            self.play(
                mob.set_color, YELLOW,
                Animation(self.products),
                rate_func = there_and_back,
                run_time = 2
            )
            self.wait()
        self.wait()
        self.play(ShowCreation(to_rhs_arrow))
        self.play(Write(rhs, run_time = 1))
        self.wait(2)

        self.post_rhs = rhs
        self.ratio_group = VGroup(ratio, to_ratio_arrow, to_rhs_arrow)

    def intuition_of_positive_feedback(self):
        friends = self.friends
        prior_num = self.sample_space.horizontal_parts.labels[0][-1]
        prior_num_ghost = prior_num.copy().set_fill(opacity = 0.5)
        post_num = self.post_rhs[-1]
        prior_rect = SurroundingRectangle(prior_num)
        post_rect = SurroundingRectangle(post_num)

        self.play(ShowCreation(prior_rect))
        self.play(Transform(
            prior_num_ghost, post_num,
            remover = True,
            path_arc = -np.pi/6,
            run_time = 2,
        ))
        self.play(ShowCreation(post_rect))
        self.wait(2)
        for mode, time in ("shruggie", 2), ("hesitant", 0):
            self.play(LaggedStartMap(
                ApplyMethod, friends,
                lambda pi : (pi.change, mode),
                run_time = 2,
            ))
            self.wait(time)
        self.play(*list(map(FadeOut, [
            prior_rect, post_rect,
            self.ratio_group, self.post_rhs
        ])))

        self.prior_num_rect = prior_rect

    def make_friends_honest(self):
        post_rects = self.post_rects

        self.play(FadeOut(self.products))
        for value in 0.5, 0.1, 0.9:
            label = self.get_conditional_label(value)
            self.play(*self.get_top_conditional_change_anims(
                value, post_rects, 
                new_label_kwargs = {"labels" : [label]},
            ), run_time = 2)
            self.wait(2)

    def fade_out_post_rect(self):
        self.play(*list(map(FadeOut, [
            self.post_rects, 
            self.post_rects.braces, 
            self.post_rects.labels, 
        ])))
        self.play(self.negative_space.restore)

    def get_negative_feedback(self):
        friends = self.friends
        old_prior_rects = self.get_prior_rectangles()
        for part in self.sample_space.horizontal_parts:
            part.vertical_parts.submobjects.reverse()
        new_prior_rects = self.get_prior_rectangles()
        post_rects = self.get_posterior_rectangles()
        label = TexMobject(
            "P(S | \\text{not } ", "\\checkmark", ")",
            "\\approx", "0.98"
        )
        label.scale(0.7)
        label.set_color_by_tex("\\checkmark", GREEN)
        braces, labels = self.get_posterior_rectangle_braces_and_labels(
            post_rects, [label]
        )
        brace = braces[0]

        self.play(old_prior_rects.fade, 0.8)
        self.play(LaggedStartMap(
            ApplyMethod, friends,
            lambda pi : (pi.change, "pondering", post_rects),
            run_time = 1
        ))
        self.wait()
        self.play(ReplacementTransform(
            new_prior_rects.copy(), post_rects,
            run_time = 2            
        ))
        self.play(GrowFromCenter(brace))
        self.wait(2)
        self.play(Write(label))
        self.wait(3)

        self.post_rects = post_rects

    def compare_prior_to_post_given_negative(self):
        post_num = self.post_rects.labels[0][-1]
        post_num_rect = SurroundingRectangle(post_num)

        self.play(ShowCreation(self.prior_num_rect))
        self.wait()
        self.play(ShowCreation(post_num_rect))
        self.wait()

        self.post_num_rect = post_num_rect

    def intuition_of_negative_feedback(self):
        friends = self.friends
        randy = self.pi_creature
        bubble = self.bubble

        modes = ["sassy", "pleading", "horrified"]
        for friend, mode in zip(friends, modes):
            friend.generate_target()
            friend.target.change(mode, randy.eyes)
        content = TextMobject("Horrible.  Just horrible.")
        content.scale(0.6)
        bubble.add_content(content)

        self.play(*list(map(MoveToTarget, friends)))
        self.play(
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.change_pi_creature_with_guitar("sad")
        self.wait()
        self.change_pi_creature_with_guitar("concerned_musician")
        self.wait(3)

    ######

    def create_pi_creature(self):
        randy = Randolph()
        randy.left_arm_range = [.36, .45]
        self.randy = randy
        return randy

    def get_conditional_label(self, value, given_suck = True):
        positive_str = "\\checkmark"
        label = TexMobject(
            "P(", positive_str, "|", 
            "" if given_suck else "\\text{not }",
            "S", ")",
            "=", str(value)
        )
        label.set_color_by_tex(positive_str, GREEN)
        label.scale(0.7)
        return label

    def change_pi_creature_with_guitar(self, target_mode, *added_anims):
        randy = self.pi_creature
        randy.remove(randy.arms, randy.guitar)
        target = randy.copy()
        target.change_mode(target_mode)
        target.arms = target.get_arm_copies()
        target.guitar = randy.guitar.copy()
        for pi in randy, target:
            pi.add(pi.guitar, pi.arms)
        self.play(Transform(randy, target), *added_anims)

    def play_notes(self, guitar):
        note = SVGMobject(file_name = "8th_note")
        note.set_height(0.5)
        note.set_stroke(width = 0)
        note.set_fill(BLUE, 1)
        note.move_to(guitar)
        note.shift(MED_SMALL_BUFF*(DOWN+2*LEFT))
        notes = VGroup(*[note.copy() for x in range(10)])
        sine_wave = FunctionGraph(np.sin, x_min = -5, x_max = 5)
        sine_wave.scale(0.75)
        sine_wave.rotate(np.pi/6, about_point = ORIGIN)
        sine_wave.shift(
            notes.get_center() - \
            sine_wave.point_from_proportion(0)
        )
        self.play(LaggedStartMap(
            MoveAlongPath, notes, 
            lambda n : (n, sine_wave),
            path_arc = np.pi/2,
            run_time = 4,
            lag_ratio = 0.5,
            rate_func = lambda t : t,
        ))

class FinalWordsOnRule(SampleSpaceScene):
    def construct(self):
        self.add_sample_space()
        self.add_uses()
        self.tweak_values()

    def add_sample_space(self):
        sample_space = self.sample_space = SampleSpace()
        prior = 0.2
        top_conditional = 0.8
        bottom_condional = 0.3
        sample_space.divide_horizontally(prior)
        sample_space[0].divide_vertically(
            top_conditional, colors = [GREEN, RED]
        )
        sample_space[1].divide_vertically(
            bottom_condional, colors = [GREEN_E, RED_E]
        )
        B = "\\text{Belief}"
        D = "\\text{Data}"
        P_B = TexMobject("P(", B, ")")
        P_D_given_B = TexMobject("P(", D, "|", B, ")")
        P_D_given_not_B = TexMobject(
            "P(", D, "|", "\\text{not }", B, ")"
        )
        P_B_given_D = TexMobject("P(", B, "|", D, ")")
        labels = VGroup(P_B, P_D_given_B, P_D_given_not_B, P_B_given_D)
        for label in labels:
            label.scale(0.7)
            label.set_color_by_tex(B, BLUE)
            label.set_color_by_tex(D, GREEN)

        prior_rects = self.get_prior_rectangles()
        post_rects = self.get_posterior_rectangles()
        for i in range(2):
            sample_space[i][1].fade(0.7)

        braces = VGroup()
        bs, ls = sample_space.get_side_braces_and_labels([P_B])
        braces.add(*bs)
        bs, ls = sample_space[0].get_top_braces_and_labels([P_D_given_B])
        braces.add(*bs)
        bs, ls = sample_space[1].get_bottom_braces_and_labels([P_D_given_not_B])
        braces.add(*bs)
        bs, ls = self.get_posterior_rectangle_braces_and_labels(
            post_rects, [P_B_given_D]
        )
        braces.add(*bs)

        group = VGroup(sample_space, braces, labels, post_rects)
        group.to_corner(DOWN + LEFT)
        self.add(group)

        self.post_rects = post_rects

    def add_uses(self):
        uses = TextMobject(
            "Machine learning, ", 
            "scientific inference, $\\dots$",
        )
        uses.to_edge(UP)
        for use in uses:
            self.play(Write(use, run_time = 2))
        self.wait()

    def tweak_values(self):
        post_rects = self.post_rects
        new_value_lists = [
            (0.85, 0.1, 0.11),
            (0.3, 0.9, 0.4),
            (0.97, 0.3, 1./22),
        ]
        for new_values in new_value_lists:
            for i, value in zip(list(range(2)), new_values):
                self.play(*self.get_conditional_change_anims(
                    i, value, post_rects
                ))
                self.wait()
            self.play(*it.chain(
                self.get_horizontal_division_change_animations(new_values[-1]),
                self.get_posterior_rectangle_change_anims(post_rects)
            ))
            self.wait()
        self.wait(2)

class FootnoteWrapper(NextVideoWrapper):
    CONFIG = {
        "title" : "Thoughts on the classic Bayes example"
    }

class PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
            "Mark Zollo",
            "James Park",
            "Erik Sundell",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Karan Bhargava",
            "Ankit Agarwal",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Markus Persson",
            "Yoni Nazarathy",
            "Ed Kellett",
            "Joseph John Cox",
            "Dan Buchoff",
            "Luc Ritchie",
            "Michael McGuffin",
            "John Haley",
            "Mourits de Beer",
            "Ankalagon",
            "Eric Lavault",
            "Tomohiro Furusawa",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Ryan Dahl",
            "Mark Govea",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Nils Schneider",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }

class Thumbnail(SampleSpaceScene):
    def construct(self):
        title = TextMobject("Bayes' rule")
        title.scale(2)
        title.to_edge(UP)
        self.add(title)

        prior_label = TexMobject("P(", "H", ")")
        post_label = TexMobject("P(", "H", "|", "D", ")")
        for label in prior_label, post_label:
            label.set_color_by_tex("H", YELLOW)
            label.set_color_by_tex("D", GREEN)
            label.scale(1.5)

        sample_space = self.get_sample_space()
        sample_space.set_height(4.5)
        sample_space.divide_horizontally(0.3)
        sample_space[0].divide_vertically(0.8, colors = [GREEN, BLUE])
        sample_space[1].divide_vertically(0.3, colors = [GREEN_E, BLUE_E])
        sample_space.get_side_braces_and_labels([prior_label])
        sample_space.add_braces_and_labels()
        post_rects = self.get_posterior_rectangles()
        group = self.get_posterior_rectangle_braces_and_labels(
            post_rects, [post_label]
        )
        post_rects.add(group)

        VGroup(sample_space, post_rects).next_to(title, DOWN, LARGE_BUFF)
        self.add(sample_space, post_rects)













