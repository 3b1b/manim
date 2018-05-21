from __future__ import absolute_import

from constants import *

from scene.scene import Scene
from camera.moving_camera import MovingCamera
from mobject.frame import ScreenRectangle


class MovingCameraScene(Scene):
    def setup(self):
        self.camera_frame = ScreenRectangle(height=FRAME_HEIGHT)
        self.camera_frame.set_stroke(width=0)
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
