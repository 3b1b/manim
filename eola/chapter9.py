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
from eola.chapter1 import plane_wave_homotopy

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

def get_small_bubble(pi_creature):
    pi_center_x = pi_creature.get_center()[0]
    kwargs = {
        "height" : 4,
        "bubble_center_adjustment_factor" : 1./6,
    }
    bubble = ThoughtBubble(**kwargs)
    bubble.stretch_to_fit_width(3)
    bubble.rotate(np.pi/4)
    if pi_center_x < 0:
        bubble.flip()
    bubble.next_to(pi_creature, UP, buff = MED_BUFF)
    bubble.to_edge(pi_center_x*RIGHT, buff = SMALL_BUFF)
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
        words.highlight_by_tex("same name ", BLUE)
        words.highlight_by_tex("different things", MAROON_B)
        # words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        author = TextMobject("-Henri Poincar\\'e.")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither(2)

class LinearCombinationScene(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : SPACE_WIDTH,
            "y_radius" : SPACE_HEIGHT,
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
            coord_mobs = map(TexMobject, map(str, numerical_coords))
            VGroup(*coord_mobs).set_fill(opacity = 0)
            for coord, basis in zip(coord_mobs, basis_vectors):
                coord.next_to(basis.label, LEFT)
        for coord, basis, scalar in zip(coord_mobs, basis_vectors, numerical_coords):
            basis.target = basis.copy().scale(scalar)
            basis.label.target = basis.label.copy()
            coord.target = coord.copy()
            new_label = VGroup(coord.target, basis.label.target)
            new_label.arrange_submobjects(aligned_edge = DOWN)
            new_label.move_to(
                basis.label, 
                aligned_edge = basis.get_center()-basis.label.get_center()
            )
            new_label.shift(
                basis.target.get_center() - basis.get_center()
            )
            coord.target.next_to(basis.label.target, LEFT)
            coord.target.set_fill(basis.get_color(), opacity = 1)
            self.play(*map(MoveToTarget, [
                coord, basis, basis.label
            ]))
            self.dither()
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
        self.dither(2)
        self.play(*it.chain(
            [basis.restore for basis in basis_vectors],
            [basis.label.restore for basis in basis_vectors],
            [FadeOut(coord) for coord in coord_mobs],
            [FadeOut(sum_vect) for x in [1] if show_sum_vect],
        ))

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
                coord.highlight, line.get_color(),
                coord.next_to, line.get_center(), direction,
                ShowCreation(line),                
            )
            self.dither()
        self.dither()
        self.play(*map(FadeOut, [x_coord, y_coord, x_line, y_line]))


    def show_abstract_scalar_idea(self, x_coord, y_coord):
        x_shift, y_shift = 4*LEFT, 4*RIGHT
        to_save = x_coord, y_coord, self.i_hat, self.j_hat
        for mob in to_save:
            mob.save_state()
        everything = VGroup(*self.get_mobjects())

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
        )
        self.play(*map(FadeIn, [self.i_hat, self.j_hat]))
        self.dither()
        self.play(Transform(self.i_hat, scaled_i))
        self.play(Transform(self.j_hat, scaled_j))
        self.dither()
        self.play(
            FadeIn(everything),
            *[mob.restore for mob in to_save]
        )
        self.dither()

    def scale_basis_vectors(self, x_coord, y_coord):
        self.play(*map(Write, [self.i_hat.label, self.j_hat.label]))
        self.show_linear_combination(
            self.vector_coords, 
            basis_vectors = [self.i_hat, self.j_hat],
            coord_mobs = [x_coord, y_coord]
        )

    def list_implicit_assumptions(self, x_coord, y_coord):
        everything = VGroup(*self.get_mobjects())
        title = TextMobject("Implicit assumptions")
        h_line = Line(title.get_left(), title.get_right())
        h_line.highlight(YELLOW)
        h_line.next_to(title, DOWN)
        title.add(h_line)

        ass1 = TextMobject("-First coordinate")
        ass1 = VGroup(ass1, self.i_hat.copy())
        ass1.arrange_submobjects(buff = MED_BUFF)

        ass2 = TextMobject("-Second coordinate")
        ass2 = VGroup(ass2, self.j_hat.copy())
        ass2.arrange_submobjects(buff = MED_BUFF)

        ass3 = TextMobject("-Unit of distance")

        group = VGroup(title, ass1, ass2, ass3)
        group.arrange_submobjects(DOWN, aligned_edge = LEFT, buff = MED_BUFF)
        group.to_corner(UP+LEFT)
        # VGroup(*group[1:]).shift(0.5*DOWN)
        for words in group:
            words.add_to_back(BackgroundRectangle(words))

        self.play(Write(title))
        self.dither()
        self.play(
            Write(ass1),
            ApplyFunction(
                lambda m : m.rotate(np.pi/6).highlight(X_COLOR),
                x_coord,
                rate_func = wiggle
            )
        )
        self.dither()
        self.play(
            Write(ass2),
            ApplyFunction(
                lambda m : m.rotate(np.pi/6).highlight(Y_COLOR),
                y_coord,
                rate_func = wiggle
            )
        )
        self.dither()
        self.play(Write(ass3))
        self.dither(2)
        keepers = VGroup(*[
            self.i_hat, self.j_hat,
            self.i_hat.label, self.j_hat.label
        ])
        self.play(
            FadeOut(everything),
            Animation(keepers.copy()),
            Animation(group)
        )
        self.dither()

class NameCoordinateSystem(Scene):
    def construct(self):
        vector = Vector([3, 2])
        coords = Matrix([3, 2])
        arrow = TexMobject("\\Rightarrow")
        vector.next_to(arrow, RIGHT, buff = 0)
        coords.next_to(arrow, LEFT, buff = 2*MED_BUFF)
        group = VGroup(coords, arrow, vector)
        group.shift(2*UP)
        coordinate_system = TextMobject("``Coordinate system''")
        coordinate_system.next_to(arrow, UP, buff = LARGE_BUFF)

        i_hat, j_hat = Vector([1, 0]), Vector([0, 1])
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        i_label = TexMobject("\\hat{\\imath}")
        i_label.highlight(X_COLOR)
        i_label.next_to(i_hat, DOWN)
        j_label = TexMobject("\\hat{\\jmath}")
        j_label.highlight(Y_COLOR)
        j_label.next_to(j_hat, LEFT)
        basis_group = VGroup(i_hat, j_hat, i_label, j_label)
        basis_group.shift(DOWN)
        basis_words = TextMobject("``Basis vectors''")
        basis_words.shift(basis_group.get_bottom()[1]*UP+MED_BUFF*DOWN)

        self.play(Write(coords))
        self.play(Write(arrow), ShowCreation(vector))
        self.dither()
        self.play(Write(coordinate_system))
        self.dither(2)
        self.play(Write(basis_group))
        self.play(Write(basis_words))
        self.dither()

class JenniferScene(LinearCombinationScene):
    CONFIG = {
        "b1_coords" : [2, 1],
        "b2_coords" : [-1, 1],
        "foreground_plane_kwargs" : {
            "x_radius" : SPACE_WIDTH,
            "y_radius" : SPACE_WIDTH,
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
            vect.label = self.get_vector_label(
                vect, "\\vec{\\textbf{b}}_%d"%(i+1),
                direction = "right",
                color = vect.get_color()
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
        self.dither()

    def add_basis_vectors(self):
        words = TextMobject("Alternate basis vectors")
        words.shift(2.5*UP)
        self.play(Write(words, run_time = 2))
        for vect in self.b1, self.b2:
            self.play(
                ShowCreation(vect),
                Write(vect.label)
            )
            self.dither()
        self.play(FadeOut(words))
        self.basis_vectors = VGroup(
            self.b1, self.b2, self.b1.label, self.b2.label
        )

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
        new_coords_mob.scale_to_fit_height(jenny.coords.get_height())
        new_coords_mob.move_to(jenny.coords)

        for coords in you.coords, jenny.coords, new_coords_mob:
            for entry in coords.get_entries():
                entry.add_background_rectangle()

        self.play(ShowCreation(v))
        self.dither()
        self.play(*it.chain(
            map(FadeIn, [
                self.plane, self.i_hat, self.j_hat, 
                self.i_hat.label, self.j_hat.label,
                you
            ]),
            map(Animation, [jenny, v]),
            map(FadeOut, self.basis_vectors),
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
            map(FadeOut, [
                self.plane, self.i_hat, self.j_hat,  
                self.i_hat.label, self.j_hat.label,
                you.bubble, you.coords
            ]),
            map(FadeIn, [self.jenny_plane, self.basis_vectors]),
            map(Animation, [v, you, jenny]),
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
            new_label.arrange_submobjects(aligned_edge = DOWN)
            new_label.move_to(
                basis.label, 
                aligned_edge = basis.get_center()-basis.label.get_center()
            )
            new_label.shift(
                basis.target.get_center() - basis.get_center()
            )
            coord.target.next_to(basis.label.target, LEFT)
            coord.target.set_fill(basis.get_color(), opacity = 1)
            self.play(*map(MoveToTarget, [
                coord, basis, basis.label
            ]))
            self.dither()
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
        self.dither(2)


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
        i_sym.highlight(X_COLOR).move_to(new_label1.target[1], aligned_edge = LEFT)
        j_sym.highlight(Y_COLOR).move_to(new_label2.target[1], aligned_edge = LEFT)
        Transform(new_label1.target[1], i_sym).update(1)
        Transform(new_label2.target[1], j_sym).update(1)
        sum_vect.target = Vector(numerical_coords)
        self.play(
            Transform(self.jenny_plane, self.plane),
            Transform(self.jenny.bubble, self.you.bubble),
            self.you.change_mode, "speaking",
            self.jenny.change_mode, "erm",
            *map(MoveToTarget, [
                self.jenny.coords,
                b1, b2, new_label1, new_label2, sum_vect
            ])
        )
        self.play(Blink(self.you))
        self.dither()

        self.play(*it.chain(
            map(FadeOut, [
                self.jenny.bubble, self.jenny.coords, 
                coord_mobs, sum_vect
            ]),
            [
                ApplyMethod(pi.change_mode, "plain") 
                for pi in self.jenny, self.you
            ],
            [mob.restore for mob in b1, b2, b1.label, b2.label]
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
            b1_coords.mover.highlight, X_COLOR
        )
        self.play(Blink(you))
        self.dither()
        self.play(Transform(b1_coords, b2_coords))
        self.play(
            b2_coords.mover.next_to, self.b2.get_end(), LEFT,
            b2_coords.mover.highlight, Y_COLOR
        )
        self.play(Blink(jenny))
        for coords, array in (b1_coords, [1, 0]), (b2_coords, [0, 1]):
            mover = coords.mover
            array_mob = Matrix(array)
            array_mob.highlight(mover.get_color())
            array_mob.scale_to_fit_height(mover.get_height())
            array_mob.move_to(mover)
            array_mob.add_to_back(BackgroundRectangle(array_mob))
            mover.target = array_mob
        self.play(
            self.jenny_plane.restore,
            FadeOut(self.you.bubble),
            FadeOut(b1_coords),
            self.jenny.change_mode, "speaking",
            self.you.change_mode, "confused",
            *map(Animation, [
                self.basis_vectors,
                b1_coords.mover,
                b2_coords.mover,
            ])
        )
        self.play(MoveToTarget(b1_coords.mover))
        self.play(MoveToTarget(b2_coords.mover))
        self.play(Blink(self.jenny))

class SpeakingDifferentLanguages(JenniferScene):
    def construct(self):
        jenny, you = self.jenny, self.you
        vector = Vector([3, 2])
        vector.center().shift(DOWN)
        you.coords = Matrix([3, 2])
        jenny.coords = Matrix(["5/3", "1/3"])
        for pi in jenny, you:
            pi.bubble = pi.get_bubble("speech", width = 4)
            pi.bubble.add_content(pi.coords)
        self.play(
            ShowCreation(vector),
            you.look_at, vector,
            jenny.look_at, vector,
        )
        for pi in you, jenny:
            self.play(
                pi.change_mode, "speaking",
                ShowCreation(pi.bubble),
                Write(pi.coords)
            )
            self.play(Blink(pi))
        self.dither()

class ShowGrid(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
    }
    def construct(self):
        self.remove(self.i_hat, self.j_hat)
        self.dither()
        self.plane.prepare_for_nonlinear_transform()
        self.play(Homotopy(plane_wave_homotopy, self.plane))
        self.play(self.plane.center)
        for vect in self.i_hat, self.j_hat:
            self.play(ShowCreation(vect))
        self.dither()

class GridIsAConstruct(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            \\centering 
            The grid is
            just a construct
        """)
        self.change_student_modes(*["pondering"]*3)
        self.random_blink(2)

























