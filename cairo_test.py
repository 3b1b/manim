import math
import cairo
from PIL import Image
import subprocess as sp
import os
import numpy as np
import sys

WIDTH, HEIGHT = 1024, 1024


def argb32_to_rgba(array):
    h, w = array.shape
    result = np.ndarray(shape=(h, w, 4), dtype=np.uint8)
    for i in range(0, 4):
        result[:, :, (i + 1) % 4] = (array // (256**i)) % 256
    # result[:, :, 3] = array % 256
    return result


data = np.ndarray(shape=(HEIGHT, WIDTH, 4), dtype=np.uint8)

surface = cairo.ImageSurface.create_for_data(
    data, cairo.FORMAT_ARGB32, WIDTH, HEIGHT
)

# surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)

# surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas

pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity

ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
ctx.set_source(pat)
ctx.fill()

ctx.translate(0.1, 0.1)  # Changing the current transformation matrix

ctx.move_to(0, 0)
# Arc(cx, cy, radius, start_angle, stop_angle)
ctx.arc(0.2, 0.1, 0.1, -math.pi / 2, 0)
ctx.line_to(0.5, 0.1)  # Line to (x,y)
# Curve(x1, y1, x2, y2, x3, y3)
ctx.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8)
ctx.close_path()

ctx.set_source_rgb(0.8, 0.2, 0.5)  # Solid color
ctx.set_line_width(0.01)
ctx.stroke()

# ctx.set_source(pat)
# ctx.fill()

new_data = np.array(data)
new_data[:,:,:3] = data[:,:,2::-1]

im = Image.fromarray(new_data, mode="RGBa")
im2 = im.convert("RGBA")
im2.show()
print(new_data[-1, -1])


surface.write_to_png("example.png")  # Output to PNG

FNULL = open(os.devnull, 'w')
sp.call(["open", "example.png"], stdout=FNULL, stderr=sp.STDOUT)
FNULL.close()

print(np.array(Image.open("example.png"))[-1, -1])
