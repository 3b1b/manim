A deeper look
=============

This document will focus on understanding manim's output files and some of the
main command line flags available.

.. note:: This tutorial picks up where :doc:`quickstart` left of, so please
          read that document before starting this one.

Manim output folders
********************

At this point, you have just executed the following command.

.. code-block:: bash

   $ manim scene.py SquareToCircle -pl

Let's dissect what just happened step by step.  First, this command executes
manim on the file ``scene.py``, which contains our animation code.  Further,
this command tells manim exactly which ``Scene`` to be rendered, in this case
it is ``SquareToCircle``.  This is necessary because a single scene file may
contain more than one scene.  Next, the flag `-p` tells manim to play the scene
once it's rendered, and the `-l` flag tells manim to render the scene in low
quality.

After the video is rendered, you will see that manim has generated some new
files and the project folder will look as follows.

.. code-block:: bash

   project/
   ├─scene.py
   └─media
     ├─videos
     |  └─scene
     |     └─480p15
     |        ├─SquareToCircle.mp4
     |        └─partial_movie_files
     ├─text
     └─Tex


There are quite a few new files.  The main output is in
``media/videos/scene/480p15/SquareToCircle.mp4``.  By default, the ``media``
folder will contain all of manim's output files.  The ``media/videos``
subfolder contains the rendered videos.  Inside of it, you will find one folder
for each different video quality.  In our case, since we used the ``-l`` flag,
the video was generated at 480 resolution at 15 frames per second from the
``scene.py`` file.  Therefore, the output can be found inside
``media/videos/scene/480p15``.  The additional folders
``media/videos/scene/480p15/partial_movie_files`` as well as ``media/text`` and
``media/Tex`` contain files that are used by manim internally.

You can see how manim makes use of the generated folder structure by executing
the following command,

.. code-block:: bash

   $ manim scene.py SquareToCircle -pe

The ``-l`` flag (for low quality) has been replaced by the ``-e`` flag, for
high quality.  Manim will take considerably longer to render this file, and it
will play it once it's done since we are using the ``-p`` flag.  The output
should look like this:

.. manim:: SquareToCircle3
   :hide_source:
   :quality: high

   class SquareToCircle3(Scene):
       def construct(self):
           circle = Circle()                    # create a circle
           circle.set_fill(PINK, opacity=0.5)   # set color and transparency

           square = Square()                    # create a square
           square.flip(RIGHT)                   # flip horizontally
           square.rotate(-3 * TAU / 8)          # rotate a certain amount

           self.play(ShowCreation(square))      # animate the creation of the square
           self.play(Transform(square, circle)) # interpolate the square into the circle
           self.play(FadeOut(square))           # fade out animation

And the folder structure should look as follows.

.. code-block:: bash

   project/
   ├─scene.py
   └─media
     ├─videos
     | └─scene
     |   ├─480p15
     |   | ├─SquareToCircle.mp4
     |   | └─partial_movie_files
     |   └─1080p60
     |     ├─SquareToCircle.mp4
     |     └─partial_movie_files
     ├─text
     └─Tex

Manim has created a new folder ``media/videos/1080p60``, which corresponds to
the high resolution and the 60 frames per second.  Inside of it, you can find
the new ``SquareToCircle.mp4``, as well as the corresponding
``partial_movie_files``.

When working on a project with multiple scenes, and trying out multiple
resolutions, the structure of the output directories will keep all your videos
organized.

Further, manim has the option to output the last frame of a scene, when adding
the flag ``-s``. This is the fastest option to quickly get a preview of a scene.
The corresponding folder structure looks like this:

.. code-block:: bash

   project/
   ├─scene.py
   └─media
     ├─images
     | └─scene
     |   ├─SquareToCircle.png
     ├─videos
     | └─scene
     |   ├─480p15
     |   | ├─SquareToCircle.mp4
     |   | └─partial_movie_files
     |   └─1080p60
     |     ├─SquareToCircle.mp4
     |     └─partial_movie_files
     ├─text
     └─Tex

Saving the last frame with ``-s`` can be combined with the flags for different
resolutions, e.g. ``-s -l``, ``-s -e``




Some command line flags
***********************

When executing the command

.. code-block:: bash

   $ manim scene.py SquareToCircle -pl

it was necessary to specify which ``Scene`` class to render.  This is because a
single file can contain more than one ``Scene`` class.  If your file contains
multiple ``Scene`` classes, and you want to render them all, you can use the
``-a`` flag.

As discussed previously, the ``-l`` specifies low render quality.  This does
not look very good, but is very useful for rapid prototyping and testing.  The
other options that specify render quality are ``-m``, ``-e``, and ``-k`` for
medium, high, and 4k quality, respectively.

The ``-p`` flag plays the animation once it is rendered.  If you want to open
the file browser at the location of the animation instead of playing it, you
can use the ``-f`` flag.  You can also omit these two flags.

Finally, by default manim will output .mp4 files.  If you want your animations
in .gif format instead, use the ``-i`` flag.  The output files will be in the
same folder as the .mp4 files, and with the same name, but different file
extension.

This was a quick review of some of the most frequent command line flags.  For a
thorough review of all flags available, see :doc:`configuration`.
