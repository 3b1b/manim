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

from topics.common_scenes import OpeningQuote, PatreonThanks

from eoc.graph_scene import *

class Chapter7OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            " Calculus required ",
            "continuity",
            ", and ",
            "continuity ",
            "was supposed to require the ",
            "infinitely little",
            "; but nobody could discover what the ",
            "infinitely little",
            " might be. ",
        ],
        "quote_arg_separator" : "",
        "highlighted_quote_terms" : {
            "continuity" : BLUE,
            "infinitely" : GREEN,
        },
        "author" : "Bertrand Russell",
    }

class ThisVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        deriv_videos = VGroup(*series[1:6])
        this_video = series[6]
        integral_videos = VGroup(*series[7:9])
        video_groups = [deriv_videos, this_video, integral_videos]

        braces = map(Brace, video_groups)
        deriv_brace, this_brace, integral_brace = braces

        tex_mobs = [
            TexMobject(*args)
            for args in [
                ("{df ", " \\over \\, ", " dx}"),
                ("\\lim_{h \\to 0}",),
                ("\\int ", "f(x)", "\\,dx"),
            ]
        ]
        deriv_tex, this_tex, integral_tex = tex_mobs
        for tex_mob, brace in zip(tex_mobs, braces):
            tex_mob.highlight_by_tex("f", GREEN)
            tex_mob.highlight_by_tex("dx", YELLOW)
            tex_mob.next_to(brace, DOWN)
        integral_tex.shift(LARGE_BUFF*RIGHT)

        lim_to_deriv_arrow = Arrow(this_tex, deriv_tex, color = WHITE)

        self.add(series)
        for index in 0, 2:
            videos = video_groups[index]
            brace = braces[index]
            tex_mob = tex_mobs[index]
            self.play(ApplyWave(
                videos,
                apply_function_kwargs = {"maintain_smoothness" : False}
            ))
            self.play(
                GrowFromCenter(brace),
                Write(tex_mob, run_time = 2)
            )
            self.dither()
        self.play(self.get_teacher().change_mode, "raise_right_hand")
        self.play(
            this_video.highlight, YELLOW,
            GrowFromCenter(this_brace)
        )
        self.play(Write(this_tex))
        self.dither()
        self.play(ShowCreation(lim_to_deriv_arrow))
        self.change_student_modes(*["happy"]*3)
        self.dither(2)

class LimitJustMeansApproach(PiCreatureScene):
    CONFIG = {
        "dx_color" : GREEN,
        "max_num_zeros" : 7,
    }
    def construct(self):
        limit_expression = self.get_limit_expression()
        limit_expression.shift(2*LEFT)
        limit_expression.to_edge(UP)

        evaluated_expressions = self.get_evaluated_expressions()
        evaluated_expressions.next_to(limit_expression, DOWN, buff = LARGE_BUFF)
        brace = Brace(evaluated_expressions[0][-1], DOWN)
        question = TextMobject("What does this ``approach''?")
        question.next_to(brace, DOWN)

        point = VectorizedPoint(limit_expression.get_right())
        expression = VGroup(
            limit_expression[1].copy(), 
            point, point.copy()
        )
        self.add(limit_expression)
        self.change_mode("raise_right_hand")
        for next_expression in evaluated_expressions:
            next_expression.move_to(evaluated_expressions[0], RIGHT)
            self.play(
                Transform(
                    expression, next_expression,
                    submobject_mode = "lagged_start",
                    lag_factor = 1.2,
                ),
                self.pi_creature.look_at, next_expression[-1]
            )
            if brace not in self.get_mobjects():
                self.play(
                    GrowFromCenter(brace),
                    Write(question)
                )
            self.dither(0.5)
        self.dither(2)

    def create_pi_creature(self):
        self.pi_creature = Mortimer().flip()
        self.pi_creature.to_corner(DOWN+LEFT)
        return self.pi_creature

    def get_limit_expression(self):
        lim = TexMobject("\\lim_", "{dx", " \\to 0}")
        lim.highlight_by_tex("dx", self.dx_color)
        ratio = self.get_expression("dx")
        ratio.next_to(lim, RIGHT)
        limit_expression = VGroup(lim, ratio)
        return limit_expression

    def get_evaluated_expressions(self):
        result = VGroup()
        for num_zeros in range(1, self.max_num_zeros+1):
            dx_str = "0." + "0"*num_zeros + "1"
            expression = self.get_expression(dx_str)            
            dx = float(dx_str)
            ratio = ((2+dx)**3-2**3)/dx
            ratio_mob = TexMobject("%.6f\\dots"%ratio)
            group = VGroup(expression, TexMobject("="), ratio_mob)
            group.arrange_submobjects(RIGHT)
            result.add(group)
        return result

    def get_expression(self, dx):
        result = TexMobject(
            "{(2 + ", str(dx), ")^3 - 2^3 \\over", str(dx)
        )
        result.highlight_by_tex(dx, self.dx_color)
        return result

class RefreshOnDerivativeDefinition(GraphScene):
    CONFIG = {
        "start_x" : 2,
        "start_dx" : 0.7,
        "df_color" : YELLOW,
        "dx_color" : GREEN,
        "secant_line_color" : MAROON_B,
    }
    def construct(self):
        self.setup_axes()
        def func(x):
            u = 0.3*x - 1.5
            return -u**3 + 5*u + 7
        graph = self.get_graph(func)
        graph_label = self.get_graph_label(graph)
        start_x_v_line, nudged_x_v_line = [
            self.get_vertical_line_to_graph(
                self.start_x + nudge, graph, 
                line_class = DashedLine,
                color = RED
            )
            for nudge in 0, self.start_dx
        ]
        nudged_x_v_line.save_state()
        ss_group = self.get_secant_slope_group(
            self.start_x, graph,
            dx = self.start_dx,
            dx_label = "dx",
            df_label = "df",
            df_line_color = self.df_color,
            dx_line_color = self.dx_color,
            secant_line_color = self.secant_line_color,
        )
        derivative = TexMobject(
            "{df", "\\over \\,", "dx}", "(", str(self.start_x), ")"
        )
        derivative.highlight_by_tex("df", self.df_color)
        derivative.highlight_by_tex("dx", self.dx_color)
        derivative.highlight_by_tex(str(self.start_x), RED)
        df = derivative.get_part_by_tex("df")
        dx = derivative.get_part_by_tex("dx")
        input_x = derivative.get_part_by_tex(str(self.start_x))
        derivative.move_to(self.coords_to_point(7, 4))
        derivative.save_state()
        deriv_brace = Brace(derivative)
        dx_to_0 = TexMobject("dx", "\\to 0")
        dx_to_0.highlight_by_tex("dx", self.dx_color)
        dx_to_0.next_to(deriv_brace, DOWN)

        #Introduce graph
        self.play(ShowCreation(graph))
        self.play(Write(graph_label, run_time = 1))
        self.play(Write(derivative))
        self.dither()
        input_copy = input_x.copy()
        self.play(
            input_copy.next_to, 
            self.coords_to_point(self.start_x, 0),
            DOWN
        )
        self.play(ShowCreation(start_x_v_line))
        self.dither()

        #ss_group_development
        self.play(
            ShowCreation(ss_group.dx_line),
            ShowCreation(ss_group.dx_label),
        )
        self.dither()
        self.play(ShowCreation(ss_group.df_line))
        self.play(Write(ss_group.df_label))
        self.dither(2)
        self.play(
            ReplacementTransform(ss_group.dx_label.copy(), dx),
            ReplacementTransform(ss_group.df_label.copy(), df),
            run_time = 2
        )
        self.play(ShowCreation(ss_group.secant_line))
        self.dither()

        #Let dx approach 0
        self.play(
            GrowFromCenter(deriv_brace),
            Write(dx_to_0),
        )
        self.animate_secant_slope_group_change(
            ss_group,
            target_dx = 0.01,
            run_time = 5,
        )
        self.dither()

        #Write out fuller limit
        new_deriv = TexMobject(
            "{f", "(", str(self.start_x), "+", "dx", ")", 
            "-", "f", "(", str(self.start_x), ")",
            "\\over \\,", "dx"
        )
        new_deriv.highlight_by_tex("dx", self.dx_color)
        new_deriv.highlight_by_tex("f", self.df_color)
        new_deriv.highlight_by_tex(str(self.start_x), RED)
        deriv_to_new_deriv = dict([
            (
                VGroup(derivative.get_part_by_tex(s)), 
                VGroup(*new_deriv.get_parts_by_tex(s))
            )
            for s in ["f", "over", "dx", "(", str(self.start_x), ")"]
        ])
        covered_new_deriv_parts = list(it.chain(*deriv_to_new_deriv.values()))
        uncovered_new_deriv_parts = filter(
            lambda part : part not in covered_new_deriv_parts,
            new_deriv
        )
        new_deriv.move_to(derivative)
        new_brace = Brace(new_deriv, DOWN)

        self.animate_secant_slope_group_change(
            ss_group,
            target_dx = self.start_dx,
            run_time = 2
        )
        self.play(ShowCreation(nudged_x_v_line))
        self.dither()
        self.play(*[
            ReplacementTransform(*pair, run_time = 2)
            for pair in deriv_to_new_deriv.items()
        ]+[
            Transform(deriv_brace, new_brace),
            dx_to_0.next_to, new_brace, DOWN
        ])
        self.play(Write(VGroup(*uncovered_new_deriv_parts), run_time = 2))
        self.dither()

        #Introduce limit notation
        lim = TexMobject("\\lim").scale(1.3)
        dx_to_0.generate_target()
        dx_to_0.target.scale(0.7)
        dx_to_0.target.next_to(lim, DOWN, buff = SMALL_BUFF)
        lim_group = VGroup(lim, dx_to_0.target)
        lim_group.move_to(new_deriv, LEFT)

        self.play(
            ReplacementTransform(deriv_brace, lim),
            MoveToTarget(dx_to_0),
            new_deriv.next_to, lim_group, RIGHT,
            run_time = 2
        )
        for sf, color in (1.2, YELLOW), (1/1.2, WHITE):
            self.play(
                lim.scale_in_place, sf,
                lim.highlight, color,
                submobject_mode = "lagged_start"
            )
        self.dither(2)
        self.animate_secant_slope_group_change(
            ss_group, target_dx = 0.01,
            run_time = 5,
            added_anims = [
                Transform(nudged_x_v_line, start_x_v_line, run_time = 5)
            ]
        )
        self.dither(2)

        #Record attributes for DiscussLowercaseDs below
        digest_locals(self)

class RantOpenAndClose(Scene):
    def construct(self):
        pass

class DiscussLowercaseDs(RefreshOnDerivativeDefinition, PiCreatureScene, ZoomedScene):
    CONFIG = {
        "zoomed_canvas_corner" : UP+LEFT
    }
    def construct(self):
        self.skip_superclass_anims()
        self.replace_dx_terms()
        self.compare_rhs_and_lhs()
        self.h_is_finite()

    def skip_superclass_anims(self):
        self.remove(self.pi_creature)        
        self.force_skipping()
        RefreshOnDerivativeDefinition.construct(self)
        self.revert_to_original_skipping_status()
        self.animate_secant_slope_group_change(
            self.ss_group, target_dx = self.start_dx,
            added_anims = [
                self.nudged_x_v_line.restore,
                Animation(self.ss_group.df_line)
            ],
            run_time = 1
        )
        everything = self.get_top_level_mobjects()
        everything.remove(self.derivative)
        self.play(*[
            ApplyMethod(mob.shift, 2.5*LEFT)
            for mob in everything
        ] + [
            FadeIn(self.pi_creature)
        ])

    def replace_dx_terms(self):
        dx_list = [self.dx_to_0[0]]
        dx_list += self.new_deriv.get_parts_by_tex("dx")
        mover = dx_list[0]
        mover_scale_val = 1.5
        mover.initial_right = mover.get_right()

        self.play(
            mover.scale, mover_scale_val,
            mover.next_to, self.pi_creature.get_corner(UP+LEFT), 
                UP, MED_SMALL_BUFF,
            self.pi_creature.change_mode, "sassy",
            path_arc = np.pi/2,
        )
        self.blink()
        self.dither()
        for tex in "\\Delta x", "h":
            dx_list_replacement = [
                TexMobject(
                    tex
                ).highlight(self.dx_color).move_to(dx, DOWN)
                for dx in dx_list
            ]
            self.play(
                Transform(
                    VGroup(*dx_list),
                    VGroup(*dx_list_replacement),
                ),
                self.pi_creature.change_mode, "raise_right_hand"
            )
            self.dither()
        self.play(
            mover.scale, 0.9,
            mover.move_to, mover.initial_right, RIGHT,
            self.pi_creature.change_mode, "happy",
        )
        self.play(
            self.dx_to_0.next_to, self.lim, DOWN, SMALL_BUFF,
        )
        self.dither()

    def compare_rhs_and_lhs(self):
        self.derivative.restore()
        lhs = self.derivative
        equals = TexMobject("=")
        rhs = VGroup(self.lim, self.dx_to_0, self.new_deriv)
        rhs.generate_target()
        rhs.target.next_to(self.pi_creature, UP, MED_LARGE_BUFF)
        rhs.target.to_edge(RIGHT)
        equals.next_to(rhs.target, LEFT)
        lhs.next_to(equals, LEFT)

        d_circles = VGroup(*[
            Circle(color = BLUE_B).replace(
                lhs.get_part_by_tex(tex)[0],
                stretch = True,
            ).scale_in_place(1.5).rotate_in_place(-np.pi/12)
            for tex in "df", "dx"
        ])
        d_words = TextMobject("""
            Limit idea is
            built in
        """)
        d_words.next_to(d_circles, DOWN)
        d_words.highlight(d_circles[0].get_color())

        lhs_rect, rhs_rect = rects = [
            Rectangle(color = GREEN_B).replace(
                mob, stretch = True
            )
            for mob in lhs, rhs.target
        ]
        for rect in rects:
            rect.stretch_to_fit_width(rect.get_width()+2*MED_SMALL_BUFF)
            rect.stretch_to_fit_height(rect.get_height()+2*MED_SMALL_BUFF)
        formal_definition_words = TextMobject("""
            Formal derivative definition 
        """)
        formal_definition_words.scale_to_fit_width(rhs_rect.get_width())
        formal_definition_words.next_to(rhs_rect, UP)
        formal_definition_words.highlight(rhs_rect.get_color())
        formal_definition_words.add_background_rectangle()

        df = VGroup(lhs.get_part_by_tex("df"))
        df_target = VGroup(*self.new_deriv.get_parts_by_tex("f"))

        self.play(
            MoveToTarget(rhs),
            Write(lhs),
            Write(equals),
        )
        self.play(
            ShowCreation(d_circles, run_time = 2),
            self.pi_creature.change_mode, "pondering"
        )
        self.play(Write(d_words))
        self.animate_secant_slope_group_change(
            self.ss_group, target_dx = 0.01,
            added_anims = [
                Transform(
                    self.nudged_x_v_line, self.start_x_v_line,
                    run_time = 3
                )
            ]
        )
        self.change_mode("thinking")
        self.dither(2)
        self.play(
            ShowCreation(lhs_rect),
            FadeOut(d_circles),
            FadeOut(d_words),
        )
        self.dither(2)
        self.play(
            ReplacementTransform(lhs_rect, rhs_rect),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.dither(2)
        self.play(ReplacementTransform(
            df.copy(), df_target, 
            path_arc = -np.pi/2,
            run_time = 2
        ))
        self.dither(2)
        self.play(Indicate(
            VGroup(*rhs[:2]),
            run_time = 2
        ))
        self.dither()

        self.play(Write(formal_definition_words))
        self.play(
            self.pi_creature.change_mode, "happy",
            self.pi_creature.look_at, formal_definition_words
        )
        self.dither(2)

        lhs.add_background_rectangle()
        self.add(rhs_rect, rhs)
        self.definition_group = VGroup(
            lhs, equals, rhs_rect, rhs, formal_definition_words
        )
        self.lhs, self.rhs, self.rhs_rect = lhs, rhs, rhs_rect

    def h_is_finite(self):
        self.play(
            FadeOut(self.graph_label),
            self.definition_group.center,
            self.definition_group.to_corner, UP+RIGHT,
            self.pi_creature.change_mode, "sassy",
            self.pi_creature.look_at, 4*UP
        )
        self.dither()


        words = TextMobject("No ``infinitely small''")
        words.next_to(
            self.definition_group, DOWN,
            buff = LARGE_BUFF, 
        ) 
        arrow = Arrow(words.get_top(), self.rhs_rect.get_bottom())
        arrow.highlight(WHITE)

        h_group = VGroup(
            self.rhs[1].get_part_by_tex("dx"),
            *self.rhs[2].get_parts_by_tex("dx")
        )
        moving_h = h_group[0]
        moving_h.original_center = moving_h.get_center()
        dx_group = VGroup()
        for h in h_group:
            dx = TexMobject("dx")
            dx.highlight(h.get_color())
            dx.replace(h, dim_to_match = 1)
            dx_group.add(dx)
        moving_dx = dx_group[0]       

        self.play(Write(words), ShowCreation(arrow))
        self.dither(2)

        self.play(
            moving_h.next_to, self.pi_creature.get_corner(UP+RIGHT), UP,
            self.pi_creature.change_mode, "raise_left_hand",
        )
        self.dither()
        moving_dx.move_to(moving_h)
        h_group.save_state()
        self.play(Transform(
            h_group, dx_group, 
            path_arc = np.pi,
        ))
        self.dither(2)
        self.play(h_group.restore, path_arc = np.pi)
        self.play(
            moving_h.move_to, moving_h.original_center,
            self.pi_creature.change_mode, "plain"
        )
        self.dither()

        self.activate_zooming()
        lil_rect = self.little_rectangle
        lil_rect.move_to(self.ss_group)
        lil_rect.scale_in_place(3)
        lil_rect.save_state()
        self.dither()
        self.add(self.rhs)
        self.play(
            lil_rect.scale_to_fit_width,
            self.ss_group.dx_line.get_width()*4,
            run_time = 4
        )
        self.dither()
        dx = self.ss_group.dx_label
        dx.save_state()
        h = TexMobject("h")
        h.highlight(dx.get_color())
        h.replace(dx, dim_to_match = 1)
        self.play(Transform(dx, h, path_arc = np.pi))
        self.play(Indicate(dx))
        self.dither()
        self.play(dx.restore, path_arc = np.pi)
        self.play(lil_rect.restore, run_time = 4)
        self.dither()
        self.disactivate_zooming()

class OtherViewsOfDx(TeacherStudentsScene):
    def construct(self):
        definition = TexMobject(
            "{df", "\\over \\,", "dx}", "(", "2", ")", "=",
            "\\lim", "_{h", "\\to", "0}", 
            "{f", "(", "2", "+", "h", ")", "-", "f", "(", "2", ")",
            "\\over \\,", "h}"
        )
        tex_to_color = {
            "df" : YELLOW,
            "f" : YELLOW,
            "dx" : GREEN,
            "h" : GREEN,
            "2" : RED
        }
        for tex, color in tex_to_color.items():
            definition.highlight_by_tex(tex, color)
        definition.scale(0.8)
        definition.to_corner(UP+LEFT)
        dx_group = VGroup(*definition.get_parts_by_tex("dx"))
        h_group = VGroup(*definition.get_parts_by_tex("h"))
        self.add(definition)

        statements = [
            TextMobject(*args)
            for args in [
                ("Why the new \\\\ variable", "$h$", "?"),
                ("$dx$", "is more $\\dots$ contentious.")
            ]
        ]
        for statement in statements:
            statement.h, statement.dx = [
                VGroup(*statement.get_parts_by_tex(
                    tex, substring = False
                )).highlight(GREEN)
                for tex in "$h$", "$dx$"
            ]


        self.force_skipping()
        self.student_says(
            statements[0],
            student_index = 1,
            target_mode = "confused"
        )
        self.play(ReplacementTransform(
            statements[0].h.copy(), h_group,
            run_time = 2,
            submobject_mode = "lagged_start",
            lag_factor = 1.5,
        ))
        self.dither()
        self.revert_to_original_skipping_status()##
        self.teacher_says(
            statements[1],
            target_mode = "hesitant",
        )
        self.play(ReplacementTransform(
            statements[1].dx.copy(), dx_group, 
            run_time = 2
        ))
        self.dither()



class GraphLimitExpression(GraphScene):
    CONFIG = {
        "start_x" : 2,
        "h_color" : GREEN,
        "f_color" : YELLOW,
        "start_x_color" : RED,
        "graph_origin" : 3*DOWN,
        "x_min" : -5,
        "x_max" : 5,
        "x_axis_label" : "$h$",
        "x_labeled_nums" : range(-5, 6),
        "y_min" : 0,
        "y_max" : 20,
        "y_tick_frequency" : 1,
        "y_labeled_nums" : range(5, 25, 5),
        "y_axis_label" : "",
    }
    def construct(self):
        self.force_skipping()

        def func(h):
            return 3*(2**2) + 3*2*h + h**2

        self.setup_axes()
        self.introduce_limit_term()
        self.show_graph()
        self.emphasize_non_definedness_at_0()
        self.point_out_limit_point()
        self.show_epsilon_delta_intuition()
        self.limits_as_a_language()

    def introduce_limit_term(self):
        abstract_limit = TexMobject(
            "\\lim", "_{h", "\\to 0}", "=",
            "{f", "(", str(self.start_x), "+", "h", ")", 
            "-", "f", "(", str(self.start_x), ")",
            "\\over \\,", "h}",
            arg_separator = "",
        )
        cube_limit = TexMobject(
            "\\lim", "_{h", "\\to 0}", "=",
            "{(", str(self.start_x), "+", "h", ")", "^3",
            "-", "(", str(self.start_x), ")", "^3",
            "\\over \\,", "h}",
            arg_separator = "",
        )
        tex_to_color = {
            "h" : self.h_color,
            "f" : self.f_color,
            "3" : self.f_color,
            str(self.start_x) : self.start_x_color
        }
        for expression in abstract_limit, cube_limit:
            for tex, color in tex_to_color.items():
                expression.highlight_by_tex(tex, color)
            expression.next_to(ORIGIN, RIGHT, LARGE_BUFF)
            expression.to_edge(UP)

        brace = Brace(VGroup(*abstract_limit[4:]), DOWN)
        graph_this = brace.get_text("Graph this")

        self.revert_to_original_skipping_status()
        self.add(abstract_limit)
        self.play(
            GrowFromCenter(brace),
            Write(graph_this)
        )
        self.dither()
        self.play(*[
            ReplacementTransform(
                VGroup(*abstract_limit.get_parts_by_tex(tex)),
                VGroup(*cube_limit.get_parts_by_tex(
                    tex if tex is not "f" else "3"
                )),
                run_time = 2,
            )
            for tex in [
                "lim", "h", "to", "=", "f", "(", 
                str(self.start_x), "+", ")", "-", "over"
            ]
        ])
        self.dither()
        for part in cube_limit.get_parts_by_tex("2"):
            self.play(Indicate(part))
        self.dither(2)

    def show_graph(self):
        pass

    def emphasize_non_definedness_at_0(self):
        pass

    def point_out_limit_point(self):
        pass

    def show_epsilon_delta_intuition(self):
        pass

    def limits_as_a_language(self):
        pass



























