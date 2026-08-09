from __future__ import annotations

import numpy as np

from manimlib.utils.structured_array import StructuredArray

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable


"""
A mobject's uniforms travel in one block. Each kind of mobject lays out the block it wants
with uniform_block_dtype, starting with the members every kind has, see Mobject.uniform_dtype,
and the struct its shaders read is generated from that same dtype, see uniform_block_code, so
the two sides cannot disagree.
"""
# What every mobject holds, as a name and a number of floats. First in every block, so that
# the inserts reading them work wherever they are used.
COMMON_UNIFORMS = (
    ("is_fixed_in_frame", 1),
    ("shading", 3),
    ("clip_plane0", 4),
    ("clip_plane1", 4),
    ("clip_plane2", 4),
    ("clip_plane3", 4),
)
# What a block member of each size is called in a shader. A mat4 is in there, being four vec4
# columns and nothing else; a mat3 is not, its columns being padded out to vec4.
BLOCK_MEMBER_TYPES = {1: "f32", 2: "vec2f", 3: "vec3f", 4: "vec4f", 16: "mat4x4f"}
# A block puts its array elements four floats apart whatever they hold, so anything narrower
# is declared as a vec4f and read from its first components.
ARRAY_ELEMENT_SIZE = 4


def uniform_block_dtype(*members: tuple[str, int] | tuple[str, int, int]) -> np.dtype:
    """
    Lays out members, each given as a name and how many floats it holds, exactly as std140
    does, so a mobject's uniforms can be handed to the gpu as they sit.

    A member given a third number holds that many of itself, e.g. ("colors", 4, 9) for nine
    colors, and is read from python as an array of that many rows.

    The rules reproduced are that a member is aligned to its own size, rounded up to four
    floats for anything wider than two, and that the block as a whole is rounded up likewise.
    What that alignment skips over is declared as a field rather than left as a gap, numpy not
    carrying the contents of a gap over when copying, which would leave whatever the memory
    held to be compared against and sent.
    """
    names: list[str] = []
    formats: list[Any] = []

    def add(name: str, shape: tuple[int, ...]) -> None:
        names.append(name)
        formats.append(np.float32 if shape == (1,) else (np.float32, shape))

    size_so_far = 0
    for name, size, *rest in members:
        count = rest[0] if rest else 1
        if count > 1 and size != ARRAY_ELEMENT_SIZE:
            raise ValueError(
                f"An array in a block holds {ARRAY_ELEMENT_SIZE} floats to an element, so "
                f"{name} cannot hold {count} of {size}"
            )
        if size not in BLOCK_MEMBER_TYPES:
            raise ValueError(f"No room in a block for {name}, of {size} floats")
        skipped = -size_so_far % (size if size <= 2 else 4)
        if skipped:
            add(f"_pad{len(names)}", (skipped,))
        add(name, (size,) if count == 1 else (count, size))
        size_so_far += skipped + count * size
    if -size_so_far % 4:
        add(f"_pad{len(names)}", (-size_so_far % 4,))
    # Left to pack the fields itself, numpy places them back to back, which is where the
    # padding above has been chosen to put them
    return np.dtype({"names": names, "formats": formats})


def uniform_block_code(dtype: np.dtype) -> str:
    """
    A dtype written as the members of a shader struct, which is where a shader gets them,
    leaving nothing for the two sides to disagree about. WGSL lays a struct out as std140 does
    for everything declared here, so the padding uniform_block_dtype inserted is left out and
    the compiler arrives at the same offsets.
    """
    lines = []
    for name in dtype.names:
        if name.startswith("_"):
            continue
        shape = dtype.fields[name][0].shape
        if len(shape) == 2:
            count, size = shape
            lines.append(f"    {name}: array<{BLOCK_MEMBER_TYPES[size]}, {count}>,")
        else:
            size = shape[0] if shape else 1
            lines.append(f"    {name}: {BLOCK_MEMBER_TYPES[size]},")
    return "\n".join(lines)


class Uniforms(StructuredArray):
    """
    A mobject's uniforms: one value each for the whole of it, laid out to match the block its
    shaders declare. Reading one gives the value itself rather than the row holding it.
    """

    def __init__(self, dtype: np.dtype):
        super().__init__(dtype, length=1)

    def __getitem__(self, key: str) -> Any:
        return self.array[key][0]

    def apply(self, key: str, func: Callable[[np.ndarray], np.ndarray]) -> None:
        """
        Passes one uniform through a function written for many rows of values, e.g. one
        that moves points, which reading a single value back has to be dressed up as.
        """
        self[key] = func(self[key][np.newaxis])[0]
