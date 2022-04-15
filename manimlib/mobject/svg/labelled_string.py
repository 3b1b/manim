from __future__ import annotations

from abc import ABC, abstractmethod
import itertools as it
import re

from manimlib.constants import WHITE
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.color import color_to_rgb
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import remove_list_redundancies

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from colour import Color
    from typing import Iterable, Union

    from manimlib.mobject.types.vectorized_mobject import VMobject

    ManimColor = Union[str, Color]
    Span = tuple[int, int]
    Selector = Union[
        str,
        re.Pattern,
        tuple[Union[int, None], Union[int, None]]
    ]


class LabelledString(SVGMobject, ABC):
    """
    An abstract base class for `MTex` and `MarkupText`
    """
    CONFIG = {
        "height": None,
        "stroke_width": 0,
        "stroke_color": WHITE,
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        },
        "base_color": WHITE,
        "isolate": [],
    }

    def __init__(self, string: str, **kwargs):
        self.string = string
        digest_config(self, kwargs)
        if self.base_color is None:
            self.base_color = WHITE

        self.pre_parse()
        self.parse()
        super().__init__()
        self.post_parse()

    def get_file_path(self) -> str:
        return self.get_file_path_(is_labelled=False)

    def get_file_path_(self, is_labelled: bool) -> str:
        content = self.get_content(is_labelled)
        return self.get_file_path_by_content(content)

    @abstractmethod
    def get_file_path_by_content(self, content: str) -> str:
        return ""

    def generate_mobject(self) -> None:
        super().generate_mobject()

        num_labels = len(self.label_span_list)
        if num_labels:
            file_path = self.get_file_path_(is_labelled=True)
            labelled_svg = SVGMobject(file_path)
            submob_color_ints = [
                self.color_to_int(submob.get_fill_color())
                for submob in labelled_svg.submobjects
            ]
        else:
            submob_color_ints = [0] * len(self.submobjects)

        if len(self.submobjects) != len(submob_color_ints):
            raise ValueError(
                "Cannot align submobjects of the labelled svg "
                "to the original svg"
            )

        unrecognized_color_ints = remove_list_redundancies(sorted(filter(
            lambda color_int: color_int > num_labels,
            submob_color_ints
        )))
        if unrecognized_color_ints:
            raise ValueError(
                "Unrecognized color label(s) detected: "
                f"{','.join(map(self.int_to_hex, unrecognized_color_ints))}"
            )

        for submob, color_int in zip(self.submobjects, submob_color_ints):
            submob.label = color_int - 1

    def pre_parse(self) -> None:
        self.string_len = len(self.string)
        self.full_span = (0, self.string_len)
        self.space_spans = self.find_spans(r"\s+")
        self.base_color_int = self.color_to_int(self.base_color)

    def parse(self) -> None:
        self.command_repl_items = self.get_command_repl_items()
        self.command_spans = self.get_command_spans()
        self.extra_entity_spans = self.get_extra_entity_spans()
        self.entity_spans = self.get_entity_spans()
        self.extra_ignored_spans = self.get_extra_ignored_spans()
        self.skipped_spans = self.get_skipped_spans()
        self.internal_specified_spans = self.get_internal_specified_spans()
        self.external_specified_spans = self.get_external_specified_spans()
        self.specified_spans = self.get_specified_spans()
        self.label_span_list = self.get_label_span_list()
        self.check_overlapping()

    def post_parse(self) -> None:
        self.labelled_submobject_items = [
            (submob.label, submob)
            for submob in self.submobjects
        ]
        self.labelled_submobjects = self.get_labelled_submobjects()
        self.specified_substrs = self.get_specified_substrs()
        self.group_items = self.get_group_items()
        self.group_substrs = self.get_group_substrs()
        self.submob_groups = self.get_submob_groups()

    def copy(self):
        return self.deepcopy()

    # Toolkits

    def get_substr(self, span: Span) -> str:
        return self.string[slice(*span)]

    def find_spans(self, pattern: str | re.Pattern) -> list[Span]:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return [
            match_obj.span()
            for match_obj in pattern.finditer(self.string)
        ]

    def match_at(self, pattern: str, pos: int) -> re.Pattern | None:
        return re.compile(pattern).match(self.string, pos=pos)

    def find_spans_by_selector(self, selector: Selector) -> list[Span]:
        if isinstance(selector, str):
            result = self.find_spans(re.escape(selector))
        elif isinstance(selector, re.Pattern):
            result = self.find_spans(selector)
        else:
            span = tuple([
                (
                    min(index, self.string_len)
                    if index >= 0
                    else max(index + self.string_len, 0)
                )
                if index is not None else default_index
                for index, default_index in zip(selector, self.full_span)
            ])
            result = [span]
        return list(filter(lambda span: span[0] < span[1], result))

    @staticmethod
    def get_neighbouring_pairs(iterable: list) -> list[tuple]:
        return list(zip(iterable[:-1], iterable[1:]))

    @staticmethod
    def span_contains(span_0: Span, span_1: Span) -> bool:
        return span_0[0] <= span_1[0] and span_0[1] >= span_1[1]

    @staticmethod
    def get_complement_spans(
        interval_spans: list[Span], universal_span: Span
    ) -> list[Span]:
        if not interval_spans:
            return [universal_span]

        span_ends, span_begins = zip(*interval_spans)
        return list(zip(
            (universal_span[0], *span_begins),
            (*span_ends, universal_span[1])
        ))

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
        return sorted_seq[index + index_shift]

    @staticmethod
    def generate_span_repl_dict(
        inserted_string_pairs: list[tuple[Span, tuple[str, str]]],
        other_repl_items: list[tuple[Span, str]]
    ) -> dict[Span, str]:
        result = dict(other_repl_items)
        if not inserted_string_pairs:
            return result

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
        result.update({
            (index, index): "".join(inserted_strings[slice(*item_span)])
            for index, item_span
            in LabelledString.compress_neighbours(indices)
        })
        return result

    def get_replaced_substr(
        self, span: Span, span_repl_dict: dict[Span, str]
    ) -> str:
        repl_spans = sorted(filter(
            lambda repl_span: self.span_contains(span, repl_span),
            span_repl_dict.keys()
        ))
        if not all(
            span_0[1] <= span_1[0]
            for span_0, span_1 in self.get_neighbouring_pairs(repl_spans)
        ):
            raise ValueError("Overlapping replacement")

        pieces = [
            self.get_substr(piece_span)
            for piece_span in self.get_complement_spans(repl_spans, span)
        ]
        repl_strs = [span_repl_dict[repl_span] for repl_span in repl_spans]
        repl_strs.append("")
        return "".join(it.chain(*zip(pieces, repl_strs)))

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
    def color_to_int(color: ManimColor) -> int:
        hex_code = rgb_to_hex(color_to_rgb(color))
        return int(hex_code[1:], 16)

    @staticmethod
    def int_to_hex(rgb_int: int) -> str:
        return "#{:06x}".format(rgb_int).upper()

    # Parsing

    @abstractmethod
    def get_command_repl_items(self) -> list[tuple[Span, str]]:
        return []

    def get_command_spans(self) -> list[Span]:
        return [cmd_span for cmd_span, _ in self.command_repl_items]

    @abstractmethod
    def get_extra_entity_spans(self) -> list[Span]:
        return []

    def get_entity_spans(self) -> list[Span]:
        return list(it.chain(
            self.command_spans,
            self.extra_entity_spans
        ))

    def is_splittable_index(self, index: int) -> bool:
        return not any([
            entity_span[0] < index < entity_span[1]
            for entity_span in self.entity_spans
        ])

    @abstractmethod
    def get_extra_ignored_spans(self) -> list[int]:
        return []

    def get_skipped_spans(self) -> list[Span]:
        return list(it.chain(
            self.find_spans(r"\s"),
            self.command_spans,
            self.extra_ignored_spans
        ))

    def shrink_span(self, span: Span) -> Span:
        return (
            self.rslide(span[0], self.skipped_spans),
            self.lslide(span[1], self.skipped_spans)
        )

    @abstractmethod
    def get_internal_specified_spans(self) -> list[Span]:
        return []

    @abstractmethod
    def get_external_specified_spans(self) -> list[Span]:
        return []

    def get_specified_spans(self) -> list[Span]:
        spans = list(it.chain(
            self.internal_specified_spans,
            self.external_specified_spans,
            *[
                self.find_spans_by_selector(selector)
                for selector in self.isolate
            ]
        ))
        filtered_spans = list(filter(
            lambda span: all([
                self.is_splittable_index(index)
                for index in span
            ]),
            spans
        ))
        shrinked_spans = list(filter(
            lambda span: span[0] < span[1],
            [self.shrink_span(span) for span in filtered_spans]
        ))
        return remove_list_redundancies(shrinked_spans)

    @abstractmethod
    def get_label_span_list(self) -> list[Span]:
        return []

    def check_overlapping(self) -> None:
        if len(self.label_span_list) >= 16777216:
            raise ValueError("Cannot label that many substrings")
        for span_0, span_1 in it.product(self.label_span_list, repeat=2):
            if not span_0[0] < span_1[0] < span_0[1] < span_1[1]:
                continue
            raise ValueError(
                "Partially overlapping substrings detected: "
                f"'{self.get_substr(span_0)}' and '{self.get_substr(span_1)}'"
            )

    @abstractmethod
    def get_content(self, is_labelled: bool) -> str:
        return ""

    # Post-parsing

    def get_labelled_submobjects(self) -> list[VMobject]:
        return [submob for _, submob in self.labelled_submobject_items]

    def get_cleaned_substr(self, span: Span) -> str:
        span_repl_dict = dict.fromkeys(self.command_spans, "")
        return self.get_replaced_substr(span, span_repl_dict)

    def get_specified_substrs(self) -> list[str]:
        return remove_list_redundancies([
            self.get_cleaned_substr(span)
            for span in self.specified_spans
        ])

    def get_group_items(self) -> list[tuple[str, VGroup]]:
        if not self.labelled_submobject_items:
            return []

        labels, labelled_submobjects = zip(*self.labelled_submobject_items)
        group_labels, labelled_submob_spans = zip(
            *self.compress_neighbours(labels)
        )
        ordered_spans = [
            self.label_span_list[label] if label != -1 else self.full_span
            for label in group_labels
        ]
        interval_spans = [
            (
                next_span[0]
                if self.span_contains(prev_span, next_span)
                else prev_span[1],
                prev_span[1]
                if self.span_contains(next_span, prev_span)
                else next_span[0]
            )
            for prev_span, next_span in self.get_neighbouring_pairs(
                ordered_spans
            )
        ]
        shrinked_spans = [
            self.shrink_span(span)
            for span in self.get_complement_spans(
                interval_spans, (ordered_spans[0][0], ordered_spans[-1][1])
            )
        ]
        group_substrs = [
            self.get_cleaned_substr(span) if span[0] < span[1] else ""
            for span in shrinked_spans
        ]
        submob_groups = VGroup(*[
            VGroup(*labelled_submobjects[slice(*submob_span)])
            for submob_span in labelled_submob_spans
        ])
        return list(zip(group_substrs, submob_groups))

    def get_group_substrs(self) -> list[str]:
        return [group_substr for group_substr, _ in self.group_items]

    def get_submob_groups(self) -> list[VGroup]:
        return [submob_group for _, submob_group in self.group_items]

    def select_parts_by_group_substr(self, substr: str) -> VGroup:
        return VGroup(*[
            group
            for group_substr, group in self.group_items
            if group_substr == substr
        ])

    # Selector

    def find_span_components(
        self, custom_span: Span, substring: bool = True
    ) -> list[Span]:
        shrinked_span = self.shrink_span(custom_span)
        if shrinked_span[0] >= shrinked_span[1]:
            return []

        if substring:
            indices = remove_list_redundancies(list(it.chain(
                self.full_span,
                *self.label_span_list
            )))
            span_begin = self.take_nearest_value(
                indices, shrinked_span[0], 0
            )
            span_end = self.take_nearest_value(
                indices, shrinked_span[1] - 1, 1
            )
        else:
            span_begin, span_end = shrinked_span

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

    def select_part_by_span(self, custom_span: Span, **kwargs) -> VGroup:
        labels = [
            label for label, span in enumerate(self.label_span_list)
            if any([
                self.span_contains(span_component, span)
                for span_component in self.find_span_components(
                    custom_span, **kwargs
                )
            ])
        ]
        return VGroup(*[
            submob for label, submob in self.labelled_submobject_items
            if label in labels
        ])

    def select_parts(self, selector: Selector, **kwargs) -> VGroup:
        return VGroup(*[
            self.select_part_by_span(span, **kwargs)
            for span in self.find_spans_by_selector(selector)
        ])

    def select_part(
        self, selector: Selector, index: int = 0, **kwargs
    ) -> VMobject:
        return self.select_parts(selector, **kwargs)[index]

    def set_parts_color(
        self, selector: Selector, color: ManimColor, **kwargs
    ):
        self.select_parts(selector, **kwargs).set_color(color)
        return self

    def set_parts_color_by_dict(
        self, color_map: dict[Selector, ManimColor], **kwargs
    ):
        for selector, color in color_map.items():
            self.set_parts_color(selector, color, **kwargs)
        return self

    def get_string(self) -> str:
        return self.string
