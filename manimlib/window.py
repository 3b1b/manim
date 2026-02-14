from __future__ import annotations

from functools import wraps

import moderngl
import numpy as np
import pyglet
import screeninfo

from pyglet.window import Window as PygletWindow

from manimlib.constants import ASPECT_RATIO
from manimlib.constants import FRAME_SHAPE

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, TypeVar, Optional
    from manimlib.scene.scene import Scene

    T = TypeVar("T")


class Window(PygletWindow):
    fullscreen: bool = False
    resizable: bool = True
    gl_version: tuple[int, int] = (3, 3)
    vsync: bool = True
    cursor: bool = True

    def __init__(
        self,
        scene: Optional[Scene] = None,
        position_string: str = "UR",
        monitor_index: int = 1,
        full_screen: bool = False,
        style: str = None,
        size: Optional[tuple[int, int]] = None,
        position: Optional[tuple[int, int]] = None,
        samples: int = 0,
    ):
        self.scene = scene
        self.monitor = self.get_monitor(monitor_index)
        self.default_size = size or self.get_default_size(full_screen)
        self.default_position = position or self.position_from_string(position_string)
        self.pressed_keys = set()
        self._has_undrawn_event = True

        config = pyglet.gl.Config(
            sample_buffers=1 if samples > 0 else 0,
            samples=samples,
            major_version=self.gl_version[0],
            minor_version=self.gl_version[1],
            double_buffer=True,
            depth_size=24,
            stencil_size=8,
        )

        pyglet.app.platform_event_loop.start()

        super().__init__(
            width=self.default_size[0],
            height=self.default_size[1],
            resizable=self.resizable,
            vsync=self.vsync,
            fullscreen=full_screen,
            style=style,
            config=config,
        )

        self.set_mouse_visible(self.cursor)
        self.set_mouse_passthrough(False)
        self.to_default_position()

        if self.scene:
            self.init_for_scene(scene)

    def init_for_scene(self, scene: Scene):
        """
        Resets the state and updates the scene associated to this window.

        This is necessary when we want to reuse an *existing* window after a
        `scene.reload()` was requested, which will create new scene instances.
        """
        self.pressed_keys.clear()
        self._has_undrawn_event = True

        self.scene = scene
        self.set_caption(str(scene))

        self.init_mgl_context()

        # This line seems to resync the viewport
        self.on_resize(*self.size)

    def init_mgl_context(self) -> None:
        self.ctx = moderngl.create_context()
        self.ctx.viewport = (0, 0, self.width, self.height)

    # Helper properties for width/height and position
    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    @size.setter
    def size(self, size: tuple[int, int]) -> None:
        self.set_size(*size)

    @property
    def position(self) -> tuple[int, int]:
        return self.get_location()

    @position.setter
    def position(self, pos: tuple[int, int]) -> None:
        self.set_location(*pos)

    def get_monitor(self, index):
        try:
            monitors = screeninfo.get_monitors()
            return monitors[min(index, len(monitors) - 1)]
        except screeninfo.ScreenInfoError:
            # Default fallback
            return screeninfo.Monitor(width=1920, height=1080)

    def get_default_size(self, full_screen=False):
        width = self.monitor.width // (1 if full_screen else 2)
        height = int(width // ASPECT_RATIO)
        return (width, height)

    def position_from_string(self, position_string):
        # Alternatively, it might be specified with a string like
        # UR, OO, DL, etc. specifying what corner it should go to
        char_to_n = {"L": 0, "U": 0, "O": 1, "R": 2, "D": 2}
        size = self.default_size
        width_diff = self.monitor.width - size[0]
        height_diff = self.monitor.height - size[1]
        x_step = char_to_n[position_string[1]] * width_diff // 2
        y_step = char_to_n[position_string[0]] * height_diff // 2
        return (self.monitor.x + x_step, -self.monitor.y + y_step)

    def focus(self):
        """
        Puts focus on this window by hiding and showing it again.

        Note that the pyglet `activate()` method didn't work as expected here,
        so that's why we have to use this workaround. This will produce a small
        flicker on the window but at least reliably focuses it. It may also
        offset the window position slightly.
        """
        self.set_visible(False)
        self.set_visible(True)

    def to_default_position(self):
        self.position = self.default_position
        # Hack. Sometimes, namely when configured to open in a separate window,
        # the window needs to be resized to display correctly.
        w, h = self.default_size
        self.size = (w - 1, h - 1)
        self.size = (w, h)

    # Delegate event handling to scene
    def pixel_coords_to_space_coords(
        self,
        px: int,
        py: int,
        relative: bool = False
    ) -> np.ndarray:
        if self.scene is None or not hasattr(self.scene, "frame"):
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

    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        if hasattr(self, "ctx"):
            self.ctx.clear(r, g, b, a, depth=1.0)
        else:
            super().clear()

    def swap_buffers(self) -> None:
        self.flip()
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
        if not self.scene:
            return
        point = self.pixel_coords_to_space_coords(x, y)
        d_point = self.pixel_coords_to_space_coords(dx, dy, relative=True)
        self.scene.on_mouse_motion(point, d_point)

    @note_undrawn_event
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        if not self.scene:
            return
        point = self.pixel_coords_to_space_coords(x, y)
        d_point = self.pixel_coords_to_space_coords(dx, dy, relative=True)
        self.scene.on_mouse_drag(point, d_point, buttons, modifiers)

    @note_undrawn_event
    def on_mouse_press(self, x: int, y: int, button: int, mods: int) -> None:
        if not self.scene:
            return
        point = self.pixel_coords_to_space_coords(x, y)
        self.scene.on_mouse_press(point, button, mods)

    @note_undrawn_event
    def on_mouse_release(self, x: int, y: int, button: int, mods: int) -> None:
        if not self.scene:
            return
        point = self.pixel_coords_to_space_coords(x, y)
        self.scene.on_mouse_release(point, button, mods)

    @note_undrawn_event
    def on_mouse_scroll(self, x: int, y: int, x_offset: float, y_offset: float) -> None:
        if not self.scene:
            return
        point = self.pixel_coords_to_space_coords(x, y)
        offset = self.pixel_coords_to_space_coords(x_offset, y_offset, relative=True)
        self.scene.on_mouse_scroll(point, offset, x_offset, y_offset)

    @note_undrawn_event
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)
        if symbol == pyglet.window.key.F11:
            if self.width == self.screen.width * self.screen.get_scale():
                self.to_default_position()
            else:
                self.maximize()
            return
        self.pressed_keys.add(symbol)  # Modifiers?
        if not self.scene:
            return
        self.scene.on_key_press(symbol, modifiers)

    @note_undrawn_event
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        self.pressed_keys.difference_update({symbol})  # Modifiers?
        if not self.scene:
            return
        self.scene.on_key_release(symbol, modifiers)

    @note_undrawn_event
    def on_resize(self, width: int, height: int) -> None:
        if hasattr(self, 'ctx'):
            self.ctx.viewport = (0, 0, width, height)
        if not self.scene:
            return
        self.scene.on_resize(width, height)

    @note_undrawn_event
    def on_show(self) -> None:
        if not self.scene:
            return
        self.scene.on_show()

    @note_undrawn_event
    def on_hide(self) -> None:
        if not self.scene:
            return
        self.scene.on_hide()

    @note_undrawn_event
    def on_close(self) -> None:
        super().on_close()
        if not self.scene:
            return
        self.scene.on_close()

    def is_key_pressed(self, symbol: int) -> bool:
        return (symbol in self.pressed_keys)

    # Methods for compatibility with previous window wrapper
    @property
    def is_closing(self) -> bool:
        return self.has_exit

    def destroy(self) -> None:
        if hasattr(self, "ctx"):
            self.ctx.release()
        self.close()
        pyglet.app.platform_event_loop.stop()
