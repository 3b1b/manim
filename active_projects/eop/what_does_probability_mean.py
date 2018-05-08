
from big_ol_pile_of_manim_imports import *

class WhatDoesItReallyMean(TeacherStudentsScene):

    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": MAROON_E,
            "flip_at_start": True,
        },
    }

    def construct(self):

        student_q = TextMobject("What does", "``probability''", "\emph{actually}", "mean?")
        student_q.set_color_by_tex("probability", YELLOW)
        self.student_says(student_q, target_mode = "sassy")
        self.wait()
        self.teacher_says("Don't worry -- philosophy can come later!")
        self.wait()

