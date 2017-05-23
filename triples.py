from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from topics.common_scenes import PatreonThanks

A_COLOR = BLUE
B_COLOR = GREEN
C_COLOR = YELLOW
SIDE_COLORS = [A_COLOR, B_COLOR, C_COLOR]

#revert_to_original_skipping_status

class IntroduceTriples(TeacherStudentsScene):
    def construct(self):
        title = TexMobject("a", "^2", "+", "b", "^2", "=", "c", "^2")
        for color, char in zip(SIDE_COLORS, "abc"):
            title.highlight_by_tex(char, color)
        title.to_edge(UP)

        triples = [
            (3, 4, 5), 
            (5, 12, 13),
            (8, 15, 17),
        ]
        triangles = VGroup(*[
            Polygon(ORIGIN, a*RIGHT, a*RIGHT+b*UP)
            for a, b, c in triples
        ])
        for triple, triangle in zip(triples, triangles):
            a, b, c = map(TexMobject, map(str, triple))
            for color, mob in zip(SIDE_COLORS, [a, b, c]):
                mob.scale(0.7)
                mob.highlight(color)
            triangle.scale(0.25)
            triangle.highlight(WHITE)
            elbow = VGroup(
                Line(UP, UP+LEFT),
                Line(UP+LEFT, LEFT)
            )
            elbow.scale_to_fit_width(0.15)
            elbow.move_to(triangle, DOWN+RIGHT)
            a.next_to(triangle, DOWN, SMALL_BUFF)
            b.next_to(triangle, RIGHT, SMALL_BUFF)
            c.next_to(triangle.get_center(), UP+LEFT, SMALL_BUFF)
            triangle.add(elbow, a, b, c)
        triangles.arrange_submobjects(
            RIGHT, buff = MED_LARGE_BUFF, aligned_edge = DOWN
        )
        triangles.next_to(self.get_pi_creatures(), UP)
        triangles.shift_onto_screen()

        self.add(title)
        self.play(
            Write(triangles[0], run_time = 2),
            self.teacher.change, "raise_right_hand"
        )
        self.change_student_modes(
            *["pondering"]*3, 
            look_at_arg = triangles[0]
        )
        for triangle in triangles[1:]:
            self.play(Write(triangle, run_time = 2))
            self.dither()
        self.dither(2)

class PythagoreanProof(Scene):
    def construct(self):
        self.add_title()
        self.show_proof()

    def add_title(self):
        title = TexMobject("a^2", "+", "b^2", "=", "c^2")
        for color, char in zip(SIDE_COLORS, "abc"):
            title.highlight_by_tex(char, color)
        title.to_edge(UP)
        self.add(title)
        self.title = title

    def show_proof(self):
        triangle = Polygon(
            ORIGIN, 5*RIGHT, 5*RIGHT+12*UP,
            stroke_color = WHITE,
            stroke_width = 2,
            fill_color = WHITE,
            fill_opacity = 0.5
        )
        triangle.scale_to_fit_height(3)
        triangle.center()
        triangle_copy = triangle.copy()
        squares = self.get_abc_squares(triangle)
        a_square, b_square, c_square = squares


        self.add(triangle, triangle_copy)
        self.play(*map(DrawBorderThenFill, squares))
        self.add_labels_to_squares(squares)
        self.dither()
        self.play(
            VGroup(triangle, c_square).move_to, 
                4*LEFT+2*DOWN, DOWN,
            VGroup(triangle_copy, a_square, b_square).move_to, 
                4*RIGHT+2*DOWN, DOWN,
        )
        self.dither()
        self.add_new_triangles(
            triangle, 
            self.get_added_triangles_to_c_square(triangle, c_square)
        )
        self.dither()
        self.add_new_triangles(
            triangle_copy,
            self.get_added_triangles_to_ab_squares(triangle_copy, a_square)
        )
        self.dither()

        big_squares = VGroup(*map(
            self.get_big_square,
            [triangle, triangle_copy]
        ))
        negative_space_words = TextMobject(
            "Same negative \\\\ space"
        )
        negative_space_words.scale(0.75)
        negative_space_words.shift(UP)
        double_arrow = DoubleArrow(LEFT, RIGHT)
        double_arrow.next_to(negative_space_words, DOWN)

        self.play(
            FadeIn(big_squares), 
            Write(negative_space_words), 
            ShowCreation(double_arrow),
            *map(FadeOut, squares)
        )
        self.dither(2)
        self.play(*it.chain(
            map(FadeIn, squares),
            map(Animation, big_squares),
        ))
        self.dither(2)

    def add_labels_to_squares(self, squares):
        labels = VGroup(*[
            self.title.get_part_by_tex(tex).copy()
            for tex in "a^2", "b^2", "c^2"
        ])
        for label, square in zip(labels, squares):
            label.generate_target()
            label.target.scale(0.7)
            label.target.move_to(square)
            square.add(label)

        self.play(LaggedStart(MoveToTarget, labels))

    def add_new_triangles(self, triangle, added_triangles):
        self.play(ReplacementTransform(
            VGroup(triangle.copy().set_fill(opacity = 0)),
            added_triangles,
            run_time = 2,
        ))
        triangle.added_triangles = added_triangles

    def get_big_square(self, triangle):
        square = Square(stroke_color = RED)
        square.replace(
            VGroup(triangle, triangle.added_triangles),
            stretch = True
        )
        square.scale_in_place(1.01)
        return square

    #####

    def get_abc_squares(self, triangle):
        a_square, b_square, c_square = squares = [
            Square(
                stroke_color = color,
                fill_color = color,
                fill_opacity = 0.5,
            )
            for color in SIDE_COLORS
        ]
        a_square.scale_to_fit_width(triangle.get_width())
        a_square.move_to(triangle.get_bottom(), UP)
        b_square.scale_to_fit_height(triangle.get_height())
        b_square.move_to(triangle.get_right(), LEFT)
        hyp_line = Line(
            triangle.get_corner(UP+RIGHT),
            triangle.get_corner(DOWN+LEFT),
        )
        c_square.scale_to_fit_width(hyp_line.get_length())
        c_square.move_to(hyp_line.get_center(), UP)
        c_square.rotate(
            hyp_line.get_angle(), 
            about_point = hyp_line.get_center()
        )

        return a_square, b_square, c_square

    def get_added_triangles_to_c_square(self, triangle, c_square):
        return VGroup(*[
            triangle.copy().rotate(i*np.pi/2, about_point = c_square.get_center())
            for i in range(1, 4)
        ])

    def get_added_triangles_to_ab_squares(self, triangle, a_square):
        t1 = triangle.copy()
        t1.rotate_in_place(np.pi)
        group = VGroup(triangle, t1).copy()
        group.rotate(-np.pi/2)
        group.move_to(a_square.get_right(), LEFT)
        t2, t3 = group
        return VGroup(t1, t2, t3)










































