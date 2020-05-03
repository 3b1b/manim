import html
from manimlib.constants import *
from manimlib.container.container import Container
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VGroup


class CodeMobject(VGroup):
    CONFIG = {
        "tab_spacing": 0.4,
        "line_spacing": 0.1,
        "coordinates": [0, 0],
        "scale_factor": 0.5,
        "run_time": 1,
        "font":'Monospac821 BT',
        'stroke_width':0,
        'indentation_char':"  "
    }

    def __init__(self, file_name=None, **kwargs):
        Container.__init__(self, **kwargs)
        self.file_name = file_name or self.file_name
        self.ensure_valid_file()
        self.gen_code_json()
        self.temp_char = Text("(").scale(self.scale_factor)
        self.code_json_to_mobject_array()
        VGroup.__init__(self, *[self.lines[i] for i in range(self.lines.__len__())], **kwargs)


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
            os.path.join(os.path.join("assets", "codes"), self.file_name),
            os.path.join(os.path.join("assets", "codes"), self.file_name + ".html"),
            os.path.join(os.path.join("assets", "codes"), self.file_name + ".htm"),
            os.path.join(os.path.join("assets", "codes"), self.file_name + ".HTML"),
            os.path.join(os.path.join("assets", "codes"), self.file_name + ".HTM"),
            self.file_name,
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.file_path = path
                return
        raise IOError("No file matching %s in codes directory" %
                      self.file_name)


    def code_json_to_mobject_array(self):
        self.lines = []
        for line_no in range(0, self.code_json.__len__()):
            line_str = ""
            for word_index in range(self.code_json[line_no].__len__()):
                line_str = line_str + self.code_json[line_no][word_index][0]
            line = Text(line_str,font=self.font, stroke_width=self.stroke_width).scale(self.scale_factor)
            line_char_index = 0
            for word_index in range(self.code_json[line_no].__len__()):
                for char_index in range(self.code_json[line_no][word_index][0].__len__()):
                    if self.code_json[line_no][word_index][0][char_index] != " ":
                        line[line_char_index].set_color(self.code_json[line_no][word_index][1])
                        line_char_index = line_char_index +1
            if line_no == 0:
                line.move_to(
                    np.array([self.coordinates[0], self.coordinates[1], 0]) +
                    np.array([line.get_width() / 2, 0, 0]) +
                    RIGHT * self.tab_spaces[line_no] * self.tab_spacing)
            else:
                line.move_to(
                    np.array([self.coordinates[0], self.coordinates[1], 0]) +
                    np.array([line.get_width() / 2, 0, 0]) +
                    DOWN * line_no * (self.temp_char.get_height() + self.line_spacing) +
                    RIGHT * (self.tab_spaces[line_no] * self.tab_spacing))
            self.lines.append(line)


    def gen_code_json(self):
        file = open(self.file_path, "r")
        html_string = file.read()
        for i in range(10, -1, -1):
            html_string = html_string.replace("</" + " " * i,"</")
        file.close()
        html_space_index = html_string.find("&#xa0;")
        str1 = html_string[0:html_space_index]
        str1 = str1[0:-31] + "\n"
        str3 = html_string[html_space_index:]
        end_point = str3.find("</span")
        str2 = ""
        html_spaces_count = int(end_point / 6)
        for k in range(0, html_spaces_count):
            str2 += " "
        str3 = str3[end_point + 7:]
        html_string = str1 + str2 + str3
        for i in range(10, -1, -1):
            html_string = html_string.replace("</span>" + " " * i, " " * i + "</span>")
        html_string = html_string.replace("#40015a", "#e1a8ff")
        lines = html_string.split("</span>")
        html_string = lines[0] + "</span>"
        for i in range(1, lines.__len__()):
            j = lines[i].find("<span")
            temp = ""
            starti = -1
            for k in range(0, j):
                if (lines[i][k] == "\n" or lines[i][k] == " ") and starti == -1:
                    continue
                else:
                    if starti == -1: starti = k
                    temp = temp + lines[i][k]
            if temp != "":
                temp = lines[i][0:starti]
                temp = temp + '<span style="color:#ffffff;">' + lines[i][starti:j] + "</span>"
                temp = temp + lines[i][j:]
                lines[i] = temp
            html_string = html_string + lines[i] + "</span>"
        lines = html_string.split("\n")
        end_point = lines.index("</pre>")
        lines = lines[0:end_point]
        start_point = lines[0].find(">")
        lines[0] = lines[0][start_point + 1:]
        code_json = []
        tab_spaces = []
        code_json_line_index = -1
        for line_index in range(0, lines.__len__()):
            if lines[line_index].__len__() == 0:
                continue
            code_json.append([])
            code_json_line_index = code_json_line_index + 1
            if lines[line_index].startswith(self.indentation_char):
                start_point = lines[line_index].find("<")
                lines[line_index] = "\t" * lines[line_index][:start_point].count(self.indentation_char) + lines[line_index][start_point:]
            indentation_char_count = 0
            while lines[line_index][indentation_char_count] == '\t':
                indentation_char_count = indentation_char_count + 1
            tab_spaces.append(indentation_char_count)
            words=lines[line_index].split("<span")
            for word_index in range(1,words.__len__()):
                color_index = words[word_index].find(":")
                color = words[word_index][color_index+1:color_index+8]
                start_point=words[word_index].find(">")
                end_point=words[word_index].find("</span>")
                text = words[word_index][start_point+1:end_point]
                text = html.unescape(text)
                code_json[code_json_line_index].append([text, color])
        self.code_json = code_json
        self.tab_spaces = tab_spaces
