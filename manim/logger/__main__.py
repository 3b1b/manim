from .console import console


if __name__=="__main__":
    default={"logging.keyword":"bold yellow",
        "logging.level.notset":"dim",
        "logging.level.debug":"green",
        "logging.level.info":"blue",
        "logging.level.warning":"red",
        "logging.level.error": "red bold",
        "logging.level.critical": "red bold reverse",
        "log.level":None,
        "log.time": "cyan dim",
        "log.message": None,
        "log.path": "dim",
        }
    console.print("[yellow bold]Manim Logger Configuration Editor[/yellow bold]",justify="center")
    for key in default:
        console.print('Enter the Style for %s'%key+':',style=key)
        default[key]=