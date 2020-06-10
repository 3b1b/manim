from rich.console import Console
from rich.progress import track
import json


if __name__=="__main__":
    console = Console()
    default={"logging.keyword":"bold yellow",
        "logging.level.notset":"dim",
        "logging.level.debug":"green",
        "logging.level.info":"blue",
        "logging.level.warning":"red",
        "logging.level.error": "red bold",
        "logging.level.critical": "red bold reverse",
        "log.level":"",
        "log.time": "cyan dim",
        "log.message": "",
        "log.path": "dim",
        }
    console.print("[yellow bold]Manim Logger Configuration Editor[/yellow bold]",justify="center")
    console.print("[red]The default colour is shown as input Statement.\nIf left empty default value will be assigned.[/red]")
    console.print("[magenta]Please follow the link for available styles.[/magenta][link=https://rich.readthedocs.io/en/latest/style.html]docs[/link]")
    for key in default:
        console.print('Enter the Style for %s'%key+':',style=key,end='')
        temp=input()
        if temp:
            default[key]=temp
    for n in track(range(100), description="Converting to JSON"):
        with open("rich.cfg","w") as fp:
            json.dump(default,fp,indent=4)
    console.print("A file called [yellow]rich.cfg[/yellow] is created. To save your theme please save that file and each time \nplace it in you current working directory(The directory where you execute manim command) for the your theme to be displayed.")