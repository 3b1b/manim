"""Interface for writing, compiling, and converting ``.tex`` files.

.. SEEALSO::

    :mod:`.mobject.svg.tex_mobject`

"""

import os
import hashlib
from pathlib import Path

from .. import file_writer_config, config, logger


def tex_hash(expression):
    id_str = str(expression)
    hasher = hashlib.sha256()
    hasher.update(id_str.encode())
    # Truncating at 16 bytes for cleanliness
    return hasher.hexdigest()[:16]


def tex_to_svg_file(expression, source_type, tex_template=None):
    if tex_template is None:
        tex_template = config["tex_template"]
    tex_file = generate_tex_file(expression, tex_template, source_type)
    dvi_file = tex_to_dvi(tex_file, tex_template.use_ctex, tex_template.tex_compiler)
    return dvi_to_svg(
        dvi_file, use_ctex=tex_template.use_ctex, tex_compiler=tex_template.tex_compiler
    )


def generate_tex_file(expression, tex_template, source_type):
    if source_type == "text":
        output = tex_template.get_text_for_text_mode(expression)
    elif source_type == "tex":
        output = tex_template.get_text_for_tex_mode(expression)

    tex_dir = file_writer_config["tex_dir"]
    if not os.path.exists(tex_dir):
        os.makedirs(tex_dir)

    result = os.path.join(tex_dir, tex_hash(output)) + ".tex"
    if not os.path.exists(result):
        logger.info('Writing "%s" to %s' % ("".join(expression), result))
        with open(result, "w", encoding="utf-8") as outfile:
            outfile.write(output)
    return result


def tex_compilation_command(compiler, tex_file, tex_dir):
    if compiler["command"] in {"latex", "pdflatex", "luatex", "lualatex"}:
        commands = [
            compiler["command"],
            "-interaction=batchmode",
            f'-output-format="{compiler["output_format"][1:]}"',
            "-halt-on-error",
            f'-output-directory="{tex_dir}"',
            f'"{tex_file}"',
            ">",
            os.devnull,
        ]
    elif compiler["command"] == "xelatex":
        if compiler["output_format"] == ".xdv":
            outflag = "-no-pdf"
        elif compiler["output_format"] == ".pdf":
            outflag = ""
        else:
            raise ValueError("xelatex output is either pdf or xdv")
        commands = [
            "xelatex",
            outflag,
            "-interaction=batchmode",
            "-halt-on-error",
            '-output-directory="{}"'.format(tex_dir),
            '"{}"'.format(tex_file),
            ">",
            os.devnull,
        ]
    else:
        raise ValueError(f"Tex compiler {compiler['command']} unknown.")
    return " ".join(commands)


def tex_to_dvi(tex_file, use_ctex=False, tex_compiler=None):
    if tex_compiler is None:
        tex_compiler = (
            {"command": "xelatex", "output_format": ".xdv"}
            if use_ctex
            else {"command": "latex", "output_format": ".dvi"}
        )
    result = tex_file.replace(".tex", tex_compiler["output_format"])
    result = Path(result).as_posix()
    tex_file = Path(tex_file).as_posix()
    tex_dir = Path(file_writer_config["tex_dir"]).as_posix()
    if not os.path.exists(result):
        command = tex_compilation_command(tex_compiler, tex_file, tex_dir)
        exit_code = os.system(command)
        if exit_code != 0:
            log_file = tex_file.replace(".tex", ".log")
            raise ValueError(
                f"{tex_compiler['command']} error converting to"
                f" {tex_compiler['output_format'][1:]}. See log output above or"
                f" the log file: {log_file}"
            )
    return result


def dvi_to_svg(
    dvi_file, use_ctex=False, tex_compiler=None, regen_if_exists=False, page=1
):
    """
    Converts a dvi, xdv, or pdf file into an svg using dvisvgm.
    """
    if tex_compiler is None:
        tex_compiler = (
            {"command": "xelatex", "output_format": ".xdv"}
            if use_ctex
            else {"command": "latex", "output_format": ".dvi"}
        )
    result = dvi_file.replace(tex_compiler["output_format"], ".svg")
    result = Path(result).as_posix()
    dvi_file = Path(dvi_file).as_posix()
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            "--pdf" if tex_compiler["output_format"] == ".pdf" else "",
            "-p " + str(page),
            '"{}"'.format(dvi_file),
            "-n",
            "-v 0",
            "-o " + f'"{result}"',
            ">",
            os.devnull,
        ]
        os.system(" ".join(commands))
    return result
