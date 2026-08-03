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
from manimlib.utils.structured_array import StructuredArray
from manimlib.utils.file_ops import find_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Sequence, Optional
    from manimlib.typing import UniformDict


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


def get_shared_uniform(name: str) -> float | tuple | None:
    """
    One of the values which hold for every program, e.g. where the camera is, as it was
    last set for the frame being drawn. None before anything has set them. See
    set_shared_uniforms.
    """
    return SHARED_UNIFORMS.get(name, None)


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


def set_program_sampler(program: moderngl.Program, name: str, unit: int) -> bool:
    """
    Points one of a program's samplers at a texture unit.

    This goes through raw GL rather than moderngl, which takes the assignment and
    reports it back, but leaves the driver's own value at zero, for programs which use
    gl_VertexID. This driver counts that among a program's active uniforms, and it is
    the ones reading their vertices out of a buffer which use it. Every sampler
    happened to want unit zero, which is where they all start, until surfaces began
    reading a buffer alongside their textures.
    """
    pid = id(program)
    if pid not in PROGRAM_UNIFORM_MIRRORS:
        PROGRAM_UNIFORM_MIRRORS[pid] = dict()
        PROGRAM_ABSENT_UNIFORMS[pid] = set()
    if name in PROGRAM_ABSENT_UNIFORMS[pid]:
        return False
    if PROGRAM_UNIFORM_MIRRORS[pid].get(name, None) == unit:
        return False

    try:
        location = program[name].location
    except KeyError:
        PROGRAM_ABSENT_UNIFORMS[pid].add(name)
        return False
    gl.glProgramUniform1i(program.glo, location, unit)
    PROGRAM_UNIFORM_MIRRORS[pid][name] = unit
    return True


"""
A mobject's uniforms travel in one std140 block, written once per mobject rather than
one uniform at a time. Each kind of mobject declares its own block, starting with the
members every kind has, see inserts/vmobject_uniforms.glsl for an example, and lays
out a matching dtype with uniform_block_dtype, see Mobject.uniform_dtype.
"""
MOBJECT_BLOCK_NAME = "MobjectUniforms"
# What every mobject holds, whatever kind it is, as a name and a number of floats.
# Mirrors inserts/common_uniform_members.glsl, and comes first in every block for the
# same reason it does there: so the inserts reading them work wherever they are used.
COMMON_UNIFORMS = (
    ("is_fixed_in_frame", 1),
    ("shading", 3),
    ("clip_plane0", 4),
    ("clip_plane1", 4),
    ("clip_plane2", 4),
    ("clip_plane3", 4),
)
# What a block member of each size is called in a shader. Anything wider than a vec4,
# a matrix say, is left out, since a block pads their columns in ways this would have
# to know about.
BLOCK_MEMBER_TYPES = {1: "float", 2: "vec2", 3: "vec3", 4: "vec4"}
GL_MEMBER_SIZES = {
    gl.GL_FLOAT: 1,
    gl.GL_FLOAT_VEC2: 2,
    gl.GL_FLOAT_VEC3: 3,
    gl.GL_FLOAT_VEC4: 4,
}


def uniform_block_dtype(*members: tuple[str, int]) -> np.dtype:
    """
    Lays out members, each given as a name and how many floats it holds, exactly as
    std140 does, so that a mobject's uniforms can be handed to the gpu as they sit
    rather than packed one member at a time.

    The rules being reproduced are that a member is aligned to its own size, rounded
    up to four floats for anything wider than two, and that the block as a whole is
    rounded up to four floats as well. What that alignment skips over is declared as a
    field of its own rather than left as a gap in the dtype, since numpy does not carry
    the contents of a gap over when copying an array, which would leave whatever the
    memory happened to hold to be compared against and sent to the gpu.
    """
    names: list[str] = []
    formats: list[Any] = []

    def add(name: str, size: int) -> None:
        names.append(name)
        formats.append(np.float32 if size == 1 else (np.float32, (size,)))

    size_so_far = 0
    for name, size in members:
        if size not in BLOCK_MEMBER_TYPES:
            raise ValueError(f"No room in a block for {name}, of {size} floats")
        skipped = -size_so_far % (size if size <= 2 else 4)
        if skipped:
            add(f"_pad{len(names)}", skipped)
        add(name, size)
        size_so_far += skipped + size
    if -size_so_far % 4:
        add(f"_pad{len(names)}", -size_so_far % 4)
    # Left to pack the fields itself, numpy places them back to back, which is where
    # the padding above has been chosen to put them
    return np.dtype({"names": names, "formats": formats})


def uniform_block_code(dtype: np.dtype) -> str:
    """
    How a dtype would be written as a block, for saying what a shader ought to
    declare when it turns out not to match.
    """
    lines = []
    for name in dtype.names:
        if name.startswith("_"):
            # Alignment is the shader compiler's own business, and writing the padding
            # it implies would only push everything after it further along
            continue
        shape = dtype.fields[name][0].shape
        size = shape[0] if shape else 1
        lines.append(f"    {BLOCK_MEMBER_TYPES[size]} {name};")
    return "\n".join(lines)


class Uniforms(StructuredArray):
    """
    A mobject's uniforms: one value each for the whole of it, laid out to match the
    block its shaders declare. Reading one gives the value itself, rather than the
    single row of the array holding it.
    """

    def __init__(self, dtype: np.dtype):
        super().__init__(dtype, length=1)

    def __getitem__(self, key: str) -> Any:
        return self.array[key][0]

    def interpolate(self, uniforms1: Uniforms, uniforms2: Uniforms, alpha: float) -> None:
        if not self.array.dtype == uniforms1.array.dtype == uniforms2.array.dtype:
            # Different kinds of mobject, so only what they have in common carries over
            for key in self:
                if key in uniforms1 and key in uniforms2:
                    self[key] = (1 - alpha) * uniforms1[key] + alpha * uniforms2[key]
            return
        floats1 = uniforms1.floats
        floats2 = uniforms2.floats
        # Most transformations leave every uniform alone, e.g. moving a mobject
        # without restyling it, and writing values equal to those already here would
        # have the buffer sent again each frame for nothing
        if np.array_equal(floats1, floats2) and np.array_equal(self.floats, floats1):
            return
        self.floats[:] = (1 - alpha) * floats1 + alpha * floats2
        self.note_change()


@lru_cache()
def check_uniform_block(program: moderngl.Program, dtype: np.dtype) -> bool:
    """
    Whether a program declares the mobject block at all, and if it does, that its
    members sit exactly where the dtype says they do.

    Nothing needs this to render, since std140's layout is what uniform_block_dtype
    reproduces, but a shader's block and a mobject's uniform_dtype drifting apart
    would otherwise show up as a wrongly drawn mobject rather than as an error. It
    costs a handful of calls into the driver, once per program.
    """
    glo = program.glo
    index = gl.glGetUniformBlockIndex(glo, MOBJECT_BLOCK_NAME)
    if index == gl.GL_INVALID_INDEX:
        return False

    def block_property(enum, length=1):
        result = (ctypes.c_int * length)()
        gl.glGetActiveUniformBlockiv(glo, index, enum, result)
        return list(result)

    count = block_property(gl.GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS)[0]
    members = block_property(gl.GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES, count)
    indices = (ctypes.c_uint * count)(*members)
    offsets = (ctypes.c_int * count)()
    types = (ctypes.c_int * count)()
    gl.glGetActiveUniformsiv(glo, count, indices, gl.GL_UNIFORM_OFFSET, offsets)
    gl.glGetActiveUniformsiv(glo, count, indices, gl.GL_UNIFORM_TYPE, types)

    for member, offset, member_type in zip(members, offsets, types):
        name = gl.glGetActiveUniform(glo, member)[0]
        name = name.decode() if isinstance(name, bytes) else name
        # Members a shader never reads get left out by the compiler, which is no
        # loss: there is nothing to be gained by reading a value nothing uses
        field = dtype.fields.get(name)
        size = GL_MEMBER_SIZES.get(member_type)
        shape = field[0].shape if field else None
        if field is None or size is None or size != (shape[0] if shape else 1) \
                or field[1] != offset:
            raise ValueError(
                f"The {MOBJECT_BLOCK_NAME} block this shader declares does not match "
                f"the uniforms of the mobject drawn with it, starting at {name}. "
                f"What the mobject holds would be declared as:\n"
                f"layout (std140) uniform {MOBJECT_BLOCK_NAME} {{\n"
                f"{uniform_block_code(dtype)}\n}};"
            )
    return True


@lru_cache()
def get_shader_code(
    filename: str,
    data_layout: tuple[int, tuple[tuple[str, int], ...]],
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


def get_data_layout_code(data_layout: tuple[int, tuple[tuple[str, int], ...]]) -> str:
    """
    Constants describing where each field of a vertex record sits within the buffer, in
    units of floats, every shader indexing into it itself.
    """
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
