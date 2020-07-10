"""
cfgwriter.py
------------

Inputs the configuration files while checking it is valid.

"""
from os import path
import configparser

from .config_utils import successfully_read_files

from rich.console import Console
from rich.progress import track
from rich.color import Color


def check_valid_colour(color):
    """Checks whether the entered color is a valid color according to rich
    Parameters
    ----------
    color : :class:`str`
        The color to check whether it is valid.
    Returns
    -------
    Boolean
        Returns whether it is valid color or not.
    """
    try:
        Color.parse(color)
        return True
    except:
        return False


def main():
    console = Console()
    config = configparser.ConfigParser()
    config.read( successfully_read_files )
    default = {
        "logging.keyword": "bold yellow",
        "logging.level.notset": "dim",
        "logging.level.debug": "green",
        "logging.level.info": "blue",
        "logging.level.warning": "red",
        "logging.level.error": "red bold",
        "logging.level.critical": "red bold reverse",
        "log.level": "",
        "log.time": "cyan dim",
        "log.message": "",
        "log.path": "dim",
    }
    console.print(
        "[yellow bold]Manim Logger Configuration Editor[/yellow bold]", justify="center"
    )
    console.print(
        "[red]The default colour is shown as input Statement.\nIf left empty default value will be assigned.[/red]"
    )
    console.print(
        "[magenta]Please follow the link for available styles.[/magenta][link=https://rich.readthedocs.io/en/latest/style.html]docs[/link]"
    )
    for key in default:
        console.print("Enter the Style for %s" % key + ":", style=key, end="")
        temp = input()
        if temp:
            while not check_valid_colour(temp):
                console.print(
                    "[red bold]Your Style is not valid. Try again.[/red bold]"
                )
                console.print("Enter the Style for %s" % key + ":", style=key, end="")
                temp = input()
            else:
                default[key] = temp
    config["log.color"] = default
    for n in track(range(100), description="Converting to Manim.cfg"):
        with open("manim.cfg", "w") as fp:
            config.write(fp)
    console.print(
        """A configuration file called [yellow]manim.cfg[/yellow] has been created.
To save your theme please save that file and each time place it in your current working directory,
(the directory where you executed the command manim)"""
    )


if __name__ == "__main__":
    main()
