Configuration
=============

Manim provides an extensive configuration system that allows it to adapt to
many different use cases.  The easiest way to do this is through the use of
command line (or *CLI*) arguments.


Command Line Arguments
**********************

Usually, manim is ran from the command line by executing

.. code-block:: bash

   $ manim <file.py> SceneName

This asks manim to search for a Scene class called :code:`SceneName` inside the
file <file.py> and render it.  One can also specify the render quality by using
the flags :code:`-ql`, :code:`-qm`, :code:`-qh`, or :code:`-qk`, for low, medium,
high, and 4k quality, respectively.

.. code-block:: bash

   $ manim <file.py> SceneName -l

Another frequent flag is :code:`-p`, which makes manim show the rendered video
right after it's done rendering.

There are in fact many more command line flags that manim accepts.  All the
possible flags are shown by the following command.

.. code-block:: bash

   $ manim -h

The output looks as follows.

.. testcode::
   :hide:

   import subprocess
   result = subprocess.run(['manim', '-h'], stdout=subprocess.PIPE)
   print(result.stdout.decode('utf-8'))

.. testoutput::
   :options: -ELLIPSIS, +NORMALIZE_WHITESPACE

   usage: manim [-h] [-o OUTPUT_FILE] [-p] [-f] [--leave_progress_bars] [-a] [-w] [-s] [-g] [-i] [--disable_caching] [--flush_cache] [--log_to_file] [-c BACKGROUND_COLOR]
             [--background_opacity BACKGROUND_OPACITY] [--media_dir MEDIA_DIR] [--log_dir LOG_DIR] [--tex_template TEX_TEMPLATE] [--dry_run] [-t] [-q {k,h,m,l}] [--low_quality] [--medium_quality]
             [--high_quality] [--fourk_quality] [-r RESOLUTION] [-n FROM_ANIMATION_NUMBER] [--use_js_renderer] [--js_renderer_path JS_RENDERER_PATH] [--config_file CONFIG_FILE] [--custom_folders]
             [-v {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--progress_bar True/False]
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
  -q {k,h,m,l}, --quality {k,h,m,l}
                        Render at specific quality, short form of the --*_quality flags
  --low_quality         Render at low quality
  --medium_quality      Render at medium quality
  --high_quality        Render at high quality
  --fourk_quality       Render at 4K quality
  -r RESOLUTION, --resolution RESOLUTION
                        Resolution, passed as "height,width". Overrides any quality flags, if present
  -n FROM_ANIMATION_NUMBER, --from_animation_number FROM_ANIMATION_NUMBER
                        Start rendering at the specified animation index, instead of the first animation. If you pass in two comma separated values, e.g. '3,6', it will end the rendering at the second
                        value
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

For example, to render a scene in high quality, but only output the last frame
of the scene instead of the whole video, you can execute

.. code-block:: bash

   $ manim <file.py> SceneName -sqh

The following example specifies the output file name (with the :code:`-o`
flag), renders only the first ten animations (:code:`-n` flag) with a white
background (:code:`-c` flag), and saves the animation as a .gif instead of as a
.mp4 file (:code:`-i` flag).  It uses the default quality and does not try to
open the file after it is rendered.

.. code-block:: bash

   $ manim <file.py> SceneName -o myscene -i -n 0,10 -c WHITE



The config files
****************

As the last example shows, executing manim from the command line may involve
using many flags at the same.  This may become a nuisance if you must execute
the same file many times in a short time period, for example when making small
incremental tweaks to your scene script.  For this purpose, manim can also be
configured using a configuration file.

To use a configuration file when rendering your scene, you must create a file
with name :code:`manim.cfg` in the same directory as your scene code.

.. warning:: The config file **must** be named :code:`manim.cfg`. Currently,
             manim does not support config files with any other name.

The config file must start with a section header, usually :code:`[CLI]`.  The
configuration options under this header have the same name as the CLI flags,
and serve the same purpose.  Take for example the following config file.

.. code-block::

   [CLI]
   output_file = myscene
   save_as_gif = True
   background_color = WHITE

Executing :code:`manim <file.py> SceneName` on a directory that contains this
config file is equivalent to executing

.. code-block:: bash

   $ manim <file.py> SceneName -o myscene -i -c WHITE

on a directory that does not contain a config file.

.. note:: The names of the configuration options admissible in config files are
          exactly the same as the **long names** of the corresponding command
          line flags.  For example, the :code:`-c` and
          :code:`--background_color` flags are interchangeable, but the config
          file only accepts :code:`background_color` as an admissible option.

.. note:: Configuration options that do not have command line analogues will be
          ignored.  For a list of all the command line flags, see `Command Line
          Arguments`_.

Manim will look for a :code:`manim.cfg` config file in the same directory as
the file being rendered, and **not** in the directory of execution.  For
example,

.. code-block:: bash

   $ manim <file.py> path/to/SceneName -o myscene -i -c WHITE

will use the config file found in :code:`path/to/SceneName`, if any.  It will
**not** use the config file found in the current working directory, even if it
exists.  In this way, the user may keep different config files for different
scenes or projects, and execute them with the right configuration from anywhere
in the system.

.. note:: Config files will ignore any line that starts with a pound symbol
          :code:`#`.


The user config file
********************

As explained in the previous section, a :code:`manim.cfg` config file only
affects the scene scripts in its same directory.  However, the user may also
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


.. note:: Config files that only apply to their own folder, explained in the
          previous section, are called **folder-wide** config files.  A user
          may have many folder-wide config files, one per folder, but only one
          **user-wide** config file.  Different users in the same computer may
          each have their own user-wide config file.

.. warning:: Do not store scene scripts in the same folder as the user-wide
             config file.  In this case, the behavior is undefined.

Whenever you use manim from anywhere in the system, manim will look for a
user-wide config file and read its configuration.


Cascading config files
**********************

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

To summarize, the order of precedence for configuration options is: *user-wide
config file < folder-wide config file < CLI flags*.


.. note:: There is also a **library-wide** config file that determines manim's
	  default behavior, and applies to every user of the library.  It has
	  the least precedence, and **the user should not try to modify it**.
	  Developers should receive explicit confirmation from the core
	  developer team before modifying it.
