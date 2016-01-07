import numpy as np
import itertools as it
import subprocess as sp
import os
import sys
from PIL import Image
import cv2
from colour import Color
import progressbar

from helpers import *

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

def paint_mobjects(mobjects, image_array = None, include_sub_mobjects = True):
    pixels = get_pixels(image_array)
    height = pixels.shape[0]
    width  = pixels.shape[1]
    space_height = SPACE_HEIGHT
    space_width  = SPACE_HEIGHT * width / height
    pixels = pixels.reshape((pixels.size/3, 3)).astype('uint8')

    if include_sub_mobjects:
        all_families = [
            mob.submobject_family() 
            for mob in mobjects
        ]
        mobjects = reduce(op.add, all_families, [])
        
    for mobject in mobjects:
        if mobject.get_num_points() == 0:
            continue
        #bunch these together so rgbs never get lost from points
        points_and_rgbs = np.append(
            mobject.points,
            255*mobject.rgbs,
            axis = 1
        )
        points_and_rgbs = place_on_screen(
            points_and_rgbs,
            space_width, space_height
        )
        #Map points to pixel space, which requires rescaling and shifting
        #Remember, 2*space_height -> height
        points_and_rgbs[:,0] = points_and_rgbs[:,0]*width/space_width/2 + width/2
        #Flip on y-axis as you go
        points_and_rgbs[:,1] = -1*points_and_rgbs[:,1]*height/space_height/2 + height/2
        points_and_rgbs = add_thickness(
            points_and_rgbs.astype('int'),
            mobject.point_thickness,
            width, height
        )

        points, rgbs = points_and_rgbs[:,:2], points_and_rgbs[:,2:]
        flattener = np.array([[1], [width]], dtype = 'int')
        indices = np.dot(points, flattener)[:,0]
        pixels[indices] = rgbs.astype('uint8')
    return pixels.reshape((height, width, 3))

def add_thickness(pixel_indices_and_rgbs, thickness, width, height):
    """
    Imagine dragging each pixel around like a paintbrush in
    a plus-sign-shaped pixel arrangement surrounding it.

    Pass rgb = None to do nothing to them
    """
    thickness = adjusted_thickness(thickness, width, height)
    original = np.array(pixel_indices_and_rgbs)
    n_extra_columns = pixel_indices_and_rgbs.shape[1] - 2
    for nudge in range(-thickness/2+1, thickness/2+1):
        if nudge == 0:
            continue
        for x, y in [[nudge, 0], [0, nudge]]:
            pixel_indices_and_rgbs = np.append(
                pixel_indices_and_rgbs, 
                original+([x, y] + [0]*n_extra_columns),
                axis = 0
            )
    admissibles = (pixel_indices_and_rgbs[:,0] >= 0) & \
                  (pixel_indices_and_rgbs[:,0] < width) & \
                  (pixel_indices_and_rgbs[:,1] >= 0) & \
                  (pixel_indices_and_rgbs[:,1] < height)
    return pixel_indices_and_rgbs[admissibles]

def adjusted_thickness(thickness, width, height):
    big_width = PRODUCTION_QUALITY_DISPLAY_CONFIG["width"]
    big_height = PRODUCTION_QUALITY_DISPLAY_CONFIG["height"]
    factor = (big_width + big_height) / (width + height)
    return 1 + (thickness-1)/factor

def place_on_screen(points_and_rgbs, space_width, space_height):
    """
    Projects points to 2d space and remove those outside a
    the space constraints.

    Pass rbgs = None to do nothing to them.
    """
    # Remove 3rd column
    points_and_rgbs = np.append(
        points_and_rgbs[:, :2], 
        points_and_rgbs[:, 3:], 
        axis = 1
    )
    
    #Removes points out of space
    to_keep = (abs(points_and_rgbs[:,0]) < space_width) & \
              (abs(points_and_rgbs[:,1]) < space_height)
    return points_and_rgbs[to_keep]

def get_file_path(name, extension):
    file_path = os.path.join(MOVIE_DIR, name)
    if not file_path.endswith(extension):
        file_path += extension
    directory = os.path.split(file_path)[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    return file_path

def write_to_movie(scene, name):
    file_path = get_file_path(name, ".mp4")
    print "Writing to %s"%file_path

    fps = int(1/scene.frame_duration)
    dim = (scene.width, scene.height)

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
        file_path,
    ]
    process = sp.Popen(command, stdin=sp.PIPE)
    for frame in scene.frames:
        process.stdin.write(frame.tostring())
    process.stdin.close()
    process.wait()



















