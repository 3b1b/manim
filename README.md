# animations
Animation engine for explanatory math videos

For those who want to play around with this tool, I should be upfront that I've mostly had my own use cases (i.e. 3b1b videos) in mind while building it, and it might not be the most friendly thing to get up and running.  In particular, I have not done a great job tracking requirements, and documentation, to put it euphamistically, almost exclusively takes the form of naming conventions.

For 9/10 math animation needs, you'd probably be better off using a more well-maintained tool, like mathplotlib or mathematica.  I happen to think the program "Grapher" built into osx is really great, and surprisingly versatile for many needs.  My own reasons for building this tool and using it for videos are twofold, and I'm not sure how well they apply to other people's use cases.

  1) If I wish to work with some new type of mathematical thing (e.g. a fractal), or to experiment with a different type of animation, it's easier to work it into the underlying system and manipulate it the same way as more standard objects/animation.  Admittedly, though, part of the reason I find this easier is because I'm more familiar with the underlying system here than I am with others.  This keeps me from shying away from certain video topics that I would otherwise have no idea how to animate.

  2) Having my own tool has been a forcing function for having a style which is more original than what I may have otherwise produced. The cost of this was slower video production when the tool was in its early days, and during points when I do some kind of rehaul, but I think the artistic benefit is a real one.  If you wish to use this tool and adopt the same style, by all means feel free.  In fact, I encourage it.  But the tricky part about anything which confers the benefit of originality is that this benefit cannot be easily shared.


## Install requirements
```sh
pip install -r requirements.txt
```

Requirements to be installed outside of pip:
aggdraw (try it from scottopell/aggdraw-64bits@c95aac4)
ffmpeg
latex

Here are directions that should work on any 64 bit platform (tested on osx
10.11.4)

This doesn't install freetype, but I don't think it's required for this project

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

Look through the old_projects folder to see the code for previous 3b1b videos.  

While developing a scene, the -s flag is helpful to just see what things look like at the end without having to generate the full animation.  It can also be helpful to put self.force_skipping() at the top of the construct method, and self.revert_to_original_skipping_status() before the portion of the scene that you want to test, and run with the -p flag to just see a preview of one part of the scene.

Scene with PiCreatures are somewhat 3b1b specific, so the specific designs for various expressions are not part of the public repo.  You should still be able to run them, but they will fall back on using the "plain" expression for the creature.



























