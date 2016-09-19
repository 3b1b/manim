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
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from mobject.vectorized_mobject import *

from eola.matrix import *
from eola.two_d_space import *
from eola.chapter1 import plane_wave_homotopy
from eola.chapter3 import ColumnsToBasisVectors
from eola.chapter5 import NameDeterminant
from eola.chapter9 import get_small_bubble
from eola.chapter10 import ExampleTranformationScene

class Student(PiCreature):
    CONFIG = {
        "name" : "Student"
    }
    def get_name(self):
        text = TextMobject(self.name)
        text.add_background_rectangle()
        text.next_to(self, DOWN)
        return text

class PhysicsStudent(Student):
    CONFIG = {
        "color" : PINK,
        "name" : "Physics student"
    }

class CSStudent(Student):
    CONFIG = {
        "color" : PURPLE_E,
        "flip_at_start" : True,
        "name" : "CS Student"
    } 

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "``Such",
            "axioms,", 
            "together with other unmotivated definitions,", 
            "serve mathematicians mainly by making it",
            "difficult for the uninitiated",
            "to master their subject, thereby elevating its authority.''",
            enforce_new_line_structure = False,
            alignment = "",
        )
        words.highlight_by_tex("axioms,", BLUE)
        words.highlight_by_tex("difficult for the uninitiated", RED)
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Vladmir Arnold")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 2*MED_BUFF)

        self.play(Write(words, run_time = 8))
        self.dither()
        self.play(FadeIn(author))
        self.dither(3)

class RevisitOriginalQuestion(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Let's revisit \\\\ an old question")
        self.random_blink()
        question = TextMobject("What are ", "vectors", "?", arg_separator = "")
        question.highlight_by_tex("vectors", YELLOW)
        self.teacher_says(
            question,
            added_anims = [
                ApplyMethod(self.get_students()[i].change_mode, mode)
                for i, mode in enumerate([
                    "pondering", "raise_right_hand", "erm"
                ])
            ]
        )
        self.random_blink(2)

class WhatIsA2DVector(LinearTransformationScene):
    CONFIG = {
        "v_coords" : [1, 2],
        "show_basis_vectors" : False,
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_HEIGHT,
            "secondary_line_ratio" : 1
        },
    }
    def construct(self):
        self.plane.fade()
        self.introduce_vector_and_space()
        self.bring_in_students()

    def introduce_vector_and_space(self):
        v = Vector(self.v_coords)
        coords = Matrix(self.v_coords)
        coords.add_to_back(BackgroundRectangle(coords))
        coords.next_to(v.get_end(), RIGHT)

        two_d_vector, two_d_space = words = [
            TextMobject(
                "``Two-dimensional ", word, "''", arg_separator = ""
            ).highlight_by_tex(word, color)
            for word, color in ("vector", YELLOW), ("space", BLUE)
        ]
        for word, vect in zip(words, [LEFT, RIGHT]):
            word.add_background_rectangle()
            word.next_to(ORIGIN, vect, buff = MED_BUFF)
            word.to_edge(UP)

        self.play(
            Write(two_d_vector),
            ShowCreation(v),
            Write(coords),
            run_time = 2
        )
        self.dither()
        last_mobs = self.get_mobjects_from_last_animation()
        self.play(
            Homotopy(plane_wave_homotopy, self.plane),
            Write(two_d_space, run_time = 2),
            *map(Animation, last_mobs)
        )
        self.dither()
        self.v, self.coords = v, coords

    def bring_in_students(self):
        everything = self.get_mobjects()
        v, coords = self.v, self.coords
        physics_student = PhysicsStudent()
        cs_student = CSStudent()
        students = [physics_student, cs_student]
        for student, vect in zip(students, [LEFT, RIGHT]):
            student.change_mode("confused")
            student.to_corner(DOWN+vect, buff = 2*MED_BUFF)
            student.look_at(v)
            student.bubble = get_small_bubble(
                student, height = 4, width = 4,
            )
        self.play(*map(FadeIn, students))
        self.play(Blink(physics_student))
        self.dither()
        for student, vect in zip(students, [RIGHT, LEFT]):
            for mob in v, coords:
                mob.target = mob.copy()
                mob.target.scale(0.7)
            arrow = TexMobject("\\Rightarrow")
            group = VGroup(v.target, arrow, coords.target)
            group.arrange_submobjects(vect)
            student.bubble.add_content(group)
            student.v, student.coords = v.copy(), coords.copy()
            student.arrow = arrow

            self.play(
                student.change_mode, "pondering",
                ShowCreation(student.bubble),
                Write(arrow),
                Transform(student.v, v.target),
                Transform(student.coords, coords.target),
            )
            self.play(Blink(student))
            self.dither()
        anims = []
        for student in students:
            v, coords = student.v, student.coords
            v.target = v.copy()
            coords.target = coords.copy()
            group = VGroup(v.target, coords.target)
            group.arrange_submobjects(DOWN)
            group.scale_to_fit_height(coords.get_height())
            group.next_to(student.arrow, RIGHT)
            student.q_marks = TexMobject("???")
            student.q_marks.gradient_highlight(BLUE, YELLOW)
            student.q_marks.next_to(student.arrow, LEFT)
            anims += [
                Write(student.q_marks),
                MoveToTarget(v),
                MoveToTarget(coords),
                student.change_mode, "erm",
                student.look_at, student.bubble
            ]
        cs_student.v.save_state()
        cs_student.coords.save_state()
        self.play(*anims)
        for student in students:
            self.play(Blink(student))
        self.dither()
        self.play(*it.chain(
            map(FadeOut, everything + [
                physics_student.bubble,
                physics_student.v,
                physics_student.coords,
                physics_student.arrow,
                physics_student.q_marks,
                cs_student.q_marks,
            ]),
            [ApplyMethod(s.change_mode, "plain") for s in students],
            map(Animation, [cs_student.bubble, cs_student.arrow]),
            [mob.restore for mob in cs_student.v, cs_student.coords],
        ))
        bubble = cs_student.get_bubble("speech", width = 4, height = 3)
        bubble.set_fill(BLACK, opacity = 1)
        bubble.next_to(cs_student, UP+LEFT)
        bubble.write("Consider higher \\\\ dimensions")
        self.play(
            cs_student.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(physics_student))
        self.dither()

class HigherDimensionalVectorsNumerically(Scene):
    def construct(self):
        words = VGroup(*map(TextMobject, [
            "4D vector", 
            "5D vector", 
            "100D vector", 
        ]))
        words.arrange_submobjects(RIGHT, buff = LARGE_BUFF*2)
        words.to_edge(UP)
        vectors = VGroup(*map(Matrix, [
            [3, 1, 4, 1],
            [5, 9, 2, 6, 5],
            [3, 5, 8, "\\vdots", 0, 8, 6]
        ]))
        colors = [YELLOW, MAROON_B, GREEN]
        for word, vector, color in zip(words, vectors, colors):
            vector.shift(word.get_center()[0]*RIGHT)
            word.highlight(color)
            vector.highlight(color)

        for word in words:
            self.play(FadeIn(word))
        self.play(Write(vectors))
        self.dither()
        for index, dim, direction in (0, 4, RIGHT), (2, 100, LEFT):
            v = vectors[index]
            v.target = v.copy()
            brace = Brace(v, direction)
            brace.move_to(v)
            v.target.next_to(brace, -direction)
            text = brace.get_text("%d numbers"%dim)            
            self.play(
                MoveToTarget(v),
                GrowFromCenter(brace),
                Write(text)
            )
            entries = v.get_entries()
            num_entries = len(list(entries))
            self.play(*[
                Transform(
                    entries[i],
                    entries[i].copy().scale_in_place(1.2).highlight(WHITE),
                    rate_func = squish_rate_func(
                        there_and_back, 
                        i/(2.*num_entries), 
                        i/(2.*num_entries)+0.5
                    ),
                    run_time = 2                    
                )
                for i in range(num_entries)
            ])
            self.dither()

class AskAbout4DCSStudent(Scene):
    def construct(self):
        cs_student = CSStudent().to_edge(DOWN).shift(2*RIGHT)
        asker = PiCreature(color = MAROON_D)
        asker.to_edge(DOWN).shift(2*LEFT)
        for pi1, pi2 in (cs_student, asker), (asker, cs_student):
            pi1.speech_bubble = pi1.get_bubble("speech")
            pi1.look_at(pi2.eyes)

        thought_bubble = get_small_bubble(cs_student)
        thought_bubble.rotate(-np.pi/6)
        thought_bubble.stretch_to_fit_height(4)
        thought_bubble.next_to(
            cs_student.get_corner(UP+RIGHT), UP, buff = 0
        )
        
        vector = Matrix([3, 1, 4, 1])
        vector.highlight(YELLOW)
        vector.scale_to_fit_height(2)
        thought_bubble.add_content(vector)
        thought_bubble.add(thought_bubble.content)
        asker.speech_bubble.write("""
            What is this ``4d space''
            you speak of?
        """)
        cs_student.speech_bubble.write(
            "The set of all",
            "ordered \\\\ quadruplets",
            "of real numbers",
        )
        cs_student.speech_bubble.content[1].highlight(YELLOW)
        for pi in asker, cs_student:
            pi.speech_bubble.add(pi.speech_bubble.content)

        self.add(asker, cs_student)
        self.play(
            asker.change_mode, "erm",
            Write(asker.speech_bubble),
        )
        self.play(Blink(cs_student))
        self.play(
            asker.change_mode, "plain",
            cs_student.change_mode, "speaking",
            FadeOut(asker.speech_bubble),
            Write(cs_student.speech_bubble),
        )
        self.play(
            asker.change_mode, "pondering",
            asker.look_at, thought_bubble,
            Write(thought_bubble)
        )
        self.play(Blink(asker))
        self.dither()

class HyperCube(VMobject):
    CONFIG = {
        "color" : BLUE_C,
        "color2" : BLUE_D, 
        "dims" : 4,
    }
    def generate_points(self):
        corners = np.array(map(np.array, it.product(*[(-1, 1)]*self.dims)))
        def project(four_d_array):
            result = four_d_array[:3]
            w = four_d_array[self.dims-1]
            scalar = interpolate(0.8, 1.2 ,(w+1)/2.)
            return scalar*result
        for a1, a2 in it.combinations(corners, 2):
            if sum(a1==a2) != self.dims-1:
                continue
            self.add(Line(project(a1), project(a2)))
        self.pose_at_angle()
        self.gradient_highlight(self.color, self.color2)

class AskAbout4DPhysicsStudent(Scene):
    def construct(self):
        physy = PhysicsStudent().flip().to_edge(DOWN).shift(2*RIGHT)
        asker = PiCreature(color = MAROON_D)
        asker.to_edge(DOWN).shift(2*LEFT)
        for pi1, pi2 in (physy, asker), (asker, physy):
            pi1.speech_bubble = pi1.get_bubble("speech")
            pi1.look_at(pi2.eyes)

        thought_bubble = get_small_bubble(physy)
        thought_bubble.rotate(-np.pi/6)
        thought_bubble.stretch_to_fit_height(5)
        thought_bubble.stretch_to_fit_width(4)
        thought_bubble.shift(RIGHT)
        thought_bubble.next_to(
            physy.get_corner(UP+RIGHT), UP, buff = 0
        )
        
        vector = Vector([1, 2])
        line = Line(LEFT, RIGHT, color = BLUE_B)
        square = Square(color = BLUE_C)
        cube = HyperCube(color = BLUE_D, dims = 3)
        hyper_cube = HyperCube()
        thought_mobs = vector, line, square, cube, hyper_cube
        for mob in thought_mobs:
            mob.scale_to_fit_height(2)
            thought_bubble.add_content(mob)
        square.scale_in_place(0.7)
        asker.speech_bubble.flip()
        asker.speech_bubble.stretch_to_fit_width(4.5)
        asker.speech_bubble.to_edge(LEFT)
        asker.speech_bubble.write("""
            Well, what do \\emph{you}
            think 4d space is?
        """)
        physy.speech_bubble.write("""
            Well, it's kind of like 
            3d space, but with another 
            dimension, you know?
        """)
        for pi in asker, physy:
            pi.speech_bubble.add(pi.speech_bubble.content)


        self.add(asker, physy, thought_bubble, vector)
        self.play(
            asker.change_mode, "sassy",
            Write(asker.speech_bubble),
        )
        self.play(Blink(physy))
        self.play(
            asker.change_mode, "plain",
            physy.change_mode, "hooray",
            FadeOut(asker.speech_bubble),
            Write(physy.speech_bubble),
        )
        self.play(
            asker.change_mode, "confused",
            asker.look_at, thought_bubble,
            physy.look_at, thought_bubble,
        )
        for mob in thought_mobs[1:]:
            self.play(Transform(vector, mob))
            self.remove(vector)
            vector = mob
            self.add(vector)
            self.dither()
        self.play(Blink(asker))
        asker.speech_bubble.remove(asker.speech_bubble.content)
        asker.speech_bubble.write("Is that real?")
        asker.speech_bubble.add(asker.speech_bubble.content)
        self.play(
            FadeOut(physy.speech_bubble),
            FadeOut(physy.speech_bubble),
            Write(asker.speech_bubble, run_time = 2),
            asker.change_mode, "sassy",
            physy.change_mode, "plain",
            physy.look_at, asker.eyes,
        )
        self.play(Blink(physy))
        self.dither()

class ManyCoordinateSystems(LinearTransformationScene):
    CONFIG = {
        "v_coords" : [2, 1],
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_WIDTH,
            "secondary_line_ratio" : 1
        },
    }
    def construct(self):
        self.title = TextMobject("Many possible coordinate systems")
        self.title.add_background_rectangle()
        self.title.to_edge(UP)
        self.add_foreground_mobject(self.title)
        self.v = Vector(self.v_coords)
        self.play(ShowCreation(self.v))
        self.add_foreground_mobject(self.v)

        t_matrices = [
            [[0.5, 0.5], [-0.5, 0.5]],
            [[1, -1], [-3, -1]],
            [[-1, 2], [-0.5, -1]],
        ]
        movers = [self.plane, self.i_hat, self.j_hat]
        for mover in movers:
            mover.save_state()
        for t_matrix in t_matrices:
            self.animate_coordinates()
            self.play(*it.chain(
                map(FadeOut, movers),
                map(Animation, self.foreground_mobjects)
            ))
            for mover in movers:
                mover.restore()
            self.apply_transposed_matrix(t_matrix, run_time = 0)
            self.play(*it.chain(
                map(FadeIn, movers),
                map(Animation, self.foreground_mobjects)
            ))
        self.animate_coordinates()


    def animate_coordinates(self):
        self.i_hat.save_state()
        self.j_hat.save_state()
        cob_matrix = np.array([
            self.i_hat.get_end()[:2],
            self.j_hat.get_end()[:2]
        ]).T
        inv_cob = np.linalg.inv(cob_matrix)
        coords = np.dot(inv_cob, self.v_coords)
        array = Matrix(map(DecimalNumber, coords))
        array.get_entries()[0].highlight(X_COLOR)
        array.get_entries()[1].highlight(Y_COLOR)
        array.add_to_back(BackgroundRectangle(array))
        for entry in array.get_entries():
            entry.add_to_back(BackgroundRectangle(entry))
        array.next_to(self.title, DOWN)

        self.i_hat.target = self.i_hat.copy().scale(coords[0])
        self.j_hat.target = self.j_hat.copy().scale(coords[1])
        coord1, coord2 = array.get_entries().copy()
        for coord, vect in (coord1, self.i_hat), (coord2, self.j_hat):
            coord.target = coord.copy().next_to(
                vect.target.get_end()/2, 
                rotate_vector(vect.get_end(), -np.pi/2)
            )

        self.play(Write(array, run_time = 1))
        self.dither()
        self.play(*map(MoveToTarget, [self.i_hat, coord1]))
        self.play(*map(MoveToTarget, [self.j_hat, coord2]))
        self.play(VGroup(self.j_hat, coord2).shift, self.i_hat.get_end())
        self.dither(2)
        self.play(
            self.i_hat.restore,
            self.j_hat.restore,
            *map(FadeOut, [array, coord1, coord2])
        )

class TransformationsWithCoordinates(ColumnsToBasisVectors):
    CONFIG = {
        "t_matrix" : [[3, 1], [1, 2]],
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_HEIGHT,
            "secondary_line_ratio" : 1
        },
    }
    def construct(self):
        self.setup()
        self.add_unit_square()
        eigenvectors = VGroup(*self.get_eigenvectors())
        
        for mob in self.square, eigenvectors:
            mob.set_fill(opacity = 0)
            mob.set_stroke(width = 0)

        det_word = TextMobject("Determinant")
        det_word.highlight(YELLOW)
        det_word.to_edge(UP)
        eigen_word = TextMobject("Eigenvectors")
        eigen_word.highlight(MAROON_B)
        eigen_word.next_to(det_word, DOWN, aligned_edge = LEFT)
        for word in det_word, eigen_word:
            word.add_background_rectangle()

        self.move_matrix_columns(self.t_matrix)
        faders = [self.matrix, self.i_coords, self.j_coords]
        self.play(*map(FadeOut, faders))
        FadeOut(VGroup(*faders)).update(1)
        self.play(
            Write(det_word, run_time = 2),
            self.square.set_fill, YELLOW, 0.3,
            self.square.set_stroke, YELLOW, DEFAULT_POINT_THICKNESS,
            *map(Animation, [self.i_hat, self.j_hat])
        )
        self.add_foreground_mobject(det_word)
        self.play(
            Write(eigen_word, run_time = 2),
            FadeIn(eigenvectors)
        )
        for eigenvector in eigenvectors:
            self.add_vector(eigenvector, animate = False)
        self.add_foreground_mobject(eigen_word)        
        self.apply_inverse_transpose(
            self.t_matrix, rate_func = there_and_back
        )
        self.dither()



    def get_eigenvectors(self):
        vals, (eig_matrix) = np.linalg.eig(self.t_matrix.T)
        v1, v2 = eig_matrix.T
        result = []
        for v in v1, v2:
            vectors = VGroup(*[
                Vector(u*x*v)
                for x in range(14, 0, -2)
                for u in -1, 1
            ])
            vectors.gradient_highlight(MAROON_B, YELLOW)
            result += list(vectors)
        return result

class NameDeterminantCopy(NameDeterminant):
    pass#

class NameEigenvectorsAndEigenvaluesCopy(ExampleTranformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "include_background_plane" : False,
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

        final_words = TextMobject("""
            Result doesn't care about 
            the coordinate system
        """)
        final_words.add_background_rectangle()
        final_words.to_corner(UP+RIGHT)

        for vectors in x_vectors, sneak_vectors:
            self.play(ShowCreation(vectors, run_time = 1))
        self.dither()
        for words in x_words, sneak_words:
            self.play(Write(words, run_time = 1.5))
            self.add_foreground_mobject(words)
            self.dither()
        self.dither()
        self.apply_transposed_matrix(
            self.t_matrix,
            path_arc = 0,
        )
        self.dither(2)
        self.play(*map(MoveToTarget, [x_words, sneak_words]))
        self.dither()
        for words in x_words, sneak_words:
            self.play(Write(words.eigen_val_words), run_time = 2)
            self.add_foreground_mobject(words.eigen_val_words)
            self.dither()
        fade_out = FadeOut(self.plane)
        self.play(fade_out, Write(final_words))
        fade_out.update(1)
        self.apply_inverse_transpose(
            self.t_matrix, 
            rate_func = there_and_back,
            path_arc = 0
        )

class ReallyWhatAreVectors(Scene):
    def construct(self):
        physy = PhysicsStudent()
        physy.thought = Vector([1, 2])
        physy.words = "Nature seems to \\\\ disagree with you"
        compy = CSStudent()
        compy.thought = Matrix([1, 2])
        compy.words = "How else could you \\\\ possibly define them?"
        for pi, vect in (physy, LEFT), (compy, RIGHT):
            pi.to_edge(DOWN)
            pi.shift(4*vect)
            pi.bubble = get_small_bubble(pi)
            pi.thought.highlight(YELLOW)
            pi.thought.scale_to_fit_height(2)
            pi.bubble.add_content(pi.thought)
            pi.bubble.add(pi.thought)

            pi.speech_bubble = pi.get_bubble("speech", width = 5)
            pi.speech_bubble.set_fill(BLACK, opacity = 1)
            pi.speech_bubble.write(pi.words)
            pi.speech_bubble.add(pi.speech_bubble.content)
            self.add(pi)
        physy.make_eye_contact(compy)

        hundred_d = Matrix(["3", "5", "\\vdots", "8", "6"])
        hundred_d.highlight(GREEN)
        hundred_d.scale_to_fit_height(compy.thought.get_height())
        hundred_d.move_to(compy.thought)

        double_speech = DoubleSpeechBubble(width = 6)
        double_speech.set_fill(BLACK, opacity = 1)
        double_speech.write("What \\emph{are} vectors???")
        double_speech.add(double_speech.content)
        double_speech.next_to(VGroup(compy, physy), UP)

        self.play(
            *[FadeIn(pi.bubble) for pi in physy, compy],
            run_time = 1
        )
        self.play(
            Write(physy.speech_bubble),
            physy.change_mode, "sassy"
        )
        self.play(Blink(compy))
        self.dither()
        self.play(
            FadeOut(physy.speech_bubble),
            Write(compy.speech_bubble),
            physy.change_mode, "pondering",
            compy.change_mode, "pleading"
        )
        self.play(Transform(compy.thought, hundred_d))
        self.play(Blink(physy))
        self.dither()
        self.play(
            FadeOut(compy.speech_bubble),
            Write(double_speech),
            compy.change_mode, "confused",
            physy.change_mode, "confused",
        )
        self.play(*map(Blink, [compy, physy]))
        self.dither()

class OtherVectorishThings(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "There are other\\\\",
            "vectorish",
            "things..."
        )
        words.highlight_by_tex("vectorish", YELLOW)
        self.teacher_says(words)
        self.change_student_modes(
            "pondering", "raise_right_hand", "erm"
        )
        self.random_blink(2)
        words = TextMobject("...like", "functions")
        words.highlight_by_tex("functions", PINK)
        self.teacher_says(words)
        self.change_student_modes(*["pondering"]*3)
        self.random_blink(2)
        self.teacher_thinks("")
        self.zoom_in_on_thought_bubble(self.get_teacher().bubble)

class FunctionGraphScene(Scene):
    CONFIG = {
        "graph_colors" : [MAROON_B, YELLOW, PINK],
        "default_functions" : [
            lambda x : (x**3 - 9*x)/10.,
            lambda x : (x**2)/8.-1
        ],
        "default_names" : ["f", "g", "h"],
        "x_min" : -4,
        "x_max" : 4,
        "line_to_line_buff" : 0.03
    }
    def setup(self):
        self.axes = Axes(
            x_min = self.x_min,
            x_max = self.x_max,
        )
        self.add(self.axes)
        self.graphs = []

    def get_function_graph(self, func = None, animate = True, 
                           add = True, **kwargs):
        index = len(self.graphs)
        if func is None:
            func = self.default_functions[
                index%len(self.default_functions)
            ]
        default_color = self.graph_colors[index%len(self.graph_colors)]
        kwargs["color"] = kwargs.get("color", default_color)
        kwargs["x_min"] = kwargs.get("x_min", self.x_min)
        kwargs["x_max"] = kwargs.get("x_max", self.x_max)
        graph = FunctionGraph(func, **kwargs)
        if animate:
            self.play(ShowCreation(graph))
        if add:
            self.add(graph)
        self.graphs.append(graph)
        return graph

    def get_index(self, function_graph):
        if function_graph not in self.graphs:
            self.graphs.append(function_graph)
        return self.graphs.index(function_graph)

    def get_output_lines(self, function_graph, num_steps = None, nudge = True):
        index = self.get_index(function_graph)
        num_steps = num_steps or function_graph.num_steps
        lines = VGroup()
        nudge_size = index*self.line_to_line_buff
        x_min, x_max = function_graph.x_min, function_graph.x_max
        for x in np.linspace(x_min, x_max, num_steps):
            if nudge:
                x += nudge_size
            y = function_graph.function(x)
            lines.add(Line(x*RIGHT, x*RIGHT+y*UP))
        lines.highlight(function_graph.get_color())
        return lines

    def add_lines(self, output_lines):
        self.play(ShowCreation(
            output_lines,
            submobject_mode = "lagged_start",
            run_time = 2
        ))


    def label_graph(self, function_graph, name = None, animate = True):
        index = self.get_index(function_graph)
        name = name or self.default_names[index%len(self.default_names)]
        label = TexMobject("%s(x)"%name)
        label.next_to(function_graph.point_from_proportion(1), RIGHT)
        label.shift_onto_screen()
        label.highlight(function_graph.get_color())
        if animate:
            self.play(Write(label))
        else:
            self.add(label)
        return label

class AddTwoFunctions(FunctionGraphScene):
    def construct(self):
        f_graph = self.get_function_graph()
        g_graph = self.get_function_graph()
        def sum_func(x):
            return f_graph.get_function()(x)+g_graph.get_function()(x)
        sum_graph = self.get_function_graph(sum_func, animate = False)
        self.remove(sum_graph)
        f_label = self.label_graph(f_graph)
        g_label = self.label_graph(g_graph)

        f_lines = self.get_output_lines(f_graph)
        g_lines = self.get_output_lines(g_graph)
        sum_lines = self.get_output_lines(sum_graph, nudge = False)
        for lines in f_lines, g_lines:
            self.add_lines(lines)
        self.play(*map(FadeOut, [f_graph, g_graph]))
        self.dither()

        curr_x_point = f_lines[0].get_start()
        sum_def = self.get_sum_definition(DecimalNumber(curr_x_point[0]))
        # sum_def.scale_to_fit_width(SPACE_WIDTH-1)
        sum_def.to_corner(UP+LEFT)
        arrow = Arrow(sum_def[2].get_bottom(), curr_x_point, color = WHITE)        
        prefix = sum_def[0]
        suffix = VGroup(*sum_def[1:])
        rect = BackgroundRectangle(sum_def)
        brace = Brace(prefix)
        brace.add(brace.get_text("New function").shift_onto_screen())

        self.play(
            Write(prefix, run_time = 2),
            FadeIn(brace)
        )
        self.dither()
        self.play(FadeOut(brace))
        fg_group = VGroup(*list(f_label)+list(g_label))
        self.play(
            FadeIn(rect),
            Animation(prefix),
            Transform(fg_group, suffix),
        )
        self.remove(prefix, fg_group)
        self.add(sum_def)
        self.play(ShowCreation(arrow))

        self.show_line_addition(f_lines[0], g_lines[0], sum_lines[0])
        self.dither()

        curr_x_point = f_lines[1].get_start()
        new_sum_def = self.get_sum_definition(DecimalNumber(curr_x_point[0]))
        new_sum_def.to_corner(UP+LEFT)
        new_arrow = Arrow(sum_def[2].get_bottom(), curr_x_point, color = WHITE)
        self.play(
            Transform(sum_def, new_sum_def),
            Transform(arrow, new_arrow),
        )
        self.show_line_addition(f_lines[1], g_lines[1], sum_lines[1])
        self.dither()

        final_sum_def = self.get_sum_definition(TexMobject("x"))
        final_sum_def.to_corner(UP+LEFT)
        self.play(
            FadeOut(rect),
            Transform(sum_def, final_sum_def),
            FadeOut(arrow)
        )
        self.show_line_addition(*it.starmap(VGroup, [
            f_lines[2:], g_lines[2:], sum_lines[2:]
        ]))
        self.play(ShowCreation(sum_graph))

    def get_sum_definition(self, input_mob):
        result = VGroup(*it.chain(
            TexMobject("(f+g)", "("), 
            [input_mob.copy()],
            TexMobject(")", "=", "f("),
            [input_mob.copy()],
            TexMobject(")", "+", "g("),
            [input_mob.copy()],
            TexMobject(")")
        ))
        result.arrange_submobjects()
        result[0].highlight(self.graph_colors[2])
        VGroup(result[5], result[7]).highlight(self.graph_colors[0])
        VGroup(result[9], result[11]).highlight(self.graph_colors[1])
        return result


    def show_line_addition(self, f_lines, g_lines, sum_lines):
        g_lines.target = g_lines.copy()
        dots = VGroup()
        dots.target = VGroup()
        for f_line, g_line in zip(f_lines, g_lines.target):
            align_perfectly = f_line.get_end()[1]*g_line.get_end()[1] > 0
            dot = Dot(g_line.get_end())
            g_line.shift(f_line.get_end()-g_line.get_start())
            dot.target = Dot(g_line.get_end())            
            if not align_perfectly:
                g_line.shift(self.line_to_line_buff*RIGHT)
            dots.add(dot)
            dots.target.add(dot.target)
        for group in dots, dots.target:
            group.highlight(sum_lines[0].get_color())
        self.play(ShowCreation(dots))
        if len(list(g_lines)) == 1:
            kwargs = {}
        else:
            kwargs = {
                "submobject_mode" : "lagged_start",
                "run_time" : 3
            }
        self.play(*[
            MoveToTarget(mob, **kwargs)
            for mob in g_lines, dots
        ])
        self.dither()
        # self.play(*map(FadeOut, [f_lines, g_lines]))
        # self.add_lines(sum_lines)
        # self.dither()

class AddVectorsCoordinateByCoordinate(Scene):
    def construct(self):
        v1 = Matrix(["x_1", "y_1", "z_1"])
        v2 = Matrix(["x_2", "y_2", "z_2"])
        v_sum =  Matrix(["x_1 + x_2", "y_1 + y_2", "z_1 + z_2"])
        for v in v1, v2, v_sum:
            v.get_entries()[0].highlight(X_COLOR)
            v.get_entries()[1].highlight(Y_COLOR)
            v.get_entries()[2].highlight(Z_COLOR)
        plus, equals = TexMobject("+=")
        VGroup(v1, plus, v2, equals, v_sum).arrange_submobjects()

        self.add(v1, plus, v2)
        self.dither()
        self.play(
            Write(equals),
            Write(v_sum.get_brackets())
        )
        self.play(
            Transform(v1.get_entries().copy(), v_sum.get_entries()),
            Transform(v2.get_entries().copy(), v_sum.get_entries()),
        )
        self.dither()

class ScaleFunction(FunctionGraphScene):
    def construct(self):
        graph = self.get_function_graph(
            lambda x : 0.7*self.default_functions[0](x),
            animate = False
        )
        scaled_graph = self.get_function_graph(
            lambda x : graph.get_function()(x)*2,
            animate = False, add = False
        )
        graph_lines = self.get_output_lines(graph)
        scaled_lines = self.get_output_lines(scaled_graph, nudge = False)

        f_label = self.label_graph(graph, "f", animate = False)
        two_f_label = self.label_graph(scaled_graph, "(2f)", animate = False)
        self.remove(two_f_label)

        title = TexMobject("(2f)", "(x) = 2", "f", "(x)")
        title.highlight_by_tex("(2f)", scaled_graph.get_color())
        title.highlight_by_tex("f", graph.get_color())
        title.next_to(ORIGIN, LEFT, buff = MED_BUFF)
        title.to_edge(UP)
        self.add(title)

        self.add_lines(graph_lines)
        self.dither()
        self.play(Transform(graph_lines, scaled_lines))
        self.play(ShowCreation(scaled_graph))
        self.play(Write(two_f_label))
        self.play(FadeOut(graph_lines))
        self.dither()

class ScaleVectorByCoordinates(Scene):
    def construct(self):
        two, dot, equals = TexMobject("2 \\cdot =")
        v1 = Matrix(list("xyz"))
        v1.get_entries().gradient_highlight(X_COLOR, Y_COLOR, Z_COLOR)
        v2 = v1.copy()
        two_targets = VGroup(*[
            two.copy().next_to(entry, LEFT)
            for entry in v2.get_entries()
        ])
        v2.get_brackets()[0].next_to(two_targets, LEFT)
        v2.add(two_targets)
        VGroup(two, dot, v1, equals, v2).arrange_submobjects()

        self.add(two, dot, v1)
        self.play(
            Write(equals),
            Write(v2.get_brackets())
        )
        self.play(
            Transform(two.copy(), two_targets),
            Transform(v1.get_entries().copy(), v2.get_entries())
        )
        self.dither()

class ShowSlopes(Animation):
    CONFIG = {
        "line_color" : YELLOW,
        "dx" : 0.01,
        "rate_func" : None,
        "run_time" : 5
    }
    def __init__(self, graph, **kwargs):
        digest_config(self, kwargs, locals())
        line = Line(LEFT, RIGHT, color = self.line_color)
        line.save_state()
        Animation.__init__(self, line, **kwargs)

    def update_mobject(self, alpha):
        f = self.graph.point_from_proportion        
        low, high = map(f, np.clip([alpha-self.dx, alpha+self.dx], 0, 1))
        slope = (high[1]-low[1])/(high[0]-low[0])
        self.mobject.restore()
        self.mobject.rotate(np.arctan(slope))
        self.mobject.move_to(f(alpha))

class FromVectorsToFunctions(VectorScene):
    def construct(self):
        self.show_vector_addition_and_scaling()
        self.bring_in_functions()
        self.show_derivative()

    def show_vector_addition_and_scaling(self):
        self.plane = self.add_plane()
        self.plane.fade()
        words1 = TextMobject("Vector", "addition")
        words2 = TextMobject("Vector", "scaling")
        for words in words1, words2:
            words.add_background_rectangle()
            words.next_to(ORIGIN, RIGHT).to_edge(UP)
        self.add(words1)

        v = self.add_vector([2, -1], color = MAROON_B)
        w = self.add_vector([3, 2], color = YELLOW)
        w.save_state()
        self.play(w.shift, v.get_end())
        vw_sum = self.add_vector(w.get_end(), color = PINK)
        self.dither()
        self.play(
            Transform(words1, words2),
            FadeOut(vw_sum),
            w.restore
        )
        self.add(
            v.copy().fade(),
            w.copy().fade()
        )
        self.play(v.scale, 2)
        self.play(w.scale, -0.5)
        self.dither()

    def bring_in_functions(self):
        everything = VGroup(*self.get_mobjects())
        axes = Axes()
        axes.shift(2*SPACE_WIDTH*LEFT)

        fg_scene_config = FunctionGraphScene.CONFIG
        graph = FunctionGraph(fg_scene_config["default_functions"][0])
        graph.highlight(MAROON_B)
        func_tex = TexMobject("\\frac{1}{9}x^3 - x")
        func_tex.highlight(graph.get_color())
        func_tex.shift(5.5*RIGHT+2*UP)

        words = VGroup(*[
            TextMobject(words).add_background_rectangle()
            for words in [
                "Linear transformations",
                "Null space",
                "Dot products",
                "Eigen-everything",
            ]
        ])
        words.gradient_highlight(BLUE_B, BLUE_D)
        words.arrange_submobjects(DOWN, aligned_edge = LEFT)
        words.to_corner(UP+LEFT)
        self.play(FadeIn(
            words,
            submobject_mode = "lagged_start",
            run_time = 3
        ))
        self.dither()
        self.play(*[
            ApplyMethod(mob.shift, 2*SPACE_WIDTH*RIGHT)
            for mob in axes, everything
        ] + [Animation(words)]
        )
        self.play(ShowCreation(graph), Animation(words))
        self.play(Write(func_tex, run_time = 2))
        self.dither(2)

        top_word = words[0]
        words.remove(top_word)
        self.play(
            FadeOut(words),
            top_word.shift, top_word.get_center()[0]*LEFT
        )
        self.dither()
        self.func_tex = func_tex
        self.graph = graph

    def show_derivative(self):
        func_tex, graph = self.func_tex, self.graph
        new_graph = FunctionGraph(lambda x : (x**2)/3.-1)
        new_graph.highlight(YELLOW)

        func_tex.generate_target()
        lp, rp = parens = TexMobject("()")
        parens.scale_to_fit_height(func_tex.get_height())
        L, equals = TexMobject("L=")
        deriv = TexMobject("\\frac{d}{dx}")
        new_func = TexMobject("\\frac{1}{3}x^2 - 1")
        new_func.highlight(YELLOW)
        group = VGroup(
            L, lp, func_tex.target, rp,
            equals, new_func
        )
        group.arrange_submobjects()
        group.shift(2*UP).to_edge(LEFT, buff = 2*MED_BUFF)
        rect = BackgroundRectangle(group)
        group.add_to_back(rect)
        deriv.move_to(L, aligned_edge = RIGHT)

        self.play(
            MoveToTarget(func_tex),
            *map(Write, [L, lp, rp, equals, new_func])
        )
        self.remove(func_tex)
        self.add(func_tex.target)
        self.dither()
        faded_graph = graph.copy().fade()
        self.add(faded_graph)
        self.play(
            Transform(graph, new_graph, run_time = 2),
            Animation(group)
        )
        self.dither()
        self.play(Transform(L, deriv))
        self.play(ShowSlopes(faded_graph))
        self.dither()

class WhatDoesLinearMean(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("""
            What does it mean for
            a transformation of functions
            to be """, "linear", "?",
            arg_separator = ""
        )
        words.highlight_by_tex("linear", BLUE)
        self.student_says(words)
        self.change_student_modes("pondering")
        self.random_blink(4)






































