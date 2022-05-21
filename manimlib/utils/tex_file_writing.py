from __future__ import annotations

import os
import re

from manimlib.config import get_custom_config
from manimlib.constants import PRESET_PREAMBLE
from manimlib.logger import log
from manimlib.utils.directories import get_tex_dir
from manimlib.utils.simple_functions import hash_string


class LatexError(Exception):
    pass


class TexTemplate:
    def __init__(self, preamble_type: str | None = None):
        tex_config = get_custom_config()["tex"]
        self.executable = tex_config["executable"]
        self.dvi_ext = tex_config["intermediate_filetype"]
        if preamble_type is None:
            preamble_type = tex_config["preamble"]
        self.preamble = list(PRESET_PREAMBLE.get(
            preamble_type, PRESET_PREAMBLE["default"]
        ))

    def __hash__(self) -> int:
        return hash(self.get_tex_file_content(""))

    def get_tex_file_content(self, content: str) -> str:
        return "\n\n".join((
            "\\documentclass[preview]{standalone}",
            "\n".join(self.preamble),
            "\\begin{document}",
            content,
            "\\end{document}"
        )) + "\n"

    def get_svg_file_path(self, content: str) -> str:
        full_tex = self.get_tex_file_content(content)
        hash_code = hash_string(full_tex)
        tex_dir = get_tex_dir()
        root = os.path.join(tex_dir, hash_code)
        svg_file_path = root + ".svg"
        if os.path.exists(svg_file_path):
            return svg_file_path

        # If svg doesn't exist, create it
        replaced_content = content.replace("\n", " ")
        displayed_msg = f"Writing \"{replaced_content}\""
        max_characters = os.get_terminal_size().columns - 1
        if len(displayed_msg) > max_characters:
            displayed_msg = displayed_msg[:max_characters - 3] + "..."
        print(displayed_msg, end="\r")

        with open(root + ".tex", "w", encoding="utf-8") as tex_file:
            tex_file.write(full_tex)

        # tex to dvi
        if os.system(" ".join((
            self.executable,
            "-interaction=batchmode",
            "-halt-on-error",
            f"-output-directory=\"{tex_dir}\"",
            f"\"{root}.tex\"",
            ">",
            os.devnull
        ))):
            log.error("LaTeX Error!  Not a worry, it happens to the best of us.")
            with open(root + ".log", "r", encoding="utf-8") as log_file:
                error_match_obj = re.search(r"(?<=\n! ).*", log_file.read())
                if error_match_obj:
                    log.debug("The error could be: `%s`", error_match_obj.group())
            raise LatexError()

        # dvi to svg
        os.system(" ".join((
            "dvisvgm",
            f"\"{root}{self.dvi_ext}\"",
            "-n",
            "-v",
            "0",
            "-o",
            f"\"{svg_file_path}\"",
            ">",
            os.devnull
        )))

        # Cleanup superfluous documents
        for ext in (".tex", self.dvi_ext, ".log", ".aux"):
            try:
                os.remove(root + ext)
            except FileNotFoundError:
                pass

        print(" " * len(displayed_msg), end="\r")
        return svg_file_path

    def add_preamble(self, *preamble_strs: str):
        self.preamble.extend(preamble_strs)
        return self
