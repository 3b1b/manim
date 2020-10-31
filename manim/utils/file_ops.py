"""Utility functions for interacting with the file system."""

__all__ = [
    "add_extension_if_not_present",
    "guarantee_existence",
    "seek_full_path_from_defaults",
    "modify_atime",
    "open_file",
]


import os
import platform
import time
import subprocess as sp
from pathlib import Path


def add_extension_if_not_present(file_name, extension):
    if file_name.suffix != extension:
        return file_name.with_suffix(extension)
    else:
        return file_name


def guarantee_existence(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.abspath(path)


def seek_full_path_from_defaults(file_name, default_dir, extensions):
    possible_paths = [file_name]
    possible_paths += [
        Path(default_dir) / f"{file_name}{extension}" for extension in ["", *extensions]
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    error = "From: {}, could not find {} at either of these locations: {}".format(
        os.getcwd(), file_name, possible_paths
    )
    raise IOError(error)


def modify_atime(file_path):
    """Will manually change the accessed time (called `atime`) of the file, as on a lot of OS the accessed time refresh is disabled by default.

    Parameters
    ----------
    file_path : :class:`str`
        The path of the file.
    """
    os.utime(file_path, times=(time.time(), os.path.getmtime(file_path)))


def open_file(file_path, in_browser=False):
    current_os = platform.system()
    if current_os == "Windows":
        os.startfile(file_path if not in_browser else os.path.dirname(file_path))
    else:
        if current_os == "Linux":
            commands = ["xdg-open"]
            file_path = file_path if not in_browser else os.path.dirname(file_path)
        elif current_os.startswith("CYGWIN"):
            commands = ["cygstart"]
            file_path = file_path if not in_browser else os.path.dirname(file_path)
        elif current_os == "Darwin":
            commands = ["open"] if not in_browser else ["open", "-R"]
        else:
            raise OSError("Unable to identify your operating system...")
        commands.append(file_path)
        sp.Popen(commands)
