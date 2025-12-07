<<<<<<< HEAD
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

Note, there are two versions of manim.  This repository began as a personal project by the author of [3Blue1Brown](https://www.3blue1brown.com/) for the purpose of animating those videos, with video-specific code available [here](https://github.com/3b1b/videos).  In 2020 a group of developers forked it into what is now the [community edition](https://github.com/ManimCommunity/manim/), with a goal of being more stable, better tested, quicker to respond to community contributions, and all around friendlier to get started with. See [this page](https://docs.manim.community/en/stable/faq/installation.html#different-versions) for more details.

## Installation
> [!Warning]
> **WARNING:** These instructions are for ManimGL _only_. Trying to use these instructions to install [Manim Community/manim](https://github.com/ManimCommunity/manim) or instructions there to install this version will cause problems. You should first decide which version you wish to install, then only follow the instructions for your desired version.

> [!Note]
> **Note**: To install manim directly through pip, please pay attention to the name of the installed package. This repository is ManimGL of 3b1b. The package name is `manimgl` instead of `manim` or `manimlib`. Please use `pip install manimgl` to install the version in this repository.

Manim runs on Python 3.7 or higher.

System requirements are [FFmpeg](https://ffmpeg.org/), [OpenGL](https://www.opengl.org/) and [LaTeX](https://www.latex-project.org) (optional, if you want to use LaTeX).
For Linux, [Pango](https://pango.org) along with its development headers are required. See instruction [here](https://github.com/ManimCommunity/ManimPango#building).


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
    ## Manim Example

    This folder contains a minimal Manim example in `Animation.py` and helper scripts to install dependencies and render scenes.

    ## Quick Setup (Arch/Manjaro)

    Run the automated install script:

    ```bash
    bash install.sh
    ```

    This will update your system, install FFmpeg and build tools, create a Python virtual environment, and install Manim and other Python dependencies.

    ## Manual Setup

    If you prefer manual installation:

    ```bash
    # Install system dependencies (Arch/Manjaro)
    sudo pacman -S --needed base-devel ffmpeg pkgconf python-pycairo mesa libxrandr libxinerama libxcursor libxi

    # Create and activate virtual environment
    python3.13 -m venv .venv
    source .venv/bin/activate

    # Install Python packages
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

    ## Rendering Animations

    ```bash
    # Render the JecklesTV lightning animation (low quality, fast)
    manim -pql Animation.py JecklesLightning

    # Render other scenes
    manim -pql Animation.py SimpleTransform
    manim -pql Animation.py TextWrite
    ```

    ### Quality Options

    - `-ql` = low quality (fast, for testing)
    - `-qm` = medium quality (balance)
    - `-qh` = high quality (slower, better output)

    ### Output Location

    Rendered videos are saved to:

    ```
    media/videos/Animation/480p15/  (low quality)
    media/videos/Animation/1080p60/ (high quality)
    ```

    ### Convert MP4 to GIF

    ```bash
    ffmpeg -i media/videos/Animation/480p15/JecklesLightning.mp4 \
      -vf "fps=15,scale=960:-1:flags=lanczos" \
      -loop 0 jeckles.gif
    ```

    For more details, see `install.sh` and `README.md` in this directory.
python -m venv .venv
