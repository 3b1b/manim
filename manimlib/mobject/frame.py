from __future__ import annotations

from manimlib.constants import BLACK, GREY_E
from manimlib.constants import FRAME_HEIGHT
from manimlib.mobject.geometry import Rectangle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manimlib.typing import ManimColor


class ScreenRectangle(Rectangle):
    """
    A rectangle whose width is determined by a specified aspect ratio
    and height.

    ``ScreenRectangle`` extends ``Rectangle`` and is useful for representing
    screens, video frames, or other rectangular regions with a fixed
    width-to-height ratio.

    Parameters
    ----------
    aspect_ratio
        Ratio of the rectangle's width to its height, calculated as
        ``width / height``. Defaults to ``16.0 / 9.0``, corresponding
        to a widescreen 16:9 format.

    height
        Height of the rectangle in scene units. Defaults to ``4``.

    **kwargs
        Additional keyword arguments forwarded to ``Rectangle.__init__``,
        except ``width`` and ``height``, which are explicitly determined
        by ``aspect_ratio`` and ``height`` in this class.

    Notes
    -----
    The rectangle's width is calculated as::

        width = aspect_ratio * height

    Changing the height while keeping the aspect ratio constant scales
    both dimensions proportionally, preserving the specified ratio.

    Examples
    --------
    Create a default widescreen rectangle:

    >>> screen = ScreenRectangle()

    Create a rectangle with a height of 3 scene units:

    >>> screen = ScreenRectangle(height=3)

    Create a rectangle with a 4:3 aspect ratio:

    >>> screen = ScreenRectangle(aspect_ratio=4 / 3, height=3)

    Create a rectangle with customized styling:

    >>> screen = ScreenRectangle(
    ...     aspect_ratio=16 / 9,
    ...     height=4,
    ...     color=BLUE,
    ...     stroke_width=2,
    ... )

    See Also
    --------
    Rectangle
    """

    def __init__(
        self,
        aspect_ratio: float = 16.0 / 9.0,
        height: float = 4,
        **kwargs
    ):
        super().__init__(
            width=aspect_ratio * height,
            height=height,
            **kwargs
        )


class FullScreenRectangle(ScreenRectangle):
    """
    A screen-sized rectangle intended to cover the entire scene frame.

    ``FullScreenRectangle`` extends ``ScreenRectangle`` and uses the
    default scene frame height to create a rectangle with the inherited
    default aspect ratio. Its default styling produces a fully opaque,
    filled rectangle without a visible stroke.

    Parameters
    ----------
    height
        Height of the rectangle in scene units. Defaults to
        ``FRAME_HEIGHT``.

    fill_color
        Color used to fill the rectangle. Defaults to ``GREY_E``.

    fill_opacity
        Opacity of the fill, typically between 0 and 1. Defaults to 1,
        making the fill fully opaque.

    stroke_width
        Width of the rectangle's outline. Defaults to 0, disabling
        the visible stroke.

    **kwargs
        Additional keyword arguments forwarded through
        ``ScreenRectangle.__init__`` to ``Rectangle.__init__``.
        These can include other supported rectangle styling options.

    Notes
    -----
    The rectangle's width is determined by the inherited
    ``ScreenRectangle`` aspect ratio and the specified height:

        width = aspect_ratio * height

    The default aspect ratio is inherited from ``ScreenRectangle``
    and is 16:9. The default height is ``FRAME_HEIGHT``, so the
    result is intended to match the scene frame's dimensions under
    the corresponding frame aspect ratio.

    Examples
    --------
    Create a default full-screen rectangle:

    >>> background = FullScreenRectangle()

    Create a fully opaque black background:

    >>> background = FullScreenRectangle(fill_color=BLACK)

    Create a partially transparent background:

    >>> background = FullScreenRectangle(
    ...     fill_color=BLUE,
    ...     fill_opacity=0.5,
    ... )

    Create a rectangle with a visible outline:

    >>> background = FullScreenRectangle(
    ...     fill_color=GREY_E,
    ...     fill_opacity=1,
    ...     stroke_width=2,
    ... )

    See Also
    --------
    ScreenRectangle
    Rectangle
    """

    def __init__(
        self,
        height: float = FRAME_HEIGHT,
        fill_color: ManimColor = GREY_E,
        fill_opacity: float = 1,
        stroke_width: float = 0,
        **kwargs,
    ):
        super().__init__(
            height=height,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs
        )


class FullScreenFadeRectangle(FullScreenRectangle):
    """
    A full-screen rectangle with a semi-transparent fill, typically used
    to darken or fade the scene behind foreground objects.

    ``FullScreenFadeRectangle`` extends ``FullScreenRectangle`` and
    provides defaults suitable for overlay effects. By default, it uses
    a black fill with 70% opacity and no visible outline.

    Parameters
    ----------
    stroke_width
        Width of the rectangle's outline. Defaults to ``0.0``, disabling
        the visible stroke.

    fill_color
        Color used to fill the rectangle. Defaults to ``BLACK``.

    fill_opacity
        Opacity of the fill. Defaults to ``0.7``, making the rectangle
        partially transparent.

    **kwargs
        Additional keyword arguments accepted by the constructor.
        Note that this implementation does not forward ``kwargs`` to
        ``FullScreenRectangle.__init__``; only ``stroke_width``,
        ``fill_color``, and ``fill_opacity`` are passed to the parent.

    Notes
    -----
    The rectangle inherits its dimensions and aspect ratio from
    ``FullScreenRectangle`` and ``ScreenRectangle``. Its default
    semi-transparent black fill is useful for placing a visual overlay
    over a scene while keeping the underlying content visible.

    Examples
    --------
    Create a default fade overlay:

    >>> fade = FullScreenFadeRectangle()

    Create a lighter overlay:

    >>> fade = FullScreenFadeRectangle(
    ...     fill_color=GREY_E,
    ...     fill_opacity=0.4,
    ... )

    Create a more opaque colored overlay:

    >>> fade = FullScreenFadeRectangle(
    ...     fill_color=BLUE,
    ...     fill_opacity=0.8,
    ... )

    See Also
    --------
    FullScreenRectangle
    ScreenRectangle
    Rectangle
    """

    def __init__(
        self,
        stroke_width: float = 0.0,
        fill_color: ManimColor = BLACK,
        fill_opacity: float = 0.7,
        **kwargs,
    ):
        super().__init__(
            stroke_width=stroke_width,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
        )
