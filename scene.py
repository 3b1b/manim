from PIL import Image
from colour import Color
import numpy as np
import itertools as it
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
                 name = None,
                 frame_duration = DEFAULT_FRAME_DURATION,
                 background = None,
                 height = DEFAULT_HEIGHT,
                 width = DEFAULT_WIDTH,):
        self.frame_duration = frame_duration
        self.frames = []
        self.mobjects = []
        if background:
            self.background = np.array(background)
            #TODO, Error checking?
        else:
            self.background = np.zeros((height, width, 3))
        self.shape = self.background.shape[:2]mobmov
        self.name = name

    def __str__(self):
        return self.name or "Babadinook" #TODO

    def add(self, *mobjects):
        """
        Mobjects will be displayed, from background to foreground,
        in the order with which they are entered.
        """
        for mobject in mobjects:
            #In case it's already in there, it should 
            #now be closer to the foreground.
            self.remove(mobject)
            self.mobjects.append(mobject)

    def remove(self, *mobjects):
        for mobject in mobjects:
            while mobject in self.mobjects:
                self.mobjects.remove(mobject)

    def animate(self, *mobmovs):
        #Runtime is determined by the first mobmov
        run_time = mobmovs[0].run_time
        moving_mobjects = [a.mobject for a in mobmovs]
        self.remove(*moving_mobjects)
        background = self.get_frame()

        print "Generating mobject movements..."
        progress_bar = progressbar.ProgressBar(maxval=run_time)
        progress_bar.start()

        for t in np.arange(0, run_time, self.frame_duration):
            progress_bar.update(t)
            new_frame = background
            for mobmov in mobmovs:
                mobmov.update(t / mobmov.run_time)
                new_frame = disp.paint_mobject(mobmov.mobject, new_frame)
            self.frames.append(new_frame)
        for mobmov in mobmovs:
            mobmov.clean_up()
        self.add(*moving_mobjects)
        progress_bar.finish()

    def get_frame(self):
        frame = self.background
        for mob in self.mobjects:
            frame = disp.paint_mobject(mob, frame)
        return frame

    def dither(self, duration = DEFAULT_DITHER_TIME):
        self.frames += [self.get_frame()]*int(duration / self.frame_duration)

    def write_to_gif(self, name = None, end_dither_time = DEFAULT_DITHER_TIME):
        self.dither(end_dither_time)
        disp.write_to_gif(self, name or str(self))

    def write_to_movie(self, name = None, end_dither_time = DEFAULT_DITHER_TIME):
        self.dither(end_dither_time)
        disp.write_to_movie(self, name or str(self))









