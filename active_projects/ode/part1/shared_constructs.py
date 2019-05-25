from manimlib.imports import *


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
            "{\\dot\\theta}": RED,
            "{\\ddot\\theta}": YELLOW,
            "{t}": WHITE,
            "{\\mu}": WHITE,
        }
    }
    ode = TexMobject(
        "{\\ddot\\theta}({t})", "=",
        "-{\\mu} {\\dot\\theta}({t})",
        "-{g \\over L} \\sin\\big({\\theta}({t})\\big)",
        **tex_config,
    )
    return ode


def get_period_formula():
    return TexMobject(
        "2\\pi", "\\sqrt{\\,", "L", "/", "g", "}",
        tex_to_color_map={
            "L": BLUE,
            "g": YELLOW,
        }
    )


def pendulum_vector_field_func(point, mu=0.1, g=9.8, L=3):
    theta, omega = point[:2]
    return np.array([
        omega,
        -np.sqrt(g / L) * np.sin(theta) - mu * omega,
        0,
    ])


def get_vector_symbol(*texs, **kwargs):
    config = {
        "include_background_rectangle": True,
        "bracket_h_buff": SMALL_BUFF,
        "bracket_v_buff": SMALL_BUFF,
        "element_alignment_corner": ORIGIN,
    }
    config.update(kwargs)
    array = [[tex] for tex in texs]
    return Matrix(array, **config)


def get_heart_var(index):
    heart = SuitSymbol("hearts")
    if index == 1:
        heart.set_color(BLUE_C)
    elif index == 2:
        heart.set_color(GREEN)
    heart.set_height(0.7)
    index = Integer(index)
    index.move_to(heart.get_corner(DR))
    heart.add(index)
    return heart


def get_heart_var_deriv(index):
    heart = get_heart_var(index)
    filler_tex = "T"
    deriv = TexMobject("{d", filler_tex, "\\over", "dt}")
    deriv.scale(2)
    filler = deriv.get_part_by_tex(filler_tex)
    heart.match_height(filler)
    heart.move_to(filler)
    heart.scale(1.5, about_edge=UL)
    deriv.remove(filler)
    deriv.add(heart)
    deriv.heart = heart
    return deriv


def get_love_equation1():
    equation = VGroup(
        get_heart_var_deriv(1),
        TexMobject("=").scale(2),
        TexMobject("a").scale(2),
        get_heart_var(2)
    )
    equation.arrange(RIGHT)
    equation[-1].shift(SMALL_BUFF * DL)
    return equation


def get_love_equation2():
    equation = VGroup(
        get_heart_var_deriv(2),
        TexMobject("=").scale(2),
        TexMobject("-b").scale(2),
        get_heart_var(1),
    )
    equation.arrange(RIGHT)
    equation[-1].shift(SMALL_BUFF * DL)
    return equation
