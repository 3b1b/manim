from manimlib.scene.scene import Scene


class ThreeDScene(Scene):
    CONFIG = {
        "camera_config": {
            "samples": 4,
        }
    }

    def begin_ambient_camera_rotation(self, rate=0.02):
        pass  # TODO

    def stop_ambient_camera_rotation(self):
        pass  # TODO

    def move_camera(self,
                    phi=None,
                    theta=None,
                    distance=None,
                    gamma=None,
                    frame_center=None,
                    **kwargs):
        pass  # TODO
