#########
Changelog
#########

******
v0.2.0
******

:Date: TBD

Changes since Manim Community release v0.1.0

Fixes
=====

#. JsRender is optional to install. (via :pr:`697`).

Configuration
=============

#. Removed the ``skip_animations`` config option and added the
   ``Renderer.skip_animations`` attribute instead (via :pr:`696`).

#. The global ``config`` dict has been replaced by a global ``config`` instance
   of the new class :class:`~.ManimConfig`.  This class has a dict-like API, so
   this should not break user code, only make it more robust.  See the
   Configuration tutorial for details.


Documentation
=============

#. Add ``:issue:`` and ``:pr:`` directives for simplifying linking to issues and
   pull requests on GitHub (via :pr:`685`).


Mobjects, Scenes, and Animations
================================

#. The ``alignment`` attribute to Tex and MathTex has been removed in favour of ``tex_environment``.
#. :class:`~.Text` now uses Pango for rendering. ``PangoText`` has been removed. The old implementation is still available as a fallback as :class:`~.CairoText`.
#. **New**: Variations of :class:`~.Dot` have been added as :class:`~.AnnotationDot`
   (a bigger dot with bolder stroke) and :class:`~.LabeledDot` (a dot containing a
   label).
#. Scene.set_variables_as_attrs has been removed (via :pr:`692`).
#. Ensure that the axes for graphs (:class:`GraphScene`) always intersect (:pr:`580`).
#. Now Mobject.add_updater does not call the newly-added updater by default
   (use ``call_updater=True`` instead) (via :pr:`710`)
#. VMobject now has methods to determine and change the direction of the points (via :pr:`647`).
#. Added BraceBetweenPoints (via :pr:`693`).
#. Added ArcPolygon and ArcPolygonFromArcs (via :pr:`707`).
#. Added Cutout (via :pr:`760`).


******
v0.1.0
******

:Date: October 21, 2020

This is the first release of manimce after forking from 3b1b/manim.  As such,
developers have focused on cleaning up and refactoring the codebase while still
maintaining backwards compatibility wherever possible.


New Features
============

Command line
------------

#. Output of 'manim --help' has been improved
#. Implement logging with the :code:`rich` library and a :code:`logger` object instead of plain ol' prints
#. Added a flag :code:`--dry_run`, which doesn’t write any media
#. Allow for running manim with :code:`python3 -m manim`
#. Refactored Tex Template management. You can now use custom templates with command line args using :code:`--tex_template`!
#. Re-add :code:`--save_frames` flag, which will save each frame as a png
#. Re-introduce manim feature that allows you to type manim code in :code:`stdin` if you pass a minus sign :code:`(-)` as filename
#. Added the :code:`--custom_folders` flag which yields a simpler output folder structure
#. Re-implement GIF export with the :code:`-i` flag (using this flag outputs ONLY a .gif file, and no .mp4 file)
#. Added a :code:`--verbose` flag
#. You can save the logs to a file by using :code:`--log_to_file`
#. Read :code:`tex_template` from config file if not specified by :code:`--tex_template`.
#. Add experimental javascript rendering with :code:`--use_js_renderer`
#. Add :code:`-q/--quality [k|p|h|m|l]` flag and removed :code:`-m/-l` flags.
#. Removed :code:`--sound` flag


Config system
-------------

#. Implement a :code:`manim.cfg` config file system, that consolidates the global configuration, the command line argument parsing, and some of the constants defined in :code:`constants.py`
#. Added utilities for manipulating Manim’s :code:`.cfg` files.
#. Added a subcommand structure for easier use of utilities managing :code:`.cfg` files
#. Also some variables have been moved from ``constants.py`` to the new config system:

    #. ``FRAME_HEIGHT`` to ``config["frame_width"]``
    #. ``TOP`` to ``config["frame_height"] / 2 * UP``
    #. ``BOTTOM`` to ``config["frame_height"] / 2 * DOWN``
    #. ``LEFT_SIDE`` to ``config["frame_width"] / 2 * LEFT``
    #. ``RIGHT_SIDE`` to ``config["frame_width"] / 2 * RIGHT``
    #. ``self.camera.frame_rate`` to ``config["frame_rate"]``




Mobjects, Scenes, and Animations
--------------------------------

#. Add customizable left and right bracket for :code:`Matrix` mobject and :code:`set_row_colors` method for matrix mobject
#. Add :code:`AddTeXLetterByLetter` animation
#. Enhanced GraphScene

    #. You can now add arrow tips to axes
    #. extend axes a bit at the start and/or end
    #. have invisible axes
    #. highlight the area between two curves
#. ThreeDScene now supports 3dillusion_camera_rotation
#. Add :code:`z_index` for manipulating depth of Objects on scene.
#. Add a :code:`VDict` class: a :code:`VDict` is to a :code:`VGroup` what a :code:`dict` is to a :code:`list`
#. Added Scene-caching feature. Now, if a partial movie file is unchanged in your code, it isn’t rendered again! [HIGHLY UNSTABLE We're working on it ;)]
#. Most :code:`get_` and :code:`set_` methods have been removed in favor of instance attributes and properties
#. The :code:`Container` class has been made into an AbstractBaseClass, i.e. in cannot be instantiated.  Instead, use one of its children classes
#. The ``TextMobject`` and ``TexMobject`` objects have been deprecated, due to their confusing names, in favour of ``Tex`` and ``MathTex``. You can still, however, continue to use ``TextMobject`` and ``TexMobject``, albeit with Deprecation Warnings constantly reminding you to switch.
#. Add a :code:`Variable` class for displaying text that continuously updates to reflect the value of a python variable.
#. The ``Tex`` and ``MathTex`` objects allow you to specify a custom TexTemplate using the ``template`` keyword argument.
#. :code:`VGroup` now supports printing the class names of contained mobjects and :code:`VDict` supports printing the internal dict of mobjects
#. Add all the standard easing functions
#. :code:`Scene` now renders when :code:`Scene.render()` is called rather than upon instantiation.
#. :code:`ValueTracker` now supports increment using the `+=` operator (in addition to the already existing `increment_value` method)
#. Add :class:`PangoText` for rendering texts using Pango.


Documentation
=============

#. Added clearer installation instructions, tutorials, examples, and API reference [WIP]


Fixes
=====

#. Initialization of directories has been moved to :code:`config.py`, and a bunch of bugs associated to file structure generation have been fixed
#. Nonfunctional file :code:`media_dir.txt` has been removed
#. Nonfunctional :code:`if` statements in :code:`scene_file_writer.py` have been removed
#. Fix a bug where trying to render the example scenes without specifying the scene would show all scene objects in the library
#. Many :code:`Exceptions` have been replaced for more specific exception subclasses
#. Fixed a couple of subtle bugs in :code:`ArcBetweenPoints`


Of interest to developers
=========================

#. Python code formatting is now enforced by using the :code:`black` tool
#. PRs now require two approving code reviews from community devs before they can be merged
#. Added tests to ensure stuff doesn’t break between commits (For developers) [Uses Github CI, and Pytest]
#. Add contribution guidelines (for developers)
#. Added autogenerated documentation with sphinx and autodoc/autosummary [WIP]
#. Made manim internally use relative imports
#. Since the introduction of the :code:`TexTemplate` class, the files :code:`tex_template.tex` and :code:`ctex_template.tex` have been removed
#. Added logging tests tools.
#. Added ability to save logs in json
#. Move to Poetry.
#. Colors have moved to an Enum

Other Changes
=============

#. Cleanup 3b1b Specific Files
#. Rename package from manimlib to manim
#. Move all imports to :code:`__init__`, so :code:`from manim import *` replaces :code:`from manimlib.imports import *`
#. Global dir variable handling has been removed. Instead :code:`initialize_directories`, if needed, overrides the values from the cfg files at runtime.
