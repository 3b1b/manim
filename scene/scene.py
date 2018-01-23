from PIL import Image
from colour import Color
import numpy as np
import itertools as it
import warnings
import time
import os
import shutil
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
from animation.continual_animation import ContinualAnimation

class Scene(object):
    CONFIG = {
        "camera_class"     : Camera,
        "camera_config"    : {},
        "frame_duration"   : LOW_QUALITY_FRAME_DURATION,
        "construct_args"   : [],
        "skip_animations"  : False,
        "write_to_movie"   : False,
        "save_frames"      : False,
        "save_pngs"        : False,
        "pngs_mode"        : "RGBA",
        "output_directory" : ANIMATIONS_DIR,
        "movie_file_extension" : ".mp4",
        "name" : None,
        "always_continually_update" : False,
        "random_seed" : 0,
        "skip_to_animation_number" : None,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.camera = self.camera_class(**self.camera_config)
        self.mobjects = []
        self.continual_animations = []
        self.foreground_mobjects = []
        self.num_plays = 0
        self.saved_frames = []
        self.shared_locals = {}
        self.frame_num = 0
        if self.name is None:
            self.name = self.__class__.__name__
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

        self.setup()
        if self.write_to_movie:
            self.open_movie_pipe()
        self.construct(*self.construct_args)
        if self.write_to_movie:
            self.close_movie_pipe()
        print("Played a total of %d animations"%self.num_plays)

    def setup(self):
        """
        This is meant to be implement by any scenes which
        are comonly subclassed, and have some common setup
        involved before the construct method is called.
        """
        pass

    def setup_bases(self):
        for base in self.__class__.__bases__:
            base.setup(self)

    def construct(self):
        pass #To be implemented in subclasses

    def __str__(self):
        return self.name

    def set_name(self, name):
        self.name = name
        return self

    def set_variables_as_attrs(self, *objects, **newly_named_objects):
        """
        This method is slightly hacky, making it a little easier
        for certain methods (typically subroutines of construct)
        to share local variables.
        """
        caller_locals = inspect.currentframe().f_back.f_locals
        for key, value in caller_locals.items():
            for o in objects:
                if value is o:
                    setattr(self, key, value)
        for key, value in newly_named_objects.items():
            setattr(self, key, value)
        return self

    def get_attrs(self, *keys):
        return [getattr(self, key) for key in keys]

    ### Only these methods should touch the camera

    def set_camera(self, camera):
        self.camera = camera

    def get_frame(self):
        return np.array(self.camera.get_pixel_array())

    def get_image(self):
        return self.camera.get_image()

    def set_camera_pixel_array(self, pixel_array):
        self.camera.set_pixel_array(pixel_array)

    def set_camera_background(self, background):
        self.camera.set_background(background)

    def reset_camera(self):
        self.camera.reset()

    def capture_mobjects_in_camera(self, mobjects, **kwargs):
        self.camera.capture_mobjects(mobjects, **kwargs)

    def update_frame(
        self, 
        mobjects = None, 
        background = None, 
        include_submobjects = True,
        **kwargs):
        if mobjects is None:
            mobjects = list_update(
                self.mobjects,
                self.foreground_mobjects,
            )
        if background is not None:
            self.set_camera_pixel_array(background)
        else:
            self.reset_camera()

        kwargs["include_submobjects"] = include_submobjects
        self.capture_mobjects_in_camera(mobjects, **kwargs)

    def freeze_background(self):
        self.update_frame()
        self.set_camera(Camera(self.get_frame()))
        self.clear()
    ###

    def continual_update(self, dt = None):
        if dt is None:
            dt = self.frame_duration
        for continual_animation in self.continual_animations:
            continual_animation.update(dt)

    def wind_down(self, *continual_animations, **kwargs):
        wind_down_time = kwargs.get("wind_down_time", 1)
        for continual_animation in continual_animations:
            continual_animation.begin_wind_down(wind_down_time)
        self.wait(wind_down_time)
        #TODO, this is not done with the remove method so as to
        #keep the relevant mobjects.  Better way?
        self.continual_animations = filter(
            lambda ca : ca in continual_animations,
            self.continual_animations
        )

    def should_continually_update(self):
        return len(self.continual_animations) > 0 or self.always_continually_update

    ###

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

    def separate_mobjects_and_continual_animations(self, mobjects_or_continual_animations):
        mobjects = []
        continual_animations = []
        for item in mobjects_or_continual_animations:
            if isinstance(item, Mobject):
                mobjects.append(item)
            elif isinstance(item, ContinualAnimation):
                mobjects.append(item.mobject)
                continual_animations.append(item)
            else:
                raise Exception("""
                    Adding/Removing something which is
                    not a Mobject or a ContinualAnimation
                 """)
        return mobjects, continual_animations

    def add(self, *mobjects_or_continual_animations):
        """
        Mobjects will be displayed, from background to foreground,
        in the order with which they are entered.
        """
        mobjects, continual_animations = self.separate_mobjects_and_continual_animations(
            mobjects_or_continual_animations
        )
        self.restructure_mobjects(to_remove = mobjects)
        self.mobjects += mobjects
        self.continual_animations += continual_animations
        return self

    def add_mobjects_among(self, values):
        """
        So a scene can just add all mobjects it's defined up to that point
        by calling add_mobjects_among(locals().values())
        """
        mobjects = filter(lambda x : isinstance(x, Mobject), values)
        self.add(*mobjects)
        return self

    def remove(self, *mobjects_or_continual_animations):
        mobjects, continual_animations = self.separate_mobjects_and_continual_animations(
            mobjects_or_continual_animations
        )

        to_remove = self.camera.extract_mobject_family_members(mobjects)
        for list_name in "mobjects", "foreground_mobjects":
            self.restructure_mobjects(mobjects, list_name, False)

        self.continual_animations = filter(
            lambda ca : ca not in continual_animations and \
                        ca.mobject not in to_remove,
            self.continual_animations
        )
        return self

    def restructure_mobjects(
        self, to_remove, 
        mobject_list_name = "mobjects", 
        extract_families = True
        ):
        """
        In cases where the scene contains a group, e.g. Group(m1, m2, m3), but one
        of its submobjects is removed, e.g. scene.remove(m1), the list of mobjects
        will be editing to contain other submobjects, but not m1, e.g. it will now
        insert m2 and m3 to where the group once was.
        """
        if extract_families:
            to_remove = self.camera.extract_mobject_family_members(to_remove)
        _list = getattr(self, mobject_list_name)
        new_list = self.get_restructured_mobject_list(_list, to_remove)
        setattr(self, mobject_list_name, new_list)
        return self

    def get_restructured_mobject_list(self, mobjects, to_remove):
        new_mobjects = []
        def add_safe_mobjects_from_list(list_to_examine, set_to_remove):
            for mob in list_to_examine:
                if mob in set_to_remove:
                    continue
                intersect = set_to_remove.intersection(mob.submobject_family())
                if intersect:
                    add_safe_mobjects_from_list(mob.submobjects, intersect)
                else:
                    new_mobjects.append(mob)
        add_safe_mobjects_from_list(mobjects, set(to_remove))
        return new_mobjects

    def add_foreground_mobjects(self, *mobjects):
        self.foreground_mobjects = list_update(
            self.foreground_mobjects,
            mobjects
        )
        self.add(*mobjects)
        return self

    def add_foreground_mobject(self, mobject):
        return self.add_foreground_mobjects(mobject)

    def remove_foreground_mobjects(self, *to_remove):
        self.restructure_mobjects(to_remove, "foreground_mobjects")
        return self

    def remove_foreground_mobject(self, mobject):
        return self.remove_foreground_mobjects(mobject)

    def bring_to_front(self, *mobjects):
        self.add(*mobjects)
        return self

    def bring_to_back(self, *mobjects):
        self.remove(*mobjects)
        self.mobjects = list(mobjects) + self.mobjects
        return self

    def clear(self):
        self.mobjects = []
        self.foreground_mobjects = []
        self.continual_animation = []
        return self

    def get_mobjects(self):
        return list(self.mobjects)

    def get_mobject_copies(self):
        return [m.copy() for m in self.mobjects]

    def get_moving_mobjects(self, *animations):
        moving_mobjects = list(it.chain(
            [
                anim.mobject for anim in animations
                if anim.mobject not in self.foreground_mobjects
            ],
            [ca.mobject for ca in self.continual_animations],
            self.foreground_mobjects,
        ))
        return moving_mobjects

    def get_time_progression(self, run_time):
        times = np.arange(0, run_time, self.frame_duration)
        time_progression = ProgressDisplay(times)
        return time_progression

    def get_animation_time_progression(self, animations):
        run_time = animations[0].run_time
        time_progression = self.get_time_progression(run_time)
        time_progression.set_description("".join([
            "Animation %d: "%self.num_plays,
            str(animations[0]),
            (", etc." if len(animations) > 1 else ""),
        ]))
        return time_progression

    def compile_play_args_to_animation_list(self, *args):
        """
        Each arg can either be an animation, or a mobject method
        followed by that methods arguments (and potentially follow
        by a dict of kwargs for that method).

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
            #
            if len(state["method_args"]) > 0 and isinstance(state["method_args"][-1], dict):
                method_kwargs = state["method_args"].pop()
            else:
                method_kwargs = {}
            state["curr_method"].im_func(
                mobject.target, 
                *state["method_args"],
                **method_kwargs
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
        if self.skip_to_animation_number:
            if self.num_plays + 1 == self.skip_to_animation_number:
                self.skip_animations = False
        if self.skip_animations:
            kwargs["run_time"] = 0

        animations = self.compile_play_args_to_animation_list(*args)
        self.num_plays += 1

        sync_animation_run_times_and_rate_funcs(*animations, **kwargs)
        moving_mobjects = self.get_moving_mobjects(*animations)
        self.update_frame(excluded_mobjects = moving_mobjects)
        static_image = self.get_frame()
        for t in self.get_animation_time_progression(animations):
            for animation in animations:
                animation.update(t / animation.run_time)
            self.continual_update()
            self.update_frame(moving_mobjects, static_image)
            self.add_frames(self.get_frame())
        self.add(*moving_mobjects)
        self.mobjects_from_last_animation = moving_mobjects
        self.clean_up_animations(*animations)
        self.continual_update(0)
        return self

    def clean_up_animations(self, *animations):
        for animation in animations:
            animation.clean_up(self)
        self.add(*self.foreground_mobjects)
        return self

    def get_mobjects_from_last_animation(self):
        if hasattr(self, "mobjects_from_last_animation"):
            return self.mobjects_from_last_animation
        return []

    def wait(self, duration = DEFAULT_WAIT_TIME):
        if self.skip_animations:
            return self

        if self.should_continually_update():
            for t in self.get_time_progression(duration):
                self.continual_update()
                self.update_frame()
                self.add_frames(self.get_frame())
        else:
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
                if self.save_pngs:
                    self.save_image("frame" + str(self.frame_num), self.pngs_mode, True)
                    self.frame_num = self.frame_num + 1
                self.writing_process.stdin.write(frame.tostring())
        if self.save_frames:
            self.saved_frames += list(frames)

    #Display methods

    def show_frame(self):
        self.update_frame()
        self.get_image().show()

    def preview(self):
        TkSceneRoot(self)
    
    def get_image_file_path(self, name = None, dont_update = False):
        folder = "images"
        if dont_update:
            folder = str(self)
        path = os.path.join(self.output_directory, folder)
        file_name = (name or str(self)) + ".png"
        return os.path.join(path, file_name)

    def save_image(self, name = None, mode = "RGB", dont_update = False):
        path = self.get_image_file_path(name, dont_update)
        directory_path = os.path.dirname(path)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        if not dont_update:
            self.update_frame()
        image = self.get_image()
        image = image.convert(mode)
        image.save(path)

    def get_movie_file_path(self, name = None, extension = None):
        if extension is None:
            extension = self.movie_file_extension
        if name is None:
            name = self.name
        file_path = os.path.join(self.output_directory, name)
        if not file_path.endswith(extension):
            file_path += extension
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        return file_path

    def open_movie_pipe(self):
        name = str(self)
        file_path = self.get_movie_file_path(name)
        temp_file_path = file_path.replace(name, name + "Temp")
        print("Writing to %s"%temp_file_path)
        self.args_to_rename_file = (temp_file_path, file_path)

        fps = int(1/self.frame_duration)
        height, width = self.camera.pixel_shape
        
        command = [
            FFMPEG_BIN,
            '-y', # overwrite output file if it exists
            '-f', 'rawvideo',
            '-vcodec','rawvideo',
            '-s', '%dx%d'%(width, height), # size of one frame
            '-pix_fmt', 'rgba',
            '-r', str(fps), # frames per second
            '-i', '-', # The imput comes from a pipe
            '-an', # Tells FFMPEG not to expect any audio
            '-vcodec', 'mpeg',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-loglevel', 'error',
            temp_file_path,
        ]
        # self.writing_process = sp.Popen(command, stdin=sp.PIPE, shell=True)
        self.writing_process = sp.Popen(command, stdin=sp.PIPE)

    def close_movie_pipe(self):
        self.writing_process.stdin.close()
        self.writing_process.wait()
        if os.name == 'nt':
            shutil.move(*self.args_to_rename_file)
        else:
            os.rename(*self.args_to_rename_file)




