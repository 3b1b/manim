#!/usr/bin/env python

from helpers import *

from topics.number_line import *

from topics.three_dimensions import *

class Test(ThreeDScene):
    # Take a look at ThreeDSCene in three_dimensions.py.
    # This has a few methods on it like set_camera_position
    # and move_camera that will be useful.  The main thing to
    # know about these is that the camera position is thought
    # of as having spherical coordinates, phi and theta.

    # In general, the nature of how this 3d camera works
    # is not always robust, do you might discover little
    # quirks here or there.  As they come up, just keep 
    # note and let me know
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
        # print self.camera.get_phi()
        # print self.camera.get_theta()

        # This animates a camera movement
        self.move_camera(
            # Tilted 20 degrees of xy plane (70 degrees off the vertical)
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

        # One possibility for the spotlights is to 
        # create 4 of them that cover the sides of 
        # a square pyramid.
        # 
        # Then again, when I looked at this it seemed
        # sort of weird, so maybe just doing it with 
        # a single spotlight whose normal is facing the
        # camera would be better.  Either way, hopefully 
        # The rotations going on here are instructive 
        # for manipulating things in this 3d world.
        from active_projects.basel import Spotlight, SwitchOn
        spotlight = Spotlight(
            screen = Line(DOWN, UP).shift(3*RIGHT),
        )
        #Rotate it off the xy-plane
        spotlight.rotate(
            0.5*spotlight.opening_angle(),
            about_point = spotlight.source_point,
            axis = DOWN,
        )
        #Create four copies, positioned as needed
        three_d_spotlight_group = VGroup(*[
            spotlight.copy().rotate(
                i*TAU/4, 
                about_point = spotlight.source_point,
                axis = RIGHT,
            )
            for i in range(4)
        ])

        self.play(*[
            SwitchOn(spotlight, run_time = 3)
            for spotlight in three_d_spotlight_group
        ])
        self.wait(4)
        text = TextMobject("Light beam")
        text.rotate(TAU/4, axis = RIGHT)
        text.next_to(three_d_spotlight_group, OUT)
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

        # There is no need to know the following, but I'll 
        # say it anyway: 
        # Under the hood, the ThreeDCamera here, self.camera,
        # has an associated mobject "rotation_mobject", which
        # is simply a point in 3d space, but that 3d space
        # is thought of as being theta-phi-r space.  This is
        # just so that all the same animation infrastructure
        # that moves mobjects around can control the camera's
        # positioning, and having it live in theta-phi-r space
        # makes the interpolations behave better at places with 
        # singularities like phi = 0.
        # 
        # Ultimately, I don't think this is handled the best
        # way it can be, but for simple needs it seems to do
        # okay.