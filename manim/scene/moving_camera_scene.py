"""A scene whose camera can be moved around.

.. SEEALSO::

    :mod:`.moving_camera`


Examples
--------

.. manim:: ChangingCameraWidthAndRestore

    class ChangingCameraWidthAndRestore(MovingCameraScene):
        def construct(self):
            text = Text("Hello World").set_color(BLUE)
            self.add(text)
            self.camera_frame.save_state()
            self.play(self.camera_frame.set_width, text.get_width() * 1.2)
            self.wait(0.3)
            self.play(Restore(self.camera_frame))


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

"""

__all__ = ["MovingCameraScene"]

from ..camera.moving_camera import MovingCamera
from ..scene.scene import Scene
from ..utils.iterables import list_update
from ..utils.family import extract_mobject_family_members


class MovingCameraScene(Scene):
    """
    This is a Scene, with special configurations and properties that
    make it suitable for cases where the camera must be moved around.

    .. SEEALSO::

        :class:`.MovingCamera`
    """

    CONFIG = {"camera_class": MovingCamera}

    def setup(self):
        """
        This method is used internally by Manim
        to set up the scene for proper use.
        """
        Scene.setup(self)
        assert isinstance(self.renderer.camera, MovingCamera)
        self.camera_frame = self.renderer.camera.frame
        # Hmm, this currently relies on the fact that MovingCamera
        # willd default to a full-sized frame.  Is that okay?
        return self

    def get_moving_mobjects(self, *animations):
        """
        This method returns a list of all of the Mobjects in the Scene that
        are moving, that are also in the animations passed.

        Parameters
        ----------
        *animations : Animation
            The Animations whose mobjects will be checked.
        """
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        all_moving_mobjects = extract_mobject_family_members(moving_mobjects)
        movement_indicators = self.renderer.camera.get_mobjects_indicating_movement()
        for movement_indicator in movement_indicators:
            if movement_indicator in all_moving_mobjects:
                # When one of these is moving, the camera should
                # consider all mobjects to be moving
                return list_update(self.mobjects, moving_mobjects)
        return moving_mobjects
