Animation
=========



The simplest of which is ``Scene.add``. The object appears on the first frame
without any animation::

  class NoAnimation(Scene):
      def construct(self):
          square = Square()
          self.add(square))

Animation are used in conjunction with ``scene.Play``

Fade
----

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationFadeIn.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationFadeIn(Scene):
      def construct(self):
          square = Square()

          anno = TextMobject("Fade In")
          anno.shift(2 * DOWN)
          self.add(anno)
          self.play(FadeIn(square))

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationFadeOut.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationFadeOut(Scene):
      def construct(self):
          square = Square()

          anno = TextMobject("Fade Out")
          anno.shift(2 * DOWN)
          self.add(anno)
          self.add(square)
          self.play(FadeOut(square))



.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationFadeInFrom.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationFadeInFrom(Scene):
      def construct(self):
          square = Square()
          for label, edge in zip(
              ["LEFT", "RIGHT", "UP", "DOWN"], [LEFT, RIGHT, UP, DOWN]
          ):
              anno = TextMobject(f"Fade In from {label}")
              anno.shift(2 * DOWN)
              self.add(anno)

              self.play(FadeInFrom(square, edge))
              self.remove(anno, square)



.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationFadeOutAndShift.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationFadeOutAndShift(Scene):
      def construct(self):
          square = Square()
          for label, edge in zip(
              ["LEFT", "RIGHT", "UP", "DOWN"], [LEFT, RIGHT, UP, DOWN]
          ):
              anno = TextMobject(f"Fade Out and shift {label}")
              anno.shift(2 * DOWN)
              self.add(anno)

              self.play(FadeOutAndShift(square, edge))
              self.remove(anno, square)



.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationFadeInFromLarge.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationFadeInFromLarge(Scene):
      def construct(self):
          square = Square()

          for factor in [0.1, 0.5, 0.8, 1, 2, 5]:
              anno = TextMobject(f"Fade In from large scale\_factor={factor}")
              anno.shift(2 * DOWN)
              self.add(anno)

              self.play(FadeInFromLarge(square, scale_factor=factor))
              self.remove(anno, square)

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationFadeInFromPoint.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationFadeInFromPoint(Scene):
      def construct(self):
          square = Square()
          for i in range(-6, 7, 2):
              anno = TextMobject(f"Fade In from point {i}")
              anno.shift(2 * DOWN)
              self.add(anno)
              self.play(FadeInFromPoint(square, point=i))
              self.remove(anno, square)



Grow
----

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationGrowFromEdge.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationGrowFromEdge(Scene):
      def construct(self):

          for label, edge in zip(
              ["LEFT", "RIGHT", "UP", "DOWN"], [LEFT, RIGHT, UP, DOWN]
          ):
              anno = TextMobject(f"Grow from {label} edge")
              anno.shift(2 * DOWN)
              self.add(anno)
              square = Square()
              self.play(GrowFromEdge(square, edge))
              self.remove(anno, square)



.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationGrowFromCenter.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationGrowFromCenter(Scene):
      def construct(self):
          square = Square()

          anno = TextMobject("Grow from center")
          anno.shift(2 * DOWN)
          self.add(anno)

          self.play(GrowFromCenter(square))




Diagonal Directions
-------------------

You can combine cardinal directions to form diagonal animations

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/AnimationFadeInFromDiagonal.mp4" type="video/mp4">
    </video>

.. code-block:: python

  class AnimationFadeInFromDiagonal(Scene):
      def construct(self):
          square = Square()
          for diag in [UP + LEFT, UP + RIGHT, DOWN + LEFT, DOWN + RIGHT]:
              self.play(FadeInFrom(square, diag))

.. note::
    You can also use the abbreviated forms like ``UL, UR, DL, DR``.
    See :ref:`ref-directions`.
