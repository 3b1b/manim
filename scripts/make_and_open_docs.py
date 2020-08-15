from pathlib import Path
import os
import webbrowser

path_makefile = Path(__file__).parents[1] / "docs"
os.system(f"cd {path_makefile} && make html")

website = path_makefile / "build" / "html" / "index.html"
webbrowser.open_new_tab(f"{website}")
#alternative to the upper line:
# webbrowser.get('firefox').open_new_tab(f"{website}")
