from __future__ import absolute_import

from constants import FRAME_HEIGHT
from constants import WHITE

from camera.camera import Camera
from mobject.frame import ScreenRectangle
from utils.config_ops import digest_config


class MovingCamera(Camera):
    """
    Stays in line with the height, width and position of it's 'frame', which is a Rectangle
    """

    CONFIG = {
        "fixed_dimension": 0,  # width
        "default_frame_stroke_color": WHITE,
        "default_frame_stroke_width": 0,
    }

    def __init__(self, frame=None, **kwargs):
        """
        frame is a Mobject, (should almost certainly be a rectangle)
        determining which region of space the camera displys
        """
        digest_config(self, kwargs)
        if frame is None:
            frame = ScreenRectangle(height=FRAME_HEIGHT)
            frame.set_stroke(
                self.default_frame_stroke_color,
                self.default_frame_stroke_width,
            )
        self.frame = frame
        Camera.__init__(self, **kwargs)

    def capture_mobjects(self, mobjects, **kwargs):
        self.reset_space_center()
        self.realign_frame_shape()
        Camera.capture_mobjects(self, mobjects, **kwargs)

    def reset_space_center(self):
        self.space_center = self.frame.get_center()

    def realign_frame_shape(self):
        height, width = self.frame_shape
        if self.fixed_dimension == 0:
            self.frame_shape = (height, self.frame.get_width())
        else:
            self.frame_shape = (self.frame.get_height(), width)
        self.resize_frame_shape(fixed_dimension=self.fixed_dimension)

    def get_mobjects_indicating_movement(self):
        """
        Returns all mobjets whose movement implies that the camera
        should think of all other mobjects on the screen as moving
        """
        return [self.frame]
