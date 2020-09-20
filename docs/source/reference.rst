Reference
===============

This reference manual details modules, functions, and variables included in
Manim, describing what they are and what they do.  For learning how to use
Manim, see :doc:`tutorials`.  For a list of changes since the last release, see
the :doc:`changelog`.

.. warning:: The pages linked to here are currently a work in progress.


********************
Mathematical Objects
********************

.. autosummary::
   :toctree: reference

   ~manim.mobject.changing
   ~manim.mobject.coordinate_systems
   ~manim.mobject.frame
   ~manim.mobject.functions
   ~manim.mobject.geometry
   ~manim.mobject.matrix
   ~manim.mobject.mobject
   ~manim.mobject.mobject_update_utils
   ~manim.mobject.number_line
   ~manim.mobject.numbers
   ~manim.mobject.probability
   ~manim.mobject.shape_matchers
   ~manim.mobject.three_d_shading_utils
   ~manim.mobject.three_d_utils
   ~manim.mobject.three_dimensions
   ~manim.mobject.value_tracker
   ~manim.mobject.vector_field
   ~manim.mobject.svg.brace
   ~manim.mobject.svg.code_mobject
   ~manim.mobject.svg.drawings
   ~manim.mobject.svg.svg_mobject
   ~manim.mobject.svg.tex_mobject
   ~manim.mobject.svg.text_mobject
   ~manim.mobject.types.image_mobject
   ~manim.mobject.types.point_cloud_mobject
   ~manim.mobject.types.vectorized_mobject


******
Scenes
******

.. autosummary::
   :toctree: reference

   ~manim.scene.graph_scene
   ~manim.scene.moving_camera_scene
   ~manim.scene.reconfigurable_scene
   ~manim.scene.sample_space_scene
   ~manim.scene.scene
   ~manim.scene.scene_file_writer
   ~manim.scene.three_d_scene
   ~manim.scene.vector_space_scene
   ~manim.scene.zoomed_scene


**********
Animations
**********

.. autosummary::
   :toctree: reference

   ~manim.animation.animation
   ~manim.animation.composition
   ~manim.animation.creation
   ~manim.animation.fading
   ~manim.animation.growing
   ~manim.animation.indication
   ~manim.animation.movement
   ~manim.animation.numbers
   ~manim.animation.rotation
   ~manim.animation.specialized
   ~manim.animation.transform
   ~manim.animation.update


*******
Cameras
*******

.. autosummary::
   :toctree: reference

   ~manim.camera.camera
   ~manim.camera.mapping_camera
   ~manim.camera.moving_camera
   ~manim.camera.multi_camera
   ~manim.camera.three_d_camera


*********
Utilities
*********

.. autosummary::
   :toctree: reference

   ~manim.utils.bezier
   ~manim.utils.color
   ~manim.utils.config_ops
   ~manim.utils.hashing
   ~manim.utils.images
   ~manim.utils.iterables
   ~manim.utils.paths
   ~manim.utils.rate_functions
   ~manim.utils.simple_functions
   ~manim.utils.sounds
   ~manim.utils.space_ops
   ~manim.utils.strings
   ~manim.utils.tex
   ~manim.utils.tex_file_writing


*************
Other modules
*************

.. autosummary::
   :toctree: reference

   ~manim._config
   ~manim.constants
   ~manim.container
   manim_directive


.. This is here so that sphinx doesn't complain about changelog.rst not being
   included in any toctree
.. toctree::
   :hidden:

   changelog
