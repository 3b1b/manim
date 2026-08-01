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


class Uniforms(dict):
    """
    A mobject's uniforms, which notes whenever one of them is set.

    Uniforms are sent to the gpu in a buffer belonging to the mobject, and that
    buffer only needs rewriting when a value has actually changed. Since dict.update
    doesn't route through __setitem__, both are overridden here.

    Values are expected to be replaced rather than written into, since mutating one
    in place would go unnoticed. Anything that does so has to say so itself.
    """
    changed: bool = True

    def __setitem__(self, key, value):
        self.changed = True
        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        self.changed = True
        super().update(*args, **kwargs)


# Global maps to reflect uniform status
PROGRAM_UNIFORM_MIRRORS: dict[int, dict[str, float | tuple]] = dict()
# Names each program turned out not to have, so they aren't looked up again
PROGRAM_ABSENT_UNIFORMS: dict[int, set[str]] = dict()
# Every program which has been compiled, so that uniforms shared by all of them,
# like those describing the camera, can be set once rather than once per mobject
ALL_PROGRAMS: list[moderngl.Program] = []
# The values last set for all of them, since programs are compiled on first use,
# which may well be partway through a frame
SHARED_UNIFORMS: dict[str, float | tuple] = dict()


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
    for name, value in SHARED_UNIFORMS.items():
        set_program_uniform(program, name, value)
    return program


def set_shared_uniforms(uniforms: UniformDict) -> None:
    """
    Sets uniforms which hold for every program, e.g. those describing where the
    camera is. Doing this once a frame saves each mobject from pushing values it
    shares with all the others.
    """
    SHARED_UNIFORMS.clear()
    SHARED_UNIFORMS.update(uniforms)
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


# The mobject's uniforms are gathered into one std140 block, given a vec4 slot
# each so that the layout is simply 16 bytes per slot
UNIFORM_BLOCK_NAME = "MobjectUniforms"
UNIFORM_SLOTS_NAME = "_mob_uniforms"
SWIZZLES = {1: "x", 2: "xy", 3: "xyz", 4: "xyzw"}


@lru_cache()
def get_shader_code(
    filename: str,
    uniform_slots: tuple[tuple[str, int], ...],
    data_layout: tuple[int, tuple[tuple[str, int], ...]] | None,
) -> str | None:
    """
    Reads a shader from file and fills in everything about it which depends on the
    shape of a mobject's data, rather than on any of the values in it.

    Namely, the mobject's uniforms are lifted out of their individual declarations
    and into one block, with a define apiece so that the shader can go on naming
    them, and shaders which read the vertex buffer themselves get constants
    describing where each of its fields sits. Since none of that varies between
    mobjects of a kind, the result is worth holding onto.
    """
    code = get_shader_code_from_file(filename)
    if code is None:
        return None
    code = code.replace("// DATA_LAYOUT", get_data_layout_code(data_layout))
    for name, _ in uniform_slots:
        code = re.sub(rf"^uniform\s+\w+\s+{name}\s*;$", "", code, flags=re.MULTILINE)
    block = get_uniform_block_code(uniform_slots)
    return code.replace("#version 330", "#version 330\n" + block, 1)


def get_uniform_block_code(uniform_slots: tuple[tuple[str, int], ...]) -> str:
    """
    Declares a block holding a mobject's uniforms, along with defines so that
    shaders can go on referring to each of them by name.
    """
    if not uniform_slots:
        return ""
    defines = [
        f"#define {name} {UNIFORM_SLOTS_NAME}[{index}].{SWIZZLES[size]}"
        for index, (name, size) in enumerate(uniform_slots)
    ]
    return "\n".join([
        f"layout (std140) uniform {UNIFORM_BLOCK_NAME} "
        f"{{ vec4 {UNIFORM_SLOTS_NAME}[{len(uniform_slots)}]; }};",
        *defines,
    ])


def get_data_layout_code(data_layout: tuple[int, tuple[tuple[str, int], ...]] | None) -> str:
    """
    Constants describing where each field of a vertex record sits within the
    buffer, in units of floats, for shaders which index into it themselves.
    """
    if data_layout is None:
        return ""
    stride, fields = data_layout
    return "\n".join([
        f"const int DATA_STRIDE = {stride};",
        *(f"const int DATA_OFFSET_{name} = {offset};" for name, offset in fields),
    ])


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
