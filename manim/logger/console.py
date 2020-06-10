import json
from rich.console import Console
from rich.theme import Theme

def parseTheme(fp):
    with open(fp,'r') as f:
        content=f.read()
        theme=json.loads(content)
    theme['listScenes']='yellow'
    customTheme=Theme(theme)
    return customTheme
customTheme =  parseTheme("rich.json")
console = Console(theme=customTheme)