import fractions
from manimlib.imports import *

A_COLOR = BLUE
B_COLOR = GREEN
C_COLOR = YELLOW
SIDE_COLORS = [A_COLOR, B_COLOR, C_COLOR]
U_COLOR = GREEN
V_COLOR = RED

#revert_to_original_skipping_status

def complex_string_with_i(z):
    if z.real == 0:
        return str(int(z.imag)) + "i"
    elif z.imag == 0:
        return str(int(z.real))
    return complex_string(z).replace("j", "i")

class IntroduceTriples(TeacherStudentsScene):
    def construct(self):
        title = TexMobject("a", "^2", "+", "b", "^2", "=", "c", "^2")
        for color, char in zip(SIDE_COLORS, "abc"):
            title.set_color_by_tex(char, color)
        title.to_corner(UP + RIGHT)

        triples = [
            (3, 4, 5), 
            (5, 12, 13),
            (8, 15, 17),
            (7, 24, 25),
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
            elbow.set_width(0.2*triangle.get_width())
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
            if c in [5, 13, 25]:
                if c == 5:
                    keys = list(range(0, 5, 2))
                elif c == 13:
                    keys = list(range(0, 13, 3))
                elif c == 25:
                    keys = list(range(0, 25, 4))
                i_list = [i for i in range(c**2) if (i%c) in keys and (i//c) in keys]
            else:
                i_list = list(range(a**2))
            not_i_list = list(filter(
                lambda i : i not in i_list,
                list(range(c**2)),
            ))
            c_square_parts = [
                VGroup(*[c_square[i] for i in i_list]),
                VGroup(*[c_square[i] for i in not_i_list]),
            ]
            full_group = VGroup(triangle, square_groups)
            full_group.set_height(4)
            full_group.center()
            full_group.to_edge(UP)

            equation = TexMobject(
                str(a), "^2", "+", str(b), "^2", "=", str(c), "^2"
            )
            for num, color in zip([a, b, c], SIDE_COLORS):
                equation.set_color_by_tex(str(num), color)
            equation.next_to(title, DOWN, MED_LARGE_BUFF)
            equation.shift_onto_screen()
            
            self.play(
                FadeIn(triangle),
                self.teacher.change_mode, "raise_right_hand"
            )
            self.play(LaggedStartMap(FadeIn, a_square))
            self.change_student_modes(
                *["pondering"]*3,
                look_at_arg = triangle,
                added_anims = [LaggedStartMap(FadeIn, b_square)]
            )
            self.play(self.teacher.change_mode, "happy")
            for start, target in zip([a_square, b_square], c_square_parts):
                mover = start.copy().set_fill(opacity = 0)
                target.set_color(start.get_color())
                self.play(ReplacementTransform(
                    mover, target,
                    run_time = 2,
                    path_arc = np.pi/2
                ))
            self.play(Write(equation))
            self.play(c_square.set_color, C_COLOR)
            self.wait()
            self.play(*list(map(FadeOut, [full_group, equation])))

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
                expression.set_color_by_tex(char, color)
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
        low_text.set_color(RED)

        self.add(square_expression, top_brace, top_text)
        self.change_student_modes(*["pondering"]*3)
        self.play(self.teacher.change, "happy", run_time = 0)
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
        self.wait()
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
            self.wait()

class WritePythagoreanTriple(Scene):
    def construct(self):
        words = TextMobject("``Pythagorean triple''")
        words.set_width(FRAME_WIDTH - LARGE_BUFF)
        words.to_corner(DOWN+LEFT)
        self.play(Write(words))
        self.wait(2)

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
            triangle.set_color(WHITE)
            max_width = max_height = 4
            triangle.set_height(max_height)
            if triangle.get_width() > max_width:
                triangle.set_width(max_width)
            triangle.move_to(2*RIGHT)
            num_strings = list(map(str, (a, b, c)))
            labels = list(map(TexMobject, num_strings))
            for label, color in zip(labels, SIDE_COLORS):
                label.set_color(color)
            labels[0].next_to(triangle, DOWN)
            labels[1].next_to(triangle, RIGHT)
            labels[2].next_to(triangle.get_center(), UP+LEFT)
            triangle.add(*labels)

            title = TexMobject(
                str(a), "^2", "+", str(b), "^2", "=", str(c), "^2"
            )
            for num, color in zip([a, b, c], SIDE_COLORS):
                title.set_color_by_tex(str(num), color)
            title.next_to(triangle, UP, LARGE_BUFF)
            title.generate_target()
            title.target.scale(0.5)

            title.target.move_to(
                (-FRAME_X_RADIUS + MED_LARGE_BUFF + 2.7*(i//8))*RIGHT + \
                (FRAME_Y_RADIUS - MED_LARGE_BUFF - (i%8))*UP,
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
        self.wait()
        self.play(MoveToTarget(title))
        for i in range(1, 17):
            new_triangle = triangles[i]
            new_title = titles[i]
            if i < 4:
                self.play(
                    Transform(triangle, new_triangle),
                    FadeIn(new_title)
                )
                self.wait()
                self.play(MoveToTarget(new_title))
            else:
                self.play(
                    Transform(triangle, new_triangle),
                    FadeIn(new_title.target)
                )
                self.wait()
        self.play(FadeOut(triangle))
        self.play(LaggedStartMap(
            FadeIn, 
            VGroup(*[
                title.target 
                for title in titles[17:]
            ]),
            run_time = 5
        ))

        self.wait(2)

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
        triples.arrange(DOWN, aligned_edge = LEFT)
        triples.set_height(FRAME_HEIGHT - LARGE_BUFF)
        triples.to_edge(RIGHT)

        self.add(title)
        self.wait()
        self.play(LaggedStartMap(FadeIn, triples, run_time = 5))
        self.wait()

class AskAboutFavoriteProof(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What's you're \\\\ favorite proof?",
            target_mode = "raise_right_hand"
        )
        self.change_student_modes("happy", "raise_right_hand", "happy")
        self.teacher_thinks("", target_mode = "thinking")
        self.wait()
        self.zoom_in_on_thought_bubble()

class PythagoreanProof(Scene):
    def construct(self):
        self.add_title()
        self.show_proof()

    def add_title(self):
        title = TexMobject("a^2", "+", "b^2", "=", "c^2")
        for color, char in zip(SIDE_COLORS, "abc"):
            title.set_color_by_tex(char, color)
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
        triangle.set_height(3)
        triangle.center()
        side_labels = self.get_triangle_side_labels(triangle)
        triangle_copy = triangle.copy()
        squares = self.get_abc_squares(triangle)
        a_square, b_square, c_square = squares


        self.add(triangle, triangle_copy)
        self.play(Write(side_labels))
        self.wait()
        self.play(*list(map(DrawBorderThenFill, squares)))
        self.add_labels_to_squares(squares, side_labels)
        self.wait()
        self.play(
            VGroup(triangle_copy, a_square, b_square).move_to, 
                4*LEFT+2*DOWN, DOWN,
            VGroup(triangle, c_square).move_to, 
                4*RIGHT+2*DOWN, DOWN,
            run_time = 2,
            path_arc = np.pi/2,
        )
        self.wait()
        self.add_new_triangles(
            triangle, 
            self.get_added_triangles_to_c_square(triangle, c_square)
        )
        self.wait()
        self.add_new_triangles(
            triangle_copy,
            self.get_added_triangles_to_ab_squares(triangle_copy, a_square)
        )
        self.wait()

        big_squares = VGroup(*list(map(
            self.get_big_square,
            [triangle, triangle_copy]
        )))
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
            *list(map(FadeOut, squares))
        )
        self.wait(2)
        self.play(*it.chain(
            list(map(FadeIn, squares)),
            list(map(Animation, big_squares)),
        ))
        self.wait(2)

    def add_labels_to_squares(self, squares, side_labels):
        for label, square in zip(side_labels, squares):
            label.target = TexMobject(label.get_tex_string() + "^2")
            label.target.set_color(label.get_color())
            # label.target.scale(0.7)
            label.target.move_to(square)
            square.add(label)

        self.play(LaggedStartMap(MoveToTarget, side_labels))

    def add_new_triangles(self, triangle, added_triangles):
        brace = Brace(added_triangles, DOWN)
        label = TexMobject("a", "+", "b")
        label.set_color_by_tex("a", A_COLOR)
        label.set_color_by_tex("b", B_COLOR)
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
        a, b, c = list(map(TexMobject, "abc"))
        for mob, color in zip([a, b, c], SIDE_COLORS):
            mob.set_color(color)
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
        a_square.set_width(triangle.get_width())
        a_square.move_to(triangle.get_bottom(), UP)
        b_square.set_height(triangle.get_height())
        b_square.move_to(triangle.get_right(), LEFT)
        hyp_line = Line(
            triangle.get_corner(UP+RIGHT),
            triangle.get_corner(DOWN+LEFT),
        )
        c_square.set_width(hyp_line.get_length())
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
        self.wait()
        for new_group in dot_tuple_groups[1:len(initial_examples)]:
            self.play(Transform(dot_tuple_group, new_group))
            self.wait()
        self.play(LaggedStartMap(
            FadeIn, all_dots,
            rate_func = there_and_back,
            run_time = 3,
            lag_ratio = 0.2,
        ))
        self.wait()
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
        self.wait(2)
        for new_group in dot_tuple_groups[1:]:
            self.play(
                Transform(group, new_group),
                Transform(group.triangle, new_group.triangle),
                Transform(group.line, new_group.line),
            )
            self.wait(2)
        self.play(*list(map(FadeOut, [group, group.triangle, group.line])))

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
            *list(map(MoveToTarget, self.plane.coordinate_labels)),
            run_time = 2
        )
        self.remove(self.plane)
        self.plane = new_plane
        self.plane.coordinate_labels = coordinate_labels 
        self.add(self.plane, coordinate_labels)
        self.wait()

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
        line.set_color(dot.get_color())
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
        self.wait()
        self.play(FadeIn(distance_labels[0]))
        self.wait(2)
        self.play(Transform(*distance_labels))
        self.wait(2)

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
        self.wait()
        self.play(FadeOut(tuple_label))
        self.play(FadeIn(new_label))
        self.wait(2)

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
        square_label.set_color(arrow.get_color())
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
        self.wait()
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
        self.wait()

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
        self.wait(2)

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
            self.wait()

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
        self.wait(2)

    def walk_through_square_geometrically(self):
        line = self.example_line
        dot = self.example_dot
        example_label = self.example_label
        distance_label = self.distance_label

        alt_line = line.copy().set_color(RED)
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
            tex_mob.shift(tex_mob.get_width()*point/get_norm(point))


        self.play(self.pi_creature.change, "happy", arc)
        self.play(ShowCreation(alt_line))
        self.play(ShowCreation(line))
        self.remove(alt_line)
        self.wait()
        self.play(
            ShowCreation(arc),
            Write(theta)
        )
        self.wait()
        self.play(Indicate(distance_label))
        self.wait()

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
            self.wait()

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
        self.wait()
        five = distance_label[2]
        distance_label.remove(five)
        for mob in five, line, dot:
            mob.generate_target()
        line.target.scale(np.sqrt(5))
        five.target.shift(line.target.get_center()-line.get_center())
        dot.target.move_to(line.target.get_end())
        self.play(
            FadeOut(distance_label),
            *list(map(MoveToTarget, [five, line, dot])),
            run_time = 2
        )
        self.wait(2)

    ####

    def get_all_plane_dots(self):
        x_min, y_min = list(map(int, self.plane.point_to_coords(
            FRAME_X_RADIUS*LEFT + FRAME_Y_RADIUS*DOWN
        )))
        x_max, y_max = list(map(int, self.plane.point_to_coords(
            FRAME_X_RADIUS*RIGHT + FRAME_Y_RADIUS*UP
        )))
        result = VGroup(*[
            Dot(
                self.plane.coords_to_point(x, y),
                radius = self.dot_radius,
                color = self.dot_color,
            )
            for x in range(int(x_min), int(x_max)+1)
            for y in range(int(y_min), int(y_max)+1)
        ])
        result.sort(lambda p : np.dot(p, UP+RIGHT))
        return result

    def create_pi_creature(self):
        morty = Mortimer().flip()
        morty.to_corner(DOWN+LEFT, buff = MED_SMALL_BUFF)
        return morty

class TimeToGetComplex(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Time to \\\\ get complex")
        self.change_student_modes("angry", "sassy", "pleading")
        self.wait(2)

class OneMoreExample(Scene):
    CONFIG = {
        "unit_size" : 0.5,
        "plane_center" : 3*LEFT + 3*DOWN,
        "dot_color" : YELLOW,
        "x_label_range" : list(range(-6, 25, 3)),
        "y_label_range" : list(range(3, 13, 3)),
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
        line.set_color(dot.get_color())
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
        self.wait()
        self.play(ReplacementTransform(*distance_labels))
        self.wait()

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
                part[i].set_color(color)
        second_line = TexMobject(
            "\\big( 3^2 + (2i)^2 \\big) + " + \
            "\\big(3 \\cdot 2 + 2 \\cdot 3 \\big)i"
        )
        for i in 1, 12, 18:
            second_line[i].set_color(BLUE)
        for i in 5, 14, 16:
            second_line[i].set_color(YELLOW)
        second_line.scale(0.9)
        final_line = TexMobject("5 + 12i")
        for i in 0, 2, 3:
            final_line[i].set_color(GREEN)
        lines = VGroup(top_line, second_line, final_line)
        lines.arrange(DOWN, buff = MED_LARGE_BUFF)
        lines.next_to(rect.get_top(), DOWN)
        minus = TexMobject("-").scale(0.9)
        minus.move_to(second_line[3])

        self.play(
            FadeIn(rect),
            Transform(VGroup(number), top_line),
            run_time = 2
        )
        self.wait()

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
            self.wait()
        self.play(
            Transform(second_line[3], minus),
            FadeOut(VGroup(*[
                second_line[i]
                for i in (4, 6, 7)
            ])),
            second_line[5].shift, 0.35*RIGHT,
        )
        self.play(VGroup(*second_line[:4]).shift, 0.55*RIGHT)
        self.wait()
        for index_alignment in index_alignment_lists[2:]:
            self.play(*[
                ReplacementTransform(
                    top_line[i][j].copy(), second_line[k],
                    run_time = 1.5
                )
                for i, j, k in index_alignment
            ])
            self.wait()
        self.play(FadeIn(final_line))
        self.wait()

        self.final_line = final_line

    def plot_result(self):
        result_label = self.final_line.copy()
        result_label.add_background_rectangle()

        point = self.plane.coords_to_point(5, 12)
        dot = Dot(point, color = GREEN)
        line = Line(self.plane.get_center_point(), point)
        line.set_color(dot.get_color())
        distance_label = TexMobject("13")
        distance_label.add_background_rectangle()
        distance_label.next_to(line.get_center(), UP+LEFT, SMALL_BUFF)

        self.play(
            result_label.next_to, dot, UP+LEFT, SMALL_BUFF,
            Animation(self.final_line),
            DrawBorderThenFill(dot)
        )
        self.wait()
        self.play(*[
            ReplacementTransform(m1.copy(), m2)
            for m1, m2 in [
                (self.line, line), 
                (self.distance_label, distance_label)
            ]
        ])
        self.wait()

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
        self.wait(2)

class ThisIsMagic(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "This is magic", target_mode = "hooray"
        )
        self.play(self.teacher.change, "happy")
        self.wait(2)

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
        line.set_color(dot.get_color())
        label = TexMobject(complex_string_with_i(z))
        label.add_background_rectangle()
        label.next_to(dot, RIGHT, SMALL_BUFF)

        square_point = self.plane.number_to_point(z**2)
        square_dot = Dot(square_point, color = self.square_color)
        square_line = Line(zero_point, square_point)
        square_line.set_color(square_dot.get_color())
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
        arrow.set_color(WHITE)
        z_to_z_squared = TexMobject("z", "\\to", "z^2")
        z_to_z_squared.set_color_by_tex("z", dot.get_color())
        z_to_z_squared.set_color_by_tex("z^2", square_dot.get_color())
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
        self.wait()
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
        self.wait()
        self.play(Write(result_length_label))
        self.wait()

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
            part.set_color(color)
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
        self.wait(2)
        self.play(Blink(morty))
        self.wait()

class FiveTwoExample(GeneralExample):
    CONFIG = {
        "number" : complex(5, 2),
        "unit_size" : 0.25,
        "x_label_range" : list(range(-10, 40, 5)),
        "y_label_range" : list(range(0, 30, 5)),
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
            top_line[i].set_color(U_COLOR)
            top_line[i+2].set_color(V_COLOR)
        top_line.next_to(rect.get_top(), DOWN)
        second_line = TexMobject(
            "\\big(", "u^2 - v^2", "\\big)", "+",
            "\\big(", "2uv", "\\big)", "i"
        )
        for i, j in (1, 0), (5, 1):
            second_line[i][j].set_color(U_COLOR)
        for i, j in (1, 3), (5, 2):
            second_line[i][j].set_color(V_COLOR)
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
            line.set_color(self.square_color)


        self.play(*list(map(FadeIn, [rect, top_line, second_line])))
        self.wait()
        self.play(
            real_part.copy().next_to, real_part_line.copy(), 
                DOWN, SMALL_BUFF,
            ShowCreation(real_part_line)
        )
        self.wait()
        self.play(
            FadeOut(VGroup(
                self.example_label, self.example_dot, self.example_line,
                self.z_to_z_squared, self.z_to_z_squared_arrow
            )),
            imag_part.copy().next_to, imag_part_line.copy(), 
                RIGHT, SMALL_BUFF,
            ShowCreation(imag_part_line)
        )
        self.wait()

        self.corner_rect = rect

    def draw_triangle(self):
        hyp_length = TexMobject("u", "^2", "+", "v", "^2")
        hyp_length.set_color_by_tex("u", U_COLOR)
        hyp_length.set_color_by_tex("v", V_COLOR)
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
        self.wait()
        self.play(FadeIn(triangle))
        self.wait()

    def show_uv_to_triples(self):
        rect = self.corner_rect.copy()
        rect.stretch_to_fit_height(FRAME_HEIGHT)
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
            pair_mob.set_color_by_tex(str(u), U_COLOR)
            pair_mob.set_color_by_tex(str(v), V_COLOR)
            triple_mob = TexMobject("(%d, %d, %d)"%(a, b, c))
            pair_mobs.add(pair_mob)
            triple_mobs.add(triple_mob)
            pair_mob.scale(0.75)
            triple_mob.scale(0.75)
        pair_mobs.arrange(DOWN)
        pair_mobs.next_to(uv_title, DOWN, MED_LARGE_BUFF)
        triple_mobs.arrange(DOWN)
        triple_mobs.next_to(triple_title, DOWN, MED_LARGE_BUFF)

        self.play(*list(map(FadeIn, [
            rect, h_line, v_line, 
            uv_title, triple_title
        ])))
        self.play(*[
            LaggedStartMap(
                FadeIn, mob, 
                run_time = 5,
                lag_ratio = 0.2
            )
            for mob in (pair_mobs, triple_mobs)
        ])

class VisualizeZSquared(Scene):
    CONFIG = {
        "initial_unit_size" : 0.4,
        "final_unit_size" : 0.1,
        "plane_center" : 3*LEFT + 2*DOWN,
        "x_label_range" : list(range(-12, 24, 4)),
        "y_label_range" : list(range(-4, 24, 4)),
        "dot_color" : YELLOW,
        "square_color" : MAROON_B,
        "big_dot_radius" : 0.075,
        "dot_radius" : 0.05,
    }
    def construct(self):
        self.force_skipping()

        self.add_plane()
        self.write_z_to_z_squared()
        self.draw_arrows()
        self.draw_dots()
        self.add_colored_grid()
        self.apply_transformation()
        self.show_triangles()
        self.zoom_out()
        self.show_more_triangles()

    def add_plane(self):
        width = (FRAME_X_RADIUS+abs(self.plane_center[0]))/self.final_unit_size
        height = (FRAME_Y_RADIUS+abs(self.plane_center[1]))/self.final_unit_size
        background_plane = ComplexPlane(
            x_radius = width,
            y_radius = height,
            stroke_width = 2,
            stroke_color = BLUE_E,
            secondary_line_ratio = 0,
        )
        background_plane.axes.set_stroke(width = 4)

        background_plane.scale(self.initial_unit_size)
        background_plane.shift(self.plane_center)

        coordinate_labels = VGroup()
        z_list = np.append(
            self.x_label_range,
            complex(0, 1)*np.array(self.y_label_range)
        )
        for z in z_list:
            if z == 0:
                continue
            if z.imag == 0:
                tex = str(int(z.real))
            else:
                tex = str(int(z.imag)) + "i"
            label = TexMobject(tex)
            label.scale(0.75)
            label.add_background_rectangle()
            point = background_plane.number_to_point(z)
            if z.imag == 0:
                label.next_to(point, DOWN, SMALL_BUFF)
            else:
                label.next_to(point, LEFT, SMALL_BUFF)
            coordinate_labels.add(label)

        self.add(background_plane, coordinate_labels)
        self.background_plane = background_plane
        self.coordinate_labels = coordinate_labels

    def write_z_to_z_squared(self):
        z_to_z_squared = TexMobject("z", "\\to", "z^2")
        z_to_z_squared.set_color_by_tex("z", YELLOW)
        z_to_z_squared.set_color_by_tex("z^2", MAROON_B)
        z_to_z_squared.add_background_rectangle()
        z_to_z_squared.to_edge(UP)
        z_to_z_squared.shift(2*RIGHT)

        self.play(Write(z_to_z_squared))
        self.wait()
        self.z_to_z_squared = z_to_z_squared

    def draw_arrows(self):
        z_list = [
            complex(2, 1),
            complex(3, 2),
            complex(0, 1),
            complex(-1, 0),
        ]

        arrows = VGroup()
        dots = VGroup()
        for z in z_list:
            z_point, square_point, mid_point = [
                self.background_plane.number_to_point(z**p)
                for p in (1, 2, 1.5)
            ]
            angle = Line(mid_point, square_point).get_angle()
            angle -= Line(z_point, mid_point).get_angle()
            angle *= 2
            arrow = Arrow(
                z_point, square_point, 
                path_arc = angle,
                color = WHITE,
                tip_length = 0.15,
                buff = SMALL_BUFF,
            )

            z_dot, square_dot = [
                Dot(
                    point, color = color,
                    radius = self.big_dot_radius,
                )
                for point, color in [
                    (z_point, self.dot_color),
                    (square_point, self.square_color),
                ]
            ]
            z_label = TexMobject(complex_string_with_i(z))
            square_label = TexMobject(complex_string_with_i(z**2))
            for label, point in (z_label, z_point), (square_label, square_point):
                if abs(z) > 2:
                    vect = RIGHT
                else:
                    vect = point - self.plane_center
                    vect /= get_norm(vect)
                    if abs(vect[1]) < 0.1:
                        vect[1] = -1
                label.next_to(point, vect)
                label.add_background_rectangle()

            self.play(*list(map(FadeIn, [z_label, z_dot])))
            self.wait()
            self.play(ShowCreation(arrow))
            self.play(ReplacementTransform(
                z_dot.copy(), square_dot,
                path_arc = angle
            ))
            self.play(FadeIn(square_label))
            self.wait()
            self.play(
                FadeOut(z_label),
                FadeOut(square_label),
                Animation(arrow)
            )

            arrows.add(arrow)
            dots.add(z_dot, square_dot)
        self.wait()
        self.play(*list(map(FadeOut, [
            dots, arrows, self.z_to_z_squared
        ])))

    def draw_dots(self):
        min_corner, max_corner = [
            self.background_plane.point_to_coords(
                u*FRAME_X_RADIUS*RIGHT + u*FRAME_Y_RADIUS*UP
            )
            for u in (-1, 1)
        ]
        x_min, y_min = list(map(int, min_corner[:2]))
        x_max, y_max = list(map(int, max_corner[:2]))

        dots = VGroup(*[
            Dot(
                self.background_plane.coords_to_point(x, y),
                color = self.dot_color,
                radius = self.dot_radius,
            )
            for x in range(x_min, x_max+1)
            for y in range(y_min, y_max+1)
        ])
        dots.sort(lambda p : np.dot(p, UP+RIGHT))

        self.add_foreground_mobject(self.coordinate_labels)
        self.play(LaggedStartMap(
            DrawBorderThenFill, dots,
            stroke_width = 3,
            stroke_color = PINK,
            run_time = 3,
            lag_ratio = 0.2
        ))
        self.wait()

        self.dots = dots

    def add_colored_grid(self):
        color_grid = self.get_color_grid()

        self.play(
            self.background_planes.set_stroke, None, 1,
            LaggedStartMap(
                FadeIn, color_grid, 
                run_time = 2
            ),
            Animation(self.dots),
        )
        self.wait()

        self.color_grid = color_grid

    def apply_transformation(self):
        for dot in self.dots:
            dot.start_point = dot.get_center()
        def update_dot(dot, alpha):
            event = list(dot.start_point) + [alpha]
            dot.move_to(self.homotopy(*event))
            return dot
        self.play(
            Homotopy(self.homotopy, self.color_grid),
            *[
                UpdateFromAlphaFunc(dot, update_dot)
                for dot in self.dots
            ],
            run_time = 3
        )
        self.wait(2)
        self.play(self.color_grid.set_stroke, None, 3)
        self.wait()
        scale_factor = self.big_dot_radius/self.dot_radius
        self.play(LaggedStartMap(
            ApplyMethod, self.dots,
            lambda d : (d.scale_in_place, scale_factor),
            rate_func = there_and_back,
            run_time = 3
        ))
        self.wait()

    def show_triangles(self):
        z_list = [
            complex(u, v)**2
            for u, v in [(2, 1), (3, 2), (4, 1)]
        ]
        triangles = self.get_triangles(z_list)
        triangle = triangles[0]
        triangle.save_state()
        triangle.scale(0.01, about_point = triangle.tip)

        self.play(triangle.restore, run_time = 2)
        self.wait(2)
        for new_triangle in triangles[1:]:
            self.play(Transform(triangle, new_triangle))
            self.wait(2)
        self.play(FadeOut(triangle))

    def zoom_out(self):
        self.remove_foreground_mobject(self.coordinate_labels)
        movers = [
            self.background_plane,
            self.color_grid,
            self.dots,
            self.coordinate_labels,
        ]
        scale_factor = self.final_unit_size/self.initial_unit_size
        for mover in movers:
            mover.generate_target()
            mover.target.scale(
                scale_factor,
                about_point = self.plane_center
            )
        for dot in self.dots.target:
            dot.scale_in_place(1./scale_factor)
        self.background_plane.target.fade()

        self.revert_to_original_skipping_status()
        self.play(
            *list(map(MoveToTarget, movers)),
            run_time = 3
        )
        self.wait(2)

    def show_more_triangles(self):
        z_list = [
            complex(u, v)**2
            for u in range(4, 7)
            for v in range(1, u)
        ]
        triangles = self.get_triangles(z_list)
        triangle = triangles[0]

        self.play(FadeOut(triangle))
        self.wait(2)
        for new_triangle in triangles[1:]:
            self.play(Transform(triangle, new_triangle))
            self.wait(2)

    ###

    def get_color_grid(self):
        width = (FRAME_X_RADIUS+abs(self.plane_center[0]))/self.initial_unit_size
        height = (FRAME_Y_RADIUS+abs(self.plane_center[1]))/self.initial_unit_size
        color_grid = ComplexPlane(
            x_radius = width,
            y_radius = int(height),
            secondary_line_ratio = 0,
            stroke_width = 2,
        )
        color_grids.set_color_by_gradient(
            *[GREEN, RED, MAROON_B, TEAL]*2
        )
        color_grid.remove(color_grid.axes[0])
        for line in color_grid.family_members_with_points():
            center = line.get_center()
            if center[0] <= 0 and abs(center[1]) < 0.01:
                line_copy = line.copy()
                line.scale(0.499, about_point = line.get_start())
                line_copy.scale(0.499, about_point = line_copy.get_end())
                color_grid.add(line_copy)
        color_grid.scale(self.initial_unit_size)
        color_grid.shift(self.plane_center)
        color_grid.prepare_for_nonlinear_transform()
        return color_grid

    def get_triangles(self, z_list):
        triangles = VGroup()
        for z in z_list:
            point = self.background_plane.number_to_point(z)
            line = Line(self.plane_center, point)
            triangle = Polygon(
                ORIGIN, RIGHT, RIGHT+UP,
                stroke_color = BLUE,
                stroke_width = 2,
                fill_color = BLUE,
                fill_opacity = 0.5,
            )
            triangle.replace(line, stretch = True)
            a = int(z.real)
            b = int(z.imag)
            c = int(abs(z))
            a_label, b_label, c_label = labels = [
                TexMobject(str(num))
                for num in (a, b, c)
            ]
            for label in b_label, c_label:
                label.add_background_rectangle()
            a_label.next_to(triangle.get_bottom(), UP, SMALL_BUFF)
            b_label.next_to(triangle, RIGHT, SMALL_BUFF)
            c_label.next_to(line.get_center(), UP+LEFT, SMALL_BUFF)
            triangle.add(*labels)
            triangle.tip = point
            triangles.add(triangle)
        return triangles

    def homotopy(self, x, y, z, t):
        z_complex = self.background_plane.point_to_number(np.array([x, y, z]))
        result = z_complex**(1+t)
        return self.background_plane.number_to_point(result)

class AskAboutHittingAllPoints(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Does this hit \\\\ all pythagorean triples?",
            target_mode = "raise_left_hand"
        )
        self.wait()
        self.teacher_says("No", target_mode = "sad")
        self.change_student_modes(*["hesitant"]*3)
        self.wait()

class PointsWeMiss(VisualizeZSquared):
    CONFIG = {
        "final_unit_size" : 0.4,
        "plane_center" : 2*LEFT + 2*DOWN,
        "dot_x_range" : list(range(-5, 6)),
        "dot_y_range" : list(range(-4, 4)),
    }
    def construct(self):
        self.add_plane()
        self.add_transformed_color_grid()
        self.add_dots()
        self.show_missing_point()
        self.show_second_missing_point()
        self.mention_one_half_rule()

    def add_transformed_color_grid(self):
        color_grid = self.get_color_grid()
        func = lambda p : self.homotopy(p[0], p[1], p[1], 1)
        color_grid.apply_function(func)
        color_grid.set_stroke(width = 4)
        self.add(color_grid, self.coordinate_labels)
        self.color_grid = color_grid

    def add_dots(self):
        z_list = [
            complex(x, y)**2
            for x in self.dot_x_range
            for y in self.dot_y_range
        ]
        dots = VGroup(*[
            Dot(
                self.background_plane.number_to_point(z),
                color = self.dot_color,
                radius = self.big_dot_radius,
            )
            for z in z_list
        ])
        dots.sort(get_norm)
        self.add(dots)
        self.dots = dots

    def show_missing_point(self):
        z_list = [complex(6, 8), complex(9, 12), complex(3, 4)]
        points = list(map(
            self.background_plane.number_to_point,
            z_list 
        ))
        dots = VGroup(*list(map(Dot, points)))
        for dot in dots[:2]:
            dot.set_stroke(RED, 4)
            dot.set_fill(opacity = 0)
        labels = VGroup(*[
            TexMobject(complex_string_with_i(z))
            for z in z_list
        ])
        labels.set_color(RED)
        labels[2].set_color(GREEN)
        rhss = VGroup()
        for label, dot in zip(labels, dots):
            label.add_background_rectangle()
            label.next_to(dot, UP+RIGHT, SMALL_BUFF)
            if label is labels[-1]:
                rhs = TexMobject("= (2+i)^2")
            else:
                rhs = TexMobject("\\ne (u+vi)^2")
            rhs.add_background_rectangle()
            rhs.next_to(label, RIGHT)
            rhss.add(rhs)
        triangles = self.get_triangles(z_list)

        self.play(FocusOn(dots[0]))
        self.play(ShowCreation(dots[0]))
        self.play(Write(labels[0]))
        self.wait()
        self.play(FadeIn(triangles[0]))
        self.wait(2)
        self.play(Write(rhss[0]))
        self.wait(2)
        groups = triangles, dots, labels, rhss
        for i in 1, 2:
            self.play(*[
                Transform(group[0], group[i])
                for group in groups
            ])
            self.wait(3)
        self.play(*[
            FadeOut(group[0])
            for group in groups
        ])

    def show_second_missing_point(self):
        z_list = [complex(4, 3), complex(8, 6)]
        points = list(map(
            self.background_plane.number_to_point,
            z_list 
        ))
        dots = VGroup(*list(map(Dot, points)))
        dots[0].set_stroke(RED, 4)
        dots[0].set_fill(opacity = 0)
        labels = VGroup(*[
            TexMobject(complex_string_with_i(z))
            for z in z_list
        ])
        labels[0].set_color(RED)
        labels[1].set_color(GREEN)
        rhss = VGroup()
        for label, dot in zip(labels, dots):
            label.add_background_rectangle()
            label.next_to(dot, UP+RIGHT, SMALL_BUFF)
            if label is labels[-1]:
                rhs = TexMobject("= (3+i)^2")
            else:
                rhs = TexMobject("\\ne (u+vi)^2")
            rhs.add_background_rectangle()
            rhs.next_to(label, RIGHT)
            rhss.add(rhs)
        triangles = self.get_triangles(z_list)
        groups = [dots, labels, rhss, triangles]
        for group in groups:
            group[0].save_state()

        self.play(ShowCreation(dots[0]))
        self.play(Write(VGroup(labels[0], rhss[0])))
        self.play(FadeIn(triangles[0]))
        self.wait(3)
        self.play(*[Transform(*group) for group in groups])
        self.wait(3)
        self.play(*[group[0].restore for group in groups])
        self.wait(2)

    def mention_one_half_rule(self):
        morty = Mortimer()
        morty.flip()
        morty.to_corner(DOWN+LEFT)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, 
            "Never need to scale \\\\ by less than $\\frac{1}{2}$"
        ))
        self.play(Blink(morty))
        self.wait(2)

class PointsWeMissAreMultiplesOfOnesWeHit(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "Every point we",
            "miss",
            "is \\\\ a multiple of one we",
            "hit"
        )
        words.set_color_by_tex("miss", RED)
        words.set_color_by_tex("hit", GREEN)
        self.teacher_says(words)
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)

class DrawSingleRadialLine(PointsWeMiss):
    def construct(self):
        self.add_plane()
        self.background_plane.set_stroke(width = 1)
        self.add_transformed_color_grid()
        self.color_grid.set_stroke(width = 1)
        self.add_dots()
        self.draw_line()

    def draw_line(self):
        point = self.background_plane.coords_to_point(3, 4)
        dot = Dot(point, color = RED)
        line = Line(
            self.plane_center,
            self.background_plane.coords_to_point(15, 20),
            color = WHITE,
        )
        added_dots = VGroup(*[
            Dot(self.background_plane.coords_to_point(3*k, 4*k))
            for k in (2, 3, 5)
        ])
        added_dots.set_color(GREEN)

        self.play(GrowFromCenter(dot))
        self.play(Indicate(dot))
        self.play(ShowCreation(line), Animation(dot))
        self.wait()
        self.play(LaggedStartMap(
            DrawBorderThenFill, added_dots,
            stroke_color = PINK,
            stroke_width = 4,
            run_time = 3
        ))
        self.wait()

class DrawRadialLines(PointsWeMiss):
    CONFIG = {
        "final_unit_size" : 0.2,
        "dot_x_range" : list(range(-4, 10)),
        "dot_y_range" : list(range(-4, 10)),
        "x_label_range" : list(range(-12, 40, 4)),
        "y_label_range" : list(range(-4, 32, 4)),
        "big_dot_radius" : 0.05,
    }
    def construct(self):
        self.add_plane()
        self.add_transformed_color_grid()
        self.resize_plane()
        self.add_dots()
        self.create_lines()
        self.show_single_line()
        self.show_all_lines()
        self.show_triangles()

    def resize_plane(self):
        everything = VGroup(*self.get_top_level_mobjects())
        everything.scale(
            self.final_unit_size/self.initial_unit_size,
            about_point = self.plane_center
        )
        self.background_plane.set_stroke(width = 1)

    def create_lines(self):
        coord_strings = set([])
        reduced_coords_yet_to_be_reached = set([])
        for dot in self.dots:
            point = dot.get_center()
            float_coords = self.background_plane.point_to_coords(point)
            coords = np.round(float_coords).astype('int')
            gcd = fractions.gcd(*coords)
            reduced_coords = coords/abs(gcd)

            if np.all(coords == [3, 4]):
                first_dot = dot

            dot.coords = coords
            dot.reduced_coords = reduced_coords
            coord_strings.add(str(coords))
            reduced_coords_yet_to_be_reached.add(str(reduced_coords))
        lines = VGroup()
        for dot in [first_dot] + list(self.dots):
            rc_str = str(dot.reduced_coords)
            if rc_str not in reduced_coords_yet_to_be_reached:
                continue
            reduced_coords_yet_to_be_reached.remove(rc_str)
            new_dots = VGroup()
            for k in range(50):
                new_coords = k*dot.reduced_coords
                if str(new_coords) in coord_strings:
                    continue
                coord_strings.add(str(new_coords))
                point = self.background_plane.coords_to_point(*new_coords)
                if abs(point[0]) > FRAME_X_RADIUS or abs(point[1]) > FRAME_Y_RADIUS:
                    continue
                new_dot = Dot(
                    point, color = GREEN,
                    radius = self.big_dot_radius
                )
                new_dots.add(new_dot)
            line = Line(self.plane_center, dot.get_center())
            line.scale(
                FRAME_WIDTH/line.get_length(),
                about_point = self.plane_center
            )
            line.set_stroke(width = 1)
            line.seed_dot = dot.copy()
            line.new_dots = new_dots
            lines.add(line)
        self.lines = lines

    def show_single_line(self):
        line = self.lines[0]
        dot = line.seed_dot

        self.play(
            dot.scale_in_place, 2,
            dot.set_color, RED
        )
        self.play(ReplacementTransform(dot, line))
        self.wait()
        self.play(LaggedStartMap(
            DrawBorderThenFill, line.new_dots,
            stroke_width = 4,
            stroke_color = PINK,
            run_time = 3,
        ))
        self.wait()

    def show_all_lines(self):
        seed_dots = VGroup(*[line.seed_dot for line in self.lines])
        new_dots = VGroup(*[line.new_dots for line in self.lines])
        for dot in seed_dots:
            dot.generate_target()
            dot.target.scale_in_place(1.5)
            dot.target.set_color(RED)

        self.play(LaggedStartMap(
            MoveToTarget, seed_dots,
            run_time = 2
        ))
        self.play(ReplacementTransform(
            seed_dots, self.lines,
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.play(LaggedStartMap(
            DrawBorderThenFill, new_dots,
            stroke_width = 4,
            stroke_color = PINK,
            run_time = 3,
        ))
        self.wait()

        self.new_dots = new_dots

    def show_triangles(self):
        z_list = [
            complex(9, 12),
            complex(7, 24),
            complex(8, 15),
            complex(21, 20),
            complex(36, 15),
        ]
        triangles = self.get_triangles(z_list)
        triangle = triangles[0]

        self.play(FadeIn(triangle))
        self.wait(2)
        for new_triangle in triangles[1:]:
            self.play(Transform(triangle, new_triangle))
            self.wait(2)

class RationalPointsOnUnitCircle(DrawRadialLines):
    CONFIG = {
        "initial_unit_size" : 1.2,
        "final_unit_size" : 0.4,
        "plane_center" : 1.5*DOWN
    }
    def construct(self):
        self.add_plane()
        self.show_rational_points_on_unit_circle()
        self.divide_by_c_squared()
        self.from_rational_point_to_triple()

    def add_plane(self):
        added_x_coords = list(range(-4, 6, 2))
        added_y_coords = list(range(-2, 4, 2))
        self.x_label_range += added_x_coords
        self.y_label_range += added_y_coords
        DrawRadialLines.add_plane(self)

    def show_rational_points_on_unit_circle(self):
        circle = self.get_unit_circle()

        coord_list = [
            (12, 5),
            (8, 15),
            (7, 24),
            (3, 4),
        ]
        groups = VGroup()
        for x, y in coord_list:
            norm = np.sqrt(x**2 + y**2)
            point = self.background_plane.coords_to_point(
                x/norm, y/norm
            )
            dot = Dot(point, color = YELLOW)
            line = Line(self.plane_center, point)
            line.set_color(dot.get_color())
            label = TexMobject(
                "{"+str(x), "\\over", str(int(norm))+"}",
                "+", 
                "{"+str(y), "\\over", str(int(norm))+"}",
                "i"
            )
            label.next_to(dot, UP+RIGHT, buff = 0)
            label.add_background_rectangle()

            group = VGroup(line, dot, label)
            group.coords = (x, y)
            groups.add(group)
        group = groups[0].copy()

        self.add(circle, self.coordinate_labels)
        self.play(FadeIn(group))
        self.wait()
        for new_group in groups[1:]:
            self.play(Transform(group, new_group))
            self.wait()

        self.curr_example_point_group = group
        self.next_rational_point_example = groups[0]
        self.unit_circle = circle

    def divide_by_c_squared(self):
        top_line = TexMobject(
            "a", "^2", "+", "b", "^2", "=", "c", "^2 \\phantom{1}"
        )
        top_line.shift(FRAME_X_RADIUS*RIGHT/2)
        top_line.to_corner(UP + LEFT)
        top_line.shift(RIGHT)
        top_rect = BackgroundRectangle(top_line)

        second_line = TexMobject(
            "\\left(", "{a", "\\over", "c}", "\\right)", "^2",
            "+",
            "\\left(", "{b", "\\over", "c}", "\\right)", "^2",
            "=", "1"
        )
        second_line.move_to(top_line, UP)
        second_line.shift_onto_screen()
        second_rect = BackgroundRectangle(second_line)

        circle_label = TextMobject(
            "All $x+yi$ where \\\\",
            "$x^2 + y^2 = 1$"
        )
        circle_label.next_to(second_line, DOWN, MED_LARGE_BUFF)
        circle_label.shift_onto_screen()
        circle_label.set_color_by_tex("x^2", GREEN)
        circle_label.add_background_rectangle()
        circle_arrow = Arrow(
            circle_label.get_bottom(),
            self.unit_circle.point_from_proportion(0.45),
            color = GREEN
        )

        self.play(FadeIn(top_rect), FadeIn(top_line))
        self.wait()
        self.play(*[
            ReplacementTransform(top_rect, second_rect)
        ] + [
            ReplacementTransform(
                top_line.get_parts_by_tex(tex, substring = False),
                second_line.get_parts_by_tex(tex),
                run_time = 2,
                path_arc = -np.pi/3
            )
            for tex  in ("a", "b", "c", "^2", "+", "=")
        ] + [
            ReplacementTransform(
                top_line.get_parts_by_tex("1"),
                second_line.get_parts_by_tex("1"),
                run_time = 2
            )
        ] + [
            Write(
                second_line.get_parts_by_tex(tex),
                run_time = 2,
                rate_func = squish_rate_func(smooth, 0, 0.5)
            )
            for tex in ("(", ")", "over",)
        ])
        self.wait(2)
        self.play(Write(circle_label))
        self.play(ShowCreation(circle_arrow))
        self.wait(2)
        self.play(FadeOut(circle_arrow))

        self.algebra = VGroup(
            second_rect, second_line, circle_label,
        )

    def from_rational_point_to_triple(self):
        rational_point_group = self.next_rational_point_example
        scale_factor = self.final_unit_size/self.initial_unit_size

        self.play(ReplacementTransform(
            self.curr_example_point_group,
            rational_point_group
        ))
        self.wait(2)
        self.play(*[
            ApplyMethod(
                mob.scale_about_point, 
                scale_factor,
                self.plane_center
            )
            for mob in [
                self.background_plane,
                self.coordinate_labels,
                self.unit_circle,
                rational_point_group,
            ]
        ] + [
            Animation(self.algebra),
        ])

        #mimic_group
        point = self.background_plane.coords_to_point(
            *rational_point_group.coords
        )
        dot = Dot(point, color = YELLOW)
        line = Line(self.plane_center, point)
        line.set_color(dot.get_color())
        x, y = rational_point_group.coords
        label = TexMobject(str(x), "+", str(y), "i")
        label.next_to(dot, UP+RIGHT, buff = 0)
        label.add_background_rectangle()
        integer_point_group = VGroup(line, dot, label)
        distance_label = TexMobject(
            str(int(np.sqrt(x**2 + y**2)))
        )
        distance_label.add_background_rectangle()
        distance_label.next_to(line.get_center(), UP+LEFT, SMALL_BUFF)

        self.play(ReplacementTransform(
            rational_point_group, 
            integer_point_group
        ))
        self.play(Write(distance_label))
        self.wait(2)

    ###

    def get_unit_circle(self):
        template_line = Line(*[
            self.background_plane.number_to_point(z)
            for z in (-1, 1)
        ])
        circle = Circle(color = GREEN)
        circle.replace(template_line, dim_to_match = 0)
        return circle

class ProjectPointsOntoUnitCircle(DrawRadialLines):
    def construct(self):
        ###
        self.force_skipping()
        self.add_plane()
        self.add_transformed_color_grid()
        self.resize_plane()
        self.add_dots()
        self.create_lines()
        self.show_all_lines()
        self.revert_to_original_skipping_status()
        ###

        self.add_unit_circle()
        self.project_all_dots()
        self.zoom_in()
        self.draw_infinitely_many_lines()


    def add_unit_circle(self):
        template_line = Line(*[
            self.background_plane.number_to_point(n)
            for n in (-1, 1)
        ])
        circle = Circle(color = BLUE)
        circle.replace(template_line, dim_to_match = 0)

        self.play(ShowCreation(circle))
        self.unit_circle = circle

    def project_all_dots(self):
        dots = self.dots
        dots.add(*self.new_dots)
        dots.sort(
            lambda p : get_norm(p - self.plane_center)
        )
        unit_length = self.unit_circle.get_width()/2.0
        for dot in dots:
            dot.generate_target()
            point = dot.get_center()
            vect = point-self.plane_center
            if np.round(vect[0], 3) == 0 and abs(vect[1]) > 2*unit_length:
                dot.target.set_fill(opacity = 0)
                continue
            distance = get_norm(vect)
            dot.target.scale(
                unit_length/distance,
                about_point = self.plane_center
            )
            dot.target.set_width(0.01)

        self.play(LaggedStartMap(
            MoveToTarget, dots,
            run_time = 3,
            lag_ratio = 0.2
        ))

    def zoom_in(self):
        target_height = 5.0
        scale_factor = target_height / self.unit_circle.get_height()
        group = VGroup(
            self.background_plane, self.coordinate_labels,
            self.color_grid,
            self.lines, self.unit_circle,
            self.dots,
        )

        self.play(
            group.shift, -self.plane_center,
            group.scale, scale_factor,
            run_time = 2
        )
        self.wait(2)

    def draw_infinitely_many_lines(self):
        lines = VGroup(*[
            Line(ORIGIN, FRAME_WIDTH*vect)
            for vect in compass_directions(1000)
        ])

        self.play(LaggedStartMap(
            ShowCreation, lines,
            run_time = 3
        ))
        self.play(FadeOut(lines))
        self.wait()

class ICanOnlyDrawFinitely(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "I can only \\\\ draw finitely",
            run_time = 2
        )
        self.wait(2)

class SupposeMissingPoint(PointsWeMiss):
    def construct(self):
        self.add_plane()
        self.background_plane.set_stroke(width = 1)
        self.draw_missing_triple()
        self.project_onto_unit_circle()

    def draw_missing_triple(self):
        point = self.background_plane.coords_to_point(12, 5)
        origin = self.plane_center
        line = Line(origin, point, color = WHITE)
        dot = Dot(point, color = YELLOW)
        triangle = Polygon(ORIGIN, RIGHT, RIGHT+UP)
        triangle.set_stroke(BLUE, 2)
        triangle.set_fill(BLUE, 0.5)
        triangle.replace(line, stretch = True)
        a = TexMobject("a")
        a.next_to(triangle.get_bottom(), UP, SMALL_BUFF)
        b = TexMobject("b")
        b.add_background_rectangle()
        b.next_to(triangle, RIGHT, SMALL_BUFF)
        c = TexMobject("c")
        c.add_background_rectangle()
        c.next_to(line.get_center(), UP+LEFT, SMALL_BUFF)
        triangle.add(a, b, c)
        words = TextMobject(
            "If we missed \\\\ a triple \\dots"
        )
        words.add_background_rectangle()
        words.next_to(dot, UP+RIGHT)
        words.shift_onto_screen()

        self.add(triangle, line, dot)
        self.play(Write(words))
        self.wait()

        self.words = words
        self.triangle = triangle
        self.line = line
        self.dot = dot


    def project_onto_unit_circle(self):
        dot, line = self.dot, self.line
        template_line = Line(*[
            self.background_plane.number_to_point(n)
            for n in (-1, 1)
        ])
        circle = Circle(color = GREEN)
        circle.replace(template_line, dim_to_match = 0)
        z = self.background_plane.point_to_number(dot.get_center())
        z_norm = abs(z)
        unit_z = z/z_norm
        new_point = self.background_plane.number_to_point(unit_z)
        dot.generate_target()
        dot.target.move_to(new_point)
        line.generate_target()
        line.target.scale(1./z_norm, about_point = self.plane_center)

        rational_point_word = TexMobject("(a/c) + (b/c)i")
        rational_point_word.next_to(
            self.background_plane.coords_to_point(0, 6), RIGHT
        )
        rational_point_word.add_background_rectangle()
        arrow = Arrow(
            rational_point_word.get_bottom(),
            dot.target,
            buff = SMALL_BUFF
        )

        self.play(ShowCreation(circle))
        self.add(dot.copy().fade())
        self.add(line.copy().set_stroke(GREY, 1))
        self.play(*list(map(MoveToTarget, [dot, line])))
        self.wait()
        self.play(
            Write(rational_point_word),
            ShowCreation(arrow)
        )
        self.wait(2)

class ProofTime(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Proof time!", target_mode = "hooray")
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)

class FinalProof(RationalPointsOnUnitCircle):
    def construct(self):
        self.add_plane()
        self.draw_rational_point()
        self.draw_line_from_example_point()
        self.show_slope_is_rational()
        self.show_all_rational_slopes()
        self.square_example_point()
        self.project_onto_circle()
        self.show_same_slope()
        self.write_v_over_u_slope()

    def draw_rational_point(self):
        circle = self.get_unit_circle()
        coords = (3./5., 4./5.)
        point = self.background_plane.coords_to_point(*coords)
        dot = Dot(point, color = YELLOW)
        label = TexMobject(
            "(a/c) + (b/c)i"
        )
        label.add_background_rectangle()
        label.next_to(dot, UP+RIGHT, buff = 0)

        self.add(circle)
        self.play(
            Write(label, run_time = 2),
            DrawBorderThenFill(dot)
        )
        self.wait()

        self.example_dot = dot
        self.example_label = label
        self.unit_circle = circle

    def draw_line_from_example_point(self):
        neg_one_point = self.background_plane.number_to_point(-1)
        neg_one_dot = Dot(neg_one_point, color = RED)
        line = Line(
            neg_one_point, self.example_dot.get_center(),
            color = RED
        )

        self.play(
            ShowCreation(line, run_time = 2),
            Animation(self.example_label)
        )
        self.play(DrawBorderThenFill(neg_one_dot))
        self.wait()

        self.neg_one_dot = neg_one_dot
        self.secant_line = line

    def show_slope_is_rational(self):
        p0 = self.neg_one_dot.get_center()
        p1 = self.example_dot.get_center()
        p_mid = p1[0]*RIGHT + p0[1]*UP

        h_line = Line(p0, p_mid, color = MAROON_B)
        v_line = Line(p_mid, p1, color = MAROON_B)
        run_brace = Brace(h_line, DOWN)
        run_text = run_brace.get_text(
            "Run = $1 + \\frac{a}{c}$"
        )
        run_text.add_background_rectangle()
        rise_brace = Brace(v_line, RIGHT)
        rise_text = rise_brace.get_text("Rise = $\\frac{b}{c}$")
        rise_text.add_background_rectangle()

        self.play(*list(map(ShowCreation, [h_line, v_line])))
        self.wait()
        self.play(
            GrowFromCenter(rise_brace),
            FadeIn(rise_text)
        )
        self.wait()
        self.play(
            GrowFromCenter(run_brace),
            FadeIn(run_text)
        )
        self.wait(3)
        self.play(*list(map(FadeOut, [
            self.example_dot, self.example_label,
            self.secant_line,
            h_line, v_line,
            run_brace, rise_brace,
            run_text, rise_text,
        ])))

    def show_all_rational_slopes(self):
        lines = VGroup()
        labels = VGroup()
        for u in range(2, 7):
            for v in range(1, u):
                if fractions.gcd(u, v) != 1:
                    continue
                z_squared = complex(u, v)**2
                unit_z_squared = z_squared/abs(z_squared)
                point = self.background_plane.number_to_point(unit_z_squared)
                dot = Dot(point, color = YELLOW)
                line = Line(
                    self.background_plane.number_to_point(-1),
                    point,
                    color = self.neg_one_dot.get_color()
                )
                line.add(dot)

                label = TexMobject(
                    "\\text{Slope = }",
                    str(v), "/", str(u)
                )
                label.add_background_rectangle()
                label.next_to(
                    self.background_plane.coords_to_point(1, 1.5),
                    RIGHT
                )

                lines.add(line)
                labels.add(label)
        line = lines[0]
        label = labels[0]

        self.play(
            ShowCreation(line),
            FadeIn(label)
        )
        self.wait()
        for new_line, new_label in zip(lines, labels)[1:]:
            self.play(
                Transform(line, new_line),
                Transform(label, new_label),
            )
            self.wait()
        self.play(*list(map(FadeOut, [line, label])))

    def square_example_point(self):
        z = complex(2, 1)
        point = self.background_plane.number_to_point(z)
        uv_dot = Dot(point, color = YELLOW)
        uv_label = TexMobject("u", "+", "v", "i")
        uv_label.add_background_rectangle()
        uv_label.next_to(uv_dot, DOWN+RIGHT, buff = 0)
        uv_line = Line(
            self.plane_center, point,
            color = YELLOW
        )
        uv_arc = Arc(
            angle = uv_line.get_angle(),
            radius = 0.75
        )
        uv_arc.shift(self.plane_center)
        theta = TexMobject("\\theta")
        theta.next_to(uv_arc, RIGHT, SMALL_BUFF, DOWN)
        theta.scale_in_place(0.8)

        square_point = self.background_plane.number_to_point(z**2)
        square_dot = Dot(square_point, color = MAROON_B)
        square_label = TexMobject("(u+vi)^2")
        square_label.add_background_rectangle()
        square_label.next_to(square_dot, RIGHT)
        square_line = Line(
            self.plane_center, square_point,
            color = MAROON_B
        )
        square_arc = Arc(
            angle = square_line.get_angle(),
            radius = 0.65
        )
        square_arc.shift(self.plane_center)
        two_theta = TexMobject("2\\theta")
        two_theta.next_to(
            self.background_plane.coords_to_point(0, 1),
            UP+RIGHT, SMALL_BUFF, 
        )
        two_theta_arrow = Arrow(
            two_theta.get_right(),
            square_arc.point_from_proportion(0.75),
            tip_length = 0.15,
            path_arc = -np.pi/2,
            color = WHITE,
            buff = SMALL_BUFF
        )
        self.two_theta_group = VGroup(two_theta, two_theta_arrow)

        z_to_z_squared_arrow = Arrow(
            point, square_point, 
            path_arc = np.pi/3,
            color = WHITE
        )
        z_to_z_squared = TexMobject("z", "\\to", "z^2")
        z_to_z_squared.set_color_by_tex("z", YELLOW)
        z_to_z_squared.set_color_by_tex("z^2", MAROON_B)
        z_to_z_squared.add_background_rectangle()
        z_to_z_squared.next_to(
            z_to_z_squared_arrow.point_from_proportion(0.5),
            RIGHT, SMALL_BUFF
        )

        self.play(
            Write(uv_label),
            DrawBorderThenFill(uv_dot)
        )
        self.play(ShowCreation(uv_line))
        self.play(ShowCreation(uv_arc))
        self.play(Write(theta))
        self.wait()
        self.play(
            ShowCreation(z_to_z_squared_arrow),
            FadeIn(z_to_z_squared)
        )
        self.play(*[
            ReplacementTransform(
                m1.copy(), m2,
                path_arc = np.pi/3
            )
            for m1, m2 in [
                (uv_dot, square_dot),
                (uv_line, square_line),
                (uv_label, square_label),
                (uv_arc, square_arc),
            ]
        ])
        self.wait()
        self.play(
            Write(two_theta),
            ShowCreation(two_theta_arrow)
        )
        self.wait(2)
        self.play(FadeOut(self.two_theta_group))

        self.theta_group = VGroup(uv_arc, theta)
        self.uv_line = uv_line
        self.uv_dot = uv_dot
        self.uv_label = uv_label
        self.square_line = square_line
        self.square_dot = square_dot

    def project_onto_circle(self):
        line = self.square_line.copy()
        dot = self.square_dot.copy()
        self.square_line.fade()
        self.square_dot.fade()

        radius = self.unit_circle.get_width()/2
        line.generate_target()
        line.target.scale(
            radius / line.get_length(),
            about_point = line.get_start()
        )
        dot.generate_target()
        dot.target.move_to(line.target.get_end())

        self.play(
            MoveToTarget(line),
            MoveToTarget(dot),
        )
        self.wait()
        self.play(FadeIn(self.two_theta_group))
        self.wait()
        self.play(FadeOut(self.two_theta_group))
        self.wait(6) ##circle geometry

        self.rational_point_dot = dot

    def show_same_slope(self):
        line = Line(
            self.neg_one_dot.get_center(),
            self.rational_point_dot.get_center(),
            color = self.neg_one_dot.get_color()
        )
        theta_group_copy = self.theta_group.copy()
        same_slope_words = TextMobject("Same slope")
        same_slope_words.add_background_rectangle()
        same_slope_words.shift(4*LEFT + 0.33*UP)
        line_copies = VGroup(
            line.copy(),
            self.uv_line.copy()
        )
        line_copies.generate_target()
        line_copies.target.next_to(same_slope_words, DOWN)

        self.play(ShowCreation(line))
        self.wait()
        self.play(
            theta_group_copy.shift,
            line.get_start() - self.uv_line.get_start()
        )
        self.wait()
        self.play(
            Write(same_slope_words),
            MoveToTarget(line_copies)
        )
        self.wait()

        self.same_slope_words = same_slope_words

    def write_v_over_u_slope(self):
        p0 = self.plane_center
        p1 = self.uv_dot.get_center()
        p_mid = p1[0]*RIGHT + p0[1]*UP
        h_line = Line(p0, p_mid, color = YELLOW)
        v_line = Line(p_mid, p1, color = YELLOW)

        rhs = TexMobject("=", "{v", "\\over", "u}")
        rhs.next_to(self.same_slope_words, RIGHT)
        rect = SurroundingRectangle(VGroup(*rhs[1:]))
        morty = Mortimer().flip()
        morty.scale(0.5)
        morty.next_to(self.same_slope_words, UP, buff = 0)

        self.play(ShowCreation(h_line))
        self.play(ShowCreation(v_line))
        self.wait()
        self.play(*[
            ReplacementTransform(
                self.uv_label.get_part_by_tex(tex).copy(),
                rhs.get_part_by_tex(tex),
                run_time = 2
            )
            for tex in ("u", "v")
        ] + [
            Write(rhs.get_part_by_tex(tex))
            for tex in ("=", "over")
        ])
        self.wait(2)
        self.play(
            ShowCreation(rect),
            FadeIn(morty)
        )
        self.play(PiCreatureSays(
            morty, "Free to choose!",
            bubble_kwargs = {"height" : 1.5, "width" : 3},
            target_mode = "hooray",
            look_at_arg = rect
        ))
        self.play(Blink(morty))
        self.wait(2)

class BitOfCircleGeometry(Scene):
    def construct(self):
        circle = Circle(color = BLUE, radius = 3)
        p0, p1, p2 = [
            circle.point_from_proportion(alpha)
            for alpha in (0, 0.15, 0.55)
        ]
        O = circle.get_center()
        O_dot = Dot(O, color = WHITE)
        self.add(circle, O_dot)


        groups = VGroup()
        for point, tex, color in (O, "2", MAROON_B), (p2, "", RED):
            line1 = Line(point, p0)
            line2 = Line(point, p1)
            dot1 = Dot(p0)
            dot2 = Dot(p1)
            angle = line1.get_angle()
            arc = Arc(
                angle = line2.get_angle()-line1.get_angle(), 
                start_angle = line1.get_angle(),
                radius = 0.75,
                color = WHITE
            )
            arc.set_stroke(YELLOW, 3)
            arc.shift(point)
            label = TexMobject(tex + "\\theta")
            label.next_to(
                arc.point_from_proportion(0.9), RIGHT
            )

            group = VGroup(line1, line2, dot1, dot2)
            group.set_color(color)
            group.add(arc, label)
            if len(groups) == 0:
                self.play(*list(map(ShowCreation, [dot1, dot2])))
                self.play(*list(map(ShowCreation, [line1, line2])))
                self.play(ShowCreation(arc))
                self.play(FadeIn(label))
            groups.add(group)

        self.wait(2)
        self.play(ReplacementTransform(
            groups[0].copy(), groups[1]
        ))
        self.wait(2)

class PatreonThanksTriples(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "Burt Humburg",
            "CrypticSwarm",
            "David Beyer",
            "Erik Sundell",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Karan Bhargava",
            "Ankit Agarwal",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Juan Benet",
            "Othman Alikhan",
            "Markus Persson",
            "Yoni Nazarathy",
            "Joseph John Cox",
            "Dan Buchoff",
            "Luc Ritchie",
            "Ankalagon",
            "Eric Lavault",
            "Tomohiro Furusawa",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "John Haley",
            "Jeff Linse",
            "Suraj Pratap",
            "Cooper Jones",
            "Ryan Dahl",
            "Ahmad Bamieh",
            "Mark Govea",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Nils Schneider",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ],
    }

class Thumbnail(DrawRadialLines):
    def construct(self):
        self.force_skipping()
        self.add_plane()
        self.add_transformed_color_grid()
        self.color_grid.set_stroke(width = 5)
        self.resize_plane()
        self.add_dots()
        self.create_lines()
        self.show_single_line()
        self.show_all_lines()

        rect = Rectangle(
            height = 4.3, width = 4.2,
            stroke_width = 3,
            stroke_color = WHITE,
            fill_color = BLACK,
            fill_opacity = 1,
        )
        rect.to_corner(UP+RIGHT, buff = 0.01)
        triples = VGroup(*list(map(TexMobject, [
            "3^2 + 4^2 = 5^2",
            "5^2 + 12^2 = 13^2",
            "8^2 + 15^2 = 17^2",
            "\\vdots"
        ])))
        triples.arrange(DOWN, buff = MED_LARGE_BUFF)
        triples.next_to(rect.get_top(), DOWN)
        self.add(rect, triples)

class Poster(DrawRadialLines):
    CONFIG = {
        "final_unit_size" : 0.1,
        "plane_center" : ORIGIN,
    }
    def construct(self):
        self.force_skipping()
        self.add_plane()
        self.add_transformed_color_grid()
        self.color_grid.set_stroke(width = 5)
        self.resize_plane()
        self.add_dots()
        self.create_lines()
        self.show_single_line()
        self.show_all_lines()

        for dot_group in self.dots, self.new_dots:
            for dot in dot_group.family_members_with_points():
                dot.scale_in_place(0.5)
        self.remove(self.coordinate_labels)

        # rect = Rectangle(
        #     height = 4.3, width = 4.2,
        #     stroke_width = 3,
        #     stroke_color = WHITE,
        #     fill_color = BLACK,
        #     fill_opacity = 1,
        # )
        # rect.to_corner(UP+RIGHT, buff = 0.01)
        # triples = VGroup(*map(TexMobject, [
        #     "3^2 + 4^2 = 5^2",
        #     "5^2 + 12^2 = 13^2",
        #     "8^2 + 15^2 = 17^2",
        #     "\\vdots"
        # ]))
        # triples.arrange(DOWN, buff = MED_LARGE_BUFF)
        # triples.next_to(rect.get_top(), DOWN)
        # self.add(rect, triples)






















