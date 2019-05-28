Learning by Example
===================

You create videos in manim by writing :class:`~scene.scene.Scene` instances.
``example_scenes.py`` contains a few simple ones that we can use to learn about
manim. For instance, take ``SquareToCircle``.

.. code-block:: python
   :linenos:

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

:meth:`~scene.scene.Scene.construct` specifies what is displayed on the screen
when the :class:`~scene.scene.Scene` is rendered to video. You can render a
:class:`~scene.scene.Scene` by running ``extract_scene.py``. Run ``python
extract_scene.py -h`` to see how it's used.

.. code-block:: none

   > python extract_scene.py -h
   usage: extract_scene.py [-h] [-p] [-w] [-s] [-l] [-m] [-g] [-f] [-t] [-q] [-a]
                   [-o OUTPUT_NAME] [-n START_AT_ANIMATION_NUMBER]
                   [-r RESOLUTION] [-c COLOR] [-d OUTPUT_DIRECTORY]
                   file [scene_name]

   positional arguments:
     file                  path to file holding the python code for the scene
     scene_name            Name of the Scene class you want to see

   optional arguments:
     -h, --help            show this help message and exit
     -p, --preview
     -w, --write_to_movie
     -s, --show_last_frame
     -l, --low_quality
     -m, --medium_quality
     -g, --save_pngs
     -f, --show_file_in_finder
     -t, --transparent
     -q, --quiet
     -a, --write_all
     -o OUTPUT_NAME, --output_name OUTPUT_NAME
     -n START_AT_ANIMATION_NUMBER, --start_at_animation_number START_AT_ANIMATION_NUMBER
     -r RESOLUTION, --resolution RESOLUTION
     -c COLOR, --color COLOR
     -d OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY

The most common flags are ``-p``, to automatically play the generated video,
``-l``, to render in lower quality in favor of speed, and ``-s``, to show the
last frame of the :class:`~scene.scene.Scene` for faster development. Run
``python extract_scene.py example_scenes.py SquareToCircle -pl`` to produce a
file called SquareToCircle.mp4 in the media directory that you have configured,
and automatically play it.

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/8tvYDIGLJJA?ecver=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

Let's step through each line of the :class:`~scene.scene.Scene`. Lines 3 and 4
instantiate a :class:`~mobject.geometry.Circle` and
:class:`~mobject.geometry.Square`, respectively. Both of these subclass
:class:`~mobject.mobject.Mobject`, the base class for objects in manim. Note
that instantiating a :class:`~mobject.mobject.Mobject` does not add it to the
:class:`~scene.scene.Scene`, so you wouldn't see anything if you were to render
the :class:`~scene.scene.Scene` at this point.

.. code-block:: python
   :linenos:
   :lineno-start: 3

   circle = Circle()
   square = Square()

Lines 5, 6, and 7 apply various modifications to the mobjects before animating
them.  The call to :meth:`~mobject.mobject.Mobject.flip` on line 5 flips the
:class:`~mobject.geometry.Square` across the RIGHT vector.  This is equivalent
to a refection across the x-axis. Then the call to
:meth:`~mobject.mobject.Mobject.rotate` on line 6 rotates the
:class:`~mobject.geometry.Square` 3/8ths of a full rotation counterclockwise.
Finally, the call to :meth:`~mobject.mobject.Mobject.set_fill` on line 7 sets
the fill color for the :class:`~mobject.geometry.Circle` to pink, and its
opacity to 0.5.

.. code-block:: python
   :linenos:
   :lineno-start: 5

   square.flip(RIGHT)
   square.rotate(-3 * TAU / 8)
   circle.set_fill(PINK, opacity=0.5)

Line 9 is the first to generate video.
:class:`~animation.creation.ShowCreation`,
:class:`~animation.transform.Transform`, and
:class:`~animation.creation.FadeOut` are
:class:`~animation.animation.Animation` instances. Each
:class:`~animation.animation.Animation` takes one or more
:class:`~mobject.mobject.Mobject` instances as arguments, which it animates
when passed to :meth:`~scene.scene.Scene.play`. This is how video is typically
created in manim. :class:`~mobject.mobject.Mobject` instances are automatically
added to the :class:`~scene.scene.Scene` when they are animated. You can add a
:class:`~mobject.mobject.Mobject` to the :class:`~scene.scene.Scene` manually
by passing it as an argument to :meth:`~scene.scene.Scene.add`.

.. code-block:: python
   :linenos:
   :lineno-start: 9

   self.play(ShowCreation(square))
   self.play(Transform(square, circle))
   self.play(FadeOut(square))

:class:`~animation.creation.ShowCreation` draws a
:class:`~mobject.mobject.Mobject` to the screen,
:class:`~animation.transform.Transform` morphs one
:class:`~mobject.mobject.Mobject` into another, and
:class:`~animation.creation.FadeOut` fades a
:class:`~mobject.mobject.Mobject` out of the :class:`~scene.scene.Scene`. Note
that only the first argument to :class:`~animation.transform.Transform` is
modified, and the second is not added to the :class:`~scene.scene.Scene`. After
line 10 is executed ``square`` is a :class:`~mobject.geometry.Square` instance
with the shape of a :class:`~mobject.geometry.Circle`.
