from __future__ import annotations

from manimlib.mobject.svg.labelled_string import LabelledString
from manimlib.utils.tex_file_writing import display_during_execution
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import tex_to_svg_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from colour import Color
    import re
    from typing import Iterable, Union

    from manimlib.mobject.types.vectorized_mobject import VGroup

    ManimColor = Union[str, Color]
    Span = tuple[int, int]
    Selector = Union[
        str,
        re.Pattern,
        tuple[Union[int, None], Union[int, None]],
        Iterable[Union[
            str,
            re.Pattern,
            tuple[Union[int, None], Union[int, None]]
        ]]
    ]


SCALE_FACTOR_PER_FONT_POINT = 0.001


class MTex(LabelledString):
    CONFIG = {
        "font_size": 48,
        "alignment": "\\centering",
        "tex_environment": "align*",
        "tex_to_color_map": {},
    }

    def __init__(self, tex_string: str, **kwargs):
        # Prevent from passing an empty string.
        if not tex_string.strip():
            tex_string = "\\\\"
        self.tex_string = tex_string
        super().__init__(tex_string, **kwargs)

        self.set_color_by_tex_to_color_map(self.tex_to_color_map)
        self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)

    @property
    def hash_seed(self) -> tuple:
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.base_color,
            self.isolate,
            self.tex_string,
            self.alignment,
            self.tex_environment,
            self.tex_to_color_map
        )

    def get_file_path_by_content(self, content: str) -> str:
        tex_config = get_tex_config()
        full_tex = tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            content
        )
        with display_during_execution(f"Writing \"{self.string}\""):
            file_path = tex_to_svg_file(full_tex)
        return file_path

    # Parsing

    def get_cmd_spans(self) -> list[Span]:
        return self.find_spans(r"\\(?:[a-zA-Z]+|\s|\S)|[_^{}]")

    def get_substr_flag(self, substr: str) -> int:
        return {"{": 1, "}": -1}.get(substr, 0)

    def get_specified_items(
        self, cmd_span_pairs: list[tuple[Span, Span]]
    ) -> list[tuple[Span, dict[str, str]]]:
        cmd_content_spans = [
            (span_begin, span_end)
            for (_, span_begin), (span_end, _) in cmd_span_pairs
        ]
        specified_spans = [
            *[
                cmd_content_spans[range_begin]
                for _, (range_begin, range_end) in self.compress_neighbours([
                    (span_begin + index, span_end - index)
                    for index, (span_begin, span_end) in enumerate(
                        cmd_content_spans
                    )
                ])
                if range_end - range_begin >= 2
            ],
            *[
                span
                for selector in self.tex_to_color_map
                for span in self.find_spans_by_selector(selector)
            ],
            *self.find_spans_by_selector(self.isolate)
        ]
        return [(span, {}) for span in specified_spans]

    def get_repl_substr_for_content(self, substr: str) -> str:
        return substr

    def get_repl_substr_for_matching(self, substr: str) -> str:
        return substr if substr.startswith("\\") else ""

    @staticmethod
    def get_color_cmd_str(rgb_hex: str) -> str:
        rgb = MTex.hex_to_int(rgb_hex)
        rg, b = divmod(rgb, 256)
        r, g = divmod(rg, 256)
        return f"\\color[RGB]{{{r}, {g}, {b}}}"

    @staticmethod
    def get_cmd_str_pair(
        attr_dict: dict[str, str], label_hex: str | None
    ) -> tuple[str, str]:
        if label_hex is None:
            return "", ""
        return "{{" + MTex.get_color_cmd_str(label_hex), "}}"

    def get_content_prefix_and_suffix(
        self, is_labelled: bool
    ) -> tuple[str, str]:
        prefix_lines = []
        suffix_lines = []
        if not is_labelled:
            prefix_lines.append(self.get_color_cmd_str(self.base_color_hex))
        if self.alignment:
            prefix_lines.append(self.alignment)
        if self.tex_environment:
            if isinstance(self.tex_environment, str):
                env_prefix = f"\\begin{{{self.tex_environment}}}"
                env_suffix = f"\\end{{{self.tex_environment}}}"
            else:
                env_prefix, env_suffix = self.tex_environment
            prefix_lines.append(env_prefix)
            suffix_lines.append(env_suffix)
        return (
            "".join([line + "\n" for line in prefix_lines]),
            "".join(["\n" + line for line in suffix_lines])
        )

    # Method alias

    def get_parts_by_tex(self, selector: Selector) -> VGroup:
        return self.select_parts(selector)

    def get_part_by_tex(self, selector: Selector) -> VGroup:
        return self.select_part(selector)

    def set_color_by_tex(self, selector: Selector, color: ManimColor):
        return self.set_parts_color(selector, color)

    def set_color_by_tex_to_color_map(
        self, color_map: dict[Selector, ManimColor]
    ):
        return self.set_parts_color_by_dict(color_map)

    def get_tex(self) -> str:
        return self.get_string()


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
