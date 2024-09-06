Manim's structure
=================


Manim's directory structure
---------------------------

The manim directory looks very complicated, with a lot of files, 
but the structure is clear.

Below is the directory structure of manim:

.. code-block:: text

    manimlib/ # manim library
    ├── __init__.py          
    ├── __main__.py          
    ├── default_config.yml   # Default configuration file
    ├── config.py            # Process CLI flags
    ├── constants.py         # Defined some constants
    ├── extract_scene.py     # Extract and run the scene
    ├── shader_wrapper.py    # Shaders' Wrapper for convenient control
    ├── window.py            # Playback window
    ├── tex_templates/ # Templates preset for LaTeX
    │   ├── tex_templates.tex   # Tex template (will be compiled with latex, default)
    │   └── ctex_templates.tex  # Tex template that support Chinese (will be compiled with xelatex)
    ├── camera/
    │   └── camera.py        # Including Camera and CameraFrame
    ├── scene/
    │   ├── scene_file_writer.py     # Used to write scene to video file
    │   ├── scene.py                 # The basic Scene class
    │   ├── three_d_scene.py         # Three-dimensional scene
    │   ├── sample_space_scene.py    # Probability related sample space scene
    │   └── vector_space_scene.py    # Vector field scene
    ├── animation/
    │   ├── animation.py     # The basic class of animation
    │   ├── composition.py   # Animation group
    │   ├── creation.py      # Animation related to Create
    │   ├── fading.py        # Fade related animation
    │   ├── growing.py       # Animation related to Grow
    │   ├── indication.py    # Some animations for emphasis
    │   ├── movement.py      # Animation related to movement
    │   ├── numbers.py       # Realize changes to DecimalNumber
    │   ├── rotation.py      # Animation related to rotation
    │   ├── specialized.py   # Some uncommon animations for special projects
    │   ├── transform_matching_parts.py # Transform which can automatically match parts
    │   ├── transform.py     # Some Transforms
    │   └── update.py        # Realize update from function
    ├── mobject/
    │   ├── mobject.py       # The basic class of all math object
    │   ├── types/ # 4 types of mobject
    │   │   ├── dot_cloud.py            # Dot cloud (an subclass of PMobject)
    │   │   ├── image_mobject.py        # Insert pictures
    │   │   ├── point_cloud_mobject.py  # PMobject (mobject composed of points)
    │   │   ├── surface.py              # ParametricSurface
    │   │   └── vectorized_mobject.py   # VMobject (vectorized mobject)
    │   ├── svg/ # mobject related to svg
    │   │   ├── svg_mobject.py          # SVGMobject
    │   │   ├── brace.py                # Brace
    │   │   ├── drawings.py             # Some special mobject of svg image
    │   │   ├── tex_mobject.py          # Tex and TexText implemented by LaTeX
    │   │   └── text_mobject.py         # Text implemented by manimpango
    │   ├── changing.py             # Dynamically changing mobject
    │   ├── coordinate_systems.py   # coordinate system
    │   ├── frame.py                # mobject related to frame
    │   ├── functions.py            # ParametricFunction
    │   ├── geometry.py             # geometry mobjects
    │   ├── matrix.py               # matrix
    │   ├── mobject_update_utils.py # some defined updater
    │   ├── number_line.py          # Number line
    │   ├── numbers.py              # Numbers that can be changed
    │   ├── probability.py          # mobject related to probability
    │   ├── shape_matchers.py       # mobject adapted to the size of other objects
    │   ├── three_dimensions.py     # Three-dimensional objects
    │   ├── value_tracker.py        # ValueTracker which storage number
    │   └── vector_field.py         # VectorField
    ├── once_useful_constructs/  # 3b1b's Common scenes written for some videos
    │   └── ...
    ├── shaders/ # GLSL scripts for rendering
    │   ├── simple_vert.glsl    # a simple glsl script for position
    │   ├── insert/ # glsl scripts to be inserted in other glsl scripts
    │   │   ├── NOTE.md   # explain how to insert glsl scripts
    │   │   └── ...       # useful scripts
    │   ├── image/ # glsl for images
    │   │   └── ... # containing shaders for vertex and fragment
    │   ├── quadratic_bezier_fill/ # glsl for the fill of quadratic bezier curve
    │   │   └── ... # containing shaders for vertex, fragment and geometry
    │   ├── quadratic_bezier_stroke/ # glsl for the stroke of quadratic bezier curve
    │   │   └── ... # containing shaders for vertex, fragment and geometry
    │   ├── surface/ # glsl for surfaces
    │   │   └── ... # containing shaders for vertex and fragment
    │   ├── textured_surface/ # glsl for textured_surface
    │   │   └── ... # containing shaders for vertex and fragment
    │   └── true_dot/ # glsl for a dot
    │       └── ... # containing shaders for vertex, fragment and geometry
    └── utils/ # Some useful utility functions
        ├── bezier.py             # For bezier curve
        ├── color.py              # For color
        ├── dict_ops.py           # Functions related to dictionary processing
        ├── customization.py      # Read from custom_config.yml
        ├── debug.py              # Utilities for debugging in program
        ├── directories.py        # Read directories from config file
        ├── family_ops.py         # Process family members
        ├── file_ops.py           # Process files and directories
        ├── images.py             # Read image
        ├── init_config.py        # Configuration guide
        ├── iterables.py          # Functions related to list/dictionary processing
        ├── paths.py              # Curve path
        ├── rate_functions.py     # Some defined rate_functions
        ├── simple_functions.py   # Some commonly used functions
        ├── sounds.py             # Process sounds
        ├── space_ops.py          # Space coordinate calculation
        ├── strings.py            # Process strings
        └── tex_file_writing.py   # Use LaTeX to write strings as svg

Inheritance structure of manim's classes
----------------------------------------

`Here <https://github.com/3b1b/manim/files/5824383/manim_shaders_structure.pdf>`_ 
is a pdf showed inheritance structure of manim's classes, large, 
but basically all classes have included:

.. image:: https://cdn.jsdelivr.net/gh/manim-kindergarten/CDN@master/manimgl_assets/manim_shaders_structure.png

Manim execution process
-----------------------

.. image:: https://cdn.jsdelivr.net/gh/manim-kindergarten/CDN@master/manimgl_assets/manim_shaders_process_en.png
