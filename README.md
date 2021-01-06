![logo](logo/cropped.png)

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
pip3 install -r requirements.txt

# Try it out
python3 -m manim example_scenes.py OpeningManimExample
```

### Directly (Windows)
1. [Install FFmpeg](https://www.wikihow.com/Install-FFmpeg-on-Windows).
2. Install a LaTeX distribution. [MiKTeX](https://miktex.org/download) is recommended.
3. Install the remaining Python packages.
    ```sh
    git clone https://github.com/3b1b/manim.git
    cd manim
    pip3 install -r requirements.txt
    python3 manim.py example_scenes.py OpeningManimExample
    ```


## Anaconda Install

* Install latex as above.
* Create a conda environment using `conda env create -f environment.yml`


### Using `virtualenv` and `virtualenvwrapper`
After installing `virtualenv` and `virtualenvwrapper`
```sh
git clone https://github.com/3b1b/manim.git
mkvirtualenv -a manim -r requirements.txt manim
python3 -m manim example_scenes.py OpeningManimExample
```


## Using manim
Try running the following:
```sh
python3 -m manim example_scenes.py OpeningManimExample
```
This should pop up a window playing a simple scene.

Some useful flags include:
* `-w` to write the scene to a file
* `-o` to write the scene to a file and open the result
* `-s` to skip to the end and just show the final frame.
    * `-so` will asve the final frame to an image and show it
* `-n <number>` to skip ahead to the `n`'th animation of a scene.
* `-f` to make the playback window fullscreen

Take a look at custom_defaults.yml for further configuration.  For example, there you can specify where videos should be output to, where manim should look for image files and sounds you want to read in, and other defaults regarding style and video quality.  If you have a file name "custom_defaults.yml" in the same directory where you are calling manim, it will look to the configuration of that file instead of the one in manim itself.

Look through [https://github.com/3b1b/videos](https://github.com/3b1b/videos) to see the code for previous 3b1b videos. Note, however, that developments are often made to the library without considering backwards compatibility with those old projects. To run an old project with a guarantee that it will work, you will have to go back to the commit which completed that project.

### Documentation
Documentation is in progress at [eulertour.com/docs](https://www.eulertour.com/docs/). And there is also an all-in-one documentation and tutorials maintained by **@manim-kindergarten**: [manim.ml](https://manim.ml/) (in Chinese).

### Walkthrough
Todd Zimmerman put together a [tutorial](https://talkingphysics.wordpress.com/2019/01/08/getting-started-animating-with-manim-and-python-3-7/) on getting started with manim, which has been updated to run on Python 3.7.

[manim-kindergarten](https://github.com/manim-kindergarten/) wrote and collected some useful extra classes and some codes of videos in [manim_sandbox repo](https://github.com/manim-kindergarten/manim_sandbox).


## Contributing
Is always welcome. In particular, there is a dire need for tests and documentation.


## License
This project falls under the MIT license.
