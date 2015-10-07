#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene, NumberLineScene
from script_wrapper import command_line_create_scene

MOVIE_PREFIX = "matrix_as_transform_2d/"

def matrix_to_string(matrix):
    return "--".join(["-".join(map(str, row)) for row in matrix])

def matrix_mobject(matrix):
    return text_mobject(
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
        (2, False),
        (0.5, False),
        (-3, False),
        (-3, True),
        (2, True),
    ]
    @staticmethod
    def args_to_string(num, show_original_line):
        end_string = "WithCopiedOriginalLine" if show_original_line else ""
        return str(num) + end_string

    def construct(self, num, show_original_line):
        NumberLineScene.construct(self, density = abs(num)*DEFAULT_POINT_DENSITY_1D)
        if show_original_line:
            self.copy_original_line()
        kwargs = {
            "run_time" : 2.0,
            "interpolation_function" : straight_path if num > 0 else counterclockwise_path
        }
        self.dither()
        new_number_line = deepcopy(self.number_line)
        new_number_line.stretch(num, 0)
        self.play(
            Transform(self.number_line, new_number_line, **kwargs),
            *[
                ApplyFunction(
                    lambda m : m.do_in_place(m.stretch, 1.0/num, 0).stretch(num, 0),
                    mobject,
                    **kwargs
                )
                for mobject in self.number_mobs
            ]
        )
        self.dither()


    def copy_original_line(self):
        copied_line = deepcopy(self.number_line)
        copied_num_mobs = deepcopy(self.number_mobs)
        self.play(
            ApplyFunction(
                lambda m : m.shift(DOWN).highlight("green"), 
                copied_line
            ), *[
                ApplyMethod(mob.shift, DOWN)
                for mob in copied_num_mobs
            ]
        )
        self.dither()






########################################################

class TransformScene2D(Scene):
    def add_number_plane(self, density_factor, use_faded_lines = True):
        config = {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_HEIGHT,
            "density" : DEFAULT_POINT_DENSITY_1D*density_factor
        }
        if not use_faded_lines:
            config["x_faded_line_frequency"] = None
            config["y_faded_line_frequency"] = None
        self.number_plane = NumberPlane(**config)
        self.add(self.number_plane)

    def add_background(self):
        self.paint_into_background(
            NumberPlane(color = "grey").add_coordinates()
        )

    def add_x_y_arrows(self):
        self.x_arrow = Arrow(
            ORIGIN, 
            self.number_plane.num_pair_to_point((1, 0)),
            color = "green"
        )
        self.y_arrow = Arrow(
            ORIGIN,
            self.number_plane.num_pair_to_point((0, 1)),
            color = "red"
        )
        self.add(self.x_arrow, self.y_arrow)
        self.number_plane.filter_out(
            lambda (x, y, z) : (0 < x) and (x < 1) and (abs(y) < 0.1)
        )
        self.number_plane.filter_out(
            lambda (x, y, z) : (0 < y) and (y < 1) and (abs(x) < 0.1)
        )
        return self


class ShowMatrixTransform(TransformScene2D):
    args_list = [
        ([[1, 2], [3, 4]], True, False),
        ([[1, 3], [-2, 0]], False, False),
        ([[1, 3], [-2, 0]], True, True),
        ([[0, -1], [1, 0]], True, False),
        ([[0, -1], [1, 0]], False, False),
        ([[-1, 0], [0, -1]], True, False),
        ([[-1, 0], [0, -1]], False, False),
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

        self.dither()
        kwargs = {
            "run_time" : 2.0,
            "interpolation_function" : self.get_interpolation_function(matrix)
        }
        anims = [ApplyFunction(func, self.number_plane, **kwargs)]
        if hasattr(self, "x_arrow") and hasattr(self, "y_arrow"):
            for arrow, index in (self.x_arrow, 0), (self.y_arrow, 1):
                new_arrow = Arrow(
                    ORIGIN,
                    self.number_plane.num_pair_to_point(matrix[:,index]),
                    color = arrow.get_color()
                )
                arrow.remove_tip()
                new_arrow.remove_tip()
                Mobject.align_data(arrow, new_arrow)
                arrow.add_tip()
                new_arrow.add_tip()
                anims.append(Transform(arrow, new_arrow, **kwargs))
        self.play(*anims)
        self.dither()

    def get_density_factor(self, matrix):
        max_norm = max([
            abs(np.linalg.norm(column))
            for column in np.transpose(matrix)
        ])
        return max(max_norm, 1)

    def get_interpolation_function(self, matrix):
        rotational_components = [
            sign*np.arccos(matrix[i,i]/np.linalg.norm(matrix[:,i]))
            for i in [0, 1]
            for sign in [((-1)**i)*np.sign(matrix[1-i, i])]
        ]
        average_rotation = sum(rotational_components)/2
        if abs(average_rotation) < np.pi / 2:
            return straight_path
        elif average_rotation > 0:
            return counterclockwise_path
        else:
            return clockwise_path









if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)