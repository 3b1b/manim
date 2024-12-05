import os
from diskcache import Cache
from contextlib import contextmanager

from manimlib.utils.directories import get_cache_dir


CACHE_SIZE = 1e9  # 1 Gig


def get_cached_value(key, value_func, message=""):
    cache = Cache(get_cache_dir(), size_limit=CACHE_SIZE)

    value = cache.get(key)
    if value is None:
        with display_during_execution(message):
            value = value_func()
        cache.set(key, value)
    return value


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
