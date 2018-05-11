from __future__ import absolute_import

from scene.scene import Scene
from camera.moving_camera import MovingCamera
from camera.multi_camera import MultiCamera
from mobject.types.image_mobject import ImageMobjectFromCamera

from constants import *


# Note, any scenes from old videos using ZoomedScene will almost certainly
# break, as it was restructured.

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
        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display

        self.zoom_activated = True
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
            # If either of the zoomed_mobjects are moving, then so is
            # everything
            return self.mobjects
        return moving_mobjects
