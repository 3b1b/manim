from __future__ import annotations

from colour import Color
from colour import hex2rgb
from colour import rgb2hex
import numpy as np

from manimlib.constants import COLORMAP_3B1B
from manimlib.constants import WHITE
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import resize_with_interpolation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Union

    ManimColor = Union[str, Color]


def color_to_rgb(color: ManimColor) -> np.ndarray:
    if isinstance(color, str):
        return hex_to_rgb(color)
    elif isinstance(color, Color):
        return np.array(color.get_rgb())
    else:
        raise Exception("Invalid color type")


def color_to_rgba(color: ManimColor, alpha: float = 1.0) -> np.ndarray:
    return np.array([*color_to_rgb(color), alpha])


def rgb_to_color(rgb: Iterable[float]) -> Color:
    try:
        return Color(rgb=tuple(rgb))
    except ValueError:
        return Color(WHITE)


def rgba_to_color(rgba: Iterable[float]) -> Color:
    return rgb_to_color(tuple(rgba)[:3])


def rgb_to_hex(rgb: Iterable[float]) -> str:
    return rgb2hex(rgb, force_long=True).upper()


def hex_to_rgb(hex_code: str) -> np.ndarray:
    return np.array(hex2rgb(hex_code))


def invert_color(color: ManimColor) -> Color:
    return rgb_to_color(1.0 - color_to_rgb(color))


def color_to_int_rgb(color: ManimColor) -> np.ndarray:
    return (255 * color_to_rgb(color)).astype('uint8')


def color_to_int_rgba(color: ManimColor, opacity: float = 1.0) -> np.ndarray:
    alpha = int(255 * opacity)
    return np.array([*color_to_int_rgb(color), alpha])


def color_gradient(
    reference_colors: Iterable[ManimColor],
    length_of_output: int
) -> list[Color]:
    if length_of_output == 0:
        return []
    rgbs = list(map(color_to_rgb, reference_colors))
    alphas = np.linspace(0, (len(rgbs) - 1), length_of_output)
    floors = alphas.astype('int')
    alphas_mod1 = alphas % 1
    # End edge case
    alphas_mod1[-1] = 1
    floors[-1] = len(rgbs) - 2
    return [
        rgb_to_color(interpolate(rgbs[i], rgbs[i + 1], alpha))
        for i, alpha in zip(floors, alphas_mod1)
    ]


def interpolate_color(
    color1: ManimColor,
    color2: ManimColor,
    alpha: float
) -> Color:
    rgb = interpolate(color_to_rgb(color1), color_to_rgb(color2), alpha)
    return rgb_to_color(rgb)


def average_color(*colors: ManimColor) -> Color:
    rgbs = np.array(list(map(color_to_rgb, colors)))
    return rgb_to_color(rgbs.mean(0))


def random_color() -> Color:
    return Color(rgb=tuple(np.random.random(3)))


def random_bright_color() -> Color:
    color = random_color()
    return average_color(color, Color(WHITE))


def get_colormap_list(
    map_name: str = "viridis",
    n_colors: int = 9
) -> np.ndarray:
    """
    Options for map_name:
    3b1b_colormap
    magma
    inferno
    plasma
    viridis
    cividis
    twilight
    twilight_shifted
    turbo
    """
    from matplotlib.cm import get_cmap

    if map_name == "3b1b_colormap":
        rgbs = [color_to_rgb(color) for color in COLORMAP_3B1B]
    else:
        rgbs = get_cmap(map_name).colors  # Make more general?
    return resize_with_interpolation(np.array(rgbs), n_colors)
