#!/usr/bin/env python
from manimlib import __version__
import manimlib.config
import manimlib.logger
import manimlib.utils.init_config
from manimlib.reload_manager import ReloadManager


def main():
    """
    Main entry point for ManimGL.
    """
    print(f"ManimGL \033[32mv{__version__}\033[0m")

    args = manimlib.config.parse_cli()
    if args.version and args.file is None:
        return
    if args.log_level:
        manimlib.logger.log.setLevel(args.log_level)

    if args.config:
        manimlib.utils.init_config.init_customization()
        return

    reload_manager = ReloadManager()
    reload_manager.args = args
    reload_manager.run()


if __name__ == "__main__":
    main()
