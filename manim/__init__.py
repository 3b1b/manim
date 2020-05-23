#!/usr/bin/env python
from . import extract_scene
from . import config
from . import constants


def main():    
    args = config.parse_cli()
    cfg = config.get_configuration(args)
    config.initialize_directories(cfg)
    extract_scene.main(cfg)
