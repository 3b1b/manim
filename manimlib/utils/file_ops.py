from __future__ import annotations

import os
from typing import Iterable

import numpy as np
import validators


def add_extension_if_not_present(file_name: str, extension: str) -> str:
    # This could conceivably be smarter about handling existing differing extensions
    if(file_name[-len(extension):] != extension):
        return file_name + extension
    else:
        return file_name


def guarantee_existence(path: str) -> str:
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.abspath(path)


def find_file(
    file_name: str,
    directories: Iterable[str] | None = None,
    extensions: Iterable[str] | None = None
) -> str:
    # Check if this is a file online first, and if so, download
    # it to a temporary directory
    if validators.url(file_name):
        import urllib.request
        from manimlib.utils.directories import get_downloads_dir
        stem, name = os.path.split(file_name)
        folder = get_downloads_dir()
        path = os.path.join(folder, name)
        urllib.request.urlretrieve(file_name, path)
        return path

    # Check if what was passed in is already a valid path to a file
    if os.path.exists(file_name):
        return file_name

    # Otherwise look in local file system
    directories = directories or [""]
    extensions = extensions or [""]
    possible_paths = (
        os.path.join(directory, file_name + extension)
        for directory in directories
        for extension in extensions
    )
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise IOError(f"{file_name} not Found")


def get_sorted_integer_files(
    directory: str,
    min_index: float = 0,
    max_index: float = np.inf,
    remove_non_integer_files: bool = False,
    remove_indices_greater_than: float | None = None,
    extension: str | None = None,
) -> list[str]:
    indexed_files = []
    for file in os.listdir(directory):
        if '.' in file:
            index_str = file[:file.index('.')]
        else:
            index_str = file

        full_path = os.path.join(directory, file)
        if index_str.isdigit():
            index = int(index_str)
            if remove_indices_greater_than is not None:
                if index > remove_indices_greater_than:
                    os.remove(full_path)
                    continue
            if extension is not None and not file.endswith(extension):
                continue
            if index >= min_index and index < max_index:
                indexed_files.append((index, file))
        elif remove_non_integer_files:
            os.remove(full_path)
    indexed_files.sort(key=lambda p: p[0])
    return list(map(lambda p: os.path.join(directory, p[1]), indexed_files))
