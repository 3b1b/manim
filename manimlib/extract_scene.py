from __future__ import annotations

import copy
import inspect
import sys

import re

from manimlib.module_loader import ModuleLoader

from manimlib.config import manim_config
from manimlib.logger import log
from manimlib.scene.interactive_scene import InteractiveScene
from manimlib.scene.scene import Scene

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    Module = importlib.util.types.ModuleType
    from typing import Optional
    from addict import Dict


class BlankScene(InteractiveScene):
    def construct(self):
        exec(manim_config.universal_import_line)
        self.embed()


def is_child_scene(obj, module):
    if not inspect.isclass(obj):
        return False
    if not issubclass(obj, Scene):
        return False
    if obj == Scene:
        return False
    if not obj.__module__.startswith(module.__name__):
        return False
    return True


def prompt_user_for_choice(scene_classes):
    name_to_class = {}
    max_digits = len(str(len(scene_classes)))
    for idx, scene_class in enumerate(scene_classes, start=1):
        name = scene_class.__name__
        print(f"{str(idx).zfill(max_digits)}: {name}")
        name_to_class[name] = scene_class
    try:
        user_input = input("\nSelect which scene to render (by name or number): ")
        return [
            name_to_class[split_str] if not split_str.isnumeric() else scene_classes[int(split_str) - 1]
            for split_str in user_input.replace(" ", "").split(",")
        ]
    except IndexError:
        log.error("Invalid scene number")
        sys.exit(2)
    except KeyError:
        log.error("Invalid scene name")
        sys.exit(2)
    except EOFError:
        sys.exit(1)


def compute_total_frames(scene_class, scene_config):
    """
    When a scene is being written to file, a copy of the scene is run with
    skip_animations set to true so as to count how many frames it will require.
    This allows for a total progress bar on rendering, and also allows runtime
    errors to be exposed preemptively for long running scenes.
    """
    pre_config = copy.deepcopy(scene_config)
    pre_config["file_writer_config"]["write_to_movie"] = False
    pre_config["file_writer_config"]["save_last_frame"] = False
    pre_config["file_writer_config"]["quiet"] = True
    pre_config["skip_animations"] = True
    pre_scene = scene_class(**pre_config)
    pre_scene.run()
    total_time = pre_scene.time - pre_scene.skip_time
    return int(total_time * manim_config.camera.fps)


def scene_from_class(scene_class, scene_config: Dict, run_config: Dict):
    fw_config = manim_config.file_writer
    if fw_config.write_to_movie and run_config.prerun:
        scene_config.file_writer_config.total_frames = compute_total_frames(scene_class, scene_config)
    return scene_class(**scene_config)


def note_missing_scenes(arg_names, module_names):
    for name in arg_names:
        if name not in module_names:
            log.error(f"No scene named {name} found")


def get_scenes_to_render(all_scene_classes: list, scene_config: Dict, run_config: Dict):
    if run_config["write_all"] or len(all_scene_classes) == 1:
        classes_to_run = all_scene_classes
    else:
        name_to_class = {sc.__name__: sc for sc in all_scene_classes}
        classes_to_run = [name_to_class.get(name) for name in run_config.scene_names]
        classes_to_run = list(filter(lambda x: x, classes_to_run))  # Remove Nones
        note_missing_scenes(run_config.scene_names, name_to_class.keys())

    if len(classes_to_run) == 0:
        classes_to_run = prompt_user_for_choice(all_scene_classes)

    return [
        scene_from_class(scene_class, scene_config, run_config)
        for scene_class in classes_to_run
    ]


def get_scene_classes(module: Optional[Module]):
    if module is None:
        # If no module was passed in, just play the blank scene
        return [BlankScene]
    if hasattr(module, "SCENES_IN_ORDER"):
        return module.SCENES_IN_ORDER
    else:
        return [
            member[1]
            for member in inspect.getmembers(
                module,
                lambda x: is_child_scene(x, module)
            )
        ]


def get_indent(code_lines: list[str], line_number: int) -> str:
    """
    Find the indent associated with a given line of python code,
    as a string of spaces
    """
    # Find most recent non-empty line
    try:
        line = next(filter(lambda line: line.strip(), code_lines[line_number - 1::-1]))
    except StopIteration:
        return ""

    # Either return its leading spaces, or add for if it ends with colon
    n_spaces = len(line) - len(line.lstrip())
    if line.endswith(":"):
        n_spaces += 4
    return n_spaces * " "


def find_enclosing_class(
    lines: list[str], insert_line: int
) -> tuple[str, int] | None:
    """
    Backtrack from `insert_line` to locate the nearest enclosing
    `class Name(` definition.

    Returns:
      (class_name, class_def_line_index) if found, else None.
    """
    for i in range(insert_line, -1, -1):
        stripped = lines[i].strip()
        if stripped.startswith("class ") and "(" in stripped:
            match = re.match(r"class (\w+)\(", stripped)
            if match:
                return match.group(1), i
    return None


def insert_embed_line_to_module(module: ModuleType, run_config: Dict) -> None:
    """
    A clever hack for live-patching ManimGL scenes by injecting a `self.embed()`
    call at runtime. This module-level doc highlights that we're doing something
    ingenious yet pragmatic: adjusting for shifting source lines, backtracking to
    the correct class, and re-compiling the module on the fly.

    Dynamically injects `self.embed()` into the user's InteractiveScene subclass.

    This function:
      1. Reads the current source lines of `module`.
      2. Computes how far the file has shifted since last insertion.
      3. Backtracks to identify the correct class definition.
      4. Inserts `self.embed()` at the adjusted line with proper indentation.
      5. Updates `run_config` so subsequent reloads keep patching the right spot.
      6. Recompiles and execs the modified source to live-patch the module.

    Arguments:
      module:     The already‐imported Python module object containing scene classes.
      run_config: A dict that must include:
                    - "embed_line":   The last insertion index (int).
                    - "last_source_len": Previous source length to compute shifts.
                    - Optionally "scene_names" and "original_class_lines" to track context.

    Raises:
      ValueError: If the function cannot locate an enclosing class.
    """
    source_lines = inspect.getsource(module).splitlines()

    # Get our last-known insertion line & adjust for any shifts
    embed_line = run_config.embed_line
    delta       = len(source_lines) - run_config.get("last_source_len", len(source_lines))
    # Ensure insert_line is within [0 .. len(source_lines)-1]
    max_index   = len(source_lines) - 1
    insert_line = max(0, min(embed_line + delta, max_index))

    # TODO: validate that insert_line is within [0..len(source_lines)-1] to prevent out-of-bounds errors
    if insert_line >= len(source_lines):
        raise ValueError(
            f"Computed insert_line {insert_line} > source length {len(source_lines)}"
        )


    # Identify which class we're actually inside
    found = find_enclosing_class(source_lines, insert_line)
    if not found:
        raise ValueError("Could not locate enclosing class for insertion.")
    target_class, class_def_line = found

    # Update run_config
    run_config["scene_names"]           = [target_class]
    run_config["original_class_lines"]  = {target_class: class_def_line}
    run_config["last_source_len"]       = len(source_lines)

    # Inject self.embed() at the adjusted line
    indent = source_lines[insert_line][:len(source_lines[insert_line]) - len(source_lines[insert_line].lstrip())]
    source_lines.insert(insert_line, indent + "self.embed()")
    run_config["embed_line"] = insert_line

    # Recompile & overwrite module in place
    new_code = "\n".join(source_lines)
    code_obj = compile(new_code, module.__name__, "exec")
    exec(code_obj, module.__dict__)

def get_module(run_config: Dict) -> Module:
    module = ModuleLoader.get_module(run_config.file_name, run_config.is_reload)
    if run_config.embed_line:
        insert_embed_line_to_module(module, run_config)
    return module


def main(scene_config: Dict, run_config: Dict):
    module = get_module(run_config)
    all_scene_classes = get_scene_classes(module)
    scenes = get_scenes_to_render(all_scene_classes, scene_config, run_config)
    if len(scenes) == 0:
        print("No scenes found to run")
    return scenes
