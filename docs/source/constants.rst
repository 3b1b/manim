Manim Constants
===============

The ``constants.py`` under ``manimlib/`` contains variables that are used
during setup and running manim. Some variables are not documented here as they are
only used internally by manim.

Directories
-----------

    MEDIA_DIR
              The directory where ``VIDEO_DIR`` and ``TEX_DIR`` will be created,
              if they aren't specified via flags.
    VIDEO_DIR
              Used to store the scenes rendered by Manim. When a scene is
              finished rendering, it will be stored under
              ``VIDEO_DIR/module_name/scene_name/quality/scene_name.mp4``.
              Created under ``MEDIA_DIR`` by default.
    TEX_DIR
              Files written by Latex are stored here. It also acts as a cache
              so that the files aren't rewritten each Latex is needed.

Those directories are created if they don't exist.

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
            1920x1080 @ 60fps. # Used when the ``-h`` or ``--high_quality`` flag
            is passed.
    MEDIUM_QUALITY_CAMERA_CONFIG
            1280x720 @ 30fps. # Used when the ``-m`` or ``--medium_quality``
            flag is passed.
    LOW_QUALITY_CAMERA_CONFIG
            854x480 @ 15fps. # Used when the ``-l`` or ``--low_quality`` flag is
            passed.

.. _ref-directions:

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
