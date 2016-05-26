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
git clone https://github.com/scottopell/aggdraw-64bits
cd aggdraw-64bits
/usr/local/bin/python setup.py build_ext -i
/usr/local/bin/python setup.py install
```

## How to Use
Try running the following:
python extract_scene.py -p example_scenes.py SquareToCircle
