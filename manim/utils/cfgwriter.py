"""
cfgwriter.py
------------

Inputs the configuration files while checking it is valid. Can be executed by `manim-cfg` command.

"""
import os
import configparser

from .config_utils import _run_config, _paths_config_file

from rich.console import Console
from rich.progress import track
from rich.style import Style
from rich.errors import StyleSyntaxError


def check_valid_style(style):
    """Checks whether the entered color is a valid color according to rich
    Parameters
    ----------
    style : :class:`str`
        The style to check whether it is valid.
    Returns
    -------
    Boolean
        Returns whether it is valid style or not according to rich.
    """
    try:
        Style.parse(style)
        return True
    except StyleSyntaxError:
        return False


def main():
    successfully_read_files = _run_config()[-1]
    console = Console()
    config = configparser.ConfigParser()
    config.read(successfully_read_files)
    default = config["logger"]
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
        temp = default[key]
        del default[key]
        key = key.replace("_", ".")
        default[key] = temp
    for key in default:
        console.print("Enter the Style for %s" % key + ":", style=key, end="")
        temp = input()
        if temp:
            while not check_valid_style(temp):
                console.print(
                    "[red bold]Your Style is not valid. Try again.[/red bold]"
                )
                console.print("Enter the Style for %s" % key + ":", style=key, end="")
                temp = input()
            else:
                default[key] = temp
    for key in default:
        temp = default[key]
        del default[key]
        key = key.replace(".", "_")
        default[key] = temp
    config["logger"] = default
    console.print(
        "Do you want it as a default for the User?(y/n)[[n]]",
        style="dim purple",
        end="",
    )
    save_to_userpath = input()
    config_paths = _paths_config_file()
    if save_to_userpath.lower() == "y":
        if not os.path.exists(os.path.abspath(os.path.join(config_paths[1], ".."))):
            os.makedirs(os.path.abspath(os.path.join(config_paths[1], "..")))
        with open(config_paths[1], "w") as fp:
            config.write(fp)
        console.print(
            """A configuration file called [yellow]{}[/yellow] has been created with your required changes.
which would be used while running manim command. If you want to overide that 
you would have to create a manim.cfg in local directory.""".format(
                config_paths[1]
            )
        )
    else:
        with open(config_paths[2], "w") as fp:
            config.write(fp)
        console.print(
            """A configuration file called [yellow]{}[/yellow] has been created.
To save your theme please save that file and each time place it in your current working directory,
(the directory where you executed the command manim)""".format(
                config_paths[2]
            )
        )


if __name__ == "__main__":
    main()
