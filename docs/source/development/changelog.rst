Changelog
=========

Unreleased
----------

Fixed bugs
^^^^^^^^^^

- `#1592 <https://github.com/3b1b/manim/pull/1592>`__: Fixed ``put_start_and_end_on`` in 3D
- `#1601 <https://github.com/3b1b/manim/pull/1601>`__: Fixed ``DecimalNumber``'s scaling issue

New Features 
^^^^^^^^^^^^

- `#1598 <https://github.com/3b1b/manim/pull/1598>`__: Supported the elliptical arc command ``A`` for ``SVGMobject``
- `#1607 <https://github.com/3b1b/manim/pull/1607>`__: Added ``FlashyFadeIn``
- `#1607 <https://github.com/3b1b/manim/pull/1607>`__: Save triangulation 
- `#1625 <https://github.com/3b1b/manim/pull/1625>`__: Added new ``Code`` mobject
- `bd356da <https://github.com/3b1b/manim/commit/bd356daa99bfe3134fcb192a5f72e0d76d853801>`__: Added ``VCube``
- `6d72893 <https://github.com/3b1b/manim/commit/6d7289338234acc6658b9377c0f0084aa1fa7119>`__: Supported ``ValueTracker`` to track vectors

Refactor
^^^^^^^^

- `#1601 <https://github.com/3b1b/manim/pull/1601>`__: Change back to simpler ``Mobject.scale`` implementation
- `b667db2 <https://github.com/3b1b/manim/commit/b667db2d311a11cbbca2a6ff511d2c3cf1675486>`__: Simplify ``Square``
- `40290ad <https://github.com/3b1b/manim/commit/40290ada8343f10901fa9151cbdf84689667786d>`__: Removed unused parameter ``triangulation_locked``

v1.1.0
-------

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