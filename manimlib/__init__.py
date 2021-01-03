#!/usr/bin/env python
import manimlib.config
import manimlib.constants
import manimlib.extract_scene


def main():
    args = manimlib.config.parse_cli()
    config = manimlib.config.get_configuration(args)
    scenes = manimlib.extract_scene.main(config)

    for scene in scenes:
        scene.run()
