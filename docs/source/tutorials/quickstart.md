# Quickstart


This document will lead you step by step through the necessary procedure to get
`manim` up and running as soon as possible.


## Installation

[INSTALLATION INSTRUCTIONS GO HERE]. Note: when this section is done, delete
installation instructions from the GitHub repo README.

+ mention pip install
+ mention choco package
+ mention things about Cairo and LaTeX


## Start a new project

To start a new manim video project, all you need to do is choose a single
folder where all of the files related to the video will reside.  For this
example, this folder will be called `project`,

```
project/
```

Every file containing code that produces a video with manim will be stored
here, as well as `manim`'s output files and configuration files.


## Your first Scene

To produce your first scene, create a new file in your project folder

```
project/
└─scene.py
```

and copy the following code in it

```python
from manim import *

# all code must be contained inside the construct
# method of a class that inherits from Scene
class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()                   # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
        self.play(ShowCreation(circle))     # show the circle on screen
```

Then open your command line, navigate to your project directory, and execute
the following command:

```bash
$ manim scene.py SquareToCircle -pl
```

After some output, `manim` should render the scene into a .mp4 file, and open
that file with the default movie player application.  You should see a video
playing the following animation.
![first scene output](../_static/quickstart/first_scene.gif)

If you see the video and it looks correct, congrats! You just wrote your first
`manim` scene from scratch.  If you get an error message instead, or if do not
see a video, or if the video output does not look like this, it is likely that
`manim` has not been installed correctly. Please refer to the Troubleshooting
page for more information.

## Some bells and whistles

Our scene is a little basic, so let's add some bells and whistles.  Modify the
`scene.py` file to contain the following:

```python
from manim import *

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()                    # create a circle
        circle.set_fill(PINK, opacity=0.5)   # set color and transparency

        square = Square()                    # create a square
        square.flip(RIGHT)                   # flip horizontally
        square.rotate(-3 * TAU / 8)          # rotate a certain amount

        self.play(ShowCreation(square))      # animate the creation of the square
        self.play(Transform(square, circle)) # interpolate the square into the circle
        self.play(FadeOut(square))           # fade out animation
```

And render it using the following command:

```bash
$ manim scene.py SquareToCircle -pl
```

The output should look as follows.

![second scene output](../_static/quickstart/second_scene.gif)

This example shows one of the most basic features of `manim`: the ability to
implement complicated and perhaps mathematically-intensive animations (such as
cleanly interpolating between two geometric shapes) in very few lines of code.


## You're done!

With a working installation of manim, and the bare basics under your belt, it
is now time to start creating awesome mathematical animations.  For a more
extensive review of manim's features, as well as its configuration and other
settings, see the Tutorial page.  For a list of all available features, see the
Reference page.
