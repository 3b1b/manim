"""
cfg_subcmd.py
------------

General Config File Managing Utilities.
The functions below can be called via the `manim cfg` subcommand.

"""
import os
import configparser

from .config_utils import _run_config, _paths_config_file, finalized_configs_dict

from rich.console import Console
from rich.progress import track
from rich.style import Style
from rich.errors import StyleSyntaxError

__all__ = ["write","show","export"]

RICH_COLOUR_INSTRUCTIONS = """[red]The default colour is used by the input statement.
If left empty, the default colour will be used.[/red]
[magenta] For a full list of styles, visit[/magenta] [green]https://rich.readthedocs.io/en/latest/style.html[/green]"""

console = Console()

def is_valid_style(style):
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


def replace_keys(default):
    """Replaces _ to . and viceversa in a dictionary for rich
    Parameters
    ----------
    default : :class:`dict`
        The dictionary to check and replace
    Returns
    -------
    :class:`dict`
        The dictionary which is modified by replcaing _ with . and viceversa
    """
    for key in default:
        if "_" in key:
            temp = default[key]
            del default[key]
            key = key.replace("_", ".")
            default[key] = temp
        else:
            temp = default[key]
            del default[key]
            key = key.replace(".", "_")
            default[key] = temp
    return default


def write(level=None):
    console.print("[yellow bold]Manim Configuration File Writer[/yellow bold]", justify="center")
    config = _run_config()[1]

    for category in config:
        console.print(f"{category}",style="bold green underline")
        default = config[category]
        if category == "logger":
            console.print(RICH_COLOUR_INSTRUCTIONS)
            default = replace_keys(default)
            for key in default:
                console.print(f"Enter the style for {key}:", style=key, end="")
                temp = input()
                if temp:
                    while not is_valid_style(temp):
                        console.print("[red bold]Invalid style. Try again.[/red bold]")
                        console.print(f"Enter the style for {key}:", style=key, end="")
                        temp = input()
                    else:
                        default[key] = temp
            default = replace_keys(default)

        else:
            for key in default:
                if default[key] in ["True","False"]:
                    console.print(
                        f"Enter value for {key} (defaults to {default[key]}):", end="")
                    temp = input()
                    if temp:
                        while not temp.lower().capitalize() in ["True","False"]:
                            console.print(
                                "[red bold]Invalid value. Try again.[/red bold]")
                            console.print(
                                f"Enter the style for {key}:", style=key, end="")
                            temp = input()
                        else:
                            default[key] = temp
        config[category] = dict(default)

    if level is None:
        console.print(
            "Do you want to save this as the default for this User?(y/n)[[n]]",
            style="dim purple",
            end="",
        )
        save_to_userpath = input()
    else:
        save_to_userpath = ""

    config_paths = _paths_config_file() + [os.path.abspath("manim.cfg")]
    if save_to_userpath.lower() == "y" or level=="user":
        if not os.path.exists(os.path.abspath(os.path.join(config_paths[1], ".."))):
            os.makedirs(os.path.abspath(os.path.join(config_paths[1], "..")))
        with open(config_paths[1], "w") as fp:
            config.write(fp)
        console.print(
            f"""A configuration file at [yellow]{config_paths[1]}[/yellow] has been created with your required changes.
This will be used when running the manim command. If you want to override this config,
you will have to create a manim.cfg in the local directory, where you want those changes to be overridden."""
        )
    else:
        with open(config_paths[2], "w") as fp:
            config.write(fp)
        console.print(
            f"""A configuration file at [yellow]{config_paths[2]}[/yellow] has been created.
To save your theme please save that file and place it in your current working directory, from where you run the manim command."""
        )

def show():
    current_config = finalized_configs_dict()
    for category in current_config:
        console.print(f"{category}",style="bold green underline")
        for entry in current_config[category]:
            if category=="logger":
                console.print(f"{entry} :",end="")
                console.print(
                    f" {current_config[category][entry]}",
                    style=current_config[category][entry]
                    )
            else:
                console.print(f"{entry} : {current_config[category][entry]}")
        console.print("\n")

def export(path):
    config = _run_config()[1]
    if os.path.abspath(path) == os.path.abspath(os.getcwd()):
        console.print(
            """You are reading the config from the same directory you are exporting to.
This means that the exported config will overwrite the config for this directory.
Are you sure you want to continue?[y/n]""",
            style="red bold", end=""
            )
        proceed = True if input().lower()=="y" else False
    else:
        proceed = True
    if proceed:
        if not os.path.isdir(path):
            console.print(f"Creating folder: {path}.",style="red bold")
            os.mkdir(path)
        with open(os.path.join(path,"manim.cfg"),"w") as outpath:
            config.write(outpath)
            from_path = os.path.join(os.getcwd(),'manim.cfg')
            to_path = os.path.join(path,'manim.cfg')
        console.print(f"Exported final Config at {from_path} to {to_path}.")
    else:
        console.print("Could NOT write config.", style="red bold")
