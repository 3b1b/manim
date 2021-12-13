import itertools as it
import re
from types import MethodType

from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.tex_file_writing import tex_to_svg_file
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import display_during_execution


SCALE_FACTOR_PER_FONT_POINT = 0.001


tex_hash_to_mob_map = {}


def _get_neighbouring_pairs(iterable):
    return list(adjacent_pairs(iterable))[:-1]


class _LabelledTex(SVGMobject):
    CONFIG = {
        "height": None,
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        },
    }

    @staticmethod
    def color_str_to_label(color_str):
        if len(color_str) == 4:
            # "#RGB" => "#RRGGBB"
            color_str = "#" + "".join([c * 2 for c in color_str[1:]])
        return int(color_str[1:], 16) - 1

    def get_mobjects_from(self, element):
        result = super().get_mobjects_from(element)
        for mob in result:
            if not hasattr(mob, "glyph_label"):
                mob.glyph_label = -1
        try:
            color_str = element.getAttribute("fill")
            if color_str:
                glyph_label = _LabelledTex.color_str_to_label(color_str)
                for mob in result:
                    mob.glyph_label = glyph_label
        except:
            pass
        return result


class _TexSpan(object):
    def __init__(self, script_type, label):
        # script_type: 0 for normal, 1 for subscript, 2 for superscript.
        # Only those spans with `script_type == 0` will be colored.
        self.script_type = script_type
        self.label = label
        self.containing_labels = []

    def __repr__(self):
        return "_TexSpan(" + ", ".join([
            attrib_name + "=" + str(getattr(self, attrib_name))
            for attrib_name in ["script_type", "label", "containing_labels"]
        ]) + ")"


class _TexParser(object):
    def __init__(self, mtex):
        self.tex_string = mtex.tex_string
        strings_to_break_up = remove_list_redundancies([
            *mtex.isolate, *mtex.tex_to_color_map.keys(), mtex.tex_string
        ])
        if "" in strings_to_break_up:
            strings_to_break_up.remove("")
        unbreakable_commands = mtex.unbreakable_commands

        self.tex_spans_dict = {}
        self.current_label = 0
        self.break_up_by_braces()
        self.break_up_by_scripts()
        self.break_up_by_additional_strings(strings_to_break_up)
        self.merge_unbreakable_commands(unbreakable_commands)
        self.analyse_containing_labels()

    @staticmethod
    def label_to_color_tuple(n):
        # Get a unique color different from black,
        # or the svg file will not include the color information.
        rgb = n + 1
        rg, b = divmod(rgb, 256)
        r, g = divmod(rg, 256)
        return r, g, b

    @staticmethod
    def contains(span_0, span_1):
        return span_0[0] <= span_1[0] and span_1[1] <= span_0[1]

    def add_tex_span(self, span_tuple, script_type=0, label=-1):
        if script_type == 0:
            # Should be additionally labelled.
            label = self.current_label
            self.current_label += 1

        tex_span = _TexSpan(script_type, label)
        self.tex_spans_dict[span_tuple] = tex_span

    def break_up_by_braces(self):
        tex_string = self.tex_string
        span_tuples = []
        left_brace_indices = []
        for match_obj in re.finditer(r"(\\*)(\{|\})", tex_string):
            # Braces following even numbers of backslashes are counted.
            if len(match_obj.group(1)) % 2 == 1:
                continue
            if match_obj.group(2) == "{":
                left_brace_index = match_obj.span(2)[0]
                left_brace_indices.append(left_brace_index)
            else:
                left_brace_index = left_brace_indices.pop()
                right_brace_index = match_obj.span(2)[1]
                span_tuples.append((left_brace_index, right_brace_index))
        if left_brace_indices:
            self.raise_tex_parsing_error()

        self.paired_braces_tuples = span_tuples
        for span_tuple in span_tuples:
            self.add_tex_span(span_tuple)

    def break_up_by_scripts(self):
        tex_string = self.tex_string
        brace_indices_dict = dict(self.tex_spans_dict.keys())
        for match_obj in re.finditer(r"((?<!\\)(_|\^)\s*)|(\s+(_|\^)\s*)", tex_string):
            script_type = 1 if "_" in match_obj.group() else 2
            token_begin, token_end = match_obj.span()
            if token_end in brace_indices_dict:
                content_span = (token_end, brace_indices_dict[token_end])
            else:
                content_match_obj = re.match(r"\w|\\[a-zA-Z]+", tex_string[token_end:])
                if not content_match_obj:
                    self.raise_tex_parsing_error()
                content_span = tuple([
                    index + token_end for index in content_match_obj.span()
                ])
                self.add_tex_span(content_span)
            label = self.tex_spans_dict[content_span].label
            self.add_tex_span(
                (token_begin, content_span[1]),
                script_type=script_type,
                label=label
            )

    def break_up_by_additional_strings(self, strings_to_break_up):
        tex_string = self.tex_string
        all_span_tuples = []
        for string in strings_to_break_up:
            # Only matches non-crossing strings.
            for match_obj in re.finditer(re.escape(string), tex_string):
                all_span_tuples.append(match_obj.span())

        script_spans_dict = dict([
            span_tuple[::-1]
            for span_tuple, tex_span in self.tex_spans_dict.items()
            if tex_span.script_type != 0
        ])
        for span_begin, span_end in all_span_tuples:
            if span_end in script_spans_dict.values():
                # Deconstruct spans with subscripts & superscripts.
                while span_end in script_spans_dict:
                    span_end = script_spans_dict[span_end]
                if span_begin >= span_end:
                    continue
            span_tuple = (span_begin, span_end)
            if span_tuple not in self.tex_spans_dict:
                self.add_tex_span(span_tuple)

    def merge_unbreakable_commands(self, unbreakable_commands):
        tex_string = self.tex_string
        command_merge_spans = []
        brace_indices_dict = dict(self.paired_braces_tuples)
        # Braces leading by `unbreakable_commands` shouldn't be marked.
        for command in unbreakable_commands:
            for match_obj in re.finditer(re.escape(command), tex_string):
                merge_begin_index = match_obj.span()[1]
                merge_end_index = merge_begin_index
                if merge_end_index not in brace_indices_dict:
                    continue
                while merge_end_index in brace_indices_dict:
                    merge_end_index = brace_indices_dict[merge_end_index]
                command_merge_spans.append((merge_begin_index, merge_end_index))

        self.tex_spans_dict = {
            span_tuple: tex_span
            for span_tuple, tex_span in self.tex_spans_dict.items()
            if all([
                not _TexParser.contains(merge_span, span_tuple)
                for merge_span in command_merge_spans
            ])
        }

    def analyse_containing_labels(self):
        for span_0, tex_span_0 in self.tex_spans_dict.items():
            if tex_span_0.script_type != 0:
                continue
            for span_1, tex_span_1 in self.tex_spans_dict.items():
                if _TexParser.contains(span_1, span_0):
                    tex_span_1.containing_labels.append(tex_span_0.label)

    def get_labelled_expression(self):
        tex_string = self.tex_string
        if not self.tex_spans_dict:
            return tex_string

        indices_with_labels = sorted([
            (span_tuple[i], i, span_tuple[1 - i], tex_span.label)
            for span_tuple, tex_span in self.tex_spans_dict.items()
            if tex_span.script_type == 0
            for i in range(2)
        ], key=lambda t: (t[0], -t[1], -t[2]))
        # Add one more item to ensure all the substrings are joined.
        indices_with_labels.append((len(tex_string), 0, 0, 0))

        result = tex_string[: indices_with_labels[0][0]]
        index_with_label_pairs = _get_neighbouring_pairs(indices_with_labels)
        for index_with_label, next_index_with_label in index_with_label_pairs:
            index, flag, _, label = index_with_label
            next_index, *_ = next_index_with_label
            # Adding one more pair of braces will help maintain the glyghs of tex file...
            if flag == 0:
                color_tuple = _TexParser.label_to_color_tuple(label)
                result += "".join([
                    "{{",
                    "\\color[RGB]",
                    "{",
                    ",".join(map(str, color_tuple)),
                    "}"
                ])
            else:
                result += "}}"
            result += tex_string[index : next_index]
        return result

    def raise_tex_parsing_error(self):
        raise ValueError(f"Failed to parse tex: \"{self.tex_string}\"")


class MTex(VMobject):
    CONFIG = {
        "fill_opacity": 1.0,
        "stroke_width": 0,
        "should_center": True,
        "font_size": 48,
        "height": None,
        "organize_left_to_right": False,
        "alignment": "\\centering",
        "tex_environment": "align*",
        "isolate": [],
        "unbreakable_commands": ["\\begin", "\\end"],
        "tex_to_color_map": {},
    }

    def __init__(self, tex_string, **kwargs):
        super().__init__(**kwargs)
        self.tex_string = MTex.modify_tex_string(tex_string)

        tex_parser = _TexParser(self)
        self.tex_spans_dict = tex_parser.tex_spans_dict

        new_tex = tex_parser.get_labelled_expression()
        full_tex = self.get_tex_file_body(new_tex)
        hash_val = hash(full_tex)
        if hash_val not in tex_hash_to_mob_map:
            with display_during_execution(f"Writing \"{tex_string}\""):
                filename = tex_to_svg_file(full_tex)
                svg_mob = _LabelledTex(filename)
                tex_hash_to_mob_map[hash_val] = svg_mob
        self.add(*[
            submob.copy()
            for submob in tex_hash_to_mob_map[hash_val]
        ])
        self.build_submobjects()

        self.init_colors()
        self.set_color_by_tex_to_color_map(self.tex_to_color_map)

        if self.height is None:
            self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    @staticmethod
    def modify_tex_string(tex_string):
        result = tex_string.strip("\n")
        # Prevent from passing an empty string.
        if not result:
            result = "\\quad"
        return result

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

    def build_submobjects(self):
        if not self.submobjects:
            return
        self.group_submobjects()
        self.sort_scripts_in_tex_order()
        self.assign_submob_tex_strings()

    def group_submobjects(self):
        # Simply pack together adjacent mobjects with the same label.
        new_submobjects = []
        def append_new_submobject(glyphs):
            if glyphs:
                submobject = VGroup(*glyphs)
                submobject.submob_label = glyphs[0].glyph_label
                new_submobjects.append(submobject)

        new_glyphs = []
        current_glyph_label = -1
        for submob in self.submobjects:
            if submob.glyph_label == current_glyph_label:
                new_glyphs.append(submob)
            else:
                append_new_submobject(new_glyphs)
                new_glyphs = [submob]
                current_glyph_label = submob.glyph_label
        append_new_submobject(new_glyphs)
        self.set_submobjects(new_submobjects)

    def sort_scripts_in_tex_order(self):
        # LaTeX always puts superscripts before subscripts.
        # This function sorts the submobjects of scripts in the order of tex given.
        index_and_span_list = sorted([
            (index, span_tuple)
            for span_tuple, tex_span in self.tex_spans_dict.items()
            if tex_span.script_type != 0
            for index in span_tuple
        ])
        index_and_span_pair = _get_neighbouring_pairs(index_and_span_list)
        for index_and_span_0, index_and_span_1 in index_and_span_pair:
            index_0, span_tuple_0 = index_and_span_0
            index_1, span_tuple_1 = index_and_span_1
            if index_0 != index_1:
                continue
            if not all([
                self.tex_spans_dict[span_tuple_0].script_type == 1,
                self.tex_spans_dict[span_tuple_1].script_type == 2
            ]):
                continue
            submob_slice_0 = self.slice_of_part(
                self.get_part_by_span_tuples([span_tuple_0])
            )
            submob_slice_1 = self.slice_of_part(
                self.get_part_by_span_tuples([span_tuple_1])
            )
            submobs = self.submobjects
            self.set_submobjects([
                *submobs[: submob_slice_1.start],
                *submobs[submob_slice_0],
                *submobs[submob_slice_1.stop : submob_slice_0.start],
                *submobs[submob_slice_1],
                *submobs[submob_slice_0.stop :]
            ])

    def assign_submob_tex_strings(self):
        # Not sure whether this is the best practice...
        # Just a temporary hack for supporting `TransformMatchingTex`.
        tex_string = self.tex_string
        # Use tex strings including "_", "^".
        label_dict = {}
        for span_tuple, tex_span in self.tex_spans_dict.items():
            if tex_span.script_type != 0:
                label_dict[tex_span.label] = span_tuple
            else:
                if tex_span.label not in label_dict:
                    label_dict[tex_span.label] = span_tuple

        curr_labels = [submob.submob_label for submob in self.submobjects]
        prev_labels = [curr_labels[-1], *curr_labels[:-1]]
        next_labels = [*curr_labels[1:], curr_labels[0]]
        tex_string_spans = []
        for curr_label, prev_label, next_label in zip(
            curr_labels, prev_labels, next_labels
        ):
            curr_span_tuple = label_dict[curr_label]
            prev_span_tuple = label_dict[prev_label]
            next_span_tuple = label_dict[next_label]
            containing_labels = self.tex_spans_dict[curr_span_tuple].containing_labels
            tex_string_spans.append([
                prev_span_tuple[1] if prev_label in containing_labels else curr_span_tuple[0],
                next_span_tuple[0] if next_label in containing_labels else curr_span_tuple[1]
            ])
        tex_string_spans[0][0] = label_dict[curr_labels[0]][0]
        tex_string_spans[-1][1] = label_dict[curr_labels[-1]][1]
        for submob, tex_string_span in zip(self.submobjects, tex_string_spans):
            submob.tex_string = tex_string[slice(*tex_string_span)]
            # Support `get_tex()` method here.
            submob.get_tex = MethodType(lambda inst: inst.tex_string, submob)

    def get_part_by_span_tuples(self, span_tuples):
        labels = remove_list_redundancies(list(it.chain(*[
            self.tex_spans_dict[span_tuple].containing_labels
            for span_tuple in span_tuples
        ])))
        return VGroup(*filter(
            lambda submob: submob.submob_label in labels,
            self.submobjects
        ))

    def find_span_components_of_custom_span(self, custom_span_tuple, partial_result=[]):
        span_begin, span_end = custom_span_tuple
        if span_begin == span_end:
            return partial_result
        next_begin_choices = sorted([
            span_tuple[1]
            for span_tuple in self.tex_spans_dict.keys()
            if span_tuple[0] == span_begin and span_tuple[1] <= span_end
        ], reverse=True)
        for next_begin in next_begin_choices:
            result = self.find_span_components_of_custom_span(
                (next_begin, span_end), [*partial_result, (span_begin, next_begin)]
            )
            if result is not None:
                return result
        return None

    def get_part_by_custom_span_tuple(self, custom_span_tuple):
        span_tuples = self.find_span_components_of_custom_span(custom_span_tuple)
        if span_tuples is None:
            tex = self.tex_string[slice(*custom_span_tuple)]
            raise ValueError(f"Failed to get span of tex: \"{tex}\"")
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
        for tex, color in list(tex_to_color_map.items()):
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

    def slice_of_part(self, part):
        indices = self.indices_of_part(part)
        return slice(indices[0], indices[-1] + 1)

    def slice_of_part_by_tex(self, tex, index=0):
        part = self.get_part_by_tex(tex, index=index)
        return self.slice_of_part(part)

    def index_of_part(self, part):
        return self.indices_of_part(part)[0]

    def index_of_part_by_tex(self, tex, index=0):
        part = self.get_part_by_tex(tex, index=index)
        return self.index_of_part(part)

    def get_tex(self):
        return self.tex_string

    def get_all_isolated_substrings(self):
        tex_string = self.tex_string
        return remove_list_redundancies([
            tex_string[slice(*span_tuple)]
            for span_tuple in self.tex_spans_dict.keys()
        ])

    def print_tex_strings_of_submobjects(self):
        # For debugging
        # Work with `index_labels()`
        print("\n")
        print(f"Submobjects of \"{self.get_tex()}\":")
        for i, submob in enumerate(self.submobjects):
            print(f"{i}: \"{submob.get_tex()}\"")
        print("\n")


class MTexText(MTex):
    CONFIG = {
        "tex_environment": None,
    }
