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
from eola.chapter3 import MatrixVectorMultiplicationAbstract

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
        self.scale_to_fit_height(self.height).center()

    def probably_contains(self, point):
        border_points = np.array(self.get_anchors_and_handles()[0])
        distances = map(lambda p : np.linalg.norm(p-point), border_points)
        min3 = border_points[np.argsort(distances)[:3]]
        center_direction = self.get_center() - point
        in_center_direction = map(
            lambda p : np.dot(p-point, center_direction) > 0, 
            min3
        )
        return sum(in_center_direction) <= 2
            

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject([
            "``The purpose of computation is \\\\",
            "insight",
            ", not ",
            "numbers.",
            "''",
        ], separate_list_arg_with_spaces = False)
        # words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words.split()[1].highlight(BLUE)
        words.split()[3].highlight(GREEN)
        author = TextMobject("-Richard Hamming")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither()

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
        self.dither(2)

class StretchingTransformation(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_title("Generally stretches space")
        self.apply_transposed_matrix([[3, 1], [-1, 2]])
        self.dither()

class SquishingTransformation(LinearTransformationScene):
    CONFIG = {
        "foreground_plane_kwargs" : {
            "x_radius" : 3*SPACE_WIDTH,
            "y_radius" : 3*SPACE_WIDTH,
            "secondary_line_ratio" : 0
        },
    }
    def construct(self):
        self.setup()
        self.add_title("Generally squishes space")
        self.apply_transposed_matrix([[1./2, -0.5], [1, 1./3]])
        self.dither()

class AskAboutStretching(LinearTransformationScene):
    def construct(self):
        self.setup()
        words = TextMobject("""
            Exactly how much are 
            things being stretched?
        """)
        words.add_background_rectangle()
        words.to_corner(UP+RIGHT)
        words.highlight(YELLOW)
        self.apply_transposed_matrix(
            [[2, 1], [-1, 3]],
            added_anims = [Write(words)]
        )
        self.dither()

class AskAboutStretchingSpecifically(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_title(["How much are", "areas", "scaled?"])
        hma, areas, scaled = self.title.split()[1].split()
        areas.highlight(YELLOW)
        blob = Blob().shift(UP+RIGHT)

        label = TextMobject("Area")
        label.highlight(YELLOW)
        label = VMobject(VectorizedPoint(label.get_left()), label)
        label.move_to(blob)
        target_label = TexMobject(["c \\cdot", "\\text{Area}"])
        target_label.split()[1].highlight(YELLOW)

        self.add_transformable_mobject(blob)
        self.add_moving_mobject(label, target_label)
        self.dither()
        self.apply_transposed_matrix([[2, -1], [1, 1]])
        arrow = Arrow(scaled, label.target.split()[0])
        self.play(ShowCreation(arrow))
        self.dither()

class BeautyNowUsesLater(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Beauty now, uses later")
        self.dither()

class DiagonalExample(LinearTransformationScene):
    CONFIG = {
        "show_square" : False, 
        "show_coordinates" : True,
        "transposed_matrix" : [[3, 0], [0, 2]]
    }
    def construct(self):
        self.setup()
        matrix = Matrix(np.array(self.transposed_matrix).transpose())
        matrix.highlight_columns(X_COLOR, Y_COLOR)
        matrix.next_to(ORIGIN, LEFT).to_edge(UP)
        matrix_background = BackgroundRectangle(matrix)
        self.play(ShowCreation(matrix_background), Write(matrix))
        if self.show_square:
            self.add_unit_square(animate = True)
        self.add_foreground_mobject(matrix_background, matrix)
        self.dither()
        self.apply_transposed_matrix([self.transposed_matrix[0], [0, 1]])
        self.apply_transposed_matrix([[1, 0], self.transposed_matrix[1]])
        self.dither()
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
            self.dither()

            width_target, height_target = width.copy(), height.copy()
            det = np.linalg.det(self.transposed_matrix)
            times, eq_det = map(TexMobject, ["\\times", "=%d"%det])
            words = TextMobject("New area $=$")
            equation = VMobject(
                words, width_target, times, height_target, eq_det
            )
            equation.arrange_submobjects(RIGHT, buff = 0.2)
            equation.next_to(self.square, UP, aligned_edge = LEFT)
            equation.shift(0.5*RIGHT)
            background_rect = BackgroundRectangle(equation)

            self.play(
                ShowCreation(background_rect),                
                Transform(width.copy(), width_target),
                Transform(height.copy(), height_target),
                *map(Write, [words, times, eq_det])
            )
            self.dither()

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
        words.highlight(YELLOW)
        words.add_background_rectangle()
        arrow = Arrow(
            words.get_bottom(), self.square.get_right(), 
            color = WHITE
        )

        self.play(Write(words, run_time = 2))
        self.play(ShowCreation(arrow))
        self.add_foreground_mobject(words, arrow)
        self.dither()
        self.apply_transposed_matrix([[1.5, -0.5], [1, 1.5]])
        self.dither()

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
            squares, submobject_mode = "lagged_start",
            run_time = 3
        ))
        self.add_transformable_mobject(squares)
        self.apply_transposed_matrix([[1, -1], [0.5, 1]])
        self.dither()

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
            squares, submobject_mode = "lagged_start",
            run_time = 2,
        ))
        self.add_transformable_mobject(squares)
        self.dither()
        self.apply_transposed_matrix([[1, -1], [0.5, 1]])
        self.dither()

class BreakBlobIntoGridSquaresGranular(BreakBlobIntoGridSquares):
    CONFIG = {
        "square_size" : 0.25
    }

class BreakBlobIntoGridSquaresVeryGranular(BreakBlobIntoGridSquares):
    CONFIG = {
        "square_size" : 0.1
    }

class NameDeterminant(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[1, 0], [2, 1]]
    }
    def construct(self):
        self.setup()
        self.add_unit_square()
        self.add_title(["The", "``determinant''", "of a transformation"])
        self.title.split()[1].split()[1].highlight(YELLOW)

        text = TextMobject("Area $=1$")
        text.move_to(self.square)
        det = np.linalg.det(self.t_matrix)
        self.add_moving_mobject(text, TextMobject("Area $=%d$"%det))
        self.show_frame()












