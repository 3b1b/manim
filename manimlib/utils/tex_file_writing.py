import logging
import sys
import os
import hashlib
from contextlib import contextmanager

from manimlib.utils.directories import get_tex_dir
from manimlib.config import get_manim_dir
from manimlib.config import get_custom_config


SAVED_TEX_CONFIG = {}


def get_tex_config():
    """
    Returns a dict which should look something like this:
    {
        "executable": "latex",
        "template_file": "tex_template.tex",
        "intermediate_filetype": "dvi",
        "text_to_replace": "YourTextHere",
        "tex_body": "..."
    }
    """
    # Only load once, then save thereafter
    if not SAVED_TEX_CONFIG:
        custom_config = get_custom_config()
        SAVED_TEX_CONFIG.update(custom_config["tex"])
        # Read in template file
        template_filename = os.path.join(
            get_manim_dir(), "manimlib", "tex_templates",
            SAVED_TEX_CONFIG["template_file"],
        )
        with open(template_filename, "r") as file:
            SAVED_TEX_CONFIG["tex_body"] = file.read()
    return SAVED_TEX_CONFIG


def tex_hash(tex_file_content):
    # Truncating at 16 bytes for cleanliness
    hasher = hashlib.sha256(tex_file_content.encode())
    return hasher.hexdigest()[:16]


def tex_to_svg_file(tex_file_content):
    svg_file = os.path.join(
        get_tex_dir(), tex_hash(tex_file_content) + ".svg"
    )
    if not os.path.exists(svg_file):
        # If svg doesn't exist, create it
        tex_to_svg(tex_file_content, svg_file)
    return svg_file


def tex_to_svg(tex_file_content, svg_file):
    tex_file = svg_file.replace(".svg", ".tex")
    with open(tex_file, "w", encoding="utf-8") as outfile:
        outfile.write(tex_file_content)
    svg_file = dvi_to_svg(tex_to_dvi(tex_file))

    # Cleanup superfluous documents
    tex_dir, name = os.path.split(svg_file)
    stem, end = name.split(".")
    for file in filter(lambda s: s.startswith(stem), os.listdir(tex_dir)):
        if not file.endswith(end):
            os.remove(os.path.join(tex_dir, file))

    return svg_file


def tex_to_dvi(tex_file):
    tex_config = get_tex_config()
    program = tex_config["executable"]
    file_type = tex_config["intermediate_filetype"]
    result = tex_file.replace(".tex", "." + file_type)
    if not os.path.exists(result):
        commands = [
            program,
            "-interaction=batchmode",
            "-halt-on-error",
            f"-output-directory=\"{os.path.dirname(tex_file)}\"",
            f"\"{tex_file}\"",
            ">",
            os.devnull
        ]
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            log_file = tex_file.replace(".tex", ".log")
            logging.log(
                logging.ERROR,
                "\n\n LaTeX Error!  Not a worry, it happens to the best of us.\n"
            )
            with open(log_file, "r") as file:
                for line in file.readlines():
                    if line.startswith("!"):
                        print(line[1:])
                        logging.log(logging.INFO, line)
            sys.exit(2)
    return result


def dvi_to_svg(dvi_file, regen_if_exists=False):
    """
    Converts a dvi, which potentially has multiple slides, into a
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    file_type = get_tex_config()["intermediate_filetype"]
    result = dvi_file.replace("." + file_type, ".svg")
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            "\"{}\"".format(dvi_file),
            "-n",
            "-v",
            "0",
            "-o",
            "\"{}\"".format(result),
            ">",
            os.devnull
        ]
        os.system(" ".join(commands))
    return result


# TODO, perhaps this should live elsewhere
@contextmanager
def display_during_execution(message):
    # Only show top line
    to_print = message.split("\n")[0]
    try:
        print(to_print, end="\r")
        yield
    finally:
        print(" " * len(to_print), end="\r")
