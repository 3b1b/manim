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
from animation import *
import displayer as disp
from tk_scene import TkSceneRoot

class Scene(object):
    DEFAULT_CONFIG = {
        "display_config" : PRODUCTION_QUALITY_DISPLAY_CONFIG,
        "construct_args" : [],
        "background" : None,
        "start_dither_time" : DEFAULT_DITHER_TIME,
        "announce_construction" : False,
    }
    def __init__(self, **kwargs):
        digest_config(self, Scene, kwargs)
        if self.announce_construction:
            print "Constructing %s..."%str(self)
        self.frame_duration = self.display_config["frame_duration"]
        self.frames = []
        self.mobjects = []
        if self.background:
            self.original_background = np.array(background)
            #TODO, Error checking?
        else:
            self.original_background = np.zeros(
                (self.display_config["height"], self.display_config["width"], 3),
                dtype = 'uint8'
            )
        self.background = self.original_background
        self.shape = self.background.shape[:2]
        #TODO, space shape
        self.construct(*self.construct_args)

    def construct(self):
        pass #To be implemented in subclasses

    def __str__(self):
        if hasattr(self, "name"):
            return self.name
        return self.__class__.__name__ + \
               self.args_to_string(*self.construct_args)
    def set_name(self, name):
        self.name = name
        return self

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
        return self

    def add_local_mobjects(self):
        """
        So a scene can just add all mobjects it's defined up to that point
        """
        caller_locals = inspect.currentframe().f_back.f_locals
        self.add(*filter(
            lambda m : isinstance(m, Mobject), 
            caller_locals.values()
        ))

    def remove(self, *mobjects):
        for mobject in mobjects:
            if not isinstance(mobject, Mobject):
                raise Exception("Removing something which is not a mobject")
            while mobject in self.mobjects:
                self.mobjects.remove(mobject)
        return self

    def clear(self):
        self.reset_background()
        self.remove(*self.mobjects)
        return self

    def highlight_region(self, region, color = None):
        self.background = disp.paint_region(
            region, 
            image_array = self.background, 
            color = color,
        )
        return self

    def highlight_region_over_time_range(self, region, time_range = None, color = "black"):
        if time_range:
            frame_range = map(lambda t : t / self.frame_duration, time_range)
            frame_range[0] = max(frame_range[0], 0)
            frame_range[1] = min(frame_range[1], len(self.frames))
        else:
            frame_range = (0, len(self.frames))
        for index in range(frame_range[0], frame_range[1]):
            self.frames[index] = disp.paint_region(
                region,
                image_array = self.frames[index],
                color = color
            )

    def reset_background(self):
        self.background = self.original_background
        return self

    def paint_into_background(self, *mobjects):
        #This way current mobjects don't have to be redrawn with
        #every change, and one can later call "apply" without worrying
        #about it applying to these mobjects
        self.background = disp.paint_mobjects(mobjects, self.background)
        return self

    def play(self, *animations, **kwargs):
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
            for animation in animations:
                animation.update(t / animation.run_time)
            new_frame = disp.paint_mobjects(moving_mobjects, background)
            self.frames.append(new_frame)
        for animation in animations:
            animation.clean_up()
        self.add(*moving_mobjects)
        progress_bar.finish()
        return self

    def play_over_time_range(self, t0, t1, *animations):
        needed_scene_time = max(abs(t0), abs(t1))
        existing_scene_time = len(self.frames)*self.frame_duration
        if existing_scene_time < needed_scene_time:
            self.dither(needed_scene_time - existing_scene_time)
            existing_scene_time = needed_scene_time
        #So negative values may be used
        if t0 < 0:
            t0 = float(t0)%existing_scene_time
        if t1 < 0:
            t1 = float(t1)%existing_scene_time
        t0, t1 = min(t0, t1), max(t0, t1)    

        moving_mobjects = [anim.mobject for anim in animations]
        for t in np.arange(t0, t1, self.frame_duration):
            for animation in animations:
                animation.update((t-t0)/(t1 - t0))
            index = int(t/self.frame_duration)
            self.frames[index] = disp.paint_mobjects(moving_mobjects, self.frames[index])
        for animation in animations:
            animation.clean_up()
        return self

    def apply(self, mob_to_anim_func, **kwargs):
        self.play(*[
            mob_to_anim_func(mobject)
            for mobject in self.mobjects
        ])

    def get_frame(self):
        return disp.paint_mobjects(self.mobjects, self.background)

    def dither(self, duration = DEFAULT_DITHER_TIME):
        self.frames += [self.get_frame()]*int(duration / self.frame_duration)
        return self

    def repeat(self, num):
        self.frames = self.frames*num
        return self

    def write_to_gif(self, name = None, 
                     end_dither_time = DEFAULT_DITHER_TIME):
        self.dither(end_dither_time)
        disp.write_to_gif(self, name or str(self))

    def write_to_movie(self, name = None):
        if len(self.frames) == 0:
            print "No frames, I'll just save an image instead"
            self.show_frame()
            self.save_image(name = name)
            return
        disp.write_to_movie(self, name or str(self))

    def show_frame(self):
        Image.fromarray(self.get_frame()).show()

    def preview(self):
        TkSceneRoot(self)

    def save_image(self, directory = MOVIE_DIR, name = None):
        path = os.path.join(directory, name or str(self)) + ".png"
        Image.fromarray(self.get_frame()).save(path)

    # To list possible args that subclasses have
    # Elements should always be a tuple
    args_list = []

    # For subclasses to turn args in the above  
    # list into stings which can be appended to the name
    @staticmethod
    def args_to_string(*args):
        return ""
    @staticmethod
    def string_to_args(string):
        raise Exception("string_to_args Not Implemented!")



























