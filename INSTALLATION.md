# General Installation
Manim runs on python 3.7. You can install it from PyPI via pip

```sh
pip3 install manimlib
```

System requirements are [cairo](https://www.cairographics.org), [ffmpeg](https://www.ffmpeg.org), [sox](http://sox.sourceforge.net) (optional, if you want to work with audio), [latex](https://www.latex-project.org) (optional, if you want to write text and equations).

You can now use it via the `manim` command. For example:

```sh
manim my_project.py MyScene
```

For more options, take a look at the “Using manim“ sections in the README.

## Unix (macOS & Linux)

If you want to hack on manimlib itself, clone this repository and in that directory execute:

```sh
# Install python requirements
python3 -m pip install -r requirements.txt

# Try it out
python3 ./manim.py example_scenes.py SquareToCircle -pl
```

## Windows
NOTE: If you have any Python versions other than 3.x, use ``python3`` and ``pip3`` in all the commands below.

1. [Install FFmpeg](https://www.wikihow.com/Install-FFmpeg-on-Windows).
2. Install Cairo. Download the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo. For most users, ``pycairo‑1.18.0‑cp37‑cp37m‑win32.whl`` will do fine.
    ```sh
    pip install C:\path\to\wheel\pycairo‑1.18.0‑cp37‑cp37m‑win32.whl
    ```
3. Install a LaTeX distribution. [MiKTeX](https://miktex.org/download) is recommended.

4. [Install SoX](https://sourceforge.net/projects/sox/files/sox/).

5. Install the remaining Python packages.
    ```sh
    git clone https://github.com/3b1b/manim.git
    cd manim
    pip install -r requirements.txt
    python manim.py example_scenes.py SquareToCircle -pl
    ```

## Install with Anaconda

* Install sox and latex as above. 
* Create a conda environment using `conda env create -f environment.yml`
* If installing on Windows, install `pyreadline` via `pip install pyreadline`. 


# Installing in Virtual Environments
## Using `virtualenv` and `virtualenvwrapper`
After installing `virtualenv` and `virtualenvwrapper`
```sh
git clone https://github.com/3b1b/manim.git
mkvirtualenv -a manim -r requirements.txt manim
python3 -m manim example_scenes.py SquareToCircle -pl
```

## Using Docker
Since it's a bit tricky to get all the dependencies set up just right, there is a Dockerfile and Compose file provided in this repo as well as [a premade image on Docker Hub](https://hub.docker.com/r/eulertour/manim/tags/). The Dockerfile contains instructions on how to build a manim image, while the Compose file contains instructions on how to run the image.

In order to do this with the Compose file, you must set the `INPUT_PATH`
environment variable to the directory containing your source code and the
`OUTPUT_DIRECTORY` environment variable to the directory where you want media
to be written.

1. [Install Docker](https://docs.docker.com)
2. [Install Docker Compose](https://docs.docker.com/compose/install/)
3. Render an animation
```sh
INPUT_PATH=/path/to/dir/containing/source/code \
OUTPUT_PATH=/path/to/dir/for/media \
docker-compose run manim example_scenes.py SquareToCircle -l
```
The first time you execute the above command, Docker will pull the image from Docker Hub and cache it. Any subsequent runs until the image is evicted will use the cached image.
Note that the image doesn't have any development tools installed and can't preview animations. Its purpose is building and testing only.
