import numpy as np
import os
import itertools as it
from PIL import Image
import random

from manimlib.constants import *

from manimlib.animation.composition import AnimationGroup
from manimlib.animation.indication import ShowPassingFlash
from manimlib.mobject.geometry import Vector
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.color import color_to_rgb
from manimlib.utils.color import rgb_to_color
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import linear
from manimlib.utils.simple_functions import sigmoid
from manimlib.utils.space_ops import get_norm
# from manimlib.utils.space_ops import normalize


DEFAULT_SCALAR_FIELD_COLORS = [BLUE_E, GREEN, YELLOW, RED]


def get_colored_background_image(scalar_field_func,
                                 number_to_rgb_func,
                                 pixel_height=DEFAULT_PIXEL_HEIGHT,
                                 pixel_width=DEFAULT_PIXEL_WIDTH):
    ph = pixel_height
    pw = pixel_width
    fw = FRAME_WIDTH
    fh = FRAME_HEIGHT
    points_array = np.zeros((ph, pw, 3))
    x_array = np.linspace(-fw / 2, fw / 2, pw)
    x_array = x_array.reshape((1, len(x_array)))
    x_array = x_array.repeat(ph, axis=0)

    y_array = np.linspace(fh / 2, -fh / 2, ph)
    y_array = y_array.reshape((len(y_array), 1))
    y_array.repeat(pw, axis=1)
    points_array[:, :, 0] = x_array
    points_array[:, :, 1] = y_array
    scalars = np.apply_along_axis(scalar_field_func, 2, points_array)
    rgb_array = number_to_rgb_func(scalars.flatten()).reshape((ph, pw, 3))
    return Image.fromarray((rgb_array * 255).astype('uint8'))


def get_rgb_gradient_function(min_value=0, max_value=1,
                              colors=[BLUE, RED],
                              flip_alphas=True,  # Why?
                              ):
    rgbs = np.array(list(map(color_to_rgb, colors)))

    def func(values):
        alphas = inverse_interpolate(
            min_value, max_value, np.array(values)
        )
        alphas = np.clip(alphas, 0, 1)
        # if flip_alphas:
        #     alphas = 1 - alphas
        scaled_alphas = alphas * (len(rgbs) - 1)
        indices = scaled_alphas.astype(int)
        next_indices = np.clip(indices + 1, 0, len(rgbs) - 1)
        inter_alphas = scaled_alphas % 1
        inter_alphas = inter_alphas.repeat(3).reshape((len(indices), 3))
        result = interpolate(rgbs[indices], rgbs[next_indices], inter_alphas)
        return result
    return func


def get_color_field_image_file(scalar_func,
                               min_value=0, max_value=2,
                               colors=DEFAULT_SCALAR_FIELD_COLORS
                               ):
    # try_hash
    np.random.seed(0)
    sample_inputs = 5 * np.random.random(size=(10, 3)) - 10
    sample_outputs = np.apply_along_axis(scalar_func, 1, sample_inputs)
    func_hash = hash(
        str(min_value) + str(max_value) + str(colors) + str(sample_outputs)
    )
    file_name = "%d.png" % func_hash
    full_path = os.path.join(RASTER_IMAGE_DIR, file_name)
    if not os.path.exists(full_path):
        print("Rendering color field image " + str(func_hash))
        rgb_gradient_func = get_rgb_gradient_function(
            min_value=min_value,
            max_value=max_value,
            colors=colors
        )
        image = get_colored_background_image(scalar_func, rgb_gradient_func)
        image.save(full_path)
    return full_path


def move_along_vector_field(mobject, func):
    mobject.add_updater(
        lambda m, dt: m.shift(
            func(m.get_center()) * dt
        )
    )
    return mobject


def move_submobjects_along_vector_field(mobject, func):
    def apply_nudge(mob, dt):
        for submob in mob:
            x, y = submob.get_center()[:2]
            if abs(x) < FRAME_WIDTH and abs(y) < FRAME_HEIGHT:
                submob.shift(func(submob.get_center()) * dt)

    mobject.add_updater(apply_nudge)
    return mobject


def move_points_along_vector_field(mobject, func):
    def apply_nudge(self, dt):
        self.mobject.apply_function(
            lambda p: p + func(p) * dt
        )
    mobject.add_updater(apply_nudge)
    return mobject


# Mobjects

class VectorField(VGroup):
    CONFIG = {
        "delta_x": 0.5,
        "delta_y": 0.5,
        "x_min": int(np.floor(-FRAME_WIDTH / 2)),
        "x_max": int(np.ceil(FRAME_WIDTH / 2)),
        "y_min": int(np.floor(-FRAME_HEIGHT / 2)),
        "y_max": int(np.ceil(FRAME_HEIGHT / 2)),
        "min_magnitude": 0,
        "max_magnitude": 2,
        "colors": DEFAULT_SCALAR_FIELD_COLORS,
        # Takes in actual norm, spits out displayed norm
        "length_func": lambda norm: 0.45 * sigmoid(norm),
        "opacity": 1.0,
        "vector_config": {},
    }

    def __init__(self, func, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.func = func
        self.rgb_gradient_function = get_rgb_gradient_function(
            self.min_magnitude,
            self.max_magnitude,
            self.colors,
            flip_alphas=False
        )
        x_range = np.arange(
            self.x_min,
            self.x_max + self.delta_x,
            self.delta_x
        )
        y_range = np.arange(
            self.y_min,
            self.y_max + self.delta_y,
            self.delta_y
        )
        for x, y in it.product(x_range, y_range):
            point = x * RIGHT + y * UP
            self.add(self.get_vector(point))
        self.set_opacity(self.opacity)

    def get_vector(self, point, **kwargs):
        output = np.array(self.func(point))
        norm = get_norm(output)
        if norm == 0:
            output *= 0
        else:
            output *= self.length_func(norm) / norm
        vector_config = dict(self.vector_config)
        vector_config.update(kwargs)
        vect = Vector(output, **vector_config)
        vect.shift(point)
        fill_color = rgb_to_color(
            self.rgb_gradient_function(np.array([norm]))[0]
        )
        vect.set_color(fill_color)
        return vect


class StreamLines(VGroup):
    CONFIG = {
        # TODO, this is an awkward way to inherit
        # defaults to a method.
        "start_points_generator_config": {},
        # Config for choosing start points
        "x_min": -8,
        "x_max": 8,
        "y_min": -5,
        "y_max": 5,
        "delta_x": 0.5,
        "delta_y": 0.5,
        "n_repeats": 1,
        "noise_factor": None,
        # Config for drawing lines
        "dt": 0.05,
        "virtual_time": 3,
        "n_anchors_per_line": 100,
        "stroke_width": 1,
        "stroke_color": WHITE,
        "color_by_arc_length": True,
        # Min and max arc lengths meant to define
        # the color range, should color_by_arc_length be True
        "min_arc_length": 0,
        "max_arc_length": 12,
        "color_by_magnitude": False,
        # Min and max magnitudes meant to define
        # the color range, should color_by_magnitude be True
        "min_magnitude": 0.5,
        "max_magnitude": 1.5,
        "colors": DEFAULT_SCALAR_FIELD_COLORS,
        "cutoff_norm": 15,
    }

    def __init__(self, func, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.func = func
        dt = self.dt

        start_points = self.get_start_points(
            **self.start_points_generator_config
        )
        for point in start_points:
            points = [point]
            for t in np.arange(0, self.virtual_time, dt):
                last_point = points[-1]
                points.append(last_point + dt * func(last_point))
                if get_norm(last_point) > self.cutoff_norm:
                    break
            line = VMobject()
            step = max(1, int(len(points) / self.n_anchors_per_line))
            line.set_points_smoothly(points[::step])
            self.add(line)

        self.set_stroke(self.stroke_color, self.stroke_width)

        if self.color_by_arc_length:
            len_to_rgb = get_rgb_gradient_function(
                self.min_arc_length,
                self.max_arc_length,
                colors=self.colors,
            )
            for line in self:
                arc_length = line.get_arc_length()
                rgb = len_to_rgb([arc_length])[0]
                color = rgb_to_color(rgb)
                line.set_color(color)
        elif self.color_by_magnitude:
            image_file = get_color_field_image_file(
                lambda p: get_norm(func(p)),
                min_value=self.min_magnitude,
                max_value=self.max_magnitude,
                colors=self.colors,
            )
            self.color_using_background_image(image_file)

    def get_start_points(self):
        x_min = self.x_min
        x_max = self.x_max
        y_min = self.y_min
        y_max = self.y_max
        delta_x = self.delta_x
        delta_y = self.delta_y
        n_repeats = self.n_repeats
        noise_factor = self.noise_factor

        if noise_factor is None:
            noise_factor = delta_y / 2
        return np.array([
            x * RIGHT + y * UP + noise_factor * np.random.random(3)
            for n in range(n_repeats)
            for x in np.arange(x_min, x_max + delta_x, delta_x)
            for y in np.arange(y_min, y_max + delta_y, delta_y)
        ])


# TODO: Make it so that you can have a group of stream_lines
# varying in response to a changing vector field, and still
# animate the resulting flow
class ShowPassingFlashWithThinningStrokeWidth(AnimationGroup):
    CONFIG = {
        "n_segments": 10,
        "time_width": 0.1,
        "remover": True
    }

    def __init__(self, vmobject, **kwargs):
        digest_config(self, kwargs)
        max_stroke_width = vmobject.get_stroke_width()
        max_time_width = kwargs.pop("time_width", self.time_width)
        AnimationGroup.__init__(self, *[
            ShowPassingFlash(
                vmobject.deepcopy().set_stroke(width=stroke_width),
                time_width=time_width,
                **kwargs
            )
            for stroke_width, time_width in zip(
                np.linspace(0, max_stroke_width, self.n_segments),
                np.linspace(max_time_width, 0, self.n_segments)
            )
        ])


# TODO, this is untested after turning it from a
# ContinualAnimation into a VGroup
class AnimatedStreamLines(VGroup):
    CONFIG = {
        "lag_range": 4,
        "line_anim_class": ShowPassingFlash,
        "line_anim_config": {
            "run_time": 4,
            "rate_func": linear,
            "time_width": 0.3,
        },
    }

    def __init__(self, stream_lines, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.stream_lines = stream_lines
        for line in stream_lines:
            line.anim = self.line_anim_class(line, **self.line_anim_config)
            line.anim.begin()
            line.time = -self.lag_range * random.random()
            self.add(line.anim.mobject)

        self.add_updater(lambda m, dt: m.update(dt))

    def update(self, dt):
        stream_lines = self.stream_lines
        for line in stream_lines:
            line.time += dt
            adjusted_time = max(line.time, 0) % line.anim.run_time
            line.anim.update(adjusted_time / line.anim.run_time)
