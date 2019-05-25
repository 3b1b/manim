import scipy
import math

from manimlib.imports import *
from old_projects.eoc.chapter1 import Car, MoveCar
from old_projects.eoc.chapter10 import derivative

#revert_to_original_skipping_status


########

class Introduce(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Next up is \\\\", "Taylor series")
        words.set_color_by_tex("Taylor", BLUE)
        derivs = VGroup(*[
            TexMobject(
                "{d", "^%d"%n, "f \\over dx", "^%d}"%n
            ).set_color_by_tex(str(n), YELLOW)
            for n in range(2, 5)
        ])
        derivs.next_to(self.teacher, UP, LARGE_BUFF)
        second_deriv = derivs[0]
        second_deriv.save_state()
        card_dot = Dot(radius = SMALL_BUFF)
        screen_rect = ScreenRectangle(height = 4)
        screen_rect.move_to(3*UP, UP)

        self.teacher_says(words, run_time = 2)
        taylor_series = words.get_part_by_tex("Taylor").copy()
        self.change_student_modes(*["happy"]*3)
        self.play(
            RemovePiCreatureBubble(
                self.teacher,
                target_mode = "raise_right_hand"
            ),
            taylor_series.next_to, screen_rect.copy(), UP,
            ShowCreation(screen_rect)
        )
        card_dot.move_to(taylor_series)
        card_dot.generate_target()
        card_dot.target.set_fill(opacity = 0)
        card_dot.target.to_edge(RIGHT, buff = MED_SMALL_BUFF)
        arrow = Arrow(
            taylor_series, card_dot.target,
            buff = MED_SMALL_BUFF,
            color = WHITE
        )
        self.play(FadeIn(second_deriv))
        self.wait(2)
        self.play(Transform(second_deriv, derivs[1]))
        self.wait(2)
        self.play(MoveToTarget(card_dot))
        self.play(ShowCreation(arrow))
        self.wait()
        self.play(Transform(second_deriv, derivs[2]))
        self.change_student_modes(*["erm"]*3)
        self.wait()
        self.play(second_deriv.restore)
        self.wait(2)

class SecondDerivativeGraphically(GraphScene):
    CONFIG = {
        "x1" : 0,
        "x2" : 4,
        "x3" : 8,
        "y" : 4,
        "deriv_color" : YELLOW,
        "second_deriv_color" : GREEN,
    }
    def construct(self):
        self.force_skipping()

        self.setup_axes()
        self.draw_f()
        self.show_derivative()
        self.write_second_derivative()
        self.show_curvature()

        self.revert_to_original_skipping_status()
        self.contrast_big_and_small_concavity()

    def draw_f(self):
        def func(x):
            return 0.1*(x-self.x1)*(x-self.x2)*(x-self.x3) + self.y

        graph = self.get_graph(func)
        graph_label = self.get_graph_label(graph, "f(x)")

        self.play(
            ShowCreation(graph, run_time = 2),
            Write(
                graph_label,
                run_time = 2,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            )
        )
        self.wait()

        self.graph = graph
        self.graph_label = graph_label

    def show_derivative(self):
        deriv = TexMobject("\\frac{df}{dx}")
        deriv.next_to(self.graph_label, DOWN, MED_LARGE_BUFF)
        deriv.set_color(self.deriv_color)
        ss_group = self.get_secant_slope_group(
            1, self.graph,
            dx = 0.01,
            secant_line_color = self.deriv_color
        )

        self.play(
            Write(deriv),
            *list(map(ShowCreation, ss_group))
        )
        self.animate_secant_slope_group_change(
            ss_group, target_x = self.x3,
            run_time = 5
        )
        self.wait()
        self.animate_secant_slope_group_change(
            ss_group, target_x = self.x2,
            run_time = 3
        )
        self.wait()

        self.ss_group = ss_group
        self.deriv = deriv

    def write_second_derivative(self):
        second_deriv = TexMobject("\\frac{d^2 f}{dx^2}")
        second_deriv.next_to(self.deriv, DOWN, MED_LARGE_BUFF)
        second_deriv.set_color(self.second_deriv_color)
        points = [
            self.input_to_graph_point(x, self.graph)
            for x in (self.x2, self.x3)
        ]
        words = TextMobject("Change to \\\\ slope")
        words.next_to(
            center_of_mass(points), UP, 1.5*LARGE_BUFF
        )
        arrows = [
            Arrow(words.get_bottom(), p, color = WHITE)
            for p in points
        ]

        self.play(Write(second_deriv))
        self.wait()
        self.play(
            Write(words),
            ShowCreation(
                arrows[0], 
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            run_time = 2
        )
        self.animate_secant_slope_group_change(
            self.ss_group, target_x = self.x3,
            run_time = 3,
            added_anims = [
                Transform(
                    *arrows, 
                    run_time = 3,
                    path_arc = 0.75*np.pi
                ),
            ]
        )
        self.play(FadeOut(arrows[0]))
        self.animate_secant_slope_group_change(
            self.ss_group, target_x = self.x2,
            run_time = 3,
        )

        self.second_deriv_words = words
        self.second_deriv = second_deriv

    def show_curvature(self):
        positive_curve, negative_curve = [
            self.get_graph(
                self.graph.underlying_function,
                x_min = x_min,
                x_max = x_max,
                color = color,
            ).set_stroke(width = 6)
            for x_min, x_max, color in [
                (self.x2, self.x3, PINK),
                (self.x1, self.x2, RED),
            ]
        ]
        dot = Dot()
        def get_dot_update_func(curve):
            def update_dot(dot):
                dot.move_to(curve.points[-1])
                return dot
            return update_dot

        self.play(
            ShowCreation(positive_curve, run_time = 3),
            UpdateFromFunc(dot, get_dot_update_func(positive_curve))
        )
        self.play(FadeOut(dot))
        self.wait()
        self.animate_secant_slope_group_change(
            self.ss_group, target_x = self.x3,
            run_time = 4,
            added_anims = [Animation(positive_curve)]
        )

        self.play(*list(map(FadeOut, [self.ss_group, positive_curve])))
        self.animate_secant_slope_group_change(
            self.ss_group, target_x = self.x1,
            run_time = 0
        )
        self.play(FadeIn(self.ss_group))
        self.play(
            ShowCreation(negative_curve, run_time = 3),
            UpdateFromFunc(dot, get_dot_update_func(negative_curve))
        )
        self.play(FadeOut(dot))
        self.animate_secant_slope_group_change(
            self.ss_group, target_x = self.x2,
            run_time = 4,
            added_anims = [Animation(negative_curve)]
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [
            self.graph, self.ss_group, 
            negative_curve, self.second_deriv_words
        ])))

    def contrast_big_and_small_concavity(self):
        colors = color_gradient([GREEN, WHITE], 3)
        x0, y0 = 4, 2
        graphs = [
            self.get_graph(func, color = color)
            for color, func in zip(colors, [
                lambda x : 5*(x - x0)**2 + y0,
                lambda x : 0.2*(x - x0)**2 + y0,
                lambda x : (x-x0) + y0,
            ])
        ]
        arg_rhs_list = [
            TexMobject("(", str(x0), ")", "=", str(rhs))
            for rhs in (10, 0.4, 0)
        ]
        for graph, arg_rhs in zip(graphs, arg_rhs_list):
            graph.ss_group = self.get_secant_slope_group(
                x0-1, graph, 
                dx = 0.001,
                secant_line_color = YELLOW
            )
            arg_rhs.move_to(self.second_deriv.get_center(), LEFT)
            graph.arg_rhs = arg_rhs
        graph = graphs[0]

        v_line = DashedLine(*[
            self.coords_to_point(x0, 0),
            self.coords_to_point(x0, y0),
        ])
        input_label = TexMobject(str(x0))
        input_label.next_to(v_line, DOWN)

        self.play(ShowCreation(graph, run_time = 2))
        self.play(
            Write(input_label),
            ShowCreation(v_line)
        )
        self.play(
            ReplacementTransform(
                input_label.copy(),
                graph.arg_rhs.get_part_by_tex(str(x0))
            ),
            self.second_deriv.next_to, graph.arg_rhs.copy(), LEFT, SMALL_BUFF,
            Write(VGroup(*[
                submob
                for submob in graph.arg_rhs
                if submob is not graph.arg_rhs.get_part_by_tex(str(x0))
            ]))
        )
        self.wait()
        self.play(FadeIn(graph.ss_group))
        self.animate_secant_slope_group_change(
            graph.ss_group, target_x = x0 + 1,
            run_time = 3,
        )
        self.play(FadeOut(graph.ss_group))
        self.wait()
        for new_graph in graphs[1:]:
            self.play(Transform(graph, new_graph))
            self.play(Transform(
                graph.arg_rhs,
                new_graph.arg_rhs,
            ))
            self.play(FadeIn(new_graph.ss_group))
            self.animate_secant_slope_group_change(
                new_graph.ss_group, target_x = x0 + 1,
                run_time = 3,
            )
            self.play(FadeOut(new_graph.ss_group))

class IntroduceNotation(TeacherStudentsScene):
    def construct(self):
        clunky_deriv = TexMobject(
            "{d", "\\big(", "{df", "\\over", "dx}", "\\big)",
            "\\over", "dx }"
        )
        over_index = clunky_deriv.index_of_part(
            clunky_deriv.get_parts_by_tex("\\over")[1]
        )
        numerator = VGroup(*clunky_deriv[:over_index])
        denominator = VGroup(*clunky_deriv[over_index+1:])


        rp = clunky_deriv.get_part_by_tex("(")
        lp = clunky_deriv.get_part_by_tex(")")
        dfs, overs, dxs = list(map(clunky_deriv.get_parts_by_tex, [
            "df", "over", "dx"
        ]))
        df_over_dx = VGroup(dfs[0], overs[0], dxs[0])
        d = clunky_deriv.get_part_by_tex("d")
        d_over_dx = VGroup(d, overs[1], dxs[1])

        d2f_over_dx2 = TexMobject("{d^2 f", "\\over", "dx", "^2}")
        d2f_over_dx2.set_color_by_tex("dx", YELLOW)

        for mob in clunky_deriv, d2f_over_dx2:
            mob.next_to(self.teacher, UP+LEFT)

        for mob in numerator, denominator:
            circle = Circle(color = YELLOW)
            circle.replace(mob, stretch = True)
            circle.scale_in_place(1.3)
            mob.circle = circle
        dx_to_zero = TexMobject("dx \\to 0")
        dx_to_zero.set_color(YELLOW)
        dx_to_zero.next_to(clunky_deriv, UP+LEFT)

        self.student_says(
            "What's that notation?",
            target_mode = "raise_left_hand"
        )
        self.change_student_modes("confused", "raise_left_hand", "confused")
        self.play(
            FadeIn(
                clunky_deriv,
                run_time = 2,
                lag_ratio = 0.5
            ),
            RemovePiCreatureBubble(self.get_students()[1]),
            self.teacher.change_mode, "raise_right_hand"
        )
        self.wait()
        self.play(ShowCreation(numerator.circle))
        self.wait()
        self.play(ReplacementTransform(
            numerator.circle,
            denominator.circle,
        ))
        self.wait()
        self.play(
            FadeOut(denominator.circle),
            Write(dx_to_zero),
            dxs.set_color, YELLOW
        )
        self.wait()
        self.play(
            FadeOut(dx_to_zero),
            *[ApplyMethod(pi.change, "plain") for pi in self.get_pi_creatures()]
        )
        self.play(
            df_over_dx.scale, dxs[1].get_height()/dxs[0].get_height(),
            df_over_dx.move_to, d_over_dx, RIGHT,
            FadeOut(VGroup(lp, rp)),
            d_over_dx.shift, 0.8*LEFT + 0.05*UP,
        )
        self.wait()
        self.play(*[
            ReplacementTransform(
                group,
                VGroup(d2f_over_dx2.get_part_by_tex(tex))
            )
            for group, tex in [
                (VGroup(d, dfs[0]), "d^2"),
                (overs, "over"),
                (dxs, "dx"),
                (VGroup(dxs[1].copy()), "^2}"),
            ]
        ])
        self.wait(2)
        self.student_says(
            "How does one... \\\\ read that?",
            student_index = 0,
        )
        self.play(self.teacher.change, "happy")
        self.wait(2)

class HowToReadNotation(GraphScene, ReconfigurableScene):
    CONFIG = {
        "x_max" : 5,
        "dx" : 0.4,
        "x" : 2,
        "graph_origin" : 2.5*DOWN + 5*LEFT,
    }
    def setup(self):
        for base in self.__class__.__bases__:
            base.setup(self)

    def construct(self):
        self.force_skipping()

        self.add_graph()
        self.take_two_steps()
        self.change_step_size()
        self.show_dfs()
        self.show_ddf()

        self.revert_to_original_skipping_status()
        self.show_proportionality_to_dx_squared()
        return

        self.write_second_derivative()

    def add_graph(self):
        self.setup_axes()
        graph = self.get_graph(lambda x : x**2)
        graph_label = self.get_graph_label(
            graph, "f(x)", 
            direction = LEFT,
            x_val = 3.3
        )
        self.add(graph, graph_label)

        self.graph = graph

    def take_two_steps(self):
        v_lines = [
            self.get_vertical_line_to_graph(
                self.x + i*self.dx, self.graph,
                line_class = DashedLine,
                color = WHITE
            )
            for i in range(3)
        ]
        braces = [
            Brace(VGroup(*v_lines[i:i+2]), buff = 0)
            for i in range(2)
        ]
        for brace in braces:
            brace.dx = TexMobject("dx")
            max_width = 0.7*brace.get_width()
            if brace.dx.get_width() > max_width:
                brace.dx.set_width(max_width)
            brace.dx.next_to(brace, DOWN, SMALL_BUFF)

        self.play(ShowCreation(v_lines[0]))
        self.wait()
        for brace, line in zip(braces, v_lines[1:]):
            self.play(
                ReplacementTransform(
                    VectorizedPoint(brace.get_corner(UP+LEFT)),
                    brace,
                ),
                Write(brace.dx, run_time = 1),
            )
            self.play(ShowCreation(line))
        self.wait()

        self.v_lines = v_lines
        self.braces = braces

    def change_step_size(self):
        self.transition_to_alt_config(dx = 0.6)
        self.transition_to_alt_config(dx = 0.01, run_time = 3)

    def show_dfs(self):
        dx_lines = VGroup()
        df_lines = VGroup()
        df_dx_groups = VGroup()
        df_labels = VGroup()
        for i, v_line1, v_line2 in zip(it.count(1), self.v_lines, self.v_lines[1:]):
            dx_line = Line(
                v_line1.get_bottom(),
                v_line2.get_bottom(),
                color = GREEN
            )
            dx_line.move_to(v_line1.get_top(), LEFT)
            dx_lines.add(dx_line)

            df_line = Line(
                dx_line.get_right(),
                v_line2.get_top(),
                color = YELLOW
            )
            df_lines.add(df_line)
            df_label = TexMobject("df_%d"%i)
            df_label.set_color(YELLOW)
            df_label.scale(0.8)
            df_label.next_to(df_line.get_center(), UP+LEFT, MED_LARGE_BUFF)
            df_arrow = Arrow(
                df_label.get_bottom(),
                df_line.get_center(),
                buff = SMALL_BUFF,
            )
            df_line.label = df_label
            df_line.arrow = df_arrow
            df_labels.add(df_label)

            df_dx_groups.add(VGroup(df_line, dx_line))

        for brace, dx_line, df_line in zip(self.braces, dx_lines, df_lines):
            self.play(
                VGroup(brace, brace.dx).next_to,
                dx_line, DOWN, SMALL_BUFF,
                FadeIn(dx_line),
            )
            self.play(ShowCreation(df_line))
            self.play(
                ShowCreation(df_line.arrow),
                Write(df_line.label)
            )
            self.wait(2)

        self.df_dx_groups = df_dx_groups
        self.df_labels = df_labels

    def show_ddf(self):
        df_dx_groups = self.df_dx_groups.copy()
        df_dx_groups.generate_target()
        df_dx_groups.target.arrange(
            RIGHT, 
            buff = MED_LARGE_BUFF,
            aligned_edge = DOWN
        )
        df_dx_groups.target.next_to(
            self.df_dx_groups, RIGHT, 
            buff = 3,
            aligned_edge = DOWN
        )

        df_labels = self.df_labels.copy()
        df_labels.generate_target()
        h_lines = VGroup()
        for group, label in zip(df_dx_groups.target, df_labels.target):
            label.next_to(group.get_right(), LEFT, SMALL_BUFF)
            width = df_dx_groups.target.get_width() + MED_SMALL_BUFF
            h_line = DashedLine(ORIGIN, width*RIGHT)
            h_line.move_to(
                group.get_corner(UP+RIGHT)[1]*UP + \
                df_dx_groups.target.get_right()[0]*RIGHT,
                RIGHT
            )
            h_lines.add(h_line)
            max_height = 0.8*group.get_height()
            if label.get_height() > max_height:
                label.set_height(max_height)


        ddf_brace = Brace(h_lines, LEFT, buff = SMALL_BUFF)
        ddf = ddf_brace.get_tex("d(df)", buff = SMALL_BUFF)
        ddf.scale(
            df_labels[0].get_height()/ddf.get_height(), 
            about_point = ddf.get_right()
        )
        ddf.set_color(MAROON_B)

        self.play(
            *list(map(MoveToTarget, [df_dx_groups, df_labels])),
            run_time = 2
        )
        self.play(ShowCreation(h_lines, run_time = 2))
        self.play(GrowFromCenter(ddf_brace))
        self.play(Write(ddf))
        self.wait(2)

        self.ddf = ddf

    def show_proportionality_to_dx_squared(self):
        ddf = self.ddf.copy()
        ddf.generate_target()
        ddf.target.next_to(self.ddf, UP, LARGE_BUFF)
        rhs = TexMobject(
            "\\approx", "(\\text{Some constant})", "(dx)^2"
        )
        rhs.scale(0.8)
        rhs.next_to(ddf.target, RIGHT)

        example_dx = TexMobject(
            "dx = 0.01 \\Rightarrow (dx)^2 = 0.0001"
        )
        example_dx.scale(0.8)
        example_dx.to_corner(UP+RIGHT)

        self.play(MoveToTarget(ddf))
        self.play(Write(rhs))
        self.wait()
        self.play(Write(example_dx))
        self.wait(2)
        self.play(FadeOut(example_dx))

        self.ddf = ddf
        self.dx_squared = rhs.get_part_by_tex("dx")

    def write_second_derivative(self):
        ddf_over_dx_squared = TexMobject(
            "{d(df)", "\\over", "(dx)^2}"
        )
        ddf_over_dx_squared.scale(0.8)
        ddf_over_dx_squared.move_to(self.ddf, RIGHT)
        ddf_over_dx_squared.set_color_by_tex("df", self.ddf.get_color())
        parens = VGroup(
            ddf_over_dx_squared[0][1],
            ddf_over_dx_squared[0][4],
            ddf_over_dx_squared[2][0],
            ddf_over_dx_squared[2][3],
        )

        right_shifter = ddf_over_dx_squared[0][0]
        left_shifter = ddf_over_dx_squared[2][4]

        exp_two = TexMobject("2")
        exp_two.set_color(self.ddf.get_color())
        exp_two.scale(0.5)
        exp_two.move_to(right_shifter.get_corner(UP+RIGHT), LEFT)
        exp_two.shift(MED_SMALL_BUFF*RIGHT)
        pre_exp_two = VGroup(ddf_over_dx_squared[0][2])

        self.play(
            Write(ddf_over_dx_squared.get_part_by_tex("over")),
            *[
                ReplacementTransform(
                    mob, 
                    ddf_over_dx_squared.get_part_by_tex(tex),
                    path_arc = -np.pi/2,                    
                )
                for mob, tex in [(self.ddf, "df"), (self.dx_squared, "dx")]
            ]
        )
        self.wait(2)
        self.play(FadeOut(parens))
        self.play(
            left_shifter.shift, 0.2*LEFT,
            right_shifter.shift, 0.2*RIGHT,
            ReplacementTransform(pre_exp_two, exp_two),
            ddf_over_dx_squared.get_part_by_tex("over").scale_in_place, 0.8
        )
        self.wait(2)

class Footnote(Scene):
    def construct(self):
        self.add(TextMobject("""
            Interestingly, there is a notion in math 
            called the ``exterior derivative'' which 
            treats this ``d'' as having a more independent 
            meaning, though it's less related to the 
            intuitions I've introduced in this series.
        """, alignment = ""))

class TrajectoryGraphScene(GraphScene):
    CONFIG = {
        "x_min" : 0,
        "x_max" : 10,
        "x_axis_label" : "t",
        "y_axis_label" : "s",
        # "func" : lambda x : 10*smooth(x/10.0),
        "func" : lambda t : 10*bezier([0, 0, 0, 1, 1, 1])(t/10.0),
        "color" : BLUE,
    }
    def construct(self):
        self.setup_axes()
        self.graph = self.get_graph(
            self.func,
            color = self.color
        )
        self.add(self.graph)

class SecondDerivativeAsAcceleration(Scene):
    CONFIG = {
        "car_run_time" : 6,
    }
    def construct(self):
        self.init_car_and_line()
        self.introduce_acceleration()
        self.show_functions()

    def init_car_and_line(self):
        line = Line(5.5*LEFT, 4.5*RIGHT)
        line.shift(2*DOWN)
        car = Car()
        car.move_to(line.get_left())
        self.add(line, car)
        self.car = car
        self.start_car_copy = car.copy()
        self.line = line

    def introduce_acceleration(self):
        a_words = TexMobject(
            "{d^2 s \\over dt^2}(t)",  "\\Leftrightarrow",
            "\\text{Acceleration}"
        )
        a_words.set_color_by_tex("d^2 s", MAROON_B)
        a_words.set_color_by_tex("Acceleration", YELLOW)
        a_words.to_corner(UP+RIGHT )
        self.add(a_words)
        self.show_car_movement()
        self.wait()

        self.a_words = a_words

    def show_functions(self):
        def get_deriv(n):
            return lambda x : derivative(
                s_scene.graph.underlying_function, x, n
            )
        s_scene = TrajectoryGraphScene()
        v_scene = TrajectoryGraphScene(
            func = get_deriv(1),
            color = GREEN,
            y_max = 4,
            y_axis_label = "v",
        )
        a_scene = TrajectoryGraphScene(
            func = get_deriv(2),
            color = MAROON_B,
            y_axis_label = "a",
            y_min = -2, 
            y_max = 2,
        )
        j_scene = TrajectoryGraphScene(
            func = get_deriv(3),
            color = PINK,
            y_axis_label = "j",
            y_min = -2, 
            y_max = 2,
        )
        s_graph, v_graph, a_graph, j_graph = graphs = [
            VGroup(*scene.get_top_level_mobjects())
            for scene in (s_scene, v_scene, a_scene, j_scene)
        ]
        for i, graph in enumerate(graphs):
            graph.set_height(FRAME_Y_RADIUS)
            graph.to_corner(UP+LEFT)
            graph.shift(i*DOWN/2.0)

        s_words = TexMobject(
            "s(t)", "\\Leftrightarrow", "\\text{Displacement}"
        )
        s_words.set_color_by_tex("s(t)", s_scene.graph.get_color())
        v_words = TexMobject(
            "\\frac{ds}{dt}(t)", "\\Leftrightarrow", 
            "\\text{Velocity}"
        )
        v_words.set_color_by_tex("ds", v_scene.graph.get_color())
        j_words = TexMobject(
            "\\frac{d^3 s}{dt^3}(t)", "\\Leftrightarrow", 
            "\\text{Jerk}"
        )
        j_words.set_color_by_tex("d^3", j_scene.graph.get_color())
        self.a_words.generate_target()
        words_group = VGroup(s_words, v_words, self.a_words.target, j_words)
        words_group.arrange(
            DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        words_group.to_corner(UP+RIGHT)
        j_graph.scale(0.3).next_to(j_words, LEFT)

        positive_rect = Rectangle()
        positive_rect.set_stroke(width = 0)
        positive_rect.set_fill(GREEN, 0.5)
        positive_rect.replace(
            Line(
                a_scene.coords_to_point(0, -1),
                a_scene.coords_to_point(5, 1),
            ),
            stretch = True
        )
        negative_rect = Rectangle()
        negative_rect.set_stroke(width = 0)
        negative_rect.set_fill(RED, 0.5)
        negative_rect.replace(
            Line(
                a_scene.coords_to_point(5, 1),
                a_scene.coords_to_point(10, -1),
            ),
            stretch = True
        )

        self.show_car_movement(
            MoveToTarget(self.a_words),
            FadeIn(s_words),
            FadeIn(s_graph),
        )
        self.play(
            s_graph.scale, 0.3,
            s_graph.next_to, s_words, LEFT
        )
        self.play(*list(map(FadeIn, [v_graph, v_words])) )
        self.wait(2)
        self.play(
            v_graph.scale, 0.3,
            v_graph.next_to, v_words, LEFT
        )
        self.wait(2)
        self.play(
            Indicate(self.a_words),
            FadeIn(a_graph),
        )
        self.wait()
        self.play(FadeIn(positive_rect))
        for x in range(2):
            self.show_car_movement(
                run_time = 3,
                rate_func = lambda t : smooth(t/2.0)
            )
            self.wait()
        self.play(FadeIn(negative_rect))
        self.wait()
        self.play(MoveCar(
            self.car, self.line.get_end(),
            run_time = 3,
            rate_func = lambda t : 2*smooth((t+1)/2.0) - 1
        ))
        self.wait()
        self.play(
            a_graph.scale, 0.3,
            a_graph.next_to, self.a_words, LEFT,
            *list(map(FadeOut, [positive_rect, negative_rect]))
        )
        self.play(
            FadeOut(self.car),
            FadeIn(j_words),
            FadeIn(j_graph),
            self.line.scale, 0.5, self.line.get_left(),
            self.line.shift, LEFT,
        )
        self.car.scale(0.5)
        self.car.move_to(self.line.get_start())
        self.play(FadeIn(self.car))
        self.show_car_movement()
        self.wait(2)

    ##########

    def show_car_movement(self, *added_anims, **kwargs):
        distance = get_norm(
            self.car.get_center() - self.start_car_copy.get_center()
        )
        if distance > 1:
            self.play(FadeOut(self.car))
            self.car.move_to(self.line.get_left())
            self.play(FadeIn(self.car))

        kwargs["run_time"] = kwargs.get("run_time", self.car_run_time)
        self.play(
            MoveCar(self.car, self.line.get_right(), **kwargs),
            *added_anims
        )

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("Chapter 10: Taylor series")
        title.to_edge(UP)
        rect = ScreenRectangle(height = 6)
        rect.next_to(title, DOWN)
        self.add(rect)
        self.play(Write(title))
        self.wait()

class Thumbnail(SecondDerivativeGraphically):
    CONFIG = {
        "graph_origin" : 5*LEFT + 3*DOWN,
        "x_axis_label" : "",
        "y_axis_label" : "",
    }
    def construct(self):
        self.setup_axes()
        self.force_skipping()
        self.draw_f()
        self.remove(self.graph_label)
        self.graph.set_stroke(GREEN, width = 8)

        tex = TexMobject("{d^n f", "\\over", "dx^n}")
        tex.set_color_by_tex("d^n", YELLOW)
        tex.set_color_by_tex("dx", BLUE)
        tex.set_height(4)
        tex.to_edge(UP)

        self.add(tex)


























