from manimlib.camera.camera import Camera
from manimlib.constants import FRAME_HEIGHT
from manimlib.constants import FRAME_WIDTH
from manimlib.constants import ORIGIN
from manimlib.constants import WHITE
from manimlib.mobject.frame import ScreenRectangle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.config_ops import digest_config


# TODO, think about how to incorporate perspective
class CameraFrame(VGroup):
    CONFIG = {
        "width": FRAME_WIDTH,
        "height": FRAME_HEIGHT,
        "center": ORIGIN,
    }

    def __init__(self, **kwargs):
        pass


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

    # TODO, make these work for a rotated frame
    def get_frame_height(self):
        return self.frame.get_height()

    def get_frame_width(self):
        return self.frame.get_width()

    def get_frame_center(self):
        return self.frame.get_center()

    def set_frame_height(self, frame_height):
        self.frame.stretch_to_fit_height(frame_height)

    def set_frame_width(self, frame_width):
        self.frame.stretch_to_fit_width(frame_width)

    def set_frame_center(self, frame_center):
        self.frame.move_to(frame_center)

    def capture_mobjects(self, mobjects, **kwargs):
        # self.reset_frame_center()
        # self.realign_frame_shape()
        Camera.capture_mobjects(self, mobjects, **kwargs)

    # Since the frame can be moving around, the cairo
    # context used for updating should be regenerated
    # at each frame.  So no caching.
    def get_cached_cairo_context(self, pixel_array):
        return None

    def cache_cairo_context(self, pixel_array, ctx):
        pass

    # def reset_frame_center(self):
    #     self.frame_center = self.frame.get_center()

    # def realign_frame_shape(self):
    #     height, width = self.frame_shape
    #     if self.fixed_dimension == 0:
    #         self.frame_shape = (height, self.frame.get_width())
    #     else:
    #         self.frame_shape = (self.frame.get_height(), width)
    #     self.resize_frame_shape(fixed_dimension=self.fixed_dimension)

    def get_mobjects_indicating_movement(self):
        """
        Returns all mobjets whose movement implies that the camera
        should think of all other mobjects on the screen as moving
        """
        return [self.frame]
