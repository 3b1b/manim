import numpy as np

from scene import Scene
from mobject import Mobject
from mobject.vectorized_mobject import VMobject
from mobject.tex_mobject import TexMobject, TextMobject
from animation.transform import ApplyPointwiseFunction, Transform, \
    ApplyMethod, FadeOut, ApplyFunction
from animation.simple_animations import ShowCreation, Write
from topics.number_line import NumberPlane, Axes
from topics.geometry import Vector, Line, Circle, Arrow, Dot

from helpers import *
from eola.matrix import Matrix, VECTOR_LABEL_SCALE_VAL, vector_coordinate_label


X_COLOR = GREEN_C
Y_COLOR = RED_C
Z_COLOR = BLUE_D


class VectorScene(Scene):
    CONFIG = {
        "basis_vector_stroke_width" : 6
    }
    def add_plane(self, animate = False, **kwargs):
        plane = NumberPlane(**kwargs)
        if animate:
            self.play(ShowCreation(plane, submobject_mode = "lagged_start"))
        self.add(plane)
        return plane

    def add_axes(self, animate = False, color = WHITE, **kwargs):
        axes = Axes(color = color, tick_frequency = 1)
        if animate:
            self.play(ShowCreation(axes, submobject_mode = "one_at_a_time"))
        self.add(axes)
        return axes

    def lock_in_faded_grid(self, dimness = 0.7, axes_dimness = 0.5):
        plane = self.add_plane()
        axes = plane.get_axes()
        plane.fade(dimness)
        axes.highlight(WHITE)
        axes.fade(axes_dimness)
        self.add(axes)
        self.freeze_background()

    def add_vector(self, vector, animate = True, color = YELLOW):
        if not isinstance(vector, Arrow):
            vector = Vector(vector, color = color)
        if animate:
            self.play(ShowCreation(vector, submobject_mode = "one_at_a_time"))
        self.add(vector)
        return vector

    def get_basis_vectors(self):
        return [
            Vector(
                vect, color = color, 
                stroke_width = self.basis_vector_stroke_width
            )
            for vect, color in [
                ([1, 0], X_COLOR), 
                ([0, 1], Y_COLOR)
            ]
        ]

    def get_basis_vector_labels(self, animate = False, **kwargs):
        i_hat, j_hat = self.get_basis_vectors()
        return [
            self.label_vector(
                vect, label, color = color, 
                animate = animate, 
                label_scale_val = 1,
                **kwargs
            )
            for vect, label , color in [
                (i_hat, "\\hat{\\imath}", X_COLOR),
                (j_hat, "\\hat{\\jmath}", Y_COLOR),
            ]
        ]

    def label_vector(self, vector, label, animate = True, 
                     direction = "left", rotate = False,
                     color = WHITE, add_to_vector = False,
                     buff_factor = 2, 
                     label_scale_val = VECTOR_LABEL_SCALE_VAL):
        if len(label) == 1:
            label = "\\vec{\\textbf{%s}}"%label
        label = TexMobject(label)
        label.highlight(color)        
        label.scale(label_scale_val)
        if rotate:
            label.rotate(vector.get_angle())

        vector_vect = vector.get_end() - vector.get_start()
        if direction is "left":
            rot_angle = -np.pi/2
        else:
            rot_angle = np.pi/2
        boundary_dir = -np.round(rotate_vector(vector_vect, rot_angle))
        boundary_point = label.get_critical_point(boundary_dir)
        label.shift(buff_factor*boundary_point)
        label.shift(vector_vect/2.)

        if add_to_vector:
            vector.add(label)
        if animate:
            self.play(Write(label, run_time = 1))
        self.add(label)
        return label

    def position_x_coordinate(self, x_coord, x_line, vector):
        x_coord.next_to(x_line, -np.sign(vector[1])*UP)
        x_coord.highlight(X_COLOR)
        return x_coord

    def position_y_coordinate(self, y_coord, y_line, vector):
        y_coord.next_to(y_line, np.sign(vector[0])*RIGHT)
        y_coord.highlight(Y_COLOR)
        return y_coord

    def coords_to_vector(self, vector, coords_start = 2*RIGHT+2*UP, clean_up = True):
        starting_mobjects = list(self.mobjects)
        array = Matrix(vector)
        array.shift(coords_start)
        arrow = Vector(vector)
        x_line = Line(ORIGIN, vector[0]*RIGHT)
        y_line = Line(x_line.get_end(), arrow.get_end())
        x_line.highlight(X_COLOR)
        y_line.highlight(Y_COLOR)
        x_coord, y_coord = array.get_mob_matrix().flatten()

        self.play(Write(array, run_time = 1))
        self.dither()
        self.play(ApplyFunction(
            lambda x : self.position_x_coordinate(x, x_line, vector),
            x_coord
        ))
        self.play(ShowCreation(x_line))
        self.play(
            ApplyFunction(
                lambda y : self.position_y_coordinate(y, y_line, vector),
                y_coord
            ),
            FadeOut(array.get_brackets())
        )
        y_coord, brackets = self.get_mobjects_from_last_animation()
        self.play(ShowCreation(y_line))
        self.play(ShowCreation(arrow))
        self.dither()
        if clean_up:
            self.clear()
            self.add(*starting_mobjects)

    def vector_to_coords(self, vector, integer_labels = True, clean_up = True):
        starting_mobjects = list(self.mobjects)
        show_creation = False
        if isinstance(vector, Arrow):
            arrow = vector
            vector = arrow.get_end()[:2]
        else:
            arrow = Vector(vector)
            show_creation = True
        array = vector_coordinate_label(arrow, integer_labels = integer_labels)
        x_line = Line(ORIGIN, vector[0]*RIGHT)
        y_line = Line(x_line.get_end(), arrow.get_end())
        x_line.highlight(X_COLOR)
        y_line.highlight(Y_COLOR)
        x_coord, y_coord = array.get_mob_matrix().flatten()
        x_coord_start = self.position_x_coordinate(
            x_coord.copy(), x_line, vector
        )
        y_coord_start = self.position_y_coordinate(
            y_coord.copy(), y_line, vector
        )
        brackets = array.get_brackets()

        if show_creation:
            self.play(ShowCreation(arrow, submobject_mode = "one_at_a_time"))
        self.play(
            ShowCreation(x_line),
            Write(x_coord_start),
            run_time = 1
        )
        self.play(
            ShowCreation(y_line),
            Write(y_coord_start),
            run_time = 1
        )
        self.dither()
        self.play(
            Transform(x_coord_start, x_coord),
            Transform(y_coord_start, y_coord),
            Write(brackets),
            run_time = 1
        )
        self.dither()

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
        x_max = int(SPACE_WIDTH + abs(vector[0]))
        y_max = int(SPACE_HEIGHT + abs(vector[1]))
        dots = VMobject(*[
            Dot(x*RIGHT + y*UP)
            for x in range(-x_max, x_max)
            for y in range(-y_max, y_max)
        ])
        dots.set_fill(BLACK, opacity = 0)
        dots_halfway = dots.copy().shift(vector/2).set_fill(WHITE, 1)
        dots_end = dots.copy().shift(vector)

        self.play(Transform(
            dots, dots_halfway, rate_func = rush_into
        ))
        self.play(Transform(
            dots, dots_end, rate_func = rush_from
        ))
        self.remove(dots)



class LinearTransformationScene(VectorScene):
    CONFIG = {
        "include_background_plane" : True,
        "include_foreground_plane" : True,
        "foreground_plane_kwargs" : {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_HEIGHT,
            "secondary_line_ratio" : 0
        },
        "background_plane_kwargs" : {
            "color" : GREY,
            "secondary_color" : DARK_GREY,
            "axes_color" : GREY,
            "stroke_width" : 2,
        },
        "show_coordinates" : False,
        "show_basis_vectors" : True,
        "i_hat_color" : X_COLOR,
        "j_hat_color" : Y_COLOR,
    }
    def setup(self):
        self.background_mobjects = []
        self.transformable_mobject = []
        self.moving_vectors = []

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
            self.add_vector((1, 0), self.i_hat_color)
            self.add_vector((0, 1), self.j_hat_color)

    def add_background_mobject(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.background_mobjects:
                self.background_mobjects.append(mobject)
                self.add(mobject)
            
    def add_transformable_mobject(self, *mobjects):
        for mobject in mobjects:
            if mobject not in self.transformable_mobject:
                self.transformable_mobject.append(mobject)
                self.add(mobject)

    def add_vector(self, vector, color = YELLOW, animate = False):
        vector = VectorScene.add_vector(
            self, vector, color = color, animate = animate
        )
        self.moving_vectors.append(vector)
        return vector

    def get_matrix_transformation(self, transposed_matrix):
        transposed_matrix = np.array(transposed_matrix)
        if transposed_matrix.shape == (2, 2):
            new_matrix = np.identity(3)
            new_matrix[:2, :2] = transposed_matrix
            transposed_matrix = new_matrix
        elif transposed_matrix.shape != (3, 3):
            raise "Matrix has bad dimensions"
        return lambda point: np.dot(point, transposed_matrix)


    def get_vector_movement(self, func):
        start = VMobject(*self.moving_vectors)       
        target = VMobject(*[
            Vector(func(v.get_end()), color = v.get_color())
            for v in self.moving_vectors
        ])
        return Transform(start, target)

    def apply_transposed_matrix(self, transposed_matrix, **kwargs):
        func = self.get_matrix_transformation(transposed_matrix)
        if "path_arc" not in kwargs:
            net_rotation = np.mean([
                angle_of_vector(func(RIGHT)),
                angle_of_vector(func(UP))-np.pi/2
            ])
            kwargs["path_arc"] = net_rotation
        self.apply_function(func, **kwargs)

    def apply_nonlinear_transformation(self, function, **kwargs):
        self.plane.prepare_for_nonlinear_transform(100)
        self.apply_function(function, **kwargs)

    def apply_function(self, function, **kwargs):
        if "run_time" not in kwargs:
            kwargs["run_time"] = 3
        self.play(
            ApplyPointwiseFunction(
                function,
                VMobject(*self.transformable_mobject),
            ),
            self.get_vector_movement(function),
            **kwargs
        )











