from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from scene.reconfigurable_scene import ReconfigurableScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.chapter1 import OpeningQuote, PatreonThanks
from eoc.graph_scene import *

SINE_COLOR = BLUE
X_SQUARED_COLOR = GREEN
SUM_COLOR = RED
PRODUCT_COLOR = YELLOW

class Chapter3OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "Using the chain rule is like peeling an onion: ",
            "you have to deal with each layer at a time, and ",
            "if it is too big you will start crying."
        ],
        "author" : "(Anonymous professor)"
    }

class TransitionFromLastVideo(TeacherStudentsScene):
    def construct(self):
        simple_rules = VGroup(*map(TexMobject, [
            "\\frac{d(x^3)}{dx} = 3x^2",
            "\\frac{d(\\sin(x))}{dx} = \\cos(x)",
            "\\frac{d(e^x)}{dx} = e^x",
        ]))

        combination_rules = VGroup(*[
            TexMobject("\\frac{d}{dx}\\left(%s\\right)"%tex)
            for tex in [
                "\\sin(x) + x^2",
                "\\sin(x)(x^2)",
                "\\sin(x^2)",
            ]
        ])
        for rules in simple_rules, combination_rules:
            rules.arrange_submobjects(buff = LARGE_BUFF)
            rules.next_to(self.get_teacher(), UP, buff = MED_LARGE_BUFF)
            rules.to_edge(LEFT)

        series = VideoSeries()
        series.to_edge(UP)
        last_video = series[2]
        last_video.save_state()
        this_video = series[3]
        brace = Brace(last_video)

        #Simple rules
        self.add(series)
        self.play(
            FadeIn(brace),
            last_video.highlight, YELLOW
        )
        for rule in simple_rules:
            self.play(
                Write(rule, run_time = 1),
                self.get_teacher().change_mode, "raise_right_hand",
                *[
                    ApplyMethod(pi.change_mode, "pondering")
                    for pi in self.get_students()
                ]
            )
        self.dither(2)
        self.play(simple_rules.replace, last_video)
        self.play(
            last_video.restore,            
            Animation(simple_rules),
            brace.next_to, this_video, DOWN,
            this_video.highlight, YELLOW
        )

        #Combination rules
        self.play(
            Write(combination_rules),
            *[
                ApplyMethod(pi.change_mode, "confused")
                for pi in self.get_students()
            ]
        )
        self.dither(2)
        for rule in combination_rules:
            interior = VGroup(*rule[5:-1])
            added_anims = []
            if rule is combination_rules[-1]:
                inner_func = VGroup(*rule[-4:-2])
                self.play(inner_func.shift, 0.5*UP)
                added_anims = [
                    inner_func.shift, 0.5*DOWN,
                    inner_func.highlight, YELLOW
                ]
            self.play(
                interior.highlight, YELLOW,
                *added_anims,
                submobject_mode = "lagged_start"
            )
            self.dither()
        self.dither()

        #Address subtraction and division
        subtraction = TexMobject("\\sin(x)", "-", "x^2")
        decomposed_subtraction = TexMobject("\\sin(x)", "+(-1)\\cdot", "x^2")
        pre_division = TexMobject("\\frac{\\sin(x)}{x^2}")
        division = VGroup(
            VGroup(*pre_division[:6]),
            VGroup(*pre_division[6:7]),
            VGroup(*pre_division[7:]),
        )
        pre_decomposed_division = TexMobject("\\sin(x)\\cdot\\frac{1}{x^2}")
        decomposed_division = VGroup(
            VGroup(*pre_decomposed_division[:6]),
            VGroup(*pre_decomposed_division[6:9]),
            VGroup(*pre_decomposed_division[9:]),
        )
        for mob in subtraction, decomposed_subtraction, division, decomposed_division:
            mob.next_to(self.get_teacher(), UP+LEFT)

        top_group = VGroup(series, simple_rules, brace)
        combination_rules.save_state()
        self.play(
            top_group.next_to, SPACE_HEIGHT*UP, UP,
            combination_rules.to_edge, UP,
        )
        pairs = [
            (subtraction, decomposed_subtraction), 
            (division, decomposed_division)
        ]
        for question, answer in pairs:
            self.play(
                Write(question),
                combination_rules.fade, 0.2,
                self.get_students()[2].change_mode, "raise_right_hand",
                self.get_teacher().change_mode, "plain",
            )
            self.dither()
            answer[1].highlight(GREEN)
            self.play(
                Transform(question, answer),
                self.get_teacher().change_mode, "hooray",
                self.get_students()[2].change_mode, "plain",
            )
            self.dither()
            self.play(FadeOut(question))

        #Monstrous expression
        monster = TexMobject(
            "\\Big(",
            "e^{\\sin(x)} \\cdot",
            "\\cos\\big(",
            "\\frac{1}{x^3}",
            " + x^3",
            "\\big)",
            "\\Big)^4"
        )
        monster.next_to(self.get_pi_creatures(), UP)
        parts = [
            VGroup(*monster[3][2:]),
            VGroup(*monster[3][:2]),
            monster[4],
            VGroup(monster[2], monster[5]),
            monster[1],
            VGroup(monster[0], monster[6])
        ]
        modes = [
            "erm", "erm",
            "confused", 
            "sad", "sad",
            "pleading",
        ]
        for part, mode in zip(parts, modes):
            self.play(
                FadeIn(part, submobject_mode = "lagged_start"),
                self.get_teacher().change_mode, "raise_right_hand",
                *[
                    ApplyMethod(pi.change_mode, mode)
                    for pi in self.get_students()
                ]
            )
        self.dither(2)

        #Bring back combinations
        self.play(
            FadeOut(monster),
            combination_rules.restore,
            *[
                ApplyMethod(pi_creature.change_mode, "pondering")
                for pi_creature in self.get_pi_creatures()
            ]
        )
        self.dither(2)

class SumRule(GraphScene, ZoomedScene):
    CONFIG = {
        "x_labeled_nums" : [],
        "y_labeled_nums" : [],
        "y_axis_label" : "",
        "x_max" : 4,
        "x_axis_width" : 2*SPACE_WIDTH,
        "y_max" : 3,
        "graph_origin" : 2.5*DOWN + 3.5*LEFT,
        "graph_label_x_value" : 1.5,
        "example_input" : 0.5,
        "example_input_string" : "0.5",
        "dx" : 0.02,
        "zoomed_canvas_corner" : UP+LEFT,
        "zoomed_canvas_corner_buff" : SMALL_BUFF,
        "little_rectangle_start_position" : 2.5*LEFT,
        "zoom_factor" : 10,
        "tex_scale_factor" : 0.8,
    }
    def construct(self):
        self.write_function()
        self.add_graphs()
        self.ask_about_derivative()
        self.add_v_lines()
        self.show_df_graphically()
        self.show_df_algebraically()
        self.show_d_sine()
        self.show_d_x_squared()
        self.complete_derivative()
        self.revisit_ss_groups()

    def write_function(self):
        func_mob = TexMobject("f(x) = ", "\\sin(x)", "+", "x^2")
        func_mob.scale(self.tex_scale_factor)
        func_mob.highlight_by_tex("\\sin(x)", SINE_COLOR)
        func_mob.highlight_by_tex("x^2", X_SQUARED_COLOR)
        func_mob.to_corner(UP+RIGHT)
        self.add(func_mob)

        self.func_mob = func_mob

    def add_graphs(self):
        self.setup_axes()
        sine_graph = self.get_graph(np.sin, color = SINE_COLOR)
        parabola = self.get_graph(lambda x : x**2, color = X_SQUARED_COLOR)
        sum_graph = self.get_graph(
            lambda x : np.sin(x) + x**2, 
            color = SUM_COLOR
        )
        sine_label = self.get_graph_label(
            sine_graph, "\\sin(x)",
            x_val = self.graph_label_x_value,
            direction = UP+RIGHT,
            buff = 0,
        )
        sine_label.scale(self.tex_scale_factor)
        parabola_label = self.get_graph_label(
            parabola, "x^2", x_val = self.graph_label_x_value,
        )
        parabola_label.scale(self.tex_scale_factor)
        sum_label = self.get_graph_label(
            sum_graph, "f(x) = \\sin(x) + x^2", 
            x_val = self.graph_label_x_value,
            direction = LEFT,
        )
        sum_label.scale(
            self.tex_scale_factor,
            about_point = sum_label.get_corner(DOWN+RIGHT)
        )
        #Break up
        sum_label = VGroup(
            VGroup(*sum_label[:11]),
            VGroup(*sum_label[11:])
        )
        graphs = VGroup(sine_graph, parabola)
        labels = VGroup(sine_label, parabola_label)
        for label in labels:
            label.add_background_rectangle()

        for graph, label in zip(graphs, labels):
            self.play(
                ShowCreation(graph),
                Write(label)
            )
        self.dither()

        sine_v_lines, parabox_v_lines = [
            self.get_vertical_lines_to_graph(
                graph, x_max = 2, num_lines = 50,
                stroke_width = 2
            )
            for graph in sine_graph, parabola
        ]
        parabox_v_lines.shift(0.02*RIGHT)
        self.play(ShowCreation(sine_v_lines), Animation(labels))
        self.play(ShowCreation(parabox_v_lines), Animation(labels))
        self.dither()
        self.play(*[
            ApplyMethod(
                l1.shift, l2.get_end()-l1.get_start()
            )
            for l1, l2, in zip(sine_v_lines, parabox_v_lines)
        ] + [Animation(labels)])
        self.dither()

        # self.play(ReplacementTransform(graphs.copy(), sum_graph))
        self.play(ShowCreation(sum_graph))
        self.play(Write(sum_label, run_time = 2))
        self.dither()


        self.sum_graph = sum_graph
        self.parabola = parabola
        self.sine_graph = sine_graph
        self.sum_v_lines = VGroup(sine_v_lines, parabox_v_lines)
        self.graph_labels = labels

    def ask_about_derivative(self):
        deriv_q = TexMobject("{df ", "\\over dx}", "=", "???")
        deriv_q.scale(self.tex_scale_factor)
        deriv_q.next_to(self.func_mob, DOWN)
        self.play(Write(deriv_q))
        self.dither()

        self.deriv_q = deriv_q

    def add_v_lines(self):
        v_line, nudged_v_line = lines = VGroup(*[
            self.get_vertical_line_to_graph(
                x, self.sum_graph,
                line_class = DashedLine,
                dashed_segment_length = 0.025,
                color = WHITE
            )
            for x in self.example_input, self.example_input+self.dx
        ])
        dots = [
            Dot(line.get_bottom(), radius = 0.03, color = YELLOW)
            for line in lines
        ]
        labels = [
            TexMobject(
                str(self.example_input) + s
            ).next_to(dot, DOWN+vect, buff = MED_LARGE_BUFF)
            for s, dot, vect in zip(
                ["", "+dx"], dots, [LEFT, RIGHT]
            )
        ]
        arrows = [
            Arrow(
                label.get_corner(UP+vect), dot,
                buff = SMALL_BUFF,
                color = WHITE,
                tip_length = 0.1
            )
            for label, dot, vect in zip(labels, dots, [RIGHT, LEFT])
        ]

        self.play(
            FadeOut(self.sum_v_lines),
            Animation(self.graph_labels)
        )
        for line, dot, label, arrow in zip(lines, dots, labels, arrows):
            self.play(
                Write(label),
                ShowCreation(arrow)
            )
            self.play(
                ShowCreation(line),
                ShowCreation(dot)
            )
            self.dither()

    def show_df_graphically(self):
        ss_group = self.get_secant_slope_group(
            self.example_input, self.sum_graph,
            dx = self.dx,
            dx_label = "dx",
            df_label = "df",
            include_secant_line = False
        )

        self.animate_activate_zooming()
        self.play(
            self.little_rectangle.move_to, ss_group,
        )
        self.play(Write(ss_group))
        self.dither()

        self.ss_group = ss_group

    def show_df_algebraically(self):
        deriv = TexMobject(
            "df", "=", "d(\\sin(x))", "+", "d(x^2)"
        )
        deriv.scale(self.tex_scale_factor)
        deriv.next_to(self.deriv_q, DOWN, buff = MED_LARGE_BUFF)
        deriv.highlight_by_tex("df", SUM_COLOR)
        deriv.highlight_by_tex("d(\\sin(x))", SINE_COLOR)
        deriv.highlight_by_tex("d(x^2)", X_SQUARED_COLOR)

        self.play(FocusOn(self.deriv_q))
        self.play(ReplacementTransform(
            self.deriv_q[0].copy(),
            deriv[0]
        ))
        self.play(Write(VGroup(*deriv[1:])))
        self.dither()

        self.deriv = deriv

    def show_d_sine(self):
        ss_group = self.get_secant_slope_group(
            self.example_input, self.sine_graph,
            dx = self.dx,
            dx_label = "dx",
            df_label = "\\cos(0.5)dx",
            include_secant_line = False
        )
        for mob, vect in (ss_group.dx_label, UP), (ss_group.df_label, LEFT):
            mob.scale(4, about_point = mob.get_edge_center(vect))

        d_sine = self.deriv[2]
        brace = Brace(d_sine)
        cosine_dx = TexMobject("\\cos(x)", "dx")
        cosine_dx.scale(self.tex_scale_factor)
        cosine_dx.next_to(brace, DOWN)
        cosine_dx.highlight(d_sine.get_color())

        self.play(
            GrowFromCenter(brace),
            Write(cosine_dx)
        )
        self.dither()
        self.play(
            self.little_rectangle.move_to, ss_group,
        )
        self.dither()
        self.play(Write(ss_group))
        self.dither()

        self.cosine = cosine_dx[0]
        self.sine_ss_group = ss_group

    def show_d_x_squared(self):
        ss_group = self.get_secant_slope_group(
            self.example_input, self.parabola,
            dx = self.dx,
            dx_label = "dx",
            df_label = "2(0.5)dx",
            include_secant_line = False
        )
        for mob, vect in (ss_group.dx_label, UP), (ss_group.df_label, LEFT):
            mob.scale(3, about_point = mob.get_edge_center(vect))

        d_x_squraed = self.deriv[4]
        brace = Brace(d_x_squraed)
        two_x_dx = TexMobject("2x", "\\,dx")
        two_x_dx.scale(self.tex_scale_factor)
        two_x_dx.next_to(brace, DOWN)
        two_x_dx.highlight(d_x_squraed.get_color())

        self.play(FocusOn(two_x_dx))
        self.play(
            GrowFromCenter(brace),
            Write(two_x_dx)
        )
        self.dither()
        self.play(
            self.little_rectangle.move_to, ss_group,
        )
        self.dither()
        self.play(Write(ss_group))
        self.dither()

        self.two_x = two_x_dx[0]
        self.x_squared_ss_group = ss_group

    def complete_derivative(self):
        cosine = self.cosine.copy()
        two_x = self.two_x.copy()
        lhs = VGroup(*self.deriv_q[:3])
        to_fade = VGroup(*self.deriv_q[3:])
        for mob in cosine, two_x, lhs:
            mob.generate_target()
        lhs.target.next_to(self.func_mob, DOWN, aligned_edge = LEFT)
        cosine.target.next_to(lhs.target)
        plus = TexMobject("+").scale(self.tex_scale_factor)
        plus.next_to(cosine.target)
        two_x.target.next_to(plus)

        box = Rectangle(color = YELLOW)
        box.replace(VGroup(lhs.target, two_x.target), stretch = True)
        box.scale_in_place(1.2)

        self.play(FocusOn(self.deriv_q))
        self.play(
            Write(plus),
            FadeOut(
                to_fade, 
                rate_func = squish_rate_func(smooth, 0, 0.5)
            ),
            *map(MoveToTarget, [cosine, two_x, lhs]),
            run_time = 2
        )
        to_fade.highlight(BLACK)
        self.play(ShowCreation(box))
        self.dither(2)

    def revisit_ss_groups(self):
        for ss_group in self.sine_ss_group, self.ss_group:
            self.play(
                self.little_rectangle.move_to, ss_group,
                run_time = 2
            )
            self.dither(2)

class DiscussProducts(TeacherStudentsScene):
    def construct(self):
        wrong_product_rule = TexMobject(
            "\\frac{d(\\sin(x)x^2)}{dx}", 
            "\\ne",
            "\\left(\\frac{d(\\sin(x))}{dx}\\right)",
            "\\left(\\frac{d(x^2)}{dx}\\right)",
        )
        not_equals = wrong_product_rule[1]
        wrong_product_rule[2].highlight(SINE_COLOR)
        wrong_product_rule[3].highlight(X_SQUARED_COLOR)
        wrong_product_rule.next_to(
            self.get_teacher().get_corner(UP+LEFT),
            UP,
            buff = MED_LARGE_BUFF
        ).shift_onto_screen()

        self.teacher_says(
            "Products are a bit different",
            target_mode = "sassy"
        )
        self.dither(2)
        self.play(RemovePiCreatureBubble(
            self.get_teacher(), 
            target_mode = "raise_right_hand"
        ))
        self.play(Write(wrong_product_rule))
        self.change_student_modes(
            "pondering", "confused", "erm",
            added_anims = [
                not_equals.scale_in_place, 1.3,
                not_equals.highlight, RED
            ]
        )
        self.dither()
        self.teacher_says(
            "Think about the \\\\ underlying meaning",
            bubble_kwargs = {"height" : 3},
            added_anims = [
                wrong_product_rule.scale, 0.7,
                wrong_product_rule.to_corner, UP+LEFT
            ]
        )
        self.change_student_modes(*["pondering"]*3)
        self.dither(2)

class NotGraphsForProducts(GraphScene):
    CONFIG = {
        "y_max" : 25,
        "x_max" : 7,
    }
    def construct(self):
        self.setup_axes()
        sine_graph = self.get_graph(np.sin, color = SINE_COLOR)
        sine_graph.label = self.get_graph_label(
            sine_graph, "\\sin(x)",
            x_val = 3*np.pi/2,
            direction = DOWN
        )
        parabola = self.get_graph(
            lambda x : x**2, color = X_SQUARED_COLOR
        )
        parabola.label = self.get_graph_label(
            parabola, "x^2",
            x_val = 2.5,
            direction = UP+LEFT,
        )
        product_graph = self.get_graph(
            lambda x : np.sin(x)*(x**2), color = PRODUCT_COLOR
        )
        product_graph.label = self.get_graph_label(
            product_graph, "\\sin(x)x^2",
            x_val = 2.8,
            direction = UP+RIGHT,
            buff = 0
        )

        graphs = [sine_graph, parabola, product_graph]
        for graph in graphs:
            self.play(
                ShowCreation(graph),
                Write(graph.label, run_time = 2)
            )
        self.dither()

        everything = VGroup(*filter(
            lambda m : not m.is_subpath,
            self.get_mobjects()
        ))
        words = TextMobject("Not the best visualization")
        words.scale(1.5)
        words.shift(SPACE_HEIGHT*UP/2)
        words.add_background_rectangle()
        words.highlight(RED)
        self.play(
            everything.fade,
            Write(words)
        )
        self.dither()

class IntroduceProductAsArea(ReconfigurableScene):
    CONFIG = {
        "top_func" : np.sin,
        "top_func_label" : "\\sin(x)",
        "top_func_nudge_label" : "d(\\sin(x))",
        "top_func_derivative" : "\\cos(x)",
        "side_func" : lambda x : x**2,
        "side_func_label" : "x^2",
        "side_func_nudge_label" : "d(x^2)",
        "side_func_derivative" : "2x",
        "x_unit_to_space_unit" : 3,
        "box_kwargs" : {
            "fill_color" : YELLOW,
            "fill_opacity" : 0.75,
            "stroke_width" : 1,
        },
        "df_box_kwargs" : {
            "fill_color" : GREEN,
            "fill_opacity" : 0.75,
            "stroke_width" : 0,
        },
        "box_corner_location" : 6*LEFT+2.5*UP,
        "slider_center" : 3.5*RIGHT+2*DOWN,
        "slider_width" : 6,
        "slider_x_max" : 3,
        "x_slider_handle_height" : 0.25,
        "slider_handle_color" : BLUE,
        "default_x" : .75,
        "dx" : 0.1,
        "tiny_dx" : 0.01,
    }
    def construct(self):
        self.introduce_box()
        self.talk_though_sine()
        self.define_f_of_x()
        self.nudge_x()
        self.write_df()
        self.show_thinner_dx()
        self.expand_derivative()
        self.write_derivative_abstractly()
        self.write_mneumonic()

    def introduce_box(self):
        box, labels = self.box_label_group = self.get_box_label_group(self.default_x)
        self.x_slider = self.get_x_slider(self.default_x)

        self.play(Write(labels))
        self.play(DrawBorderThenFill(box))
        self.dither()
        for mob in self.x_slider:
            self.play(Write(mob, run_time = 1))
        self.dither()
        for new_x in 0.5, 2, self.default_x:
            self.animate_x_change(
                new_x, run_time = 2
            )
        self.dither()

    def talk_though_sine(self):
        x_axis = self.x_slider[0]
        graph = FunctionGraph(
            np.sin, x_min = 0, x_max = np.pi,
            color = SINE_COLOR
        )
        scale_factor = self.x_slider.get_width()/self.slider_x_max
        graph.scale(scale_factor)
        graph.move_to(x_axis.number_to_point(0), LEFT)

        label = TexMobject("\\sin(x)")
        label.highlight(SINE_COLOR)
        label.next_to(graph, UP)

        y_axis = x_axis.copy()
        y_axis.remove(*y_axis.numbers)

        v_line = Line(ORIGIN, UP, color = WHITE, stroke_width = 2)
        def v_line_update(v_line):
            x = x_axis.point_to_number(self.x_slider[1].get_top())
            v_line.scale_to_fit_height(np.sin(x)*scale_factor)
            v_line.move_to(x_axis.number_to_point(x), DOWN)
        v_line_update(v_line)

        self.play(
            Rotate(y_axis, np.pi/2, about_point = y_axis.get_left()),
            Animation(x_axis)
        )
        self.play(
            ShowCreation(graph),
            Write(label, run_time = 1)
        )
        self.play(ShowCreation(v_line))
        for x, rt in zip([0.25, np.pi/2, 3, self.default_x], [2, 4, 4, 2]):
            self.animate_x_change(
                x, run_time = rt, 
                added_anims = [
                    UpdateFromFunc(v_line, v_line_update)
                ]
            )
            self.dither()
        self.play(*it.chain(
            map(FadeOut, [y_axis, graph, label, v_line]),
            [Animation(x_axis)]
        ))
        self.dither()
        for x in 1, 0.5, self.default_x:
            self.animate_x_change(x)
        self.dither()

    def define_f_of_x(self):
        f_def = TexMobject(
            "f(x)", "=",
            self.top_func_label,
            self.side_func_label,
            "=", 
            "\\text{Area}"
        )
        f_def.to_corner(UP+RIGHT)
        f_def[-1].highlight(self.box_kwargs["fill_color"])

        box, labels = self.box_label_group

        self.play(Write(VGroup(*f_def[:-1])))
        self.play(Transform(
            box.copy().set_fill(opacity = 0), f_def[-1],
            run_time = 1.5,
        ))
        self.dither()

        self.f_def = f_def

    def nudge_x(self):
        box, labels = self.box_label_group
        nudge_label_group = self.get_nudge_label_group()
        original_dx = self.dx
        self.dx = self.tiny_dx
        thin_df_boxes = self.get_df_boxes()
        self.dx = original_dx
        df_boxes = self.get_df_boxes()
        right_box, corner_box, right_box = df_boxes
        df_box_labels = self.get_df_box_labels(df_boxes)

        self.play(*map(GrowFromCenter, nudge_label_group))
        self.animate_x_change(
            self.default_x+self.dx,
            rate_func = there_and_back,
            run_time = 2,
            added_anims = [Animation(nudge_label_group)]
        ) 
        self.dither()
        self.play(
            ReplacementTransform(thin_df_boxes, df_boxes),
            VGroup(*labels[1]).shift, right_box.get_width()*RIGHT,
            *map(GrowFromCenter, df_box_labels)
        )
        self.play(
            df_boxes.space_out_submobjects, 1.1,
            df_boxes.move_to, box, UP+LEFT,
            *[
                MaintainPositionRelativeTo(label, box)
                for label, box in zip(
                    df_box_labels, [right_box, corner_box]
                )
            ]
        )
        self.dither()

        self.df_boxes = df_boxes
        self.df_box_labels = df_box_labels
        self.x_slider.add(nudge_label_group)

    def get_nudge_label_group(self):
        line, triangle, x_mob = self.x_slider
        dx_line = Line(*[
            line.number_to_point(self.x_slider.x_val + num)
            for num in 0, self.dx,
        ])
        dx_line.set_stroke(
            self.df_box_kwargs["fill_color"], 
            width = 6
        )
        brace = Brace(dx_line, UP, buff = SMALL_BUFF)
        brace.stretch_to_fit_height(0.2)
        brace.next_to(dx_line, UP, buff = SMALL_BUFF)
        brace.set_stroke(width = 1)
        dx = TexMobject("dx")
        dx.scale(0.7)
        dx.next_to(brace, UP, buff = SMALL_BUFF)
        dx.highlight(dx_line.get_color())

        return VGroup(dx_line, brace, dx)

    def get_df_boxes(self):
        box, labels = self.box_label_group
        alt_box = self.get_box(self.x_slider.x_val + self.dx)

        h, w = box.get_height(), box.get_width()
        dh, dw = alt_box.get_height()-h, alt_box.get_width()-w
        heights_and_widths = [(dh, w), (dh, dw), (h, dw)]
        vects = [DOWN, DOWN+RIGHT, RIGHT]
        df_boxes = VGroup(*[
            Rectangle(
                height = height, width = width, **self.df_box_kwargs
            ).next_to(box, vect, buff = 0)
            for (height, width), vect in zip(
                heights_and_widths, vects
            )
        ])
        return df_boxes

    def get_df_box_labels(self, df_boxes):
        bottom_box, corner_box, right_box = df_boxes
        result = VGroup()
        quads = [
            (right_box, UP, self.top_func_nudge_label, LEFT),
            (corner_box, RIGHT, self.side_func_nudge_label, ORIGIN),
        ]
        for box, vect, label_tex, aligned_edge in quads:
            brace = Brace(box, vect)
            label = TexMobject(label_tex)
            label.next_to(
                brace, vect,
                aligned_edge = aligned_edge,
                buff = SMALL_BUFF
            )
            label.highlight(df_boxes[0].get_color())
            result.add(VGroup(brace, label))
        return result

    def write_df(self):
        deriv = TexMobject(
            "df", "=", 
            self.top_func_label, 
            self.side_func_nudge_label,
            "+",
            self.side_func_label,
            self.top_func_nudge_label,
        )
        deriv.scale(0.9)
        deriv.next_to(self.f_def, DOWN, buff = LARGE_BUFF)
        deriv.to_edge(RIGHT)
        for submob, tex in zip(deriv, deriv.expression_parts):
            if tex.startswith("d"):
                submob.highlight(self.df_box_kwargs["fill_color"])
        bottom_box_area = VGroup(*deriv[2:4])
        right_box_area = VGroup(*deriv[5:7])

        bottom_box, corner_box, right_box = self.df_boxes
        plus = TexMobject("+").set_fill(opacity = 0)
        df_boxes_copy = VGroup(
            bottom_box.copy(),
            plus,
            right_box.copy(),
            plus.copy(),
            corner_box.copy(),
        )

        self.deriv = deriv
        self.df_boxes_copy = df_boxes_copy
        box, labels = self.box_label_group
        self.full_box_parts = VGroup(*it.chain(
            [box], self.df_boxes, labels, self.df_box_labels
        ))

        self.play(Write(VGroup(*deriv[:2])))
        self.play(
            df_boxes_copy.arrange_submobjects,
            df_boxes_copy.set_fill, None, self.df_box_kwargs["fill_opacity"],
            df_boxes_copy.next_to, deriv[1]
        )
        deriv.submobjects[4] = df_boxes_copy[1]
        self.dither()

        self.highlight_right_boxes()
        self.highlight_bottom_boxes()
        self.describe_bottom_box(bottom_box_area)
        self.describe_right_box(right_box_area)
        self.ignore_corner()

        # self.add(deriv)

    def highlight_boxes_and_label(self, boxes, label):
        boxes.save_state()
        label.save_state()
        self.play(
            boxes.highlight, RED,
            label.highlight, RED,
        )
        self.play(
            label[1].scale_in_place, 1.1,
            rate_func = there_and_back
        )
        self.play(boxes.restore, label.restore)
        self.dither()

    def highlight_right_boxes(self):
        self.highlight_boxes_and_label(
            VGroup(*self.df_boxes[1:]),
            self.df_box_labels[0]
        )

    def highlight_bottom_boxes(self):
        self.highlight_boxes_and_label(
            VGroup(*self.df_boxes[:-1]),
            self.df_box_labels[1]
        )

    def describe_bottom_box(self, bottom_box_area):
        bottom_box = self.df_boxes[0]
        bottom_box_copy = self.df_boxes_copy[0]
        other_box_copies = VGroup(*self.df_boxes_copy[1:])
        top_label = self.box_label_group[1][0]
        right_label = self.df_box_labels[1]

        faders = VGroup(*filter(
            lambda m : m not in [bottom_box, top_label, right_label],
            self.full_box_parts
        ))
        faders.save_state()

        self.play(faders.fade, 0.8)
        self.dither()
        self.play(FocusOn(bottom_box_copy))
        self.play(
            ReplacementTransform(bottom_box_copy, bottom_box_area),
            other_box_copies.next_to, bottom_box_area, RIGHT
        )
        self.dither()
        self.play(faders.restore)

    def describe_right_box(self, right_box_area):
        right_box = self.df_boxes[2]
        right_box_copy = self.df_boxes_copy[2]
        right_box_area.next_to(self.df_boxes_copy[1])
        other_box_copies = VGroup(*self.df_boxes_copy[3:])
        top_label = self.df_box_labels[0]
        right_label = self.box_label_group[1][1]

        faders = VGroup(*filter(
            lambda m : m not in [right_box, top_label, right_label],
            self.full_box_parts
        ))
        faders.save_state()

        self.play(faders.fade, 0.8)
        self.dither()
        self.play(FocusOn(right_box_copy))
        self.play(
            ReplacementTransform(right_box_copy, right_box_area),                        
            other_box_copies.next_to, right_box_area, DOWN, 
            MED_SMALL_BUFF, RIGHT,

        )
        self.dither()
        self.play(faders.restore)

    def ignore_corner(self):
        corner = self.df_boxes[1]
        corner.save_state()
        corner_copy = VGroup(*self.df_boxes_copy[-2:])
        words = TextMobject("Ignore")
        words.highlight(RED)
        words.next_to(corner_copy, LEFT, buff = LARGE_BUFF)
        words.shift(MED_SMALL_BUFF*DOWN)
        arrow = Arrow(words, corner_copy, buff = SMALL_BUFF, color = RED)

        self.play(
            corner.highlight, RED,
            corner_copy.highlight, RED,
        )
        self.dither()
        self.play(Write(words), ShowCreation(arrow))
        self.dither()
        self.play(*map(FadeOut, [words, arrow, corner_copy]))
        self.dither()
        corner_copy.highlight(BLACK)

    def show_thinner_dx(self):
        self.transition_to_alt_config(dx = self.tiny_dx)

    def expand_derivative(self):
        # self.play(
        #     self.deriv.next_to, self.f_def, DOWN, MED_LARGE_BUFF,
        #     self.deriv.shift_onto_screen
        # )
        # self.dither()

        expanded_deriv = TexMobject(
            "df", "=", 
            self.top_func_label, 
            self.side_func_derivative,
            "\\,dx",
            "+", 
            self.side_func_label,
            self.top_func_derivative, 
            "\\,dx"
        )
        final_deriv = TexMobject(
            "{df \\over ", "dx}", "=", 
            self.top_func_label, 
            self.side_func_derivative,
            "+", 
            self.side_func_label,
            self.top_func_derivative, 
        )
        color = self.deriv[0].get_color()
        for new_deriv in expanded_deriv, final_deriv:        
            for submob, tex in zip(new_deriv, new_deriv.expression_parts):
                for substr in "df", "dx", self.top_func_derivative, self.side_func_derivative:
                    if substr in tex:
                        submob.highlight(color)
            new_deriv.scale(0.9)
            new_deriv.next_to(self.deriv, DOWN, buff = MED_LARGE_BUFF)
            new_deriv.shift_onto_screen()

        for index in 3, 6:
            self.deriv.submobjects.insert(
                index+1, self.deriv[index].copy()
            )
        self.play(ReplacementTransform(
            self.deriv.copy(), expanded_deriv
        ))
        self.dither()
        self.play(*[
            Transform(
                expanded_deriv[i], final_deriv[j],
                path_arc = -np.pi/2
            )
            for i, j in [
                (0, 0),
                (1, 2),
                (2, 3),
                (3, 4),
                (4, 1),
                (5, 5),
                (6, 6),
                (7, 7),
                (8, 1),
            ]
        ])
        self.dither()

    def write_derivative_abstractly(self):
        self.transition_to_alt_config(
            return_to_original_configuration = False,
            top_func_label = "g(x)",
            top_func_nudge_label = "dg",
            top_func_derivative = "\\frac{dg}{dx}",
            side_func_label = "h(x)",
            side_func_nudge_label = "dh",
            side_func_derivative = "\\frac{dh}{dx}",
        )
        self.dither()

    def write_mneumonic(self):
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_edge(DOWN)
        morty.shift(2*LEFT)
        words = TextMobject(
            "``Left ", "d(Right) ", "+", " Right ", "d(Left)", "''",
            arg_separator = ""
        )
        VGroup(words[1], words[4]).highlight(self.df_boxes[0].get_color())
        words.scale(0.7)
        words.next_to(morty.get_corner(UP+LEFT), UP)
        words.shift_onto_screen()

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "raise_right_hand",
            Write(words)
        )
        self.dither()

    ###############

    def animate_x_change(
        self, target_x, 
        box_label_group = None, 
        x_slider = None,
        **kwargs
        ):
        box_label_group = box_label_group or self.box_label_group
        x_slider = x_slider or self.x_slider
        kwargs["run_time"] = kwargs.get("run_time", 2)
        added_anims = kwargs.get("added_anims", [])

        start_x = x_slider.x_val
        def update_box_label_group(box_label_group, alpha):
            new_x = interpolate(start_x, target_x, alpha)
            new_box_label_group = self.get_box_label_group(new_x)
            Transform(box_label_group, new_box_label_group).update(1)
        
        def update_x_slider(x_slider, alpha):
            new_x = interpolate(start_x, target_x, alpha)
            new_x_slider = self.get_x_slider(new_x)
            Transform(x_slider, new_x_slider).update(1)

        self.play(
            UpdateFromAlphaFunc(
                box_label_group, 
                update_box_label_group
            ),
            UpdateFromAlphaFunc(
                x_slider, 
                update_x_slider
            ),
            *added_anims,
            **kwargs
        )
        x_slider.x_val = target_x

    def get_x_slider(self, x):
        numbers = range(int(self.slider_x_max) + 1)
        line = NumberLine(
            x_min = 0,
            x_max = self.slider_x_max,
            space_unit_to_num = float(self.slider_width)/self.slider_x_max,
            color = GREY,
            numbers_with_elongated_ticks = numbers,
            tick_frequency = 0.25,
        )
        line.add_numbers(*numbers)
        line.numbers.next_to(line, UP, buff = SMALL_BUFF)
        for number in line.numbers:
            number.add_background_rectangle()
        line.move_to(self.slider_center)

        triangle = RegularPolygon(
            3, start_angle = np.pi/2,
            fill_color = self.slider_handle_color,
            fill_opacity = 0.8,
            stroke_width = 0,
        )
        triangle.scale_to_fit_height(self.x_slider_handle_height)
        triangle.move_to(line.number_to_point(x), UP)

        x_mob = TexMobject("x")
        x_mob.next_to(triangle, DOWN, buff = SMALL_BUFF)

        result = VGroup(line, triangle, x_mob)
        result.x_val = x
        return result

    def get_box_label_group(self, x):
        box = self.get_box(x)
        labels = self.get_box_labels(box)
        return VGroup(box, labels)

    def get_box(self, x):
        box = Rectangle(
            width = self.x_unit_to_space_unit * self.top_func(x),
            height = self.x_unit_to_space_unit * self.side_func(x),
            **self.box_kwargs
        )
        box.move_to(self.box_corner_location, UP+LEFT)
        return box

    def get_box_labels(self, box):
        result = VGroup()
        for label_tex, vect in (self.top_func_label, UP), (self.side_func_label, RIGHT):
            brace = Brace(box, vect, min_num_quads = 5)
            label = TexMobject(label_tex)
            label.next_to(brace, vect, buff = SMALL_BUFF)
            result.add(VGroup(brace, label))
        return result

class MneumonicExample(TeacherStudentsScene):
    def construct(self):
        d, left, right, rp = deriv_q = TexMobject(
            "\\frac{d}{dx}(", "\\sin(x)", "x^2", ")"
        )
        deriv_q.to_edge(UP)

        words = TextMobject(
            "Left ", "d(Right) ", "+", " Right ", "d(Left)",
            arg_separator = ""
        )
        deriv = TexMobject("\\sin(x)", "2x", "+", "x^2", "\\cos(x)")
        for mob in words, deriv:
            VGroup(mob[1], mob[4]).highlight(GREEN)
            mob.next_to(deriv_q, DOWN, buff = MED_LARGE_BUFF)
        deriv.shift(words[2].get_center()-deriv[2].get_center())

        self.add(words)
        self.play(
            Write(deriv_q),
            self.get_teacher().change_mode, "raise_right_hand"
        )
        self.change_student_modes(*["pondering"]*3)
        for i, j, vect in [(0, 2, RIGHT), (2, 5, LEFT)]:
            these_words = VGroup(*words[i:j])
            these_terms = VGroup(*deriv[i:j])
            self.play(
                these_words.next_to, these_terms, DOWN,
                MED_LARGE_BUFF, vect
            )
            self.play(ReplacementTransform(
                these_words.copy(), these_terms
            ))
            self.dither()
        self.play(*it.chain(*[
            [pi.change_mode, "confused", pi.look_at, deriv_q]
            for pi in self.get_pi_creatures()
        ]))
        self.dither()

class ConstantMultiplication(TeacherStudentsScene):
    def construct(self):
        question = TextMobject("What about $\\dfrac{d}{dx}(2\\sin(x))$?")
        answer = TextMobject("2\\cos(x)")
        self.teacher_says(question)
        self.dither()
        self.student_says(
            answer, target_mode = "hooray",
            added_anims = [question.copy().to_edge, UP]
        )
        self.play(self.get_teacher().change_mode, "happy")
        self.change_student_modes("pondering", "hooray", "pondering")
        self.dither(3)

class ConstantMultiplicationFigure(IntroduceProductAsArea):
    CONFIG = {
        "side_func" : lambda x : 1,
        "side_func_label" : "\\text{Constant}",
        "side_func_nudge_label" : "",
        "side_func_derivative" : "",
        "x_unit_to_space_unit" : 3,
        "default_x" : 0.5,
        "dx" : 0.1
    }
    def construct(self):
        self.box_label_group = self.get_box_label_group(self.default_x)
        self.x_slider = self.get_x_slider(self.default_x)
        # df_boxes = self.get_df_boxes()
        # df_box_labels = self.get_df_box_labels(df_boxes)

        self.add(self.box_label_group, self.x_slider)
        self.nudge_x()

class ShoveXSquaredInSine(Scene):
    def construct(self):
        title = TextMobject("Function composition")
        title.to_edge(UP)

        sine = TexMobject("g(", "x", ")", "=", "\\sin(", "x", ")")
        sine.highlight(SINE_COLOR)
        x_squared = TexMobject("h(x)", "=", "x^2")
        x_squared.highlight(X_SQUARED_COLOR)
        group = VGroup(sine, x_squared)
        group.arrange_submobjects(buff = LARGE_BUFF)
        group.shift(UP)
        composition = TexMobject(
            "g(", "h(x)", ")", "=", "\\sin(", "x^2", ")"
        )
        for i in 0, 2, 4, 6:
            composition[i].highlight(SINE_COLOR)
        for i in 1, 5:
            composition[i].highlight(X_SQUARED_COLOR)
        composition.next_to(group, DOWN, buff = LARGE_BUFF)

        brace = Brace(VGroup(*composition[-3:]), DOWN)
        deriv_q = brace.get_text("Derivative?")

        self.add(group)
        self.play(Write(title))
        self.dither()
        triplets = [
            [sine, (0, 2), (0, 2)],
            [x_squared, (0,), (1,)],
            [sine, (3, 4, 6), (3, 4, 6)],
            [x_squared, (2,), (5,)]
        ]
        for premob, pre_indices, comp_indicies in triplets:
            self.play(*[
                ReplacementTransform(
                    premob[i].copy(), composition[j]
                )
                for i, j in zip(pre_indices, comp_indicies)
            ])
            self.dither()
        self.dither()
        self.play(
            GrowFromCenter(brace),
            Write(deriv_q)
        )
        self.dither()

class ThreeLinesChainRule(Scene):
    CONFIG = {
        "default_x" : 0.5,
        "line_configs" : [
            {
                "x_min" : 0,
                "x_max" : 3,
                "numbers_to_show" : range(4),
                "tick_frequency" : 0.25,
            },
            {
                "x_min" : 0,
                "x_max" : 9,
                "numbers_to_show" : range(0, 10, 2),
                "tick_frequency" : 1,
            },
            {
                "x_min" : -2,
                "x_max" : 2,
                "numbers_to_show" : range(-2, 3),
                "tick_frequency" : 0.25,
            },
        ],
        "line_width" : 6,
    }
    def construct(self):
        lines_group = self.get_three_lines_group()

        self.add(lines_group)

    def get_three_line_group(self, x):
        number_lines = VGroup(*[
            self.get_line(x, **line_config)
            for line_config in self.line_configs
        ])
        number_lines.arrange_submobjects(DOWN, buff = LARGE_BUFF)
        return number_lines

    def get_number_line(self, x, **line_config):
        number_line = NumberLine(**line_config)









































