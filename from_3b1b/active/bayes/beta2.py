from manimlib.imports import *
from from_3b1b.active.bayes.beta_helpers import *
from from_3b1b.active.bayes.beta1 import *
from from_3b1b.old.hyperdarts import Dartboard

import scipy.stats

OUTPUT_DIRECTORY = "bayes/beta2"


class WeightedCoin(Scene):
    def construct(self):
        # Coin grid
        bools = 50 * [True] + 50 * [False]
        random.shuffle(bools)
        grid = get_coin_grid(bools)

        sorted_grid = VGroup(*grid)
        sorted_grid.submobjects.sort(key=lambda m: m.symbol)

        # Prob label
        p_label = get_prob_coin_label()
        p_label.set_height(0.7)
        p_label.to_edge(UP)

        rhs = p_label[-1]
        rhs_box = SurroundingRectangle(rhs, color=RED)
        rhs_label = TextMobject("Not necessarily")
        rhs_label.next_to(rhs_box, DOWN, LARGE_BUFF)
        rhs_label.to_edge(RIGHT)
        rhs_label.match_color(rhs_box)

        rhs_arrow = Arrow(
            rhs_label.get_top(),
            rhs_box.get_right(),
            buff=SMALL_BUFF,
            path_arc=60 * DEGREES,
            color=rhs_box.get_color()
        )

        # Introduce coin
        self.play(FadeIn(
            grid,
            run_time=2,
            rate_func=linear,
            lag_ratio=3 / len(grid),
        ))
        self.wait()
        self.play(
            grid.set_height, 5,
            grid.to_edge, DOWN,
            FadeInFromDown(p_label)
        )

        for coin in grid:
            coin.generate_target()
        sorted_coins = list(grid)
        sorted_coins.sort(key=lambda m: m.symbol)
        for c1, c2 in zip(sorted_coins, grid):
            c1.target.move_to(c2)

        self.play(
            FadeIn(rhs_label, lag_ratio=0.1),
            ShowCreation(rhs_arrow),
            ShowCreation(rhs_box),
            LaggedStartMap(
                MoveToTarget, grid,
                path_arc=30 * DEGREES,
                lag_ratio=0.01,
            ),
        )

        # Alternate weightings
        old_grid = VGroup(*sorted_coins)
        rhs_junk_on_screen = True
        for value in [0.2, 0.9, 0.0, 0.31]:
            n = int(100 * value)
            new_grid = get_coin_grid([True] * n + [False] * (100 - n))
            new_grid.replace(grid)

            anims = []
            if rhs_junk_on_screen:
                anims += [
                    FadeOut(rhs_box),
                    FadeOut(rhs_label),
                    FadeOut(rhs_arrow),
                ]
                rhs_junk_on_screen = False

            self.wait()
            self.play(
                FadeOut(
                    old_grid,
                    0.1 * DOWN,
                    lag_ratio=0.01,
                    run_time=1.5
                ),
                FadeIn(new_grid, lag_ratio=0.01, run_time=1.5),
                ChangeDecimalToValue(rhs, value),
                *anims,
            )
            old_grid = new_grid

        long_rhs = DecimalNumber(
            0.31415926,
            num_decimal_places=8,
            show_ellipsis=True,
        )
        long_rhs.match_height(rhs)
        long_rhs.move_to(rhs, DL)

        self.play(ShowIncreasingSubsets(long_rhs, rate_func=linear))
        self.wait()

        # You just don't know
        box = get_q_box(rhs)

        self.remove(rhs)
        self.play(
            FadeOut(old_grid, lag_ratio=0.1),
            FadeOut(long_rhs, 0.1 * RIGHT, lag_ratio=0.1),
            Write(box),
        )
        p_label.add(box)
        self.wait()

        # 7/10 heads
        bools = [True] * 7 + [False] * 3
        random.shuffle(bools)
        coins = VGroup(*[
            get_coin("H" if heads else "T")
            for heads in bools
        ])
        coins.arrange(RIGHT)
        coins.set_height(0.7)
        coins.next_to(p_label, DOWN, buff=LARGE_BUFF)

        heads_arrows = VGroup(*[
            Vector(
                0.5 * UP,
                max_stroke_width_to_length_ratio=15,
                max_tip_length_to_length_ratio=0.4,
            ).next_to(coin, DOWN)
            for coin in coins
            if coin.symbol == "H"
        ])
        numbers = VGroup(*[
            Integer(i + 1).next_to(arrow, DOWN, SMALL_BUFF)
            for i, arrow in enumerate(heads_arrows)
        ])

        for coin in coins:
            coin.save_state()
            coin.stretch(0, 0)
            coin.set_opacity(0)

        self.play(LaggedStartMap(Restore, coins), run_time=1)
        self.play(
            ShowIncreasingSubsets(heads_arrows),
            ShowIncreasingSubsets(numbers),
            rate_func=linear,
        )
        self.wait()

        # Plot
        axes = scaled_pdf_axes()
        axes.to_edge(DOWN, buff=MED_SMALL_BUFF)
        axes.y_axis.numbers.set_opacity(0)
        axes.y_axis_label.set_opacity(0)

        x_axis_label = p_label[:4].copy()
        x_axis_label.set_height(0.4)
        x_axis_label.next_to(axes.c2p(1, 0), UR, buff=SMALL_BUFF)
        axes.x_axis.add(x_axis_label)

        n_heads = 7
        n_tails = 3
        graph = get_beta_graph(axes, n_heads, n_tails)
        dist = scipy.stats.beta(n_heads + 1, n_tails + 1)
        true_graph = axes.get_graph(dist.pdf)

        v_line = Line(
            axes.c2p(0.7, 0),
            axes.input_to_graph_point(0.7, true_graph),
        )
        v_line.set_stroke(YELLOW, 4)

        region = get_region_under_curve(axes, true_graph, 0.6, 0.8)
        region.set_fill(GREY, 0.85)
        region.set_stroke(YELLOW, 1)

        eq_label = VGroup(
            p_label[:4].copy(),
            TexMobject("= 0.7"),
        )
        for mob in eq_label:
            mob.set_height(0.4)
        eq_label.arrange(RIGHT, buff=SMALL_BUFF)
        pp_label = VGroup(
            TexMobject("P("),
            eq_label,
            TexMobject(")"),
        )
        for mob in pp_label[::2]:
            mob.set_height(0.7)
            mob.set_color(YELLOW)
        pp_label.arrange(RIGHT, buff=SMALL_BUFF)
        pp_label.move_to(axes.c2p(0.3, 3))

        self.play(
            FadeOut(heads_arrows),
            FadeOut(numbers),
            Write(axes),
            DrawBorderThenFill(graph),
        )
        self.play(
            FadeIn(pp_label[::2]),
            ShowCreation(v_line),
        )
        self.wait()
        self.play(TransformFromCopy(p_label[:4], eq_label[0]))
        self.play(
            GrowFromPoint(eq_label[1], v_line.get_center())
        )
        self.wait()

        # Look confused
        randy = Randolph()
        randy.set_height(1.5)
        randy.next_to(axes.c2p(0, 0), UR, MED_LARGE_BUFF)

        self.play(FadeIn(randy))
        self.play(randy.change, "confused", pp_label.get_top())
        self.play(Blink(randy))
        self.wait()
        self.play(FadeOut(randy))

        # Remind what the title is
        title = TextMobject(
            "Probabilities", "of", "Probabilities"
        )
        title.arrange(DOWN, aligned_edge=LEFT)
        title.next_to(axes.c2p(0, 0), UR, buff=MED_LARGE_BUFF)
        title.align_to(pp_label, LEFT)

        self.play(ShowIncreasingSubsets(title, rate_func=linear))
        self.wait()
        self.play(FadeOut(title))

        # Continuous values
        v_line.tracker = ValueTracker(0.7)
        v_line.axes = axes
        v_line.graph = true_graph
        v_line.add_updater(
            lambda m: m.put_start_and_end_on(
                m.axes.c2p(m.tracker.get_value(), 0),
                m.axes.input_to_graph_point(m.tracker.get_value(), m.graph),
            )
        )

        for value in [0.4, 0.9, 0.7]:
            self.play(
                v_line.tracker.set_value, value,
                run_time=3,
            )

        # Label h
        brace = Brace(rhs_box, DOWN, buff=SMALL_BUFF)
        h_label = TexMobject("h", buff=SMALL_BUFF)
        h_label.set_color(YELLOW)
        h_label.next_to(brace, DOWN)

        self.play(
            LaggedStartMap(FadeOutAndShift, coins, lambda m: (m, DOWN)),
            GrowFromCenter(brace),
            Write(h_label),
        )
        self.wait()

        # End
        self.embed()


class Eq70(Scene):
    def construct(self):
        label = TexMobject("=", "70", "\\%", "?")
        fix_percent(label.get_part_by_tex("\\%")[0])
        self.play(FadeIn(label))
        self.wait()


class ShowInfiniteContinuum(Scene):
    def construct(self):
        # Axes
        axes = scaled_pdf_axes()
        axes.to_edge(DOWN, buff=MED_SMALL_BUFF)
        axes.y_axis.numbers.set_opacity(0)
        axes.y_axis_label.set_opacity(0)
        self.add(axes)

        # Label
        p_label = get_prob_coin_label()
        p_label.set_height(0.7)
        p_label.to_edge(UP)
        box = get_q_box(p_label[-1])
        p_label.add(box)

        brace = Brace(box, DOWN, buff=SMALL_BUFF)
        h_label = TexMobject("h")
        h_label.next_to(brace, DOWN)
        h_label.set_color(YELLOW)
        eq = TexMobject("=")
        eq.next_to(h_label, RIGHT)
        value = DecimalNumber(0, num_decimal_places=4)
        value.match_height(h_label)
        value.next_to(eq, RIGHT)
        value.set_color(YELLOW)

        self.add(p_label)
        self.add(brace)
        self.add(h_label)

        # Moving h
        h_part = h_label.copy()
        x_line = Line(axes.c2p(0, 0), axes.c2p(1, 0))
        x_line.set_stroke(YELLOW, 3)

        self.play(
            h_part.next_to, x_line.get_start(), UR, SMALL_BUFF,
            Write(eq),
            FadeInFromPoint(value, h_part.get_center()),
        )

        # Scan continuum
        h_part.tracked = x_line
        value.tracked = x_line
        value.x_axis = axes.x_axis
        self.play(
            ShowCreation(x_line),
            UpdateFromFunc(
                h_part,
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
            FadeOut(eq),
            FadeOut(value),
        )

        # Arrows
        arrows = VGroup()
        arrow_template = Vector(DOWN)
        arrow_template.lock_triangulation()

        def get_arrow(s, denom, arrow_template=arrow_template, axes=axes):
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
            "lag_ratio": 0.05,
            "run_time": 5,
            "rate_func": lambda t: t**5,
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
            lag_ratio=10 / len(arrows),
            rate_func=smooth,
            run_time=3,
        ))
        self.remove(arrows)
        self.wait()


class TitleCard(Scene):
    def construct(self):
        text = TextMobject("A beginner's guide to\\\\probability density")
        text.scale(2)
        text.to_edge(UP, buff=1.5)

        subtext = TextMobject("Probabilities of probabilities, ", "part 2")
        subtext.set_width(FRAME_WIDTH - 3)
        subtext[0].set_color(BLUE)
        subtext.next_to(text, DOWN, LARGE_BUFF)

        self.add(text)
        self.play(FadeIn(subtext, lag_ratio=0.1, run_time=2))
        self.wait(2)


class NamePdfs(Scene):
    def construct(self):
        label = TextMobject("Probability density\\\\function")
        self.play(Write(label))
        self.wait()


class LabelH(Scene):
    def construct(self):
        p_label = get_prob_coin_label()
        p_label.scale(1.5)
        brace = Brace(p_label, DOWN)
        h = TexMobject("h")
        h.scale(2)
        h.next_to(brace, DOWN)

        self.add(p_label)
        self.play(ShowCreationThenFadeAround(p_label))
        self.play(
            GrowFromCenter(brace),
            FadeIn(h, UP),
        )
        self.wait()


class DrawUnderline(Scene):
    def construct(self):
        line = Line(2 * LEFT, 2 * RIGHT)
        line.set_stroke(PINK, 5)
        self.play(ShowCreation(line))
        self.wait()
        line.reverse_points()
        self.play(Uncreate(line))


class TryAssigningProbabilitiesToSpecificValues(Scene):
    def construct(self):
        # To get "P(s = .7000001) = ???" type labels
        def get_p_label(value):
            result = TexMobject(
                # "P(", "{s}", "=", value, "\\%", ")",
                "P(", "{h}", "=", value, ")",
            )
            # fix_percent(result.get_part_by_tex("\\%")[0])
            result.set_color_by_tex("{h}", YELLOW)
            return result

        labels = VGroup(
            get_p_label("0.70000000"),
            get_p_label("0.70000001"),
            get_p_label("0.70314159"),
            get_p_label("0.70271828"),
            get_p_label("0.70466920"),
            get_p_label("0.70161803"),
        )
        labels.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        labels.set_height(4.5)
        labels.to_edge(DOWN, buff=LARGE_BUFF)

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
        self.play(FadeIn(q_marks[0], LEFT))
        self.wait()
        self.play(*[
            TransformFromCopy(m1, m2)
            for m1, m2 in [
                (q_marks[0], q_marks[1]),
                (labels[0][:3], labels[1][:3]),
                (labels[0][-1], labels[1][-1]),
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
            "\\sum_{0 \\le {h} \\le 1}", "P(", "{h}", ")", "=",
            tex_to_color_map={"{h}": YELLOW},
        )
        # sum_label.set_color_by_tex("{s}", YELLOW)
        sum_label[0].set_color(WHITE)
        sum_label.scale(1.75)
        sum_label.next_to(ORIGIN, RIGHT, buff=1)
        sum_label.shift(LEFT)

        morty = Mortimer()
        morty.set_height(2)
        morty.to_corner(DR)

        self.play(group.to_corner, DL)
        self.play(
            Write(sum_label),
            VFadeIn(morty),
            morty.change, "confused", sum_label,
        )

        infty = TexMobject("\\infty")
        zero = TexMobject("0")
        for mob in [infty, zero]:
            mob.scale(2)
            mob.next_to(sum_label[-1], RIGHT)
        zero.set_color(RED)
        zero.shift(SMALL_BUFF * RIGHT)

        self.play(
            Write(infty),
            morty.change, "horrified", infty,
        )
        self.play(Blink(morty))
        self.wait()

        # If equal to zero
        eq_zero.move_to(gt_zero)
        eq_zero.set_color(RED)
        gt_zero.unlock_triangulation()
        self.play(
            ReplacementTransform(
                gt_zero, eq_zero,
                lag_ratio=0.05,
                run_time=2,
                path_arc=30 * DEGREES,
            ),
            morty.change, "pondering", eq_zero,
        )
        self.wait()
        self.play(
            FadeIn(zero, DOWN),
            FadeOut(infty, UP),
            morty.change, "sad", zero
        )
        self.play(Blink(morty))
        self.wait()


class WanderingArrow(Scene):
    def construct(self):
        arrow = Vector(0.8 * DOWN)
        arrow.move_to(4 * LEFT, DOWN)
        for u in [1, -1, 1, -1, 1]:
            self.play(
                arrow.shift, u * 8 * RIGHT,
                run_time=3
            )


class ProbabilityToContinuousValuesSupplement(Scene):
    def construct(self):
        nl = UnitInterval()
        nl.set_width(10)
        nl.add_numbers(
            *np.arange(0, 1.1, 0.1),
            buff=0.3,
        )
        nl.to_edge(LEFT)
        self.add(nl)

        def f(x):
            return -100 * (x - 0.6) * (x - 0.8)

        values = np.linspace(0.65, 0.75, 100)
        lines = VGroup()
        for x, color in zip(values, it.cycle([BLUE_E, BLUE_C])):
            line = Line(ORIGIN, UP)
            line.set_height(f(x))
            line.set_stroke(color, 1)
            line.move_to(nl.n2p(x), DOWN)
            lines.add(line)

        self.play(ShowCreation(lines, lag_ratio=0.9, run_time=5))

        lines_row = lines.copy()
        lines_row.generate_target()
        for lt in lines_row.target:
            lt.rotate(90 * DEGREES)
        lines_row.target.arrange(RIGHT, buff=0)
        lines_row.target.set_stroke(width=4)
        lines_row.target.next_to(nl, UP, LARGE_BUFF)
        lines_row.target.align_to(nl.n2p(0), LEFT)

        self.play(
            MoveToTarget(
                lines_row,
                lag_ratio=0.1,
                rate_func=rush_into,
                run_time=4,
            )
        )
        self.wait()
        self.play(
            lines.set_height, 0.01, {"about_edge": DOWN, "stretch": True},
            ApplyMethod(
                lines_row.set_width, 0.01, {"about_edge": LEFT},
                rate_func=rush_into,
            ),
            run_time=6,
        )
        self.wait()


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
            TextMobject("What can you say"),
            TexMobject(
                "\\text{about } P(\\text{defect})?",
                tex_to_color_map={"\\text{defect}": RED}
            )
        )

        question.arrange(DOWN, aligned_edge=LEFT)
        question.next_to(denom_words, DOWN, buff=1.5, aligned_edge=LEFT)

        self.play(FadeIn(question))
        self.wait()


class TeacherHoldingValue(TeacherStudentsScene):
    def construct(self):
        self.play(self.teacher.change, "raise_right_hand", self.screen)
        self.change_all_student_modes(
            "pondering",
            look_at_arg=self.screen,
        )
        self.wait(8)


class ShowLimitToPdf(Scene):
    def construct(self):
        # Init
        axes = self.get_axes()
        alpha = 4
        beta = 2
        dist = scipy.stats.beta(alpha, beta)
        bars = self.get_bars(axes, dist, 0.05)

        axis_prob_label = TextMobject("Probability")
        axis_prob_label.next_to(axes.y_axis, UP)
        axis_prob_label.to_edge(LEFT)

        self.add(axes)
        self.add(axis_prob_label)

        # From individual to ranges
        kw = {"tex_to_color_map": {"h": YELLOW}}
        eq_label = TexMobject("P(h = 0.8)", **kw)
        ineq_label = TexMobject("P(0.8 < h < 0.85)", **kw)

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
            FadeIn(eq_label, 0.2 * DOWN),
            GrowArrow(arrows[0]),
        )
        self.wait()
        vect = eq_label.get_center() - ineq_label.get_center()
        self.play(
            FadeOut(eq_label, -vect),
            FadeIn(ineq_label, vect),
            TransformFromCopy(*arrows),
            GrowFromPoint(brace, brace.get_left()),
        )
        self.wait()

        # Bars
        arrow = arrows[0]
        arrow.generate_target()
        arrow.target.next_to(bars[16], UP, SMALL_BUFF)
        highlighted_bar_color = RED_E
        bars[16].set_color(highlighted_bar_color)

        for bar in bars:
            bar.save_state()
            bar.stretch(0, 1, about_edge=DOWN)

        kw = {
            "run_time": 2,
            "rate_func": squish_rate_func(smooth, 0.3, 0.9),
        }
        self.play(
            MoveToTarget(arrow, **kw),
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
            FadeOut(axis_prob_label, LEFT)
        )
        self.wait()
        self.play(
            FadeOut(height_word, UP),
            FadeOut(height_cross, UP),
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

        # Ask about where values come from
        randy = Randolph(height=1)
        randy.next_to(prob_label, UP, aligned_edge=LEFT)

        bubble = SpeechBubble(
            height=2,
            width=4,
        )
        bubble.move_to(randy.get_corner(UR), DL)
        bubble.write("Where do these\\\\probabilities come from?")

        self.play(
            FadeIn(randy),
            ShowCreation(bubble),
        )
        self.play(
            randy.change, "confused",
            FadeIn(bubble.content, lag_ratio=0.1)
        )
        self.play(Blink(randy))

        bars.generate_target()
        bars.save_state()
        bars.target.arrange(RIGHT, buff=SMALL_BUFF, aligned_edge=DOWN)
        bars.target.next_to(bars.get_bottom(), UP)

        self.play(MoveToTarget(bars))
        self.play(LaggedStartMap(Indicate, bars, scale_factor=1.05), run_time=1)
        self.play(Restore(bars))
        self.play(Blink(randy))
        self.play(
            FadeOut(randy),
            FadeOut(bubble),
            FadeOut(bubble.content),
        )

        # Refine
        last_ineq_label = ineq_label
        last_bars = bars
        all_ineq_labels = VGroup(ineq_label)
        for step_size in [0.025, 0.01, 0.005, 0.001]:
            new_bars = self.get_bars(axes, dist, step_size)
            new_ineq_label = TexMobject(
                "P(0.8 < h < {:.3})".format(0.8 + step_size),
                tex_to_color_map={"h": YELLOW},
            )

            if step_size <= 0.005:
                new_bars.set_stroke(width=0)

            arrow.generate_target()
            bar = new_bars[int(0.8 * len(new_bars))]
            bar.set_color(highlighted_bar_color)
            arrow.target.next_to(bar, UP, SMALL_BUFF)
            new_ineq_label.next_to(arrow.target, UP)

            vect = new_ineq_label.get_center() - last_ineq_label.get_center()

            self.wait()
            self.play(
                ReplacementTransform(
                    last_bars, new_bars,
                    lag_ratio=step_size,
                ),
                MoveToTarget(arrow),
                FadeOut(last_ineq_label, vect),
                FadeIn(new_ineq_label, -vect),
                run_time=2,
            )
            last_ineq_label = new_ineq_label
            last_bars = new_bars
            all_ineq_labels.add(new_ineq_label)

        # Show continuous graph
        graph = get_beta_graph(axes, alpha - 1, beta - 1)
        graph_curve = axes.get_graph(dist.pdf)
        graph_curve.set_stroke([YELLOW, GREEN])

        limit_words = TextMobject("In the limit...")
        limit_words.next_to(
            axes.input_to_graph_point(0.75, graph_curve),
            UP, MED_LARGE_BUFF,
        )

        self.play(
            FadeIn(graph),
            FadeOut(last_ineq_label),
            FadeOut(arrow),
            FadeOut(last_bars),
        )
        self.play(
            ShowCreation(graph_curve),
            Write(limit_words, run_time=1)
        )
        self.play(FadeOut(graph_curve))
        self.wait()

        # Show individual probabilities goes to zero
        all_ineq_labels.arrange(DOWN, aligned_edge=LEFT)
        all_ineq_labels.move_to(prob_label, LEFT)
        all_ineq_labels.to_edge(UP)

        prob_label.generate_target()
        prob_label.target.next_to(
            all_ineq_labels, DOWN,
            buff=MED_LARGE_BUFF,
            aligned_edge=LEFT
        )

        rhss = VGroup()
        step_sizes = [0.05, 0.025, 0.01, 0.005, 0.001]
        for label, step in zip(all_ineq_labels, step_sizes):
            eq = TexMobject("=")
            decimal = DecimalNumber(
                dist.cdf(0.8 + step) - dist.cdf(0.8),
                num_decimal_places=3,
            )
            eq.next_to(label, RIGHT)
            decimal.next_to(eq, RIGHT)
            decimal.set_stroke(BLACK, 3, background=True)
            rhss.add(VGroup(eq, decimal))

        for rhs in rhss:
            rhs.align_to(rhss[1], LEFT)

        VGroup(all_ineq_labels, rhss).set_height(3, about_edge=UL)

        arrow = Arrow(rhss.get_top(), rhss.get_bottom(), buff=0)
        arrow.next_to(rhss, RIGHT)
        arrow.set_color(YELLOW)
        to_zero_words = TextMobject("Individual probabilites\\\\", "go to zero")
        to_zero_words[1].align_to(to_zero_words[0], LEFT)
        to_zero_words.next_to(arrow, RIGHT, aligned_edge=UP)

        self.play(
            LaggedStartMap(
                FadeInFrom, all_ineq_labels,
                lambda m: (m, UP),
            ),
            LaggedStartMap(
                FadeInFrom, rhss,
                lambda m: (m, UP),
            ),
            MoveToTarget(prob_label)
        )
        self.play(
            GrowArrow(arrow),
            FadeIn(to_zero_words),
        )
        self.play(
            LaggedStartMap(
                Indicate, rhss,
                scale_factor=1.05,
            )
        )
        self.wait(2)

        # What if it was heights
        bars.restore()
        height_word.move_to(area_word, RIGHT)
        height_word.set_color(PINK)
        step = 0.05
        new_y_numbers = VGroup(*[
            DecimalNumber(x) for x in np.arange(step, 5 * step, step)
        ])
        for n1, n2 in zip(axes.y_axis.numbers, new_y_numbers):
            n2.match_height(n1)
            n2.add_background_rectangle(
                opacity=1,
                buff=SMALL_BUFF,
            )
            n2.move_to(n1, RIGHT)

        self.play(
            FadeOut(limit_words),
            FadeOut(graph),
            FadeIn(bars),
            FadeOut(area_word, UP),
            FadeIn(height_word, DOWN),
            FadeIn(new_y_numbers, 0.5 * RIGHT),
        )

        # Height refine
        rect = SurroundingRectangle(rhss[0][1])
        rect.set_stroke(RED, 3)
        self.play(FadeIn(rect))

        last_bars = bars
        for step_size, rhs in zip(step_sizes[1:], rhss[1:]):
            new_bars = self.get_bars(axes, dist, step_size)
            bar = new_bars[int(0.8 * len(new_bars))]
            bar.set_color(highlighted_bar_color)
            new_bars.stretch(
                step_size / 0.05, 1,
                about_edge=DOWN,
            )
            if step_size <= 0.05:
                new_bars.set_stroke(width=0)
            self.remove(last_bars)
            self.play(
                TransformFromCopy(last_bars, new_bars, lag_ratio=step_size),
                rect.move_to, rhs[1],
            )
            last_bars = new_bars
        self.play(
            FadeOut(last_bars),
            FadeOutAndShiftDown(rect),
        )
        self.wait()

        # Back to area
        self.play(
            FadeIn(graph),
            FadeIn(area_word, 0.5 * DOWN),
            FadeOut(height_word, 0.5 * UP),
            FadeOut(new_y_numbers, lag_ratio=0.2),
        )
        self.play(
            arrow.scale, 0, {"about_edge": DOWN},
            FadeOut(to_zero_words, DOWN),
            LaggedStartMap(FadeOutAndShiftDown, all_ineq_labels),
            LaggedStartMap(FadeOutAndShiftDown, rhss),
        )
        self.wait()

        # Ask about y_axis units
        arrow = Arrow(
            axes.y_axis.get_top() + 3 * RIGHT,
            axes.y_axis.get_top(),
            path_arc=90 * DEGREES,
        )
        question = TextMobject("What are the\\\\units here?")
        question.next_to(arrow.get_start(), DOWN)

        self.play(
            FadeIn(question, lag_ratio=0.1),
            ShowCreation(arrow),
        )
        self.wait()

        # Bring back bars
        bars = self.get_bars(axes, dist, 0.05)
        self.play(
            FadeOut(graph),
            FadeIn(bars),
        )
        bars.generate_target()
        bars.save_state()
        bars.target.set_opacity(0.2)
        bar_index = int(0.8 * len(bars))
        bars.target[bar_index].set_opacity(0.8)
        bar = bars[bar_index]

        prob_word = TextMobject("Probability")
        prob_word.rotate(90 * DEGREES)
        prob_word.set_height(0.8 * bar.get_height())
        prob_word.move_to(bar)

        self.play(
            MoveToTarget(bars),
            Write(prob_word, run_time=1),
        )
        self.wait()

        # Show dimensions of bar
        top_brace = Brace(bar, UP)
        side_brace = Brace(bar, LEFT)
        top_label = top_brace.get_tex("\\Delta x")
        side_label = side_brace.get_tex(
            "{\\text{Prob.} \\over \\Delta x}"
        )

        self.play(
            GrowFromCenter(top_brace),
            FadeIn(top_label),
        )
        self.play(GrowFromCenter(side_brace))
        self.wait()
        self.play(Write(side_label))
        self.wait()

        y_label = TextMobject("Probability density")
        y_label.next_to(axes.y_axis, UP, aligned_edge=LEFT)

        self.play(
            Uncreate(arrow),
            FadeOutAndShiftDown(question),
            Write(y_label),
        )
        self.wait(2)
        self.play(
            Restore(bars),
            FadeOut(top_brace),
            FadeOut(side_brace),
            FadeOut(top_label),
            FadeOut(side_label),
            FadeOut(prob_word),
        )

        # Point out total area is 1
        total_label = TextMobject("Total area = 1")
        total_label.set_height(0.5)
        total_label.next_to(bars, UP, LARGE_BUFF)

        self.play(FadeIn(total_label, DOWN))
        bars.save_state()
        self.play(
            bars.arrange, RIGHT, {"aligned_edge": DOWN, "buff": SMALL_BUFF},
            bars.move_to, bars.get_bottom() + 0.5 * UP, DOWN,
        )
        self.play(LaggedStartMap(Indicate, bars, scale_factor=1.05))
        self.play(Restore(bars))

        # Refine again
        for step_size in step_sizes[1:]:
            new_bars = self.get_bars(axes, dist, step_size)
            if step_size <= 0.05:
                new_bars.set_stroke(width=0)
            self.play(
                ReplacementTransform(
                    bars, new_bars, lag_ratio=step_size
                ),
                run_time=3,
            )
            self.wait()
            bars = new_bars
        self.add(graph, total_label)
        self.play(
            FadeIn(graph),
            FadeOut(bars),
            total_label.move_to, axes.c2p(0.7, 0.8)
        )
        self.wait()

        # Name pdf
        func_name = TextMobject("Probability ", "Density ", "Function")
        initials = TextMobject("P", "D", "F")
        for mob in func_name, initials:
            mob.set_color(YELLOW)
            mob.next_to(axes.input_to_graph_point(0.75, graph_curve), UP)

        self.play(
            ShowCreation(graph_curve),
            Write(func_name, run_time=1),
        )
        self.wait()
        func_name_copy = func_name.copy()
        self.play(
            func_name.next_to, initials, UP,
            *[
                ReplacementTransform(np[0], ip[0])
                for np, ip in zip(func_name_copy, initials)
            ],
            *[
                FadeOut(np[1:])
                for np in func_name_copy
            ]
        )
        self.add(initials)
        self.wait()
        self.play(
            FadeOut(func_name),
            FadeOut(total_label),
            FadeOut(graph_curve),
            initials.next_to, axes.input_to_graph_point(0.95, graph_curve), UR,
        )

        # Look at bounded area
        min_x = 0.6
        max_x = 0.8
        region = get_region_under_curve(axes, graph_curve, min_x, max_x)
        area_label = DecimalNumber(
            dist.cdf(max_x) - dist.cdf(min_x),
            num_decimal_places=3,
        )
        area_label.move_to(region)

        v_lines = VGroup()
        for x in [min_x, max_x]:
            v_lines.add(
                DashedLine(
                    axes.c2p(x, 0),
                    axes.c2p(x, 2.5),
                )
            )
        v_lines.set_stroke(YELLOW, 2)

        p_label = VGroup(
            TexMobject("P("),
            DecimalNumber(min_x),
            TexMobject("\\le"),
            TexMobject("h", color=YELLOW),
            TexMobject("\\le"),
            DecimalNumber(max_x),
            TexMobject(")")
        )
        p_label.arrange(RIGHT, buff=0.25)
        VGroup(p_label[0], p_label[-1]).space_out_submobjects(0.92)
        p_label.next_to(v_lines, UP)

        rhs = VGroup(
            TexMobject("="),
            area_label.copy()
        )
        rhs.arrange(RIGHT)
        rhs.next_to(p_label, RIGHT)

        self.play(
            FadeIn(p_label, 2 * DOWN),
            *map(ShowCreation, v_lines),
        )
        self.wait()
        region.func = get_region_under_curve
        self.play(
            UpdateFromAlphaFunc(
                region,
                lambda m, a: m.become(
                    m.func(
                        m.axes, m.graph,
                        m.min_x,
                        interpolate(m.min_x, m.max_x, a)
                    )
                )
            ),
            CountInFrom(area_label),
            UpdateFromAlphaFunc(
                area_label,
                lambda m, a: m.set_opacity(a),
            ),
        )
        self.wait()
        self.play(
            TransformFromCopy(area_label, rhs[1]),
            Write(rhs[0]),
        )
        self.wait()

        # Change range
        new_x = np.mean([min_x, max_x])
        area_label.original_width = area_label.get_width()
        region.new_x = new_x
        # Squish to area 1
        self.play(
            ChangeDecimalToValue(p_label[1], new_x),
            ChangeDecimalToValue(p_label[5], new_x),
            ChangeDecimalToValue(area_label, 0),
            UpdateFromAlphaFunc(
                area_label,
                lambda m, a: m.set_width(
                    interpolate(m.original_width, 1e-6, a)
                )
            ),
            ChangeDecimalToValue(rhs[1], 0),
            v_lines[0].move_to, axes.c2p(new_x, 0), DOWN,
            v_lines[1].move_to, axes.c2p(new_x, 0), DOWN,
            UpdateFromAlphaFunc(
                region,
                lambda m, a: m.become(m.func(
                    m.axes, m.graph,
                    interpolate(m.min_x, m.new_x, a),
                    interpolate(m.max_x, m.new_x, a),
                ))
            ),
            run_time=2,
        )
        self.wait()

        # Stretch to area 1
        self.play(
            ChangeDecimalToValue(p_label[1], 0),
            ChangeDecimalToValue(p_label[5], 1),
            ChangeDecimalToValue(area_label, 1),
            UpdateFromAlphaFunc(
                area_label,
                lambda m, a: m.set_width(
                    interpolate(1e-6, m.original_width, clip(5 * a, 0, 1))
                )
            ),
            ChangeDecimalToValue(rhs[1], 1),
            v_lines[0].move_to, axes.c2p(0, 0), DOWN,
            v_lines[1].move_to, axes.c2p(1, 0), DOWN,
            UpdateFromAlphaFunc(
                region,
                lambda m, a: m.become(m.func(
                    m.axes, m.graph,
                    interpolate(m.new_x, 0, a),
                    interpolate(m.new_x, 1, a),
                ))
            ),
            run_time=5,
        )
        self.wait()

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

        h_label = TexMobject("h")
        h_label.set_color(YELLOW)
        h_label.next_to(axes.x_axis.n2p(1), UR, buff=0.2)
        axes.x_axis.add(h_label)
        axes.x_axis.label = h_label

        axes.x_axis.add_numbers(
            *np.arange(0.2, 1.2, 0.2),
            number_config={"num_decimal_places": 1}
        )
        axes.y_axis.add_numbers(*range(1, 5))
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


class FiniteVsContinuum(Scene):
    def construct(self):
        # Title
        f_title = TextMobject("Discrete context")
        f_title.set_height(0.5)
        f_title.to_edge(UP)
        f_underline = Underline(f_title)
        f_underline.scale(1.3)
        f_title.add(f_underline)
        self.add(f_title)

        # Equations
        dice = get_die_faces()[::2]
        cards = [PlayingCard(letter + "H") for letter in "A35"]

        eqs = VGroup(
            self.get_union_equation(dice),
            self.get_union_equation(cards),
        )
        for eq in eqs:
            eq.set_width(FRAME_WIDTH - 1)
        eqs.arrange(DOWN, buff=LARGE_BUFF)
        eqs.next_to(f_underline, DOWN, LARGE_BUFF)

        anims = []
        for eq in eqs:
            movers = eq.mob_copies1.copy()
            for m1, m2 in zip(movers, eq.mob_copies2):
                m1.generate_target()
                m1.target.replace(m2)
            eq.mob_copies2.set_opacity(0)
            eq.add(movers)

            self.play(FadeIn(eq[0]))

            anims.append(FadeIn(eq[1:]))
            anims.append(LaggedStartMap(
                MoveToTarget, movers,
                path_arc=30 * DEGREES,
                lag_ratio=0.1,
            ))
        self.wait()
        for anim in anims:
            self.play(anim)

        # Continuum label
        c_title = TextMobject("Continuous context")
        c_title.match_height(f_title)
        c_underline = Underline(c_title)
        c_underline.scale(1.25)

        self.play(
            Write(c_title, run_time=1),
            ShowCreation(c_underline),
            eqs[0].shift, 0.5 * UP,
            eqs[1].shift, UP,
        )

        # Range sum
        c_eq = TexMobject(
            "P\\big(", "x \\in [0.65, 0.75]", "\\big)",
            "=",
            "\\sum_{x \\in [0.65, 0.75]}",
            "P(", "x", ")",
        )
        c_eq.set_color_by_tex("P", YELLOW)
        c_eq.set_color_by_tex(")", YELLOW)
        c_eq.next_to(c_underline, DOWN, LARGE_BUFF)
        c_eq.to_edge(LEFT)

        equals = c_eq.get_part_by_tex("=")
        equals.shift(SMALL_BUFF * RIGHT)
        e_cross = Line(DL, UR)
        e_cross.replace(equals, dim_to_match=0)
        e_cross.set_stroke(RED, 5)

        self.play(FadeIn(c_eq))
        self.wait(2)
        self.play(ShowCreation(e_cross))
        self.wait()

    def get_union_equation(self, mobs):
        mob_copies1 = VGroup()
        mob_copies2 = VGroup()
        p_color = YELLOW

        # Create mob_set
        brackets = TexMobject("\\big\\{\\big\\}")[0]
        mob_set = VGroup(brackets[0])
        commas = VGroup()
        for mob in mobs:
            mc = mob.copy()
            mc.match_height(mob_set[0])
            mob_copies1.add(mc)
            comma = TexMobject(",")
            commas.add(comma)
            mob_set.add(mc)
            mob_set.add(comma)

        mob_set.remove(commas[-1])
        commas.remove(commas[-1])
        mob_set.add(brackets[1])
        mob_set.arrange(RIGHT, buff=0.15)
        commas.set_y(mob_set[1].get_bottom()[1])

        mob_set.scale(0.8)

        # Create individual probabilities
        probs = VGroup()
        for mob in mobs:
            prob = TexMobject("P(", "x = ", "00", ")")
            index = prob.index_of_part_by_tex("00")
            mc = mob.copy()
            mc.replace(prob[index])
            mc.scale(0.8, about_edge=LEFT)
            mc.match_y(prob[-1])
            mob_copies2.add(mc)
            prob.replace_submobject(index, mc)
            prob[0].set_color(p_color)
            prob[1].match_y(mc)
            prob[-1].set_color(p_color)
            probs.add(prob)

        # Result
        lhs = VGroup(
            TexMobject("P\\big(", color=p_color),
            TexMobject("x \\in"),
            mob_set,
            TexMobject("\\big)", color=p_color),
        )
        lhs.arrange(RIGHT, buff=SMALL_BUFF)
        group = VGroup(lhs, TexMobject("="))
        for prob in probs:
            group.add(prob)
            group.add(TexMobject("+"))
        group.remove(group[-1])

        group.arrange(RIGHT, buff=0.2)
        group.mob_copies1 = mob_copies1
        group.mob_copies2 = mob_copies2

        return group


class ComplainAboutRuleChange(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Wait, the rules\\\\changed?",
            target_mode="sassy",
            added_anims=[self.teacher.change, "tease"]
        )
        self.change_student_modes("erm", "confused")
        self.wait(4)
        self.teacher_says("You may enjoy\\\\``Measure theory''")
        self.change_all_student_modes(
            "pondering",
            look_at_arg=self.teacher.bubble
        )
        self.wait(8)


class HalfFiniteHalfContinuous(Scene):
    def construct(self):
        # Basic symbols
        box = Rectangle(width=3, height=1.2)
        box.set_stroke(WHITE, 2)
        box.set_fill(GREY_E, 1)
        box.move_to(2.5 * LEFT, RIGHT)

        arrows = VGroup()
        arrow_labels = VGroup()
        for vect in [UP, DOWN]:
            arrow = Arrow(
                box.get_corner(vect + RIGHT),
                box.get_corner(vect + RIGHT) + 3 * RIGHT + 1.5 * vect,
                buff=MED_SMALL_BUFF,
            )
            label = TexMobject("50\\%")
            fix_percent(label[0][-1])
            label.set_color(YELLOW)
            label.next_to(
                arrow.get_center(),
                vect + LEFT,
                buff=SMALL_BUFF,
            )

            arrow_labels.add(label)
            arrows.add(arrow)

        zero = Integer(0)
        zero.set_height(0.5)
        zero.next_to(arrows[0].get_end(), RIGHT)

        # Half Gaussian
        axes = Axes(
            x_min=0,
            x_max=6.5,
            y_min=0,
            y_max=0.25,
            y_axis_config={
                "tick_frequency": 1 / 16,
                "unit_size": 10,
                "include_tip": False,
            }
        )
        axes.next_to(arrows[1].get_end(), RIGHT)

        dist = scipy.stats.norm(0, 2)
        graph = axes.get_graph(dist.pdf)
        graph_fill = graph.copy()
        close_off_graph(axes, graph_fill)
        graph.set_stroke(BLUE, 3)
        graph_fill.set_fill(BLUE_E, 1)
        graph_fill.set_stroke(BLUE_E, 0)

        half_gauss = Group(
            graph, graph_fill, axes,
        )

        # Random Decimal
        number = DecimalNumber(num_decimal_places=4)
        number.set_height(0.6)
        number.move_to(box)

        number.time = 0
        number.last_change = 0
        number.change_freq = 0.2

        def update_number(number, dt, dist=dist):
            number.time += dt

            if (number.time - number.last_change) < number.change_freq:
                return

            number.last_change = number.time
            rand_val = random.random()
            if rand_val < 0.5:
                number.set_value(0)
            else:
                number.set_value(dist.ppf(rand_val))

        number.add_updater(update_number)

        v_line = SurroundingRectangle(zero)
        v_line.save_state()
        v_line.set_stroke(YELLOW, 3)

        def update_v_line(v_line, number=number, axes=axes, graph=graph):
            x = number.get_value()
            if x < 0.5:
                v_line.restore()
            else:
                v_line.set_width(1e-6)
                p1 = axes.c2p(x, 0)
                p2 = axes.input_to_graph_point(x, graph)
                v_line.set_height(get_norm(p2 - p1), stretch=True)
                v_line.move_to(p1, DOWN)

        v_line.add_updater(update_v_line)

        # Add everything
        self.add(box)
        self.add(number)
        self.wait(4)
        self.play(
            GrowArrow(arrows[0]),
            FadeIn(arrow_labels[0]),
            GrowFromPoint(zero, box.get_corner(UR))
        )
        self.wait(2)
        self.play(
            GrowArrow(arrows[1]),
            FadeIn(arrow_labels[1]),
            FadeIn(half_gauss),
        )
        self.add(v_line)

        self.wait(30)


class SumToIntegral(Scene):
    def construct(self):
        # Titles
        titles = VGroup(
            TextMobject("Discrete context"),
            TextMobject("Continuous context"),
        )
        titles.set_height(0.5)
        for title, vect in zip(titles, [LEFT, RIGHT]):
            title.move_to(vect * FRAME_WIDTH / 4)
            title.to_edge(UP, buff=MED_SMALL_BUFF)

        v_line = Line(UP, DOWN).set_height(FRAME_HEIGHT)
        h_line = Line(LEFT, RIGHT).set_width(FRAME_WIDTH)
        h_line.next_to(titles, DOWN)
        h_line.set_x(0)
        v_line.center()

        self.play(
            ShowCreation(VGroup(h_line, v_line)),
            LaggedStartMap(
                FadeInFrom, titles,
                lambda m: (m, -0.2 * m.get_center()[0] * RIGHT),
                run_time=1,
                lag_ratio=0.1,
            ),
        )
        self.wait()

        # Sum and int
        kw = {"tex_to_color_map": {"S": BLUE}}
        s_sym = TexMobject("\\sum", "_{x \\in S} P(x)", **kw)
        i_sym = TexMobject("\\int_{S} p(x)", "\\text{d}x", **kw)
        syms = VGroup(s_sym, i_sym)
        syms.scale(2)
        for sym, title in zip(syms, titles):
            sym.shift(-sym[-1].get_center())
            sym.match_x(title)

        arrow = Arrow(
            s_sym[0].get_corner(UP),
            i_sym[0].get_corner(UP),
            path_arc=-90 * DEGREES,
        )
        arrow.set_color(YELLOW)

        self.play(Write(s_sym, run_time=1))
        anims = [ShowCreation(arrow)]
        for i, j in [(0, 0), (2, 1), (3, 2)]:
            source = s_sym[i].deepcopy()
            target = i_sym[j]
            target.save_state()
            source.generate_target()
            target.replace(source, stretch=True)
            source.target.replace(target, stretch=True)
            target.set_opacity(0)
            source.target.set_opacity(0)
            anims += [
                Restore(target, path_arc=-60 * DEGREES),
                MoveToTarget(source, path_arc=-60 * DEGREES),
            ]
        self.play(LaggedStart(*anims))
        self.play(FadeInFromDown(i_sym[3]))
        self.add(i_sym)
        self.wait()
        self.play(
            FadeOut(arrow, UP),
            syms.next_to, h_line, DOWN, {"buff": MED_LARGE_BUFF},
            syms.match_x, syms,
        )

        # Add curve area in editing
        # Add bar chart
        axes = Axes(
            x_min=0,
            x_max=10,
            y_min=0,
            y_max=7,
            y_axis_config={
                "unit_size": 0.75,
            }
        )
        axes.set_width(0.5 * FRAME_WIDTH - 1)
        axes.next_to(s_sym, DOWN)
        axes.y_axis.add_numbers(2, 4, 6)

        bars = VGroup()
        for x, y in [(1, 1), (4, 3), (7, 2)]:
            bar = Rectangle()
            bar.set_stroke(WHITE, 1)
            bar.set_fill(BLUE_D, 1)
            line = Line(axes.c2p(x, 0), axes.c2p(x + 2, y))
            bar.replace(line, stretch=True)
            bars.add(bar)

        addition_formula = TexMobject(*"1+3+2")
        addition_formula.space_out_submobjects(2.1)
        addition_formula.next_to(bars, UP)

        for bar in bars:
            bar.save_state()
            bar.stretch(0, 1, about_edge=DOWN)

        self.play(
            Write(axes),
            LaggedStartMap(Restore, bars),
            LaggedStartMap(FadeInFromDown, addition_formula),
        )
        self.wait()

        # Confusion
        morty = Mortimer()
        morty.to_corner(DR)
        morty.look_at(i_sym)
        self.play(
            *map(FadeOut, [axes, bars, addition_formula]),
            FadeIn(morty)
        )
        self.play(morty.change, "maybe")
        self.play(Blink(morty))
        self.play(morty.change, "confused", i_sym.get_right())
        self.play(Blink(morty))
        self.wait()

        # Focus on integral
        self.play(
            Uncreate(VGroup(v_line, h_line)),
            FadeOut(titles, UP),
            FadeOut(morty, RIGHT),
            FadeOut(s_sym, LEFT),
            i_sym.center,
            i_sym.to_edge, LEFT
        )

        arrows = VGroup()
        for vect in [UP, DOWN]:
            corner = i_sym[-1].get_corner(RIGHT + vect)
            arrows.add(Arrow(
                corner,
                corner + 2 * RIGHT + 2 * vect,
                path_arc=-np.sign(vect[1]) * 60 * DEGREES,
            ))

        self.play(*map(ShowCreation, arrows))

        # Types of integration
        dist = scipy.stats.beta(7 + 1, 3 + 1)
        axes_pair = VGroup()
        graph_pair = VGroup()
        for arrow in arrows:
            axes = get_beta_dist_axes(y_max=5, y_unit=1)
            axes.set_width(4)
            axes.next_to(arrow.get_end(), RIGHT)
            graph = axes.get_graph(dist.pdf)
            graph.set_stroke(BLUE, 2)
            graph.set_fill(BLUE_E, 0)
            graph.make_smooth()
            axes_pair.add(axes)
            graph_pair.add(graph)

        r_axes, l_axes = axes_pair
        r_graph, l_graph = graph_pair
        r_name = TextMobject("Riemann\\\\Integration")
        r_name.next_to(r_axes, RIGHT)
        l_name = TextMobject("Lebesgue\\\\Integration$^*$")
        l_name.next_to(l_axes, RIGHT)
        footnote = TextMobject("*a bit more complicated than\\\\these bars make it look")
        footnote.match_width(l_name)
        footnote.next_to(l_name, DOWN)

        self.play(LaggedStart(
            FadeIn(r_axes),
            FadeIn(r_graph),
            FadeIn(r_name),
            FadeIn(l_axes),
            FadeIn(l_graph),
            FadeIn(l_name),
            run_time=1,
        ))

        # Approximation bars
        def get_riemann_rects(dx, axes=r_axes, func=dist.pdf):
            bars = VGroup()
            for x in np.arange(0, 1, dx):
                bar = Rectangle()
                line = Line(
                    axes.c2p(x, 0),
                    axes.c2p(x + dx, func(x)),
                )
                bar.replace(line, stretch=True)
                bar.set_stroke(BLUE_E, width=10 * dx, opacity=1)
                bar.set_fill(BLUE, 0.5)
                bars.add(bar)
            return bars

        def get_lebesgue_bars(dy, axes=l_axes, func=dist.pdf, mx=0.7, y_max=dist.pdf(0.7)):
            bars = VGroup()
            for y in np.arange(dy, y_max + dy, dy):
                x0 = binary_search(func, y, 0, mx) or mx
                x1 = binary_search(func, y, mx, 1) or mx
                line = Line(axes.c2p(x0, y - dy), axes.c2p(x1, y))
                bar = Rectangle()
                bar.set_stroke(RED_E, 0)
                bar.set_fill(RED_E, 0.5)
                bar.replace(line, stretch=True)
                bars.add(bar)
            return bars

        r_bar_groups = []
        l_bar_groups = []
        Ns = [10, 20, 40, 80, 160]
        Ms = [2, 4, 8, 16, 32]
        for N, M in zip(Ns, Ms):
            r_bar_groups.append(get_riemann_rects(dx=1 / N))
            l_bar_groups.append(get_lebesgue_bars(dy=1 / M))
        self.play(
            FadeIn(r_bar_groups[0], lag_ratio=0.1),
            FadeIn(l_bar_groups[0], lag_ratio=0.1),
            FadeIn(footnote),
        )
        self.wait()
        for rbg0, rbg1, lbg0, lbg1 in zip(r_bar_groups, r_bar_groups[1:], l_bar_groups, l_bar_groups[1:]):
            self.play(
                ReplacementTransform(
                    rbg0, rbg1,
                    lag_ratio=1 / len(rbg0),
                    run_time=2,
                ),
                ReplacementTransform(
                    lbg0, lbg1,
                    lag_ratio=1 / len(lbg0),
                    run_time=2,
                ),
            )
            self.wait()
        self.play(
            FadeOut(r_bar_groups[-1]),
            FadeOut(l_bar_groups[-1]),
            r_graph.set_fill, BLUE_E, 1,
            l_graph.set_fill, RED_E, 1,
        )


class MeasureTheoryLeadsTo(Scene):
    def construct(self):
        words = TextMobject("Measure Theory")
        words.set_color(RED)
        arrow = Vector(DOWN)
        arrow.next_to(words, DOWN, buff=SMALL_BUFF)
        arrow.set_stroke(width=7)
        arrow.rotate(45 * DEGREES, about_point=arrow.get_start())
        self.play(
            FadeIn(words, DOWN),
            GrowArrow(arrow),
            UpdateFromAlphaFunc(arrow, lambda m, a: m.set_opacity(a)),
        )
        self.wait()


class WhenIWasFirstLearning(TeacherStudentsScene):
    def construct(self):
        self.teacher.change_mode("raise_right_hand")
        self.play(
            self.get_student_changes("pondering", "thinking", "tease"),
            self.teacher.change, "thinking",
        )

        younger = BabyPiCreature(color=GREY_BROWN)
        younger.set_height(2)
        younger.move_to(self.students, DL)

        self.look_at(self.screen)
        self.wait()
        self.play(
            ReplacementTransform(self.teacher, younger),
            LaggedStartMap(
                FadeOutAndShift, self.students,
                lambda m: (m, DOWN),
            )
        )

        # Bubble
        bubble = ThoughtBubble()
        bubble[-1].set_fill(GREEN_SCREEN, 1)
        bubble.move_to(younger.get_corner(UR), DL)

        self.play(
            Write(bubble),
            younger.change, "maybe", bubble.get_bubble_center(),
        )
        self.play(Blink(younger))
        for mode in ["confused", "angry", "pondering", "maybe"]:
            self.play(younger.change, mode)
            for x in range(2):
                self.wait()
                if random.random() < 0.5:
                    self.play(Blink(younger))


class PossibleYetProbabilityZero(Scene):
    def construct(self):
        poss = TextMobject("Possible")
        prob = TextMobject("Probability = 0")
        total = TextMobject("P(dart hits somewhere) = 1")
        # total[1].next_to(total[0][0], RIGHT)
        words = VGroup(poss, prob, total)
        words.scale(1.5)
        words.arrange(DOWN, aligned_edge=LEFT, buff=MED_LARGE_BUFF)

        self.play(Write(poss, run_time=0.5))
        self.wait()
        self.play(FadeIn(prob, UP))
        self.wait()
        self.play(FadeIn(total, UP))
        self.wait()


class TiePossibleToDensity(Scene):
    def construct(self):
        poss = TextMobject("Possibility")
        prob = TextMobject("Probability", " $>$ 0")
        dens = TextMobject("Probability \\emph{density}", " $>$ 0")
        dens[0].set_color(BLUE)
        implies = TexMobject("\\Rightarrow")
        implies2 = implies.copy()

        poss.next_to(implies, LEFT)
        prob.next_to(implies, RIGHT)
        dens.next_to(implies, RIGHT)
        cross = Cross(implies)

        self.camera.frame.scale(0.7, about_point=dens.get_center())

        self.add(poss)
        self.play(
            FadeIn(prob, LEFT),
            Write(implies, run_time=1)
        )
        self.wait()
        self.play(ShowCreation(cross))
        self.wait()

        self.play(
            VGroup(implies, cross, prob).shift, UP,
            FadeIn(implies2),
            FadeIn(dens),
        )
        self.wait()

        self.embed()


class DrawBigRect(Scene):
    def construct(self):
        rect = Rectangle(width=7, height=2.5)
        rect.set_stroke(RED, 5)
        rect.to_edge(RIGHT)

        words = TextMobject("Not how to\\\\think about it")
        words.set_color(RED)
        words.align_to(rect, LEFT)
        words.to_edge(UP)

        arrow = Arrow(
            words.get_bottom(),
            rect.get_top(),
            buff=0.25,
            color=RED,
        )

        self.play(ShowCreation(rect))
        self.play(
            FadeInFromDown(words),
            GrowArrow(arrow),
        )
        self.wait()


class Thumbnail(Scene):
    def construct(self):
        dartboard = Dartboard()
        axes = NumberPlane(
            x_min=-1.25,
            x_max=1.25,
            y_min=-1.25,
            y_max=1.25,
            axis_config={
                "unit_size": 0.5 * dartboard.get_width(),
                "tick_frequency": 0.25,
            },
            x_line_frequency=1.0,
            y_line_frequency=1.0,
        )
        group = VGroup(dartboard, axes)
        group.to_edge(LEFT, buff=0)

        # Arrow
        arrow = Vector(DR, max_stroke_width_to_length_ratio=np.inf)
        arrow.move_to(axes.c2p(PI / 10, np.exp(1) / 10), DR)
        arrow.scale(1.5, about_edge=DR)
        arrow.set_stroke(WHITE, 10)

        black_arrow = arrow.copy()
        black_arrow.set_color(BLACK)
        black_arrow.set_stroke(width=20)

        arrow.points[0] += 0.025 * DR

        # Coords
        coords = TexMobject("(x, y) = (0.31415\\dots, 0.27182\\dots)")
        coords.set_width(5.5)
        coords.set_stroke(BLACK, 10, background=True)
        coords.next_to(axes.get_bottom(), UP, buff=0)

        # Words
        words = VGroup(
            TextMobject("Probability = 0"),
            TextMobject("$\\dots$but still possible"),
        )
        for word in words:
            word.set_width(6)
        words.arrange(DOWN, buff=MED_LARGE_BUFF)
        words.next_to(axes, RIGHT)
        words.to_edge(UP, buff=LARGE_BUFF)

        # Pi
        morty = Mortimer()
        morty.to_corner(DR)
        morty.change("confused", words)

        self.add(group)
        self.add(black_arrow)
        self.add(arrow)
        self.add(coords)
        self.add(words)
        self.add(morty)

        self.embed()


class Part2EndScreen(PatreonEndScreen):
    CONFIG = {
        "scroll_time": 30,
        "specific_patrons": [
            "1stViewMaths",
            "Adam Dřínek",
            "Aidan Shenkman",
            "Alan Stein",
            "Albin Egasse",
            "Alex Mijalis",
            "Alexander Mai",
            "Alexis Olson",
            "Ali Yahya",
            "Andrew Busey",
            "Andrew Cary",
            "Andrew R. Whalley",
            "Anthony Losego",
            "Aravind C V",
            "Arjun Chakroborty",
            "Arthur Zey",
            "Ashwin Siddarth",
            "Augustine Lim",
            "Austin Goodman",
            "Avi Finkel",
            "Awoo",
            "Axel Ericsson",
            "Ayan Doss",
            "AZsorcerer",
            "Barry Fam",
            "Ben Delo",
            "Bernd Sing",
            "Bill Gatliff",
            "Bob Sanderson",
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
            "Chris Druta",
            "Christian Kaiser",
            "cinterloper",
            "Clark Gaebel",
            "Colwyn Fritze-Moor",
            "Cooper Jones",
            "Corey Ogburn",
            "D. Sivakumar",
            "Dan Herbatschek",
            "Daniel Brown",
            "Daniel Herrera C",
            "Darrell Thomas",
            "Dave B",
            "Dave Kester",
            "dave nicponski",
            "David B. Hill",
            "David Clark",
            "David Gow",
            "Delton Ding",
            "Dominik Wagner",
            "Eddie Landesberg",
            "Eduardo Rodriguez",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Fernando Via Canel",
            "Frank R. Brown, Jr.",
            "Gavin",
            "Giovanni Filippi",
            "Goodwine",
            "Hal Hildebrand",
            "Hitoshi Yamauchi",
            "Ivan Sorokin",
            "Jacob Baxter",
            "Jacob Harmon",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jalex Stark",
            "Jameel Syed",
            "James Beall",
            "Jason Hise",
            "Jayne Gabriele",
            "Jean-Manuel Izaret",
            "Jeff Dodds",
            "Jeff Linse",
            "Jeff Straathof",
            "Jimmy Yang",
            "John C. Vesey",
            "John Camp",
            "John Haley",
            "John Le",
            "John Luttig",
            "John Rizzo",
            "John V Wertheim",
            "Jonathan Heckerman",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Joseph Kelly",
            "Josh Kinnear",
            "Joshua Claeys",
            "Joshua Ouellette",
            "Juan Benet",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Karl Niu",
            "Kartik Cating-Subramanian",
            "Kaustuv DeBiswas",
            "Killian McGuinness",
            "Klaas Moerman",
            "Kros Dai",
            "L0j1k",
            "Lael S Costa",
            "LAI Oscar",
            "Lambda GPU Workstations",
            "Laura Gast",
            "Lee Redden",
            "Linh Tran",
            "Luc Ritchie",
            "Ludwig Schubert",
            "Lukas Biewald",
            "Lukas Zenick",
            "Magister Mugit",
            "Magnus Dahlström",
            "Magnus Hiie",
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
            "Maxim Nitsche",
            "Michael Bos",
            "Michael Day",
            "Michael Hardel",
            "Michael W White",
            "Mihran Vardanyan",
            "Mirik Gogri",
            "Molly Mackinlay",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nate Heckmann",
            "Nicholas Cahill",
            "Nikita Lesnikov",
            "Oleg Leonov",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Patrick Lucas",
            "Pavel Dubov",
            "Pesho Ivanov",
            "Petar Veličković",
            "Peter Ehrnstrom",
            "Peter Francis",
            "Peter Mcinerney",
            "Pierre Lancien",
            "Pradeep Gollakota",
            "Rafael Bove Barrios",
            "Randy C. Will",
            "rehmi post",
            "Rex Godby",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roman Sergeychik",
            "Roobie",
            "Ryan Atallah",
            "Ryan Prayogo",
            "Samuel Judge",
            "SansWord Huang",
            "Scott Gray",
            "Scott Walter, Ph.D.",
            "soekul",
            "Solara570",
            "Steve Huynh",
            "Steve Muench",
            "Steve Sperandeo",
            "Steven Siddals",
            "Stevie Metke",
            "Sunil Nagaraj",
            "supershabam",
            "Susanne Fenja Mehr-Koks",
            "Suteerth Vishnu",
            "Suthen Thomas",
            "Tal Einav",
            "Taras Bobrovytsky",
            "Tauba Auerbach",
            "Ted Suzman",
            "THIS IS THE point OF NO RE tUUurRrhghgGHhhnnn",
            "Thomas J Sargent",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tihan Seale",
            "Tyler Herrmann",
            "Tyler McAtee",
            "Tyler VanValkenburg",
            "Tyler Veness",
            "Vassili Philippov",
            "Vasu Dubey",
            "Veritasium",
            "Vignesh Ganapathi Subramanian",
            "Vinicius Reis",
            "Vladimir Solomatin",
            "Wooyong Ee",
            "Xuanji Li",
            "Yana Chernobilsky",
            "YinYangBalance.Asia",
            "Yorick Lesecque",
            "Yu Jun",
            "Yurii Monastyrshyn",
        ],
    }
