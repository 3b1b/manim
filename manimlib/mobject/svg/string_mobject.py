from __future__ import annotations

from abc import ABC, abstractmethod
import itertools as it
import re
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

from manimlib.constants import WHITE
from manimlib.logger import log
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.color import color_to_rgb
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.config_ops import digest_config

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from colour import Color
    from typing import Iterable, TypeVar, Union

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


class StringMobject(SVGMobject, ABC):
    """
    An abstract base class for `MTex` and `MarkupText`

    This class aims to optimize the logic of "slicing submobjects
    via substrings". This could be much clearer and more user-friendly
    than slicing through numerical indices explicitly.

    Users are expected to specify substrings in `isolate` parameter
    if they want to do anything with their corresponding submobjects.
    `isolate` parameter can be either a string, a `re.Pattern` object,
    or a 2-tuple containing integers or None, or a collection of the above.
    Note, substrings specified cannot *partly* overlap with each other.

    Each instance of `StringMobject` generates 2 svg files.
    The additional one is generated with some color commands inserted,
    so that each submobject of the original `SVGMobject` will be labelled
    by the color of its paired submobject from the additional `SVGMobject`.
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
        "isolate": (),
    }

    def __init__(self, string: str, **kwargs):
        self.string = string
        digest_config(self, kwargs)
        if self.base_color is None:
            self.base_color = WHITE
        self.base_color_hex = self.color_to_hex(self.base_color)

        self.full_len = len(self.string)
        self.parse()
        super().__init__(**kwargs)
        self.labels = [submob.label for submob in self.submobjects]

    def get_file_path(self) -> str:
        original_content = self.get_content(is_labelled=False)
        return self.get_file_path_by_content(original_content)

    @abstractmethod
    def get_file_path_by_content(self, content: str) -> str:
        return ""

    def generate_mobject(self) -> None:
        super().generate_mobject()

        labels_count = len(self.labelled_spans)
        if not labels_count:
            for submob in self.submobjects:
                submob.label = -1
            return

        labelled_content = self.get_content(is_labelled=True)
        file_path = self.get_file_path_by_content(labelled_content)
        labelled_svg = SVGMobject(file_path)
        if len(self.submobjects) != len(labelled_svg.submobjects):
            log.warning(
                "Cannot align submobjects of the labelled svg "
                "to the original svg. Skip the labelling process."
            )
            for submob in self.submobjects:
                submob.label = -1
            return

        self.rearrange_submobjects_by_positions(labelled_svg)
        unrecognizable_colors = []
        for submob, labelled_svg_submob in zip(
            self.submobjects, labelled_svg.submobjects
        ):
            color_int = self.hex_to_int(self.color_to_hex(
                labelled_svg_submob.get_fill_color()
            ))
            if color_int > labels_count:
                unrecognizable_colors.append(color_int)
                color_int = 0
            submob.label = color_int - 1
        if unrecognizable_colors:
            log.warning(
                "Unrecognizable color labels detected (%s, etc). "
                "The result could be unexpected.",
                self.int_to_hex(unrecognizable_colors[0])
            )

    def rearrange_submobjects_by_positions(
        self, labelled_svg: SVGMobject
    ) -> None:
        # Rearrange submobjects of `labelled_svg` so that
        # each submobject is labelled by the nearest one of `labelled_svg`.
        # The correctness cannot be ensured, since the svg may
        # change significantly after inserting color commands.
        if not labelled_svg.submobjects:
            return

        bb_0 = self.get_bounding_box()
        bb_1 = labelled_svg.get_bounding_box()
        scale_factor = abs((bb_0[2] - bb_0[0]) / (bb_1[2] - bb_1[0]))
        labelled_svg.move_to(self).scale(scale_factor)

        distance_matrix = cdist(
            [submob.get_center() for submob in self.submobjects],
            [submob.get_center() for submob in labelled_svg.submobjects]
        )
        _, indices = linear_sum_assignment(distance_matrix)
        labelled_svg.set_submobjects([
            labelled_svg.submobjects[index]
            for index in indices
        ])

    # Toolkits

    def find_spans_by_selector(self, selector: Selector) -> list[Span]:
        def find_spans_by_single_selector(sel):
            if isinstance(sel, str):
                return [
                    match_obj.span()
                    for match_obj in re.finditer(re.escape(sel), self.string)
                ]
            if isinstance(sel, re.Pattern):
                return [
                    match_obj.span()
                    for match_obj in sel.finditer(self.string)
                ]
            if isinstance(sel, tuple) and len(sel) == 2 and all(
                isinstance(index, int) or index is None
                for index in sel
            ):
                l = self.full_len
                span = tuple(
                    default_index if index is None else
                    min(index, l) if index >= 0 else max(index + l, 0)
                    for index, default_index in zip(sel, (0, l))
                )
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
        return list(filter(lambda span: span[0] < span[1], result))

    def get_substr(self, span: Span) -> str:
        return self.string[slice(*span)]

    @staticmethod
    def get_neighbouring_pairs(vals: Iterable[T]) -> list[tuple[T, T]]:
        val_list = list(vals)
        return list(zip(val_list[:-1], val_list[1:]))

    @staticmethod
    def join_strs(strs, inserted_strs):
        return "".join(it.chain(*zip(strs, (*inserted_strs, ""))))

    @staticmethod
    def span_contains(span_0: Span, span_1: Span) -> bool:
        return span_0[0] <= span_1[0] and span_0[1] >= span_1[1]

    @staticmethod
    def get_complement_spans(
        universal_span: Span, interval_spans: list[Span]
    ) -> list[Span]:
        if not interval_spans:
            return [universal_span]

        span_ends, span_starts = zip(*interval_spans)
        return list(zip(
            (universal_span[0], *span_starts),
            (*span_ends, universal_span[1])
        ))

    @staticmethod
    def color_to_hex(color: ManimColor) -> str:
        return rgb_to_hex(color_to_rgb(color))

    @staticmethod
    def hex_to_int(rgb_hex: str) -> int:
        return int(rgb_hex[1:], 16)

    @staticmethod
    def int_to_hex(rgb_int: int) -> str:
        return f"#{rgb_int:06x}".upper()

    # Parsing

    def parse(self) -> None:
        command_matches = list(re.finditer(
            self.get_command_pattern(), self.string, re.X | re.S
        ))
        command_flags = [
            self.get_command_flag(command_match)
            for command_match in command_matches
        ]
        command_match_pairs = self.get_command_match_pairs(
            command_matches, command_flags
        )
        all_specified_items = [
            *self.get_internal_specified_items(command_match_pairs),
            *self.get_external_specified_items(),
            *[
                (span, {})
                for span in self.find_spans_by_selector(self.isolate)
            ]
        ]
        command_spans = [match_obj.span() for match_obj in command_matches]
        region_spans = self.get_complement_spans(
            (0, self.full_len), command_spans
        )

        def get_region_index(index):
            for region_index, (start, end) in enumerate(region_spans):
                if start <= index <= end:
                    return region_index
            return -1

        labelled_spans = []
        attr_dicts = []
        for span, attr_dict in all_specified_items:
            region_range = tuple(get_region_index(index) for index in span)
            if -1 in region_range:
                continue
            levels = list(it.accumulate(command_flags[slice(*region_range)]))
            if levels and any([
                *(level < 0 for level in levels), levels[-1] > 0
            ]):
                log.warning(
                    "Cannot handle substring '%s', ignored",
                    self.get_substr(span)
                )
                continue
            overlapped_spans = [
                s for s in labelled_spans if any([
                    s[0] < span[0] < s[1] < span[1],
                    span[0] < s[0] < span[1] < s[1]
                ])
            ]
            if overlapped_spans:
                log.warning(
                    "Substring '%s' partly overlaps with '%s', ignored",
                    self.get_substr(span),
                    self.get_substr(overlapped_spans[0])
                )
                continue
            labelled_spans.append(span)
            attr_dicts.append(attr_dict)

        insertion_items = [
            label_flag_pair
            for _, label_flag_pair in sorted(it.chain(*(
                sorted([
                    (span[::flag], (label, flag))
                    for label, span in list(enumerate(labelled_spans))[::flag]
                ], key=lambda t: (t[0][0], -t[0][1]))
                for flag in (-1, 1)
            )), key=lambda t: t[0][0])
        ]
        insertion_interval_items = [
            tuple(zip(*pair))
            for pair in self.get_neighbouring_pairs([
                (index, get_region_index(index))
                for index in [0, *(
                    labelled_spans[label][flag < 0]
                    for label, flag in insertion_items
                ), self.full_len]
            ])
        ]

        def get_replaced_pieces(replace_func):
            return [
                self.join_strs([
                    self.get_substr(s)
                    for s in self.get_complement_spans(
                        span, command_spans[slice(*region_range)]
                    )
                ], [
                    replace_func(command_match)
                    for command_match in command_matches[slice(*region_range)]
                ])
                for span, region_range in insertion_interval_items
            ]

        self.labelled_spans = labelled_spans
        self.attr_dicts = attr_dicts
        self.insertion_items = insertion_items
        self.content_pieces = get_replaced_pieces(self.replace_for_content)
        self.matching_pieces = get_replaced_pieces(self.replace_for_matching)

    @staticmethod
    @abstractmethod
    def get_command_pattern() -> str:
        return r"(?!)"

    @staticmethod
    @abstractmethod
    def get_command_flag(match_obj: re.Match) -> int:
        return 0

    @staticmethod
    @abstractmethod
    def replace_for_content(match_obj: re.Match) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def replace_for_matching(match_obj: re.Match) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_internal_specified_items(
        command_match_pairs: list[tuple[re.Match, re.Match]]
    ) -> list[tuple[Span, dict[str, str]]]:
        return []

    @abstractmethod
    def get_external_specified_items(self) -> list[tuple[Span, dict[str, str]]]:
        return []

    @staticmethod
    @abstractmethod
    def get_command_string(
        attr_dict: dict[str, str], is_end: bool, label_hex: str | None
    ) -> str:
        return ""

    @abstractmethod
    def get_content_prefix_and_suffix(
        self, is_labelled: bool
    ) -> tuple[str, str]:
        return "", ""

    @staticmethod
    def get_command_match_pairs(
        command_matches: list[re.Match], command_flags: list[int]
    ) -> list[tuple[re.Match, re.Match]]:
        result = []
        start_cmd_matches_stack = []
        for cmd_match, command_flag in zip(command_matches, command_flags):
            if command_flag == 1:
                start_cmd_matches_stack.append(cmd_match)
            elif command_flag == -1:
                if not start_cmd_matches_stack:
                    raise ValueError("Missing open command")
                start_cmd_match = start_cmd_matches_stack.pop()
                result.append(
                    (start_cmd_match, cmd_match)
                )
        if start_cmd_matches_stack:
            raise ValueError("Missing close command")
        return result

    def get_content(self, is_labelled: bool) -> str:
        insertion_strings = [
            self.get_command_string(
                self.attr_dicts[label],
                is_end=flag < 0,
                label_hex=self.int_to_hex(label + 1) if is_labelled else None
            )
            for label, flag in self.insertion_items
        ]
        prefix, suffix = self.get_content_prefix_and_suffix(
            is_labelled=is_labelled
        )
        return "".join([
            prefix,
            self.join_strs(self.content_pieces, insertion_strings),
            suffix
        ])

    def get_group_substrs(self, group_labels: list[int]) -> list[str]:
        if not group_labels:
            return []

        insertion_items = self.insertion_items

        def get_index(label, flag):
            if label == -1:
                return 0 if flag == 1 else len(insertion_items) + 1
            return insertion_items.index((label, flag)) + 1

        def get_labelled_span(label):
            if label == -1:
                return (0, self.full_len)
            return self.labelled_spans[label]

        def label_contains(label_0, label_1):
            return self.span_contains(
                get_labelled_span(label_0), get_labelled_span(label_1)
            )

        piece_ranges = self.get_complement_spans(
            (get_index(group_labels[0], 1), get_index(group_labels[-1], -1)),
            [
                (
                    get_index(next_label, 1)
                    if label_contains(prev_label, next_label)
                    else get_index(prev_label, -1),
                    get_index(prev_label, -1)
                    if label_contains(next_label, prev_label)
                    else get_index(next_label, 1)
                )
                for prev_label, next_label in self.get_neighbouring_pairs(
                    group_labels
                )
            ]
        )
        return [
            re.sub(r"\s+", "", "".join(
                self.matching_pieces[slice(*piece_range)]
            ))
            for piece_range in piece_ranges
        ]

    # Selector

    def get_submob_indices_list_by_span(
        self, arbitrary_span: Span
    ) -> list[int]:
        return [
            submob_index
            for submob_index, label in enumerate(self.labels)
            if label != -1 and self.span_contains(
                arbitrary_span, self.labelled_spans[label]
            )
        ]

    def get_specified_part_items(self) -> list[tuple[str, list[int]]]:
        return [
            (
                self.get_substr(span),
                self.get_submob_indices_list_by_span(span)
            )
            for span in self.labelled_spans
        ]

    def get_group_part_items(self) -> list[tuple[str, list[int]]]:
        if not self.labels:
            return []

        range_lens, group_labels = zip(*(
            (len(list(grouper)), val)
            for val, grouper in it.groupby(self.labels)
        ))
        submob_indices_lists = [
            list(range(*submob_range))
            for submob_range in self.get_neighbouring_pairs(
                [0, *it.accumulate(range_lens)]
            )
        ]
        group_substrs = self.get_group_substrs(list(group_labels))
        return list(zip(group_substrs, submob_indices_lists))

    def get_submob_indices_lists_by_selector(
        self, selector: Selector
    ) -> list[list[int]]:
        return list(filter(
            lambda indices_list: indices_list,
            [
                self.get_submob_indices_list_by_span(span)
                for span in self.find_spans_by_selector(selector)
            ]
        ))

    def build_parts_from_indices_lists(
        self, indices_lists: list[list[int]]
    ) -> VGroup:
        return VGroup(*[
            VGroup(*[
                self.submobjects[submob_index]
                for submob_index in indices_list
            ])
            for indices_list in indices_lists
        ])

    def build_groups(self) -> VGroup:
        return self.build_parts_from_indices_lists([
            indices_list
            for _, indices_list in self.get_group_part_items()
        ])

    def select_parts(self, selector: Selector) -> VGroup:
        return self.build_parts_from_indices_lists(
            self.get_submob_indices_lists_by_selector(selector)
        )

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
