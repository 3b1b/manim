import itertools as it
import re
from types import MethodType

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


SCALE_FACTOR_PER_FONT_POINT = 0.001


def _get_neighbouring_pairs(iterable):
    return list(adjacent_pairs(iterable))[:-1]


class _TexParser(object):
    def __init__(self, tex_string, additional_substrings):
        self.tex_string = tex_string
        self.whitespace_indices = self.get_whitespace_indices()
        self.backslash_indices = self.get_backslash_indices()
        self.script_indices = self.get_script_indices()
        self.brace_indices_dict = self.get_brace_indices_dict()
        self.tex_span_list = []
        self.script_span_to_char_dict = {}
        self.script_span_to_tex_span_dict = {}
        self.neighbouring_script_span_pairs = []
        self.specified_substrings = []
        self.add_tex_span((0, len(tex_string)))
        self.break_up_by_scripts()
        self.break_up_by_double_braces()
        self.break_up_by_additional_substrings(additional_substrings)
        self.tex_span_list.sort(key=lambda t: (t[0], -t[1]))
        self.specified_substrings = remove_list_redundancies(
            self.specified_substrings
        )
        self.containing_labels_dict = self.get_containing_labels_dict()

    def add_tex_span(self, tex_span):
        if tex_span not in self.tex_span_list:
            self.tex_span_list.append(tex_span)

    def get_whitespace_indices(self):
        return [
            match_obj.start()
            for match_obj in re.finditer(r"\s", self.tex_string)
        ]

    def get_backslash_indices(self):
        # Newlines (`\\`) don't count.
        return [
            match_obj.end() - 1
            for match_obj in re.finditer(r"\\+", self.tex_string)
            if len(match_obj.group()) % 2 == 1
        ]

    def filter_out_escaped_characters(self, indices):
        return list(filter(
            lambda index: index - 1 not in self.backslash_indices,
            indices
        ))

    def get_script_indices(self):
        return self.filter_out_escaped_characters([
            match_obj.start()
            for match_obj in re.finditer(r"[_^]", self.tex_string)
        ])

    def get_brace_indices_dict(self):
        tex_string = self.tex_string
        indices = self.filter_out_escaped_characters([
            match_obj.start()
            for match_obj in re.finditer(r"[{}]", tex_string)
        ])
        result = {}
        left_brace_indices_stack = []
        for index in indices:
            if tex_string[index] == "{":
                left_brace_indices_stack.append(index)
            else:
                left_brace_index = left_brace_indices_stack.pop()
                result[left_brace_index] = index
        return result

    def break_up_by_scripts(self):
        # Match subscripts & superscripts.
        tex_string = self.tex_string
        whitespace_indices = self.whitespace_indices
        brace_indices_dict = self.brace_indices_dict
        script_spans = []
        for script_index in self.script_indices:
            script_char = tex_string[script_index]
            extended_begin = script_index
            while extended_begin - 1 in whitespace_indices:
                extended_begin -= 1
            script_begin = script_index + 1
            while script_begin in whitespace_indices:
                script_begin += 1
            if script_begin in brace_indices_dict.keys():
                script_end = brace_indices_dict[script_begin] + 1
            else:
                pattern = re.compile(r"[a-zA-Z0-9]|\\[a-zA-Z]+")
                match_obj = pattern.match(tex_string, pos=script_begin)
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
                script_end = match_obj.end()
            tex_span = (script_begin, script_end)
            script_span = (extended_begin, script_end)
            script_spans.append(script_span)
            self.add_tex_span(tex_span)
            self.script_span_to_char_dict[script_span] = script_char
            self.script_span_to_tex_span_dict[script_span] = tex_span

        if not script_spans:
            return

        _, sorted_script_spans = zip(*sorted([
            (index, script_span)
            for script_span in script_spans
            for index in script_span
        ]))
        for span_0, span_1 in _get_neighbouring_pairs(sorted_script_spans):
            if span_0[1] == span_1[0]:
                self.neighbouring_script_span_pairs.append((span_0, span_1))

    def break_up_by_double_braces(self):
        # Match paired double braces (`{{...}}`).
        tex_string = self.tex_string
        reversed_indices_dict = dict(
            item[::-1] for item in self.brace_indices_dict.items()
        )
        skip = False
        for prev_right_index, right_index in _get_neighbouring_pairs(
            list(reversed_indices_dict.keys())
        ):
            if skip:
                skip = False
                continue
            if right_index != prev_right_index + 1:
                continue
            left_index = reversed_indices_dict[right_index]
            prev_left_index = reversed_indices_dict[prev_right_index]
            if left_index != prev_left_index - 1:
                continue
            tex_span = (left_index, right_index + 1)
            self.add_tex_span(tex_span)
            self.specified_substrings.append(tex_string[slice(*tex_span)])
            skip = True

    def break_up_by_additional_substrings(self, additional_substrings):
        stripped_substrings = sorted(remove_list_redundancies([
            string.strip()
            for string in additional_substrings
        ]))
        if "" in stripped_substrings:
            stripped_substrings.remove("")

        tex_string = self.tex_string
        all_tex_spans = []
        for string in stripped_substrings:
            match_objs = list(re.finditer(re.escape(string), tex_string))
            if not match_objs:
                continue
            self.specified_substrings.append(string)
            for match_obj in match_objs:
                all_tex_spans.append(match_obj.span())

        former_script_spans_dict = dict([
            script_span_pair[0][::-1]
            for script_span_pair in self.neighbouring_script_span_pairs
        ])
        for span_begin, span_end in all_tex_spans:
            # Deconstruct spans containing one out of two scripts.
            if span_end in former_script_spans_dict.keys():
                span_end = former_script_spans_dict[span_end]
                if span_begin >= span_end:
                    continue
            self.add_tex_span((span_begin, span_end))

    def get_containing_labels_dict(self):
        tex_span_list = self.tex_span_list
        result = {
            tex_span: []
            for tex_span in tex_span_list
        }
        overlapping_tex_span_pairs = []
        for index_0, span_0 in enumerate(tex_span_list):
            for index_1, span_1 in enumerate(tex_span_list[index_0:]):
                if span_0[1] <= span_1[0]:
                    continue
                if span_0[1] < span_1[1]:
                    overlapping_tex_span_pairs.append((span_0, span_1))
                result[span_0].append(index_0 + index_1)
        if overlapping_tex_span_pairs:
            tex_string = self.tex_string
            log.error("Partially overlapping substrings detected:")
            for tex_span_pair in overlapping_tex_span_pairs:
                log.error(", ".join(
                    f"\"{tex_string[slice(*tex_span)]}\""
                    for tex_span in tex_span_pair
                ))
            raise ValueError
        return result

    def get_labelled_tex_string(self):
        indices, _, flags, labels = zip(*sorted([
            (*tex_span[::(1, -1)[flag]], flag, label)
            for label, tex_span in enumerate(self.tex_span_list)
            for flag in range(2)
        ], key=lambda t: (t[0], -t[2], -t[1])))
        command_pieces = [
            ("{{" + self.get_color_command(label), "}}")[flag]
            for flag, label in zip(flags, labels)
        ][1:-1]
        command_pieces.insert(0, "")
        string_pieces = [
            self.tex_string[slice(*tex_span)]
            for tex_span in _get_neighbouring_pairs(indices)
        ]
        return "".join(it.chain(*zip(command_pieces, string_pieces)))

    @staticmethod
    def get_color_command(label):
        rg, b = divmod(label, 256)
        r, g = divmod(rg, 256)
        return "".join([
            "\\color[RGB]",
            "{",
            ",".join(map(str, (r, g, b))),
            "}"
        ])

    def get_sorted_submob_indices(self, submob_labels):
        def script_span_to_submob_range(script_span):
            tex_span = self.script_span_to_tex_span_dict[script_span]
            submob_indices = [
                index for index, label in enumerate(submob_labels)
                if label in self.containing_labels_dict[tex_span]
            ]
            return range(submob_indices[0], submob_indices[-1] + 1)

        filtered_script_span_pairs = filter(
            lambda script_span_pair: all([
                self.script_span_to_char_dict[script_span] == character
                for script_span, character in zip(script_span_pair, "_^")
            ]),
            self.neighbouring_script_span_pairs
        )
        switch_range_pairs = sorted([
            tuple([
                script_span_to_submob_range(script_span)
                for script_span in script_span_pair
            ])
            for script_span_pair in filtered_script_span_pairs
        ], key=lambda t: (t[0].stop, -t[0].start))
        result = list(range(len(submob_labels)))
        for range_0, range_1 in switch_range_pairs:
            result = [
                *result[:range_1.start],
                *result[range_0.start:range_0.stop],
                *result[range_1.stop:range_0.start],
                *result[range_1.start:range_1.stop],
                *result[range_0.stop:]
            ]
        return result

    def get_submob_tex_strings(self, submob_labels):
        ordered_tex_spans = [
            self.tex_span_list[label] for label in submob_labels
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

        tex_string = self.tex_string
        left_brace_indices = sorted(self.brace_indices_dict.keys())
        right_brace_indices = sorted(self.brace_indices_dict.values())
        ignored_indices = sorted(it.chain(
            self.whitespace_indices,
            left_brace_indices,
            right_brace_indices,
            self.script_indices
        ))
        result = []
        for span_begin, span_end in zip(string_span_begins, string_span_ends):
            while span_begin in ignored_indices:
                span_begin += 1
            if span_begin >= span_end:
                result.append("")
                continue
            while span_end - 1 in ignored_indices:
                span_end -= 1
            unclosed_left_brace = 0
            unclosed_right_brace = 0
            for index in range(span_begin, span_end):
                if index in left_brace_indices:
                    unclosed_left_brace += 1
                elif index in right_brace_indices:
                    if unclosed_left_brace == 0:
                        unclosed_right_brace += 1
                    else:
                        unclosed_left_brace -= 1
            result.append("".join([
                unclosed_right_brace * "{",
                tex_string[span_begin:span_end],
                unclosed_left_brace * "}"
            ]))
        return result

    def find_span_components_of_custom_span(self, custom_span):
        skipped_indices = sorted(it.chain(
            self.whitespace_indices,
            self.script_indices
        ))
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

    def get_containing_labels_by_tex_spans(self, tex_spans):
        return remove_list_redundancies(list(it.chain(*[
            self.containing_labels_dict[tex_span]
            for tex_span in tex_spans
        ])))

    def get_specified_substrings(self):
        return self.specified_substrings

    def get_isolated_substrings(self):
        return remove_list_redundancies([
            self.tex_string[slice(*tex_span)]
            for tex_span in self.tex_span_list
        ])


class _TexSVG(SVGMobject):
    CONFIG = {
        "height": None,
        "fill_opacity": 1.0,
        "stroke_width": 0,
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        },
    }


class MTex(_TexSVG):
    CONFIG = {
        "color": WHITE,
        "font_size": 48,
        "alignment": "\\centering",
        "tex_environment": "align*",
        "isolate": [],
        "tex_to_color_map": {},
        "use_plain_tex": False,
    }

    def __init__(self, tex_string, **kwargs):
        digest_config(self, kwargs)
        tex_string = tex_string.strip()
        # Prevent from passing an empty string.
        if not tex_string:
            tex_string = "\\quad"
        self.tex_string = tex_string
        self.parser = _TexParser(
            self.tex_string,
            [*self.tex_to_color_map.keys(), *self.isolate]
        )
        super().__init__(**kwargs)

        self.set_color_by_tex_to_color_map(self.tex_to_color_map)
        self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)

    @property
    def hash_seed(self):
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.tex_string,
            self.parser.specified_substrings,
            self.alignment,
            self.tex_environment,
            self.use_plain_tex
        )

    def get_file_path(self):
        return self._get_file_path(self.use_plain_tex)

    def _get_file_path(self, use_plain_tex):
        if use_plain_tex:
            tex_string = self.tex_string
        else:
            tex_string = self.parser.get_labelled_tex_string()

        full_tex = self.get_tex_file_body(tex_string)
        with display_during_execution(f"Writing \"{self.tex_string}\""):
            file_path = self.tex_to_svg_file_path(full_tex)
        return file_path

    def get_tex_file_body(self, tex_string):
        if self.tex_environment:
            tex_string = "\n".join([
                f"\\begin{{{self.tex_environment}}}",
                tex_string,
                f"\\end{{{self.tex_environment}}}"
            ])
        if self.alignment:
            tex_string = "\n".join([self.alignment, tex_string])
        
        tex_config = get_tex_config()
        return tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            tex_string
        )

    @staticmethod
    def tex_to_svg_file_path(tex_file_content):
        return tex_to_svg_file(tex_file_content)

    def generate_mobject(self):
        super().generate_mobject()

        if not self.use_plain_tex:
            labelled_svg_glyphs = self
        else:
            file_path = self._get_file_path(use_plain_tex=False)
            labelled_svg_glyphs = _TexSVG(file_path)

        glyph_labels = [
            self.color_to_label(labelled_glyph.get_fill_color())
            for labelled_glyph in labelled_svg_glyphs
        ]
        mob = self.build_mobject(self, glyph_labels)
        self.set_submobjects(mob.submobjects)

    @staticmethod
    def color_to_label(color):
        r, g, b = color_to_int_rgb(color)
        rg = r * 256 + g
        return rg * 256 + b

    def build_mobject(self, svg_glyphs, glyph_labels):
        if not svg_glyphs:
            return VGroup()

        # Simply pack together adjacent mobjects with the same label.
        submobjects = []
        submob_labels = []
        new_glyphs = []
        current_glyph_label = glyph_labels[0]
        for glyph, label in zip(svg_glyphs, glyph_labels):
            if label == current_glyph_label:
                new_glyphs.append(glyph)
            else:
                submobject = VGroup(*new_glyphs)
                submob_labels.append(current_glyph_label)
                submobjects.append(submobject)
                new_glyphs = [glyph]
                current_glyph_label = label
        submobject = VGroup(*new_glyphs)
        submob_labels.append(current_glyph_label)
        submobjects.append(submobject)

        indices = self.parser.get_sorted_submob_indices(submob_labels)
        rearranged_submobjects = [submobjects[index] for index in indices]
        rearranged_labels = [submob_labels[index] for index in indices]

        submob_tex_strings = self.parser.get_submob_tex_strings(
            rearranged_labels
        )
        for submob, label, submob_tex in zip(
            rearranged_submobjects, rearranged_labels, submob_tex_strings
        ):
            submob.submob_label = label
            submob.tex_string = submob_tex
            # Support `get_tex()` method here.
            submob.get_tex = MethodType(lambda inst: inst.tex_string, submob)
        return VGroup(*rearranged_submobjects)

    def get_part_by_tex_spans(self, tex_spans):
        labels = self.parser.get_containing_labels_by_tex_spans(tex_spans)
        return VGroup(*filter(
            lambda submob: submob.submob_label in labels,
            self.submobjects
        ))

    def get_part_by_custom_span(self, custom_span):
        tex_spans = self.parser.find_span_components_of_custom_span(
            custom_span
        )
        if tex_spans is None:
            tex = self.tex_string[slice(*custom_span)]
            raise ValueError(f"Failed to match mobjects from tex: \"{tex}\"")
        return self.get_part_by_tex_spans(tex_spans)

    def get_parts_by_tex(self, tex):
        return VGroup(*[
            self.get_part_by_custom_span(match_obj.span())
            for match_obj in re.finditer(
                re.escape(tex.strip()), self.tex_string
            )
        ])

    def get_part_by_tex(self, tex, index=0):
        all_parts = self.get_parts_by_tex(tex)
        return all_parts[index]

    def set_color_by_tex(self, tex, color):
        self.get_parts_by_tex(tex).set_color(color)
        return self

    def set_color_by_tex_to_color_map(self, tex_to_color_map):
        for tex, color in tex_to_color_map.items():
            self.set_color_by_tex(tex, color)
        return self

    def indices_of_part(self, part):
        indices = [
            index for index, submob in enumerate(self.submobjects)
            if submob in part
        ]
        if not indices:
            raise ValueError("Failed to find part in tex")
        return indices

    def indices_of_part_by_tex(self, tex, index=0):
        part = self.get_part_by_tex(tex, index=index)
        return self.indices_of_part(part)

    def get_tex(self):
        return self.tex_string

    def get_submob_tex(self):
        return [
            submob.get_tex()
            for submob in self.submobjects
        ]

    def get_specified_substrings(self):
        return self.parser.get_specified_substrings()

    def get_isolated_substrings(self):
        return self.parser.get_isolated_substrings()


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
