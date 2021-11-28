import itertools as it
import re

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


class _LabelledTex(SVGMobject):
    CONFIG = {
        "height": None,
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        },
    }

    def get_mobjects_from(self, element):
        result = super().get_mobjects_from(element)
        for mob in result:
            if not hasattr(mob, "label_str"):
                mob.label_str = ""
        try:
            label_str = element.getAttribute("fill")
            if label_str:
                if len(label_str) == 4:
                    # "#RGB" => "#RRGGBB"
                    label_str = "#" + "".join([c * 2 for c in label_str[1:]])
                for mob in result:
                    mob.label_str = label_str
        except:
            pass
        return result


class _TexSpan(object):
    def __init__(self, script_type, label, containing_labels):
        # 0 for normal, 1 for subscript, 2 for superscript.
        self.script_type = script_type
        self.label = label
        self.containing_labels = containing_labels

    def __repr__(self):
        return "_TexSpan(" + ", ".join([
            attrib_name + "=" + str(getattr(self, attrib_name))
            for attrib_name in ["script_type", "label", "containing_labels"]
        ]) + ")"


class MTex(VMobject):
    CONFIG = {
        "fill_opacity": 1.0,
        "stroke_width": 0,
        "should_center": True,
        "font_size": 48,
        "height": None,
        "organize_left_to_right": False,
        "alignment": "\\centering",
        "math_mode": True,
        "isolate": [],
        "tex_to_color_map": {},
    }

    def __init__(self, tex_string, **kwargs):
        super().__init__(**kwargs)
        self.tex_string = tex_string
        self.parse_tex()

        full_tex = self.get_tex_file_body()
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
        self.build_structure()

        self.init_colors()
        self.set_color_by_tex_to_color_map(self.tex_to_color_map)

        if self.height is None:
            self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def add_tex_span(self, span_tuple, script_type=0, containing_labels=None):
        if containing_labels is None:
            # Should be additionally labelled.
            label = self.current_label
            self.current_label += 1
            containing_labels = [label]
        else:
            label = -1

        # 0 for normal, 1 for subscript, 2 for superscript.
        # Only those spans with `label != -1` will be colored.
        tex_span = _TexSpan(script_type, label, containing_labels)
        self.tex_spans_dict[span_tuple] = tex_span

    def parse_tex(self):
        self.tex_spans_dict = {}
        self.current_label = 0
        self.break_up_by_braces()
        self.break_up_by_scripts()
        self.break_up_by_additional_strings()
        self.analyse_containing_labels()

    def break_up_by_braces(self):
        span_tuples = []
        left_brace_indices = []
        for match_obj in re.finditer(r"(?<!\\)(\{|\})", self.tex_string):
            if match_obj.group() == "{":
                left_brace_index = match_obj.span()[0]
                left_brace_indices.append(left_brace_index)
            else:
                left_brace_index = left_brace_indices.pop()
                right_brace_index = match_obj.span()[1]
                span_tuples.append((left_brace_index, right_brace_index))
        if left_brace_indices:
            self.raise_tex_parsing_error()

        for span_tuple in span_tuples:
            self.add_tex_span(span_tuple)

    def break_up_by_scripts(self):
        tex_string = self.tex_string
        brace_indices_dict = dict([
            (span_tuple[0], span_tuple)
            for span_tuple in self.tex_spans_dict.keys()
        ])
        for match_obj in re.finditer(r"((?<!\\)(_|\^)\s*)|(\s+(_|\^)\s*)", tex_string):
            script_type = 1 if "_" in match_obj.group() else 2
            token_begin, token_end = match_obj.span()
            if token_end in brace_indices_dict:
                content_span = brace_indices_dict[token_end]
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
                containing_labels=[label]
            )

    def break_up_by_additional_strings(self):
        additional_strings_to_break_up = remove_list_redundancies([
            *self.isolate, *self.tex_to_color_map.keys()
        ])
        if "" in additional_strings_to_break_up:
            additional_strings_to_break_up.remove("")
        if not additional_strings_to_break_up:
            return

        tex_string = self.tex_string
        all_span_tuples = list(self.tex_spans_dict.keys())
        for string in additional_strings_to_break_up:
            # Only matches non-overlapping strings.
            for match_obj in re.finditer(re.escape(string), tex_string):
                all_span_tuples.append(match_obj.span())

        # Deconstruct spans with subscripts & superscripts.
        script_spans_dict = dict([
            span_tuple[::-1]
            for span_tuple, tex_span in self.tex_spans_dict.items()
            if tex_span.script_type != 0
        ])
        for span_begin, span_end in all_span_tuples:
            while span_end in script_spans_dict:
                span_end = script_spans_dict[span_end]
            if span_begin >= span_end:
                continue
            span_tuple = (span_begin, span_end)
            if span_tuple not in self.tex_spans_dict:
                self.add_tex_span(span_tuple)

    def analyse_containing_labels(self):
        all_span_tuples = list(self.tex_spans_dict.keys())
        if not all_span_tuples:
            return

        for i, span_0 in enumerate(all_span_tuples):
            for j, span_1 in enumerate(all_span_tuples):
                if i == j:
                    continue
                tex_span_0 = self.tex_spans_dict[span_0]
                tex_span_1 = self.tex_spans_dict[span_1]
                if tex_span_0.label == -1:
                    continue
                if span_0[0] <= span_1[0] and span_0[1] >= span_1[1]:
                    tex_span_0.containing_labels.append(tex_span_1.label)

    def raise_tex_parsing_error(self):
        raise ValueError(f"Failed to parse tex: \"{self.tex_string}\"")

    def get_tex_file_body(self):
        new_tex = self.get_modified_expression()
        if self.math_mode:
            new_tex = "\\begin{align*}\n" + new_tex + "\n\\end{align*}"

        new_tex = self.alignment + "\n" + new_tex

        tex_config = get_tex_config()
        return tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            new_tex
        )

    def get_modified_expression(self):
        tex_string = self.tex_string
        if not self.tex_spans_dict:
            return tex_string

        indices_with_labels = sorted([
            (span_tuple[i], i, span_tuple[1 - i], tex_span.label)
            for span_tuple, tex_span in self.tex_spans_dict.items()
            for i in range(2)
            if tex_span.label != -1
        ], key=lambda t: (t[0], 1 - t[1], -t[2]))
        # Add one more item to ensure all the substrings are joined.
        indices_with_labels.append((
            len(tex_string), 0, 0, -1
        ))

        result = tex_string[: indices_with_labels[0][0]]
        for index_0_with_label, index_1_with_label in list(adjacent_pairs(indices_with_labels))[:-1]:
            index, flag, _, label = index_0_with_label
            if flag == 0:
                color_tuple = MTex.label_to_color_tuple(label)
                result += "".join([
                    "{{",
                    "\\color[RGB]",
                    "{" + ",".join(map(str, color_tuple)) + "}"
                ])
            else:
                result += "}}"
            result += tex_string[index : index_1_with_label[0]]
        return result

    @staticmethod
    def label_to_color_tuple(n):
        # Get a unique color different from black,
        # or the svg file will not include the color information.
        return (
            (n + 1) // 256 // 256,
            (n + 1) // 256 % 256,
            (n + 1) % 256
        )

    @staticmethod
    def color_str_to_label(color):
        return int(color[1:], 16) - 1

    def build_structure(self):
        # Simply pack together adjacent mobjects with the same label.
        new_submobjects = []
        new_submobject_components = []
        current_label_str = ""
        for submob in self.submobjects:
            if submob.label_str == current_label_str:
                new_submobject_components.append(submob)
            else:
                if new_submobject_components:
                    new_submobjects.append(VGroup(*new_submobject_components))
                new_submobject_components = [submob]
                current_label_str = submob.label_str
        if new_submobject_components:
            new_submobjects.append(VGroup(*new_submobject_components))

        self.set_submobjects(new_submobjects)
        return self

    def get_all_isolated_substrings(self):
        tex_string = self.tex_string
        return remove_list_redundancies([
            tex_string[slice(*span_tuple)]
            for span_tuple in self.tex_spans_dict.keys()
        ])

    def get_parts_by_tex(self, tex):
        all_span_tuples = sorted(
            list(self.tex_spans_dict.keys()),
            key=lambda t: (t[0], -t[1])
        )
        def find_components_of_span(span_tuple, partial_components=[]):
            span_begin, span_end = span_tuple
            if span_begin == span_end:
                return partial_components
            if span_begin > span_end:
                return None
            next_tuple_choices = filter(lambda t: t[0] == span_begin, all_span_tuples)
            for possible_tuple in next_tuple_choices:
                result = find_components_of_span(
                    (possible_tuple[1], span_end), [*partial_components, possible_tuple]
                )
                if result is not None:
                    return result
            return None

        result = VGroup()
        for match_obj in re.finditer(re.escape(tex), self.tex_string):
            span_tuples = find_components_of_span(match_obj.span())
            if span_tuples is None:
                raise ValueError(f"Failed to get span of tex: \"{tex}\"")
            labels = remove_list_redundancies(list(it.chain(*[
                self.tex_spans_dict[span_tuple].containing_labels
                for span_tuple in span_tuples
            ])))
            mob = VGroup(*filter(
                lambda submob: submob.label_str \
                    and MTex.color_str_to_label(submob.label_str) in labels,
                it.chain(*self.submobjects)
            ))
            result.add(mob)
        return result

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

    def slice_of_part(self, part):
        # Only finds where the head and the tail of `part` is in.
        submobs = self.submobjects
        submobs_len = len(submobs)
        begin_mob = part[0]
        begin_index = 0
        while begin_mob < submobs_len and begin_mob not in submobs[begin_index]:
            begin_index += 1
        end_mob = part[-1]
        end_index = submobs_len - 1
        while end_index >= 0 and end_mob not in submobs[end_index]:
            end_index -= 1
        if begin_index > end_index:
            raise ValueError("Unable to find part")
        return slice(begin_index, end_index + 1)

    def slice_of_part_by_tex(self, tex, index=0):
        part = self.get_part_by_tex(tex, index=index)
        return self.slice_of_part(part)

    def index_of_part(self, part):
        return self.slice_of_part(part).start

    def index_of_part_by_tex(self, tex, index=0):
        return self.slice_of_part_by_tex(tex, index=index).start


class MTexText(MTex):
    CONFIG = {
        "math_mode": False,
    }
