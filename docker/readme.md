# Quick reference
- **Maintained by:** [the Manim Community developers](https://github.com/ManimCommunity/manim)
- **Getting help:** [Manim Documentation](https://docs.manim.community) and [further helpful resources](https://manim.community)

# Supported tags
- `v0.1.0`, `latest` -- the latest released version
- `stable` -- a more recent version corresponding to [the stable branch](https://github.com/ManimCommunity/manim/tree/stable)
- `experimental` -- the most recent version corresponding to [the master branch](https://github.com/ManimCommunity/manim)

# What is Manim?
![logo](https://raw.githubusercontent.com/ManimCommunity/manim/master/logo/cropped.png)

Manim is a Python library for creating mathematical animations [originally created](https://github.com/3b1b/manim) by Grant "3Blue1Brown" Sanderson. The images in this repository correspond to the [community-maintained version of Manim](https://github.com/ManimCommunity/manim).

To get an impression what Manim can be used for, have a look at our [Example Gallery](https://docs.manim.community/en/stable/examples.html).

# How to use this image
## Quick Example
To render a scene `CircleToSquare` in a file `test_scenes.py` contained in your current working directory while preserving your user and group ID, use
```
$ docker run --rm -it  --user="$(id -u):$(id -g)" -v "$(pwd)":/manim manimcommunity/manim manim test_scenes.py CircleToSquare -qm
```

## Running the image in the background
Instead of using the "throwaway container" approach sketched above, you can also create a named container that you can also modify to your liking. First, run
```
$ docker run -it --name my-manim-container -v "$(pwd):/manim" manimcommunity/manim /bin/bash
```
to obtain an interactive shell inside your container allowing you to, e.g., install further dependencies (like texlive packages using `tlmgr`). Exit the container as soon as you are satisfied. Then, before using it, start the container by running
```
$ docker start my-manim-container
```
Then, to render a scene `CircleToSquare` in a file `test_scenes.py`, call
```
$ docker exec -it --user="$(id -u):$(id -g)" my-manim-container manim test.py CircleToSquare -qm
```

# Important notes
When executing `manim` within a Docker container, several command line flags (in particular `-p` (preview file) and `-f` (show output file in the file browser)) are not supported.

# Building the image
The docker image corresponding to the checked out version of the git repository
can be built by running
```
docker build -t manimcommunity/manim:TAG -f docker/Dockerfile .
```
from the root directory of the repository.