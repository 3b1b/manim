from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import VMobject

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.numerals import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from mobject.vectorized_mobject import *

from eola.matrix import *
from eola.two_d_space import *
from eola.chapter1 import plane_wave_homotopy

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
            enforce_new_line_structure = False
        )
        words.highlight_by_tex("mathematics", BLUE)
        words.highlight_by_tex("music", BLUE)
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Serge Lang")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(Write(words, run_time = 10))
        self.dither()
        self.play(FadeIn(author))
        self.dither(3)

class StudentsFindThisConfusing(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Eigenvectors and Eigenvalues")
        title.to_edge(UP)
        students = self.get_students()

        self.play(
            Write(title), 
            *[
                ApplyMethod(pi.look_at, title)
                for pi in self.get_everyone()
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
            buff = MED_BUFF
        )
        equation = TexMobject(
            "\\det\\left( %s \\right)=0"%matrix_to_tex_string([
                ["a-\\lambda", "b"],
                ["c", "d-\\lambda"],
            ])
        )
        equation.highlight(YELLOW)
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
            pi_creature_target_mode = "hooray"
        )
        self.change_student_modes(
            "pondering", "pondering", "erm"
        )
        self.random_blink(4)

class ManyPrerequisites(Scene):
    def construct(self):
        title = TextMobject("Many prerequisites")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        h_line.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(h_line))

        rect = Rectangle(height = 9, width = 16, color = BLUE)
        rect.scale_to_fit_width(SPACE_WIDTH-2)
        rects = [rect]+[rect.copy() for i in range(3)]
        words = [
            "Linear transformations",
            "Determinants",
            "Linear systems",
            "Change of basis",
        ]
        for rect, word in zip(rects, words):
            word_mob = TextMobject(word)
            word_mob.next_to(rect, UP, buff = MED_BUFF)
            rect.add(word_mob)

        Matrix(np.array(rects).reshape((2, 2)))
        rects = VGroup(*rects)
        rects.scale_to_fit_height(2*SPACE_HEIGHT - 1.5)
        rects.next_to(h_line, DOWN, buff = MED_BUFF)

        self.play(Write(rects[0]))
        self.dither()
        self.play(*map(FadeIn, rects[1:]))
        self.dither()

class ExampleTranformationScene(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[3, 0], [1, 2]]
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        self.add_matrix()

    def add_matrix(self):
        matrix = Matrix(self.t_matrix.T)
        matrix.highlight_columns(X_COLOR, Y_COLOR)
        matrix.next_to(ORIGIN, LEFT, buff = MED_BUFF)
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
            coords.highlight(vect.get_color())
            coords.scale(0.8)
            coords.rect = BackgroundRectangle(coords)
            coords.add_to_back(coords.rect)
            coords.next_to(vect.get_end(), RIGHT)
            self.play(Write(coords))
            self.dither()
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
        self.play(Transform(
            j_coords.copy().get_entries(),
            VGroup(*self.matrix.get_mob_matrix()[:,1])
        ))
        self.dither()

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
            MED_BUFF*LEFT
        )
        for text in all_words:
            text.add_to_back(BackgroundRectangle(text))

        self.add_vector(vector)
        self.dither()
        self.play(
            ShowCreation(line),
            Write(span_label),
            Animation(vector),
        )
        self.add_foreground_mobject(span_label)
        self.dither()
        self.apply_transposed_matrix(self.t_matrix)
        self.play(Animation(span_label.copy()), Write(all_words))
        self.dither()

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
        self.dither()
        self.apply_transposed_matrix(self.t_matrix)
        self.play(Write(words))
        self.dither()
        target_vectors = [
            vector.copy().scale(scalar)
            for scalar in 2, -2, 1
        ]
        for target, time in zip(target_vectors, [1, 2, 2]):
            self.play(Transform(vector, target, run_time = time))
        self.dither()

class IHatAsEigenVector(ExampleTranformationScene):
    def construct(self):
        self.highlight_first_column()
        self.highlight_x_axis()        
        self.apply_transposed_matrix(self.t_matrix, path_arc = 0)
        self.label_i_hat_landing_spot()

    def highlight_first_column(self):
        faders = VGroup(self.plane, self.i_hat, self.j_hat)
        faders.save_state()
        column1 = VGroup(*self.matrix.get_mob_matrix()[:,0])

        self.play(faders.fade, 0.7, Animation(self.matrix))
        self.play(column1.scale_in_place, 1.3, rate_func = there_and_back)
        self.dither()
        self.play(faders.restore, Animation(self.matrix))
        self.dither()

    def highlight_x_axis(self):
        x_axis = self.plane.axes[0]
        targets = [
            self.i_hat.copy().scale(val)
            for val in -SPACE_WIDTH, SPACE_WIDTH, 1
        ]
        lines = [
            Line(v1.get_end(), v2.get_end(), color = YELLOW)
            for v1, v2 in adjascent_pairs([self.i_hat]+targets)
        ]
        for target, line in zip(targets, lines):
            self.play(
                ShowCreation(line),                
                Transform(self.i_hat, target),
            )
        self.dither()
        self.remove(*lines)
        x_axis.highlight(YELLOW)

    def label_i_hat_landing_spot(self):
        array = Matrix(self.t_matrix[0])
        array.highlight(X_COLOR)
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
        self.dither()

class AllXAxisVectorsAreEigenvectors(ExampleTranformationScene):
    def construct(self):
        vectors = VGroup(*[
            self.add_vector(u*x*RIGHT, animate = False)
            for x in reversed(range(1, int(SPACE_WIDTH)+1))
            for u in -1, 1
        ])
        vectors.gradient_highlight(YELLOW, X_COLOR)
        self.play(ShowCreation(vectors))
        self.dither()
        self.apply_transposed_matrix(self.t_matrix, path_arc = 0)
        self.dither()

class SneakierEigenVector(ExampleTranformationScene):
    def construct(self):
        coords = [-1, 1]
        vector = Vector(coords)
        array = Matrix(coords)
        array.scale(0.7)
        array.highlight(vector.get_color())
        array.add_to_back(BackgroundRectangle(array))        
        array.target = array.copy()
        array.next_to(vector.get_end(), LEFT)
        array.target.next_to(2*vector.get_end(), LEFT)
        two_times = TexMobject("2 \\cdot")
        two_times.add_background_rectangle()
        two_times.next_to(array.target, LEFT)
        span_line = Line(-4*vector.get_end(), 4*vector.get_end())
        span_line.highlight(MAROON_B)

        self.matrix.shift(-2*self.matrix.get_center()[0]*RIGHT)

        self.add_vector(vector)
        self.play(Write(array))
        self.play(
            ShowCreation(span_line), 
            Animation(vector),
            Animation(array),
        )
        self.dither()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [
                MoveToTarget(array),
                Transform(VectorizedPoint(array.get_left()), two_times)
            ],
            path_arc = 0,
        )
        self.dither()

class FullSneakyEigenspace(ExampleTranformationScene):
    def construct(self):
        self.matrix.shift(-2*self.matrix.get_center()[0]*RIGHT)
        vectors = VGroup(*[
            self.add_vector(u*x*(LEFT+UP), animate = False)
            for x in reversed(np.arange(0.5, 5, 0.5))
            for u in -1, 1
        ])
        vectors.gradient_highlight(MAROON_B, YELLOW)
        words = TextMobject("Stretch by 2")
        words.add_background_rectangle()
        words.next_to(ORIGIN, DOWN+LEFT, buff = MED_BUFF)
        words.shift(MED_BUFF*LEFT)
        words.rotate(vectors[0].get_angle())
        words.start = words.copy()
        words.start.scale(0.5)
        words.start.set_fill(opacity = 0)

        self.play(ShowCreation(vectors))
        self.dither()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [Transform(words.start, words)],
            path_arc = 0
        )
        self.dither()

class NameEigenvectorsAndEigenvalues(ExampleTranformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.remove(self.matrix)
        self.foreground_mobjects.remove(self.matrix)
        x_vectors = VGroup(*[
            self.add_vector(u*x*RIGHT, animate = False)
            for x in range(int(SPACE_WIDTH)+1, 0, -1)
            for u in -1, 1
        ])
        x_vectors.gradient_highlight(YELLOW, X_COLOR)
        self.remove(x_vectors)
        sneak_vectors = VGroup(*[
            self.add_vector(u*x*(LEFT+UP), animate = False)
            for x in np.arange(int(SPACE_HEIGHT), 0, -0.5)
            for u in -1, 1
        ])
        sneak_vectors.gradient_highlight(MAROON_B, YELLOW)
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
        x_words.eigen_val_words.highlight(X_COLOR)
        sneak_words.eigen_val_words.highlight(YELLOW)

        VGroup(
            sneak_words,
            sneak_words.target,
            sneak_words.eigen_val_words,
        ).rotate(sneak_vectors[0].get_angle())

        non_eigen = Vector([1, 1], color = PINK)
        non_eigen_span = Line(
            -SPACE_HEIGHT*non_eigen.get_end(), 
            SPACE_HEIGHT*non_eigen.get_end(), 
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
        self.dither()
        for words in x_words, sneak_words:
            self.play(Write(words, run_time = 1.5))
            self.add_foreground_mobject(words)
            self.dither()
        self.play(ShowCreation(non_eigen))
        self.play(
            ShowCreation(non_eigen_span),
            Write(non_eigen_words),
            Animation(non_eigen)
        )
        self.add_vector(non_eigen, animate = False)
        self.dither()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [FadeOut(non_eigen_words)],
            path_arc = 0,
        )
        self.dither(2)
        self.play(*map(FadeOut, [non_eigen, non_eigen_span]))
        self.play(*map(MoveToTarget, [x_words, sneak_words]))
        self.dither()
        for words in x_words, sneak_words:
            self.play(Write(words.eigen_val_words), run_time = 2)
            self.dither()























