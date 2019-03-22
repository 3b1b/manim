from big_ol_pile_of_manim_imports import *


Lg_formula_config = {
    "tex_to_color_map": {
        "\\theta_0": WHITE,
        "{L}": BLUE,
        "{g}": YELLOW,
    },
}


class You(PiCreature):
    CONFIG = {
        "color": BLUE_C,
    }


def get_ode():
    tex_config = {
        "tex_to_color_map": {
            "{\\theta}": BLUE,
            "{t}": WHITE,
        }
    }
    ode = TexMobject(
        "\\ddot {\\theta}({t})", "=",
        "-\\mu \\dot {\\theta}({t})",
        "-{g \\over L} \\sin\\big({\\theta}({t})\\big)",
        **tex_config,
    )
    return ode
