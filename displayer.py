import numpy as np
import itertools as it
import os
from PIL import Image
import subprocess
import cv2
from colour import Color
import progressbar

from mobject import *
from constants import *

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
    a square of pixels tickness x thickness big surrounding it
    """
    original = np.array(pixel_indices)
    original_rgbs = np.array(rgbs)
    for nudge in range(-thickness/2+1, thickness/2+1):
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
    frames = scene.frames
    progress_bar = progressbar.ProgressBar(maxval=len(frames))
    progress_bar.start()
    print "writing " + name + "..."

    filepath = os.path.join(MOVIE_DIR, name)
    filedir = "/".join(filepath.split("/")[:-1])
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    rate = int(1/scene.frame_duration)

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



















