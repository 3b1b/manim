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
from mobject import Mobject, VMobject
from animation import Animation
from animation.animation import sync_animation_run_times_and_rate_funcs
from animation.transform import MoveToTarget

class Scene(object):
    CONFIG = {
        "camera_class"     : Camera,
        "camera_config"    : {},
        "frame_duration"   : LOW_QUALITY_FRAME_DURATION,
        "construct_args"   : [],
        "skip_animations"  : False,
        "write_to_movie"   : True,
        "save_frames"      : False,
        "output_directory" : MOVIE_DIR,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.camera = self.camera_class(**self.camera_config)
        self.mobjects = []
        self.foreground_mobjects = []
        self.num_plays = 0
        self.saved_frames = []

        self.setup()
        if self.write_to_movie:
            self.open_movie_pipe()
        self.construct(*self.construct_args)
        if self.write_to_movie:
            self.close_movie_pipe()

    def setup(self):
        """
        This is meant to be implement by any scenes which
        are comonly subclassed, and have some common setup
        involved before the construct method is called.
        """
        pass

    def construct(self):
        pass #To be implemented in subclasses

    def __str__(self):
        if hasattr(self, "name"):
            return self.name
        return self.__class__.__name__

    def set_name(self, name):
        self.name = name
        return self

    ### Only these methods should touch the camera

    def set_camera(self, camera):
        self.camera = camera

    def get_frame(self):
        return self.camera.get_image()

    def set_camera_image(self, pixel_array):
        self.camera.set_image(pixel_array)

    def set_camera_background(self, background):
        self.camera.set_background(background)

    def reset_camera(self):
        self.camera.reset()

    def capture_mobjects_in_camera(self, mobjects, **kwargs):
        self.camera.capture_mobjects(mobjects, **kwargs)

    def update_frame(self, mobjects = None, background = None, **kwargs):
        if "include_submobjects" not in kwargs:
            kwargs["include_submobjects"] = False
        if mobjects is None:
            mobjects = self.mobjects
        if background is not None:
            self.set_camera_image(background)
        else:
            self.reset_camera()
        self.capture_mobjects_in_camera(mobjects, **kwargs)

    def freeze_background(self):
        self.update_frame()
        self.set_camera(Camera(self.get_frame()))
        self.clear()
    ###

    def extract_mobject_family_members(self, *mobjects):
        return remove_list_redundancies(list(
            it.chain(*[
                m.submobject_family()
                for m in mobjects
                if not (isinstance(m, VMobject) and m.is_subpath)
            ])
        ))

    def get_top_level_mobjects(self):
        # Return only those which are not in the family
        # of another mobject from the scene
        mobjects = self.get_mobjects()
        families = [m.submobject_family() for m in mobjects]
        def is_top_level(mobject):
            num_families = sum([
                (mobject in family) 
                for family in families
            ])
            return num_families == 1
        return filter(is_top_level, mobjects)
        
    def add(self, *mobjects_to_add):
        """
        Mobjects will be displayed, from background to foreground,
        in the order with which they are entered.

        Scene class keeps track not just of the mobject directly added,
        but also of every family member therein.
        """
        if not all_elements_are_instances(mobjects_to_add, Mobject):
            raise Exception("Adding something which is not a mobject")
        mobjects_to_add = self.extract_mobject_family_members(*mobjects_to_add)
        self.mobjects = list_update(self.mobjects, mobjects_to_add)
        return self

    def add_mobjects_among(self, values):
        """
        So a scene can just add all mobjects it's defined up to that point
        by calling add_mobjects_among(locals().values())
        """
        mobjects = filter(lambda x : isinstance(x, Mobject), values)
        self.add(*mobjects)
        return self

    def remove(self, *mobjects_to_remove):
        if not all_elements_are_instances(mobjects_to_remove, Mobject):
            raise Exception("Removing something which is not a mobject")
        mobjects_to_remove = self.extract_mobject_family_members(*mobjects_to_remove)
        self.mobjects = filter(
            lambda m : m not in mobjects_to_remove,
            self.mobjects
        )
        self.remove_mobjects_not_completely_on_screen()
        return self

    def remove_mobjects_not_completely_on_screen(self):
        def should_keep(mobject):
            return all([
                submob in self.mobjects
                for submob in mobject.family_members_with_points()
            ])

        self.mobjects = filter(should_keep, self.mobjects)
        return self

    def add_foreground_mobjects(self, *mobjects):
        self.foreground_mobjects = list_update(
            self.foreground_mobjects, 
            mobjects
        )
        self.add(*mobjects)
        return self

    def add_foreground_mobject(self, mobject):
        return self.add_foreground_mobjects(mobject)

    def remove_foreground_mobjects(self, *mobjects):
        self.foreground_mobjects = filter(
            lambda m : m not in mobjects,
            self.foreground_mobjects
        )
        return self

    def remove_foreground_mobject(self, mobject):
        return self.remove_foreground_mobjects(mobject)

    def bring_to_front(self, *mobjects):
        self.add(*mobjects)
        return self

    def bring_to_back(self, *mobjects):
        self.remove(*mobjects)
        self.mobjects = mobjects + self.mobjects
        return self

    def clear(self):
        self.mobjects = []
        return self

    def get_mobjects(self):
        return list(self.mobjects)

    def get_mobject_copies(self):
        return [m.copy() for m in self.mobjects]

    def separate_moving_and_static_mobjects(self, *animations):
        """
        """
        moving_mobjects = self.extract_mobject_family_members(
            *[anim.mobject for anim in animations] + \
            self.foreground_mobjects
        )
        static_mobjects = filter(
            lambda m : m not in moving_mobjects,
            self.mobjects
        )
        return moving_mobjects, static_mobjects

    def get_time_progression(self, animations):
        run_time = animations[0].run_time
        times = np.arange(0, run_time, self.frame_duration)
        time_progression = ProgressDisplay(times)
        time_progression.set_description("".join([
            "Animation %d: "%self.num_plays,
            str(animations[0]),
            (", etc." if len(animations) > 1 else ""),
        ]))
        return time_progression

    def compile_play_args_to_animation_list(self, *args):
        """
        Eacn arg can either be an animation, or a mobject method
        followed by that methods arguments.  

        This animation list is built by going through the args list, 
        and each animation is simply added, but when a mobject method 
        s hit, a MoveToTarget animation is built using the args that 
        follow up until either another animation is hit, another method 
        is hit, or the args list runs out.
        """
        animations = []
        state = {
            "curr_method" : None,
            "last_method" : None,
            "method_args" : [],
        }
        def compile_method(state):
            if state["curr_method"] is None:
                return
            mobject = state["curr_method"].im_self
            if state["last_method"] and state["last_method"].im_self is mobject:
                animations.pop()
                #method should already have target then.
            else:
                mobject.target = mobject.copy()
            state["curr_method"].im_func(
                mobject.target, *state["method_args"]
            )
            animations.append(MoveToTarget(mobject))
            state["last_method"] = state["curr_method"]
            state["curr_method"] = None
            state["method_args"] = []

        for arg in args:
            if isinstance(arg, Animation):
                compile_method(state)
                animations.append(arg)
            elif inspect.ismethod(arg):
                compile_method(state)
                state["curr_method"] = arg
            elif state["curr_method"] is not None:
                state["method_args"].append(arg)
            elif isinstance(arg, Mobject):
                raise Exception("""
                    I think you may have invoked a method 
                    you meant to pass in as a Scene.play argument
                """)
            else:
                raise Exception("Invalid play arguments")
        compile_method(state)
        return animations

    def play(self, *args, **kwargs):
        if len(args) == 0:
            warnings.warn("Called Scene.play with no animations")
            return
        if self.skip_animations:
            kwargs["run_time"] = 0

        animations = self.compile_play_args_to_animation_list(*args)
        self.num_plays += 1

        sync_animation_run_times_and_rate_funcs(*animations, **kwargs)
        moving_mobjects, static_mobjects = \
            self.separate_moving_and_static_mobjects(*animations)
        self.update_frame(static_mobjects)
        static_image = self.get_frame()
        for t in self.get_time_progression(animations):
            for animation in animations:
                animation.update(t / animation.run_time)
            self.update_frame(moving_mobjects, static_image)
            self.add_frames(self.get_frame())
        self.add(*moving_mobjects)
        self.mobjects_from_last_animation = moving_mobjects
        self.clean_up_animations(*animations)
        return self

    def clean_up_animations(self, *animations):
        for animation in animations:
            animation.clean_up(self)
        return self

    def get_mobjects_from_last_animation(self):
        if hasattr(self, "mobjects_from_last_animation"):
            return self.mobjects_from_last_animation
        return []

    def dither(self, duration = DEFAULT_DITHER_TIME):
        if self.skip_animations:
            return self
        self.update_frame()
        self.add_frames(*[self.get_frame()]*int(duration / self.frame_duration))
        return self

    def force_skipping(self):
        self.original_skipping_status = self.skip_animations
        self.skip_animations = True
        return self

    def revert_to_original_skipping_status(self):
        if hasattr(self, "original_skipping_status"):
            self.skip_animations = self.original_skipping_status
        return self

    def add_frames(self, *frames):
        if self.write_to_movie:
            for frame in frames:
                self.writing_process.stdin.write(frame.tostring())
        if self.save_frames:
            self.saved_frames += list(frames)

    def repeat_frames(self, num = 1):
        assert(self.save_frames)
        self.add_frames(*self.saved_frames*num)
        return self

    def invert_colors(self):
        white_frame = 255*np.ones(self.get_frame().shape, dtype = 'uint8')
        self.saved_frames = [
            white_frame-frame
            for frame in self.saved_frames
        ]
        return self

    def show_frame(self):
        self.update_frame()
        Image.fromarray(self.get_frame()).show()

    def preview(self):
        TkSceneRoot(self)

    def save_image(self, name = None):
        path = os.path.join(self.output_directory, "images")
        file_name = (name or str(self)) + ".png"
        full_path = os.path.join(path, file_name)
        if not os.path.exists(path):
            os.makedirs(path)
        self.update_frame()
        Image.fromarray(self.get_frame()).save(full_path)

    def get_movie_file_path(self, name, extension):
        file_path = os.path.join(self.output_directory, name)
        if not file_path.endswith(extension):
            file_path += extension
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        return file_path

    def open_movie_pipe(self):
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
            '-r', str(fps), # frames per second
            '-i', '-',      # The imput comes from a pipe
            '-an',          # Tells FFMPEG not to expect any audio
            '-vcodec', 'mpeg',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-loglevel', 'error',
            file_path,
        ]
        self.writing_process = sp.Popen(command, stdin=sp.PIPE)

    def close_movie_pipe(self):
        self.writing_process.stdin.close()
        self.writing_process.wait()

























