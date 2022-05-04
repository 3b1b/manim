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

    #@property
    #def sort_labelled_submobs(self) -> bool:
    #    return False

    # Toolkits

    @staticmethod
    def get_color_command_str(rgb_hex: str) -> str:
        rgb = MTex.hex_to_int(rgb_hex)
        rg, b = divmod(rgb, 256)
        r, g = divmod(rg, 256)
        return f"\\color[RGB]{{{r}, {g}, {b}}}"

    @staticmethod
    def get_tag_string_pair(
        attr_dict: dict[str, str], label_hex: str | None
    ) -> tuple[str, str]:
        if label_hex is None:
            return ("", "")
        return ("{{" + MTex.get_color_command_str(label_hex), "}}")

    # Parsing

    def get_command_spans(self) -> tuple[list[Span], list[Span], list[Span]]:
        cmd_spans = self.find_spans(r"\\(?:[a-zA-Z]+|\s|\S)")
        begin_cmd_spans = [
            span
            for span in self.find_spans("{")
            if (span[0] - 1, span[1]) not in cmd_spans
        ]
        end_cmd_spans = [
            span
            for span in self.find_spans("}")
            if (span[0] - 1, span[1]) not in cmd_spans
        ]
        return begin_cmd_spans, end_cmd_spans, cmd_spans

    def get_specified_items(
        self, cmd_span_pairs: list[tuple[Span, Span]]
    ) -> list[tuple[Span, dict[str, str]]]:
        cmd_content_spans = [
            (span_begin, span_end)
            for (_, span_begin), (span_end, _) in cmd_span_pairs
        ]
        specified_spans = self.chain(
            [
                cmd_content_spans[range_begin]
                for _, (range_begin, range_end) in self.compress_neighbours([
                    (span_begin + index, span_end - index)
                    for index, (span_begin, span_end) in enumerate(
                        cmd_content_spans
                    )
                ])
                if range_end - range_begin >= 2
            ],
            [
                span
                for selector in self.tex_to_color_map
                for span in self.find_spans_by_selector(selector)
            ],
            self.find_spans_by_selector(self.isolate)
        )
        return [(span, {}) for span in specified_spans]

    def get_replaced_substr(self, substr: str, flag: int) -> str:
        return substr

    def get_full_content_string(self, content_string: str, is_labelled: bool) -> str:
        result = content_string

        if self.tex_environment:
            if isinstance(self.tex_environment, str):
                prefix = f"\\begin{{{self.tex_environment}}}"
                suffix = f"\\end{{{self.tex_environment}}}"
            else:
                prefix, suffix = self.tex_environment
            result = "\n".join([prefix, result, suffix])
        if self.alignment:
            result = "\n".join([self.alignment, result])

        if not is_labelled:
            result = "\n".join([
                self.get_color_command_str(self.base_color_hex),
                result
            ])
        return result

    # Selector

    def get_cleaned_substr(self, span: Span) -> str:
        backslash_indices = [
            index for index, _ in self.find_spans(r"\\[\s\S]")
        ]
        ignored_indices = [
            index
            for index, _ in self.find_spans(r"[\s_^{}]")
            if index - 1 not in backslash_indices
        ]
        span_begin, span_end = span
        while span_begin in ignored_indices:
            span_begin += 1
        while span_end - 1 in ignored_indices:
            span_end -= 1
        shrinked_span = (span_begin, span_end)

        whitespace_repl_items = []
        for whitespace_span in self.find_spans(r"\s+"):
            if not self.span_contains(shrinked_span, whitespace_span):
                continue
            if whitespace_span[0] - 1 in backslash_indices:
                whitespace_span = (whitespace_span[0] + 1, whitespace_span[1])
            if all(
                self.get_substr((index, index + 1)).isalpha()
                for index in (whitespace_span[0] - 1, whitespace_span[1])
            ):
                replaced_substr = " "
            else:
                replaced_substr = ""
            whitespace_repl_items.append((whitespace_span, replaced_substr))

        _, unclosed_right_braces, unclosed_left_braces = self.split_span_by_levels(shrinked_span)
        return "".join([
            unclosed_right_braces * "{",
            self.replace_string(shrinked_span, whitespace_repl_items),
            unclosed_left_braces * "}"
        ])

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
