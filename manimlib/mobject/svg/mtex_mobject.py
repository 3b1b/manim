from __future__ import annotations

import re
import colour
import itertools as it
from types import MethodType
from typing import Iterable, Union, Sequence

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


SCALE_FACTOR_PER_FONT_POINT = 0.001


class _TexSVG(SVGMobject):
    CONFIG = {
        "height": None,
        "stroke_width": 0,
        "stroke_color": WHITE,
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        },
    }


class MTex(_TexSVG):
    CONFIG = {
        "base_color": WHITE,
        "font_size": 48,
        "alignment": "\\centering",
        "tex_environment": "align*",
        "isolate": [],
        "tex_to_color_map": {},
        "use_plain_tex": False,
    }

    def __init__(self, string: str, **kwargs):
        digest_config(self, kwargs)
        string = string.strip()
        # Prevent from passing an empty string.
        if not string:
            string = "\\quad"
        self.tex_string = string
        self.string = string
        super().__init__(**kwargs)

        self.set_color_by_tex_to_color_map(self.tex_to_color_map)
        self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)

    @property
    def hash_seed(self) -> tuple:
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.string,
            self.base_color,
            self.alignment,
            self.tex_environment,
            self.isolate,
            self.tex_to_color_map,
            self.use_plain_tex
        )

    def get_file_path(self) -> str:
        self.init_parser()
        self.use_plain_file = any([
            self.use_plain_tex,
            self.color_cmd_repl_items,
            self.base_color != WHITE
        ])
        return self.get_file_path_(use_plain_file=self.use_plain_file)

    def get_file_path_(self, use_plain_file: bool) -> str:
        if use_plain_file:
            content = "".join([
                "{{",
                self.get_color_command(self.color_to_int(self.base_color)),
                self.string,
                "}}"
            ])
        else:
            content = self.get_labelled_string()

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

    def generate_mobject(self) -> None:
        super().generate_mobject()

        glyphs = self.submobjects
        if not glyphs:
            return

        if self.use_plain_file:
            file_path = self.get_file_path_(use_plain_file=False)
            labelled_svg_glyphs = _TexSVG(file_path)
            predefined_colors = [
                labelled_glyph.get_fill_color()
                for labelled_glyph in self.submobjects
            ]
        else:
            labelled_svg_glyphs = self
            predefined_colors = [self.base_color] * len(glyphs)

        glyph_labels = [
            self.color_to_label(labelled_glyph.get_fill_color())
            for labelled_glyph in labelled_svg_glyphs
        ]
        for glyph, glyph_color in zip(glyphs, predefined_colors):
            glyph.set_fill(glyph_color)

        # Simply pack together adjacent mobjects with the same label.
        submob_labels, glyphs_lists = self.group_neighbours(
            glyph_labels, glyphs
        )
        submobjects = [
            VGroup(*glyph_list)
            for glyph_list in glyphs_lists
        ]
        submob_tex_strings = self.get_submob_tex_strings(submob_labels)
        for submob, label, submob_tex in zip(
            submobjects, submob_labels, submob_tex_strings
        ):
            submob.label = label
            submob.tex_string = submob_tex
            # Support `get_tex()` method here.
            submob.get_tex = MethodType(lambda inst: inst.tex_string, submob)
        self.set_submobjects(submobjects)

    ## Static methods

    @staticmethod
    def color_to_int(color: ManimColor) -> int:
        r, g, b = color_to_int_rgb(color)
        rg = r * 256 + g
        return rg * 256 + b

    @staticmethod
    def color_to_label(color: ManimColor) -> int:
        result = MTex.color_to_int(color)
        if result == 16777215:  # white
            return -1
        return result

    @staticmethod
    def get_color_command(label: int) -> str:
        rg, b = divmod(label, 256)
        r, g = divmod(rg, 256)
        return "".join([
            "\\color[RGB]",
            "{",
            ",".join(map(str, (r, g, b))),
            "}"
        ])

    @staticmethod
    def get_neighbouring_pairs(iterable: Iterable) -> list:
        return list(adjacent_pairs(iterable))[:-1]

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

    ## Parser

    def init_parser(self) -> None:
        self.additional_substrings = self.get_additional_substrings()
        self.full_span = self.get_full_span()
        self.backslash_indices = self.get_backslash_indices()
        self.left_brace_indices, self.right_brace_indices = \
            self.get_left_and_right_indices()
        self.script_char_spans = self.get_script_char_spans()
        self.skipped_indices = self.get_skipped_indices()
        self.script_spans = self.get_script_spans()
        self.script_content_spans = self.get_script_content_spans()
        self.double_braces_spans = self.get_double_braces_spans()
        self.stripped_substrings = self.get_stripped_substrings()
        self.specified_substrings = self.get_specified_substrings()
        self.specified_spans, self.extended_specified_spans = \
            self.get_specified_spans()
        self.tex_span_list = self.get_tex_span_list()
        self.extended_tex_span_list = self.get_extended_tex_span_list()
        self.isolated_substrings = self.get_isolated_substrings()
        self.containing_labels_dict = self.get_containing_labels_dict()
        self.color_cmd_repl_items = self.get_color_cmd_repl_items()
        self.span_repl_dict = self.get_span_repl_dict()

    def get_additional_substrings(self) -> list[str]:
        return list(it.chain(
            self.tex_to_color_map.keys(),
            self.isolate
        ))

    def get_full_span(self) -> tuple[int, int]:
        return (0, len(self.string))

    def get_backslash_indices(self) -> list[int]:
        # Newlines (`\\`) don't count.
        return [
            match_obj.end() - 1
            for match_obj in re.finditer(r"\\+", self.string)
            if len(match_obj.group()) % 2 == 1
        ]

    def get_left_and_right_indices(self) -> list[tuple[int, int]]:
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
        return left_brace_indices, right_brace_indices

    def get_script_char_spans(self) -> list[tuple[int, int]]:
        return [
            match_obj.span()
            for match_obj in re.finditer(r"(\s*)[_^]\s*", self.string)
            if match_obj.group(1)
            or match_obj.start() - 1 not in self.backslash_indices
        ]

    def get_skipped_indices(self) -> list[int]:
        return sorted(remove_list_redundancies([
            match_obj.start()
            for match_obj in re.finditer(r"\s", self.string)
        ] + list(it.chain(*[
            range(*script_char_span)
            for script_char_span in self.script_char_spans
        ]))))

    def get_script_spans(self) -> list[tuple[int, int]]:
        string = self.string
        result = []
        brace_indices_dict = dict(zip(
            self.left_brace_indices, self.right_brace_indices
        ))
        for char_begin, span_begin in self.script_char_spans:
            if span_begin in brace_indices_dict.keys():
                span_end = brace_indices_dict[span_begin] + 1
            else:
                pattern = re.compile(r"[a-zA-Z0-9]|\\[a-zA-Z]+")
                match_obj = pattern.match(string, pos=span_begin)
                if not match_obj:
                    script_name = {
                        "_": "subscript",
                        "^": "superscript"
                    }[script_char]
                    log.warning(
                        f"Unclear {script_name} detected while parsing. "
                        "Please use braces to clarify"
                    )
                    continue
                span_end = match_obj.end()
            result.append((char_begin, span_end))
        return result

    def get_script_content_spans(self) -> list[tuple[int, int]]:
        return [
            (script_char_span[1], script_span[1])
            for script_char_span, script_span in zip(
                self.script_char_spans, self.script_spans
            )
        ]

    def get_double_braces_spans(self) -> list[tuple[int, int]]:
        # Match paired double braces (`{{...}}`).
        result = []
        reversed_brace_indices_dict = dict(zip(
            self.right_brace_indices, self.left_brace_indices
        ))
        skip = False
        for prev_right_index, right_index in self.get_neighbouring_pairs(
            sorted(reversed_brace_indices_dict.keys())
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

    def get_stripped_substrings(self) -> list[str]:
        result = remove_list_redundancies([
            substr.strip()
            for substr in self.additional_substrings
        ])
        if "" in result:
            result.remove("")
        return result

    def get_specified_substrings(self) -> list[str]:
        return remove_list_redundancies([
            self.string[slice(*double_braces_span)]
            for double_braces_span in self.double_braces_spans
        ] + list(filter(
            lambda s: s in self.string,
            self.stripped_substrings
        )))

    def get_specified_spans(
        self
    ) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        tex_spans = sorted(remove_list_redundancies([
            self.full_span,
            *self.double_braces_spans,
            *[
                match_obj.span()
                for substr in self.stripped_substrings
                for match_obj in re.finditer(re.escape(substr), self.string)
            ]
        ]), key=lambda t: (t[0], -t[1]))
        result = []
        extended_result = []
        script_spans_dict = dict(self.script_spans)
        reversed_script_spans_dict = dict([
            script_span[::-1] for script_span in self.script_spans
        ])
        for tex_span in tex_spans:
            if tex_span in self.script_content_spans:
                continue
            span_begin, span_end = tex_span
            extended_span_end = span_end
            while span_end in reversed_script_spans_dict.keys():
                span_end = reversed_script_spans_dict[span_end]
            while extended_span_end in script_spans_dict.keys():
                extended_span_end = script_spans_dict[extended_span_end]
            specified_span = (span_begin, span_end)
            extended_specified_span = (span_begin, extended_span_end)
            if span_begin >= span_end:
                continue
            if extended_specified_span in result:
                continue
            result.append(specified_span)
            extended_result.append(extended_specified_span)
        return result, extended_result

    def get_tex_span_list(self) -> list[tuple[int, int]]:
        return self.specified_spans + self.script_content_spans

    def get_extended_tex_span_list(self) -> list[tuple[int, int]]:
        return self.extended_specified_spans + self.script_content_spans

    def get_isolated_substrings(self) -> list[str]:
        return remove_list_redundancies([
            self.string[slice(*tex_span)]
            for tex_span in self.tex_span_list
        ])

    def get_containing_labels_dict(self) -> dict[tuple[int, int], list[int]]:
        tex_span_list = self.tex_span_list
        result = {
            tex_span: []
            for tex_span in tex_span_list
        }
        for span_0 in tex_span_list:
            for span_index, span_1 in enumerate(tex_span_list):
                if span_0[0] <= span_1[0] and span_1[1] <= span_0[1]:
                    result[span_0].append(span_index)
                elif span_0[0] < span_1[0] < span_0[1] < span_1[1]:
                    string_0, string_1 = [
                        self.string[slice(*tex_span)]
                        for tex_span in [span_0, span_1]
                    ]
                    raise ValueError(
                        "Partially overlapping substrings detected: "
                        f"'{string_0}' and '{string_1}'"
                    )
        result[self.full_span] = list(range(len(tex_span_list)))
        return result

    def get_color_cmd_repl_items(self) -> list[tuple[tuple[int, int], str]]:
        color_related_command_items = [
            ("color", 1, ""),
            ("textcolor", 1, ""),
            ("pagecolor", 1, "\\pagecolor{white}"),
            ("colorbox", 1, "\\colorbox{white}"),
            ("fcolorbox", 2, "\\fcolorbox{white}{white}"),
        ]
        result = []
        string = self.string
        backslash_indices = self.backslash_indices
        left_indices = self.left_brace_indices
        brace_indices_dict = dict(zip(
            self.left_brace_indices, self.right_brace_indices
        ))
        for cmd_name, n_braces, repl_str in color_related_command_items:
            pattern = cmd_name + r"(?![a-zA-Z])"
            for match_obj in re.finditer(pattern, string):
                span_begin, span_end = match_obj.span()
                span_begin -= 1
                if span_begin not in backslash_indices:
                    continue
                for _ in range(n_braces):
                    left_index = min(filter(
                        lambda index: index >= span_end, left_indices
                    ))
                    span_end = brace_indices_dict[left_index] + 1
                result.append(((span_begin, span_end), repl_str))
        return result

    def get_span_repl_dict(self) -> dict[tuple[int, int], str]:
        indices, _, _, cmd_strings = zip(*sorted([
            (
                tex_span[flag],
                -flag,
                -tex_span[1 - flag],
                ("{{" + self.get_color_command(label), "}}")[flag]
            )
            for label, tex_span in enumerate(self.tex_span_list)
            for flag in range(2)
        ]))
        result = {
            (index, index): "".join(cmd_strs)
            for index, cmd_strs in zip(*self.group_neighbours(
                indices, cmd_strings
            ))
        }
        result.update(self.color_cmd_repl_items)
        return result

    def get_labelled_string(self) -> str:
        if not self.span_repl_dict:
            return self.string

        spans = sorted(self.span_repl_dict.keys())
        if not all(
            span_0[1] <= span_1[0]
            for span_0, span_1 in self.get_neighbouring_pairs(spans)
        ):
            raise ValueError("Failed to generate the labelled string")

        span_ends, span_begins = zip(*spans)
        string_pieces = [
            self.string[slice(*span)]
            for span in zip(
                (0, *span_begins),
                (*span_ends, len(self.string))
            )
        ]
        repl_strs = [
            self.span_repl_dict[span]
            for span in spans
        ]
        repl_strs.append("")
        return "".join(it.chain(*zip(string_pieces, repl_strs)))

    def get_submob_tex_strings(self, submob_labels: list[int]) -> list[str]:
        ordered_tex_spans = [
            self.tex_span_list[label] if label != -1 else self.full_span
            for label in submob_labels
        ]
        ordered_containing_labels = [
            self.containing_labels_dict[tex_span]
            for tex_span in ordered_tex_spans
        ]
        ordered_span_begins, ordered_span_ends = zip(*ordered_tex_spans)
        string_span_begins = [
            prev_end if prev_label in containing_labels else curr_begin
            for prev_end, prev_label, containing_labels, curr_begin in zip(
                ordered_span_ends[:-1], submob_labels[:-1],
                ordered_containing_labels[1:], ordered_span_begins[1:]
            )
        ]
        string_span_begins.insert(0, ordered_span_begins[0])
        string_span_ends = [
            next_begin if next_label in containing_labels else curr_end
            for next_begin, next_label, containing_labels, curr_end in zip(
                ordered_span_begins[1:], submob_labels[1:],
                ordered_containing_labels[:-1], ordered_span_ends[:-1]
            )
        ]
        string_span_ends.append(ordered_span_ends[-1])

        string = self.string
        left_indices = self.left_brace_indices
        right_indices = self.right_brace_indices
        skipped_indices = sorted(it.chain(
            self.skipped_indices,
            left_indices,
            right_indices
        ))
        result = []
        for span_begin, span_end in zip(string_span_begins, string_span_ends):
            while span_begin in skipped_indices:
                span_begin += 1
            if span_begin >= span_end:
                result.append("")
                continue
            while span_end - 1 in skipped_indices:
                span_end -= 1
            unclosed_left_brace = 0
            unclosed_right_brace = 0
            for index in range(span_begin, span_end):
                if index in left_indices:
                    unclosed_left_brace += 1
                elif index in right_indices:
                    if unclosed_left_brace == 0:
                        unclosed_right_brace += 1
                    else:
                        unclosed_left_brace -= 1
            result.append("".join([
                unclosed_right_brace * "{",
                string[span_begin:span_end],
                unclosed_left_brace * "}"
            ]))
        return result

    ## Selector

    def find_span_components_of_custom_span(
        self,
        custom_span: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        skipped_indices = self.skipped_indices
        tex_span_choices = sorted(filter(
            lambda tex_span: all([
                tex_span[0] >= custom_span[0],
                tex_span[1] <= custom_span[1]
            ]),
            self.tex_span_list
        ))
        # Choose spans that reach the farthest.
        tex_span_choices_dict = dict(tex_span_choices)

        span_begin, span_end = custom_span
        result = []
        while span_begin != span_end:
            if span_begin not in tex_span_choices_dict.keys():
                if span_begin in skipped_indices:
                    span_begin += 1
                    continue
                return None
            next_begin = tex_span_choices_dict[span_begin]
            result.append((span_begin, next_begin))
            span_begin = next_begin
        return result

    def get_part_by_custom_span(self, custom_span: tuple[int, int]) -> VGroup:
        tex_spans = self.find_span_components_of_custom_span(
            custom_span
        )
        if tex_spans is None:
            tex = self.string[slice(*custom_span)]
            raise ValueError(f"Failed to match mobjects from tex: \"{tex}\"")

        labels = set(it.chain(*[
            self.containing_labels_dict[tex_span]
            for tex_span in tex_spans
        ]))
        return VGroup(*filter(
            lambda submob: submob.label in labels,
            self.submobjects
        ))

    def get_parts_by_tex(self, tex: str) -> VGroup:
        return VGroup(*[
            self.get_part_by_custom_span(match_obj.span())
            for match_obj in re.finditer(
                re.escape(tex.strip()), self.string
            )
        ])

    def get_part_by_tex(self, tex: str, index: int = 0) -> VMobject:
        all_parts = self.get_parts_by_tex(tex)
        return all_parts[index]

    def set_color_by_tex(self, tex: str, color: ManimColor):
        self.get_parts_by_tex(tex).set_color(color)
        return self

    def set_color_by_tex_to_color_map(
        self,
        tex_to_color_map: dict[str, ManimColor]
    ):
        for tex, color in tex_to_color_map.items():
            self.set_color_by_tex(tex, color)
        return self

    def indices_of_part(self, part: Iterable[VMobject]) -> list[int]:
        indices = [
            index for index, submob in enumerate(self.submobjects)
            if submob in part
        ]
        if not indices:
            raise ValueError("Failed to find part in tex")
        return indices

    def indices_of_part_by_tex(self, tex: str, index: int = 0) -> list[int]:
        part = self.get_part_by_tex(tex, index=index)
        return self.indices_of_part(part)

    def get_tex(self) -> str:
        return self.string

    def get_submob_tex(self) -> list[str]:
        return [
            submob.get_tex()
            for submob in self.submobjects
        ]


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
