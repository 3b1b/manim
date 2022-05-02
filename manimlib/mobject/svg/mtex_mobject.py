from __future__ import annotations

from manimlib.mobject.svg.labelled_string import LabelledString
from manimlib.utils.tex_file_writing import display_during_execution
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import tex_to_svg_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from colour import Color
    import re
    from typing import Iterable, Union

    from manimlib.mobject.types.vectorized_mobject import VGroup

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


SCALE_FACTOR_PER_FONT_POINT = 0.001


TEX_COLOR_COMMANDS_DICT = {
    "\\color": (1, False),
    "\\textcolor": (1, False),
    "\\pagecolor": (1, True),
    "\\colorbox": (1, True),
    "\\fcolorbox": (2, True),
}
TEX_COLOR_COMMAND_SUFFIX = "replaced"


class MTex(LabelledString):
    CONFIG = {
        "font_size": 48,
        "alignment": "\\centering",
        "tex_environment": "align*",
        "tex_to_color_map": {},
    }

    def __init__(self, tex_string: str, **kwargs):
        # Prevent from passing an empty string.
        if not tex_string.strip():
            tex_string = "\\\\"
        self.tex_string = tex_string
        super().__init__(tex_string, **kwargs)

        #self.set_color_by_tex_to_color_map(self.tex_to_color_map)
        self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)

    @property
    def hash_seed(self) -> tuple:
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.base_color,
            self.isolate,
            self.tex_string,
            self.alignment,
            self.tex_environment,
            self.tex_to_color_map
        )

    def get_file_path_by_content(self, content: str) -> str:
        tex_config = get_tex_config()
        full_tex = tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            content
        )
        with display_during_execution(f"Writing \"{self.string}\""):
            file_path = tex_to_svg_file(full_tex)
        return file_path

    #@property
    #def sort_labelled_submobs(self) -> bool:
    #    return False

    # Toolkits

    @staticmethod
    def get_color_command_str(rgb_hex: str) -> str:
        rgb = MTex.hex_to_int(rgb_hex)
        rg, b = divmod(rgb, 256)
        r, g = divmod(rg, 256)
        return f"\\color[RGB]{{{r}, {g}, {b}}}"

    @staticmethod
    def get_tag_str(
        attr_dict: dict[str, str], escape_color_keys: bool, is_begin_tag: bool
    ) -> str:
        if escape_color_keys:
            return ""
        if not is_begin_tag:
            return "}}"
        if "foreground" not in attr_dict:
            return "{{"
        return "{{" + MTex.get_color_command_str(attr_dict["foreground"])

    #@staticmethod
    #def shrink_span(span: Span, skippable_indices: list[int]) -> Span:
    #    span_begin, span_end = span
    #    while span_begin in skippable_indices:
    #        span_begin += 1
    #    while span_end - 1 in skippable_indices:
    #        span_end -= 1
    #    return (span_begin, span_end)

    # Parsing

    #def parse(self) -> None:  # TODO
        #command_spans = self.find_spans(r"\\(?:[a-zA-Z]+|.)")


        #specified_spans = self.chain(
        #    inner_content_spans,
        #    *[
        #        self.find_spans_by_selector(selector)
        #        for selector in self.tex_to_color_map.keys()
        #    ],
        #    self.find_spans_by_selector(self.isolate)
        #)
        #print(specified_spans)
        #label_span_list = self.remove_redundancies(self.chain(*[
        #    self.split_span(span)
        #    for span in specified_spans
        #]))
        #print(label_span_list)
        #for span in all_specified_spans:
        #    adjusted_span, _, _ = self.adjust_span(span, align_level=True)
        #    if adjusted_span[0] > adjusted_span[1]:
        #        continue
        #    specified_spans.append(adjusted_span)



        #reversed_script_spans_dict = {
        #    span_end: span_begin
        #    for span_begin, _, span_end in script_items
        #}
        #label_span_list = [
        #    (content_begin, span_end)
        #    for _, content_begin, span_end in script_items
        #]
        #for span_begin, span_end in specified_spans:
        #    while span_end in reversed_script_spans_dict:
        #        span_end = reversed_script_spans_dict[span_end]
        #    if span_begin >= span_end:
        #        continue
        #    shrinked_span = (span_begin, span_end)
        #    if shrinked_span in label_span_list:
        #        continue
        #    label_span_list.append(shrinked_span)

        #inserted_str_items = [
        #    (span, (
        #        ("{{", "{{" + self.get_color_command_str(label + 1)),
        #        ("}}", "}}"),
        #    ))
        #    for label, span in enumerate(label_span_list)
        #]
        #command_repl_items = [
        #    ((index, index), str_pair)
        #    for index, str_pair in self.sort_obj_pairs_by_spans(inserted_str_items)
        #]
        #for cmd_span in command_spans:
        #    cmd_str = self.get_substr(cmd_span)
        #    if cmd_str not in TEX_COLOR_COMMANDS_DICT:
        #        continue
        #    repl_str = f"{cmd_str}{TEX_COLOR_COMMAND_SUFFIX}"
        #    command_repl_items.append((cmd_span, (cmd_str, repl_str)))
        #print(decorated_strings)
        #return specified_spans, label_span_list, decorated_strings



        #self.command_spans = self.find_spans(r"\\(?:[a-zA-Z]+|.)")
        #self.ignorable_indices = self.get_ignorable_indices()
        #self.brace_content_spans = self.get_brace_content_spans()
        #self.command_repl_items = self.get_command_repl_items()
        ##self.backslash_indices = self.get_backslash_indices()
        #self.ignorable_indices = self.get_ignorable_indices()
        ##self.script_items = self.get_script_items()
        ##self.script_char_indices = self.get_script_char_indices()
        ##self.script_content_spans = self.get_script_content_spans()
        ##self.script_spans = self.get_script_spans()
        #self.specified_spans = self.get_specified_spans()
        ##super().parse()
        #self.label_span_list = self.get_label_span_list()

    def get_entity_spans(self) -> list[Span]:
        return self.find_spans(r"\\(?:[a-zA-Z]+|.)")

    def get_internal_items(
        self
    ) -> tuple[list[tuple[Span, Span]], list[tuple[Span, dict[str, str]]]]:
        command_spans = self.entity_spans
        brace_span_pairs = []
        brace_begin_spans_stack = []
        for span in self.find_spans(r"[{}]"):
            char_index = span[0]
            if (char_index - 1, char_index + 1) in command_spans:
                continue
            if self.get_substr(span) == "{":
                brace_begin_spans_stack.append(span)
            else:
                if not brace_begin_spans_stack:
                    raise ValueError("Missing '{' inserted")
                brace_span = brace_begin_spans_stack.pop()
                brace_span_pairs.append((brace_span, span))
        if brace_begin_spans_stack:
            raise ValueError("Missing '}' inserted")

        #tag_span_pairs = brace_span_pairs.copy()
        script_entity_dict = dict(self.chain(
            [
                (span_begin, span_end)
                for (span_begin, _), (_, span_end) in brace_span_pairs
            ],
            command_spans
        ))
        script_additional_brace_spans = [
            (char_index + 1, script_entity_dict.get(
                script_begin, script_begin + 1
            ))
            for char_index, script_begin in self.find_spans(r"[_^]\s*(?=.)")
            if (char_index - 1, char_index + 1) not in command_spans
        ]
        #for char_index, script_begin in self.find_spans(r"[_^]\s*(?=.)"):
        #    if (char_index - 1, char_index + 1) in command_spans:
        #        continue
        #    script_end = script_entity_dict.get(script_begin, script_begin + 1)
        #    tag_span_pairs.append(
        #        ((char_index, char_index + 1), (script_end, script_end))
        #    )
        #    script_additional_brace_spans.append((char_index + 1, script_end))

        tag_span_pairs = self.chain(
            brace_span_pairs,
            [
                ((script_begin - 1, script_begin), (script_end, script_end))
                for script_begin, script_end in script_additional_brace_spans
            ]
        )

        brace_content_spans = [
            (span_begin, span_end)
            for (_, span_begin), (span_end, _) in brace_span_pairs
        ]
        internal_items = [
            (brace_content_spans[range_begin], {})
            for _, (range_begin, range_end) in self.compress_neighbours([
                (span_begin + index, span_end - index)
                for index, (span_begin, span_end) in enumerate(
                    brace_content_spans
                )
            ])
            if range_end - range_begin >= 2
        ]
        self.script_additional_brace_spans = script_additional_brace_spans
        return tag_span_pairs, internal_items

    def get_external_items(self) -> list[tuple[Span, dict[str, str]]]:
        return [
            (span, {"foreground": self.color_to_hex(color)})
            for selector, color in self.tex_to_color_map.items()
            for span in self.find_spans_by_selector(selector)
        ]

    #def get_spans_from_items(self, specified_items: list[Span]) -> list[Span]:
    #    return specified_items

    #def get_split_items(self, specified_items: list[Span]) -> list[Span]:
    #    return self.remove_redundancies(self.chain(*[
    #        self.split_span(span)
    #        for span in specified_items
    #    ]))

    def get_label_span_list(self, split_spans: list[Span]) -> list[Span]:
        return split_spans

    def get_additional_inserted_str_pairs(
        self
    ) -> list[tuple[Span, tuple[str, str]]]:
        return [
            (span, ("{", "}"))
            for span in self.script_additional_brace_spans
        ]

    def get_command_repl_items(self, is_labelled: bool) -> list[Span, str]:
        if not is_labelled:
            return []
        result = []
        command_spans = self.entity_spans  # TODO
        for cmd_span in command_spans:
            cmd_str = self.get_substr(cmd_span)
            if cmd_str not in TEX_COLOR_COMMANDS_DICT:
                continue
            repl_str = f"{cmd_str}{TEX_COLOR_COMMAND_SUFFIX}"
            result.append((cmd_span, repl_str))
        return result

    #def get_predefined_inserted_str_items(
    #    self, split_items: list[Span]
    #) -> list[tuple[Span, tuple[str, str]]]:
    #    return []

    #def get_ignorable_indices(self) -> list[int]:
    #    return self.chain(
    #        [
    #            index
    #            for index, _ in self.find_spans(r"\s")
    #        ],
    #        [
    #            index
    #            for index, _ in self.find_spans(r"[_^{}]")
    #            if (index - 1, index + 1) not in self.command_spans
    #        ],
    #    )

    #def get_bracket_content_spans(self) -> list[Span]:
    #    span_begins = []
    #    span_ends = []
    #    span_begins_stack = []
    #    for match_obj in re.finditer(r"[{}]", self.string):
    #        index = match_obj.start()
    #        if (index - 1, index + 1) in command_spans:
    #            continue
    #        if match_obj.group() == "{":
    #            span_begins_stack.append(index + 1)
    #        else:
    #            if not span_begins_stack:
    #                raise ValueError("Missing '{' inserted")
    #            span_begins.append(span_begins_stack.pop())
    #            span_ends.append(index)
    #    if span_begins_stack:
    #        raise ValueError("Missing '}' inserted")
    #    return list(zip(span_begins, span_ends))

    #def get_command_repl_items(self) -> list[tuple[Span, str]]:
    #    result = []
    #    for cmd_span in self.command_spans:
    #        cmd_str = self.get_substr(cmd_span)
    #        if cmd_str in TEX_COLOR_COMMANDS_DICT:
    #            repl_str = f"{cmd_str}{TEX_COLOR_COMMAND_SUFFIX}"
    #        else:
    #            repl_str = cmd_str
    #        result.append((cmd_span, repl_str))
    #    return result

    #def get_specified_spans(self) -> list[Span]:
    #    # Match paired double braces (`{{...}}`).
    #    sorted_content_spans = sorted(
    #        self.bracket_content_spans, key=lambda t: t[1]
    #    )
    #    inner_content_spans = [
    #        sorted_content_spans[range_begin]
    #        for _, (range_begin, range_end) in self.compress_neighbours([
    #            (span_begin + index, span_end - index)
    #            for index, (span_begin, span_end) in enumerate(
    #                sorted_content_spans
    #            )
    #        ])
    #        if range_end - range_begin >= 2
    #    ]
    #    #inner_content_spans = [
    #    #    (span_begin + 1, span_end - 1)
    #    #    for span_begin, span_end in inner_brace_spans
    #    #    if span_end - span_begin > 2
    #    #]

    #    return self.remove_redundancies(self.chain(
    #        inner_content_spans,
    #        *[
    #            self.find_spans_by_selector(selector)
    #            for selector in self.tex_to_color_map.keys()
    #        ],
    #        self.find_spans_by_selector(self.isolate)
    #    ))
    #    #return list(filter(
    #    #    lambda span: not any([
    #    #        entity_begin < index < entity_end
    #    #        for index in span
    #    #        for entity_begin, entity_end in self.command_spans
    #    #    ]),
    #    #    result
    #    #))

    #def get_label_span_list(self) -> tuple[list[int], list[Span]]:
    #    script_entity_dict = dict(self.chain(
    #        [
    #            (span_begin - 1, span_end + 1)
    #            for span_begin, span_end in self.bracket_content_spans
    #        ],
    #        self.command_spans
    #    ))
    #    script_items = []
    #    for match_obj in re.finditer(r"\s*([_^])\s*(?=.)", self.string):
    #        char_index = match_obj.start(1)
    #        if (char_index - 1, char_index + 1) in self.command_spans:
    #            continue
    #        span_begin, content_begin = match_obj.span()
    #        span_end = script_entity_dict.get(span_begin, content_begin + 1)
    #        script_items.append(
    #            (span_begin, char_index, content_begin, span_end)
    #        )

    #    reversed_script_spans_dict = {
    #        span_end: span_begin
    #        for span_begin, _, _, span_end in script_items
    #    }
    #    ignorable_indices = self.chain(
    #        [index for index, _ in self.find_spans(r"\s")],
    #        [char_index for _, char_index, _, _ in script_items]
    #    )
    #    result = [
    #        (content_begin, span_end)
    #        for _, _, content_begin, span_end in script_items
    #    ]
    #    for span in self.specified_spans:
    #        span_begin, span_end = self.shrink_span(span, ignorable_indices)
    #        while span_end in reversed_script_spans_dict:
    #            span_end = reversed_script_spans_dict[span_end]
    #        if span_begin >= span_end:
    #            continue
    #        shrinked_span = (span_begin, span_end)
    #        if shrinked_span in result:
    #            continue
    #        result.append(shrinked_span)
    #    return result

    #def get_command_spans(self) -> list[Span]:
    #    return self.find_spans()

    #def get_command_repl_items(self) -> list[Span]:
    #    return [
    #        (span, self.get_substr(span))
    #        for span in self.find_spans(r"\\(?:[a-zA-Z]+|.)")
    #    ]

    #def get_command_spans(self) -> list[Span]:
    #    return self.find_spans(r"\\(?:[a-zA-Z]+|.)")
        #return [
        #    self.match(r"\\(?:[a-zA-Z]+|.)", pos=index).span()
        #    for index in self.backslash_indices
        #]

    #@staticmethod
    #def get_command_repl_dict() -> dict[str | re.Pattern, str]:
    #    return {
    #        cmd_name: f"{cmd_name}replaced"
    #        for cmd_name in TEX_COLOR_COMMANDS_DICT
    #    }

    #def get_backslash_indices(self) -> list[int]:
    #    # The latter of `\\` doesn't count.
    #    return self.find_indices(r"\\.")

    #def get_unescaped_char_indices(self, char: str) -> list[int]:
    #    return list(filter(
    #        lambda index: index - 1 not in self.backslash_indices,
    #        self.find_indices(re.escape(char))
    #    ))

    #def get_script_items(self) -> list[tuple[int, int, int, int]]:
    #    script_entity_dict = dict(self.chain(
    #        self.brace_spans,
    #        self.command_spans
    #    ))
    #    result = []
    #    for match_obj in re.finditer(r"\s*([_^])\s*(?=.)", self.string):
    #        char_index = match_obj.start(1)
    #        if char_index - 1 in self.backslash_indices:
    #            continue
    #        span_begin, content_begin = match_obj.span()
    #        span_end = script_entity_dict.get(span_begin, content_begin + 1)
    #        result.append((span_begin, char_index, content_begin, span_end))
    #    return result

    #def get_script_char_indices(self) -> list[int]:
    #    return self.chain(*[
    #        self.get_unescaped_char_indices(char)
    #        for char in "_^"
    #    ])

    #def get_script_content_spans(self) -> list[Span]:
    #    result = []
    #    script_entity_dict = dict(self.chain(
    #        self.brace_spans,
    #        self.command_spans
    #    ))
    #    for index in self.script_char_indices:
    #        span_begin = self.match(r"\s*", pos=index + 1).end()
    #        if span_begin in script_entity_dict.keys():
    #            span_end = script_entity_dict[span_begin]
    #        else:
    #            match_obj = self.match(r".", pos=span_begin)
    #            if match_obj is None:
    #                continue
    #            span_end = match_obj.end()
    #        result.append((span_begin, span_end))
    #    return result

    #def get_script_spans(self) -> list[Span]:
    #    return [
    #        (
    #            self.match(r"[\s\S]*?(\s*)$", endpos=index).start(1),
    #            script_content_span[1]
    #        )
    #        for index, script_content_span in zip(
    #            self.script_char_indices, self.script_content_spans
    #        )
    #    ]

    #def get_command_repl_items(self) -> list[tuple[Span, str]]:
    #    result = []
    #    brace_spans_dict = dict(self.brace_spans)
    #    brace_begins = list(brace_spans_dict.keys())
    #    for cmd_span in self.command_spans:
    #        cmd_name = self.get_substr(cmd_span)
    #        if cmd_name not in TEX_COLOR_COMMANDS_DICT:
    #            continue
    #        n_braces, substitute_cmd = TEX_COLOR_COMMANDS_DICT[cmd_name]
    #        span_begin, span_end = cmd_span
    #        for _ in range(n_braces):
    #            span_end = brace_spans_dict[min(filter(
    #                lambda index: index >= span_end,
    #                brace_begins
    #            ))]
    #        if substitute_cmd:
    #            repl_str = cmd_name + n_braces * "{black}"
    #        else:
    #            repl_str = ""
    #        result.append(((span_begin, span_end), repl_str))
    #    return result

    #def get_inserted_string_pairs(
    #    self, is_labelled: bool
    #) -> list[tuple[Span, tuple[str, str]]]:
    #    if not is_labelled:
    #        return []
    #    return [
    #        (span, (
    #            "{{" + self.get_color_command_str(label + 1),
    #            "}}"
    #        ))
    #        for label, span in enumerate(self.label_span_list)
    #    ]

    def get_full_content_string(
        self,
        label_span_list: list[Span],
        split_items: list[tuple[Span, dict[str, str]]],
        is_labelled: bool
    ) -> str:
        result = super().get_full_content_string(
            label_span_list, split_items, is_labelled
        )

        if self.tex_environment:
            if isinstance(self.tex_environment, str):
                prefix = f"\\begin{{{self.tex_environment}}}"
                suffix = f"\\end{{{self.tex_environment}}}"
            else:
                prefix, suffix = self.tex_environment
            result = "\n".join([prefix, result, suffix])
        if self.alignment:
            result = "\n".join([self.alignment, result])

        if is_labelled:
            occurred_commands = [
                # TODO
                self.get_substr(span) for span in self.entity_spans
            ]
            newcommand_lines = [
                "".join([
                    f"\\newcommand{cmd_name}{TEX_COLOR_COMMAND_SUFFIX}",
                    f"[{n_braces + 1}][]",
                    "{",
                    cmd_name + "{black}" * n_braces if substitute_cmd else "",
                    "}"
                ])
                for cmd_name, (n_braces, substitute_cmd)
                in TEX_COLOR_COMMANDS_DICT.items()
                if cmd_name in occurred_commands
            ]
            result = "\n".join([*newcommand_lines, result])
        else:
            result = "\n".join([
                self.get_color_command_str(self.base_color_hex),
                result
            ])
        return result

    # Selector

    def get_cleaned_substr(self, span: Span) -> str:
        return self.get_substr(span)   # TODO: test
        #left_brace_indices = [
        #    span_begin - 1
        #    for span_begin, _ in self.brace_content_spans
        #]
        #right_brace_indices = [
        #    span_end
        #    for _, span_end in self.brace_content_spans
        #]
        #skippable_indices = self.chain(
        #    self.ignorable_indices,
        #    #self.script_char_indices,
        #    left_brace_indices,
        #    right_brace_indices
        #)
        #shrinked_span = self.shrink_span(span, skippable_indices)

        ##if shrinked_span[0] >= shrinked_span[1]:
        ##    return ""

        ## Balance braces.
        #unclosed_left_braces = 0
        #unclosed_right_braces = 0
        #for index in range(*shrinked_span):
        #    if index in left_brace_indices:
        #        unclosed_left_braces += 1
        #    elif index in right_brace_indices:
        #        if unclosed_left_braces == 0:
        #            unclosed_right_braces += 1
        #        else:
        #            unclosed_left_braces -= 1
        ##adjusted_span, unclosed_left_braces, unclosed_right_braces \
        ##    = self.adjust_span(span, align_level=False)
        #return "".join([
        #    unclosed_right_braces * "{",
        #    self.get_substr(shrinked_span),
        #    unclosed_left_braces * "}"
        #])

    # Method alias

    def get_parts_by_tex(self, selector: Selector) -> VGroup:
        return self.select_parts(selector)

    def get_part_by_tex(self, selector: Selector) -> VGroup:
        return self.select_part(selector)

    def set_color_by_tex(self, selector: Selector, color: ManimColor):
        return self.set_parts_color(selector, color)

    def set_color_by_tex_to_color_map(
        self, color_map: dict[Selector, ManimColor]
    ):
        return self.set_parts_color_by_dict(color_map)

    def get_tex(self) -> str:
        return self.get_string()


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
