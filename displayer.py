import numpy as np
import itertools as it
import subprocess as sp
import os
import sys
from PIL import Image
import cv2
from colour import Color
import progressbar

from mobject import *
from constants import *

FFMPEG_BIN = "ffmpeg"

def get_pixels(image_array): #TODO, FIX WIDTH/HEIGHT PROBLEM HERE
    if image_array is None:
        return np.zeros(
            (DEFAULT_HEIGHT, DEFAULT_WIDTH, 3), 
            dtype = 'uint8'
        )
    else:
        pixels = np.array(image_array).astype('uint8')
        assert len(pixels.shape) == 3 and pixels.shape[2] == 3
        return pixels

def paint_region(region, image_array = None, color = None):
    pixels = get_pixels(image_array)
    assert region.shape == pixels.shape[:2]
    if color is None:
        #Random dark color
        rgb = 0.5 * np.random.random(3)
    else:
        rgb = np.array(Color(color).get_rgb()) 
    pixels[region.bool_grid] = (255*rgb).astype('uint8')
    return pixels

def paint_mobject(mobject, image_array = None):
    return paint_mobjects([mobject], image_array)

def paint_mobjects(mobjects, image_array = None):
    pixels = get_pixels(image_array)
    height = pixels.shape[0]
    width  = pixels.shape[1]
    space_height = SPACE_HEIGHT
    space_width  = SPACE_HEIGHT * width / height
    pixels = pixels.reshape((pixels.size/3, 3))

    for mobject in mobjects:
        if mobject.get_num_points() == 0:
            continue
        points, rgbs = place_on_screen(mobject.points, mobject.rgbs, 
                                       space_width, space_height)
        #Map points to pixel space, which requires rescaling and shifting
        #Remember, 2*space_height -> height
        points[:,0] = points[:,0]*width/space_width/2 + width/2
        #Flip on y-axis as you go
        points[:,1] = -1*points[:,1]*height/space_height/2 + height/2
        points, rgbs = add_thickness(
            points.astype('int'), rgbs, 
            mobject.point_thickness,
            width, height
        )

        flattener = np.array([[1], [width]], dtype = 'int')
        indices = np.dot(points, flattener)[:,0]
        pixels[indices] = (255*rgbs).astype('uint8')

    pixels = pixels.reshape((height, width, 3)).astype('uint8')
    return pixels

def add_thickness(pixel_indices, rgbs, thickness, width, height):
    """
    Imagine dragging each pixel around like a paintbrush in
    a plus-sign-shaped pixel arrangement surrounding it
    """
    thickness = adjusted_thickness(thickness, width, height)
    original = np.array(pixel_indices)
    original_rgbs = np.array(rgbs)
    for nudge in range(-thickness/2+1, thickness/2+1):
        if nudge == 0:
            continue
        for x, y in [[nudge, 0], [0, nudge]]:
            pixel_indices = np.append(
                pixel_indices, 
                original+[x, y], 
                axis = 0
            )
            rgbs = np.append(rgbs, original_rgbs, axis = 0)
    admissibles = (pixel_indices[:,0] >= 0) & \
                  (pixel_indices[:,0] < width) & \
                  (pixel_indices[:,1] >= 0) & \
                  (pixel_indices[:,1] < height)
    return pixel_indices[admissibles], rgbs[admissibles]

def adjusted_thickness(thickness, width, height):
    big_width = PRODUCTION_QUALITY_DISPLAY_CONFIG["width"]
    big_height = PRODUCTION_QUALITY_DISPLAY_CONFIG["height"]
    factor = (big_width + big_height) / (width + height)
    return 1 + (thickness-1)/factor

def place_on_screen(points, rgbs, space_width, space_height):
    """
    Projects points to 2d space and remove those outside a
    the space constraints
    """
    # camera_distance = 10
    points = np.array(points[:, :2])
    # for i in range(2):
    #     points[:,i] *= camera_distance/(camera_distance-mobject.points[:,2])
    rgbs   = np.array(rgbs)
    
    #Removes points out of space
    to_keep = (abs(points[:,0]) < space_width) & \
              (abs(points[:,1]) < space_height)
    return points[to_keep], rgbs[to_keep]

def write_to_gif(scene, name):
    #TODO, find better means of compression
    if not name.endswith(".gif"):
        name += ".gif"
    filepath = os.path.join(GIF_DIR, name)
    temppath = os.path.join(GIF_DIR, "Temp.gif")
    print "Writing " + name + "..."
    images = [Image.fromarray(frame) for frame in scene.frames]
    writeGif(temppath, images, scene.frame_duration)
    print "Compressing..."
    os.system("gifsicle -O " + temppath + " > " + filepath)
    os.system("rm " + temppath)

def write_to_movie(scene, name):
    filepath = os.path.join(MOVIE_DIR, name) + ".mp4"    
    print "Writing to %s"%filepath

    fps = int(1/scene.display_config["frame_duration"])
    dim = (scene.display_config["width"], scene.display_config["height"])

    command = [ 
        FFMPEG_BIN,
        '-y',                 # overwrite output file if it exists
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-s', '%dx%d'%dim,    # size of one frame
        '-pix_fmt', 'rgb24',
        '-r', str(fps),       # frames per second
        '-i', '-',            # The imput comes from a pipe
        '-an',                # Tells FFMPEG not to expect any audio
        '-vcodec', 'mpeg',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-loglevel', 'error',
        filepath,
    ]
    process = sp.Popen(command, stdin=sp.PIPE)
    for frame in scene.frames:
        process.stdin.write(frame.tostring())

    process.stdin.close()
    process.wait()



















