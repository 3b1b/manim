from __future__ import annotations

from collections import OrderedDict
import inspect
import os
import platform
import pyperclip
import random
import time
import re
from functools import wraps

from IPython.terminal import pt_inputhooks
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.core.getipython import get_ipython

import numpy as np
from tqdm.auto import tqdm as ProgressDisplay

from manimlib.animation.animation import prepare_animation
from manimlib.animation.fading import VFadeInThenOut
from manimlib.camera.camera import Camera
from manimlib.camera.camera_frame import CameraFrame
from manimlib.config import get_module
from manimlib.constants import ARROW_SYMBOLS
from manimlib.constants import DEFAULT_WAIT_TIME
from manimlib.constants import COMMAND_MODIFIER
from manimlib.constants import SHIFT_MODIFIER
from manimlib.constants import RED
from manimlib.event_handler import EVENT_DISPATCHER
from manimlib.event_handler.event_type import EventType
from manimlib.logger import log
from manimlib.mobject.frame import FullScreenRectangle
from manimlib.mobject.mobject import _AnimationBuilder
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.scene.scene_file_writer import SceneFileWriter
from manimlib.utils.family_ops import extract_mobject_family_members
from manimlib.utils.family_ops import recursive_mobject_remove
from manimlib.utils.iterables import batch_by_property

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Iterable, TypeVar
    from manimlib.typing import Vect3

    T = TypeVar('T')

    from PIL.Image import Image

    from manimlib.animation.animation import Animation


PAN_3D_KEY = 'd'
FRAME_SHIFT_KEY = 'f'
RESET_FRAME_KEY = 'r'
QUIT_KEY = 'q'


class Scene(object):
    random_seed: int = 0
    pan_sensitivity: float = 0.5
    scroll_sensitivity: float = 20
    drag_to_pan: bool = True
    max_num_saved_states: int = 50
    default_camera_config: dict = dict()
    default_window_config: dict = dict()
    default_file_writer_config: dict = dict()
    samples = 0
    # Euler angles, in degrees
    default_frame_orientation = (0, 0)

    def __init__(
        self,
        window_config: dict = dict(),
        camera_config: dict = dict(),
        file_writer_config: dict = dict(),
        skip_animations: bool = False,
        always_update_mobjects: bool = False,
        start_at_animation_number: int | None = None,
        end_at_animation_number: int | None = None,
        leave_progress_bars: bool = False,
        preview: bool = True,
        presenter_mode: bool = False,
        show_animation_progress: bool = False,
        embed_exception_mode: str = "",
        embed_error_sound: bool = False,
    ):
        self.skip_animations = skip_animations
        self.always_update_mobjects = always_update_mobjects
        self.start_at_animation_number = start_at_animation_number
        self.end_at_animation_number = end_at_animation_number
        self.leave_progress_bars = leave_progress_bars
        self.preview = preview
        self.presenter_mode = presenter_mode
        self.show_animation_progress = show_animation_progress
        self.embed_exception_mode = embed_exception_mode
        self.embed_error_sound = embed_error_sound

        self.camera_config = {**self.default_camera_config, **camera_config}
        self.window_config = {**self.default_window_config, **window_config}
        for config in self.camera_config, self.window_config:
            config["samples"] = self.samples
        self.file_writer_config = {**self.default_file_writer_config, **file_writer_config}

        # Initialize window, if applicable
        if self.preview:
            from manimlib.window import Window
            self.window = Window(scene=self, **self.window_config)
            self.camera_config["window"] = self.window
            self.camera_config["fps"] = 30  # Where's that 30 from?
        else:
            self.window = None

        # Core state of the scene
        self.camera: Camera = Camera(**self.camera_config)
        self.frame: CameraFrame = self.camera.frame
        self.frame.reorient(*self.default_frame_orientation)
        self.frame.make_orientation_default()

        self.file_writer = SceneFileWriter(self, **self.file_writer_config)
        self.mobjects: list[Mobject] = [self.camera.frame]
        self.render_groups: list[Mobject] = []
        self.id_to_mobject_map: dict[int, Mobject] = dict()
        self.num_plays: int = 0
        self.time: float = 0
        self.skip_time: float = 0
        self.original_skipping_status: bool = self.skip_animations
        self.checkpoint_states: dict[str, list[tuple[Mobject, Mobject]]] = dict()
        self.undo_stack = []
        self.redo_stack = []

        if self.start_at_animation_number is not None:
            self.skip_animations = True
        if self.file_writer.has_progress_display():
            self.show_animation_progress = False

        # Items associated with interaction
        self.mouse_point = Point()
        self.mouse_drag_point = Point()
        self.hold_on_wait = self.presenter_mode
        self.quit_interaction = False

        # Much nicer to work with deterministic scenes
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

    def __str__(self) -> str:
        return self.__class__.__name__

    def run(self) -> None:
        self.virtual_animation_start_time: float = 0
        self.real_animation_start_time: float = time.time()
        self.file_writer.begin()

        self.setup()
        try:
            self.construct()
            self.interact()
        except EndScene:
            pass
        except KeyboardInterrupt:
            # Get rid keyboard interupt symbols
            print("", end="\r")
            self.file_writer.ended_with_interrupt = True
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
        if self.window:
            self.window.destroy()
            self.window = None

    def interact(self) -> None:
        """
        If there is a window, enter a loop
        which updates the frame while under
        the hood calling the pyglet event loop
        """
        if self.window is None:
            return
        log.info(
            "\nTips: Using the keys `d`, `f`, or `z` " +
            "you can interact with the scene. " +
            "Press `command + q` or `esc` to quit"
        )
        self.skip_animations = False
        while not self.is_window_closing():
            self.update_frame(1 / self.camera.fps)

    def embed(
        self,
        close_scene_on_exit: bool = True,
        show_animation_progress: bool = False,
    ) -> None:
        if not self.preview:
            # Embed is only relevant with a preview
            return
        self.stop_skipping()
        self.update_frame(force_draw=True)
        self.save_state()
        self.show_animation_progress = show_animation_progress

        # Create embedded IPython terminal configured to have access to
        # the local namespace of the caller
        caller_frame = inspect.currentframe().f_back
        module = get_module(caller_frame.f_globals["__file__"])
        shell = InteractiveShellEmbed(user_module=module)

        # Add a few custom shortcuts to that local namespace
        local_ns = dict(caller_frame.f_locals)
        local_ns.update(
            play=self.play,
            wait=self.wait,
            add=self.add,
            remove=self.remove,
            clear=self.clear,
            save_state=self.save_state,
            undo=self.undo,
            redo=self.redo,
            i2g=self.i2g,
            i2m=self.i2m,
            checkpoint_paste=self.checkpoint_paste,
            touch=lambda: shell.enable_gui("manim"),
            notouch=lambda: shell.enable_gui(None),
        )

        # Update the shell module with the caller's locals + shortcuts
        module.__dict__.update(local_ns)

        # Enables gui interactions during the embed
        def inputhook(context):
            while not context.input_is_ready():
                if not self.is_window_closing():
                    self.update_frame(dt=0)
            if self.is_window_closing():
                shell.ask_exit()

        pt_inputhooks.register("manim", inputhook)
        shell.enable_gui("manim")

        # Operation to run after each ipython command
        def post_cell_func(*args, **kwargs):
            if not self.is_window_closing():
                self.update_frame(dt=0, force_draw=True)

        shell.events.register("post_run_cell", post_cell_func)

        # Flash border, and potentially play sound, on exceptions
        def custom_exc(shell, etype, evalue, tb, tb_offset=None):
            # Show the error don't just swallow it
            shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)
            if self.embed_error_sound:
                os.system("printf '\a'")
            rect = FullScreenRectangle().set_stroke(RED, 30).set_fill(opacity=0)
            rect.fix_in_frame()
            self.play(VFadeInThenOut(rect, run_time=0.5))

        shell.set_custom_exc((Exception,), custom_exc)

        # Set desired exception mode
        shell.magic(f"xmode {self.embed_exception_mode}")

        # Launch shell
        shell()

        # End scene when exiting an embed
        if close_scene_on_exit:
            raise EndScene()

    # Only these methods should touch the camera

    def get_image(self) -> Image:
        if self.window is not None:
            self.camera.use_window_fbo(False)
            self.camera.capture(*self.render_groups)
        image = self.camera.get_image()
        if self.window is not None:
            self.camera.use_window_fbo(True)
        return image

    def show(self) -> None:
        self.update_frame(force_draw=True)
        self.get_image().show()

    def update_frame(self, dt: float = 0, force_draw: bool = False) -> None:
        self.increment_time(dt)
        self.update_mobjects(dt)
        if self.skip_animations and not force_draw:
            return

        if self.is_window_closing():
            raise EndScene()

        if self.window and dt == 0 and not self.window.has_undrawn_event() and not force_draw:
            # In this case, there's no need for new rendering, but we
            # shoudl still listen for new events
            self.window._window.dispatch_events()
            return

        self.camera.capture(*self.render_groups)

        if self.window and not self.skip_animations:
            vt = self.time - self.virtual_animation_start_time
            rt = time.time() - self.real_animation_start_time
            time.sleep(max(vt - rt, 0))

    def emit_frame(self) -> None:
        if not self.skip_animations:
            self.file_writer.write_frame(self.camera)

    # Related to updating

    def update_mobjects(self, dt: float) -> None:
        for mobject in self.mobjects:
            mobject.update(dt)

    def should_update_mobjects(self) -> bool:
        return self.always_update_mobjects or any(
            mob.has_updaters() for mob in self.mobjects
        )

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

    def assemble_render_groups(self):
        """
        Rendering can be more efficient when mobjects of the
        same type are grouped together, so this function creates
        Groups of all clusters of adjacent Mobjects in the scene
        """
        batches = batch_by_property(
            self.mobjects,
            lambda m: str(type(m)) + str(m.get_shader_wrapper(self.camera.ctx).get_id())
        )

        for group in self.render_groups:
            group.clear()
        self.render_groups = [
            batch[0].get_group_class()(*batch)
            for batch, key in batches
        ]

    @staticmethod
    def affects_mobject_list(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.assemble_render_groups()
            return self
        return wrapper

    @affects_mobject_list
    def add(self, *new_mobjects: Mobject):
        """
        Mobjects will be displayed, from background to
        foreground in the order with which they are added.
        """
        self.remove(*new_mobjects)
        self.mobjects += new_mobjects

        # Reorder based on z_index
        id_to_scene_order = {id(m): idx for idx, m in enumerate(self.mobjects)}
        self.mobjects.sort(key=lambda m: (m.z_index, id_to_scene_order[id(m)]))

        self.id_to_mobject_map.update({
            id(sm): sm
            for m in new_mobjects
            for sm in m.get_family()
        })
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

    @affects_mobject_list
    def replace(self, mobject: Mobject, *replacements: Mobject):
        if mobject in self.mobjects:
            index = self.mobjects.index(mobject)
            self.mobjects = [
                *self.mobjects[:index],
                *replacements,
                *self.mobjects[index + 1:]
            ]
        return self

    @affects_mobject_list
    def remove(self, *mobjects_to_remove: Mobject):
        """
        Removes anything in mobjects from scenes mobject list, but in the event that one
        of the items to be removed is a member of the family of an item in mobject_list,
        the other family members are added back into the list.

        For example, if the scene includes Group(m1, m2, m3), and we call scene.remove(m1),
        the desired behavior is for the scene to then include m2 and m3 (ungrouped).
        """
        to_remove = set(extract_mobject_family_members(mobjects_to_remove))
        new_mobjects, _ = recursive_mobject_remove(self.mobjects, to_remove)
        self.mobjects = new_mobjects

    def bring_to_front(self, *mobjects: Mobject):
        self.add(*mobjects)
        return self

    @affects_mobject_list
    def bring_to_back(self, *mobjects: Mobject):
        self.remove(*mobjects)
        self.mobjects = list(mobjects) + self.mobjects
        return self

    @affects_mobject_list
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
        return self.id_to_mobject_map[id_value]

    def ids_to_group(self, *id_values):
        return self.get_group(*filter(
            lambda x: x is not None,
            map(self.id_to_mobject, id_values)
        ))

    def i2g(self, *id_values):
        return self.ids_to_group(*id_values)

    def i2m(self, id_value):
        return self.id_to_mobject(id_value)

    # Related to skipping

    def update_skipping_status(self) -> None:
        if self.start_at_animation_number is not None:
            if self.num_plays == self.start_at_animation_number:
                self.skip_time = self.time
                if not self.original_skipping_status:
                    self.stop_skipping()
        if self.end_at_animation_number is not None:
            if self.num_plays >= self.end_at_animation_number:
                raise EndScene()

    def stop_skipping(self) -> None:
        self.virtual_animation_start_time = self.time
        self.real_animation_start_time = time.time()
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

        times = np.arange(0, run_time, 1 / self.camera.fps) + 1 / self.camera.fps

        self.file_writer.set_progress_display_description(sub_desc=desc)

        if self.show_animation_progress:
            return ProgressDisplay(
                times,
                total=n_iterations,
                leave=self.leave_progress_bars,
                ascii=True if platform.system() == 'Windows' else None,
                desc=desc,
                bar_format="{l_bar} {n_fmt:3}/{total_fmt:3} {rate_fmt}{postfix}",
            )
        else:
            return times

    def get_run_time(self, animations: Iterable[Animation]) -> float:
        return np.max([animation.get_run_time() for animation in animations])

    def get_animation_time_progression(
        self,
        animations: Iterable[Animation]
    ) -> list[float] | np.ndarray | ProgressDisplay:
        animations = list(animations)
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

    def pre_play(self):
        if self.presenter_mode and self.num_plays == 0:
            self.hold_loop()

        self.update_skipping_status()

        if not self.skip_animations:
            self.file_writer.begin_animation()

        if self.window:
            self.virtual_animation_start_time = self.time
            self.real_animation_start_time = time.time()

    def post_play(self):
        if not self.skip_animations:
            self.file_writer.end_animation()

        if self.skip_animations and self.window is not None:
            # Show some quick frames along the way
            self.update_frame(dt=0, force_draw=True)

        self.num_plays += 1

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

    @affects_mobject_list
    def play(
        self,
        *proto_animations: Animation | _AnimationBuilder,
        run_time: float | None = None,
        rate_func: Callable[[float], float] | None = None,
        lag_ratio: float | None = None,
    ) -> None:
        if len(proto_animations) == 0:
            log.warning("Called Scene.play with no animations")
            return
        animations = list(map(prepare_animation, proto_animations))
        for anim in animations:
            anim.update_rate_info(run_time, rate_func, lag_ratio)
        self.pre_play()
        self.begin_animations(animations)
        self.progress_through_animations(animations)
        self.finish_animations(animations)
        self.post_play()

    def wait(
        self,
        duration: float = DEFAULT_WAIT_TIME,
        stop_condition: Callable[[], bool] = None,
        note: str = None,
        ignore_presenter_mode: bool = False
    ):
        self.pre_play()
        self.update_mobjects(dt=0)  # Any problems with this?
        if self.presenter_mode and not self.skip_animations and not ignore_presenter_mode:
            if note:
                log.info(note)
            self.hold_loop()
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
        self.post_play()

    def hold_loop(self):
        while self.hold_on_wait:
            self.update_frame(dt=1 / self.camera.fps)
        self.hold_on_wait = True

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

    def get_state(self) -> SceneState:
        return SceneState(self)

    @affects_mobject_list
    def restore_state(self, scene_state: SceneState):
        scene_state.restore_scene(self)

    def save_state(self) -> None:
        if not self.preview:
            return
        state = self.get_state()
        if self.undo_stack and state.mobjects_match(self.undo_stack[-1]):
            return
        self.redo_stack = []
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_num_saved_states:
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.get_state())
            self.restore_state(self.undo_stack.pop())

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.get_state())
            self.restore_state(self.redo_stack.pop())

    def checkpoint_paste(
        self,
        skip: bool = False,
        record: bool = False,
        progress_bar: bool = True
    ):
        """
        Used during interactive development to run (or re-run)
        a block of scene code.

        If the copied selection starts with a comment, this will
        revert to the state of the scene the first time this function
        was called on a block of code starting with that comment.
        """
        shell = get_ipython()
        if shell is None or self.window is None:
            raise Exception(
                "Scene.checkpoint_paste cannot be called outside of " +
                "an ipython shell"
            )

        pasted = pyperclip.paste()
        lines = pasted.split("\n")

        # Commented lines trigger saved checkpoints
        if lines[0].lstrip().startswith("#"):
            if lines[0] not in self.checkpoint_states:
                self.checkpoint(lines[0])
            else:
                self.revert_to_checkpoint(lines[0])

        # Copied methods of a scene are handled specially
        # A bit hacky, yes, but convenient
        method_pattern = r"^def\s+([a-zA-Z_]\w*)\s*\(self.*\):"
        method_names = re.findall(method_pattern ,lines[0].strip())
        if method_names:
            method_name = method_names[0]
            indent = " " * lines[0].index(lines[0].strip())
            pasted = "\n".join([
                # Remove self from function signature
                re.sub(r"self(,\s*)?", "", lines[0]),
                *lines[1:],
                # Attach to scene via self.func_name = func_name
                f"{indent}self.{method_name} = {method_name}"
            ])

        # Keep track of skipping and progress bar status
        self.skip_animations = skip

        prev_progress = self.show_animation_progress
        self.show_animation_progress = progress_bar

        if record:
            self.camera.use_window_fbo(False)
            self.file_writer.begin_insert()

        shell.run_cell(pasted)

        if record:
            self.file_writer.end_insert()
            self.camera.use_window_fbo(True)

        self.stop_skipping()
        self.show_animation_progress = prev_progress

    def checkpoint(self, key: str):
        self.checkpoint_states[key] = self.get_state()

    def revert_to_checkpoint(self, key: str):
        if key not in self.checkpoint_states:
            log.error(f"No checkpoint at {key}")
            return
        all_keys = list(self.checkpoint_states.keys())
        index = all_keys.index(key)
        for later_key in all_keys[index + 1:]:
            self.checkpoint_states.pop(later_key)

        self.restore_state(self.checkpoint_states[key])

    def clear_checkpoints(self):
        self.checkpoint_states = dict()

    def save_mobject_to_file(self, mobject: Mobject, file_path: str | None = None) -> None:
        if file_path is None:
            file_path = self.file_writer.get_saved_mobject_path(mobject)
            if file_path is None:
                return
        mobject.save_to_file(file_path)

    def load_mobject(self, file_name):
        if os.path.exists(file_name):
            path = file_name
        else:
            directory = self.file_writer.get_saved_mobject_directory()
            path = os.path.join(directory, file_name)
        return Mobject.load(path)

    def is_window_closing(self):
        return self.window and (self.window.is_closing or self.quit_interaction)

    # Event handling
    def set_floor_plane(self, plane: str = "xy"):
        if plane == "xy":
            self.frame.set_euler_axes("zxz")
        elif plane == "xz":
            self.frame.set_euler_axes("zxy")
        else:
            raise Exception("Only `xz` and `xy` are valid floor planes")

    def on_mouse_motion(
        self,
        point: Vect3,
        d_point: Vect3
    ) -> None:
        assert self.window is not None
        self.mouse_point.move_to(point)

        event_data = {"point": point, "d_point": d_point}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseMotionEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

        frame = self.camera.frame
        # Handle perspective changes
        if self.window.is_key_pressed(ord(PAN_3D_KEY)):
            ff_d_point = frame.to_fixed_frame_point(d_point, relative=True)
            ff_d_point *= self.pan_sensitivity
            frame.increment_theta(-ff_d_point[0])
            frame.increment_phi(ff_d_point[1])
        # Handle frame movements
        elif self.window.is_key_pressed(ord(FRAME_SHIFT_KEY)):
            frame.shift(-d_point)

    def on_mouse_drag(
        self,
        point: Vect3,
        d_point: Vect3,
        buttons: int,
        modifiers: int
    ) -> None:
        self.mouse_drag_point.move_to(point)
        if self.drag_to_pan:
            self.frame.shift(-d_point)

        event_data = {"point": point, "d_point": d_point, "buttons": buttons, "modifiers": modifiers}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseDragEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_press(
        self,
        point: Vect3,
        button: int,
        mods: int
    ) -> None:
        self.mouse_drag_point.move_to(point)
        event_data = {"point": point, "button": button, "mods": mods}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MousePressEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_release(
        self,
        point: Vect3,
        button: int,
        mods: int
    ) -> None:
        event_data = {"point": point, "button": button, "mods": mods}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseReleaseEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_scroll(
        self,
        point: Vect3,
        offset: Vect3,
        x_pixel_offset: float,
        y_pixel_offset: float
    ) -> None:
        event_data = {"point": point, "offset": offset}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseScrollEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

        rel_offset = y_pixel_offset / self.camera.get_pixel_height()
        self.frame.scale(
            1 - self.scroll_sensitivity * rel_offset,
            about_point=point
        )

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

        if char == RESET_FRAME_KEY:
            self.play(self.camera.frame.animate.to_default_state())
        elif char == "z" and modifiers == COMMAND_MODIFIER:
            self.undo()
        elif char == "z" and modifiers == COMMAND_MODIFIER | SHIFT_MODIFIER:
            self.redo()
        # command + q
        elif char == QUIT_KEY and modifiers == COMMAND_MODIFIER:
            self.quit_interaction = True
        # Space or right arrow
        elif char == " " or symbol == ARROW_SYMBOLS[2]:
            self.hold_on_wait = False

    def on_resize(self, width: int, height: int) -> None:
        pass

    def on_show(self) -> None:
        pass

    def on_hide(self) -> None:
        pass

    def on_close(self) -> None:
        pass


class SceneState():
    def __init__(self, scene: Scene, ignore: list[Mobject] | None = None):
        self.time = scene.time
        self.num_plays = scene.num_plays
        self.mobjects_to_copies = OrderedDict.fromkeys(scene.mobjects)
        if ignore:
            for mob in ignore:
                self.mobjects_to_copies.pop(mob, None)

        last_m2c = scene.undo_stack[-1].mobjects_to_copies if scene.undo_stack else dict()
        for mob in self.mobjects_to_copies:
            # If it hasn't changed since the last state, just point to the
            # same copy as before
            if mob in last_m2c and last_m2c[mob].looks_identical(mob):
                self.mobjects_to_copies[mob] = last_m2c[mob]
            else:
                self.mobjects_to_copies[mob] = mob.copy()

    def __eq__(self, state: SceneState):
        return all((
            self.time == state.time,
            self.num_plays == state.num_plays,
            self.mobjects_to_copies == state.mobjects_to_copies
        ))

    def mobjects_match(self, state: SceneState):
        return self.mobjects_to_copies == state.mobjects_to_copies

    def n_changes(self, state: SceneState):
        m2c = state.mobjects_to_copies
        return sum(
            1 - int(mob in m2c and mob.looks_identical(m2c[mob]))
            for mob in self.mobjects_to_copies
        )

    def restore_scene(self, scene: Scene):
        scene.time = self.time
        scene.num_plays = self.num_plays
        scene.mobjects = [
            mob.become(mob_copy)
            for mob, mob_copy in self.mobjects_to_copies.items()
        ]


class EndScene(Exception):
    pass


class ThreeDScene(Scene):
    samples = 4
    default_frame_orientation = (-30, 70)
    always_depth_test = True

    def add(self, *mobjects: Mobject, set_depth_test: bool = True, perp_stroke: bool = True):
        for mob in mobjects:
            if set_depth_test and not mob.is_fixed_in_frame() and self.always_depth_test:
                mob.apply_depth_test()
            if isinstance(mob, VMobject) and mob.has_stroke() and perp_stroke:
                mob.set_flat_stroke(False)
        super().add(*mobjects)
