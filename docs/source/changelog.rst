#########
Changelog
#########

.. contents:: Release history
   :depth: 1
   :local:
   :backlinks: none


****************
Upcoming release
****************

:Date: TBD

Changes for the upcoming release are tracked `in our GitHub wiki <https://github.com/ManimCommunity/manim/wiki/Changelog-for-next-release>`_.


******
v0.3.0
******

:Date: February 1, 2021

The changes since Manim Community release v0.2.0 are listed below.


New Features
============

- :pr:`945`: :meth:`~.Graph.change_layout` method for :class:`~.Graph` mobject
- :pr:`943`: IPython %%manim magic
- :pr:`970`: Added ``--version`` command line flag
- :pr:`948`: Allow passing a code string to :class:`~.Code`
- :pr:`917`: Allow overriding new-style method animations
- :pr:`756`: Allow setting frame_height and frame_width via config file
- :pr:`939`: Added custom font files support
- :pr:`892`: Added ManimCommunity colors
- :pr:`922`: Tree layout for Graph mobject
- :pr:`935`: Added code of conduct
- :pr:`916`: Multi-column layout for partite graphs
- :pr:`742`: Units: Pixels, Munits, Percent in :mod:`~.utils.unit`
- :pr:`893`: Convenience method :meth:`~.Graph.from_networkx` for creating a graph from a networkx graph

Bugfixes and Enhancements
=========================

- :pr:`988`: Fix Windows CI pipeline by adding missing LaTeX package
- :pr:`961`: Added typings and docs for vectorized mobjects and bezier related functions
- :pr:`977`: JupyterLab docker image and documentation for manim and IPython
- :pr:`985`: Fix variable name for webgl renderer
- :pr:`954`: Fix edges lagging behind vertices in animations of graphs
- :pr:`980`: Allow usage of custom Pygments styles in Code
- :pr:`952`: Allow passing tween information to the WebGL frontend
- :pr:`978`: Fix ``possible_paths`` not printing in ``code_mobject``
- :pr:`976`: Update ``ManimPango``
- :pr:`967`: Automatically import plugins
- :pr:`971`: Make ManimCommunity look consistent
- :pr:`957`: Raise ``NotImplementedError`` when trying to chain overridden method animations
- :pr:`947`: Several fixes and improvements for :class:`~.PointCloundDot`
- :pr:`923`: Documentation: move installation instructions for developers to page for developers
- :pr:`964`: Added unit test for :class:`~.NumberLine`'s unit vector
- :pr:`960`: Magnitude of :class:`~.NumberLine`'s unit vector should be ``unit_size``, not 1
- :pr:`958`: Fix code formatting in ``utils/debug.py``
- :pr:`953`: Update license year
- :pr:`944`: Interpolate stroke opacity in :class:`~.FadeIn` and update ``stroke_opacity`` and ``fill_opacity`` in :meth:`~.VMobject.set_stroke` and :meth:`~.VMobject.set_fill`
- :pr:`865`: Rename ``get_submobject_index_labels`` to ``index_labels``
- :pr:`941`: Added keyword arguments ``x_min``, ``x_max``, ``y_min``, ``y_max`` to :class:`~.ThreeDAxes`
- :pr:`886`: Let the render progress bar show details about the rendered animation again
- :pr:`936`: Fix :class:`~.BulletedList` TeX environment problem and add a typing to ``get_module``
- :pr:`938`: Remove dependency on progressbar
- :pr:`937`: Change 'brew cask install' to 'brew install --cask' for CI pipeline
- :pr:`933`: Make matrix work with lists again
- :pr:`932`: Correctly parse ``log_dir`` option
- :pr:`920`: Raise error if markup in :class:`~.MarkupText` is invalid
- :pr:`929`: Raise an error if a :class:`~.Matrix` object is created with < 2-dimensional input
- :pr:`907`: Make Scene.add_sound work again (when running with ``--disable_caching``)
- :pr:`906`: Allow new-style method animation to be used in animation groups
- :pr:`908`: Removed deprecated command line arguments from documentation
- :pr:`903`: Tiny grammar improvements
- :pr:`904`: Added blank line between imports and class example
- :pr:`898`: CI: fix publish workflow


******
v0.2.0
******

:Date: January 1, 2021

The changes since Manim Community release v0.1.1 are listed below.

Breaking Changes
================

- Remove all CONFIG dictionaries and all calls to ``digest_config`` and allow
  passing options directly to the constructor of the corresponding classes (:pr:`783`).

  Practically, this means that old constructions using ``CONFIG`` like::

      class SomeMobject(Thing):
          CONFIG = {
              "my_awesome_property": 42
          }

  where corresponding objects were then instantiated as ``my_mobject = SomeMobject()``
  should now be created simply using ``my_mobject = SomeMobject(my_awesome_property=42)``.

- Remove old syntax for animating mobject methods by passing the methods and arguments to ``self.play``,
  and use a new syntax featuring the ``animate`` property (:pr:`881`).

  For example: the old-style ``play`` call
  ::

      self.play(my_square.shift, LEFT)

  should be replaced with the new following call using the ``animate`` property::

      self.play(my_square.animate.shift(LEFT))

New Features
============

- Added creation animation for :class:`~.ManimBanner` (:pr:`814`)
- Added some documentation to :meth:`~.Scene.construct` (:pr:`753`)
- Added a black and white monochromatic version of Manim's logo (:pr:`826`)
- Added support for a plugin system (``manim plugin`` subcommand + documentation) (:pr:`784`)
- Implemented ``__add__``, ``__iadd__``, ``__sub__``, and ``__isub__`` for :class:`~.Mobject` (allowing for notation like ``some_vgroup + some_mobject``) (:pr:`790`)
- Added type hints to several files in the library (:pr:`835`)
- Added some examples to :mod:`~.animation.creation` (:pr:`820`)
- Added some examples to :class:`~.DashedLine` and :class:`~.CurvesAsSubmobjects` (:pr:`833`)
- Added new implementation for text rendered with Pango, :class:`~.MarkupText`, which can be formatted with an HTML-like syntax (:pr:`855`)
- Added Fading in and out examples and deprecation of ``FadeInFromDown`` and ``FadeOutAndShiftDown`` (:pr:`827`)
- Added example for :class:`~.MoveAlongPath` to the docs (:pr:`873`)
- Added ambient rotate for other angles - theta, phi, gamma (:pr:`660`)
- Use custom bindings for Pango (:pr:`878`)
- Added :class:`~.Graph`, a basic implementation for (graph theory) graphs (:pr:`861`)
- Allow for chaining methods when using the new ``.animate`` syntax in :meth:`~.Scene.play` (:pr:`889`)

Bugfixes
========

- Fix doctests in .rst files (:pr:`797`)
- Fix failing doctest after adding ``manim plugin`` subcommand (:pr:`831`)
- Normalize the direction vector in :meth:`~.mobject_update_utils.always_shift` (:pr:`839`)
- Add ``disable_ligatures`` to :class:`~.Text` (via :pr:`804`)
- Make scene caching aware of order of Mobjects (:pr:`845`)
- Fix :class:`~.CairoText` to work with new config structure (:pr:`858`)
- Added missing argument to classes inheriting from :class:`~.Matrix` (:pr:`859`)
- Fixed: ``z_index`` of mobjects contained in others as submobjects is now properly respected (:pr:`872`)
- Let :meth:`~.ParametricSurface.set_fill_by_checkboard` return the modified surface to allow method chaining (:pr:`883`)
- Mobjects added during an updater are added to ``Scene.moving_mobjects`` (:pr:`838`)
- Pass background color to JS renderer (:pr:`876`)
- Small fixes to docstrings. Tiny cleanups. Remove ``digest_mobject_attrs``. (:pr:`834`)
- Added closed shape detection in :class:`~.DashedVMobject` in order to achieve an even dash pattern (:pr:`884`)
- Fix Spelling in docstrings and variables across the library (:pr:`890`)

Other changes
=============

- Change library name to manim (:pr:`811`)
- Docker: use local files when building an image (:pr:`803`)
- Let ffmpeg render partial movie files directly instead of temp files (:pr:`817`)
- ``manimce`` to ``manim`` & capitalizing Manim in readme (:pr:`794`)
- Added flowchart for different docstring categories (:pr:`828`)
- Improve example in module docstring of :mod:`~.animation.creation` + explicitly document buff parameter in :meth:`~.Mobject.arrange` (:pr:`825`)
- Disable CI pipeline for Python 3.6 (:pr:`823`)
- Update URLs in docs (:pr:`832`)
- Move upcoming changelog to GitHub-wiki (:pr:`822`)
- Change badges in readme (:pr:`854`)
- Exclude generated gRPC files from source control (:pr:`868`)
- Added linguist-generated attribute to ``.gitattributes`` (:pr:`877`)
- Cleanup: removed inheritance from ``object`` for some classes, refactor some imports (:pr:`795`)
- Change several ``str.format()`` to ``f``-strings (:pr:`867`)
- Update javascript renderer (:pr:`830`)
- Bump version number to 0.2.0, update changelog (:pr:`894`)


******
v0.1.1
******

:Date: December 1, 2020

Changes since Manim Community release v0.1.0

Plugins
=======

#. Provided a standardized method for plugin discoverability, creation,
   installation, and usage. See the :ref:`documentation <plugins>`.

Fixes
=====

#. JsRender is optional to install. (via :pr:`697`).
#. Allow importing modules from the same directory as the input
   file when using ``manim`` from the command line (via :pr:`724`).
#. Remove some unnecessary or unpythonic methods from :class:`~.Scene`
   (``get_mobjects``, ``add_mobjects_among``, ``get_mobject_copies``),
   via :pr:`758`.
#. Fix formatting of :class:`~.Code` (via :pr:`798`).

Configuration
=============

#. Removed the ``skip_animations`` config option and added the
   ``Renderer.skip_animations`` attribute instead (via :pr:`696`).
#. The global ``config`` dict has been replaced by a global ``config`` instance
   of the new class :class:`~.ManimConfig`.  This class has a dict-like API, so
   this should not break user code, only make it more robust.  See the
   Configuration tutorial for details.
#. Added the option to configure a directory for external assets (via :pr:`649`).


Documentation
=============

#. Add ``:issue:`` and ``:pr:`` directives for simplifying linking to issues and
   pull requests on GitHub (via :pr:`685`).
#. Add a ``skip-manim`` tag for skipping the ``.. manim::`` directive when
   building the documentation locally (via :pr:`796`).


Mobjects, Scenes, and Animations
================================

#. The ``alignment`` attribute to Tex and MathTex has been removed in favour of ``tex_environment``.
#. :class:`~.Text` now uses Pango for rendering. ``PangoText`` has been removed. The old implementation is still available as a fallback as :class:`~.CairoText`.
#. Variations of :class:`~.Dot` have been added as :class:`~.AnnotationDot`
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
#. Added Mobject raise not implemented errors for dunder methods and implementations for VGroup dunder methods (via :pr:`790`).
#. Added :class:`~.ManimBanner` for a animated version of our logo and banner (via :pr:`729`)
#. The background color of a scene can now be changed reliably by setting, e.g.,
   ``self.camera.background_color = RED`` (via :pr:`716`).



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
#. Added a flag :code:`--dry_run`, which doesn't write any media
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
#. Added tests to ensure stuff doesn't break between commits (For developers) [Uses Github CI, and Pytest]
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
