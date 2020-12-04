"""
plugins_flags.py
------------

Plugin Managing Utility.
"""

import pathlib
import pkg_resources

from manim import console

__all__ = ["list_plugins", "update"]


def get_plugins():
    plugins = {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points("manim.plugins")
    }
    return plugins


def list_plugins():
    console.print("[green bold]Plugins:[/green bold]", justify="left")

    plugins = get_plugins()
    for plugin in plugins:
        console.print(f" • {plugin}")
