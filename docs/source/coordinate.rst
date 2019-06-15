Coordinate
==========

By default, the scene in manim is made up by 8 x 14 grid. The grid is addressed using a numpy
array in the form of [x, y, z]. For 2D animations only the x and y axes are used.

.. code-block:: python

  class DotMap(Scene):
      def construct(self):
          dots = dict()
          annos = dict()
          var_index = 0
          for x in range(-7, 8):
              for y in range(-4, 5):
                  annos[f"{x}{y}"] = TexMobject(f"({x}, {y})")
                  dots[f"{var_index}"] = Dot(np.array([x, y, 0]))
                  var_index = var_index + 1
          for anno, dot in zip(annos.values(), dots.values()):
              self.add(anno)
              self.add(dot)
              self.wait(0.2)
              self.remove(anno)

.. raw:: html

    <video width="700" height="394" controls>
        <source src="_static/coordinate/DotMap.mp4" type="video/mp4">
    </video>

.. note::
  You can place objects outside this boundary, but it won't show up in the render.

Using Coordinates
-----------------

Coordinates are used for creating geometries (`VMobject` in manim) and animations.

Here coordinates are used to create this Polygon

.. code-block:: python

  class CoorPolygon(Scene):
      def construct(self):
          for x in range(-7, 8):
              for y in range(-4, 5):
                  self.add(Dot(np.array([x, y, 0]), color=DARK_GREY))
          polygon = Polygon(
              np.array([3, 2, 0]),
              np.array([1, -1, 0]),
              np.array([-5, -4, 0]),
              np.array([-4, 4, 0]))
          self.add(polygon)


.. Image:: assets/coordinate/CoorPolygon.png
   :width: 700px

Coordinate Aliasing
-------------------

From some animations typing a ``np.array`` everytime you need a coordinate can be tedious.
Manim provides aliases to the most common coordinates::

  UP == np.array([0, 1, 0])
  DOWN == np.array([0, -1, 0])
  LEFT ==  np.array([-1, 0, 0])
  RIGHT == np.array([1, 0, 0])
  UL == np.array([-1, 1, 0])
  DL == np.array([-1, -1, 0])
  UR == np.array([1, 1, 0])
  DR == np.array([1, -1, 0])

Here coordinates are used for animations

.. code-block:: python

  class CoorAlias(Scene):
      def construct(self):
          for x in range(-7, 8):
              for y in range(-4, 5):
                  self.add(Dot(np.array([x, y, 0]), color=DARK_GREY))

          aliases = {
              "UP": UP,
              "np.array([0,1,0])": np.array([0, 1, 0]),
              "DOWN": DOWN,
              "np.array([0,-1,0])": np.array([0, -1, 0]),
              "LEFT": LEFT,
              "np.array([-1,0,0])": np.array([-1, 0, 0]),
              "RIGHT": RIGHT,
              "np.array([1,0,0])": np.array([1, 0, 0]),
              "UL": UL,
              "np.array([-1,1,0])": np.array([-1, 1, 0]),
              "DL": DL,
              "np.array([-1,-1,0])": np.array([-1, -1, 0]),
              "UR": UR,
              "np.array([1,1,0])": np.array([1, 1, 0]),
              "DR": DR,
              "np.array([1,-1,0])": np.array([1, -1, 0])}
          circle = Circle(color=RED, radius=0.5)
          self.add(circle)
          self.wait(0.5)

          for text, aliase in aliases.items():
              anno = TexMobject(f"\\texttt{{{text}}}")
              self.play(Write(anno, run_time=0.2))
              self.play(ApplyMethod(circle.shift, aliase))
              self.wait(0.2)
              self.play(FadeOut(anno, run_time=0.2))

.. raw:: html

    <video width="700" height="394" controls>
        <source src="_static/coordinate/CoorAlias.mp4" type="video/mp4">
    </video>

Coordinate Arithmetic
---------------------

Numpy array allows arithmetic operations::

  >>> numpy.array([2,2,0]) + 4
  array([6, 6, 4])

  >>> np.array([1, -3, 0]) + np.array([-4, 2, 0])
  array([-3, -1,  0])

  >>> np.array([2, 2, 0]) - np.array([3,6, 0])
  array([-1, -4,  0])

  >>> numpy.array([2,2,0]) - 3
  array([-1, -1, -3])

  >>> np.array([1, -3, 0]) * 3
  array([ 3, -9,  0])

  >>> numpy.array([2,2,0]) / 2
  array([1., 1., 0.])

  >>> numpy.array([2,2,0]) / numpy.array([1, 4, 0])
  __main__:1: RuntimeWarning: invalid value encountered in true_divide
  array([2. , 0.5, nan])

.. code-block:: python

  class CoorArithmetic(Scene):
      def construct(self):
          for x in range(-7, 8):
              for y in range(-4, 5):
                  self.add(Dot(np.array([x, y, 0]), color=DARK_GREY))

          circle = Circle(color=RED, radius=0.5)
          self.add(circle)
          self.wait(0.5)

          aliases = {
              "LEFT * 3": LEFT * 3,
              "UP + RIGHT / 2": UP + RIGHT / 2,
              "DOWN + LEFT * 2": DOWN + LEFT * 2,
              "RIGHT * 3.75 * DOWN": RIGHT * 3.75 * DOWN,
              # certain arithmetic won't work as you expected
              # In [4]: RIGHT * 3.75 * DOWN
              # Out[4]: array([ 0., -0.,  0.])
              "RIGHT * 3.75 + DOWN": RIGHT * 3.75 + DOWN}

          for text, aliase in aliases.items():
              anno = TexMobject(f"\\texttt{{{text}}}")
              self.play(Write(anno, run_time=0.2))
              self.play(ApplyMethod(circle.shift, aliase))
              self.wait(0.2)
              self.play(FadeOut(anno, run_time=0.2))

.. raw:: html

    <video width="700" height="394" controls>
        <source src="_static/coordinate/CoorArithmetic.mp4" type="video/mp4">
    </video>
