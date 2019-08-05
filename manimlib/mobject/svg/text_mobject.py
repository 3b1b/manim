import cairo
import copy
import hashlib
import re
import os
from manimlib.constants import *
from manimlib.mobject.svg.svg_mobject import SVGMobject
import manimlib.constants as consts


class TextStyle(object):
    def __init__(self, start, end, font, slant, weight, line_num=-1):
        self.start = start
        self.end = end
        self.font = font
        self.slant = slant
        self.weight = weight
        self.line_num = line_num


class Text(SVGMobject):
    '''
    Params:
    -------
    text ::
    a str, the space(' ') in front or back and '\\n' and '\\t' will be ignored
    
    Params(optional):
    -----------------
    color ::
    color defined in constants.py or a str like '#FFFFFF', default is WHITE
    
    font ::
    a str, the name of font like 'Source Han Sans', default is DEFAULT_FONT, defined in constants.py
    
    lsh (line_spacing_height) ::
    a number, better larger than 0.1(due to anti-aliasing), irrelevant with MUnit, default is DEFAULT_LSH

    size ::
    a number, better larger than 0.1(due to anti-aliasing), irrelevant with MUnit, default is DEFAULT_SIZE 
    
    slant ::
    NORMAL or ITALIC, default is NORMAL, defined in constants.py(a str actually)
    
    weight :: 
    NORMAL or BOLD, default is NORMAL, defined in constants.py(a str actually)
    
    fill_color ::
    the same as color
    
    fill_opacity ::
    a float, default is 1
    
    stroke_color ::
    the same as color
    
    storke_opacity ::
    a float
    
    t2c (text2color) ::
    a dict like {'text':color} or Accurate mode
    
    t2f (text2font) ::
    a dict like {'text':font} or Accurate mode
    
    t2s (text2slant) ::
    a dict like {'text':slant} or Accurate mode
    
    t2w (text2weight) ::
    a dict like {'text':weight} or Accurate mode
    
    Functions :
    -----------
    set_color(mobject function) ::
    param color, this will set the color of the whole text

    set_text_color ::
    param t2c, the same as the t2c mentioned above(require a dict!)

    Accurate mode:
    --------------
    This will help you to choose a specific text just like slicing, e.g. ::
    text = Text('ooo', t2c={'[:1]':RED, '[1:2]':GREEN, '[2:]':BLUE})

    btw, you can use '[[:]]' to represent the text '[:]'
    '''
    CONFIG = {
        "color": WHITE,
        "fill_opacity": 1,
        "height": None,
    }

    def __init__(self, text, **kwargs):
        self.text = text
        
        kwargs = self.full2short(**kwargs)
        file_name = self.text2svg(text, **kwargs)
        SVGMobject.__init__(self, file_name=file_name, **kwargs)
        if kwargs.__contains__('t2c'):
            self.text2color(text, **kwargs)
        #anti-aliasing
        self.scale(0.1)

    def full2short(self, **kwargs):
        if kwargs.__contains__('line_spacing_height'):
            kwargs['lsh'] = kwargs.pop('line_spacing_height')
        if kwargs.__contains__('text2color'):
            kwargs['t2c'] = kwargs.pop('text2color')
        if kwargs.__contains__('text2font'):
            kwargs['t2f'] = kwargs.pop('text2font')
        if kwargs.__contains__('text2slant'):
            kwargs['t2s'] = kwargs.pop('text2slant')
        if kwargs.__contains__('text2weight'):
            kwargs['t2w'] = kwargs.pop('text2weight')
        return kwargs

    def find_indexes(self, text, word):
        indexes = []
        if re.match(r'\[\[[0-9\-]{0,}:[0-9\-]{0,}\]\]', word):
            word = word[1:-1]
        index = text.find(word)
        while index != -1:
            indexes.append((index, index+len(word)))
            index = text.find(word, index+len(word))
        return indexes

    def find_strat_and_end(self, text, word):
        m = re.match(r'\[([0-9\-]{0,}):([0-9\-]{0,})\]', word)
        start = int(m.group(1)) if m.group(1) != '' else 0
        end = int(m.group(2)) if m.group(2) != '' else len(text)
        return (start, end)

    def is_slicing(self, word):
        m = re.match(r'\[[0-9\-]{0,}:[0-9\-]{0,}\]', word)
        return True if m else False

    def get_t2c_indexes(self, t2c):
        text = self.text
        length = len(text)
        t2c_indexes = []
        for word, color in list(t2c.items()):
            # accurate mode
            if self.is_slicing(word):
                start, end = self.find_strat_and_end(text, word)
                start = length + start if start < 0 else start
                end = length + end if end < 0 else end
                t2c_indexes.append((start, end, color))                
                continue
            for start, end in self.find_indexes(text, word):
                t2c_indexes.append((start, end, color))   
        return sorted(t2c_indexes, key=lambda i: i[1])                            

    def getfsw(self, **kwargs):
        font = kwargs['font'] if kwargs.__contains__('font') else DEFAULT_FONT
        slant = kwargs['slant'] if kwargs.__contains__('slant') else NORMAL
        weight = kwargs['weight'] if kwargs.__contains__('weight') else NORMAL
        return (font, slant, weight)

    def getxywh(self, text, font, slant, weight, size):
        dir_name = consts.TEXT_DIR
        file_name = os.path.join(dir_name, 'temp')+'.svg'

        temp_surface = cairo.SVGSurface(file_name, 1, 1)
        temp_context = cairo.Context(temp_surface)
        temp_context.set_font_size(size)
        if font != '':
            fs = self.str2slant(slant)
            fw = self.str2weight(weight)
            temp_context.select_font_face(font, fs, fw)
        x, y, w, h, dx, dy = temp_context.text_extents(text)
        return (x, y, w, h)

    def get_space_w(self, font, size):
        x1, y1, w1, h1 = self.getxywh('a', font, NORMAL, NORMAL, size)
        x2, y2, w2, h2, = self.getxywh('aa', font, NORMAL, NORMAL, size)
        return w2 - w1*2

    def has_multi_line(self, text):
        return True if re.search(r'\n', text) else False

    def set_text_color(self, t2c):
        self.text2color(self.text, t2c=t2c)
        
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

    def text2color(self, text, **kwargs):
        for word, color in list(kwargs['t2c'].items()):
            # accurate mode
            if self.is_slicing(word):
                start, end = self.find_strat_and_end(text, word)
                self[start:end].set_color(color)
                continue
            for start, end in self.find_indexes(text, word):
                self[start:end].set_color(color)

    def text2hash(self, text, **kwargs):
        ignores = [
            'color', 't2c', 
            'fill_color', 'fill_opacity', 
            'stroke_color', 'storke_opacity'
        ]
        for ignore in ignores:
            if kwargs.__contains__(ignore):
                kwargs.pop(ignore)

        id_str = text+str(kwargs)
        hasher = hashlib.sha256()
        hasher.update(id_str.encode())
        return hasher.hexdigest()[:16]

    def text2styles(self, text, **kwargs):
        styles = []
        f0, s0, w0 = self.getfsw(**kwargs)

        if kwargs.__contains__('t2f'):
            for word, font in list(kwargs['t2f'].items()):
                if self.is_slicing(word):
                    start, end = self.find_strat_and_end(text, word)
                    styles.append(TextStyle(start, end, font, s0, w0))
                for start, end in self.find_indexes(text, word):
                    styles.append(TextStyle(start, end, font, s0, w0))

        if kwargs.__contains__('t2s'):
            for word, slant in list(kwargs['t2s'].items()):
                if self.is_slicing(word):
                    start, end = self.find_strat_and_end(text, word)
                    styles.append(TextStyle(start, end, f0, slant, w0))
                for start, end in self.find_indexes(text, word):
                    styles.append(TextStyle(start, end, f0, slant, w0))

        if kwargs.__contains__('t2w'):
            for word, weight in list(kwargs['t2w'].items()):
                if self.is_slicing(word):
                    start, end = self.find_strat_and_end(text, word)
                    styles.append(TextStyle(start, end, f0, s0, weight))
                for start, end in self.find_indexes(text, word):
                    styles.append(TextStyle(start, end, f0, s0, weight))

        #Set All text styles(default font slant weight)
        styles = sorted(styles, key=lambda s: s.start)
        temp_styles = styles.copy()
        start = 0
        for style in styles:
            if style.start != start:
                temp_styles.append(TextStyle(start, style.start, f0, s0, w0))
            start = style.end
        if start != len(text):
            temp_styles.append(TextStyle(start, len(text), f0, s0, w0))
        styles = sorted(temp_styles, key=lambda s: s.start)

        if self.has_multi_line(text):
            line_num = 0
            for start, end in self.find_indexes(text, '\n'):
                for style in styles:
                    if style.line_num == -1:
                        style.line_num = line_num
                    if start < style.end:
                        line_num += 1
                        new_style = copy.copy(style)
                        style.end = end
                        new_style.start = end
                        new_style.line_num = line_num
                        styles.append(new_style)
                        styles = sorted(styles, key=lambda s: s.start)
                        break

        return styles

    def text2svg(self, text, **kwargs):
        font, slant, weight = self.getfsw(**kwargs)
        size = kwargs['size'] if kwargs.__contains__('size') else DEFAULT_SIZE
        lsh = kwargs['lsh'] if kwargs.__contains__('lsh') else DEFAULT_LSH
        #anti-aliasing
        size *= 10
        lsh *= 10

        if font == '':
            print(NOT_SETTING_FONT_MSG)

        dir_name = consts.TEXT_DIR
        hash_name = self.text2hash(text, **kwargs)
        file_name = os.path.join(dir_name, hash_name)+'.svg'
        if os.path.exists(file_name):
            return file_name

        text_surface = cairo.SVGSurface(file_name, 300, 200)
        text_context = cairo.Context(text_surface)
        text_context.set_font_size(size)
 
        styles = self.text2styles(text, **kwargs)
        last_width = 0
        last_ln = 0
        for style in styles:
            temp_text = text[style.start:style.end]
            sf = style.font
            ss = style.slant
            sw = style.weight
            sln = style.line_num if style.line_num != -1 else 0
            x1, y1, w1, h1 = self.getxywh(temp_text, sf, ss, sw, size)
            csf = self.str2slant(ss)
            csw = self.str2weight(sw)

            text_context.select_font_face(sf, csf, csw)
            if sln != last_ln:
                last_width = 0
                last_ln = sln
            text_context.move_to(last_width-x1, lsh*sln)
            text_context.show_text(temp_text)

            last_width += w1 + self.get_space_w(sf, size)

        return file_name
