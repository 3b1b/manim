3D Scenes
=================================

.. manim:: Example3DNo1
    :quality: medium
    :save_last_frame:

    class Example3DNo1(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()

            sphere = ParametricSurface(
                lambda u, v: np.array([
                    1.5 * np.cos(u) * np.cos(v),
                    1.5 * np.cos(u) * np.sin(v),
                    1.5 * np.sin(u)
                ]), v_min=0, v_max=TAU, u_min=-PI / 2, u_max=PI / 2, checkerboard_colors=[RED_D, RED_E],
                resolution=(15, 32))

            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)

            self.add(axes, sphere)


