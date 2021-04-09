What's new
==========

Usage changes of new version manim
----------------------------------

There are many changes in the new version of manim, and here are only the changes that 
may have an impact at the code writing level. 

Some of the changes here may not have any major impact on the use, and some changes 
that affect the use are not mentioned below.

This document is for reference only, see the source code for details.

- ``Animation``
  
  - Added ``Fade`` as the parent class of ``FadeIn`` and ``FadeOut``
  - ``FadeIn`` and ``FadeOut`` can be passed in ``shift`` and ``scale`` parameters
  - Deleted ``FadeInFrom, FadeInFromDown, FadeOutAndShift, FadeOutAndShiftDown, FadeInFromLarge``, these can be used ``FadeIn, FadeOut`` to achieve the same effect more easily
  - Added ``FadeTransform`` to cross fade between two objects, and subclass ``FadeTransformPieces``
  - Added ``CountInFrom(decimal_mob, source_number=0)`` to count ``decimal_mob`` from ``source_number`` to the current value
  - ``Rotating`` can directly pass in ``angle`` and ``axis`` without writing keywords ``angle=, axis=``
  - ``Rotate`` has become a subclass of ``Rotating``, and the distortion effect in ``Transform`` will not appear
  - Removed ``MoveCar`` animation
  - Added ``TransformMatchingShapes(mobject, target_mobject)`` and ``TransformMatchingTex(mobject, target_mobject)``
  
- ``Camera``

  - Removed all camera classes except ``Camera`` (``MappingCamera``, ``MovingCamera``, ``MultiCamera``) and all functions in ``ThreeDCamera``
  - Implemented ``CameraFrame`` (as a ``Mobject``)
  
    - Can be called by ``self.camera.frame`` in ``Scene``
    - All methods of ``Mobject`` can be used, such as ``.shift()``, ``.scale()``, etc.
    - Call ``.to_default_state()`` to place in the default position
    - Set the Euler angles of the camera by ``.set_euler_angles(theta, phi, gamma)``
    - Set three single Euler angles by ``.set_theta(theta)``, ``.set_phi(phi)``, ``.set_gamma(gamma)``
    - Use ``.increment_theta(dtheta)``, ``.increment_phi(dphi)``, ``.increment_gamma(gamma)`` to increase the three Euler angles by a certain value. Can be used to realize automatic rotation ``self.camera.frame.add_updater(lambda mob, dt: mob.increment_theta(0.1 * dt))``
  
  - ``Camera`` adds a light source, which is a ``Point``, which can be called by ``self.camera.light_source`` in ``Scene`` to move and so on. The default position is ``(- 10, 10, 10)``
  
- Delete ``Container``
- ``Mobject``
  
  - ``svg`` related
  
    - Added ``Checkmark`` and ``Exmark``
    - Some unnecessary classes have been removed from ``drawings.py``
    - Removed ``Code`` and ``Paragraph`` (by mistake)
    - ``TexMobject`` is renamed to ``Tex``, ``TextMobject`` is renamed to ``TexText``
    - ``font_size`` has been added to ``Tex``, ``TexText`` and ``Text``
    - ``Tex`` and ``TexText`` added ``isolate``, which is a list, which will be automatically split
  
  - Mobject ``types``
  
    - Added a new class ``Surface``, which is the parent class of ``ParametricSurface`` and ``TexturedSurface``.
    - Added the group ``SGroup`` for ``Surface``
    - Added ``TexturedSurface(uv_surface, image_file, dark_image_file=None)``, where ``uv_surface`` is a ``Surface``, ``image_file`` is the image to be posted, and ``dark_image_file`` is the image to be posted in the dark (default and ``image_file`` is the same)
    - Deleted ``Mobject1D``, ``Mobject2D``, ``PointCloudDot``
    - Added ``DotCloud`` (a ``PMobject``), which has been greatly optimized
    - Removed ``AbstractImageMobject``, ``ImageMobjectFromCamera``
    - Removed ``sheen`` from ``VMobject``
  
  - ``Mobject``
  
    - Added ``gloss`` and ``shadow``, which are the numbers between ``[0, 1]`` respectively. There are four methods of ``.get_gloss()``, ``.set_gloss(gloss)``, ``.get_shadow()``, ``.set_shadow(shadow)``
    - Added ``.get_grid(n_rows, n_cols)`` to copy into grid
    - Added ``.set_color_by_code(glsl_code)`` to use GLSL code to change the color
    - Added ``.set_color_by_xyz_func(glsl_snippet, min_value=-5.0, max_value=5.0, colormap="viridis")`` to pass in GLSL expression in the form of ``x,y,z``, the return value should be a floating point number
  
  - Coordinate system (including ``Axes``, ``ThreeDAxes``, ``NumberPlane``, ``ComplexPlane``)

    - No longer use ``x_min``, ``x_max``, ``y_min``, ``y_max``, but use ``x_range``, ``y_range`` as a ``np.array()``, containing three numbers ``np.array([ Minimum, maximum, step size])``
    - Added the abbreviation ``.i2gp(x, graph)`` of ``.input_to_graph_point(x, graph)``
    - Added some functions of the original ``GraphScene``
  
      - Added ``.get_v_line(point)``, ``.get_h_line(point)`` to return the line from ``point`` to the two coordinate axes, and specify the line type through the keyword argument of ``line_func`` (default ``DashedLine``)
      - Added ``.get_graph_label(graph, label, x, direction, buff, color)`` to return the label added to the image
      - Added ``.get_v_line_to_graph(x, graph)``, ``.get_h_line_to_graph(x, graph)`` to return the line from the point with the abscissa of ``x`` on the ``graph`` to the two- axis line
      - Added ``.angle_of_tangent(x, graph, dx=EPSILON)``, returns the inclination angle of ``graph`` at ``x``
      - Added ``.slope_of_tangent(x, graph, dx=EPSILON)``, returns the slope of tangent line of ``graph`` at ``x``
      - Added ``.get_tangent_line(x, graph, length=5)`` to return the tangent line of ``graph`` at ``x``
      - Added ``.get_riemann_rectangles(graph, x_range, dx, input_sample_type, ...)`` to return Riemann rectangles (a ``VGroup``)
  
    - The attribute ``number_line_config`` of ``Axes`` is renamed to ``axis_config``
    - ``Axes`` original ``.get_coordinate_labels(x_values, y_values)`` method was renamed to ``.add_coordinate_labels(x_values, y_values)`` (but it is not added to the screen)
    - ``.add_coordinate_labels(numbers)`` of ``ComplexPlane`` will directly add the coordinates to the screen
  
  - ``NumberLine``
  
    - No longer use ``x_min``, ``x_max``, ``tick_frequency``, but use ``x_range``, which is an array containing three numbers ``[min, max, step]``
    - The original ``label_direction`` attribute changed to the ``line_to_number_direction`` attribute
    - Replace ``tip_width`` and ``tip_height`` with ``tip_config`` (dictionary) attributes
    - The original ``exclude_zero_from_default`` attribute is modified to the ``numbers_to_exclude`` attribute (default is None)
    - The original ``.add_tick_marks()`` method was changed to the ``.add_ticks()`` method
    - Delete the ``.get_number_mobjects(*numbers)`` method, only use the ``.add_numbers(x_values=None, excluding=None)`` method
  
  - Three-dimensional objects
  
    - Added ``SurfaceMesh(uv_surface)``, pass in a ``Surface`` to generate its uv mesh
    - ``ParametricSurface`` no longer uses ``u_min, u_max, v_min, v_max``, but instead uses ``u_range, v_range``, which is a tuple (``(min, max)``), and ``resolution`` can be set larger, don’t worry Speed ​​issue
    - Added ``Torus``, controlled by ``r1, r2`` keyword parameters
    - Added ``Cylinder``, controlled by ``height, radius`` keyword parameters
    - Added ``Line3D`` (extremely thin cylinder), controlled by the ``width`` keyword parameter
    - Added ``Disk3D``, controlled by ``radius`` keyword parameter
    - Add ``Square3D``, controlled by ``side_length`` keyword parameter
    - Improved ``Cube`` and ``Prism``, the usage remains unchanged
  
  - Other objects
  
    - ``ParametricFunction`` is renamed to ``ParametricCurve``. Instead of using ``t_min, t_max, step_size``, use ``t_range``, which is an array of three numbers (``[t_min, t_max, step_size]``). ``dt`` was renamed to ``epsilon``. Other usage remains unchanged
    - All ``TipableVMobject`` can pass in ``tip_length`` to control the style of ``tip``
    - ``Line`` adds ``.set_points_by_ends(start, end, buff=0, path_arc=0)`` method
    - ``Line`` added ``.get_projection(point)`` to return the projection position of ``point`` on a straight line
    - ``Arrow`` adds three attributes of ``thickness, tip_width_ratio, tip_angle``
    - ``CubicBezier`` is changed to ``a0, h0, h1, a1``, that is, only a third-order Bezier curve is supported
    - ``Square`` can be initialized directly by passing in ``side_length`` instead of using the keyword ``side_length=``
    - ``always_redraw(func, *args, **kwargs)`` supports incoming parameters ``*args, **kwargs``
    - The ``digit_to_digit_buff`` property of ``DecimalNumber`` has been renamed to ``digit_buff_per_font_unit``, and the ``.scale()`` method has been improved
    - ``ValueTracker`` adds ``value_type`` attribute, the default is ``np.float64``
  
- ``Scene``
  
  - Removed all functions of ``GraphScene`` (moved to ``once_useful_constructs``), ``MovingCameraScene``, ``ReconfigurableScene``, ``SceneFromVideo``, ``ZoomedScene``, and ``ThreeDScene``. Because these can basically be achieved by adjusting ``CameraFrame`` (``self.camera.frame``)
  - Currently ``SampleSpaceScene`` and ``VectorScene`` have not been changed for the new version, so it is not recommended to use (only ``Scene`` is recommended)
  - Fix the export of gif, just use the ``-i`` option directly
  - Added the ``.interact()`` method, during which the mouse and keyboard can be used to continue the interaction, which will be executed by default after the scene ends
  - Added ``.embed()`` method, open iPython terminal to enter interactive mode
  - Added ``.save_state()`` method to save the current state of the scene
  - Added ``.restore()`` method to restore the entire scene to the saved state
  
- ``utils``
  
  - A series of functions related to second-order Bezier have been added to ``utils/bezier.py``
  - Added a function to read color map from ``matplotlib`` in ``utils/color.py``
  - Added a series of related functions for processing folders/custom styles/object families
  - ``resize_array``, ``resize_preserving_order``, ``resize_with_interpolation`` three functions have been added to ``utils/iterables.py``
  - The definition of ``smooth`` is updated in ``utils/rate_functions.py``
  - ``clip(a, min_a, max_a)`` function has been added to ``utils/simple_functions.py``
  - Some functions have been improved in ``utils/space_ops.py``, some functions for space calculation, and functions for processing triangulation have been added
  
- ``constants``
  
  - Fixed the aspect ratio of the screen to 16:9
  - Deleted the old gray series (``LIGHT_GREY``, ``GREY``, ``DARK_GREY``, ``DARKER_GREY``), added a new series of gray ``GREY_A`` ~ ``GREY_E``