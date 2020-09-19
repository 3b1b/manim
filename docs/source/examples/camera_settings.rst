Camera Settings
=================================

.. manim:: TestZoom1
    :quality: medium

    class TestZoom1(ZoomedScene):
        CONFIG = {
            "zoomed_camera_frame_starting_position": [0, 0, 0],
            "zoomed_display_corner": [0, 0, 0],
            "zoomed_display_height": config['frame_height'],
            "zoomed_display_width": config['frame_width'],
            "zoom_factor": 0.1,
        }
        def construct(self):
            self.activate_zooming(animate=True)
            d = Dot()
            self.add(d)
