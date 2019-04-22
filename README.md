# Manim - Mathematical Animation Engine
[![Documentation Status](https://readthedocs.org/projects/manim/badge/?version=latest)](https://manim.readthedocs.io/en/latest/?badge=latest)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)

Manim is an animation engine for explanatory math videos. It's used to create precise animations programmatically, as seen in the videos at [3Blue1Brown](https://www.3blue1brown.com/).

## Installation
Manim runs on python 3.7. You can install the python requirements with
`python3 -m pip install -r requirements.txt`. System requirements are
[cairo](https://www.cairographics.org), [latex](https://www.latex-project.org),
[ffmpeg](https://www.ffmpeg.org), and [sox](http://sox.sourceforge.net).

### Directly
```sh
git clone https://github.com/3b1b/manim.git
cd manim
python3 -m pip install -r requirements.txt
python3 -m manim example_scenes.py SquareToCircle -pl
```

### Directly (Windows)
1. [Install FFmpeg](https://www.wikihow.com/Install-FFmpeg-on-Windows).
2. Install Cairo. Download the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo. For most users, ``pycairo‑1.18.0‑cp37‑cp37m‑win32.whl`` will do fine.
    ```sh
    pip3 install C:\path\to\wheel\pycairo‑1.18.0‑cp37‑cp37m‑win32.whl
    ```
3. Install a LaTeX distribution. [MiKTeX](https://miktex.org/download) is recommended.

4. [Install SoX](https://sourceforge.net/projects/sox/files/sox/).

5. Install the remaining Python packages. Make sure that ``pycairo==1.17.1`` is changed to ``pycairo==1.18.0`` in requirements.txt.
    ```sh
    git clone https://github.com/3b1b/manim.git
    cd manim
    pip3 install -r requirements.txt
    python3 manim.py example_scenes.py SquareToCircle -pl
    ```

### Using `virtualenv` and `virtualenvwrapper`
After installing `virtualenv` and `virtualenvwrapper`
```sh
git clone https://github.com/3b1b/manim.git
mkvirtualenv -a manim -r requirements.txt manim
python3 -m manim example_scenes.py SquareToCircle -pl
```

### Using Docker
Since it's a bit tricky to get all the dependencies set up just right, there is a Dockerfile and Compose file provided in this repo as well as [a premade image on Docker Hub](https://hub.docker.com/r/eulertour/manim/tags/). The Dockerfile contains instructions on how to build a manim image, while the Compose file contains instructions on how to run the image.

The image does not contain a copy of the repo. This is intentional, as it allows you to either bind mount a repo that you've cloned locally or clone any fork/branch you want. In order to do this with the Compose file, you must set the `MANIM_PATH` environment variable to the absolute path to the manim repo.

1. [Install Docker](https://www.docker.com/products/overview)
2. [Install Docker Compose](https://docs.docker.com/compose/install/)
3. Render an animation
```sh
MANIM_PATH=/absolute/path/to/manim/repo docker-compose run manim example_scenes.py SquareToCircle -l
```
The first time you execute the above command, Docker will pull the image from Docker Hub and cache it. Any subsequent runs until the image is evicted will use the cached image.
Note that the image doesn't have any development tools installed and can't preview animations. Its purpose is building and testing only.

## Using manim
Try running the following:
```sh
python3 -m manim example_scenes.py SquareToCircle -pl
```
The -p is for previewing, meaning the video file will automatically open when it is done rendering.
Use -l for a faster rendering at a lower quality.
Use -s to skip to the end and just show the final frame.
Use -n (number) to skip ahead to the n'th animation of a scene.
Use -f to show the file in finder (for osx)

Set MEDIA_DIR environment variable to determine where image and animation files will be written.

Look through the old_projects folder to see the code for previous 3b1b videos.  Note, however, that developments are often made to the library without considering backwards compatibility on those old_projects.  To run them with a guarantee that they will work, you will have to go back to the commit which complete that project.

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
