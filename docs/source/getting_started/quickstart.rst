Quick Start
===========

After installing the manim environment according to the instructions on the
:doc:`installation` page, you can try to make a scene yourself from scratch.

First, create a new ``.py`` file (such as ``start.py``) according to the following
directory structure:

.. code-block:: text
    :emphasize-lines: 8

    manim/
    ├── manimlib/
    │   ├── animation/
    │   ├── ...
    │   ├── default_config.yml
    │   └── window.py
    ├── custom_config.yml
    └── start.py

And paste the following code (I will explain the function of each line in detail later):

.. code-block:: python
    :linenos:

    from manimlib import *

    class SquareToCircle(Scene):
        def construct(self):
            circle = Circle()
            circle.set_fill(BLUE, opacity=0.5)
            circle.set_stroke(BLUE_E, width=4)

            self.add(circle)

And run this command:

.. code-block:: sh

    manimgl start.py SquareToCircle

A window will pop up on the screen. And then you can :

- scroll the middle mouse button to move the screen up and down
- hold down the :kbd:`z` on the keyboard while scrolling the middle mouse button to zoom the screen
- hold down the :kbd:`s` key on the keyboard and move the mouse to pan the screen
- hold down the :kbd:`d` key on the keyboard and move the mouse to change the three-dimensional perspective.

Finally, you can close the window and exit the program by pressing :kbd:`q`.

Run this command again:

.. code-block:: sh

    manimgl start.py SquareToCircle -os

At this time, no window will pop up. When the program is finished, this rendered
image will be automatically opened (saved in the subdirectory ``images/`` of the same
level directory of ``start.py`` by default):

.. image:: https://cdn.jsdelivr.net/gh/manim-kindergarten/CDN@master/manimgl_assets/quickstart/SquareToCircle.png
    :align: center

Make an image
-------------

Next, let's take a detailed look at what each row does.

**Line 1**:

.. code-block:: python
    
    from manimlib import *
    
This will import all the classes that may be used when using manim.

**Line 3**:

.. code-block:: python

    class SquareToCircle(Scene):

Create a :class:`Scene` subclass ``SquareToCircle``, which will be
the scene you write and render.

**Line 4**:

.. code-block:: python

    def construct(self):

Write the ``construct()`` method, the content of which will determine
how to create the mobjects in the screen and what operations need to be performed.

**Line 5**:

.. code-block:: python

    circle = Circle()

Create a circle (an instance of the :class:`Circle` class), called ``circle``

**Line 6~7**:

.. code-block:: python

    circle.set_fill(BLUE, opacity=0.5)
    circle.set_stroke(BLUE_E, width=4)

Set the circle style by calling the circle's method.

- The ``.set_fill()`` method sets the fill color of this circle to blue (``BLUE``, defined in :doc:`../documentation/constants`), and the fill transparency to 0.5.
- The ``.set_stroke()`` method sets the stroke color of this circle to dark blue (``BLUE_E``, defined in :doc:`../documentation/constants`), and the stroke width to 4.

**Line 9**:

.. code-block:: python

    self.add(circle)

Add this circle to the screen through the ``.add()`` method of :class:`Scene`.

Add animations
--------------

Let's change some codes and add some animations to make videos instead of just pictures.

.. code-block:: python
    :linenos:

    from manimlib import *

    class SquareToCircle(Scene):
        def construct(self):
            circle = Circle()
            circle.set_fill(BLUE, opacity=0.5)
            circle.set_stroke(BLUE_E, width=4)
            square = Square()

            self.play(ShowCreation(square))
            self.wait()
            self.play(ReplacementTransform(square, circle))
            self.wait()

Run this command this time:

.. code-block:: sh

    manimgl start.py SquareToCircle

The pop-up window will play animations of drawing a square and transforming
it into a circle. If you want to save this video, run:

.. code-block:: sh
    
    manimgl start.py SquareToCircle -o

This time there will be no pop-up window, but the video file (saved in the subdirectory
``videos/`` of the same level directory of ``start.py`` by default) will be automatically
opened after the operation is over:

.. raw:: html

    <video class="manim-video" controls loop autoplay src="https://cdn.jsdelivr.net/gh/manim-kindergarten/CDN@master/manimgl_assets/quickstart/SquareToCircle.mp4"></video>

Let's take a look at the code this time. The first 7 lines are the same as the previous
ones, and the 8th line is similar to the 5th line, which creates an instance of the
:class:`Square` class and named it ``square``.

**Line 10**:

.. code-block:: python

    self.play(ShowCreation(square))

An animation is played through :class:`Scene`'s ``.play()`` method. :class:`ShowCreation`
is an animation that shows the process of creating a given mobject.
``self.play(ShowCreation(square))`` is to play the animation of creating ``square``.

**Line 11**:

.. code-block:: python

    self.wait()

Use :class:`Scene`'s ``.wait()`` method to pause (default 1s), you can pass in
parameters to indicate the pause time (for example, ``self.wait(3)`` means pause for 3s).

**Line 12**:

.. code-block:: python

    self.play(ReplacementTransform(square, circle))

Play the animation that transforms ``square`` into ``circle``.
``ReplacementTransform(A, B)`` means to transform A into B's pattern and replace A with B.

**Line 13**: Same as line 11, pause for 1s.


Enable interaction
------------------

Interaction is a new feature of the new version. You can add the following line
at the end of the code to enable interaction:

.. code-block:: python

    self.embed()

Then run ``manimgl start.py SquareToCircle``. 

After the previous animation is executed, the ipython terminal will be opened on
the command line. After that, you can continue to write code in it, and the statement
you entered will be executed immediately after pressing :kbd:`Enter`.

For example: input the following lines (without comment lines) into it respectively
(``self.play`` can be abbreviated as ``play`` in this mode):

.. code-block:: python

    # Stretched 4 times in the vertical direction
    play(circle.animate.stretch(4, dim=0))
    # Rotate the ellipse 90°
    play(Rotate(circle, TAU / 4))
    # Move 2 units to the right and shrink to 1/4 of the original
    play(circle.animate.shift(2 * RIGHT), circle.animate.scale(0.25))
    # Insert 10 curves into circle for non-linear transformation (no animation will play)
    circle.insert_n_curves(10)
    # Apply a complex transformation of f(z)=z^2 to all points on the circle
    play(circle.animate.apply_complex_function(lambda z: z**2))
    # Close the window and exit the program
    exit()

You will get an animation similar to the following:

.. raw:: html

    <video class="manim-video" controls loop autoplay src="https://cdn.jsdelivr.net/gh/manim-kindergarten/CDN@master/manimgl_assets/quickstart/SquareToCircleEmbed.mp4"></video>

If you want to enter the interactive mode directly, you don't have to write an
empty scene containing only ``self.embed()``, you can directly run the following command
(this will enter the ipython terminal while the window pops up):

.. code-block:: sh

    manimgl

You succeeded!
--------------

After reading the above content, you already know how to use manim.
Below you can see some examples, in the :doc:`example_scenes` page.
But before that, you'd better have a look at the :doc:`configuration` of manim.

