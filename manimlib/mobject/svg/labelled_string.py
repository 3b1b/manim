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

        self.string_len = len(self.string)
        self.full_span = (0, self.string_len)
        self.parse()
        super().__init__()
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

    def parse(self) -> None:
        self.skippable_indices = self.get_skippable_indices()
        self.entity_spans = self.get_entity_spans()
        self.bracket_spans = self.get_bracket_spans()
        self.extra_isolated_items = self.get_extra_isolated_items()
        self.specified_items = self.get_specified_items()
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

    @staticmethod
    def is_single_selector(selector: Selector) -> bool:
        if isinstance(selector, str):
            return True
        if isinstance(selector, re.Pattern):
            return True
        if isinstance(selector, tuple):
            if len(selector) == 2 and all([
                isinstance(index, int) or index is None
                for index in selector
            ]):
                return True
        return False

    def find_spans_by_selector(self, selector: Selector) -> list[Span]:
        if self.is_single_selector(selector):
            selector = (selector,)
        result = []
        for sel in selector:
            if not self.is_single_selector(sel):
                raise TypeError(f"Invalid selector: '{sel}'")
            if isinstance(sel, str):
                spans = self.find_spans(re.escape(sel))
            elif isinstance(sel, re.Pattern):
                spans = self.find_spans(sel)
            else:
                span = tuple([
                    (
                        min(index, self.string_len)
                        if index >= 0
                        else max(index + self.string_len, 0)
                    )
                    if index is not None else default_index
                    for index, default_index in zip(sel, self.full_span)
                ])
                spans = [span]
            result.extend(spans)
        return sorted(filter(
            lambda span: span[0] < span[1],
            remove_list_redundancies(result)
        ))

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
    def generate_span_repl_dict(
        inserted_string_pairs: list[tuple[Span, tuple[str, str]]],
        repl_items: list[tuple[Span, str]]
    ) -> dict[Span, str]:
        result = dict(repl_items)
        if not inserted_string_pairs:
            return result

        indices, _, _, _, inserted_strings = zip(*sorted([
            (
                item[0][flag],
                -flag,
                -item[0][1 - flag],
                (1, -1)[flag] * item_index,
                item[1][flag]
            )
            for item_index, item in enumerate(inserted_string_pairs)
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
    def color_to_int(color: ManimColor) -> int:
        hex_code = rgb_to_hex(color_to_rgb(color))
        return int(hex_code[1:], 16)

    @staticmethod
    def int_to_hex(rgb_int: int) -> str:
        return "#{:06x}".format(rgb_int).upper()

    # Parsing

    @abstractmethod
    def get_skippable_indices(self) -> list[int]:
        return []

    @staticmethod
    def shrink_span(span: Span, skippable_indices: list[int]) -> Span:
        span_begin, span_end = span
        while span_begin in skippable_indices:
            span_begin += 1
        while span_end - 1 in skippable_indices:
            span_end -= 1
        return (span_begin, span_end)

    @abstractmethod
    def get_entity_spans(self) -> list[Span]:
        return []

    @abstractmethod
    def get_bracket_spans(self) -> list[Span]:
        return []

    @abstractmethod
    def get_extra_isolated_items(self) -> list[tuple[Span, dict[str, str]]]:
        return []

    def get_specified_items(self) -> list[tuple[Span, dict[str, str]]]:
        span_items = list(it.chain(
            self.extra_isolated_items,
            [
                (span, {})
                for span in self.find_spans_by_selector(self.isolate)
            ]
        ))
        result = []
        for span, attr_dict in span_items:
            shrinked_span = self.shrink_span(span, self.skippable_indices)
            if shrinked_span[0] >= shrinked_span[1]:
                continue
            if any([
                entity_span[0] < index < entity_span[1]
                for index in shrinked_span
                for entity_span in self.entity_spans
            ]):
                continue
            result.append((shrinked_span, attr_dict))
        return result

    def get_specified_spans(self) -> list[Span]:
        return remove_list_redundancies([
            span for span, _ in self.specified_items
        ])

    def check_overlapping(self) -> None:
        spans = remove_list_redundancies(list(it.chain(
            self.specified_spans,
            self.bracket_spans
        )))
        for span_0, span_1 in it.product(spans, repeat=2):
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
        group_substrs = [
            self.get_cleaned_substr(span) if span[0] < span[1] else ""
            for span in self.get_complement_spans(
                interval_spans, (ordered_spans[0][0], ordered_spans[-1][1])
            )
        ]
        submob_groups = VGroup(*[
            VGroup(*labelled_submobjects[slice(*submob_span)])
            for submob_span in labelled_submob_spans
        ])
        return list(zip(group_substrs, submob_groups))

    def get_specified_part_items(self) -> list[tuple[str, VGroup]]:
        return [
            (
                self.get_substr(span),
                self.select_part_by_span(span, substring=False)
            )
            for span in self.specified_spans
        ]

    def find_span_components(
        self, custom_span: Span, substring: bool = True
    ) -> list[Span]:
        shrinked_span = self.shrink_span(custom_span, self.skippable_indices)
        if shrinked_span[0] >= shrinked_span[1]:
            return []

        if substring:
            indices = remove_list_redundancies(list(it.chain(
                self.full_span,
                *self.label_span_list
            )))
            span_begin = max(filter(
                lambda index: index <= shrinked_span[0], indices
            ))
            span_end = min(filter(
                lambda index: index >= shrinked_span[1], indices
            ))
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
        return VGroup(*filter(
            lambda part: part.submobjects,
            [
                self.select_part_by_span(span, **kwargs)
                for span in self.find_spans_by_selector(selector)
            ]
        ))

    def select_part(
        self, selector: Selector, index: int = 0, **kwargs
    ) -> VGroup:
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
