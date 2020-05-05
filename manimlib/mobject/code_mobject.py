import html
from manimlib.constants import *
from manimlib.container.container import Container
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VGroup

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter

'''
Creates a three things
codemobject[0] is codemobject.background_rect 
    which is a Rectangle()
codemobject[1] is codemobject.line_numbers
    Which is a VGroup() of Text() objects with line numbers as a text, this mean you can use 
        codemobject.line_numbers[0] or codemobject[1][0] to access first line number 
codemobject[2] is codemobject.code
    Which is a VGroup() of lines with color highlighted, this mean you can use 
        codemobject.code[1] or codemobject[2][1] 
            line number 1
        codemobject.code[1][0] or codemobject.code[1][0] 
            first character of line number 1
        codemobject.code[1][0:5] or codemobject.code[1][0:5] 
            first five characters of line number 1
            
NOTE : " " spaces are not counted in Text() object
for example if line number 5 of code is "c = a+b" then 
            codemobject.code[5][1] -> c
            codemobject.code[5][2] -> =
            codemobject.code[5][3] -> a
            codemobject.code[5][4] -> +
            codemobject.code[5][5] -> a
            codemobject.code[5][6] -> b
'''

class CodeMobject(VGroup):
    CONFIG = {
        "tab_spacing": 0.4,
        "line_spacing": 0.1,
        "coordinates": [0, 0],
        "scale_factor": 0.5,
        "run_time": 1,
        "font": 'Monospac821 BT',
        'stroke_width': 0,
        'margin': 0.3,
        'indentation_char': "  ",
        'insert_line_no': True,
        'line_no_from': 1,
        'style': 'vim',
        'language': 'cpp',
        'generate_html_file': False
    }

    def __init__(self, file_name=None, **kwargs):
        Container.__init__(self, **kwargs)
        self.file_name = file_name or self.file_name
        self.ensure_valid_file()
        self.style = self.style.lower()
        self.gen_html_string()
        strati = self.html_string.find("background:")
        self.background_color = self.html_string[strati + 12:strati + 19]
        self.gen_code_json()
        self.temp_char = Text("(").scale(self.scale_factor)

        if self.insert_line_no:
            self.gen_line_numbers()
            self.line_numbers = VGroup(
                *[self.line_numbers_array[i] for i in range(self.line_numbers_array.__len__())])

        self.gen_colored_lines()
        self.code = VGroup(*[self.lines[i] for i in range(self.lines.__len__())])
        if self.insert_line_no:
            rectw = VGroup(self.code, self.line_numbers).get_width() + (self.margin * 2)
        else:
            rectw = self.code.get_width() + (self.margin * 2)

        recth = self.code.get_height() + (self.margin * 2)
        self.background_rect = Rectangle(height=recth,
                                         width=rectw,
                                         color=self.background_color,
                                         fill_color=self.background_color,
                                         stroke_width=0,
                                         fill_opacity=1, )
        self.background_rect.move_to(np.array([self.coordinates[0], self.coordinates[1], 0]) +
                                     np.array([self.background_rect.get_width() / 2, 0, 0]) -
                                     np.array([0, self.background_rect.get_height() / 2, 0]) +
                                     np.array([0, self.temp_char.get_height() / 2, 0])
                                     )

        if self.insert_line_no:
            VGroup.__init__(self, self.background_rect, self.line_numbers, *self.code, **kwargs)
        else:
            VGroup.__init__(self, self.background_rect, *self.code, **kwargs)

    def apply_points_function_about_point(self, func, about_point=None, about_edge=None):
        if about_point is None:
            if about_edge is None:
                about_edge = self.get_corner(UP + LEFT)
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
            os.path.join(os.path.join("assets", "codes"), self.file_name),
            self.file_name,
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.file_path = path
                return
        raise IOError("No file matching %s in codes directory" %
                      self.file_name)

    def gen_line_numbers(self):
        self.line_numbers_array = []
        last_number = self.line_no_from + self.code_json.__len__()
        max_len = str(last_number).__len__()
        for line_no in range(0, self.code_json.__len__()):
            number = Text(("{:0" + str(max_len) + "d}").format(self.line_no_from + line_no), font=self.font,
                          stroke_width=self.stroke_width).scale(self.scale_factor)
            number_len = str(self.line_no_from + line_no).__len__()
            # print(("'{:0" + str(max_len) + "d}'").format(self.line_no_from + line_no))
            for char_index in range(max_len - 1, max_len - number_len - 1, -1):
                number[char_index].set_color(self.default_color)
            if line_no == 0:
                number.move_to(
                    np.array([self.coordinates[0], self.coordinates[1], 0]) +
                    np.array([number.get_width() / 2, 0, 0]) +
                    RIGHT * self.margin +
                    DOWN * self.margin
                )
            else:
                number.move_to(
                    np.array([self.coordinates[0], self.coordinates[1], 0]) +
                    np.array([number.get_width() / 2, 0, 0]) +
                    DOWN * line_no * (self.temp_char.get_height() + self.line_spacing) +
                    RIGHT * self.margin +
                    DOWN * self.margin
                )
            self.line_numbers_array.append(number)

    def gen_colored_lines(self):
        self.lines = []
        for line_no in range(0, self.code_json.__len__()):
            line_str = ""
            for word_index in range(self.code_json[line_no].__len__()):
                line_str = line_str + self.code_json[line_no][word_index][0]
            line = Text(line_str, font=self.font, stroke_width=self.stroke_width).scale(self.scale_factor)
            line_char_index = 0
            for word_index in range(self.code_json[line_no].__len__()):
                for char_index in range(self.code_json[line_no][word_index][0].__len__()):
                    if self.code_json[line_no][word_index][0][char_index] != " ":
                        line[line_char_index].set_color(self.code_json[line_no][word_index][1])
                        line_char_index = line_char_index + 1
            if self.insert_line_no:
                if line_no == 0:
                    line.move_to(np.array([self.coordinates[0], self.coordinates[1], 0]) +
                                 np.array(
                                     [self.line_numbers_array[line_no].get_width() + self.temp_char.get_width() * 5, 0,
                                      0]) +
                                 np.array([line.get_width() / 2, 0, 0]) +
                                 RIGHT * self.tab_spaces[line_no] * self.tab_spacing +
                                 RIGHT * self.margin +
                                 DOWN * self.margin
                                 )

                else:
                    line.move_to(np.array([self.coordinates[0], self.coordinates[1], 0]) +
                                 np.array(
                                     [self.line_numbers_array[line_no].get_width() + self.temp_char.get_width() * 5, 0,
                                      0]) +
                                 np.array([line.get_width() / 2, 0, 0]) +
                                 DOWN * line_no * (self.temp_char.get_height() + self.line_spacing) +
                                 RIGHT * (self.tab_spaces[line_no] * self.tab_spacing) +
                                 RIGHT * self.margin +
                                 DOWN * self.margin
                                 )
            else:
                if line_no == 0:
                    line.move_to(
                        np.array([self.coordinates[0], self.coordinates[1], 0]) +
                        np.array([line.get_width() / 2, 0, 0]) +
                        RIGHT * self.tab_spaces[line_no] * self.tab_spacing +
                        RIGHT * self.margin +
                        DOWN * self.margin
                    )
                else:
                    line.move_to(
                        np.array([self.coordinates[0], self.coordinates[1], 0]) +
                        np.array([line.get_width() / 2, 0, 0]) +
                        DOWN * line_no * (self.temp_char.get_height() + self.line_spacing) +
                        RIGHT * (self.tab_spaces[line_no] * self.tab_spacing) +
                        RIGHT * self.margin +
                        DOWN * self.margin
                    )
            self.lines.append(line)

    def gen_html_string(self):
        file = open(self.file_path, "r")
        code_str = file.read()
        file.close()
        self.html_string = hilite_me(code_str, self.language, {}, self.style, self.insert_line_no,
                                     "border:solid gray;border-width:.1em .1em .1em .8em;padding:.2em .6em;")
        if self.generate_html_file:
            os.makedirs(os.path.join("assets", "codes", "generated_html_files"), exist_ok=True)
            file = open(os.path.join("assets", "codes", "generated_html_files", self.file_name + ".html"), "w")
            file.write(self.html_string)
            file.close()

    def gen_code_json(self):
        if self.background_color == "#111111" or \
                self.background_color == "#272822" or \
                self.background_color == "#202020" or \
                self.background_color == "#000000":
            self.default_color = "#ffffff"
        else:
            self.default_color = "#000000"
        for i in range(3, -1, -1):
            self.html_string = self.html_string.replace("</" + " " * i, "</")
        for i in range(10, -1, -1):
            self.html_string = self.html_string.replace("</span>" + " " * i, " " * i + "</span>")
        self.html_string = self.html_string.replace("background-color:", "background:")

        if self.insert_line_no:
            start_point = self.html_string.find("</td><td><pre")
            start_point = start_point + 9
        else:
            start_point = self.html_string.find("<pre")
        self.html_string = self.html_string[start_point:]
        # print(self.html_string)
        lines = self.html_string.split("\n")
        lines = lines[0:lines.__len__() - 2]
        start_point = lines[0].find(">")
        lines[0] = lines[0][start_point + 1:]
        # print(lines)
        self.code_json = []
        self.tab_spaces = []
        code_json_line_index = -1
        for line_index in range(0, lines.__len__()):
            if lines[line_index].__len__() == 0:
                continue
            # print(lines[line_index])
            self.code_json.append([])
            code_json_line_index = code_json_line_index + 1
            if lines[line_index].startswith(self.indentation_char):
                start_point = lines[line_index].find("<")
                starting_string = lines[line_index][:start_point]
                indentation_char_count = lines[line_index][:start_point].count(self.indentation_char)
                if starting_string.__len__() != indentation_char_count * self.indentation_char.__len__():
                    lines[line_index] = "\t" * indentation_char_count + starting_string[starting_string.rfind(
                        self.indentation_char) + self.indentation_char.__len__():] + \
                                        lines[line_index][start_point:]
                else:
                    lines[line_index] = "\t" * indentation_char_count + lines[line_index][start_point:]

            indentation_char_count = 0
            while lines[line_index][indentation_char_count] == '\t':
                indentation_char_count = indentation_char_count + 1
            self.tab_spaces.append(indentation_char_count)
            # print(lines[line_index])
            lines[line_index] = self.correct_non_span(lines[line_index])
            # print(lines[line_index])
            words = lines[line_index].split("<span")
            for word_index in range(1, words.__len__()):
                color_index = words[word_index].find("color:")
                if color_index == -1:
                    color = self.default_color
                else:
                    starti = words[word_index][color_index:].find("#")
                    color = words[word_index][color_index + starti:color_index + starti + 7]

                start_point = words[word_index].find(">")
                end_point = words[word_index].find("</span>")
                text = words[word_index][start_point + 1:end_point]
                text = html.unescape(text)
                if text != "":
                    # print(text, "'" + color + "'")
                    self.code_json[code_json_line_index].append([text, color])
        # print(self.code_json)

    def correct_non_span(self, line_str):
        words = line_str.split("</span>")
        line_str = ""
        for i in range(0, words.__len__()):
            if i != words.__len__() - 1:
                j = words[i].find("<span")
            else:
                j = words[i].__len__()
            temp = ""
            starti = -1
            for k in range(0, j):
                if words[i][k] == "\t" and starti == -1:
                    continue
                else:
                    if starti == -1: starti = k
                    temp = temp + words[i][k]
            if temp != "":
                if i != words.__len__() - 1:
                    temp = '<span style="color:' + self.default_color + '">' + words[i][starti:j] + "</span>"
                else:
                    temp = '<span style="color:' + self.default_color + '">' + words[i][starti:j]
                temp = temp + words[i][j:]
                words[i] = temp
            if words[i] != "":
                line_str = line_str + words[i] + "</span>"
        return line_str


def hilite_me(code, lexer, options, style, linenos, divstyles):
    lexer = lexer or 'python'
    style = style or 'colorful'
    defstyles = 'overflow:auto;width:auto;'

    formatter = HtmlFormatter(style=style,
                              linenos=False,
                              noclasses=True,
                              cssclass='',
                              cssstyles=defstyles + divstyles,
                              prestyles='margin: 0')
    html = highlight(code, get_lexer_by_name(lexer, **options), formatter)
    if linenos:
        html = insert_line_numbers(html)
    html = "<!-- HTML generated using hilite.me -->" + html
    return html


def get_default_style():
    return 'border:solid gray;border-width:.1em .1em .1em .8em;padding:.2em .6em;'


def insert_line_numbers(html):
    match = re.search('(<pre[^>]*>)(.*)(</pre>)', html, re.DOTALL)
    if not match: return html

    pre_open = match.group(1)
    pre = match.group(2)
    pre_close = match.group(3)

    html = html.replace(pre_close, '</pre></td></tr></table>')
    numbers = range(1, pre.count('\n') + 1)
    format = '%' + str(len(str(numbers[-1]))) + 'i'
    lines = '\n'.join(format % i for i in numbers)
    html = html.replace(pre_open, '<table><tr><td>' + pre_open + lines + '</pre></td><td>' + pre_open)
    return html
