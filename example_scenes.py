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














