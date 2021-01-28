import types
from importlib import import_module

import pkg_resources

from .. import config, logger

__all__ = []


plugins_requested: list = config["plugins"]
if "" in plugins_requested:
    plugins_requested.remove("")
for plugin in pkg_resources.iter_entry_points("manim.plugins"):
    if plugin.name not in plugins_requested:
        continue
    loaded_plugin = plugin.load()
    if isinstance(loaded_plugin, types.ModuleType):
        # it is a module so it can't be called
        # see if __all__ is defined
        # if it is defined use that to load all the modules necessary
        # essentially this would be similar to `from plugin import *``
        # if not just import the module with the plugin name
        if hasattr(loaded_plugin, "__all__"):
            for thing in loaded_plugin.__all__:
                exec(f"{thing}=loaded_plugin.{thing}")
                __all__.append(thing)
        else:
            exec(f"{plugin.name}=loaded_plugin")
            __all__.append(plugin.name)
    elif isinstance(loaded_plugin, types.FunctionType):
        # call the function first
        # it will return a list of modules to add globally
        # finally add it
        lists = loaded_plugin()
        for l in lists:
            exec(f"{l.__name__}=l")
            __all__.append(l.__name__)
    plugins_requested.remove(plugin.name)
else:
    if plugins_requested != []:
        logger.warning("Missing Plugins: %s", plugins_requested)
