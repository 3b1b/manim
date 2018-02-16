#!/usr/bin/env python

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from scene import Scene
from camera import Camera

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *

from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.combinatorics import *
from topics.three_dimensions import *

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
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3*TAU/8)

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


class SpinAroundCube(ThreeDScene):
    # Take a look at ThreeDSCene in three_dimensions.py.
    # This has a few methods on it like set_camera_position
    # and move_camera that will be useful.  The main thing to
    # know about these is that the camera position is thought
    # of as having spherical coordinates, phi and theta.

    # In general, the nature of how this 3d camera works
    # is not always robust, you might discover little
    # quirks here or there
    def construct(self):
        axes = ThreeDAxes()
        cube = Cube(
            fill_opacity = 1,
            stroke_color = LIGHT_GREY,
            stroke_width = 1,
        )
        # The constant OUT is np.array([0, 0, 1])
        cube.next_to(ORIGIN, UP+RIGHT+OUT)
        self.add(axes, cube)

        # The camera starts positioned with phi=0, meaning it
        # is directly above the xy-plane, and theta = -TAU/4, 
        # which makes the "down" direction of the screen point
        # in the negative y direction.

        # This animates a camera movement
        self.move_camera(
            # Tilted 20 degrees off xy plane (70 degrees off the vertical)
            phi = (70./360.)*TAU,
            # Positioned above the third quadrant of
            # the xy-plane
            theta = (-110./360.)*TAU, 
            # pass in animation config just like a .play call
            run_time = 3
        )
        self.wait()
        # If you want the camera to slowly rotate about
        # the z-axis
        self.begin_ambient_camera_rotation()
        self.wait(4)
        self.play(FadeOut(cube))



        text = TextMobject("Your ad here")
        text.rotate(TAU/4, axis = RIGHT)
        text.next_to(cube, OUT)
        self.play(Write(text))
        # If you want to play animations while moving the camera,
        # include them in an "added_anims" list to move_camera
        self.move_camera(
            theta = -0.2*TAU,
            added_anims = [
                text.shift, 3*OUT, 
                text.set_fill, {"opacity" : 1},
            ]
        )
        self.wait(4)














