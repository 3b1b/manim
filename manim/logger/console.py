import configparser
from rich.console import Console
from rich.theme import Theme

def parseTheme(fp):
    config = configparser.ConfigParser()
    config.read(fp)
    theme=dict(config['log.color'])
    customTheme=Theme(theme)
    return customTheme
try:
    customTheme =  parseTheme("manim.cfg")
    console = Console(theme=customTheme)
except KeyError:
    console = Console()

