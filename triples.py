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
U_COLOR = GREEN
V_COLOR = RED

#revert_to_original_skipping_status

def complex_string_with_i(z):
    return complex_string(z).replace("j", "i")

class IntroduceTriples(TeacherStudentsScene):
    def construct(self):
        title = TexMobject("a", "^2", "+", "b", "^2", "=", "c", "^2")
        for color, char in zip(SIDE_COLORS, "abc"):
            title.highlight_by_tex(char, color)
        title.to_corner(UP + RIGHT)

        triples = [
            (3, 4, 5), 
            (5, 12, 13),
            (8, 15, 17),
        ]

        self.add(title)
        for a, b, c in triples:
            triangle = Polygon(
                ORIGIN, a*RIGHT, a*RIGHT+b*UP,
                stroke_width = 0,
                fill_color = WHITE,
                fill_opacity = 0.5
            )
            hyp_line = Line(ORIGIN, a*RIGHT+b*UP)
            elbow = VMobject()
            elbow.set_points_as_corners([LEFT, LEFT+UP, UP])
            elbow.scale_to_fit_width(0.2*triangle.get_width())
            elbow.move_to(triangle, DOWN+RIGHT)
            triangle.add(elbow)

            square = Square(side_length = 1)
            square_groups = VGroup()
            for n, color in zip([a, b, c], SIDE_COLORS):
                square_group = VGroup(*[
                    square.copy().shift(x*RIGHT + y*UP)
                    for x in range(n)
                    for y in range(n)
                ])
                square_group.set_stroke(color, width = 3)
                square_group.set_fill(color, opacity = 0.5)
                square_groups.add(square_group)
            a_square, b_square, c_square = square_groups
            a_square.move_to(triangle.get_bottom(), UP)
            b_square.move_to(triangle.get_right(), LEFT)
            c_square.move_to(hyp_line.get_center(), DOWN)
            c_square.rotate(
                hyp_line.get_angle(),
                about_point = hyp_line.get_center()
            )
            if c in [5, 13]:
                if c == 5:
                    keys = range(0, 5, 2)
                elif c == 13:
                    keys = range(0, 13, 3)
                i_list = filter(
                    lambda i : (i%c) in keys and (i//c) in keys,
                    range(c**2)
                )
            else:
                i_list = range(a**2)
            not_i_list = filter(
                lambda i : i not in i_list,
                range(c**2),
            )
            c_square_parts = [
                VGroup(*[c_square[i] for i in i_list]),
                VGroup(*[c_square[i] for i in not_i_list]),
            ]
            full_group = VGroup(triangle, square_groups)
            full_group.scale_to_fit_height(4)
            full_group.center()
            full_group.to_edge(UP)

            equation = TexMobject(
                str(a), "^2", "+", str(b), "^2", "=", str(c), "^2"
            )
            for num, color in zip([a, b, c], SIDE_COLORS):
                equation.highlight_by_tex(str(num), color)
            equation.next_to(title, DOWN, MED_LARGE_BUFF)
            equation.shift_onto_screen()
            
            self.play(
                FadeIn(triangle),
                self.teacher.change_mode, "raise_right_hand"
            )
            self.play(LaggedStart(FadeIn, a_square))
            self.change_student_modes(
                *["pondering"]*3,
                look_at_arg = triangle,
                added_anims = [LaggedStart(FadeIn, b_square)]
            )
            self.play(self.teacher.change_mode, "happy")
            for start, target in zip([a_square, b_square], c_square_parts):
                mover = start.copy().set_fill(opacity = 0)
                target.highlight(start.get_color())
                self.play(ReplacementTransform(
                    mover, target,
                    run_time = 2,
                    path_arc = np.pi/2
                ))
            self.play(Write(equation))
            self.play(c_square.highlight, C_COLOR)
            self.dither()
            self.play(*map(FadeOut, [full_group, equation]))

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

class WritePythagoreanTriple(Scene):
    def construct(self):
        words = TextMobject("``Pythagorean triple''")
        words.scale_to_fit_width(2*SPACE_WIDTH - LARGE_BUFF)
        words.to_corner(DOWN+LEFT)
        self.play(Write(words))
        self.dither(2)

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
        side_labels = self.get_triangle_side_labels(triangle)
        triangle_copy = triangle.copy()
        squares = self.get_abc_squares(triangle)
        a_square, b_square, c_square = squares


        self.add(triangle, triangle_copy)
        self.play(Write(side_labels))
        self.dither()
        self.play(*map(DrawBorderThenFill, squares))
        self.add_labels_to_squares(squares, side_labels)
        self.dither()
        self.play(
            VGroup(triangle_copy, a_square, b_square).move_to, 
                4*LEFT+2*DOWN, DOWN,
            VGroup(triangle, c_square).move_to, 
                4*RIGHT+2*DOWN, DOWN,
            run_time = 2,
            path_arc = np.pi/2,
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

    def add_labels_to_squares(self, squares, side_labels):
        for label, square in zip(side_labels, squares):
            label.target = TexMobject(label.get_tex_string() + "^2")
            label.target.highlight(label.get_color())
            # label.target.scale(0.7)
            label.target.move_to(square)
            square.add(label)

        self.play(LaggedStart(MoveToTarget, side_labels))

    def add_new_triangles(self, triangle, added_triangles):
        brace = Brace(added_triangles, DOWN)
        label = TexMobject("a", "+", "b")
        label.highlight_by_tex("a", A_COLOR)
        label.highlight_by_tex("b", B_COLOR)
        label.next_to(brace, DOWN)

        self.play(ReplacementTransform(
            VGroup(triangle.copy().set_fill(opacity = 0)),
            added_triangles,
            run_time = 2,
        ))
        self.play(GrowFromCenter(brace))
        self.play(Write(label))
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

    def get_triangle_side_labels(self, triangle):
        a, b, c = map(TexMobject, "abc")
        for mob, color in zip([a, b, c], SIDE_COLORS):
            mob.highlight(color)
        a.next_to(triangle, DOWN)
        b.next_to(triangle, RIGHT)
        c.next_to(triangle.get_center(), LEFT)
        return VGroup(a, b, c)

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

##TODO, REMOVE
class LastVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Pi hiding in prime regularities")
        title.to_edge(UP)
        screen_rect = ScreenRectangle(height = 6)
        screen_rect.next_to(title, DOWN)

        self.play(ShowCreation(screen_rect))
        self.play(Write(title))
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
        "x_label_range" : range(-6, 25, 3),
        "y_label_range" : range(3, 13, 3),
    }
    def construct(self):
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
        for x in self.x_label_range:
            if x == 0:
                continue
            coord = TexMobject(str(x))
            coord.scale(0.75)
            coord.next_to(plane.coords_to_point(x, 0), DOWN, SMALL_BUFF)
            coord.add_background_rectangle()
            coordinate_labels.add(coord)
        for y in self.y_label_range:
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
        number_label = TexMobject("3+2i")
        number_label.add_background_rectangle()
        number_label.next_to(dot, RIGHT, SMALL_BUFF)
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

        self.play(
            FadeIn(number_label), 
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
        self.number_label = number_label

    def square_algebraically(self):
        #Crazy hacky.  To anyone looking at this, for God's
        #sake, don't mimic this.
        rect = Rectangle(
            height = 3.5, width = 7,
            stroke_color = WHITE,
            stroke_width = 2,
            fill_color = BLACK,
            fill_opacity = 0.8
        )
        rect.to_corner(UP+RIGHT, buff = 0)
        number = self.number_label[1].copy()

        top_line = TexMobject("(3+2i)", "(3+2i)")
        for part in top_line:
            for i, color in zip([1, 3], [BLUE, YELLOW]):
                part[i].highlight(color)
        second_line = TexMobject(
            "\\big( 3^2 + (2i)^2 \\big) + " + \
            "\\big(3 \\cdot 2 + 2 \\cdot 3 \\big)i"
        )
        for i in 1, 12, 18:
            second_line[i].highlight(BLUE)
        for i in 5, 14, 16:
            second_line[i].highlight(YELLOW)
        second_line.scale(0.9)
        final_line = TexMobject("5 + 12i")
        for i in 0, 2, 3:
            final_line[i].highlight(GREEN)
        lines = VGroup(top_line, second_line, final_line)
        lines.arrange_submobjects(DOWN, buff = MED_LARGE_BUFF)
        lines.next_to(rect.get_top(), DOWN)
        minus = TexMobject("-").scale(0.9)
        minus.move_to(second_line[3])

        self.play(
            FadeIn(rect),
            Transform(VGroup(number), top_line),
            run_time = 2
        )
        self.dither()

        index_alignment_lists = [
            [(0, 0, 0), (0, 1, 1), (1, 1, 2), (1, 5, 9)],
            [
                (0, 2, 3), (1, 3, 4), (0, 3, 5), 
                (0, 4, 6), (1, 4, 7), (1, 3, 8)
            ],
            [
                (0, 2, 10), (0, 0, 11), (0, 1, 12), 
                (1, 3, 13), (1, 3, 14), (1, 5, 19), 
                (0, 4, 20), (1, 4, 20),
            ],
            [
                (0, 2, 15), (0, 3, 16), 
                (1, 1, 17), (1, 1, 18),
            ],
        ]
        for index_alignment in index_alignment_lists[:2]:
            self.play(*[
                ReplacementTransform(
                    top_line[i][j].copy(), second_line[k],
                    run_time = 1.5
                )
                for i, j, k in index_alignment
            ])
            self.dither()
        self.play(
            Transform(second_line[3], minus),
            FadeOut(VGroup(*[
                second_line[i]
                for i in 4, 6, 7
            ])),
            second_line[5].shift, 0.35*RIGHT,
        )
        self.play(VGroup(*second_line[:4]).shift, 0.55*RIGHT)
        self.dither()
        for index_alignment in index_alignment_lists[2:]:
            self.play(*[
                ReplacementTransform(
                    top_line[i][j].copy(), second_line[k],
                    run_time = 1.5
                )
                for i, j, k in index_alignment
            ])
            self.dither()
        self.play(FadeIn(final_line))
        self.dither()

        self.final_line = final_line

    def plot_result(self):
        result_label = self.final_line.copy()
        result_label.add_background_rectangle()

        point = self.plane.coords_to_point(5, 12)
        dot = Dot(point, color = GREEN)
        line = Line(self.plane.get_center_point(), point)
        line.highlight(dot.get_color())
        distance_label = TexMobject("13")
        distance_label.add_background_rectangle()
        distance_label.next_to(line.get_center(), UP+LEFT, SMALL_BUFF)

        self.play(
            result_label.next_to, dot, UP+LEFT, SMALL_BUFF,
            Animation(self.final_line),
            DrawBorderThenFill(dot)
        )
        self.dither()
        self.play(*[
            ReplacementTransform(m1.copy(), m2)
            for m1, m2 in [
                (self.line, line), 
                (self.distance_label, distance_label)
            ]
        ])
        self.dither()

    def show_triangle(self):
        triangle = Polygon(*[
            self.plane.coords_to_point(x, y)
            for x, y in [(0, 0), (5, 0), (5, 12)]
        ])
        triangle.set_stroke(WHITE, 1)
        triangle.set_fill(BLUE, opacity = 0.75)

        self.play(
            FadeIn(triangle),
            Animation(VGroup(
                self.line, self.dot, 
                self.number_label[1], *self.distance_label[1:]
            )),
            run_time = 2
        )
        self.dither(2)

class ThisIsMagic(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "This is magic", target_mode = "hooray"
        )
        self.play(self.teacher.change, "happy")
        self.dither(2)

class GeneralExample(OneMoreExample):
    CONFIG = {
        "number" : complex(4, 1),
        "square_color" : MAROON_B,
        "result_label_vect" : UP+LEFT,
    }
    def construct(self):
        self.add_plane()
        self.square_point()

    def square_point(self):
        z = self.number
        z_point = self.plane.number_to_point(z)
        zero_point = self.plane.number_to_point(0)
        dot = Dot(z_point, color = self.dot_color)
        line = Line(zero_point, z_point)
        line.highlight(dot.get_color())
        label = TexMobject(complex_string_with_i(z))
        label.add_background_rectangle()
        label.next_to(dot, RIGHT, SMALL_BUFF)

        square_point = self.plane.number_to_point(z**2)
        square_dot = Dot(square_point, color = self.square_color)
        square_line = Line(zero_point, square_point)
        square_line.highlight(square_dot.get_color())
        square_label = TexMobject(complex_string_with_i(z**2))
        square_label.add_background_rectangle()
        square_label.next_to(square_dot, UP+RIGHT, SMALL_BUFF)
        result_length_label = TexMobject(str(int(abs(z**2))))
        result_length_label.next_to(
            square_line.get_center(), self.result_label_vect
        )
        result_length_label.add_background_rectangle()

        arrow = Arrow(
            z_point, square_point, 
            # buff = SMALL_BUFF,
            path_arc = np.pi/2
        )
        arrow.highlight(WHITE)
        z_to_z_squared = TexMobject("z", "\\to", "z^2")
        z_to_z_squared.highlight_by_tex("z", dot.get_color())
        z_to_z_squared.highlight_by_tex("z^2", square_dot.get_color())
        z_to_z_squared.next_to(
            arrow.point_from_proportion(0.5), 
            RIGHT, MED_SMALL_BUFF
        )
        z_to_z_squared.add_to_back(
            BackgroundRectangle(VGroup(
                z_to_z_squared[2][0],
                *z_to_z_squared[:-1]
            )),
            BackgroundRectangle(z_to_z_squared[2][1])
        )


        self.play(
            Write(label), 
            ShowCreation(line),
            DrawBorderThenFill(dot)
        )
        self.dither()
        self.play(
            ShowCreation(arrow),
            FadeIn(z_to_z_squared),
            Animation(label),
        )
        self.play(*[
            ReplacementTransform(
                start.copy(), target,
                path_arc = np.pi/2,
                run_time = 1.5
            )
            for start, target in [
                (dot, square_dot),
                (line, square_line),
                (label, square_label),
            ]
        ])
        self.dither()
        self.play(Write(result_length_label))
        self.dither()

        self.example_dot = dot
        self.example_label = label
        self.example_line = line
        self.square_dot = square_dot
        self.square_label = square_label
        self.square_line = square_line
        self.z_to_z_squared = z_to_z_squared
        self.z_to_z_squared_arrow = arrow
        self.result_length_label = result_length_label

class BoringExample(GeneralExample):
    CONFIG = {
        "number" : complex(2, 2),
        "result_label_vect" : RIGHT,
    }
    def construct(self):
        self.add_plane()
        self.square_point()
        self.show_associated_triplet()

    def show_associated_triplet(self):
        arrow = Arrow(LEFT, RIGHT, color = GREEN)
        arrow.next_to(self.square_label, RIGHT)
        triple = TexMobject("0^2 + 8^2 = 8^2")
        for part, color in zip(triple[::3], SIDE_COLORS):
            part.highlight(color)
        triple.add_background_rectangle()
        triple.next_to(arrow, RIGHT)

        morty = Mortimer()
        morty.next_to(self.plane.coords_to_point(12, 0), UP)

        self.play(
            ShowCreation(arrow),
            FadeIn(morty)
        )
        self.play(
            Write(triple),
            morty.change, "raise_right_hand", triple
        )
        self.play(Blink(morty))
        self.play(morty.change, "tired")
        self.dither(2)
        self.play(Blink(morty))
        self.dither()

class FiveTwoExample(GeneralExample):
    CONFIG = {
        "number" : complex(5, 2),
        "unit_size" : 0.25,
        "x_label_range" : range(-10, 40, 5),
        "y_label_range" : range(0, 30, 5),
    }

class WriteGeneralFormula(GeneralExample):
    CONFIG = {
        "plane_center" : 2*RIGHT,
        "x_label_range" : [],
        "y_label_range" : [],
        "unit_size" : 0.7,
        "number" : complex(2, 1),
    }
    def construct(self):
        self.add_plane()
        self.show_squaring()
        self.expand_square()
        self.draw_triangle()
        self.show_uv_to_triples()

    def show_squaring(self):
        self.force_skipping()
        self.square_point()
        dot = self.example_dot
        old_label = self.example_label
        line = self.example_line
        square_dot = self.square_dot
        old_square_label = self.square_label
        square_line = self.square_line
        z_to_z_squared = self.z_to_z_squared
        arrow = self.z_to_z_squared_arrow
        result_length_label = self.result_length_label
        self.clear()
        self.add(self.plane, self.plane.coordinate_labels)
        self.revert_to_original_skipping_status()

        label = TexMobject("u+vi")
        label.move_to(old_label, LEFT)
        label.add_background_rectangle()
        square_label = TexMobject("(u+vi)^2")
        square_label.move_to(old_square_label, LEFT)
        square_label.add_background_rectangle()

        self.add(label, dot, line)
        self.play(
            ShowCreation(arrow),
            FadeIn(z_to_z_squared)
        )
        self.play(*[
            ReplacementTransform(
                start.copy(), target,
                run_time = 1.5,
                path_arc = np.pi/2
            )
            for start, target in [
                (dot, square_dot),
                (line, square_line),
                (label, square_label),
            ]
        ])

        self.example_label = label
        self.square_label = square_label

    def expand_square(self):
        rect = Rectangle(
            height = 2.5, width = 7,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        rect.to_corner(UP+LEFT, buff = 0)
        top_line = TexMobject("(u+vi)(u+vi)")
        for i in 1, 7:
            top_line[i].highlight(U_COLOR)
            top_line[i+2].highlight(V_COLOR)
        top_line.next_to(rect.get_top(), DOWN)
        second_line = TexMobject(
            "\\big(", "u^2 - v^2", "\\big)", "+",
            "\\big(", "2uv", "\\big)", "i"
        )
        for i, j in (1, 0), (5, 1):
            second_line[i][j].highlight(U_COLOR)
        for i, j in (1, 3), (5, 2):
            second_line[i][j].highlight(V_COLOR)
        second_line.next_to(top_line, DOWN, MED_LARGE_BUFF)
        real_part = second_line[1]
        imag_part = second_line[5]
        for part in real_part, imag_part:
            part.add_to_back(BackgroundRectangle(part))

        z = self.number**2
        square_point = self.plane.number_to_point(z)
        zero_point = self.plane.number_to_point(0)
        real_part_point = self.plane.number_to_point(z.real)
        real_part_line = Line(zero_point, real_part_point)
        imag_part_line = Line(real_part_point, square_point)
        for line in real_part_line, imag_part_line:
            line.highlight(self.square_color)


        self.play(*map(FadeIn, [rect, top_line, second_line]))
        self.dither()
        self.play(
            real_part.copy().next_to, real_part_line.copy(), 
                DOWN, SMALL_BUFF,
            ShowCreation(real_part_line)
        )
        self.dither()
        self.play(
            FadeOut(VGroup(
                self.example_label, self.example_dot, self.example_line,
                self.z_to_z_squared, self.z_to_z_squared_arrow
            )),
            imag_part.copy().next_to, imag_part_line.copy(), 
                RIGHT, SMALL_BUFF,
            ShowCreation(imag_part_line)
        )
        self.dither()

        self.corner_rect = rect

    def draw_triangle(self):
        hyp_length = TexMobject("u", "^2", "+", "v", "^2")
        hyp_length.highlight_by_tex("u", U_COLOR)
        hyp_length.highlight_by_tex("v", V_COLOR)
        hyp_length.add_background_rectangle()
        line = self.square_line
        hyp_length.next_to(line.get_center(), UP, SMALL_BUFF)
        hyp_length.rotate(
            line.get_angle(),
            about_point = line.get_center()
        )
        triangle = Polygon(
            ORIGIN, RIGHT, RIGHT+UP,
            stroke_width = 0,
            fill_color = MAROON_B,
            fill_opacity = 0.5,
        )
        triangle.replace(line, stretch = True)

        self.play(Write(hyp_length))
        self.dither()
        self.play(FadeIn(triangle))
        self.dither()

    def show_uv_to_triples(self):
        rect = self.corner_rect.copy()
        rect.stretch_to_fit_height(2*SPACE_HEIGHT)
        rect.move_to(self.corner_rect.get_bottom(), UP)

        h_line = Line(rect.get_left(), rect.get_right())
        h_line.next_to(rect.get_top(), DOWN, LARGE_BUFF)
        v_line = Line(rect.get_top(), rect.get_bottom())
        v_line.shift(1.3*LEFT)
        uv_title = TexMobject("(u, v)")
        triple_title = TexMobject("(u^2 - v^2, 2uv, u^2 + v^2)")
        uv_title.scale(0.75)
        triple_title.scale(0.75)
        uv_title.next_to(
            h_line.point_from_proportion(1./6), 
            UP, SMALL_BUFF
        )
        triple_title.next_to(
            h_line.point_from_proportion(2./3),
            UP, SMALL_BUFF
        )

        pairs = [(2, 1), (3, 2), (4, 1), (4, 3), (5, 2), (5, 4)]
        pair_mobs = VGroup()
        triple_mobs = VGroup()
        for u, v in pairs:
            a, b, c = u**2 - v**2, 2*u*v, u**2 + v**2
            pair_mob = TexMobject("(", str(u), ",", str(v), ")")
            pair_mob.highlight_by_tex(str(u), U_COLOR)
            pair_mob.highlight_by_tex(str(v), V_COLOR)
            triple_mob = TexMobject("(%d, %d, %d)"%(a, b, c))
            pair_mobs.add(pair_mob)
            triple_mobs.add(triple_mob)
            pair_mob.scale(0.75)
            triple_mob.scale(0.75)
        pair_mobs.arrange_submobjects(DOWN)
        pair_mobs.next_to(uv_title, DOWN, MED_LARGE_BUFF)
        triple_mobs.arrange_submobjects(DOWN)
        triple_mobs.next_to(triple_title, DOWN, MED_LARGE_BUFF)

        self.play(*map(FadeIn, [
            rect, h_line, v_line, 
            uv_title, triple_title
        ]))
        self.play(*[
            LaggedStart(
                FadeIn, mob, 
                run_time = 5,
                lag_ratio = 0.2
            )
            for mob in pair_mobs, triple_mobs
        ])























