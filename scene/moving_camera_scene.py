from helpers import *

from camera import MovingCamera
from scene import Scene
from topics.geometry import ScreenRectangle

class MovingCameraScene(Scene):
    def setup(self):
        self.camera_frame = ScreenRectangle(height = 2*SPACE_HEIGHT)
        self.camera_frame.set_stroke(width = 0)
        self.camera = MovingCamera(
            self.camera_frame, **self.camera_config
        )
        return self

    def get_moving_mobjects(self, *animations):
        # TODO: Code repetition from ZoomedScene
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        if self.camera_frame in moving_mobjects:
            # When the camera is moving, so is everything,
            return self.mobjects
        else:
            return moving_mobjects