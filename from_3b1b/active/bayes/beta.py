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
        axes.y_axis.remove(axes.y_axis.numbers)
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
        "random_seed": 1,
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
            histogram.bars.set_fill(GREY_C)
            histogram.bars[48].set_fill(GREEN)
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

    def get_row(self, n=50):
        row = get_random_checks_and_crosses(n, self.s)
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
        # Add histogram
        dist = scipy.stats.binom(50, self.s)
        data = np.array([
            dist.pmf(x)
            for x in range(0, 51)
        ])
        histogram = self.get_histogram(data)
        histogram.bars.set_fill(GREY_C)
        histogram.bars[48].set_fill(GREEN)
        self.add(histogram)

        row = self.get_row()
        self.add(row)

        # Formula
        prob_label = get_prob_review_label(48, 2)
        eq = TexMobject("=")
        formula = get_binomial_formula(50, 48, self.s)

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

        self.explain_n_choose_k(row, formula)

        # Circle formula parts
        rect1 = SurroundingRectangle(formula[4:8])
        rect2 = SurroundingRectangle(formula[8:])
        rect1.set_stroke(GREEN, 2)
        rect2.set_stroke(RED, 2)

        for rect in rect1, rect2:
            self.play(ShowCreation(rect))
            self.wait()
            self.play(FadeOut(rect))

        # Show numerical answer
        eq2 = TexMobject("=")
        value = DecimalNumber(dist.pmf(48), num_decimal_places=5)
        rhs = VGroup(eq2, value)
        rhs.arrange(RIGHT)
        rhs.match_y(eq)
        rhs.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        self.play(
            FadeInFrom(value, LEFT),
            FadeIn(eq2),
            equation.next_to, eq2, LEFT,
        )
        self.wait()

        # Show alternate values of k
        n = 50
        for k in it.chain(range(47, 42, -1), range(43, 51), [49, 48]):
            new_prob_label = get_prob_review_label(k, n - k)
            new_prob_label.replace(prob_label)
            prob_label.become(new_prob_label)
            new_formula = get_binomial_formula(n, k, self.s)
            new_formula.replace(formula)
            formula.set_submobjects(new_formula)

            value.set_value(dist.pmf(k))
            histogram.bars.set_fill(LIGHT_GREY)
            histogram.bars[k].set_fill(GREEN)
            arrow.next_to(histogram.bars[k], UP, SMALL_BUFF)

            new_row = get_checks_and_crosses((n - k) * [False] + k * [True])
            new_row.replace(row)
            row.become(new_row)
            self.wait(0.5)

        # Name it as the Binomial distribution
        long_equation = VGroup(prob_label, eq, formula, eq2, value)
        bin_name = TextMobject("Binomial", " Distribution")
        bin_name.scale(1.5)
        bin_name.next_to(histogram, UP, MED_LARGE_BUFF)

        underline = Underline(bin_name[0])
        underline.set_stroke(PINK, 2)
        nck_rect = SurroundingRectangle(formula[:4])
        nck_rect.set_stroke(PINK, 2)

        self.play(
            long_equation.next_to, self.slots, DOWN, MED_LARGE_BUFF,
            long_equation.to_edge, RIGHT,
            FadeInFrom(bin_name, DOWN),
        )
        self.wait()
        self.play(ShowCreationThenDestruction(underline))
        self.wait()
        bools = [True] * 50
        bools[random.randint(0, 49)] = False
        bools[random.randint(0, 49)] = False
        row.become(get_checks_and_crosses(bools).replace(row))
        self.play(ShowIncreasingSubsets(row, run_time=4))
        self.wait()

        # Show likelihood and posterior labels
        likelihood_label = TexMobject(
            "P(",
            "\\text{data}", "\\,|\\,",
            "\\text{success rate}",
            ")",
        )
        posterior_label = TexMobject(
            "P(",
            "\\text{success rate}",
            "\\,|\\,",
            "\\text{data}",
            ")",
        )
        for label in (likelihood_label, posterior_label):
            label.set_color_by_tex_to_color_map({
                "data": GREEN,
                "success": YELLOW,
            })

        likelihood_label.next_to(
            prob_label, DOWN, LARGE_BUFF, aligned_edge=LEFT
        )

        right_arrow = Vector(RIGHT)
        right_arrow.next_to(likelihood_label, RIGHT)
        ra_label = TextMobject("But we want")
        ra_label.match_width(right_arrow)
        ra_label.next_to(right_arrow, UP, SMALL_BUFF)
        posterior_label.next_to(right_arrow, RIGHT)

        self.play(
            FadeInFrom(likelihood_label, UP),
            bin_name.set_height, 0.4,
            bin_name.set_y, histogram.axes.c2p(0, .25)[1]
        )
        self.wait()
        self.play(
            GrowArrow(right_arrow),
            FadeInFrom(ra_label, 0.5 * LEFT),
        )
        anims = []
        for i, j in enumerate([0, 3, 2, 1, 4]):
            anims.append(
                TransformFromCopy(
                    likelihood_label[i],
                    posterior_label[j],
                    path_arc=-45 * DEGREES,
                    run_time=2,
                )
            )
        self.play(*anims)
        self.add(posterior_label)
        self.wait()

        # Prepare for new plot
        histogram.add(bin_name)
        always(arrow.next_to, histogram.bars[48], UP, SMALL_BUFF)
        self.play(
            FadeOut(likelihood_label),
            FadeOut(posterior_label),
            FadeOut(right_arrow),
            FadeOut(ra_label),
            FadeOutAndShift(row, UP),
            FadeOutAndShift(self.slots, UP),
            histogram.scale, 0.7,
            histogram.to_edge, UP,
            arrow.scale, 0.5,
            arrow.set_stroke, None, 4,
            long_equation.center,
            run_time=1.5,
        )
        self.add(arrow)

        # x_labels = histogram.axes.x_labels
        # underline = Underline(x_labels)
        # underline.set_stroke(GREEN, 3)
        # self.play(
        #     LaggedStartMap(
        #         ApplyFunction, x_labels,
        #         lambda mob: (
        #             lambda m: m.scale(1.5).set_color(GREEN),
        #             mob,
        #         ),
        #         rate_func=there_and_back,
        #     ),
        #     ShowCreationThenDestruction(underline),
        # )
        # num_checks = TexMobject("\\# " + CMARK_TEX)
        # num_checks.set_color(GREEN)
        # num_checks.next_to(
        #     x_labels, RIGHT,
        #     MED_LARGE_BUFF,
        #     aligned_edge=DOWN,
        # )
        # self.play(Write(num_checks))
        # self.wait()

        low_axes = get_beta_dist_axes(y_max=0.3, y_unit=0.1, label_y=False)
        low_axes.y_axis.set_height(
            2,
            about_point=low_axes.c2p(0, 0),
            stretch=True,
        )
        low_axes.to_edge(DOWN)
        low_axes.x_axis.numbers.set_color(YELLOW)
        y_label_copies = histogram.axes.y_labels.copy()
        y_label_copies.set_height(0.6 * low_axes.get_height())
        y_label_copies.next_to(low_axes, LEFT, 0, aligned_edge=UP)
        y_label_copies.shift(SMALL_BUFF * UP)
        low_axes.y_axis.add(y_label_copies)
        low_axes.y_axis.set_opacity(0)

        # Show alternate values of s
        s_tracker = ValueTracker(self.s)

        s_tip = ArrowTip(start_angle=-90 * DEGREES)
        s_tip.set_color(YELLOW)
        s_tip.axis = low_axes.x_axis
        s_tip.st = s_tracker
        s_tip.add_updater(
            lambda m: m.next_to(m.axis.n2p(m.st.get_value()), UP, buff=0)
        )

        pl_decimal = DecimalNumber(self.s)
        pl_decimal.set_color(YELLOW)
        pl_decimal.replace(prob_label[-2][2:])
        prob_label[-2][2:].set_opacity(0)

        s_label = VGroup(prob_label[-2][:2], pl_decimal).copy()
        sl_rect = SurroundingRectangle(s_label)
        sl_rect.set_stroke(YELLOW, 2)

        self.add(pl_decimal)
        self.play(
            ShowCreation(sl_rect),
            Write(low_axes),
        )
        self.play(
            s_label.next_to, s_tip, UP, 0.2, ORIGIN, s_label[1],
            ReplacementTransform(sl_rect, s_tip)
        )
        always(s_label.next_to, s_tip, UP, 0.2, ORIGIN, s_label[1])

        decimals = VGroup(pl_decimal, s_label[1], formula[5], formula[9])
        decimals.s_tracker = s_tracker

        histogram.s_tracker = s_tracker
        histogram.n = n
        histogram.rhs_value = value

        def update_decimals(decs):
            for dec in decs:
                dec.set_value(decs.s_tracker.get_value())

        def update_histogram(hist):
            new_dist = scipy.stats.binom(hist.n, hist.s_tracker.get_value())
            new_data = np.array([
                new_dist.pmf(x)
                for x in range(0, 51)
            ])
            new_bars = hist.get_bars(new_data)
            new_bars.match_style(hist.bars)
            hist.bars.become(new_bars)
            hist.rhs_value.set_value(new_dist.pmf(48))

        bar_copy = histogram.bars[48].copy()
        value.initial_config["num_decimal_places"] = 2
        value.set_value(value.get_value())
        bar_copy.next_to(value, RIGHT, aligned_edge=DOWN)
        bar_copy.add_updater(
            lambda m: m.set_height(
                max(
                    histogram.bars[48].get_height() * 0.75,
                    1e-6,
                ),
                stretch=True,
                about_edge=DOWN,
            )
        )
        self.add(bar_copy)

        self.add(histogram)
        self.add(decimals)
        for s in [0.95, 0.5, 0.99, 0.9]:
            self.play(
                s_tracker.set_value, s,
                UpdateFromFunc(decimals, update_decimals),
                UpdateFromFunc(histogram, update_histogram),
                UpdateFromFunc(value, lambda m: m),
                UpdateFromFunc(s_label, lambda m: m.update),
                run_time=5,
            )
            self.wait()

        # Plot
        def func(x):
            return scipy.stats.binom(50, x).pmf(48) + 1e-5
        graph = low_axes.get_graph(func, step_size=0.05)
        graph.set_stroke(BLUE, 3)

        v_line = Line(DOWN, UP)
        v_line.axes = low_axes
        v_line.st = s_tracker
        v_line.graph = graph
        v_line.add_updater(
            lambda m: m.put_start_and_end_on(
                m.axes.c2p(m.st.get_value(), 0),
                m.axes.input_to_graph_point(
                    m.st.get_value(),
                    m.graph,
                ),
            )
        )
        v_line.set_stroke(GREEN, 2)
        dot = Dot()
        dot.line = v_line
        dot.set_height(0.05)
        dot.add_updater(lambda m: m.move_to(m.line.get_end()))

        self.play(
            ApplyMethod(
                histogram.bars[48].stretch, 2, 1, {"about_edge": DOWN},
                rate_func=there_and_back,
                run_time=2,
            ),
        )
        self.wait()
        self.play(low_axes.y_axis.set_opacity, 1)
        self.play(
            FadeIn(graph),
            FadeOut(s_label),
            FadeOut(s_tip),
        )
        self.play(
            TransformFromCopy(histogram.bars[48], v_line),
            FadeIn(dot),
        )

        self.add(histogram)
        decimals.remove(decimals[1])
        for s in [0.9, 0.96, 1, 0.8, 0.96]:
            self.play(
                s_tracker.set_value, s,
                UpdateFromFunc(decimals, update_decimals),
                UpdateFromFunc(histogram, update_histogram),
                UpdateFromFunc(value, lambda m: m),
                run_time=5,
            )
            self.wait()

    def explain_n_choose_k(self, row, formula):
        row.add_updater(lambda m: m)

        brace = Brace(formula[:4], UP, buff=SMALL_BUFF)
        words = brace.get_text("``50 choose 48''")

        slots = self.slots = VGroup()
        for sym in row:
            line = Underline(sym)
            line.scale(0.9)
            slots.add(line)
        for slot in slots:
            slot.match_y(slots[0])

        formula[1].counted = slots
        k_rect = SurroundingRectangle(formula[2])
        k_rect.set_stroke(GREEN, 2)

        checks = VGroup()
        for sym in row:
            if sym.positive:
                checks.add(sym)

        self.play(
            GrowFromCenter(brace),
            FadeInFromDown(words),
        )
        self.wait()
        self.play(FadeOut(words))
        formula.save_state()
        self.play(
            ShowIncreasingSubsets(slots),
            UpdateFromFunc(
                formula[1],
                lambda m: m.set_value(len(m.counted))
            ),
            run_time=2,
        )
        formula.restore()
        self.add(formula)
        self.wait()
        self.play(
            LaggedStartMap(
                ApplyMethod, checks,
                lambda m: (m.shift, 0.3 * DOWN),
                rate_func=there_and_back,
                lag_ratio=0.05,
            ),
            ShowCreationThenFadeOut(k_rect),
            run_time=2,
        )
        self.remove(checks)
        self.add(row)
        self.wait()

        # Example orderings
        row_target = VGroup()
        for sym in row:
            sym.generate_target()
            row_target.add(sym.target)

        row_target.sort(submob_func=lambda m: -int(m.positive))
        row_target.arrange(
            RIGHT, buff=get_norm(row[0].get_right() - row[1].get_left())
        )
        row_target.move_to(row)
        self.play(
            LaggedStartMap(
                MoveToTarget, row,
                path_arc=30 * DEGREES,
                lag_ratio=0,
            ),
        )
        self.wait()
        row.sort()
        self.play(Swap(*row[-3:-1]))
        self.add(row)
        self.wait()

        # All orderings
        nck_count = Integer(2)
        nck_count.next_to(brace, UP)
        nck_top = nck_count.get_top()
        always(nck_count.move_to, nck_top, UP)

        combs = list(it.combinations(range(50), 48))
        bool_lists = [
            [i in comb for i in range(50)]
            for comb in combs
        ]
        row.counter = nck_count
        row.bool_lists = bool_lists

        def update_row(r):
            i = r.counter.get_value() - 1
            new_row = get_checks_and_crosses(r.bool_lists[i])
            new_row.replace(r, dim_to_match=0)
            r.set_submobjects(new_row)

        row.add_updater(update_row)
        self.add(row)
        self.play(
            ChangeDecimalToValue(nck_count, choose(50, 48)),
            run_time=10,
        )
        row.clear_updaters()
        self.wait()
        self.play(
            FadeOut(nck_count),
            FadeOut(brace),
        )


class WriteLikelihoodFunction(Scene):
    def construct(self):
        formula = TexMobject(
            "f({s}) = (\\text{const.})",
            "{s}^{\\#" + CMARK_TEX + "}",
            "(1 - {s})^{\\#" + XMARK_TEX, "}",
            tex_to_color_map={
                "{s}": YELLOW,
                "\\#" + CMARK_TEX: GREEN,
                "\\#" + XMARK_TEX: RED,
            }
        )
        formula.scale(2)

        rect1 = SurroundingRectangle(formula[3:6])
        rect2 = SurroundingRectangle(formula[6:])

        self.play(FadeInFromDown(formula))
        self.wait()
        self.play(ShowCreationThenFadeOut(rect1))
        self.wait()
        self.play(ShowCreationThenFadeOut(rect2))
        self.wait()

        self.add(formula)
        self.embed()


class LikelihoodGraphFor10of10(ShowBinomialFormula):
    CONFIG = {
        "histogram_config": {
            "x_label_freq": 2,
            "y_axis_numbers_to_show": range(25, 125, 25),
            "y_max": 1,
            "y_tick_freq": 0.25,
            "height": 2,
            "bar_colors": [BLUE],
        },
    }

    def construct(self):
        # Add histogram
        dist = scipy.stats.binom(10, self.s)
        data = np.array([
            dist.pmf(x)
            for x in range(0, 11)
        ])
        histogram = self.get_histogram(data)
        histogram.bars.set_fill(GREY_C)
        histogram.bars[10].set_fill(GREEN)
        histogram.to_edge(UP)

        x_label = TexMobject("\\#" + CMARK_TEX)
        x_label.set_color(GREEN)
        x_label.next_to(histogram.axes.x_axis.get_end(), RIGHT)
        histogram.add(x_label)
        self.add(histogram)

        # Add formula
        prob_label = get_prob_review_label(10, 0)
        eq = TexMobject("=")
        formula = get_binomial_formula(10, 10, self.s)
        eq2 = TexMobject("=")
        value = DecimalNumber(dist.pmf(10), num_decimal_places=2)

        equation = VGroup(prob_label, eq, formula, eq2, value)
        equation.arrange(RIGHT)
        equation.next_to(histogram, DOWN, MED_LARGE_BUFF)

        arrow = Vector(DOWN)
        arrow.next_to(histogram.bars[10], UP, SMALL_BUFF)

        self.add(equation)
        self.add(arrow)

        # Add lower axes
        low_axes = get_beta_dist_axes(y_max=1, y_unit=0.25, label_y=False)
        low_axes.y_axis.set_height(
            2,
            about_point=low_axes.c2p(0, 0),
            stretch=True,
        )
        low_axes.to_edge(DOWN)
        low_axes.x_axis.numbers.set_color(YELLOW)
        y_label_copies = histogram.axes.y_labels.copy()
        y_label_copies.set_height(0.7 * low_axes.get_height())
        y_label_copies.next_to(low_axes, LEFT, 0, aligned_edge=UP)
        y_label_copies.shift(SMALL_BUFF * UP)
        low_axes.y_axis.add(y_label_copies)

        self.add(low_axes)

        # Add lower plot
        s_tracker = ValueTracker(self.s)

        def func(x):
            return x**10
        graph = low_axes.get_graph(func, step_size=0.05)
        graph.set_stroke(BLUE, 3)

        v_line = Line(DOWN, UP)
        v_line.axes = low_axes
        v_line.st = s_tracker
        v_line.graph = graph
        v_line.add_updater(
            lambda m: m.put_start_and_end_on(
                m.axes.c2p(m.st.get_value(), 0),
                m.axes.input_to_graph_point(
                    m.st.get_value(),
                    m.graph,
                ),
            )
        )
        v_line.set_stroke(GREEN, 2)
        dot = Dot()
        dot.line = v_line
        dot.set_height(0.05)
        dot.add_updater(lambda m: m.move_to(m.line.get_end()))

        self.add(graph, v_line, dot)

        # Show simpler formula
        brace = Brace(formula, DOWN, buff=SMALL_BUFF)
        simpler_formula = TexMobject("s", "^{10}")
        simpler_formula.set_color_by_tex("s", YELLOW)
        simpler_formula.set_color_by_tex("10", GREEN)
        simpler_formula.next_to(brace, DOWN)

        rects = VGroup(
            BackgroundRectangle(formula[:4]),
            BackgroundRectangle(formula[8:]),
        )
        rects.set_opacity(0.75)

        self.wait()
        self.play(FadeIn(rects))
        self.play(
            GrowFromCenter(brace),
            FadeInFrom(simpler_formula, UP)
        )
        self.wait()

        # Show various values of s
        pl_decimal = DecimalNumber(self.s)
        pl_decimal.set_color(YELLOW)
        pl_decimal.replace(prob_label[-2][2:])
        prob_label[-2][2:].set_opacity(0)

        decimals = VGroup(pl_decimal, formula[5], formula[9])
        decimals.s_tracker = s_tracker

        histogram.s_tracker = s_tracker
        histogram.n = 10
        histogram.rhs_value = value

        def update_decimals(decs):
            for dec in decs:
                dec.set_value(decs.s_tracker.get_value())

        def update_histogram(hist):
            new_dist = scipy.stats.binom(hist.n, hist.s_tracker.get_value())
            new_data = np.array([
                new_dist.pmf(x)
                for x in range(0, 11)
            ])
            new_bars = hist.get_bars(new_data)
            new_bars.match_style(hist.bars)
            hist.bars.become(new_bars)
            hist.rhs_value.set_value(new_dist.pmf(10))

        self.add(histogram)
        self.add(decimals, rects)
        always(arrow.next_to, histogram.bars[10], UP, SMALL_BUFF)
        for s in [0.8, 1]:
            self.play(
                s_tracker.set_value, s,
                UpdateFromFunc(decimals, update_decimals),
                UpdateFromFunc(histogram, update_histogram),
                UpdateFromFunc(value, lambda m: m),
                run_time=5,
            )
            self.wait()


class StateNeedForBayesRule(TeacherStudentsScene):
    def construct(self):
        axes = get_beta_dist_axes(y_max=1, y_unit=0.25, label_y=False)
        axes.y_axis.set_height(
            2,
            about_point=axes.c2p(0, 0),
            stretch=True,
        )
        axes.set_width(5)
        graph = axes.get_graph(lambda x: x**10)
        graph.set_stroke(BLUE, 3)
        alt_graph = graph.copy()
        alt_graph.add_line_to(axes.c2p(1, 0))
        alt_graph.add_line_to(axes.c2p(0, 0))
        alt_graph.set_stroke(width=0)
        alt_graph.set_fill(BLUE_E, 1)

        plot = VGroup(axes, alt_graph, graph)

        student0, student1, student2 = self.students
        plot.next_to(student2.get_corner(UL), UP, MED_LARGE_BUFF)
        plot.shift(LEFT)

        v_lines = VGroup(
            DashedLine(axes.c2p(0.8, 0), axes.c2p(0.8, 1)),
            DashedLine(axes.c2p(1, 0), axes.c2p(1, 1)),
        )
        v_lines.set_stroke(YELLOW, 2)

        self.play(
            LaggedStart(
                ApplyMethod(student0.change, "pondering", plot),
                ApplyMethod(student1.change, "pondering", plot),
                ApplyMethod(student2.change, "raise_left_hand", plot),
            ),
            FadeInFrom(plot, DOWN),
            run_time=1.5
        )
        self.play(*map(ShowCreation, v_lines))
        self.play(
            self.teacher.change, "tease",
            *[
                ApplyMethod(
                    v_line.move_to,
                    axes.c2p(0.9, 0),
                    DOWN,
                )
                for v_line in v_lines
            ]
        )
        self.change_student_modes(
            "thinking", "thinking", "pondering",
            look_at_arg=v_lines,
        )
        self.wait(3)

        self.teacher_says(
            "First we need\\\\Bayes' rule",
            added_anims=[
                FadeOutAndShift(plot, LEFT),
                FadeOutAndShift(v_lines, LEFT),
                self.get_student_changes(
                    "pondering", "thinking", "pondering",
                    look_at_arg=self.teacher.eyes,
                )
            ]
        )
        self.change_all_student_modes("hooray")
        self.wait(2)


class ShowBayesRule(Scene):
    def construct(self):
        hyp = "\\text{Hypothesis}"
        data = "\\text{Data}"
        bayes = TexMobject(
            f"P({hyp} \\,|\\, {data})", "=", "{",
            f"P({data} \\,|\\, {hyp})", f"P({hyp})",
            "\\over", f"P({data})",
            tex_to_color_map={
                hyp: YELLOW,
                data: GREEN,
            }
        )

        title = TextMobject("Bayes' rule")
        title.scale(2)
        title.to_edge(UP)

        self.add(title)
        self.add(*bayes[:5])
        self.wait()
        self.play(
            *[
                TransformFromCopy(bayes[i], bayes[j], path_arc=30 * DEGREES)
                for i, j in [
                    (0, 7),
                    (1, 10),
                    (2, 9),
                    (3, 8),
                    (4, 11),
                ]
            ],
            FadeIn(bayes[5]),
            run_time=1.5
        )
        self.wait()
        self.play(
            *[
                TransformFromCopy(bayes[i], bayes[j], path_arc=30 * DEGREES)
                for i, j in [
                    (0, 12),
                    (1, 13),
                    (4, 14),
                    (0, 16),
                    (3, 17),
                    (4, 18),
                ]
            ],
            FadeIn(bayes[15]),
            run_time=1.5
        )
        self.add(bayes)
        self.wait()

        hyp_word = bayes.get_part_by_tex(hyp)
        example_hyp = TextMobject(
            "For example,\\\\",
            "$0.9 < s < 0.99$",
        )
        example_hyp[1].set_color(YELLOW)
        example_hyp.next_to(hyp_word, DOWN, buff=1.5)

        data_word = bayes.get_part_by_tex(data)
        example_data = TexMobject(
            "48\\,", CMARK_TEX,
            "\\,2\\,", XMARK_TEX,
        )
        example_data.set_color_by_tex(CMARK_TEX, GREEN)
        example_data.set_color_by_tex(XMARK_TEX, RED)
        example_data.scale(1.5)
        example_data.next_to(example_hyp, RIGHT, buff=1.5)

        hyp_arrow = Arrow(
            hyp_word.get_bottom(),
            example_hyp.get_top(),
        )
        data_arrow = Arrow(
            data_word.get_bottom(),
            example_data.get_top(),
        )

        self.play(
            GrowArrow(hyp_arrow),
            FadeInFromPoint(example_hyp, hyp_word.get_center()),
        )
        self.wait()
        self.play(
            GrowArrow(data_arrow),
            FadeInFromPoint(example_data, data_word.get_center()),
        )
        self.wait()


class VisualizeBayesRule(Scene):
    def construct(self):
        self.show_continuum()
        self.show_arrows()
        self.show_discrete_probabilities()
        self.show_bayes_formula()
        self.parallel_universes()
        self.update_from_data()

    def show_continuum(self):
        axes = get_beta_dist_axes(y_max=1, y_unit=0.1)
        axes.y_axis.add_numbers(
            *np.arange(0.2, 1.2, 0.2),
            number_config={
                "num_decimal_places": 1,
            }
        )

        p_label = TexMobject(
            "P(s \\,|\\, \\text{data})",
            tex_to_color_map={
                "s": YELLOW,
                "\\text{data}": GREEN,
            }
        )
        p_label.scale(1.5)
        p_label.to_edge(UP, LARGE_BUFF)

        s_part = p_label.get_part_by_tex("s").copy()
        x_line = Line(axes.c2p(0, 0), axes.c2p(1, 0))
        x_line.set_stroke(YELLOW, 3)

        arrow = Vector(DOWN)
        arrow.next_to(s_part, DOWN, SMALL_BUFF)
        value = DecimalNumber(0, num_decimal_places=4)
        value.set_color(YELLOW)
        value.next_to(arrow, DOWN)

        self.add(axes)
        self.add(p_label)
        self.play(
            s_part.next_to, x_line.get_start(), UR, SMALL_BUFF,
            GrowArrow(arrow),
            FadeInFromPoint(value, s_part.get_center()),
        )

        s_part.tracked = x_line
        value.tracked = x_line
        value.x_axis = axes.x_axis
        self.play(
            ShowCreation(x_line),
            UpdateFromFunc(
                s_part,
                lambda m: m.next_to(m.tracked.get_end(), UR, SMALL_BUFF)
            ),
            UpdateFromFunc(
                value,
                lambda m: m.set_value(
                    m.x_axis.p2n(m.tracked.get_end())
                )
            ),
            run_time=3,
        )
        self.wait()
        self.play(
            FadeOut(arrow),
            FadeOut(value),
        )

        self.p_label = p_label
        self.s_part = s_part
        self.value = value
        self.x_line = x_line
        self.axes = axes

    def show_arrows(self):
        axes = self.axes

        arrows = VGroup()
        arrow_template = Vector(DOWN)
        arrow_template.lock_triangulation()

        def get_arrow(s, denom):
            arrow = arrow_template.copy()
            arrow.set_height(4 / denom)
            arrow.move_to(axes.c2p(s, 0), DOWN)
            arrow.set_color(interpolate_color(
                GREY_A, GREY_C, random.random()
            ))
            return arrow

        for k in range(2, 50):
            for n in range(1, k):
                if np.gcd(n, k) != 1:
                    continue
                s = n / k
                arrows.add(get_arrow(s, k))
        for k in range(50, 1000):
            arrows.add(get_arrow(1 / k, k))
            arrows.add(get_arrow(1 - 1 / k, k))

        kw = {
            "lag_ratio": 0.5,
            "run_time": 5,
            "rate_func": lambda t: t**4,
        }
        arrows.save_state()
        for arrow in arrows:
            arrow.stretch(0, 0)
            arrow.set_stroke(width=0)
            arrow.set_opacity(0)
        self.play(Restore(arrows, **kw))
        self.play(LaggedStartMap(
            ApplyMethod, arrows,
            lambda m: (m.scale, 0, {"about_edge": DOWN}),
            **kw
        ))
        self.remove(arrows)
        self.wait()

    def show_discrete_probabilities(self):
        axes = self.axes

        x_lines = VGroup()
        dx = 0.01
        for x in np.arange(0, 1, dx):
            line = Line(
                axes.c2p(x, 0),
                axes.c2p(x + dx, 0),
            )
            line.set_stroke(BLUE, 3)
            line.generate_target()
            line.target.rotate(
                90 * DEGREES,
                about_point=line.get_start()
            )
            x_lines.add(line)

        self.add(x_lines)
        self.play(
            FadeOut(self.x_line),
            LaggedStartMap(
                MoveToTarget, x_lines,
            )
        )

        label = Integer(0)
        label.set_height(0.5)
        label.next_to(self.p_label[1], DOWN, LARGE_BUFF)
        unit = TexMobject("\\%")
        unit.match_height(label)
        fix_percent(unit.family_members_with_points()[0])
        always(unit.next_to, label, RIGHT, SMALL_BUFF)

        arrow = Arrow()
        arrow.max_stroke_width_to_length_ratio = 1
        arrow.axes = axes
        arrow.label = label
        arrow.add_updater(lambda m: m.put_start_and_end_on(
            m.label.get_bottom() + MED_SMALL_BUFF * DOWN,
            m.axes.c2p(0.01 * m.label.get_value(), 0.03),
        ))

        self.add(label, unit, arrow)
        self.play(
            ChangeDecimalToValue(label, 99),
            run_time=5,
        )
        self.wait()
        self.play(*map(FadeOut, [label, unit, arrow]))

        # Show prior label
        p_label = self.p_label
        given_data = p_label[2:4]
        prior_label = TexMobject("P(s)", tex_to_color_map={"s": YELLOW})
        prior_label.match_height(p_label)
        prior_label.move_to(p_label, DOWN, LARGE_BUFF)

        p_label.save_state()
        self.play(
            given_data.scale, 0.5,
            given_data.set_opacity, 0.5,
            given_data.to_corner, UR,
            Transform(p_label[:2], prior_label[:2]),
            Transform(p_label[-1], prior_label[-1]),
        )
        self.wait()

        # Zoom in on the y-values
        new_ticks = VGroup()
        new_labels = VGroup()
        dy = 0.01
        for y in np.arange(dy, 5 * dy, dy):
            height = get_norm(axes.c2p(0, dy) - axes.c2p(0, 0))
            tick = axes.y_axis.get_tick(y, SMALL_BUFF)
            label = DecimalNumber(y)
            label.match_height(axes.y_axis.numbers[0])
            always(label.next_to, tick, LEFT, SMALL_BUFF)

            new_ticks.add(tick)
            new_labels.add(label)

        for num in axes.y_axis.numbers:
            height = num.get_height()
            always(num.set_height, height, stretch=True)

        bars = VGroup()
        dx = 0.01
        origin = axes.c2p(0, 0)
        for x in np.arange(0, 1, dx):
            rect = Rectangle(
                width=get_norm(axes.c2p(dx, 0) - origin),
                height=get_norm(axes.c2p(0, dy) - origin),
            )
            rect.x = x
            rect.set_stroke(BLUE, 1)
            rect.set_fill(BLUE, 0.5)
            rect.move_to(axes.c2p(x, 0), DL)
            bars.add(rect)

        stretch_group = VGroup(
            axes.y_axis,
            bars,
            new_ticks,
            x_lines,
        )
        x_lines.set_height(
            bars.get_height(),
            about_edge=DOWN,
            stretch=True,
        )

        self.play(
            stretch_group.stretch, 25, 1, {"about_point": axes.c2p(0, 0)},
            VFadeIn(bars),
            VFadeIn(new_ticks),
            VFadeIn(new_labels),
            VFadeOut(x_lines),
            run_time=4,
        )

        highlighted_bars = bars.copy()
        highlighted_bars.set_color(YELLOW)
        self.play(
            LaggedStartMap(
                FadeIn, highlighted_bars,
                lag_ratio=0.5,
                rate_func=there_and_back,
            ),
            ShowCreationThenFadeAround(new_labels[0]),
            run_time=3,
        )
        self.remove(highlighted_bars)

        # Nmae as prior
        prior_name = TextMobject("Prior", " distribution")
        prior_name.set_height(0.6)
        prior_name.next_to(prior_label, DOWN, LARGE_BUFF)

        self.play(FadeInFromDown(prior_name))
        self.wait()

        # Show alternate distribution
        bars.save_state()
        for a, b in [(5, 2), (1, 6)]:
            dist = scipy.stats.beta(a, b)
            for bar, saved in zip(bars, bars.saved_state):
                bar.target = saved.copy()
                height = get_norm(axes.c2p(0.1 * dist.pdf(bar.x)) - axes.c2p(0, 0))
                bar.target.set_height(height, about_edge=DOWN, stretch=True)

            self.play(LaggedStartMap(MoveToTarget, bars, lag_ratio=0.00))
            self.wait()
        self.play(Restore(bars))
        self.wait()

        uniform_name = TextMobject("Uniform")
        uniform_name.match_height(prior_name)
        uniform_name.move_to(prior_name, DL)
        uniform_name.shift(RIGHT)
        uniform_name.set_y(bars.get_top()[1] + MED_SMALL_BUFF, DOWN)
        self.play(
            prior_name[0].next_to, uniform_name, RIGHT, MED_SMALL_BUFF, DOWN,
            FadeOutAndShift(prior_name[1], RIGHT),
            FadeInFrom(uniform_name, LEFT)
        )
        self.wait()

        self.bars = bars
        self.uniform_label = VGroup(uniform_name, prior_name[0])

    def show_bayes_formula(self):
        uniform_label = self.uniform_label
        p_label = self.p_label
        bars = self.bars

        prior_label = VGroup(
            p_label[0].deepcopy(),
            p_label[1].deepcopy(),
            p_label[4].deepcopy(),
        )
        eq = TexMobject("=")
        likelihood_label = TexMobject(
            "P(", "\\text{data}", "|", "s", ")",
        )
        likelihood_label.set_color_by_tex("data", GREEN)
        likelihood_label.set_color_by_tex("s", YELLOW)
        over = Line(LEFT, RIGHT)
        p_data_label = TextMobject("P(", "\\text{data}", ")")
        p_data_label.set_color_by_tex("data", GREEN)

        for mob in [eq, likelihood_label, over, p_data_label]:
            mob.scale(1.5)
            mob.set_opacity(0.1)

        eq.move_to(prior_label, LEFT)
        over.set_width(
            prior_label.get_width() +
            likelihood_label.get_width() +
            MED_SMALL_BUFF
        )
        over.next_to(eq, RIGHT, MED_SMALL_BUFF)
        p_data_label.next_to(over, DOWN, MED_SMALL_BUFF)
        likelihood_label.next_to(over, UP, MED_SMALL_BUFF, RIGHT)

        self.play(
            p_label.restore,
            p_label.next_to, eq, LEFT, MED_SMALL_BUFF,
            prior_label.next_to, over, UP, MED_SMALL_BUFF, LEFT,
            FadeIn(eq),
            FadeIn(likelihood_label),
            FadeIn(over),
            FadeIn(p_data_label),
            FadeOut(uniform_label),
        )

        # Show new distribution
        post_bars = bars.copy()
        total_prob = 0
        for bar, p in zip(post_bars, np.arange(0, 1, 0.01)):
            prob = scipy.stats.binom(50, p).pmf(48)
            bar.stretch(prob, 1, about_edge=DOWN)
            total_prob += 0.01 * prob
        post_bars.stretch(1 / total_prob, 1, about_edge=DOWN)
        post_bars.stretch(0.25, 1, about_edge=DOWN)  # Lie to fit on screen...
        post_bars.set_color(MAROON_D)
        post_bars.set_fill(opacity=0.8)

        brace = Brace(p_label, DOWN)
        post_word = brace.get_text("Posterior")
        post_word.scale(1.25, about_edge=UP)
        post_word.set_color(MAROON_D)

        self.play(
            ReplacementTransform(
                bars.copy().set_opacity(0),
                post_bars,
            ),
            GrowFromCenter(brace),
            FadeInFrom(post_word, 0.25 * UP)
        )
        self.wait()
        self.play(
            eq.set_opacity, 1,
            likelihood_label.set_opacity, 1,
        )
        self.wait()

        data = get_check_count_label(48, 2)
        data.scale(1.5)
        data.next_to(likelihood_label, DOWN, buff=2, aligned_edge=LEFT)
        data_arrow = Arrow(
            likelihood_label[1].get_bottom(),
            data.get_top()
        )
        data_arrow.set_color(GREEN)

        self.play(
            GrowArrow(data_arrow),
            GrowFromPoint(data, data_arrow.get_start()),
        )
        self.wait()
        self.play(FadeOut(data_arrow))
        self.play(
            over.set_opacity, 1,
            p_data_label.set_opacity, 1,
        )
        self.wait()

        self.play(
            FadeOut(brace),
            FadeOut(post_word),
            FadeOut(post_bars),
            FadeOut(data),
            p_label.set_opacity, 0.1,
            eq.set_opacity, 0.1,
            likelihood_label.set_opacity, 0.1,
            over.set_opacity, 0.1,
            p_data_label.set_opacity, 0.1,
        )

        self.bayes = VGroup(
            p_label, eq,
            prior_label, likelihood_label,
            over, p_data_label
        )
        self.data = data

    def parallel_universes(self):
        bars = self.bars

        cols = VGroup()
        squares = VGroup()
        sample_colors = color_gradient(
            [GREEN_C, GREEN_D, GREEN_E],
            100
        )
        for bar in bars:
            n_rows = 12
            col = VGroup()
            for x in range(n_rows):
                square = Rectangle(
                    width=bar.get_width(),
                    height=bar.get_height() / n_rows,
                )
                square.set_stroke(width=0)
                square.set_fill(opacity=1)
                square.set_color(random.choice(sample_colors))
                col.add(square)
                squares.add(square)
            col.arrange(DOWN, buff=0)
            col.move_to(bar)
            cols.add(col)
        squares.shuffle()

        self.play(
            LaggedStartMap(
                VFadeInThenOut, squares,
                lag_ratio=0.005,
                run_time=3
            )
        )
        self.remove(squares)
        squares.set_opacity(1)
        self.wait()

        example_col = cols[95]

        self.play(
            bars.set_opacity, 0.25,
            FadeIn(example_col, lag_ratio=0.1),
        )
        self.wait()

        dist = scipy.stats.binom(50, 0.95)
        for x in range(12):
            square = random.choice(example_col).copy()
            square.set_fill(opacity=0)
            square.set_stroke(YELLOW, 2)
            self.add(square)
            nc = dist.ppf(random.random())
            data = get_check_count_label(nc, 50 - nc)
            data.next_to(example_col, UP)

            self.add(square, data)
            self.wait(0.5)
            self.remove(square, data)
        self.wait()

        self.data.set_opacity(1)
        self.play(
            FadeIn(self.data),
            FadeOut(example_col),
            self.bayes[3].set_opacity, 1,
        )
        self.wait()

    def update_from_data(self):
        bars = self.bars
        data = self.data
        bayes = self.bayes

        new_bars = bars.copy()
        new_bars.set_stroke(opacity=1)
        new_bars.set_fill(opacity=0.8)
        for bar, p in zip(new_bars, np.arange(0, 1, 0.01)):
            dist = scipy.stats.binom(50, p)
            scalar = dist.pmf(48)
            bar.stretch(scalar, 1, about_edge=DOWN)

        self.play(
            ReplacementTransform(
                bars.copy().set_opacity(0),
                new_bars
            ),
            bars.set_fill, {"opacity": 0.1},
            bars.set_stroke, {"opacity": 0.1},
            run_time=2,
        )

        # Show example bar
        bar95 = VGroup(
            bars[95].copy(),
            new_bars[95].copy()
        )
        bar95.save_state()
        bar95.generate_target()
        bar95.target.scale(2)
        bar95.target.next_to(bar95, UP, LARGE_BUFF)
        bar95.target.set_stroke(BLUE, 3)

        ex_label = TexMobject("s", "=", "0.95")
        ex_label.set_color(YELLOW)
        ex_label.next_to(bar95.target, DOWN, submobject_to_align=ex_label[-1])

        highlight = SurroundingRectangle(bar95, buff=0)
        highlight.set_stroke(YELLOW, 2)

        self.play(FadeIn(highlight))
        self.play(
            MoveToTarget(bar95),
            FadeInFromDown(ex_label),
            data.shift, LEFT,
        )
        self.wait()

        side_brace = Brace(bar95[1], RIGHT, buff=SMALL_BUFF)
        side_label = side_brace.get_text("0.26", buff=SMALL_BUFF)
        self.play(
            GrowFromCenter(side_brace),
            FadeIn(side_label)
        )
        self.wait()
        self.play(
            FadeOut(side_brace),
            FadeOut(side_label),
            FadeOut(ex_label),
        )
        self.play(
            bar95.restore,
            bar95.set_opacity, 0,
        )

        for bar in bars[94:80:-1]:
            highlight.move_to(bar)
            self.wait(0.5)
        self.play(FadeOut(highlight))
        self.wait()

        # Emphasize formula terms
        tops = VGroup()
        for bar, new_bar in zip(bars, new_bars):
            top = Line(bar.get_corner(UL), bar.get_corner(UR))
            top.set_stroke(YELLOW, 2)
            top.generate_target()
            top.target.move_to(new_bar, UP)
            tops.add(top)

        rect = SurroundingRectangle(bayes[2])
        rect.set_stroke(YELLOW, 1)
        rect.target = SurroundingRectangle(bayes[3])
        rect.target.match_style(rect)
        self.play(
            ShowCreation(rect),
            ShowCreation(tops),
        )
        self.wait()
        self.play(
            LaggedStartMap(
                MoveToTarget, tops,
                run_time=2,
                lag_ratio=0.02,
            ),
            MoveToTarget(rect),
        )
        self.play(FadeOut(tops))
        self.wait()

        # Show alternate priors
        axes = self.axes
        bar_groups = VGroup()
        for bar, new_bar in zip(bars, new_bars):
            bar_groups.add(VGroup(bar, new_bar))

        bar_groups.save_state()
        for a, b in [(5, 2), (7, 1)]:
            dist = scipy.stats.beta(a, b)
            for bar, saved in zip(bar_groups, bar_groups.saved_state):
                bar.target = saved.copy()
                height = get_norm(axes.c2p(0.1 * dist.pdf(bar[0].x)) - axes.c2p(0, 0))
                height = max(height, 1e-6)
                bar.target.set_height(height, about_edge=DOWN, stretch=True)

            self.play(LaggedStartMap(MoveToTarget, bar_groups, lag_ratio=0))
            self.wait()
        self.play(Restore(bar_groups))
        self.wait()

        # Rescale
        ex_p_label = TexMobject(
            "P(s = 0.95 | 00000000) = ",
            tex_to_color_map={
                "s = 0.95": YELLOW,
                "00000000": WHITE,
            }
        )
        ex_p_label.scale(1.5)
        ex_p_label.next_to(bars, UP, LARGE_BUFF)
        ex_p_label.align_to(bayes, LEFT)
        template = ex_p_label.get_part_by_tex("00000000")
        template.set_opacity(0)

        highlight = SurroundingRectangle(new_bars[95], buff=0)
        highlight.set_stroke(YELLOW, 1)

        self.remove(data)
        self.play(
            FadeIn(ex_p_label),
            VFadeOut(data[0]),
            data[1:].move_to, template,
            FadeIn(highlight)
        )
        self.wait()

        numer = new_bars[95].copy()
        numer.set_stroke(YELLOW, 1)
        denom = new_bars[80:].copy()
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(3)
        h_line.set_stroke(width=2)
        h_line.next_to(ex_p_label, RIGHT)

        self.play(
            numer.next_to, h_line, UP,
            denom.next_to, h_line, DOWN,
            ShowCreation(h_line),
        )
        self.wait()
        self.play(
            denom.space_out_submobjects,
            rate_func=there_and_back
        )
        self.play(
            bayes[4].set_opacity, 1,
            bayes[5].set_opacity, 1,
            FadeOut(rect),
        )
        self.wait()

        # Rescale
        self.play(
            FadeOut(highlight),
            FadeOut(ex_p_label),
            FadeOut(data),
            FadeOut(h_line),
            FadeOut(numer),
            FadeOut(denom),
            bayes.set_opacity, 1,
        )

        new_bars.unlock_shader_data()
        self.remove(new_bars, *new_bars)
        self.play(
            new_bars.set_height, 5, {"about_edge": DOWN, "stretch": True},
            new_bars.set_color, MAROON_D,
        )
        self.wait()


class UniverseOf95Percent(WhatsTheModel):
    CONFIG = {"s": 0.95}

    def construct(self):
        self.introduce_buyer_and_seller()
        for m, v in [(self.seller, RIGHT), (self.buyer, LEFT)]:
            m.shift(v)
            m.label.shift(v)

        pis = VGroup(self.seller, self.buyer)
        label = get_prob_positive_experience_label(True, True)
        label[-1].set_value(self.s)
        label.set_height(1)
        label.next_to(pis, UP, LARGE_BUFF)
        self.add(label)

        for x in range(4):
            self.play(*self.experience_animations(
                self.seller, self.buyer, arc=30 * DEGREES, p=self.s
            ))

        self.embed()


class UniverseOf50Percent(UniverseOf95Percent):
    CONFIG = {"s": 0.5}


class OpenAndCloseAsideOnPdfs(Scene):
    def construct(self):
        labels = VGroup(
            TextMobject("$\\langle$", "Aside on", " pdfs", "$\\rangle$"),
            TextMobject("$\\langle$/", "Aside on", " pdfs", "$\\rangle$"),
        )
        labels.set_width(FRAME_WIDTH / 2)
        for label in labels:
            label.set_color_by_tex("pdfs", YELLOW)

        self.play(FadeInFromDown(labels[0]))
        self.wait()
        self.play(Transform(*labels))
        self.wait()


class TryAssigningProbabilitiesToSpecificValues(Scene):
    def construct(self):
        # To get "P(s = 95.9999%) ="" type labels
        def get_p_label(value):
            result = TexMobject(
                "P(", "{s}", "=", value, "\\%", ")",
            )
            fix_percent(result.get_part_by_tex("\\%")[0])
            result.set_color_by_tex("{s}", YELLOW)
            return result

        labels = VGroup(
            get_p_label("95.0000000"),
            get_p_label("94.9999999"),
            get_p_label("94.9314159"),
            get_p_label("94.9271828"),
            get_p_label("94.9466920"),
            get_p_label("94.9161803"),
        )
        labels.arrange(DOWN, buff=0.35, aligned_edge=LEFT)

        q_marks = VGroup()
        gt_zero = VGroup()
        eq_zero = VGroup()
        for label in labels:
            qm = TexMobject("=", "\\,???")
            qm.next_to(label, RIGHT)
            qm[1].set_color(TEAL)
            q_marks.add(qm)

            gt = TexMobject("> 0")
            gt.next_to(label, RIGHT)
            gt_zero.add(gt)

            eqz = TexMobject("= 0")
            eqz.next_to(label, RIGHT)
            eq_zero.add(eqz)

        v_dots = TexMobject("\\vdots")
        v_dots.next_to(q_marks[-1][0], DOWN, MED_LARGE_BUFF)

        # Animations
        self.play(FadeInFromDown(labels[0]))
        self.play(FadeInFrom(q_marks[0], LEFT))
        self.wait()
        self.play(*[
            TransformFromCopy(m1, m2)
            for m1, m2 in [
                (q_marks[0], q_marks[1]),
                (labels[0][:3], labels[1][:3]),
                (labels[0][5], labels[1][5]),
            ]
        ])
        self.play(ShowIncreasingSubsets(
            labels[1][3],
            run_time=3,
            int_func=np.ceil,
            rate_func=linear,
        ))
        self.add(labels[1])
        self.wait()
        self.play(
            LaggedStartMap(
                FadeInFrom, labels[2:],
                lambda m: (m, UP),
            ),
            LaggedStartMap(
                FadeInFrom, q_marks[2:],
                lambda m: (m, UP),
            ),
            Write(v_dots, rate_func=squish_rate_func(smooth, 0.5, 1))
        )
        self.add(labels, q_marks)
        self.wait()

        q_marks.unlock_triangulation()
        self.play(
            ReplacementTransform(q_marks, gt_zero, lag_ratio=0.05),
            run_time=2,
        )
        self.wait()

        # Show sum
        group = VGroup(labels, gt_zero, v_dots)
        sum_label = TexMobject(
            "\\sum_{s}", "P(", "{s}", ")", "=",
            tex_to_color_map={"{s}": YELLOW},
        )
        # sum_label.set_color_by_tex("{s}", YELLOW)
        sum_label[0].set_color(WHITE)
        sum_label.scale(1.75)
        sum_label.next_to(ORIGIN, RIGHT, buff=1)

        self.play(group.next_to, ORIGIN, LEFT)
        self.play(Write(sum_label))

        infty = TexMobject("\\infty")
        zero = TexMobject("0")
        for mob in [infty, zero]:
            mob.scale(2)
            mob.next_to(sum_label[-1], RIGHT)
        zero.set_color(RED)

        self.play(Write(infty))
        self.wait()

        # If equal to zero
        eq_zero.move_to(gt_zero)
        eq_zero.set_color(RED)
        gt_zero.unlock_triangulation()
        self.play(
            ReplacementTransform(gt_zero, eq_zero),
            lag_ratio=0.05,
            run_time=2,
            path_arc=30 * DEGREES,
        )
        self.wait()
        self.play(
            FadeInFrom(zero, DOWN),
            FadeOutAndShift(infty, UP),
        )
        self.wait()


class ShowLimitToPdf(Scene):
    def construct(self):
        # Init
        axes = self.get_axes()
        dist = scipy.stats.beta(4, 2)
        bars = self.get_bars(axes, dist, 0.05)

        axis_prob_label = TextMobject("Probability")
        axis_prob_label.next_to(axes.y_axis, UP)
        axis_prob_label.to_edge(LEFT)

        self.add(axes)
        self.add(axis_prob_label)

        # From individual to ranges
        kw = {"tex_to_color_map": {"s": YELLOW}}
        eq_label = TexMobject("P(s = 0.8)", **kw)
        ineq_label = TexMobject("P(0.8 < s < 0.85)", **kw)

        arrows = VGroup(Vector(DOWN), Vector(DOWN))
        for arrow, x in zip(arrows, [0.8, 0.85]):
            arrow.move_to(axes.c2p(x, 0), DOWN)
        brace = Brace(
            Line(arrows[0].get_start(), arrows[1].get_start()),
            UP, buff=SMALL_BUFF
        )
        eq_label.next_to(arrows[0], UP)
        ineq_label.next_to(brace, UP)

        self.play(
            FadeInFrom(eq_label, 0.2 * DOWN),
            GrowArrow(arrows[0]),
        )
        self.wait()
        vect = eq_label.get_center() - ineq_label.get_center()
        self.play(
            FadeOutAndShift(eq_label, -vect),
            FadeInFrom(ineq_label, vect),
            TransformFromCopy(*arrows),
            GrowFromPoint(brace, brace.get_left()),
        )
        self.wait()

        arrows[0].generate_target()
        arrows[0].target.next_to(bars[16], UP, SMALL_BUFF)

        for bar in bars:
            bar.save_state()
            bar.stretch(0, 1, about_edge=DOWN)

        kw = {
            "run_time": 2,
            "rate_func": squish_rate_func(smooth, 0.3, 0.9),
        }
        self.play(
            MoveToTarget(arrows[0], **kw),
            ApplyMethod(ineq_label.next_to, arrows[0].target, UP, **kw),
            FadeOut(arrows[1]),
            FadeOut(brace),
            LaggedStartMap(Restore, bars, run_time=2, lag_ratio=0.025),
        )
        self.wait()

        # Focus on area, not height
        lines = VGroup()
        new_bars = VGroup()
        for bar in bars:
            line = Line(
                bar.get_corner(DL),
                bar.get_corner(DR),
            )
            line.set_stroke(YELLOW, 0)
            line.generate_target()
            line.target.set_stroke(YELLOW, 3)
            line.target.move_to(bar.get_top())
            lines.add(line)

            new_bar = bar.copy()
            new_bar.match_style(line)
            new_bar.set_fill(YELLOW, 0.5)
            new_bar.generate_target()
            new_bar.stretch(0, 1, about_edge=UP)
            new_bars.add(new_bar)

        prob_label = TextMobject(
            "Height",
            "$\\rightarrow$",
            "Probability",
        )
        prob_label.space_out_submobjects(1.1)
        prob_label.next_to(bars[10], UL, LARGE_BUFF)
        height_word = prob_label[0]
        height_cross = Cross(height_word)
        area_word = TextMobject("Area")
        area_word.move_to(height_word, UR)
        area_word.set_color(YELLOW)

        self.play(
            LaggedStartMap(
                MoveToTarget, lines,
                lag_ratio=0.01,
            ),
            FadeInFromDown(prob_label),
        )
        self.add(height_word)
        self.play(
            ShowCreation(height_cross),
            FadeOutAndShift(axis_prob_label, LEFT)
        )
        self.wait()
        self.play(
            FadeOutAndShift(height_word, UP),
            FadeOutAndShift(height_cross, UP),
            FadeInFromDown(area_word),
        )
        self.play(
            FadeOut(lines),
            LaggedStartMap(
                MoveToTarget, new_bars,
                lag_ratio=0.01,
            )
        )
        self.play(
            FadeOut(new_bars),
            area_word.set_color, BLUE,
        )

        prob_label = VGroup(area_word, *prob_label[1:])
        self.add(prob_label)

        self.embed()

    def get_axes(self):
        axes = Axes(
            x_min=0,
            x_max=1,
            x_axis_config={
                "tick_frequency": 0.05,
                "unit_size": 12,
                "include_tip": False,
            },
            y_min=0,
            y_max=4,
            y_axis_config={
                "tick_frequency": 1,
                "unit_size": 1.25,
                "include_tip": False,
            }
        )
        axes.center()

        s_label = TexMobject("s")
        s_label.set_color(YELLOW)
        s_label.next_to(axes.x_axis, RIGHT)
        axes.x_axis.add(s_label)
        axes.x_axis.s_label = s_label

        axes.x_axis.add_numbers(
            *np.arange(0.2, 1.2, 0.2),
            number_config={"num_decimal_places": 1}
        )
        return axes

    def get_bars(self, axes, dist, step_size):
        bars = VGroup()
        for x in np.arange(0, 1, step_size):
            bar = Rectangle()
            bar.set_stroke(BLUE, 2)
            bar.set_fill(BLUE, 0.5)
            h_line = Line(
                axes.c2p(x, 0),
                axes.c2p(x + step_size, 0),
            )
            v_line = Line(
                axes.c2p(0, 0),
                axes.c2p(0, dist.pdf(x)),
            )
            bar.match_width(h_line, stretch=True)
            bar.match_height(v_line, stretch=True)
            bar.move_to(h_line, DOWN)
            bars.add(bar)
        return bars
