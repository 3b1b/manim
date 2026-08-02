from __future__ import annotations

import os
import ctypes
import re
from functools import lru_cache
import moderngl
import OpenGL.GL as gl
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
    A mobject's uniforms, which notes which of them have been set.

    Uniforms are sent to the gpu in a buffer belonging to the mobject, and only the
    ones which have changed need packing into it again. Animating one of them, say
    the opacity of a fill, otherwise has the other fifteen repacked for nothing.
    Since dict.update doesn't route through __setitem__, both are overridden here.

    Values are expected to be replaced rather than written into, since mutating one
    in place would go unnoticed. Anything that does so has to say which it was.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nothing has been sent yet, so everything counts as having changed
        self.changed: set[str] = set(self)

    def __setitem__(self, key, value):
        self.changed.add(key)
        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        # Which ones an update touched takes some untangling, and it is never done
        # per frame, so take all of them as having changed
        self.changed.update(self)


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


"""
A mobject's uniforms travel in one std140 block, written once per mobject rather
than one uniform at a time. Each kind of mobject declares its own block, starting
with the members every kind has, see inserts/vmobject_uniforms.glsl for an example.

Where each member of a block sits is asked of the driver once the program is
compiled, rather than worked out here, so that nothing has to reproduce std140's
rules about how members of different sizes pack together.
"""
MOBJECT_BLOCK_NAME = "MobjectUniforms"
# How many floats each kind of block member is made of. The matrix types are left
# out, since a block pads their columns in ways that packing would have to know of.
BLOCK_MEMBER_SIZES = {
    gl.GL_FLOAT: 1,
    gl.GL_FLOAT_VEC2: 2,
    gl.GL_FLOAT_VEC3: 3,
    gl.GL_FLOAT_VEC4: 4,
}


@lru_cache()
def get_block_layout(
    program: moderngl.Program,
    block_name: str
) -> tuple[int, dict[str, tuple[int, int]]] | None:
    """
    How many bytes a block takes up, and where each of its members goes: which float
    of the block it starts at, and how many of them it is made of. None if this
    program has no such block. Members a shader never reads get left out by the
    compiler, and so are missing here, which is no loss: there is nothing to be
    gained by sending a value nothing reads.

    A property of the program rather than of any mobject drawn with it, and asking
    costs a call into the driver per member, so it is asked once per program. Every
    mobject of a kind shares its programs, so that is once rather than thousands.
    """
    glo = program.glo
    index = gl.glGetUniformBlockIndex(glo, block_name)
    if index == gl.GL_INVALID_INDEX:
        return None

    def block_property(enum, length=1):
        result = (ctypes.c_int * length)()
        gl.glGetActiveUniformBlockiv(glo, index, enum, result)
        return list(result)

    size = block_property(gl.GL_UNIFORM_BLOCK_DATA_SIZE)[0]
    count = block_property(gl.GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS)[0]
    if count == 0:
        return size, dict()
    members = block_property(gl.GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES, count)

    indices = (ctypes.c_uint * count)(*members)
    offsets = (ctypes.c_int * count)()
    types = (ctypes.c_int * count)()
    gl.glGetActiveUniformsiv(glo, count, indices, gl.GL_UNIFORM_OFFSET, offsets)
    gl.glGetActiveUniformsiv(glo, count, indices, gl.GL_UNIFORM_TYPE, types)

    layout = dict()
    for member, offset, member_type in zip(members, offsets, types):
        name = gl.glGetActiveUniform(glo, member)[0]
        name = name.decode() if isinstance(name, bytes) else name
        if member_type not in BLOCK_MEMBER_SIZES:
            raise ValueError(f"No packing this block\'s {name} into floats")
        layout[name] = (offset // 4, BLOCK_MEMBER_SIZES[member_type])
    return size, layout


@lru_cache()
def get_shader_code(
    filename: str,
    data_layout: tuple[int, tuple[tuple[str, int], ...]] | None,
) -> str | None:
    """
    Reads a shader from file, filling in where the fields of a vertex record sit for
    those shaders which read the buffer themselves. That is the only thing about a
    shader's source which depends on the mobject it will be drawing.
    """
    code = get_shader_code_from_file(filename)
    if code is None:
        return None
    return code.replace("// DATA_LAYOUT", get_data_layout_code(data_layout))


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
