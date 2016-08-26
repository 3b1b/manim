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
from eola.chapter5 import get_det_text


U_COLOR = ORANGE
V_COLOR = YELLOW
W_COLOR = MAROON_B

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "From [Grothendieck], I have also learned not"
            "to take glory in the ", 
            "difficulty of a proof:", 
            "difficulty means we have not understood."
            "The idea is to be able to",
            "paint a landscape",
            "in which the proof is obvious.",
            arg_separator = " "
        )
        words.highlight_by_tex("difficulty of a proof:", RED)
        words.highlight_by_tex("paint a landscape", GREEN)
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Pierre Deligne")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(4)
        self.play(Write(author, run_time = 3))
        self.dither()

class DoTheSameForCross(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Let's do the same \\\\ for", "cross products")
        words.highlight_by_tex("cross products", YELLOW)
        self.teacher_says(words, pi_creature_target_mode = "surprised")
        self.random_blink(2)
        self.change_student_modes("pondering")
        self.random_blink()

class ListSteps(RandolphScene):
    CONFIG = {
        "randy_corner" : DOWN+RIGHT
    }
    def construct(self):
        title = TextMobject("Two parts")
        title.highlight(YELLOW)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        h_line.next_to(title, DOWN)

        step_1 = TextMobject("1. Standard introduction")
        step_2 = TextMobject("2. Deeper understanding with ", "linear transformations")
        step_2.highlight_by_tex("linear transformations", BLUE)
        steps = Group(step_1, step_2)
        steps.arrange_submobjects(DOWN, aligned_edge = LEFT, buff = LARGE_BUFF)
        steps.next_to(self.randy, UP)
        steps.to_edge(LEFT)

        self.play(
            FadeIn(step_1),
            self.randy.change_mode, "happy"
        )
        self.dither()
        self.play(
            Write(step_2),
            self.randy.change_mode, "pondering"
        )
        self.dither()

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
            title.shift(vect*SPACE_WIDTH/2)
            title.to_edge(UP)
            title.highlight(color)
            self.add(title)
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        l_h_line = Line(LEFT, ORIGIN).scale(SPACE_WIDTH)
        r_h_line = Line(ORIGIN, RIGHT).scale(SPACE_WIDTH)
        r_h_line.next_to(title, DOWN)
        l_h_line.next_to(r_h_line, LEFT, buff = 0)
        self.add(v_line, l_h_line, r_h_line)
        self.l_h_line, self.r_h_line = l_h_line, r_h_line

    def add_dot_products(self, max_width = SPACE_WIDTH-1, dims = [2, 5]):
        colors = [X_COLOR, Y_COLOR, Z_COLOR, MAROON_B, TEAL]
        last_mob = self.l_h_line
        for dim in dims:
            arrays = [
                [random.randint(0, 9) for in_count in range(dim)]
                for out_count in range(2)
            ]
            m1, m2 = map(Matrix, arrays)
            for matrix in m1, m2:
                for entry, color in zip(matrix.get_entries(), colors):
                    entry.highlight(color)
            syms = map(TexMobject, ["="] + ["+"]*(dim-1))
            result = Group(*it.chain(*zip(
                syms,
                [
                    Group(
                        e1, TexMobject("\\cdot"), e2
                    ).arrange_submobjects()
                    for e1, e2 in zip(*[m.copy().get_entries() for m in m1, m2])
                ]
            )))
            result.arrange_submobjects(RIGHT)
            dot_prod = Group(
                m1, TexMobject("\\cdot"), m2, result
            )
            dot_prod.arrange_submobjects(RIGHT)
            if dot_prod.get_width() > max_width:
                dot_prod.scale_to_fit_width(max_width)
            dot_prod.next_to(last_mob, DOWN, buff = MED_BUFF)
            last_mob = dot_prod
            dot_prod.to_edge(LEFT)
            self.play(Write(dot_prod))

    def add_cross_product(self):
        colors = [X_COLOR, Y_COLOR, Z_COLOR]

        arrays = [
            [random.randint(0, 9) for in_count in range(3)]
            for out_count in range(2)
        ]
        matrices = map(Matrix, arrays)
        for matrix in matrices:
            for entry, color in zip(matrix.get_entries(), colors):
                entry.highlight(color)
        m1, m2 = matrices
        cross_product = Group(m1, TexMobject("\\times"), m2)
        cross_product.arrange_submobjects()

        index_to_cross_enty = {}
        syms = Group()
        movement_sets = []
        for a, b, c in it.permutations(range(3)):
            e1, e2 = m1.get_entries()[b], m2.get_entries()[c]
            for e in e1, e2:
                e.target = e.copy()
            movement_sets.append([e1, e1.target, e2, e2.target])
            dot = TexMobject("\\cdot")
            syms.add(dot)
            cross_entry = Group(e1.target, dot, e2.target)
            cross_entry.arrange_submobjects()
            if a not in index_to_cross_enty:
                index_to_cross_enty[a] = []
            index_to_cross_enty[a].append(cross_entry)
        result_entries = []
        for a in range(3):
            prod1, prod2 = index_to_cross_enty[a]
            if a == 1:
                prod1, prod2 = prod2, prod1
            prod2.arrange_submobjects(LEFT)
            minus = TexMobject("-")
            syms.add(minus)
            entry = Group(prod1, minus, prod2)
            entry.arrange_submobjects(RIGHT)
            result_entries.append(entry)

        result = Matrix(result_entries)
        full_cross_product = Group(
            cross_product, TexMobject("="), result
        )
        full_cross_product.arrange_submobjects()
        full_cross_product.scale(0.75)
        full_cross_product.next_to(self.r_h_line, DOWN, buff = MED_BUFF/2)
        full_cross_product.remove(result)
        self.play(
            Write(full_cross_product),
            Write(syms)
        )
        movements = []
        for e1, e1_target, e2, e2_target in movement_sets:
            movements += [
                e1.copy().move_to, e1_target,
                e2.copy().move_to, e2_target,
            ]
        self.play(
            Write(result.get_brackets()),
            *movements,
            run_time = 2
        )
        self.dither()

        brace = Brace(cross_product)
        brace_text = brace.get_text("Only 3d")
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )

        self.cross_result = result
        self.only_3d_text = brace_text

    def add_2d_cross_product(self):
        h_line = DashedLine(ORIGIN, SPACE_WIDTH*RIGHT)
        h_line.next_to(self.only_3d_text, DOWN, buff = MED_BUFF/2)
        h_line.to_edge(RIGHT, buff = 0)
        arrays = np.random.randint(0, 9, (2, 2))
        m1, m2 = matrices = map(Matrix, arrays)
        for m in matrices:
            for e, color in zip(m.get_entries(), [X_COLOR, Y_COLOR]):
                e.highlight(color)
        cross_product = Group(m1, TexMobject("\\times"), m2)
        cross_product.arrange_submobjects()
        (x1, x2), (x3, x4) = tuple(m1.get_entries()), tuple(m2.get_entries())
        entries = [x1, x2, x3, x4]
        for entry in entries:
            entry.target = entry.copy()
        eq, dot1, minus, dot2 = syms = map(TexMobject, 
            ["=", "\\cdot", "-", "\\cdot"]
        )
        result = Group(
            eq, x1.target, dot1, x4.target,
            minus, x3.target, dot2, x2.target,
        )
        result.arrange_submobjects(RIGHT)
        full_cross_product = Group(cross_product, result)
        full_cross_product.arrange_submobjects(RIGHT)
        full_cross_product.next_to(h_line, DOWN, buff = MED_BUFF/2)

        self.play(ShowCreation(h_line))
        self.play(Write(cross_product))
        self.play(
            Write(Group(*syms)),
            *[
                Transform(entry.copy(), entry.target)
                for entry in entries
            ]
        )
        self.dither()
        self.two_d_result = Group(*result[1:])

    def emphasize_output_type(self):
        three_d_brace = Brace(self.cross_result)
        two_d_brace = Brace(self.two_d_result)
        vector = three_d_brace.get_text("Vector")
        number = two_d_brace.get_text("Number")

        self.play(
            GrowFromCenter(three_d_brace),
            Write(vector)
        )
        self.dither()
        self.play(
            GrowFromCenter(two_d_brace),
            Write(number)
        )
        self.dither()

class PrereqDeterminant(Scene):
    def construct(self):
        title = TextMobject("""
            Prerequisite: Understanding determinants
        """)
        title.scale_to_fit_width(2*SPACE_WIDTH - 2)
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.scale_to_fit_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.dither()  

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
                vect, name, color = color, direction = direction
            )
            vect.coord_array = self.write_vector_coordinates(
                vect, color = color
            )
            self.foreground_mobjects.remove(vect.coord_array)
            vect.coords = vect.coord_array.get_entries()
        for vect, edge in (v, DOWN), (w, UP):
            vect.coord_array.move_to(
                vect.coord_array.get_center(), 
                aligned_edge = edge
            )
        movers = [v.label, w.label, v.coords, w.coords]
        for mover in movers:
            mover.target = mover.copy()
        times = TexMobject("\\times")
        cross_product = Group(
            v.label.target, times, w.label.target
        )

        cross_product.arrange_submobjects()
        matrix = Matrix(np.array([
            list(v.coords.target),
            list(w.coords.target)
        ]).T)
        det_text = get_det_text(matrix)
        full_det = Group(det_text, matrix)
        equals = TexMobject("=")
        equation = Group(cross_product, equals, full_det)
        equation.arrange_submobjects()
        equation.to_corner(UP+LEFT)

        matrix_background = BackgroundRectangle(matrix)
        cross_background = BackgroundRectangle(cross_product)        

        disclaimer = TextMobject("$^*$ See ``Note on conventions'' in description")
        disclaimer.scale(0.7)
        disclaimer.highlight(RED)
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
        self.dither()
        self.play(Transform(v.coords.copy(), v.coords.target))
        self.play(Transform(w.coords.copy(), w.coords.target))
        self.play(
            ShowCreation(matrix_background),            
            Write(matrix.get_brackets()), 
            Animation(matrix.get_entries()),
            run_time = 1
        )
        matrix.add_to_back(matrix_background)
        self.dither()
        self.play(
            Write(equals),
            Write(det_text),
            Animation(matrix),
        )
        self.dither()
        self.play(FadeIn(disclaimer))
        self.dither()
        self.play(FadeOut(disclaimer))
        self.dither()

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
            *map(FadeOut, everything) + [
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
        self.dither()

        side_brace = Brace(matrix, RIGHT)
        transform_words = side_brace.get_text("Linear transformation")
        transform_words.add_background_rectangle()

        col1, col2 = [
            Group(*matrix.get_mob_matrix()[i,:])
            for i in 0, 1
        ]

        both_words = []
        for char, color, col in ("i", X_COLOR, col1), ("j", Y_COLOR, col2):
            words = TextMobject("Where $\\hat\\%smath$ lands"%char)
            words.highlight(color)
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
            col1.highlight, X_COLOR
        )
        self.dither()
        self.play(
            Transform(i_words, j_words),
            Transform(i_words.arrow, j_words.arrow),
            col2.highlight, Y_COLOR
        )
        self.dither()
        self.play(*map(FadeOut, [i_words, i_words.arrow, basis_labels]))

        self.add_vector(i_hat, animate = False)
        self.add_vector(j_hat, animate = False)
        self.play(*map(FadeOut, [side_brace, transform_words]))
        self.add_foreground_mobject(matrix)
        self.apply_transposed_matrix([self.v_coords, self.w_coords])
        self.dither()
        self.play(
            FadeOut(self.plane),
            *map(Animation, [
                self.background_plane,
                matrix,
                i_hat,
                j_hat,
            ])
        )
        self.play(
            ShowCreation(self.v),
            ShowCreation(self.w),
            FadeIn(self.v.label),
            FadeIn(self.w.label),
            FadeIn(self.v.coord_array),
            FadeIn(self.w.coord_array),
            matrix.highlight_columns, V_COLOR, W_COLOR
        )
        self.dither()
        self.i_hat, self.j_hat = i_hat, j_hat
        self.matrix = matrix


    def transform_square(self):
        self.play(Write(self.det_text))
        self.matrix.add(self.det_text)

        vect_stuffs = Group(*it.chain(*[
            [m, m.label, m.coord_array]
            for m in self.v, self.w
        ]))
        to_restore = [self.plane, self.i_hat, self.j_hat]
        for mob in to_restore:
            mob.fade(1)

        self.play(*map(FadeOut, vect_stuffs))
        self.play(
            *[m.restore for m in to_restore] + [
                Animation(self.matrix)
            ]
        )
        self.add_unit_square(animate = True, opacity = 0.2)
        self.square.save_state()
        self.dither()
        self.apply_transposed_matrix(
            [self.v_coords, self.w_coords]
        )
        self.dither()
        self.play(
            FadeOut(self.plane),
            Animation(self.matrix),
            *map(FadeIn, vect_stuffs)
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
        self.dither()

        pm = Group(*map(TexMobject, ["+", "-"]))
        pm.gradient_highlight(GREEN, RED)
        pm.arrange_submobjects(DOWN, buff = SMALL_BUFF)
        pm.add_to_back(BackgroundRectangle(pm))
        pm.next_to(area_words[0], LEFT, aligned_edge = DOWN)
        self.play(
            Transform(self.square.get_point_mobject(), pm),
            path_arc = -np.pi/2
        )
        self.dither()
        self.play(*map(FadeOut, [
            area_arrow, self.v.coord_array, self.w.coord_array
        ]))

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

        movers = Group(self.square, self.v, self.w)
        movers.target = Group(*[m.target for m in movers])
        movers.save_state()
        self.remove(self.square)
        self.play(Transform(movers, movers.target))
        self.dither()

        v_tex, w_tex = ["\\vec{\\textbf{%s}}"%s for s in "v", "w"]
        positive_words, negative_words = words_list = [
            TexMobject(v_tex, "\\times", w_tex, "\\text{ is }", word)
            for word in "\\text{positive}", "\\text{negative}"
        ]
        for words in words_list:
            words.highlight_by_tex(v_tex, V_COLOR)
            words.highlight_by_tex(w_tex, W_COLOR)
            words.highlight_by_tex("\\text{positive}", GREEN)
            words.highlight_by_tex("\\text{negative}", RED)
            words.add_background_rectangle()
            words.next_to(self.square, UP)
        arc = self.get_arc(self.v, self.w)
        arc.highlight(GREEN)
        self.play(
            Write(positive_words),
            ShowCreation(arc)
        )
        self.dither()
        self.remove(arc)
        self.play(movers.restore)
        arc = self.get_arc(self.v, self.w)
        arc.highlight(RED)
        self.play(
            Transform(positive_words, negative_words),
            ShowCreation(arc)
        )
        self.dither()

        anticommute = TexMobject(
            v_tex, "\\times", w_tex, "=-", w_tex, "\\times", v_tex
        )
        anticommute.shift(SPACE_WIDTH*RIGHT/2)
        anticommute.to_edge(UP)
        anticommute.highlight_by_tex(v_tex, V_COLOR)
        anticommute.highlight_by_tex(w_tex, W_COLOR)
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
        self.dither()

    def get_arc(self, v, w, radius = 2):
        v_angle, w_angle = v.get_angle(), w.get_angle()
        nudge = 0.05
        arc = Arc(
            (1-2*nudge)*(v_angle - w_angle),
            start_angle = interpolate(w_angle, v_angle, nudge),
            radius = radius,
            stroke_width = 8,
        )
        arc.add_tip()
        return arc




























