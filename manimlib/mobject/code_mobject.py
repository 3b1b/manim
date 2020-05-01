import html
import os
import numpy as np
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
        'stroke_width':0
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


    def code_json_to_mobject_array(self):
        self.lines = []
        for line_no in range(0, self.code_json.__len__()):
            #print([self.code_json[line_no][j][0] for j in range(self.code_json[line_no].__len__())])
            line_chars_list = []
            for j in range(self.code_json[line_no].__len__()):
                for k in range(self.code_json[line_no][j][0].__len__()):
                    line_chars_list.append(self.code_json[line_no][j][0][k])
            line = Text(*line_chars_list,font=self.font, stroke_width=self.stroke_width).scale(self.scale_factor)
            m = 0
            for j in range(self.code_json[line_no].__len__()):
                for k in range(self.code_json[line_no][j][0].__len__()):
                    line[m].set_color(self.code_json[line_no][j][1])
                    m = m +1
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
        i = html_string.find("&#xa0;")
        str1 = html_string[0:i]
        str1 = str1[0:-31] + "" \
                             "\n"
        str3 = html_string[i:]
        j = str3.find("</span")
        str2 = ""
        for k in range(0, int(j / 6)):
            str2 += " "
        str3 = str3[j + 7:]
        html_string = str1 + str2 + str3
        for i in range(10, -1, -1):
            html_string = html_string.replace("</span>" + " " * i, " " * i + "</span>")
        html_string = html_string.replace("#40015a", "#e1a8ff")
        st = html_string.split("</span>")
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
        html_string = str
        lines = html_string.split("\n")
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
            count = 0
            while lines[i][count] == '\t':
                count = count + 1
            tab_spaces.append(count)
            spans=lines[i].split("<span")
            for j in range(1,spans.__len__()):
                k1 = spans[j].find(":")
                color = spans[j][k1+1:k1+8]
                k1=spans[j].find(">")
                k2=spans[j].find("</span>")
                text = spans[j][k1+1:k2]
                text = html.unescape(text)
                code_json[k].append([text, color])
        self.code_json = code_json
        self.tab_spaces = tab_spaces
