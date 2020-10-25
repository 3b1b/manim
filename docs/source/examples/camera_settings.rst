Camera Settings
=================================

.. manim:: ChangingCameraWidth

    class ChangingCameraWidth(MovingCameraScene):
        def construct(self):
            text = Text("Hello World")
            self.add(text)
            self.play(self.camera_frame.set_width, text.get_width() * 1.2)
            self.wait()

.. manim:: ChangingCameraWidthAndRestore

    class ChangingCameraWidthAndRestore(MovingCameraScene):
        def construct(self):
            text = Text("Hello World").set_color(BLUE)
            self.add(text)
            self.camera_frame.save_state()
            self.play(self.camera_frame.set_width, text.get_width() * 1.2)
            self.wait(0.3)
            self.play(Restore(self.camera_frame))

.. manim:: ChangingCameraWidthAndRevert

    class ChangingCameraWidthAndRevert(MovingCameraScene):
        def construct(self):
            text = Text("Hello World").set_color(BLUE)
            self.add(text)
            self.play(self.camera_frame.set_width, text.get_width() * 1.2)
            self.wait(0.3)
            self.play(self.camera_frame.set_width, 14)


.. manim:: MovingCameraCenter

    class MovingCameraCenter(MovingCameraScene):
        def construct(self):
            s = Square(color=RED, fill_opacity=0.5).move_to(2 * LEFT)
            t = Triangle(color=GREEN, fill_opacity=0.5).move_to(2 * RIGHT)
            self.wait(0.3)
            self.add(s, t)
            self.play(self.camera_frame.move_to, s)
            self.wait(0.3)
            self.play(self.camera_frame.move_to, t)

.. manim:: MovingAndZoomingCamera

    class MovingAndZoomingCamera(MovingCameraScene):
        def construct(self):
            s = Square(color=BLUE, fill_opacity=0.5).move_to(2 * LEFT)
            t = Triangle(color=YELLOW, fill_opacity=0.5).move_to(2 * RIGHT)
            self.add(s, t)
            self.play(self.camera_frame.move_to, s,
                      self.camera_frame.set_width,s.get_width()*2)
            self.wait(0.3)
            self.play(self.camera_frame.move_to, t,
                      self.camera_frame.set_width,t.get_width()*2)

            self.play(self.camera_frame.move_to, ORIGIN,
                      self.camera_frame.set_width,14)

.. manim:: MovingCameraOnGraph

    class MovingCameraOnGraph(GraphScene, MovingCameraScene):
        def setup(self):
            GraphScene.setup(self)
            MovingCameraScene.setup(self)
        def construct(self):
            self.camera_frame.save_state()
            self.setup_axes(animate=False)
            graph = self.get_graph(lambda x: np.sin(x),
                                   color=WHITE,
                                   x_min=0,
                                   x_max=3 * PI
                                   )
            dot_at_start_graph = Dot().move_to(graph.points[0])
            dot_at_end_grap = Dot().move_to(graph.points[-1])
            self.add(graph, dot_at_end_grap, dot_at_start_graph)
            self.play(self.camera_frame.scale, 0.5, self.camera_frame.move_to, dot_at_start_graph)
            self.play(self.camera_frame.move_to, dot_at_end_grap)
            self.play(Restore(self.camera_frame))
            self.wait()

.. manim:: FollowingGraphCamera

    class FollowingGraphCamera(GraphScene, MovingCameraScene):
        def setup(self):
            GraphScene.setup(self)
            MovingCameraScene.setup(self)
        def construct(self):
            self.camera_frame.save_state()
            self.setup_axes(animate=False)
            graph = self.get_graph(lambda x: np.sin(x),
                                   color=BLUE,
                                   x_min=0,
                                   x_max=3 * PI
                                   )
            moving_dot = Dot().move_to(graph.points[0]).set_color(ORANGE)

            dot_at_start_graph = Dot().move_to(graph.points[0])
            dot_at_end_grap = Dot().move_to(graph.points[-1])
            self.add(graph, dot_at_end_grap, dot_at_start_graph, moving_dot)
            self.play( self.camera_frame.scale,0.5,self.camera_frame.move_to,moving_dot)

            def update_curve(mob):
                mob.move_to(moving_dot.get_center())

            self.camera_frame.add_updater(update_curve)
            self.play(MoveAlongPath(moving_dot, graph, rate_func=linear))
            self.camera_frame.remove_updater(update_curve)

            self.play(Restore(self.camera_frame))


Note: ZoomedScene is derived class of MovingCameraScene,
so one can use all functionality that were used before in the MovingCameraScene examples.

.. manim:: UseZoomedScene

    class UseZoomedScene(ZoomedScene):
        def construct(self):
            dot = Dot().set_color(GREEN)
            self.add(dot)
            self.wait(1)
            self.activate_zooming(animate=False)
            self.wait(1)
            self.play(dot.shift, LEFT)

.. manim:: ChangingZoomScale

    class ChangingZoomScale(ZoomedScene):
        CONFIG = {
            "zoom_factor": 0.3,
            "zoomed_display_height": 1,
            "zoomed_display_width": 3,
            "image_frame_stroke_width": 20,
            "zoomed_camera_config": {
                "default_frame_stroke_width": 3,
            },
        }
        def construct(self):
            dot = Dot().set_color(GREEN)
            sq = Circle(fill_opacity=1, radius=0.2).next_to(dot, RIGHT)
            self.add(dot, sq)
            self.wait(1)
            self.activate_zooming(animate=False)
            self.wait(1)
            self.play(dot.shift, LEFT * 0.3)

            self.play(self.zoomed_camera.frame.scale, 4)
            self.play(self.zoomed_camera.frame.shift, 0.5 * DOWN)


.. manim:: MovingZoomedSceneAround

    class MovingZoomedSceneAround(ZoomedScene):
    # contributed by TheoremofBeethoven, www.youtube.com/c/TheoremofBeethoven
        CONFIG = {
            "zoom_factor": 0.3,
            "zoomed_display_height": 1,
            "zoomed_display_width": 6,
            "image_frame_stroke_width": 20,
            "zoomed_camera_config": {
                "default_frame_stroke_width": 3,
            },
        }

        def construct(self):
            dot = Dot().shift(UL * 2)
            image = ImageMobject(np.uint8([[0, 100, 30, 200],
                                           [255, 0, 5, 33]]))
            image.set_height(7)
            frame_text = Text("Frame", color=PURPLE).scale(1.4)
            zoomed_camera_text = Text("Zoomed camera", color=RED).scale(1.4)

            self.add(image, dot)
            zoomed_camera = self.zoomed_camera
            zoomed_display = self.zoomed_display
            frame = zoomed_camera.frame
            zoomed_display_frame = zoomed_display.display_frame

            frame.move_to(dot)
            frame.set_color(PURPLE)
            zoomed_display_frame.set_color(RED)
            zoomed_display.shift(DOWN)

            zd_rect = BackgroundRectangle(zoomed_display, fill_opacity=0, buff=MED_SMALL_BUFF)
            self.add_foreground_mobject(zd_rect)

            unfold_camera = UpdateFromFunc(zd_rect, lambda rect: rect.replace(zoomed_display))

            frame_text.next_to(frame, DOWN)

            self.play(ShowCreation(frame), FadeInFrom(frame_text, direction=DOWN))
            self.activate_zooming()

            self.play(self.get_zoomed_display_pop_out_animation(), unfold_camera)
            zoomed_camera_text.next_to(zoomed_display_frame, DOWN)
            self.play(FadeInFrom(zoomed_camera_text, direction=DOWN))
            # Scale in        x   y  z
            scale_factor = [0.5, 1.5, 0]
            self.play(
                frame.scale, scale_factor,
                zoomed_display.scale, scale_factor,
                FadeOut(zoomed_camera_text),
                FadeOut(frame_text)
            )
            self.wait()
            self.play(ScaleInPlace(zoomed_display, 2))
            self.wait()
            self.play(frame.shift, 2.5 * DOWN)
            self.wait()
            self.play(self.get_zoomed_display_pop_out_animation(), unfold_camera, rate_func=lambda t: smooth(1 - t))
            self.play(Uncreate(zoomed_display_frame), FadeOut(frame))
            self.wait()
