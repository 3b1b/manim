![logo](https://raw.githubusercontent.com/ManimCommunity/manim/master/logo/banner.svg)

![CI](https://github.com/ManimCommunity/manim/workflows/CI/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/manimce/badge/?version=latest)](https://manimce.readthedocs.io/en/latest/?badge=latest)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)
[![Manim Subreddit](https://img.shields.io/reddit/subreddit-subscribers/manim.svg?color=ff4301&label=reddit)](https://www.reddit.com/r/manim/)
[![Manim Discord](https://img.shields.io/discord/581738731934056449.svg?label=discord)](https://discord.gg/mMRrZQW)

Manim is an animation engine for explanatory math videos. It's used to create precise animations programmatically, as seen in the videos at [3Blue1Brown](https://www.3blue1brown.com/).

> NOTE: This repository is maintained by the Manim Community, and is not associated with Grant Sanderson or 3Blue1Brown in any way (though we are definitely indebted to him for providing his work to the world). If you want to study how Grant makes his videos, head over to his repository (3b1b/manim). This is a more frequently updated repository than that one, and is recommended if you want to use Manim for your own projects.

## Table of Contents:

- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Help with Manim](#help-with-manim)
- [Contributing](#contributing)
- [License](#license)

## Installation

Manim has a few dependencies that need to be installed before it. Please visit
the
[documentation](https://manimce.readthedocs.io/en/latest/installation.html)
and follow the instructions according to your operating system.

## Usage

Here is an example manim script:

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

Save this code in a file called `example.py`. Now open your terminal in the
folder where you saved the file and execute

```sh
manim example.py SquareToCircle -pl
```

You should see your video player pop up and play a simple scene where a square
is transformed into a circle. You can find some more simple examples in the
[GitHub repository](https://github.com/ManimCommunity/manim/tree/master/example_scenes).
Visit the [official gallery](https://manimce.readthedocs.io/en/latest/examples.html) for more advanced examples.

## Command line arguments

The general usage of manim is as follows:

![manim-illustration](https://raw.githubusercontent.com/ManimCommunity/manim/master/readme-assets/command.png)

The `-p` flag in the command above is for previewing, meaning the video file will automatically open when it is done rendering. The `-l` flag is for a faster rendering at a lower quality.

Some other useful flags include:

- `-s` to skip to the end and just show the final frame.
- `-n <number>` to skip ahead to the `n`'th animation of a scene.
- `-f` show the file in the file browser.

For a thorough list of command line arguments, visit the
[documentation](https://manimce.readthedocs.io/en/latest/tutorials/configuration.html).

## Documentation

Documentation is in progress at [ReadTheDocs](https://manimce.readthedocs.io/en/latest/).

## Help with Manim

If you need help installing or using Manim, please take a look at [the Reddit
Community](https://www.reddit.com/r/manim) or the [Discord
Community](https://discord.gg/mMRrZQW). For bug reports and feature requests,
please open an issue.

## Contributing

Is always welcome. In particular, there is a dire need for tests and
documentation. For guidelines please see the
[documentation](https://manimce.readthedocs.io/en/latest/contributing.html).
This project uses [Poetry](https://python-poetry.org/docs/) for management. You need to have poetry installed and available in your environment.
You can find more information about it in its [Documentation](https://manimce.readthedocs.io/en/latest/installation/for_dev.html)

## License

The software is double-licensed under the MIT license, with copyright
by 3blue1brown LLC (see LICENSE), and copyright by Manim Community
Developers (see LICENSE.community).
