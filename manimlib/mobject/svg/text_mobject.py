import re
import os
import copy
import hashlib
import cairo
import manimlib.constants as consts
from manimlib.constants import *
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_text_dir


TEXT_MOB_SCALE_FACTOR = 0.05


# Warning, these classes are currently based on an old rendering mode
# not supported in this version of manim

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
        'stroke_width': 0,
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
    }

    def __init__(self, text, **config):
        self.text = text
        self.full2short(config)
        digest_config(self, config)
        self.lsh = self.size if self.lsh == -1 else self.lsh

        file_name = self.text2svg()
        SVGMobject.__init__(self, file_name, **config)

        if self.t2c:
            self.set_color_by_t2c()
        if self.gradient:
            self.set_color_by_gradient(*self.gradient)
        if self.t2g:
            self.set_color_by_t2g()

        # anti-aliasing
        if self.height is None:
            self.scale(TEXT_MOB_SCALE_FACTOR)

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
            print(NOT_SETTING_FONT_MSG)

        dir_name = get_text_dir()
        hash_name = self.text2hash()
        file_name = os.path.join(dir_name, hash_name) +'.svg'
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
            context.move_to(START_X + offset_x, START_Y + lsh * setting.line_num)
            context.show_text(text)
            offset_x += context.text_extents(text)[4]

        return file_name
