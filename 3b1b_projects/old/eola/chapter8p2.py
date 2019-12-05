from manimlib.imports import *
from old_projects.eola.chapter5 import get_det_text
from old_projects.eola.chapter8 import *


class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "From [Grothendieck], I have also learned not",
            "to take glory in the ", 
            "difficulty of a proof:", 
            "difficulty means we have not understood.",
            "The idea is to be able to ",
            "paint a landscape",
            "in which the proof is obvious.",
            arg_separator = " "
        )
        words.set_color_by_tex("difficulty of a proof:", RED)
        words.set_color_by_tex("paint a landscape", GREEN)
        words.set_width(FRAME_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Pierre Deligne")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(4)
        self.play(Write(author, run_time = 3))
        self.wait()

class CrossProductSymbols(Scene):
    def construct(self):
        v_tex, w_tex, p_tex = get_vect_tex(*"vwp")
        equation = TexMobject(
            v_tex, "\\times", w_tex, "=", p_tex
        )
        equation.set_color_by_tex(v_tex, V_COLOR)
        equation.set_color_by_tex(w_tex, W_COLOR)
        equation.set_color_by_tex(p_tex, P_COLOR)
        brace = Brace(equation[-1])
        brace.stretch_to_fit_width(0.7)
        vector_text = brace.get_text("Vector")
        vector_text.set_color(RED)
        self.add(equation)
        self.play(*list(map(Write, [brace, vector_text])))
        self.wait()

class DeterminantTrickCopy(DeterminantTrick):
    pass

class BruteForceVerification(Scene):
    def construct(self):
        v = Matrix(["v_1", "v_2", "v_3"])
        w = Matrix(["w_1", "w_2", "w_3"])
        v1, v2, v3 = v.get_entries()
        w1, w2, w3 = w.get_entries()
        v.set_color(V_COLOR)
        w.set_color(W_COLOR)
        def get_term(e1, e2, e3, e4):
            group = VGroup(
                e1.copy(), e2.copy(), 
                TexMobject("-"),
                e3.copy(), e4.copy(),
            )
            group.arrange()
            return group
        cross = Matrix(list(it.starmap(get_term, [
            (v2, w3, v3, w2),
            (v3, w1, v1, w3),
            (v2, w3, v3, w2),
        ])))
        cross_product = VGroup(
            v.copy(), TexMobject("\\times"), w.copy(),
            TexMobject("="), cross.copy()
        )
        cross_product.arrange()
        cross_product.scale(0.75)

        formula_word = TextMobject("Numerical formula")
        computation_words = TextMobject("""
            Facts you could (painfully)
            verify computationally
        """)
        computation_words.scale(0.75)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        computation_words.to_edge(UP, buff = MED_SMALL_BUFF/2)
        h_line.next_to(computation_words, DOWN)
        formula_word.next_to(h_line, UP, buff = MED_SMALL_BUFF)
        computation_words.shift(FRAME_X_RADIUS*RIGHT/2)
        formula_word.shift(FRAME_X_RADIUS*LEFT/2)

        cross_product.next_to(formula_word, DOWN, buff = LARGE_BUFF)

        self.add(formula_word, computation_words)
        self.play(
            ShowCreation(h_line),
            ShowCreation(v_line),
            Write(cross_product)
        )

        v_tex, w_tex = get_vect_tex(*"vw")
        v_dot, w_dot = [
            TexMobject(
                tex, "\\cdot", 
                "(", v_tex, "\\times", w_tex, ")",
                "= 0"
            )
            for tex in (v_tex, w_tex)
        ]
        theta_def = TexMobject(
            "\\theta", 
            "= \\cos^{-1} \\big(", v_tex, "\\cdot", w_tex, "/",
            "(||", v_tex, "||", "\\cdot", "||", w_tex, "||)", "\\big)"
        )

        length_check = TexMobject(
            "||", "(", v_tex, "\\times", w_tex, ")", "|| = ",
            "(||", v_tex, "||)",
            "(||", w_tex, "||)",
            "\\sin(", "\\theta", ")"
        )
        last_point = h_line.get_center()+FRAME_X_RADIUS*RIGHT/2
        max_width = FRAME_X_RADIUS-1
        for mob in v_dot, w_dot, theta_def, length_check:
            mob.set_color_by_tex(v_tex, V_COLOR)
            mob.set_color_by_tex(w_tex, W_COLOR)
            mob.set_color_by_tex("\\theta", GREEN)
            mob.next_to(last_point, DOWN, buff = MED_SMALL_BUFF)
            if mob.get_width() > max_width:
                mob.set_width(max_width)
            last_point = mob
            self.play(FadeIn(mob))
        self.wait()

class ButWeCanDoBetter(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("But we can do \\\\ better than that")
        self.change_student_modes(*["happy"]*3)
        self.random_blink(3)

class Prerequisites(Scene):
    def construct(self):
        title = TextMobject("Prerequisites")
        title.to_edge(UP)
        title.set_color(YELLOW)

        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_width(FRAME_X_RADIUS - 1)
        left_rect, right_rect = [
            rect.copy().shift(DOWN/2).to_edge(edge)
            for edge in (LEFT, RIGHT)
        ]
        chapter5 = TextMobject("""
            \\centering 
            Chapter 5 
            Determinants
        """)
        chapter7 = TextMobject("""
            \\centering
            Chapter 7: 
            Dot products and duality
        """)

        self.add(title)
        for chapter, rect in (chapter5, left_rect), (chapter7, right_rect):
            if chapter.get_width() > rect.get_width():
                chapter.set_width(rect.get_width())
            chapter.next_to(rect, UP)
            self.play(
                Write(chapter5), 
                ShowCreation(left_rect)
            )
        self.play(
            Write(chapter7),
            ShowCreation(right_rect)
        )
        self.wait()

class DualityReview(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Quick", "duality", "review")
        words[1].set_color_by_gradient(BLUE, YELLOW)
        self.teacher_says(words, target_mode = "surprised")
        self.change_student_modes("pondering")
        self.random_blink(2)

class DotProductToTransformSymbol(Scene):
    CONFIG = {
        "vect_coords" : [2, 1]
    }
    def construct(self):
        v_mob = TexMobject(get_vect_tex("v"))
        v_mob.set_color(V_COLOR)

        matrix = Matrix([self.vect_coords])
        vector = Matrix(self.vect_coords)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        vector.set_column_colors(YELLOW)
        _input = Matrix(["x", "y"])
        _input.get_entries().set_color_by_gradient(X_COLOR, Y_COLOR)
        left_input, right_input = [_input.copy() for x in range(2)]
        dot, equals = list(map(TexMobject, ["\\cdot", "="]))
        equation = VGroup(
            vector, dot, left_input, equals,
            matrix, right_input
        )
        equation.arrange()
        left_brace = Brace(VGroup(vector, left_input))
        right_brace = Brace(matrix, UP)
        left_words = left_brace.get_text("Dot product")
        right_words = right_brace.get_text("Transform")
        right_words.set_width(right_brace.get_width())

        right_v_brace = Brace(right_input, UP)
        right_v_mob = v_mob.copy()
        right_v_brace.put_at_tip(right_v_mob)
        right_input.add(right_v_brace, right_v_mob)
        left_v_brace = Brace(left_input, UP)
        left_v_mob = v_mob.copy()
        left_v_brace.put_at_tip(left_v_mob)
        left_input.add(left_v_brace, left_v_mob)        


        self.add(matrix, right_input)
        self.play(
            GrowFromCenter(right_brace),
            Write(right_words, run_time = 1)
        )
        self.wait()
        self.play(
            Write(equals),
            Write(dot),
            Transform(matrix.copy(), vector),
            Transform(right_input.copy(), left_input)
        )
        self.play(
            GrowFromCenter(left_brace),
            Write(left_words, run_time = 1)
        )
        self.wait()

class MathematicalWild(Scene):
    def construct(self):
        title = TextMobject("In the mathematical wild")
        title.to_edge(UP)
        self.add(title)

        randy = Randolph()
        randy.shift(DOWN)
        bubble = ThoughtBubble(width = 5, height = 4)
        bubble.write("""
            \\centering
            Some linear 
            transformation
            to the number line
        """)
        bubble.content.set_color(BLUE)
        bubble.content.shift(MED_SMALL_BUFF*UP/2)
        bubble.remove(*bubble[:-1])
        bubble.add(bubble.content)
        bubble.next_to(randy.get_corner(UP+RIGHT), RIGHT)
        vector = Vector([1, 2])
        vector.move_to(randy.get_corner(UP+LEFT), aligned_edge = DOWN+LEFT)
        dual_words = TextMobject("Dual vector")
        dual_words.set_color_by_gradient(BLUE, YELLOW)
        dual_words.next_to(vector, LEFT)

        self.add(randy)
        self.play(Blink(randy))
        self.play(FadeIn(bubble))
        self.play(randy.change_mode, "sassy")
        self.play(Blink(randy))
        self.wait()
        self.play(randy.look, UP+LEFT)
        self.play(
            ShowCreation(vector),
            randy.change_mode, "raise_right_hand"
        )
        self.wait()
        self.play(Write(dual_words))
        self.play(Blink(randy))
        self.wait()

class ThreeStepPlan(Scene):
    def construct(self):
        title = TextMobject("The plan")
        title.set_color(YELLOW)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)

        v_tex, w_tex = get_vect_tex(*"vw")
        v_text, w_text, cross_text = [
            "$%s$"%s 
            for s in (v_tex, w_tex, v_tex + "\\times" + w_tex)
        ]
        steps = [
            TextMobject(
                "1. Define a 3d-to-1d", "linear \\\\", "transformation",
                "in terms of", v_text, "and", w_text
            ),
            TextMobject(
                "2. Find its", "dual vector"
            ),
            TextMobject(
                "3. Show that this dual is", cross_text
            )
        ]
        linear, transformation = steps[0][1:1+2]
        steps[0].set_color_by_tex(v_text, V_COLOR)
        steps[0].set_color_by_tex(w_text, W_COLOR)
        steps[1][1].set_color_by_gradient(BLUE, YELLOW)
        steps[2].set_color_by_tex(cross_text, P_COLOR)
        VGroup(*steps).arrange(
            DOWN, aligned_edge = LEFT, buff = LARGE_BUFF
        ).next_to(h_line, DOWN, buff = MED_SMALL_BUFF)

        self.add(title)
        self.play(ShowCreation(h_line))
        for step in steps:
            self.play(Write(step, run_time = 2))
            self.wait()

        linear_transformation = TextMobject("Linear", "transformation")
        linear_transformation.next_to(h_line, DOWN, MED_SMALL_BUFF)
        det = self.get_det()
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(3.5)
        left_right_arrow = TexMobject("\\Leftrightarrow")
        left_right_arrow.shift(DOWN)
        det.next_to(left_right_arrow, LEFT)
        rect.next_to(left_right_arrow, RIGHT)

        steps[0].remove(linear, transformation)
        self.play(
            Transform(
                VGroup(linear, transformation), 
                linear_transformation
            ),
            *list(map(FadeOut, steps))
        )
        self.wait()
        self.play(Write(left_right_arrow))
        self.play(Write(det))
        self.play(ShowCreation(rect))
        self.wait(0)

    def get_det(self):
        matrix = Matrix(np.array([
            ["\\hat{\\imath}", "\\hat{\\jmath}", "\\hat{k}"],
            ["v_%d"%d for d in range(1, 4)],
            ["w_%d"%d for d in range(1, 4)],
        ]).T)
        matrix.set_column_colors(X_COLOR, V_COLOR, W_COLOR)
        matrix.get_mob_matrix()[1, 0].set_color(Y_COLOR)
        matrix.get_mob_matrix()[2, 0].set_color(Z_COLOR)
        VGroup(*matrix.get_mob_matrix()[1, 1:]).shift(0.15*DOWN)
        VGroup(*matrix.get_mob_matrix()[2, 1:]).shift(0.35*DOWN)
        det_text = get_det_text(matrix)
        det_text.add(matrix)
        return det_text

class DefineDualTransform(Scene):
    def construct(self):
        self.add_title()
        self.show_triple_cross_product()
        self.write_function()
        self.introduce_dual_vector()
        self.expand_dot_product()
        self.ask_question()

    def add_title(self):
        title = TextMobject("What a student might think")
        title.not_real = TextMobject("Not the real cross product")
        for mob in title, title.not_real:
            mob.set_width(FRAME_X_RADIUS - 1)
            mob.set_color(RED)
            mob.to_edge(UP)
        self.add(title)
        self.title = title

    def show_triple_cross_product(self):
        colors = [WHITE, ORANGE, W_COLOR]
        tex_mobs = list(map(TexMobject, get_vect_tex(*"uvw")))
        u_tex, v_tex, w_tex = tex_mobs
        arrays = [
            Matrix(["%s_%d"%(s, d) for d in range(1, 4)])
            for s in "uvw"
        ]
        defs_equals = VGroup()
        definitions = VGroup()
        for array, tex_mob, color in zip(arrays, tex_mobs, colors):
            array.set_column_colors(color)
            tex_mob.set_color(color)
            equals = TexMobject("=")
            definition = VGroup(tex_mob, equals, array)
            definition.arrange(RIGHT)
            definitions.add(definition)
            defs_equals.add(equals)
        definitions.arrange(buff = MED_SMALL_BUFF)
        definitions.shift(2*DOWN)

        mobs_with_targets = list(it.chain(
            tex_mobs, *[a.get_entries() for a in arrays]
        ))
        for mob in mobs_with_targets:
            mob.target = mob.copy()
        matrix = Matrix(np.array([
            [e.target for e in array.get_entries()]
            for array in arrays
        ]).T)
        det_text = get_det_text(matrix, background_rect = False)
        syms = times1, times2, equals = [
            TexMobject(sym) 
            for sym in ("\\times", "\\times", "=",)
        ]
        triple_cross = VGroup(
            u_tex.target, times1, v_tex.target, times2, w_tex.target, equals
        )
        triple_cross.arrange()

        final_mobs = VGroup(triple_cross, VGroup(det_text, matrix))
        final_mobs.arrange()
        final_mobs.next_to(self.title, DOWN, buff = MED_SMALL_BUFF)

        for mob in definitions, final_mobs:
            mob.set_width(FRAME_X_RADIUS - 1)

        for array in arrays:
            brackets = array.get_brackets()
            brackets.target = matrix.get_brackets()
            mobs_with_targets.append(brackets)
        for def_equals in defs_equals:
            def_equals.target = equals
            mobs_with_targets.append(def_equals)

        self.play(FadeIn(
            definitions,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait(2)
        self.play(*[
            Transform(mob.copy(), mob.target)
            for mob in tex_mobs
        ] + [
            Write(times1),
            Write(times2),
        ])
        triple_cross.add(*self.get_mobjects_from_last_animation()[:3])
        self.play(*[
            Transform(mob.copy(), mob.target)
            for mob in mobs_with_targets
            if mob not in tex_mobs
        ])
        u_entries = self.get_mobjects_from_last_animation()[:3]
        v_entries = self.get_mobjects_from_last_animation()[3:6]
        w_entries = self.get_mobjects_from_last_animation()[6:9]
        self.play(Write(det_text))
        self.wait(2)

        self.det_text = det_text
        self.definitions = definitions
        self.u_entries = u_entries
        self.v_entries = v_entries
        self.w_entries = w_entries
        self.matrix = matrix
        self.triple_cross = triple_cross
        self.v_tex, self.w_tex = v_tex, w_tex
        self.equals = equals

    def write_function(self):
        brace = Brace(self.det_text, DOWN)
        number_text = brace.get_text("Number")
        self.play(Transform(self.title, self.title.not_real))
        self.wait()
        self.play(FadeOut(self.definitions))
        self.play(
            GrowFromCenter(brace),
            Write(number_text)
        )
        self.wait()

        x, y, z = variables = list(map(TexMobject, "xyz"))
        for var, entry in zip(variables, self.u_entries):
            var.scale(0.8) 
            var.move_to(entry)
            entry.target = var
        brace.target = Brace(z)
        brace.target.stretch_to_fit_width(0.5)
        number_text.target = brace.target.get_text("Variable")
        v_brace = Brace(self.matrix.get_mob_matrix()[0, 1], UP)
        w_brace = Brace(self.matrix.get_mob_matrix()[0, 2], UP)
        for vect_brace, tex in (v_brace, self.v_tex), (w_brace, self.w_tex):
            vect_brace.stretch_to_fit_width(brace.target.get_width())
            new_tex = tex.copy()
            vect_brace.put_at_tip(new_tex)
            vect_brace.tex = new_tex
        func_tex = TexMobject(
            "f\\left(%s\\right)"%matrix_to_tex_string(list("xyz"))
        )
        func_tex.scale(0.7)
        func_input = Matrix(list("xyz"))
        func_input_template = VGroup(*func_tex[3:-2])
        func_input.set_height(func_input_template.get_height())
        func_input.next_to(VGroup(*func_tex[:3]), RIGHT)
        VGroup(*func_tex[-2:]).next_to(func_input, RIGHT)
        func_tex[0].scale_in_place(1.5)

        func_tex = VGroup(
            VGroup(*[func_tex[i] for i in (0, 1, 2, -2, -1)]),
            func_input
        )
        func_tex.next_to(self.equals, LEFT)

        self.play(
            FadeOut(self.title),
            FadeOut(self.triple_cross),
            *[
                Transform(mob, mob.target)
                for mob in [brace, number_text]
            ]
        )
        self.play(*[
            Transform(mob, mob.target)
            for mob in self.u_entries
        ])
        self.play(*[
            Write(VGroup(vect_brace, vect_brace.tex))
            for vect_brace in (v_brace, w_brace)
        ])
        self.wait()
        self.play(Write(func_tex))
        self.wait()

        self.func_tex = func_tex
        self.variables_text = VGroup(brace, number_text)

    def introduce_dual_vector(self):
        everything = VGroup(*self.get_mobjects())
        colors = [X_COLOR, Y_COLOR, Z_COLOR]
        q_marks = VGroup(*list(map(TextMobject, "???")))
        q_marks.scale(2)
        q_marks.set_color_by_gradient(*colors)

        title = VGroup(TextMobject("This function is linear"))
        title.set_color(GREEN)
        title.to_edge(UP)
        matrix = Matrix([list(q_marks.copy())])
        matrix.set_height(self.func_tex.get_height()/2)
        dual_vector = Matrix(list(q_marks))
        dual_vector.set_height(self.func_tex.get_height())
        dual_vector.get_brackets()[0].shift(0.2*LEFT)
        dual_vector.get_entries().shift(0.1*LEFT)
        dual_vector.scale(1.25)
        dual_dot = VGroup(
            dual_vector,
            TexMobject("\\cdot").next_to(dual_vector)
        )
        matrix_words = TextMobject("""
            $1 \\times 3$ matrix encoding the 
            3d-to-1d linear transformation
        """)

        self.play(
            Write(title, run_time = 2),
            everything.shift, DOWN
        )
        self.remove(everything)
        self.add(*everything)
        self.wait()

        func, func_input = self.func_tex
        func_input.target = func_input.copy()
        func_input.target.scale(1.2)
        func_input.target.move_to(self.func_tex, aligned_edge = RIGHT)
        matrix.next_to(func_input.target, LEFT)
        dual_dot.next_to(func_input.target, LEFT)
        matrix_words.next_to(matrix, DOWN, buff = 1.5)
        matrix_words.shift_onto_screen()
        matrix_arrow = Arrow(
            matrix_words.get_top(),
            matrix.get_bottom(),
            color = WHITE
        )

        self.play(
            Transform(func, matrix),
            MoveToTarget(func_input),
            FadeOut(self.variables_text),
        )
        self.wait()
        self.play(
            Write(matrix_words),
            ShowCreation(matrix_arrow)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [matrix_words, matrix_arrow])))
        self.play(
            Transform(func, dual_vector),
            Write(dual_dot[1])
        )
        self.wait()

        p_coords = VGroup(*list(map(TexMobject, [
            "p_%d"%d for d in range(1, 4)
        ])))
        p_coords.set_color(RED)        
        p_array = Matrix(list(p_coords))
        p_array.set_height(dual_vector.get_height())
        p_array.move_to(dual_vector, aligned_edge = RIGHT)
        p_brace = Brace(p_array, UP)
        p_tex = TexMobject(get_vect_tex("p"))
        p_tex.set_color(P_COLOR)
        p_brace.put_at_tip(p_tex)

        self.play(
            GrowFromCenter(p_brace),
            Write(p_tex)
        )
        self.play(Transform(
            func, p_array,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.remove(func)
        self.add(p_array)
        self.wait()
        self.play(FadeOut(title))
        self.wait()

        self.p_array = p_array
        self.input_array = func_input

    def expand_dot_product(self):
        everything = VGroup(*self.get_mobjects())
        self.play(everything.to_edge, UP)
        self.remove(everything)
        self.add(*everything)
        to_fade = VGroup()

        p_entries = self.p_array.get_entries()
        input_entries = self.input_array.get_entries()
        dot_components = VGroup()
        for p, x, i in zip(p_entries, input_entries, it.count()):
            if i == 2:
                x.sym  = TexMobject("=")
            else:
                x.sym  = TexMobject("+")
            p.sym = TexMobject("\\cdot")
            p.target = p.copy().scale(2)
            x.target = x.copy().scale(2)
            component = VGroup(p.target, p.sym, x.target, x.sym)
            component.arrange()
            dot_components.add(component)
        dot_components.arrange()
        dot_components.next_to(ORIGIN, LEFT)
        dot_components.shift(1.5*DOWN)
        dot_arrow = Arrow(self.p_array.get_corner(DOWN+RIGHT), dot_components)
        to_fade.add(dot_arrow)
        self.play(ShowCreation(dot_arrow))
        new_ps = VGroup()
        for p, x in zip(p_entries, input_entries):
            self.play(
                MoveToTarget(p.copy()),
                MoveToTarget(x.copy()),
                Write(p.sym),
                Write(x.sym)
            )
            mobs = self.get_mobjects_from_last_animation()
            new_ps.add(mobs[0])
            to_fade.add(*mobs[1:])
            self.wait()

        x, y, z = self.u_entries
        v1, v2, v3 = self.v_entries
        w1, w2, w3 = self.w_entries
        cross_components = VGroup()
        quints = [
            (x, v2, w3, v3, w2),
            (y, v3, w1, v1, w3),
            (z, v1, w2, v2, w1),
        ]
        quints = [
            [m.copy() for m in quint]
            for quint in quints
        ]
        for i, quint in enumerate(quints):
            sym_strings = ["(", "\\cdot", "-", "\\cdot", ")"]
            if i < 2:
                sym_strings[-1] += "+"
            syms = list(map(TexMobject, sym_strings))
            for mob, sym in zip(quint, syms):
                mob.target = mob.copy()
                mob.target.scale(1.5)
                mob.sym = sym
            quint_targets = [mob.target for mob in quint]
            component = VGroup(*it.chain(*list(zip(quint_targets, syms))))
            component.arrange()
            cross_components.add(component)
            to_fade.add(syms[0], syms[-1], quint[0])
        cross_components.arrange(DOWN, aligned_edge = LEFT, buff = MED_SMALL_BUFF)
        cross_components.next_to(dot_components, RIGHT)
        for quint in quints:
            self.play(*[
                ApplyMethod(mob.set_color, YELLOW)
                for mob in quint
            ])
            self.wait(0.5)
            self.play(*[
                MoveToTarget(mob)
                for mob in quint
            ] + [
                Write(mob.sym)
                for mob in quint
            ])
            self.wait()
        self.play(
            ApplyFunction(
                lambda m : m.arrange(
                    DOWN, buff = MED_SMALL_BUFF+SMALL_BUFF
                ).next_to(cross_components, LEFT),
                new_ps
            ),
            *list(map(FadeOut, to_fade))
        )
        self.play(*[
            Write(TexMobject("=").next_to(p, buff = 2*SMALL_BUFF))
            for p in new_ps
        ])
        equals = self.get_mobjects_from_last_animation()
        self.wait(2)

        everything = everything.copy()
        self.play(
            FadeOut(VGroup(*self.get_mobjects())),
            Animation(everything)
        )
        self.clear()
        self.add(everything)

    def ask_question(self):
        everything = VGroup(*self.get_mobjects())
        p_tex = "$%s$"%get_vect_tex("p")
        question = TextMobject(
            "What vector", 
            p_tex, 
            "has \\\\ the property that"
        )
        question.to_edge(UP)
        question.set_color(YELLOW)
        question.set_color_by_tex(p_tex, P_COLOR)
        everything.target = everything.copy()
        everything.target.next_to(
            question, DOWN, buff = MED_SMALL_BUFF
        )
        self.play(
            MoveToTarget(everything),
            Write(question)
        )
        self.wait()

class WhyAreWeDoingThis(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Um...why are \\\\ we doing this?",
            target_mode = "confused"
        )
        self.random_blink()
        self.play(self.get_teacher().change_mode, "erm")
        self.change_student_modes("plain", "confused", "raise_left_hand")
        self.random_blink()
        self.change_student_modes("pondering", "confused", "raise_left_hand")
        self.random_blink(5)

class ThreeDTripleCrossProduct(Scene):
    pass #Simple parallelepiped

class ThreeDMovingVariableVector(Scene):
    pass #white u moves around

class ThreeDMovingVariableVectorWithCrossShowing(Scene):
    pass #white u moves around, red p is present

class NowForTheCoolPart(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Now for the\\\\", 
            "cool part"
        )
        self.change_student_modes(*["happy"]*3)
        self.random_blink(2)
        self.teacher_says(
            "Let's answer the same question,\\\\",
            "but this time geometrically"
        )
        self.change_student_modes(*["pondering"]*3)
        self.random_blink(2)

class ThreeDDotProductProjection(Scene):
    pass #

class DotProductWords(Scene):
    def construct(self):
        p_tex = "$%s$"%get_vect_tex("p")
        p_mob = TextMobject(p_tex)
        p_mob.scale(1.5)
        p_mob.set_color(P_COLOR)
        input_array = Matrix(list("xyz"))
        dot_product = VGroup(p_mob, Dot(radius = 0.07), input_array)
        dot_product.arrange(buff = MED_SMALL_BUFF/2)
        equals = TexMobject("=")
        dot_product.next_to(equals, LEFT)
        words = VGroup(*it.starmap(TextMobject, [
            ("(Length of projection)",),
            ("(Length of ", p_tex, ")",)
        ]))
        times = TexMobject("\\times")
        words[1].set_color_by_tex(p_tex, P_COLOR)
        words[0].next_to(equals, RIGHT)
        words[1].next_to(words[0], DOWN, aligned_edge = LEFT)
        times.next_to(words[0], RIGHT)

        everyone = VGroup(dot_product, equals, times, words)
        everyone.center().set_width(FRAME_X_RADIUS - 1)
        self.add(dot_product)
        self.play(Write(equals))
        self.play(Write(words[0]))
        self.wait()
        self.play(
            Write(times),
            Write(words[1])
        )
        self.wait()

class ThreeDProjectToPerpendicular(Scene):
    pass #

class GeometricVolumeWords(Scene):
    def construct(self):
        v_tex, w_tex = [
            "$%s$"%s
            for s in get_vect_tex(*"vw")
        ]

        words = VGroup(
            TextMobject("(Area of", "parallelogram", ")$\\times$"),
            TextMobject(
                "(Component of $%s$"%matrix_to_tex_string(list("xyz")),
                "perpendicular to", v_tex, "and", w_tex, ")"
            )
        )
        words[0].set_color_by_tex("parallelogram", BLUE)
        words[1].set_color_by_tex(v_tex, ORANGE)
        words[1].set_color_by_tex(w_tex, W_COLOR)
        words.arrange(RIGHT)
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(DOWN, buff = SMALL_BUFF)
        for word in words:
            self.play(Write(word))
            self.wait()

class WriteXYZ(Scene):
    def construct(self):
        self.play(Write(Matrix(list("xyz"))))
        self.wait()

class ThreeDDotProductWithCross(Scene):
    pass 

class CrossVectorEmphasisWords(Scene):
    def construct(self):
        v_tex, w_tex = ["$%s$"%s for s in get_vect_tex(*"vw")]
        words = [
            TextMobject("Perpendicular to", v_tex, "and", w_tex),
            TextMobject("Length = (Area of ", "parallelogram", ")")
        ]
        for word in words:
            word.set_color_by_tex(v_tex, ORANGE)
            word.set_color_by_tex(w_tex, W_COLOR)
            word.set_color_by_tex("parallelogram", BLUE)
            self.play(Write(word))
            self.wait()
            self.play(FadeOut(word))

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: Change of basis
        """)
        title.to_edge(UP, buff = MED_SMALL_BUFF/2)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()

class ChangeOfBasisPreview(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "secondary_line_ratio" : 0
        },
        "t_matrix" : [[2, 1], [-1, 1]],
        "i_target_color" : YELLOW,
        "j_target_color" : MAROON_B,
        "sum_color" : PINK,
        "vector" : [-1, 2],
    }
    def construct(self):
        randy = Randolph()
        pinky = Mortimer(color = PINK)
        randy.to_corner(DOWN+LEFT)
        pinky.to_corner(DOWN+RIGHT)
        self.plane.fade()

        self.add_foreground_mobject(randy, pinky)
        coords = Matrix(self.vector)
        coords.add_to_back(BackgroundRectangle(coords))
        self.add_foreground_mobject(coords)
        coords.move_to(
            randy.get_corner(UP+RIGHT),
            aligned_edge = DOWN+LEFT
        )
        coords.target = coords.copy()
        coords.target.move_to(
            pinky.get_corner(UP+LEFT),
            aligned_edge = DOWN+RIGHT
        )
        self.play(
            Write(coords),
            randy.change_mode, "speaking"
        )
        self.scale_basis_vectors()
        self.apply_transposed_matrix(
            self.t_matrix,
            added_anims = [
                MoveToTarget(coords),
                ApplyMethod(pinky.change_mode, "speaking"),
                ApplyMethod(randy.change_mode, "plain"),
            ]
        )
        self.play(
            randy.change_mode, "erm",
            self.i_hat.set_color, self.i_target_color,
            self.j_hat.set_color, self.j_target_color,
        )
        self.i_hat.color = self.i_target_color
        self.j_hat.color = self.j_target_color
        self.scale_basis_vectors()

    def scale_basis_vectors(self):
        for vect in self.i_hat, self.j_hat:
            vect.save_state()
        self.play(self.i_hat.scale, self.vector[0])
        self.play(self.j_hat.scale, self.vector[1])
        self.play(self.j_hat.shift, self.i_hat.get_end())
        sum_vect = Vector(self.j_hat.get_end(), color = self.sum_color)
        self.play(ShowCreation(sum_vect))
        self.wait(2)
        self.play(
            FadeOut(sum_vect),
            self.i_hat.restore,
            self.j_hat.restore,
        )
        self.wait()














