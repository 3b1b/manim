constants
=========

The ``constants.py`` in the ``manimlib`` folder defines the constants 
needed when running manim. Some constants are not explained here because 
they are only used inside manim.

Frame and pixel shape
---------------------

These values will be determined based on the ``camera`` configuration in default_config.yml or custom_config.yml

.. code-block:: python

    ASPECT_RATIO
    FRAME_HEIGHT
    FRAME_WIDTH
    FRAME_Y_RADIUS
    FRAME_X_RADIUS

    DEFAULT_PIXEL_HEIGHT
    DEFAULT_PIXEL_WIDTH
    DEFAULT_FPS

Buffs
-----

These values will be determined based on the ``size`` configuration in default_config.yml or custom_config.yml


.. code-block:: python

    SMALL_BUFF
    MED_SMALL_BUFF
    MED_LARGE_BUFF
    LARGE_BUFF

    DEFAULT_MOBJECT_TO_EDGE_BUFF
    DEFAULT_MOBJECT_TO_MOBJECT_BUFF

Coordinates
-----------

manim uses three-dimensional coordinates and uses the type of ``ndarray``

.. code-block:: python

    ORIGIN = np.array((0., 0., 0.))
    UP = np.array((0., 1., 0.))
    DOWN = np.array((0., -1., 0.))
    RIGHT = np.array((1., 0., 0.))
    LEFT = np.array((-1., 0., 0.))
    IN = np.array((0., 0., -1.))
    OUT = np.array((0., 0., 1.))
    X_AXIS = np.array((1., 0., 0.))
    Y_AXIS = np.array((0., 1., 0.))
    Z_AXIS = np.array((0., 0., 1.))

    # Useful abbreviations for diagonals
    UL = UP + LEFT
    UR = UP + RIGHT
    DL = DOWN + LEFT
    DR = DOWN + RIGHT

    TOP = FRAME_Y_RADIUS * UP
    BOTTOM = FRAME_Y_RADIUS * DOWN
    LEFT_SIDE = FRAME_X_RADIUS * LEFT
    RIGHT_SIDE = FRAME_X_RADIUS * RIGHT

Mathematical constant
---------------------

.. code-block:: python

   PI = np.pi
   TAU = 2 * PI
   DEGREES = TAU / 360

Text
----

.. code-block:: python

    NORMAL = "NORMAL"
    ITALIC = "ITALIC"
    OBLIQUE = "OBLIQUE"
    BOLD = "BOLD"

Colours
-------

Color constants are determined based on the ``color`` configuration in default_config.yml or custom_config.yml

Here are the preview of default colours. (Modified from 
`elteoremadebeethoven <https://elteoremadebeethoven.github.io/manim_3feb_docs.github.io/html/_static/colors/colors.html>`_)

.. raw:: html

    <div style="float: left;">
    <h3>BLUE</h3>
    <div class="colors BLUE_E"><p class="color-text">BLUE_E</p></div>
    <div class="colors BLUE_D"><p class="color-text">BLUE_D</p></div>
    <div class="colors BLUE_C"><p class="color-text">BLUE_C</p></div>
    <div class="colors BLUE_B"><p class="color-text">BLUE_B</p></div>
    <div class="colors BLUE_A"><p class="color-text">BLUE_A</p></div>
    </div>
    <div style="float: left;">
    <h3>TEAL</h3>
    <div class="colors TEAL_E"><p class="color-text">TEAL_E</p></div>
    <div class="colors TEAL_D"><p class="color-text">TEAL_D</p></div>
    <div class="colors TEAL_C"><p class="color-text">TEAL_C</p></div>
    <div class="colors TEAL_B"><p class="color-text">TEAL_B</p></div>
    <div class="colors TEAL_A"><p class="color-text">TEAL_A</p></div>
    </div>
    <div style="float: left;">
    <h3>GREEN</h3>
    <div class="colors GREEN_E"><p class="color-text">GREEN_E</p></div>
    <div class="colors GREEN_D"><p class="color-text">GREEN_D</p></div>
    <div class="colors GREEN_C"><p class="color-text">GREEN_C</p></div>
    <div class="colors GREEN_B"><p class="color-text">GREEN_B</p></div>
    <div class="colors GREEN_A"><p class="color-text">GREEN_A</p></div>
    </div>
    <div style="float: left;">
    <h3>YELLOW</h3>
    <div class="colors YELLOW_E"><p class="color-text">YELLOW_E</p></div>
    <div class="colors YELLOW_D"><p class="color-text">YELLOW_D</p></div>
    <div class="colors YELLOW_C"><p class="color-text">YELLOW_C</p></div>
    <div class="colors YELLOW_B"><p class="color-text">YELLOW_B</p></div>
    <div class="colors YELLOW_A"><p class="color-text">YELLOW_A</p></div>
    </div>
    <div style="float: left;">
    <h3>GOLD</h3>
    <div class="colors GOLD_E"><p class="color-text">GOLD_E</p></div>
    <div class="colors GOLD_D"><p class="color-text">GOLD_D</p></div>
    <div class="colors GOLD_C"><p class="color-text">GOLD_C</p></div>
    <div class="colors GOLD_B"><p class="color-text">GOLD_B</p></div>
    <div class="colors GOLD_A"><p class="color-text">GOLD_A</p></div>
    </div>
    <div style="float: left;">
    <h3>RED</h3>
    <div class="colors RED_E"><p class="color-text">RED_E</p></div>
    <div class="colors RED_D"><p class="color-text">RED_D</p></div>
    <div class="colors RED_C"><p class="color-text">RED_C</p></div>
    <div class="colors RED_B"><p class="color-text">RED_B</p></div>
    <div class="colors RED_A"><p class="color-text">RED_A</p></div>
    </div>
    <div style="float: left;">
    <h3>MAROON</h3>
    <div class="colors MAROON_E"><p class="color-text">MAROON_E</p></div>
    <div class="colors MAROON_D"><p class="color-text">MAROON_D</p></div>
    <div class="colors MAROON_C"><p class="color-text">MAROON_C</p></div>
    <div class="colors MAROON_B"><p class="color-text">MAROON_B</p></div>
    <div class="colors MAROON_A"><p class="color-text">MAROON_A</p></div>
    </div>
    <div style="float: left;">
    <h3>PURPLE</h3>
    <div class="colors PURPLE_E"><p class="color-text">PURPLE_E</p></div>
    <div class="colors PURPLE_D"><p class="color-text">PURPLE_D</p></div>
    <div class="colors PURPLE_C"><p class="color-text">PURPLE_C</p></div>
    <div class="colors PURPLE_B"><p class="color-text">PURPLE_B</p></div>
    <div class="colors PURPLE_A"><p class="color-text">PURPLE_A</p></div>
    </div>
    <div style="float: left;">
    <h3>GREY</h3>
    <div class="colors GREY_E"><p class="color-text">GREY_E</p></div>
    <div class="colors GREY_D"><p class="color-text">GREY_D</p></div>
    <div class="colors GREY_C"><p class="color-text">GREY_C</p></div>
    <div class="colors GREY_B"><p class="color-text">GREY_B</p></div>
    <div class="colors GREY_A"><p class="color-text">GREY_A</p></div>
    </div>
    <div style="float: left;">
    <h3>Others</h3>
    <div class="colors WHITE"><p class="color-text" style="color: BLACK">WHITE</p></div>
    <div class="colors BLACK"><p class="color-text">BLACK</p></div>
    <div class="colors GREY_BROWN"><p class="color-text-small">GREY_BROWN</p></div>
    <div class="colors DARK_BROWN"><p class="color-text-small">DARK_BROWN</p></div>
    <div class="colors LIGHT_BROWN"><p class="color-text-small">LIGHT_BROWN</p></div>
    <div class="colors PINK"><p class="color-text">PINK</p></div>
    <div class="colors LIGHT_PINK"><p class="color-text-small">LIGHT_PINK</p></div>
    <div class="colors GREEN_SCREEN"><p class="color-text-small">GREEN_SCREEN</p></div>
    <div class="colors ORANGE"><p class="color-text">ORANGE</p></div>
    </div>
