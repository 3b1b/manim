from __future__ import annotations

from contextlib import contextmanager
import os
import re
import yaml

from manimlib.config import get_custom_config
from manimlib.config import get_manim_dir
from manimlib.logger import log
from manimlib.utils.directories import get_tex_dir
from manimlib.utils.simple_functions import hash_string


SAVED_TEX_CONFIG = {}


def get_tex_template_config(template_name: str) -> dict[str, str]:
    name = template_name.replace(" ", "_").lower()
    with open(os.path.join(
        get_manim_dir(), "manimlib", "tex_templates.yml"
    ), encoding="utf-8") as tex_templates_file:
        templates_dict = yaml.safe_load(tex_templates_file)
    if name not in templates_dict:
        log.warning(
            "Cannot recognize template '%s', falling back to 'default'.",
            name
        )
        name = "default"
    return templates_dict[name]


def get_tex_config() -> dict[str, str]:
    """
    Returns a dict which should look something like this:
    {
        "template": "default",
        "compiler": "latex",
        "documentclass": \documentclass[preview]{standalone},
        "preamble": "..."
    }
    """
    # Only load once, then save thereafter
    if not SAVED_TEX_CONFIG:
        template_name = get_custom_config()["style"]["tex_template"]
        template_config = get_tex_template_config(template_name)
        SAVED_TEX_CONFIG.update({
            "template": template_name,
            "compiler": template_config["compiler"],
            "documentclass": template_config["documentclass"],
            "preamble": template_config["preamble"]
        })
    return SAVED_TEX_CONFIG


def tex_content_to_svg_file(
    content: str, template: str, additional_preamble: str,
    short_tex: str, documentclass: str="", pdf_flag: bool=True
) -> str:
    tex_config = get_tex_config()
    if not template or template == tex_config["template"]:
        compiler = tex_config["compiler"]
        _documentclass = tex_config["documentclass"]
        preamble = tex_config["preamble"]
    else:
        config = get_tex_template_config(template)
        compiler = config["compiler"]
        _documentclass = tex_config["documentclass"]
        preamble = config["preamble"]

    if additional_preamble:
        preamble += "\n" + additional_preamble
        
    if documentclass is None or documentclass == "":
        documentclass = _documentclass
    
    full_tex = "\n\n".join((
        documentclass,
        preamble,
        "\\begin{document}",
        content,
        "\\end{document}"
    )) + "\n"

    svg_file = os.path.join(
        get_tex_dir(), hash_string(full_tex) + ".svg"
    )
    if not os.path.exists(svg_file):
        # If svg doesn't exist, create it
        with display_during_execution("Writing " + short_tex):
            create_tex_svg(full_tex, svg_file, compiler, pdf_flag)
    return svg_file


def create_tex_svg(full_tex: str, svg_file: str, compiler: str, pdf_flag: bool=True) -> None:    
    if compiler == "latex":
        if pdf_flag:
            program ="latex -output-format=pdf"
            dvi_ext = ".pdf"
        else:
            program = "latex"
            dvi_ext = ".dvi"
    elif compiler == "xelatex":
        if pdf_flag:
            program ="xelatex"
            dvi_ext = ".pdf"
        else:
            program = "xelatex -no-pdf"
            dvi_ext = ".xdv"
    elif compiler == "lualatex":
        if pdf_flag:
            program = "lualatex -output-format=pdf"
            dvi_ext = ".pdf"
        else:
            program = "lualatex"
            dvi_ext = ".dvi"
    else:
        raise NotImplementedError(
            f"Compiler '{compiler}' is not implemented"
        )

    # Write tex file
    root, _ = os.path.splitext(svg_file)
    with open(root + ".tex", "w", encoding="utf-8") as tex_file:
        tex_file.write(full_tex)

    # tex to dvi,xdv or pdf
    if os.system(" ".join((
        program,
        "-interaction=batchmode",
        "-halt-on-error",
        f"-output-directory=\"{os.path.dirname(svg_file)}\"",
        f"\"{root}.tex\"",
        ">",
        os.devnull
    ))):
        log.error(
            "LaTeX Error!  Not a worry, it happens to the best of us."
        )
        error_str = ""
        with open(root + ".log", "r", encoding="utf-8") as log_file:
            error_match_obj = re.search(r"(?<=\n! ).*\n.*\n", log_file.read())
            if error_match_obj:
                error_str = error_match_obj.group()
                log.debug(
                    f"The error could be:\n`{error_str}`",
                )
        raise LatexError(error_str)

    if pdf_flag:
        # pdf to svg
        os.system(" ".join((
            "dvisvgm",
            "--pdf",
            f"\"{root}{dvi_ext}\"",
            "-n",
            "-v",
            "0",
            "-o",
            f"\"{svg_file}\"",
            ">",
            os.devnull
        )))
    
    else:
        # dvi,xdv to svg
        os.system(" ".join((
            "dvisvgm",
            f"\"{root}{dvi_ext}\"",
            "-n",
            "-v",
            "0",
            "-o",
            f"\"{svg_file}\"",
            ">",
            os.devnull
        )))

    # Cleanup superfluous documents
    for ext in (".tex", dvi_ext, ".log", ".aux"):
        try:
            os.remove(root + ext)
        except FileNotFoundError:
            pass


# TODO, perhaps this should live elsewhere
@contextmanager
def display_during_execution(message: str):
    # Merge into a single line
    to_print = message.replace("\n", " ")
    max_characters = os.get_terminal_size().columns - 1
    if len(to_print) > max_characters:
        to_print = to_print[:max_characters - 3] + "..."
    try:
        print(to_print, end="\r")
        yield
    finally:
        print(" " * len(to_print), end="\r")


class LatexError(Exception):
    pass
