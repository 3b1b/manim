from __future__ import annotations

import os
from diskcache import Cache
from contextlib import contextmanager
from functools import wraps

from manimlib.utils.directories import get_cache_dir
from manimlib.utils.simple_functions import hash_string

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    T = TypeVar('T')


CACHE_SIZE = 1e9  # 1 Gig
_cache = Cache(get_cache_dir(), size_limit=CACHE_SIZE)


def cache_on_disk(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = hash_string("".join(map(str, [func.__name__, args, kwargs])))
        value = _cache.get(key)
        if value is None:
            # print(f"Executing {func.__name__}({args[0]}, ...)")
            value = func(*args, **kwargs)
            _cache.set(key, value)
        return value
    return wrapper


def clear_cache():
    _cache.clear()


@contextmanager
def display_during_execution(message: str):
    # Merge into a single line
    to_print = message.replace("\n", " ")
    max_characters = os.get_terminal_size().columns - 1
    if len(to_print) > max_characters:
        to_print = to_print[:max_characters - 3] + "..."
    try:
        print(to_print, end="\r")
        yield
    finally:
        print(" " * len(to_print), end="\r")
