# -*- coding: utf-8 -*-

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

class Goals(Scene):
    def construct(self):
        goals = [
            TextMobject("Goal %d:"%d, s)
            for d, s in [
                (1, "Formal definition of derivatives"),
                (2, "$(\\epsilon, \\delta)$ definition of a limit"),
                (3, "L'Hôpital's rule"),
            ]
        ]
        for goal in goals:
            goal.scale(1.3)
            goal.shift(3*DOWN).to_edge(LEFT)

        curr_goal = goals[0]
        self.play(FadeIn(curr_goal))
        self.dither(2)
        for goal in goals[1:]:
            self.play(Transform(curr_goal, goal))
            self.dither(2)

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
        opening, closing = [
            TextMobject(
                start, "Rant on infinitesimals", "$>$",
                arg_separator = ""
            )
            for start in "$<$", "$<$/"
        ]
        self.play(FadeIn(opening))
        self.dither(2)
        self.play(Transform(opening, closing))
        self.dither(2)

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

        #Zoom in
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
        self.dither()

        #Last approaching reference
        for target_dx in 3, 0.01, -2, 0.01:
            self.animate_secant_slope_group_change(
                self.ss_group, target_dx = target_dx,
                run_time = 4,
            )
            self.dither()

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
                ("$dx$", "is more $\\dots$ contentious."),
                ("$dx$", "is infinitely small"),
                ("$dx$", "is nothing more \\\\ than a symbol"),
            ]
        ]
        for statement in statements:
            statement.h, statement.dx = [
                VGroup(*statement.get_parts_by_tex(
                    tex, substring = False
                )).highlight(GREEN)
                for tex in "$h$", "$dx$"
            ]

        #Question
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

        #Teacher answer
        self.teacher_says(
            statements[1],
            target_mode = "hesitant",
            bubble_creation_class = FadeIn,
        )
        self.play(ReplacementTransform(
            statements[1].dx.copy(), dx_group, 
            run_time = 2,
        ))
        self.dither()

        #First alternate view
        moving_dx = dx_group.copy()
        bubble_intro = PiCreatureBubbleIntroduction(
            self.get_students()[2],
            statements[2],
            target_mode = "hooray",
            bubble_creation_class = FadeIn,
        )
        bubble_intro.update(1)
        dx_movement = Transform(
            moving_dx, statements[2].dx,
            run_time = 2
        )
        bubble_intro.update(0)
        self.play(
            bubble_intro, dx_movement,
            RemovePiCreatureBubble(self.get_teacher()),
        )   
        self.play(self.get_teacher().change_mode, "erm")
        self.dither()

        #Next alternate view
        bubble_intro = PiCreatureBubbleIntroduction(
            self.get_students()[0],
            statements[3],
            target_mode = "maybe",
            look_at_arg = 3*UP,
            bubble_creation_class = FadeIn,
        )
        bubble_intro.update(1)
        dx_movement = Transform(
            moving_dx, statements[3].dx,
            run_time = 2
        )
        bubble_intro.update(0)
        last_bubble = self.get_students()[2].bubble
        self.play(
            bubble_intro, dx_movement,
            FadeOut(last_bubble),
            FadeOut(last_bubble.content),
            *it.chain(*[
                [
                    pi.change_mode, "pondering", 
                    pi.look_at, bubble_intro.mobject
                ]
                for pi in self.get_students()[1:]
            ])
        )
        self.dither(3)
        
class GraphLimitExpression(GraphScene):
    CONFIG = {
        "start_x" : 2,
        "h_color" : GREEN,
        "f_color" : YELLOW,
        "two_color" : RED,
        "graph_origin" : 3*DOWN+LEFT,
        "x_min" : -8,
        "x_max" : 5,
        "x_axis_label" : "$h$",
        "x_labeled_nums" : range(-8, 6, 2),
        "y_min" : 0,
        "y_max" : 20,
        "y_tick_frequency" : 1,
        "y_labeled_nums" : range(5, 25, 5),
        "y_axis_label" : "",
        "big_delta" : 0.7,
        "small_delta" : 0.01,
    }
    def construct(self):
        self.func = lambda h : 3*(2**2) + 3*2*h + h**2
        self.setup_axes()
        self.introduce_function()
        self.emphasize_non_definedness_at_0()
        self.draw_limit_point_hole()
        self.show_limit()
        self.skeptic_asks()
        self.show_epsilon_delta_intuition()

    def introduce_function(self):
        expression = TexMobject(
            "{(", "2", "+", "h", ")", "^3",
            "-", "(", "2", ")", "^3",
            "\\over \\,", "h}",
            arg_separator = "",
        )
        limit = TexMobject("\\lim", "_{h", "\\to 0}")
        derivative = TexMobject(
            "{d(x^3)", "\\over \\,", "dx}", "(", "2", ")"
        )
        tex_to_color = {
            "h" : self.h_color,
            "dx" : self.h_color,
            "2" : self.two_color
        }
        for tex_mob in expression, limit, derivative:
            for tex, color in tex_to_color.items():
                tex_mob.highlight_by_tex(tex, color)
            tex_mob.next_to(ORIGIN, RIGHT, LARGE_BUFF)
            tex_mob.to_edge(UP)

        expression.save_state()
        expression.generate_target()
        expression.target.next_to(limit, RIGHT)
        brace = Brace(VGroup(limit, expression.target))
        derivative.next_to(brace, DOWN)

        graph = self.get_graph(self.func, color = BLUE)

        indices = [0, 6, 11, 13]
        for i, j in zip(indices, indices[1:]):
            group = VGroup(*expression[i:j])
            self.play(FadeIn(
                group,
                submobject_mode = "lagged_start",
                lag_factor = 1.5
            ))
            self.dither()
        self.play(ShowCreation(graph))
        self.dither()
        self.play(
            MoveToTarget(expression),
            FadeIn(limit, submobject_mode = "lagged_start"),
            GrowFromCenter(brace)
        )
        self.play(Write(derivative))
        self.dither(2)
        self.play(
            expression.restore,
            *map(FadeOut, [derivative, brace, limit])
        )
        self.dither()

        colored_graph = graph.copy().highlight(YELLOW)
        self.play(ShowCreation(colored_graph))
        self.dither()
        self.play(ShowCreation(graph))
        self.remove(colored_graph)
        self.dither()

        self.expression = expression
        self.limit = limit
        self.graph = graph

    def emphasize_non_definedness_at_0(self):
        expression = self.expression
        
        dot = Dot(self.graph_origin, color = GREEN)
        h_equals_0 = TexMobject("h", "=", "0", "?")
        h_equals_0.next_to(self.graph_origin, UP+RIGHT, LARGE_BUFF)
        for tex in "h", "0":
            h_equals_0.highlight_by_tex(tex, GREEN)

        arrow = Arrow(h_equals_0.get_left(), self.graph_origin)
        arrow.highlight(WHITE)

        new_expression = expression.copy()
        h_group = VGroup(*new_expression.get_parts_by_tex("h"))
        for h in h_group:
            zero = TexMobject("0")
            zero.highlight(h.get_color())
            zero.replace(h, dim_to_match = 1)
            Transform(h, zero).update(1)
        rhs = TexMobject("=", "{\\, 0\\,", "\\over \\,", "0\\,}")
        rhs.highlight_by_tex("0", GREEN)
        rhs.next_to(new_expression, RIGHT)
        equation = VGroup(new_expression, rhs)
        equation.next_to(expression, DOWN, buff = LARGE_BUFF)

        ud_brace = Brace(VGroup(*rhs[1:]), DOWN)
        undefined = TextMobject("Undefined")
        undefined.next_to(ud_brace, DOWN)
        undefined.to_edge(RIGHT)

        self.play(Write(h_equals_0, run_time = 2))
        self.play(*map(ShowCreation, [arrow, dot]))
        self.dither()
        self.play(ReplacementTransform(
            expression.copy(), new_expression
        ))
        self.dither()
        self.play(Write(rhs))
        self.dither()
        self.play(
            GrowFromCenter(ud_brace),
            Write(undefined)
        )
        self.dither(2)

        self.point_to_zero_group = VGroup(
            h_equals_0, arrow, dot
        )
        self.plug_in_zero_group = VGroup(
            new_expression, rhs, ud_brace, undefined
        )

    def draw_limit_point_hole(self):
        dx = 0.07
        color = self.graph.get_color()
        circle = Circle(
            radius = dx, 
            stroke_color = color,
            fill_color = BLACK,
            fill_opacity = 1,
        )
        circle.move_to(self.coords_to_point(0, 12))
        colored_circle = circle.copy()
        colored_circle.set_stroke(YELLOW)
        colored_circle.set_fill(opacity = 0)

        self.play(GrowFromCenter(circle))
        self.dither()
        self.play(ShowCreation(colored_circle))
        self.play(ShowCreation(
            circle.copy().set_fill(opacity = 0),
            remover = True
        ))
        self.remove(colored_circle)
        self.play(
            circle.scale_in_place, 0.3,
            run_time = 2,
            rate_func = wiggle
        )
        self.dither()

        self.limit_point_hole = circle

    def show_limit(self):
        dot = self.point_to_zero_group[-1]
        ed_group = self.get_epsilon_delta_group(self.big_delta)

        left_v_line, right_v_line = ed_group.delta_lines
        bottom_h_line, top_h_line = ed_group.epsilon_lines
        ed_group.delta_lines.save_state()
        ed_group.epsilon_lines.save_state()

        brace = Brace(ed_group.input_range, UP)
        brace_text = brace.get_text("Inputs around 0", buff = SMALL_BUFF)
        brace_text.add_background_rectangle()
        brace_text.shift(RIGHT)

        limit_point_hole_copy = self.limit_point_hole.copy()
        limit_point_hole_copy.set_stroke(YELLOW)
        h_zero_hole = limit_point_hole_copy.copy()
        h_zero_hole.move_to(self.graph_origin)

        ed_group.input_range.add(h_zero_hole)
        ed_group.output_range.add(limit_point_hole_copy)

        #Show range around 0
        self.play(
            FadeOut(self.plug_in_zero_group),
            FadeOut(VGroup(*self.point_to_zero_group[:-1])),
        )
        self.play(
            GrowFromCenter(brace),
            Write(brace_text),
            ReplacementTransform(dot, ed_group.input_range),
        )
        self.add(h_zero_hole)
        self.dither()
        self.play(
            ReplacementTransform(
                ed_group.input_range.copy(), 
                ed_group.output_range, 
                run_time = 2
            ),
        )
        self.remove(self.limit_point_hole)

        #Show approaching
        self.play(*map(FadeOut, [brace, brace_text]))
        for v_line, h_line in (right_v_line, top_h_line), (left_v_line, bottom_h_line):
            self.play(
                ShowCreation(v_line),
                ShowCreation(h_line)
            )
            self.dither()
            self.play(
                v_line.move_to, self.coords_to_point(0, 0), DOWN,
                h_line.move_to, self.coords_to_point(0, self.func(0)),
                run_time = 3
            )
            self.play(
                VGroup(h_line, v_line).set_stroke, GREY, 2,
            )
        self.dither()

        #Write limit
        limit = self.limit
        limit.next_to(self.expression, LEFT)
        equals, twelve = rhs = TexMobject("=", "12")
        rhs.next_to(self.expression, RIGHT)
        twelve_copy = twelve.copy()
        limit_group = VGroup(limit, rhs)

        self.play(Write(limit_group))
        self.dither()
        self.play(twelve_copy.next_to, top_h_line, RIGHT)
        self.dither()

        self.twelve_copy = twelve_copy
        self.ed_group = ed_group
        self.input_range_brace_group = VGroup(brace, brace_text)

    def skeptic_asks(self):
        randy = Randolph()
        randy.scale(0.9)
        randy.to_edge(DOWN)

        self.play(FadeIn(randy))
        self.play(PiCreatureSays(
            randy, """
                What \\emph{exactly} do you
                mean by ``approach''
            """,
            bubble_kwargs = {
                "height" : 3,
                "width" : 5,
                "fill_opacity" : 1,
                "direction" : LEFT,
            },
            target_mode = "sassy"
        ))
        self.remove(self.twelve_copy)
        self.play(randy.look, OUT)
        self.play(Blink(randy))
        self.dither()
        self.play(RemovePiCreatureBubble(
            randy, target_mode = "pondering",
            look_at_arg = self.limit_point_hole
        ))
        self.play(
            self.ed_group.delta_lines.restore,
            self.ed_group.epsilon_lines.restore,
            Animation(randy),
            rate_func = there_and_back,
            run_time = 5,
        )
        self.play(Blink(randy))
        self.play(FadeOut(randy))

    def show_epsilon_delta_intuition(self):
        self.play(
            FadeOut(self.ed_group.epsilon_lines),
            FadeIn(self.input_range_brace_group)
        )
        self.ed_group.epsilon_lines.restore()
        self.dither()
        self.play(
            self.ed_group.delta_lines.restore, 
            Animation(self.input_range_brace_group),
            run_time = 2
        )
        self.play(FadeOut(self.input_range_brace_group))
        self.play(
            ReplacementTransform(
                self.ed_group.input_range.copy(),
                self.ed_group.output_range,
                run_time = 2
            )
        )
        self.dither()
        self.play(*map(GrowFromCenter, self.ed_group.epsilon_lines))
        self.play(*[
            ApplyMethod(
                line.copy().set_stroke(GREY, 2).move_to,
                self.coords_to_point(0, self.func(0)),
                run_time = 3,
                rate_func = there_and_back,
                remover = True,
            )
            for line in self.ed_group.epsilon_lines
        ])
        self.dither()

        holes = VGroup(
            self.ed_group.input_range.submobjects.pop(),
            self.ed_group.output_range.submobjects.pop(),
        )
        holes.save_state()
        self.animate_epsilon_delta_group_change(
            self.ed_group,
            target_delta = self.small_delta,
            run_time = 8,
            rate_func = lambda t : smooth(t, 2),
            added_anims = [
                ApplyMethod(
                    hole.scale_in_place, 0.5,
                    run_time = 8
                )
                for hole in holes
            ]
        )
        self.dither()

        self.holes = holes

    #########

    def get_epsilon_delta_group(
        self, 
        delta,
        dashed_line_stroke_width = 3,
        dashed_line_length = 2*SPACE_HEIGHT,
        input_range_color = YELLOW,
        input_range_stroke_width = 6,
        ):
        kwargs = dict(locals())
        result = VGroup()
        kwargs.pop("self")
        result.delta = kwargs.pop("delta")
        result.kwargs = kwargs
        dashed_line = DashedLine(
            ORIGIN, dashed_line_length*RIGHT,
            stroke_width = dashed_line_stroke_width
        )
        x_values = [-delta, delta]
        x_axis_points = [self.coords_to_point(x, 0) for x in x_values]
        result.delta_lines = VGroup(*[
            dashed_line.copy().rotate(np.pi/2).move_to(
                point, DOWN
            )
            for point in x_axis_points
        ])
        result.epsilon_lines = VGroup(*[
            dashed_line.copy().move_to(
                self.coords_to_point(0, self.func(x))
            )
            for x in x_values
        ])
        basically_zero = 0.00001
        result.input_range, result.output_range = [
            VGroup(*[
                self.get_graph(
                    func,
                    color = input_range_color,
                    x_min = x_min,
                    x_max = x_max,
                )
                for x_min, x_max in [
                    (-delta, -basically_zero),
                    (basically_zero, delta),
                ]
            ]).set_stroke(width = input_range_stroke_width)
            for func in lambda h : 0, self.func
        ]

        result.digest_mobject_attrs()
        return result

    def animate_epsilon_delta_group_change(
        self, epsilon_delta_group, target_delta,
        **kwargs
        ):
        added_anims = kwargs.get("added_anims", [])
        start_delta = epsilon_delta_group.delta
        ed_group_kwargs = epsilon_delta_group.kwargs
        def update_ed_group(ed_group, alpha):
            delta = interpolate(start_delta, target_delta, alpha)
            new_group = self.get_epsilon_delta_group(
                delta, **ed_group_kwargs
            )
            Transform(ed_group, new_group).update(1)
            return ed_group

        self.play(
            UpdateFromAlphaFunc(
                epsilon_delta_group, update_ed_group,
                **kwargs
            ),
            *added_anims
        )

class LimitCounterExample(GraphLimitExpression):
    CONFIG = {
        "x_min" : -8,
        "x_max" : 8,
        "x_labeled_nums" : range(-8, 10, 2),
        "x_axis_width" : 2*SPACE_WIDTH - LARGE_BUFF,
        "y_min" : -4,
        "y_max" : 4,
        "y_labeled_nums" : range(-2, 4, 1),
        "y_axis_height" : 2*SPACE_HEIGHT+2*LARGE_BUFF,
        "graph_origin" : DOWN,
        "graph_color" : BLUE,
        "hole_radius" : 0.075,
        "big_delta" : 1.5,
        "small_delta" : 0.05,
    }
    def construct(self):
        def func(h):
            square = 0.25*h**2
            if h < 0:
                return -square + 1
            else:
                return square + 2
        self.func = func

        self.setup_axes()
        self.draw_graph()
        self.approach_zero()
        self.write_limit_not_defined()
        self.show_epsilon_delta_intuition()

    def draw_graph(self):
        epsilon = 0.1
        left_graph, right_graph = [
            self.get_graph(
                self.func,
                color = self.graph_color,
                x_min = x_min,
                x_max = x_max,
            )
            for x_min, x_max in [
                (self.x_min, -epsilon),
                (epsilon, self.x_max),
            ]
        ]
        left_hole = self.get_hole(0, 1, color = self.graph_color)
        right_hole = self.get_hole(0, 2, color = self.graph_color)
        graph = VGroup(
            left_graph, left_hole, 
            right_hole, right_graph
        )

        self.play(ShowCreation(graph, run_time = 5))
        self.dither()
        self.play(ReplacementTransform(
            left_hole.copy().set_stroke(YELLOW), right_hole
        ))
        self.dither()

        self.graph = graph
        self.graph_holes = VGroup(left_hole, right_hole)

    def approach_zero(self):
        ed_group = self.get_epsilon_delta_group(self.big_delta)
        left_v_line, right_v_line = ed_group.delta_lines
        bottom_h_line, top_h_line = ed_group.epsilon_lines
        ed_group.delta_lines.save_state()
        ed_group.epsilon_lines.save_state()

        right_lines = VGroup(right_v_line, top_h_line)
        left_lines = VGroup(left_v_line, bottom_h_line)

        basically_zero = 0.00001
        def update_lines(lines, alpha):
            v_line, h_line = lines
            sign = 1 if v_line is right_v_line else -1
            x_val = interpolate(sign*self.big_delta, sign*basically_zero, alpha)
            v_line.move_to(self.coords_to_point(x_val, 0), DOWN)
            h_line.move_to(self.coords_to_point(0, self.func(x_val)))
            return lines

        for lines in right_lines, left_lines:
            self.play(*map(ShowCreation, lines))
            self.play(UpdateFromAlphaFunc(
                lines, update_lines,
                run_time = 3
            ))
            self.play(lines.set_stroke, GREY, 3)
            self.dither()

        self.ed_group = ed_group

    def write_limit_not_defined(self):
        limit = TexMobject(
            "\\lim", "_{h", "\\to 0}", "f(", "h", ")"
        )
        limit.highlight_by_tex("h", GREEN)
        limit.move_to(self.coords_to_point(2, 1.5))

        words = TextMobject("is not defined")
        words.highlight(RED)
        words.next_to(limit, RIGHT, align_using_submobjects = True)

        limit_group = VGroup(limit, words)

        self.play(Write(limit))
        self.dither()
        self.play(Write(words))
        self.dither()
        self.play(limit_group.to_corner, UP+LEFT)
        self.dither()

    def show_epsilon_delta_intuition(self):
        ed_group = self.ed_group
        self.play(
            ed_group.delta_lines.restore,
            ed_group.epsilon_lines.restore,
        )
        self.play(ShowCreation(ed_group.input_range))
        self.dither()
        self.play(ReplacementTransform(
            ed_group.input_range.copy(),
            ed_group.output_range,
            run_time = 2
        ))
        self.graph.remove(*self.graph_holes)
        self.remove(*self.graph_holes)
        self.dither()
        self.animate_epsilon_delta_group_change(
            ed_group, target_delta = self.small_delta,
            run_time = 6
        )

        brace = Brace(self.ed_group.epsilon_lines, RIGHT, buff = SMALL_BUFF)
        brace_text = brace.get_text("Can't get \\\\ smaller", buff = SMALL_BUFF)
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.dither()
        run_time_rate_func_pairs = [
            (3, lambda t : 1 - there_and_back(t)),
            (1, lambda t : 1 - 0.2*there_and_back(3*t % 1)),
            (1, lambda t : 1 - 0.2*there_and_back(5*t % 1)),
        ]
        for run_time, rate_func in run_time_rate_func_pairs:
            self.animate_epsilon_delta_group_change(
                ed_group, target_delta = self.small_delta,
                run_time = run_time,
                rate_func = rate_func,
            )
            self.dither()

    #####

    def get_epsilon_delta_group(self, delta, **kwargs):
        ed_group = GraphLimitExpression.get_epsilon_delta_group(self, delta, **kwargs)
        color = ed_group.kwargs["input_range_color"]
        radius = min(delta/2, self.hole_radius)
        pairs = [
            (ed_group.input_range[0], (0, 0)),
            (ed_group.input_range[1], (0, 0)),
            (ed_group.output_range[0], (0, 1)),
            (ed_group.output_range[1], (0, 2)),
        ]
        for mob, coords in pairs:
            mob.add(self.get_hole(
                *coords, 
                color = color,
                radius = radius
            ))
        return ed_group

    def get_hole(self, *coords, **kwargs):
        color = kwargs.get("color", BLUE)
        radius = kwargs.get("radius", self.hole_radius)
        return Circle(
            radius = radius,
            stroke_color = color,
            fill_color = BLACK,
            fill_opacity = 1,
        ).move_to(self.coords_to_point(*coords))

class PrefaceToEpsilonDeltaDefinition(TeacherStudentsScene):
    def construct(self):
        title = TexMobject("(\\epsilon, \\delta) \\text{ definition}")
        title.next_to(self.get_teacher().get_corner(UP+LEFT), UP)
        title.save_state()
        title.shift(DOWN)
        title.set_fill(opacity = 0)

        self.play(
            title.restore,
            self.get_teacher().change_mode, "raise_right_hand",
        )
        self.change_student_modes(*["confused"]*3)
        self.dither()
        self.student_says(
            "Isn't that pretty \\\\ technical?",
            target_mode = "guilty",
            added_anims = [
                title.to_edge, UP,
                self.get_teacher().change_mode, "plain",
                self.get_teacher().look_at, self.get_students()[1].eyes
            ]
        )
        self.look_at(self.get_teacher().eyes, self.get_students())
        self.dither()
        self.teacher_says("", bubble_kwargs = {"stroke_width" : 0})
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = UP+LEFT,
            added_anims = [self.get_teacher().look_at, UP+LEFT]
        )
        self.dither(3)
        words = TextMobject(
            "It's a glimpse of\\\\",
            "real analysis"
        )
        words.highlight_by_tex("real", YELLOW)
        self.teacher_says(
            words, 
            bubble_kwargs = {"height" : 3, "width" : 6}
        )
        self.change_student_modes(*["happy"]*3)
        self.dither(6)

class EpsilonDeltaExample(GraphLimitExpression):
    def construct(self):
        self.skip_superclass_anims()

    def skip_superclass_anims(self):
        self.force_skipping()
        GraphLimitExpression.construct(self)
        self.animate_epsilon_delta_group_change(
            self.ed_group,
            target_delta = self.big_delta,
        )
        self.holes.restore()
        self.add(self.holes)
        self.revert_to_original_skipping_status()


















