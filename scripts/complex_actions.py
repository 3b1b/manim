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

MOVIE_PREFIX = "complex_actions/"

class ComplexMultiplication(Scene):
    @staticmethod
    def args_to_string(multiplier):
        return filter(lambda c : c not in "()", str(multiplier))

    @staticmethod
    def string_to_args(num_string):
        return complex(num_string)

    def construct(self, multiplier):
        norm = np.linalg.norm(multiplier)
        arg  = np.log(multiplier).imag
        plane_config = {
            "faded_line_frequency" : 0
        }
        if norm > 1:
            plane_config["density"] = norm*DEFAULT_POINT_DENSITY_1D
        radius = SPACE_WIDTH
        if norm > 0 and norm < 1:
            radius /= norm
        plane_config["x_radius"] = plane_config["y_radius"] = radius
        plane = ComplexPlane(**plane_config)
        self.anim_config = {
            "run_time" : 2.0,
            "interpolation_function" : get_best_interpolation_function(arg)
        }

        background = ComplexPlane(color = "grey")            
        labels = background.get_coordinate_labels()
        self.paint_into_background(background, *labels)
        arrow, new_arrow = [
            plane.get_vector(plane.number_to_point(z), color = "skyblue")
            for z in [1, multiplier]
        ]
        self.add(arrow)
        self.additional_animations = [Transform(
            arrow, new_arrow, **self.anim_config
        )]

        self.mobjects_to_multiply = [plane]
        self.mobjects_to_move_without_molding = []
        self.multiplier = multiplier
        self.plane = plane
        if self.__class__ == ComplexMultiplication:
            self.apply_multiplication()

    def apply_multiplication(self):
        def func((x, y, z)):
            complex_num = self.multiplier*complex(x, y)
            return (complex_num.real, complex_num.imag, z)
        mobjects = self.mobjects_to_multiply+self.mobjects_to_move_without_molding
        mobjects += [anim.mobject for anim in self.additional_animations]
        self.add(*mobjects)
        full_multiplications = [
            ApplyMethod(mobject.apply_function, func, **self.anim_config)
            for mobject in self.mobjects_to_multiply
        ]
        movements_with_plane = [
            ApplyMethod(
                mobject.shift, 
                func(mobject.get_center())-mobject.get_center(),
                **self.anim_config            
            )
            for mobject in self.mobjects_to_move_without_molding
        ]
        self.dither()
        self.play(*reduce(op.add, [
            full_multiplications,
            movements_with_plane,
            self.additional_animations
        ]))
        self.dither()

class MultiplicationWithDot(ComplexMultiplication):
    @staticmethod
    def args_to_string(multiplier, dot_coords):
        start = ComplexMultiplication.args_to_string(multiplier)
        return start + "WithDotAt%d-%d"%dot_coords[:2]

    @staticmethod
    def string_to_args(arg_string):
        parts = arg_string.split()
        if len(parts) < 2 or len(parts) > 3:
            raise Exception("Invalid arguments")
        multiplier = complex(parts[0])
        tup_string = filter(lambda c : c not in "()", parts[1])
        nums = tuple(map(int, tup_string.split(",")))[:2]
        return multiplier, nums

    def construct(self, multiplier, dot_coords):
        ComplexMultiplication.construct(self, multiplier)
        self.mobjects_to_move_without_molding.append(
            Dot().shift(dot_coords)
        )
        self.apply_multiplication()


class ShowComplexPower(ComplexMultiplication):
    @staticmethod
    def args_to_string(multiplier, num_repeats):
        start = ComplexMultiplication.args_to_string(multiplier)
        return start + "ToThe%d"%num_repeats

    @staticmethod
    def string_to_args(arg_string):
        parts = arg_string.split()
        if len(parts) < 2 or len(parts) > 3:
            raise Exception("Invalid arguments")
        multiplier = complex(parts[0])
        num_repeats = int(parts[1])
        return multiplier, num_repeats

    def construct(self, multiplier, num_repeats):
        ComplexMultiplication.construct(self, multiplier)
        for x in range(num_repeats):
            arrow_transform = Transform(*[
                self.plane.get_vector(point, color = "skyblue")
                for z in [multiplier**(x), multiplier**(x+1)]
                for point in [self.plane.number_to_point(z)]
            ], **self.anim_config)
            self.remove(*[anim.mobject for anim in self.additional_animations])
            self.additional_animations = [arrow_transform]
            self.apply_multiplication()















if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)