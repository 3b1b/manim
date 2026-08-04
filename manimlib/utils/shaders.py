from __future__ import annotations

import os
import re
from functools import lru_cache
import wgpu
from PIL import Image
import numpy as np

from manimlib.utils.directories import get_shader_dir
from manimlib.utils.structured_array import StructuredArray
from manimlib.utils.file_ops import find_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Sequence


@lru_cache()
def image_path_to_texture(path: str, device) -> Any:
    """An image on the gpu, for whatever samples it. Made once per path."""
    image = Image.open(path).convert("RGBA")
    pixels = np.asarray(image, dtype=np.uint8)
    texture = device.create_texture(
        size=(image.width, image.height, 1),
        format=wgpu.TextureFormat.rgba8unorm,
        usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST,
    )
    device.queue.write_texture(
        {"texture": texture, "mip_level": 0, "origin": (0, 0, 0)},
        pixels,
        {"offset": 0, "bytes_per_row": 4 * image.width, "rows_per_image": image.height},
        (image.width, image.height, 1),
    )
    return texture


@lru_cache()
def get_shader_module(device, code: str):
    """
    One module holds both stages of a shader, so what GL needed two files and a pair of
    matching varying declarations for is one file whose stages share a struct.
    """
    return device.create_shader_module(code=code)


"""
A mobject's uniforms travel in one block, written once per mobject rather than one
uniform at a time. Each kind of mobject lays out the block it wants with
uniform_block_dtype, starting with the members every kind has, see Mobject.uniform_dtype,
and the struct its shaders read is generated from that dtype, see uniform_block_code.
"""
# Where a shader finds each thing it reads, grouped by how often it changes: once a frame,
# once a mobject, and once the buffers behind it are replaced. A shader says these numbers
# itself, in the inserts declaring each, so what is here is what those agree with.
FRAME_GROUP = 0
MOBJECT_GROUP = 1
RESOURCE_GROUP = 2
# Within the mobject's own group: its records first, then a sampler and a texture for each
# image its kind names, see texture_binding_code
DATA_BINDING = 0
SAMPLER_BINDING = 1
FIRST_TEXTURE_BINDING = 2
# What every mobject holds, whatever kind it is, as a name and a number of floats.
# First in every block, so that the inserts reading them work wherever they are used.
COMMON_UNIFORMS = (
    ("is_fixed_in_frame", 1),
    ("shading", 3),
    ("clip_plane0", 4),
    ("clip_plane1", 4),
    ("clip_plane2", 4),
    ("clip_plane3", 4),
)
# What a block member of each size is called in a shader. A mat4 is in there because a
# block lays one out as four vec4 columns, which is four vec4s and nothing else; a mat3
# is not, because its columns get padded out to vec4 and this would have to know it.
BLOCK_MEMBER_TYPES = {1: "f32", 2: "vec2f", 3: "vec3f", 4: "vec4f", 16: "mat4x4f"}

"""
The camera's uniforms travel the same way a mobject's do, in one block, except that there
is one of them for the whole frame rather than one per mobject. Every program reads it from
the same buffer, bound once a frame rather than once a mobject, see Renderer.
"""
# Mirrors inserts/frame_uniforms.wgsl. Ordered so that each vec3 is followed by the float
# which fits beside it, leaving nothing padded but the last three floats.
FRAME_UNIFORMS = (
    ("view", 16),
    ("frame_rescale_factors", 3),
    ("frame_scale", 1),
    ("camera_position", 3),
    ("pixel_size", 1),
    ("light_position", 3),
)


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
    A dtype written as the members of a shader struct, which is where a shader gets them:
    generating the declaration from the dtype rather than asking a shader to repeat it
    leaves nothing for the two to disagree about. WGSL lays a struct out as std140 does for
    everything declared here, which uniform_block_dtype has already accounted for, so the
    padding it inserted is left out and the compiler arrives at the same offsets.
    """
    lines = []
    for name in dtype.names:
        if name.startswith("_"):
            # Alignment is the shader compiler's own business, and writing the padding
            # it implies would only push everything after it further along
            continue
        shape = dtype.fields[name][0].shape
        size = shape[0] if shape else 1
        lines.append(f"    {name}: {BLOCK_MEMBER_TYPES[size]},")
    return "\n".join(lines)


FRAME_DTYPE = uniform_block_dtype(*FRAME_UNIFORMS)


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


def get_shader_code(
    filename: str,
    data_layout: tuple[int, tuple[tuple[str, int], ...]],
    uniform_dtype: np.dtype,
    texture_names: tuple[str, ...] = (),
) -> str | None:
    """
    Reads a shader from file, filling in what its source depends on about the mobject it
    will be drawing: where the fields of a vertex record sit, what that mobject holds for
    the whole of itself, and which of its bindings each image it named is at.

    Generating all three rather than asking a shader to repeat them leaves nothing for the
    two sides to disagree about.
    """
    code = get_shader_code_from_file(filename)
    if code is None:
        return None
    return (
        code
        .replace("// DATA_LAYOUT", get_data_layout_code(data_layout))
        .replace("// MOBJECT_UNIFORMS", uniform_block_code(uniform_dtype))
        .replace("// TEXTURES", texture_binding_code(texture_names))
    )


def texture_binding_code(texture_names: tuple[str, ...]) -> str:
    """
    How a shader declares the images its kind of mobject named, and the sampler they share.
    Generated, so that a shader reads each image from the binding that image was put in
    rather than from wherever the order of two lists happens to agree.
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


def get_data_layout_code(data_layout: tuple[int, tuple[tuple[str, int], ...]]) -> str:
    """
    Constants describing where each field of a vertex record sits within the buffer, in
    units of floats, every shader indexing into it itself.
    """
    stride, fields = data_layout
    return "\n".join([
        f"const DATA_STRIDE: u32 = {stride}u;",
        *(f"const DATA_OFFSET_{name}: u32 = {offset}u;" for name, offset in fields),
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
    insertions = re.findall(r"^#INSERT .*\.wgsl$", result, flags=re.MULTILINE)
    for line in insertions:
        inserted_code = get_shader_code_from_file(
            os.path.join("inserts", line.replace("#INSERT ", ""))
        )
        result = result.replace(line, inserted_code)
    return result


def get_colormap_code(rgb_list: Sequence[float]) -> str:
    """A list of colors as a shader array literal, for a snippet coloring by a value"""
    colors = ", ".join("vec3f({}, {}, {})".format(*rgb) for rgb in rgb_list)
    return f"array<vec3f, {len(rgb_list)}>({colors})"
