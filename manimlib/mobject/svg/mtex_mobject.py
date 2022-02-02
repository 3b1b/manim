import itertools as it
import re
from types import MethodType

from manimlib.constants import BLACK
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.color import color_to_int_rgb
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.tex_file_writing import tex_to_svg_file
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import display_during_execution
from manimlib.logger import log


SCALE_FACTOR_PER_FONT_POINT = 0.001


TEX_HASH_TO_MOB_MAP = {}


def _contains(span_0, span_1):
    return span_0[0] <= span_1[0] and span_1[1] <= span_0[1]


def _get_neighbouring_pairs(iterable):
    return list(adjacent_pairs(iterable))[:-1]


class _TexSVG(SVGMobject):
    CONFIG = {
        "color": BLACK,
        "height": None,
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        },
    }


class _TexSpan(object):
    def __init__(self, label, script_type, command_span):
        self.label = label
        # `script_type`: 0 for normal, 1 for subscript, 2 for superscript.
        self.script_type = script_type
        self.command_span = command_span
        self.containing_labels = []

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join([
            key + "=" + repr(value)
            for key, value in self.__dict__.items()
            if not key.startswith("__")
        ]) + ")"


class _TexParser(object):
    def __init__(self, tex_string, additional_substrings):
        self.tex_string = tex_string
        self.whitespace_indices = self.get_whitespace_indices()
        self.backslash_indices = self.get_backslash_indices()
        self.script_indices = self.get_script_indices()
        self.brace_indices_dict = self.get_brace_indices_dict()
        self.tex_spans_dict = {}
        self.labels_count = 0
        self.specified_substrings = []
        self.add_tex_span((0, len(tex_string)))
        self.break_up_by_scripts()
        self.break_up_by_double_braces()
        self.break_up_by_additional_substrings(additional_substrings)
        self.specified_substrings = remove_list_redundancies(
            self.specified_substrings
        )
        self.check_if_partially_overlap()
        self.analyse_containing_labels()

    def add_tex_span(self, span_tuple, script_type=0, command_span=None):
        if span_tuple in self.tex_spans_dict:
            return

        if command_span is None:
            command_span = span_tuple
        tex_span = _TexSpan(self.labels_count, script_type, command_span)
        self.tex_spans_dict[span_tuple] = tex_span
        self.labels_count += 1

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
        for script_index in self.script_indices:
            script_type = 1 if tex_string[script_index] == "_" else 2
            content_begin = script_index + 1
            while content_begin in whitespace_indices:
                content_begin += 1
            if content_begin in brace_indices_dict.keys():
                content_end = brace_indices_dict[content_begin] + 1
            else:
                pattern = re.compile(r"\w|\\[a-zA-Z]+")
                match_obj = pattern.match(tex_string, pos=content_begin)
                if not match_obj:
                    script_name = ("subscript", "superscript")[script_type - 1]
                    log.warning(f"Unclear {script_name} while parsing")
                    continue
                content_end = match_obj.end()
            self.add_tex_span(
                (script_index, content_end),
                script_type=script_type,
                command_span=(content_begin, content_end)
            )

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
            span_tuple = (left_index, right_index + 1)
            self.add_tex_span(span_tuple)
            self.specified_substrings.append(tex_string[slice(*span_tuple)])
            skip = True

    def break_up_by_additional_substrings(self, additional_substrings):
        stripped_substrings = sorted(remove_list_redundancies([
            string.strip()
            for string in additional_substrings
        ]))
        if "" in stripped_substrings:
            stripped_substrings.remove("")

        tex_string = self.tex_string
        all_span_tuples = []
        for string in stripped_substrings:
            match_objs = list(re.finditer(re.escape(string), tex_string))
            if not match_objs:
                continue
            self.specified_substrings.append(string)
            for match_obj in match_objs:
                all_span_tuples.append(match_obj.span())

        whitespace_indices = self.whitespace_indices
        script_spans_dict = dict([
            span_tuple[::-1]
            for span_tuple, tex_span in self.tex_spans_dict.items()
            if tex_span.script_type != 0
        ])
        for span_begin, span_end in all_span_tuples:
            # Deconstruct spans containing one out of two scripts.
            if span_end in script_spans_dict.keys():
                whitespace_span_end = span_end
                while whitespace_span_end in whitespace_indices:
                    whitespace_span_end += 1
                if whitespace_span_end in script_spans_dict.values():
                    span_end = script_spans_dict[span_end]
                    while span_end in whitespace_indices:
                        span_end -= 1
                    if span_begin >= span_end:
                        continue
            self.add_tex_span((span_begin, span_end))

    def check_if_partially_overlap(self):
        span_tuples = sorted(
            self.tex_spans_dict.keys(),
            key=lambda t: (t[0], -t[1])
        )
        overlapping_span_pairs = []
        for index, span_0 in enumerate(span_tuples):
            for span_1 in span_tuples[index + 1:]:
                if span_0[1] <= span_1[0]:
                    continue
                if span_0[1] < span_1[1]:
                    overlapping_span_pairs.append((span_0, span_1))
        if overlapping_span_pairs:
            tex_string = self.tex_string
            log.error("Partially overlapping substring pairs occur in MTex:")
            for span_tuple_pair in overlapping_span_pairs:
                log.error(", ".join(
                    f"\"{tex_string[slice(*span_tuple)]}\""
                    for span_tuple in span_tuple_pair
                ))
            raise ValueError

    def analyse_containing_labels(self):
        for span_0, tex_span_0 in self.tex_spans_dict.items():
            for span_1, tex_span_1 in self.tex_spans_dict.items():
                if _contains(span_1, span_0):
                    tex_span_1.containing_labels.append(tex_span_0.label)

    def get_labelled_tex_string(self):
        tex_string = self.tex_string
        indices_with_labels = sorted([
            (
                tex_span.command_span[i],
                i,
                tex_span.command_span[1 - i],
                tex_span.label
            )
            for tex_span in self.tex_spans_dict.values()
            for i in range(2)
        ], key=lambda t: (t[0], -t[1], -t[2]))
        indices, flags, _, labels = zip(*indices_with_labels)
        command_pieces = [
            ("{{\\color[HTML]{" + "{:06x}".format(label) + "}", "}}")[flag]
            for flag, label in zip(flags, labels)
        ][1:-1]
        command_pieces.insert(0, "")
        string_pieces = [
            tex_string[slice(*span_tuple)]
            for span_tuple in _get_neighbouring_pairs(indices)
        ]
        return "".join(it.chain(*zip(command_pieces, string_pieces)))

    def require_labelled_tex_file(self):
        return self.labels_count > 1

    def get_sorted_submob_indices(self, submob_labels):
        whitespace_indices = self.whitespace_indices
        tex_spans_dict = self.tex_spans_dict
        indices_with_spans = sorted([
            (*span_tuple[::(-1, 1)[tex_span.script_type - 1]], tex_span)
            for span_tuple, tex_span in tex_spans_dict.items()
            if tex_span.script_type != 0
        ])

        switch_range_pairs = []
        for index_with_span_0, index_with_span_1 in _get_neighbouring_pairs(
            indices_with_spans
        ):
            index_0, _, tex_span_0 = index_with_span_0
            index_1, _, tex_span_1 = index_with_span_1
            if tex_span_0.script_type != 1 or tex_span_1.script_type != 2:
                continue
            if not all([
                index in whitespace_indices
                for index in range(index_0, index_1)
            ]):
                continue
            indices_0 = [
                i for i, label in enumerate(submob_labels)
                if label in tex_span_0.containing_labels
            ]
            range_0 = range(indices_0[0], indices_0[-1] + 1)
            indices_1 = [
                i for i, label in enumerate(submob_labels)
                if label in tex_span_1.containing_labels
            ]
            range_1 = range(indices_1[0], indices_1[-1] + 1)
            switch_range_pairs.append((range_0, range_1))

        switch_range_pairs.sort(key=lambda t: (t[0].stop, -t[0].start))
        indices = list(range(len(submob_labels)))
        for range_0, range_1 in switch_range_pairs:
            indices = [
                *indices[:range_1.start],
                *indices[range_0.start:range_0.stop],
                *indices[range_1.stop:range_0.start],
                *indices[range_1.start:range_1.stop],
                *indices[range_0.stop:]
            ]
        return indices

    def get_submob_tex_strings(self, submob_labels):
        # Not sure whether this is the best practice...
        tex_spans_dict = self.tex_spans_dict
        labels = submob_labels + [submob_labels[0]]
        label_dict = {
            tex_span.label: span_tuple
            for span_tuple, tex_span in tex_spans_dict.items()
        }
        span_tuples = [label_dict[label] for label in labels]
        tex_string_spans = []
        for index, label in enumerate(span_tuples[:-1]):
            containing_labels = tex_spans_dict[label].containing_labels
            if labels[index - 1] in containing_labels:
                span_begin = span_tuples[index - 1][1]
            else:
                span_begin = span_tuples[index][0]
            if labels[index + 1] in containing_labels:
                span_end = span_tuples[index + 1][0]
            else:
                span_end = span_tuples[index][1]
            tex_string_spans.append([span_begin, span_end])
        tex_string_spans[0][0] = label_dict[submob_labels[0]][0]
        tex_string_spans[-1][1] = label_dict[submob_labels[-1]][1]

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
        for tex_string_span in tex_string_spans:
            span_begin, span_end = tex_string_span
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

    def find_span_components_of_custom_span(self, custom_span_tuple):
        whitespace_indices = self.whitespace_indices
        span_choices = sorted(filter(
            lambda t: _contains(custom_span_tuple, t),
            self.tex_spans_dict.keys()
        ))
        # Filter out spans that reach the farthest.
        span_choices_dict = dict(span_choices)

        span_begin, span_end = custom_span_tuple
        result = []
        while span_begin != span_end:
            if span_begin not in span_choices_dict:
                if span_begin in whitespace_indices:
                    # Whitespaces may occur between spans.
                    span_begin += 1
                    continue
                return None
            next_begin = span_choices_dict[span_begin]
            result.append((span_begin, next_begin))
            span_begin = next_begin
        return result

    def get_containing_labels_by_span_tuples(self, span_tuples):
        return remove_list_redundancies(list(it.chain(*[
            self.tex_spans_dict[span_tuple].containing_labels
            for span_tuple in span_tuples
        ])))

    def get_specified_substrings(self):
        return self.specified_substrings

    def get_all_isolated_substrings(self):
        return remove_list_redundancies([
            self.tex_string[slice(*span_tuple)]
            for span_tuple in self.tex_spans_dict.keys()
        ])


class MTex(VMobject):
    CONFIG = {
        "fill_opacity": 1.0,
        "stroke_width": 0,
        "font_size": 48,
        "alignment": "\\centering",
        "tex_environment": "align*",
        "isolate": [],
        "tex_to_color_map": {},
    }

    def __init__(self, tex_string, **kwargs):
        super().__init__(**kwargs)
        tex_string = tex_string.strip()
        # Prevent from passing an empty string.
        if not tex_string:
            tex_string = "\\quad"
        self.tex_string = tex_string

        self.__parser = _TexParser(
            self.tex_string,
            [*self.tex_to_color_map.keys(), *self.isolate]
        )
        self.generate_mobject()
        self.init_colors()
        self.set_color_by_tex_to_color_map(self.tex_to_color_map)
        self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)

    @staticmethod
    def color_to_label(color):
        r, g, b = color_to_int_rgb(color)
        rg = r * 256 + g
        return rg * 256 + b

    def generate_mobject(self):
        parser = self.__parser
        labelled_tex = self.get_tex_file_body(parser.get_labelled_tex_string())
        hash_val = hash(labelled_tex)
        if hash_val not in TEX_HASH_TO_MOB_MAP:
            with display_during_execution(f"Writing \"{self.tex_string}\""):
                full_tex = self.get_tex_file_body(self.tex_string)
                if parser.require_labelled_tex_file():
                    labelled_svg_glyphs = MTex.tex_to_glyphs(labelled_tex)
                    svg_glyphs = MTex.tex_to_glyphs(full_tex)
                    for glyph, labelled_glyph in zip(
                        svg_glyphs, labelled_svg_glyphs
                    ):
                        glyph.glyph_label = MTex.color_to_label(
                            labelled_glyph.fill_color
                        )
                else:
                    svg_glyphs = MTex.tex_to_glyphs(full_tex)
                    for glyph in svg_glyphs:
                        glyph.glyph_label = 0
            TEX_HASH_TO_MOB_MAP[hash_val] = self.build_submobjects(svg_glyphs)
        self.add(*TEX_HASH_TO_MOB_MAP[hash_val].copy())

    def get_tex_file_body(self, new_tex):
        if self.tex_environment:
            new_tex = "\n".join([
                f"\\begin{{{self.tex_environment}}}",
                new_tex,
                f"\\end{{{self.tex_environment}}}"
            ])
        if self.alignment:
            new_tex = "\n".join([self.alignment, new_tex])

        tex_config = get_tex_config()
        return tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            new_tex
        )

    @staticmethod
    def tex_to_glyphs(full_tex):
        filename = tex_to_svg_file(full_tex)
        return _TexSVG(filename)

    def build_submobjects(self, svg_glyphs):
        if not svg_glyphs:
            return []

        # Simply pack together adjacent mobjects with the same label.
        submobjects = []
        submob_labels = []
        new_glyphs = []
        current_glyph_label = svg_glyphs[0].glyph_label
        for glyph in svg_glyphs:
            if glyph.glyph_label == current_glyph_label:
                new_glyphs.append(glyph)
            else:
                submobject = VGroup(*new_glyphs)
                submob_labels.append(new_glyphs[0].glyph_label)
                submobjects.append(submobject)
                new_glyphs = [glyph]
                current_glyph_label = glyph.glyph_label
        submobject = VGroup(*new_glyphs)
        submob_labels.append(new_glyphs[0].glyph_label)
        submobjects.append(submobject)
        for submob, label in zip(submobjects, submob_labels):
            submob.submob_label = label

        parser = self.__parser
        indices = parser.get_sorted_submob_indices(submob_labels)
        submobjects = [submobjects[index] for index in indices]

        submob_tex_strings = parser.get_submob_tex_strings(submob_labels)
        for submob, submob_tex in zip(submobjects, submob_tex_strings):
            submob.tex_string = submob_tex
            # Support `get_tex()` method here.
            submob.get_tex = MethodType(lambda inst: inst.tex_string, submob)
        return submobjects

    def get_part_by_span_tuples(self, span_tuples):
        labels = self.__parser.get_containing_labels_by_span_tuples(
            span_tuples
        )
        return VGroup(*filter(
            lambda submob: submob.submob_label in labels,
            self.submobjects
        ))

    def get_part_by_custom_span_tuple(self, custom_span_tuple):
        span_tuples = self.__parser.find_span_components_of_custom_span(
            custom_span_tuple
        )
        if span_tuples is None:
            tex = self.tex_string[slice(*custom_span_tuple)]
            raise ValueError(f"Failed to match mobjects from tex: \"{tex}\"")
        return self.get_part_by_span_tuples(span_tuples)

    def get_parts_by_tex(self, tex):
        return VGroup(*[
            self.get_part_by_custom_span_tuple(match_obj.span())
            for match_obj in re.finditer(re.escape(tex), self.tex_string)
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
            i for i, submob in enumerate(self.submobjects)
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

    def get_specified_substrings(self):
        return self.__parser.get_specified_substrings()

    def get_all_isolated_substrings(self):
        return self.__parser.get_all_isolated_substrings()


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
