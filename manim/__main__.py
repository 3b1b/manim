import inspect
import os
import platform
import subprocess as sp
import sys
import re
import traceback
import importlib.util
import types

from . import constants, logger, console, file_writer_config
from .config.config import camera_config, args
from .config import cfg_subcmds
from .utils.module_ops import (
    get_module,
    get_scene_classes_from_module,
    get_scenes_to_render,
)
from .scene.scene import Scene
from .utils.file_ops import open_file as open_media_file
from .grpc.impl import frame_server_impl
from .renderer.cairo_renderer import CairoRenderer


def open_file_if_needed(file_writer):
    if file_writer_config["verbosity"] != "DEBUG":
        curr_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    open_file = any(
        [file_writer_config["preview"], file_writer_config["show_in_file_browser"]]
    )
    if open_file:
        current_os = platform.system()
        file_paths = []

        if file_writer_config["save_last_frame"]:
            file_paths.append(file_writer.get_image_file_path())
        if (
            file_writer_config["write_to_movie"]
            and not file_writer_config["save_as_gif"]
        ):
            file_paths.append(file_writer.get_movie_file_path())
        if file_writer_config["save_as_gif"]:
            file_paths.append(file_writer.gif_file_path)

        for file_path in file_paths:
            if file_writer_config["show_in_file_browser"]:
                open_media_file(file_path, True)
            if file_writer_config["preview"]:
                open_media_file(file_path, False)

    if file_writer_config["verbosity"] != "DEBUG":
        sys.stdout.close()
        sys.stdout = curr_stdout


def main():
    if hasattr(args, "subcommands"):
        if "cfg" in args.subcommands:
            if args.cfg_subcommand is not None:
                subcommand = args.cfg_subcommand
                if subcommand == "write":
                    cfg_subcmds.write(args.level, args.open)
                elif subcommand == "show":
                    cfg_subcmds.show()
                elif subcommand == "export":
                    cfg_subcmds.export(args.dir)
            else:
                logger.error("No argument provided; Exiting...")

    else:
        module = get_module(file_writer_config["input_file"])
        all_scene_classes = get_scene_classes_from_module(module)
        scene_classes_to_render = get_scenes_to_render(all_scene_classes)
        for SceneClass in scene_classes_to_render:
            try:
                if camera_config["use_js_renderer"]:
                    frame_server_impl.get(SceneClass).start()
                else:
                    scene = SceneClass()
                    scene.render()
                    open_file_if_needed(scene.renderer.file_writer)
            except Exception:
                print("\n\n")
                traceback.print_exc()
                print("\n\n")


if __name__ == "__main__":
    main()
