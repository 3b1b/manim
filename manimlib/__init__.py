#!/usr/bin/env python
import sys, subprocess
import manimlib.config
import manimlib.constants
import manimlib.extract_scene
import manimlib.stream_starter
import manimlib.addon_loader


def main():
    print("Starting...", end="\r")

    manimlib.addon_loader.read_addons(True)
    args = manimlib.config.parse_cli()

    if not args.livestream:
        config = manimlib.config.get_configuration(args)
        manimlib.constants.initialize_directories(config)
        manimlib.addon_loader.pass_config_to_addons(config)
        manimlib.extract_scene.main(config)
    else:
        manimlib.stream_starter.start_livestream(
            to_twitch=args.to_twitch,
            twitch_key=args.twitch_key,
        )
