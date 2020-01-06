from manimlib.imports import *

from active_projects.eop.bayes import IntroducePokerHand

SICKLY_GREEN = "#9BBD37"


class BayesClassicExampleOpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "When faced with a difficult question, we often " \
            "answer an easier one instead, usually without " \
            "noticing the substitution.",
        ],
        "author" : "Daniel Kahneman",
    }

class Introduction(TeacherStudentsScene):
    def construct(self):
        self.hold_up_example()
        self.write_counter_intuitive()
        self.comment_on_crazy_results()
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
            randy.set_color, SICKLY_GREEN
        )
        self.play(ShowCreation(rect))
        self.play(
            FadeIn(everyone),
            example.scale, 0.5,
            example.next_to, self.teacher.get_corner(UP+LEFT), UP,
        )
        self.wait(2)

        self.example = example

    def write_counter_intuitive(self):
        bayes = TextMobject("Bayes")
        arrow = TexMobject("\\leftrightarrow")
        intuition = TextMobject("Intuition")

        group = VGroup(bayes, arrow, intuition)
        group.arrange(RIGHT, buff = SMALL_BUFF)
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

        self.play(*list(map(FadeIn, [bayes, intuition])))
        self.play(Write(arrow))
        self.play(ShowCreation(cross))
        self.change_student_modes(*["confused"]*3)
        self.wait(2)

        self.bayes_to_intuition = group

    def comment_on_crazy_results(self):
        disease_group = VGroup(self.example, self.bayes_to_intuition)
        disease_group.save_state()

        self.teacher_says(
            "Who doesn't love \\\\ crazy results?",
            target_mode = "hooray",
            added_anims = [disease_group.to_corner, UP+LEFT]
        )
        self.wait(2)

        self.disease_group = disease_group

    def put_it_first(self):
        poker_example = self.get_poker_example()
        music_example = self.get_music_example()
        disease_group = self.disease_group

        self.play(
            disease_group.restore,
            disease_group.to_edge, LEFT,
            RemovePiCreatureBubble(
                self.teacher,
                target_mode = "hesitant"
            )
        )
        self.change_student_modes(
            *["pondering"]*3, 
            look_at_arg = disease_group
        )

        poker_example.next_to(self.example, RIGHT)
        music_example.next_to(poker_example, RIGHT)
        examples = VGroup(poker_example, music_example)
        brace = Brace(examples, UP)
        bayes_to_intuition = VGroup(*list(map(TextMobject, [
            "Bayes", "$\\leftrightarrow$", "Intuition"
        ])))
        bayes_to_intuition.arrange(RIGHT, buff = SMALL_BUFF)
        bayes_to_intuition.next_to(brace, UP, SMALL_BUFF)
        check = TexMobject("\\checkmark")
        check.set_color(GREEN)
        check.next_to(bayes_to_intuition[1], UP, SMALL_BUFF)

        for example in examples:
            self.play(FadeIn(example))
            self.wait()
        self.play(GrowFromCenter(brace))
        self.play(FadeIn(bayes_to_intuition))
        self.play(Write(check))
        self.wait(2)

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
        something_else.set_color(YELLOW)
        something_else.set_height(bayes.get_height())
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
        self.wait(3)


    #####

    def get_poker_example(self):
        rect = self.get_example_rect()
        values = IntroducePokerHand.CONFIG["community_card_values"]
        community_cards = VGroup(*list(map(PlayingCard, values)))
        community_cards.arrange(RIGHT)
        deck = VGroup(*[
            PlayingCard(turned_over = True)
            for x in range(5)
        ])
        for i, card in enumerate(deck):
            card.shift(i*(0.03*RIGHT + 0.015*DOWN))
        deck.next_to(community_cards, LEFT)
        cards = VGroup(deck, community_cards)
        cards.set_width(rect.get_width() - 2*SMALL_BUFF)
        cards.next_to(rect.get_bottom(), UP, MED_SMALL_BUFF)

        probability = TexMobject(
            "P(", "\\text{Flush}", "|", "\\text{High bet}", ")"
        )
        probability.set_color_by_tex("Flush", RED)
        probability.set_color_by_tex("High bet", GREEN)
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
        musician.set_height(0.7*rect.get_height())
        musician.next_to(rect.get_bottom(), UP, SMALL_BUFF)

        probability = TexMobject(
            "P(", "\\text{Suck }", "|", "\\text{ Good review}", ")"
        )
        probability.set_color_by_tex("Suck", RED)
        probability.set_color_by_tex("Good", GREEN)
        probability.scale(0.5)
        probability.next_to(rect.get_top(), DOWN)

        return VGroup(rect, musician, probability)

    def get_example_rect(self):
        rect = self.example[0].copy()
        rect.set_color(WHITE)
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
            ]).arrange(DOWN, SMALL_BUFF)
            for x in range(40)
        ]).arrange(RIGHT, SMALL_BUFF)
        all_creatures.set_width(FRAME_WIDTH - 4)
        all_creatures.next_to(title, DOWN)
        randy = all_creatures[0][0]
        all_creatures[0].remove(randy)
        randy.change_mode("sick")
        randy.set_color(SICKLY_GREEN)
        randy.save_state()
        randy.set_height(3)
        randy.center()
        randy.change_mode("plain")
        randy.set_color(BLUE)

        self.add(randy)
        self.play(
            randy.change_mode, "sick",
            randy.set_color, SICKLY_GREEN
        )
        self.play(Blink(randy))
        self.play(randy.restore)
        self.play(
            Write(title),
            LaggedStartMap(FadeIn, all_creatures, run_time = 3)
        )
        self.wait()

class TestScene(PiCreatureScene):
    def get_result(self, creature, word, color):
        arrow = self.get_test_arrow()
        test_result = TextMobject(word)
        test_result.set_color(color)
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

    def create_pi_creature(self):
        randy = Randolph()
        randy.next_to(ORIGIN, LEFT)
        return randy

class TestDiseaseCase(TestScene):
    def construct(self):
        randy = self.pi_creature
        randy.change_mode("sick")
        randy.set_color(SICKLY_GREEN)
        result = self.get_positive_result(randy)
        accuracy = TextMobject("100\\% Accuracy")
        accuracy.next_to(VGroup(randy, result), UP)
        accuracy.to_edge(UP)

        self.add(randy)
        self.play(FadeIn(result[0]))
        self.play(Write(result[1]))
        self.play(FadeIn(accuracy))
        self.wait()

class TestNonDiseaseCase(TestScene):
    def construct(self):
        randy = self.pi_creature
        randy.change_mode("happy")
        randy.next_to(ORIGIN, LEFT)
        result = self.get_negative_result(randy)
        accuracy = TextMobject("99\\% Accuracy")
        accuracy.next_to(VGroup(randy, result), UP)
        accuracy.to_edge(UP)

        all_creatures = VGroup(*[
            VGroup(*[
                randy.copy()
                for y in range(10)
            ]).arrange(DOWN)
            for y in range(10)
        ]).arrange(RIGHT)
        all_creatures.set_height(6)
        all_creatures.to_corner(DOWN+LEFT)
        last_guy = all_creatures[-1][-1]
        rect = SurroundingRectangle(last_guy, buff = 0)
        rect.set_color(YELLOW)

        self.add(randy, accuracy)
        self.play(FadeIn(result[0]))
        self.play(Write(result[1]))
        self.play(Blink(randy))
        self.play(
            ReplacementTransform(randy, all_creatures[0][0]),
            LaggedStartMap(FadeIn, all_creatures, run_time = 2),
            FadeOut(result)
        )
        self.play(ShowCreation(rect))
        self.play(
            last_guy.set_height, 2,
            last_guy.next_to, all_creatures, RIGHT
        )
        result = self.get_positive_result(last_guy)
        false_positive = TextMobject("False positive")
        false_positive.scale(0.8)
        false_positive.next_to(result, UP, LARGE_BUFF)
        false_positive.to_edge(RIGHT)
        arrow = Arrow(
            false_positive.get_bottom(), result[1].get_top(),
            buff = SMALL_BUFF
        )
        self.play(FadeIn(result))
        self.play(
            FadeIn(false_positive),
            ShowCreation(arrow),
            last_guy.change, "confused", result,
        )
        for x in range(2):
            self.play(Blink(last_guy))
            self.wait(2)

class ReceivePositiveResults(TestScene):
    def construct(self):
        status = TextMobject("Health status: ???")
        status.to_edge(UP)

        randy = self.pi_creature
        result = self.get_positive_result(randy)
        accuracy = TextMobject("99\% Accuracy")
        accuracy.next_to(result[1], DOWN, LARGE_BUFF)
        accuracy.set_color(YELLOW)

        self.add(status, randy)
        self.play(FadeIn(result[0]))
        self.wait()
        self.play(Write(result[1]))
        self.play(randy.change, "maybe", result)
        self.wait(2)
        self.play(
            randy.change, "pleading", accuracy,
            Write(accuracy, run_time = 1)
        )
        self.wait()
        self.play(randy.change, "sad", accuracy)
        self.wait(2)

class AskAboutRephrasingQuestion(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "What if we rephrased \\\\ the question?",
            run_time = 1
        )
        self.wait(3)

class RephraseQuestion(Scene):
    def construct(self):
        words = VGroup(*list(map(TextMobject, [
            r"1 in $1{,000}$ chance \\ of having disease",
            r"1 in $100$ \\ false positive rate.",
            r"""\underline{\phantom{1 in 10}} chance \\
                of having disease \\
                after testing positive.
            """,
        ])))
        words.arrange(RIGHT, buff = LARGE_BUFF)
        words.set_width(2*(FRAME_X_RADIUS - MED_LARGE_BUFF))

        prior = TextMobject("Prior")
        prior.set_color(GREEN)
        prior.next_to(words[0], UP, 1.5*LARGE_BUFF)
        prior_arrow = Arrow(prior, words[0])
        prior_arrow.set_color(prior.get_color())

        posterior = TextMobject("Posterior")
        posterior.next_to(words[2], UP)
        posterior.shift(
            (prior.get_center() - posterior.get_center())[1]*UP
        )
        posterior.set_color(YELLOW)
        posterior_arrow = Arrow(posterior, words[2])
        posterior_arrow.set_color(posterior.get_color())

        self.add(words[0])
        self.play(
            LaggedStartMap(FadeIn, prior),
            ShowCreation(prior_arrow),
            run_time = 1
        )
        self.wait()
        self.play(FadeIn(words[1]))
        self.wait()
        self.play(FadeIn(words[2]))
        self.play(
            LaggedStartMap(FadeIn, posterior),
            ShowCreation(posterior_arrow),
            run_time = 1
        )
        self.wait(2)

class TryUnitSquareVisual(SampleSpaceScene):
    def construct(self):
        sample_space = self.get_sample_space()
        self.add_prior_division()
        self.add(sample_space)
        self.add_conditional_divisions()
        prior_label = sample_space.horizontal_parts.labels[0]
        final_labels = self.final_labels

        hard_to_see = TextMobject("Hard to see")
        hard_to_see.scale(0.7)
        hard_to_see.next_to(prior_label, UP)
        hard_to_see.to_edge(UP)
        hard_to_see.set_color(YELLOW)
        arrow = Arrow(hard_to_see, prior_label)

        self.wait()
        anims = self.get_division_change_animations(
            sample_space, sample_space.horizontal_parts,
            0.001, new_label_kwargs = {"labels" : final_labels}
        )
        self.play(*anims, run_time = 2)
        self.wait()
        self.play(
            Write(hard_to_see, run_time = 2),
            ShowCreation(arrow)
        )
        self.wait(2)

    def add_prior_division(self):
        sample_space = self.sample_space
        sample_space.divide_horizontally(0.1)
        initial_labels, final_labels = [
            VGroup(
                TexMobject("P(\\text{Disease})", s1),
                TexMobject("P(\\text{Not disease})", s2),
            ).scale(0.7)
            for s1, s2 in (("", ""), ("= 0.001", "= 0.999"))
        ]
        sample_space.get_side_braces_and_labels(initial_labels)
        sample_space.add_braces_and_labels()

        self.final_labels = final_labels

    def add_conditional_divisions(self):
        sample_space = self.sample_space
        top_part, bottom_part = sample_space.horizontal_parts

        top_brace = Brace(top_part, UP)
        top_label = TexMobject(
            "P(", "+", "|", "\\text{Disease}", ")", "=", "1"
        )
        top_label.scale(0.7)
        top_label.next_to(top_brace, UP)
        top_label.set_color_by_tex("+", GREEN)

        self.play(GrowFromCenter(top_brace))
        self.play(FadeIn(top_label))
        self.wait()

        bottom_part.divide_vertically(
            0.95, colors = [BLUE_E, YELLOW_E]
        )
        bottom_label = TexMobject(
            "P(", "+", "|", "\\text{Not disease}", ")", "=", "1"
        )
        bottom_label.scale(0.7)
        bottom_label.set_color_by_tex("+", GREEN)
        braces, labels = bottom_part.get_bottom_braces_and_labels(
            [bottom_label]
        )
        bottom_brace = braces[0]

        self.play(
            FadeIn(bottom_part.vertical_parts),
            GrowFromCenter(bottom_brace),
        )
        self.play(FadeIn(bottom_label))
        self.wait()

class ShowRestrictedSpace(Scene):
    CONFIG = {
        "n_rows" : 25,
        "n_cols" : 40,
        "n_false_positives" : 10,
        "false_positive_color" : YELLOW_E,
    }
    def construct(self):
        self.add_all_creatures()
        self.show_accurate_positive_result()
        self.show_false_positive_conditional()
        self.show_false_positive_individuals()
        self.fade_out_negative_result_individuals()
        self.show_posterior_probability()
        self.contrast_with_prior()

    def add_all_creatures(self):
        title = TextMobject("$1{,}000$ individuals")
        title.to_edge(UP)
        all_creatures = self.get_all_creatures()
        sick_one = all_creatures.sick_one
        healthy_creatures = all_creatures.healthy_creatures

        sick_one.save_state()
        sick_one_words = TextMobject("1 sick")
        sick_one_words.next_to(sick_one, RIGHT)
        sick_one_words.to_edge(RIGHT)
        sick_one_words.set_color(SICKLY_GREEN)
        sick_one_arrow = Arrow(
            sick_one_words, sick_one,
            color = SICKLY_GREEN
        )

        healthy_words = TextMobject("999 healthy")
        healthy_words.next_to(sick_one_words, UP, MED_LARGE_BUFF)
        healthy_words.shift_onto_screen()
        healthy_words.set_color(BLUE)

        self.add(title)
        self.play(LaggedStartMap(FadeIn, all_creatures))
        self.play(
            FadeIn(sick_one_words),
            ShowCreation(sick_one_arrow)
        )
        self.play(
            sick_one.set_height, 2,
            sick_one.next_to, sick_one_words, DOWN,
            sick_one.to_edge, RIGHT,
        )
        self.wait()
        self.play(sick_one.restore)
        self.play(
            Write(healthy_words),
            LaggedStartMap(
                ApplyMethod, healthy_creatures,
                lambda m : (m.shift, MED_SMALL_BUFF*UP),
                rate_func = there_and_back,
                lag_ratio = 0.2,
            )
        )
        self.wait()
        self.play(FadeOut(title))

        self.all_creatures = all_creatures
        self.healthy_creatures = healthy_creatures
        self.sick_one = sick_one
        self.sick_one_label = VGroup(sick_one_words, sick_one_arrow)
        self.healthy_ones_label = healthy_words

    def show_accurate_positive_result(self):
        equation = TexMobject(
            "P(", "\\text{Test positive }", "|", 
            "\\text{ sick}", ")", "=", "100\\%"
        )
        equation.set_color_by_tex("positive", YELLOW)
        equation.set_color_by_tex("sick", SICKLY_GREEN)
        equation.to_corner(UP+LEFT)

        self.play(Write(equation, run_time = 1))
        self.wait(2)

        self.disease_conditional = equation

    def show_false_positive_conditional(self):
        equation = TexMobject(
            "P(", "\\text{Test positive }", "|", 
            "\\text{ healthy}", ")", "=", "1\\%"
        )
        equation.set_color_by_tex("positive", YELLOW)
        equation.set_color_by_tex("healthy", BLUE)
        equation.to_corner(UP+LEFT)

        self.play(ReplacementTransform(
            self.disease_conditional, equation
        ))
        self.wait()

        self.healthy_conditional = equation

    def show_false_positive_individuals(self):
        all_creatures = self.all_creatures
        false_positives = VGroup(
            *all_creatures[-1][1:1+self.n_false_positives]
        )
        self.healthy_creatures.remove(*false_positives)
        brace = Brace(false_positives, RIGHT)
        words = TextMobject("10 False positives")
        words.scale(0.8)
        words.next_to(brace, RIGHT)

        self.play(
            GrowFromCenter(brace),
            LaggedStartMap(
                ApplyMethod, false_positives,
                lambda pi : (pi.set_color, self.false_positive_color),
                run_time = 1
            )
        )
        self.play(Write(words))
        self.wait()

        self.false_positives = false_positives
        self.false_positives_brace = brace
        self.false_positives_words = words

    def fade_out_negative_result_individuals(self):
        to_fade = VGroup(
            self.healthy_creatures,
            self.healthy_conditional,
            self.sick_one_label,
            self.healthy_ones_label,
        )
        movers = VGroup(self.sick_one, *self.false_positives)
        movers.generate_target()
        movers.target.set_width(1)
        movers.target.arrange(RIGHT)
        movers.target.shift(DOWN)
        brace = Brace(VGroup(*movers.target[1:]))

        words = TextMobject("You are one of these")
        words.to_edge(UP)
        arrows = [
            Arrow(words.get_bottom(), movers.target[i].get_top())
            for i in (0, -1)
        ]

        self.play(FadeOut(to_fade))
        self.play(
            MoveToTarget(movers),
            ReplacementTransform(self.false_positives_brace, brace),
            self.false_positives_words.next_to, brace, DOWN
        )
        self.play(
            Write(words, run_time = 2),
            ShowCreation(arrows[0])
        )
        self.play(Transform(
            *arrows, run_time = 4, rate_func = there_and_back
        ))
        self.play(*list(map(FadeOut, [words, arrows[0]])))

        self.brace = brace

    def show_posterior_probability(self):
        posterior = TexMobject(
            "P(", "\\text{Sick }", "|", 
            "\\text{ Positive test result}", ")",
            "\\approx \\frac{1}{11}", "\\approx 9\\%"
        )
        posterior.set_color_by_tex("Sick", SICKLY_GREEN)
        posterior.set_color_by_tex("Positive", YELLOW)
        posterior.to_edge(UP)
        posterior.shift(LEFT)

        self.play(FadeIn(posterior))
        self.wait(2)

        self.posterior = posterior

    def contrast_with_prior(self):
        prior = TexMobject(
            "P(", "\\text{Sick}", ")", "= 0.1\\%"
        )
        prior.set_color_by_tex("Sick", SICKLY_GREEN)
        prior.move_to(self.posterior, UP+RIGHT)

        self.revert_to_original_skipping_status()
        self.play(
            Write(prior, run_time = 1),
            self.posterior.shift, DOWN,
        )
        arrow = Arrow(
            prior.get_right(), self.posterior.get_right(),
            path_arc = -np.pi,
        )
        times_90 = TexMobject("\\times 90")
        times_90.next_to(arrow, RIGHT)
        self.play(ShowCreation(arrow))
        self.play(Write(times_90, run_time = 1))
        self.wait(2)

    ######

    def get_all_creatures(self):
        creature = PiCreature()
        all_creatures = VGroup(*[
            VGroup(*[
                creature.copy()
                for y in range(self.n_rows)
            ]).arrange(DOWN, SMALL_BUFF)
            for x in range(self.n_cols)
        ]).arrange(RIGHT, SMALL_BUFF)
        all_creatures.set_height(5)
        all_creatures.center().to_edge(LEFT)

        healthy_creatures = VGroup(*it.chain(*all_creatures))
        sick_one = all_creatures[-1][0]
        sick_one.change_mode("sick")
        sick_one.set_color(SICKLY_GREEN)
        healthy_creatures.remove(sick_one)
        all_creatures.sick_one = sick_one
        all_creatures.healthy_creatures = healthy_creatures
        return all_creatures

class DepressingForMedicalTestDesigners(TestScene):
    def construct(self):
        self.remove(self.pi_creature)
        self.show_99_percent_accuracy()
        self.reject_test()

    def show_99_percent_accuracy(self):
        title = TextMobject("99\\% Accuracy")
        title.to_edge(UP)
        title.generate_target()
        title.target.to_corner(UP+LEFT)

        checks = VGroup(*[
            VGroup(*[
                TexMobject("\\checkmark").set_color(GREEN)
                for y in range(10)
            ]).arrange(DOWN)
            for x in range(10)
        ]).arrange(RIGHT)
        cross = TexMobject("\\times")
        cross.replace(checks[-1][-1])
        cross.set_color(RED)
        Transform(checks[-1][-1], cross).update(1)
        checks.set_height(6)
        checks.next_to(title, DOWN)
        checks.generate_target()
        checks.target.scale(0.5)
        checks.target.next_to(title.target, DOWN)

        self.add(title)
        self.play(Write(checks))
        self.wait(2)
        self.play(*list(map(MoveToTarget, [title, checks])))

    def reject_test(self):
        randy = self.pi_creature
        randy.to_edge(DOWN)
        result = self.get_positive_result(randy)

        self.play(FadeIn(randy))
        self.play(
            FadeIn(result),
            randy.change_mode, "pondering"
        )
        self.wait()
        self.say(
            "Whatever, I'm 91\\% \\\\ sure that's wrong",
            target_mode = "shruggie"
        )
        self.wait(2)

class HowMuchCanYouChangeThisPrior(ShowRestrictedSpace, PiCreatureScene):
    def construct(self):
        self.single_out_new_sick_one()
        self.show_subgroups()
        self.isolate_special_group()

    def create_pi_creatures(self):
        creatures = self.get_all_creatures()
        creatures.set_height(6.5)
        creatures.center()
        creatures.submobjects  = list(it.chain(*creatures))

        self.add(creatures)
        self.sick_one = creatures.sick_one
        return creatures

    def single_out_new_sick_one(self):
        creatures = self.pi_creatures
        sick_one = self.sick_one
        new_sick_one = sick_one.copy()
        new_sick_one.shift(1.3*sick_one.get_width()*RIGHT)
        sick_one.change_mode("plain")
        sick_one.set_color(BLUE_E)

        self.add(new_sick_one)
        self.sick_one = new_sick_one

    def show_subgroups(self):
        subgroups = VGroup(*[
            VGroup(*it.chain(
                self.pi_creatures[i:i+5],
                self.pi_creatures[i+25:i+25+5:]
            ))
            for i in range(0, 1000)
            if i%5 == 0 and (i/25)%2 == 0
        ])
        special_group = subgroups[-5]
        special_group.add(self.sick_one)
        subgroups.generate_target()
        width_factor = FRAME_WIDTH/subgroups.get_width()
        height_factor = FRAME_HEIGHT/subgroups.get_height()
        subgroups.target.stretch_in_place(width_factor, 0)
        subgroups.target.stretch_in_place(height_factor, 1)
        for subgroup in subgroups.target:
            subgroup.stretch_in_place(1./width_factor, 0)
            subgroup.stretch_in_place(1./height_factor, 1)

        self.wait()
        self.play(MoveToTarget(subgroups))
        subgroups.remove(special_group)

        rects = VGroup(*[
            SurroundingRectangle(
                group, buff = 0, color = GREEN
            )
            for group in subgroups
        ])
        special_rect = SurroundingRectangle(
            special_group, buff = 0, color = RED
        )
        self.play(FadeIn(rects), FadeIn(special_rect))
        self.wait()

        self.to_fade = VGroup(subgroups, rects)
        self.special_group = special_group
        self.special_rect = special_rect

    def isolate_special_group(self):
        to_fade, special_group = self.to_fade, self.special_group
        self.play(FadeOut(to_fade))
        self.play(
            FadeOut(self.special_rect),
            special_group.set_height, 6,
            special_group.center,
        )
        self.wait()

class ShowTheFormula(TeacherStudentsScene):
    CONFIG = {
        "seconds_to_blink" : 3,
    }
    def construct(self):
        scale_factor = 0.7
        sick = "\\text{sick}"
        positive = "\\text{positive}"
        formula = TexMobject(
            "P(", sick, "\\,|\\,", positive, ")", "=",
            "{\\quad P(", sick, "\\text{ and }", positive, ") \\quad",
            "\\over",
            "P(", positive, ")}", "=",
            "{1/1{,}000", "\\over", "1/1{,}000", "+", "(999/1{,}000)(0.01)}"
        )
        formula.scale(scale_factor)
        formula.next_to(self.pi_creatures, UP, LARGE_BUFF)
        formula.shift_onto_screen(buff = MED_LARGE_BUFF)
        equals_group = formula.get_parts_by_tex("=")
        equals_indices = [
            formula.index_of_part(equals)
            for equals in equals_group
        ]

        lhs = VGroup(*formula[:equals_indices[0]])
        initial_formula = VGroup(*formula[:equals_indices[1]])
        initial_formula.save_state()
        initial_formula.shift(3*RIGHT)

        over = formula.get_part_by_tex("\\over")
        num_start_index = equals_indices[0] + 1
        num_end_index = formula.index_of_part(over)
        numerator = VGroup(
            *formula[num_start_index:num_end_index]
        )
        numerator_rect = SurroundingRectangle(numerator)

        alt_numerator = TexMobject(
            "P(", sick, ")", "P(", positive, "\\,|\\,", sick, ")"
        )
        alt_numerator.scale(scale_factor)
        alt_numerator.move_to(numerator)

        number_fraction = VGroup(*formula[equals_indices[-1]:])

        rhs = TexMobject("\\approx 0.09")
        rhs.scale(scale_factor)
        rhs.move_to(equals_group[-1], LEFT)
        rhs.set_color(YELLOW)

        for mob in formula, alt_numerator:
            mob.set_color_by_tex(sick, SICKLY_GREEN)
            mob.set_color_by_tex(positive, YELLOW)


        #Ask question
        self.student_says("What does the \\\\ formula look like here?")
        self.play(self.teacher.change, "happy")
        self.wait()
        self.play(
            Write(lhs),
            RemovePiCreatureBubble(
                self.students[1], target_mode = "pondering",
            ),
            self.teacher.change, "raise_right_hand",
            self.students[0].change, "pondering",
            self.students[2].change, "pondering",
        )
        self.wait()

        #Show initial formula
        lhs_copy = lhs.copy()
        self.play(
            LaggedStartMap(
                FadeIn, initial_formula, 
                lag_ratio = 0.7
            ),
            Animation(lhs_copy, remover = True),
        )
        self.wait(2)
        self.play(ShowCreation(numerator_rect))
        self.play(FadeOut(numerator_rect))
        self.wait()
        self.play(Transform(numerator, alt_numerator))
        initial_formula.add(*numerator)
        formula.add(*numerator)
        self.wait(3)

        #Show number_fraction
        self.play(
            initial_formula.move_to, initial_formula.saved_state,
            FadeIn(VGroup(*number_fraction[:3]))
        )
        self.wait(2)
        self.play(LaggedStartMap(
            FadeIn, VGroup(*number_fraction[3:]),
            run_time = 3,
            lag_ratio = 0.7
        ))
        self.wait(2)

        #Show rhs
        self.play(formula.shift, UP)
        self.play(Write(rhs))
        self.change_student_modes(*["happy"]*3)
        self.look_at(rhs)
        self.wait(2)

class SourceOfConfusion(Scene):
    CONFIG = {
        "arrow_width" : 5,
    }
    def construct(self):
        self.add_progression()
        self.ask_question()
        self.write_bayes_rule()
        self.shift_arrow()

    def add_progression(self):
        prior = TexMobject("P(", "S", ")", "= 0.001")
        arrow = Arrow(ORIGIN, self.arrow_width*RIGHT)
        posterior = TexMobject("P(", "S", "|", "+", ")", "= 0.09")
        for mob in prior, posterior:
            mob.set_color_by_tex("S", SICKLY_GREEN)
            mob.set_color_by_tex("+", YELLOW)
        progression = VGroup(prior, arrow, posterior)
        progression.arrange(RIGHT)
        progression.shift(DOWN)

        bayes_rule_words = TextMobject("Bayes' rule")
        bayes_rule_words.next_to(arrow, UP, buff = 0)
        arrow.add(bayes_rule_words)

        for mob, word in (prior, "Prior"), (posterior, "Posterior"):
            brace = Brace(mob, DOWN)
            label = brace.get_text(word)
            mob.add(brace, label)

        self.add(progression)
        self.progression = progression
        self.bayes_rule_words = bayes_rule_words

    def ask_question(self):
        question = TextMobject(
            "Where do math and \\\\ intuition disagree?"
        )
        question.to_corner(UP+LEFT)
        question_arrow = Arrow(
            question.get_bottom(),
            self.bayes_rule_words.get_top(),
            color = WHITE
        )

        self.play(Write(question))
        self.wait()
        self.play(ShowCreation(question_arrow))

        self.question = question
        self.question_arrow = question_arrow

    def write_bayes_rule(self):
        words = self.bayes_rule_words
        words_rect = SurroundingRectangle(words)
        rule = TexMobject(
            "P(", "S", "|", "+", ")", "=", 
            "P(", "S", ")", 
            "{P(", "+", "|", "S", ")", "\\over",
            "P(", "+", ")}"
        )
        rule.set_color_by_tex("S", SICKLY_GREEN)
        rule.set_color_by_tex("+", YELLOW)
        rule.to_corner(UP+RIGHT)
        rule_rect = SurroundingRectangle(rule)
        rule_rect.set_color(BLUE)
        rule.save_state()
        rule.replace(words_rect)
        rule.scale_in_place(0.9)
        rule.set_fill(opacity = 0)

        self.play(ShowCreation(words_rect))
        self.play(
            ReplacementTransform(words_rect, rule_rect),
            rule.restore,
            run_time = 2
        )
        self.wait(3)

    def shift_arrow(self):
        new_arrow = Arrow(
            self.question.get_bottom(),
            self.progression[0].get_top(),
            color = WHITE
        )

        self.play(Transform(
            self.question_arrow,
            new_arrow
        ))
        self.wait(2)

class StatisticsVsEmpathy(PiCreatureScene):
    def construct(self):
        randy, morty = self.randy, self.morty
        sick_one = PiCreature()
        sick_one.scale(0.5)
        sick_group = VGroup(
            sick_one, VectorizedPoint(sick_one.get_bottom())
        )
        priors = VGroup(*[
            TexMobject("%.1f"%p+ "\\%").move_to(ORIGIN, RIGHT)
            for p in np.arange(0.1, 2.0, 0.1)
        ])
        priors.next_to(randy, UP+LEFT, LARGE_BUFF)
        prior = priors[0]
        prior.save_state()

        self.play(PiCreatureSays(
            morty, 
            "1 in 1{,}000 people \\\\ have this disease.",
            look_at_arg = randy.eyes
        ))
        self.play(randy.change, "pondering", morty.eyes)
        self.wait()
        self.play(Write(prior))
        self.wait()
        self.play(
            prior.scale, 0.1,
            prior.set_fill, None, 0,
            prior.move_to, randy.eyes
        )
        self.wait()
        self.play(
            PiCreatureBubbleIntroduction(
                randy, sick_group,
                target_mode = "guilty",
                bubble_class = ThoughtBubble,
                content_introduction_class = FadeIn,
                look_at_arg = sick_one,
            ),
            RemovePiCreatureBubble(morty)
        )
        self.play(
            sick_one.change_mode, "sick",
            sick_one.set_color, SICKLY_GREEN
        )
        self.wait()

        probably_me = TextMobject("That's probably \\\\ me")
        probably_me.next_to(sick_one, DOWN)
        target_sick_group = VGroup(
            sick_one.copy(),
            probably_me
        )
        target_sick_group.scale(0.8)
        self.pi_creature_thinks(
            target_sick_group,
            target_mode = "pleading",
        )
        self.wait(2)

        self.play(prior.restore)
        for new_prior in priors[1:]:
            self.play(Transform(prior, new_prior, run_time = 0.5))
        self.wait()

    ######

    def create_pi_creatures(self):
        randy = self.randy = Randolph()
        morty = self.morty = Mortimer()
        randy.to_edge(DOWN).shift(3*LEFT)
        morty.to_edge(DOWN).shift(3*RIGHT)
        return VGroup(randy, morty)

class LessMedicalExample(Scene):
    def construct(self):
        disease = TexMobject("P(\\text{Having a disease})")
        telepathy = TexMobject("P(\\text{Telepathy})")
        cross = Cross(disease)

        self.add(disease)
        self.wait()
        self.play(ShowCreation(cross))
        self.play(
            FadeIn(telepathy),
            VGroup(disease, cross).shift, 2*UP
        )
        self.wait()

class PlaneCrashProbability(Scene):
    def construct(self):
        plane_prob = TexMobject(
            "P(\\text{Dying in a }", "\\text{plane}", "\\text{ crash})", 
            "\\approx", "1/", "11{,}000{,}000"
        )
        plane_prob.set_color_by_tex("plane", BLUE)
        car_prob = TexMobject(
            "P(\\text{Dying in a }", "\\text{car}", "\\text{ crash})", 
            "\\approx", "1/", "5{,}000"
        )
        car_prob.set_color_by_tex("car", YELLOW)
        plane_prob.shift(UP)
        car_prob.shift(
            plane_prob.get_part_by_tex("approx").get_center() -\
            car_prob.get_part_by_tex("approx").get_center() +\
            DOWN
        )

        self.play(Write(plane_prob))
        self.wait(2)
        self.play(ReplacementTransform(
            plane_prob.copy(), car_prob
        ))
        self.wait(2)

class IntroduceTelepathyExample(StatisticsVsEmpathy):
    def construct(self):
        self.force_skipping()

        self.show_mind_reading_powers()
        self.claim_mind_reading_powers()
        self.generate_random_number()
        self.guess_number_correctly()
        self.ask_about_chances()
        self.revert_to_original_skipping_status()
        self.say_you_probably_got_lucky()

    def show_mind_reading_powers(self):
        randy, morty = self.randy, self.morty
        title = TextMobject("1 in 1{,}000 read minds")
        title.to_edge(UP)

        self.add(title)
        self.read_mind(randy, morty)

        self.title = title

    def claim_mind_reading_powers(self):
        randy, morty = self.randy, self.morty
        self.play(PiCreatureSays(
            randy, "I have the gift.",
            run_time = 1,
            look_at_arg = morty.eyes,
        ))
        self.wait()
        self.play(RemovePiCreatureBubble(
            randy,
            target_mode = "happy",
            look_at_arg = morty.eyes
        ))

    def generate_random_number(self):
        morty = self.morty
        bubble = morty.get_bubble("", direction = LEFT)
        numbers = [
            Integer(random.choice(list(range(100))))
            for x in range(30)
        ]
        numbers.append(Integer(67))
        for number in numbers:
            number.next_to(morty, UP, LARGE_BUFF, RIGHT)


        for number in numbers:
            self.add(number)
            Scene.wait(self, 0.1)
            self.remove(number)
        self.play(
            ShowCreation(bubble),
            number.move_to, bubble.get_bubble_center(), DOWN+LEFT,
            morty.change, "pondering", 
        )
        self.wait()

        morty.bubble = bubble
        self.number = number

    def guess_number_correctly(self):
        randy, morty = self.randy, self.morty
        number_copy = self.number.copy()

        self.read_mind(randy, morty)
        self.play(PiCreatureSays(
            randy, number_copy,
            target_mode = "hooray",
            look_at_arg = morty.eyes
        ))
        self.wait()

    def ask_about_chances(self):
        probability = TexMobject(
            "P(", "\\text{Telepath }", "|", "\\text{ Correct}", ")",
            "=", "???"
        )
        probability.set_color_by_tex("Telepath", BLUE)
        probability.set_color_by_tex("Correct", GREEN)
        probability.to_edge(UP)

        self.play(morty.change, "confused", randy.eyes)
        self.wait()
        self.play(ReplacementTransform(
            self.title, VGroup(*it.chain(*probability))
        ))
        self.wait()

    def say_you_probably_got_lucky(self):
        randy, morty = self.randy, self.morty

        self.play(
            PiCreatureSays(
                morty, "You probably \\\\ got lucky.",
                target_mode = "sassy",
                look_at_arg = randy.eyes,
                bubble_kwargs = {"height" : 3, "width" : 4}
            ),
            RemovePiCreatureBubble(
                randy, 
                target_mode = "plain",
                look_at_arg = morty.eyes,
            )
        )
        self.wait(2)


    ###

    def read_mind(self, pi1, pi2):
        self.play(pi1.change, "telepath", pi2.eyes)
        self.send_mind_waves(pi1, pi2)
        self.send_mind_waves(pi2, pi1)
        self.wait()

    def send_mind_waves(self, pi1, pi2):
        angle = np.pi/3
        n_arcs = 5
        vect = pi2.eyes.get_center() - pi1.eyes.get_center()
        vect[1] = 0

        arc = Arc(angle = angle)
        arc.rotate(-angle/2 + angle_of_vector(vect), about_point = ORIGIN)
        arc.scale(3)
        arcs = VGroup(*[arc.copy() for x in range(n_arcs)])
        arcs.move_to(pi2.eyes.get_center(), vect)
        arcs.set_stroke(BLACK, 0)
        for arc in arcs:
            arc.save_state()
        arcs.scale(0.1)
        arcs.move_to(pi1.eyes, vect)
        arcs.set_stroke(WHITE, 4)

        self.play(LaggedStartMap(
            ApplyMethod, arcs,
            lambda m : (m.restore,),
            lag_ratio = 0.7,
        ))
        self.remove(arcs)

class CompareNumbersInBothExamples(Scene):
    def construct(self):
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_line.shift(MED_LARGE_BUFF*LEFT)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.to_edge(UP, buff = 1.25*LARGE_BUFF)
        titles = VGroup()
        for word, vect in ("Disease", LEFT), ("Telepathy", RIGHT):
            title = TextMobject("%s example"%word)
            title.shift(vect*FRAME_X_RADIUS/2.0)
            title.to_edge(UP)
            titles.add(title)
        priors = VGroup(*[
            TexMobject(
                "P(", "\\text{%s}"%s, ")", "= 1/1{,}000}"
            )
            for s in ("Sick", "Powers")
        ])
        likelihoods = VGroup(*[
            TexMobject(
                "P(", "\\text{%s}"%s1, "|", 
                "\\text{Not }", "\\text{%s}"%s2, ")",
                "=", "1/100"
            )
            for s1, s2 in [("+", "Sick"), ("Correct", "Powers")]
        ])
        priors.next_to(likelihoods, UP, LARGE_BUFF)
        for group in priors, likelihoods:
            for mob, vect in zip(group, [LEFT, RIGHT]):
                mob.set_color_by_tex("Sick", BLUE)
                mob.set_color_by_tex("Powers", BLUE)
                mob.set_color_by_tex("+", GREEN)
                mob.set_color_by_tex("Correct", GREEN)
                mob.scale(0.8)
                mob.shift(vect*FRAME_X_RADIUS/2)

        self.play(
            LaggedStartMap(FadeIn, titles, lag_ratio = 0.7),
            *list(map(ShowCreation, [h_line, v_line]))
        )
        self.wait()
        self.play(FadeIn(priors))
        self.wait()
        self.play(FadeIn(likelihoods))
        self.wait(3)


class NonchalantReactionToPositiveTest(TestScene):
    def construct(self):
        randy = self.pi_creature
        randy.shift(DOWN+2*RIGHT)
        result = self.get_positive_result(randy)
        accuracy = TextMobject("99\\% Accuracy")
        accuracy.set_color(YELLOW)
        accuracy.next_to(result, DOWN, LARGE_BUFF, RIGHT)

        self.add(accuracy)
        self.play(Write(result, run_time = 2))
        self.play(randy.change, "pondering", result)
        self.wait()
        words = TextMobject("Pssht, I'm probably fine.")
        words.scale(0.8)
        self.pi_creature_says(
            words,
            target_mode = "shruggie",
            bubble_kwargs = {
                "direction" : RIGHT,
                "width" : 6,
                "height" : 3,
            },
            content_introduction_class = FadeIn,
        )
        self.wait(4)

class OneInOneThousandHaveDiseaseCopy(OneInOneThousandHaveDisease):
    pass

class ExampleMeasuresDisbeliefInStatistics(Introduction):
    def construct(self):
        self.teacher.shift(LEFT)
        self.hold_up_example()
        self.write_counter_intuitive()
        self.write_new_theory()
        self.either_way()

    def write_new_theory(self):
        bayes_to_intuition = self.bayes_to_intuition
        cross = bayes_to_intuition[-1]
        bayes_to_intuition.remove(cross)
        statistics_to_belief = TextMobject(
            "Statistics ", "$\\leftrightarrow$", " Belief"
        )
        statistics_to_belief.scale(0.8)
        arrow = statistics_to_belief.get_part_by_tex("arrow")
        statistics_to_belief.next_to(self.example, UP)

        self.revert_to_original_skipping_status()
        self.play(bayes_to_intuition.to_edge, UP)
        self.play(
            LaggedStartMap(FadeIn, statistics_to_belief),
            cross.move_to, arrow
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = statistics_to_belief
        )
        self.wait(3)

        statistics_to_belief.add(cross)
        self.statistics_to_belief = statistics_to_belief

    def either_way(self):
        b_to_i = self.bayes_to_intuition
        s_to_b = self.statistics_to_belief
        
        self.play(FadeOut(self.example))
        self.play(
            self.teacher.change_mode, "raise_left_hand",
            self.teacher.look, UP+RIGHT,
            b_to_i.next_to, self.teacher, UP,
            b_to_i.to_edge, RIGHT, MED_SMALL_BUFF,
        )
        self.wait(2)
        self.play(
            self.teacher.change_mode, "raise_right_hand",
            self.teacher.look, UP+LEFT,
            s_to_b.next_to, self.teacher, UP,
            s_to_b.shift, LEFT,
            b_to_i.shift, 2*UP
        )
        self.wait(2)

class AlwaysPictureTheSpaceOfPossibilities(PiCreatureScene):
    def construct(self):
        self.pi_creature_thinks(
            "", bubble_kwargs = {
                "height" : 4.5,
                "width" : 8,
            }
        )
        self.wait(3)

    def create_pi_creature(self):
        return Randolph().to_corner(DOWN+LEFT)

class Thumbnail(Scene):
    def construct(self):
        title = TextMobject("Why is this \\\\ counterintuitive?")
        title.scale(2)
        title.to_edge(UP)

        randy = Randolph(mode = "sick",  color = SICKLY_GREEN)
        # randy.look_at(title)
        randy.scale(1.5)
        randy.shift(3*LEFT)
        randy.to_edge(DOWN)

        prob = TexMobject("P(", "\\text{Sick}", "|", "\\text{Test+}", ")")
        prob.scale(2)
        prob.set_color_by_tex("Sick", YELLOW)
        prob.set_color_by_tex("Test", GREEN)
        prob.next_to(randy, RIGHT)

        self.add(title, randy, prob)




























