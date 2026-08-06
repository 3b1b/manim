from __future__ import annotations

import glfw
import numpy as np
import wgpu
from rendercanvas.glfw import RenderCanvas

from manimlib.constants import ASPECT_RATIO
from manimlib.constants import FRAME_SHAPE
from manimlib.event_keys import Keys
from manimlib.event_keys import Mods
from manimlib.utils.shaders import get_shader_code_from_file
from manimlib.utils.shaders import get_shader_module

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Sequence
    from manimlib.renderer.renderer import Renderer
    from manimlib.scene.scene import Scene


# The canvas names a key the way a browser does, manim names it after event_keys.py, and this
# is where the two meet. A key which types something needs no entry, being named by what it
# types in both.
KEY_NAMES: dict[str, int] = {
    "Backspace": Keys.BACKSPACE,
    "Tab": Keys.TAB,
    "Enter": Keys.ENTER,
    "Escape": Keys.ESCAPE,
    "Delete": Keys.DELETE,
    "ArrowLeft": Keys.LEFT,
    "ArrowRight": Keys.RIGHT,
    "ArrowUp": Keys.UP,
    "ArrowDown": Keys.DOWN,
    "Shift": Keys.SHIFT,
    "Control": Keys.CTRL,
    "Alt": Keys.ALT,
    "Meta": Keys.CMD,
}
MOD_NAMES: dict[str, int] = {
    "Shift": Mods.SHIFT,
    "Control": Mods.CTRL,
    "Alt": Mods.ALT,
    "Meta": Mods.CMD,
}
# A wheel is reported in hundredths of a notch, where scroll_sensitivity expects whole ones
WHEEL_NOTCH = 100.0
# The shader which puts a finished frame on the surface, see Window.present
PRESENT_SHADER = "present.wgsl"
# Where the corner named by a position string sits along each edge of the monitor
POSITION_STEPS = {"L": 0.0, "U": 0.0, "O": 0.5, "R": 1.0, "D": 1.0}


def to_key(name: str) -> Optional[int]:
    """
    manim's name for a key, or None for one it has no name for, which is every key nothing
    can be bound to. A letter comes back the same whether or not shift was held, so that a
    binding tested while shift is down still matches.
    """
    if name in KEY_NAMES:
        return KEY_NAMES[name]
    return ord(name.lower()) if len(name) == 1 else None


def to_mods(names: Sequence[str]) -> int:
    return sum(MOD_NAMES.get(name, 0) for name in names)


class Window(object):
    """
    Where a scene is previewed: somewhere to show a finished frame, and where mouse and key
    events come from.

    manim drives its own loop, self.wait and self.embed being that loop, so a frame is asked
    for whenever the scene says rather than from a callback the canvas decides when to call.
    What the canvas is left to own is the surface, kept configured through resizes and whatever
    the display's scale factor is, and the presenting of a texture onto it.

    That canvas is rendercanvas's glfw one, over a glfw window this reaches for directly in the
    two places a canvas offers no say, see glfw_window.
    """

    def __init__(
        self,
        scene: Optional[Scene] = None,
        position_string: str = "UR",
        monitor_index: int = 1,
        full_screen: bool = False,
        size: Optional[tuple[int, int]] = None,
        position: Optional[tuple[int, int]] = None,
    ):
        self.scene: Optional[Scene] = None
        self.renderer: Optional[Renderer] = None
        self.frame_view = None
        self.pressed_keys: set[int] = set()
        self.pointer_position = np.zeros(2)
        self.undrawn_event = True

        # Asking about monitors needs glfw started, which creating the canvas would otherwise
        # be what did
        glfw.init()
        monitor = self.get_monitor(monitor_index)
        self.canvas = RenderCanvas(
            size=size or self.get_default_size(monitor, full_screen),
            update_mode="manual",
        )
        self.canvas.request_draw(self.draw)
        self.context = self.canvas.get_context("wgpu")
        glfw.set_window_pos(self.glfw_window, *(
            position or self.get_position(monitor, position_string)
        ))

        for event_type, handler in [
            ("pointer_move", self.on_pointer_move),
            ("pointer_down", self.on_pointer_down),
            ("pointer_up", self.on_pointer_up),
            ("wheel", self.on_wheel),
            ("key_down", self.on_key_down),
            ("key_up", self.on_key_up),
            ("resize", self.on_resize),
            ("close", self.on_close),
        ]:
            self.canvas.add_event_handler(handler, event_type)

        if scene:
            self.init_for_scene(scene)

    @property
    def glfw_window(self):
        """
        The window itself, for the two things a canvas offers no way to say: where on which
        monitor it opens, and that it should take focus.
        """
        return self.canvas._window

    def init_for_scene(self, scene: Scene) -> None:
        """
        Resets the state and updates the scene associated to this window.

        This is necessary when we want to reuse an *existing* window after a
        `scene.reload()` was requested, which will create new scene instances.
        """
        self.pressed_keys.clear()
        self.undrawn_event = True
        self.scene = scene
        self.canvas.set_title(str(scene))

    def configure(self, renderer: Renderer) -> None:
        """
        Points the surface at the device whose frames it will be showing, the first moment
        either knows of the other: a window outlives the scenes shown in it, and a scene's
        camera is what brings a device.

        The plain form of whatever format the surface prefers, never the sRGB one. Writing to
        an sRGB target gamma encodes what the shader returned, and a frame here already holds
        the color it means: encoding again lightens everything and washes it out.
        """
        self.renderer = renderer
        self.device = renderer.device
        preferred = self.context.get_preferred_format(renderer.device.adapter)
        self.format = preferred.removesuffix("-srgb")
        self.context.configure(device=renderer.device, format=self.format)
        self.init_present_resources()

    def get_size(self) -> tuple[int, int]:
        """How many pixels there are to draw, which is not the size in screen coordinates"""
        return self.canvas.get_physical_size()

    def show(self, frame_view) -> None:
        """
        Puts a finished frame on screen. The canvas presents whatever its draw function drew,
        so the frame is handed over and then asked for.
        """
        self.frame_view = frame_view
        self.canvas.force_draw()
        self.undrawn_event = False
        self.poll_events()

    def draw(self) -> None:
        self.present(self.context.get_current_texture().create_view())

    def init_present_resources(self) -> None:
        """What a finished frame is read through on its way to the surface, made once"""
        self.present_layout = self.device.create_bind_group_layout(entries=[
            {"binding": 0, "visibility": wgpu.ShaderStage.FRAGMENT,
             "texture": {"sample_type": wgpu.TextureSampleType.float}},
            {"binding": 1, "visibility": wgpu.ShaderStage.FRAGMENT,
             "sampler": {"type": wgpu.SamplerBindingType.filtering}},
        ])
        # Smoothly, since a window is rarely exactly the size of the frame drawn for it
        self.present_sampler = self.device.create_sampler(
            mag_filter=wgpu.FilterMode.linear, min_filter=wgpu.FilterMode.linear,
        )
        module = get_shader_module(
            self.device, get_shader_code_from_file(PRESENT_SHADER),
        )
        self.present_pipeline = self.device.create_render_pipeline(
            layout=self.device.create_pipeline_layout(
                bind_group_layouts=[self.present_layout],
            ),
            vertex={"module": module, "entry_point": "vs_main"},
            fragment={
                "module": module,
                "entry_point": "fs_main",
                "targets": [{"format": self.format}],
            },
            primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
        )

    def present(self, target_view) -> None:
        """
        Draws the finished frame onto what the surface gave us, stretched to fill it, see
        shaders/present.wgsl. A pass of its own, the two textures differing in size and format.
        """
        bind_group = self.device.create_bind_group(layout=self.present_layout, entries=[
            {"binding": 0, "resource": self.frame_view},
            {"binding": 1, "resource": self.present_sampler},
        ])
        encoder = self.device.create_command_encoder()
        render_pass = encoder.begin_render_pass(color_attachments=[{
            "view": target_view,
            "load_op": wgpu.LoadOp.clear,
            "store_op": wgpu.StoreOp.store,
            "clear_value": (0.0, 0.0, 0.0, 1.0),
        }])
        render_pass.set_pipeline(self.present_pipeline)
        render_pass.set_bind_group(0, bind_group)
        render_pass.draw(3)
        render_pass.end()
        self.renderer.queue.submit([encoder.finish()])

    def poll_events(self) -> None:
        """
        Hands whatever the window has to say to the handlers below, and notices if it has been
        closed. A canvas would do this from its own loop, which manim does not run.
        """
        self.canvas._process_events()

    @property
    def is_closing(self) -> bool:
        return self.canvas.get_closed()

    def has_undrawn_event(self) -> bool:
        return self.undrawn_event

    def is_key_pressed(self, key: int) -> bool:
        return key in self.pressed_keys

    def focus(self) -> None:
        glfw.focus_window(self.glfw_window)

    def destroy(self) -> None:
        self.canvas.close()

    # Where it opens

    def get_monitor(self, index: int):
        monitors = glfw.get_monitors()
        return monitors[min(index, len(monitors) - 1)] if monitors else None

    def get_monitor_area(self, monitor) -> tuple[int, int, int, int]:
        """Where the monitor's usable area is and how big it is, in screen coordinates"""
        if monitor is None:
            return (0, 0, 1920, 1080)
        return glfw.get_monitor_workarea(monitor)

    def get_default_size(self, monitor, full_screen: bool) -> tuple[int, int]:
        _, _, width, _ = self.get_monitor_area(monitor)
        if not full_screen:
            width //= 2
        return (width, int(width / ASPECT_RATIO))

    def get_position(self, monitor, position_string: str) -> tuple[int, int]:
        """
        Which corner of the monitor to open in, named by a pair of characters as in UR for
        upper right or OO for the middle, see the window section of default_config.yml.
        """
        left, top, width, height = self.get_monitor_area(monitor)
        size = self.canvas.get_logical_size()
        return (
            int(left + POSITION_STEPS[position_string[1]] * (width - size[0])),
            int(top + POSITION_STEPS[position_string[0]] * (height - size[1])),
        )

    # Events, translated and handed to the scene

    def note_event(self) -> None:
        self.undrawn_event = True

    def pixel_coords_to_space_coords(
        self,
        px: float,
        py: float,
        relative: bool = False
    ) -> np.ndarray:
        """
        Where in the scene a place in the window is, both measuring y upwards from the
        bottom, see event_position for where an event's own way round is undone.
        """
        if self.scene is None or not hasattr(self.scene, "frame"):
            return np.zeros(3)

        pixel_shape = np.array(self.canvas.get_logical_size())
        fixed_frame_shape = np.array(FRAME_SHAPE)
        frame = self.scene.frame

        coords = np.zeros(3)
        coords[:2] = (fixed_frame_shape / pixel_shape) * np.array([px, py])
        if not relative:
            coords[:2] -= 0.5 * fixed_frame_shape
        return frame.from_fixed_frame_point(coords, relative)

    def event_position(self, event: dict) -> np.ndarray:
        """
        Where in the window something happened, measuring y upwards from the bottom the way
        the scene does, where an event measures it downwards from the top.
        """
        _, height = self.canvas.get_logical_size()
        return np.array([event["x"], height - event["y"]])

    def event_point(self, event: dict) -> np.ndarray:
        return self.pixel_coords_to_space_coords(*self.event_position(event))

    def on_pointer_move(self, event: dict) -> None:
        self.note_event()
        if self.scene is None:
            return
        position = self.event_position(event)
        movement = position - self.pointer_position
        self.pointer_position = position
        point = self.pixel_coords_to_space_coords(*position)
        d_point = self.pixel_coords_to_space_coords(*movement, relative=True)
        if event["buttons"]:
            # A move with a button held is what manim means by a drag; nothing but the
            # buttons distinguishes the two
            self.scene.on_mouse_drag(
                point, d_point, event["buttons"], to_mods(event["modifiers"]),
            )
        else:
            self.scene.on_mouse_motion(point, d_point)

    def on_pointer_down(self, event: dict) -> None:
        self.note_event()
        if self.scene is None:
            return
        self.pointer_position = self.event_position(event)
        self.scene.on_mouse_press(
            self.event_point(event), event["button"], to_mods(event["modifiers"]),
        )

    def on_pointer_up(self, event: dict) -> None:
        self.note_event()
        if self.scene is None:
            return
        self.scene.on_mouse_release(
            self.event_point(event), event["button"], to_mods(event["modifiers"]),
        )

    def on_wheel(self, event: dict) -> None:
        self.note_event()
        if self.scene is None:
            return
        notches = np.array([event["dx"], event["dy"]]) / WHEEL_NOTCH
        self.scene.on_mouse_scroll(
            self.event_point(event),
            self.pixel_coords_to_space_coords(*notches, relative=True),
            *notches,
        )

    def on_key_down(self, event: dict) -> None:
        self.note_event()
        key = to_key(event["key"])
        if key is None:
            return
        self.pressed_keys.add(key)
        if self.scene:
            self.scene.on_key_press(key, to_mods(event["modifiers"]))

    def on_key_up(self, event: dict) -> None:
        self.note_event()
        key = to_key(event["key"])
        if key is None:
            return
        self.pressed_keys.discard(key)
        if self.scene:
            self.scene.on_key_release(key, to_mods(event["modifiers"]))

    def on_resize(self, event: dict) -> None:
        self.note_event()
        if self.scene:
            self.scene.on_resize(event["width"], event["height"])

    def on_close(self, event: dict) -> None:
        self.note_event()
        if self.scene:
            self.scene.on_close()
