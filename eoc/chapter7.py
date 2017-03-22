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

class ApproachWordToLim(PiCreatureScene):
    CONFIG = {
        "dx_color" : GREEN
    }
    def construct(self):
        limit_expression = self.get_limit_expression()
        limit_expression.next_to(
            self.pi_creature, LEFT, aligned_edge = UP
        )

        evaluated_expressions = self.get_evaluated_expressions()
        evaluated_expressions.to_edge(UP)
        brace = Brace(evaluated_expressions[0][-1], DOWN)
        question = TextMobject("What does this ``approach''?")
        question.next_to(brace, DOWN)

        expression = evaluated_expressions[0]
        self.add(expression, brace, question)
        self.change_mode("raise_right_hand")
        for next_expression in evaluated_expressions[1:]:
            next_expression.move_to(expression, RIGHT)
            self.play(Transform(expression, next_expression))
            self.dither(0.5)
        self.play(
            Write(limit_expression),
            self.pi_creature.change_mode, "pondering"
        )
        self.play(Indicate(limit_expression[0]))
        self.dither(2)

    def get_limit_expression(self):
        lim = TexMobject("\\lim_", "{dx", " \\to 0}")
        lim.highlight_by_tex("dx", self.dx_color)
        ratio = self.get_expression("dx")
        ratio.next_to(lim, RIGHT)
        limit_expression = VGroup(lim, ratio)
        return limit_expression

    def get_evaluated_expressions(self):
        result = VGroup()
        for num_zeros in range(1, 6):
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
        "dx" : 0.7,
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
            for nudge in 0, self.dx
        ]
        ss_group = self.get_secant_slope_group(
            self.start_x, graph,
            dx = self.dx,
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
            target_dx = self.dx,
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


























