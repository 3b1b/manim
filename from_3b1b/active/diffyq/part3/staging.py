from manimlib.imports import *

from active_projects.diffyq.part2.fourier_series import FourierOfTrebleClef


class FourierNameIntro(Scene):
    def construct(self):
        self.show_two_titles()
        self.transition_to_image()
        self.show_paper()

    def show_two_titles(self):
        lt = TextMobject("Fourier", "Series")
        rt = TextMobject("Fourier", "Transform")
        lt_variants = VGroup(
            TextMobject("Complex", "Fourier Series"),
            TextMobject("Discrete", "Fourier Series"),
        )
        rt_variants = VGroup(
            TextMobject("Discrete", "Fourier Transform"),
            TextMobject("Fast", "Fourier Transform"),
            TextMobject("Quantum", "Fourier Transform"),
        )

        titles = VGroup(lt, rt)
        titles.scale(1.5)
        for title, vect in (lt, LEFT), (rt, RIGHT):
            title.move_to(vect * FRAME_WIDTH / 4)
            title.to_edge(UP)

        for title, variants in (lt, lt_variants), (rt, rt_variants):
            title.save_state()
            title.target = title.copy()
            title.target.scale(1 / 1.5, about_edge=RIGHT)
            for variant in variants:
                variant.move_to(title.target, UR)
                variant[0].set_color(YELLOW)

        v_line = Line(UP, DOWN)
        v_line.set_height(FRAME_HEIGHT)
        v_line.set_stroke(WHITE, 2)

        self.play(
            FadeInFrom(lt, RIGHT),
            ShowCreation(v_line)
        )
        self.play(
            FadeInFrom(rt, LEFT),
        )
        # Edit in images of circle animations
        # and clips from FT video

        # for title, variants in (rt, rt_variants), (lt, lt_variants):
        for title, variants in [(rt, rt_variants)]:
            # Maybe do it for left variant, maybe not...
            self.play(
                MoveToTarget(title),
                FadeInFrom(variants[0][0], LEFT)
            )
            for v1, v2 in zip(variants, variants[1:]):
                self.play(
                    FadeOutAndShift(v1[0], UP),
                    FadeInFrom(v2[0], DOWN),
                    run_time=0.5,
                )
                self.wait(0.5)
            self.play(
                Restore(title),
                FadeOut(variants[-1][0])
            )
        self.wait()

        self.titles = titles
        self.v_line = v_line

    def transition_to_image(self):
        titles = self.titles
        v_line = self.v_line

        image = ImageMobject("Joseph Fourier")
        image.set_height(5)
        image.to_edge(LEFT)

        frame = Rectangle()
        frame.replace(image, stretch=True)

        name = TextMobject("Joseph", "Fourier")
        fourier_part = name.get_part_by_tex("Fourier")
        fourier_part.set_color(YELLOW)
        F_sym = fourier_part[0]
        name.match_width(image)
        name.next_to(image, DOWN)

        self.play(
            ReplacementTransform(v_line, frame),
            FadeIn(image),
            FadeIn(name[0]),
            *[
                ReplacementTransform(
                    title[0].deepcopy(),
                    name[1]
                )
                for title in titles
            ],
            titles.scale, 0.65,
            titles.arrange, DOWN,
            titles.next_to, image, UP,
        )
        self.wait()

        big_F = F_sym.copy()
        big_F.set_fill(opacity=0)
        big_F.set_stroke(WHITE, 2)
        big_F.set_height(3)
        big_F.move_to(midpoint(
            image.get_right(),
            RIGHT_SIDE,
        ))
        big_F.shift(DOWN)
        equivalence = VGroup(
            fourier_part.copy().scale(1.25),
            TexMobject("\\Leftrightarrow").scale(1.5),
            TextMobject("Break down into\\\\pure frequencies"),
        )
        equivalence.arrange(RIGHT)
        equivalence.move_to(big_F)
        equivalence.to_edge(UP)

        self.play(
            FadeIn(big_F),
            TransformFromCopy(fourier_part, equivalence[0]),
            Write(equivalence[1:]),
        )
        self.wait(3)
        self.play(FadeOut(VGroup(big_F, equivalence)))

        self.image = image
        self.name = name

    def show_paper(self):
        image = self.image
        paper = ImageMobject("Fourier paper")
        paper.match_height(image)
        paper.next_to(image, RIGHT, MED_LARGE_BUFF)

        date = TexMobject("1822")
        date.next_to(paper, DOWN)
        date_rect = SurroundingRectangle(date)
        date_rect.scale(0.3)
        date_rect.set_color(RED)
        date_rect.shift(1.37 * UP + 0.08 * LEFT)
        date_arrow = Arrow(
            date_rect.get_bottom(),
            date.get_top(),
            buff=SMALL_BUFF,
            color=date_rect.get_color(),
        )

        heat_rect = SurroundingRectangle(
            TextMobject("CHALEUR")
        )
        heat_rect.set_color(RED)
        heat_rect.scale(0.6)
        heat_rect.move_to(
            paper.get_top() +
            1.22 * DOWN + 0.37 * RIGHT
        )
        heat_word = TextMobject("Heat")
        heat_word.scale(1.5)
        heat_word.next_to(paper, UP)
        heat_word.shift(paper.get_width() * RIGHT)
        heat_arrow = Arrow(
            heat_rect.get_top(),
            heat_word.get_left(),
            buff=0.1,
            path_arc=-60 * DEGREES,
            color=heat_rect.get_color(),
        )

        self.play(FadeInFrom(paper, LEFT))
        self.play(
            ShowCreation(date_rect),
        )
        self.play(
            GrowFromPoint(date, date_arrow.get_start()),
            ShowCreation(date_arrow),
        )
        self.wait(3)

        # Insert animation of circles/sine waves
        # approximating a square wave

        self.play(
            ShowCreation(heat_rect),
        )
        self.play(
            GrowFromPoint(heat_word, heat_arrow.get_start()),
            ShowCreation(heat_arrow),
        )
        self.wait(3)


class ManyCousinsOfFourierThings(Scene):
    def construct(self):
        series_variants = VGroup(
            TextMobject("Complex", "Fourier Series"),
            TextMobject("Discrete", "Fourier Series"),
        )
        transform_variants = VGroup(
            TextMobject("Discrete", "Fourier Transform"),
            TextMobject("Fast", "Fourier Transform"),
            TextMobject("Quantum", "Fourier Transform"),
        )
        groups = VGroup(series_variants, transform_variants)
        for group, vect in zip(groups, [LEFT, RIGHT]):
            group.scale(0.7)
            group.arrange(DOWN, aligned_edge=LEFT)
            group.move_to(
                vect * FRAME_WIDTH / 4
            )
            group.set_color(YELLOW)

        self.play(*[
            LaggedStartMap(FadeIn, group)
            for group in groups
        ])
        self.play(*[
            LaggedStartMap(FadeOut, group)
            for group in groups
        ])


class FourierSeriesIllustraiton(Scene):
    CONFIG = {
        "n_range": range(1, 31, 2),
        "axes_config": {
            "axis_config": {
                "include_tip": False,
            },
            "x_axis_config": {
                "tick_frequency": 1 / 4,
                "unit_size": 4,
            },
            "x_min": 0,
            "x_max": 1,
            "y_min": -1,
            "y_max": 1,
        },
        "colors": [BLUE, GREEN, RED, YELLOW, PINK],
    }

    def construct(self):
        aaa_group = self.get_axes_arrow_axes()
        aaa_group.shift(2 * UP)
        aaa_group.shift_onto_screen()
        axes1, arrow, axes2 = aaa_group

        axes2.add(self.get_target_func_graph(axes2))

        sine_graphs = self.get_sine_graphs(axes1)
        partial_sums = self.get_partial_sums(axes1, sine_graphs)

        sum_tex = self.get_sum_tex()
        sum_tex.next_to(axes1, DOWN, LARGE_BUFF)
        sum_tex.shift(RIGHT)
        eq = TexMobject("=")
        target_func_tex = self.get_target_func_tex()
        target_func_tex.next_to(axes2, DOWN)
        target_func_tex.match_y(sum_tex)
        eq.move_to(midpoint(
            target_func_tex.get_left(),
            sum_tex.get_right()
        ))

        range_words = TextMobject(
            "For $0 \\le x \\le 1$"
        )
        range_words.next_to(
            VGroup(sum_tex, target_func_tex),
            DOWN,
        )

        rects = it.chain(
            [
                SurroundingRectangle(piece)
                for piece in self.get_sum_tex_pieces(sum_tex)
            ],
            it.cycle([None])
        )

        self.add(axes1, arrow, axes2)
        self.add(sum_tex, eq, target_func_tex)
        self.add(range_words)

        curr_partial_sum = axes1.get_graph(lambda x: 0)
        curr_partial_sum.set_stroke(width=1)
        for sine_graph, partial_sum, rect in zip(sine_graphs, partial_sums, rects):
            anims1 = [
                ShowCreation(sine_graph)
            ]
            partial_sum.set_stroke(BLACK, 4, background=True)
            anims2 = [
                curr_partial_sum.set_stroke,
                {"width": 1, "opacity": 0.5},
                curr_partial_sum.set_stroke,
                {"width": 0, "background": True},
                ReplacementTransform(
                    sine_graph, partial_sum,
                    remover=True
                ),
            ]
            if rect:
                rect.match_style(sine_graph)
                anims1.append(ShowCreation(rect))
                anims2.append(FadeOut(rect))
            self.play(*anims1)
            self.play(*anims2)
            curr_partial_sum = partial_sum

    def get_axes_arrow_axes(self):
        axes1 = Axes(**self.axes_config)
        axes1.x_axis.add_numbers(
            0.5, 1,
            number_config={"num_decimal_places": 1}
        )
        axes1.y_axis.add_numbers(
            -1, 1,
            number_config={"num_decimal_places": 1},
            direction=LEFT,
        )
        axes2 = axes1.deepcopy()

        arrow = Arrow(LEFT, RIGHT, color=WHITE)
        group = VGroup(axes1, arrow, axes2)
        group.arrange(RIGHT, buff=MED_LARGE_BUFF)
        return group

    def get_sine_graphs(self, axes):
        sine_graphs = VGroup(*[
            axes.get_graph(self.generate_nth_func(n))
            for n in self.n_range
        ])
        sine_graphs.set_stroke(width=3)
        for graph, color in zip(sine_graphs, it.cycle(self.colors)):
            graph.set_color(color)
        return sine_graphs

    def get_partial_sums(self, axes, sine_graphs):
        partial_sums = VGroup(*[
            axes.get_graph(self.generate_kth_partial_sum_func(k + 1))
            for k in range(len(self.n_range))
        ])
        partial_sums.match_style(sine_graphs)
        return partial_sums

    def get_sum_tex(self):
        return TexMobject(
            "\\frac{4}{\\pi} \\left(",
            "\\frac{\\cos(\\pi x)}{1}",
            "-\\frac{\\cos(3\\pi x)}{3}",
            "+\\frac{\\cos(5\\pi x)}{5}",
            "- \\cdots \\right)"
        ).scale(0.75)

    def get_sum_tex_pieces(self, sum_tex):
        return sum_tex[1:4]

    def get_target_func_tex(self):
        step_tex = TexMobject(
            """
            1 \\quad \\text{if $x < 0.5$} \\\\
            0 \\quad \\text{if $x = 0.5$} \\\\
            -1 \\quad \\text{if $x > 0.5$} \\\\
            """
        )
        lb = Brace(step_tex, LEFT, buff=SMALL_BUFF)
        step_tex.add(lb)
        return step_tex

    def get_target_func_graph(self, axes):
        step_func = axes.get_graph(
            lambda x: (1 if x < 0.5 else -1),
            discontinuities=[0.5],
            color=YELLOW,
            stroke_width=3,
        )
        dot = Dot(axes.c2p(0.5, 0), color=step_func.get_color())
        dot.scale(0.5)
        step_func.add(dot)
        return step_func

    # def generate_nth_func(self, n):
    #     return lambda x: (4 / n / PI) * np.sin(TAU * n * x)

    def generate_nth_func(self, n):
        return lambda x: np.prod([
            (4 / PI),
            (1 / n) * (-1)**((n - 1) / 2),
            np.cos(PI * n * x)
        ])

    def generate_kth_partial_sum_func(self, k):
        return lambda x: np.sum([
            self.generate_nth_func(n)(x)
            for n in self.n_range[:k]
        ])


class FourierSeriesOfLineIllustration(FourierSeriesIllustraiton):
    CONFIG = {
        "n_range": range(1, 31, 2),
        "axes_config": {
            "y_axis_config": {
                "unit_size": 2,
                "tick_frequency": 0.25,
                "numbers_with_elongated_ticks": [-1, 1],
            }
        }
    }

    def get_sum_tex(self):
        return TexMobject(
            "\\frac{8}{\\pi^2} \\left(",
            "\\frac{\\cos(\\pi x)}{1^2}",
            "+\\frac{\\cos(3\\pi x)}{3^2}",
            "+\\frac{\\cos(5\\pi x)}{5^2}",
            "+ \\cdots \\right)"
        ).scale(0.75)

    # def get_sum_tex_pieces(self, sum_tex):
    #     return sum_tex[1:4]

    def get_target_func_tex(self):
        result = TexMobject("1 - 2x")
        result.scale(1.5)
        point = VectorizedPoint()
        point.next_to(result, RIGHT, 1.5 * LARGE_BUFF)
        # result.add(point)
        return result

    def get_target_func_graph(self, axes):
        return axes.get_graph(
            lambda x: 1 - 2 * x,
            color=YELLOW,
            stroke_width=3,
        )

    # def generate_nth_func(self, n):
    #     return lambda x: (4 / n / PI) * np.sin(TAU * n * x)

    def generate_nth_func(self, n):
        return lambda x: np.prod([
            (8 / PI**2),
            (1 / n**2),
            np.cos(PI * n * x)
        ])


class CircleAnimationOfF(FourierOfTrebleClef):
    CONFIG = {
        "height": 3,
        "n_circles": 200,
        "run_time": 10,
        "arrow_config": {
            "tip_length": 0.1,
            "stroke_width": 2,
        }
    }

    def get_shape(self):
        path = VMobject()
        shape = TextMobject("F")
        for sp in shape.family_members_with_points():
            path.append_points(sp.points)
        return path


class ExponentialDecay(PiCreatureScene):
    def construct(self):
        k = 0.2
        mk_tex = "-0.2"
        mk_tex_color = GREEN
        t2c = {mk_tex: mk_tex_color}

        # Pi creature
        randy = self.pi_creature
        randy.flip()
        randy.set_height(2.5)
        randy.move_to(3 * RIGHT)
        randy.to_edge(DOWN)
        bubble = ThoughtBubble(
            direction=LEFT,
            height=3.5,
            width=3,
        )
        bubble.pin_to(randy)
        bubble.set_fill(DARKER_GREY)
        exp = TexMobject(
            "Ce^{", mk_tex, "t}",
            tex_to_color_map=t2c,
        )
        exp.move_to(bubble.get_bubble_center())

        # Setup axes
        axes = Axes(
            x_min=0,
            x_max=13,
            y_min=-4,
            y_max=4,
        )
        axes.set_stroke(width=2)
        axes.set_color(LIGHT_GREY)
        axes.scale(0.9)
        axes.to_edge(LEFT, buff=LARGE_BUFF)
        axes.x_axis.add_numbers()
        axes.y_axis.add_numbers()
        axes.y_axis.add_numbers(0)
        axes.x_axis.add(
            TextMobject("Time").next_to(
                axes.x_axis.get_end(), DR,
            )
        )
        axes.y_axis.add(
            TexMobject("f").next_to(
                axes.y_axis.get_corner(UR), RIGHT,
            ).set_color(YELLOW)
        )
        axes.x_axis.set_opacity(0)

        # Value trackers
        y_tracker = ValueTracker(3)
        x_tracker = ValueTracker(0)
        dydt_tracker = ValueTracker()
        dxdt_tracker = ValueTracker(0)
        self.add(
            y_tracker, x_tracker,
            dydt_tracker, dxdt_tracker,
        )

        get_y = y_tracker.get_value
        get_x = x_tracker.get_value
        get_dydt = dydt_tracker.get_value
        get_dxdt = dxdt_tracker.get_value

        dydt_tracker.add_updater(lambda m: m.set_value(
            - k * get_y()
        ))
        y_tracker.add_updater(lambda m, dt: m.increment_value(
            dt * get_dydt()
        ))
        x_tracker.add_updater(lambda m, dt: m.increment_value(
            dt * get_dxdt()
        ))

        # Tip/decimal
        tip = ArrowTip(color=YELLOW)
        tip.set_width(0.25)
        tip.add_updater(lambda m: m.move_to(
            axes.c2p(get_x(), get_y()), LEFT
        ))
        decimal = DecimalNumber()
        decimal.add_updater(lambda d: d.set_value(get_y()))
        decimal.add_updater(lambda d: d.next_to(
            tip, RIGHT,
            SMALL_BUFF,
        ))

        # Rate of change arrow
        arrow = Vector(
            DOWN, color=RED,
            max_stroke_width_to_length_ratio=50,
            max_tip_length_to_length_ratio=0.2,
        )
        arrow.set_stroke(width=4)
        arrow.add_updater(lambda m: m.scale(
            2.5 * abs(get_dydt()) / m.get_length()
        ))
        arrow.add_updater(lambda m: m.move_to(
            tip.get_left(), UP
        ))

        # Graph
        graph = TracedPath(tip.get_left)

        # Equation
        ode = TexMobject(
            "{d{f} \\over dt}(t)",
            "=", mk_tex, "\\cdot {f}(t)",
            tex_to_color_map={
                "{f}": YELLOW,
                "=": WHITE,
                mk_tex: mk_tex_color
            }
        )
        ode.to_edge(UP)
        dfdt = ode[:3]
        ft = ode[-2:]

        self.add(axes)
        self.add(tip)
        self.add(decimal)
        self.add(arrow)
        self.add(randy)
        self.add(ode)

        # Show rate of change dependent on itself
        rect = SurroundingRectangle(dfdt)
        self.play(ShowCreation(rect))
        self.wait()
        self.play(
            Transform(
                rect,
                SurroundingRectangle(ft)
            )
        )
        self.wait(3)

        # Show graph over time
        self.play(
            DrawBorderThenFill(bubble),
            Write(exp),
            FadeOut(rect),
            randy.change, "thinking",
        )
        axes.x_axis.set_opacity(1)
        self.play(
            y_tracker.set_value, 3,
            ShowCreation(axes.x_axis),
        )
        dxdt_tracker.set_value(1)
        self.add(graph)
        randy.add_updater(lambda r: r.look_at(tip))
        self.wait(4)

        # Show derivative of exponential
        eq = TexMobject("=")
        eq.next_to(ode.get_part_by_tex("="), DOWN, LARGE_BUFF)
        exp.generate_target()
        exp.target.next_to(eq, LEFT)
        d_dt = TexMobject("{d \\over dt}")
        d_dt.next_to(exp.target, LEFT)
        const = TexMobject(mk_tex)
        const.set_color(mk_tex_color)
        dot = TexMobject("\\cdot")
        const.next_to(eq, RIGHT)
        dot.next_to(const, RIGHT, 2 * SMALL_BUFF)
        exp_copy = exp.copy()
        exp_copy.next_to(dot, RIGHT, 2 * SMALL_BUFF)
        VGroup(const, dot, eq).align_to(exp_copy, DOWN)

        self.play(
            MoveToTarget(exp),
            FadeOut(bubble),
            FadeIn(d_dt),
            FadeIn(eq),
        )
        self.wait(2)
        self.play(
            ApplyMethod(
                exp[1].copy().replace,
                const[0],
            )
        )
        self.wait()
        rect = SurroundingRectangle(exp)
        rect.set_stroke(BLUE, 2)
        self.play(FadeIn(rect))
        self.play(
            Write(dot),
            TransformFromCopy(exp, exp_copy),
            rect.move_to, exp_copy
        )
        self.play(FadeOut(rect))
        self.wait(5)


class InvestmentGrowth(Scene):
    CONFIG = {
        "output_tex": "{M}",
        "output_color": GREEN,
        "initial_value": 1,
        "initial_value_tex": "{M_0}",
        "k": 0.05,
        "k_tex": "0.05",
        "total_time": 43,
        "time_rate": 3,
    }

    def construct(self):
        # Axes
        axes = Axes(
            x_min=0,
            x_max=self.total_time,
            y_min=0,
            y_max=6,
            x_axis_config={
                "unit_size": 0.3,
                "tick_size": 0.05,
                "numbers_with_elongated_ticks": range(
                    0, self.total_time, 5
                )
            }
        )
        axes.to_corner(DL, buff=LARGE_BUFF)

        time_label = TextMobject("Time")
        time_label.next_to(
            axes.x_axis.get_right(),
            UP, MED_LARGE_BUFF
        )
        time_label.shift_onto_screen()
        axes.x_axis.add(time_label)
        money_label = TexMobject(self.output_tex)
        money_label.set_color(self.output_color)
        money_label.next_to(
            axes.y_axis.get_top(),
            UP,
        )
        axes.y_axis.add(money_label)

        # Graph
        graph = axes.get_graph(
            lambda x: self.initial_value * np.exp(self.k * x)
        )
        graph.set_color(self.output_color)
        full_graph = graph.copy()
        time_tracker = self.get_time_tracker()
        graph.add_updater(lambda m: m.pointwise_become_partial(
            full_graph, 0,
            np.clip(
                time_tracker.get_value() / self.total_time,
                0, 1,
            )
        ))

        # Equation
        tex_kwargs = {
            "tex_to_color_map": {
                self.output_tex: self.output_color,
                self.initial_value_tex: BLUE,
            }
        }
        ode = TexMobject(
            "{d",
            "\\over dt}",
            self.output_tex,
            "(t)",
            "=", self.k_tex,
            "\\cdot", self.output_tex, "(t)",
            **tex_kwargs
        )
        ode.to_edge(UP)
        exp = TexMobject(
            self.output_tex,
            "(t) =", self.initial_value_tex,
            "e^{", self.k_tex, "t}",
            **tex_kwargs
        )
        exp.next_to(ode, DOWN, LARGE_BUFF)

        M0_part = exp.get_part_by_tex(self.initial_value_tex)
        exp_part = exp[-3:]
        M0_label = M0_part.copy()
        M0_label.next_to(
            axes.c2p(0, self.initial_value),
            LEFT
        )
        M0_part.set_opacity(0)
        exp_part.save_state()
        exp_part.align_to(M0_part, LEFT)

        self.add(axes)
        self.add(graph)
        self.add(time_tracker)

        self.play(FadeInFromDown(ode))
        self.wait(6)
        self.play(FadeInFrom(exp, UP))
        self.wait(2)
        self.play(
            Restore(exp_part),
            M0_part.set_opacity, 1,
        )
        self.play(TransformFromCopy(
            M0_part, M0_label
        ))
        self.wait(5)

    def get_time_tracker(self):
        time_tracker = ValueTracker(0)
        time_tracker.add_updater(
            lambda m, dt: m.increment_value(
                self.time_rate * dt
            )
        )
        return time_tracker


class GrowingPileOfMoney(InvestmentGrowth):
    CONFIG = {
        "total_time": 60
    }

    def construct(self):
        initial_count = 5
        k = self.k
        total_time = self.total_time

        time_tracker = self.get_time_tracker()

        final_count = initial_count * np.exp(k * total_time)
        dollar_signs = VGroup(*[
            TexMobject("\\$")
            for x in range(int(final_count))
        ])
        dollar_signs.set_color(GREEN)
        for ds in dollar_signs:
            ds.shift(
                3 * np.random.random(3)
            )
        dollar_signs.center()
        dollar_signs.sort(get_norm)
        dollar_signs.set_stroke(BLACK, 3, background=True)

        def update_dollar_signs(group):
            t = time_tracker.get_value()
            count = initial_count * np.exp(k * t)
            alpha = count / final_count
            n, sa = integer_interpolate(0, len(dollar_signs), alpha)
            group.set_opacity(1)
            group[n:].set_opacity(0)
            group[n].set_opacity(sa)

        dollar_signs.add_updater(update_dollar_signs)

        self.add(time_tracker)
        self.add(dollar_signs)
        self.wait(20)


class CarbonDecayCurve(InvestmentGrowth):
    CONFIG = {
        "output_tex": "{^{14}C}",
        "output_color": GOLD,
        "initial_value": 4,
        "initial_value_tex": "{^{14}C_0}",
        "k": -0.1,
        "k_tex": "-k",
        "time_rate": 6,
    }


class CarbonDecayingInMammoth(Scene):
    def construct(self):
        mammoth = SVGMobject("Mammoth")
        mammoth.set_color(
            interpolate_color(GREY_BROWN, WHITE, 0.25)
        )
        mammoth.set_height(4)
        body = mammoth[9]

        atoms = VGroup(*[
            self.get_atom(body)
            for n in range(600)
        ])

        p_decay = 0.2

        def update_atoms(group, dt):
            for atom in group:
                if np.random.random() < dt * p_decay:
                    group.remove(atom)
            return group
        atoms.add_updater(update_atoms)

        self.add(mammoth)
        self.add(atoms)
        self.wait(20)

    def get_atom(self, body):
        atom = Dot(color=GOLD)
        atom.set_height(0.05)

        dl = body.get_corner(DL)
        ur = body.get_corner(UR)

        wn = 0
        while wn == 0:
            point = np.array([
                interpolate(dl[0], ur[0], np.random.random()),
                interpolate(dl[1], ur[1], np.random.random()),
                0
            ])
            wn = get_winding_number([
                body.point_from_proportion(a) - point
                for a in np.linspace(0, 1, 300)
            ])
            wn = int(np.round(wn))

        atom.move_to(point)
        return atom


class BoundaryConditionInterlude(Scene):
    def construct(self):
        background = FullScreenFadeRectangle(
            fill_color=DARK_GREY
        )
        storyline = self.get_main_storyline()
        storyline.generate_target()
        v_shift = 2 * DOWN
        storyline.target.shift(v_shift)
        im_to_im = storyline[1].get_center() - storyline[0].get_center()

        bc_image = self.get_labeled_image(
            "Boundary\\\\conditions",
            "boundary_condition_thumbnail"
        )
        bc_image.next_to(storyline[1], UP)
        new_arrow0 = Arrow(
            storyline.arrows[0].get_start() + v_shift,
            bc_image.get_left() + SMALL_BUFF * LEFT,
            path_arc=-90 * DEGREES,
            buff=0,
        )
        new_mid_arrow = Arrow(
            bc_image.get_bottom(),
            storyline[1].get_top() + v_shift,
            buff=SMALL_BUFF,
            path_arc=60 * DEGREES,
        )

        # BC detour
        self.add(background)
        self.add(storyline[0])
        for im1, im2, arrow in zip(storyline, storyline[1:], storyline.arrows):
            self.add(im2, im1)
            self.play(
                FadeInFrom(im2, -im_to_im),
                ShowCreation(arrow),
            )
        self.wait()
        self.play(
            GrowFromCenter(bc_image),
            MoveToTarget(storyline),
            Transform(
                storyline.arrows[0],
                new_arrow0,
            ),
            MaintainPositionRelativeTo(
                storyline.arrows[1],
                storyline,
            ),
        )
        self.play(ShowCreation(new_mid_arrow))
        self.wait()

        # From BC to next step
        rect1 = bc_image[2].copy()
        rect2 = storyline[1][2].copy()
        rect3 = storyline[2][2].copy()
        for rect in rect1, rect2, rect3:
            rect.set_stroke(YELLOW, 3)

        self.play(FadeIn(rect1))
        kw = {"path_arc": 60 * DEGREES}
        self.play(
            LaggedStart(
                Transform(rect1, rect2, **kw),
                # TransformFromCopy(rect1, rect3, **kw),
                lag_ratio=0.4,
            )
        )
        self.play(
            FadeOut(rect1),
            # FadeOut(rect3),
        )

        # Reorganize images
        im1, im3, im4 = storyline
        im2 = bc_image
        l_group = Group(im1, im2)
        r_group = Group(im3, im4)
        for group in l_group, r_group:
            group.generate_target()
            group.target.arrange(DOWN, buff=LARGE_BUFF)
            group.target.center()

        l_group.target.to_edge(LEFT)
        r_group.target.move_to(
            FRAME_WIDTH * RIGHT / 4
        )
        brace = Brace(r_group.target, LEFT)
        nv_text = brace.get_text("Next\\\\video")
        nv_text.scale(1.5, about_edge=RIGHT)
        nv_text.set_color(YELLOW)
        brace.set_color(YELLOW)

        arrows = VGroup(
            storyline.arrows,
            new_mid_arrow,
        )

        self.play(
            LaggedStart(
                MoveToTarget(l_group),
                MoveToTarget(r_group),
                lag_ratio=0.3,
            ),
            FadeOut(arrows),
        )
        self.play(
            GrowFromCenter(brace),
            FadeInFrom(nv_text, RIGHT)
        )
        self.wait()

    def get_main_storyline(self):
        images = Group(
            self.get_sine_curve_image(),
            self.get_linearity_image(),
            self.get_fourier_series_image(),
        )
        for image in images:
            image.set_height(3)
        images.arrange(RIGHT, buff=1)
        images.set_width(FRAME_WIDTH - 1)

        arrows = VGroup()
        for im1, im2 in zip(images, images[1:]):
            arrow = Arrow(
                im1.get_top(),
                im2.get_top(),
                color=WHITE,
                buff=MED_SMALL_BUFF,
                path_arc=-120 * DEGREES,
                rectangular_stem_width=0.025,
            )
            arrow.scale(0.7, about_edge=DOWN)
            arrows.add(arrow)
        images.arrows = arrows

        return images

    def get_sine_curve_image(self):
        return self.get_labeled_image(
            "Sine curves",
            "sine_curve_temp_graph",
        )

    def get_linearity_image(self):
        return self.get_labeled_image(
            "Linearity",
            "linearity_thumbnail",
        )

    def get_fourier_series_image(self):
        return self.get_labeled_image(
            "Fourier series",
            "fourier_series_thumbnail",
        )

    def get_labeled_image(self, text, image_file):
        rect = ScreenRectangle(height=2)
        border = rect.copy()
        rect.set_fill(BLACK, 1)
        rect.set_stroke(WHITE, 0)
        border.set_stroke(WHITE, 2)

        text_mob = TextMobject(text)
        text_mob.set_stroke(BLACK, 5, background=True)
        text_mob.next_to(rect.get_top(), DOWN, SMALL_BUFF)

        image = ImageMobject(image_file)
        image.replace(rect, dim_to_match=1)
        image.scale(0.8, about_edge=DOWN)

        return Group(rect, image, border, text_mob)


class GiantCross(Scene):
    def construct(self):
        rect = FullScreenFadeRectangle()
        cross = Cross(rect)
        cross.set_stroke(RED, 25)

        words = TextMobject("This wouldn't\\\\happen!")
        words.scale(2)
        words.set_color(RED)
        words.to_edge(UP)

        self.play(
            FadeInFromDown(words),
            ShowCreation(cross),
        )
        self.wait()


class EndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "1stViewMaths",
            "Adrian Robinson",
            "Alexis Olson",
            "Andreas Benjamin Brössel",
            "Andrew Busey",
            "Ankalagon",
            "Antoine Bruguier",
            "Antonio Juarez",
            "Arjun Chakroborty",
            "Art Ianuzzi",
            "Awoo",
            "Ayan Doss",
            "AZsorcerer",
            "Barry Fam",
            "Bernd Sing",
            "Boris Veselinovich",
            "Brian Staroselsky",
            "Charles Southerland",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Cooper Jones",
            "Danger Dai",
            "Daniel Pang",
            "Dave B",
            "Dave Kester",
            "David B. Hill",
            "David Clark",
            "Delton Ding",
            "eaglle",
            "Empirasign",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Fernando Via Canel",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Hitoshi Yamauchi",
            "Isaac Jeffrey Lee",
            "j eduardo perez",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jameel Syed",
            "Jason Hise",
            "Jeff Linse",
            "Jeff Straathof",
            "John C. Vesey",
            "John Griffith",
            "John Haley",
            "John V Wertheim",
            "Jonathan Eppele",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Kartik\\\\Cating-Subramanian",
            "L0j1k",
            "Lee Redden",
            "Linh Tran",
            "Ludwig Schubert",
            "Magister Mugit",
            "Mark B Bahu",
            "Martin Price",
            "Mathias Jansson",
            "Matt Langford",
            "Matt Roveto",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Michael Faust",
            "Michael Hardel",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nero Li",
            "Nikita Lesnikov",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Patrick",
            "Peter Ehrnstrom",
            "RedAgent14",
            "rehmi post",
            "Richard Comish",
            "Ripta Pasay",
            "Rish Kundalia",
            "Robert Teed",
            "Roobie",
            "Ryan Williams",
            "Sebastian Garcia",
            "Solara570",
            "Stephan Arlinghaus",
            "Steven Siddals",
            "Stevie Metke",
            "Tal Einav",
            "Ted Suzman",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tom Fleming",
            "Valeriy Skobelev",
            "Xuanji Li",
            "Yavor Ivanov",
            "YinYangBalance.Asia",
            "Zach Cardwell",
            "Luc Ritchie",
            "Britt Selvitelle",
            "David Gow",
            "J",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Magnus Dahlström",
            "Randy C. Will",
            "Ryan Atallah",
            "Lukas -krtek.net- Novy",
            "Jordan Scales",
            "Ali Yahya",
            "Arthur Zey",
            "Atul S",
            "dave nicponski",
            "Evan Phillips",
            "Joseph Kelly",
            "Kaustuv DeBiswas",
            "Lambda AI Hardware",
            "Lukas Biewald",
            "Mark Heising",
            "Mike Coleman",
            "Nicholas Cahill",
            "Peter Mcinerney",
            "Quantopian",
            "Roy Larson",
            "Scott Walter, Ph.D.",
            "Yana Chernobilsky",
            "Yu Jun",
            "D. Sivakumar",
            "Richard Barthel",
            "Burt Humburg",
            "Matt Russell",
            "Scott Gray",
            "soekul",
            "Tihan Seale",
            "Juan Benet",
            "Vassili Philippov",
            "Kurt Dicus",
        ],
    }
