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
        self.base_color_hex = self.color_to_hex(self.base_color)

        self.full_span = (0, len(self.string))
        self.parse()
        super().__init__(**kwargs)
        self.labelled_submobject_items = [
            (submob.label, submob)
            for submob in self.submobjects
        ]

    def get_file_path(self) -> str:
        return self.get_file_path_by_content(self.original_content)

    @abstractmethod
    def get_file_path_by_content(self, content: str) -> str:
        return ""

    def generate_mobject(self) -> None:
        super().generate_mobject()

        file_path = self.get_file_path_by_content(self.labelled_content)
        labelled_svg = SVGMobject(file_path)
        num_submobjects = len(self.submobjects)
        if num_submobjects != len(labelled_svg.submobjects):
            raise ValueError(
                "Cannot align submobjects of the labelled svg "
                "to the original svg"
            )

        submob_color_ints = [
            self.hex_to_int(self.color_to_hex(submob.get_fill_color()))
            for submob in labelled_svg.submobjects
        ]
        unrecognized_color_ints = self.remove_redundancies(sorted(filter(
            lambda color_int: color_int > len(self.label_span_list),
            submob_color_ints
        )))
        if unrecognized_color_ints:
            raise ValueError(
                "Unrecognized color label(s) detected: "
                f"{', '.join(map(self.int_to_hex, unrecognized_color_ints))}"
            )

        #if self.sort_labelled_submobs:
        submob_indices = sorted(
            range(num_submobjects),
            key=lambda index: tuple(
                self.submobjects[index].get_center()
            )
        )
        labelled_submob_indices = sorted(
            range(num_submobjects),
            key=lambda index: tuple(
                labelled_svg.submobjects[index].get_center()
            )
        )
        submob_color_ints = [
            submob_color_ints[
                labelled_submob_indices[submob_indices.index(index)]
            ]
            for index in range(num_submobjects)
        ]

        for submob, color_int in zip(self.submobjects, submob_color_ints):
            submob.label = color_int - 1

    #@property
    #@abstractmethod
    #def sort_labelled_submobs(self) -> bool:
    #    return False

    # Toolkits

    def get_substr(self, span: Span) -> str:
        return self.string[slice(*span)]

    #def match(self, pattern: str | re.Pattern, **kwargs) -> re.Pattern | None:
    #    if isinstance(pattern, str):
    #        pattern = re.compile(pattern)
    #    return re.compile(pattern).match(self.string, **kwargs)

    def find_spans(self, pattern: str | re.Pattern, **kwargs) -> list[Span]:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return [
            match_obj.span()
            for match_obj in pattern.finditer(self.string, **kwargs)
        ]

    #def find_indices(self, pattern: str | re.Pattern, **kwargs) -> list[int]:
    #    return [index for index, _ in self.find_spans(pattern, **kwargs)]

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
    def sort_obj_pairs_by_spans(
        obj_pairs: list[tuple[Span, tuple[T, T]]]
    ) -> list[tuple[int, T]]:
        return [
            (index, obj)
            for (index, _), obj in sorted([
                (span, begin_obj)
                for span, (begin_obj, _) in obj_pairs
            ] + [
                (span[::-1], end_obj)
                for span, (_, end_obj) in reversed(obj_pairs)
            ], key=lambda t: (t[0][0], -t[0][1]))
        ]

    @staticmethod
    def span_contains(span_0: Span, span_1: Span) -> bool:
        return span_0[0] <= span_1[0] and span_0[1] >= span_1[1]

    def get_piece_items(
        self,
        tag_span_pairs: list[tuple[Span, Span]],
        entity_spans: list[Span]
    ) -> tuple[list[Span], list[int]]:
        tagged_items = sorted(self.chain(
            [(begin_cmd_span, 1) for begin_cmd_span, _ in tag_span_pairs],
            [(end_cmd_span, -1) for _, end_cmd_span in tag_span_pairs],
            [(entity_span, 0) for entity_span in entity_spans],
        ), key=lambda t: t[0])
        piece_spans = self.get_complement_spans(self.full_span, [
            interval_span for interval_span, _ in tagged_items
        ])
        piece_levels = [0, *it.accumulate([tag for _, tag in tagged_items])]
        return piece_spans, piece_levels

    def split_span(self, arbitrary_span: Span) -> list[Span]:
        # ignorable_indices --
        # left_bracket_spans
        # right_bracket_spans
        # entity_spans
        #piece_spans, piece_levels = zip(*self.piece_items)
        #ignorable_indices = self.ignorable_indices
        piece_spans = self.piece_spans
        piece_levels = self.piece_levels
        #piece_begins, piece_ends = zip(*piece_spans)
        #span_begin, span_end = arbitrary_span
        #while span_begin in ignorable_indices:
        #    span_begin += 1
        #while span_end - 1 in ignorable_indices:
        #    span_end -= 1
        #entity_spans = self.chain(
        #    left_bracket_spans, right_bracket_spans, entity_spans
        #)
        index_begin = sum([
            arbitrary_span[0] > piece_end
            for _, piece_end in piece_spans
        ])
        index_end = sum([
            arbitrary_span[1] >= piece_begin
            for piece_begin, _ in piece_spans
        ])
        if index_begin >= index_end:
            return []

        lowest_level = min(
            piece_levels[index_begin:index_end]
        )
        split_piece_indices = []
        target_level = piece_levels[index_begin]
        for piece_index in range(index_begin, index_end):
            if piece_levels[piece_index] != target_level:
                continue
            split_piece_indices.append(piece_index)
            target_level -= 1
            if target_level < lowest_level:
                break
        len_indices = len(split_piece_indices)
        target_level = piece_levels[index_end - 1]
        for piece_index in range(index_begin, index_end)[::-1]:
            if piece_levels[piece_index] != target_level:
                continue
            split_piece_indices.insert(len_indices, piece_index + 1)
            target_level -= 1
            if target_level < lowest_level:
                break

        span_begins = [
            piece_spans[piece_index][0]
            for piece_index in split_piece_indices[:-1]
        ]
        span_begins[0] = max(arbitrary_span[0], span_begins[0])
        span_ends = [
            piece_spans[piece_index - 1][1]
            for piece_index in split_piece_indices[1:]
        ]
        span_ends[-1] = min(arbitrary_span[1], span_ends[-1])
        return list(zip(span_begins, span_ends))
        #lowest_level_indices = [
        #    piece_index
        #    for piece_index, piece_level in enumerate(piece_levels)
        #    if left_piece_index <= piece_index <= right_piece_index
        #    and piece_level == lowest_level
        #]
        #left_lowest_index = min(lowest_level_indices)
        #right_lowest_index = max(lowest_level_indices)
        #while right_lowest_index != right_piece_index:


        #left_parallel_index = max(
        #    piece_index
        #    for piece_index, piece_level in enumerate(piece_levels)
        #    if left_piece_index <= piece_index <= right_piece_index
        #    and piece_level == piece_levels[left_piece_index]
        #)
        #right_parallel_index = min(
        #    piece_index
        #    for piece_index, piece_level in enumerate(piece_levels)
        #    if left_piece_index <= piece_index <= right_piece_index
        #    and piece_level == piece_levels[right_piece_index]
        #)
        #result.append((
        #    piece_spans[left_lowest_index][0],
        #    piece_spans[right_lowest_index][1]
        #))
        #lowest_piece_indices = [
        #    piece_index
        #    for piece_index, piece_level in enumerate(

        #    )
        #]
        #adjusted_span_begin = max(span_begin, piece_spans[begin_piece_index][0])  ##
        #adjusted_span_end = min(span_end, piece_spans[end_piece_index][1])  ##
        #begin_level_mismatch = piece_levels[begin_piece_index] - lowest_level
        #end_level_mismatch = piece_levels[end_piece_index] - lowest_level
        #if begin_level_mismatch:
        #    span_begin = piece_spans[max([
        #        index
        #        for index, piece_level in enumerate(piece_levels)
        #        if piece_level == lowest_level and index < begin_piece_index
        #    ])][1]
        #    begin_level_mismatch = 0
        #if end_level_mismatch:
        #    span_end = piece_spans[min([
        #        index
        #        for index, piece_level in enumerate(piece_levels)
        #        if piece_level == lowest_level and index > end_piece_index
        #    ])][0]
        #    end_level_mismatch = 0

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

    def get_replaced_substr(self, span: Span, repl_items: list[Span, str]):  # TODO: need `span` attr?
        if not repl_items:
            return self.get_substr(span)

        repl_spans, repl_strs = zip(*sorted(
            repl_items, key=lambda t: t[0]
        ))
        pieces = [
            self.get_substr(piece_span)
            for piece_span in self.get_complement_spans(span, repl_spans)
        ]
        repl_strs = [*repl_strs, ""]
        return "".join(self.chain(*zip(pieces, repl_strs)))

    #def get_replaced_string(
    #    self,
    #    inserted_string_pairs: list[tuple[Span, tuple[str, str]]],
    #    repl_items: list[tuple[Span, str]]
    #) -> str:
    #    all_repl_items = self.chain(
    #        repl_items,
    #        [
    #            ((index, index), inserted_string)
    #            for index, inserted_string
    #            in self.sort_inserted_strings_from_pairs(
    #                inserted_string_pairs
    #            )
    #        ]
    #    )
    #    return self.get_replaced_substr(self.full_span, all_repl_items)

    @staticmethod
    def color_to_hex(color: ManimColor) -> str:
        return rgb_to_hex(color_to_rgb(color))

    @staticmethod
    def hex_to_int(rgb_hex: str) -> int:
        return int(rgb_hex[1:], 16)

    @staticmethod
    def int_to_hex(rgb_int: int) -> str:
        return f"#{rgb_int:06x}".upper()

    @staticmethod
    @abstractmethod
    def get_tag_str(
        attr_dict: dict[str, str], escape_color_keys: bool, is_begin_tag: bool
    ) -> str:
        return ""

    #def get_color_tag_str(self, rgb_int: int, is_begin_tag: bool) -> str:
    #    return self.get_tag_str({
    #        "foreground": self.int_to_hex(rgb_int)
    #    }, escape_color_keys=False, is_begin_tag=is_begin_tag)

    # Parsing

    #@abstractmethod
    #def get_command_spans(self) -> list[Span]:
    #    return []
    #    #return [
    #    #    self.match(r"\\(?:[a-zA-Z]+|.)", pos=index).span()
    #    #    for index in self.backslash_indices
    #    #]

    #@abstractmethod
    #@staticmethod
    #def get_command_repl_dict() -> dict[str | re.Pattern, str]:
    #    return {}

    #@abstractmethod
    #def parse_setup(self) -> None:
    #    return

    #@abstractmethod
    #def get_command_repl_items(self) -> list[tuple[Span, str]]:
    #    return []
    #    #result = []
    #    #for cmd_span in self.command_spans:
    #    #    cmd_str = self.get_substr(cmd_span)
    #    #    if 
    #    #    repl_str = self.command_repl_dict.get(cmd_str, cmd_str)
    #    #    result.append((cmd_span, repl_str))
    #    #return result

    #def span_cuts_at_entity(self, span: Span) -> bool:
    #    return any([
    #        entity_begin < index < entity_end
    #        for index in span
    #        for entity_begin, entity_end in self.command_repl_items
    #    ])

    #@abstractmethod
    #def get_all_specified_items(self) -> list[tuple[Span, dict[str, str]]]:
    #    return []

    #def get_specified_items(self) -> list[tuple[Span, dict[str, str]]]:
    #    return [
    #        (span, attr_dict)
    #        for span, attr_dict in self.get_all_specified_items()
    #        if not any([
    #            entity_begin < index < entity_end
    #            for index in span
    #            for entity_begin, entity_end in self.command_repl_items
    #        ])
    #    ]

    #def get_specified_spans(self) -> list[Span]:
    #    return [span for span, _ in self.specified_items]

    def parse(self) -> None:
        self.entity_spans = self.get_entity_spans()
        tag_span_pairs, internal_items = self.get_internal_items()
        self.piece_spans, self.piece_levels = self.get_piece_items(
            tag_span_pairs, self.entity_spans
        )
        #self.tag_content_spans = [
        #    (content_begin, content_end)
        #    for (_, content_begin), (content_end, _) in tag_span_pairs
        #]
        self.tag_spans = self.chain(*tag_span_pairs)
        specified_items = self.chain(
            internal_items,
            self.get_external_items(),
            [
                (span, {})
                for span in self.find_spans_by_selector(self.isolate)
            ]
        )
        print(f"\n{specified_items=}\n")
        specified_spans = [span for span, _ in specified_items]
        for span_0, span_1 in it.product(specified_spans, repeat=2):
            if not span_0[0] < span_1[0] < span_0[1] < span_1[1]:
                continue
            raise ValueError(
                "Partially overlapping substrings detected: "
                f"'{self.get_substr(span_0)}' and '{self.get_substr(span_1)}'"
            )

        split_items = [
            (span, attr_dict)
            for specified_span, attr_dict in specified_items
            for span in self.split_span(specified_span)
        ]
        print(f"\n{split_items=}\n")
        split_spans = [span for span, _ in split_items]
        label_span_list = self.get_label_span_list(split_spans)
        if len(label_span_list) >= 16777216:
            raise ValueError("Cannot handle that many substrings")

        #content_strings = []
        #for is_labelled in (False, True):
        #    
        #    content_strings.append(content_string)

        #inserted_str_pairs = self.chain(
        #    [
        #        (span, (
        #            self.get_tag_str(attr_dict, escape_color_keys=True, is_begin_tag=True),
        #            self.get_tag_str(attr_dict, escape_color_keys=True, is_begin_tag=False)
        #        ))
        #        for span, attr_dict in split_items
        #    ],
        #    [
        #        (span, (
        #            self.get_color_tag_str(label + 1, is_begin_tag=True),
        #            self.get_color_tag_str(label + 1, is_begin_tag=False)
        #        ))
        #        for span, attr_dict in split_items
        #    ]
        #)


        #decorated_strings = [
        #    self.get_replaced_substr(self.full_span, [
        #        (span, str_pair[flag])
        #        for span, str_pair in command_repl_items
        #    ])
        #    for flag in range(2)
        #]

        self.specified_spans = specified_spans
        self.label_span_list = label_span_list
        self.original_content = self.get_full_content_string(
            label_span_list, split_items, is_labelled=False
        )
        self.labelled_content = self.get_full_content_string(
            label_span_list, split_items, is_labelled=True
        )
        print(self.original_content)
        print()
        print(self.labelled_content)


        #self.command_repl_dict = self.get_command_repl_dict()
        #self.command_repl_items = []
        #self.bracket_content_spans = []
        ##self.command_spans = self.get_command_spans()
        ##self.specified_items = self.get_specified_items()
        #self.specified_spans = []
        #self.check_overlapping()  #######
        #self.label_span_list = []
        #if len(self.label_span_list) >= 16777216:
        #    raise ValueError("Cannot handle that many substrings")

    @abstractmethod
    def get_entity_spans(self) -> list[Span]:
        return []

    @abstractmethod
    def get_internal_items(
        self
    ) -> tuple[list[tuple[Span, Span]], list[tuple[Span, dict[str, str]]]]:
        return [], []

    @abstractmethod
    def get_external_items(self) -> list[tuple[Span, dict[str, str]]]:
        return []

    #@abstractmethod
    #def get_spans_from_items(self, specified_items: list[tuple[Span, dict[str, str]]]) -> list[Span]:
    #    return []

    #def split_span(self, arbitrary_span: Span) -> list[Span]:
    #    span_begin, span_end = arbitrary_span
    #    # TODO: improve algorithm
    #    span_begin += sum([
    #        entity_end - span_begin
    #        for entity_begin, entity_end in self.entity_spans
    #        if entity_begin < span_begin < entity_end
    #    ])
    #    span_end -= sum([
    #        span_end - entity_begin
    #        for entity_begin, entity_end in self.entity_spans
    #        if entity_begin < span_end < entity_end
    #    ])
    #    if span_begin >= span_end:
    #        return []

    #    adjusted_span = (span_begin, span_end)
    #    result = []
    #    span_choices = list(filter(
    #        lambda span: span[0] < span[1] and self.span_contains(
    #            adjusted_span, span
    #        ),
    #        self.tag_content_spans
    #    ))
    #    while span_choices:
    #        chosen_span = min(span_choices, key=lambda t: (t[0], -t[1]))
    #        result.append(chosen_span)
    #        span_choices = list(filter(
    #            lambda span: chosen_span[1] <= span[0],
    #            span_choices
    #        ))
    #    result.extend(self.chain(*[
    #        self.get_complement_spans(span, sorted([
    #            (max(tag_span[0], span[0]), min(tag_span[1], span[1]))
    #            for tag_span in self.tag_spans
    #            if tag_span[0] < span[1] and span[0] < tag_span[1]
    #        ]))
    #        for span in self.get_complement_spans(adjusted_span, result)
    #    ]))
        return list(filter(lambda span: span[0] < span[1], result))

    #@abstractmethod
    #def get_split_items(self, specified_items: list[T]) -> list[T]:
    #    return []

    @abstractmethod
    def get_label_span_list(self, split_spans: list[Span]) -> list[Span]:
        return []

    #@abstractmethod
    #def get_predefined_inserted_str_items(
    #    self, split_items: list[T]
    #) -> list[tuple[Span, tuple[str, str]]]:
    #    return []

    #def check_overlapping(self) -> None:
        
        #for span_0, span_1 in it.product(self.specified_spans, self.bracket_content_spans):
        #    if not any(
        #        span_0[0] < span_1[0] <= span_0[1] <= span_1[1],
        #        span_1[0] <= span_0[0] <= span_1[1] < span_0[1]
        #    ):
        #        continue
        #    raise ValueError(
        #        f"Invalid substring detected: '{self.get_substr(span_0)}'"
        #    )
        # TODO: test bracket_content_spans

    #@abstractmethod
    #def get_inserted_string_pairs(
    #    self, is_labelled: bool
    #) -> list[tuple[Span, tuple[str, str]]]:
    #    return []

    #@abstractmethod
    #def get_label_span_list(self) -> list[Span]:
    #    return []

    #def get_decorated_string(
    #    self, is_labelled: bool, replace_commands: bool
    #) -> str:
    #    inserted_string_pairs = [
    #        (indices, str_pair)
    #        for indices, str_pair in self.get_inserted_string_pairs(
    #            is_labelled=is_labelled
    #        )
    #        if not any(
    #            cmd_begin < index < cmd_end
    #            for index in indices
    #            for (cmd_begin, cmd_end), _ in self.command_repl_items
    #        )
    #    ]
    #    repl_items = [
    #        ((index, index), inserted_string)
    #        for index, inserted_string
    #        in self.sort_inserted_strings_from_pairs(
    #            inserted_string_pairs
    #        )
    #    ]
    #    if replace_commands:
    #        repl_items.extend(self.command_repl_items)
    #    return self.get_replaced_substr(self.full_span, repl_items)

    @abstractmethod
    def get_additional_inserted_str_pairs(
        self
    ) -> list[tuple[Span, tuple[str, str]]]:
        return []

    @abstractmethod
    def get_command_repl_items(self, is_labelled: bool) -> list[Span, str]:
        return []

    def get_full_content_string(
        self,
        label_span_list: list[Span],
        split_items: list[tuple[Span, dict[str, str]]],
        is_labelled: bool
    ) -> str:
        label_items = [
            (span, {
                "foreground": self.int_to_hex(label + 1)
            } if is_labelled else {})
            for label, span in enumerate(label_span_list)
        ]
        inserted_str_pairs = self.chain(
            self.get_additional_inserted_str_pairs(),
            [
                (span, tuple(
                    self.get_tag_str(
                        attr_dict,
                        escape_color_keys=is_labelled and not is_label_item,
                        is_begin_tag=is_begin_tag
                    )
                    for is_begin_tag in (True, False)
                ))
                for is_label_item, items in enumerate((
                    split_items, label_items
                ))
                for span, attr_dict in items
            ]
        )
        repl_items = self.chain(
            self.get_command_repl_items(is_labelled),
            [
                ((index, index), inserted_str)
                for index, inserted_str
                in self.sort_obj_pairs_by_spans(inserted_str_pairs)
            ]
        )
        return self.get_replaced_substr(
            self.full_span, repl_items
        )

    #def get_content(self, is_labelled: bool) -> str:
    #    return self.content_strings[int(is_labelled)]

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
                (ordered_spans[0][0], ordered_spans[-1][1]), interval_spans
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

    def select_part_by_span(self, arbitrary_span: Span) -> VGroup:
        return VGroup(*[
            submob for label, submob in self.labelled_submobject_items
            if label != -1
            and self.span_contains(arbitrary_span, self.label_span_list[label])
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
