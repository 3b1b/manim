Making a Scene
==============

A scene is what renders when manim is executed. Each scene contains mobjects, which can then be animated as
previously explained. In code, a scene is a class that extends ``Scene`` and implements the ``construct``
function. Manim will execute this function to render the scene. Mobjects are added to the scene by declaring
them. Animations are added with a ``self.play()`` call, becuase they must be played by the scene.

.. code-block:: python
   :linenos:

   from manimlib.imports import *

   class ExampleScene(Scene):
       def construct(self):
           # Add mobjects here
           mobject = Mobject()

           # Animate mobjects here
           self.play(Animate(mobject))