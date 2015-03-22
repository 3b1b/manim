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

from epii_animations import name_to_image


PI_COLOR         = "red"
E_COLOR          = "skyblue"
I_COLOR          = "green"
ADDER_COLOR      = "limegreen"
MULTIPLIER_COLOR = "yellow"
ONE_COLOR        = "skyblue"

POEM_MOVIE_DIR = "poem"

symbol_images = load_pdf_images("epii_poem.pdf", regen_if_exists = False)

RUN_TIMES = [
    0.4,
    0.4,
    0.4,
    0.4,
    0.4,
    0.4,
    0.4,
    0.4,
]
DITHER_TIMES = [
    0,
    0.1,
    0,
    0.1,
    0,
    0.05,
    0.0,
    0.1,
]
LAST_FRAME_REST_KWARGS = {"run_time" : 1.0, "dither_time" : 0}
LINE_KWARGS = [
    {"run_time" : run_time, "dither_time" : dither_time}
    for run_time, dither_time in zip(RUN_TIMES, DITHER_TIMES)
]

LINES_PER_VERSE = 8
LINES_PER_LAST_VERSE = 4
VERSES = 10

def get_text_transitions(verse):
        num_lines = LINES_PER_LAST_VERSE if (verse == VERSES - 1) else LINES_PER_VERSE
        lines = [
            ImageMobject(symbol_images[LINES_PER_VERSE * verse + x])
            for x in range(num_lines)
        ]
        lines[2].shift((-1, 0, 0))
        transitions = []
        for x in range(num_lines):
            if x == 0:
                transition = Animation(lines[x], **LINE_KWARGS[x])
            elif x == 1:
                transition = Reveal(lines[x], **LINE_KWARGS[x])
            elif x in range(2, num_lines-1):
                transition = Transform(lines[x-2], lines[x], **LINE_KWARGS[x])
            else:
                transition = Transform(
                    CompoundMobject(lines[x-2], lines[x-1]), lines[x],
                    **LINE_KWARGS[x]
                )
            if x in range(1, num_lines-1):
                transition.with_background(lines[x - 1])
            transitions.append(transition)
        return transitions

def augment_verse_0(transitions):
    mobs = [e, pi, i, equals_neg1] = [
        ImageMobject(name_to_image[name])
        for name in ["e", "pi", "i", "equals_neg1"]
    ]
    center = CompoundMobject(*mobs).get_center()
    for mob in mobs:
        mob.shift(-center)
    for x, mob in zip([1, 2, 3, 7], mobs):
        transitions[x].while_also(ShowCreation(mob, **LINE_KWARGS[x]))
        for y in range(x + 1, LINES_PER_VERSE):
            transitions[y].with_background(mob)

def augment_verse_1(transitions):
    e, pi, i, e_by_e_pi_i_times = [
        ImageMobject(name_to_image[name])
        for name in ["e", "pi", "i", "e_by_e_pi_i_times"]
    ]
    epii = CompoundMobject(e, pi, i).center()
    for x in range(4):
        transitions[x].with_background(epii)
    transitions[4].while_also(Transform(epii, e_by_e_pi_i_times, **LINE_KWARGS[4]))
    for x in range(5, LINES_PER_VERSE):
        transitions[x].with_background(e_by_e_pi_i_times)

def augment_verse_2(transitions):
    e, pi, i, pi_question, i_question = [
        ImageMobject(name_to_image[name])
        for name in ["e", "pi", "i", "pi_question", "i_question"]
    ]
    center = CompoundMobject(e, pi, i).get_center()
    for mob in e, pi, i:
        mob.shift(-center)
    pi.highlight(PI_COLOR)
    pi_question.highlight(PI_COLOR).shift((-1, -1, 0))
    i.highlight(I_COLOR)
    i_question.highlight(I_COLOR).shift((1, 1, 0))
    for x in [2, 3]:
        transitions[x].with_background(pi_question, i_question)
    transitions[4].while_also(
        Transform(pi_question, pi, **LINE_KWARGS[4])
    ).with_background(i_question)
    transitions[5].while_also(
        Transform(i_question, i, **LINE_KWARGS[5])
    ).with_background(pi)
    for x in [6, 7]:
        transitions[x].with_background(pi, i)
    transitions[7].while_also(Reveal(e, **LINE_KWARGS[7]))

def augment_verse_3(transitions):
    one, i, minus, two, three_point_five = [
        ImageMobject(name_to_image[name])
        for name in ["one", "i", "minus", "two", "three_point_five"]
    ]
    minus.shift((-0.8, 0.25, 0))
    minus_two = CompoundMobject(minus, two)
    nums = [one, i, minus_two, three_point_five]
    for num in nums:
        num.center().shift((0.5, 0, 0)).highlight(ADDER_COLOR)
    i.scale(2)

    plane = Grid(radius = SPACE_WIDTH + SPACE_HEIGHT)
    transitions[3].while_also(ShowCreation(plane, **LINE_KWARGS[3]))
    for x, c, num in zip([4, 5, 6, 7], [1, complex(0, 1), -2, 3.5], nums):
        transitions[x].while_also(
            ComplexFunction(lambda z : z + c, plane, **LINE_KWARGS[x])
        ).with_background(num)

def augment_verse_4(transitions):
    i, two = [
        ImageMobject(name_to_image[name])
        for name in ["i", "two"]
    ]
    for num in i, two:
        num.center().shift((0.5, 0, 0)).highlight(MULTIPLIER_COLOR)

    plane = Grid(radius = SPACE_WIDTH + SPACE_HEIGHT)
    for x in [0, 1, 2, 3, 6, 7]:
        transitions[x].with_background(plane)
    transitions[4].while_also(
        RotationAsTransform(plane, np.pi/2, **LINE_KWARGS[4])
    ).with_background(i)
    transitions[5].while_also(
        ComplexFunction(lambda z : 2*z, plane, **LINE_KWARGS[5])
    ).with_background(two)

def augment_verse_5(transitions):
    e_to_x = ImageMobject(name_to_image["e_to_x"]).center()
    for transition in transitions:
        transition.with_background(e_to_x)

def augment_verse_6(transitions):
    e_to_x, e_by_e_x_times, not_what_is_happening, two, e_to_2 = [
        ImageMobject(name_to_image[name])
        for name in ["e_to_x", "e_by_e_x_times", "not_what_is_happening",
                     "two", "e_to_2_value"]
    ]
    two.center().shift((-2, 0, 0)).highlight(ADDER_COLOR)
    e_to_2.center().shift((2, 0, 0)).highlight(MULTIPLIER_COLOR)
    e_to_x.center()
    point = Point()
    not_what_is_happening.rotate(np.pi/7).highlight("red")
    transitions[0].while_also(Transform(e_to_x, e_by_e_x_times, **LINE_KWARGS[0]))
    transitions[1].while_also(
        Reveal(not_what_is_happening, **LINE_KWARGS[1])
    ).with_background(e_by_e_x_times)
    for x in [2, 3]:
        transitions[x].with_background(e_by_e_x_times, not_what_is_happening)
    transitions[4].with_background(two, e_to_x)
    transitions[5].while_also(
        Transform(two, point, **LINE_KWARGS[5])
    ).with_background(e_to_x)
    transitions[6].while_also(
        Transform(point, e_to_2, **LINE_KWARGS[6])
    ).with_background(e_to_x)
    transitions[7].with_background(e_to_2, e_to_x)


def augment_verse_7(transitions):
    plane = Grid(SPACE_HEIGHT + SPACE_WIDTH)
    for x, c in zip([0, 1, 4, 5], [1, -1, complex(0, 1), complex(0, -1)]):
        transitions[x].while_also(
            ComplexFunction(lambda z : z + c, plane, **LINE_KWARGS[x])
        )
    big_plane = copy.deepcopy(plane).scale(2)
    for x, c, mob in zip([2, 3], [2, 0.5], [plane, big_plane]):
        transitions[x].while_also(
            ComplexFunction(lambda z : z*c, mob, **LINE_KWARGS[x])
        )
    rotated_plane = copy.deepcopy(plane).rotate(np.pi / 4)
    for x, r, mob in zip([6, 7], [np.pi/4, -np.pi/4], [plane, rotated_plane]):
        transitions[x].while_also(
            RotationAsTransform(mob, r, **LINE_KWARGS[x])
        )

def augment_verse_8(transitions):
    pi, i, neg_1 = [
        ImageMobject(name_to_image[name])
        for name in ["pi", "i", "neg_1"]
    ]
    pi_i = CompoundMobject(pi, i).center()
    pi_i.shift((-0.3, np.pi, 0))
    neg_1.center().shift((-1.2, 0, 0))
    imaginaries = ParametricFunction(
        lambda t : (0, np.pi * t, 0),
        color = ADDER_COLOR
    )
    plane = Grid()
    circle = Circle(color = MULTIPLIER_COLOR)

    transitions[0].with_background(plane)
    transitions[1].while_also(
        Reveal(pi_i, **LINE_KWARGS[1])
    ).with_background(plane)
    transitions[2].while_also(
        ComplexFunction(lambda z : z + np.pi * complex(0, 1), **LINE_KWARGS[2])
    ).with_background(pi_i)
    transitions[3].with_background(plane, pi_i)
    transitions[4].while_also(
        Transform(imaginaries, circle, **LINE_KWARGS[4])
    ).while_also(
        Transform(pi, neg_1, **LINE_KWARGS[4])
    ).with_background(plane)
    transitions[5].with_background(plane, neg_1, circle)
    transitions[6].while_also(
        RotationAsTransform(plane, np.pi, **LINE_KWARGS[6])
    ).with_background(circle, neg_1)
    transitions[7].with_background(plane, circle, neg_1)

def augment_verse_9(transitions):
    mobs = [e, pi, i, equals_neg1] = [
        ImageMobject(name_to_image[name])
        for name in ["e", "pi", "i", "equals_neg1"]
    ]
    epii_neg1 = CompoundMobject(*mobs).center()
    for transition in transitions:
        transition.with_background(epii_neg1)


if __name__ == '__main__':
    augment_verse = [
        augment_verse_0,
        augment_verse_1,
        augment_verse_2,
        augment_verse_3,
        augment_verse_4,
        augment_verse_5,
        augment_verse_6,
        augment_verse_7,
        augment_verse_8,
        augment_verse_9,
    ]
    for verse in range(VERSES):
        transitions = get_text_transitions(verse)
        augment_verse[verse](transitions)
        name = os.path.join(POEM_MOVIE_DIR, "Verse%d"%verse)
        reduce(Animation.then, transitions).write_to_movie(name)


















