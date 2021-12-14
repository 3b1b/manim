CONFIG dictionary
=================

What's CONFIG
-------------

``CONFIG`` dictionary is a feature of manim, which facilitates the inheritance 
and modification of parameters between parent and child classes.

| ``CONFIG`` dictionary 's processing is in ``manimlib/utils/config_ops.py``
| It can convert the key-value pairs in the ``CONFIG`` dictionary into class attributes and values

Generally, the first line of the ``.__init__()`` method in some basic class (``Mobject``, ``Animation``, 
etc.) will call this function ``digest_config(self, kwargs)`` to convert both 
the ``CONFIG`` dictionary and ``kwargs`` into attributes. Then it can be accessed 
directly through ``self.``, which simplifies the handling of inheritance between classes.

**An example**:

There are many class inheritance relationships in ``manimlib/mobject/geometry.py``

.. code-block:: python

    # Line 279
    class Circle(Arc):
        CONFIG = {
            "color": RED,
            "close_new_points": True,
            "anchors_span_full_range": False
        }

.. code-block:: python

    # Line 304
    class Dot(Circle):
        CONFIG = {
            "radius": DEFAULT_DOT_RADIUS,
            "stroke_width": 0,
            "fill_opacity": 1.0,
            "color": WHITE
        }

The ``Circle`` class uses the key-value pair ``"color": RED`` in the ``CONFIG`` 
dictionary to add the attribute ``self.color``.

At the same time, the ``Dot`` class also contains the key ``color`` in the 
``CONFIG`` dictionary, but the value is different. At this time, the priority will 
modify the attribute ``self.color`` to  ``WHITE``. 

CONFIG nesting
--------------

The ``CONFIG`` dictionary supports nesting, that is, the value of the key is also 
a dictionary, for example:

.. code-block:: python

    class Camera(object):
        CONFIG = {
            # configs
        }

.. code-block:: python

    class Scene(object):
        CONFIG = {
            "window_config": {},
            "camera_class": Camera,
            "camera_config": {},
            "file_writer_config": {},
            # other configs
        }

        def __init__(self, **kwargs):
            digest_config(self, kwargs)
            # some lines
            self.camera = self.camera_class(**self.camera_config)

The ``CONFIG`` dictionary of the ``Camera`` class contains many key-value pairs, 
and this class needs to be instantiated in the ``Scene`` class. For more convenient 
control, there is a special key-value pair in the Scene class ``"camera_config": {}``,
Its value is a dictionary, passed in as ``kwargs`` when initializing the ``Camera`` class 
to modify the value of the properties of the ``Camera`` class.

So the nesting of the ``CONFIG`` dictionary **essentially** passes in the value as ``kwargs``.
