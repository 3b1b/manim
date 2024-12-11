custom_config
==============

``directories``
---------------

- ``mirror_module_path``
    (``True`` or ``False``) Whether to create a folder named the name of the 
    running file under the ``output`` path, and save the output (``images/`` 
    or ``videos/``) in it.

- ``base``
    The root directory that will hold files, such as video files manim renders,
    or image resources that it pulls from

- ``output``
    Output file path, the videos will be saved in the ``videos/`` folder under it, 
    and the pictures will be saved in the ``images/`` folder under it.

    For example, if you set ``output`` to ``"/.../manim/output"`` and 
    ``mirror_module_path`` to ``False``, then you exported ``Scene1`` in the code 
    file and saved the last frame, then the final directory structure will be like:

    .. code-block:: text
        :emphasize-lines: 9, 11

            manim/
            ├── manimlib/
            │   ├── animation/
            │   ├── ...
            │   ├── default_config.yml
            │   └── window.py
            ├── output/
            │   ├── images
            │   │   └── Scene1.png
            │   └── videos
            │       └── Scene1.mp4
            ├── code.py
            └── custom_config.yml

    But if you set ``mirror_module_path`` to ``True``, the directory structure will be:

    .. code-block:: text
        :emphasize-lines: 8

            manim/
            ├── manimlib/
            │   ├── animation/
            │   ├── ...
            │   ├── default_config.yml
            │   └── window.py
            ├── output/
            │   └── code/
            │       ├── images
            │       │   └── Scene1.png
            │       └── videos
            │           └── Scene1.mp4
            ├── code.py
            └── custom_config.yml

- ``raster_images`` 
    The directory for storing raster images to be used in the code (including 
    ``.jpg``, ``.jpeg``, ``.png`` and ``.gif``), which will be read by ``ImageMobject``.

- ``vector_images``
    The directory for storing vector images to be used in the code (including 
    ``.svg`` and ``.xdv``), which will be read by ``SVGMobject``.

- ``sounds``
    The directory for storing sound files to be used in ``Scene.add_sound()`` (
    including ``.wav`` and ``.mp3``).

- ``cache``
    The directory for storing temporarily generated cache files, including 
    ``Tex`` cache, ``Text`` cache and storage of object points.


``window``
----------

- ``position_string``
    The relative position of the playback window on the display (two characters, 
    the first character means upper(U) / middle(O) / lower(D), the second character 
    means left(L) / middle(O) / right(R)).

- ``monitor_index``
    If using multiple monitors, which one should the window show up in?

- ``full_screen``
    Should the preview window be full screen. If not, it defaults to half the screen

- ``position``
    This is an option to more manually set the default window position, in pixel
    coordinates, e.g. (500, 300)

- ``size``
    Option to more manually set the default window size, in pixel coordinates,
    e.g. (1920, 1080)


``camera``
----------

- ``resolution``
    Resolution to render at, e.g. (1920, 1080)

- ``background_color``
    Default background color of scenes

- ``fps``
    Framerate

- ``background_opacity``
    Opacity of the background


``file_writer``
---------------
Configuration specifying how files are written, e.g. what ffmpeg parameters to use


``scene``
-------
Some default configuration for the Scene class


``text``
-------

- ``font`` 
    Default font of Text

- ``text_alignment``
    Default text alignment for LaTeX

``tex``
-------

- ``template``
    Which configuration from the manimlib/tex_template.yml file should be used
    to determine the latex compiler to use, and what preamble to include for 
    rendering tex. 


``sizes``
---------

Valuess for various constants used in manimm to specify distances, like the height
of the frame, the value of SMALL_BUFF, LARGE_BUFF, etc.


``colors``
----------

Color pallete to use, determining values of color constants like RED, BLUE_E, TEAL, etc.

``loglevel``
------------

Can be DEBUG / INFO / WARNING / ERROR / CRITICAL


``universal_import_line``
-------------------------

Import line that need to execute when entering interactive mode directly.


``ignore_manimlib_modules_on_reload``
-------------------------------------

When calling ``reload`` during the interactive mode, imported modules are
by default reloaded, in case the user writing a scene which pulls from various
other files they have written. By default, modules withinn the manim library will
be ignored, but one developing manim may want to set this to be False so that 
edits to the library are reloaded as well.
