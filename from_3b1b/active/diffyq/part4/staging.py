from manimlib.imports import *
from active_projects.diffyq.part3.staging import FourierSeriesIllustraiton
from active_projects.diffyq.part2.wordy_scenes import WriteHeatEquationTemplate


class FourierName(Scene):
    def construct(self):
        name = TextMobject("Joseph Fourier")
        name.scale(1.5)
        self.add(name)


class FourierSeriesFormula(Scene):
    def construct(self):
        formula = TexMobject(
            "c_{n} = \\int_0^1 e^{-2\\pi i {n} {t}}f({t}){dt}",
            tex_to_color_map={
                "{n}": YELLOW,
                "{t}": PINK,
            }
        )

        self.play(Write(formula))
        self.wait()


class Zoom100Label(Scene):
    def construct(self):
        text = TextMobject("100x Zoom")
        text.scale(2)
        self.play(GrowFromCenter(text))
        self.wait()


class RelationToOtherVideos(Scene):
    CONFIG = {
        "camera_config": {
            "background_color": DARK_GREY,
        },
    }

    def construct(self):
        # Show three videos
        videos = self.get_video_thumbnails()
        brace = Brace(videos, UP)
        text = TextMobject("Heat equation")
        text.scale(2)
        text.next_to(brace, UP)

        self.play(
            LaggedStartMap(
                FadeInFrom, videos,
                lambda m: (m, LEFT),
                lag_ratio=0.4,
                run_time=2,
            ),
            GrowFromCenter(brace),
            FadeInFromDown(text),
        )
        self.wait()
        group = Group(text, brace, videos)

        # Show Fourier thinking
        fourier = ImageMobject("Joseph Fourier")
        fourier.set_height(4)
        fourier.to_edge(RIGHT)
        group.generate_target()
        group.target.to_edge(DOWN)
        fourier.align_to(group.target[0], DOWN)
        bubble = ThoughtBubble(
            direction=RIGHT,
            width=3,
            height=2,
            fill_opacity=0.5,
            stroke_color=WHITE,
        )
        bubble[-1].shift(0.25 * DOWN + 0.5 * LEFT)
        bubble[:-1].rotate(20 * DEGREES)
        for mob in bubble[:-1]:
            mob.rotate(-20 * DEGREES)
        bubble.move_to(
            fourier.get_center(), RIGHT
        )
        bubble.shift(LEFT)
        bubble.to_edge(UP, buff=SMALL_BUFF)

        self.play(
            MoveToTarget(group),
            FadeInFrom(fourier, LEFT)
        )
        self.play(Write(bubble, run_time=1))
        self.wait()

        # Discount first two
        first_two = videos[:2]
        first_two.generate_target()
        first_two.target.scale(0.5)
        first_two.target.to_corner(DL)
        new_brace = Brace(first_two.target, UP)

        self.play(
            # fourier.scale, 0.8,
            fourier.match_x, new_brace,
            fourier.to_edge, UP,
            MoveToTarget(first_two),
            Transform(brace, new_brace),
            text.scale, 0.7,
            text.next_to, new_brace, UP,
            FadeOutAndShift(bubble, LEFT),
        )
        self.play(
            videos[2].scale, 1.7,
            videos[2].to_corner, UR,
        )
        self.wait()

    #
    def get_video_thumbnails(self):
        thumbnails = Group(
            ImageMobject("diffyq_part2_thumbnail"),
            ImageMobject("diffyq_part3_thumbnail"),
            ImageMobject("diffyq_part4_thumbnail"),
        )
        for thumbnail in thumbnails:
            thumbnail.set_height(4)
            thumbnail.add(SurroundingRectangle(
                thumbnail,
                color=WHITE,
                stroke_width=2,
                buff=0
            ))
        thumbnails.arrange(RIGHT, buff=LARGE_BUFF)
        thumbnails.set_width(FRAME_WIDTH - 1)
        return thumbnails


class FourierGainsImmortality(Scene):
    CONFIG = {
        "mathematicians": [
            "Pythagoras",
            "Euclid",
            "Archimedes",
            "Fermat",
            "Newton",
            "Leibniz",
            "Johann_Bernoulli2",
            "Euler",
            "Joseph Fourier",
            "Gauss",
            "Riemann",
            "Cantor",
            "Noether",
            "Ramanujan",
            "Godel",
            "Turing",
        ]
    }

    def construct(self):
        fourier = ImageMobject("Joseph Fourier")
        fourier.set_height(5)
        fourier.to_edge(LEFT)
        name = TextMobject("Joseph Fourier")
        name.next_to(fourier, DOWN)

        immortals = self.get_immortals()
        immortals.remove(immortals.fourier)
        immortals.to_edge(RIGHT)

        self.add(fourier, name)
        self.play(LaggedStartMap(
            FadeIn, immortals,
            lag_ratio=0.1,
            run_time=2,
        ))
        self.play(
            TransformFromCopy(fourier, immortals.fourier)
        )
        self.wait()

    def get_immortals(self):
        images = Group(*[
            ImageMobject(name)
            for name in self.mathematicians
        ])
        for image in images:
            image.set_height(1)
        images.arrange_in_grid(n_rows=4)

        last_row = images[-4:]
        low_center = last_row.get_center()
        last_row.arrange(RIGHT, buff=0.4, center=False)
        last_row.move_to(low_center)

        frame = SurroundingRectangle(images)
        frame.set_color(WHITE)
        title = TextMobject("Immortals of Math")
        title.match_width(frame)
        title.next_to(frame, UP)

        result = Group(title, frame, *images)
        result.set_height(FRAME_HEIGHT - 1)
        result.to_edge(RIGHT)
        for image, name in zip(images, self.mathematicians):
            setattr(
                result,
                name.split(" ")[-1].lower(),
                image,
            )
        return result


class WhichWavesAreAvailable(Scene):
    CONFIG = {
        "axes_config": {
            "x_min": 0,
            "x_max": TAU,
            "y_min": -1.5,
            "y_max": 1.5,
            "x_axis_config": {
                "tick_frequency": PI / 2,
                "unit_size": 1,
                "include_tip": False,
            },
            "y_axis_config": {
                "unit_size": 1,
                "tick_frequency": 0.5,
                "include_tip": False,
            },
        },
        "n_axes": 5,
        "trig_func": np.cos,
        "trig_func_tex": "\\cos",
        "bc_words": "Restricted by\\\\boundary conditions",
    }

    def construct(self):
        self.setup_little_axes()
        self.show_cosine_waves()

    def setup_little_axes(self):
        axes_group = VGroup(*[
            Axes(**self.axes_config)
            for n in range(self.n_axes)
        ])
        axes_group.set_stroke(width=2)
        axes_group.arrange(DOWN, buff=1)
        axes_group.set_height(FRAME_HEIGHT - 1.25)
        axes_group.to_edge(RIGHT)
        axes_group.to_edge(UP, buff=MED_SMALL_BUFF)
        dots = TextMobject("\\vdots")
        dots.next_to(axes_group, DOWN)
        dots.shift_onto_screen()

        self.add(axes_group)
        self.add(dots)

        self.axes_group = axes_group

    def show_cosine_waves(self):
        axes_group = self.axes_group
        colors = [BLUE, GREEN, RED, YELLOW, PINK]

        graphs = VGroup()
        h_lines = VGroup()
        func_labels = VGroup()
        for k, axes, color in zip(it.count(1), axes_group, colors):
            L = axes.x_max
            graph = axes.get_graph(
                lambda x: self.trig_func(x * k * PI / L),
                color=color
            )
            graph.set_stroke(width=2)
            graphs.add(graph)

            func_label = TexMobject(
                self.trig_func_tex + "\\left(",
                str(k),
                "(\\pi / L)x\\right)",
                tex_to_color_map={
                    str(k): color,
                }
            )
            func_label.scale(0.7)
            func_label.next_to(axes, LEFT)
            func_labels.add(func_label)

            hl1 = DashedLine(LEFT, RIGHT)
            hl1.set_width(0.5)
            hl1.set_stroke(WHITE, 2)
            hl1.move_to(graph.get_start())
            hl2 = hl1.copy()
            hl2.move_to(graph.get_end())
            h_lines.add(hl1, hl2)

        words = TextMobject(self.bc_words)
        words.next_to(axes_group, LEFT)
        words.to_edge(UP)

        self.play(
            FadeIn(words),
            LaggedStartMap(
                ShowCreation, graphs,
            )
        )
        self.play(Write(h_lines))
        self.play(FadeOut(h_lines))
        self.wait()
        self.play(
            words.next_to, func_labels, LEFT,
            words.to_edge, UP,
            LaggedStartMap(
                FadeInFrom, func_labels,
                lambda m: (m, RIGHT)
            )
        )
        self.wait()


class AlternateBoundaryConditions(WhichWavesAreAvailable):
    CONFIG = {
        "trig_func": np.sin,
        "trig_func_tex": "\\sin",
        "bc_words": "Alternate\\\\boundary condition"
    }


class AskQuestionOfGraph(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature

        self.pi_creature_says(
            randy,
            "What sine waves\\\\are you made of?",
            target_mode="sassy",
        )
        self.wait(2)
        self.play(
            randy.change, "pondering",
            randy.bubble.get_right()
        )
        self.wait(2)


class CommentOnFouriersImmortality(FourierGainsImmortality):
    def construct(self):
        immortals = self.get_immortals()
        immortals.to_edge(LEFT)
        fourier = immortals.fourier
        name = TextMobject("Joseph", "Fourier")
        name.scale(1.5)
        name.move_to(FRAME_WIDTH * RIGHT / 4)
        name.to_edge(DOWN)

        fourier_things = VGroup(
            TextMobject("Fourier transform"),
            TextMobject("Fourier series"),
            TextMobject("Complex Fourier series"),
            TextMobject("Discrete Fourier transform"),
            TextMobject("Fractional Fourier transform"),
            TextMobject("Fast Fourier transform"),
            TextMobject("Quantum Fourier transform"),
            TextMobject("Fourier transform spectroscopy"),
            TexMobject("\\vdots"),
        )
        fourier_things.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=MED_LARGE_BUFF
        )
        fourier_things.to_corner(UL)
        fourier_things[-1].shift(RIGHT + 0.25 * UP)

        self.add(immortals)
        immortals.remove(immortals.fourier)
        self.play(
            fourier.set_height, 6,
            fourier.next_to, name, UP,
            FadeInFromDown(name),
        )
        self.play(FadeOut(immortals))
        self.wait(2)
        self.play(
            LaggedStartMap(
                FadeInFrom, fourier_things,
                lambda m: (m, UP),
                run_time=5,
                lag_ratio=0.3,
            )
        )
        self.wait()


class ShowInfiniteSum(FourierSeriesIllustraiton):
    CONFIG = {
        "n_range": range(1, 101, 2),
        "colors": [BLUE, GREEN, RED, YELLOW, PINK],
        "axes_config": {
            "y_max": 1.5,
            "y_min": -1.5,
            "y_axis_config": {
                "tick_frequency": 0.5,
                "unit_size": 1.0,
                "stroke_width": 2,
            },
            "x_axis_config": {
                "tick_frequency": 0.1,
                "stroke_width": 2,
            },
        },
    }

    def construct(self):
        self.add_equation()
        self.add_graphs()
        self.show_to_infinity()
        self.walk_through_constants()

        self.ask_about_infinite_sum()
        self.show_inf_sum_of_numbers()
        self.show_many_inputs_in_parallel()
        self.follow_single_inputs()

    def add_equation(self):
        inf_sum = self.get_infinite_sum()
        step_func_def = self.get_step_func_definition()
        step_func_def.next_to(inf_sum, RIGHT)
        equation = VGroup(inf_sum, step_func_def)
        equation.set_width(FRAME_WIDTH - 1)
        equation.center().to_edge(UP)

        self.add(equation)

        self.equation = equation
        self.inf_sum = inf_sum
        self.inf_sum = inf_sum
        self.step_func_def = step_func_def

    def add_graphs(self):
        aaa_group = self.get_axes_arrow_axes()
        aaa_group.next_to(self.equation, DOWN, buff=1.5)
        axes1, arrow, axes2 = aaa_group

        tfg = self.get_target_func_graph(axes2)
        tfg.set_color(WHITE)
        axes2.add(tfg)

        sine_graphs = self.get_sine_graphs(axes1)
        partial_sums = self.get_partial_sums(axes1, sine_graphs)
        partial_sums.set_stroke(width=0.5)
        partial_sums[-1].set_stroke(width=2)
        colors = self.colors
        partial_sums[len(colors):].set_color_by_gradient(*colors)

        self.add(aaa_group)
        self.add(partial_sums)

        self.partial_sums = partial_sums
        self.sine_graphs = sine_graphs
        self.aaa_group = aaa_group

    def show_to_infinity(self):
        dots = self.inf_sum.dots
        arrow = Vector(1.5 * RIGHT)
        arrow.next_to(
            dots, DOWN, MED_LARGE_BUFF,
            aligned_edge=RIGHT
        )
        words = TextMobject("Sum to $\\infty$")
        words.next_to(arrow, DOWN)

        self.play(
            FadeInFrom(words, LEFT),
            GrowArrow(arrow)
        )
        self.wait()

        self.inf_words = VGroup(arrow, words)

    def walk_through_constants(self):
        inf_sum = self.inf_sum
        terms = self.inf_sum.terms
        sine_graphs = self.sine_graphs
        partial_sums = self.partial_sums

        rects = VGroup(*[
            SurroundingRectangle(
                term,
                color=term[-1].get_color(),
                stroke_width=2
            )
            for term in terms
        ])
        dots_rect = SurroundingRectangle(inf_sum.dots)
        dots_rect.set_stroke(width=2)

        curr_rect = rects[0].copy()
        curr_partial_sum = partial_sums[0]
        curr_partial_sum.set_stroke(width=3)

        self.play(
            FadeOut(partial_sums[1:]),
            FadeIn(curr_rect),
            FadeIn(curr_partial_sum),
        )

        for sg, ps, rect in zip(sine_graphs[1:], partial_sums[1:], rects[1:]):
            self.play(
                FadeOut(curr_rect),
                FadeIn(rect),
                FadeIn(sg),
            )
            curr_rect.become(rect)
            self.remove(rect)
            self.add(curr_rect)
            ps.set_stroke(width=3)
            self.play(
                curr_partial_sum.set_stroke, {"width": 0.5},
                ReplacementTransform(sg, ps),
            )
            curr_partial_sum = ps
        self.play(
            Transform(curr_rect, dots_rect),
            curr_partial_sum.set_stroke, {"width": 0.5},
            LaggedStart(
                *[
                    UpdateFromAlphaFunc(
                        ps,
                        lambda m, a: m.set_stroke(
                            width=(3 * there_and_back(a) + 0.5 * a)
                        ),
                    )
                    for ps in partial_sums[4:]
                ],
                run_time=3,
                lag_ratio=0.2,
            ),
        )
        self.play(partial_sums[-1].set_stroke, {"width": 2})
        self.play(
            FadeOut(curr_rect),
            ShowCreationThenFadeAround(inf_sum.four_over_pi),
        )
        self.wait()

    def ask_about_infinite_sum(self):
        inf_words = self.inf_words
        randy = Randolph(mode="confused")
        randy.set_height(1.5)

        outline = inf_words[1].copy()
        outline.set_stroke(YELLOW, 1)
        outline.set_fill(opacity=0)

        question = TextMobject(
            "What$\\dots$\\\\ does this mean?"
        )
        question.scale(0.7)
        question.next_to(inf_words, LEFT)
        randy.next_to(question, DOWN, aligned_edge=RIGHT)

        self.play(FadeIn(question))
        self.play(FadeIn(randy))
        self.play(
            Blink(randy),
            ShowCreationThenFadeOut(outline)
        )
        self.wait()
        self.play(FadeOut(randy), FadeOut(question))

    def show_inf_sum_of_numbers(self):
        inf_sum = self.inf_sum
        graph_group = VGroup(
            self.aaa_group, self.partial_sums
        )

        number_line = NumberLine(
            x_min=0,
            x_max=1,
            tick_frequency=0.1,
            numbers_with_elongated_ticks=[0, 0.5, 1],
            unit_size=8,
            # line_to_number_buff=0.4,
        )
        number_line.set_stroke(LIGHT_GREY, 2)
        number_line.move_to(2 * DOWN)
        number_line.add_numbers(
            *np.arange(0, 1.5, 0.5),
            number_config={
                "num_decimal_places": 1,
            },
        )

        num_inf_sum = TexMobject(
            "{1 \\over 1}",
            "-{1 \\over 3}",
            "+{1 \\over 5}",
            "-{1 \\over 7}",
            "+{1 \\over 9}",
            "-{1 \\over 11}",
            "+\\cdots",
            "= {\\pi \\over 4}"
        )
        num_inf_sum.move_to(UP)

        self.play(
            FadeOutAndShift(graph_group, DOWN),
            FadeInFrom(number_line, UP),
            FadeOut(self.inf_words),
            *[
                TransformFromCopy(t1[-1:], t2)
                for t1, t2 in zip(
                    inf_sum.terms,
                    num_inf_sum,
                )
            ],
            TransformFromCopy(
                inf_sum.dots,
                num_inf_sum[-2],
            ),
            TransformFromCopy(
                inf_sum.dots,
                num_inf_sum[-4:-2]
            ),
            self.equation.set_opacity, 0.5,
        )
        self.play(Write(num_inf_sum[-1]))

        # Show sums
        terms = [
            u / n
            for u, n in zip(
                it.cycle([1, -1]),
                range(1, 1001, 2)
            )
        ]
        partial_sums = np.cumsum(terms)
        tip = ArrowTip(start_angle=-TAU / 4)
        value_tracker = ValueTracker(1)
        get_value = value_tracker.get_value
        tip.add_updater(
            lambda t: t.move_to(
                number_line.n2p(get_value()),
                DOWN,
            )
        )
        n_braces = 7
        braces = VGroup(*[
            Brace(num_inf_sum[:n], DOWN)
            for n in range(1, n_braces + 1)
        ])
        brace = braces[0].copy()
        decimal = DecimalNumber(
            0, num_decimal_places=6,
        )
        decimal.add_updater(lambda d: d.set_value(get_value()))
        decimal.add_updater(lambda d: d.next_to(tip, UP, SMALL_BUFF))

        term_count = VGroup(
            Integer(1), TextMobject("terms")
        )
        term_count_tracker = ValueTracker(1)
        term_count[0].set_color(YELLOW)
        term_count.add_updater(
            lambda m: m[0].set_value(term_count_tracker.get_value())
        )
        term_count.add_updater(lambda m: m.arrange(
            RIGHT, aligned_edge=DOWN
        ))
        term_count.add_updater(lambda m: m.next_to(brace, DOWN))

        pi_fourths_tip = ArrowTip(start_angle=90 * DEGREES)
        pi_fourths_tip.set_color(WHITE)
        pi_fourths_tip.move_to(
            number_line.n2p(PI / 4), UP,
        )
        pi_fourths_label = TexMobject(
            "{\\pi \\over 4} ="
        )
        pi_fourths_value = DecimalNumber(
            PI / 4, num_decimal_places=4
        )
        pi_fourths_value.scale(0.8)
        pi_fourths_value.next_to(pi_fourths_label, RIGHT, buff=0.2)
        pi_fourths_label.add(pi_fourths_value)
        # pi_fourths_label.scale(0.7)
        pi_fourths_label.next_to(
            pi_fourths_tip, DOWN, MED_SMALL_BUFF,
            aligned_edge=LEFT,
        )

        self.play(
            LaggedStartMap(
                FadeIn, VGroup(
                    brace, tip, decimal,
                    term_count,
                )
            ),
            FadeIn(pi_fourths_tip),
            FadeIn(pi_fourths_label),
        )
        for ps, new_brace in zip(partial_sums[1:], braces[1:]):
            term_count_tracker.increment_value(1)
            self.play(
                Transform(brace, new_brace),
                value_tracker.set_value, ps,
            )
            self.leave_mark(number_line, ps)
            self.wait()

        count = 0
        num_moving_values = n_braces + 8
        for ps in partial_sums[n_braces:num_moving_values]:
            value_tracker.set_value(ps)
            self.leave_mark(number_line, ps)
            count += 1
            term_count_tracker.increment_value(1)
            self.wait(0.5)
        decimal.remove_updater(decimal.updaters[-1])
        decimal.match_x(pi_fourths_tip)

        new_marks = VGroup(*[
            self.leave_mark(number_line, ps)
            for ps in partial_sums[num_moving_values:]
        ])
        number_line.remove(*new_marks)
        term_count_tracker.increment_value(1)
        self.play(
            UpdateFromAlphaFunc(
                value_tracker,
                lambda m, a: m.set_value(
                    partial_sums[integer_interpolate(
                        num_moving_values,
                        len(partial_sums) - 1,
                        a,
                    )[0]]
                ),
            ),
            ShowIncreasingSubsets(new_marks),
            term_count_tracker.set_value, len(partial_sums),
            run_time=10,
            rate_func=smooth,
        )
        self.play(LaggedStartMap(
            FadeOut, VGroup(
                num_inf_sum,
                brace,
                decimal,
                term_count,
                tip,
                number_line,
                new_marks,
                pi_fourths_tip,
                pi_fourths_label,
            ),
            lag_ratio=0.3,
        ))
        self.play(
            FadeInFromDown(graph_group),
            self.equation.set_opacity, 1,
        )

    def show_many_inputs_in_parallel(self):
        aaa_group = self.aaa_group
        axes1, arrow, axes2 = aaa_group
        partial_sums = self.partial_sums

        inputs = np.linspace(0, 1, 21)
        n_iterations = 100

        values = np.array([
            [
                (4 / PI) * (u / n) * np.cos(n * PI * x)
                for x in inputs
            ]
            for u, n in zip(
                it.cycle([1, -1]),
                range(1, 2 * n_iterations + 1, 2),
            )
        ])
        p_sums = np.apply_along_axis(np.cumsum, 0, values)

        dots = VGroup(*[Dot() for x in inputs])
        dots.scale(0.5)
        dots.set_color_by_gradient(BLUE, YELLOW)
        n_tracker = ValueTracker(0)

        def update_dots(dots):
            n = int(n_tracker.get_value())
            outputs = p_sums[n]
            for dot, x, y in zip(dots, inputs, outputs):
                dot.move_to(axes1.c2p(x, y))
        dots.add_updater(update_dots)

        lines = VGroup(*[
            self.get_dot_line(dot, axes1.x_axis)
            for dot in dots
        ])

        self.remove(*self.inf_words)
        self.play(
            FadeOut(partial_sums),
            FadeIn(dots),
            FadeIn(lines),
        )
        self.play(
            n_tracker.set_value, len(p_sums) - 1,
            run_time=5,
        )
        dots.clear_updaters()

        index = 4
        self.input_dot = dots[index]
        self.input_line = lines[index]
        self.partial_sum_values = p_sums[:, index]
        self.cosine_values = values[:, index]

        dots.remove(self.input_dot)
        lines.remove(self.input_line)
        self.add(self.input_line)
        self.add(self.input_dot)

        self.play(
            FadeOut(dots),
            FadeOut(lines),
        )

    def follow_single_inputs(self):
        aaa_group = self.aaa_group
        inf_sum = self.inf_sum
        axes1, arrow, axes2 = aaa_group
        x_axis = axes1.x_axis
        dot = self.input_dot
        partial_sums = self.partial_sums
        partial_sums.set_stroke(width=2)

        input_tracker = ValueTracker(
            x_axis.p2n(dot.get_center())
        )
        get_input = input_tracker.get_value

        input_label = TexMobject("x =", "0.2")
        input_decimal = DecimalNumber(get_input())
        input_decimal.replace(input_label[1])
        input_decimal.set_color(BLUE)
        input_label.remove(input_label[1])
        input_label.add(input_decimal)
        input_label.next_to(dot, UR, SMALL_BUFF)

        def get_brace_value_label(brace, u, n):
            result = DecimalNumber()
            result.scale(0.7)
            result.next_to(brace, DOWN, SMALL_BUFF)
            result.add_updater(lambda d: d.set_value(
                (u / n) * np.cos(PI * n * get_input())
            ))
            return result

        braces = VGroup(*[
            Brace(term, DOWN)
            for term in inf_sum.terms
        ])
        brace_value_labels = VGroup(*[
            get_brace_value_label(brace, u, n)
            for brace, u, n in zip(
                braces,
                it.cycle([1, -1]),
                it.count(1, 2),
            )
        ])
        bv_rects = VGroup(*[
            SurroundingRectangle(
                brace_value_labels[:n],
                color=BLUE,
                stroke_width=1,
            )
            for n in range(1, len(braces) + 1)
        ])

        bv_rect = bv_rects[0].copy()
        partial_sum = partial_sums[0].copy()

        dot.add_updater(
            lambda d: d.move_to(partial_sum.point_from_proportion(
                inverse_interpolate(
                    x_axis.x_min,
                    x_axis.x_max,
                    get_input(),
                )
            ))
        )

        n_waves_label = TextMobject(
            "Sum of", "10", "waves"
        )
        n_waves_label.next_to(axes1.c2p(0.5, 1), UR)
        n_tracker = ValueTracker(1)
        n_dec = Integer(1)
        n_dec.set_color(YELLOW)
        n_dec.move_to(n_waves_label[1])
        n_waves_label[1].set_opacity(0)
        n_waves_label.add(n_dec)
        n_dec.add_updater(lambda n: n.set_value(
            n_tracker.get_value()
        ))
        n_dec.add_updater(lambda m: m.move_to(
            n_waves_label[1]
        ))

        self.play(
            FadeInFrom(input_label, LEFT),
            dot.scale, 1.5,
        )
        self.wait()
        self.play(
            LaggedStartMap(GrowFromCenter, braces),
            LaggedStartMap(GrowFromCenter, brace_value_labels),
            *[
                TransformFromCopy(
                    input_label[0][0],
                    term[n][1],
                )
                for i, term in enumerate(inf_sum.terms)
                for n in [2 if i == 0 else 4]
            ]
        )
        self.wait()

        self.add(partial_sum, dot)
        dot.set_stroke(BLACK, 1, background=True)
        self.play(
            FadeOut(input_label),
            FadeIn(n_waves_label),
            FadeIn(bv_rect),
            FadeIn(partial_sum),
        )
        self.wait()

        ps_iter = iter(partial_sums[1:])

        def get_ps_anim():
            return AnimationGroup(
                Transform(partial_sum, next(ps_iter)),
                ApplyMethod(n_tracker.increment_value, 1),
            )

        for i in range(1, 4):
            self.play(
                Transform(bv_rect, bv_rects[i]),
                get_ps_anim(),
            )
            self.wait()

        self.play(
            FadeOut(bv_rect),
            get_ps_anim()
        )
        for x in range(3):
            self.play(get_ps_anim())
        self.play(
            input_tracker.set_value, 0.7,
        )
        for x in range(6):
            self.play(get_ps_anim())
        self.play(input_tracker.set_value, 0.5)
        for x in range(40):
            self.play(
                get_ps_anim(),
                run_time=0.5,
            )

    #
    def get_dot_line(self, dot, axis, line_class=Line):
        def get_line():
            p = dot.get_center()
            lp = axis.n2p(axis.p2n(p))
            return line_class(lp, p, stroke_width=1)
        return always_redraw(get_line)

    def leave_mark(self, number_line, value):
        tick = number_line.get_tick(value)
        tick.set_color(BLUE)
        number_line.add(tick)
        return tick

    def get_infinite_sum(self):
        colors = self.colors
        inf_sum = TexMobject(
            "{4 \\over \\pi}", "\\left(",
            "{\\cos\\left({1}\\pi x\\right) \\over {1}}",
            "-",
            "{\\cos\\left({3}\\pi x\\right) \\over {3}}",
            "+",
            "{\\cos\\left({5}\\pi x\\right) \\over {5}}",
            "-",
            "{\\cos\\left({7}\\pi x\\right) \\over {7}}",
            "+",
            "\\cdots",
            "\\right)",
            tex_to_color_map={
                "{1}": colors[0],
                "{-1 \\over 3}": colors[1],
                "{3}": colors[1],
                "{1 \\over 5}": colors[2],
                "{5}": colors[2],
                "{-1 \\over 7}": colors[3],
                "{7}": colors[3],
                "{1 \\over 9}": colors[4],
                "{9}": colors[4],
            }
        )
        inf_sum.get_parts_by_tex("-")[0].set_color(colors[1])
        inf_sum.get_parts_by_tex("-")[1].set_color(colors[3])
        inf_sum.get_parts_by_tex("+")[0].set_color(colors[2])

        inf_sum.terms = VGroup(
            inf_sum[2:6],
            inf_sum[6:12],
            inf_sum[12:18],
            inf_sum[18:24],
        )
        inf_sum.dots = inf_sum.get_part_by_tex("\\cdots")
        inf_sum.four_over_pi = inf_sum.get_part_by_tex(
            "{4 \\over \\pi}"
        )

        return inf_sum

    def get_step_func_definition(self):
        values = VGroup(*map(Integer, [1, 0, -1]))
        conditions = VGroup(*map(TextMobject, [
            "if $x < 0.5$",
            "if $x = 0.5$",
            "if $x > 0.5$",
        ]))
        values.arrange(DOWN, buff=MED_LARGE_BUFF)
        for condition, value in zip(conditions, values):
            condition.move_to(value)
            condition.align_to(conditions[0], LEFT)
        conditions.next_to(values, RIGHT, LARGE_BUFF)
        brace = Brace(values, LEFT)

        eq = TexMobject("=")
        eq.scale(1.5)
        eq.next_to(brace, LEFT)

        return VGroup(eq, brace, values, conditions)


class StepFunctionSolutionFormla(WriteHeatEquationTemplate):
    CONFIG = {
        "tex_mobject_config": {
            "tex_to_color_map": {
                "{1}": WHITE,  # BLUE,
                "{3}": WHITE,  # GREEN,
                "{5}": WHITE,  # RED,
                "{7}": WHITE,  # YELLOW,
            },
        },
    }

    def construct(self):
        formula = TexMobject(
            "T({x}, {t}) = ",
            "{4 \\over \\pi}",
            "\\left(",
            "{\\cos\\left({1}\\pi {x}\\right) \\over {1}}",
            "e^{-\\alpha {1}^2 {t} }",
            "-"
            "{\\cos\\left({3}\\pi {x}\\right) \\over {3}}",
            "e^{-\\alpha {3}^2 {t} }",
            "+",
            "{\\cos\\left({5}\\pi {x}\\right) \\over {5}}",
            "e^{-\\alpha {5}^2 {t} }",
            "- \\cdots",
            "\\right)",
            **self.tex_mobject_config,
        )

        formula.set_width(FRAME_WIDTH - 1)
        formula.to_edge(UP)

        self.play(FadeInFromDown(formula))
        self.wait()


class TechnicalNuances(Scene):
    def construct(self):
        title = TextMobject("Technical nuances not discussed")
        title.scale(1.5)
        title.set_color(YELLOW)
        line = DashedLine(title.get_left(), title.get_right())
        line.next_to(title, DOWN, SMALL_BUFF)
        line.set_stroke(LIGHT_GREY, 3)

        questions = VGroup(*map(TextMobject, [
            "Does the value at $0.5$ matter?",
            "What does it mean to solve a PDE with\\\\"
            "a discontinuous initial condition?",
            "Is the limit of a sequence of solutions\\\\"
            "also a solution?",
            "Do all functions have a Fourier series?",
        ]))

        self.play(
            Write(title),
            ShowCreation(line),
        )
        title.add(line)
        self.play(
            title.to_edge, UP,
        )

        last_question = VMobject()
        for question in questions:
            question.next_to(line, DOWN, MED_LARGE_BUFF)
            self.play(
                FadeInFromDown(question),
                FadeOutAndShift(last_question, UP)
            )
            self.wait(2)
            last_question = question


class ArrowAndCircle(Scene):
    def construct(self):
        circle = Circle(color=RED)
        circle.set_stroke(width=4)
        circle.set_height(0.25)

        arrow = Vector(DL)
        arrow.set_color(RED)
        arrow.next_to(circle, UR)
        self.play(ShowCreation(arrow))
        self.play(ShowCreation(circle))
        self.play(FadeOut(circle))
        self.wait()


class SineWaveResidue(Scene):
    def construct(self):
        f = 2
        wave = FunctionGraph(
            lambda x: np.cos(-0.1 * f * TAU * x),
            x_min=0,
            x_max=20,
            color=YELLOW,
        )
        wave.next_to(LEFT_SIDE, LEFT, buff=0)
        time = 10
        self.play(
            wave.shift, time * RIGHT,
            run_time=f * time,
            rate_func=linear,
        )


class AskAboutComplexNotVector(Scene):
    def construct(self):
        c_ex = DecimalNumber(
            complex(2, 1),
            num_decimal_places=0
        )
        i_part = c_ex[-1]
        v_ex = IntegerMatrix(
            [[2], [1]],
            bracket_h_buff=SMALL_BUFF,
            bracket_v_buff=SMALL_BUFF,
        )
        group = VGroup(v_ex, c_ex)
        group.scale(1.5)
        # group.arrange(RIGHT, buff=4)
        group.arrange(DOWN, buff=0.9)
        group.to_corner(UL, buff=0.2)

        q1, q2 = questions = VGroup(
            TextMobject("Why not this?").set_color(BLUE),
            TextMobject("Instead of this?").set_color(YELLOW),
        )
        questions.scale(1.5)
        for q, ex in zip(questions, group):
            ex.add_background_rectangle()
            q.add_background_rectangle()
            q.next_to(ex, RIGHT)

        plane = NumberPlane(axis_config={"unit_size": 2})
        vect = Vector([4, 2, 0])

        self.play(
            ShowCreation(plane, lag_ratio=0.1),
            FadeIn(vect),
        )
        for q, ex in zip(questions, group):
            self.play(
                FadeInFrom(q, LEFT),
                FadeIn(ex)
            )
        self.wait()
        self.play(ShowCreationThenFadeAround(i_part))
        self.wait()


class SwapIntegralAndSum(Scene):
    def construct(self):
        self.perform_swap()
        self.show_average_of_individual_terms()
        self.ask_about_c2()
        self.multiply_f_by_exp_neg_2()
        self.show_modified_averages()
        self.add_general_expression()

    def perform_swap(self):
        light_pink = self.light_pink = interpolate_color(
            PINK, WHITE, 0.25
        )
        tex_config = self.tex_config = {
            "tex_to_color_map": {
                "=": WHITE,
                "\\int_0^1": WHITE,
                "+": WHITE,
                "\\cdots": WHITE,
                "{t}": PINK,
                "{dt}": light_pink,
                "{-2}": YELLOW,
                "{\\cdot 1}": YELLOW,
                "{0}": YELLOW,
                "{1}": YELLOW,
                "{2}": YELLOW,
                "{n}": YELLOW,
            },
        }
        int_ft = TexMobject(
            "\\int_0^1 f({t}) {dt}",
            **tex_config
        )
        int_sum = TexMobject(
            """
            =
            \\int_0^1 \\left(
            \\cdots +
            c_{\\cdot 1}e^{{\\cdot 1} \\cdot 2\\pi i {t}} +
            c_{0}e^{{0} \\cdot 2\\pi i {t}} +
            c_{1}e^{{1} \\cdot 2\\pi i {t}} +
            c_{2}e^{{2} \\cdot 2\\pi i {t}} +
            \\cdots
            \\right){dt}
            """,
            **tex_config
        )
        sum_int = TexMobject(
            """
            = \\cdots +
            \\int_0^1
            c_{\\cdot 1}e^{{\\cdot 1} \\cdot 2\\pi i {t}}
            {dt} +
            \\int_0^1
            c_{0}e^{{0} \\cdot 2\\pi i {t}}
            {dt} +
            \\int_0^1
            c_{1}e^{{1} \\cdot 2\\pi i {t}}
            {dt} +
            \\int_0^1
            c_{2}e^{{2} \\cdot 2\\pi i {t}}
            {dt} +
            \\cdots
            """,
            **tex_config
        )

        self.fix_minuses(int_sum)
        self.fix_minuses(sum_int)

        group = VGroup(int_ft, int_sum, sum_int)
        group.arrange(
            DOWN, buff=MED_LARGE_BUFF,
            aligned_edge=LEFT
        )
        group.set_width(FRAME_WIDTH - 1)
        group.to_corner(UL)
        int_ft.align_to(int_sum[1], LEFT)
        int_ft.shift(0.2 * RIGHT)

        int_sum.exp_terms = self.get_exp_terms(int_sum)
        sum_int.exp_terms = self.get_exp_terms(sum_int)
        sum_int.int_terms = self.get_integral_terms(sum_int)

        breakdown_label = TextMobject(
            "Break this down"
        )
        arrow = Vector(LEFT)
        arrow.next_to(int_ft, RIGHT)
        breakdown_label.next_to(arrow, RIGHT)

        aos_label = TextMobject(
            "Average of a sum",
            tex_to_color_map={
                "Average": light_pink,
                "sum": YELLOW,
            }
        )
        soa_label = TextMobject(
            "Sum over averages",
            tex_to_color_map={
                "averages": light_pink,
                "Sum": YELLOW,
            }
        )
        aos_label.next_to(ORIGIN, RIGHT, buff=2)
        aos_label.to_edge(UP)
        soa_label.move_to(2.5 * DOWN)
        aos_arrow = Arrow(
            aos_label.get_corner(DL),
            int_sum.get_corner(TOP) + 2 * RIGHT,
            buff=0.3,
        )
        soa_arrow = Arrow(
            soa_label.get_top(),
            sum_int.get_bottom(),
            buff=0.3,
        )

        self.add(int_ft)
        self.play(
            FadeInFrom(breakdown_label, LEFT),
            GrowArrow(arrow),
        )
        self.wait()
        self.play(
            FadeOut(breakdown_label),
            FadeOut(arrow),
            FadeIn(int_sum.get_parts_by_tex("=")),
            FadeIn(int_sum.get_parts_by_tex("+")),
            FadeIn(int_sum.get_parts_by_tex("\\cdots")),
            FadeIn(int_sum.get_parts_by_tex("(")),
            FadeIn(int_sum.get_parts_by_tex(")")),
            *[
                TransformFromCopy(
                    int_ft.get_part_by_tex(tex),
                    int_sum.get_part_by_tex(tex),
                )
                for tex in ["\\int_0^1", "{dt}"]
            ]
        )
        self.play(LaggedStart(*[
            GrowFromPoint(
                term,
                int_ft.get_part_by_tex("{t}").get_center(),
            )
            for term in int_sum.exp_terms
        ]))
        self.wait()
        self.play(
            FadeIn(aos_label),
            GrowArrow(aos_arrow)
        )
        self.play(
            *[
                TransformFromCopy(
                    int_sum.get_parts_by_tex(tex),
                    sum_int.get_parts_by_tex(tex),
                    run_time=2,
                )
                for tex in ["\\cdots", "+"]
            ],
            TransformFromCopy(
                int_sum.exp_terms,
                sum_int.exp_terms,
                run_time=2,
            ),
            FadeIn(soa_label),
            GrowArrow(soa_arrow),
        )
        self.play(
            *[
                TransformFromCopy(
                    int_sum.get_part_by_tex("\\int_0^1"),
                    part,
                    run_time=2,
                )
                for part in sum_int.get_parts_by_tex(
                    "\\int_0^1"
                )
            ],
            FadeIn(sum_int.get_parts_by_tex("{dt}"))
        )
        self.wait()
        self.play(
            FadeOut(soa_arrow),
            soa_label.to_edge, DOWN,
        )

        self.int_sum = int_sum
        self.sum_int = sum_int
        self.int_ft = int_ft
        self.aos_label = aos_label
        self.aos_arrow = aos_arrow
        self.soa_label = soa_label
        self.soa_arrow = soa_arrow

    def show_average_of_individual_terms(self):
        sum_int = self.sum_int
        int_ft = self.int_ft

        braces = VGroup(*[
            Brace(term, DOWN, buff=SMALL_BUFF)
            for term in sum_int.int_terms
        ])
        self.play(LaggedStartMap(
            GrowFromCenter, braces
        ))

        self.show_individual_average(braces[0], -1)
        self.show_individual_average(braces[2], 1)
        self.show_individual_average(braces[3], 2)
        self.show_individual_average(braces[1], 0)

        eq = TexMobject("=")
        eq.next_to(int_ft, RIGHT)
        c0 = self.c0.copy()
        c0.generate_target()
        c0.target.next_to(eq, RIGHT)
        c0.target.shift(0.05 * DOWN)
        self.play(
            FadeIn(eq),
            MoveToTarget(c0, run_time=2)
        )
        self.wait()

        self.braces = braces
        self.eq_c0 = VGroup(eq, c0)

    def ask_about_c2(self):
        int_sum = self.int_sum
        sum_int = self.sum_int

        c2 = int_sum.exp_terms[-1][:2]
        c2_rect = SurroundingRectangle(c2, buff=0.05)
        c2_rect.set_stroke(WHITE, 2)
        c2_rect.stretch(1.5, 1, about_edge=DOWN)

        q_marks = TexMobject("???")
        q_marks.next_to(c2_rect, UP)

        last_diagram = self.all_average_diagrams[-2]
        last_int = sum_int.int_terms[-1]
        big_rect = SurroundingRectangle(
            VGroup(last_int, last_diagram)
        )
        big_rect.set_stroke(WHITE, 2)

        self.play(
            ShowCreation(c2_rect),
            FadeOut(self.aos_arrow),
            FadeInFromDown(q_marks),
        )
        self.play(ShowCreation(big_rect))
        self.wait(2)
        self.to_fade = VGroup(c2_rect, q_marks, big_rect)

    def multiply_f_by_exp_neg_2(self):
        int_ft = self.int_ft
        int_sum = self.int_sum
        sum_int = self.sum_int
        eq_c0 = self.eq_c0
        diagrams = self.all_average_diagrams
        diagrams.sort(lambda p: p[0])

        dt_part = int_ft.get_part_by_tex("{dt}")
        pre_dt_part = int_ft[:-1]
        new_exp = TexMobject(
            "e^{{-2} \\cdot 2\\pi i {t}}",
            **self.tex_config,
        )
        new_exp.next_to(pre_dt_part, RIGHT, SMALL_BUFF)
        new_exp.shift(0.05 * UP)
        something = TextMobject("(something)")
        something.replace(new_exp, dim_to_match=0)
        something.align_to(new_exp, DOWN)

        self.play(
            FadeOut(eq_c0),
            Write(something, run_time=1),
            dt_part.next_to, new_exp, RIGHT, SMALL_BUFF,
            dt_part.align_to, dt_part, DOWN,
        )
        self.wait()
        self.play(*[
            Rotating(
                diagram[2],
                radians=n * TAU,
                about_point=diagram[0].n2p(0),
                run_time=3,
                rate_func=lambda t: smooth(t, 1)
            )
            for n, diagram in zip(it.count(-3), diagrams)
        ])
        self.wait()
        self.play(
            FadeOutAndShift(something, UP),
            FadeInFrom(new_exp, DOWN),
        )
        self.play(FadeOut(self.to_fade))

        # Go through each term
        moving_exp = new_exp.copy()
        rect = SurroundingRectangle(moving_exp)
        rect.set_stroke(LIGHT_GREY, width=1)
        times = TexMobject("\\times")
        times.next_to(rect, LEFT, SMALL_BUFF)
        moving_exp.add(VGroup(rect, times))
        moving_exp[-1].set_opacity(0)
        moving_exp.save_state()
        moving_exp.generate_target()

        quads = zip(
            it.count(-3),
            int_sum.exp_terms,
            sum_int.exp_terms,
            diagrams,
        )
        for n, c_exp1, c_exp2, diagram in quads:
            exp1 = c_exp1[2:]
            exp2 = c_exp2[2:]
            moving_exp.target[-1][0].set_stroke(opacity=1)
            moving_exp.target[-1][1].set_fill(opacity=1)
            moving_exp.target.next_to(exp1, UP, SMALL_BUFF)
            if n < 0:
                n_str = "{\\cdot" + str(abs(n)) + "}"
            else:
                n_str = "{" + str(n) + "}"
            replacement1 = TexMobject(
                "e^{", n_str, "\\cdot 2\\pi i", "{t}",
                tex_to_color_map={
                    "{t}": PINK,
                    n_str: YELLOW,
                }
            )
            self.fix_minuses(replacement1)
            replacement1[1][0].shift(0.025 * LEFT)
            replacement1.match_height(exp1)
            replacement1.move_to(exp1, DL)
            replacement2 = replacement1.copy()
            replacement2.move_to(exp2, DL)
            self.play(MoveToTarget(moving_exp))
            self.play(
                TransformFromCopy(
                    moving_exp[1],
                    replacement1[1],
                ),
                FadeOutAndShift(exp1[1], DOWN),
                Transform(exp1[0], replacement1[0]),
                Transform(exp1[2:], replacement1[2:]),
            )
            self.play(
                TransformFromCopy(replacement1, replacement2),
                FadeOutAndShift(exp2, DOWN),
                FadeOut(diagram),
            )
        self.play(Restore(moving_exp))

    def show_modified_averages(self):
        braces = self.braces

        for brace, n in zip(braces, it.count(-3)):
            self.show_individual_average(brace, n, "c_2")

        int_ft = self.int_ft
        c2 = self.c0.copy()
        c2.generate_target()
        eq = TexMobject("=")
        eq.next_to(int_ft, RIGHT)
        c2.target.next_to(eq, RIGHT)
        c2.target.shift(0.05 * DOWN)
        self.play(
            FadeIn(eq),
            MoveToTarget(c2)
        )
        self.wait()

    def add_general_expression(self):
        expression = TexMobject(
            """
            c_{n} =
            \\int_0^1 f({t})
            e^{-{n} \\cdot 2\\pi i {t}}{dt}
            """,
            **self.tex_config,
        )
        rect = SurroundingRectangle(expression, buff=MED_SMALL_BUFF)
        rect.set_fill(DARK_GREY, 1)
        rect.set_stroke(WHITE, 3)
        group = VGroup(rect, expression)
        group.to_edge(UP, buff=SMALL_BUFF)
        group.to_edge(RIGHT, buff=LARGE_BUFF)

        self.play(
            FadeOut(self.aos_label),
            FadeIn(rect),
            FadeIn(expression)
        )
        self.wait()

    #
    def show_individual_average(self, brace, n, cn_tex=None):
        if not hasattr(self, "all_average_diagrams"):
            self.all_average_diagrams = VGroup()

        seed = brace.get_center()[0] + 1
        int_seed = np.array([seed]).astype("uint32")
        np.random.seed(int_seed)
        if n == 0:
            if cn_tex is None:
                cn_tex = "c_" + str(n)
            result = TexMobject(cn_tex)
            result[0][1].set_color(YELLOW)
            self.c0 = result
        else:
            result = TexMobject("0")
            result.set_color(self.light_pink)
        result.next_to(brace, DOWN, SMALL_BUFF)

        coord_max = 1.25
        plane = ComplexPlane(
            x_min=-coord_max,
            x_max=coord_max,
            y_min=-coord_max,
            y_max=coord_max,
            axis_config={
                "stroke_color": LIGHT_GREY,
                "stroke_width": 1,
                "unit_size": 0.75,
            },
            background_line_style={
                "stroke_color": LIGHT_GREY,
                "stroke_width": 1,
            },
        )
        plane.next_to(result, DOWN, SMALL_BUFF)

        vector = Arrow(
            plane.n2p(0),
            plane.n2p(
                (0.2 + 0.8 * np.random.random()) * np.exp(complex(
                    0, TAU * np.random.random()
                ))
            ),
            buff=0,
            color=WHITE,
        )
        circle = Circle()
        circle.set_stroke(BLUE, 2)
        circle.rotate(vector.get_angle())
        circle.set_width(2 * vector.get_length())
        circle.move_to(plane.n2p(0))

        dots = VGroup(*[
            Dot(
                circle.point_from_proportion(
                    (n * a) % 1
                ),
                radius=0.04,
                color=PINK,
                fill_opacity=0.75,
            )
            for a in np.arange(0, 1, 1 / 25)
        ])
        dot_center = center_of_mass([
            d.get_center() for d in dots
        ])

        self.play(
            FadeIn(plane),
            FadeIn(circle),
            FadeIn(vector),
        )
        self.play(
            Rotating(
                vector,
                radians=n * TAU,
                about_point=plane.n2p(0),
            ),
            ShowIncreasingSubsets(
                dots,
                int_func=np.ceil,
            ),
            rate_func=lambda t: smooth(t, 1),
            run_time=3,
        )
        dot_copies = dots.copy()
        self.play(*[
            ApplyMethod(dot.move_to, dot_center)
            for dot in dot_copies
        ])
        self.play(
            TransformFromCopy(dot_copies[0], result)
        )
        self.wait()

        self.all_average_diagrams.add(VGroup(
            plane, circle, vector,
            dots, dot_copies, result,
        ))

    #
    def fix_minuses(self, tex_mob):
        for mob in tex_mob.get_parts_by_tex("{\\cdot"):
            minus = TexMobject("-")
            minus.match_style(mob[0])
            minus.set_width(
                3 * mob[0].get_width(),
                stretch=True,
            )
            minus.move_to(mob, LEFT)
            mob.submobjects[0] = minus

    def get_terms_by_tex_bounds(self, tex_mob, tex1, tex2):
        c_parts = tex_mob.get_parts_by_tex(tex1)
        t_parts = tex_mob.get_parts_by_tex(tex2)
        result = VGroup()
        for p1, p2 in zip(c_parts, t_parts):
            i1 = tex_mob.index_of_part(p1)
            i2 = tex_mob.index_of_part(p2)
            result.add(tex_mob[i1:i2 + 1])
        return result

    def get_exp_terms(self, tex_mob):
        return self.get_terms_by_tex_bounds(
            tex_mob, "c_", "{t}"
        )

    def get_integral_terms(self, tex_mob):
        return self.get_terms_by_tex_bounds(
            tex_mob, "\\int", "{dt}"
        )


class FootnoteOnSwappingIntegralAndSum(Scene):
    def construct(self):
        words = TextMobject(
            """
            Typically in math, you have to be more\\\\
            careful swapping the order of sums like\\\\
            this when infinities are involved. Again,\\\\
            such questions are what real analysis \\\\
            is built for.
            """,
            alignment=""
        )

        self.add(words)
        self.wait()


class ShowRangeOfCnFormulas(Scene):
    def construct(self):
        formulas = VGroup(*[
            self.get_formula(n)
            for n in [-50, None, -1, 0, 1, None, 50]
        ])
        formulas.scale(0.7)
        formulas.arrange(
            DOWN,
            buff=MED_LARGE_BUFF,
            aligned_edge=LEFT
        )
        dots = formulas[1::4]
        dots.shift(MED_LARGE_BUFF * RIGHT)

        formulas.set_height(FRAME_HEIGHT - 0.5)
        formulas.to_edge(LEFT)

        self.play(LaggedStartMap(
            FadeInFrom, formulas,
            lambda m: (m, UP),
            lag_ratio=0.2,
            run_time=4,
        ))
        self.wait()

    def get_formula(self, n):
        if n is None:
            return TexMobject("\\vdots")
        light_pink = interpolate_color(PINK, WHITE, 0.25)
        n_str = "{" + str(n) + "}"
        neg_n_str = "{" + str(-n) + "}"
        expression = TexMobject(
            "c_" + n_str, "=",
            "\\int_0^1 f({t})",
            "e^{", neg_n_str,
            "\\cdot 2\\pi i {t}}{dt}",
            tex_to_color_map={
                "{t}": light_pink,
                "{dt}": light_pink,
                n_str: YELLOW,
                neg_n_str: YELLOW,
            }
        )
        return expression


class DescribeSVG(Scene):
    def construct(self):
        plane = ComplexPlane(
            axis_config={"unit_size": 2}
        )
        plane.add_coordinates()
        self.add(plane)

        svg_mob = SVGMobject("TrebleClef")
        path = svg_mob.family_members_with_points()[0]
        path.set_fill(opacity=0)
        path.set_stroke(YELLOW, 2)
        path.set_height(6)
        path.shift(0.5 * RIGHT)
        path_parts = CurvesAsSubmobjects(path)
        path_parts.set_stroke(GREEN, 3)
        self.add(path)

        dot = Dot()
        dot.set_color(PINK)
        ft_label = TexMobject("f(t) = ")
        ft_label.to_corner(UL)
        z_decimal = DecimalNumber(num_decimal_places=3)
        z_decimal.next_to(ft_label, RIGHT)
        z_decimal.add_updater(lambda m: m.set_value(
            plane.p2n(dot.get_center())
        ))
        z_decimal.set_color(interpolate_color(PINK, WHITE, 0.25))
        rect = BackgroundRectangle(VGroup(ft_label, z_decimal))

        brace = Brace(rect, DOWN)
        question = TextMobject("Where is this defined?")
        question.add_background_rectangle()
        question.next_to(brace, DOWN)

        answer = TextMobject("Read in some .svg")
        answer.add_background_rectangle()
        answer.next_to(question, DOWN, LARGE_BUFF)

        self.add(rect, ft_label, z_decimal)
        self.add(question, brace)
        self.play(UpdateFromAlphaFunc(
            dot,
            lambda d, a: d.move_to(path.point_from_proportion(a)),
            run_time=5,
            rate_func=lambda t: 0.3 * there_and_back(t)
        ))
        self.wait()
        self.play(FadeInFrom(answer, UP))
        self.play(
            FadeOut(path),
            FadeOut(dot),
            FadeIn(path_parts),
        )

        path_parts.generate_target()
        path_parts.save_state()
        path_parts.target.space_out_submobjects(1.3)
        for part in path_parts.target:
            part.shift(0.2 * part.get_center()[0] * RIGHT)
        path_parts.target.move_to(path_parts)
        self.play(
            MoveToTarget(path_parts)
        )

        indicators = self.get_bezier_point_indicators(path_parts)
        self.play(ShowCreation(
            indicators,
            lag_ratio=0.5,
            run_time=3,
        ))
        self.wait()
        self.play(
            FadeOut(indicators),
            path_parts.restore,
        )

    def get_bezier_point_indicators(self, path):
        dots = VGroup()
        lines = VGroup()
        for part in path.family_members_with_points():
            for tup in part.get_cubic_bezier_tuples():
                a1, h1, h2, a2 = tup
                dots.add(
                    Dot(a1),
                    Dot(a2),
                    Dot(h2, color=YELLOW),
                    Dot(h1, color=YELLOW),
                )
                lines.add(
                    Line(a1, h1),
                    Line(a2, h2),
                )
        for dot in dots:
            dot.set_width(0.05)
        lines.set_stroke(WHITE, 1)
        return VGroup(dots, lines)


class NumericalIntegration(Scene):
    CONFIG = {
        "tex_config": {
            "tex_to_color_map": {
                "{t}": LIGHT_PINK,
                "{dt}": LIGHT_PINK,
                "{n}": YELLOW,
                "{0.01}": WHITE,
            }
        }
    }

    def construct(self):
        self.add_title()
        self.add_integral()

    def add_title(self):
        title = TextMobject("Integrate numerically")
        title.scale(1.5)
        title.to_edge(UP)
        line = Line()
        line.set_width(title.get_width() + 1)
        line.next_to(title, DOWN)
        self.add(title, line)
        self.title = title

    def add_integral(self):
        integral = TexMobject(
            "c_{n}", "=", "\\int_0^1 f({t})"
            "e^{-{n} \\cdot 2\\pi i {t}}{dt}",
            **self.tex_config,
        )
        integral.to_edge(LEFT)

        sum_tex = TexMobject(
            " \\approx \\text{sum([} \\dots",
            "f({0.01}) e^{-{n} \\cdot 2\\pi i ({0.01})}({0.01})"
            "\\dots \\text{])}",
            **self.tex_config,
        )
        sum_tex.next_to(
            integral.get_part_by_tex("="), DOWN,
            buff=LARGE_BUFF,
            aligned_edge=LEFT,
        )

        group = VGroup(integral, sum_tex)
        group.next_to(self.title, DOWN, LARGE_BUFF)

        t_tracker = ValueTracker(0)
        decimal_templates = sum_tex.get_parts_by_tex("{0.01}")
        decimal_templates.set_color(LIGHT_PINK)
        decimals = VGroup(*[DecimalNumber() for x in range(2)])
        for d, dt in zip(decimals, decimal_templates):
            d.replace(dt)
            d.set_color(LIGHT_PINK)
            d.add_updater(lambda d: d.set_value(
                t_tracker.get_value()
            ))
            dt.set_opacity(0)

        delta_t_brace = Brace(decimal_templates[-1], UP, buff=SMALL_BUFF)
        delta_t = delta_t_brace.get_tex(
            "\\Delta t", buff=SMALL_BUFF
        )
        delta_t.set_color(PINK)

        input_line = UnitInterval(
            unit_size=10,
        )
        input_line.next_to(group, DOWN, LARGE_BUFF)
        input_line.add_numbers(0, 0.5, 1)
        dots = VGroup(*[
            Dot(
                input_line.n2p(t),
                color=PINK,
                radius=0.03,
            ).stretch(2, 1)
            for t in np.arange(0, 1, 0.01)
        ])

        self.add(integral)
        self.add(sum_tex)
        self.add(decimals)
        self.add(delta_t, delta_t_brace)
        self.add(input_line)

        time = 15
        self.play(
            t_tracker.set_value, 0.99,
            ShowIncreasingSubsets(dots),
            run_time=time,
            rate_func=lambda t: smooth(t, 1),
        )
        self.wait()

    def get_term(self, t, dt):
        pass


class StepFunctionIntegral(Scene):
    def construct(self):
        light_pink = interpolate_color(PINK, WHITE, 0.25)
        tex_config = {
            "tex_to_color_map": {
                "{t}": light_pink,
                "{dt}": light_pink,
                "{n}": YELLOW,
            }
        }
        cn_expression = TexMobject(
            """
            c_{n} =
            \\int_0^1 \\text{step}({t})
            e^{-{n}\\cdot 2\\pi i {t}} {dt}
            """,
            **tex_config
        )
        expansion = TexMobject(
            """
            =
            \\int_0^{0.5} 1 \\cdot e^{-{n}\\cdot 2\\pi i {t}} {dt} +
            \\int_{0.5}^1 -1 \\cdot e^{-{n}\\cdot 2\\pi i {t}} {dt}
            """,
            **tex_config
        )
        group = VGroup(cn_expression, expansion)
        group.arrange(RIGHT)
        group.set_width(FRAME_WIDTH - 1)
        group.to_corner(UL)

        words1 = TexMobject(
            "\\text{Challenge 1: Show that }"
            "c_{n} = {2 \\over {n} \\pi i}",
            "\\text{ for odd }", "{n}",
            "\\text{ and 0 otherwise}",
            **tex_config,
        )
        words2 = TexMobject(
            "\\text{Challenge 2: }",
            "&\\text{Using }",
            "\\sin(x) = (e^{ix} - e^{-ix}) / 2i,",
            "\\text{ show that}\\\\"
            "&\\text{step}({t}) = "
            "\\sum_{n = -\\infty}^{\\infty}",
            "c_{n} e^{{n} \\cdot 2\\pi i {t}}",
            "=",
            "\\sum_{n = 1, 3, 5, \\dots}",
            "{4 \\over {n} \\pi}",
            "\\sin\\left({n} \\cdot 2\\pi {t}\\right)",
            **tex_config,
        )
        words3 = TextMobject(
            "Challenge 3: How can you turn this into an "
            "expansion with \\\\ \\phantom{Challenge 3:} cosines? "
            "(Hint: Draw the sine waves over $[0.25, 0.75]$)",
            # "Challenge 3: By focusing on the range $[0.25, 0.75]$, relate\\\\"
            # "\\quad\\;\\, this to an expansion with cosines."
            alignment="",
        )

        all_words = VGroup(words1, words2, words3)
        all_words.arrange(DOWN, buff=LARGE_BUFF, aligned_edge=LEFT)
        all_words.scale(0.8)
        all_words.to_edge(DOWN)

        self.add(cn_expression)
        self.wait()
        self.play(FadeInFrom(expansion, LEFT))
        for words in all_words:
            self.play(FadeIn(words))
            self.wait()


class GeneralChallenge(Scene):
    def construct(self):
        title = TextMobject("More ambitious challenge")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        title.set_color(BLUE)
        line = Line()
        line.match_width(title)
        line.next_to(title, DOWN, SMALL_BUFF)
        self.add(title, line)

        light_pink = interpolate_color(PINK, WHITE, 0.25)
        tex_config = {
            "tex_to_color_map": {
                "{t}": light_pink,
                "{dt}": light_pink,
                # "{0}": YELLOW,
                "{n}": YELLOW,
            }
        }
        words1 = TextMobject(
            "In some texts, for a function $f$ on the input range $[0, 1]$,\\\\",
            "its Fourier series is presented like this:",
            alignment="",
        )
        formula1 = TexMobject(
            "f(t) = {a_{0} \\over 2} + "
            "\\sum_{n = 1}^{\\infty} \\big("
            "a_{n} \\cos\\left({n} \\cdot 2\\pi {t}\\right) + "
            "b_{n} \\sin\\left({n} \\cdot 2\\pi {t}\\right) \\big)",
            **tex_config
        )
        formula1[0][6].set_color(YELLOW)
        words2 = TextMobject("where")
        formula2 = TexMobject(
            "a_{n} = 2\\int_0^1 f({t})\\cos\\left({n} \\cdot 2\\pi {t}\\right) {dt}\\\\"
            # "\\text{ and }"
            "b_{n} = 2\\int_0^1 f({t})\\sin\\left({n} \\cdot 2\\pi {t}\\right) {dt}",
            **tex_config
        )
        words3 = TextMobject("How is this the same as what we just did?")

        prompt = VGroup(words1, formula1, words2, formula2, words3)
        prompt.arrange(DOWN, buff=MED_LARGE_BUFF)
        words2.align_to(words1, LEFT)
        words3.align_to(words1, LEFT)
        prompt.set_height(6)
        prompt.next_to(line, DOWN)

        self.add(prompt)
        self.wait()


class HintToGeneralChallenge(Scene):
    def construct(self):
        self.add(FullScreenFadeRectangle(
            fill_color=DARKER_GREY,
            fill_opacity=1,
        ))
        words1 = TextMobject("Hint: Try writing")
        formula1 = TexMobject(
            "c_{n} =",
            "{", "a_{n} \\over 2} +",
            "{", "b_{n} \\over 2} i",
            tex_to_color_map={
                "{n}": YELLOW,
            }
        )
        words2 = TextMobject("and")
        formula2 = TexMobject(
            "e^{i{x}} =",
            "\\cos\\left({x}\\right) +",
            "i\\sin\\left({x}\\right)",
            tex_to_color_map={
                "{x}": GREEN
            }
        )

        all_words = VGroup(
            words1, formula1,
            words2, formula2
        )
        all_words.arrange(DOWN, buff=LARGE_BUFF)

        self.add(all_words)


class OtherResources(Scene):
    def construct(self):
        thumbnails = Group(
            ImageMobject("MathologerFourier"),
            ImageMobject("CodingTrainFourier"),
        )
        names = VGroup(
            TextMobject("Mathologer"),
            TextMobject("The Coding Train"),
        )

        for thumbnail, name in zip(thumbnails, names):
            thumbnail.set_height(3)

        thumbnails.arrange(RIGHT, buff=LARGE_BUFF)
        thumbnails.set_width(FRAME_WIDTH - 1)

        for thumbnail, name in zip(thumbnails, names):
            name.scale(1.5)
            name.next_to(thumbnail, UP)
            thumbnail.add(name)
            self.play(
                FadeInFromDown(name),
                GrowFromCenter(thumbnail)
            )
            self.wait()

        url = TextMobject("www.jezzamon.com")
        url.scale(1.5)
        url.move_to(FRAME_WIDTH * RIGHT / 5)
        url.to_edge(UP)
        self.play(
            thumbnails.arrange, DOWN, {"buff": LARGE_BUFF},
            thumbnails.set_height, FRAME_HEIGHT - 2,
            thumbnails.to_edge, LEFT
        )
        self.play(FadeInFromDown(url))
        self.wait()


class ExponentialsMoreBroadly(Scene):
    def construct(self):
        self.write_fourier_series()
        self.pull_out_complex_exponent()
        self.show_matrix_exponent()

    def write_fourier_series(self):
        formula = TexMobject(
            "f({t}) = "
            "\\sum_{n = -\\infty}^\\infty",
            "c_{n}", "e^{{n} \\cdot 2\\pi i {t}}"
            "",
            tex_to_color_map={
                "{t}": LIGHT_PINK,
                "{n}": YELLOW
            }
        )
        formula[2][4].set_color(YELLOW)
        formula.scale(1.5)
        formula.to_edge(UP)
        formula.add_background_rectangle_to_submobjects()

        plane = ComplexPlane(
            axis_config={"unit_size": 2}
        )

        self.play(FadeInFromDown(formula))
        self.wait()
        self.add(plane, formula)
        self.play(
            formula.scale, 0.7,
            formula.to_corner, UL,
            ShowCreation(plane)
        )

        self.formula = formula
        self.plane = plane

    def pull_out_complex_exponent(self):
        formula = self.formula

        c_exp = TexMobject("e^{it}")
        c_exp[0][2].set_color(LIGHT_PINK)
        c_exp.set_stroke(BLACK, 3, background=True)
        c_exp.move_to(formula.get_part_by_tex("e^"), DL)
        c_exp.set_opacity(0)

        dot = Dot()
        circle = Circle(radius=2)
        circle.set_color(YELLOW)
        dot.add_updater(lambda d: d.move_to(circle.get_end()))

        self.play(
            c_exp.set_opacity, 1,
            c_exp.scale, 1.5,
            c_exp.next_to, dot, UR, SMALL_BUFF,
            GrowFromCenter(dot),
        )
        c_exp.add_updater(
            lambda m: m.next_to(dot, UR, SMALL_BUFF)
        )
        self.play(
            ShowCreation(circle),
            run_time=4,
        )
        self.wait()

        self.c_exp = c_exp
        self.circle = circle
        self.dot = dot

    def show_matrix_exponent(self):
        c_exp = self.c_exp
        formula = self.formula
        circle = self.circle
        dot = self.dot

        m_exp = TexMobject(
            "\\text{exp}\\left("
            "\\left[ \\begin{array}{cc}0 & -1 \\\\ 1 & 0 \\end{array} \\right]",
            "{t} \\right)",
            "=",
            "\\left[ \\begin{array}{cc}"
            "\\cos(t) & -\\sin(t) \\\\ \\sin(t) & \\cos(t)"
            "\\end{array} \\right]",
        )
        VGroup(
            m_exp[1][0],
            m_exp[3][5],
            m_exp[3][12],
            m_exp[3][18],
            m_exp[3][24],
        ).set_color(LIGHT_PINK)
        m_exp.to_corner(UL)
        m_exp.add_background_rectangle_to_submobjects()

        vector_field = VectorField(
            lambda p: rotate_vector(p, TAU / 4),
            max_magnitude=7,
            delta_x=0.5,
            delta_y=0.5,
            length_func=lambda norm: 0.35 * sigmoid(norm),
        )
        vector_field.sort(get_norm)

        self.play(
            FadeInFromDown(m_exp),
            FadeOutAndShift(formula, UP),
            FadeOut(c_exp)
        )
        self.add(vector_field, circle, dot, m_exp)
        self.play(
            ShowCreation(
                vector_field,
                lag_ratio=0.001,
            )
        )
        self.play(Rotating(circle, run_time=TAU))
        self.wait()


class Part4EndScreen(PatreonEndScreen):
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
            "Caleb Johnstone",
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
            "DeathByShrimp",
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
            "Jacob Harmon",
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
            "Josh Kinnear",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Kartik Cating-Subramanian",
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
            "Michael R Rader",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nero Li",
            "Nikita Lesnikov",
            "Omar Zrien",
            "Oscar Wu",
            "Owen Campbell-Moore",
            "Patrick Lucas",
            "Peter Ehrnstrom",
            "RedAgent14",
            "rehmi post",
            "Richard Comish",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roobie",
            "Ryan Williams",
            "Sebastian Garcia",
            "Solara570",
            "Steven Siddals",
            "Stevie Metke",
            "Tal Einav",
            "Ted Suzman",
            "Tianyu Ge",
            "Tom Fleming",
            "Tyler VanValkenburg",
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

