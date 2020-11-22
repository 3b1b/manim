<p align="center">
    <a href="https://www.manim.community/"><img src="https://raw.githubusercontent.com/ManimCommunity/manim/master/logo/cropped.png"></a>
    <br />
    <br />
    <a href="http://choosealicense.com/licenses/mit/"><img src="https://img.shields.io/badge/license-MIT-red.svg?style=flat" alt="MIT License"></a>
    <a href="https://www.reddit.com/r/manim/"><img src="https://img.shields.io/reddit/subreddit-subscribers/manim.svg?color=orange&label=reddit" alt="Reddit" href=></a>
    <a href="https://discord.gg/mMRrZQW"><img src="https://img.shields.io/discord/581738731934056449.svg?label=discord&color=yellow" alt="Discord"></a>
    <a href="https://manimce.readthedocs.io/en/latest/"><img src="https://readthedocs.org/projects/manimce/badge/?version=latest" alt="Documentation Status"></a>
    <a href="https://hub.docker.com/r/manimcommunity/manim"><img src="https://img.shields.io/docker/v/manimcommunity/manim?color=%23099cec&label=docker%20image" alt="Docker image"> </a>
    <img src="https://github.com/ManimCommunity/manim/workflows/CI/badge.svg" alt="CI">
    <br />
    <br />
    <i>An animation engine for explanatory math videos</i>
</p>

<hr />

`manim` is an animation engine for explanatory math videos. It's used to create precise animations programmatically, as demonstrated in the videos of [3Blue1Brown](https://www.3blue1brown.com/).

> NOTE: This repository is maintained by the Manim Community, and is not associated with Grant Sanderson or 3Blue1Brown in any way (although we are definitely indebted to him for providing his work to the world). If you would like to study how Grant makes his videos, head over to his repository ([3b1b/manim](https://github.com/3b1b/manim)). This fork is updated more frequently than his, and it's recommended to use this fork if you'd like to use Manim for your own projects.

## Table of Contents:

-  [Installation](#installation)
-  [Usage](#usage)
-  [Documentation](#documentation)
-  [Help with Manim](#help-with-manim)
-  [Contributing](#contributing)
-  [License](#license)

## Installation

Manim requires a few dependencies that must be installed prior to using it. Please visit the [documentation](https://manimce.readthedocs.io/en/latest/installation.html) and follow the appropriate instructions for your operating system.

Once the dependencies have been installed, run the following in a terminal window:

```bash
pip install manimce
```

## Usage

Manim is an extremely versatile package. The following is an example `Scene` you can construct:

```python
from manim import *

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)

        self.play(ShowCreation(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))
```

In order to view the output of this scene, save the code in a file called `example.py`. Then, run the following in a terminal window:

```sh
manim example.py SquareToCircle -p -ql
```

You should see your native video player program pop up and play a simple scene in which a square is transformed into a circle. You may find some more simple examples within this
[GitHub repository](master/example_scenes). You can also visit the [official gallery](https://manimce.readthedocs.io/en/latest/examples.html) for more advanced examples.

## Command line arguments

The general usage of manim is as follows:

![manim-illustration](https://raw.githubusercontent.com/ManimCommunity/manim/master/docs/source/_static/command.png)

The `-p` flag in the command above is for previewing, meaning the video file will automatically open when it is done rendering. The `-ql` flag is for a faster rendering at a lower quality.

Some other useful flags include:

-  `-s` to skip to the end and just show the final frame.
-  `-n <number>` to skip ahead to the `n`'th animation of a scene.
-  `-f` show the file in the file browser.

For a thorough list of command line arguments, visit the [documentation](https://manimce.readthedocs.io/en/latest/tutorials/configuration.html).

## Documentation

Documentation is in progress at [ReadTheDocs](https://manimce.readthedocs.io/en/latest/).

## Help with Manim

If you need help installing or using Manim, feel free to reach out to our [Discord
Server](https://discord.gg/mMRrZQW) or [Reddit Community](https://www.reddit.com/r/manim). If you would like to submit bug report or feature request, please open an issue.

## Contributing

Contributions to `manim` are always welcome. In particular, there is a dire need for tests and documentation. For contribution guidelines, please see the [documentation](https://manimce.readthedocs.io/en/latest/contributing.html).

This project uses [Poetry](https://python-poetry.org/docs/) for management. You must have poetry installed and available in your environment. You can learn more `poetry` and how to use it at its [Documentation](https://manimce.readthedocs.io/en/latest/installation/for_dev.html).

## License

The software is double-licensed under the MIT license, with copyright by 3blue1brown LLC (see LICENSE), and copyright by Manim Community Developers (see LICENSE.community).
