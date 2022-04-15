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
    from typing import Union

    from manimlib.mobject.types.vectorized_mobject import VGroup
    from manimlib.mobject.types.vectorized_mobject import VMobject

    ManimColor = Union[str, Color]
    Span = tuple[int, int]
    Selector = Union[
        str,
        re.Pattern,
        tuple[Union[int, None], Union[int, None]]
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

    def pre_parse(self) -> None:
        super().pre_parse()
        self.backslash_indices = self.get_backslash_indices()
        self.brace_index_pairs = self.get_brace_index_pairs()
        self.script_char_spans = self.get_script_char_spans()
        self.script_content_spans = self.get_script_content_spans()
        self.script_spans = self.get_script_spans()

    # Toolkits

    @staticmethod
    def get_color_command_str(rgb_int: int) -> str:
        rg, b = divmod(rgb_int, 256)
        r, g = divmod(rg, 256)
        return f"\\color[RGB]{{{r}, {g}, {b}}}"

    # Pre-parsing

    def get_backslash_indices(self) -> list[int]:
        # The latter of `\\` doesn't count.
        return list(it.chain(*[
            range(span[0], span[1], 2)
            for span in self.find_spans(r"\\+")
        ]))

    def get_unescaped_char_spans(self, chars: str):
        return sorted(filter(
            lambda span: span[0] - 1 not in self.backslash_indices,
            list(it.chain(*[
                self.find_spans(re.escape(char))
                for char in chars
            ]))
        ))

    def get_brace_index_pairs(self) -> list[Span]:
        left_brace_indices = []
        right_brace_indices = []
        left_brace_indices_stack = []
        for span in self.get_unescaped_char_spans("{}"):
            index = span[0]
            if self.get_substr(span) == "{":
                left_brace_indices_stack.append(index)
            else:
                if not left_brace_indices_stack:
                    raise ValueError("Missing '{' inserted")
                left_brace_index = left_brace_indices_stack.pop()
                left_brace_indices.append(left_brace_index)
                right_brace_indices.append(index)
        if left_brace_indices_stack:
            raise ValueError("Missing '}' inserted")
        return list(zip(left_brace_indices, right_brace_indices))

    def get_script_char_spans(self) -> list[int]:
        return self.get_unescaped_char_spans("_^")

    def get_script_content_spans(self) -> list[Span]:
        result = []
        brace_indices_dict = dict(self.brace_index_pairs)
        script_pattern = r"[a-zA-Z0-9]|\\[a-zA-Z]+"
        for char_span in self.script_char_spans:
            span_begin = self.rslide(char_span[1], self.space_spans)
            if span_begin in brace_indices_dict.keys():
                span_end = brace_indices_dict[span_begin] + 1
            else:
                match_obj = self.match_at(script_pattern, span_begin)
                if match_obj is None:
                    script_name = {
                        "_": "subscript",
                        "^": "superscript"
                    }[self.get_string(char_span)]
                    raise ValueError(
                        f"Unclear {script_name} detected while parsing "
                        f"(position {char_span[0]}). "
                        "Please use braces to clarify"
                    )
                span_end = match_obj.end()
            result.append((span_begin, span_end))
        return result

    def get_script_spans(self) -> list[Span]:
        return [
            (
                self.lslide(char_span[0], self.space_spans),
                script_content_span[1]
            )
            for char_span, script_content_span in zip(
                self.script_char_spans, self.script_content_spans
            )
        ]

    # Parsing

    def get_command_repl_items(self) -> list[tuple[Span, str]]:
        color_related_command_dict = {
            "color": (1, False),
            "textcolor": (1, False),
            "pagecolor": (1, True),
            "colorbox": (1, True),
            "fcolorbox": (2, True),
        }
        result = []
        backslash_indices = self.backslash_indices
        right_brace_indices = [
            right_index
            for left_index, right_index in self.brace_index_pairs
        ]
        pattern = "".join([
            r"\\",
            "(",
            "|".join(color_related_command_dict.keys()),
            ")",
            r"(?![a-zA-Z])"
        ])
        for match_obj in re.finditer(pattern, self.string):
            span_begin, cmd_end = match_obj.span()
            if span_begin not in backslash_indices:
                continue
            cmd_name = match_obj.group(1)
            n_braces, substitute_cmd = color_related_command_dict[cmd_name]
            span_end = self.take_nearest_value(
                right_brace_indices, cmd_end, n_braces
            ) + 1
            if substitute_cmd:
                repl_str = "\\" + cmd_name + n_braces * "{black}"
            else:
                repl_str = ""
            result.append(((span_begin, span_end), repl_str))
        return result

    def get_extra_entity_spans(self) -> list[Span]:
        return [
            self.match_at(r"\\([a-zA-Z]+|.?)", index).span()
            for index in self.backslash_indices
        ]

    def get_extra_ignored_spans(self) -> list[int]:
        return self.script_char_spans.copy()

    def get_internal_specified_spans(self) -> list[Span]:
        # Match paired double braces (`{{...}}`).
        result = []
        reversed_brace_indices_dict = dict([
            pair[::-1] for pair in self.brace_index_pairs
        ])
        skip = False
        for prev_right_index, right_index in self.get_neighbouring_pairs(
            list(reversed_brace_indices_dict.keys())
        ):
            if skip:
                skip = False
                continue
            if right_index != prev_right_index + 1:
                continue
            left_index = reversed_brace_indices_dict[right_index]
            prev_left_index = reversed_brace_indices_dict[prev_right_index]
            if left_index != prev_left_index - 1:
                continue
            result.append((left_index, right_index + 1))
            skip = True
        return result

    def get_external_specified_spans(self) -> list[Span]:
        return list(it.chain(*[
            self.find_spans_by_selector(selector)
            for selector in self.tex_to_color_map.keys()
        ]))

    def get_label_span_list(self) -> list[Span]:
        result = self.script_content_spans.copy()
        for span_begin, span_end in self.specified_spans:
            shrinked_end = self.lslide(span_end, self.script_spans)
            if span_begin >= shrinked_end:
                continue
            shrinked_span = (span_begin, shrinked_end)
            if shrinked_span in result:
                continue
            result.append(shrinked_span)
        return result

    def get_content(self, is_labelled: bool) -> str:
        if is_labelled:
            extended_label_span_list = [
                span
                if span in self.script_content_spans
                else (span[0], self.rslide(span[1], self.script_spans))
                for span in self.label_span_list
            ]
            inserted_string_pairs = [
                (span, (
                    "{{" + self.get_color_command_str(label + 1),
                    "}}"
                ))
                for label, span in enumerate(extended_label_span_list)
            ]
            span_repl_dict = self.generate_span_repl_dict(
                inserted_string_pairs,
                self.command_repl_items
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

    # Post-parsing

    def get_cleaned_substr(self, span: Span) -> str:
        substr = super().get_cleaned_substr(span)
        if not self.brace_index_pairs:
            return substr

        # Balance braces.
        left_brace_indices, right_brace_indices = zip(*self.brace_index_pairs)
        unclosed_left_braces = 0
        unclosed_right_braces = 0
        for index in range(*span):
            if index in left_brace_indices:
                unclosed_left_braces += 1
            elif index in right_brace_indices:
                if unclosed_left_braces == 0:
                    unclosed_right_braces += 1
                else:
                    unclosed_left_braces -= 1
        return "".join([
            unclosed_right_braces * "{",
            substr,
            unclosed_left_braces * "}"
        ])

    # Method alias

    def get_parts_by_tex(self, selector: Selector, **kwargs) -> VGroup:
        return self.select_parts(selector, **kwargs)

    def get_part_by_tex(self, selector: Selector, **kwargs) -> VMobject:
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
