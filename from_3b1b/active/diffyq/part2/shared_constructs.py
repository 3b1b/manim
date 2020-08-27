from manimlib.imports import *

TIME_COLOR = YELLOW
X_COLOR = GREEN


def get_heat_equation():
    pass


def temperature_to_color(temp, min_temp=-1, max_temp=1):
    colors = [BLUE, TEAL, GREEN, YELLOW, "#ff0000"]

    alpha = inverse_interpolate(min_temp, max_temp, temp)
    index, sub_alpha = integer_interpolate(
        0, len(colors) - 1, alpha
    )
    return interpolate_color(
        colors[index], colors[index + 1], sub_alpha
    )


def two_d_temp_func(x, y, t):
    return np.sum([
        c * np.sin(f * var) * np.exp(-(f**2) * t)
        for c, f, var in [
            (0.2, 1, x),
            (0.3, 3, x),
            (0.02, 5, x),
            (0.01, 7, x),
            (0.5, 2, y),
            (0.1, 10, y),
            (0.01, 20, y),
        ]
    ])
