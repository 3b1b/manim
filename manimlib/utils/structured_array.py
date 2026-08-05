from __future__ import annotations

import copy

import numpy as np

from manimlib.utils.iterables import resize_array

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Iterator, Mapping, Sequence
    from manimlib.typing import Self


class StructuredArray(object):
    """
    A structured numpy array laid out to match what a shader reads, and read from
    python as a dict of its fields.

    What a mobject holds for the gpu sits in an array like this, whether it is one value
    per point, as its data is, or one value for the whole of it, as its uniforms are.
    Either way, what gets sent is a copy of the whole array, which is why the layout has
    to mirror what the shader declares, see Mobject.data_dtype and uniform_dtype.

    Three things come with holding it here rather than as a bare array. Every write to
    it is counted, so that whatever has sent it somewhere can ask whether what it sent
    is still what the array holds, see has_changed. Emptying the array remembers what was
    in it, so that a mobject stripped of its points and given new ones keeps the style it
    had, see resize. And fields are read and written by name, as with a dict, while rows
    are read and written by index, as with the array itself.

    Either kind of write is counted. Reading, though, hands back a view onto the array,
    so writing through one of those, as in

        mob.data["point"][::2] = new_points

    goes uncounted, and whoever does it has to say so with

        mob.data.note_change()

    Assigning the whole field instead, mob.data["point"] = new_points, needs no such
    thing, and is the same operation as far as the array is concerned: a field cannot
    be rebound, only written into.
    """

    def __init__(self, dtype: np.dtype, length: int = 0):
        self.array: np.ndarray = np.zeros(length, dtype=dtype)
        # What to fill in with when growing from nothing, see resize
        self.defaults: np.ndarray = np.ones(1, dtype=dtype)
        # Counted up by every write. A count rather than a yes or no, since more than one
        # thing may be watching and each needs to know what it has missed rather than
        # whether anyone has missed anything.
        self.version: int = 1
        # Which version each of those things last saw, see has_changed
        self.seen_by: dict[Any, int] = dict()

    def __getitem__(self, key: str | int | slice | np.ndarray) -> np.ndarray:
        return self.array[key]

    def __setitem__(self, key: str | int | slice | np.ndarray, value: Any) -> None:
        self.array[key] = value
        self.version += 1

    def __len__(self) -> int:
        return len(self.array)

    def __contains__(self, key: str) -> bool:
        return key in self.keys()

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    def __repr__(self) -> str:
        values = ", ".join(f"{key}={self[key]}" for key in self)
        return f"{type(self).__name__}({values})"

    def note_change(self) -> None:
        """
        Says that the array was written to in a way it had no chance to count, as any
        write through a view onto it is.
        """
        self.version += 1

    def has_changed(self, observer: Any) -> bool:
        """
        Whether the array has been written to since this observer last asked.

        Everything watching an array wants the same thing of it, to know whether what it last
        read is still what the array holds, and would otherwise each keep its own note of the
        version it saw and remember to move that note on. The notes are kept here instead, one
        for each observer, so that watching an array takes nothing but asking it.

        Asking counts as having looked, the answer being about the writes since the last ask.
        So two things which want the same answer have to be two observers, or ask once between
        them, see ShaderWrapper.write_uniform_buffer for one which does the latter.

        An observer is remembered for as long as the array is, so one which is thrown away
        while its array lives on is kept alive by it. Nothing here is replaced often enough
        for that to be worth weak references, which cost four times as much to look up.
        """
        if self.seen_by.get(observer) == self.version:
            return False
        self.seen_by[observer] = self.version
        return True

    @property
    def dtype(self) -> np.dtype:
        return self.array.dtype

    def keys(self) -> Sequence[str]:
        # Padding, which a uniform block's alignment calls for, is named with a leading
        # underscore, and is no part of what the array holds as far as anyone can tell
        return tuple(
            name for name in self.array.dtype.names
            if not name.startswith("_")
        )

    def update(self, values: Mapping | None = None, **kwargs) -> None:
        """
        Fields the array has no room for are passed over, since one mobject's values
        are often handed to another which holds a different set of them.
        """
        for source in (values, kwargs):
            if not source:
                continue
            for key in source:
                if key in self:
                    self[key] = source[key]

    @property
    def floats(self) -> np.ndarray:
        """
        Every field as one flat array, for reading or writing the lot in one go.
        Includes whatever padding the dtype carries, which is harmless to touch.
        """
        return self.array.view(np.float32)

    @property
    def rows_or_defaults(self) -> np.ndarray:
        """
        The rows held, or the row of defaults standing in for them while there are
        none, which is where a style read or written in the meantime belongs. Being the
        array itself, writing into what this hands back goes uncounted, so say so with
        note_change.
        """
        return self.array if len(self.array) else self.defaults

    def resize(
        self,
        length: int,
        resize_func: Callable[[np.ndarray, int], np.ndarray] = resize_array
    ) -> None:
        """
        Emptying the array keeps hold of its first row, and growing from empty starts
        from that row again, so that whatever a mobject was styled with survives having
        its points cleared and set afresh.
        """
        if length == 0:
            if len(self.array) > 0:
                self.defaults[:] = self.array[:1]
        elif len(self.array) == 0:
            self.array = self.defaults.copy()
        self.array = resize_func(self.array, length)
        self.version += 1

    def match(self, other: StructuredArray) -> None:
        """
        Takes on another's values, field by field where the two are laid out
        differently, e.g. because they belong to different kinds of mobject.
        """
        if self.dtype == other.dtype and len(self) == len(other):
            self.array[:] = other.array
            self.version += 1
        else:
            self.update(other)

    def copy(self) -> Self:
        result = copy.copy(self)
        result.array = self.array.copy()
        result.defaults = self.defaults.copy()
        result.version += 1
        # A copy has been looked at by nobody, whatever has looked at what it was copied from
        result.seen_by = dict()
        return result
