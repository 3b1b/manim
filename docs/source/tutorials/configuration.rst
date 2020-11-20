Configuration
#############

Manim provides an extensive configuration system that allows it to adapt to
many different use cases.  There are many configuration options that can be
configured at different times during the scene rendering process.  Each option
can be configured programatically via `the ManimConfig class`_, or at the time
of command invocation via `command line arguments`_, or at the time the library
is first imported via `the config files`_.


The ManimConfig class
*********************

The most direct way of configuring manim is via the global ``config`` object,
which is an instance of :class:`.ManimConfig`.  Each property of this class is
a config option that can be accessed either with standard attribute syntax, or
with dict-like syntax:

.. code-block:: python

   >>> from manim import *
   >>> config.background_color = WHITE
   >>> config['background_color'] = WHITE

The former is preferred; the latter is provided mostly for backwards
compatibility.

Most classes, including :class:`.Camera`, :class:`.Mobject`, and
:class:`.Animation`, read some of their default configuration from the global
``config``.

.. code-block:: python

   >>> Camera({}).background_color
   <Color white>
   >>> config.background_color = RED  # 0xfc6255
   >>> Camera({}).background_color
   <Color #fc6255>

:class:`.ManimConfig` is designed to keep internal consistency.  For example,
setting ``frame_y_radius`` will affect ``frame_height``:

.. code-block:: python

    >>> config.frame_height
    8.0
    >>> config.frame_y_radius = 5.0
    >>> config.frame_height
    10.0

The global ``config`` object is mean to be the single source of truth for all
config options.  All of the other ways of setting config options ultimately
change the values of the global ``config`` object.

The following example illustrates the video resolution chosen for examples
rendered in our documentation with a reference frame.

.. manim:: ShowScreenResolution
    :save_last_frame:

    class ShowScreenResolution(Scene):
        def construct(self):
            pixel_height = config["pixel_height"]  #  1080 is default
            pixel_width = config["pixel_width"]  # 1920 is default
            frame_width = config["frame_width"]
            frame_height = config["frame_height"]
            self.add(Dot())
            d1 = Line(frame_width * LEFT / 2, frame_width * RIGHT / 2).to_edge(DOWN)
            self.add(d1)
            self.add(Text(str(pixel_width)).next_to(d1, UP))
            d2 = Line(frame_height * UP / 2, frame_height * DOWN / 2).to_edge(LEFT)
            self.add(d2)
            self.add(Text(str(pixel_height)).next_to(d2, RIGHT))


Command line arguments
**********************

Usually, manim is ran from the command line by executing

.. code-block:: bash

   $ manim <file.py> SceneName

This asks manim to search for a Scene class called :code:`SceneName` inside the
file <file.py> and render it.  One can also specify the render quality by using
the flags :code:`-ql`, :code:`-qm`, :code:`-qh`, or :code:`-qk`, for low, medium,
high, and 4k quality, respectively.

.. code-block:: bash

   $ manim <file.py> SceneName -ql

These flags set the values of the config options ``config.pixel_width``,
``config.pixel_height``, ``config.frame_rate``, and ``config.quality``.

Another frequent flag is ``-p`` ("preview"), which makes manim show the rendered video
right after it's done rendering.

.. note:: The ``-p`` flag does not change any properties of the global
          ``config`` dict.  The ``-p`` flag is only a command line convenience.


Examples
========

To render a scene in high quality, but only output the last frame of the scene
instead of the whole video, you can execute

.. code-block:: bash

   $ manim <file.py> SceneName -sqh

The following example specifies the output file name (with the :code:`-o`
flag), renders only the first ten animations (:code:`-n` flag) with a white
background (:code:`-c` flag), and saves the animation as a .gif instead of as a
.mp4 file (:code:`-i` flag).  It uses the default quality and does not try to
open the file after it is rendered.

.. code-block:: bash

   $ manim <file.py> SceneName -o myscene -i -n 0,10 -c WHITE

.. tip:: There are many more command line flags that manim accepts.  All the
	 possible flags are shown by executing ``manim -h``.  A complete list
	 of CLI flags is at the end of this document.


The config files
****************

As the last example shows, executing manim from the command line may involve
using many flags at the same time.  This may become a nuisance if you must
execute the same script many times in a short time period, for example when
making small incremental tweaks to your scene script.  For this purpose, manim
can also be configured using a configuration file.  A configuration file is a
file ending with the suffix ``.cfg``.

To use a configuration file when rendering your scene, you must create a file
with name ``manim.cfg`` in the same directory as your scene code.

.. warning:: The config file **must** be named ``manim.cfg``. Currently, manim
             does not support config files with any other name.

The config file must start with the section header ``[CLI]``.  The
configuration options under this header have the same name as the CLI flags,
and serve the same purpose.  Take for example the following config file.

.. code-block::

   [CLI]
   # my config file
   output_file = myscene
   save_as_gif = True
   background_color = WHITE

Config files are read with the standard python library ``configparser``. In
particular, they will ignore any line that starts with a pound symbol ``#``.

Now, executing the following command

.. code-block:: bash

   $ manim <file.py> SceneName -o myscene -i -c WHITE

is equivalent to executing the following command, provided that ``manim.cfg``
is in the same directory as <file.py>,

.. code-block:: bash

   $ manim <file.py> SceneName

.. tip:: The names of the configuration options admissible in config files are
         exactly the same as the **long names** of the corresponding command
         line flags.  For example, the ``-c`` and ``--background_color`` flags
         are interchangeable, but the config file only accepts
         :code:`background_color` as an admissible option.

Since config files are meant to replace CLI flags, all CLI flags can be set via
a config file.  Moreover, any config option can be set via a config file,
whether or not it has an associated CLI flag.  For a list of all CLI flags and
all config options, see the bottom of this document.

Manim will look for a ``manim.cfg`` config file in the same directory as the
file being rendered, and **not** in the directory of execution.  For example,

.. code-block:: bash

   $ manim <path/to/file.py> SceneName -o myscene -i -c WHITE

will use the config file found in ``path/to/file.py``, if any.  It will **not**
use the config file found in the current working directory, even if it exists.
In this way, the user may keep different config files for different scenes or
projects, and execute them with the right configuration from anywhere in the
system.

The file described here is called the **folder-wide** config file, because it
affects all scene scripts found in the same folder.


The user config file
====================

As explained in the previous section, a :code:`manim.cfg` config file only
affects the scene scripts in its same folder.  However, the user may also
create a special config file that will apply to all scenes rendered by that
user. This is referred to as the **user-wide** config file, and it will apply
regardless of where manim is executed from, and regardless of where the scene
script is stored.

The user-wide config file lives in a special folder, depending on the operating
system.

* Windows: :code:`UserDirectory`/AppData/Roaming/Manim/manim.cfg
* MacOS: :code:`UserDirectory`/config/manim/manim.cfg
* Linux: :code:`UserDirectory`/config/manim/manim.cfg

Here, :code:`UserDirectory` is the user's home folder.


.. note:: A user may have many **folder-wide** config files, one per folder,
          but only one **user-wide** config file.  Different users in the same
          computer may each have their own user-wide config file.

.. warning:: Do not store scene scripts in the same folder as the user-wide
             config file.  In this case, the behavior is undefined.

Whenever you use manim from anywhere in the system, manim will look for a
user-wide config file and read its configuration.


Cascading config files
======================

What happens if you execute manim and it finds both a folder-wide config file
and a user-wide config file?  Manim will read both files, but if they are
incompatible, **the folder-wide file takes precedence**.

For example, take the following user-wide config file

.. code-block::

   # user-wide
   [CLI]
   output_file = myscene
   save_as_gif = True
   background_color = WHITE

and the following folder-wide file

.. code-block::

   # folder-wide
   [CLI]
   save_as_gif = False

Then, executing :code:`manim <file.py> SceneName` will be equivalent to not
using any config files and executing

.. code-block:: bash

   manim <file.py> SceneName -o myscene -c WHITE

Any command line flags have precedence over any config file.  For example,
using the previous two config files and executing :code:`manim <file.py>
SceneName -c RED` is equivalent to not using any config files and executing

.. code-block:: bash

   manim <file.py> SceneName -o myscene -c RED

There is also a **library-wide** config file that determines manim's default
behavior, and applies to every user of the library.  It has the least
precedence, so any config options in the user-wide and any folder-wide files
will override the library-wide file.  This is referred to as the *cascading*
config file system.

.. warning:: **The user should not try to modify the library-wide file**.
	     Contributors should receive explicit confirmation from the core
	     developer team before modifying it.


Order of operations
*******************

With so many different ways of configuring manim, it can be difficult to know
when each config option is being set.  In fact, this will depend on how manim
is being used.

If manim is imported from a module, then the configuration system will follow
these steps:

1. The library-wide config file is loaded.
2. The user-wide and folder-wide files are loaded, if they exist.
3. All files found in the previous two steps are parsed in a single
   :class:`ConfigParser` object, called ``parser``.  This is where *cascading*
   happens.
4. :class:`logging.Logger` is instantiated to create manim's global ``logger``
   object. It is configured using the "logger" section of the parser,
   i.e. ``parser['logger']``.
5. :class:`ManimConfig` is instantiated to create the global ``config`` object.
6. The ``parser`` from step 3 is fed into the ``config`` from step 5 via
   :meth:`ManimConfig.digest_parser`.
7. Both ``logger`` and ``config`` are exposed to the user.

If manim is being invoked from the command line, all of the previous steps
happen, and are complemented by:

8. The CLI flags are parsed and fed into ``config`` via
   :meth:`~ManimConfig.digest_args`.
9. If the ``--config_file`` flag was used, a new :class:`ConfigParser` object
   is created with the contents of the library-wide file, the user-wide file if
   it exists, and the file passed via ``--config_file``.  In this case, the
   folder-wide file, if it exists, is ignored.
10. The new parser is fed into ``config``.
11. The rest of the CLI flags are processed.

To summarize, the order of precedence for configuration options, from lowest to
highest precedence, is:

1. Library-wide config file,
2. user-wide config file, if it exists,
3. folder-wide config file, if it exists OR custom config file, if passed via
   ``--config_file``,
4. other CLI flags, and
5. any programmatic changes made after the config system is set.


A list of all config options
****************************

.. testcode::
   :hide:

   from manim._config import ManimConfig
   from inspect import getmembers
   sorted([n for n, _ in getmembers(ManimConfig, lambda v: isinstance(v, property))])

.. testoutput::
   :options: -ELLIPSIS, +NORMALIZE_WHITESPACE

   ['aspect_ratio', 'background_color', 'background_opacity', 'bottom',
   'custom_folders', 'disable_caching', 'dry_run', 'ffmpeg_loglevel',
   'flush_cache', 'frame_height', 'frame_rate', 'frame_size', 'frame_width',
   'frame_x_radius', 'frame_y_radius', 'from_animation_number', 'images_dir',
   'input_file', 'js_renderer_path', 'leave_progress_bars', 'left_side',
   'log_dir', 'log_to_file', 'max_files_cached', 'media_dir',
   'movie_file_extension', 'output_file', 'partial_movie_dir', 'pixel_height',
   'pixel_width', 'png_mode', 'preview', 'progress_bar', 'quality',
   'right_side', 'save_as_gif', 'save_last_frame', 'save_pngs', 'scene_names',
   'show_in_file_browser', 'skip_animations', 'sound', 'tex_dir',
   'tex_template', 'tex_template_file', 'text_dir', 'top', 'transparent',
   'upto_animation_number', 'use_js_renderer', 'verbosity', 'video_dir',
   'write_all', 'write_to_movie']


A list of all CLI flags
***********************

.. testcode::
   :hide:

   import subprocess
   result = subprocess.run(['manim', '-h'], stdout=subprocess.PIPE)
   print(result.stdout.decode('utf-8'))

.. testoutput::
   :options: -ELLIPSIS, +NORMALIZE_WHITESPACE

   usage: manim [-h] [-o OUTPUT_FILE] [-p] [-f] [--leave_progress_bars] [-a] [-w] [-s] [-g] [-i] [--disable_caching] [--flush_cache] [--log_to_file] [-c BACKGROUND_COLOR]
                [--background_opacity BACKGROUND_OPACITY] [--media_dir MEDIA_DIR] [--log_dir LOG_DIR] [--tex_template TEX_TEMPLATE] [--dry_run] [-t] [-q {k,p,h,m,l}]
                [--low_quality] [--medium_quality] [--high_quality] [--production_quality] [--fourk_quality] [-l] [-m] [-e] [-k] [-r RESOLUTION] [-n FROM_ANIMATION_NUMBER]
                [--use_js_renderer] [--js_renderer_path JS_RENDERER_PATH] [--config_file CONFIG_FILE] [--custom_folders] [-v {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                [--progress_bar True/False]
                {cfg} ... file [scene_names [scene_names ...]]

   Animation engine for explanatory math videos

   positional arguments:
     {cfg}
     file                  path to file holding the python code for the scene
     scene_names           Name of the Scene class you want to see

   optional arguments:
     -h, --help            show this help message and exit
     -o OUTPUT_FILE, --output_file OUTPUT_FILE
                           Specify the name of the output file, if it should be different from the scene class name
     -p, --preview         Automatically open the saved file once its done
     -f, --show_in_file_browser
                           Show the output file in the File Browser
     --leave_progress_bars
                           Leave progress bars displayed in terminal
     -a, --write_all       Write all the scenes from a file
     -w, --write_to_movie  Render the scene as a movie file (this is on by default)
     -s, --save_last_frame
                           Save the last frame only (no movie file is generated)
     -g, --save_pngs       Save each frame as a png
     -i, --save_as_gif     Save the video as gif
     --disable_caching     Disable caching (will generate partial-movie-files anyway)
     --flush_cache         Remove all cached partial-movie-files
     --log_to_file         Log terminal output to file
     -c BACKGROUND_COLOR, --background_color BACKGROUND_COLOR
                           Specify background color
     --background_opacity BACKGROUND_OPACITY
                           Specify background opacity
     --media_dir MEDIA_DIR
                           Directory to store media (including video files)
     --log_dir LOG_DIR     Directory to store log files
     --tex_template TEX_TEMPLATE
                           Specify a custom TeX template file
     --dry_run             Do a dry run (render scenes but generate no output files)
     -t, --transparent     Render a scene with an alpha channel
     -q {k,p,h,m,l}, --quality {k,p,h,m,l}
                           Render at specific quality, short form of the --*_quality flags
     --low_quality         Render at low quality
     --medium_quality      Render at medium quality
     --high_quality        Render at high quality
     --production_quality  Render at default production quality
     --fourk_quality       Render at 4K quality
     -l                    DEPRECATED: USE -ql or --quality l
     -m                    DEPRECATED: USE -qm or --quality m
     -e                    DEPRECATED: USE -qh or --quality h
     -k                    DEPRECATED: USE -qk or --quality k
     -r RESOLUTION, --resolution RESOLUTION
                           Resolution, passed as "height,width". Overrides any quality flags, if present
     -n FROM_ANIMATION_NUMBER, --from_animation_number FROM_ANIMATION_NUMBER
                           Start rendering at the specified animation index, instead of the first animation. If you pass in two comma separated values, e.g. '3,6', it will end
                           the rendering at the second value
     --use_js_renderer     Render animations using the javascript frontend
     --js_renderer_path JS_RENDERER_PATH
                           Path to the javascript frontend
     --config_file CONFIG_FILE
                           Specify the configuration file
     --custom_folders      Use the folders defined in the [custom_folders] section of the config file to define the output folder structure
     -v {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --verbosity {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                           Verbosity level. Also changes the ffmpeg log level unless the latter is specified in the config
     --progress_bar True/False
                           Display the progress bar

   Made with <3 by the manim community devs
