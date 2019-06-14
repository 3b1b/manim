import numpy as np

from manimlib.animation.animation import Animation
from manimlib.animation.creation import ShowCreation
from manimlib.animation.creation import Write
from manimlib.animation.fading import FadeOut
from manimlib.animation.growing import GrowArrow
from manimlib.animation.transform import ApplyFunction
from manimlib.animation.transform import ApplyPointwiseFunction
from manimlib.animation.transform import Transform
from manimlib.constants import *
from manimlib.mobject.coordinate_systems import Axes
from manimlib.mobject.coordinate_systems import NumberPlane
from manimlib.mobject.geometry import Arrow
from manimlib.mobject.geometry import Dot
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import Vector
from manimlib.mobject.matrix import Matrix
from manimlib.mobject.matrix import VECTOR_LABEL_SCALE_FACTOR
from manimlib.mobject.matrix import vector_coordinate_label
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.scene.scene import Scene
from manimlib.utils.rate_functions import rush_from
from manimlib.utils.rate_functions import rush_into
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import get_norm

X_COLOR = GREEN_C
Y_COLOR = RED_C
Z_COLOR = BLUE_D


# TODO: Much of this scene type seems dependent on the coordinate system chosen.
# That is, being centered at the origin with grid units corresponding to the
# arbitrary space units.  Change it!
#
# Also, methods I would have thought of as getters, like coords_to_vector, are
# actually doing a lot of animating.
class VectorScene(Scene):
    CONFIG = {
        "basis_vector_stroke_width": 6
    }

    def add_plane(self, animate=False, **kwargs):
        plane = NumberPlane(**kwargs)
        if animate:
            self.play(ShowCreation(plane, lag_ratio=0.5))
        self.add(plane)
        return plane

    def add_axes(self, animate=False, color=WHITE, **kwargs):
        axes = Axes(color=color, tick_frequency=1)
        if animate:
            self.play(ShowCreation(axes))
        self.add(axes)
        return axes

    def lock_in_faded_grid(self, dimness=0.7, axes_dimness=0.5):
        plane = self.add_plane()
        axes = plane.get_axes()
        plane.fade(dimness)
        axes.set_color(WHITE)
        axes.fade(axes_dimness)
        self.add(axes)
        self.freeze_background()

    def get_vector(self, numerical_vector, **kwargs):
        return Arrow(
            self.plane.coords_to_point(0, 0),
            self.plane.coords_to_point(*numerical_vector[:2]),
            buff=0,
            **kwargs
        )

    def add_vector(self, vector, color=YELLOW, animate=True, **kwargs):
        if not isinstance(vector, Arrow):
            vector = Vector(vector, color=color, **kwargs)
        if animate:
            self.play(GrowArrow(vector))
        self.add(vector)
        return vector

    def write_vector_coordinates(self, vector, **kwargs):
        coords = vector_coordinate_label(vector, **kwargs)
        self.play(Write(coords))
        return coords

    def get_basis_vectors(self, i_hat_color=X_COLOR, j_hat_color=Y_COLOR):
        return VGroup(*[
            Vector(
                vect,
                color=color,
                stroke_width=self.basis_vector_stroke_width
            )
            for vect, color in [
                ([1, 0], i_hat_color),
                ([0, 1], j_hat_color)
            ]
        ])

    def get_basis_vector_labels(self, **kwargs):
        i_hat, j_hat = self.get_basis_vectors()
        return VGroup(*[
            self.get_vector_label(
                vect, label, color=color,
                label_scale_factor=1,
                **kwargs
            )
            for vect, label, color in [
                (i_hat, "\\hat{\\imath}", X_COLOR),
                (j_hat, "\\hat{\\jmath}", Y_COLOR),
            ]
        ])

    def get_vector_label(self, vector, label,
                         at_tip=False,
                         direction="left",
                         rotate=False,
                         color=None,
                         label_scale_factor=VECTOR_LABEL_SCALE_FACTOR):
        if not isinstance(label, TexMobject):
            if len(label) == 1:
                label = "\\vec{\\textbf{%s}}" % label
            label = TexMobject(label)
            if color is None:
                color = vector.get_color()
            label.set_color(color)
        label.scale(label_scale_factor)
        label.add_background_rectangle()

        if at_tip:
            vect = vector.get_vector()
            vect /= get_norm(vect)
            label.next_to(vector.get_end(), vect, buff=SMALL_BUFF)
        else:
            angle = vector.get_angle()
            if not rotate:
                label.rotate(-angle, about_point=ORIGIN)
            if direction == "left":
                label.shift(-label.get_bottom() + 0.1 * UP)
            else:
                label.shift(-label.get_top() + 0.1 * DOWN)
            label.rotate(angle, about_point=ORIGIN)
            label.shift((vector.get_end() - vector.get_start()) / 2)
        return label

    def label_vector(self, vector, label, animate=True, **kwargs):
        label = self.get_vector_label(vector, label, **kwargs)
        if animate:
            self.play(Write(label, run_time=1))
        self.add(label)
        return label

    def position_x_coordinate(self, x_coord, x_line, vector):
        x_coord.next_to(x_line, -np.sign(vector[1]) * UP)
        x_coord.set_color(X_COLOR)
        return x_coord

    def position_y_coordinate(self, y_coord, y_line, vector):
        y_coord.next_to(y_line, np.sign(vector[0]) * RIGHT)
        y_coord.set_color(Y_COLOR)
        return y_coord

    def coords_to_vector(self, vector, coords_start=2 * RIGHT + 2 * UP, clean_up=True):
        starting_mobjects = list(self.mobjects)
        array = Matrix(vector)
        array.shift(coords_start)
        arrow = Vector(vector)
        x_line = Line(ORIGIN, vector[0] * RIGHT)
        y_line = Line(x_line.get_end(), arrow.get_end())
        x_line.set_color(X_COLOR)
        y_line.set_color(Y_COLOR)
        x_coord, y_coord = array.get_mob_matrix().flatten()

        self.play(Write(array, run_time=1))
        self.wait()
        self.play(ApplyFunction(
            lambda x: self.position_x_coordinate(x, x_line, vector),
            x_coord
        ))
        self.play(ShowCreation(x_line))
        self.play(
            ApplyFunction(
                lambda y: self.position_y_coordinate(y, y_line, vector),
                y_coord
            ),
            FadeOut(array.get_brackets())
        )
        y_coord, brackets = self.get_mobjects_from_last_animation()
        self.play(ShowCreation(y_line))
        self.play(ShowCreation(arrow))
        self.wait()
        if clean_up:
            self.clear()
            self.add(*starting_mobjects)

    def vector_to_coords(self, vector, integer_labels=True, clean_up=True):
        starting_mobjects = list(self.mobjects)
        show_creation = False
        if isinstance(vector, Arrow):
            arrow = vector
            vector = arrow.get_end()[:2]
        else:
            arrow = Vector(vector)
            show_creation = True
        array = vector_coordinate_label(arrow, integer_labels=integer_labels)
        x_line = Line(ORIGIN, vector[0] * RIGHT)
        y_line = Line(x_line.get_end(), arrow.get_end())
        x_line.set_color(X_COLOR)
        y_line.set_color(Y_COLOR)
        x_coord, y_coord = array.get_mob_matrix().flatten()
        x_coord_start = self.position_x_coordinate(
            x_coord.copy(), x_line, vector
        )
        y_coord_start = self.position_y_coordinate(
            y_coord.copy(), y_line, vector
        )
        brackets = array.get_brackets()

        if show_creation:
            self.play(ShowCreation(arrow))
        self.play(
            ShowCreation(x_line),
            Write(x_coord_start),
            run_time=1
        )
        self.play(
            ShowCreation(y_line),
            Write(y_coord_start),
            run_time=1
        )
        self.wait()
        self.play(
            Transform(x_coord_start, x_coord, lag_ratio=0),
            Transform(y_coord_start, y_coord, lag_ratio=0),
            Write(brackets, run_time=1),
        )
        self.wait()

        self.remove(x_coord_start, y_coord_start, brackets)
        self.add(array)
        if clean_up:
            self.clear()
            self.add(*starting_mobjects)
        return array, x_line, y_line

    def show_ghost_movement(self, vector):
        if isinstance(vector, Arrow):
            vector = vector.get_end() - vector.get_start()
        elif len(vector) == 2:
            vector = np.append(np.array(vector), 0.0)
        x_max = int(FRAME_X_RADIUS + abs(vector[0]))
        y_max = int(FRAME_Y_RADIUS + abs(vector[1]))
        dots = VMobject(*[
            Dot(x * RIGHT + y * UP)
            for x in range(-x_max, x_max)
            for y in range(-y_max, y_max)
        ])
        dots.set_fill(BLACK, opacity=0)
        dots_halfway = dots.copy().shift(vector / 2).set_fill(WHITE, 1)
        dots_end = dots.copy().shift(vector)

        self.play(Transform(
            dots, dots_halfway, rate_func=rush_into
        ))
        self.play(Transform(
            dots, dots_end, rate_func=rush_from
        ))
        self.remove(dots)


class LinearTransformationScene(VectorScene):
    CONFIG = {
        "include_background_plane": True,
        "include_foreground_plane": True,
        "foreground_plane_kwargs": {
            "x_max": FRAME_WIDTH / 2,
            "x_min": -FRAME_WIDTH / 2,
            "y_max": FRAME_WIDTH / 2,
            "y_min": -FRAME_WIDTH / 2,
            "faded_line_ratio": 0
        },
        "background_plane_kwargs": {
            "color": GREY,
            "axis_config": {
                "stroke_color": LIGHT_GREY,
            },
            "number_line_config": {
                "color": GREY,
            },
            "background_line_style": {
                "stroke_color": GREY,
                "stroke_width": 1,
            },
        },
        "show_coordinates": False,
        "show_basis_vectors": True,
        "basis_vector_stroke_width": 6,
        "i_hat_color": X_COLOR,
        "j_hat_color": Y_COLOR,
        "leave_ghost_vectors": False,
        "t_matrix": [[3, 0], [1, 2]],
    }

    def setup(self):
        # The has_already_setup attr is to not break all the old Scenes
        if hasattr(self, "has_already_setup"):
            return
        self.has_already_setup = True
        self.background_mobjects = []
        self.foreground_mobjects = []
        self.transformable_mobjects = []
        self.moving_vectors = []
        self.transformable_labels = []
        self.moving_mobjects = []

        self.t_matrix = np.array(self.t_matrix)
        self.background_plane = NumberPlane(
            **self.background_plane_kwargs
        )

        if self.show_coordinates:
            self.background_plane.add_coordinates()
        if self.include_background_plane:
            self.add_background_mobject(self.background_plane)
        if self.include_foreground_plane:
            self.plane = NumberPlane(**self.foreground_plane_kwargs)
            self.add_transformable_mobject(self.plane)
        if self.show_basis_vectors:
            self.basis_vectors = self.get_basis_vectors(
                i_hat_color=self.i_hat_color,
                j_hat_color=self.j_hat_color,
            )
            self.moving_vectors += list(self.basis_vectors)
            self.i_hat, self.j_hat = self.basis_vectors
            self.add(self.basis_vectors)

    def add_special_mobjects(self, mob_list, *mobs_to_add):
        for mobject in mobs_to_add:
            if mobject not in mob_list:
                mob_list.append(mobject)
                self.add(mobject)

    def add_background_mobject(self, *mobjects):
        self.add_special_mobjects(self.background_mobjects, *mobjects)

    # TODO, this conflicts with Scene.add_fore
    def add_foreground_mobject(self, *mobjects):
        self.add_special_mobjects(self.foreground_mobjects, *mobjects)

    def add_transformable_mobject(self, *mobjects):
        self.add_special_mobjects(self.transformable_mobjects, *mobjects)

    def add_moving_mobject(self, mobject, target_mobject=None):
        mobject.target = target_mobject
        self.add_special_mobjects(self.moving_mobjects, mobject)

    def get_unit_square(self, color=YELLOW, opacity=0.3, stroke_width=3):
        square = self.square = Rectangle(
            color=color,
            width=self.plane.get_x_unit_size(),
            height=self.plane.get_y_unit_size(),
            stroke_color=color,
            stroke_width=stroke_width,
            fill_color=color,
            fill_opacity=opacity
        )
        square.move_to(self.plane.coords_to_point(0, 0), DL)
        return square

    def add_unit_square(self, animate=False, **kwargs):
        square = self.get_unit_square(**kwargs)
        if animate:
            self.play(
                DrawBorderThenFill(square),
                Animation(Group(*self.moving_vectors))
            )
        self.add_transformable_mobject(square)
        self.bring_to_front(*self.moving_vectors)
        self.square = square
        return self

    def add_vector(self, vector, color=YELLOW, **kwargs):
        vector = VectorScene.add_vector(
            self, vector, color=color, **kwargs
        )
        self.moving_vectors.append(vector)
        return vector

    def write_vector_coordinates(self, vector, **kwargs):
        coords = VectorScene.write_vector_coordinates(self, vector, **kwargs)
        self.add_foreground_mobject(coords)
        return coords

    def add_transformable_label(
            self, vector, label,
            transformation_name="L",
            new_label=None,
            **kwargs):
        label_mob = self.label_vector(vector, label, **kwargs)
        if new_label:
            label_mob.target_text = new_label
        else:
            label_mob.target_text = "%s(%s)" % (
                transformation_name,
                label_mob.get_tex_string()
            )
        label_mob.vector = vector
        label_mob.kwargs = kwargs
        if "animate" in label_mob.kwargs:
            label_mob.kwargs.pop("animate")
        self.transformable_labels.append(label_mob)
        return label_mob

    def add_title(self, title, scale_factor=1.5, animate=False):
        if not isinstance(title, Mobject):
            title = TextMobject(title).scale(scale_factor)
        title.to_edge(UP)
        title.add_background_rectangle()
        if animate:
            self.play(Write(title))
        self.add_foreground_mobject(title)
        self.title = title
        return self

    def get_matrix_transformation(self, matrix):
        return self.get_transposed_matrix_transformation(np.array(matrix).T)

    def get_transposed_matrix_transformation(self, transposed_matrix):
        transposed_matrix = np.array(transposed_matrix)
        if transposed_matrix.shape == (2, 2):
            new_matrix = np.identity(3)
            new_matrix[:2, :2] = transposed_matrix
            transposed_matrix = new_matrix
        elif transposed_matrix.shape != (3, 3):
            raise Exception("Matrix has bad dimensions")
        return lambda point: np.dot(point, transposed_matrix)

    def get_piece_movement(self, pieces):
        start = VGroup(*pieces)
        target = VGroup(*[mob.target for mob in pieces])
        if self.leave_ghost_vectors:
            self.add(start.copy().fade(0.7))
        return Transform(start, target, lag_ratio=0)

    def get_moving_mobject_movement(self, func):
        for m in self.moving_mobjects:
            if m.target is None:
                m.target = m.copy()
            target_point = func(m.get_center())
            m.target.move_to(target_point)
        return self.get_piece_movement(self.moving_mobjects)

    def get_vector_movement(self, func):
        for v in self.moving_vectors:
            v.target = Vector(func(v.get_end()), color=v.get_color())
            norm = get_norm(v.target.get_end())
            if norm < 0.1:
                v.target.get_tip().scale_in_place(norm)
        return self.get_piece_movement(self.moving_vectors)

    def get_transformable_label_movement(self):
        for l in self.transformable_labels:
            l.target = self.get_vector_label(
                l.vector.target, l.target_text, **l.kwargs
            )
        return self.get_piece_movement(self.transformable_labels)

    def apply_matrix(self, matrix, **kwargs):
        self.apply_transposed_matrix(np.array(matrix).T, **kwargs)

    def apply_inverse(self, matrix, **kwargs):
        self.apply_matrix(np.linalg.inv(matrix), **kwargs)

    def apply_transposed_matrix(self, transposed_matrix, **kwargs):
        func = self.get_transposed_matrix_transformation(transposed_matrix)
        if "path_arc" not in kwargs:
            net_rotation = np.mean([
                angle_of_vector(func(RIGHT)),
                angle_of_vector(func(UP)) - np.pi / 2
            ])
            kwargs["path_arc"] = net_rotation
        self.apply_function(func, **kwargs)

    def apply_inverse_transpose(self, t_matrix, **kwargs):
        t_inv = np.linalg.inv(np.array(t_matrix).T).T
        self.apply_transposed_matrix(t_inv, **kwargs)

    def apply_nonlinear_transformation(self, function, **kwargs):
        self.plane.prepare_for_nonlinear_transform()
        self.apply_function(function, **kwargs)

    def apply_function(self, function, added_anims=[], **kwargs):
        if "run_time" not in kwargs:
            kwargs["run_time"] = 3
        anims = [
            ApplyPointwiseFunction(function, t_mob)
            for t_mob in self.transformable_mobjects
        ] + [
            self.get_vector_movement(function),
            self.get_transformable_label_movement(),
            self.get_moving_mobject_movement(function),
        ] + [
            Animation(f_mob)
            for f_mob in self.foreground_mobjects
        ] + added_anims
        self.play(*anims, **kwargs)
