#!/usr/bin/env python

import numpy as np
import itertools as it
from copy import deepcopy
import sys


from animation import *
from mobject import *
from constants import *
from region import *
from scene import Scene, SceneFromVideo
from script_wrapper import command_line_create_scene

MOVIE_PREFIX = "counting_in_binary/"
BASE_HAND_FILE = os.path.join(MOVIE_DIR, MOVIE_PREFIX, "Base.mp4")
FORCED_FRAME_DURATION = 0.02
TIME_RANGE = (0, 42)
INITIAL_PADDING = 27
NUM_GOOD_FRAMES = 1223

ALGORITHM_TEXT = [
    """
    \\begin{flushleft}
    Turn up the rightmost finger that is down.
    """, """
    Turn down all fingers to its right.
    \\end{flushleft}
    """
]
FINGER_WORDS = [
    "Thumb",
    "Index Finger",
    "Middle Finger",
    "Ring Finger",
    "Pinky",
]

COUNT_TO_FRAME_NUM = {
    0 : 0,
    1 : 27,
    2 : 76,
    3 : 110,
    4 : 163,
    5 : 189,
    6 : 226,
    7 : 264,
    8 : 318,
    9 : 356,
    10 : 384,
    11 : 423,
    12 : 457,
    13 : 513,
    14 : 528,
    15 : 590,
    16 : 620,
    17 : 671,
    18 : 691,
    19 : 740,
    20 : 781,
    21 : 810,
    22 : 855,
    23 : 881,
    24 : 940,
    25 : 970,
    26 : 1014,
    27 : 1055,
    28 : 1092,
    29 : 1143,
    30 : 1184,
    31 : 1219,
}
    
class Hand(ImageMobject):
    def __init__(self, num, **kwargs):
        Mobject2D.__init__(self, **kwargs)
        path = os.path.join(
            MOVIE_DIR, MOVIE_PREFIX, "images", "Hand%d.png"%num
        )
        invert = False
        if self.read_in_cached_attrs(path, invert):
            return
        ImageMobject.__init__(self, path, invert = invert)
        center = self.get_center()
        self.center()
        self.rotate(np.pi, axis = RIGHT+UP)
        self.sort_points(lambda p : np.log(complex(*p[:2])).imag)
        self.rotate(np.pi, axis = RIGHT+UP)
        self.shift(center)
        self.cache_attrs(path, invert = False)

    # def highlight_thumb(self, color = "yellow"):
    #     self.highlight(
    #         color = color,
    #         condition = lambda p : p[0] > 4.5 and p[1] > -1.5
    #     )

def get_algorithm():
    return text_mobject(ALGORITHM_TEXT)
    
def get_finger_colors():
    return list(Color("yellow").range_to("red", 5))

def five_char_binary(num):
    result = bin(num)[2:]
    return (5-len(result))*"0" + result

def read_reversed_binary(string):
    return sum([
        2**count if char == '1' else 0
        for count, char in zip(it.count(), string)
    ])

class LeftHand(Hand):
    def __init__(self, num, **kwargs):
        Hand.__init__(
            self,
            read_reversed_binary(five_char_binary(num)), 
            **kwargs
        )
        self.rotate(np.pi, UP)
        self.to_edge(LEFT)

def get_hand_map(which_hand = "right"):
    if which_hand == "right":
        Class = Hand
    elif which_hand == "left":
        Class = LeftHand
    else:
        print "Bad arg, bro"
        return
    return dict([
        (num, Class(num))
        for num in range(32)
    ])

class OverHand(SceneFromVideo):
    def construct(self):
        SceneFromVideo.construct(self, BASE_HAND_FILE)
        self.frame_duration = FORCED_FRAME_DURATION
        self.frames = self.frames[:NUM_GOOD_FRAMES]


class SaveEachNumber(OverHand):
    def construct(self):
        OverHand.construct(self)
        for count in COUNT_TO_FRAME_NUM:
            path = os.path.join(
                MOVIE_DIR, MOVIE_PREFIX, "images", 
                "Hand%d.png"%count
            )
            Image.fromarray(self.frames[COUNT_TO_FRAME_NUM[count]]).save(path)

    def write_to_movie(self, name = None):
        print "Why bother writing to movie..."

class ShowCounting(OverHand):
    def construct(self):
        OverHand.construct(self)
        self.frames = INITIAL_PADDING*[self.frames[0]] + self.frames
        num_frames = len(self.frames)
        self.frames = [
            disp.paint_mobject(
                self.get_counting_mob(32*count // num_frames),
                frame
            )
            for frame, count in zip(self.frames, it.count())
        ]

    def get_counting_mob(self, count):
        mob = tex_mobject(str(count))
        mob.scale(2)
        mob.shift(LEFT)
        mob.to_edge(UP, buff = 0.1)
        return mob


class ShowFrameNum(OverHand):
    def construct(self):
        OverHand.construct(self)
        for frame, count in zip(self.frames, it.count()):
            print count, "of", len(self.frames)
            mob = CompoundMobject(*[
                tex_mobject(char).shift(0.3*x*RIGHT)
                for char, x, in zip(str(count), it.count())
            ])
            self.frames[count] = disp.paint_mobject(
                mob.to_corner(UP+LEFT),
                frame
            )

class CountTo1023(Scene):
    def construct(self):
        rh_map = get_hand_map("right")
        lh_map = get_hand_map("left")
        for mob in rh_map.values()+lh_map.values():
            mob.scale(0.9)
            mob.to_edge(DOWN, buff = 0)
        for mob in rh_map.values():
            mob.to_edge(RIGHT)
        for mob in lh_map.values():
            mob.to_edge(LEFT)
        def get_num(count):
            return CompoundMobject(*[
                tex_mobject(char).shift(0.35*x*RIGHT)
                for char, x, in zip(str(count), it.count())
            ]).center().to_edge(UP)
        self.frames = [
            disp.paint_mobject(CompoundMobject(
                rh_map[count%32], lh_map[count//32], get_num(count)
            ))
            for count in range(2**10)
        ]

class Introduction(Scene):
    def construct(self):
        words = text_mobject("""
            First, let's see how to count
            to 31 on just one hand...
        """)
        hand = Hand(0)
        for mob in words, hand:
            mob.sort_points(lambda p : p[0])

        self.add(words)
        self.dither()
        self.animate(DelayByOrder(Transform(words, hand)))
        self.dither()

class ShowReadingRule(Scene):
    def construct(self):
        pass

class CountWithReadingRule(ShowCounting):
    def get_counting_mob(self, count):
        pass

class ShowIncrementRule(Scene):
    def construct(self):
        pass




if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)











