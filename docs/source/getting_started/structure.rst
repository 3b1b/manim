Manim's structure
=================


Manim's directory structure
----------------------------

The manim directory looks very complicated, with a lot of files,
but the structure is clear.

Below is the directory structure of manim:

.. code-block:: text

    manimlib/                         # Main Manim library package
    ├── __init__.py                   # Package initializer
    ├── __main__.py                   # CLI entry point
    ├── config.py                     # Configuration handling
    ├── constants.py                  # Global constants (colors, directions, etc.)
    ├── default_config.yml            # Default configuration file
    ├── extract_scene.py              # Extract and run scenes
    ├── logger.py                     # Logging utilities
    ├── module_loader.py              # Dynamic module loading
    ├── shader_wrapper.py             # Shader wrapper for convenient control
    ├── tex_templates.yml             # LaTeX templates
    ├── typing.py                     # Custom typing definitions
    ├── window.py                     # Playback window

    ├── animation/                    # Animation system
    │   ├── animation.py              # Base Animation class
    │   ├── composition.py            # AnimationGroup, Succession, etc.
    │   ├── creation.py               # Create / Write animations
    │   ├── fading.py                 # FadeIn, FadeOut
    │   ├── growing.py                # Grow animations
    │   ├── indication.py             # Emphasis animations
    │   ├── movement.py               # Movement animations
    │   ├── numbers.py                # DecimalNumber animations
    │   ├── rotation.py               # Rotation animations
    │   ├── specialized.py            # Special project animations
    │   ├── transform.py              # Transform animations
    │   ├── transform_matching_parts.py # Smart matching transforms
    │   └── update.py                 # UpdateFromFunc animations

    ├── camera/                       # Camera system
    │   ├── camera.py                 # Camera and CameraFrame
    │   └── camera_frame.py           # CameraFrame definition

    ├── event_handle/                 # Event handling (keyboard, mouse)
    │   ├── event_dispatcher.py       # Event dispatcher
    │   ├── event_listner.py          # Event listeners
    │   └── event_type.py             # Event type definitions

    ├── mobject/                      # Core visual objects
    │   ├── mobject.py                # Base Mobject class
    │   ├── mobject_update_utils.py   # Updater utilities
    │   ├── boolean_ops.py            # Union, intersection, difference
    │   ├── changing.py               # Dynamically changing mobjects
    │   ├── coordinate_systems.py     # Axes, NumberPlane
    │   ├── frame.py                  # Frame-related mobjects
    │   ├── functions.py              # ParametricFunction
    │   ├── geometry.py               # Circle, Square, Line, etc.
    │   ├── interactive.py            # Interactive mobjects
    │   ├── matrix.py                 # Matrix mobject
    │   ├── number_line.py            # NumberLine
    │   ├── numbers.py                # DecimalNumber, Integer
    │   ├── probability.py            # Probability visuals
    │   ├── shape_matchers.py         # SurroundingRectangle, etc.
    │   ├── three_dimensions.py       # 3D objects
    │   ├── value_tracker.py          # ValueTracker
    │   └── vector_field.py           # VectorField

    │   ├── types/                    # Core mobject types
    │   │   ├── vectorized_mobject.py # VMobject (Bezier-based)
    │   │   ├── point_cloud_mobject.py# PMobject (points-based)
    │   │   ├── dot_cloud.py          # DotCloud
    │   │   ├── image_mobject.py      # ImageMobject
    │   │   └── surface.py            # ParametricSurface

    │   └── svg/                      # SVG & LaTeX-based mobjects
    │       ├── svg_mobject.py        # SVG loader
    │       ├── tex_mobject.py        # Tex (LaTeX)
    │       ├── text_mobject.py       # Text (Pango)
    │       ├── string_mobject.py     # String-based objects
    │       ├── special_tex.py        # Special LaTeX
    │       ├── old_tex_mobject.py    # Legacy Tex
    │       ├── brace.py              # Brace object
    │       └── drawings.py           # Custom SVG drawings

    ├── scene/                        # Scene system
    │   ├── scene.py                  # Base Scene class
    │   ├── interactive_scene.py      # Interactive scenes
    │   ├── scene_embed.py            # Embed mode
    │   └── scene_file_writer.py      # Video writer

    ├── shaders/                      # GLSL shaders
    │   ├── simple_vert.glsl          # Basic vertex shader
    │   ├── insert/                   # GLSL snippets
    │   ├── image/                    # Image shaders
    │   ├── surface/                  # Surface shaders
    │   ├── textured_surface/         # Textured surface shaders
    │   ├── quadratic_bezier/         # Bezier fill shaders
    │   ├── true_dot/                 # Dot shader
    │   ├── mandelbrot_fractal/       # Mandelbrot shader
    │   └── newton_fractal/           # Newton fractal shader

    └── utils/                        # Utility functions
        ├── bezier.py                 # Bezier curve math
        ├── cache.py                  # Caching utilities
        ├── color.py                  # Color utilities
        ├── debug.py                  # Debug helpers
        ├── dict_ops.py               # Dictionary operations
        ├── directories.py            # Directory management
        ├── family_ops.py             # Mobject family handling
        ├── file_ops.py               # File utilities
        ├── images.py                 # Image processing
        ├── iterables.py              # Iterable helpers
        ├── paths.py                  # Path calculations
        ├── rate_functions.py         # Animation easing functions
        ├── shaders.py                # Shader utilities
        ├── simple_functions.py       # Common helper functions
        ├── sounds.py                 # Sound processing
        ├── space_ops.py              # Vector/space math
        ├── text.py                   # Text utilities
        ├── tex_file_writing.py       # LaTeX compilation
        └── tex_to_symbol_count.py    # LaTeX symbol counting


Inheritance structure of Manim's classes
----------------------------------------

Here is a PDF showing the inheritance structure of Manim's classes:

https://github.com/3b1b/manim/files/5824383/manim_shaders_structure.pdf

The structure is large, but fundamentally most components are built upon:

- Mobject
- VMobject / PMobject
- Animation
- Scene
- Camera