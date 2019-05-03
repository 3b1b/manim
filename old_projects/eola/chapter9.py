from manimlib.imports import *
from old_projects.eola.chapter1 import plane_wave_homotopy

V_COLOR = YELLOW

class Jennifer(PiCreature):
    CONFIG = {
        "color" : PINK,
        "start_corner" : DOWN+LEFT,
    }

class You(PiCreature):
    CONFIG = {
        "color" : BLUE_E,
        "start_corner" : DOWN+RIGHT,
        "flip_at_start" : True,
    }

def get_small_bubble(pi_creature, height = 4, width = 3):
    pi_center_x = pi_creature.get_center()[0]
    kwargs = {
        "height" : 4,
        "bubble_center_adjustment_factor" : 1./6,
    }
    bubble = ThoughtBubble(**kwargs)
    bubble.stretch_to_fit_width(3)##Canonical width
    bubble.rotate(np.pi/4)
    bubble.stretch_to_fit_width(width)
    bubble.stretch_to_fit_height(height)
    if pi_center_x < 0:
        bubble.flip()
    bubble.next_to(pi_creature, UP, buff = MED_SMALL_BUFF)
    bubble.shift_onto_screen()
    bubble.set_fill(BLACK, opacity = 0.8)
    return bubble

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "\\centering ``Mathematics is the art of giving the \\\\",
            "same name ",
            "to ",
            "different things",
            ".''",
            arg_separator = " "
        )
        words.set_color_by_tex("same name ", BLUE)
        words.set_color_by_tex("different things", MAROON_B)
        # words.set_width(FRAME_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Henri Poincar\\'e.")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(2)
        self.play(Write(author, run_time = 3))
        self.wait(2)

class LinearCombinationScene(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_X_RADIUS,
            "y_radius" : FRAME_Y_RADIUS,
            "secondary_line_ratio" : 1
        },
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        self.i_hat.label = self.get_vector_label(
            self.i_hat, "\\hat{\\imath}", "right"
        )
        self.j_hat.label = self.get_vector_label(
            self.j_hat, "\\hat{\\jmath}", "left"
        )

    def show_linear_combination(self, numerical_coords,
                                basis_vectors,
                                coord_mobs,
                                revert_to_original = True,
                                show_sum_vect = False,
                                sum_vect_color = V_COLOR,
                                ):
        for basis in basis_vectors:
            if not hasattr(basis, "label"):
                basis.label = VectorizedPoint()
                direction = np.round(rotate_vector(
                    basis.get_end(), np.pi/2
                ))
                basis.label.next_to(basis.get_center(), direction)
            basis.save_state()
            basis.label.save_state()
        if coord_mobs is None:
            coord_mobs = list(map(TexMobject, list(map(str, numerical_coords))))
            VGroup(*coord_mobs).set_fill(opacity = 0)
            for coord, basis in zip(coord_mobs, basis_vectors):
                coord.next_to(basis.label, LEFT)
        for coord, basis, scalar in zip(coord_mobs, basis_vectors, numerical_coords):
            basis.target = basis.copy().scale(scalar)
            basis.label.target = basis.label.copy()
            coord.target = coord.copy()
            new_label = VGroup(coord.target, basis.label.target)
            new_label.arrange(aligned_edge = DOWN)
            new_label.move_to(
                basis.label, 
                aligned_edge = basis.get_center()-basis.label.get_center()
            )
            new_label.shift(
                basis.target.get_center() - basis.get_center()
            )
            coord.target.next_to(basis.label.target, LEFT)
            coord.target.set_fill(basis.get_color(), opacity = 1)
            self.play(*list(map(MoveToTarget, [
                coord, basis, basis.label
            ])))
            self.wait()
        self.play(*[
            ApplyMethod(m.shift, basis_vectors[0].get_end())
            for m in self.get_mobjects_from_last_animation()
        ])
        if show_sum_vect:
            sum_vect = Vector(
                basis_vectors[1].get_end(),
                color = sum_vect_color
            )
            self.play(ShowCreation(sum_vect))
        self.wait(2)
        if revert_to_original:
            self.play(*it.chain(
                [basis.restore for basis in basis_vectors],
                [basis.label.restore for basis in basis_vectors],
                [FadeOut(coord) for coord in coord_mobs],
                [FadeOut(sum_vect) for x in [1] if show_sum_vect],
            ))
        if show_sum_vect:
            return sum_vect

class RemindOfCoordinates(LinearCombinationScene):
    CONFIG = {
        "vector_coords" : [3, 2]
    }
    def construct(self):
        self.remove(self.i_hat, self.j_hat)

        v = self.add_vector(self.vector_coords, color = V_COLOR)
        coords = self.write_vector_coordinates(v)
        self.show_standard_coord_meaning(*coords.get_entries().copy())
        self.show_abstract_scalar_idea(*coords.get_entries().copy())
        self.scale_basis_vectors(*coords.get_entries().copy())
        self.list_implicit_assumptions(*coords.get_entries())


    def show_standard_coord_meaning(self, x_coord, y_coord):
        x, y = self.vector_coords
        x_line = Line(ORIGIN, x*RIGHT, color = GREEN)
        y_line = Line(ORIGIN, y*UP, color = RED)
        y_line.shift(x_line.get_end())
        for line, coord, direction in (x_line, x_coord, DOWN), (y_line, y_coord, LEFT):
            self.play(
                coord.set_color, line.get_color(),
                coord.next_to, line.get_center(), direction,
                ShowCreation(line),                
            )
            self.wait()
        self.wait()
        self.play(*list(map(FadeOut, [x_coord, y_coord, x_line, y_line])))


    def show_abstract_scalar_idea(self, x_coord, y_coord):
        x_shift, y_shift = 4*LEFT, 4*RIGHT
        to_save = x_coord, y_coord, self.i_hat, self.j_hat
        for mob in to_save:
            mob.save_state()
        everything = VGroup(*self.get_mobjects())
        words = TextMobject("Think of coordinates \\\\ as", "scalars")
        words.set_color_by_tex("scalars", YELLOW)
        words.to_edge(UP)

        x, y = self.vector_coords  
        scaled_i = self.i_hat.copy().scale(x)
        scaled_j = self.j_hat.copy().scale(y)
        VGroup(self.i_hat, scaled_i).shift(x_shift)
        VGroup(self.j_hat, scaled_j).shift(y_shift)

        self.play(
            FadeOut(everything),
            x_coord.scale_in_place, 1.5,
            x_coord.move_to, x_shift + 3*UP,
            y_coord.scale_in_place, 1.5,
            y_coord.move_to, y_shift + 3*UP,
            Write(words)
        )
        self.play(*list(map(FadeIn, [self.i_hat, self.j_hat])))
        self.wait()
        self.play(Transform(self.i_hat, scaled_i))
        self.play(Transform(self.j_hat, scaled_j))
        self.wait()
        self.play(
            FadeOut(words),
            FadeIn(everything),
            *[mob.restore for mob in to_save]
        )
        self.wait()

    def scale_basis_vectors(self, x_coord, y_coord):
        self.play(*list(map(Write, [self.i_hat.label, self.j_hat.label])))
        self.show_linear_combination(
            self.vector_coords, 
            basis_vectors = [self.i_hat, self.j_hat],
            coord_mobs = [x_coord, y_coord]
        )

    def list_implicit_assumptions(self, x_coord, y_coord):
        everything = VGroup(*self.get_mobjects())
        title = TextMobject("Implicit assumptions")
        h_line = Line(title.get_left(), title.get_right())
        h_line.set_color(YELLOW)
        h_line.next_to(title, DOWN)
        title.add(h_line)

        ass1 = TextMobject("-First coordinate")
        ass1 = VGroup(ass1, self.i_hat.copy())
        ass1.arrange(buff = MED_SMALL_BUFF)

        ass2 = TextMobject("-Second coordinate")
        ass2 = VGroup(ass2, self.j_hat.copy())
        ass2.arrange(buff = MED_SMALL_BUFF)

        ass3 = TextMobject("-Unit of distance")

        group = VGroup(title, ass1, ass2, ass3)
        group.arrange(DOWN, aligned_edge = LEFT, buff = MED_SMALL_BUFF)
        group.to_corner(UP+LEFT)
        # VGroup(*group[1:]).shift(0.5*DOWN)
        for words in group:
            words.add_to_back(BackgroundRectangle(words))

        self.play(Write(title))
        self.wait()
        self.play(
            Write(ass1),
            ApplyFunction(
                lambda m : m.rotate_in_place(np.pi/6).set_color(X_COLOR),
                x_coord,
                rate_func = wiggle
            )
        )
        self.wait()
        self.play(
            Write(ass2),
            ApplyFunction(
                lambda m : m.rotate_in_place(np.pi/6).set_color(Y_COLOR),
                y_coord,
                rate_func = wiggle
            )
        )
        self.wait()
        self.play(Write(ass3))
        self.wait(2)
        keepers = VGroup(*[
            self.i_hat, self.j_hat,
            self.i_hat.label, self.j_hat.label
        ])
        self.play(
            FadeOut(everything),
            Animation(keepers.copy()),
            Animation(group)
        )
        self.wait()

class NameCoordinateSystem(Scene):
    def construct(self):
        vector = Vector([3, 2])
        coords = Matrix([3, 2])
        arrow = TexMobject("\\Rightarrow")
        vector.next_to(arrow, RIGHT, buff = 0)
        coords.next_to(arrow, LEFT, buff = MED_LARGE_BUFF)
        group = VGroup(coords, arrow, vector)
        group.shift(2*UP)
        coordinate_system = TextMobject("``Coordinate system''")
        coordinate_system.next_to(arrow, UP, buff = LARGE_BUFF)

        i_hat, j_hat = Vector([1, 0]), Vector([0, 1])
        i_hat.set_color(X_COLOR)
        j_hat.set_color(Y_COLOR)
        i_label = TexMobject("\\hat{\\imath}")
        i_label.set_color(X_COLOR)
        i_label.next_to(i_hat, DOWN)
        j_label = TexMobject("\\hat{\\jmath}")
        j_label.set_color(Y_COLOR)
        j_label.next_to(j_hat, LEFT)
        basis_group = VGroup(i_hat, j_hat, i_label, j_label)
        basis_group.shift(DOWN)
        basis_words = TextMobject("``Basis vectors''")
        basis_words.shift(basis_group.get_bottom()[1]*UP+MED_SMALL_BUFF*DOWN)

        self.play(Write(coords))
        self.play(Write(arrow), ShowCreation(vector))
        self.wait()
        self.play(Write(coordinate_system))
        self.wait(2)
        self.play(Write(basis_group))
        self.play(Write(basis_words))
        self.wait()

class WhatAboutOtherBasis(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            \\centering What if we used
            different basis vectors
        """)
        self.random_blink()
        self.change_student_modes("pondering")
        self.random_blink(2)

class JenniferScene(LinearCombinationScene):
    CONFIG = {
        "b1_coords" : [2, 1],
        "b2_coords" : [-1, 1],
        "foreground_plane_kwargs" : {
            "x_radius" : FRAME_X_RADIUS,
            "y_radius" : FRAME_X_RADIUS,
        },
    }
    def setup(self):
        LinearCombinationScene.setup(self)
        self.remove(self.plane, self.i_hat, self.j_hat)
        self.jenny = Jennifer()
        self.you = You()
        self.b1 = Vector(self.b1_coords, color = X_COLOR)
        self.b2 = Vector(self.b2_coords, color = Y_COLOR)
        for i, vect in enumerate([self.b1, self.b2]):
            vect.label = TexMobject("\\vec{\\textbf{b}}_%d"%(i+1))
            vect.label.scale(0.7)
            vect.label.add_background_rectangle()
            vect.label.set_color(vect.get_color())
        self.b1.label.next_to(
            self.b1.get_end()*0.4, UP+LEFT, SMALL_BUFF/2
        )
        self.b2.label.next_to(
            self.b2.get_end(), DOWN+LEFT, buff = SMALL_BUFF
        )
        self.basis_vectors = VGroup(
            self.b1, self.b2, self.b1.label, self.b2.label
        )

        transform = self.get_matrix_transformation(self.cob_matrix().T)
        self.jenny_plane = self.plane.copy()
        self.jenny_plane.apply_function(transform)

    def cob_matrix(self):
        return np.array([self.b1_coords, self.b2_coords]).T

    def inv_cob_matrix(self):
        return np.linalg.inv(self.cob_matrix())

class IntroduceJennifer(JenniferScene):
    CONFIG = {
        "v_coords" : [3, 2]
    }
    def construct(self):
        for plane in self.plane, self.jenny_plane:
            plane.fade()
        self.introduce_jenny()
        self.add_basis_vectors()
        self.show_v_from_both_perspectives()
        self.how_we_label_her_basis()

    def introduce_jenny(self):
        jenny = self.jenny
        name = TextMobject("Jennifer")
        name.next_to(jenny, UP)
        name.shift_onto_screen()

        self.add(jenny)
        self.play(
            jenny.change_mode, "wave_1",
            jenny.look, OUT,
            Write(name)
        )
        self.play(
            jenny.change_mode, "happy",
            jenny.look, UP+RIGHT,
            FadeOut(name)
        )
        self.wait()

    def add_basis_vectors(self):
        words = TextMobject("Alternate basis vectors")
        words.shift(2.5*UP)
        self.play(Write(words, run_time = 2))
        for vect in self.b1, self.b2:
            self.play(
                ShowCreation(vect),
                Write(vect.label)
            )
            self.wait()
        self.play(FadeOut(words))

    def show_v_from_both_perspectives(self):
        v = Vector(self.v_coords)
        jenny = self.jenny
        you = self.you

        you.coords = Matrix([3, 2])
        jenny.coords = Matrix(["(5/3)", "(1/3)"])
        for pi in you, jenny:
            pi.bubble = get_small_bubble(pi)
            pi.bubble.set_fill(BLACK, opacity = 0.7)
            pi.bubble.add_content(pi.coords)
        jenny.coords.scale_in_place(0.7)

        new_coords = [-1, 2]
        new_coords_mob = Matrix(new_coords)
        new_coords_mob.set_height(jenny.coords.get_height())
        new_coords_mob.move_to(jenny.coords)

        for coords in you.coords, jenny.coords, new_coords_mob:
            for entry in coords.get_entries():
                entry.add_background_rectangle()

        self.play(ShowCreation(v))
        self.wait()
        self.play(*it.chain(
            list(map(FadeIn, [
                self.plane, self.i_hat, self.j_hat, 
                self.i_hat.label, self.j_hat.label,
                you
            ])),
            list(map(Animation, [jenny, v])),
            list(map(FadeOut, self.basis_vectors)),
        ))
        self.play(
            ShowCreation(you.bubble),
            Write(you.coords)
        )
        self.play(you.change_mode, "speaking")
        self.show_linear_combination(
            self.v_coords,
            basis_vectors = [self.i_hat, self.j_hat],
            coord_mobs = you.coords.get_entries().copy(),
        )
        self.play(*it.chain(
            list(map(FadeOut, [
                self.plane, self.i_hat, self.j_hat,  
                self.i_hat.label, self.j_hat.label,
                you.bubble, you.coords
            ])),
            list(map(FadeIn, [self.jenny_plane, self.basis_vectors])),
            list(map(Animation, [v, you, jenny])),
        ))
        self.play(
            ShowCreation(jenny.bubble),
            Write(jenny.coords),
            jenny.change_mode, "speaking",
        )
        self.play(you.change_mode, "erm")
        self.show_linear_combination(
            np.dot(self.inv_cob_matrix(), self.v_coords),
            basis_vectors = [self.b1, self.b2],
            coord_mobs = jenny.coords.get_entries().copy(),
        )
        self.play(
            FadeOut(v),
            jenny.change_mode, "plain"
        )
        self.play(
            Transform(jenny.coords, new_coords_mob),
            Blink(jenny),
        )
        self.hacked_show_linear_combination(
            new_coords,
            basis_vectors = [self.b1, self.b2],
            coord_mobs = jenny.coords.get_entries().copy(),
            show_sum_vect = True,
        )

    def hacked_show_linear_combination(
        self, numerical_coords,
        basis_vectors,
        coord_mobs = None,
        show_sum_vect = False,
        sum_vect_color = V_COLOR,
        ):
        for coord, basis, scalar in zip(coord_mobs, basis_vectors, numerical_coords):
            basis.save_state()
            basis.label.save_state()
            basis.target = basis.copy().scale(scalar)
            basis.label.target = basis.label.copy()
            coord.target = coord.copy()
            new_label = VGroup(coord.target, basis.label.target)
            new_label.arrange(aligned_edge = DOWN)
            new_label.move_to(
                basis.label, 
                aligned_edge = basis.get_center()-basis.label.get_center()
            )
            new_label.shift(
                basis.target.get_center() - basis.get_center()
            )
            coord.target.next_to(basis.label.target, LEFT)
            coord.target.set_fill(basis.get_color(), opacity = 1)
            self.play(*list(map(MoveToTarget, [
                coord, basis, basis.label
            ])))
            self.wait()
        self.play(*[
            ApplyMethod(m.shift, basis_vectors[0].get_end())
            for m in self.get_mobjects_from_last_animation()
        ])
        if show_sum_vect:
            sum_vect = Vector(
                basis_vectors[1].get_end(),
                color = sum_vect_color
            )
            self.play(ShowCreation(sum_vect))
        self.wait(2)


        b1, b2 = basis_vectors
        self.jenny_plane.save_state()
        self.jenny.bubble.save_state()

        self.jenny.coords.target = self.jenny.coords.copy()
        self.you.bubble.add_content(self.jenny.coords.target)

        x, y = numerical_coords        
        b1.target = self.i_hat.copy().scale(x)
        b2.target = self.j_hat.copy().scale(y)
        b2.target.shift(b1.target.get_end())
        new_label1 = VGroup(coord_mobs[0], b1.label)
        new_label2 = VGroup(coord_mobs[1], b2.label)
        new_label1.target = new_label1.copy().next_to(b1.target, DOWN)
        new_label2.target = new_label2.copy().next_to(b2.target, LEFT)
        i_sym = TexMobject("\\hat{\\imath}").add_background_rectangle()
        j_sym = TexMobject("\\hat{\\jmath}").add_background_rectangle()
        i_sym.set_color(X_COLOR).move_to(new_label1.target[1], aligned_edge = LEFT)
        j_sym.set_color(Y_COLOR).move_to(new_label2.target[1], aligned_edge = LEFT)
        Transform(new_label1.target[1], i_sym).update(1)
        Transform(new_label2.target[1], j_sym).update(1)
        sum_vect.target = Vector(numerical_coords)
        self.play(
            Transform(self.jenny_plane, self.plane),
            Transform(self.jenny.bubble, self.you.bubble),
            self.you.change_mode, "speaking",
            self.jenny.change_mode, "erm",
            *list(map(MoveToTarget, [
                self.jenny.coords,
                b1, b2, new_label1, new_label2, sum_vect
            ]))
        )
        self.play(Blink(self.you))
        self.wait()

        self.play(*it.chain(
            list(map(FadeOut, [
                self.jenny.bubble, self.jenny.coords, 
                coord_mobs, sum_vect
            ])),
            [
                ApplyMethod(pi.change_mode, "plain") 
                for pi in (self.jenny, self.you)
            ],
            [mob.restore for mob in (b1, b2, b1.label, b2.label)]
        ))
        self.jenny.bubble.restore()

    def how_we_label_her_basis(self):
        you, jenny = self.you, self.jenny
        b1_coords = Matrix(self.b1_coords)
        b2_coords = Matrix(self.b2_coords)
        for coords in b1_coords, b2_coords:
            coords.add_to_back(BackgroundRectangle(coords))
            coords.scale(0.7)
            coords.add_to_back(BackgroundRectangle(coords))
            you.bubble.add_content(coords)
            coords.mover = coords.copy()

        self.play(jenny.change_mode, "erm")
        self.play(
            ShowCreation(you.bubble),
            Write(b1_coords),
            you.change_mode, "speaking"
        )
        self.play(
            b1_coords.mover.next_to, self.b1.get_end(), RIGHT,
            b1_coords.mover.set_color, X_COLOR
        )
        self.play(Blink(you))
        self.wait()
        self.play(Transform(b1_coords, b2_coords))
        self.play(
            b2_coords.mover.next_to, self.b2.get_end(), LEFT,
            b2_coords.mover.set_color, Y_COLOR
        )
        self.play(Blink(jenny))
        for coords, array in (b1_coords, [1, 0]), (b2_coords, [0, 1]):
            mover = coords.mover
            array_mob = Matrix(array)
            array_mob.set_color(mover.get_color())
            array_mob.set_height(mover.get_height())
            array_mob.move_to(mover)
            array_mob.add_to_back(BackgroundRectangle(array_mob))
            mover.target = array_mob
        self.play(
            self.jenny_plane.restore,
            FadeOut(self.you.bubble),
            FadeOut(b1_coords),
            self.jenny.change_mode, "speaking",
            self.you.change_mode, "confused",
            *list(map(Animation, [
                self.basis_vectors,
                b1_coords.mover,
                b2_coords.mover,
            ]))
        )
        self.play(MoveToTarget(b1_coords.mover))
        self.play(MoveToTarget(b2_coords.mover))
        self.play(Blink(self.jenny))

class SpeakingDifferentLanguages(JenniferScene):
    def construct(self):
        jenny, you = self.jenny, self.you
        title = TextMobject("Different languages")
        title.to_edge(UP)

        vector = Vector([3, 2])
        vector.center().shift(DOWN)
        you.coords = Matrix([3, 2])
        you.text = TextMobject("Looks to be")
        jenny.coords = Matrix(["5/3", "1/3"])
        jenny.text = TextMobject("Non, c'est")
        for pi in jenny, you:
            pi.bubble = pi.get_bubble(SpeechBubble, width = 4.5, height = 3.5)
            if pi is you:
                pi.bubble.shift(MED_SMALL_BUFF*RIGHT)
            else:
                pi.coords.scale(0.8)
                pi.bubble.shift(MED_SMALL_BUFF*LEFT)
            pi.coords.next_to(pi.text, buff = MED_SMALL_BUFF)
            pi.coords.add(pi.text)
            pi.bubble.add_content(pi.coords)

        self.add(you, jenny)
        self.play(Write(title))
        self.play(
            ShowCreation(vector),
            you.look_at, vector,
            jenny.look_at, vector,
        )
        for pi in you, jenny:
            self.play(
                pi.change_mode, "speaking" if pi is you else "sassy",
                ShowCreation(pi.bubble),
                Write(pi.coords)
            )
            self.play(Blink(pi))
        self.wait()

class ShowGrid(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
    }
    def construct(self):
        self.remove(self.i_hat, self.j_hat)
        self.wait()
        self.plane.prepare_for_nonlinear_transform()
        self.plane.save_state()
        self.play(Homotopy(plane_wave_homotopy, self.plane))
        self.play(self.plane.restore)
        for vect in self.i_hat, self.j_hat:
            self.play(ShowCreation(vect))
        self.wait()

class GridIsAConstruct(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            \\centering 
            The grid is
            just a construct
        """)
        self.change_student_modes(*["pondering"]*3)
        self.random_blink(2)

class SpaceHasNoGrid(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False
    }
    def construct(self):
        words = TextMobject("Space has no grid")
        words.to_edge(UP)
        self.play(
            Write(words),
            FadeOut(self.plane),
            *list(map(Animation, [self.i_hat, self.j_hat]))
        )
        self.wait()

class JennysGrid(JenniferScene):
    def construct(self):
        self.add(self.jenny)
        self.jenny.shift(3*RIGHT)
        bubble = self.jenny.get_bubble(SpeechBubble, width = 4)
        bubble.flip()
        bubble.set_fill(BLACK, opacity = 0.8)
        bubble.to_edge(LEFT)
        bubble.write("""
            This grid is also
            just a construct
        """)
        coords = [1.5, -3]
        coords_mob = Matrix(coords)
        coords_mob.add_background_to_entries()
        bubble.position_mobject_inside(coords_mob)

        for vect in self.b1, self.b2:
            self.play(
                ShowCreation(vect),
                Write(vect.label)
            )
        self.wait()
        self.play(
            ShowCreation(
                self.jenny_plane, 
                run_time = 3, 
                lag_ratio = 0.5
            ),
            self.jenny.change_mode, "speaking",
            self.jenny.look_at, ORIGIN,
            ShowCreation(bubble),
            Write(bubble.content),
            Animation(self.basis_vectors)
        )
        self.play(Blink(self.jenny))
        self.play(
            FadeOut(bubble.content),
            FadeIn(coords_mob)
        )
        self.show_linear_combination(
            numerical_coords = coords,
            basis_vectors = [self.b1, self.b2],
            coord_mobs = coords_mob.get_entries().copy(),
            show_sum_vect = True
        )

class ShowOriginOfGrid(JenniferScene):
    def construct(self):
        for plane in self.plane, self.jenny_plane:
            plane.fade(0.3)
        self.add(self.jenny_plane)
        self.jenny_plane.save_state()

        origin_word = TextMobject("Origin")
        origin_word.shift(2*RIGHT+2.5*UP)
        origin_word.add_background_rectangle()
        arrow = Arrow(origin_word, ORIGIN, color = RED)
        origin_dot = Dot(ORIGIN, radius = 0.1, color = RED)
        coords = Matrix([0, 0])
        coords.add_to_back(BackgroundRectangle(coords))
        coords.next_to(ORIGIN, DOWN+LEFT)
        vector = Vector([3, -2], color = PINK)

        self.play(
            Write(origin_word),
            ShowCreation(arrow)
        )
        self.play(ShowCreation(origin_dot))
        self.wait()
        self.play(
            Transform(self.jenny_plane, self.plane),
            *list(map(Animation, [origin_word, origin_dot, arrow]))
        )
        self.wait()
        self.play(Write(coords))
        self.wait()
        self.play(FadeIn(vector))
        self.wait()
        self.play(Transform(vector, Mobject.scale(vector.copy(), 0)))
        self.wait()
        self.play(
            self.jenny_plane.restore, 
            *list(map(Animation, [origin_word, origin_dot, arrow, coords]))
        )
        for vect in self.b1, self.b2:
            self.play(
                ShowCreation(vect),
                Write(vect.label)
            )
        self.wait()

class AskAboutTranslation(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "\\centering How do you translate \\\\ between coordinate systems?",
            target_mode = "raise_right_hand"
        )
        self.random_blink(3)

class TranslateFromJenny(JenniferScene):
    CONFIG = {
        "coords" : [-1, 2]
    }
    def construct(self):
        self.add_players()
        self.ask_question()
        self.establish_coordinates()
        self.perform_arithmetic()

    def add_players(self):
        for plane in self.jenny_plane, self.plane:
            plane.fade()
        self.add(
            self.jenny_plane, 
            self.jenny, self.you, 
            self.basis_vectors
        )
        self.jenny.coords = Matrix(self.coords)
        self.you.coords = Matrix(["?", "?"])
        self.you.coords.get_entries().set_color_by_gradient(X_COLOR, Y_COLOR)
        for pi in self.jenny, self.you:
            pi.bubble = get_small_bubble(pi)
            pi.bubble.set_fill(BLACK, opacity = 0.8)
            pi.coords.scale(0.8)
            pi.coords.add_background_to_entries()
            pi.bubble.add_content(pi.coords)

    def ask_question(self):
        self.play(
            self.jenny.change_mode, "pondering",
            ShowCreation(self.jenny.bubble),
            Write(self.jenny.coords)
        )
        coord_mobs = self.jenny.coords.get_entries().copy()
        self.basis_vectors_copy = self.basis_vectors.copy()
        self.basis_vectors_copy.fade(0.3)
        self.add(self.basis_vectors_copy, self.basis_vectors)
        sum_vect = self.show_linear_combination(
            numerical_coords = self.coords,
            basis_vectors = [self.b1, self.b2],
            coord_mobs = coord_mobs,
            revert_to_original = False,
            show_sum_vect = True,
        )
        self.wait()
        everything = self.get_mobjects()
        for submob in self.jenny_plane.get_family():
            everything.remove(submob)
        self.play(
            Transform(self.jenny_plane, self.plane),
            *list(map(Animation, everything))
        )
        self.play(
            self.you.change_mode, "confused",
            ShowCreation(self.you.bubble),
            Write(self.you.coords)
        )
        self.wait()

    def establish_coordinates(self):
        b1, b2 = self.basis_vectors_copy[:2]
        b1_coords = Matrix(self.b1_coords).set_color(X_COLOR)
        b2_coords = Matrix(self.b2_coords).set_color(Y_COLOR)
        for coords in b1_coords, b2_coords:
            coords.scale(0.7)
            coords.add_to_back(BackgroundRectangle(coords))
        b1_coords.next_to(b1.get_end(), RIGHT)
        b2_coords.next_to(b2.get_end(), UP)

        for coords in b1_coords, b2_coords:
            self.play(Write(coords))
        self.b1_coords_mob, self.b2_coords_mob = b1_coords, b2_coords

    def perform_arithmetic(self):
        jenny_x, jenny_y = self.jenny.coords.get_entries().copy()
        equals, plus, equals2 = syms = list(map(TexMobject, list("=+=")))
        result = Matrix([-4, 1])
        result.set_height(self.you.coords.get_height())
        for mob in syms + [self.you.coords, self.jenny.coords, result]:
            mob.add_to_back(BackgroundRectangle(mob))
        movers = [
            self.you.coords, equals,
            jenny_x, self.b1_coords_mob, plus,
            jenny_y, self.b2_coords_mob,
            equals2, result
        ]
        for mover in movers:
            mover.target = mover.copy()
        mover_targets = VGroup(*[mover.target for mover in movers])
        mover_targets.arrange()
        mover_targets.to_edge(UP)
        for mob in syms + [result]:
            mob.move_to(mob.target)
            mob.set_fill(BLACK, opacity = 0)

        mover_sets = [
            [jenny_x, self.b1_coords_mob],
            [plus, jenny_y, self.b2_coords_mob],
            [self.you.coords, equals],
        ]
        for mover_set in mover_sets:
            self.play(*list(map(MoveToTarget, mover_set)))
            self.wait()
        self.play(
            MoveToTarget(equals2),
            Transform(self.b1_coords_mob.copy(), result.target),
            Transform(self.b2_coords_mob.copy(), result.target),
        )
        self.remove(*self.get_mobjects_from_last_animation())
        result = result.target
        self.add(equals2, result)
        self.wait()

        result_copy = result.copy()
        self.you.bubble.add_content(result_copy)
        self.play(
            self.you.change_mode, "hooray",
            Transform(result.copy(), result_copy)
        )
        self.play(Blink(self.you))
        self.wait()

        matrix = Matrix(np.array([self.b1_coords, self.b2_coords]).T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        self.jenny.coords.target = self.jenny.coords.copy()
        self.jenny.coords.target.next_to(equals, LEFT)
        matrix.set_height(self.jenny.coords.get_height())
        matrix.next_to(self.jenny.coords.target, LEFT)
        matrix.add_to_back(BackgroundRectangle(matrix))

        self.play(
            FadeOut(self.jenny.bubble),
            FadeOut(self.you.coords),
            self.jenny.change_mode, "plain",
            MoveToTarget(self.jenny.coords),
            FadeIn(matrix)
        )
        self.wait()

class WatchChapter3(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            You've all watched 
            chapter 3, right?
        """)
        self.random_blink()
        self.play(
            self.get_students()[0].look, LEFT,
            self.get_students()[1].change_mode, "happy",
            self.get_students()[2].change_mode, "happy",
        )
        self.random_blink(2)

class TalkThroughChangeOfBasisMatrix(JenniferScene):
    def construct(self):
        self.add(self.plane, self.jenny, self.you)
        self.plane.fade()
        self.jenny_plane.fade()
        for pi in self.jenny, self.you:
            pi.bubble = get_small_bubble(pi)

        matrix = Matrix(np.array([self.b1_coords, self.b2_coords]).T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.next_to(ORIGIN, RIGHT, buff = MED_SMALL_BUFF).to_edge(UP)

        b1_coords = Matrix(self.b1_coords)
        b1_coords.set_color(X_COLOR)
        b1_coords.next_to(self.b1.get_end(), RIGHT)
        b2_coords = Matrix(self.b2_coords)
        b2_coords.set_color(Y_COLOR)
        b2_coords.next_to(self.b2.get_end(), UP)
        for coords in b1_coords, b2_coords:
            coords.scale_in_place(0.7)

        basis_coords_pair = VGroup(
            Matrix([1, 0]).set_color(X_COLOR).scale(0.7),
            TexMobject(","),
            Matrix([0, 1]).set_color(Y_COLOR).scale(0.7),
        )
        basis_coords_pair.arrange(aligned_edge = DOWN)
        self.you.bubble.add_content(basis_coords_pair)

        t_matrix1 = np.array([self.b1_coords, [0, 1]])
        t_matrix2 = np.dot(
            self.cob_matrix(), 
            np.linalg.inv(t_matrix1.T)
        ).T

        for mob in matrix, b1_coords, b2_coords:
            mob.rect = BackgroundRectangle(mob)
            mob.add_to_back(mob.rect)

        self.play(Write(matrix))
        for vect in self.i_hat, self.j_hat:
            self.play(
                ShowCreation(vect),
                Write(vect.label)
            )
        self.play(
            self.you.change_mode, "pondering",
            ShowCreation(self.you.bubble),
            Write(basis_coords_pair)
        )
        self.play(Blink(self.you))
        self.wait()

        self.add_foreground_mobject(
            self.jenny, self.you, self.you.bubble, 
            basis_coords_pair, matrix
        )
        matrix_copy = matrix.copy()
        matrix_copy.rect.set_fill(opacity = 0)
        self.apply_transposed_matrix(
            t_matrix1, 
            added_anims = [
                Transform(self.i_hat, self.b1),
                Transform(self.i_hat.label, self.b1.label),
                Transform(matrix_copy.rect, b1_coords.rect),                
                Transform(
                    matrix_copy.get_brackets(),
                    b1_coords.get_brackets(),
                ),
                Transform(
                    VGroup(*matrix_copy.get_mob_matrix()[:,0]),
                    b1_coords.get_entries()
                ),
            ]
        )
        self.remove(matrix_copy)
        self.add_foreground_mobject(b1_coords)
        matrix_copy = matrix.copy()
        matrix_copy.rect.set_fill(opacity = 0)
        self.apply_transposed_matrix(
            t_matrix2, 
            added_anims = [
                Transform(self.j_hat, self.b2),
                Transform(self.j_hat.label, self.b2.label),
                Transform(matrix_copy.rect, b2_coords.rect),                
                Transform(
                    matrix_copy.get_brackets(),
                    b2_coords.get_brackets(),
                ),
                Transform(
                    VGroup(*matrix_copy.get_mob_matrix()[:,1]),
                    b2_coords.get_entries()
                ),
            ]
        )
        self.remove(matrix_copy)
        self.add_foreground_mobject(b2_coords)
        basis_coords_pair.target = basis_coords_pair.copy()
        self.jenny.bubble.add_content(basis_coords_pair.target)
        self.wait()
        self.play(
            FadeOut(b1_coords),
            FadeOut(b2_coords),
            self.jenny.change_mode, "speaking",
            Transform(self.you.bubble, self.jenny.bubble),
            MoveToTarget(basis_coords_pair),
        )

class ChangeOfBasisExample(JenniferScene):
    CONFIG = {
        "v_coords" : [-1, 2]
    }
    def construct(self):
        self.add(
            self.plane, self.i_hat, self.j_hat, 
            self.i_hat.label, self.j_hat.label,
        )
        self.j_hat.label.next_to(self.j_hat, RIGHT)
        v = self.add_vector(self.v_coords)
        v_coords = Matrix(self.v_coords)
        v_coords.scale(0.8)
        v_coords.add_to_back(BackgroundRectangle(v_coords))
        v_coords.to_corner(UP+LEFT)
        v_coords.add_background_to_entries()
        for pi in self.you, self.jenny:
            pi.change_mode("pondering")
            pi.bubble = get_small_bubble(pi)
            pi.bubble.add_content(v_coords.copy())
            pi.add(pi.bubble, pi.bubble.content)

        start_words = TextMobject("How", "we", "think of")
        start_words.add_background_rectangle()
        start_group = VGroup(start_words, v_coords)
        start_group.arrange(buff = MED_SMALL_BUFF)
        start_group.next_to(self.you, LEFT, buff = 0)
        start_group.to_edge(UP)
        end_words = TextMobject("How", "Jennifer", "thinks of")
        end_words.add_background_rectangle()
        end_words.move_to(start_words, aligned_edge = RIGHT)


        self.play(
            Write(start_group),
            FadeIn(self.you),
        )
        self.add_foreground_mobject(start_group, self.you)

        self.show_linear_combination(
            numerical_coords = self.v_coords,
            basis_vectors = [self.i_hat, self.j_hat],
            coord_mobs = v_coords.get_entries().copy(),
        )
        self.play(*list(map(FadeOut, [self.i_hat.label, self.j_hat.label])))
        self.apply_transposed_matrix(self.cob_matrix().T)
        VGroup(self.i_hat, self.j_hat).fade()
        self.add(self.b1, self.b2)
        self.play(
            Transform(start_words, end_words),
            Transform(self.you, self.jenny),
            *list(map(Write, [self.b1.label, self.b2.label]))
        )
        self.play(Blink(self.you))
        self.show_linear_combination(
            numerical_coords = self.v_coords,
            basis_vectors = [self.b1, self.b2],
            coord_mobs = v_coords.get_entries().copy(),
        )

class FeelsBackwards(Scene):
    def construct(self):
        matrix = Matrix(np.array([
            JenniferScene.CONFIG["b1_coords"], 
            JenniferScene.CONFIG["b2_coords"],
        ]).T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.shift(UP)
        top_arrow = Arrow(matrix.get_left(), matrix.get_right())
        bottom_arrow = top_arrow.copy().rotate(np.pi)
        top_arrow.next_to(matrix, UP, buff = LARGE_BUFF)
        bottom_arrow.next_to(matrix, DOWN, buff = LARGE_BUFF)
        top_arrow.set_color(BLUE)

        jenny_grid = TextMobject("Jennifer's grid").set_color(BLUE)
        our_grid = TextMobject("Our grid").set_color(BLUE)
        jenny_language = TextMobject("Jennifer's language")
        our_language = TextMobject("Our language")

        our_grid.next_to(top_arrow, LEFT)
        jenny_grid.next_to(top_arrow, RIGHT)
        jenny_language.next_to(bottom_arrow, RIGHT)
        our_language.next_to(bottom_arrow, LEFT)

        self.add(matrix)
        self.play(Write(our_grid))
        self.play(
            ShowCreation(top_arrow),
            Write(jenny_grid)
        )
        self.wait()
        self.play(Write(jenny_language))
        self.play(
            ShowCreation(bottom_arrow),
            Write(our_language)
        )
        self.wait()

        ##Swap things
        inverse_word = TextMobject("Inverse")
        inverse_word.next_to(matrix, LEFT, buff = MED_SMALL_BUFF)
        inverse_exponent = TexMobject("-1")
        inverse_exponent.next_to(matrix.get_corner(UP+RIGHT), RIGHT)
        self.play(*list(map(Write, [inverse_word, inverse_exponent])))
        self.play(
            Swap(jenny_grid, our_grid),
            top_arrow.scale_in_place, 0.8,
            top_arrow.shift, 0.8*RIGHT,
            top_arrow.set_color, BLUE,
        )
        self.play(
            Swap(jenny_language, our_language),
            bottom_arrow.scale_in_place, 0.8,
            bottom_arrow.shift, 0.8*RIGHT
        )
        self.wait()

class AskAboutOtherWayAround(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            What about the 
            other way around?
        """)
        self.random_blink(3)

class RecallInverse(JenniferScene):
    def construct(self):
        numerical_t_matrix = np.array([self.b1_coords, self.b2_coords])
        matrix = Matrix(numerical_t_matrix.T)
        matrix.add_to_back(BackgroundRectangle(matrix))
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.to_corner(UP+LEFT, buff = MED_LARGE_BUFF)
        # matrix.shift(MED_SMALL_BUFF*DOWN)
        inverse_exponent = TexMobject("-1")
        inverse_exponent.next_to(matrix.get_corner(UP+RIGHT), RIGHT)
        inverse_exponent.add_background_rectangle()
        brace = Brace(VGroup(matrix, inverse_exponent))
        inverse_word = brace.get_text("Inverse")
        inverse_word.add_background_rectangle()

        equals = TexMobject("=")
        equals.add_background_rectangle()
        inv_matrix = Matrix([
            ["1/3", "1/3"],
            ["-1/3", "2/3"]
        ])
        inv_matrix.set_height(matrix.get_height())
        inv_matrix.add_to_back(BackgroundRectangle(inv_matrix))
        equals.next_to(matrix, RIGHT, buff = 0.7)
        inv_matrix.next_to(equals, RIGHT, buff = MED_SMALL_BUFF)

        self.add_foreground_mobject(matrix)
        self.apply_transposed_matrix(numerical_t_matrix)
        self.play(
            GrowFromCenter(brace),
            Write(inverse_word),
            Write(inverse_exponent)
        )
        self.add_foreground_mobject(*self.get_mobjects_from_last_animation())
        self.wait()
        self.apply_inverse_transpose(numerical_t_matrix)
        self.wait()
        self.play(
            Write(equals),
            Transform(matrix.copy(), inv_matrix)
        )
        self.remove(*self.get_mobjects_from_last_animation())
        self.add_foreground_mobject(equals, inv_matrix)
        self.wait()
        for mob in self.plane, self.i_hat, self.j_hat:
            self.add(mob.copy().fade(0.7))
        self.apply_transposed_matrix(numerical_t_matrix)
        self.play(FadeIn(self.jenny))
        self.play(self.jenny.change_mode, "speaking")
        #Little hacky now
        inv_matrix.set_column_colors(X_COLOR)
        self.play(*[
            ApplyMethod(
                mob.scale_in_place, 1.2, 
                rate_func = there_and_back
            )
            for mob in inv_matrix.get_mob_matrix()[:,0]
        ])
        self.wait()
        inv_matrix.set_column_colors(X_COLOR, Y_COLOR)
        self.play(*[
            ApplyMethod(
                mob.scale_in_place, 1.2, 
                rate_func = there_and_back
            )
            for mob in inv_matrix.get_mob_matrix()[:,1]
        ])
        self.wait()

class WorkOutInverseComputation(Scene):
    def construct(self):
        our_vector = Matrix([3, 2])
        her_vector = Matrix(["5/3", "1/3"])
        matrix = Matrix([["1/3", "1/3"], ["-1/3", "2/3"]])
        our_vector.set_color(BLUE_D)
        her_vector.set_color(MAROON_B)
        equals = TexMobject("=")
        equation = VGroup(
            matrix, our_vector, equals, her_vector
        )
        for mob in equation:
            if isinstance(mob, Matrix):
                mob.set_height(2)
        equation.arrange()

        matrix_brace = Brace(matrix, UP)
        our_vector_brace = Brace(our_vector)
        her_vector_brace = Brace(her_vector, UP)
        matrix_text = matrix_brace.get_text("""
            \\centering
            Inverse
            change of basis
            matrix
        """)
        our_text = our_vector_brace.get_text("""
            \\centering
            Written in
            our language
        """)
        our_text.set_color(our_vector.get_color())
        her_text = her_vector_brace.get_text("""
            \\centering
            Same vector
            in her language
        """)
        her_text.set_color(her_vector.get_color())
        for text in our_text, her_text:
            text.scale_in_place(0.7)

        self.add(our_vector)
        self.play(
            GrowFromCenter(our_vector_brace),
            Write(our_text)
        )
        self.wait()
        self.play(
            FadeIn(matrix),
            GrowFromCenter(matrix_brace),
            Write(matrix_text)
        )
        self.wait()
        self.play(
            Write(equals),
            Write(her_vector)
        )
        self.play(
            GrowFromCenter(her_vector_brace),
            Write(her_text)
        )
        self.wait()

class SoThatsTranslation(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("So that's translation")
        self.random_blink(3)

class SummarizeTranslationProcess(Scene):
    def construct(self):
        self.define_matrix()
        self.show_translation()

    def define_matrix(self):
        matrix = Matrix([[2, -1], [1, 1]])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        A, equals = list(map(TexMobject, list("A=")))
        equation = VGroup(A, equals, matrix)
        equation.arrange()
        equation.to_corner(UP+LEFT)
        equation.shift(RIGHT)
        words = TextMobject("""
            Jennifer's basis vectors, 
            written in our coordinates
        """)
        words.to_edge(LEFT)
        mob_matrix = matrix.get_mob_matrix()
        arrow1 = Arrow(words, mob_matrix[1, 0], color = X_COLOR)
        arrow2 = Arrow(words, mob_matrix[1, 1], color = Y_COLOR)

        self.add(A, equals, matrix)
        self.play(
            Write(words),
            *list(map(ShowCreation, [arrow1, arrow2]))
        )
        self.A_copy = A.copy()

    def show_translation(self):
        our_vector = Matrix(["x_o", "y_o"])
        her_vector = Matrix(["x_j", "y_j"])
        for vector, color in (our_vector, BLUE_D), (her_vector, MAROON_B):
            # vector.set_height(1.5)
            vector.set_color(color)
        A = TexMobject("A")
        A_inv = TexMobject("A^{-1}")
        equals = TexMobject("=")

        equation = VGroup(A, her_vector, equals, our_vector)
        equation.arrange()
        equation.to_edge(RIGHT)
        equation.shift(0.5*UP)
        A_inv.next_to(our_vector, LEFT)

        her_words = TextMobject("Vector in her coordinates")
        her_words.set_color(her_vector.get_color())
        her_words.scale(0.8).to_corner(UP+RIGHT)
        her_arrow = Arrow(
            her_words, her_vector, 
            color = her_vector.get_color()
        )
        our_words = TextMobject("Same vector in\\\\ our coordinates")
        our_words.set_color(our_vector.get_color())
        our_words.scale(0.8).to_edge(RIGHT).shift(2*DOWN)
        our_words.shift_onto_screen()
        our_arrow = Arrow(
            our_words.get_top(), our_vector.get_bottom(), 
            color = our_vector.get_color()
        )

        self.play(
            Write(equation),
            Transform(self.A_copy, A)
        )
        self.remove(self.A_copy)
        self.play(
            Write(her_words),
            ShowCreation(her_arrow)
        )
        self.play(
            Write(our_words),
            ShowCreation(our_arrow)
        )
        self.wait(2)
        self.play(
            VGroup(her_vector, equals).next_to, A_inv, LEFT,
            her_arrow.rotate_in_place, -np.pi/6,
            her_arrow.shift, MED_SMALL_BUFF*LEFT,
            Transform(A, A_inv, path_arc = np.pi)
        )
        self.wait()

class VectorsAreNotTheOnlyOnes(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            \\centering
            Vectors aren't the
            only thing with coordinates
        """)
        self.change_student_modes("pondering", "confused", "erm")
        self.random_blink(3)

class Prerequisites(Scene):
    def construct(self):
        title = TextMobject("Prerequisites")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)

        self.add(title, h_line)
        prereqs = list(map(TextMobject, [
            "Linear transformations",
            "Matrix multiplication",
        ]))
        for direction, words in zip([LEFT, RIGHT], prereqs):
            rect = Rectangle(height = 9, width = 16)
            rect.set_height(3.5)
            rect.next_to(ORIGIN, direction, buff = MED_SMALL_BUFF)
            rect.set_color(BLUE)
            words.next_to(rect, UP, buff =  MED_SMALL_BUFF)
            self.play(
                Write(words),
                ShowCreation(rect)
            )
        self.wait()

class RotationExample(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[0, 1], [-1, 0]]
    }
    def construct(self):
        words = TextMobject("$90^\\circ$ rotation")
        words.scale(1.2)
        words.add_background_rectangle()
        words.to_edge(UP)

        matrix = Matrix(self.t_matrix.T)
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.rect = BackgroundRectangle(matrix)
        matrix.add_to_back(matrix.rect)
        matrix.next_to(words, DOWN)
        matrix.shift(2*RIGHT)

        self.play(Write(words))
        self.add_foreground_mobject(words)
        self.wait()
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()
        self.play(
            self.i_hat.rotate, np.pi/12,
            self.j_hat.rotate, -np.pi/12,
            rate_func = wiggle,
            run_time = 2
        )
        self.wait()

        i_coords, j_coords = coord_arrays = list(map(Matrix, self.t_matrix))
        for coords, vect in zip(coord_arrays, [self.i_hat, self.j_hat]):
            coords.scale(0.7)
            coords.rect = BackgroundRectangle(coords)
            coords.add_to_back(coords.rect)
            coords.set_color(vect.get_color())
            direction = UP if vect is self.j_hat else RIGHT
            coords.next_to(vect.get_end(), direction, buff = MED_SMALL_BUFF)
            self.play(Write(coords))
            self.wait()

        self.play(
            Transform(i_coords.rect, matrix.rect),
            Transform(i_coords.get_brackets(), matrix.get_brackets()),
            Transform(
                i_coords.get_entries(), 
                VGroup(*matrix.get_mob_matrix()[:, 0])
            ),
        )
        self.play(
            FadeOut(j_coords.rect),
            FadeOut(j_coords.get_brackets()),
            Transform(
                j_coords.get_entries(), 
                VGroup(*matrix.get_mob_matrix()[:, 1])
            ),
        )
        self.wait()
        self.add_words(matrix)

    def add_words(self, matrix):
        follow_basis = TextMobject(
            "Follow", "our choice",
            "\\\\ of basis vectors"
        )
        follow_basis.set_color_by_tex("our choice", YELLOW)
        follow_basis.add_background_rectangle()
        follow_basis.next_to(
            matrix, LEFT, 
            buff = MED_SMALL_BUFF, 
        )

        record = TextMobject(
            "Record using \\\\",
            "our coordinates"
        )
        record.set_color_by_tex("our coordinates", YELLOW)
        record.add_background_rectangle()
        record.next_to(
            matrix, DOWN, 
            buff = MED_SMALL_BUFF, 
            aligned_edge = LEFT
        )

        self.play(Write(follow_basis))
        self.wait()
        self.play(Write(record))
        self.wait()
        
class JennyWatchesRotation(JenniferScene):
    def construct(self):
        jenny = self.jenny
        self.add(self.jenny_plane.copy().fade())        
        self.add(self.jenny_plane)
        self.add(jenny)
        for vect in self.b1, self.b2:
            self.add_vector(vect)

        matrix = Matrix([["?", "?"], ["?", "?"]])
        matrix.get_entries().set_color_by_gradient(X_COLOR, Y_COLOR)
        jenny.bubble = get_small_bubble(jenny)
        jenny.bubble.add_content(matrix)
        matrix.scale_in_place(0.8)

        self.play(
            jenny.change_mode, "sassy",
            ShowCreation(jenny.bubble),
            Write(matrix)
        )
        self.play(*it.chain(
            [
                Rotate(mob, np.pi/2, run_time = 3)
                for mob in (self.jenny_plane, self.b1, self.b2)
            ],
            list(map(Animation, [jenny, jenny.bubble, matrix]))
        ))
        self.play(jenny.change_mode, "pondering")
        self.play(Blink(jenny))
        self.wait()

class AksAboutTranslatingColumns(TeacherStudentsScene):
    def construct(self):
        matrix = Matrix([[0, -1], [1, 0]])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.scale(0.7)
        words = TextMobject("Translate columns of")
        matrix.next_to(words, DOWN)
        words.add(matrix)
        self.student_says(words, student_index = 0)
        self.random_blink(2)

        student = self.get_students()[0]
        bubble = get_small_bubble(student)
        bubble.set_fill(opacity = 0)
        matrix.target = matrix.copy()
        bubble.add_content(matrix.target)
        self.play(
            Transform(student.bubble, bubble),
            FadeOut(student.bubble.content),
            MoveToTarget(matrix.copy()),
            student.change_mode, "pondering",
        )
        self.remove(student.bubble)
        student.bubble = None
        self.add(bubble, matrix.target)

        self.random_blink()
        words = TextMobject(
            "\\centering Those columns still \\\\ represent ",
            "our basis", ", not ", "hers",
            arg_separator = ""
        )
        words.set_color_by_tex("our basis", BLUE)
        words.set_color_by_tex("hers", MAROON_B)
        self.teacher_says(words)
        self.change_student_modes("erm", "pondering", "pondering")
        self.random_blink()

class HowToTranslateAMatrix(Scene):
    def construct(self):
        self.add_title()

        arrays = VGroup(*list(map(Matrix, [
            [["1/3", "-2/3"], ["5/3", "-1/3"]],
            [-1, 2],
            [[2, -1], [1, 1]],
            [[0, -1], [1, 0]],
            [[2, -1], [1, 1]],
        ])))
        result, her_vector, cob_matrix, transform, inv_cob = arrays
        neg_1 = TexMobject("-1")
        neg_1.next_to(inv_cob.get_corner(UP+RIGHT), RIGHT)
        inv_cob.add(neg_1)
        arrays.arrange(LEFT)
        arrays.to_edge(LEFT, buff = LARGE_BUFF/2.)
        for array in arrays:
            array.brace = Brace(array)
            array.top_brace = Brace(VGroup(array, her_vector), UP)
        for array in cob_matrix, inv_cob:
            submobs = array.split()
            submobs.sort(key=lambda m: m.get_center()[0])
            array.submobjects = submobs
        her_vector.set_color(MAROON_B)
        cob_matrix.set_color_by_gradient(BLUE, MAROON_B)
        transform.set_column_colors(X_COLOR, Y_COLOR)
        transform.get_brackets().set_color(BLUE)
        inv_cob.set_color_by_gradient(MAROON_B, BLUE)
        result.set_column_colors(X_COLOR, Y_COLOR)
        result.get_brackets().set_color(MAROON_B)

        final_top_brace = Brace(VGroup(cob_matrix, inv_cob), UP)

        brace_text_pairs = [
            (her_vector.brace, ("Vector in \\\\", "Jennifer's language")),
            (her_vector.top_brace, ("",)),
            (cob_matrix.brace, ("Change of basis \\\\", "matrix")),
            (cob_matrix.top_brace, ("Same vector \\\\", "in", "our", "language")),
            (transform.brace, ("Transformation matrix \\\\", "in", "our", "language")),
            (transform.top_brace, ("Transformed vector \\\\", "in", "our", "language")),
            (inv_cob.brace, ("Inverse \\\\", "change of basis \\\\", "matrix")),
            (inv_cob.top_brace, ("Transformed vector \\\\", "in", "her", "language")),
            (final_top_brace, ("Transformation matrix \\\\", "in", "her", "language"))
        ]
        for brace, text_args in brace_text_pairs:
            text_args = list(text_args)
            text_args[0] = "\\centering " + text_args[0]
            text = TextMobject(*text_args)
            text.set_color_by_tex("our", BLUE)
            text.set_color_by_tex("her", MAROON_B)
            brace.put_at_tip(text)
            brace.text = text

        brace = her_vector.brace
        bottom_words = her_vector.brace.text
        top_brace = cob_matrix.top_brace
        top_words = cob_matrix.top_brace.text
        def introduce(array):
            self.play(
                Write(array),
                Transform(brace, array.brace),
                Transform(bottom_words, array.brace.text)
            )
            self.wait()
        def echo_introduce(array):
            self.play(
                Transform(top_brace, array.top_brace),
                Transform(top_words, array.top_brace.text)
            )
            self.wait()

        self.play(Write(her_vector))
        self.play(
            GrowFromCenter(brace),
            Write(bottom_words)
        )
        self.wait()
        introduce(cob_matrix)
        self.play(
            GrowFromCenter(top_brace),
            Write(top_words)
        )
        self.wait()
        introduce(transform)
        echo_introduce(transform)
        introduce(inv_cob),
        echo_introduce(inv_cob)

        #Genearlize to single matrix
        v = TexMobject("\\vec{\\textbf{v}}")
        v.set_color(her_vector.get_color())
        v.move_to(her_vector, aligned_edge = LEFT)
        self.play(
            Transform(her_vector, v),
            FadeOut(bottom_words),
            FadeOut(brace),
        )
        self.wait()
        self.play(
            Transform(top_brace, final_top_brace),
            Transform(top_brace.text, final_top_brace.text),
        )
        self.wait()

        equals = TexMobject("=")
        equals.replace(v)
        result.next_to(equals, RIGHT)
        self.play(
            Transform(her_vector, equals),
            Write(result)
        )
        self.wait(2)

        everything = VGroup(*self.get_mobjects())
        self.play(
            FadeOut(everything),
            result.to_corner, UP+LEFT
        )
        self.add(result)
        self.wait()


    def add_title(self):
        title = TextMobject("How to translate a matrix")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(h_line))
        self.wait()

class JennyWatchesRotationWithMatrixAndVector(JenniferScene):
    def construct(self):
        self.add(self.jenny_plane.copy().fade(0.8))
        self.add(self.jenny_plane, self.jenny, self.b1, self.b2)

        matrix = Matrix([["1/3", "-2/3"], ["5/3", "-1/3"]])
        matrix.set_column_colors(X_COLOR, Y_COLOR)
        matrix.to_corner(UP+LEFT)

        vector_coords = [1, 2]
        vector_array = Matrix(vector_coords)
        vector_array.set_color(YELLOW)
        vector_array.next_to(matrix, RIGHT)

        result = Matrix([-1, 1])
        equals = TexMobject("=")
        equals.next_to(vector_array)
        result.next_to(equals)

        for array in matrix, vector_array, result:
            array.add_to_back(BackgroundRectangle(array))

        vector = Vector(np.dot(self.cob_matrix(), vector_coords))

        self.add(matrix)
        self.play(Write(vector_array))
        self.play(ShowCreation(vector))
        self.play(Blink(self.jenny))
        self.play(*it.chain(
            [
                Rotate(mob, np.pi/2, run_time = 3) 
                for mob in (self.jenny_plane, self.b1, self.b2, vector)
            ],
            list(map(Animation, [self.jenny, matrix, vector_array])),
        ))
        self.play(
            self.jenny.change_mode, "pondering",
            Write(equals),
            Write(result)
        )
        self.play(Blink(self.jenny))
        self.wait()

class MathematicalEmpathy(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "\\centering An expression like",
            "$A^{-1} M A$",
            "\\\\ suggests a mathematical \\\\",
            "sort of empathy"
        )
        A1, neg, one, M, A2 = words[1]
        As = VGroup(A1, neg, one, A2)
        VGroup(As, M).set_color(YELLOW)

        self.teacher_says(words)
        self.random_blink()
        for mob, color in (M, BLUE), (As, MAROON_B):
            self.play(mob.set_color, color)
            self.play(mob.scale_in_place, 1.2, rate_func = there_and_back)
            self.random_blink(2)

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("""
            Next video: Eigenvectors and eigenvalues
        """)
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()


















