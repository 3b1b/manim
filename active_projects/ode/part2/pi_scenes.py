from manimlib.imports import *
from active_projects.ode.part2.wordy_scenes import WriteHeatEquationTemplate


class ReactionsToInitialHeatEquation(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.set_color(BLUE_C)
        randy.center()

        point = VectorizedPoint().next_to(randy, UL, LARGE_BUFF)
        randy.add_updater(lambda r: r.look_at(point))

        self.play(randy.change, "horrified")
        self.wait()
        self.play(randy.change, "pondering")
        self.wait()
        self.play(
            randy.change, "confused",
            point.next_to, randy, UR, LARGE_BUFF,
        )
        self.wait(2)
        self.play(
            point.shift, 2 * DOWN,
            randy.change, "horrified"
        )
        self.wait(4)


class ContrastPDEToODE(TeacherStudentsScene):
    CONFIG = {
        "random_seed": 2,
    }

    def construct(self):
        student = self.students[2]
        pde, ode = words = VGroup(*[
            TextMobject(
                text + "\\\\",
                "Differential\\\\",
                "Equation"
            )
            for text in ("Partial", "Ordinary")
        ])
        pde[0].set_color(YELLOW)
        ode[0].set_color(BLUE)
        for word in words:
            word.arrange(DOWN, aligned_edge=LEFT)

        words.arrange(RIGHT, buff=LARGE_BUFF)
        words.next_to(student.get_corner(UR), UP, MED_LARGE_BUFF)
        words.shift(UR)
        lt = TexMobject("<")
        lt.scale(1.5)
        lt.move_to(Line(pde.get_right(), ode.get_left()))

        for pi in self.pi_creatures:
            pi.add_updater(lambda p: p.look_at(pde))

        self.play(
            FadeInFromDown(VGroup(words, lt)),
            student.change, "raise_right_hand",
        )
        self.play(
            self.get_student_changes("pondering", "pondering", "hooray"),
            self.teacher.change, "happy"
        )
        self.wait(3)
        self.play(
            Swap(ode, pde),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(
                "erm", "sassy", "confused"
            )
        )
        self.look_at(words)
        self.change_student_modes(
            "thinking", "thinking", "tease",
        )
        self.wait(3)


class AskAboutWhereEquationComesFrom(TeacherStudentsScene, WriteHeatEquationTemplate):
    def construct(self):
        equation = self.get_d1_equation()
        equation.move_to(self.hold_up_spot, DOWN)

        self.play(
            FadeInFromDown(equation),
            self.teacher.change, "raise_right_hand"
        )
        self.student_says(
            "Um...why?",
            target_mode="sassy",
            student_index=2,
            bubble_kwargs={"direction": RIGHT},
        )
        self.change_student_modes(
            "confused", "confused", "sassy",
        )
        self.wait()
        self.play(
            self.teacher.change, "pondering",
        )
        self.wait(2)


class AskWhyRewriteIt(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Why?", student_index=1,
            bubble_kwargs={"height": 2, "width": 2},
        )
        self.students[1].bubble = None
        self.teacher_says(
            "One step closer\\\\to derivatives"
        )
        self.change_student_modes(
            "thinking", "thinking", "thinking",
            look_at_arg=4 * LEFT + 2 * UP
        )
        self.wait(2)


class ReferenceKhanVideo(TeacherStudentsScene):
    def construct(self):
        khan_logo = ImageMobject("KhanLogo")
        khan_logo.set_height(1)
        khan_logo.next_to(self.teacher, UP, buff=2)
        khan_logo.shift(2 * LEFT)

        self.play(
            self.teacher.change, "raise_right_hand",
        )
        self.change_student_modes(
            "thinking", "pondering", "thinking",
            look_at_arg=self.screen
        )
        self.wait()
        self.play(FadeInFromDown(khan_logo))
        self.look_at(self.screen)
        self.wait(15)
