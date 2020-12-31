![logo](logo/cropped.png)

[![Build Status](https://travis-ci.org/3b1b/manim.svg?branch=master)](https://travis-ci.org/3b1b/manim)
[![Documentation](https://img.shields.io/badge/docs-EulerTour-blue.svg)](https://www.eulertour.com/learn/manim/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)
[![Manim Subreddit](https://img.shields.io/reddit/subreddit-subscribers/manim.svg?color=ff4301&label=reddit)](https://www.reddit.com/r/manim/)
[![Manim Discord](https://img.shields.io/discord/581738731934056449.svg?label=discord)](https://discord.gg/mMRrZQW)

Manim is an animation engine for explanatory math videos. It's used to create precise animations programmatically, as seen in the videos at [3Blue1Brown](https://www.3blue1brown.com/).

This repository contains the version of manim used by 3Blue1Brown.  There is also a community maintained version at https://github.com/ManimCommunity/manim/. To get help or to join the development effort, please join the discord.

## Installation
Manim runs on Python 3.8.

System requirements are [FFmpeg](https://ffmpeg.org/), [OpenGL](https://www.opengl.org//) and [latex](https://www.latex-project.org) (optional, if you want to use LaTeX).

For more options, take a look at the [Using manim](#using-manim) sections further below.

### Directly

If you want to hack on manimlib itself, clone this repository and in that directory execute:

```sh
# Install python requirements
python3 -m pip install -r requirements.txt

# Try it out
python3 ./manim.py example_scenes.py SquareToCircle
```

### Directly (Windows)
1. [Install FFmpeg](https://www.wikihow.com/Install-FFmpeg-on-Windows).
2. Install a LaTeX distribution. [MiKTeX](https://miktex.org/download) is recommended.
3. Install the remaining Python packages.
    ```sh
    git clone https://github.com/3b1b/manim.git
    cd manim
    pip3 install -r requirements.txt
    python3 manim.py example_scenes.py SquareToCircle
    ```


## Anaconda Install

* Install latex as above. 
* Create a conda environment using `conda env create -f environment.yml`
* **WINDOWS ONLY** Install `pyreadline` via `pip install pyreadline`. 


### Using `virtualenv` and `virtualenvwrapper`
After installing `virtualenv` and `virtualenvwrapper`
```sh
git clone https://github.com/3b1b/manim.git
mkvirtualenv -a manim -r requirements.txt manim
python3 -m manim example_scenes.py SquareToCircle
```

### Using Docker
Since it's a bit tricky to get all the dependencies set up just right, there is a Dockerfile and Compose file provided in this repo as well as [a premade image on Docker Hub](https://hub.docker.com/r/eulertour/manim/tags/). The Dockerfile contains instructions on how to build a manim image, while the Compose file contains instructions on how to run the image.

The prebuilt container image has manim repository included.
`INPUT_PATH` is where the container looks for scene files. You must set the `INPUT_PATH`
environment variable to the absolute path containing your scene file and the
`OUTPUT_PATH` environment variable to the directory where you want media to be written.

1. [Install Docker](https://docs.docker.com)
2. [Install Docker Compose](https://docs.docker.com/compose/install/)
3. Render an animation:
```sh
INPUT_PATH=/path/to/dir/containing/source/code \
OUTPUT_PATH=/path/to/output/ \
docker-compose run manim example_scenes.py SquareToCircle -l
```
The command needs to be run as root if your username is not in the docker group.

You can replace `example.scenes.py` with any relative path from your `INPUT_PATH`.

![docker diagram](./manim_docker_diagram.png)

After running the output will say files ready at `/tmp/output/`, which refers to path inside the container. Your `OUTPUT_PATH` is bind mounted to this `/tmp/output` so any changes made by the container to `/tmp/output` will be mirrored on your `OUTPUT_PATH`. `/media/` will be created in `OUTPUT_PATH`.

`-p` won't work as manim would look for video player in the container system, which it does not have.

The first time you execute the above command, Docker will pull the image from Docker Hub and cache it. Any subsequent runs until the image is evicted will use the cached image.
Note that the image doesn't have any development tools installed and can't preview animations. Its purpose is building and testing only.

## Using manim
Try running the following:
```sh
python3 -m manim example_scenes.py SquareToCircle
```
This should pop up a window playing a simple scene.

Some useful flags include:
* `-w` to write the scene to a file
* `-o` to write the scene to a file and open the result
* `-s` to skip to the end and just show the final frame.
* `-n <number>` to skip ahead to the `n`'th animation of a scene.
* `-f` to show the file in finder (for OSX).

Set `MEDIA_DIR` environment variable to specify where the image and animation files will be written.

Look through [https://github.com/3b1b/videos](https://github.com/3b1b/videos) to see the code for previous 3b1b videos. Note, however, that developments are often made to the library without considering backwards compatibility with those old projects. To run an old project with a guarantee that it will work, you will have to go back to the commit which completed that project.

### Documentation
Documentation is in progress at [eulertour.com/learn/manim](https://www.eulertour.com/learn/manim/).

### Walkthrough
Todd Zimmerman put together a [tutorial](https://talkingphysics.wordpress.com/2019/01/08/getting-started-animating-with-manim-and-python-3-7/) on getting started with manim, which has been updated to run on Python 3.7.


## Contributing
Is always welcome. In particular, there is a dire need for tests and documentation.


## License
This project falls under the MIT license.
