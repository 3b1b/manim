from manimlib.imports import *
from old_projects.eola.chapter3 import MatrixVectorMultiplicationAbstract


class Blob(Circle):
    CONFIG = {
        "stroke_color" : TEAL,
        "fill_color" : BLUE_E,
        "fill_opacity" : 1,
        "random_seed" : 1,
        "random_nudge_size" : 0.5,
        "height" : 2,
    }
    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)
        random.seed(self.random_seed)
        self.apply_complex_function(
            lambda z : z*(1+self.random_nudge_size*(random.random()-0.5))
        )
        self.set_height(self.height).center()

    def probably_contains(self, point):
        border_points = np.array(self.get_anchors_and_handles()[0])
        distances = [get_norm(p-point) for p in border_points]
        min3 = border_points[np.argsort(distances)[:3]]
        center_direction = self.get_center() - point
        in_center_direction = [np.dot(p-point, center_direction) > 0 for p in min3]
        return sum(in_center_direction) <= 2
            
class RightHand(VMobject):
    def __init__(self, **kwargs):
        hand = SVGMobject("RightHandOutline")
        self.inlines = VMobject(*hand.split()[:-4])
        self.outline = VMobject(*hand.split()[-4:])
        self.outline.set_stroke(color = WHITE, width = 5)
        self.inlines.set_stroke(color = DARK_GREY, width = 3)
        VMobject.__init__(self, self.outline, self.inlines)
        self.center().set_height(3)

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject([
            "``The purpose of computation is \\\\",
            "insight",
            ", not ",
            "numbers.",
            "''",
        ], arg_separator = "")
        # words.set_width(FRAME_WIDTH - 2)
        words.to_edge(UP)
        words.split()[1].set_color(BLUE)
        words.split()[3].set_color(GREEN)
        author = TextMobject("-Richard Hamming")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(2)
        self.play(Write(author, run_time = 3))
        self.wait()

class MovingForward(TeacherStudentsScene):
    def construct(self):
        self.setup()
        student = self.get_students()[1]
        bubble = student.get_bubble(direction = RIGHT, width = 5)
        bubble.rotate(-np.pi/12)
        bubble.next_to(student, UP, aligned_edge = RIGHT)
        bubble.shift(0.5*LEFT)
        bubble.make_green_screen()

        self.teacher_says("""
            Y'all know about linear
            transformations, right?
        """, width = 7)
        self.play(
            ShowCreation(bubble),
            student.change_mode, "pondering"
        )
        self.wait(2)

class StretchingTransformation(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_title("Generally stretches space")
        self.apply_transposed_matrix([[3, 1], [-1, 2]])
        self.wait()

class SquishingTransformation(LinearTransformationScene):
    CONFIG = {
        "foreground_plane_kwargs" : {
            "x_radius" : 3*FRAME_X_RADIUS,
            "y_radius" : 3*FRAME_X_RADIUS,
            "secondary_line_ratio" : 0
        },
    }
    def construct(self):
        self.setup()
        self.add_title("Generally squishes space")
        self.apply_transposed_matrix([[1./2, -0.5], [1, 1./3]])
        self.wait()

class AskAboutStretching(LinearTransformationScene):
    def construct(self):
        self.setup()
        words = TextMobject("""
            Exactly how much are 
            things being stretched?
        """)
        words.add_background_rectangle()
        words.to_corner(UP+RIGHT)
        words.set_color(YELLOW)
        self.apply_transposed_matrix(
            [[2, 1], [-1, 3]],
            added_anims = [Write(words)]
        )
        self.wait()

class AskAboutStretchingSpecifically(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_title(["How much are", "areas", "scaled?"])
        hma, areas, scaled = self.title.split()[1].split()
        areas.set_color(YELLOW)
        blob = Blob().shift(UP+RIGHT)

        label = TextMobject("Area")
        label.set_color(YELLOW)
        label = VMobject(VectorizedPoint(label.get_left()), label)
        label.move_to(blob)
        target_label = TexMobject(["c \\cdot", "\\text{Area}"])
        target_label.split()[1].set_color(YELLOW)

        self.add_transformable_mobject(blob)
        self.add_moving_mobject(label, target_label)
        self.wait()
        self.apply_transposed_matrix([[2, -1], [1, 1]])
        arrow = Arrow(scaled, label.target.split()[0])
        self.play(ShowCreation(arrow))
        self.wait()

class BeautyNowUsesLater(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Beauty now, uses later")
        self.wait()

class DiagonalExample(LinearTransformationScene):
    CONFIG = {
        "show_square" : False, 
        "show_coordinates" : True,
        "transposed_matrix" : [[3, 0], [0, 2]]
    }
    def construct(self):
        self.setup()
        matrix = Matrix(np.array(self.transposed_matrix).transpose())
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(ORIGIN, LEFT).to_edge(UP)
        matrix_background = BackgroundRectangle(matrix)
        self.play(ShowCreation(matrix_background), Write(matrix))
        if self.show_square:
            self.add_unit_square(animate = True)
        self.add_foreground_mobject(matrix_background, matrix)
        self.wait()
        self.apply_transposed_matrix([self.transposed_matrix[0], [0, 1]])
        self.apply_transposed_matrix([[1, 0], self.transposed_matrix[1]])
        self.wait()
        if self.show_square:


            bottom_brace = Brace(self.i_hat, DOWN)
            right_brace = Brace(self.square, RIGHT)
            width = TexMobject(str(self.transposed_matrix[0][0]))
            height = TexMobject(str(self.transposed_matrix[1][1]))
            width.next_to(bottom_brace, DOWN)
            height.next_to(right_brace, RIGHT)
            for mob in bottom_brace, width, right_brace, height:
                mob.add_background_rectangle()
                self.play(Write(mob, run_time = 0.5))
            self.wait()

            width_target, height_target = width.copy(), height.copy()
            det = np.linalg.det(self.transposed_matrix)
            times, eq_det = list(map(TexMobject, ["\\times", "=%d"%det]))
            words = TextMobject("New area $=$")
            equation = VMobject(
                words, width_target, times, height_target, eq_det
            )
            equation.arrange(RIGHT, buff = 0.2)
            equation.next_to(self.square, UP, aligned_edge = LEFT)
            equation.shift(0.5*RIGHT)
            background_rect = BackgroundRectangle(equation)

            self.play(
                ShowCreation(background_rect),                
                Transform(width.copy(), width_target),
                Transform(height.copy(), height_target),
                *list(map(Write, [words, times, eq_det]))
            )
            self.wait()

class DiagonalExampleWithSquare(DiagonalExample):
    CONFIG = {
        "show_square" : True
    }

class ShearExample(DiagonalExample):
    CONFIG = {
        "show_square" : False, 
        "show_coordinates" : True,
        "transposed_matrix" : [[1, 0], [1, 1]]
    }

class ShearExampleWithSquare(DiagonalExample):
    CONFIG = {
        "show_square" : True, 
        "show_coordinates" : True,
        "show_coordinates" : False,
        "transposed_matrix" : [[1, 0], [1, 1]]
    }

class ThisSquareTellsEverything(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_unit_square()
        words = TextMobject("""
            This square gives you
            everything you need.
        """)
        words.to_corner(UP+RIGHT)
        words.set_color(YELLOW)
        words.add_background_rectangle()
        arrow = Arrow(
            words.get_bottom(), self.square.get_right(), 
            color = WHITE
        )

        self.play(Write(words, run_time = 2))
        self.play(ShowCreation(arrow))
        self.add_foreground_mobject(words, arrow)
        self.wait()
        self.apply_transposed_matrix([[1.5, -0.5], [1, 1.5]])
        self.wait()

class WhatHappensToOneSquareHappensToAll(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_unit_square()
        pairs = [
            (2*RIGHT+UP, 1),
            (3*LEFT, 2),
            (2*LEFT+DOWN, 0.5),          
            (3.5*RIGHT+2.5*UP, 1.5),
            (RIGHT+2*DOWN, 0.25),
            (3*LEFT+3*DOWN, 1),
        ]
        squares = VMobject()
        for position, side_length in pairs:
            square = self.square.copy()
            square.scale(side_length)
            square.shift(position)
            squares.add(square)
        self.play(FadeIn(
            squares, lag_ratio = 0.5,
            run_time = 3
        ))
        self.add_transformable_mobject(squares)
        self.apply_transposed_matrix([[1, -1], [0.5, 1]])
        self.wait()

class BreakBlobIntoGridSquares(LinearTransformationScene):
    CONFIG = {
        "square_size" : 0.5,
        "blob_height" : 3,
    }
    def construct(self):
        self.setup()
        blob = Blob(
            height = self.blob_height, 
            random_seed = 5,
            random_nudge_size = 0.2,
        )
        blob.next_to(ORIGIN, UP+RIGHT)
        self.add_transformable_mobject(blob)
        arange = np.arange(
            0, self.blob_height + self.square_size, 
            self.square_size
        )
        square = Square(side_length = self.square_size)
        square.set_stroke(YELLOW, width = 2)
        square.set_fill(YELLOW, opacity = 0.3)
        squares = VMobject()
        for x, y in it.product(*[arange]*2):
            point = x*RIGHT + y*UP
            if blob.probably_contains(point):
                squares.add(square.copy().shift(point))
        self.play(ShowCreation(
            squares, lag_ratio = 0.5,
            run_time = 2,
        ))
        self.add_transformable_mobject(squares)
        self.wait()
        self.apply_transposed_matrix([[1, -1], [0.5, 1]])
        self.wait()

class BreakBlobIntoGridSquaresGranular(BreakBlobIntoGridSquares):
    CONFIG = {
        "square_size" : 0.25
    }

class BreakBlobIntoGridSquaresMoreGranular(BreakBlobIntoGridSquares):
    CONFIG = {
        "square_size" : 0.15
    }    

class BreakBlobIntoGridSquaresVeryGranular(BreakBlobIntoGridSquares):
    CONFIG = {
        "square_size" : 0.1
    }

class NameDeterminant(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[3, 0], [2, 2]]
    }
    def construct(self):
        self.setup()
        self.plane.fade(0.3)
        self.add_unit_square(color = YELLOW_E, opacity = 0.5)
        self.add_title(
            ["The", "``determinant''", "of a transformation"],
            scale_factor = 1
        )
        self.title.split()[1].split()[1].set_color(YELLOW)

        matrix_background, matrix, det_text = self.get_matrix()
        self.add_foreground_mobject(matrix_background, matrix)

        A = TexMobject("A")
        area_label = VMobject(A.copy(), A.copy(), A)
        area_label.move_to(self.square)
        det = np.linalg.det(self.t_matrix)
        if np.round(det) == det:
            det = int(det)
        area_label_target = VMobject(
            TexMobject(str(det)), TexMobject("\\cdot"), A.copy()
        )
        if det < 1 and det > 0:
            area_label_target.scale(det)
        area_label_target.arrange(RIGHT, buff = 0.1)
        self.add_moving_mobject(area_label, area_label_target)
        
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()
        det_mob_copy = area_label.split()[0].copy()
        new_det_mob = det_mob_copy.copy().set_height(
            det_text.split()[0].get_height()
        )
        new_det_mob.next_to(det_text, RIGHT, buff = 0.2)
        new_det_mob.add_background_rectangle()
        det_mob_copy.add_background_rectangle(opacity = 0)
        self.play(Write(det_text))
        self.play(Transform(det_mob_copy, new_det_mob))
        self.wait()


    def get_matrix(self):
        matrix = Matrix(np.array(self.t_matrix).transpose())
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(self.title, DOWN, buff = 0.5)
        matrix.shift(2*LEFT)
        matrix_background = BackgroundRectangle(matrix)
        det_text = get_det_text(matrix, 0)
        det_text.remove(det_text.split()[-1])
        return matrix_background, matrix, det_text

class SecondDeterminantExample(NameDeterminant):
    CONFIG = {
        "t_matrix" : [[-1, -1], [1, -1]]
    }

class DeterminantIsThree(NameDeterminant):
    CONFIG = {
        "t_matrix" : [[0, -1.5], [2, 1]]
    }

class DeterminantIsOneHalf(NameDeterminant):
    CONFIG = {
        "t_matrix" : [[0.5, -0.5], [0.5, 0.5]],
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "secondary_line_ratio" : 0
        },
    }

class DeterminantIsZero(NameDeterminant):
    CONFIG = {
        "t_matrix" : [[4, 2], [2, 1]],
    }

class SecondDeterminantIsZeroExamlpe(NameDeterminant):
    CONFIG = {
        "t_matrix" : [[0, 0], [0, 0]],
        "show_basis_vectors" : False
    }

class NextFewVideos(Scene):
    def construct(self):
        icon = SVGMobject("video_icon")
        icon.center()
        icon.set_width(FRAME_WIDTH/12.)
        icon.set_stroke(color = WHITE, width = 0)
        icon.set_fill(WHITE, opacity = 1)
        icons = VMobject(*[icon.copy() for x in range(10)])
        icons.set_submobject_colors_by_gradient(BLUE_A, BLUE_D)
        icons.arrange(RIGHT)
        icons.to_edge(LEFT)

        self.play(
            FadeIn(icons, lag_ratio = 0.5),
            run_time = 3
        )
        self.wait()

class UnderstandingBeforeApplication(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("""
            Just the visual 
            understanding for now
        """)
        self.random_blink()
        self.wait()

class WhatIveSaidSoFar(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("""
            What I've said so far
            is not quite right...
        """)
        self.wait()

class NegativeDeterminant(Scene):
    def construct(self):
        numerical_matrix = [[1, 2], [3, 4]]
        matrix = Matrix(numerical_matrix)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        det_text = get_det_text(matrix, np.linalg.det(numerical_matrix))
        words = TextMobject("""
            How can you scale area
            by a negative number?
        """)
        words.set_color(YELLOW)
        words.to_corner(UP+RIGHT)
        det_num = det_text.split()[-1]
        arrow = Arrow(words.get_bottom(), det_num)

        self.add(matrix)
        self.play(Write(det_text))
        self.wait()
        self.play(
            Write(words, run_time = 2),
            ShowCreation(arrow)
        )
        self.play(det_num.set_color, YELLOW)
        self.wait()

class FlipSpaceOver(Scene):
    def construct(self):
        plane1 = NumberPlane(y_radius = FRAME_X_RADIUS)
        plane2 = NumberPlane(
            y_radius = FRAME_X_RADIUS,
            color = RED_D, secondary_color = RED_E
        )
        axis = UP
        for word, plane in ("Front", plane1), ("Back", plane2):
            text = TextMobject(word)
            if word == "Back":
                text.rotate(np.pi, axis = axis)
            text.scale(2)
            text.next_to(ORIGIN, RIGHT).to_edge(UP)
            text.add_background_rectangle()
            plane.add(text)

        self.play(ShowCreation(
            plane1, lag_ratio = 0.5,
            run_time = 1
        ))
        self.wait()
        self.play(Rotate(
            plane1, axis = axis,
            rate_func = lambda t : smooth(t/2),
            run_time = 1.5,
            path_arc = np.pi/2,
        ))
        self.remove(plane1)
        self.play(Rotate(
            plane2, axis = axis,
            rate_func = lambda t : smooth((t+1)/2),
            run_time = 1.5,
            path_arc = np.pi/2,
        ))
        self.wait()

class RandyThinking(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        bubble = randy.get_bubble()
        bubble.make_green_screen()

        self.play(
            randy.change_mode, "pondering",
            ShowCreation(bubble)
        )
        self.wait()
        self.play(Blink(randy))
        self.wait(2)
        self.play(Blink(randy))

class NegativeDeterminantTransformation(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[1, 1], [2, -1]],
    }
    def construct(self):
        self.setup()
        self.add_title("Feels like flipping space")
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()

class ThinkAboutFlippingPaper(Scene):
    def construct(self):
        pass

class NegativeDeterminantTransformation2(NegativeDeterminantTransformation):
    CONFIG  ={
        "t_matrix" : [[-2, 1], [2, 1]]
    }

class IHatJHatOrientation(NegativeDeterminantTransformation):
    def construct(self):
        self.setup()
        i_label, j_label = self.get_basis_vector_labels()
        self.add_transformable_label(self.i_hat, i_label, color = X_COLOR)
        self.add_transformable_label(self.j_hat, j_label, color = Y_COLOR)

        arc = Arc(start_angle = 0, angle = np.pi/2, color = YELLOW)
        arc.shift(0.5*(RIGHT+UP)).scale(1/1.6)
        arc.add_tip()
        words1 = TextMobject([
            "$\\hat{\\jmath}$",
            "is to the",
            "left",
            "of",
            "$\\hat{\\imath}$",
        ])
        words1.split()[0].set_color(Y_COLOR)
        words1.split()[2].set_color(YELLOW)
        words1.split()[-1].set_color(X_COLOR)
        words1.add_background_rectangle()
        words1.next_to(arc, UP+RIGHT)

        words2 = TextMobject([
            "$L(\\hat{\\jmath})$",
            "is to the \\\\",
            "\\emph{right}",
            "of",
            "$L(\\hat{\\imath})$",
        ])
        words2.split()[0].set_color(Y_COLOR)
        words2.split()[2].set_color(YELLOW)
        words2.split()[-1].set_color(X_COLOR)
        words2.add_background_rectangle()


        self.play(ShowCreation(arc))
        self.play(Write(words1))
        self.wait()
        self.remove(words1, arc)
        self.apply_transposed_matrix(self.t_matrix)
        arc.submobjects = []
        arc.apply_function(self.get_matrix_transformation(self.t_matrix))
        arc.add_tip()
        words2.next_to(arc, RIGHT)
        self.play(
            ShowCreation(arc),
            Write(words2, run_time = 2),
        )
        self.wait()
        title = TextMobject("Orientation has been reversed")
        title.to_edge(UP)
        title.add_background_rectangle()
        self.play(Write(title, run_time = 1))
        self.wait()

class WriteNegativeDeterminant(NegativeDeterminantTransformation):
    def construct(self):
        self.setup()
        self.add_unit_square()
        matrix = Matrix(np.array(self.t_matrix).transpose())
        matrix.next_to(ORIGIN, LEFT)
        matrix.to_edge(UP)
        matrix.set_column_colors(X_COLOR, Y_COLOR)

        det_text = get_det_text(
            matrix, determinant = np.linalg.det(self.t_matrix)
        )
        three = VMobject(*det_text.split()[-1].split()[1:])
        for mob in det_text.split():
            if isinstance(mob, TexMobject):
                mob.add_background_rectangle()
        matrix_background = BackgroundRectangle(matrix)
        self.play(
            ShowCreation(matrix_background),
            Write(matrix),
            Write(det_text),
        )
        self.add_foreground_mobject(matrix_background, matrix, det_text)
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)

        self.play(three.copy().move_to, self.square)
        self.wait()

class AltWriteNegativeDeterminant(WriteNegativeDeterminant):
    CONFIG = {
        "t_matrix" : [[2, -1], [1, -3]]
    }

class WhyNegativeScaling(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says("""
            Why does negative area 
            relate to orientation-flipping? 
        """)
        other_students = np.array(self.get_students())[[0, 2]]
        self.play(*[
            ApplyMethod(student.change_mode, "confused")
            for student in other_students
        ])
        self.random_blink()
        self.wait()
        self.random_blink()

class SlowlyRotateIHat(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_unit_square()
        self.apply_transposed_matrix(
            [[-1, 0], [0, 1]],
            path_arc = np.pi,
            run_time = 30,
            rate_func=linear,
        )

class DeterminantGraphForRotatingIHat(Scene):
    def construct(self):
        t_axis = NumberLine(
            numbers_with_elongated_ticks = [],
            x_min = 0,
            x_max = 10,
            color = WHITE,
        )
        det_axis = NumberLine(
            numbers_with_elongated_ticks = [],
            x_min = -2,
            x_max = 2,
            color = WHITE
        )
        det_axis.rotate(np.pi/2)
        t_axis.next_to(ORIGIN, RIGHT, buff = 0)
        det_axis.move_to(t_axis.get_left())
        axes = VMobject(det_axis, t_axis)
        graph = FunctionGraph(np.cos, x_min = 0, x_max = np.pi)
        graph.next_to(det_axis, RIGHT, buff = 0)
        graph.set_color(YELLOW)
        det_word = TextMobject("Det")
        det_word.next_to(det_axis, RIGHT, aligned_edge = UP)
        time_word = TextMobject("time")
        time_word.next_to(t_axis, UP)
        time_word.to_edge(RIGHT)
        everything = VMobject(axes, det_word, time_word, graph)
        everything.scale(1.5)

        self.add(axes, det_word, time_word)
        self.play(ShowCreation(
            graph, rate_func=linear, run_time = 10
        ))

class WhatAboutThreeDimensions(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says("""
            What about 3D 
            transformations?
        """)
        self.random_blink()
        self.wait()
        self.random_blink()

class Transforming3DCube(Scene):
    def construct(self):
        pass

class NameParallelepiped(Scene):
    def construct(self):
        word = TextMobject("``Parallelepiped''")
        word.scale(2)
        pp_part1 = VMobject(*word.split()[:len(word.split())/2])
        pp_part2 = VMobject(*word.split()[len(word.split())/2:])
        pp_part1.set_submobject_colors_by_gradient(X_COLOR, Y_COLOR)
        pp_part2.set_submobject_colors_by_gradient(Y_COLOR, Z_COLOR)
        self.play(Write(word))
        self.wait(2)

class DeterminantIsVolumeOfParallelepiped(Scene):
    def construct(self):
        matrix = Matrix([[1, 0, 0.5], [0.5, 1, 0], [1, 0, 1]])
        matrix.shift(3*LEFT)
        matrix.set_column_colors(X_COLOR, Y_COLOR, Z_COLOR)
        det_text = get_det_text(matrix)
        eq = TexMobject("=")
        eq.next_to(det_text, RIGHT)
        words = TextMobject([
            "Volume of this\\\\",
            "parallelepiped"
        ])
        pp = words.split()[1]
        pp_part1 = VMobject(*pp.split()[:len(pp.split())/2])
        pp_part2 = VMobject(*pp.split()[len(pp.split())/2:])
        pp_part1.set_submobject_colors_by_gradient(X_COLOR, Y_COLOR)
        pp_part2.set_submobject_colors_by_gradient(Y_COLOR, Z_COLOR)

        words.next_to(eq, RIGHT)

        self.play(Write(matrix))
        self.wait()
        self.play(Write(det_text), Write(words), Write(eq))
        self.wait()

class Degenerate3DTransformation(Scene):
    def construct(self):
        pass

class WriteZeroDeterminant(Scene):
    def construct(self):
        matrix = Matrix([[1, 0, 1], [0.5, 1, 1.5], [1, 0, 1]])
        matrix.shift(2*LEFT)
        matrix.set_column_colors(X_COLOR, Y_COLOR, Z_COLOR)
        det_text = get_det_text(matrix, 0)
        brace = Brace(matrix, DOWN)
        words = TextMobject("""
            Columns must be
            linearly dependent
        """)
        words.set_color(YELLOW)
        words.next_to(brace, DOWN)

        self.play(Write(matrix))
        self.wait()
        self.play(Write(det_text))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(words, run_time = 2)
        )
        self.wait()

class AskAboutNegaive3DDeterminant(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says("""
            What would det$(M) < 0$ mean?
        """)
        self.random_blink()
        self.play(self.teacher.change_mode, "pondering")
        self.wait()
        self.random_blink()

class OrientationReversing3DTransformation(Scene):
    def construct(self):
        pass

class RightHandRule(Scene):
    CONFIG = {
        "flip" : False,
        "labels_tex" : ["\\hat{\\imath}", "\\hat{\\jmath}", "\\hat{k}"],
        "colors" : [X_COLOR, Y_COLOR, Z_COLOR],
    }
    def construct(self):
        hand = RightHand()
        v1 = Vector([-1.75, 0.5])
        v2 = Vector([-1.4, -0.7])
        v3 = Vector([0, 1.7])
        vects = [v1, v2, v3]        
        if self.flip:
            VMobject(hand, *vects).flip()

        v1_label, v2_label, v3_label = [
            TexMobject(label_tex).scale(1.5)
            for label_tex in self.labels_tex
        ]
        v1_label.next_to(v1.get_end(), UP)
        v2_label.next_to(v2.get_end(), DOWN)
        v3_label.next_to(v3.get_end(), UP)

        labels = [v1_label, v2_label, v3_label]

        # self.add(NumberPlane())
        self.play(
            ShowCreation(hand.outline, run_time = 2, rate_func=linear),
            FadeIn(hand.inlines)
        )
        self.wait()
        for vect, label, color in zip(vects, labels, self.colors):
            vect.set_color(color)
            label.set_color(color)
            vect.set_stroke(width = 8)
            self.play(ShowCreation(vect))
            self.play(Write(label))
            self.wait()

class LeftHandRule(RightHandRule):
    CONFIG = {
        "flip" : True
    }

class AskHowToCompute(TeacherStudentsScene):
    def construct(self):
        self.setup()
        student = self.get_students()[1]
        self.student_says("How do you \\\\ compute this?")
        self.play(student.change_mode, "confused")
        self.random_blink()
        self.wait()
        self.random_blink()

class TwoDDeterminantFormula(Scene):
    def construct(self):
        eq = TextMobject("=")
        matrix = Matrix([["a", "b"], ["c", "d"]])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        ma, mb, mc, md = matrix.get_entries().split()
        ma.shift(0.1*DOWN)
        mc.shift(0.7*mc.get_height()*DOWN)
        det_text = get_det_text(matrix)
        VMobject(matrix, det_text).next_to(eq, LEFT)
        formula = TexMobject(list("ad-bc"))
        formula.next_to(eq, RIGHT)
        formula.shift(0.1*UP)

        a, d, minus, b, c = formula.split()
        VMobject(a, c).set_color(X_COLOR)
        VMobject(b, d).set_color(Y_COLOR)

        for mob in mb, mc, b, c:
            if mob is c:
                mob.zero = TexMobject("\\cdot 0")
            else:
                mob.zero = TexMobject("0")
            mob.zero.move_to(mob, aligned_edge = DOWN+LEFT)
            mob.zero.set_color(mob.get_color())
            mob.original = mob.copy()
        c.zero.shift(0.1*RIGHT)

        self.add(matrix)
        self.play(Write(det_text, run_time = 1))
        self.play(Write(eq), Write(formula))
        self.wait()
        self.play(*[
            Transform(m, m.zero)
            for m in (mb, mc, b, c)
        ])
        self.wait()
        for pair in (mb, b), (mc, c):
            self.play(*[
                Transform(m, m.original)
                for m in pair
            ])
            self.wait()

class TwoDDeterminantFormulaIntuition(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_unit_square()
        a, b, c, d = 3, 2, 3.5, 2

        self.wait()
        self.apply_transposed_matrix([[a, 0], [0, 1]])
        i_brace = Brace(self.i_hat, DOWN)
        width = TexMobject("a").scale(1.5)
        i_brace.put_at_tip(width)
        width.set_color(X_COLOR)
        width.add_background_rectangle()
        self.play(GrowFromCenter(i_brace), Write(width))
        self.wait()

        self.apply_transposed_matrix([[1, 0], [0, d]])
        side_brace = Brace(self.square, RIGHT)
        height = TexMobject("d").scale(1.5)
        side_brace.put_at_tip(height)
        height.set_color(Y_COLOR)
        height.add_background_rectangle()
        self.play(GrowFromCenter(side_brace), Write(height))
        self.wait()

        self.apply_transposed_matrix(
            [[1, 0], [float(b)/d, 1]],
            added_anims = [
                ApplyMethod(m.shift, b*RIGHT)
                for m in (side_brace, height)
            ]
        )
        self.wait()
        self.play(*list(map(FadeOut, [i_brace, side_brace, width, height])))
        matrix1 = np.dot(
            [[a, b], [c, d]],
            np.linalg.inv([[a, b], [0, d]])
        )
        matrix2 = np.dot(
            [[a, b], [-c, d]],
            np.linalg.inv([[a, b], [c, d]])
        )
        self.apply_transposed_matrix(matrix1.transpose(), path_arc = 0)
        self.wait()
        self.apply_transposed_matrix(matrix2.transpose(), path_arc = 0)
        self.wait()

class FullFormulaExplanation(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_unit_square()
        self.apply_transposed_matrix([[3, 1], [1, 2]], run_time = 0)
        self.add_braces()        
        self.add_polygons()
        self.show_formula()

    def get_matrix(self):
        matrix = Matrix([["a", "b"], ["c", "d"]])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        ma, mb, mc, md = matrix.get_entries().split()
        ma.shift(0.1*DOWN)
        mc.shift(0.7*mc.get_height()*DOWN)
        matrix.shift(2*DOWN+4*LEFT)
        return matrix

    def add_polygons(self):
        a = self.i_hat.get_end()[0]*RIGHT
        b = self.j_hat.get_end()[0]*RIGHT
        c = self.i_hat.get_end()[1]*UP
        d = self.j_hat.get_end()[1]*UP

        shapes_colors_and_tex = [
            (Polygon(ORIGIN, a, a+c), MAROON, "ac/2"),
            (Polygon(ORIGIN, d+b, d, d), TEAL, "\\dfrac{bd}{2}"),
            (Polygon(a+c, a+b+c, a+b+c, a+b+c+d), TEAL, "\\dfrac{bd}{2}"),
            (Polygon(b+d, a+b+c+d, b+c+d), MAROON, "ac/2"),
            (Polygon(a, a+b, a+b+c, a+c), PINK, "bc"),
            (Polygon(d, d+b, d+b+c, d+c), PINK, "bc"),
        ]
        everyone = VMobject()
        for shape, color, tex in shapes_colors_and_tex:
            shape.set_stroke(width = 0)
            shape.set_fill(color = color, opacity = 0.7)
            tex_mob = TexMobject(tex)
            tex_mob.scale(0.7)
            tex_mob.move_to(shape.get_center_of_mass())
            everyone.add(shape, tex_mob)
        self.play(FadeIn(
            everyone, 
            lag_ratio = 0.5,
            run_time = 1
        ))



    def add_braces(self):
        a = self.i_hat.get_end()[0]*RIGHT
        b = self.j_hat.get_end()[0]*RIGHT
        c = self.i_hat.get_end()[1]*UP
        d = self.j_hat.get_end()[1]*UP

        quads = [
            (ORIGIN, a, DOWN, "a"),
            (a, a+b, DOWN, "b"),
            (a+b, a+b+c, RIGHT, "c"),
            (a+b+c, a+b+c+d, RIGHT, "d"),
            (a+b+c+d, b+c+d, UP, "a"),
            (b+c+d, d+c, UP, "b"),
            (d+c, d, LEFT, "c"),
            (d, ORIGIN, LEFT, "d"),
        ]
        everyone = VMobject()
        for p1, p2, direction, char in quads:
            line = Line(p1, p2)
            brace = Brace(line, direction, buff = 0)
            text = brace.get_text(char)
            text.add_background_rectangle()
            if char in ["a", "c"]:
                text.set_color(X_COLOR)
            else:
                text.set_color(Y_COLOR)
            everyone.add(brace, text)
        self.play(Write(everyone), run_time = 1)


    def show_formula(self):
        matrix = self.get_matrix()
        det_text = get_det_text(matrix)
        f_str = "=(a+b)(c+d)-ac-bd-2bc=ad-bc"
        formula = TexMobject(f_str)

        formula.next_to(det_text, RIGHT)
        everyone = VMobject(det_text, matrix, formula)
        everyone.set_width(FRAME_WIDTH - 1)
        everyone.next_to(DOWN, DOWN)
        background_rect = BackgroundRectangle(everyone)
        self.play(
            ShowCreation(background_rect),
            Write(everyone)
        )
        self.wait()

class ThreeDDetFormula(Scene):
    def construct(self):
        matrix = Matrix([list("abc"), list("def"), list("ghi")])
        matrix.set_column_colors(X_COLOR, Y_COLOR, Z_COLOR)
        m1 = Matrix([["e", "f"], ["h", "i"]])
        m1.set_column_colors(Y_COLOR, Z_COLOR)
        m2 = Matrix([["d", "f"], ["g", "i"]])
        m2.set_column_colors(X_COLOR, Z_COLOR)
        m3 = Matrix([["d", "e"], ["g", "h"]])
        m3.set_column_colors(X_COLOR, Y_COLOR)

        for m in matrix, m1, m2, m3:
            m.add(get_det_text(m))
        a, b, c = matrix.get_entries().split()[:3]
        parts = it.starmap(VMobject, [
            [matrix], 
            [TexMobject("="), a.copy(), m1], 
            [TexMobject("-"), b.copy(), m2],
            [TexMobject("+"), c.copy(), m3],
        ])
        parts = list(parts)
        for part in parts:
            part.arrange(RIGHT, buff = 0.2)
        parts[1].next_to(parts[0], RIGHT)
        parts[2].next_to(parts[1], DOWN, aligned_edge = LEFT)
        parts[3].next_to(parts[2], DOWN, aligned_edge = LEFT)
        everyone = VMobject(*parts)
        everyone.center().to_edge(UP)
        for part in parts:
            self.play(Write(part))
        self.wait(2)

class QuizTime(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Quiz time!")
        self.random_blink()
        self.wait()
        self.random_blink()

class ProductProperty(Scene):
    def construct(self):
        lhs = TexMobject([
            "\\text{det}(",
            "M_1", 
            "M_2",
            ")"
        ])
        det, m1, m2, rp = lhs.split()
        m1.set_color(TEAL)
        m2.set_color(PINK)

        rhs = TexMobject([
            "=\\text{det}(",
            "M_1", 
            ")\\text{det}(",
            "M_2",
            ")"
        ])
        rhs.split()[1].set_color(TEAL)
        rhs.split()[3].set_color(PINK)

        rhs.next_to(lhs, RIGHT)
        formula = VMobject(lhs, rhs)
        formula.center()

        title = TextMobject("Explain in one sentence")
        title.set_color(YELLOW)
        title.next_to(formula, UP, buff = 0.5)

        self.play(Write(m1))
        self.play(Write(m2))
        self.wait()
        self.play(Write(det), Write(rp))
        self.play(Write(rhs))
        self.wait(2)
        self.play(Write(title))
        self.wait(2)

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: Inverse matrices, column space and null space
        """)
        title.set_width(FRAME_WIDTH - 2)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()  












