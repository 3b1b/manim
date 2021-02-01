import os
import numpy as np

import validators
import urllib.request
import tempfile


def add_extension_if_not_present(file_name, extension):
    # This could conceivably be smarter about handling existing differing extensions
    if(file_name[-len(extension):] != extension):
        return file_name + extension
    else:
        return file_name


def guarantee_existence(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.abspath(path)


def find_file(file_name, directories=None, extensions=None):
    # Check if this is a file online first, and if so, download
    # it to a temporary directory
    if validators.url(file_name):
        stem, name = os.path.split(file_name)
        folder = guarantee_existence(
            os.path.join(tempfile.gettempdir(), "manim_downloads")
        )
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


def get_sorted_integer_files(directory,
                             min_index=0,
                             max_index=np.inf,
                             remove_non_integer_files=False,
                             remove_indices_greater_than=None,
                             extension=None,
                             ):
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
