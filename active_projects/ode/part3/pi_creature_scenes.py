from manimlib.imports import *


class IveHeardOfThis(TeacherStudentsScene):
    def construct(self):
        point = VectorizedPoint()
        point.move_to(3 * RIGHT + 2 * UP)
        self.student_says(
            "I've heard\\\\", "of this!",
            student_index=1,
            target_mode="hooray",
            bubble_kwargs={
                "height": 3,
                "width": 3,
                "direction": RIGHT,
            },
            run_time=1,
        )
        self.change_student_modes(
            "thinking", "hooray", "thinking",
            look_at_arg=point,
            added_anims=[self.teacher.change, "happy"]
        )
        self.wait(3)
        self.student_says(
            "But who\\\\", "cares?",
            student_index=1,
            target_mode="maybe",
            bubble_kwargs={
                "direction": RIGHT,
                "width": 3,
                "height": 3,
            },
            run_time=1,
        )
        self.change_student_modes(
            "pondering", "maybe", "pondering",
            look_at_arg=point,
            added_anims=[self.teacher.change, "guilty"]
        )
        self.wait(5)
