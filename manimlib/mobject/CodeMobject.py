from manimlib.imports_with_c import *
from htmldom import htmldom
import html

def latex_escape(str):
    # Replace a \ with $\backslash$
    # This is made more complicated because the dollars will be escaped
    # by the subsequent replacement. Easiest to add \backslash
    # now and then add the dollars
    # Must be done after escape of \ since this command adds latex escapes
    # Replace characters that can be escaped
    # Replace ^ characters with \^{} so that $^F works okay
    # Replace tilde (~) with \texttt{\~{}} # Replace tilde (~) with \texttt{\~{}}
    list = ["\\", "^", "~", '&', '%', '$', '#', '_', '{', '}']
    change_to = ["$\\backslash$", "\\^{}", "\\texttt{\\~{}}", '\\&', '\\%', '\\$', '\\#', '\\_', '\\{', '\\}']

    for i in list:
        if i in str:
            str = str.replace(i, change_to[list.index(i)])
            break
    return str


class CodeMobject(VGroup):
    CONFIG = {
        "tab_spacing": 0.4,
        "line_spacing": 0.1,
        "coordinates": [0, 0],
        "scale_factor": 0.5,
        "run_time": 1,
    }

    def __init__(self, file_name=None, **kwargs):
        Container.__init__(self, **kwargs)
        self.file_name = file_name or self.file_name
        self.ensure_valid_file()
        self.gen_code_json()
        self.temp_char = TextMobject("(").scale(self.scale_factor)
        self.code_json_to_mobject_array()
        self.gen_words_matrix()
        self.gen_chars_matrix()
        VGroup.__init__(self, *[self.chars_matrix[i] for i in range(self.chars_matrix.__len__())], **kwargs)

    def scale(self, scale_factor,**kwargs):
        self.apply_points_function_about_point(
            lambda points: scale_factor * points, **kwargs
        )
        return self

    def apply_points_function_about_point(self, func, about_point=None, about_edge=None):
        if about_point is None:
            if about_edge is None:
                about_edge = self.get_corner(UP+LEFT)
            about_point = self.get_critical_point(about_edge)
        for mob in self.family_members_with_points():
            mob.points -= about_point
            mob.points = func(mob.points)
            mob.points += about_point
        return self

    def ensure_valid_file(self):
        if self.file_name is None:
            raise Exception("Must specify file for CodeMobject")
        possible_paths = [
            os.path.join(os.path.join("assets", "code_htmls"), self.file_name),
            os.path.join(os.path.join("assets", "code_htmls"), self.file_name + ".html"),
            os.path.join(os.path.join("assets", "code_htmls"), self.file_name + ".htm"),
            os.path.join(os.path.join("assets", "code_htmls"), self.file_name + ".HTML"),
            os.path.join(os.path.join("assets", "code_htmls"), self.file_name + ".HTM"),
            self.file_name,
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.file_path = path
                return
        raise IOError("No file matching %s in image directory" %
                      self.file_name)

    def gen_words_matrix(self):
        self.words_matrix = VGroup()
        for i in range(0, self.lines_mobjets.__len__()):
            self.words_matrix.add(VGroup())
            for j in range(0, self.lines_mobjets[i].__len__()):
                for k in range(0, self.lines_mobjets[i][j].__len__()):
                    self.words_matrix[i].add(self.lines_mobjets[i][j][k])

    def gen_chars_matrix(self):
        self.chars_matrix = VGroup()
        for i in range(0, self.lines_mobjets.__len__()):
            self.chars_matrix.add(VGroup())
            for j in range(0, self.lines_mobjets[i].__len__()):
                for k in range(0, self.lines_mobjets[i][j].__len__()):
                    for l in range(0, self.lines_mobjets[i][j][k].__len__()):
                        self.chars_matrix[i].add(self.lines_mobjets[i][j][k][l])

    def move_to_initial_pos(self, line_no, line_or_brace_index):
        self.lines_mobjets[line_no][line_or_brace_index].move_to(
            np.array([self.coordinates[0], self.coordinates[1], 0]) +
            np.array([self.lines_mobjets[line_no][line_or_brace_index].get_width() / 2, 0, 0]) +
            RIGHT * self.tab_spaces[line_no] * self.tab_spacing)

    def move_to_next_line_initial_pos(self, line_no, line_or_brace_index):
        self.lines_mobjets[line_no][line_or_brace_index].move_to(
            np.array([self.coordinates[0], self.coordinates[1], 0]) +
            np.array([self.lines_mobjets[line_no][line_or_brace_index].get_width() / 2, 0, 0]) +
            DOWN * line_no * (self.temp_char.get_height() + self.line_spacing) +
            RIGHT * (self.tab_spaces[line_no] * self.tab_spacing))

    def move_to_next_word_initial_pos(self, line_no, line_or_brace_index):
        self.lines_mobjets[line_no][line_or_brace_index].move_to(
            self.lines_mobjets[line_no][line_or_brace_index - 1].get_right() +
            np.array(
                [self.lines_mobjets[line_no][line_or_brace_index].get_width() / 2, 0,
                 0]) +
            np.array([self.temp_char.get_width(), 0, 0]))

    def code_json_to_mobject_array(self):
        self.lines_mobjets = []
        self.total_chars = 0
        self.no_of_chars = []
        for line_no in range(0, self.code_json.__len__()):
            self.lines_mobjets.append([])
            line = []
            char_count = 0
            line_or_brace_index = -1
            endc = False
            pre_index = -1
            brace_count = 0
            for j in range(0, self.code_json[line_no].__len__()):
                endc = False
                text = self.code_json[line_no][j][0]
                if j == 0:
                    self.code_json[line_no][j][0] = text.lstrip()
                if j == self.code_json[line_no].__len__() - 1:
                    self.code_json[line_no][j][0] = text.rstrip()
                text = self.code_json[line_no][j][0]
                self.total_chars = self.total_chars + text.__len__()
                char_count = char_count + text.__len__()
                # print(text)
                color = self.code_json[line_no][j][1]
                if text == '{' or text == '}':
                    if line.__len__() != 0:
                        temp_text = line[line.__len__() - 1]
                        line_temp = temp_text.rstrip()
                        c_temp = temp_text.__len__() - line_temp.__len__()
                        self.total_chars = self.total_chars - c_temp
                        char_count = char_count - c_temp

                    brace_count = brace_count + 1
                    endc = True
                    if line_or_brace_index == -1 and line.__len__() == 0:
                        char_count = 0
                        # print(text,"yesssssss")
                        if text == "{":
                            cb = Brace(self.temp_char, LEFT,
                                       width_multiplier=self.get_braces_scale_factor_acc_to_text_scale_factor(
                                           self.scale_factor), color=color)
                            # cb.set_width(self.temp_char.get_width())
                            # cb = SVGMobject("LeftCurlyBracket.svg", color=color)
                            # cb.set_height(self.temp_char.get_height())
                        else:
                            cb = Brace(self.temp_char, RIGHT,
                                       width_multiplier=self.get_braces_scale_factor_acc_to_text_scale_factor(
                                           self.scale_factor), color=color)
                            # cb = SVGMobject("RightCurlyBracket.svg", color=color).set_height(
                            # self.temp_char.get_height())
                        self.lines_mobjets[line_no].append(cb)
                        line_or_brace_index = line_or_brace_index + 1
                        if line_no == 0:
                            self.move_to_initial_pos(line_no, line_or_brace_index)
                        else:
                            self.move_to_next_line_initial_pos(line_no, line_or_brace_index)
                    elif line_or_brace_index == -1:
                        # print(line)
                        tmo = TextMobject(*line).scale(self.scale_factor)
                        z = -1
                        for l in range(pre_index + 1, j):
                            z = z + 1
                            tmo[z].set_color(self.code_json[line_no][l][1])
                        self.lines_mobjets[line_no].append(tmo)
                        char_count = 0
                        line = []
                        line_or_brace_index = line_or_brace_index + 1
                        self.move_to_next_line_initial_pos(line_no, line_or_brace_index)
                        if text == "{":
                            cb = Brace(self.temp_char, LEFT,
                                       width_multiplier=self.get_braces_scale_factor_acc_to_text_scale_factor(
                                           self.scale_factor), color=color)
                            # cb = SVGMobject("LeftCurlyBracket.svg", color=color).set_height(
                            # self.temp_char.get_height())
                        else:
                            cb = Brace(self.temp_char, RIGHT,
                                       width_multiplier=self.get_braces_scale_factor_acc_to_text_scale_factor(
                                           self.scale_factor), color=color)
                            # cb = SVGMobject("RightCurlyBracket.svg", color=color).set_height(
                            # self.temp_char.get_height())
                        self.lines_mobjets[line_no].append(cb)
                        line_or_brace_index = line_or_brace_index + 1
                        self.move_to_next_word_initial_pos(line_no, line_or_brace_index)
                    else:
                        # print(self.code_json[line_no])
                        tmo = TextMobject(*line).scale(self.scale_factor)
                        z = -1
                        for l in range(pre_index + 1, j):
                            z = z + 1
                            tmo[z].set_color(self.code_json[line_no][l][1])
                        self.lines_mobjets[line_no].append(tmo)
                        char_count = 0
                        line = []
                        line_or_brace_index = line_or_brace_index + 1
                        self.move_to_next_word_initial_pos(line_no, line_or_brace_index)
                        if text == "{":
                            cb = Brace(self.temp_char, LEFT,
                                       width_multiplier=self.get_braces_scale_factor_acc_to_text_scale_factor(
                                           self.scale_factor), color=color)
                            # cb = SVGMobject("LeftCurlyBracket.svg", color=color).set_height(
                            # self.temp_char.get_height())
                        else:
                            cb = Brace(self.temp_char, RIGHT,
                                       width_multiplier=self.get_braces_scale_factor_acc_to_text_scale_factor(
                                           self.scale_factor), color=color)
                            # cb = SVGMobject("RightCurlyBracket.svg", color=color).set_height(
                            # self.temp_char.get_height())
                        self.lines_mobjets[line_no].append(cb)
                        line_or_brace_index = line_or_brace_index + 1
                        self.move_to_next_word_initial_pos(line_no, line_or_brace_index)
                    pre_index = j
                else:
                    line.append(latex_escape(text))
            if not endc:
                # print(line)
                tmo = TextMobject(*line).scale(self.scale_factor)
                z = 0
                for l in range(pre_index + 1, self.code_json[line_no].__len__()):
                    tmo[z].set_color(self.code_json[line_no][l][1])
                    z = z + 1
                self.lines_mobjets[line_no].append(tmo)
                char_count = 0
                line_or_brace_index = line_or_brace_index + 1
                if line_or_brace_index != 0:
                    self.move_to_next_word_initial_pos(line_no, line_or_brace_index)
                elif line_or_brace_index == 0:
                    if line_no != 0:
                        self.move_to_next_line_initial_pos(line_no, line_or_brace_index)
                    else:
                        self.move_to_initial_pos(line_no, line_or_brace_index)
            self.no_of_chars.append(char_count)
        self.run_time_per_char = self.run_time / self.total_chars
        # print(self.run_time_per_char, self.total_chars, self.run_time_per_char * self.total_chars)

    def gen_code_json(self):
        file = open(self.file_path, "r")
        self.html_string = file.read()
        i = self.html_string.find("&#xa0;")
        str1 = self.html_string[0:i]
        str1 = str1[0:-31] + "" \
                             "\n"
        str3 = self.html_string[i:]
        j = str3.find("</span")
        str2 = ""
        for k in range(0, int(j / 6)):
            str2 += " "
        str3 = str3[j + 7:]
        self.html_string = str1 + str2 + str3
        for i in range(10, -1, -1):
            self.html_string = self.html_string.replace("</span>" + " " * i, " " * i + "</span>")
        self.html_string = self.html_string.replace("#40015a", "#e1a8ff")
        st = self.html_string.split("</span>")
        str = st[0] + "</span>"
        for i in range(1, st.__len__()):
            j = st[i].find("<span")
            temp = ""
            starti = -1
            for k in range(0, j):
                if (st[i][k] == "\n" or st[i][k] == " ") and starti == -1:
                    continue
                else:
                    if starti == -1: starti = k
                    temp = temp + st[i][k]
            if temp != "":
                temp = st[i][0:starti]
                temp = temp + '<span style="color:#ffffff;">' + st[i][starti:j] + "</span>"
                temp = temp + st[i][j:]
                st[i] = temp
            str = str + st[i] + "</span>"
        self.html_string = str
        lines = self.html_string.split("\n")
        i = lines.index("</pre>")
        lines = lines[0:i]
        i = lines[0].find(">")
        lines[0] = lines[0][i + 1:]
        code_json = []
        tab_spaces = []
        k = -1
        for i in range(0, lines.__len__()):
            if lines[i].__len__() == 0:
                continue
            code_json.append([])
            k = k + 1
            if lines[i][0] == " ":
                j = lines[i].find("<")
                lines[i] = "\t" * int(j / 2) + lines[i][j:]
            dom = htmldom.HtmlDom().createDom(lines[i])
            count = 0
            while lines[i][count] == '\t':
                count = count + 1
            tab_spaces.append(count)
            span = dom.find("span")
            for j in span:
                style = j.attr("style")[6:]
                color = style[:style.find(";")]
                text = html.unescape(j.text())  # .strip()
                # print(text)
                text = self.handling_braces(text)
                code_json[k].extend([[sub_text, color] for sub_text in text])
        self.code_json = code_json
        self.tab_spaces = tab_spaces

    def get_braces_scale_factor_acc_to_text_scale_factor(self, text_scale_factor):
        if text_scale_factor <= 0.6:
            return 9
        elif 0.6 < text_scale_factor <= 1:
            return 6.5
        elif 1 < text_scale_factor <= 1.5:
            return 5
        elif 1.5 < text_scale_factor <= 2:
            return 3.5
        elif 2 < text_scale_factor <= 2.5:
            return 2.5
        elif 2.5 < text_scale_factor:
            return 2

    def handling_braces(self, text):
        text_array_full = []
        if "{" in text or "}" in text:
            text_array = []
            text_parts = text.split("{")
            text_array.append(text_parts[0])
            for j in range(1, text_parts.__len__()):
                text_array.append("{")
                text_array.append(text_parts[j])
            for i in range(0, text_array.__len__()):
                if "}" in text_array[i]:
                    text_parts = text_array[i].split("}")
                    text_array_full.append(text_parts[0])
                    for j in range(1, text_parts.__len__()):
                        text_array_full.append("}")
                        text_array_full.append(text_parts[j])
                else:
                    text_array_full.append(text_array[i])
        else:
            text_array_full.append(text)
        text_array_full = list(filter(lambda
                                          a: a != '' and
                                             a != ' ' and
                                             a != '  ' and
                                             a != '   ' and
                                             a != '    ' and
                                             a != '     ' and
                                             a != '      ',
                                      text_array_full))
        return text_array_full
