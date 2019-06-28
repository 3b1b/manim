#!/usr/bin/env python
import sys, subprocess
import manimlib.config
import manimlib.constants
import manimlib.extract_scene
import manimlib.stream_starter
import manimlib.addon_helper


def main():
    if sys.argv[1] == "addon_info":
        subprocess.run([
            "python", "addon_info.py"
        ])
    else:
        print("Starting...", end="\r")

        addon_helper.read_addons(True)
        args = manimlib.config.parse_cli()
        
        if not args.livestream:
            config = manimlib.config.get_configuration(args)
            manimlib.constants.initialize_directories(config)
            addon_helper.pass_config_to_addons(config)
            manimlib.extract_scene.main(config)
        else:
            manimlib.stream_starter.start_livestream(
                to_twitch=args.to_twitch,
                twitch_key=args.twitch_key,
            )
