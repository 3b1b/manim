import numpy as np
import itertools as it
import os
from PIL import Image
import subprocess
import cv2
from colour import Color
import progressbar

from mobject import *

def get_pixels(image_array):
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
        rgb = 0.5 * np.random.random(3) #Random darker colors
    else:
        rgb = np.array(Color(color).get_rgb()) 
    pixels[region.bool_grid] = (255*rgb).astype('uint8')
    return pixels

def paint_mobject(mobject, image_array = None):
    pixels = get_pixels(image_array)
    height = pixels.shape[0]
    width  = pixels.shape[1]
    space_height = SPACE_HEIGHT
    space_width = SPACE_HEIGHT * width / height

    #TODO, Let z add a depth componenet?
    points = np.array(mobject.points[:, :2])
    rgbs   = np.array(mobject.rgbs)
    #Flips y-axis
    points[:,1] *= -1
    #Map points to pixel space, then create pixel array first in terms
    #of its flattened version
    points += np.array(
        [space_width, space_height]*points.shape[0]
    ).reshape(points.shape)
    points *= np.array(
        [width / (2.0 * space_width), height / (2.0 * space_height)]*\
        points.shape[0]
    ).reshape(points.shape)
    points = points.astype('int')
    flattener = np.array([1, width], dtype = 'int').reshape((2, 1))
    indices = np.dot(points, flattener)
    indices = indices.reshape(indices.size)
    if mobject.should_buffer_points():#Is this alright?
        for tweak in [
            indices + 1, 
            indices + width, 
            indices + width + 1
            ]:
            indices = np.append(indices, tweak)
        rgbs = np.array(list(rgbs) * 4)
    admissibles = (indices < height * width) * (indices > 0)
    indices = indices[admissibles]
    rgbs = rgbs[admissibles]
    rgbs = (rgbs * 255).astype(int)
    pixels = pixels.reshape((height * width, 3))
    pixels[indices] = rgbs.reshape((rgbs.size/3), 3)#WHY?
    pixels = pixels.reshape((height, width, 3)).astype('uint8')
    return pixels

def write_to_gif(scene, name):
    #TODO, find better means of compression
    if not name.endswith(".gif"):
        name += ".gif"
    filepath = os.path.join(GIF_DIR, name)
    temppath = os.path.join(GIF_DIR, "Temp.gif")
    print "Writing " + name + "..."
    images = [Image.fromarray(frame) for frame in scene.frames]
    writeGif(temppath, images, scene.display_config["frame_duration"])
    print "Compressing..."
    os.system("gifsicle -O " + temppath + " > " + filepath)
    os.system("rm " + temppath)

def write_to_movie(scene, name):
    frames = scene.frames
    progress_bar = progressbar.ProgressBar(maxval=len(frames))
    progress_bar.start()
    print "writing " + name + "..."

    filepath = os.path.join(MOVIE_DIR, name)
    filedir = "/".join(filepath.split("/")[:-1])
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    rate = int(1/scene.display_config["frame_duration"])

    tmp_stem = os.path.join(TMP_IMAGE_DIR, name.replace("/", "_"))
    suffix = "-%04d.png"
    image_files = []
    for frame, count in zip(frames, it.count()):
        progress_bar.update(int(0.9 * count))
        Image.fromarray(frame).save(tmp_stem + suffix%count)
        image_files.append(tmp_stem + suffix%count)
    commands = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        tmp_stem + suffix,
        "-c:v",
        "libx264",
        "-vf",
        "fps=%d,format=yuv420p"%rate,
        filepath + ".mp4"
    ]
    os.system(" ".join(commands))
    for image_file in image_files:
        os.remove(image_file)
    progress_bar.finish()


    # vs = VideoSink(scene.shape, filepath, rate)
    # for frame in frames:
    #     vs.run(frame)
    # vs.close()
    # progress_bar.finish()


    # filepath = os.path.join(MOVIE_DIR, name + ".mov")
    # fourcc = cv2.cv.FOURCC(*"8bps")
    # out = cv2.VideoWriter(
    #     filepath, fourcc, 1.0/scene.frame_duration, (DEFAULT_WIDTH, DEFAULT_HEIGHT), True
    # )
    # progress = 0
    # for frame in frames:
    #     if progress == 0:
    #         print "Writing movie"
    #     progress_bar.update(progress)
    #     r, g, b = cv2.split(np.array(frame))
    #     bgr_frame = cv2.merge([b, g, r])
    #     out.write(bgr_frame)
    #     progress += 1
    # out.release()
    # progress_bar.finish()


# class VideoSink(object):
#     def __init__(self, size, filename="output", rate=10, byteorder="bgra") :
#             self.size = size
#             cmdstring  = [
#                 'mencoder',
#                 '/dev/stdin',
#                 '-demuxer', 'rawvideo',
#                 '-rawvideo', 'w=%i:h=%i'%size[::-1]+":fps=%i:format=%s"%(rate,byteorder),
#                 '-o', filename+'.mp4',
#                 '-ovc', 'lavc',
#             ]
#             self.p = subprocess.Popen(cmdstring, stdin=subprocess.PIPE, shell=False)

#     def run(self, image):
#         """
#         Image comes in as HEIGHTxWIDTHx3 numpy array, order rgb
#         """
#         assert image.shape == self.size + (3,)
#         r, g, b = [image[:,:,i].astype('uint32') for i in range(3)]
#         a = np.ones(image.shape[:2], dtype = 'uint32')
#         #hacky
#         image = sum([
#             arr << 8**i 
#             for arr, i in zip(range(4), [a, r, g, b])
#         ])
#         self.p.stdin.write(image.tostring())

#     def close(self):
#         self.p.stdin.close()



















