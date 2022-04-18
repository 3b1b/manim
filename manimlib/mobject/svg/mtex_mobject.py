from __future__ import annotations

import itertools as it
import re

from manimlib.mobject.svg.labelled_string import LabelledString
from manimlib.utils.tex_file_writing import display_during_execution
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import tex_to_svg_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from colour import Color
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


TEX_COLOR_COMMANDS_DICT = {
    "\\color": (1, False),
    "\\textcolor": (1, False),
    "\\pagecolor": (1, True),
    "\\colorbox": (1, True),
    "\\fcolorbox": (2, True),
}


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

    def parse(self) -> None:
        self.backslash_indices = self.get_backslash_indices()
        self.command_spans = self.get_command_spans()
        self.brace_spans = self.get_brace_spans()
        self.script_char_indices = self.get_script_char_indices()
        self.script_content_spans = self.get_script_content_spans()
        self.script_spans = self.get_script_spans()
        self.command_repl_items = self.get_command_repl_items()
        super().parse()

    # Toolkits

    @staticmethod
    def get_color_command_str(rgb_int: int) -> str:
        rg, b = divmod(rgb_int, 256)
        r, g = divmod(rg, 256)
        return f"\\color[RGB]{{{r}, {g}, {b}}}"

    # Parsing

    def get_backslash_indices(self) -> list[int]:
        # The latter of `\\` doesn't count.
        return self.find_indices(r"\\.")

    def get_command_spans(self) -> list[Span]:
        return [
            self.match(r"\\(?:[a-zA-Z]+|.)", pos=index).span()
            for index in self.backslash_indices
        ]

    def get_unescaped_char_indices(self, char: str) -> list[int]:
        return list(filter(
            lambda index: index - 1 not in self.backslash_indices,
            self.find_indices(re.escape(char))
        ))

    def get_brace_spans(self) -> list[Span]:
        span_begins = []
        span_ends = []
        span_begins_stack = []
        char_items = sorted([
            (index, char)
            for char in "{}"
            for index in self.get_unescaped_char_indices(char)
        ])
        for index, char in char_items:
            if char == "{":
                span_begins_stack.append(index)
            else:
                if not span_begins_stack:
                    raise ValueError("Missing '{' inserted")
                span_begins.append(span_begins_stack.pop())
                span_ends.append(index + 1)
        if span_begins_stack:
            raise ValueError("Missing '}' inserted")
        return list(zip(span_begins, span_ends))

    def get_script_char_indices(self) -> list[int]:
        return list(it.chain(*[
            self.get_unescaped_char_indices(char)
            for char in "_^"
        ]))

    def get_script_content_spans(self) -> list[Span]:
        result = []
        script_entity_dict = dict(it.chain(
            self.brace_spans,
            self.command_spans
        ))
        for index in self.script_char_indices:
            span_begin = self.match(r"\s*", pos=index + 1).end()
            if span_begin in script_entity_dict.keys():
                span_end = script_entity_dict[span_begin]
            else:
                match_obj = self.match(r".", pos=span_begin)
                if match_obj is None:
                    continue
                span_end = match_obj.end()
            result.append((span_begin, span_end))
        return result

    def get_script_spans(self) -> list[Span]:
        return [
            (
                self.match(r"[\s\S]*?(\s*)$", endpos=index).start(1),
                script_content_span[1]
            )
            for index, script_content_span in zip(
                self.script_char_indices, self.script_content_spans
            )
        ]

    def get_command_repl_items(self) -> list[tuple[Span, str]]:
        result = []
        brace_spans_dict = dict(self.brace_spans)
        brace_begins = list(brace_spans_dict.keys())
        for cmd_span in self.command_spans:
            cmd_name = self.get_substr(cmd_span)
            if cmd_name not in TEX_COLOR_COMMANDS_DICT.keys():
                continue
            n_braces, substitute_cmd = TEX_COLOR_COMMANDS_DICT[cmd_name]
            span_begin, span_end = cmd_span
            for _ in range(n_braces):
                span_end = brace_spans_dict[min(filter(
                    lambda index: index >= span_end,
                    brace_begins
                ))]
            if substitute_cmd:
                repl_str = cmd_name + n_braces * "{black}"
            else:
                repl_str = ""
            result.append(((span_begin, span_end), repl_str))
        return result

    def get_skippable_indices(self) -> list[int]:
        return list(it.chain(
            self.find_indices(r"\s"),
            self.script_char_indices
        ))

    def get_entity_spans(self) -> list[Span]:
        return self.command_spans.copy()

    def get_bracket_spans(self) -> list[Span]:
        return self.brace_spans.copy()

    def get_extra_isolated_items(self) -> list[tuple[Span, dict[str, str]]]:
        result = []

        # Match paired double braces (`{{...}}`).
        sorted_brace_spans = sorted(
            self.brace_spans, key=lambda span: span[1]
        )
        skip = False
        for prev_span, span in self.get_neighbouring_pairs(
            sorted_brace_spans
        ):
            if skip:
                skip = False
                continue
            if span[0] != prev_span[0] - 1 or span[1] != prev_span[1] + 1:
                continue
            result.append(span)
            skip = True

        result.extend(it.chain(*[
            self.find_spans_by_selector(selector)
            for selector in self.tex_to_color_map.keys()
        ]))
        return [(span, {}) for span in result]

    def get_label_span_list(self) -> list[Span]:
        result = self.script_content_spans.copy()
        reversed_script_spans_dict = dict([
            script_span[::-1] for script_span in self.script_spans
        ])
        for span_begin, span_end in self.specified_spans:
            while span_end in reversed_script_spans_dict.keys():
                span_end = reversed_script_spans_dict[span_end]
            if span_begin >= span_end:
                continue
            shrinked_span = (span_begin, span_end)
            if shrinked_span in result:
                continue
            result.append(shrinked_span)
        return result

    def get_content(self, is_labelled: bool) -> str:
        if is_labelled:
            extended_label_span_list = []
            script_spans_dict = dict(self.script_spans)
            for span in self.label_span_list:
                if span not in self.script_content_spans:
                    span_begin, span_end = span
                    while span_end in script_spans_dict.keys():
                        span_end = script_spans_dict[span_end]
                    span = (span_begin, span_end)
                extended_label_span_list.append(span)
            inserted_string_pairs = [
                (span, (
                    "{{" + self.get_color_command_str(label + 1),
                    "}}"
                ))
                for label, span in enumerate(extended_label_span_list)
            ]
            span_repl_dict = self.generate_span_repl_dict(
                inserted_string_pairs, self.command_repl_items
            )
        else:
            span_repl_dict = {}
        result = self.get_replaced_substr(self.full_span, span_repl_dict)

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
                self.get_color_command_str(self.base_color_int),
                result
            ])
        return result

    # Selector

    def get_cleaned_substr(self, span: Span) -> str:
        if not self.brace_spans:
            brace_begins, brace_ends = [], []
        else:
            brace_begins, brace_ends = zip(*self.brace_spans)
        left_brace_indices = list(brace_begins)
        right_brace_indices = [index - 1 for index in brace_ends]
        skippable_indices = list(it.chain(
            self.skippable_indices,
            left_brace_indices,
            right_brace_indices
        ))
        shrinked_span = self.shrink_span(span, skippable_indices)

        if shrinked_span[0] >= shrinked_span[1]:
            return ""

        # Balance braces.
        unclosed_left_braces = 0
        unclosed_right_braces = 0
        for index in range(*shrinked_span):
            if index in left_brace_indices:
                unclosed_left_braces += 1
            elif index in right_brace_indices:
                if unclosed_left_braces == 0:
                    unclosed_right_braces += 1
                else:
                    unclosed_left_braces -= 1
        return "".join([
            unclosed_right_braces * "{",
            self.get_substr(shrinked_span),
            unclosed_left_braces * "}"
        ])

    # Method alias

    def get_parts_by_tex(self, selector: Selector, **kwargs) -> VGroup:
        return self.select_parts(selector, **kwargs)

    def get_part_by_tex(self, selector: Selector, **kwargs) -> VGroup:
        return self.select_part(selector, **kwargs)

    def set_color_by_tex(
        self, selector: Selector, color: ManimColor, **kwargs
    ):
        return self.set_parts_color(selector, color, **kwargs)

    def set_color_by_tex_to_color_map(
        self, color_map: dict[Selector, ManimColor], **kwargs
    ):
        return self.set_parts_color_by_dict(color_map, **kwargs)

    def get_tex(self) -> str:
        return self.get_string()


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
