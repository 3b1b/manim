from manim import PangoText, START_X, START_Y, SVGMobject
import os
import cairocffi
import pangocairocffi
import pangocffi


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
    surface = cairocffi.SVGSurface(filename, 600, 400)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(600))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text(text)
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    b = SVGMobject(filename)
    assert len(a.submobjects) == len(b.submobjects)


def test_render_text_svgobject():
    """Checks number of submobjects generated when directly called using ``SVGMobject``"""
    size = 1
    text = r"臂猿「黛比」帶著孩子"
    folder = os.path.abspath(os.path.join("media", "texts"))
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = os.path.join(folder, "hello1.svg")
    a = PangoText(text, size=10, font="amiri")
    pangoManim = os.path.join(folder, a.text2hash() + ".svg")
    surface = cairocffi.SVGSurface(filename, 600, 400)
    context = cairocffi.Context(surface)
    context.move_to(START_X, START_Y)
    layout = pangocairocffi.create_layout(context)
    layout.set_width(pangocffi.units_from_double(600))
    fontdesc = pangocffi.FontDescription()
    fontdesc.set_family("amiri")
    fontdesc.set_size(pangocffi.units_from_double(size * 10))
    layout.set_font_description(fontdesc)
    layout.set_text(text)
    pangocairocffi.show_layout(context, layout)
    surface.finish()
    b = SVGMobject(filename)
    assert len(a.submobjects) == len(b.submobjects)
