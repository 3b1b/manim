#!/usr/bin/env python
"""demonstrate pycairo and pygame"""

from __future__ import print_function

import math
import sys

import cairo
import pygame


def draw(surface):
    x, y, radius = (250, 250, 200)
    ctx = cairo.Context(surface)
    ctx.set_line_width(15)
    ctx.arc(x, y, radius, 0, 2.0 * math.pi)
    ctx.set_source_rgb(0.8, 0.8, 0.8)
    ctx.fill_preserve()
    ctx.set_source_rgb(1, 1, 1)
    ctx.stroke()


def input(events):
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)
        else:
            print(event)


def main():
    width, height = 512, 512
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

    pygame.init()
    pygame.display.set_mode((width, height))
    screen = pygame.display.get_surface()

    draw(surface)

    # Create PyGame surface from Cairo Surface
    buf = surface.get_data()
    image = pygame.image.frombuffer(buf, (width, height), "ARGB")
    # Tranfer to Screen
    screen.blit(image, (0, 0))
    pygame.display.flip()

    while True:
        input(pygame.event.get())


if __name__ == "__main__":
    main()