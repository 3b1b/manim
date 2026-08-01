from __future__ import annotations

import os
import re
from functools import lru_cache
import moderngl
from PIL import Image
import numpy as np

from manimlib.utils.directories import get_shader_dir
from manimlib.utils.file_ops import find_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Optional
    from manimlib.typing import UniformDict


# Global maps to reflect uniform status
PROGRAM_UNIFORM_MIRRORS: dict[int, dict[str, float | tuple]] = dict()
# Names each program turned out not to have, so they aren't looked up again
PROGRAM_ABSENT_UNIFORMS: dict[int, set[str]] = dict()
# Every program which has been compiled, so that uniforms shared by all of them,
# like those describing the camera, can be set once rather than once per mobject
ALL_PROGRAMS: list[moderngl.Program] = []


@lru_cache()
def image_path_to_texture(path: str, ctx: moderngl.Context) -> moderngl.Texture:
    im = Image.open(path).convert("RGBA")
    return ctx.texture(
        size=im.size,
        components=len(im.getbands()),
        data=im.tobytes(),
    )


@lru_cache()
def get_shader_program(
        ctx: moderngl.context.Context,
        vertex_shader: str,
        fragment_shader: Optional[str] = None,
) -> moderngl.Program:
    program = ctx.program(
        vertex_shader=vertex_shader,
        fragment_shader=fragment_shader,
    )
    ALL_PROGRAMS.append(program)
    return program


def set_shared_uniforms(uniforms: UniformDict) -> None:
    """
    Sets uniforms which hold for every program, e.g. those describing where the
    camera is. Doing this once a frame saves each mobject from pushing values it
    shares with all the others.
    """
    for program in ALL_PROGRAMS:
        for name, value in uniforms.items():
            set_program_uniform(program, name, value)


def set_program_uniform(
    program: moderngl.Program,
    name: str,
    value: float | tuple | np.ndarray
) -> bool:
    """
    Sets a program uniform, and also keeps track of a dictionary
    of previously set uniforms for that program so that it
    doesn't needlessly reset it, requiring an exchange with gpu
    memory, if it sees the same value again.

    Returns True if changed the program, False if it left it as is.
    """

    pid = id(program)
    if pid not in PROGRAM_UNIFORM_MIRRORS:
        PROGRAM_UNIFORM_MIRRORS[pid] = dict()
        PROGRAM_ABSENT_UNIFORMS[pid] = set()
    uniform_mirror = PROGRAM_UNIFORM_MIRRORS[pid]

    # Shaders which don't mention a uniform get compiled without it, and asking
    # for one that isn't there is expensive enough to be worth only doing once
    if name in PROGRAM_ABSENT_UNIFORMS[pid]:
        return False

    if type(value) is np.ndarray and value.ndim > 0:
        value = tuple(value.flatten())
    if uniform_mirror.get(name, None) == value:
        return False

    try:
        program[name].value = value
    except KeyError:
        PROGRAM_ABSENT_UNIFORMS[pid].add(name)
        return False
    uniform_mirror[name] = value
    return True


@lru_cache()
def get_shader_code_from_file(filename: str) -> str | None:
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

    # To share functionality between shaders, some functions are read in
    # from other files an inserted into the relevant strings before
    # passing to ctx.program for compiling
    # Replace "#INSERT " lines with relevant code
    insertions = re.findall(r"^#INSERT .*\.glsl$", result, flags=re.MULTILINE)
    for line in insertions:
        inserted_code = get_shader_code_from_file(
            os.path.join("inserts", line.replace("#INSERT ", ""))
        )
        result = result.replace(line, inserted_code)
    return result


def get_colormap_code(rgb_list: Sequence[float]) -> str:
    data = ",".join(
        "vec3({}, {}, {})".format(*rgb)
        for rgb in rgb_list
    )
    return f"vec3[{len(rgb_list)}]({data})"
