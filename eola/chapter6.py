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

from ka_playgrounds.circuits import Resistor, Source, LongResistor

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject([
            "The question you raise, ",
            "``how can such a formulation lead to computations?''",
                "doesn't bother me in the least! Throughout my whole life "
                "as a mathematician, the possibility of making explicit, "
                "elegant computations has always come out by itself, as a "
                "byproduct of a ",
            "thorough conceptual understanding."
        ], separate_list_arg_with_spaces = False)
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words.split()[1].highlight(BLUE)
        words.split()[3].highlight(GREEN)
        author = TextMobject(["-Grothendieck", "(a hero of mine)"])
        author.split()[0].highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither()

class ListTerms(Scene):
    def construct(self):
        title = TextMobject("Under the light of linear transformations")
        title.highlight(YELLOW)
        title.to_edge(UP)
        randy = Randolph().to_corner()
        words = VMobject(*map(TextMobject, [
            "Inverse matrices", 
            "Column space", 
            "Rank",
            "Null space",
        ]))
        words.arrange_submobjects(DOWN, aligned_edge = LEFT)
        words.next_to(title, DOWN, aligned_edge = LEFT)
        words.shift(RIGHT)

        self.add(title, randy)
        for i, word in enumerate(words.split()):
            self.play(Write(word), run_time = 1)
            if i%2 == 0:
                self.play(Blink(randy))
            else:
                self.dither()
        self.dither()

class NoComputations(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says(
            "Will you cover \\\\ computations?",
            pi_creature_target_mode = "raise_left_hand"
        )
        self.random_blink()
        self.teacher_says(
            "Well...uh...no",
            pi_creature_target_mode = "guilty",
        )
        self.play(*[
            ApplyMethod(student.change_mode, mode)
            for student, mode in zip(
                self.get_students(),
                ["dejected", "confused", "angry"]
            )
        ])
        self.random_blink()
        self.dither()
        new_words = self.teacher.bubble.position_mobject_inside(
            TextMobject([
                "Search",
                "``Gaussian elimination'' \\\\",
                "and",
                "``Row echelon form''",
            ])
        )
        new_words.split()[1].highlight(YELLOW)
        new_words.split()[3].highlight(GREEN)
        self.play(
            Transform(self.teacher.bubble.content, new_words),
            self.teacher.change_mode, "speaking"
        )
        self.play(*[
            ApplyMethod(student.change_mode, "pondering")
            for student in self.get_students()
        ])
        self.random_blink()

class UsefulnessOfMatrices(Scene):
    def construct(self):
        title = TextMobject("Usefulness of matrices")
        title.highlight(YELLOW)
        title.to_edge(UP)
        self.add(title)
        self.dither(3) #Play some 3d linear transform over this

        equations = TexMobject("""
            6x - 3y + 2z &= 7 \\\\
            x + 2y + 5z &= 0 \\\\
            2x - 8y - z &= -2 \\\\
        """)
        equations.to_edge(RIGHT, buff = 2)
        syms = VMobject(*np.array(equations.split())[[1, 4, 7]])
        new_syms = VMobject(*[
            m.copy().highlight(c) 
            for m, c in zip(syms.split(), [X_COLOR, Y_COLOR, Z_COLOR])
        ])
        new_syms.arrange_submobjects(RIGHT, buff = 0.5)
        new_syms.next_to(equations, LEFT, buff = 3)
        sym_brace = Brace(new_syms, DOWN)
        unknowns = sym_brace.get_text("Unknown variables")
        eq_brace = Brace(equations, DOWN)
        eq_words = eq_brace.get_text("Equations")

        self.play(Write(equations))
        self.dither()
        self.play(Transform(syms.copy(), new_syms, path_arc = np.pi/2))
        for brace, words in (sym_brace, unknowns), (eq_brace, eq_words):
            self.play(
                GrowFromCenter(brace),
                Write(words)
            )
            self.dither()

class CircuitDiagram(Scene):
    def construct(self):
        self.add(TextMobject("Voltages").to_edge(UP))

        source = Source()
        p1, p2 = source.get_top(), source.get_bottom()
        r1 = Resistor(p1, p1+2*RIGHT)
        r2 = LongResistor(p1+2*RIGHT, p2+2*RIGHT)
        r3 = Resistor(p1+2*RIGHT, p1+2*2*RIGHT)
        l1 = Line(p1+2*2*RIGHT, p2+2*2*RIGHT)
        l2 = Line(p2+2*2*RIGHT, p2)
        circuit = VMobject(source, r1, r2, r3, l1, l2)
        circuit.center()
        v1 = TexMobject("v_1").next_to(r1, UP)
        v2 = TexMobject("v_2").next_to(r2, RIGHT)
        v3 = TexMobject("v_3").next_to(r3, UP)
        unknowns = VMobject(v1, v2, v3)
        unknowns.highlight(BLUE)

        self.play(ShowCreation(circuit))
        self.dither()
        self.play(Write(unknowns))
        self.dither()

class StockLine(VMobject):
    CONFIG = {
        "num_points" : 15,
        "step_range" : 2
    }
    def generate_points(self):
        points = [ORIGIN]
        for x in range(self.num_points):
            step_size = self.step_range*(random.random() - 0.5)
            points.append(points[-1] + 0.5*RIGHT + step_size*UP)
        self.set_anchor_points(points, mode = "corners")

class StockPrices(Scene):
    def construct(self):
        self.add(TextMobject("Stock prices").to_edge(UP))

        x_axis = Line(ORIGIN, SPACE_WIDTH*RIGHT)
        y_axis = Line(ORIGIN, SPACE_HEIGHT*UP)
        everyone = VMobject(x_axis, y_axis)
        stock_lines = []
        for color in TEAL, PINK, YELLOW, RED, BLUE:
            sl = StockLine(color = color)
            sl.move_to(y_axis.get_center(), side_to_align = LEFT)
            everyone.add(sl)
            stock_lines.append(sl)
        everyone.center()

        self.add(x_axis, y_axis)
        self.play(ShowCreation(
            VMobject(*stock_lines),
            run_time = 3,
            submobject_mode = "lagged_start"
        ))
        self.dither()

class MachineLearningNetwork(Scene):
    def construct(self):
        self.add(TextMobject("Machine learning parameters").to_edge(UP))

        layers = []
        for i, num_nodes in enumerate([3, 4, 4, 1]):
            layer = VMobject(*[
                Circle(radius = 0.5, color = YELLOW)
                for x in range(num_nodes)
            ])
            for j, mob in enumerate(layer.split()):
                sym = TexMobject("x_{%d, %d}"%(i, j))
                sym.move_to(mob)
                mob.add(sym)
            layer.arrange_submobjects(DOWN, buff = 0.5)
            layer.center()
            layers.append(layer)
        VMobject(*layers).arrange_submobjects(RIGHT, buff = 1.5)
        lines = VMobject()
        for l_layer, r_layer in zip(layers, layers[1:]):
            for l_node, r_node in it.product(l_layer.split(), r_layer.split()):
                lines.add(Line(l_node, r_node))
        lines.submobject_gradient_highlight(BLUE_E, BLUE_A)
        for mob in VMobject(*layers), lines:
            self.play(Write(mob), run_time = 2)
        self.dither()

class SystemOfEquations(Scene):
    def construct(self):
        equations = self.get_equations()
        self.show_linearity_rules(equations)
        self.describe_organization(equations)
        self.factor_into_matrix(equations)

    def get_equations(self):
        matrix = Matrix([
            [2, 5, 3],
            [4, 0, 8],
            [1, 3, 0]
        ])
        mob_matrix = matrix.get_mob_matrix()
        rhs = map(TexMobject, map(str, [-3, 0, 2]))
        variables = map(TexMobject, list("xyz"))
        for v, color in zip(variables, [X_COLOR, Y_COLOR, Z_COLOR]):
            v.highlight(color)
        equations = VMobject()
        for row in mob_matrix:
            equation = VMobject(*it.chain(*zip(
                row, 
                [v.copy() for v in variables],
                map(TexMobject, list("++="))
            )))
            equation.arrange_submobjects(
                RIGHT, buff = 0.1, 
                aligned_edge = DOWN
            )
            equation.split()[4].shift(0.1*DOWN)
            equation.split()[-1].next_to(equation.split()[-2], RIGHT)
            equations.add(equation)
        equations.arrange_submobjects(DOWN, aligned_edge = RIGHT)
        for eq, rhs_elem in zip(equations.split(), rhs):
            rhs_elem.next_to(eq, RIGHT)
            eq.add(rhs_elem)
        equations.center()
        self.play(Write(equations))
        self.add(equations)
        return equations

    def show_linearity_rules(self, equations):
        top_equation = equations.split()[0]
        other_equations = VMobject(*equations.split()[1:])
        other_equations.save_state()
        scaled_vars = VMobject(*[
            VMobject(*top_equation.split()[3*i:3*i+2])
            for i in range(3)
        ])
        scaled_vars.save_state()
        isolated_scaled_vars = scaled_vars.copy()
        isolated_scaled_vars.scale(1.5)
        isolated_scaled_vars.next_to(top_equation, UP)
        scalars = VMobject(*[m.split()[0] for m in scaled_vars.split()])
        plusses = np.array(top_equation.split())[[2, 5]]

        self.play(other_equations.fade, 0.7)
        self.play(Transform(scaled_vars, isolated_scaled_vars))
        self.play(scalars.highlight, YELLOW, submobject_mode = "lagged_start")
        self.play(*[
            ApplyMethod(m.scale_in_place, 1.2, rate_func = there_and_back)
            for m in scalars.split()
        ])
        self.dither()
        self.remove(scalars)
        self.play(scaled_vars.restore)
        self.play(*[
            ApplyMethod(p.scale_in_place, 1.5, rate_func = there_and_back)
            for p in plusses
        ])
        self.dither()
        self.show_nonlinearity_examples()
        self.play(other_equations.restore)

    def show_nonlinearity_examples(self):
        squared = TexMobject("x^2")
        squared.split()[0].highlight(X_COLOR)
        sine = TexMobject("\\sin(x)")
        sine.split()[-2].highlight(X_COLOR)
        product = TexMobject("xy")
        product.split()[0].highlight(X_COLOR)
        product.split()[1].highlight(Y_COLOR)


        words = TextMobject("Not allowed!")
        words.highlight(RED)
        words.to_corner(UP+LEFT, buff = 1)
        arrow = Vector(RIGHT, color = RED)
        arrow.next_to(words, RIGHT)
        for mob in squared, sine, product:
            mob.scale(1.7)
            mob.next_to(arrow.get_end(), RIGHT, buff = 0.5)
        circle_slash = Circle(color = RED)
        line = Line(LEFT, RIGHT, color = RED)
        line.rotate(np.pi/4)
        circle_slash.add(line)
        circle_slash.next_to(arrow, RIGHT)
        def draw_circle_slash(mob):
            circle_slash.replace(mob)
            circle_slash.scale_in_place(1.4)
            self.play(ShowCreation(circle_slash), run_time = 0.5)
            self.dither(0.5)
            self.play(FadeOut(circle_slash), run_time = 0.5)

        self.play(
            Write(squared),
            Write(words, run_time = 1),
            ShowCreation(arrow),
        )
        draw_circle_slash(squared)
        for mob in sine, product:
            self.play(Transform(squared, mob))
            draw_circle_slash(mob)
        self.play(*map(FadeOut, [words, arrow, squared]))
        self.dither()


    def describe_organization(self, equations):
        variables = VMobject(*it.chain(*[
            eq.split()[:-2]
            for eq in equations.split()
        ]))
        variables.words = "Throw variables on the left"
        constants = VMobject(*[
            eq.split()[-1]
            for eq in equations.split()
        ])
        constants.words = "Lingering constants on the right"
        xs, ys, zs = [
            VMobject(*[
                eq.split()[i]
                for eq in equations.split()
            ])
            for i in 1, 4, 7
        ]
        ys.words = "Vertically align variables"
        colors = [PINK, YELLOW, BLUE_B, BLUE_C, BLUE_D]
        for mob, color in zip([variables, constants, xs, ys, zs], colors):
            mob.square = Square(color = color)
            mob.square.replace(mob, stretch = True)
            mob.square.scale_in_place(1.1)
            if hasattr(mob, "words"):
                mob.words = TextMobject(mob.words)
                mob.words.highlight(color)
                mob.words.next_to(mob.square, UP)
        ys.square.add(xs.square, zs.square)
        zero_circles = VMobject(*[
            Circle().replace(mob).scale_in_place(1.3)
            for mob in [
                VMobject(*equations.split()[i].split()[j:j+2])
                for i, j in (1, 3), (2, 6)
            ]
        ])
        zero_circles.highlight(PINK)
        zero_circles.words = TextMobject("Add zeros as needed")
        zero_circles.words.highlight(zero_circles.get_color())
        zero_circles.words.next_to(equations, UP)

        for mob in variables, constants, ys:
            self.play(
                FadeIn(mob.square),
                FadeIn(mob.words)
            )
            self.dither()
            self.play(*map(FadeOut, [mob.square, mob.words]))
        self.play(
            ShowCreation(zero_circles),
            Write(zero_circles.words, run_time = 1)
        )
        self.dither()
        self.play(*map(FadeOut, [zero_circles, zero_circles.words]))
        self.dither()
        title = TextMobject("``Linear system of equations''")
        title.scale(1.5)
        title.to_edge(UP)
        self.play(Write(title))
        self.dither()
        self.play(FadeOut(title))


    def factor_into_matrix(self, equations):
        coefficients = np.array([
            np.array(eq.split())[[0, 3, 6]]
            for eq in equations.split()
        ])
        variable_arrays = np.array([
            np.array(eq.split())[[1, 4, 7]]
            for eq in equations.split()
        ])
        rhs_entries = np.array([
            eq.split()[-1]
            for eq in equations.split()
        ])

        matrix = Matrix(copy.deepcopy(coefficients))
        x_array = Matrix(copy.deepcopy(variable_arrays[0]))
        v_array = Matrix(copy.deepcopy(rhs_entries))
        equals = TexMobject("=")
        ax_equals_v = VMobject(matrix, x_array, equals, v_array)
        ax_equals_v.arrange_submobjects(RIGHT)
        ax_equals_v.to_edge(RIGHT)
        all_brackets = [
            mob.get_brackets()
            for mob in matrix, x_array, v_array
        ]

        self.play(equations.to_edge, LEFT)
        arrow = Vector(RIGHT, color = YELLOW)
        arrow.next_to(ax_equals_v, LEFT)
        self.play(ShowCreation(arrow))
        self.play(*it.chain(*[
            [
                Transform(
                    m1.copy(), m2, 
                    run_time = 2,
                    path_arc = -np.pi/2
                )
                for m1, m2 in zip(
                    start_array.flatten(),
                    matrix_mobject.get_entries().split()
                )
            ]
            for start_array, matrix_mobject in [
                (coefficients, matrix),
                (variable_arrays[0], x_array),
                (variable_arrays[1], x_array),
                (variable_arrays[2], x_array),
                (rhs_entries, v_array)
            ]
        ]))
        self.play(*[
            Write(mob)
            for mob in all_brackets + [equals]
        ])
        self.dither()
        self.label_matrix_product(matrix, x_array, v_array)
        
    def label_matrix_product(self, matrix, x_array, v_array):
        matrix.words = "Coefficients"
        matrix.symbol = "A"
        x_array.words = "Variables"
        x_array.symbol = "\\vec{\\textbf{x}}"
        v_array.words = "Constants"
        v_array.symbol = "\\vec{\\textbf{v}}"
        parts = matrix, x_array, v_array
        for mob in parts:
            mob.brace = Brace(mob, UP)
            mob.words = mob.brace.get_text(mob.words)
            mob.words.shift_onto_screen()
            mob.symbol = TexMobject(mob.symbol)
            mob.brace.put_at_tip(mob.symbol)
        x_array.words.submobject_gradient_highlight(
            X_COLOR, Y_COLOR, Z_COLOR
        )
        x_array.symbol.highlight(PINK)
        v_array.symbol.highlight(YELLOW)
        for mob in parts:
            self.play(
                GrowFromCenter(mob.brace),
                FadeIn(mob.words)
            )
            self.dither()
            self.play(*map(FadeOut, [mob.brace, mob.words]))
        self.dither()
        for mob in parts:
            self.play(
                FadeIn(mob.brace),
                Write(mob.symbol)
            )
        compact_equation = VMobject(*[
            mob.symbol for mob in parts
        ])
        compact_equation.submobjects.insert(
            2, TexMobject("=").next_to(x_array, RIGHT)
        )
        compact_equation.target = compact_equation.copy()
        compact_equation.target.arrange_submobjects(buff = 0.1)
        compact_equation.target.to_edge(UP)

        self.play(Transform(
            compact_equation.copy(), 
            compact_equation.target
        ))
        self.dither()

class LinearSystemTransformationScene(LinearTransformationScene):
    def setup(self):
        LinearTransformationScene.setup(self)
        equation = TexMobject([
            "A",
            "\\vec{\\textbf{x}}",
            "=",
            "\\vec{\\textbf{v}}",
        ])
        equation.scale(1.5)
        equation.next_to(ORIGIN, LEFT).to_edge(UP)
        equation.add_background_rectangle()
        self.add_foreground_mobject(equation)
        self.equation = equation
        self.A, self.x, eq, self.v = equation.split()[1].split()
        self.x.highlight(PINK)
        self.v.highlight(YELLOW)

class MentionThatItsATransformation(LinearSystemTransformationScene):
    CONFIG = {
        "t_matrix" : np.array([[2, 1], [2, 3]])
    }
    def construct(self):
        self.setup()
        brace = Brace(self.A)
        words = brace.get_text("Transformation")
        words.add_background_rectangle()
        self.play(GrowFromCenter(brace), Write(words, run_time = 1))
        self.add_foreground_mobject(words, brace)
        self.apply_transposed_matrix(self.t_matrix)
        self.dither()

class LookForX(MentionThatItsATransformation):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        v = [-4, - 1]
        x = np.linalg.solve(self.t_matrix.T, v)
        v = Vector(v, color = YELLOW)
        x = Vector(x, color = PINK)
        v_label = self.get_vector_label(v, "v", color = YELLOW)
        x_label = self.get_vector_label(x, "x", color = PINK)
        for label in x_label, v_label:
            label.add_background_rectangle()
        self.play(
            ShowCreation(v),
            Write(v_label)
        )
        self.add_foreground_mobject(v_label)
        x = self.add_vector(x, animate = False)
        self.play(
            ShowCreation(x),
            Write(x_label)
        )
        self.dither()
        self.add(VMobject(x, x_label).copy().fade())
        self.apply_transposed_matrix(self.t_matrix)
        self.dither()

class SystemOfTwoEquationsTwoUnknowns(Scene):
    def construct(self):
        system = TexMobject("""
            2x + 2y &= -4 \\\\
            1x + 3y &= -1
        """)
        system.to_edge(UP)
        for indices, color in ((1, 9), X_COLOR), ((4, 12), Y_COLOR):
            for i in indices:
                system.split()[i].highlight(color)
        matrix = Matrix([[2, 2], [1, 3]])
        v = Matrix([-4, -1])
        x = Matrix(["x", "y"])
        x.get_entries().submobject_gradient_highlight(X_COLOR, Y_COLOR)
        matrix_system = VMobject(
            matrix, x, TexMobject("="), v
        )
        matrix_system.arrange_submobjects(RIGHT)
        matrix_system.next_to(system, DOWN, buff = 1)

        self.add(system)
        self.play(Write(matrix_system))
        self.dither()

class ShowBijectivity(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "t_matrix" : np.array([[0, -1], [2, 1]])
    }
    def construct(self):
        self.setup()
        vectors = VMobject(*[
            Vector([x, y])
            for x, y in it.product(*[
                np.arange(-int(val)+0.5, int(val)+0.5)
                for val in SPACE_WIDTH, SPACE_HEIGHT
            ])
        ])
        vectors.submobject_gradient_highlight(BLUE_E, PINK)
        dots = VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in vectors.split()
        ])
        titles = [
            TextMobject([
                "Each vector lands on\\\\",
                "exactly one vector"
            ]),
            TextMobject([
                "Every vector has \\\\",
                "been landed on"
            ])
        ]
        for title in titles:
            title.to_edge(UP)
        background = BackgroundRectangle(VMobject(*titles))
        self.add_foreground_mobject(background, titles[0])

        kwargs = {
            "submobject_mode" : "lagged_start",
            "run_time" : 2
        }
        anims = map(Animation, self.foreground_mobjects)
        self.play(ShowCreation(vectors, **kwargs), *anims)
        self.play(Transform(vectors, dots, **kwargs), *anims)
        self.dither()
        self.add_transformable_mobject(vectors)
        self.apply_transposed_matrix(self.t_matrix)
        self.dither()
        self.play(Transform(*titles))
        self.dither()
        self.apply_transposed_matrix(
            np.linalg.inv(self.t_matrix.T).T
        )
        self.dither()

class LabeledExample(LinearSystemTransformationScene):
    CONFIG = {
        "title" : "",
        "t_matrix" : [[0, 0], [0, 0]],
    }
    def setup(self):
        LinearSystemTransformationScene.setup(self)
        title = TextMobject(self.title)
        title.scale(1.5)
        title.next_to(self.equation, DOWN)
        title.add_background_rectangle()
        self.add_foreground_mobject(title)        
        self.title = title

    def construct(self):
        self.setup()
        self.dither()
        self.apply_transposed_matrix(self.t_matrix)
        self.dither()

class SquishExmapleWithWords(LabeledExample):
    CONFIG = {
        "title" : "$A$ squishes things to a lower dimension",
        "t_matrix" : [[-2, -1], [2, 1]]
    }

class FullRankExmapleWithWords(LabeledExample):
    CONFIG = {
        "title" : "$A$ keeps things 2D",
        "t_matrix" : [[3, 0], [2, 1]]
    }

class SquishExmapleDet(SquishExmapleWithWords):
    CONFIG = {
        "title" : "$\\det(A) = 0$",
    }

class FullRankExmapleDet(FullRankExmapleWithWords):
    CONFIG = {
        "title" : "$\\det(A) \\ne 0$",
    }

class PlayInReverse(FullRankExmapleDet):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        FullRankExmapleDet.construct(self)
        v = self.add_vector([-2, -2], color = YELLOW)
        v_label = self.label_vector(v, "v", color = YELLOW)
        self.add(v.copy())
        self.apply_inverse_transpose(self.t_matrix)
        self.play(v.highlight, PINK)
        self.label_vector(v, "x", color = PINK)
        self.dither()

class DescribeInverse(LinearTransformationScene):
    CONFIG = {
        "show_matrix" : False
    }
    def construct(self):
        self.setup()
        title = TextMobject("Transformation:")
        new_title = TextMobject("Inverse transformation:")
        if self.show_matrix:
            matrix = Matrix(self.t_matrix.T)
            inv_matrix = Matrix(np.linalg.inv(self.t_matrix.T).astype('int'))
        else:
            matrix, inv_matrix = map(TexMobject, ["A", "A^{-1}"])
        for m, text in (matrix, title), (inv_matrix, new_title):
            m.rect = BackgroundRectangle(m)
            m = VMobject(m.rect, m)
            text.add_background_rectangle()
            m.next_to(text, RIGHT)
            text.add(m)
            if text.get_width() > 2*SPACE_WIDTH-1:
                text.scale_to_fit_width(2*SPACE_WIDTH-1)
            text.center().to_edge(UP)

        self.add_foreground_mobject(title)
        self.apply_transposed_matrix(self.t_matrix)
        self.dither()
        self.play(Transform(title, new_title))
        self.apply_inverse_transpose(self.t_matrix)
        self.dither()

class ClockwiseCounterclockwise(DescribeInverse):
    CONFIG = {
        "t_matrix" : [[0, 1], [-1, 0]],
        "show_matrix" : True,
    }

class ShearInverseShear(DescribeInverse):
    CONFIG = {
        "t_matrix" : [[1, 0], [1, 1]],
        "show_matrix" : True,
    }

class MultiplyToIdentity(LinearTransformationScene):
    def construct(self):
        self.setup()
        lhs = TexMobject("A", "A^{-1}", "=")
        lhs.scale(1.5)
        A, A_inv, eq = lhs.split()
        identity = Matrix([[1, 0], [0, 1]])
        identity.highlight_columns(X_COLOR, Y_COLOR)
        identity.next_to(eq, RIGHT)
        VMobject(lhs, identity).center().to_edge(UP)
        lhs.add_background_rectangle()
        identity.add_to_back(BackgroundRectangle(identity))

        col1 = VMobject(*identity.get_mob_matrix[:,0])
        col2 = VMobject(*identity.get_mob_matrix[:,1])

        A.text = "Transformation"
        A_inv.text = "Inverse transformation"
        product = VMobject(A, A_inv)
        product.text = "Matrix multiplication"
        identity.text = "The transformation that does nothing"
        for mob in A, A_inv, product, identity:
            mob.brace = Brace(mob)
            mob.text = mob.brace.get_text(mob.text)
            mob.text.add_background_rectangle()

        self.add(A, A_inv)































