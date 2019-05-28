Mathematical Objects
====================

Everything that appears on screen in a manim video is a
:class:`~mobject.mobject.Mobject`, or Mathematical Object. A
:class:`~mobject.mobject.Mobject`'s appearance is determined by 3
factors:

* ``m.points``, an Nx3 ``numpy.array`` specifying how to draw ``m``
* ``m``'s style attributes, such as ``m.color``, ``m.stroke_width``, and
  ``m.fill_opacity``
* ``m.submobjects``, a list of :class:`~mobject.mobject.Mobject` instances that
  are considered part of ``m``
