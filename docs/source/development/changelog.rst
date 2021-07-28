Changelog
=========

Unreleased
----------

Fixed bugs
^^^^^^^^^^

- Fixed the bug of :func:`~manimlib.utils.iterables.resize_with_interpolation` in the case of ``length=0``
- Fixed the bug of ``__init__`` in :class:`~manimlib.mobject.geometry.Elbow`
- If chosen monitor is not available, choose one that does exist
- Make sure mobject data gets unlocked after animations
- Fixed a bug for off-center vector fields
- Had ``Mobject.match_points`` return self
- Fixed chaining animation in example scenes
- Fixed the default color of tip
- Fixed a typo in ``ShowPassingFlashWithThinningStrokeWidth``
- Fixed the default size of ``Text``
- Fixed a missing import line in ``mobject.py``
- Fixed the bug in ControlsExample
- Make sure frame is added to the scene when initialization
- Fixed zooming directions
- Rewrote ``earclip_triangulation`` to fix triangulation
- Allowed sound_file_name to be taken in without extensions

New Features
^^^^^^^^^^^^

- Added :class:`~manimlib.animation.indication.VShowPassingFlash`
- Added ``COLORMAP_3B1B``
- Added some methods to coordinate system to access all axes ranges
  
  - :meth:`~manimlib.mobject.coordinate_systems.CoordinateSystem.get_origin`
  - :meth:`~manimlib.mobject.coordinate_systems.CoordinateSystem.get_all_ranges`
- Added :meth:`~manimlib.mobject.mobject.Mobject.set_color_by_rgba_func`
- Updated :class:`~manimlib.mobject.vector_field.VectorField` and :class:`~manimlib.mobject.vector_field.StreamLines`
- Allow ``3b1b_colormap`` as an option for :func:`~manimlib.utils.color.get_colormap_list`
- Return ``stroke_width`` as 1d array
- Added :meth:`~manimlib.mobject.svg.text_mobject.Text.get_parts_by_text`
- Use Text not TexText for Brace
- Update to Cross to make it default to variable stroke width
- Added :class:`~manimlib.animation.indication.FlashAround` and :class:`~manimlib.animation.indication.FlashUnder`
- Allowed configuration in ``Brace.get_text``
- Added :meth:`~manimlib.camera.camera.CameraFrame.reorient` for quicker changes to frame angle
- Added ``units`` to :meth:`~manimlib.camera.camera.CameraFrame.set_euler_angles`
- Allowed any ``VMobject`` to be passed into ``TransformMatchingTex``
- Removed double brace convention in ``Tex`` and ``TexText``
- Added support for debugger launch
- Added CLI flag ``--config_file`` to load configuration file manually
- Added ``tip_style`` to ``tip_config``
- Added ``MarkupText``
- Take in ``u_range`` and ``v_range`` as arguments to ``ParametricSurface``
- Added ``TrueDot``