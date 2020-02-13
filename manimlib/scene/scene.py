import inspect
import random
import warnings
import platform

from tqdm import tqdm as ProgressDisplay
import numpy as np
import time

from manimlib.animation.animation import Animation
from manimlib.animation.transform import MoveToTarget
from manimlib.camera.camera import Camera
from manimlib.constants import *
from manimlib.container.container import Container
from manimlib.mobject.mobject import Mobject
from manimlib.scene.scene_file_writer import SceneFileWriter
from manimlib.utils.family_ops import extract_mobject_family_members
from manimlib.utils.family_ops import restructure_list_to_exclude_certain_family_members
from manimlib.utils.iterables import list_difference_update
from manimlib.window import Window


class Scene(Container):
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
    }

    def __init__(self, **kwargs):
        Container.__init__(self, **kwargs)
        if self.preview:
            self.window = Window(self, **self.window_config)
            self.camera_config["ctx"] = self.window.ctx
        else:
            self.window = None

        self.camera = self.camera_class(**self.camera_config)
        self.file_writer = SceneFileWriter(self, **self.file_writer_config)
        self.mobjects = []
        self.displayed_mobjects = []
        self.num_plays = 0
        self.time = 0
        self.original_skipping_status = self.skip_animations
        self.time_of_last_frame = time.time()
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
        # To be implemented in subclasses
        pass

    def tear_down(self):
        self.skip_animations = False
        if self.file_writer.save_last_frame:
            self.update_frame()

        self.file_writer.finish()
        self.print_end_message()

        if self.window:
            self.interact()

    def interact(self):
        # If there is a window, enter a loop
        # which updates the frame while under
        # the hood calling the pyglet event loop
        while not self.window.is_closing:
            self.update_frame()
        self.window.destroy()

    def __str__(self):
        return self.__class__.__name__

    def print_end_message(self):
        print(f"Played {self.num_plays} animations")

    def set_variables_as_attrs(self, *objects, **newly_named_objects):
        """
        This method is slightly hacky, making it a little easier
        for certain methods (typically subroutines of construct)
        to share local variables.
        """
        caller_locals = inspect.currentframe().f_back.f_locals
        for key, value in list(caller_locals.items()):
            for o in objects:
                if value is o:
                    setattr(self, key, value)
        for key, value in list(newly_named_objects.items()):
            setattr(self, key, value)
        return self

    def get_attrs(self, *keys):
        return [getattr(self, key) for key in keys]

    # Only these methods should touch the camera
    def get_image(self):
        return self.camera.get_image()

    def update_frame(self, ignore_skipping=False):
        if self.skip_animations and not ignore_skipping:
            return

        if self.window:
            self.window.clear()
        self.camera.clear()
        self.camera.capture(*self.displayed_mobjects)
        if self.window:
            self.window.swap_buffers()

    def emit_frame(self, dt):
        self.increment_time(dt)
        if not self.skip_animations:
            self.file_writer.write_frame(self.camera)

        if self.window:
            frame_duration = 1 / self.camera.frame_rate
            t, dt = self.window.timer.next_frame()
            time.sleep(np.clip(0, frame_duration - dt, frame_duration))

    ###

    def update_mobjects(self, dt):
        for mobject in self.mobjects:
            mobject.update(dt)

    def should_update_mobjects(self):
        return self.always_update_mobjects or any([
            mob.has_time_based_updater()
            for mob in self.get_mobject_family_members()
        ])

    ###

    def get_time(self):
        return self.time

    def increment_time(self, d_time):
        self.time += d_time

    ###
    def recompute_displayed_mobjects(self):
        self.displayed_mobjects = extract_mobject_family_members(
            self.mobjects,
            only_those_with_points=True,
        )

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
        self.recompute_displayed_mobjects()
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
        self.recompute_displayed_mobjects()
        return self

    def bring_to_front(self, *mobjects):
        self.add(*mobjects)
        return self

    def bring_to_back(self, *mobjects):
        self.remove(*mobjects)
        self.mobjects = list(mobjects) + self.mobjects
        self.recompute_displayed_mobjects()
        return self

    def clear(self):
        self.mobjects = []
        self.recompute_displayed_mobjects()
        return self

    def get_mobjects(self):
        return list(self.mobjects)

    def get_mobject_copies(self):
        return [m.copy() for m in self.mobjects]

    def get_moving_mobjects(self, *animations):
        # Go through mobjects from start to end, and
        # as soon as there's one that needs updating of
        # some kind per frame, return the list from that
        # point forward.
        animation_mobjects = [anim.mobject for anim in animations]
        mobjects = self.get_mobject_family_members()
        for i, mob in enumerate(mobjects):
            is_animated = (mob in animation_mobjects)
            is_updated = (len(mob.get_family_updaters()) > 0)
            if is_animated or is_updated:
                return mobjects[i:]
        return []

    def get_time_progression(self, run_time, n_iterations=None, override_skip_animations=False):
        if self.skip_animations and not override_skip_animations:
            times = [run_time]
        else:
            step = 1 / self.camera.frame_rate
            times = np.arange(0, run_time, step)
        time_progression = ProgressDisplay(
            times, total=n_iterations,
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
            "Animation {}: ".format(self.num_plays),
            str(animations[0]),
            (", etc." if len(animations) > 1 else ""),
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
        if self.start_at_animation_number:
            if self.num_plays == self.start_at_animation_number:
                self.skip_animations = False
        if self.end_at_animation_number:
            if self.num_plays >= self.end_at_animation_number:
                self.skip_animations = True
                raise EndSceneEarlyException()

    # Methods associated with running animations
    def handle_play_like_call(func):
        def wrapper(self, *args, **kwargs):
            self.update_skipping_status()
            if not self.skip_animations:
                self.file_writer.begin_animation()
                func(self, *args, **kwargs)
                self.file_writer.end_animation()
            else:
                func(self, *args, **kwargs)
            self.num_plays += 1
        return wrapper

    def begin_animations(self, animations):
        curr_mobjects = self.get_mobject_family_members()
        for animation in animations:
            # Begin animation
            animation.begin()
            # Anything animated that's not already in the
            # scene gets added to the scene
            mob = animation.mobject
            if mob not in curr_mobjects:
                self.add(mob)
                curr_mobjects += mob.get_family()

    def progress_through_animations(self, animations):
        # Paint all non-moving objects onto the screen, so they don't
        # have to be rendered every frame
        # moving_mobjects = self.get_moving_mobjects(*animations)
        last_t = 0
        for t in self.get_animation_time_progression(animations):
            dt = t - last_t
            last_t = t
            for animation in animations:
                animation.update_mobjects(dt)
                alpha = t / animation.run_time
                animation.interpolate(alpha)
            self.update_mobjects(dt)
            self.update_frame()
            self.emit_frame(dt)

    def finish_animations(self, animations):
        for animation in animations:
            animation.finish()
            animation.clean_up_from_scene(self)
        self.mobjects_from_last_animation = [
            anim.mobject for anim in animations
        ]
        if self.skip_animations:
            # TODO, run this call in for each animation?
            self.update_mobjects(self.get_run_time(animations))
        else:
            self.update_mobjects(0)

    @handle_play_like_call
    def play(self, *args, **kwargs):
        if len(args) == 0:
            warnings.warn("Called Scene.play with no animations")
            return
        animations = self.anims_from_play_args(*args, **kwargs)
        self.begin_animations(animations)
        self.progress_through_animations(animations)
        self.finish_animations(animations)

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
            time_progression = self.get_wait_time_progression(duration, stop_condition)
            last_t = 0
            for t in time_progression:
                dt = t - last_t
                last_t = t
                self.update_mobjects(dt)
                self.update_frame()
                self.emit_frame(dt)
                if stop_condition is not None and stop_condition():
                    time_progression.close()
                    break
        elif self.skip_animations:
            # Do nothing
            return self
        else:
            self.update_frame()
            dt = 1 / self.camera.frame_rate
            n_frames = int(duration / dt)
            for n in range(n_frames):
                self.emit_frame(dt)
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

    # Event handling
    def on_mouse_motion(self, point, d_point):
        pass

    def on_mouse_drag(self, point, d_point, buttons, modifiers):
        self.camera.frame.shift(-d_point)
        self.camera.refresh_shader_uniforms()

    def on_mouse_press(self, point, button, mods):
        pass

    def on_mouse_release(self, point, button, mods):
        pass

    def on_mouse_scroll(self, point, offset):
        self.camera.frame.scale(
            1 + np.arctan(3 * offset[1]),
            about_point=point,
        )
        self.camera.refresh_shader_uniforms()

    def on_key_release(self, symbol, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        if chr(symbol) == "r":
            self.camera.frame.restore()
            self.camera.refresh_shader_uniforms()

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
