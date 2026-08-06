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
    A structured numpy array laid out to match what a shader reads, and read from python as a
    dict of its fields.

    What a mobject holds for the gpu sits in an array like this, whether one value per point,
    as its data is, or one value for the whole of it, as its uniforms are. Either way the whole
    array is what gets sent, which is why the layout has to mirror what the shader declares,
    see Mobject.data_dtype and uniform_dtype.

    Three things come with holding it here rather than as a bare array. Every write is counted,
    so whatever has sent the array somewhere can ask whether what it sent is still what the
    array holds, see has_changed. Emptying the array remembers what was in it, so a mobject
    stripped of its points and given new ones keeps its style, see resize. And fields are read
    and written by name, rows by index.

    Reading hands back a view onto the array, so a write through one of those, as in

        mob.data["point"][::2] = new_points

    goes uncounted, and whoever does it has to say so with

        mob.data.note_change()

    Assigning the whole field instead, mob.data["point"] = new_points, needs no such thing.
    """

    def __init__(self, dtype: np.dtype, length: int = 0):
        self.set_array(np.zeros(length, dtype=dtype))
        # What to fill in with when growing from nothing, see resize
        self.defaults: np.ndarray = np.ones(1, dtype=dtype)
        # Counted up by every write, rather than a yes or no, since each of several watchers
        # needs to know what it has missed
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

    def set_array(self, array: np.ndarray) -> None:
        """
        The array, along with the two ways of seeing the whole of it at once: every field as one
        run of floats, and the same as bytes, padding included.

        Made once here rather than where they are wanted, making a view costing more than the
        copy it is for, see Arena.put and Uniforms.interpolate.
        """
        self.array: np.ndarray = array
        self.floats: np.ndarray = array.view(np.float32)
        self.bytes: np.ndarray = array.view(np.uint8)

    def note_change(self) -> None:
        """Says that the array was written to through a view onto it, which it cannot count"""
        self.version += 1

    def has_changed(self, observer: Any) -> bool:
        """
        Whether the array has been written to since this observer last asked. A note of the
        version each has seen is kept here, so that watching an array takes nothing but asking
        it.

        Asking counts as having looked. So two things wanting the same answer have to be two
        observers, or ask once between them, see Program.write_uniforms.

        An observer is remembered for as long as the array is. Nothing here is replaced often
        enough for that to be worth weak references, which cost four times as much to look up.
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
        # underscore and is no part of what the array holds
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
            self.set_array(self.defaults.copy())
        self.set_array(resize_func(self.array, length))
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

    def interpolate(self, array1: StructuredArray, array2: StructuredArray, alpha: float) -> None:
        """
        Takes on the blend of two others, every field at once.

        Laid out the same way, the three can be read as one flat run of floats and blended
        in a single pass. That is several times quicker than working field by field, each
        of those reaching across the array in strides rather than straight along it, and it
        costs no more to blend a field than to decide whether to. Whatever a field wants
        done to it other than a blend, the caller writes over afterwards, see
        Mobject.interpolate.
        """
        same_layout = self.dtype == array1.dtype == array2.dtype
        if not (same_layout and len(self) == len(array1) == len(array2)):
            # Different kinds of mobject, so only what they have in common carries over
            for key in self:
                if key in array1 and key in array2:
                    self[key] = (1 - alpha) * array1[key] + alpha * array2[key]
            return
        floats1 = array1.floats
        floats2 = array2.floats
        # Most transformations leave most of what they move through alone, e.g. shifting a
        # mobject without restyling it, and writing values equal to those here would send
        # the array again for nothing
        if np.array_equal(floats1, floats2) and np.array_equal(self.floats, floats1):
            return
        self.floats[:] = (1 - alpha) * floats1 + alpha * floats2
        self.note_change()

    def copy(self) -> Self:
        result = copy.copy(self)
        result.set_array(self.array.copy())
        result.defaults = self.defaults.copy()
        result.version += 1
        # A copy has been looked at by nobody, whatever has looked at what it was copied from
        result.seen_by = dict()
        return result
