import moderngl_window as mglw
from moderngl_window.context.pyglet.window import Window as PygletWindow
from moderngl_window.timers.clock import Timer
from screeninfo import get_monitors

from manimlib.utils.config_ops import digest_config
from manimlib.utils.customization import get_customization


class Window(PygletWindow):
    fullscreen = False
    resizable = True
    gl_version = (3, 3)
    vsync = True
    cursor = True

    def __init__(self, scene, **kwargs):
        super().__init__(**kwargs)
        digest_config(self, kwargs)

        self.init_mgl_context()
        mglw.activate_context(window=self)
        self.timer = Timer()
        self.config = mglw.WindowConfig(ctx=self.ctx, wnd=self, timer=self.timer)
        self.timer.start()

        self.scene = scene
        self.title = str(scene)
        self.pressed_keys = set()
        # No idea why, but when self.position is set once
        # it sometimes doesn't actually change the position
        # to the specified tuple on the rhs, but doing it
        # twice seems to make it work.  ¯\_(ツ)_/¯
        initial_position = self.find_initial_position()
        self.position = initial_position
        self.position = initial_position

        if "size" in kwargs:
            self.size = kwargs["size"]

    def find_initial_position(self):
        custom_position = get_customization()["window_position"]
        monitor = get_monitors()[get_customization()["window_monitor"]]
        window_width, window_height = self.size
        # Position might be specified with a string of the form
        # x,y for integers x and y
        if "," in custom_position:
            return tuple(map(int, custom_position.split(",")))

        # Alternatively, it might be specified with a string like
        # UR, OO, DL, etc. specifiying what corner it should go to
        char_to_n = {"L": 0, "U": 0, "O": 1, "R": 2, "D": 2}
        width_diff = monitor.width - window_width
        height_diff = monitor.height - window_height
        return (
            monitor.x + char_to_n[custom_position[1]] * width_diff // 2,
            -monitor.y + char_to_n[custom_position[0]] * height_diff // 2,
        )

    # Delegate event handling to scene
    def pixel_coords_to_space_coords(self, px, py, relative=False):
        return self.scene.camera.pixel_coords_to_space_coords(px, py, relative)

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        point = self.pixel_coords_to_space_coords(x, y)
        d_point = self.pixel_coords_to_space_coords(dx, dy, relative=True)
        self.scene.on_mouse_motion(point, d_point)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        point = self.pixel_coords_to_space_coords(x, y)
        d_point = self.pixel_coords_to_space_coords(dx, dy, relative=True)
        self.scene.on_mouse_drag(point, d_point, buttons, modifiers)

    def on_mouse_press(self, x: int, y: int, button, mods):
        super().on_mouse_press(x, y, button, mods)
        point = self.pixel_coords_to_space_coords(x, y)
        self.scene.on_mouse_press(point, button, mods)

    def on_mouse_release(self, x: int, y: int, button, mods):
        super().on_mouse_release(x, y, button, mods)
        point = self.pixel_coords_to_space_coords(x, y)
        self.scene.on_mouse_release(point, button, mods)

    def on_mouse_scroll(self, x, y, x_offset: float, y_offset: float):
        super().on_mouse_scroll(x, y, x_offset, y_offset)
        point = self.pixel_coords_to_space_coords(x, y)
        offset = self.pixel_coords_to_space_coords(x_offset, y_offset, relative=True)
        self.scene.on_mouse_scroll(point, offset)

    def on_key_press(self, symbol, modifiers):
        self.pressed_keys.add(symbol)  # Modifiers?
        super().on_key_press(symbol, modifiers)
        self.scene.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.pressed_keys.difference_update({symbol})  # Modifiers?
        super().on_key_release(symbol, modifiers)
        self.scene.on_key_release(symbol, modifiers)

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.scene.on_resize(width, height)

    def on_show(self):
        super().on_show()
        self.scene.on_show()

    def on_hide(self):
        super().on_hide()
        self.scene.on_hide()

    def on_close(self):
        super().on_close()
        self.scene.on_close()

    def is_key_pressed(self, symbol):
        return (symbol in self.pressed_keys)
