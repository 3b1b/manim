from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.shared_constructs import *


class SomeOfYouWatching(TeacherStudentsScene):
    CONFIG = {
        "camera_config": {
            "background_color": DARKER_GREY,
        }
    }

    def construct(self):
        screen = self.screen
        screen.scale(1.25, about_edge=UL)
        screen.set_fill(BLACK, 1)
        self.add(screen)

        self.teacher.change("raise_right_hand")
        for student in self.students:
            student.change("pondering", screen)

        self.student_says(
            "Well...yeah",
            target_mode="tease"
        )
        self.wait(3)


class FormulasAreLies(PiCreatureScene):
    def construct(self):
        you = self.pi_creature
        t2c = {
            "{L}": BLUE,
            "{g}": YELLOW,
            "\\theta_0": WHITE,
            "\\sqrt{\\,": WHITE,
        }
        kwargs = {"tex_to_color_map": t2c}
        period_eq = TexMobject(
            "\\text{Period} = 2\\pi \\sqrt{\\,{L} / {g}}",
            **kwargs
        )
        theta_eq = TexMobject(
            "\\theta(t) = \\theta_0 \\cos\\left("
            "\\sqrt{\\,{L} / {g}} \\cdot t"
            "\\right)",
            **kwargs
        )
        equations = VGroup(theta_eq, period_eq)
        equations.arrange(DOWN, buff=LARGE_BUFF)

        for eq in period_eq, theta_eq:
            i = eq.index_of_part_by_tex("\\sqrt")
            eq.sqrt_part = eq[i:i + 4]

        theta0 = theta_eq.get_part_by_tex("\\theta_0")
        theta0_words = TextMobject("Starting angle")
        theta0_words.next_to(theta0, UL)
        theta0_words.shift(UP + 0.5 * RIGHT)
        arrow = Arrow(
            theta0_words.get_bottom(),
            theta0,
            color=WHITE,
            tip_length=0.25,
        )

        bubble = SpeechBubble()
        bubble.pin_to(you)
        bubble.write("Lies!")
        bubble.content.scale(2)
        bubble.resize_to_content()

        self.add(period_eq)
        you.change("pondering", period_eq)
        self.wait()
        theta_eq.remove(*theta_eq.sqrt_part)
        self.play(
            TransformFromCopy(
                period_eq.sqrt_part,
                theta_eq.sqrt_part,
            ),
            FadeIn(theta_eq)
        )
        theta_eq.add(*theta_eq.sqrt_part)
        self.play(
            FadeInFrom(theta0_words, LEFT),
            GrowArrow(arrow),
        )
        self.wait()
        self.play(you.change, "confused")
        self.wait()
        self.play(
            you.change, "angry",
            ShowCreation(bubble),
            FadeInFromPoint(bubble.content, you.mouth),
            equations.to_edge, LEFT,
            FadeOut(arrow),
            FadeOut(theta0_words),
        )
        self.wait()

    def create_pi_creature(self):
        return You().flip().to_corner(DR)


class ProveTeacherWrong(TeacherStudentsScene):
    def construct(self):
        tex_config = {
            "tex_to_color_map": {"{\\theta}": BLUE}
        }
        func = TexMobject(
            "{\\theta}(t)", "=",
            "\\theta_0", "\\cos(\\sqrt{g / L} \\cdot t)",
            **tex_config,
        )
        d_func = TexMobject(
            "\\dot {\\theta}(t)", "=",
            "-\\left(\\sqrt{g / L}\\right)",
            "\\theta_0", "\\sin(\\sqrt{g / L} \\cdot t)",
            **tex_config,
        )
        dd_func = TexMobject(
            "\\ddot {\\theta}(t)", "=",
            "-\\left(g / L\\right)",
            "\\theta_0", "\\cos(\\sqrt{g / L} \\cdot t)",
            **tex_config,
        )
        ode = TexMobject(
            "\\ddot {\\theta}({t})", "=",
            "-\\mu \\dot {\\theta}({t})",
            "-{g \\over L} \\sin\\big({\\theta}({t})\\big)",
            **tex_config,
        )
        arrows = [TexMobject("\\Downarrow") for x in range(2)]

        VGroup(func, d_func, dd_func, ode, *arrows).scale(0.7)

        teacher = self.teacher
        you = self.students[2]

        self.student_thinks(ode)
        you.add_updater(lambda m: m.look_at(func))
        self.teacher_holds_up(func)
        self.wait()

        group = VGroup(arrows[0], d_func, arrows[1], dd_func)
        group.arrange(DOWN)
        group.move_to(func, DOWN)

        arrow = Arrow(
            group.get_corner(UL),
            ode.get_top(),
            path_arc=PI / 2,
        )
        q_marks = VGroup(*[
            TexMobject("?").scale(1.5).next_to(
                arrow.point_from_proportion(a),
                UP
            )
            for a in np.linspace(0.2, 0.8, 5)
        ])
        cycle_animation(VFadeInThenOut(
            q_marks,
            lag_ratio=0.2,
            run_time=4,
            rate_func=squish_rate_func(smooth, 0, 0.5)
        ))

        self.play(
            func.next_to, group, UP,
            LaggedStartMap(
                FadeInFrom, group,
                lambda m: (m, UP)
            ),
            teacher.change, "guilty",
            you.change, "sassy",
        )

        rect = SurroundingRectangle(
            VGroup(group, func)
        )
        dashed_rect = DashedVMobject(rect, num_dashes=75)
        animated_rect = AnimatedBoundary(dashed_rect, cycle_rate=1)

        self.wait()
        self.add(animated_rect, q_marks)
        self.play(
            ShowCreation(arrow),
            # FadeInFromDown(q_mark),
            self.get_student_changes("confused", "confused")
        )
        self.wait(4)
        self.change_student_modes(
            *3 * ["pondering"],
            self.teacher.change, "maybe"
        )
        self.wait(8)
