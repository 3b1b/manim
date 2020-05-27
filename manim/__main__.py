from .config import config
from . import extract_scene
from . import constants


def main():
    extract_scene.main(config)


if __name__ == "__main__":
    main()
