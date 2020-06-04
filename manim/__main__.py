from .config import initialize_tex, config
from . import extract_scene
from . import constants


def main():
    initialize_tex(config)
    extract_scene.main(config)



if __name__ == "__main__":
    main()
