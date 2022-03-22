<p align="center">
    <a href="https://github.com/3b1b/manim">
        <img src="https://raw.githubusercontent.com/3b1b/manim/master/logo/cropped.png">
    </a>
</p>

[![pypi version](https://img.shields.io/pypi/v/manimgl?logo=pypi)](https://pypi.org/project/manimgl/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)
[![Manim Subreddit](https://img.shields.io/reddit/subreddit-subscribers/manim.svg?color=ff4301&label=reddit&logo=reddit)](https://www.reddit.com/r/manim/)
[![Manim Discord](https://img.shields.io/discord/581738731934056449.svg?label=discord&logo=discord)](https://discord.com/invite/bYCyhM9Kz2)
[![docs](https://github.com/3b1b/manim/workflows/docs/badge.svg)](https://3b1b.github.io/manim/)

Manim is an engine for precise programmatic animations, designed for creating explanatory math videos.

Note, there are two versions of manim.  This repository began as a personal project by the author of [3Blue1Brown](https://www.3blue1brown.com/) for the purpose of animating those videos, with video-specific code available [here](https://github.com/3b1b/videos).  In 2020 a group of developers forked it into what is now the [community edition](https://github.com/ManimCommunity/manim/), with a goal of being more stable, better tested, quicker to respond to community contributions, and all around friendlier to get started with. See [this page](https://docs.manim.community/en/stable/installation/versions.html?highlight=OpenGL#which-version-to-use) for more details.

## Installation
> **WARNING:** These instructions are for ManimGL _only_. Trying to use these instructions to install [ManimCommunity/manim](https://github.com/ManimCommunity/manim) or instructions there to install this version will cause problems. You should first decide which version you wish to install, then only follow the instructions for your desired version.
> 
> **Note**: To install manim directly through pip, please pay attention to the name of the installed package. This repository is ManimGL of 3b1b. The package name is `manimgl` instead of `manim` or `manimlib`. Please use `pip install manimgl` to install the version in this repository.

Manim runs on Python 3.7 or higher.

System requirements are [FFmpeg](https://ffmpeg.org/), [OpenGL](https://www.opengl.org/) and [LaTeX](https://www.latex-project.org) (optional, if you want to use LaTeX).
For Linux, [Pango](https://pango.gnome.org) along with its development headers are required. See instruction [here](https://github.com/ManimCommunity/ManimPango#building).


### Directly

```sh
# Install manimgl
pip install manimgl

# Try it out
manimgl
```

For more options, take a look at the [Using manim](#using-manim) sections further below.

If you want to hack on manimlib itself, clone this repository and in that directory execute:

```sh
# Install manimgl
pip install -e .

# Try it out
manimgl example_scenes.py OpeningManimExample
# or
manim-render example_scenes.py OpeningManimExample
```

### Directly (Windows)

1. [Install FFmpeg](https://www.wikihow.com/Install-FFmpeg-on-Windows).
2. Install a LaTeX distribution. [MiKTeX](https://miktex.org/download) is recommended.
3. Install the remaining Python packages.
    ```sh
    git clone https://github.com/3b1b/manim.git
    cd manim
    pip install -e .
    manimgl example_scenes.py OpeningManimExample
    ```

### Mac OSX

1. Install FFmpeg, LaTeX in terminal using homebrew.
    ```sh
    brew install ffmpeg mactex
    ```
   
2. Install latest version of manim using these command.
    ```sh
    git clone https://github.com/3b1b/manim.git
    cd manim
    pip install -e .
    manimgl example_scenes.py OpeningManimExample
    ```

## Anaconda Install

1. Install LaTeX as above.
2. Create a conda environment using `conda create -n manim python=3.8`.
3. Activate the environment using `conda activate manim`.
4. Install manimgl using `pip install -e .`.


## Using manim
Try running the following:
```sh
manimgl example_scenes.py OpeningManimExample
```
This should pop up a window playing a simple scene.

Some useful flags include:
* `-w` to write the scene to a file
* `-o` to write the scene to a file and open the result
* `-s` to skip to the end and just show the final frame.
    * `-so` will save the final frame to an image and show it
* `-n <number>` to skip ahead to the `n`'th animation of a scene.
* `-f` to make the playback window fullscreen

Take a look at custom_config.yml for further configuration.  To add your customization, you can either edit this file, or add another file by the same name "custom_config.yml" to whatever directory you are running manim from.  For example [this is the one](https://github.com/3b1b/videos/blob/master/custom_config.yml) for 3blue1brown videos.  There you can specify where videos should be output to, where manim should look for image files and sounds you want to read in, and other defaults regarding style and video quality.

Look through the [example scenes](https://3b1b.github.io/manim/getting_started/example_scenes.html) to get a sense of how it is used, and feel free to look through the code behind [3blue1brown videos](https://github.com/3b1b/videos) for a much larger set of example. Note, however, that developments are often made to the library without considering backwards compatibility with those old videos. To run an old project with a guarantee that it will work, you will have to go back to the commit which completed that project.

### Documentation
Documentation is in progress at [3b1b.github.io/manim](https://3b1b.github.io/manim/). And there is also a Chinese version maintained by [**@manim-kindergarten**](https://manim.org.cn): [docs.manim.org.cn](https://docs.manim.org.cn/) (in Chinese).

[manim-kindergarten](https://github.com/manim-kindergarten/) wrote and collected some useful extra classes and some codes of videos in [manim_sandbox repo](https://github.com/manim-kindergarten/manim_sandbox).


## Contributing
Is always welcome.  As mentioned above, the [community edition](https://github.com/ManimCommunity/manim) has the most active ecosystem for contributions, with testing and continuous integration, but pull requests are welcome here too.  Please explain the motivation for a given change and examples of its effect.


## License
This project falls under the MIT license.
