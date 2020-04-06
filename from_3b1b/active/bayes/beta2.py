from manimlib.imports import *
from from_3b1b.active.bayes.beta_helpers import *
from from_3b1b.active.bayes.beta1 import *

import scipy.stats

OUTPUT_DIRECTORY = "bayes/beta2"


class PartTwoReady(Scene):
    def construct(self):
        br = FullScreenFadeRectangle()
        br.set_fill(GREY_E, 1)
        self.add(br)
        text = TextMobject(
            "Part 2\\\\",
            "Early view\\\\for supporters"
        )
        text.scale(1.5)
        text[0].match_width(text[1], about_edge=DOWN)
        text[0].shift(MED_SMALL_BUFF * UP)
        text[1].set_color("#f96854")
        self.add(text)


class ShowBayesianUpdating(Scene):
    CONFIG = {
        "true_p": 0.72,
        "random_seed": 4,
        "initial_axis_scale_factor": 3.5
    }

    def construct(self):
        # Axes
        axes = self.get_axes()
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
            self.play(
                FadeIn(new_graph),
                run_time=0.25,
            )
            self.play(
                FadeOut(graph),
                run_time=0.25,
            )
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
    def get_axes(self):
        axes = get_beta_dist_axes(
            label_y=True,
            y_unit=1,
        )
        axes.y_axis.numbers.set_submobjects([
            *axes.y_axis.numbers[:5],
            *axes.y_axis.numbers[4::5]
        ])
        sf = self.initial_axis_scale_factor
        axes.y_axis.stretch(sf, 1, about_point=axes.c2p(0, 0))
        for number in axes.y_axis.numbers:
            number.stretch(1 / sf, 1)
        axes.y_axis_label.to_edge(LEFT)
        axes.y_axis_label.add_background_rectangle(opacity=1)
        axes.set_stroke(background=True)
        return axes

    def get_coins(self, bool_values):
        coins = VGroup(*[
            get_coin(BLUE_E, "H")
            if heads else
            get_coin(RED_E, "T")
            for heads in bool_values
        ])
        coins.arrange_in_grid(n_rows=10, buff=MED_LARGE_BUFF)
        coins.set_height(5)
        return coins

    def get_probability_label(self):
        head = get_coin(BLUE_E, "H")
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

        morty = Mortimer()
        morty.set_height(2)
        morty.to_corner(DR)

        self.play(group.next_to, ORIGIN, LEFT)
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
            FadeInFrom(zero, DOWN),
            FadeOutAndShift(infty, UP),
            morty.change, "sad", zero
        )
        self.play(Blink(morty))
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

        arrow = arrows[0]
        arrow.generate_target()
        arrow.target.next_to(bars[16], UP, SMALL_BUFF)
        bars[16].set_color(GREEN)

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

        # Refine
        last_ineq_label = ineq_label
        last_bars = bars
        all_ineq_labels = VGroup(ineq_label)
        for step_size in [0.025, 0.01, 0.005, 0.001]:
            new_bars = self.get_bars(axes, dist, step_size)
            new_ineq_label = TexMobject(
                "P(0.8 < s < {:.3})".format(0.8 + step_size),
                tex_to_color_map={"s": YELLOW},
            )

            if step_size <= 0.005:
                new_bars.set_stroke(width=0)

            arrow.generate_target()
            bar = new_bars[int(0.8 * len(new_bars))]
            bar.set_color(GREEN)
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
                FadeOutAndShift(last_ineq_label, vect),
                FadeInFrom(new_ineq_label, -vect),
                run_time=2,
            )
            last_ineq_label = new_ineq_label
            last_bars = new_bars
            all_ineq_labels.add(new_ineq_label)

        # Show continuous graph
        graph = get_beta_graph(axes, 3, 1)
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
        self.play(
            arrow.scale, 0, {"about_edge": DOWN},
            FadeOutAndShift(to_zero_words, DOWN),
            LaggedStartMap(FadeOutAndShiftDown, all_ineq_labels),
            LaggedStartMap(FadeOutAndShiftDown, rhss),
        )

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
            FadeOut(limit_words)
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

        self.play(FadeInFrom(total_label, DOWN))
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
            self.play(ReplacementTransform(
                bars, new_bars, lag_ratio=step_size
            ))
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
            TexMobject("s", color=YELLOW),
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
            FadeInFrom(p_label, 2 * DOWN),
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
            run_time=3,
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

        s_label = TexMobject("s")
        s_label.set_color(YELLOW)
        s_label.next_to(axes.x_axis, RIGHT)
        axes.x_axis.add(s_label)
        axes.x_axis.s_label = s_label

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
                FadeOutAndShift(last_row, DOWN),
                FadeIn(row, lag_ratio=0.1)
            )
            last_row = row
        self.play(FadeOutAndShift(last_row, DOWN))

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
            FadeInFrom(coin, DOWN),
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
            FadeOutAndShift(one, UP),
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
            FadeOutAndShift(two, UP),
            FadeInFrom(const, DOWN)
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
            FadeInFrom(l_1mx, 0.5 * DOWN),
        )
        self.wait()
        self.play(ShowCreationThenFadeOut(Underline(p_label)))
        self.play(Indicate(coins[1]))
        self.wait()
        self.play(
            TransformFromCopy(l_1mx, eq_1mx),
            FadeInFrom(dot, RIGHT),
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
            FadeInFrom(exp1, DOWN),
            FadeInFrom(exp2, DOWN),
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
                FadeInFrom(coin, DOWN),
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
                FadeOutAndShift(old_exp, MED_SMALL_BUFF * UP),
                FadeInFrom(new_exp, MED_SMALL_BUFF * DOWN),
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
        self.play(FadeInFrom(label, DOWN))
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
            FadeInFrom(all_data_label, 0.2 * UP),
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
            FadeInFrom(rhs, UP)
        )
        self.wait()
