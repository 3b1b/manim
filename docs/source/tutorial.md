# Tutorial

[NOTE:] this is some text I wrote that was originally meant to be part of the
quickstart.  However, after some thought I've decided that it's probably a bit
too much for the quickstart, as the quickstart document is supposed to showcase
the quickest way of getting up and running with manim.  I've moved it here for
now, but feel free to edit/delete/move this text elsewhere in the
documentation.


## A deeper look

Let's dissect what just happened step by step.  First, the following command

```bash
$ manim scene.py SquareToCircle -pl
```

executes `manim` on the file `scene.py`, which contains our animation code.
Further, this command tells manim exactly which `Scene` to be rendered, in this
case it is `SquareToCircle`.  A single scene file may contain more than one
scene.  Next, the flag `-p` tells manim to play the scene once it's rendered,
and the `-l` flag tells manim to render the scene in low quality.

After the video is rendered, you will see that manim has generated some new
files and the project folder will look as follows.

```
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
```

There are quite a few new files.  The main output is in
`media/videos/scene/480p15/SquareToCircle.mp4`.  By default, the `media` folder
will contain all of manim's output files.  The `media/videos` subfolder
contains the rendered videos.  Inside of it, you will find one folder for each
different video quality.  In our case, since we used the `-l` flag, the video
was generated at 480p at 15 frames per second from the `scene.py` file.
Therefore, the output can be found inside `media/videos/scene/480p15`.  The
additional folders `media/videos/scene/480p15/partial_movie_files` as well as
`media/text` and `media/Tex` contain files that are used by manim internally.

You can see how manim makes use of the generated folder structure by executing
the following command,

```bash
$ manim scene.py SquareToCircle -pk
```

The `-l` flag (for low quality) has been replaced by the `-k` flag, for 4K
quality.  Manim will take considerably longer to render this file, and it will
play it once it's done since we are using the `-p` flag.  The output should
look like this:

![first scene output](_static/quickstart/first_scene_4k.gif)

And the folder structure should look as follows.

```
project/
├─scene.py
└─media
  ├─videos
  | └─scene
  |   ├─480p15
  |   | ├─SquareToCircle.mp4
  |   | └─partial_movie_files
  |   └─2160p60
  |     ├─SquareToCircle.mp4
  |     └─partial_movie_files
  ├─text
  └─Tex
```

Manim has created a new folder `media/videos/2160p60`, which corresponds to the
resolution and the 60 frames per second corresponding to 4k quality.  Inside of
it, you can find the new `SquareToCircle.mp4`, as well as the corresponding
`partial_movie_files`.
