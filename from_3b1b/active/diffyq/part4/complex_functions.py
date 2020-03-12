from manimlib.imports import *


class GeneralizeToComplexFunctions(Scene):
    CONFIG = {
        "axes_config": {
            "x_min": 0,
            "x_max": 10,
            "x_axis_config": {
                "stroke_width": 2,
            },
            "y_min": -2.5,
            "y_max": 2.5,
            "y_axis_config": {
                "tick_frequency": 0.25,
                "unit_size": 1.5,
                "include_tip": False,
                "stroke_width": 2,
            },
        },
        "complex_plane_config": {
            "axis_config": {
                "unit_size": 2
            }
        },
    }

    def construct(self):
        self.show_cosine_wave()
        self.transition_to_complex_plane()
        self.add_rotating_vectors_making_cos()

    def show_cosine_wave(self):
        axes = Axes(**self.axes_config)
        axes.shift(2 * LEFT - axes.c2p(0, 0))
        y_axis = axes.y_axis
        y_labels = y_axis.get_number_mobjects(
            *range(-2, 3),
            number_config={"num_decimal_places": 1},
        )

        t_tracker = ValueTracker(0)
        t_tracker.add_updater(lambda t, dt: t.increment_value(dt))
        get_t = t_tracker.get_value

        def func(x):
            return 2 * np.cos(x)

        cos_x_max = 20
        cos_wave = axes.get_graph(func, x_max=cos_x_max)
        cos_wave.set_color(YELLOW)
        shown_cos_wave = cos_wave.copy()
        shown_cos_wave.add_updater(
            lambda m: m.pointwise_become_partial(
                cos_wave, 0,
                np.clip(get_t() / cos_x_max, 0, 1),
            ),
        )

        dot = Dot()
        dot.set_color(PINK)
        dot.add_updater(lambda d: d.move_to(
            y_axis.n2p(func(get_t())),
        ))

        h_line = always_redraw(lambda: Line(
            dot.get_right(),
            shown_cos_wave.get_end(),
            stroke_width=1,
        ))

        real_words = TextMobject(
            "Real number\\\\output"
        )
        real_words.to_edge(LEFT)
        real_words.shift(2 * UP)
        real_arrow = Arrow()
        real_arrow.add_updater(
            lambda m: m.put_start_and_end_on(
                real_words.get_corner(DR),
                dot.get_center(),
            ).scale(0.9),
        )

        self.add(t_tracker)
        self.add(axes)
        self.add(y_labels)
        self.add(shown_cos_wave)
        self.add(dot)
        self.add(h_line)

        self.wait(2)
        self.play(
            FadeInFrom(real_words, RIGHT),
            FadeIn(real_arrow),
        )
        self.wait(5)

        y_axis.generate_target()
        y_axis.target.rotate(-90 * DEGREES)
        y_axis.target.center()
        y_axis.target.scale(2 / 1.5)
        y_labels.generate_target()
        for label in y_labels.target:
            label.next_to(
                y_axis.target.n2p(label.get_value()),
                DOWN, MED_SMALL_BUFF,
            )
        self.play(
            FadeOut(shown_cos_wave),
            FadeOut(axes.x_axis),
            FadeOut(h_line),
        )
        self.play(
            MoveToTarget(y_axis),
            MoveToTarget(y_labels),
            real_words.shift, 2 * RIGHT + UP,
        )
        self.wait()

        self.y_axis = y_axis
        self.y_labels = y_labels
        self.real_words = real_words
        self.real_arrow = real_arrow
        self.dot = dot
        self.t_tracker = t_tracker

    def transition_to_complex_plane(self):
        y_axis = self.y_axis
        y_labels = self.y_labels

        plane = self.get_complex_plane()
        plane_words = plane.label

        self.add(plane, *self.get_mobjects())
        self.play(
            FadeOut(y_labels),
            FadeOut(y_axis),
            ShowCreation(plane),
        )
        self.play(Write(plane_words))
        self.wait()

        self.plane = plane
        self.plane_words = plane_words

    def add_rotating_vectors_making_cos(self):
        plane = self.plane
        real_words = self.real_words
        real_arrow = self.real_arrow
        t_tracker = self.t_tracker
        get_t = t_tracker.get_value

        v1 = Vector(2 * RIGHT)
        v2 = Vector(2 * RIGHT)
        v1.set_color(BLUE)
        v2.set_color(interpolate_color(GREY_BROWN, WHITE, 0.5))
        v1.add_updater(
            lambda v: v.set_angle(get_t())
        )
        v2.add_updater(
            lambda v: v.set_angle(-get_t())
        )
        v1.add_updater(
            lambda v: v.shift(plane.n2p(0) - v.get_start())
        )
        # Change?
        v2.add_updater(
            lambda v: v.shift(plane.n2p(0) - v.get_start())
        )

        ghost_v1 = v1.copy()
        ghost_v1.set_opacity(0.5)
        ghost_v1.add_updater(
            lambda v: v.shift(
                v2.get_end() - v.get_start()
            )
        )

        ghost_v2 = v2.copy()
        ghost_v2.set_opacity(0.5)
        ghost_v2.add_updater(
            lambda v: v.shift(
                v1.get_end() - v.get_start()
            )
        )

        circle = Circle(color=GREY_BROWN)
        circle.set_stroke(width=1)
        circle.set_width(2 * v1.get_length())
        circle.move_to(plane.n2p(0))

        formula = TexMobject(
            # "\\cos(x) ="
            # "{1 \\over 2}e^{ix} +"
            # "{1 \\over 2}e^{-ix}",
            "2\\cos(x) =",
            "e^{ix}", "+", "e^{-ix}",
            tex_to_color_map={
                "e^{ix}": v1.get_color(),
                "e^{-ix}": v2.get_color(),
            }
        )
        formula.next_to(ORIGIN, UP, buff=0.75)
        # formula.add_background_rectangle()
        formula.set_stroke(BLACK, 3, background=True)
        formula.to_edge(LEFT, buff=MED_SMALL_BUFF)
        formula_brace = Brace(formula[1:], UP)
        formula_words = formula_brace.get_text(
            "Sum of\\\\rotations"
        )
        formula_words.set_stroke(BLACK, 3, background=True)

        randy = Randolph()
        randy.to_corner(DL)
        randy.look_at(formula)

        self.play(
            FadeOut(real_words),
            FadeOut(real_arrow),
        )
        self.play(
            FadeIn(v1),
            FadeIn(v2),
            FadeIn(circle),
            FadeIn(ghost_v1),
            FadeIn(ghost_v2),
        )
        self.wait(3)
        self.play(FadeInFromDown(formula))
        self.play(
            GrowFromCenter(formula_brace),
            FadeIn(formula_words),
        )
        self.wait(2)
        self.play(FadeIn(randy))
        self.play(randy.change, "pleading")
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change, "confused")
        self.play(Blink(randy))
        self.wait()
        self.play(FadeOut(randy))
        self.wait(20)

    #
    def get_complex_plane(self):
        plane = ComplexPlane(**self.complex_plane_config)
        plane.add_coordinates()

        plane.label = TextMobject("Complex plane")
        plane.label.scale(1.5)
        plane.label.to_corner(UR, buff=MED_SMALL_BUFF)
        return plane


class ClarifyInputAndOutput(GeneralizeToComplexFunctions):
    CONFIG = {
        "input_space_rect_config": {
            "stroke_color": WHITE,
            "stroke_width": 1,
            "fill_color": DARKER_GREY,
            "fill_opacity": 1,
            "width": 6,
            "height": 2,
        },
    }

    def construct(self):
        self.setup_plane()
        self.setup_input_space()
        self.setup_input_trackers()

        self.describe_input()
        self.describe_output()

    def setup_plane(self):
        plane = self.get_complex_plane()
        plane.sublabel = TextMobject("(Output space)")
        plane.sublabel.add_background_rectangle()
        plane.sublabel.next_to(plane.label, DOWN)
        self.add(plane, plane.label)
        self.plane = plane

    def setup_input_space(self):
        rect = Rectangle(**self.input_space_rect_config)
        rect.to_corner(UL, buff=SMALL_BUFF)

        input_line = self.get_input_line(rect)
        input_words = TextMobject("Input space")
        input_words.next_to(
            rect.get_bottom(), UP,
            SMALL_BUFF,
        )

        self.add(rect)
        self.add(input_line)

        self.input_rect = rect
        self.input_line = input_line
        self.input_words = input_words

    def setup_input_trackers(self):
        plane = self.plane
        input_line = self.input_line
        input_tracker = ValueTracker(0)
        get_input = input_tracker.get_value

        input_dot = Dot()
        input_dot.set_color(PINK)
        f_always(
            input_dot.move_to,
            lambda: input_line.n2p(get_input())
        )

        input_decimal = DecimalNumber()
        input_decimal.scale(0.7)
        always(input_decimal.next_to, input_dot, UP)
        f_always(input_decimal.set_value, get_input)

        path = self.get_path()

        def get_output_point():
            return path.point_from_proportion(
                get_input()
            )

        output_dot = Dot()
        output_dot.match_style(input_dot)
        f_always(output_dot.move_to, get_output_point)

        output_vector = Vector()
        output_vector.set_color(WHITE)
        output_vector.add_updater(
            lambda v: v.put_start_and_end_on(
                plane.n2p(0),
                get_output_point()
            )
        )

        output_decimal = DecimalNumber()
        output_decimal.scale(0.7)
        always(output_decimal.next_to, output_dot, UR, SMALL_BUFF)
        f_always(
            output_decimal.set_value,
            lambda: plane.p2n(get_output_point()),
        )

        self.input_tracker = input_tracker
        self.input_dot = input_dot
        self.input_decimal = input_decimal
        self.path = path
        self.output_dot = output_dot
        self.output_vector = output_vector
        self.output_decimal = output_decimal

    def describe_input(self):
        input_tracker = self.input_tracker

        self.play(FadeInFrom(self.input_words, UP))
        self.play(
            FadeInFromLarge(self.input_dot),
            FadeIn(self.input_decimal),
        )
        for value in 1, 0:
            self.play(
                input_tracker.set_value, value,
                run_time=2
            )
        self.wait()

    def describe_output(self):
        path = self.path
        output_dot = self.output_dot
        output_decimal = self.output_decimal
        input_dot = self.input_dot
        input_tracker = self.input_tracker
        plane = self.plane
        real_line = plane.x_axis.copy()
        real_line.set_stroke(RED, 4)
        real_words = TextMobject("Real number line")
        real_words.next_to(ORIGIN, UP)
        real_words.to_edge(RIGHT)

        traced_path = TracedPath(output_dot.get_center)
        traced_path.match_style(path)

        self.play(
            ShowCreation(real_line),
            FadeInFrom(real_words, DOWN)
        )
        self.play(
            FadeOut(real_line),
            FadeOut(real_words),
        )
        self.play(
            FadeInFrom(plane.sublabel, UP)
        )
        self.play(
            FadeIn(output_decimal),
            TransformFromCopy(input_dot, output_dot),
        )

        kw = {
            "run_time": 10,
            "rate_func": lambda t: smooth(t, 1),
        }
        self.play(
            ApplyMethod(input_tracker.set_value, 1, **kw),
            ShowCreation(path.copy(), remover=True, **kw),
        )
        self.add(path)
        self.add(output_dot)
        self.wait()

        # Flatten to 1d
        real_function_word = TextMobject(
            "Real-valued function"
        )
        real_function_word.next_to(ORIGIN, DOWN, MED_LARGE_BUFF)
        path.generate_target()
        path.target.stretch(0, 1)
        path.target.move_to(plane.n2p(0))

        self.play(
            FadeIn(real_function_word),
            MoveToTarget(path),
        )
        input_tracker.set_value(0)
        self.play(
            input_tracker.set_value, 1,
            **kw
        )

    #
    def get_input_line(self, input_rect):
        input_line = UnitInterval()
        input_line.move_to(input_rect)
        input_line.shift(0.25 * UP)
        input_line.set_width(
            input_rect.get_width() - 1
        )
        input_line.add_numbers(0, 0.5, 1)
        return input_line

    def get_path(self):
        # mob = SVGMobject("BatmanLogo")
        mob = TexMobject("\\pi")
        path = mob.family_members_with_points()[0]
        path.set_height(3.5)
        path.move_to(2 * DOWN, DOWN)
        path.set_stroke(YELLOW, 2)
        path.set_fill(opacity=0)
        return path


class GraphForFlattenedPi(ClarifyInputAndOutput):
    CONFIG = {
        "camera_config": {"background_color": DARKER_GREY},
    }

    def construct(self):
        self.setup_plane()
        plane = self.plane
        self.remove(plane, plane.label)

        path = self.get_path()

        axes = Axes(
            x_min=0,
            x_max=1,
            x_axis_config={
                "unit_size": 7,
                "include_tip": False,
                "tick_frequency": 0.1,
            },
            y_min=-1.5,
            y_max=1.5,
            y_axis_config={
                "include_tip": False,
                "unit_size": 2.5,
                "tick_frequency": 0.5,
            },
        )
        axes.set_width(FRAME_WIDTH - 1)
        axes.set_height(FRAME_HEIGHT - 1, stretch=True)
        axes.center()

        axes.x_axis.add_numbers(
            0.5, 1.0,
            number_config={"num_decimal_places": 1},
        )
        axes.y_axis.add_numbers(
            -1.0, 1.0,
            number_config={"num_decimal_places": 1},
        )

        def func(t):
            return plane.x_axis.p2n(
                path.point_from_proportion(t)
            )

        graph = axes.get_graph(func)
        graph.set_color(PINK)

        v_line = always_redraw(lambda: Line(
            axes.x_axis.n2p(axes.x_axis.p2n(graph.get_end())),
            graph.get_end(),
            stroke_width=1,
        ))

        self.add(axes)
        self.add(v_line)

        kw = {
            "run_time": 10,
            "rate_func": lambda t: smooth(t, 1),
        }
        self.play(ShowCreation(graph, **kw))
        self.wait()


class SimpleComplexExponentExample(ClarifyInputAndOutput):
    CONFIG = {
        "input_space_rect_config": {
            "width": 14,
            "height": 1.5,
        },
        "input_line_config": {
            "unit_size": 0.5,
            "x_min": 0,
            "x_max": 25,
            "stroke_width": 2,
        },
        "input_numbers": range(0, 30, 5),
        "input_tex_args": ["t", "="],
    }

    def construct(self):
        self.setup_plane()
        self.setup_input_space()
        self.setup_input_trackers()
        self.setup_output_trackers()

        # Testing
        time = self.input_line.x_max
        self.play(
            self.input_tracker.set_value, time,
            run_time=time,
            rate_func=linear,
        )

    def setup_plane(self):
        plane = ComplexPlane()
        plane.scale(2)
        plane.add_coordinates()
        plane.shift(DOWN)
        self.plane = plane
        self.add(plane)

    def setup_input_trackers(self):
        input_line = self.input_line
        input_tracker = ValueTracker(0)
        get_input = input_tracker.get_value

        input_tip = ArrowTip(start_angle=-TAU / 4)
        input_tip.scale(0.5)
        input_tip.set_color(PINK)
        f_always(
            input_tip.move_to,
            lambda: input_line.n2p(get_input()),
            lambda: DOWN,
        )

        input_label = VGroup(
            TexMobject(*self.input_tex_args),
            DecimalNumber(),
        )
        input_label[0].set_color_by_tex("t", PINK)
        input_label.scale(0.7)
        input_label.add_updater(
            lambda m: m.arrange(RIGHT, buff=SMALL_BUFF)
        )
        input_label.add_updater(
            lambda m: m[1].set_value(get_input())
        )
        input_label.add_updater(
            lambda m: m.next_to(input_tip, UP, SMALL_BUFF)
        )

        self.input_tracker = input_tracker
        self.input_tip = input_tip
        self.input_label = input_label

        self.add(input_tip, input_label)

    def setup_output_trackers(self):
        plane = self.plane
        get_input = self.input_tracker.get_value

        def get_output():
            return np.exp(complex(0, get_input()))

        def get_output_point():
            return plane.n2p(get_output())

        output_label, static_output_label = [
            TexMobject(
                "e^{i t}" + s,
                tex_to_color_map={"t": PINK},
                background_stroke_width=3,
            )
            for s in ["", "\\approx"]
        ]
        output_label.scale(1.2)
        output_label.add_updater(
            lambda m: m.shift(
                -m.get_bottom() +
                get_output_point() +
                rotate_vector(
                    0.35 * RIGHT,
                    get_input(),
                )
            )
        )

        output_vector = Vector()
        output_vector.set_opacity(0.75)
        output_vector.add_updater(
            lambda m: m.put_start_and_end_on(
                plane.n2p(0), get_output_point(),
            )
        )

        t_max = 40
        full_output_path = ParametricFunction(
            lambda t: plane.n2p(np.exp(complex(0, t))),
            t_min=0,
            t_max=t_max
        )
        output_path = VMobject()
        output_path.set_stroke(YELLOW, 2)
        output_path.add_updater(
            lambda m: m.pointwise_become_partial(
                full_output_path,
                0, get_input() / t_max,
            )
        )

        static_output_label.next_to(plane.c2p(1, 1), UR)
        output_decimal = DecimalNumber(
            include_sign=True,
        )
        output_decimal.scale(0.8)
        output_decimal.set_stroke(BLACK, 3, background=True)
        output_decimal.add_updater(
            lambda m: m.set_value(get_output())
        )
        output_decimal.add_updater(
            lambda m: m.next_to(
                static_output_label,
                RIGHT, 2 * SMALL_BUFF,
                aligned_edge=DOWN,
            )
        )

        self.add(output_path)
        self.add(output_vector)
        self.add(output_label)
        self.add(static_output_label)
        self.add(BackgroundRectangle(output_decimal))
        self.add(output_decimal)

    #
    def get_input_line(self, input_rect):
        input_line = NumberLine(**self.input_line_config)
        input_line.move_to(input_rect)
        input_line.set_width(
            input_rect.get_width() - 1.5,
            stretch=True,
        )
        input_line.add_numbers(*self.input_numbers)
        return input_line


class TRangingFrom0To1(SimpleComplexExponentExample):
    CONFIG = {
        "input_space_rect_config": {
            "width": 6,
            "height": 2,
        },
    }

    def construct(self):
        self.setup_input_space()
        self.setup_input_trackers()

        self.play(
            self.input_tracker.set_value, 1,
            run_time=10,
            rate_func=linear
        )

    def get_input_line(self, rect):
        result = ClarifyInputAndOutput.get_input_line(self, rect)
        result.stretch(0.9, 0)
        result.set_stroke(width=2)
        for sm in result.get_family():
            if isinstance(sm, DecimalNumber):
                sm.stretch(1 / 0.9, 0)
                sm.set_stroke(width=0)
        return result
