from __future__ import absolute_import

from scene.scene import Scene
from camera.moving_camera import MovingCamera


class MovingCameraScene(Scene):
    CONFIG = {
        "camera_class": MovingCamera
    }

    def setup(self):
        Scene.setup(self)
        assert(isinstance(self.camera, MovingCamera))
        self.camera_frame = self.camera.frame
        # Hmm, this currently relies on the fact that MovingCamera
        # willd default to a full-sized frame.  Is that okay?
        return self

    def get_moving_mobjects(self, *animations):
        # TODO: Code repetition from ZoomedScene
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        if self.camera_frame in moving_mobjects:
            # When the camera is moving, so is everything,
            return self.mobjects
        else:
            return moving_mobjects
