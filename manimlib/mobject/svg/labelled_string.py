from __future__ import annotations

import re
import colour
import itertools as it
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
        "isolate": [],
    }

    def __init__(self, string: str, **kwargs):
        self.string = string
        digest_config(self, kwargs)
        self.pre_parse()
        self.parse()
        super().__init__(**kwargs)

    def get_file_path(self, use_plain_file: bool = False) -> str:
        content = self.get_decorated_string(use_plain_file=use_plain_file)
        return self.get_file_path_by_content(content)

    @abstractmethod
    def get_file_path_by_content(self, content: str) -> str:
        return ""

    def generate_mobject(self) -> None:
        super().generate_mobject()

        submob_labels = [
            self.color_to_label(submob.get_fill_color())
            for submob in self.submobjects
        ]
        if self.use_plain_file or self.has_predefined_colors:
            file_path = self.get_file_path(use_plain_file=True)
            plain_svg = _StringSVG(file_path)
            self.set_submobjects(plain_svg.submobjects)
        else:
            self.set_fill(self.base_color)
        for submob, label in zip(self.submobjects, submob_labels):
            submob.label = label
        self.submob_labels = submob_labels
        self.post_parse()

    def pre_parse(self) -> None:
        self.full_span = self.get_full_span()
        self.space_spans = self.get_space_spans()

    def parse(self) -> None:
        self.command_repl_items = self.get_command_repl_items()
        self.command_spans = self.get_command_spans()
        self.ignored_indices = self.get_ignored_indices()
        self.skipped_spans = self.get_skipped_spans()
        self.internal_specified_spans = self.get_internal_specified_spans()
        self.external_specified_spans = self.get_external_specified_spans()
        self.specified_spans = self.get_specified_spans()
        self.label_span_list = self.get_label_span_list()
        self.has_predefined_colors = self.get_has_predefined_colors()

    def post_parse(self) -> None:
        self.containing_labels_dict = self.get_containing_labels_dict()
        self.specified_substrings = self.get_specified_substrings()
        self.group_substrs = self.get_group_substrs()

    # Toolkits

    def find_spans(self, pattern: str) -> list[Span]:
        return [
            match_obj.span()
            for match_obj in re.finditer(pattern, self.string)
        ]

    @staticmethod
    def get_neighbouring_pairs(iterable: Iterable) -> list:
        return list(adjacent_pairs(iterable))[:-1]

    @staticmethod
    def span_contains(span_0: Span, span_1: Span) -> bool:
        return span_0[0] <= span_1[0] and span_0[1] >= span_1[1]

    @staticmethod
    def compress_neighbours(vals: list[int]) -> list[tuple[int, Span]]:
        if not vals:
            return []

        unique_vals = [vals[0]]
        indices = [0]
        for index, val in enumerate(vals):
            if val == unique_vals[-1]:
                continue
            unique_vals.append(val)
            indices.append(index)
        indices.append(len(vals))
        spans = LabelledString.get_neighbouring_pairs(indices)
        return list(zip(unique_vals, spans))

    @staticmethod
    def find_region_index(seq: list[int], val: int) -> int:
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
    def take_nearest_value(seq: list[int], val: int, index_shift: int) -> int:
        sorted_seq = sorted(seq)
        index = LabelledString.find_region_index(sorted_seq, val)
        if index == -1:
            raise IndexError
        return sorted_seq[index + index_shift]

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
            (index, index): "".join(inserted_strings[slice(*item_span)])
            for index, item_span
            in LabelledString.compress_neighbours(indices)
        }
        result.update(other_repl_items)
        return result

    @staticmethod
    def rslide(index: int, skipped: list[Span]) -> int:
        transfer_dict = dict(sorted(skipped))
        while index in transfer_dict.keys():
            index = transfer_dict[index]
        return index

    @staticmethod
    def lslide(index: int, skipped: list[Span]) -> int:
        transfer_dict = dict(sorted([
            skipped_span[::-1] for skipped_span in skipped
        ], reverse=True))
        while index in transfer_dict.keys():
            index = transfer_dict[index]
        return index

    @staticmethod
    def shrink_span(span: Span, skipped: list[Span]) -> Span:
        return (
            LabelledString.rslide(span[0], skipped),
            LabelledString.lslide(span[1], skipped)
        )

    @staticmethod
    def extend_span(span: Span, skipped: list[Span]) -> Span:
        return (
            LabelledString.lslide(span[0], skipped),
            LabelledString.rslide(span[1], skipped)
        )

    @staticmethod
    def rgb_to_int(rgb_tuple: tuple[int, int, int]) -> int:
        r, g, b = rgb_tuple
        rg = r * 256 + g
        return rg * 256 + b

    @staticmethod
    def int_to_rgb(rgb_int: int) -> tuple[int, int, int]:
        rg, b = divmod(rgb_int, 256)
        r, g = divmod(rg, 256)
        return r, g, b

    @staticmethod
    def color_to_label(color: ManimColor) -> int:
        rgb_tuple = color_to_int_rgb(color)
        rgb = LabelledString.rgb_to_int(rgb_tuple)
        if rgb == 16777215:  # white
            return -1
        return rgb

    @abstractmethod
    def get_begin_color_command_str(int_rgb: int) -> str:
        return ""

    @abstractmethod
    def get_end_color_command_str() -> str:
        return ""

    # Pre-parsing

    def get_full_span(self) -> Span:
        return (0, len(self.string))

    def get_space_spans(self) -> list[Span]:
        return self.find_spans(r"\s+")

    # Parsing

    @abstractmethod
    def get_command_repl_items(self) -> list[tuple[Span, str]]:
        return []

    def get_command_spans(self) -> list[Span]:
        return [cmd_span for cmd_span, _ in self.command_repl_items]

    def get_ignored_indices(self) -> list[int]:
        return []

    def get_skipped_spans(self) -> list[Span]:
        return list(it.chain(
            self.space_spans,
            self.command_spans,
            [
                (index, index + 1)
                for index in self.ignored_indices
            ]
        ))

    @abstractmethod
    def get_internal_specified_spans(self) -> list[Span]:
        return []

    def get_external_specified_spans(self) -> list[Span]:
        if "" in self.isolate:
            return self.get_neighbouring_pairs(
                list(range(len(self.string) + 1))
            )

        return remove_list_redundancies(list(it.chain(*[
            self.find_spans(re.escape(substr))
            for substr in self.isolate
        ])))

    def get_specified_spans(self) -> list[Span]:
        spans = [
            self.full_span,
            *self.internal_specified_spans,
            *self.external_specified_spans
        ]
        shrinked_spans = list(filter(
            lambda span: span[0] < span[1],
            [
                self.shrink_span(span, self.skipped_spans)
                for span in spans
            ]
        ))
        return remove_list_redundancies(shrinked_spans)

    @abstractmethod
    def get_label_span_list(self) -> list[Span]:
        return []

    @abstractmethod
    def get_inserted_string_pairs(
        self, use_plain_file: bool
    ) -> list[tuple[Span, tuple[str, str]]]:
        return []

    @abstractmethod
    def get_other_repl_items(
        self, use_plain_file: bool
    ) -> list[tuple[Span, str]]:
        return []

    def get_decorated_string(self, use_plain_file: bool) -> str:
        span_repl_dict = self.get_span_replacement_dict(
            self.get_inserted_string_pairs(use_plain_file),
            self.get_other_repl_items(use_plain_file)
        )
        result = self.replace_str_by_spans(self.string, span_repl_dict)

        if not use_plain_file:
            return result
        return "".join([
            self.get_begin_color_command_str(
                self.rgb_to_int(color_to_int_rgb(self.base_color))
            ),
            result,
            self.get_end_color_command_str()
        ])

    @abstractmethod
    def get_has_predefined_colors(self) -> bool:
        return False

    # Post-parsing

    def get_containing_labels_dict(self) -> dict[Span, list[int]]:
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
        if self.full_span not in result:
            result[self.full_span] = list(range(len(label_span_list)))
        return result

    def get_cleaned_substr(self, span: Span) -> str:
        span_repl_dict = {
            tuple([index - span[0] for index in cmd_span]): ""
            for cmd_span in self.command_spans
            if self.span_contains(span, cmd_span)
        }
        return self.replace_str_by_spans(
            self.string[slice(*span)], span_repl_dict
        )

    def get_specified_substrings(self) -> list[str]:
        return remove_list_redundancies([
            self.get_cleaned_substr(span)
            for span in self.specified_spans
        ])

    def get_group_span_items(self) -> tuple[list[int], list[Span]]:
        if not self.submob_labels:
            return [], []
        return tuple(zip(
            *self.compress_neighbours(self.submob_labels)
        ))

    def get_group_substrs(self) -> list[str]:
        group_labels, _ = self.get_group_span_items()
        ordered_spans = [
            self.label_span_list[label] if label != -1 else self.full_span
            for label in group_labels
        ]
        ordered_containing_labels = [
            self.containing_labels_dict[span]
            for span in ordered_spans
        ]
        ordered_span_begins, ordered_span_ends = zip(*ordered_spans)
        span_begins = [
            prev_end if prev_label in containing_labels else curr_begin
            for prev_end, prev_label, containing_labels, curr_begin in zip(
                ordered_span_ends[:-1], group_labels[:-1],
                ordered_containing_labels[1:], ordered_span_begins[1:]
            )
        ]
        span_ends = [
            next_begin if next_label in containing_labels else curr_end
            for next_begin, next_label, containing_labels, curr_end in zip(
                ordered_span_begins[1:], group_labels[1:],
                ordered_containing_labels[:-1], ordered_span_ends[:-1]
            )
        ]
        spans = list(zip(
            (ordered_span_begins[0], *span_begins),
            (*span_ends, ordered_span_ends[-1])
        ))
        shrinked_spans = [
            self.shrink_span(span, self.skipped_spans)
            for span in spans
        ]
        group_substrs = [
            self.get_cleaned_substr(span) if span[0] < span[1] else ""
            for span in shrinked_spans
        ]
        return group_substrs

    def get_submob_groups(self) -> VGroup:
        _, submob_spans = self.get_group_span_items()
        return VGroup(*[
            VGroup(*self.submobjects[slice(*submob_span)])
            for submob_span in submob_spans
        ])

    # Selector

    def find_span_components_of_custom_span(
        self, custom_span: Span
    ) -> list[Span]:
        if custom_span[0] >= custom_span[1]:
            return []

        indices = remove_list_redundancies(list(it.chain(
            self.full_span,
            *self.label_span_list
        )))
        span_begin = self.take_nearest_value(indices, custom_span[0], 0)
        span_end = self.take_nearest_value(indices, custom_span[1] - 1, 1)
        span_choices = sorted(filter(
            lambda span: self.span_contains((span_begin, span_end), span),
            self.label_span_list
        ))
        # Choose spans that reach the farthest.
        span_choices_dict = dict(span_choices)

        result = []
        while span_begin < span_end:
            if span_begin not in span_choices_dict.keys():
                span_begin += 1
                continue
            next_begin = span_choices_dict[span_begin]
            result.append((span_begin, next_begin))
            span_begin = next_begin
        return result

    def get_parts_by_custom_span(self, custom_span: Span) -> VGroup:
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
        if not substr:
            return VGroup()
        return VGroup(*[
            self.get_parts_by_custom_span(span)
            for span in self.find_spans(re.escape(substr))
        ])

    def get_parts_by_group_substr(self, substr: str) -> VGroup:
        return VGroup(*[
            group
            for group, group_substr in zip(
                self.get_submob_groups(), self.group_substrs
            )
            if group_substr == substr
        ])

    def get_part_by_string(self, substr: str, index : int = 0) -> VMobject:
        return self.get_parts_by_string(substr)[index]

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
        return [self.submobjects.index(submob) for submob in part]

    def indices_lists_of_parts(
        self, parts: Iterable[Iterable[VMobject]]
    ) -> list[list[int]]:
        return [self.indices_of_part(part) for part in parts]

    def get_string(self) -> str:
        return self.string


class MTex(LabelledString):
    CONFIG = {
        "font_size": 48,
        "alignment": "\\centering",
        "tex_environment": "align*",
        "tex_to_color_map": {},
    }

    def __init__(self, tex_string: str, **kwargs):
        digest_config(self, kwargs)
        # Prevent from passing an empty string.
        if not tex_string:
            tex_string = "\\quad"
        self.tex_string = tex_string
        self.isolate.extend(self.tex_to_color_map.keys())
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
            self.isolate,
            self.tex_string,
            self.alignment,
            self.tex_environment,
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

    def pre_parse(self) -> None:
        super().pre_parse()
        self.backslash_indices = self.get_backslash_indices()
        self.brace_index_pairs = self.get_brace_index_pairs()
        self.script_char_indices = self.get_script_char_indices()
        self.script_char_spans = self.get_script_char_spans()
        self.script_content_spans = self.get_script_content_spans()
        self.script_spans = self.get_script_spans()

    # Toolkits

    @staticmethod
    def get_begin_color_command_str(rgb_int: int) -> str:
        rgb_tuple = MTex.int_to_rgb(rgb_int)
        return "".join([
            "{{",
            "\\color[RGB]",
            "{",
            ",".join(map(str, rgb_tuple)),
            "}"
        ])

    @staticmethod
    def get_end_color_command_str() -> str:
        return "}}"

    # Pre-parsing

    def get_backslash_indices(self) -> list[int]:
        # Newlines (`\\`) don't count.
        return [
            span[1] - 1
            for span in self.find_spans(r"\\+")
            if (span[1] - span[0]) % 2 == 1
        ]

    def get_unescaped_char_indices(self, *chars: str):
        return sorted(filter(
            lambda index: index - 1 not in self.backslash_indices,
            [
                span[0]
                for char in chars
                for span in self.find_spans(re.escape(char))
            ]
        ))

    def get_brace_index_pairs(self) -> list[Span]:
        string = self.string
        indices = self.get_unescaped_char_indices("{", "}")
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
        return list(zip(left_brace_indices, right_brace_indices))

    def get_script_char_indices(self) -> list[int]:
        return self.get_unescaped_char_indices("_", "^")

    def get_script_char_spans(self) -> list[Span]:
        return [
            self.extend_span((index, index + 1), self.space_spans)
            for index in self.script_char_indices
        ]

    def get_script_content_spans(self) -> list[Span]:
        result = []
        brace_indices_dict = dict(self.brace_index_pairs)
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

    def get_script_spans(self) -> list[Span]:
        return [
            (script_char_span[0], script_content_span[1])
            for script_char_span, script_content_span in zip(
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
                repl_str = "\\" + cmd_name + n_braces * "{white}"
            else:
                repl_str = ""
            result.append(((span_begin, span_end), repl_str))
        return result

    def get_ignored_indices(self) -> list[int]:
        return self.script_char_indices

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

    def get_inserted_string_pairs(
        self, use_plain_file: bool
    ) -> list[tuple[Span, tuple[str, str]]]:
        if use_plain_file:
            return []

        extended_label_span_list = [
            span
            if span in self.script_content_spans
            else (span[0], self.rslide(span[1], self.script_spans))
            for span in self.label_span_list
        ]
        return [
            (span, (
                self.get_begin_color_command_str(label),
                self.get_end_color_command_str()
            ))
            for label, span in enumerate(extended_label_span_list)
        ]

    def get_other_repl_items(
        self, use_plain_file: bool
    ) -> list[tuple[Span, str]]:
        if use_plain_file:
            return []
        return self.command_repl_items.copy()

    def get_has_predefined_colors(self) -> bool:
        return bool(self.command_repl_items)

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

    def get_parts_by_tex(self, tex: str) -> VGroup:
        return self.get_parts_by_string(tex)

    def get_part_by_tex(self, tex: str) -> VMobject:
        return self.get_part_by_string(tex)

    def set_color_by_tex(self, tex: str, color: ManimColor):
        return self.set_color_by_string(tex, color)

    def set_color_by_tex_to_color_map(
        self, tex_to_color_map: dict[str, ManimColor]
    ):
        return self.set_color_by_string_to_color_map(tex_to_color_map)

    def get_tex(self) -> str:
        return self.get_string()


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
