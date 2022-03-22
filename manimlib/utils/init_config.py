import os
import yaml
import inspect
import importlib
from typing import Any

from rich import box
from rich.rule import Rule 
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt, Confirm


def get_manim_dir() -> str:
    manimlib_module = importlib.import_module("manimlib")
    manimlib_dir = os.path.dirname(inspect.getabsfile(manimlib_module))
    return os.path.abspath(os.path.join(manimlib_dir, ".."))


def remove_empty_value(dictionary: dict[str, Any]) -> None:
    for key in list(dictionary.keys()):
        if dictionary[key] == "":
            dictionary.pop(key)
        elif isinstance(dictionary[key], dict):
            remove_empty_value(dictionary[key])


def init_customization() -> None:
    configuration = {
        "directories": {
            "mirror_module_path": False,
            "output": "",
            "raster_images": "",
            "vector_images": "",
            "sounds": "",
            "temporary_storage": "",
        },
        "tex": {
            "executable": "",
            "template_file": "",
            "intermediate_filetype": "",
            "text_to_replace": "[tex_expression]",
        },
        "universal_import_line": "from manimlib import *",
        "style": {
            "font": "Consolas",
            "background_color": "",
        },
        "window_position": "UR",
        "window_monitor": 0,
        "full_screen": False,
        "break_into_partial_movies": False,
        "camera_qualities": {
            "low": {
                "resolution": "854x480",
                "frame_rate": 15,
            },
            "medium": {
                "resolution": "1280x720",
                "frame_rate": 30,
            },
            "high": {
                "resolution": "1920x1080",
                "frame_rate": 60,
            },
            "ultra_high": {
                "resolution": "3840x2160",
                "frame_rate": 60,
            },
            "default_quality": "",
        }
    }

    console = Console()
    console.print(Rule("[bold]Configuration Guide[/bold]"))
    # print("Initialize configuration")
    try:
        scope = Prompt.ask(
            "  Select the scope of the configuration", 
            choices=["global", "local"],
            default="local"
        )

        console.print("[bold]Directories:[/bold]")
        dir_config = configuration["directories"]
        dir_config["output"] = Prompt.ask(
            "  Where should manim [bold]output[/bold] video and image files place [prompt.default](optional, default is none)",
            default="",
            show_default=False
        )
        dir_config["raster_images"] = Prompt.ask(
            "  Which folder should manim find [bold]raster images[/bold] (.jpg .png .gif) in "
            "[prompt.default](optional, default is none)",
            default="",
            show_default=False
        )
        dir_config["vector_images"] = Prompt.ask(
            "  Which folder should manim find [bold]vector images[/bold] (.svg .xdv) in "
            "[prompt.default](optional, default is none)",
            default="",
            show_default=False
        )
        dir_config["sounds"] = Prompt.ask(
            "  Which folder should manim find [bold]sound files[/bold] (.mp3 .wav) in "
            "[prompt.default](optional, default is none)",
            default="",
            show_default=False
        )
        dir_config["temporary_storage"] = Prompt.ask(
            "  Which folder should manim storage [bold]temporary files[/bold] "
            "[prompt.default](recommended, use system temporary folder by default)",
            default="",
            show_default=False
        )

        console.print("[bold]LaTeX:[/bold]")
        tex_config = configuration["tex"]
        tex = Prompt.ask(
            "  Select an executable program to use to compile a LaTeX source file",
            choices=["latex", "xelatex"],
            default="latex"
        )
        if tex == "latex":
            tex_config["executable"] = "latex"
            tex_config["template_file"] = "tex_template.tex"
            tex_config["intermediate_filetype"] = "dvi"
        else:
            tex_config["executable"] = "xelatex -no-pdf"
            tex_config["template_file"] = "ctex_template.tex"
            tex_config["intermediate_filetype"] = "xdv"
        
        console.print("[bold]Styles:[/bold]")
        configuration["style"]["background_color"] = Prompt.ask(
            "  Which [bold]background color[/bold] do you want [italic](hex code)",
            default="#333333"
        )

        console.print("[bold]Camera qualities:[/bold]")
        table = Table(
            "low", "medium", "high", "ultra_high",
            title="Four defined qualities",
            box=box.ROUNDED
        )
        table.add_row("480p15", "720p30", "1080p60", "2160p60")
        console.print(table)
        configuration["camera_qualities"]["default_quality"] = Prompt.ask(
            "  Which one to choose as the default rendering quality",
            choices=["low", "medium", "high", "ultra_high"],
            default="high"
        )

        write_to_file = Confirm.ask(
            "\n[bold]Are you sure to write these configs to file?[/bold]",
            default=True
        )
        if not write_to_file:
            raise KeyboardInterrupt

        global_file_name = os.path.join(get_manim_dir(), "manimlib", "default_config.yml")
        if scope == "global":
            file_name = global_file_name
        else:
            if os.path.exists(global_file_name):
                remove_empty_value(configuration)
            file_name = os.path.join(os.getcwd(), "custom_config.yml")
        with open(file_name, "w", encoding="utf-8") as f:
            yaml.dump(configuration, f)
        
        console.print(f"\n:rocket: You have successfully set up a {scope} configuration file!")
        console.print(f"You can manually modify it in: [cyan]`{file_name}`[/cyan]")

    except KeyboardInterrupt:
        console.print("\n[green]Exit configuration guide[/green]")
