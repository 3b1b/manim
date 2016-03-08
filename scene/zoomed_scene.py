import numpy as np

from scene import Scene
from mobject import Mobject
from topics.geometry import Rectangle
from camera import MovingCamera, Camera

from helpers import *

class ZoomedScene(Scene):
    CONFIG = {
        "zoomed_canvas_space_shape" : (3, 3),
        "zoomed_canvas_center"      : None,
        "zoomed_canvas_corner"      : UP+RIGHT,
        "zoomed_camera_background"  : None,
        "zoom_factor"               : 6,
        "square_color"              : WHITE,
        "zoom_activated"            : False,
    }
    def activate_zooming(self):
        self.generate_big_rectangle()
        self.setup_zoomed_canvas()
        self.setup_zoomed_camera()
        self.zoom_activated = True

    def disactivate_zooming(self):
        self.remove(self.big_rectangle, self.little_rectangle)
        self.zoom_activated = False

    def get_zoomed_camera_mobject(self):
        return self.little_rectangle

    def get_zoomed_screen(self):
        return self.big_rectangle

    def generate_big_rectangle(self):
        height, width = self.zoomed_canvas_space_shape
        self.big_rectangle = Rectangle(
            height = height,
            width = width,
            color = self.square_color
        )
        if self.zoomed_canvas_center is not None:
            self.big_rectangle.shift(self.zoomed_canvas_center)
        elif self.zoomed_canvas_corner is not None:
            self.big_rectangle.to_corner(self.zoomed_canvas_corner)
        self.add(self.big_rectangle)


    def setup_zoomed_canvas(self):
        upper_left = self.big_rectangle.get_corner(UP+LEFT)
        lower_right = self.big_rectangle.get_corner(DOWN+RIGHT)
        pixel_coords = self.camera.points_to_pixel_coords(
            np.array([upper_left, lower_right])
        )
        self.zoomed_canvas_pixel_indices = pixel_coords
        (up, left), (down, right) = pixel_coords
        self.zoomed_canvas_pixel_shape = (
            down-up,
            right-left
        )

    def setup_zoomed_camera(self):
        self.little_rectangle = self.big_rectangle.copy()
        self.little_rectangle.scale(1./self.zoom_factor)
        self.little_rectangle.center()
        self.zoomed_camera = MovingCamera(
            self.little_rectangle,
            pixel_shape = self.zoomed_canvas_pixel_shape,
            background = self.zoomed_camera_background
        )
        self.add(self.little_rectangle)
        #TODO, is there a better way to hanld this?
        self.zoomed_camera.adjusted_thickness = lambda x : x

    def get_frame(self):
        frame = Scene.get_frame(self)
        if self.zoom_activated:
            (up, left), (down, right) = self.zoomed_canvas_pixel_indices
            frame[left:right, up:down, :] = self.zoomed_camera.get_image()
        return frame

    def update_frame(self, *args, **kwargs):
        Scene.update_frame(self, *args, **kwargs)        
        if self.zoom_activated:
            self.zoomed_camera.reset()
            self.zoomed_camera.capture_mobjects(self.mobjects)






