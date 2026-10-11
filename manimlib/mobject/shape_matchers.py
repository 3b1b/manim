from __future__ import annotations

from colour import Color

from manimlib.config import manim_config
from manimlib.constants import BLACK, RED, YELLOW, DEFAULT_MOBJECT_COLOR
from manimlib.constants import DL, DOWN, DR, LEFT, RIGHT, UL, UR
from manimlib.constants import SMALL_BUFF
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence
    from manimlib.mobject.mobject import Mobject
    from manimlib.typing import ManimColor, Self


class SurroundingRectangle(Rectangle):
    """
    A rectangle that automatically resizes and repositions itself to surround
    a specified mobject, with a configurable buffer around its boundary.

    SurroundingRectangle is useful for highlighting, emphasizing, or visually
    grouping an object in a scene. It inherits the geometry and styling
    capabilities of :class:`Rectangle`.

    Parameters
    ----------
    mobject : Mobject
        The mobject to surround. The rectangle is sized and positioned around
        this object during initialization.
    buff : float, optional
        Extra spacing between the surrounded mobject and the rectangle's
        boundary. Defaults to ``SMALL_BUFF``.
    color : ManimColor, optional
        The rectangle's color. Defaults to ``YELLOW``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Rectangle`, allowing
        other supported rectangle properties to be configured.

    Attributes
    ----------
    mobject : Mobject
        The object currently being surrounded.
    buff : float
        The buffer used when positioning and sizing the rectangle.

    Methods
    -------
    surround(mobject, buff=None)
        Updates the target object and adjusts the rectangle to surround it.
        If ``buff`` is ``None``, the existing buffer is retained. Returns self.

    set_buff(buff)
        Updates the buffer and repositions and resizes the rectangle around
        the currently stored mobject. Returns self.

    Notes
    -----
    - The constructor immediately calls ``surround(mobject)`` to fit the
      rectangle around the target.
    - If the target is fixed in the frame, the rectangle is also fixed in
      the frame using ``fix_in_frame()``.
    - Calling ``surround()`` changes the stored target and can optionally
      change the buffer.
    - Calling ``set_buff()`` changes the spacing without changing the target.
    - The class inherits other geometry and styling methods from
      :class:`Rectangle`.
    - SurroundingRectangle does not automatically track later transformations
      of the target. To update the rectangle, call ``surround()`` again or
      use an appropriate updater.

    Examples
    --------
    Surround a text object with a yellow rectangle::

        text = Tex("Hello, Manim")
        rect = SurroundingRectangle(text)
        self.add(text, rect)

    Choose a custom buffer and color::

        text = Tex("Important")
        rect = SurroundingRectangle(
            text,
            buff=0.2,
            color=RED,
            stroke_width=3,
        )
        self.add(text, rect)

    Change the buffer after construction::

        text = Tex("Math")
        rect = SurroundingRectangle(text, buff=0.1)
        rect.set_buff(0.4)

    Surround a different object::

        first = Circle()
        second = Square()
        rect = SurroundingRectangle(first)
        rect.surround(second, buff=0.2)

    See Also
    --------
    Rectangle
    SurroundingRectangle.surround
    SurroundingRectangle.set_buff
    """

    def __init__(
        self,
        mobject: Mobject,
        buff: float = SMALL_BUFF,
        color: ManimColor = YELLOW,
        **kwargs
    ):
        super().__init__(color=color, **kwargs)
        self.buff = buff
        self.surround(mobject)
        if mobject.is_fixed_in_frame():
            self.fix_in_frame()

    def surround(self, mobject, buff=None) -> Self:
        self.mobject = mobject
        self.buff = buff if buff is not None else self.buff
        super().surround(mobject, self.buff)
        return self

    def set_buff(self, buff) -> Self:
        self.buff = buff
        self.surround(self.mobject)
        return self


class BackgroundRectangle(SurroundingRectangle):
    """
    A rectangle designed to provide a filled background behind a mobject.

    BackgroundRectangle inherits from :class:`SurroundingRectangle` and is
    commonly used to improve text readability, highlight content, or place
    a translucent background behind objects. By default, it uses the camera's
    background color, has no visible stroke, and has a partially opaque fill.

    Parameters
    ----------
    mobject : Mobject
        The mobject to surround with the background rectangle.
    color : ManimColor or None, optional
        The background rectangle's color. If ``None``, uses
        ``manim_config.camera.background_color``.
    stroke_width : float, optional
        Stroke width passed to the parent constructor. Defaults to ``0``.
        The overridden ``set_style()`` method forces the stroke width to zero.
    stroke_opacity : float, optional
        Stroke opacity passed to the parent constructor. Defaults to ``0``.
        The overridden ``set_style()`` method does not preserve this setting.
    fill_opacity : float, optional
        Initial fill opacity. Defaults to ``0.75``. This value is also stored
        as ``original_fill_opacity``.
    buff : float, optional
        Extra spacing around the target mobject. Defaults to ``0``, so the
        rectangle closely fits the target.
    **kwargs
        Additional keyword arguments forwarded through
        :class:`SurroundingRectangle` to :class:`Rectangle`.

    Attributes
    ----------
    original_fill_opacity : float
        The fill opacity provided during initialization. Used by
        ``pointwise_become_partial()`` to calculate the opacity of a partial
        representation.

    Methods
    -------
    pointwise_become_partial(mobject, a, b)
        Sets the fill opacity to ``b * original_fill_opacity`` and returns
        this object. The ``mobject`` and ``a`` arguments are not used by
        this implementation.

    set_style(stroke_color=None, stroke_width=None, fill_color=None,
              fill_opacity=None, family=True, **kwargs)
        Applies a fixed style through ``VMobject.set_style()``: black stroke
        color, zero stroke width, and black fill color. Only the supplied
        ``fill_opacity`` is forwarded. Other style arguments, including
        ``stroke_color``, ``stroke_width``, ``fill_color``, ``family``, and
        additional keyword arguments, do not change this fixed style.

    get_fill_color()
        Returns ``Color(self.color)``. This reports the object's ``color``
        attribute converted to a ``Color`` object; it does not directly query
        the fill color set by ``set_style()``.

    Notes
    -----
    - If ``color`` is omitted or ``None``, the rectangle takes its initial
      color from the configured camera background color.
    - The default buffer is zero, unlike the nonzero default used by
      ``SurroundingRectangle``.
    - ``original_fill_opacity`` preserves the initialization value even if
      the fill opacity is later changed.
    - ``pointwise_become_partial()`` uses the parameter ``b`` as a multiplier
      of the original opacity; it does not interpolate between ``a`` and
      ``b`` in this implementation.
    - The overridden ``set_style()`` intentionally restricts styling to a
      black fill and an invisible stroke, with configurable fill opacity.
    - Although the constructor accepts a ``color`` argument, ``get_fill_color()``
      returns the object's ``color`` attribute, which may differ from the
      black fill color explicitly applied by ``set_style()``.

    Examples
    --------
    Create a background rectangle behind text::

        text = Tex("Background")
        background = BackgroundRectangle(text)
        self.add(background, text)

    Specify a color and opacity::

        text = Tex("Highlighted text")
        background = BackgroundRectangle(
            text,
            color=BLUE,
            fill_opacity=0.5,
            buff=0.1,
        )
        self.add(background, text)

    Change the fill opacity::

        background = BackgroundRectangle(Tex("Example"))
        background.set_style(fill_opacity=0.3)

    See Also
    --------
    SurroundingRectangle
    Rectangle
    """

    def __init__(
        self,
        mobject: Mobject,
        color: ManimColor = None,
        stroke_width: float = 0,
        stroke_opacity: float = 0,
        fill_opacity: float = 0.75,
        buff: float = 0,
        **kwargs
    ):
        if color is None:
            color = manim_config.camera.background_color
        super().__init__(
            mobject,
            color=color,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
            fill_opacity=fill_opacity,
            buff=buff,
            **kwargs
        )
        self.original_fill_opacity = fill_opacity

    def pointwise_become_partial(self, mobject: Mobject, a: float, b: float) -> Self:
        self.set_fill(opacity=b * self.original_fill_opacity)
        return self

    def set_style(
        self,
        stroke_color: ManimColor | None = None,
        stroke_width: float | None = None,
        fill_color: ManimColor | None = None,
        fill_opacity: float | None = None,
        family: bool = True,
        **kwargs
    ) -> Self:
        # Unchangeable style, except for fill_opacity
        VMobject.set_style(
            self,
            stroke_color=BLACK,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=fill_opacity
        )
        return self

    def get_fill_color(self) -> Color:
        return Color(self.color)


class Cross(VGroup):
    """
    A cross-shaped group of two diagonal lines used to mark, reject, or cross
    out a mobject in a scene.

    Cross consists of two diagonal lines forming an X. The group is initially
    constructed from unit-diagonal lines, then resized to match the supplied
    mobject's bounding box and styled with the requested stroke color and width.

    Parameters
    ----------
    mobject : Mobject
        The mobject whose position and dimensions determine the cross's
        placement and size.
    stroke_color : ManimColor, optional
        Color applied to both diagonal lines. Defaults to ``RED``.
    stroke_width : float or Sequence[float], optional
        Stroke width passed to ``set_stroke()``. Defaults to ``[0, 6, 0]``.
        A sequence can specify different widths across the curves according
        to Manim's stroke-width handling.
    **kwargs
        Accepted by the constructor signature but not forwarded or otherwise
        used in this implementation.

    Attributes
    ----------
    Inherited from VGroup
        The two diagonal Line objects are stored as the group's submobjects.

    Notes
    -----
    - The two lines run from ``UL`` to ``DR`` and from ``UR`` to ``DL``,
      forming an X.
    - ``insert_n_curves(20)`` increases the curve structure before resizing
      and styling the group.
    - ``replace(mobject, stretch=True)`` positions and resizes the cross to
      match the target mobject's bounding box, allowing independent horizontal
      and vertical stretching.
    - The target mobject is not added to the group; it is used only to
      determine the cross's size and position.
    - The default stroke-width sequence is applied to the group's curves
      through ``set_stroke()``.
    - This constructor does not explicitly set a fill style or create an
      updater, so the cross does not automatically follow later transformations
      of the target mobject.

    Examples
    --------
    Cross out a text object::

        text = Tex("Incorrect")
        cross = Cross(text)
        self.add(text, cross)

    Customize the cross color and width::

        shape = Square()
        cross = Cross(
            shape,
            stroke_color=BLUE,
            stroke_width=4,
        )
        self.add(shape, cross)

    Cross out a larger object::

        circle = Circle(radius=2)
        cross = Cross(circle, stroke_color=RED)
        self.add(circle, cross)

    See Also
    --------
    VGroup
    Line
    SurroundingRectangle
    """

    def __init__(
        self,
        mobject: Mobject,
        stroke_color: ManimColor = RED,
        stroke_width: float | Sequence[float] = [0, 6, 0],
        **kwargs
    ):
        super().__init__(
            Line(UL, DR),
            Line(UR, DL),
        )
        self.insert_n_curves(20)
        self.replace(mobject, stretch=True)
        self.set_stroke(stroke_color, width=stroke_width)


class Underline(Line):
    """
    A horizontal line positioned beneath a mobject to visually underline it.

    Underline inherits from :class:`Line`. Its width is derived from the
    target mobject's width and a configurable stretch factor, and it is placed
    below the target with a configurable buffer.

    Parameters
    ----------
    mobject : Mobject
        The object to underline. Its width and position determine the
        underline's dimensions and placement.
    buff : float, optional
        Vertical distance between the mobject and the underline. Defaults to
        ``SMALL_BUFF``.
    stroke_color : ManimColor, optional
        Color of the underline. Defaults to ``DEFAULT_MOBJECT_COLOR``.
    stroke_width : float or Sequence[float], optional
        Stroke width or sequence of stroke widths passed to ``set_stroke()``.
        Defaults to ``[0, 3, 3, 0]``. If a sequence is supplied, additional
        curves are inserted based on its length before the stroke is applied.
    stretch_factor : float, optional
        Multiplier applied to the target mobject's width. Defaults to ``1.2``,
        making the underline 20% wider than the target.
    **kwargs
        Additional keyword arguments forwarded to the :class:`Line`
        constructor.

    Attributes
    ----------
    Inherited from Line
        The underline's endpoints, geometry, and stroke properties are
        provided by the parent class.

    Notes
    -----
    - The line is initially created from ``LEFT`` to ``RIGHT``.
    - If ``stroke_width`` is not a scalar ``float`` or ``int``, the
      implementation inserts ``len(stroke_width) - 2`` additional curves.
    - The requested stroke color and width are applied before the line is
      resized and positioned.
    - The final width is ``mobject.get_width() * stretch_factor``.
    - ``next_to(mobject, DOWN, buff=buff)`` positions the line below the
      target object.
    - The target mobject is not added to the underline, and no updater is
      created. Later changes to the target do not automatically reposition
      or resize the underline.
    - A zero-width target can produce a zero-width underline. The supplied
      stretch factor is not validated.

    Examples
    --------
    Underline a text object::

        text = Tex("Important result")
        underline = Underline(text)
        self.add(text, underline)

    Customize the underline's appearance::

        text = Tex("Theorem")
        underline = Underline(
            text,
            buff=0.15,
            stroke_color=BLUE,
            stroke_width=4,
            stretch_factor=1.3,
        )
        self.add(text, underline)

    Use a multiple stroke width::

        text = Tex("Definition")
        underline = Underline(text)
        underline.insert_n_curves(10)
        underline.set_stroke(width=[0, 2, 2, 0])
        self.add(text, underline)

    See Also
    --------
    Line
    Cross
    SurroundingRectangle
    """

    def __init__(
        self,
        mobject: Mobject,
        buff: float = SMALL_BUFF,
        stroke_color=DEFAULT_MOBJECT_COLOR,
        stroke_width: float | Sequence[float] = [0, 3, 3, 0],
        stretch_factor=1.2,
        **kwargs
    ):
        super().__init__(LEFT, RIGHT, **kwargs)
        if not isinstance(stroke_width, (float, int)):
            self.insert_n_curves(len(stroke_width) - 2)
        self.set_stroke(stroke_color, stroke_width)
        self.set_width(mobject.get_width() * stretch_factor)
        self.next_to(mobject, DOWN, buff=buff)
