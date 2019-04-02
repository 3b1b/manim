import random

from colour import Color
import numpy as np

from manimlib.constants import PALETTE
from manimlib.constants import WHITE
from manimlib.utils.bezier import interpolate
from manimlib.utils.simple_functions import clip_in_place
from manimlib.utils.space_ops import normalize


def color_to_rgb(color):
    if isinstance(color, str):
        return hex_to_rgb(color)
    elif isinstance(color, Color):
        return np.array(color.get_rgb())
    else:
        raise Exception("Invalid color type")


def color_to_rgba(color, alpha=1):
    return np.array([*color_to_rgb(color), alpha])


def rgb_to_color(rgb):
    try:
        return Color(rgb=rgb)
    except:
        return Color(WHITE)


def rgba_to_color(rgba):
    return rgb_to_color(rgba[:3])


def rgb_to_hex(rgb):
    return "#" + "".join('%02x' % int(255 * x) for x in rgb)


def hex_to_rgb(hex_code):
    hex_part = hex_code[1:]
    if len(hex_part) == 3:
        "".join([2 * c for c in hex_part])
    return np.array([
        int(hex_part[i:i + 2], 16) / 255
        for i in range(0, 6, 2)
    ])


def invert_color(color):
    return rgb_to_color(1.0 - color_to_rgb(color))


def color_to_int_rgb(color):
    return (255 * color_to_rgb(color)).astype('uint8')


def color_to_int_rgba(color, opacity=1.0):
    alpha = int(255 * opacity)
    return np.append(color_to_int_rgb(color), alpha)


def color_gradient(reference_colors, length_of_output):
    if length_of_output == 0:
        return reference_colors[0]
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


def interpolate_color(color1, color2, alpha):
    rgb = interpolate(color_to_rgb(color1), color_to_rgb(color2), alpha)
    return rgb_to_color(rgb)


def average_color(*colors):
    rgbs = np.array(list(map(color_to_rgb, colors)))
    mean_rgb = np.apply_along_axis(np.mean, 0, rgbs)
    return rgb_to_color(mean_rgb)


def random_bright_color():
    color = random_color()
    curr_rgb = color_to_rgb(color)
    new_rgb = interpolate(
        curr_rgb, np.ones(len(curr_rgb)), 0.5
    )
    return Color(rgb=new_rgb)


def random_color():
    return random.choice(PALETTE)


def get_shaded_rgb(rgb, point, unit_normal_vect, light_source):
    to_sun = normalize(light_source - point)
    factor = 0.5 * np.dot(unit_normal_vect, to_sun)**3
    if factor < 0:
        factor *= 0.5
    result = rgb + factor
    clip_in_place(rgb + factor, 0, 1)
    return result
