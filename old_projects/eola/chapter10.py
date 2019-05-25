from manimlib.imports import *
from old_projects.eola.chapter1 import plane_wave_homotopy
from old_projects.eola.chapter3 import ColumnsToBasisVectors
from old_projects.eola.chapter5 import get_det_text
from old_projects.eola.chapter9 import get_small_bubble


class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "``Last time, I asked: `What does",
            "mathematics", 
            """ mean to you?', and some people answered: `The 
            manipulation of numbers, the manipulation of structures.' 
            And if I had asked what""",
            "music",
            """means to you, would you have answered: `The 
            manipulation of notes?' '' """, 
            enforce_new_line_structure = False,
            alignment = "",
        )
        words.set_color_by_tex("mathematics", BLUE)
        words.set_color_by_tex("music", BLUE)
        words.set_width(FRAME_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Serge Lang")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(Write(words, run_time = 10))
        self.wait()
        self.play(FadeIn(author))
        self.wait(3)

class StudentsFindThisConfusing(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Eigenvectors and Eigenvalues")
        title.to_edge(UP)
        students = self.get_students()

        self.play(
            Write(title), 
            *[
                ApplyMethod(pi.look_at, title)
                for pi in self.get_pi_creatures()
            ]
        )
        self.play(
            self.get_teacher().look_at, students[-1].eyes,
            students[0].change_mode, "confused",
            students[1].change_mode, "tired",
            students[2].change_mode, "sassy",
        )
        self.random_blink()
        self.student_says(
            "Why are we doing this?",
            student_index = 0,
            run_time = 2,
        )
        question1 = students[0].bubble.content.copy()
        self.student_says(
            "What does this actually mean?",
            student_index = 2,
            added_anims = [
                question1.scale_in_place, 0.8,
                question1.to_edge, LEFT,
                question1.shift, DOWN,
            ]
        )
        question2 = students[2].bubble.content.copy()
        question2.target = question2.copy()
        question2.target.next_to(
            question1, DOWN, 
            aligned_edge = LEFT, 
            buff = MED_SMALL_BUFF
        )
        equation = TexMobject(
            "\\det\\left( %s \\right)=0"%matrix_to_tex_string([
                ["a-\\lambda", "b"],
                ["c", "d-\\lambda"],
            ])
        )
        equation.set_color(YELLOW)
        self.teacher_says(
            equation,
            added_anims = [MoveToTarget(question2)]
        )
        self.change_student_modes(*["confused"]*3)
        self.random_blink(3)

class ShowComments(Scene):
    pass #TODO

class EigenThingsArentAllThatBad(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Eigen-things aren't \\\\ actually so bad",
            target_mode = "hooray"
        )
        self.change_student_modes(
            "pondering", "pondering", "erm"
        )
        self.random_blink(4)

class ManyPrerequisites(Scene):
    def construct(self):
        title = TextMobject("Many prerequisites")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(h_line))

        rect = Rectangle(height = 9, width = 16, color = BLUE)
        rect.set_width(FRAME_X_RADIUS-2)
        rects = [rect]+[rect.copy() for i in range(3)]
        words = [
            "Linear transformations",
            "Determinants",
            "Linear systems",
            "Change of basis",
        ]
        for rect, word in zip(rects, words):
            word_mob = TextMobject(word)
            word_mob.next_to(rect, UP, buff = MED_SMALL_BUFF)
            rect.add(word_mob)

        Matrix(np.array(rects).reshape((2, 2)))
        rects = VGroup(*rects)
        rects.set_height(FRAME_HEIGHT - 1.5)
        rects.next_to(h_line, DOWN, buff = MED_SMALL_BUFF)

        self.play(Write(rects[0]))
        self.wait()
        self.play(*list(map(FadeIn, rects[1:])))
        self.wait()

class ExampleTranformationScene(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[3, 0], [1, 2]]
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        self.add_matrix()

    def add_matrix(self):
        matrix = Matrix(self.t_matrix.T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(ORIGIN, LEFT, buff = MED_SMALL_BUFF)
        matrix.to_edge(UP)
        matrix.rect = BackgroundRectangle(matrix)
        matrix.add_to_back(matrix.rect)
        self.add_foreground_mobject(matrix)
        self.matrix = matrix

    def remove_matrix(self):
        self.remove(self.matrix)
        self.foreground_mobjects.remove(self.matrix)

class IntroduceExampleTransformation(ExampleTranformationScene):
    def construct(self):
        self.remove_matrix()
        i_coords = Matrix(self.t_matrix[0])
        j_coords = Matrix(self.t_matrix[1])

        self.apply_transposed_matrix(self.t_matrix)
        for coords, vect in (i_coords, self.i_hat), (j_coords, self.j_hat):
            coords.set_color(vect.get_color())
            coords.scale(0.8)
            coords.rect = BackgroundRectangle(coords)
            coords.add_to_back(coords.rect)
            coords.next_to(vect.get_end(), RIGHT)
            self.play(Write(coords))
            self.wait()
        i_coords_copy = i_coords.copy()
        self.play(*[
            Transform(*pair)
            for pair in [
                (i_coords_copy.rect, self.matrix.rect),            
                (i_coords_copy.get_brackets(), self.matrix.get_brackets()),
                (
                    i_coords_copy.get_entries(), 
                    VGroup(*self.matrix.get_mob_matrix()[:,0])
                )
            ]
        ])
        to_remove = self.get_mobjects_from_last_animation()
        self.play(Transform(
            j_coords.copy().get_entries(),
            VGroup(*self.matrix.get_mob_matrix()[:,1])
        ))
        to_remove += self.get_mobjects_from_last_animation()
        self.wait()
        self.remove(*to_remove)
        self.add(self.matrix)

class VectorKnockedOffSpan(ExampleTranformationScene):
    def construct(self):
        vector = Vector([2, 1])
        line = Line(vector.get_end()*-4, vector.get_end()*4, color = MAROON_B)
        vector.scale(0.7)
        top_words, off, span_label = all_words = TextMobject(
            "\\centering Vector gets knocked", "\\\\ off", "Span"
        )
        all_words.shift(
            line.point_from_proportion(0.75) - \
            span_label.get_corner(DOWN+RIGHT) + \
            MED_SMALL_BUFF*LEFT
        )
        for text in all_words:
            text.add_to_back(BackgroundRectangle(text))

        self.add_vector(vector)
        self.wait()
        self.play(
            ShowCreation(line),
            Write(span_label),
            Animation(vector),
        )
        self.add_foreground_mobject(span_label)
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.play(Animation(span_label.copy()), Write(all_words))
        self.wait()

class VectorRemainsOnSpan(ExampleTranformationScene):
    def construct(self):
        vector = Vector([1, -1])
        v_end = vector.get_end()
        line = Line(-4*v_end, 4*v_end, color = MAROON_B)
        words = TextMobject("Vector remains on", "\\\\its own span")
        words.next_to(ORIGIN, DOWN+LEFT)
        for part in words:
            part.add_to_back(BackgroundRectangle(part))

        self.add_vector(vector)
        self.play(ShowCreation(line), Animation(vector))
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.play(Write(words))
        self.wait()
        target_vectors = [
            vector.copy().scale(scalar)
            for scalar in (2, -2, 1)
        ]
        for target, time in zip(target_vectors, [1, 2, 2]):
            self.play(Transform(vector, target, run_time = time))
        self.wait()

class IHatAsEigenVector(ExampleTranformationScene):
    def construct(self):
        self.set_color_first_column()
        self.set_color_x_axis()        
        self.apply_transposed_matrix(self.t_matrix, path_arc = 0)
        self.label_i_hat_landing_spot()

    def set_color_first_column(self):
        faders = VGroup(self.plane, self.i_hat, self.j_hat)
        faders.save_state()
        column1 = VGroup(*self.matrix.get_mob_matrix()[:,0])

        self.play(faders.fade, 0.7, Animation(self.matrix))
        self.play(column1.scale_in_place, 1.3, rate_func = there_and_back)
        self.wait()
        self.play(faders.restore, Animation(self.matrix))
        self.wait()

    def set_color_x_axis(self):
        x_axis = self.plane.axes[0]
        targets = [
            self.i_hat.copy().scale(val)
            for val in (-FRAME_X_RADIUS, FRAME_X_RADIUS, 1)
        ]
        lines = [
            Line(v1.get_end(), v2.get_end(), color = YELLOW)
            for v1, v2 in adjacent_pairs([self.i_hat]+targets)
        ]
        for target, line in zip(targets, lines):
            self.play(
                ShowCreation(line),                
                Transform(self.i_hat, target),
            )
        self.wait()
        self.remove(*lines)
        x_axis.set_color(YELLOW)

    def label_i_hat_landing_spot(self):
        array = Matrix(self.t_matrix[0])
        array.set_color(X_COLOR)
        array.rect = BackgroundRectangle(array)
        array.add_to_back(array.rect)
        brace = Brace(self.i_hat, buff = 0)
        brace.put_at_tip(array)

        self.play(GrowFromCenter(brace))
        matrix = self.matrix.copy()
        self.play(
            Transform(matrix.rect, array.rect),
            Transform(matrix.get_brackets(), array.get_brackets()),
            Transform(
                VGroup(*matrix.get_mob_matrix()[:,0]), 
                array.get_entries()
            ),
        )
        self.wait()

class AllXAxisVectorsAreEigenvectors(ExampleTranformationScene):
    def construct(self):
        vectors = VGroup(*[
            self.add_vector(u*x*RIGHT, animate = False)
            for x in reversed(list(range(1, int(FRAME_X_RADIUS)+1)))
            for u in [-1, 1]
        ])
        vectors.set_color_by_gradient(YELLOW, X_COLOR)
        self.play(ShowCreation(vectors))
        self.wait()
        self.apply_transposed_matrix(self.t_matrix, path_arc = 0)
        self.wait()

class SneakierEigenVector(ExampleTranformationScene):
    def construct(self):
        coords = [-1, 1]
        vector = Vector(coords)
        array = Matrix(coords)
        array.scale(0.7)
        array.set_color(vector.get_color())
        array.add_to_back(BackgroundRectangle(array))        
        array.target = array.copy()
        array.next_to(vector.get_end(), LEFT)
        array.target.next_to(2*vector.get_end(), LEFT)
        two_times = TexMobject("2 \\cdot")
        two_times.add_background_rectangle()
        two_times.next_to(array.target, LEFT)
        span_line = Line(-4*vector.get_end(), 4*vector.get_end())
        span_line.set_color(MAROON_B)

        self.matrix.shift(-2*self.matrix.get_center()[0]*RIGHT)

        self.add_vector(vector)
        self.play(Write(array))
        self.play(
            ShowCreation(span_line), 
            Animation(vector),
            Animation(array),
        )
        self.wait()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [
                MoveToTarget(array),
                Transform(VectorizedPoint(array.get_left()), two_times)
            ],
            path_arc = 0,
        )
        self.wait()

class FullSneakyEigenspace(ExampleTranformationScene):
    def construct(self):
        self.matrix.shift(-2*self.matrix.get_center()[0]*RIGHT)
        vectors = VGroup(*[
            self.add_vector(u*x*(LEFT+UP), animate = False)
            for x in reversed(np.arange(0.5, 5, 0.5))
            for u in [-1, 1]
        ])
        vectors.set_color_by_gradient(MAROON_B, YELLOW)
        words = TextMobject("Stretch by 2")
        words.add_background_rectangle()
        words.next_to(ORIGIN, DOWN+LEFT, buff = MED_SMALL_BUFF)
        words.shift(MED_SMALL_BUFF*LEFT)
        words.rotate(vectors[0].get_angle())
        words.start = words.copy()
        words.start.scale(0.5)
        words.start.set_fill(opacity = 0)

        self.play(ShowCreation(vectors))
        self.wait()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [Transform(words.start, words)],
            path_arc = 0
        )
        self.wait()

class NameEigenvectorsAndEigenvalues(ExampleTranformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.remove(self.matrix)
        self.foreground_mobjects.remove(self.matrix)
        x_vectors = VGroup(*[
            self.add_vector(u*x*RIGHT, animate = False)
            for x in range(int(FRAME_X_RADIUS)+1, 0, -1)
            for u in [-1, 1]
        ])
        x_vectors.set_color_by_gradient(YELLOW, X_COLOR)
        self.remove(x_vectors)
        sneak_vectors = VGroup(*[
            self.add_vector(u*x*(LEFT+UP), animate = False)
            for x in np.arange(int(FRAME_Y_RADIUS), 0, -0.5)
            for u in [-1, 1]
        ])
        sneak_vectors.set_color_by_gradient(MAROON_B, YELLOW)
        self.remove(sneak_vectors)

        x_words = TextMobject("Stretched by 3")
        sneak_words = TextMobject("Stretched by 2")
        for words in x_words, sneak_words:
            words.add_background_rectangle()
            words.next_to(x_vectors, DOWN)
            words.next_to(words.get_center(), LEFT, buff = 1.5)
            eigen_word = TextMobject("Eigenvectors")
            eigen_word.add_background_rectangle()
            eigen_word.replace(words)
            words.target = eigen_word
            eigen_val_words = TextMobject(
                "with eigenvalue ",
                "%s"%words.get_tex_string()[-1]
            )
            eigen_val_words.add_background_rectangle()
            eigen_val_words.next_to(words, DOWN, aligned_edge = RIGHT)
            words.eigen_val_words = eigen_val_words
        x_words.eigen_val_words.set_color(X_COLOR)
        sneak_words.eigen_val_words.set_color(YELLOW)

        VGroup(
            sneak_words,
            sneak_words.target,
            sneak_words.eigen_val_words,
        ).rotate(sneak_vectors[0].get_angle())

        non_eigen = Vector([1, 1], color = PINK)
        non_eigen_span = Line(
            -FRAME_Y_RADIUS*non_eigen.get_end(), 
            FRAME_Y_RADIUS*non_eigen.get_end(), 
            color = RED
        )
        non_eigen_words = TextMobject("""
            Knocked off
            its own span
        """)
        non_eigen_words.add_background_rectangle()
        non_eigen_words.scale(0.7)
        non_eigen_words.next_to(non_eigen.get_end(), RIGHT)
        non_eigen_span.fade()

        for vectors in x_vectors, sneak_vectors:
            self.play(ShowCreation(vectors, run_time = 1))
        self.wait()
        for words in x_words, sneak_words:
            self.play(Write(words, run_time = 1.5))
            self.add_foreground_mobject(words)
            self.wait()
        self.play(ShowCreation(non_eigen))
        self.play(
            ShowCreation(non_eigen_span),
            Write(non_eigen_words),
            Animation(non_eigen)
        )
        self.add_vector(non_eigen, animate = False)
        self.wait()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [FadeOut(non_eigen_words)],
            path_arc = 0,
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [non_eigen, non_eigen_span])))
        self.play(*list(map(MoveToTarget, [x_words, sneak_words])))
        self.wait()
        for words in x_words, sneak_words:
            self.play(Write(words.eigen_val_words), run_time = 2)
            self.wait()

class CanEigenvaluesBeNegative(TeacherStudentsScene):
    def construct(self):
        self.student_says("Can eigenvalues be negative?")
        self.random_blink()
        self.teacher_says("But of course!", target_mode = "hooray")
        self.random_blink()

class EigenvalueNegativeOneHalf(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[0.5, -1], [-1, 0.5]],
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "secondary_line_ratio" : 0
        },
        "include_background_plane" : False
    }
    def construct(self):
        matrix = Matrix(self.t_matrix.T)
        matrix.add_to_back(BackgroundRectangle(matrix))
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(ORIGIN, LEFT)
        matrix.to_edge(UP)
        self.add_foreground_mobject(matrix)

        vector = self.add_vector([1, 1])
        words = TextMobject("Eigenvector with \\\\ eigenvalue $-\\frac{1}{2}$")
        words.add_background_rectangle()
        words.next_to(vector.get_end(), RIGHT)
        span = Line(
            -FRAME_Y_RADIUS*vector.get_end(), 
            FRAME_Y_RADIUS*vector.get_end(),
            color = MAROON_B
        )

        self.play(Write(words))
        self.play(
            ShowCreation(span), 
            Animation(vector),
            Animation(words),
        )
        self.wait()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [FadeOut(words)]
        )
        self.wait()
        self.play(
            Rotate(span, np.pi/12, rate_func = wiggle),
            Animation(vector),
        )
        self.wait()
        
class ThreeDRotationTitle(Scene):
    def construct(self):
        title = TextMobject("3D Rotation")
        title.scale(2)
        self.play(Write(title))
        self.wait()

class ThreeDShowRotation(Scene):
    pass

class ThreeDShowRotationWithEigenvector(Scene):
    pass

class EigenvectorToAxisOfRotation(Scene):
    def construct(self):
        words = [
            TextMobject("Eigenvector"),
            TextMobject("Axis of rotation"),
        ]
        for word in words:
            word.scale(2)
        self.play(Write(words[0]))
        self.wait()
        self.play(Transform(*words))
        self.wait()

class EigenvalueOne(Scene):
    def construct(self):
        text = TextMobject("Eigenvalue = $1$")
        text.set_color(MAROON_B)
        self.play(Write(text))
        self.wait()

class ContrastMatrixUnderstandingWithEigenvalue(TeacherStudentsScene):
    def construct(self):
        axis_and_rotation = TextMobject(
            "Rotate", "$30^\\circ$", "around", 
            "$%s$"%matrix_to_tex_string([2, 3, 1])
        )
        axis_and_rotation[1].set_color(BLUE)
        axis_and_rotation[-1].set_color(MAROON_B)

        matrix = Matrix([
            [
                "\\cos(\\theta)\\cos(\\phi)", 
                "-\\sin(\\phi)",
                "\\cos(\\theta)\\sin(\\phi)",
            ],
            [
                "\\sin(\\theta)\\cos(\\phi)",
                "\\cos(\\theta)",
                "\\sin(\\theta)\\sin(\\phi)",
            ],
            [
                "-\\sin(\\phi)",
                "0",
                "\\cos(\\phi)"
            ]
        ])
        matrix.scale(0.7)
        for mob in axis_and_rotation, matrix:
            mob.to_corner(UP+RIGHT)

        everyone = self.get_pi_creatures()
        self.play(
            Write(axis_and_rotation),
            *it.chain(*list(zip(
                [pi.change_mode for pi in everyone],
                ["hooray"]*4,
                [pi.look_at for pi in everyone],
                [axis_and_rotation]*4,
            ))),
            run_time = 2
        )
        self.random_blink(2)
        self.play(
            Transform(axis_and_rotation, matrix),
            *it.chain(*list(zip(
                [pi.change_mode for pi in everyone],
                ["confused"]*4,
                [pi.look_at for pi in everyone],
                [matrix]*4,
            )))

        )
        self.random_blink(3)

class CommonPattern(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            This is a common pattern 
            in linear algebra.
        """)
        self.random_blink(2)

class DeduceTransformationFromMatrix(ColumnsToBasisVectors):
    def construct(self):
        self.setup()
        self.move_matrix_columns([[3, 0], [1, 2]])
        words = TextMobject("""
            This gives too much weight 
            to our coordinate system
        """)
        words.add_background_rectangle()
        words.next_to(ORIGIN, DOWN+LEFT, buff = MED_SMALL_BUFF)
        words.shift_onto_screen()
        self.play(Write(words))
        self.wait()

class WordsOnComputation(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "I won't cover the full\\\\",
            "details of computation...",
            target_mode = "guilty"
        )
        self.change_student_modes("angry", "sassy", "angry")
        self.random_blink()
        self.teacher_says(
            "...but I'll hit the \\\\",
            "important parts"
        )
        self.change_student_modes(*["happy"]*3)
        self.random_blink(3)

class SymbolicEigenvectors(Scene):
    def construct(self):
        self.introduce_terms()
        self.contrast_multiplication_types()
        self.rewrite_righthand_side()
        self.reveal_as_linear_system()
        self.bring_in_determinant()

    def introduce_terms(self):
        self.expression = TexMobject(
            "A", "\\vec{\\textbf{v}}", "=", 
            "\\lambda", "\\vec{\\textbf{v}}"
        )
        self.expression.scale(1.5)
        self.expression.shift(UP+2*LEFT)
        A, v1, equals, lamb, v2 = self.expression
        vs = VGroup(v1, v2)
        vs.set_color(YELLOW)
        lamb.set_color(MAROON_B)

        A_brace = Brace(A, UP, buff = 0)
        A_text = TextMobject("Transformation \\\\ matrix")
        A_text.next_to(A_brace, UP)

        lamb_brace = Brace(lamb, UP, buff = 0)
        lamb_text = TextMobject("Eigenvalue")
        lamb_text.set_color(lamb.get_color())
        lamb_text.next_to(lamb_brace, UP, aligned_edge = LEFT)

        v_text = TextMobject("Eigenvector")
        v_text.set_color(vs.get_color())
        v_text.next_to(vs, DOWN, buff = 1.5*LARGE_BUFF)
        v_arrows = VGroup(*[
            Arrow(v_text.get_top(), v.get_bottom())
            for v in vs
        ])

        self.play(Write(self.expression))
        self.wait()
        self.play(
            GrowFromCenter(A_brace),
            Write(A_text)
        )
        self.wait()
        self.play(
            Write(v_text),
            ShowCreation(v_arrows)
        )
        self.wait()
        self.play(
            GrowFromCenter(lamb_brace),
            Write(lamb_text)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [
            A_brace, A_text, 
            lamb_brace, lamb_text,
            v_text, v_arrows
        ])))

    def contrast_multiplication_types(self):
        A, v1, equals, lamb, v2 = self.expression

        left_group = VGroup(A, v1)
        left_group.brace = Brace(left_group, UP)
        left_group.text = left_group.brace.get_text("Matrix-vector multiplication")

        right_group = VGroup(lamb, v2)
        right_group.brace = Brace(right_group, DOWN)
        right_group.text = right_group.brace.get_text("Scalar multiplication")
        right_group.text.set_color(lamb.get_color())

        for group in left_group, right_group:
            self.play(
                GrowFromCenter(group.brace),
                Write(group.text, run_time = 2)
            )
            self.play(group.scale_in_place, 1.2, rate_func = there_and_back)
            self.wait()

        morty = Mortimer().to_edge(DOWN)
        morty.change_mode("speaking")
        bubble = morty.get_bubble(SpeechBubble, width = 5, direction = LEFT)
        VGroup(morty, bubble).to_edge(RIGHT)
        solve_text = TextMobject(
            "Solve for \\\\",
            "$\\lambda$", "and", "$\\vec{\\textbf{v}}$"
        )
        solve_text.set_color_by_tex("$\\lambda$", lamb.get_color())
        solve_text.set_color_by_tex("$\\vec{\\textbf{v}}$", v1.get_color())
        bubble.add_content(solve_text)

        self.play(
            FadeIn(morty),
            FadeIn(bubble),
            Write(solve_text)
        )
        self.play(Blink(morty))
        self.wait(2)
        bubble.write("Fix different", "\\\\ multiplication", "types")
        self.play(
            Transform(solve_text, bubble.content),
            morty.change_mode, "sassy"
        )
        self.play(Blink(morty))
        self.wait()
        self.play(*list(map(FadeOut, [
            left_group.brace, left_group.text,
            right_group.brace, right_group.text,
            morty, bubble, solve_text
        ])))

    def rewrite_righthand_side(self):
        A, v1, equals, lamb, v2 = self.expression

        lamb_copy = lamb.copy()
        scaling_by = VGroup(
            TextMobject("Scaling by "), lamb_copy
        )
        scaling_by.arrange()
        arrow = TexMobject("\\Updownarrow")
        matrix_multiplication = TextMobject(
            "Matrix multiplication by"
        )
        matrix = Matrix(np.identity(3, dtype = int))

        corner_group = VGroup(
            scaling_by, arrow, matrix_multiplication, matrix
        )
        corner_group.arrange(DOWN)
        corner_group.to_corner(UP+RIGHT)

        q_marks = VGroup(*[
            TexMobject("?").replace(entry)
            for entry in matrix.get_entries()
        ])
        q_marks.set_color_by_gradient(X_COLOR, Y_COLOR, Z_COLOR)
        diag_entries = VGroup(*[
            matrix.get_mob_matrix()[i,i]
            for i in range(3)
        ])
        diag_entries.save_state()
        for entry in diag_entries:
            new_lamb = TexMobject("\\lambda")
            new_lamb.move_to(entry)
            new_lamb.set_color(lamb.get_color())
            Transform(entry, new_lamb).update(1)
        new_lamb = lamb.copy()
        new_lamb.next_to(matrix, LEFT)
        id_brace = Brace(matrix)
        id_text = TexMobject("I").scale(1.5)
        id_text.next_to(id_brace, DOWN)

        self.play(
            Transform(lamb.copy(), lamb_copy),
            Write(scaling_by)
        )
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(scaling_by)
        self.play(Write(VGroup(
            matrix_multiplication,
            arrow,
            matrix.get_brackets(),
            q_marks,
        ), run_time = 2
        ))
        self.wait()
        self.play(Transform(
            q_marks, matrix.get_entries(), 
            lag_ratio = 0.5,
            run_time = 2
        ))
        self.remove(q_marks)
        self.add(*matrix.get_entries())
        self.wait()
        self.play(
            Transform(diag_entries.copy(), new_lamb),
            diag_entries.restore
        )
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(new_lamb, diag_entries)
        self.play(
            GrowFromCenter(id_brace),
            Write(id_text)
        )
        self.wait()
        id_text_copy = id_text.copy()
        self.add(id_text_copy)

        l_paren, r_paren = parens = TexMobject("()").scale(1.5)
        for mob in lamb, id_text, v2:
            mob.target = mob.copy()
        VGroup(
            l_paren, lamb.target, id_text.target, 
            r_paren, v2.target
        ).arrange().next_to(equals).shift(SMALL_BUFF*UP)
        self.play(
            Write(parens),
            *list(map(MoveToTarget, [lamb, id_text, v2]))
        )
        self.wait()
        self.play(*list(map(FadeOut, [
            corner_group, id_brace, id_text_copy, new_lamb
        ])))
        self.expression = VGroup(
            A, v1, equals, 
            VGroup(l_paren, lamb, id_text, r_paren),
            v2
        )

    def reveal_as_linear_system(self):
        A, v1, equals, lamb_group, v2 = self.expression
        l_paren, lamb, I, r_paren = lamb_group
        zero = TexMobject("\\vec{\\textbf{0}}")
        zero.scale(1.3)
        zero.next_to(equals, RIGHT)
        zero.shift(SMALL_BUFF*UP/2)
        minus = TexMobject("-").scale(1.5)
        movers = A, v1, lamb_group, v2
        for mob in movers:
            mob.target = mob.copy()
        VGroup(
            A.target, v1.target, minus,
            lamb_group.target, v2.target
        ).arrange().next_to(equals, LEFT)
        self.play(
            Write(zero), 
            Write(minus),
            *list(map(MoveToTarget, movers)),
            path_arc = np.pi/3
        )
        self.wait()
        A.target.next_to(minus, LEFT)
        l_paren.target = l_paren.copy()
        l_paren.target.next_to(A.target, LEFT)
        self.play(
            MoveToTarget(A),
            MoveToTarget(l_paren),
            Transform(v1, v2, path_arc = np.pi/3)
        )
        self.remove(v1)
        self.wait()

        brace = Brace(VGroup(l_paren, r_paren))
        brace.text = TextMobject("This matrix looks \\\\ something like")
        brace.text.next_to(brace, DOWN)
        brace.text.to_edge(LEFT)
        matrix = Matrix([
            ["3-\\lambda", "1", "4"],
            ["1", "5-\\lambda", "9"],
            ["2", "6", "5-\\lambda"],
        ])
        matrix.scale(0.7)
        VGroup(
            matrix.get_brackets()[1],
            *matrix.get_mob_matrix()[:,2]
        ).shift(0.5*RIGHT)
        matrix.next_to(brace.text, DOWN)
        for entry in matrix.get_entries():
            if len(entry.get_tex_string()) > 1:
                entry[-1].set_color(lamb.get_color())
        self.play(
            GrowFromCenter(brace),
            Write(brace.text),
            Write(matrix)
        )
        self.wait()

        vect_words = TextMobject(
            "We want a nonzero solution for"
        )
        v_copy = v2.copy().next_to(vect_words)
        vect_words.add(v_copy)
        vect_words.to_corner(UP+LEFT)
        arrow = Arrow(vect_words.get_bottom(), v2.get_top())
        self.play(
            Write(vect_words), 
            ShowCreation(arrow)
        )
        self.wait()

    def bring_in_determinant(self):
        randy = Randolph(mode = "speaking").to_edge(DOWN)
        randy.flip()
        randy.look_at(self.expression)
        bubble = randy.get_bubble(SpeechBubble, direction = LEFT, width = 5)
        words = TextMobject("We need")
        equation = TexMobject(
            "\\det(A-", "\\lambda", "I)", "=0"
        )
        equation.set_color_by_tex("\\lambda", MAROON_B)
        equation.next_to(words, DOWN)
        words.add(equation)
        bubble.add_content(words)

        self.play(
            FadeIn(randy),
            ShowCreation(bubble),
            Write(words)
        )
        self.play(Blink(randy))
        self.wait()
        everything = self.get_mobjects()
        equation_copy = equation.copy()
        self.play(
            FadeOut(VGroup(*everything)),
            Animation(equation_copy)
        )
        self.play(
            equation_copy.center,
            equation_copy.scale, 1.5
        )
        self.wait()

class NonZeroSolutionsVisually(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[1, 1], [2, 2]],
        "v_coords" : [2, -1]
    }
    def construct(self):
        equation = TexMobject(
            "(A-", "\\lambda", "I)", "\\vec{\\textbf{v}}",
            "= \\vec{\\textbf{0}}"
        )
        equation_matrix = VGroup(*equation[:3])
        equation.set_color_by_tex("\\lambda", MAROON_B)
        equation.set_color_by_tex("\\vec{\\textbf{v}}", YELLOW)
        equation.add_background_rectangle()
        equation.next_to(ORIGIN, DOWN, buff = MED_SMALL_BUFF)
        equation.to_edge(LEFT)

        det_equation = TexMobject(
            "\\text{Squishification} \\Rightarrow",
            "\\det", "(A-", "\\lambda", "I", ")", "=0"
        )
        det_equation_matrix = VGroup(*det_equation[2:2+4])
        det_equation.set_color_by_tex("\\lambda", MAROON_B)
        det_equation.next_to(equation, DOWN, buff = MED_SMALL_BUFF)
        det_equation.to_edge(LEFT)
        det_equation.add_background_rectangle()


        self.add_foreground_mobject(equation)
        v = self.add_vector(self.v_coords)
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()
        transform = Transform(
            equation_matrix.copy(), det_equation_matrix
        )
        self.play(Write(det_equation), transform)
        self.wait()

class TweakLambda(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[2, 1], [2, 3]],
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "secondary_line_ratio" : 1
        },
    }
    def construct(self):
        matrix = Matrix([
            ["2-0.00", "2"],
            ["1", "3-0.00"],
        ])
        matrix.add_to_back(BackgroundRectangle(matrix))
        matrix.next_to(ORIGIN, LEFT, buff = LARGE_BUFF)
        matrix.to_edge(UP)

        self.lambda_vals = []
        for i in range(2):
            entry = matrix.get_mob_matrix()[i,i]
            place_holders = VGroup(*entry[2:])
            entry.remove(*place_holders)
            place_holders.set_color(MAROON_B)
            self.lambda_vals.append(place_holders)


        brace = Brace(matrix)
        brace_text = TexMobject("(A-", "\\lambda", "I)")
        brace_text.set_color_by_tex("\\lambda", MAROON_B)
        brace_text.next_to(brace, DOWN)
        brace_text.add_background_rectangle()

        det_text = get_det_text(matrix)
        equals = TexMobject("=").next_to(det_text)
        det = DecimalNumber(np.linalg.det(self.t_matrix))
        det.set_color(YELLOW)
        det.next_to(equals)
        det.rect = BackgroundRectangle(det)

        self.det = det

        self.matrix = VGroup(matrix, brace, brace_text)
        self.add_foreground_mobject(
            self.matrix, *self.lambda_vals
        )
        self.add_unit_square()
        self.plane_mobjects = [
            self.plane, self.square,
        ]
        for mob in self.plane_mobjects:
            mob.save_state()
        self.apply_transposed_matrix(self.t_matrix)
        self.play(
            Write(det_text),
            Write(equals),
            ShowCreation(det.rect),
            Write(det)
        )
        self.matrix.add(det_text, equals, det.rect)
        self.wait()

        self.range_lambda(0, 3, run_time = 5)
        self.wait()
        self.range_lambda(3, 0.5, run_time = 5)
        self.wait()
        self.range_lambda(0.5, 1.5, run_time = 3)
        self.wait()
        self.range_lambda(1.5, 1, run_time = 2)
        self.wait()

    def get_t_matrix(self, lambda_val):
        return self.t_matrix - lambda_val*np.identity(2)

    def range_lambda(self, start_val, end_val, run_time = 3):
        alphas = np.linspace(0, 1, run_time/self.frame_duration)
        matrix_transform = self.get_matrix_transformation(
            self.get_t_matrix(end_val)
        )
        transformations = []
        for mob in self.plane_mobjects:
            mob.target = mob.copy().restore().apply_function(matrix_transform)
            transformations.append(MoveToTarget(mob))
        transformations += [
            Transform(
                self.i_hat, 
                Vector(matrix_transform(RIGHT), color = X_COLOR)
            ),
            Transform(
                self.j_hat, 
                Vector(matrix_transform(UP), color = Y_COLOR)
            ),
        ]
        for alpha in alphas:
            self.clear()
            val = interpolate(start_val, end_val, alpha)
            new_t_matrix = self.get_t_matrix(val)
            for transformation in transformations:
                transformation.update(alpha)
                self.add(transformation.mobject)
            self.add(self.matrix)

            new_lambda_vals = []
            for lambda_val in self.lambda_vals:
                new_lambda = DecimalNumber(val)
                new_lambda.move_to(lambda_val, aligned_edge = LEFT)
                new_lambda.set_color(lambda_val.get_color())
                new_lambda_vals.append(new_lambda)
            self.lambda_vals = new_lambda_vals
            self.add(*self.lambda_vals)

            new_det = DecimalNumber(
                np.linalg.det([
                    self.i_hat.get_end()[:2],
                    self.j_hat.get_end()[:2],
                ])
            )
            new_det.move_to(self.det, aligned_edge = LEFT)
            new_det.set_color(self.det.get_color())
            self.det = new_det
            self.add(self.det)

            self.wait(self.frame_duration)

class ShowEigenVectorAfterComputing(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[2, 1], [2, 3]],
        "v_coords" : [2, -1],
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "secondary_line_ratio" : 1
        },
    }
    def construct(self):
        matrix = Matrix(self.t_matrix.T)
        matrix.add_to_back(BackgroundRectangle(matrix))
        matrix.next_to(ORIGIN, RIGHT)
        matrix.shift(self.v_coords[0]*RIGHT)
        self.add_foreground_mobject(matrix)

        v_label = TexMobject(
            "\\vec{\\textbf{v}}",
            "=",
            "1", 
            "\\vec{\\textbf{v}}",
        )
        v_label.next_to(matrix, RIGHT)
        v_label.set_color_by_tex("\\vec{\\textbf{v}}", YELLOW)
        v_label.set_color_by_tex("1", MAROON_B)
        v_label.add_background_rectangle()

        v = self.add_vector(self.v_coords)
        eigenvector = TextMobject("Eigenvector")
        eigenvector.add_background_rectangle()
        eigenvector.next_to(ORIGIN, DOWN+RIGHT)
        eigenvector.rotate(v.get_angle())
        self.play(Write(eigenvector))
        self.add_foreground_mobject(eigenvector)

        line = Line(v.get_end()*(-4), v.get_end()*4, color = MAROON_B)
        self.play(Write(v_label))
        self.add_foreground_mobject(v_label)
        self.play(ShowCreation(line), Animation(v))
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()

class LineOfReasoning(Scene):
    def construct(self):
        v_tex = "\\vec{\\textbf{v}}"
        expressions = VGroup(*it.starmap(TexMobject, [
            ("A", v_tex, "=", "\\lambda", v_tex),
            ("A", v_tex, "-", "\\lambda", "I", v_tex, "=", "0"),
            ("(", "A", "-", "\\lambda", "I)", v_tex, "=", "0"),
            ("\\det(A-", "\\lambda", "I)", "=", "0")
        ]))
        expressions.arrange(DOWN, buff = LARGE_BUFF/2.)
        for expression in expressions:
            for i, expression_part in enumerate(expression.expression_parts):
                if expression_part == "=":
                    equals = expression[i]
                    expression.shift(equals.get_center()[0]*LEFT)
                    break
            expression.set_color_by_tex(v_tex, YELLOW)
            expression.set_color_by_tex("\\lambda", MAROON_B)
            self.play(FadeIn(expression))
        self.wait()

class IfYouDidntKnowDeterminants(TeacherStudentsScene):
    def construct(self):
        expression = TexMobject("\\det(A-", "\\lambda", "I" ")=0")
        expression.set_color_by_tex("\\lambda", MAROON_B)
        expression.scale(1.3)
        self.teacher_says(expression)
        self.random_blink()
        student = self.get_students()[0]
        bubble = get_small_bubble(student)
        bubble.write("Wait...why?")
        self.play(
            ShowCreation(bubble),
            Write(bubble.content),
            student.change_mode, "confused"
        )
        self.random_blink(4)

class RevisitExampleTransformation(ExampleTranformationScene):
    def construct(self):
        self.introduce_matrix()

        seeking_eigenvalue = TextMobject("Seeking eigenvalue")
        seeking_eigenvalue.add_background_rectangle()
        lamb = TexMobject("\\lambda")
        lamb.set_color(MAROON_B)
        words = VGroup(seeking_eigenvalue, lamb)
        words.arrange()
        words.next_to(self.matrix, DOWN, buff = LARGE_BUFF)
        self.play(Write(words))
        self.wait()
        self.play(*self.get_lambda_to_diag_movements(lamb.copy()))
        self.add_foreground_mobject(*self.get_mobjects_from_last_animation())
        self.wait()
        self.show_determinant(to_fade = words)
        self.show_diagonally_altered_transform()
        self.show_unaltered_transform()

    def introduce_matrix(self):
        self.matrix.shift(2*LEFT)
        for mob in self.plane, self.i_hat, self.j_hat:
            mob.save_state()
        self.remove_matrix()
        i_coords = Matrix(self.t_matrix[0])
        j_coords = Matrix(self.t_matrix[1])

        self.apply_transposed_matrix(self.t_matrix)
        for coords, vect in (i_coords, self.i_hat), (j_coords, self.j_hat):
            coords.set_color(vect.get_color())
            coords.scale(0.8)
            coords.rect = BackgroundRectangle(coords)
            coords.add_to_back(coords.rect)
            coords.next_to(
                vect.get_end(), 
                RIGHT+DOWN if coords is i_coords else RIGHT
            )
        self.play(
            Write(i_coords),
            Write(j_coords),
        )
        self.wait()
        self.play(*[
            Transform(*pair)
            for pair in [
                (i_coords.rect, self.matrix.rect),            
                (i_coords.get_brackets(), self.matrix.get_brackets()),
                (
                    i_coords.get_entries(), 
                    VGroup(*self.matrix.get_mob_matrix()[:,0])
                )
            ]
        ])
        to_remove = self.get_mobjects_from_last_animation()
        self.play(
            FadeOut(j_coords.get_brackets()),
            FadeOut(j_coords.rect),
            Transform(
                j_coords.get_entries(),
                VGroup(*self.matrix.get_mob_matrix()[:,1])
            ),
        )
        to_remove += self.get_mobjects_from_last_animation()
        self.wait()
        self.remove(*to_remove)
        self.add_foreground_mobject(self.matrix)

    def get_lambda_to_diag_movements(self, lamb):
        three, two = [self.matrix.get_mob_matrix()[i, i] for i in range(2)]
        l_bracket, r_bracket = self.matrix.get_brackets()
        rect = self.matrix.rect
        lamb_copy = lamb.copy()
        movers = [rect, three, two, l_bracket, r_bracket, lamb, lamb_copy]
        for mover in movers:
            mover.target = mover.copy()
        minus1, minus2 = [TexMobject("-") for x in range(2)]
        new_three = VGroup(three.target, minus1, lamb.target)
        new_three.arrange()
        new_three.move_to(three)
        new_two = VGroup(two.target, minus2, lamb_copy.target)
        new_two.arrange()
        new_two.move_to(two)
        l_bracket.target.next_to(VGroup(new_three, new_two), LEFT)
        r_bracket.target.next_to(VGroup(new_three, new_two), RIGHT)
        rect.target = BackgroundRectangle(
            VGroup(l_bracket.target, r_bracket.target)
        )
        result = list(map(MoveToTarget, movers)) 
        result += list(map(Write, [minus1, minus2]))
        result += list(map(Animation, [
            self.matrix.get_mob_matrix()[i, 1-i]
            for i in range(2)
        ]))
        self.diag_entries = [
            VGroup(three, minus1, lamb),
            VGroup(two, minus2, lamb_copy),
        ]
        return result

    def show_determinant(self, to_fade = None):
        det_text = get_det_text(self.matrix)
        equals = TexMobject("=").next_to(det_text)
        three_minus_lamb, two_minus_lamb = diag_entries = [
            entry.copy() for entry in self.diag_entries
        ]
        one = self.matrix.get_mob_matrix()[0, 1].copy()
        zero = self.matrix.get_mob_matrix()[1, 0].copy()
        for entry in diag_entries + [one, zero]:
            entry.target = entry.copy()
        lp1, rp1, lp2, rp2 = parens = TexMobject("()()")
        minus = TexMobject("-")
        cdot = TexMobject("\\cdot")
        VGroup(
            lp1, three_minus_lamb.target, rp1,
            lp2, two_minus_lamb.target, rp2,
            minus, one.target, cdot, zero.target
        ).arrange().next_to(equals)

        parens.add_background_rectangle()
        new_rect = BackgroundRectangle(VGroup(minus, zero.target))

        brace = Brace(new_rect, buff = 0)
        brace_text = brace.get_text("Equals 0, so ", "ignore")
        brace_text.add_background_rectangle()

        brace.target = Brace(parens)
        brace_text.target = brace.target.get_text(
            "Quadratic polynomial in ", "$\\lambda$"
        )
        brace_text.target.set_color_by_tex("$\\lambda$", MAROON_B)
        brace_text.target.add_background_rectangle()

        equals_0 = TexMobject("=0")
        equals_0.next_to(parens, RIGHT)
        equals_0.add_background_rectangle()

        final_brace = Brace(VGroup(parens, equals_0))
        final_text = TexMobject(
            "\\lambda", "=2", "\\text{ or }",
            "\\lambda", "=3"
        )
        final_text.set_color_by_tex("\\lambda", MAROON_B)
        final_text.next_to(final_brace, DOWN)
        lambda_equals_two = VGroup(*final_text[:2]).copy()
        lambda_equals_two.add_to_back(BackgroundRectangle(lambda_equals_two))
        final_text.add_background_rectangle()

        self.play(
            Write(det_text),
            Write(equals)
        )
        self.wait()
        self.play(
            Write(parens),            
            MoveToTarget(three_minus_lamb),
            MoveToTarget(two_minus_lamb),
            run_time = 2
        )
        self.wait()
        self.play(
            FadeIn(new_rect),
            MoveToTarget(one),
            MoveToTarget(zero),
            Write(minus),
            Write(cdot),
            run_time = 2
        )
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        self.play(*it.chain(
            list(map(MoveToTarget, [brace, brace_text])),
            list(map(FadeOut, [one, zero, minus, cdot, new_rect]))
        ))
        self.wait()
        self.play(Write(equals_0))
        self.wait()
        self.play(
            Transform(brace, final_brace),
            Transform(brace_text, final_text)
        )
        self.wait()
        faders = [
            det_text, equals, parens, 
            three_minus_lamb, two_minus_lamb,
            brace, brace_text, equals_0, 
        ]
        if to_fade is not None:
            faders.append(to_fade)
        self.play(*it.chain(
            list(map(FadeOut, faders)),
            [
                lambda_equals_two.scale_in_place, 1.3,
                lambda_equals_two.next_to, self.matrix, DOWN                
            ]
        ))
        self.add_foreground_mobject(lambda_equals_two)
        self.lambda_equals_two = lambda_equals_two
        self.wait()

    def show_diagonally_altered_transform(self):
        for entry in self.diag_entries:
            lamb = entry[-1]
            two = TexMobject("2")
            two.set_color(lamb.get_color())
            two.move_to(lamb)
            self.play(Transform(lamb, two))
        self.play(*it.chain(
            [mob.restore for mob in (self.plane, self.i_hat, self.j_hat)],
            list(map(Animation, self.foreground_mobjects)),            
        ))

        xy_array = Matrix(["x", "y"])
        xy_array.set_color(YELLOW)
        zero_array = Matrix([0, 0])
        for array in xy_array, zero_array:
            array.set_height(self.matrix.get_height())
            array.add_to_back(BackgroundRectangle(array))
        xy_array.next_to(self.matrix)
        equals = TexMobject("=").next_to(xy_array)
        equals.add_background_rectangle()
        zero_array.next_to(equals)
        self.play(*list(map(Write, [xy_array, equals, zero_array])))
        self.wait()

        vectors = VGroup(*[
            self.add_vector(u*x*(LEFT+UP), animate = False)
            for x in range(4, 0, -1)
            for u in [-1, 1]
        ])
        vectors.set_color_by_gradient(MAROON_B, YELLOW)
        vectors.save_state()
        self.play(
            ShowCreation(
                vectors, 
                lag_ratio = 0.5,
                run_time = 2
            ),
            *list(map(Animation, self.foreground_mobjects))
        )
        self.wait()
        self.apply_transposed_matrix(
            self.t_matrix - 2*np.identity(2)
        )
        self.wait()
        self.play(*it.chain(
            [mob.restore for mob in (self.plane, self.i_hat, self.j_hat, vectors)],
            list(map(FadeOut, [xy_array, equals, zero_array])),
            list(map(Animation, self.foreground_mobjects))
        ))

    def show_unaltered_transform(self):
        movers = []
        faders = []
        for entry in self.diag_entries:
            mover = entry[0]
            faders += list(entry[1:])
            mover.target = mover.copy()
            mover.target.move_to(entry)
            movers.append(mover)
        brace = Brace(self.matrix)
        brace_text = brace.get_text("Unaltered matrix")
        brace_text.add_background_rectangle()
        self.lambda_equals_two.target = brace_text
        movers.append(self.lambda_equals_two)
        self.play(*it.chain(
            list(map(MoveToTarget, movers)),
            list(map(FadeOut, faders)),
            [GrowFromCenter(brace)]
        ))
        VGroup(*faders).set_fill(opacity = 0)
        self.add_foreground_mobject(brace)
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()

class ThereMightNotBeEigenvectors(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            There could be
            \\emph{no} eigenvectors
        """)
        self.random_blink(3)

class Rotate90Degrees(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[0, 1], [-1, 0]],
        "example_vector_coords" : None,
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        matrix = Matrix(self.t_matrix.T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(ORIGIN, LEFT)
        matrix.to_edge(UP)
        matrix.rect = BackgroundRectangle(matrix)
        matrix.add_to_back(matrix.rect)
        self.add_foreground_mobject(matrix)
        self.matrix = matrix
        if self.example_vector_coords is not None:
            v = self.add_vector(self.example_vector_coords, animate = False)
            line = Line(v.get_end()*(-4), v.get_end()*4, color = MAROON_B)
            self.play(ShowCreation(line), Animation(v))
            self.add_foreground_mobject(line)

    def construct(self):
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()

class Rotate90DegreesWithVector(Rotate90Degrees):
    CONFIG = {
        "example_vector_coords" : [1, 2]
    }

class SolveRotationEigenvalues(Rotate90Degrees):
    def construct(self):
        self.apply_transposed_matrix(self.t_matrix, run_time = 0)
        self.wait()
        diag_entries = [
            self.matrix.get_mob_matrix()[i, i] 
            for i in range(2)
        ]
        off_diag_entries = [
            self.matrix.get_mob_matrix()[i, 1-i]
            for i in range(2)
        ]
        for entry in diag_entries:
            minus_lambda = TexMobject("-\\lambda")
            minus_lambda.set_color(MAROON_B)
            minus_lambda.move_to(entry)
            self.play(Transform(entry, minus_lambda))
        self.wait()

        det_text = get_det_text(self.matrix)
        equals = TexMobject("=").next_to(det_text)
        self.play(*list(map(Write, [det_text, equals])))
        self.wait()
        minus = TexMobject("-")
        for entries, sym in (diag_entries, equals), (off_diag_entries, minus):
            lp1, rp1, lp2, rp2 = parens = TexMobject("()()")
            for entry in entries:
                entry.target = entry.copy()
            group = VGroup(
                lp1, entries[0].target, rp1,
                lp2, entries[1].target, rp2,
            )
            group.arrange()
            group.next_to(sym)
            parens.add_background_rectangle()
            self.play(
                Write(parens),
                *[MoveToTarget(entry.copy()) for entry in entries],
                run_time = 2
            )
            self.wait()
            if entries == diag_entries:
                minus.next_to(parens)
                self.play(Write(minus))
        polynomial = TexMobject(
            "=", "\\lambda^2", "+1=0"
        )
        polynomial.set_color_by_tex("\\lambda^2", MAROON_B)
        polynomial.add_background_rectangle()
        polynomial.next_to(equals, DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT)
        self.play(Write(polynomial))
        self.wait()

        result = TexMobject(
            "\\lambda", "= i", "\\text{ or }",
            "\\lambda", "= -i"
        )
        result.set_color_by_tex("\\lambda", MAROON_B)
        result.add_background_rectangle()
        result.next_to(polynomial, DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT)
        self.play(Write(result))
        self.wait()

        interesting_tidbit = TextMobject("""
            Interestingly, though, the fact that multiplication by i 
            in the complex plane looks like a 90 degree rotation is 
            related to the fact that i is an eigenvalue of this 
            transformation of 2d real vectors. The specifics of this 
            are a little beyond what I want to talk about today, but 
            note that that eigenvalues which are complex numbers 
            generally correspond to some kind of rotation in the 
            transformation.
        """, alignment = "")
        interesting_tidbit.add_background_rectangle()
        interesting_tidbit.set_height(FRAME_Y_RADIUS-0.5)
        interesting_tidbit.to_corner(DOWN+RIGHT)
        self.play(FadeIn(interesting_tidbit))
        self.wait()

class ShearExample(RevisitExampleTransformation):
    CONFIG = {
        "t_matrix" : [[1, 0], [1, 1]],
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_HEIGHT,
            "secondary_line_ratio" : 1
        },
    }
    def construct(self):
        self.plane.fade()
        self.introduce_matrix()
        self.point_out_eigenvectors()
        lamb = TexMobject("\\lambda")
        lamb.set_color(MAROON_B)
        lamb.next_to(self.matrix, DOWN)
        self.play(FadeIn(lamb))
        self.play(*self.get_lambda_to_diag_movements(lamb))
        self.add_foreground_mobject(*self.get_mobjects_from_last_animation())
        self.wait()
        self.show_determinant()

    def point_out_eigenvectors(self):
        vectors = VGroup(*[
            self.add_vector(u*x*RIGHT, animate = False)
            for x in range(int(FRAME_X_RADIUS)+1, 0, -1)
            for u in [-1, 1]
        ])
        vectors.set_color_by_gradient(YELLOW, X_COLOR)
        words = VGroup(
            TextMobject("Eigenvectors"),
            TextMobject("with eigenvalue", "1")
        )
        for word in words:
            word.set_color_by_tex("1", MAROON_B)
            word.add_to_back(BackgroundRectangle(word))
        words.arrange(DOWN, buff = MED_SMALL_BUFF)
        words.next_to(ORIGIN, DOWN+RIGHT, buff = MED_SMALL_BUFF)
        self.play(ShowCreation(vectors), run_time = 2)
        self.play(Write(words))
        self.wait()

    def show_determinant(self):
        det_text = get_det_text(self.matrix)
        equals = TexMobject("=").next_to(det_text)
        three_minus_lamb, two_minus_lamb = diag_entries = [
            entry.copy() for entry in self.diag_entries
        ]
        one = self.matrix.get_mob_matrix()[0, 1].copy()
        zero = self.matrix.get_mob_matrix()[1, 0].copy()
        for entry in diag_entries + [one, zero]:
            entry.target = entry.copy()
        lp1, rp1, lp2, rp2 = parens = TexMobject("()()")
        minus = TexMobject("-")
        cdot = TexMobject("\\cdot")
        VGroup(
            lp1, three_minus_lamb.target, rp1,
            lp2, two_minus_lamb.target, rp2,
            minus, one.target, cdot, zero.target
        ).arrange().next_to(equals)

        parens.add_background_rectangle()
        new_rect = BackgroundRectangle(VGroup(minus, zero.target))

        brace = Brace(new_rect, buff = 0)
        brace_text = brace.get_text("Equals 0, so ", "ignore")
        brace_text.add_background_rectangle()

        brace.target = Brace(parens)
        brace_text.target = brace.target.get_text(
            "Quadratic polynomial in ", "$\\lambda$"
        )
        brace_text.target.set_color_by_tex("$\\lambda$", MAROON_B)
        brace_text.target.add_background_rectangle()

        equals_0 = TexMobject("=0")
        equals_0.next_to(parens, RIGHT)
        equals_0.add_background_rectangle()

        final_brace = Brace(VGroup(parens, equals_0))
        final_text = TexMobject("\\lambda", "=1")
        final_text.set_color_by_tex("\\lambda", MAROON_B)
        final_text.next_to(final_brace, DOWN)
        lambda_equals_two = VGroup(*final_text[:2]).copy()
        lambda_equals_two.add_to_back(BackgroundRectangle(lambda_equals_two))
        final_text.add_background_rectangle()

        self.play(
            Write(det_text),
            Write(equals)
        )
        self.wait()
        self.play(
            Write(parens),            
            MoveToTarget(three_minus_lamb),
            MoveToTarget(two_minus_lamb),
            run_time = 2
        )
        self.wait()
        self.play(
            FadeIn(new_rect),
            MoveToTarget(one),
            MoveToTarget(zero),
            Write(minus),
            Write(cdot),
            run_time = 2
        )
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        self.play(* list(map(FadeOut, [
            one, zero, minus, cdot, new_rect, brace, brace_text
        ])))
        self.wait()
        self.play(Write(equals_0))
        self.wait()
        self.play(
            FadeIn(final_brace),
            FadeIn(final_text)
        )
        self.wait()
        # faders = [
        #     det_text, equals, parens, 
        #     three_minus_lamb, two_minus_lamb,
        #     brace, brace_text, equals_0, 
        # ]
        # if to_fade is not None:
        #     faders.append(to_fade)
        # self.play(*it.chain(
        #     map(FadeOut, faders),
        #     [
        #         lambda_equals_two.scale_in_place, 1.3,
        #         lambda_equals_two.next_to, self.matrix, DOWN                
        #     ]
        # ))
        # self.add_foreground_mobject(lambda_equals_two)
        # self.lambda_equals_two = lambda_equals_two
        # self.wait()

class EigenvalueCanHaveMultipleEigenVectors(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            A single eigenvalue can 
            have more that a line
            full of eigenvectors
        """)
        self.change_student_modes(*["pondering"]*3)
        self.random_blink(2)

class ScalingExample(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[2, 0], [0, 2]]
    }
    def construct(self):
        matrix = Matrix(self.t_matrix.T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.add_to_back(BackgroundRectangle(matrix))
        matrix.next_to(ORIGIN, LEFT)
        matrix.to_edge(UP)
        words = TextMobject("Scale everything by 2")
        words.add_background_rectangle()
        words.next_to(matrix, RIGHT)
        self.add_foreground_mobject(matrix, words)
        for coords in [2, 1], [-2.5, -1], [1, -1]:
            self.add_vector(coords, color = random_color())
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()

class IntroduceEigenbasis(TeacherStudentsScene):
    def construct(self):
        words1, words2 = list(map(TextMobject, [
            "Finish with ``eigenbasis.''",
            """Make sure you've
            watched the last video"""
        ]))
        words1.set_color(YELLOW)
        self.teacher_says(words1)
        self.change_student_modes(
            "pondering", "raise_right_hand", "erm"
        )
        self.random_blink()
        new_words = VGroup(words1.copy(), words2)
        new_words.arrange(DOWN, buff = MED_SMALL_BUFF)
        new_words.scale(0.8)
        self.teacher.bubble.add_content(new_words)
        self.play(
            self.get_teacher().change_mode, "sassy",
            Write(words2),
            Transform(words1, new_words[0])
        )
        student = self.get_students()[0]
        self.play(
            student.change_mode, "guilty",
            student.look, LEFT
        )
        self.random_blink(2)

class BasisVectorsAreEigenvectors(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[-1, 0], [0, 2]]
    }
    def construct(self):
        matrix = Matrix(self.t_matrix.T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(ORIGIN, LEFT)
        matrix.to_edge(UP)

        words = TextMobject(
            "What if both basis vectors \\\\",
            "are eigenvectors?"
        )
        for word in words:
            word.add_to_back(BackgroundRectangle(word))
        words.to_corner(UP+RIGHT)

        self.play(Write(words))
        self.add_foreground_mobject(words)
        self.wait()
        self.apply_transposed_matrix([self.t_matrix[0], [0, 1]])
        self.wait()
        self.apply_transposed_matrix([[1, 0], self.t_matrix[1]])
        self.wait()

        i_coords = Matrix(self.t_matrix[0])
        i_coords.next_to(self.i_hat.get_end(), DOWN+LEFT)
        i_coords.set_color(X_COLOR)
        j_coords = Matrix(self.t_matrix[1])
        j_coords.next_to(self.j_hat.get_end(), RIGHT)
        j_coords.set_color(Y_COLOR)

        for array in matrix, i_coords, j_coords:
            array.rect = BackgroundRectangle(array)
            array.add_to_back(array.rect)
        self.play(*list(map(Write, [i_coords, j_coords])))
        self.wait()
        self.play(
            Transform(i_coords.rect, matrix.rect),
            Transform(i_coords.get_brackets(), matrix.get_brackets()),
            i_coords.get_entries().move_to, VGroup(
                *matrix.get_mob_matrix()[:,0]
            )
        )
        self.play(
            FadeOut(j_coords.rect),
            FadeOut(j_coords.get_brackets()),
            j_coords.get_entries().move_to, VGroup(
                *matrix.get_mob_matrix()[:,1]
            )
        )
        self.remove(i_coords, j_coords)
        self.add(matrix)
        self.wait()


        diag_entries = VGroup(*[
            matrix.get_mob_matrix()[i, i]
            for i in range(2)
        ])
        off_diag_entries = VGroup(*[
            matrix.get_mob_matrix()[1-i, i]
            for i in range(2)
        ])
        for entries in diag_entries, off_diag_entries:
            self.play(
                entries.scale_in_place, 1.3,
                entries.set_color, YELLOW,
                run_time = 2,
                rate_func = there_and_back
            )
        self.wait()

class DefineDiagonalMatrix(Scene):
    def construct(self):
        n_dims = 4
        numerical_matrix = np.identity(n_dims, dtype = 'int')
        for x in range(n_dims):
            numerical_matrix[x, x] = random.randint(-9, 9)
        matrix = Matrix(numerical_matrix)
        diag_entries = VGroup(*[
            matrix.get_mob_matrix()[i,i]
            for i in range(n_dims)
        ])
        off_diag_entries = VGroup(*[
            matrix.get_mob_matrix()[i, j]
            for i in range(n_dims)
            for j in range(n_dims)
            if i != j
        ])

        title = TextMobject("``Diagonal matrix''")
        title.to_edge(UP)

        self.add(matrix)
        self.wait()
        for entries in off_diag_entries, diag_entries:
            self.play(
                entries.scale_in_place, 1.1,
                entries.set_color, YELLOW,
                rate_func = there_and_back,
            )
        self.wait()
        self.play(Write(title))
        self.wait()
        self.play(
            matrix.set_column_colors,
            X_COLOR, Y_COLOR, Z_COLOR, YELLOW
        )
        self.wait()
        self.play(diag_entries.set_color, MAROON_B)
        self.play(
            diag_entries.scale_in_place, 1.1,
            rate_func = there_and_back,
        )
        self.wait()

class RepeatedMultiplicationInAction(Scene):
    def construct(self):
        vector = Matrix(["x", "y"])
        vector.set_color(YELLOW)
        vector.scale(1.2)
        vector.shift(RIGHT)
        matrix, scalars = self.get_matrix(vector)
        #First multiplication
        for v_entry, scalar in zip(vector.get_entries(), scalars):
            scalar.target = scalar.copy()
            scalar.target.next_to(v_entry, LEFT)
        l_bracket = vector.get_brackets()[0]
        l_bracket.target = l_bracket.copy()
        l_bracket.target.next_to(VGroup(*[
            scalar.target for scalar in scalars
        ]), LEFT)

        self.add(vector)
        self.play(*list(map(FadeIn, [matrix]+scalars)))
        self.wait()
        self.play(
            FadeOut(matrix),
            *list(map(MoveToTarget, scalars + [l_bracket]))
        )
        self.wait()
        #nth multiplications                    
        for scalar in scalars:
            scalar.exp = VectorizedPoint(scalar.get_corner(UP+RIGHT))
            scalar.exp.shift(SMALL_BUFF*RIGHT/2.)
        for new_exp in range(2, 6):
            matrix, new_scalars = self.get_matrix(vector)
            new_exp_mob = TexMobject(str(new_exp)).scale(0.7)
            movers = []
            to_remove = []
            for v_entry, scalar, new_scalar in zip(vector.get_entries(), scalars, new_scalars):
                scalar.exp.target = new_exp_mob.copy()
                scalar.exp.target.set_color(scalar.get_color())
                scalar.exp.target.move_to(scalar.exp, aligned_edge = LEFT)
                new_scalar.target = scalar.exp.target
                scalar.target = scalar.copy()
                VGroup(scalar.target, scalar.exp.target).next_to(
                    v_entry, LEFT, aligned_edge = DOWN
                )
                movers += [scalar, scalar.exp, new_scalar]
                to_remove.append(new_scalar)
            l_bracket.target.next_to(VGroup(*[
                scalar.target for scalar in scalars
            ]), LEFT)
            movers.append(l_bracket)

            self.play(*list(map(FadeIn, [matrix]+new_scalars)))
            self.wait()
            self.play(
                FadeOut(matrix),
                *list(map(MoveToTarget, movers))
            )
            self.remove(*to_remove)
            self.wait()


    def get_matrix(self, vector):
        matrix = Matrix([[3, 0], [0, 2]])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(vector, LEFT)
        scalars = [matrix.get_mob_matrix()[i, i] for i in range(2)]
        matrix.remove(*scalars)
        return matrix, scalars

class RepeatedMultilpicationOfMatrices(Scene):
    CONFIG = {
        "matrix" : [[3, 0], [0, 2]],
        "diagonal" : True,
    }
    def construct(self):
        vector = Matrix(["x", "y"])
        vector.set_color(YELLOW)
        matrix = Matrix(self.matrix)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrices = VGroup(*[
            matrix.copy(),
            TexMobject("\\dots\\dots"),
            matrix.copy(),
            matrix.copy(),
            matrix.copy(),
        ])
        last_matrix = matrices[-1]
        group = VGroup(*list(matrices) + [vector])
        group.arrange()

        brace = Brace(matrices)
        brace_text = brace.get_text("100", "times")
        hundred = brace_text[0]
        hundred_copy = hundred.copy()

        self.add(vector)
        for matrix in reversed(list(matrices)):
            self.play(FadeIn(matrix))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()

        if self.diagonal:
            last_matrix.target = last_matrix.copy()
            for i, hund in enumerate([hundred, hundred_copy]):
                entry = last_matrix.target.get_mob_matrix()[i, i]
                hund.target = hund.copy()
                hund.target.scale(0.5)
                hund.target.next_to(entry, UP+RIGHT, buff = 0)
                hund.target.set_color(entry.get_color())
                VGroup(hund.target, entry).move_to(entry, aligned_edge = DOWN)
            lb, rb = last_matrix.target.get_brackets()
            lb.shift(SMALL_BUFF*LEFT)
            rb.shift(SMALL_BUFF*RIGHT)
            VGroup(
                last_matrix.target, hundred.target, hundred_copy.target
            ).next_to(vector, LEFT)

            self.play(*it.chain(
                list(map(FadeOut, [brace, brace_text[1]] + list(matrices[:-1]))),
                list(map(MoveToTarget, [hundred, hundred_copy, last_matrix]))
            ), run_time = 2)
            self.wait()
        else:
            randy = Randolph().to_corner()
            self.play(FadeIn(randy))
            self.play(randy.change_mode, "angry")
            self.play(Blink(randy))
            self.wait()
            self.play(Blink(randy))
            self.wait()

class RepeatedMultilpicationOfNonDiagonalMatrices(RepeatedMultilpicationOfMatrices):
    CONFIG = {
        "matrix" : [[3, 4], [1, 1]],
        "diagonal" : False,
    }

class WhatAreTheOddsOfThat(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            Sure, but what are the
            odds of that happening?
        """)
        self.random_blink()
        self.change_student_modes("pondering")
        self.random_blink(3)

class LastVideo(Scene):
    def construct(self):
        title = TextMobject("Last chapter: Change of basis")
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN, buff = MED_SMALL_BUFF)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()

class ChangeToEigenBasis(ExampleTranformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_HEIGHT,
            "secondary_line_ratio" : 0
        },
    }
    def construct(self):
        self.plane.fade()
        self.introduce_eigenvectors()
        self.write_change_of_basis_matrix()
        self.ask_about_power()

    def introduce_eigenvectors(self):
        x_vectors, v_vectors = [
            VGroup(*[
                self.add_vector(u*x*vect, animate = False)
                for x in range(num, 0, -1)
                for u in [-1, 1]
            ])
            for vect, num in [(RIGHT, 7), (UP+LEFT, 4)]
        ]
        x_vectors.set_color_by_gradient(YELLOW, X_COLOR)
        v_vectors.set_color_by_gradient(MAROON_B, YELLOW)
        self.remove(x_vectors, v_vectors)
        self.play(ShowCreation(x_vectors, run_time = 2))
        self.play(ShowCreation(v_vectors, run_time = 2))
        self.wait()
        self.plane.save_state()
        self.apply_transposed_matrix(
            self.t_matrix, 
            rate_func = there_and_back,
            path_arc = 0
        )

        x_vector = x_vectors[-1]
        v_vector = v_vectors[-1]
        x_vectors.remove(x_vector)
        v_vectors.remove(v_vector)
        words = TextMobject("Eigenvectors span space")
        new_words = TextMobject("Use eigenvectors as basis")
        for text in words, new_words:
            text.add_background_rectangle()
            text.next_to(ORIGIN, DOWN+LEFT, buff = MED_SMALL_BUFF)
            # text.to_edge(RIGHT)

        self.play(Write(words))
        self.play(
            FadeOut(x_vectors),
            FadeOut(v_vectors),
            Animation(x_vector),
            Animation(v_vector),
        )
        self.wait()
        self.play(Transform(words, new_words))
        self.wait()
        self.b1, self.b2 = x_vector, v_vector
        self.moving_vectors = [self.b1, self.b2]
        self.to_fade = [words]

    def write_change_of_basis_matrix(self):
        b1, b2 = self.b1, self.b2
        for vect in b1, b2:
            vect.coords = vector_coordinate_label(vect)
            vect.coords.set_color(vect.get_color())
            vect.entries = vect.coords.get_entries()
            vect.entries.target = vect.entries.copy()
        b1.coords.next_to(b1.get_end(), DOWN+RIGHT)
        b2.coords.next_to(b2.get_end(), LEFT)
        for vect in b1, b2:
            self.play(Write(vect.coords))
        self.wait()

        cob_matrix = Matrix(np.array([
            list(vect.entries.target)
            for vect in (b1, b2)
        ]).T)
        cob_matrix.rect = BackgroundRectangle(cob_matrix)
        cob_matrix.add_to_back(cob_matrix.rect)
        cob_matrix.set_height(self.matrix.get_height())
        cob_matrix.next_to(self.matrix)
        brace = Brace(cob_matrix)
        brace_text = brace.get_text("Change of basis matrix")
        brace_text.next_to(brace, DOWN, aligned_edge = LEFT)
        brace_text.add_background_rectangle()

        copies = [vect.coords.copy() for vect in (b1, b2)]
        self.to_fade += copies
        self.add(*copies)
        self.play(
            Transform(b1.coords.rect, cob_matrix.rect),
            Transform(b1.coords.get_brackets(), cob_matrix.get_brackets()),
            MoveToTarget(b1.entries)
        )
        to_remove = self.get_mobjects_from_last_animation()
        self.play(MoveToTarget(b2.entries))
        to_remove += self.get_mobjects_from_last_animation()
        self.remove(*to_remove)
        self.add(cob_matrix)
        self.to_fade += [b2.coords]
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.to_fade += [brace, brace_text]
        self.wait()

        inv_cob = cob_matrix.copy()
        inv_cob.target = inv_cob.copy()
        neg_1 = TexMobject("-1")
        neg_1.add_background_rectangle()
        inv_cob.target.next_to(
            self.matrix, LEFT, buff = neg_1.get_width()+2*SMALL_BUFF
        )
        neg_1.next_to(
            inv_cob.target.get_corner(UP+RIGHT), 
            RIGHT, 
        )
        self.play(
            MoveToTarget(inv_cob, path_arc = -np.pi/2),
            Write(neg_1)
        )
        self.wait()
        self.add_foreground_mobject(cob_matrix, inv_cob, neg_1)
        self.play(*list(map(FadeOut, self.to_fade)))
        self.wait()
        self.play(FadeOut(self.plane))
        cob_transform = self.get_matrix_transformation([[1, 0], [-1, 1]])        
        ApplyMethod(self.plane.apply_function, cob_transform).update(1)
        self.planes.set_color(BLUE_D)
        self.plane.axes.set_color(WHITE)
        self.play(
            FadeIn(self.plane),
            *list(map(Animation, self.foreground_mobjects+self.moving_vectors))
        )
        self.add(self.plane.copy().set_color(GREY).set_stroke(width = 2))
        self.apply_transposed_matrix(self.t_matrix)

        equals = TexMobject("=").next_to(cob_matrix)
        final_matrix = Matrix([[3, 0], [0, 2]])
        final_matrix.add_to_back(BackgroundRectangle(final_matrix))
        for i in range(2):
            final_matrix.get_mob_matrix()[i, i].set_color(MAROON_B)
        final_matrix.next_to(equals, RIGHT)
        self.play(
            Write(equals),
            Write(final_matrix)
        )
        self.wait()

        eigenbasis = TextMobject("``Eigenbasis''")
        eigenbasis.add_background_rectangle()
        eigenbasis.next_to(ORIGIN, DOWN)
        self.play(Write(eigenbasis))
        self.wait()

    def ask_about_power(self):
        morty = Mortimer()
        morty.to_edge(DOWN).shift(LEFT)
        bubble = morty.get_bubble(
            "speech", height = 3, width = 5, direction = RIGHT
        )
        bubble.set_fill(BLACK, opacity = 1)
        matrix_copy = self.matrix.copy().scale(0.7)
        hundred = TexMobject("100").scale(0.7)
        hundred.next_to(matrix_copy.get_corner(UP+RIGHT), RIGHT)
        compute = TextMobject("Compute")
        compute.next_to(matrix_copy, LEFT, buff = MED_SMALL_BUFF)
        words = VGroup(compute, matrix_copy, hundred)
        bubble.add_content(words)

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "speaking",
            ShowCreation(bubble),
            Write(words)
        )
        for x in range(2):
            self.play(Blink(morty))
            self.wait(2)

class CannotDoWithWithAllTransformations(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Not all matrices
            can become diagonal
        """)
        self.change_student_modes(*["tired"]*3)
        self.random_blink(2)
















