#!/usr/bin/env python
import manimlib.config
import manimlib.constants
import manimlib.extract_scene


def main():
    args = manimlib.config.parse_cli()
    config = manimlib.config.get_configuration(args)
    manimlib.constants.initialize_directories(config)
    manimlib.extract_scene.main(config)
