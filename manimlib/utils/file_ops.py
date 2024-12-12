from __future__ import annotations

import os
from pathlib import Path
import hashlib

import numpy as np
import validators
import urllib.request

import manimlib.utils.directories
from manimlib.utils.simple_functions import hash_string

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable


def guarantee_existence(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path.absolute()


def find_file(
    file_name: str,
    directories: Iterable[str] | None = None,
    extensions: Iterable[str] | None = None
) -> Path:
    # Check if this is a file online first, and if so, download
    # it to a temporary directory
    if validators.url(file_name):
        suffix = Path(file_name).suffix
        file_hash = hash_string(file_name)
        folder = manimlib.utils.directories.get_downloads_dir()

        path = Path(folder, file_hash).with_suffix(suffix)
        urllib.request.urlretrieve(file_name, path)
        return path

    # Check if what was passed in is already a valid path to a file
    if os.path.exists(file_name):
        return Path(file_name)

    # Otherwise look in local file system
    directories = directories or [""]
    extensions = extensions or [""]
    possible_paths = (
        Path(directory, file_name + extension)
        for directory in directories
        for extension in extensions
    )
    for path in possible_paths:
        if path.exists():
            return path
    raise IOError(f"{file_name} not Found")
