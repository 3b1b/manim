from manimlib.imports import *
from functools import reduce

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
        words.set_width(FRAME_WIDTH - 2)
        words.to_edge(UP)
        words.split()[0].set_color(YELLOW)
        words.split()[2].set_color(YELLOW)

        three_d = words.submobjects.pop()
        three_d.set_color(BLUE)
        self.play(FadeIn(words))
        self.play(Write(three_d))
        self.wait(2)

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
        self.wait()
        student = self.get_students()[0]
        self.student_thinks(student_index = 0)
        student.bubble.make_green_screen()
        self.wait()

class SymbolicThreeDTransform(Scene):
    CONFIG = {
        "input_coords" : [2, 6, -1],
        "output_coords" : [3, 2, 0],
        "title" : "Three-dimensional transformation",
    }
    def construct(self):
        in_vect = Matrix(self.input_coords)
        out_vect = Matrix(self.output_coords)
        in_vect.set_color(BLUE)
        out_vect.set_color(GREEN)
        func = TexMobject("L(\\vec{\\textbf{v}})")
        point = VectorizedPoint(func.get_center())
        in_vect.next_to(func, LEFT, buff = 1)
        out_vect.next_to(func, RIGHT, buff = 1)
        in_words = TextMobject("Input")
        in_words.next_to(in_vect, DOWN)
        in_words.set_color(BLUE_C)
        out_words = TextMobject("Output")
        out_words.next_to(out_vect, DOWN)
        out_words.set_color(GREEN_C)


        title = TextMobject(self.title)
        title.to_edge(UP)
        self.add(title)

        self.play(Write(func))
        self.play(Write(in_vect), Write(in_words))
        self.wait()
        self.add(in_vect.copy())
        self.play(Transform(in_vect, point, lag_ratio = 0.5))
        self.play(Transform(in_vect, out_vect, lag_ratio = 0.5))
        self.add(out_words)
        self.wait()

class ThreeDLinearTransformExample(Scene):
    pass

class SingleVectorToOutput(Scene):
    pass

class InputWordOutputWord(Scene):
    def construct(self):
        self.add(TextMobject("Input").scale(2))
        self.wait()
        self.clear()
        self.add(TextMobject("Output").scale(2))
        self.wait()

class TransformOnlyBasisVectors(Scene):
    pass

class IHatJHatKHatWritten(Scene):
    def construct(self):
        for char, color in zip(["\\imath", "\\jmath", "k"], [X_COLOR, Y_COLOR, Z_COLOR]):
            sym = TexMobject("{\\hat{%s}}"%char)
            sym.scale(3)
            sym.set_color(color)
            self.play(Write(sym))
            self.wait()
            self.clear()
 
class PutTogether3x3Matrix(Scene):
    CONFIG = {
        "col1" : [1, 0, -1],
        "col2" : [1, 1, 0],
        "col3" : [1, 0, 1],
    }
    def construct(self):
        i_to = TexMobject("\\hat{\\imath} \\to").set_color(X_COLOR)
        j_to = TexMobject("\\hat{\\jmath} \\to").set_color(Y_COLOR)
        k_to = TexMobject("\\hat{k} \\to").set_color(Z_COLOR)
        i_array = Matrix(self.col1)
        j_array = Matrix(self.col2)
        k_array = Matrix(self.col3)
        everything = VMobject(
            i_to, i_array, TexMobject("=").set_color(BLACK),
            j_to, j_array, TexMobject("=").set_color(BLACK),
            k_to, k_array, TexMobject("=").set_color(BLACK),
        )
        everything.arrange(RIGHT, buff = 0.1)
        everything.set_width(FRAME_WIDTH-1)
        everything.to_edge(DOWN)

        i_array.set_color(X_COLOR)
        j_array.set_color(Y_COLOR)
        k_array.set_color(Z_COLOR)
        arrays = [i_array, j_array, k_array]
        matrix = Matrix(reduce(
            lambda a1, a2 : np.append(a1, a2, axis = 1),
            [m.copy().get_mob_matrix() for m in arrays]
        ))
        matrix.to_edge(DOWN)

        start_entries = reduce(op.add, [a.get_entries().split() for a in arrays])
        target_entries = matrix.get_mob_matrix().transpose().flatten()
        start_l_bracket = i_array.get_brackets().split()[0]
        start_r_bracket = k_array.get_brackets().split()[1]
        start_brackets = VMobject(start_l_bracket, start_r_bracket)
        target_bracketes = matrix.get_brackets()

        for mob in everything.split():
            self.play(Write(mob, run_time = 1))
        self.wait()
        self.play(
            FadeOut(everything),
            Transform(VMobject(*start_entries), VMobject(*target_entries)),
            Transform(start_brackets, target_bracketes)
        )
        self.wait()

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
        v.set_color(YELLOW)
        eq = TexMobject("=")
        coords = Matrix(["x", "y", "z"])
        eq2 = eq.copy()
        if self.post_transform:
            L, l_paren, r_paren = list(map(TexMobject, "L()"))
            parens = VMobject(l_paren, r_paren)
            parens.scale(2)
            parens.stretch_to_fit_height(
                coords.get_height()
            )
            VMobject(L, l_paren, coords, r_paren).arrange(buff = 0.1)
            coords.submobjects = [L, l_paren] + coords.submobjects + [r_paren]

        lin_comb = VMobject(*list(map(TexMobject, [
            "x", self.i_str, "+",
            "y", self.j_str, "+",
            "z", self.k_str,
        ])))
        lin_comb.arrange(
            RIGHT, buff = 0.1, 
            aligned_edge = ORIGIN if self.post_transform else DOWN
        )
        lin_comb_parts = np.array(lin_comb.split())
        new_x, new_y, new_z = lin_comb_parts[[0, 3, 6]]
        i, j, k = lin_comb_parts[[1, 4, 7]]
        plusses = lin_comb_parts[[2, 5]]
        i.set_color(X_COLOR)
        j.set_color(Y_COLOR)
        k.set_color(Z_COLOR)

        everything = VMobject(v, eq, coords, eq2, lin_comb)
        everything.arrange(buff = 0.2)
        everything.set_width(FRAME_WIDTH - 1)
        everything.to_edge(DOWN)
        if not self.post_transform:
            lin_comb.shift(0.35*UP)

        self.play(*list(map(Write, [v, eq, coords])))
        self.wait()
        self.play(
            Transform(
                coords.get_entries().copy(),
                VMobject(new_x, new_y, new_z),
                path_arc = -np.pi,
                lag_ratio = 0.5
            ),
            Write(VMobject(*[eq2, i, j, k] + list(plusses))),
            run_time = 3
        )
        self.wait()

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
        vect.set_height(matrix.get_height())
        col1, col2, col3 = columns = [
            Matrix(col)
            for col in matrix.copy().get_mob_matrix().transpose()
        ]
        coords = x, y, z = [m.copy() for m in vect.get_entries().split()]
        eq, plus1, plus2 = list(map(TexMobject, list("=++")))
        everything = VMobject(
            matrix, vect, eq,
            x, col1, plus1,
            y, col2, plus2,
            z, col3
        )
        everything.arrange(buff = 0.1)
        everything.set_width(FRAME_WIDTH-1)
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


        self.play(*list(map(Write, [matrix, vect])), run_time = 2)
        self.play(Write(matrix_brace, run_time = 1))
        self.play(Write(vect_brace, run_time = 1))
        sexts = list(zip(
            matrix.get_mob_matrix().transpose(),
            columns,
            vect.get_entries().split(),
            coords,
            [eq, plus1, plus2],
            [X_COLOR, Y_COLOR, Z_COLOR]
        ))
        for o_col, col, start_coord, coord, sym, color in sexts:
            o_col = VMobject(*o_col)
            self.play(
                start_coord.set_color, YELLOW,
                o_col.set_color, color
            )
            coord.set_color(YELLOW)
            col.set_color(color)
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
            self.wait()
        self.play(Write(result_brace, run_time = 1))
        self.wait()

class ShowMatrixMultiplication(Scene):
    def construct(self):
        right = Matrix(np.arange(9).reshape((3, 3)))
        left = Matrix(np.random.random_integers(-5, 5, (3, 3)))
        VMobject(left, right).arrange(buff = 0.1)
        right.set_column_colors(X_COLOR, Y_COLOR, Z_COLOR)
        left.set_color(PINK)

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

        VMobject(*self.get_mobjects()).set_width(FRAME_WIDTH-1)

        self.add(right, left)
        self.play(Write(right_brace))
        self.play(Write(left_brace))
        self.wait()

class ApplyTwoSuccessiveTransforms(Scene):
    pass

class ComputerGraphicsAndRobotics(Scene):
    def construct(self):
        mob = VMobject(
            TextMobject("Computer graphics"),
            TextMobject("Robotics")
        )
        mob.arrange(DOWN, buff = 1)
        self.play(Write(mob, run_time = 1))
        self.wait()

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
        title.set_color(YELLOW).to_edge(UP)
        self.add(title)
        questions = VMobject(*list(map(TextMobject, [
            "1. Can you visualize these transformations?",
            "2. Can you represent them with matrices?",
            "3. How many rows and columns?",
            "4. When can you multiply these matrices?",
        ])))
        questions.arrange(DOWN, buff = 1, aligned_edge = LEFT)
        questions.to_edge(LEFT)
        for question in questions.split():
            self.play(Write(question, run_time = 1))
            self.wait()

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: The determinant
        """)
        title.set_width(FRAME_WIDTH - 2)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()  


















