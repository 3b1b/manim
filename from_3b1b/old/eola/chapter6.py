from manimlib.imports import *
from ka_playgrounds.circuits import Resistor, Source, LongResistor

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "To ask the",
            "right question\\\\",
            "is harder than to answer it." 
        )
        words.to_edge(UP)
        words[1].set_color(BLUE)
        author = TextMobject("-Georg Cantor")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(2)
        self.play(Write(author, run_time = 3))
        self.wait()

class ListTerms(Scene):
    def construct(self):
        title = TextMobject("Under the light of linear transformations")
        title.set_color(YELLOW)
        title.to_edge(UP)
        randy = Randolph().to_corner()
        words = VMobject(*list(map(TextMobject, [
            "Inverse matrices", 
            "Column space", 
            "Rank",
            "Null space",
        ])))
        words.arrange(DOWN, aligned_edge = LEFT)
        words.next_to(title, DOWN, aligned_edge = LEFT)
        words.shift(RIGHT)

        self.add(title, randy)
        for i, word in enumerate(words.split()):
            self.play(Write(word), run_time = 1)
            if i%2 == 0:
                self.play(Blink(randy))
            else:
                self.wait()
        self.wait()

class NoComputations(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says(
            "Will you cover \\\\ computations?",
            target_mode = "raise_left_hand"
        )
        self.random_blink()
        self.teacher_says(
            "Well...uh...no",
            target_mode = "guilty",
        )
        self.play(*[
            ApplyMethod(student.change_mode, mode)
            for student, mode in zip(
                self.get_students(),
                ["dejected", "confused", "angry"]
            )
        ])
        self.random_blink()
        self.wait()
        new_words = self.teacher.bubble.position_mobject_inside(
            TextMobject([
                "Search",
                "``Gaussian elimination'' \\\\",
                "and",
                "``Row echelon form''",
            ])
        )
        new_words.split()[1].set_color(YELLOW)
        new_words.split()[3].set_color(GREEN)
        self.play(
            Transform(self.teacher.bubble.content, new_words),
            self.teacher.change_mode, "speaking"
        )
        self.play(*[
            ApplyMethod(student.change_mode, "pondering")
            for student in self.get_students()
        ])
        self.random_blink()

class PuntToSoftware(Scene):
    def construct(self):
        self.play(Write("Let the computers do the computing"))

class UsefulnessOfMatrices(Scene):
    def construct(self):
        title = TextMobject("Usefulness of matrices")
        title.set_color(YELLOW)
        title.to_edge(UP)
        self.add(title)
        self.wait(3) #Play some 3d linear transform over this

        equations = TexMobject("""
            6x - 3y + 2z &= 7 \\\\
            x + 2y + 5z &= 0 \\\\
            2x - 8y - z &= -2 \\\\
        """)
        equations.to_edge(RIGHT, buff = 2)
        syms = VMobject(*np.array(equations.split())[[1, 4, 7]])
        new_syms = VMobject(*[
            m.copy().set_color(c) 
            for m, c in zip(syms.split(), [X_COLOR, Y_COLOR, Z_COLOR])
        ])
        new_syms.arrange(RIGHT, buff = 0.5)
        new_syms.next_to(equations, LEFT, buff = 3)
        sym_brace = Brace(new_syms, DOWN)
        unknowns = sym_brace.get_text("Unknown variables")
        eq_brace = Brace(equations, DOWN)
        eq_words = eq_brace.get_text("Equations")

        self.play(Write(equations))
        self.wait()
        self.play(Transform(syms.copy(), new_syms, path_arc = np.pi/2))
        for brace, words in (sym_brace, unknowns), (eq_brace, eq_words):
            self.play(
                GrowFromCenter(brace),
                Write(words)
            )
            self.wait()

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
        unknowns.set_color(BLUE)

        self.play(ShowCreation(circuit))
        self.wait()
        self.play(Write(unknowns))
        self.wait()

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
        self.set_points_as_corners(points)

class StockPrices(Scene):
    def construct(self):
        self.add(TextMobject("Stock prices").to_edge(UP))

        x_axis = Line(ORIGIN, FRAME_X_RADIUS*RIGHT)
        y_axis = Line(ORIGIN, FRAME_Y_RADIUS*UP)
        everyone = VMobject(x_axis, y_axis)
        stock_lines = []
        for color in TEAL, PINK, YELLOW, RED, BLUE:
            sl = StockLine(color = color)
            sl.move_to(y_axis.get_center(), aligned_edge = LEFT)
            everyone.add(sl)
            stock_lines.append(sl)
        everyone.center()

        self.add(x_axis, y_axis)
        self.play(ShowCreation(
            VMobject(*stock_lines),
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait()

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
            layer.arrange(DOWN, buff = 0.5)
            layer.center()
            layers.append(layer)
        VMobject(*layers).arrange(RIGHT, buff = 1.5)
        lines = VMobject()
        for l_layer, r_layer in zip(layers, layers[1:]):
            for l_node, r_node in it.product(l_layer.split(), r_layer.split()):
                lines.add(Line(l_node, r_node))
        lines.set_submobject_colors_by_gradient(BLUE_E, BLUE_A)
        for mob in VMobject(*layers), lines:
            self.play(Write(mob), run_time = 2)
        self.wait()

class ComplicatedSystem(Scene):
    def construct(self):
        system = TexMobject("""
        \\begin{align*}
            \\dfrac{1}{1-e^{2x-3y+4z}} &= 1 \\\\ \\\\
            \\sin(xy) + z^2 &= \\sqrt{y} \\\\ \\\\
            x^2 + y^2 &= e^{-z}
        \\end{align*}
        """)
        system.to_edge(UP)
        randy = Randolph().to_corner(DOWN+LEFT)

        self.add(randy)
        self.play(Write(system, run_time = 1))
        self.play(randy.change_mode, "sassy")
        self.play(Blink(randy))
        self.wait()

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
        rhs = list(map(TexMobject, list(map(str, [-3, 0, 2]))))
        variables = list(map(TexMobject, list("xyz")))
        for v, color in zip(variables, [X_COLOR, Y_COLOR, Z_COLOR]):
            v.set_color(color)
        equations = VMobject()
        for row in mob_matrix:
            equation = VMobject(*it.chain(*list(zip(
                row, 
                [v.copy() for v in variables],
                list(map(TexMobject, list("++=")))
            ))))
            equation.arrange(
                RIGHT, buff = 0.1, 
                aligned_edge = DOWN
            )
            equation.split()[4].shift(0.1*DOWN)
            equation.split()[-1].next_to(equation.split()[-2], RIGHT)
            equations.add(equation)
        equations.arrange(DOWN, aligned_edge = RIGHT)
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
        self.play(scalars.set_color, YELLOW, lag_ratio = 0.5)
        self.play(*[
            ApplyMethod(m.scale_in_place, 1.2, rate_func = there_and_back)
            for m in scalars.split()
        ])
        self.wait()
        self.remove(scalars)
        self.play(scaled_vars.restore)
        self.play(*[
            ApplyMethod(p.scale_in_place, 1.5, rate_func = there_and_back)
            for p in plusses
        ])
        self.wait()
        self.show_nonlinearity_examples()
        self.play(other_equations.restore)

    def show_nonlinearity_examples(self):
        squared = TexMobject("x^2")
        squared.split()[0].set_color(X_COLOR)
        sine = TexMobject("\\sin(x)")
        sine.split()[-2].set_color(X_COLOR)
        product = TexMobject("xy")
        product.split()[0].set_color(X_COLOR)
        product.split()[1].set_color(Y_COLOR)


        words = TextMobject("Not allowed!")
        words.set_color(RED)
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
            self.wait(0.5)
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
        self.play(*list(map(FadeOut, [words, arrow, squared])))
        self.wait()


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
            for i in (1, 4, 7)
        ]
        ys.words = "Vertically align variables"
        colors = [PINK, YELLOW, BLUE_B, BLUE_C, BLUE_D]
        for mob, color in zip([variables, constants, xs, ys, zs], colors):
            mob.square = Square(color = color)
            mob.square.replace(mob, stretch = True)
            mob.square.scale_in_place(1.1)
            if hasattr(mob, "words"):
                mob.words = TextMobject(mob.words)
                mob.words.set_color(color)
                mob.words.next_to(mob.square, UP)
        ys.square.add(xs.square, zs.square)
        zero_circles = VMobject(*[
            Circle().replace(mob).scale_in_place(1.3)
            for mob in [
                VMobject(*equations.split()[i].split()[j:j+2])
                for i, j in [(1, 3), (2, 6)]
            ]
        ])
        zero_circles.set_color(PINK)
        zero_circles.words = TextMobject("Add zeros as needed")
        zero_circles.words.set_color(zero_circles.get_color())
        zero_circles.words.next_to(equations, UP)

        for mob in variables, constants, ys:
            self.play(
                FadeIn(mob.square),
                FadeIn(mob.words)
            )
            self.wait()
            self.play(*list(map(FadeOut, [mob.square, mob.words])))
        self.play(
            ShowCreation(zero_circles),
            Write(zero_circles.words, run_time = 1)
        )
        self.wait()
        self.play(*list(map(FadeOut, [zero_circles, zero_circles.words])))
        self.wait()
        title = TextMobject("``Linear system of equations''")
        title.scale(1.5)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()
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
        ax_equals_v.arrange(RIGHT)
        ax_equals_v.to_edge(RIGHT)
        all_brackets = [
            mob.get_brackets()
            for mob in (matrix, x_array, v_array)
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
        self.wait()
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
        x_array.words.set_submobject_colors_by_gradient(
            X_COLOR, Y_COLOR, Z_COLOR
        )
        x_array.symbol.set_color(PINK)
        v_array.symbol.set_color(YELLOW)
        for mob in parts:
            self.play(
                GrowFromCenter(mob.brace),
                FadeIn(mob.words)
            )
            self.wait()
            self.play(*list(map(FadeOut, [mob.brace, mob.words])))
        self.wait()
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
        compact_equation.target.arrange(buff = 0.1)
        compact_equation.target.to_edge(UP)

        self.play(Transform(
            compact_equation.copy(), 
            compact_equation.target
        ))
        self.wait()

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
        self.x.set_color(PINK)
        self.v.set_color(YELLOW)

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
        self.wait()

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
        self.wait()
        self.add(VMobject(x, x_label).copy().fade())
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()

class ThinkAboutWhatsHappening(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_corner()
        bubble = randy.get_bubble(height = 5)
        bubble.add_content(TexMobject("""
            3x + 1y + 4z &= 1 \\\\
            5x + 9y + 2z &= 6 \\\\
            5x + 3y + 5z &= 8
        """))

        self.play(randy.change_mode, "pondering")
        self.play(ShowCreation(bubble))
        self.play(Write(bubble.content, run_time = 2))
        self.play(Blink(randy))
        self.wait()
        everything = VMobject(*self.get_mobjects())
        self.play(
            ApplyFunction(
                lambda m : m.shift(2*DOWN).scale(5),
                everything
            ),
            bubble.content.set_color, BLACK,
            run_time = 2
        )

class SystemOfTwoEquationsTwoUnknowns(Scene):
    def construct(self):
        system = TexMobject("""
            2x + 2y &= -4 \\\\
            1x + 3y &= -1
        """)
        system.to_edge(UP)
        for indices, color in ((1, 9), X_COLOR), ((4, 12), Y_COLOR):
            for i in indices:
                system.split()[i].set_color(color)
        matrix = Matrix([[2, 2], [1, 3]])
        v = Matrix([-4, -1])
        x = Matrix(["x", "y"])
        x.get_entries().set_submobject_colors_by_gradient(X_COLOR, Y_COLOR)
        matrix_system = VMobject(
            matrix, x, TexMobject("="), v
        )
        matrix_system.arrange(RIGHT)
        matrix_system.next_to(system, DOWN, buff = 1)
        matrix.label = "A"
        matrix.label_color = WHITE
        x.label = "\\vec{\\textbf{x}}"
        x.label_color = PINK
        v.label = "\\vec{\\textbf{v}}"
        v.label_color = YELLOW
        for mob in matrix, x, v:
            brace = Brace(mob)
            label = brace.get_text("$%s$"%mob.label)
            label.set_color(mob.label_color)
            brace.add(label)
            mob.brace = brace

        self.add(system)
        self.play(Write(matrix_system))
        self.wait()
        for mob in matrix, v, x:
            self.play(Write(mob.brace))
            self.wait()

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
                for val in (FRAME_X_RADIUS, FRAME_Y_RADIUS)
            ])
        ])
        vectors.set_submobject_colors_by_gradient(BLUE_E, PINK)
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
            "lag_ratio" : 0.5,
            "run_time" : 2
        }
        anims = list(map(Animation, self.foreground_mobjects))
        self.play(ShowCreation(vectors, **kwargs), *anims)
        self.play(Transform(vectors, dots, **kwargs), *anims)
        self.wait()
        self.add_transformable_mobject(vectors)
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()
        self.play(Transform(*titles))
        self.wait()
        self.apply_transposed_matrix(
            np.linalg.inv(self.t_matrix.T).T
        )
        self.wait()

class LabeledExample(LinearSystemTransformationScene):
    CONFIG = {
        "title" : "",
        "t_matrix" : [[0, 0], [0, 0]],
        "show_square" : False,
    }
    def setup(self):
        LinearSystemTransformationScene.setup(self)
        title = TextMobject(self.title)
        title.next_to(self.equation, DOWN, buff = 1)
        title.add_background_rectangle()
        title.shift_onto_screen()
        self.add_foreground_mobject(title)        
        self.title = title
        if self.show_square:
            self.add_unit_square()

    def construct(self):
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()

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
        "show_square" : True,
    }

class FullRankExmapleDet(FullRankExmapleWithWords):
    CONFIG = {
        "title" : "$\\det(A) \\ne 0$",
        "show_square" : True,
    }

class StartWithNonzeroDetCase(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "Let's start with \\\\",
            "the", "$\\det(A) \\ne 0$", "case"
        )
        words[2].set_color(TEAL)
        self.teacher_says(words)
        self.random_blink()
        self.play(
            random.choice(self.get_students()).change_mode,
            "happy"
        )
        self.wait()

class DeclareNewTransformation(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "Playing a transformation in\\\\",
            "reverse gives a", "new transformation"
        )
        words[-1].set_color(GREEN)
        self.teacher_says(words)
        self.change_student_modes("pondering", "sassy")
        self.random_blink()

class PlayInReverse(FullRankExmapleDet):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        FullRankExmapleDet.construct(self)
        v = self.add_vector([-4, -1], color = YELLOW)
        v_label = self.label_vector(v, "v", color = YELLOW)
        self.add(v.copy())
        self.apply_inverse_transpose(self.t_matrix)
        self.play(v.set_color, PINK)
        self.label_vector(v, "x", color = PINK)
        self.wait()

class DescribeInverse(LinearTransformationScene):
    CONFIG = {
        "show_actual_inverse" : False,
        "matrix_label" : "$A$",
        "inv_label" : "$A^{-1}$",
    }
    def construct(self):
        title = TextMobject("Transformation:")
        new_title = TextMobject("Inverse transformation:")
        matrix = Matrix(self.t_matrix.T)
        if not self.show_actual_inverse:
            inv_matrix = matrix.copy()
            neg_1 = TexMobject("-1")
            neg_1.move_to(
                inv_matrix.get_corner(UP+RIGHT), 
                aligned_edge = LEFT
            )
            neg_1.shift(0.1*RIGHT)
            inv_matrix.add(neg_1)
            matrix.add(VectorizedPoint(matrix.get_corner(UP+RIGHT)))
        else:
            inv_matrix = Matrix(np.linalg.inv(self.t_matrix.T).astype('int'))
        matrix.label = self.matrix_label
        inv_matrix.label = self.inv_label
        for m, text in (matrix, title), (inv_matrix, new_title):
            m.add_to_back(BackgroundRectangle(m))
            text.add_background_rectangle()
            m.next_to(text, RIGHT)
            brace = Brace(m)
            label_mob = brace.get_text(m.label)
            label_mob.add_background_rectangle()
            m.add(brace, label_mob)
            text.add(m)
            if text.get_width() > FRAME_WIDTH-1:
                text.set_width(FRAME_WIDTH-1)
            text.center().to_corner(UP+RIGHT)
        matrix.set_color(PINK)
        inv_matrix.set_color(YELLOW)

        self.add_foreground_mobject(title)
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()
        self.play(Transform(title, new_title))
        self.apply_inverse_transpose(self.t_matrix)
        self.wait()

class ClockwiseCounterclockwise(DescribeInverse):
    CONFIG = {
        "t_matrix" : [[0, 1], [-1, 0]],
        "show_actual_inverse" : True,
        "matrix_label" : "$90^\\circ$ Couterclockwise",
        "inv_label" : "$90^\\circ$ Clockwise",
    }

class ShearInverseShear(DescribeInverse):
    CONFIG = {
        "t_matrix" : [[1, 0], [1, 1]],
        "show_actual_inverse" : True,
        "matrix_label" : "Rightward shear",
        "inv_label" : "Leftward shear",
    }

class MultiplyToIdentity(LinearTransformationScene):
    def construct(self):
        self.setup()
        lhs = TexMobject("A^{-1}", "A", "=")
        lhs.scale(1.5)
        A_inv, A, eq = lhs.split()
        identity = Matrix([[1, 0], [0, 1]])
        identity.set_column_colors(X_COLOR, Y_COLOR)
        identity.next_to(eq, RIGHT)
        VMobject(lhs, identity).center().to_corner(UP+RIGHT)
        for mob in A, A_inv, eq:
            mob.add_to_back(BackgroundRectangle(mob))
        identity.background = BackgroundRectangle(identity)

        col1 = VMobject(*identity.get_mob_matrix()[:,0])
        col2 = VMobject(*identity.get_mob_matrix()[:,1])

        A.text = "Transformation"
        A_inv.text = "Inverse transformation"
        product = VMobject(A, A_inv)
        product.text = "Matrix multiplication"
        identity.text = "The transformation \\\\ that does nothing"
        for mob in A, A_inv, product, identity:
            mob.brace = Brace(mob)
            mob.text = mob.brace.get_text(mob.text)
            mob.text.shift_onto_screen()
            mob.text.add_background_rectangle()

        self.add_foreground_mobject(A, A_inv)
        brace, text = A.brace, A.text
        self.play(GrowFromCenter(brace), Write(text), run_time = 1)
        self.add_foreground_mobject(brace, text)
        self.apply_transposed_matrix(self.t_matrix)
        self.play(
            Transform(brace, A_inv.brace),
            Transform(text, A_inv.text),
        )
        self.apply_inverse_transpose(self.t_matrix)
        self.wait()
        self.play(
            Transform(brace, product.brace),
            Transform(text, product.text)
        )
        self.wait()
        self.play(
            Write(identity.background),
            Write(identity.get_brackets()),
            Write(eq),
            Transform(brace, identity.brace),
            Transform(text, identity.text)
        )
        self.wait()
        self.play(Write(col1))
        self.wait()
        self.play(Write(col2))
        self.wait()

class ThereAreComputationMethods(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            There are methods
            to compute $A^{-1}$
        """)
        self.random_blink()
        self.wait()

class TwoDInverseFormula(Scene):
    def construct(self):
        title = TextMobject("If you're curious...")
        title.set_color(YELLOW)
        title.to_edge(UP)
        morty = Mortimer().to_corner(DOWN+RIGHT)
        self.add(title, morty)
        matrix = [["a", "b"], ["c", "d"]]
        scaled_inv = [["d", "-b"], ["-c", "a"]]
        formula = TexMobject("""
            %s^{-1} = \\dfrac{1}{ad-bc} %s
        """%(
            matrix_to_tex_string(matrix),
            matrix_to_tex_string(scaled_inv)
        ))
        self.play(Write(formula))
        self.play(morty.change_mode, "confused")
        self.play(Blink(morty))

class SymbolicInversion(Scene):
    def construct(self):
        vec = lambda s : "\\vec{\\textbf{%s}}"%s
        
        words = TextMobject("Once you have this:")
        words.to_edge(UP, buff = 2)
        inv = TexMobject("A^{-1}")
        inv.set_color(GREEN)
        inv.next_to(words.split()[-1], RIGHT, aligned_edge = DOWN)
        inv2 = inv.copy()

        start = TexMobject("A", vec("x"), "=", vec("v"))
        interim = TexMobject("A^{-1}", "A", vec("x"), "=", "A^{-1}", vec("v"))
        end = TexMobject(vec("x"), "=", "A^{-1}", vec("v"))

        A, x, eq, v = start.split()
        x.set_color(PINK)
        v.set_color(YELLOW)
        interim_mobs = [inv, A, x, eq, inv2, v]
        for i, mob in enumerate(interim_mobs):
            mob.interim = mob.copy().move_to(interim.split()[i])

        self.add(start)
        self.play(Write(words), FadeIn(inv), run_time = 1)
        self.wait()
        self.play(
            FadeOut(words),
            *[Transform(m, m.interim) for m in interim_mobs]
        )
        self.wait()

        product = VMobject(A, inv)
        product.brace = Brace(product)
        product.words = product.brace.get_text(
            "The ``do nothing'' matrix"
        )
        product.words.set_color(BLUE)
        self.play(
            GrowFromCenter(product.brace),
            Write(product.words, run_time = 1),
            product.set_color, BLUE
        )
        self.wait()
        self.play(*[
            ApplyMethod(m.set_color, BLACK)
            for m in (product, product.brace, product.words)
        ])
        self.wait()
        self.play(ApplyFunction(
            lambda m : m.center().to_edge(UP),
            VMobject(x, eq, inv2, v)
        ))
        self.wait()

class PlayInReverseWithSolution(PlayInReverse):
    CONFIG = {
        "t_matrix" : [[2, 1], [2, 3]]
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        equation = TexMobject([
            "\\vec{\\textbf{x}}",
            "=",
            "A^{-1}",
            "\\vec{\\textbf{v}}",
        ])
        equation.to_edge(UP)
        equation.add_background_rectangle()
        self.add_foreground_mobject(equation)
        self.equation = equation
        self.x, eq, self.inv, self.v = equation.split()[1].split()
        self.x.set_color(PINK)
        self.v.set_color(YELLOW)
        self.inv.set_color(GREEN)

class OneUniqueSolution(Scene):
    def construct(self):
        system = TexMobject("""
            \\begin{align*}
                ax + cy &= e \\\\
                bx + dy &= f
            \\end{align*}
        """)
        VMobject(*np.array(system.split())[[1, 8]]).set_color(X_COLOR)
        VMobject(*np.array(system.split())[[4, 11]]).set_color(Y_COLOR)
        brace = Brace(system, UP)
        brace.set_color(YELLOW)
        words = brace.get_text("One unique solution \\dots", "probably")
        words.set_color(YELLOW)
        words.split()[1].set_color(GREEN)

        self.add(system)
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(words.split()[0])
        )
        self.wait()
        self.play(Write(words.split()[1], run_time = 1))
        self.wait()

class ThreeDTransformXToV(Scene):
    pass

class ThreeDTransformAndReverse(Scene):
    pass

class DetNEZeroRule(Scene):
    def construct(self):
        text = TexMobject("\\det(A) \\ne 0")
        text.shift(2*UP)
        A_inv = TextMobject("$A^{-1}$ exists")
        A_inv.shift(DOWN)
        arrow = Arrow(text, A_inv)
        self.play(Write(text))
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(Write(A_inv, run_time = 1))
        self.wait()


class ThreeDInverseRule(Scene):
    def construct(self):
        form = TexMobject("A^{-1} A = ")
        form.scale(2)
        matrix = Matrix(np.identity(3, 'int'))
        matrix.set_column_colors(X_COLOR, Y_COLOR, Z_COLOR)
        matrix.next_to(form, RIGHT)
        self.add(form)
        self.play(Write(matrix))
        self.wait()

class ThreeDApplyReverseToV(Scene):
    pass

class InversesDontAlwaysExist(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("$A^{-1}$ doesn't always exist")
        self.random_blink()
        self.wait()
        self.random_blink()

class InvertNonInvertable(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[2, 1], [-2, -1]]
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        det_text = TexMobject("\\det(A) = 0")
        det_text.scale(1.5)
        det_text.to_corner(UP+LEFT)
        det_text.add_background_rectangle()
        self.add_foreground_mobject(det_text)

    def construct(self):
        no_func = TextMobject("No function does this")
        no_func.shift(2*UP)
        no_func.set_color(RED)
        no_func.add_background_rectangle()
        grid = VMobject(self.plane, self.i_hat, self.j_hat)
        grid.save_state()
        self.apply_transposed_matrix(self.t_matrix, path_arc = 0)
        self.wait()
        self.play(Write(no_func, run_time = 1))
        self.add_foreground_mobject(no_func)
        self.play(
            grid.restore,
            *list(map(Animation, self.foreground_mobjects)),
            run_time = 3
        )
        self.wait()

class OneInputMultipleOutputs(InvertNonInvertable):
    def construct(self):
        input_vectors = VMobject(*[
            Vector([x+2, x]) for x in np.arange(-4, 4.5, 0.5)
        ])
        input_vectors.set_submobject_colors_by_gradient(PINK, YELLOW)
        output_vector = Vector([4, 2], color = YELLOW)

        grid = VMobject(self.plane, self.i_hat, self.j_hat)
        grid.save_state()

        self.apply_transposed_matrix(self.t_matrix, path_arc = 0)
        self.play(ShowCreation(output_vector))
        single_input = TextMobject("Single vector")
        single_input.add_background_rectangle()
        single_input.next_to(output_vector.get_end(), UP)
        single_input.set_color(YELLOW) 
        self.play(Write(single_input))
        self.wait()
        self.remove(single_input, output_vector)
        self.play(
            grid.restore,
            *[
                Transform(output_vector.copy(), input_vector)
                for input_vector in input_vectors.split()
            ] + list(map(Animation, self.foreground_mobjects)),
            run_time = 3
        )
        multiple_outputs = TextMobject(
            "Must map to \\\\",
            "multiple vectors"
        )
        multiple_outputs.split()[1].set_submobject_colors_by_gradient(YELLOW, PINK)
        multiple_outputs.next_to(ORIGIN, DOWN).to_edge(RIGHT)
        multiple_outputs.add_background_rectangle()
        self.play(Write(multiple_outputs, run_time = 2))
        self.wait()

class SolutionsCanStillExist(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("""
            Solutions can still 
            exist when""",  "$\\det(A) = 0$"
        )
        words[1].set_color(TEAL)
        self.teacher_says(words)
        self.random_blink(2)

class ShowVInAndOutOfColumnSpace(LinearSystemTransformationScene):
    CONFIG = {
        "t_matrix" : [[2, 1], [-2, -1]]
    }
    def construct(self):
        v_out = Vector([1, -1])
        v_in = Vector([-4, -2])
        v_out.words = "No solution exists"
        v_in.words = "Solutions exist"
        v_in.words_color = YELLOW
        v_out.words_color = RED


        self.apply_transposed_matrix(self.t_matrix, path_arc = 0)
        self.wait()
        for v in v_in, v_out:
            self.add_vector(v, animate = True)
            words = TextMobject(v.words)
            words.set_color(v.words_color)
            words.next_to(v.get_end(), DOWN+RIGHT)
            words.add_background_rectangle()
            self.play(Write(words), run_time = 2)
        self.wait()

class NotAllSquishesAreCreatedEqual(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            Some squishes feel
            ...squishier
        """)
        self.random_blink(2)

class PrepareForRank(Scene):
    def construct(self):
        new_term, rank = words = TextMobject(
            "New terminology: ",
            "rank"
        )
        rank.set_color(TEAL)
        self.play(Write(words))
        self.wait()

class DefineRank(Scene):
    def construct(self):
        rank = TextMobject("``Rank''")
        rank.set_color(TEAL)
        arrow = DoubleArrow(LEFT, RIGHT)
        dims = TextMobject(
            "Number of\\\\", "dimensions \\\\", 
            "in the output"
        )
        dims[1].set_color(rank.get_color())

        rank.next_to(arrow, LEFT)
        dims.next_to(arrow, RIGHT)

        self.play(Write(rank))
        self.play(
            ShowCreation(arrow),
            *list(map(Write, dims))
        )
        self.wait()

class DefineColumnSpace(Scene):
    def construct(self):
        left_words = TextMobject(
            "Set of all possible\\\\",
            "outputs",
            "$A\\vec{\\textbf{v}}$",
        )
        left_words[1].set_color(TEAL)
        VMobject(*left_words[-1][1:]).set_color(YELLOW)
        arrow = DoubleArrow(LEFT, RIGHT).to_edge(UP)
        right_words = TextMobject("``Column space''", "of $A$")
        right_words[0].set_color(left_words[1].get_color())

        everyone = VMobject(left_words, arrow, right_words)
        everyone.arrange(RIGHT)
        everyone.to_edge(UP)

        self.play(Write(left_words))
        self.wait()
        self.play(
            ShowCreation(arrow),
            Write(right_words)
        )
        self.wait()

class ColumnsRepresentBasisVectors(Scene):
    def construct(self):
        matrix = Matrix([[3, 1], [4, 1]])
        matrix.shift(UP)
        i_hat_words, j_hat_words = [
            TextMobject("Where $\\hat{\\%smath}$ lands"%char)
            for char in ("i", "j")
        ]
        i_hat_words.set_color(X_COLOR)
        i_hat_words.next_to(ORIGIN, LEFT).to_edge(UP)
        j_hat_words.set_color(Y_COLOR)
        j_hat_words.next_to(ORIGIN, RIGHT).to_edge(UP)

        self.add(matrix)
        self.wait()
        for i, words in enumerate([i_hat_words, j_hat_words]):

            arrow = Arrow(
                words.get_bottom(),
                matrix.get_mob_matrix()[0,i].get_top(),
                color = words.get_color()
            )
            self.play(
                Write(words, run_time = 1),
                ShowCreation(arrow),
                *[
                    ApplyMethod(m.set_color, words.get_color())
                    for m in matrix.get_mob_matrix()[:,i]
                ]
            )
        self.wait()

class ThreeDOntoPlane(Scene):
    pass

class ThreeDOntoLine(Scene):
    pass

class ThreeDOntoPoint(Scene):
    pass

class TowDColumnsDontSpan(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[2, 1], [-2, -1]]
    }
    def construct(self):
        matrix = Matrix(self.t_matrix.T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.add_to_back(BackgroundRectangle(matrix))
        self.add_foreground_mobject(matrix)
        brace = Brace(matrix)
        words = VMobject(
            TextMobject("Span", "of columns"),
            TexMobject("\\Updownarrow"),
            TextMobject("``Column space''")
        )
        words.arrange(DOWN, buff = 0.1)
        words.next_to(brace, DOWN)
        words[0][0].set_color(PINK)
        words[2].set_color(TEAL)
        words[0].add_background_rectangle()
        words[2].add_background_rectangle()
        VMobject(matrix, brace, words).to_corner(UP+LEFT)

        self.apply_transposed_matrix(self.t_matrix, path_arc = 0)
        self.play(
            GrowFromCenter(brace),
            Write(words, run_time = 2)
        )
        self.wait()
        self.play(ApplyFunction(
            lambda m : m.scale(-1).shift(self.i_hat.get_end()),
            self.j_hat
        ))
        bases = [self.i_hat, self.j_hat]
        for mob in bases:
            mob.original = mob.copy()
        for x in range(8):
            for mob in bases:
                mob.target = mob.original.copy()
                mob.target.set_stroke(width = 6)
                target_len = random.uniform(0.5, 1.5)
                target_len *= random.choice([-1, 1])
                mob.target.scale(target_len)
            self.j_hat.target.shift(
                -self.j_hat.target.get_start()+ \
                self.i_hat.target.get_end()
            )
            self.play(Transform(
                VMobject(*bases),
                VMobject(*[m.target for m in bases]),
                run_time = 2
            ))

class FullRankWords(Scene):
    def construct(self):
        self.play(Write(TextMobject("Full rank").scale(2)))

class ThreeDColumnsDontSpan(Scene):
    def construct(self):
        matrix = Matrix(np.array([
            [1, 1, 0],
            [0, 1, 1],
            [-1, -2, -1],
        ]).T)
        matrix.set_column_colors(X_COLOR, Y_COLOR, Z_COLOR)
        brace = Brace(matrix)
        words = brace.get_text(
            "Columns don't",
            "span \\\\",
            "full output space"
        )
        words[1].set_color(PINK)

        self.add(matrix)
        self.play(
            GrowFromCenter(brace),
            Write(words, run_time = 2)
        )
        self.wait()

class NameColumnSpace(Scene):
    def construct(self):
        matrix = Matrix(np.array([
            [1, 1, 0],
            [0, 1, 1],
            [-1, -2, -1],
        ]).T)
        matrix.set_column_colors(X_COLOR, Y_COLOR, Z_COLOR)
        matrix.to_corner(UP+LEFT)
        cols = list(matrix.copy().get_mob_matrix().T)
        col_arrays = list(map(Matrix, cols))

        span_text = TexMobject(
            "\\text{Span}", 
            "\\Big(",
            matrix_to_tex_string([1, 2, 3]),
            ",",
            matrix_to_tex_string([1, 2, 3]),
            ",",
            matrix_to_tex_string([1, 2, 3]),
            "\\big)"
        )
        for i in 1, -1:
            span_text[i].stretch(1.5, 1)
            span_text[i].do_in_place(
                span_text[i].set_height, 
                span_text.get_height()
            )
        for col_array, index in zip(col_arrays, [2, 4, 6]):
            col_array.replace(span_text[index], dim_to_match = 1)
            span_text.submobjects[index] = col_array
        span_text.arrange(RIGHT, buff = 0.2)

        arrow = DoubleArrow(LEFT, RIGHT)
        column_space = TextMobject("``Column space''")
        for mob in column_space, arrow:
            mob.set_color(TEAL)
        text = VMobject(span_text, arrow, column_space)
        text.arrange(RIGHT)
        text.next_to(matrix, DOWN, buff = 1, aligned_edge = LEFT)

        self.add(matrix)
        self.wait()
        self.play(*[
            Transform(
                VMobject(*matrix.copy().get_mob_matrix()[:,i]),
                col_arrays[i].get_entries()
            )
            for i in range(3)
        ])
        self.play(
            Write(span_text),
            *list(map(Animation, self.get_mobjects_from_last_animation()))
        )
        self.play(
            ShowCreation(arrow),
            Write(column_space)
        )
        self.wait()
        self.play(FadeOut(matrix))
        self.clear()
        self.add(text)

        words = TextMobject(
            "To solve", 
            "$A\\vec{\\textbf{x}} = \\vec{\\textbf{v}}$,\\\\",
            "$\\vec{\\textbf{v}}$", 
            "must be in \\\\ the",
            "column space."
        )
        VMobject(*words[1][1:3]).set_color(PINK)
        VMobject(*words[1][4:6]).set_color(YELLOW)
        words[2].set_color(YELLOW)
        words[4].set_color(TEAL)
        words.to_corner(UP+LEFT)

        self.play(Write(words))
        self.wait(2)
        self.play(FadeOut(words))

        brace = Brace(column_space, UP)
        rank_words = brace.get_text(
            "Number of dimensions \\\\ is called",
            "``rank''"
        )
        rank_words[1].set_color(MAROON)
        self.play(
            GrowFromCenter(brace),
            Write(rank_words)
        )
        self.wait()
        self.cycle_through_span_possibilities(span_text)

    def cycle_through_span_possibilities(self, span_text):
        span_text.save_state()
        two_d_span = span_text.copy()
        for index, arr, c in (2, [1, 1], X_COLOR), (4, [0, 1], Y_COLOR):
            col = Matrix(arr)
            col.replace(two_d_span[index])
            two_d_span.submobjects[index] = col
            col.get_entries().set_color(c)
        for index in 5, 6:
            two_d_span[index].scale(0)
        two_d_span.arrange(RIGHT, buff = 0.2)
        two_d_span[-1].next_to(two_d_span[4], RIGHT, buff = 0.2)
        two_d_span.move_to(span_text, aligned_edge = RIGHT)
        mob_matrix = np.array([
            two_d_span[i].get_entries().split()
            for i in (2, 4)
        ])

        self.play(Transform(span_text, two_d_span))
        #horrible hack
        span_text.shift(10*DOWN)
        span_text = span_text.copy().restore()
        ###
        self.add(two_d_span)
        self.wait()
        self.replace_number_matrix(mob_matrix, [[1, 1], [1, 1]])
        self.wait()
        self.replace_number_matrix(mob_matrix, [[0, 0], [0, 0]])
        self.wait()
        self.play(Transform(two_d_span, span_text))
        self.wait()
        self.remove(two_d_span)
        self.add(span_text)
        mob_matrix = np.array([
            span_text[i].get_entries().split()
            for i in (2, 4, 6)
        ])
        self.replace_number_matrix(mob_matrix, [[1, 1, 0], [0, 1, 1], [1, 0, 1]])
        self.wait()
        self.replace_number_matrix(mob_matrix, [[1, 1, 0], [0, 1, 1], [-1, -2, -1]])
        self.wait()
        self.replace_number_matrix(mob_matrix, [[1, 1, 0], [2, 2, 0], [3, 3, 0]])
        self.wait()
        self.replace_number_matrix(mob_matrix, np.zeros((3, 3)).astype('int'))
        self.wait()


    def replace_number_matrix(self, matrix, new_numbers):
        starters = matrix.flatten()
        targets = list(map(TexMobject, list(map(str, np.array(new_numbers).flatten()))))
        for start, target in zip(starters, targets):
            target.move_to(start)
            target.set_color(start.get_color())
        self.play(*[
            Transform(*pair, path_arc = np.pi)
            for pair in zip(starters, targets)
        ])

class IHatShear(LinearTransformationScene):
    CONFIG = {
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "secondary_line_ratio" : 0
        },
    }
    def construct(self):
        self.apply_transposed_matrix([[1, 1], [0, 1]])
        self.wait()

class DiagonalDegenerate(LinearTransformationScene):
    def construct(self):
        self.apply_transposed_matrix([[1, 1], [1, 1]])

class ZeroMatirx(LinearTransformationScene):
    def construct(self):
        origin = Dot(ORIGIN)
        self.play(Transform(
            VMobject(self.plane, self.i_hat, self.j_hat),
            origin,
            run_time = 3
        ))
        self.wait()

class RankNumber(Scene):
    CONFIG = {
        "number" : 3,
        "color" : BLUE
    }
    def construct(self):
        words = TextMobject("Rank", "%d"%self.number)
        words[1].set_color(self.color)
        self.add(words)

class RankNumber2(RankNumber):
    CONFIG = {
        "number" : 2,
        "color" : RED,
    }

class RankNumber1(RankNumber):
    CONFIG = {
        "number" : 1,
        "color" : GREEN
    }

class RankNumber0(RankNumber):
    CONFIG = {
        "number" : 0,
        "color" : GREY
    }  

class NameFullRank(Scene):
    def construct(self):
        matrix = Matrix([[2, 5, 1], [3, 1, 4], [-4, 0, 0]])
        matrix.set_column_colors(X_COLOR, Y_COLOR, Z_COLOR)
        matrix.to_edge(UP)
        brace = Brace(matrix)
        top_words = brace.get_text(
            "When", "rank", "$=$", "number of columns",
        )
        top_words[1].set_color(MAROON)
        low_words = TextMobject(
            "matrix is", "``full rank''"
        )
        low_words[1].set_color(MAROON)
        low_words.next_to(top_words, DOWN)
        VMobject(matrix, brace, top_words, low_words).to_corner(UP+LEFT)
        self.add(matrix)
        self.play(
            GrowFromCenter(brace),
            Write(top_words)
        )
        self.wait()
        self.play(Write(low_words))
        self.wait()

class OriginIsAlwaysInColumnSpace(LinearTransformationScene):
    def construct(self):
        vector = Matrix([0, 0]).set_color(YELLOW)
        words = TextMobject("is always in the", "column space")
        words[1].set_color(TEAL)
        words.next_to(vector, RIGHT)
        vector.add_to_back(BackgroundRectangle(vector))
        words.add_background_rectangle()
        VMobject(vector, words).center().to_edge(UP)
        arrow = Arrow(vector.get_bottom(), ORIGIN)
        dot = Dot(ORIGIN, color = YELLOW)

        self.play(Write(vector), Write(words))
        self.play(ShowCreation(arrow))
        self.play(ShowCreation(dot, run_time = 0.5))
        self.add_foreground_mobject(vector, words, arrow, dot)
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()
        self.apply_transposed_matrix([[1./3, -1./2], [-1./3, 1./2]])
        self.wait()

class FullRankCase(LinearTransformationScene):
    CONFIG = {
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "secondary_line_ratio" : 0
        },
    }
    def construct(self):
        t_matrices = [
            [[2, 1], [-3, 2]],
            [[1./2, 1], [1./3, -1./2]]
        ]
        vector = Matrix([0, 0]).set_color(YELLOW)
        title = VMobject(
            TextMobject("Only"), vector,
            TextMobject("lands on"), vector.copy()
        )
        title.arrange(buff = 0.2)
        title.to_edge(UP)
        for mob in title:
            mob.add_to_back(BackgroundRectangle(mob))
        arrow = Arrow(vector.get_bottom(), ORIGIN)
        dot = Dot(ORIGIN, color = YELLOW) 

        words_on = False
        for t_matrix in t_matrices:
            self.apply_transposed_matrix(t_matrix)
            if not words_on:
                self.play(Write(title))
                self.play(ShowCreation(arrow))
                self.play(ShowCreation(dot, run_time = 0.5))
                self.add_foreground_mobject(title, arrow, dot)
                words_on = True
            self.apply_inverse_transpose(t_matrix)
            self.wait()

class NameNullSpace(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "t_matrix" : [[1, -1], [-1, 1]]
    }
    def construct(self):
        vectors = self.get_vectors()
        dot = Dot(ORIGIN, color = YELLOW)
        line = Line(vectors[0].get_end(), vectors[-1].get_end())
        line.set_color(YELLOW)
        null_space_label = TextMobject("``Null space''")
        kernel_label = TextMobject("``Kernel''")
        null_space_label.move_to(vectors[13].get_end(), aligned_edge = UP+LEFT)
        kernel_label.next_to(null_space_label, DOWN)
        for mob in null_space_label, kernel_label:
            mob.set_color(YELLOW)
            mob.add_background_rectangle()

        self.play(ShowCreation(vectors, run_time = 3))
        self.wait()
        vectors.save_state()
        self.plane.save_state()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [Transform(vectors, dot)],
            path_arc = 0
        )
        self.wait()
        self.play(
            vectors.restore, 
            self.plane.restore, 
            *list(map(Animation, self.foreground_mobjects)),
            run_time = 2
        )
        self.play(Transform(
            vectors, line, 
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait()
        for label in null_space_label, kernel_label:
            self.play(Write(label))
            self.wait()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [
                Transform(vectors, dot),
                ApplyMethod(null_space_label.scale, 0),
                ApplyMethod(kernel_label.scale, 0),
            ],
            path_arc = 0
        )
        self.wait()

    def get_vectors(self, offset = 0):
        vect = np.array(UP+RIGHT)
        vectors = VMobject(*[
            Vector(a*vect + offset)
            for a in np.linspace(-5, 5, 18)
        ])
        vectors.set_submobject_colors_by_gradient(PINK, YELLOW)
        return vectors

class ThreeDNullSpaceIsLine(Scene):
    pass

class ThreeDNullSpaceIsPlane(Scene):
    pass

class NullSpaceSolveForVEqualsZero(NameNullSpace):
    def construct(self):
        vec = lambda s : "\\vec{\\textbf{%s}}"%s
        equation = TexMobject("A", vec("x"), "=", vec("v"))
        A, x, eq, v = equation
        x.set_color(PINK)
        v.set_color(YELLOW)
        zero_vector = Matrix([0, 0])
        zero_vector.set_color(YELLOW)
        zero_vector.scale(0.7)
        zero_vector.move_to(v, aligned_edge = LEFT)
        VMobject(equation, zero_vector).next_to(ORIGIN, LEFT).to_edge(UP)
        zero_vector_rect = BackgroundRectangle(zero_vector)        
        equation.add_background_rectangle()

        self.play(Write(equation))
        self.wait()
        self.play(
            ShowCreation(zero_vector_rect),
            Transform(v, zero_vector)
        )
        self.wait()
        self.add_foreground_mobject(zero_vector_rect, equation)
        NameNullSpace.construct(self)

class OffsetNullSpace(NameNullSpace):
    def construct(self):
        x = Vector([-2, 1], color = RED)
        vectors = self.get_vectors()
        offset_vectors = self.get_vectors(offset = x.get_end())
        dots = VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in offset_vectors
        ])
        dot = Dot(
            self.get_matrix_transformation(self.t_matrix)(x.get_end()),
            color = RED
        )
        circle = Circle(color = YELLOW).replace(dot)
        circle.scale_in_place(5)
        words = TextMobject("""
            All vectors still land 
            on the same spot
        """)
        words.set_color(YELLOW)
        words.add_background_rectangle()
        words.next_to(circle)
        x_copies = VMobject(*[
            x.copy().shift(v.get_end())
            for v in vectors
        ])

        self.play(FadeIn(vectors))
        self.wait()
        self.add_vector(x, animate = True)
        self.wait()
        x_copy = VMobject(x.copy())
        self.play(Transform(x_copy, x_copies))
        self.play(
            Transform(vectors, offset_vectors),
            *[
                Transform(v, VectorizedPoint(v.get_end()))
                for v in x_copy
            ]
        )
        self.remove(x_copy)
        self.wait()
        self.play(Transform(vectors, dots))
        self.wait()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [Transform(vectors, dot)]
        )
        self.wait()        
        self.play(
            ShowCreation(circle),
            Write(words)
        )
        self.wait()

class ShowAdditivityProperty(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "t_matrix" : [[1, 0.5], [-1, 1]],
        "include_background_plane" : False,
    }
    def construct(self):
        v = Vector([2, -1])
        w = Vector([1, 2])
        v.set_color(YELLOW)
        w.set_color(MAROON_B)
        sum_vect = Vector(v.get_end()+w.get_end(), color = PINK)
        form = TexMobject(
            "A(",
            "\\vec{\\textbf{v}}",
            "+",
            "\\vec{\\textbf{w}}",
            ")",
            "=A",
            "\\vec{\\textbf{v}}",
            "+A",
            "\\vec{\\textbf{w}}",
        )
        form.to_corner(UP+RIGHT)
        VMobject(form[1], form[6]).set_color(YELLOW)
        VMobject(form[3], form[8]).set_color(MAROON_B)
        initial_sum = VMobject(*form[1:4])
        transformer = VMobject(form[0], form[4])
        final_sum = VMobject(*form[5:])
        form_rect = BackgroundRectangle(form)

        self.add(form_rect)
        self.add_vector(v, animate = True)
        self.add_vector(w, animate = True)
        w_copy = w.copy()
        self.play(w_copy.shift, v.get_end())
        self.add_vector(sum_vect, animate = True)
        self.play(
            Write(initial_sum),
            FadeOut(w_copy)
        )
        self.add_foreground_mobject(form_rect, initial_sum)
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [Write(transformer)]
        )
        self.wait()
        self.play(w.copy().shift, v.get_end())
        self.play(Write(final_sum))
        self.wait()

class AddJustOneNullSpaceVector(NameNullSpace):
    def construct(self):
        vectors = self.get_vectors()
        self.add(vectors)
        null_vector = vectors[int(0.7*len(vectors.split()))]
        vectors.remove(null_vector)
        null_vector.label = "$\\vec{\\textbf{n}}$"
        x = Vector([-1, 1], color = RED)
        x.label = "$\\vec{\\textbf{x}}$"
        sum_vect = Vector(
            x.get_end() + null_vector.get_end(),
            color = PINK
        )
        for v in x, null_vector:
            v.label = TextMobject(v.label)
            v.label.set_color(v.get_color())
            v.label.next_to(v.get_end(), UP)
            v.label.add_background_rectangle()
        dot = Dot(ORIGIN, color = null_vector.get_color())

        form = TexMobject(
            "A(",
            "\\vec{\\textbf{x}}",
            "+",
            "\\vec{\\textbf{n}}",
            ")",
            "=A",
            "\\vec{\\textbf{x}}",
            "+A",
            "\\vec{\\textbf{n}}",
        )
        form.to_corner(UP+RIGHT)
        VMobject(form[1], form[6]).set_color(x.get_color())
        VMobject(form[3], form[8]).set_color(null_vector.get_color())
        initial_sum = VMobject(*form[1:4])
        transformer = VMobject(form[0], form[4])
        final_sum = VMobject(*form[5:])
        brace = Brace(VMobject(*form[-2:]))
        brace.add(brace.get_text("+0").add_background_rectangle())
        form_rect = BackgroundRectangle(form)
        sum_vect.label = initial_sum.copy()
        sum_vect.label.next_to(sum_vect.get_end(), UP)

        self.add_vector(x, animate = True)
        self.play(Write(x.label))
        self.wait()
        self.play(
            FadeOut(vectors),
            Animation(null_vector)
        )
        self.play(Write(null_vector.label))
        self.wait()
        x_copy = x.copy()
        self.play(x_copy.shift, null_vector.get_end())
        self.add_vector(sum_vect, animate = True)
        self.play(
            FadeOut(x_copy),
            Write(sum_vect.label)
        )
        self.wait()
        self.play(
            ShowCreation(form_rect),
            sum_vect.label.replace, initial_sum
        )
        self.add_foreground_mobject(form_rect, sum_vect.label)
        self.remove(x.label, null_vector.label)
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [
                Transform(null_vector, dot),
                Write(transformer)
            ]
        )
        self.play(Write(final_sum))
        self.wait()
        self.play(Write(brace))
        self.wait()
        words = TextMobject(
            "$\\vec{\\textbf{x}}$",
            "and the",
            "$\\vec{\\textbf{x}} + \\vec{\\textbf{n}}$\\\\",
            "land on the same spot"
        )
        words[0].set_color(x.get_color())
        VMobject(*words[2][:2]).set_color(x.get_color())
        VMobject(*words[2][3:]).set_color(null_vector.get_color())
        words.next_to(brace, DOWN)
        words.to_edge(RIGHT)
        self.play(Write(words))
        self.wait()

class NullSpaceOffsetRule(Scene):
    def construct(self):
        vec = lambda s : "\\vec{\\textbf{%s}}"%s
        equation = TexMobject("A", vec("x"), "=", vec("v"))
        A, x, equals, v = equation
        x.set_color(PINK)
        v.set_color(YELLOW)
        A_text = TextMobject(
            "When $A$ is not", "full rank"
        )
        A_text[1].set_color(MAROON_C)
        A_text.next_to(A, UP+LEFT, buff = 1)
        A_text.shift_onto_screen()
        A_arrow = Arrow(A_text.get_bottom(), A, color = WHITE)
        v_text = TextMobject(
            "If", "$%s$"%vec("v"), "is in the", 
            "column space", "of $A$"
        )
        v_text[1].set_color(YELLOW)
        v_text[3].set_color(TEAL)
        v_text.next_to(v, DOWN+RIGHT, buff = 1)
        v_text.shift_onto_screen()
        v_arrow = Arrow(v_text.get_top(), v, color = YELLOW)


        self.add(equation)
        self.play(Write(A_text, run_time = 2))
        self.play(ShowCreation(A_arrow))
        self.wait()
        self.play(Write(v_text, run_time = 2))
        self.play(ShowCreation(v_arrow))
        self.wait()

class MuchLeftToLearn(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "That's the high \\\\",
            "level overview"
        )
        self.random_blink()
        self.wait()
        self.teacher_says(
            "There is still \\\\",
            "much to learn"
        )
        for pi in self.get_students():
            target_mode = random.choice([
                "raise_right_hand", "raise_left_hand"
            ])
            self.play(pi.change_mode, target_mode)
        self.random_blink()
        self.wait()

class NotToLearnItAllNow(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            The goal is not to
            learn it all now
        """)
        self.random_blink()
        self.wait()
        self.random_blink()

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: Nonsquare matrices
        """)
        title.set_width(FRAME_WIDTH - 2)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()  

class WhatAboutNonsquareMatrices(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What about \\\\ nonsquare matrices?",
            target_mode = "raise_right_hand"
        )
        self.play(self.get_students()[0].change_mode, "confused")
        self.random_blink(6)

















