#!/usr/bin/env python
from manimlib import __version__
import manimlib.config
import manimlib.extract_scene
import manimlib.logger
import manimlib.utils.init_config

# Command line arguments
ARGS = None

# Last interactive window spawned
WINDOW = None

# Last seen scenes
SCENES = None


def main():
    """
    Main entry point for ManimGL.
    """
    global ARGS, SCENES

    print(f"ManimGL \033[32mv{__version__}\033[0m")

    ARGS = manimlib.config.parse_cli()
    if ARGS.version and ARGS.file is None:
        return
    if ARGS.log_level:
        manimlib.logger.log.setLevel(ARGS.log_level)

    if ARGS.config:
        manimlib.utils.init_config.init_customization()
    else:
        get_scenes_and_run()
        # while True:
        #     try:
        #         get_scenes_and_run()
        #     except ReloadSceneException as e:
        #         SCENES = None
        #         get_scenes_and_run(e.start_at_line)


def get_scenes_and_run(overwrite_start_at_line: int | None = None):
    """
    Generates a configuration and runs the scenes.
    """
    global WINDOW, SCENES

    # Args
    if overwrite_start_at_line is not None:
        ARGS.embed = str(overwrite_start_at_line)  # type: ignore
    if ARGS is None:
        print("Fatal error: ARGS is None but it shouldn't be")
        return

    # Args to Config
    config = manimlib.config.get_configuration(ARGS)
    if WINDOW is not None:
        config["existing_window"] = WINDOW

    # Scenes
    scenes = manimlib.extract_scene.main(config)
    SCENES = scenes
    if len(scenes) > 0:
        window = scenes[0].window
        if window is not None:
            WINDOW = window
    for scene in scenes:
        scene.run()


if __name__ == "__main__":
    main()
