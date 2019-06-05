#!/usr/bin/env python
import manimlib.config
import manimlib.constants
import manimlib.extract_scene
import manimlib.stream_starter


def main():
    args = manimlib.config.parse_cli()
    if not args.livestream:
        config = manimlib.config.get_configuration(args)
        manimlib.constants.initialize_directories(config)
        manimlib.extract_scene.main(config)
    else:
        manimlib.stream_starter.start_livestream(
            to_twitch=args.to_twitch,
            twitch_key=args.twitch_key,
        )
