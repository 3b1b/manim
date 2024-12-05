from __future__ import annotations

import os
import tempfile
import appdirs


from manimlib.config import get_global_config
from manimlib.config import get_manim_dir
from manimlib.utils.file_ops import guarantee_existence


def get_directories() -> dict[str, str]:
    return get_global_config()["directories"]


def get_cache_dir() -> str:
    return get_directories()["cache"] or appdirs.user_cache_dir("manim")


def get_temp_dir() -> str:
    return get_directories()["temporary_storage"] or tempfile.gettempdir()


def get_downloads_dir() -> str:
    return guarantee_existence(os.path.join(get_temp_dir(), "manim_downloads"))


def get_output_dir() -> str:
    return guarantee_existence(get_directories()["output"])


def get_raster_image_dir() -> str:
    return get_directories()["raster_images"]


def get_vector_image_dir() -> str:
    return get_directories()["vector_images"]


def get_sound_dir() -> str:
    return get_directories()["sounds"]


def get_shader_dir() -> str:
    return os.path.join(get_manim_dir(), "manimlib", "shaders")
