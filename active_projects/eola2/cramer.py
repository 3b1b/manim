from big_ol_pile_of_manim_imports import *


X_COLOR = GREEN
Y_COLOR = RED
Z_COLOR = BLUE
OUTPUT_COLOR = MAROON_B


def get_cramer_matrix(matrix, output_vect):
    """
    The inputs matrix and output_vect should be Matrix mobjects
    """
    # new_matrix = np.append(
    #     matrix.mob_matrix[:, :2],
    #     output_vect,
    #     axis=1
    # )
    pass


class LinearSystem(VGroup):
    CONFIG = {
        "matrix_config": {
            "element_to_mobject": Integer,
        },
        "dimensions": 3,
        "min_int": -9,
        "max_int": 10,
        "height": 4,
    }

    def __init__(self, matrix=None, output_vect=None, **kwargs):
        VGroup.__init__(self, **kwargs)
        dim = self.dimensions
        if matrix is None:
            matrix = np.random.randint(
                self.min_int,
                self.max_int,
                size=(dim, dim)
            )
        self.matrix_mobject = IntegerMatrix(matrix)
        self.equals = TexMobject("=")
        self.equals.scale(1.5)

        colors = [X_COLOR, Y_COLOR, Z_COLOR][:dim]
        self.input_vect_mob = Matrix(np.array(["x", "y", "z"]))
        self.input_vect_mob.elements.set_color_by_gradient(*colors)

        if output_vect is None:
            output_vect = np.random.randint(self.min_int, self.max_int, size=(dim, 1))
        self.output_vect_mob = IntegerMatrix(output_vect)
        self.output_vect_mob.elements.set_color(OUTPUT_COLOR)

        for mob in self.matrix_mobject, self.input_vect_mob, self.output_vect_mob:
            mob.scale_to_fit_height(self.height)

        self.add(
            self.matrix_mobject,
            self.input_vect_mob,
            self.equals,
            self.output_vect_mob,
        )
        self.arrange_submobjects(RIGHT, buff=SMALL_BUFF)


# Scenes


class LeaveItToComputers(TeacherStudentsScene):
    CONFIG = {
        "random_seed": 1,
    }

    def construct(self):
        system = LinearSystem(height=3)
        system.next_to(self.pi_creatures, UP)
        system.generate_target()
        system.target.scale(0.5)
        system.target.to_corner(UL)

        self.play(
            Write(system),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes("pondering", "thinking", "hooray")
        )
        self.wait(2)
        self.play(
            PiCreatureSays(
                self.teacher, "Let the computer \\\\ handle it",
                target_mode="shruggie",
            ),
            MoveToTarget(system, rate_func=running_start),
            self.get_student_changes(*["confused"] * 3)
        )
        self.wait(3)



































































