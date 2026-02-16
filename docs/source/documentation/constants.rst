Constants
=========

The ``constants.py`` in ``manimlib`` defines all the constants needed when running Manim. 
Some constants are internal and not usually modified by users.

Frame and Pixel Shape
--------------------

These values are determined based on ``manim_config.camera`` in ``default_config.yml`` or ``custom_config.yml``:

.. code-block:: python

    DEFAULT_RESOLUTION: tuple[int, int] = manim_config.camera.resolution
    DEFAULT_PIXEL_WIDTH: int = DEFAULT_RESOLUTION[0]
    DEFAULT_PIXEL_HEIGHT: int = DEFAULT_RESOLUTION[1]

    ASPECT_RATIO: float = DEFAULT_PIXEL_WIDTH / DEFAULT_PIXEL_HEIGHT
    FRAME_HEIGHT: float = manim_config.sizes.frame_height
    FRAME_WIDTH: float = FRAME_HEIGHT * ASPECT_RATIO
    FRAME_SHAPE: tuple[float, float] = (FRAME_WIDTH, FRAME_HEIGHT)
    FRAME_Y_RADIUS: float = FRAME_HEIGHT / 2
    FRAME_X_RADIUS: float = FRAME_WIDTH / 2

Buffs
-----

Useful spacing values, configured in ``manim_config.sizes``:

.. code-block:: python

    SMALL_BUFF: float = manim_config.sizes.small_buff
    MED_SMALL_BUFF: float = manim_config.sizes.med_small_buff
    MED_LARGE_BUFF: float = manim_config.sizes.med_large_buff
    LARGE_BUFF: float = manim_config.sizes.large_buff

    DEFAULT_MOBJECT_TO_EDGE_BUFF: float = manim_config.sizes.default_mobject_to_edge_buff
    DEFAULT_MOBJECT_TO_MOBJECT_BUFF: float = manim_config.sizes.default_mobject_to_mobject_buff

Coordinates
-----------

Manim uses 3D coordinates (``ndarray``) for positioning:

.. code-block:: python

    ORIGIN: Vect3 = np.array([0., 0., 0.])
    UP: Vect3 = np.array([0., 1., 0.])
    DOWN: Vect3 = np.array([0., -1., 0.])
    RIGHT: Vect3 = np.array([1., 0., 0.])
    LEFT: Vect3 = np.array([-1., 0., 0.])
    IN: Vect3 = np.array([0., 0., -1.])
    OUT: Vect3 = np.array([0., 0., 1.])
    X_AXIS: Vect3 = RIGHT
    Y_AXIS: Vect3 = UP
    Z_AXIS: Vect3 = OUT
    NULL_POINTS = np.array([[0., 0., 0.]])

Diagonal shortcuts:

.. code-block:: python

    UL: Vect3 = UP + LEFT
    UR: Vect3 = UP + RIGHT
    DL: Vect3 = DOWN + LEFT
    DR: Vect3 = DOWN + RIGHT

Frame edges:

.. code-block:: python

    TOP: Vect3 = FRAME_Y_RADIUS * UP
    BOTTOM: Vect3 = FRAME_Y_RADIUS * DOWN
    LEFT_SIDE: Vect3 = FRAME_X_RADIUS * LEFT
    RIGHT_SIDE: Vect3 = FRAME_X_RADIUS * RIGHT

Angles
------

.. code-block:: python

    PI: float = np.pi
    TAU: float = 2 * PI
    DEG: float = TAU / 360
    DEGREES = DEG  # Older animations may use this
    RADIANS: float = 1

Text Styles
-----------

.. code-block:: python

    NORMAL: str = "NORMAL"
    ITALIC: str = "ITALIC"
    OBLIQUE: str = "OBLIQUE"
    BOLD: str = "BOLD"

Colours
-------

Color constants are determined based on the ``manim_config.colors`` configuration 
in ``default_config.yml`` or ``custom_config.yml``.

Here are the preview of default colours.

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
    <div class="colors PURE_RED"><p class="color-text">PURE_RED</p></div>
    <div class="colors PURE_GREEN"><p class="color-text">PURE_GREEN</p></div>
    <div class="colors PURE_BLUE"><p class="color-text">PURE_BLUE</p></div>
    </div>

    <div style="clear: both;"></div>