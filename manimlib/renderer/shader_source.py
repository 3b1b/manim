from __future__ import annotations

import os
import re
from functools import lru_cache

from manimlib.renderer.uniform_block import uniform_block_code
from manimlib.utils.directories import get_shader_dir
from manimlib.utils.file_ops import find_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence
    import numpy as np


"""
Where a shader finds each thing it reads, grouped by how often it changes. These numbers are
the contract between the source generated here and the bind groups the renderer sets: a shader
declares them in the inserts, and what is below is what those agree with.
"""
FRAME_GROUP = 0
MOBJECT_GROUP = 1
RESOURCE_GROUP = 2
# Within the resource group: a mobject's records first, then a sampler and a texture for each
# image its kind names, see texture_binding_code
DATA_BINDING = 0
SAMPLER_BINDING = 1
FIRST_TEXTURE_BINDING = 2


def get_shader_code(
    filename: str,
    data_dtype: np.dtype,
    uniform_dtype: np.dtype,
    texture_names: tuple[str, ...] = (),
) -> str | None:
    """
    Reads a shader from file, filling in what its source depends on about the mobject it will
    be drawing: where the fields of a record sit, what it holds for the whole of itself, and
    which binding each image it named is at.

    Called once per kind of mobject, when its material is built, so nothing here is cached
    beyond the reading of the files themselves.
    """
    code = read_shader_file(filename)
    if code is None:
        return None
    return (
        code
        .replace("// DATA_LAYOUT", data_layout_code(data_dtype))
        .replace("// MOBJECT_UNIFORMS", uniform_block_code(uniform_dtype))
        .replace("// TEXTURES", texture_binding_code(texture_names))
    )


def data_layout_code(dtype: np.dtype) -> str:
    """
    Where each field of a record sits, in floats, for a shader to index by. No shader is handed
    vertex attributes: each reads the records of its buffer itself, as a flat array of floats,
    see inserts/read_data.wgsl.
    """
    return "\n".join([
        f"const DATA_STRIDE: u32 = {dtype.itemsize // 4}u;",
        *(
            f"const DATA_OFFSET_{name}: u32 = {dtype.fields[name][1] // 4}u;"
            for name in dtype.names
        ),
    ])


def texture_binding_code(texture_names: tuple[str, ...]) -> str:
    """
    How a shader declares the images its kind of mobject named, and the sampler they share,
    each from the binding it was actually put in.
    """
    if not texture_names:
        return ""
    lines = [f"@group({RESOURCE_GROUP}) @binding({SAMPLER_BINDING}) "
             f"var image_sampler: sampler;"]
    lines += [
        f"@group({RESOURCE_GROUP}) @binding({FIRST_TEXTURE_BINDING + index}) "
        f"var {name}: texture_2d<f32>;"
        for index, name in enumerate(texture_names)
    ]
    return "\n".join(lines)


@lru_cache()
def read_shader_file(filename: str) -> str | None:
    """The source of one shader, with the files it names by "#INSERT" pasted into it"""
    if not filename:
        return None

    try:
        filepath = find_file(
            filename,
            directories=[get_shader_dir(), "/"],
            extensions=[],
        )
    except IOError:
        return None

    with open(filepath, "r") as f:
        result = f.read()

    # Functions shared between shaders live in files of their own, named by "#INSERT" lines
    insertions = re.findall(r"^#INSERT .*\.wgsl$", result, flags=re.MULTILINE)
    for line in insertions:
        inserted_code = read_shader_file(
            os.path.join("inserts", line.replace("#INSERT ", ""))
        )
        result = result.replace(line, inserted_code)
    return result


def get_colormap_code(rgb_list: Sequence[float]) -> str:
    """A list of colors as a shader array literal, for a snippet coloring by a value"""
    colors = ", ".join("vec3f({}, {}, {})".format(*rgb) for rgb in rgb_list)
    return f"array<vec3f, {len(rgb_list)}>({colors})"
