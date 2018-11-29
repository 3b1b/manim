# Manim - Mathematical Animation Engine
[![Documentation Status](https://readthedocs.org/projects/manim/badge/?version=latest)](https://manim.readthedocs.io/en/latest/?badge=latest)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)

Manim is an animation engine for explanatory math videos. It's used to create precise animations programmatically.

## Installation
Manim runs on python 3.7. You can install the python requirements with
`pip install -r requirements.txt`. System requirements are
[cairo](https://www.cairographics.org), [latex](https://www.latex-project.org),
[ffmpeg](https://www.ffmpeg.org), and [sox](http://sox.sourceforge.net).

### Directly
```sh
git clone https://github.com/3b1b/manim.git
cd manim
pip install -r requirements.txt
mkdir media
echo "media" > media_dir.txt
python3 extract_scene.py example_scenes.py SquareToCircle -pl
```

### Using `virtualenv` and `virtualenvwrapper`
After installing `virtualenv` and `virtualenvwrapper`
```sh
git clone https://github.com/3b1b/manim.git
mkvirtualenv -a manim -r requirements.txt manim
mkdir media
echo "media" > media_dir.txt
python3 extract_scene.py example_scenes.py SquareToCircle -pl
```

### Using Docker
Since it's a bit tricky to get all the dependencies set up just right, there is a Dockerfile provided in this repo as well as [a premade image on Docker Hub](https://hub.docker.com/r/eulertour/manim/tags/).

The image does not contain a copy of the repo. This is intentional, as it allows you to either bind mount a repo that you've cloned locally or clone any fork/branch you want. Since test coverage is painfully lacking, the image may not have dependencies for all of manim.

1. [Install Docker](https://www.docker.com/products/overview)
2. Get the docker image
  * Pull it (recommended): `docker pull eulertour/manim:latest`, or
  * Build it: `docker build -t manim .`
3. Start the image
  * Bind mount a local repo (recommended): `docker run -itv /absolute/path/to/your/local/manim/repo:/root/manim eulertour/manim` or
  * Clone a remote repo: `docker run -it eulertour/manim`, then `git clone https://github.com/eulertour/manim.git`
4. Render an animation
```
cd manim
mkdir media
echo "media" > media_dir.txt
python3 extract_scene.py example_scenes.py SquareToCircle -l
```
Note that the image doesn't have any development tools installed and can't preview animations. Its purpose is building and testing only.

## Using manim
Try running the following:
```sh
python3 extract_scene.py example_scenes.py SquareToCircle -pl
```
The -p is for previewing, meaning the the video file will automatically open when it is done rendering.
Use -l for a faster rendering at a lower quality.
Use -s to skip to the end and just show the final frame.
Use -n (number) to skip ahead to the n'th animation of a scene.
Use -f to show the file in finder (for osx)

Set MEDIA_DIR environment variable to determine where image and animation files will be written.

Look through the old_projects folder to see the code for previous 3b1b videos.  Note, however, that developments are often made to the library without considering backwards compatibility on those old_projects.  To run them with a guarantee that they will work, you will have to go back to the commit which complete that project.

While developing a scene, the `-s` flag is helpful to just see what things look like at the end without having to generate the full animation.  It can also be helpful to use the `-n` flag to skip over some number of animations.

### Documentation
Documentation is in progress at [manim.readthedocs.io](https://manim.readthedocs.io).

### (Outdated) Walkthrough
Todd Zimmerman put together a [tutorial](https://talkingphysics.wordpress.com/2018/06/11/learning-how-to-animate-videos-using-manim-series-a-journey/) on getting started with manim, but it uses an outdated version that runs on python 2.7. It may not be fully compatible with the current version of manim, but it does a good job laying out the basics.

### Live Streaming
To live stream your animations, simply assign `IS_LIVE_STREAMING = True` in `constants.py` file and from your Python Interactive Shell (`python3`) import the stream starter with `from stream_starter import *` while under the project directory. This will provide a clean interactive shell to enter your commands. `manim` object is a `Manim()` instance so as soon as you play an animation with `manim.play()` your stream will start. A video player will pop-up and you can broadcast that video using [OBS Studio](https://obsproject.com/) which is the most practical way of streaming with this math animation library. An example:

```
>>> from stream_starter import *
YOUR STREAM IS READY!
>>> circle = Circle()
>>> manim.play(ShowCreation(circle))
Animation 0: ShowCreationCircle: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 60/60 [00:01<00:00, 37.30it/s]
<scene.scene.Scene object at 0x7f0756d5a8d0>
```

It is also possible to stream directly to Twitch. To do that simply assign `IS_STREAMING_TO_TWITCH = True` in `constants.py` file and put your Twitch Stream Key to `TWITCH_STREAM_KEY = "YOUR_STREAM_KEY"` and when you follow the above example the stream will directly start on your Twitch channel(with no audio support).


## Contributing
Is always welcome. In particular, there is a dire need for tests and documentation.


## License
All files in the directories active_projects and old_projects, which by and large generate the visuals for 3b1b videos, are copyright 3Blue1Brown.

The general purpose animation code found in the remainder of the repository, on the other hand, is under the MIT license.
