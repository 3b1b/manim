import os
import warnings
import re
import moderngl

from manimlib.constants import SHADER_DIR

# Mobjects that should be rendered with
# the same shader will be organized and
# clumped together based on keeping track
# of a dict holding all the relevant information
# to that shader


SHADER_INFO_KEYS = [
    "data",
    "vert",
    "geom",
    "frag",
    "texture_path",
    "render_primative",
]


def get_shader_info(data=None,
                    vert_file=None,
                    geom_file=None,
                    frag_file=None,
                    texture_path=None,
                    render_primative=moderngl.TRIANGLE_STRIP):
    return {
        key: value
        for key, value in zip(
            SHADER_INFO_KEYS,
            [
                data, vert_file, geom_file, frag_file,
                texture_path, str(render_primative)
            ]
        )
    }


def is_valid_shader_info(shader_info):
    data = shader_info["data"]
    return all([
        data is not None and len(data) > 0,
        shader_info["vert"],
        shader_info["frag"],
    ])


def shader_info_to_id(shader_info):
    # A unique id for a shader based on the
    # files holding its code and texture
    return "|".join([
        shader_info.get(key, "") or ""
        for key in SHADER_INFO_KEYS[1:]
    ])


def shader_id_to_info(sid):
    return {
        key: (value or None)
        for key, value in zip(
            SHADER_INFO_KEYS,
            [None, *sid.split("|")]
        )
    }


def same_shader_type(info1, info2):
    return all([
        info1[key] == info2[key]
        for key in [
            "vert",
            "geom",
            "frag",
            "texture_path",
            "render_primative",
        ]
    ])


def get_shader_code_from_file(filename):
    if not filename:
        return None

    filepath = os.path.join(SHADER_DIR, filename)
    if not os.path.exists(filepath):
        warnings.warn(f"No file at {filepath}")
        return

    with open(filepath, "r") as f:
        result = f.read()

    # To share functionality between shaders, some functions are read in
    # from other files an inserted into the relevant strings before
    # passing to ctx.program for compiling
    # Replace "#INSERT " lines with relevant code
    insertions = re.findall(r"^#INSERT .*\.glsl$", result, flags=re.MULTILINE)
    for line in insertions:
        inserted_code = get_shader_code_from_file(line.replace("#INSERT ", ""))
        result = result.replace(line, inserted_code)
    return result
