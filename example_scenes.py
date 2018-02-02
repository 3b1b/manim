#!/usr/bin/env python

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.combinatorics import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from mobject.vectorized_mobject import *

from topics.three_dimensions import *

# To watch one of these scenes, run the following:
# python extract_scene.py file_name <SceneName> -p
# 
# Use the flat -l for a faster rendering at a lower 
# quality, use -s to skip to the end and just show
# the final frame, and use -n <number> to skip ahead
# to the n'th animation of a scene.


class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        # circle.flip(RIGHT)
        # circle.rotate(3*TAU/8)
        square = Square()

        self.play(ShowCreation(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))

class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(ApplyPointwiseFunction(
            lambda (x, y, z) : complex_to_R3(np.exp(complex(x, y))),
            square
        ))
        self.wait()


class WriteStuff(Scene):
    def construct(self):
        self.play(Write(TextMobject("Stuff").scale(3)))


class Rotation3d(ThreeDScene):
    def construct(self):
        # STEP 1
        # Build two cube in the 3D scene, one for around the origin,
        # the other shifted along the vector RIGHT + UP + OUT
        cube_origin = Cube(fill_opacity = 0.8, stroke_width = 1.,
                           side_length = 1., fill_color = WHITE)

        # RIGHT side: Red
        # UP    side: Green
        # OUT   side: Blue
        orientations = [IN, OUT, LEFT, RIGHT, UP, DOWN]
        for face, orient in zip(cube_origin.family_members_with_points(), orientations):
            if np.array_equal(orient, RIGHT):
                face.set_style_data(fill_color = RED)
            elif np.array_equal(orient, UP):
                face.set_style_data(fill_color = GREEN)
            elif np.array_equal(orient, OUT):
                face.set_style_data(fill_color = BLUE)

        cube_shifted = Cube(fill_opacity = 0.8, stroke_width = 1.,
                            side_length = 1., fill_color = BLUE)
        shift_vec = 2*(RIGHT + UP + OUT)
        cube_shifted.shift(shift_vec)

        # STEP 2
        # Add the cubes in the 3D scene
        self.add(cube_origin)
        self.add(cube_shifted)

        # STEP 3
        # Setup the camera position
        phi, theta, distance = ThreeDCamera().get_spherical_coords()
        angle_factor = 0.9
        phi      += 2*np.pi/4*angle_factor
        theta    += 3*2*np.pi/8
        self.set_camera_position(phi, theta, distance)
        self.wait()

        # STEP 4
        # Animation
        # Animation 1: rotation around the Z-axis with the ORIGIN of the space
        #              as center of rotation
        theta += 2*np.pi
        self.move_camera(phi, theta, distance,
                         run_time = 5)

        # Animation 2: shift the space in order of to get the center of the shifted cube
        #              as the next center of rotation
        cube_center = cube_shifted.get_center()
        self.move_camera(center_x = cube_center[0],
                         center_y = cube_center[1],
                         center_z = cube_center[2],
                         run_time = 2)

        # Animation 3: rotation around the Z-axis with the center of the shifted cube 
        #              as center of rotation
        theta += 2*np.pi
        self.move_camera(phi, theta, distance,
                         run_time = 5)











