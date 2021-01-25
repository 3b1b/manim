Example Scenes
==============

.. manim-example:: WarpSquare
   :media: ../_static/example_scenes/WarpSquare.mp4

   class WarpSquare(Scene):
       def construct(self):
           square = Square()
           self.play(square.apply_complex_function, np.exp)
           self.wait()