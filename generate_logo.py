#!/usr/bin/env python

from PIL import Image
from animation import *
from mobject import *
from constants import *
from helpers import *
from scene import *
from image_mobject import *
import itertools as it
import os


import numpy as np

DARK_BLUE = "#236B8E"
DARK_BROWN = "#8B4513"
LIGHT_BROWN = "#CD853F"
LOGO_RADIUS = 1.5


if __name__ == '__main__':
    circle = Circle(density = 100, color = 'skyblue').repeat(5).scale(LOGO_RADIUS)
    sphere = Sphere(density = 50, color = DARK_BLUE).scale(LOGO_RADIUS)
    sphere.rotate(-np.pi / 7, [1, 0, 0])
    sphere.rotate(-np.pi / 7)
    alpha = 0.3
    iris = Mobject()
    Mobject.interpolate(circle, sphere, iris, alpha)
    for mob, color in [(iris, LIGHT_BROWN), (circle, DARK_BROWN)]:
        mob.highlight(color, lambda (x, y, z) : x < 0 and y > 0)
        mob.highlight("black", lambda point: np.linalg.norm(point) < 0.55*LOGO_RADIUS)

    name = tex_mobject(r"\text{3Blue1Brown}").center()
    name.highlight("gray")
    name.shift((0, -2, 0))
    sc = Scene()
    sc.animate(Transform(
        circle, iris, 
        run_time = DEFAULT_ANIMATION_RUN_TIME
    ))
    sc.add(name)
    sc.dither()
    sc.frames = drag_pixels(sc.frames)
    sc.write_to_movie("LogoGeneration", end_dither_time = 0)


    # index = int(DEFAULT_ANIMATION_RUN_TIME / DEFAULT_ANIMATION_PAUSE_TIME)
    # create_eye.frames[index].save(LOGO_PATH)
