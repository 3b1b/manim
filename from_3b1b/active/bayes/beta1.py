from manimlib.imports import *
from from_3b1b.active.bayes.beta_helpers import *

import scipy.stats

OUTPUT_DIRECTORY = "bayes/beta1"


# Scenes
class BarChartTest(Scene):
    def construct(self):
        bar_chart = BarChart()
        bar_chart.to_edge(DOWN)
        self.add(bar_chart)


class Thumbnail1(Scene):
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


class AltThumbnail1(Scene):
    def construct(self):
        N = 20
        n_trials = 10000
        p = 0.7
        outcomes = (np.random.random((N, n_trials)) < p).sum(0)
        counts = []
        for k in range(N + 1):
            counts.append((outcomes == k).sum())

        hist = Histogram(
            counts,
            y_max=0.3,
            y_tick_freq=0.05,
            y_axis_numbers_to_show=[10, 20, 30],
            x_label_freq=10,
        )
        hist.set_width(FRAME_WIDTH - 1)
        hist.bars.set_submobject_colors_by_gradient(YELLOW, YELLOW, GREEN, BLUE)
        hist.bars.set_stroke(WHITE, 2)

        title = TextMobject("Binomial distribution")
        title.set_width(12)
        title.to_corner(UR, buff=0.8)
        title.add_background_rectangle()

        self.add(hist)
        self.add(title)


class Thumbnail2(Scene):
    def construct(self):
        axes = self.get_axes()
        graph = get_beta_graph(axes, 2, 2)
        # sub_graph = axes.get_graph(
        #     lambda x: (1 - x) * graph.underlying_function(x)
        # )
        # sub_graph.add_line_to(axes.c2p(1, 0))
        # sub_graph.add_line_to(axes.c2p(0, 0))
        # sub_graph.set_stroke(YELLOW, 4)
        # sub_graph.set_fill(YELLOW_D, 1)

        new_graph = get_beta_graph(axes, 9, 2)
        new_graph.set_stroke(GREEN, 4)
        new_graph.set_fill(GREEN, 0.5)

        self.add(axes)
        self.add(graph)
        self.add(new_graph)

        arrow = Arrow(
            axes.input_to_graph_point(0.5, graph),
            axes.input_to_graph_point(0.8, new_graph),
            path_arc=-90 * DEGREES,
            buff=0.3
        )
        self.add(arrow)

        formula = TexMobject(
            "P(H|D) = {P(H)P(D|H) \\over P(D)}",
            tex_to_color_map={
                "H": YELLOW,
                "D": GREEN,
            }
        )
        formula.next_to(axes.c2p(0, 3), RIGHT, LARGE_BUFF)
        formula.set_height(1.5)
        formula.to_edge(LEFT)
        formula.to_edge(UP, LARGE_BUFF)
        formula.add_to_back(BackgroundRectangle(formula[:4], buff=0.25))

        self.add(formula)

    def get_axes(self, y_max=3, y_height=4.5, y_unit=0.5):
        axes = get_beta_dist_axes(y_max=y_max, y_unit=y_unit)
        axes.y_axis.set_height(y_height, about_point=axes.c2p(0, 0))
        axes.to_edge(DOWN)
        axes.scale(0.9)
        return axes


class Thumbnail3(Thumbnail2):
    def construct(self):
        axes = self.get_axes(y_max=4, y_height=6)
        axes.set_height(7)
        graph = get_beta_graph(axes, 9, 2)

        self.add(axes)
        self.add(graph)

        label = TexMobject(
            "\\text{Beta}(10, 3)",
            tex_to_color_map={
                "10": GREEN,
                "3": RED,
            }
        )
        label = get_beta_label(9, 2)
        label.set_height(1.25)
        label.next_to(axes.c2p(0, 3), RIGHT, LARGE_BUFF)

        self.add(label)


class HighlightReviewParts(Scene):
    CONFIG = {
        "reverse_order": False,
    }

    def construct(self):
        # Setup up rectangles
        rects = VGroup(*[Rectangle() for x in range(3)])
        rects.set_stroke(width=0)
        rects.set_fill(GREY, 0.5)

        rects.set_height(1.35, stretch=True)
        rects.set_width(9.75, stretch=True)

        rects[0].move_to([-0.2, 0.5, 0])
        rects[1].next_to(rects[0], DOWN, buff=0)
        rects[2].next_to(rects[1], DOWN, buff=0)

        rects[2].set_height(1, stretch=True, about_edge=UP)

        inv_rects = VGroup()
        for rect in rects:
            fsr = FullScreenFadeRectangle()
            fsr.append_points(rect.points[::-1])
            inv_rects.add(fsr)

        inv_rects.set_fill(BLACK, 0.85)

        # Set up labels
        ratings = [100, 96, 93]
        n_reviews = [10, 50, 200]
        colors = [PINK, BLUE, YELLOW]

        review_labels = VGroup()
        for rect, rating, nr, color in zip(rects, ratings, n_reviews, colors):
            label = TexMobject(
                f"{nr}", "\\text{ reviews }",
                f"{rating}", "\\%",
            )
            label[2:].set_color(color)
            label.set_height(1)
            label.next_to(rect, UP, aligned_edge=RIGHT)
            label.set_stroke(BLACK, 4, background=True)
            fix_percent(label[3][0])
            review_labels.add(label)

        # Animations
        curr_fsr = inv_rects[0]
        curr_label = None

        tuples = list(zip(inv_rects, review_labels))
        if self.reverse_order:
            tuples = reversed(tuples)
            curr_fsr = inv_rects[-1]

        for fsr, label in tuples:
            if curr_fsr is fsr:
                self.play(VFadeIn(fsr))
            else:
                self.play(
                    Transform(curr_fsr, fsr),
                    MoveToTarget(curr_label),
                )

            first, second = label[2:], label[:2]
            if self.reverse_order:
                first, second = second, first

            self.add(first)
            self.wait(2)
            self.add(second)
            self.wait(2)

            label.generate_target()
            label.target.scale(0.3)
            if curr_label is None:
                label.target.to_corner(UR)
                label.target.shift(MED_LARGE_BUFF * LEFT)
            else:
                label.target.next_to(curr_label, DOWN)

            curr_label = label
        self.play(MoveToTarget(curr_label))
        self.wait()

        br = BackgroundRectangle(review_labels, buff=0.25)
        br.set_fill(BLACK, 0.85)
        br.set_width(FRAME_WIDTH)
        br.set_height(FRAME_HEIGHT, stretch=True)
        br.center()
        self.add(br, review_labels)
        self.play(
            FadeOut(curr_fsr),
            FadeIn(br),
        )
        self.wait()


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
                FadeIn(ar, 0.5 * DOWN, lag_ratio=0.2),
                FadeOut(last_review),
                FadeIn(ap, 0.5 * DOWN),
                FadeOut(last_percent, 0.5 * UP),
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


class PreviewThreeVideos(Scene):
    def construct(self):
        # Write equations
        equations = VGroup(
            TexMobject("{10", "\\over", "10}", "=", "100\\%"),
            TexMobject("{48", "\\over", "50}", "=", "96\\%"),
            TexMobject("{186", "\\over", "200}", "=", "93\\%"),
        )
        equations.arrange(RIGHT, buff=3)
        equations.to_edge(UP)

        colors = [PINK, BLUE, YELLOW]
        for eq, color in zip(equations, colors):
            eq[-1].set_color(color)
            fix_percent(eq[-1][-1])

        vs_labels = VGroup(*[TextMobject("vs.") for x in range(2)])
        for eq1, eq2, vs in zip(equations, equations[1:], vs_labels):
            vs.move_to(midpoint(eq1.get_right(), eq2.get_left()))

        self.add(equations)
        self.add(vs_labels)

        # Show topics
        title = TextMobject("To be explained:")
        title.set_height(0.7)
        title.next_to(equations, DOWN, LARGE_BUFF)
        title.to_edge(LEFT)
        title.add(Underline(title))

        topics = VGroup(
            TextMobject("Binomial distributions"),
            TextMobject("Bayesian updating"),
            TextMobject("Probability density functions"),
            TextMobject("Beta distribution"),
        )
        topics.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        topics.next_to(title, DOWN, MED_LARGE_BUFF)
        topics.to_edge(LEFT, buff=LARGE_BUFF)

        bullets = VGroup()
        for topic in topics:
            bullet = Dot()
            bullet.next_to(topic, LEFT)
            bullets.add(bullet)

        self.play(
            Write(title),
            Write(bullets),
            run_time=1,
        )
        self.play(LaggedStart(*[
            FadeIn(topic, lag_ratio=0.1)
            for topic in topics
        ], run_time=3, lag_ratio=0.3))
        self.wait()

        # Show videos
        images = [
            ImageMobject(os.path.join(
                consts.VIDEO_DIR,
                OUTPUT_DIRECTORY,
                "images",
                name
            ))
            for name in ["Thumbnail1", "Thumbnail2", "Thumbnail3"]
        ]
        thumbnails = Group()
        for image in images:
            image.set_width(FRAME_WIDTH / 3 - 1)
            rect = SurroundingRectangle(image, buff=0)
            rect.set_stroke(WHITE, 3)
            rect.set_fill(BLACK, 1)
            thumbnails.add(Group(rect, image))

        thumbnails.arrange(RIGHT, buff=LARGE_BUFF)

        for topic, i in zip(topics, [0, 1, 1, 2]):
            thumbnail = thumbnails[i]
            topic.generate_target()
            topic.target.scale(0.6)
            topic.target.next_to(thumbnail, DOWN, aligned_edge=LEFT)
        topics[2].target.next_to(
            topics[1].target, DOWN,
            aligned_edge=LEFT,
        )

        self.play(
            FadeOut(title, LEFT),
            FadeOut(bullets, LEFT),
            LaggedStartMap(MoveToTarget, topics),
            LaggedStartMap(FadeIn, thumbnails),
        )
        self.wait()

        tn_groups = Group(
            Group(thumbnails[0], topics[0]),
            Group(thumbnails[1], topics[1], topics[2]),
            Group(thumbnails[2], topics[3]),
        )

        setup_words = TextMobject("Set up the model")
        analysis_words = TextMobject("Analysis")
        for words in [setup_words, analysis_words]:
            words.scale(topics[0][0].get_height() / words[0][0].get_height())
            words.set_color(YELLOW)
        setup_words.move_to(topics[0], UL)
        analysis_words.next_to(topics[3], DOWN, aligned_edge=LEFT)

        def set_opacity(mob, alpha):
            for sm in mob.family_members_with_points():
                sm.set_opacity(alpha)
            return mob

        self.play(ApplyFunction(lambda m: set_opacity(m, 0.2), tn_groups[1:]))
        self.play(
            FadeIn(setup_words, lag_ratio=0.1),
            topics[0].next_to, setup_words, DOWN, {"aligned_edge": LEFT},
        )
        tn_groups[0].add(setup_words)
        self.wait(2)
        for i in 0, 1:
            self.play(
                ApplyFunction(lambda m: set_opacity(m, 0.2), tn_groups[i]),
                ApplyFunction(lambda m: set_opacity(m, 1), tn_groups[i + 1]),
            )
            self.wait(2)
        self.play(FadeIn(analysis_words, 0.25 * UP))
        tn_groups[2].add(analysis_words)
        self.wait(2)

        self.play(
            FadeOut(setup_words),
            FadeOut(topics[0]),
            FadeOut(tn_groups[1]),
            FadeOut(tn_groups[2]),
            FadeOut(vs_labels, UP),
            FadeOut(equations, UP),
            ApplyFunction(lambda m: set_opacity(m, 1), thumbnails[0]),
        )
        thumbnails[0].generate_target()
        # thumbnails[0].target.set_width(FRAME_WIDTH)
        # thumbnails[0].target.center()
        thumbnails[0].target.to_edge(UP)
        self.play(MoveToTarget(thumbnails[0], run_time=4))
        self.wait()


class LetsLookAtOneAnswer(TeacherStudentsScene):
    def construct(self):
        self.remove(self.background)
        self.teacher_says(
            "Let me show you\\\\one answer.",
            added_anims=[
                self.get_student_changes("pondering", "thinking", "pondering")
            ]
        )
        self.look_at(self.screen)
        self.change_all_student_modes("thinking", look_at_arg=self.screen)
        self.wait(4)


class LaplacesRuleOfSuccession(Scene):
    def construct(self):
        # Setup
        title = TextMobject("How to read a rating")
        title.set_height(0.75)
        title.to_edge(UP)
        underline = Underline(title)
        underline.scale(1.2)
        self.add(title, underline)

        data = get_checks_and_crosses(11 * [True] + [False], width=10)
        data.shift(DOWN)
        underlines = get_underlines(data)

        real_data = data[:10]
        fake_data = data[10:]

        def get_review_label(num, denom):
            result = VGroup(
                Integer(num, color=GREEN),
                TextMobject("out of"),
                Integer(denom),
            )
            result.arrange(RIGHT)
            result.set_height(0.6)
            return result

        review_label = get_review_label(10, 10)
        review_label.next_to(data[:10], UP, MED_LARGE_BUFF)

        # Show initial review
        self.add(review_label)
        self.add(underlines[:10])

        self.play(
            ShowIncreasingSubsets(real_data, int_func=np.ceil),
            CountInFrom(review_label[0], 0),
            rate_func=lambda t: smooth(t, 3),
        )
        self.wait()

        # Fake data
        fd_rect = SurroundingRectangle(VGroup(fake_data, underlines[10:]))
        fd_rect.set_stroke(WHITE, 2)
        fd_rect.set_fill(GREY_E, 1)

        fd_label = TextMobject("Pretend you see\\\\two more")
        fd_label.next_to(fd_rect, DOWN)
        fd_label.shift_onto_screen()

        self.play(
            FadeIn(fd_label, UP),
            DrawBorderThenFill(fd_rect),
            ShowCreation(underlines[10:])
        )
        self.wait()
        for mark in data[10:]:
            self.play(Write(mark))
        self.wait()

        # Update rating
        review_center = VectorizedPoint(review_label.get_center())
        pretend_label = TextMobject("Pretend that it's")
        pretend_label.match_width(review_label)
        pretend_label.next_to(review_label, UP, MED_LARGE_BUFF)
        pretend_label.match_x(data)
        pretend_label.set_color(BLUE_D)

        old_review_label = VGroup(Integer(0), TextMobject("out of"), Integer(0))
        old_review_label.become(review_label)

        self.add(old_review_label, review_label)
        self.play(
            review_center.set_x, data.get_center()[0],
            MaintainPositionRelativeTo(review_label, review_center),
            UpdateFromAlphaFunc(
                review_label[0],
                lambda m, a: m.set_value(int(interpolate(10, 11, a)))
            ),
            UpdateFromAlphaFunc(
                review_label[2],
                lambda m, a: m.set_value(int(interpolate(10, 12, a)))
            ),
            FadeIn(pretend_label, LEFT),
            old_review_label.scale, 0.5,
            old_review_label.set_opacity, 0.5,
            old_review_label.to_edge, LEFT,
        )
        self.wait()

        # Show fraction
        eq = TexMobject(
            "{11", "\\over", "12}",
            "\\approx", "91.7\\%"
        )
        fix_percent(eq[-1][-1])
        eq.set_color_by_tex("11", GREEN)

        eq.next_to(pretend_label, RIGHT)
        eq.to_edge(RIGHT, buff=MED_LARGE_BUFF)

        self.play(Write(eq))
        self.wait()
        self.play(ShowCreationThenFadeAround(eq))
        self.wait()

        # Remove clutter
        old_review_label.generate_target()
        old_review_label.target.next_to(title, DOWN, LARGE_BUFF)
        old_review_label.target.to_edge(LEFT)
        old_review_label.target.set_opacity(1)
        arrow = Vector(0.5 * RIGHT)
        arrow.next_to(old_review_label.target, RIGHT)

        self.play(
            MoveToTarget(old_review_label),
            FadeIn(arrow),
            eq.next_to, arrow, RIGHT,
            FadeOut(
                VGroup(
                    fake_data,
                    underlines,
                    pretend_label,
                    review_label,
                    fd_rect, fd_label,
                ),
                DOWN,
                lag_ratio=0.01,
            ),
            real_data.match_width, old_review_label.target,
            real_data.next_to, old_review_label.target, DOWN,
        )
        self.wait()

        # Show 48 of 50 case
        # Largely copied from above...not great
        data = get_checks_and_crosses(
            48 * [True] + 2 * [False] + [True, False],
            width=FRAME_WIDTH - 1,
        )
        data.shift(DOWN)
        underlines = get_underlines(data)

        review_label = get_review_label(48, 50)
        review_label.next_to(data, UP, MED_LARGE_BUFF)

        true_data = data[:-2]
        fake_data = data[-2:]

        fd_rect.replace(fake_data, stretch=True)
        fd_rect.stretch(1.2, 0)
        fd_rect.stretch(2.2, 1)
        fd_rect.shift(0.025 * DOWN)
        fd_label.next_to(fd_rect, DOWN, LARGE_BUFF)
        fd_label.shift_onto_screen()
        fd_arrow = Arrow(fd_label.get_top(), fd_rect.get_corner(DL))

        self.play(
            FadeIn(underlines[:-2]),
            ShowIncreasingSubsets(true_data, int_func=np.ceil),
            CountInFrom(review_label[0], 0),
            UpdateFromAlphaFunc(
                review_label,
                lambda m, a: m.set_opacity(a),
            ),
        )
        self.wait()
        self.play(
            FadeIn(fd_label),
            GrowArrow(fd_arrow),
            FadeIn(fd_rect),
            Write(fake_data),
            Write(underlines[-2:]),
        )
        self.wait()

        # Pretend it's 49 / 52
        old_review_label = VGroup(Integer(0), TextMobject("out of"), Integer(0))
        old_review_label.become(review_label)
        review_center = VectorizedPoint(review_label.get_center())

        self.play(
            review_center.set_x, data.get_center()[0] + 3,
            MaintainPositionRelativeTo(review_label, review_center),
            UpdateFromAlphaFunc(
                review_label[0],
                lambda m, a: m.set_value(int(interpolate(48, 49, a)))
            ),
            UpdateFromAlphaFunc(
                review_label[2],
                lambda m, a: m.set_value(int(interpolate(50, 52, a)))
            ),
            old_review_label.scale, 0.5,
            old_review_label.to_edge, LEFT,
        )
        self.wait()

        arrow2 = Vector(0.5 * RIGHT)
        arrow2.next_to(old_review_label, RIGHT)

        eq2 = TexMobject(
            "{49", "\\over", "52}",
            "\\approx", "94.2\\%"
        )
        fix_percent(eq2[-1][-1])
        eq2[0].set_color(GREEN)
        eq2.next_to(arrow2, RIGHT)
        eq2.save_state()
        eq2[1].set_opacity(0)
        eq2[3:].set_opacity(0)
        eq2[0].replace(review_label[0])
        eq2[2].replace(review_label[2])

        self.play(
            Restore(eq2, run_time=1.5),
            FadeIn(arrow2),
        )
        self.wait()

        faders = VGroup(
            fd_rect, fd_arrow, fd_label,
            fake_data, underlines,
            review_label,
        )
        self.play(
            FadeOut(faders),
            true_data.match_width, old_review_label,
            true_data.next_to, old_review_label, DOWN,
        )

        # 200 review case
        final_review_label = get_review_label(186, 200)
        final_review_label.match_height(old_review_label)
        final_review_label.move_to(old_review_label, LEFT)
        final_review_label.shift(
            arrow2.get_center() -
            arrow.get_center()
        )

        data = get_checks_and_crosses([True] * 186 + [False] * 14 + [True, False])
        data[:200].arrange_in_grid(10, 20, buff=0)
        data[-2:].next_to(data[:200], DOWN, buff=0)
        data.set_width(FRAME_WIDTH / 2 - 1)
        data.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        data.to_edge(DOWN)
        for mark in data:
            mark.scale(0.5)

        true_data = data[:-2]
        fake_data = data[-2:]

        self.play(
            UpdateFromAlphaFunc(
                final_review_label,
                lambda m, a: m.set_opacity(a),
            ),
            CountInFrom(final_review_label[0], 0),
            ShowIncreasingSubsets(true_data),
        )
        self.wait()

        arrow3 = Vector(0.5 * RIGHT)
        arrow3.next_to(final_review_label, RIGHT)

        eq3 = TexMobject(
            "{187", "\\over", "202}",
            "\\approx", "92.6\\%"
        )
        fix_percent(eq3[-1][-1])
        eq3[0].set_color(GREEN)
        eq3.next_to(arrow3, RIGHT)

        self.play(
            GrowArrow(arrow3),
            FadeIn(eq3),
            Write(fake_data)
        )
        self.wait()
        self.play(
            true_data.match_width, final_review_label,
            true_data.next_to, final_review_label, DOWN,
            FadeOut(fake_data)
        )
        self.wait()

        # Make a selection
        rect = SurroundingRectangle(VGroup(eq2, old_review_label))
        rect.set_stroke(YELLOW, 2)

        self.play(
            ShowCreation(rect),
            eq2[-1].set_color, YELLOW,
        )
        self.wait()

        # Retitle
        name = TextMobject("Laplace's rule of succession")
        name.match_height(title)
        name.move_to(title)
        name.set_color(TEAL)

        self.play(
            FadeInFromDown(name),
            FadeOut(title, UP),
            underline.match_width, name,
        )
        self.wait()


class AskWhy(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Wait...why?",
            look_at_arg=self.screen,
        )
        self.play(
            self.students[0].change, "confused", self.screen,
            self.students[1].change, "confused", self.screen,
            self.teacher.change, "tease", self.students[2].eyes,
        )
        self.wait(3)

        self.students[2].bubble.content.unlock_triangulation()
        self.student_says(
            "Is that really\\\\the answer?",
            target_mode="raise_right_hand",
            added_anims=[self.teacher.change, "thinking"],
        )
        self.wait(2)
        self.teacher_says("Let's dive in!", target_mode="hooray")
        self.change_all_student_modes("hooray")
        self.wait(3)


class BinomialName(Scene):
    def construct(self):
        text = TextMobject("Probabilities of probabilities\\\\", "Part 1")
        text.set_width(FRAME_WIDTH - 1)
        text[0].set_color(BLUE)
        self.add(text[0])
        self.play(Write(text[1], run_time=2))
        self.wait(2)


class WhatsTheModel(Scene):
    CONFIG = {
        "random_seed": 5,
    }

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
        self.play(FadeIn(questions[0]))
        self.play(FadeIn(questions[1], UP))
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
            FadeIn(success_rate, 0.5 * DOWN)
        )
        self.wait()
        self.play(
            TransformFromCopy(success_rate[0], s_sym),
            FadeOut(success_rate, 0.1 * RIGHT, lag_ratio=0.1),
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
            FadeOut(rhs, 0.5 * DOWN),
            FadeIn(grey_box, 0.5 * UP),
            FadeIn(lil_q_marks, DOWN),
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
                "coin_flip_1",
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
        self.show_simulated_reviews()

    def add_review(self):
        reviews = VGroup(*[TexMobject(CMARK_TEX) for x in range(10)])
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

    def show_simulated_reviews(self):
        prob_label_group = self.prob_label_group
        review_group = self.review_group

        # Set up decimals
        random.seed(2)
        decimals = VGroup()
        for x in range(10):
            dec = DecimalNumber()
            decimals.add(dec)

        def randomize_decimals(decimals):
            for dec in decimals:
                value = random.random()
                dec.set_value(value)
                if value > 0.95:
                    dec.set_color(RED)
                else:
                    dec.set_color(WHITE)

        randomize_decimals(decimals)

        decimals.set_height(0.3)
        decimals.arrange(RIGHT, buff=MED_LARGE_BUFF)
        decimals.next_to(ORIGIN, DOWN)
        decimals[0].set_value(0.42)
        decimals[0].set_color(WHITE)
        decimals[1].set_value(0.97)
        decimals[1].set_color(RED)

        random_label = TextMobject("Random number\\\\in [0, 1]")
        random_label.scale(0.7)
        random_label.next_to(decimals[0], DOWN)
        random_label.set_color(GREY_B)

        arrows = VGroup()
        for dec in decimals:
            arrow = Vector(0.4 * UP)
            arrow.next_to(dec, UP)
            arrows.add(arrow)

        # Set up marks
        def get_marks(decs, arrows):
            marks = VGroup()
            for dec, arrow in zip(decs, arrows):
                if dec.get_value() < 0.95:
                    mark = TexMobject(CMARK_TEX)
                    mark.set_color(GREEN)
                else:
                    mark = TexMobject(XMARK_TEX)
                    mark.set_color(RED)
                mark.set_height(0.5)
                mark.next_to(arrow, UP)
                marks.add(mark)
            return marks

        marks = get_marks(decimals, arrows)

        lt_p95 = TexMobject("< 0.95")
        gte_p95 = TexMobject("\\ge 0.95")
        for label in lt_p95, gte_p95:
            label.match_height(decimals[0])

        lt_p95.next_to(decimals[0], RIGHT, MED_SMALL_BUFF)
        gte_p95.next_to(decimals[1], RIGHT, MED_SMALL_BUFF)
        lt_p95.set_color(GREEN)
        gte_p95.set_color(RED)

        # Introduce simulation
        review_group.save_state()
        self.play(
            review_group.scale, 0.25,
            review_group.to_corner, UR,
            Write(random_label),
            CountInFrom(decimals[0], 0),
        )
        self.wait()
        self.play(FadeIn(lt_p95, LEFT))
        self.play(
            GrowArrow(arrows[0]),
            FadeIn(marks[0], DOWN)
        )
        self.wait()
        self.play(
            FadeOut(lt_p95, 0.5 * RIGHT),
            FadeIn(gte_p95, 0.5 * LEFT),
        )
        self.play(
            random_label.match_x, decimals[1],
            CountInFrom(decimals[1], 0),
            UpdateFromAlphaFunc(
                decimals[1],
                lambda m, a: m.set_opacity(a),
            ),
        )
        self.play(
            GrowArrow(arrows[1]),
            FadeIn(marks[1], DOWN),
        )
        self.wait()
        self.play(
            LaggedStartMap(
                CountInFrom, decimals[2:],
            ),
            UpdateFromAlphaFunc(
                decimals[2:],
                lambda m, a: m.set_opacity(a),
            ),
            FadeOut(gte_p95),
            run_time=1,
        )
        self.add(decimals)
        self.play(
            LaggedStartMap(GrowArrow, arrows[2:]),
            LaggedStartMap(FadeInFromDown, marks[2:]),
            run_time=1
        )
        self.add(arrows, marks)
        self.wait()

        # Add new rows
        decimals.arrows = arrows
        decimals.add_updater(lambda d: d.next_to(d.arrows, DOWN))
        added_anims = [FadeOut(random_label)]
        rows = VGroup(marks)
        for x in range(3):
            self.play(
                arrows.shift, DOWN,
                UpdateFromFunc(decimals, randomize_decimals),
                *added_anims,
            )
            added_anims = []
            new_marks = get_marks(decimals, arrows)
            self.play(LaggedStartMap(FadeInFromDown, new_marks))
            self.wait()
            rows.add(new_marks)

        # Create a stockpile of new rows
        added_rows = VGroup()
        decimals.clear_updaters()
        decimals.save_state()
        for x in range(100):
            randomize_decimals(decimals)
            added_rows.add(get_marks(decimals, arrows))
        decimals.restore()

        # Compress rows
        rows.generate_target()
        for group in rows.target, added_rows:
            group.scale(0.3)
            for row in group:
                row.arrange(RIGHT, buff=SMALL_BUFF)
            group.arrange(DOWN, buff=0.2)
        rows.target.next_to(prob_label_group, DOWN, MED_LARGE_BUFF)
        rows.target.set_x(-3.5)

        nr = 15
        added_rows[:nr].move_to(rows.target, UP)
        added_rows[nr:2 * nr].move_to(rows.target, UP)
        added_rows[nr:2 * nr].shift(3.5 * RIGHT)
        added_rows[2 * nr:3 * nr].move_to(rows.target, UP)
        added_rows[2 * nr:3 * nr].shift(7 * RIGHT)
        added_rows = added_rows[4:3 * nr]

        self.play(
            MoveToTarget(rows),
            FadeOut(decimals),
            FadeOut(arrows),
        )
        self.play(ShowIncreasingSubsets(added_rows), run_time=3)

        # Show scores
        all_rows = VGroup(*rows, *added_rows)
        scores = VGroup()
        ten_rects = VGroup()
        for row in all_rows:
            score = Integer(sum([
                mark.get_color() == Color(GREEN)
                for mark in row
            ]))
            score.match_height(row)
            score.next_to(row, RIGHT)
            if score.get_value() == 10:
                score.set_color(TEAL)
                ten_rects.add(SurroundingRectangle(score))
            scores.add(score)

        ten_rects.set_stroke(YELLOW, 2)

        self.play(FadeIn(scores))
        self.wait()
        self.play(LaggedStartMap(ShowCreation, ten_rects))
        self.play(LaggedStartMap(FadeOut, ten_rects))
        self.wait(2)

        # Show alternate possibilities
        prob = DecimalNumber(0.95)
        prob.set_color(YELLOW)
        template = prob_label_group[0][-1]
        prob.match_height(template)
        prob.move_to(template, LEFT)
        rect = BackgroundRectangle(template, buff=SMALL_BUFF)
        rect.set_fill(BLACK, 1)
        self.add(rect)
        self.add(prob)
        self.play(
            LaggedStartMap(FadeOutAndShift, all_rows, lag_ratio=0.01),
            LaggedStartMap(FadeOutAndShift, scores, lag_ratio=0.01),
            Restore(review_group),
        )
        for value in [0.9, 0.99, 0.8, 0.95]:
            self.play(ChangeDecimalToValue(prob, value))
            self.wait()

    # No longer used
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
        # highlights = VGroup(*[
        #     square.copy().move_to(mob)
        #     for row in rows
        #     for mob in row
        #     if mob.get_value() < 95
        # ])

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
            FadeOut(self.review_group, DOWN),
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
        self.wait(10)
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
                FadeOut(unknown_title, UP),
                FadeOut(prob_title, UP),
                lag_ratio=0.2,
            ),
            FadeOut(h_line, UP, lag_ratio=0.1),
            FadeOut(processes, LEFT, lag_ratio=0.1),
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
            FadeIn(question, UP),
        )
        self.wait(2)
        self.play(
            FadeOut(question, RIGHT),
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
            FadeOut(half, UP),
            FadeIn(q_marks, DOWN),
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
            get_coin("H"),
            get_coin("T"),
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


class AskProbabilityOfCoins(Scene):
    def construct(self):
        condition = VGroup(
            TextMobject("If you've seen"),
            Integer(80, color=BLUE_C),
            get_coin("H").set_height(0.5),
            TextMobject("and"),
            Integer(20, color=RED_C),
            get_coin("T").set_height(0.5),
        )
        condition.arrange(RIGHT)
        condition.to_edge(UP)
        self.add(condition)

        question = TexMobject(
            "\\text{What is }",
            "P(", "00", ")", "?"
        )
        coin = get_coin("H")
        coin.replace(question.get_part_by_tex("00"))
        question.replace_submobject(
            question.index_of_part_by_tex("00"),
            coin
        )
        question.next_to(condition, DOWN)
        self.add(question)

        values = ["H"] * 80 + ["T"] * 20
        random.shuffle(values)

        coins = VGroup(*[
            get_coin(symbol)
            for symbol in values
        ])
        coins.arrange_in_grid(10, 10, buff=MED_SMALL_BUFF)
        coins.set_width(5)
        coins.next_to(question, DOWN, MED_LARGE_BUFF)

        self.play(
            ShowIncreasingSubsets(coins),
            run_time=8,
            rate_func=bezier([0, 0, 1, 1])
        )
        self.wait()

        self.embed()


class RunCarFactory(Scene):
    def construct(self):
        # Factory
        factory = SVGMobject(file_name="factory")
        factory.set_fill(GREY_D)
        factory.set_stroke(width=0)
        factory.flip()
        factory.set_height(6)
        factory.to_edge(LEFT)

        self.add(factory)

        # Dumb hack
        l1 = Line(
            factory[0].points[-200],
            factory[0].points[-216],
        )
        l2 = Line(
            factory[0].points[-300],
            factory[0].points[-318],
        )
        for line in l1, l2:
            square = Square()
            square.set_fill(BLACK, 1)
            square.set_stroke(width=0)
            square.replace(line)
            factory.add(square)

        rect = Rectangle()
        rect.match_style(factory)
        rect.set_height(1.1)
        rect.set_width(6.75, stretch=True)
        rect.move_to(factory, DL)

        # Get cars
        car = Car(color=interpolate_color(BLUE_E, GREY_C, 0.5))
        car.set_height(0.9)
        for tire in car.get_tires():
            tire.set_fill(GREY_C)
            tire.set_stroke(BLACK)
        car.randy.set_opacity(0)
        car.move_to(rect.get_corner(DR))

        cars = VGroup()
        n_cars = 20
        for x in range(n_cars):
            cars.add(car.copy())

        for car in cars[4], cars[6]:
            scratch = VMobject()
            scratch.start_new_path(UP)
            scratch.add_line_to(0.25 * DL)
            scratch.add_line_to(0.25 * UR)
            scratch.add_line_to(DOWN)
            scratch.set_stroke([RED_A, RED_C], [0.1, 2, 2, 0.1])
            scratch.set_height(0.25)
            scratch.move_to(car)
            scratch.shift(0.1 * DOWN)
            car.add(scratch)

        self.add(cars, rect)
        self.play(LaggedStartMap(
            MoveCar, cars,
            lambda m: (m, m.get_corner(DR) + 10 * RIGHT),
            lag_ratio=0.3,
            rate_func=linear,
            run_time=1.5 * n_cars,
        ))
        self.remove(cars)


class CarFactoryNumbers(Scene):
    def construct(self):
        # Test words
        denom_words = TextMobject(
            "in a test of 100 cars",
            tex_to_color_map={"100": BLUE},
        )
        denom_words.to_corner(UR)

        numer_words = TextMobject(
            "2 defects found",
            tex_to_color_map={"2": RED}
        )
        numer_words.move_to(denom_words, LEFT)

        self.play(Write(denom_words, run_time=1))
        self.wait()
        self.play(
            denom_words.next_to, numer_words, DOWN, {"aligned_edge": LEFT},
            FadeIn(numer_words),
        )
        self.wait()

        # Question words
        question = VGroup(
            TextMobject("How do you plan"),
            TextMobject("for"),
            Integer(int(1e6), color=BLUE),
            TextMobject("cars?")
        )
        question[1:].arrange(RIGHT, aligned_edge=DOWN)
        question[2].shift(
            (question[2][1].get_bottom()[1] - question[2][0].get_bottom()[1]) * UP
        )
        question[1:].next_to(question[0], DOWN, aligned_edge=LEFT)
        question.next_to(denom_words, DOWN, LARGE_BUFF, aligned_edge=LEFT)

        self.play(
            UpdateFromAlphaFunc(
                question,
                lambda m, a: m.set_opacity(a),
            ),
            CountInFrom(question[2], 0, run_time=1.5)
        )
        self.wait()


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
            self.get_prob_review_label(186, 14),
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
            FadeIn(short_label, UP),
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
        "s": 0.95,
        "histogram_height": 5,
        "histogram_width": 10,
    }

    def construct(self):
        # Add s label
        s_label = TexMobject("s = 0.95")
        s_label.set_height(0.3)
        s_label.to_corner(UL, buff=MED_SMALL_BUFF)
        s_label.set_color(YELLOW)
        self.add(s_label)
        self.camera.frame.shift(LEFT)
        s_label.shift(LEFT)

        # Add random row
        np.random.seed(0)
        row = get_random_num_row(self.s)
        count = self.get_count(row)
        count.add_updater(
            lambda m: m.set_value(
                sum([s.positive for s in row.syms])
            )
        )

        def update_nums(nums):
            for num in nums:
                num.set_value(np.random.random())

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
        histogram = self.get_histogram(data)

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

        # Random samples in histogram
        self.play(
            FadeIn(histogram),
            ApplyFunction(
                put_into_histogram,
                VGroup(row, count),
            )
        )
        self.wait()
        for x in range(2):
            row = get_random_num_row(self.s)
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

        # More!
        for x in range(40):
            row = get_random_num_row(self.s)
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
            new_row = get_random_num_row(self.s)
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
    def get_histogram(self, data):
        histogram = Histogram(
            data,
            bar_colors=[RED, RED, BLUE, GREEN],
            height=self.histogram_height,
            width=self.histogram_width,
        )
        histogram.to_edge(DOWN)

        histogram.axes.y_labels.set_opacity(0)
        histogram.axes.h_lines.set_opacity(0)
        return histogram

    def get_count(self, row):
        count = Integer()
        count.set_height(0.75)
        count.next_to(row, DOWN, buff=0.65)
        count.set_value(sum([s.positive for s in row.syms]))
        return count


class SimulationsOf10ReviewsSquished(SimulationsOf10Reviews):
    CONFIG = {
        "histogram_height": 2,
        "histogram_width": 11,
    }

    def get_histogram(self, data):
        hist = super().get_histogram(data)
        hist.to_edge(UP, buff=1.5)
        return hist


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
        row.move_to(3.5 * UP)
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
            FadeIn(value, LEFT),
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
            FadeIn(bin_name, DOWN),
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
            FadeIn(likelihood_label, UP),
            bin_name.set_height, 0.4,
            bin_name.set_y, histogram.axes.c2p(0, .25)[1]
        )
        self.wait()
        self.play(
            GrowArrow(right_arrow),
            FadeIn(ra_label, 0.5 * LEFT),
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
            FadeOut(row, UP),
            FadeOut(self.slots, UP),
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
        value.initial_config["num_decimal_places"] = 3
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

        # Write formula
        clean_form = TexMobject(
            "P(", "\\text{data}", "\\,|\\,", "{s}", ")", "=",
            "c", "\\cdot",
            "{s}", "^{\\#" + CMARK_TEX + "}",
            "(1 - ", "{s}", ")", "^{\\#" + XMARK_TEX + "}",
            tex_to_color_map={
                "{s}": YELLOW,
                "\\#" + CMARK_TEX: GREEN,
                "\\#" + XMARK_TEX: RED,
            }
        )
        clean_form.next_to(formula, DOWN, MED_LARGE_BUFF)
        clean_form.save_state()
        clean_form[:6].align_to(equation[1], RIGHT)
        clean_form[6].match_x(formula[2])
        clean_form[7].set_opacity(0)
        clean_form[7].next_to(clean_form[6], RIGHT, SMALL_BUFF)
        clean_form[8:11].match_x(formula[4:8])
        clean_form[11:].match_x(formula[8:])
        clean_form.saved_state.move_to(clean_form, LEFT)

        fade_rects = VGroup(
            BackgroundRectangle(equation[:2]),
            BackgroundRectangle(formula),
            BackgroundRectangle(VGroup(eq2, bar_copy)),
        )
        fade_rects.set_fill(BLACK, 0.8)
        fade_rects[1].set_fill(opacity=0)

        pre_c = formula[:4].copy()
        pre_s = formula[4:8].copy()
        pre_1ms = formula[8:].copy()

        self.play(
            FadeIn(fade_rects),
            FadeIn(clean_form[:6])
        )
        self.play(ShowCreationThenFadeAround(clean_form[3]))
        self.wait()
        for cf, pre in (clean_form[6], pre_c), (clean_form[8:11], pre_s), (clean_form[11:], pre_1ms):
            self.play(
                GrowFromPoint(cf, pre.get_center()),
                pre.move_to, cf,
                pre.scale, 0,
            )
            self.remove(pre)
            self.wait()

        self.wait()
        self.play(Restore(clean_form))

        # Show with 480 and 20
        top_fade_rect = BackgroundRectangle(histogram)
        top_fade_rect.shift(SMALL_BUFF * DOWN)
        top_fade_rect.scale(1.5, about_edge=DOWN)
        top_fade_rect.set_fill(BLACK, 0)

        new_formula = get_binomial_formula(500, 480, 0.96)
        new_formula.move_to(formula)

        def func500(x):
            return scipy.stats.binom(500, x).pmf(480) + 1e-5

        graph500 = low_axes.get_graph(func500, step_size=0.05)
        graph500.set_stroke(TEAL, 3)

        self.play(
            top_fade_rect.set_opacity, 1,
            fade_rects.set_opacity, 1,
            FadeIn(new_formula)
        )

        self.clear()
        self.add(new_formula, clean_form, low_axes, graph, v_line, dot)
        self.add(low_axes.y_axis)

        self.play(TransformFromCopy(graph, graph500))
        self.wait()

        y_axis = low_axes.y_axis
        y_axis.save_state()
        sf = 3
        y_axis.stretch(sf, 1, about_point=low_axes.c2p(0, 0))
        for label in y_label_copies:
            label.stretch(1 / sf, 1)

        v_line.suspend_updating()
        v_line.graph = graph500
        self.play(
            Restore(y_axis, rate_func=reverse_smooth),
            graph.stretch, sf, 1, {"about_edge": DOWN},
            graph500.stretch, sf, 1, {"about_edge": DOWN},
        )
        v_line.resume_updating()
        self.add(v_line, dot)

        sub_decimals = VGroup(new_formula[5], new_formula[9])
        sub_decimals.s_tracker = s_tracker

        for s in [0.94, 0.98, 0.96]:
            self.play(
                s_tracker.set_value, s,
                UpdateFromFunc(sub_decimals, update_decimals),
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


class StateIndependence(Scene):
    def construct(self):
        row = get_random_checks_and_crosses()
        row.to_edge(UP)
        # self.add(row)

        arrows = VGroup()
        for m1, m2 in zip(row, row[1:]):
            arrow = Arrow(
                m1.get_bottom() + 0.025 * DOWN,
                m2.get_bottom(),
                path_arc=145 * DEGREES,
                max_stroke_width_to_length_ratio=10,
                max_tip_length_to_length_ratio=0.5,
            )
            arrow.tip.rotate(-10 * DEGREES)
            arrow.shift(SMALL_BUFF * DOWN)
            arrow.set_color(YELLOW)
            arrows.add(arrow)

        words = TextMobject("No influence")
        words.set_height(0.25)
        words.next_to(arrows[0], DOWN)

        self.play(
            ShowCreation(arrows[0]),
            FadeIn(words)
        )
        for i in range(10):
            self.play(
                words.next_to, arrows[i + 1], DOWN,
                FadeOut(arrows[i]),
                ShowCreation(arrows[i + 1])
            )
            last_arrow = arrows[i + 1]

        self.play(
            FadeOut(words),
            FadeOut(last_arrow),
        )


class IllustrateBinomialSetupWithCoins(Scene):
    def construct(self):
        coins = [
            get_coin("H"),
            get_coin("T"),
        ]

        coin_row = VGroup()
        for x in range(12):
            coin_row.add(random.choice(coins).copy())

        coin_row.arrange(RIGHT)
        coin_row.to_edge(UP)

        first_coin = get_random_coin(shuffle_time=2, total_time=2)
        first_coin.move_to(coin_row[0])

        brace = Brace(coin_row, UP)
        brace_label = brace.get_text("$N$ times")

        prob_label = TexMobject(
            "P(\\# 00 = k)",
            tex_to_color_map={
                "00": WHITE,
                "k": GREEN,
            }
        )
        heads = get_coin("H")
        template = prob_label.get_part_by_tex("00")
        heads.replace(template)
        prob_label.replace_submobject(
            prob_label.index_of_part(template),
            heads,
        )
        prob_label.set_height(1)
        prob_label.next_to(coin_row, DOWN, LARGE_BUFF)

        self.camera.frame.set_height(1.5 * FRAME_HEIGHT)

        self.add(first_coin)
        for x in range(4):
            self.wait()
            first_coin.suspend_updating()
            self.wait()
            first_coin.resume_updating()

        self.remove(first_coin)
        self.play(
            ShowIncreasingSubsets(coin_row, int_func=np.ceil),
            GrowFromPoint(brace, brace.get_left()),
            FadeIn(brace_label, 3 * LEFT)
        )
        self.wait()
        self.play(FadeIn(prob_label, lag_ratio=0.1))
        self.wait()


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


class Guess96Percent(Scene):
    def construct(self):
        randy = Randolph()
        randy.set_height(1)

        bubble = SpeechBubble(height=2, width=3)
        bubble.pin_to(randy)
        words = TextMobject("96$\\%$, right?")
        fix_percent(words[0][2])
        bubble.add_content(words)

        arrow = Vector(2 * RIGHT + DOWN)
        arrow.next_to(randy, RIGHT)
        arrow.shift(2 * UP)

        self.play(
            FadeIn(randy),
            ShowCreation(bubble),
            Write(words),
        )
        self.play(randy.change, "shruggie", randy.get_right() + RIGHT)
        self.play(ShowCreation(arrow))
        for x in range(2):
            self.play(Blink(randy))
            self.wait()

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

        arrow = Vector(DOWN)
        arrow.next_to(histogram.bars[10], UP, SMALL_BUFF)
        self.add(arrow)

        # Add formula
        prob_label = get_prob_review_label(10, 0)
        eq = TexMobject("=")
        formula = get_binomial_formula(10, 10, self.s)
        eq2 = TexMobject("=")
        value = DecimalNumber(dist.pmf(10), num_decimal_places=2)

        equation = VGroup(prob_label, eq, formula, eq2, value)
        equation.arrange(RIGHT)
        equation.next_to(histogram, DOWN, MED_LARGE_BUFF)

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
        self.play(FadeIn(equation))

        self.wait()
        self.play(
            FadeIn(rects),
            GrowFromCenter(brace),
            FadeIn(simpler_formula, UP)
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
        self.play(
            FadeIn(low_axes),
        )
        self.play(
            ShowCreation(v_line),
            FadeIn(dot),
        )
        self.add(graph, v_line, dot)
        self.play(ShowCreation(graph))
        self.wait()

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
            FadeIn(plot, DOWN),
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
        self.wait(2)

        self.teacher_says(
            "But first...",
            added_anims=[
                FadeOut(plot, LEFT),
                FadeOut(v_lines, LEFT),
                self.get_student_changes(
                    "erm", "erm", "erm",
                    look_at_arg=self.teacher.eyes,
                )
            ]
        )
        self.wait(5)


class Part1EndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "1stViewMaths",
            "Adam Dřínek",
            "Aidan Shenkman",
            "Alan Stein",
            "Alex Mijalis",
            "Alexis Olson",
            "Ali Yahya",
            "Andrew Busey",
            "Andrew Cary",
            "Andrew R. Whalley",
            "Aravind C V",
            "Arjun Chakroborty",
            "Arthur Zey",
            "Ashwin Siddarth",
            "Austin Goodman",
            "Avi Finkel",
            "Awoo",
            "Axel Ericsson",
            "Ayan Doss",
            "AZsorcerer",
            "Barry Fam",
            "Bernd Sing",
            "Boris Veselinovich",
            "Bradley Pirtle",
            "Brandon Huang",
            "Brian Staroselsky",
            "Britt Selvitelle",
            "Britton Finley",
            "Burt Humburg",
            "Calvin Lin",
            "Charles Southerland",
            "Charlie N",
            "Chenna Kautilya",
            "Chris Connett",
            "Christian Kaiser",
            "cinterloper",
            "Clark Gaebel",
            "Colwyn Fritze-Moor",
            "Cooper Jones",
            "Corey Ogburn",
            "D. Sivakumar",
            "Dan Herbatschek",
            "Daniel Herrera C",
            "Dave B",
            "Dave Kester",
            "dave nicponski",
            "David B. Hill",
            "David Clark",
            "David Gow",
            "Delton Ding",
            "Dominik Wagner",
            "Douglas Cantrell",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Farzaneh Sarafraz",
            "Federico Lebron",
            "Frank R. Brown, Jr.",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Hitoshi Yamauchi",
            "Ivan Sorokin",
            "Jacob Baxter",
            "Jacob Harmon",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jake Vartuli - Schonberg",
            "Jalex Stark",
            "Jameel Syed",
            "Jason Hise",
            "Jayne Gabriele",
            "Jean-Manuel Izaret",
            "Jeff Linse",
            "Jeff Straathof",
            "Jimmy Yang",
            "John C. Vesey",
            "John Haley",
            "John Le",
            "John V Wertheim",
            "Jonathan Heckerman",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Joseph Kelly",
            "Josh Kinnear",
            "Joshua Claeys",
            "Juan Benet",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Karl Niu",
            "Kartik Cating-Subramanian",
            "Kaustuv DeBiswas",
            "Killian McGuinness",
            "Kros Dai",
            "L0j1k",
            "LAI Oscar",
            "Lambda GPU Workstations",
            "Lee Redden",
            "Linh Tran",
            "Luc Ritchie",
            "Ludwig Schubert",
            "Lukas Biewald",
            "Magister Mugit",
            "Magnus Dahlström",
            "Manoj Rewatkar - RITEK SOLUTIONS",
            "Mark B Bahu",
            "Mark Heising",
            "Mark Mann",
            "Martin Price",
            "Mathias Jansson",
            "Matt Godbolt",
            "Matt Langford",
            "Matt Roveto",
            "Matt Russell",
            "Matteo Delabre",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Mia Parent",
            "Michael Hardel",
            "Michael W White",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nicholas Cahill",
            "Nikita Lesnikov",
            "Oleg Leonov",
            "Oliver Steele",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Patrick Lucas",
            "Pavel Dubov",
            "Peter Ehrnstrom",
            "Peter Mcinerney",
            "Pierre Lancien",
            "Quantopian",
            "Randy C. Will",
            "rehmi post",
            "Rex Godby",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roman Sergeychik",
            "Roobie",
            "Ryan Atallah",
            "Samuel Judge",
            "SansWord Huang",
            "Scott Gray",
            "Scott Walter, Ph.D.",
            "soekul",
            "Solara570",
            "Steve Huynh",
            "Steve Sperandeo",
            "Steven Braun",
            "Steven Siddals",
            "Stevie Metke",
            "supershabam",
            "Suteerth Vishnu",
            "Suthen Thomas",
            "Tal Einav",
            "Taras Bobrovytsky",
            "Tauba Auerbach",
            "Ted Suzman",
            "Thomas J Sargent",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tihan Seale",
            "Tyler VanValkenburg",
            "Vassili Philippov",
            "Veritasium",
            "Vignesh Ganapathi Subramanian",
            "Vinicius Reis",
            "Xuanji Li",
            "Yana Chernobilsky",
            "Yavor Ivanov",
            "YinYangBalance.Asia",
            "Yu Jun",
            "Yurii Monastyrshyn",
        ],
    }
