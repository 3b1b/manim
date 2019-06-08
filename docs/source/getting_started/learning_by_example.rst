Learning by Example
===================

SquareToCircle
--------------

``example_scenes.py`` contains simple examples that we can use to learn about manim.

Go ahead and try out the ``SquareToCircle`` scene by running it with ``$ manim example_scenes.py SquareToCircle -p``
in manim directory.

.. code-block:: python
   :linenos:

   from manimlib.imports import *

   class SquareToCircle(Scene):
       def construct(self):
           circle = Circle()
           square = Square()
           square.flip(RIGHT)
           square.rotate(-3 * TAU / 8)
           circle.set_fill(PINK, opacity=0.5)

           self.play(ShowCreation(square))
           self.play(Transform(square, circle))
           self.play(FadeOut(square))

.. raw:: html

   <video width="560" height="315" controls>
       <source src="../_static/SquareToCircle.mp4" type="video/mp4">
   </video>


.. note::

  The flag ``-p`` plays the rendered video with default video player.

  Other frequently used flags are:

    * ``-l`` for rendering video in lower resolution (which renders faster)
    * ``-s`` to show the last frame of the video.

  Run ``manim -h`` all the available flags (``python -m manim -h`` if you installed it to a venv)


Let's step through each line of ``SquareToCircle``

.. code-block:: python
   :lineno-start: 3

   class SquareToCircle(Scene):

You create videos in manim by writing :class:`~scene.scene.Scene` classes.

Each :class:`~scene.scene.Scene` in manim is self-contained. That means everything
you created under this scene does not exist outside the class.

.. code-block:: python
   :lineno-start: 4

   def construct(self):

:meth:`~scene.scene.Scene.construct` specifies what is displayed on the screen
when the :class:`~scene.scene.Scene` is rendered to video.

.. code-block:: python
   :lineno-start: 5

   circle = Circle()
   square = Square()

``Circle()`` and ``Square()`` create :class:`~mobject.geometry.Circle` and :class:`~mobject.geometry.Square`.

Both of these are instances of :class:`~mobject.mobject.Mobject` subclasses, the base class for objects in manim. Note
that instantiating a :class:`~mobject.mobject.Mobject` does not add it to the
:class:`~scene.scene.Scene`, so you wouldn't see anything if you were to render
the :class:`~scene.scene.Scene` at this point.

.. code-block:: python
   :lineno-start: 7

   square.flip(RIGHT)
   square.rotate(-3 * TAU / 8)
   circle.set_fill(PINK, opacity=0.5)

``flip()`` ``rotate()`` ``set_fill()`` apply various modifications to the mobjects before animating
them.  The call to :meth:`~mobject.mobject.Mobject.flip` flips the
:class:`~mobject.geometry.Square` across the RIGHT vector.  This is equivalent
to a refection across the x-axis.

The call to :meth:`~mobject.mobject.Mobject.rotate` rotates the
:class:`~mobject.geometry.Square` 3/8ths of a full rotation counterclockwise.

The call to :meth:`~mobject.mobject.Mobject.set_fill` sets
the fill color for the :class:`~mobject.geometry.Circle` to pink, and its opacity to 0.5.

.. code-block:: python
   :lineno-start: 11

   self.play(ShowCreation(square))
   self.play(Transform(square, circle))
   self.play(FadeOut(square))

To generated animation, :class:`~animation.animation.Animation` classes are used.

Each :class:`~animation.animation.Animation` takes one or more :class:`~mobject.mobject.Mobject` instances as arguments, which it animates
when passed to :meth:`~scene.scene.Scene.play`. This is how video is typically
created in manim.

:class:`~mobject.mobject.Mobject` instances are automatically
added to the :class:`~scene.scene.Scene` when they are animated. You can add a
:class:`~mobject.mobject.Mobject` to the :class:`~scene.scene.Scene` manually
by passing it as an argument to :meth:`~scene.scene.Scene.add`.


:class:`~animation.creation.ShowCreation` draws a :class:`~mobject.mobject.Mobject` to the screen.

:class:`~animation.transform.Transform` morphs one :class:`~mobject.mobject.Mobject` into another.

:class:`~animation.creation.FadeOut` fades a :class:`~mobject.mobject.Mobject` out of the :class:`~scene.scene.Scene`.

.. note::

  Only the first argument to :class:`~animation.transform.Transform` is modified,
  the second is not added to the :class:`~scene.scene.Scene`. :class:`~animation.tranform.Transform`
  only changes the appearance but not the underlying properties.

  After the call to ``transform()`` ``square`` is still a :class:`~mobject.geometry.Square` instance
  but with the shape of :class:`~mobject.geometry.Circle`.
