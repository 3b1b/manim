from manimlib.imports import *


class WhyWouldYouCare(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Who cares!",
            target_mode="sassy",
            student_index=2,
            added_anims=[self.teacher.change, "guilty"],
        )
        self.wait()
        self.play(
            RemovePiCreatureBubble(self.students[2]),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(
                "pondering", "erm", "thinking",
                look_at_arg=self.screen,
            )
        )
        self.look_at(self.screen)
        self.wait(5)
