import os
import platform
import sys
import traceback

from manim import constants, logger, console, config
from manim import Scene
from manim.utils.module_ops import (
    get_module,
    get_scene_classes_from_module,
    get_scenes_to_render,
)
from manim.utils.file_ops import open_file as open_media_file
from manim.grpc.impl import frame_server_impl
from manim.config.utils import init_dirs
from manim.config.main_utils import *


def open_file_if_needed(file_writer):
    if config["verbosity"] != "DEBUG":
        curr_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    open_file = any([config["preview"], config["show_in_file_browser"]])

    if open_file:
        current_os = platform.system()
        file_paths = []

        if config["save_last_frame"]:
            file_paths.append(file_writer.get_image_file_path())
        if config["write_to_movie"] and not config["save_as_gif"]:
            file_paths.append(file_writer.get_movie_file_path())
        if config["save_as_gif"]:
            file_paths.append(file_writer.gif_file_path)

        for file_path in file_paths:
            if config["show_in_file_browser"]:
                open_media_file(file_path, True)
            if config["preview"]:
                open_media_file(file_path, False)

    if config["verbosity"] != "DEBUG":
        sys.stdout.close()
        sys.stdout = curr_stdout


def main():
    args = parse_args(sys.argv)

    if hasattr(args, "cmd"):
        if args.cmd == "cfg":
            if args.subcmd:
                from manim.config import cfg_subcmds

                if args.subcmd == "write":
                    cfg_subcmds.write(args.level, args.open)
                elif args.subcmd == "show":
                    cfg_subcmds.show()
                elif args.subcmd == "export":
                    cfg_subcmds.export(args.dir)
            else:
                logger.error("No subcommand provided; Exiting...")

        # elif args.cmd == "some_other_cmd":
        #     something_else_here()

    else:
        config.digest_args(args)
        init_dirs(config)

        module = get_module(config["input_file"])
        all_scene_classes = get_scene_classes_from_module(module)
        scene_classes_to_render = get_scenes_to_render(all_scene_classes)
        for SceneClass in scene_classes_to_render:
            try:
                if config["use_js_renderer"]:
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
