Changelog
=========

Unreleased
----------

New Features
^^^^^^^^^^^^

- `10f850d <https://github.com/3b1b/manim/commit/10f850d0d9f971931cc85d44befe67dc842af6d>`__: Added CLI flag ``--log-level`` to specify log level


v1.2.0
------

Fixed bugs
^^^^^^^^^^

- `#1592 <https://github.com/3b1b/manim/pull/1592>`__: Fixed ``put_start_and_end_on`` in 3D
- `#1601 <https://github.com/3b1b/manim/pull/1601>`__: Fixed ``DecimalNumber``'s scaling issue
- `56df154 <https://github.com/3b1b/manim/commit/56df15453f3e3837ed731581e52a1d76d5692077>`__: Fixed bug with common range array used for all coordinate systems
- `8645894 <https://github.com/3b1b/manim/commit/86458942550c639a241267d04d57d0e909fcf252>`__: Fixed ``CoordinateSystem`` init bug
- `0dc096b <https://github.com/3b1b/manim/commit/0dc096bf576ea900b351e6f4a80c13a77676f89b>`__: Fixed bug for single-valued ``ValueTracker``
- `54ad355 <https://github.com/3b1b/manim/commit/54ad3550ef0c0e2fda46b26700a43fa8cde0973f>`__: Fixed bug with SVG rectangles
- `d45ea28 <https://github.com/3b1b/manim/commit/d45ea28dc1d92ab9c639a047c00c151382eb0131>`__: Fixed ``DotCloud.set_radii``
- `b543cc0 <https://github.com/3b1b/manim/commit/b543cc0e32d45399ee81638b6d4fb631437664cd>`__: Temporarily fixed bug for ``PMobject`` array resizing
- `5f878a2 <https://github.com/3b1b/manim/commit/5f878a2c1aa531b7682bd048468c72d2835c7fe5>`__: Fixed ``match_style``
- `719c81d <https://github.com/3b1b/manim/commit/719c81d72b00dcf49f148d7c146774b22e0fe348>`__: Fixed negative ``path_arc`` case
- `c726eb7 <https://github.com/3b1b/manim/commit/c726eb7a180b669ee81a18555112de26a8aff6d6>`__: Fixed bug with ``CoordinateSystem.get_lines_parallel_to_axis``
- `7732d2f <https://github.com/3b1b/manim/commit/7732d2f0ee10449c5731499396d4911c03e89648>`__: Fixed ``ComplexPlane`` -i display bug

New Features 
^^^^^^^^^^^^

- `#1598 <https://github.com/3b1b/manim/pull/1598>`__: Supported the elliptical arc command ``A`` for ``SVGMobject``
- `#1607 <https://github.com/3b1b/manim/pull/1607>`__: Added ``FlashyFadeIn``
- `#1607 <https://github.com/3b1b/manim/pull/1607>`__: Save triangulation 
- `#1625 <https://github.com/3b1b/manim/pull/1625>`__: Added new ``Code`` mobject
- `#1637 <https://github.com/3b1b/manim/pull/1637>`__: Add warnings and use rich to display log
- `bd356da <https://github.com/3b1b/manim/commit/bd356daa99bfe3134fcb192a5f72e0d76d853801>`__: Added ``VCube``
- `6d72893 <https://github.com/3b1b/manim/commit/6d7289338234acc6658b9377c0f0084aa1fa7119>`__: Supported ``ValueTracker`` to track vectors
- `3bb8f3f <https://github.com/3b1b/manim/commit/3bb8f3f0422a5dfba0da6ef122dc0c01f31aff03>`__: Added ``set_max_width``, ``set_max_height``, ``set_max_depth`` to ``Mobject``
- `a35dd5a <https://github.com/3b1b/manim/commit/a35dd5a3cbdeffa3891d5aa5f80287c18dba2f7f>`__: Added ``TracgTail``
- `acba13f <https://github.com/3b1b/manim/commit/acba13f4991b78d54c0bf93cce7ca3b351c25476>`__: Added ``Scene.point_to_mobject``
- `f84b8a6 <https://github.com/3b1b/manim/commit/f84b8a66fe9e8b3872e5c716c5c240c14bb555ee>`__: Added poly_fractal shader
- `b24ba19 <https://github.com/3b1b/manim/commit/b24ba19dec48ba4e38acbde8eec6d3a308b6ab83>`__: Added kwargs to ``TipableVMobject.set_length``
- `17c2772 <https://github.com/3b1b/manim/commit/17c2772b84abf6392a4170030e36e981de4737d0>`__: Added ``Mobject.replicate``
- `33fa76d <https://github.com/3b1b/manim/commit/33fa76dfac36e70bb5fad69dc6a336800c6dacce>`__: Added mandelbrot_fractal shader
- `f22a341 <https://github.com/3b1b/manim/commit/f22a341e8411eae9331d4dd976b5e15bc6db08d9>`__: Saved state before each embed
- `e10a752 <https://github.com/3b1b/manim/commit/e10a752c0001e8981038faa03be4de2603d3565f>`__: Allowed releasing of Textures
- `14fbed7 <https://github.com/3b1b/manim/commit/14fbed76da4b493191136caebb8a955e2d41265b>`__: Consolidated and renamed newton_fractal shader
- `6cdbe0d <https://github.com/3b1b/manim/commit/6cdbe0d67a11ab14a6d84840a114ae6d3af10168>`__: Hade ``ImageMoject`` remember the filepath to the Image

Refactor
^^^^^^^^

- `#1601 <https://github.com/3b1b/manim/pull/1601>`__: Changed back to simpler ``Mobject.scale`` implementation
- `b667db2 <https://github.com/3b1b/manim/commit/b667db2d311a11cbbca2a6ff511d2c3cf1675486>`__: Simplified ``Square``
- `40290ad <https://github.com/3b1b/manim/commit/40290ada8343f10901fa9151cbdf84689667786d>`__: Removed unused parameter ``triangulation_locked``
- `8647a64 <https://github.com/3b1b/manim/commit/8647a6429dd0c52cba14e971b8c09194a93cfd87>`__: Reimplemented ``Arrow``
- `d8378d8 <https://github.com/3b1b/manim/commit/d8378d8157040cd797cc47ef9576beffd8607863>`__: Used ``make_approximately_smooth`` for ``set_points_smoothly`` by default
- `7b4199c <https://github.com/3b1b/manim/commit/7b4199c674e291f1b84678828b63b6bd4fcc6b17>`__: Refactored to call ``_handle_scale_side_effects`` after scaling takes place
- `7356a36 <https://github.com/3b1b/manim/commit/7356a36fa70a8279b43ae74e247cbd43b2bfd411>`__: Refactored to only call ``throw_error_if_no_points`` once for ``get_start_and_end``
- `0787c4f <https://github.com/3b1b/manim/commit/0787c4f36270a6560b50ce3e07b30b0ec5f2ba3e>`__: Made sure framerate is 30 for previewed scenes
- `c635f19 <https://github.com/3b1b/manim/commit/c635f19f2a33e916509e53ded46f55e2afa8f5f2>`__: Pushed ``pixel_coords_to_space_coords`` to ``Window``
- `d5a88d0 <https://github.com/3b1b/manim/commit/d5a88d0fa457cfcf4cb9db417a098c37c95c7051>`__: Refactored to pass tuples and not arrays to uniforms
- `9483f26 <https://github.com/3b1b/manim/commit/9483f26a3b056de0e34f27acabd1a946f1adbdf9>`__: Refactored to copy uniform arrays in ``Mobject.copy``
- `ed1fc4d <https://github.com/3b1b/manim/commit/ed1fc4d5f94467d602a568466281ca2d0368b506>`__: Added ``bounding_box`` as exceptional key to point_cloud mobject
- `329d2c6 <https://github.com/3b1b/manim/commit/329d2c6eaec3d88bfb754b555575a3ea7c97a7e0>`__: Made sure stroke width is always a float


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