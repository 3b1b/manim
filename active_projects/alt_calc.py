from big_ol_pile_of_manim_imports import *


class NumberlineTransformationScene(Scene):
    CONFIG = {
        "input_line_center": 2 * UP,
        "output_line_center": 2 * DOWN,
        "number_line_config": {
            "include_numbers": True,
            "x_min": -3.5,
            "x_max": 3.5,
            "unit_size": 2,
        },
        # These would override number_line_config
        "input_line_config": {
            "color": BLUE,
        },
        "output_line_config": {},
        "num_inserted_number_line_anchors": 20,
    }

    def setup(self):
        self.setup_number_lines()
        self.setup_titles()

    def setup_number_lines(self):
        number_lines = self.number_lines = VGroup()
        added_configs = (self.input_line_config, self.output_line_config)
        centers = (self.input_line_center, self.output_line_center)
        for added_config, center in zip(added_configs, centers):
            full_config = dict(self.number_line_config)
            full_config.update(added_config)
            number_line = NumberLine(**full_config)
            number_line.main_line.insert_n_anchor_points(
                self.num_inserted_number_line_anchors
            )
            number_line.move_to(center)
            number_lines.add(number_line)
        self.input_line, self.output_line = number_lines

        self.add(number_lines)

    def setup_titles(self):
        input_title, output_title = self.titles = VGroup(*[
            TextMobject()
            for word in "Inputs", "Outputs"
        ])
        for title, line in zip(self.titles, self.number_lines):
            title.next_to(line, UP)
            title.shift_onto_screen()

        self.add(self.titles)

    def get_line_mapping_animation(self, func, run_time=3, path_arc=30 * DEGREES):
        input_line, output_line = self.number_lines
        input_line_copy = input_line.deepcopy()
        input_line_copy.remove(input_line_copy.numbers)
        input_line_copy.set_stroke(width=2)

        def point_func(point):
            input_number = input_line.point_to_number(point)
            output_number = func(input_number)
            return output_line.number_to_point(output_number)

        return ApplyPointwiseFunction(
            point_func, input_line_copy,
            run_time=run_time,
            path_arc=path_arc,
        )


class ExampleNumberlineTransformationScene(NumberlineTransformationScene):
    def construct(self):
        func = lambda x: x**2
        anim = self.get_line_mapping_animation(func)
        self.play(anim)
        self.wait()

# Scenes


class WriteOpeningWords(Scene):
    def construct(self):
        raw_string1 = "Dear calculus student,"
        raw_string2 = "You're about to go through your first course. Like " + \
                      "any new topic, it will take some hard work to understand,"
        words1, words2 = [
            TextMobject("\\Large", *rs.split(" "))
            for rs in raw_string1, raw_string2
        ]
        words1.next_to(words2, UP, aligned_edge=LEFT, buff=LARGE_BUFF)
        words = VGroup(*it.chain(words1, words2))
        words.scale_to_fit_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        words.to_edge(UP)

        letter_wait = 0.05
        word_wait = 2 * letter_wait
        comma_wait = 5 * letter_wait
        for word in words:
            self.play(LaggedStart(
                FadeIn, word,
                run_time=len(word) * letter_wait,
                lag_ratio=1.5 / len(word)
            ))
            self.wait(word_wait)
            if word.get_tex_string()[-1] == ",":
                self.wait(comma_wait)


class StartingCalc101(PiCreatureScene):
    CONFIG = {
    }

    def construct(self):
        randy = self.pi_creature
        deriv_equation = TexMobject(
            "\\frac{df}{dx}(x) = \\lim_{\\Delta x \\to \\infty}" +
            "{f(x + \\Delta x) - f(x) \\over \\Delta x}",
            tex_to_color_map={"\\Delta x": BLUE}
        )
        self.add(deriv_equation)
        equations = VGroup(deriv_equation)

        title = TextMobject("Calculus 101")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT)
        h_line.scale_to_fit_width(FRAME_WIDTH - LARGE_BUFF)
        h_line.next_to(title, DOWN)

        self.add(title, h_line)
        self.play(randy.change, "erm", title)
        self.wait()


class StandardDerivativeVisual(GraphScene):
    CONFIG = {
        # "y_axis_label": "$f(x)$",
        "y_max": 8,
        "y_axis_height": 5,
    }

    def construct(self):
        self.add_title()
        self.show_function_graph()
        self.show_slope_of_graph()
        self.encourage_not_to_think_of_slope_as_definition()
        self.show_sensitivity()

    def add_title(self):
        title = self.title = TextMobject("Standard derivative visual")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT)
        h_line.scale_to_fit_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        h_line.next_to(title, DOWN)

        self.add(title, h_line)

    def show_function_graph(self):
        self.setup_axes()

        def func(x):
            x -= 5
            return 0.1 * (x + 3) * (x - 3) * x + 3
        graph = self.get_graph(func)
        graph_label = self.get_graph_label(graph, x_val=9.5)

        input_tracker = ValueTracker(4)

        def get_x_value():
            return input_tracker.get_value()

        def get_y_value():
            return graph.underlying_function(get_x_value())

        def get_x_point():
            return self.coords_to_point(get_x_value(), 0)

        def get_y_point():
            return self.coords_to_point(0, get_y_value())

        def get_graph_point():
            return self.coords_to_point(get_x_value(), get_y_value())

        def get_v_line():
            return DashedLine(get_x_point(), get_graph_point(), stroke_width=2)

        def get_h_line():
            return DashedLine(get_graph_point(), get_y_point(), stroke_width=2)

        input_triangle = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle, output_triangle:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)

        input_triangle_update = ContinualUpdateFromFunc(
            input_triangle, lambda m: m.move_to(get_x_point(), UP)
        )
        output_triangle_update = ContinualUpdateFromFunc(
            output_triangle, lambda m: m.move_to(get_y_point(), RIGHT)
        )

        x_label = TexMobject("x")
        x_label_update = ContinualUpdateFromFunc(
            x_label, lambda m: m.next_to(input_triangle, DOWN, SMALL_BUFF)
        )

        output_label = TexMobject("f(x)")
        output_label_update = ContinualUpdateFromFunc(
            output_label, lambda m: m.next_to(
                output_triangle, LEFT, SMALL_BUFF)
        )

        v_line = get_v_line()
        v_line_update = ContinualUpdateFromFunc(
            v_line, lambda vl: Transform(vl, get_v_line()).update(1)
        )

        h_line = get_h_line()
        h_line_update = ContinualUpdateFromFunc(
            h_line, lambda hl: Transform(hl, get_h_line()).update(1)
        )

        graph_dot = Dot(color=YELLOW)
        graph_dot_update = ContinualUpdateFromFunc(
            graph_dot, lambda m: m.move_to(get_graph_point())
        )

        self.play(
            ShowCreation(graph),
            Write(graph_label),
        )
        self.play(
            DrawBorderThenFill(input_triangle, run_time=1),
            Write(x_label),
            ShowCreation(v_line),
            GrowFromCenter(graph_dot),
        )
        self.add_foreground_mobject(graph_dot)
        self.play(
            ShowCreation(h_line),
            Write(output_label),
            DrawBorderThenFill(output_triangle, run_time=1)
        )
        self.add(
            input_triangle_update,
            x_label_update,
            graph_dot_update,
            v_line_update,
            h_line_update,
            output_triangle_update,
            output_label_update,
        )
        self.play(
            input_tracker.set_value, 8,
            run_time=6,
            rate_func=there_and_back
        )

        self.input_tracker = input_tracker
        self.graph = graph

    def show_slope_of_graph(self):
        input_tracker = self.input_tracker
        deriv_input_tracker = ValueTracker(input_tracker.get_value())

        # Slope line
        def get_slope_line():
            return self.get_secant_slope_group(
                x=deriv_input_tracker.get_value(),
                graph=self.graph,
                dx=0.01,
                secant_line_length=4
            ).secant_line

        slope_line = get_slope_line()
        slope_line_update = ContinualUpdateFromFunc(
            slope_line, lambda sg: Transform(sg, get_slope_line()).update(1)
        )

        def position_deriv_label(deriv_label):
            deriv_label.next_to(slope_line, UP)
            return deriv_label
        deriv_label = TexMobject(
            "\\frac{df}{dx}(x) =", "\\text{Slope}", "="
        )
        deriv_label.get_part_by_tex("Slope").match_color(slope_line)
        deriv_label_update = ContinualUpdateFromFunc(
            deriv_label, position_deriv_label
        )

        slope_decimal = DecimalNumber(slope_line.get_slope())
        slope_decimal.match_color(slope_line)
        slope_decimal_update = ContinualChangingDecimal(
            slope_decimal, lambda dt: slope_line.get_slope(),
            position_update_func=lambda m: m.next_to(
                deriv_label, RIGHT, SMALL_BUFF
            ).shift(0.2 * SMALL_BUFF * DOWN)
        )

        self.play(
            ShowCreation(slope_line),
            Write(deriv_label),
            Write(slope_decimal),
            run_time=1
        )
        self.wait()
        self.add(
            slope_line_update,
            # deriv_label_update,
            slope_decimal_update,
        )
        for x in 9, 2, 4:
            self.play(
                input_tracker.set_value, x,
                deriv_input_tracker.set_value, x,
                run_time=3
            )
            self.wait()

        self.deriv_input_tracker = deriv_input_tracker

    def encourage_not_to_think_of_slope_as_definition(self):
        morty = Mortimer(height=2)
        morty.to_corner(DR)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, "Don't think of \\\\ this as the definition",
            bubble_kwargs={"height": 2, "width": 4}
        ))
        self.play(Blink(morty))
        self.wait()
        self.play(
            RemovePiCreatureBubble(morty),
            UpdateFromAlphaFunc(
                morty, lambda m, a: m.set_fill(opacity=1 - a),
                remover=True
            )
        )

    def show_sensitivity(self):
        input_tracker = self.input_tracker
        deriv_input_tracker = self.deriv_input_tracker

        self.wiggle_input()
        for x in 9, 7, 2:
            self.play(
                input_tracker.set_value, x,
                deriv_input_tracker.set_value, x,
                run_time=3
            )
            self.wiggle_input()

    ###
    def wiggle_input(self, dx=0.5, run_time=3):
        input_tracker = self.input_tracker

        x = input_tracker.get_value()
        x_min = x - dx
        x_max = x + dx
        y, y_min, y_max = map(
            self.graph.underlying_function,
            [x, x_min, x_max]
        )
        x_line = Line(
            self.coords_to_point(x_min, 0),
            self.coords_to_point(x_max, 0),
        )
        y_line = Line(
            self.coords_to_point(0, y_min),
            self.coords_to_point(0, y_max),
        )

        x_rect, y_rect = rects = VGroup(Rectangle(), Rectangle())
        rects.set_stroke(width=0)
        rects.set_fill(YELLOW, 0.5)
        x_rect.match_width(x_line)
        x_rect.stretch_to_fit_height(0.25)
        x_rect.move_to(x_line)
        y_rect.match_height(y_line)
        y_rect.stretch_to_fit_width(0.25)
        y_rect.move_to(y_line)

        self.play(
            ApplyMethod(
                input_tracker.set_value, input_tracker.get_value() + dx,
                rate_func=lambda t: wiggle(t, 6)
            ),
            FadeIn(
                rects,
                rate_func=squish_rate_func(smooth, 0, 0.33),
                remover=True,
            ),
            run_time=run_time,
        )
        self.play(FadeOut(rects))


class EoCWrapper(Scene):
    def construct(self):
        title = Title("Essence of calculus")
        self.play(Write(title))
        self.wait()
