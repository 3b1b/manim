#!/usr/bin/env python
from . import config
from . import constants


def main():
    args = config.parse_cli()
    cfg = config.get_configuration(args)
    constants.initialize_directories(cfg)
    from . import extract_scene
    extract_scene.main(cfg)
