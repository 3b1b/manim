from big_ol_pile_of_manim_imports import *


X_COLOR = GREEN
Y_COLOR = RED
Z_COLOR = BLUE
OUTPUT_COLOR = MAROON_B
INPUT_COLOR = YELLOW


def get_cramer_matrix(matrix, output_vect, index=0):
    """
    The inputs matrix and output_vect should be Matrix mobjects
    """
    new_matrix = np.array(matrix.mob_matrix)
    new_matrix[:, index] = output_vect.mob_matrix[:, 0]
    # Create a new Matrix mobject with copies of these entries
    result = Matrix(new_matrix, element_to_mobject=lambda m: m.copy())
    result.match_height(matrix)
    return result


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
        if matrix is None:
            dim = self.dimensions
            matrix = np.random.randint(
                self.min_int,
                self.max_int,
                size=(dim, dim)
            )
        else:
            dim = len(matrix)
        self.matrix_mobject = IntegerMatrix(matrix)
        self.equals = TexMobject("=")
        self.equals.scale(1.5)

        colors = [X_COLOR, Y_COLOR, Z_COLOR][:dim]
        chars = ["x", "y", "z"][:dim]
        self.input_vect_mob = Matrix(np.array(chars))
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

        cramer_groups = VGroup()
        for i in range(3):
            numer_matrix = get_cramer_matrix(
                system.matrix_mobject, system.output_vect_mob,
                index=i
            )
            numer = VGroup(
                get_det_text(numer_matrix, initial_scale_factor=4),
                numer_matrix
            )
            numer.to_corner(UP)
            denom_matrix_mobject = system.matrix_mobject.copy()
            denom = VGroup(
                get_det_text(denom_matrix_mobject, initial_scale_factor=4),
                denom_matrix_mobject,
            )
            rhs = VGroup(numer, Line(LEFT, RIGHT).match_width(numer), denom)
            rhs.arrange_submobjects(DOWN)
            rhs.scale_to_fit_height(2.25)
            rhs.move_to(self.hold_up_spot, DOWN)
            equals = TexMobject("=").next_to(rhs, LEFT)
            variable = system.input_vect_mob.elements[i].copy()
            variable.next_to(equals, LEFT)
            cramer_group = VGroup(variable, equals, rhs)
            cramer_group.variable = variable
            cramer_group.equals = equals
            cramer_group.rhs = rhs
            cramer_groups.add(cramer_group)

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
            MoveToTarget(system, path_arc=90 * DEGREES),
            self.get_student_changes(*["confused"] * 3)
        )
        self.wait(3)

        cg = cramer_groups[0]
        scale_factor = 1.5
        cg.scale(scale_factor, about_edge=DOWN)
        numer, line, denom = cg.rhs
        x_copy = system.input_vect_mob.elements[0].copy()
        self.play(
            RemovePiCreatureBubble(self.teacher, target_mode="raise_right_hand"),
            ShowCreation(line),
            ReplacementTransform(
                system.matrix_mobject.copy(),
                denom[1],
            ),
            Write(denom[0]),
            FadeIn(cg.equals),
            ReplacementTransform(x_copy, cg.variable),
        )
        denom_mover = denom.deepcopy()
        denom_mover.target = numer.deepcopy()
        column1 = VGroup(*denom_mover.target[1].mob_matrix[:, 0])
        column1.set_fill(opacity=0)
        self.play(MoveToTarget(denom_mover))
        self.look_at(system)
        self.play(
            ReplacementTransform(
                system.output_vect_mob.elements.copy(),
                VGroup(*numer[1].mob_matrix[:, 0]),
                path_arc=180 * DEGREES
            ),
            self.teacher.change, "happy",
        )
        self.remove(denom_mover)
        self.add(cg)
        self.change_all_student_modes("sassy")
        self.wait(2)
        self.play(
            cramer_groups[0].scale, 1 / scale_factor,
            cramer_groups[0].next_to, cramer_groups[1], LEFT, MED_LARGE_BUFF,
            FadeIn(cramer_groups[1]),
            FadeOut(system),
            self.get_student_changes(*3 * ["horrified"], look_at_arg=UP),
        )
        self.wait()
        self.play(
            FadeIn(cramer_groups[2]),
            cramer_groups[:2].next_to, cramer_groups[2], LEFT, MED_LARGE_BUFF,
            self.get_student_changes(*3 * ["horrified"], look_at_arg=UP),
        )
        self.wait()

        brace = Brace(cramer_groups, UP)
        rule_text = brace.get_text("``Cramer's rule''")

        self.play(
            GrowFromCenter(brace),
            Write(rule_text),
            self.get_student_changes(
                "pondering", "erm", "maybe",
                look_at_arg=brace,
            )
        )
        self.wait(3)


class PrerequisiteKnowledge(TeacherStudentsScene):
    CONFIG = {
        "camera_config": {"background_alpha": 255}
    }

    def construct(self):
        self.remove(*self.pi_creatures)
        randy = self.students[1]
        self.add(randy)

        title = TextMobject("Prerequisites")
        title.to_edge(UP)

        h_line = Line(LEFT, RIGHT).scale(5)
        h_line.next_to(title, DOWN)

        images = Group(*[
            ImageMobject("eola%d_thumbnail" % d)
            for d in [5, 6, 7]
        ])
        images.arrange_submobjects(RIGHT, buff=LARGE_BUFF)
        images.next_to(h_line, DOWN, MED_LARGE_BUFF)
        for image in images:
            rect = SurroundingRectangle(image, color=BLUE)
            image.rect = rect

        self.add(title)
        self.play(
            ShowCreation(h_line),
            randy.change, "erm"
        )
        self.wait()
        for image in images:
            self.play(
                FadeInFromDown(image),
                FadeInFromDown(image.rect),
                randy.change, "pondering"
            )
            self.wait()


class NotTheMostComputationallyEfficient(Scene):
    def construct(self):
        big_rect = FullScreenFadeRectangle(opacity=0.5)
        self.add(big_rect)

        words = TextMobject("Not the most \\\\ computationally \\\\ efficient")
        words.set_color(RED)
        words.set_stroke(WHITE, 1)
        words.scale_to_fit_height(4)
        self.play(Write(words))
        self.wait()


class SetupSimpleSystemOfEquations(LinearTransformationScene):
    CONFIG = {
        "matrix": [[3, 2], [-1, 2]],
        "output_vect": [-5, -1],
    }

    def construct(self):
        self.remove_grid()
        self.introduce_system()
        self.from_system_to_matrix()
        self.show_geometry()

    def remove_grid(self):
        self.clear()

    def introduce_system(self):
        system = self.system = self.get_system(self.matrix, self.output_vect)
        big_dim = 7  # Big system size
        big_matrix = np.random.randint(-9, 10, size=(big_dim, big_dim))
        big_output_vect = np.random.randint(-9, 10, size=big_dim)
        big_matrix[:2, :2] = self.matrix
        big_output_vect[:2] = self.output_vect
        big_system = self.get_system(big_matrix, big_output_vect)

        unknown_circles = VGroup(*[
            Circle(color=YELLOW).replace(term).scale(1.5)
            for term in system.unknowns
        ])
        unknown_circles.set_stroke(YELLOW, 2)
        for circle in unknown_circles:
            circle.save_state()
            circle.scale(5)
            circle.fade(1)
        row_rects = VGroup(*map(SurroundingRectangle, system))
        row_rects.set_stroke(BLUE, 2)

        self.add(system)
        self.wait()
        self.play(LaggedStart(
            ApplyMethod, unknown_circles,
            lambda m: (m.restore,),
            lag_ratio=0.7
        ))
        self.play(FadeOut(unknown_circles))
        self.play(LaggedStart(ShowCreation, row_rects, run_time=1, lag_ratio=0.8))
        self.play(FadeOut(row_rects))
        self.wait()
        self.remove(system)
        self.play(ReplacementTransform(system.copy(), big_system))
        self.wait(2)
        # Oh yeah, super readable line...
        self.play(*[
            ReplacementTransform(big_system[i][:5], system[i][:5])
            for i in range(2)
        ] + [
            ReplacementTransform(big_system[i][-2:], system[i][-2:])
            for i in range(2)
        ] + [
            FadeOut(big_system[i][start:end])
            for i in range(big_dim)
            for start in [5 if i < 2 else 0]
            for end in [-2 if i < 2 else len(big_system[i])]
        ])
        self.remove(big_system, system)
        self.add(system)

    def from_system_to_matrix(self):
        system_in_lines = self.system
        matrix_system = self.matrix_system = LinearSystem(
            self.matrix, self.output_vect, height=2
        )
        matrix_system.center()

        corner_rect = self.corner_rect = SurroundingRectangle(
            matrix_system, buff=MED_SMALL_BUFF
        )
        corner_rect.set_stroke(width=0)
        corner_rect.set_fill(BLACK, opacity=0.8)
        corner_rect.scale_to_fit_height(2)
        corner_rect.to_corner(UL, buff=0)

        self.play(system_in_lines.to_edge, UP)
        system_in_lines_copy = system_in_lines.deepcopy()
        self.play(
            ReplacementTransform(
                system_in_lines_copy.matrix_elements,
                matrix_system.matrix_mobject.elements,
            ),
            ReplacementTransform(
                system_in_lines_copy.output_vect_elements,
                matrix_system.output_vect_mob.elements,
            ),
            ReplacementTransform(
                system_in_lines_copy.unknowns[:2],
                matrix_system.input_vect_mob.elements,
            ),
            Write(matrix_system.matrix_mobject.brackets),
            Write(matrix_system.output_vect_mob.brackets),
            Write(matrix_system.input_vect_mob.brackets),
            Write(matrix_system.equals)
        )
        self.wait()
        self.play(
            Write(self.background_plane),
            Write(self.plane),
            FadeOut(system_in_lines),
            FadeIn(corner_rect),
            matrix_system.scale_to_fit_height, corner_rect.get_height() - MED_LARGE_BUFF,
            matrix_system.move_to, corner_rect,
        )
        self.play(*map(GrowArrow, self.basis_vectors))

        self.add_foreground_mobject(corner_rect)
        self.add_foreground_mobject(matrix_system)

    def show_geometry(self):
        system = self.matrix_system
        matrix_mobject = system.matrix_mobject
        columns = VGroup(*[
            VGroup(*matrix_mobject.mob_matrix[:, i])
            for i in 0, 1
        ])

        matrix = np.array(self.matrix)
        first_half_matrix = np.identity(matrix.shape[0])
        first_half_matrix[:, 0] = matrix[:, 0]
        second_half_matrix = np.dot(
            matrix,
            np.linalg.inv(first_half_matrix),
        )

        scale_factor = 0.75

        column_mobs = VGroup()
        for i in 0, 1:
            column_mob = IntegerMatrix(matrix[:, i])
            column_mob.elements.set_color([X_COLOR, Y_COLOR][i])
            column_mob.scale(scale_factor)
            column_mob.next_to(self.plane.coords_to_point(*matrix[:, i]), RIGHT)
            column_mob.add_to_back(BackgroundRectangle(column_mob))
            column_mobs.add(column_mob)

        output_vect_mob = self.get_vector(self.output_vect, color=OUTPUT_COLOR)
        output_vect_label = system.output_vect_mob.deepcopy()
        output_vect_label.add_to_back(BackgroundRectangle(output_vect_label))
        output_vect_label.generate_target()
        output_vect_label.target.scale(scale_factor)
        output_vect_label.target.next_to(output_vect_mob.get_end(), LEFT, SMALL_BUFF)

        input_vect = np.dot(np.linalg.inv(self.matrix), self.output_vect)
        input_vect_mob = self.get_vector(input_vect, color=INPUT_COLOR)
        q_marks = TexMobject("????")
        q_marks.set_color_by_gradient(INPUT_COLOR, OUTPUT_COLOR)
        q_marks.next_to(input_vect_mob.get_end(), DOWN, SMALL_BUFF)
        q_marks_rect = SurroundingRectangle(q_marks, color=WHITE)

        # Show output vector
        self.play(
            GrowArrow(output_vect_mob),
            MoveToTarget(output_vect_label),
        )
        self.add_foreground_mobjects(output_vect_mob, output_vect_label)
        self.wait()

        # Show columns
        for column, color in zip(columns, [X_COLOR, Y_COLOR]):
            rect = SurroundingRectangle(column, color=WHITE)
            self.play(
                column.set_color, color,
                system.input_vect_mob.elements.set_color, WHITE,
                ShowPassingFlash(rect),
            )
        matrices = [first_half_matrix, second_half_matrix]
        for column, column_mob, m in zip(columns, column_mobs, matrices):
            column_mob.save_state()
            column_mob[0].scale(0).move_to(matrix_mobject)
            Transform(column_mob.elements, column).update(1)
            Transform(column_mob.brackets, matrix_mobject.brackets).update(1)
            self.add_foreground_mobject(column_mob)
            self.apply_matrix(m, added_anims=[
                ApplyMethod(column_mob.restore, path_arc=90 * DEGREES)
            ])
        self.wait()

        # Do inverse transformation to reveal input
        self.remove_foreground_mobjects(column_mobs)
        self.apply_inverse(self.matrix, run_time=1, added_anims=[
            ReplacementTransform(output_vect_mob.copy(), input_vect_mob),
            ReplacementTransform(output_vect_label.elements.copy(), q_marks),
            FadeOut(column_mobs)
        ])
        self.play(ShowPassingFlash(q_marks_rect))
        self.wait(2)
        self.apply_matrix(self.matrix, added_anims=[
            FadeOut(q_marks),
            ReplacementTransform(input_vect_mob, output_vect_mob),
            FadeIn(column_mobs),
        ])

    # Helpers

    def get_system(self, matrix, output_vect):
        if len(matrix) <= 3:
            chars = "xyzwv"
        else:
            chars = ["x_%d" % d for d in range(len(matrix))]
        colors = [
            color
            for i, color in zip(
                range(len(matrix)),
                it.cycle([X_COLOR, Y_COLOR, Z_COLOR, YELLOW, MAROON_B, TEAL])
            )
        ]
        system = VGroup()
        system.matrix_elements = VGroup()
        system.output_vect_elements = VGroup()
        system.unknowns = VGroup()
        for row, num in zip(matrix, output_vect):
            args = []
            for i in range(len(row)):
                if i + 1 == len(row):
                    sign = "="
                elif row[i + 1] < 0:
                    sign = "-"
                else:
                    sign = "+"
                args += [str(abs(row[i])), chars[i], sign]
            args.append(str(num))
            line = TexMobject(*args)
            line.set_color_by_tex_to_color_map(dict([
                (char, color)
                for char, color in zip(chars, colors)
            ]))
            system.add(line)
            system.matrix_elements.add(*line[0:-1:3])
            system.unknowns.add(*line[1:-1:3])
            system.output_vect_elements.add(line[-1])

        system.output_vect_elements.set_color(OUTPUT_COLOR)
        system.arrange_submobjects(
            DOWN,
            buff=0.75,
            index_of_submobject_to_align=-2
        )
        return system
