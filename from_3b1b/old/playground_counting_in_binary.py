#!/usr/bin/env python


import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from mobject.region import  *
from scene.scene import Scene, SceneFromVideo
from script_wrapper import command_line_create_scene
from functools import reduce

MOVIE_PREFIX = "counting_in_binary/"

COUNT_TO_FRAME_NUM = {
    0 : 0,
    1 : 53,
    2 : 84,
    3 : 128,
    4 : 169,
    5 : 208,
    6 : 238,
    7 : 281,
    8 : 331,
    9 : 365,
    10 : 395,
    11 : 435,
    12 : 475,
    13 : 518,
    14 : 556,
    15 : 595,
    16 : 636,
    17 : 676,
    18 : 709,
    19 : 753,
    20 : 790,
    21 : 835,
    22 : 869,
    23 : 903,
    24 : 950,
    25 : 988,
    26 : 1027,
    27 : 1065,
    28 : 1104,
    29 : 1145,
    30 : 1181,
    31 : 1224,
    32 : 1239,
}

class Hand(ImageMobject):
    def __init__(self, num, **kwargs):
        Mobject2D.__init__(self, **kwargs)
        path = os.path.join(
            VIDEO_DIR, MOVIE_PREFIX, "images", "Hand%d.png"%num
        )
        invert = False
        if self.read_in_cached_attrs(path, invert):
            return
        ImageMobject.__init__(self, path, invert)
        center = self.get_center()
        self.center()
        self.rotate(np.pi, axis = RIGHT+UP)
        self.sort_points(lambda p : np.log(complex(*p[:2])).imag)
        self.rotate(np.pi, axis = RIGHT+UP)
        self.shift(center)
        self.cache_attrs(path, invert = False)


class EdgeDetection(SceneFromVideo):
    args_list = [
        ("CountingInBinary.m4v", 35, 70),
        ("CountingInBinary.m4v", 0, 100),
        ("CountingInBinary.m4v", 10, 50),
    ]
    @staticmethod
    def args_to_string(filename, t1, t2):
        return "-".join([filename.split(".")[0], str(t1), str(t2)])

    def construct(self, filename, t1, t2):
        path = os.path.join(VIDEO_DIR, filename)
        SceneFromVideo.construct(self, path)
        self.apply_gaussian_blur()
        self.apply_edge_detection(t1, t2)

class BufferedCounting(SceneFromVideo):
    def construct(self):
        path = os.path.join(VIDEO_DIR, "CountingInBinary.m4v")
        time_range = (3, 42)
        SceneFromVideo.construct(self, path, time_range = time_range)
        self.buffer_pixels(spreads = (3, 2))
        # self.make_all_black_or_white()

    def buffer_pixels(self, spreads = (2, 2)):
        ksize = (5, 5)
        sigmaX = 10
        threshold1 = 35
        threshold2 = 70

        matrices = [
            thick_diagonal(dim, spread)
            for dim, spread in zip(self.shape, spreads)
        ]
        for frame, index in zip(self.frames, it.count()):
            print(index + "of" + len(self.frames))
            blurred = cv2.GaussianBlur(frame, ksize, sigmaX)
            edged = cv2.Canny(blurred, threshold1, threshold2)
            buffed = reduce(np.dot, [matrices[0], edged, matrices[1]])
            for i in range(3):
                self.frames[index][:,:,i] = buffed


    def make_all_black_or_white(self):
        self.frames = [
            255*(frame != 0).astype('uint8')
            for frame in self.frames
        ]

class ClearLeftSide(SceneFromVideo):
    args_list = [
        ("BufferedCounting",),
    ]
    @staticmethod
    def args_to_string(scenename):
        return scenename

    def construct(self, scenename):
        path = os.path.join(VIDEO_DIR, MOVIE_PREFIX, scenename + ".mp4")
        SceneFromVideo.construct(self, path)
        self.set_color_region_over_time_range(
            Region(lambda x, y : x < -1, shape = self.shape)
        )



class DraggedPixels(SceneFromVideo):
    args_list = [
        ("BufferedCounting",),
        ("CountingWithLeftClear",),
    ]
    @staticmethod
    def args_to_string(*args):
        return args[0]

    def construct(self, video):
        path = os.path.join(VIDEO_DIR, MOVIE_PREFIX, video+".mp4")
        SceneFromVideo.construct(self, path)
        self.drag_pixels()

    def drag_pixels(self, num_frames_to_drag_over = 5):
        for index in range(len(self.frames)-1, 0, -1):
            self.frames[index] = np.max([
                self.frames[k]
                for k in range(
                    max(index-num_frames_to_drag_over, 0),
                    index
                )
            ], axis = 0)


class SaveEachNumber(SceneFromVideo):
    def construct(self):
        path = os.path.join(VIDEO_DIR, MOVIE_PREFIX, "ClearLeftSideBufferedCounting.mp4")
        SceneFromVideo.construct(self, path)
        for count in COUNT_TO_FRAME_NUM:
            path = os.path.join(
                VIDEO_DIR, MOVIE_PREFIX, "images",
                "Hand%d.png"%count
            )
            Image.fromarray(self.frames[COUNT_TO_FRAME_NUM[count]]).save(path)

class ShowCounting(SceneFromVideo):
    args_list = [
        ("CountingWithLeftClear",),
        ("ClearLeftSideBufferedCounting",),
    ]
    @staticmethod
    def args_to_string(filename):
        return filename

    def construct(self, filename):
        path = os.path.join(VIDEO_DIR, MOVIE_PREFIX, filename + ".mp4")
        SceneFromVideo.construct(self, path)
        total_time = len(self.frames)*self.frame_duration
        for count in range(32):
            print(count)
            mob = TexMobject(str(count)).scale(1.5)
            mob.shift(0.3*LEFT).to_edge(UP, buff = 0.1)
            index_range = list(range(
                max(COUNT_TO_FRAME_NUM[count]-10, 0),
                COUNT_TO_FRAME_NUM[count+1]-10))
            for index in index_range:
                self.frames[index] = disp.paint_mobject(
                    mob, self.frames[index]
                )

class ShowFrameNum(SceneFromVideo):
    args_list = [
        ("ClearLeftSideBufferedCounting",),
    ]
    @staticmethod
    def args_to_string(filename):
        return filename

    def construct(self, filename):
        path = os.path.join(VIDEO_DIR, MOVIE_PREFIX, filename+".mp4")
        SceneFromVideo.construct(self, path)
        for frame, count in zip(self.frames, it.count()):
            print(count + "of" + len(self.frames))
            mob = Mobject(*[
                TexMobject(char).shift(0.3*x*RIGHT)
                for char, x, in zip(str(count), it.count())
            ])
            self.frames[count] = disp.paint_mobject(
                mob.to_corner(UP+LEFT),
                frame
            )





if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)
