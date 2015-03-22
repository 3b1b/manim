#!/usr/bin/env python

from PIL import Image
from animate import *
from mobject import *
from constants import *
from helpers import *
import itertools as it
import os


import numpy as np

DARK_BLUE = "#236B8E"
DARK_BROWN = "#8B4513"
LIGHT_BROWN = "#CD853F"

size = 1.5
circle = Circle(color = 'skyblue').repeat(4).scale(size)
sphere = Sphere(density = 100, color = DARK_BLUE).scale(size)
sphere.rotate(-np.pi / 7, [1, 0, 0])
sphere.rotate(-np.pi / 7)
alpha = 0.3
iris = Mobject()
Mobject.interpolate(circle, sphere, iris, alpha)
for mob, color in [(iris, LIGHT_BROWN), (circle, DARK_BROWN)]:
    mob.highlight(color, lambda (x, y, z) : x < 0 and y > 0)
    mob.highlight("black", lambda point: np.linalg.norm(point) < size/2)

name = ImageMobject(NAME_TO_IMAGE_FILE["3Blue1Brown"]).center()
name.highlight("gray")
# name.highlight(DARK_BROWN, lambda (x, y, z) : x < 0 and y > 0)
name.shift((0, -2, 0))

create_eye = Transform(
    circle, iris, 
    run_time = DEFAULT_ANIMATION_RUN_TIME,
    name = "LogoGeneration"
).then(
    Animation(name, dither_time = 0)
).drag_pixels()
create_eye.write_to_movie()
index = int(DEFAULT_ANIMATION_RUN_TIME / DEFAULT_ANIMATION_PAUSE_TIME)
create_eye.frames[index].save(LOGO_PATH)
