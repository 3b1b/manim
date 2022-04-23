from __future__ import annotations

import numpy as np

import moderngl_window as mglw
from moderngl_window.context.pyglet.window import Window as PygletWindow
from moderngl_window.timers.clock import Timer
from screeninfo import get_monitors

from manimlib.utils.config_ops import digest_config
from manimlib.utils.customization import get_customization

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.scene.scene import Scene


class Window(PygletWindow):
    fullscreen = False
    resizable = True
    gl_version = (3, 3)
    vsync = True
    cursor = True

    def __init__(
        self,
        scene: Scene,
        size: tuple[int, int] = (1280, 720),
        **kwargs
    ):
        super().__init__(size=size)
        digest_config(self, kwargs)

        self.scene = scene
        self.pressed_keys = set()
        self.title = str(scene)
        self.size = size

        mglw.activate_context(window=self)
        self.timer = Timer()
        self.config = mglw.WindowConfig(ctx=self.ctx, wnd=self, timer=self.timer)
        self.timer.start()

        # No idea why, but when self.position is set once
        # it sometimes doesn't actually change the position
        # to the specified tuple on the rhs, but doing it
        # twice seems to make it work.  ¯\_(ツ)_/¯
        initial_position = self.find_initial_position(size)
        self.position = initial_position
        self.position = initial_position

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
        pw, ph = self.size
        fw, fh = self.scene.camera.get_frame_shape()
        fc = self.scene.camera.get_frame_center()
        if relative:
            return np.array([px / pw, py / ph, 0])
        else:
            return np.array([
                fc[0] + px * fw / pw - fw / 2,
                fc[1] + py * fh / ph - fh / 2,
                0
            ])

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        super().on_mouse_motion(x, y, dx, dy)
        point = self.pixel_coords_to_space_coords(x, y)
        d_point = self.pixel_coords_to_space_coords(dx, dy, relative=True)
        self.scene.on_mouse_motion(point, d_point)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        point = self.pixel_coords_to_space_coords(x, y)
        d_point = self.pixel_coords_to_space_coords(dx, dy, relative=True)
        self.scene.on_mouse_drag(point, d_point, buttons, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, mods: int) -> None:
        super().on_mouse_press(x, y, button, mods)
        point = self.pixel_coords_to_space_coords(x, y)
        self.scene.on_mouse_press(point, button, mods)

    def on_mouse_release(self, x: int, y: int, button: int, mods: int) -> None:
        super().on_mouse_release(x, y, button, mods)
        point = self.pixel_coords_to_space_coords(x, y)
        self.scene.on_mouse_release(point, button, mods)

    def on_mouse_scroll(self, x: int, y: int, x_offset: float, y_offset: float) -> None:
        super().on_mouse_scroll(x, y, x_offset, y_offset)
        point = self.pixel_coords_to_space_coords(x, y)
        offset = self.pixel_coords_to_space_coords(x_offset, y_offset, relative=True)
        self.scene.on_mouse_scroll(point, offset)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.pressed_keys.add(symbol)  # Modifiers?
        super().on_key_press(symbol, modifiers)
        self.scene.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        self.pressed_keys.difference_update({symbol})  # Modifiers?
        super().on_key_release(symbol, modifiers)
        self.scene.on_key_release(symbol, modifiers)

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.scene.on_resize(width, height)

    def on_show(self) -> None:
        super().on_show()
        self.scene.on_show()

    def on_hide(self) -> None:
        super().on_hide()
        self.scene.on_hide()

    def on_close(self) -> None:
        super().on_close()
        self.scene.on_close()

    def is_key_pressed(self, symbol: int) -> bool:
        return (symbol in self.pressed_keys)
