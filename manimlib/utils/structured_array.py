from __future__ import annotations

import copy
from contextlib import contextmanager

import numpy as np

from manimlib.utils.iterables import resize_array
from manimlib.utils.bezier import interpolate

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
    so whatever has sent the array somewhere can tell whether what it sent is still what the
    array holds by keeping the count it saw, see version. Emptying the array remembers what was
    in it, so a mobject
    stripped of its points and given new ones keeps its style, see resize. And fields are read
    and written by name, rows by index.

    Reading hands back a view onto the array, so a write through one of those, as in

        mob.data["point"][::2] = new_points

    goes uncounted. Wrap such writes in

        with mob.data.being_written() as data:
            data["point"][::2] = new_points

    which counts them on the way out, rather than leaving it to whoever wrote them to
    remember. Assigning the whole field instead, mob.data["point"] = new_points, needs
    no such thing.
    """

    def __init__(self, dtype: np.dtype, length: int = 0):
        self.set_array(np.zeros(length, dtype=dtype))
        # What to fill in with when growing from nothing, see resize
        self.defaults: np.ndarray = np.ones(1, dtype=dtype)
        # What a blend between two other arrays comes to, settled by whoever knows the pair
        # rather than worked out again every frame, see prepare_interpolation. Until it is
        # settled an array blends, and blends a field at a time, that being the way which is
        # right whatever the two it blends between are laid out like.
        self.skip_interpolation = False
        self.blend_in_one_pass = False
        # Counted up by every write
        self.version: int = 1

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
        copy it is for, see SharedBuffer.put and StructuredArray.interpolate.
        """
        self.array: np.ndarray = array
        self.floats: np.ndarray = array.view(np.float32)
        self.bytes: np.ndarray = array.view(np.uint8)

    def note_change(self) -> None:
        """Says that the array was written to through a view onto it, which it cannot count"""
        self.version += 1

    @contextmanager
    def being_written(self) -> Iterator[np.ndarray]:
        """
        The rows, for writing into. Writes made through the view this hands back cannot be
        counted as they happen, so they are counted here on the way out, whether or not
        they all went through.

        What comes back is rows_or_defaults, since a style written while there are no
        points belongs in the row standing in for them.
        """
        try:
            yield self.rows_or_defaults
        finally:
            self.version += 1

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

    def prepare_interpolation(self, array1: StructuredArray, array2: StructuredArray) -> None:
        """
        Settles what a blend between these two comes to for as long as the pair stands:
        whether it has anything to say at all, and whether it can be made in one pass.

        Both are facts about the pair rather than about any one frame, and interpolate runs
        once per mobject per frame, so they are worked out here and read off there.
        """
        self.skip_interpolation = np.array_equal(array1.floats, array2.floats)
        self.blend_in_one_pass = (
            self.dtype == array1.dtype == array2.dtype
            and len(self) == len(array1) == len(array2)
        )

    def turn_off_interpolation_skip(self) -> None:
        self.skip_interpolation = False
        self.blend_in_one_pass = False

    def interpolate(
        self,
        array1: StructuredArray,
        array2: StructuredArray,
        alpha: float,
        # A map from keys to alternate interpolation functions
        keys_to_alt_func: dict[str, Callable] | None = None
    ) -> None:
        """
        Takes on the blend of two others, every field at once.

        Laid out the same way, the three can be read as one flat run of floats and blended in
        a single pass. That is several times quicker than working field by field, each of
        those reaching across the array in strides rather than straight along it.

        Two different kinds of mobject are laid out differently, and then only what they have
        in common carries over, a field at a time. Which of the two it is was settled when the
        pair was, see prepare_interpolation.
        """
        if self.skip_interpolation:
            return

        if not self.blend_in_one_pass:
            if keys_to_alt_func is None:
                keys_to_alt_func = dict()
            for key in self:
                if key in array1 and key in array2:
                    func = keys_to_alt_func.get(key, interpolate)
                    self[key] = func(array1[key], array2[key], alpha)
            self.note_change()
            return

        # Interpolate the arrays with as much in-place computation as we can
        np.multiply(array1.floats, 1 - alpha, out=self.floats)
        np.add(self.floats, alpha * array2.floats, out=self.floats)

        # Sweep through any keys with special interpolation functions
        if keys_to_alt_func:
            for key, func in keys_to_alt_func.items():
                self[key] = func(array1[key], array2[key], alpha)

        self.note_change()

    def copy(self) -> Self:
        result = copy.copy(self)
        result.set_array(self.array.copy())
        result.defaults = self.defaults.copy()
        # Counted on, so that a watcher carried over from what this was copied from finds it
        # different rather than taking its own array to be the one it has already seen
        result.version += 1
        return result
