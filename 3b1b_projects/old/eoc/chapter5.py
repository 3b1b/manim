from manimlib.imports import *
from old_projects.eoc.chapter4 import ThreeLinesChainRule

class ExpFootnoteOpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
        "Who has not been amazed to learn that the function",
        "$y = e^x$,", "like a phoenix rising again from its own",
        "ashes, is its own derivative?",
        ],
        "highlighted_quote_terms" : {
            "$y = e^x$" : MAROON_B
        },
        "author" : "Francois le Lionnais"
    }

class LastVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        last_video = series[2]
        last_video.save_state()
        this_video = series[3]

        known_formulas = VGroup(*list(map(TexMobject, [
            "\\frac{d(x^n)}{dx} = nx^{n-1}",
            "\\frac{d(\\sin(x))}{dx} = \\cos(x)",
        ])))
        known_formulas.arrange(
            DOWN, buff = MED_LARGE_BUFF,
        )
        known_formulas.set_height(2.5)
        exp_question = TexMobject("2^x", ", 7^x, ", "e^x", " ???")

        last_video_brace = Brace(last_video)
        known_formulas.next_to(last_video_brace, DOWN)
        known_formulas.shift(MED_LARGE_BUFF*LEFT)
        last_video_brace.save_state()
        last_video_brace.shift(3*LEFT)
        last_video_brace.set_fill(opacity = 0)

        self.add(series)
        self.play(
            last_video_brace.restore,
            last_video.set_color, YELLOW,
            self.get_teacher().change_mode, "raise_right_hand",
        )
        self.play(Write(known_formulas))
        self.wait()
        self.student_says(
            exp_question, student_index = 1,
            added_anims = [self.get_teacher().change_mode, "pondering"]
        )
        self.wait(3)
        e_to_x = exp_question.get_part_by_tex("e^x")
        self.play(
            self.teacher.change_mode, "raise_right_hand",
            e_to_x.scale, 1.5,
            e_to_x.set_color, YELLOW,
            e_to_x.next_to, self.teacher.get_corner(UP+LEFT), UP
        )
        self.wait(2)

class PopulationSizeGraphVsPopulationMassGraph(Scene):
    def construct(self):
        pass

class DoublingPopulation(PiCreatureScene):
    CONFIG = {
        "time_color" : YELLOW,
        "pi_creature_grid_dimensions" : (8, 8),
        "pi_creature_grid_height" : 6,
    }
    
    def construct(self):
        self.remove(self.get_pi_creatures())
        self.introduce_expression()
        self.introduce_pi_creatures()
        self.count_through_days()
        self.ask_about_dM_dt()
        self.growth_per_day()
        self.relate_growth_rate_to_pop_size()

    def introduce_expression(self):
        f_x = TexMobject("f(x)", "=", "2^x")
        f_t = TexMobject("f(t)", "=", "2^t")
        P_t = TexMobject("P(t)", "=", "2^t")
        M_t = TexMobject("M(t)", "=", "2^t")
        functions = VGroup(f_x, f_t, P_t, M_t)
        for function in functions:
            function.scale(1.2)
            function.to_corner(UP+LEFT)
        for function in functions[1:]:
            for i, j in (0, 2), (2, 1):
                function[i][j].set_color(self.time_color)

        t_expression = TexMobject("t", "=", "\\text{Time (in days)}")
        t_expression.to_corner(UP+RIGHT)
        t_expression[0].set_color(self.time_color)

        pop_brace, mass_brace = [
            Brace(function[0], DOWN)
            for function in (P_t, M_t)
        ]
        for brace, word in (pop_brace, "size"), (mass_brace, "mass"):
            text = brace.get_text("Population %s"%word)
            text.to_edge(LEFT)
            brace.text = text

        self.play(Write(f_x))
        self.wait()
        self.play(
            Transform(f_x, f_t),
            FadeIn(
                t_expression,
                run_time = 2,
                lag_ratio = 0.5
            )
        )
        self.play(Transform(f_x, P_t))
        self.play(
            GrowFromCenter(pop_brace),
            Write(pop_brace.text, run_time = 2)
        )
        self.wait(2)

        self.function = f_x
        self.pop_brace = pop_brace
        self.t_expression = t_expression
        self.mass_function = M_t
        self.mass_brace = mass_brace

    def introduce_pi_creatures(self):
        creatures = self.get_pi_creatures()
        total_num_days = self.get_num_days()
        num_start_days = 4

        self.reset()
        for x in range(num_start_days):
            self.let_one_day_pass()
        self.wait()
        self.play(
            Transform(self.function, self.mass_function),
            Transform(self.pop_brace, self.mass_brace),
            Transform(self.pop_brace.text, self.mass_brace.text),
        )
        self.wait()
        for x in range(total_num_days-num_start_days):
            self.let_one_day_pass()
            self.wait()
        self.joint_blink(shuffle = False)
        self.wait()

    def count_through_days(self):
        self.reset()
        brace = self.get_population_size_descriptor()
        days_to_let_pass = 3

        self.play(GrowFromCenter(brace))
        self.wait()
        for x in range(days_to_let_pass):
            self.let_one_day_pass()
            new_brace = self.get_population_size_descriptor()
            self.play(Transform(brace, new_brace))
            self.wait()

        self.population_size_descriptor = brace

    def ask_about_dM_dt(self):
        dM_dt_question = TexMobject("{dM", "\\over dt}", "=", "???")
        dM, dt, equals, q_marks = dM_dt_question
        dM_dt_question.next_to(self.function, DOWN, buff = LARGE_BUFF)
        dM_dt_question.to_edge(LEFT)

        self.play(
            FadeOut(self.pop_brace),
            FadeOut(self.pop_brace.text),
            Write(dM_dt_question)
        )
        self.wait(3)
        for mob in dM, dt:
            self.play(Indicate(mob))
            self.wait()

        self.dM_dt_question = dM_dt_question

    def growth_per_day(self):
        day_to_day, frac = self.get_from_day_to_day_label()

        self.play(
            FadeOut(self.dM_dt_question),
            FadeOut(self.population_size_descriptor),
            FadeIn(day_to_day)
        )
        rect = self.let_day_pass_and_highlight_new_creatures(frac)

        for x in range(2):
            new_day_to_day, new_frac = self.get_from_day_to_day_label()
            self.play(*list(map(FadeOut, [rect, frac])))
            frac = new_frac
            self.play(Transform(day_to_day, new_day_to_day))
            rect = self.let_day_pass_and_highlight_new_creatures(frac)
        self.play(*list(map(FadeOut, [rect, frac, day_to_day])))

    def let_day_pass_and_highlight_new_creatures(self, frac):
        num_new_creatures = 2**self.get_curr_day()

        self.let_one_day_pass()
        new_creatures = VGroup(
            *self.get_on_screen_pi_creatures()[-num_new_creatures:]
        )
        rect = Rectangle(
            color = GREEN,
            fill_color = BLUE,
            fill_opacity = 0.3,
        )
        rect.replace(new_creatures, stretch = True)
        rect.stretch_to_fit_height(rect.get_height()+MED_SMALL_BUFF)
        rect.stretch_to_fit_width(rect.get_width()+MED_SMALL_BUFF)
        self.play(DrawBorderThenFill(rect))
        self.play(Write(frac))
        self.wait()
        return rect

    def relate_growth_rate_to_pop_size(self):
        false_deriv = TexMobject(
            "{d(2^t) ", "\\over dt}", "= 2^t"
        )
        difference_eq = TexMobject(
            "{ {2^{t+1} - 2^t} \\over", "1}", "= 2^t"
        )
        real_deriv = TexMobject(
            "{ {2^{t+dt} - 2^t} \\over", "dt}", "= \\, ???"
        )
        VGroup(
            false_deriv[0][3], 
            false_deriv[2][-1],
            difference_eq[0][1],
            difference_eq[0][-2],
            difference_eq[2][-1],
            difference_eq[2][-1],
            real_deriv[0][1],
            real_deriv[0][-2],
        ).set_color(YELLOW)
        VGroup(
            difference_eq[0][3],
            difference_eq[1][-1],
            real_deriv[0][3],
            real_deriv[0][4],
            real_deriv[1][-2],
            real_deriv[1][-1],
        ).set_color(GREEN)

        expressions = [false_deriv, difference_eq, real_deriv]
        text_arg_list = [
            ("Tempting", "...",),
            ("Rate of change", "\\\\ over one full day"),
            ("Rate of change", "\\\\ in a small time"),
        ]
        for expression, text_args in zip(expressions, text_arg_list):
            expression.next_to(
                self.function, DOWN, 
                buff = LARGE_BUFF,
                aligned_edge = LEFT,
            )
            expression.brace = Brace(expression, DOWN)
            expression.brace_text = expression.brace.get_text(*text_args)

        time = self.t_expression[-1]
        new_time = TexMobject("3")
        new_time.move_to(time, LEFT)

        fading_creatures = VGroup(*self.get_on_screen_pi_creatures()[8:])


        self.play(*list(map(FadeIn, [
            false_deriv, false_deriv.brace, false_deriv.brace_text
        ])))
        self.wait()
        self.play(
            Transform(time, new_time),
            FadeOut(fading_creatures)
        )
        self.wait()
        for x in range(3):
            self.let_one_day_pass(run_time = 2)
            self.wait(2)

        for expression in difference_eq, real_deriv:
            expression.brace_text[1].set_color(GREEN)
            self.play(
                Transform(false_deriv, expression),
                Transform(false_deriv.brace, expression.brace),
                Transform(false_deriv.brace_text, expression.brace_text),
            )
            self.wait(3)
        self.reset()
        for x in range(self.get_num_days()):
            self.let_one_day_pass()
        self.wait()

        rect = Rectangle(color = YELLOW)
        rect.replace(real_deriv)
        rect.stretch_to_fit_width(rect.get_width()+MED_SMALL_BUFF)
        rect.stretch_to_fit_height(rect.get_height()+MED_SMALL_BUFF)
        self.play(*list(map(FadeOut, [
            false_deriv.brace, false_deriv.brace_text
        ])))
        self.play(ShowCreation(rect))
        self.play(*[
            ApplyFunction(
                lambda pi : pi.change_mode("pondering").look_at(real_deriv),
                pi,
                run_time = 2,
                rate_func = squish_rate_func(smooth, a, a+0.5)
            )
            for pi in self.get_pi_creatures()
            for a in [0.5*random.random()]
        ])
        self.wait(3)

    ###########

    def create_pi_creatures(self):
        width, height = self.pi_creature_grid_dimensions
        creature_array = VGroup(*[
            VGroup(*[
                PiCreature(mode = "plain")
                for y in range(height)
            ]).arrange(UP, buff = MED_LARGE_BUFF)
            for x in range(width)
        ]).arrange(RIGHT, buff = MED_LARGE_BUFF)
        creatures = VGroup(*it.chain(*creature_array))
        creatures.set_height(self.pi_creature_grid_height)
        creatures.to_corner(DOWN+RIGHT)

        colors = color_gradient([BLUE, GREEN, GREY_BROWN], len(creatures))
        random.shuffle(colors)
        for creature, color in zip(creatures, colors):
            creature.set_color(color)

        return creatures

    def reset(self):
        time = self.t_expression[-1]
        faders = [time] + list(self.get_on_screen_pi_creatures())
        new_time = TexMobject("0")
        new_time.next_to(self.t_expression[-2], RIGHT)
        first_creature = self.get_pi_creatures()[0]

        self.play(*list(map(FadeOut, faders)))
        self.play(*list(map(FadeIn, [first_creature, new_time])))
        self.t_expression.submobjects[-1] = new_time

    def let_one_day_pass(self, run_time = 2):
        all_creatures = self.get_pi_creatures()
        on_screen_creatures = self.get_on_screen_pi_creatures()
        low_i = len(on_screen_creatures)
        high_i = min(2*low_i, len(all_creatures))
        new_creatures = VGroup(*all_creatures[low_i:high_i])

        to_children_anims = []
        growing_anims = []
        for old_pi, pi in zip(on_screen_creatures, new_creatures):
            pi.save_state()
            child = pi.copy()
            child.scale(0.25, about_point = child.get_bottom())
            child.eyes.scale(1.5, about_point = child.eyes.get_bottom())
            pi.move_to(old_pi)
            pi.set_fill(opacity = 0)

            index = list(new_creatures).index(pi)
            prop = float(index)/len(new_creatures)
            alpha  = np.clip(len(new_creatures)/8.0, 0, 0.5)
            rate_func = squish_rate_func(
                smooth, alpha*prop, alpha*prop+(1-alpha)
            )

            to_child_anim = Transform(pi, child, rate_func = rate_func)
            to_child_anim.update(1)
            growing_anim = ApplyMethod(pi.restore, rate_func = rate_func)
            to_child_anim.update(0)

            to_children_anims.append(to_child_anim)
            growing_anims.append(growing_anim)

        time = self.t_expression[-1]
        total_new_creatures = len(on_screen_creatures) + len(new_creatures)
        new_time = TexMobject(str(int(np.log2(total_new_creatures))))
        new_time.move_to(time, LEFT)

        growing_anims.append(Transform(time, new_time))

        self.play(*to_children_anims, run_time = run_time/2.0)
        self.play(*growing_anims, run_time = run_time/2.0)
        
    def get_num_pi_creatures_on_screen(self):
        mobjects = self.get_mobjects()
        return sum([
            pi in mobjects for pi in self.get_pi_creatures()
        ])

    def get_population_size_descriptor(self):
        on_screen_creatures = self.get_on_screen_pi_creatures()
        brace = Brace(on_screen_creatures, LEFT)
        n = len(on_screen_creatures)
        label = brace.get_text(
            "$2^%d$"%int(np.log2(n)),
            "$=%d$"%n,
        )
        brace.add(label)
        return brace

    def get_num_days(self):
        x, y = self.pi_creature_grid_dimensions
        return int(np.log2(x*y))

    def get_curr_day(self):
        return int(np.log2(len(self.get_on_screen_pi_creatures())))

    def get_from_day_to_day_label(self):
        curr_day = self.get_curr_day()
        top_words = TextMobject(
            "From day", str(curr_day), 
            "to", str(curr_day+1), ":"
        )
        top_words.set_width(4)
        top_words.next_to(
            self.function, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        top_words[1].set_color(GREEN)

        bottom_words = TexMobject(
            str(2**curr_day),
            "\\text{ creatures}", "\\over {1 \\text{ day}}"
        )
        bottom_words[0].set_color(GREEN)
        bottom_words.next_to(top_words, DOWN, buff = MED_LARGE_BUFF)

        return top_words, bottom_words

class GraphOfTwoToT(GraphScene):
    CONFIG = {
        "x_axis_label" : "$t$",
        "y_axis_label" : "$M$",
        "x_labeled_nums" : list(range(1, 7)),
        "y_labeled_nums" : list(range(8, 40, 8)),
        "x_max" : 6,
        "y_min" : 0,
        "y_max" : 32,
        "y_tick_frequency" : 2,
        "graph_origin" : 2.5*DOWN + 5*LEFT,
    }
    def construct(self):
        self.setup_axes()
        example_t = 3
        graph = self.get_graph(lambda t : 2**t, color = BLUE_C)
        self.graph = graph
        graph_label = self.get_graph_label(
            graph, "M(t) = 2^t",
            direction = LEFT,
        )
        label_group = self.get_label_group(example_t)
        v_line, brace, height_label, ss_group, slope_label = label_group
        self.animate_secant_slope_group_change(
            ss_group,
            target_dx = 1,
            run_time = 0
        )
        self.remove(ss_group)

        #Draw graph and revert to tangent
        self.play(ShowCreation(graph))
        self.play(Write(graph_label))
        self.wait()
        self.play(Write(ss_group))
        self.wait()
        for target_dx in 0.01, 1, 0.01:
            self.animate_secant_slope_group_change(
                ss_group,
                target_dx = target_dx
            )
            self.wait()

        #Mark up with values

        self.play(ShowCreation(v_line))
        self.play(
            GrowFromCenter(brace),
            Write(height_label, run_time = 1)
        )
        self.wait()
        self.play(
            FadeIn(
                slope_label, 
                run_time = 4,
                lag_ratio = 0.5
            ),
            ReplacementTransform(
                height_label.copy(),
                slope_label.get_part_by_tex("2^")
            )
        )
        self.wait()

        #Vary value
        threes = VGroup(height_label[1], slope_label[2][1])
        ts = VGroup(*[
            TexMobject("t").set_color(YELLOW).scale(0.75).move_to(three)
            for three in threes
        ])
        self.play(Transform(threes, ts))

        alt_example_t = example_t+1
        def update_label_group(group, alpha):
            t = interpolate(example_t, alt_example_t, alpha)
            new_group = self.get_label_group(t)
            Transform(group, new_group).update(1)
            for t, three in zip(ts, threes):
                t.move_to(three)
            Transform(threes, ts).update(1)
            return group

        self.play(UpdateFromAlphaFunc(
            label_group, update_label_group,
            run_time = 3,
        ))
        self.play(UpdateFromAlphaFunc(
            label_group, update_label_group,
            run_time = 3,
            rate_func = lambda t : 1 - 1.5*smooth(t)
        ))

    def get_label_group(self, t):
        graph = self.graph

        v_line = self.get_vertical_line_to_graph(
            t, graph,
            color = YELLOW,
        )
        brace = Brace(v_line, RIGHT)
        height_label = brace.get_text("$2^%d$"%t)

        ss_group = self.get_secant_slope_group(
            t, graph, dx = 0.01,
            df_label = "dM",
            dx_label = "dt",
            dx_line_color = GREEN,
            secant_line_color = RED,
        )
        slope_label = TexMobject(
            "\\text{Slope}", "=", 
            "2^%d"%t,
            "(%.7f\\dots)"%np.log(2)
        )
        slope_label.next_to(
            ss_group.secant_line.point_from_proportion(0.65),
            DOWN+RIGHT,
            buff = 0
        )
        slope_label.set_color_by_tex("Slope", RED)
        return VGroup(
            v_line, brace, height_label,
            ss_group, slope_label
        )

class SimpleGraphOfTwoToT(GraphOfTwoToT):
    CONFIG = {
        "x_axis_label" : "",
        "y_axis_label" : "",
    }
    def construct(self):
        self.setup_axes()
        func = lambda t : 2**t
        graph = self.get_graph(func)
        line_pairs = VGroup()
        for x in 1, 2, 3, 4, 5:
            point = self.coords_to_point(x, func(x))
            x_axis_point = self.coords_to_point(x, 0)
            y_axis_point = self.coords_to_point(0, func(x))
            line_pairs.add(VGroup(
                DashedLine(x_axis_point, point),
                DashedLine(y_axis_point, point),
            ))


        self.play(ShowCreation(graph, run_time = 2))
        for pair in line_pairs:
            self.play(ShowCreation(pair))
        self.wait()

class FakeDiagram(TeacherStudentsScene):
    def construct(self):
        gs = GraphScene(skip_animations = True)
        gs.setup_axes()
        background_graph, foreground_graph = graphs = VGroup(*[
            gs.get_graph(
                lambda t : np.log(2)*2**t,
                x_min = -8,
                x_max = 2 + dx
            )
            for dx in (0.25, 0)
        ])
        for graph in graphs:
            end_point = graph.points[-1]
            axis_point = end_point[0]*RIGHT + gs.graph_origin[1]*UP
            for alpha in np.linspace(0, 1, 20):
                point = interpolate(axis_point, graph.points[0], alpha)
                graph.add_line_to(point)
            graph.set_stroke(width = 1)
            graph.set_fill(opacity = 1)
            graph.set_color(BLUE_D)
        background_graph.set_color(YELLOW)
        background_graph.set_stroke(width = 0.5)

        graphs.next_to(self.teacher, UP+LEFT, LARGE_BUFF)
        two_to_t = TexMobject("2^t")
        two_to_t.next_to(
            foreground_graph.get_corner(DOWN+RIGHT), UP+LEFT
        )
        corner_line = Line(*[
            graph.get_corner(DOWN+RIGHT)
            for graph in graphs
        ])
        dt_brace = Brace(corner_line, DOWN, buff = SMALL_BUFF)
        dt = dt_brace.get_text("$dt$")

        side_brace = Brace(graphs, RIGHT, buff = SMALL_BUFF)
        deriv = side_brace.get_text("$\\frac{d(2^t)}{dt}$")

        circle = Circle(color = RED)
        circle.replace(deriv, stretch = True)
        circle.scale_in_place(1.5)

        words = TextMobject("Not a real explanation")
        words.to_edge(UP)
        arrow = Arrow(words.get_bottom(), two_to_t.get_corner(UP+LEFT))
        arrow.set_color(WHITE)

        diagram = VGroup(
            graphs, two_to_t, dt_brace, dt, 
            side_brace, deriv, circle,
            words, arrow
        )

        self.play(self.teacher.change_mode, "raise_right_hand")
        self.play(
            Animation(VectorizedPoint(graphs.get_right())),
            DrawBorderThenFill(foreground_graph),
            Write(two_to_t)
        )
        self.wait()
        self.play(
            ReplacementTransform(
                foreground_graph.copy(),
                background_graph,
            ),
            Animation(foreground_graph),
            Animation(two_to_t),
            GrowFromCenter(dt_brace),
            Write(dt)
        )
        self.play(GrowFromCenter(side_brace))
        self.play(Write(deriv, run_time = 2))
        self.wait()

        self.play(
            ShowCreation(circle),
            self.teacher.change_mode, "hooray"
        )
        self.change_student_modes(*["confused"]*3)
        self.play(
            Write(words),
            ShowCreation(arrow),
            self.teacher.change_mode, "shruggie"
        )
        self.wait(3)
        self.play(
            FadeOut(diagram),
            *[
                ApplyMethod(pi.change_mode, "plain")
                for pi in self.get_pi_creatures()
            ]
        )
        self.teacher_says(
            "More numerical \\\\ than visual..."
        )
        self.wait(2)

        self.diagram = diagram

class AnalyzeExponentRatio(PiCreatureScene):
    CONFIG = {
        "base" : 2,
        "base_str" : "2",
    }
    def construct(self):
        base_str = self.base_str

        func_def = TexMobject("M(", "t", ")", "= ", "%s^"%base_str, "t")
        func_def.to_corner(UP+LEFT)
        self.add(func_def)

        ratio = TexMobject(
            "{ {%s^"%base_str, "{t", "+", "dt}", "-", 
            "%s^"%base_str, "t}",
            "\\over \\,", "dt}"
        )
        ratio.shift(UP+LEFT)

        lhs = TexMobject("{dM", "\\over \\,", "dt}", "(", "t", ")", "=")
        lhs.next_to(ratio, LEFT)


        two_to_t_plus_dt = VGroup(*ratio[:4])
        two_to_t = VGroup(*ratio[5:7])
        two_to_t_two_to_dt = TexMobject(
            "%s^"%base_str, "t", 
            "%s^"%base_str, "{dt}"
        )
        two_to_t_two_to_dt.move_to(two_to_t_plus_dt, DOWN+LEFT)
        exp_prop_brace = Brace(two_to_t_two_to_dt, UP)

        one = TexMobject("1")
        one.move_to(ratio[5], DOWN)
        lp, rp = parens = TexMobject("()")
        parens.stretch(1.3, 1)
        parens.set_height(ratio.get_height())
        lp.next_to(ratio, LEFT, buff = 0)
        rp.next_to(ratio, RIGHT, buff = 0)

        extracted_two_to_t = TexMobject("%s^"%base_str, "t")
        extracted_two_to_t.next_to(lp, LEFT, buff = SMALL_BUFF)

        expressions = [
            ratio, two_to_t_two_to_dt, 
            extracted_two_to_t, lhs, func_def
        ]
        for expression in expressions:
            expression.set_color_by_tex("t", YELLOW)
            expression.set_color_by_tex("dt", GREEN)

        #Apply exponential property
        self.play(
            Write(ratio), Write(lhs),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.wait(2)
        self.play(
            two_to_t_plus_dt.next_to, exp_prop_brace, UP,
            self.pi_creature.change_mode, "pondering"
        )
        self.play(
            ReplacementTransform(
                two_to_t_plus_dt.copy(), two_to_t_two_to_dt,
                run_time = 2,
                path_arc = np.pi,
            ),
            FadeIn(exp_prop_brace)
        )
        self.wait(2)

        #Talk about exponential property
        add_exp_rect, mult_rect = rects = [
            Rectangle(
                stroke_color = BLUE,
                stroke_width = 2,
            ).replace(mob).scale_in_place(1.1)
            for mob in [
                VGroup(*two_to_t_plus_dt[1:]),
                two_to_t_two_to_dt
            ]
        ]
        words = VGroup(*[
            TextMobject(s, " ideas")
            for s in ("Additive", "Multiplicative")
        ])
        words[0].move_to(words[1], LEFT)
        words.set_color(BLUE)
        words.next_to(two_to_t_plus_dt, RIGHT, buff = 1.5*LARGE_BUFF)
        arrows = VGroup(*[
            Arrow(word.get_left(), rect, color = words.get_color())
            for word, rect in zip(words, rects)
        ])

        self.play(ShowCreation(add_exp_rect))
        self.wait()
        self.play(ReplacementTransform(
            add_exp_rect.copy(), mult_rect
        ))
        self.wait()
        self.change_mode("happy")
        self.play(Write(words[0], run_time = 2))
        self.play(ShowCreation(arrows[0]))
        self.wait()
        self.play(
            Transform(*words),
            Transform(*arrows),
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [
            words[0], arrows[0], add_exp_rect, mult_rect,
            two_to_t_plus_dt, exp_prop_brace,
        ])))

        #Factor out 2^t
        self.play(*[
            FadeIn(
                mob,
                run_time = 2,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            )
            for mob in (one, lp, rp)
        ] + [
            ReplacementTransform(
                mob, extracted_two_to_t,
                path_arc = np.pi/2,
                run_time = 2,
            )
            for mob in (two_to_t, VGroup(*two_to_t_two_to_dt[:2]))
        ] + [
            lhs.next_to, extracted_two_to_t, LEFT
        ])
        self.change_mode("pondering")
        shifter = VGroup(ratio[4], one, *two_to_t_two_to_dt[2:])
        stretcher = VGroup(lp, ratio[7], rp)
        self.play(
            shifter.next_to, ratio[7], UP,
            stretcher.stretch_in_place, 0.9, 0
        )
        self.wait(2)

        #Ask about dt -> 0
        brace = Brace(VGroup(extracted_two_to_t, ratio), DOWN)
        alt_brace = Brace(parens, DOWN)
        dt_to_zero = TexMobject("dt", "\\to 0")
        dt_to_zero.set_color_by_tex("dt", GREEN)
        dt_to_zero.next_to(brace, DOWN)

        self.play(GrowFromCenter(brace))
        self.play(Write(dt_to_zero))
        self.wait(2)

        #Who cares
        randy = Randolph()
        randy.scale(0.7)
        randy.to_edge(DOWN)

        self.play(
            FadeIn(randy),
            self.pi_creature.change_mode, "plain",
        )
        self.play(PiCreatureSays(
            randy, "Who cares?", 
            bubble_kwargs = {"direction" : LEFT},
            target_mode = "angry",
        ))
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(randy),
            FadeOut(randy),
            self.pi_creature.change_mode, "hooray",
            self.pi_creature.look_at, parens
        )
        self.play(
            Transform(brace, alt_brace),
            dt_to_zero.next_to, alt_brace, DOWN
        )
        self.wait()

        #Highlight separation
        rects = [
            Rectangle(
                stroke_color = color,
                stroke_width = 2,
            ).replace(mob, stretch = True).scale_in_place(1.1)
            for mob, color in [
                (VGroup(parens, dt_to_zero), GREEN), 
                (extracted_two_to_t, YELLOW),
            ]
        ]
        self.play(ShowCreation(rects[0]))
        self.wait(2)
        self.play(ReplacementTransform(rects[0].copy(), rects[1]))
        self.change_mode("happy")
        self.wait()
        self.play(*list(map(FadeOut, rects)))

        #Plug in specific values
        static_constant = self.try_specific_dt_values()
        constant = static_constant.copy()

        #Replace with actual constant
        limit_term = VGroup(
            brace, dt_to_zero, ratio[4], one, rects[0],
            *ratio[7:]+two_to_t_two_to_dt[2:]
        )
        self.play(FadeIn(rects[0]))
        self.play(limit_term.to_corner, DOWN+LEFT)
        self.play(
            lp.stretch, 0.5, 1,
            lp.stretch, 0.8, 0,
            lp.next_to, extracted_two_to_t[0], RIGHT,
            rp.stretch, 0.5, 1,
            rp.stretch, 0.8, 0,
            rp.next_to, lp, RIGHT, SMALL_BUFF,
            rp.shift, constant.get_width()*RIGHT,
            constant.next_to, extracted_two_to_t[0], RIGHT, MED_LARGE_BUFF
        )
        self.wait()
        self.change_mode("confused")
        self.wait()

        #Indicate distinction between dt group and t group again
        for mob in limit_term, extracted_two_to_t:
            self.play(FocusOn(mob))
            self.play(Indicate(mob))
        self.wait()

        #hold_final_value
        derivative = VGroup(
            lhs, extracted_two_to_t, parens, constant
        )
        func_def_rhs = VGroup(*func_def[-2:]).copy()
        func_lp, func_rp = func_parens = TexMobject("()")
        func_parens.set_fill(opacity = 0)
        func_lp.next_to(func_def_rhs[0], LEFT, buff = 0)
        func_rp.next_to(func_lp, RIGHT, buff = func_def_rhs.get_width())
        func_def_rhs.add(func_parens)
        M = lhs[0][1]

        self.play(
            FadeOut(M),
            func_def_rhs.move_to, M, LEFT,
            func_def_rhs.set_fill, None, 1,
        )
        lhs[0].submobjects[1] = func_def_rhs
        self.wait()
        self.play(
            derivative.next_to, self.pi_creature, UP,
            derivative.to_edge, RIGHT,
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.wait(2)
        for mob in extracted_two_to_t, constant:
            self.play(Indicate(mob))
            self.wait()
        self.wait(2)

    def try_specific_dt_values(self):
        expressions = []
        for num_zeros in [1, 2, 4, 7]:
            dt_str = "0." + num_zeros*"0" + "1"
            dt_num = float(dt_str)
            output_num = (self.base**dt_num - 1) / dt_num
            output_str = "%.7f\\dots"%output_num

            expression = TexMobject(
                "{%s^"%self.base_str, "{%s}"%dt_str, "-1", 
                "\\over \\,", "%s}"%dt_str, 
                "=", output_str
            )
            expression.set_color_by_tex(dt_str, GREEN)
            expression.set_color_by_tex(output_str, BLUE)
            expression.to_corner(UP+RIGHT)
            expressions.append(expression)

        curr_expression = expressions[0]
        self.play(
            Write(curr_expression),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait(2)
        for expression in expressions[1:]:
            self.play(Transform(curr_expression, expression))
            self.wait(2)
        return curr_expression[-1]

class ExponentRatioWithThree(AnalyzeExponentRatio):
    CONFIG = {
        "base" : 3,
        "base_str" : "3",
    }

class ExponentRatioWithSeven(AnalyzeExponentRatio):
    CONFIG = {
        "base" : 7,
        "base_str" : "7",
    }

class ExponentRatioWithEight(AnalyzeExponentRatio):
    CONFIG = {
        "base" : 8,
        "base_str" : "8",
    }

class ExponentRatioWithE(AnalyzeExponentRatio):
    CONFIG = {
        "base" : np.exp(1),
        "base_str" : "e",
    }

class CompareTwoConstantToEightConstant(PiCreatureScene):
    def construct(self):
        two_deriv, eight_deriv = derivs = VGroup(*[
            self.get_derivative_expression(base)
            for base in (2, 8)
        ])

        derivs.arrange(
            DOWN, buff = 1.5, aligned_edge = LEFT
        )
        derivs.to_edge(LEFT, LARGE_BUFF).shift(UP)
        arrow = Arrow(*[deriv[-2] for deriv in derivs])
        times_three = TexMobject("\\times 3")
        times_three.next_to(arrow, RIGHT)

        why = TextMobject("Why?")
        why.next_to(self.pi_creature, UP, MED_LARGE_BUFF)

        self.add(eight_deriv)
        self.wait()
        self.play(ReplacementTransform(
            eight_deriv.copy(),
            two_deriv
        ))
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(
            Write(times_three),
            self.pi_creature.change_mode, "thinking"
        )
        self.wait(3)

        self.play(
            Animation(derivs),
            Write(why),
            self.pi_creature.change, "confused", derivs
        )
        self.wait()
        for deriv in derivs:
            for index in -5, -2:
                self.play(Indicate(deriv[index]))
            self.wait()
        self.wait(2)

    def get_derivative_expression(self, base):
        base_str = str(base)
        const_str = "%.4f\\dots"%np.log(base)
        result = TexMobject(
            "{d(", base_str, "^t", ")", "\\over", "dt}", 
            "=", base_str, "^t", "(", const_str, ")"
        )
        tex_color_paris = [
            ("t", YELLOW), 
            ("dt", GREEN), 
            (const_str, BLUE)
        ]
        for tex, color in tex_color_paris:
            result.set_color_by_tex(tex, color)
        return result

    def create_pi_creature(self):
        self.pi_creature = Randolph().flip()
        self.pi_creature.to_edge(DOWN).shift(3*RIGHT)
        return self.pi_creature

class AskAboutConstantOne(TeacherStudentsScene):
    def construct(self):
        note = TexMobject(
            "{ d(a^", "t", ")", "\\over \\,", "dt}", 
            "=", "a^", "t", "(\\text{Some constant})"
        )
        note.set_color_by_tex("t", YELLOW)
        note.set_color_by_tex("dt", GREEN)
        note.set_color_by_tex("constant", BLUE)
        note.to_corner(UP+LEFT)
        self.add(note)

        self.student_says(
            "Is there a base where\\\\",
            "that constant is 1?"
        )
        self.change_student_modes(
            "pondering", "raise_right_hand", "thinking",
            # look_at_arg = self.get_students()[1].bubble
        )
        self.wait(2)
        self.play(FadeOut(note[-1], run_time = 3))
        self.wait()

        self.teacher_says(
            "There is!\\\\",
            "$e = 2.71828\\dots$",
            target_mode = "hooray"
        )
        self.change_student_modes(*["confused"]*3)
        self.wait(3)

class WhyPi(PiCreatureScene):
    def construct(self):
        circle = Circle(radius = 1, color = MAROON_B)
        circle.rotate(np.pi/2)
        circle.to_edge(UP)
        ghost_circle = circle.copy()
        ghost_circle.set_stroke(width = 1)
        diam = Line(circle.get_left(), circle.get_right())
        diam.set_color(YELLOW)
        one = TexMobject("1")
        one.next_to(diam, UP)
        circum = diam.copy()
        circum.set_color(circle.get_color())
        circum.scale(np.pi)
        circum.next_to(circle, DOWN, LARGE_BUFF)
        circum.insert_n_curves(circle.get_num_curves()-2)
        circum.make_jagged()
        pi = TexMobject("\\pi")
        pi.next_to(circum, UP)
        why = TextMobject("Why?")
        why.next_to(self.pi_creature, UP, MED_LARGE_BUFF)

        self.add(ghost_circle, circle, diam, one)
        self.wait()
        self.play(Transform(circle, circum, run_time = 2))
        self.play(
            Write(pi),
            Write(why),
            self.pi_creature.change_mode, "confused",
        )
        self.wait(3)


    #######

    def create_pi_creature(self):
        self.pi_creature = Randolph()
        self.pi_creature.to_corner(DOWN+LEFT)
        return self.pi_creature

class GraphOfExp(GraphScene):
    CONFIG = {
        "x_min" : -3,
        "x_max" : 3,
        "x_tick_frequency" : 1,
        "x_axis_label" : "t",
        "x_labeled_nums" : list(range(-3, 4)),
        "x_axis_width" : 11,
        "graph_origin" : 2*DOWN + LEFT,
        "example_inputs" : [1, 2],
        "small_dx" : 0.01,
    }
    def construct(self):
        self.setup_axes()
        self.show_slopes()

    def show_slopes(self):
        graph = self.get_graph(np.exp)
        graph_label = self.get_graph_label(
            graph, "e^t", direction = LEFT
        )
        graph_label.shift(MED_SMALL_BUFF*LEFT)

        start_input, target_input = self.example_inputs
        ss_group = self.get_secant_slope_group(
            start_input, graph,
            dx = self.small_dx,
            dx_label = "dt",
            df_label = "d(e^t)",
            secant_line_color = YELLOW,
        )
        v_lines = [
            self.get_vertical_line_to_graph(
                x, graph, 
                color = WHITE,
            )
            for x in self.example_inputs
        ]
        height_labels = [
            TexMobject("e^%d"%x).next_to(vl, RIGHT, SMALL_BUFF)
            for vl, x in zip(v_lines, self.example_inputs)
        ]
        slope_labels = [
            TextMobject(
                "Slope = $e^%d$"%x
            ).next_to(vl.get_top(), UP+RIGHT).shift(0.7*RIGHT/x)
           for vl, x in zip(v_lines, self.example_inputs)
        ]

        self.play(
            ShowCreation(graph, run_time = 2),
            Write(
                graph_label, 
                rate_func = squish_rate_func(smooth, 0.5, 1),
            )
        )
        self.wait()
        self.play(*list(map(ShowCreation, ss_group)))
        self.play(Write(slope_labels[0]))
        self.play(ShowCreation(v_lines[0]))
        self.play(Write(height_labels[0]))
        self.wait(2)
        self.animate_secant_slope_group_change(
            ss_group,
            target_x = target_input,
            run_time = 2,
            added_anims = [
                Transform(
                    *pair, 
                    path_arc = np.pi/6,
                    run_time = 2
                )
                for pair in [
                    slope_labels,
                    v_lines,
                    height_labels,
                ]
            ]
        )
        self.wait(2)

        self.graph = graph
        self.ss_group = ss_group

class Chapter4Wrapper(Scene):
    def construct(self):
        title = TextMobject("Chapter 4 chain rule intuition")
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9)
        rect.set_height(1.5*FRAME_Y_RADIUS)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait(3)

class ApplyChainRule(TeacherStudentsScene):
    def construct(self):
        deriv_equation = TexMobject(
            "{d(", "e^", "{3", "t}", ")", "\\over", "dt}",
            "=", "3", "e^", "{3", "t}",
        )
        deriv_equation.next_to(self.teacher, UP+LEFT)
        deriv_equation.shift(UP)
        deriv_equation.set_color_by_tex("3", BLUE)
        deriv = VGroup(*deriv_equation[:7])
        exponent = VGroup(*deriv_equation[-2:])
        circle = Circle(color = YELLOW)
        circle.replace(exponent, stretch = True)
        circle.scale_in_place(1.5)

        self.teacher_says("Think of the \\\\ chain rule")
        self.change_student_modes(*["pondering"]*3)
        self.play(
            Write(deriv),
            RemovePiCreatureBubble(
                self.teacher,
                target_mode = "raise_right_hand"
            ),
        )
        self.wait(2)
        self.play(*[
            Transform(
                *deriv_equation.get_parts_by_tex(
                    tex, substring = False
                ).copy()[:2],
                path_arc = -np.pi,
                run_time = 2
            )
            for tex in ("e^", "{3", "t}")
        ] + [
            Write(deriv_equation.get_part_by_tex("="))
        ])
        self.play(self.teacher.change_mode, "happy")
        self.wait()
        self.play(ShowCreation(circle))
        self.play(Transform(
            *deriv_equation.get_parts_by_tex("3").copy()[-1:-3:-1]
        ))
        self.play(FadeOut(circle))
        self.wait(3)

class ChainRuleIntuition(ThreeLinesChainRule):
    CONFIG = {
        "line_configs" : [
            {
                "func" : lambda t : t,
                "func_label" : "t",
                "triangle_color" : WHITE,
                "center_y" : 3,
                "x_min" : 0,
                "x_max" : 3,
                "numbers_to_show" : list(range(4)),
                "numbers_with_elongated_ticks" : list(range(4)),
                "tick_frequency" : 1,
            },
            {
                "func" : lambda t : 3*t,
                "func_label" : "3t",
                "triangle_color" : GREEN,
                "center_y" : 0.5,
                "x_min" : 0,
                "x_max" : 3,
                "numbers_to_show" : list(range(0, 4)),
                "numbers_with_elongated_ticks" : list(range(4)),
                "tick_frequency" : 1,
            },
            {
                "func" : lambda t : np.exp(3*t),
                "func_label" : "e^{3t}",
                "triangle_color" : BLUE,
                "center_y" : -2,
                "x_min" : 0,
                "x_max" : 10,
                "numbers_to_show" : list(range(0, 11, 3)),
                "numbers_with_elongated_ticks" : list(range(11)),
                "tick_frequency" : 1,
            },
        ],
        "example_x" : 0.4,
        "start_x" : 0.4,
        "max_x" : 0.6,
        "min_x" : 0.2,
    }
    def construct(self):
        self.introduce_line_group()
        self.nudge_x()

    def nudge_x(self):
        lines, labels = self.line_group
        def get_value_points():
            return [
                label[0].get_bottom()
                for label in labels
            ]
        starts = get_value_points()
        self.animate_x_change(self.example_x + self.dx, run_time = 0)
        ends = get_value_points()
        self.animate_x_change(self.example_x, run_time = 0)

        nudge_lines = VGroup()
        braces = VGroup()
        numbers = VGroup()
        for start, end, line, label, config in zip(starts, ends, lines, labels, self.line_configs):
            color = label[0].get_color()
            nudge_line = Line(start, end)
            nudge_line.set_stroke(color, width = 6)
            brace = Brace(nudge_line, DOWN, buff = SMALL_BUFF)
            brace.set_color(color)
            func_label = config["func_label"]
            if len(func_label) == 1:
                text = "$d%s$"%func_label
            else:
                text = "$d(%s)$"%func_label
            brace.text = brace.get_text(text, buff = SMALL_BUFF)
            brace.text.set_color(color)
            brace.add(brace.text)

            line.add(nudge_line)
            nudge_lines.add(nudge_line)
            braces.add(brace)
            numbers.add(line.numbers)
            line.remove(*line.numbers)
        dt_brace, d3t_brace, dexp3t_brace = braces

        self.play(*list(map(FadeIn, [nudge_lines, braces])))
        self.wait()
        for count in range(3):
            for dx in self.dx, 0:
                self.animate_x_change(
                    self.example_x + dx, 
                    run_time = 2
                )
        self.wait()

class WhyNaturalLogOf2ShowsUp(TeacherStudentsScene):
    def construct(self):
        self.add_e_to_the_three_t()
        self.show_e_to_log_2()

    def add_e_to_the_three_t(self):
        exp_c = self.get_exp_C("c")
        exp_c.next_to(self.teacher, UP+LEFT)

        self.play(
            FadeIn(
                exp_c, 
                run_time = 2, 
                lag_ratio = 0.5
            ),
            self.teacher.change, "raise_right_hand"
        )
        self.wait()
        self.look_at(4*LEFT + UP)
        self.wait(3)

        self.exp_c = exp_c

    def show_e_to_log_2(self):
        equation = TexMobject(
            "2", "^t", "= e^", "{\\ln(2)", "t}"
        )
        equation.move_to(self.exp_c)
        t_group = equation.get_parts_by_tex("t")
        non_t_group = VGroup(*equation)
        non_t_group.remove(*t_group)

        log_words = TextMobject("``$e$ to the ", "\\emph{what}", "equals 2?''")
        log_words.set_color_by_tex("what", BLUE)
        log_words.next_to(equation, UP+LEFT)
        log_words_arrow = Arrow(
            log_words.get_right(),
            equation.get_part_by_tex("ln(2)").get_corner(UP+LEFT),
            color = BLUE,
        )

        derivative = TexMobject(
            "\\ln(2)", "2", "^t", "=", "\\ln(2)", "e^", "{\\ln(2)", "t}"
        )
        derivative.move_to(equation)
        for tex_mob in equation, derivative:
            tex_mob.set_color_by_tex("ln(2)", BLUE)
            tex_mob.set_color_by_tex("t", YELLOW)
        derivative_arrow = Arrow(1.5*UP, ORIGIN, buff = 0)
        derivative_arrow.set_color(WHITE)
        derivative_arrow.next_to(
            derivative.get_parts_by_tex("="), UP
        )
        derivative_symbol = TextMobject("Derivative")
        derivative_symbol.next_to(derivative_arrow, RIGHT)

        self.play(
            Write(non_t_group),
            self.exp_c.next_to, equation, LEFT, 2*LARGE_BUFF,
            self.exp_c.to_edge, UP,
        )
        self.change_student_modes("confused", "sassy", "erm")
        self.play(
            Write(log_words),
            ShowCreation(
                log_words_arrow, 
                run_time = 2,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            )
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = log_words
        )
        self.wait(2)

        t_group.save_state()
        t_group.shift(UP)
        t_group.set_fill(opacity = 0)
        self.play(
            ApplyMethod(
                t_group.restore,
                run_time = 2,
                lag_ratio = 0.5,
            ),
            self.teacher.change_mode, "speaking"
        )
        self.wait(2)
        self.play(FocusOn(self.exp_c))
        self.play(Indicate(self.exp_c, scale_factor = 1.05))
        self.wait(2)

        self.play(
            equation.next_to, derivative_arrow, UP,
            equation.shift, MED_SMALL_BUFF*RIGHT,
            FadeOut(VGroup(log_words, log_words_arrow)),
            self.teacher.change_mode, "raise_right_hand",
        )
        self.play(
            ShowCreation(derivative_arrow),
            Write(derivative_symbol),
            Write(derivative)
        )
        self.wait(3)
        self.play(self.teacher.change_mode, "happy")
        self.wait(2)

        student = self.get_students()[1]
        ln = derivative.get_part_by_tex("ln(2)").copy()
        rhs = TexMobject("=%s"%self.get_log_str(2))
        self.play(
            ln.next_to, student, UP+LEFT, MED_LARGE_BUFF,
            student.change_mode, "raise_left_hand",
        )
        rhs.next_to(ln, RIGHT)
        self.play(Write(rhs))
        self.wait(2)


    ######

    def get_exp_C(self, C):
        C_str = str(C)
        result = TexMobject(
            "{d(", "e^", "{%s"%C_str, "t}", ")", "\\over", "dt}",
            "=", C_str, "e^", "{%s"%C_str, "t}",
        )
        result.set_color_by_tex(C_str, BLUE)
        result.C_str = C_str
        return result

    def get_a_to_t(self, a):
        a_str = str(a)
        log_str = self.get_log_str(a)
        result = TexMobject(
            "{d(", a_str, "^t", ")", "\\over", "dt}",
            "=", log_str, a_str, "^t"
        )
        result.set_color_by_tex(log_str, BLUE)
        return result

    def get_log_str(self, a):
        return "%.4f\\dots"%np.log(float(a))

class CompareWaysToWriteExponentials(GraphScene):
    CONFIG = {
        "y_max" : 50,
        "y_tick_frequency" : 5,
        "x_max" : 7,
    }
    def construct(self):
        self.setup_axes()
        bases = list(range(2, 7))
        graphs = [
            self.get_graph(lambda t : base**t, color = GREEN)
            for base in bases
        ]
        graph = graphs[0]

        a_to_t = TexMobject("a^t")
        a_to_t.move_to(self.coords_to_point(6, 45))

        cross = TexMobject("\\times")
        cross.set_color(RED)
        cross.replace(a_to_t, stretch = True)
        e_to_ct = TexMobject("e^", "{c", "t}")
        e_to_ct.set_color_by_tex("c", BLUE)
        e_to_ct.scale(1.5)
        e_to_ct.next_to(a_to_t, DOWN)

        equations = VGroup()
        for base in bases:
            log_str =  "%.4f\\dots"%np.log(base)
            equation = TexMobject(
                str(base), "^t", "=",
                "e^", "{(%s)"%log_str, "t}", 
            )
            equation.set_color_by_tex(log_str, BLUE)
            equation.scale(1.2)
            equations.add(equation)

        equation = equations[0]
        equations.next_to(e_to_ct, DOWN, LARGE_BUFF, LEFT)

        self.play(
            ShowCreation(graph),
            Write(
                a_to_t,
                rate_func = squish_rate_func(smooth, 0.5, 1) 
            ),
            run_time = 2
        )
        self.play(Write(cross, run_time = 2))
        self.play(Write(e_to_ct, run_time = 2))
        self.wait(2)
        self.play(Write(equation))
        self.wait(2)
        for new_graph, new_equation in zip(graphs, equations)[1:]:
            self.play(
                Transform(graph, new_graph),
                Transform(equation, new_equation)
            )
            self.wait(2)
        self.wait()

class ManyExponentialForms(TeacherStudentsScene):
    def construct(self):
        lhs = TexMobject("2", "^t")
        rhs_list = [
            TexMobject("=", "%s^"%tex, "{(%.5f\\dots)"%log, "t}")
            for tex, log in [
                ("e", np.log(2)),
                ("\\pi", np.log(2)/np.log(np.pi)),
                ("42", np.log(2)/np.log(42)),
            ]
        ]
        group = VGroup(lhs, *rhs_list)
        group.arrange(RIGHT)
        group.set_width(FRAME_WIDTH - LARGE_BUFF)
        group.next_to(self.get_pi_creatures(), UP, 2*LARGE_BUFF)
        for part in group:
            part.set_color_by_tex("t", YELLOW)
            const = part.get_part_by_tex("dots")
            if const:
                const.set_color(BLUE)
                brace = Brace(const, UP)
                log = brace.get_text(
                    "$\\log_{%s}(2)$"%part[1].get_tex_string()[:-1]
                )
                log.set_color(BLUE)
                part.add(brace, log)
        exp = VGroup(*rhs_list[0][1:4])
        rect = BackgroundRectangle(group)

        self.add(lhs, rhs_list[0])
        self.wait()
        for rhs in rhs_list[1:]:
            self.play(FadeIn(
                rhs, 
                run_time = 2,
                lag_ratio = 0.5,
            ))
            self.wait(2)
        self.wait()
        self.play(
            FadeIn(rect),
            exp.next_to, self.teacher, UP+LEFT,
            self.teacher.change, "raise_right_hand",
        )
        self.play(*[
            ApplyFunction(
                lambda m : m.shift(SMALL_BUFF*UP).set_color(RED),
                part,
                run_time = 2,
                rate_func = squish_rate_func(there_and_back, a, a+0.3)
            )
            for part, a in zip(exp[1], np.linspace(0, 0.7, len(exp[1])))
        ])
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = exp
        )
        self.wait(3)

class TooManySymbols(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Too symbol heavy!",
            target_mode = "pleading"
        )
        self.play(self.teacher.change_mode, "guilty")
        self.wait(3)

class TemperatureOverTimeOfWarmWater(GraphScene):
    CONFIG = {
        "x_min" : 0,
        "x_axis_label" : "$t$",
        "y_axis_label" : "Temperature",
        "T_room" : 4,
        "include_solution" : False,
    }
    def construct(self):
        self.setup_axes()
        graph = self.get_graph(
            lambda t : 3*np.exp(-0.3*t) + self.T_room,
            color = RED
        )
        h_line = DashedLine(*[
            self.coords_to_point(x, self.T_room)
            for x in (self.x_min, self.x_max)
        ])
        T_room_label = TexMobject("T_{\\text{room}}")
        T_room_label.next_to(h_line, LEFT)

        ode = TexMobject(
            "\\frac{d\\Delta T}{dt} = -k \\Delta T"
        )
        ode.to_corner(UP+RIGHT)

        solution = TexMobject(
            "\\Delta T(", "t", ") = e", "^{-k", "t}"
        )
        solution.next_to(ode, DOWN, MED_LARGE_BUFF)
        solution.set_color_by_tex("t", YELLOW)
        solution.set_color_by_tex("Delta", WHITE)

        delta_T_brace = Brace(graph, RIGHT)
        delta_T_label = TexMobject("\\Delta T")
        delta_T_group = VGroup(delta_T_brace, delta_T_label)
        def update_delta_T_group(group):
            brace, label = group
            v_line = Line(
                graph.points[-1],
                graph.points[-1][0]*RIGHT + h_line.get_center()[1]*UP
            )
            brace.set_height(v_line.get_height())
            brace.next_to(v_line, RIGHT, SMALL_BUFF)
            label.set_height(min(
                label.get_height(),
                brace.get_height()
            ))
            label.next_to(brace, RIGHT, SMALL_BUFF)

        self.add(ode)
        self.play(
            Write(T_room_label),
            ShowCreation(h_line, run_time = 2)
        )
        if self.include_solution:
            self.play(Write(solution))
        graph_growth = ShowCreation(graph, rate_func=linear)
        delta_T_group_update = UpdateFromFunc(
            delta_T_group, update_delta_T_group
        )
        self.play(
            GrowFromCenter(delta_T_brace),
            Write(delta_T_label),
        )
        self.play(graph_growth, delta_T_group_update, run_time = 15)
        self.wait(2)

class TemperatureOverTimeOfWarmWaterWithSolution(TemperatureOverTimeOfWarmWater):
    CONFIG = {
        "include_solution" : True
    }

class InvestedMoney(Scene):
    def construct(self):
        # cash_str = "\\$\\$\\$"
        cash_str = "M"
        equation = TexMobject(
            "{d", cash_str, "\\over", "dt}",
            "=", "(1 + r)", cash_str
        )
        equation.set_color_by_tex(cash_str, GREEN)
        equation.next_to(ORIGIN, LEFT)
        equation.to_edge(UP)

        arrow = Arrow(LEFT, RIGHT, color = WHITE)
        arrow.next_to(equation)

        solution = TexMobject(
            cash_str, "(", "t", ")", "=", "e^", "{(1+r)", "t}"
        )
        solution.set_color_by_tex("t", YELLOW)
        solution.set_color_by_tex(cash_str, GREEN)
        solution.next_to(arrow, RIGHT)

        cash = TexMobject("\\$")
        cash_pile = VGroup(*[
            cash.copy().shift(
                x*(1+MED_SMALL_BUFF)*cash.get_width()*RIGHT +\
                y*(1+MED_SMALL_BUFF)*cash.get_height()*UP
            )
            for x in range(40)
            for y in range(8)
        ])
        cash_pile.set_color(GREEN)
        cash_pile.center()
        cash_pile.shift(DOWN)

        anims = []
        cash_size = len(cash_pile)
        run_time = 10
        const = np.log(cash_size)/run_time
        for i, cash in enumerate(cash_pile):
            start_time = np.log(i+1)/const
            prop = start_time/run_time
            rate_func = squish_rate_func(
                smooth,
                np.clip(prop-0.5/run_time, 0, 1),
                np.clip(prop+0.5/run_time, 0, 1),
            )
            anims.append(GrowFromCenter(
                cash, rate_func = rate_func,
            ))

        self.add(equation)
        self.play(*anims, run_time = run_time)
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(Write(solution, run_time = 2))
        self.wait()
        self.play(FadeOut(cash_pile))
        self.play(*anims, run_time = run_time)
        self.wait()

class NaturalLog(Scene):
    def construct(self):
        expressions = VGroup(*list(map(self.get_expression, [2, 3, 7])))
        expressions.arrange(DOWN, buff = MED_SMALL_BUFF)
        expressions.to_edge(LEFT)

        self.play(FadeIn(
            expressions, 
            run_time = 3, 
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(
            expressions.set_fill, None, 1,
            run_time = 2,
            lag_ratio = 0.5
        )
        self.wait()
        for i in 0, 2, 1:
            self.show_natural_loggedness(expressions[i])

    def show_natural_loggedness(self, expression):
        base, constant = expression[1], expression[-3]

        log_constant, exp_constant = constant.copy(), constant.copy()
        log_base, exp_base = base.copy(), base.copy()
        log_equals, exp_equals = list(map(TexMobject, "=="))

        ln = TexMobject("\\ln(2)")
        log_base.move_to(ln[-2])        
        ln.remove(ln[-2])
        log_equals.next_to(ln, LEFT)
        log_constant.next_to(log_equals, LEFT)
        log_expression = VGroup(
            ln, log_constant, log_equals, log_base
        )

        e = TexMobject("e")
        exp_constant.scale(0.7)
        exp_constant.next_to(e, UP+RIGHT, buff = 0)
        exp_base.next_to(exp_equals, RIGHT)
        VGroup(exp_base, exp_equals).next_to(
            VGroup(e, exp_constant), RIGHT, 
            aligned_edge = DOWN
        )
        exp_expression = VGroup(
            e, exp_constant, exp_equals, exp_base
        )

        for group, vect in (log_expression, UP), (exp_expression, DOWN):
            group.to_edge(RIGHT)
            group.shift(vect)

        self.play(
            ReplacementTransform(base.copy(), log_base),
            ReplacementTransform(constant.copy(), log_constant),
            run_time = 2
        )
        self.play(Write(ln), Write(log_equals))
        self.wait()
        self.play(
            ReplacementTransform(
                log_expression.copy(),
                exp_expression,
                run_time = 2,
            )
        )
        self.wait(2)

        ln_a = expression[-1]
        self.play(
            FadeOut(expression[-2]),
            FadeOut(constant),
            ln_a.move_to, constant, LEFT,
            ln_a.set_color, BLUE
        )
        self.wait()
        self.play(*list(map(FadeOut, [log_expression, exp_expression])))
        self.wait()

    def get_expression(self, base):
        expression = TexMobject(
            "{d(", "%d^"%base, "t", ")", "\\over \\,", "dt}",
            "=", "%d^"%base, "t", "(%.4f\\dots)"%np.log(base),
        )
        expression.set_color_by_tex("t", YELLOW)
        expression.set_color_by_tex("dt", GREEN)
        expression.set_color_by_tex("\\dots", BLUE)

        brace = Brace(expression.get_part_by_tex("\\dots"), UP)
        brace_text = brace.get_text("$\\ln(%d)$"%base)
        for mob in brace, brace_text:
            mob.set_fill(opacity = 0)

        expression.add(brace, brace_text)
        return expression

class NextVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        this_video = series[3]
        next_video = series[4]
        brace = Brace(this_video, DOWN)
        this_video.save_state()
        this_video.set_color(YELLOW)

        this_tex = TexMobject(
            "{d(", "a^t", ") \\over dt} = ", "a^t", "\\ln(a)"
        )
        this_tex[1][1].set_color(YELLOW)
        this_tex[3][1].set_color(YELLOW)
        this_tex.next_to(brace, DOWN)

        next_tex = VGroup(*list(map(TextMobject, [
            "Chain rule", "Product rule", "$\\vdots$"
        ])))
        next_tex.arrange(DOWN)
        next_tex.next_to(brace, DOWN)
        next_tex.shift(
            next_video.get_center()[0]*RIGHT\
            -next_tex.get_center()[0]*RIGHT
        )

        self.add(series, brace, *this_tex[:3])
        self.change_student_modes(
            "confused", "pondering", "erm",
            look_at_arg = this_tex
        )
        self.play(ReplacementTransform(
            this_tex[1].copy(), this_tex[3]
        ))
        self.wait()
        self.play(
            Write(this_tex[4]),
            ReplacementTransform(
                this_tex[3][0].copy(),
                this_tex[4][3],
                path_arc = np.pi,
                remover = True
            )
        )
        self.wait(2)
        self.play(this_tex.replace, this_video)
        self.play(
            brace.next_to, next_video, DOWN,
            this_video.restore,
            Animation(this_tex),
            next_video.set_color, YELLOW,
            Write(next_tex),
            self.get_teacher().change_mode, "raise_right_hand"
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = next_tex
        )
        self.wait(3)

class ExpPatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali  Yahya",
            "Meshal  Alshammari",
            "CrypticSwarm    ",
            "Kathryn Schmiedicke",
            "Nathan Pellegrin",
            "Karan Bhargava", 
            "Justin Helps",
            "Ankit   Agarwal",
            "Yu  Jun",
            "Dave    Nicponski",
            "Damion  Kistler",
            "Juan    Benet",
            "Othman  Alikhan",
            "Justin Helps",
            "Markus  Persson",
            "Dan Buchoff",
            "Derek   Dai",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Mustafa Mahdi",
            "Daan Smedinga",
            "Jonathan Eppele",
            "Albert Nguyen",
            "Nils Schneider",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Guido   Gambardella",
            "Jerry   Ling",
            "Mark    Govea",
            "Vecht",
            "Shimin Kuang",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }

class Thumbnail(GraphOfTwoToT):
    CONFIG = {
        "x_axis_label" : "",
        "y_axis_label" : "",
        "x_labeled_nums" : None,
        "y_labeled_nums" : None,
        "y_max" : 32,
        "y_tick_frequency" : 4,
        "graph_origin" : 3*DOWN + 5*LEFT,
        "x_axis_width" : 12,
    }
    def construct(self):
        derivative = TexMobject(
            "\\frac{d(a^t)}{dt} =", "a^t \\ln(a)"
        )
        derivative[0][3].set_color(YELLOW)
        derivative[1][1].set_color(YELLOW)
        derivative[0][2].set_color(BLUE)
        derivative[1][0].set_color(BLUE)
        derivative[1][5].set_color(BLUE)
        derivative.scale(2)
        derivative.add_background_rectangle()
        derivative.to_corner(DOWN+RIGHT, buff = MED_SMALL_BUFF)

        # brace = Brace(Line(LEFT, RIGHT), UP)
        # brace.set_width(derivative[1].get_width())
        # brace.next_to(derivative[1], UP)
        # question = TextMobject("Why?")
        # question.scale(2.5)
        # question.next_to(brace, UP)

        # randy = Randolph()
        # randy.scale(1.3)
        # randy.next_to(ORIGIN, LEFT).to_edge(DOWN)
        # randy.change_mode("pondering")

        question = TextMobject("What is $e\\,$?")
        e = question[-2]
        e.scale(1.2, about_point = e.get_bottom())
        e.set_color(BLUE)
        question.scale(3)
        question.add_background_rectangle()
        question.to_edge(UP)
        # randy.look_at(question)

        self.setup_axes()
        graph = self.get_graph(np.exp)
        graph.set_stroke(YELLOW, 8)

        self.add(graph, question, derivative)




























