from __future__ import annotations

import builtins
import importlib
import os
import sys
import sysconfig

from manimlib.logger import log

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    Module = importlib.util.types.ModuleType


class ModuleLoader:
    """
    Utility class to load a module from a file and handle its imports.
    """

    @staticmethod
    def get_module(file_name: str | None, is_during_reload=False) -> Module | None:
        """
        Imports a module from a file and returns it.

        During reload (when the user calls `reload()` in the IPython shell), we
        also track the imported modules and reload them as well (they would be
        cached otherwise). See the reload_manager where the reload parameter is set.

        Note that exec_module is called twice when reloading a module:
        1. In exec_module_and_track_imports to track the imports
        2. Here to actually execute the module again with the respective
           imported modules reloaded.
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

        spec.loader.exec_module(module)
        return module

    @staticmethod
    def exec_module_and_track_imports(spec, module: Module) -> set[str]:
        """
        Executes the given module (imports it) and returns all the modules that
        are imported during its execution.

        This is achieved by replacing the __import__ function with a custom one
        that tracks the imported modules. At the end, the original __import__
        built-in function is restored.
        """
        imported_modules: set[str] = set()
        original_import = builtins.__import__

        def tracked_import(name, globals=None, locals=None, fromlist=(), level=0):
            """
            Custom __import__ function that does exactly the same as the original
            one, but also tracks the imported modules by means of adding their
            names to a set.
            """
            result = original_import(name, globals, locals, fromlist, level)
            imported_modules.add(name)
            return result

        builtins.__import__ = tracked_import

        try:
            # Remove the "_insert_embed" suffix from the module name
            module_name = module.__name__
            if module.__name__.endswith("_insert_embed"):
                module_name = module_name[:-13]
            log.debug('RReloading module "%s"', module_name)

            spec.loader.exec_module(module)
        finally:
            builtins.__import__ = original_import

        return imported_modules

    @staticmethod
    def reload_modules(modules: set[str], reloaded_modules_tracker: set[str]):
        """
        Out of the given modules, reloads the ones that were not already imported.

        We skip module that are not user-defined.
        """
        for mod in modules:
            if mod in reloaded_modules_tracker:
                continue

            if not ModuleLoader.is_user_defined_module(mod):
                continue

            log.debug('Reloading module "%s"', mod)
            module = sys.modules[mod]
            importlib.reload(module)

            reloaded_modules_tracker.add(mod)

    @staticmethod
    def is_user_defined_module(mod: str) -> bool:
        """
        Returns whether the given module is user-defined or not.

        A module is considered user-defined if it is not part of the standard
        library, not an external library (site-packages or dist-packages), and
        is located in the current working directory (or subdirectories).
        """
        if mod not in sys.modules:
            return False

        if mod in sys.builtin_module_names:
            return False

        module = sys.modules[mod]
        module_path = getattr(module, "__file__", None)
        if module_path is None:
            return False
        module_path = os.path.abspath(module_path)

        # Standard lib
        standard_lib_path = sysconfig.get_path("stdlib")
        if module_path.startswith(standard_lib_path):
            return False

        # External libraries (site-packages or dist-packages), e.g. numpy
        if "site-packages" in module_path or "dist-packages" in module_path:
            return False

        return True
