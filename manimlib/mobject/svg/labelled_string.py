from __future__ import annotations

from abc import ABC, abstractmethod
import itertools as it
import re

import numpy as np

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
    from typing import Iterable, Sequence, TypeVar, Union

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
    T = TypeVar("T")


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
        self.base_color_int = self.color_to_int(self.base_color)

        self.full_span = (0, len(self.string))
        self.parse()
        super().__init__(**kwargs)
        self.labelled_submobject_items = [
            (submob.label, submob)
            for submob in self.submobjects
        ]

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

        unrecognized_color_ints = self.remove_redundancies(sorted(filter(
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

    def parse(self) -> None:
        self.command_repl_items = self.get_command_repl_items()
        self.specified_spans = self.get_specified_spans()
        self.check_overlapping()
        self.label_span_list = self.get_label_span_list()
        if len(self.label_span_list) >= 16777216:
            raise ValueError("Cannot handle that many substrings")

    # Toolkits

    def get_substr(self, span: Span) -> str:
        return self.string[slice(*span)]

    def match(self, pattern: str | re.Pattern, **kwargs) -> re.Pattern | None:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return re.compile(pattern).match(self.string, **kwargs)

    def find_spans(self, pattern: str | re.Pattern, **kwargs) -> list[Span]:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return [
            match_obj.span()
            for match_obj in pattern.finditer(self.string, **kwargs)
        ]

    def find_indices(self, pattern: str | re.Pattern, **kwargs) -> list[int]:
        return [index for index, _ in self.find_spans(pattern, **kwargs)]

    def find_spans_by_selector(self, selector: Selector) -> list[Span]:
        def find_spans_by_single_selector(sel):
            if isinstance(sel, str):
                return self.find_spans(re.escape(sel))
            if isinstance(sel, re.Pattern):
                return self.find_spans(sel)
            if isinstance(sel, tuple) and len(sel) == 2 and all([
                isinstance(index, int) or index is None
                for index in sel
            ]):
                string_len = self.full_span[1]
                span = tuple([
                    (
                        min(index, string_len)
                        if index >= 0
                        else max(index + string_len, 0)
                    )
                    if index is not None else default_index
                    for index, default_index in zip(sel, self.full_span)
                ])
                return [span]
            return None

        result = find_spans_by_single_selector(selector)
        if result is None:
            result = []
            for sel in selector:
                spans = find_spans_by_single_selector(sel)
                if spans is None:
                    raise TypeError(f"Invalid selector: '{sel}'")
                result.extend(spans)
        return sorted(filter(
            lambda span: span[0] < span[1],
            self.remove_redundancies(result)
        ))

    @staticmethod
    def chain(*iterables: Iterable[T]) -> list[T]:
        return list(it.chain(*iterables))

    @staticmethod
    def remove_redundancies(vals: Sequence[T]) -> list[T]:
        return remove_list_redundancies(vals)

    @staticmethod
    def get_neighbouring_pairs(vals: Sequence[T]) -> list[tuple[T, T]]:
        return list(zip(vals[:-1], vals[1:]))

    @staticmethod
    def compress_neighbours(vals: Sequence[T]) -> list[tuple[T, Span]]:
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
        val_ranges = LabelledString.get_neighbouring_pairs(indices)
        return list(zip(unique_vals, val_ranges))

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
    def merge_inserted_strings_from_pairs(
        inserted_string_pairs: list[tuple[Span, tuple[str, str]]]
    ) -> list[tuple[int, str]]:
        if not inserted_string_pairs:
            return []

        indices, *_, inserted_strings = zip(*sorted([
            (
                span[flag],
                np.sign(span[1 - flag] - span[flag]),
                -span[1 - flag],
                flag,
                (1, -1)[flag] * item_index,
                str_pair[flag]
            )
            for item_index, (span, str_pair) in enumerate(
                inserted_string_pairs
            )
            for flag in range(2)
        ]))
        return [
            (index, "".join(inserted_strings[slice(*index_range)]))
            for index, index_range
            in LabelledString.compress_neighbours(indices)
        ]

    def get_replaced_substr(
        self, span: Span, repl_items: list[tuple[Span, str]]
    ) -> str:
        if not repl_items:
            return self.get_substr(span)

        repl_spans, repl_strs = zip(*sorted(repl_items))
        pieces = [
            self.get_substr(piece_span)
            for piece_span in self.get_complement_spans(repl_spans, span)
        ]
        repl_strs = [*repl_strs, ""]
        return "".join(self.chain(*zip(pieces, repl_strs)))

    def get_replaced_string(
        self,
        inserted_string_pairs: list[tuple[Span, tuple[str, str]]],
        repl_items: list[tuple[Span, str]]
    ) -> str:
        all_repl_items = self.chain(
            repl_items,
            [
                ((index, index), inserted_string)
                for index, inserted_string
                in self.merge_inserted_strings_from_pairs(
                    inserted_string_pairs
                )
            ]
        )
        return self.get_replaced_substr(self.full_span, all_repl_items)

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

    @abstractmethod
    def get_specified_spans(self) -> list[Span]:
        return []

    def check_overlapping(self) -> None:
        for span_0, span_1 in it.product(self.specified_spans, repeat=2):
            if not span_0[0] < span_1[0] < span_0[1] < span_1[1]:
                continue
            raise ValueError(
                "Partially overlapping substrings detected: "
                f"'{self.get_substr(span_0)}' and '{self.get_substr(span_1)}'"
            )

    @abstractmethod
    def get_label_span_list(self) -> list[Span]:
        return []

    @abstractmethod
    def get_content(self, is_labelled: bool) -> str:
        return ""

    # Selector

    @abstractmethod
    def get_cleaned_substr(self, span: Span) -> str:
        return ""

    def get_group_part_items(self) -> list[tuple[str, VGroup]]:
        if not self.labelled_submobject_items:
            return []

        labels, labelled_submobjects = zip(*self.labelled_submobject_items)
        group_labels, labelled_submob_ranges = zip(
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
        group_substrs = [
            self.get_cleaned_substr(span) if span[0] < span[1] else ""
            for span in self.get_complement_spans(
                interval_spans, (ordered_spans[0][0], ordered_spans[-1][1])
            )
        ]
        submob_groups = VGroup(*[
            VGroup(*labelled_submobjects[slice(*submob_range)])
            for submob_range in labelled_submob_ranges
        ])
        return list(zip(group_substrs, submob_groups))

    def get_specified_part_items(self) -> list[tuple[str, VGroup]]:
        return [
            (
                self.get_substr(span),
                self.select_part_by_span(span)
            )
            for span in self.specified_spans
        ]

    def select_part_by_span(self, custom_span: Span) -> VGroup:
        return VGroup(*[
            submob for label, submob in self.labelled_submobject_items
            if self.span_contains(custom_span, self.label_span_list[label])
        ])

    def select_parts(self, selector: Selector) -> VGroup:
        return VGroup(*filter(
            lambda part: part.submobjects,
            [
                self.select_part_by_span(span)
                for span in self.find_spans_by_selector(selector)
            ]
        ))

    def select_part(self, selector: Selector, index: int = 0) -> VGroup:
        return self.select_parts(selector)[index]

    def set_parts_color(self, selector: Selector, color: ManimColor):
        self.select_parts(selector).set_color(color)
        return self

    def set_parts_color_by_dict(self, color_map: dict[Selector, ManimColor]):
        for selector, color in color_map.items():
            self.set_parts_color(selector, color)
        return self

    def get_string(self) -> str:
        return self.string
