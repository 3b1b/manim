Manim Constants
===============

The ``constants.py`` under ``manimlib/`` contains variables that are used
during setup and running manim. Some variables are not documented here as they are
only used internally by manim.

Directories
-----------

    MEDIA_DIR
              The root directory for media files. First the environment variable
              ``MEDIA_DIR`` is queried. If the env is not found, use the path
              as specified in ``manimlib/media_dir.txt``. If media_dir.txt is empty,
              a directory is created under users home. If ``MEDIA_DIR`` is not a
              directory, ``media`` will be created under current working directory.
              Defaults to ``manimlib/media``
    VIDEO_DIR
              Created under ``MEDIA_DIR``. Used to store rendered manim scenes.
              When scene finished rendering, it will be stored under ``media/project_name/quality/scene_name.mp4``
    RASTER_IMAGE_DIR
              Created under ``media/designs/raster_images``. For storing
              raster images like jpg, png, etc.
    SVG_IMAGE_DIR
              Created under ``media/designs/svg_images``. For storing svg files.
    SOUND_DIR
              Created under ``media/designs/sounds``. For storing sound files.
    THIS_DIR
              Path to the directory which ``constants.py`` resides.
    FILE_DIR
              The root directory for misc files. Specified by the environment variable
              ``FILE_DIR``. If the variable is not found, a directory ``files`` will be
              created under current working directory.
    TEX_DIR
              Created under ``FILE_DIR/files``. TexMObject and TextMobject are rendered
              here for temporary storage.

Those directories are created if they don't exist.

.. note::
    ``MOBJECT_DIR`` and ``IMAGE_MOBJECT_DIR`` is deprecated.

Tex
---
    TEX_USE_CTEX
              A boolean value. Change it to True if you need to use Chinese typesetting.
    TEX_TEXT_TO_REPLACE
              Placeholder text used by manim when generating tex files
    TEMPLATE_TEX_FILE
              By default ``manimlib/tex_template.tex`` is used. If ``TEX_USE_CTEX``
              is set to True then ``manimlib/ctex_template.tex`` is used.

Numerical Constants
-------------------

    PI
            alias to ``numpy.pi``
    TAU
            PI * 2

    DEGREES
            TAU / 360

Camera Configuration
--------------------

Render setting presets

    PRODUCTION_QUALITY_CAMERA_CONFIG
            2560x1440 @ 60fps # This is the default when rendering a scene
    HIGH_QUALITY_CAMERA_CONFIG
            1920x1080 @ 60fps.
    MEDIUM_QUALITY_CAMERA_CONFIG
            1280x720 @ 30fps # Used when ``-m`` flag is passed
    LOW_QUALITY_CAMERA_CONFIG
            854x480 @ 15fps. # Used when ``-l`` flag is passed

Coordinates
-----------

Used for 2d/3d animations and placements::

    ORIGIN
    UP
    DOWN
    RIGHT
    LEFT
    IN # 3d camera only, away from camera
    OUT # 3d camera only, close to camera

    UL = UP + LEFT # diagonal abbreviations. You can use either one
    UR = UP + RIGHT
    DL = DOWN + LEFT
    DR = DOWN + RIGHT

    TOP
    BOTTOM
    LEFT_SIDE
    RIGHT_SIDE``

Colors
------

    COLOR_MAP
            A predefined color maps
    PALETTE
            A list of color hex strings, derived from COLOR_MAP
