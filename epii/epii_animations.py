#!/usr/bin/env python

from PIL import Image
from animate import *
from mobject import *
from constants import *
from helpers import *
from tex_image_utils import load_pdf_images
from displayer import *
import itertools as it
import os
import numpy as np
from copy import deepcopy


PI_COLOR         = "red"
E_COLOR          = "skyblue"
I_COLOR          = "green"
ADDER_COLOR      = "limegreen"
MULTIPLIER_COLOR = "yellow"
ONE_COLOR        = "skyblue"

EPII_MOVIE_DIR = "epii"

symbol_images = load_pdf_images("epii_symbols.pdf", regen_if_exists = False)
phrase_images = load_pdf_images("epii_phrases.pdf", regen_if_exists = False)

name_to_image = dict(
    zip([
        "e",
        "pi",
        "i",
        "equals_neg1", 
        "pile_of_equations",
        "two",
        "plus",
        "three",
        "four",
        "times",
        "five",
        "fours_underbrace",
        "e_to_x",
        "e_by_e_x_times",
        "e_by_e_pi_i_times",
        "e_to_x_property",
        "e_to_x_series",
        "e_to_5",
        "e_to_sum_ones",
        "e_to_1_product",
        "e_to_x_plus_y",
        "e_by_e_x_plus_y_times",
        "x_es_then_y_es",
        "e_to_x_e_to_y",
        "i_squared_equals_neg_1",
        "epii_series",
        "e_to_complex",
        "e_to_matrix",
        "e_to_derivative",
        "adder_to_multiplier_property",
        "defining_property",
        "e_by_e",
        "e_by_e_by_e",
        "e_def",
        "e_approx",
        "one",
        "sqrt_neg1",
        "e_digits",
        "twenty",
        "three_point_five",
        "sqrt_two",
        "six",
        "e_to_2_value",
        "e_to_3_value",
        "e_to_5_value",
        "zero",
        "minus",
        "neg_1",
        "to_the_x",
    ], symbol_images) + zip([
        "e_question", 
        "pi_question", 
        "i_question", 
        "what", 
        "just_trust_it",
        "ish",
        "question_marks",
        "not_what_is_happening",
        "what_it_means",
        "why_it_works",
        "why_it_is_intuitive",
        "colon_explanation",
        "adder",
        "multiplier",
        "other_way_around",
        "how_do_we_define_this",
        "unlearn_what_you_have_learned",
        "e_in_nature",
    ], phrase_images)
)

def logo_to_epii():
    e, pi, i, equals_neg1 = [
        ImageMobject(name_to_image[name])
        for name in [
            "e", "pi", "i", "equals_neg1"
        ]
    ]
    epii_neg1 = CompoundMobject(e, pi, i, equals_neg1)
    epii_neg1.center().shift((0, 2, 0))
    # stars = Stars()
    return Transform(
        ImageMobject(LOGO_PATH, invert = False),
        epii_neg1,
        dither_time = 0, run_time = 2.0,
    ).then(
        Animation(epii_neg1)
    )
    # .then(
    #     Transform(
    #         stars,
    #         epii_neg1,
    #         dither_time = 0, run_time = 3.0,
    #     )
    

def write_epii():
    e, pi, i, equals_neg1 = [
        ImageMobject(name_to_image[name])
        for name in ["e", "pi", "i", "equals_neg1"]
    ]
    center = CompoundMobject(e, pi, i, equals_neg1).get_center()
    for mob in e, pi, i, equals_neg1:
        mob.shift(-center)
    anims=[
        ShowCreation(e),
        ShowCreation(pi).with_background(e),
        ShowCreation(i).with_background(e, pi),
        ShowCreation(equals_neg1).with_background(e, pi, i),
    ]
    for anim in anims:
        anim.set_run_time(1.0)
    for anim in anims[1:]:
        anim.set_dither(1)
        anims[0].then(anim)
    return anims[0]


def the_terms():
    e, pi, i, one, e_digits, sqrt_neg1, equals_neg1 = [
        ImageMobject(name_to_image[name])
        for name in [
            "e", "pi", "i", "one", "e_digits",
            "sqrt_neg1", "equals_neg1"
        ]
    ]
    center = CompoundMobject(e, pi, i, equals_neg1).get_center()
    for mob in [e, pi, i, equals_neg1]:
        mob.shift(-center + (0, 2, 0))
    colored_e = deepcopy(e).highlight(E_COLOR)
    colored_pi = deepcopy(pi).highlight(PI_COLOR)
    colored_i = deepcopy(i).highlight(I_COLOR)

    e_digits.highlight(E_COLOR)
    sqrt_neg1.highlight(I_COLOR)

    e_digits.shift([2, -2, 0])
    sqrt_neg1.shift([2, 2, 0])

    pi_copy = deepcopy(colored_pi)
    pi_copy.scale(1.5)
    pi_copy.center()
    pi_copy.shift([-0.8, 0, 0])

    one.center()
    one.shift([0.2, 0, 0])

    long_line = ParametricFunction(lambda t : (-1, np.pi * t, 0))
    diameter = ParametricFunction(lambda t : (0, t, 0))
    circle = Circle()
    for mobject in [circle, diameter, one, long_line, pi_copy]:
        mobject.shift([-1, 0, 0])
        mobject.highlight(PI_COLOR)

    return Transform(
        CompoundMobject(e, pi, i, equals_neg1),
        CompoundMobject(colored_e, colored_pi, colored_i, equals_neg1)
    ).then(
        Transform(
            colored_e, e_digits
        ).while_also(
            Transform(
                colored_i, sqrt_neg1
            )
        ).while_also(
            Transform(
                colored_pi, pi_copy
            )
        ).while_also(
            Transform(
                circle, long_line, 
            )
        ).with_background(
            diameter, one, colored_e, colored_pi, colored_i, equals_neg1
        )
    )

def literal_epii():
    e, pi, i, e_by_e_pi_i_times, what = [
        ImageMobject(name_to_image[name])
        for name in [
            "e", "pi", "i", "e_by_e_pi_i_times", "what"
        ]
    ]
    what.shift([0, -1, 0])
    return Transform(
        CompoundMobject(e, pi, i).center().shift((0, 2, 0)),
        e_by_e_pi_i_times
    ).then(
        Animation(what, run_time = 2.1).with_background(
            e_by_e_pi_i_times
        )
    )

def pile_of_equations():
    return ShowCreation(
        CompoundMobject(
            ImageMobject(name_to_image["pile_of_equations"]).center(),
            ImageMobject(
                name_to_image["just_trust_it"]
            ).center().shift([2, -3, 0]).highlight("red")
        ),
        alpha_func = None,
        run_time = 5.0
    )

def confusion_of_terms():
    e, pi, i, e_question, pi_question, i_question, what_it_means = [
        ImageMobject(name_to_image[name])
        for name in [
            "e", "pi", "i", "e_question", "pi_question", "i_question", "what_it_means"
        ]
    ]
    colored_e = deepcopy(e).highlight(E_COLOR)
    colored_pi = deepcopy(pi).highlight(PI_COLOR)
    colored_i = deepcopy(i).highlight(I_COLOR)

    e_question.highlight(E_COLOR).shift([2, 1, 0])
    pi_question.highlight(PI_COLOR).shift([0, -1, 0])
    i_question.highlight(I_COLOR).shift([-1, 0, 0])
    what_it_means.center().shift((-3, 0, 0))

    stars = Stars()

    e_anim = Transform(colored_e, e_question)
    e_anim.with_background(colored_pi, colored_i)
    i_anim = Transform(colored_i, i_question)
    i_anim.with_background(e_question, colored_pi)
    pi_anim = Transform(colored_pi, pi_question)
    pi_anim.with_background(e_question, i_question)
    all_questions = CompoundMobject(e_question, pi_question, i_question)
    to_stars = Transform(
        all_questions,
        stars, run_time = 5.0, dither_time = 0
    )
    stall_1 = Animation(all_questions)
    to_goal = Transform(stars, what_it_means, dither_time = 0, run_time = 2.0)
    for anim in [e_anim, i_anim, pi_anim]:
        anim.set_run_time(1.0)
        anim.set_dither(0)
    for anim in [i_anim, pi_anim, stall_1, to_stars, to_goal]:
        e_anim.then(anim)
    return e_anim

def list_of_goals():
    goals = [
        ImageMobject(name_to_image[name]).center()
        for name in [
            "what_it_means", "why_it_works", "why_it_is_intuitive"
        ]
    ]
    for x in range(3):
        goals[x].shift((3*(x - 1), 0, 0))
    stars = Stars()
    rotating_stars = Rotating(stars, radians = np.pi / 3)
    return Transform(stars, goals[0]).while_also(
        rotating_stars, display = False
    ).then(
        Reveal(goals[1], dither_time = 0).with_background(goals[0])
    ).then(
        Reveal(goals[2]).with_background(*goals[:2])
    )

def not_repeated_multiplication():
    e_to_x, e_by_e_x_times, not_what_is_happening = [
        ImageMobject(name_to_image[name]).center()
        for name in ["e_to_x", "e_by_e_x_times", "not_what_is_happening"]
    ]
    not_what_is_happening.rotate(np.pi/7).highlight("red")
    return Transform(e_to_x, e_by_e_x_times).then(
        Reveal(not_what_is_happening).with_background(e_by_e_x_times)
    ).then(
        Animation(
            CompoundMobject(e_by_e_x_times, not_what_is_happening),
            run_time = 1.0
        )
    )

def problems_with_repeated_multiplication():
    e, e_by_e, e_by_e_by_e, e_def, how_do_we_define_this = [
        ImageMobject(name_to_image[name]).center()
        for name in ["e", "e_by_e", "e_by_e_by_e", 
                     "e_def", "how_do_we_define_this"]
    ]
    how_do_we_define_this.highlight(E_COLOR).shift((0, -1, 0))
    kwargs = {"run_time" : 0.2, "dither_time" : 0.5}
    return Transform(e, e_by_e, **kwargs).then(
        Transform(e_by_e, e_by_e_by_e, **kwargs)
    ).then(
        Transform(e_by_e_by_e, e_def).while_also(
            Reveal(how_do_we_define_this)
        )
    )

def numbers_as_actions():
    three = ImageMobject(name_to_image["three"]).center()
    sphere = Sphere().scale(2).highlight(MULTIPLIER_COLOR)
    def custom_alpha(t):
        return high_inflection_0_to_1(1.7 * t * (1 - t))
    return Transform(
        three, sphere, run_time = 3.0,
        alpha_func = custom_alpha
    ).while_also(
        Rotating(sphere, radians = 10 * np.pi), 
        display = False
    )


def numbers_as_counting():
    three = ImageMobject(name_to_image["three"])
    three.center()
    spheres = CompoundMobject(*[
        Sphere().scale(0.5).shift([x - 1, 0, 0])
        for x in range(3)
    ])
    return Transform(
        three, spheres, 
    ).while_also(
        Rotating(spheres, axis = [1, 0, 0]),
        display = False
    )


def addition_by_counting():
    two, plus, three, five = [
        ImageMobject(name_to_image[name])
        for name in [
            "two", "plus", "three", "five"
        ]
    ]
    tps_center = CompoundMobject(two, plus, three).get_center()
    for mob in two, plus, three:
        mob.shift(tps_center)
    five.center()
    spheres = []
    for x in range(5):
        spheres.append(Sphere().scale(0.5).shift([x-2, 0, 0]))
    first_two  = CompoundMobject(*spheres[:2])
    last_three = CompoundMobject(*spheres[2:])
    all_five   = CompoundMobject(*spheres)
    plus_three = CompoundMobject(plus, three)
    return Animation(
        CompoundMobject(two, plus_three), 
        run_time = 2.0, dither_time = 0.0,
    ).then(
        Transform(
            two, first_two,
        ).set_dither(0).with_background(
            plus_three
        )
    ).then(
        Transform(
            plus_three, last_three, 
        ).with_background(first_two).set_dither(0)
    ).then(
        Transform(
            all_five, five,
        ).set_dither(0)
    ).then(
        Animation(five, run_time = 1.0, dither_time = 0.0)
    )

def multiplication_by_counting():
    four, times, five, fours_underbrace, twenty = [
        ImageMobject(name_to_image[name])
        for name in [
            "four", "times", "five", "fours_underbrace", "twenty"
        ]
    ]
    spheres = CompoundMobject(*[
        Sphere().scale(0.5).shift([1.5*x-3, 1.5-y, 0])
        for y in range(4)
        for x in range(5)
    ])
    fours_underbrace.center()
    twenty.center()
    rot_spheres = Rotating(spheres, axis = [1, 0, 0], radians = np.pi)
    four_times_five = CompoundMobject(four, times, five).center()
    first  = Transform(four_times_five, fours_underbrace).set_dither(0.5)
    second = Transform(copy.deepcopy(fours_underbrace), spheres).set_dither(0)
    second.while_also(rot_spheres, display = False).generate_frames()
    third  = Transform(spheres, twenty).set_dither(0.5)
    third.while_also(rot_spheres, display = False)
    return first.then(second).then(third)

def fraction_counting():
    three_point_five = ImageMobject(name_to_image["three_point_five"]).center()
    spheres = [
        Sphere().scale(0.5).shift([x-1.5, 0, 0])
        for x in range(4)
    ]
    num_points = spheres[-1].get_num_points()
    for attr in ['points', 'rgbs']:
        setattr(
            spheres[-1], attr, 
            getattr(spheres[-1], attr)[:num_points/2, :]
        )
    spheres = CompoundMobject(*spheres)
    spheres.rotate(np.pi/4, [1, 0, 0])
    return Transform(
        three_point_five, spheres,
    ).while_also(
        Rotating(spheres, axis = [1, 0, 0], radians = np.pi),
        display = False
    )

def irrational_counting():
    sqrt_two = ImageMobject(name_to_image["sqrt_two"]).center()
    ish      = ImageMobject(name_to_image["ish"]).center()
    spheres = [
        Sphere().scale(0.5).rotate(np.pi/4, [1, 0, 0]).shift([x-0.5, 0, 0])
        for x in range(2)
    ]
    num_points = spheres[-1].get_num_points()
    for attr in ['points', 'rgbs']:
        setattr(
            spheres[-1], attr, 
            getattr(spheres[-1], attr)[:int(num_points*(np.sqrt(2)-2)), :]
        )
    ish.shift([1.3, 0, 0])
    spheres = CompoundMobject(ish, *spheres)
    return Transform(
        sqrt_two, spheres
    ).while_also(
        Rotating(spheres, axis = [1, 0, 0], radians = np.pi),
        display = False
    )

def imaginary_counting():
    sqrt_neg1, question_marks = [
        ImageMobject(name_to_image[name]).center()
        for name in ["sqrt_neg1", "question_marks"]
    ]
    return Transform(sqrt_neg1, question_marks)

def real_number_as_three_things():
    three, adder, multiplier = [
        ImageMobject(name_to_image[name]).center()
        for name in ["three", "adder", "multiplier"]
    ]
    adder_three = copy.deepcopy(three).highlight(ADDER_COLOR)
    mult_three = copy.deepcopy(three).highlight(MULTIPLIER_COLOR)

    three.shift([0, 2, 0])
    adder_three.shift([-1, 2, 0])
    mult_three.shift([1, 2, 0])

    adder.highlight(ADDER_COLOR).shift((2, 2, 0))
    multiplier.highlight(MULTIPLIER_COLOR).shift((2, 2, 0))

    radius = 2 * SPACE_WIDTH
    marked_number_line = NumberLine(
        radius = radius, 
        with_numbers = True
    )
    number_line = NumberLine(radius = radius)
    three_dist = 3 * number_line.interval_size

    split_three = Transform(
        copy.deepcopy(three),
        CompoundMobject(three, adder_three, mult_three)
    )
    adder_three.center().shift(three.get_center())
    mult_three.center().shift(three.get_center())
    draw_number_line = ShowCreation(marked_number_line)
    three_to_point = Transform(
        copy.deepcopy(three), 
        Point((three_dist, 0, 0))
    )
    add_by_three = ApplyFunction(
        lambda (x, y, z) : (three_dist+x, y, z), 
        number_line, dither_time = 2.0
    ).while_also(Reveal(adder, dither_time = 2.0))
    multiply_by_three = ApplyFunction(
        lambda (x, y, z) : (3*x, y, z),
        number_line, dither_time = 2.0
    ).while_also(Reveal(multiplier, dither_time = 2.0))
    draw_number_line.set_dither(0)

    return split_three.then(
        draw_number_line.with_background(three)
    ).then(
        add_by_three.with_background(adder_three)
    ).then(
        multiply_by_three.with_background(mult_three)
    )


def wrong_adder_conception():
    vert_disp = -0.3
    number_line = NumberLine(radius = SPACE_WIDTH + 3)
    nlis = number_line.interval_size
    three = ImageMobject(name_to_image["three"])
    three.center().shift((0, 2, 0)).highlight(ADDER_COLOR)
    initial_numbers = [
        ImageMobject(
            NAME_TO_IMAGE_FILE[str(x)]
        ).center().scale(0.5).shift((x*nlis, vert_disp, 0))
        for x in range(-3, 4)
    ]
    final_numbers = [
        ImageMobject(
            NAME_TO_IMAGE_FILE[str(x)]
        ).center().scale(0.5).shift((x*nlis, vert_disp, 0))
        for x in range(0, 7)
    ]
    dots1 = ImageMobject(NAME_TO_IMAGE_FILE["cdots"]).center()
    dots2 = copy.deepcopy(dots1).shift((-4 * nlis, vert_disp, 0))
    dots1.shift((4*nlis, vert_disp, 0))
    number_line.add(dots1, dots2)
    kwargs = {"run_time" : 2.0, "dither_time" : 1.0}
    anim = ComplexFunction(lambda z : z + 3*nlis, number_line, **kwargs)
    for init, final in zip(initial_numbers, final_numbers):
        anim.while_also(Transform(init, final, **kwargs))
    anim.while_also(
        Transform(three, CompoundMobject(*final_numbers), **kwargs)
    )
    return anim

def real_addition_rule():
    three = ImageMobject(name_to_image["three"]).center()
    three.shift([0, 2, 0]).highlight(ADDER_COLOR)
    marked_number_line = NumberLine(radius = 2 * SPACE_WIDTH, with_numbers = True)
    number_line = NumberLine(radius = 2 * SPACE_WIDTH)
    three_dist = 3 * number_line.interval_size
    shifted_line = copy.deepcopy(number_line).shift((three_dist, 0, 0))
    zero_arrow = Arrow().nudge().shift((0, -0.3, 0))
    three_arrow = Arrow((three_dist, -0.3, 0)).nudge().highlight(ADDER_COLOR)
    return Reveal(
        CompoundMobject(zero_arrow, three_arrow)
    ).with_background(marked_number_line, three).then(
        Transform(
            CompoundMobject(number_line, zero_arrow),
            CompoundMobject(shifted_line, three_arrow),
            dither_time = 0, run_time = 3.0
        ).with_background(three, three_arrow)
    ).then(
        Flash(three_arrow).with_background(shifted_line, three)
    ).then(
        Animation(CompoundMobject(three_arrow, shifted_line, three))
    )

def real_multiplication_rule():
    three = ImageMobject(name_to_image["three"]).center()
    three.shift([0, 2, 0]).highlight(MULTIPLIER_COLOR)
    marked_number_line = NumberLine(with_numbers = True)
    number_line = NumberLine()
    three_dist = 3 * number_line.interval_size
    stretched_line = copy.deepcopy(number_line)
    stretched_line.points = np.array(
        map(lambda (x, y, z) : (3*x, y, z), stretched_line.points)
    )
    zero_arrow = Arrow(direction = (0, 1, 0)).nudge().shift((0, -0.3, 0))
    zero_arrow.highlight("white")
    one_arrow = Arrow().nudge().shift((number_line.interval_size, -0.3, 0))
    one_arrow.highlight(ONE_COLOR)
    three_arrow = Arrow((three_dist, -0.3, 0)).nudge().highlight(MULTIPLIER_COLOR)
    return Reveal(
        CompoundMobject(zero_arrow, one_arrow, three_arrow)
    ).with_background(marked_number_line, three).then(
        Transform(
            CompoundMobject(number_line, one_arrow),
            CompoundMobject(stretched_line, three_arrow),
            dither_time = 0, run_time = 3.0
        ).with_background(three, three_arrow, zero_arrow)
    ).then(
        Flash(three_arrow).with_background(stretched_line, three, zero_arrow)
    ).then(
        Animation(CompoundMobject(zero_arrow, three_arrow, stretched_line, three))
    )

def real_addition_by_sliding():
    two, plus, three, five = [
        ImageMobject(
            name_to_image[name]
        )
        for name in [
            "two", "plus", "three", "five"
        ]
    ]
    center = CompoundMobject(two, plus, three).get_center()
    for mob in two, plus, three:
        mob.shift(-center + (0, 2, 0)).highlight(ADDER_COLOR)
    five.center().shift((0, 2, 0)).highlight(ADDER_COLOR)
    number_line = NumberLine(radius = 2 * SPACE_WIDTH) #Numbers?
    int_size = number_line.interval_size
    shifted_line = dict()
    for x in [2, 5]:
        shifted_line[x] = copy.deepcopy(number_line).shift((x*int_size, 0, 0))
    return Transform(
        copy.deepcopy(number_line), shifted_line[2], dither_time = 0.5
    ).with_background(two).then(
        Transform(
            shifted_line[2], shifted_line[5], dither_time = 0.5
        ).with_background(two, plus, three)
    ).then(
        Transform(
            number_line, shifted_line[5], dither_time = 0.5
        ).with_background(five)
    )

def real_multiplication_by_stretching():
    two, times, three, six = [
        ImageMobject(
            name_to_image[name]
        ).highlight(MULTIPLIER_COLOR)
        for name in [
            "two", "times", "three", "six"
        ]
    ]
    center = CompoundMobject(two, times, three).get_center()
    for mob in two, times, three:
        mob.shift(-center + (0, 2, 0))
    six.center().shift((0, 2, 0))
    number_line = NumberLine() #Numbers?
    int_size = number_line.interval_size
    stretched_line = dict()
    for num in [2, 6]:
        stretched_line[num] = copy.deepcopy(number_line)
        stretched_line[num].points = np.array(
            map(lambda (x, y, z) : (num*x, y, z), stretched_line[num].points)
        )
    return Transform(
        copy.deepcopy(number_line), stretched_line[2], dither_time = 0.5
    ).with_background(two).then(
        Transform(
            stretched_line[2], stretched_line[6], dither_time = 0.5
        ).with_background(two, times, three)
    ).then(
        Transform(
            number_line, stretched_line[6], dither_time = 0.5
        ).with_background(six)
    )



def exp_turns_adder_to_muliplier():
    two, e_to_x, e_to_2_value = [
        ImageMobject(name_to_image[name]).center()
        for name in ["two", "e_to_x", "e_to_2_value"]
    ]
    two.center().shift((-2, 2, 0)).highlight(ADDER_COLOR)
    e_to_x.center().shift((0, 2, 0))
    e_to_2_value.center().shift((2, 2, 0)).highlight(MULTIPLIER_COLOR)
    number_line = NumberLine(radius = SPACE_WIDTH*2)
    point = Point(e_to_x.get_center())
    shift_line   = ApplyFunction(
        lambda (x,y,z) : (x+2*number_line.interval_size,y,z), 
        copy.deepcopy(number_line),
        run_time = 1.0, dither_time = 0
    )
    stretch_line = ApplyFunction(
        lambda (x,y,z) : (x*np.exp(2),y,z), 
        number_line,
        run_time = 1.0
    )
    return Reveal(two).set_dither(0).with_background(e_to_x).then(
        shift_line.with_background(two, e_to_x)
    ).then(
        Transform(two, point, dither_time = 0).with_background(e_to_x)
    ).then(
        Transform(point, e_to_2_value, dither_time = 0).with_background(e_to_x)
    ).then(
        stretch_line.with_background(e_to_x, e_to_2_value)
    )

def exp_is_homomorphism():
    two, three, five, e_to_x, e_to_2_value, e_to_3_value, e_to_5_value, plus, times = [
        ImageMobject(name_to_image[name]).center()
        for name in ["two", "three", "five", "e_to_x", "e_to_2_value", 
                     "e_to_3_value", "e_to_5_value", "plus", "times"]
    ]
    two.shift((-2.2, 2.2, 0))
    three.shift((-1.8, 1.8, 0))
    two_three = CompoundMobject(two, three).highlight(ADDER_COLOR)
    five.shift((-2, -2, 0)).highlight(ADDER_COLOR)
    e_to_2_value.shift((1.8, 2.2, 0))
    e_to_3_value.shift((2.2, 1.8, 0))
    e_to_2_value_e_to_3_value = CompoundMobject(e_to_2_value, e_to_3_value).highlight(MULTIPLIER_COLOR)
    e_to_5_value.shift((2, -2, 0)).highlight(MULTIPLIER_COLOR)
    e_to_x_copy = copy.deepcopy(e_to_x)
    e_to_x.shift((0, 2, 0))
    e_to_x_copy.shift((0, -2, 0))
    plus.shift((-2, 0, 0))
    times.shift((2, 0, 0))
    operations = CompoundMobject(e_to_x, e_to_x_copy, plus, times)
    high_exp_point = Point(e_to_x.get_center())
    low_exp_point  = Point(e_to_x_copy.get_center())
    plus_point  = Point(plus.get_center())
    times_point = Point(times.get_center())

    anim = Transform(
        two_three, plus_point, dither_time = 0
    ).with_background(operations)
    for start, end in [
        (plus_point, five), 
        (five, low_exp_point), 
        (low_exp_point, e_to_5_value), 
        (copy.deepcopy(two_three), high_exp_point),
        (high_exp_point, e_to_2_value_e_to_3_value),
        (e_to_2_value_e_to_3_value, times_point),
        (times_point, e_to_5_value)
        ]:
        anim.then(Transform(start, end, dither_time = 0), 
            carry_over_background = True
        )
        if end in [e_to_5_value, five, e_to_2_value_e_to_3_value]:
            anim.then(
                Animation(end, run_time = 1.0, dither_time = 0),
                carry_over_background = True,
            )
    return anim

def repeated_product_gives_property():
    expressions = [
        ImageMobject(name_to_image[name]).center()
        for name in ["e_to_x_plus_y", "e_by_e_x_plus_y_times", 
                     "x_es_then_y_es", "e_to_x_e_to_y",]
    ]
    anim = Transform(expressions[0], expressions[1], run_time = 0.5)
    for x in range(1, 3):
        anim.then(
            Transform(expressions[x], expressions[x + 1]),
            run_time = 0.5
        )
    return anim


def repeated_product_as_consequence():
    defining_property, other_way_around, e_to_5, \
    e_to_sum_ones, e_to_1_product = [
        ImageMobject(name_to_image[name]).center()
        for name in ["defining_property", "other_way_around", "e_to_5", 
                     "e_to_sum_ones", "e_to_1_product"]
    ]
    return Animation(other_way_around, run_time = 1.0, dither_time = 0).then(
        Animation(defining_property, run_time = 2.0, dither_time = 0)
    ).then(
        Transform(e_to_5, e_to_sum_ones, run_time = 0.5)
    ).then(
        Transform(e_to_sum_ones, e_to_1_product, run_time = 0.5)
    )


def e_to_x_definition():
    adder_to_multiplier_property, e_to_x_series, \
    colon_explanation, e_def, e_approx, e_in_nature = [
        ImageMobject(name_to_image[name])
        for name in [
            "adder_to_multiplier_property", 
            "e_to_x_series",
            "colon_explanation", 
            "e_def", 
            "e_approx",
            "e_in_nature"
            ]
    ]
    for mob in e_to_x_series, colon_explanation:
        mob.center()
    colon_explanation.shift((-1, 1.5, 0))
    colon_explanation.add(Arrow(point = (-3.5, 0.4, 0), direction = (-1,-1,0)))
    e_in_nature.shift((0, -2, 0))
    for mob in e_def, e_approx:
        mob.shift((0, 1, 0))
    return Transform(
        adder_to_multiplier_property, 
        e_to_x_series
    ).then(
        Reveal(colon_explanation).with_background(e_to_x_series)
    ).then(
        Transform(e_to_x_series, e_def).while_also(
            Reveal(CompoundMobject(e_approx, e_in_nature))
        )
    )

def less_natural_exponentials():
    two, five, i, to_the_x, adder_to_multiplier_property = [
        ImageMobject(name_to_image[name])
        for name in ["two", "five", "i", "to_the_x", 
                     "adder_to_multiplier_property"]
    ]
    two.center()
    five.center()
    i.scale(1.5).center()
    to_the_x.shift((0, -0.25, 0))
    kwargs = {"dither_time" : 0.5}
    return Transform(
        adder_to_multiplier_property,
        CompoundMobject(two, to_the_x), **kwargs
    ).then(
        Transform(two, five, **kwargs).with_background(
            to_the_x
        )
    ).then(
        Transform(five, i, **kwargs).with_background(
            to_the_x
        )
    )


def complex_addition(num):
    complex_plane = Grid(radius = 2 * SPACE_WIDTH).add(Cross())
    point = Cross().shift((num.real, num.imag, 0)).highlight(ADDER_COLOR)
    return ShowCreation(point).with_background(complex_plane).then(
        ComplexFunction(
            (lambda z : z + num), complex_plane
        ).with_background(
            point
        )
    )     

def complex_multiplication(num):
    complex_plane = Grid(radius = 2 * SPACE_WIDTH)
    zero = Cross()
    one  = Cross().shift((1, 0, 0)).highlight(ONE_COLOR)
    num_dot = Cross().shift((num.real, num.imag, 0)).highlight(MULTIPLIER_COLOR)
    return ComplexFunction(
        (lambda z : z*num), complex_plane
    ).while_also(
        ComplexFunction((lambda z : z + num - 1), one)
    ).with_background(
        zero, num_dot
    )

def multiply_i_twice():
    zero, one, i, new_one = [
        Cross(), 
        Cross().shift((1, 0, 0)).highlight(ONE_COLOR),
        Cross().shift((0, 1, 0)).highlight(MULTIPLIER_COLOR),
        Cross().shift((0, 1, 0)).highlight(ONE_COLOR),
    ]
    complex_plane = Grid(radius = 2 * SPACE_WIDTH)
    return RotationAsTransform(complex_plane, np.pi/2).while_also(
        RotationAsTransform(one, np.pi/2)
    ).with_background(zero, i).then(
        RotationAsTransform(complex_plane, np.pi/2).while_also(
            RotationAsTransform(CompoundMobject(new_one), np.pi/2)
        ).with_background(zero)
    )

def multiply_neg_1():
    zero, one, neg_1 = [
        Cross(), 
        Cross().shift((1, 0, 0)).highlight(ONE_COLOR),
        Cross().shift((-1, 0, 0)).highlight(MULTIPLIER_COLOR),
    ]
    complex_plane = Grid(radius = 2 * SPACE_WIDTH).add(zero, one)
    return RotationAsTransform(
        complex_plane.add(zero, one), np.pi
    ).with_background(neg_1)

def i_squared_equals_neg_1():
    equation = ImageMobject(name_to_image["i_squared_equals_neg_1"]).center()
    plane = Grid().add(Cross(), Cross().shift((-1, 0, 0)).highlight(MULTIPLIER_COLOR))
    return Transform(plane, equation, dither_time = 2.0)

def reals_in_complex():
    radius = 2 * SPACE_WIDTH
    plain_complex_plane = Grid(radius = radius)
    complex_plane = copy.deepcopy(plain_complex_plane)
    complex_plane.highlight(NumberLine.DEFAULT_COLOR, lambda (x, y, z) : y == 0)
    shifted = copy.deepcopy(complex_plane).shift((3, 0, 0))
    stretched = copy.deepcopy(complex_plane).scale(2)
    anim = Transform(plain_complex_plane, complex_plane)
    for start, end in [
        (copy.deepcopy(complex_plane), shifted),
        (shifted, complex_plane),
        (copy.deepcopy(complex_plane), stretched),
        (stretched, complex_plane)
        ]:
        anim.then(Transform(start, end, run_time = 2.0, dither_time = 0.0))
    return anim

def broken_up_complex_addition(num):
    complex_plane = Grid(radius = 2 * SPACE_WIDTH).add(Cross())
    point = Cross().shift((num.real, num.imag, 0)).highlight(ADDER_COLOR)
    plane_plus_real = copy.deepcopy(complex_plane).shift((num.real, 0, 0))
    plane_plus_num = copy.deepcopy(complex_plane).shift((num.real, num.imag, 0))    
    return Transform(complex_plane, plane_plus_real).with_background(point).then(
        Transform(plane_plus_real, plane_plus_num),
        carry_over_background = True
    )

def broken_up_complex_multiplication(num):
    complex_plane = Grid(radius = 2 * SPACE_WIDTH)
    zero = Cross()
    one  = Cross().shift((1, 0, 0)).highlight(ONE_COLOR)
    num_dot = Cross().shift((num.real, num.imag, 0)).highlight(MULTIPLIER_COLOR)
    plane_stretched = copy.deepcopy(complex_plane).scale(np.linalg.norm(num))
    plane_times_num = copy.deepcopy(plane_stretched).rotate(np.log(num).imag)
    one_stretched = copy.deepcopy(one).shift((np.linalg.norm(num) - 1, 0, 0))
    one_times_num = copy.deepcopy(one).center().shift(num_dot.get_center())
    return Transform(
        complex_plane, plane_stretched
    ).with_background(zero, num_dot).while_also(
        Transform(one, one_stretched)
    ).then(
        Transform(
            plane_stretched, plane_times_num
        ).while_also(Transform(one_stretched, one_times_num)),
        carry_over_background = True
    )

def new_dimensions():
    adder = ComplexFunction(lambda z : z + complex(0, 1))
    multiplier = RotationAsTransform(Grid(radius = SPACE_HEIGHT + SPACE_WIDTH), np.pi / 3)
    for anim in adder, multiplier:
        anim.set_run_time(5.0).set_dither(0.5).set_alpha_func(there_and_back)
    return adder.then(multiplier)


def wrap_imaginaries_to_circle():
    imaginaries = ParametricFunction(
        lambda t : (0, t * SPACE_HEIGHT, 0),
        color = ADDER_COLOR
    )
    imaginaries.shift((0.01, 0, 0))
    circle = Circle(color = MULTIPLIER_COLOR)
    Mobject.align_data(imaginaries, circle)
    complex_plane = Grid()
    hidden_plane = Grid(color = "black")
    return FadeOut(
        complex_plane, alpha_func = there_and_back
    ).with_background(imaginaries).then(
        ShowCreation(circle).with_background(imaginaries, complex_plane), 
    ).then(
        ComplexFunction(np.exp, imaginaries).with_background(
            circle, complex_plane), 
    )

def wrap_imaginaries_to_circle_with_measurments():
    pi, i, minus, neg_1 = [
        ImageMobject(name_to_image[name])
        for name in ["pi", "i", "minus", "neg_1"]
    ]
    pi_i = CompoundMobject(pi, i).center()
    minus_pi_i = copy.deepcopy(pi_i).center().add(
        minus.center().scale(0.5).shift((-0.2, 0, 0))
    )
    for mob, sgn in (pi_i, 1), (minus_pi_i, -1):
        mob.shift((-0.3, sgn*np.pi, 0))
        mob.add(
            Cross().scale(0.5).shift((0, sgn*np.pi, 0)).highlight(ADDER_COLOR)
        )
    neg_1.center().shift((-1.2, 0, 0))
    imaginaries = ParametricFunction(
        lambda t : (0, np.pi * t, 0),
        color = ADDER_COLOR
    )
    complex_plane = Grid()
    circle = Circle(color = MULTIPLIER_COLOR)
    return ComplexFunction(np.exp, imaginaries).with_background(
        circle, complex_plane
    ).while_also(
        Transform(CompoundMobject(pi_i, minus_pi_i), neg_1, 
            run_time = DEFAULT_ANIMATION_RUN_TIME,
        )
    )

def definition_of_pi():
    pi, one, two = [
        ImageMobject(name_to_image[name]).center()
        for name in [
            "pi", "one", "two"
        ]
    ]
    two.scale(0.7).shift((-0.1, 0, 0))
    two_pi = CompoundMobject(two, pi.shift((0.1, 0, 0)))
    one.shift((0.5, 0.3, 0))
    two_pi.shift((0, -1.3, 0))
    circle = Circle().rotate(np.pi/4)
    line = Line((-np.pi, -1, 0), (np.pi, -1, 0)).highlight(Circle.DEFAULT_COLOR)
    radius = Line((0, 0, 0), (1, 0, 0))
    kwargs = {"run_time" : 2, "dither_time" : 1}
    return Transform(circle, line, **kwargs).with_background(
        one, radius
    ).while_also(
        Reveal(two_pi, **kwargs)
    )


def epii_adder_to_multiplier():
    e, pi, i, equals_neg1, neg_1 = [
        ImageMobject(name_to_image[name])
        for name in [
            "e", "pi", "i", "equals_neg1", "neg_1"
        ]
    ]
    pi.highlight(ADDER_COLOR)
    i.highlight(ADDER_COLOR)
    equals_neg1.highlight(MULTIPLIER_COLOR, lambda (x, y, z) : x > 0.25)
    neg_1.highlight(MULTIPLIER_COLOR)
    epii_neg1 = CompoundMobject(e, pi, i, equals_neg1)

    dividing_line = Line((0, -SPACE_HEIGHT, 0), (0, SPACE_HEIGHT, 0))
    half_width = SPACE_WIDTH / 2
    left_grid = Grid(radius = SPACE_HEIGHT + np.pi).filter_out(
        lambda (x, y, z) : abs(x) > half_width
    ).add(Cross())
    right_grid = Grid().add(Cross(), Cross().highlight(ONE_COLOR).shift((1, 0, 0)))
    # pi_i = CompoundMobject(pi, i).center().shift((-0.25, np.pi, 0))
    pi_i = Cross().highlight(ADDER_COLOR).shift((0, np.pi, 0))
    # neg_1.center().shift((-1.5, 0, 0))
    neg_1 = Cross().highlight(MULTIPLIER_COLOR).shift((-1, 0, 0))
    return Animation(epii_neg1, run_time = 2, dither_time = 0).then(
        ComplexFunction(lambda z : z + complex(0, np.pi), left_grid).with_background(
            pi_i, dividing_line.shift((half_width, 0, 0))
        ).shift((-half_width, 0, 0)).while_also(
            RotationAsTransform(right_grid, np.pi).with_background(
                neg_1
            ).restrict_width(half_width).shift((half_width, 0, 0))
        ).while_also(
            Animation(epii_neg1)
        )
    )

    # return Animation(epii_neg1, run_time = 1.0, dither_time = 0).then(
    #     ComplexFunction(lambda z : z + complex(0, np.pi), Grid(radius = 2*SPACE_HEIGHT))
    # ).with_background(epii_neg1).then(
    #     RotationAsTransform(Grid(radius = 2*SPACE_HEIGHT), np.pi)
    # ).with_background(epii_neg1)

def e_to_all_kinds_of_things():
    expressions = [
        ImageMobject(name_to_image[name])
        for name in [
           "e_to_complex", "e_to_matrix", "e_to_derivative", "e_def"
        ]
    ]
    return reduce(
        Animation.then, 
        [
            Transform(expressions[x], expressions[x + 1])
            for x in range(3)
        ]
    )



if __name__ == '__main__':
    example_complex = complex(2, 1)
    functions = [
        # (logo_to_epii, []),
        # (write_epii, []),
        # (the_terms, []),
        # (literal_epii, []),
        # (pile_of_equations, []),
        # (confusion_of_terms, []),
        # (list_of_goals, []),
        # (not_repeated_multiplication, []),
        # (problems_with_repeated_multiplication, []),
        # (numbers_as_actions, []),
        # (numbers_as_counting, []),
        # (addition_by_counting, []),
        # (multiplication_by_counting, []),
        # (fraction_counting, []),
        # (irrational_counting, []),
        # (imaginary_counting, []),
        # (real_number_as_three_things, []),
        # (wrong_adder_conception, []),
        # (real_addition_rule, []),
        # (real_multiplication_rule, []),
        # (real_addition_by_sliding, []),
        # (real_multiplication_by_stretching, []),
        # (exp_turns_adder_to_muliplier, []),
        # (exp_is_homomorphism, []),
        # (repeated_product_gives_property, []),
        # (repeated_product_as_consequence, []),
        (e_to_x_definition, []),
        # (less_natural_exponentials, []),
        # (complex_addition, [example_complex]),
        # (complex_multiplication, [example_complex]),
        # (multiply_i_twice, []),
        # (multiply_neg_1, []),
        # (i_squared_equals_neg_1, []),
        # (complex_addition, [complex(0, 1)]),
        # (reals_in_complex, []),
        # (broken_up_complex_addition, [example_complex]),
        # (broken_up_complex_multiplication, [example_complex]),
        # (new_dimensions, []),
        # (wrap_imaginaries_to_circle, []),
        # (wrap_imaginaries_to_circle_with_measurments, []),
        # (definition_of_pi, []),
        # (epii_adder_to_multiplier, []),
        # (e_to_all_kinds_of_things, []),
    ]

    full_path = os.path.join(MOVIE_DIR, EPII_MOVIE_DIR)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    for func, args in functions:
        name = os.path.join(
            EPII_MOVIE_DIR, 
            to_cammel_case(func.__name__) + hash_args(args)
        )
        func(*args).write_to_movie(name)

    for anim in [
            # ShowCreation(Grid(), run_time = 3.0), 
            # Rotating(Stars(), radians = np.pi / 3),
            # ComplexFunction(np.exp, Grid(radius = SPACE_HEIGHT))
        ]:
        anim.write_to_movie(os.path.join(EPII_MOVIE_DIR, str(anim)))









