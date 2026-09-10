"""Adapted from example_scenes.py's SurfaceExample, dropping the networked textures
so this renders with no external downloads."""
from manimlib import *


class SphereExample(ThreeDScene):
    def construct(self):
        sphere = Sphere(radius=2)
        sphere.set_color(BLUE_D)
        sphere.set_opacity(0.8)
        mesh = SurfaceMesh(sphere)
        mesh.set_stroke(WHITE, 1, opacity=0.5)

        self.play(
            FadeIn(sphere),
            ShowCreation(mesh, lag_ratio=0.01, run_time=2),
        )
        # self.frame is the camera frame; ThreeDScene lets you orbit it
        # with increment_phi/increment_theta.
        self.play(
            self.frame.animate.increment_phi(-20 * DEG),
            self.frame.animate.increment_theta(-30 * DEG),
            run_time=2,
        )
        self.wait()
