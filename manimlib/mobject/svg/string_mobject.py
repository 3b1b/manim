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
    Note, substrings specified cannot *partially* overlap with each other.

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

        self.full_span = (0, len(self.string))
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

    def get_substr(self, span: Span) -> str:
        return self.string[slice(*span)]

    def find_spans(self, pattern: str | re.Pattern) -> list[Span]:
        return [
            match_obj.span()
            for match_obj in re.finditer(pattern, self.string)
        ]

    def find_spans_by_selector(self, selector: Selector) -> list[Span]:
        def find_spans_by_single_selector(sel):
            if isinstance(sel, str):
                return self.find_spans(re.escape(sel))
            if isinstance(sel, re.Pattern):
                return self.find_spans(sel)
            if isinstance(sel, tuple) and len(sel) == 2 and all(
                isinstance(index, int) or index is None
                for index in sel
            ):
                l = self.full_span[1]
                span = tuple(
                    min(index, l) if index >= 0 else max(index + l, 0)
                    if index is not None else default_index
                    for index, default_index in zip(sel, self.full_span)
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
        return result

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
        val_ranges = StringMobject.get_neighbouring_pairs(indices)
        return list(zip(unique_vals, val_ranges))

    @staticmethod
    def span_contains(span_0: Span, span_1: Span) -> bool:
        return span_0[0] <= span_1[0] and span_0[1] >= span_1[1]

    @staticmethod
    def get_complement_spans(
        universal_span: Span, interval_spans: list[Span]
    ) -> list[Span]:
        if not interval_spans:
            return [universal_span]

        span_ends, span_begins = zip(*interval_spans)
        return list(zip(
            (universal_span[0], *span_begins),
            (*span_ends, universal_span[1])
        ))

    def replace_substr(self, span: Span, repl_items: list[Span, str]):
        if not repl_items:
            return self.get_substr(span)

        repl_spans, repl_strs = zip(*sorted(repl_items, key=lambda t: t[0]))
        pieces = [
            self.get_substr(piece_span)
            for piece_span in self.get_complement_spans(span, repl_spans)
        ]
        repl_strs = [*repl_strs, ""]
        return "".join(it.chain(*zip(pieces, repl_strs)))

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
        cmd_spans = self.get_cmd_spans()
        cmd_substrs = [self.get_substr(span) for span in cmd_spans]
        flags = [self.get_substr_flag(substr) for substr in cmd_substrs]
        specified_items = self.get_specified_items(
            self.get_cmd_span_pairs(cmd_spans, flags)
        )
        split_items = [
            (span, attr_dict)
            for specified_span, attr_dict in specified_items
            for span in self.split_span_by_levels(
                specified_span, cmd_spans, flags
            )
        ]

        self.specified_spans = [span for span, _ in specified_items]
        self.split_items = split_items
        self.labelled_spans = [span for span, _ in split_items]
        self.cmd_repl_items_for_content = [
            (span, self.get_repl_substr_for_content(substr))
            for span, substr in zip(cmd_spans, cmd_substrs)
        ]
        self.cmd_repl_items_for_matching = [
            (span, self.get_repl_substr_for_matching(substr))
            for span, substr in zip(cmd_spans, cmd_substrs)
        ]
        self.check_overlapping()

    @abstractmethod
    def get_cmd_spans(self) -> list[Span]:
        return []

    @abstractmethod
    def get_substr_flag(self, substr: str) -> int:
        return 0

    @abstractmethod
    def get_repl_substr_for_content(self, substr: str) -> str:
        return ""

    @abstractmethod
    def get_repl_substr_for_matching(self, substr: str) -> str:
        return ""

    @staticmethod
    def get_cmd_span_pairs(
        cmd_spans: list[Span], flags: list[int]
    ) -> list[tuple[Span, Span]]:
        result = []
        begin_cmd_spans_stack = []
        for cmd_span, flag in zip(cmd_spans, flags):
            if flag == 1:
                begin_cmd_spans_stack.append(cmd_span)
            elif flag == -1:
                if not begin_cmd_spans_stack:
                    raise ValueError("Missing open command")
                begin_cmd_span = begin_cmd_spans_stack.pop()
                result.append((begin_cmd_span, cmd_span))
        if begin_cmd_spans_stack:
            raise ValueError("Missing close command")
        return result

    @abstractmethod
    def get_specified_items(
        self, cmd_span_pairs: list[tuple[Span, Span]]
    ) -> list[tuple[Span, dict[str, str]]]:
        return []

    def split_span_by_levels(
        self, arbitrary_span: Span, cmd_spans: list[Span], flags: list[int]
    ) -> list[Span]:
        cmd_range = (
            sum([
                arbitrary_span[0] > interval_begin
                for interval_begin, _ in cmd_spans
            ]),
            sum([
                arbitrary_span[1] >= interval_end
                for _, interval_end in cmd_spans
            ])
        )
        complement_spans = self.get_complement_spans(
            self.full_span, cmd_spans
        )
        adjusted_span = (
            max(arbitrary_span[0], complement_spans[cmd_range[0]][0]),
            min(arbitrary_span[1], complement_spans[cmd_range[1]][1])
        )
        if adjusted_span[0] > adjusted_span[1]:
            return []

        upward_cmd_spans = []
        downward_cmd_spans = []
        for cmd_span, flag in list(zip(cmd_spans, flags))[slice(*cmd_range)]:
            if flag == 1:
                upward_cmd_spans.append(cmd_span)
            elif flag == -1:
                if upward_cmd_spans:
                    upward_cmd_spans.pop()
                else:
                    downward_cmd_spans.append(cmd_span)
        return list(filter(
            lambda span: self.get_substr(span).strip(),
            self.get_complement_spans(
                adjusted_span, downward_cmd_spans + upward_cmd_spans
            )
        ))

    def check_overlapping(self) -> None:
        labelled_spans = self.labelled_spans
        if len(labelled_spans) >= 16777216:
            raise ValueError("Cannot handle that many substrings")
        for span_0, span_1 in it.product(labelled_spans, repeat=2):
            if not span_0[0] < span_1[0] < span_0[1] < span_1[1]:
                continue
            raise ValueError(
                "Partially overlapping substrings detected: "
                f"'{self.get_substr(span_0)}' and '{self.get_substr(span_1)}'"
            )

    @staticmethod
    @abstractmethod
    def get_cmd_str_pair(
        attr_dict: dict[str, str], label_hex: str | None
    ) -> tuple[str, str]:
        return "", ""

    @abstractmethod
    def get_content_prefix_and_suffix(
        self, is_labelled: bool
    ) -> tuple[str, str]:
        return "", ""

    def get_content(self, is_labelled: bool) -> str:
        inserted_str_pairs = [
            (span, self.get_cmd_str_pair(
                attr_dict,
                label_hex=self.int_to_hex(label + 1) if is_labelled else None
            ))
            for label, (span, attr_dict) in enumerate(self.split_items)
        ]
        inserted_str_items = sorted([
            (index, s)
            for (index, _), s in [
                *sorted([
                    (span[::-1], end_str)
                    for span, (_, end_str) in reversed(inserted_str_pairs)
                ], key=lambda t: (t[0][0], -t[0][1])),
                *sorted([
                    (span, begin_str)
                    for span, (begin_str, _) in inserted_str_pairs
                ], key=lambda t: (t[0][0], -t[0][1]))
            ]
        ], key=lambda t: t[0])
        repl_items = self.cmd_repl_items_for_content + [
            ((index, index), inserted_str)
            for index, inserted_str in inserted_str_items
        ]
        prefix, suffix = self.get_content_prefix_and_suffix(is_labelled)
        return "".join([
            prefix,
            self.replace_substr(self.full_span, repl_items),
            suffix
        ])

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
            for span in self.specified_spans
        ]

    def get_group_part_items(self) -> list[tuple[str, list[int]]]:
        if not self.labels:
            return []

        group_labels, labelled_submob_ranges = zip(
            *self.compress_neighbours(self.labels)
        )
        ordered_spans = [
            self.labelled_spans[label] if label != -1 else self.full_span
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
            re.sub(r"\s+", "", self.replace_substr(
                span, [
                    (cmd_span, repl_str)
                    for cmd_span, repl_str in self.cmd_repl_items_for_matching
                    if self.span_contains(span, cmd_span)
                ]
            ))
            for span in self.get_complement_spans(
                (ordered_spans[0][0], ordered_spans[-1][1]), interval_spans
            )
        ]
        submob_indices_lists = [
            list(range(*submob_range))
            for submob_range in labelled_submob_ranges
        ]
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
