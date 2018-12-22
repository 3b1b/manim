#!/usr/bin/env python
import config
import extract_scene
import stream_starter

args = config.parse_cli()
if not args.livestream:
    config = config.get_configuration(args)
    extract_scene.main(config)
else:
    stream_starter.start_livestream(args.to_twitch)
