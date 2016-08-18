# animations
Animation engine for explanatory math videos

For those who want to play around with this tool, I should
be upfront that I've mostly had my own use cases (i.e. 3b1b videos)
in mind while building it, and it might not be the most friendly thing 
to get up and running.  In particular, I have not done a great job
tracking requirements, and documentation is..well..sparse.

## Install requirements
```sh
pip install -r requirements.txt
```

Requirements to be installed outside of pip:
aggdraw
ffmpeg
latex

Here are directions that should work on any 64 bit platform (tested on osx
10.11.4)

This doesn't install freetype, but I don't think its required for this project

```
cd $TMPDIR
git clone https://github.com/scottopell/aggdraw-64bits
cd aggdraw-64bits
/usr/local/bin/python setup.py build_ext -i
/usr/local/bin/python setup.py install
```

## How to Use
Try running the following:

python extract_scene.py -p example_scenes.py SquareToCircle

-p gives a preview of an animation, -w will write it to a file, and -s will show/save the final image in the animation.

## Docker Method
Since its a bit tricky to get all the dependencies set up just right, there is
a Dockerfile provided.

1. [Install Docker](https://www.docker.com/products/overview)
2. Build docker image. `docker build -t manim .`
3. Run it! `docker run --rm -v "$PWD/files":/app/files manim example_scenes.py WarpSquare`

You'll find the output images in `./files` as usual.
