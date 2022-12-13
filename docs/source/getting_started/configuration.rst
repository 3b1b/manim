CLI flags and configuration
===========================

Command Line Interface
----------------------

To run manim, you need to enter the directory at the same level as ``manimlib/`` 
and enter the command in the following format into terminal:

.. code-block:: sh

    manimgl <code>.py <Scene> <flags>
    # or
    manim-render <code>.py <Scene> <flags>

- ``<code>.py`` : The python file you wrote. Needs to be at the same level as ``manimlib/``, otherwise you need to use an absolute path or a relative path.
- ``<Scene>`` : The scene you want to render here. If it is not written or written incorrectly, it will list all for you to choose. And if there is only one ``Scene`` in the file, this class will be rendered directly.
- ``<flags>`` : CLI flags.

Some useful flags
^^^^^^^^^^^^^^^^^

- ``-w`` to write the scene to a file.
- ``-o`` to write the scene to a file and open the result.
- ``-s`` to skip to the end and just show the final frame. 

  - ``-so`` will save the final frame to an image and show it.

- ``-n <number>`` to skip ahead to the ``n``\ ’th animation of a scene. 
- ``-f`` to make the playback window fullscreen.

All supported flags
^^^^^^^^^^^^^^^^^^^

========================================================== ====== =====================================================================================================================================================================================================
flag                                                       abbr   function
========================================================== ====== =====================================================================================================================================================================================================
``--help``                                                 ``-h`` Show the help message and exit
``--version``                                              ``-v`` Display the version of manimgl
``--write_file``                                           ``-w`` Render the scene as a movie file
``--skip_animations``                                      ``-s`` Skip to the last frame
``--low_quality``                                          ``-l`` Render at a low quality (for faster rendering)
``--medium_quality``                                       ``-m`` Render at a medium quality
``--hd``                                                          Render at a 1080p quality
``--uhd``                                                         Render at a 4k quality
``--full_screen``                                          ``-f`` Show window in full screen
``--presenter_mode``                                       ``-p`` Scene will stay paused during wait calls until space bar or right arrow is hit, like a slide show
``--save_pngs``                                            ``-g`` Save each frame as a png
``--gif``                                                  ``-i`` Save the video as gif
``--transparent``                                          ``-t`` Render to a movie file with an alpha channel
``--quiet``                                                ``-q``
``--write_all``                                            ``-a`` Write all the scenes from a file
``--open``                                                 ``-o`` Automatically open the saved file once its done
``--finder``                                                      Show the output file in finder
``--config``                                                      Guide for automatic configuration
``--file_name FILE_NAME``                                         Name for the movie or image file
``--start_at_animation_number START_AT_ANIMATION_NUMBER``  ``-n`` Start rendering not from the first animation, but from another, specified by its index. If you passing two comma separated values, e.g. "3,6", it will end the rendering at the second value.
``--embed [EMBED]``                                        ``-e`` Creates a new file where the line ``self.embed`` is inserted into the Scenes construct method. If a string is passed in, the line will be inserted below the last line of code including that string.
``--resolution RESOLUTION``                                ``-r`` Resolution, passed as "WxH", e.g. "1920x1080"
``--fps FPS``                                                     Frame rate, as an integer
``--color COLOR``                                          ``-c`` Background color
``--leave_progress_bars``                                         Leave progress bars displayed in terminal
``--video_dir VIDEO_DIR``                                         Directory to write video
``--config_file CONFIG_FILE``                                     Path to the custom configuration file
``--log-level LOG_LEVEL``                                         Level of messages to Display, can be DEBUG / INFO / WARNING / ERROR / CRITICAL
========================================================== ====== =====================================================================================================================================================================================================

custom_config
--------------

In order to perform more configuration (about directories, etc.) and permanently 
change the default value (you don't have to add flags to the command every time), 
you can modify ``custom_config.yml``. The meaning of each option is in 
page :doc:`../documentation/custom_config`.

You can also use different ``custom_config.yml`` for different directories, such as 
following the directory structure:

.. code-block:: text

    manim/
    ├── manimlib/
    │   ├── animation/
    │   ├── ...
    │   ├── default_config.yml
    │   └── window.py
    ├── project/
    │   ├── code.py
    │   └── custom_config.yml
    └── custom_config.yml

When you enter the ``project/`` folder and run ``manimgl code.py <Scene>``, 
it will overwrite ``manim/default_config.yml`` with ``custom_config.yml`` 
in the ``project`` folder.

Alternatively, you can use ``--config_file`` flag in CLI to specify configuration file manually.

.. code-block:: sh

    manimgl project/code.py --config_file /path/to/custom_config.yml