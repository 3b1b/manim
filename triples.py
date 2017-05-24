from helpers import *
import fractions

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
U_COLOR = MAROON_B
V_COLOR = RED

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

class LastVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Pi hiding in prime regularities")
        title.to_edge(UP)
        screen_rect = ScreenRectangle(height = 6)
        screen_rect.next_to(title, DOWN)

        self.play(ShowCreation(screen_rect))
        self.play(Write(title))
        self.dither()

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

class ShowManyTriples(Scene):
    def construct(self):
        triples = [
            (u**2 - v**2, 2*u*v, u**2 + v**2)
            for u in range(1, 15)
            for v in range(1, u)
            if fractions.gcd(u, v) == 1 and not (u%2 == v%2)
        ][:40]
        triangles = VGroup()
        titles = VGroup()
        for i, (a, b, c) in enumerate(triples):
            triangle = Polygon(ORIGIN, a*RIGHT, a*RIGHT+b*UP)
            triangle.highlight(WHITE)
            max_width = max_height = 4
            triangle.scale_to_fit_height(max_height)
            if triangle.get_width() > max_width:
                triangle.scale_to_fit_width(max_width)
            triangle.move_to(2*RIGHT)
            num_strings = map(str, (a, b, c))
            labels = map(TexMobject, num_strings)
            for label, color in zip(labels, SIDE_COLORS):
                label.highlight(color)
            labels[0].next_to(triangle, DOWN)
            labels[1].next_to(triangle, RIGHT)
            labels[2].next_to(triangle.get_center(), UP+LEFT)
            triangle.add(*labels)

            title = TexMobject(
                str(a), "^2", "+", str(b), "^2", "=", str(c), "^2"
            )
            for num, color in zip([a, b, c], SIDE_COLORS):
                title.highlight_by_tex(str(num), color)
            title.next_to(triangle, UP, LARGE_BUFF)
            title.generate_target()
            title.target.scale(0.5)

            title.target.move_to(
                (-SPACE_WIDTH + MED_LARGE_BUFF + 2.7*(i//8))*RIGHT + \
                (SPACE_HEIGHT - MED_LARGE_BUFF - (i%8))*UP,
                UP+LEFT
            )

            triangles.add(triangle)
            titles.add(title)

        triangle = triangles[0]
        title = titles[0]
        self.play(
            Write(triangle),
            Write(title),
            run_time = 2,
        )
        self.dither()
        self.play(MoveToTarget(title))
        for i in range(1, 17):
            new_triangle = triangles[i]
            new_title = titles[i]
            if i < 4:
                self.play(
                    Transform(triangle, new_triangle),
                    FadeIn(new_title)
                )
                self.dither()
                self.play(MoveToTarget(new_title))
            else:
                self.play(
                    Transform(triangle, new_triangle),
                    FadeIn(new_title.target)
                )
                self.dither()
        self.play(FadeOut(triangle))
        self.play(LaggedStart(
            FadeIn, 
            VGroup(*[
                title.target 
                for title in titles[17:]
            ]),
            run_time = 5
        ))

        self.dither(2)

class CompareToFermatsLastTheorem(TeacherStudentsScene):
    def construct(self):
        expressions = [
            TexMobject(
                "a", "^%d"%d, "+", "b", "^%d"%d, 
                "=", "c", "^%d"%d
            )
            for d in range(2, 9)
        ]
        for expression in expressions:
            for char, color in zip("abc", SIDE_COLORS):
                expression.highlight_by_tex(char, color)
            expression.next_to(self.get_pi_creatures(), UP, buff = 1.3)
        square_expression = expressions[0]
        low_expression = expressions[1]
        square_expression.to_edge(UP, buff = 1.3)
        top_brace = Brace(square_expression, UP, buff = SMALL_BUFF)
        top_text = top_brace.get_text(
            "Abundant integer solutions", buff = SMALL_BUFF
        )
        low_brace = Brace(low_expression, DOWN, buff = SMALL_BUFF)
        low_text = low_brace.get_text(
            "No integer solutions", buff = SMALL_BUFF
        )
        low_text.highlight(RED)

        self.add(square_expression, top_brace, top_text)
        self.play(
            ReplacementTransform(
                square_expression.copy(),
                low_expression
            ),
            self.teacher.change_mode, "raise_right_hand",
            *[
                ApplyMethod(pi.change, "confused", expressions[1])
                for pi in self.get_students()
            ]
        )
        self.dither()
        self.play(Transform(low_expression, expressions[2]))
        self.play(
            GrowFromCenter(low_brace),
            FadeIn(low_text),
        )
        self.change_student_modes(
            "sassy", "angry", "erm",
            look_at_arg = low_expression,
            added_anims = [Transform(low_expression, expressions[3])]
        )
        for expression in expressions[4:]:
            self.play(Transform(low_expression, expression))
            self.dither()

class BabylonianTablets(Scene):
    def construct(self):
        title = TextMobject("Plimpton 322 Tablets \\\\ (1800 BC)")
        title.to_corner(UP+LEFT)
        ac_pairs = [
            (119, 169),
            (3367, 4825),
            (4601, 6649),
            (12709, 18541),
            (65, 97),
            (319, 481),
            (2291, 3541),
            (799, 1249),
            (481, 769),
            (4961, 8161),
            (45, 75),
            (1679, 2929),
            (161, 289),
            (1771, 3229),
            (56, 106),
        ]
        triples = VGroup()
        for a, c in ac_pairs:
            b = int(np.sqrt(c**2 - a**2))
            tex = "%s^2 + %s^2 = %s^2"%tuple(
                map("{:,}".format, [a, b, c])
            )
            tex = tex.replace(",", "{,}")
            triple = TexMobject(tex)
            triples.add(triple)
        triples.arrange_submobjects(DOWN, aligned_edge = LEFT)
        triples.scale_to_fit_height(2*SPACE_HEIGHT - LARGE_BUFF)
        triples.to_edge(RIGHT)

        self.add(title)
        self.dither()
        self.play(LaggedStart(FadeIn, triples, run_time = 5))
        self.dither()

class ReframeOnLattice(PiCreatureScene):
    CONFIG = {
        "initial_plane_center" : 3*LEFT + DOWN,
        "new_plane_center" : ORIGIN,
        "initial_unit_size" : 0.5,
        "new_unit_size" : 0.8,
        "dot_radius" : 0.075,
        "dot_color" : YELLOW,
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.add_plane()
        self.wander_over_lattice_points()
        self.show_whole_distance_examples()
        self.resize_plane()
        self.show_root_example()
        self.view_as_complex_number()
        self.mention_squaring_it()
        self.work_out_square_algebraically()
        self.walk_through_square_geometrically()

    def add_plane(self):
        plane = ComplexPlane(
            center_point = self.initial_plane_center,
            unit_size = self.initial_unit_size,
            stroke_width = 2,
            secondary_line_ratio = 0,
        )
        plane.axes.set_stroke(width = 4)
        plane.coordinate_labels = VGroup()
        for x in range(-8, 20, 2):
            if x == 0:
                continue
            label = TexMobject(str(x))
            label.scale(0.5)
            label.add_background_rectangle(opacity = 1)
            label.next_to(plane.coords_to_point(x, 0), DOWN, SMALL_BUFF)
            plane.coordinate_labels.add(label)

        self.add(plane, plane.coordinate_labels)
        self.plane = plane

    def wander_over_lattice_points(self):
        initial_examples = [(5, 3), (6, 8), (2, 7)]
        integer_distance_examples = [(3, 4), (12, 5), (15, 8)]
        dot_tuple_groups = VGroup()
        for x, y in initial_examples + integer_distance_examples:
            dot = Dot(
                self.plane.coords_to_point(x, y),
                color = self.dot_color,
                radius = self.dot_radius,
            )
            tuple_mob = TexMobject("(", str(x), ",", str(y), ")")
            tuple_mob.add_background_rectangle()
            tuple_mob.next_to(dot, UP+RIGHT, buff = 0)
            dot_tuple_groups.add(VGroup(dot, tuple_mob))
        dot_tuple_group = dot_tuple_groups[0]
        final_group = dot_tuple_groups[-len(integer_distance_examples)]

        all_dots = self.get_all_plane_dots()

        self.play(Write(dot_tuple_group, run_time = 2))
        self.dither()
        for new_group in dot_tuple_groups[1:len(initial_examples)]:
            self.play(Transform(dot_tuple_group, new_group))
            self.dither()
        self.play(LaggedStart(
            FadeIn, all_dots,
            rate_func = there_and_back,
            run_time = 3,
            lag_ratio = 0.2,
        ))
        self.dither()
        self.play(ReplacementTransform(
            dot_tuple_group, final_group
        ))

        self.integer_distance_dot_tuple_groups = VGroup(
            *dot_tuple_groups[len(initial_examples):]
        )

    def show_whole_distance_examples(self):
        dot_tuple_groups = self.integer_distance_dot_tuple_groups
        for dot_tuple_group in dot_tuple_groups:
            dot, tuple_mob = dot_tuple_group
            p0 = self.plane.get_center_point()
            p1 = dot.get_center()
            triangle = Polygon(
                p0, p1[0]*RIGHT + p0[1]*UP, p1,
                stroke_width = 0,
                fill_color = BLUE,
                fill_opacity = 0.75,
            )
            line = Line(p0, p1, color = dot.get_color())
            a, b = self.plane.point_to_coords(p1)
            c = int(np.sqrt(a**2 + b**2))
            hyp_label = TexMobject(str(c))
            hyp_label.add_background_rectangle()
            hyp_label.next_to(
                triangle.get_center(), UP+LEFT, buff = SMALL_BUFF
            )
            line.add(hyp_label)

            dot_tuple_group.triangle = triangle
            dot_tuple_group.line = line

        group = dot_tuple_groups[0]

        self.play(Write(group.line))
        self.play(FadeIn(group.triangle), Animation(group.line))
        self.dither(2)
        for new_group in dot_tuple_groups[1:]:
            self.play(
                Transform(group, new_group),
                Transform(group.triangle, new_group.triangle),
                Transform(group.line, new_group.line),
            )
            self.dither(2)
        self.play(*map(FadeOut, [group, group.triangle, group.line]))

    def resize_plane(self):
        new_plane = ComplexPlane(
            plane_center = self.new_plane_center,
            unit_size = self.new_unit_size,
            y_radius = 8,
            x_radius = 11,
            stroke_width = 2,
            secondary_line_ratio = 0,
        )
        new_plane.axes.set_stroke(width = 4)
        self.plane.generate_target()
        self.plane.target.unit_size = self.new_unit_size
        self.plane.target.plane_center = self.new_plane_center
        self.plane.target.shift(
            new_plane.coords_to_point(0, 0) - \
            self.plane.target.coords_to_point(0, 0)
        )
        self.plane.target.scale(
            self.new_unit_size / self.initial_unit_size
        )
        coordinate_labels = self.plane.coordinate_labels
        for coord in coordinate_labels:
            x = int(coord.get_tex_string())
            coord.generate_target()
            coord.target.scale(1.5)
            coord.target.next_to(
                new_plane.coords_to_point(x, 0),
                DOWN, buff = SMALL_BUFF
            )


        self.play(
            MoveToTarget(self.plane),
            *map(MoveToTarget, self.plane.coordinate_labels),
            run_time = 2
        )
        self.remove(self.plane)
        self.plane = new_plane
        self.plane.coordinate_labels = coordinate_labels 
        self.add(self.plane, coordinate_labels)
        self.dither()

    def show_root_example(self):
        x, y = (2, 1)
        point = self.plane.coords_to_point(x, y)
        dot = Dot(
            point,
            color = self.dot_color,
            radius = self.dot_radius
        )
        tuple_label = TexMobject(str((x, y)))
        tuple_label.add_background_rectangle()
        tuple_label.next_to(dot, RIGHT, SMALL_BUFF)
        line = Line(self.plane.get_center_point(), point)
        line.highlight(dot.get_color())
        distance_labels = VGroup()
        for tex in "2^2 + 1^2", "5":
            pre_label = TexMobject("\\sqrt{%s}"%tex)
            rect = BackgroundRectangle(pre_label)
            label = VGroup(
                rect,
                VGroup(*pre_label[:2]),
                VGroup(*pre_label[2:]),
            )
            label.scale(0.8)
            label.next_to(line.get_center(), UP, SMALL_BUFF)
            label.rotate(
                line.get_angle(),
                about_point = line.get_center()
            )
            distance_labels.add(label)

        self.play(
            ShowCreation(line),
            DrawBorderThenFill(
                dot,
                stroke_width = 3,
                stroke_color = PINK
            )
        )
        self.play(Write(tuple_label))
        self.dither()
        self.play(FadeIn(distance_labels[0]))
        self.dither(2)
        self.play(Transform(*distance_labels))
        self.dither(2)

        self.distance_label = distance_labels[0]
        self.example_dot = dot
        self.example_line = line
        self.example_tuple_label = tuple_label

    def view_as_complex_number(self):
        imag_coords = VGroup()
        for y in range(-4, 5, 2):
            if y == 0:
                continue
            label = TexMobject("%di"%y)
            label.add_background_rectangle()
            label.scale(0.75)
            label.next_to(
                self.plane.coords_to_point(0, y),
                LEFT, SMALL_BUFF
            )
            imag_coords.add(label)
        tuple_label = self.example_tuple_label
        new_label = TexMobject("2+i")
        new_label.add_background_rectangle()
        new_label.next_to(
            self.example_dot,
            DOWN+RIGHT, buff = 0,
        )

        self.play(Write(imag_coords))
        self.dither()
        self.play(FadeOut(tuple_label))
        self.play(FadeIn(new_label))
        self.dither(2)

        self.example_label = new_label
        self.plane.coordinate_labels.add(*imag_coords)

    def mention_squaring_it(self):
        morty = self.pi_creature
        arrow = Arrow(
            self.plane.coords_to_point(2, 1),
            self.plane.coords_to_point(3, 4),
            path_arc = np.pi/3,
            color = MAROON_B
        )
        square_label = TexMobject("z \\to z^2")
        square_label.highlight(arrow.get_color())
        square_label.add_background_rectangle()
        square_label.next_to(
            arrow.point_from_proportion(0.5), 
            RIGHT, buff = SMALL_BUFF
        )

        self.play(FadeIn(morty))
        self.play(
            PiCreatureSays(
                morty, "Try squaring \\\\ it!",
                target_mode = "hooray",
                bubble_kwargs = {"width" : 4, "height" : 3},
            )
        )
        self.play(
            ShowCreation(arrow),
            Write(square_label)
        )
        self.dither()
        self.play(RemovePiCreatureBubble(
            morty, target_mode = "pondering",
            look_at_arg = self.example_label
        ))

    def work_out_square_algebraically(self):
        rect = Rectangle(
            height = 3.5, width = 6.5,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8
        )
        rect.to_corner(UP+LEFT, buff = 0)
        top_line = TexMobject("(2+i)", "(2+i)")
        top_line.next_to(rect.get_top(), DOWN)
        second_line = TexMobject(
            "2^2 + 2i + 2i + i^2"
        )
        second_line.next_to(top_line, DOWN, MED_LARGE_BUFF)
        final_line = TexMobject("3 + 4i")
        final_line.next_to(second_line, DOWN, MED_LARGE_BUFF)

        result_dot = Dot(
            self.plane.coords_to_point(3, 4),
            color = MAROON_B,
            radius = self.dot_radius
        )

        self.play(
            FadeIn(rect),
            ReplacementTransform(
                VGroup(self.example_label[1].copy()),
                top_line
            ),
            run_time = 2
        )
        self.dither()

        #From top line to second line
        index_alignment_lists = [
            [(0, 1, 0), (1, 1, 1)],
            [(0, 2, 2), (0, 1, 3), (1, 3, 4)],
            [(0, 2, 5), (1, 1, 6), (0, 3, 7)],
            [(0, 2, 8), (0, 3, 9), (1, 3, 10)],
        ]
        for index_alignment in index_alignment_lists:
            self.play(*[
                ReplacementTransform(
                    top_line[i][j].copy(), second_line[k],
                )
                for i, j, k in index_alignment
            ])
        self.dither(2)

        #From second line to final line
        index_alignment_lists = [
            [(0, 0), (1, 0), (9, 0), (10, 0)],
            [(2, 1), (3, 2), (4, 3), (6, 2), (7, 3)],
        ]
        for index_alignment in index_alignment_lists:
            self.play(*[
                ReplacementTransform(
                    second_line[i].copy(), final_line[j],
                    run_time = 1.5
                )
                for i, j in index_alignment
            ])
            self.dither()

        #Move result to appropriate place
        result_label = final_line.copy()
        result_label.add_background_rectangle()
        self.play(
            result_label.next_to, result_dot, UP+RIGHT, SMALL_BUFF,
            Animation(final_line),
            run_time = 2,
        )
        self.play(DrawBorderThenFill(
            result_dot,
            stroke_width = 4,
            stroke_color = PINK
        ))
        self.dither(2)

    def walk_through_square_geometrically(self):
        line = self.example_line
        dot = self.example_dot
        example_label = self.example_label
        distance_label = self.distance_label

        alt_line = line.copy().highlight(RED)
        arc = Arc(
            angle = line.get_angle(),
            radius = 0.7,
            color = WHITE
        )
        double_arc = Arc(
            angle = 2*line.get_angle(),
            radius = 0.8,
            color = RED,
        )
        theta = TexMobject("\\theta")
        two_theta = TexMobject("2\\theta")
        for tex_mob, arc_mob in (theta, arc), (two_theta, double_arc):
            tex_mob.scale(0.75)
            tex_mob.add_background_rectangle()
            point = arc_mob.point_from_proportion(0.5)
            tex_mob.move_to(point)
            tex_mob.shift(tex_mob.get_width()*point/np.linalg.norm(point))


        self.play(self.pi_creature.change, "happy", arc)
        self.play(ShowCreation(alt_line))
        self.play(ShowCreation(line))
        self.remove(alt_line)
        self.dither()
        self.play(
            ShowCreation(arc),
            Write(theta)
        )
        self.dither()
        self.play(Indicate(distance_label))
        self.dither()

        #Multiply full plane under everything
        everything = VGroup(*self.get_top_level_mobjects())
        everything.remove(self.plane)
        self.plane.save_state()
        ghost_plane = self.plane.copy().fade()
        method_args_list = [
            (self.plane.rotate, (line.get_angle(),)),
            (self.plane.scale, (np.sqrt(5),)),
            (self.plane.restore, ()),
        ]
        for method, args in method_args_list:
            self.play(
                Animation(ghost_plane),
                ApplyMethod(method, *args),
                Animation(everything),
                run_time = 1.5
            )
            self.dither()

        #Multiply number by itself
        ghost_arc = arc.copy().fade()
        ghost_line = line.copy().fade()
        ghots_dot = dot.copy().fade()
        self.add(ghost_arc, ghost_line, ghots_dot)

        self.play(
            VGroup(
                line, dot, distance_label,
            ).rotate, line.get_angle(),
            Transform(arc, double_arc),
            Transform(theta, two_theta),
        )
        self.dither()
        five = distance_label[2]
        distance_label.remove(five)
        for mob in five, line, dot:
            mob.generate_target()
        line.target.scale(np.sqrt(5))
        five.target.shift(line.target.get_center()-line.get_center())
        dot.target.move_to(line.target.get_end())
        self.play(
            FadeOut(distance_label),
            *map(MoveToTarget, [five, line, dot]),
            run_time = 2
        )
        self.dither(2)

    ####

    def get_all_plane_dots(self):
        x_min, y_min = map(int, self.plane.point_to_coords(
            SPACE_WIDTH*LEFT + SPACE_HEIGHT*DOWN
        ))
        x_max, y_max = map(int, self.plane.point_to_coords(
            SPACE_WIDTH*RIGHT + SPACE_HEIGHT*UP
        ))
        result = VGroup(*[
            Dot(
                self.plane.coords_to_point(x, y),
                radius = self.dot_radius,
                color = self.dot_color,
            )
            for x in range(int(x_min), int(x_max)+1)
            for y in range(int(y_min), int(y_max)+1)
        ])
        result.sort_submobjects(lambda p : np.dot(p, UP+RIGHT))
        return result

    def create_pi_creature(self):
        morty = Mortimer().flip()
        morty.to_corner(DOWN+LEFT, buff = MED_SMALL_BUFF)
        return morty

class OneMoreExample(Scene):
    CONFIG = {
        "unit_size" : 0.5,
        "plane_center" : 3*LEFT + 3*DOWN,
        "dot_color" : YELLOW,
    }
    def construct(self):
        self.force_skipping()

        self.add_plane()
        self.add_point()
        self.square_algebraically()
        self.plot_result()
        self.show_triangle()

    def add_plane(self):
        plane = ComplexPlane(
            unit_size = self.unit_size,
            center_point = self.plane_center,
            stroke_width = 2,
        )
        plane.axes.set_stroke(width = 4)
        coordinate_labels = VGroup()
        for x in range(-6, 25, 3):
            if x == 0:
                continue
            coord = TexMobject(str(x))
            coord.scale(0.75)
            coord.next_to(plane.coords_to_point(x, 0), DOWN, SMALL_BUFF)
            coord.add_background_rectangle()
            coordinate_labels.add(coord)
        for y in range(3, 13, 3):
            if y == 0:
                continue
            coord = TexMobject("%di"%y)
            coord.scale(0.75)
            coord.next_to(plane.coords_to_point(0, y), LEFT, SMALL_BUFF)
            coord.add_background_rectangle()
            coordinate_labels.add(coord)
        self.add(plane, coordinate_labels)

        self.plane = plane
        self.plane.coordinate_labels = coordinate_labels

    def add_point(self):
        point = self.plane.coords_to_point(3, 2)
        dot = Dot(point, color = self.dot_color)
        line = Line(self.plane.get_center_point(), point)
        line.highlight(dot.get_color())
        tuple_label = TexMobject("3+2i")
        tuple_label.add_background_rectangle()
        tuple_label.next_to(dot, RIGHT, SMALL_BUFF)
        distance_labels = VGroup() 
        for tex in "3^2 + 2^2", "13":
            pre_label = TexMobject("\\sqrt{%s}"%tex)
            label = VGroup(
                BackgroundRectangle(pre_label),
                VGroup(*pre_label[:2]),
                VGroup(*pre_label[2:]),
            )
            label.scale(0.75)
            label.next_to(line.get_center(), UP, SMALL_BUFF)
            label.rotate(
                line.get_angle(),
                about_point = line.get_center()
            )
            distance_labels.add(label)

        self.revert_to_original_skipping_status()
        self.play(
            FadeIn(tuple_label), 
            ShowCreation(line),
            DrawBorderThenFill(dot)
        )
        self.play(Write(distance_labels[0]))
        self.dither()
        self.play(ReplacementTransform(*distance_labels))
        self.dither()

        self.distance_label = distance_labels[1]
        self.line = line
        self.dot = dot
        self.tuple_label = tuple_label

    def square_algebraically(self):
        pass

    def plot_result(self):
        pass

    def show_triangle(self):
        pass

































