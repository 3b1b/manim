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

from eoc.graph_scene import *

class LastVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        last_video = series[2]
        next_video = series[3]
        last_video_color = last_video[0].get_fill_color()
        early_videos = VGroup(*series[:3])
        later_videos = VGroup(*series[3:])
        this_video = VideoIcon().scale(0.5)
        this_video.move_to(VGroup(last_video, next_video), DOWN)

        known_formulas = VGroup(*map(TexMobject, [
            "\\frac{d(x^n)}{dx} = nx^{n-1}",
            "\\frac{d(\\sin(x))}{dx} = \\cos(x)",
        ]))
        known_formulas.arrange_submobjects(
            DOWN, buff = MED_LARGE_BUFF,
        )
        known_formulas.scale_to_fit_height(2.5)
        exp_question = TexMobject("2^x", ", 7^x", ", e^x", " ???")

        last_video_brace = Brace(last_video)
        known_formulas.next_to(last_video_brace, DOWN)
        last_video_brace.save_state()
        last_video_brace.shift(3*LEFT)
        last_video_brace.set_fill(opacity = 0)

        self.add(series)
        self.play(
            last_video_brace.restore,
            last_video.highlight, YELLOW,
            self.get_teacher().change_mode, "raise_right_hand",
        )
        self.play(Write(known_formulas))
        self.dither()
        self.student_says(
            exp_question, student_index = -1,
            added_anims = [self.get_teacher().change_mode, "pondering"]
        )
        self.dither(2)
        self.play(known_formulas.replace, last_video)
        last_video.add(known_formulas)
        this_video_copy = this_video.copy()
        self.play(
            early_videos.stretch_to_fit_width,
            early_videos.get_width() - this_video_copy.get_width(),
            early_videos.next_to, this_video_copy, LEFT, SMALL_BUFF, DOWN,
            later_videos.stretch_to_fit_width,
            later_videos.get_width() - this_video_copy.get_width(),
            later_videos.next_to, this_video_copy, RIGHT, SMALL_BUFF, DOWN,
            last_video_brace.stretch_to_fit_width, 
            this_video_copy.get_width(),
            last_video_brace.next_to, this_video_copy, DOWN, SMALL_BUFF,
            GrowFromCenter(this_video)
        )
        self.play(
            last_video.highlight, last_video_color,
            this_video.highlight, YELLOW
        )
        self.play(
            FadeOut(self.get_students()[-1].bubble),            
            exp_question.next_to, last_video_brace, DOWN,
            *[
                ApplyMethod(pi.change_mode, "pondering")
                for pi in self.get_students()
            ]
        )

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
                function[i][j].highlight(self.time_color)

        t_expression = TexMobject("t", "=", "\\text{Time (in days)}")
        t_expression.to_corner(UP+RIGHT)
        t_expression[0].highlight(self.time_color)

        pop_brace, mass_brace = [
            Brace(function[0], DOWN)
            for function in P_t, M_t
        ]
        for brace, word in (pop_brace, "size"), (mass_brace, "mass"):
            text = brace.get_text("Population %s"%word)
            text.to_edge(LEFT)
            brace.text = text

        self.play(Write(f_x))
        self.dither()
        self.play(
            Transform(f_x, f_t),
            FadeIn(
                t_expression,
                run_time = 2,
                submobject_mode = "lagged_start"
            )
        )
        self.play(Transform(f_x, P_t))
        self.play(
            GrowFromCenter(pop_brace),
            Write(pop_brace.text, run_time = 2)
        )
        self.dither(2)

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
        self.dither()
        self.play(
            Transform(self.function, self.mass_function),
            Transform(self.pop_brace, self.mass_brace),
            Transform(self.pop_brace.text, self.mass_brace.text),
        )
        self.dither()
        for x in range(total_num_days-num_start_days):
            self.let_one_day_pass()
            self.dither()
        self.joint_blink(shuffle = False)
        self.dither()

    def count_through_days(self):
        self.reset()
        brace = self.get_population_size_descriptor()
        days_to_let_pass = 3

        self.play(GrowFromCenter(brace))
        self.dither()
        for x in range(days_to_let_pass):
            self.let_one_day_pass()
            new_brace = self.get_population_size_descriptor()
            self.play(Transform(brace, new_brace))
            self.dither()

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
        self.dither(3)
        for mob in dM, dt:
            self.play(Indicate(mob))
            self.dither()

        self.dM_dt_question = dM_dt_question

    def growth_per_day(self):
        day_to_day, frac = self.get_from_day_to_day_label()

        self.play(
            FadeOut(self.dM_dt_question),
            FadeIn(day_to_day)
        )
        rect = self.let_day_pass_and_highlight_new_creatures(frac)

        for x in range(2):
            new_day_to_day, new_frac = self.get_from_day_to_day_label()
            self.play(*map(FadeOut, [rect, frac]))
            frac = new_frac
            self.play(Transform(day_to_day, new_day_to_day))
            rect = self.let_day_pass_and_highlight_new_creatures(frac)
        self.play(*map(FadeOut, [rect, frac, day_to_day]))

    def let_day_pass_and_highlight_new_creatures(self, frac):
        num_new_creatures = 2**self.get_curr_day()
        brace = self.population_size_descriptor

        self.let_one_day_pass()
        new_brace = self.get_population_size_descriptor()
        self.play(Transform(brace, new_brace))
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
        self.dither()
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
        ).highlight(YELLOW)
        VGroup(
            difference_eq[0][3],
            difference_eq[1][-1],
            real_deriv[0][3],
            real_deriv[0][4],
            real_deriv[1][-2],
            real_deriv[1][-1],
        ).highlight(GREEN)

        expressions = [false_deriv, difference_eq, real_deriv]
        text_arg_list = [
            ("Tempting", "...",),
            ("Rate of change", "\\\\ per day"),
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

        brace = self.population_size_descriptor

        self.play(*map(FadeIn, [
            false_deriv, false_deriv.brace, false_deriv.brace_text
        ]))
        self.dither()
        self.play(
            Transform(time, new_time),
            FadeOut(fading_creatures)
        )
        new_brace = self.get_population_size_descriptor()
        self.play(Transform(brace, new_brace))
        self.dither()
        for x in range(3):
            self.let_one_day_pass(run_time = 2)
            new_brace = self.get_population_size_descriptor()
            self.play(Transform(brace, new_brace))
            self.dither(2)

        for expression in difference_eq, real_deriv:
            expression.brace_text[1].highlight(GREEN)
            self.play(
                Transform(false_deriv, expression),
                Transform(false_deriv.brace, expression.brace),
                Transform(false_deriv.brace_text, expression.brace_text),
            )
            self.dither(3)
        self.play(FadeOut(brace))
        self.reset()
        for x in range(self.get_num_days()):
            self.let_one_day_pass()
        self.dither()

        rect = Rectangle(color = YELLOW)
        rect.replace(real_deriv)
        rect.stretch_to_fit_width(rect.get_width()+MED_SMALL_BUFF)
        rect.stretch_to_fit_height(rect.get_height()+MED_SMALL_BUFF)
        self.play(*map(FadeOut, [
            false_deriv.brace, false_deriv.brace_text
        ]))
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
        self.dither(3)

    ###########

    def create_pi_creatures(self):
        width, height = self.pi_creature_grid_dimensions
        creature_array = VGroup(*[
            VGroup(*[
                PiCreature(mode = "plain")
                for y in range(height)
            ]).arrange_submobjects(UP, buff = MED_LARGE_BUFF)
            for x in range(width)
        ]).arrange_submobjects(RIGHT, buff = MED_LARGE_BUFF)
        creatures = VGroup(*it.chain(*creature_array))
        creatures.scale_to_fit_height(self.pi_creature_grid_height)
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

        self.play(*map(FadeOut, faders))
        self.play(*map(FadeIn, [first_creature, new_time]))
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
        top_words.scale_to_fit_width(4)
        top_words.next_to(
            self.function, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        top_words[1].highlight(GREEN)

        bottom_words = TexMobject(
            str(2**curr_day),
            "\\text{ creatures}", "\\over {1 \\text{ day}}"
        )
        bottom_words[0].highlight(GREEN)
        bottom_words.next_to(top_words, DOWN, buff = MED_LARGE_BUFF)

        return top_words, bottom_words






































