custom_config
=============

This file determines the default configuration for how Manim is run, including
names for directories it will write to, default parameters for various classes,
style choices, etc. To customize your own, create a ``custom_config.yml`` file
in whatever directory you are running Manim.  

Alternatively, you can create it wherever you like, and on running Manim, pass in
``--config_file /path/to/custom/config/file.yml``.

directories
-----------

- ``mirror_module_path``
    (``True`` or ``False``) Whether to create a folder named the name of the
    running file under the ``output`` path, and save the output
    (``images/`` or ``videos/``) in it.

- ``removed_mirror_prefix``
    Path prefix to remove from mirrored directories.

- ``base``
    The root directory that will hold files, such as video files Manim renders,
    or image resources that it pulls from.

- ``subdirs``
    Subdirectories under ``base`` for various resources:

    - ``output``: Where Manim saves video and image files.
    - ``raster_images``: For ``.jpg``, ``.jpeg``, ``.png``, ``.gif`` used by ``ImageMobject``.
    - ``vector_images``: For ``.svg`` and ``.xdv`` used by ``SVGMobject``.
    - ``pi_creature_images``: SVG images for Pi creatures.
    - ``three_d_models``: For 3D model files.
    - ``sounds``: For audio files used in ``Scene.add_sound()``.
    - ``data``: Any project-related data like CSVs.
    - ``downloads``: Default folder for downloaded assets.
    - ``latex_cache``: For storing cached LaTeX compilation results.

- ``cache``
    Directory for storing temporary cache files, including Tex/Text caches.

window
------

- ``position_string``: Position of the playback window on screen (e.g. UR → Upper Right).
- ``monitor_index``: Which monitor to display the window on.
- ``full_screen``: Whether to use full screen.
- ``position``: Optional pixel coordinates to manually set window position.
- ``size``: Optional pixel dimensions to manually set window size.

camera
------

- ``resolution``: Output resolution, e.g. (1920, 1080).
- ``background_color``: Default scene background color.
- ``fps``: Frames per second.
- ``background_opacity``: Opacity of background.

file_writer
-----------

Configuration for file writing, e.g., ffmpeg parameters:

- ``ffmpeg_bin``: Path to ffmpeg.
- ``video_codec``: Codec to use.
- ``pixel_format``: Pixel format.
- ``saturation``: Saturation value.
- ``gamma``: Gamma correction.

scene
-----

Default configuration for the ``Scene`` class:

- ``show_animation_progress``: Show progress bars.
- ``leave_progress_bars``: Keep progress bars visible.
- ``preview_while_skipping``: Render a single frame when skipping animations.
- ``default_wait_time``: Duration for ``Scene.wait()`` calls.

vmobject
--------

- ``default_stroke_width``: Stroke width.
- ``default_stroke_color``: Default stroke color.
- ``default_fill_color``: Default fill color.

mobject
-------

- ``default_mobject_color``: Default mobject color.
- ``default_light_color``: Default light color.

tex
---

- ``template``: Tex template to use (see ``tex_templates.yml``).

text
----

- ``font``: Default font for Text.
- ``alignment``: Default alignment for LaTeX text.

embed
-----

- ``exception_mode``: Mode for displaying exceptions.
- ``autoreload``: Whether to automatically reload scripts.

resolution_options
------------------

- ``low``: Low resolution (854, 480)
- ``med``: Medium resolution (1280, 720)
- ``high``: High resolution (1920, 1080)
- ``4k``: Ultra HD (3840, 2160)

sizes
-----

- ``frame_height``: Frame height for Manim coordinate system.
- ``small_buff``, ``med_small_buff``, ``med_large_buff``, ``large_buff``: Default spacing constants.
- ``default_mobject_to_edge_buff``: Buffer for ``Mobject.to_edge``.
- ``default_mobject_to_mobject_buff``: Buffer for ``Mobject.next_to``.

key_bindings
------------

Default keyboard bindings:

- ``pan_3d``: d
- ``pan``: f
- ``reset``: r
- ``quit``: q
- ``select``: s
- ``unselect``: u
- ``grab``: g
- ``x_grab``: h
- ``y_grab``: v
- ``z_grab``: z
- ``resize``: t
- ``color``: c
- ``information``: i
- ``cursor``: k

colors
------

Defined in ``custom_config.yml`` (see colors section above).

log_level
---------

Can be DEBUG / INFO / WARNING / ERROR / CRITICAL.

universal_import_line
---------------------

Python import line to execute in interactive mode.

ignore_manimlib_modules_on_reload
---------------------------------

If False, modules inside Manim are reloaded when calling ``reload`` in interactive mode.