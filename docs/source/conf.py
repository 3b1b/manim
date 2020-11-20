# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import subprocess
import sys
from distutils.sysconfig import get_python_lib
from pathlib import Path

sys.path.insert(0, os.path.abspath("."))


if os.environ.get("READTHEDOCS") == "True":
    site_path = get_python_lib()
    # we need to add ffmpeg to the path
    ffmpeg_path = os.path.join(site_path, "imageio_ffmpeg", "binaries")
    # the included binary is named ffmpeg-linux..., create a symlink
    [ffmpeg_bin] = [
        file for file in os.listdir(ffmpeg_path) if file.startswith("ffmpeg-")
    ]
    os.symlink(
        os.path.join(ffmpeg_path, ffmpeg_bin), os.path.join(ffmpeg_path, "ffmpeg")
    )
    os.environ["PATH"] += os.pathsep + ffmpeg_path


# -- Project information -----------------------------------------------------

project = "Manim"
copyright = "2020, The Manim Community Dev Team"
author = "The Manim Community Dev Team"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "recommonmark",
    "sphinx_copybutton",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.linkcode",
    "sphinxext.opengraph",
    "manim_directive",
]

# Automatically generate stub pages when using the .. autosummary directive
autosummary_generate = True

# generate documentation from type hints
autodoc_typehints = "description"
autoclass_content = "both"

# controls whether functions documented by the autofunction directive
# appear with their full module names
add_module_names = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Custom section headings in our documentation
napoleon_custom_sections = ["Tests", ("Test", "Tests")]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import guzzle_sphinx_theme

html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_theme = "guzzle_sphinx_theme"
html_favicon = str(Path("_static/favicon.ico"))

# There's a standing issue with Sphinx's new-style sidebars.  This is a
# workaround.  Taken from
# https://github.com/guzzle/guzzle_sphinx_theme/issues/33#issuecomment-637081826
html_sidebars = {"**": ["logo-text.html", "globaltoc.html", "searchbox.html"]}

# Register the theme as an extension to generate a sitemap.xml
extensions.append("guzzle_sphinx_theme")

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# This specifies any additional css files that will override the theme's
html_css_files = ["custom.css"]

# source links to github
def linkcode_resolve(domain, info):
    if domain != "py":
        return None
    if not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    version = os.getenv("READTHEDOCS_VERSION", "master")
    if version == "latest":
        version = "master"
    return f"https://github.com/ManimCommunity/manim/blob/{version}/{filename}.py"


# external links
extlinks = {
    "issue": ("https://github.com/ManimCommunity/manim/issues/%s", "issue "),
    "pr": ("https://github.com/ManimCommunity/manim/pull/%s", "pull request "),
}

# opengraph settings
ogp_image = "https://www.manim.community/logo.png"
ogp_site_name = "Manim Community | Documentation"
ogp_site_url = "https://docs.manim.community/"
