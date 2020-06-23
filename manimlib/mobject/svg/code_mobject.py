import html
from manimlib.constants import *
from manimlib.container.container import Container
from manimlib.mobject.geometry import Dot, RoundedRectangle
from manimlib.mobject.shape_matchers import SurroundingRectangle
from manimlib.mobject.svg.text_mobject import Paragraph, remove_invisible_chars
from manimlib.mobject.types.vectorized_mobject import VGroup
from pygments.lexers import guess_lexer_for_filename

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments.styles import get_all_styles

'''
Code.styles_list static variable is containing list of names of all styles 
Code is VGroup() with three things
    Code[0] is Code.background_mobject is a VGroup()
        VGroup() of SurroundingRectangle() if background == "rectangle" 
        VGroup() of RoundedRectangle() and Dot() for three buttons if background == "window" 
    Code[1] is Code.line_numbers Which is a Paragraph() object, this mean you can use 
                Code.line_numbers[0] or Code.line_numbers.chars[0] or Code[1].chars[0] to access first line number 
    Code[2] is Code.code
        Which is a Paragraph() with color highlighted, this mean you can use 
            Code.code[1] or Code.code.chars[1] or Code[2].chars[1] 
                line number 1
            Code.code[1][0] or Code.code.chars[1][0] or Code[2].chars[1][0]
                first character of line number 1
            Code.code[1][0:5] Code.code.chars[1][0:5] or Code[2].chars[1][0:5]
                first five characters of line number 1
Code.code[][] Code.code.chars[][] or Code[2].chars[][] will create problems when using Transform() because of invisible characters 
so, before using Transform() remove invisible characters by using remove_invisible_chars()
for example self.play(Transform(remove_invisible_chars(Code.code.chars[0:2]), remove_invisible_chars(Code.code.chars[3][0:3])))
or remove_invisible_chars(Code.code) or remove_invisible_chars(Code)
'''


class Code(VGroup):
    """Class Code is used to display code with color highlighted.
    
    Parameters
    ----------
    file_name : :class:`str`
        Name of the code file to display.
    tab_width : :class:`int`, optional (default is 3).
        Number of space characters for a tab character.
    line_spacing : :class:`float`, optional (default is 0.3, which means 30% of font size)
        Amount of space between lines in respect of font size.
    scale_factor : class:`float`, optional (default is 0.5)
        It is a number which scales displayed code.
    font : :class:`str`, optional (default is 'Monospac821 BT')
         Name of text font.
    stroke_width : class:`float`, optional (default is 0)
        Stroke width for text. 0 is recommended.
    margin: class :`float`, optional (default is 0.3)
        Inner margin of text from background.
    indentation_chars : :class:`str`, optional (default is "    ")
        Indentation chars refers to the spaces/tabs at the beginning of given code line.
    background : :class:`str`, optional (default is "rectangle")
        It defines background type. Currently supports only "rectangle" and "window".
    background_stroke_width : class:`float`, optional (default is 1)
        It defines stroke width of background.
    background_stroke_color : class:`str`, optional (default is WHITE)
        It defines stroke color for background.
    corner_radius : :class:`float`, optional (default is 0.2)
        It defines corner radius for background.
    insert_line_no : :class:`bool`, optional (default is True)
        It defines whether insert line numbers in displayed code.
    line_no_from : :class:`int`, optional (default is 1)
        It defines starting number for counting lines.
    line_no_buff : :class:`float`, optional (default is 0.4)
        It defines space between line numbers and displayed code.
    style : :class:`str`, optional (default is 'vim')
        It defines style type of displayed code. You can see names of styles from Code.styles_list.
    language : :class:`str`, optional (default is None, Which mean it will automatically detects the language)
        It defines the language name of given code.
        For Knowing more available options visit https://pygments.org/docs/lexers/  for 'aliases or short names'
    generate_html_file : :class:`bool`, optional (default is False)
        It defines whether to generate code highlighted html to folder assets/codes/generated_html_files.
        
    Attributes
    ----------
    background_mobject : :class:`~.VGroup`
        To display background according to background type specified by background in Parameters.
        VGroup with SurroundingRectangle() if background == "rectangle"
        VGroup with RoundedRectangle() and Dot() for three buttons if background == "window"
    line_numbers : :class:`~.Paragraph`
        To display line numbers of displayed code if insert_line_no == True.
    code : :class:`~.Paragraph`
        To display highlighted code.
    """

    # tuples in the form (name, aliases, filetypes, mimetypes)
    # 'language' of CONFIG is aliases or short names
    # For more information about pygments.lexers visit https://pygments.org/docs/lexers/
    # from pygments.lexers import get_all_lexers
    # all_lexers = get_all_lexers()
    styles_list = list(get_all_styles())
    # For more information about pygments.styles visit https://pygments.org/docs/styles/
    CONFIG = {
        "tab_width": 3,
        "line_spacing": 0.3,
        "scale_factor": 0.5,
        "font": 'Monospac821 BT',
        'stroke_width': 0,
        'margin': 0.3,
        'indentation_chars': "    ",
        "background": "rectangle",  # or window
        "background_stroke_width": 1,
        "background_stroke_color": WHITE,
        "corner_radius": 0.2,
        'insert_line_no': True,
        'line_no_from': 1,
        "line_no_buff": 0.4,
        'style': 'vim',
        'language': None,
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

        self.code = self.gen_colored_lines()
        if self.insert_line_no:
            self.line_numbers = self.gen_line_numbers()
            self.line_numbers.next_to(self.code, direction=LEFT, buff=self.line_no_buff)

        if self.background == "rectangle":
            if self.insert_line_no:
                forground = VGroup(self.code, self.line_numbers)
            else:
                forground = self.code
            rect = SurroundingRectangle(forground, buff=self.margin,
                                        color=self.background_color,
                                        fill_color=self.background_color,
                                        stroke_width=self.background_stroke_width,
                                        stroke_color=self.background_stroke_color,
                                        fill_opacity=1, )
            rect.round_corners(self.corner_radius)
            self.background_mobject = VGroup(rect)
        else:
            if self.insert_line_no:
                forground = VGroup(self.code, self.line_numbers)
            else:
                forground = self.code

            height = forground.get_height() + 0.1 * 3 + 2 * self.margin
            width = forground.get_width() + 0.1 * 3 + 2 * self.margin

            rect = RoundedRectangle(corner_radius=self.corner_radius, height=height, width=width,
                                    stroke_width=self.background_stroke_width,
                                    stroke_color=self.background_stroke_color,
                                    color=self.background_color, fill_opacity=1)
            red_button = Dot(radius=0.1, stroke_width=0, color='#ff5f56')
            red_button.shift(LEFT * 0.1 * 3)
            yellow_button = Dot(radius=0.1, stroke_width=0, color='#ffbd2e')
            green_button = Dot(radius=0.1, stroke_width=0, color='#27c93f')
            green_button.shift(RIGHT * 0.1 * 3)
            buttons = VGroup(red_button, yellow_button, green_button)
            buttons.shift(
                UP * (height / 2 - 0.1 * 2 - 0.05) + LEFT * (width / 2 - 0.1 * 5 - self.corner_radius / 2 - 0.05))

            self.background_mobject = VGroup(rect, buttons)
            x = (height - forground.get_height()) / 2 - 0.1 * 3
            self.background_mobject.shift(forground.get_center())
            self.background_mobject.shift(UP * x)

        if self.insert_line_no:
            VGroup.__init__(self, self.background_mobject, self.line_numbers, self.code, **kwargs)
        else:
            VGroup.__init__(self, self.background_mobject, Dot(fill_opacity=0, stroke_opacity=0), self.code, **kwargs)

        self.move_to(np.array([0, 0, 0]))

    def ensure_valid_file(self):
        """Function to validate file.
        """

        if self.file_name is None:
            raise Exception("Must specify file for Code")
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
        """Function to generate line_numbers.

        Returns
        -------
        :class:`~.Paragraph`
            The generated line_numbers according to parameters.
        """
        line_numbers_array = []
        for line_no in range(0, self.code_json.__len__()):
            number = str(self.line_no_from + line_no)
            line_numbers_array.append(number)
        line_numbers = Paragraph(*[i for i in line_numbers_array], line_spacing=self.line_spacing,
                                 alignment="right", font=self.font, stroke_width=self.stroke_width).scale(
            self.scale_factor)
        for i in line_numbers:
            i.set_color(self.default_color)
        return line_numbers

    def gen_colored_lines(self):
        """Function to generate code.
        Returns
        -------
        :class:`~.Paragraph`
            The generated code according to parameters.
        """
        lines_text = []
        for line_no in range(0, self.code_json.__len__()):
            line_str = ""
            for word_index in range(self.code_json[line_no].__len__()):
                line_str = line_str + self.code_json[line_no][word_index][0]
            lines_text.append(self.tab_spaces[line_no] * "\t" + line_str)
        code = Paragraph(*[i for i in lines_text], line_spacing=self.line_spacing, tab_width=self.tab_width,
                         font=self.font, stroke_width=self.stroke_width).scale(self.scale_factor)
        for line_no in range(code.__len__()):
            line = code.chars[line_no]
            line_char_index = self.tab_spaces[line_no]
            for word_index in range(self.code_json[line_no].__len__()):
                line[line_char_index:line_char_index + self.code_json[line_no][word_index][0].__len__()].set_color(
                    self.code_json[line_no][word_index][1])
                line_char_index += self.code_json[line_no][word_index][0].__len__()
        return code

    def gen_html_string(self):
        """Function to generate html string with code highlighted and stores in variable html_string.
        """
        file = open(self.file_path, "r")
        code_str = file.read()
        file.close()
        self.html_string = hilite_me(code_str, self.language, self.style, self.insert_line_no,
                                     "border:solid gray;border-width:.1em .1em .1em .8em;padding:.2em .6em;",
                                     self.file_path)

        if self.generate_html_file:
            os.makedirs(os.path.join("assets", "codes", "generated_html_files"), exist_ok=True)
            file = open(os.path.join("assets", "codes", "generated_html_files", self.file_name + ".html"), "w")
            file.write(self.html_string)
            file.close()

    def gen_code_json(self):
        """Function to background_color, generate code_json and tab_spaces from html_string.
        background_color is just background color of displayed code.
        code_json is 2d array with rows as line numbers
        and columns as a array with length 2 having text and text's color value.
        tab_spaces is 2d array with rows as line numbers
        and columns as corresponding number of indentation_chars in front of that line in code.
        """
        if self.background_color == "#111111" or \
                self.background_color == "#272822" or \
                self.background_color == "#202020" or \
                self.background_color == "#000000":
            self.default_color = "#ffffff"
        else:
            self.default_color = "#000000"
        # print(self.default_color,self.background_color)
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
            if lines[line_index].startswith(self.indentation_chars):
                start_point = lines[line_index].find("<")
                starting_string = lines[line_index][:start_point]
                indentation_chars_count = lines[line_index][:start_point].count(self.indentation_chars)
                if starting_string.__len__() != indentation_chars_count * self.indentation_chars.__len__():
                    lines[line_index] = "\t" * indentation_chars_count + starting_string[starting_string.rfind(
                        self.indentation_chars) + self.indentation_chars.__len__():] + \
                                        lines[line_index][start_point:]
                else:
                    lines[line_index] = "\t" * indentation_chars_count + lines[line_index][start_point:]

            indentation_chars_count = 0
            while lines[line_index][indentation_chars_count] == '\t':
                indentation_chars_count = indentation_chars_count + 1
            self.tab_spaces.append(indentation_chars_count)
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
        """Function put text color to those strings that don't have one according to background_color of displayed code.
        Parameters
        ---------
        line_str : :class:`str`
            Takes a string to put color to it according to background_color of displayed code.
        """
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


def hilite_me(code, language, style, insert_line_no, divstyles, file_path):
    """Function to highlight code from string to html.

    Parameters
    ---------
    code : :class:`str`
        Code string.
    language : :class:`str`
        The name of the programming language the given code was written in.

    style : :class:`str`
        Code style name.
    insert_line_no : :class:`bool`
        It defines whether insert line numbers in html file.
    divstyles : :class:`str`
        Some html css styles.
    file_path : :class:`str`
        Path of code file.
       """
    style = style or 'colorful'
    defstyles = 'overflow:auto;width:auto;'

    formatter = HtmlFormatter(style=style,
                              linenos=False,
                              noclasses=True,
                              cssclass='',
                              cssstyles=defstyles + divstyles,
                              prestyles='margin: 0')
    if language is None:
        lexer = guess_lexer_for_filename(file_path, code)
        html = highlight(code, lexer, formatter)
    else:
        html = highlight(code, get_lexer_by_name(language, **{}), formatter)
    if insert_line_no:
        html = insert_line_numbers(html)
    html = "<!-- HTML generated by Code() -->" + html
    return html


def insert_line_numbers(html):
    """Function put line numbers to html of highlighted code.
    Arguments
    ---------
    html : :class:`str`
        html string of highlighted code.
    """
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
