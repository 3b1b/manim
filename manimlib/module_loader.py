from __future__ import annotations

import builtins
import importlib
import os
import sys

from manimlib.logger import log

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    Module = importlib.util.types.ModuleType


class ModuleLoader:
    """
    Utility class to load a module from a file and handle its imports.
    """

    @staticmethod
    def exec_module_and_track_imports(spec, module: Module):
        """
        Executes the given module (imports it) and returns all the modules that
        are imported during its execution.

        This is achieved by replacing the __import__ function with a custom one that
        tracks the imported modules. At the end, the original __import__ function is
        restored.
        """
        imported_modules = set()
        original_import = builtins.__import__

        def tracked_import(name, globals=None, locals=None, fromlist=(), level=0):
            result = original_import(name, globals, locals, fromlist, level)
            imported_modules.add(name)
            return result

        builtins.__import__ = tracked_import

        try:
            spec.loader.exec_module(module)
        finally:
            builtins.__import__ = original_import

        return imported_modules

    @staticmethod
    def reload_modules(modules, reloaded_modules_tracker: set):
        """
        Out of the given modules, reloads the ones that were not already imported.

        We also restrict ourselves to reloading only the modules that are not
        built-in Python modules to avoid potential issues since they were mostly
        not designed to be reloaded.
        """
        for mod in modules:
            if mod in reloaded_modules_tracker:
                continue

            if mod not in sys.modules:
                continue

            if mod in sys.builtin_module_names or mod in [
                "pkg_resources",
                "setuptools",
            ]:
                continue

            log.debug('Reloading module "%s"', mod)
            importlib.reload(sys.modules[mod])

            reloaded_modules_tracker.add(mod)

    @staticmethod
    def get_module(file_name: str | None, is_during_reload=False) -> Module | None:
        """
        Imports a module from a file and returns it.

        During reload (when the user calls `reload()` in the IPython shell), we
        also track the imported modules and reload them as well (they would be
        cached otherwise). See the reload_manager where the reload parameter is set.
        """
        if file_name is None:
            return None
        module_name = file_name.replace(os.sep, ".").replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_name)
        module = importlib.util.module_from_spec(spec)

        if is_during_reload:
            imported_modules = ModuleLoader.exec_module_and_track_imports(spec, module)
            reloaded_modules_tracker = set()
            ModuleLoader.reload_modules(imported_modules, reloaded_modules_tracker)

        # In the case of reloading, the following statement is executed twice:
        # 1. to track the imports
        # 2. to actually execute the module again with the respective
        #    imports reloaded
        spec.loader.exec_module(module)

        return module
