from manim import PangoText, START_X, START_Y, SVGMobject
import os
import cairocffi
import pangocairocffi
import pangocffi

rtl_text = """صباح الخير
مرحبا جميعا"""

width = 600
height = 400


def test_general_text_svgobject():
    """Checks number of submobjects generated when directly called using ``SVGMobject``"""
    text = "hello"
    size = 1
    folder = os.path.abspath(os.path.join("media", "texts"))
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = os.path.join(folder, "hello.svg")
    a = PangoText(text, size=10)
    pangoManim = os.path.join(folder, a.text2hash() + ".svg")
    surface = cairocffi.SVGSurface(filename, width, height)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(width))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text(text)
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    b = SVGMobject(filename)
    assert len(a.submobjects) == len(b.submobjects)


def test_rtl_text_text_svgobject():
    """Checks number of submobjects generated when directly called using ``SVGMobject``"""
    size = 1
    text = rtl_text
    folder = os.path.abspath(os.path.join("media", "texts"))
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = os.path.join(folder, "hello.svg")
    a = PangoText(text, size=1)
    pangoManim = os.path.join(folder, a.text2hash() + ".svg")
    surface = cairocffi.SVGSurface(filename, width, height)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(width))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text(text)
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    b = SVGMobject(filename)
    assert len(a.submobjects) == len(b.submobjects)


def test_font_face():
    """Checks font face using submobject len"""
    size = 1
    text = rtl_text
    font_face = "sans"
    folder = os.path.abspath(os.path.join("media", "texts"))
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = os.path.join(folder, "hello.svg")
    a = PangoText(text, size=1, font=font_face)
    pangoManim = os.path.join(folder, a.text2hash() + ".svg")
    surface = cairocffi.SVGSurface(filename, width, height)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(width))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_family(font_face)
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text(text)
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    b = SVGMobject(filename)
    assert len(a.submobjects) == len(b.submobjects)


def test_whether_svg_file_created():
    """Checks Whether SVG file is created in desired location"""
    a = PangoText("hello", size=1)
    folder = os.path.abspath(os.path.join("media", "texts"))
    if not os.path.exists(folder):
        os.makedirs(folder)
    theoPath = os.path.abspath(os.path.join(folder, a.text2hash() + ".svg"))
    actualPath = os.path.abspath(a.text2svg())
    assert theoPath == actualPath


def test_tabs_replace():
    """Checks whether are there in end svg image. Pango should handle tabs and line breaks."""
    size = 1
    folder = os.path.abspath(os.path.join("media", "texts"))
    if not os.path.exists(folder):
        os.makedirs(folder)
    a = PangoText("hello\thi\nf")
    assert a.text == "hellohif"
    pangoManim = os.path.join(folder, a.text2hash() + ".svg")
    filename = os.path.join(folder, "hello.svg")
    surface = cairocffi.SVGSurface(filename, width, height)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(width))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text("hello\thi\nf")
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    b = SVGMobject(filename)
    assert len(a.submobjects) == len(b.submobjects)


test_tabs_replace()
