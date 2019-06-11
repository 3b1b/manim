import scipy
import fractions

from manimlib.imports import *

class Chapter9OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "We often hear that mathematics consists mainly of", 
            "proving theorems.",
            "Is a writer's job mainly that of\\\\",
            "writing sentences?"
        ],
        "highlighted_quote_terms" : {
            "proving theorems." : MAROON_B,
            "writing sentences?" : MAROON_B,
        },
        "author" : "Gian-Carlo Rota",
    }

class AverageOfContinuousVariable(GraphScene):
    CONFIG = {
        "bounds" : [1, 7],
        "bound_colors" : [RED, GREEN],
    }
    def construct(self):
        self.setup_axes()
        graph = self.get_graph(
            lambda x : 0.1*x*(x-3)*(x-6) + 4
        )
        graph_label = self.get_graph_label(graph, "f(x)")
        boundary_lines = self.get_vertical_lines_to_graph(
            graph, *self.bounds, num_lines = 2,
            line_class = DashedLine
        )
        for line, color in zip(boundary_lines, self.bound_colors):
            line.set_color(color)
        v_line = self.get_vertical_line_to_graph(
            self.bounds[0], graph, color = YELLOW,
        )

        question = TextMobject(
            "What is the average \\\\ value of $f(x)$?"
        )
        question.next_to(boundary_lines, UP)

        self.play(ShowCreation(graph), Write(graph_label))
        self.play(ShowCreation(boundary_lines))
        self.play(FadeIn(
            question,
            run_time = 2,
            lag_ratio = 0.5,
        ))
        self.play(ShowCreation(v_line))
        for bound in reversed(self.bounds):
            self.play(self.get_v_line_change_anim(
                v_line, graph, bound, 
                run_time = 3,
            ))
            self.wait()
        self.wait()

    def get_v_line_change_anim(self, v_line, graph, target_x, **kwargs):
        start_x = self.x_axis.point_to_number(v_line.get_bottom())
        def update(v_line, alpha):
            new_x = interpolate(start_x, target_x, alpha)
            v_line.put_start_and_end_on(
                self.coords_to_point(new_x, 0),
                self.input_to_graph_point(new_x, graph)
            )
            return v_line
        return UpdateFromAlphaFunc(v_line, update, **kwargs)

class ThisVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        this_video = series[8]

        self.play(FadeIn(series, lag_ratio = 0.5))
        self.teacher_says(
            "A new view of \\\\ the fundamental theorem",
            bubble_kwargs = {"height" : 3},
            added_anims = [
                this_video.shift, this_video.get_height()*DOWN/2,
                this_video.set_color, YELLOW,
            ]
        )
        self.change_student_modes(*["pondering"]*3)
        self.wait(3)

class AverageOfSineStart(AverageOfContinuousVariable):
    CONFIG = {
        "y_min" : -2, 
        "y_max" : 2,
        "x_min" : -1,
        "x_max" : 2.5*np.pi,
        "x_leftmost_tick" : 0,
        "x_tick_frequency" : np.pi/4,
        "x_axis_width" : 12,
        "graph_origin" : 5*LEFT,
        "x_label_scale_val" : 0.75,
        "func" : np.sin,
        "graph_color" : BLUE,
        "bounds" : [0, np.pi],
    }
    def construct(self):
        self.setup_axes()
        self.add_graph()
        self.ask_about_average()

    def add_graph(self, run_time = 1):
        graph = self.get_graph(self.func, color = self.graph_color)
        graph_label = self.get_graph_label(
            graph, "\\sin(x)",
            direction = UP
        )
        self.play(
            ShowCreation(graph),
            Write(graph_label),
            run_time = run_time
        )

        self.graph = graph
        self.graph_label = graph_label

    def ask_about_average(self):
        half_period_graph = self.get_graph_portion_between_bounds()
        question = TextMobject("Average height?")
        question.to_edge(UP)
        arrow = Arrow(question.get_bottom(), half_period_graph.get_top())
        midpoint = np.mean(self.bounds)
        v_line = self.get_vertical_line_to_graph(
            midpoint, self.graph,
            line_class = DashedLine,
            color = WHITE
        )

        self.play(FadeIn(half_period_graph))
        self.play(
            Write(question, run_time = 2),
            ShowCreation(arrow)
        )
        self.play(ShowCreation(v_line))
        for bound in self.bounds + [midpoint]:
            self.play(self.get_v_line_change_anim(
                v_line, self.graph, bound,
                run_time = 3
            ))

    #########

    def get_graph_portion_between_bounds(self):
        self.graph_portion_between_bounds = self.get_graph(
            self.func,
            x_min = self.bounds[0],
            x_max = self.bounds[1],
            color = YELLOW
        )
        return self.graph_portion_between_bounds

    def setup_axes(self):
        GraphScene.setup_axes(self)
        self.add_x_axis_labels()

    def add_x_axis_labels(self):
        labels_and_x_values = [
            ("\\pi/2", np.pi/2),
            ("\\pi", np.pi),
            ("3\\pi/2", 3*np.pi/2),
            ("2\\pi", 2*np.pi),
        ]
        self.x_axis_labels = VGroup()
        for label, x in labels_and_x_values:
            tex_mob = TexMobject(label)
            tex_mob.scale(self.x_label_scale_val)
            tex_mob.move_to(
                self.coords_to_point(x, -3*self.x_axis.tick_size), 
            )
            self.add(tex_mob)
            self.x_axis_labels.add(tex_mob)

class LengthOfDayGraph(GraphScene):
    CONFIG = {
        "x_min" : 0,
        "x_max" : 365,
        "x_axis_width" : 12,
        "x_tick_frequency" : 25,
        "x_labeled_nums" : list(range(50, 365, 50)),
        "x_axis_label" : "Days since March 21",
        "y_min" : 0,
        "y_max" : 16,
        "y_axis_height" : 6,
        "y_tick_frequency" : 1,
        "y_labeled_nums" : list(range(2, 15, 2)),
        "y_axis_label" : "Hours of daylight",
        "graph_origin" : 6*LEFT + 3*DOWN,
        "camera_class" : ThreeDCamera,
        "camera_config" : {
            "shading_factor" : 1,
        }
    }
    def construct(self):
        self.setup_axes()
        self.add_graph()
        self.show_solar_pannel()
        self.set_color_summer_months()
        self.mention_constants()

    def add_graph(self):
        x_label = self.x_axis_label_mob
        y_label = self.y_axis_label_mob

        graph = self.get_graph(
            lambda x : 2.7*np.sin((2*np.pi)*x/365 ) + 12.4,
            color = GREEN,
        )
        graph_label = TexMobject("2.7\\sin(2\\pi x/365) + 12.4")
        graph_label.to_corner(UP+RIGHT).shift(LEFT)
        VGroup(*graph_label[3:6]).set_color(graph.get_color())
        graph_label[9].set_color(YELLOW)

        self.remove(x_label, y_label)
        for label in y_label, x_label:
            self.play(FadeIn(
                label, 
                run_time = 2,
                lag_ratio = 0.5
            ))
        self.play(
            ShowCreation(graph, rate_func=linear),
            FadeIn(
                graph_label,
                rate_func = squish_rate_func(smooth, 0.5, 1),
                lag_ratio = 0.5
            ),
            run_time = 3,
        )
        self.wait()

        self.graph = graph 
        self.graph_label = graph_label

    def show_solar_pannel(self):
        randy = Randolph()
        randy.to_edge(DOWN)
        panel = ThreeDMobject(*[
            Rectangle(
                height = 0.7, width = 0.25,
                fill_color = DARK_GREY,
                fill_opacity = 1,
                stroke_width = 1,
                stroke_color = GREY,
            )
            for x in range(6)
        ])
        panel.arrange(RIGHT, buff = SMALL_BUFF)
        panel.center()
        panels = ThreeDMobject(panel, panel.copy(), panel.copy())
        panels.arrange(DOWN)
        panels.rotate(4*np.pi/12, DOWN)
        panels.rotate(-np.pi/6, OUT)
        side_vect = RIGHT
        side_vect = rotate_vector(side_vect, 4*np.pi/12, DOWN)
        side_vect = rotate_vector(side_vect, -np.pi/3, OUT)
        panels.next_to(randy.get_corner(UP+RIGHT), RIGHT)

        self.play(FadeIn(randy))
        self.play(
            randy.change, "thinking", panels.get_right(),
            FadeIn(
                panels, 
                run_time = 2,
                lag_ratio = 0.5
            )
        )
        for angle in -np.pi/4, np.pi/4:
            self.play(*[
                Rotate(
                    panel, angle,
                    axis = side_vect,
                    in_place = True,
                    run_time = 2,
                    rate_func = squish_rate_func(smooth, a, a+0.8)              
                )
                for panel, a in zip(panels, np.linspace(0, 0.2, len(panels)))
            ])
        self.play(Blink(randy))
        self.play(*list(map(FadeOut, [randy, panels])))

    def set_color_summer_months(self):
        summer_rect = Rectangle()
        summer_rect.set_stroke(width = 0)
        summer_rect.set_fill(YELLOW, opacity = 0.25)
        summer_rect.replace(Line(
            self.graph_origin,
            self.coords_to_point(365/2, 15.5)
        ), stretch = True)

        winter_rect = Rectangle()
        winter_rect.set_stroke(width = 0)
        winter_rect.set_fill(BLUE, opacity = 0.25)
        winter_rect.replace(Line(
            self.coords_to_point(365/2, 15.5),
            self.coords_to_point(365, 0),
        ), stretch = True)


        summer_words, winter_words = [
            TextMobject("%s \\\\ months"%s).move_to(rect)
            for s, rect in [
                ("Summer", summer_rect),
                ("Winter", winter_rect),
            ]
        ]

        for rect, words in (summer_rect, summer_words), (winter_rect, winter_words):
            self.play(
                FadeIn(rect),
                Write(words, run_time = 2)
            )
        self.wait()

    def mention_constants(self):
        #2.7\\sin(2\\pi t/365) + 12.4
        constants = VGroup(*[
            VGroup(*self.graph_label[i:j])
            for i, j in [(0, 3), (7, 9), (11, 14), (16, 20)]
        ])

        self.play(*[
            ApplyFunction(
                lambda c : c.scale_in_place(0.9).shift(SMALL_BUFF*DOWN).set_color(RED),
                constant,
                run_time = 3,
                rate_func = squish_rate_func(there_and_back, a, a+0.7)
            )
            for constant, a in zip(
                constants, 
                np.linspace(0, 0.3, len(constants))
            )
        ])
        self.wait()


    #####

class AskAboutAverageOfContinuousVariables(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "The average \\dots of a \\\\ continuous thing?",
            target_mode = "sassy",
        )
        self.change_student_modes("confused", "sassy", "confused")
        self.play(self.teacher.change_mode, "happy")
        self.wait(2)

class AverageOfFiniteSet(Scene):
    CONFIG = {
        "lengths" : [1, 4, 2, 5]
    }
    def construct(self):
        lengths = self.lengths
        lines = VGroup(*[
            Line(ORIGIN, length*RIGHT)
            for length in lengths
        ])
        colors = Color(BLUE).range_to(RED, len(lengths))
        lines.set_color_by_gradient(*colors)
        lines.arrange(RIGHT)
        lines.generate_target()
        lines.target.arrange(RIGHT, buff = 0)
        for mob in lines, lines.target:
            mob.shift(UP)
        brace = Brace(lines.target, UP)

        labels = VGroup(*[
            TexMobject(str(d)).next_to(line, UP).set_color(line.get_color())
            for d, line in zip(lengths, lines)
        ])
        plusses = [TexMobject("+") for x in range(len(lengths)-1)]
        symbols = VGroup(*
            plusses + [TexMobject("=")]
        )
        symbols.set_fill(opacity = 0)

        labels.generate_target()
        symbols.generate_target()
        symbols.target.set_fill(opacity = 1)
        sum_eq = VGroup(*it.chain(*list(zip(labels.target, symbols.target))))
        sum_eq.arrange(RIGHT)
        sum_eq.next_to(brace, UP)

        sum_mob = TexMobject(str(sum(lengths)))
        sum_mob.next_to(sum_eq, RIGHT)

        dividing_lines = VGroup(*[
            DashedLine(p + MED_SMALL_BUFF*UP, p + MED_LARGE_BUFF*DOWN)
            for alpha in np.linspace(0, 1, len(lengths)+1)
            for p in [interpolate(
                lines.target.get_left(),
                lines.target.get_right(),
                alpha
            )]
        ])

        lower_braces = VGroup(*[
            Brace(VGroup(*dividing_lines[i:i+2]), DOWN)
            for i in range(len(lengths))
        ])
        averages = VGroup(*[
            lb.get_text("$%d/%d$"%(sum(lengths), len(lengths)))
            for lb in lower_braces
        ])
        circle = Circle(color = YELLOW)
        circle.replace(averages[1], stretch = True)
        circle.scale_in_place(1.5)

        self.add(lines)
        self.play(FadeIn(
            labels,
            lag_ratio = 0.5,
            run_time = 3
        ))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            *list(map(MoveToTarget, [lines, labels, symbols])),
            run_time = 2
        )
        self.play(Write(sum_mob))
        self.wait()
        self.play(ShowCreation(dividing_lines, run_time = 2))
        self.play(*it.chain(
            list(map(Write, averages)),
            list(map(GrowFromCenter, lower_braces))
        ))
        self.play(ShowCreation(circle))
        self.wait(2)

class TryToAddInfinitelyManyPoints(AverageOfSineStart):
    CONFIG = {
        "max_denominator" : 40,
    }
    def construct(self):
        self.add_graph()
        self.try_to_add_infinitely_many_values()
        self.show_continuum()
        self.mention_integral()

    def add_graph(self):
        self.setup_axes()
        AverageOfSineStart.add_graph(self, run_time = 0)
        self.add(self.get_graph_portion_between_bounds())
        self.graph_label.to_edge(RIGHT)
        self.graph_label.shift(DOWN)

    def try_to_add_infinitely_many_values(self):
        v_lines = VGroup(*[
            self.get_vertical_line_to_graph(
                numerator*np.pi/denominator, self.graph,
                color = YELLOW,
                stroke_width = 6./denominator
            )
            for denominator in range(self.max_denominator)
            for numerator in range(1, denominator)
            if fractions.gcd(numerator, denominator) == 1
        ])
        ghost_lines = v_lines.copy().set_stroke(GREY)

        v_lines.generate_target()
        start_lines = VGroup(*v_lines.target[:15])
        end_lines = VGroup(*v_lines.target[15:])

        plusses = VGroup(*[TexMobject("+") for x in start_lines])
        sum_eq = VGroup(*it.chain(*list(zip(start_lines, plusses))))
        sum_eq.add(*end_lines)
        sum_eq.arrange(RIGHT)
        sum_eq.next_to(v_lines[0], UP, aligned_edge = LEFT)
        sum_eq.to_edge(UP, buff = MED_SMALL_BUFF)

        h_line = Line(LEFT, RIGHT)
        h_line.set_width(start_lines.get_width())
        h_line.set_color(WHITE)
        h_line.next_to(sum_eq, DOWN, aligned_edge = LEFT)

        infinity = TexMobject("\\infty")
        infinity.next_to(h_line, DOWN)

        self.play(ShowCreation(
            v_lines, 
            run_time = 3,
        ))
        self.add(ghost_lines, v_lines)
        self.wait(2)
        self.play(
            MoveToTarget(
                v_lines,
                run_time = 3,
                lag_ratio = 0.5
            ),
            Write(plusses)
        )
        self.play(ShowCreation(h_line))
        self.play(Write(infinity))
        self.wait()

    def show_continuum(self):
        arrow = Arrow(ORIGIN, UP+LEFT)
        input_range = Line(*[
            self.coords_to_point(bound, 0)
            for bound in self.bounds
        ])
        VGroup(arrow, input_range).set_color(RED)

        self.play(FadeIn(arrow))
        self.play(
            arrow.next_to, input_range.get_start(), 
            DOWN+RIGHT, SMALL_BUFF
        )
        self.play(
            arrow.next_to, input_range.copy().get_end(), 
            DOWN+RIGHT, SMALL_BUFF,
            ShowCreation(input_range),
            run_time = 3,
        )
        self.play(
            arrow.next_to, input_range.get_start(), 
            DOWN+RIGHT, SMALL_BUFF,
            run_time = 3
        )
        self.play(FadeOut(arrow))
        self.wait()

    def mention_integral(self):
        randy = Randolph()
        randy.to_edge(DOWN)
        randy.shift(3*LEFT)

        self.play(FadeIn(randy))
        self.play(PiCreatureBubbleIntroduction(
            randy, "Use an integral!",
            bubble_class = ThoughtBubble,
            target_mode = "hooray"
        ))
        self.play(Blink(randy))
        curr_bubble = randy.bubble
        new_bubble = randy.get_bubble("Somehow...")
        self.play(
            Transform(curr_bubble, new_bubble),
            Transform(curr_bubble.content, new_bubble.content),
            randy.change_mode, "shruggie",
        )
        self.play(Blink(randy))
        self.wait()

class FiniteSample(TryToAddInfinitelyManyPoints):
    CONFIG = {
        "dx" : 0.1,
        "graph_origin" : 6*LEFT + 0.5*DOWN,
    }
    def construct(self):
        self.add_graph()
        self.show_finite_sample()

    def show_finite_sample(self):
        v_lines = self.get_sample_lines(dx = self.dx)
        summed_v_lines = v_lines.copy()
        plusses = VGroup(*[
            TexMobject("+").scale(0.75)
            for l in v_lines
        ])
        numerator = VGroup(*it.chain(*list(zip(summed_v_lines, plusses))))
        for group in numerator, plusses:
            group.remove(plusses[-1])
        numerator.arrange(
            RIGHT, 
            buff = SMALL_BUFF,
            aligned_edge = DOWN
        )
        # numerator.set_width(FRAME_X_RADIUS)
        numerator.scale(0.5)
        numerator.move_to(self.coords_to_point(3*np.pi/2, 0))
        numerator.to_edge(UP)
        frac_line = TexMobject("\\over \\,")
        frac_line.stretch_to_fit_width(numerator.get_width())
        frac_line.next_to(numerator, DOWN)
        denominator = TextMobject("(Num. samples)")
        denominator.next_to(frac_line, DOWN)

        self.play(ShowCreation(v_lines, run_time = 3))
        self.wait()
        self.play(
            ReplacementTransform(
                v_lines.copy(),
                summed_v_lines,
                run_time = 3,
                lag_ratio = 0.5
            ),
            Write(
                plusses,
                rate_func = squish_rate_func(smooth, 0.3, 1)
            )
        )
        self.play(Write(frac_line, run_time = 1))
        self.play(Write(denominator))
        self.wait()

        self.plusses = plusses
        self.average = VGroup(numerator, frac_line, denominator)
        self.v_lines = v_lines

    ###

    def get_sample_lines(self, dx, color = YELLOW, stroke_width = 2):
        return VGroup(*[
            self.get_vertical_line_to_graph(
                x, self.graph,
                color = color,
                stroke_width = stroke_width,
            )
            for x in np.arange(
                self.bounds[0]+dx, 
                self.bounds[1], 
                dx
            )
        ])

class FiniteSampleWithMoreSamplePoints(FiniteSample):
    CONFIG = {
        "dx" : 0.05
    }

class FeelsRelatedToAnIntegral(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Seems integral-ish...",
            target_mode = "maybe"
        )
        self.play(self.teacher.change_mode, "happy")
        self.wait(2)

class IntegralOfSine(FiniteSample):
    CONFIG = {
        "thin_dx" : 0.01,
        "rect_opacity" : 0.75,
    }
    def construct(self):
        self.force_skipping()
        FiniteSample.construct(self)
        self.remove(self.y_axis_label_mob)
        self.remove(*self.x_axis_labels[::2])
        self.revert_to_original_skipping_status()

        self.put_average_in_corner()
        self.write_integral()
        self.show_riemann_rectangles()
        self.let_dx_approach_zero()
        self.bring_back_average()
        self.distribute_dx()
        self.let_dx_approach_zero(restore = False)
        self.write_area_over_width()
        self.show_moving_v_line()

    def put_average_in_corner(self):
        self.average.save_state()
        self.plusses.set_stroke(width = 0.5)
        self.play(
            self.average.scale, 0.75,
            self.average.to_corner, DOWN+RIGHT,
        )

    def write_integral(self):
        integral = TexMobject("\\int_0^\\pi", "\\sin(x)", "\\,dx")
        integral.move_to(self.graph_portion_between_bounds)
        integral.to_edge(UP)

        self.play(Write(integral))
        self.wait(2)

        self.integral = integral

    def show_riemann_rectangles(self):
        kwargs = {
            "dx" : self.dx,
            "x_min" : self.bounds[0],
            "x_max" : self.bounds[1],
            "fill_opacity" : self.rect_opacity,
        }
        rects = self.get_riemann_rectangles(self.graph, **kwargs)
        rects.set_stroke(YELLOW, width = 1)
        flat_rects = self.get_riemann_rectangles(
            self.get_graph(lambda x : 0),
            **kwargs
        )
        thin_kwargs = dict(kwargs)
        thin_kwargs["dx"] = self.thin_dx
        thin_kwargs["stroke_width"] = 0
        self.thin_rects = self.get_riemann_rectangles(
            self.graph,
            **thin_kwargs
        )


        start_index = 20
        end_index = start_index + 5
        low_opacity = 0.5
        high_opacity = 1

        start_rect = rects[start_index]
        side_brace = Brace(start_rect, LEFT, buff = SMALL_BUFF)
        bottom_brace = Brace(start_rect, DOWN, buff = SMALL_BUFF)
        sin_x = TexMobject("\\sin(x)")
        sin_x.next_to(side_brace, LEFT, SMALL_BUFF)
        dx = bottom_brace.get_text("$dx$", buff = SMALL_BUFF)

        self.transform_between_riemann_rects(
            flat_rects, rects,
            replace_mobject_with_target_in_scene = True,
        )
        self.remove(self.v_lines)
        self.wait()

        rects.save_state()
        self.play(*it.chain(
            [
                ApplyMethod(
                    rect.set_style_data, BLACK, 1,
                    None, #Fill color
                    high_opacity if rect is start_rect else low_opacity
                )
                for rect in rects
            ],
            list(map(GrowFromCenter, [side_brace, bottom_brace])),
            list(map(Write, [sin_x, dx])),
        ))
        self.wait()
        for i in range(start_index+1, end_index):
            self.play(
                rects[i-1].set_fill, None, low_opacity,
                rects[i].set_fill, None, high_opacity,
                side_brace.set_height, rects[i].get_height(),
                side_brace.next_to, rects[i], LEFT, SMALL_BUFF,
                bottom_brace.next_to, rects[i], DOWN, SMALL_BUFF,
                MaintainPositionRelativeTo(sin_x, side_brace),
                MaintainPositionRelativeTo(dx, bottom_brace),
            )
            self.wait()
        self.play(
            rects.restore,
            *list(map(FadeOut, [sin_x, dx, side_brace, bottom_brace]))
        )

        self.rects = rects
        self.dx_brace = bottom_brace
        self.dx_label = dx

    def let_dx_approach_zero(self, restore = True):
        start_state = self.rects.copy()
        self.transform_between_riemann_rects(
            self.rects, self.thin_rects,
            run_time = 3
        )
        self.wait(2)
        if restore:
            self.transform_between_riemann_rects(
                self.rects, start_state.copy(),
                run_time = 2,
            )
            self.remove(self.rects)
            self.rects = start_state
            self.rects.set_fill(opacity = 1)
            self.play(
                self.rects.set_fill, None,
                    self.rect_opacity,
            )
            self.wait()

    def bring_back_average(self):
        num_samples = self.average[-1]

        example_dx = TexMobject("0.1")
        example_dx.move_to(self.dx_label)

        input_range = Line(*[
            self.coords_to_point(bound, 0)
            for bound in self.bounds
        ])
        input_range.set_color(RED)

        #Bring back average
        self.play(
            self.average.restore,
            self.average.center,
            self.average.to_edge, UP,
            self.integral.to_edge, DOWN,
            run_time = 2
        )
        self.wait()
        self.play(
            Write(self.dx_brace),
            Write(self.dx_label),
        )
        self.wait()
        self.play(
            FadeOut(self.dx_label),
            FadeIn(example_dx)
        )
        self.play(Indicate(example_dx))
        self.wait()
        self.play(ShowCreation(input_range))
        self.play(FadeOut(input_range))
        self.wait()

        #Ask how many there are
        num_samples_copy = num_samples.copy()
        v_lines = self.v_lines
        self.play(*[
            ApplyFunction(
                lambda l : l.shift(0.5*UP).set_color(GREEN),
                line,
                rate_func = squish_rate_func(
                    there_and_back, a, a+0.3
                ),
                run_time = 3,
            )
            for line, a in zip(
                self.v_lines, 
                np.linspace(0, 0.7, len(self.v_lines))
            )
        ] + [
            num_samples_copy.set_color, GREEN
        ])
        self.play(FadeOut(v_lines))
        self.wait()

        #Count number of samples
        num_samples_copy.generate_target()
        num_samples_copy.target.shift(DOWN + 0.5*LEFT)
        rhs = TexMobject("\\approx", "\\pi", "/", "0.1")
        rhs.next_to(num_samples_copy.target, RIGHT)
        self.play(
            MoveToTarget(num_samples_copy),
            Write(rhs.get_part_by_tex("approx")),
        )
        self.play(ShowCreation(input_range))
        self.play(ReplacementTransform(
            self.x_axis_labels[1].copy(), 
            rhs.get_part_by_tex("pi")
        ))
        self.play(FadeOut(input_range))
        self.play(
            ReplacementTransform(
                example_dx.copy(), 
                rhs.get_part_by_tex("0.1")
            ),
            Write(rhs.get_part_by_tex("/"))
        )
        self.wait(2)

        #Substitute number of samples
        self.play(ReplacementTransform(
            example_dx, self.dx_label
        ))
        dx = rhs.get_part_by_tex("0.1") 
        self.play(Transform(
            dx, TexMobject("dx").move_to(dx)
        ))
        self.wait(2)
        approx = rhs.get_part_by_tex("approx")
        rhs.remove(approx)
        self.play(
            FadeOut(num_samples),
            FadeOut(num_samples_copy),
            FadeOut(approx),
            rhs.next_to, self.average[1], DOWN
        )
        self.wait()

        self.pi_over_dx = rhs

    def distribute_dx(self):
        numerator, frac_line, denominator = self.average
        pi, over, dx = self.pi_over_dx
        integral = self.integral

        dx.generate_target()
        lp, rp = parens = TexMobject("()")
        parens.set_height(numerator.get_height())
        lp.next_to(numerator, LEFT)
        rp.next_to(numerator, RIGHT)
        dx.target.next_to(rp, RIGHT)

        self.play(
            MoveToTarget(dx, path_arc = np.pi/2),
            Write(parens),
            frac_line.stretch_to_fit_width, 
                parens.get_width() + dx.get_width(),
            frac_line.shift, dx.get_width()*RIGHT/2,
            FadeOut(over)
        )
        self.wait(2)

        average = VGroup(parens, numerator, dx, frac_line, pi)
        integral.generate_target()
        over_pi = TexMobject("\\frac{\\phantom{\\int \\sin(x)\\dx}}{\\pi}")
        integral.target.set_width(over_pi.get_width())
        integral.target.next_to(over_pi, UP)
        integral_over_pi = VGroup(integral.target, over_pi)
        integral_over_pi.to_corner(UP+RIGHT)
        arrow = Arrow(LEFT, RIGHT)
        arrow.next_to(integral.target, LEFT)

        self.play(
            average.scale, 0.9,
            average.next_to, arrow, LEFT,
            average.shift_onto_screen,
            ShowCreation(arrow),
            Write(over_pi),
            MoveToTarget(integral, run_time = 2)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [self.dx_label, self.dx_brace])))

        self.integral_over_pi = VGroup(integral, over_pi)
        self.average = average
        self.average_arrow = arrow

    def write_area_over_width(self):
        self.play(
            self.integral_over_pi.shift, 2*LEFT,
            *list(map(FadeOut, [self.average, self.average_arrow]))
        )

        average_height = TextMobject("Average height = ")
        area_over_width = TexMobject(
            "{\\text{Area}", "\\over\\,", "\\text{Width}}", "="
        )
        area_over_width.get_part_by_tex("Area").set_color_by_gradient(
            BLUE, GREEN
        )
        area_over_width.next_to(self.integral_over_pi[1][0], LEFT)
        average_height.next_to(area_over_width, LEFT)

        self.play(*list(map(FadeIn, [average_height, area_over_width])))
        self.wait()

    def show_moving_v_line(self):
        mean = np.mean(self.bounds)
        v_line = self.get_vertical_line_to_graph(
            mean, self.graph,
            line_class = DashedLine,
            color = WHITE,
        )
        self.play(ShowCreation(v_line))
        for count in range(2):
            for x in self.bounds + [mean]:
                self.play(self.get_v_line_change_anim(
                    v_line, self.graph, x,
                    run_time = 3
                ))

class Approx31(Scene):
    def construct(self):
        tex = TexMobject("\\approx 31")
        tex.set_width(FRAME_WIDTH - LARGE_BUFF)
        tex.to_edge(LEFT)
        self.play(Write(tex))
        self.wait(3)

class LetsSolveThis(TeacherStudentsScene):
    def construct(self):
        expression = TexMobject(
            "{\\int_0^\\pi ", " \\sin(x)", "\\,dx \\over \\pi}"
        )
        expression.to_corner(UP+LEFT)
        question = TextMobject(
            "What's the antiderivative \\\\ of",
            "$\\sin(x)$",
            "?"
        )
        for tex_mob in expression, question:
            tex_mob.set_color_by_tex("sin", BLUE)
        self.add(expression)

        self.teacher_says("Let's compute it.")
        self.wait()
        self.student_thinks(question)
        self.wait(2)

class Antiderivative(AverageOfSineStart):
    CONFIG = {
        "antideriv_color" : GREEN,
        "deriv_color" : BLUE,
        "riemann_rect_dx" : 0.01,
        "y_axis_label" : "",
        "graph_origin" : 4*LEFT + DOWN,
    }
    def construct(self):
        self.setup_axes()
        self.add_x_axis_labels()
        self.negate_derivative_of_cosine()
        self.walk_through_slopes()
        self.apply_ftoc()
        self.show_difference_in_antiderivative()
        self.comment_on_area()
        self.divide_by_pi()
        self.set_color_antiderivative_fraction()
        self.show_slope()
        self.bring_back_derivative()
        self.show_tangent_slope()

    def add_x_axis_labels(self):
        AverageOfSineStart.add_x_axis_labels(self)
        self.remove(*self.x_axis_labels[::2])

    def negate_derivative_of_cosine(self):
        cos, neg_cos, sin, neg_sin = graphs = [
            self.get_graph(func)
            for func in [
                np.cos, 
                lambda x : -np.cos(x), 
                np.sin,
                lambda x : -np.sin(x),
            ]
        ]
        VGroup(cos, neg_cos).set_color(self.antideriv_color)
        VGroup(sin, neg_sin).set_color(self.deriv_color)
        labels = ["\\cos(x)", "-\\cos(x)", "\\sin(x)", "-\\sin(x)"]
        x_vals = [2*np.pi, 2*np.pi, 5*np.pi/2, 5*np.pi/2]
        vects = [UP, DOWN, UP, DOWN]
        for graph, label, x_val, vect in zip(graphs, labels, x_vals, vects):
            graph.label = self.get_graph_label(
                graph, label,
                x_val = x_val,
                direction = vect,
                buff = SMALL_BUFF
            ) 

        derivs = []
        for F, f in ("\\cos", "-\\sin"), ("-\\cos", "\\sin"):
            deriv = TexMobject(
                "{d(", F, ")", "\\over\\,", "dx}", "(x)", 
                "=", f, "(x)"
            )
            deriv.set_color_by_tex(F, self.antideriv_color)
            deriv.set_color_by_tex(f, self.deriv_color)
            deriv.to_edge(UP)
            derivs.append(deriv)
        cos_deriv, neg_cos_deriv = derivs

        self.add(cos_deriv)
        for graph in cos, neg_sin:
            self.play(
                ShowCreation(graph, rate_func = smooth),
                Write(
                    graph.label, 
                    rate_func = squish_rate_func(smooth, 0.3, 1)
                ),
                run_time = 2
            )
            self.wait()
        self.wait()
        self.play(*[
            ReplacementTransform(*pair)
            for pair in [
                (derivs),
                (cos, neg_cos),
                (cos.label, neg_cos.label),
                (neg_sin, sin),
                (neg_sin.label, sin.label),
            ]
        ])
        self.wait(2)

        self.neg_cos = neg_cos
        self.sin = sin
        self.deriv = neg_cos_deriv

    def walk_through_slopes(self):
        neg_cos = self.neg_cos
        sin = self.sin

        faders = sin, sin.label
        for mob in faders:
            mob.save_state()
        sin_copy = self.get_graph(
            np.sin,
            x_min = 0,
            x_max = 2*np.pi,
            color = BLUE,
        )
        v_line = self.get_vertical_line_to_graph(
            0, neg_cos,
            line_class = DashedLine,
            color = WHITE
        )

        ss_group = self.get_secant_slope_group(
            0, neg_cos,
            dx = 0.001,
            secant_line_color = YELLOW
        )
        def quad_smooth(t):
            return 0.25*(np.floor(4*t) + smooth((4*t) % 1))

        self.play(*[
            ApplyMethod(m.fade, 0.6)
            for m in faders
        ])
        self.wait()
        self.play(*list(map(ShowCreation, ss_group)), run_time = 2)
        kwargs = {
            "run_time" : 20,
            "rate_func" : quad_smooth,
        }
        v_line_anim = self.get_v_line_change_anim(
            v_line, sin_copy, 2*np.pi,
            **kwargs
        )
        self.animate_secant_slope_group_change(
            ss_group,
            target_x = 2*np.pi,
            added_anims = [
                ShowCreation(sin_copy, **kwargs),
                v_line_anim
            ],
            **kwargs
        )
        self.play(
            *list(map(FadeOut, [ss_group, v_line, sin_copy]))
        )
        self.wait()

        self.ss_group = ss_group

    def apply_ftoc(self):
        deriv = self.deriv
        integral = TexMobject(
            "\\int", "^\\pi", "_0", "\\sin(x)", "\\,dx"
        )
        rhs = TexMobject(
            "=", "\\big(", "-\\cos", "(", "\\pi", ")", "\\big)",
            "-", "\\big(", "-\\cos", "(", "0", ")", "\\big)",
        )
        rhs.next_to(integral, RIGHT)
        equation = VGroup(integral, rhs)
        equation.to_corner(UP+RIGHT, buff = MED_SMALL_BUFF)
        (start_pi, end_pi), (start_zero, end_zero) = start_end_pairs = [
            [
                m.get_part_by_tex(tex) 
                for m in (integral, rhs)
            ]
            for tex in ("\\pi", "0")
        ]

        for tex_mob in integral, rhs:
            tex_mob.set_color_by_tex("sin", self.deriv_color)
            tex_mob.set_color_by_tex("cos", self.antideriv_color)
            tex_mob.set_color_by_tex("0", YELLOW)
            tex_mob.set_color_by_tex("\\pi", YELLOW)

        self.play(
            Write(integral),
            self.deriv.scale, 0.5,
            self.deriv.center,
            self.deriv.to_edge, LEFT, MED_SMALL_BUFF,
            self.deriv.shift, UP,
        )
        self.wait()

        self.play(FadeIn(
            VGroup(*[part for part in rhs if part not in [end_pi, end_zero]]),
            lag_ratio = 0.5,
            run_time = 2,
        ))
        self.wait()
        for start, end in start_end_pairs:
            self.play(ReplacementTransform(
                start.copy(), end,
                path_arc = np.pi/6,
                run_time = 2
            ))
            self.wait()

        self.integral = integral
        self.rhs = rhs

    def show_difference_in_antiderivative(self):
        pi_point, zero_point = points = [
            self.input_to_graph_point(x, self.neg_cos)
            for x in reversed(self.bounds)
        ]
        interim_point = pi_point[0]*RIGHT + zero_point[1]*UP
        pi_dot, zero_dot = dots = [
            Dot(point, color = YELLOW)
            for point in points
        ]
        v_line = DashedLine(pi_point, interim_point)
        h_line = DashedLine(interim_point, zero_point)
        v_line_brace = Brace(v_line, RIGHT)
        two_height_label = v_line_brace.get_text(
            "$2$", buff = SMALL_BUFF
        )
        two_height_label.add_background_rectangle()

        pi = self.x_axis_labels[1]
        #Horrible hack
        black_pi = pi.copy().set_color(BLACK)
        self.add(black_pi, pi)

        cos_tex = self.rhs.get_part_by_tex("cos")

        self.play(ReplacementTransform(
            cos_tex.copy(), pi_dot
        ))
        self.wait()
        moving_dot = pi_dot.copy()
        self.play(
            ShowCreation(v_line),
            # Animation(pi),
            pi.shift, 0.8*pi.get_width()*(LEFT+UP),
            moving_dot.move_to, interim_point,
        )
        self.play(
            ShowCreation(h_line),
            ReplacementTransform(moving_dot, zero_dot)
        )
        self.play(GrowFromCenter(v_line_brace))
        self.wait(2)
        self.play(Write(two_height_label))
        self.wait(2)

        self.v_line = v_line
        self.h_line = h_line
        self.pi_dot = pi_dot
        self.zero_dot = zero_dot
        self.v_line_brace = v_line_brace
        self.two_height_label = two_height_label

    def comment_on_area(self):
        rects = self.get_riemann_rectangles(
            self.sin, 
            dx = self.riemann_rect_dx,
            stroke_width = 0,
            fill_opacity = 0.7,
            x_min = self.bounds[0],
            x_max = self.bounds[1],
        )
        area_two = TexMobject("2").replace(
            self.two_height_label
        )

        self.play(Write(rects))
        self.wait()
        self.play(area_two.move_to, rects)
        self.wait(2)

        self.rects = rects
        self.area_two = area_two

    def divide_by_pi(self):
        integral = self.integral
        rhs = self.rhs
        equals = rhs[0]
        rhs_without_eq = VGroup(*rhs[1:])
        frac_lines = VGroup(*[
            TexMobject("\\over\\,").stretch_to_fit_width(
                mob.get_width()
            ).move_to(mob)
            for mob in (integral, rhs_without_eq)
        ])
        frac_lines.shift(
            (integral.get_height()/2 + SMALL_BUFF)*DOWN
        )
        pi_minus_zeros = VGroup(*[
            TexMobject("\\pi", "-", "0").next_to(line, DOWN)
            for line in frac_lines
        ])
        for tex_mob in pi_minus_zeros:
            for tex in "pi", "0":
                tex_mob.set_color_by_tex(tex, YELLOW)

        answer = TexMobject(" = \\frac{2}{\\pi}")
        answer.next_to(
            frac_lines, RIGHT,
            align_using_submobjects = True
        )
        answer.shift_onto_screen()

        self.play(
            equals.next_to, frac_lines[0].copy(), RIGHT,
            rhs_without_eq.next_to, frac_lines[1].copy(), UP,
            *list(map(Write, frac_lines))
        )
        self.play(*[
            ReplacementTransform(
                integral.get_part_by_tex(tex).copy(),
                pi_minus_zeros[0].get_part_by_tex(tex)
            )
            for tex in ("\\pi","0")
        ] + [
            Write(pi_minus_zeros[0].get_part_by_tex("-"))
        ])
        self.play(*[
            ReplacementTransform(
                rhs.get_part_by_tex(
                    tex, substring = False
                ).copy(),
                pi_minus_zeros[1].get_part_by_tex(tex)
            )
            for tex in ("\\pi", "-", "0")
        ])
        self.wait(2)

        full_equation = VGroup(
            integral, frac_lines, rhs, pi_minus_zeros
        )
        background_rect = BackgroundRectangle(full_equation, fill_opacity = 1)
        background_rect.stretch_in_place(1.2, dim = 1)
        full_equation.add_to_back(background_rect)
        self.play(
            full_equation.shift, 
            (answer.get_width()+MED_LARGE_BUFF)*LEFT
        )
        self.play(Write(answer))
        self.wait()

        self.antiderivative_fraction = VGroup(
            rhs_without_eq,
            frac_lines[1],
            pi_minus_zeros[1]
        )
        self.integral_fraction = VGroup(
            integral,
            frac_lines[0],
            pi_minus_zeros[0],
            equals
        )

    def set_color_antiderivative_fraction(self):
        fraction = self.antiderivative_fraction
        big_rect = Rectangle(
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.75,
        )
        big_rect.set_width(FRAME_WIDTH)
        big_rect.set_height(FRAME_HEIGHT)
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)

        self.play(
            FadeIn(big_rect),
            FadeIn(morty),
            Animation(fraction)
        )
        self.play(morty.change, "raise_right_hand", fraction)
        self.play(Blink(morty))
        self.wait(2)
        self.play(
            FadeOut(big_rect),
            FadeOut(morty),
            Animation(fraction)
        )

    def show_slope(self):
        line = Line(
            self.zero_dot.get_center(),
            self.pi_dot.get_center(),
        )
        line.set_color(RED)
        line.scale_in_place(1.2)

        new_v_line = self.v_line.copy().set_color(RED)
        new_h_line = self.h_line.copy().set_color(RED)

        pi = TexMobject("\\pi")
        pi.next_to(self.h_line, DOWN)

        self.play(
            FadeOut(self.rects),
            FadeOut(self.area_two)
        )
        self.play(ShowCreation(new_v_line))
        self.play(
            ShowCreation(new_h_line),
            Write(pi)
        )
        self.wait()
        self.play(ShowCreation(line, run_time = 2))
        self.wait()

    def bring_back_derivative(self):
        self.play(
            FadeOut(self.integral_fraction),
            self.deriv.scale, 1.7,
            self.deriv.to_corner, UP+LEFT, MED_LARGE_BUFF,
            self.deriv.shift, MED_SMALL_BUFF*DOWN,
        )
        self.wait()

    def show_tangent_slope(self):
        ss_group = self.get_secant_slope_group(
            0, self.neg_cos,
            dx = 0.001,
            secant_line_color = YELLOW,
            secant_line_length = 4,
        )

        self.play(*list(map(ShowCreation, ss_group)), run_time = 2)
        for count in range(2):
            for x in reversed(self.bounds):
                self.animate_secant_slope_group_change(
                    ss_group,
                    target_x = x,
                    run_time = 6,
                )

class GeneralAverage(AverageOfContinuousVariable):
    CONFIG = {
        "bounds" : [1, 6],
        "bound_colors" : [GREEN, RED],
        "graph_origin" : 5*LEFT + 2*DOWN,
        "num_rect_iterations" : 4,
        "max_dx" : 0.25,
    }
    def construct(self):
        self.setup_axes()
        self.add_graph()
        self.ask_about_average()
        self.show_signed_area()
        self.put_area_away()
        self.show_finite_sample()
        self.show_improving_samples()

    def add_graph(self):
        graph = self.get_graph(self.func)
        graph_label = self.get_graph_label(graph, "f(x)")
        v_lines = VGroup(*[
            self.get_vertical_line_to_graph(
                x, graph, line_class = DashedLine
            )
            for x in self.bounds
        ])
        for line, color in zip(v_lines, self.bound_colors):
            line.set_color(color)
        labels = list(map(TexMobject, "ab"))
        for line, label in zip(v_lines, labels):
            vect = line.get_start()-line.get_end()
            label.next_to(line, vect/get_norm(vect))
            label.set_color(line.get_color())

        self.y_axis_label_mob.shift(0.7*LEFT)

        self.play(
            ShowCreation(graph),
            Write(
                graph_label, 
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            run_time = 2
        )
        for line, label in zip(v_lines, labels):
            self.play(
                Write(label),
                ShowCreation(line)
            )
        self.wait()

        self.graph = graph
        self.graph_label = graph_label
        self.bounds_labels = labels
        self.bound_lines = v_lines

    def ask_about_average(self):
        v_line = self.get_vertical_line_to_graph(
            self.bounds[0], self.graph, 
            line_class = DashedLine,
            color = WHITE
        )
        average = TextMobject("Average = ")
        fraction = TexMobject(
            "{\\displaystyle \\int", "^b", "_a", "f(x)", "\\,dx",
            "\\over", "b", "-", "a}"
        )
        for color, tex in zip(self.bound_colors, "ab"):
            fraction.set_color_by_tex(tex, color)
        fraction.set_color_by_tex("displaystyle", WHITE)
        integral = VGroup(*fraction[:5])
        denominator = VGroup(*fraction[5:])
        average.next_to(fraction.get_part_by_tex("over"), LEFT)
        group = VGroup(average, fraction)
        group.center().to_edge(UP).shift(LEFT)

        self.count = 0
        def next_v_line_anim():
            target = self.bounds[0] if self.count%2 == 1 else self.bounds[1]
            self.count += 1
            return self.get_v_line_change_anim(
                v_line, self.graph, target,
                run_time = 4,
            )

        self.play(
            next_v_line_anim(),
            Write(average, run_time = 2),
        )
        self.play(
            next_v_line_anim(),
            Write(
                VGroup(*[
                    fraction.get_part_by_tex(tex)
                    for tex in ("int", "f(x)", "dx", "over")
                ]),
                rate_func = squish_rate_func(smooth, 0.25, 0.75),
                run_time = 4
            ),
            *[
                ReplacementTransform(
                    label.copy(),
                    fraction.get_part_by_tex(tex, substring = False),
                    run_time = 2
                )
                for label, tex in zip(
                    self.bounds_labels, 
                    ["_a", "^b"]
                )
            ]
        )
        self.play(
            next_v_line_anim(),
            Write(
                fraction.get_part_by_tex("-"),
                run_time = 4,
                rate_func = squish_rate_func(smooth, 0.5, 0.75),
            ),
            *[
                ReplacementTransform(
                    label.copy(),
                    fraction.get_part_by_tex(tex, substring = False),
                    run_time = 4,
                    rate_func = squish_rate_func(smooth, 0.25, 0.75)
                )
                for label, tex in zip(
                    self.bounds_labels, 
                    ["a}", "b"]
                )
            ]

        )
        self.play(next_v_line_anim())
        self.play(FadeOut(v_line))

        self.average_expression = VGroup(average, fraction)

    def show_signed_area(self):
        rect_list = self.get_riemann_rectangles_list(
            self.graph,
            self.num_rect_iterations,
            max_dx = self.max_dx,
            x_min = self.bounds[0],
            x_max = self.bounds[1],
            end_color = BLUE,
            fill_opacity = 0.75,
            stroke_width = 0.25,
        )
        rects = rect_list[0]
        plus = TexMobject("+")
        plus.move_to(self.coords_to_point(2, 2))
        minus = TexMobject("-")
        minus.move_to(self.coords_to_point(5.24, -1))

        self.play(FadeIn(
            rects, 
            run_time = 2,
            lag_ratio = 0.5
        ))
        for new_rects in rect_list[1:]:
            self.transform_between_riemann_rects(rects, new_rects)
        self.play(Write(plus))
        self.play(Write(minus))
        self.wait(2)

        self.area = VGroup(rects, plus, minus)

    def put_area_away(self):
        self.play(
            FadeOut(self.area),
            self.average_expression.scale, 0.75,
            self.average_expression.to_corner, DOWN+RIGHT,
        )
        self.wait()

    def show_finite_sample(self):
        v_lines = self.get_vertical_lines_to_graph(
            self.graph,
            x_min = self.bounds[0],
            x_max = self.bounds[1],
            color = GREEN
        )
        for line in v_lines:
            if self.y_axis.point_to_number(line.get_end()) < 0:
                line.set_color(RED)
            line.save_state()

        line_pair = VGroup(*v_lines[6:8])
        brace = Brace(line_pair, DOWN)
        dx = brace.get_text("$dx$")

        num_samples = TextMobject("Num. samples")
        approx = TexMobject("\\approx")
        rhs = TexMobject("{b", "-", "a", "\\over", "dx}")
        for tex, color in zip("ab", self.bound_colors):
            rhs.set_color_by_tex(tex, color)
        expression = VGroup(num_samples, approx, rhs)
        expression.arrange(RIGHT)
        expression.next_to(self.y_axis, RIGHT)
        rhs_copy = rhs.copy()

        f_brace = Brace(line_pair, LEFT, buff = 0)
        f_x = f_brace.get_text("$f(x)$")
        add_up_f_over = TexMobject("\\text{Add up $f(x)$}", "\\over")
        add_up_f_over.next_to(num_samples, UP)
        add_up_f_over.to_edge(UP)


        self.play(ShowCreation(v_lines, run_time = 2))
        self.play(*list(map(Write, [brace, dx])))
        self.wait()
        self.play(Write(VGroup(num_samples, approx, *rhs[:-1])))
        self.play(ReplacementTransform(
            dx.copy(), rhs.get_part_by_tex("dx")
        ))
        self.wait(2)

        self.play(
            FadeIn(add_up_f_over),
            *[
                ApplyFunction(
                    lambda m : m.fade().set_stroke(width = 2),
                    v_line
                )
                for v_line in v_lines
            ]
        )
        self.play(*[
            ApplyFunction(
                lambda m : m.restore().set_stroke(width = 5),
                v_line,
                run_time = 3,
                rate_func = squish_rate_func(
                    there_and_back, a, a+0.2
                )
            )
            for v_line, a in zip(v_lines, np.linspace(0, 0.8, len(v_lines)))
        ])
        self.play(*[vl.restore for vl in v_lines])
        self.play(rhs_copy.next_to, add_up_f_over, DOWN)
        self.wait(2)
        frac_line = add_up_f_over[1]
        self.play(
            FadeOut(rhs_copy.get_part_by_tex("over")),
            rhs_copy.get_part_by_tex("dx").next_to,
                add_up_f_over[0], RIGHT, SMALL_BUFF,
            frac_line.scale_about_point, 1.2, frac_line.get_left(),
            frac_line.stretch_to_fit_height, frac_line.get_height(),
        )
        rhs_copy.remove(rhs_copy.get_part_by_tex("over"))
        self.wait(2)

        int_fraction = self.average_expression[1].copy()
        int_fraction.generate_target()
        int_fraction.target.next_to(add_up_f_over, RIGHT, LARGE_BUFF)
        int_fraction.target.shift_onto_screen()
        double_arrow = TexMobject("\\Leftrightarrow")
        double_arrow.next_to(
            int_fraction.target.get_part_by_tex("over"), LEFT
        )

        self.play(
            MoveToTarget(int_fraction),
            VGroup(add_up_f_over, rhs_copy).shift, 0.4*DOWN
        )
        self.play(Write(double_arrow))
        self.play(*list(map(FadeOut, [
            dx, brace, num_samples, approx, rhs
        ])))
        self.wait()

        self.v_lines = v_lines

    def show_improving_samples(self):
        stroke_width = self.v_lines[0].get_stroke_width()
        new_v_lines_list = [
            self.get_vertical_lines_to_graph(
                self.graph,
                x_min = self.bounds[0],
                x_max = self.bounds[1],
                num_lines = len(self.v_lines)*(2**n),
                color = GREEN,
                stroke_width = float(stroke_width)/n
            )
            for n in range(1, 4)
        ]
        for new_v_lines in new_v_lines_list:
            for line in new_v_lines:
                if self.y_axis.point_to_number(line.get_end()) < 0:
                    line.set_color(RED)

        for new_v_lines in new_v_lines_list:
            self.play(Transform(
                self.v_lines, new_v_lines,
                run_time = 2,
                lag_ratio = 0.5
            ))
        self.wait()

    ####

    def func(self, x):
        return 0.09*(x+1)*(x-4)*(x-8)

class GeneralAntiderivative(GeneralAverage):
    def construct(self):
        self.force_skipping()
        self.setup_axes()
        self.add_graph()
        self.revert_to_original_skipping_status()

        self.fade_existing_graph()
        self.add_fraction()
        self.add_antiderivative_graph()
        self.show_average_in_terms_of_F()
        self.draw_slope()
        self.show_tangent_line_slopes()

    def fade_existing_graph(self):
        self.graph.fade(0.3)
        self.graph_label.fade(0.3)
        self.bound_lines.fade(0.3)

    def add_fraction(self):
        fraction = TexMobject(
            "{\\displaystyle \\int", "^b", "_a", "f(x)", "\\,dx",
            "\\over", "b", "-", "a}"
        )
        for tex, color in zip("ab", self.bound_colors):
            fraction.set_color_by_tex(tex, color)
        fraction.set_color_by_tex("display", WHITE)

        fraction.scale(0.8)
        fraction.next_to(self.y_axis, RIGHT)
        fraction.to_edge(UP, buff = MED_SMALL_BUFF)
        self.add(fraction)

        self.fraction = fraction

    def add_antiderivative_graph(self):
        x_max = 9.7
        antideriv_graph = self.get_graph(
            lambda x : scipy.integrate.quad(
                self.graph.underlying_function,
                1, x
            )[0],
            color = YELLOW,
            x_max = x_max,
        )
        antideriv_graph_label = self.get_graph_label(
            antideriv_graph, "F(x)",
            x_val = x_max
        )

        deriv = TexMobject(
            "{dF", "\\over", "dx}", "(x)", "=", "f(x)"
        )
        deriv.set_color_by_tex("dF", antideriv_graph.get_color())
        deriv.set_color_by_tex("f(x)", BLUE)
        deriv.next_to(
            antideriv_graph_label, DOWN, MED_LARGE_BUFF, LEFT
        )

        self.play(
            ShowCreation(antideriv_graph),
            Write(
                antideriv_graph_label, 
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            run_time = 2,
        )
        self.wait()
        self.play(Write(deriv))
        self.wait()

        self.antideriv_graph = antideriv_graph

    def show_average_in_terms_of_F(self):
        new_fraction = TexMobject(
            "=", 
            "{F", "(", "b", ")", "-", "F", "(", "a", ")",
            "\\over",
            "b", "-", "a}"
        )
        for tex, color in zip("abF", self.bound_colors+[YELLOW]):
            new_fraction.set_color_by_tex(tex, color)
        new_fraction.next_to(
            self.fraction.get_part_by_tex("over"), RIGHT,
            align_using_submobjects = True
        )   

        to_write = VGroup(*it.chain(*[
            new_fraction.get_parts_by_tex(tex)
            for tex in "=F()-"
        ]))
        to_write.remove(new_fraction.get_parts_by_tex("-")[-1])

        numerator = VGroup(*new_fraction[1:10])
        denominator = VGroup(*new_fraction[-3:])

        self.play(Write(to_write))
        self.play(*[
            ReplacementTransform(
                label.copy(),
                new_fraction.get_part_by_tex(tex),
                run_time = 2,
                rate_func = squish_rate_func(smooth, a, a+0.7)
            )
            for label, tex, a in zip(
                self.bounds_labels, "ab", [0, 0.3]
            )
        ])
        self.wait()

        self.show_change_in_height(numerator.copy())
        self.shift_antideriv_graph_up_and_down()
        self.play(Write(VGroup(*new_fraction[-4:])))
        self.wait()

        h_line_brace = Brace(self.h_line, DOWN)
        denominator_copy = denominator.copy()
        a_label = self.bounds_labels[0]
        self.play(
            GrowFromCenter(h_line_brace),
            a_label.shift, 0.7*a_label.get_width()*LEFT,
            a_label.shift, 2.2*a_label.get_height()*UP,
        )
        self.play(
            denominator_copy.next_to, h_line_brace, 
            DOWN, SMALL_BUFF
        )
        self.wait(3)

    def show_change_in_height(self, numerator):
        numerator.add_to_back(BackgroundRectangle(numerator))
        a_point, b_point = points = [
            self.input_to_graph_point(x, self.antideriv_graph)
            for x in self.bounds
        ]
        interim_point = b_point[0]*RIGHT + a_point[1]*UP

        v_line = Line(b_point, interim_point)
        h_line = Line(interim_point, a_point)
        VGroup(v_line, h_line).set_color(WHITE)
        brace = Brace(v_line, RIGHT, buff = SMALL_BUFF)

        graph_within_bounds = self.get_graph(
            self.antideriv_graph.underlying_function,
            x_min = self.bounds[0], 
            x_max = self.bounds[1],
            color = self.antideriv_graph.get_color()
        )

        b_label = self.bounds_labels[1]
        self.play(
            self.antideriv_graph.fade, 0.7,
            Animation(graph_within_bounds)
        )
        self.play(
            ShowCreation(v_line),
            b_label.shift, b_label.get_width()*RIGHT,
            b_label.shift, 1.75*b_label.get_height()*DOWN,
        )
        self.play(ShowCreation(h_line))
        self.play(
            numerator.scale, 0.75,
            numerator.next_to, brace.copy(), RIGHT, SMALL_BUFF,
            GrowFromCenter(brace),
        )
        self.wait(2)

        self.antideriv_graph.add(
            graph_within_bounds, v_line, h_line, numerator, brace
        )
        self.h_line = h_line
        self.graph_points_at_bounds = points

    def shift_antideriv_graph_up_and_down(self):
        for vect in 2*UP, 3*DOWN, UP:
            self.play(
                self.antideriv_graph.shift, vect,
                run_time = 2
            )
        self.wait()

    def draw_slope(self):
        line = Line(*self.graph_points_at_bounds)
        line.set_color(PINK)
        line.scale_in_place(1.3)

        self.play(ShowCreation(line, run_time = 2))
        self.wait()

    def show_tangent_line_slopes(self):
        ss_group = self.get_secant_slope_group(
            x = self.bounds[0],
            graph = self.antideriv_graph,
            dx = 0.001,
            secant_line_color = BLUE,
            secant_line_length = 2,
        )

        self.play(*list(map(ShowCreation, ss_group)))
        for x in range(2):
            for bound in reversed(self.bounds):
                self.animate_secant_slope_group_change(
                    ss_group,
                    target_x = bound,
                    run_time = 5,
                )

class LastVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Chapter 8: Integrals")
        title.to_edge(UP)
        rect = Rectangle(height = 9, width = 16)
        rect.set_stroke(WHITE)
        rect.set_height(1.5*FRAME_Y_RADIUS)
        rect.next_to(title, DOWN)

        self.play(Write(title), ShowCreation(rect))
        self.wait(5)

class ASecondIntegralSensation(TeacherStudentsScene):
    def construct(self):
        finite_average = TexMobject("{1+5+4+2 \\over 4}")
        numbers = VGroup(*finite_average[0:7:2])
        plusses = VGroup(*finite_average[1:7:2])
        denominator = VGroup(*finite_average[7:])
        finite_average.to_corner(UP+LEFT)
        finite_average.to_edge(LEFT)

        continuum = UnitInterval(
            color = GREY,
            unit_size = 6
        )
        continuum.next_to(finite_average, RIGHT, 2)
        line = Line(continuum.get_left(), continuum.get_right())
        line.set_color(YELLOW)
        arrow = Arrow(DOWN+RIGHT, ORIGIN)
        arrow.next_to(line.get_start(), DOWN+RIGHT, SMALL_BUFF)

        sigma_to_integral = TexMobject(
            "\\sum \\Leftrightarrow \\int"
        )
        sigma_to_integral.next_to(
            self.teacher.get_corner(UP+LEFT), UP, MED_LARGE_BUFF
        )

        self.teacher_says(
            "A second integral \\\\ sensation"
        )
        self.change_student_modes(*["erm"]*3)
        self.wait()
        self.play(
            Write(numbers),
            RemovePiCreatureBubble(self.teacher),
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = numbers
        )
        self.play(Write(plusses))
        self.wait()
        self.play(Write(denominator))
        self.wait()

        self.change_student_modes(
            *["confused"]*3,
            look_at_arg = continuum,
            added_anims = [Write(continuum, run_time = 2)]
        )
        self.play(ShowCreation(arrow))
        arrow.save_state()
        self.play(
            arrow.next_to, line.copy().get_end(), DOWN+RIGHT, SMALL_BUFF,
            ShowCreation(line),
            run_time = 2
        )
        self.play(*list(map(FadeOut, [arrow])))
        self.wait(2)
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = sigma_to_integral,
            added_anims = [
                Write(sigma_to_integral),
                self.teacher.change_mode, "raise_right_hand"
            ]
        )
        self.wait(3)

class Chapter9PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "CrypticSwarm",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Karan Bhargava",
            "Ankit Agarwal",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Juan Benet",
            "Othman Alikhan",
            "Markus Persson",
            "Dan Buchoff",
            "Derek Dai",
            "Joseph John Cox",
            "Luc Ritchie",
            "Zac Wentzell",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Nils Schneider",
            "James Thornton",
            "Mustafa Mahdi",
            "Jonathan Eppele",
            "Mathew Bramson",
            "Jerry Ling",
            "Mark Govea",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ],
    }

class Thumbnail(GraphScene):
    CONFIG = {
        "x_min" : -0.2,
        "x_max" : 3.5,
        "x_leftmost_tick" : 0,
        "x_tick_frequency" : np.pi/4,
        "x_axis_label" : "",
        "y_min" : -0.75,
        "y_max" : 0.75,
        "y_axis_height" : 4.5,
        "y_tick_frequency" : 0.25,
        "y_axis_label" : ""
    }
    def construct(self):
        self.setup_axes()
        self.remove(self.axes)

        sine = self.get_graph(np.sin)
        rects = self.get_riemann_rectangles(
            sine,
            x_min = 0,
            x_max = np.pi,
            dx = 0.01,
            stroke_width = 0,
        )
        sine.add_to_back(rects)
        sine.add(self.axes.copy())
        sine.to_corner(UP+LEFT, buff = SMALL_BUFF)
        sine.scale(0.9)

        area = TextMobject("Area")
        area.scale(3)
        area.move_to(rects)

        cosine = self.get_graph(lambda x : -np.cos(x))
        cosine.set_stroke(GREEN, 8)
        line = self.get_secant_slope_group(
            0.75*np.pi, cosine, 
            dx = 0.01
        ).secant_line
        line.set_stroke(PINK, 7)
        cosine.add(line)
        cosine.add(self.axes.copy())
        cosine.scale(0.7)
        cosine.to_corner(DOWN+RIGHT, buff = MED_SMALL_BUFF)

        slope = TextMobject("Slope")
        slope.scale(3)
        # slope.next_to(cosine, LEFT, buff = 0)
        # slope.to_edge(DOWN)
        slope.to_corner(DOWN+RIGHT)

        double_arrow = DoubleArrow(
            area.get_bottom(),
            slope.get_left(),
            color = YELLOW,
            tip_length = 0.75,
            buff = MED_LARGE_BUFF
        )
        double_arrow.set_stroke(width = 18)

        triangle = Polygon(
            ORIGIN, UP, UP+RIGHT,
            stroke_width = 0,
            fill_color = BLUE_E,
            fill_opacity = 0.5,
        )
        triangle.stretch_to_fit_width(FRAME_WIDTH)
        triangle.stretch_to_fit_height(FRAME_HEIGHT)
        triangle.to_corner(UP+LEFT, buff = 0)

        alt_triangle = triangle.copy()
        alt_triangle.rotate(np.pi)
        alt_triangle.set_fill(BLACK, 1)

        self.add(
            triangle, sine, area, 
            alt_triangle, cosine, slope, 
            double_arrow,
        )







































