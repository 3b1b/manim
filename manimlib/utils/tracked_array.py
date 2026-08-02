from __future__ import annotations

import copy

import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterator, Mapping, Sequence
    from manimlib.typing import Self


class TrackedArray(object):
    """
    A structured numpy array which notes when it has been written to.

    What a mobject holds for the gpu sits in an array like this, whether it is one
    value per point, as its data is, or one value for the whole of it, as its uniforms
    are. Either way, what gets sent is a copy of the whole array, so the only thing
    worth noting is whether anything has changed since it was last sent, which
    whoever sends it clears.

    Fields are read and written by name, as with a dict. A value is meant to be
    replaced rather than written into, since reading one hands back a view onto the
    array, and mutating that in place would go unnoticed here. Anything with reason
    to do so has to say as much, by setting changed itself.
    """

    def __init__(self, dtype: np.dtype, length: int = 0):
        self.array: np.ndarray = np.zeros(length, dtype=dtype)
        # Nothing has been sent yet, so it all counts as having changed
        self.changed: bool = True

    def __getitem__(self, key: str) -> np.ndarray:
        return self.array[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.array[key] = value
        self.changed = True

    def __contains__(self, key: str) -> bool:
        return key in self.keys()

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    def __repr__(self) -> str:
        values = ", ".join(f"{key}={self[key]}" for key in self)
        return f"{type(self).__name__}({values})"

    def keys(self) -> Sequence[str]:
        # Padding, which a uniform block's alignment calls for, is named with a leading
        # underscore, and is no part of what the array holds as far as anyone can tell
        return tuple(
            name for name in self.array.dtype.names
            if not name.startswith("_")
        )

    def items(self) -> list[tuple[str, Any]]:
        return [(key, self[key]) for key in self]

    def get(self, key: str, default: Any = None) -> Any:
        return self[key] if key in self else default

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

    def match(self, other: TrackedArray) -> None:
        """
        Takes on another's values, field by field where the two are laid out
        differently, e.g. because they belong to different kinds of mobject.
        """
        if self.array.dtype == other.array.dtype and len(self.array) == len(other.array):
            self.array[:] = other.array
            self.changed = True
        else:
            self.update(other)

    def copy(self) -> Self:
        result = copy.copy(self)
        result.array = self.array.copy()
        result.changed = True
        return result
