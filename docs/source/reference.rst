Reference
===============

This reference manual details modules, functions, and variables included in
Manim, describing what they are and what they do.  For learning how to use
Manim, see :doc:`tutorials`.  For a list of changes since the last release, see
the :doc:`changelog`.

.. warning:: The pages linked to here are currently a work in progress.


List of Modules
***************

.. currentmodule:: manim

**Mathematical Objects**

.. autosummary::
   :toctree: reference

   ~mobject.mobject
   ~mobject.types.vectorized_mobject
   ~mobject.geometry
   ~mobject.number_line
   ~mobject.svg.svg_mobject


**Scenes**

.. autosummary::
   :toctree: reference

   ~scene.scene
   ~scene.zoomed_scene
   ~scene.moving_camera_scene


**Animations**

.. autosummary::
   :toctree: reference

   ~animation.animation
   ~animation.creation
   ~animation.fading
   ~animation.composition


**Cameras**

.. autosummary::
   :toctree: reference

   ~camera.camera
   ~camera.mapping_camera
   ~camera.moving_camera
   ~camera.multi_camera
   ~camera.three_d_camera


**Other modules**

.. autosummary::
   :toctree: reference

   config
   constants
   container


.. This is here so that sphinx doesn't complain about changelog.rst not being
   included in any toctree
.. toctree::
   :hidden:

   changelog
