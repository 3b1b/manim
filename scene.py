from PIL import Image
from colour import Color
import numpy as np
import warnings
import time
import os
import copy
import progressbar
import inspect


from helpers import *
from mobject import *
from animate import *
import displayer as disp

class Scene(object):
    def __init__(self, 
                 frame_duration = DEFAULT_FRAME_DURATION,
                 name = None):
        self.frame_duration = frame_duration
        self.frames = []
        self.mobjects = set([])
        self.name = name

    def __str__(self):
        return self.name or "Babadinook" #TODO

    def add(self, *mobjects):
        #TODO, perhaps mobjects should be ordered, for foreground/background
        self.mobjects.update(mobjects)

    def remove(self, *mobjects):
        self.mobjects.difference_update(mobjects)

    def animate(self, animations,
                dither_time = DEFAULT_DITHER_TIME):
        if isinstance(animations, Animation):
            animations = [animations]
        self.pause(dither_time)
        run_time = max([anim.run_time for anim in animations])

        print "Generating animations..."
        progress_bar = progressbar.ProgressBar(maxval=run_time)
        progress_bar.start()

        for t in np.arange(0, run_time, self.frame_duration):
            progress_bar.update(t)
            for anim in animations:
                anim.update(t)
            self.frames.append(self.get_frame(*animations))
        for anim in animations:
            anim.clean_up()
        progress_bar.finish()

    def pause(self, duration):
        self.frames += [self.get_frame()]*int(duration / self.frame_duration)

    def get_frame(self, *animations):
        #Include animations so as to display mobjects not in the list
        #TODO, This is temporary
        mob = list(self.mobjects)[0]
        return disp.get_image(mob.points, mob.rgbs)

    def write_to_gif(self, name = None, end_dither_time = DEFAULT_DITHER_TIME):
        self.pause(end_dither_time)
        disp.write_to_gif(self, name or str(self))

    def write_to_movie(self, name = None, end_dither_time = DEFAULT_DITHER_TIME):
        self.pause(end_dither_time)
        disp.write_to_movie(self, name or str(self))









