from __future__ import annotations

import time
import random
import inspect
import platform
import itertools as it
from functools import wraps
from typing import Iterable, Callable

from tqdm import tqdm as ProgressDisplay
import numpy as np

from manimlib.animation.animation import prepare_animation
from manimlib.animation.transform import MoveToTarget
from manimlib.camera.camera import Camera
from manimlib.constants import DEFAULT_WAIT_TIME
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.scene.scene_file_writer import SceneFileWriter
from manimlib.utils.config_ops import digest_config
from manimlib.utils.family_ops import extract_mobject_family_members
from manimlib.utils.family_ops import restructure_list_to_exclude_certain_family_members
from manimlib.event_handler.event_type import EventType
from manimlib.event_handler import EVENT_DISPATCHER
from manimlib.logger import log

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image
    from manimlib.animation.animation import Animation


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
        "presenter_mode": False,
        "linger_after_completion": True,
        "pan_sensitivity": 3,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.preview:
            from manimlib.window import Window
            self.window = Window(scene=self, **self.window_config)
            self.camera_config["ctx"] = self.window.ctx
            self.camera_config["frame_rate"] = 30  # Where's that 30 from?
        else:
            self.window = None

        self.camera: Camera = self.camera_class(**self.camera_config)
        self.file_writer = SceneFileWriter(self, **self.file_writer_config)
        self.mobjects: list[Mobject] = [self.camera.frame]
        self.num_plays: int = 0
        self.time: float = 0
        self.skip_time: float = 0
        self.original_skipping_status: bool = self.skip_animations
        if self.start_at_animation_number is not None:
            self.skip_animations = True

        # Items associated with interaction
        self.mouse_point = Point()
        self.mouse_drag_point = Point()
        self.hold_on_wait = self.presenter_mode

        # Much nicer to work with deterministic scenes
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

    def run(self) -> None:
        self.virtual_animation_start_time: float = 0
        self.real_animation_start_time: float = time.time()
        self.file_writer.begin()

        self.setup()
        try:
            self.construct()
        except EndSceneEarlyException:
            pass
        self.tear_down()

    def setup(self) -> None:
        """
        This is meant to be implement by any scenes which
        are comonly subclassed, and have some common setup
        involved before the construct method is called.
        """
        pass

    def construct(self) -> None:
        # Where all the animation happens
        # To be implemented in subclasses
        pass

    def tear_down(self) -> None:
        self.stop_skipping()
        self.file_writer.finish()
        if self.window and self.linger_after_completion:
            self.interact()

    def interact(self) -> None:
        # If there is a window, enter a loop
        # which updates the frame while under
        # the hood calling the pyglet event loop
        log.info(
            "Tips: You are now in the interactive mode. Now you can use the keyboard"
            " and the mouse to interact with the scene. Just press `q` if you want to quit."
        )
        self.quit_interaction = False
        self.refresh_static_mobjects()
        while not (self.window.is_closing or self.quit_interaction):
            self.update_frame(1 / self.camera.frame_rate)
        if self.window.is_closing:
            self.window.destroy()

    def embed(self, close_scene_on_exit: bool = True) -> None:
        if not self.preview:
            # If the scene is just being
            # written, ignore embed calls
            return
        self.stop_skipping()
        self.linger_after_completion = False
        self.update_frame()

        # Save scene state at the point of embedding
        self.save_state()

        from IPython.terminal.embed import InteractiveShellEmbed
        shell = InteractiveShellEmbed()
        # Have the frame update after each command
        shell.events.register('post_run_cell', lambda *a, **kw: self.refresh_static_mobjects())
        shell.events.register('post_run_cell', lambda *a, **kw: self.update_frame())
        # Use the locals of the caller as the local namespace
        # once embedded, and add a few custom shortcuts
        local_ns = inspect.currentframe().f_back.f_locals
        local_ns["touch"] = self.interact
        for term in ("play", "wait", "add", "remove", "clear", "save_state", "restore"):
            local_ns[term] = getattr(self, term)
        log.info("Tips: Now the embed iPython terminal is open. But you can't interact with"
                 " the window directly. To do so, you need to type `touch()` or `self.interact()`")
        shell(local_ns=local_ns, stack_depth=2)
        # End scene when exiting an embed
        if close_scene_on_exit:
            raise EndSceneEarlyException()

    def __str__(self) -> str:
        return self.__class__.__name__

    # Only these methods should touch the camera
    def get_image(self) -> Image:
        return self.camera.get_image()

    def show(self) -> None:
        self.update_frame(ignore_skipping=True)
        self.get_image().show()

    def update_frame(self, dt: float = 0, ignore_skipping: bool = False) -> None:
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

    def emit_frame(self) -> None:
        if not self.skip_animations:
            self.file_writer.write_frame(self.camera)

    # Related to updating
    def update_mobjects(self, dt: float) -> None:
        for mobject in self.mobjects:
            mobject.update(dt)

    def should_update_mobjects(self) -> bool:
        return self.always_update_mobjects or any([
            len(mob.get_family_updaters()) > 0
            for mob in self.mobjects
        ])

    def has_time_based_updaters(self) -> bool:
        return any([
            sm.has_time_based_updater()
            for mob in self.mobjects()
            for sm in mob.get_family()
        ])

    # Related to time
    def get_time(self) -> float:
        return self.time

    def increment_time(self, dt: float) -> None:
        self.time += dt

    # Related to internal mobject organization
    def get_top_level_mobjects(self) -> list[Mobject]:
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

    def get_mobject_family_members(self) -> list[Mobject]:
        return extract_mobject_family_members(self.mobjects)

    def add(self, *new_mobjects: Mobject):
        """
        Mobjects will be displayed, from background to
        foreground in the order with which they are added.
        """
        self.remove(*new_mobjects)
        self.mobjects += new_mobjects
        return self

    def add_mobjects_among(self, values: Iterable):
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

    def remove(self, *mobjects_to_remove: Mobject):
        self.mobjects = restructure_list_to_exclude_certain_family_members(
            self.mobjects, mobjects_to_remove
        )
        return self

    def bring_to_front(self, *mobjects: Mobject):
        self.add(*mobjects)
        return self

    def bring_to_back(self, *mobjects: Mobject):
        self.remove(*mobjects)
        self.mobjects = list(mobjects) + self.mobjects
        return self

    def clear(self):
        self.mobjects = []
        return self

    def get_mobjects(self) -> list[Mobject]:
        return list(self.mobjects)

    def get_mobject_copies(self) -> list[Mobject]:
        return [m.copy() for m in self.mobjects]

    def point_to_mobject(
        self,
        point: np.ndarray,
        search_set: Iterable[Mobject] | None = None,
        buff: float = 0
    ) -> Mobject | None:
        """
        E.g. if clicking on the scene, this returns the top layer mobject
        under a given point
        """
        if search_set is None:
            search_set = self.mobjects
        for mobject in reversed(search_set):
            if mobject.is_point_touching(point, buff=buff):
                return mobject
        return None

    def get_group(self, *mobjects):
        if all(isinstance(m, VMobject) for m in mobjects):
            return VGroup(*mobjects)
        else:
            return Group(*mobjects)

    def id_to_mobject(self, id_value):
        for mob in self.mobjects:
            for sm in mob.get_family():
                if id(sm) == id_value:
                    return sm
        return None

    def ids_to_group(self, *id_values):
        return self.get_group(*filter(
            lambda x: x is not None,
            map(self.id_to_mobject, id_values)
        ))

    # Related to skipping
    def update_skipping_status(self) -> None:
        if self.start_at_animation_number is not None:
            if self.num_plays == self.start_at_animation_number:
                self.skip_time = self.time
                if not self.original_skipping_status:
                    self.stop_skipping()
        if self.end_at_animation_number is not None:
            if self.num_plays >= self.end_at_animation_number:
                raise EndSceneEarlyException()

    def stop_skipping(self) -> None:
        self.virtual_animation_start_time = self.time
        self.skip_animations = False

    # Methods associated with running animations
    def get_time_progression(
        self,
        run_time: float,
        n_iterations: int | None = None,
        desc: str = "",
        override_skip_animations: bool = False
    ) -> list[float] | np.ndarray | ProgressDisplay:
        if self.skip_animations and not override_skip_animations:
            return [run_time]
        else:
            step = 1 / self.camera.frame_rate
            times = np.arange(0, run_time, step)

        if self.file_writer.has_progress_display:
            self.file_writer.set_progress_display_subdescription(desc)
            return times

        return ProgressDisplay(
            times,
            total=n_iterations,
            leave=self.leave_progress_bars,
            ascii=True if platform.system() == 'Windows' else None,
            desc=desc,
        )

    def get_run_time(self, animations: Iterable[Animation]) -> float:
        return np.max([animation.run_time for animation in animations])

    def get_animation_time_progression(
        self,
        animations: Iterable[Animation]
    ) -> list[float] | np.ndarray | ProgressDisplay:
        run_time = self.get_run_time(animations)
        description = f"{self.num_plays} {animations[0]}"
        if len(animations) > 1:
            description += ", etc."
        time_progression = self.get_time_progression(run_time, desc=description)
        return time_progression

    def get_wait_time_progression(
        self,
        duration: float,
        stop_condition: Callable[[], bool] | None = None
    ) -> list[float] | np.ndarray | ProgressDisplay:
        kw = {"desc": f"{self.num_plays} Waiting"}
        if stop_condition is not None:
            kw["n_iterations"] = -1  # So it doesn't show % progress
            kw["override_skip_animations"] = True
        return self.get_time_progression(duration, **kw)

    def anims_from_play_args(self, *args, **kwargs) -> list[Animation]:
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
            if inspect.ismethod(arg):
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
                try:
                    anim = prepare_animation(arg)
                except TypeError:
                    raise TypeError(f"Unexpected argument {arg} passed to Scene.play()")

                compile_method(state)
                animations.append(anim)
        compile_method(state)

        for animation in animations:
            # This is where kwargs to play like run_time and rate_func
            # get applied to all animations
            animation.update_config(**kwargs)

        return animations

    def handle_play_like_call(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.update_skipping_status()
            should_write = not self.skip_animations
            if should_write:
                self.file_writer.begin_animation()

            if self.window:
                self.real_animation_start_time = time.time()
                self.virtual_animation_start_time = self.time

            self.refresh_static_mobjects()
            func(self, *args, **kwargs)

            if should_write:
                self.file_writer.end_animation()

            self.num_plays += 1
        return wrapper

    def refresh_static_mobjects(self) -> None:
        self.camera.refresh_static_mobjects()

    def begin_animations(self, animations: Iterable[Animation]) -> None:
        for animation in animations:
            animation.begin()
            # Anything animated that's not already in the
            # scene gets added to the scene.  Note, for
            # animated mobjects that are in the family of
            # those on screen, this can result in a restructuring
            # of the scene.mobjects list, which is usually desired.
            if animation.mobject not in self.mobjects:
                self.add(animation.mobject)

    def progress_through_animations(self, animations: Iterable[Animation]) -> None:
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

    def finish_animations(self, animations: Iterable[Animation]) -> None:
        for animation in animations:
            animation.finish()
            animation.clean_up_from_scene(self)
        if self.skip_animations:
            self.update_mobjects(self.get_run_time(animations))
        else:
            self.update_mobjects(0)

    @handle_play_like_call
    def play(self, *args, **kwargs) -> None:
        if len(args) == 0:
            log.warning("Called Scene.play with no animations")
            return
        animations = self.anims_from_play_args(*args, **kwargs)
        self.begin_animations(animations)
        self.progress_through_animations(animations)
        self.finish_animations(animations)

    @handle_play_like_call
    def wait(
        self,
        duration: float = DEFAULT_WAIT_TIME,
        stop_condition: Callable[[], bool] = None,
        note: str = None,
        ignore_presenter_mode: bool = False
    ):
        if note:
            log.info(note)
        self.update_mobjects(dt=0)  # Any problems with this?
        if self.presenter_mode and not self.skip_animations and not ignore_presenter_mode:
            while self.hold_on_wait:
                self.update_frame(dt=1 / self.camera.frame_rate)
            self.hold_on_wait = True
        else:
            time_progression = self.get_wait_time_progression(duration, stop_condition)
            last_t = 0
            for t in time_progression:
                dt = t - last_t
                last_t = t
                self.update_frame(dt)
                self.emit_frame()
                if stop_condition is not None and stop_condition():
                    break
        self.refresh_static_mobjects()
        return self

    def wait_until(
        self,
        stop_condition: Callable[[], bool],
        max_time: float = 60
    ):
        self.wait(max_time, stop_condition=stop_condition)

    def force_skipping(self):
        self.original_skipping_status = self.skip_animations
        self.skip_animations = True
        return self

    def revert_to_original_skipping_status(self):
        if hasattr(self, "original_skipping_status"):
            self.skip_animations = self.original_skipping_status
        return self

    def add_sound(
        self,
        sound_file: str,
        time_offset: float = 0,
        gain: float | None = None,
        gain_to_background: float | None = None
    ):
        if self.skip_animations:
            return
        time = self.get_time() + time_offset
        self.file_writer.add_sound(sound_file, time, gain, gain_to_background)

    # Helpers for interactive development
    def save_state(self) -> None:
        self.saved_state = [
            (mob, mob.copy())
            for mob in self.mobjects
        ]

    def restore(self) -> None:
        if not hasattr(self, "saved_state"):
            raise Exception("Trying to restore scene without having saved")
        self.mobjects = []
        for mob, mob_state in self.saved_state:
            mob.become(mob_state)
            self.mobjects.append(mob)

    # Event handling

    def on_mouse_motion(
        self,
        point: np.ndarray,
        d_point: np.ndarray
    ) -> None:
        self.mouse_point.move_to(point)

        event_data = {"point": point, "d_point": d_point}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseMotionEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

        frame = self.camera.frame
        # Handle perspective changes
        if self.window.is_key_pressed(ord("d")):
            frame.increment_theta(-self.pan_sensitivity * d_point[0])
            frame.increment_phi(self.pan_sensitivity * d_point[1])
        # Handle frame movements
        elif self.window.is_key_pressed(ord("s")):
            shift = -d_point
            shift[0] *= frame.get_width() / 2
            shift[1] *= frame.get_height() / 2
            transform = frame.get_inverse_camera_rotation_matrix()
            shift = np.dot(np.transpose(transform), shift)
            frame.shift(shift)

    def on_mouse_drag(
        self,
        point: np.ndarray,
        d_point: np.ndarray,
        buttons: int,
        modifiers: int
    ) -> None:
        self.mouse_drag_point.move_to(point)

        event_data = {"point": point, "d_point": d_point, "buttons": buttons, "modifiers": modifiers}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseDragEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_press(
        self,
        point: np.ndarray,
        button: int,
        mods: int
    ) -> None:
        event_data = {"point": point, "button": button, "mods": mods}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MousePressEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_release(
        self,
        point: np.ndarray,
        button: int,
        mods: int
    ) -> None:
        event_data = {"point": point, "button": button, "mods": mods}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseReleaseEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_scroll(
        self,
        point: np.ndarray,
        offset: np.ndarray
    ) -> None:
        event_data = {"point": point, "offset": offset}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseScrollEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

        frame = self.camera.frame
        if self.window.is_key_pressed(ord("z")):
            factor = 1 + np.arctan(10 * offset[1])
            frame.scale(1/factor, about_point=point)
        else:
            transform = frame.get_inverse_camera_rotation_matrix()
            shift = np.dot(np.transpose(transform), offset)
            frame.shift(-20.0 * shift)

    def on_key_release(
        self,
        symbol: int,
        modifiers: int
    ) -> None:
        event_data = {"symbol": symbol, "modifiers": modifiers}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.KeyReleaseEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_key_press(
        self,
        symbol: int,
        modifiers: int
    ) -> None:
        try:
            char = chr(symbol)
        except OverflowError:
            log.warning("The value of the pressed key is too large.")
            return

        event_data = {"symbol": symbol, "modifiers": modifiers}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.KeyPressEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

        if char == "r":
            self.camera.frame.to_default_state()
        elif char == "q":
            self.quit_interaction = True
        elif char == " " or symbol == 65363:  # Space or right arrow
            self.hold_on_wait = False
        elif char == "e" and modifiers == 3:  # ctrl + shift + e
            self.embed(close_scene_on_exit=False)

    def on_resize(self, width: int, height: int) -> None:
        self.camera.reset_pixel_shape(width, height)

    def on_show(self) -> None:
        pass

    def on_hide(self) -> None:
        pass

    def on_close(self) -> None:
        pass


class EndSceneEarlyException(Exception):
    pass
