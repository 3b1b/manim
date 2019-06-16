<img src="logo/cropped.png"/>

[![Build Status](https://travis-ci.org/3b1b/manim.svg?branch=master)](https://travis-ci.org/3b1b/manim)
[![Documentation](https://img.shields.io/badge/docs-EulerTour-blue.svg)](https://www.eulertour.com/learn/manim/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)
[![Manim Subreddit](https://img.shields.io/reddit/subreddit-subscribers/manim.svg?color=ff4301&label=reddit)](https://www.reddit.com/r/manim/)
[![Manim Discord](https://img.shields.io/discord/581738731934056449.svg?label=discord)](https://discord.gg/mMRrZQW)

Manim is an animation engine for explanatory math videos. It's used to create precise animations programmatically, as seen in the videos at [3Blue1Brown](https://www.3blue1brown.com/).

## Installation
You can install manim from PyPI via pip. (Use ``pip3`` if you have Python versions other than 3.x installed.)

```sh
pip install manimlib
```

System requirements are [Python 3.7](https://www.python.org/downloads/release/python-373/), [cairo](https://www.cairographics.org), [ffmpeg](https://www.ffmpeg.org), [sox](http://sox.sourceforge.net) (optional, for working with audio), [latex](https://www.latex-project.org) (optional, for writing text and equations).

More detailed installation procedures can be found in the [installation readme](https://github.com/3b1b/manim/blob/master/INSTALLATION.md).

You can now use it via the `manim` command. For example:

```sh
manim my_project.py MyScene
```

For more usage options, take a look at the “Using manim“ sections further below.

## Using manim
Both of the following commands will render an example scene:
```sh
python3 -m manim example_scenes.py SquareToCircle -pl
manim example_scenes.py SqaureToCircle -pl
```
The `-p` flag in the command above is for previewing, meaning the video file will automatically open when it is done rendering. The `-l` flag is for a faster rendering at a lower quality.

Some other useful flags include:

* `-s` to skip to the end and just show the final frame.
* `-n <number>` to skip ahead to the `n`'th animation of a scene.
* `-f` to show the file in finder (for OSX).

Set `MEDIA_DIR` environment variable to specify where the image and animation files will be written.

Look through the `old_projects` folder to see the code for previous 3b1b videos.  Note, however, that developments are often made to the library without considering backwards compatibility with those old projects.  To run an old project with a guarantee that it will work, you will have to go back to the commit which completed that project.

While developing a scene, the `-sp` flags are helpful to just see what things look like at the end without having to generate the full animation.  It can also be helpful to use the `-n` flag to skip over some number of animations.

### Documentation
Documentation is in progress at [manim.readthedocs.io](https://manim.readthedocs.io).

### Walkthrough
Todd Zimmerman put together a [tutorial](https://talkingphysics.wordpress.com/2019/01/08/getting-started-animating-with-manim-and-python-3-7/) on getting started with manim, which has been updated to run on python 3.7.

### Live Streaming
To live stream your animations, simply run manim with the `--livestream` option.

```sh
> python -m manim --livestream
Writing to media/videos/scene/scene/1080p30/LiveStreamTemp.mp4

Manim is now running in streaming mode. Stream animations by passing
them to manim.play(), e.g.
>>> c = Circle()
>>> manim.play(ShowCreation(c))

>>>
```

It is also possible to stream directly to Twitch. To do that simply pass
--livestream and --to-twitch to manim and specify the stream key with
--with-key. Then when you follow the above example the stream will directly
start on your Twitch channel (with no audio support).


## Contributing
Is always welcome. In particular, there is a dire need for tests and documentation.


## License
All files in the directories active_projects and old_projects, which by and large generate the visuals for 3b1b videos, are copyright 3Blue1Brown.

The general purpose animation code found in the remainder of the repository, on the other hand, is under the MIT license.
