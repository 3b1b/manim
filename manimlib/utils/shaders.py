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
    # A structred array caring all of the points/color/lighting/etc. information
    # needed for the shader.
    "raw_data",
    # List of variable names corresponding to inputs of vertex shader
    "attributes",
    # Filename of vetex shader
    "vert",
    # Filename of geometry shader, if there is one
    "geom",
    # Filename of fragment shader
    "frag",
    # A dictionary mapping names of uniform variables
    "uniforms",
    # A dictionary mapping names (as they show up in)
    # the shader to filepaths for textures.
    "texture_paths",
    # Whether or not to apply depth test
    "depth_test",
    # E.g. moderngl.TRIANGLE_STRIP
    "render_primative",
]

# Exclude raw_data
SHADER_KEYS_FOR_ID = SHADER_INFO_KEYS[2:]


def get_shader_info(raw_data=None,
                    attributes=None,
                    vert_file=None,
                    geom_file=None,
                    frag_file=None,
                    uniforms=None,
                    texture_paths=None,
                    depth_test=False,
                    render_primative=moderngl.TRIANGLE_STRIP,
                    ):
    result = {
        "raw_data": raw_data,
        "attributes": attributes,
        "vert": vert_file,
        "geom": geom_file,
        "frag": frag_file,
        "uniforms": uniforms or dict(),
        "texture_paths": texture_paths or dict(),
        "depth_test": depth_test,
        "render_primative": str(render_primative),
    }
    # # A unique id for a shader
    # result["id"] = "|".join([str(result[key]) for key in SHADER_KEYS_FOR_ID])
    return result


def is_valid_shader_info(shader_info):
    raw_data = shader_info["raw_data"]
    return all([
        raw_data is not None and len(raw_data) > 0,
        shader_info["vert"],
        shader_info["frag"],
    ])


def shader_info_to_id(shader_info):
    # A unique id for a shader
    return "|".join([str(shader_info[key]) for key in SHADER_KEYS_FOR_ID])


def same_shader_type(info1, info2):
    return all([
        info1[key] == info2[key]
        for key in SHADER_KEYS_FOR_ID
    ])


def shader_info_to_program_code(shader_info):
    return {
        "vertex_shader": get_shader_code_from_file(shader_info["vert"]),
        "geometry_shader": get_shader_code_from_file(shader_info["geom"]),
        "fragment_shader": get_shader_code_from_file(shader_info["frag"]),
    }


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
