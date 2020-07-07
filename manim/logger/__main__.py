from rich.console import Console
from rich.progress import track
from rich.color import Color
import configparser


def check_valid_colour(color):
    '''Checks whether the entered color is a valid color according to rich
    Parameters
    ----------
    color : :class:`str`
        The color to check whether it is valid.
    Returns
    -------
    Boolean
        Returns whether it is valid color or not.
    '''
    try:
        Color.parse(color) is None
        return True
    except:
        return False
def main():
    console = Console()
    config = configparser.ConfigParser()
    config.read('manim.cfg')
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
            while check_valid_colour(temp)==False:
                console.print("[red bold]Your Style is not valid. Try again.[/red bold]")
                console.print('Enter the Style for %s'%key+':',style=key,end='')
                temp=input()
            else:
                default[key]=temp
    config['log.color']=default
    for n in track(range(100), description="Converting to Manim.cfg"):
        with open("manim.cfg","w") as fp:
            config.write(fp)
    console.print("A file called [yellow]manim.cfg[/yellow] is created. To save your theme please save that file and each time \nplace it in you current working directory(The directory where you execute manim command) for the your theme to be displayed.")
if __name__=="__main__":
    main()