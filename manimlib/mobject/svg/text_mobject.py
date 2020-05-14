import re
import os
import copy
import hashlib
import cairo
import manimlib.constants as consts
from manimlib.constants import *
from manimlib.container.container import Container
from manimlib.mobject.geometry import Dot, Rectangle
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.config_ops import digest_config


TEXT_MOB_SCALE_FACTOR = 0.05


class TextSetting(object):
    def __init__(self, start, end, font, slant, weight, line_num=-1):
        self.start = start
        self.end = end
        self.font = font
        self.slant = slant
        self.weight = weight
        self.line_num = line_num


class Text(SVGMobject):
    CONFIG = {
        # Mobject
        'color': consts.WHITE,
        'height': None,
        'width': None,
        'fill_opacity': 1,
        'stroke_width': 0,
        "should_center": True,
        "unpack_groups": True,
        # Text
        'font': '',
        'gradient': None,
        'lsh': -1,
        'size': 1,
        'slant': NORMAL,
        'weight': NORMAL,
        't2c': {},
        't2f': {},
        't2g': {},
        't2s': {},
        't2w': {},
        'tab_width': 4,
    }

    def __init__(self, text, **config):
        self.full2short(config)
        digest_config(self, config)
        text_without_tabs = text
        if text.find('\t') != -1:
            text_without_tabs = text.replace('\t', ' '*self.tab_width)
        self.text = text_without_tabs
        self.lsh = self.size if self.lsh == -1 else self.lsh

        file_name = self.text2svg()
        self.remove_last_M(file_name)
        SVGMobject.__init__(self, file_name, **config)
        self.apply_front_and_end_spaces()
        self.text = text
        self.apply_space_chars()

        nppc = self.n_points_per_cubic_curve
        for each in self:
            if len(each.points) == 0:
                continue
            points = each.points
            last = points[0]
            each.clear_points()
            for index, point in enumerate(points):
                each.append_points([point])
                if index != len(points) - 1 and (index + 1) % nppc == 0 and any(point != points[index+1]):
                    each.add_line_to(last)
                    last = points[index + 1]
            each.add_line_to(last)

        if self.t2c:
            self.set_color_by_t2c()
        if self.gradient:
            self.set_color_by_gradient(*self.gradient)
        if self.t2g:
            self.set_color_by_t2g()

        # anti-aliasing
        if self.height is None and self.width is None:
            self.scale(TEXT_MOB_SCALE_FACTOR)

    def get_space_width(self):
        size = self.size * 10

        dir_name = consts.TEXT_DIR
        file_name = os.path.join(dir_name, "space") + '.svg'

        surface = cairo.SVGSurface(file_name, 600, 400)
        context = cairo.Context(surface)
        context.set_font_size(size)
        context.move_to(START_X, START_Y)
        context.select_font_face(self.font, self.str2slant(self.slant), self.str2weight(self.weight))
        context.move_to(START_X, START_Y)
        context.show_text("_")
        surface.finish()
        svg_with_space = SVGMobject(file_name, height=self.height,
                                    width=self.width,
                                    stroke_width=self.stroke_width,
                                    should_center=self.should_center,
                                    unpack_groups=self.unpack_groups, )
        space_width = svg_with_space.get_width()
        return space_width

    def apply_front_and_end_spaces(self):
        space_width = self.get_space_width()
        max_height = self.get_height()
        front_spaces_count = 0
        i = -1
        for i in range(self.text.__len__()):
            if self.text[i] == " ":
                front_spaces_count += 1
                continue
            else:
                break
        first_visible_char_index = i
        if first_visible_char_index != 0:
            space = Rectangle(width=space_width * front_spaces_count, height=max_height, fill_opacity=0,
                                  stroke_opacity=0,
                                  stroke_width=0)
            text_width = self.get_width()
            space.move_to(np.array([-text_width / 2, max_height / 2, 0]))
            self.next_to(space, direction=RIGHT, buff=0)
            self.submobjects.insert(0, space)

        i = -1
        last_spaces_count = 0
        for i in range(self.text.__len__() - 1, -1, -1):
            if self.text[i] == " ":
                last_spaces_count += 1
                continue
            else:
                break
        last_visible_char_index = i
        if last_visible_char_index != self.text.__len__() - 1:
            space = Rectangle(width=space_width * last_spaces_count, height=max_height, fill_opacity=0,
                                  stroke_opacity=0,
                                  stroke_width=0)
            text_width = self.get_width()
            space.move_to(np.array([-text_width / 2, max_height / 2, 0]))
            self.next_to(space, direction=LEFT, buff=0)
            self.submobjects.append(space)
        self.move_to(np.array([0,0,0]))

    def apply_space_chars(self):
        char_index = 0
        while char_index < self.text.__len__() - 1:
            char_index += 1
            if self.text[char_index] == " " or self.text[char_index] == "\t" or self.text[char_index] == "\n":
                space = Dot(fill_opacity=0, stroke_opacity=0)
                space.move_to(self.submobjects[char_index - 1].get_center())
                self.submobjects.insert(char_index, space)

    def remove_last_M(self, file_name):
        with open(file_name, 'r') as fpr:
            content = fpr.read()
        content = re.sub(r'Z M [^A-Za-z]*? "\/>', 'Z "/>', content)
        with open(file_name, 'w') as fpw:
            fpw.write(content)

    def find_indexes(self, word):
        m = re.match(r'\[([0-9\-]{0,}):([0-9\-]{0,})\]', word)
        if m:
            start = int(m.group(1)) if m.group(1) != '' else 0
            end = int(m.group(2)) if m.group(2) != '' else len(self.text)
            start = len(self.text) + start if start < 0 else start
            end = len(self.text) + end if end < 0 else end
            return [(start, end)]

        indexes = []
        index = self.text.find(word)
        while index != -1:
            indexes.append((index, index + len(word)))
            index = self.text.find(word, index + len(word))
        return indexes

    def full2short(self, config):
        for kwargs in [config, self.CONFIG]:
            if kwargs.__contains__('line_spacing_height'):
                kwargs['lsh'] = kwargs.pop('line_spacing_height')
            if kwargs.__contains__('text2color'):
                kwargs['t2c'] = kwargs.pop('text2color')
            if kwargs.__contains__('text2font'):
                kwargs['t2f'] = kwargs.pop('text2font')
            if kwargs.__contains__('text2gradient'):
                kwargs['t2g'] = kwargs.pop('text2gradient')
            if kwargs.__contains__('text2slant'):
                kwargs['t2s'] = kwargs.pop('text2slant')
            if kwargs.__contains__('text2weight'):
                kwargs['t2w'] = kwargs.pop('text2weight')

    def set_color_by_t2c(self, t2c=None):
        t2c = t2c if t2c else self.t2c
        for word, color in list(t2c.items()):
            for start, end in self.find_indexes(word):
                self[start:end].set_color(color)

    def set_color_by_t2g(self, t2g=None):
        t2g = t2g if t2g else self.t2g
        for word, gradient in list(t2g.items()):
            for start, end in self.find_indexes(word):
                self[start:end].set_color_by_gradient(*gradient)

    def str2slant(self, string):
        if string == NORMAL:
            return cairo.FontSlant.NORMAL
        if string == ITALIC:
            return cairo.FontSlant.ITALIC
        if string == OBLIQUE:
            return cairo.FontSlant.OBLIQUE

    def str2weight(self, string):
        if string == NORMAL:
            return cairo.FontWeight.NORMAL
        if string == BOLD:
            return cairo.FontWeight.BOLD

    def text2hash(self):
        settings = self.font + self.slant + self.weight
        settings += str(self.t2f) + str(self.t2s) + str(self.t2w)
        settings += str(self.lsh) + str(self.size)
        id_str = self.text+settings
        hasher = hashlib.sha256()
        hasher.update(id_str.encode())
        return hasher.hexdigest()[:16]

    def text2settings(self):
        settings = []
        t2x = [self.t2f, self.t2s, self.t2w]
        for i in range(len(t2x)):
            fsw = [self.font, self.slant, self.weight]
            if t2x[i]:
                for word, x in list(t2x[i].items()):
                    for start, end in self.find_indexes(word):
                        fsw[i] = x
                        settings.append(TextSetting(start, end, *fsw))

        # Set All text settings(default font slant weight)
        fsw = [self.font, self.slant, self.weight]
        settings.sort(key=lambda setting: setting.start)
        temp_settings = settings.copy()
        start = 0
        for setting in settings:
            if setting.start != start:
                temp_settings.append(TextSetting(start, setting.start, *fsw))
            start = setting.end
        if start != len(self.text):
            temp_settings.append(TextSetting(start, len(self.text), *fsw))
        settings = sorted(temp_settings, key=lambda setting: setting.start)

        if re.search(r'\n', self.text):
            line_num = 0
            for start, end in self.find_indexes('\n'):
                for setting in settings:
                    if setting.line_num == -1:
                        setting.line_num = line_num
                    if start < setting.end:
                        line_num += 1
                        new_setting = copy.copy(setting)
                        setting.end = end
                        new_setting.start = end
                        new_setting.line_num = line_num
                        settings.append(new_setting)
                        settings.sort(key=lambda setting: setting.start)
                        break

        for setting in settings:
            if setting.line_num == -1:
                setting.line_num = 0

        return settings

    def text2svg(self):
        # anti-aliasing
        size = self.size * 10
        lsh = self.lsh * 10

        if self.font == '':
            if NOT_SETTING_FONT_MSG != '':
                print(NOT_SETTING_FONT_MSG)

        dir_name = consts.TEXT_DIR
        hash_name = self.text2hash()
        file_name = os.path.join(dir_name, hash_name)+'.svg'
        if os.path.exists(file_name):
            return file_name

        surface = cairo.SVGSurface(file_name, 600, 400)
        context = cairo.Context(surface)
        context.set_font_size(size)
        context.move_to(START_X, START_Y)

        settings = self.text2settings()
        offset_x = 0
        last_line_num = 0
        for setting in settings:
            font = setting.font
            slant = self.str2slant(setting.slant)
            weight = self.str2weight(setting.weight)
            text = self.text[setting.start:setting.end].replace('\n', ' ')

            context.select_font_face(font, slant, weight)
            if setting.line_num != last_line_num:
                offset_x = 0
                last_line_num = setting.line_num
            context.move_to(START_X + offset_x, START_Y + lsh*setting.line_num)
            context.show_text(text)
            offset_x += context.text_extents(text)[4]

        return file_name

class TextWithFixHeight(Text):
    def __init__(self, text, **kwargs):
        Text.__init__(self, text, **kwargs)
        max_height = Text("(gyt{[/QW", **kwargs).get_height()
        rectangle = Rectangle(width=0, height=max_height, fill_opacity=0,
                              stroke_opacity=0,
                              stroke_width=0)
        self.submobjects.append(rectangle)

class Paragraph(VGroup):
    CONFIG = {
        "line_spacing": 0.1,
        "alignment": "center",
    }

    def __init__(self, *text, **config):
        Container.__init__(self, **config)
        self.lines_list = list(text)
        self.lines = []
        self.lines.append([])
        for line_no in range(self.lines_list.__len__()):
            if "\n" in self.lines_list[line_no]:
                self.lines_list[line_no:line_no + 1] = self.lines_list[line_no].split("\n")
        for line_no in range(self.lines_list.__len__()):
            self.lines[0].append(TextWithFixHeight(self.lines_list[line_no], **config))
        self.char_height = TextWithFixHeight("(", **config).get_height()
        self.lines.append([])
        self.lines[1].extend([self.alignment for _ in range(self.lines_list.__len__())])
        self.lines[0][0].move_to(np.array([0, 0, 0]))
        self.align_lines()
        VGroup.__init__(self, *[self.lines[0][i] for i in range(self.lines[0].__len__())], **config)
        self.move_to(np.array([0, 0, 0]))

    def set_all_lines_alignment(self, alignment):
        self.lines[1] = [alignment for _ in range(self.lines_list.__len__())]
        for line_no in range(0, self.lines[0].__len__()):
            self.change_alignment_for_a_line(alignment, line_no)
        return self

    def set_alignment(self, alignment, line_no):
        self.change_alignment_for_a_line(alignment, line_no)
        return self

    def change_alignment_for_a_line(self, alignment, line_no):
        self.lines[1][line_no] = alignment
        if self.lines[1][line_no] == "center":
            self[line_no].move_to(self.get_top() +
                                  np.array([0, -self.char_height / 2, 0]) +
                                  np.array([0, - line_no * (self.char_height + self.line_spacing), 0]))
        elif self.lines[1][line_no] == "right":
            self[line_no].move_to(self.get_top() +
                                  np.array([0, -self.char_height / 2, 0]) +
                                  np.array([self.get_width() / 2 - self.lines[0][line_no].get_width() / 2,
                                            - line_no * (self.char_height + self.line_spacing), 0])
                                  )
        elif self.lines[1][line_no] == "left":
            self[line_no].move_to(self.get_top() +
                                  np.array([0, -self.char_height / 2, 0]) +
                                  np.array([- self.get_width() / 2 + self.lines[0][line_no].get_width() / 2,
                                            - line_no * (self.char_height + self.line_spacing), 0])
                                  )

    def align_lines(self):
        for line_no in range(0, self.lines[0].__len__()):
            if self.lines[1][line_no] == "center":
                self.lines[0][line_no].move_to(
                    np.array([0, 0, 0]) + np.array([0, - line_no * (self.char_height + self.line_spacing), 0]))
            elif self.lines[1][line_no] == "left":
                self.lines[0][line_no].move_to(np.array([0, 0, 0]) +
                                               np.array([self.lines[0][line_no].get_width() / 2,
                                                         - line_no * (self.char_height + self.line_spacing), 0])
                                               )
            elif self.lines[1][line_no] == "right":
                self.lines[0][line_no].move_to(np.array([0, 0, 0]) +
                                               np.array([- self.lines[0][line_no].get_width() / 2,
                                                         - line_no * (self.char_height + self.line_spacing), 0])
                                               )
