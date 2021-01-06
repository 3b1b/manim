import numpy as np
from PIL import Image

from manimlib.utils.file_ops import find_file
from manimlib.utils.directories import get_raster_image_dir
from manimlib.utils.directories import get_vector_image_dir


def get_full_raster_image_path(image_file_name):
    return find_file(
        image_file_name,
        directories=[get_raster_image_dir()],
        extensions=[".jpg", ".png", ".gif"]
    )


def get_full_vector_image_path(image_file_name):
    return find_file(
        image_file_name,
        directories=[get_vector_image_dir()],
        extensions=[".svg", ".xdv"],
    )


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
