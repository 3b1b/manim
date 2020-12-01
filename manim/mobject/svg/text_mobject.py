"""Mobjects used for displaying (non-LaTeX) text.

The simplest way to add text to your animations is to use the :class:`~.Text` class. It uses the Pango library to render text.
With Pango, you are also able to render non-English alphabets like `你好` or  `こんにちは` or `안녕하세요` or `مرحبا بالعالم`.

Examples
--------

.. manim:: HelloWorld
    :save_last_frame:

    class HelloWorld(Scene):
        def construct(self):
            text = Text('Hello world').scale(3)
            self.add(text)

.. manim:: TextAlignement
    :save_last_frame:

    class TextAlignement(Scene):
        def construct(self):
            title = Text("K-means clustering and Logistic Regression", color=WHITE)
            title.scale_in_place(0.75)
            self.add(title.to_edge(UP))

            t1 = Text("1. Measuring").set_color(WHITE)
            t1.next_to(ORIGIN, direction=RIGHT, aligned_edge=UP)

            t2 = Text("2. Clustering").set_color(WHITE)
            t2.next_to(t1, direction=DOWN, aligned_edge=LEFT)

            t3 = Text("3. Regression").set_color(WHITE)
            t3.next_to(t2, direction=DOWN, aligned_edge=LEFT)

            t4 = Text("4. Prediction").set_color(WHITE)
            t4.next_to(t3, direction=DOWN, aligned_edge=LEFT)

            x = VGroup(t1, t2, t3, t4).scale_in_place(0.7)
            x.set_opacity(0.5)
            x.submobjects[1].set_opacity(1)
            self.add(x)

"""

__all__ = ["Text", "Paragraph", "CairoText"]


import copy
import hashlib
import os
import re

import cairo
import cairocffi
import pangocairocffi
import pangocffi

from ... import config, logger
from ...constants import *
from ...mobject.geometry import Dot
from ...mobject.svg.svg_mobject import SVGMobject
from ...mobject.types.vectorized_mobject import VGroup
from ...utils.config_ops import digest_config
from ...utils.color import WHITE

TEXT_MOB_SCALE_FACTOR = 0.05


def remove_invisible_chars(mobject):
    """Function to remove unwanted invisible characters from some mobject

    Parameters
    ----------
    mobject : :class:`~.SVGMobject`
        Any SVGMobject from which we want to remove unwanted invisible characters.

    Returns
    -------
    :class:`~.SVGMobject`
        The SVGMobject without unwanted invisible characters.
    """

    iscode = False
    if mobject.__class__.__name__ == "Text":
        mobject = mobject[:]
    elif mobject.__class__.__name__ == "Code":
        iscode = True
        code = mobject
        mobject = mobject.code
    mobject_without_dots = VGroup()
    if mobject[0].__class__ == VGroup:
        for i in range(mobject.__len__()):
            mobject_without_dots.add(VGroup())
            mobject_without_dots[i].add(*[k for k in mobject[i] if k.__class__ != Dot])
    else:
        mobject_without_dots.add(*[k for k in mobject if k.__class__ != Dot])
    if iscode:
        code.code = mobject_without_dots
        return code
    return mobject_without_dots


class TextSetting(object):
    def __init__(self, start, end, font, slant, weight, line_num=-1):
        self.start = start
        self.end = end
        self.font = font
        self.slant = slant
        self.weight = weight
        self.line_num = line_num


class CairoText(SVGMobject):
    """Display (non-LaTeX) text.

    Text objects behave like a :class:`.VGroup`-like iterable of all characters
    in the given text. In particular, slicing is possible.



    .. WARNING::

        Using a :class:`.Transform` on text with leading whitespace can look
        `weird <https://github.com/3b1b/manim/issues/1067>`_. Consider using
        :meth:`remove_invisible_chars` to resolve this issue.

    Tests
    -----

    Check whether writing text works::

        >>> Text('The horse does not eat cucumber salad.')
        Text('The horse does not eat cucumber salad.')

    """

    CONFIG = {
        # Mobject
        "color": WHITE,
        "height": None,
        "width": None,
        "fill_opacity": 1,
        "stroke_width": 0,
        "should_center": True,
        "unpack_groups": True,
        # Text
        "font": "",
        "gradient": None,
        "line_spacing": -1,
        "size": 1,
        "slant": NORMAL,
        "weight": NORMAL,
        "t2c": {},
        "t2f": {},
        "t2g": {},
        "t2s": {},
        "t2w": {},
        "tab_width": 4,
    }

    def __init__(self, text, **config):
        self.full2short(config)
        digest_config(self, config)
        self.original_text = text
        text_without_tabs = text
        if text.find("\t") != -1:
            text_without_tabs = text.replace("\t", " " * self.tab_width)
        self.text = text_without_tabs
        if self.line_spacing == -1:
            self.line_spacing = self.size + self.size * 0.3
        else:
            self.line_spacing = self.size + self.size * self.line_spacing
        file_name = self.text2svg()
        self.remove_last_M(file_name)
        SVGMobject.__init__(self, file_name, **config)
        self.text = text
        self.submobjects = [*self.gen_chars()]
        self.chars = VGroup(*self.submobjects)
        self.text = text_without_tabs.replace(" ", "").replace("\n", "")
        nppc = self.n_points_per_cubic_curve
        for each in self:
            if len(each.points) == 0:
                continue
            points = each.points
            last = points[0]
            each.clear_points()
            for index, point in enumerate(points):
                each.append_points([point])
                if (
                    index != len(points) - 1
                    and (index + 1) % nppc == 0
                    and any(point != points[index + 1])
                ):
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

    def __repr__(self):
        return f"Text({repr(self.original_text)})"

    def gen_chars(self):
        chars = VGroup()
        submobjects_char_index = 0
        for char_index in range(self.text.__len__()):
            if (
                self.text[char_index] == " "
                or self.text[char_index] == "\t"
                or self.text[char_index] == "\n"
            ):
                space = Dot(redius=0, fill_opacity=0, stroke_opacity=0)
                if char_index == 0:
                    space.move_to(self.submobjects[submobjects_char_index].get_center())
                else:
                    space.move_to(
                        self.submobjects[submobjects_char_index - 1].get_center()
                    )
                chars.add(space)
            else:
                chars.add(self.submobjects[submobjects_char_index])
                submobjects_char_index += 1
        return chars

    def remove_last_M(self, file_name):
        with open(file_name, "r") as fpr:
            content = fpr.read()
        content = re.sub(r'Z M [^A-Za-z]*? "\/>', 'Z "/>', content)
        with open(file_name, "w") as fpw:
            fpw.write(content)

    def find_indexes(self, word, text):
        m = re.match(r"\[([0-9\-]{0,}):([0-9\-]{0,})\]", word)
        if m:
            start = int(m.group(1)) if m.group(1) != "" else 0
            end = int(m.group(2)) if m.group(2) != "" else len(text)
            start = len(text) + start if start < 0 else start
            end = len(text) + end if end < 0 else end
            return [(start, end)]
        indexes = []
        index = text.find(word)
        while index != -1:
            indexes.append((index, index + len(word)))
            index = text.find(word, index + len(word))
        return indexes

    def full2short(self, config):
        for kwargs in [config, self.CONFIG]:
            if kwargs.__contains__("text2color"):
                kwargs["t2c"] = kwargs.pop("text2color")
            if kwargs.__contains__("text2font"):
                kwargs["t2f"] = kwargs.pop("text2font")
            if kwargs.__contains__("text2gradient"):
                kwargs["t2g"] = kwargs.pop("text2gradient")
            if kwargs.__contains__("text2slant"):
                kwargs["t2s"] = kwargs.pop("text2slant")
            if kwargs.__contains__("text2weight"):
                kwargs["t2w"] = kwargs.pop("text2weight")

    def set_color_by_t2c(self, t2c=None):
        t2c = t2c if t2c else self.t2c
        for word, color in list(t2c.items()):
            for start, end in self.find_indexes(word, self.original_text):
                self.chars[start:end].set_color(color)

    def set_color_by_t2g(self, t2g=None):
        t2g = t2g if t2g else self.t2g
        for word, gradient in list(t2g.items()):
            for start, end in self.find_indexes(word, self.original_text):
                self.chars[start:end].set_color_by_gradient(*gradient)

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
        settings += str(self.line_spacing) + str(self.size)
        id_str = self.text + settings
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
                    for start, end in self.find_indexes(word, self.text):
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

        if re.search(r"\n", self.text):
            line_num = 0
            for start, end in self.find_indexes("\n", self.text):
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
        line_spacing = self.line_spacing * 10

        if self.font == "":
            if NOT_SETTING_FONT_MSG:
                logger.warning(NOT_SETTING_FONT_MSG)

        dir_name = config.get_dir("text_dir")
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        hash_name = self.text2hash()
        file_name = os.path.join(dir_name, hash_name) + ".svg"
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
            text = self.text[setting.start : setting.end].replace("\n", " ")

            context.select_font_face(font, slant, weight)
            if setting.line_num != last_line_num:
                offset_x = 0
                last_line_num = setting.line_num
            context.move_to(
                START_X + offset_x, START_Y + line_spacing * setting.line_num
            )
            context.show_text(text)
            offset_x += context.text_extents(text)[4]
        surface.finish()
        return file_name


class Paragraph(VGroup):
    r"""Display a paragraph of text.

    For a given :class:`.Paragraph` ``par``, the attribute ``par.chars`` is a
    :class:`.VGroup` containing all the lines. In this context, every line is
    constructed as a :class:`.VGroup` of characters contained in the line.

    .. WARNING::

        Using a :class:`.Transform` on text with leading whitespace can look
        `weird <https://github.com/3b1b/manim/issues/1067>`_. Consider using
        :meth:`remove_invisible_chars` to resolve this issue.

    .. note::

        Due to issues with the Pango-powered :class:`.Text`, this class uses
        :class:`.CairoText`.

    Parameters
    ----------
    line_spacing : :class:`int`, optional
        Represents the spaning betweeb lines. Default to -1, which means auto.
    alignment : :class:`str`, optional
        Defines the alignment of paragraph. Default to "left". Possible values are "left", "right", "center"

    Examples
    --------
    Normal usage::

        paragraph = Paragraph('this is a awesome', 'paragraph',
                              'With \nNewlines', '\tWith Tabs',
                              '  With Spaces', 'With Alignments',
                              'center', 'left', 'right')

    Remove unwanted invisible characters::

        self.play(Transform(remove_invisible_chars(paragraph.chars[0:2]),
                            remove_invisible_chars(paragraph.chars[3][0:3]))

    """

    CONFIG = {
        "line_spacing": -1,
        "alignment": None,
    }

    def __init__(self, *text, **config):
        VGroup.__init__(self, **config)

        lines_str = "\n".join(list(text))
        self.lines_text = CairoText(lines_str, **config)
        lines_str_list = lines_str.split("\n")
        self.chars = self.gen_chars(lines_str_list)

        chars_lines_text_list = VGroup()
        char_index_counter = 0
        for line_index in range(lines_str_list.__len__()):
            chars_lines_text_list.add(
                self.lines_text[
                    char_index_counter : char_index_counter
                    + lines_str_list[line_index].__len__()
                    + 1
                ]
            )
            char_index_counter += lines_str_list[line_index].__len__() + 1
        self.lines = []
        self.lines.append([])
        for line_no in range(chars_lines_text_list.__len__()):
            self.lines[0].append(chars_lines_text_list[line_no])
        self.lines_initial_positions = []
        for line_no in range(self.lines[0].__len__()):
            self.lines_initial_positions.append(self.lines[0][line_no].get_center())
        self.lines.append([])
        self.lines[1].extend(
            [self.alignment for _ in range(chars_lines_text_list.__len__())]
        )
        VGroup.__init__(
            self, *[self.lines[0][i] for i in range(self.lines[0].__len__())], **config
        )
        self.move_to(np.array([0, 0, 0]))
        if self.alignment:
            self.set_all_lines_alignments(self.alignment)

    def gen_chars(self, lines_str_list):
        """Function to convert plain string to 2d-VGroup of chars. 2d-VGroup mean "VGroup of VGroup".

        Parameters
        ----------
        lines_str_list : :class:`str`
            Plain text string.

        Returns
        -------
        :class:`~.VGroup`
            The generated 2d-VGroup of chars.
        """
        char_index_counter = 0
        chars = VGroup()
        for line_no in range(lines_str_list.__len__()):
            chars.add(VGroup())
            chars[line_no].add(
                *self.lines_text.chars[
                    char_index_counter : char_index_counter
                    + lines_str_list[line_no].__len__()
                    + 1
                ]
            )
            char_index_counter += lines_str_list[line_no].__len__() + 1
        return chars

    def set_all_lines_alignments(self, alignment):
        """Function to set all line's aligment to a specific value.

        Parameters
        ----------
        alignment : :class:`str`
            Defines the alignment of paragraph. Possible values are "left", "right", "center".
        """
        for line_no in range(0, self.lines[0].__len__()):
            self.change_alignment_for_a_line(alignment, line_no)
        return self

    def set_line_alignment(self, alignment, line_no):
        """Function to set one line's aligment to a specific value.

        Parameters
        ----------
        alignment : :class:`str`
            Defines the alignment of paragraph. Possible values are "left", "right", "center".
        line_no : :class:`int`
            Defines the line number for which we want to set given alignment.
        """
        self.change_alignment_for_a_line(alignment, line_no)
        return self

    def set_all_lines_to_initial_positions(self):
        """Set all lines to their initial positions."""
        self.lines[1] = [None for _ in range(self.lines[0].__len__())]
        for line_no in range(0, self.lines[0].__len__()):
            self[line_no].move_to(
                self.get_center() + self.lines_initial_positions[line_no]
            )
        return self

    def set_line_to_initial_position(self, line_no):
        """Function to set one line to initial positions.

        Parameters
        ----------
        line_no : :class:`int`
            Defines the line number for which we want to set given alignment.
        """
        self.lines[1][line_no] = None
        self[line_no].move_to(self.get_center() + self.lines_initial_positions[line_no])
        return self

    def change_alignment_for_a_line(self, alignment, line_no):
        """Function to change one line's aligment to a specific value.

        Parameters
        ----------
        alignment : :class:`str`
            Defines the alignment of paragraph. Possible values are "left", "right", "center".
        line_no : :class:`int`
            Defines the line number for which we want to set given alignment.
        """
        self.lines[1][line_no] = alignment
        if self.lines[1][line_no] == "center":
            self[line_no].move_to(
                np.array([self.get_center()[0], self[line_no].get_center()[1], 0])
            )
        elif self.lines[1][line_no] == "right":
            self[line_no].move_to(
                np.array(
                    [
                        self.get_right()[0] - self[line_no].get_width() / 2,
                        self[line_no].get_center()[1],
                        0,
                    ]
                )
            )
        elif self.lines[1][line_no] == "left":
            self[line_no].move_to(
                np.array(
                    [
                        self.get_left()[0] + self[line_no].get_width() / 2,
                        self[line_no].get_center()[1],
                        0,
                    ]
                )
            )


class Text(SVGMobject):
    r"""Display (non-LaTeX) text rendered using `Pango <https://pango.gnome.org/>`_.

    Text objects behave like a :class:`.VGroup`-like iterable of all characters
    in the given text. In particular, slicing is possible.

    Parameters
    ----------
    text : :class:`str`
        The text that need to created as mobject.

    Returns
    -------
    :class:`Text`
        The mobject like :class:`.VGroup`.

    Examples
    ---------

    .. manim:: Example1Text
        :save_last_frame:

        class Example1Text(Scene):
            def construct(self):
                text = Text('Hello world').scale(3)
                self.add(text)

    .. manim:: TextColorExample
        :save_last_frame:

        class TextColorExample(Scene):
            def construct(self):
                text1 = Text('Hello world', color=BLUE).scale(3)
                text2 = Text('Hello world', gradient=(BLUE, GREEN)).scale(3).next_to(text1, DOWN)
                self.add(text1, text2)

    .. manim:: TextItalicAndBoldExample
        :save_last_frame:

        class TextItalicAndBoldExample(Scene):
            def construct(self):
                text0 = Text('Hello world', slant=ITALIC)
                text1 = Text('Hello world', t2s={'world':ITALIC})
                text2 = Text('Hello world', weight=BOLD)
                text3 = Text('Hello world', t2w={'world':BOLD})
                self.add(text0,text1, text2,text3)
                for i,mobj in enumerate(self.mobjects):
                    mobj.shift(DOWN*(i-1))


    .. manim:: TextMoreCustomization
            :save_last_frame:

            class TextMoreCustomization(Scene):
                def construct(self):
                    text1 = Text(
                        'Google',
                        t2c={'[:1]': '#3174f0', '[1:2]': '#e53125',
                             '[2:3]': '#fbb003', '[3:4]': '#3174f0',
                             '[4:5]': '#269a43', '[5:]': '#e53125'}, size=1.2).scale(3)
                    self.add(text1)

    As :class:`Text` uses Pango to render text, rendering non-English
    characters is easily possible:

    .. manim:: MultipleFonts
        :save_last_frame:

        class MultipleFonts(Scene):
            def construct(self):
                morning = Text("வணக்கம்", font="sans-serif")
                chin = Text(
                    "見 角 言 谷  辛 辰 辵 邑 酉 釆 里!", t2c={"見 角 言": BLUE}
                )  # works same as ``Text``.
                mess = Text("Multi-Language", style=BOLD)
                russ = Text("Здравствуйте मस नम म ", font="sans-serif")
                hin = Text("नमस्ते", font="sans-serif")
                arb = Text(
                    "صباح الخير \n تشرفت بمقابلتك", font="sans-serif"
                )  # don't mix RTL and LTR languages nothing shows up then ;-)
                japanese = Text("臂猿「黛比」帶著孩子", font="sans-serif")
                self.add(morning,chin,mess,russ,hin,arb,japanese)
                for i,mobj in enumerate(self.mobjects):
                    mobj.shift(DOWN*(i-3))


    .. manim:: PangoRender
        :quality: low

        class PangoRender(Scene):
            def construct(self):
                morning = Text("வணக்கம்", font="sans-serif")
                self.play(Write(morning))
                self.wait(2)

    Tests
    -----

    Check that the creation of :class:`~.Text` works::

        >>> Text('The horse does not eat cucumber salad.')
        Text('The horse does not eat cucumber salad.')

    .. WARNING::

        Using a :class:`.Transform` on text with leading whitespace can look
        `weird <https://github.com/3b1b/manim/issues/1067>`_. Consider using
        :meth:`remove_invisible_chars` to resolve this issue.

    """

    CONFIG = {
        # Mobject
        "color": WHITE,
        "height": None,
        "width": None,
        "fill_opacity": 1,
        "stroke_width": 0,
        "should_center": True,
        "unpack_groups": True,
        # Text
        "font": "",
        "gradient": None,
        "line_spacing": -1,
        "size": 1,
        "slant": NORMAL,
        "weight": NORMAL,
        "t2c": {},
        "t2f": {},
        "t2g": {},
        "t2s": {},
        "t2w": {},
        "tab_width": 4,
    }

    def __init__(self, text: str, **config):  # pylint: disable=redefined-outer-name
        logger.info(
            "Text now uses Pango for rendering. "
            "In case of problems, the old implementation is available as CairoText."
        )
        self.full2short(config)
        digest_config(self, config)
        self.original_text = text
        text_without_tabs = text
        if text.find("\t") != -1:
            text_without_tabs = text.replace("\t", " " * self.tab_width)
        self.text = text_without_tabs
        if self.line_spacing == -1:
            self.line_spacing = self.size + self.size * 0.3
        else:
            self.line_spacing = self.size + self.size * self.line_spacing
        file_name = self.text2svg()
        self.remove_last_M(file_name)
        SVGMobject.__init__(self, file_name, **config)
        self.text = text
        self.chars = VGroup(*self.submobjects)
        self.text = text_without_tabs.replace(" ", "").replace("\n", "")
        nppc = self.n_points_per_cubic_curve
        for each in self:
            if len(each.points) == 0:
                continue
            points = each.points
            last = points[0]
            each.clear_points()
            for index, point in enumerate(points):
                each.append_points([point])
                if (
                    index != len(points) - 1
                    and (index + 1) % nppc == 0
                    and any(point != points[index + 1])
                ):
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

    def __repr__(self):
        return f"Text({repr(self.original_text)})"

    def remove_last_M(self, file_name: str):  # pylint: disable=invalid-name
        """Internally used. Use to format the rendered SVG files."""
        with open(file_name, "r") as fpr:
            content = fpr.read()
        content = re.sub(r'Z M [^A-Za-z]*? "\/>', 'Z "/>', content)
        with open(file_name, "w") as fpw:
            fpw.write(content)

    def find_indexes(self, word: str, text: str):
        """Internally used function. Finds the indexes of ``text`` in ``word``."""
        temp = re.match(r"\[([0-9\-]{0,}):([0-9\-]{0,})\]", word)
        if temp:
            start = int(temp.group(1)) if temp.group(1) != "" else 0
            end = int(temp.group(2)) if temp.group(2) != "" else len(text)
            start = len(text) + start if start < 0 else start
            end = len(text) + end if end < 0 else end
            return [(start, end)]
        indexes = []
        index = text.find(word)
        while index != -1:
            indexes.append((index, index + len(word)))
            index = text.find(word, index + len(word))
        return indexes

    def full2short(self, config):  # pylint: disable=redefined-outer-name
        """Internally used function. Fomats some exapansion to short forms.
        text2color -> t2c
        text2font -> t2f
        text2gradient -> t2g
        text2slant -> t2s
        text2weight -> t2w
        """
        for kwargs in [config, self.CONFIG]:
            if "text2color" in kwargs:
                kwargs["t2c"] = kwargs.pop("text2color")
            if "text2font" in kwargs:
                kwargs["t2f"] = kwargs.pop("text2font")
            if "text2gradient" in kwargs:
                kwargs["t2g"] = kwargs.pop("text2gradient")
            if "text2slant" in kwargs:
                kwargs["t2s"] = kwargs.pop("text2slant")
            if "text2weight" in kwargs:
                kwargs["t2w"] = kwargs.pop("text2weight")

    def set_color_by_t2c(self, t2c=None):
        """Internally used function. Sets colour for specified strings."""
        t2c = t2c if t2c else self.t2c
        for word, color in list(t2c.items()):
            for start, end in self.find_indexes(word, self.original_text):
                self.chars[start:end].set_color(color)

    def set_color_by_t2g(self, t2g=None):
        """Internally used. Sets gradient colors for specified
        strings. Behaves similarly to ``set_color_by_t2c``."""
        t2g = t2g if t2g else self.t2g
        for word, gradient in list(t2g.items()):
            for start, end in self.find_indexes(word, self.original_text):
                self.chars[start:end].set_color_by_gradient(*gradient)

    def str2style(self, string):
        """Internally used function. Converts text to Pango Understandable Styles."""
        if string == NORMAL:
            return pangocffi.Style.NORMAL
        elif string == ITALIC:
            return pangocffi.Style.ITALIC
        elif string == OBLIQUE:
            return pangocffi.Style.OBLIQUE
        else:
            raise AttributeError("There is no Style Called %s" % string)

    def str2weight(self, string):
        """Internally used function. Convert text to Pango Understandable Weight"""
        if string == NORMAL:
            return pangocffi.Weight.NORMAL
        elif string == BOLD:
            return pangocffi.Weight.BOLD
        elif string == THIN:
            return pangocffi.Weight.THIN
        elif string == ULTRALIGHT:
            return pangocffi.Weight.ULTRALIGHT
        elif string == LIGHT:
            return pangocffi.Weight.LIGHT
        elif string == SEMILIGHT:
            return pangocffi.Weight.SEMILIGHT
        elif string == BOOK:
            return pangocffi.Weight.BOOK
        elif string == MEDIUM:
            return pangocffi.Weight.MEDIUM
        elif string == SEMIBOLD:
            return pangocffi.Weight.SEMIBOLD
        elif string == ULTRABOLD:
            return pangocffi.Weight.ULTRABOLD
        elif string == HEAVY:
            return pangocffi.Weight.HEAVY
        elif string == ULTRAHEAVY:
            return pangocffi.Weight.ULTRAHEAVY
        else:
            raise AttributeError("There is no Font Weight Called %s" % string)

    def text2hash(self):
        """Internally used function.
        Generates ``sha256`` hash for file name.
        """
        settings = (
            "PANGO" + self.font + self.slant + self.weight
        )  # to differentiate Text and CairoText
        settings += str(self.t2f) + str(self.t2s) + str(self.t2w)
        settings += str(self.line_spacing) + str(self.size)
        id_str = self.text + settings
        hasher = hashlib.sha256()
        hasher.update(id_str.encode())
        return hasher.hexdigest()[:16]

    def text2settings(self):
        """Internally used function. Converts the texts and styles
        to a setting for parsing."""
        settings = []
        t2x = [self.t2f, self.t2s, self.t2w]
        for i in range(len(t2x)):
            fsw = [self.font, self.slant, self.weight]
            if t2x[i]:
                for word, x in list(t2x[i].items()):
                    for start, end in self.find_indexes(word, self.text):
                        fsw[i] = x
                        settings.append(TextSetting(start, end, *fsw))
        # Set all text settings (default font, slant, weight)
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

        if re.search(r"\n", self.text):
            line_num = 0
            for start, end in self.find_indexes("\n", self.text):
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
        """Internally used function.
        Convert the text to SVG using Pango
        """
        size = self.size * 10
        line_spacing = self.line_spacing * 10
        dir_name = config.get_dir("text_dir")
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        hash_name = self.text2hash()
        file_name = os.path.join(dir_name, hash_name) + ".svg"
        if os.path.exists(file_name):
            return file_name
        surface = cairocffi.SVGSurface(file_name, 600, 400)
        context = cairocffi.Context(surface)
        context.move_to(START_X, START_Y)
        settings = self.text2settings()
        offset_x = 0
        last_line_num = 0
        layout = pangocairocffi.create_layout(context)
        layout.set_width(pangocffi.units_from_double(600))
        for setting in settings:
            family = setting.font
            style = self.str2style(setting.slant)
            weight = self.str2weight(setting.weight)
            text = self.text[setting.start : setting.end].replace("\n", " ")
            fontdesc = pangocffi.FontDescription()
            fontdesc.set_size(pangocffi.units_from_double(size))
            if family:
                fontdesc.set_family(family)
            fontdesc.set_style(style)
            fontdesc.set_weight(weight)
            layout.set_font_description(fontdesc)
            if setting.line_num != last_line_num:
                offset_x = 0
                last_line_num = setting.line_num
            context.move_to(
                START_X + offset_x, START_Y + line_spacing * setting.line_num
            )
            pangocairocffi.update_layout(context, layout)
            layout.set_text(text)
            logger.debug(f"Setting Text {text}")
            pangocairocffi.show_layout(context, layout)
            offset_x += pangocffi.units_to_double(layout.get_size()[0])
        surface.finish()
        return file_name
