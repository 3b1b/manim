import os
import tempfile

from manimlib.utils.file_ops import guarantee_existence
from manimlib.config import get_custom_defaults
from manimlib.config import get_manim_dir

PRE_COMPUTED_DIRS = {}


def get_directories():
    if not PRE_COMPUTED_DIRS:
        custom_defaults = get_custom_defaults()
        PRE_COMPUTED_DIRS.update(custom_defaults["directories"])

        # Unless user has specified otherwise, use the system default temp
        # directory for storing tex files, mobject_data, etc.
        if not PRE_COMPUTED_DIRS["temporary_storage"]:
            PRE_COMPUTED_DIRS["temporary_storage"] = tempfile.gettempdir()

        # Assumes all shaders are written into manimlib/shaders
        PRE_COMPUTED_DIRS["shaders"] = os.path.join(
            get_manim_dir(), "manimlib", "shaders"
        )
    return PRE_COMPUTED_DIRS


def get_temp_dir():
    return get_directories()["temporary_storage"]


def get_tex_dir():
    return guarantee_existence(os.path.join(get_temp_dir(), "Tex"))


def get_text_dir():
    return guarantee_existence(os.path.join(get_temp_dir(), "Text"))


def get_mobject_data_dir():
    return guarantee_existence(os.path.join(get_temp_dir(), "mobject_data"))


def get_output_dir():
    return guarantee_existence(get_directories()["output"])


def get_raster_image_dir():
    return get_directories()["raster_images"]


def get_vector_image_dir():
    return get_directories()["vector_images"]


def get_shader_dir():
    return get_directories()["shaders"]
