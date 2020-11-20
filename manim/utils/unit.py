"""Implement the Unit class."""

import numpy as np

from .. import constants, config


def m(val):
    return val


def px(val):
    return val * config.frame_width / config.pixel_width


def pct(val, axis):
    if np.array_equal(axis, constants.X_AXIS):
        return val / 100 * config.frame_width
    if np.array_equal(axis, constants.Y_AXIS):
        return val / 100 * config.frame_height
    if np.array_equal(axis, constants.Z_AXIS):
        raise NotImplementedError('length of Z axis is undefined...')
