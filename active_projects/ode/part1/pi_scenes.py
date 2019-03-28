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


# class TourOfDifferentialEquations(Scene):
#     def construct(self):
#         pass


class ProveTeacherWrong(TeacherStudentsScene):
    def construct(self):
        tex_config = {
            "tex_to_color_map": {
                "{\\theta}": BLUE,
                "{\\dot\\theta}": YELLOW,
                "{\\ddot\\theta}": RED,
            }
        }
        func = TexMobject(
            "{\\theta}(t)", "=",
            "\\theta_0", "\\cos(\\sqrt{g / L} \\cdot t)",
            **tex_config,
        )
        d_func = TexMobject(
            "{\\dot\\theta}(t)", "=",
            "-\\left(\\sqrt{g / L}\\right)",
            "\\theta_0", "\\sin(\\sqrt{g / L} \\cdot t)",
            **tex_config,
        )
        dd_func = TexMobject(
            "{\\ddot\\theta}(t)", "=",
            "-\\left(g / L\\right)",
            "\\theta_0", "\\cos(\\sqrt{g / L} \\cdot t)",
            **tex_config,
        )
        # ode = TexMobject(
        #     "\\ddot {\\theta}({t})", "=",
        #     "-\\mu \\dot {\\theta}({t})",
        #     "-{g \\over L} \\sin\\big({\\theta}({t})\\big)",
        #     **tex_config,
        # )
        ode = get_ode()
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


class AskAboutActuallySolving(TeacherStudentsScene):
    def construct(self):
        ode = get_ode()
        ode.to_corner(UL)
        self.add(ode)
        morty = self.teacher

        self.student_says(
            "Yeah yeah, but how do\\\\"
            "you acutally \\emph{solve} it?",
            student_index=1,
            target_mode="sassy",
            added_anims=[morty.change, "thinking"],
        )
        self.change_student_modes(
            "confused", "sassy", "confused",
            look_at_arg=ode,
        )
        self.wait()
        self.teacher_says(
            "What do you mean\\\\ by ``solve''?",
            target_mode="speaking",
            added_anims=[self.get_student_changes(
                *3 * ["erm"]
            )]
        )
        self.play(self.students[1].change, "angry")
        self.wait(3)


class HungerForExactness(TeacherStudentsScene):
    def construct(self):
        students = self.students
        you = students[2]
        teacher = self.teacher

        ode = get_ode()
        ode.to_corner(UL)
        left_part = ode[:5]
        friction_part = ode[5:11]
        right_part = ode[11:]
        self.add(ode)
        frictionless_group = VGroup(left_part, right_part)

        proposed_solution = TexMobject(
            "\\theta_0\\cos((\\sqrt{g/L})t)e^{-\\mu t}"
        )
        proposed_solution.next_to(
            you.get_corner(UL), UP, buff=0.7
        )
        proposed_solution_rect = SurroundingRectangle(
            proposed_solution, buff=MED_SMALL_BUFF,
        )
        proposed_solution_rect.set_color(BLUE)
        proposed_solution_rect.round_corners()

        solution_p1 = TexMobject(
            """
            \\theta(t) = 2\\text{am}\\left(
                \\frac{\\sqrt{2g + Lc_1} (t + c_2)}{2\\sqrt{L}},
                \\frac{4g}{2g + Lc_1}
            \\right)
            """,
        )
        solution_p1.to_corner(UL)
        solution_p2 = TexMobject(
            "c_1, c_2 = \\text{Constants depending on initial conditions}"
        )
        solution_p2.set_color(LIGHT_GREY)
        solution_p2.scale(0.75)
        solution_p3 = TexMobject(
            """
            \\text{am}(u, k) =
            \\int_0^u \\text{dn}(v, k)\\,dv
            """
        )
        solution_p3.name = TextMobject(
            "(Jacobi amplitude function)"
        )
        solution_p4 = TexMobject(
            """
            \\text{dn}(u, k) =
            \\sqrt{1 - k^2 \\sin^2(\\phi)}
            """
        )
        solution_p4.name = TextMobject(
            "(Jacobi elliptic function)"
        )
        solution_p5 = TextMobject("Where $\\phi$ satisfies")
        solution_p6 = TexMobject(
            """
            u = \\int_0^\\phi \\frac{dt}{\\sqrt{1 - k^2 \\sin^2(t)}}
            """
        )

        solution = VGroup(
            solution_p1,
            solution_p2,
            solution_p3,
            solution_p4,
            solution_p5,
            solution_p6,
        )
        solution.arrange(DOWN)
        solution.scale(0.7)
        solution.to_corner(UL, buff=MED_SMALL_BUFF)
        solution.set_stroke(width=0, background=True)

        solution.remove(solution_p2)
        solution_p1.add(solution_p2)
        solution.remove(solution_p5)
        solution_p6.add(solution_p5)

        for part in [solution_p3, solution_p4]:
            part.name.scale(0.7 * 0.7)
            part.name.set_color(LIGHT_GREY)
            part.name.next_to(part, RIGHT)
            part.add(part.name)

        self.student_says(
            "Right, but like,\\\\"
            "what \\emph{is} $\\theta(t)$?",
            target_mode="sassy",
            added_anims=[teacher.change, "guilty"],
        )
        self.wait()
        self.play(
            FadeInFromDown(proposed_solution),
            RemovePiCreatureBubble(
                you,
                target_mode="raise_left_hand",
                look_at_arg=proposed_solution,
            ),
            teacher.change, "pondering",
            students[0].change, "pondering",
            students[1].change, "hesitant",
        )
        self.play(ShowCreation(proposed_solution_rect))
        self.play(
            proposed_solution.shift, 3 * RIGHT,
            proposed_solution_rect.shift, 3 * RIGHT,
            you.change, "raise_right_hand", teacher.eyes,
        )
        self.wait(3)

        self.play(
            FadeOut(proposed_solution),
            FadeOut(proposed_solution_rect),
            ode.move_to, self.hold_up_spot, DOWN,
            ode.shift, LEFT,
            teacher.change, "raise_right_hand",
            self.get_student_changes(*3 * ["pondering"])
        )
        self.wait()
        ode.save_state()
        self.play(
            left_part.move_to, friction_part, RIGHT,
            left_part.match_y, left_part,
            friction_part.to_corner, DR,
            friction_part.fade, 0.5,
        )
        self.wait()

        modes = ["erm", "sad", "sad", "horrified"]
        for part, mode in zip(solution, modes):
            self.play(
                FadeInFrom(part, UP),
                self.get_student_changes(
                    *3 * [mode],
                    look_at_arg=part,
                )
            )
            self.wait()
        self.wait(3)
        self.change_student_modes("tired", "sad", "concerned_musician")
        self.wait(4)
        self.look_at(solution)
        self.wait(5)
        self.play(
            FadeOutAndShift(solution, 2 * LEFT),
            Restore(ode),
            self.get_student_changes(
                "sick", "angry", "tired",
            )
        )
        self.wait(3)

        mystery = TexMobject(
            "\\theta(t) = ???",
            tex_to_color_map={"\\theta": BLUE},
        )
        mystery.scale(2)
        mystery.to_edge(UP)
        mystery.set_stroke(width=0, background=True)

        self.play(
            FadeInFromDown(mystery),
            self.teacher.change, "pondering"
        )
        self.add(
            AnimatedBoundary(mystery, stroke_width=1),
            mystery,
        )
        self.change_all_student_modes("sad")
        self.look_at(mystery)
        self.wait(5)


class ItGetsWorse(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("It gets\\\\worse")
        self.change_student_modes(
            "hesitant", "pleading", "erm"
        )
        self.wait(2)
