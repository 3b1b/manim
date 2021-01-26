import os
import sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath('../../'))


project = 'manim'
copyright = '- This document has been placed in the public domain.'
author = 'TonyCrane'

release = ''

extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc', 
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
    'manim_example_ext'
]

autoclass_content = 'both'
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'default'

html_static_path = ["_static"]
html_css_files = ["custom.css", "colors.css"]
html_theme = 'furo'  # pip install furo==2020.10.5b9
html_favicon = '_static/icon.png'
html_logo = '../../logo/transparent_graph.png'
html_theme_options = {
    "sidebar_hide_name": True,
}
