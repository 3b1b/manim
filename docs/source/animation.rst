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

ShowSubmojectsOneByOne
----------------------

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

Transform
---------

Transforms a *mobject* into another *mobject*.
This does not only perform the animation but changes the properties of the transformed object.

Parameters :

*mobject* \: Mobject
        object to be transformed

*target_mobject* \: Mobject, optional, default: None
        target object

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationTransform.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationTransform(Scene):
            def construct(self):
                square = Square()
                circle = Circle()
                anno = TextMobject("Transform")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(Transform(square, circle))
                square.generate_target()
                square.target.move_to(2*UP)
                self.play(MoveToTarget(square))

ReplacementTransform
--------------------

Same as Transforms.
However, the target object is the one that is now to be used for future actions.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationReplacementTransform.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationReplacementTransform(Scene):
            def construct(self):
                square = Square()
                circle = Circle()
                anno = TextMobject("Replacement Transform")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(ReplacementTransform(square, circle))
                circle.generate_target()
                circle.target.move_to(2*UP)
                self.play(MoveToTarget(circle))

TransformFromCopy
-----------------

Similar to ReplacementTransform but also keeps the first object as it was.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationTransformFromCopy.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationTransformFromCopy(Scene):
            def construct(self):
                square = Square()
                circle = Circle()
                anno = TextMobject("Transform from copy")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(TransformFromCopy(square, circle))
                self.remove(circle)
                self.wait(2)

ClockwiseTransform
------------------

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationClockwiseTransform.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationClockwiseTransform(Scene):
            def construct(self):
                square = Square()
                circle = Circle()
                anno = TextMobject("Clockwise transform")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(ClockwiseTransform(square, circle))

CounterclockwiseTransform
-------------------------

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationCounterclockwiseTransform.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationCounterclockwiseTransform(Scene):
            def construct(self):
                square = Square()
                circle = Circle()
                anno = TextMobject("Counterclockwise transform")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(CounterclockwiseTransform(square, circle))

MoveToTarget
------------

Move the *mobject* to its target.
A target must first be generated by calling ``Mobject.generate_target(use_deepcopy=False)``.
The target can then be accessed by the attribute ``Mobject.target``.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationMoveToTarget.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationMoveToTarget(Scene):
            def construct(self):
                square = Square()
                square.generate_target()
                square.target.shift(2*UP)
                anno = TextMobject("Move to target")
                anno.shift(2 * DOWN)
                self.add(square)
                self.play(MoveToTarget(square))

ApplyMethod
-----------

Similar to *MoveToTarget* but with a custom method.

Parameters :

*method* \:
        the method to apply. It must be the method of a *Mobject* and must return a *Mobject*.

*\*args* \:
        arguments to be passed to the method

*\*\*kwargs* \:
        meta-paramerters to be passed to the Animation

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationApplyMethod.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class CustomSquare(Square):
            def custom_method(self, color):
                self.set_color(color)
                self.shift(2 * UP)
                return self


        class AnimationApplyMethod(Scene):
            def construct(self):
                square = CustomSquare()
                anno = TextMobject("Apply method")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(ApplyMethod(square.custom_method, RED))

ApplyPointwiseFunction
----------------------

Applies a function on each point defining the *Mobject*.

Parameters :

*function* \:
        the function to apply at each point. It should return a point, numpy array of dimension 3.

*mobject* \:
        *Mobject* to which the function is applied at each point

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationApplyPointwiseFunction.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationApplyPointwiseFunction(Scene):
            def construct(self):
                square = Square()
                anno = TextMobject("Apply pointwise function")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(ApplyPointwiseFunction(lambda x: 2 * x + UP, square))

FadeToColor
-----------

Takes as second parameter the color to which the *Mobject* should fade to.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationFadeToColor.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationFadeToColor(Scene):
            def construct(self):
                square = Square(fill_opacity=1)
                anno = TextMobject("Fade to color")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(FadeToColor(square, RED))

ScaleInPlace
------------

Takes as second parameter the scaling factor.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationScaleInPlace.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationScaleInPlace(Scene):
            def construct(self):
                square = Square()
                anno = TextMobject("Scale in place")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(ScaleInPlace(square, 0.5))

ShrinkToCenter
--------------

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationShrinkToCenter.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationShrinkToCenter(Scene):
            def construct(self):
                square = Square()
                anno = TextMobject("Shrink to center")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(ShrinkToCenter(square))

Restore
-------

Restores the *Mobject* to a previous saved state.
A state is saved by applying ``Mobject.save_state()``.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationRestore.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationRestore(Scene):
            def construct(self):
                square = Square()
                anno = TextMobject("Restore")
                anno.shift(2 * DOWN)
                self.add(anno)
                square.save_state()
                circle = Circle()
                self.play(Transform(square, circle))
                square.generate_target()
                square.target.shift(2 * UP)
                self.play(MoveToTarget(square))
                self.play(Restore(square))

ApplyFunction
-------------

Applies a function the *Mobject*.

Parameters :

*function* \:
        the function to apply. It should return a *Mobject*.

*mobject* \:
        *Mobject* to which the function is applied

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationApplyFunction.mp4" type="video/mp4">
    </video>

.. code-block:: python

        def shift_up(mobject):
            return mobject.shift(2 * UP)


        class AnimationApplyFunction(Scene):
            def construct(self):
                square = Square()
                anno = TextMobject("Apply Function")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(ApplyFunction(shift_up, square))

ApplyMatrix
-----------

Applies a each point defining the *Mobject*, the transformation :

.. math::

        matrix \times point = new\_point

Parameters :

*matrix* \: matrix of 2x2, can be list of lists or numpy arrays
        the matrix to apply

*mobject* \:
        *Mobject* to which the matrix is applied

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationApplyMatrix.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationApplyMatrix(Scene):
            def construct(self):
                mat = [[1.0, 0.5], [1.0, 0.0]]
                square = Square()
                anno = TextMobject("Apply Matrix")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(ApplyMatrix(mat, square))

ApplyComplexFunction
--------------------

Applies a each point defining the *Mobject*, the complex function.
The function considers the point as a complex such that :

.. math::

        new\_x = imaginary(f(x+i*y))\\
        new\_y = real(f(x+i*y))

It performs the transformation and moves the object on an arc trajectory dependant of the function.

Parameters :

*function* \:
        the complex function to apply. It should take a complex as parameter and return a parameter.

*mobject* \:
        *Mobject* to which the function is applied at each point.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationApplyComplexFunction.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationApplyComplexFunction(Scene):
            def construct(self):
                square = Square()
                anno = TextMobject("Apply Complex Function")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.play(
                    ApplyComplexFunction(
                        lambda complex_num: complex_num + 2 * np.complex(0, 1), square
                    )
                )

CyclicReplace
-------------

Replaces every *Mobject* passed as an argument by the next on the list.

.. raw:: html

    <video width="560" height="315" controls>
        <source src="_static/animation/AnimationCyclicReplace.mp4" type="video/mp4">
    </video>

.. code-block:: python

        class AnimationCyclicReplace(Scene):
            def construct(self):
                square = Square()
                circle = Circle()
                circle.shift(2 * UP + 2 * RIGHT)
                triangle = Triangle()
                triangle.shift(2 * UP + 2 * LEFT)
                anno = TextMobject("Cyclic Replace")
                anno.shift(2 * DOWN)
                self.add(anno)
                self.add(square)
                self.add(circle)
                self.add(triangle)
                self.play(CyclicReplace(square, circle, triangle))

Swap
----

Alias for cyclic replace.

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
