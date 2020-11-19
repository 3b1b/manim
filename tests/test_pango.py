"""Tests :class:`Text` by comparing SVG files created.
"""
import os
import re

import cairocffi
import pangocairocffi
import pangocffi
from manim import START_X, START_Y, Text, SVGMobject, ITALIC

RTL_TEXT: str = """صباح الخير
مرحبا جميعا"""

WIDTH: int = 600
HEIGTH: int = 400
folder: str = os.path.abspath(os.path.join("media", "texts"))
filename: str = os.path.join(folder, "hello.svg")


def remove_last_M(file_path: str) -> None:  # pylint: disable=invalid-name
    """Format SVG file so that it can be compared"""
    with open(file_path, "r") as fpr:
        content = fpr.read()
    content = re.sub(r'Z M [^A-Za-z]*? "\/>', 'Z "/>', content)
    with open(file_path, "w") as fpw:
        fpw.write(content)


def compare_SVGObject_with_PangoText(  # pylint: disable=invalid-name
    text: Text, svg_path: str
) -> bool:
    """Checks for the path_string formed by Text and Formed SVG file.
    Uses SVGMobject as it parses the SVG and returns the path_string
    """
    remove_last_M(svg_path)  # to prevent issue displaying
    svg = SVGMobject(svg_path)
    assert len(text.submobjects) == len(svg.submobjects)
    assert (text.points == svg.points).all()
    for i in range(len(text.submobjects)):
        assert text.submobjects[i].path_string == svg.submobjects[i].path_string
        assert (
            text.submobjects[i].sheen_direction == svg.submobjects[i].sheen_direction
        ).all()
        assert (
            text.submobjects[i].stroke_rgbas == svg.submobjects[i].stroke_rgbas
        ).all()
    return True


def test_general_text_svgobject() -> None:
    """Checks number of submobjects generated when directly
    called using ``SVGMobject``
    """
    text = "hello"
    size = 1
    temp_pango_text = Text(text, size=size)
    surface = cairocffi.SVGSurface(filename, WIDTH, HEIGTH)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(WIDTH))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text(text)
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    assert compare_SVGObject_with_PangoText(temp_pango_text, filename)


def test_rtl_text_to_svgobject() -> None:
    """Checks number of submobjects generated when directly
    called using ``SVGMobject``"""
    size = 1
    text = RTL_TEXT.replace("\n", "")
    temp_pango_text = Text(text, size=1)
    surface = cairocffi.SVGSurface(filename, WIDTH, HEIGTH)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(WIDTH))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text(text)
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    assert compare_SVGObject_with_PangoText(temp_pango_text, filename)


def test_font_face() -> None:
    """Checks font face using submobject len"""
    size = 1
    text = RTL_TEXT.replace("\n", "")
    font_face = "sans"
    temp_pango_text = Text(text, size=1, font=font_face)
    surface = cairocffi.SVGSurface(filename, WIDTH, HEIGTH)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(WIDTH))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_family(font_face)
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text(text)
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    assert compare_SVGObject_with_PangoText(temp_pango_text, filename)


def test_whether_svg_file_created() -> None:
    """Checks Whether SVG file is created in desired location"""
    temp_pango_text = Text("hello", size=1)
    theo_path = os.path.abspath(
        os.path.join(folder, temp_pango_text.text2hash() + ".svg")
    )
    actual_path = os.path.abspath(temp_pango_text.text2svg())
    assert theo_path == actual_path


def test_tabs_replace() -> None:
    """Checks whether are there in end svg image.
    Pango should handle tabs and line breaks."""
    size = 1
    temp_pango_text = Text("hello\thi\nf")
    assert temp_pango_text.text == "hellohif"
    surface = cairocffi.SVGSurface(filename, WIDTH, HEIGTH)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(WIDTH))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text("hellohif")
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    assert compare_SVGObject_with_PangoText(temp_pango_text, filename)


def test_t2s() -> None:
    size = 1
    temp_pango_text = Text("Helloworld", t2s={"world": ITALIC})
    surface = cairocffi.SVGSurface(filename, WIDTH, HEIGTH)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(WIDTH))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_markup('Hello<span style="italic">world</span>')  # yay, pango markup
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    assert compare_SVGObject_with_PangoText(temp_pango_text, filename)
