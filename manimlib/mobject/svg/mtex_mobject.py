from __future__ import annotations

import re
import colour
import itertools as it
from types import MethodType
from typing import Iterable, Union, Sequence
from abc import abstractmethod

from manimlib.constants import WHITE
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.color import color_to_int_rgb
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.tex_file_writing import tex_to_svg_file
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import display_during_execution
from manimlib.logger import log


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.types.vectorized_mobject import VMobject
    ManimColor = Union[str, colour.Color, Sequence[float]]
    Span = tuple[int, int]


SCALE_FACTOR_PER_FONT_POINT = 0.001


class _StringSVG(SVGMobject):
    CONFIG = {
        "height": None,
        "stroke_width": 0,
        "stroke_color": WHITE,
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        },
    }


class LabelledString(_StringSVG):
    """
    An abstract base class for `MTex` and `MarkupText`
    """
    CONFIG = {
        "base_color": WHITE,
        "use_plain_file": False,
    }

    def __init__(self, string: str, **kwargs):
        self.string = string
        super().__init__(**kwargs)

    def get_file_path(self, use_plain_file: bool = False) -> str:
        if use_plain_file:
            content = self.plain_string
        else:
            content = self.labelled_string
        return self.get_file_path_by_content(content)

    @abstractmethod
    def get_file_path_by_content(self, content: str) -> str:
        return ""

    def generate_mobject(self) -> None:
        super().generate_mobject()

        if not self.submobjects:
            return

        glyph_labels = [
            self.color_to_label(glyph.get_fill_color())
            for glyph in self.submobjects
        ]

        if self.use_plain_file or self.has_predefined_colors:
            file_path = self.get_file_path(use_plain_file=True)
            glyphs = _StringSVG(file_path).submobjects
            for glyph, plain_glyph in zip(self.submobjects, glyphs):
                glyph.set_fill(plain_glyph.get_fill_color())
        else:
            glyphs = self.submobjects
            self.set_fill(self.base_color)

        # Simply pack together adjacent mobjects with the same label.
        submob_labels, glyphs_lists = self.group_neighbours(
            glyph_labels, glyphs
        )
        submob_strings = self.get_submob_strings(submob_labels)
        submobjects = []
        for glyph_list, label, submob_string in zip(
            glyphs_lists, submob_labels, submob_strings
        ):
            submob = VGroup(*glyph_list)
            submob.label = label
            submob.string = submob_string
            submob.get_string = MethodType(lambda inst: inst.string, submob)
            submobjects.append(submob)
        self.set_submobjects(submobjects)

    # Toolkits

    @staticmethod
    def color_to_label(color: ManimColor) -> int:
        r, g, b = color_to_int_rgb(color)
        rg = r * 256 + g
        rgb = rg * 256 + b
        if rgb == 16777215:  # white
            return -1
        return rgb

    @staticmethod
    def get_neighbouring_pairs(iterable: Iterable) -> list:
        return list(adjacent_pairs(iterable))[:-1]

    @staticmethod
    def span_contains(span_0: Span, span_1: Span) -> bool:
        return span_0[0] <= span_1[0] and span_0[1] >= span_1[1]

    @staticmethod
    def group_neighbours(
        labels: Iterable[object],
        objs: Iterable[object]
    ) -> tuple[list[object], list[list[object]]]:
        # Pack together neighbouring objects sharing the same label.
        if not labels:
            return [], []

        group_labels = []
        groups = []
        new_group = []
        current_label = labels[0]
        for label, obj in zip(labels, objs):
            if label == current_label:
                new_group.append(obj)
            else:
                group_labels.append(current_label)
                groups.append(new_group)
                new_group = [obj]
                current_label = label
        group_labels.append(current_label)
        groups.append(new_group)
        return group_labels, groups

    @staticmethod
    def find_region_index(val: int, seq: list[int]) -> int:
        # Returns an integer in `range(-1, len(seq))` satisfying
        # `seq[result] <= val < seq[result + 1]`.
        # `seq` should be sorted in ascending order.
        if not seq or val < seq[0]:
            return -1
        result = len(seq) - 1
        while val < seq[result]:
            result -= 1
        return result

    @staticmethod
    def replace_str_by_spans(
        substr: str, span_repl_dict: dict[Span, str]
    ) -> str:
        if not span_repl_dict:
            return substr

        spans = sorted(span_repl_dict.keys())
        if not all(
            span_0[1] <= span_1[0]
            for span_0, span_1 in LabelledString.get_neighbouring_pairs(spans)
        ):
            raise ValueError("Overlapping replacement")

        span_ends, span_begins = zip(*spans)
        pieces = [
            substr[slice(*span)]
            for span in zip(
                (0, *span_begins),
                (*span_ends, len(substr))
            )
        ]
        repl_strs = [*[span_repl_dict[span] for span in spans], ""]
        return "".join(it.chain(*zip(pieces, repl_strs)))

    @staticmethod
    def get_span_replacement_dict(
        inserted_string_pairs: list[tuple[Span, tuple[str, str]]],
        other_repl_items: list[tuple[Span, str]]
    ) -> dict[Span, str]:
        if not inserted_string_pairs:
            return other_repl_items.copy()

        indices, _, _, inserted_strings = zip(*sorted([
            (
                span[flag],
                -flag,
                -span[1 - flag],
                str_pair[flag]
            )
            for span, str_pair in inserted_string_pairs
            for flag in range(2)
        ]))
        result = {
            (index, index): "".join(inserted_strs)
            for index, inserted_strs in zip(*LabelledString.group_neighbours(
                indices, inserted_strings
            ))
        }
        result.update(other_repl_items)
        return result

    @property
    def skipped_spans(self) -> list[Span]:
        return []

    def lstrip(self, index: int) -> int:
        index_seq = list(it.chain(*self.skipped_spans))
        region_index = self.find_region_index(index, index_seq)
        if region_index % 2 == 0:
            return index_seq[region_index + 1]
        return index

    def rstrip(self, index: int) -> int:
        index_seq = list(it.chain(*self.skipped_spans))
        region_index = self.find_region_index(index - 1, index_seq)
        if region_index % 2 == 0:
            return index_seq[region_index]
        return index

    def strip(self, span: Span) -> Span | None:
        result = (
            self.lstrip(span[0]),
            self.rstrip(span[1])
        )
        if result[0] >= result[1]:
            return None
        return result

    @staticmethod
    def lslide(index: int, slid_spans: list[Span]) -> int:
        slide_dict = dict(sorted(slid_spans))
        while index in slide_dict.keys():
            index = slide_dict[index]
        return index

    @staticmethod
    def rslide(index: int, slid_spans: list[Span]) -> int:
        slide_dict = dict(sorted([
            slide_span[::-1] for slide_span in slid_spans
        ], reverse=True))
        while index in slide_dict.keys():
            index = slide_dict[index]
        return index

    @staticmethod
    def slide(span: Span, slid_spans: list[Span]) -> Span | None:
        result = (
            LabelledString.lslide(span[0], slid_spans),
            LabelledString.rslide(span[1], slid_spans)
        )
        if result[0] >= result[1]:
            return None
        return result

    # Parser

    @property
    def full_span(self) -> Span:
        return (0, len(self.string))

    def get_substrs_to_isolate(self, substrs: list[str]) -> list[str]:
        result = list(filter(
            lambda s: s in self.string,
            remove_list_redundancies(substrs)
        ))
        if "" in result:
            result.remove("")
        return result

    @property
    def label_span_list(self) -> list[Span]:
        return []

    @property
    def inserted_string_pairs(self) -> list[tuple[Span, tuple[str, str]]]:
        return []

    @property
    def command_repl_items(self) -> list[tuple[Span, str]]:
        return []

    @abstractmethod
    def has_predefined_colors(self) -> bool:
        return False

    @property
    def plain_string(self) -> str:
        return self.string

    @property
    def labelled_string(self) -> str:
        return self.replace_str_by_spans(
            self.string, self.get_span_replacement_dict(
                self.inserted_string_pairs,
                self.command_repl_items
            )
        )

    @property
    def ignored_indices_for_submob_strings(self) -> list[int]:
        return []

    def handle_submob_string(self, substr: str, string_span: Span) -> str:
        return substr

    def get_submob_strings(self, submob_labels: list[int]) -> list[str]:
        ordered_spans = [
            self.label_span_list[label] if label != -1 else self.full_span
            for label in submob_labels
        ]
        ordered_containing_labels = [
            self.containing_labels_dict[span]
            for span in ordered_spans
        ]
        ordered_span_begins, ordered_span_ends = zip(*ordered_spans)
        string_span_begins = [
            prev_end if prev_label in containing_labels else curr_begin
            for prev_end, prev_label, containing_labels, curr_begin in zip(
                ordered_span_ends[:-1], submob_labels[:-1],
                ordered_containing_labels[1:], ordered_span_begins[1:]
            )
        ]
        string_span_ends = [
            next_begin if next_label in containing_labels else curr_end
            for next_begin, next_label, containing_labels, curr_end in zip(
                ordered_span_begins[1:], submob_labels[1:],
                ordered_containing_labels[:-1], ordered_span_ends[:-1]
            )
        ]
        string_spans = list(zip(
            (ordered_span_begins[0], *string_span_begins),
            (*string_span_ends, ordered_span_ends[-1])
        ))

        command_spans = [span for span, _ in self.command_repl_items]
        slid_spans = list(it.chain(
            self.skipped_spans,
            command_spans,
            [
                (index, index + 1)
                for index in self.ignored_indices_for_submob_strings
            ]
        ))
        result = []
        for string_span in string_spans:
            string_span = self.slide(string_span, slid_spans)
            if string_span is None:
                result.append("")
                continue

            span_repl_dict = {
                tuple([index - string_span[0] for index in cmd_span]): ""
                for cmd_span in command_spans
                if self.span_contains(string_span, cmd_span)
            }
            substr = self.string[slice(*string_span)]
            substr = self.replace_str_by_spans(substr, span_repl_dict)
            substr = self.handle_submob_string(substr, string_span)
            result.append(substr)
        return result

    # Selector

    @property
    def containing_labels_dict(self) -> dict[Span, list[int]]:
        label_span_list = self.label_span_list
        result = {
            span: []
            for span in label_span_list
        }
        for span_0 in label_span_list:
            for span_index, span_1 in enumerate(label_span_list):
                if self.span_contains(span_0, span_1):
                    result[span_0].append(span_index)
                elif span_0[0] < span_1[0] < span_0[1] < span_1[1]:
                    string_0, string_1 = [
                        self.string[slice(*span)]
                        for span in [span_0, span_1]
                    ]
                    raise ValueError(
                        "Partially overlapping substrings detected: "
                        f"'{string_0}' and '{string_1}'"
                    )
        result[self.full_span] = list(range(-1, len(label_span_list)))
        return result

    def find_span_components_of_custom_span(
        self, custom_span: Span
    ) -> list[Span]:
        span_choices = sorted(filter(
            lambda span: self.span_contains(custom_span, span),
            self.label_span_list
        ))
        # Choose spans that reach the farthest.
        span_choices_dict = dict(span_choices)

        result = []
        span_begin, span_end = custom_span
        span_begin = self.rstrip(span_begin)
        span_end = self.rstrip(span_end)
        while span_begin != span_end:
            span_begin = self.lstrip(span_begin)
            if span_begin not in span_choices_dict.keys():
                return []
            next_begin = span_choices_dict[span_begin]
            result.append((span_begin, next_begin))
            span_begin = next_begin
        return result

    def get_part_by_custom_span(self, custom_span: Span) -> VGroup:
        spans = self.find_span_components_of_custom_span(custom_span)
        labels = set(it.chain(*[
            self.containing_labels_dict[span]
            for span in spans
        ]))
        return VGroup(*filter(
            lambda submob: submob.label in labels,
            self.submobjects
        ))

    def get_parts_by_string(self, substr: str) -> VGroup:
        return VGroup(*[
            self.get_part_by_custom_span(match_obj.span())
            for match_obj in re.finditer(re.escape(substr), self.string)
        ])

    def get_part_by_string(self, substr: str, index: int = 0) -> VMobject:
        all_parts = self.get_parts_by_string(substr)
        return all_parts[index]

    def set_color_by_string(self, substr: str, color: ManimColor):
        self.get_parts_by_string(substr).set_color(color)
        return self

    def set_color_by_string_to_color_map(
        self, string_to_color_map: dict[str, ManimColor]
    ):
        for substr, color in string_to_color_map.items():
            self.set_color_by_string(substr, color)
        return self

    def indices_of_part(self, part: Iterable[VMobject]) -> list[int]:
        indices = [
            index for index, submob in enumerate(self.submobjects)
            if submob in part
        ]
        if not indices:
            raise ValueError("Failed to find part")
        return indices

    def indices_of_part_by_string(
        self, substr: str, index: int = 0
    ) -> list[int]:
        part = self.get_part_by_string(substr, index=index)
        return self.indices_of_part(part)

    @property
    def specified_substrings(self) -> list[str]:
        return []

    def get_specified_substrings(self) -> list[str]:
        return self.specified_substrings

    @property
    def isolated_substrings(self) -> list[str]:
        return remove_list_redundancies([
            self.string[slice(*span)]
            for span in self.label_span_list
        ])

    def get_isolated_substrings(self) -> list[str]:
        return self.isolated_substrings

    def get_string(self) -> str:
        return self.string


class MTex(LabelledString):
    CONFIG = {
        "font_size": 48,
        "alignment": "\\centering",
        "tex_environment": "align*",
        "isolate": [],
        "tex_to_color_map": {},
    }

    def __init__(self, tex_string: str, **kwargs):
        tex_string = tex_string.strip()
        # Prevent from passing an empty string.
        if not tex_string:
            tex_string = "\\quad"
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
            self.use_plain_file,
            self.tex_string,
            self.alignment,
            self.tex_environment,
            self.isolate,
            self.tex_to_color_map
        )

    def get_file_path_by_content(self, content: str) -> str:
        full_tex = self.get_tex_file_body(content)
        with display_during_execution(f"Writing \"{self.string}\""):
            file_path = self.tex_to_svg_file_path(full_tex)
        return file_path

    def get_tex_file_body(self, content: str) -> str:
        if self.tex_environment:
            content = "\n".join([
                f"\\begin{{{self.tex_environment}}}",
                content,
                f"\\end{{{self.tex_environment}}}"
            ])
        if self.alignment:
            content = "\n".join([self.alignment, content])

        tex_config = get_tex_config()
        return tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            content
        )

    @staticmethod
    def tex_to_svg_file_path(tex_file_content: str) -> str:
        return tex_to_svg_file(tex_file_content)

    # Parser

    @property
    def backslash_indices(self) -> list[int]:
        # Newlines (`\\`) don't count.
        return [
            match_obj.end() - 1
            for match_obj in re.finditer(r"\\+", self.string)
            if len(match_obj.group()) % 2 == 1
        ]

    def get_brace_indices_lists(self) -> tuple[list[Span], list[Span]]:
        string = self.string
        indices = list(filter(
            lambda index: index - 1 not in self.backslash_indices,
            [
                match_obj.start()
                for match_obj in re.finditer(r"[{}]", string)
            ]
        ))
        left_brace_indices = []
        right_brace_indices = []
        left_brace_indices_stack = []
        for index in indices:
            if string[index] == "{":
                left_brace_indices_stack.append(index)
            else:
                if not left_brace_indices_stack:
                    raise ValueError("Missing '{' inserted")
                left_brace_index = left_brace_indices_stack.pop()
                left_brace_indices.append(left_brace_index)
                right_brace_indices.append(index)
        if left_brace_indices_stack:
            raise ValueError("Missing '}' inserted")
        # `right_brace_indices` is already sorted.
        return left_brace_indices, right_brace_indices

    @property
    def left_brace_indices(self) -> list[Span]:
        return self.get_brace_indices_lists()[0]

    @property
    def right_brace_indices(self) -> list[Span]:
        return self.get_brace_indices_lists()[1]

    @property
    def skipped_spans(self) -> list[Span]:
        return [
            match_obj.span()
            for match_obj in re.finditer(r"\s*([_^])\s*|(\s+)", self.string)
            if match_obj.group(2) is not None
            or match_obj.start(1) - 1 not in self.backslash_indices
        ]

    @property
    def script_char_spans(self) -> list[Span]:
        return list(filter(
            lambda span: self.string[slice(*span)].strip(),
            self.skipped_spans
        ))

    @property
    def script_content_spans(self) -> list[Span]:
        result = []
        brace_indices_dict = dict(zip(
            self.left_brace_indices, self.right_brace_indices
        ))
        for _, span_begin in self.script_char_spans:
            if span_begin in brace_indices_dict.keys():
                span_end = brace_indices_dict[span_begin] + 1
            else:
                pattern = re.compile(r"[a-zA-Z0-9]|\\[a-zA-Z]+")
                match_obj = pattern.match(self.string, pos=span_begin)
                if not match_obj:
                    script_name = {
                        "_": "subscript",
                        "^": "superscript"
                    }[script_char]
                    raise ValueError(
                        f"Unclear {script_name} detected while parsing. "
                        "Please use braces to clarify"
                    )
                span_end = match_obj.end()
            result.append((span_begin, span_end))
        return result

    @property
    def double_braces_spans(self) -> list[Span]:
        # Match paired double braces (`{{...}}`).
        result = []
        reversed_brace_indices_dict = dict(zip(
            self.right_brace_indices, self.left_brace_indices
        ))
        skip = False
        for prev_right_index, right_index in self.get_neighbouring_pairs(
            self.right_brace_indices
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

    @property
    def additional_substrings(self) -> list[str]:
        return self.get_substrs_to_isolate(list(it.chain(
            self.tex_to_color_map.keys(),
            self.isolate
        )))

    def get_label_span_list(self, extended: bool) -> list[Span]:
        script_content_spans = self.script_content_spans
        script_spans = [
            (script_char_span[0], script_content_span[1])
            for script_char_span, script_content_span in zip(
                self.script_char_spans, script_content_spans
            )
        ]
        spans = remove_list_redundancies([
            self.full_span,
            *self.double_braces_spans,
            *filter(lambda stripped_span: stripped_span is not None, [
                self.strip(match_obj.span())
                for substr in self.additional_substrings
                for match_obj in re.finditer(re.escape(substr), self.string)
            ]),
            *script_content_spans
        ])
        result = []
        for span in spans:
            if span in script_content_spans:
                continue
            span_begin, span_end = span
            shrinked_end = self.rslide(span_end, script_spans)
            if span_begin >= shrinked_end:
                continue
            shrinked_span = (span_begin, shrinked_end)
            if shrinked_span in result:
                continue
            result.append(shrinked_span)

        if extended:
            result = [
                (span_begin, self.lslide(span_end, script_spans))
                for span_begin, span_end in result
            ]
        return script_content_spans + result

    @property
    def label_span_list(self) -> list[Span]:
        return self.get_label_span_list(extended=False)

    @property
    def inserted_string_pairs(self) -> list[tuple[Span, tuple[str, str]]]:
        return [
            (span, (
                "{{" + self.get_color_command_by_label(label),
                "}}"
            ))
            for label, span in enumerate(
                self.get_label_span_list(extended=True)
            )
        ]

    @property
    def command_repl_items(self) -> list[tuple[Span, str]]:
        color_related_command_dict = {
            "color": (1, False),
            "textcolor": (1, False),
            "pagecolor": (1, True),
            "colorbox": (1, True),
            "fcolorbox": (2, True),
        }
        result = []
        backslash_indices = self.backslash_indices
        right_brace_indices = self.right_brace_indices
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
            span_end = right_brace_indices[self.find_region_index(
                cmd_end, right_brace_indices
            ) + n_braces] + 1
            if substitute_cmd:
                repl_str = "\\" + cmd_name + n_braces * "{white}"
            else:
                repl_str = ""
            result.append(((span_begin, span_end), repl_str))
        return result

    @property
    def has_predefined_colors(self) -> bool:
        return bool(self.command_repl_items)

    @staticmethod
    def get_color_command_by_label(label: int) -> str:
        if label == -1:
            label = 16777215  # white
        rg, b = divmod(label, 256)
        r, g = divmod(rg, 256)
        return "".join([
            "\\color[RGB]",
            "{",
            ",".join(map(str, (r, g, b))),
            "}"
        ])

    @property
    def plain_string(self) -> str:
        return "".join([
            "{{",
            self.get_color_command_by_label(
                self.color_to_label(self.base_color)
            ),
            self.string,
            "}}"
        ])

    @property
    def ignored_indices_for_submob_strings(self) -> list[int]:
        return self.left_brace_indices + self.right_brace_indices

    def handle_submob_string(self, substr: str, string_span: Span) -> str:
        unclosed_left_braces = 0
        unclosed_right_braces = 0
        for index in range(*string_span):
            if index in self.left_brace_indices:
                unclosed_left_braces += 1
            elif index in self.right_brace_indices:
                if unclosed_left_braces == 0:
                    unclosed_right_braces += 1
                else:
                    unclosed_left_braces -= 1
        return "".join([
            unclosed_right_braces * "{",
            substr,
            unclosed_left_braces * "}"
        ])

    @property
    def specified_substrings(self) -> list[str]:
        return remove_list_redundancies([
            self.string[slice(*double_braces_span)]
            for double_braces_span in self.double_braces_spans
        ] + self.additional_substrings)

    # Method alias

    def get_parts_by_tex(self, substr: str) -> VGroup:
        return self.get_parts_by_string(substr)

    def get_part_by_tex(self, substr: str, index: int = 0) -> VMobject:
        return self.get_part_by_string(substr, index)

    def set_color_by_tex(self, substr: str, color: ManimColor):
        return self.set_color_by_string(substr, color)

    def set_color_by_tex_to_color_map(
        self, tex_to_color_map: dict[str, ManimColor]
    ):
        return self.set_color_by_string_to_color_map(tex_to_color_map)

    def indices_of_part_by_tex(
        self, substr: str, index: int = 0
    ) -> list[int]:
        return self.indices_of_part_by_string(substr, index)

    def get_tex(self) -> str:
        return self.get_string()


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
