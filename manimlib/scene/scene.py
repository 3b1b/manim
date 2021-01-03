import inspect
import random
import warnings
import platform
import itertools as it

from tqdm import tqdm as ProgressDisplay
import numpy as np
import time
from IPython.terminal.embed import InteractiveShellEmbed

from manimlib.animation.animation import Animation
from manimlib.animation.transform import MoveToTarget
from manimlib.mobject.mobject import Point
from manimlib.camera.camera import Camera
from manimlib.config import get_custom_defaults
from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.scene.scene_file_writer import SceneFileWriter
from manimlib.utils.config_ops import digest_config
from manimlib.utils.family_ops import extract_mobject_family_members
from manimlib.utils.family_ops import restructure_list_to_exclude_certain_family_members
from manimlib.window import Window


class Scene(object):
    CONFIG = {
        "window_config": {},
        "camera_class": Camera,
        "camera_config": {},
        "file_writer_config": {},
        "skip_animations": False,
        "always_update_mobjects": False,
        "random_seed": 0,
        "start_at_animation_number": None,
        "end_at_animation_number": None,
        "leave_progress_bars": False,
        "preview": True,
        "linger_after_completion": True,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.preview:
            self.window = Window(self, **self.window_config)
            self.camera_config["ctx"] = self.window.ctx
            self.virtual_animation_start_time = 0
            self.real_animation_start_time = time.time()
        else:
            self.window = None

        self.camera = self.camera_class(**self.camera_config)
        self.file_writer = SceneFileWriter(self, **self.file_writer_config)
        self.mobjects = []
        self.num_plays = 0
        self.time = 0
        self.skip_time = 0
        self.original_skipping_status = self.skip_animations
        self.time_of_last_frame = time.time()

        # Items associated with interaction
        self.mouse_point = Point()
        self.mouse_drag_point = Point()
        self.zoom_on_scroll = False
        self.quit_interaction = False

        # Much nice to work with deterministic scenes
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

    def run(self):
        self.setup()
        try:
            self.construct()
        except EndSceneEarlyException:
            pass
        self.tear_down()

    def setup(self):
        """
        This is meant to be implement by any scenes which
        are comonly subclassed, and have some common setup
        involved before the construct method is called.
        """
        pass

    def construct(self):
        # Where all the animation happens
        # To be implemented in subclasses
        pass

    def tear_down(self):
        self.stop_skipping()
        self.file_writer.finish()
        if self.window and self.linger_after_completion:
            self.interact()

    def interact(self):
        # If there is a window, enter a loop
        # which updates the frame while under
        # the hood calling the pyglet event loop
        self.quit_interaction = False
        self.lock_static_mobject_data()
        while not self.window.is_closing and not self.quit_interaction:
            self.update_frame()
        if self.window.is_closing:
            self.window.destroy()
        if self.quit_interaction:
            self.unlock_mobject_data()

    def embed(self):
        if not self.preview:
            # If the scene is just being
            # written, ignore embed calls
            return
        self.stop_skipping()
        self.linger_after_completion = False
        self.update_frame()

        shell = InteractiveShellEmbed()
        # Have the frame update after each command
        shell.events.register('post_run_cell', lambda *a, **kw: self.update_frame())
        # Stack depth of 2 means the shell will use
        # the namespace of the caller, not this method
        shell(stack_depth=2)
        # End scene when exiting an embed.
        raise EndSceneEarlyException()

    def __str__(self):
        return self.__class__.__name__

    # Only these methods should touch the camera
    def get_image(self):
        return self.camera.get_image()

    def update_frame(self, dt=0, ignore_skipping=False):
        self.increment_time(dt)
        self.update_mobjects(dt)
        if self.skip_animations and not ignore_skipping:
            return

        if self.window:
            self.window.clear()
        self.camera.clear()
        self.camera.capture(*self.mobjects)

        if self.window:
            self.window.swap_buffers()
            vt = self.time - self.virtual_animation_start_time
            rt = time.time() - self.real_animation_start_time
            if rt < vt:
                self.update_frame(0)

    def emit_frame(self):
        if not self.skip_animations:
            self.file_writer.write_frame(self.camera)

    ###

    def update_mobjects(self, dt):
        for mobject in self.mobjects:
            mobject.update(dt)

    def should_update_mobjects(self):
        return self.always_update_mobjects or any([
            len(mob.get_family_updaters()) > 0
            for mob in self.mobjects
        ])

    ###

    def get_time(self):
        return self.time

    def increment_time(self, dt):
        self.time += dt

    ###
    def get_top_level_mobjects(self):
        # Return only those which are not in the family
        # of another mobject from the scene
        mobjects = self.get_mobjects()
        families = [m.get_family() for m in mobjects]

        def is_top_level(mobject):
            num_families = sum([
                (mobject in family)
                for family in families
            ])
            return num_families == 1
        return list(filter(is_top_level, mobjects))

    def get_mobject_family_members(self):
        return extract_mobject_family_members(self.mobjects)

    def add(self, *new_mobjects):
        """
        Mobjects will be displayed, from background to
        foreground in the order with which they are added.
        """
        self.remove(*new_mobjects)
        self.mobjects += new_mobjects
        return self

    def add_mobjects_among(self, values):
        """
        This is meant mostly for quick prototyping,
        e.g. to add all mobjects defined up to a point,
        call self.add_mobjects_among(locals().values())
        """
        self.add(*filter(
            lambda m: isinstance(m, Mobject),
            values
        ))
        return self

    def remove(self, *mobjects_to_remove):
        self.mobjects = restructure_list_to_exclude_certain_family_members(
            self.mobjects, mobjects_to_remove
        )
        return self

    def bring_to_front(self, *mobjects):
        self.add(*mobjects)
        return self

    def bring_to_back(self, *mobjects):
        self.remove(*mobjects)
        self.mobjects = list(mobjects) + self.mobjects
        return self

    def clear(self):
        self.mobjects = []
        return self

    def get_mobjects(self):
        return list(self.mobjects)

    def get_mobject_copies(self):
        return [m.copy() for m in self.mobjects]

    def get_time_progression(self, run_time, n_iterations=None, override_skip_animations=False):
        if self.skip_animations and not override_skip_animations:
            times = [run_time]
        else:
            step = 1 / self.camera.frame_rate
            times = np.arange(0, run_time, step)
        time_progression = ProgressDisplay(
            times,
            total=n_iterations,
            leave=self.leave_progress_bars,
            ascii=False if platform.system() != 'Windows' else True
        )
        return time_progression

    def get_run_time(self, animations):
        return np.max([animation.run_time for animation in animations])

    def get_animation_time_progression(self, animations):
        run_time = self.get_run_time(animations)
        time_progression = self.get_time_progression(run_time)
        time_progression.set_description("".join([
            f"Animation {self.num_plays}: {animations[0]}",
            ", etc." if len(animations) > 1 else "",
        ]))
        return time_progression

    def anims_from_play_args(self, *args, **kwargs):
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
            "curr_method": None,
            "last_method": None,
            "method_args": [],
        }

        def compile_method(state):
            if state["curr_method"] is None:
                return
            mobject = state["curr_method"].__self__
            if state["last_method"] and state["last_method"].__self__ is mobject:
                animations.pop()
                # method should already have target then.
            else:
                mobject.generate_target()
            #
            if len(state["method_args"]) > 0 and isinstance(state["method_args"][-1], dict):
                method_kwargs = state["method_args"].pop()
            else:
                method_kwargs = {}
            state["curr_method"].__func__(
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

        for animation in animations:
            # This is where kwargs to play like run_time and rate_func
            # get applied to all animations
            animation.update_config(**kwargs)

        return animations

    def update_skipping_status(self):
        if self.start_at_animation_number is not None:
            if self.num_plays == self.start_at_animation_number:
                self.stop_skipping()
        if self.end_at_animation_number is not None:
            if self.num_plays >= self.end_at_animation_number:
                raise EndSceneEarlyException()

    def stop_skipping(self):
        if self.skip_animations:
            self.skip_animations = False
            self.skip_time += self.time

    # Methods associated with running animations
    def handle_play_like_call(func):
        def wrapper(self, *args, **kwargs):
            self.update_skipping_status()
            should_write = not self.skip_animations
            if should_write:
                self.file_writer.begin_animation()

            if self.window:
                self.real_animation_start_time = time.time()
                self.virtual_animation_start_time = self.time

            func(self, *args, **kwargs)

            if should_write:
                self.file_writer.end_animation()

            self.num_plays += 1
        return wrapper

    def lock_static_mobject_data(self, *animations):
        movers = list(it.chain(*[
            anim.mobject.get_family()
            for anim in animations
        ]))
        for mobject in self.mobjects:
            if mobject in movers:
                continue
            if mobject.get_family_updaters():
                continue
            self.camera.set_mobjects_as_static(mobject)

    def unlock_mobject_data(self):
        self.camera.release_static_mobjects()

    def begin_animations(self, animations):
        for animation in animations:
            animation.begin()
            # Anything animated that's not already in the
            # scene gets added to the scene.  Note, for
            # animated mobjects that are in the family of
            # those on screen, this can result in a restructuring
            # of the scene.mobjects list, which is usually desired.
            mob = animation.mobject
            if mob not in self.mobjects:
                self.add(mob)

    def progress_through_animations(self, animations):
        last_t = 0
        for t in self.get_animation_time_progression(animations):
            dt = t - last_t
            last_t = t
            for animation in animations:
                animation.update_mobjects(dt)
                alpha = t / animation.run_time
                animation.interpolate(alpha)
            self.update_frame(dt)
            self.emit_frame()

    def finish_animations(self, animations):
        for animation in animations:
            animation.finish()
            animation.clean_up_from_scene(self)
        self.mobjects_from_last_animation = [
            anim.mobject for anim in animations
        ]
        if self.skip_animations:
            self.update_mobjects(self.get_run_time(animations))
        else:
            self.update_mobjects(0)

    @handle_play_like_call
    def play(self, *args, **kwargs):
        if len(args) == 0:
            warnings.warn("Called Scene.play with no animations")
            return
        animations = self.anims_from_play_args(*args, **kwargs)
        self.lock_static_mobject_data(*animations)
        self.begin_animations(animations)
        self.progress_through_animations(animations)
        self.finish_animations(animations)
        self.unlock_mobject_data()

    def clean_up_animations(self, *animations):
        for animation in animations:
            animation.clean_up_from_scene(self)
        return self

    def get_mobjects_from_last_animation(self):
        if hasattr(self, "mobjects_from_last_animation"):
            return self.mobjects_from_last_animation
        return []

    def get_wait_time_progression(self, duration, stop_condition):
        if stop_condition is not None:
            time_progression = self.get_time_progression(
                duration,
                n_iterations=-1,  # So it doesn't show % progress
                override_skip_animations=True
            )
            time_progression.set_description(
                "Waiting for {}".format(stop_condition.__name__)
            )
        else:
            time_progression = self.get_time_progression(duration)
            time_progression.set_description(
                "Waiting {}".format(self.num_plays)
            )
        return time_progression

    @handle_play_like_call
    def wait(self, duration=DEFAULT_WAIT_TIME, stop_condition=None):
        self.update_mobjects(dt=0)  # Any problems with this?
        if self.should_update_mobjects():
            self.lock_static_mobject_data()
            time_progression = self.get_wait_time_progression(duration, stop_condition)
            last_t = 0
            for t in time_progression:
                dt = t - last_t
                last_t = t
                self.update_frame(dt)
                self.emit_frame()
                if stop_condition is not None and stop_condition():
                    time_progression.close()
                    break
            self.unlock_mobject_data()
        elif self.skip_animations:
            # Do nothing
            return self
        else:
            self.update_frame(duration)
            n_frames = int(duration * self.camera.frame_rate)
            for n in range(n_frames):
                self.emit_frame()
        return self

    def wait_until(self, stop_condition, max_time=60):
        self.wait(max_time, stop_condition=stop_condition)

    def force_skipping(self):
        self.original_skipping_status = self.skip_animations
        self.skip_animations = True
        return self

    def revert_to_original_skipping_status(self):
        if hasattr(self, "original_skipping_status"):
            self.skip_animations = self.original_skipping_status
        return self

    def add_sound(self, sound_file, time_offset=0, gain=None, **kwargs):
        if self.skip_animations:
            return
        time = self.get_time() + time_offset
        self.file_writer.add_sound(sound_file, time, gain, **kwargs)

    def show(self):
        self.update_frame(ignore_skipping=True)
        self.get_image().show()

    # Helpers for interactive development
    def save_state(self):
        self.saved_state = {
            "mobjects": self.mobjects,
            "mobject_states": [
                mob.copy()
                for mob in self.mobjects
            ],
        }

    def restore(self):
        if not hasattr(self, "saved_state"):
            raise Exception("Trying to restore scene without having saved")
        mobjects = self.saved_state["mobjects"]
        states = self.saved_state["mobject_states"]
        for mob, state in zip(mobjects, states):
            mob.become(state)
        self.mobjects = mobjects

    # Event handling
    def on_mouse_motion(self, point, d_point):
        self.mouse_point.move_to(point)

    def on_mouse_drag(self, point, d_point, buttons, modifiers):
        self.mouse_drag_point.move_to(point)
        # Only if 3d rotation is enabled?
        self.camera.frame.increment_theta(-d_point[0])
        self.camera.frame.increment_phi(d_point[1])

    def on_mouse_press(self, point, button, mods):
        pass

    def on_mouse_release(self, point, button, mods):
        pass

    def on_mouse_scroll(self, point, offset):
        frame = self.camera.frame
        if self.zoom_on_scroll:
            factor = 1 + np.arctan(10 * offset[1])
            frame.scale(factor, about_point=point)
        else:
            frame.shift(-30 * offset)

    def on_key_release(self, symbol, modifiers):
        if chr(symbol) == "z":
            self.zoom_on_scroll = False

    def on_key_press(self, symbol, modifiers):
        if chr(symbol) == "r":
            self.camera.frame.to_default_state()
        elif chr(symbol) == "z":
            self.zoom_on_scroll = True
        elif chr(symbol) == "q":
            self.quit_interaction = True

    def on_resize(self, width: int, height: int):
        self.camera.reset_pixel_shape(width, height)

    def on_show(self):
        pass

    def on_hide(self):
        pass

    def on_close(self):
        pass


class EndSceneEarlyException(Exception):
    pass
