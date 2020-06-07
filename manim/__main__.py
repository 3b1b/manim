from . import extract_scene
from . import config
from . import constants


def main():
    args = config.parse_cli()
    cfg = config.get_configuration(args)
    config.initialize_directories(cfg)
    config.initialize_tex(cfg)
    extract_scene.main(cfg)


if __name__ == "__main__":
    main()
