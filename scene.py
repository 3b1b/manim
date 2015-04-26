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
from image_mobject import *
from animation import *
import displayer as disp

DEFAULT_COUNT_NUM_OFFSET = (SPACE_WIDTH - 1, SPACE_HEIGHT - 1, 0)
DEFAULT_COUNT_RUN_TIME   = 5.0

class Scene(object):
    def __init__(self, 
                 name = None,
                 frame_duration = DEFAULT_FRAME_DURATION,
                 background = None,
                 height = DEFAULT_HEIGHT,
                 width = DEFAULT_WIDTH,
                 start_dither_time = DEFAULT_DITHER_TIME):
        self.frame_duration = frame_duration
        self.frames = []
        self.mobjects = []
        if background:
            self.original_background = np.array(background)
            #TODO, Error checking?
        else:
            self.original_background = np.zeros(
                (height, width, 3),
                dtype = 'uint8'
            )
        self.background = self.original_background
        self.shape = self.background.shape[:2]
        #TODO, space shape
        self.name = name

    def __str__(self):
        return self.name or "Babadinook" #TODO

    def set_name(self, name):
        self.name = name

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

    def highlight_region(self, region, color = None):
        self.background = disp.paint_region(
            region, 
            image_array = self.background, 
            color = color,
        )

    def reset_background(self):
        self.background = self.original_background

    def animate(self, *animations, **kwargs):
        if "run_time" in kwargs:
            run_time = kwargs["run_time"]
        else:
            run_time = animations[0].run_time
        for animation in animations:
            animation.set_run_time(run_time)
        moving_mobjects = [anim.mobject for anim in animations]
        self.remove(*moving_mobjects)
        background = self.get_frame()

        print "Generating " + ", ".join(map(str, animations))
        progress_bar = progressbar.ProgressBar(maxval=run_time)
        progress_bar.start()

        for t in np.arange(0, run_time, self.frame_duration):
            progress_bar.update(t)
            new_frame = background
            for animation in animations:
                animation.update(t / animation.run_time)
                new_frame = disp.paint_mobject(animation.mobject, new_frame)
            self.frames.append(new_frame)
        for animation in animations:
            animation.clean_up()
        self.add(*moving_mobjects)
        progress_bar.finish()

    def count(self, items, item_type = "mobject", *args, **kwargs):
        if item_type == "mobject":
            self.count_mobjects(items, *args, **kwargs)
        elif item_type == "region":
            self.count_regions(items, *args, **kwargs)

    def count_mobjects(
        self, mobjects, mode = "highlight",
        color = "red", 
        num_offset = DEFAULT_COUNT_NUM_OFFSET,
        run_time   = DEFAULT_COUNT_RUN_TIME):
        """
        Note: Leaves scene with a "number" attribute 
        for the final number mobject.

        mode can be "highlight", "show_creation" or "show", otherwise
        a warning is given and nothing is animating during the count
        """
        if len(mobjects) > 50: #TODO
            raise Exception("I don't know if you should be counting \
                             too many mobjects...")
        if mode not in ["highlight", "show_creation", "show"]:
            raise Warning("Unknown mode")
        frame_time = run_time / len(mobjects)
        if mode == "highlight":
            self.add(*mobjects)
        for mob, num in zip(mobjects, it.count(1)):
            num_mob = tex_mobject(str(num))
            num_mob.center().shift(num_offset)
            self.add(num_mob)
            if mode == "highlight":
                original_color = mob.color
                mob.highlight(color)
                self.dither(frame_time)
                mob.highlight(original_color)
            if mode == "show_creation":
                self.animate(ShowCreation(mob, run_time = frame_time))
            if mode == "show":
                self.add(mob)
                self.dither(frame_time)
            self.remove(num_mob)
        self.add(num_mob)
        self.number = num_mob

    def count_regions(self, regions, 
                      mode = "one_at_a_time",
                      num_offset = DEFAULT_COUNT_NUM_OFFSET,
                      run_time   = DEFAULT_COUNT_RUN_TIME,
                      **unused_kwargsn):
        if mode not in ["one_at_a_time", "show_all"]:
            raise Warning("Unknown mode")
        frame_time = run_time / (len(regions))
        for region, count in zip(regions, it.count(1)):
            num_mob = tex_mobject(str(count))
            num_mob.center().shift(num_offset)
            self.add(num_mob)
            self.highlight_region(region)
            self.dither(frame_time)
            if mode == "one_at_a_time":
                self.reset_background()
            self.remove(num_mob)
        self.add(num_mob)
        self.number = num_mob


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

    def show(self):
        Image.fromarray(self.get_frame()).show()









