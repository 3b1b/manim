from manimlib.imports import *
from old_projects.eola.chapter1 import plane_wave_homotopy

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject("""
            Mathematics requires a small dose, not of genius, 
            but of an imaginative freedom which, in a larger 
            dose, would be insanity.
        """)
        words.to_edge(UP)    
        for mob in words.submobjects[49:49+18]:
            mob.set_color(GREEN)
        author = TextMobject("-Angus K. Rodgers")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(3)
        self.play(Write(author, run_time = 3))
        self.wait()


class CoordinatesWereFamiliar(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says("I know this already")
        self.random_blink()
        self.teacher_says("Ah, but there is a subtlety")
        self.random_blink()
        self.wait()


class CoordinatesAsScalars(VectorScene):
    CONFIG = {
        "vector_coords" : [3, -2]
    }

    def construct(self):
        self.lock_in_faded_grid()

        vector = self.add_vector(self.vector_coords)
        array, x_line, y_line = self.vector_to_coords(vector)
        self.add(array)
        self.wait()
        new_array = self.general_idea_of_scalars(array, vector)
        self.scale_basis_vectors(new_array)
        self.show_symbolic_sum(new_array, vector)

    def general_idea_of_scalars(self, array, vector):
        starting_mobjects = self.get_mobjects()

        title = TextMobject("Think of each coordinate as a scalar")
        title.to_edge(UP)

        x, y = array.get_mob_matrix().flatten()
        new_x = x.copy().scale(2).set_color(X_COLOR)
        new_x.move_to(3*LEFT+2*UP)
        new_y = y.copy().scale(2).set_color(Y_COLOR)
        new_y.move_to(3*RIGHT+2*UP)

        i_hat, j_hat = self.get_basis_vectors()
        new_i_hat = Vector(
            self.vector_coords[0]*i_hat.get_end(), 
            color = X_COLOR
        )
        new_j_hat = Vector(
            self.vector_coords[1]*j_hat.get_end(), 
            color = Y_COLOR
        )
        VMobject(i_hat, new_i_hat).shift(3*LEFT)
        VMobject(j_hat, new_j_hat).shift(3*RIGHT)

        new_array = Matrix([new_x.copy(), new_y.copy()])
        new_array.scale(0.5)
        new_array.shift(
            -new_array.get_boundary_point(-vector.get_end()) + \
            1.1*vector.get_end()
        )

        self.remove(*starting_mobjects)
        self.play(
            Transform(x, new_x),
            Transform(y, new_y),
            Write(title),
        )
        self.play(FadeIn(i_hat), FadeIn(j_hat))
        self.wait()
        self.play(
            Transform(i_hat, new_i_hat),
            Transform(j_hat, new_j_hat),
            run_time = 3
        )
        self.wait()
        starting_mobjects.remove(array)

        new_x, new_y = new_array.get_mob_matrix().flatten()
        self.play(
            Transform(x, new_x),
            Transform(y, new_y),
            FadeOut(i_hat),
            FadeOut(j_hat),
            Write(new_array.get_brackets()),
            FadeIn(VMobject(*starting_mobjects)),
            FadeOut(title)
        )
        self.remove(x, y)
        self.add(new_array)
        return new_array

    def scale_basis_vectors(self, new_array):
        i_hat, j_hat = self.get_basis_vectors()
        self.add_vector(i_hat)
        i_hat_label = self.label_vector(
            i_hat, "\\hat{\\imath}", 
            color = X_COLOR, 
            label_scale_factor = 1
        )
        self.add_vector(j_hat)
        j_hat_label = self.label_vector(
            j_hat, "\\hat{\\jmath}", 
            color = Y_COLOR, 
            label_scale_factor = 1
        )
        self.wait()

        x, y = new_array.get_mob_matrix().flatten()
        for coord, v, label, factor, shift_right in [
            (x, i_hat, i_hat_label, self.vector_coords[0], False), 
            (y, j_hat, j_hat_label, self.vector_coords[1], True)
            ]:
            faded_v = v.copy().fade(0.7)
            scaled_v = Vector(factor*v.get_end(), color = v.get_color())

            scaled_label = VMobject(coord.copy(), label.copy())
            scaled_label.arrange(RIGHT, buff = 0.1)
            scaled_label.move_to(label, DOWN+RIGHT)
            scaled_label.shift((scaled_v.get_end()-v.get_end())/2)
            coord_copy = coord.copy()
            self.play(
                Transform(v.copy(), faded_v),
                Transform(v, scaled_v),
                Transform(VMobject(coord_copy, label), scaled_label),
            )
            self.wait()
            if shift_right:
                group = VMobject(v, coord_copy, label)
                self.play(ApplyMethod(
                    group.shift, self.vector_coords[0]*RIGHT
                ))
        self.wait()


    def show_symbolic_sum(self, new_array, vector):
        new_mob = TexMobject([
            "(%d)\\hat{\\imath}"%self.vector_coords[0], 
            "+", 
            "(%d)\\hat{\\jmath}"%self.vector_coords[1]
        ])
        new_mob.move_to(new_array)
        new_mob.shift_onto_screen()
        i_hat, plus, j_hat = new_mob.split()
        i_hat.set_color(X_COLOR)
        j_hat.set_color(Y_COLOR)

        self.play(Transform(new_array, new_mob))
        self.wait()
        


class CoordinatesAsScalarsExample2(CoordinatesAsScalars):
    CONFIG = {
        "vector_coords" : [-5, 2]
    }

    def construct(self):
        self.lock_in_faded_grid()

        basis_vectors = self.get_basis_vectors()
        labels = self.get_basis_vector_labels()
        self.add(*basis_vectors)
        self.add(*labels)
        text = TextMobject("""
            $\\hat{\\imath}$ and $\\hat{\\jmath}$ 
            are the ``basis vectors'' \\\\
            of the $xy$ coordinate system
        """)
        text.set_width(FRAME_X_RADIUS-1)
        text.to_corner(UP+RIGHT)
        VMobject(*text.split()[:2]).set_color(X_COLOR)
        VMobject(*text.split()[5:7]).set_color(Y_COLOR)
        self.play(Write(text))
        self.wait(2)
        self.remove(*basis_vectors + labels)
        CoordinatesAsScalars.construct(self)


class WhatIfWeChoseADifferentBasis(Scene):
    def construct(self):
        self.play(Write(
            "What if we chose different basis vectors?",
            run_time = 2
        ))
        self.wait(2)

class ShowVaryingLinearCombinations(VectorScene):
    CONFIG = {
        "vector1" : [1, 2],
        "vector2" : [3, -1],
        "vector1_color" : MAROON_C,
        "vector2_color" : BLUE,
        "vector1_label" : "v",
        "vector2_label" : "w",
        "sum_color" : PINK,
        "scalar_pairs" : [
            (1.5, 0.6),
            (0.7, 1.3),
            (-1, -1.5),
            (1, -1.13),
            (1.25, 0.5),
            (-0.8, 1.3),
        ], 
        "leave_sum_vector_copies" : False,
        "start_with_non_sum_scaling" : True,
        "finish_with_standard_basis_comparison" : True,
        "finish_by_drawing_lines" : False,
    }
    def construct(self):
        self.lock_in_faded_grid()
        v1 = self.add_vector(self.vector1, color = self.vector1_color)
        v2 = self.add_vector(self.vector2, color = self.vector2_color)
        v1_label = self.label_vector(
            v1, self.vector1_label, color = self.vector1_color, 
            buff_factor = 3
        )
        v2_label = self.label_vector(
            v2, self.vector2_label, color = self.vector2_color, 
            buff_factor = 3
        )
        label_anims = [
            MaintainPositionRelativeTo(label, v)
            for v, label in [(v1, v1_label), (v2, v2_label)]
        ]
        scalar_anims = self.get_scalar_anims(v1, v2, v1_label, v2_label)
        self.last_scalar_pair = (1, 1)

        if self.start_with_non_sum_scaling:
            self.initial_scaling(v1, v2, label_anims, scalar_anims)
        self.show_sum(v1, v2, label_anims, scalar_anims)
        self.scale_with_sum(v1, v2, label_anims, scalar_anims)
        if self.finish_with_standard_basis_comparison:
            self.standard_basis_comparison(label_anims, scalar_anims)
        if self.finish_by_drawing_lines:
            self.draw_lines(v1, v2, label_anims, scalar_anims)

    def get_scalar_anims(self, v1, v2, v1_label, v2_label):
        def get_val_func(vect):
            original_vect = np.array(vect.get_end()-vect.get_start())
            square_norm = get_norm(original_vect)**2
            return lambda a : np.dot(
                original_vect, vect.get_end()-vect.get_start()
            )/square_norm
        return [
            RangingValues(
                tracked_mobject = label,
                tracked_mobject_next_to_kwargs = {
                    "direction" : LEFT,
                    "buff" : 0.1
                },
                scale_factor = 0.75,
                value_function = get_val_func(v)
            )
            for v, label in [(v1, v1_label), (v2, v2_label)]
        ]

    def get_rate_func_pair(self):
        return [
            squish_rate_func(smooth, a, b) 
            for a, b in [(0, 0.7), (0.3, 1)]
        ] 

    def initial_scaling(self, v1, v2, label_anims, scalar_anims):
        scalar_pair = self.scalar_pairs.pop(0)
        anims = [
            ApplyMethod(v.scale, s, rate_func = rf)
            for v, s, rf in zip(
                [v1, v2],
                scalar_pair,
                self.get_rate_func_pair()
            )
        ]
        anims += [
            ApplyMethod(v.copy().fade, 0.7)
            for v in (v1, v2)
        ]
        anims += label_anims + scalar_anims
        self.play(*anims, **{"run_time" : 2})
        self.wait()
        self.last_scalar_pair = scalar_pair

    def show_sum(self, v1, v2, label_anims, scalar_anims):
        self.play(
            ApplyMethod(v2.shift, v1.get_end()),
            *label_anims + scalar_anims
        )
        self.sum_vector = self.add_vector(
            v2.get_end(), color = self.sum_color
        )
        self.wait()

    def scale_with_sum(self, v1, v2, label_anims, scalar_anims):
        v2_anim, sum_anim = self.get_sum_animations(v1, v2)
        while self.scalar_pairs:
            scalar_pair = self.scalar_pairs.pop(0)
            anims = [
                ApplyMethod(v.scale, s/s_old, rate_func = rf)
                for v, s, s_old, rf in zip(
                    [v1, v2], 
                    scalar_pair, 
                    self.last_scalar_pair,
                    self.get_rate_func_pair()
                )
            ]
            anims += [v2_anim, sum_anim] + label_anims + scalar_anims
            self.play(*anims, **{"run_time" : 2})
            if self.leave_sum_vector_copies:
                self.add(self.sum_vector.copy())
            self.wait()
            self.last_scalar_pair = scalar_pair

    def get_sum_animations(self, v1, v2):
        v2_anim = UpdateFromFunc(
            v2, lambda m : m.shift(v1.get_end()-m.get_start())
        )
        sum_anim = UpdateFromFunc(
            self.sum_vector, 
            lambda v : v.put_start_and_end_on(v1.get_start(), v2.get_end())
        )
        return v2_anim, sum_anim

    def standard_basis_comparison(self, label_anims, scalar_anims):
        everything = self.get_mobjects()
        everything.remove(self.sum_vector)
        everything = VMobject(*everything)
        alt_coords = [a.mobject for a in scalar_anims]
        array = Matrix([
            mob.copy().set_color(color)
            for mob, color in zip(
                alt_coords, 
                [self.vector1_color, self.vector2_color]
            )
        ])
        array.scale(0.8)
        array.to_edge(UP)
        array.shift(RIGHT)
        brackets = array.get_brackets()

        anims = [
            Transform(*pair)
            for pair in zip(alt_coords, array.get_mob_matrix().flatten())
        ]
        # anims += [
        #     FadeOut(a.mobject)
        #     for a in label_anims
        # ]
        self.play(*anims + [Write(brackets)])
        self.wait()
        self.remove(brackets, *alt_coords)
        self.add(array)
        self.play(
            FadeOut(everything), 
            Animation(array),
        )

        self.add_axes(animate = True)
        ij_array, x_line, y_line = self.vector_to_coords(
            self.sum_vector, integer_labels = False
        )
        self.add(ij_array, x_line, y_line)
        x, y = ij_array.get_mob_matrix().flatten()
        self.play(
            ApplyMethod(x.set_color, X_COLOR),
            ApplyMethod(y.set_color, Y_COLOR),
        )
        neq = TexMobject("\\neq")
        neq.next_to(array)
        self.play(
            ApplyMethod(ij_array.next_to, neq),
            Write(neq)
        )
        self.wait()

    def draw_lines(self, v1, v2, label_anims, scalar_anims):
        sum_anims = self.get_sum_animations(v1, v2)
        aux_anims = list(sum_anims) + label_anims + scalar_anims

        scale_factor = 2
        for w1, w2 in (v2, v1), (v1, v2):
            w1_vect = w1.get_end()-w1.get_start()
            w2_vect = w2.get_end()-w2.get_start()
            for num in scale_factor, -1, -1./scale_factor:
                curr_tip = self.sum_vector.get_end()
                line = Line(ORIGIN, curr_tip)
                self.play(
                    ApplyMethod(w2.scale, num), 
                    UpdateFromFunc(
                        line, lambda l : l.put_start_and_end_on(curr_tip, self.sum_vector.get_end())
                    ),
                    *aux_anims
                )
                self.add(line, v2)
            self.wait()



class AltShowVaryingLinearCombinations(ShowVaryingLinearCombinations):
    CONFIG = {
        "scalar_pairs" : [
            (1.5, 0.3),
            (0.64, 1.3),
            (-1, -1.5),
            (1, 1.13),
            (1.25, 0.5),
            (-0.8, 1.14),
        ], 
        "finish_with_standard_basis_comparison" : False
    }


class NameLinearCombinations(Scene):
    def construct(self):
        v_color = MAROON_C
        w_color = BLUE
        words = TextMobject([
            "``Linear combination'' of",
            "$\\vec{\\textbf{v}}$",
            "and",
            "$\\vec{\\textbf{w}}$"
        ])
        words.split()[1].set_color(v_color)
        words.split()[3].set_color(w_color)
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(UP)

        equation = TexMobject([
            "a", "\\vec{\\textbf{v}}", "+", "b", "\\vec{\\textbf{w}}"
        ])
        equation.arrange(buff = 0.1, aligned_edge = DOWN)
        equation.split()[1].set_color(v_color)
        equation.split()[4].set_color(w_color)
        a, b = np.array(equation.split())[[0, 3]]
        equation.scale(2)
        equation.next_to(words, DOWN, buff = 1)

        scalars_word = TextMobject("Scalars")
        scalars_word.scale(1.5)
        scalars_word.next_to(equation, DOWN, buff = 2)
        arrows = [
            Arrow(scalars_word, letter)
            for letter in (a, b)
        ]

        self.add(equation)
        self.play(Write(words))
        self.play(
            ShowCreation(VMobject(*arrows)),
            Write(scalars_word)
        )
        self.wait(2)


class LinearCombinationsDrawLines(ShowVaryingLinearCombinations):
    CONFIG = {
        "scalar_pairs" : [
            (1.5, 0.6),
            (0.7, 1.3),
            (1, 1),
        ], 
        "start_with_non_sum_scaling" : False,
        "finish_with_standard_basis_comparison" : False,
        "finish_by_drawing_lines" : True,
    }


class LinearCombinationsWithSumCopies(ShowVaryingLinearCombinations):
    CONFIG = {
        "scalar_pairs" : [
            (1.5, 0.6),
            (0.7, 1.3),
            (-1, -1.5),
            (1, -1.13),
            (1.25, 0.5),
            (-0.8, 1.3),
            (-0.9, 1.4),
            (0.9, 2),
        ], 
        "leave_sum_vector_copies" : True,
        "start_with_non_sum_scaling" : False,
        "finish_with_standard_basis_comparison" : False,
        "finish_by_drawing_lines" : False,
    }



class LinearDependentVectors(ShowVaryingLinearCombinations):
    CONFIG = {
        "vector1" : [1, 2],
        "vector2" : [0.5, 1],
        "vector1_color" : MAROON_C,
        "vector2_color" : BLUE,
        "vector1_label" : "v",
        "vector2_label" : "w",
        "sum_color" : PINK,
        "scalar_pairs" : [
            (1.5, 0.6),
            (0.7, 1.3),
            (-1, -1.5),
            (1.25, 0.5),
            (-0.8, 1.3),
            (-0.9, 1.4),
            (0.9, 2),
        ], 
        "leave_sum_vector_copies" : False,
        "start_with_non_sum_scaling" : False,
        "finish_with_standard_basis_comparison" : False,
        "finish_by_drawing_lines" : False,
    }

    def get_sum_animations(self, v1, v2):
        v2_anim, sum_anim = ShowVaryingLinearCombinations.get_sum_animations(self, v1, v2) 
        self.remove(self.sum_vector)
        return v2_anim, Animation(VMobject())

class WhenVectorsLineUp(LinearDependentVectors):
    CONFIG = {
        "vector1" : [3, 2],
        "vector2" : [1.5, 1],
        "scalar_pairs" : [
            (1.5, 0.6),
            (0.7, 1.3),
        ], 
    }    

class AnimationUnderSpanDefinition(ShowVaryingLinearCombinations):
    CONFIG = {
        "scalar_pairs" : [
            (1.5, 0.6),
            (0.7, 1.3),
            (-1, -1.5),
            (1.25, 0.5),
            (0.8, 1.3),
            (0.93, -1.4),
            (-2, -0.5),
        ], 
        "leave_sum_vector_copies" : True,
        "start_with_non_sum_scaling" : False,
        "finish_with_standard_basis_comparison" : False,
        "finish_by_drawing_lines" : False,
    }


class BothVectorsCouldBeZero(VectorScene):
    def construct(self):
        plane = self.add_plane()
        plane.fade(0.7)
        v1 = self.add_vector([1, 2], color = MAROON_C)
        v2 = self.add_vector([3, -1], color = BLUE)
        self.play(Transform(v1, Dot(ORIGIN)))
        self.play(Transform(v2, Dot(ORIGIN)))
        self.wait()


class DefineSpan(Scene):
    def construct(self):
        v_color = MAROON_C
        w_color = BLUE

        definition = TextMobject("""
            The ``span'' of $\\vec{\\textbf{v}}$ and 
            $\\vec{\\textbf{w}}$ is the \\\\ set of all their
            linear combinations.
        """)
        definition.set_width(FRAME_WIDTH-1)
        definition.to_edge(UP)
        def_mobs = np.array(definition.split())
        VMobject(*def_mobs[4:4+4]).set_color(PINK)
        VMobject(*def_mobs[11:11+2]).set_color(v_color)
        VMobject(*def_mobs[16:16+2]).set_color(w_color)
        VMobject(*def_mobs[-19:-1]).set_color(YELLOW)

        equation = TexMobject([
            "a", "\\vec{\\textbf{v}}", "+", "b", "\\vec{\\textbf{w}}"
        ])
        equation.arrange(buff = 0.1, aligned_edge = DOWN)
        equation.split()[1].set_color(v_color)
        equation.split()[4].set_color(w_color)
        a, b = np.array(equation.split())[[0, 3]]
        equation.scale(2)
        equation.next_to(definition, DOWN, buff = 1)

        vary_words = TextMobject(
            "Let $a$ and $b$ vary \\\\ over all real numbers"
        )
        vary_words.scale(1.5)
        vary_words.next_to(equation, DOWN, buff = 2)
        arrows = [
            Arrow(vary_words, letter)
            for letter in (a, b)
        ]

        self.play(Write(definition))
        self.play(Write(equation))
        self.wait()
        self.play(
            FadeIn(vary_words),
            ShowCreation(VMobject(*arrows))
        )
        self.wait()


class VectorsVsPoints(Scene):
    def construct(self):
        self.play(Write("Vectors vs. Points"))
        self.wait(2)


class VectorsToDotsScene(VectorScene):
    CONFIG = {
        "num_vectors" : 16,
        "start_color" : PINK,
        "end_color" : BLUE_E,
    }
    def construct(self):
        self.lock_in_faded_grid()

        vectors = self.get_vectors()
        colors = Color(self.start_color).range_to(
            self.end_color, len(vectors)
        )
        for vect, color in zip(vectors, colors):
            vect.set_color(color)
        prototype_vector = vectors[3*len(vectors)/4]

        vector_group = VMobject(*vectors)
        self.play(
            ShowCreation(
                vector_group, 
                run_time = 3
            )
        )
        vectors.sort(key=lambda v: v.get_length())
        self.add(*vectors)
        def v_to_dot(vector):
            return Dot(vector.get_end(), fill_color = vector.get_stroke_color())
        self.wait()
        vectors.remove(prototype_vector)
        self.play(*list(map(FadeOut, vectors))+[Animation(prototype_vector)])
        self.remove(vector_group)
        self.add(prototype_vector)
        self.wait()
        self.play(Transform(prototype_vector, v_to_dot(prototype_vector)))
        self.wait()
        self.play(*list(map(FadeIn, vectors)) + [Animation(prototype_vector)])
        rate_functions = [
            squish_rate_func(smooth, float(x)/(len(vectors)+2), 1)
            for x in range(len(vectors))
        ]
        self.play(*[
            Transform(v, v_to_dot(v), rate_func = rf, run_time = 2) 
            for v, rf in zip(vectors, rate_functions)
        ])
        self.wait()
        self.remove(prototype_vector)
        self.play_final_animation(vectors, rate_functions)
        self.wait()

    def get_vectors(self):
        raise Exception("Not implemented")

    def play_final_animation(self, vectors, rate_functions):
        raise Exception("Not implemented")


class VectorsOnALine(VectorsToDotsScene):
    def get_vectors(self):
        return [
            Vector(a*np.array([1.5, 1]))
            for a in np.linspace(
                -FRAME_Y_RADIUS, FRAME_Y_RADIUS, self.num_vectors
            )
        ]

    def play_final_animation(self, vectors, rate_functions):
        line_copies = [
            Line(vectors[0].get_end(), vectors[-1].get_end())
            for v in vectors
        ]
        self.play(*[
            Transform(v, mob, rate_func = rf, run_time = 2)
            for v, mob, rf in zip(vectors, line_copies, rate_functions)
        ])


class VectorsInThePlane(VectorsToDotsScene):
    CONFIG = {
        "num_vectors" : 16,
        "start_color" : PINK,
        "end_color" : BLUE_E,
    }
    def get_vectors(self):
        return [
            Vector([x, y])
            for x in np.arange(-int(FRAME_X_RADIUS)-0.5, int(FRAME_X_RADIUS)+0.5)
            for y in np.arange(-int(FRAME_Y_RADIUS)-0.5, int(FRAME_Y_RADIUS)+0.5)
        ]

    def play_final_animation(self, vectors, rate_functions):
        h_line = Line(
            FRAME_X_RADIUS*RIGHT, FRAME_X_RADIUS*LEFT,
            stroke_width = 0.5,
            color = BLUE_E
        )
        v_line = Line(
            FRAME_Y_RADIUS*UP, FRAME_Y_RADIUS*DOWN,
            stroke_width = 0.5,
            color = BLUE_E
        )
        line_pairs = [
            VMobject(h_line.copy().shift(y), v_line.copy().shift(x))
            for v in vectors
            for x, y, z in [v.get_center()]
        ]
        plane = NumberPlane()
        self.play(
            ShowCreation(plane),
            *[
                Transform(v, p, rate_func = rf) 
                for v, p, rf in zip(vectors, line_pairs, rate_functions)
            ]
        )
        self.remove(*vectors)
        self.wait()


class HowToThinkVectorsVsPoint(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        bubble = randy.get_bubble(height = 3.8)
        text1 = TextMobject("Think of individual vectors as arrows")
        text2 = TextMobject("Think of sets of vectors as points")
        for text in text1, text2:
            text.to_edge(UP)

        single_vector = Vector([2, 1])
        vector_group = VMobject(*[
            Vector([x, 1])
            for x in np.linspace(-2, 2, 5)
        ])
        bubble.position_mobject_inside(single_vector)
        bubble.position_mobject_inside(vector_group)
        dots = VMobject(*[
            Dot(v.get_end())
            for v in vector_group.split()
        ])

        self.add(randy)
        self.play(
            ApplyMethod(randy.change_mode, "pondering"),
            ShowCreation(bubble)
        )
        self.play(FadeIn(text1))
        self.play(ShowCreation(single_vector))
        self.wait(3)
        self.play(
            Transform(text1, text2),
            Transform(single_vector, vector_group)
        )
        self.remove(single_vector)
        self.add(vector_group)
        self.wait()
        self.play(Transform(vector_group, dots))
        self.wait()


class IntroduceThreeDSpan(Scene):
    pass

class AskAboutThreeDSpan(Scene):
    def construct(self):
        self.play(Write("What does the span of two 3d vectors look like?"))
        self.wait(2)

class ThreeDVectorSpan(Scene):
    pass


class LinearCombinationOfThreeVectors(Scene):
    pass

class VaryingLinearCombinationOfThreeVectors(Scene):
    pass

class LinearCombinationOfThreeVectorsText(Scene):
    def construct(self):
        text = TextMobject("""
            Linear combination of 
            $\\vec{\\textbf{v}}$, 
            $\\vec{\\textbf{w}}$, and
            $\\vec{\\textbf{u}}$:
        """)
        VMobject(*text.split()[-12:-10]).set_color(MAROON_C)
        VMobject(*text.split()[-9:-7]).set_color(BLUE)
        VMobject(*text.split()[-3:-1]).set_color(RED_C)
        VMobject(*text.split()[:17]).set_color(GREEN)        
        text.set_width(FRAME_WIDTH - 1)
        text.to_edge(UP)

        equation = TextMobject("""$
            a\\vec{\\textbf{v}} + 
            b\\vec{\\textbf{w}} + 
            c\\vec{\\textbf{u}}
        $""")
        VMobject(*equation.split()[-10:-8]).set_color(MAROON_C)
        VMobject(*equation.split()[-6:-4]).set_color(BLUE)
        VMobject(*equation.split()[-2:]).set_color(RED_C)

        a, b, c = np.array(equation.split())[[0, 4, 8]]

        equation.scale(1.5)
        equation.next_to(text, DOWN, buff = 1)

        span_comment = TextMobject("For span, let these constants vary")
        span_comment.scale(1.5)
        span_comment.next_to(equation, DOWN, buff = 2)
        VMobject(*span_comment.split()[3:7]).set_color(YELLOW)
        arrows = VMobject(*[
            Arrow(span_comment, var)
            for var in (a, b, c)
        ])

        self.play(Write(text))
        self.play(Write(equation))
        self.wait()
        self.play(
            ShowCreation(arrows),
            Write(span_comment)
        )
        self.wait()


class ThirdVectorOnSpanOfFirstTwo(Scene):
    pass

class ThirdVectorOutsideSpanOfFirstTwo(Scene):
    pass

class SpanCasesWords(Scene):
    def construct(self):
        words1 = TextMobject("""
            Case 1: $\\vec{\\textbf{u}}$ is in the span of
            $\\vec{\\textbf{v}}$ and $\\vec{\\textbf{u}}$
        """)
        VMobject(*words1.split()[6:8]).set_color(RED_C)
        VMobject(*words1.split()[-7:-5]).set_color(MAROON_C)
        VMobject(*words1.split()[-2:]).set_color(BLUE)

        words2 = TextMobject("""
            Case 2: $\\vec{\\textbf{u}}$ is not in the span of
            $\\vec{\\textbf{v}}$ and $\\vec{\\textbf{u}}$
        """)
        VMobject(*words2.split()[6:8]).set_color(RED_C)
        VMobject(*words2.split()[-7:-5]).set_color(MAROON_C)
        VMobject(*words2.split()[-2:]).set_color(BLUE)
        VMobject(*words2.split()[10:13]).set_color(RED)

        for words in words1, words2:
            words.set_width(FRAME_WIDTH - 1)
        self.play(Write(words1))
        self.wait()
        self.play(Transform(words1, words2))
        self.wait()



class LinearDependentWords(Scene):
    def construct(self):
        words1 = TextMobject([
            "$\\vec{\\textbf{v}}$", 
            "and",
            "$\\vec{\\textbf{w}}$",
            "are",
            "``Linearly dependent'' ",
        ])
        v, _and, w, are, rest = words1.split()
        v.set_color(MAROON_C)
        w.set_color(BLUE)
        rest.set_color(YELLOW)

        words2 = TextMobject([
            "$\\vec{\\textbf{v}}$,", 
            "$\\vec{\\textbf{w}}$",
            "and",
            "$\\vec{\\textbf{u}}$",
            "are",
            "``Linearly dependent'' ",
        ])
        v, w, _and, u, are, rest = words2.split()
        v.set_color(MAROON_C)
        w.set_color(BLUE)
        u.set_color(RED_C)
        rest.set_color(YELLOW)

        for words in words1, words2:
            words.set_width(FRAME_WIDTH - 1)

        self.play(Write(words1))
        self.wait()
        self.play(Transform(words1, words2))
        self.wait()


class LinearDependentEquations(Scene):
    def construct(self):
        title = TextMobject("``Linearly dependent'' ")
        title.set_color(YELLOW)
        title.scale(2)
        title.to_edge(UP)
        self.add(title)

        equation1 = TexMobject([
            "\\vec{\\textbf{w}}",
            "=",
            "a",
            "\\vec{\\textbf{v}}",
        ])
        w, eq, a, v = equation1.split()
        w.set_color(BLUE)
        v.set_color(MAROON_C)
        equation1.scale(2)
        eq1_copy = equation1.copy()

        low_words1 = TextMobject("For some value of $a$")
        low_words1.scale(2)
        low_words1.to_edge(DOWN)
        arrow = Arrow(low_words1, a)
        arrow_copy = arrow.copy()

        equation2 = TexMobject([
            "\\vec{\\textbf{u}}",
            "=",
            "a",
            "\\vec{\\textbf{v}}",
            "+",
            "b",
            "\\vec{\\textbf{w}}",
        ])
        u, eq, a, v, plus, b, w = equation2.split()
        u.set_color(RED)
        w.set_color(BLUE)
        v.set_color(MAROON_C)
        equation2.scale(2)
        eq2_copy = equation2.copy()

        low_words2 = TextMobject("For some values of a and b")
        low_words2.scale(2)
        low_words2.to_edge(DOWN)
        arrows = VMobject(*[
            Arrow(low_words2, var)
            for var in (a, b)
        ])

        self.play(Write(equation1))
        self.play(
            ShowCreation(arrow),
            Write(low_words1)
        )
        self.wait()

        self.play(
            Transform(equation1, equation2),
            Transform(low_words1, low_words2),
            Transform(arrow, arrows)
        )
        self.wait(2)

        new_title = TextMobject("``Linearly independent'' ")
        new_title.set_color(GREEN)
        new_title.replace(title)

        for eq_copy in eq1_copy, eq2_copy:
            neq = TexMobject("\\neq")
            neq.replace(eq_copy.submobjects[1])
            eq_copy.submobjects[1] = neq

        new_low_words1 = TextMobject(["For", "all", "values of a"])
        new_low_words2 = TextMobject(["For", "all", "values of a and b"])
        for low_words in new_low_words1, new_low_words2:
            low_words.split()[1].set_color(GREEN)
            low_words.scale(2)
            low_words.to_edge(DOWN)

        self.play(
            Transform(title, new_title),
            Transform(equation1, eq1_copy),
            Transform(arrow, arrow_copy),
            Transform(low_words1, new_low_words1)
        )
        self.wait()
        self.play(
            Transform(equation1, eq2_copy),
            Transform(arrow, arrows),
            Transform(low_words1, new_low_words2)
        )
        self.wait()



class AlternateDefOfLinearlyDependent(Scene):
    def construct(self):
        title1 = TextMobject([
            "$\\vec{\\textbf{v}}$,",
            "$\\vec{\\textbf{w}}$",
            "and",
            "$\\vec{\\textbf{u}}$",
            "are",
            "linearly dependent",
            "if",
        ])
        title2 = TextMobject([
            "$\\vec{\\textbf{v}}$,",
            "$\\vec{\\textbf{w}}$",
            "and",
            "$\\vec{\\textbf{u}}$",
            "are",
            "linearly independent",
            "if",
        ])
        for title in title1, title2:
            v, w, _and, u, are, ld, _if = title.split()
            v.set_color(MAROON_C)
            w.set_color(BLUE)
            u.set_color(RED_C)
            title.to_edge(UP)
        title1.split()[-2].set_color(YELLOW)
        title2.split()[-2].set_color(GREEN)

        subtitle = TextMobject("the only solution to")
        subtitle.next_to(title2, DOWN, aligned_edge = LEFT)

        self.add(title1)

        equations = self.get_equations()
        added_words1 = TextMobject(
            "where at least one of $a$, $b$ and $c$ is not $0$"
        )
        added_words2 = TextMobject(
            "is a = b = c = 0"
        )

        scalar_specification = TextMobject(
            "For some choice of $a$ and $b$"
        )
        scalar_specification.shift(1.5*DOWN)
        scalar_specification.add(*[
            Arrow(scalar_specification, equations[0].split()[i])
            for i in (2, 5)
        ])

        brace = Brace(VMobject(*equations[2].split()[2:]))
        brace_words = TextMobject("Linear combination")
        brace_words.next_to(brace, DOWN)

        equation = equations[0]
        for added_words in added_words1, added_words2:
            added_words.next_to(title, DOWN, buff = 3.5, aligned_edge = LEFT) 
        self.play(Write(equation))
        for i, new_eq in enumerate(equations):
            if i == 0:
                self.play(FadeIn(scalar_specification))
                self.wait(2)
                self.play(FadeOut(scalar_specification))
            elif i == 3:
                self.play(
                    GrowFromCenter(brace),
                    Write(brace_words)
                )
                self.wait(3)
                self.play(FadeOut(brace), FadeOut(brace_words))
            self.play(Transform(
                equation, new_eq, 
                path_arc = (np.pi/2 if i == 1 else 0)
            ))
            self.wait(3)
        self.play(Write(added_words1))
        self.wait(2)
        self.play(
            Transform(title1, title2),
            Write(subtitle),
            Transform(added_words1, added_words2),
        )
        self.wait(3)
        everything = VMobject(*self.get_mobjects())
        self.play(ApplyFunction(
            lambda m : m.scale(0.5).to_corner(UP+LEFT),
            everything
        ))
        self.wait()


    def get_equations(self):
        equation1 = TexMobject([
            "\\vec{\\textbf{u}}",
            "=",
            "a",
            "\\vec{\\textbf{v}}",
            "+",
            "b",
            "\\vec{\\textbf{w}}",
        ])
        u = equation1.split()[0]
        equation1.submobjects = list(it.chain(
            [VectorizedPoint(u.get_center())],
            equation1.submobjects[1:],
            [VectorizedPoint(u.get_left())],
            [u]
        ))
        equation2 = TexMobject([
            "\\left[\\begin{array}{c} 0 \\\\ 0 \\\\ 0 \\end{array} \\right]",
            "=",
            "a",
            "\\vec{\\textbf{v}}",
            "+",
            "b",
            "\\vec{\\textbf{w}}",
            "-",
            "\\vec{\\textbf{u}}",
        ])
        equation3 = TexMobject([
            "\\vec{\\textbf{0}}",
            "=",
            "a",
            "\\vec{\\textbf{v}}",
            "+",
            "b",
            "\\vec{\\textbf{w}}",
            "-",
            "\\vec{\\textbf{u}}",
        ])
        equation4 = TexMobject([
            "\\vec{\\textbf{0}}",
            "=",
            "0",
            "\\vec{\\textbf{v}}",
            "+",
            "0",
            "\\vec{\\textbf{w}}",
            "+0",
            "\\vec{\\textbf{u}}",
        ])
        equation5 = TexMobject([
            "\\vec{\\textbf{0}}",
            "=",
            "a",
            "\\vec{\\textbf{v}}",
            "+",
            "b",
            "\\vec{\\textbf{w}}",
            "+(-1)",
            "\\vec{\\textbf{u}}",
        ])
        equation5.split()[-2].set_color(YELLOW)
        equation6 = TexMobject([
            "\\vec{\\textbf{0}}",
            "=",
            "a",
            "\\vec{\\textbf{v}}",
            "+",
            "b",
            "\\vec{\\textbf{w}}",
            "+c",
            "\\vec{\\textbf{u}}",
        ])
        result = [equation1, equation2, equation3, equation4, equation5, equation6]
        for eq in result:
            eq.split()[3].set_color(MAROON_C)
            eq.split()[6].set_color(BLUE)
            eq.split()[-1].set_color(RED_C)
            eq.scale(1.5)
            eq.shift(UP)
        return result



class MathematiciansLikeToConfuse(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("""
            We wouldn't want things to \\\\ 
            be \\emph{understandable} would we?
        """)
        modes = "pondering", "sassy", "confused"
        self.play(*[
            ApplyMethod(student.change_mode, mode)
            for student, mode in zip(self.get_students(), modes)
        ])
        self.wait(2)

class CheckYourUnderstanding(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Quiz time!")
        self.random_blink()
        self.wait()
        self.random_blink()


class TechnicalDefinitionOfBasis(Scene):
    def construct(self):
        title  = TextMobject("Technical definition of basis:")
        title.to_edge(UP)
        definition = TextMobject([
            "The",
            "basis",
            "of a vector space is a set of",
            "linearly independent",
            "vectors that",
            "span",
            "the full space",
        ])
        t, b, oavsiaso, li, vt, s, tfs = definition.split()
        b.set_color(BLUE)
        li.set_color(GREEN)
        s.set_color(YELLOW)
        definition.set_width(FRAME_WIDTH-1)

        self.add(title)
        self.play(Write(definition))
        self.wait()

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("Next video: Matrices as linear transformations")
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait() 















