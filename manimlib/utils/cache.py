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
        key = hash_string(f"{func.__name__}{args}{kwargs}")
        value = _cache.get(key)
        if value is None:
            value = func(*args, **kwargs)
            _cache.set(key, value)
        return value
    return wrapper


def clear_cache():
    _cache.clear()
