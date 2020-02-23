from manimlib.imports import *
from from_3b1b.active.bayes.beta_helpers import *

import scipy.stats

OUTPUT_DIRECTORY = "bayes/beta"


# Scenes
class BarChartTest(Scene):
    def construct(self):
        bar_chart = BarChart()
        bar_chart.to_edge(DOWN)
        self.add(bar_chart)


class Thumbnail(Scene):
    def construct(self):
        p1 = "$96\\%$"
        p2 = "$93\\%$"
        n1 = "50"
        n2 = "200"
        t2c = {
            p1: BLUE,
            p2: YELLOW,
            n1: BLUE_C,
            n2: YELLOW,
        }
        kw = {"tex_to_color_map": t2c}
        text = VGroup(
            TextMobject(f"{p1} with {n1} reviews", **kw),
            TextMobject("vs.", **kw),
            TextMobject(f"{p2} with {n2} reviews", **kw),
        )
        fix_percent(text[0].get_part_by_tex(p1)[-1])
        fix_percent(text[2].get_part_by_tex(p2)[-1])
        text.scale(2)
        text.arrange(DOWN, buff=LARGE_BUFF)
        text.set_width(FRAME_WIDTH - 1)
        self.add(text)


class ShowThreeCases(Scene):
    def construct(self):
        titles = self.get_titles()
        reviews = self.get_reviews(titles)
        for review in reviews:
            review.match_x(reviews[2])

        # Introduce everything
        self.play(LaggedStartMap(
            FadeInFrom, titles,
            lambda m: (m, DOWN),
            lag_ratio=0.2
        ))
        self.play(LaggedStart(*[
            LaggedStartMap(
                FadeInFromLarge, review,
                lag_ratio=0.1
            )
            for review in reviews
        ], lag_ratio=0.1))
        self.add(reviews)
        self.wait()

        self.play(ShowCreationThenFadeAround(reviews[2]))
        self.wait()

        # Suspicious of 100%
        randy = Randolph()
        randy.flip()
        randy.set_height(2)
        randy.next_to(
            reviews[0], RIGHT, LARGE_BUFF,
            aligned_edge=UP,
        )
        randy.look_at(reviews[0])
        self.play(FadeIn(randy))
        self.play(randy.change, "sassy")
        self.play(Blink(randy))
        self.wait()
        self.play(FadeOut(randy))

        # Low number means it could be a fluke.
        review = reviews[0]

        review.generate_target()
        review.target.scale(2)
        review.target.arrange(RIGHT)
        review.target.move_to(review)

        self.play(MoveToTarget(review))

        alt_negs = [1, 2, 1, 0]
        alt_reviews = VGroup()
        for k in alt_negs:
            alt_reviews.add(self.get_plusses_and_minuses(titles[0], 1, 10, k))
        for ar in alt_reviews:
            for m1, m2 in zip(ar, review):
                m1.replace(m2)

        alt_percents = VGroup(*[
            TexMobject(str(10 * (10 - k)) + "\\%")
            for k in alt_negs
        ])
        hundo = titles[0][0]
        for ap in alt_percents:
            fix_percent(ap.family_members_with_points()[-1])
            ap.match_style(hundo)
            ap.match_height(hundo)
            ap.move_to(hundo, RIGHT)

        last_review = review
        last_percent = hundo
        for ar, ap in zip(alt_reviews, alt_percents):
            self.play(
                FadeInFrom(ar, 0.5 * DOWN, lag_ratio=0.2),
                FadeOut(last_review),
                FadeInFrom(ap, 0.5 * DOWN),
                FadeOutAndShift(last_percent, 0.5 * UP),
                run_time=1.5
            )
            last_review = ar
            last_percent = ap
        self.remove(last_review, last_percent)
        self.add(titles, *reviews)

        # How do you think about the tradeoff?
        p1 = titles[1][0]
        p2 = titles[2][0]
        nums = VGroup(p1, p2)
        lower_reviews = reviews[1:]
        lower_reviews.generate_target()
        lower_reviews.target.arrange(LEFT, buff=1.5)
        lower_reviews.target.center()
        nums.generate_target()
        for nt, review in zip(nums.target, lower_reviews.target):
            nt.next_to(review, UP, MED_LARGE_BUFF)

        nums.target[0].match_y(nums.target[1])

        self.clear()
        self.play(
            MoveToTarget(lower_reviews),
            MoveToTarget(nums),
            FadeOut(titles[1][1:]),
            FadeOut(titles[2][1:]),
            FadeOut(titles[0]),
            FadeOut(reviews[0]),
            run_time=2,
        )

        greater_than = TexMobject(">")
        greater_than.scale(2)
        greater_than.move_to(midpoint(
            reviews[2].get_right(),
            reviews[1].get_left(),
        ))
        less_than = greater_than.copy().flip()
        less_than.match_height(nums[0][0])
        less_than.match_y(nums, DOWN)

        nums.generate_target()
        nums.target[1].next_to(less_than, LEFT, MED_LARGE_BUFF)
        nums.target[0].next_to(less_than, RIGHT, MED_LARGE_BUFF)

        squares = VGroup(*[
            SurroundingRectangle(
                submob, buff=0.01,
                stroke_color=LIGHT_GREY,
                stroke_width=1,
            )
            for submob in reviews[2]
        ])
        squares.shuffle()
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeOut, squares,
                lag_ratio=0.5 / len(squares),
                run_time=3,
            ),
            Write(greater_than),
        )
        self.wait()
        self.play(
            MoveToTarget(nums),
            TransformFromCopy(
                greater_than, less_than,
            )
        )
        self.wait()

    def get_titles(self):
        titles = VGroup(
            TextMobject(
                "$100\\%$ \\\\",
                "10 reviews"
            ),
            TextMobject(
                "$96\\%$ \\\\",
                "50 reviews"
            ),
            TextMobject(
                "$93\\%$ \\\\",
                "200 reviews"
            ),
        )
        colors = [PINK, BLUE, YELLOW]
        for title, color in zip(titles, colors):
            fix_percent(title[0][-1])
            title[0].set_color(color)

        titles.scale(1.25)
        titles.arrange(DOWN, buff=1.5)
        titles.to_corner(UL)
        return titles

    def get_reviews(self, titles):
        return VGroup(
            self.get_plusses_and_minuses(
                titles[0], 5, 2, 0,
            ),
            self.get_plusses_and_minuses(
                titles[1], 5, 10, 2,
            ),
            self.get_plusses_and_minuses(
                titles[2], 8, 25, 14,
            ),
        )

    def get_plusses_and_minuses(self, title, n_rows, n_cols, n_minus):
        check = TexMobject(CMARK_TEX, color=GREEN)
        cross = TexMobject(XMARK_TEX, color=RED)
        checks = VGroup(*[
            check.copy() for x in range(n_rows * n_cols)
        ])
        checks.arrange_in_grid(n_rows=n_rows, n_cols=n_cols)
        checks.scale(0.5)
        # if checks.get_height() > title.get_height():
        #     checks.match_height(title)
        checks.next_to(title, RIGHT, LARGE_BUFF)

        for check in random.sample(list(checks), n_minus):
            mob = cross.copy()
            mob.replace(check, dim_to_match=0)
            check.become(mob)

        return checks


class WhatsTheModel(Scene):
    def construct(self):
        self.add_questions()
        self.introduce_buyer_and_seller()

        for x in range(3):
            self.play(*self.experience_animations(self.seller, self.buyer))
        self.wait()

        self.add_probability_label()
        self.bring_up_goal()

    def add_questions(self):
        questions = VGroup(
            TextMobject("What's the model?"),
            TextMobject("What are you optimizing?"),
        )
        for question, vect in zip(questions, [LEFT, RIGHT]):
            question.move_to(vect * FRAME_WIDTH / 4)
        questions.arrange(DOWN, buff=LARGE_BUFF)
        questions.scale(1.5)

        # Intro questions
        self.play(FadeInFrom(questions[0]))
        self.play(FadeInFrom(questions[1], UP))
        self.wait()
        questions[1].save_state()

        self.questions = questions

    def introduce_buyer_and_seller(self):
        if hasattr(self, "questions"):
            questions = self.questions
            added_anims = [
                questions[0].to_edge, UP,
                questions[1].set_opacity, 0.5,
                questions[1].scale, 0.25,
                questions[1].to_corner, UR,
            ]
        else:
            added_anims = []

        seller = Randolph(mode="coin_flip_1")
        seller.to_edge(LEFT)
        seller.label = TextMobject("Seller")

        buyer = Mortimer()
        buyer.to_edge(RIGHT)
        buyer.label = TextMobject("Buyer")

        VGroup(buyer, seller).shift(DOWN)

        labels = VGroup()
        for pi in seller, buyer:
            pi.set_height(2)
            pi.label.scale(1.5)
            pi.label.next_to(pi, DOWN, MED_LARGE_BUFF)
            labels.add(pi.label)
        buyer.make_eye_contact(seller)

        self.play(
            LaggedStartMap(
                FadeInFromDown, VGroup(seller, buyer, *labels),
                lag_ratio=0.2
            ),
            *added_anims
        )
        self.wait()

        self.buyer = buyer
        self.seller = seller

    def add_probability_label(self):
        seller = self.seller
        buyer = self.buyer

        label = get_prob_positive_experience_label()
        label.add(TexMobject("=").next_to(label, RIGHT))
        rhs = DecimalNumber(0.75)
        rhs.next_to(label, RIGHT)
        rhs.align_to(label[0], DOWN)
        label.add(rhs)
        label.scale(1.5)
        label.next_to(seller, UP, MED_LARGE_BUFF, aligned_edge=LEFT)

        rhs.set_color(YELLOW)
        brace = Brace(rhs, UP)
        success_rate = brace.get_text("Success rate")[0]
        s_sym = brace.get_tex("s").scale(1.5, about_edge=DOWN)
        success_rate.match_color(rhs)
        s_sym.match_color(rhs)

        self.add(label)

        self.play(
            GrowFromCenter(brace),
            FadeInFrom(success_rate, 0.5 * DOWN)
        )
        self.wait()
        self.play(
            TransformFromCopy(success_rate[0], s_sym),
            FadeOutAndShift(success_rate, 0.1 * RIGHT, lag_ratio=0.1),
        )
        for x in range(2):
            self.play(*self.experience_animations(seller, buyer, arc=30 * DEGREES))
        self.wait()

        grey_box = SurroundingRectangle(rhs, buff=SMALL_BUFF)
        grey_box.set_stroke(GREY_E, 0.5)
        grey_box.set_fill(GREY_D, 1)
        lil_q_marks = TexMobject("???")
        lil_q_marks.scale(0.5)
        lil_q_marks.next_to(buyer, UP)

        self.play(
            FadeOutAndShift(rhs, 0.5 * DOWN),
            FadeInFrom(grey_box, 0.5 * UP),
            FadeInFrom(lil_q_marks, DOWN),
            buyer.change, "confused", grey_box,
        )
        rhs.set_opacity(0)
        for x in range(2):
            self.play(*self.experience_animations(seller, buyer, arc=30 * DEGREES))
        self.play(buyer.change, "confused", lil_q_marks)
        self.play(Blink(buyer))

        self.prob_group = VGroup(
            label, grey_box, brace, s_sym,
        )
        self.buyer_q_marks = lil_q_marks

    def bring_up_goal(self):
        prob_group = self.prob_group
        questions = self.questions
        questions.generate_target()
        questions.target[1].replace(questions[0], dim_to_match=1)
        questions.target[1].match_style(questions[0])
        questions.target[0].replace(questions[1], dim_to_match=1)
        questions.target[0].match_style(questions[1])

        prob_group.generate_target()
        prob_group.target.scale(0.5)
        prob_group.target.next_to(self.seller, RIGHT)

        self.play(
            FadeOut(self.buyer_q_marks),
            self.buyer.change, "pondering", questions[0],
            self.seller.change, "pondering", questions[0],
            MoveToTarget(prob_group),
            MoveToTarget(questions),
        )
        self.play(self.seller.change, "coin_flip_1")
        for x in range(3):
            self.play(*self.experience_animations(self.seller, self.buyer))
        self.wait()

    #
    def experience_animations(self, seller, buyer, arc=-30 * DEGREES, p=0.75):
        positive = (random.random() < p)
        words = TextMobject(
            "Positive\\\\experience"
            if positive else
            "Negative\\\\experience"
        )
        words.set_color(GREEN if positive else RED)
        if positive:
            new_mode = random.choice([
                "hooray",
                "happy",
            ])
        else:
            new_mode = random.choice([
                "tired",
                "angry",
                "sad",
            ])

        words.move_to(seller.get_corner(UR))
        result = [
            ApplyMethod(
                words.move_to, buyer.get_corner(UL),
                path_arc=arc,
                run_time=2
            ),
            VFadeInThenOut(words, run_time=2),
            ApplyMethod(
                buyer.change, new_mode, seller.eyes,
                run_time=2,
                rate_func=squish_rate_func(smooth, 0.5, 1),
            ),
            ApplyMethod(
                seller.change, "coin_flip_2", buyer.eyes,
                rate_func=there_and_back,
            ),
        ]
        return result


class IsSellerOne100(Scene):
    def construct(self):
        self.add_review()
        self.show_probability()
        self.show_random_numbers()

    def add_review(self):
        reviews = VGroup(*[TexMobject("\\checkmark") for x in range(10)])
        reviews.arrange(RIGHT)
        reviews.scale(2)
        reviews.set_color(GREEN)
        reviews.next_to(ORIGIN, UP)

        blanks = VGroup(*[
            Line(LEFT, RIGHT).match_width(rev).next_to(rev, DOWN, SMALL_BUFF)
            for rev in reviews
        ])
        blanks.shift(0.25 * reviews[0].get_width() * LEFT)

        label = TextMobject(
            " out of ",
        )
        tens = VGroup(*[Integer(10) for x in range(2)])
        tens[0].next_to(label, LEFT)
        tens[1].next_to(label, RIGHT)
        tens.set_color(GREEN)
        label.add(tens)
        label.scale(2)
        label.next_to(reviews, DOWN, LARGE_BUFF)

        self.add(label)
        self.add(blanks)
        tens[0].to_count = reviews
        self.play(
            ShowIncreasingSubsets(reviews, int_func=np.ceil),
            UpdateFromAlphaFunc(
                tens[0],
                lambda m, a: m.set_color(
                    interpolate_color(RED, GREEN, a)
                ).set_value(len(m.to_count))
            ),
            run_time=2,
            rate_func=bezier([0, 0, 1, 1]),
        )
        self.wait()

        self.review_group = VGroup(reviews, blanks, label)

    def show_probability(self):
        review_group = self.review_group

        prob_label = get_prob_positive_experience_label()
        prob_label.add(TexMobject("=").next_to(prob_label, RIGHT))
        rhs = DecimalNumber(1)
        rhs.next_to(prob_label, RIGHT)
        rhs.set_color(YELLOW)
        prob_label.add(rhs)
        prob_label.scale(2)
        prob_label.to_corner(UL)

        q_mark = TexMobject("?")
        q_mark.set_color(YELLOW)
        q_mark.match_height(rhs)
        q_mark.reference = rhs
        q_mark.add_updater(lambda m: m.next_to(m.reference, RIGHT))

        rhs_rect = SurroundingRectangle(rhs, buff=0.2)
        rhs_rect.set_color(RED)

        not_necessarily = TextMobject("Not necessarily!")
        not_necessarily.set_color(RED)
        not_necessarily.scale(1.5)
        not_necessarily.next_to(prob_label, DOWN, 1.5)
        arrow = Arrow(
            not_necessarily.get_top(),
            rhs_rect.get_corner(DL),
            buff=MED_SMALL_BUFF,
        )
        arrow.set_color(RED)

        rhs.set_value(0)
        self.play(
            ChangeDecimalToValue(rhs, 1),
            UpdateFromAlphaFunc(
                prob_label,
                lambda m, a: m.set_opacity(a),
            ),
            FadeIn(q_mark),
        )
        self.wait()
        self.play(
            ShowCreation(rhs_rect),
            Write(not_necessarily),
            ShowCreation(arrow),
            review_group.to_edge, DOWN,
            run_time=1,
        )
        self.wait()
        self.play(
            ChangeDecimalToValue(rhs, 0.95),
            FadeOut(rhs_rect),
            FadeOut(arrow),
            FadeOut(not_necessarily),
        )
        self.wait()

        self.prob_label_group = VGroup(
            prob_label, rhs, q_mark,
        )

    def show_random_numbers(self):
        prob_label_group = self.prob_label_group

        random.seed(2)
        rows = VGroup(*[
            VGroup(*[
                Integer(
                    random.randint(0, 99)
                ).move_to(0.85 * x * RIGHT)
                for x in range(10)
            ])
            for y in range(10 * 2)
        ])
        rows.arrange_in_grid(n_cols=2, buff=MED_LARGE_BUFF)
        rows[:10].shift(LEFT)
        rows.set_height(5.5)
        rows.center().to_edge(DOWN)

        lt_95 = VGroup(*[
            mob
            for row in rows
            for mob in row
            if mob.get_value() < 95
        ])

        square = Square()
        square.set_stroke(width=0)
        square.set_fill(YELLOW, 0.5)
        square.set_width(1.5 * rows[0][0].get_height())
        highlights = VGroup(*[
            square.copy().move_to(mob)
            for row in rows
            for mob in row
            if mob.get_value() < 95
        ])

        row_rects = VGroup(*[
            SurroundingRectangle(row)
            for row in rows
            if all([m.get_value() < 95 for m in row])
        ])
        row_rects.set_stroke(GREEN, 2)

        self.play(
            LaggedStartMap(
                ShowIncreasingSubsets, rows,
                run_time=3,
                lag_ratio=0.25,
            ),
            FadeOutAndShift(self.review_group, DOWN),
            prob_label_group.set_height, 0.75,
            prob_label_group.to_corner, UL,
        )
        self.wait()
        # self.add(highlights, rows)
        self.play(
            # FadeIn(highlights)
            lt_95.set_fill, BLUE,
            lt_95.set_stroke, BLUE, 2, {"background": True},
        )
        self.wait()
        self.play(LaggedStartMap(ShowCreation, row_rects))
        self.wait()


class LookAtAllPossibleSuccessRates(Scene):
    def construct(self):
        axes = get_beta_dist_axes(y_max=6, y_unit=1)
        dist = scipy.stats.beta(10, 2)
        graph = axes.get_graph(dist.pdf)
        graph.set_stroke(BLUE, 3)
        flat_graph = graph.copy()
        flat_graph.points[:, 1] = axes.c2p(0, 0)[1]
        flat_graph.set_stroke(YELLOW, 3)

        x_labels = axes.x_axis.numbers
        x_labels.set_opacity(0)

        sellers = VGroup(*[
            self.get_example_seller(label.get_value())
            for label in x_labels
        ])
        sellers.arrange(RIGHT, buff=LARGE_BUFF)
        sellers.set_width(FRAME_WIDTH - 1)
        sellers.to_edge(UP, buff=LARGE_BUFF)

        sellers.generate_target()
        for seller, label in zip(sellers.target, x_labels):
            seller.next_to(label, DOWN)
            seller[0].set_opacity(0)
            seller[1].set_opacity(0)
            seller[2].replace(label, dim_to_match=1)

        x_label = TextMobject("All possible success rates")
        x_label.next_to(axes.c2p(0.5, 0), UP)
        x_label.shift(2 * LEFT)

        y_axis_label = TextMobject(
            "A kind of probability\\\\",
            "of probabilities"
        )
        y_axis_label.scale(0.75)
        y_axis_label.next_to(axes.y_axis, RIGHT)
        y_axis_label.to_edge(UP)
        y_axis_label[1].set_color(YELLOW)

        graph_label = TextMobject(
            "Some notion of likelihood\\\\",
            "for each one"
        )
        graph_label[1].align_to(graph_label[0], LEFT)
        graph_label.next_to(graph.get_boundary_point(UP), UP)
        graph_label.shift(0.5 * DOWN)
        graph_label.to_edge(RIGHT)

        x_axis_line = Line(axes.c2p(0, 0), axes.c2p(1, 0))
        x_axis_line.set_stroke(YELLOW, 3)

        shuffled_sellers = VGroup(*sellers)
        shuffled_sellers.shuffle()
        self.play(GrowFromCenter(shuffled_sellers[0]))
        self.play(LaggedStartMap(
            FadeInFromPoint, shuffled_sellers[1:],
            lambda m: (m, sellers.get_center())
        ))
        self.wait()
        self.play(
            MoveToTarget(sellers),
            FadeIn(axes),
            run_time=2,
        )

        self.play(
            x_label.shift, 4 * RIGHT,
            UpdateFromAlphaFunc(
                x_label,
                lambda m, a: m.set_opacity(a),
                rate_func=there_and_back,
            ),
            ShowCreation(x_axis_line),
            run_time=3,
        )
        self.play(FadeOut(x_axis_line))
        self.wait()
        self.play(
            FadeInFromDown(graph_label),
            ReplacementTransform(flat_graph, graph),
        )
        self.wait()
        self.play(FadeInFromDown(y_axis_label))

        # Show probabilities
        x_tracker = ValueTracker(0.5)

        prob_label = get_prob_positive_experience_label(True, True, True)
        prob_label.next_to(axes.c2p(0, 2), RIGHT, MED_LARGE_BUFF)
        prob_label.decimal.tracker = x_tracker
        prob_label.decimal.add_updater(
            lambda m: m.set_value(m.tracker.get_value())
        )

        v_line = Line(DOWN, UP)
        v_line.set_stroke(YELLOW, 2)
        v_line.tracker = x_tracker
        v_line.graph = graph
        v_line.axes = axes
        v_line.add_updater(
            lambda m: m.put_start_and_end_on(
                m.axes.x_axis.n2p(m.tracker.get_value()),
                m.axes.input_to_graph_point(m.tracker.get_value(), m.graph),
            )
        )

        self.add(v_line)
        for x in [0.95, 0.8, 0.9]:
            self.play(
                x_tracker.set_value, x,
                run_time=4,
            )
        self.wait()

    def get_example_seller(self, success_rate):
        randy = Randolph(mode="coin_flip_1", height=1)
        label = TexMobject("s = ")
        decimal = DecimalNumber(success_rate)
        decimal.match_height(label)
        decimal.next_to(label[-1], RIGHT)
        label.set_color(YELLOW)
        decimal.set_color(YELLOW)
        VGroup(label, decimal).next_to(randy, DOWN)
        result = VGroup(randy, label, decimal)
        result.randy = randy
        result.label = label
        result.decimal = decimal
        return result


class AskAboutUnknownProbabilities(Scene):
    def construct(self):
        # Setup
        unknown_title, prob_title = titles = self.get_titles()

        v_line = Line(UP, DOWN)
        v_line.set_height(FRAME_HEIGHT)
        v_line.set_stroke([WHITE, LIGHT_GREY], 3)
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_WIDTH)
        h_line.next_to(titles, DOWN)

        processes = VGroup(
            get_random_coin(shuffle_time=1),
            get_random_die(shuffle_time=1.5),
            get_random_card(shuffle_time=2),
        )
        processes.arrange(DOWN, buff=0.7)
        processes.next_to(unknown_title, DOWN, LARGE_BUFF)
        processes_rect = BackgroundRectangle(processes)
        processes_rect.set_fill(BLACK, 1)

        prob_labels = VGroup(
            TexMobject("P(", "00", ")", "=", "1 / 2"),
            TexMobject("P(", "00", ")", "=", "1 / 6}"),
            TexMobject("P(", "00", ")", "=", "1 / 52}"),
        )
        prob_labels.scale(1.5)
        prob_labels.arrange(DOWN, aligned_edge=LEFT)
        prob_labels.match_x(prob_title)
        for pl, pr in zip(prob_labels, processes):
            pl.match_y(pr)
            content = pr[1].copy()
            content.replace(pl[1], dim_to_match=0)
            pl.replace_submobject(1, content)

        # Putting numbers to the unknown
        number_rects = VGroup(*[
            SurroundingRectangle(pl[-1])
            for pl in prob_labels
        ])
        number_rects.set_stroke(YELLOW, 2)

        for pl in prob_labels:
            pl.save_state()
            pl[:3].match_x(prob_title)
            pl[3:].match_x(prob_title)
            pl.set_opacity(0)

        self.add(processes)
        self.play(
            LaggedStartMap(FadeInFromDown, titles),
            LaggedStart(
                ShowCreation(v_line),
                ShowCreation(h_line),
                lag_ratio=0.1,
            ),
            LaggedStartMap(Restore, prob_labels),
            run_time=1
        )
        self.wait(2)
        # self.play(
        #     LaggedStartMap(
        #         ShowCreationThenFadeOut,
        #         number_rects,
        #         run_time=3,
        #     )
        # )
        # self.wait(2)

        # Highlight coin flip
        fade_rects = VGroup(*[
            VGroup(
                BackgroundRectangle(pl, buff=MED_SMALL_BUFF),
                BackgroundRectangle(pr, buff=MED_SMALL_BUFF),
            )
            for pl, pr in zip(prob_labels, processes)
        ])
        fade_rects.set_fill(BLACK, 0.8)

        prob_half = prob_labels[0]
        half = prob_half[-1]
        half_underline = Line(LEFT, RIGHT)
        half_underline.set_width(half.get_width() + MED_SMALL_BUFF)
        half_underline.next_to(half, DOWN, buff=SMALL_BUFF)
        half_underline.set_stroke(YELLOW, 3)

        self.play(
            FadeIn(fade_rects[1]),
            FadeIn(fade_rects[2]),
        )
        self.wait(2)
        self.play(
            FadeIn(fade_rects[0]),
            FadeOut(fade_rects[1]),
        )
        self.wait(3)
        self.play(
            FadeOut(fade_rects[0]),
            FadeOut(fade_rects[2]),
        )
        self.wait(4)

        # Transition to question
        processes.suspend_updating()
        self.play(
            LaggedStart(
                FadeOutAndShift(unknown_title, UP),
                FadeOutAndShift(prob_title, UP),
                lag_ratio=0.2,
            ),
            FadeOutAndShift(h_line, UP, lag_ratio=0.1),
            FadeOutAndShift(processes, LEFT, lag_ratio=0.1),
            FadeOut(prob_labels[1]),
            FadeOut(prob_labels[2]),
            v_line.rotate, 90 * DEGREES,
            v_line.shift, 0.6 * FRAME_HEIGHT * UP,
            prob_half.center,
            prob_half.to_edge, UP,
            run_time=2,
        )
        self.clear()
        self.add(prob_half)

        arrow = Vector(UP)
        arrow.next_to(half, DOWN)
        question = TextMobject("What exactly does\\\\this mean?")
        question.next_to(arrow, DOWN)

        self.play(
            GrowArrow(arrow),
            FadeInFrom(question, UP),
        )
        self.wait(2)
        self.play(
            FadeOutAndShift(question, RIGHT),
            Rotate(arrow, 90 * DEGREES),
            VFadeOut(arrow),
        )

        # Show long run averages
        self.show_many_coins(20, 50)
        self.show_many_coins(40, 100)

        # Make probability itself unknown
        q_marks = TexMobject("???")
        q_marks.set_color(YELLOW)
        q_marks.replace(half, dim_to_match=0)

        randy = Randolph(mode="confused")
        randy.center()
        randy.look_at(prob_half)

        self.play(
            FadeOutAndShift(half, UP),
            FadeInFrom(q_marks, DOWN),
        )
        self.play(FadeIn(randy))
        self.play(Blink(randy))
        self.wait()

        # self.embed()

    def get_titles(self):
        unknown_label = TextMobject("Random process")
        prob_label = TextMobject("Long-run frequency")
        titles = VGroup(unknown_label, prob_label)
        titles.scale(1.25)

        unknown_label.move_to(FRAME_WIDTH * LEFT / 4)
        prob_label.move_to(FRAME_WIDTH * RIGHT / 4)
        titles.to_edge(UP, buff=MED_SMALL_BUFF)
        titles.set_color(BLUE)
        return titles

    def show_many_coins(self, n_rows, n_cols):
        coin_choices = VGroup(
            get_coin(BLUE_E, "H"),
            get_coin(RED_E, "T"),
        )
        coin_choices.set_stroke(width=0)
        coins = VGroup(*[
            random.choice(coin_choices).copy()
            for x in range(n_rows * n_cols)
        ])

        def organize_coins(coin_group):
            coin_group.scale(1 / coin_group[0].get_height())
            coin_group.arrange_in_grid(n_rows=n_rows)
            coin_group.set_width(FRAME_WIDTH - 1)
            coin_group.to_edge(DOWN, MED_LARGE_BUFF)

        organize_coins(coins)

        sorted_coins = VGroup()
        for coin in coins:
            coin.generate_target()
            sorted_coins.add(coin.target)
        sorted_coins.submobjects.sort(key=lambda m: m.symbol)
        organize_coins(sorted_coins)

        self.play(LaggedStartMap(
            FadeInFrom, coins,
            lambda m: (m, 0.2 * DOWN),
            run_time=3,
            rate_func=linear
        ))
        self.wait()
        self.play(LaggedStartMap(
            MoveToTarget, coins,
            path_arc=30 * DEGREES,
            run_time=2,
            lag_ratio=1 / len(coins),
        ))
        self.wait()
        self.play(FadeOut(coins))


class ComplainAboutSimplisticModel(TeacherStudentsScene):
    def construct(self):
        axes = self.get_experience_graph()

        self.add(axes)
        self.play(
            self.teacher.change, "raise_right_hand", axes,
            self.get_student_changes(
                "pondering", "erm", "sassy",
                look_at_arg=axes,
            ),
            ShowCreation(
                axes.graph,
                run_time=3,
                rate_func=linear,
            ),
        )
        self.wait(2)

        student = self.students[2]
        bubble = SpeechBubble(
            direction=LEFT,
            height=3,
            width=5,
        )
        bubble.pin_to(student)
        bubble.write("What about something\\\\like this?")

        self.play(
            axes.next_to, student, UL,
            VFadeOut(axes.graph),
            FadeIn(bubble),
            Write(bubble.content, run_time=1),
            student.change, "raise_left_hand",
            self.students[0].change, "thinking", axes,
            self.students[1].change, "thinking", axes,
            self.teacher.change, "happy",
        )

        new_graph = VMobject()
        new_graph.set_points_as_corners([
            axes.c2p(0, 0.75),
            axes.c2p(2, 0.9),
            axes.c2p(4, 0.5),
            axes.c2p(6, 0.75),
            axes.c2p(8, 0.55),
            axes.c2p(10, 0.95),
        ])
        new_graph.make_smooth()
        new_graph.set_stroke([YELLOW, RED, GREEN], 2)

        self.play(
            ShowCreation(new_graph),
            *[
                ApplyMethod(pi.look_at, new_graph)
                for pi in self.pi_creatures
            ]
        )
        self.wait(3)

    def get_experience_graph(self):
        axes = Axes(
            x_min=-1,
            x_max=10,
            y_min=0,
            y_max=1.25,
            y_axis_config={
                "unit_size": 5,
                "tick_frequency": 0.25,
                "include_tip": False,
            }
        )
        axes.set_stroke(LIGHT_GREY, 1)
        axes.set_height(3)
        y_label = TextMobject("Experience quality")
        y_label.scale(0.5)
        y_label.next_to(axes.y_axis.get_top(), RIGHT, SMALL_BUFF)
        axes.add(y_label)

        lines = VGroup()
        for x in range(10):
            lines.add(
                Line(axes.c2p(x, 0), axes.c2p(x + 0.9, 0))
            )
        lines.set_stroke(RED, 3)
        for line in lines:
            if random.random() < 0.5:
                line.set_y(axes.c2p(0, 1)[1])
                line.set_stroke(GREEN)

        axes.add(lines)
        axes.graph = lines

        rect = BackgroundRectangle(axes, buff=0.25)
        rect.set_stroke(WHITE, 1)
        rect.set_fill(BLACK, 1)

        axes.add_to_back(rect)
        axes.to_corner(UR)

        return axes


class ComingUpWrapper(Scene):
    def construct(self):
        background = FullScreenFadeRectangle()
        background.set_fill(GREY_E, 1)

        title = TextMobject("What's coming...")
        title.scale(1.5)
        title.to_edge(UP)

        rect = ScreenRectangle()
        rect.set_height(6)
        rect.set_stroke(WHITE)
        rect.set_fill(BLACK, 1)
        rect.next_to(title, DOWN)

        self.add(background, rect)
        self.play(FadeInFromDown(title))
        self.wait()


class PreviewBeta(Scene):
    def construct(self):
        axes = get_beta_dist_axes(label_y=True)
        marks = get_plusses_and_minuses(p=0.75)
        marks.next_to(axes.y_axis.get_top(), DR, buff=0.75)

        beta_label = get_beta_label(0, 0)
        beta_label.next_to(marks, UR, buff=LARGE_BUFF)
        beta_label.to_edge(UP)
        bl_left = beta_label.get_left()

        beta_container = VGroup()
        graph_container = VGroup()
        n_graphs = 2
        for x in range(n_graphs):
            graph_container.add(VMobject())

        def get_counts(marks):
            is_plusses = [m.is_plus for m in marks]
            p = sum(is_plusses)
            n = len(is_plusses) - p
            return p, n

        def update_beta(container):
            counts = get_counts(marks)
            new_label = get_beta_label(*counts)
            new_label.move_to(bl_left, LEFT)
            container.set_submobjects([new_label])
            return container

        def update_graph(container):
            counts = get_counts(marks)
            new_graph = get_beta_graph(axes, *counts)
            new_graphs = [*container[1:], new_graph]
            for g, a in zip(new_graphs, np.linspace(0.2, 1, n_graphs)):
                g.set_opacity(a)

            container.set_submobjects(new_graphs)
            return container

        self.add(axes)
        self.play(
            ShowIncreasingSubsets(marks),
            UpdateFromFunc(
                beta_container,
                update_beta,
            ),
            UpdateFromFunc(
                graph_container,
                update_graph,
            ),
            run_time=15,
            rate_func=bezier([0, 0, 1, 1]),
        )
        self.wait()


class AskInverseQuestion(WhatsTheModel):
    def construct(self):
        self.force_skipping()
        self.introduce_buyer_and_seller()
        self.bs_group = VGroup(
            self.buyer,
            self.seller,
            self.buyer.label,
            self.seller.label,
        )
        self.bs_group.to_edge(DOWN)
        self.revert_to_original_skipping_status()

        self.add_probability_label()
        self.show_many_review_animations()
        self.ask_question()

    def add_probability_label(self):
        label = get_prob_positive_experience_label(True, True, False)
        label.decimal.set_value(0.95)
        label.next_to(self.seller, UP, aligned_edge=LEFT, buff=MED_LARGE_BUFF)

        self.add(label)
        self.probability_label = label

    def show_many_review_animations(self):
        for x in range(7):
            self.play(*self.experience_animations(
                self.seller,
                self.buyer,
                arc=30 * DEGREES,
                p=0.95,
            ))

    def ask_question(self):
        pis = [self.buyer, self.seller]
        labels = VGroup(
            self.get_prob_review_label(10, 0),
            self.get_prob_review_label(48, 2),
            self.get_prob_review_label(184, 16),
        )
        labels.arrange(DOWN)
        labels.to_edge(UP)

        labels[0].save_state()
        labels[0].set_opacity(0)
        words = labels[0][-3:-1]
        words.set_opacity(1)
        words.scale(1.5)
        words.center().to_edge(UP)

        self.play(
            FadeInFromDown(words),
        )
        self.wait()
        self.play(
            Restore(labels[0]),
            *[
                ApplyMethod(pi.change, 'pondering', labels)
                for pi in pis
            ]
        )
        self.play(Blink(pis[0]))
        self.play(Blink(pis[1]))
        self.play(LaggedStartMap(FadeInFromDown, labels[1:]))
        self.wait(2)

        # Succinct
        short_label = TexMobject(
            "P(\\text{data} | s)",
            tex_to_color_map={
                "\\text{data}": LIGHT_GREY,
                "s": YELLOW
            }
        )
        short_label.scale(2)
        short_label.next_to(labels, DOWN, LARGE_BUFF),
        rect = SurroundingRectangle(short_label, buff=MED_SMALL_BUFF)
        bs_group = self.bs_group
        bs_group.add(self.probability_label)

        self.play(
            FadeInFrom(short_label, UP),
            bs_group.scale, 0.5, {"about_edge": DOWN},
        )
        self.play(ShowCreation(rect))
        self.wait()

    def get_prob_review_label(self, n_positive, n_negative):
        label = TexMobject(
            "P(",
            f"{n_positive}\\,{CMARK_TEX}", ",\\,",
            f"{n_negative}\\,{XMARK_TEX}",
            "\\,\\text{ Given that }",
            "s = 0.95",
            ")",
        )
        label.set_color_by_tex_to_color_map({
            CMARK_TEX: GREEN,
            XMARK_TEX: RED,
            "0.95": YELLOW,
        })
        return label


class SimulationsOf10Reviews(Scene):
    CONFIG = {
        "s": 0.95
    }

    def construct(self):
        s_label = TexMobject("s = 0.95")
        s_label.set_height(0.3)
        s_label.to_corner(UL, buff=MED_SMALL_BUFF)
        s_label.set_color(YELLOW)
        self.add(s_label)
        self.camera.frame.shift(LEFT)
        s_label.shift(LEFT)

        np.random.seed(6)
        row = get_random_lt100_row(self.s)
        count = self.get_count(row)
        count.add_updater(
            lambda m: m.set_value(
                sum([s.positive for s in row.syms])
            )
        )

        def update_nums(nums):
            for num in nums:
                num.set_value(np.random.randint(0, 100))

        row.nums.save_state()
        row.nums.set_color(WHITE)
        self.play(
            UpdateFromFunc(row.nums, update_nums),
            run_time=2,
        )
        row.nums.restore()
        self.wait()

        self.add(count)
        self.play(
            ShowIncreasingSubsets(row.syms),
            run_time=2,
            rate_func=linear,
        )
        count.clear_updaters()
        self.wait()

        # Histogram
        data = np.zeros(11)
        histogram = Histogram(
            data,
            bar_colors=[RED, RED, BLUE, GREEN]
        )
        histogram.to_edge(DOWN)

        histogram.axes.y_labels.set_opacity(0)
        histogram.axes.h_lines.set_opacity(0)

        stacks = VGroup()
        for bar in histogram.bars:
            stacks.add(VGroup(bar.copy()))

        def put_into_histogram(row_count_group):
            row, count = row_count_group
            count.clear_updaters()
            index = int(count.get_value())
            stack = stacks[index]

            row.set_width(stack.get_width() - SMALL_BUFF)
            row.next_to(stack, UP, SMALL_BUFF)
            count.replace(histogram.axes.x_labels[index])
            stack.add(row)
            return row_count_group

        self.play(
            FadeIn(histogram),
            ApplyFunction(
                put_into_histogram,
                VGroup(row, count),
            )
        )
        self.wait()
        for x in range(2):
            row = get_random_lt100_row(self.s)
            count = self.get_count(row)
            group = VGroup(row, count)
            self.play(FadeIn(group, lag_ratio=0.2))
            self.wait(0.5)
            self.play(
                ApplyFunction(
                    put_into_histogram,
                    VGroup(row, count),
                )
            )

        for x in range(40):
            row = get_random_lt100_row(self.s)
            count = self.get_count(row)
            lower_group = VGroup(row, count).copy()
            put_into_histogram(lower_group)
            self.add(row, count, lower_group)
            self.wait(0.1)
            self.remove(row, count)

        data = np.array([len(stack) - 1 for stack in stacks])
        self.add(row, count)
        self.play(
            FadeOut(stacks),
            FadeOut(count),
            histogram.bars.become, histogram.get_bars(data),
            histogram.axes.y_labels.set_opacity, 1,
            histogram.axes.h_lines.set_opacity, 1,
            histogram.axes.y_axis.set_opacity, 1,
        )
        self.remove(stacks)

        arrow = Vector(0.5 * DOWN)
        arrow.set_stroke(width=5)
        arrow.set_color(YELLOW)
        arrow.next_to(histogram.bars[10], UP, SMALL_BUFF)

        def update(dummy):
            new_row = get_random_lt100_row(self.s)
            row.become(new_row)
            count = sum([m.positive for m in new_row.nums])
            data[count] += 1
            histogram.bars.become(histogram.get_bars(data))
            arrow.next_to(histogram.bars[count], UP, SMALL_BUFF)

        self.add(arrow)
        self.play(
            UpdateFromFunc(Group(row, arrow, histogram.bars), update),
            run_time=10,
        )

    #
    def get_count(self, row):
        count = Integer()
        count.set_height(0.75)
        count.next_to(row, DOWN, buff=0.65)
        count.set_value(sum([s.positive for s in row.syms]))
        return count


class SimulationsOf50Reviews(Scene):
    CONFIG = {
        "s": 0.95,
        "histogram_config": {
            "x_label_freq": 5,
            "y_axis_numbers_to_show": range(10, 70, 10),
            "y_max": 0.6,
            "y_tick_freq": 0.1,
            "height": 5,
            "bar_colors": [BLUE],
        },
    }

    def construct(self):
        self.add_s_label()

        data = np.zeros(51)
        histogram = self.get_histogram(data)

        row = self.get_row()
        count = self.get_count(row)
        original_count = count.get_value()
        count.set_value(0)

        self.add(histogram)
        self.play(
            ShowIncreasingSubsets(row),
            ChangeDecimalToValue(count, original_count)
        )

        # Run many samples
        arrow = Vector(0.5 * DOWN)
        arrow.set_stroke(width=5)
        arrow.set_color(YELLOW)
        arrow.next_to(histogram.bars[10], UP, SMALL_BUFF)

        total_data_label = VGroup(
            TextMobject("Total samples: "),
            Integer(1),
        )
        total_data_label.arrange(RIGHT)
        total_data_label.next_to(row, DOWN)
        total_data_label.add_updater(
            lambda m: m[1].set_value(data.sum())
        )

        def update(dummy, n_added_data_points=0):
            new_row = self.get_row()
            row.become(new_row)
            num_positive = sum([m.positive for m in new_row])
            count.set_value(num_positive)
            data[num_positive] += 1
            if n_added_data_points:
                values = np.random.random((n_added_data_points, 50))
                counts = (values < self.s).sum(1)
                for i in range(len(data)):
                    data[i] += (counts == i).sum()
            histogram.bars.become(histogram.get_bars(data))
            histogram.bars[48].set_color(YELLOW)
            arrow.next_to(histogram.bars[num_positive], UP, SMALL_BUFF)

        self.add(arrow, total_data_label)
        group = VGroup(histogram.bars, row, count, arrow)
        self.play(
            UpdateFromFunc(group, update),
            run_time=4
        )
        self.play(
            UpdateFromFunc(
                group,
                lambda m: update(m, 1000)
            ),
            run_time=4
        )
        random.seed(0)
        np.random.seed(0)
        update(group)
        self.wait()

        # Show 48 bar
        axes = histogram.axes
        y = choose(50, 48) * (self.s)**48 * (1 - self.s)**2
        line = DashedLine(
            axes.c2p(0, y),
            axes.c2p(51, y),
        )
        label = TexMobject("{:.1f}\\%".format(100 * y))
        fix_percent(label.family_members_with_points()[-1])
        label.next_to(line, RIGHT)

        self.play(
            ShowCreation(line),
            FadeInFromPoint(label, line.get_start())
        )

    def add_s_label(self):
        s_label = TexMobject("s = 0.95")
        s_label.set_height(0.3)
        s_label.to_corner(UL, buff=MED_SMALL_BUFF)
        s_label.shift(0.8 * DOWN)
        s_label.set_color(YELLOW)
        self.add(s_label)

    def get_histogram(self, data):
        histogram = Histogram(
            data, **self.histogram_config
        )
        histogram.to_edge(DOWN)
        return histogram

    def get_row(self):
        row = get_random_checks_and_crosses(50, self.s)
        row.to_edge(UP)
        return row

    def get_count(self, row):
        count = Integer(sum([m.positive for m in row]))
        count.set_height(0.3)
        count.next_to(row, RIGHT)
        return count


class ShowBinomialFormula(SimulationsOf50Reviews):
    CONFIG = {
        "histogram_config": {
            "x_label_freq": 5,
            "y_axis_numbers_to_show": range(10, 40, 10),
            "y_max": 0.3,
            "y_tick_freq": 0.1,
            "height": 2.5,
            "bar_colors": [BLUE],
        },
        "random_seed": 0,
    }

    def construct(self):
        dist = scipy.stats.binom(50, self.s)
        data = np.array([
            dist.pmf(x)
            for x in range(0, 51)
        ])
        histogram = self.get_histogram(data)
        histogram.bars[48].set_color(YELLOW)
        self.add(histogram)

        row = self.get_row()
        count = self.get_count(row)
        self.add(row, count)

        # Formula
        prob_label = get_prob_review_label(48, 2)
        eq = TexMobject("=")
        formula = TexMobject(
            "{50 \\choose 48}",
            "(0.95)", "^{48}",
            "(1 - 0.95)", "^{2}",
        )
        formula[0][-3:-1].set_color(GREEN)
        formula[2].set_color(GREEN)
        formula.set_color_by_tex_to_color_map({
            "2": RED,
            "0.95": YELLOW,
        })

        equation = VGroup(
            prob_label,
            eq,
            formula,
        )
        equation.arrange(RIGHT)
        equation.next_to(histogram, UP, LARGE_BUFF)
        equation.to_edge(RIGHT)

        prob_label.save_state()
        arrow = Vector(DOWN)
        arrow.next_to(histogram.bars[48], UP, SMALL_BUFF)
        prob_label.next_to(arrow, UP)

        self.play(
            FadeIn(prob_label),
            GrowArrow(arrow),
        )
        for mob in prob_label[1::2]:
            line = Underline(mob)
            line.match_color(mob)
            self.play(ShowCreationThenDestruction(line))
            self.wait(0.5)
        self.play(
            Restore(prob_label),
            FadeIn(equation[1:], lag_ratio=0.1),
        )
        self.wait()

        # Talk through n choose k term

        self.embed()
