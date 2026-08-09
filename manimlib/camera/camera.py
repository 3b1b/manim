from __future__ import annotations

from contextlib import contextmanager

import numpy as np
import wgpu
from PIL import Image

from manimlib.camera.camera_frame import CameraFrame
from manimlib.constants import BLACK
from manimlib.constants import DEFAULT_RESOLUTION
from manimlib.constants import FRAME_HEIGHT
from manimlib.constants import FRAME_WIDTH
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.renderer.gpu import Gpu
from manimlib.renderer.pipeline import COLOR_FORMAT
from manimlib.renderer.pipeline import DEPTH_STENCIL_FORMAT
from manimlib.renderer.renderer import Renderer
from manimlib.utils.color import color_to_rgba

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from manimlib.typing import ManimColor, Vect3
    from manimlib.window import Window


class FrameStream(object):
    """
    Frames off the gpu and into somewhere they are being written, staying a frame behind so
    that the copy of one happens while the next is being drawn.

    Getting a frame back means copying the texture into a buffer the cpu can read, which the
    gpu cannot do until it has finished drawing, so asking and reading in one breath waits, as
    Camera.get_frame_bytes does. Here the copy is only asked for, and what gets written is the
    frame before it, whose copy has had a whole frame's drawing to finish.

    Frames still go to the same place in the same order. Whoever is writing them has only to
    drain what is in flight before closing, see SceneFileWriter.close_movie_pipe.
    """

    def __init__(self, camera: Camera, sink, behind: int = 1):
        self.camera = camera
        self.sink = sink
        self.behind = behind
        self.device = camera.gpu.device
        self.queue = camera.gpu.queue
        # Settled here rather than read afresh, since whatever is being written was opened
        # expecting frames of one size
        self.width, self.height = camera.get_pixel_shape()
        self.row = 4 * self.width
        # A texture copy leaves each row a multiple of 256 bytes from the next, so rows come
        # back with padding on the end of them unless the width happens to suit
        self.padded_row = self.row + (-self.row % 256)
        # One buffer per frame in flight and one more to be copying into, which is what being
        # a frame behind costs: a frame's worth of memory each, so 33MB apiece at 4k
        self.buffers = [
            self.device.create_buffer(
                size=self.padded_row * self.height,
                usage=wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.MAP_READ,
            )
            for _ in range(behind + 1)
        ]
        # Which buffers are waiting to be read, oldest first, and how many have been asked
        # for, counted so that no buffer receives a copy while still mapped from an earlier
        # frame
        self.waiting: list = []
        self.asked = 0

    def send(self) -> None:
        """Asks for the frame as it stands, and writes whichever one is ready"""
        buffer = self.buffers[self.asked % len(self.buffers)]
        self.asked += 1
        encoder = self.device.create_command_encoder()
        encoder.copy_texture_to_buffer(
            {"texture": self.camera.color_texture, "mip_level": 0, "origin": (0, 0, 0)},
            {"buffer": buffer, "offset": 0,
             "bytes_per_row": self.padded_row, "rows_per_image": self.height},
            (self.width, self.height, 1),
        )
        self.queue.submit([encoder.finish()])
        self.waiting.append((buffer, buffer.map_async("READ", 0, buffer.size)))
        if len(self.waiting) > self.behind:
            self.write_oldest()

    def drain(self) -> None:
        """
        Writes every frame still in flight. Whatever is being written to has to be told this
        before it is closed, or the last frames of it are the ones which never arrive.
        """
        while self.waiting:
            self.write_oldest()

    def write_oldest(self) -> None:
        buffer, promise = self.waiting.pop(0)
        promise.sync_wait()
        frame = buffer.read_mapped(copy=False)
        if self.padded_row > self.row:
            rows = np.frombuffer(frame, np.uint8).reshape((self.height, self.padded_row))
            frame = rows[:, :self.row].tobytes()
        self.sink.write(frame)
        # What was read is a view onto the buffer, so it is done with before the buffer is
        buffer.unmap()


class Camera(object):
    def __init__(
        self,
        window: Optional[Window] = None,
        frame_config: dict = dict(),
        # Note: frame height and width will be resized to match this resolution aspect ratio
        resolution=DEFAULT_RESOLUTION,
        fps: int = 30,
        background_color: ManimColor = BLACK,
        background_opacity: float = 1.0,
        light_source_position: Vect3 = np.array([-10, 10, 10]),
        bundle_draws: bool = True,
        draw_together: bool = True,
        # Although vector graphics handle antialiasing fine
        # without multisampling, for 3d scenes one might want
        # to set samples to be greater than 0.
        samples: int = 0,
    ):
        self.window = window
        self.default_pixel_shape = resolution  # Rename?
        self.fps = fps
        self.light_source_position = light_source_position
        self.samples = samples
        self.bundle_draws = bundle_draws
        self.draw_together = draw_together

        self.background_rgba: list[float] = list(color_to_rgba(
            background_color, background_opacity
        ))
        # Where a window is showing the scene, frames are drawn at its size rather than at
        # the resolution they are written at, since drawing 4k to shrink into a small window
        # costs more than it shows. See at_output_resolution for the exception.
        self.draw_at_window_size = window is not None
        self.pixel_shape = (0, 0)
        self.init_frame(**frame_config)
        self.init_renderer()
        self.init_target()
        self.init_light_source()

    def init_frame(self, **config) -> None:
        self.frame = CameraFrame(**config)

    def init_renderer(self) -> None:
        # A window's surface can be configured for one device only, so a scene shown in one
        # draws through the device it already holds rather than bringing another, see
        # Window.configure. That also spares every scene after the first the compiling of
        # every pipeline again, those being kept on the device.
        self.gpu = Gpu() if self.window is None else self.window.gpu
        self.renderer = Renderer(
            self.gpu, bundle=self.bundle_draws, together=self.draw_together,
        )

    def get_target_shape(self) -> tuple[int, int]:
        if self.draw_at_window_size and self.window is not None:
            return self.window.get_size()
        return self.default_pixel_shape

    def resize_target(self) -> None:
        """
        Makes what a frame is drawn into the size it ought to be, which changes when the
        window is resized or when a frame is wanted at the resolution it will be written at.
        """
        if self.get_target_shape() != self.pixel_shape:
            self.init_target()

    @contextmanager
    def at_output_resolution(self):
        """
        Draws at the resolution frames are written at rather than at the window's size, for
        as long as the block lasts. Without a window the two are already the same.
        """
        was_at_window_size = self.draw_at_window_size
        self.draw_at_window_size = False
        try:
            yield
        finally:
            self.draw_at_window_size = was_at_window_size

    def init_target(self) -> None:
        """
        What every frame is drawn into: one color texture and one depth-stencil texture. Where
        samples are being taken there is a second color texture holding them, which the first
        is resolved down to.
        """
        device = self.gpu.device
        self.pixel_shape = self.get_target_shape()
        width, height = self.pixel_shape
        samples = self.gpu.samples = max(1, self.samples)

        self.color_texture = device.create_texture(
            size=(width, height, 1),
            format=COLOR_FORMAT,
            usage=(
                wgpu.TextureUsage.RENDER_ATTACHMENT
                | wgpu.TextureUsage.COPY_SRC
                | wgpu.TextureUsage.TEXTURE_BINDING
            ),
        )
        self.multisample_texture = None
        if samples > 1:
            self.multisample_texture = device.create_texture(
                size=(width, height, 1),
                format=COLOR_FORMAT,
                usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
                sample_count=samples,
            )
        self.depth_stencil_texture = device.create_texture(
            size=(width, height, 1),
            format=DEPTH_STENCIL_FORMAT,
            usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
            sample_count=samples,
        )

        # A view onto a texture is the same every frame, so they are made along with it
        drawn_into = self.multisample_texture or self.color_texture
        self.color_view = drawn_into.create_view()
        self.resolve_view = self.color_texture.create_view() if samples > 1 else None
        self.depth_stencil_view = self.depth_stencil_texture.create_view()
        # What a finished frame is read from, which is where samples end up rather than
        # where they are taken
        self.frame_view = self.color_texture.create_view()

    def init_light_source(self) -> None:
        self.light_source = Point(self.light_source_position)

    def get_attachments(self) -> dict:
        """
        The textures a frame is drawn into, and what to do with what they already hold.
        Beginning the pass is what clears them.
        """
        return {
            "color_attachments": [{
                "view": self.color_view,
                "resolve_target": self.resolve_view,
                "clear_value": tuple(self.background_rgba),
                "load_op": wgpu.LoadOp.clear,
                "store_op": wgpu.StoreOp.store,
            }],
            "depth_stencil_attachment": {
                "view": self.depth_stencil_view,
                "depth_clear_value": 1.0,
                "depth_load_op": wgpu.LoadOp.clear,
                "depth_store_op": wgpu.StoreOp.store,
                "stencil_clear_value": 0,
                "stencil_load_op": wgpu.LoadOp.clear,
                "stencil_store_op": wgpu.StoreOp.store,
            },
        }

    def get_frame_bytes(self) -> memoryview:
        """
        The frame as it stands, four bytes to a pixel, a row at a time from the top, as a view
        onto what came off the gpu rather than a copy of it.
        """
        width, height = self.pixel_shape
        return self.gpu.queue.read_texture(
            {"texture": self.color_texture, "mip_level": 0, "origin": (0, 0, 0)},
            {"offset": 0, "bytes_per_row": 4 * width, "rows_per_image": height},
            (width, height, 1),
        )

    def get_image(self) -> Image.Image:
        return Image.frombytes("RGBA", self.pixel_shape, self.get_frame_bytes())

    # Getting camera attributes
    def get_pixel_size(self) -> float:
        return self.frame.get_width() / self.get_pixel_shape()[0]

    def get_pixel_shape(self) -> tuple[int, int]:
        return self.pixel_shape

    def get_pixel_width(self) -> int:
        return self.get_pixel_shape()[0]

    def get_pixel_height(self) -> int:
        return self.get_pixel_shape()[1]

    def get_aspect_ratio(self):
        pw, ph = self.get_pixel_shape()
        return pw / ph

    def get_frame_height(self) -> float:
        return self.frame.get_height()

    def get_frame_width(self) -> float:
        return self.frame.get_width()

    def get_frame_shape(self) -> tuple[float, float]:
        return (self.get_frame_width(), self.get_frame_height())

    def get_frame_center(self) -> np.ndarray:
        return self.frame.get_center()

    def get_location(self) -> tuple[float, float, float]:
        return self.frame.get_implied_camera_location()

    def resize_frame_shape(self, fixed_dimension: bool = False) -> None:
        """
        Changes frame_shape to match the aspect ratio
        of the pixels, where fixed_dimension determines
        whether frame_height or frame_width
        remains fixed while the other changes accordingly.
        """
        frame_height = self.get_frame_height()
        frame_width = self.get_frame_width()
        aspect_ratio = self.get_aspect_ratio()
        if not fixed_dimension:
            frame_height = frame_width / aspect_ratio
        else:
            frame_width = aspect_ratio * frame_height
        self.frame.set_height(frame_height, stretch=True)
        self.frame.set_width(frame_width, stretch=True)

    # Rendering
    def capture(self, *mobjects: Mobject) -> None:
        self.resize_target()
        self.refresh_uniforms()
        self.gpu.send_frame_uniforms()
        self.renderer.draw(mobjects, self.get_attachments())
        if self.window is not None:
            self.window.show(self.frame_view)

    def refresh_uniforms(self) -> None:
        """
        What every shader reads about where the frame, the camera and the light are,
        written into the block they all share, see Gpu.
        """
        frame = self.frame
        self.gpu.frame_uniforms.update(
            view=frame.get_view_matrix().T.flatten(),
            frame_scale=frame.get_scale(),
            frame_rescale_factors=(
                2.0 / FRAME_WIDTH,
                2.0 / FRAME_HEIGHT,
                frame.get_scale() / frame.get_focal_distance(),
            ),
            pixel_size=self.get_pixel_size(),
            camera_position=frame.get_implied_camera_location(),
            light_position=self.light_source.get_location(),
        )


# Mostly just defined so old scenes don't break
class ThreeDCamera(Camera):
    def __init__(self, samples: int = 4, **kwargs):
        super().__init__(samples=samples, **kwargs)
