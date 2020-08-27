# -*- coding: utf-8 -*-
from manimlib.imports import *

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

        braces = list(map(Brace, video_groups))
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
            tex_mob.set_color_by_tex("f", GREEN)
            tex_mob.set_color_by_tex("dx", YELLOW)
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
                direction = DOWN,
            ))
            self.play(
                GrowFromCenter(brace),
                Write(tex_mob, run_time = 2)
            )
        self.play(
            this_video.set_color, YELLOW,
            GrowFromCenter(this_brace),
            self.get_teacher().change_mode, "raise_right_hand",
            self.get_teacher().look_at, this_video
        )
        self.play(Write(this_tex))
        self.wait(2)
        self.play(self.get_teacher().change_mode, "sassy")
        self.wait(2)

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
                    lag_ratio = 0.5,
                ),
                self.pi_creature.look_at, next_expression[-1]
            )
            if brace not in self.get_mobjects():
                self.play(
                    GrowFromCenter(brace),
                    Write(question)
                )
            self.wait(0.5)
        self.wait(2)

    def create_pi_creature(self):
        self.pi_creature = Mortimer().flip()
        self.pi_creature.to_corner(DOWN+LEFT)
        return self.pi_creature

    def get_limit_expression(self):
        lim = TexMobject("\\lim_", "{dx", " \\to 0}")
        lim.set_color_by_tex("dx", self.dx_color)
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
            group.arrange(RIGHT)
            result.add(group)
        return result

    def get_expression(self, dx):
        result = TexMobject(
            "{(2 + ", str(dx), ")^3 - 2^3 \\over", str(dx)
        )
        result.set_color_by_tex(dx, self.dx_color)
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
        self.wait(2)
        for goal in goals[1:]:
            self.play(Transform(curr_goal, goal))
            self.wait(2)

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
            for nudge in (0, self.start_dx)
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
        derivative.set_color_by_tex("df", self.df_color)
        derivative.set_color_by_tex("dx", self.dx_color)
        derivative.set_color_by_tex(str(self.start_x), RED)
        df = derivative.get_part_by_tex("df")
        dx = derivative.get_part_by_tex("dx")
        input_x = derivative.get_part_by_tex(str(self.start_x))
        derivative.move_to(self.coords_to_point(7, 4))
        derivative.save_state()
        deriv_brace = Brace(derivative)
        dx_to_0 = TexMobject("dx", "\\to 0")
        dx_to_0.set_color_by_tex("dx", self.dx_color)
        dx_to_0.next_to(deriv_brace, DOWN)

        #Introduce graph
        self.play(ShowCreation(graph))
        self.play(Write(graph_label, run_time = 1))
        self.play(Write(derivative))
        self.wait()
        input_copy = input_x.copy()
        self.play(
            input_copy.next_to, 
            self.coords_to_point(self.start_x, 0),
            DOWN
        )
        self.play(ShowCreation(start_x_v_line))
        self.wait()

        #ss_group_development
        self.play(
            ShowCreation(ss_group.dx_line),
            ShowCreation(ss_group.dx_label),
        )
        self.wait()
        self.play(ShowCreation(ss_group.df_line))
        self.play(Write(ss_group.df_label))
        self.wait(2)
        self.play(
            ReplacementTransform(ss_group.dx_label.copy(), dx),
            ReplacementTransform(ss_group.df_label.copy(), df),
            run_time = 2
        )
        self.play(ShowCreation(ss_group.secant_line))
        self.wait()

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
        self.wait()

        #Write out fuller limit
        new_deriv = TexMobject(
            "{f", "(", str(self.start_x), "+", "dx", ")", 
            "-", "f", "(", str(self.start_x), ")",
            "\\over \\,", "dx"
        )
        new_deriv.set_color_by_tex("dx", self.dx_color)
        new_deriv.set_color_by_tex("f", self.df_color)
        new_deriv.set_color_by_tex(str(self.start_x), RED)
        deriv_to_new_deriv = dict([
            (
                VGroup(derivative.get_part_by_tex(s)), 
                VGroup(*new_deriv.get_parts_by_tex(s))
            )
            for s in ["f", "over", "dx", "(", str(self.start_x), ")"]
        ])
        covered_new_deriv_parts = list(it.chain(*list(deriv_to_new_deriv.values())))
        uncovered_new_deriv_parts = [part for part in new_deriv if part not in covered_new_deriv_parts]
        new_deriv.move_to(derivative)
        new_brace = Brace(new_deriv, DOWN)

        self.animate_secant_slope_group_change(
            ss_group,
            target_dx = self.start_dx,
            run_time = 2
        )
        self.play(ShowCreation(nudged_x_v_line))
        self.wait()
        self.play(*[
            ReplacementTransform(*pair, run_time = 2)
            for pair in list(deriv_to_new_deriv.items())
        ]+[
            Transform(deriv_brace, new_brace),
            dx_to_0.next_to, new_brace, DOWN
        ])
        self.play(Write(VGroup(*uncovered_new_deriv_parts), run_time = 2))
        self.wait()

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
                lim.set_color, color,
                lag_ratio = 0.5
            )
        self.wait(2)
        self.animate_secant_slope_group_change(
            ss_group, target_dx = 0.01,
            run_time = 5,
            added_anims = [
                Transform(nudged_x_v_line, start_x_v_line, run_time = 5)
            ]
        )
        self.wait(2)

        #Record attributes for DiscussLowercaseDs below
        digest_locals(self)

class RantOpenAndClose(Scene):
    def construct(self):
        opening, closing = [
            TextMobject(
                start, "Rant on infinitesimals", "$>$",
                arg_separator = ""
            )
            for start in ("$<$", "$<$/")
        ]
        self.play(FadeIn(opening))
        self.wait(2)
        self.play(Transform(opening, closing))
        self.wait(2)

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
        self.wait()
        for tex in "\\Delta x", "h":
            dx_list_replacement = [
                TexMobject(
                    tex
                ).set_color(self.dx_color).move_to(dx, DOWN)
                for dx in dx_list
            ]
            self.play(
                Transform(
                    VGroup(*dx_list),
                    VGroup(*dx_list_replacement),
                ),
                self.pi_creature.change_mode, "raise_right_hand"
            )
            self.wait()
        self.play(
            mover.scale, 0.9,
            mover.move_to, mover.initial_right, RIGHT,
            self.pi_creature.change_mode, "happy",
        )
        self.play(
            self.dx_to_0.next_to, self.lim, DOWN, SMALL_BUFF,
        )
        self.wait()

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
            for tex in ("df", "dx")
        ])
        d_words = TextMobject("""
            Limit idea is
            built in
        """)
        d_words.next_to(d_circles, DOWN)
        d_words.set_color(d_circles[0].get_color())

        lhs_rect, rhs_rect = rects = [
            Rectangle(color = GREEN_B).replace(
                mob, stretch = True
            )
            for mob in (lhs, rhs.target)
        ]
        for rect in rects:
            rect.stretch_to_fit_width(rect.get_width()+2*MED_SMALL_BUFF)
            rect.stretch_to_fit_height(rect.get_height()+2*MED_SMALL_BUFF)
        formal_definition_words = TextMobject("""
            Formal derivative definition 
        """)
        formal_definition_words.set_width(rhs_rect.get_width())
        formal_definition_words.next_to(rhs_rect, UP)
        formal_definition_words.set_color(rhs_rect.get_color())
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
        self.wait(2)
        self.play(
            ShowCreation(lhs_rect),
            FadeOut(d_circles),
            FadeOut(d_words),
        )
        self.wait(2)
        self.play(
            ReplacementTransform(lhs_rect, rhs_rect),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.wait(2)
        self.play(ReplacementTransform(
            df.copy(), df_target, 
            path_arc = -np.pi/2,
            run_time = 2
        ))
        self.wait(2)
        self.play(Indicate(
            VGroup(*rhs[:2]),
            run_time = 2
        ))
        self.wait()

        self.play(Write(formal_definition_words))
        self.play(
            self.pi_creature.change_mode, "happy",
            self.pi_creature.look_at, formal_definition_words
        )
        self.wait(2)

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
        self.wait()


        words = TextMobject("No ``infinitely small''")
        words.next_to(
            self.definition_group, DOWN,
            buff = LARGE_BUFF, 
        ) 
        arrow = Arrow(words.get_top(), self.rhs_rect.get_bottom())
        arrow.set_color(WHITE)

        h_group = VGroup(
            self.rhs[1].get_part_by_tex("dx"),
            *self.rhs[2].get_parts_by_tex("dx")
        )
        moving_h = h_group[0]
        moving_h.original_center = moving_h.get_center()
        dx_group = VGroup()
        for h in h_group:
            dx = TexMobject("dx")
            dx.set_color(h.get_color())
            dx.replace(h, dim_to_match = 1)
            dx_group.add(dx)
        moving_dx = dx_group[0]       

        self.play(Write(words), ShowCreation(arrow))
        self.wait(2)

        self.play(
            moving_h.next_to, self.pi_creature.get_corner(UP+RIGHT), UP,
            self.pi_creature.change_mode, "raise_left_hand",
        )
        self.wait()
        moving_dx.move_to(moving_h)
        h_group.save_state()
        self.play(Transform(
            h_group, dx_group, 
            path_arc = np.pi,
        ))
        self.wait(2)
        self.play(h_group.restore, path_arc = np.pi)
        self.play(
            moving_h.move_to, moving_h.original_center,
            self.pi_creature.change_mode, "plain"
        )
        self.wait()

        #Zoom in
        self.activate_zooming()
        lil_rect = self.little_rectangle
        lil_rect.move_to(self.ss_group)
        lil_rect.scale_in_place(3)
        lil_rect.save_state()
        self.wait()
        self.add(self.rhs)
        self.play(
            lil_rect.set_width,
            self.ss_group.dx_line.get_width()*4,
            run_time = 4
        )
        self.wait()
        dx = self.ss_group.dx_label
        dx.save_state()
        h = TexMobject("h")
        h.set_color(dx.get_color())
        h.replace(dx, dim_to_match = 1)
        self.play(Transform(dx, h, path_arc = np.pi))
        self.play(Indicate(dx))
        self.wait()
        self.play(dx.restore, path_arc = np.pi)
        self.play(lil_rect.restore, run_time = 4)
        self.wait()
        self.disactivate_zooming()
        self.wait()

        #Last approaching reference
        for target_dx in 3, 0.01, -2, 0.01:
            self.animate_secant_slope_group_change(
                self.ss_group, target_dx = target_dx,
                run_time = 4,
            )
            self.wait()

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
        for tex, color in list(tex_to_color.items()):
            definition.set_color_by_tex(tex, color)
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
                )).set_color(GREEN)
                for tex in ("$h$", "$dx$")
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
            lag_ratio = 0.5,
        ))
        self.wait()

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
        self.wait()

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
        self.wait()

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
        self.wait(3)

class GoalsListed(Scene):
    def construct(self):
        goals = VGroup(*[
            TextMobject("Goal %d: %s"%(d, s))
            for d, s in zip(it.count(1), [
                "Formal definition of a derivative",
                "$(\\epsilon, \\delta)$ definition of limits",
                "L'Hôpital's rule",
            ])
        ])
        goals.arrange(
            DOWN, buff = LARGE_BUFF, aligned_edge = LEFT
        )

        for goal in goals:
            self.play(FadeIn(goal))
            self.wait()
        for i, goal in enumerate(goals):
            anims = [goal.set_color, YELLOW]
            if i > 0:
                anims += [goals[i-1].set_color, WHITE]
            self.play(*anims)
            self.wait()

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
        "x_labeled_nums" : list(range(-8, 6, 2)),
        "y_min" : 0,
        "y_max" : 20,
        "y_tick_frequency" : 1,
        "y_labeled_nums" : list(range(5, 25, 5)),
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
            for tex, color in list(tex_to_color.items()):
                tex_mob.set_color_by_tex(tex, color)
            tex_mob.next_to(ORIGIN, RIGHT, LARGE_BUFF)
            tex_mob.to_edge(UP)

        expression.save_state()
        expression.generate_target()
        expression.target.next_to(limit, RIGHT)
        brace = Brace(VGroup(limit, expression.target))
        derivative.next_to(brace, DOWN)



        indices = [0, 6, 11, 13]
        funcs = [
            lambda h : (2+h)**3,
            lambda h : (2+h)**3 - 2**3,
            self.func
        ]
        graph = None
        for i, j, func in zip(indices, indices[1:], funcs):
            anims = [FadeIn(
                VGroup(*expression[i:j]),
                lag_ratio = 0.5,
            )]
            new_graph = self.get_graph(func, color = BLUE)
            if graph is None:
                graph = new_graph
                anims.append(FadeIn(graph))
            else:
                anims.append(Transform(graph, new_graph))
            self.play(*anims)
            self.wait()
        self.wait()
        self.play(
            MoveToTarget(expression),
            FadeIn(limit, lag_ratio = 0.5),
            GrowFromCenter(brace)
        )
        self.play(Write(derivative))
        self.wait(2)
        self.play(
            expression.restore,
            *list(map(FadeOut, [derivative, brace, limit]))
        )
        self.wait()

        colored_graph = graph.copy().set_color(YELLOW)
        self.play(ShowCreation(colored_graph))
        self.wait()
        self.play(ShowCreation(graph))
        self.remove(colored_graph)
        self.wait()

        self.expression = expression
        self.limit = limit
        self.graph = graph

    def emphasize_non_definedness_at_0(self):
        expression = self.expression
        
        dot = Dot(self.graph_origin, color = GREEN)
        h_equals_0 = TexMobject("h", "=", "0", "?")
        h_equals_0.next_to(self.graph_origin, UP+RIGHT, LARGE_BUFF)
        for tex in "h", "0":
            h_equals_0.set_color_by_tex(tex, GREEN)

        arrow = Arrow(h_equals_0.get_left(), self.graph_origin)
        arrow.set_color(WHITE)

        new_expression = expression.deepcopy()
        h_group = VGroup(*new_expression.get_parts_by_tex("h"))
        for h in h_group:
            zero = TexMobject("0")
            zero.set_color(h.get_color())
            zero.replace(h, dim_to_match = 1)
            Transform(h, zero).update(1)
        rhs = TexMobject("=", "{\\, 0\\,", "\\over \\,", "0\\,}")
        rhs.set_color_by_tex("0", GREEN)
        rhs.next_to(new_expression, RIGHT)
        equation = VGroup(new_expression, rhs)
        equation.next_to(expression, DOWN, buff = LARGE_BUFF)

        ud_brace = Brace(VGroup(*rhs[1:]), DOWN)
        undefined = TextMobject("Undefined")
        undefined.next_to(ud_brace, DOWN)
        undefined.to_edge(RIGHT)

        self.play(Write(h_equals_0, run_time = 2))
        self.play(*list(map(ShowCreation, [arrow, dot])))
        self.wait()
        self.play(ReplacementTransform(
            expression.copy(), new_expression
        ))
        self.wait()
        self.play(Write(rhs))
        self.wait()
        self.play(
            GrowFromCenter(ud_brace),
            Write(undefined)
        )
        self.wait(2)

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
        self.wait()
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
        self.wait()

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
        self.wait()
        self.play(
            ReplacementTransform(
                ed_group.input_range.copy(), 
                ed_group.output_range, 
                run_time = 2
            ),
        )
        self.remove(self.limit_point_hole)

        #Show approaching
        self.play(*list(map(FadeOut, [brace, brace_text])))
        for v_line, h_line in (right_v_line, top_h_line), (left_v_line, bottom_h_line):
            self.play(
                ShowCreation(v_line),
                ShowCreation(h_line)
            )
            self.wait()
            self.play(
                v_line.move_to, self.coords_to_point(0, 0), DOWN,
                h_line.move_to, self.coords_to_point(0, self.func(0)),
                run_time = 3
            )
            self.play(
                VGroup(h_line, v_line).set_stroke, GREY, 2,
            )
        self.wait()

        #Write limit
        limit = self.limit
        limit.next_to(self.expression, LEFT)
        equals, twelve = rhs = TexMobject("=", "12")
        rhs.next_to(self.expression, RIGHT)
        twelve_copy = twelve.copy()
        limit_group = VGroup(limit, rhs)

        self.play(Write(limit_group))
        self.wait()
        self.play(twelve_copy.next_to, top_h_line, RIGHT)
        self.wait()

        self.twelve_copy = twelve_copy
        self.rhs = rhs
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
        self.wait()
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
        self.wait()
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
        self.wait()
        self.play(*list(map(GrowFromCenter, self.ed_group.epsilon_lines)))
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
        self.wait()

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
        self.wait()

        self.holes = holes

    #########

    def get_epsilon_delta_group(
        self, 
        delta,
        limit_x = 0,
        dashed_line_stroke_width = 3,
        dashed_line_length = FRAME_HEIGHT,
        input_range_color = YELLOW,
        input_range_stroke_width = 6,
        ):
        kwargs = dict(locals())
        result = VGroup()
        kwargs.pop("self")
        result.delta = kwargs.pop("delta")
        result.limit_x = kwargs.pop("limit_x")
        result.kwargs = kwargs
        dashed_line = DashedLine(
            ORIGIN, dashed_line_length*RIGHT,
            stroke_width = dashed_line_stroke_width
        )
        x_values = [limit_x-delta, limit_x+delta]
        x_axis_points = [self.coords_to_point(x, 0) for x in x_values]
        result.delta_lines = VGroup(*[
            dashed_line.copy().rotate(np.pi/2).move_to(
                point, DOWN
            )
            for point in x_axis_points
        ])
        if self.func(limit_x) < 0:
            result.delta_lines.rotate(
                np.pi, RIGHT, 
                about_point = result.delta_lines.get_bottom()
            )
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
                    (limit_x-delta, limit_x-basically_zero),
                    (limit_x+basically_zero, limit_x+delta),
                ]
            ]).set_stroke(width = input_range_stroke_width)
            for func in ((lambda h : 0), self.func)
        ]
        result.epsilon_lines = VGroup(*[
            dashed_line.copy().move_to(
                self.coords_to_point(limit_x, 0)[0]*RIGHT+\
                result.output_range.get_edge_center(vect)[1]*UP
            )
            for vect in (DOWN, UP)
        ])

        result.digest_mobject_attrs()
        return result

    def animate_epsilon_delta_group_change(
        self, epsilon_delta_group, target_delta,
        **kwargs
        ):
        added_anims = kwargs.get("added_anims", [])
        limit_x = epsilon_delta_group.limit_x
        start_delta = epsilon_delta_group.delta
        ed_group_kwargs = epsilon_delta_group.kwargs
        def update_ed_group(ed_group, alpha):
            delta = interpolate(start_delta, target_delta, alpha)
            new_group = self.get_epsilon_delta_group(
                delta, limit_x = limit_x,
                **ed_group_kwargs
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
        "x_labeled_nums" : list(range(-8, 10, 2)),
        "x_axis_width" : FRAME_WIDTH - LARGE_BUFF,
        "y_min" : -4,
        "y_max" : 4,
        "y_labeled_nums" : list(range(-2, 4, 1)),
        "y_axis_height" : FRAME_HEIGHT+2*LARGE_BUFF,
        "graph_origin" : DOWN,
        "graph_color" : BLUE,
        "hole_radius" : 0.075,
        "smaller_hole_radius" : 0.04,
        "big_delta" : 1.5,
        "small_delta" : 0.05,
    }
    def construct(self):
        self.add_func()
        self.setup_axes()
        self.draw_graph()
        self.approach_zero()
        self.write_limit_not_defined()
        self.show_epsilon_delta_intuition()

    def add_func(self):
        def func(h):
            square = 0.25*h**2
            if h < 0:
                return -square + 1
            else:
                return square + 2
        self.func = func

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
        self.wait()
        self.play(ReplacementTransform(
            left_hole.copy().set_stroke(YELLOW), right_hole
        ))
        self.wait()

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
            self.play(*list(map(ShowCreation, lines)))
            self.play(UpdateFromAlphaFunc(
                lines, update_lines,
                run_time = 3
            ))
            self.play(lines.set_stroke, GREY, 3)
            self.wait()

        self.ed_group = ed_group

    def write_limit_not_defined(self):
        limit = TexMobject(
            "\\lim", "_{h", "\\to 0}", "f(", "h", ")"
        )
        limit.set_color_by_tex("h", GREEN)
        limit.move_to(self.coords_to_point(2, 1.5))

        words = TextMobject("is not defined")
        words.set_color(RED)
        words.next_to(limit, RIGHT, align_using_submobjects = True)

        limit_group = VGroup(limit, words)

        self.play(Write(limit))
        self.wait()
        self.play(Write(words))
        self.wait()
        self.play(limit_group.to_corner, UP+LEFT)
        self.wait()

    def show_epsilon_delta_intuition(self):
        ed_group = self.ed_group
        self.play(
            ed_group.delta_lines.restore,
            ed_group.epsilon_lines.restore,
        )
        self.play(ShowCreation(ed_group.input_range))
        self.wait()
        self.play(ReplacementTransform(
            ed_group.input_range.copy(),
            ed_group.output_range,
            run_time = 2
        ))
        self.graph.remove(*self.graph_holes)
        self.remove(*self.graph_holes)
        self.wait()
        self.animate_epsilon_delta_group_change(
            ed_group, target_delta = self.small_delta,
            run_time = 6
        )
        self.hole_radius = self.smaller_hole_radius

        brace = Brace(self.ed_group.epsilon_lines, RIGHT, buff = SMALL_BUFF)
        brace_text = brace.get_text("Can't get \\\\ smaller", buff = SMALL_BUFF)
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
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
            self.wait()

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
        self.wait()
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
        self.wait()
        self.teacher_says("", bubble_kwargs = {"stroke_width" : 0})
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = UP+LEFT,
            added_anims = [self.get_teacher().look_at, UP+LEFT]
        )
        self.wait(3)
        words = TextMobject(
            "It's a glimpse of\\\\",
            "real analysis"
        )
        words.set_color_by_tex("real", YELLOW)
        self.teacher_says(
            words, 
            bubble_kwargs = {"height" : 3, "width" : 6}
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(6)

class EpsilonDeltaExample(GraphLimitExpression, ZoomedScene):
    CONFIG = {
        "epsilon_list" : [2, 1, 0.5],
        "zoomed_canvas_corner" : DOWN+RIGHT,
    }
    def construct(self):
        self.delta_list = [
            epsilon/6.0 for epsilon in self.epsilon_list
        ]
        self.skip_superclass_anims()
        self.introduce_epsilon()
        self.match_epsilon()
        self.zoom_in()
        self.introduce_delta()
        self.smaller_epsilon()

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

    def introduce_epsilon(self):
        epsilon_group, small_epsilon_group = list(map(
            self.get_epsilon_group,
            self.epsilon_list[:2]
        ))

        twelve_line = epsilon_group.limit_line
        twelve = self.rhs[-1]
        twelve_copy = twelve.copy()
        twelve_copy.next_to(twelve_line)

        distance = TextMobject("Distance")
        distance.next_to(epsilon_group.labels, DOWN, LARGE_BUFF)
        distance.to_edge(RIGHT)
        arrows = VGroup(*[
            Arrow(distance.get_top(), label.get_right())
            for label in epsilon_group.labels
        ])

        self.play(ShowCreation(twelve_line))
        self.play(Write(twelve_copy))
        self.play(ReplacementTransform(twelve_copy, twelve))
        self.wait()

        self.play(*it.chain(
            [
                ReplacementTransform(twelve_line.copy(), line)
                for line in epsilon_group.epsilon_lines
            ], 
            list(map(GrowFromCenter, epsilon_group.braces)),
        ))
        self.play(*list(map(Write, epsilon_group.labels)))
        self.play(
            Write(distance),
            ShowCreation(arrows)
        )
        self.wait()
        self.play(*list(map(FadeOut, [distance, arrows])))
        self.play(Transform(
            epsilon_group, small_epsilon_group,
            run_time = 2
        ))
        self.wait()

        self.epsilon_group = epsilon_group

    def match_epsilon(self):
        self.animate_epsilon_delta_group_change(
            self.ed_group, target_delta = self.delta_list[1],
            run_time = 2,
            added_anims = [
                ApplyMethod(
                    hole.scale_in_place, 0.25,
                    run_time = 2
                )
                for hole in self.holes
            ]
        )
        self.ed_group.delta = self.delta_list[1]
        self.ed_group.input_range.make_jagged()
        self.wait()

    def zoom_in(self):
        self.ed_group.input_range.make_jagged()

        self.activate_zooming()
        lil_rect = self.little_rectangle
        lil_rect.move_to(self.graph_origin)
        lil_rect.scale_in_place(self.zoom_factor)
        self.add(self.holes)
        self.wait()
        self.play(lil_rect.scale_in_place, 1./self.zoom_factor)
        self.wait()

    def introduce_delta(self):
        delta_group = self.get_delta_group(self.delta_list[1])
        self.play(*list(map(GrowFromCenter, delta_group.braces)))
        self.play(*list(map(Write, delta_group.labels)))
        self.wait()
        self.play(
            ReplacementTransform(
                self.ed_group.input_range.copy(),
                self.ed_group.output_range,
                run_time = 2
            ),
            Animation(self.holes),
        )
        self.play(ApplyWave(
            VGroup(self.ed_group.output_range, self.holes[1]),
            direction = RIGHT
        ))
        self.wait(2)

        self.delta_group = delta_group

    def smaller_epsilon(self):
        new_epsilon = self.epsilon_list[-1]
        new_delta = self.delta_list[-1]
        self.play(Transform(
            self.epsilon_group,
            self.get_epsilon_group(new_epsilon)
        ))
        self.wait()
        self.animate_epsilon_delta_group_change(
            self.ed_group, target_delta = new_delta,
            added_anims = [
                Transform(
                    self.delta_group,
                    self.get_delta_group(new_delta)
                )
            ] + [
                ApplyMethod(hole.scale_in_place, 0.5)
                for hole in self.holes
            ]
        )
        self.ed_group.input_range.make_jagged()
        self.wait(2)

    ##

    def get_epsilon_group(self, epsilon, limit_value = 12):
        result = VGroup()
        line_length = FRAME_HEIGHT
        lines = [
            Line(
                ORIGIN, line_length*RIGHT,
            ).move_to(self.coords_to_point(0, limit_value+nudge))
            for nudge in (0, -epsilon, epsilon)
        ]
        result.limit_line = lines[0]
        result.limit_line.set_stroke(RED, width = 3)
        result.epsilon_lines = VGroup(*lines[1:])
        result.epsilon_lines.set_stroke(MAROON_B, width = 2)
        brace = Brace(Line(ORIGIN, 0.5*UP), RIGHT)
        result.braces = VGroup(*[
            brace.copy().set_height(
                group.get_height()
            ).next_to(group, RIGHT, SMALL_BUFF)
            for i in (1, 2)
            for group in [VGroup(lines[0], lines[i])]
        ])
        result.labels = VGroup(*[
            brace.get_text("\\Big $\\epsilon$", buff = SMALL_BUFF)
            for brace in result.braces
        ])
        for label, brace in zip(result.labels, result.braces):
            label.set_height(min(
                label.get_height(),
                0.8*brace.get_height()
            ))

        result.digest_mobject_attrs()
        return result

    def get_delta_group(self, delta):
        result = VGroup()
        brace = Brace(Line(ORIGIN, RIGHT), DOWN)
        brace.set_width(
            (self.coords_to_point(delta, 0)-self.graph_origin)[0]
        )
        result.braces = VGroup(*[
            brace.copy().move_to(self.coords_to_point(x, 0))
            for x in (-delta/2, delta/2)
        ])
        result.braces.shift(self.holes[0].get_height()*DOWN)
        result.labels = VGroup(*[
            TexMobject("\\delta").scale(
                1./self.zoom_factor
            )
            for brace in result.braces
        ])
        for label, brace in zip(result.labels, result.braces):
            label.next_to(
                brace, DOWN, 
                buff = SMALL_BUFF/self.zoom_factor
            )

        result.digest_mobject_attrs()
        return result

class EpsilonDeltaCounterExample(LimitCounterExample, EpsilonDeltaExample):
    def construct(self):
        self.hole_radius = 0.04
        self.add_func()
        self.setup_axes()
        self.draw_graph()
        self.introduce_epsilon()
        self.introduce_epsilon_delta_group()
        self.move_epsilon_group_up_and_down()

    def introduce_epsilon(self):
        epsilon_group = self.get_epsilon_group(0.4, 1.5)
        rhs = TexMobject("=0.4")
        label = epsilon_group.labels[1]
        rhs.next_to(label, RIGHT)
        epsilon_group.add(rhs)

        self.play(ShowCreation(epsilon_group.limit_line))
        self.play(*it.chain(
            [
                ReplacementTransform(
                    epsilon_group.limit_line.copy(),
                    line
                )
                for line in epsilon_group.epsilon_lines
            ],
            list(map(GrowFromCenter, epsilon_group.braces))
        ))
        self.play(*list(map(Write, epsilon_group.labels)))
        self.play(Write(rhs))
        self.wait()

        self.epsilon_group = epsilon_group

    def introduce_epsilon_delta_group(self):
        ed_group = self.get_epsilon_delta_group(self.big_delta)

        self.play(*list(map(ShowCreation, ed_group.delta_lines)))
        self.play(ShowCreation(ed_group.input_range))
        self.play(ReplacementTransform(
            ed_group.input_range.copy(),
            ed_group.output_range,
            run_time = 2
        ))
        self.remove(self.graph_holes)
        self.play(*list(map(GrowFromCenter, ed_group.epsilon_lines)))
        self.wait(2)
        self.animate_epsilon_delta_group_change(
            ed_group, target_delta = self.small_delta,
            run_time = 3
        )
        ed_group.delta = self.small_delta
        self.wait()

        self.ed_group = ed_group

    def move_epsilon_group_up_and_down(self):
        vects = [
            self.coords_to_point(0, 2) - self.coords_to_point(0, 1.5),
            self.coords_to_point(0, 1) - self.coords_to_point(0, 2),
            self.coords_to_point(0, 1.5) - self.coords_to_point(0, 1),
        ]
        for vect in vects:
            self.play(self.epsilon_group.shift, vect)
            self.wait()
            self.shake_ed_group()
            self.wait()

    ##

    def shake_ed_group(self):
        self.animate_epsilon_delta_group_change(
            self.ed_group, target_delta = self.big_delta,
            rate_func = lambda t : 0.2*there_and_back(2*t%1)
        )

class TheoryHeavy(TeacherStudentsScene):
    def construct(self):
        lhs = TexMobject(
            "{df", "\\over \\,", "dx}", "(", "x", ")"
        )
        equals = TexMobject("=")
        rhs = TexMobject(
            "\\lim", "_{h", "\\to 0}", 
            "{f", "(", "x", "+", "h", ")", "-", "f", "(", "x", ")",
            "\\over \\,", "h}"
        )
        derivative = VGroup(lhs, equals, rhs)
        derivative.arrange(RIGHT)
        for tex_mob in derivative:
            tex_mob.set_color_by_tex("x", RED)
            tex_mob.set_color_by_tex("h", GREEN)
            tex_mob.set_color_by_tex("dx", GREEN)
            tex_mob.set_color_by_tex("f", YELLOW)
        derivative.next_to(self.get_pi_creatures(), UP, buff = MED_LARGE_BUFF)

        lim = rhs.get_part_by_tex("lim")
        epsilon_delta = TexMobject("(\\epsilon, \\delta)")
        epsilon_delta.next_to(lim, UP, buff = 1.5*LARGE_BUFF)
        arrow = Arrow(epsilon_delta, lim, color = WHITE)


        self.student_says(
            "Too much theory!",
            target_mode = "angry",
            content_introduction_kwargs = {"run_time" : 2},
        )
        self.wait()
        student = self.get_students()[1]
        Scene.play(self,
            Write(lhs),
            FadeOut(student.bubble),
            FadeOut(student.bubble.content),
            *[
                ApplyFunction(
                    lambda pi : pi.change_mode("pondering").look_at(epsilon_delta),
                    pi
                )
                for pi in self.get_pi_creatures()
            ]
        )
        student.bubble = None
        part_tex_pairs = [
            ("df", "f"),
            ("over", "+"),
            ("over", "-"),
            ("over", "to"),
            ("over", "over"),
            ("dx", "h"),
            ("(", "("),
            ("x", "x"),
            (")", ")"),
        ]
        self.play(Write(equals), Write(lim), *[
            ReplacementTransform(
                VGroup(*lhs.get_parts_by_tex(t1)).copy(),
                VGroup(*rhs.get_parts_by_tex(t2)),
                run_time = 2,
                rate_func = squish_rate_func(smooth, alpha, alpha+0.5)
            )
            for (t1, t2), alpha in zip(
                part_tex_pairs,
                np.linspace(0, 0.5, len(part_tex_pairs))
            )
        ])
        self.wait(2)
        self.play(
            Write(epsilon_delta),
            ShowCreation(arrow)
        )
        self.wait(3)
        derivative.add(epsilon_delta, arrow)
        self.student_says(
            "How do you \\\\ compute limits?",
            student_index = 2,
            added_anims = [
                derivative.scale, 0.8,
                derivative.to_corner, UP+LEFT
            ]
        )
        self.play(self.get_teacher().change_mode, "happy")
        self.wait(2)

class LHopitalExample(LimitCounterExample, PiCreatureScene, ZoomedScene, ReconfigurableScene):
    CONFIG = {
        "graph_origin" : ORIGIN,
        "x_axis_width" : FRAME_WIDTH,
        "x_min" : -5,
        "x_max" : 5,
        "x_labeled_nums" : list(range(-6, 8, 2)),
        "x_axis_label" : "$x$",
        "y_axis_height" : FRAME_HEIGHT,
        "y_min" : -3.1,
        "y_max" : 3.1,
        "y_bottom_tick" : -4,
        "y_labeled_nums" : list(range(-2, 4, 2)),
        "y_axis_label" : "",
        "x_color" : RED,
        "hole_radius" : 0.07,
        "big_delta" : 0.5,
        "small_delta" : 0.01,
        "dx" : 0.06,
        "dx_color" : WHITE,
        "tex_scale_value" : 0.9,
        "sin_color" : GREEN,
        "parabola_color" : YELLOW,
        "zoomed_canvas_corner" : DOWN+LEFT,
        "zoom_factor" : 10,
        "zoomed_canvas_frame_shape" : (5, 5),
        "zoomed_canvas_corner_buff" : MED_SMALL_BUFF,
        "zoomed_rect_center_coords" : (1 + 0.1, -0.03),
    }
    def construct(self):
        self.setup_axes()
        self.introduce_function()
        self.show_non_definedness_at_one()
        self.plug_in_value_close_to_one()
        self.ask_about_systematic_process()
        self.show_graph_of_numerator_and_denominator()
        self.zoom_in_to_trouble_point()
        self.talk_through_sizes_of_nudges()
        self.show_final_ratio()
        self.show_final_height()

    def setup(self):
        PiCreatureScene.setup(self)
        ZoomedScene.setup(self)
        ReconfigurableScene.setup(self)
        self.remove(*self.get_pi_creatures()) 

    def setup_axes(self):
        GraphScene.setup_axes(self)
        self.x_axis_label_mob.set_color(self.x_color)

    def introduce_function(self):
        graph = self.get_graph(self.func)
        colored_graph = graph.copy().set_color(YELLOW)
        func_label = self.get_func_label()
        func_label.next_to(ORIGIN, RIGHT, buff = LARGE_BUFF)
        func_label.to_edge(UP)

        x_copy = self.x_axis_label_mob.copy()

        self.play(
            Write(func_label),
            Transform(
                x_copy, VGroup(*func_label.get_parts_by_tex("x")),
                remover = True
            )
        )
        self.play(ShowCreation(
            graph,
            run_time = 3,
            rate_func=linear
        ))
        self.wait(4) ## Overly oscillation
        self.play(ShowCreation(colored_graph, run_time = 2))
        self.wait()
        self.play(ShowCreation(graph, run_time = 2))
        self.remove(colored_graph)
        self.wait()

        self.graph = graph
        self.func_label = func_label

    def show_non_definedness_at_one(self):
        morty = self.get_primary_pi_creature()
        words = TexMobject("\\text{Try }", "x", "=1")
        words.set_color_by_tex("x", self.x_color, substring = False)

        v_line, alt_v_line = [
            self.get_vertical_line_to_graph(
                x, self.graph, 
                line_class = DashedLine,
                color = self.x_color
            )
            for x in (1, -1)
        ]
        hole, alt_hole = [
            self.get_hole(x, self.func(x))
            for x in (1, -1)
        ]
        ed_group = self.get_epsilon_delta_group(
            self.big_delta, limit_x = 1,
        )

        func_1 = self.get_func_label("1")
        func_1.next_to(self.func_label, DOWN, buff = MED_LARGE_BUFF)
        rhs = TexMobject("\\Rightarrow \\frac{0}{0}")
        rhs.next_to(func_1, RIGHT)
        func_1_group = VGroup(func_1, *rhs)
        func_1_group.add_to_back(BackgroundRectangle(func_1_group))

        lim = TexMobject("\\lim", "_{x", "\\to 1}")
        lim.set_color_by_tex("x", self.x_color)
        lim.move_to(self.func_label, LEFT)
        self.func_label.generate_target()
        self.func_label.target.next_to(lim, RIGHT)
        equals_q = TexMobject("=", "???")
        equals_q.next_to(self.func_label.target, RIGHT)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(morty, words))
        self.play(
            Blink(morty),
            ShowCreation(v_line)
        )
        self.play(
            RemovePiCreatureBubble(
                morty, target_mode = "pondering",
                look_at_arg = func_1
            ),
            ReplacementTransform(
                self.func_label.copy(),
                func_1
            )
        )
        self.wait(2)
        self.play(Write(VGroup(*rhs[:-1])))
        self.wait()
        self.play(Write(rhs[-1]))
        self.wait()
        self.play(GrowFromCenter(hole))
        self.wait()

        self.play(ShowCreation(alt_v_line))
        self.play(GrowFromCenter(alt_hole))
        self.wait()
        alt_group = VGroup(alt_v_line, alt_hole)
        self.play(alt_group.set_stroke, GREY, 2)
        self.play(FocusOn(hole))
        self.wait()

        self.play(GrowFromCenter(ed_group.input_range))
        self.play(
            ReplacementTransform(
                ed_group.input_range.copy(),
                ed_group.output_range
            ),
            *list(map(ShowCreation, ed_group.delta_lines))
        )
        self.play(*list(map(GrowFromCenter, ed_group.epsilon_lines)))
        self.play(morty.change_mode, "thinking")
        self.animate_epsilon_delta_group_change(
            ed_group, target_delta = self.small_delta,
            run_time = 4
        )
        self.wait()
        self.play(
            Write(lim),
            MoveToTarget(self.func_label),
            Write(equals_q),
            morty.change_mode, "confused", 
            morty.look_at, lim
        )
        self.wait(2)
        self.play(
            func_1_group.to_corner, UP+LEFT,
            *list(map(FadeOut, [morty, ed_group]))
        )
        self.wait()

        self.lim_group = VGroup(lim, self.func_label, equals_q)
        for part in self.lim_group:
            part.add_background_rectangle()
        self.func_1_group = func_1_group
        self.v_line = v_line

    def plug_in_value_close_to_one(self):
        num = 1.00001
        result = self.func(num)
        label = self.get_func_label(num)
        label.add_background_rectangle()
        rhs = TexMobject("= %.4f\\dots"%result)
        rhs.next_to(label, RIGHT)
        approx_group = VGroup(label, rhs)
        approx_group.set_width(FRAME_X_RADIUS-2*MED_LARGE_BUFF)
        approx_group.next_to(ORIGIN, UP, buff = MED_LARGE_BUFF)
        approx_group.to_edge(RIGHT)

        self.play(ReplacementTransform(
            self.func_label.copy(),
            label
        ))
        self.wait()
        self.play(Write(rhs))
        self.wait()

        self.approx_group = approx_group

    def ask_about_systematic_process(self):
        morty = self.pi_creature
        morty.change_mode("plain")

        self.func_1_group.save_state()
        to_fade = VGroup(
            *self.x_axis.numbers[:len(self.x_axis.numbers)/2]
        )

        self.play(
            FadeIn(morty),
            FadeOut(to_fade)
        )
        self.x_axis.remove(*to_fade)

        self.pi_creature_says(
            morty, "Is there a \\\\ better way?",
            bubble_kwargs = {
                "height" : 3,
                "width" : 4,
            },
        )
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(
                morty, target_mode = "raise_left_hand",
                look_at_arg = self.func_1_group
            ),
            self.func_1_group.scale, self.tex_scale_value,
            self.func_1_group.move_to, 
                morty.get_corner(UP+LEFT), DOWN+LEFT,
            self.func_1_group.shift, MED_LARGE_BUFF*UP,
        )
        self.wait(2)
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look, UP+RIGHT,
            FadeOut(self.approx_group),
            self.func_1_group.restore,
            self.lim_group.next_to, 
                morty.get_corner(UP+RIGHT), RIGHT,
        )
        self.wait(2)
        self.play(
            FadeOut(self.func_1_group),
            self.lim_group.scale, self.tex_scale_value,
            self.lim_group.to_corner, UP+LEFT,
            # self.lim_group.next_to, ORIGIN, UP, MED_LARGE_BUFF,
            # self.lim_group.to_edge, LEFT,
            morty.change_mode, "plain"
        )
        self.wait()
        self.play(FadeOut(morty))

    def show_graph_of_numerator_and_denominator(self):
        sine_graph = self.get_graph(
            lambda x : np.sin(np.pi*x), 
            color = self.sin_color
        )
        sine_label = self.get_graph_label(
            sine_graph, "\\sin(\\pi x)",
            x_val = 4.5,
            direction = UP
        )
        parabola = self.get_graph(
            lambda x : x**2 - 1,
            color = self.parabola_color
        )
        parabola_label = self.get_graph_label(
            parabola, "x^2 - 1"
        )
        fader = VGroup(*[
            Rectangle(
                width = FRAME_WIDTH,
                height = FRAME_HEIGHT,
                stroke_width = 0,
                fill_opacity = 0.75,
                fill_color = BLACK,
            ).next_to(self.coords_to_point(1, 0), vect, MED_LARGE_BUFF)
            for vect in (LEFT, RIGHT)
        ])

        self.play(
            ShowCreation(sine_graph, run_time = 2),
            Animation(self.lim_group)
        )
        self.play(FadeIn(sine_label))
        self.wait()
        self.play(ShowCreation(parabola, run_time = 2))
        self.play(FadeIn(parabola_label))
        self.wait()
        self.play(FadeIn(fader, run_time = 2))
        self.wait()
        self.play(FadeOut(fader))

        self.sine_graph = sine_graph
        self.sine_label = sine_label
        self.parabola = parabola
        self.parabola_label = parabola_label

    def zoom_in_to_trouble_point(self):
        self.activate_zooming()
        lil_rect = self.little_rectangle
        lil_rect.scale(self.zoom_factor)
        lil_rect.move_to(self.coords_to_point(
            *self.zoomed_rect_center_coords
        ))
        self.wait()
        self.play(lil_rect.scale_in_place, 1./self.zoom_factor)
        self.wait()

    def talk_through_sizes_of_nudges(self):
        arrow_tip_length = 0.15/self.zoom_factor
        zoom_tex_scale_factor = min(
            0.75/self.zoom_factor,
            1.5*self.dx
        )

        dx_arrow = Arrow(
            self.coords_to_point(1, 0),
            self.coords_to_point(1+self.dx, 0),
            tip_length = arrow_tip_length,
            color = WHITE,
        )
        dx_label = TexMobject("dx")
        dx_label.scale(zoom_tex_scale_factor)
        dx_label.next_to(dx_arrow, UP, buff = SMALL_BUFF/self.zoom_factor)

        d_sine_arrow, d_parabola_arrow = [
            Arrow(
                self.coords_to_point(1+self.dx, 0),
                self.coords_to_point(
                    1+self.dx, 
                    graph.underlying_function(1+self.dx)
                ),
                tip_length = arrow_tip_length,
                color = graph.get_color()
            )
            for graph in (self.sine_graph, self.parabola)
        ]
        tex_arrow_pairs = [
            [("d\\big(", "\\sin(", "\\pi", "x", ")", "\\big)"), d_sine_arrow],
            [("d\\big(", "x", "^2", "-1", "\\big)"), d_parabola_arrow],
            [("\\cos(", "\\pi", "x", ")", "\\pi ", "\\, dx"), d_sine_arrow],
            [("2", "x", "\\, dx"), d_parabola_arrow],
        ]
        d_labels = []
        for tex_args, arrow in tex_arrow_pairs:
            label = TexMobject(*tex_args)
            label.set_color_by_tex("x", self.x_color)
            label.set_color_by_tex("dx", self.dx_color)
            label.scale(zoom_tex_scale_factor)
            label.next_to(arrow, RIGHT, buff = SMALL_BUFF/self.zoom_factor)
            d_labels.append(label)
        d_sine_label, d_parabola_label, cos_dx, two_x_dx = d_labels

        #Show dx        
        self.play(ShowCreation(dx_arrow))
        self.play(Write(dx_label))
        self.wait()

        #Show d_sine bump
        point = VectorizedPoint(self.coords_to_point(1, 0))
        self.play(ReplacementTransform(point, d_sine_arrow))
        self.wait()
        self.play(ReplacementTransform(
            VGroup(dx_label[1].copy()),
            d_sine_label,
            run_time = 2
        ))
        self.wait(2)
        self.play(
            d_sine_label.shift, d_sine_label.get_height()*UP
        )
        tex_pair_lists = [
            [
                ("sin", "cos"),
                ("pi", "pi"),
                ("x", "x"),
                (")", ")"),
            ],
            [
                ("pi", "\\pi "), #Space there is important, though hacky
            ],
            [
                ("d\\big(", "dx"),
                ("\\big)", "dx"),
            ]
        ]
        for tex_pairs in tex_pair_lists:
            self.play(*[
                ReplacementTransform(
                    d_sine_label.get_part_by_tex(t1).copy(), 
                    cos_dx.get_part_by_tex(t2)
                )
                for t1, t2 in tex_pairs
            ])
            self.wait()
        self.play(FadeOut(d_sine_label))
        self.wait()

        #Substitute x = 1
        self.substitute_x_equals_1(cos_dx, zoom_tex_scale_factor)

        #Proportionality constant
        cos_pi = VGroup(*cos_dx[:-1])
        cos = VGroup(*cos_dx[:-2])
        brace = Brace(Line(LEFT, RIGHT), UP)
        brace.set_width(cos_pi.get_width())
        brace.move_to(cos_pi.get_top(), DOWN)
        brace_text = TextMobject(
            """
                \\begin{flushleft} 
                Proportionality
                constant 
                \\end{flushleft}
            """
        )
        brace_text.scale(0.9*zoom_tex_scale_factor)
        brace_text.add_background_rectangle()
        brace_text.next_to(brace, UP, SMALL_BUFF/self.zoom_factor, LEFT)
        neg_one = TexMobject("-", "1")
        neg_one.add_background_rectangle()
        neg_one.scale(zoom_tex_scale_factor)

        self.play(GrowFromCenter(brace))
        self.play(Write(brace_text))
        self.wait(2)
        self.play(
            brace.set_width, cos.get_width(),
            brace.next_to, cos, UP, SMALL_BUFF/self.zoom_factor,
            FadeOut(brace_text)
        )
        neg_one.next_to(brace, UP, SMALL_BUFF/self.zoom_factor)
        self.play(Write(neg_one))
        self.wait()
        self.play(FadeOut(cos))
        neg = neg_one.get_part_by_tex("-").copy()
        self.play(neg.next_to, cos_dx[-2], LEFT, SMALL_BUFF/self.zoom_factor)
        self.play(*list(map(FadeOut, [neg_one, brace])))
        neg_pi_dx = VGroup(neg, *cos_dx[-2:])
        self.play(
            neg_pi_dx.next_to, d_sine_arrow, 
            RIGHT, SMALL_BUFF/self.zoom_factor
        )
        self.wait()

        #Show d_parabola bump
        point = VectorizedPoint(self.coords_to_point(1, 0))
        self.play(ReplacementTransform(point, d_parabola_arrow))
        self.play(ReplacementTransform(
            VGroup(dx_label[1].copy()),
            d_parabola_label,
            run_time = 2
        ))
        self.wait(2)
        self.play(
            d_parabola_label.shift, d_parabola_label.get_height()*UP
        )
        tex_pair_lists = [
            [
                ("2", "2"),
                ("x", "x"),
            ],
            [
                ("d\\big(", "dx"),
                ("\\big)", "dx"),
            ]
        ]
        for tex_pairs in tex_pair_lists:
            self.play(*[
                ReplacementTransform(
                    d_parabola_label.get_part_by_tex(t1).copy(), 
                    two_x_dx.get_part_by_tex(t2)
                )
                for t1, t2 in tex_pairs
            ])
        self.wait()
        self.play(FadeOut(d_parabola_label))
        self.wait()

        #Substitute x = 1
        self.substitute_x_equals_1(two_x_dx, zoom_tex_scale_factor)

    def substitute_x_equals_1(self, tex_mob, zoom_tex_scale_factor):
        x = tex_mob.get_part_by_tex("x")
        equation = TexMobject("x", "=", "1")
        eq_x, equals, one = equation
        equation.scale(zoom_tex_scale_factor)
        equation.next_to(
            x, UP, 
            buff = MED_SMALL_BUFF/self.zoom_factor,
            aligned_edge = LEFT
        )
        equation.set_color_by_tex("x", self.x_color)
        equation.set_color_by_tex("1", self.x_color)
        dot_one = TexMobject("\\cdot", "1")
        dot_one.scale(zoom_tex_scale_factor)
        dot_one.set_color(self.x_color)
        dot_one.move_to(x, DOWN+LEFT)

        self.play(x.move_to, eq_x)
        self.wait()
        self.play(
            ReplacementTransform(x.copy(), eq_x),
            Transform(x, one),
            Write(equals)
        )
        self.wait()
        self.play(Transform(x, dot_one))
        self.wait()
        self.play(*list(map(FadeOut, [eq_x, equals])))
        self.wait()

    def show_final_ratio(self):
        lim, ratio, equals_q = self.lim_group
        self.remove(self.lim_group)
        self.add(*self.lim_group)
        numerator = VGroup(*ratio[1][:3])
        denominator = VGroup(*ratio[1][-2:])
        rhs = TexMobject(
            "\\approx", 
            "{-\\pi", "\\, dx", "\\over \\,", "2", "\\, dx}"
        )
        rhs.add_background_rectangle()
        rhs.move_to(equals_q, LEFT)
        equals = TexMobject("=")
        approx = rhs.get_part_by_tex("approx")
        equals.move_to(approx)

        dxs = VGroup(*rhs.get_parts_by_tex("dx"))
        circles = VGroup(*[
            Circle(color = GREEN).replace(dx).scale_in_place(1.3)
            for dx in dxs
        ])

        #Show numerator and denominator
        self.play(FocusOn(ratio))
        for mob in numerator, denominator:
            self.play(ApplyWave(
                mob, direction = UP+RIGHT, amplitude = 0.1
            ))
            self.wait()
        self.play(ReplacementTransform(equals_q, rhs))
        self.wait()

        #Cancel dx's
        self.play(*list(map(ShowCreation, circles)), run_time = 2)
        self.wait()
        self.play(dxs.fade, 0.75, FadeOut(circles))
        self.wait()

        #Shrink dx
        self.transition_to_alt_config(
            transformation_kwargs = {"run_time" : 2},
            dx = self.dx/10
        )
        self.wait()
        self.play(Transform(approx, equals))
        self.play(Indicate(approx))
        self.wait()

        self.final_ratio = rhs

    def show_final_height(self):
        brace = Brace(self.v_line, LEFT)
        height = brace.get_text("$\\dfrac{-\\pi}{2}$")
        height.add_background_rectangle()
        
        self.disactivate_zooming()
        self.play(*list(map(FadeOut, [
            self.sine_graph, self.sine_label,
            self.parabola, self.parabola_label,
        ])) + [
            Animation(self.final_ratio)
        ])
        self.play(GrowFromCenter(brace))
        self.play(Write(height))
        self.wait(2)

    ##

    def create_pi_creature(self):
        self.pi_creature = Mortimer().flip().to_corner(DOWN+LEFT)
        return self.pi_creature

    def func(self, x):
        if abs(x) != 1:
            return np.sin(x*np.pi) / (x**2 - 1)
        else:
            return np.pi*np.cos(x*np.pi) / (2*x)

    def get_func_label(self, argument = "x"):
        in_tex = "{%s}"%str(argument)
        result = TexMobject(
            "{\\sin(\\pi ", in_tex, ")", " \\over \\,",
            in_tex, "^2 - 1}"
        )
        result.set_color_by_tex(in_tex, self.x_color)
        return result

    def get_epsilon_delta_group(self, delta, **kwargs):
        ed_group = GraphLimitExpression.get_epsilon_delta_group(self, delta, **kwargs)
        color = ed_group.kwargs["input_range_color"]
        radius = min(delta/2, self.hole_radius)
        pairs = [
            # (ed_group.input_range[0], (1, 0)),
            (ed_group.input_range[1], (1, 0)),
            # (ed_group.output_range[0], (1, self.func(1))),
            (ed_group.output_range[1], (1, self.func(1))),
        ]
        for mob, coords in pairs:
            mob.add(self.get_hole(
                *coords, 
                color = color,
                radius = radius
            ))
        return ed_group

class DerivativeLimitReciprocity(Scene):
    def construct(self):
        arrow = Arrow(LEFT, RIGHT, color = WHITE)
        lim = TexMobject("\\lim", "_{h", "\\to 0}")
        lim.set_color_by_tex("h", GREEN)
        lim.next_to(arrow, LEFT)
        deriv = TexMobject("{df", "\\over\\,", "dx}")
        deriv.set_color_by_tex("dx", GREEN)
        deriv.set_color_by_tex("df", YELLOW)
        deriv.next_to(arrow, RIGHT)

        self.play(FadeIn(lim, lag_ratio = 0.5))
        self.play(ShowCreation(arrow))
        self.play(FadeIn(deriv, lag_ratio = 0.5))
        self.wait()
        self.play(Rotate(arrow, np.pi, run_time = 2))
        self.wait()

class GeneralLHoptial(LHopitalExample):
    CONFIG = {
        "f_color" : BLUE,
        "g_color" : YELLOW,
        "a_value" : 2.5,
        "zoomed_rect_center_coords" : (2.55, 0),
        "zoom_factor" : 15,
        "image_height" : 3,
    }
    def construct(self):
        self.setup_axes()
        self.add_graphs()
        self.zoom_in()
        self.show_limit_in_symbols()
        self.show_tiny_nudge()
        self.show_derivative_ratio()
        self.show_example()
        self.show_bernoulli_and_lHopital()

    def add_graphs(self):
        f_graph = self.get_graph(self.f, self.f_color)
        f_label = self.get_graph_label(
            f_graph, "f(x)", 
            x_val = 3, 
            direction = RIGHT
        )
        g_graph = ParametricFunction(
            lambda y : self.coords_to_point(np.exp(y)+self.a_value-1, y),
            t_min = self.y_min,
            t_max = self.y_max,
            color = self.g_color
        )
        g_graph.underlying_function = self.g
        g_label = self.get_graph_label(
            g_graph, "g(x)", x_val = 4, direction = UP
        )

        a_dot = Dot(self.coords_to_point(self.a_value, 0))
        a_label = TexMobject("x = a")
        a_label.next_to(a_dot, UP, LARGE_BUFF)
        a_arrow = Arrow(a_label.get_bottom(), a_dot, buff = SMALL_BUFF)
        VGroup(a_dot, a_label, a_arrow).set_color(self.x_color)

        self.play(ShowCreation(f_graph), Write(f_label))
        self.play(ShowCreation(g_graph), Write(g_label))
        self.wait()

        self.play(
            Write(a_label),
            ShowCreation(a_arrow),
            ShowCreation(a_dot),
        )
        self.wait()
        self.play(*list(map(FadeOut, [a_label, a_arrow])))

        self.a_dot = a_dot
        self.f_graph = f_graph
        self.f_label = f_label
        self.g_graph = g_graph
        self.g_label = g_label

    def zoom_in(self):
        self.activate_zooming()
        lil_rect = self.little_rectangle
        lil_rect.scale(self.zoom_factor)
        lil_rect.move_to(self.coords_to_point(
            *self.zoomed_rect_center_coords
        ))
        self.wait()
        self.play(
            lil_rect.scale_in_place, 1./self.zoom_factor,
            self.a_dot.scale_in_place, 1./self.zoom_factor,
            run_time = 3,
        )
        self.wait()

    def show_limit_in_symbols(self):
        frac_a = self.get_frac("a", self.x_color)
        frac_x = self.get_frac("x")
        lim = TexMobject("\\lim", "_{x", "\\to", "a}")
        lim.set_color_by_tex("a", self.x_color)
        equals_zero_over_zero = TexMobject(
            "=", "{\\, 0 \\,", "\\over \\,", "0 \\,}"
        )
        equals_q = TexMobject(*"=???")
        frac_x.next_to(lim, RIGHT, SMALL_BUFF)
        VGroup(lim, frac_x).to_corner(UP+LEFT)
        frac_a.move_to(frac_x)
        equals_zero_over_zero.next_to(frac_a, RIGHT)
        equals_q.next_to(frac_a, RIGHT)

        self.play(
            ReplacementTransform(
                VGroup(*self.f_label).copy(), 
                VGroup(frac_a.numerator)
            ),
            ReplacementTransform(
                VGroup(*self.g_label).copy(),
                VGroup(frac_a.denominator)
            ),
            Write(frac_a.over),
            run_time = 2
        )
        self.wait()
        self.play(Write(equals_zero_over_zero))
        self.wait(2)
        self.play(
            ReplacementTransform(
                VGroup(*frac_a.get_parts_by_tex("a")),
                VGroup(lim.get_part_by_tex("a"))
            )
        )
        self.play(Write(VGroup(*lim[:-1])))
        self.play(ReplacementTransform(
            VGroup(*lim.get_parts_by_tex("x")).copy(),
            VGroup(*frac_x.get_parts_by_tex("x"))
        ))
        self.play(ReplacementTransform(
            equals_zero_over_zero, equals_q
        ))
        self.wait()

        self.remove(frac_a)
        self.add(frac_x)
        self.frac_x = frac_x
        self.remove(equals_q)
        self.add(*equals_q)
        self.equals_q = equals_q

    def show_tiny_nudge(self):
        arrow_tip_length = 0.15/self.zoom_factor
        zoom_tex_scale_factor = min(
            0.75/self.zoom_factor,
            1.5*self.dx
        )
        z_small_buff = SMALL_BUFF/self.zoom_factor

        dx_arrow = Arrow(
            self.coords_to_point(self.a_value, 0),
            self.coords_to_point(self.a_value+self.dx, 0),
            tip_length = arrow_tip_length,
            color = WHITE,
        )
        dx_label = TexMobject("dx")
        dx_label.scale(zoom_tex_scale_factor)
        dx_label.next_to(dx_arrow, UP, buff = z_small_buff)
        dx_label.shift(z_small_buff*RIGHT)

        df_arrow, dg_arrow = [
            Arrow(
                self.coords_to_point(self.a_value+self.dx, 0),
                self.coords_to_point(
                    self.a_value+self.dx, 
                    graph.underlying_function(self.a_value+self.dx)
                ),
                tip_length = arrow_tip_length,
                color = graph.get_color()
            )
            for graph in (self.f_graph, self.g_graph)
        ]
        v_labels = []
        for char, arrow in ("f", df_arrow), ("g", dg_arrow):
            label = TexMobject(
                "\\frac{d%s}{dx}"%char, "(", "a", ")", "\\,dx"
            )
            label.scale(zoom_tex_scale_factor)
            label.set_color_by_tex("a", self.x_color)
            label.set_color_by_tex("frac", arrow.get_color())
            label.next_to(arrow, RIGHT, z_small_buff)
            v_labels.append(label)
        df_label, dg_label = v_labels

        self.play(ShowCreation(dx_arrow))
        self.play(Write(dx_label))
        self.play(Indicate(dx_label))
        self.wait(2)

        self.play(ShowCreation(df_arrow))
        self.play(Write(df_label))
        self.wait()

        self.play(ShowCreation(dg_arrow))
        self.play(Write(dg_label))
        self.wait()

    def show_derivative_ratio(self):
        q_marks = VGroup(*self.equals_q[1:])

        deriv_ratio = TexMobject(
            "{ \\frac{df}{dx}", "(", "a", ")", "\\,dx",
            "\\over \\,",
            "\\frac{dg}{dx}", "(", "a", ")", "\\,dx}",
        )
        deriv_ratio.set_color_by_tex("a", self.x_color)
        deriv_ratio.set_color_by_tex("df", self.f_color)
        deriv_ratio.set_color_by_tex("dg", self.g_color)
        deriv_ratio.move_to(q_marks, LEFT)

        dxs = VGroup(*deriv_ratio.get_parts_by_tex("\\,dx"))
        circles = VGroup(*[
            Circle(color = GREEN).replace(dx).scale_in_place(1.3)
            for dx in dxs
        ])

        self.play(FadeOut(q_marks))
        self.play(Write(deriv_ratio))
        self.wait(2)

        self.play(FadeIn(circles))
        self.wait()
        self.play(FadeOut(circles), dxs.fade, 0.75)
        self.wait(2)

        self.transition_to_alt_config(
            transformation_kwargs = {"run_time" : 2},
            dx = self.dx/10,
        )
        self.wait()

    def show_example(self):
        lhs = TexMobject(
            "\\lim", "_{x \\to", "0}",
            "{\\sin(", "x", ")", "\\over \\,", "x}",
        )
        rhs = TexMobject(
            "=", 
            "{\\cos(", "0", ")", "\\over \\,", "1}",
            "=", "1"
        )
        rhs.next_to(lhs, RIGHT)
        equation = VGroup(lhs, rhs)
        equation.to_corner(UP+RIGHT)
        for part in equation:
            part.set_color_by_tex("0", self.x_color)
        brace = Brace(lhs, DOWN)
        brace_text = brace.get_text("Looks like 0/0")
        brace_text.add_background_rectangle()

        name = TextMobject(
            "``", "L'Hôpital's", " rule", "''",
            arg_separator = ""
        )
        name.shift(FRAME_X_RADIUS*RIGHT/2)
        name.to_edge(UP)

        self.play(Write(lhs))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        self.play(Write(rhs[0]), ReplacementTransform(
            VGroup(*lhs[3:6]).copy(),
            VGroup(*rhs[1:4])
        ))
        self.wait()
        self.play(ReplacementTransform(
            VGroup(*lhs[6:8]).copy(),
            VGroup(*rhs[4:6]),
        ))
        self.wait()
        self.play(Write(VGroup(*rhs[6:])))
        self.wait(2)

        ##Slide away
        example = VGroup(lhs, rhs, brace, brace_text)
        self.play(
            example.scale, 0.7,
            example.to_corner, DOWN+RIGHT, SMALL_BUFF,
            path_arc = 7*np.pi/6,
        )
        self.play(Write(name))
        self.wait(2)

        self.rule_name = name

    def show_bernoulli_and_lHopital(self):
        lhopital_name = self.rule_name.get_part_by_tex("L'Hôpital's")
        strike = Line(
            lhopital_name.get_left(),
            lhopital_name.get_right(),
            color = RED
        )
        bernoulli_name = TextMobject("Bernoulli's")
        bernoulli_name.next_to(lhopital_name, DOWN)

        bernoulli_image = ImageMobject("Johann_Bernoulli2")
        lhopital_image = ImageMobject("Guillaume_de_L'Hopital")
        for image in bernoulli_image, lhopital_image:
            image.set_height(self.image_height)
            image.to_edge(UP)

        arrow = Arrow(ORIGIN, DOWN, buff = 0, color = GREEN)
        arrow.next_to(lhopital_image, DOWN, buff = SMALL_BUFF)
        dollars = VGroup(*[TexMobject("\\$") for x in range(5)])
        for dollar, alpha in zip(dollars, np.linspace(0, 1, len(dollars))):
            angle = alpha*np.pi
            dollar.move_to(np.sin(angle)*RIGHT + np.cos(angle)*UP)
        dollars.set_color(GREEN)
        dollars.next_to(arrow, RIGHT, MED_LARGE_BUFF)
        dollars[0].set_fill(opacity = 0)
        dollars.save_state()

        self.play(ShowCreation(strike))
        self.play(
            Write(bernoulli_name),
            FadeIn(bernoulli_image)
        )
        self.wait()
        self.play(
            FadeIn(lhopital_image),
            bernoulli_image.next_to, arrow, DOWN, SMALL_BUFF,
            ShowCreation(arrow),
            FadeIn(dollars)
        )

        for x in range(10):
            dollars.restore()
            self.play(*[
                Transform(*pair)
                for pair in zip(dollars, dollars[1:])
            ] + [
                FadeOut(dollars[-1])
            ])

    ####

    def f(self, x):
        return -0.1*(x-self.a_value)*x*(x+4.5)

    def g(self, x):
        return np.log(x-self.a_value+1)

    def get_frac(self, input_tex, color = WHITE):
        result = TexMobject(
            "{f", "(", input_tex, ")", "\\over \\,",
            "g", "(", input_tex, ")}"
        )
        result.set_color_by_tex("f", self.f_color)
        result.set_color_by_tex("g", self.g_color)
        result.set_color_by_tex(input_tex, color)

        result.numerator = VGroup(*result[:4])
        result.denominator = VGroup(*result[-4:])
        result.over = result.get_part_by_tex("over")

        return result

class CannotUseLHopital(TeacherStudentsScene):
    def construct(self):
        deriv = TexMobject(
            "{d(e^x)", "\\over \\,", "dx}", "(", "x", ")", "=",
            "\\lim", "_{h", "\\to 0}",
            "{e^{", "x", "+", "h}", 
            "-", "e^", "x",
            "\\over \\,", "h}"
        )
        deriv.to_edge(UP)
        deriv.set_color_by_tex("x", RED)
        deriv.set_color_by_tex("dx", GREEN)
        deriv.set_color_by_tex("h", GREEN)
        deriv.set_color_by_tex("e^", YELLOW)

        self.play(
            Write(deriv),
            *it.chain(*[
                [pi.change_mode, "pondering", pi.look_at, deriv]
                for pi in self.get_pi_creatures()
            ])
        )
        self.wait()
        self.student_says(
            "Use L'Hôpital's rule!", 
            target_mode = "hooray"
        )
        self.wait()
        answer = TexMobject(
            "\\text{That requires knowing }",
            "{d(e^x)", "\\over \\,", "dx}"
        )
        answer.set_color_by_tex("e^", YELLOW)
        answer.set_color_by_tex("dx", GREEN)
        self.teacher_says(
            answer,
            bubble_kwargs = {"height" : 2.5},
            target_mode = "hesitant"
        )
        self.change_student_modes(*["confused"]*3)
        self.wait(3)

class NextVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        next_video = series[7]
        brace = Brace(next_video, DOWN)

        integral = TexMobject("\\int", "f(x)", "dx")
        ftc = TexMobject(
            "F(b)", "-", "F(a)", "=", "\\int_a^b", 
            "{dF", "\\over \\,", "dx}", "(x)", "dx"
        )
        for tex_mob in integral, ftc:
            tex_mob.set_color_by_tex("dx", GREEN)
            tex_mob.set_color_by_tex("f", YELLOW)
            tex_mob.set_color_by_tex("F", YELLOW)
            tex_mob.next_to(brace, DOWN)

        self.add(series)
        self.play(
            GrowFromCenter(brace),
            next_video.set_color, YELLOW,
            self.get_teacher().change_mode, "raise_right_hand",
            self.get_teacher().look_at, next_video
        )
        self.play(Write(integral))
        self.wait(2)
        self.play(*[
            ReplacementTransform(
                VGroup(*integral.get_parts_by_tex(p1)),
                VGroup(*ftc.get_parts_by_tex(p2)),
                run_time = 2,
                path_arc = np.pi/2,
                rate_func = squish_rate_func(smooth, alpha, alpha+0.5)
            )
            for alpha, (p1, p2) in zip(np.linspace(0, 0.5, 3), [
                ("int", "int"),
                ("f", "F"),
                ("dx", "dx"),
            ])
        ]+[
            Write(VGroup(*ftc.get_parts_by_tex(part)))
            for part in ("-", "=", "over", "(x)")
        ])
        self.change_student_modes(*["pondering"]*3)
        self.wait(3)

class Chapter7PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali  Yahya",
            "Meshal  Alshammari",
            "CrypticSwarm    ",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Nathan Pellegrin",
            "Karan Bhargava", 
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
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }

class Thumbnail(Scene):
    def construct(self):
        lim = TexMobject("\\lim", "_{h", "\\to 0}")
        lim.set_color_by_tex("h", GREEN)
        lim.set_height(5)
        self.add(lim)















