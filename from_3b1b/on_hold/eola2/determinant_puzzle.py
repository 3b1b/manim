from manimlib.imports import *


class WorkOutNumerically(Scene):
    CONFIG = {
        "M1_COLOR": TEAL,
        "M2_COLOR": PINK,
    }

    def construct(self):
        self.add_question()
        self.add_example()
        self.compute_rhs()
        self.compute_lhs()

    def add_question(self):
        equation = self.original_equation = TexMobject(
            "\\det(", "M_1", "M_2", ")", "=",
            "\\det(", "M_1", ")",
            "\\det(", "M_2", ")",
        )
        equation.set_color_by_tex_to_color_map({
            "M_1": self.M1_COLOR,
            "M_2": self.M2_COLOR,
        })
        challenge = TextMobject("Explain in one sentence")
        challenge.set_color(YELLOW)
        group = VGroup(challenge, equation)
        group.arrange(DOWN)
        group.to_edge(UP)

        self.add(equation)
        self.play(Write(challenge))
        self.wait()

    def add_example(self):
        M1 = self.M1 = Matrix([[2, -1], [1, 1]])
        M1.set_color(self.M1_COLOR)
        self.M1_copy = M1.copy()
        M2 = self.M2 = Matrix([[-1, 4], [1, 1]])
        M2.set_color(self.M2_COLOR)
        self.M2_copy = M2.copy()
        eq_parts = TexMobject(
            "\\det", "\\big(", "\\big)", "=",
            "\\det", "\\big(", "\\big)",
            "\\det", "\\big(", "\\big)",
        )
        for part in eq_parts.get_parts_by_tex("\\big"):
            part.scale(2)
            part.stretch(1.5, 1)
        i1, i2, i3 = [
            eq_parts.index_of_part(part) + 1
            for part in eq_parts.get_parts_by_tex("\\big(")
        ]
        equation = self.equation_with_numbers = VGroup(*it.chain(
            eq_parts[:i1], [M1, M2],
            eq_parts[i1:i2], [self.M1_copy],
            eq_parts[i2:i3], [self.M2_copy],
            eq_parts[i3:],
        ))
        equation.arrange(RIGHT, buff=SMALL_BUFF)
        eq_parts.get_part_by_tex("=").shift(0.2 * SMALL_BUFF * DOWN)
        equation.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        equation.next_to(self.original_equation, DOWN, MED_LARGE_BUFF)

        self.play(LaggedStartMap(FadeIn, equation))

    def compute_rhs(self):
        M1, M2 = self.M1_copy, self.M2_copy

        line1 = VGroup(
            TexMobject(
                "\\big(", "2", "\\cdot", "2", "-",
                "(-1)", "\\cdot", "1", "\\big)"
            ),
            TexMobject(
                "\\big(", "-1", "\\cdot", "1", "-",
                "4", "\\cdot", "1", "\\big)"
            ),
        )
        line1.arrange(RIGHT, buff=SMALL_BUFF)
        line1[0].set_color(self.M1_COLOR)
        line1[1].set_color(self.M2_COLOR)
        indices = [1, 3, 5, 7]

        line2 = TexMobject("(3)", "(-5)")
        line2.match_style(line1)
        line3 = TexMobject("-15")
        arrows = [TexMobject("\\downarrow") for x in range(2)]
        lines = VGroup(line1, arrows[0], line2, arrows[1], line3)
        lines.arrange(DOWN, buff=MED_SMALL_BUFF)
        lines.next_to(self.equation_with_numbers, DOWN, buff=MED_LARGE_BUFF)
        lines.to_edge(RIGHT)

        for matrix, det in zip([M1, M2], line1):
            numbers = VGroup(*[det[i] for i in indices])
            numbers_iter = iter(numbers)
            non_numbers = VGroup(*[m for m in det if m not in numbers])
            matrix_numbers = VGroup(*[
                matrix.mob_matrix[i][j].copy()
                for i, j in ((0, 0), (1, 1), (0, 1), (1, 0))
            ])
            self.play(
                LaggedStartMap(FadeIn, non_numbers, run_time=1),
                LaggedStartMap(
                    ReplacementTransform,
                    matrix_numbers,
                    lambda m: (m, next(numbers_iter)),
                    path_arc=TAU / 6
                ),
            )
        self.play(LaggedStartMap(FadeIn, lines[1:], run_time=3))

    def compute_lhs(self):
        matrix = Matrix([[-3, 7], [0, 5]])
        matrix.set_color(BLUE)
        matrix.scale(0.8)
        empty_det_tex = TexMobject("\\det", "\\big(", "\\big)")
        empty_det_tex[1:].scale(1.5)
        empty_det_tex[1:].match_height(matrix, stretch=True)
        det_tex = VGroup(empty_det_tex[:2], matrix, *empty_det_tex[2:])
        det_tex.arrange(RIGHT, buff=SMALL_BUFF)

        group = VGroup(
            det_tex,
            TexMobject("\\downarrow"),
            TexMobject("(-3)(5) - (7)(0)").scale(0.8),
            TexMobject("\\downarrow"),
            TexMobject("-15"),
        )
        group.arrange(DOWN, buff=2 * SMALL_BUFF)
        # group.set_height(0.4*FRAME_HEIGHT)
        group.next_to(self.equation_with_numbers, DOWN)
        group.shift(FRAME_WIDTH * LEFT / 4)

        self.play(FadeIn(empty_det_tex))
        self.play(*[
            ReplacementTransform(M.copy(), matrix)
            for M in (self.M1, self.M2)
        ])
        self.play(LaggedStartMap(FadeIn, group[1:]))
        self.wait()


class LetsGoInOneSentence(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Here we go, \\\\", "one sentence!"
        )
        self.change_all_student_modes("hooray")
        self.teacher_says(
            "Or three...", "",
            target_mode="guilty"
        )
        self.change_all_student_modes("sassy")
        self.wait(4)


class SuccessiveLinearTransformations(LinearTransformationScene):
    CONFIG = {
        "matrix_2": [[3, -1], [0, 1]],
        "matrix_1": [[2, 3], [-1. / 3, 2]],
    }

    def construct(self):
        self.create_product_and_inverse()
        self.scale_area_successively()
        self.apply_transformations_successively()
        self.scale_area_successively(
            "\\det(M_2)", "\\det(M_1)", "\\det(M_1 M_2)",
            reset=False
        )
        # self.show_det_as_scaling_factor()

    def create_product_and_inverse(self):
        self.matrix_product = np.dot(self.matrix_1, self.matrix_2)
        self.matrix_product_inverse = np.linalg.inv(self.matrix_product)

    def scale_area_successively(self, tex2="3", tex1="5", tex_prod="15", reset=True):
        self.add_unit_square()
        t1 = "$%s \\, \\cdot $" % tex1
        t2 = "$%s \\, \\cdot $" % tex2
        t3 = "Area"
        areas = VGroup(
            TextMobject("", "", t3),
            TextMobject("", t2, t3),
            TextMobject(t1, t2, t3),
        )
        areas.scale(0.8)
        areas.move_to(self.square)
        area = areas[0]
        self.add_moving_mobject(area, areas[1])

        self.play(
            FadeIn(self.square),
            Write(area),
            Animation(self.basis_vectors)
        )
        self.apply_matrix(self.matrix_2)
        self.wait()
        self.add_moving_mobject(area, areas[2])
        self.apply_matrix(self.matrix_1)
        self.wait()

        product = VGroup(area[:2])
        brace = Brace(product, DOWN, buff=SMALL_BUFF)
        brace_tex = brace.get_tex(tex_prod, buff=SMALL_BUFF)
        brace_tex.scale(0.8, about_edge=UP)

        self.play(
            GrowFromCenter(brace),
            Write(brace_tex)
        )
        self.wait()
        if reset:
            self.play(
                FadeOut(VGroup(self.square, area, brace, brace_tex)),
                Animation(self.plane),
                Animation(self.basis_vectors)
            )
            self.transformable_mobjects.remove(self.square)
            self.moving_mobjects = []
            self.reset_plane()
        self.wait()

    def apply_transformations_successively(self):
        M1, M2, all_space = expression = TexMobject(
            "M_1", "M_2", "\\text{(All 2d space)}"
        )
        expression.set_color_by_tex_to_color_map({
            "M_1": TEAL,
            "M_2": PINK,
        })
        expression.shift(FRAME_WIDTH * LEFT / 4)
        expression.to_edge(UP)
        for part in expression:
            part.add_background_rectangle()
            part.background_rectangle.stretch(1.05, 0)
        M1.save_state()
        M1.move_to(ORIGIN)
        M1.fade(1)

        # Apply one after the other
        self.play(
            FocusOn(M2, run_time=1),
            FadeIn(VGroup(M2, all_space))
        )
        self.add_foreground_mobjects(M2, all_space)
        self.apply_matrix(self.matrix_2)
        self.wait()
        self.play(M1.restore)
        self.add_foreground_mobjects(M1)
        self.apply_matrix(self.matrix_1)
        self.wait()

        # Show full composition
        rp, lp = parens = TexMobject("()")
        matrices = VGroup(M1, M2)
        matrices.generate_target()
        parens.match_height(matrices)
        lp.move_to(matrices, RIGHT)
        matrices.target.next_to(lp, LEFT, SMALL_BUFF)
        rp.next_to(matrices.target, LEFT, SMALL_BUFF)

        self.reset_plane()
        self.play(
            MoveToTarget(matrices),
            *list(map(GrowFromCenter, parens))
        )
        self.apply_matrix(self.matrix_product)
        self.wait()
        self.reset_plane()

    def show_det_as_scaling_factor(self):
        pass

    ###

    def reset_plane(self):
        plane_and_bases = VGroup(self.plane, self.basis_vectors)
        self.play(FadeOut(plane_and_bases))
        self.apply_matrix(self.matrix_product_inverse, run_time=0)
        self.play(FadeIn(plane_and_bases))
