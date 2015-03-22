import numpy as np
import itertools as it
import os
from PIL import Image
import cv2

from animate import *


def get_image(points, rgbs):
    return Image.fromarray(get_pixels(points, rgbs))

def get_pixels(points, rgbs):
    #TODO, Let z add a depth componenet?
    points = points[:, :2]
    #Flips y-axis
    points[:,1] *= -1
    #Map points to pixel space, then create pixel array first in terms
    #of its flattened version
    points += np.array(
        [SPACE_WIDTH, SPACE_HEIGHT]*points.shape[0]
    ).reshape(points.shape)
    points *= np.array(
        [HEIGHT / (2.0 * SPACE_HEIGHT), WIDTH / (2.0 * SPACE_WIDTH)]*\
        points.shape[0]
    ).reshape(points.shape)
    points = points.astype('int')
    flattener = np.array([1, WIDTH], dtype = 'int').reshape((2, 1))
    indices = np.dot(points, flattener)
    indices = indices.reshape(indices.size)
    admissibles = (indices < HEIGHT * WIDTH) * (indices > 0)
    indices = indices[admissibles]
    rgbs = rgbs[admissibles]
    rgbs = (rgbs * 255).astype(int)
    pixels = np.zeros((HEIGHT * WIDTH, 3))
    pixels[indices] = rgbs
    return pixels.reshape((HEIGHT, WIDTH, 3)).astype('uint8')

def write_to_gif(animation, name):
    #TODO, find better means of compression
    if not name.endswith(".gif"):
        name += ".gif"
    filepath = os.path.join(GIF_DIR, name)
    temppath = os.path.join(GIF_DIR, "Temp.gif")
    print "Writing " + name + "..."
    writeGif(temppath, animation.get_frames(), animation.pause_time)
    print "Compressing..."
    os.system("gifsicle -O " + temppath + " > " + filepath)
    os.system("rm " + temppath)

def write_to_movie(animation, name):
    frames = animation.get_frames()
    progress_bar = progressbar.ProgressBar(maxval=len(frames))
    progress_bar.start()
    print "writing " + name + "..."

    tmp_stem = os.path.join(TMP_IMAGE_DIR, name.replace("/", "_"))
    suffix = "-%04d.png"
    image_files = []
    for frame, count in zip(frames, it.count()):
        progress_bar.update(int(0.9 * count))
        frame.save(tmp_stem + suffix%count)
        image_files.append(tmp_stem + suffix%count)
    filepath = os.path.join(MOVIE_DIR, name + ".mp4")
    filedir = "/".join(filepath.split("/")[:-1])
    if not os.path.exists(filedir):
        os.makedirs(filedir)
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
        "fps=%d,format=yuv420p"%int(1/animation.pause_time),
        filepath
    ]
    os.system(" ".join(commands))
    for image_file in image_files:
        os.remove(image_file)
    progress_bar.finish()


    # filepath = os.path.join(MOVIE_DIR, name + ".mov")
    # fourcc = cv2.cv.FOURCC(*"8bps")
    # out = cv2.VideoWriter(
    #     filepath, fourcc, 1.0/animation.pause_time, (WIDTH, HEIGHT), True
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






















