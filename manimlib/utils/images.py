import numpy as np
import os

from PIL import Image

from manimlib.constants import RASTER_IMAGE_DIR


def get_full_raster_image_path(image_file_name):
    possible_paths = [
        image_file_name,
        os.path.join(RASTER_IMAGE_DIR, image_file_name),
        os.path.join(RASTER_IMAGE_DIR, image_file_name + ".jpg"),
        os.path.join(RASTER_IMAGE_DIR, image_file_name + ".png"),
        os.path.join(RASTER_IMAGE_DIR, image_file_name + ".gif"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise IOError("File %s not Found" % image_file_name)


def drag_pixels(frames):
    curr = frames[0]
    new_frames = []
    for frame in frames:
        curr += (curr == 0) * np.array(frame)
        new_frames.append(np.array(curr))
    return new_frames


def invert_image(image):
    arr = np.array(image)
    arr = (255 * np.ones(arr.shape)).astype(arr.dtype) - arr
    return Image.fromarray(arr)
