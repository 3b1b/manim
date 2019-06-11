#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys

from manimlib.imports import *

ARROW_CONFIG = {"stroke_width" : 2*DEFAULT_STROKE_WIDTH}
LIGHT_RED = RED_E

def matrix_to_string(matrix):
    return "--".join(["-".join(map(str, row)) for row in matrix])

def matrix_mobject(matrix):
    return TextMobject(
        """
        \\left(
            \\begin{array}{%s}
                %d & %d \\\\
                %d & %d
            \\end{array}
        \\right)
        """%tuple(["c"*matrix.shape[1]] + list(matrix.flatten())),
        size = "\\Huge"
    )

class ShowMultiplication(NumberLineScene):
    args_list = [
        (2, True),
        (0.5, True),
        (-3, True),
        (-3, True),
        (2, True),
        (6, True),
    ]
    @staticmethod
    def args_to_string(num, show_original_line):
        end_string = "WithCopiedOriginalLine" if show_original_line else ""
        return str(num) + end_string
    @staticmethod
    def string_to_args(string):
        parts = string.split()
        if len(parts) == 2:
            num, original_line = parts
            show_original_line = original_line == "WithCopiedOriginalLine"
            return float(num), False
        else:
            return float(parts[0]), False

    def construct(self, num, show_original_line):
        config = {
            "density" : max(abs(num), 1)*DEFAULT_POINT_DENSITY_1D,
            "stroke_width" : 2*DEFAULT_STROKE_WIDTH
        }
        if abs(num) < 1:
            config["numerical_radius"] = FRAME_X_RADIUS/num

        NumberLineScene.construct(self, **config)
        if show_original_line:
            self.copy_original_line()
        self.wait()
        self.show_multiplication(num, run_time = 1.5)
        self.wait()

    def copy_original_line(self):
        copied_line = deepcopy(self.number_line)
        copied_num_mobs = deepcopy(self.number_mobs)
        self.play(
            ApplyFunction(
                lambda m : m.shift(DOWN).set_color("lightgreen"), 
                copied_line
            ), *[
                ApplyMethod(mob.shift, DOWN)
                for mob in copied_num_mobs
            ]
        )
        self.wait()

class ExamplesOfOneDimensionalLinearTransforms(ShowMultiplication):
    args_list = []
    @staticmethod
    def args_to_string():
        return ""

    def construct(self):
        for num in [2, 0.5, -3]:
            self.clear()            
            ShowMultiplication.construct(self, num, False)



class ExamplesOfNonlinearOneDimensionalTransforms(NumberLineScene):
    def construct(self):
        def sinx_plux_x(x_y_z):
            (x, y, z) = x_y_z
            return (np.sin(x) + 1.2*x, y, z)

        def shift_zero(x_y_z):
            (x, y, z) = x_y_z
            return (2*x+4, y, z)

        self.nonlinear = TextMobject("Not a Linear Transform")
        self.nonlinear.set_color(LIGHT_RED).to_edge(UP, buff = 1.5)
        pairs = [
            (sinx_plux_x, "numbers don't remain evenly spaced"),
            (shift_zero, "zero does not remain fixed")
        ]
        for func, explanation in pairs:
            self.run_function(func, explanation)
            self.wait(3)

    def run_function(self, function, explanation):
        self.clear()
        self.add(self.nonlinear)
        config = {
            "stroke_width" : 2*DEFAULT_STROKE_WIDTH,
            "density" : 5*DEFAULT_POINT_DENSITY_1D,
        }
        NumberLineScene.construct(self, **config)
        words = TextMobject(explanation).set_color(LIGHT_RED)
        words.next_to(self.nonlinear, DOWN, buff = 0.5)
        self.add(words)

        self.play(
            ApplyPointwiseFunction(function, self.number_line),
            *[
                ApplyMethod(
                    mob.shift,
                    function(mob.get_center()) - mob.get_center()
                )
                for mob in self.number_mobs
            ],
            run_time = 2.0
        )


class ShowTwoThenThree(ShowMultiplication):
    args_list = []
    @staticmethod
    def args_to_string():
        return ""

    def construct(self):
        config = {
            "stroke_width" : 2*DEFAULT_STROKE_WIDTH,
            "density" : 6*DEFAULT_POINT_DENSITY_1D,
        }
        NumberLineScene.construct(self, **config)
        self.copy_original_line()
        self.show_multiplication(2)
        self.wait()
        self.show_multiplication(3)
        self.wait()


########################################################

class TransformScene2D(Scene):
    def add_number_plane(self, density_factor = 1, use_faded_lines = True):
        config = {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "density" : DEFAULT_POINT_DENSITY_1D*density_factor,
            "stroke_width" : 2*DEFAULT_STROKE_WIDTH
        }
        if not use_faded_lines:
            config["x_faded_line_frequency"] = None
            config["y_faded_line_frequency"] = None
        self.number_plane = NumberPlane(**config)
        self.add(self.number_plane)

    def add_background(self):
        grey_plane = NumberPlane(color = "grey")
        num_mobs = grey_plane.get_coordinate_labels()
        self.paint_into_background(grey_plane, *num_mobs)

    def add_x_y_arrows(self):
        self.x_arrow = Arrow(
            ORIGIN, 
            self.number_plane.num_pair_to_point((1, 0)),
            color = "lightgreen",
            **ARROW_CONFIG
        )
        self.y_arrow = Arrow(
            ORIGIN,
            self.number_plane.num_pair_to_point((0, 1)),
            color = LIGHT_RED,
            **ARROW_CONFIG
        )
        self.add(self.x_arrow, self.y_arrow)
        self.number_plane.filter_out(
            lambda x_y_z : (0 < x_y_z[0]) and (x_y_z[0] < 1) and (abs(x_y_z[1]) < 0.1)
        )
        self.number_plane.filter_out(
            lambda x_y_z1 : (0 < x_y_z1[1]) and (x_y_z1[1] < 1) and (abs(x_y_z1[0]) < 0.1)
        )
        return self


class ShowMatrixTransform(TransformScene2D):
    args_list = [
        ([[1, 3], [-2, 0]], False, False),
        ([[1, 3], [-2, 0]], True, False),
        ([[1, 0.5], [0.5, 1]], True, False),
        ([[2, 0], [0, 2]], True, False),
        ([[0.5, 0], [0, 0.5]], True, False),
        ([[-1, 0], [0, -1]], True, False),
        ([[0, 1], [1, 0]], True, False),
        ([[-2, 0], [-1, -1]], True, False),
        ([[0, -1], [1, 0]], True, False),
    ]
    @staticmethod
    def args_to_string(matrix, with_background, show_matrix):
        background_string = "WithBackground" if with_background else "WithoutBackground"
        show_string = "ShowingMatrix" if show_matrix else ""
        return matrix_to_string(matrix) + background_string + show_string

    def construct(self, matrix, with_background, show_matrix):
        matrix = np.array(matrix)
        number_plane_config = {
            "density_factor" : self.get_density_factor(matrix)
        }
        if with_background:
            self.add_background()
            number_plane_config["use_faded_lines"] = False
            self.add_number_plane(**number_plane_config)
            self.add_x_y_arrows()
        else:
            self.add_number_plane(**number_plane_config)
        if show_matrix:
            self.add(matrix_mobject(matrix).to_corner(UP+LEFT))
        def func(mobject):
            mobject.points[:, :2] = np.dot(mobject.points[:, :2], np.transpose(matrix))
            return mobject

        self.wait()
        kwargs = {
            "run_time" : 2.0,
            "path_func" : self.get_path_func(matrix)
        }
        anims = [ApplyFunction(func, self.number_plane, **kwargs)]
        if hasattr(self, "x_arrow") and hasattr(self, "y_arrow"):
            for arrow, index in (self.x_arrow, 0), (self.y_arrow, 1):
                new_arrow = Arrow(
                    ORIGIN,
                    self.number_plane.num_pair_to_point(matrix[:,index]),
                    color = arrow.get_color(),
                    **ARROW_CONFIG
                )
                arrow.remove_tip()
                new_arrow.remove_tip()
                Mobject.align_data(arrow, new_arrow)
                arrow.add_tip()
                new_arrow.add_tip()
                anims.append(Transform(arrow, new_arrow, **kwargs))
        self.play(*anims)
        self.wait()

    def get_density_factor(self, matrix):
        max_norm = max([
            abs(get_norm(column))
            for column in np.transpose(matrix)
        ])
        return max(max_norm, 1)

    def get_path_func(self, matrix):
        rotational_components = np.array([
            np.log(multiplier*complex(*matrix[:,i])).imag
            for i, multiplier in [(0, 1), (1, complex(0, -1))]
        ])
        rotational_components[rotational_components == -np.pi] = np.pi
        return path_along_arc(np.mean(rotational_components))


class ExamplesOfTwoDimensionalLinearTransformations(ShowMatrixTransform):
    args_list = []
    @staticmethod
    def args_to_string():
        return ""

    def construct(self):
        matrices = [
            [[1, 0.5], 
             [0.5, 1]],
            [[0, -1],
             [2, 0]],
            [[1, 3],
             [-2, 0]],
        ]
        for matrix in matrices:
            self.clear()
            ShowMatrixTransform.construct(self, matrix, False, False)


class ExamplesOfNonlinearTwoDimensionalTransformations(Scene):
    def construct(self):
        Scene.construct(self)
        def squiggle(x_y_z):
            (x, y, z) = x_y_z
            return (x+np.sin(y), y+np.cos(x), z)

        def shift_zero(x_y_z):
            (x, y, z) = x_y_z
            return (2*x + 3*y + 4, -1*x+y+2, z)

        self.nonlinear = TextMobject("Nonlinear Transform")
        self.nonlinear.set_color(LIGHT_RED)
        self.nonlinear.to_edge(UP, buff = 1.5)
        pairs = [
            (squiggle, "lines do not remain straight"),
            (shift_zero, "the origin does not remain fixed")
        ]
        self.get_blackness()
        for function, explanation in pairs:
            self.apply_function(function, explanation)


    def apply_function(self, function, explanation):
        self.clear()
        config = {
            "x_radius" : FRAME_WIDTH,
            "y_radius" : FRAME_WIDTH,
            "density" : 3*DEFAULT_POINT_DENSITY_1D,
            "stroke_width" : 2*DEFAULT_STROKE_WIDTH
        }
        number_plane = NumberPlane(**config)
        numbers = number_plane.get_coordinate_labels()
        words = TextMobject(explanation)
        words.set_color(LIGHT_RED)
        words.next_to(self.nonlinear, DOWN, buff = 0.5)

        self.add(number_plane, *numbers)
        self.add(self.blackness, self.nonlinear, words)
        self.wait()
        self.play(
            ApplyPointwiseFunction(function, number_plane),
            *[
                ApplyMethod(
                    mob.shift,
                    function(mob.get_center())-mob.get_center()
                )
                for mob in numbers
            ] + [
                Animation(self.blackness),
                Animation(words),
                Animation(self.nonlinear)
            ],
            run_time = 2.0
        )
        self.wait(3)

    def get_blackness(self):
        vertices = [
            3.5*LEFT+1.05*UP,
            3.5*RIGHT+1.05*UP,
            3.5*RIGHT+2.75*UP,
            3.5*LEFT+2.75*UP,
        ]

        region = region_from_polygon_vertices(*vertices)
        image = disp.paint_region(region, color = WHITE)
        self.blackness = TextMobject("")
        ImageMobject.generate_points_from_image_array(self.blackness, image)
        self.blackness.set_color(BLACK)
        rectangle = Rectangle(width = 7, height=1.7)
        rectangle.set_color(WHITE)
        rectangle.shift(self.blackness.get_center())
        self.blackness.add(rectangle)
        self.blackness.scale_in_place(0.95)


class TrickyExamplesOfNonlinearTwoDimensionalTransformations(Scene):
    def construct(self):
        config = {
            "x_radius" : 0.6*FRAME_WIDTH,
            "y_radius" : 0.6*FRAME_WIDTH,
            "density" : 10*DEFAULT_POINT_DENSITY_1D,
            "stroke_width" : 2*DEFAULT_STROKE_WIDTH
        }
        number_plane = NumberPlane(**config)
        phrase1, phrase2 = TextMobject([
            "These might look like they keep lines straight...",
            "but diagonal lines get curved"
        ]).to_edge(UP, buff = 1.5).split()
        phrase2.set_color(LIGHT_RED)
        diagonal = Line(
            DOWN*FRAME_Y_RADIUS+LEFT*FRAME_X_RADIUS,
            UP*FRAME_Y_RADIUS+RIGHT*FRAME_X_RADIUS,
            density = 10*DEFAULT_POINT_DENSITY_1D
        )

        def sunrise(x_y_z):
            (x, y, z) = x_y_z
            return ((FRAME_Y_RADIUS+y)*x, y, z)

        def squished(x_y_z):
            (x, y, z) = x_y_z
            return (x + np.sin(x), y+np.sin(y), z)

        self.get_blackness()

        self.run_function(sunrise, number_plane, phrase1)
        self.run_function(squished, number_plane, phrase1)
        phrase1.add(phrase2)
        self.add(phrase1)
        self.play(ShowCreation(diagonal))
        self.remove(diagonal)
        number_plane.add(diagonal)
        self.run_function(sunrise, number_plane, phrase1)
        self.run_function(squished, number_plane, phrase1, False)


    def run_function(self, function, plane, phrase, remove_plane = True):
        number_plane = deepcopy(plane)
        self.add(number_plane, self.blackness, phrase)
        self.wait()
        self.play(
            ApplyPointwiseFunction(function, number_plane, run_time = 2.0),
            Animation(self.blackness),            
            Animation(phrase),
        )
        self.wait(3)
        if remove_plane:
            self.remove(number_plane)

    def get_blackness(self):
        vertices = [
            4.5*LEFT+1.25*UP,
            4.5*RIGHT+1.25*UP,
            4.5*RIGHT+2.75*UP,
            4.5*LEFT+2.75*UP,
        ]

        region = region_from_polygon_vertices(*vertices)
        image = disp.paint_region(region, color = WHITE)
        self.blackness = TextMobject("")
        ImageMobject.generate_points_from_image_array(self.blackness, image)
        self.blackness.set_color(BLACK)
        rectangle = Rectangle(width = 9, height=1.5)
        rectangle.set_color(WHITE)
        rectangle.shift(self.blackness.get_center())
        self.blackness.add(rectangle)
        self.blackness.scale_in_place(0.95)


############# HORRIBLE! ##########################
class ShowMatrixTransformWithDot(TransformScene2D):
    args_list = [
        ([[1, 3], [-2, 0]], True, False),
    ]
    @staticmethod
    def args_to_string(matrix, with_background, show_matrix):
        background_string = "WithBackground" if with_background else "WithoutBackground"
        show_string = "ShowingMatrix" if show_matrix else ""
        return matrix_to_string(matrix) + background_string + show_string

    def construct(self, matrix, with_background, show_matrix):
        matrix = np.array(matrix)
        number_plane_config = {
            "density_factor" : self.get_density_factor(matrix),
        }
        if with_background:
            self.add_background()
            number_plane_config["use_faded_lines"] = False
            self.add_number_plane(**number_plane_config)
            self.add_x_y_arrows()
        else:
            self.add_number_plane(**number_plane_config)
        if show_matrix:
            self.add(matrix_mobject(matrix).to_corner(UP+LEFT))
        def func(mobject):
            mobject.points[:, :2] = np.dot(mobject.points[:, :2], np.transpose(matrix))
            return mobject
        dot = Dot((-1, 2, 0), color = "yellow")
        self.add(dot)
        x_arrow_copy = deepcopy(self.x_arrow)
        y_arrow_copy = Arrow(LEFT, LEFT+2*UP, color = LIGHT_RED, **ARROW_CONFIG)

        self.play(ApplyMethod(x_arrow_copy.rotate, np.pi))
        self.play(ShowCreation(y_arrow_copy))
        self.wait()
        self.remove(x_arrow_copy, y_arrow_copy)
        kwargs = {
            "run_time" : 2.0,
            "path_func" : self.get_path_func(matrix)
        }
        anims = [
            ApplyFunction(func, self.number_plane, **kwargs),
            ApplyMethod(dot.shift, func(deepcopy(dot)).get_center()-dot.get_center(), **kwargs),
        ]
        if hasattr(self, "x_arrow") and hasattr(self, "y_arrow"):
            for arrow, index in (self.x_arrow, 0), (self.y_arrow, 1):
                new_arrow = Arrow(
                    ORIGIN,
                    self.number_plane.num_pair_to_point(matrix[:,index]),
                    color = arrow.get_color(),
                    **ARROW_CONFIG
                )
                arrow.remove_tip()
                new_arrow.remove_tip()
                Mobject.align_data(arrow, new_arrow)
                arrow.add_tip()
                new_arrow.add_tip()
                anims.append(Transform(arrow, new_arrow, **kwargs))
        self.play(*anims)
        self.wait()

        x_arrow_copy = deepcopy(self.x_arrow)
        y_arrow_copy = Arrow(LEFT+2*UP, 5*RIGHT+2*UP, color = LIGHT_RED, **ARROW_CONFIG)
        self.play(ApplyMethod(x_arrow_copy.rotate, np.pi))
        self.play(ShowCreation(y_arrow_copy))
        self.wait(3)
        self.remove(x_arrow_copy, y_arrow_copy)        

    def get_density_factor(self, matrix):
        max_norm = max([
            abs(get_norm(column))
            for column in np.transpose(matrix)
        ])
        return max(max_norm, 1)

    def get_path_func(self, matrix):
        rotational_components = [
            sign*np.arccos(matrix[i,i]/get_norm(matrix[:,i]))
            for i in [0, 1]
            for sign in [((-1)**i)*np.sign(matrix[1-i, i])]
        ]
        average_rotation = sum(rotational_components)/2
        if abs(average_rotation) < np.pi / 2:
            return straight_path
        elif average_rotation > 0:
            return counterclockwise_path()
        else:
            return clockwise_path()


class Show90DegreeRotation(TransformScene2D):
    def construct(self):
        self.add_number_plane()
        self.add_background()
        self.add_x_y_arrows()

        self.wait()
        self.play(*[
            RotationAsTransform(mob, run_time = 2.0)
            for mob in (self.number_plane, self.x_arrow, self.y_arrow)
        ])
        self.wait()

