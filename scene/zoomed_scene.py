from __future__ import absolute_import

import numpy as np

from scene.scene import Scene
from animation.creation import FadeIn
from camera.moving_camera import MovingCamera
from camera.multi_camera import MultiCamera
from mobject.geometry import Rectangle
from mobject.types.image_mobject import ImageMobjectFromCamera

from constants import *


class ZoomedScene(Scene):
    CONFIG = {
        "camera_class": MultiCamera,
        "zoomed_display_height": 3,
        "zoomed_display_width": 3,
        "zoomed_display_center": None,
        "zoomed_display_corner": UP + RIGHT,
        "zoomed_display_corner_buff": DEFAULT_MOBJECT_TO_EDGE_BUFFER,
        "zoomed_camera_config": {
            "default_frame_stroke_width": 2,
        },
        "zoomed_camera_image_mobject_config": {},
        "zoomed_camera_frame_starting_position": ORIGIN,
        "zoom_factor": 0.15,
        "image_frame_stroke_width": 3,
        "zoom_activated": False,
    }

    def setup(self):
        # Initialize camera and display
        zoomed_camera = MovingCamera(**self.zoomed_camera_config)
        zoomed_display = ImageMobjectFromCamera(
            zoomed_camera, **self.zoomed_camera_image_mobject_config
        )
        zoomed_display.add_display_frame()
        for mob in zoomed_camera.frame, zoomed_display:
            mob.stretch_to_fit_height(self.zoomed_display_height)
            mob.stretch_to_fit_width(self.zoomed_display_width)
        zoomed_camera.frame.scale(self.zoom_factor)

        # Position camera and display
        zoomed_camera.frame.move_to(self.zoomed_camera_frame_starting_position)
        if self.zoomed_display_center is not None:
            zoomed_display.move_to(self.zoomed_display_center)
        else:
            zoomed_display.to_corner(
                self.zoomed_display_corner,
                buff=self.zoomed_display_corner_buff
            )

        self.zoomed_camera = zoomed_camera
        self.zoomed_display = zoomed_display

    def activate_zooming(self, animate=False, run_times=[2, 1]):
        self.zoom_activated = True
        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        self.camera.add_image_mobject_from_camera(zoomed_display)

        to_add = [zoomed_camera.frame, zoomed_display]
        if animate:
            zoomed_display.save_state(use_deepcopy=True)
            zoomed_display.replace(zoomed_camera.frame)

            full_frame_height, full_frame_width = self.camera.frame_shape
            zoomed_camera.frame.save_state()
            zoomed_camera.frame.stretch_to_fit_width(full_frame_width)
            zoomed_camera.frame.stretch_to_fit_height(full_frame_height)
            zoomed_camera.frame.center()
            zoomed_camera.frame.set_stroke(width=0)

            for mover, run_time in zip(to_add, run_times):
                self.add_foreground_mobject(mover)
                self.play(mover.restore, run_time=run_time)
        else:
            self.add_foreground_mobjects(*to_add)

    def get_moving_mobjects(self, *animations):
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        zoomed_mobjects = [self.zoomed_camera.frame, self.zoomed_display]
        moving_zoomed_mobjects = set(moving_mobjects).intersection(zoomed_mobjects)
        if self.zoom_activated and moving_zoomed_mobjects:
            return self.mobjects
        else:
            return moving_mobjects



class OldZoomedScene(Scene):
    """
    Move around self.little_rectangle to determine
    which part of the screen is zoomed in on.
    """
    CONFIG = {
        "zoomed_canvas_frame_shape": (3, 3),
        "zoomed_canvas_center": None,
        "zoomed_canvas_corner": UP + RIGHT,
        "zoomed_canvas_corner_buff": DEFAULT_MOBJECT_TO_EDGE_BUFFER,
        "zoomed_camera_background": None,
        "little_rectangle_start_position": ORIGIN,
        "zoom_factor": 6,
        "square_color": WHITE,
        "zoom_activated": False,
    }

    def activate_zooming(self):
        self.generate_big_rectangle()
        self.setup_zoomed_canvas()
        self.setup_zoomed_camera()
        self.zoom_activated = True

    def animate_activate_zooming(self):
        self.activate_zooming()
        self.play(*map(FadeIn, [
            self.little_rectangle, self.big_rectangle
        ]))

    def disactivate_zooming(self):
        self.remove(self.big_rectangle, self.little_rectangle)
        self.zoom_activated = False

    def get_zoomed_camera_mobject(self):
        return self.little_rectangle

    def get_zoomed_screen(self):
        return self.big_rectangle

    def generate_big_rectangle(self):
        height, width = self.zoomed_canvas_frame_shape
        self.big_rectangle = Rectangle(
            height=height,
            width=width,
            color=self.square_color
        )
        if self.zoomed_canvas_center is not None:
            self.big_rectangle.shift(self.zoomed_canvas_center)
        elif self.zoomed_canvas_corner is not None:
            self.big_rectangle.to_corner(
                self.zoomed_canvas_corner,
                buff=self.zoomed_canvas_corner_buff
            )
        self.add(self.big_rectangle)

    def setup_zoomed_canvas(self):
        upper_left = self.big_rectangle.get_corner(UP + LEFT)
        lower_right = self.big_rectangle.get_corner(DOWN + RIGHT)
        pixel_coords = self.camera.points_to_pixel_coords(
            np.array([upper_left, lower_right])
        )
        self.zoomed_canvas_pixel_indices = pixel_coords
        (up, left), (down, right) = pixel_coords
        self.zoomed_canvas_pixel_shape = (
            right - left,
            down - up,
        )

    def setup_zoomed_camera(self):
        self.little_rectangle = self.big_rectangle.copy()
        self.little_rectangle.scale(1. / self.zoom_factor)
        self.little_rectangle.move_to(
            self.little_rectangle_start_position
        )
        self.zoomed_camera = MovingCamera(
            self.little_rectangle,
            pixel_shape=self.zoomed_canvas_pixel_shape,
            background=self.zoomed_camera_background
        )
        self.add(self.little_rectangle)
        # TODO, is there a better way to hanld this?
        self.zoomed_camera.adjusted_thickness = lambda x: x

    def get_frame(self):
        frame = Scene.get_frame(self)
        if self.zoom_activated:
            (up, left), (down, right) = self.zoomed_canvas_pixel_indices
            frame[left:right, up:down, :] = self.zoomed_camera.get_image()
        return frame

    def set_camera_pixel_array(self, pixel_array):
        self.camera.set_pixel_array(pixel_array)
        if self.zoom_activated:
            (up, left), (down, right) = self.zoomed_canvas_pixel_indices
            self.zoomed_camera.set_pixel_array(
                pixel_array[left:right, up:down])

    def set_camera_background(self, background):
        self.set_camera_pixel_array(self, background)
        # TODO, check this...

    def reset_camera(self):
        self.camera.reset()
        if self.zoom_activated:
            self.zoomed_camera.reset()

    def capture_mobjects_in_camera(self, mobjects, **kwargs):
        self.camera.capture_mobjects(mobjects, **kwargs)
        if self.zoom_activated:
            if self.big_rectangle in mobjects:
                mobjects = list(mobjects)
                mobjects.remove(self.big_rectangle)
            self.zoomed_camera.capture_mobjects(
                mobjects, **kwargs
            )

    def get_moving_mobjects(self, *animations):
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        if self.zoom_activated and self.little_rectangle in moving_mobjects:
            # When the camera is moving, so is everything,
            return self.mobjects
        else:
            return moving_mobjects
