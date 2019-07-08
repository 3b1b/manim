Making a Scene
==============

To make a scene, jump on the table and do a dance. Oh, a manim scene? Alright.

A scene is what renders when manim is executed. Each scene contains mobjects, which can then be animated as
previously explained. In code, a scene is a class that extends ``Scene`` and implements the ``construct``
function, like so:

.. code-block:: python
   :linenos:

   from manimlib.imports import *

   class ExampleScene(Scene):
       def construct(self):
           # Add and animate mobjects here