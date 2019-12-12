# -*- coding: utf-8 -*-

from manimlib.imports import *

from old_projects.uncertainty import Flash
from old_projects.WindingNumber import *


# Warning, this file uses ContinualChangingDecimal,
# which has since been been deprecated.  Use a mobject
# updater instead


class AltTeacherStudentsScene(TeacherStudentsScene):
    def setup(self):
        TeacherStudentsScene.setup(self)
        self.teacher.set_color(YELLOW_E)

###############


class IntroSceneWrapper(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs" : {
            "color" : YELLOW_E,
            "flip_at_start" : False,
            "height" : 2,
        },
        "default_pi_creature_start_corner" : DOWN+LEFT,
    }
    def construct(self):
        self.introduce_two_words()
        self.describe_main_topic()
        self.describe_meta_topic()

    def introduce_two_words(self):
        morty = self.pi_creature
        rect = ScreenRectangle(height = 5)
        rect.to_corner(UP+RIGHT)
        self.add(rect)

        h_line = Line(LEFT, RIGHT).scale(2)
        h_line.to_corner(UP+LEFT)
        h_line.shift(0.5*DOWN)

        main_topic, meta_topic = topics = VGroup(
            TextMobject("Main topic"),
            TextMobject("Meta topic"),
        )
        topics.next_to(morty, UP)
        topics.shift_onto_screen()

        self.play(
            morty.change, "raise_left_hand",
            FadeInFromDown(main_topic)
        )
        self.wait()
        self.play(
            morty.change, "raise_right_hand",
            main_topic.next_to, meta_topic.get_top(), UP, MED_SMALL_BUFF,
            FadeInFromDown(meta_topic)
        )
        self.wait()
        self.play(
            morty.change, "happy",
            main_topic.next_to, h_line, UP,
            meta_topic.set_fill, {"opacity" : 0.2},
        )
        self.play(ShowCreation(h_line))
        self.wait()

        self.set_variables_as_attrs(h_line, main_topic, meta_topic)

    def describe_main_topic(self):
        h_line = self.h_line
        morty = self.pi_creature
        main_topic = self.main_topic
        meta_topic = self.meta_topic

        solver = TextMobject("2d equation solver")
        solver.match_width(h_line)
        solver.next_to(h_line, DOWN)
        rainbow_solver1 = solver.copy()
        rainbow_solver2 = solver.copy()
        colors = ["RED", "ORANGE", "YELLOW", "GREEN", BLUE, "PURPLE", PINK]
        rainbow_solver1.set_color_by_gradient(*colors)
        rainbow_solver2.set_color_by_gradient(*reversed(colors))


        xy_equation = TexMobject("""
            \\left[\\begin{array}{c}
                ye^x \\\\
                \\sin(|xy|)
            \\end{array}\\right] = 
            \\left[\\begin{array}{c}
                y^2 \\\\
                3y
            \\end{array}\\right]
        """)
        # xy_equation.set_color_by_tex_to_color_map({
        #     "x" : BLUE,
        #     "y" : YELLOW
        # })
        xy_equation.scale(0.8)
        xy_equation.next_to(solver, DOWN, MED_LARGE_BUFF)

        z_equation = TexMobject("z", "^5", "+", "z", "+", "1", "=", "0")
        z_equation.set_color_by_tex("z", GREEN)
        z_equation.move_to(xy_equation, UP)

        zeta = TexMobject("\\zeta(s) = 0")
        zeta[2].set_color(GREEN)
        zeta.next_to(z_equation, DOWN, MED_LARGE_BUFF)

        self.play(Write(solver))
        self.play(
            LaggedStartMap(FadeIn, xy_equation, run_time = 1),
            morty.change, "pondering"
        )
        self.wait(2)
        self.play(
            FadeOut(xy_equation),
            FadeIn(z_equation)
        )
        self.wait()
        self.play(Write(zeta))
        self.wait()
        solver.save_state()
        for rainbow_solver in rainbow_solver1, rainbow_solver2:
            self.play(Transform(
                solver, rainbow_solver,
                run_time = 2,
                lag_ratio = 0.5
            ))
        self.play(solver.restore)
        self.wait()

        self.play(LaggedStartMap(
            FadeOut, VGroup(solver, z_equation, zeta)
        ))
        self.play(
            main_topic.move_to, meta_topic,
            main_topic.set_fill, {"opacity" : 0.2},
            meta_topic.move_to, main_topic,
            meta_topic.set_fill, {"opacity" : 1},
            morty.change, "hesitant",
            path_arc = TAU/8,
        )

    def describe_meta_topic(self):
        h_line = self.h_line
        morty = self.pi_creature

        words = TextMobject("Seek constructs which \\\\ compose nicely")
        words.scale(0.7)
        words.next_to(h_line, DOWN)

        self.play(Write(words))
        self.play(morty.change, "happy")
        self.wait(3)

class Introduce1DFunctionCase(Scene):
    CONFIG = {
        "search_range_rect_height" : 0.15,
        "arrow_opacity" : 1,
        "show_dotted_line_to_f" : True,
        "arrow_config": {
            "max_tip_length_to_length_ratio" : 0.5,
        },
        "show_midpoint_value" : True,
    }
    def construct(self):
        self.show_axes_one_at_a_time()
        self.show_two_graphs()
        self.transition_to_sqrt_2_case()
        self.show_example_binary_search()

    def show_axes_one_at_a_time(self):
        axes = Axes(
            x_min = -1, x_max = 3.2,
            x_axis_config = {
                "unit_size" : 3,
                "tick_frequency" : 0.25,
                "numbers_with_elongated_ticks" : list(range(-1, 4))
            },
            y_min = -2, y_max = 4.5,
        )
        axes.to_corner(DOWN+LEFT)
        axes.x_axis.add_numbers(*list(range(-1, 4)))
        axes.y_axis.label_direction = LEFT
        axes.y_axis.add_numbers(-1, *list(range(1, 5)))

        inputs = TextMobject("Inputs")
        inputs.next_to(axes.x_axis, UP, aligned_edge = RIGHT)

        outputs = TextMobject("Outputs")
        outputs.next_to(axes.y_axis, UP, SMALL_BUFF)

        self.play(
            ShowCreation(axes.x_axis),
            Write(inputs)
        )
        self.wait()
        self.play(
            ShowCreation(axes.y_axis),
            FadeOut(axes.x_axis.numbers[1], rate_func = squish_rate_func(smooth, 0, 0.2)),
            Write(outputs)
        )
        self.wait()

        self.axes = axes
        self.inputs_label = inputs
        self.outputs_label = outputs

    def show_two_graphs(self):
        axes = self.axes
        f_graph = axes.get_graph(
            lambda x : 2*x*(x - 0.75)*(x - 1.5) + 1,
            color = BLUE
        )
        g_graph = axes.get_graph(
            lambda x : 1.8*np.cos(TAU*x/2),
            color = YELLOW
        )

        label_x_corod = 2
        f_label = TexMobject("f(x)")
        f_label.match_color(f_graph)
        f_label.next_to(axes.input_to_graph_point(label_x_corod, f_graph), LEFT)

        g_label = TexMobject("g(x)")
        g_label.match_color(g_graph)
        g_label.next_to(
            axes.input_to_graph_point(label_x_corod, g_graph), UP, SMALL_BUFF
        )

        solution = 0.24
        cross_point = axes.input_to_graph_point(solution, f_graph)
        l_v_line, r_v_line, v_line = [
            DashedLine(
                axes.coords_to_point(x, 0),
                axes.coords_to_point(x, f_graph.underlying_function(solution)),
            )
            for x in (axes.x_min, axes.x_max, solution)
        ]

        equation = TexMobject("f(x)", "=", "g(x)")
        equation[0].match_color(f_label)
        equation[2].match_color(g_label)
        equation.next_to(cross_point, UP, buff = 1.5, aligned_edge = LEFT)
        equation_arrow = Arrow(
            equation.get_bottom(), cross_point,
            buff = SMALL_BUFF,
            color = WHITE
        )
        equation.target = TexMobject("x^2", "=", "2")
        equation.target.match_style(equation)
        equation.target.to_edge(UP)

        for graph, label in (f_graph, f_label), (g_graph, g_label):
            self.play(
                ShowCreation(graph),
                Write(label, rate_func = squish_rate_func(smooth, 0.5, 1)),
                run_time = 2
            )
        self.wait()
        self.play(
            ReplacementTransform(r_v_line.copy().fade(1), v_line),
            ReplacementTransform(l_v_line.copy().fade(1), v_line),
            run_time = 2
        )
        self.play(
            ReplacementTransform(f_label.copy(), equation[0]),
            ReplacementTransform(g_label.copy(), equation[2]),
            Write(equation[1]),
            GrowArrow(equation_arrow),
        )
        for x in range(4):
            self.play(
                FadeOut(v_line.copy()),
                ShowCreation(v_line, rate_func = squish_rate_func(smooth, 0.5, 1)),
                run_time = 1.5
            )
        self.wait()
        self.play(
            MoveToTarget(equation, replace_mobject_with_target_in_scene = True),
            *list(map(FadeOut, [equation_arrow, v_line]))
        )

        self.set_variables_as_attrs(
            f_graph, f_label, g_graph, g_label,
            equation = equation.target
        )

    def transition_to_sqrt_2_case(self):
        f_graph = self.f_graph
        f_label = VGroup(self.f_label)
        g_graph = self.g_graph
        g_label = VGroup(self.g_label)
        axes = self.axes
        for label in f_label, g_label:
            for x in range(2):
                label.add(VectorizedPoint(label.get_center()))
        for number in axes.y_axis.numbers:
            number.add_background_rectangle()

        squared_graph = axes.get_graph(lambda x : x**2)
        squared_graph.match_style(f_graph)
        two_graph = axes.get_graph(lambda x : 2)
        two_graph.match_style(g_graph)

        squared_label = TexMobject("f(x)", "=", "x^2")
        squared_label.next_to(
            axes.input_to_graph_point(2, squared_graph), RIGHT
        )
        squared_label.match_color(squared_graph)
        two_label = TexMobject("g(x)", "=", "2")
        two_label.next_to(
            axes.input_to_graph_point(3, two_graph), UP,
        )
        two_label.match_color(two_graph)

        find_sqrt_2 = self.find_sqrt_2 = TextMobject("(Find $\\sqrt{2}$)")
        find_sqrt_2.next_to(self.equation, DOWN)

        self.play(
            ReplacementTransform(f_graph, squared_graph),
            ReplacementTransform(f_label, squared_label),
        )
        self.play(
            ReplacementTransform(g_graph, two_graph),
            ReplacementTransform(g_label, two_label),
            Animation(axes.y_axis.numbers)
        )
        self.wait()
        self.play(Write(find_sqrt_2))
        self.wait()

        self.set_variables_as_attrs(
            squared_graph, two_graph,
            squared_label, two_label,
        )

    def show_example_binary_search(self):
        self.binary_search(
            self.squared_graph, self.two_graph,
            x0 = 1, x1 = 2,
            n_iterations = 8
        )

    ##

    def binary_search(
        self, 
        f_graph, g_graph, 
        x0, x1, 
        n_iterations,
        n_iterations_with_sign_mention = 0,
        zoom = False,
        ):

        axes = self.axes
        rect = self.rect = Rectangle()
        rect.set_stroke(width = 0)
        rect.set_fill(YELLOW, 0.5)
        rect.replace(Line(
            axes.coords_to_point(x0, 0),
            axes.coords_to_point(x1, 0),
        ), dim_to_match = 0)
        rect.stretch_to_fit_height(self.search_range_rect_height)

        #Show first left and right
        mention_signs = n_iterations_with_sign_mention > 0
        kwargs = {"mention_signs" : mention_signs}
        leftovers0 = self.compare_graphs_at_x(f_graph, g_graph, x0, **kwargs)
        self.wait()
        leftovers1 = self.compare_graphs_at_x(f_graph, g_graph, x1, **kwargs)
        self.wait()
        self.play(GrowFromCenter(rect))
        self.wait()

        all_leftovers = VGroup(leftovers0, leftovers1)
        end_points = [x0, x1]
        if mention_signs:
            sign_word0 = leftovers0.sign_word
            sign_word1 = leftovers1.sign_word

        midpoint_line = Line(MED_SMALL_BUFF*UP, ORIGIN, color = YELLOW)
        midpoint_line_update = UpdateFromFunc(
            midpoint_line, lambda l : l.move_to(rect)
        )
        decimal = DecimalNumber(
            0,
            num_decimal_places = 3,
            show_ellipsis = True,
        )
        decimal.scale(0.7)
        decimal_update = ChangingDecimal(
            decimal, lambda a : axes.x_axis.point_to_number(rect.get_center()),
            position_update_func = lambda m : m.next_to(
                midpoint_line, DOWN, SMALL_BUFF,
                submobject_to_align = decimal[:-1],
            ),
        )
        if not self.show_midpoint_value:
            decimal.set_fill(opacity = 0)
            midpoint_line.set_stroke(width = 0)

        #Restrict to by a half each time
        kwargs = {
            "mention_signs" : False,
            "show_decimal" : zoom,
        } 
        for x in range(n_iterations - 1):
            x_mid = np.mean(end_points)
            leftovers_mid = self.compare_graphs_at_x(f_graph, g_graph, x_mid, **kwargs)
            if leftovers_mid.too_high == all_leftovers[0].too_high:
                index_to_fade = 0
            else:
                index_to_fade = 1
            edge = [RIGHT, LEFT][index_to_fade]
            to_fade = all_leftovers[index_to_fade]
            all_leftovers.submobjects[index_to_fade] = leftovers_mid
            end_points[index_to_fade] = x_mid

            added_anims = []
            if mention_signs:
                word = [leftovers0, leftovers1][index_to_fade].sign_word
                if x < n_iterations_with_sign_mention:
                    added_anims = [word.next_to, leftovers_mid[0].get_end(), -edge]
                elif word in self.camera.extract_mobject_family_members(self.mobjects):
                    added_anims = [FadeOut(word)]

            rect.generate_target()
            rect.target.stretch(0.5, 0, about_edge = edge)
            rect.target.stretch_to_fit_height(self.search_range_rect_height)
            self.play(
                MoveToTarget(rect),
                midpoint_line_update,
                decimal_update,
                Animation(all_leftovers),
                FadeOut(to_fade),
                *added_anims
            )
            if zoom:
                factor = 2.0/rect.get_width()
                everything = VGroup(*self.mobjects)
                decimal_index = everything.submobjects.index(decimal)
                midpoint_line_index = everything.submobjects.index(midpoint_line)
                everything.generate_target()
                everything.target.scale(factor, about_point = rect.get_center())
                everything.target[decimal_index].scale(1./factor, about_edge = UP)
                everything.target[midpoint_line_index].scale(1./factor)
                if factor > 1:
                    self.play(
                        everything.scale, factor, 
                        {"about_point" : rect.get_center()}
                    )
            else:
                self.wait()

    def compare_graphs_at_x(
        self, f_graph, g_graph, x, 
        mention_signs = False,
        show_decimal = False,
        ):
        axes = self.axes
        f_point = axes.input_to_graph_point(x, f_graph)
        g_point = axes.input_to_graph_point(x, g_graph)
        arrow = Arrow(
            g_point, f_point, buff = 0,
            **self.arrow_config
        )
        too_high = f_point[1] > g_point[1]
        if too_high:
            arrow.set_fill(GREEN, opacity = self.arrow_opacity)
        else:
            arrow.set_fill(RED, opacity = self.arrow_opacity)

        leftovers = VGroup(arrow)
        leftovers.too_high = too_high

        if self.show_dotted_line_to_f:
            v_line = DashedLine(axes.coords_to_point(x, 0), f_point)
            self.play(ShowCreation(v_line))
            leftovers.add(v_line)

        added_anims = []
        if show_decimal:
            decimal = DecimalNumber(
                axes.x_axis.point_to_number(arrow.get_start()),
                num_decimal_places = 3,
                # show_ellipsis = True,
            )
            height = self.rect.get_height()
            decimal.set_height(height)
            next_to_kwargs = {
                "buff" : height,
            }
            if too_high:
                decimal.next_to(arrow, DOWN, **next_to_kwargs)
                if hasattr(self, "last_up_arrow_decimal"):
                    added_anims += [FadeOut(self.last_up_arrow_decimal)]
                self.last_up_arrow_decimal = decimal
            else:
                decimal.next_to(arrow, UP, **next_to_kwargs)
                if hasattr(self, "last_down_arrow_decimal"):
                    added_anims += [FadeOut(self.last_down_arrow_decimal)]
                self.last_down_arrow_decimal = decimal
            line = Line(decimal, arrow, buff = 0)
            # line.match_color(arrow)
            line.set_stroke(WHITE, 1)
            decimal.add(line)
            added_anims += [FadeIn(decimal)]

        if mention_signs:
            if too_high:
                sign_word = TextMobject("Positive")
                sign_word.set_color(GREEN)
                sign_word.scale(0.7)
                sign_word.next_to(arrow.get_end(), RIGHT)
            else:
                sign_word = TextMobject("Negative")
                sign_word.set_color(RED)
                sign_word.scale(0.7)
                sign_word.next_to(arrow.get_end(), LEFT)
            sign_word.add_background_rectangle()
            added_anims += [FadeIn(sign_word)]
            leftovers.sign_word = sign_word

        self.play(GrowArrow(arrow), *added_anims)

        return leftovers

class PiCreaturesAreIntrigued(AltTeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "You can extend \\\\ this to 2d",
            bubble_kwargs = {"width" : 4, "height" : 3}
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.look_at(self.screen)
        self.wait(3)

class TransitionFromEquationSolverToZeroFinder(Introduce1DFunctionCase):
    CONFIG = {
        "show_dotted_line_to_f" : False,
        "arrow_config" : {},
        "show_midpoint_value" : False,
    }
    def construct(self):
        #Just run through these without animating.
        self.force_skipping()
        self.show_axes_one_at_a_time()
        self.show_two_graphs()
        self.transition_to_sqrt_2_case()
        self.revert_to_original_skipping_status()
        ##

        self.transition_to_difference_graph()
        self.show_binary_search_with_signs()

    def transition_to_difference_graph(self):
        axes = self.axes
        equation = x_squared, equals, two = self.equation
        for s in "-", "0":
            tex_mob = TexMobject(s)
            tex_mob.scale(0.01)
            tex_mob.fade(1)
            tex_mob.move_to(equation.get_right())
            equation.add(tex_mob)
        find_sqrt_2 = self.find_sqrt_2
        rect = SurroundingRectangle(VGroup(equation, find_sqrt_2))
        rect.set_color(WHITE)

        f_graph = self.squared_graph
        g_graph = self.two_graph
        new_graph = axes.get_graph(
            lambda x : f_graph.underlying_function(x) - g_graph.underlying_function(x),
            color = GREEN
        )
        zero_graph = axes.get_graph(lambda x : 0)
        zero_graph.set_stroke(BLACK, 0)

        f_label = self.squared_label
        g_label = self.two_label
        new_label = TexMobject("f(x)", "-", "g(x)")
        new_label[0].match_color(f_label)
        new_label[2].match_color(g_label)
        new_label.next_to(
            axes.input_to_graph_point(2, new_graph),
            LEFT
        )

        fg_labels = VGroup(f_label, g_label)
        fg_labels.generate_target()
        fg_labels.target.arrange(DOWN, aligned_edge = LEFT)
        fg_labels.target.to_corner(UP+RIGHT)

        new_equation = TexMobject("x^2", "-", "2", "=", "0")
        new_equation[0].match_style(equation[0])
        new_equation[2].match_style(equation[2])
        new_equation.move_to(equation, RIGHT)
        for tex in equation, new_equation:
            tex.sort_alphabetically()

        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.play(
            ReplacementTransform(equation, new_equation, path_arc = TAU/4),
            find_sqrt_2.next_to, new_equation, DOWN,
        )
        self.play(MoveToTarget(fg_labels))
        self.play(
            ReplacementTransform(f_graph, new_graph),
            ReplacementTransform(g_graph, zero_graph),
        )
        self.play(
            ReplacementTransform(f_label[0].copy(), new_label[0]),
            ReplacementTransform(g_label[0].copy(), new_label[2]),
            Write(new_label[1]),
        )
        self.wait()

        self.set_variables_as_attrs(new_graph, zero_graph)

    def show_binary_search_with_signs(self):
        self.play(FadeOut(self.axes.x_axis.numbers[2]))
        self.binary_search(
            self.new_graph, self.zero_graph,
            1, 2,
            n_iterations = 9,
            n_iterations_with_sign_mention = 2,
            zoom = True,
        )

class RewriteEquationWithTeacher(AltTeacherStudentsScene):
    def construct(self):
        root_two_equations = VGroup(
            TexMobject("x^2", "", "=", "2", ""),
            TexMobject("x^2", "-", "2", "=", "0"),
        )
        for equation in root_two_equations:
            equation.sort_alphabetically()
            for part in equation.get_parts_by_tex("text"):
                part[2:-1].set_color(YELLOW)
                part[2:-1].scale(0.9)
            equation.move_to(self.hold_up_spot, DOWN)

        brace = Brace(root_two_equations[1], UP)
        f_equals_0 = brace.get_tex("f(x) = 0")

        self.teacher_holds_up(root_two_equations[0])
        self.wait()
        self.play(Transform(
            *root_two_equations, 
            run_time = 1.5,
            path_arc = TAU/2
        ))
        self.play(self.get_student_changes(*["pondering"]*3))
        self.play(
            GrowFromCenter(brace),
            self.teacher.change, "happy"
        )
        self.play(Write(f_equals_0))
        self.change_student_modes(*["happy"]*3)
        self.wait()

        #
        to_remove = VGroup(root_two_equations[0], brace, f_equals_0)
        two_d_equation = TexMobject("""
            \\left[\\begin{array}{c}
                ye^x \\\\
                \\sin(xy)
            \\end{array}\\right] = 
            \\left[\\begin{array}{c}
                y^2 + x^3 \\\\
                3y - x
            \\end{array}\\right]
        """)
        complex_equation = TexMobject("z", "^5 + ", "z", " + 1 = 0")
        z_def = TextMobject(
            "(", "$z$", " is complex, ", "$a + bi$", ")",
            arg_separator = ""
        )
        complex_group = VGroup(complex_equation, z_def)
        complex_group.arrange(DOWN)
        for tex in complex_group:
            tex.set_color_by_tex("z", GREEN)
        complex_group.move_to(self.hold_up_spot, DOWN)

        self.play(
            ApplyMethod(
                to_remove.next_to, FRAME_X_RADIUS*RIGHT, RIGHT,
                remover = True,
                rate_func = running_start,
                path_arc = -TAU/4,
            ),
            self.teacher.change, "hesitant",
            self.get_student_changes(*["erm"]*3)
        )
        self.teacher_holds_up(two_d_equation)
        self.change_all_student_modes("horrified")
        self.wait()
        self.play(
            FadeOut(two_d_equation),
            FadeInFromDown(complex_group),
        )
        self.change_all_student_modes("confused")
        self.wait(3)

class InputOutputScene(Scene):
    CONFIG = {
        "plane_width" : 6,
        "plane_height" : 6,
        "x_shift" : FRAME_X_RADIUS/2,
        "y_shift" : MED_LARGE_BUFF,
        "output_scalar" : 10,
        "non_renormalized_func" : plane_func_by_wind_spec(
            (-2, -1, 2), 
            (1, 1, 1), 
            (2, -2, -1),
        ),
    }

    ###

    def func(self, coord_pair):
        out_coords = np.array(self.non_renormalized_func(coord_pair))
        out_norm = get_norm(out_coords)
        if out_norm > 1:
            angle = angle_of_vector(out_coords)
            factor = 0.5-0.1*np.cos(4*angle)
            target_norm = factor*np.log(out_norm)
            out_coords *= target_norm / out_norm
        else:
            out_coords = (0, 0)
        return tuple(out_coords)

    def point_function(self, point):
        in_coords = self.input_plane.point_to_coords(point)
        out_coords = self.func(in_coords)
        return self.output_plane.coords_to_point(*out_coords)

    def get_colorings(self):
        in_cmos = ColorMappedObjectsScene(
            func = lambda p : self.non_renormalized_func(
                (p[0]+self.x_shift, p[1]+self.y_shift)
            )
        )
        scalar = self.output_scalar
        out_cmos = ColorMappedObjectsScene(
            func = lambda p : (
                scalar*(p[0]-self.x_shift), scalar*(p[1]+self.y_shift)
            )
        )

        input_coloring = Rectangle(
            height = self.plane_height,
            width = self.plane_width,
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 1,
        )
        output_coloring = input_coloring.copy()
        colorings = VGroup(input_coloring, output_coloring)
        vects = [LEFT, RIGHT]
        cmos_pair = [in_cmos, out_cmos]
        for coloring, vect, cmos in zip(colorings, vects, cmos_pair):
            coloring.move_to(self.x_shift*vect + self.y_shift*DOWN)
            coloring.color_using_background_image(cmos.background_image_file)
        return colorings

    def get_planes(self):
        input_plane = self.input_plane = NumberPlane(
            x_radius = self.plane_width / 2.0,
            y_radius = self.plane_height / 2.0,
        )
        output_plane = self.output_plane = input_plane.deepcopy()
        planes = VGroup(input_plane, output_plane)
        vects = [LEFT, RIGHT]
        label_texts = ["Input", "Output"]
        label_colors = [GREEN, RED]
        for plane, vect, text, color in zip(planes, vects, label_texts, label_colors):
            plane.stretch_to_fit_width(self.plane_width)
            plane.add_coordinates(x_vals = list(range(-2, 3)), y_vals = list(range(-2, 3)))
            plane.white_parts = VGroup(plane.axes, plane.coordinate_labels)
            plane.coordinate_labels.set_background_stroke(width=0)
            plane.lines_to_fade = VGroup(planes, plane.secondary_lines)
            plane.move_to(vect*FRAME_X_RADIUS/2 + self.y_shift*DOWN)
            label = TextMobject(text)
            label.scale(1.5)
            label.add_background_rectangle()
            label.move_to(plane)
            label.to_edge(UP, buff = MED_SMALL_BUFF)
            plane.add(label)
            plane.label = label
            for submob in plane.get_family():
                if isinstance(submob, TexMobject) and hasattr(submob, "background_rectangle"):
                    submob.remove(submob.background_rectangle)

        return planes

    def get_v_line(self):
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_line.set_stroke(WHITE, 5)
        return v_line

    def get_dots(self, input_plane, output_plane):
        step = self.dot_density
        x_min = -3.0
        x_max = 3.0
        y_min = -3.0
        y_max = 3.0
        dots = VGroup()
        for x in np.arange(x_min, x_max + step, step):
            for y in np.arange(y_max, y_min - step, -step):
                out_coords = self.func((x, y))
                dot = Dot(radius = self.dot_radius)
                dot.set_stroke(BLACK, 1)
                dot.move_to(input_plane.coords_to_point(x, y))
                dot.original_position = dot.get_center()
                dot.generate_target()
                dot.target.move_to(output_plane.coords_to_point(*out_coords))
                dot.target_color = rgba_to_color(point_to_rgba(
                    tuple(self.output_scalar*np.array(out_coords))
                ))
                dots.add(dot)
        return dots

class IntroduceInputOutputScene(InputOutputScene):
    CONFIG = {
        "dot_radius" : 0.05,
        "dot_density" : 0.25,
    }
    def construct(self):
        self.setup_planes()
        self.map_single_point_to_point()

    def setup_planes(self):
        self.input_plane, self.output_plane = self.get_planes()
        self.v_line = self.get_v_line()
        self.add(self.input_plane, self.output_plane, self.v_line)

    def map_single_point_to_point(self):
        input_plane = self.input_plane
        output_plane = self.output_plane

        #Dots
        dots = self.get_dots()

        in_dot = dots[int(0.55*len(dots))].copy()
        out_dot = in_dot.target
        for mob in in_dot, out_dot:
            mob.scale(1.5)
        in_dot.set_color(YELLOW)
        out_dot.set_color(PINK)

        input_label_arrow = Vector(DOWN+RIGHT)
        input_label_arrow.next_to(in_dot, UP+LEFT, SMALL_BUFF)
        input_label = TextMobject("Input point")
        input_label.next_to(input_label_arrow.get_start(), UP, SMALL_BUFF)
        for mob in input_label, input_label_arrow:
            mob.match_color(in_dot)
        input_label.add_background_rectangle()
        
        output_label_arrow = Vector(DOWN+LEFT)
        output_label_arrow.next_to(out_dot, UP+RIGHT, SMALL_BUFF)
        output_label = TextMobject("Output point")
        output_label.next_to(output_label_arrow.get_start(), UP, SMALL_BUFF)
        for mob in output_label, output_label_arrow:
            mob.match_color(out_dot)
        output_label.add_background_rectangle()

        path_arc = -TAU/4
        curved_arrow = Arrow(
            in_dot, out_dot,
            buff = SMALL_BUFF,
            path_arc = path_arc,
            color = WHITE,
        )
        curved_arrow.pointwise_become_partial(curved_arrow, 0, 0.95)
        function_label = TexMobject("f(", "\\text{2d input}", ")")
        function_label.next_to(curved_arrow, UP)
        function_label.add_background_rectangle()


        self.play(LaggedStartMap(GrowFromCenter, dots))
        self.play(LaggedStartMap(
            MoveToTarget, dots,
            path_arc = path_arc
        ))
        self.wait()
        self.play(FadeOut(dots))
        self.play(
            GrowFromCenter(in_dot),
            GrowArrow(input_label_arrow),
            FadeIn(input_label)
        )
        self.wait()
        self.play(
            ShowCreation(curved_arrow),
            ReplacementTransform(
                in_dot.copy(), out_dot,
                path_arc = path_arc
            ),
            FadeIn(function_label),
        )
        self.play(
            GrowArrow(output_label_arrow),
            FadeIn(output_label)
        )
        self.wait()
        self.play(*list(map(FadeOut, [
            input_label_arrow, input_label,
            output_label_arrow, output_label,
            curved_arrow, function_label,
        ])))

        #General movements and wiggles
        out_dot_continual_update = self.get_output_dot_continual_update(in_dot, out_dot)
        self.add(out_dot_continual_update)

        for vect in UP, RIGHT:
            self.play(
                in_dot.shift, 0.25*vect,
                rate_func = lambda t : wiggle(t, 8),
                run_time = 2
            )
        for vect in compass_directions(4, UP+RIGHT):
            self.play(Rotating(
                in_dot, about_point = in_dot.get_corner(vect),
                radians = TAU,
                run_time = 1
            ))
        self.wait()
        for coords in (-2, 2), (-2, -2), (2, -2), (1.5, 1.5):
            self.play(
                in_dot.move_to, input_plane.coords_to_point(*coords),
                path_arc = -TAU/4,
                run_time = 2
            )
        self.wait()

    ###

    def get_dots(self):
        input_plane = self.input_plane
        dots = VGroup()
        step = self.dot_density
        x_max = input_plane.x_radius
        x_min = -x_max
        y_max = input_plane.y_radius
        y_min = -y_max

        reverse = False
        for x in np.arange(x_min+step, x_max, step):
            y_range = list(np.arange(x_min+step, x_max, step))
            if reverse:
                y_range.reverse()
            reverse = not reverse
            for y in y_range:
                dot = Dot(radius = self.dot_radius)
                dot.move_to(input_plane.coords_to_point(x, y))
                dot.generate_target()
                dot.target.move_to(self.point_function(dot.get_center()))
                dots.add(dot)
        return dots

    def get_output_dot_continual_update(self, input_dot, output_dot):
        return Mobject.add_updater(
            output_dot, 
            lambda od : od.move_to(self.point_function(input_dot.get_center()))
        )

class IntroduceVectorField(IntroduceInputOutputScene):
    CONFIG = {
        "dot_density" : 0.5,
    }
    def construct(self):
        self.setup_planes()
        input_plane, output_plane = self.input_plane, self.output_plane
        dots = self.get_dots()

        in_dot = dots[0].copy()
        in_dot.move_to(input_plane.coords_to_point(1.5, 1.5))
        out_dot = in_dot.copy()
        out_dot_continual_update = self.get_output_dot_continual_update(in_dot, out_dot)
        for mob in in_dot, out_dot:
            mob.scale(1.5)
        in_dot.set_color(YELLOW)
        out_dot.set_color(PINK)

        out_vector = Arrow(
            LEFT, RIGHT, 
            color = out_dot.get_color(),
        )
        out_vector.set_stroke(BLACK, 1)
        continual_out_vector_update = Mobject.add_updater(
            out_vector, lambda ov : ov.put_start_and_end_on(
                output_plane.coords_to_point(0, 0),
                out_dot.get_center(),
            )
        )

        in_vector = out_vector.copy()
        def update_in_vector(in_vector):
            Transform(in_vector, out_vector).update(1)
            in_vector.scale(0.5)
            in_vector.shift(in_dot.get_center() - in_vector.get_start())
        continual_in_vector_update = Mobject.add_updater(
            in_vector, update_in_vector
        )
        continual_updates = [
            out_dot_continual_update,
            continual_out_vector_update, 
            continual_in_vector_update
        ]

        self.add(in_dot, out_dot)
        self.play(GrowArrow(out_vector, run_time = 2))
        self.wait()
        self.add_foreground_mobjects(in_dot)
        self.play(ReplacementTransform(out_vector.copy(), in_vector))
        self.wait()
        self.add(*continual_updates)
        path = Square().rotate(-90*DEGREES)
        path.replace(Line(
            input_plane.coords_to_point(-1.5, -1.5),
            input_plane.coords_to_point(1.5, 1.5),
        ), stretch = True)
        in_vectors = VGroup()
        self.add(in_vectors)
        for a in np.linspace(0, 1, 25):
            self.play(
                in_dot.move_to, path.point_from_proportion(a),
                run_time = 0.2,
                rate_func=linear,
            )
            in_vectors.add(in_vector.copy())

        # Full vector field
        newer_in_vectors = VGroup()
        self.add(newer_in_vectors)
        for dot in dots:
            self.play(in_dot.move_to, dot, run_time = 1./15)
            newer_in_vectors.add(in_vector.copy())
        self.remove(*continual_updates)
        self.remove()
        self.play(*list(map(FadeOut, [
            out_dot, out_vector, in_vectors, in_dot, in_vector
        ])))
        self.wait()
        target_length = 0.4
        for vector in newer_in_vectors:
            vector.generate_target()
            if vector.get_length() == 0:
                continue
            factor = target_length / vector.get_length()
            vector.target.scale(factor, about_point = vector.get_start())

        self.play(LaggedStartMap(MoveToTarget, newer_in_vectors))
        self.wait()

class TwoDScreenInOurThreeDWorld(AltTeacherStudentsScene, ThreeDScene):
    def construct(self):
        self.ask_about_2d_functions()
        self.show_3d()

    def ask_about_2d_functions(self):
        in_plane = NumberPlane(x_radius = 2.5, y_radius = 2.5)
        in_plane.add_coordinates()
        in_plane.set_height(3)
        out_plane = in_plane.copy()

        in_text = TextMobject("Input space")
        out_text = TextMobject("Output space")
        VGroup(in_text, out_text).scale(0.75)
        in_text.next_to(in_plane, UP, SMALL_BUFF)
        out_text.next_to(out_plane, UP, SMALL_BUFF)
        in_plane.add(in_text)
        out_plane.add(out_text)

        arrow = Arrow(
            LEFT, RIGHT, 
            path_arc = -TAU/4,
            color = WHITE
        )
        arrow.pointwise_become_partial(arrow, 0.0, 0.97)
        group = VGroup(in_plane, arrow, out_plane)
        group.arrange(RIGHT)
        arrow.shift(UP)
        group.move_to(self.students)
        group.to_edge(UP)

        dots = VGroup()
        dots_target = VGroup()
        for x in np.arange(-2.5, 3.0, 0.5):
            for y in np.arange(-2.5, 3.0, 0.5):
                dot = Dot(radius = 0.05)
                dot.move_to(in_plane.coords_to_point(x, y))
                dot.generate_target()
                dot.target.move_to(out_plane.coords_to_point(
                    x + 0.25*np.cos(5*y), y + 0.25*np.sin(3*x)
                ))
                dots.add(dot)
                dots_target.add(dot.target)
        dots.set_color_by_gradient(YELLOW, RED)
        dots_target.set_color_by_gradient(YELLOW, RED)

        self.play(
            self.teacher.change, "raise_right_hand",
            Write(in_plane, run_time = 1)
        )
        self.play(
            ShowCreation(arrow),
            ReplacementTransform(
                in_plane.copy(), out_plane,
                path_arc = -TAU/4,
            )
        )
        self.play(
            LaggedStartMap(GrowFromCenter, dots, run_time = 1),
            self.get_student_changes(*3*["erm"]),
        )
        self.play(LaggedStartMap(MoveToTarget, dots, path_arc = -TAU/4))
        self.wait(3)


    def show_3d(self):
        laptop = Laptop().scale(2)
        laptop.rotate(-TAU/12, DOWN)
        laptop.rotate(-5*TAU/24, LEFT)
        laptop.rotate(TAU/8, LEFT)
        laptop.scale(2.3*FRAME_X_RADIUS/laptop.screen_plate.get_width())
        laptop.shift(-laptop.screen_plate.get_center() + 0.1*IN)
        should_shade_in_3d(laptop)

        everything = VGroup(laptop, *self.mobjects)
        everything.generate_target()
        # for mob in everything.target.get_family():
        #     if isinstance(mob, PiCreature):
        #         mob.change_mode("confused")
        everything.target.rotate(TAU/12, LEFT)
        everything.target.rotate(TAU/16, UP)
        everything.target.shift(4*UP)

        self.move_camera(
            distance = 12,
            run_time = 4,
            added_anims = [MoveToTarget(everything, run_time = 4)],
        )
        always_rotate(everything, axis=UP, rate=3 * DEGREES)
        self.wait(10)

class EveryOutputPointHasAColor(ColorMappedObjectsScene):
    CONFIG = {
        "func" : lambda p : p,
        "dot_spacing" : 0.1,
        "dot_radius" : 0.01,
    }
    def construct(self):
        full_rect = FullScreenRectangle()
        full_rect.set_fill(WHITE, 1)
        full_rect.set_stroke(WHITE, 0)
        full_rect.color_using_background_image(self.background_image_file)

        title = TextMobject("Output Space")
        title.scale(1.5)
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        title.set_stroke(BLACK, 1)
        # self.add_foreground_mobjects(title)

        plane = NumberPlane()
        plane.fade(0.5)
        plane.axes.set_stroke(WHITE, 3)
        # plane.add(BackgroundRectangle(title))
        self.add(plane)


        dots = VGroup()
        step = self.dot_spacing
        for x in np.arange(-FRAME_X_RADIUS, FRAME_X_RADIUS+step, step):
            for y in np.arange(-FRAME_Y_RADIUS, FRAME_Y_RADIUS+step, step):
                dot = Dot(color = WHITE)
                dot.color_using_background_image(self.background_image_file)
                dot.move_to(x*RIGHT + y*UP)
                dots.add(dot)
        random.shuffle(dots.submobjects)

        m = 3 #exponential factor        
        n = 1
        dot_groups = VGroup()
        while n <= len(dots):
            dot_groups.add(dots[n-1:m*n-1])
            n *= m
        self.play(LaggedStartMap(
            LaggedStartMap, dot_groups,
            lambda dg : (GrowFromCenter,  dg),
            run_time = 8,
            lag_ratio = 0.2,
        ))

class DotsHoppingToColor(InputOutputScene):
    CONFIG = {
        "dot_radius" : 0.05,
        "dot_density" : 0.25,
    }
    def construct(self):
        input_coloring, output_coloring = self.get_colorings()
        input_plane, output_plane = self.get_planes()
        v_line = self.get_v_line()

        dots = self.get_dots(input_plane, output_plane)

        right_half_block = Rectangle(
            height = FRAME_HEIGHT,
            width = FRAME_X_RADIUS - SMALL_BUFF,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        right_half_block.to_edge(RIGHT, buff = 0)

        #Introduce parts
        self.add(input_plane, output_plane, v_line)
        self.play(
            FadeIn(output_coloring), 
            Animation(output_plane),
            output_plane.white_parts.set_color, BLACK,
            output_plane.lines_to_fade.set_stroke, {"width" : 0},
        )
        self.wait()
        self.play(LaggedStartMap(GrowFromCenter, dots, run_time = 3))
        self.wait()

        #Hop over and back
        self.play(LaggedStartMap(
            MoveToTarget, dots, 
            path_arc = -TAU/4,
            run_time = 3,
        ))
        self.wait()
        self.play(LaggedStartMap(
            ApplyMethod, dots,
            lambda d : (d.set_fill, d.target_color),
        ))
        self.wait()
        self.play(LaggedStartMap(
            ApplyMethod, dots,
            lambda d : (d.move_to, d.original_position),
            path_arc = TAU/4,
            run_time = 3,
        ))
        self.wait()
        self.play(
            FadeIn(input_coloring),
            Animation(input_plane),
            input_plane.white_parts.set_color, BLACK,
            input_plane.lines_to_fade.set_stroke, {"width" : 0},
            FadeOut(dots),
        )
        self.wait()

        #Cover output half
        right_half_block.save_state()
        right_half_block.next_to(FRAME_X_RADIUS*RIGHT, RIGHT)
        self.play(right_half_block.restore)
        self.wait()

        # Show yellow points
        inspector = DashedLine(
            ORIGIN, TAU*UP,
            dash_length = TAU/24,
            fill_opacity = 0,
            stroke_width = 3,
            stroke_color = WHITE,
        )
        inspector.add(*inspector.copy().set_color(BLACK).shift((TAU/24)*UP))
        inspector.apply_complex_function(np.exp)
        inspector.scale(0.15)

        inspector_image = inspector.copy()
        def update_inspector_image(inspector_image):
            inspector_image.move_to(self.point_function(inspector.get_center()))

        inspector_image_update_anim = UpdateFromFunc(
            inspector_image, update_inspector_image
        )
        pink_points_label = TextMobject("Pink points")
        pink_points_label.scale(0.7)
        pink_points_label.set_color(BLACK)

        self.play(
            inspector.move_to, input_plane.coords_to_point(-2.75, 2.75),
            inspector.set_stroke, {"width" : 2},
        )
        pink_points_label.next_to(inspector, RIGHT)
        self.play(
            Rotating(
                inspector, about_point = inspector.get_center(),
                rate_func = smooth,
                run_time = 2,
            ),
            Write(pink_points_label)
        )
        self.wait()
        self.play(right_half_block.next_to, FRAME_X_RADIUS*RIGHT, RIGHT)
        inspector_image_update_anim.update(0)
        self.play(ReplacementTransform(
            inspector.copy(), inspector_image,
            path_arc = -TAU/4,
        ))
        self.play(
            ApplyMethod(
                inspector.move_to, 
                input_plane.coords_to_point(-2, 0),
                path_arc = -TAU/8,
                run_time = 3,
            ),
            inspector_image_update_anim
        )
        self.play(
            ApplyMethod(
                inspector.move_to, 
                input_plane.coords_to_point(-2.75, 2.75),
                path_arc = TAU/8,
                run_time = 3,
            ),
            inspector_image_update_anim
        )
        self.play(FadeOut(pink_points_label))

        # Show black zero
        zeros = tuple(it.starmap(input_plane.coords_to_point, [
            (-2., -1), (1, 1), (2, -2),
        ]))
        for x in range(2):
            for zero in zeros:
                path = ParametricFunction(
                    bezier([
                        inspector.get_center(), 
                        input_plane.coords_to_point(0, 0),
                        zero
                    ]),
                    t_min = 0, t_max = 1
                )
                self.play(
                    MoveAlongPath(inspector, path, run_time = 2),
                    inspector_image_update_anim,
                )
                self.wait()
        self.play(FadeOut(VGroup(inspector, inspector_image)))

        # Show all dots and slowly fade them out
        for dot in dots:
            dot.scale(1.5)
        self.play(
            FadeOut(input_coloring),
            input_plane.white_parts.set_color, WHITE,
            LaggedStartMap(GrowFromCenter, dots)
        )
        self.wait()
        random.shuffle(dots.submobjects)
        self.play(LaggedStartMap(
            FadeOut, dots,
            lag_ratio = 0.05,
            run_time = 10,
        ))

        # Ask about whether a region contains a zero
        question = TextMobject("Does this region \\\\ contain a zero?")
        question.add_background_rectangle(opacity = 1)
        question.next_to(input_plane.label, DOWN)
        square = Square()
        square.match_background_image_file(input_coloring)
        square.move_to(input_plane)

        self.play(ShowCreation(square), Write(question))
        self.wait()
        quads = [
            (0, 0.5, 6, 6.25),
            (1, 1, 0.5, 2),
            (-1, -1, 3, 4.5),
            (0, 1.25, 5, 1.7),
            (-2, -1, 1, 1),
        ]
        for x, y, width, height in quads:
            self.play(
                square.stretch_to_fit_width, width,
                square.stretch_to_fit_height, height,
                square.move_to, input_plane.coords_to_point(x, y)
            )
            self.wait()

class SoWeFoundTheZeros(AltTeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Aha! So we \\\\ found the solutions!",
            target_mode = "hooray",
            student_index = 2,
            bubble_kwargs = {"direction" : LEFT},
        )
        self.wait()
        self.teacher_says(
            "Er...only \\\\ kind of",
            target_mode = "hesitant"
        )
        self.wait(3)

class Rearrange2DEquation(AltTeacherStudentsScene):
    def construct(self):
        f_tex, g_tex, h_tex = [
            "%s(\\text{2d point})"%char
            for char in ("f", "g", "h") 
        ]
        zero_tex = "\\vec{\\textbf{0}}"
        equations = VGroup(
            TexMobject(g_tex, "", "=", h_tex, ""),
            TexMobject(g_tex, "-", h_tex, "=", zero_tex),
        )
        equations.move_to(self.hold_up_spot, DOWN)
        equations.shift_onto_screen()

        brace = Brace(equations[1], UP)
        zero_eq = brace.get_tex("%s = %s"%(f_tex, zero_tex))

        for equation in equations:
            equation.set_color_by_tex(g_tex, BLUE)
            equation.set_color_by_tex(h_tex, YELLOW)
            equation.sort_alphabetically()


        self.teacher_holds_up(equations[0])
        self.change_all_student_modes("pondering")
        self.play(Transform(
            *equations,
            run_time = 1.5,
            path_arc = TAU/2
        ))
        self.play(
            Succession(
                GrowFromCenter(brace),
                Write(zero_eq, run_time = 1)
            ),
            self.get_student_changes(*["happy"]*3)
        )
        self.play(*[
            ApplyMethod(pi.change, "thinking", self.screen)
            for pi in self.pi_creatures
        ])
        self.wait(3)

class SearchForZerosInInputSpace(ColorMappedObjectsScene):
    CONFIG = {
        "func" : example_plane_func,
    }
    def construct(self):
        ColorMappedObjectsScene.construct(self)
        title = TextMobject("Input space")
        title.scale(2)
        title.to_edge(UP)
        title.set_stroke(BLACK, 1)
        title.add_background_rectangle()

        plane = NumberPlane()
        plane.fade(0.5)
        plane.axes.set_stroke(WHITE, 3)

        self.add(plane, title)

        looking_glass = Circle()
        looking_glass.set_stroke(WHITE, 3)
        looking_glass.set_fill(WHITE, 0.6)
        looking_glass.color_using_background_image(self.background_image_file)
        question = TextMobject("Which points go to 0?")
        question.next_to(looking_glass, DOWN)
        question.add_background_rectangle()

        mover = VGroup(looking_glass, question)
        mover.move_to(4*LEFT + UP)

        self.play(FadeIn(mover))
        points = [4*RIGHT+UP, 2*RIGHT+2*DOWN, 2*LEFT+2*DOWN, 3*RIGHT+2.5*DOWN]
        for point in points:
            self.play(mover.move_to, point, run_time = 1.5)
            self.wait()

class OneDRegionBoundary(Scene):
    CONFIG = {
        "graph_color" : BLUE,
        "region_rect_height" : 0.1,
    }
    def construct(self):
        x0 = self.x0 = 3 
        x1 = self.x1 = 6
        fx0 = self.fx0 = -2
        fx1 = self.fx1 = 2

        axes = self.axes = Axes(
            x_min = -1, x_max = 10,
            y_min = -3, y_max = 3,
        )
        axes.center()
        axes.set_stroke(width = 2)

        input_word = TextMobject("Input")
        input_word.next_to(axes.x_axis, UP, SMALL_BUFF, RIGHT)
        output_word = TextMobject("Output")
        output_word.next_to(axes.y_axis, UP)
        axes.add(input_word, output_word)
        self.add(axes)

        graph = self.get_graph_part(1, 1)
        alt_graphs = [
            self.get_graph_part(*points)
            for points in [
                (-1, -2),
                (-1, -1, -1),
                (1, 1, 1),
                (-0.75, 0, 1.75),
                (-3, -2, -1),
            ]
        ]

        #Region and boundary
        line = Line(axes.coords_to_point(x0, 0), axes.coords_to_point(x1, 0))
        region = Rectangle(
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = 0.5,
            height = self.region_rect_height
        )
        region.match_width(line, stretch = True)
        region.move_to(line)

        region_words = TextMobject("Input region")
        region_words.set_width(0.8*region.get_width())
        region_words.next_to(region, UP)

        x0_arrow, x1_arrow = arrows = VGroup(*[
            Arrow(
                axes.coords_to_point(x, 0),
                axes.coords_to_point(x, fx),
                color = color,
                buff = 0
            )
            for x, fx, color in [(x0, fx0, RED), (x1, fx1, GREEN)]
        ])
        minus = TexMobject("-")
        minus.match_color(x0_arrow)
        minus.next_to(x0_arrow, UP)
        plus = TexMobject("+")
        plus.match_color(x1_arrow)
        plus.next_to(x1_arrow, DOWN)
        signs = VGroup(plus, minus)


        self.play(
            GrowFromCenter(region),
            FadeIn(region_words)
        )
        self.wait()
        self.play(*it.chain(
            list(map(GrowArrow, arrows)),
            list(map(Write, signs))
        ))
        self.wait()
        self.play(
            ShowCreation(graph), 
            FadeOut(region_words),
        )
        self.wait()
        for alt_graph in alt_graphs + alt_graphs:
            self.play(Transform(graph, alt_graph, path_arc = 0.1*TAU))
        self.wait()


    ###

    def get_graph_part(self, *interim_values):
        result = VMobject()
        result.set_stroke(self.graph_color, 3)
        result.set_fill(opacity = 0)
        values = [self.fx0] + list(interim_values) + [self.fx1]
        result.set_points_smoothly([
            self.axes.coords_to_point(x, fx)
            for x, fx in zip(
                np.linspace(self.x0, self.x1, len(values)),
                values
            )
        ])
        return result

class DirectionOfA2DFunctionAlongABoundary(InputOutputScene):
    def construct(self):
        colorings = self.get_colorings()
        colorings.set_fill(opacity = 0.25)
        input_plane, output_plane = planes = self.get_planes()
        for plane in planes:
            plane.lines_to_fade.set_stroke(width = 0)
        v_line = self.get_v_line()

        rect = Rectangle()
        rect.set_stroke(WHITE, 5)
        rect.set_fill(WHITE, 0)
        line = Line(
            input_plane.coords_to_point(-0.75, 2.5),
            input_plane.coords_to_point(2.5, -1.5),
        )
        rect.replace(line, stretch = True)
        rect.insert_n_curves(50)
        rect.match_background_image_file(colorings[0])

        rect_image = rect.copy()
        rect_image.match_background_image_file(colorings[1])
        def update_rect_image(rect_image):
            rect_image.points = np.array(rect.points)
            rect_image.apply_function(self.point_function)
        rect_image_update_anim = UpdateFromFunc(rect_image, update_rect_image)


        def get_input_point():
            return rect.points[-1]

        def get_output_coords():
            in_coords = input_plane.point_to_coords(get_input_point())
            return self.func(in_coords)

        def get_angle():
            return angle_of_vector(get_output_coords())

        def get_color():
            return rev_to_color(get_angle()/TAU) #Negative?


        out_vect = Vector(RIGHT, color = WHITE)
        out_vect_update_anim = UpdateFromFunc(
            out_vect,
            lambda ov : ov.put_start_and_end_on(
                output_plane.coords_to_point(0, 0),
                rect_image.points[-1]
            ).set_color(get_color())
        )

        dot = Dot()
        dot.set_stroke(BLACK, 1)
        dot_update_anim = UpdateFromFunc(
            dot, lambda d : d.move_to(get_input_point()).set_fill(get_color())
        )

        in_vect = Vector(RIGHT)
        def update_in_vect(in_vect):
            in_vect.put_start_and_end_on(ORIGIN, 0.5*RIGHT)
            in_vect.rotate(get_angle())
            in_vect.set_color(get_color())
            in_vect.shift(get_input_point() - in_vect.get_start())
            return in_vect
        in_vect_update_anim = UpdateFromFunc(in_vect, update_in_vect)

        self.add(colorings, planes, v_line)

        self.play(
            GrowArrow(out_vect),
            GrowArrow(in_vect),
            Animation(dot),
        )
        self.play(
            ShowCreation(rect),
            ShowCreation(rect_image),
            out_vect_update_anim,
            in_vect_update_anim,
            dot_update_anim,
            rate_func = bezier([0, 0, 1, 1]),
            run_time = 10,
        )

class AskAboutHowToGeneralizeSigns(AltTeacherStudentsScene):
    def construct(self):
        # 2d plane
        plane = NumberPlane(x_radius = 2.5, y_radius = 2.5)
        plane.scale(0.8)
        plane.to_corner(UP+LEFT)
        plane.add_coordinates()

        dot = Dot(color = YELLOW)
        label = TextMobject("Sign?")
        label.add_background_rectangle()
        label.scale(0.5)
        label.next_to(dot, UP, SMALL_BUFF)
        dot.add(label)
        dot.move_to(plane.coords_to_point(1, 1))
        dot.save_state()
        dot.fade(1)
        dot.center()

        question = TextMobject(
            "Wait...what would \\\\ positive and negative \\\\ be in 2d?",
        )
        # question.set_color_by_tex_to_color_map({
        #     "+" : "green", 
        #     "textminus" : "red"
        # })


        self.student_says(
            question,
            target_mode = "sassy",
            student_index = 2,
            added_anims = [
                self.teacher.change, "plain",
            ],
            bubble_kwargs = {"direction" : LEFT},
            run_time = 1,
        )
        self.play(
            Write(plane, run_time = 1),
            self.students[0].change, "confused",
            self.students[1].change, "confused",
        )
        self.play(dot.restore)
        for coords in (-1, 1), (1, -1), (0, -2), (-2, 1):
            self.wait(0.5)
            self.play(dot.move_to, plane.coords_to_point(*coords))
        self.wait()

class HypothesisAboutFullyColoredBoundary(ColorMappedObjectsScene):
    CONFIG = {
        "func" : plane_func_from_complex_func(lambda z : z**3),
    }
    def construct(self):
        ColorMappedObjectsScene.construct(self)
        square = Square(side_length = 4)
        square.color_using_background_image(self.background_image_file)
        hypothesis = TextMobject(
           "Working Hypothesis: \\\\",
           "If a 2d function hits outputs of all possible colors \\\\" + 
           "on the boundary of a 2d region,", 
           "that region \\\\ contains a zero.",
           alignment = "",
        )
        hypothesis[0].next_to(hypothesis[1:], UP)
        hypothesis[0].set_color(YELLOW)
        s = hypothesis[1].get_tex_string()
        s = [c for c in s if c not in string.whitespace]
        n = s.index("colors")
        hypothesis[1][n:n+len("colors")].set_color_by_gradient(
            # RED, GOLD_E, YELLOW, GREEN, BLUE, PINK,
            BLUE, PINK, YELLOW,
        )
        hypothesis.to_edge(UP)
        square.next_to(hypothesis, DOWN, MED_LARGE_BUFF)

        self.add(hypothesis[0])
        self.play(
            LaggedStartMap(FadeIn, hypothesis[1]),
            ShowCreation(square, run_time = 8)
        )
        self.play(LaggedStartMap(FadeIn, hypothesis[2]))
        self.play(square.set_fill, {"opacity" : 1}, run_time = 2)
        self.wait()

class PiCreatureAsksWhatWentWrong(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.set_color(YELLOW_E)
        randy.flip()
        randy.to_corner(DOWN+LEFT)
        question = TextMobject("What went wrong?")
        question.next_to(randy, UP)
        question.shift_onto_screen()
        question.save_state()
        question.shift(DOWN).fade(1)

        self.play(randy.change, "erm")
        self.wait(2)
        self.play(
            Animation(VectorizedPoint(ORIGIN)),
            question.restore,
            randy.change, "confused",
        )
        self.wait(5)

class ForeverNarrowingLoop(InputOutputScene):
    CONFIG = {
        "target_coords" : (1, 1),
        "input_plane_corner" : UP+RIGHT,
        "shrink_time" : 20,
        "circle_start_radius" : 2.25,
        "start_around_target" : False,

        # Added as a flag to not mess up one clip already used and fine-timed
        # but to make it more convenient to do the other TinyLoop edits
        "add_convenient_waits" : False
    }
    def construct(self):
        input_coloring, output_coloring = colorings = VGroup(*self.get_colorings())
        input_plane, output_plane = planes = VGroup(*self.get_planes())
        for plane in planes:
            plane.white_parts.set_color(BLACK)
            plane.lines_to_fade.set_stroke(width = 0)

        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_line.set_stroke(WHITE, 5)

        self.add(colorings, v_line, planes)
        self.play(*it.chain(
            [
                ApplyMethod(coloring.set_fill, {"opacity" : 0.2})
                for coloring in colorings
            ],
            [
                ApplyMethod(plane.white_parts.set_color, WHITE)
                for plane in planes
            ]
        ), run_time = 2)

        # circle
        circle = Circle(color = WHITE, radius = self.circle_start_radius)
        circle.flip(axis = RIGHT)
        circle.insert_n_curves(50)
        if self.start_around_target:
            circle.move_to(input_plane.coords_to_point(*self.target_coords))
        else:
            circle.next_to(
                input_coloring.get_corner(self.input_plane_corner), 
                -self.input_plane_corner, 
                SMALL_BUFF
            )
        circle.set_stroke(width = 5)
        circle_image = circle.copy()
        circle.match_background_image_file(input_coloring)
        circle_image.match_background_image_file(output_coloring)

        def update_circle_image(circle_image):
            circle_image.points = circle.points
            circle_image.apply_function(self.point_function)
            circle_image.make_smooth()

        circle_image_update_anim = UpdateFromFunc(
            circle_image, update_circle_image
        )

        def optional_wait():
            if self.add_convenient_waits:
                self.wait()

        optional_wait()
        self.play(
            ShowCreation(circle),
            ShowCreation(circle_image),
            run_time = 3,
            rate_func = bezier([0, 0, 1, 1])
        )
        optional_wait()
        self.play(
            circle.scale, 0,
            circle.move_to, input_plane.coords_to_point(*self.target_coords),
            circle_image_update_anim,
            run_time = self.shrink_time,
            rate_func = bezier([0, 0, 1, 1])
        )

class AltForeverNarrowingLoop(ForeverNarrowingLoop):
    CONFIG = {
        "target_coords" : (-2, -1),
        "input_plane_corner" : DOWN+LEFT,
        "shrink_time" : 3,
    }

class TinyLoop(ForeverNarrowingLoop):
    CONFIG = {
        "circle_start_radius" : 0.5,
        "start_around_target" : True,
        "shrink_time" : 1,
        "add_convenient_waits" : True,
    }

class TinyLoopAroundZero(TinyLoop):
    CONFIG = {
        "target_coords" : (1, 1),
    }

class TinyLoopAroundBlue(TinyLoop):
    CONFIG = {
        "target_coords" : (2.4, 0),
    }

class TinyLoopAroundYellow(TinyLoop):
    CONFIG = {
        "target_coords" : (0, -1.3),
    }

class TinyLoopAroundOrange(TinyLoop):
    CONFIG = {
        "target_coords" : (0, -0.5),
    }

class TinyLoopAroundRed(TinyLoop):
    CONFIG = {
        "target_coords" : (-1, 1),
    }

class ConfusedPiCreature(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        morty.set_color(YELLOW_E)
        morty.flip()
        morty.center()

        self.play(morty.change, "awe", DOWN+3*RIGHT)
        self.wait(2)
        self.play(morty.change, "confused")
        self.wait(2)
        self.play(morty.change, "pondering")
        self.wait(2)

class FailureOfComposition(ColorMappedObjectsScene):
    CONFIG = {
        "func" : lambda p : (
            np.cos(TAU*p[1]/3.5), 
            np.sin(TAU*p[1]/3.5)
        )
    }
    def construct(self):
        ColorMappedObjectsScene.construct(self)

        big_square = Square(side_length = 4)
        big_square.move_to(ORIGIN, RIGHT)
        small_squares = VGroup(*[
            Square(side_length = 2) for x in range(2)
        ])
        small_squares.match_width(big_square, stretch = True)
        small_squares.arrange(DOWN, buff = 0)
        small_squares.move_to(big_square)
        small_squares.space_out_submobjects(1.1)
        all_squares = VGroup(big_square, *small_squares)
        all_squares.set_stroke(width = 6)

        for square in all_squares:
            square.set_color(WHITE)
            square.color_using_background_image(self.background_image_file)

        question = TextMobject("Does my border go through every color?")
        question.to_edge(UP)
        no_answers = VGroup()
        yes_answers = VGroup()
        for square in all_squares:
            if square is big_square:
                square.answer = TextMobject("Yes")
                square.answer.set_color(GREEN)
                yes_answers.add(square.answer)
            else:
                square.answer = TextMobject("No")
                square.answer.set_color(RED)
                no_answers.add(square.answer)
            square.answer.move_to(square)

        no_answers_in_equation = no_answers.copy()
        yes_answers_in_equation = yes_answers.copy()
        plus, equals = plus_equals = TexMobject("+=")
        equation = VGroup(
            no_answers_in_equation[0], plus,
            no_answers_in_equation[1], equals,
            yes_answers_in_equation
        )
        equation.arrange(RIGHT, buff = SMALL_BUFF)
        equation.next_to(big_square, RIGHT, MED_LARGE_BUFF)
        q_marks = TexMobject("???")
        q_marks.next_to(equals, UP)


        self.add(question)
        self.play(LaggedStartMap(ShowCreation, small_squares, lag_ratio = 0.8))
        self.play(LaggedStartMap(Write, no_answers))
        self.wait()
        self.play(
            small_squares.arrange, DOWN, {"buff" : 0},
            small_squares.move_to, big_square,
            no_answers.space_out_submobjects, 0.9,
        )
        self.add(big_square)
        no_answers_copy = no_answers.copy()
        small_squares.save_state()
        self.play(
            Transform(no_answers, no_answers_in_equation),
            Write(plus_equals),
            small_squares.set_stroke, {"width" : 0},
        )
        self.play(
            Write(yes_answers),
            Write(yes_answers_in_equation),
        )
        self.play(LaggedStartMap(FadeIn, q_marks, run_time = 1, lag_ratio = 0.8))
        self.wait(2)
        self.play(
            small_squares.restore,
            FadeOut(yes_answers),
            FadeIn(no_answers_copy),
        )
        self.wait()
        self.play(
            small_squares.set_stroke, {"width" : 0},
            FadeOut(no_answers_copy),
            FadeIn(yes_answers),
        )
        self.wait()

        # We can find a better notion of what we want

        cross = Cross(question)

        self.play(
            ShowCreation(cross, run_time = 2),
            FadeOut(equation),
            FadeOut(no_answers),
            FadeOut(q_marks),
            FadeOut(yes_answers),
        )

        x, plus, y = x_plus_y = TexMobject("x+y")
        x_plus_y.move_to(big_square)
        x_plus_y.save_state()
        x.move_to(no_answers_copy[0])
        y.move_to(no_answers_copy[1])
        plus.fade(1)

        for square, char in zip(small_squares, [x, y]):
            ghost = square.copy()
            ghost.set_stroke(width = 5)
            ghost.background_image_file = None
            self.play(
                small_squares.restore,
                ShowPassingFlash(ghost),
                Write(char)
            )
        self.wait()
        ghost = big_square.copy()
        ghost.background_image_file = None
        self.play(
            small_squares.set_stroke, {"width" : 0},
            x_plus_y.restore,
        )
        self.play(ShowPassingFlash(ghost))
        self.wait()

class PathContainingZero(InputOutputScene, PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs" : {
            "flip_at_start" : False,
            "height" : 1.5,
        },
        "default_pi_creature_start_corner" : DOWN+LEFT,
    }
    def construct(self):
        self.setup_planes()
        self.draw_path_hitting_zero()
        self.comment_on_zero()

    def setup_planes(self):
        colorings = VGroup(*self.get_colorings())
        self.input_coloring, self.output_coloring = colorings
        colorings.set_fill(opacity = 0.3)

        planes = VGroup(*self.get_planes())
        self.input_plane, self.output_plane = planes
        for plane in planes:
            # plane.white_parts.set_color(BLACK)
            plane.lines_to_fade.set_stroke(width = 0)

        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_line.set_stroke(WHITE, 5)

        self.add(colorings, planes)
        self.add(v_line)

    def draw_path_hitting_zero(self):
        morty = self.pi_creature

        path = self.path = VMobject(
            stroke_width = 5,
            stroke_color = WHITE,
            fill_opacity = 0,
        )
        path.match_background_image_file(self.input_coloring)
        path.set_points_smoothly(list(it.starmap(
            self.input_plane.coords_to_point, 
            [(1, 2.5), (2.5, 2.5), (2, 0.5), (1, 1), (0.5, 1), (0.5, 2), (1, 2.5)]
        )))

        out_path = self.out_path = path.copy()
        out_path.apply_function(self.point_function)
        out_path.match_background_image_file(self.output_coloring)
        out_path.make_smooth()

        self.play(
            Flash(
                VectorizedPoint(self.output_plane.coords_to_point(0, 0)),
                color = WHITE,
                flash_radius = 0.3,
                line_length = 0.2,
                num_lines = 13,
                rate_func = squish_rate_func(smooth, 0.5, 0.6),
            ),
            morty.change, "pondering",
            *[
                ShowCreation(mob, rate_func = bezier([0, 0, 1, 1]))
                for mob in (path, out_path)
            ],
            run_time = 5
        )

    def comment_on_zero(self):
        morty = self.pi_creature

        words = TextMobject(
            "Output is zero \\\\",
            "which has no direction"
        )
        origin = self.output_plane.coords_to_point(0, 0)
        words.to_edge(DOWN, buff = LARGE_BUFF)
        background_rect = BackgroundRectangle(
            words, buff = SMALL_BUFF,
            opacity = 1.0
        )
        background_rect.stretch_to_fit_width(0.1)

        arrow = Arrow(words.get_top(), origin)

        circles = VGroup()
        for point in self.input_plane.coords_to_point(1, 1), origin:
            circle = Circle(color = BLACK, radius = 0.5, stroke_width = 0)
            circle.move_to(point)
            circle.generate_target()
            circle.target.scale(0)
            circle.target.set_stroke(width = 4)
            circles.add(circle)
        in_circle, out_circle = circles

        new_words = TextMobject(
            "But we want $\\vec{\\textbf{x}}$ \\\\",
            "where $f(\\vec{\\textbf{x}}) = 0$",
        )
        new_words.move_to(words)

        self.play(
            FadeIn(background_rect),
            Write(words[0]),
            GrowArrow(arrow),
        )
        self.play(
            Write(words[1]),
            morty.change, "pleading",
            MoveToTarget(out_circle, run_time = 2)
        )
        self.wait()
        self.play(FadeOut(words))
        self.play(
            FadeIn(new_words),
            morty.change, "happy"
        )
        self.play(MoveToTarget(in_circle, run_time = 2))
        self.play(morty.change, "hooray")
        self.wait(3)

class TransitionFromPathsToBoundaries(ColorMappedObjectsScene):
    CONFIG = {
        "func" : plane_func_by_wind_spec(
            (-2, 0, 2), (2, 0, 1)
        ),
        "dot_fill_opacity" : 1,
        "dot_stroke_width" : 1,
        "include_walkers" : True,
        "include_question_mark" : True,
    }
    def construct(self):
        ColorMappedObjectsScene.construct(self)

        #Setup paths
        squares, joint_rect = self.get_squares_and_joint_rect()
        left_square, right_square = squares

        path1, path2 = paths = VGroup(*[
            Line(square.get_corner(UP+LEFT), square.get_corner(UP+RIGHT))
            for square in squares
        ])
        joint_path = Line(path1.get_start(), path2.get_end())

        for mob in it.chain(paths, [joint_path]):
            mob.set_stroke(WHITE, 4)
            mob.color_using_background_image(self.background_image_file)

        dot = self.get_dot_and_add_continual_animations()

        #Setup path braces
        for mob, tex in (path1, "x"), (path2, "y"), (joint_path, "x+y"):
            mob.brace = Brace(mob, DOWN)
            label = TextMobject("Winding =", "$%s$"%tex)
            label.next_to(mob.brace, DOWN)
            mob.brace.add(label)

        #Setup region labels

        sum_tex = "x+y"
        if self.include_question_mark:
            sum_tex += "\\, ?"
        for square, tex in (left_square, "x"), (right_square, "y"), (joint_rect, sum_tex):
            square.label = TextMobject("Winding = ", "$%s$"%tex)
            square.label.move_to(square)

        #Add paths
        self.position_dot(path1.get_start())
        for path in path1, path2:
            self.position_dot(path.get_start())
            self.play(
                MoveAlongPath(dot, path.copy()),
                ShowCreation(path),
                run_time = 2
            )
            self.play(GrowFromCenter(path.brace))
        self.wait()
        self.position_dot(joint_path.get_start())
        self.play(
            MoveAlongPath(dot, joint_path, run_time = 3),
            FadeOut(VGroup(path1.brace, path2.brace)),
            FadeIn(joint_path.brace),
        )
        self.wait()

        #Add regions
        self.play(
            FadeOut(paths),
            FadeOut(joint_path.brace), 
            dot.move_to, path1.get_start()
        )
        for square in squares:
            self.position_dot(square.points[0])
            kwargs = {
                "run_time" : 4,
                "rate_func" : bezier([0, 0, 1, 1]),
            }
            self.play(
                MoveAlongPath(dot, square.copy(), **kwargs),
                ShowCreation(square, **kwargs),
                Write(square.label, run_time = 2),
            )
            self.wait()
        self.play(
            dot.move_to, joint_rect.points[0],
            FadeOut(squares),
            FadeIn(joint_rect),
        )
        self.position_dot(joint_rect.points[0])
        self.play(
            Transform(left_square.label[0], joint_rect.label[0]),
            Transform(
                left_square.label[1], joint_rect.label[1][0],
                path_arc = TAU/6
            ),
            FadeIn(joint_rect.label[1][1]),
            FadeIn(joint_rect.label[1][3:]),
            FadeOut(right_square.label[0]),
            Transform(
                right_square.label[1], joint_rect.label[1][2],
                path_arc = TAU/6
            ),
            MoveAlongPath(
                dot, joint_rect,
                run_time = 6,
                rate_func = bezier([0, 0, 1, 1])
            )
        )
        self.wait()

    ###

    def get_squares_and_joint_rect(self):
        squares = VGroup(*[
            Square(side_length = 4).next_to(ORIGIN, vect, buff = 0)
            for vect in (LEFT, RIGHT)
        ])
        joint_rect = SurroundingRectangle(squares, buff = 0)
        for mob in it.chain(squares, [joint_rect]):
            mob.set_stroke(WHITE, 4)
            mob.color_using_background_image(self.background_image_file)
        return squares, joint_rect

    def get_dot_and_add_continual_animations(self):
        #Define important functions for updates
        get_output = lambda : self.func(tuple(dot.get_center()[:2]))
        get_output_color = lambda : rgba_to_color(point_to_rgba(get_output()))
        get_output_rev = lambda : -point_to_rev(get_output())
        self.get_output_rev = get_output_rev

        self.start_rev = 0
        self.curr_winding = 0
        def get_total_winding(dt = 0):
            rev = (get_output_rev() - self.start_rev)%1
            possible_windings = [
                np.floor(self.curr_winding)+k+rev
                for k in (-1, 0, 1)
            ]
            i = np.argmin([abs(pw - self.curr_winding) for pw in possible_windings])
            self.curr_winding = possible_windings[i]
            return self.curr_winding


        #Setup dot, arrow and label
        dot = self.dot = Dot(radius = 0.1)
        dot.set_stroke(WHITE, self.dot_stroke_width)
        update_dot_color = Mobject.add_updater(
            dot, lambda d : d.set_fill(
                get_output_color(),
                self.dot_fill_opacity
            )
        )

        label = DecimalNumber(0, num_decimal_places = 1)
        label_upadte = ContinualChangingDecimal(
            label, get_total_winding,
            position_update_func = lambda l : l.next_to(dot, UP+LEFT, SMALL_BUFF)
        )

        arrow_length = 0.75
        arrow = Vector(arrow_length*RIGHT)
        arrow.set_stroke(WHITE, self.dot_stroke_width)
        def arrow_update_func(arrow):
            arrow.set_fill(get_output_color(), 1)
            arrow.rotate(-TAU*get_output_rev() - arrow.get_angle())
            arrow.scale(arrow_length/arrow.get_length())
            arrow.shift(dot.get_center() - arrow.get_start())
            return arrow
        update_arrow = Mobject.add_updater(arrow, arrow_update_func)

        if self.include_walkers:
            self.add(update_arrow, update_dot_color, label_upadte)
        return dot

    def position_dot(self, point):
        self.dot.move_to(point)
        self.start_rev = self.get_output_rev()
        self.curr_winding = 0

class TransitionFromPathsToBoundariesArrowless(TransitionFromPathsToBoundaries):
    CONFIG = {
        "func" : plane_func_by_wind_spec(
            (-2, 0, 2), (2, 0, 1)
        ),
        "dot_fill_opacity" : 0,
        "dot_stroke_width" : 0,
        "include_walkers" : False,
        "include_question_mark" : False,
    }

class BreakDownLoopWithNonzeroWinding(TransitionFromPathsToBoundaries):
    def construct(self):
        TransitionFromPathsToBoundaries.construct(self)
        zero_point = 2*LEFT

        squares, joint_rect = self.get_squares_and_joint_rect()
        left_square, right_square = squares
        VGroup(squares, joint_rect).shift(MED_LARGE_BUFF*DOWN)

        dot = self.get_dot_and_add_continual_animations()

        for rect, tex in (left_square, "x"), (right_square, "y"), (joint_rect, "3"):
            rect.label = TextMobject("Winding = ", "$%s$"%tex)
            rect.label.move_to(rect)
        sum_label = TexMobject("x", "+", "y", "=", "3")
        x, plus, y, equals, three = sum_label
        sum_label.next_to(joint_rect, UP)

        both_cannot_be_zero = TextMobject("These cannot both be 0")
        both_cannot_be_zero.move_to(plus)
        both_cannot_be_zero.to_edge(UP)
        arrows = VGroup(*[
            Arrow(both_cannot_be_zero.get_bottom(), var.get_top(), buff = SMALL_BUFF)
            for var in (x, y)
        ])

        self.position_dot(joint_rect.points[0])
        self.add(joint_rect)
        self.play(
            MoveAlongPath(dot, joint_rect, rate_func = bezier([0, 0, 1, 1])),
            Write(joint_rect.label, rate_func = squish_rate_func(smooth, 0.7, 1)),
            run_time = 4
        )
        self.wait()
        self.play(
            ReplacementTransform(joint_rect.label, left_square.label),
            ReplacementTransform(joint_rect.label.copy(), right_square.label),
            ReplacementTransform(joint_rect.label[1].copy(), three),
            FadeIn(left_square),
            FadeIn(right_square),
        )
        self.play(
            ReplacementTransform(left_square.label[1].copy(), x),
            ReplacementTransform(right_square.label[1].copy(), y),
            FadeIn(plus),
            FadeIn(equals),
        )
        self.play(
            FadeIn(both_cannot_be_zero),
            *list(map(GrowArrow, arrows))
        )
        self.wait()

class BackToEquationSolving(AltTeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Back to solving \\\\ equations"
        )
        self.change_all_student_modes("hooray")
        self.play(*[
            ApplyMethod(pi.look_at, self.screen)
            for pi in self.pi_creatures
        ])
        self.wait(3)

class MonomialTerm(PathContainingZero):
    CONFIG = {
        "non_renormalized_func" : plane_func_from_complex_func(lambda z : z**5),
        "full_func_label" : "f(x) = x^5",
        "func_label" : "x^5",
        "loop_radius" : 1.1,
        "label_buff" : 0.3,
        "label_move_to_corner" : ORIGIN,
        "should_end_with_rescaling" : True,
    }
    def construct(self):
        self.setup_planes()
        self.relabel_planes()
        self.add_function_label()
        self.show_winding()
        if self.should_end_with_rescaling:
            self.rescale_output_plane()

    def relabel_planes(self):
        for plane in self.input_plane, self.output_plane:
            for mob in plane:
                if isinstance(mob, TexMobject):
                    plane.remove(mob)

            if hasattr(plane, "numbers_to_show"):
                _range = plane.numbers_to_show
            else:
                _range = list(range(-2, 3))
            for x in _range:
                if x == 0:
                    continue
                label = TexMobject(str(x))
                label.scale(0.5)
                point = plane.coords_to_point(x, 0)
                label.next_to(point, DOWN, MED_SMALL_BUFF)
                plane.add(label)
                self.add_foreground_mobject(label)
                tick = Line(SMALL_BUFF*DOWN, SMALL_BUFF*UP)
                tick.move_to(point)
                plane.add(tick)
            for y in _range:
                if y == 0:
                    continue
                label = TexMobject("%di"%y)
                label.scale(0.5)
                point = plane.coords_to_point(0, y)
                label.next_to(point, LEFT, MED_SMALL_BUFF)
                plane.add(label)
                self.add_foreground_mobject(label)
                tick = Line(SMALL_BUFF*LEFT, SMALL_BUFF*RIGHT)
                tick.move_to(point)
                plane.add(tick)
        self.add(self.input_plane, self.output_plane)

    def add_function_label(self):
        label = TexMobject(self.full_func_label)
        label.add_background_rectangle(opacity = 1, buff = SMALL_BUFF)
        arrow = Arrow(
            2*LEFT, 2*RIGHT, path_arc = -TAU/3,
        )
        arrow.pointwise_become_partial(arrow, 0, 0.95)
        label.next_to(arrow, UP)
        VGroup(arrow, label).to_edge(UP)
        self.add(label, arrow)

    def show_winding(self):
        loop = Arc(color = WHITE, angle = 1.02*TAU, num_anchors = 42)
        loop.scale(self.loop_radius)
        loop.match_background_image_file(self.input_coloring)
        loop.move_to(self.input_plane.coords_to_point(0, 0))

        out_loop = loop.copy()
        out_loop.apply_function(self.point_function)
        out_loop.match_background_image_file(self.output_coloring)

        get_in_point = lambda : loop.points[-1]
        get_out_point = lambda : out_loop.points[-1]
        in_origin = self.input_plane.coords_to_point(0, 0)
        out_origin = self.output_plane.coords_to_point(0, 0)

        dot = Dot()
        update_dot = UpdateFromFunc(dot, lambda d : d.move_to(get_in_point()))

        out_dot = Dot()
        update_out_dot = UpdateFromFunc(out_dot, lambda d : d.move_to(get_out_point()))

        buff = self.label_buff
        def generate_label_update(label, point_func, origin):
            return UpdateFromFunc(
                label, lambda m : m.move_to(
                    (1+buff)*point_func() - buff*origin,
                    self.label_move_to_corner
                )
            )
        x = TexMobject("x")
        fx = TexMobject(self.func_label)
        update_x = generate_label_update(x, get_in_point, in_origin)
        update_fx = generate_label_update(fx, get_out_point, out_origin)

        morty = self.pi_creature

        kwargs = {
            "run_time" : 15,
            "rate_func" : None,
        }
        self.play(
            ShowCreation(loop, **kwargs),
            ShowCreation(out_loop, **kwargs),
            update_dot,
            update_out_dot,
            update_x,
            update_fx,
            ApplyMethod(morty.change, "pondering", out_dot),
        )
        self.play(
            FadeOut(VGroup(dot, out_dot, x, fx))
        )
        self.loop = loop
        self.out_loop = out_loop

    def rescale_output_plane(self):
        output_stuff = VGroup(self.output_plane, self.output_coloring)
        self.play(*list(map(FadeOut, [self.loop, self.out_loop])))
        self.play(
            output_stuff.scale, 3.0/50, run_time = 2
        )
        self.wait()

    ###

    def func(self, coords):
        return self.non_renormalized_func(coords)

class PolynomialTerms(MonomialTerm):
    CONFIG = {
        "non_renormalized_func" : plane_func_from_complex_func(lambda z : z**5 - z - 1),
        "full_func_label" : "f(x) = x^5 - x - 1",
        "func_label" : "x^5 + \\cdots",
        "loop_radius" : 2.0,
        "label_buff" : 0.15,
        "label_move_to_corner" : DOWN+LEFT,
        "should_end_with_rescaling" : False,
    }
    def construct(self):
        self.pi_creature.change("pondering", VectorizedPoint(ORIGIN))
        MonomialTerm.construct(self)
        self.cinch_loop()
        # self.sweep_through_loop_interior()

    def relabel_planes(self):
        self.output_plane.x_radius = 50
        self.output_plane.y_radius = 50
        self.output_plane.numbers_to_show = list(range(-45, 50, 15))
        MonomialTerm.relabel_planes(self)

    def sweep_through_loop_interior(self):
        loop = self.loop
        morty = self.pi_creature

        line, line_target = [
            Line(
                loop.get_left(), loop.get_right(),
                path_arc = u*TAU/2,
                n_arc_anchors = 40,
                background_image_file = self.input_coloring.background_image_file ,
                stroke_width = 4,
            )
            for u in (-1, 1)
        ]
        out_line = line.copy()
        update_out_line = UpdateFromFunc(
            out_line, 
            lambda m : m.set_points(line.points).apply_function(self.point_function),
        )

        self.play(
            Transform(
                line, line_target,
                run_time = 10,
                rate_func = there_and_back
            ),
            update_out_line,
            morty.change, "hooray"
        )
        self.wait()

    def cinch_loop(self):
        loop = self.loop
        out_loop = self.out_loop
        morty = self.pi_creature

        update_out_loop = UpdateFromFunc(
            out_loop,
            lambda m : m.set_points(loop.points).apply_function(self.point_function)
        )

        self.add(
            loop.copy().set_stroke(width = 1),
            out_loop.copy().set_stroke(width = 1),
        )
        self.play(
            ApplyMethod(
                loop.scale, 0, {"about_point" : self.input_plane.coords_to_point(0.2, 1)},
                run_time = 12,
                rate_func = bezier([0, 0, 1, 1])
            ),
            update_out_loop,
            morty.change, "hooray"
        )
        self.wait()

class SearchSpacePerimeterVsArea(EquationSolver2d):
    CONFIG = {
        "func" : example_plane_func,
        "num_iterations" : 15,
        "display_in_parallel" : False,
        "use_fancy_lines" : True,
    }
    def construct(self):
        self.force_skipping()
        EquationSolver2d.construct(self)
        self.revert_to_original_skipping_status()

        all_parts = VGroup(*self.get_mobjects())
        path_parts = VGroup()
        non_path_parts = VGroup()
        for part in all_parts:
            if part.get_background_image_file() is not None:
                path_parts.add(part)
            else:
                non_path_parts.add(part)
        path_parts.save_state()
        path_parts.generate_target()
        for path_target in path_parts.target:
            if isinstance(path_target, Line):
                path_target.rotate(-path_target.get_angle())
        path_parts.target.arrange(DOWN, buff = MED_SMALL_BUFF)
        alt_path_parts = path_parts.copy()
        size = lambda m : m.get_height() + m.get_width()
        alt_path_parts.submobjects.sort(
            key=lambda m1: -size(m1)
        )

        full_rect = SurroundingRectangle(
            path_parts,
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 1,
            background_image_file = path_parts[0].background_image_file
        )
        full_rect.save_state()
        full_rect.stretch(0, 1, about_edge = UP)

        self.play(
            FadeOut(non_path_parts),
            path_parts.set_stroke, {"width" : 1},
        )
        self.remove(all_parts)
        for x in range(2):
            alt_path_parts.save_state()
            self.play(LaggedStartMap(
                FadeIn, alt_path_parts,
                rate_func = there_and_back,
                lag_ratio = 0.3,
                run_time = 3,
                remover = True
            ))
            alt_path_parts.restore()
        self.play(
            full_rect.restore,
            run_time = 2,
        )
        self.wait()
        self.play(FadeOut(full_rect))
        self.wait()

class ShowPolynomialFinalState(SolveX5MinusXMinus1):
    CONFIG = {
        "num_iterations" : 15,
    }
    def construct(self):
        self.force_skipping()
        SolveX5MinusXMinus1.construct(self)
        self.revert_to_original_skipping_status()

class PiCreatureInAwe(Scene):
    def construct(self):
        randy = Randolph()


        self.play(randy.change, "awe")
        self.play(Blink(randy))
        self.play(randy.look, UP, run_time = 2)
        self.play(
            randy.look, RIGHT, 
            run_time = 4, 
            rate_func = there_and_back,
            path_arc = -TAU/4
        )
        self.wait()

class ShowComplexFunction(Scene):
    def construct(self):
        plane = ComplexPlane()
        plane.add_coordinates()
        four_i = plane.coordinate_labels[-1]
        plane.coordinate_labels.remove(four_i)
        plane.remove(four_i)

        title = TextMobject("Complex Plane")
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        rect = BackgroundRectangle(title, fill_opacity = 1, buff = MED_SMALL_BUFF)

        x = complex(1, 0.4)
        f = lambda x : x**5 - x - 1

        x_point = plane.number_to_point(x)
        fx_point = plane.number_to_point(f(x))

        x_dot = Dot(x_point)
        fx_dot = Dot(fx_point, color = YELLOW)
        arrow = Arrow(
            x_point, fx_point,
            path_arc = TAU/3,
            color = YELLOW
        )
        arrow.pointwise_become_partial(arrow, 0, 0.95)

        x_label = TexMobject("x = %d+%.1fi"%(x.real, x.imag))
        x_label.next_to(x_dot, RIGHT)
        x_label.add_background_rectangle()

        fx_label = TexMobject("f(x) = x^5 - x - 1")
        fx_label.next_to(fx_dot, DOWN, SMALL_BUFF)
        fx_label.set_color(YELLOW)
        fx_label.add_background_rectangle()
        fx_label.generate_target()
        fx_label.target.move_to(title)
        fx_label.target[1].set_color(WHITE)

        self.play(
            Write(plane),
            FadeIn(rect),
            LaggedStartMap(FadeIn, title)
        )
        self.play(*list(map(FadeIn, [x_dot, x_label])))
        self.wait()
        self.play(
            ReplacementTransform(x_dot.copy(), fx_dot, path_arc = arrow.path_arc),
            ShowCreation(arrow, rate_func = squish_rate_func(smooth, 0.2, 1))
        )
        self.play(FadeIn(fx_label))
        self.wait(2)
        self.play(
            MoveToTarget(fx_label),
            *list(map(FadeOut, [title, x_dot, x_label, arrow, fx_dot]))
        )
        self.play(FadeOut(plane.coordinate_labels))
        self.wait()

class WindingNumbersInInputOutputContext(PathContainingZero):
    CONFIG = {
        "in_loop_center_coords" : (-2, -1),
        "run_time" : 10,
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.setup_planes()

        in_loop = Circle()
        in_loop.flip(RIGHT)
        # in_loop = Square(side_length = 2)
        in_loop.insert_n_curves(100)
        in_loop.move_to(self.input_plane.coords_to_point(
            *self.in_loop_center_coords
        ))
        in_loop.match_background_image_file(self.input_coloring)

        out_loop = in_loop.copy()
        out_loop.match_background_image_file(self.output_coloring)
        update_out_loop = Mobject.add_updater(
            out_loop,
            lambda m : m.set_points(in_loop.points).apply_function(self.point_function)
        )
        # self.add(update_out_loop)

        in_dot = Dot(radius = 0.04)
        update_in_dot = Mobject.add_updater(
            in_dot, lambda d : d.move_to(in_loop.point_from_proportion(1))
        )
        self.add(update_in_dot)

        out_arrow = Arrow(LEFT, RIGHT)
        update_out_arrow = Mobject.add_updater(
            out_arrow, 
            lambda a : a.put_start_and_end_on(
                self.output_plane.coords_to_point(0, 0),
                out_loop.point_from_proportion(1)
            )
        )
        update_out_arrow_color = Mobject.add_updater(
            out_arrow,
            lambda a : a.set_color(rev_to_color(a.get_angle()/TAU))
        )
        self.add(update_out_arrow, update_out_arrow_color)

        words = TextMobject(
            "How many times does \\\\ the output wind around?"
        )
        label = self.output_plane.label
        words.move_to(label, UP)
        self.output_plane.remove(label)
        self.add(words)

        decimal = DecimalNumber(0)
        decimal.next_to(self.output_plane.get_corner(UP+RIGHT), DOWN+LEFT)


        self.play(
            ShowCreation(in_loop),
            ShowCreation(out_loop),
            ChangeDecimalToValue(decimal, 2),
            Animation(in_dot),
            run_time = self.run_time,
            rate_func = bezier([0, 0, 1, 1])
        )

class SolveX5SkipToEnd(SolveX5MinusXMinus1):
    CONFIG = {
        "num_iterations" : 4,
    }
    def construct(self):
        self.force_skipping()
        SolveX5MinusXMinus1.construct(self)
        self.revert_to_original_skipping_status()

        mobjects = VGroup(*self.get_mobjects())
        lines = VGroup()
        rects = VGroup()
        for mob in mobjects:
            if mob.background_image_file is not None:
                mob.set_stroke(width = 2)
                lines.add(mob)
            elif isinstance(mob, Polygon):
                rects.add(mob)
            else:
                self.remove(mob)

        self.clear()
        self.add(lines, rects)

class ZeroFoundOnBoundary(Scene):
    def construct(self):
        arrow = Vector(DOWN+LEFT, color = WHITE)
        words = TextMobject("Found zero on boundary!")
        words.next_to(arrow.get_start(), UP)
        words.shift(1.5*RIGHT)

        point = VectorizedPoint()
        point.next_to(arrow, DOWN+LEFT)

        self.play(Flash(point))
        self.play(
            GrowArrow(arrow),
            Write(words),
        )
        self.wait()

class AllOfTheVideos(Scene):
    CONFIG = {
        "camera_config" : {
            "background_opacity" : 1,
        }
    }
    def construct(self):
        thumbnail_dir = os.path.join(MEDIA_DIR, "3b1b_videos/Winding/OldThumbnails")
        n = 4
        images = Group(*[
            ImageMobject(os.path.join(thumbnail_dir, file))
            for file in os.listdir(thumbnail_dir)[:n**2]
        ])
        for image in images:
            rect = SurroundingRectangle(image, buff = 0)
            rect.set_stroke(WHITE, 1)
            image.add(rect)
        images.arrange_in_grid(n, n, buff = 0)
        images.set_height(FRAME_HEIGHT)
        random.shuffle(images.submobjects)

        self.play(LaggedStartMap(FadeIn, images, run_time = 4))
        self.wait()

class EndingCredits(Scene):
    def construct(self):
        text = TextMobject(
            "Written and animated by: \\\\",
            "Sridhar Ramesh \\\\",
            "Grant Sanderson"
        )
        text[0].shift(MED_SMALL_BUFF*UP)
        text.to_edge(UP)

        pi = PiCreature(color = YELLOW_E, height = 2)
        pi.to_edge(DOWN)
        pi.change_mode("happy")
        self.add(pi)

        self.play(LaggedStartMap(FadeIn, text), pi.look_at, text)
        self.play(pi.change, "wave_1", text)
        self.play(Blink(pi))
        self.play(pi.change, "happy")
        self.wait()

class MentionQAndA(Scene):
    def construct(self):
        title = TextMobject("Q\\&A with ", "Ben", "and", "Sridhar\\\\", "at", "Patreon")
        title.set_color_by_tex_to_color_map({
            "Ben" : MAROON,
            "Sridhar" : YELLOW,
        })
        patreon_logo = VGroup(*PatreonLogo().family_members_with_points())
        patreon_logo.sort()
        patreon_logo.replace(title.get_parts_by_tex("Patreon"))
        patreon_logo.scale(1.3, about_edge = LEFT)
        patreon_logo.shift(0.5*SMALL_BUFF*DOWN)
        title.submobjects[-1] = patreon_logo

        title.to_edge(UP)
        self.add(title)

        questions = VGroup(*list(map(TextMobject, [
            "If you think of the current videos as short stories, \\\\ what is the novel that you want to write?",
            "How did you get into mathematics?",
            "What motivated you to join 3b1b?",
            "$\\vdots$",
        ])))
        questions.arrange(DOWN, buff = 0.75)
        questions.next_to(title, DOWN, LARGE_BUFF)

        self.play(LaggedStartMap(FadeIn, questions, run_time = 3))
        self.wait(2)
        self.play(FadeOut(questions))
        self.wait()

class TickingClock(Scene):
    CONFIG = {
        "run_time" : 90,
    }
    def construct(self):
        clock = Clock()
        clock.set_height(FRAME_HEIGHT - 1)
        clock.to_edge(LEFT)
        lines = [clock.hour_hand, clock.minute_hand]
        def update_line(line):
            rev = line.get_angle()/TAU
            line.set_color(rev_to_color(rev))

        for line in lines:
            self.add(Mobject.add_updater(line, update_line))

        run_time = self.run_time
        self.play(ClockPassesTime(
            clock, 
            run_time = run_time,
            hours_passed = 0.1*run_time
        ))

class InfiniteListOfTopics(Scene):
    def construct(self):
        rect = Rectangle(width = 5, height = 7)
        rect.to_edge(RIGHT)
        title = TextMobject("Infinite list \\\\ of topics")
        title.next_to(rect.get_top(), DOWN)
        lines = VGroup(*[
            TextMobject(words).scale(0.5)
            for words in [
                "Winding number",
                "Laplace transform",
                "Wallis product",
                "Quantum information",
                "Elliptic curve cryptography",
                "Strange attractors",
                "Convolutional neural networks",
                "Fixed points",
            ]
        ] + [TexMobject("\\vdots")])
        lines.arrange(DOWN, buff = MED_SMALL_BUFF, aligned_edge = LEFT)
        lines.next_to(title, DOWN, MED_LARGE_BUFF)
        lines[-1].next_to(lines[-2], DOWN)

        self.add(rect, title)
        self.play(LaggedStartMap(FadeIn, lines, run_time = 5))
        self.wait()

class ManyIterations(Scene):
    def construct(self):
        words = VGroup(*[
            TextMobject(word, alignment = "")
            for word in [
                "Winding numbers, v1",
                "Winding numbers, v2 \\\\ (center on domain coloring)",
                "Winding numbers, v3 \\\\ (clarify visuals of 2d functions)",
                "Winding numbers, v4 \\\\ (postpone topology examples for part 2)",
                "Winding numbers, v5 \\\\ (start down wrong path)",
            ]
        ])
        words.arrange(DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT)
        words.scale(0.75)
        words.to_edge(RIGHT)

        self.add(words[0])
        for last_word, word in zip(words, words[1:]):
            cross = Cross(last_word)
            self.play(ShowCreation(cross))
            self.play(FadeIn(word))
        self.wait()

class MentionFree(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs" : {
            "flip_at_start" : False,
        },
        "default_pi_creature_start_corner" : DOWN,
    }
    def construct(self):
        morty = self.pi_creature
        morty.shift(RIGHT)

        items = VGroup(
            TextMobject("Movie:", "$>\\$10.00$"),
            TextMobject("College course:", "$>\\$1{,}000.00$"),
            TextMobject("YouTube video:", "$=\\$0.00$"),
        )
        # items.arrange(DOWN, buff = MED_LARGE_BUFF)
        items.next_to(morty, UP, LARGE_BUFF)
        right_x = morty.get_right()[0]
        for item in items:
            item[1].set_color(GREEN)
            item.shift((right_x - item[0].get_right()[0])*RIGHT)

        self.play(
            morty.change, "raise_right_hand",
            FadeInFromDown(items[0])
        )
        self.wait()
        self.play(
            FadeInFromDown(items[1]),
            items[0].shift, UP,
        )
        self.wait()
        self.play(
            items[:2].shift, UP,
            FadeInFromDown(items[2]),
            morty.change, "surprised"
        )
        self.wait(4)
        self.play(
            morty.change, "raise_left_hand", VectorizedPoint(3*LEFT)
        )
        self.wait(4)
        self.play(morty.change, "gracious", OUT)
        self.wait(4)


class EndScreen(PatreonEndScreen, PiCreatureScene):
    CONFIG = {
        "run_time" : 0,
    }
    def construct(self):
        self.remove(self.pi_creature)
        PatreonEndScreen.construct(self)
        randy, morty = self.pi_creatures
        randy.change("plain")
        morty.change("plain")

        for mode in "thinking", "confused", "pondering", "hooray":
            self.play(randy.change, mode)
            self.wait()
            self.play(morty.change, mode)
            self.wait(2)

class Thumbnail(SearchSpacePerimeterVsArea):
    CONFIG = {
        "num_iterations" : 18,
        "func" : plane_func_by_wind_spec(
            (-3, -1.3, 2), (0.1, 0.2, 1), (2.8, -2, 1)
        ),
    }
    def construct(self):
        self.force_skipping()
        EquationSolver2d.construct(self)
        self.revert_to_original_skipping_status()

        mobjects = VGroup(*self.get_mobjects())
        lines = VGroup()
        rects = VGroup()
        get_length = lambda mob : max(mob.get_width(), mob.get_height())
        for mob in mobjects:
            if mob.background_image_file is not None:
                mob.set_stroke(width = 4*np.sqrt(get_length(mob)))
                lines.add(mob)
            elif isinstance(mob, Polygon):
                rects.add(mob)
            else:
                self.remove(mob)

        self.clear()
        self.add(lines)

