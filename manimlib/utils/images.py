from __future__ import annotations

import numpy as np
from PIL import Image

from manimlib.utils.directories import get_raster_image_dir
from manimlib.utils.directories import get_vector_image_dir
from manimlib.utils.file_ops import find_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable


def get_full_raster_image_path(image_file_name: str) -> str:
    return find_file(
        image_file_name,
        directories=[get_raster_image_dir()],
        extensions=[".jpg", ".jpeg", ".png", ".gif", ""]
    )


def get_full_vector_image_path(image_file_name: str) -> str:
    return find_file(
        image_file_name,
        directories=[get_vector_image_dir()],
        extensions=[".svg", ".xdv", ""],
    )


def invert_image(image: Iterable) -> Image.Image:
    arr = np.array(image)
    arr = (255 * np.ones(arr.shape)).astype(arr.dtype) - arr
    return Image.fromarray(arr)
