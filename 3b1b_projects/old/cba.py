from manimlib.imports import *


class EnumerableSaveScene(Scene):
    def setup(self):
        self.save_count = 0

    def save_enumerated_image(self):
        file_path = self.file_writer.get_image_file_path()
        file_path = file_path.replace(
            ".png", "{:02}.png".format(self.save_count)
        )
        self.update_frame(ignore_skipping=True)
        image = self.get_image()
        image.save(file_path)
        self.save_count += 1


class LayersOfAbstraction(EnumerableSaveScene):
    def construct(self):
        self.save_count = 0
        # self.add_title()
        self.show_layers()
        self.show_pairwise_relations()
        self.circle_certain_pairs()

    def add_title(self):
        title = TextMobject("Layers of abstraction")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        line = Line(LEFT, RIGHT)
        line.set_width(FRAME_WIDTH)
        line.next_to(title, DOWN, SMALL_BUFF)

        self.add(title, line)

    def show_layers(self):
        layers = self.layers = self.get_layers()
        for layer in layers:
            self.add(layer[0])

        self.save_enumerated_image()
        for layer in layers:
            self.add(layer)
            self.save_enumerated_image()

    def show_pairwise_relations(self):
        p1, p2 = [l.get_left() for l in self.layers[2:4]]
        down_arrow = Arrow(p2, p1, path_arc=PI)
        down_words = TextMobject("``For example''")
        down_words.scale(0.8)
        down_words.next_to(down_arrow, LEFT)
        up_arrow = Arrow(p1, p2, path_arc=-PI)
        up_words = TextMobject("``In general''")
        up_words.scale(0.8)
        up_words.next_to(up_arrow, LEFT)

        VGroup(up_words, down_words).set_color(YELLOW)

        self.add(down_arrow, down_words)
        self.save_enumerated_image()
        self.remove(down_arrow, down_words)
        self.add(up_arrow, up_words)
        self.save_enumerated_image()
        self.remove(up_arrow, up_words)

    def circle_certain_pairs(self):
        layers = self.layers

        for l1, l2 in zip(layers, layers[1:]):
            group = VGroup(l1, l2)
            group.save_state()
            layers.save_state()
            layers.fade(0.75)
            rect = SurroundingRectangle(group)
            rect.set_stroke(YELLOW, 5)
            group.restore()
            self.add(rect)
            self.save_enumerated_image()
            self.remove(rect)
            layers.restore()

    #

    def get_layers(self):
        layers = VGroup(*[
            VGroup(Rectangle(height=1, width=5))
            for x in range(6)
        ])
        layers.arrange_submobjects(UP, buff=0)
        layers.set_stroke(GREY, 2)
        layers.set_sheen(1, UL)

        # Layer 0: Quantities
        triangle = Triangle().set_height(0.25)
        tri_dots = VGroup(*[Dot(v) for v in triangle.get_vertices()])
        dots_rect = VGroup(*[Dot() for x in range(12)])
        dots_rect.arrange_in_grid(3, 4, buff=SMALL_BUFF)
        for i, color in enumerate([RED, GREEN, BLUE]):
            dots_rect[i::4].set_color(color)
        pi_chart = VGroup(*[
            Sector(start_angle=a, angle=TAU / 3)
            for a in np.arange(0, TAU, TAU / 3)
        ])
        pi_chart.set_fill(opacity=0)
        pi_chart.set_stroke(WHITE, 2)
        pi_chart[0].set_fill(BLUE, 1)
        pi_chart.rotate(PI / 3)
        pi_chart.match_height(dots_rect)
        quantities = VGroup(tri_dots, dots_rect, pi_chart)
        quantities.arrange(RIGHT, buff=LARGE_BUFF)

        # Layer 1: Numbers
        numbers = VGroup(
            TexMobject("3"),
            TexMobject("3 \\times 4"),
            TexMobject("1 / 3"),
        )
        for number, quantity in zip(numbers, quantities):
            number.move_to(quantity)

        # Layer 2: Algebra
        algebra = VGroup(
            TexMobject("x^2 - 1 = (x + 1)(x - 1)")
        )
        algebra.set_width(layers.get_width() - MED_LARGE_BUFF)

        # Layer 3: Functions
        functions = VGroup(
            TexMobject("f(x) = 0"),
            TexMobject("\\frac{df}{dx}"),
        )
        functions.set_height(layers[0].get_height() - 2 * SMALL_BUFF)
        functions.arrange(RIGHT, buff=LARGE_BUFF)
        # functions.match_width(algebra)

        # Layer 4: Vector space
        t2c_map = {
            "\\textbf{v}": YELLOW,
            "\\textbf{w}": PINK,
        }
        vector_spaces = VGroup(
            TexMobject(
                "\\textbf{v} + \\textbf{w} ="
                "\\textbf{w} + \\textbf{v}",
                tex_to_color_map=t2c_map,
            ),
            TexMobject(
                "s(\\textbf{v} + \\textbf{w}) ="
                "s\\textbf{v} + s\\textbf{w}",
                tex_to_color_map=t2c_map,
            ),
        )
        vector_spaces.arrange(DOWN, buff=MED_SMALL_BUFF)
        vector_spaces.set_height(layers[0].get_height() - MED_LARGE_BUFF)
        v, w = vectors = VGroup(
            Vector([2, 1, 0], color=YELLOW),
            Vector([1, 2, 0], color=PINK),
        )
        vectors.add(DashedLine(v.get_end(), v.get_end() + w.get_vector()))
        vectors.add(DashedLine(w.get_end(), w.get_end() + v.get_vector()))
        vectors.match_height(vector_spaces)
        vectors.next_to(vector_spaces, RIGHT)
        vectors.set_stroke(width=2)
        # vector_spaces.add(vectors)

        inner_product = TexMobject(
            "\\langle f, g \\rangle ="
            "\\int f(x)g(x)dx"
        )
        inner_product.match_height(vector_spaces)
        inner_product.next_to(vector_spaces, RIGHT)
        vector_spaces.add(inner_product)

        # Layer 5: Categories
        dots = VGroup(Dot(UP), Dot(UR), Dot(RIGHT))
        arrows = VGroup(
            Arrow(dots[0], dots[1], buff=SMALL_BUFF),
            Arrow(dots[1], dots[2], buff=SMALL_BUFF),
            Arrow(dots[0], dots[2], buff=SMALL_BUFF),
        )
        arrows.set_stroke(width=2)
        arrow_labels = VGroup(
            TexMobject("m_1").next_to(arrows[0], UP, SMALL_BUFF),
            TexMobject("m_2").next_to(arrows[1], RIGHT, SMALL_BUFF),
            TexMobject("m_2 \\circ m_1").rotate(-45 * DEGREES).move_to(
                arrows[2]
            ).shift(MED_SMALL_BUFF * DL)
        )
        categories = VGroup(dots, arrows, arrow_labels)
        categories.set_height(layers[0].get_height() - MED_SMALL_BUFF)

        # Put it all together
        all_content = [
            quantities, numbers, algebra,
            functions, vector_spaces, categories,
        ]

        for layer, content in zip(layers, all_content):
            content.move_to(layer)
            layer.add(content)
            layer.content = content

        layer_titles = VGroup(*map(TextMobject, [
            "Quantities",
            "Numbers",
            "Algebra",
            "Functions",
            "Vector spaces",
            "Categories",
        ]))
        for layer, title in zip(layers, layer_titles):
            title.next_to(layer, RIGHT)
            layer.add(title)
            layer.title = title
        layers.titles = layer_titles

        layers.center()
        layers.to_edge(DOWN)
        layers.shift(0.5 * RIGHT)
        return layers


class DifferenceOfSquares(Scene):
    def construct(self):
        squares = VGroup(*[
            VGroup(*[
                Square()
                for x in range(8)
            ]).arrange(RIGHT, buff=0)
            for y in range(8)
        ]).arrange(DOWN, buff=0)
        squares.set_height(4)
        squares.set_stroke(BLUE, 3)
        squares.set_fill(BLUE, 0.5)

        last_row_parts = VGroup()
        for row in squares[-3:]:
            row[-3:].set_color(RED)
            row[:-3].set_color(BLUE_B)
            last_row_parts.add(row[:-3])
        squares.to_edge(LEFT)

        arrow = Vector(RIGHT, color=WHITE)
        arrow.shift(1.5 * LEFT)
        squares.next_to(arrow, LEFT)

        new_squares = squares[:-3].copy()
        new_squares.next_to(arrow, RIGHT)
        new_squares.align_to(squares, UP)

        x1 = TexMobject("x").set_color(BLUE)
        x2 = x1.copy()
        x1.next_to(squares, UP)
        x2.next_to(squares, LEFT)
        y1 = TexMobject("y").set_color(RED)
        y2 = y1.copy()
        y1.next_to(squares[-2], RIGHT)
        y2.next_to(squares[-1][-2], DOWN)

        xpy = TexMobject("x", "+", "y")
        xmy = TexMobject("x", "-", "y")
        for mob in xpy, xmy:
            mob[0].set_color(BLUE)
            mob[2].set_color(RED)
        xpy.next_to(new_squares, UP)
        # xmy.rotate(90 * DEGREES)
        xmy.next_to(new_squares, RIGHT)
        xmy.to_edge(RIGHT)

        self.add(squares, x1, x2, y1, y2)
        self.play(
            ReplacementTransform(
                squares[:-3].copy().set_fill(opacity=0),
                new_squares
            ),
            ShowCreation(arrow),
            lag_ratio=0,
        )
        last_row_parts = last_row_parts.copy()
        last_row_parts.save_state()
        last_row_parts.set_fill(opacity=0)
        self.play(
            last_row_parts.restore,
            last_row_parts.rotate, -90 * DEGREES,
            last_row_parts.next_to, new_squares, RIGHT, {"buff": 0},
            lag_ratio=0,
        )
        self.play(Write(xmy), Write(xpy))
        self.wait()


class Lightbulbs(EnumerableSaveScene):
    def construct(self):
        dots = VGroup(*[Dot() for x in range(4)])
        dots.set_height(0.5)
        dots.arrange(RIGHT, buff=2)
        dots.set_fill(opacity=0)
        dots.set_stroke(width=2, color=WHITE)
        dot_radius = dots[0].get_width() / 2

        connections = VGroup()
        for d1, d2 in it.product(dots, dots):
            line = Line(
                d1.get_center(),
                d2.get_center(),
                path_arc=30 * DEGREES,
                buff=dot_radius,
                color=YELLOW,
            )
            connections.add(line)

        lower_dots = dots[:3].copy()
        lower_dots.next_to(dots, DOWN, buff=2)
        lower_lines = VGroup(*[
            Line(d.get_center(), ld.get_center(), buff=dot_radius)
            for d, ld in it.product(dots, lower_dots[1:])
        ])
        lower_lines.match_style(connections)

        top_dot = dots[0].copy()
        top_dot.next_to(dots, UP, buff=2)

        top_lines = VGroup(*[
            Line(d.get_center(), top_dot.get_center(), buff=dot_radius)
            for d in dots
        ])
        top_lines.match_style(connections)

        self.add(dots)
        self.add(top_dot)
        self.save_enumerated_image()
        dots.set_fill(YELLOW, 1)
        self.save_enumerated_image()
        self.add(connections)
        self.save_enumerated_image()
        self.add(lower_dots)
        self.add(lower_lines)
        lower_dots[1:].set_fill(YELLOW, 1)
        self.save_enumerated_image()

        self.add(top_lines)
        connections.set_stroke(width=1)
        lower_lines.set_stroke(width=1)
        top_dot.set_fill(YELLOW, 1)
        self.save_enumerated_image()

        self.remove(connections)
        self.remove(top_lines)
        self.remove(lower_lines)
        dots.set_fill(opacity=0)
        lower_dots.set_fill(opacity=0)


class LayersOfLightbulbs(Scene):
    CONFIG = {
        "random_seed": 1,
    }

    def construct(self):
        layers = VGroup()
        for x in range(6):
            n_dots = 5 + (x % 2)
            dots = VGroup(*[Dot() for x in range(n_dots)])
            dots.scale(2)
            dots.arrange(RIGHT, buff=MED_LARGE_BUFF)
            dots.set_stroke(WHITE, 2)
            for dot in dots:
                dot.set_fill(YELLOW, np.random.random())
            layers.add(dots)

        layers.arrange(UP, buff=LARGE_BUFF)

        lines = VGroup()
        for l1, l2 in zip(layers, layers[1:]):
            for d1, d2 in it.product(l1, l2):
                color = interpolate_color(
                    YELLOW, GREEN, np.random.random()
                )
                line = Line(
                    d1.get_center(),
                    d2.get_center(),
                    buff=(d1.get_width() / 2),
                    color=color,
                    stroke_width=2 * np.random.random(),
                )
                lines.add(line)

        self.add(layers, lines)


class Test(Scene):
    def construct(self):
        # self.change_all_student_modes("hooray")
        # self.teacher.change("raise_right_hand")
        # self.look_at(3 * UP)
        randy = Randolph()
        randy.change("pondering")
        randy.set_height(6)
        randy.look(RIGHT)
        self.add(randy)
        # eq = TexMobject("143", "=", "11 \\cdot 13")
        # eq[0].set_color(YELLOW)
        # eq.scale(0.7)
        # self.add(eq)
