#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene
from script_wrapper import command_line_create_scene

MOVIE_PREFIX = "matrix_as_transform_2d/"

def matrix_to_string(matrix):
    return "--".join(["-".join(map(str, row)) for row in matrix])








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
            lambda (x, y, z) : (0 < x) and (x < 1) and (y < 0.1)
        )
        self.number_plane.filter_out(
            lambda (x, y, z) : (0 < y) and (y < 1) and (x < 0.1)
        )
        return self


class ShowMatrixTransform(TransformScene2D):
    args_list = [
        ([[1, 2], [3, 4]], True),
        ([[1, 3], [-2, 0]], False),
        ([[1, 3], [-2, 0]], True),
        ([[0, -1], [1, 0]], True),
        ([[0, -1], [1, 0]], False),
    ]
    @staticmethod
    def args_to_string(matrix, with_background):
        background_string = "WithBackground" if with_background else "WithoutBackground"
        return matrix_to_string(matrix) + background_string

    def construct(self, matrix, with_background):
        matrix = np.array(matrix)
        number_plane_config = {
            "density_factor" : self.get_density_factor(matrix)
        }
        if with_background:
            self.add_background()
            number_plane_config["use_faded_lines"] = False
        self.add_number_plane(**number_plane_config)
        if with_background:
            self.add_x_y_arrows()
        def func(mobject):
            mobject.points[:, :2] = np.dot(mobject.points[:, :2], np.transpose(matrix))
            return mobject
        TransformScene2D.construct(self)
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
                anims.append(Transform(arrow, new_arrow))
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