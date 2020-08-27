#!/usr/bin/env python


import numpy as np
import itertools as it
import operator as op
from copy import deepcopy

from manimlib.imports import *

RADIUS = FRAME_Y_RADIUS - 0.1
CIRCLE_DENSITY = DEFAULT_POINT_DENSITY_1D*RADIUS


def logo_to_circle():
    from .generate_logo import DARK_BROWN, LOGO_RADIUS
    sc = Scene()
    small_circle = Circle(
        density = CIRCLE_DENSITY,
        color = 'skyblue'
    ).scale(LOGO_RADIUS).set_color(
        DARK_BROWN, lambda x_y_z : x_y_z[0] < 0 and x_y_z[1] > 0
    )
    big_circle = Circle(density = CIRCLE_DENSITY).scale(RADIUS)
    sc.add(small_circle)
    sc.wait()
    sc.animate(Transform(small_circle, big_circle))
    return sc

def count_sections(*radians):
    sc = Scene()
    circle = Circle(density = CIRCLE_DENSITY).scale(RADIUS)
    sc.add(circle)
    points = [
        (RADIUS * np.cos(angle), RADIUS * np.sin(angle), 0)
        for angle in radians
    ]
    dots = [Dot(point) for point in points]
    interior = Region(lambda x, y : x**2 + y**2 < RADIUS**2)    
    for x in range(1, len(points)):
        if x == 1:
            sc.animate(ShowCreation(dots[0]), ShowCreation(dots[1]))
            sc.add(dots[0], dots[1])
        else:
            sc.animate(ShowCreation(dots[x]))
            sc.add(dots[x])
        new_lines = Mobject(*[
            Line(points[x], points[y]) for y in range(x)
        ])
        sc.animate(Transform(deepcopy(dots[x]), new_lines, run_time = 2.0))
        sc.add(new_lines)
        sc.wait()
        regions = plane_partition_from_points(*points[:x+1])
        for reg in regions:
            reg.intersect(interior)
        regions = [reg for reg in regions if reg.bool_grid.any()]

        last_num = None
        for reg, count in zip(regions, it.count(1)):
            number = TexMobject(str(count)).shift((RADIUS, 3, 0))
            sc.set_color_region(reg)
            rt = 1.0 / (x**0.8)
            sc.add(number)
            sc.remove(last_num)
            last_num = number
            sc.wait(rt)
            sc.reset_background()
        sc.remove(last_num)
        sc.animate(Transform(last_num, deepcopy(last_num).center()))
        sc.wait()
        sc.remove(last_num)
    return sc

def summarize_pattern(*radians):
    sc = Scene()
    circle = Circle(density = CIRCLE_DENSITY).scale(RADIUS)
    sc.add(circle)
    points = [
        (RADIUS * np.cos(angle), RADIUS * np.sin(angle), 0)
        for angle in radians
    ]
    dots = [Dot(point) for point in points]
    last_num = None
    for x in range(len(points)):
        new_lines = Mobject(*[
            Line(points[x], points[y]) for y in range(x)
        ])
        num = TexMobject(str(moser_function(x + 1))).center()
        sc.animate(
            Transform(last_num, num) if last_num else ShowCreation(num),
            FadeIn(new_lines),
            FadeIn(dots[x]),
            run_time = 0.5,
        )
        sc.remove(last_num)
        last_num = num
        sc.add(num, dots[x], new_lines)
        sc.wait()
    return sc

def connect_points(*radians):
    sc = Scene()
    circle = Circle(density = CIRCLE_DENSITY).scale(RADIUS)
    sc.add(circle)
    points = [
        (RADIUS * np.cos(angle), RADIUS * np.sin(angle), 0)
        for angle in radians
    ]
    dots = [Dot(point) for point in points]
    sc.add(*dots)
    anims = []
    all_lines = []
    for x in range(len(points)):
        lines = [Line(points[x], points[y]) for y in range(len(points))]
        lines = Mobject(*lines)
        anims.append(Transform(deepcopy(dots[x]), lines, run_time = 3.0))
        all_lines.append(lines)
    sc.animate(*anims)
    sc.add(*all_lines)
    sc.wait()
    return sc

def interesting_problems():
    sc = Scene()
    locales = [(6, 2, 0), (6, -2, 0), (-5, -2, 0)]
    fermat = Mobject(*TexMobjects(["x^n","+","y^n","=","z^n"]))
    fermat.scale(0.5).shift((-2.5, 0.7, 0))
    face = SimpleFace()
    tb = ThoughtBubble().shift((-1.5, 1, 0))
    sb = SpeechBubble().shift((-2.4, 1.3, 0))
    fermat_copies, face_copies, tb_copies, sb_copies = (
        Mobject(*[
            deepcopy(mob).scale(0.5).shift(locale)
            for locale in locales
        ])
        for mob in [fermat, face, tb, sb]
    )

    sc.add(face, tb)
    sc.animate(ShowCreation(fermat, run_time = 1))
    sc.add(fermat)
    sc.wait()
    sc.animate(
        Transform(
            deepcopy(fermat).repeat(len(locales)),
            fermat_copies
        ),
        FadeIn(face_copies, run_time = 1.0)
    )
    sc.animate(FadeIn(tb_copies))
    sc.wait()
    sc.animate(
        Transform(tb, sb),
        Transform(tb_copies, sb_copies)
    )
    return sc

def response_invitation():
    sc = Scene()
    video_icon = VideoIcon()
    mini_videos = Mobject(*[
        deepcopy(video_icon).scale(0.5).shift((3, y, 0))
        for y in [-2, 0, 2]
    ])
    comments = Mobject(*[
        Line((-1.2, y, 0), (1.2, y, 0), color = 'white')
        for y in [-1.5, -1.75, -2]
    ])

    sc.add(video_icon)
    sc.wait()
    sc.animate(Transform(deepcopy(video_icon).repeat(3), mini_videos))
    sc.add(mini_videos)
    sc.wait()
    sc.animate(ShowCreation(comments, run_time = 1.0))
    return sc

def different_points(radians1, radians2):
    sc = Scene()
    circle = Circle(density = CIRCLE_DENSITY).scale(RADIUS)
    sc.add(circle)
    points1, points2 = (
        [
            (RADIUS * np.cos(angle), RADIUS * np.sin(angle), 0)
            for angle in radians
        ]
        for radians in (radians1, radians2)
    )
    dots1, dots2 = (
        Mobject(*[Dot(point) for point in points])
        for points in (points1, points2)
    )
    lines1, lines2 = (
        [
            Line(point1, point2)
            for point1, point2 in it.combinations(points, 2)
        ]
        for points in (points1, points2)
    )
    sc.add(dots1, *lines1)
    sc.animate(
        Transform(dots1, dots2, run_time = 3),
        *[
            Transform(line1, line2, run_time = 3)
            for line1, line2 in zip(lines1, lines2)
        ]
    )
    sc.wait()
    return sc

def next_few_videos(*radians):
    sc = Scene()
    circle = Circle(density = CIRCLE_DENSITY).scale(RADIUS)
    points = [
        (RADIUS * np.cos(angle), RADIUS * np.sin(angle), 0)
        for angle in radians
    ]
    dots = Mobject(*[
        Dot(point) for point in points
    ])
    lines = Mobject(*[
        Line(point1, point2)
        for point1, point2 in it.combinations(points, 2)
    ])
    thumbnail = Mobject(circle, dots, lines)
    frame = VideoIcon().set_color(
        "black",
        lambda point : get_norm(point) < 0.5
    )
    big_frame = deepcopy(frame).scale(FRAME_X_RADIUS)
    frame.shift((-5, 0, 0))

    sc.add(thumbnail)
    sc.wait()
    sc.animate(
        Transform(big_frame, frame),
        Transform(
            thumbnail, 
            deepcopy(thumbnail).scale(0.15).shift((-5, 0, 0))
        )
    )
    sc.add(frame, thumbnail)
    sc.wait()
    last = frame
    for x in [-2, 1, 4]:
        vi = VideoIcon().shift((x, 0, 0))
        sc.animate(
            Transform(deepcopy(last), vi),
            Animation(thumbnail)#Keeps it from getting burried
        )
        sc.add(vi)
        last = vi
    return sc



if __name__ == '__main__':
    radians = [1, 3, 5, 2, 4, 6]
    more_radians = radians + [10, 13, 20, 17, 15, 21, 18.5]
    different_radians = [1.7, 4.8, 3.2, 3.5, 2.1, 5.5]
    # logo_to_circle().write_to_movie("moser/LogoToCircle")
    # count_sections(*radians).write_to_movie("moser/CountingSections")
    # summarize_pattern(*radians).write_to_movie("moser/SummarizePattern")
    # interesting_problems().write_to_movie("moser/InterestingProblems")
    # summarize_pattern(*more_radians).write_to_movie("moser/ExtendedPattern")
    # connect_points(*radians).write_to_movie("moser/ConnectPoints")
    # response_invitation().write_to_movie("moser/ResponseInvitation")
    # different_points(radians, different_radians).write_to_movie("moser/DifferentPoints")
    # next_few_videos(*radians).write_to_movie("moser/NextFewVideos")
    # summarize_pattern(*different_radians).write_to_movie("moser/PatternWithDifferentPoints")

    #Images
    # TexMobject(r"""
    #     \Underbrace{1, 2, 4, 8, 16, 31, \dots}_\text{What?}
    # """).save_image("moser/NumberList31")
    # TexMobject("""
    #     1, 2, 4, 8, 16, 32, 63, \dots
    # """).save_image("moser/NumberList63")
    # TexMobject("""
    #     1, 2, 4, 8, 15, \dots
    # """).save_image("moser/NumberList15")
    













