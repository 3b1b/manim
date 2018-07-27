from __future__ import print_function
import os
import sys

from constants import TEX_DIR
from constants import TEX_TEXT_TO_REPLACE


def tex_hash(expression, template_tex_file):
    """Sometimes the hash function returns negative
    value and the LaTex compiler gets confused, so to get around this
    problem, the 1st character of the hash has been striped off."""

    return str(hash(expression + template_tex_file))[1:]


def tex_to_svg_file(expression, template_tex_file):
    tex_file = generate_tex_file(expression, template_tex_file)
    dvi_file = tex_to_dvi(tex_file)
    return dvi_to_svg(dvi_file)


def generate_tex_file(expression, template_tex_file):
    result = os.path.join(
        TEX_DIR,
        tex_hash(expression, template_tex_file)
    ) + ".tex"
    if not os.path.exists(result):
        print("Writing \"%s\" to %s" % (
            "".join(expression), result
        ))
        with open(template_tex_file, "r") as infile:
            body = infile.read()
            body = body.replace(TEX_TEXT_TO_REPLACE, expression)
        with open(result, "w") as outfile:
            outfile.write(body)
    return result


def get_null():
    if os.name == "nt":
        return "NUL"
    return "/dev/null"


def tex_to_dvi(tex_file):
    commands = [
        "latex",
        "-interaction=batchmode",
        "-halt-on-error",
        "-output-directory=" + TEX_DIR,
        tex_file,
    ]  # This is the Latex compiler
    falloff_commands = [
        "pdflatex",
        "-interaction=batchmode",
        "-halt-on-error",
        "-output-directory=" + TEX_DIR,
        "-output-format=dvi",
        tex_file,
    ]  # This is the PdfLatex compiler

    result = tex_file.replace(".tex", ".dvi")

    if not os.path.exists(result):
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            # If the Latex compiler doesnot work, the pdflatex compiler is used
            exit_code = os.system(" ".join(falloff_commands))
            if exit_code != 0:
                log_file = tex_file.replace(".tex", ".log")

                raise Exception(
                    "Latex error converting to dvi. "
                    "See log output above or the log file: %s \n"
                    "Your can try few things to resolve the problem,"
                    "\n"
                    "1. Make sure your have latex installed.\n"
                    "2. Make sure all the plugins needed is installed\n"
                    "for Debian-Based Linux distribution, try ```sudo apt-get"
                    "install texlive-full" % log_file)

    return result


def dvi_to_svg(dvi_file, regen_if_exists=False):
    """
    Converts a dvi, which potentially has multiple slides, into a
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    result = dvi_file.replace(".dvi", ".svg")
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            dvi_file,
            "-n",
            "-v",
            "0",
            "-o",
            result,
        ]
        os.system(" ".join(commands))
    return result
