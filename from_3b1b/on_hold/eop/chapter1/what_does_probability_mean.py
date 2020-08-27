from manimlib.imports import *


class WhatDoesItReallyMean(TeacherStudentsScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": MAROON_E,
            "flip_at_start": True,
        },
    }

    def construct(self):
        student_q = TextMobject(
            "What does", "``probability''\\\\",
            "\\emph{actually}", "mean?"
        )
        student_q.set_color_by_tex("probability", YELLOW)
        self.student_says(student_q, target_mode="sassy")
        self.wait()
        self.play(
            self.students[1].change_mode, "confused"
        )
        self.wait(2)
        student_bubble = self.students[1].bubble
        self.students[1].bubble = None
        student_bubble.add(student_bubble.content)
        self.play(
            student_bubble.scale, 0.5,
            student_bubble.to_corner, UL,
        )
        self.teacher_says(
            "Don't worry -- philosophy\\\\ can come later!",
            added_anims=[self.get_student_changes(*3 * ["happy"])],
        )
        self.wait(2)
        self.play(RemovePiCreatureBubble(self.teacher))
        self.play(*[
            ApplyMethod(pi.look_at, ORIGIN) for pi in self.get_pi_creatures()
        ])
        self.change_all_student_modes("pondering", look_at_arg=UP)
        self.wait(3)
        self.change_student_modes("confused", look_at_arg=UP)
        self.wait(3)
