#!/usr/bin/env python
import manimlib.config
import manimlib.extract_scene
import manimlib.utils.init_config


def main():
    args = manimlib.config.parse_cli()

    if args.config:
        manimlib.utils.init_config.init_customization()
    else:
        config = manimlib.config.get_configuration(args)
        scenes = manimlib.extract_scene.main(config)

        for scene in scenes:
            scene.run()

if __name__ == '__main__':
    main()
