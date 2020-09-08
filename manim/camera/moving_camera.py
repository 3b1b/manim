__all__ = ["CameraFrame", "MovingCamera"]


from .. import config
from ..camera.camera import Camera
from ..constants import ORIGIN, WHITE
from ..mobject.frame import ScreenRectangle
from ..mobject.types.vectorized_mobject import VGroup
from ..utils.config_ops import digest_config


# TODO, think about how to incorporate perspective
class CameraFrame(VGroup):
    CONFIG = {
        "center": ORIGIN,
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.width = config["frame_width"]
        self.height = config["frame_height"]


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
            frame = ScreenRectangle(height=config["frame_height"])
            frame.set_stroke(
                self.default_frame_stroke_color,
                self.default_frame_stroke_width,
            )
        self.frame = frame
        Camera.__init__(self, **kwargs)

    # TODO, make these work for a rotated frame
    def get_frame_height(self):
        """Returns the height of the frame.

        Returns
        -------
        float
            The height of the frame.
        """
        return self.frame.get_height()

    def get_frame_width(self):
        """Returns the width of the frame

        Returns
        -------
        float
            The width of the frame.
        """
        return self.frame.get_width()

    def get_frame_center(self):
        """Returns the centerpoint of the frame in cartesian coordinates.

        Returns
        -------
        np.array
            The cartesian coordinates of the center of the frame.
        """
        return self.frame.get_center()

    def set_frame_height(self, frame_height):
        """Sets the height of the frame in MUnits.

        Parameters
        ----------
        frame_height : int, float
            The new frame_height.
        """
        self.frame.stretch_to_fit_height(frame_height)

    def set_frame_width(self, frame_width):
        """Sets the width of the frame in MUnits.

        Parameters
        ----------
        frame_width : int, float
            The new frame_width.
        """
        self.frame.stretch_to_fit_width(frame_width)

    def set_frame_center(self, frame_center):
        """Sets the centerpoint of the frame.

        Parameters
        ----------
        frame_center : np.array, list, tuple, Mobject
            The point to which the frame must be moved.
            If is of type mobject, the frame will be moved to
            the center of that mobject.
        """
        self.frame.move_to(frame_center)

    def capture_mobjects(self, mobjects, **kwargs):
        # self.reset_frame_center()
        # self.realign_frame_shape()
        Camera.capture_mobjects(self, mobjects, **kwargs)

    # Since the frame can be moving around, the cairo
    # context used for updating should be regenerated
    # at each frame.  So no caching.
    def get_cached_cairo_context(self, pixel_array):
        """
        Since the frame can be moving around, the cairo
        context used for updating should be regenerated
        at each frame.  So no caching.
        """
        return None

    def cache_cairo_context(self, pixel_array, ctx):
        """
        Since the frame can be moving around, the cairo
        context used for updating should be regenerated
        at each frame.  So no caching.
        """
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

        Returns
        -------
        list
        """
        return [self.frame]
