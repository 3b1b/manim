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
    def __init__(self, label):
        self.label = label
        self.containing_labels = []

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join([
            key + "=" + repr(value)
            for key, value in self.__dict__.items()
            if not key.startswith("__")
        ]) + ")"


class _ScriptSpan(object):
    def __init__(self, span_tuple, script_char):
        self.span_tuple = span_tuple
        self.script_char = script_char

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
        self.script_spans_dict = {}
        self.neighbouring_script_span_pairs = []
        self.specified_substrings = []
        self.add_tex_span((0, len(tex_string)))
        self.break_up_by_scripts()
        self.break_up_by_double_braces()
        self.break_up_by_additional_substrings(additional_substrings)
        self.specified_substrings = remove_list_redundancies(
            self.specified_substrings
        )
        self.analyse_containing_labels()

    def add_tex_span(self, span_tuple):
        if span_tuple in self.tex_spans_dict:
            return

        tex_span = _TexSpan(self.labels_count)
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
            extended_begin = script_index
            while extended_begin - 1 in whitespace_indices:
                extended_begin -= 1
            script_begin = script_index + 1
            while script_begin in whitespace_indices:
                script_begin += 1
            if script_begin in brace_indices_dict.keys():
                script_end = brace_indices_dict[script_begin] + 1
            else:
                pattern = re.compile(r"\w|\\[a-zA-Z]+")
                match_obj = pattern.match(tex_string, pos=script_begin)
                if not match_obj:
                    if tex_string[script_index] == "_":
                        script_name = "subscript"
                    else:
                        script_name = "superscript"
                    log.warning(
                        f"Unclear {script_name} detected while parsing. "
                        "Please use braces to clarify"
                    )
                    continue
                script_end = match_obj.end()
            span_tuple = (script_begin, script_end)
            script_span = (extended_begin, script_end)
            self.add_tex_span(span_tuple)
            self.script_spans_dict[script_span] = _ScriptSpan(
                span_tuple, tex_string[script_index]
            )

        if not self.script_spans_dict:
            return

        indices_with_script_spans = sorted([
            (index, script_span)
            for script_span in self.script_spans_dict.keys()
            for index in script_span
        ])
        _, sorted_script_spans = zip(*indices_with_script_spans)
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

        former_script_spans_dict = dict([
            span_tuple[0][::-1]
            for span_tuple in self.neighbouring_script_span_pairs
        ])
        for span_begin, span_end in all_span_tuples:
            # Deconstruct spans containing one out of two scripts.
            if span_end in former_script_spans_dict.keys():
                span_end = former_script_spans_dict[span_end]
                if span_begin >= span_end:
                    continue
            self.add_tex_span((span_begin, span_end))

    def analyse_containing_labels(self):
        tex_spans_dict = self.tex_spans_dict
        span_tuples = sorted(
            tex_spans_dict.keys(),
            key=lambda t: (t[0], -t[1])
        )
        overlapping_span_pairs = []
        for index, span_0 in enumerate(span_tuples):
            for span_1 in span_tuples[index:]:
                if span_0[1] <= span_1[0]:
                    continue
                if span_0[1] < span_1[1]:
                    overlapping_span_pairs.append((span_0, span_1))
                tex_spans_dict[span_0].containing_labels.append(
                    tex_spans_dict[span_1].label
                )
        if overlapping_span_pairs:
            tex_string = self.tex_string
            log.error("Partially overlapping substrings detected:")
            for span_tuple_pair in overlapping_span_pairs:
                log.error(", ".join(
                    f"\"{tex_string[slice(*span_tuple)]}\""
                    for span_tuple in span_tuple_pair
                ))
            raise ValueError

    def get_labelled_tex_string(self):
        tex_string = self.tex_string
        indices_with_labels = sorted([
            (
                *span_tuple[::(1, -1)[flag]],
                flag,
                tex_span.label
            )
            for span_tuple, tex_span in self.tex_spans_dict.items()
            for flag in range(2)
        ], key=lambda t: (t[0], -t[2], -t[1]))
        indices, _, flags, labels = zip(*indices_with_labels)
        command_pieces = [
            ("{{{{\\color[HTML]{{{:06x}}}".format(label), "}}")[flag]
            for flag, label in zip(flags, labels)
        ][1:-1]
        command_pieces.insert(0, "")
        string_pieces = [
            tex_string[slice(*span_tuple)]
            for span_tuple in _get_neighbouring_pairs(indices)
        ]
        return "".join(it.chain(*zip(command_pieces, string_pieces)))

    def get_sorted_submob_indices(self, submob_labels):
        tex_spans_dict = self.tex_spans_dict
        script_spans_dict = self.script_spans_dict
        switch_range_pairs = []
        for span_pair in self.neighbouring_script_span_pairs:
            if not all([
                script_spans_dict[script_span].script_char != "_^"[i]
                for i, script_span in enumerate(span_pair)
            ]):
                continue
            range_pair = []
            for script_span in span_pair:
                span_tuple = script_spans_dict[script_span].span_tuple
                indices = [
                    i for i, label in enumerate(submob_labels)
                    if label in tex_spans_dict[span_tuple].containing_labels
                ]
                range_pair.append(range(indices[0], indices[-1] + 1))
            switch_range_pairs.append(tuple(range_pair))

        switch_range_pairs.sort(key=lambda t: (t[0].stop, -t[0].start))
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
        skipped_indices = sorted(it.chain(
            self.whitespace_indices,
            self.script_indices
        ))
        span_choices = sorted(filter(
            lambda span_tuple: all([
                span_tuple[0] >= custom_span_tuple[0],
                span_tuple[1] <= custom_span_tuple[1]
            ]),
            self.tex_spans_dict.keys()
        ))
        # Filter out spans that reach the farthest.
        span_choices_dict = dict(span_choices)

        span_begin, span_end = custom_span_tuple
        result = []
        while span_begin != span_end:
            if span_begin not in span_choices_dict:
                if span_begin in skipped_indices:
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

    def get_isolated_substrings(self):
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
        "use_plain_tex": False,
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
        labelled_tex_string = self.__parser.get_labelled_tex_string()
        labelled_tex_content = self.get_tex_file_content(labelled_tex_string)
        hash_val = hash(labelled_tex_content)
        if hash_val not in TEX_HASH_TO_MOB_MAP:
            TEX_HASH_TO_MOB_MAP[hash_val] = [None, None]
        mob_list = TEX_HASH_TO_MOB_MAP[hash_val]

        if not self.use_plain_tex:
            if mob_list[0] is not None:
                self.add(*mob_list[0].copy())
                return

            with display_during_execution(f"Writing \"{self.tex_string}\""):
                labelled_svg_glyphs = MTex.tex_content_to_glyphs(
                    labelled_tex_content
                )
                for labelled_glyph in labelled_svg_glyphs:
                    labelled_glyph.glyph_label = MTex.color_to_label(
                        labelled_glyph.fill_color
                    )
                mob = self.build_mobject(labelled_svg_glyphs)
            mob_list[0] = mob
            self.add(*mob.copy())
            return

        if mob_list[1] is not None:
            self.add(*mob_list[1].copy())
            return

        with display_during_execution(f"Writing \"{self.tex_string}\""):
            tex_content = self.get_tex_file_content(self.tex_string)
            labelled_svg_glyphs = MTex.tex_content_to_glyphs(
                labelled_tex_content
            )
            svg_glyphs = MTex.tex_content_to_glyphs(tex_content)
            for glyph, labelled_glyph in zip(svg_glyphs, labelled_svg_glyphs):
                glyph.glyph_label = MTex.color_to_label(
                    labelled_glyph.fill_color
                )
            mob = self.build_mobject(svg_glyphs)
        mob_list[1] = mob
        self.add(*mob.copy())

    def get_tex_file_content(self, tex_string):
        if self.tex_environment:
            tex_string = "\n".join([
                f"\\begin{{{self.tex_environment}}}",
                tex_string,
                f"\\end{{{self.tex_environment}}}"
            ])
        if self.alignment:
            tex_string = "\n".join([self.alignment, tex_string])
        return tex_string

    @staticmethod
    def tex_content_to_glyphs(tex_content):
        tex_config = get_tex_config()
        full_tex = tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            tex_content
        )
        filename = tex_to_svg_file(full_tex)
        return _TexSVG(filename)

    def build_mobject(self, svg_glyphs):
        if not svg_glyphs:
            return VGroup()

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

        indices = self.__parser.get_sorted_submob_indices(submob_labels)
        submobjects = [submobjects[index] for index in indices]

        submob_tex_strings = self.__parser.get_submob_tex_strings(
            submob_labels
        )
        for submob, submob_tex in zip(submobjects, submob_tex_strings):
            submob.tex_string = submob_tex
            # Support `get_tex()` method here.
            submob.get_tex = MethodType(lambda inst: inst.tex_string, submob)
        return VGroup(*submobjects)

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

    def get_isolated_substrings(self):
        return self.__parser.get_isolated_substrings()


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
