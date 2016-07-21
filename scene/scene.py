from PIL import Image
from colour import Color
import numpy as np
import itertools as it
import warnings
import time
import os
import copy
from tqdm import tqdm as ProgressDisplay
import inspect
import subprocess as sp

from helpers import *

from camera import Camera
from tk_scene import TkSceneRoot
from mobject import Mobject

class Scene(object):
    CONFIG = {
        "camera_config"  : {},
        "frame_duration" : DEFAULT_FRAME_DURATION,
        "construct_args" : [],
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.camera = Camera(**self.camera_config)
        self.frames = []
        self.mobjects = []
        self.num_animations = 0

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

    ### Only these methods should touch the camera

    def set_camera(self, camera):
        self.camera = camera

    def get_frame(self):
        return self.camera.get_image()

    def update_frame(self, mobjects = None, background = None, **kwargs):
        if mobjects is None:
            mobjects = self.mobjects
        if background is not None:
            self.camera.set_image(background)
        else:
            self.camera.reset()
        self.camera.capture_mobjects(mobjects, **kwargs)

    def freeze_background(self):
        self.update_frame()
        self.set_camera(Camera(self.get_frame()))
        self.clear()
    ###

    def extract_mobjects_with_points(self, *mobjects):
        return list(it.chain(*[
            m.family_members_with_points()
            for m in mobjects
        ]))
        

    def add(self, *mobjects):
        """
        Mobjects will be displayed, from background to foreground,
        in the order with which they are entered.

        Scene class only keeps track of top-level monjects, all 
        concerns with submobjects is left to animations and subclass
        implementations of the construct method.
        """
        if not all_elements_are_instances(mobjects, Mobject):
            raise Exception("Adding something which is not a mobject")
        old_mobjects = filter(lambda m : m not in mobjects, self.mobjects)
        self.mobjects = old_mobjects + list(mobjects)
        return self

    def add_mobjects_among(self, values):
        """
        So a scene can just add all mobjects it's defined up to that point
        by calling add_mobjects_among(locals().values())
        """
        mobjects = filter(lambda x : isinstance(x, Mobject), values)
        self.add(*mobjects)
        return self

    def remove(self, *mobjects):
        if not all_elements_are_instances(mobjects, Mobject):
            raise Exception("Removing something which is not a mobject")
        mobjects = list(it.chain(*[m.submobject_family() for m in mobjects]))
        if len(mobjects) == 0:
            return
        self.mobjects = filter(
            lambda m : not set(
                m.family_members_with_points()
            ).issubset(mobjects),
            self.mobjects
        )
        return self

    def bring_to_front(self, mobject):
        self.add(mobject)
        return self

    def bring_to_back(self, mobject):
        self.remove(mobject)
        self.mobjects = [mobject] + self.mobjects
        return self

    def clear(self):
        self.mobjects = []
        return self

    def get_mobjects(self):
        return list(self.mobjects)

    def get_mobject_copies(self):
        return [m.copy() for m in self.mobjects]

    def align_run_times(self, *animations, **kwargs):
        if "run_time" in kwargs:
            run_time = kwargs["run_time"]
            for animation in animations:
                animation.set_run_time(run_time)
        else:
            max_run_time = max([a.run_time for a in animations])
            for animation in animations:
                if animation.run_time != max_run_time:
                    new_rate_func = squish_rate_func(
                        animation.get_rate_func(),
                        0, 1./max_run_time
                    )
                    animation.set_rate_func(new_rate_func)
                    animation.set_run_time(max_run_time)
        return animations

    def separate_moving_and_static_mobjects(self, *animations):
        """
        """
        moving_mobjects = [anim.mobject for anim in animations]
        moving_parts = self.extract_mobjects_with_points(*moving_mobjects)
        static_mobjects = filter(
            lambda m : m not in moving_parts,
            self.extract_mobjects_with_points(*self.mobjects)
        )
        return moving_mobjects, static_mobjects

    def get_time_progression(self, animations):
        run_time = animations[0].run_time
        times = np.arange(0, run_time, self.frame_duration)
        time_progression = ProgressDisplay(times)
        time_progression.set_description("".join([
            "Animation %d: "%self.num_animations,
            str(animations[0]),
            (", etc." if len(animations) > 1 else ""),
        ]))
        return time_progression


    def play(self, *animations, **kwargs):
        if len(animations) == 0:
            raise Warning("Called Scene.play with no animations")
            return
        self.num_animations += 1

        animations = self.align_run_times(*animations, **kwargs)
        moving_mobjects, static_mobjects = \
            self.separate_moving_and_static_mobjects(*animations)
        self.update_frame(static_mobjects)
        static_image = self.get_frame()

        for t in self.get_time_progression(animations):
            for animation in animations:
                animation.update(t / animation.run_time)
            self.update_frame(moving_mobjects, static_image)
            self.frames.append(self.get_frame())

        self.clean_up_animations(*animations)
        return self

    def clean_up_animations(self, *animations):
        self.mobjects_from_last_animation = []        
        for animation in animations:
            animation.clean_up()
            if animation.is_remover():
                self.remove(animation.mobject)
            else:
                self.add(animation.mobject)
            self.mobjects_from_last_animation.append(animation.mobject)
        return self

    def get_mobjects_from_last_animation(self):
        if hasattr(self, "mobjects_from_last_animation"):
            return self.mobjects_from_last_animation
        return []

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

        moving_mobjects, static_mobjects = \
            self.separate_moving_and_static_mobjects(*animations)
        for t in np.arange(t0, t1, self.frame_duration):
            for animation in animations:
                animation.update((t-t0)/(t1 - t0))
            index = int(t/self.frame_duration)
            self.update_frame(moving_mobjects, self.frames[index])
            self.frames[index] = self.get_frame()
        for animation in animations:
            animation.clean_up()
        return self

    def dither(self, duration = DEFAULT_DITHER_TIME):
        self.update_frame()
        self.frames += [self.get_frame()]*int(duration / self.frame_duration)
        return self

    def repeat_frames(self, num):
        self.frames = self.frames*num
        return self

    def reverse_frames(self):
        self.frames.reverse()
        return self

    def invert_colors(self):
        white_frame = 255*np.ones(self.get_frame().shape, dtype = 'uint8')
        self.frames = [
            white_frame-frame
            for frame in self.frames
        ]
        return self

    def show_frame(self):
        self.update_frame()
        Image.fromarray(self.get_frame()).show()

    def preview(self):
        TkSceneRoot(self)

    def save_image(self, directory = MOVIE_DIR, name = None):
        path = os.path.join(directory, "images")
        file_name = (name or str(self)) + ".png"
        full_path = os.path.join(path, file_name)
        if not os.path.exists(path):
            os.makedirs(path)
        Image.fromarray(self.get_frame()).save(full_path)

    def get_movie_file_path(self, name, extension):
        file_path = os.path.join(MOVIE_DIR, name)
        if not file_path.endswith(extension):
            file_path += extension
        directory = os.path.split(file_path)[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        return file_path

    def write_to_movie(self, name = None):
        if len(self.frames) == 0:
            print "No frames, so I'm not writing anything"
            return
        if name is None:
            name = str(self)
        file_path = self.get_movie_file_path(name, ".mp4")
        print "Writing to %s"%file_path

        fps = int(1/self.frame_duration)
        height, width = self.camera.pixel_shape

        command = [
            FFMPEG_BIN,
            '-y',                 # overwrite output file if it exists
            '-f', 'rawvideo',
            '-vcodec','rawvideo',
            '-s', '%dx%d'%(width, height), # size of one frame
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
        for frame in self.frames:
            process.stdin.write(frame.tostring())
        process.stdin.close()
        process.wait()        

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



























