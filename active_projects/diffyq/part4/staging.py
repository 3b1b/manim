from manimlib.imports import *
from active_projects.diffyq.part3.staging import FourierSeriesIllustraiton
from active_projects.diffyq.part2.wordy_scenes import WriteHeatEquationTemplate


class FourierSeriesFormula(Scene):
    def construct(self):
        formula = TexMobject(
            "c_{n} = \\int_0^1 e^{-2\\pi i {n} {t}}f({t}){dt}",
            tex_to_color_map={
                "{n}": RED,
                "{t}": YELLOW,
            }
        )

        self.play(Write(formula))
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
        bubble.move_tip_to(
            fourier.get_corner(UL) + DOWN
        )
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

    def perform_swap(self):
        tex_config = {
            "tex_to_color_map": {
                "=": WHITE,
                "\\int_0^1": WHITE,
                "{t}": PINK,
                "{dt}": interpolate_color(PINK, WHITE, 0.25),
                "{\\cdot 1}": YELLOW,
                "{0}": YELLOW,
                "{1}": YELLOW,
                "{2}": YELLOW,
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

        # top_line = VGroup(int_ft, int_sum)
        # top_line.arrange(RIGHT, buff=SMALL_BUFF)
        # top_line.set_width(FRAME_WIDTH - 1)
        # top_line.to_corner(UL)


        group = VGroup(int_ft, int_sum, sum_int)
        group.arrange(
            DOWN, buff=MED_LARGE_BUFF,
            aligned_edge=LEFT
        )
        group.set_width(FRAME_WIDTH - 1)
        group.to_corner(UL)
        int_ft.align_to(int_sum[1], LEFT)
        int_ft.shift(0.2 * RIGHT)

        self.add(int_ft)
        self.add(int_sum)
        self.add(sum_int)

    def show_average_of_individual_terms(self):
        pass

    #
    def fix_minuses(self, tex_mob):
        for mob in tex_mob.get_parts_by_tex("{\\cdot 1}"):
            minus = TexMobject("-")
            minus.match_style(mob[0])
            minus.set_width(
                3 * mob[0].get_width(),
                stretch=True,
            )
            minus.move_to(mob, LEFT)
            mob.submobjects[0] = minus


class FootnoteOnSwappingIntegralAndSum(Scene):
    def construct(self):
        pass
