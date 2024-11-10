from __future__ import annotations

import numpy as np

import moderngl_window as mglw
from moderngl_window.context.pyglet.window import Window as PygletWindow
from moderngl_window.timers.clock import Timer
from screeninfo import get_monitors
from functools import wraps

from manimlib.constants import FRAME_SHAPE
from manimlib.utils.customization import get_customization

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.scene.scene import Scene


class Window(PygletWindow):
    fullscreen: bool = False
    resizable: bool = True
    gl_version: tuple[int, int] = (3, 3)
    vsync: bool = True
    cursor: bool = True

    def __init__(
        self,
        scene: Scene,
        size: tuple[int, int] = (1280, 720),
        samples: int = 0
    ):
        scene.window = self
        super().__init__(size=size, samples=samples)

        self.default_size = size
        self.default_position = self.find_initial_position(size)
        self.scene = scene
        self.pressed_keys = set()
        self.title = str(scene)
        self.size = size
        self.update_scene(scene)

        mglw.activate_context(window=self)

    def reset_state(self):
        self.pressed_keys.clear()
        self._has_undrawn_event = True

        mglw.activate_context(window=self)
        self.timer = Timer()
        self.config = mglw.WindowConfig(ctx=self.ctx, wnd=self, timer=self.timer)
        self.timer.start()

        self.to_default_position()

    def update_scene(self, scene: Scene):
        self.reset_state()
        self.scene = scene
        self.title = str(scene)

    def to_default_position(self):
        self.position = self.default_position
        # Hack. Sometimes, namely when configured to open in a separate window,
        # the window needs to be resized to display correctly.
        w, h = self.default_size
        self.size = (w - 1, h - 1)
        self.size = (w, h)

    def find_initial_position(self, size: tuple[int, int]) -> tuple[int, int]:
        custom_position = get_customization()["window_position"]
        monitors = get_monitors()
        mon_index = get_customization()["window_monitor"]
        monitor = monitors[min(mon_index, len(monitors) - 1)]
        window_width, window_height = size
        # Position might be specified with a string of the form
        # x,y for integers x and y
        if "," in custom_position:
            return tuple(map(int, custom_position.split(",")))

        # Alternatively, it might be specified with a string like
        # UR, OO, DL, etc. specifying what corner it should go to
        char_to_n = {"L": 0, "U": 0, "O": 1, "R": 2, "D": 2}
        width_diff = monitor.width - window_width
        height_diff = monitor.height - window_height
        return (
            monitor.x + char_to_n[custom_position[1]] * width_diff // 2,
            -monitor.y + char_to_n[custom_position[0]] * height_diff // 2,
        )

    # Delegate event handling to scene
    def pixel_coords_to_space_coords(
        self,
        px: int,
        py: int,
        relative: bool = False
    ) -> np.ndarray:
        if not hasattr(self.scene, "frame"):
            return np.zeros(3)

        pixel_shape = np.array(self.size)
        fixed_frame_shape = np.array(FRAME_SHAPE)
        frame = self.scene.frame

        coords = np.zeros(3)
        coords[:2] = (fixed_frame_shape / pixel_shape) * np.array([px, py])
        if not relative:
            coords[:2] -= 0.5 * fixed_frame_shape
        return frame.from_fixed_frame_point(coords, relative)

    def has_undrawn_event(self) -> bool:
        return self._has_undrawn_event

    def swap_buffers(self):
        super().swap_buffers()
        self._has_undrawn_event = False

    @staticmethod
    def note_undrawn_event(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._has_undrawn_event = True
        return wrapper

    @note_undrawn_event
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        super().on_mouse_motion(x, y, dx, dy)
        point = self.pixel_coords_to_space_coords(x, y)
        d_point = self.pixel_coords_to_space_coords(dx, dy, relative=True)
        self.scene.on_mouse_motion(point, d_point)

    @note_undrawn_event
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        point = self.pixel_coords_to_space_coords(x, y)
        d_point = self.pixel_coords_to_space_coords(dx, dy, relative=True)
        self.scene.on_mouse_drag(point, d_point, buttons, modifiers)

    @note_undrawn_event
    def on_mouse_press(self, x: int, y: int, button: int, mods: int) -> None:
        super().on_mouse_press(x, y, button, mods)
        point = self.pixel_coords_to_space_coords(x, y)
        self.scene.on_mouse_press(point, button, mods)

    @note_undrawn_event
    def on_mouse_release(self, x: int, y: int, button: int, mods: int) -> None:
        super().on_mouse_release(x, y, button, mods)
        point = self.pixel_coords_to_space_coords(x, y)
        self.scene.on_mouse_release(point, button, mods)

    @note_undrawn_event
    def on_mouse_scroll(self, x: int, y: int, x_offset: float, y_offset: float) -> None:
        super().on_mouse_scroll(x, y, x_offset, y_offset)
        point = self.pixel_coords_to_space_coords(x, y)
        offset = self.pixel_coords_to_space_coords(x_offset, y_offset, relative=True)
        self.scene.on_mouse_scroll(point, offset, x_offset, y_offset)

    @note_undrawn_event
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.pressed_keys.add(symbol)  # Modifiers?
        super().on_key_press(symbol, modifiers)
        self.scene.on_key_press(symbol, modifiers)

    @note_undrawn_event
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        self.pressed_keys.difference_update({symbol})  # Modifiers?
        super().on_key_release(symbol, modifiers)
        self.scene.on_key_release(symbol, modifiers)

    @note_undrawn_event
    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.scene.on_resize(width, height)

    @note_undrawn_event
    def on_show(self) -> None:
        super().on_show()
        self.scene.on_show()

    @note_undrawn_event
    def on_hide(self) -> None:
        super().on_hide()
        self.scene.on_hide()

    @note_undrawn_event
    def on_close(self) -> None:
        super().on_close()
        self.scene.on_close()

    def is_key_pressed(self, symbol: int) -> bool:
        return (symbol in self.pressed_keys)
