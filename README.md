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

Manim runs on Python 3.10 or higher (3.12+ recommended).

System requirements are [FFmpeg](https://ffmpeg.org/), [OpenGL](https://www.opengl.org/) and [LaTeX](https://www.latex-project.org) (optional, if you want to use LaTeX).
For Linux, [Pango](https://pango.org) along with its development headers are required. See instruction [here](https://github.com/ManimCommunity/ManimPango#building).

### Using uv (recommended)

This project uses [uv](https://docs.astral.sh/uv/) for environment and dependency management.

```sh
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and sync
git clone https://github.com/3b1b/manim.git
cd manim
uv sync

# Try it out
uv run manimgl example_scenes.py OpeningManimExample
# or
uv run manim-render example_scenes.py OpeningManimExample
```

### Using pip

```sh
# Install manimgl from PyPI
pip install manimgl

# Try it out
manimgl
```

If you want to hack on manimlib itself, clone this repository and install in editable mode:

```sh
git clone https://github.com/3b1b/manim.git
cd manim
pip install -e .
manimgl example_scenes.py OpeningManimExample
```

### Platform-specific notes

**Windows:**
1. [Install FFmpeg](https://www.wikihow.com/Install-FFmpeg-on-Windows).
2. Install a LaTeX distribution. [MiKTeX](https://miktex.org/download) is recommended.
3. Clone and install as above.

**Mac OSX:**
1. Install FFmpeg and LaTeX via homebrew:
    ```sh
    brew install ffmpeg mactex
    ```
    <details>
      <summary>💡 An alternative to heavyweight MacTeX bundle.</summary>

      > To avoid installing the full MacTeX bundle, which is ~6GB, you can alternatively install the
      > lightweight [BasicTeX](https://formulae.brew.sh/cask/basictex) and then gradually add
      > only the LaTeX packages you actually need. A list of packages sufficient to run examples can
      > be found [here](https://github.com/3b1b/manim/issues/2133#issuecomment-2414547866).
      > For an overview of the MacTeX installer bundles, see https://www.tug.org/mactex/.
    </details>

2. If you are using an ARM-based processor, install Cairo:
    ```sh
    arch -arm64 brew install pkg-config cairo
    ```

3. Clone and install as above.

**Linux:**
Install Pango development headers (required for `manimpango`):
```sh
sudo apt-get install libpango1.0-dev  # Debian/Ubuntu
```

## Using manim
Try running the following:
```sh
manimgl example_scenes.py OpeningManimExample
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

## MCP Server

This repository includes an [MCP](https://modelcontextprotocol.io/) (Model Context Protocol) server that exposes ManimGL's functionality to LLMs. This lets AI assistants generate and render animations, inspect available objects and animations, and validate scene code.

### Setup

```sh
uv sync --extra mcp
uv run manimgl-mcp
```

### Tools

| Tool | Description |
|---|---|
| `render` | Render a scene to mp4, gif, or png from Python code |
| `preview` | Capture a single frame as base64 PNG for quick feedback |
| `validate` | Check scene code for syntax/import errors without rendering |
| `list_mobjects` | List available mathematical object classes with signatures |
| `list_animations` | List available animation classes with signatures |
| `get_example` | Get working example code for common patterns |

### Client configuration

To use the MCP server with an LLM client (Claude Desktop, Kiro, etc.), add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "manimgl": {
      "command": "uv",
      "args": ["run", "--extra", "mcp", "manimgl-mcp"],
      "cwd": "/path/to/this/repo"
    }
  }
}
```

## Documentation
Documentation is in progress at [3b1b.github.io/manim](https://3b1b.github.io/manim/). And there is also a Chinese version maintained by [**@manim-kindergarten**](https://manim.org.cn): [docs.manim.org.cn](https://docs.manim.org.cn/) (in Chinese).

[manim-kindergarten](https://github.com/manim-kindergarten/) wrote and collected some useful extra classes and some codes of videos in [manim_sandbox repo](https://github.com/manim-kindergarten/manim_sandbox).


## Contributing
Is always welcome.  As mentioned above, the [community edition](https://github.com/ManimCommunity/manim) has the most active ecosystem for contributions, with testing and continuous integration, but pull requests are welcome here too.  Please explain the motivation for a given change and examples of its effect.


## License
This project falls under the MIT license.
