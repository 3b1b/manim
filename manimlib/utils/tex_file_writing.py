import logging
import sys
import os
import hashlib

from manimlib.utils.directories import get_tex_dir
from manimlib.config import get_manim_dir
from manimlib.config import get_custom_defaults


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
        custom_defaults = get_custom_defaults()
        SAVED_TEX_CONFIG.update(custom_defaults["tex"])
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
    directory = get_tex_dir()
    tex_file = generate_tex_file(tex_file_content, directory)
    dvi_file = tex_to_dvi(tex_file)
    return dvi_to_svg(dvi_file)


def generate_tex_file(tex_file_content, directory):
    file_name = f"{tex_hash(tex_file_content)}.tex"
    path = os.path.join(directory, file_name)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(tex_file_content)
    return path


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
