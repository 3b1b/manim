Animation
=========

Animation is the core of manim.
*MObjects* can be animated in a scene by applying the method ``Scene.play``.

.. code-block:: python

        class SimpleAnimation(Scene):
            def construct(self):
                triangle = Triangle()
                self.play(ShowCreation(triangle))
                self.wait(2)

*MObjects* can also simply be added to a scene by ``Scene.add``
The object appears on the first frame
without any animation::

  class NoAnimation(Scene):
      def construct(self):
          square = Square()
          self.add(square))

The animation classes can take the following parameters :

*run_time* \: float, optional, default: DEFAULT_ANIMATION_RUN_TIME
        the duration of the animation


ShowCreation
------------

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationShowCreation.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationShowCreation(Scene):
            def construct(self):
                square = Square()
                anno = TextMobject("Show Creation")
                anno.shift(2*DOWN)
                self.add(anno)
                self.play(ShowCreation(square))

Uncreate
--------

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationUncreate.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationUncreate(Scene):
            def construct(self):
                square = Square()
                anno = TextMobject("Uncreate")
                anno.shift(2*DOWN)
                self.add(anno)
                self.add(square)
                self.play(Uncreate(square))

DrawBorderThenFill
------------------

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationDrawBorderThenFill.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationDrawBorderThenFill(Scene):
            def construct(self):
                square = Square(fill_opacity=1.0)
                anno = TextMobject("Draw border then fill")
                anno.shift(2*DOWN)
                self.add(anno)
                self.add(square)
                self.play(DrawBorderThenFill(square))

Write
-----

Writes the text object passed as argument.
Should be used with classes like *TexMobject* or *TextMobject*.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationWrite.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationWrite(Scene):
            def construct(self):
                text = TextMobject("Hello World")
                anno = TextMobject("Write")
                anno.shift(2*DOWN)
                self.add(anno)
                self.play(Write(text))

ShowIncreasingSubsets
---------------------

Should be used with a group, instance of *VGroup*.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationShowIncreasingSubsets.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationShowIncreasingSubsets(Scene):
            def construct(self):
                points = []
                for x in range(-5,6):
                    points.append(Dot(point=np.array([x, 0.0, 0.0])))
                group = VGroup(*points)
                self.play(ShowIncreasingSubsets(group, run_time=3.0))

ShowIncreasingSubsets
---------------------

Should be used with a group, instance of *VGroup*.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationShowSubmobjectsOneByOne.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationShowSubmobjectsOneByOne(Scene):
            def construct(self):
                points = []
                for x in range(-5,6):
                    points.append(Dot(point=np.array([x, 0.0, 0.0])))
                group = VGroup(*points)
                anno = TextMobject("Show submobjects one by one")
                anno.shift(2*DOWN)
                self.add(anno)
                self.play(ShowSubmobjectsOneByOne(group, run_time=3.0))

AddTextWordByWord
-----------------

This is indicated as broken in the source code.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationAddTextWordByWord.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationAddTextWordByWord(Scene):
            def construct(self):
                text = TextMobject(r"Hello World !\\This should be written word by word.")
                anno = TextMobject("Add text word by word")
                anno.shift(2*DOWN)
                self.add(anno)
                self.play(AddTextWordByWord(text, run_time=5.0))

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
