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
from manimlib.utils.iterables import remove_list_redundancies


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.types.vectorized_mobject import VMobject
    ManimColor = Union[str, colour.Color, Sequence[float]]
    Span = tuple[int, int]


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
        "base_color": None,
        "use_plain_file": False,
        "isolate": [],
    }

    def __init__(self, string: str, **kwargs):
        self.string = string
        reserved_svg_default = kwargs.pop("svg_default", {})
        digest_config(self, kwargs)
        self.reserved_svg_default = reserved_svg_default
        self.base_color = self.base_color \
            or reserved_svg_default.get("color", None) \
            or reserved_svg_default.get("fill_color", None) \
            or WHITE

        self.pre_parse()
        self.parse()
        super().__init__(**kwargs)

    def get_file_path(self) -> str:
        return self.get_file_path_(use_plain_file=False)

    def get_file_path_(self, use_plain_file: bool) -> str:
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
        if any([
            self.use_plain_file,
            self.reserved_svg_default,
            self.has_predefined_colors
        ]):
            file_path = self.get_file_path_(use_plain_file=True)
            plain_svg = _StringSVG(
                file_path,
                svg_default=self.reserved_svg_default,
                path_string_config=self.path_string_config
            )
            self.set_submobjects(plain_svg.submobjects)
        else:
            self.set_fill(self.base_color)
        for submob, label in zip(self.submobjects, submob_labels):
            submob.label = label

    def pre_parse(self) -> None:
        self.string_len = len(self.string)
        self.full_span = (0, self.string_len)

    def parse(self) -> None:
        self.command_repl_items = self.get_command_repl_items()
        self.command_spans = self.get_command_spans()
        self.ignored_spans = self.get_ignored_spans()
        self.skipped_spans = self.get_skipped_spans()
        self.internal_specified_spans = self.get_internal_specified_spans()
        self.external_specified_spans = self.get_external_specified_spans()
        self.specified_spans = self.get_specified_spans()
        self.label_span_list = self.get_label_span_list()
        self.check_overlapping()

    # Toolkits

    def get_substr(self, span: Span) -> str:
        return self.string[slice(*span)]

    def finditer(
        self, pattern: str, flags: int = 0, **kwargs
    ) -> Iterable[re.Match]:
        return re.compile(pattern, flags).finditer(self.string, **kwargs)

    def search(self, pattern: str, flags: int = 0, **kwargs) -> re.Match:
        return re.compile(pattern, flags).search(self.string, **kwargs)

    def match(self, pattern: str, flags: int = 0, **kwargs) -> re.Match:
        return re.compile(pattern, flags).match(self.string, **kwargs)

    def find_spans(self, pattern: str, **kwargs) -> list[Span]:
        return [
            match_obj.span()
            for match_obj in self.finditer(pattern, **kwargs)
        ]

    def find_substr(self, substr: str, **kwargs) -> list[Span]:
        if not substr:
            return []
        return self.find_spans(re.escape(substr), **kwargs)

    def find_substrs(self, substrs: list[str], **kwargs) -> list[Span]:
        return list(it.chain(*[
            self.find_substr(substr, **kwargs)
            for substr in remove_list_redundancies(substrs)
        ]))

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
    def get_span_replacement_dict(
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

    # Parsing

    @abstractmethod
    def get_command_repl_items(self) -> list[tuple[Span, str]]:
        return []

    def get_command_spans(self) -> list[Span]:
        return [cmd_span for cmd_span, _ in self.command_repl_items]

    def get_ignored_spans(self) -> list[int]:
        return []

    def get_skipped_spans(self) -> list[Span]:
        return list(it.chain(
            self.find_spans(r"\s"),
            self.command_spans,
            self.ignored_spans
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
        spans = [
            self.full_span,
            *self.internal_specified_spans,
            *self.external_specified_spans,
            *self.find_substrs(self.isolate)
        ]
        shrinked_spans = list(filter(
            lambda span: span[0] < span[1],
            [self.shrink_span(span) for span in spans]
        ))
        return remove_list_redundancies(shrinked_spans)

    @abstractmethod
    def get_label_span_list(self) -> list[Span]:
        return []

    def check_overlapping(self) -> None:
        for span_0, span_1 in it.product(self.label_span_list, repeat=2):
            if not span_0[0] < span_1[0] < span_0[1] < span_1[1]:
                continue
            raise ValueError(
                "Partially overlapping substrings detected: "
                f"'{self.get_substr(span_0)}' and '{self.get_substr(span_1)}'"
            )

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
        result = self.get_replaced_substr(self.full_span, span_repl_dict)

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
    def has_predefined_colors(self) -> bool:
        return False

    # Post-parsing

    def get_cleaned_substr(self, span: Span) -> str:
        span_repl_dict = dict.fromkeys(self.command_spans, "")
        return self.get_replaced_substr(span, span_repl_dict)

    def get_specified_substrs(self) -> list[str]:
        return remove_list_redundancies([
            self.get_cleaned_substr(span)
            for span in self.specified_spans
        ])

    def get_group_span_items(self) -> tuple[list[int], list[Span]]:
        submob_labels = [submob.label for submob in self.submobjects]
        if not submob_labels:
            return [], []
        return tuple(zip(*self.compress_neighbours(submob_labels)))

    def get_group_substrs(self) -> list[str]:
        group_labels, _ = self.get_group_span_items()
        if not group_labels:
            return []

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
        return [
            self.get_cleaned_substr(span) if span[0] < span[1] else ""
            for span in shrinked_spans
        ]

    def get_submob_groups(self) -> VGroup:
        _, submob_spans = self.get_group_span_items()
        return VGroup(*[
            VGroup(*self.submobjects[slice(*submob_span)])
            for submob_span in submob_spans
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

    def get_parts_by_custom_span(self, custom_span: Span, **kwargs) -> VGroup:
        labels = [
            label for label, span in enumerate(self.label_span_list)
            if any([
                self.span_contains(span_component, span)
                for span_component in self.find_span_components(
                    custom_span, **kwargs
                )
            ])
        ]
        return VGroup(*filter(
            lambda submob: submob.label in labels,
            self.submobjects
        ))

    def get_parts_by_string(
        self, substr: str, case_sensitive: bool = True, **kwargs
    ) -> VGroup:
        flags = 0
        if not case_sensitive:
            flags |= re.I
        return VGroup(*[
            self.get_parts_by_custom_span(span, **kwargs)
            for span in self.find_substr(substr, flags=flags)
        ])

    def get_parts_by_group_substr(self, substr: str) -> VGroup:
        return VGroup(*[
            group
            for group, group_substr in zip(
                self.get_submob_groups(), self.get_group_substrs()
            )
            if group_substr == substr
        ])

    def get_part_by_string(
        self, substr: str, index: int = 0, **kwargs
    ) -> VMobject:
        return self.get_parts_by_string(substr, **kwargs)[index]

    def set_color_by_string(self, substr: str, color: ManimColor, **kwargs):
        self.get_parts_by_string(substr, **kwargs).set_color(color)
        return self

    def set_color_by_string_to_color_map(
        self, string_to_color_map: dict[str, ManimColor], **kwargs
    ):
        for substr, color in string_to_color_map.items():
            self.set_color_by_string(substr, color, **kwargs)
        return self

    def indices_of_part(self, part: Iterable[VMobject]) -> list[int]:
        return [self.submobjects.index(submob) for submob in part]

    def indices_lists_of_parts(
        self, parts: Iterable[Iterable[VMobject]]
    ) -> list[list[int]]:
        return [self.indices_of_part(part) for part in parts]

    def get_string(self) -> str:
        return self.string
