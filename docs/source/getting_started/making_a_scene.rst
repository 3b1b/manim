Making a Scene
==============

A scene is what renders when manim is executed. Each scene contains mobjects, which can then be animated as
previously explained. In code, a scene is a class that extends ``Scene`` and implements the ``construct``
function, like so. Manim will execute this function to render the scene.

.. code-block:: python
   :linenos:

   from manimlib.imports import *

   class ExampleScene(Scene):
       def construct(self):
           # Add and animate mobjects here