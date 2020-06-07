from manimlib.imports import *
from from_3b1b.active.bayes.beta_helpers import *
from from_3b1b.active.bayes.beta1 import *
from from_3b1b.active.bayes.beta2 import ShowLimitToPdf

import scipy.stats

OUTPUT_DIRECTORY = "bayes/beta3"


class RemindOfWeightedCoin(Scene):
    def construct(self):
        # Largely copied from beta2

        # Prob label
        p_label = get_prob_coin_label()
        p_label.set_height(0.7)
        p_label.to_edge(UP)

        rhs = p_label[-1]
        q_box = get_q_box(rhs)
        p_label.add(q_box)

        self.add(p_label)

        # Coin grid
        def get_random_coin_grid(p):
            bools = np.random.random(100) < p
            grid = get_coin_grid(bools)
            return grid

        grid = get_random_coin_grid(0.5)
        grid.next_to(p_label, DOWN, MED_LARGE_BUFF)

        self.play(LaggedStartMap(
            FadeIn, grid,
            lag_ratio=2 / len(grid),
            run_time=3,
        ))
        self.wait()

        # Label as h
        brace = Brace(q_box, DOWN, buff=SMALL_BUFF)
        h_label = TexMobject("h")
        h_label.next_to(brace, DOWN)
        eq = TexMobject("=")
        eq.next_to(h_label, RIGHT)
        h_decimal = DecimalNumber(0.5)
        h_decimal.next_to(eq, RIGHT)

        self.play(
            GrowFromCenter(brace),
            FadeIn(h_label, UP),
            grid.scale, 0.8, {"about_edge": DOWN},
        )
        self.wait()

        # Alternate weightings
        tail_grid = get_random_coin_grid(0)
        head_grid = get_random_coin_grid(1)
        grid70 = get_random_coin_grid(0.7)
        alt_grids = [tail_grid, head_grid, grid70]
        for ag in alt_grids:
            ag.replace(grid)

        for coins in [grid, *alt_grids]:
            for coin in coins:
                coin.generate_target()
                coin.target.rotate(90 * DEGREES, axis=UP)
                coin.target.set_opacity(0)

        def get_grid_swap_anims(g1, g2):
            return [
                LaggedStartMap(MoveToTarget, g1, lag_ratio=0.02, run_time=1.5, remover=True),
                LaggedStartMap(MoveToTarget, g2, lag_ratio=0.02, run_time=1.5, rate_func=reverse_smooth),
            ]

        self.play(
            FadeIn(eq),
            UpdateFromAlphaFunc(h_decimal, lambda m, a: m.set_opacity(a)),
            ChangeDecimalToValue(h_decimal, 0, run_time=2),
            *get_grid_swap_anims(grid, tail_grid)
        )
        self.wait()
        self.play(
            ChangeDecimalToValue(h_decimal, 1, run_time=1.5),
            *get_grid_swap_anims(tail_grid, head_grid)
        )
        self.wait()
        self.play(
            ChangeDecimalToValue(h_decimal, 0.7, run_time=1.5),
            *get_grid_swap_anims(head_grid, grid70)
        )
        self.wait()

        # Graph
        axes = scaled_pdf_axes()
        axes.to_edge(DOWN, buff=MED_SMALL_BUFF)
        axes.y_axis.numbers.set_opacity(0)
        axes.y_axis_label.set_opacity(0)

        h_lines = VGroup()
        for y in range(15):
            h_line = Line(axes.c2p(0, y), axes.c2p(1, y))
            h_lines.add(h_line)
        h_lines.set_stroke(WHITE, 0.5, opacity=0.5)
        axes.add(h_lines)

        x_axis_label = p_label[:4].copy()
        x_axis_label.set_height(0.4)
        x_axis_label.next_to(axes.c2p(1, 0), UR, buff=SMALL_BUFF)
        axes.x_axis.add(x_axis_label)

        n_heads_tracker = ValueTracker(3)
        n_tails_tracker = ValueTracker(3)

        def get_graph(axes=axes, nht=n_heads_tracker, ntt=n_tails_tracker):
            dist = scipy.stats.beta(nht.get_value() + 1, ntt.get_value() + 1)
            graph = axes.get_graph(dist.pdf, step_size=0.05)
            graph.set_stroke(BLUE, 3)
            graph.set_fill(BLUE_E, 1)
            return graph

        graph = always_redraw(get_graph)

        area_label = TextMobject("Area = 1")
        area_label.set_height(0.5)
        area_label.move_to(axes.c2p(0.5, 1))

        # pdf label
        pdf_label = TextMobject("probability ", "density ", "function")
        pdf_label.next_to(axes.input_to_graph_point(0.5, graph), UP)
        pdf_target_template = TextMobject("p", "d", "f")
        pdf_target_template.next_to(axes.input_to_graph_point(0.7, graph), UR)
        pdf_label.generate_target()
        for part, letter2 in zip(pdf_label.target, pdf_target_template):
            for letter1 in part:
                letter1.move_to(letter2)
            part[1:].set_opacity(0)

        # Add plot
        self.add(axes, *self.mobjects)
        self.play(
            FadeOut(eq),
            FadeOut(h_decimal),
            LaggedStartMap(MoveToTarget, grid70, run_time=1, remover=True),
            FadeIn(axes),
        )
        self.play(
            DrawBorderThenFill(graph),
            FadeIn(area_label, rate_func=squish_rate_func(smooth, 0.5, 1), run_time=2),
            Write(pdf_label, run_time=1),
        )
        self.wait()

        # Region
        lh_tracker = ValueTracker(0.7)
        rh_tracker = ValueTracker(0.7)

        def get_region(axes=axes, graph=graph, lh_tracker=lh_tracker, rh_tracker=rh_tracker):
            lh = lh_tracker.get_value()
            rh = rh_tracker.get_value()
            region = get_region_under_curve(axes, graph, lh, rh)
            region.set_fill(GREY, 0.85)
            region.set_stroke(YELLOW, 1)
            return region

        region = always_redraw(get_region)

        region_area_label = DecimalNumber(num_decimal_places=3)
        region_area_label.next_to(axes.c2p(0.7, 0), UP, MED_LARGE_BUFF)

        def update_ra_label(label, nht=n_heads_tracker, ntt=n_tails_tracker, lht=lh_tracker, rht=rh_tracker):
            dist = scipy.stats.beta(nht.get_value() + 1, ntt.get_value() + 1)
            area = dist.cdf(rht.get_value()) - dist.cdf(lht.get_value())
            label.set_value(area)

        region_area_label.add_updater(update_ra_label)

        range_label = VGroup(
            TexMobject("0.6 \\le"),
            p_label[:4].copy(),
            TexMobject("\\le 0.8"),
        )
        for mob in range_label:
            mob.set_height(0.4)
        range_label.arrange(RIGHT, buff=SMALL_BUFF)
        pp_label = VGroup(
            TexMobject("P("),
            range_label,
            TexMobject(")"),
        )
        for mob in pp_label[::2]:
            mob.set_height(0.7)
            mob.set_color(YELLOW)
        pp_label.arrange(RIGHT, buff=SMALL_BUFF)
        pp_label.move_to(axes.c2p(0.3, 3))

        self.play(
            FadeIn(pp_label[::2]),
            MoveToTarget(pdf_label),
            FadeOut(area_label),
        )
        self.wait()
        self.play(TransformFromCopy(p_label[:4], range_label[1]))
        self.wait()
        self.play(TransformFromCopy(axes.x_axis.numbers[2], range_label[0]))
        self.play(TransformFromCopy(axes.x_axis.numbers[3], range_label[2]))
        self.wait()

        self.add(region)
        self.play(
            lh_tracker.set_value, 0.6,
            rh_tracker.set_value, 0.8,
            UpdateFromAlphaFunc(
                region_area_label,
                lambda m, a: m.set_opacity(a),
                rate_func=squish_rate_func(smooth, 0.25, 1)
            ),
            run_time=3,
        )
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
        coins.next_to(h_label, DOWN, buff=MED_LARGE_BUFF)

        heads = [c for c in coins if c.symbol == "H"]
        numbers = VGroup(*[
            Integer(i + 1).set_height(0.2).next_to(coin, DOWN, SMALL_BUFF)
            for i, coin in enumerate(heads)
        ])

        for coin in coins:
            coin.save_state()
            coin.rotate(90 * DEGREES, UP)
            coin.set_opacity(0)

        pp_label.generate_target()
        pp_label.target.set_height(0.5)
        pp_label.target.next_to(axes.c2p(0, 2), RIGHT, MED_LARGE_BUFF)

        self.play(
            LaggedStartMap(Restore, coins),
            MoveToTarget(pp_label),
            run_time=1,
        )
        self.play(ShowIncreasingSubsets(numbers))
        self.wait()

        # Move plot
        self.play(
            n_heads_tracker.set_value, 7,
            n_tails_tracker.set_value, 3,
            FadeOut(pdf_label, rate_func=squish_rate_func(smooth, 0, 0.5)),
            run_time=2
        )
        self.wait()

        # How does the answer change with more data
        new_bools = [True] * 63 + [False] * 27
        random.shuffle(new_bools)
        bools = [c.symbol == "H" for c in coins] + new_bools
        grid = get_coin_grid(bools)
        grid.set_height(3.5)
        grid.next_to(axes.c2p(0, 3), RIGHT, MED_LARGE_BUFF)

        self.play(
            FadeOut(numbers),
            ReplacementTransform(coins, grid[:10]),
        )
        self.play(
            FadeIn(grid[10:], lag_ratio=0.1, rate_func=linear),
            pp_label.next_to, grid, DOWN,
        )
        self.wait()
        self.add(graph, region, region_area_label, p_label, q_box, brace, h_label)
        self.play(
            n_heads_tracker.set_value, 70,
            n_tails_tracker.set_value, 30,
        )
        self.wait()
        origin = axes.c2p(0, 0)
        self.play(
            axes.y_axis.stretch, 0.5, 1, {"about_point": origin},
            h_lines.stretch, 0.5, 1, {"about_point": origin},
        )
        self.wait()

        # Shift the shape around
        pairs = [
            (70 * 3, 30 * 3),
            (35, 15),
            (35 + 20, 15 + 20),
            (7, 3),
            (70, 30),
        ]
        for nh, nt in pairs:
            self.play(
                n_heads_tracker.set_value, nh,
                n_tails_tracker.set_value, nt,
                run_time=2,
            )
            self.wait()

        # End
        self.embed()


class LastTimeWrapper(Scene):
    def construct(self):
        fs_rect = FullScreenFadeRectangle(fill_opacity=1, fill_color=GREY_E)
        self.add(fs_rect)

        title = TextMobject("Last Time")
        title.scale(1.5)
        title.to_edge(UP)

        rect = ScreenRectangle()
        rect.set_height(6)
        rect.set_fill(BLACK, 1)
        rect.next_to(title, DOWN)

        self.play(
            DrawBorderThenFill(rect),
            FadeInFromDown(title),
        )
        self.wait()


class ComplainAboutSimplisticModel(ExternallyAnimatedScene):
    pass


class BayesianFrequentistDivide(Scene):
    def construct(self):
        # Setup Bayesian vs. Frequentist divide
        b_label = TextMobject("Bayesian")
        f_label = TextMobject("Frequentist")
        labels = VGroup(b_label, f_label)
        for label, vect in zip(labels, [LEFT, RIGHT]):
            label.set_height(0.7)
            label.move_to(vect * FRAME_WIDTH / 4)
            label.to_edge(UP, buff=0.35)

        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_WIDTH)
        h_line.next_to(labels, DOWN)
        v_line = Line(UP, DOWN)
        v_line.set_height(FRAME_HEIGHT)
        v_line.center()

        for label in labels:
            label.save_state()
            label.set_y(0)
            self.play(
                FadeIn(label, -normalize(label.get_center())),
            )
        self.wait()
        self.play(
            ShowCreation(VGroup(v_line, h_line)),
            *map(Restore, labels),
        )
        self.wait()

        # Overlay ShowBayesianUpdating in editing
        # Frequentist list (ignore?)
        kw = {
            "tex_to_color_map": {
                "$p$-value": YELLOW,
                "$H_0$": PINK,
                "$\\alpha$": BLUE,
            },
            "alignment": "",
        }
        freq_list = VGroup(
            TextMobject("1. State a null hypothesis $H_0$", **kw),
            TextMobject("2. Choose a test statistic,\\\\", "$\\qquad$ compute its value", **kw),
            TextMobject("3. Calculate a $p$-value", **kw),
            TextMobject("4. Choose a significance value $\\alpha$", **kw),
            TextMobject("5. Reject $H_0$ if $p$-value\\\\", "$\\qquad$ is less than $\\alpha$", **kw),
        )

        freq_list.set_width(0.5 * FRAME_WIDTH - 1)
        freq_list.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        freq_list.move_to(FRAME_WIDTH * RIGHT / 4)
        freq_list.to_edge(DOWN, buff=LARGE_BUFF)

        # Frequentist icon
        axes = get_beta_dist_axes(y_max=5, y_unit=1)
        axes.set_width(0.5 * FRAME_WIDTH - 1)
        axes.move_to(FRAME_WIDTH * RIGHT / 4 + DOWN)

        dist = scipy.stats.norm(0.5, 0.1)
        graph = axes.get_graph(dist.pdf)
        graphs = VGroup()
        for x_min, x_max in [(0, 0.3), (0.3, 0.7), (0.7, 1.0)]:
            graph = axes.get_graph(dist.pdf, x_min=x_min, x_max=x_max)
            graph.add_line_to(axes.c2p(x_max, 0))
            graph.add_line_to(axes.c2p(x_min, 0))
            graph.add_line_to(graph.get_start())
            graphs.add(graph)

        graphs.set_stroke(width=0)
        graphs.set_fill(RED, 1)
        graphs[1].set_fill(GREY_D, 1)

        H_words = VGroup(*[TextMobject("Reject\\\\$H_0$") for x in range(2)])
        for H_word, graph, vect in zip(H_words, graphs[::2], [RIGHT, LEFT]):
            H_word.next_to(graph, UP, MED_LARGE_BUFF)
            arrow = Arrow(
                H_word.get_bottom(),
                graph.get_center() + 0.75 * vect,
                buff=SMALL_BUFF
            )
            H_word.add(arrow)

        H_words.set_color(RED)
        self.add(H_words)

        self.add(axes)
        self.add(graphs)

        self.embed()

        # Transition to 2x2
        # Go back to prior
        # Label uniform prior
        # Talk about real coin prior
        # Update ad infinitum


class ArgumentBetweenBayesianAndFrequentist(Scene):
    def construct(self):
        pass


# From version 1
class ShowBayesianUpdating(Scene):
    CONFIG = {
        "true_p": 0.72,
        "random_seed": 4,
        "initial_axis_scale_factor": 3.5
    }

    def construct(self):
        # Axes
        axes = scaled_pdf_axes(self.initial_axis_scale_factor)
        self.add(axes)

        # Graph
        n_heads = 0
        n_tails = 0
        graph = get_beta_graph(axes, n_heads, n_tails)
        self.add(graph)

        # Get coins
        true_p = self.true_p
        bool_values = np.random.random(100) < true_p
        bool_values[1] = True
        coins = self.get_coins(bool_values)
        coins.next_to(axes.y_axis, RIGHT, MED_LARGE_BUFF)
        coins.to_edge(UP, LARGE_BUFF)

        # Probability label
        p_label, prob, prob_box = self.get_probability_label()
        self.add(p_label)
        self.add(prob_box)

        # Slow animations
        def head_likelihood(x):
            return x

        def tail_likelihood(x):
            return 1 - x

        n_previews = 10
        n_slow_previews = 5
        for x in range(n_previews):
            coin = coins[x]
            is_heads = bool_values[x]

            new_data_label = TextMobject("New data")
            new_data_label.set_height(0.3)
            arrow = Vector(0.5 * UP)
            arrow.next_to(coin, DOWN, SMALL_BUFF)
            new_data_label.next_to(arrow, DOWN, SMALL_BUFF)
            new_data_label.shift(MED_SMALL_BUFF * RIGHT)

            if is_heads:
                line = axes.get_graph(lambda x: x)
                label = TexMobject("\\text{Scale by } x")
                likelihood = head_likelihood
                n_heads += 1
            else:
                line = axes.get_graph(lambda x: 1 - x)
                label = TexMobject("\\text{Scale by } (1 - x)")
                likelihood = tail_likelihood
                n_tails += 1
            label.next_to(graph, UP)
            label.set_stroke(BLACK, 3, background=True)
            line.set_stroke(YELLOW, 3)

            graph_copy = graph.copy()
            graph_copy.unlock_triangulation()
            scaled_graph = graph.copy()
            scaled_graph.apply_function(
                lambda p: axes.c2p(
                    axes.x_axis.p2n(p),
                    axes.y_axis.p2n(p) * likelihood(axes.x_axis.p2n(p))
                )
            )
            scaled_graph.set_color(GREEN)

            renorm_label = TextMobject("Renormalize")
            renorm_label.move_to(label)

            new_graph = get_beta_graph(axes, n_heads, n_tails)

            renormalized_graph = scaled_graph.copy()
            renormalized_graph.match_style(graph)
            renormalized_graph.match_height(new_graph, stretch=True, about_edge=DOWN)

            if x < n_slow_previews:
                self.play(
                    FadeInFromDown(coin),
                    FadeIn(new_data_label),
                    GrowArrow(arrow),
                )
                self.play(
                    FadeOut(new_data_label),
                    FadeOut(arrow),
                    ShowCreation(line),
                    FadeIn(label),
                )
                self.add(graph_copy, line, label)
                self.play(Transform(graph_copy, scaled_graph))
                self.play(
                    FadeOut(line),
                    FadeOut(label),
                    FadeIn(renorm_label),
                )
                self.play(
                    Transform(graph_copy, renormalized_graph),
                    FadeOut(graph),
                )
                self.play(FadeOut(renorm_label))
            else:
                self.add(coin)
                graph_copy.become(scaled_graph)
                self.add(graph_copy)
                self.play(
                    Transform(graph_copy, renormalized_graph),
                    FadeOut(graph),
                )
            graph = new_graph
            self.remove(graph_copy)
            self.add(new_graph)

        # Rescale y axis
        axes.save_state()
        sf = self.initial_axis_scale_factor
        axes.y_axis.stretch(1 / sf, 1, about_point=axes.c2p(0, 0))
        for number in axes.y_axis.numbers:
            number.stretch(sf, 1)
        axes.y_axis.numbers[:4].set_opacity(0)

        self.play(
            Restore(axes, rate_func=lambda t: smooth(1 - t)),
            graph.stretch, 1 / sf, 1, {"about_edge": DOWN},
            run_time=2,
        )

        # Fast animations
        for x in range(n_previews, len(coins)):
            coin = coins[x]
            is_heads = bool_values[x]

            if is_heads:
                n_heads += 1
            else:
                n_tails += 1
            new_graph = get_beta_graph(axes, n_heads, n_tails)

            self.add(coins[:x + 1])
            self.add(new_graph)
            self.remove(graph)
            self.wait(0.25)
            # self.play(
            #     FadeIn(new_graph),
            #     run_time=0.25,
            # )
            # self.play(
            #     FadeOut(graph),
            #     run_time=0.25,
            # )
            graph = new_graph

        # Show confidence interval
        dist = scipy.stats.beta(n_heads + 1, n_tails + 1)
        v_lines = VGroup()
        labels = VGroup()
        x_bounds = dist.interval(0.95)
        for x in x_bounds:
            line = DashedLine(
                axes.c2p(x, 0),
                axes.c2p(x, 12),
            )
            line.set_color(YELLOW)
            v_lines.add(line)
            label = DecimalNumber(x)
            label.set_height(0.25)
            label.next_to(line, UP)
            label.match_color(line)
            labels.add(label)

        true_graph = axes.get_graph(dist.pdf)
        region = get_region_under_curve(axes, true_graph, *x_bounds)
        region.set_fill(GREY_BROWN, 0.85)
        region.set_stroke(YELLOW, 1)

        label95 = TexMobject("95\\%")
        fix_percent(label95.family_members_with_points()[-1])
        label95.move_to(region, DOWN)
        label95.shift(0.5 * UP)

        self.play(*map(ShowCreation, v_lines))
        self.play(
            FadeIn(region),
            Write(label95)
        )
        self.wait()
        for label in labels:
            self.play(FadeInFromDown(label))
        self.wait()

        # Show true value
        self.wait()
        self.play(FadeOut(prob_box))
        self.play(ShowCreationThenFadeAround(prob))
        self.wait()

        # Much more data
        many_bools = np.hstack([
            bool_values,
            (np.random.random(1000) < true_p)
        ])
        N_tracker = ValueTracker(100)
        graph.N_tracker = N_tracker
        graph.bools = many_bools
        graph.axes = axes
        graph.v_lines = v_lines
        graph.labels = labels
        graph.region = region
        graph.label95 = label95

        label95.width_ratio = label95.get_width() / region.get_width()

        def update_graph(graph):
            N = int(graph.N_tracker.get_value())
            nh = sum(graph.bools[:N])
            nt = len(graph.bools[:N]) - nh
            new_graph = get_beta_graph(graph.axes, nh, nt, step_size=0.05)
            graph.become(new_graph)

            dist = scipy.stats.beta(nh + 1, nt + 1)
            x_bounds = dist.interval(0.95)
            for x, line, label in zip(x_bounds, graph.v_lines, graph.labels):
                line.set_x(graph.axes.c2p(x, 0)[0])
                label.set_x(graph.axes.c2p(x, 0)[0])
                label.set_value(x)

            graph.labels[0].shift(MED_SMALL_BUFF * LEFT)
            graph.labels[1].shift(MED_SMALL_BUFF * RIGHT)

            new_simple_graph = graph.axes.get_graph(dist.pdf)
            new_region = get_region_under_curve(graph.axes, new_simple_graph, *x_bounds)
            new_region.match_style(graph.region)
            graph.region.become(new_region)

            graph.label95.set_width(graph.label95.width_ratio * graph.region.get_width())
            graph.label95.match_x(graph.region)

        self.add(graph, region, label95, p_label)
        self.play(
            N_tracker.set_value, 1000,
            UpdateFromFunc(graph, update_graph),
            Animation(v_lines),
            Animation(labels),
            Animation(graph.region),
            Animation(graph.label95),
            run_time=5,
        )
        self.wait()

    #

    def get_coins(self, bool_values):
        coins = VGroup(*[
            get_coin("H" if heads else "T")
            for heads in bool_values
        ])
        coins.arrange_in_grid(n_rows=10, buff=MED_LARGE_BUFF)
        coins.set_height(5)
        return coins

    def get_probability_label(self):
        head = get_coin("H")
        p_label = TexMobject(
            "P(00) = ",
            tex_to_color_map={"00": WHITE}
        )
        template = p_label.get_part_by_tex("00")
        head.replace(template)
        p_label.replace_submobject(
            p_label.index_of_part(template),
            head,
        )
        prob = DecimalNumber(self.true_p)
        prob.next_to(p_label, RIGHT)
        p_label.add(prob)
        p_label.set_height(0.75)
        p_label.to_corner(UR)

        prob_box = SurroundingRectangle(prob, buff=SMALL_BUFF)
        prob_box.set_fill(GREY_D, 1)
        prob_box.set_stroke(WHITE, 2)

        q_marks = TexMobject("???")
        q_marks.move_to(prob_box)
        prob_box.add(q_marks)

        return p_label, prob, prob_box


class HighlightReviewPartsReversed(HighlightReviewParts):
    CONFIG = {
        "reverse_order": True,
    }


class Grey(Scene):
    def construct(self):
        self.add(FullScreenFadeRectangle(fill_color=GREY_D, fill_opacity=1))


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
            FadeOut(prior_name[1], RIGHT),
            FadeIn(uniform_name, LEFT)
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
            FadeIn(post_word, 0.25 * UP)
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


class BayesRuleWithPdf(ShowLimitToPdf):
    def construct(self):
        # Axes
        axes = self.get_axes()
        sf = 1.5
        axes.y_axis.stretch(sf, 1, about_point=axes.c2p(0, 0))
        for number in axes.y_axis.numbers:
            number.stretch(1 / sf, 1)
        self.add(axes)

        # Formula
        bayes = self.get_formula()

        post = bayes[:5]
        eq = bayes[5]
        prior = bayes[6:9]
        likelihood = bayes[9:14]
        over = bayes[14]
        p_data = bayes[15:]

        self.play(FadeInFromDown(bayes))
        self.wait()

        # Prior
        prior_graph = get_beta_graph(axes, 0, 0)
        prior_graph_top = Line(
            prior_graph.get_corner(UL),
            prior_graph.get_corner(UR),
        )
        prior_graph_top.set_stroke(YELLOW, 3)

        bayes.save_state()
        bayes.set_opacity(0.2)
        prior.set_opacity(1)

        self.play(
            Restore(bayes, rate_func=reverse_smooth),
            FadeIn(prior_graph),
            ShowCreation(prior_graph_top),
        )
        self.play(FadeOut(prior_graph_top))
        self.wait()

        # Scale Down
        nh = 1
        nt = 2

        scaled_graph = axes.get_graph(
            lambda x: scipy.stats.binom(3, x).pmf(1) + 1e-6
        )
        scaled_graph.set_stroke(GREEN)
        scaled_region = get_region_under_curve(axes, scaled_graph, 0, 1)

        def to_uniform(p, axes=axes):
            return axes.c2p(
                axes.x_axis.p2n(p),
                int(axes.y_axis.p2n(p) != 0),
            )

        scaled_region.set_fill(opacity=0.75)
        scaled_region.save_state()
        scaled_region.apply_function(to_uniform)

        self.play(
            Restore(scaled_region),
            UpdateFromAlphaFunc(
                scaled_region,
                lambda m, a: m.set_opacity(a * 0.75),
            ),
            likelihood.set_opacity, 1,
        )
        self.wait()

        # Rescale
        new_graph = get_beta_graph(axes, nh, nt)
        self.play(
            ApplyMethod(
                scaled_region.set_height, new_graph.get_height(),
                {"about_edge": DOWN, "stretch": True},
                run_time=2,
            ),
            over.set_opacity, 1,
            p_data.set_opacity, 1,
        )
        self.wait()
        self.play(
            post.set_opacity, 1,
            eq.set_opacity, 1,
        )
        self.wait()

        # Use lower case
        new_bayes = self.get_formula(lowercase=True)
        new_bayes.replace(bayes, dim_to_match=0)
        rects = VGroup(
            SurroundingRectangle(new_bayes[0][0]),
            SurroundingRectangle(new_bayes[6][0]),
        )
        rects.set_stroke(YELLOW, 3)

        self.remove(bayes)
        bayes = self.get_formula()
        bayes.unlock_triangulation()
        self.add(bayes)
        self.play(Transform(bayes, new_bayes))
        self.play(ShowCreationThenFadeOut(rects))

    def get_formula(self, lowercase=False):
        p_sym = "p" if lowercase else "P"
        bayes = TexMobject(
            p_sym + "({s} \\,|\\, \\text{data})", "=",
            "{" + p_sym + "({s})",
            "P(\\text{data} \\,|\\, {s})",
            "\\over",
            "P(\\text{data})",
            tex_to_color_map={
                "{s}": YELLOW,
                "\\text{data}": GREEN,
            }
        )
        bayes.set_height(1.5)
        bayes.to_edge(UP)
        return bayes


class TalkThroughCoinExample(ShowBayesianUpdating):
    def construct(self):
        # Setup
        axes = self.get_axes()
        x_label = TexMobject("x")
        x_label.next_to(axes.x_axis.get_end(), UR, MED_SMALL_BUFF)
        axes.add(x_label)

        p_label, prob, prob_box = self.get_probability_label()
        prob_box_x = x_label.copy().move_to(prob_box)

        self.add(axes)
        self.add(p_label)
        self.add(prob_box)

        self.wait()
        q_marks = prob_box[1]
        prob_box.remove(q_marks)
        self.play(
            FadeOut(q_marks),
            TransformFromCopy(x_label, prob_box_x)
        )
        prob_box.add(prob_box_x)

        # Setup coins
        bool_values = (np.random.random(100) < self.true_p)
        bool_values[:5] = [True, False, True, True, False]
        coins = self.get_coins(bool_values)
        coins.next_to(axes.y_axis, RIGHT, MED_LARGE_BUFF)
        coins.to_edge(UP)

        # Random coin
        rows = VGroup()
        for x in range(5):
            row = self.get_coins(np.random.random(10) < self.true_p)
            row.arrange(RIGHT, buff=MED_LARGE_BUFF)
            row.set_width(6)
            row.move_to(UP)
            rows.add(row)

        last_row = VMobject()
        for row in rows:
            self.play(
                FadeOut(last_row, DOWN),
                FadeIn(row, lag_ratio=0.1)
            )
            last_row = row
        self.play(FadeOut(last_row, DOWN))

        # Uniform pdf
        region = get_beta_graph(axes, 0, 0)
        graph = Line(
            region.get_corner(UL),
            region.get_corner(UR),
        )
        func_label = TexMobject("f(x) =", "1")
        func_label.next_to(graph, UP)

        self.play(
            FadeIn(func_label, lag_ratio=0.1),
            ShowCreation(graph),
        )
        self.add(region, graph)
        self.play(FadeIn(region))
        self.wait()

        # First flip
        coin = coins[0]
        arrow = Vector(0.5 * UP)
        arrow.next_to(coin, DOWN, SMALL_BUFF)
        data_label = TextMobject("New data")
        data_label.set_height(0.25)
        data_label.next_to(arrow, DOWN)
        data_label.shift(0.5 * RIGHT)

        self.play(
            FadeIn(coin, DOWN),
            GrowArrow(arrow),
            Write(data_label, run_time=1)
        )
        self.wait()

        # Show Bayes rule
        bayes = TexMobject(
            "p({x} | \\text{data})", "=",
            "p({x})",
            "{P(\\text{data} | {x})",
            "\\over",
            "P(\\text{data})",
            tex_to_color_map={
                "{x}": WHITE,
                "\\text{data}": GREEN,
            }
        )
        bayes.next_to(func_label, UP, LARGE_BUFF, LEFT)

        likelihood = bayes[9:14]
        p_data = bayes[15:]
        likelihood_rect = SurroundingRectangle(likelihood, buff=0.05)
        likelihood_rect.save_state()
        p_data_rect = SurroundingRectangle(p_data, buff=0.05)

        likelihood_x_label = TexMobject("x")
        likelihood_x_label.next_to(likelihood_rect, UP)

        self.play(FadeInFromDown(bayes))
        self.wait()
        self.play(ShowCreation(likelihood_rect))
        self.wait()

        self.play(TransformFromCopy(likelihood[-2], likelihood_x_label))
        self.wait()

        # Scale by x
        times_x = TexMobject("\\cdot \\, x")
        times_x.next_to(func_label, RIGHT, buff=0.2)

        new_graph = axes.get_graph(lambda x: x)
        sub_region = get_region_under_curve(axes, new_graph, 0, 1)

        self.play(
            Write(times_x),
            Transform(graph, new_graph),
        )
        self.play(
            region.set_opacity, 0.5,
            FadeIn(sub_region),
        )
        self.wait()

        # Show example scalings
        low_x = 0.1
        high_x = 0.9
        lines = VGroup()
        for x in [low_x, high_x]:
            lines.add(Line(axes.c2p(x, 0), axes.c2p(x, 1)))

        lines.set_stroke(YELLOW, 3)

        for x, line in zip([low_x, high_x], lines):
            self.play(FadeIn(line))
            self.play(line.scale, x, {"about_edge": DOWN})
        self.wait()
        self.play(FadeOut(lines))

        # Renormalize
        self.play(
            FadeOut(likelihood_x_label),
            ReplacementTransform(likelihood_rect, p_data_rect),
        )
        self.wait()

        one = func_label[1]
        two = TexMobject("2")
        two.move_to(one, LEFT)

        self.play(
            FadeOut(region),
            sub_region.stretch, 2, 1, {"about_edge": DOWN},
            sub_region.set_color, BLUE,
            graph.stretch, 2, 1, {"about_edge": DOWN},
            FadeInFromDown(two),
            FadeOut(one, UP),
        )
        region = sub_region
        func_label = VGroup(func_label[0], two, times_x)
        self.add(func_label)

        self.play(func_label.shift, 0.5 * UP)
        self.wait()

        const = TexMobject("C")
        const.scale(0.9)
        const.move_to(two, DR)
        const.shift(0.07 * RIGHT)
        self.play(
            FadeOut(two, UP),
            FadeIn(const, DOWN)
        )
        self.remove(func_label)
        func_label = VGroup(func_label[0], const, times_x)
        self.add(func_label)
        self.play(FadeOut(p_data_rect))
        self.wait()

        # Show tails
        coin = coins[1]
        self.play(
            arrow.next_to, coin, DOWN, SMALL_BUFF,
            MaintainPositionRelativeTo(data_label, arrow),
            FadeInFromDown(coin),
        )
        self.wait()

        to_prior_arrow = Arrow(
            func_label[0][3],
            bayes[6],
            max_tip_length_to_length_ratio=0.15,
            stroke_width=3,
        )
        to_prior_arrow.set_color(RED)

        self.play(Indicate(func_label, scale_factor=1.2, color=RED))
        self.play(ShowCreation(to_prior_arrow))
        self.wait()
        self.play(FadeOut(to_prior_arrow))

        # Scale by (1 - x)
        eq_1mx = TexMobject("(1 - x)")
        dot = TexMobject("\\cdot")
        rhs_part = VGroup(dot, eq_1mx)
        rhs_part.arrange(RIGHT, buff=0.2)
        rhs_part.move_to(func_label, RIGHT)

        l_1mx = eq_1mx.copy()
        likelihood_rect.restore()
        l_1mx.next_to(likelihood_rect, UP, SMALL_BUFF)

        self.play(
            ShowCreation(likelihood_rect),
            FadeIn(l_1mx, 0.5 * DOWN),
        )
        self.wait()
        self.play(ShowCreationThenFadeOut(Underline(p_label)))
        self.play(Indicate(coins[1]))
        self.wait()
        self.play(
            TransformFromCopy(l_1mx, eq_1mx),
            FadeIn(dot, RIGHT),
            func_label.next_to, dot, LEFT, 0.2,
        )

        scaled_graph = axes.get_graph(lambda x: 2 * x * (1 - x))
        scaled_region = get_region_under_curve(axes, scaled_graph, 0, 1)

        self.play(Transform(graph, scaled_graph))
        self.play(FadeIn(scaled_region))
        self.wait()

        # Renormalize
        self.remove(likelihood_rect)
        self.play(
            TransformFromCopy(likelihood_rect, p_data_rect),
            FadeOut(l_1mx)
        )
        new_graph = get_beta_graph(axes, 1, 1)
        group = VGroup(graph, scaled_region)
        self.play(
            group.set_height,
            new_graph.get_height(), {"about_edge": DOWN, "stretch": True},
            group.set_color, BLUE,
            FadeOut(region),
        )
        region = scaled_region
        self.play(FadeOut(p_data_rect))
        self.wait()
        self.play(ShowCreationThenFadeAround(const))

        # Repeat
        exp1 = Integer(1)
        exp1.set_height(0.2)
        exp1.move_to(func_label[2].get_corner(UR), DL)
        exp1.shift(0.02 * DOWN + 0.07 * RIGHT)

        exp2 = exp1.copy()
        exp2.move_to(eq_1mx.get_corner(UR), DL)
        exp2.shift(0.1 * RIGHT)
        exp2.align_to(exp1, DOWN)

        shift_vect = UP + 0.5 * LEFT
        VGroup(exp1, exp2).shift(shift_vect)

        self.play(
            FadeIn(exp1, DOWN),
            FadeIn(exp2, DOWN),
            VGroup(func_label, dot, eq_1mx).shift, shift_vect,
            bayes.scale, 0.5,
            bayes.next_to, p_label, DOWN, LARGE_BUFF, {"aligned_edge": RIGHT},
        )
        nh = 1
        nt = 1
        for coin, is_heads in zip(coins[2:10], bool_values[2:10]):
            self.play(
                arrow.next_to, coin, DOWN, SMALL_BUFF,
                MaintainPositionRelativeTo(data_label, arrow),
                FadeIn(coin, DOWN),
            )
            if is_heads:
                nh += 1
                old_exp = exp1
            else:
                nt += 1
                old_exp = exp2

            new_exp = old_exp.copy()
            new_exp.increment_value(1)

            dist = scipy.stats.beta(nh + 1, nt + 1)
            new_graph = axes.get_graph(dist.pdf)
            new_region = get_region_under_curve(axes, new_graph, 0, 1)
            new_region.match_style(region)

            self.play(
                FadeOut(graph),
                FadeOut(region),
                FadeIn(new_graph),
                FadeIn(new_region),
                FadeOut(old_exp, MED_SMALL_BUFF * UP),
                FadeIn(new_exp, MED_SMALL_BUFF * DOWN),
            )
            graph = new_graph
            region = new_region
            self.remove(new_exp)
            self.add(old_exp)
            old_exp.increment_value()
            self.wait()

            if coin is coins[4]:
                area_label = TextMobject("Area = 1")
                area_label.move_to(axes.c2p(0.6, 0.8))
                self.play(GrowFromPoint(
                    area_label, const.get_center()
                ))


class PDefectEqualsQmark(Scene):
    def construct(self):
        label = TexMobject(
            "P(\\text{Defect}) = ???",
            tex_to_color_map={
                "\\text{Defect}": RED,
            }
        )
        self.play(FadeIn(label, DOWN))
        self.wait()


class UpdateOnceWithBinomial(TalkThroughCoinExample):
    def construct(self):
        # Fair bit of copy-pasting from above.  If there's
        # time, refactor this properly
        # Setup
        axes = self.get_axes()
        x_label = TexMobject("x")
        x_label.next_to(axes.x_axis.get_end(), UR, MED_SMALL_BUFF)
        axes.add(x_label)

        p_label, prob, prob_box = self.get_probability_label()
        prob_box_x = x_label.copy().move_to(prob_box)

        q_marks = prob_box[1]
        prob_box.remove(q_marks)
        prob_box.add(prob_box_x)

        self.add(axes)
        self.add(p_label)
        self.add(prob_box)

        # Coins
        bool_values = (np.random.random(100) < self.true_p)
        bool_values[:5] = [True, False, True, True, False]
        coins = self.get_coins(bool_values)
        coins.next_to(axes.y_axis, RIGHT, MED_LARGE_BUFF)
        coins.to_edge(UP)
        self.add(coins[:10])

        # Uniform pdf
        region = get_beta_graph(axes, 0, 0)
        graph = axes.get_graph(
            lambda x: 1,
            min_samples=30,
        )
        self.add(region, graph)

        # Show Bayes rule
        bayes = TexMobject(
            "p({x} | \\text{data})", "=",
            "p({x})",
            "{P(\\text{data} | {x})",
            "\\over",
            "P(\\text{data})",
            tex_to_color_map={
                "{x}": WHITE,
                "\\text{data}": GREEN,
            }
        )
        bayes.move_to(axes.c2p(0, 2.5))
        bayes.align_to(coins, LEFT)

        likelihood = bayes[9:14]
        # likelihood_rect = SurroundingRectangle(likelihood, buff=0.05)

        self.add(bayes)

        # All data at once
        brace = Brace(coins[:10], DOWN)
        all_data_label = brace.get_text("One update from all data")

        self.wait()
        self.play(
            GrowFromCenter(brace),
            FadeIn(all_data_label, 0.2 * UP),
        )
        self.wait()

        # Binomial formula
        nh = sum(bool_values[:10])
        nt = sum(~bool_values[:10])

        likelihood_brace = Brace(likelihood, UP)
        t2c = {
            str(nh): BLUE,
            str(nt): RED,
        }
        binom_formula = TexMobject(
            "{10 \\choose ", str(nh), "}",
            "x^{", str(nh), "}",
            "(1-x)^{" + str(nt) + "}",
            tex_to_color_map=t2c,
        )
        binom_formula[0][-1].set_color(BLUE)
        binom_formula[1].set_color(WHITE)
        binom_formula.set_width(likelihood_brace.get_width() + 0.5)
        binom_formula.next_to(likelihood_brace, UP)

        self.play(
            TransformFromCopy(brace, likelihood_brace),
            FadeOut(all_data_label),
            FadeIn(binom_formula)
        )
        self.wait()

        # New plot
        rhs = TexMobject(
            "C \\cdot",
            "x^{", str(nh), "}",
            "(1-x)^{", str(nt), "}",
            tex_to_color_map=t2c
        )
        rhs.next_to(bayes[:5], DOWN, LARGE_BUFF, aligned_edge=LEFT)
        eq = TexMobject("=")
        eq.rotate(90 * DEGREES)
        eq.next_to(bayes[:5], DOWN, buff=0.35)

        dist = scipy.stats.beta(nh + 1, nt + 1)
        new_graph = axes.get_graph(dist.pdf)
        new_graph.shift(1e-6 * UP)
        new_graph.set_stroke(WHITE, 1, opacity=0.5)
        new_region = get_region_under_curve(axes, new_graph, 0, 1)
        new_region.match_style(region)
        new_region.set_opacity(0.75)

        self.add(new_region, new_graph, bayes)
        region.unlock_triangulation()
        self.play(
            FadeOut(graph),
            FadeOut(region),
            FadeIn(new_graph),
            FadeIn(new_region),
            run_time=1,
        )
        self.play(
            Write(eq),
            FadeIn(rhs, UP)
        )
        self.wait()
