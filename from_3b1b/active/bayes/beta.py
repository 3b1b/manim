from manimlib.imports import *
from from_3b1b.active.bayes.beta_helpers import *

import scipy.stats

OUTPUT_DIRECTORY = "bayes/beta"


class Histogram(Axes):
    CONFIG = {
        "x_min": 0,
        "x_max": 10,
        "y_min": 0,
        "y_max": 1,
        "axis_config": {
            "include_tip": False,
        },
        "y_axis_config": {
            "tick_frequency": 0.2,
        },
        "height": 5,
        "width": 10,
        "y_axis_numbers_to_show": range(20, 120, 20),
        "y_axis_label_height": 0.25,
        "include_h_lines": True,
        "h_line_style": {
            "stroke_width": 1,
            "stroke_color": LIGHT_GREY,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize()
        self.center()
        self.add_y_axis_labels()
        if self.include_h_lines:
            self.add_h_lines()
        self.add_bars()

    # Initializing methods
    def resize(self):
        self.x_axis.set_width(
            self.width,
            stretch=True,
            about_point=self.c2p(0, 0),
        )
        self.y_axis.set_height(
            self.height,
            stretch=True,
            about_point=self.c2p(0, 0),
        )

    def add_y_axis_labels(self):
        labels = VGroup()
        for value in self.y_axis_numbers_to_show:
            label = Integer(value, unit="\\%")
            label.set_height(self.y_axis_label_height)
            label.next_to(self.y_axis.n2p(0.01 * value), LEFT)
            labels.add(label)
        self.y_axis_labels = labels
        self.y_axis.add(labels)
        return self

    def add_h_lines(self):
        self.h_lines = VGroup()
        for tick in self.y_axis.tick_marks:
            line = Line(**self.h_line_style)
            line.match_width(self.x_axis)
            line.move_to(tick.get_center(), LEFT)
            self.h_lines.add(line)
        self.add(self.h_lines)

    def add_bars(self):
        pass

    # Bar manipulations


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
        check = TexMobject("\\checkmark", color=GREEN)
        cross = TexMobject("\\times", color=RED)
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
        questions = self.questions

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

        self.play(
            LaggedStartMap(
                FadeInFromDown, VGroup(seller, buyer, *labels),
                lag_ratio=0.2
            ),
            questions[0].to_edge, UP,
            questions[1].set_opacity, 0.5,
            questions[1].scale, 0.25,
            questions[1].to_corner, UR,
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
        grey_box.set_fill(GREY_D)
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
    def experience_animations(self, seller, buyer, arc=-30 * DEGREES):
        positive = (random.random() < 0.75)
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

        row_rects = VGroup(*[
            SurroundingRectangle(row)
            for row in rows
            if all([m.get_value() < 95 for m in row])
        ])
        row_rects.set_stroke(YELLOW, 1)

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
        self.play(
            lt_95.set_color, BLUE,
            lt_95.set_stroke, GREEN, 1, {"background": True},
        )
        self.wait()
        self.play(LaggedStartMap(ShowCreation, row_rects))
        self.wait()


class LookAtAllPossibleSuccessRates(Scene):
    def construct(self):
        axes = get_beta_dist_axes()

        # Add a seller
        # Point out y ais

        self.embed()


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
            get_random_die(shuffle_time=1.20),
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
            pl.submobjects[1] = content

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
            ),
            run_time=1
        )
        self.wait(2)
        self.play(
            LaggedStartMap(Restore, prob_labels),
            run_time=3,
            lag_ratio=0.3,
        )
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeOut,
                number_rects,
                run_time=3,
            )
        )
        self.wait(2)

        # Highlight coin flip
        fade_rect = BackgroundRectangle(
            VGroup(prob_labels[1:], processes[1:]),
            buff=MED_SMALL_BUFF,
        )
        fade_rect.set_width(FRAME_WIDTH, stretch=True)
        fade_rect.set_fill(BLACK, 0.8)

        prob_half = prob_labels[0]
        half = prob_half[-1]
        half_underline = Line(LEFT, RIGHT)
        half_underline.set_width(half.get_width() + MED_SMALL_BUFF)
        half_underline.next_to(half, DOWN, buff=SMALL_BUFF)
        half_underline.set_stroke(YELLOW, 3)

        self.add(fade_rect, v_line, prob_half)
        self.play(FadeIn(fade_rect))
        self.wait(2)
        self.play(
            ShowCreation(half_underline),
            half.set_color, YELLOW,
        )
        self.play(FadeOut(half_underline))
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
            ApplyMethod(fade_rect.set_fill, BLACK, 1, remover=True),
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
        unknown_label = TextMobject("Unknown event")
        prob_label = TextMobject("Probability")
        titles = VGroup(unknown_label, prob_label)
        titles.scale(1.5)

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
