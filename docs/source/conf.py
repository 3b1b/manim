import os
import sys
sys.path.insert(0, os.path.abspath('../../'))


project = 'manim'
copyright = '- This document has been placed in the public domain.'
author = 'TonyCrane'

release = '0.1'

extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc', 
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme'
]

autoclass_content = 'both'
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'default'

# html_static_path = ['assets']
html_theme = 'sphinx_rtd_theme'
# html_favicon = '../../logo/graph.png'
html_logo = '../../logo/transparent_graph.png'
html_theme_options = {
    'logo_only': True,
    'style_nav_header_background': '#343131',
}
