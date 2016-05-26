# animations
Animation engine for explanatory math videos

updates coming...

## Install requirements
```sh
pip install -r requirements.txt
```

`aggdraw` has to be installed manually, pip can't do it for you.

Here are directions that should work on any 64 bit platform (tested on osx
10.11.4)

This doesn't install freetype, but I don't think its required for this project

```
cd $TMPDIR
# or hg clone https://stefanfoulis@bitbucket.org/2degrees/aggdraw-64bits
# instead of the next 2 commands
wget https://bitbucket.org/2degrees/aggdraw-64bits/get/a95a86958b68.zip
unzip a95a86958b68.zip -d aggdraw-64bits
cd aggdraw-64bits
/usr/local/bin/python setup.py build_ext -i
/usr/local/bin/python setup.py install
```

## How to Use
Not exactly sure. I think I'm supposed to run `python extract_scene.py
generate_logo.py`, but that fails with the following error.

```
Traceback (most recent call last):
  File "extract_scene.py", line 205, in main
    handle_scene(SceneClass(**scene_kwargs), **config)
  File "/Users/scott/scratch/manim/scene/scene.py", line 32, in __init__
    self.construct(*self.construct_args)
  File "/Users/scott/scratch/manim/./generate_logo.py", line 50, in construct
    self.interpolation_factor
TypeError: interpolate() takes exactly 5 arguments (4 given)
```
