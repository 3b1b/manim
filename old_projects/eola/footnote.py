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

from topics.matrix import *
from topics.vector_space_scene import *

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject([
            "Lisa:",
            "Well, where's my dad?\\\\ \\\\",
            "Frink:",
            """Well, it should be obvious to even the most 
            dimwitted individual who holds an advanced degree 
            in hyperbolic topology that Homer Simpson has stumbled
            into...(dramatic pause)...""",
            "the third dimension."
        ])
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words.split()[0].highlight(YELLOW)
        words.split()[2].highlight(YELLOW)

        three_d = words.submobjects.pop()
        three_d.highlight(BLUE)
        self.play(FadeIn(words))
        self.play(Write(three_d))
        self.dither(2)

class QuickFootnote(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Quick footnote here...")
        self.random_blink()
        self.play(
            random.choice(self.get_students()).change_mode, "happy"
        )
        self.random_blink()

class PeakOutsideFlatland(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Peak outside flatland")
        self.dither()
        student = self.get_students()[0]
        self.student_thinks(student_index = 0)
        student.bubble.make_green_screen()
        self.dither()

class SymbolicThreeDTransform(Scene):
    CONFIG = {
        "input_coords" : [2, 6, -1],
        "output_coords" : [3, 2, 0],
        "title" : "Three-dimensional transformation",
    }
    def construct(self):
        in_vect = Matrix(self.input_coords)
        out_vect = Matrix(self.output_coords)
        in_vect.highlight(BLUE)
        out_vect.highlight(GREEN)
        func = TexMobject("L(\\vec{\\textbf{v}})")
        point = VectorizedPoint(func.get_center())
        in_vect.next_to(func, LEFT, buff = 1)
        out_vect.next_to(func, RIGHT, buff = 1)
        in_words = TextMobject("Input")
        in_words.next_to(in_vect, DOWN)
        in_words.highlight(BLUE_C)
        out_words = TextMobject("Output")
        out_words.next_to(out_vect, DOWN)
        out_words.highlight(GREEN_C)


        title = TextMobject(self.title)
        title.to_edge(UP)
        self.add(title)

        self.play(Write(func))
        self.play(Write(in_vect), Write(in_words))
        self.dither()
        self.add(in_vect.copy())
        self.play(Transform(in_vect, point, submobject_mode = "lagged_start"))
        self.play(Transform(in_vect, out_vect, submobject_mode = "lagged_start"))
        self.add(out_words)
        self.dither()

class ThreeDLinearTransformExample(Scene):
    pass

class SingleVectorToOutput(Scene):
    pass

class InputWordOutputWord(Scene):
    def construct(self):
        self.add(TextMobject("Input").scale(2))
        self.dither()
        self.clear()
        self.add(TextMobject("Output").scale(2))
        self.dither()

class TransformOnlyBasisVectors(Scene):
    pass

class IHatJHatKHatWritten(Scene):
    def construct(self):
        for char, color in zip(["\\imath", "\\jmath", "k"], [X_COLOR, Y_COLOR, Z_COLOR]):
            sym = TexMobject("{\\hat{%s}}"%char)
            sym.scale(3)
            sym.highlight(color)
            self.play(Write(sym))
            self.dither()
            self.clear()
 
class PutTogether3x3Matrix(Scene):
    CONFIG = {
        "col1" : [1, 0, -1],
        "col2" : [1, 1, 0],
        "col3" : [1, 0, 1],
    }
    def construct(self):
        i_to = TexMobject("\\hat{\\imath} \\to").highlight(X_COLOR)
        j_to = TexMobject("\\hat{\\jmath} \\to").highlight(Y_COLOR)
        k_to = TexMobject("\\hat{k} \\to").highlight(Z_COLOR)
        i_array = Matrix(self.col1)
        j_array = Matrix(self.col2)
        k_array = Matrix(self.col3)
        everything = VMobject(
            i_to, i_array, TexMobject("=").highlight(BLACK),
            j_to, j_array, TexMobject("=").highlight(BLACK),
            k_to, k_array, TexMobject("=").highlight(BLACK),
        )
        everything.arrange_submobjects(RIGHT, buff = 0.1)
        everything.scale_to_fit_width(2*SPACE_WIDTH-1)
        everything.to_edge(DOWN)

        i_array.highlight(X_COLOR)
        j_array.highlight(Y_COLOR)
        k_array.highlight(Z_COLOR)
        arrays = [i_array, j_array, k_array]
        matrix = Matrix(reduce(
            lambda a1, a2 : np.append(a1, a2, axis = 1),
            [m.copy().get_mob_matrix() for m in arrays]
        ))
        matrix.to_edge(DOWN)

        start_entries = reduce(op.add, map(
            lambda a : a.get_entries().split(),
            arrays
        ))
        target_entries = matrix.get_mob_matrix().transpose().flatten()
        start_l_bracket = i_array.get_brackets().split()[0]
        start_r_bracket = k_array.get_brackets().split()[1]
        start_brackets = VMobject(start_l_bracket, start_r_bracket)
        target_bracketes = matrix.get_brackets()

        for mob in everything.split():
            self.play(Write(mob, run_time = 1))
        self.dither()
        self.play(
            FadeOut(everything),
            Transform(VMobject(*start_entries), VMobject(*target_entries)),
            Transform(start_brackets, target_bracketes)
        )
        self.dither()

class RotateSpaceAboutYAxis(Scene):
    pass

class RotateOnlyBasisVectorsAboutYAxis(Scene):
    pass

class PutTogetherRotationMatrix(PutTogether3x3Matrix):
    CONFIG = {
        "col1" : [0, 0, -1],
        "col2" : [0, 1, 0],
        "col3" : [1, 0, 0]
    }

class ScaleAndAddBeforeTransformation(Scene):
    pass

class ShowVCoordinateMeaning(Scene):
    CONFIG = {
        "v_str" : "\\vec{\\textbf{v}}",
        "i_str" : "\\hat{\\imath}",
        "j_str" : "\\hat{\\jmath}",
        "k_str" : "\\hat{k}",
        "post_transform" : False,
    }
    def construct(self):
        v = TexMobject(self.v_str)
        v.highlight(YELLOW)
        eq = TexMobject("=")
        coords = Matrix(["x", "y", "z"])
        eq2 = eq.copy()
        if self.post_transform:
            L, l_paren, r_paren = map(TexMobject, "L()")
            parens = VMobject(l_paren, r_paren)
            parens.scale(2)
            parens.stretch_to_fit_height(
                coords.get_height()
            )
            VMobject(L, l_paren, coords, r_paren).arrange_submobjects(buff = 0.1)
            coords.submobjects = [L, l_paren] + coords.submobjects + [r_paren]

        lin_comb = VMobject(*map(TexMobject, [
            "x", self.i_str, "+",
            "y", self.j_str, "+",
            "z", self.k_str,
        ]))
        lin_comb.arrange_submobjects(
            RIGHT, buff = 0.1, 
            aligned_edge = ORIGIN if self.post_transform else DOWN
        )
        lin_comb_parts = np.array(lin_comb.split())
        new_x, new_y, new_z = lin_comb_parts[[0, 3, 6]]
        i, j, k = lin_comb_parts[[1, 4, 7]]
        plusses = lin_comb_parts[[2, 5]]
        i.highlight(X_COLOR)
        j.highlight(Y_COLOR)
        k.highlight(Z_COLOR)

        everything = VMobject(v, eq, coords, eq2, lin_comb)
        everything.arrange_submobjects(buff = 0.2)
        everything.scale_to_fit_width(2*SPACE_WIDTH - 1)
        everything.to_edge(DOWN)
        if not self.post_transform:
            lin_comb.shift(0.35*UP)

        self.play(*map(Write, [v, eq, coords]))
        self.dither()
        self.play(
            Transform(
                coords.get_entries().copy(),
                VMobject(new_x, new_y, new_z),
                path_arc = -np.pi,
                submobject_mode = "lagged_start"
            ),
            Write(VMobject(*[eq2, i, j, k] + list(plusses))),
            run_time = 3
        )
        self.dither()

class ScaleAndAddAfterTransformation(Scene):
    pass

class ShowVCoordinateMeaningAfterTransform(ShowVCoordinateMeaning):
    CONFIG = {
        "v_str" : "L(\\vec{\\textbf{v}})",
        "i_str" : "L(\\hat{\\imath})",
        "j_str" : "L(\\hat{\\jmath})",
        "k_str" : "L(\\hat{k})",
        "post_transform" : True,
    }

class ShowMatrixVectorMultiplication(Scene):
    def construct(self):
        matrix = Matrix(np.arange(9).reshape((3, 3)))
        vect = Matrix(list("xyz"))
        vect.scale_to_fit_height(matrix.get_height())
        col1, col2, col3 = columns = [
            Matrix(col)
            for col in matrix.copy().get_mob_matrix().transpose()
        ]
        coords = x, y, z = [m.copy() for m in vect.get_entries().split()]
        eq, plus1, plus2 = map(TexMobject, list("=++"))
        everything = VMobject(
            matrix, vect, eq,
            x, col1, plus1,
            y, col2, plus2,
            z, col3
        )
        everything.arrange_submobjects(buff = 0.1)
        everything.scale_to_fit_width(2*SPACE_WIDTH-1)
        result = VMobject(x, col1, plus1, y, col2, plus2, z, col3)

        trips = [
            (matrix, DOWN, "Transformation"),
            (vect, UP, "Input vector"),
            (result, DOWN, "Output vector"),
        ]
        braces = []
        for mob, direction, text in trips:
            brace = Brace(mob, direction)
            words = TextMobject(text)
            words.next_to(brace, direction)
            brace.add(words)
            braces.append(brace)
        matrix_brace, vect_brace, result_brace = braces


        self.play(*map(Write, [matrix, vect]), run_time = 2)
        self.play(Write(matrix_brace, run_time = 1))
        self.play(Write(vect_brace, run_time = 1))
        sexts = zip(
            matrix.get_mob_matrix().transpose(),
            columns,
            vect.get_entries().split(),
            coords,
            [eq, plus1, plus2],
            [X_COLOR, Y_COLOR, Z_COLOR]
        )
        for o_col, col, start_coord, coord, sym, color in sexts:
            o_col = VMobject(*o_col)
            self.play(
                start_coord.highlight, YELLOW,
                o_col.highlight, color
            )
            coord.highlight(YELLOW)
            col.highlight(color)
            self.play(
                Write(col.get_brackets()),
                Transform(
                    o_col.copy(), col.get_entries(),
                    path_arc = -np.pi
                ),
                Transform(
                    start_coord.copy(), coord, 
                    path_arc = -np.pi
                ),
                Write(sym)
            )
            self.dither()
        self.play(Write(result_brace, run_time = 1))
        self.dither()

class ShowMatrixMultiplication(Scene):
    def construct(self):
        right = Matrix(np.arange(9).reshape((3, 3)))
        left = Matrix(np.random.random_integers(-5, 5, (3, 3)))
        VMobject(left, right).arrange_submobjects(buff = 0.1)
        right.highlight_columns(X_COLOR, Y_COLOR, Z_COLOR)
        left.highlight(PINK)

        trips = [
            (right, DOWN, "First transformation"),
            (left, UP, "Second transformation"),
        ]
        braces = []
        for mob, direction, text in trips:
            brace = Brace(mob, direction)
            words = TextMobject(text)
            words.next_to(brace, direction)
            brace.add(words)
            braces.append(brace)
        right_brace, left_brace = braces

        VMobject(*self.get_mobjects()).scale_to_fit_width(2*SPACE_WIDTH-1)

        self.add(right, left)
        self.play(Write(right_brace))
        self.play(Write(left_brace))
        self.dither()

class ApplyTwoSuccessiveTransforms(Scene):
    pass

class ComputerGraphicsAndRobotics(Scene):
    def construct(self):
        mob = VMobject(
            TextMobject("Computer graphics"),
            TextMobject("Robotics")
        )
        mob.arrange_submobjects(DOWN, buff = 1)
        self.play(Write(mob, run_time = 1))
        self.dither()

class ThreeDRotation(Scene):
    pass

class ThreeDRotationBrokenUp(Scene):
    pass

class SymbolicTwoDToThreeDTransform(SymbolicThreeDTransform):
    CONFIG = {
        "input_coords" : [2, 6],
        "output_coords" : [3, 2, 0],
        "title" : "Two dimensions to three dimensions",
    }

class SymbolicThreeDToTwoDTransform(SymbolicThreeDTransform):
    CONFIG = {
        "input_coords" : [4, -3, 1],
        "output_coords" : [8, 4],
        "title" : "Three dimensions to two dimensions",
    }

class QuestionsToPonder(Scene):
    def construct(self):
        title = TextMobject("Questions to ponder")
        title.highlight(YELLOW).to_edge(UP)
        self.add(title)
        questions = VMobject(*map(TextMobject, [
            "1. Can you visualize these transformations?",
            "2. Can you represent them with matrices?",
            "3. How many rows and columns?",
            "4. When can you multiply these matrices?",
        ]))
        questions.arrange_submobjects(DOWN, buff = 1, aligned_edge = LEFT)
        questions.to_edge(LEFT)
        for question in questions.split():
            self.play(Write(question, run_time = 1))
            self.dither()

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: The determinant
        """)
        title.scale_to_fit_width(2*SPACE_WIDTH - 2)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.scale_to_fit_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.dither()  


















