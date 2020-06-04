import os
import hashlib

from pathlib import Path

from .. import constants
from .. import dirs
from ..logger import logger

def tex_hash(expression):
    id_str = str(expression)
    hasher = hashlib.sha256()
    hasher.update(id_str.encode())
    # Truncating at 16 bytes for cleanliness
    return hasher.hexdigest()[:16]

def tex_to_svg_file(expression, source_type):
    tex_template = constants.TEX_TEMPLATE
    tex_file = generate_tex_file(expression, tex_template, source_type)
    dvi_file = tex_to_dvi(tex_file, tex_template.use_ctex)
    return dvi_to_svg(dvi_file, use_ctex=tex_template.use_ctex)

def generate_tex_file(expression, tex_template, source_type):
    if source_type == "text":
        output = tex_template.get_text_for_text_mode(expression)
    elif source_type == "tex":
        output = tex_template.get_text_for_tex_mode(expression)

    result = os.path.join(
        dirs.TEX_DIR,
        tex_hash(output)
    ) + ".tex"
    if not os.path.exists(result):
        logger.info("Writing \"%s\" to %s" % (
            "".join(expression), result
        ))
        with open(result, "w", encoding="utf-8") as outfile:
            outfile.write(output)
    return result


def tex_to_dvi(tex_file, use_ctex = False):
    result = tex_file.replace(".tex", ".dvi" if not use_ctex else ".xdv")
    result = Path(result).as_posix()
    tex_file = Path(tex_file).as_posix()
    tex_dir = Path(dirs.TEX_DIR).as_posix()
    if not os.path.exists(result):
        commands = [
            "latex",
            "-interaction=batchmode",
            "-halt-on-error",
            "-output-directory=\"{}\"".format(tex_dir),
            "\"{}\"".format(tex_file),
            ">",
            os.devnull
        ] if not use_ctex else [
            "xelatex",
            "-no-pdf",
            "-interaction=batchmode",
            "-halt-on-error",
            "-output-directory=\"{}\"".format(tex_dir),
            "\"{}\"".format(tex_file),
            ">",
            os.devnull
        ]
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            log_file = tex_file.replace(".tex", ".log")
            raise Exception(
                ("LaTeX error converting to dvi. " if not use_ctex
                else "XeLaTeX error converting to xdv. ") +
                "See log output above or the log file: %s" % log_file)
    return result


def dvi_to_svg(dvi_file, use_ctex=False, regen_if_exists=False):
    """
    Converts a dvi, which potentially has multiple slides, into a
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    result = dvi_file.replace(".dvi" if not use_ctex else ".xdv", ".svg")
    result = Path(result).as_posix()
    dvi_file = Path(dvi_file).as_posix()
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
