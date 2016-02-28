import numpy as np

from scene import Scene
from mobject import Mobject
from camera import MovingCamera, Camera

from helpers import *

class ZoomedScene(Scene):
    CONFIG = {
        "zoomed_canvas_space_shape" : (3, 3),
        "zoomed_canvas_center" : None,
        "zoomed_canvas_corner" : UP+RIGHT,
        "zoomed_camera_background" : None
    }
    def init_zooming(self, moving_camera_mobject):
        self.setup_zoomed_canvas()
        self.zoomed_camera = MovingCamera(
            moving_camera_mobject,
            pixel_shape = self.zoomed_canvas_pixel_shape,
            background = self.zoomed_camera_background
        )
        self.add(moving_camera_mobject)

    def setup_zoomed_canvas(self):
        height, width = self.zoomed_canvas_space_shape
        canvas_corners = Mobject().add_points([
            ORIGIN, DOWN+RIGHT
        ])
        canvas_corners.stretch_to_fit_height(height)
        canvas_corners.stretch_to_fit_width(width)
        canvas_corners.center()        
        if self.zoomed_canvas_center is not None:
            canvas_corners.shift(self.zoomed_canvas_center)
        elif self.zoomed_canvas_corner is not None:
            canvas_corners.to_corner(self.zoomed_canvas_corner)

        pixel_coords = self.camera.points_to_pixel_coords(canvas_corners.points)
        upper_left, lower_right = pixel_coords
        self.zoomed_canvas_pixel_indices = pixel_coords
        self.zoomed_canvas_pixel_shape = (
            lower_right[0] - upper_left[0],
            lower_right[1] - upper_left[1]
        )

    def get_frame(self):
        frame = Scene.get_frame(self)
        (up, left), (down, right) = self.zoomed_canvas_pixel_indices
        frame[left:right, up:down, :] = self.zoomed_camera.get_image()
        return frame

    def update_frame(self, *args, **kwargs):
        Scene.update_frame(self, *args, **kwargs)        
        self.zoomed_camera.reset()
        self.zoomed_camera.capture_mobjects(self.mobjects)






