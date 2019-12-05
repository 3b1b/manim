from manimlib.imports import *
from old_projects.eola.chapter5 import get_det_text, RightHandRule


U_COLOR = ORANGE
V_COLOR = YELLOW
W_COLOR = MAROON_B
P_COLOR = RED

def get_vect_tex(*strings):
    result = ["\\vec{\\textbf{%s}}"%s for s in strings]
    if len(result) == 1:
        return result[0]
    else:
        return result

def get_perm_sign(*permutation):
    identity = np.identity(len(permutation))
    return np.linalg.det(identity[list(permutation)])

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject("``Every dimension is special.''")
        words.to_edge(UP)
        author = TextMobject("-Jeff Lagarias")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(1)
        self.play(Write(author, run_time = 3))
        self.wait()

class LastVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Last video: Dot products and duality
        """)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()  

class DoTheSameForCross(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Let's do the same \\\\ for", "cross products")
        words.set_color_by_tex("cross products", YELLOW)
        self.teacher_says(words, target_mode = "surprised")
        self.random_blink(2)
        self.change_student_modes("pondering")
        self.random_blink()

class ListSteps(Scene):
    CONFIG = {
        "randy_corner" : DOWN+RIGHT
    }
    def construct(self):
        title = TextMobject("Two part chapter")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)
        randy = Randolph().flip().to_corner(DOWN+RIGHT)
        randy.look(UP+LEFT)

        step_1 = TextMobject("This video: Standard introduction")
        step_2 = TextMobject("Next video: Deeper understanding with ", "linear transformations")
        step_2.set_color_by_tex("linear transformations", BLUE)
        steps = VGroup(step_1, step_2)
        steps.arrange(DOWN, aligned_edge = LEFT, buff = LARGE_BUFF)
        steps.next_to(randy, UP)
        steps.to_edge(LEFT, buff = LARGE_BUFF)

        self.add(title)
        self.play(ShowCreation(h_line))
        for step in steps:
            self.play(Write(step))
            self.wait()
        for step in steps:
            target = step.copy()
            target.scale_in_place(1.1)
            target.set_color(YELLOW)
            target.set_color_by_tex("linear transformations", BLUE)
            step.target = target
            step.save_state()
        self.play(FadeIn(randy))
        self.play(Blink(randy))
        self.play(
            MoveToTarget(step_1),
            step_2.fade,
            randy.change_mode, "happy"
        )
        self.play(Blink(randy))
        self.play(
            Transform(step_1, step_1.copy().restore().fade()),
            MoveToTarget(step_2),
            randy.look, LEFT
        )
        self.play(randy.change_mode, "erm")
        self.wait(2)
        self.play(randy.change_mode, "pondering")
        self.play(Blink(randy))

class SimpleDefine2dCrossProduct(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "v_coords" : [3, 2],
        "w_coords" : [2, -1],
    }
    def construct(self):
        self.add_vectors()
        self.show_area()
        self.write_area_words()        
        self.show_sign()
        self.swap_v_and_w()

    def add_vectors(self):
        self.plane.fade()
        v = self.add_vector(self.v_coords, color = V_COLOR)
        w = self.add_vector(self.w_coords, color = W_COLOR)
        for vect, name, direction in (v, "v", "left"), (w, "w", "right"):
            color = vect.get_color()
            vect.label = self.label_vector(
                vect, name, color = color, direction = direction,
            )
        self.v, self.w = v, w

    def show_area(self):
        self.add_unit_square()
        transform = self.get_matrix_transformation(np.array([
            self.v_coords, 
            self.w_coords,
        ]))
        self.square.apply_function(transform)
        self.play(
            ShowCreation(self.square),
            *list(map(Animation, [self.v, self.w]))
        )
        self.wait()
        self.play(FadeOut(self.square))
        v_copy = self.v.copy()
        w_copy = self.w.copy()
        self.play(v_copy.shift, self.w.get_end())
        self.play(w_copy.shift, self.v.get_end())
        self.wait()
        self.play(
            FadeIn(self.square),
            *list(map(Animation, [self.v, self.w, v_copy, w_copy]))
        )
        self.wait()
        self.play(*list(map(FadeOut, [v_copy, w_copy])))

    def write_area_words(self):
        times = TexMobject("\\times")
        for vect in self.v, self.w:
            vect.label.target = vect.label.copy()
            vect.label.target.save_state()
        cross = VGroup(self.v.label.target, times, self.w.label.target)
        cross.arrange(aligned_edge = DOWN)
        cross.scale(1.5)        
        cross.shift(2.5*UP).to_edge(LEFT)
        cross_rect = BackgroundRectangle(cross)
        equals = TexMobject("=")
        equals.add_background_rectangle()
        equals.next_to(cross, buff = MED_SMALL_BUFF/2)
        words = TextMobject("Area of parallelogram")
        words.add_background_rectangle()
        words.next_to(equals, buff = MED_SMALL_BUFF/2)
        arrow = Arrow(
            words.get_bottom(), 
            self.square.get_center(),
            color = WHITE
        )

        self.play(
            FadeIn(cross_rect),            
            Write(times),
            *[
                ApplyMethod(
                    vect.label.target.restore, 
                    rate_func = lambda t : smooth(1-t)
                )
                for vect in (self.v, self.w)
            ]
        )
        self.wait()
        self.play(ApplyFunction(
            lambda m : m.scale_in_place(1.2).set_color(RED),
            times,
            rate_func = there_and_back
        ))
        self.wait()
        self.play(Write(words), Write(equals))
        self.play(ShowCreation(arrow))
        self.wait()
        self.play(FadeOut(arrow))

        self.area_words = words
        self.cross = cross

    def show_sign(self):        
        for vect, angle in (self.v, -np.pi/2), (self.w, np.pi/2):
            vect.add(vect.label)
            vect.save_state()
            vect.target = vect.copy()
            vect.target.rotate(angle)
            vect.target.label.rotate_in_place(-angle)
            vect.target.label.background_rectangle.set_fill(opacity = 0)
        square = self.square
        square.save_state()
        self.add_unit_square(animate = False, opacity = 0.15)
        transform = self.get_matrix_transformation([
            self.v.target.get_end()[:2],
            self.w.target.get_end()[:2],
        ])
        self.square.apply_function(transform)
        self.remove(self.square)
        square.target = self.square
        self.square = square

        positive = TextMobject("Positive").set_color(GREEN)
        negative = TextMobject("Negative").set_color(RED)
        for word in positive, negative:
            word.add_background_rectangle()
            word.arrow = Arrow(
                word.get_top(), word.get_top() + 1.5*UP,
                color = word.get_color()
            )
            VGroup(word, word.arrow).next_to(
                self.area_words, DOWN, 
                aligned_edge = LEFT, 
                buff = SMALL_BUFF
            )
        minus_sign = TexMobject("-")
        minus_sign.set_color(RED)
        minus_sign.move_to(self.area_words, aligned_edge = LEFT)
        self.area_words.target = self.area_words.copy()
        self.area_words.target.next_to(minus_sign, RIGHT)

        self.play(*list(map(MoveToTarget, [square, self.v, self.w])))
        arc = self.get_arc(self.v, self.w, radius = 1.5)
        arc.set_color(GREEN)
        self.play(ShowCreation(arc))
        self.wait()
        self.play(Write(positive), ShowCreation(positive.arrow))
        self.remove(arc)
        self.play(
            FadeOut(positive), 
            FadeOut(positive.arrow),
            *[mob.restore for mob in (square, self.v, self.w)]
        )
        arc = self.get_arc(self.v, self.w, radius = 1.5)
        arc.set_color(RED)
        self.play(ShowCreation(arc))
        self.play(
            Write(negative),
            ShowCreation(negative.arrow),
            Write(minus_sign),
            MoveToTarget(self.area_words)
        )
        self.wait()
        self.play(*list(map(FadeOut, [negative, negative.arrow, arc])))

    def swap_v_and_w(self):
        new_cross = self.cross.copy()
        new_cross.arrange(LEFT, aligned_edge = DOWN)
        new_cross.move_to(self.area_words, aligned_edge = LEFT)
        for vect in self.v, self.w:
            vect.remove(vect.label)

        self.play(
            FadeOut(self.area_words),
            Transform(self.cross.copy(), new_cross, path_arc = np.pi/2)
        )
        self.wait()

        curr_matrix = np.array([self.v.get_end()[:2], self.w.get_end()[:2]])
        new_matrix = np.array(list(reversed(curr_matrix)))
        transform = self.get_matrix_transformation(
            np.dot(new_matrix.T, np.linalg.inv(curr_matrix.T)).T
        )
        self.square.target = self.square.copy().apply_function(transform)
        self.play(
            MoveToTarget(self.square),            
            Transform(self.v, self.w),
            Transform(self.w, self.v),
            rate_func = there_and_back,
            run_time = 3
        )
        self.wait()


    def get_arc(self, v, w, radius = 2):
        v_angle, w_angle = v.get_angle(), w.get_angle()
        nudge = 0.05
        arc = Arc(
            (1-2*nudge)*(w_angle - v_angle),
            start_angle = interpolate(v_angle, w_angle, nudge),
            radius = radius,
            stroke_width = 8,
        )
        arc.add_tip()
        return arc

class CrossBasisVectors(LinearTransformationScene):
    def construct(self):
        self.plane.fade()
        i_label = self.get_vector_label(
            self.i_hat, "\\hat{\\imath}",
            direction = "right",
            color = X_COLOR,
        )
        j_label = self.get_vector_label(
            self.j_hat, "\\hat{\\jmath}",
            direction = "left",
            color = Y_COLOR,
        )
        for label in i_label, j_label:
            self.play(Write(label))
            label.target = label.copy()
        i_label.target.scale(1.5)
        j_label.target.scale(1.2)

        self.wait()

        times = TexMobject("\\times")
        cross = VGroup(i_label.target, times, j_label.target)
        cross.arrange()
        cross.next_to(ORIGIN).shift(1.5*UP)
        cross_rect = BackgroundRectangle(cross)
        eq = TexMobject("= + 1")
        eq.add_background_rectangle()
        eq.next_to(cross, RIGHT)

        self.play(
            ShowCreation(cross_rect),            
            MoveToTarget(i_label.copy()),
            MoveToTarget(j_label.copy()),
            Write(times),
        )
        self.play(Write(eq))
        self.wait()
        arc = self.get_arc(self.i_hat, self.j_hat, radius = 1)
        # arc.set_color(GREEN)
        self.play(ShowCreation(arc))
        self.wait()


    def get_arc(self, v, w, radius = 2):
        v_angle, w_angle = v.get_angle(), w.get_angle()
        nudge = 0.05
        arc = Arc(
            (1-2*nudge)*(w_angle - v_angle),
            start_angle = interpolate(v_angle, w_angle, nudge),
            radius = radius,
            stroke_width = 8,
        )
        arc.add_tip()
        return arc

class VisualExample(SimpleDefine2dCrossProduct):
    CONFIG = {
        "show_basis_vectors" : False,
        "v_coords" : [3, 1],
        "w_coords" : [1, -2],
    }
    def construct(self):
        self.add_vectors()
        # self.show_coords()
        self.show_area()
        self.write_area_words()

        result = np.linalg.det([self.v_coords, self.w_coords])
        val = TexMobject(str(int(abs(result)))).scale(2)
        val.move_to(self.square.get_center())
        arc = self.get_arc(self.v, self.w, radius = 1)
        arc.set_color(RED)
        minus = TexMobject("-").set_color(RED)
        minus.scale(1.5)
        minus.move_to(self.area_words, aligned_edge = LEFT)

        self.play(ShowCreation(val))
        self.wait()
        self.play(ShowCreation(arc))
        self.wait()
        self.play(FadeOut(self.area_words))
        self.play(
            Transform(arc, minus),
            val.next_to, minus, RIGHT
        )
        self.wait()

    def show_coords(self):
        for vect, edge in (self.v, DOWN), (self.w, UP):        
            color = vect.get_color()
            vect.coord_array = vector_coordinate_label(
                vect, color = color,
            )
            vect.coord_array.move_to(
                vect.coord_array.get_center(), 
                aligned_edge = edge
            )
            self.play(Write(vect.coord_array, run_time = 1))

class HowDoYouCompute(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "How do you \\\\ compute this?",
            target_mode = "raise_left_hand"
        )
        self.random_blink(2)

class ContrastDotAndCross(Scene):
    def construct(self):
        self.add_t_chart()
        self.add_dot_products()
        self.add_cross_product()
        self.add_2d_cross_product()
        self.emphasize_output_type()

    def add_t_chart(self):
        for word, vect, color in ("Dot", LEFT, BLUE_C), ("Cross", RIGHT, YELLOW):
            title = TextMobject("%s product"%word)
            title.shift(vect*FRAME_X_RADIUS/2)
            title.to_edge(UP)
            title.set_color(color)
            self.add(title)
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        l_h_line = Line(LEFT, ORIGIN).scale(FRAME_X_RADIUS)
        r_h_line = Line(ORIGIN, RIGHT).scale(FRAME_X_RADIUS)
        r_h_line.next_to(title, DOWN)
        l_h_line.next_to(r_h_line, LEFT, buff = 0)
        self.add(v_line, l_h_line, r_h_line)
        self.l_h_line, self.r_h_line = l_h_line, r_h_line

    def add_dot_products(self, max_width = FRAME_X_RADIUS-1, dims = [2, 5]):
        colors = [X_COLOR, Y_COLOR, Z_COLOR, MAROON_B, TEAL]
        last_mob = self.l_h_line
        dot_products = []
        for dim in dims:
            arrays = [
                [random.randint(0, 9) for in_count in range(dim)]
                for out_count in range(2)
            ]
            m1, m2 = list(map(Matrix, arrays))
            for matrix in m1, m2:
                for entry, color in zip(matrix.get_entries(), colors):
                    entry.set_color(color)
                    entry.target = entry.copy()
            syms = VGroup(*list(map(TexMobject, ["="] + ["+"]*(dim-1))))
            def get_dot():
                dot = TexMobject("\\cdot")
                syms.add(dot)
                return dot
            result = VGroup(*it.chain(*list(zip(
                syms,
                [
                    VGroup(
                        e1.target, get_dot(), e2.target
                    ).arrange()
                    for e1, e2 in zip(m1.get_entries(), m2.get_entries())
                ]
            ))))
            result.arrange(RIGHT)
            dot_prod = VGroup(
                m1, TexMobject("\\cdot"), m2, result
            )
            dot_prod.arrange(RIGHT)
            if dot_prod.get_width() > max_width:
                dot_prod.set_width(max_width)
            dot_prod.next_to(last_mob, DOWN, buff = MED_SMALL_BUFF)
            last_mob = dot_prod
            dot_prod.to_edge(LEFT)
            dot_prod.remove(result)
            dot_prod.syms = syms
            dot_prod.entries = list(m1.get_entries())+list(m2.get_entries())
            dot_products.append(dot_prod)
        self.add(*dot_products)
        for dot_prod in dot_products:
            self.play(
                Write(dot_prod.syms),
                *[
                    Transform(
                        e.copy(), e.target, 
                        path_arc = -np.pi/6
                    )
                    for e in dot_prod.entries
                ],
                run_time = 2
            )
        self.wait()

    def add_cross_product(self):
        colors = [X_COLOR, Y_COLOR, Z_COLOR]

        arrays = [
            [random.randint(0, 9) for in_count in range(3)]
            for out_count in range(2)
        ]
        matrices = list(map(Matrix, arrays))
        for matrix in matrices:
            for entry, color in zip(matrix.get_entries(), colors):
                entry.set_color(color)
        m1, m2 = matrices
        cross_product = VGroup(m1, TexMobject("\\times"), m2)
        cross_product.arrange()

        index_to_cross_enty = {}
        syms = VGroup()
        movement_sets = []
        for a, b, c in it.permutations(list(range(3))):
            e1, e2 = m1.get_entries()[b], m2.get_entries()[c]
            for e in e1, e2:
                e.target = e.copy()
            movement_sets.append([e1, e1.target, e2, e2.target])
            dot = TexMobject("\\cdot")
            syms.add(dot)
            cross_entry = VGroup(e1.target, dot, e2.target)
            cross_entry.arrange()
            if a not in index_to_cross_enty:
                index_to_cross_enty[a] = []
            index_to_cross_enty[a].append(cross_entry)
        result_entries = []
        for a in range(3):
            prod1, prod2 = index_to_cross_enty[a]
            if a == 1:
                prod1, prod2 = prod2, prod1
            prod2.arrange(LEFT)
            minus = TexMobject("-")
            syms.add(minus)
            entry = VGroup(prod1, minus, prod2)
            entry.arrange(RIGHT)
            result_entries.append(entry)

        result = Matrix(result_entries)
        full_cross_product = VGroup(
            cross_product, TexMobject("="), result
        )
        full_cross_product.arrange()
        full_cross_product.scale(0.75)
        full_cross_product.next_to(self.r_h_line, DOWN, buff = MED_SMALL_BUFF/2)
        full_cross_product.remove(result)
        self.play(
            Write(full_cross_product),
        )
        movements = []
        for e1, e1_target, e2, e2_target in movement_sets:
            movements += [
                e1.copy().move_to, e1_target,
                e2.copy().move_to, e2_target,
            ]

        brace = Brace(cross_product)
        brace_text = brace.get_text("Only 3d")
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )

        self.play(
            Write(result.get_brackets()),
            Write(syms),
            *movements,
            run_time = 2
        )
        self.wait()

        self.cross_result = result
        self.only_3d_text = brace_text

    def add_2d_cross_product(self):
        h_line = DashedLine(ORIGIN, FRAME_X_RADIUS*RIGHT)
        h_line.next_to(self.only_3d_text, DOWN, buff = MED_SMALL_BUFF/2)
        h_line.to_edge(RIGHT, buff = 0)
        arrays = np.random.randint(0, 9, (2, 2))
        m1, m2 = matrices = list(map(Matrix, arrays))
        for m in matrices:
            for e, color in zip(m.get_entries(), [X_COLOR, Y_COLOR]):
                e.set_color(color)
        cross_product = VGroup(m1, TexMobject("\\times"), m2)
        cross_product.arrange()
        (x1, x2), (x3, x4) = tuple(m1.get_entries()), tuple(m2.get_entries())
        entries = [x1, x2, x3, x4]
        for entry in entries:
            entry.target = entry.copy()
        eq, dot1, minus, dot2 = syms = list(map(TexMobject, 
            ["=", "\\cdot", "-", "\\cdot"]
        ))
        result = VGroup(
            eq, x1.target, dot1, x4.target,
            minus, x3.target, dot2, x2.target,
        )
        result.arrange(RIGHT)
        full_cross_product = VGroup(cross_product, result)
        full_cross_product.arrange(RIGHT)
        full_cross_product.next_to(h_line, DOWN, buff = MED_SMALL_BUFF/2)

        self.play(ShowCreation(h_line))
        self.play(Write(cross_product))
        self.play(
            Write(VGroup(*syms)),
            *[
                Transform(entry.copy(), entry.target)
                for entry in entries
            ]
        )
        self.wait()
        self.two_d_result = VGroup(*result[1:])

    def emphasize_output_type(self):
        three_d_brace = Brace(self.cross_result)
        two_d_brace = Brace(self.two_d_result)
        vector = three_d_brace.get_text("Vector")
        number = two_d_brace.get_text("Number")

        self.play(
            GrowFromCenter(two_d_brace),
            Write(number)
        )
        self.wait()
        self.play(
            GrowFromCenter(three_d_brace),
            Write(vector)
        )
        self.wait()

class PrereqDeterminant(Scene):
    def construct(self):
        title = TextMobject("""
            Prerequisite: Understanding determinants
        """)
        title.set_width(FRAME_WIDTH - 2)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()  

class Define2dCrossProduct(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "v_coords" : [3, 1],
        "w_coords" : [2, -1],
    }
    def construct(self):
        self.initial_definition()
        self.show_transformation()
        self.transform_square()
        self.show_orientation_rule()


    def initial_definition(self):
        self.plane.save_state()
        self.plane.fade()
        v = self.add_vector(self.v_coords, color = V_COLOR)
        w = self.add_vector(self.w_coords, color = W_COLOR)
        self.moving_vectors.remove(v)
        self.moving_vectors.remove(w)
        for vect, name, direction in (v, "v", "left"), (w, "w", "right"):
            color = vect.get_color()
            vect.label = self.label_vector(
                vect, name, color = color, direction = direction,
            )
            vect.coord_array = vector_coordinate_label(
                vect, color = color,
            )
            vect.coords = vect.coord_array.get_entries()
        for vect, edge in (v, DOWN), (w, UP):
            vect.coord_array.move_to(
                vect.coord_array.get_center(), 
                aligned_edge = edge
            )
            self.play(Write(vect.coord_array, run_time = 1))
        movers = [v.label, w.label, v.coords, w.coords]
        for mover in movers:
            mover.target = mover.copy()
        times = TexMobject("\\times")
        cross_product = VGroup(
            v.label.target, times, w.label.target
        )

        cross_product.arrange()
        matrix = Matrix(np.array([
            list(v.coords.target),
            list(w.coords.target)
        ]).T)
        det_text = get_det_text(matrix)
        full_det = VGroup(det_text, matrix)
        equals = TexMobject("=")
        equation = VGroup(cross_product, equals, full_det)
        equation.arrange()
        equation.to_corner(UP+LEFT)

        matrix_background = BackgroundRectangle(matrix)
        cross_background = BackgroundRectangle(cross_product)        

        disclaimer = TextMobject("$^*$ See ``Note on conventions'' in description")
        disclaimer.scale(0.7)
        disclaimer.set_color(RED)
        disclaimer.next_to(
            det_text.get_corner(UP+RIGHT), RIGHT, buff = 0
        )
        disclaimer.add_background_rectangle()

        self.play(
            FadeIn(cross_background),
            Transform(v.label.copy(), v.label.target),
            Transform(w.label.copy(), w.label.target),
            Write(times),
        )
        self.wait()
        self.play(
            ShowCreation(matrix_background),            
            Write(matrix.get_brackets()), 
            run_time = 1
        )
        self.play(Transform(v.coords.copy(), v.coords.target))
        self.play(Transform(w.coords.copy(), w.coords.target))
        matrix.add_to_back(matrix_background)
        self.wait()
        self.play(
            Write(equals),
            Write(det_text),
            Animation(matrix),
        )
        self.wait()
        self.play(FadeIn(disclaimer))
        self.wait()
        self.play(FadeOut(disclaimer))
        self.wait()

        cross_product.add_to_back(cross_background)
        cross_product.add(equals)
        self.cross_product = cross_product
        self.matrix = matrix
        self.det_text = det_text
        self.v, self.w = v, w

    def show_transformation(self):
        matrix = self.matrix.copy()
        everything = self.get_mobjects()
        everything.remove(self.plane)
        everything.remove(self.background_plane)
        self.play(
            *list(map(FadeOut, everything)) + [
            Animation(self.background_plane),
            self.plane.restore,            
            Animation(matrix),
        ])
        i_hat, j_hat = self.get_basis_vectors()
        for vect in i_hat, j_hat:
            vect.save_state()
        basis_labels = self.get_basis_vector_labels()
        self.play(
            ShowCreation(i_hat),
            ShowCreation(j_hat),
            Write(basis_labels)
        )
        self.wait()

        side_brace = Brace(matrix, RIGHT)
        transform_words = side_brace.get_text("Linear transformation")
        transform_words.add_background_rectangle()

        col1, col2 = [
            VGroup(*matrix.get_mob_matrix()[i,:])
            for i in (0, 1)
        ]

        both_words = []
        for char, color, col in ("i", X_COLOR, col1), ("j", Y_COLOR, col2):
            words = TextMobject("Where $\\hat\\%smath$ lands"%char)
            words.set_color(color)
            words.add_background_rectangle()
            words.next_to(col, DOWN, buff = LARGE_BUFF)
            words.arrow = Arrow(words.get_top(), col.get_bottom(), color = color)
            both_words.append(words)
        i_words, j_words = both_words

        self.play(
            GrowFromCenter(side_brace),
            Write(transform_words)
        )
        self.play(
            Write(i_words),
            ShowCreation(i_words.arrow),
            col1.set_color, X_COLOR
        )
        self.wait()
        self.play(
            Transform(i_words, j_words),
            Transform(i_words.arrow, j_words.arrow),
            col2.set_color, Y_COLOR
        )
        self.wait()
        self.play(*list(map(FadeOut, [i_words, i_words.arrow, basis_labels])))

        self.add_vector(i_hat, animate = False)
        self.add_vector(j_hat, animate = False)
        self.play(*list(map(FadeOut, [side_brace, transform_words])))
        self.add_foreground_mobject(matrix)
        self.apply_transposed_matrix([self.v_coords, self.w_coords])
        self.wait()
        self.play(
            FadeOut(self.plane),
            *list(map(Animation, [
                self.background_plane,
                matrix,
                i_hat,
                j_hat,
            ]))
        )
        self.play(
            ShowCreation(self.v),
            ShowCreation(self.w),
            FadeIn(self.v.label),
            FadeIn(self.w.label),
            FadeIn(self.v.coord_array),
            FadeIn(self.w.coord_array),
            matrix.set_column_colors, V_COLOR, W_COLOR
        )
        self.wait()
        self.i_hat, self.j_hat = i_hat, j_hat
        self.matrix = matrix


    def transform_square(self):
        self.play(Write(self.det_text))
        self.matrix.add(self.det_text)

        vect_stuffs = VGroup(*it.chain(*[
            [m, m.label, m.coord_array]
            for m in (self.v, self.w)
        ]))
        to_restore = [self.plane, self.i_hat, self.j_hat]
        for mob in to_restore:
            mob.fade(1)

        self.play(*list(map(FadeOut, vect_stuffs)))
        self.play(
            *[m.restore for m in to_restore] + [
                Animation(self.matrix)
            ]
        )
        self.add_unit_square(animate = True, opacity = 0.2)
        self.square.save_state()
        self.wait()
        self.apply_transposed_matrix(
            [self.v_coords, self.w_coords]
        )
        self.wait()
        self.play(
            FadeOut(self.plane),
            Animation(self.matrix),
            *list(map(FadeIn, vect_stuffs))
        )
        self.play(Write(self.cross_product))

        det_text_brace = Brace(self.det_text)
        area_words = det_text_brace.get_text("Area of this parallelogram")
        area_words.add_background_rectangle()
        area_arrow = Arrow(
            area_words.get_bottom(), 
            self.square.get_center(),
            color = WHITE
        )
        self.play(
            GrowFromCenter(det_text_brace),
            Write(area_words),
            ShowCreation(area_arrow)
        )
        self.wait()

        pm = VGroup(*list(map(TexMobject, ["+", "-"])))
        pm.set_color_by_gradient(GREEN, RED)
        pm.arrange(DOWN, buff = SMALL_BUFF)
        pm.add_to_back(BackgroundRectangle(pm))
        pm.next_to(area_words[0], LEFT, aligned_edge = DOWN)
        self.play(
            Transform(self.square.get_point_mobject(), pm),
            path_arc = -np.pi/2
        )
        self.wait()
        self.play(*list(map(FadeOut, [
            area_arrow, self.v.coord_array, self.w.coord_array
        ])))

    def show_orientation_rule(self):
        self.remove(self.i_hat, self.j_hat)
        for vect in self.v, self.w:
            vect.add(vect.label)
            vect.target = vect.copy()
        angle = np.pi/3
        self.v.target.rotate(-angle)
        self.w.target.rotate(angle)
        self.v.target.label.rotate_in_place(angle)
        self.w.target.label.rotate_in_place(-angle)
        for vect in self.v, self.w:
            vect.target.label[0].set_fill(opacity = 0)
        self.square.target = self.square.copy().restore()
        transform = self.get_matrix_transformation([
            self.v.target.get_end()[:2],
            self.w.target.get_end()[:2],
        ])
        self.square.target.apply_function(transform)

        movers = VGroup(self.square, self.v, self.w)
        movers.target = VGroup(*[m.target for m in movers])
        movers.save_state()
        self.remove(self.square)
        self.play(Transform(movers, movers.target))
        self.wait()

        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%s for s in ("v", "w")]
        positive_words, negative_words = words_list = [
            TexMobject(v_tex, "\\times", w_tex, "\\text{ is }", word)
            for word in ("\\text{positive}", "\\text{negative}")
        ]
        for words in words_list:
            words.set_color_by_tex(v_tex, V_COLOR)
            words.set_color_by_tex(w_tex, W_COLOR)
            words.set_color_by_tex("\\text{positive}", GREEN)
            words.set_color_by_tex("\\text{negative}", RED)
            words.add_background_rectangle()
            words.next_to(self.square, UP)
        arc = self.get_arc(self.v, self.w)
        arc.set_color(GREEN)
        self.play(
            Write(positive_words),
            ShowCreation(arc)
        )
        self.wait()
        self.remove(arc)
        self.play(movers.restore)
        arc = self.get_arc(self.v, self.w)
        arc.set_color(RED)
        self.play(
            Transform(positive_words, negative_words),
            ShowCreation(arc)
        )
        self.wait()

        anticommute = TexMobject(
            v_tex, "\\times", w_tex, "=-", w_tex, "\\times", v_tex
        )
        anticommute.shift(FRAME_X_RADIUS*RIGHT/2)
        anticommute.to_edge(UP)
        anticommute.set_color_by_tex(v_tex, V_COLOR)
        anticommute.set_color_by_tex(w_tex, W_COLOR)
        anticommute.add_background_rectangle()
        for v1, v2 in (self.v, self.w), (self.w, self.v):
            v1.label[0].set_fill(opacity = 0)
            v1.target = v1.copy()
            v1.target.label.rotate_in_place(v1.get_angle()-v2.get_angle())
            v1.target.label.scale_in_place(v1.get_length()/v2.get_length())
            v1.target.rotate(v2.get_angle()-v1.get_angle())
            v1.target.scale(v2.get_length()/v1.get_length())
            v1.target.label.move_to(v2.label)
        self.play(
            FadeOut(arc),
            Transform(positive_words, anticommute)
        )
        self.play(
            Transform(self.v, self.v.target),
            Transform(self.w, self.w.target),
            rate_func = there_and_back,
            run_time = 2,
        )
        self.wait()

    def get_arc(self, v, w, radius = 2):
        v_angle, w_angle = v.get_angle(), w.get_angle()
        nudge = 0.05
        arc = Arc(
            (1-2*nudge)*(w_angle - v_angle),
            start_angle = interpolate(v_angle, w_angle, nudge),
            radius = radius,
            stroke_width = 8,
        )
        arc.add_tip()
        return arc

class TwoDCrossProductExample(Define2dCrossProduct):
    CONFIG = {
        "v_coords" : [-3, 1],
        "w_coords" : [2, 1],
    }
    def construct(self):
        self.plane.fade()
        v = Vector(self.v_coords, color = V_COLOR)
        w = Vector(self.w_coords, color = W_COLOR)

        v.coords = Matrix(self.v_coords)
        w.coords = Matrix(self.w_coords)
        v.coords.next_to(v.get_end(), LEFT)
        w.coords.next_to(w.get_end(), RIGHT)
        v.coords.set_color(v.get_color())
        w.coords.set_color(w.get_color())
        for coords in v.coords, w.coords:
            coords.background_rectangle = BackgroundRectangle(coords)
            coords.add_to_back(coords.background_rectangle)


        v.label = self.get_vector_label(v, "v", "left", color = v.get_color())
        w.label = self.get_vector_label(w, "w", "right", color = w.get_color())

        matrix = Matrix(np.array([
            list(v.coords.copy().get_entries()),
            list(w.coords.copy().get_entries()),
        ]).T)
        matrix_background = BackgroundRectangle(matrix)        
        col1, col2 = it.starmap(Group, matrix.get_mob_matrix().T)
        det_text = get_det_text(matrix)
        v_tex, w_tex = get_vect_tex("v", "w")
        cross_product = TexMobject(v_tex, "\\times", w_tex, "=")
        cross_product.set_color_by_tex(v_tex, V_COLOR)
        cross_product.set_color_by_tex(w_tex, W_COLOR)
        cross_product.add_background_rectangle()
        equation_start = VGroup(
            cross_product, 
            VGroup(matrix_background, det_text, matrix)
        )
        equation_start.arrange()
        equation_start.next_to(ORIGIN, DOWN).to_edge(LEFT)


        for vect in v, w:
            self.play(
                ShowCreation(vect),
                Write(vect.coords),
                Write(vect.label)
            )
            self.wait()
        self.play(
            Transform(v.coords.background_rectangle, matrix_background),
            Transform(w.coords.background_rectangle, matrix_background),
            Transform(v.coords.get_entries(), col1),
            Transform(w.coords.get_entries(), col2),
            Transform(v.coords.get_brackets(), matrix.get_brackets()),
            Transform(w.coords.get_brackets(), matrix.get_brackets()),
        )
        self.play(*list(map(Write, [det_text, cross_product])))


        v1, v2 = v.coords.get_entries()
        w1, w2 = w.coords.get_entries()
        entries = v1, v2, w1, w2
        for entry in entries:
            entry.target = entry.copy()
        det = np.linalg.det([self.v_coords, self.w_coords])
        equals, dot1, minus, dot2, equals_result = syms = VGroup(*list(map(
            TexMobject,
            ["=", "\\cdot", "-", "\\cdot", "=%d"%det]
        )))

        equation_end = VGroup(
            equals, v1.target, dot1, w2.target, 
            minus, w1.target, dot2, v2.target, equals_result
        )
        equation_end.arrange()
        equation_end.next_to(equation_start)
        syms_rect = BackgroundRectangle(syms)
        syms.add_to_back(syms_rect)
        equation_end.add_to_back(syms_rect)
        syms.remove(equals_result)        

        self.play(
            Write(syms),            
            Transform(
                VGroup(v1, w2).copy(), VGroup(v1.target, w2.target),
                rate_func = squish_rate_func(smooth, 0, 1./3),
                path_arc = np.pi/2
            ),
            Transform(
                VGroup(v2, w1).copy(), VGroup(v2.target, w1.target),
                rate_func = squish_rate_func(smooth, 2./3, 1),
                path_arc = np.pi/2
            ),
            run_time = 3
        )
        self.wait()
        self.play(Write(equals_result))

        self.add_foreground_mobject(equation_start, equation_end)
        self.show_transformation(v, w)
        det_sym = TexMobject(str(int(abs(det))))
        det_sym.scale(1.5)
        det_sym.next_to(v.get_end()+w.get_end(), DOWN+RIGHT, buff = MED_SMALL_BUFF/2)
        arc = self.get_arc(v, w, radius = 1)
        arc.set_color(RED)
        self.play(Write(det_sym))
        self.play(ShowCreation(arc))
        self.wait()


    def show_transformation(self, v, w):
        i_hat, j_hat = self.get_basis_vectors()
        self.play(*list(map(ShowCreation, [i_hat, j_hat])))
        self.add_unit_square(animate = True, opacity = 0.2)
        self.apply_transposed_matrix(
            [v.get_end()[:2], w.get_end()[:2]],
            added_anims = [
                Transform(i_hat, v),
                Transform(j_hat, w)
            ]
        )

class PlayAround(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(""" \\centering 
            Play with the idea if
            you wish to understand it 
        """)
        self.change_student_modes("pondering", "happy", "happy")
        self.random_blink(2)
        self.student_thinks("", student_index = 0)
        self.zoom_in_on_thought_bubble()

class BiggerWhenPerpendicular(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
    }
    def construct(self):
        self.lock_in_faded_grid()
        self.add_unit_square(animate = False)
        square = self.square
        self.remove(square)

        start_words = TextMobject("More perpendicular")
        end_words = TextMobject("Similar direction")
        arrow = TextMobject("\\Rightarrow")
        v_tex, w_tex = get_vect_tex("v", "w")
        cross_is = TexMobject(v_tex, "\\times", w_tex, "\\text{ is }")
        cross_is.set_color_by_tex(v_tex, V_COLOR)
        cross_is.set_color_by_tex(w_tex, W_COLOR)
        bigger = TextMobject("bigger")
        smaller = TextMobject("smaller")
        bigger.scale(1.5)
        smaller.scale(0.75)
        bigger.set_color(PINK)
        smaller.set_color(TEAL)
        group = VGroup(start_words, arrow, cross_is, bigger)
        group.arrange()
        group.to_edge(UP)
        end_words.move_to(start_words, aligned_edge = RIGHT)
        smaller.next_to(cross_is, buff = MED_SMALL_BUFF/2, aligned_edge = DOWN)
        for mob in list(group) + [end_words, smaller]:
            mob.add_background_rectangle()

        v = Vector([2, 2], color = V_COLOR)
        w = Vector([2, -2], color = W_COLOR)
        v.target = v.copy().rotate(-np.pi/5)
        w.target = w.copy().rotate(np.pi/5)
        transforms = [
            self.get_matrix_transformation([v1.get_end()[:2], v2.get_end()[:2]])
            for v1, v2 in [(v, w), (v.target, w.target)]
        ]
        start_square, end_square = [
            square.copy().apply_function(transform)
            for transform in transforms
        ]

        for vect in v, w:
            self.play(ShowCreation(vect))
        group.remove(bigger)
        self.play(
            FadeIn(group), 
            ShowCreation(start_square),
            *list(map(Animation, [v, w]))
        )
        self.play(GrowFromCenter(bigger))
        self.wait()
        self.play(
            Transform(start_square, end_square),            
            Transform(v, v.target),
            Transform(w, w.target),
        )
        self.play(
            Transform(start_words, end_words),
            Transform(bigger, smaller)
        )
        self.wait()

class ScalingRule(LinearTransformationScene):
    CONFIG = {
        "v_coords" : [2, -1],
        "w_coords" : [1, 1],
        "show_basis_vectors" : False
    }
    def construct(self):
        self.lock_in_faded_grid()
        self.add_unit_square(animate = False)
        self.remove(self.square)
        square = self.square

        v = Vector(self.v_coords, color = V_COLOR)
        w = Vector(self.w_coords, color = W_COLOR)
        v.label = self.get_vector_label(v, "v", "right", color = V_COLOR)
        w.label = self.get_vector_label(w, "w", "left", color = W_COLOR)
        new_v = v.copy().scale(3)
        new_v.label = self.get_vector_label(
            new_v, "3\\vec{\\textbf{v}}", "right", color = V_COLOR
        )
        for vect in v, w, new_v:
            vect.add(vect.label)

        transform = self.get_matrix_transformation(
            [self.v_coords, self.w_coords]
        )
        square.apply_function(transform)
        new_squares = VGroup(*[
            square.copy().shift(m*v.get_end())
            for m in range(3)
        ])

        v_tex, w_tex = get_vect_tex("v", "w")
        cross_product = TexMobject(v_tex, "\\times", w_tex)
        rhs = TexMobject("=3(", v_tex, "\\times", w_tex, ")")
        three_v = TexMobject("(3", v_tex, ")")
        for tex_mob in cross_product, rhs, three_v:
            tex_mob.set_color_by_tex(v_tex, V_COLOR)
            tex_mob.set_color_by_tex(w_tex, W_COLOR)
        equation = VGroup(cross_product, rhs)
        equation.arrange()
        equation.to_edge(UP)
        v_tex_mob = cross_product[0]
        three_v.move_to(v_tex_mob, aligned_edge = RIGHT)
        for tex_mob in cross_product, rhs:
            tex_mob.add_background_rectangle()

        self.add(cross_product)
        self.play(ShowCreation(v))
        self.play(ShowCreation(w))
        self.play(
            ShowCreation(square),
            *list(map(Animation, [v, w]))
        )
        self.wait()
        self.play(
            Transform(v, new_v),
            Transform(v_tex_mob, three_v),
        )
        self.wait()
        self.play(
            Transform(square, new_squares),
            *list(map(Animation, [v, w])),
            path_arc = -np.pi/6
        )
        self.wait()
        self.play(Write(rhs))
        self.wait()

class TechnicallyNotTheDotProduct(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            That was technically
            not the cross product
        """)
        self.change_student_modes("confused")
        self.change_student_modes("confused", "angry")
        self.change_student_modes("confused", "angry", "sassy")
        self.random_blink(3)

class ThreeDShowParallelogramAndCrossProductVector(Scene):
    pass

class WriteAreaOfParallelogram(Scene):
    def construct(self):
        words = TextMobject(
            "Area of ", "parallelogram", " $=$ ", "$2.5$",
            arg_separator = ""
        )
        words.set_color_by_tex("parallelogram", BLUE)
        words.set_color_by_tex("$2.5$", BLUE)
        result = words[-1]
        words.remove(result)

        self.play(Write(words))
        self.wait()
        self.play(Write(result, run_time = 1))
        self.wait()

class WriteCrossProductProperties(Scene):
    def construct(self):
        v_tex, w_tex, p_tex = texs = get_vect_tex(*"vwp")
        v_cash, w_cash, p_cash = ["$%s$"%tex for tex in texs]
        cross_product = TexMobject(v_tex, "\\times", w_tex, "=", p_tex)
        cross_product.set_color_by_tex(v_tex, V_COLOR)
        cross_product.set_color_by_tex(w_tex, W_COLOR)
        cross_product.set_color_by_tex(p_tex, P_COLOR)
        cross_product.to_edge(UP, buff = LARGE_BUFF)
        p_mob = cross_product[-1]
        brace = Brace(p_mob)
        brace.do_in_place(brace.stretch, 2, 0)
        vector = brace.get_text("vector")
        vector.set_color(P_COLOR)
        length_words = TextMobject(
            "Length of ", p_cash, "\\\\ = ", 
            "(parallelogram's area)"
        )
        length_words.set_color_by_tex(p_cash, P_COLOR)
        length_words.set_width(FRAME_X_RADIUS - 1)
        length_words.set_color_by_tex("(parallelogram's area)", BLUE)
        length_words.next_to(VGroup(cross_product, vector), DOWN, buff = LARGE_BUFF)
        perpendicular = TextMobject(
            "\\centering Perpendicular to",
            v_cash, "and", w_cash
        )
        perpendicular.set_width(FRAME_X_RADIUS - 1)        
        perpendicular.set_color_by_tex(v_cash, V_COLOR)
        perpendicular.set_color_by_tex(w_cash, W_COLOR)
        perpendicular.next_to(length_words, DOWN, buff = LARGE_BUFF)


        self.play(Write(cross_product))
        self.play(
            GrowFromCenter(brace),
            Write(vector, run_time = 1)
        )
        self.wait()
        self.play(Write(length_words, run_time = 1))
        self.wait()
        self.play(Write(perpendicular))
        self.wait()

def get_cross_product_right_hand_rule_labels():
    v_tex, w_tex = get_vect_tex(*"vw")
    return [
        v_tex, w_tex,
        "%s \\times %s"%(v_tex, w_tex)
    ]

class CrossProductRightHandRule(RightHandRule):
    CONFIG = {
        "flip" : False,
        "labels_tex" : get_cross_product_right_hand_rule_labels(),
        "colors" : [U_COLOR, W_COLOR, P_COLOR],
    }

class LabelingExampleVectors(Scene):
    def construct(self):
        v_tex, w_tex = texs = get_vect_tex(*"vw")
        colors = [U_COLOR, W_COLOR, P_COLOR]
        equations = [
            TexMobject(v_tex, "=%s"%matrix_to_tex_string([0, 0, 2])),
            TexMobject(w_tex, "=%s"%matrix_to_tex_string([0, 2, 0])),
            TexMobject(
                v_tex, "\\times", w_tex, 
                "=%s"%matrix_to_tex_string([-4, 0, 0])
            ),
        ]
        for eq, color in zip(equations, colors):
            eq.set_color(color)
            eq.scale(2)

        area_words = TextMobject("Area", "=4")
        area_words[0].set_color(BLUE)
        area_words.scale(2)
        for mob in equations[:2] + [area_words, equations[2]]:
            self.fade_in_out(mob)

    def fade_in_out(self, mob):            
        self.play(FadeIn(mob))
        self.wait()
        self.play(FadeOut(mob))

class ThreeDTwoPossiblePerpendicularVectors(Scene):
    pass

class ThreeDCrossProductExample(Scene):
    pass

class ShowCrossProductFormula(Scene):
    def construct(self):
        colors = [X_COLOR, Y_COLOR, Z_COLOR]

        arrays = [
            ["%s_%d"%(s, i) for i in range(1, 4)]
            for s in ("v", "w")
        ]
        matrices = list(map(Matrix, arrays))
        for matrix in matrices:
            for entry, color in zip(matrix.get_entries(), colors):
                entry.set_color(color)
        m1, m2 = matrices
        cross_product = VGroup(m1, TexMobject("\\times"), m2)
        cross_product.arrange()
        cross_product.shift(2*LEFT)

        entry_dicts = [{} for x in range(3)]
        movement_sets = []
        for a, b, c in it.permutations(list(range(3))):
            sign = get_perm_sign(a, b, c)
            e1, e2 = m1.get_entries()[b], m2.get_entries()[c]
            for e in e1, e2:
                e.target = e.copy()
            dot = TexMobject("\\cdot")
            syms = VGroup(dot)
            
            if sign < 0:
                minus = TexMobject("-")
                syms.add(minus)
                cross_entry = VGroup(minus, e2.target, dot, e1.target)
                cross_entry.arrange()
                entry_dicts[a]["negative"] = cross_entry
            else:
                cross_entry = VGroup(e1.target, dot, e2.target)
                cross_entry.arrange()
                entry_dicts[a]["positive"] = cross_entry
            cross_entry.arrange()
            movement_sets.append([
                e1, e1.target,
                e2, e2.target,
                syms
            ])

        result = Matrix([
            VGroup(
                entry_dict["positive"],
                entry_dict["negative"],
            ).arrange()
            for entry_dict in entry_dicts
        ])
        equals = TexMobject("=").next_to(cross_product)
        result.next_to(equals)

        self.play(FadeIn(cross_product))
        self.play(
            Write(equals),
            Write(result.get_brackets())
        )
        self.wait()
        movement_sets[2], movement_sets[3] = movement_sets[3], movement_sets[2]
        for e1, e1_target, e2, e2_target, syms in movement_sets:
            e1.save_state()
            e2.save_state()
            self.play(
                e1.scale_in_place, 1.5,
                e2.scale_in_place, 1.5,
            )
            self.play(
                Transform(e1.copy(), e1_target),
                Transform(e2.copy(), e2_target),
                Write(syms),
                e1.restore, 
                e2.restore,
                path_arc = -np.pi/2
            )
        self.wait()

class ThisGetsWeird(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "This gets weird...", 
            target_mode = "sassy"
        )
        self.random_blink(2)

class DeterminantTrick(Scene):
    def construct(self):
        v_terms, w_terms = [
            ["%s_%d"%(s, d) for d in range(1, 4)]
            for s in ("v", "w")
        ]
        v = Matrix(v_terms)
        w = Matrix(w_terms)
        v.set_color(V_COLOR)
        w.set_color(W_COLOR)
        matrix = Matrix(np.array([
            [
                TexMobject("\\hat{%s}"%s)
                for s in ("\\imath", "\\jmath", "k")
            ],
            list(v.get_entries().copy()),
            list(w.get_entries().copy()),
        ]).T)
        colors = [X_COLOR, Y_COLOR, Z_COLOR]
        col1, col2, col3 = it.starmap(Group, matrix.get_mob_matrix().T)
        i, j, k = col1
        v1, v2, v3 = col2
        w1, w2, w3 = col3
        ##Really should fix Matrix mobject...
        j.shift(0.1*UP)
        k.shift(0.2*UP)
        VGroup(v2, w2).shift(0.1*DOWN)
        VGroup(v3, w3).shift(0.2*DOWN)
        ##

        for color, entry in zip(colors, col1):
            entry.set_color(color)
        det_text = get_det_text(matrix)
        equals = TexMobject("=")
        equation = VGroup(
            v, TexMobject("\\times"), w,
            equals, VGroup(det_text, matrix)
        )
        equation.arrange()

        self.add(*equation[:-2])
        self.wait()
        self.play(Write(matrix.get_brackets()))
        for col, vect in (col2, v), (col3, w):
            col.save_state()
            col.move_to(vect.get_entries())
            self.play(
                col.restore,
                path_arc = -np.pi/2,
            )
        for entry in col1:
            self.play(Write(entry))
        self.wait()
        self.play(*list(map(Write, [equals, det_text])))
        self.wait()

        disclaimer = TextMobject("$^*$ See ``Note on conventions'' in description")
        disclaimer.scale(0.7)
        disclaimer.set_color(RED)
        disclaimer.next_to(equation, DOWN)
        self.play(FadeIn(disclaimer))
        self.wait()
        self.play(FadeOut(disclaimer))

        circle = Circle()
        circle.stretch_to_fit_height(col1.get_height()+1)
        circle.stretch_to_fit_width(col1.get_width()+1)
        circle.move_to(col1)
        randy = Randolph()
        randy.scale(0.9)
        randy.to_corner()
        randy.to_edge(DOWN, buff = SMALL_BUFF)
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            ShowCreation(circle)
        )
        self.play(randy.look, RIGHT)
        self.wait()
        self.play(FadeOut(circle))

        self.play(
            equation.to_corner, UP+LEFT,
            ApplyFunction(
                lambda r : r.change_mode("plain").look(UP+RIGHT),
                randy
            )
        )
        quints = [
            (i, v2, w3, v3, w2),
            (j, v3, w1, v1, w3),
            (k, v1, w2, v2, w1),
        ]
        last_mob = None
        paren_sets = []
        for quint in quints:
            for mob in quint:
                mob.t = mob.copy()
                mob.save_state()
            basis = quint[0]
            basis.t.scale(1/0.8)
            lp, minus, rp = syms = VGroup(*list(map(TexMobject, "(-)")))
            term = VGroup(
                basis.t, lp,
                quint[1].t, quint[2].t, minus,
                quint[3].t, quint[4].t, rp
            )
            term.arrange()
            if last_mob:
                plus = TexMobject("+")
                syms.add(plus)
                plus.next_to(term, LEFT, buff = MED_SMALL_BUFF/2)
                term.add_to_back(plus)
                term.next_to(last_mob, RIGHT, buff = MED_SMALL_BUFF/2)
            else:
                term.next_to(equation, DOWN, buff = MED_SMALL_BUFF, aligned_edge = LEFT)
            last_mob = term
            self.play(*it.chain(*[
                [mob.scale_in_place, 1.2]
                for mob in quint
            ]))
            self.wait() 
            self.play(*[
                Transform(mob.copy(), mob.t) 
                for mob in quint
            ] + [
                mob.restore for mob in quint
            ] + [
                Write(syms)
            ], 
                run_time = 2
            )
            self.wait()
            paren_sets.append(VGroup(lp, rp))
        self.wait()
        self.play(randy.change_mode, "pondering")
        for parens in paren_sets:
            brace = Brace(parens)
            text = brace.get_text("Some number")
            text.set_width(brace.get_width())
            self.play(
                GrowFromCenter(brace),
                Write(text, run_time = 2)
            )
        self.wait()

class ThereIsAReason(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "\\centering Sure, it's a \\\\", "notational", "trick",
        )
        self.random_blink(2)
        words = TextMobject(
            "\\centering but there is a\\\\", 
            "reason", "for doing it"
        )
        words.set_color_by_tex("reason", YELLOW)
        self.teacher_says(words, target_mode = "surprised")
        self.change_student_modes(
            "raise_right_hand", "confused", "raise_left_hand"
        )
        self.random_blink()

class RememberDuality(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Remember ", "duality", "?", arg_separator = "")
        words[1].set_color_by_gradient(BLUE, YELLOW)
        self.teacher_says(words, target_mode = "sassy")
        self.random_blink(2)

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: Cross products in the
            light of linear transformations
        """)
        title.set_height(1.2)
        title.to_edge(UP, buff = MED_SMALL_BUFF/2)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()

class CrossAndDualWords(Scene):
    def construct(self):
        v_tex, w_tex, p_tex = get_vect_tex(*"vwp")
        vector_word = TextMobject("Vector:")
        transform_word = TextMobject("Dual transform:")

        cross = TexMobject(
            p_tex, "=", v_tex, "\\times", w_tex
        )
        for tex, color in zip([v_tex, w_tex, p_tex], [U_COLOR, W_COLOR, P_COLOR]):
            cross.set_color_by_tex(tex, color)
        input_array_tex = matrix_to_tex_string(["x", "y", "z"])
        func = TexMobject("L\\left(%s\\right) = "%input_array_tex)
        matrix = Matrix(np.array([
            ["x", "y", "z"],
            ["v_1", "v_2", "v_3"],
            ["w_1", "w_2", "w_3"],
        ]).T)
        matrix.set_column_colors(WHITE, U_COLOR, W_COLOR)
        det_text = get_det_text(matrix, background_rect = False)
        det_text.add(matrix)
        dot_with_cross = TexMobject(
            "%s \\cdot ( "%input_array_tex,
            v_tex, "\\times", w_tex, ")"
        )
        dot_with_cross.set_color_by_tex(v_tex, U_COLOR)
        dot_with_cross.set_color_by_tex(w_tex, W_COLOR)
        transform = VGroup(func, det_text)
        transform.arrange()

        VGroup(transform, dot_with_cross).scale(0.7)
        VGroup(vector_word, cross).arrange(
            RIGHT, buff = MED_SMALL_BUFF
        ).center().shift(LEFT).to_edge(UP)
        transform_word.next_to(vector_word, DOWN, buff = MED_SMALL_BUFF, aligned_edge = LEFT)
        transform.next_to(transform_word, DOWN, buff = MED_SMALL_BUFF, aligned_edge = LEFT)
        dot_with_cross.next_to(func, RIGHT)

        self.add(vector_word)
        self.play(Write(cross))
        self.wait()
        self.play(FadeIn(transform_word))
        self.play(Write(transform))
        self.wait()
        self.play(Transform(det_text, dot_with_cross))
        self.wait()










