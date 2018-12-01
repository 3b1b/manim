import constants
import os
import importlib

modules = filter(
    lambda x: x.endswith(".py"),
    os.listdir(constants.THIS_DIR + os.sep + "once_useful_constructs"),
)
modules = list(map(
    lambda x: x[:x.find(".py")],
    modules
))
for m in modules:
    if m == "__init__":
        continue
    else:
        importlib.import_module("once_useful_constructs." + m, package="once_useful_constructs")

for m in modules:
    if m == "__init__":
        continue
    m = globals()[m]
    module_dict = m.__dict__
    try:
        to_import = m.__all__
    except AttributeError:
        to_import = [name for name in module_dict if not name.startswith('_')]
    globals().update({name: module_dict[name] for name in to_import})
