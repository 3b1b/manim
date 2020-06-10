import json
from rich.console import Console
from rich.theme import Theme

def parseTheme(fp):
    with open(fp,'r') as f:
        content=f.read()
        theme=json.loads(content)
    customTheme=Theme(theme)
    return customTheme
try:
    customTheme =  parseTheme("rich.cfg")
    console = Console(theme=customTheme)
except:
    console = Console()

