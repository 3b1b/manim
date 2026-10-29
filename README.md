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

This repository is **ManimGL**, distributed as `manimgl` and imported as
`manimlib`. [Manim Community](https://github.com/ManimCommunity/manim/) is a
separate project with different commands and examples.

### System dependencies

Install [FFmpeg](https://ffmpeg.org/) and the native libraries needed for text
rendering. A compatible GPU and graphics drivers are needed to render scenes.

On macOS:

```sh
brew install ffmpeg cairo pango pkg-config
```

On Ubuntu/Debian:

```sh
sudo apt update
sudo apt install ffmpeg libpango1.0-dev pkg-config
```

On Windows, install FFmpeg using its [download instructions](https://ffmpeg.org/download.html)
and make sure it is on `PATH`.

[LaTeX](https://www.latex-project.org/) and `dvisvgm` are also needed for scenes
that contain `Tex` or `TexText`. On macOS, use [MacTeX or BasicTeX](https://www.tug.org/mactex/).
On Ubuntu/Debian, install `texlive-science`, `texlive-fonts-extra`, and
`texlive-latex-extra`. On Windows, [MiKTeX](https://miktex.org/download) is an option.

### Set up the project with uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then clone
this repository and create its locked environment:

```sh
git clone https://github.com/3b1b/manim.git
cd manim
uv sync --locked
uv run --locked manimgl --version
uv run --locked manimgl example_scenes.py OpeningManimExample
```

uv manages the repository's `.venv` and installs this checkout in editable mode.
It selects Python 3.12 from `.python-version`, downloading it when necessary.
The package itself continues to support Python 3.10 and newer. Python dependencies
are declared in `pyproject.toml` and resolved in the committed `uv.lock`; FFmpeg,
LaTeX, and native libraries are installed separately as described above.

To render a video without opening the preview window:

```sh
uv run --locked manimgl example_scenes.py OpeningManimExample -w -l
```

The equivalent `manim-render` entry point is available through `uv run --locked`
as well.

## Development with uv

Source edits are available immediately through the editable installation. Run
the unit tests with:

```sh
uv run --locked pytest
```

Declare dependency changes with `uv add` (or `uv add --dev` for development tools)
and commit both `pyproject.toml` and `uv.lock`. Use `uv lock --upgrade` to explicitly
update locked dependencies. `uv sync --locked` checks that the lockfile agrees
with the project metadata and is also used in CI.

Build the source distribution and wheel with:

```sh
uv build
```

The project retains the setuptools build backend and standard Python packaging
metadata, so uv is a development workflow rather than a runtime dependency.

To build the documentation with only its dependency group:

```sh
uv sync --locked --only-group docs
uv run --locked --only-group docs sphinx-build -M html docs/source docs/build
```

The documentation group does not require ManimGL or its native rendering
dependencies. A subsequent `uv sync --locked` restores the development environment.

## Using manim
Try running the following:
```sh
uv run --locked manimgl example_scenes.py OpeningManimExample
```
This should pop up a window playing a simple scene.

Look through the [example scenes](https://3b1b.github.io/manim/getting_started/example_scenes.html) to see examples of the library's syntax, animation types and object types. In the [3b1b/videos](https://github.com/3b1b/videos) repo, you can see all the code for 3blue1brown videos, though code from older videos may not be compatible with the most recent version of manim. The readme of that repo also outlines some details for how to set up a more interactive workflow, as shown in [this manim demo video](https://www.youtube.com/watch?v=rbu7Zu5X1zI) for example.

When running in the CLI, some useful flags include:
* `-w` to write the scene to a file
* `-o` to write the scene to a file and open the result
* `-s` to skip to the end and just show the final frame.
    * `-so` will save the final frame to an image and show it
* `-n <number>` to skip ahead to the `n`'th animation of a scene.
* `-f` to make the playback window fullscreen

Take a look at custom_config.yml for further configuration.  To add your customization, you can either edit this file, or add another file by the same name "custom_config.yml" to whatever directory you are running manim from.  For example [this is the one](https://github.com/3b1b/videos/blob/master/custom_config.yml) for 3blue1brown videos.  There you can specify where videos should be output to, where manim should look for image files and sounds you want to read in, and other defaults regarding style and video quality.

### Documentation
Documentation is in progress at [3b1b.github.io/manim](https://3b1b.github.io/manim/). And there is also a Chinese version maintained by [**@manim-kindergarten**](https://manim.org.cn): [docs.manim.org.cn](https://docs.manim.org.cn/) (in Chinese).

[manim-kindergarten](https://github.com/manim-kindergarten/) wrote and collected some useful extra classes and some codes of videos in [manim_sandbox repo](https://github.com/manim-kindergarten/manim_sandbox).


## Contributing
Is always welcome.  As mentioned above, the [community edition](https://github.com/ManimCommunity/manim) has the most active ecosystem for contributions, with testing and continuous integration, but pull requests are welcome here too.  Please explain the motivation for a given change and examples of its effect.


## License
This project falls under the MIT license.
