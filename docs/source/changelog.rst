*********
Changelog
*********

manimce-v1.0.0-dev
==================

:Date: N/A

New Features
-------------
#. Add 4k rendering option
#. Added clearer installation instructions and quick-use scripts
#. Added tests to ensure stuff doesn’t break between commits (For developers) [Uses Github CI, and Pytest]
#. high quality has gotten its own short argument (-e), and the quality argument explanations have been improved
#. Implement logging with :code:`rich` and :code:`logger` instead of plain ol` prints.
#. Add customizable left and right bracket for :code:`Matrix` mobject and :code:`set_row_colors` method for matrix mobject
#. Added a flag :code:`dry_run`, which doesn’t write any media.
#. Allow for running manim with :code:`python3 -m manim`
#. Add :code:`AddTeXLetterByLetter` animation
#. Implement a :code:`manim.cfg` config file system, where the majority of variables in :code:`constant.py` can be modified
#. Re-add GIF export
#. Refactored Tex Template management. You can now use custom templates with command line args!

#. Enhanced GraphScene
    #. You can now add arrow tips to axes
    #. extend axes a bit at the start and/or end
    #. have invisible axes
#. Add :code:`z_index` for manipulating depth of Objects on scene.
#. Add contribution guidelines (for developers)
#. Re-add :code:`--save_frames` flag, which will save each frame as a png
#. Add a :code:`VDict` class, which is basically to a :code:`VGroup` what a :code:`dictionary` is to a :code:`list`
#. Re-introduce manim feature that allows you to type manim code in :code:`stdin` if you pass “-“ as filename
#. Added utilities for manipulating Manim’s :code:`.cfg` files.
#. Added a subcommand structure for easier use of utilities managing :code:`.cfg` files
#. Added Scene-caching feature. Now, if a partial movie file is unchanged in your code, it isn’t rendered again! [HIGHLY UNSTABLE We're working on it ;)]

Fixes
-----
#. Initialization of directories has been moved to config.py, and a bunch of bugs associated to file structure generation have been fixed
#. Nonfunctional :code:`media_dir.txt` has been removed
#. Nonfunctional if statements in :code:`scene_file_writer.py` have been removed
#. Fix a bug where trying to render the example scenes without specifying the scene would show all scene objects in the library.


Other Changes
--------------
#. Cleanup 3b1b Specific Files
#. Made manim internally use relative imports (For developers)
#. Move all imports to :code:`__init__`, so :code:`from manim import *` replaces :code:`from manimlib.imports import *`
#. Rename Folder from manimlib to manim
#. Global dir variable handling has been removed. Instead :code:`initialize_directories`, if needed, overrides the values from the cfg files at runtime.
